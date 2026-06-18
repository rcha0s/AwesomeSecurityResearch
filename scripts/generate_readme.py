#!/usr/bin/env python3
"""
generate_readme.py — Render README.md from data/research.json.

The data file is the single source of truth. This script produces a polished,
"awesome-list"-style README with per-domain sections, subtype grouping, and a
Threat / Conditions / Mitigations / Source block for every entry.

Usage:
    python scripts/generate_readme.py
"""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "research.json"
README = ROOT / "README.md"

DOMAIN_ORDER = ["AI Security", "Web Application Security", "Mobile Security"]
DOMAIN_ANCHOR = {
    "AI Security": "ai-security",
    "Web Application Security": "web-application-security",
    "Mobile Security": "mobile-security",
}
SEV_BADGE = {
    "Critical": "🔴 Critical",
    "High": "🟠 High",
    "Medium": "🟡 Medium",
    "Low": "🟢 Low",
    "Unrated": "⚪ Unrated",
}


def load_data() -> dict:
    with DATA_FILE.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def fmt_date(d: str) -> str:
    try:
        return datetime.strptime(d, "%Y-%m").strftime("%b %Y")
    except ValueError:
        return d or "—"


def entry_block(e: dict) -> str:
    sev = SEV_BADGE.get(e.get("severity", "Unrated"), e.get("severity", ""))
    flag = " · _pending review_" if e.get("needs_review") else ""
    lines = [
        f"#### {e['title']}",
        "",
        f"**Severity:** {sev}  ·  **Disclosed:** {fmt_date(e.get('date',''))}  ·  "
        f"**Subtype:** {e.get('subtype','—')}{flag}",
        "",
        f"- **Threat —** {e.get('threat','').strip()}",
        f"- **Conditions —** {e.get('conditions','').strip()}",
        f"- **Mitigations —** {e.get('mitigations','').strip()}",
        f"- **Source —** [{e.get('source_name','')}]({e.get('source_url','')}) "
        f"*( {e.get('source_type','')} )*",
        "",
    ]
    return "\n".join(lines)


