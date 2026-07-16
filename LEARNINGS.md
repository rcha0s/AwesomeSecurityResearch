# Learnings digest

> Ranked, source-cited takeaways across Security and AI. Updated 2026-07-16.

## 📈 Ranked findings

### AsyncAPI npm compromise: import-time payload defeats --ignore-scripts · `74.88`
- **Topic:** product-security / Supply Chain & Dependencies
- **Takeaway:** Import-time malware makes --ignore-scripts useless and a valid provenance attestation is not a trust signal when the pipeline itself is hijacked.
- **Action (takeaway):** Don't treat provenance/--ignore-scripts as sufficient supply-chain defenses — Add a CI check that diffs a dependency's published tarball against its tagged source before promotion, and audit any pull_request_target workflow that checks out and runs untrusted PR code with access to secrets.
- **Source:** [source](https://www.microsoft.com/en-us/security/blog/2026/07/15/unpacking-asyncapi-npm-supply-chain-compromise-import-time-payload-delivery/)

### Phantom Squatting: attackers register the domains LLMs hallucinate · `71.05`
- **Topic:** product-security / Supply Chain
- **Takeaway:** LLM hallucinations are a predictable supply-chain attack surface: attackers pre-register the domains/packages models invent.
- **Action (tool):** Enumerate & monitor your brand's hallucinated domains — Query LLMs for your brand's URLs/packages at scale, then pre-register or block-list the hallucinated ones and monitor for adversary registration.
- **Source:** [Palo Alto Networks Unit 42](https://unit42.paloaltonetworks.com/phantom-squatting-hallucinated-web-domains/)

### ToolHive MCP SSRF: host-side discovery runs outside the sandbox it enforces · `70.15`
- **Topic:** ai-security / MCP & Tools
- **Takeaway:** Put SSRF guards on every outbound client that touches untrusted input, re-validate redirect targets, and never suppress a taint warning on a 'trusted config' premise your threat model calls untrusted.
- **Action (harness):** SSRF-guard every host-side fetch in an agent/MCP runtime — For any outbound request whose URL derives from a tool/server response, enforce a private-IP dialer deny-list AND a CheckRedirect that re-applies it to each hop; treat `#nosec`/lint suppressions on such sinks as findings to review against the threat model, not settled decisions.
- **Source:** [source](https://github.com/advisories/GHSA-pr64-jmmf-jp54)

### Better Models, Worse Tools: SOTA models regress on non-native tool schemas · `70.0`
- **Topic:** ai-research / Tooling & Infrastructure
- **Takeaway:** Newer ≠ better for YOUR tools: match your harness's tool schemas to what the target model was trained on.
- **Action (harness):** Offer model-matched edit tools — In a multi-model harness, provide the edit-tool format each model was trained on (Claude str-replace, OpenAI apply_patch) instead of one custom schema, and validate/repair malformed tool calls.
- **Source:** [Simon Willison's Weblog](https://simonwillison.net/2026/Jul/4/better-models-worse-tools/#atom-everything)

### Goal-persistent agents: a frontier model built a bespoke zlib fuzzing lab in a day · `66.4`
- **Topic:** ai-research / Agents & Harnesses
- **Takeaway:** When you hand an agent a durable goal plus strict 'what counts as a real finding' rules, it will plan multi-step tooling and self-filter noise — the rules, not the model alone, are what make the output actionable.
- **Action (harness):** Pair a durable goal with explicit reportability criteria — For autonomous security/analysis agents, encode the objective so it persists across turns/compactions AND specify hard validity rules (what is reachable, in-scope, and reportable) inside the goal — this is what suppresses high-confidence noise and lets the agent self-reject weak findings.
- **Source:** [source](https://blog.trailofbits.com/2026/07/02/field-reports-from-patch-the-planet/)

### Agent skill security is a lifecycle problem, not just a runtime one (SkillSec-Eval) · `64.6`
- **Topic:** ai-security / Skill Supply Chain
- **Takeaway:** When you scan or admit agent skills, cover the whole lifecycle (admission, retrieval, planner selection, evolution) — a runtime-only check misses where most of the risk actually lives.
- **Action (tool):** Lifecycle-aware skill scanning — Extend a skill/marketplace scanner beyond runtime: check repository-admission provenance, semantic-retrieval poisoning (does a crafted description win retrieval?), planner-selection hijacking, and skill-evolution drift between approved and current versions.
- **Source:** [source](https://arxiv.org/abs/2607.13987)

### OpenClaw's ClawHub skill marketplace: an agentic supply-chain attack surface · `64.25`
- **Topic:** ai-security / Harness & Agent Security
- **Takeaway:** Agent skill marketplaces are a critical, largely-untrusted link in the software supply chain — marketplace scanning alone does not make them safe.
- **Action (harness):** Vet and sandbox agent skills — Pin and review third-party agent skills from trusted publishers, sandbox their execution with least-privilege, and don't rely on marketplace scanning — add your own allow-list + runtime policy.
- **Source:** [Palo Alto Networks Unit 42](https://unit42.paloaltonetworks.com/openclaw-ai-supply-chain-risk/)

### GigaWiper: modular destructive malware that fakes ransomware · `64.0`
- **Topic:** product-security / Malware & Wipers
- **Takeaway:** Wiper malware is consolidating into modular platforms, and 'ransomware' may be undecryptable destruction in disguise — plan recovery accordingly.
- **Action (takeaway):** Assume fake-ransomware; harden recovery — Treat ransomware incidents as potentially unrecoverable: prioritize offline/immutable backups and rapid detection of raw disk writes / partition-metadata tampering.
- **Source:** [Microsoft Security Blog](https://www.microsoft.com/en-us/security/blog/2026/07/09/gigawiper-anatomy-of-a-destructive-backdoor-assembled-from-multiple-malware/)

### Kemp LoadMaster pre-auth RCE: uninitialized heap + missing null byte (CVE-2026-8037) · `58.85`
- **Topic:** product-security / Application Security
- **Takeaway:** A minimal 'just null-terminate the buffer' patch can hide a pre-auth RCE — diff patches carefully, and treat missing null-termination next to attacker-controlled heap data as exploitable, not cosmetic.
- **Action (takeaway):** Prioritize edge-appliance patches and read the diff, not the CVE title — When a vendor ships a one-line string-handling fix on an internet-facing appliance, assume memory-corruption impact until proven otherwise and patch on the critical track; missing null-termination adjacent to attacker-sprayable heap data is an RCE primitive, not a hardening nit.
- **Source:** [source](https://labs.watchtowr.com/enterprise-tech-in-shell-out-progress-kemp-loadmaster-uninitialized-heap-to-pre-auth-rce-cve-2026-8037/)

### Omnigent: an open-source meta-harness over Claude Code, Codex, Cursor · `58.1`
- **Topic:** ai-research / Meta-Harness
- **Takeaway:** The 'meta-harness' is emerging as an abstraction layer above individual coding agents — orchestrate many, swap freely, enforce policy centrally.
- **Action (harness):** Consider a meta-harness for multi-agent work — Evaluate an orchestration layer (like Omnigent) when running multiple coding agents, so policy/sandboxing/routing live in one place instead of per-agent.
- **Source:** [omnigent-ai/omnigent](https://github.com/omnigent-ai/omnigent)


---

<sub>Generated by scripts/generate_skills.py on 2026-07-16.</sub>
