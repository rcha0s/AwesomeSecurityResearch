#!/usr/bin/env python3
"""
ingest_conferences.py — Discover peer-reviewed conference work via arXiv.

The approved venues (USENIX Security, NDSS, IEEE SaTML, ACM AISec, NeurIPS,
ICML/PMLR, ISSTA) publish no usable feed: their proceedings and accepted-paper
lists are HTML, and several sit behind paywalls we deliberately never touch.
But authors record venue acceptance in the arXiv `comments` field, and arXiv's
API is free, keyless, and searchable on that field — so one robust API replaces
a fleet of brittle per-site scrapers, and every hit resolves to a free full text.

Two quality gates matter here:
  * ACCEPTANCE, not submission. "Submitted to NeurIPS" is an unreviewed preprint
    wearing a venue's name; only acceptance language is staged (see ACCEPT_RE /
    REJECT_RE). This is the peer-review signal raw arXiv cs.CR cannot give us.
  * ON-THESIS ONLY. Venue acceptance alone would drag in the whole ML firehose,
    so each item must also keyword-classify onto a tracked domain.

Runs anywhere with network; no auth, no LLM. Venues live in sources.yaml
`conferences:`.

Usage:
    python scripts/ingest_conferences.py --dry-run
    python scripts/ingest_conferences.py --max 8
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.parse
from datetime import UTC, datetime, timedelta

import aggregate as agg
import common as c

ARXIV_API = "http://export.arxiv.org/api/query"
# Peer-reviewed acceptance at a named venue outranks a bare preprint, but is not
# first-party vendor research: a high-medium rank.
CONFERENCE_SOURCE_RANK = 72.0
# arXiv asks for <1 request/3s; be a good citizen between venue queries.
REQUEST_SPACING_SECONDS = 3.0

# Acceptance language. "Accepted", "to appear", "published/presented at",
# "camera-ready", or "in proceedings of" all mean a program committee said yes.
ACCEPT_RE = re.compile(
    r"\b(accepted|to appear|camera[- ]ready|published (?:at|in)|presented at|in proceedings of)\b",
    re.I,
)
# ...but these mean nobody has reviewed it yet.
REJECT_RE = re.compile(
    r"\b(submitted to|under review|in submission|preprint of a submission)\b", re.I
)

ENTRY_RE = re.compile(r"<entry>(.*?)</entry>", re.S)


def _tag(entry_xml: str, tag: str) -> str:
    m = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", entry_xml, re.S)
    return " ".join(m.group(1).split()) if m else ""


def is_accepted(comment: str) -> bool:
    """True when the arXiv comment claims acceptance rather than submission."""
    if not comment or REJECT_RE.search(comment):
        return False
    return bool(ACCEPT_RE.search(comment))


def search_venue(venue: str, limit: int) -> list[dict]:
    """Recent arXiv entries whose comment field names `venue`. [] on failure."""
    import requests  # local import keeps offline unit tests import-clean

    query = urllib.parse.quote(f'co:"{venue}"')
    url = (
        f"{ARXIV_API}?search_query={query}"
        f"&sortBy=submittedDate&sortOrder=descending&max_results={limit}"
    )
    try:
        resp = requests.get(url, timeout=45, headers={"User-Agent": "AwesomeSecurityResearch/1.0"})
        resp.raise_for_status()
    except Exception as exc:  # noqa: BLE001 - discovery is best-effort
        print(f"   ! arXiv search failed for {venue!r}: {exc}", file=sys.stderr)
        return []
    out = []
    for chunk in ENTRY_RE.findall(resp.text):
        out.append(
            {
                "title": _tag(chunk, "title"),
                "summary": _tag(chunk, "summary"),
                "published": _tag(chunk, "published"),
                "link": _tag(chunk, "id"),
                "comment": _tag(chunk, "arxiv:comment"),
            }
        )
    return out


def entry_to_candidate(
    item: dict, venue: str, rules: dict, security_terms: tuple[str, ...] = ()
) -> dict | None:
    """Map an arXiv entry to a candidate; None if unaccepted or off-topic.

    `security_terms` is non-empty for broad ML/SE venues, where venue acceptance
    alone would admit the entire field — there the blob must name a security
    concern as well.
    """
    title, url = item.get("title", ""), item.get("link", "")
    if not title or not c.normalize_url(url) or not is_accepted(item.get("comment", "")):
        return None
    excerpt = c.clean_summary(item.get("summary", ""), 320)
    blob = f"{title} {excerpt}"
    if security_terms and not any(term in blob.lower() for term in security_terms):
        return None
    # Strict: venue acceptance alone isn't enough, it must classify on-topic too.
    domain = agg.classify_domain(blob, rules, [])
    if domain is None:
        return None
    published = (item.get("published") or "")[:10] or None
    return {
        "id": c.make_id(title, c.normalize_url(url)),
        "discovered_via": "rss",
        "title": title,
        "source_name": f"{venue} (via arXiv)",
        "source_type": "conference",
        "source_url": url,
        "article_url": url,
        "tweet_url": None,
        "author": None,
        "published": published,
        "date": published[:7] if published else None,
        "excerpt": excerpt,
        "raw_path": None,
        "guess_topic": c.topic_for_domain(domain),
        "guess_domain": domain,
        "guess_subtype": agg.classify_subtype(blob, domain, rules),
        "source_id": None,
        "source_rank": CONFERENCE_SOURCE_RANK,
        "source_topics": [],
        "venue": venue,
        "venue_comment": item.get("comment", ""),
        "retrieved_at": c.utcnow_iso(),
    }


def collect(cfg: dict, rules: dict, per_venue: int | None) -> list[dict]:
    import time

    conf_cfg = cfg.get("conferences", {})
    security_terms = tuple(t.lower() for t in conf_cfg.get("security_terms", []))
    # (venue, extra security gate) — broad venues must also name a security concern.
    plan = [(v, ()) for v in conf_cfg.get("venues", [])]
    plan += [(v, security_terms) for v in conf_cfg.get("broad_venues", [])]
    if not plan:
        print("   (no conferences.venues configured in sources.yaml)")
        return []
    limit = per_venue or conf_cfg.get("per_venue", 20)
    max_age = c.load_config().max_age_days
    cutoff = (datetime.now(UTC) - timedelta(days=max_age)).date().isoformat()

    out: list[dict] = []
    for idx, (venue, terms) in enumerate(plan):
        gate = " +security-gated" if terms else ""
        print(f"-> arXiv co:{venue!r} (accepted only, last {max_age}d{gate})")
        if idx:
            time.sleep(REQUEST_SPACING_SECONDS)
        for item in search_venue(venue, limit):
            if (item.get("published") or "")[:10] < cutoff:
                continue
            cand = entry_to_candidate(item, venue, rules, terms)
            if cand:
                out.append(cand)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max", type=int, default=None, help="override per-venue limit")
    args = ap.parse_args()

    cfg = c.load_yaml(c.SOURCES_FILE)
    candidates = collect(cfg, cfg["classification"], args.max)
    print(f"\nFound {len(candidates)} conference candidate(s).")

    if args.dry_run:
        for cand in candidates:
            print(
                f"   [{cand['guess_topic']}/{cand['guess_domain']}] {cand['venue']}: {cand['title']}"
            )
        return 0

    added = c.add_candidates(candidates)
    print(f"Staged {len(added)} new candidate(s) in {c.CANDIDATES_FILE.name}.")
    for cand in added:
        print(f"   [{cand['guess_topic']}] {cand['venue']}: {cand['title'][:70]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
