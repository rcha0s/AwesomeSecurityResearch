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
    domain = classify_domain(blob, rules, feed.get("domains", []))
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
        "date": dt.strftime("%Y-%m") if dt else None,
        "excerpt": excerpt,
        "raw_path": None,
        "guess_track": c.track_for_domain(domain),
        "guess_domain": domain,
        "guess_subtype": classify_subtype(blob, domain, rules),
        "retrieved_at": c.utcnow_iso(),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="don't write changes")
    args = ap.parse_args()

    config = c.load_yaml(c.SOURCES_FILE)
    rules = config["classification"]
    cutoff = datetime.now(UTC) - timedelta(days=config.get("max_age_days", 183))

    candidates: list[dict] = []
    for feed in config["feeds"]:
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

    if args.dry_run:
        print(f"\n(dry run) {len(candidates)} candidate(s) would be staged:")
        for cand in candidates:
            print(f"   [{cand['guess_track']}/{cand['guess_domain']}] {cand['title']}")
        return 0

    added = c.add_candidates(candidates)
    print(f"\nStaged {len(added)} new candidate(s) in {c.CANDIDATES_FILE.name}.")
    for cand in added:
        print(f"   [{cand['guess_track']}/{cand['guess_domain']}] {cand['title']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
