#!/usr/bin/env python3
"""
ingest_ghsa.py — Discover reviewed supply-chain advisories from the GitHub
Advisory Database (GHSA).

Pulls recently-published, human-reviewed advisories via the authed `gh` CLI
(`gh api /advisories`), keeps those inside the freshness window, classifies each
(supply-chain by default; AI Security when the summary matches AI keywords), and
stages them as candidates. GHSA is a disclosure-velocity signal for the
dependency/package attack surface — the material an appsec reader must track.

Runs on Windows or WSL (needs `gh` authenticated). No LLM here.

Usage:
    python scripts/ingest_ghsa.py --dry-run
    python scripts/ingest_ghsa.py --max 20
"""

from __future__ import annotations

import argparse
import json

import aggregate as agg
import common as c
from ingest_github import run_gh

AI_KEYWORDS = ("llm", "prompt injection", "genai", "agent", "mcp", "model", "ml ")


def fetch_advisories(limit: int) -> list[dict]:
    """Recently-published reviewed advisories, newest first. [] on any failure."""
    out = run_gh(
        [
            "api",
            f"/advisories?type=reviewed&sort=published&direction=desc&per_page={limit}",
        ],
        timeout=60,
    )
    if not out:
        return []
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def _affected_packages(adv: dict) -> str:
    """A short 'ecosystem/name' summary of the affected packages, for the excerpt."""
    pkgs = []
    for v in adv.get("vulnerabilities") or []:
        pkg = (v or {}).get("package") or {}
        eco, name = pkg.get("ecosystem"), pkg.get("name")
        if name:
            pkgs.append(f"{eco}/{name}" if eco else name)
    return ", ".join(dict.fromkeys(pkgs))  # dedup, keep order


def advisory_to_candidate(adv: dict, rules: dict) -> dict | None:
    """Map a GHSA advisory to a candidate; None if it lacks an id/url."""
    ghsa_id = adv.get("ghsa_id") or ""
    url = adv.get("html_url") or ""
    summary = (adv.get("summary") or "").strip()
    if not ghsa_id or not c.normalize_url(url):
        return None
    packages = _affected_packages(adv)
    description = c.clean_summary(adv.get("description") or "", 600)
    blob = f"{summary} {packages} {description}".lower()
    # AI-package advisories route to AI Security; everything else is supply chain.
    if any(kw in blob for kw in AI_KEYWORDS):
        domain = "AI Security"
    else:
        domain = agg.classify_domain(blob, rules, []) or "Supply Chain & Dependencies"
    severity = (adv.get("severity") or "").upper()
    published = (adv.get("published_at") or "")[:10] or None
    title = summary or ghsa_id
    cand_id = c.make_id(ghsa_id, c.normalize_url(url))
    return {
        "id": cand_id,
        "discovered_via": "github",
        "title": f"{title} ({ghsa_id})",
        "source_name": "GitHub Advisory Database",
        "source_type": "GHSA",
        "source_url": url,
        "article_url": url,
        "tweet_url": None,
        "author": None,
        "published": published,
        "date": published[:7] if published else None,
        "excerpt": c.clean_summary(
            f"[{severity}] {summary} — affects {packages or 'n/a'}. {description}", 400
        ),
        "raw_path": None,
        "guess_topic": c.topic_for_domain(domain) or "product-security",
        "guess_domain": domain,
        "guess_subtype": agg.classify_subtype(blob, domain, rules),
        "severity": severity,
        "source_id": None,
        "source_rank": 70.0,  # first-party GitHub, human-reviewed
        "source_topics": [],
        "retrieved_at": c.utcnow_iso(),
    }


def collect(cfg: dict, rules: dict, limit: int | None) -> list[dict]:
    ghsa_cfg = cfg.get("ghsa", {})
    if not ghsa_cfg.get("enabled", True):
        print("   (ghsa ingestion disabled in sources.yaml)")
        return []
    per_run = limit or ghsa_cfg.get("per_run", 20)
    conf = c.load_config()
    print(f"-> gh api /advisories (reviewed, newest {per_run}, last {conf.max_age_days}d)")
    out: list[dict] = []
    for adv in fetch_advisories(per_run):
        cand = advisory_to_candidate(adv, rules)
        if cand and c.is_fresh(cand, conf.max_age_days):
            out.append(cand)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max", type=int, default=None, help="override advisory count")
    args = ap.parse_args()

    cfg = c.load_yaml(c.SOURCES_FILE)
    rules = cfg["classification"]
    candidates = collect(cfg, rules, args.max)
    print(f"\nFound {len(candidates)} GHSA candidate(s).")

    if args.dry_run:
        for cand in candidates:
            print(f"   [{cand['guess_topic']}/{cand['guess_domain']}] {cand['title']}")
        return 0

    added = c.add_candidates(candidates)
    print(f"Staged {len(added)} new candidate(s) in {c.CANDIDATES_FILE.name}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
