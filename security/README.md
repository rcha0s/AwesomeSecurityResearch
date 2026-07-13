# Security Research

> 28 findings · updated 2026-07-13 · ranked by composite score.

| Domain | Findings |
| --- | --- |
| AI Security | 11 |
| Web Application Security | 10 |
| Mobile Security | 7 |

## AI Security

- **[MemoryTrap: persistent memory poisoning in AI coding agents (OWASP ASI06)](ai-security/2026-05-memorytrap-persistent-memory-poisoning-in-ai-coding-agents-o.md)** · composite **68.3** · May 2026  
  Agent memory/persistence is a first-class attack surface: untrusted input carried forward becomes durable, trusted instruction.  
  _[OWASP GenAI Security Project](https://genai.owasp.org/2026/05/13/memory-is-a-feature-it-is-also-an-attack-surface/)_
- **[Prismor: a runtime firewall that blocks rogue AI-agent tool calls](ai-security/2026-02-prismor-a-runtime-firewall-that-blocks-rogue-ai-agent-tool-c.md)** · composite **56.55** · Feb 2026  
  The strongest control point for agent safety is the tool-call boundary — enforce policy at call time, not just in the prompt.  
  _[PrismorSec/prismor](https://github.com/PrismorSec/prismor)_
- **[Augustus: a production LLM vulnerability scanner (210+ probes)](ai-security/2026-02-augustus-a-production-llm-vulnerability-scanner-210-probes.md)** · composite **55.5** · Feb 2026  
  LLM red-teaming is becoming an operational, CI-ready discipline — run a probe suite against every model/prompt change, not just at launch.  
  _[praetorian-inc/augustus](https://github.com/praetorian-inc/augustus)_
- **[Prompt injection in the wild: Google on the current state](ai-security/2026-04-prompt-injection-in-the-wild-google-on-the-current-state.md)** · composite **54.1** · Apr 2026  
  Indirect prompt injection is now an operational threat, not a theoretical one; design agents assuming hostile web content.  
  _[Google Online Security Blog](http://security.googleblog.com/2026/04/ai-threats-in-wild-current-state-of.html)_
- **[Systemic MCP implementation flaw exposes up to ~200k instances](ai-security/2026-05-systemic-mcp-implementation-flaw-exposes-up-to-200k-instance.md)** · composite **6.0** · May 2026  
  Researchers disclosed a systemic vulnerability in widely used MCP implementations (across Python, TypeScript, Java, and Rust), described as a core AI supply-chain weakness exposing large numbers of…  
  _[OX Security (via OWASP GenAI round-up)](https://genai.owasp.org/2026/04/14/owasp-genai-exploit-round-up-report-q1-2026/)_
- **[AI agent skill registry poisoned at scale (ClawHub)](ai-security/2026-03-ai-agent-skill-registry-poisoned-at-scale-clawhub.md)** · composite **1.5** · Mar 2026  
  An AI agent skill marketplace became the first registry systematically poisoned at scale, with several of the most-downloaded skills confirmed as malware, enabling credential theft and code execution…  
  _[OWASP GenAI Security Project](https://genai.owasp.org/2026/04/14/owasp-genai-exploit-round-up-report-q1-2026/)_
- **[First large-scale indirect prompt injection attacks observed in the wild](ai-security/2026-03-first-large-scale-indirect-prompt-injection-attacks-observed.md)** · composite **1.5** · Mar 2026  
  Adversaries embed hidden instructions inside content an LLM later retrieves (web pages, documents, ad copy) rather than in the user's direct prompt. Unit 42 documented the first large-scale,…  
  _[Palo Alto Networks Unit 42](https://unit42.paloaltonetworks.com/monitoring-npm-supply-chain-attacks/)_
- **[MCP tool poisoning attacks (TPAs) via hidden tool-description metadata](ai-security/2026-02-mcp-tool-poisoning-attacks-tpas-via-hidden-tool-description.md)** · composite **0.9** · Feb 2026  
  Malicious instructions hidden in Model Context Protocol tool descriptions (metadata read by the model but not shown to users) coerce agents into leaking data or invoking dangerous tools. Studies…  
  _[Checkmarx Zero](https://checkmarx.com/zero-post/11-emerging-ai-security-risks-with-mcp-model-context-protocol/)_
- **[RAG poisoning via injected malicious documents in the retrieval corpus](ai-security/2026-02-rag-poisoning-via-injected-malicious-documents-in-the-retrie.md)** · composite **0.9** · Feb 2026  
  Adversaries plant malicious documents in the retrieval corpus so the model surfaces and acts on attacker-controlled content, enabling misinformation, data exfiltration prompts, or indirect injection…  
  _[OWASP GenAI / TokenMix analysis](https://tokenmix.ai/blog/llm-security-news-2026-attacks-defenses-updates)_
- **[Image-based prompt injection hijacks multimodal LLMs](ai-security/2026-01-image-based-prompt-injection-hijacks-multimodal-llms.md)** · composite **0.3** · Jan 2026  
  Adversarial instructions are visually embedded in images (including steganographic or low-contrast text and QR codes) and interpreted as commands by multimodal models, hijacking behavior without any…  
  _[Cloud Security Alliance (CSA) Labs](https://labs.cloudsecurityalliance.org/research/csa-research-note-image-prompt-injection-multimodal-llm-2026/)_
- **[System-prompt extraction remains broadly effective](ai-security/2026-01-system-prompt-extraction-remains-broadly-effective.md)** · composite **0.3** · Jan 2026  
  Multi-step prompting that exploits a model's tendency to summarize or restate its own instructions reliably extracts hidden system prompts, exposing guardrails, secrets, and business logic.  
  _[TokenMix LLM Security News](https://tokenmix.ai/blog/llm-security-news-2026-attacks-defenses-updates)_

## Web Application Security

- **[Phantom Squatting: attackers register the domains LLMs hallucinate](web-application-security/2026-07-phantom-squatting-attackers-register-the-domains-llms-halluc.md)** · composite **84.7** · Jul 2026  
  LLM hallucinations are a predictable supply-chain attack surface: attackers pre-register the domains/packages models invent.  
  _[Palo Alto Networks Unit 42](https://unit42.paloaltonetworks.com/phantom-squatting-hallucinated-web-domains/)_
- **[PortSwigger's Top 10 Web Hacking Techniques of 2025](web-application-security/2026-02-portswigger-s-top-10-web-hacking-techniques-of-2025.md)** · composite **52.0** · Feb 2026  
  The single best reading list for web-security researchers each year — a curated map of the techniques that will define the next cycle of attacks.  
  _[PortSwigger Research](https://portswigger.net/research/top-10-web-hacking-techniques-of-2025)_
- **[@redhat-cloud-services npm namespace compromise (32+ packages)](web-application-security/2026-06-redhat-cloud-services-npm-namespace-compromise-32-packages.md)** · composite **11.7** · Jun 2026  
  Attackers compromised at least 32 packages under the @redhat-cloud-services scope, bypassing code review to push a payload dubbed Miasma.  
  _[Red Hat Security](https://access.redhat.com/security/vulnerabilities/RHSB-2026-006)_
- **[Typosquatted npm packages steal cloud and CI/CD secrets](web-application-security/2026-05-typosquatted-npm-packages-steal-cloud-and-ci-cd-secrets.md)** · composite **6.0** · May 2026  
  A single actor published 14 malicious packages in ~4 hours typosquatting OpenSearch/ElasticSearch/DevOps libraries; on install they harvest AWS credentials, HashiCorp Vault tokens, and CI/CD pipeline…  
  _[Microsoft Security Blog](https://www.microsoft.com/en-us/security/blog/2026/05/28/typosquatted-npm-packages-used-steal-cloud-ci-cd-secrets/)_
- **[Axios npm package compromised (100M+ weekly downloads)](web-application-security/2026-03-axios-npm-package-compromised-100m-weekly-downloads.md)** · composite **1.5** · Mar 2026  
  Malicious Axios versions (1.14.1, 0.30.4) were published with an injected dependency that pulled payloads from attacker C2. Microsoft attributed it to the North Korean actor Sapphire Sleet. CISA…  
  _[Microsoft Security / CISA](https://www.cisa.gov/news-events/alerts/2026/04/20/supply-chain-compromise-impacts-axios-node-package-manager)_
- **[AI-authored code is a leading source of new web-app vulnerabilities](web-application-security/2026-02-ai-authored-code-is-a-leading-source-of-new-web-app-vulnerab.md)** · composite **0.9** · Feb 2026  
  With 90%+ of organizations using AI coding assistants, AI-generated code has become a top AppSec blind spot, frequently introducing injection, auth, and secrets-handling flaws that ship faster than…  
  _[Cycode](https://cycode.com/blog/application-security-vulnerabilities/)_
- **[CL.0 and browser-powered desync request smuggling](web-application-security/2025-12-cl-0-and-browser-powered-desync-request-smuggling.md)** · composite **0.3** · Dec 2025  
  PortSwigger research on browser-powered desync and CL.0 shows back-end servers can be made to ignore Content-Length, enabling request smuggling without chunked encoding or HTTP/2 downgrade, leading…  
  _[PortSwigger Research](https://portswigger.net/research/browser-powered-desync-attacks)_
- **[WAFFLED: parsing discrepancies bypass web application firewalls](web-application-security/2025-12-waffled-parsing-discrepancies-bypass-web-application-firewal.md)** · composite **0.3** · Dec 2025  
  Academic work shows attackers exploit differences in how WAFs and back-ends parse requests (encodings, multipart, content types) to slip malicious payloads past the WAF that the application still…  
  _[arXiv (WAFFLED)](https://arxiv.org/pdf/2503.10846)_
- **[New OWASP category: Software Supply Chain Failures (A03)](web-application-security/2025-11-new-owasp-category-software-supply-chain-failures-a03.md)** · composite **0.0** · Nov 2025  
  OWASP added a dedicated Software Supply Chain Failures category, recognizing dependency, build-pipeline, and artifact-integrity risks as a top web-app risk class distinct from generic vulnerable…  
  _[OWASP Foundation](https://owasp.org/www-project-top-ten/)_
- **[OWASP Top 10:2025 — Broken Access Control (#1) now subsumes SSRF](web-application-security/2025-11-owasp-top-10-2025-broken-access-control-1-now-subsumes-ssrf.md)** · composite **0.0** · Nov 2025  
  The 2025 Top 10 (based on 175k+ vulnerabilities) keeps Broken Access Control at #1 and folds in Server-Side Request Forgery, reflecting how missing authorization and SSRF let attackers reach internal…  
  _[OWASP Foundation](https://owasp.org/www-project-top-ten/)_

## Mobile Security

- **[Project Zero: a 0-click exploit chain for the Pixel 10](mobile-security/2026-05-project-zero-a-0-click-exploit-chain-for-the-pixel-10.md)** · composite **61.3** · May 2026  
  0-click chains remain viable on flagship, hardened devices; defense-in-depth and rapid patching still matter most.  
  _[Google Project Zero](https://projectzero.google/2026/05/pixel-10-exploit.html)_
- **[Google brings Rust (memory safety) to the Pixel baseband](mobile-security/2026-04-google-brings-rust-memory-safety-to-the-pixel-baseband.md)** · composite **52.0** · Apr 2026  
  Memory-safe languages are reaching the lowest, most security-critical layers — the baseband — meaningfully shrinking remote attack surface.  
  _[Google Online Security Blog](http://security.googleblog.com/2026/04/bringing-rust-to-pixel-baseband.html)_
- **[Qualcomm zero-day (CVE-2026-21385) in March 2026 Android update](mobile-security/2026-03-qualcomm-zero-day-cve-2026-21385-in-march-2026-android-updat.md)** · composite **1.5** · Mar 2026  
  The March 2026 Android security bulletin patched 129 vulnerabilities including a Qualcomm zero-day (CVE-2026-21385) reported as affecting a large number of chipset models, exploitable in the wild.  
  _[Android Security Bulletin (via Vervali analysis)](https://www.vervali.com/blog/android-malware-statistics-2026-threat-landscape-ios-comparison-and-detection-trends/)_
- **[50+ mobile apps ship hardcoded AWS credentials](mobile-security/2026-02-50-mobile-apps-ship-hardcoded-aws-credentials.md)** · composite **0.9** · Feb 2026  
  More than 50 apps were found with hardcoded AWS credentials in their binaries, giving attackers a direct path to production databases, customer data, and in some cases root-level cloud control.  
  _[Quokka (State of Mobile App Security 2026)](https://www.quokka.io/blog/the-state-of-mobile-app-security-2026-report-findings)_
- **[Hardcoded cryptographic keys in 47.8% of Android and 17.6% of iOS apps](mobile-security/2026-02-hardcoded-cryptographic-keys-in-47-8-of-android-and-17-6-of.md)** · composite **0.9** · Feb 2026  
  Quokka's analysis of 150k+ apps found cryptographic keys embedded directly in app binaries. Because every install ships the same key, extraction via trivial decompilation compromises all users'…  
  _[Quokka (State of Mobile App Security 2026)](https://www.quokka.io/blog/the-state-of-mobile-app-security-2026-report-findings)_
- **[Shipped apps carry years-old Critical CVEs in bundled components](mobile-security/2026-02-shipped-apps-carry-years-old-critical-cves-in-bundled-compon.md)** · composite **0.9** · Feb 2026  
  Quokka found Android apps shipping Critical CVEs spanning nearly a decade of unpatched components, and 2,075 iOS apps containing a Critical CVE first disclosed in 2023 — outdated bundled…  
  _[Quokka (State of Mobile App Security 2026)](https://www.quokka.io/blog/the-state-of-mobile-app-security-2026-report-findings)_
- **[LANDFALL spyware exploited Samsung zero-day (CVE-2025-21042)](mobile-security/2025-11-landfall-spyware-exploited-samsung-zero-day-cve-2025-21042.md)** · composite **0.0** · Nov 2025  
  Commercial-grade Android spyware exploited a zero-day in a Samsung image-processing library (CVE-2025-21042) via malicious DNG image files delivered over WhatsApp, achieving remote code execution…  
  _[Palo Alto Networks Unit 42](https://unit42.paloaltonetworks.com/landfall-is-new-commercial-grade-android-spyware/)_

---

[← Home](../README.md) · [Learnings digest](../LEARNINGS.md)
