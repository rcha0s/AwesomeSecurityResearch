#!/usr/bin/env python3
"""
generate_site.py — Render the two knowledge directories from the pools.

Reads data/security.json + data/ai.json and writes:
  - README.md               landing page (what this is + global Top-10 learnings)
  - security/README.md      ranked Security-track index
  - ai/README.md            ranked AI-track index
  - <track>/<domain>/<YYYY-MM>-<slug>.md   one citation-first page per finding

Ranking uses each entry's composite score (rerank.py fills these); entries with
no scores yet are ranked by a live-computed newness so legacy items still sort.
Do not hand-edit generated files — edit the pools and regenerate.

Usage:
    python scripts/generate_site.py
"""

from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime

import common as c

TOP_N_LANDING = 10


def fmt_month(date: str) -> str:
    for fmt in ("%Y-%m-%d", "%Y-%m"):
        try:
            return datetime.strptime(date, fmt).strftime("%b %Y")
        except (ValueError, TypeError):
            continue
    return date or "—"


def fmt_published(entry: dict) -> str:
    """Human-readable source publish date, day-precision when known."""
    pub = entry.get("published") or entry.get("date") or ""
    try:
        return datetime.strptime(pub, "%Y-%m-%d").strftime("%b %-d, %Y")
    except (ValueError, TypeError):
        pass
    try:  # Windows strftime has no %-d
        return datetime.strptime(pub, "%Y-%m-%d").strftime("%b %d, %Y").replace(" 0", " ")
    except (ValueError, TypeError):
        return fmt_month(pub)


def entry_scores(entry: dict, conf: c.Config) -> dict:
    scores = dict(entry.get("scores") or {})
    if "newness" not in scores:
        scores["newness"] = c.newness_score(entry.get("date") or "", conf.half_life_days)
    scores.setdefault("novelty", 0)
    scores.setdefault("relevance", 0)
    if "composite" not in scores:
        scores["composite"] = c.composite_score(scores, conf.weights)
    return scores


def rank(entries: list[dict], conf: c.Config) -> list[dict]:
    return sorted(
        entries,
        key=lambda e: (
            -entry_scores(e, conf)["composite"],
            e.get("date") or "",
            e.get("title", ""),
        ),
    )


def entry_filename(entry: dict) -> str:
    return f"{(entry.get('date') or 'undated')}-{c.slugify(entry.get('title',''), 60)}.md"


def entry_relpath(entry: dict) -> str:
    return f"{c.domain_slug(entry['domain'])}/{entry_filename(entry)}"


def score_line(scores: dict) -> str:
    return (
        f"**Scores:** 🆕 Newness {scores['newness']} · ✨ Novelty {scores['novelty']} · "
        f"🎯 Relevance {scores['relevance']} · **Composite {scores['composite']}**"
    )


def render_actionable(entry: dict) -> list[str]:
    act = entry.get("actionable")
    if not isinstance(act, dict):
        return []
    kind = act.get("type", "takeaway")
    line = f"**[{kind}]** {act.get('title','')} — {act.get('detail','')}".rstrip(" —")
    out = ["## Actionable leverage", "", line]
    if kind == "skill" and act.get("skill_slug"):
        out.append("")
        out.append(
            f"→ Generated skill: [`skills/{act['skill_slug']}`](../../skills/{act['skill_slug']}/SKILL.md)"
        )
    out.append("")
    return out


