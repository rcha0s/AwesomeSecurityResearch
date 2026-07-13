# WAFFLED: parsing discrepancies bypass web application firewalls

**Track:** Security  ·  **Domain:** Web Application Security  ·  **Subtype:** WAF Bypass  
**Source:** [arXiv (WAFFLED)](https://arxiv.org/pdf/2503.10846)  ·  **Disclosed:** Dec 2025  
**Scores:** 🆕 Newness 1 · ✨ Novelty 0 · 🎯 Relevance 0 · **Composite 0.3**

## Threat · Conditions · Mitigations

- **Threat —** Academic work shows attackers exploit differences in how WAFs and back-ends parse requests (encodings, multipart, content types) to slip malicious payloads past the WAF that the application still processes.
- **Conditions —** Affects apps relying on a WAF as a primary control where WAF and origin parse input differently.
- **Mitigations —** Do not treat the WAF as the sole defense; fix root-cause input handling; align parsing between WAF and app; canonicalize input; keep WAF rule/engine updated and test bypass classes.

---

_Source: [https://arxiv.org/pdf/2503.10846](https://arxiv.org/pdf/2503.10846)_  ·  [← back to index](../README.md)
