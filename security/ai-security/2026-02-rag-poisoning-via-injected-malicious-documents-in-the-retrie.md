# RAG poisoning via injected malicious documents in the retrieval corpus

**Track:** Security  ·  **Domain:** AI Security  ·  **Subtype:** RAG / Data Poisoning  
**Source:** [OWASP GenAI / TokenMix analysis](https://tokenmix.ai/blog/llm-security-news-2026-attacks-defenses-updates)  ·  **Disclosed:** Feb 2026  
**Scores:** 🆕 Newness 3 · ✨ Novelty 0 · 🎯 Relevance 0 · **Composite 0.9**

## Threat · Conditions · Mitigations

- **Threat —** Adversaries plant malicious documents in the retrieval corpus so the model surfaces and acts on attacker-controlled content, enabling misinformation, data exfiltration prompts, or indirect injection at query time.
- **Conditions —** Affects RAG systems that ingest from open or weakly-governed sources (wikis, ticketing, web crawls, user uploads) without content validation.
- **Mitigations —** Govern ingestion with source allow-lists and validation; sign/verify trusted documents; isolate retrieved text from instruction context; add retrieval-time anomaly detection and provenance metadata.

---

_Source: [https://tokenmix.ai/blog/llm-security-news-2026-attacks-defenses-updates](https://tokenmix.ai/blog/llm-security-news-2026-attacks-defenses-updates)_  ·  [← back to index](../README.md)
