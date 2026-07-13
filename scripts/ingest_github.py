#!/usr/bin/env python3
"""
ingest_github.py — Discover trending/novel security & AI repos via `gh search`.

Runs the queries in sources.yaml `github:` against GitHub (using the authed `gh`
CLI), filters by stars + recency (bias toward genuinely new work), fetches each
repo's README for grounding, and stages candidates in data/candidates.json. The
LLM analyze step (the /research-scan skill) judges novelty and curates — well-
known or derivative repos score low and are held by the curation gate.

Runs on Windows or WSL (needs `gh` authenticated). No LLM here.

Usage:
    python scripts/ingest_github.py --dry-run
    python scripts/ingest_github.py --max 5
"""

from __future__ import annotations

import argparse
import base64
import json
import subprocess
import sys
from datetime import UTC, datetime, timedelta

import common as c

REPO_FIELDS = "fullName,description,url,stargazersCount,updatedAt,createdAt"


def run_gh(args: list[str], timeout: int = 60) -> str | None:
    try:
        proc = subprocess.run(
            ["gh", *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        print(f"   ! gh unavailable ({exc.__class__.__name__})", file=sys.stderr)
        return None
    if proc.returncode != 0:
        print(f"   ! gh {' '.join(args)} failed: {proc.stderr.strip()[:160]}", file=sys.stderr)
        return None
    return proc.stdout


def search_repos(query: str, limit: int, created_after: str) -> list[dict]:
    full_query = f"{query} created:>{created_after}"
    out = run_gh(
        [
            "search",
            "repos",
            full_query,
            "--sort",
            "stars",
            "--order",
            "desc",
            "--limit",
            str(limit),
            "--json",
            REPO_FIELDS,
        ]
    )
    if not out:
        return []
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return []


def fetch_readme(full_name: str, max_chars: int) -> str | None:
    out = run_gh(["api", f"repos/{full_name}/readme", "--jq", ".content"], timeout=40)
    if not out:
        return None
    try:
        text = base64.b64decode(out.strip()).decode("utf-8", "replace")
    except (ValueError, UnicodeDecodeError):
        return None
    return text[:max_chars] if text.strip() else None


def repo_to_candidate(repo: dict, q: dict, fetch: bool, max_chars: int) -> dict:
    full_name = repo.get("fullName", "")
    url = repo.get("url", "")
    stars = repo.get("stargazersCount", 0)
    desc = repo.get("description") or ""
    created = repo.get("createdAt", "")
    cand_id = c.make_id(full_name, c.normalize_url(url))
    raw_path = None
    if fetch:
        readme = fetch_readme(full_name, max_chars)
        if readme:
            raw_path = c.write_raw(cand_id, f"# {full_name} ({stars} stars)\n{desc}\n\n{readme}")
    return {
        "id": cand_id,
        "discovered_via": "github",
        "title": full_name,
        "source_name": full_name,
        "source_type": "GitHub repository",
        "source_url": url,
        "article_url": url,
        "tweet_url": None,
        "author": full_name.split("/")[0] if "/" in full_name else None,
        "date": created[:7] if len(created) >= 7 else None,
        "excerpt": c.clean_summary(f"{desc} ({stars} stars)", 320),
        "raw_path": raw_path,
        "stars": stars,
        "guess_track": q.get("track"),
        "guess_domain": q.get("domain"),
        "guess_subtype": None,
        "retrieved_at": c.utcnow_iso(),
    }


def collect(cfg: dict, per_query: int | None, fetch: bool) -> list[dict]:
    gh_cfg = cfg.get("github", {})
    if not gh_cfg.get("queries"):
        print("   (no github.queries configured)")
        return []
    min_stars = gh_cfg.get("min_stars", 0)
    limit = per_query or gh_cfg.get("per_query", 8)
    max_chars = c.load_config().limits.get("article_chars", 20000)
    cutoff = datetime.now(UTC) - timedelta(days=gh_cfg.get("max_age_days", 200))
    created_after = cutoff.strftime("%Y-%m-%d")

    out: list[dict] = []
    for q in gh_cfg["queries"]:
        print(f"-> gh search: {q['query']} (>= {min_stars} stars, created > {created_after})")
        for repo in search_repos(q["query"], limit, created_after):
            if repo.get("stargazersCount", 0) < min_stars:
                continue
            out.append(repo_to_candidate(repo, q, fetch, max_chars))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max", type=int, default=None, help="override per-query limit")
    ap.add_argument("--no-fetch", action="store_true", help="skip README fetch")
    args = ap.parse_args()

    cfg = c.load_yaml(c.SOURCES_FILE)
    candidates = collect(cfg, args.max, fetch=not args.no_fetch)
    print(f"\nFound {len(candidates)} repo candidate(s).")

    if args.dry_run:
        for cand in candidates:
            print(
                f"   [{cand['guess_track']}/{cand['guess_domain']}] {cand['title']} "
                f"({cand['stars']} stars)"
            )
        return 0

    added = c.add_candidates(candidates)
    print(f"Staged {len(added)} new candidate(s) in {c.CANDIDATES_FILE.name}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
