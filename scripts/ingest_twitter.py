#!/usr/bin/env python3
"""
ingest_twitter.py — Pull the burner's X feed + curated accounts via Agent Reach.

Health-gates on `agent-reach doctor`, then reads the home timeline
(`twitter feed`) and each curated account (`twitter user-posts`) as JSON,
extracts linked article URLs, fetches clean article text via Jina Reader, and
stages everything as candidates in data/candidates.json. The LLM analyze step
(the /research-scan skill) scores and files them.

Runs LOCALLY ONLY (WSL2) — datacenter-IP polling risks the account. Prefer the
stable `feed`/`user-posts` primitives over `twitter search` (GraphQL churn).

Usage:
    python scripts/ingest_twitter.py --dry-run
    python scripts/ingest_twitter.py --max 20
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys

import common as c
import sources_registry as sr


def run_cli(args: list[str], timeout: int = 60) -> str | None:
    """Run a CLI, returning stdout on success or None on any failure."""
    try:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        print(f"   ! {args[0]} unavailable ({exc.__class__.__name__})", file=sys.stderr)
        return None
    if proc.returncode != 0:
        print(f"   ! {' '.join(args)} failed: {proc.stderr.strip()[:200]}", file=sys.stderr)
        return None
    return proc.stdout


def doctor_ok() -> bool:
    out = run_cli(["agent-reach", "doctor", "--json"], timeout=90)
    if out is None:
        return False
    try:
        report = json.loads(out)
    except json.JSONDecodeError:
        return "twitter" in out.lower() and "ok" in out.lower()
    twitter = report.get("twitter") or report.get("channels", {}).get("twitter", {})
    status = str(twitter.get("status", twitter)).lower()
    return "ok" in status


def parse_tweets(raw: str) -> list[dict]:
    """Parse twitter-cli JSON into a list of tweet dicts (shape-tolerant)."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if isinstance(data, dict):
        for key in ("tweets", "data", "results", "items"):
            if isinstance(data.get(key), list):
                return data[key]
        return [data]
    return data if isinstance(data, list) else []


def _author_handle(t: dict) -> str:
    author = t.get("author")
    if isinstance(author, dict):
        author = author.get("screenName") or author.get("screen_name") or author.get("name") or ""
    author = (
        author
        or t.get("username")
        or t.get("screen_name")
        or (t.get("user") or {}).get("screen_name")
        or ""
    )
    return str(author).lstrip("@")


def _tweet_links(t: dict, text: str) -> list[str]:
    """Extract external links from the twitter-cli `urls` field or the text."""
    links: list[str] = []
    for u in t.get("urls") or []:
        if isinstance(u, dict):
            links.append(u.get("expandedUrl") or u.get("expanded_url") or u.get("url") or "")
        elif isinstance(u, str):
            links.append(u)
    # legacy shape + text fallback
    for u in (t.get("entities", {}) or {}).get("urls", []):
        if isinstance(u, dict):
            links.append(u.get("expanded_url") or u.get("url") or "")
    links = [u for u in links if u] or c.extract_urls(text)
    external = [u for u in links if "twitter.com" not in u and "x.com" not in u]
    # Resolve shorteners (t.co/…) so a tweet-linked article de-dups with its RSS permalink.
    return [c.resolve_redirects(u) for u in external]


def normalize_tweet(t: dict) -> dict:
    text = (t.get("text") or t.get("full_text") or t.get("content") or "").strip()
    author = _author_handle(t)
    url = t.get("url") or t.get("tweet_url") or t.get("permalink") or ""
    if not url and author and t.get("id"):
        url = f"https://x.com/{author}/status/{t['id']}"
    return {
        "text": text,
        "author": author,
        "url": url,
        "created": t.get("createdAtISO")
        or t.get("created_at")
        or t.get("date")
        or t.get("created"),
        "links": _tweet_links(t, text),
    }


