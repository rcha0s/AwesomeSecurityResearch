# AGENTS.md — operating manual for firstmate & coding agents

This repo is a **firstmate**-managed project. Ongoing development runs as `ship`
(→ PR) and `scout` (→ report) tasks in **direct-PR mode**: every change lands on a
branch and a PR you review/merge on GitHub. Nothing is merged unseen.

> firstmate is macOS/Linux-only (tmux). On Windows it runs in **WSL2**; this repo
> is at `/mnt/c/Users/rohan/Desktop/AwesomeSecurityResearch`. If treehouse worktrees
> on `/mnt/c` misbehave, point treehouse `root` at a WSL-native path.

## What this project is

An auto-updating analyzer that scans X/Twitter, LinkedIn/articles, and RSS for
**AI and security** material, extracts the most *teachable* lessons, scores them by
newness / novelty / relevance, derives an actionable leverage per finding, and grows
three source-cited public knowledge directories — **`ai-security/`**, **`product-security/`**,
**`ai-research/`** — plus a rolling **`NEWSLETTER.md`** and **`TRENDS.md`**.

## Repo layout

```
config.yaml               # scoring weights, decay half-life, thresholds, freshness window
data/ai-security.json     # AI Security pool (source of truth)
data/product-security.json# Product Security pool (source of truth)
data/ai-research.json     # AI Research (practitioner) pool (source of truth)
data/archive.json         # aged-out findings (preserved, not shown)
data/sources.json         # ranked source registry (add via add_source.py)
data/candidates.json      # transient ingest staging (gitignored)
data/_raw/                # transient fetched article text (gitignored)
scripts/common.py         # shared helpers, TOPICS, schema, scoring, Jina fetch
scripts/sources_registry.py # source registry + hybrid ranking
scripts/aggregate.py · ingest_twitter.py · ingest_github.py · ingest_youtube.py · add.py  # ingest → candidates
scripts/add_source.py     # register a source (x/blog/newsletter/github/youtube)
scripts/merge_analysis.py # validate + dedup + route by topic + rerank into pools
scripts/rerank.py         # decay + composite + sort + prune stale → archive
scripts/generate_site.py  # README.md + the 3 topic trees + per-entry pages
scripts/trends.py         # data/trends.json + TRENDS.md (emerging themes)
scripts/generate_newsletter.py # NEWSLETTER.md (rolling, 3 topic sections)
scripts/generate_review.py# REVIEW.md (non-vetted queue: needs_review or below composite floor)
scripts/generate_skills.py# skills/<slug>/SKILL.md + LEARNINGS.md (vetted only)
.claude/skills/           # /research-scan /add-resource /add-source — the LLM stages
README.md · NEWSLETTER.md · TRENDS.md · REVIEW.md · LEARNINGS.md · ai-security/ product-security/ ai-research/ skills/  # GENERATED
# Curated view (topic pages + newsletter) shows only VETTED findings; the rest wait in REVIEW.md.
```

## How to run

The pools are the source of truth; the LLM analysis lives in the two skills.

```bash
# Ingest (Twitter needs Agent Reach in WSL2)
python scripts/ingest_twitter.py --max 20
python scripts/aggregate.py
python scripts/add.py "<url>"          # ad-hoc; --text/--file fallback for LinkedIn

# Analysis is done by the /research-scan or /add-resource skill, which writes
# data/analysis_out.json, then:
python scripts/merge_analysis.py
python scripts/generate_site.py
python scripts/generate_skills.py
```

## How to validate a change end-to-end

A change is only "done" when the pipeline runs clean on real data — not just units:

1. `python scripts/aggregate.py --dry-run` — feeds parse, candidates classify.
2. Round-trip a sample: stage a candidate (`add.py … --text "…"`), hand-write a
   one-entry `data/analysis_out.json`, run `merge_analysis.py` → confirm it lands in
   the correct pool, low-confidence flags `needs_review`, and re-adding is idempotent.
3. `python scripts/rerank.py && python scripts/generate_site.py && python scripts/generate_skills.py`
   — confirm the 3 topic trees regenerate, per-entry pages + `TRENDS.md`/`NEWSLETTER.md` exist,
   and the pools ↔ rendered site stay in sync (a second run is a no-op diff).

## Standard test suite (must be green before a PR)

```bash
ruff check scripts tests
black --check scripts tests
pytest --cov=scripts --cov-report=term-missing   # ≥80% on deterministic modules
```

## PR requirements

- Conventional commit messages (`feat:`, `fix:`, `chore:`, `docs:`).
- **No committed secrets** — cookies, `.env`, `data/candidates.json`, `data/_raw/`,
  `data/analysis_out.json` stay gitignored.
- Regenerate the site + skills from the pools and commit them in sync (CI enforces).
- Tests + lint green. Every published finding cites a real source URL.

## Escalation policy

Stop and ask the captain when: a source can't be verified, Twitter/Agent Reach auth
is failing (never swap in the user's main X account), scoring weights/schema need to
change, or a change would delete/relicense existing curated findings.

## Conventions

- Data pools are the single source of truth; regenerate rendered files, never edit them.
- Keep functions <40 lines, named constants in `config.yaml`, PEP 8 + type hints.
- Twitter/Agent Reach ingestion is **local/WSL2 only** — never wire it into CI.
