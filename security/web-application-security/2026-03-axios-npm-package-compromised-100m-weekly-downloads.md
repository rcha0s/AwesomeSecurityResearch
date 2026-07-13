# Axios npm package compromised (100M+ weekly downloads)

**Track:** Security  ·  **Domain:** Web Application Security  ·  **Subtype:** Supply Chain  
**Source:** [Microsoft Security / CISA](https://www.cisa.gov/news-events/alerts/2026/04/20/supply-chain-compromise-impacts-axios-node-package-manager)  ·  **Disclosed:** Mar 2026  
**Scores:** 🆕 Newness 5 · ✨ Novelty 0 · 🎯 Relevance 0 · **Composite 1.5**

## Threat · Conditions · Mitigations

- **Threat —** Malicious Axios versions (1.14.1, 0.30.4) were published with an injected dependency that pulled payloads from attacker C2. Microsoft attributed it to the North Korean actor Sapphire Sleet. CISA issued an alert.
- **Conditions —** Affects projects that installed or auto-updated to the malicious versions of this widely used HTTP client.
- **Mitigations —** Pin to known-good Axios versions and rebuild; audit lockfiles; rotate any exposed secrets; enable install-time scanning and provenance checks; subscribe to ecosystem advisories.

---

_Source: [https://www.cisa.gov/news-events/alerts/2026/04/20/supply-chain-compromise-impacts-axios-node-package-manager](https://www.cisa.gov/news-events/alerts/2026/04/20/supply-chain-compromise-impacts-axios-node-package-manager)_  ·  [← back to index](../README.md)
