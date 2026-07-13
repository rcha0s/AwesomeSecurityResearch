# New OWASP category: Software Supply Chain Failures (A03)

**Track:** Security  ·  **Domain:** Web Application Security  ·  **Subtype:** Supply Chain  
**Source:** [OWASP Foundation](https://owasp.org/www-project-top-ten/)  ·  **Disclosed:** Nov 2025  
**Scores:** 🆕 Newness 0 · ✨ Novelty 0 · 🎯 Relevance 0 · **Composite 0.0**

## Threat · Conditions · Mitigations

- **Threat —** OWASP added a dedicated Software Supply Chain Failures category, recognizing dependency, build-pipeline, and artifact-integrity risks as a top web-app risk class distinct from generic vulnerable components.
- **Conditions —** Affects any application consuming third-party packages, build actions, or container bases without integrity verification.
- **Mitigations —** Maintain an SBOM; pin and verify dependencies by hash; use signed artifacts and provenance (SLSA); restrict CI permissions; continuously scan and monitor for compromised packages.

---

_Source: [https://owasp.org/www-project-top-ten/](https://owasp.org/www-project-top-ten/)_  ·  [← back to index](../README.md)
