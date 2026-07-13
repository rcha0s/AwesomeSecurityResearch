# Shipped apps carry years-old Critical CVEs in bundled components

**Track:** Security  ·  **Domain:** Mobile Security  ·  **Subtype:** Legacy CVE Exposure  
**Source:** [Quokka (State of Mobile App Security 2026)](https://www.quokka.io/blog/the-state-of-mobile-app-security-2026-report-findings)  ·  **Disclosed:** Feb 2026  
**Scores:** 🆕 Newness 3 · ✨ Novelty 0 · 🎯 Relevance 0 · **Composite 0.9**

## Threat · Conditions · Mitigations

- **Threat —** Quokka found Android apps shipping Critical CVEs spanning nearly a decade of unpatched components, and 2,075 iOS apps containing a Critical CVE first disclosed in 2023 — outdated bundled SDKs/libraries remain a major exposure.
- **Conditions —** Affects apps bundling outdated third-party SDKs/native libraries without dependency patching.
- **Mitigations —** Maintain a mobile SBOM; continuously scan bundled SDKs for known CVEs; patch/upgrade dependencies on a schedule; gate releases on component vulnerability checks.

---

_Source: [https://www.quokka.io/blog/the-state-of-mobile-app-security-2026-report-findings](https://www.quokka.io/blog/the-state-of-mobile-app-security-2026-report-findings)_  ·  [← back to index](../README.md)
