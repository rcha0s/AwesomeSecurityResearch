# First large-scale indirect prompt injection attacks observed in the wild

**Track:** Security  ·  **Domain:** AI Security  ·  **Subtype:** Prompt Injection  
**Source:** [Palo Alto Networks Unit 42](https://unit42.paloaltonetworks.com/monitoring-npm-supply-chain-attacks/)  ·  **Disclosed:** Mar 2026  
**Scores:** 🆕 Newness 5 · ✨ Novelty 0 · 🎯 Relevance 0 · **Composite 1.5**

## Threat · Conditions · Mitigations

- **Threat —** Adversaries embed hidden instructions inside content an LLM later retrieves (web pages, documents, ad copy) rather than in the user's direct prompt. Unit 42 documented the first large-scale, real-world cases, including ad-review evasion and system-prompt leakage on live commercial platforms.
- **Conditions —** Affects LLM apps and agents that ingest untrusted external data (RAG, browsing, email/doc summarization, tool output) and act on it without isolating instructions from data.
- **Mitigations —** Treat all retrieved content as untrusted data, not instructions; enforce strict input/output boundaries and content provenance; constrain tool/agent permissions with allow-lists; add injection detection and human-in-the-loop for high-impact actions.

---

_Source: [https://unit42.paloaltonetworks.com/monitoring-npm-supply-chain-attacks/](https://unit42.paloaltonetworks.com/monitoring-npm-supply-chain-attacks/)_  ·  [← back to index](../README.md)
