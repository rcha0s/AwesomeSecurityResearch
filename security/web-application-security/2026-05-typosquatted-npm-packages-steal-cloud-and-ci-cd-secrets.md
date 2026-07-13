# Typosquatted npm packages steal cloud and CI/CD secrets

**Track:** Security  ·  **Domain:** Web Application Security  ·  **Subtype:** Supply Chain  
**Source:** [Microsoft Security Blog](https://www.microsoft.com/en-us/security/blog/2026/05/28/typosquatted-npm-packages-used-steal-cloud-ci-cd-secrets/)  ·  **Disclosed:** May 2026  
**Scores:** 🆕 Newness 20 · ✨ Novelty 0 · 🎯 Relevance 0 · **Composite 6.0**

## Threat · Conditions · Mitigations

- **Threat —** A single actor published 14 malicious packages in ~4 hours typosquatting OpenSearch/ElasticSearch/DevOps libraries; on install they harvest AWS credentials, HashiCorp Vault tokens, and CI/CD pipeline secrets.
- **Conditions —** Affects developer and CI environments that install packages by name without verifying the publisher, especially with ambient cloud credentials present.
- **Mitigations —** Use scoped/internal registries and name allow-lists; remove standing secrets from build hosts (use OIDC short-lived tokens); scan installs; enforce typosquat detection and 2FA on publishing.

---

_Source: [https://www.microsoft.com/en-us/security/blog/2026/05/28/typosquatted-npm-packages-used-steal-cloud-ci-cd-secrets/](https://www.microsoft.com/en-us/security/blog/2026/05/28/typosquatted-npm-packages-used-steal-cloud-ci-cd-secrets/)_  ·  [← back to index](../README.md)
