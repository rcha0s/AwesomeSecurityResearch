# Prismor: a runtime firewall that blocks rogue AI-agent tool calls

**Track:** Security  ·  **Domain:** AI Security  ·  **Subtype:** Agentic AI / MCP  
**Source:** [PrismorSec/prismor](https://github.com/PrismorSec/prismor)  ·  **Author:** PrismorSec  ·  **Disclosed:** Feb 2026  ·  **Retrieved:** 2026-07-13  
**Scores:** 🆕 Newness 3 · ✨ Novelty 74 · 🎯 Relevance 85 · **Composite 56.55**  
**Tags:** `agent-security`, `mcp`, `runtime-enforcement`, `tool-use`, `tooling-2026`

> **Takeaway —** The strongest control point for agent safety is the tool-call boundary — enforce policy at call time, not just in the prompt.

## Summary

Prismor is a runtime firewall for AI agents: it intercepts an agent's tool calls before they execute and blocks dangerous commands, secret leakage, and rogue actions. It represents a shift from static agent auditing to runtime enforcement at the tool-call boundary.

## What to learn

- Put a policy-enforcing firewall between the agent and its tools so a compromised prompt can't reach a destructive action — _"catches the rogue tool call before it runs"_
- Runtime enforcement complements static scanning — assume the model will be tricked and contain the blast radius — _"Runtime Firewall for AI agents"_

## Actionable leverage

**[harness]** Add a tool-call firewall to your agent harness — Interpose an allow/deny policy layer on every tool call (esp. shell, network, secret access) with human-in-the-loop for high-impact actions.

---

_Source: [https://github.com/PrismorSec/prismor](https://github.com/PrismorSec/prismor)_  ·  [← back to index](../README.md)
