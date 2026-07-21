# OpenClaw's ClawHub skill marketplace: an agentic supply-chain attack surface

**Topic:** AI Security  ·  **Domain:** Harness & Agent Security  
**Source:** [Palo Alto Networks Unit 42](https://unit42.paloaltonetworks.com/openclaw-ai-supply-chain-risk/)  ·  **Published:** Jun 23, 2026  ·  **Retrieved:** 2026-07-13  
**Scores:** 🆕 Newness 6 · ✨ Novelty 82 · 🎯 Relevance 88 · 🏛️ Credibility 75 · **Composite 63.75**  
**Tags:** `agent-security`, `skill-scanning`, `supply-chain`, `agentic-threats`, `unit42`

> **Takeaway —** Agent skill marketplaces are a critical, largely-untrusted link in the software supply chain — marketplace scanning alone does not make them safe.

## TL;DR

_The gist, not every detail — read the [full source](https://unit42.paloaltonetworks.com/openclaw-ai-supply-chain-risk/) for the complete write-up._

Unit 42 found five evasive malicious 'skills' persisting on ClawHub — the marketplace OpenClaw's agent pulls third-party, markdown-driven packages from with broad local system access — despite VirusTotal + ClawScan screening added after February's incidents. The five span infostealers (macOS, C2), scanner evasion (inflated file size to exceed thresholds), and two NOVEL agentic threats: runtime agentic affiliate injection and agentic front-running.

## What to learn

- Agent skills are broad-access packages; the marketplace is a supply-chain link to treat as untrusted — _"markdown-driven packages with broad local system access, making ClawHub a critical link in the agentic software supply chain"_ ✅
- Malware evades marketplace scanners with simple tricks (oversized files exceed scan thresholds) — _"inflated file size to exceed scanner thresholds, bypassing both ClawScan and VirusTotal detection"_ ✅
- New 'agentic' threat classes are emerging — affiliate injection and front-running done at agent runtime — _"runtime agentic affiliate injection and agentic front-running. Both are novel techniques"_ ✅

## Actionable leverage

**[harness]** Vet and sandbox agent skills — Pin and review third-party agent skills from trusted publishers, sandbox their execution with least-privilege, and don't rely on marketplace scanning — add your own allow-list + runtime policy.

---

_Source: [https://unit42.paloaltonetworks.com/openclaw-ai-supply-chain-risk/](https://unit42.paloaltonetworks.com/openclaw-ai-supply-chain-risk/)_  ·  [← back to index](../README.md)
