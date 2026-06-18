# Contributing

Thanks for helping keep this tracker credible and current. The bar for inclusion is deliberately high.

## What belongs here

A finding qualifies if **all** of the following are true:

1. **Credible, first-party source.** A recognized security research team, vendor research lab, standards body (e.g. OWASP), national CERT/CISA advisory, or peer-reviewed/preprint venue. No news aggregators, marketing posts, or unattributed claims.
2. **New.** Disclosed within the **last six months**. Older items age out automatically.
3. **In scope.** One of: AI Security, Web Application Security, Mobile Security.
4. **Actionable.** You can articulate the threat, the conditions under which it applies, and at least one practical mitigation.

## How to add an entry

1. Edit [`data/research.json`](data/research.json) — this is the single source of truth. The README is generated and should never be hand-edited.
2. Add an object to `entries` with these fields:

   | Field | Notes |
   | --- | --- |
   | `id` | Unique kebab-case slug. |
   | `domain` | `AI Security` \| `Web Application Security` \| `Mobile Security`. |
   | `subtype` | A sub-category within the domain (see existing values). |
   | `title` | Concise, specific finding title. |
   | `date` | `YYYY-MM` of disclosure. |
   | `severity` | `Critical` \| `High` \| `Medium` \| `Low`. |
   | `threat` | What the attack/weakness is. |
   | `conditions` | Who/what is affected and when. |
   | `mitigations` | Concrete defensive actions. |
   | `source_name` / `source_type` / `source_url` | Attribution + link. |
   | `needs_review` | `false` for curated entries. |

3. Regenerate and open a PR:

   ```bash
   pip install -r requirements.txt
   python scripts/generate_readme.py
   ```

## Adding a source feed

Propose new feeds in [`scripts/sources.yaml`](scripts/sources.yaml). Include a short justification for why the source meets the credibility bar. Single-domain feeds classify more accurately than broad ones.

## Reviewing auto-discovered items

Items added by the aggregator carry `needs_review: true` and placeholder text. To promote one: write the threat/conditions/mitigations, set a severity, set `needs_review` to `false`, then regenerate the README.
