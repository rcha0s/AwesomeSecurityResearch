#!/usr/bin/env python3
"""
ingest_hn.py — Discover fast-moving security/AI stories from Hacker News.

Queries the keyless HN Algolia API (`search_by_date`) for the topics in
sources.yaml `hackernews:`, keeps stories inside the freshness window that clear
a points floor, classifies each with the shared keyword classifier, and stages
them as candidates in data/candidates.json. HN is a velocity signal — it surfaces
a wave breaking, hours to days before it reaches a curated feed. Novelty is judged
at analysis time (the /research-scan skill); the curation gate holds derivative
items as needs_review.

Runs on Windows or WSL (network, no auth). No LLM here.

Usage:
    python scripts/ingest_hn.py --dry-run
    python scripts/ingest_hn.py --max 6
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime, timedelta

import aggregate as agg
import common as c

HN_SEARCH = "http://hn.algolia.com/api/v1/search_by_date"
HN_ITEM = "https://news.ycombinator.com/item?id="
# HN is an aggregator, not a first-party source: a neutral-medium credibility.
HN_SOURCE_RANK = 55.0


def search_stories(query: str, limit: int, since_ts: int) -> list[dict]:
    """Recent HN stories matching `query`, newest first. [] on any failure."""
    import requests  # local import keeps offline unit tests import-clean

    params = {
        "query": query,
        "tags": "story",
        "numericFilters": f"created_at_i>={since_ts}",
        "hitsPerPage": str(limit),
    }
    try:
        resp = requests.get(
            HN_SEARCH,
            params=params,
            timeout=30,
            headers={"User-Agent": "AwesomeSecurityResearch/1.0"},
        )
        resp.raise_for_status()
        return resp.json().get("hits", []) or []
    except Exception as exc:  # noqa: BLE001 - discovery is best-effort
        print(f"   ! HN search failed for {query!r}: {exc}", file=sys.stderr)
        return []


def hit_to_candidate(hit: dict, rules: dict) -> dict | None:
    """Map an HN Algolia hit to a candidate; None if it doesn't classify on-topic."""
    title = (hit.get("title") or "").strip()
    # Self/Ask-HN posts have no external url — fall back to the HN discussion.
    external = (hit.get("url") or "").strip()
    hn_url = HN_ITEM + str(hit.get("objectID", ""))
    article_url = external or hn_url
    if not title or not c.normalize_url(article_url):
        return None
    body = c.clean_summary(hit.get("story_text") or "", 320)
    blob = f"{title} {body}"
    # Strict: only stage items that actually keyword-match a topic (no fallback),
    # so the HN firehose stays on-scope.
    domain = agg.classify_domain(blob, rules, [])
    if domain is None:
        return None
    published = (hit.get("created_at") or "")[:10] or None
    cand_id = c.make_id(title, c.normalize_url(article_url))
    return {
        "id": cand_id,
        "discovered_via": "rss",  # a fetched link, same handling as an RSS item
        "title": title,
        "source_name": (
            f"@{hit.get('author')} via Hacker News" if hit.get("author") else "Hacker News"
        ),
        "source_type": "Hacker News",
        "source_url": article_url,
        "article_url": article_url,
        "tweet_url": None,
        "author": hit.get("author"),
        "published": published,
        "date": published[:7] if published else None,
        "excerpt": body
        or f"HN: {hit.get('points', 0)} points, {hit.get('num_comments', 0)} comments",
        "raw_path": None,
        "guess_topic": c.topic_for_domain(domain),
        "guess_domain": domain,
        "guess_subtype": agg.classify_subtype(blob, domain, rules),
        "source_id": None,
        "source_rank": HN_SOURCE_RANK,
        "source_topics": [],
        "hn_points": hit.get("points", 0),
        "retrieved_at": c.utcnow_iso(),
    }


def collect(cfg: dict, rules: dict, per_query: int | None) -> list[dict]:
    hn_cfg = cfg.get("hackernews", {})
    queries = hn_cfg.get("queries", [])
    if not queries:
        print("   (no hackernews.queries configured in sources.yaml)")
        return []
    min_points = hn_cfg.get("min_points", 0)
    limit = per_query or hn_cfg.get("per_query", 8)
    cutoff = datetime.now(UTC) - timedelta(days=c.load_config().max_age_days)
    since_ts = int(cutoff.timestamp())

    out: list[dict] = []
    for query in queries:
        print(
            f"-> HN search: {query!r} (>= {min_points} points, last {c.load_config().max_age_days}d)"
        )
        for hit in search_stories(query, limit, since_ts):
            if int(hit.get("points", 0) or 0) < min_points:
                continue
            cand = hit_to_candidate(hit, rules)
            if cand:
                out.append(cand)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max", type=int, default=None, help="override per-query limit")
    args = ap.parse_args()

    cfg = c.load_yaml(c.SOURCES_FILE)
    rules = cfg["classification"]
    candidates = collect(cfg, rules, args.max)
    print(f"\nFound {len(candidates)} HN candidate(s).")

    if args.dry_run:
        for cand in candidates:
            print(f"   [{cand['guess_topic']}/{cand['guess_domain']}] {cand['title']}")
        return 0

    added = c.add_candidates(candidates)
    print(f"Staged {len(added)} new candidate(s) in {c.CANDIDATES_FILE.name}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
