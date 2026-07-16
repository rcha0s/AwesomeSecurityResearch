# ToolHive MCP SSRF: host-side discovery runs outside the sandbox it enforces

**Topic:** AI Security  ·  **Domain:** MCP & Tools  
**Source:** [source](https://github.com/advisories/GHSA-pr64-jmmf-jp54)  ·  **Published:** Jul 15, 2026  ·  **Retrieved:** 2026-07-16  
**Scores:** 🆕 Newness 43 · ✨ Novelty 78 · 🎯 Relevance 85 · 🏛️ Credibility 70 · **Composite 70.15**  
**Tags:** `mcp`, `ssrf`, `agent-security`, `cloud-metadata`, `sandbox-escape`  
**Verification:** ✓ independently verified · closest prior art: Classic cloud-metadata SSRF (169.254.169.254) is well known; the novel delta is the MCP-specific vector — a control running host-side, outside the very container sandbox the tool advertises, reached purely through a server's auth-discovery response.

> **Takeaway —** Put SSRF guards on every outbound client that touches untrusted input, re-validate redirect targets, and never suppress a taint warning on a 'trusted config' premise your threat model calls untrusted.

## TL;DR

_The gist, not every detail — read the [full source](https://github.com/advisories/GHSA-pr64-jmmf-jp54) for the complete write-up._

ToolHive isolates every MCP server in a container, but its remote-auth discovery code runs host-side, outside that sandbox, and follows a server-controlled `WWW-Authenticate: resource_metadata` URL (and its redirects) with no private-IP guard. A malicious remote MCP server can 302 the host to 169.254.169.254; where AWS IMDSv1 is enabled that returns IAM credentials directly, and on IMDSv2/GCP the reachable impact is the broader internal-GET surface — either way the exact reach the container sandbox exists to deny.

## What to learn

- A security control that runs outside the boundary it protects doesn't count: the discovery code executes in the host process, before the per-server container sandbox. — _"This discovery code runs host-side, in the ToolHive process, before and outside that per-server container sandbox."_ ✅
- The SSRF was actively waved through: maintainers added `#nosec G704` suppressions asserting the URL was 'internal config', a premise that contradicts the project's own 'MCP server is untrusted' threat model. — _"The maintainers saw the taint-analysis warning on these requests and waved it through on a trust assumption that contradicts the project's design."_ ✅
- Validating only the initial URL is not enough — the redirect target must be re-validated, because an HTTPS metadata URL can 302 to an internal http address. — _"Re-validating the redirect target, not only the initial URL, is the load-bearing part"_ ✅

## Threat · Conditions · Mitigations

- **Threat —** A remote MCP server the victim intentionally connects to can drive the host to issue arbitrary internal GETs and, on AWS IMDSv1, exfiltrate IAM credentials.
- **Conditions —** User adds/runs a malicious or compromised remote MCP server via the normal `thv run --remote-auth` workflow; no user targeting of an internal address needed.
- **Mitigations —** Wrap discovery clients with the existing IsPrivateIP dialer guard, set CheckRedirect to reject cross-host/scheme-downgrade redirects, and re-validate every redirect hop — not just the first URL.

## Actionable leverage

**[harness]** SSRF-guard every host-side fetch in an agent/MCP runtime — For any outbound request whose URL derives from a tool/server response, enforce a private-IP dialer deny-list AND a CheckRedirect that re-applies it to each hop; treat `#nosec`/lint suppressions on such sinks as findings to review against the threat model, not settled decisions.

---

_Source: [https://github.com/advisories/GHSA-pr64-jmmf-jp54](https://github.com/advisories/GHSA-pr64-jmmf-jp54)_  ·  [← back to index](../README.md)
