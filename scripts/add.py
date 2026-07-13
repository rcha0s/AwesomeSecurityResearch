#!/usr/bin/env python3
"""
add.py — Ad-hoc: drop in a single article/LinkedIn URL (or pasted text) and
stage it for immediate analysis by the /add-resource skill.

Tries Jina Reader for a URL; LinkedIn and other auth-walled pages often block
the fetch, so `--text`/`--file` are first-class inputs (paste the content).

Usage:
    python scripts/add.py https://example.com/post
    python scripts/add.py https://linkedin.com/posts/... --text "pasted body..."
    python scripts/add.py --file article.txt --title "My title" --track ai
"""

from __future__ import annotations

import argparse
import sys

import common as c


def source_via(url: str) -> str:
    host = (url or "").lower()
    if "linkedin.com" in host:
        return "linkedin"
    if "twitter.com" in host or "x.com" in host:
        return "twitter"
    return "manual"


def resolve_text(args: argparse.Namespace) -> tuple[str, bool]:
    """Return (text, fetched_from_url)."""
    if args.text:
        return args.text.strip(), False
    if args.file:
        return c.Path(args.file).read_text(encoding="utf-8").strip(), False
    if args.url:
        try:
            return c.fetch_readable(args.url), True
        except Exception as exc:  # noqa: BLE001 - surface a helpful fallback
            print(
                f"Could not fetch {args.url} ({exc}).\n"
                "This is common for LinkedIn / auth-walled pages. Re-run with the\n"
                'content pasted in:  python scripts/add.py <url> --text "<paste>"\n'
                "                or:  python scripts/add.py <url> --file body.txt",
                file=sys.stderr,
            )
            raise SystemExit(2) from exc
    raise SystemExit("Provide a URL, or --text, or --file.")


def build_candidate(args: argparse.Namespace, text: str) -> dict:
    url = args.url or ""
    title = args.title or (text.splitlines()[0][:120] if text else "Untitled resource")
    cand_id = c.make_id(title, c.normalize_url(url) or title)
    raw_path = c.write_raw(cand_id, text) if text else None
    topic = None if args.topic == "auto" else args.topic
    return {
        "id": cand_id,
        "discovered_via": source_via(url),
        "title": title,
        "source_name": args.author or (url.split("/")[2] if url else "Manual add"),
        "source_type": "Manual add",
        "source_url": url or f"manual:{cand_id}",
        "article_url": url or None,
        "tweet_url": None,
        "author": args.author,
        "published": args.date or c.date_from_url(url),
        "date": c.to_month(args.date or c.date_from_url(url)),
        "excerpt": c.clean_summary(text, 320),
        "raw_path": raw_path,
        "guess_topic": topic,
        "guess_domain": None,
        "guess_subtype": None,
        "retrieved_at": c.utcnow_iso(),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url", nargs="?", help="article / LinkedIn / post URL")
    ap.add_argument("--text", help="paste the resource body (fetch fallback)")
    ap.add_argument("--file", help="read the resource body from a file")
    ap.add_argument("--title", help="explicit title")
    ap.add_argument("--author", help="author / byline")
    ap.add_argument("--date", help="publish date YYYY-MM (optional)")
    ap.add_argument(
        "--topic",
        choices=["auto", "ai-security", "product-security", "ai-research"],
        default="auto",
        help="topic hint; 'auto' lets the analyzer decide",
    )
    args = ap.parse_args()

    text, fetched = resolve_text(args)
    cand = build_candidate(args, text)
    added = c.add_candidates([cand])
    if not added:
        print(f"Already in the pool or staging queue: {cand['title']}")
        return 0
    src = "fetched" if fetched else "pasted"
    print(f"Staged ({src}) candidate: {cand['title']}")
    print(f"  id: {cand['id']}  ·  raw: {cand['raw_path']}")
    print("Next: run the /add-resource skill to analyze, merge, re-rank, and render.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
