# AI agent skill registry poisoned at scale (ClawHub)

**Track:** Security  ·  **Domain:** AI Security  ·  **Subtype:** Agentic AI / Supply Chain  
**Source:** [OWASP GenAI Security Project](https://genai.owasp.org/2026/04/14/owasp-genai-exploit-round-up-report-q1-2026/)  ·  **Disclosed:** Mar 2026  
**Scores:** 🆕 Newness 5 · ✨ Novelty 0 · 🎯 Relevance 0 · **Composite 1.5**

## Threat · Conditions · Mitigations

- **Threat —** An AI agent skill marketplace became the first registry systematically poisoned at scale, with several of the most-downloaded skills confirmed as malware, enabling credential theft and code execution inside agent environments.
- **Conditions —** Affects teams that install community agent skills/plugins automatically without provenance checks or sandboxing.
- **Mitigations —** Vet and pin skills by publisher and hash; isolate skill execution; scan skills for malicious behavior; prefer signed/verified sources; monitor for post-install network and credential access.

---

_Source: [https://genai.owasp.org/2026/04/14/owasp-genai-exploit-round-up-report-q1-2026/](https://genai.owasp.org/2026/04/14/owasp-genai-exploit-round-up-report-q1-2026/)_  ·  [← back to index](../README.md)
