#!/usr/bin/env python3
"""
aggregate.py — Discover recent research from credible RSS/Atom feeds.

Pulls items from the feeds in sources.yaml, keeps those published in the last
`max_age_days` days, makes a best-guess track/domain classification, and stages
them as candidates in data/candidates.json (de-duped against both the staging
queue and the published pools). The LLM analyze step (the /research-scan skill)
turns candidates into scored, actionable pool entries — this script never writes
to the pools directly.

Usage:
    python scripts/aggregate.py            # stage new candidates
    python scripts/aggregate.py --dry-run  # print what would be staged, no write
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime, timedelta

import common as c
import sources_registry as sr

try:
    import feedparser
except ImportError:  # pragma: no cover - environment guard
    sys.exit("Missing dependencies. Run: pip install -r requirements.txt")


def classify_domain(text: str, rules: dict, feed_domains: list[str]) -> str | None:
    text = text.lower()
    for domain, keywords in rules["domains"].items():
        if any(kw in text for kw in keywords):
            return domain
    if len(feed_domains) == 1:
        return feed_domains[0]
    return None


def classify_subtype(text: str, domain: str, rules: dict) -> str:
    text = text.lower()
    for subtype, keywords in rules["subtypes"].get(domain, {}).items():
        if any(kw in text for kw in keywords):
            return subtype
    return "Uncategorized"


def build_candidate(entry: dict, feed: dict, rules: dict) -> dict | None:
    url = entry.get("link", "")
    if not c.normalize_url(url):
        return None
    dt = c.entry_datetime(entry)
    title = (entry.get("title") or "").strip()
    excerpt = c.clean_summary(entry.get("summary", ""))
    blob = f"{title} {excerpt}"
    # A `strict` feed (e.g. the high-volume arXiv cs.AI/cs.LG firehose) only stages
    # items that actually keyword-match a topic — no single-domain fallback.
    feed_domains = [] if feed.get("strict") else feed.get("domains", [])
    domain = classify_domain(blob, rules, feed_domains)
    if domain is None:
        return None
    return {
        "id": c.make_id(title, c.normalize_url(url)),
        "discovered_via": "rss",
        "title": title,
        "source_name": feed["name"],
        "source_type": feed.get("type", ""),
        "source_url": url,
        "article_url": url,
        "tweet_url": None,
        "author": None,
        "published": dt.strftime("%Y-%m-%d") if dt else c.date_from_url(url),
        "date": dt.strftime("%Y-%m") if dt else None,
        "excerpt": excerpt,
        "raw_path": None,
        "guess_topic": c.topic_for_domain(domain),
        "guess_domain": domain,
        "guess_subtype": classify_subtype(blob, domain, rules),
        "source_id": feed.get("source_id"),
        "source_rank": feed.get("source_rank"),
        "source_topics": feed.get("topics", []),
        "retrieved_at": c.utcnow_iso(),
    }


def feed_from_source(source: dict) -> dict:
    return {
        "name": source["name"],
        "url": source["handle"],
        "type": source.get("notes", ""),
        "domains": source.get("domains", []),
        "strict": source.get("strict", False),
        "source_id": source["id"],
        "source_rank": source.get("rank"),
        "topics": source.get("topics", []),
    }


def collect_rss(rules: dict, cutoff: datetime) -> list[dict]:
    """Fetch every registered rss/newsletter feed and build fresh candidates."""
    feeds = sr.sources_of_type("rss") + sr.sources_of_type("newsletter")
    candidates: list[dict] = []
    for source in feeds:
        feed = feed_from_source(source)
        print(f"-> {feed['name']}: {feed['url']}")
        parsed = feedparser.parse(feed["url"])
        if parsed.bozo and not parsed.entries:
            print(f"   ! could not parse feed ({getattr(parsed, 'bozo_exception', '')})")
            continue
        for entry in parsed.entries:
            dt = c.entry_datetime(entry)
            if dt is None or dt < cutoff:
                continue
            cand = build_candidate(entry, feed, rules)
            if cand:
                candidates.append(cand)
    return candidates


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="don't write changes")
    args = ap.parse_args()

    rules = c.load_yaml(c.SOURCES_FILE)["classification"]
    cutoff = datetime.now(UTC) - timedelta(days=c.load_config().max_age_days)
    candidates = collect_rss(rules, cutoff)

    if args.dry_run:
        print(f"\n(dry run) {len(candidates)} candidate(s) would be staged:")
        for cand in candidates:
            print(f"   [{cand['guess_topic']}/{cand['guess_domain']}] {cand['title']}")
        return 0

    added = c.add_candidates(candidates)
    print(f"\nStaged {len(added)} new candidate(s) in {c.CANDIDATES_FILE.name}.")
    for cand in added:
        print(f"   [{cand['guess_topic']}/{cand['guess_domain']}] {cand['title']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
