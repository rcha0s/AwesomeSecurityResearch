# MemoryTrap: persistent memory poisoning in AI coding agents (OWASP ASI06)

**Track:** Security  ·  **Domain:** AI Security  ·  **Subtype:** Memory & Context Poisoning  
**Source:** [OWASP GenAI Security Project](https://genai.owasp.org/2026/05/13/memory-is-a-feature-it-is-also-an-attack-surface/)  ·  **Disclosed:** May 2026  ·  **Retrieved:** 2026-07-13  
**Scores:** 🆕 Newness 20 · ✨ Novelty 88 · 🎯 Relevance 90 · **Composite 68.3**  
**Tags:** `memory-poisoning`, `prompt-injection`, `agent-security`, `owasp-asi`, `claude-code`

> **Takeaway —** Agent memory/persistence is a first-class attack surface: untrusted input carried forward becomes durable, trusted instruction.

## Summary

OWASP's ASI06 (Memory & Context Poisoning) is illustrated by Cisco's 'MemoryTrap' vulnerability in Claude Code: a routine workflow (clone repo → approve an npm install) let a payload reach persistent memory, global hooks config, and the system-prompt layer — turning a one-time action into prompt injection that persists across sessions, projects, and reboots.

## What to learn

- Persistent memory + hooks + system prompt are high-trust layers that untrusted content must never silently reach — _"a one-time action could shape the model's future behavior across sessions, projects, and even reboots"_
- The dangerous path looked ordinary — the agent was 'being helpful' by installing a suggested dependency — _"Claude Code was not doing something obviously dangerous. It was being helpful."_

## Actionable leverage

**[harness]** Isolate and review agent memory writes — Treat writes to persistent memory, hooks, and system-prompt layers as privileged: require explicit review, provenance tracking, and don't let tool output mutate them implicitly.

---

_Source: [https://genai.owasp.org/2026/05/13/memory-is-a-feature-it-is-also-an-attack-surface/](https://genai.owasp.org/2026/05/13/memory-is-a-feature-it-is-also-an-attack-surface/)_  ·  [← back to index](../README.md)
