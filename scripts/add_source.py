#!/usr/bin/env python3
"""
add_source.py — Add an approved source to the rankable registry.

Supports the five source shapes the analyzer harvests recurringly:
  x_account      an X/Twitter user to follow      (handle: @user)
  rss / blog     a blog or feed                    (handle: feed URL or site URL — feed auto-discovered)
  newsletter     a newsletter                      (handle: feed URL or site URL — feed auto-discovered)
  github_user    a GitHub user's new work          (handle: username)
  github_query   a GitHub search query             (handle: "query string")
  youtube        a YouTube channel                 (handle: channel URL / @handle / id)
  conference     a conference proceedings/accepted-papers index (handle: index URL)

Ranking is hybrid (tier + reach signals + hit-rate); see sources_registry.py.
Signals: GitHub-user followers are fetched automatically; others may be passed
with --followers/--stars/--subscribers (or left to tier).

Usage:
    python scripts/add_source.py x_account @simonw --topics ai-research --tier high
    python scripts/add_source.py blog https://blog.trailofbits.com --topics product-security
    python scripts/add_source.py github_user praetorian-inc --topics ai-security,product-security
    python scripts/add_source.py youtube https://youtube.com/@LiveOverflow --topics product-security
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys

import sources_registry as sr

FEED_HINTS = ("/feed", "/rss", "/rss.xml", "/atom.xml", "/feed.xml", "/index.xml")
FEED_LINK_RE = re.compile(
    r'<link[^>]+type=["\']application/(?:rss|atom)\+xml["\'][^>]*href=["\']([^"\']+)["\']',
    re.I,
)


def looks_like_feed(text: str) -> bool:
    head = text[:1500].lower()
    return "<rss" in head or "<feed" in head or "<rdf" in head


def discover_feed(url: str) -> str | None:
    """Return a feed URL for a blog/newsletter site (or the URL itself if it is
    already a feed). Best-effort: checks the page's <link> tag then common paths."""
    import requests

    try:
        resp = requests.get(url, timeout=20, headers={"User-Agent": "ASR/1.0"})
        if looks_like_feed(resp.text):
            return url
        m = FEED_LINK_RE.search(resp.text)
        if m:
            href = m.group(1)
            return href if href.startswith("http") else url.rstrip("/") + "/" + href.lstrip("/")
    except Exception:  # noqa: BLE001 - best effort
        pass
    base = url.rstrip("/")
    for hint in FEED_HINTS:
        try:
            r = requests.get(base + hint, timeout=15, headers={"User-Agent": "ASR/1.0"})
            if r.ok and looks_like_feed(r.text):
                return base + hint
        except Exception:  # noqa: BLE001
            continue
    return None


def github_user_followers(user: str) -> int | None:
    try:
        out = subprocess.run(
            ["gh", "api", f"users/{user}", "--jq", ".followers"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        if out.returncode == 0 and out.stdout.strip().isdigit():
            return int(out.stdout.strip())
    except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
        pass
    return None


def resolve(args: argparse.Namespace) -> tuple[str, str, str | None]:
    """Return (stored_type, handle, url) after type-specific normalization."""
    stype, handle = args.type, args.handle.strip()
    if stype in ("blog", "newsletter", "rss"):
        stored = "newsletter" if stype == "newsletter" else "rss"
        if handle.startswith("http") and not looks_feed_url(handle):
            feed = discover_feed(handle)
            if not feed:
                sys.exit(
                    f"Could not find an RSS/Atom feed for {handle}. Pass the feed URL directly."
                )
            return stored, feed, handle
        return stored, handle, handle
    if stype == "x_account":
        h = handle.lstrip("@")
        return "x_account", h, f"https://x.com/{h}"
    if stype == "github_user":
        return "github_user", handle, f"https://github.com/{handle}"
    if stype == "github_query":
        return "github_query", handle, None
    if stype == "conference":
        # Proceedings/accepted-papers index; harvested by the conference ingestor,
        # which resolves each title to a FREE full text (no paywalled fetches).
        return "conference", handle, handle
    if stype == "research_index":
        # A lab's research listing that publishes no feed (JS-rendered index).
        # Same harvest path as `conference`: scrape the index, resolve free text.
        return "research_index", handle, handle
    if stype == "youtube":
        return "youtube", handle, handle if handle.startswith("http") else None
    sys.exit(f"unknown type: {stype}")


def looks_feed_url(url: str) -> bool:
    return any(h in url.lower() for h in ("/feed", "/rss", "/atom", ".xml"))


def collect_signals(args: argparse.Namespace, stored_type: str, handle: str) -> dict:
    signals: dict[str, int] = {}
    for key in ("followers", "stars", "subscribers"):
        val = getattr(args, key, None)
        if val:
            signals[key] = val
    if stored_type == "github_user" and "followers" not in signals:
        f = github_user_followers(handle)
        if f is not None:
            signals["followers"] = f
    return signals


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "type",
        help="x_account|rss|blog|newsletter|github_user|github_query|youtube|conference",
    )
    ap.add_argument("handle", help="@user | feed/site URL | username | query | channel URL")
    ap.add_argument("--name", help="display name")
    ap.add_argument("--topics", help="comma list: ai-security,product-security,ai-research")
    ap.add_argument("--tier", choices=["high", "medium", "low"], default="medium")
    ap.add_argument("--notes")
    ap.add_argument("--followers", type=int)
    ap.add_argument("--stars", type=int)
    ap.add_argument("--subscribers", type=int)
    args = ap.parse_args()

    topics = [t.strip() for t in (args.topics or "").split(",") if t.strip()]
    bad = [t for t in topics if t not in sr.TOPIC_SLUGS]
    if bad:
        sys.exit(f"unknown topic(s) {bad}; valid: {sr.TOPIC_SLUGS}")

    stored_type, handle, url = resolve(args)
    signals = collect_signals(args, stored_type, handle)
    src = sr.new_source(
        stored_type,
        handle,
        name=args.name,
        url=url,
        topics=topics,
        tier=args.tier,
        signals=signals,
        notes=args.notes,
    )
    saved, is_new = sr.add_source(src)
    if not is_new:
        print(f"Already registered: {saved['id']} (rank {saved['rank']})")
        return 0
    print(f"Added source {saved['id']}  ·  rank {saved['rank']}  ·  tier {saved['tier']}")
    print(f"  topics: {saved['topics'] or '(none — will classify at analysis time)'}")
    if signals:
        print(f"  signals: {json.dumps(signals)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
