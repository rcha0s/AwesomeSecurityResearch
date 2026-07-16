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
    scores.setdefault("credibility", c.credibility_of(entry))
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
        f"🎯 Relevance {scores['relevance']} · 🏛️ Credibility {round(scores.get('credibility', 50))} · "
        f"**Composite {scores['composite']}**"
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


def _entry_meta(entry: dict, scores: dict) -> list[str]:
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
    corr = entry.get("corroborating_sources") or []
    if corr:
        links = ", ".join(f"[{s.get('name') or 'source'}]({s.get('url','')})" for s in corr)
        meta.append(f"**Also reported by:** {links} _(+{len(corr)} corroborating)_")
    verified = entry.get("verified")
    if verified is True:
        line = "**Verification:** ✓ independently verified"
        if entry.get("prior_art"):
            line += f" · closest prior art: {entry['prior_art']}"
        meta.append(line)
    elif verified is False:
        meta.append("> ⚠️ _Failed independent verification._")
    if entry.get("needs_review"):
        meta.append("> ⚠️ _Pending review — auto-analyzed, not yet human-verified._")
    return meta


def _grounding_mark(les: dict) -> str:
    grounded = les.get("grounded")
    if grounded is True:
        return " ✅"
    if grounded is False:
        return " ⚠️ _(excerpt not found in source)_"
    return ""


def _entry_lessons_md(entry: dict) -> list[str]:
    lessons = entry.get("lessons") or []
    if not lessons:
        return []
    out = ["## What to learn", ""]
    for les in lessons:
        if isinstance(les, dict):
            line = f"- {les.get('point','')}"
            if les.get("excerpt"):
                line += f' — _"{les["excerpt"]}"_{_grounding_mark(les)}'
            out.append(line)
        else:
            out.append(f"- {les}")
    return out + [""]


def _entry_tcm_md(entry: dict) -> list[str]:
    if not any(entry.get(k) for k in ("threat", "conditions", "mitigations")):
        return []
    out = ["## Threat · Conditions · Mitigations", ""]
    for label in ("threat", "conditions", "mitigations"):
        if entry.get(label):
            out.append(f"- **{label.title()} —** {entry[label].strip()}")
    return out + [""]


def render_entry_page(entry: dict, conf: c.Config) -> str:
    src = entry.get("source_url", "")
    out = [
        f"# {entry.get('title','Untitled')}",
        "",
        "  \n".join(_entry_meta(entry, entry_scores(entry, conf))),
        "",
    ]
    if entry.get("takeaway"):
        out += [f"> **Takeaway —** {entry['takeaway']}", ""]
    if entry.get("summary"):
        out += ["## Summary", "", entry["summary"].strip(), ""]
    out += _entry_lessons_md(entry)
    out += _entry_tcm_md(entry)
    out += render_actionable(entry)
    out += ["---", "", f"_Source: [{src}]({src})_  ·  [← back to index](../README.md)", ""]
    return "\n".join(out)


def render_index_block(entry: dict, conf: c.Config) -> str:
    scores = entry_scores(entry, conf)
    takeaway = entry.get("takeaway") or entry.get("summary") or entry.get("threat") or ""
    flag = " · ⚠️ _review_" if entry.get("needs_review") else ""
    n_corr = len(entry.get("corroborating_sources") or [])
    corr = f" · 🔗 +{n_corr} sources" if n_corr else ""
    return (
        f"- **[{entry.get('title','Untitled')}]({entry_relpath(entry)})** "
        f"· composite **{scores['composite']}** · {fmt_published(entry)}{corr}{flag}  \n"
        f"  {c.clean_summary(takeaway, 200)}  \n"
        f"  _[{entry.get('source_name','source')}]({entry.get('source_url','')})_"
    )


def _write_entry_pages(base: c.Path, by_domain: dict[str, list[dict]], conf: c.Config) -> None:
    if base.exists():  # clear stale per-domain pages first
        for old in base.glob("*/*.md"):
            old.unlink()
    for domain, items in by_domain.items():
        dpath = base / c.domain_slug(domain)
        dpath.mkdir(parents=True, exist_ok=True)
        for e in items:
            (dpath / entry_filename(e)).write_text(render_entry_page(e, conf), encoding="utf-8")


