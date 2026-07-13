# OWASP Top 10:2025 — Broken Access Control (#1) now subsumes SSRF

**Track:** Security  ·  **Domain:** Web Application Security  ·  **Subtype:** Access Control  
**Source:** [OWASP Foundation](https://owasp.org/www-project-top-ten/)  ·  **Disclosed:** Nov 2025  
**Scores:** 🆕 Newness 0 · ✨ Novelty 0 · 🎯 Relevance 0 · **Composite 0.0**

## Threat · Conditions · Mitigations

- **Threat —** The 2025 Top 10 (based on 175k+ vulnerabilities) keeps Broken Access Control at #1 and folds in Server-Side Request Forgery, reflecting how missing authorization and SSRF let attackers reach internal services and data.
- **Conditions —** Affects apps with object-level/function-level authorization gaps or server-side fetchers that accept user-controlled URLs.
- **Mitigations —** Enforce server-side authorization on every request; deny-by-default; validate and allow-list outbound URLs; block link-local/metadata endpoints; add automated access-control tests.

---

_Source: [https://owasp.org/www-project-top-ten/](https://owasp.org/www-project-top-ten/)_  ·  [← back to index](../README.md)
