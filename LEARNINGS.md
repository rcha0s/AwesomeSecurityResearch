# Learnings digest

> Ranked, source-cited takeaways across Security and AI. Updated 2026-07-13.

## 📈 Ranked findings

### Phantom Squatting: attackers register the domains LLMs hallucinate · `84.7`
- **Track:** security / Web Application Security
- **Takeaway:** LLM hallucinations are a predictable supply-chain attack surface: attackers pre-register the domains/packages models invent.
- **Action (tool):** Enumerate & monitor your brand's hallucinated domains — Query LLMs for your brand's URLs/packages at scale, then pre-register or block-list the hallucinated ones and monitor for adversary registration.
- **Source:** [Palo Alto Networks Unit 42](https://unit42.paloaltonetworks.com/phantom-squatting-hallucinated-web-domains/)

### Omnigent: an open-source meta-harness over Claude Code, Codex, Cursor · `68.4`
- **Track:** ai / Agents & Harnesses
- **Takeaway:** The 'meta-harness' is emerging as an abstraction layer above individual coding agents — orchestrate many, swap freely, enforce policy centrally.
- **Action (harness):** Consider a meta-harness for multi-agent work — Evaluate an orchestration layer (like Omnigent) when running multiple coding agents, so policy/sandboxing/routing live in one place instead of per-agent.
- **Source:** [omnigent-ai/omnigent](https://github.com/omnigent-ai/omnigent)

### MemoryTrap: persistent memory poisoning in AI coding agents (OWASP ASI06) · `68.3`
- **Track:** security / AI Security
- **Takeaway:** Agent memory/persistence is a first-class attack surface: untrusted input carried forward becomes durable, trusted instruction.
- **Action (harness):** Isolate and review agent memory writes — Treat writes to persistent memory, hooks, and system-prompt layers as privileged: require explicit review, provenance tracking, and don't let tool output mutate them implicitly.
- **Source:** [OWASP GenAI Security Project](https://genai.owasp.org/2026/05/13/memory-is-a-feature-it-is-also-an-attack-surface/)

### Project Zero: a 0-click exploit chain for the Pixel 10 · `61.3`
- **Track:** security / Mobile Security
- **Takeaway:** 0-click chains remain viable on flagship, hardened devices; defense-in-depth and rapid patching still matter most.
- **Action (takeaway):** Prioritize 0-click attack-surface reduction — Audit message/media parsers reachable without user interaction; keep devices on the latest patch level.
- **Source:** [Google Project Zero](https://projectzero.google/2026/05/pixel-10-exploit.html)

### PawBench: benchmarking LLM x harness performance · `59.2`
- **Track:** ai / Evaluation & Safety
- **Takeaway:** Evaluate the model-plus-harness as a unit; the harness is a first-class variable in agent performance.
- **Action (tool):** Add harness-aware evals — When comparing agents, hold the task set fixed and vary the harness; measure end-to-end task success, not raw model scores.
- **Source:** [agentscope-ai/PawBench](https://github.com/agentscope-ai/PawBench)

### Prismor: a runtime firewall that blocks rogue AI-agent tool calls · `56.55`
- **Track:** security / AI Security
- **Takeaway:** The strongest control point for agent safety is the tool-call boundary — enforce policy at call time, not just in the prompt.
- **Action (harness):** Add a tool-call firewall to your agent harness — Interpose an allow/deny policy layer on every tool call (esp. shell, network, secret access) with human-in-the-loop for high-impact actions.
- **Source:** [PrismorSec/prismor](https://github.com/PrismorSec/prismor)

### Augustus: a production LLM vulnerability scanner (210+ probes) · `55.5`
- **Track:** security / AI Security
- **Takeaway:** LLM red-teaming is becoming an operational, CI-ready discipline — run a probe suite against every model/prompt change, not just at launch.
- **Action (tool):** Adopt an LLM probe suite in CI — Wire Augustus (or garak/promptfoo) into CI to run prompt-injection/jailbreak probes on each model or system-prompt change; gate releases on the report.
- **Source:** [praetorian-inc/augustus](https://github.com/praetorian-inc/augustus)

### Prompt injection in the wild: Google on the current state · `54.1`
- **Track:** security / AI Security
- **Takeaway:** Indirect prompt injection is now an operational threat, not a theoretical one; design agents assuming hostile web content.
- **Action (takeaway):** Assume hostile web content in agent design — For browsing/RAG agents, isolate retrieved content from the instruction channel and constrain downstream tool permissions.
- **Source:** [Google Online Security Blog](http://security.googleblog.com/2026/04/ai-threats-in-wild-current-state-of.html)

### PortSwigger's Top 10 Web Hacking Techniques of 2025 · `52.0`
- **Track:** security / Web Application Security
- **Takeaway:** The single best reading list for web-security researchers each year — a curated map of the techniques that will define the next cycle of attacks.
- **Action (takeaway):** Work through the Top-10 list — Use the annual PortSwigger Top 10 as a study syllabus; reproduce each technique against a lab target to internalize it.
- **Source:** [PortSwigger Research](https://portswigger.net/research/top-10-web-hacking-techniques-of-2025)

### Google brings Rust (memory safety) to the Pixel baseband · `52.0`
- **Track:** security / Mobile Security
- **Takeaway:** Memory-safe languages are reaching the lowest, most security-critical layers — the baseband — meaningfully shrinking remote attack surface.
- **Action (takeaway):** Favor memory-safe rewrites for remote parsers — Target memory-unsafe code on remotely-reachable attack surfaces first when planning Rust migrations.
- **Source:** [Google Online Security Blog](http://security.googleblog.com/2026/04/bringing-rust-to-pixel-baseband.html)

### @redhat-cloud-services npm namespace compromise (32+ packages) · `11.7`
- **Track:** security / Web Application Security
- **Takeaway:** Attackers compromised at least 32 packages under the @redhat-cloud-services scope, bypassing code review to push a payload dubbed Miasma.
- **Source:** [Red Hat Security](https://access.redhat.com/security/vulnerabilities/RHSB-2026-006)

### Systemic MCP implementation flaw exposes up to ~200k instances · `6.0`
- **Track:** security / AI Security
- **Takeaway:** Researchers disclosed a systemic vulnerability in widely used MCP implementations (across Python, TypeScript, Java, and Rust), described as a core AI supply-chain weakness exposing large numbers of MCP instances embedded in IDEs, internal…
- **Source:** [OX Security (via OWASP GenAI round-up)](https://genai.owasp.org/2026/04/14/owasp-genai-exploit-round-up-report-q1-2026/)

### Typosquatted npm packages steal cloud and CI/CD secrets · `6.0`
- **Track:** security / Web Application Security
- **Takeaway:** A single actor published 14 malicious packages in ~4 hours typosquatting OpenSearch/ElasticSearch/DevOps libraries; on install they harvest AWS credentials, HashiCorp Vault tokens, and CI/CD pipeline secrets.
- **Source:** [Microsoft Security Blog](https://www.microsoft.com/en-us/security/blog/2026/05/28/typosquatted-npm-packages-used-steal-cloud-ci-cd-secrets/)

### AI agent skill registry poisoned at scale (ClawHub) · `1.5`
- **Track:** security / AI Security
- **Takeaway:** An AI agent skill marketplace became the first registry systematically poisoned at scale, with several of the most-downloaded skills confirmed as malware, enabling credential theft and code execution inside agent environments.
- **Source:** [OWASP GenAI Security Project](https://genai.owasp.org/2026/04/14/owasp-genai-exploit-round-up-report-q1-2026/)

### Axios npm package compromised (100M+ weekly downloads) · `1.5`
- **Track:** security / Web Application Security
- **Takeaway:** Malicious Axios versions (1.14.1, 0.30.4) were published with an injected dependency that pulled payloads from attacker C2. Microsoft attributed it to the North Korean actor Sapphire Sleet. CISA issued an alert.
- **Source:** [Microsoft Security / CISA](https://www.cisa.gov/news-events/alerts/2026/04/20/supply-chain-compromise-impacts-axios-node-package-manager)

### First large-scale indirect prompt injection attacks observed in the wild · `1.5`
- **Track:** security / AI Security
- **Takeaway:** Adversaries embed hidden instructions inside content an LLM later retrieves (web pages, documents, ad copy) rather than in the user's direct prompt. Unit 42 documented the first large-scale, real-world cases, including ad-review evasion…
- **Source:** [Palo Alto Networks Unit 42](https://unit42.paloaltonetworks.com/monitoring-npm-supply-chain-attacks/)

### Qualcomm zero-day (CVE-2026-21385) in March 2026 Android update · `1.5`
- **Track:** security / Mobile Security
- **Takeaway:** The March 2026 Android security bulletin patched 129 vulnerabilities including a Qualcomm zero-day (CVE-2026-21385) reported as affecting a large number of chipset models, exploitable in the wild.
- **Source:** [Android Security Bulletin (via Vervali analysis)](https://www.vervali.com/blog/android-malware-statistics-2026-threat-landscape-ios-comparison-and-detection-trends/)

### 50+ mobile apps ship hardcoded AWS credentials · `0.9`
- **Track:** security / Mobile Security
- **Takeaway:** More than 50 apps were found with hardcoded AWS credentials in their binaries, giving attackers a direct path to production databases, customer data, and in some cases root-level cloud control.
- **Source:** [Quokka (State of Mobile App Security 2026)](https://www.quokka.io/blog/the-state-of-mobile-app-security-2026-report-findings)

### AI-authored code is a leading source of new web-app vulnerabilities · `0.9`
- **Track:** security / Web Application Security
- **Takeaway:** With 90%+ of organizations using AI coding assistants, AI-generated code has become a top AppSec blind spot, frequently introducing injection, auth, and secrets-handling flaws that ship faster than review can catch.
- **Source:** [Cycode](https://cycode.com/blog/application-security-vulnerabilities/)

### Hardcoded cryptographic keys in 47.8% of Android and 17.6% of iOS apps · `0.9`
- **Track:** security / Mobile Security
- **Takeaway:** Quokka's analysis of 150k+ apps found cryptographic keys embedded directly in app binaries. Because every install ships the same key, extraction via trivial decompilation compromises all users' protected data retroactively.
- **Source:** [Quokka (State of Mobile App Security 2026)](https://www.quokka.io/blog/the-state-of-mobile-app-security-2026-report-findings)

### MCP tool poisoning attacks (TPAs) via hidden tool-description metadata · `0.9`
- **Track:** security / AI Security
- **Takeaway:** Malicious instructions hidden in Model Context Protocol tool descriptions (metadata read by the model but not shown to users) coerce agents into leaking data or invoking dangerous tools. Studies found a large share of MCP servers also…
- **Source:** [Checkmarx Zero](https://checkmarx.com/zero-post/11-emerging-ai-security-risks-with-mcp-model-context-protocol/)

### RAG poisoning via injected malicious documents in the retrieval corpus · `0.9`
- **Track:** security / AI Security
- **Takeaway:** Adversaries plant malicious documents in the retrieval corpus so the model surfaces and acts on attacker-controlled content, enabling misinformation, data exfiltration prompts, or indirect injection at query time.
- **Source:** [OWASP GenAI / TokenMix analysis](https://tokenmix.ai/blog/llm-security-news-2026-attacks-defenses-updates)

### Shipped apps carry years-old Critical CVEs in bundled components · `0.9`
- **Track:** security / Mobile Security
- **Takeaway:** Quokka found Android apps shipping Critical CVEs spanning nearly a decade of unpatched components, and 2,075 iOS apps containing a Critical CVE first disclosed in 2023 — outdated bundled SDKs/libraries remain a major exposure.
- **Source:** [Quokka (State of Mobile App Security 2026)](https://www.quokka.io/blog/the-state-of-mobile-app-security-2026-report-findings)

### CL.0 and browser-powered desync request smuggling · `0.3`
- **Track:** security / Web Application Security
- **Takeaway:** PortSwigger research on browser-powered desync and CL.0 shows back-end servers can be made to ignore Content-Length, enabling request smuggling without chunked encoding or HTTP/2 downgrade, leading to request hijacking and cache poisoning.
- **Source:** [PortSwigger Research](https://portswigger.net/research/browser-powered-desync-attacks)

### WAFFLED: parsing discrepancies bypass web application firewalls · `0.3`
- **Track:** security / Web Application Security
- **Takeaway:** Academic work shows attackers exploit differences in how WAFs and back-ends parse requests (encodings, multipart, content types) to slip malicious payloads past the WAF that the application still processes.
- **Source:** [arXiv (WAFFLED)](https://arxiv.org/pdf/2503.10846)

### Image-based prompt injection hijacks multimodal LLMs · `0.3`
- **Track:** security / AI Security
- **Takeaway:** Adversarial instructions are visually embedded in images (including steganographic or low-contrast text and QR codes) and interpreted as commands by multimodal models, hijacking behavior without any malicious text in the prompt.
- **Source:** [Cloud Security Alliance (CSA) Labs](https://labs.cloudsecurityalliance.org/research/csa-research-note-image-prompt-injection-multimodal-llm-2026/)

### System-prompt extraction remains broadly effective · `0.3`
- **Track:** security / AI Security
- **Takeaway:** Multi-step prompting that exploits a model's tendency to summarize or restate its own instructions reliably extracts hidden system prompts, exposing guardrails, secrets, and business logic.
- **Source:** [TokenMix LLM Security News](https://tokenmix.ai/blog/llm-security-news-2026-attacks-defenses-updates)

### LANDFALL spyware exploited Samsung zero-day (CVE-2025-21042) · `0.0`
- **Track:** security / Mobile Security
- **Takeaway:** Commercial-grade Android spyware exploited a zero-day in a Samsung image-processing library (CVE-2025-21042) via malicious DNG image files delivered over WhatsApp, achieving remote code execution with little/no user interaction;…
- **Source:** [Palo Alto Networks Unit 42](https://unit42.paloaltonetworks.com/landfall-is-new-commercial-grade-android-spyware/)

### New OWASP category: Software Supply Chain Failures (A03) · `0.0`
- **Track:** security / Web Application Security
- **Takeaway:** OWASP added a dedicated Software Supply Chain Failures category, recognizing dependency, build-pipeline, and artifact-integrity risks as a top web-app risk class distinct from generic vulnerable components.
- **Source:** [OWASP Foundation](https://owasp.org/www-project-top-ten/)

### OWASP Top 10:2025 — Broken Access Control (#1) now subsumes SSRF · `0.0`
- **Track:** security / Web Application Security
- **Takeaway:** The 2025 Top 10 (based on 175k+ vulnerabilities) keeps Broken Access Control at #1 and folds in Server-Side Request Forgery, reflecting how missing authorization and SSRF let attackers reach internal services and data.
- **Source:** [OWASP Foundation](https://owasp.org/www-project-top-ten/)


---

<sub>Generated by scripts/generate_skills.py on 2026-07-13.</sub>