def tweet_to_candidate(tweet: dict, fetch: bool, max_chars: int = 20000) -> dict | None:
    tw = normalize_tweet(tweet)
    if not tw["text"] and not tw["links"]:
        return None
    article_url = tw["links"][0] if tw["links"] else tw["url"]
    title = tw["text"][:120] or f"Tweet by @{tw['author']}"
    cand_id = c.make_id(title, c.normalize_url(article_url))
    created = tw.get("created") or ""
    date = created[:7] if len(created) >= 7 and created[4] == "-" else None
    raw_path = None
    if fetch and tw["links"]:
        try:
            raw_path = c.write_raw(cand_id, c.fetch_readable(article_url, max_chars=max_chars))
        except Exception as exc:  # noqa: BLE001 - network best-effort
            print(f"   ! fetch failed for {article_url}: {exc}", file=sys.stderr)
    return {
        "id": cand_id,
        "discovered_via": "twitter",
        "title": title,
        "source_name": f"@{tw['author']}" if tw["author"] else "X/Twitter",
        "source_type": "Social (X/Twitter)",
        "source_url": article_url,
        "article_url": article_url if tw["links"] else None,
        "tweet_url": tw["url"] or None,
        "author": tw["author"] or None,
        "published": created[:10] if len(created) >= 10 and created[4] == "-" else None,
        "date": date,
        "excerpt": tw["text"][:320],
        "raw_path": raw_path,
        "guess_topic": None,
        "guess_domain": None,
        "guess_subtype": None,
        "source_id": (tweet.get("_source") or {}).get("id"),
        "source_rank": (tweet.get("_source") or {}).get("rank"),
        "source_topics": (tweet.get("_source") or {}).get("topics", []),
        "retrieved_at": c.utcnow_iso(),
    }


def collect_tweets(cfg: dict, limits: dict) -> list[dict]:
    """Home timeline (unranked) + each registered x_account source (ranked)."""
    tweets: list[dict] = []
    if cfg.get("twitter", {}).get("home_feed"):
        n = limits.get("twitter_feed", 40)
        print(f"-> twitter feed -n {n}")
        out = run_cli(["twitter", "feed", "-n", str(n), "--json"])
        if out:
            tweets += parse_tweets(out)  # home-feed tweets carry no _source
    for source in sr.sources_of_type("x_account"):
        account = source["handle"]
        n = limits.get("twitter_user_posts", 20)
        print(f"-> twitter user-posts @{account} -n {n}  (rank {source.get('rank')})")
        out = run_cli(["twitter", "user-posts", f"@{account}", "-n", str(n), "--json"])
        if out:
            for tw in parse_tweets(out):
                tw["_source"] = {
                    "id": source["id"],
                    "rank": source.get("rank"),
                    "topics": source.get("topics", []),
                }
                tweets.append(tw)
    return tweets


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max", type=int, default=None, help="override per-source cap")
    ap.add_argument("--no-fetch", action="store_true", help="skip article fetch")
    args = ap.parse_args()

    cfg = c.load_yaml(c.SOURCES_FILE)
    conf = c.load_config()
    limits = dict(conf.limits)
    if args.max is not None:
        limits["twitter_feed"] = args.max
        limits["twitter_user_posts"] = args.max

    if not doctor_ok():
        print(
            "Agent Reach / twitter-cli not healthy. In WSL2:\n"
            "  source ~/.agent-reach/twitter.env   # exports TWITTER_AUTH_TOKEN + TWITTER_CT0\n"
            "  agent-reach doctor --json           # twitter should be 'ok'\n"
            "If unset, refresh the burner cookies (auth_token + ct0) into that env file.",
            file=sys.stderr,
        )
        return 1

    tweets = collect_tweets(cfg, limits)
    max_chars = limits.get("article_chars", 20000)
    candidates = [
        cand
        for cand in (
            tweet_to_candidate(t, fetch=not args.no_fetch, max_chars=max_chars) for t in tweets
        )
        if cand
    ]
    print(f"\nParsed {len(candidates)} candidate tweet(s).")

    if args.dry_run:
        for cand in candidates:
            print(f"   @{cand['author']}: {cand['title'][:70]}")
        return 0

    added = c.add_candidates(candidates)
    print(f"Staged {len(added)} new candidate(s) in {c.CANDIDATES_FILE.name}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
