# 50+ mobile apps ship hardcoded AWS credentials

**Track:** Security  ·  **Domain:** Mobile Security  ·  **Subtype:** Insecure Storage / Cryptography  
**Source:** [Quokka (State of Mobile App Security 2026)](https://www.quokka.io/blog/the-state-of-mobile-app-security-2026-report-findings)  ·  **Disclosed:** Feb 2026  
**Scores:** 🆕 Newness 3 · ✨ Novelty 0 · 🎯 Relevance 0 · **Composite 0.9**

## Threat · Conditions · Mitigations

- **Threat —** More than 50 apps were found with hardcoded AWS credentials in their binaries, giving attackers a direct path to production databases, customer data, and in some cases root-level cloud control.
- **Conditions —** Affects apps that embed long-lived cloud credentials for backend access instead of brokering access server-side.
- **Mitigations —** Remove all cloud credentials from clients; use short-lived tokens via an authenticated backend (Cognito/STS/OIDC); rotate exposed keys immediately; add CI checks that fail builds containing credentials.

---

_Source: [https://www.quokka.io/blog/the-state-of-mobile-app-security-2026-report-findings](https://www.quokka.io/blog/the-state-of-mobile-app-security-2026-report-findings)_  ·  [← back to index](../README.md)
