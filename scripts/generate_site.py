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
    return f"{c.domain_slug(entry.get('domain') or 'General')}/{entry_filename(entry)}"


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
    topic_name = c.TOPICS.get(entry.get("topic", ""), {}).get("name", entry.get("topic", ""))
    meta = [
        f"**Topic:** {topic_name}  ·  **Domain:** {entry.get('domain','—')}",
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


def write_topic(topic: str, conf: c.Config, now: str) -> list[dict]:
    base = c.ROOT / topic
    entries = c.load_pool(topic)["entries"]
    by_domain: dict[str, list[dict]] = defaultdict(list)
    for e in entries:
        by_domain[e.get("domain") or "General"].append(e)

    # Clear stale per-domain dirs, then write a page per entry.
    if base.exists():
        for old in base.glob("*/*.md"):
            old.unlink()
    for domain, items in by_domain.items():
        dpath = base / c.domain_slug(domain)
        dpath.mkdir(parents=True, exist_ok=True)
        for e in items:
            (dpath / entry_filename(e)).write_text(render_entry_page(e, conf), encoding="utf-8")

    meta = c.TOPICS[topic]
    out = [
        f"# {meta['name']}",
        "",
        f"> {meta['blurb']}",
        "",
        f"_{len(entries)} findings · updated {now} · ranked by composite · "
        f"latest {conf.max_age_days} days only._",
        "",
        "| Domain | Findings |",
        "| --- | --- |",
    ]
    for domain in sorted(by_domain, key=lambda d: -len(by_domain[d])):
        out.append(f"| {domain} | {len(by_domain[domain])} |")
    out.append("")
    for domain in sorted(by_domain, key=lambda d: -len(by_domain[d])):
        items = rank(by_domain[domain], conf)
        out += [f"## {domain}", ""]
        out += [render_index_block(e, conf) for e in items]
        out.append("")
    out += [
        "---",
        "",
        "[← Home](../README.md) · [Newsletter](../NEWSLETTER.md) · "
        "[Trends](../TRENDS.md) · [Learnings](../LEARNINGS.md)",
        "",
    ]
    base.mkdir(parents=True, exist_ok=True)
    (base / "README.md").write_text("\n".join(out), encoding="utf-8")
    return entries


TOPIC_EMOJI = {"ai-security": "🤖🛡️", "product-security": "🛡️", "ai-research": "🧠"}


def render_landing(all_entries: list[dict], conf: c.Config, now: str) -> str:
    ranked = rank(all_entries, conf)[:TOP_N_LANDING]
    counts = {t: len(c.load_pool(t)["entries"]) for t in c.TOPICS}
    total = sum(counts.values())
    out = [
        "# Awesome Security & AI Research "
        "[![Awesome](https://cdn.jsdelivr.net/gh/sindresorhus/awesome@d7305f38d29fed78fa85652e3a63e154dd8e8829/media/badge.svg)](https://github.com/sindresorhus/awesome)",
        "",
        "> An auto-updating, source-cited tracker of the most **teachable** security and AI "
        "research — scanned from X/Twitter, GitHub, YouTube, articles, and RSS, then extracted, "
        "scored, and turned into actionable takeaways, skills, and harness improvements.",
        "",
        f"**Only the latest research:** every entry was published within the last "
        f"~{conf.max_age_days} days. Older findings age out to "
        "[`data/archive.json`](data/archive.json) automatically.",
        "",
        f"![Updated](https://img.shields.io/badge/updated-{now.replace('-', '--')}-blue) "
        f"![Findings](https://img.shields.io/badge/findings-{total}-success) "
        "![License](https://img.shields.io/badge/license-CC--BY--4.0-lightgrey)",
        "",
        "Three rolling knowledge bases — plus a [📰 Newsletter](NEWSLETTER.md) and "
        "[📈 Trends](TRENDS.md):",
        "",
    ]
    for t, meta in c.TOPICS.items():
        out.append(
            f"- {TOPIC_EMOJI.get(t, '•')} **[{meta['name']}]({t}/README.md)** "
            f"— {counts[t]} findings. {meta['blurb']}"
        )
    out += ["- 📓 **[Learnings digest](LEARNINGS.md)** — ranked takeaways + generated skills.", ""]
    out += ["## 🔝 Top findings right now", ""]
    if ranked:
        for e in ranked:
            s = entry_scores(e, conf)
            take = e.get("takeaway") or e.get("summary") or e.get("threat") or ""
            tname = c.TOPICS.get(e.get("topic", ""), {}).get("name", e.get("topic", ""))
            out.append(
                f"1. **[{e.get('title','')}]({e['topic']}/{entry_relpath(e)})** "
                f"· {tname} · composite **{s['composite']}**  \n   {c.clean_summary(take, 180)}"
            )
    else:
        out.append("_Run the `/research-scan` skill to populate the pools._")
    out += [
        "",
        "## How it works",
        "",
        "```",
        "X / GitHub / YouTube / articles / RSS  → ingest + Jina Reader (clean text)",
        "  → analyze (extract lessons · score newness/novelty/relevance · derive action)",
        "  → merge into the 3 topic pools → rerank → render + newsletter + trends",
        "```",
        "",
        "Add a single resource: `python scripts/add.py <url>` (`/add-resource`). Add a source "
        "to track: `python scripts/add_source.py …` (`/add-source`). Batch-scan with "
        "`/research-scan` (self-paced via `/loop`).",
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
    for topic in c.TOPICS:
        all_entries += write_topic(topic, conf, now)
    (c.ROOT / "README.md").write_text(render_landing(all_entries, conf, now), encoding="utf-8")
    print(f"Rendered README.md + {'/ '.join(c.TOPICS)}/ ({len(all_entries)} findings).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
