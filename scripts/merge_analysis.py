#!/usr/bin/env python3
"""
merge_analysis.py — Fold the LLM's analysis output into the research pools.

Reads data/analysis_out.json (a list of fully-analyzed v2 entries emitted by the
/research-scan or /add-resource skill), validates each against the schema,
de-duplicates against the existing pools (URL + fuzzy title), gates low-confidence
findings to needs_review, routes each into data/security.json or data/ai.json,
clears the merged candidates, and re-ranks. Idempotent: re-merging the same URL
updates the entry in place rather than duplicating it.

Usage:
    python scripts/merge_analysis.py
"""

from __future__ import annotations

import sys

import common as c
import rerank


def entry_confidence(entry: dict) -> float:
    lessons = entry.get("lessons") or []
    confs = [
        float(x.get("confidence"))
        for x in lessons
        if isinstance(x, dict) and x.get("confidence") is not None
    ]
    if "confidence" in entry:
        confs.append(float(entry["confidence"]))
    return min(confs) if confs else 1.0


def match_index(entries: list[dict], entry: dict) -> int | None:
    urls = {
        c.normalize_url(entry.get(k, ""))
        for k in ("source_url", "article_url", "tweet_url")
        if entry.get(k)
    }
    for i, existing in enumerate(entries):
        for k in ("source_url", "article_url", "tweet_url"):
            if existing.get(k) and c.normalize_url(existing[k]) in urls:
                return i
        if c.title_similar(existing.get("title", ""), entry.get("title", "")):
            return i
    return None


def below_curation_bar(entry: dict, conf: c.Config) -> bool:
    """True if the finding isn't novel/relevant enough for the vetted set."""
    scores = entry.get("scores") or {}
    min_nov = conf.curation.get("min_novelty", 0)
    min_rel = conf.curation.get("min_relevance", 0)
    return (
        float(scores.get("novelty", 0) or 0) < min_nov
        or float(scores.get("relevance", 0) or 0) < min_rel
    )


def normalize_entry(entry: dict, conf: c.Config) -> dict:
    entry = dict(entry)
    for key in ("source_url", "article_url", "tweet_url"):
        if entry.get(key):
            entry[key] = c.clean_source_url(entry[key])
    url = entry.get("source_url") or entry.get("article_url") or entry.get("title", "")
    entry.setdefault("id", c.make_id(entry.get("title", ""), c.normalize_url(url)))
    entry.setdefault("retrieved_at", c.utcnow_iso())
    entry.setdefault("discovered_via", "manual")
    # Held from the vetted set if unverifiable OR not novel/relevant enough.
    entry["needs_review"] = entry_confidence(entry) < conf.confidence_min or below_curation_bar(
        entry, conf
    )
    return entry


def merge(analyzed: list[dict], conf: c.Config) -> tuple[list[dict], list[str], set[str]]:
    pools = {t: c.load_pool(t) for t in c.TRACK_DOMAINS}
    merged: list[dict] = []
    errors: list[str] = []
    merged_urls: set[str] = set()
    for raw in analyzed:
        problems = c.validate_entry(raw)
        if problems:
            errors.append(f"{raw.get('title', '?')[:50]}: {'; '.join(problems)}")
            continue
        entry = normalize_entry(raw, conf)
        entries = pools[entry["track"]]["entries"]
        idx = match_index(entries, entry)
        if idx is None:
            entries.append(entry)
        else:
            entries[idx] = {**entries[idx], **entry, "id": entries[idx].get("id", entry["id"])}
        merged.append(entry)
        for k in ("source_url", "article_url"):
            if entry.get(k):
                merged_urls.add(c.normalize_url(entry[k]))
    for track, pool in pools.items():
        c.save_pool(track, pool)
    return merged, errors, merged_urls


def clear_candidates(merged: list[dict], merged_urls: set[str]) -> int:
    merged_ids = {m["id"] for m in merged}
    remaining = [
        cand
        for cand in c.load_candidates()
        if cand.get("id") not in merged_ids
        and c.normalize_url(cand.get("source_url", "")) not in merged_urls
    ]
    before = len(c.load_candidates())
    c.save_candidates(remaining)
    return before - len(remaining)


def main() -> int:
    conf = c.load_config()
    analyzed = c.load_json(c.ANALYSIS_OUT, default=None)
    if not analyzed:
        print(f"No {c.ANALYSIS_OUT.name} to merge.", file=sys.stderr)
        return 1
    if isinstance(analyzed, dict):
        analyzed = analyzed.get("entries", [])

    merged, errors, merged_urls = merge(analyzed, conf)
    print(f"Merged {len(merged)} entr(y/ies) into the pools.")
    for track in c.TRACK_DOMAINS:
        flagged = sum(1 for m in merged if m["track"] == track and m.get("needs_review"))
        count = sum(1 for m in merged if m["track"] == track)
        print(f"  {track}: {count} merged ({flagged} flagged needs_review)")
    if errors:
        print(f"\nSkipped {len(errors)} invalid entr(y/ies):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)

    cleared = clear_candidates(merged, merged_urls)
    print(f"Cleared {cleared} staged candidate(s).")

    rerank.rerank_all(conf)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
