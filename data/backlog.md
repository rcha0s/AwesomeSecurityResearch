# Backlog

Follow-on evolution for the research analyzer. Dispatch these as firstmate
`ship`/`scout` tasks (direct-PR mode). See [AGENTS.md](../AGENTS.md).

## Todo

- [ ] **Backfill legacy entries** — analyze the original 20 security findings so they
  gain `lessons`, `scores`, and `actionable` (run `/research-scan` backfill mode).
- [ ] **Embedding-based novelty** — replace the pool-relative heuristic novelty with a
  local embedding similarity check against existing entries.
- [ ] **GitHub Pages** — publish `security/` and `ai/` as a browsable site.
- [ ] **More sources** — expand `sources.yaml` X accounts + AI-research RSS (labs,
  practitioner blogs); add Reddit via Agent Reach.
- [ ] **LinkedIn-MCP hardening** — make `add.py` use the Agent Reach `linkedin` channel
  directly, with the paste fallback as a last resort.
- [ ] **Weekly digest issue** — open a GitHub issue summarizing the week's top learnings.
- [ ] **Dedup upgrade** — canonicalize tweet→article links (unwrap t.co / trackers)
  before URL de-duplication.

## Done

_(kept short; older items archived to data/done-archive.md)_