def render_entry_page(entry: dict, conf: c.Config) -> str:
    scores = entry_scores(entry, conf)
    src = entry.get("source_url", "")
    meta = [
        f"**Track:** {entry.get('track','').title()}  ·  **Domain:** {entry.get('domain','')}"
        f"  ·  **Subtype:** {entry.get('subtype','—')}",
        f"**Source:** [{entry.get('source_name','source')}]({src})"
        + (f"  ·  **Author:** {entry['author']}" if entry.get("author") else "")
        + f"  ·  **Published:** {fmt_published(entry)}"
        + (
            f"  ·  **Retrieved:** {entry['retrieved_at'][:10]}" if entry.get("retrieved_at") else ""
        ),
        score_line(scores),
    ]
    if entry.get("tags"):
        meta.append("**Tags:** " + ", ".join(f"`{t}`" for t in entry["tags"]))
    if entry.get("needs_review"):
        meta.append("> ⚠️ _Pending review — auto-analyzed, not yet human-verified._")

    out = [f"# {entry.get('title','Untitled')}", "", "  \n".join(meta), ""]
    if entry.get("takeaway"):
        out += [f"> **Takeaway —** {entry['takeaway']}", ""]
    if entry.get("summary"):
        out += ["## Summary", "", entry["summary"].strip(), ""]

    lessons = entry.get("lessons") or []
    if lessons:
        out += ["## What to learn", ""]
        for les in lessons:
            if isinstance(les, dict):
                line = f"- {les.get('point','')}"
                if les.get("excerpt"):
                    line += f' — _"{les["excerpt"]}"_'
                out.append(line)
            else:
                out.append(f"- {les}")
        out.append("")

    if any(entry.get(k) for k in ("threat", "conditions", "mitigations")):
        out += ["## Threat · Conditions · Mitigations", ""]
        for label in ("threat", "conditions", "mitigations"):
            if entry.get(label):
                out.append(f"- **{label.title()} —** {entry[label].strip()}")
        out.append("")

    out += render_actionable(entry)
    out += ["---", "", f"_Source: [{src}]({src})_  ·  [← back to index](../README.md)", ""]
    return "\n".join(out)


def render_index_block(entry: dict, conf: c.Config) -> str:
    scores = entry_scores(entry, conf)
    takeaway = entry.get("takeaway") or entry.get("summary") or entry.get("threat") or ""
    flag = " · ⚠️ _review_" if entry.get("needs_review") else ""
    return (
        f"- **[{entry.get('title','Untitled')}]({entry_relpath(entry)})** "
        f"· composite **{scores['composite']}** · {fmt_published(entry)}{flag}  \n"
        f"  {c.clean_summary(takeaway, 200)}  \n"
        f"  _[{entry.get('source_name','source')}]({entry.get('source_url','')})_"
    )


def write_track(track: str, conf: c.Config, now: str) -> list[dict]:
    base = c.ROOT / track
    entries = c.load_pool(track)["entries"]
    by_domain: dict[str, list[dict]] = defaultdict(list)
    for e in entries:
        by_domain[e.get("domain", "Uncategorized")].append(e)

    for domain in c.TRACK_DOMAINS[track]:
        dpath = base / c.domain_slug(domain)
        if dpath.exists():
            for old in dpath.glob("*.md"):
                old.unlink()
        for e in by_domain.get(domain, []):
            page = render_entry_page(e, conf)
            (dpath).mkdir(parents=True, exist_ok=True)
            (dpath / entry_filename(e)).write_text(page, encoding="utf-8")

    title = "Security Research" if track == "security" else "AI Research"
    out = [
        f"# {title}",
        "",
        f"> {len(entries)} findings · updated {now} · ranked by composite score.",
        "",
    ]
    out += ["| Domain | Findings |", "| --- | --- |"]
    for domain in c.TRACK_DOMAINS[track]:
        out.append(f"| {domain} | {len(by_domain.get(domain, []))} |")
    out.append("")
    for domain in c.TRACK_DOMAINS[track]:
        items = rank(by_domain.get(domain, []), conf)
        if not items:
            continue
        out += [f"## {domain}", ""]
        out += [render_index_block(e, conf) for e in items]
        out.append("")
    out += ["---", "", "[← Home](../README.md) · [Learnings digest](../LEARNINGS.md)", ""]
    (base / "README.md").parent.mkdir(parents=True, exist_ok=True)
    (base / "README.md").write_text("\n".join(out), encoding="utf-8")
    return entries


