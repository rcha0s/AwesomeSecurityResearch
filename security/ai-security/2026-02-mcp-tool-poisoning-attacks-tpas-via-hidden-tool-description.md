# MCP tool poisoning attacks (TPAs) via hidden tool-description metadata

**Track:** Security  ·  **Domain:** AI Security  ·  **Subtype:** Agentic AI / MCP  
**Source:** [Checkmarx Zero](https://checkmarx.com/zero-post/11-emerging-ai-security-risks-with-mcp-model-context-protocol/)  ·  **Disclosed:** Feb 2026  
**Scores:** 🆕 Newness 3 · ✨ Novelty 0 · 🎯 Relevance 0 · **Composite 0.9**

## Threat · Conditions · Mitigations

- **Threat —** Malicious instructions hidden in Model Context Protocol tool descriptions (metadata read by the model but not shown to users) coerce agents into leaking data or invoking dangerous tools. Studies found a large share of MCP servers also contain command injection, path traversal, and SSRF flaws.
- **Conditions —** Affects AI agents that auto-load third-party MCP servers/tools and trust tool descriptions as benign; worsened by excessive autonomy and broad credential scope.
- **Mitigations —** Pin and review MCP servers from trusted publishers only; render and audit full tool descriptions; sandbox tool execution; apply least-privilege credentials and per-tool allow-lists; monitor for anomalous tool calls.

---

_Source: [https://checkmarx.com/zero-post/11-emerging-ai-security-risks-with-mcp-model-context-protocol/](https://checkmarx.com/zero-post/11-emerging-ai-security-risks-with-mcp-model-context-protocol/)_  ·  [← back to index](../README.md)
