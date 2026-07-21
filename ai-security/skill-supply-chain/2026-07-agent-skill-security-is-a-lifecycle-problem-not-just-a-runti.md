# Agent skill security is a lifecycle problem, not just a runtime one (SkillSec-Eval)

**Topic:** AI Security  ·  **Domain:** Skill Supply Chain  
**Source:** [source](https://arxiv.org/abs/2607.13987)  ·  **Published:** Jul 16, 2026  ·  **Retrieved:** 2026-07-16  
**Scores:** 🆕 Newness 32 · ✨ Novelty 72 · 🎯 Relevance 80 · 🏛️ Credibility 55 · **Composite 61.85**  
**Tags:** `agent-skills`, `skill-scanning`, `supply-chain`, `threat-modeling`, `evals`  
**Verification:** ✓ independently verified · closest prior art: OpenClaw/ClawHub agentic supply-chain and MCP tool-poisoning work cover parts of this; the novel delta is the explicit lifecycle taxonomy (five stages) plus an empirical study over 327 real skills rather than a single attack demo.

> **Takeaway —** When you scan or admit agent skills, cover the whole lifecycle (admission, retrieval, planner selection, evolution) — a runtime-only check misses where most of the risk actually lives.

## TL;DR

_The gist, not every detail — read the [full source](https://arxiv.org/abs/2607.13987) for the complete write-up._

Reusable agent 'skills' are a new supply-chain unit, but security work has mostly looked at prompt injection and runtime execution. SkillSec-Eval maps threats across the whole skill lifecycle — repository admission, semantic retrieval, planner selection, execution, and skill evolution — and, over 327 real skills, shows vulnerabilities appear at stages well before execution.

## What to learn

- Skill security today is scoped too narrowly — it fixates on prompt injection and runtime, leaving the rest of the skill lifecycle unexamined. — _"existing security research primarily focuses on prompt injection and runtime execution, leaving security risks throughout the broader skill lifecycle largely unexplored"_ ✅
- A useful threat model spans five lifecycle stages, so a skill scanner should check admission, retrieval, and planner-selection risks, not only execution. — _"a threat taxonomy spanning repository admission, semantic retrieval, planner selection, execution, and skill evolution"_ ✅
- Empirically, across 327 real-world skills, vulnerabilities show up at multiple stages beyond execution — so lifecycle-aware analysis is needed, not just a runtime guard. — _"vulnerabilities arise at multiple lifecycle stages beyond execution"_ ✅

## Actionable leverage

**[tool]** Lifecycle-aware skill scanning — Extend a skill/marketplace scanner beyond runtime: check repository-admission provenance, semantic-retrieval poisoning (does a crafted description win retrieval?), planner-selection hijacking, and skill-evolution drift between approved and current versions.

---

_Source: [https://arxiv.org/abs/2607.13987](https://arxiv.org/abs/2607.13987)_  ·  [← back to index](../README.md)
