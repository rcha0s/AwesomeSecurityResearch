# Kemp LoadMaster pre-auth RCE: uninitialized heap + missing null byte (CVE-2026-8037)

**Topic:** Product Security  ·  **Domain:** Application Security  
**Source:** [source](https://labs.watchtowr.com/enterprise-tech-in-shell-out-progress-kemp-loadmaster-uninitialized-heap-to-pre-auth-rce-cve-2026-8037/)  ·  **Published:** Jun 29, 2026  ·  **Retrieved:** 2026-07-16  
**Scores:** 🆕 Newness 8 · ✨ Novelty 70 · 🎯 Relevance 82 · 🏛️ Credibility 75 · **Composite 58.85**  
**Tags:** `memory-safety`, `heap`, `rce`, `edge-appliance`, `n-day`  
**Verification:** ✓ independently verified · closest prior art: Uninitialized-memory and heap-spray techniques are classic; the novel delta is the specific n-day chain (patch-diff -> non-null-terminated escape buffer -> OOB read into sprayed JSON chunk) on a widely deployed edge load balancer.

> **Takeaway —** A minimal 'just null-terminate the buffer' patch can hide a pre-auth RCE — diff patches carefully, and treat missing null-termination next to attacker-controlled heap data as exploitable, not cosmetic.

## TL;DR

_The gist, not every detail — read the [full source](https://labs.watchtowr.com/enterprise-tech-in-shell-out-progress-kemp-loadmaster-uninitialized-heap-to-pre-auth-rce-cve-2026-8037/) for the complete write-up._

A one-function patch to `escape_quotes()` in Kemp LoadMaster revealed a pre-auth RCE. The escaped buffer wasn't null-terminated, so `__sprintf_chk()` reads out of bounds into an adjacent heap chunk; by heap-spraying an un-escaped command-injection payload (via JSON key/value pairs) into that neighboring chunk, an unauthenticated attacker turns an 'uninitialized memory' bug into command execution.

## What to learn

- The whole bug is a missing null terminator: the escaped buffer wasn't null-terminated, so a formatting call runs off the end into adjacent heap memory. — _"the escaped buffer was not null-terminated"_ ✅
- Out-of-bounds read becomes injection when the neighboring freed chunk holds an un-escaped payload with no null byte — the sanitizer is bypassed by reading past where it stopped. — _"That means if an adjacent freed heap chunk contains an unescaped command injection payload"_ ✅
- Attacker-controlled heap layout is the exploit primitive: spraying many JSON key/value pairs places the payload chunk exactly where the OOB read lands. — _"This gives us a useful heap-spraying primitive by adding lots of JSON key/value pairs."_ ✅

## Threat · Conditions · Mitigations

- **Threat —** Unauthenticated remote code execution on an edge load balancer reachable by anyone who can reach the API.
- **Conditions —** Network access to the LoadMaster API; no credentials required.
- **Mitigations —** Apply Progress' June 2026 patch; a tiny-looking diff (adding null-termination) can be the fix for a critical bug, so patch edge appliances promptly.

## Actionable leverage

**[takeaway]** Prioritize edge-appliance patches and read the diff, not the CVE title — When a vendor ships a one-line string-handling fix on an internet-facing appliance, assume memory-corruption impact until proven otherwise and patch on the critical track; missing null-termination adjacent to attacker-sprayable heap data is an RCE primitive, not a hardening nit.

---

_Source: [https://labs.watchtowr.com/enterprise-tech-in-shell-out-progress-kemp-loadmaster-uninitialized-heap-to-pre-auth-rce-cve-2026-8037/](https://labs.watchtowr.com/enterprise-tech-in-shell-out-progress-kemp-loadmaster-uninitialized-heap-to-pre-auth-rce-cve-2026-8037/)_  ·  [← back to index](../README.md)
