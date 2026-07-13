# Contributing

Thanks for helping keep this pool credible, current, and teachable. The bar for
inclusion is deliberately high, and every finding must cite a real source.

## Two tracks

Findings live in one of two growing pools (the source of truth):

- **Security** (`data/security.json`) — domains: `AI Security`, `Web Application
  Security`, `Mobile Security`. Threats and defenses.
- **AI** (`data/ai.json`) — domains: `Agents & Harnesses`, `Prompting & Context`,
  `Models & Capabilities`, `Tooling & Infrastructure`, `Evaluation & Safety`.
  Capabilities, how-tos, and harness learnings.

The rendered `README.md`, `security/`, `ai/`, `skills/`, and `LEARNINGS.md` are
**generated** — never hand-edit them. Edit the pools and regenerate.

## What belongs here

1. **Credible, first-party source** — a recognized research team, vendor lab,
   standards body, CERT advisory, peer-reviewed/preprint venue, or a substantive
   practitioner post. No marketing or unattributed claims.
2. **New (hard rule)** — the source must have been published within the freshness window (`max_age_days` in `config.yaml`, ~1 month). We track only the latest research; older entries age out to `data/archive.json` automatically and are no longer shown.
3. **In scope** — one of the two tracks above.
4. **Teachable & actionable** — you can state the lessons and a concrete action.

## The easy way: let the skills do it

- One resource: `python scripts/add.py "<url>"` then run the **`/add-resource`** skill.
  (LinkedIn/auth-walled? paste it: `add.py "<url>" --text "<body>"`.)
- A batch from your X feed + RSS: run the **`/research-scan`** skill.

Both extract lessons, score novelty/relevance, derive an actionable leverage, merge
into the right pool, re-rank, and regenerate the site.

## The manual way: add an entry directly

Add an object to `entries` in the right pool file (schema v2). Key fields:

| Field | Notes |
| --- | --- |
| `track` | `security` \| `ai`. |
| `domain` / `subtype` | Valid domain for the track (see `scripts/common.py`). |
| `title` | Concise, specific. |
| `date` | `YYYY-MM` of disclosure. |
| `summary` | Teachable 2-3 sentences. |
| `lessons` | List of `{point, excerpt, confidence}` (excerpt anchors to the source). |
| `takeaway` | One-line "so what". |
| `actionable` | `{type, title, detail, skill_slug?}`, type ∈ takeaway/skill/harness/tool/other. |
| `tags` | Cross-cutting topics. |
| `scores` | `{novelty, relevance}` 0-100 (newness + composite are computed). |
| `source_name` / `source_type` / `source_url` | Attribution + link. |
| `needs_review` | `false` for verified entries. |

Security entries may also carry `threat` / `conditions` / `mitigations`. Then:

```bash
pip install -r requirements.txt
python scripts/rerank.py
python scripts/generate_site.py
python scripts/generate_skills.py
```

Open a PR (direct-PR mode — see [AGENTS.md](AGENTS.md)). Keep lint + tests green.

## Adding a source feed / account

Propose feeds in [`scripts/sources.yaml`](scripts/sources.yaml) with a short
credibility justification. X accounts go under `twitter.accounts` (use a **burner**
account — never your main). Single-domain feeds classify more accurately.