def render_landing(all_entries: list[dict], conf: c.Config, now: str) -> str:
    ranked = rank(all_entries, conf)[:TOP_N_LANDING]
    counts = {t: len(c.load_pool(t)["entries"]) for t in c.TRACK_DOMAINS}
    total = sum(counts.values())
    out = [
        "# Awesome Security & AI Research "
        "[![Awesome](https://cdn.jsdelivr.net/gh/sindresorhus/awesome@d7305f38d29fed78fa85652e3a63e154dd8e8829/media/badge.svg)](https://github.com/sindresorhus/awesome)",
        "",
        "> An auto-updating, source-cited tracker of the most **teachable** security and AI "
        "research — scanned from X/Twitter, GitHub, articles, and RSS, then extracted, scored, "
        "and turned into actionable takeaways, skills, and harness improvements.",
        "",
        f"**Only the latest research:** every entry was published within the last "
        f"~{conf.max_age_days} days. Older findings age out to "
        "[`data/archive.json`](data/archive.json) automatically.",
        "",
        f"![Updated](https://img.shields.io/badge/updated-{now.replace('-', '--')}-blue) "
        f"![Findings](https://img.shields.io/badge/findings-{total}-success) "
        f"![Security](https://img.shields.io/badge/security-{counts['security']}-orange) "
        f"![AI](https://img.shields.io/badge/AI-{counts['ai']}-purple) "
        "![License](https://img.shields.io/badge/license-CC--BY--4.0-lightgrey)",
        "",
        "Two growing knowledge directories:",
        "",
        f"- 🛡️ **[Security Research](security/README.md)** — {counts['security']} findings (AI, Web, Mobile).",
        f"- 🤖 **[AI Research](ai/README.md)** — {counts['ai']} findings (agents, harnesses, prompting, models, tooling, evaluation).",
        "- 📓 **[Learnings digest](LEARNINGS.md)** — ranked takeaways + generated skills.",
        "",
        "## 🔝 Top learnings right now",
        "",
    ]
    if ranked:
        for e in ranked:
            s = entry_scores(e, conf)
            take = e.get("takeaway") or e.get("summary") or e.get("threat") or ""
            out.append(
                f"1. **[{e.get('title','')}]({e['track']}/{entry_relpath(e)})** "
                f"· {e['track']} · composite **{s['composite']}**  \n   {c.clean_summary(take, 180)}"
            )
    else:
        out.append("_Run the `/research-scan` skill to populate the pool._")
    out += [
        "",
        "## How it works",
        "",
        "```",
        "X feed / LinkedIn / articles / RSS   → ingest + Jina Reader (clean text)",
        "  → analyze (extract lessons · score newness/novelty/relevance · derive action)",
        "  → merge into data/{security,ai}.json → rerank → render these directories",
        "```",
        "",
        "Add a single resource anytime: `python scripts/add.py <url>` then the `/add-resource` "
        "skill. Batch-scan your X feed with the `/research-scan` skill (self-paced via `/loop`).",
        "",
        "## License",
        "",
        "Curated content under [CC BY 4.0](LICENSE); scripts under MIT. Linked research remains "
        "the property of its original authors — every finding cites its source.",
        "",
        f"<sub>Generated by <code>scripts/generate_site.py</code> on {now}. "
        "Edit the pools in <code>data/</code> and regenerate — do not hand-edit rendered files.</sub>",
        "",
    ]
    return "\n".join(out)


def main() -> int:
    conf = c.load_config()
    now = datetime.now(UTC).strftime("%Y-%m-%d")
    all_entries: list[dict] = []
    for track in c.TRACK_DOMAINS:
        all_entries += write_track(track, conf, now)
    (c.ROOT / "README.md").write_text(render_landing(all_entries, conf, now), encoding="utf-8")
    print(f"Rendered README.md + security/ + ai/ ({len(all_entries)} findings).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
