---
name: add-resource
description: Drop in a single article or LinkedIn/X URL (or pasted text) and immediately get its teachable summary, takeaway, and action — then merge it into the pool and re-rank. Use when the user shares one link/resource to capture.
---

# add-resource

Fast single-resource path: capture one article/post, analyze it now, show the user
the teachable summary + takeaway + action, and fold it into the growing pools with a
re-rank. Same rubric as `/research-scan`, one item.

**Input:** a URL, or pasted text, or a file — whatever the user provided.

## Steps

1. **Stage the resource:**
   ```bash
   python scripts/add.py "<url>"                     # tries Jina Reader
   # if the fetch is blocked (LinkedIn/auth-walled), the script tells you to paste:
   python scripts/add.py "<url>" --text "<pasted body>"
   python scripts/add.py --file <path> --title "<title>"
   ```
   Use `--topic ai-security|product-security|ai-research` only if the user already knows it;
   otherwise let the analysis decide. `add.py` prints the candidate `id` and its `raw_path`.

2. **Read the content** from the candidate's `raw_path` in `data/candidates.json` (or the
   pasted text). Ground everything below in this text.

3. **Analyze the single item** with the `/research-scan` rubric:
   a valid `topic` (`ai-security` | `product-security` | `ai-research` — see `common.py`
   `TOPICS`) + a free-text `domain`; a teachable `summary`; `lessons` as
   `{point, excerpt, confidence}`; a one-line `takeaway`; `tags`; and an open-ended
   `actionable` `{type, title, detail, skill_slug?}` (skill | harness | tool | takeaway |
   other). Score `novelty` (vs. the existing pools — skim `data/{ai-security,product-security,
   ai-research}.json`) and `relevance` (0-100). Write it as a one-element list to
   `data/analysis_out.json` (carry over `source_id` if present).

4. **Merge, re-rank, render:**
   ```bash
   python scripts/merge_analysis.py       # merge the one item, re-rank (can demote neighbors)
   python scripts/generate_site.py
   python scripts/trends.py
   python scripts/generate_newsletter.py
   python scripts/generate_skills.py
   ```

5. **Show the user, inline**, before finishing:
   - **Teachable summary** — the 2-3 sentence summary.
   - **Takeaway** — the one-liner.
   - **Action** — the actionable leverage (type + what to do), and if a skill was
     generated, its `skills/<slug>/SKILL.md` path.
   - Which topic it landed in (`ai-security/`, `product-security/`, or `ai-research/…`) and
     whether the re-rank moved anything.

6. **Commit (direct-PR mode)** if the user wants it persisted: branch → commit the pools +
   regenerated site (never the gitignored staging files) → PR.