def _topic_index_md(topic: str, by_domain: dict, curated: list, held: int, conf, now) -> str:
    meta = c.TOPICS[topic]
    held_note = f" · [{held} held for review](../REVIEW.md)" if held else ""
    out = [
        f"# {meta['name']}",
        "",
        f"> {meta['blurb']}",
        "",
        f"_{len(curated)} vetted findings · updated {now} · ranked by composite · "
        f"latest {conf.max_age_days} days only{held_note}._",
        "",
        "| Domain | Findings |",
        "| --- | --- |",
    ]
    order = sorted(by_domain, key=lambda d: -len(by_domain[d]))
    out += [f"| {d} | {len(by_domain[d])} |" for d in order] + [""]
    for domain in order:
        out += (
            [f"## {domain}", ""]
            + [render_index_block(e, conf) for e in rank(by_domain[domain], conf)]
            + [""]
        )
    out += [
        "---",
        "",
        "[← Home](../README.md) · [Newsletter](../NEWSLETTER.md) · [Trends](../TRENDS.md) · "
        "[Review queue](../REVIEW.md) · [Learnings](../LEARNINGS.md)",
        "",
    ]
    return "\n".join(out)


def write_topic(topic: str, conf: c.Config, now: str) -> list[dict]:
    base = c.ROOT / topic
    all_entries = c.load_pool(topic)["entries"]
    # Only VETTED findings are shown; the rest live in the REVIEW.md queue.
    curated = [e for e in all_entries if c.is_curated(e, conf)]
    by_domain: dict[str, list[dict]] = defaultdict(list)
    for e in curated:
        by_domain[e.get("domain") or "General"].append(e)
    _write_entry_pages(base, by_domain, conf)
    base.mkdir(parents=True, exist_ok=True)
    md = _topic_index_md(topic, by_domain, curated, len(all_entries) - len(curated), conf, now)
    (base / "README.md").write_text(md, encoding="utf-8")
    return curated


TOPIC_EMOJI = {"ai-security": "🤖🛡️", "product-security": "🛡️", "ai-research": "🧠"}


def _week_snapshot(curated_entries: list[dict], conf: c.Config) -> list[str]:
    """This week's snapshot: curated findings published in the last snapshot_days,
    each linking to both its writeup page and the original source article."""
    fresh = [e for e in curated_entries if c.is_fresh(e, conf.snapshot_days)]
    ranked = rank(fresh, conf)[:TOP_N_LANDING]
    out = [
        "## 📸 This week's snapshot",
        "",
        f"> The top curated findings published in the last {conf.snapshot_days} days — each links "
        "to its writeup here **and** the original source. For the full digest see the "
        "[📰 newsletter](NEWSLETTER.md).",
        "",
    ]
    if not ranked:
        return out + [
            "_No new curated findings this week. Browse the databases below or the "
            "[latest newsletter](NEWSLETTER.md)._",
            "",
        ]
    for e in ranked:
        s = entry_scores(e, conf)
        take = e.get("takeaway") or e.get("summary") or e.get("threat") or ""
        tname = c.TOPICS.get(e.get("topic", ""), {}).get("name", e.get("topic", ""))
        out.append(
            f"- **[{e.get('title','')}]({e['topic']}/{entry_relpath(e)})** · {tname} · "
            f"{fmt_published(e)} · composite **{s['composite']}** · "
            f"[source ↗]({e.get('source_url','')})  \n  {c.clean_summary(take, 180)}"
        )
    return out + [""]


def _databases_index(counts: dict[str, int]) -> list[str]:
    lines = ["## 📚 The three databases", ""]
    for t, meta in c.TOPICS.items():
        lines.append(
            f"- {TOPIC_EMOJI.get(t, '•')} **[{meta['name']}]({t}/README.md)** "
            f"— {counts[t]} vetted findings. {meta['blurb']}"
        )
    lines += [
        "",
        "Also generated every run: [📰 Newsletter](NEWSLETTER.md) (daily snapshot) · "
        "[📈 Trends](TRENDS.md) (emerging themes) · [🔍 Review queue](REVIEW.md) "
        "(not-yet-vetted) · [📓 Learnings](LEARNINGS.md) (takeaways + generated skills).",
        "",
    ]
    return lines


