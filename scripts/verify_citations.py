#!/usr/bin/env python3
"""
verify_citations.py — Ground every lesson excerpt against its source text.

For each finding, we confirm that each lesson's `excerpt` actually appears in the
fetched source (verbatim after normalization) — not a paraphrase the model
invented. The verdict is persisted onto the entry (`lesson.grounded` +
`grounding_score`) so a hallucinated "quote" can never reach the curated view.

Runs at merge time (using the candidate's cached raw text) and can be re-run over
the pools (re-fetching sources) via `main`. If a source can't be fetched, the
entry is left unverified (grounding_score = null) rather than penalized.

Usage:
    python scripts/verify_citations.py            # verify + persist over the pools
    python scripts/verify_citations.py --report   # print results, don't write
"""

from __future__ import annotations

import argparse
import sys

import common as c


def source_text_for(entry: dict) -> str | None:
    """Cached raw text if available, else a best-effort re-fetch of the source."""
    raw = entry.get("raw_path")
    if raw:
        path = c.ROOT / raw
        if path.exists():
            return path.read_text(encoding="utf-8", errors="replace")
    url = entry.get("article_url") or entry.get("source_url") or ""
    if url and not url.startswith("manual:"):
        try:
            return c.fetch_readable(url)
        except Exception:  # noqa: BLE001 - source may be down/auth-walled
            return None
    return None


def ground_entry(entry: dict, source_text: str | None = None) -> dict:
    """Annotate each lesson `grounded` and set `grounding_score` (fraction of
    excerpt-bearing lessons verified), or None if the source can't be checked."""
    lessons = entry.get("lessons") or []
    with_excerpt = [le for le in lessons if isinstance(le, dict) and le.get("excerpt")]
    if source_text is None:
        source_text = source_text_for(entry)
    if not source_text or not with_excerpt:
        entry["grounding_score"] = None
        return entry
    grounded = 0
    for le in with_excerpt:
        ok = c.is_grounded(le["excerpt"], source_text)
        le["grounded"] = ok
        grounded += ok
    entry["grounding_score"] = round(grounded / len(with_excerpt), 2)
    return entry


def fully_grounded(entry: dict) -> bool:
    """True unless we verified the source and found an ungrounded excerpt."""
    score = entry.get("grounding_score")
    return score is None or score >= 1.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true", help="print, don't persist")
    args = ap.parse_args()
    total = flagged = unverifiable = 0
    for topic in c.TOPICS:
        pool = c.load_pool(topic)
        for e in pool["entries"]:
            ground_entry(e)
            total += 1
            if e.get("grounding_score") is None:
                unverifiable += 1
            elif not fully_grounded(e):
                flagged += 1
                print(
                    f"  ⚠ ungrounded excerpt: [{topic}] {e.get('title','')[:60]} "
                    f"(score {e['grounding_score']})",
                    file=sys.stderr,
                )
        if not args.report:
            c.save_pool(topic, pool)
    print(
        f"Verified {total} findings: {flagged} with ungrounded excerpts, "
        f"{unverifiable} unverifiable (source unavailable)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
