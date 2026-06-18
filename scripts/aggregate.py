#!/usr/bin/env python3
"""
aggregate.py — Discover recent security research from credible source feeds.

Pulls items from the feeds defined in sources.yaml, keeps only those published
in the last `max_age_days` days, classifies each into one of the three tracked
domains and a subtype, de-duplicates against data/research.json, and appends new
discoveries with `needs_review: true`.

Curated entries (needs_review: false) are never modified or removed by this
script — a human promotes auto-discovered items after review.

Usage:
    python scripts/aggregate.py            # update data/research.json in place
    python scripts/aggregate.py --dry-run  # print what would be added, no write
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    import feedparser
    import yaml
    from dateutil import parser as dateparser
except ImportError:
    sys.exit(
        "Missing dependencies. Run: pip install -r requirements.txt"
    )

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "research.json"
SOURCES_FILE = ROOT / "scripts" / "sources.yaml"


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_data(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def save_data(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def normalize_url(url: str) -> str:
    url = (url or "").strip().lower()
    url = re.sub(r"#.*$", "", url)
    url = re.sub(r"\?.*$", "", url)
    return url.rstrip("/")


def make_id(title: str, url: str) -> str:
    digest = hashlib.sha1((title + url).encode("utf-8")).hexdigest()[:10]
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:48]
    return f"auto-{slug}-{digest}"


def entry_datetime(entry) -> datetime | None:
    for key in ("published", "updated", "created"):
        val = entry.get(key)
        if val:
            try:
                dt = dateparser.parse(val)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except (ValueError, OverflowError):
                continue
    for key in ("published_parsed", "updated_parsed"):
        val = entry.get(key)
        if val:
            return datetime(*val[:6], tzinfo=timezone.utc)
    return None


def classify_domain(text: str, rules: dict, feed_domains: list[str]) -> str | None:
    text = text.lower()
    for domain, keywords in rules["domains"].items():
        if any(kw in text for kw in keywords):
            return domain
    # Fall back to the feed's primary domain when keywords are inconclusive
    # but only if the feed is single-domain (avoids mis-bucketing).
    if len(feed_domains) == 1:
        return feed_domains[0]
    return None


def classify_subtype(text: str, domain: str, rules: dict) -> str:
    text = text.lower()
    subtypes = rules["subtypes"].get(domain, {})
    for subtype, keywords in subtypes.items():
        if any(kw in text for kw in keywords):
            return subtype
    return "Uncategorized"


def clean_summary(raw: str, limit: int = 320) -> str:
    text = re.sub(r"<[^>]+>", " ", raw or "")
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > limit:
        text = text[:limit].rsplit(" ", 1)[0] + "…"
    return text


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="don't write changes")
    args = ap.parse_args()

    config = load_yaml(SOURCES_FILE)
    data = load_data(DATA_FILE)
    rules = config["classification"]
    max_age = config.get("max_age_days", 183)
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_age)

    known_urls = {normalize_url(e.get("source_url", "")) for e in data["entries"]}
    added: list[dict] = []

    for feed in config["feeds"]:
        print(f"-> {feed['name']}: {feed['url']}")
        parsed = feedparser.parse(feed["url"])
        if parsed.bozo and not parsed.entries:
            print(f"   ! could not parse feed ({getattr(parsed, 'bozo_exception', '')})")
            continue
        for entry in parsed.entries:
            url = entry.get("link", "")
            nurl = normalize_url(url)
            if not nurl or nurl in known_urls:
                continue
            dt = entry_datetime(entry)
            if dt is None or dt < cutoff:
                continue
            title = (entry.get("title") or "").strip()
            summary = clean_summary(entry.get("summary", ""))
            blob = f"{title} {summary}"
            domain = classify_domain(blob, rules, feed.get("domains", []))
            if domain is None:
                continue
            subtype = classify_subtype(blob, domain, rules)
            item = {
                "id": make_id(title, nurl),
                "domain": domain,
                "subtype": subtype,
                "title": title,
                "date": dt.strftime("%Y-%m"),
                "severity": "Unrated",
                "threat": summary or "(Auto-discovered — summarize the threat during review.)",
                "conditions": "(Auto-discovered — describe affected conditions during review.)",
                "mitigations": "(Auto-discovered — add mitigations during review.)",
                "source_name": feed["name"],
                "source_type": feed.get("type", ""),
                "source_url": url,
                "needs_review": True,
            }
            data["entries"].append(item)
            known_urls.add(nurl)
            added.append(item)

    print(f"\nDiscovered {len(added)} new item(s).")
    for item in added:
        print(f"   [{item['domain']} / {item['subtype']}] {item['title']}")

    if args.dry_run:
        print("\n(dry run — no changes written)")
        return 0

    if added:
        data["entries"].sort(
            key=lambda e: (e["domain"], e.get("date", ""), e["title"]), reverse=False
        )
        save_data(DATA_FILE, data)
        print(f"\nWrote {DATA_FILE.relative_to(ROOT)}")
    else:
        print("\nNo changes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
