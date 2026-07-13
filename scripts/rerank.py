#!/usr/bin/env python3
"""
rerank.py — Deterministic (re)ranking of the research pools.

Recomputes time-decayed newness for every entry, folds it with the LLM-provided
novelty/relevance into a weighted composite, and re-sorts each pool. This is
cheap (no LLM) and runs after every ingest/merge and in CI, so ordering stays
fresh as findings age and as new ones arrive.

Usage:
    python scripts/rerank.py            # rerank both pools in place
    python scripts/rerank.py --track ai
"""

from __future__ import annotations

import argparse

import common as c


def score_entry(entry: dict, conf: c.Config, now=None) -> dict:
    """Return a new entry with refreshed scores.{newness,composite,scored_at}."""
    scores = dict(entry.get("scores") or {})
    scores["newness"] = c.newness_score(entry.get("date") or "", conf.half_life_days, now=now)
    scores.setdefault("novelty", 0)
    scores.setdefault("relevance", 0)
    scores["composite"] = c.composite_score(scores, conf.weights)
    scores["scored_at"] = c.utcnow_iso()
    return {**entry, "scores": scores}


def sort_key(entry: dict) -> tuple:
    scores = entry.get("scores") or {}
    return (-float(scores.get("composite", 0)), entry.get("date") or "", entry.get("title", ""))


def rerank_pool(track: str, conf: c.Config | None = None, now=None) -> dict:
    conf = conf or c.load_config()
    pool = c.load_pool(track)
    pool["entries"] = sorted((score_entry(e, conf, now=now) for e in pool["entries"]), key=sort_key)
    c.save_pool(track, pool)
    return pool


def rerank_all(conf: c.Config | None = None, now=None) -> None:
    conf = conf or c.load_config()
    for track in c.TRACK_DOMAINS:
        pool = rerank_pool(track, conf, now=now)
        print(f"reranked {track}: {len(pool['entries'])} entries")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--track", choices=list(c.TRACK_DOMAINS), default=None)
    args = ap.parse_args()
    if args.track:
        rerank_pool(args.track)
    else:
        rerank_all()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
