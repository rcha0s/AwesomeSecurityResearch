# Awesome Security & AI Research [![Awesome](https://cdn.jsdelivr.net/gh/sindresorhus/awesome@d7305f38d29fed78fa85652e3a63e154dd8e8829/media/badge.svg)](https://github.com/sindresorhus/awesome)

> An auto-updating, source-cited tracker of the most **teachable** security and AI research. It scans a ranked set of sources (X, GitHub, YouTube, blogs, newsletters, RSS), extracts the transferable lesson + a concrete action from each, curates hard, and files it into three rolling databases — **AI Security**, **Product Security**, and **AI Research** (practitioner).

![Updated](https://img.shields.io/badge/updated-2026--07--16-blue) ![Vetted findings](https://img.shields.io/badge/vetted-10-success) ![Window](https://img.shields.io/badge/window-last_31_days-orange) ![License](https://img.shields.io/badge/license-CC--BY--4.0-lightgrey)

## 📸 This week's snapshot

> The top curated findings published in the last 7 days. Every entry is a **TL;DR** — we track the gist (what's new + why it matters + what to do), and each links to its writeup here **and** the original source for the full detail. For the full digest see the [📰 newsletter](NEWSLETTER.md).

- **[AsyncAPI npm compromise: import-time payload defeats --ignore-scripts](product-security/supply-chain-dependencies/2026-07-asyncapi-npm-compromise-import-time-payload-defeats-ignore-s.md)** · Product Security · Jul 16, 2026 · composite **74.88** · [source ↗](https://www.microsoft.com/en-us/security/blog/2026/07/15/unpacking-asyncapi-npm-supply-chain-compromise-import-time-payload-delivery/)  
  Import-time malware makes --ignore-scripts useless and a valid provenance attestation is not a trust signal when the pipeline itself is hijacked.
- **[ToolHive MCP SSRF: host-side discovery runs outside the sandbox it enforces](ai-security/mcp-tools/2026-07-toolhive-mcp-ssrf-host-side-discovery-runs-outside-the-sandb.md)** · AI Security · Jul 15, 2026 · composite **70.15** · [source ↗](https://github.com/advisories/GHSA-pr64-jmmf-jp54)  
  Put SSRF guards on every outbound client that touches untrusted input, re-validate redirect targets, and never suppress a taint warning on a 'trusted config' premise your threat…
- **[Agent skill security is a lifecycle problem, not just a runtime one (SkillSec-Eval)](ai-security/skill-supply-chain/2026-07-agent-skill-security-is-a-lifecycle-problem-not-just-a-runti.md)** · AI Security · Jul 16, 2026 · composite **64.6** · [source ↗](https://arxiv.org/abs/2607.13987)  
  When you scan or admit agent skills, cover the whole lifecycle (admission, retrieval, planner selection, evolution) — a runtime-only check misses where most of the risk actually…
- **[GigaWiper: modular destructive malware that fakes ransomware](product-security/malware-wipers/2026-07-gigawiper-modular-destructive-malware-that-fakes-ransomware.md)** · Product Security · Jul 9, 2026 · composite **64.0** · [source ↗](https://www.microsoft.com/en-us/security/blog/2026/07/09/gigawiper-anatomy-of-a-destructive-backdoor-assembled-from-multiple-malware/)  
  Wiper malware is consolidating into modular platforms, and 'ransomware' may be undecryptable destruction in disguise — plan recovery accordingly.

## 📚 The three databases

- 🤖🛡️ **[AI Security](ai-security/README.md)** — 3 vetted findings. Securing AI systems: harness & agent security, MCP, skill scanning, prompt injection, memory poisoning, model supply chain, LLM red-teaming.
- 🛡️ **[Product Security](product-security/README.md)** — 4 vetted findings. Securing products: application security, supply chain, cloud & infra, identity, mobile, plus red teaming and threat modeling (AI-assisted or not).
- 🧠 **[AI Research](ai-research/README.md)** — 3 vetted findings. Practitioner AI: improving your harness, understanding, and architecture for using LLMs/agents on real tasks. Not model internals or ML-research.

Also generated every run: [📰 Newsletter](NEWSLETTER.md) (daily snapshot) · [📈 Trends](TRENDS.md) (emerging themes) · [🔍 Review queue](REVIEW.md) (not-yet-vetted) · [📓 Learnings](LEARNINGS.md) (takeaways + generated skills).

## How it works

```
X / GitHub / YouTube / LinkedIn / articles / RSS   (ranked source registry)
  └─ ingest + Jina Reader (clean text)      → data/candidates.json
     └─ analyze  (extract teachable lessons · score newness/novelty/relevance
                  · derive an actionable takeaway/skill/harness idea)
        └─ curate (vetted-only gate) → merge into the 3 topic pools → re-rank
           └─ render  README · topic pages · newsletter · trends · review · skills
```

- **Latest only.** Findings older than ~31 days age out to [`data/archive.json`](data/archive.json); the *snapshot* above is the last 7 days.
- **Vetted-only.** A finding is shown only if it isn't flagged for review and clears the composite floor; the rest wait in [REVIEW.md](REVIEW.md). Nothing is deleted.
- **Ranked sources.** Approved sources live in a registry and self-rank by how often they yield *curated* findings (tier + reach + hit-rate).
- **Emerging trends.** Tagged findings are clustered over time to surface waves early ([TRENDS.md](TRENDS.md)).

## How to use this repo

| I want to… | Do this |
| --- | --- |
| Read the latest, curated | Skim the snapshot above → open a topic database or [the newsletter](NEWSLETTER.md) |
| Track a new source | `python scripts/add_source.py <type> <handle> --topics …` (or the `/add-source` skill) — X user, blog, newsletter, GitHub user/query, YouTube |
| Capture one article now | `python scripts/add.py <url>` then the `/add-resource` skill — returns summary + takeaway + action and files it |
| Run a full scan | the `/research-scan` skill (self-pace with `/loop 12h /research-scan`) |
| Regenerate the site | `rerank.py` → `generate_site.py` → `trends.py` → `generate_newsletter.py` → `generate_review.py` → `generate_skills.py` |

**Setup** (Agent Reach + burner X account in WSL2, one-time): see [PUBLISH.md](PUBLISH.md). **Contributing / how findings are structured:** [CONTRIBUTING.md](CONTRIBUTING.md). **Automation & dev workflow:** [AGENTS.md](AGENTS.md).

## Repo layout

```
data/{ai-security,product-security,ai-research}.json  the 3 rolling pools (source of truth)
data/archive.json · data/sources.json                 aged-out findings · ranked sources
scripts/                                               ingest · analyze-merge · rank · render
.claude/skills/                                        /research-scan /add-resource /add-source
ai-security/ product-security/ ai-research/            rendered per-topic pages (generated)
README.md NEWSLETTER.md TRENDS.md REVIEW.md LEARNINGS.md   generated — do not hand-edit
```

## License

Curated content under [CC BY 4.0](LICENSE); scripts under MIT. Linked research remains the property of its original authors — every finding cites its original source.

<sub>Generated by <code>scripts/generate_site.py</code> on 2026-07-16. Edit the pools in <code>data/</code> and regenerate — do not hand-edit rendered files.</sub>
