# AsyncAPI npm compromise: import-time payload defeats --ignore-scripts

**Topic:** Product Security  ·  **Domain:** Supply Chain & Dependencies  
**Source:** [source](https://www.microsoft.com/en-us/security/blog/2026/07/15/unpacking-asyncapi-npm-supply-chain-compromise-import-time-payload-delivery/)  ·  **Published:** Jul 16, 2026  ·  **Retrieved:** 2026-07-16  
**Scores:** 🆕 Newness 43 · ✨ Novelty 80 · 🎯 Relevance 90 · 🏛️ Credibility 88 · **Composite 74.88**  
**Tags:** `supply-chain`, `npm`, `provenance`, `ci-cd`, `github-actions`  
**Also reported by:** [Semgrep Blog](https://semgrep.dev/blog/2026/miasma-v3-asyncapi-npm-hardening), [Chainguard Unchained](https://www.chainguard.dev/unchained/asyncapi-supply-chain-compromise-npm-packages-backdoored-via-github-actions) _(+2 corroborating)_  
**Verification:** ✓ independently verified · closest prior art: The 2025 Shai-Hulud / npm postinstall-worm campaigns and the related @mastra scope takeover — same 'compromise a maintainer/bot identity' root cause, but those triggered on install hooks; the novel delta here is import-time execution plus abuse of trusted-publishing provenance.

> **Takeaway —** Import-time malware makes --ignore-scripts useless and a valid provenance attestation is not a trust signal when the pipeline itself is hijacked.

## TL;DR

_The gist, not every detail — read the [full source](https://www.microsoft.com/en-us/security/blog/2026/07/15/unpacking-asyncapi-npm-supply-chain-compromise-import-time-payload-delivery/) for the complete write-up._

Attackers backdoored five @asyncapi npm versions that execute at module-load (import/require) time rather than via a postinstall hook, so `npm install --ignore-scripts` doesn't stop them. They didn't compromise npm directly: a `pull_request_target` pwn request exposed the project's bot token (PAT), after which the project's own trusted-publishing (GitHub OIDC) pipeline shipped the poisoned packages with valid provenance attestations.

## What to learn

- The payload runs at import time, not install time — so the standard --ignore-scripts defense is irrelevant; the trigger is require()/import, not a lifecycle hook. — _"Because the trigger is an import rather than an install script"_
- Hook-focused scanners miss this entirely because the packages declare no preinstall/postinstall hooks at all. — _"Security tooling that focuses on preinstall/postinstall auditing will not flag these packages."_
- Trusted publishing / provenance did NOT prevent the attack: valid OIDC attestations were produced from unauthorized commits, so a green provenance check is not proof of a trustworthy release. — _"The attestations accurately identified the legitimate repositories, commits, and workflows that created the packages, even though the triggering commits were unauthorized."_

## Threat · Conditions · Mitigations

- **Threat —** A poisoned transitive dependency runs attacker code on any workstation, CI runner, or container build that imports it, with no install script required.
- **Mitigations —** Pin/lock and vet dependency updates by content (not just provenance); treat import-time behavior as executable; segment CI credentials; audit pull_request_target workflows that check out untrusted PR code.

## Actionable leverage

**[takeaway]** Don't treat provenance/--ignore-scripts as sufficient supply-chain defenses — Add a CI check that diffs a dependency's published tarball against its tagged source before promotion, and audit any pull_request_target workflow that checks out and runs untrusted PR code with access to secrets.

---

_Source: [https://www.microsoft.com/en-us/security/blog/2026/07/15/unpacking-asyncapi-npm-supply-chain-compromise-import-time-payload-delivery/](https://www.microsoft.com/en-us/security/blog/2026/07/15/unpacking-asyncapi-npm-supply-chain-compromise-import-time-payload-delivery/)_  ·  [← back to index](../README.md)
