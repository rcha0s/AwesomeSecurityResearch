# AI Security

> Securing AI systems: harness & agent security, MCP, skill scanning, prompt injection, memory poisoning, model supply chain, LLM red-teaming.

_3 vetted findings · updated 2026-07-16 · ranked by composite · latest 31 days only · [1 held for review](../REVIEW.md)._

| Domain | Findings |
| --- | --- |
| MCP & Tools | 1 |
| Skill Supply Chain | 1 |
| Harness & Agent Security | 1 |

## MCP & Tools

- **[ToolHive MCP SSRF: host-side discovery runs outside the sandbox it enforces](mcp-tools/2026-07-toolhive-mcp-ssrf-host-side-discovery-runs-outside-the-sandb.md)** · composite **70.15** · Jul 15, 2026  
  Put SSRF guards on every outbound client that touches untrusted input, re-validate redirect targets, and never suppress a taint warning on a 'trusted config' premise your threat model calls untrusted.  
  _[source](https://github.com/advisories/GHSA-pr64-jmmf-jp54)_

## Skill Supply Chain

- **[Agent skill security is a lifecycle problem, not just a runtime one (SkillSec-Eval)](skill-supply-chain/2026-07-agent-skill-security-is-a-lifecycle-problem-not-just-a-runti.md)** · composite **64.6** · Jul 16, 2026  
  When you scan or admit agent skills, cover the whole lifecycle (admission, retrieval, planner selection, evolution) — a runtime-only check misses where most of the risk actually lives.  
  _[source](https://arxiv.org/abs/2607.13987)_

## Harness & Agent Security

- **[OpenClaw's ClawHub skill marketplace: an agentic supply-chain attack surface](harness-agent-security/2026-06-openclaw-s-clawhub-skill-marketplace-an-agentic-supply-chain.md)** · composite **64.25** · Jun 23, 2026  
  Agent skill marketplaces are a critical, largely-untrusted link in the software supply chain — marketplace scanning alone does not make them safe.  
  _[Palo Alto Networks Unit 42](https://unit42.paloaltonetworks.com/openclaw-ai-supply-chain-risk/)_

---

[← Home](../README.md) · [Newsletter](../NEWSLETTER.md) · [Trends](../TRENDS.md) · [Review queue](../REVIEW.md) · [Learnings](../LEARNINGS.md)