def _how_it_works(conf: c.Config) -> list[str]:
    return [
        "## How it works",
        "",
        "```",
        "X / GitHub / YouTube / LinkedIn / articles / RSS   (ranked source registry)",
        "  └─ ingest + Jina Reader (clean text)      → data/candidates.json",
        "     └─ analyze  (extract teachable lessons · score newness/novelty/relevance",
        "                  · derive an actionable takeaway/skill/harness idea)",
        "        └─ curate (vetted-only gate) → merge into the 3 topic pools → re-rank",
        "           └─ render  README · topic pages · newsletter · trends · review · skills",
        "```",
        "",
        f"- **Latest only.** Findings older than ~{conf.max_age_days} days age out to "
        "[`data/archive.json`](data/archive.json); the *snapshot* above is the last "
        f"{conf.snapshot_days} days.",
        "- **Vetted-only.** A finding is shown only if it isn't flagged for review and clears the "
        "composite floor; the rest wait in [REVIEW.md](REVIEW.md). Nothing is deleted.",
        "- **Ranked sources.** Approved sources live in a registry and self-rank by how often they "
        "yield *curated* findings (tier + reach + hit-rate).",
        "- **Emerging trends.** Tagged findings are clustered over time to surface waves early "
        "([TRENDS.md](TRENDS.md)).",
        "",
    ]


def _how_to_use() -> list[str]:
    return [
        "## How to use this repo",
        "",
        "| I want to… | Do this |",
        "| --- | --- |",
        "| Read the latest, curated | Skim the snapshot above → open a topic database or "
        "[the newsletter](NEWSLETTER.md) |",
        "| Track a new source | `python scripts/add_source.py <type> <handle> --topics …` "
        "(or the `/add-source` skill) — X user, blog, newsletter, GitHub user/query, YouTube |",
        "| Capture one article now | `python scripts/add.py <url>` then the `/add-resource` skill "
        "— returns summary + takeaway + action and files it |",
        "| Run a full scan | the `/research-scan` skill (self-pace with `/loop 12h /research-scan`) |",
        "| Regenerate the site | `rerank.py` → `generate_site.py` → `trends.py` → "
        "`generate_newsletter.py` → `generate_review.py` → `generate_skills.py` |",
        "",
        "**Setup** (Agent Reach + burner X account in WSL2, one-time): see "
        "[PUBLISH.md](PUBLISH.md). **Contributing / how findings are structured:** "
        "[CONTRIBUTING.md](CONTRIBUTING.md). **Automation & dev workflow:** [AGENTS.md](AGENTS.md).",
        "",
        "## Repo layout",
        "",
        "```",
        "data/{ai-security,product-security,ai-research}.json  the 3 rolling pools (source of truth)",
        "data/archive.json · data/sources.json                 aged-out findings · ranked sources",
        "scripts/                                               ingest · analyze-merge · rank · render",
        ".claude/skills/                                        /research-scan /add-resource /add-source",
        "ai-security/ product-security/ ai-research/            rendered per-topic pages (generated)",
        "README.md NEWSLETTER.md TRENDS.md REVIEW.md LEARNINGS.md   generated — do not hand-edit",
        "```",
        "",
    ]


def render_readme(curated_entries: list[dict], conf: c.Config, now: str) -> str:
    counts = {
        t: sum(1 for e in c.load_pool(t)["entries"] if c.is_curated(e, conf)) for t in c.TOPICS
    }
    total = sum(counts.values())
    out = [
        "# Awesome Security & AI Research "
        "[![Awesome](https://cdn.jsdelivr.net/gh/sindresorhus/awesome@d7305f38d29fed78fa85652e3a63e154dd8e8829/media/badge.svg)](https://github.com/sindresorhus/awesome)",
        "",
        "> An auto-updating, source-cited tracker of the most **teachable** security and AI "
        "research. It scans a ranked set of sources (X, GitHub, YouTube, blogs, newsletters, RSS), "
        "extracts the transferable lesson + a concrete action from each, curates hard, and files "
        "it into three rolling databases — **AI Security**, **Product Security**, and "
        "**AI Research** (practitioner).",
        "",
        f"![Updated](https://img.shields.io/badge/updated-{now.replace('-', '--')}-blue) "
        f"![Vetted findings](https://img.shields.io/badge/vetted-{total}-success) "
        f"![Window](https://img.shields.io/badge/window-last_{conf.max_age_days}_days-orange) "
        "![License](https://img.shields.io/badge/license-CC--BY--4.0-lightgrey)",
        "",
    ]
    out += _week_snapshot(curated_entries, conf)
    out += _databases_index(counts)
    out += _how_it_works(conf)
    out += _how_to_use()
    out += [
        "## License",
        "",
        "Curated content under [CC BY 4.0](LICENSE); scripts under MIT. Linked research remains "
        "the property of its original authors — every finding cites its original source.",
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
    (c.ROOT / "README.md").write_text(render_readme(all_entries, conf, now), encoding="utf-8")
    print(f"Rendered README.md + {'/ '.join(c.TOPICS)}/ ({len(all_entries)} vetted findings).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
