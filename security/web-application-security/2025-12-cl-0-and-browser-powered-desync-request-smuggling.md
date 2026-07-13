# CL.0 and browser-powered desync request smuggling

**Track:** Security  ·  **Domain:** Web Application Security  ·  **Subtype:** Request Smuggling / Desync  
**Source:** [PortSwigger Research](https://portswigger.net/research/browser-powered-desync-attacks)  ·  **Disclosed:** Dec 2025  
**Scores:** 🆕 Newness 1 · ✨ Novelty 0 · 🎯 Relevance 0 · **Composite 0.3**

## Threat · Conditions · Mitigations

- **Threat —** PortSwigger research on browser-powered desync and CL.0 shows back-end servers can be made to ignore Content-Length, enabling request smuggling without chunked encoding or HTTP/2 downgrade, leading to request hijacking and cache poisoning.
- **Conditions —** Affects multi-tier deployments where front-end and back-end disagree on request boundaries (reverse proxies, CDNs, load balancers).
- **Mitigations —** Normalize request parsing across tiers; prefer HTTP/2 end-to-end and reject ambiguous Content-Length; deploy current proxy/server versions; test with smuggling tooling; the longer-term fix is retiring HTTP/1.1 back-ends.

---

_Source: [https://portswigger.net/research/browser-powered-desync-attacks](https://portswigger.net/research/browser-powered-desync-attacks)_  ·  [← back to index](../README.md)