def build() -> str:
    data = load_data()
    entries = data["entries"]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    by_domain: dict[str, list[dict]] = defaultdict(list)
    for e in entries:
        by_domain[e["domain"]].append(e)

    total = len(entries)
    curated = sum(1 for e in entries if not e.get("needs_review"))
    pending = total - curated

    out: list[str] = []
    # ---- Header ----------------------------------------------------------
    out.append("# Awesome Security Research [![Awesome](https://cdn.jsdelivr.net/gh/sindresorhus/awesome@d7305f38d29fed78fa85652e3a63e154dd8e8829/media/badge.svg)](https://github.com/sindresorhus/awesome)")
    out.append("")
    out.append("> A continuously updated, source-cited tracker of the most relevant **new** security research across **AI Security**, **Web Application Security**, and **Mobile Security** — covering the trailing six months only.")
    out.append("")
    out.append(
        "![Last updated](https://img.shields.io/badge/updated-{date}-blue) "
        "![Entries](https://img.shields.io/badge/tracked_findings-{total}-success) "
        "![Window](https://img.shields.io/badge/window-last_6_months-orange) "
        "![License](https://img.shields.io/badge/license-CC--BY--4.0-lightgrey)".format(
            date=now.replace("-", "--"), total=total
        )
    )
    out.append("")
    out.append("Every entry distills a single finding into four things: the **threat**, the **conditions** under which it applies, the **mitigations**, and a link to the **original credible source**. Sources are limited to first-party security researchers, vendor research teams, standards bodies, and peer-reviewed venues. News aggregators and rumor are excluded by design.")
    out.append("")

    # ---- Why trust this --------------------------------------------------
    out.append("## Why this list")
    out.append("")
    out.append("- **New, not noise.** Only research disclosed in the trailing six months is kept; older findings age out automatically.")
    out.append("- **Credible by construction.** Sources are an allow-list of recognized research teams and standards bodies (see [Sources & Methodology](#sources--methodology)).")
    out.append("- **Actionable.** Each finding is summarized as threat → conditions → mitigations, so it is usable by defenders, not just readers.")
    out.append("- **Auditable & automated.** A scheduled job pulls fresh research from source feeds; the curated set is human-reviewed. The data lives in [`data/research.json`](data/research.json) as the single source of truth.")
    out.append("")

    # ---- Stats -----------------------------------------------------------
    out.append("## At a glance")
    out.append("")
    out.append("| Domain | Findings | Subtypes |")
    out.append("| --- | --- | --- |")
    for domain in DOMAIN_ORDER:
        items = by_domain.get(domain, [])
        subtypes = sorted({i.get("subtype", "—") for i in items})
        out.append(
            f"| [{domain}](#{DOMAIN_ANCHOR[domain]}) | {len(items)} | {', '.join(subtypes)} |"
        )
    out.append(f"| **Total** | **{total}** | {curated} curated · {pending} pending review |")
    out.append("")

    # ---- TOC -------------------------------------------------------------
    out.append("## Contents")
    out.append("")
    for domain in DOMAIN_ORDER:
        out.append(f"- [{domain}](#{DOMAIN_ANCHOR[domain]})")
    out.append("- [Sources & Methodology](#sources--methodology)")
    out.append("- [How it stays current](#how-it-stays-current)")
    out.append("- [Contributing](#contributing)")
    out.append("- [License](#license)")
    out.append("")

    # ---- Domain sections -------------------------------------------------
    sev_rank = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Unrated": 4}
    for domain in DOMAIN_ORDER:
        items = by_domain.get(domain, [])
        out.append("---")
        out.append("")
        out.append(f"## {domain}")
        out.append("")
        if not items:
            out.append("_No current findings in this window._")
            out.append("")
            continue
        by_sub: dict[str, list[dict]] = defaultdict(list)
        for e in items:
            by_sub[e.get("subtype", "Uncategorized")].append(e)
        for subtype in sorted(by_sub):
            out.append(f"### {subtype}")
            out.append("")
            ordered = sorted(
                by_sub[subtype],
                key=lambda e: (sev_rank.get(e.get("severity", "Unrated"), 9), e.get("date", "")),
            )
            for e in ordered:
                out.append(entry_block(e))

    # ---- Methodology -----------------------------------------------------
    out.append("---")
    out.append("")
    out.append("## Sources & Methodology")
    out.append("")
    out.append("Findings are sourced from a curated allow-list of credible security research publishers. The feed configuration lives in [`scripts/sources.yaml`](scripts/sources.yaml). Current sources include:")
    out.append("")
    out.append("| Source | Type | Primary coverage |")
    out.append("| --- | --- | --- |")
    seen = set()
    for e in sorted(entries, key=lambda x: x.get("source_name", "")):
        name = e.get("source_name", "")
        if name in seen:
            continue
        seen.add(name)
        out.append(f"| [{name}]({e.get('source_url','')}) | {e.get('source_type','')} | {e.get('domain','')} |")
    out.append("")
    out.append("**Inclusion criteria:** (1) first-party research from a recognized team, vendor lab, standards body, or peer-reviewed venue; (2) disclosed within the last six months; (3) a clear, defensible threat with practical mitigations. **Severity** ratings are editorial, harmonized to a Critical/High/Medium/Low scale.")
    out.append("")

    # ---- Automation ------------------------------------------------------
    out.append("## How it stays current")
    out.append("")
    out.append("```")
    out.append("scripts/aggregate.py        # pull feeds -> classify -> filter to last 6 months -> append new items")
    out.append("scripts/generate_readme.py  # render this README from data/research.json")
    out.append("```")
    out.append("")
    out.append("A GitHub Actions workflow ([`.github/workflows/update.yml`](.github/workflows/update.yml)) runs weekly: it executes the aggregator, regenerates the README, and opens a commit when anything changes. Auto-discovered items are flagged `pending review` until a maintainer writes the threat/conditions/mitigations and assigns a severity. To run it locally:")
    out.append("")
    out.append("```bash")
    out.append("pip install -r requirements.txt")
    out.append("python scripts/aggregate.py        # add newly published research")
    out.append("python scripts/generate_readme.py  # rebuild README.md")
    out.append("```")
    out.append("")

    # ---- Contributing / License -----------------------------------------
    out.append("## Contributing")
    out.append("")
    out.append("Contributions are welcome. Add or refine an entry in [`data/research.json`](data/research.json), run `python scripts/generate_readme.py`, and open a PR. Please keep the source allow-list standard high — see [CONTRIBUTING.md](CONTRIBUTING.md).")
    out.append("")
    out.append("## License")
    out.append("")
    out.append("Curated content is released under [CC BY 4.0](LICENSE); the scripts are under the MIT terms noted in [`scripts/`](scripts/). Linked research remains the property of its original authors.")
    out.append("")
    out.append("---")
    out.append("")
    out.append(f"<sub>Generated by <code>scripts/generate_readme.py</code> on {now}. Do not edit README.md by hand — edit <code>data/research.json</code> and regenerate.</sub>")
    out.append("")
    return "\n".join(out)


def main() -> int:
    README.write_text(build(), encoding="utf-8")
    print(f"Wrote {README.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
