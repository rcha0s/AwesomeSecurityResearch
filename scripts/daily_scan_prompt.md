You are running the AwesomeSecurityResearch daily scan, unattended. Candidates
have ALREADY been ingested into `data/candidates.json` by the wrapper script — do
NOT re-run the ingestors, and do NOT run any git command (the wrapper handles the
branch, commit, and PR). Your job is analysis → merge → render only.

Follow the `/research-scan` skill (`.claude/skills/research-scan/SKILL.md`) steps
2–6, with these guardrails for autonomous operation:

1. Load `data/candidates.json`. Triage HARD: the pool is large and noisy. Rank by
   source credibility × claim-level novelty and shortlist only the **6–10 most
   novel, teachable** findings across the three topics (ai-security,
   product-security, ai-research). Skip marketing posts, release notes, listicles,
   and near-duplicates of what is already in the pools.

2. For each shortlisted finding, fetch the source text (its `raw_path`, or
   `curl -s https://r.jina.ai/<article_url>`; for GHSA use
   `gh api graphql -f query='{ securityAdvisory(ghsaId:"<id>"){ summary description severity }}'`).
   Write the source text to `data/_raw/<candidate_id>.txt` and set `raw_path` so
   grounding can verify the excerpts. Every `excerpt` MUST be a verbatim substring
   of the source — never paraphrase a quote.

3. Write each entry as a **TL;DR** — the gist (what's new + why it matters + what
   to do), 2–3 sentence summary + 3 concise lessons. Do not reproduce the whole
   article. Score novelty as claim-level delta-vs-prior-art and name `prior_art`.

4. Run the independent verification pass (skill step 4): for each shortlisted
   finding spawn a fresh Task subagent given ONLY the raw source + the claims,
   prompted to REFUTE. Correct any overstatement it finds and lower novelty to
   match the source; set `verified` true/false + a short `verify_note`. If a
   verifier is blocked by a safeguard, self-verify against the source and note it.

5. Emit `data/analysis_out.json`, then run, in order:
   `python scripts/merge_analysis.py`, `python scripts/verify_citations.py`,
   `python scripts/generate_site.py`, `python scripts/trends.py`,
   `python scripts/generate_newsletter.py`, `python scripts/generate_review.py`,
   `python scripts/generate_skills.py`.

6. Finally, print a one-block RUN SUMMARY (plain text, no code fence):
   `SCAN_RESULT: merged=<n> curated=<n> review=<n> topics=<...> titles=<comma-list>`
   so the wrapper can put it in the PR body. If there were no worthwhile new
   findings, print exactly `SCAN_RESULT: merged=0` and stop — the wrapper will
   skip the PR.

Be conservative: it is better to curate 4 excellent findings than 10 mediocre
ones. Nothing you can't ground gets published — the curation gate holds the rest
in REVIEW.md automatically.
