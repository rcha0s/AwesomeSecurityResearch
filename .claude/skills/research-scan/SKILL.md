---
name: research-scan
description: Scan the X/Twitter feed + RSS for AI and security material, extract teachable lessons, score newness/novelty/relevance, derive actionable leverage, and grow the security/ and ai/ knowledge pools. Use for a full batch refresh (self-pace with /loop).
---

# research-scan

Batch pipeline that turns fresh security/AI material into scored, source-cited,
actionable pool entries. You (the model) are the analysis engine — the Python
scripts handle deterministic ingestion, merging, ranking, and rendering.

Run everything from the repo root. Twitter ingestion needs Agent Reach in WSL2.

## Steps

1. **Ingest → stage candidates** (writes `data/candidates.json`, gitignored).
   Twitter ingest MUST run inside WSL2 (that's where `twitter`/`agent-reach` live) with
   the burner env sourced and the WSL venv:
   ```bash
   wsl bash -lc 'source ~/.agent-reach/twitter.env
     cd /mnt/c/Users/rohan/Desktop/AwesomeSecurityResearch
     ~/.venvs/asr/bin/python scripts/ingest_twitter.py --max 20
     ~/.venvs/asr/bin/python scripts/aggregate.py'
   ```
   The other ingestors run fine on Windows Python (no WSL, no cookies) and should also
   run each scan for breadth:
   ```bash
   python scripts/aggregate.py       # RSS/Atom + newsletter feeds (the registry)
   python scripts/ingest_github.py   # trending/novel repos (needs `gh` authed)
   python scripts/ingest_ghsa.py     # reviewed supply-chain advisories (needs `gh` authed)
   python scripts/ingest_hn.py       # Hacker News velocity signal (keyless, network)
   python scripts/ingest_conferences.py  # accepted papers at USENIX/NDSS/SaTML/AISec/CCS
                                         # (+security-gated NeurIPS/ICML/ISSTA) via arXiv
   ```
   If Twitter ingest reports Agent Reach unhealthy, the cookies likely expired — refresh the
   burner's `auth_token`+`ct0` into `~/.agent-reach/twitter.env` — and continue with the rest.
   Note: the burner's **home feed is often low-signal** (algorithmic timeline); the
   high-signal material comes from the curated `x_account` sources in the registry.

2. **Read the candidates.** Load `data/candidates.json`. For each candidate, read its
   `raw_path` file under `data/_raw/` for the full article text. If `raw_path` is null
   but `article_url` is set, fetch clean text yourself: `curl -s https://r.jina.ai/<url>`.

3. **Analyze each candidate** grounded in the source text (never invent facts):
   - **topic** — exactly one of three (see `scripts/common.py` `TOPICS`):
     - `ai-security` — securing AI systems: harness/agent security, MCP, skill scanning,
       prompt injection, memory poisoning, model supply chain, LLM red-teaming.
     - `product-security` — securing products: appsec, supply chain, cloud/infra, identity,
       mobile, **red teaming and threat modeling** (AI-assisted or not).
     - `ai-research` — **practitioner** AI: improving your harness, understanding, or
       architecture for using LLMs/agents on real tasks. NOT model internals / ML-research.
   - **domain** — a short sub-grouping label within the topic (free text; see the topic's
     suggested `domains` in `common.py`, but you may coin a precise one).
   - **summary** — 2-3 sentence teachable summary.
   - **lessons** — the concrete, transferable takeaways. Each: `{point, excerpt,
     confidence}` where `excerpt` is a short quote/anchor from the source and
     `confidence` ∈ [0,1] reflects how well the source supports the point. Be honest —
     low confidence auto-flags the entry for review instead of publishing it as fact.
   - **takeaway** — one-line "so what."
   - **tags** — cross-cutting topics (e.g. `prompt-injection`, `mcp`, `rag`, `evals`).
   - **actionable** — `{type, title, detail, skill_slug?}`. `type` ∈ takeaway | skill |
     harness | tool | other. Choose whatever genuinely fits: a reusable **skill** (set a
     kebab `skill_slug`), a **harness** improvement, a **tool** idea, or just a
     **takeaway**. `detail` should be concrete enough to act on.
   - **scores** — `{novelty, relevance}` each 0-100 (newness + credibility are computed):
     - **novelty is a claim-level "delta vs prior art", NOT text similarity.** First state the
       finding's core *claim* (the specific technique/mechanism/result/implementation). Then
       skim the existing entries in `data/{ai-security,product-security,ai-research}.json` +
       recent `data/archive.json` for the nearest ones, and judge how much is genuinely new
       versus known prior work. Can't name an equivalent → high; a variation of something known
       → mid; a restatement/duplicate → low. Put the closest prior work in a `prior_art` field.
     - **relevance**: usefulness to the topic's audience (AI Security = a defender; Product
       Security = an appsec/red-team engineer; AI Research = a harness/agent builder).
   - Security findings may also include `threat`/`conditions`/`mitigations`.

4. **Independent verification (adversarial second pass).** For each shortlisted finding, spawn a
   FRESH subagent (the Task tool) given ONLY the raw source text + the extracted claims — do NOT
   give it your scores. Prompt it to **refute**: (a) is every lesson actually supported by the
   source? (b) independently re-judge novelty as claim-level delta-vs-prior-art (name the closest
   prior work). (c) re-judge relevance. Then reconcile:
   - if the verifier refutes a claim, or its novelty is much lower than yours (disagreement),
     set `verified: false` and a short `verify_note` — the merge gate sends it to REVIEW.md;
   - otherwise set `verified: true`, take the **lower** of the two novelty scores, and record
     `prior_art`. This makes the score an independent judgment, not a self-grade.

5. **Emit** `data/analysis_out.json` — a JSON list of analyzed entries (each: at minimum
   `topic, domain, title, source_url`, plus the fields above incl. `verified`, `prior_art`;
   carry over `article_url, tweet_url, author, date, published, raw_path, discovered_via,
   source_id, source_rank, source_topics` from the candidate). `source_id` lets
   `merge_analysis.py` credit the source's hit-rate; `raw_path` lets it ground the excerpts.

6. **Merge + rerank + render:**
   ```bash
   python scripts/merge_analysis.py       # validate, dedup, route by topic, GROUND excerpts, flag, rerank
   python scripts/verify_citations.py     # re-verify every lesson excerpt vs its source (persist grounding)
   python scripts/generate_site.py        # README.md + ai-security/ product-security/ ai-research/
   python scripts/trends.py               # data/trends.json + TRENDS.md (emerging themes)
   python scripts/generate_newsletter.py  # NEWSLETTER.md (rolling, 3 topic sections)
   python scripts/generate_review.py      # REVIEW.md (non-vetted queue)
   python scripts/generate_skills.py      # skills/<slug>/SKILL.md + LEARNINGS.md
   ```
   Only **vetted** findings (not `needs_review`, composite ≥ `curation.min_composite`) appear on
   the topic pages/newsletter; borderline ones land in `REVIEW.md` for a human to promote.

7. **Commit (direct-PR mode).** Create a branch, commit the regenerated pools + site
   (never commit `data/candidates.json`, `data/_raw/`, `data/analysis_out.json`, or
   cookies), and open a PR. Then print a **run summary**: candidates ingested, entries
   merged per topic, how many flagged needs_review, and the top movers by composite.

## Backfill mode

If asked to backfill, treat the existing pool entries that lack `lessons`/`scores` as
candidates: read their `source_url`, analyze with the same rubric, and re-emit them
through `analysis_out.json` (merge updates them in place by URL).
