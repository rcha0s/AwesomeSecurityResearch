# Awesome Security Research [![Awesome](https://cdn.jsdelivr.net/gh/sindresorhus/awesome@d7305f38d29fed78fa85652e3a63e154dd8e8829/media/badge.svg)](https://github.com/sindresorhus/awesome)

> A continuously updated, source-cited tracker of the most relevant **new** security research across **AI Security**, **Web Application Security**, and **Mobile Security** — covering the trailing six months only.

![Last updated](https://img.shields.io/badge/updated-2026--06--18-blue) ![Entries](https://img.shields.io/badge/tracked_findings-20-success) ![Window](https://img.shields.io/badge/window-last_6_months-orange) ![License](https://img.shields.io/badge/license-CC--BY--4.0-lightgrey)

Every entry distills a single finding into four things: the **threat**, the **conditions** under which it applies, the **mitigations**, and a link to the **original credible source**. Sources are limited to first-party security researchers, vendor research teams, standards bodies, and peer-reviewed venues. News aggregators and rumor are excluded by design.

## Why this list

- **New, not noise.** Only research disclosed in the trailing six months is kept; older findings age out automatically.
- **Credible by construction.** Sources are an allow-list of recognized research teams and standards bodies (see [Sources & Methodology](#sources--methodology)).
- **Actionable.** Each finding is summarized as threat → conditions → mitigations, so it is usable by defenders, not just readers.
- **Auditable & automated.** A scheduled job pulls fresh research from source feeds; the curated set is human-reviewed. The data lives in [`data/research.json`](data/research.json) as the single source of truth.

## At a glance

| Domain | Findings | Subtypes |
| --- | --- | --- |
| [AI Security](#ai-security) | 7 | Agentic AI / MCP, Agentic AI / Supply Chain, Information Disclosure, Prompt Injection, RAG / Data Poisoning |
| [Web Application Security](#web-application-security) | 8 | AI-Generated Code Risk, Access Control, Request Smuggling / Desync, Supply Chain, WAF Bypass |
| [Mobile Security](#mobile-security) | 5 | Insecure Storage / Cryptography, Legacy CVE Exposure, Spyware / Zero-Day |
| **Total** | **20** | 20 curated · 0 pending review |

## Contents

- [AI Security](#ai-security)
- [Web Application Security](#web-application-security)
- [Mobile Security](#mobile-security)
- [Sources & Methodology](#sources--methodology)
- [How it stays current](#how-it-stays-current)
- [Contributing](#contributing)
- [License](#license)

---

## AI Security

### Agentic AI / MCP

#### MCP tool poisoning attacks (TPAs) via hidden tool-description metadata

**Severity:** 🔴 Critical  ·  **Disclosed:** Feb 2026  ·  **Subtype:** Agentic AI / MCP

- **Threat —** Malicious instructions hidden in Model Context Protocol tool descriptions (metadata read by the model but not shown to users) coerce agents into leaking data or invoking dangerous tools. Studies found a large share of MCP servers also contain command injection, path traversal, and SSRF flaws.
- **Conditions —** Affects AI agents that auto-load third-party MCP servers/tools and trust tool descriptions as benign; worsened by excessive autonomy and broad credential scope.
- **Mitigations —** Pin and review MCP servers from trusted publishers only; render and audit full tool descriptions; sandbox tool execution; apply least-privilege credentials and per-tool allow-lists; monitor for anomalous tool calls.
- **Source —** [Checkmarx Zero](https://checkmarx.com/zero-post/11-emerging-ai-security-risks-with-mcp-model-context-protocol/) *( Vendor research )*

#### Systemic MCP implementation flaw exposes up to ~200k instances

**Severity:** 🔴 Critical  ·  **Disclosed:** May 2026  ·  **Subtype:** Agentic AI / MCP

- **Threat —** Researchers disclosed a systemic vulnerability in widely used MCP implementations (across Python, TypeScript, Java, and Rust), described as a core AI supply-chain weakness exposing large numbers of MCP instances embedded in IDEs, internal tools, and cloud services.
- **Conditions —** Affects deployments that expose or embed vulnerable MCP server implementations, particularly network-reachable or IDE-integrated instances.
- **Mitigations —** Inventory all MCP instances; patch to fixed implementation versions; remove network exposure; require authentication; apply egress controls and continuous SCA on AI tooling dependencies.
- **Source —** [OX Security (via OWASP GenAI round-up)](https://genai.owasp.org/2026/04/14/owasp-genai-exploit-round-up-report-q1-2026/) *( Vendor research / consortium )*

### Agentic AI / Supply Chain

#### AI agent skill registry poisoned at scale (ClawHub)

**Severity:** 🟠 High  ·  **Disclosed:** Mar 2026  ·  **Subtype:** Agentic AI / Supply Chain

- **Threat —** An AI agent skill marketplace became the first registry systematically poisoned at scale, with several of the most-downloaded skills confirmed as malware, enabling credential theft and code execution inside agent environments.
- **Conditions —** Affects teams that install community agent skills/plugins automatically without provenance checks or sandboxing.
- **Mitigations —** Vet and pin skills by publisher and hash; isolate skill execution; scan skills for malicious behavior; prefer signed/verified sources; monitor for post-install network and credential access.
- **Source —** [OWASP GenAI Security Project](https://genai.owasp.org/2026/04/14/owasp-genai-exploit-round-up-report-q1-2026/) *( Industry consortium report )*

### Information Disclosure

#### System-prompt extraction remains broadly effective

**Severity:** 🟡 Medium  ·  **Disclosed:** Jan 2026  ·  **Subtype:** Information Disclosure

- **Threat —** Multi-step prompting that exploits a model's tendency to summarize or restate its own instructions reliably extracts hidden system prompts, exposing guardrails, secrets, and business logic.
- **Conditions —** Affects assistants that place sensitive instructions, keys, or policy in the system prompt and expose a conversational interface.
- **Mitigations —** Never store secrets in prompts; minimize sensitive content in system prompts; add extraction-pattern detection; enforce output filters; treat the system prompt as non-confidential by design.
- **Source —** [TokenMix LLM Security News](https://tokenmix.ai/blog/llm-security-news-2026-attacks-defenses-updates) *( Industry analysis )*

### Prompt Injection

#### Image-based prompt injection hijacks multimodal LLMs

**Severity:** 🟠 High  ·  **Disclosed:** Jan 2026  ·  **Subtype:** Prompt Injection

- **Threat —** Adversarial instructions are visually embedded in images (including steganographic or low-contrast text and QR codes) and interpreted as commands by multimodal models, hijacking behavior without any malicious text in the prompt.
- **Conditions —** Applies to multimodal LLMs that accept user- or web-supplied images, especially in agentic pipelines that screenshot pages or process uploaded media.
- **Mitigations —** Sanitize/normalize images before model ingestion; separate visual content from instruction channels; OCR-and-scan images for embedded instructions; restrict actions the model can take from image-derived content.
- **Source —** [Cloud Security Alliance (CSA) Labs](https://labs.cloudsecurityalliance.org/research/csa-research-note-image-prompt-injection-multimodal-llm-2026/) *( Industry consortium research )*

#### First large-scale indirect prompt injection attacks observed in the wild

**Severity:** 🟠 High  ·  **Disclosed:** Mar 2026  ·  **Subtype:** Prompt Injection

- **Threat —** Adversaries embed hidden instructions inside content an LLM later retrieves (web pages, documents, ad copy) rather than in the user's direct prompt. Unit 42 documented the first large-scale, real-world cases, including ad-review evasion and system-prompt leakage on live commercial platforms.
- **Conditions —** Affects LLM apps and agents that ingest untrusted external data (RAG, browsing, email/doc summarization, tool output) and act on it without isolating instructions from data.
- **Mitigations —** Treat all retrieved content as untrusted data, not instructions; enforce strict input/output boundaries and content provenance; constrain tool/agent permissions with allow-lists; add injection detection and human-in-the-loop for high-impact actions.
- **Source —** [Palo Alto Networks Unit 42](https://unit42.paloaltonetworks.com/monitoring-npm-supply-chain-attacks/) *( Vendor research )*

### RAG / Data Poisoning

#### RAG poisoning via injected malicious documents in the retrieval corpus

**Severity:** 🟠 High  ·  **Disclosed:** Feb 2026  ·  **Subtype:** RAG / Data Poisoning

- **Threat —** Adversaries plant malicious documents in the retrieval corpus so the model surfaces and acts on attacker-controlled content, enabling misinformation, data exfiltration prompts, or indirect injection at query time.
- **Conditions —** Affects RAG systems that ingest from open or weakly-governed sources (wikis, ticketing, web crawls, user uploads) without content validation.
- **Mitigations —** Govern ingestion with source allow-lists and validation; sign/verify trusted documents; isolate retrieved text from instruction context; add retrieval-time anomaly detection and provenance metadata.
- **Source —** [OWASP GenAI / TokenMix analysis](https://tokenmix.ai/blog/llm-security-news-2026-attacks-defenses-updates) *( Industry analysis )*

---

## Web Application Security

### AI-Generated Code Risk

#### AI-authored code is a leading source of new web-app vulnerabilities

**Severity:** 🟡 Medium  ·  **Disclosed:** Feb 2026  ·  **Subtype:** AI-Generated Code Risk

- **Threat —** With 90%+ of organizations using AI coding assistants, AI-generated code has become a top AppSec blind spot, frequently introducing injection, auth, and secrets-handling flaws that ship faster than review can catch.
- **Conditions —** Affects teams shipping AI-assisted code without commensurate review, SAST, and secrets scanning in the pipeline.
- **Mitigations —** Mandate human review of AI-generated code; enforce SAST/DAST and secret scanning in CI; add guardrail prompts and policy; track provenance of generated code; security-train developers on AI pitfalls.
- **Source —** [Cycode](https://cycode.com/blog/application-security-vulnerabilities/) *( Vendor research )*

### Access Control

#### OWASP Top 10:2025 — Broken Access Control (#1) now subsumes SSRF

**Severity:** 🟠 High  ·  **Disclosed:** Nov 2025  ·  **Subtype:** Access Control

- **Threat —** The 2025 Top 10 (based on 175k+ vulnerabilities) keeps Broken Access Control at #1 and folds in Server-Side Request Forgery, reflecting how missing authorization and SSRF let attackers reach internal services and data.
- **Conditions —** Affects apps with object-level/function-level authorization gaps or server-side fetchers that accept user-controlled URLs.
- **Mitigations —** Enforce server-side authorization on every request; deny-by-default; validate and allow-list outbound URLs; block link-local/metadata endpoints; add automated access-control tests.
- **Source —** [OWASP Foundation](https://owasp.org/www-project-top-ten/) *( Standards body )*

### Request Smuggling / Desync

#### CL.0 and browser-powered desync request smuggling

**Severity:** 🟠 High  ·  **Disclosed:** Dec 2025  ·  **Subtype:** Request Smuggling / Desync

- **Threat —** PortSwigger research on browser-powered desync and CL.0 shows back-end servers can be made to ignore Content-Length, enabling request smuggling without chunked encoding or HTTP/2 downgrade, leading to request hijacking and cache poisoning.
- **Conditions —** Affects multi-tier deployments where front-end and back-end disagree on request boundaries (reverse proxies, CDNs, load balancers).
- **Mitigations —** Normalize request parsing across tiers; prefer HTTP/2 end-to-end and reject ambiguous Content-Length; deploy current proxy/server versions; test with smuggling tooling; the longer-term fix is retiring HTTP/1.1 back-ends.
- **Source —** [PortSwigger Research](https://portswigger.net/research/browser-powered-desync-attacks) *( Vendor research )*

### Supply Chain

#### Axios npm package compromised (100M+ weekly downloads)

**Severity:** 🔴 Critical  ·  **Disclosed:** Mar 2026  ·  **Subtype:** Supply Chain

- **Threat —** Malicious Axios versions (1.14.1, 0.30.4) were published with an injected dependency that pulled payloads from attacker C2. Microsoft attributed it to the North Korean actor Sapphire Sleet. CISA issued an alert.
- **Conditions —** Affects projects that installed or auto-updated to the malicious versions of this widely used HTTP client.
- **Mitigations —** Pin to known-good Axios versions and rebuild; audit lockfiles; rotate any exposed secrets; enable install-time scanning and provenance checks; subscribe to ecosystem advisories.
- **Source —** [Microsoft Security / CISA](https://www.cisa.gov/news-events/alerts/2026/04/20/supply-chain-compromise-impacts-axios-node-package-manager) *( Vendor + government advisory )*

#### New OWASP category: Software Supply Chain Failures (A03)

**Severity:** 🟠 High  ·  **Disclosed:** Nov 2025  ·  **Subtype:** Supply Chain

- **Threat —** OWASP added a dedicated Software Supply Chain Failures category, recognizing dependency, build-pipeline, and artifact-integrity risks as a top web-app risk class distinct from generic vulnerable components.
- **Conditions —** Affects any application consuming third-party packages, build actions, or container bases without integrity verification.
- **Mitigations —** Maintain an SBOM; pin and verify dependencies by hash; use signed artifacts and provenance (SLSA); restrict CI permissions; continuously scan and monitor for compromised packages.
- **Source —** [OWASP Foundation](https://owasp.org/www-project-top-ten/) *( Standards body )*

#### Typosquatted npm packages steal cloud and CI/CD secrets

**Severity:** 🟠 High  ·  **Disclosed:** May 2026  ·  **Subtype:** Supply Chain

- **Threat —** A single actor published 14 malicious packages in ~4 hours typosquatting OpenSearch/ElasticSearch/DevOps libraries; on install they harvest AWS credentials, HashiCorp Vault tokens, and CI/CD pipeline secrets.
- **Conditions —** Affects developer and CI environments that install packages by name without verifying the publisher, especially with ambient cloud credentials present.
- **Mitigations —** Use scoped/internal registries and name allow-lists; remove standing secrets from build hosts (use OIDC short-lived tokens); scan installs; enforce typosquat detection and 2FA on publishing.
- **Source —** [Microsoft Security Blog](https://www.microsoft.com/en-us/security/blog/2026/05/28/typosquatted-npm-packages-used-steal-cloud-ci-cd-secrets/) *( Vendor research )*

#### @redhat-cloud-services npm namespace compromise (32+ packages)

**Severity:** 🟠 High  ·  **Disclosed:** Jun 2026  ·  **Subtype:** Supply Chain

- **Threat —** Attackers compromised at least 32 packages under the @redhat-cloud-services scope, bypassing code review to push a payload dubbed Miasma.
- **Conditions —** Affects consumers of the affected scoped packages and downstream builds that pulled compromised versions.
- **Mitigations —** Identify affected versions from the Red Hat advisory; pin to clean releases; rotate impacted credentials; verify package signatures/provenance; harden publishing with mandatory review and 2FA.
- **Source —** [Red Hat Security](https://access.redhat.com/security/vulnerabilities/RHSB-2026-006) *( Vendor advisory )*

### WAF Bypass

#### WAFFLED: parsing discrepancies bypass web application firewalls

**Severity:** 🟡 Medium  ·  **Disclosed:** Dec 2025  ·  **Subtype:** WAF Bypass

- **Threat —** Academic work shows attackers exploit differences in how WAFs and back-ends parse requests (encodings, multipart, content types) to slip malicious payloads past the WAF that the application still processes.
- **Conditions —** Affects apps relying on a WAF as a primary control where WAF and origin parse input differently.
- **Mitigations —** Do not treat the WAF as the sole defense; fix root-cause input handling; align parsing between WAF and app; canonicalize input; keep WAF rule/engine updated and test bypass classes.
- **Source —** [arXiv (WAFFLED)](https://arxiv.org/pdf/2503.10846) *( Academic research )*

---

## Mobile Security

### Insecure Storage / Cryptography

#### 50+ mobile apps ship hardcoded AWS credentials

**Severity:** 🔴 Critical  ·  **Disclosed:** Feb 2026  ·  **Subtype:** Insecure Storage / Cryptography

- **Threat —** More than 50 apps were found with hardcoded AWS credentials in their binaries, giving attackers a direct path to production databases, customer data, and in some cases root-level cloud control.
- **Conditions —** Affects apps that embed long-lived cloud credentials for backend access instead of brokering access server-side.
- **Mitigations —** Remove all cloud credentials from clients; use short-lived tokens via an authenticated backend (Cognito/STS/OIDC); rotate exposed keys immediately; add CI checks that fail builds containing credentials.
- **Source —** [Quokka (State of Mobile App Security 2026)](https://www.quokka.io/blog/the-state-of-mobile-app-security-2026-report-findings) *( Vendor research report )*

#### Hardcoded cryptographic keys in 47.8% of Android and 17.6% of iOS apps

**Severity:** 🟠 High  ·  **Disclosed:** Feb 2026  ·  **Subtype:** Insecure Storage / Cryptography

- **Threat —** Quokka's analysis of 150k+ apps found cryptographic keys embedded directly in app binaries. Because every install ships the same key, extraction via trivial decompilation compromises all users' protected data retroactively.
- **Conditions —** Affects apps that embed symmetric keys or secrets in the binary for on-device encryption or API access.
- **Mitigations —** Move on-device keys to Android Keystore / iOS Secure Enclave; fetch secrets at runtime from an authenticated vault (HashiCorp Vault, AWS Secrets Manager); never ship secrets in the binary; scan builds for embedded keys.
- **Source —** [Quokka (State of Mobile App Security 2026)](https://www.quokka.io/blog/the-state-of-mobile-app-security-2026-report-findings) *( Vendor research report )*

### Legacy CVE Exposure

#### Shipped apps carry years-old Critical CVEs in bundled components

**Severity:** 🟠 High  ·  **Disclosed:** Feb 2026  ·  **Subtype:** Legacy CVE Exposure

- **Threat —** Quokka found Android apps shipping Critical CVEs spanning nearly a decade of unpatched components, and 2,075 iOS apps containing a Critical CVE first disclosed in 2023 — outdated bundled SDKs/libraries remain a major exposure.
- **Conditions —** Affects apps bundling outdated third-party SDKs/native libraries without dependency patching.
- **Mitigations —** Maintain a mobile SBOM; continuously scan bundled SDKs for known CVEs; patch/upgrade dependencies on a schedule; gate releases on component vulnerability checks.
- **Source —** [Quokka (State of Mobile App Security 2026)](https://www.quokka.io/blog/the-state-of-mobile-app-security-2026-report-findings) *( Vendor research report )*

### Spyware / Zero-Day

#### LANDFALL spyware exploited Samsung zero-day (CVE-2025-21042)

**Severity:** 🔴 Critical  ·  **Disclosed:** Nov 2025  ·  **Subtype:** Spyware / Zero-Day

- **Threat —** Commercial-grade Android spyware exploited a zero-day in a Samsung image-processing library (CVE-2025-21042) via malicious DNG image files delivered over WhatsApp, achieving remote code execution with little/no user interaction; capabilities include mic recording, location tracking, and data theft.
- **Conditions —** Affected unpatched Samsung Galaxy devices (campaign active mid-2024 to patch in April 2025); targeted individuals in the Middle East/North Africa.
- **Mitigations —** Apply Samsung security updates (patched April 2025); keep messaging apps and OS current; use lockdown/hardening modes for high-risk users; deploy mobile threat detection.
- **Source —** [Palo Alto Networks Unit 42](https://unit42.paloaltonetworks.com/landfall-is-new-commercial-grade-android-spyware/) *( Vendor research )*

#### Qualcomm zero-day (CVE-2026-21385) in March 2026 Android update

**Severity:** 🔴 Critical  ·  **Disclosed:** Mar 2026  ·  **Subtype:** Spyware / Zero-Day

- **Threat —** The March 2026 Android security bulletin patched 129 vulnerabilities including a Qualcomm zero-day (CVE-2026-21385) reported as affecting a large number of chipset models, exploitable in the wild.
- **Conditions —** Affects Android devices on vulnerable Qualcomm chipsets prior to the March 2026 patch level.
- **Mitigations —** Apply the March 2026 (or later) Android security patch level; enforce minimum patch level via MDM; prioritize devices on affected chipsets.
- **Source —** [Android Security Bulletin (via Vervali analysis)](https://www.vervali.com/blog/android-malware-statistics-2026-threat-landscape-ios-comparison-and-detection-trends/) *( Vendor advisory / analysis )*

---

## Sources & Methodology

Findings are sourced from a curated allow-list of credible security research publishers. The feed configuration lives in [`scripts/sources.yaml`](scripts/sources.yaml). Current sources include:

| Source | Type | Primary coverage |
| --- | --- | --- |
| [Android Security Bulletin (via Vervali analysis)](https://www.vervali.com/blog/android-malware-statistics-2026-threat-landscape-ios-comparison-and-detection-trends/) | Vendor advisory / analysis | Mobile Security |
| [Checkmarx Zero](https://checkmarx.com/zero-post/11-emerging-ai-security-risks-with-mcp-model-context-protocol/) | Vendor research | AI Security |
| [Cloud Security Alliance (CSA) Labs](https://labs.cloudsecurityalliance.org/research/csa-research-note-image-prompt-injection-multimodal-llm-2026/) | Industry consortium research | AI Security |
| [Cycode](https://cycode.com/blog/application-security-vulnerabilities/) | Vendor research | Web Application Security |
| [Microsoft Security / CISA](https://www.cisa.gov/news-events/alerts/2026/04/20/supply-chain-compromise-impacts-axios-node-package-manager) | Vendor + government advisory | Web Application Security |
| [Microsoft Security Blog](https://www.microsoft.com/en-us/security/blog/2026/05/28/typosquatted-npm-packages-used-steal-cloud-ci-cd-secrets/) | Vendor research | Web Application Security |
| [OWASP Foundation](https://owasp.org/www-project-top-ten/) | Standards body | Web Application Security |
| [OWASP GenAI / TokenMix analysis](https://tokenmix.ai/blog/llm-security-news-2026-attacks-defenses-updates) | Industry analysis | AI Security |
| [OWASP GenAI Security Project](https://genai.owasp.org/2026/04/14/owasp-genai-exploit-round-up-report-q1-2026/) | Industry consortium report | AI Security |
| [OX Security (via OWASP GenAI round-up)](https://genai.owasp.org/2026/04/14/owasp-genai-exploit-round-up-report-q1-2026/) | Vendor research / consortium | AI Security |
| [Palo Alto Networks Unit 42](https://unit42.paloaltonetworks.com/monitoring-npm-supply-chain-attacks/) | Vendor research | AI Security |
| [PortSwigger Research](https://portswigger.net/research/browser-powered-desync-attacks) | Vendor research | Web Application Security |
| [Quokka (State of Mobile App Security 2026)](https://www.quokka.io/blog/the-state-of-mobile-app-security-2026-report-findings) | Vendor research report | Mobile Security |
| [Red Hat Security](https://access.redhat.com/security/vulnerabilities/RHSB-2026-006) | Vendor advisory | Web Application Security |
| [TokenMix LLM Security News](https://tokenmix.ai/blog/llm-security-news-2026-attacks-defenses-updates) | Industry analysis | AI Security |
| [arXiv (WAFFLED)](https://arxiv.org/pdf/2503.10846) | Academic research | Web Application Security |

**Inclusion criteria:** (1) first-party research from a recognized team, vendor lab, standards body, or peer-reviewed venue; (2) disclosed within the last six months; (3) a clear, defensible threat with practical mitigations. **Severity** ratings are editorial, harmonized to a Critical/High/Medium/Low scale.

## How it stays current

```
scripts/aggregate.py        # pull feeds -> classify -> filter to last 6 months -> append new items
scripts/generate_readme.py  # render this README from data/research.json
```

A GitHub Actions workflow ([`.github/workflows/update.yml`](.github/workflows/update.yml)) runs weekly: it executes the aggregator, regenerates the README, and opens a commit when anything changes. Auto-discovered items are flagged `pending review` until a maintainer writes the threat/conditions/mitigations and assigns a severity. To run it locally:

```bash
pip install -r requirements.txt
python scripts/aggregate.py        # add newly published research
python scripts/generate_readme.py  # rebuild README.md
```

## Contributing

Contributions are welcome. Add or refine an entry in [`data/research.json`](data/research.json), run `python scripts/generate_readme.py`, and open a PR. Please keep the source allow-list standard high — see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Curated content is released under [CC BY 4.0](LICENSE); the scripts are under the MIT terms noted in [`scripts/`](scripts/). Linked research remains the property of its original authors.

---

<sub>Generated by <code>scripts/generate_readme.py</code> on 2026-06-18. Do not edit README.md by hand — edit <code>data/research.json</code> and regenerate.</sub>
