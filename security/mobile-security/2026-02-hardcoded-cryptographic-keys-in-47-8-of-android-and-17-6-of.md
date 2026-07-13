# Hardcoded cryptographic keys in 47.8% of Android and 17.6% of iOS apps

**Track:** Security  ·  **Domain:** Mobile Security  ·  **Subtype:** Insecure Storage / Cryptography  
**Source:** [Quokka (State of Mobile App Security 2026)](https://www.quokka.io/blog/the-state-of-mobile-app-security-2026-report-findings)  ·  **Disclosed:** Feb 2026  
**Scores:** 🆕 Newness 3 · ✨ Novelty 0 · 🎯 Relevance 0 · **Composite 0.9**

## Threat · Conditions · Mitigations

- **Threat —** Quokka's analysis of 150k+ apps found cryptographic keys embedded directly in app binaries. Because every install ships the same key, extraction via trivial decompilation compromises all users' protected data retroactively.
- **Conditions —** Affects apps that embed symmetric keys or secrets in the binary for on-device encryption or API access.
- **Mitigations —** Move on-device keys to Android Keystore / iOS Secure Enclave; fetch secrets at runtime from an authenticated vault (HashiCorp Vault, AWS Secrets Manager); never ship secrets in the binary; scan builds for embedded keys.

---

_Source: [https://www.quokka.io/blog/the-state-of-mobile-app-security-2026-report-findings](https://www.quokka.io/blog/the-state-of-mobile-app-security-2026-report-findings)_  ·  [← back to index](../README.md)
