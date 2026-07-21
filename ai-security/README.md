# AI Security

> Securing AI systems: harness & agent security, MCP, skill scanning, prompt injection, memory poisoning, model supply chain, LLM red-teaming.

_6 vetted findings · updated 2026-07-21 · ranked by composite · latest 31 days only · [6 held for review](../REVIEW.md)._

| Domain | Findings |
| --- | --- |
| Model Supply Chain | 3 |
| MCP & Tools | 1 |
| Harness & Agent Security | 1 |
| Skill Supply Chain | 1 |

## Model Supply Chain

- **[ShadowPickle: pickle-VM import tricks evade ten model scanners and four model hubs](model-supply-chain/2026-07-shadowpickle-pickle-vm-import-tricks-evade-ten-model-scanner.md)** · composite **62.22** · Jul 20, 2026  
  A clean model-scanner result is weak evidence - prefer non-executable formats and sandbox deserialization of any third-party model.  
  _[source](https://arxiv.org/abs/2607.17503)_
- **[A malicious federated-learning aggregator can backdoor a QA model without ever seeing client data](model-supply-chain/2026-06-a-malicious-federated-learning-aggregator-can-backdoor-a-qa.md)** · composite **54.3** · Jun 25, 2026  
  In federated training the aggregator is a trust boundary, not a neutral party - protect gradients and test the global model for triggers.  
  _[source](https://arxiv.org/abs/2606.27511)_
- **[QuantGuard: a pre-quantization defense against backdoors that only wake up after you quantize](model-supply-chain/2026-06-quantguard-a-pre-quantization-defense-against-backdoors-that.md)** · composite **53.7** · Jun 28, 2026  
  Audit models at deployment precision, not the precision you were handed - some backdoors only exist after you quantize.  
  _[source](https://arxiv.org/abs/2606.29239)_

## MCP & Tools

- **[ToolHive MCP SSRF: host-side discovery runs outside the sandbox it enforces](mcp-tools/2026-07-toolhive-mcp-ssrf-host-side-discovery-runs-outside-the-sandb.md)** · composite **67.4** · Jul 15, 2026  
  Put SSRF guards on every outbound client that touches untrusted input, re-validate redirect targets, and never suppress a taint warning on a 'trusted config' premise your threat model calls untrusted.  
  _[source](https://github.com/advisories/GHSA-pr64-jmmf-jp54)_

## Harness & Agent Security

- **[OpenClaw's ClawHub skill marketplace: an agentic supply-chain attack surface](harness-agent-security/2026-06-openclaw-s-clawhub-skill-marketplace-an-agentic-supply-chain.md)** · composite **63.75** · Jun 23, 2026  
  Agent skill marketplaces are a critical, largely-untrusted link in the software supply chain — marketplace scanning alone does not make them safe.  
  _[Palo Alto Networks Unit 42](https://unit42.paloaltonetworks.com/openclaw-ai-supply-chain-risk/)_

## Skill Supply Chain

- **[Agent skill security is a lifecycle problem, not just a runtime one (SkillSec-Eval)](skill-supply-chain/2026-07-agent-skill-security-is-a-lifecycle-problem-not-just-a-runti.md)** · composite **61.85** · Jul 16, 2026  
  When you scan or admit agent skills, cover the whole lifecycle (admission, retrieval, planner selection, evolution) — a runtime-only check misses where most of the risk actually lives.  
  _[source](https://arxiv.org/abs/2607.13987)_

---

[← Home](../README.md) · [Newsletter](../NEWSLETTER.md) · [Trends](../TRENDS.md) · [Review queue](../REVIEW.md) · [Learnings](../LEARNINGS.md)
