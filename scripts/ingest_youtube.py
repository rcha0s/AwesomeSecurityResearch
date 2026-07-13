#!/usr/bin/env python3
"""
ingest_youtube.py — Harvest recent videos from registered YouTube channels.

For each `youtube` source in the registry, lists the channel's most recent
videos via yt-dlp (title, description, upload date, URL) and stages them as
candidates. The analyze step can pull the full transcript later (yt-dlp
subtitles or Agent Reach). Degrades gracefully if yt-dlp is not installed.

Usage:
    python scripts/ingest_youtube.py --dry-run
    python scripts/ingest_youtube.py --max 5
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys

import common as c
import sources_registry as sr

DEFAULT_MAX = 5


def channel_videos_url(handle: str) -> str:
    h = handle.strip()
    if h.startswith("http"):
        return h.rstrip("/") + ("" if h.rstrip("/").endswith("/videos") else "/videos")
    if h.startswith("@"):
        return f"https://www.youtube.com/{h}/videos"
    if h.startswith("UC"):
        return f"https://www.youtube.com/channel/{h}/videos"
    return f"https://www.youtube.com/@{h}/videos"


def list_videos(handle: str, n: int) -> list[dict]:
    """Return up to n recent videos with metadata, or [] on failure/no yt-dlp."""
    url = channel_videos_url(handle)
    try:
        proc = subprocess.run(
            ["yt-dlp", "-J", "--no-warnings", "--playlist-end", str(n), url],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        print(
            f"   ! yt-dlp unavailable ({exc.__class__.__name__}); install: pip install yt-dlp",
            file=sys.stderr,
        )
        return []
    if proc.returncode != 0:
        print(f"   ! yt-dlp failed for {url}: {proc.stderr.strip()[:160]}", file=sys.stderr)
        return []
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return []
    return data.get("entries", []) if isinstance(data, dict) else []


def video_to_candidate(v: dict, source: dict) -> dict | None:
    vid_url = v.get("webpage_url") or v.get("url") or ""
    title = (v.get("title") or "").strip()
    if not vid_url or not title:
        return None
    upload = v.get("upload_date") or ""  # YYYYMMDD
    published = f"{upload[:4]}-{upload[4:6]}-{upload[6:8]}" if len(upload) == 8 else None
    desc = c.clean_summary(v.get("description") or "", 320)
    cand_id = c.make_id(title, c.normalize_url(vid_url))
    return {
        "id": cand_id,
        "discovered_via": "youtube",
        "title": title,
        "source_name": source.get("name") or v.get("channel") or "YouTube",
        "source_type": "YouTube video",
        "source_url": vid_url,
        "article_url": vid_url,
        "tweet_url": None,
        "author": v.get("channel") or v.get("uploader"),
        "published": published,
        "date": published[:7] if published else None,
        "excerpt": desc or title,
        "raw_path": None,
        "guess_track": None,
        "guess_domain": None,
        "guess_subtype": None,
        "source_id": source.get("id"),
        "source_rank": source.get("rank"),
        "source_topics": source.get("topics", []),
        "retrieved_at": c.utcnow_iso(),
    }


def collect(per_channel: int) -> list[dict]:
    out: list[dict] = []
    for source in sr.sources_of_type("youtube"):
        print(f"-> youtube {source['handle']} (rank {source.get('rank')})")
        for v in list_videos(source["handle"], per_channel):
            cand = video_to_candidate(v, source)
            if cand:
                out.append(cand)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max", type=int, default=DEFAULT_MAX, help="videos per channel")
    args = ap.parse_args()

    candidates = collect(args.max)
    print(f"\nFound {len(candidates)} video candidate(s).")
    if args.dry_run:
        for cand in candidates:
            print(f"   {cand['published']} | {cand['title'][:70]}")
        return 0
    added = c.add_candidates(candidates)
    print(f"Staged {len(added)} new candidate(s) in {c.CANDIDATES_FILE.name}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
