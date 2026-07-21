# 📰 Security & AI Research — Daily Snapshot (2026-07-21)

> A daily-refreshed digest of the most teachable, **vetted** security and AI research from the last 31 days, curated and source-cited. Three tracks: AI Security, Product Security, AI Research.

21 vetted findings in window · [← home](README.md) · [full trends](TRENDS.md) · [all learnings](LEARNINGS.md)

---

## AI Security

_Securing AI systems: harness & agent security, MCP, skill scanning, prompt injection, memory poisoning, model supply chain, LLM red-teaming._

**🔬 Latest research**

- **[ToolHive MCP SSRF: host-side discovery runs outside the sandbox it enforces](https://github.com/advisories/GHSA-pr64-jmmf-jp54)** · _source_ · composite 67.4
  Put SSRF guards on every outbound client that touches untrusted input, re-validate redirect targets, and never suppress a taint warning on a 'trusted config' premise your threat model calls untrusted.
  → **Do:** (harness) SSRF-guard every host-side fetch in an agent/MCP runtime
- **[OpenClaw's ClawHub skill marketplace: an agentic supply-chain attack surface](https://unit42.paloaltonetworks.com/openclaw-ai-supply-chain-risk/)** · _Palo Alto Networks Unit 42_ · composite 63.75
  Agent skill marketplaces are a critical, largely-untrusted link in the software supply chain — marketplace scanning alone does not make them safe.
  → **Do:** (harness) Vet and sandbox agent skills
- **[ShadowPickle: pickle-VM import tricks evade ten model scanners and four model hubs](https://arxiv.org/abs/2607.17503)** · _source_ · composite 62.22
  A clean model-scanner result is weak evidence - prefer non-executable formats and sandbox deserialization of any third-party model.
  → **Do:** (tool) Regression-test your model scanner with PickleBench
- **[Agent skill security is a lifecycle problem, not just a runtime one (SkillSec-Eval)](https://arxiv.org/abs/2607.13987)** · _source_ · composite 61.85
  When you scan or admit agent skills, cover the whole lifecycle (admission, retrieval, planner selection, evolution) — a runtime-only check misses where most of the risk actually lives.
  → **Do:** (tool) Lifecycle-aware skill scanning

**📈 Emerging trends**

- **agent-security** (🔺 rising) — 9 findings from 9 sources since 2026-02.
- **supply-chain** (🔺 rising) — 4 findings from 4 sources since 2026-06-23.
- **prompt-injection** (🔺 rising) — 5 findings from 5 sources since 2026-02.

[→ Full AI Security database](ai-security/README.md)

---

## Product Security

_Securing products: application security, supply chain, cloud & infra, identity, mobile, plus red teaming and threat modeling (AI-assisted or not)._

**🔬 Latest research**

- **[AsyncAPI npm compromise: import-time payload defeats --ignore-scripts](https://www.microsoft.com/en-us/security/blog/2026/07/15/unpacking-asyncapi-npm-supply-chain-compromise-import-time-payload-delivery/)** · _source_ · composite 72.12
  Import-time malware makes --ignore-scripts useless and a valid provenance attestation is not a trust signal when the pipeline itself is hijacked.
  → **Do:** (takeaway) Don't treat provenance/--ignore-scripts as sufficient supply-chain defenses
- **[Phantom Squatting: attackers register the domains LLMs hallucinate](https://unit42.paloaltonetworks.com/phantom-squatting-hallucinated-web-domains/)** · _Palo Alto Networks Unit 42_ · composite 68.3
  LLM hallucinations are a predictable supply-chain attack surface: attackers pre-register the domains/packages models invent.
  → **Do:** (tool) Enumerate & monitor your brand's hallucinated domains
- **[GigaWiper: modular destructive malware that fakes ransomware](https://www.microsoft.com/en-us/security/blog/2026/07/09/gigawiper-anatomy-of-a-destructive-backdoor-assembled-from-multiple-malware/)** · _Microsoft Security Blog_ · composite 61.25
  Wiper malware is consolidating into modular platforms, and 'ransomware' may be undecryptable destruction in disguise — plan recovery accordingly.
  → **Do:** (takeaway) Assume fake-ransomware; harden recovery
- **[Kemp LoadMaster pre-auth RCE: uninitialized heap + missing null byte (CVE-2026-8037)](https://labs.watchtowr.com/enterprise-tech-in-shell-out-progress-kemp-loadmaster-uninitialized-heap-to-pre-auth-rce-cve-2026-8037/)** · _source_ · composite 58.35
  A minimal 'just null-terminate the buffer' patch can hide a pre-auth RCE — diff patches carefully, and treat missing null-termination next to attacker-controlled heap data as exploitable, not cosmetic.
  → **Do:** (takeaway) Prioritize edge-appliance patches and read the diff, not the CVE title

**📈 Emerging trends**

- **supply-chain** (🔺 rising) — 3 findings from 3 sources since 2026-06-30.
- **memory-safety** (🔺 rising) — 2 findings from 2 sources since 2026-04.
- **android** (watching) — 2 findings from 2 sources since 2026-04.

[→ Full Product Security database](product-security/README.md)

---

## AI Research

_Practitioner AI: improving your harness, understanding, and architecture for using LLMs/agents on real tasks. Not model internals or ML-research._

**🔬 Latest research**

- **[Better Models, Worse Tools: SOTA models regress on non-native tool schemas](https://simonwillison.net/2026/Jul/4/better-models-worse-tools/#atom-everything)** · _Simon Willison's Weblog_ · composite 67.25
  Newer ≠ better for YOUR tools: match your harness's tool schemas to what the target model was trained on.
  → **Do:** (harness) Offer model-matched edit tools
- **[Goal-persistent agents: a frontier model built a bespoke zlib fuzzing lab in a day](https://blog.trailofbits.com/2026/07/02/field-reports-from-patch-the-planet/)** · _source_ · composite 63.65
  When you hand an agent a durable goal plus strict 'what counts as a real finding' rules, it will plan multi-step tooling and self-filter noise — the rules, not the model alone, are what make the output actionable.
  → **Do:** (harness) Pair a durable goal with explicit reportability criteria
- **[Omnigent: an open-source meta-harness over Claude Code, Codex, Cursor](https://github.com/omnigent-ai/omnigent)** · _omnigent-ai/omnigent_ · composite 57.6
  The 'meta-harness' is emerging as an abstraction layer above individual coding agents — orchestrate many, swap freely, enforce policy centrally.
  → **Do:** (harness) Consider a meta-harness for multi-agent work

**📈 Emerging trends**

- **agents** (🔺 rising) — 5 findings from 4 sources since 2026-05.
- **evals** (🔺 rising) — 3 findings from 3 sources since 2026-05.
- **claude-code** (🔺 rising) — 2 findings from 2 sources since 2026-06.

[→ Full AI Research database](ai-research/README.md)

---

_Every finding links its original source. Curated by the AwesomeSecurityResearch analyzer; low-confidence or unverified items are held for review and not shown here._

<sub>Generated by scripts/generate_newsletter.py on 2026-07-21.</sub>
