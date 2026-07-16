# Product Security

> Securing products: application security, supply chain, cloud & infra, identity, mobile, plus red teaming and threat modeling (AI-assisted or not).

_4 vetted findings · updated 2026-07-16 · ranked by composite · latest 31 days only · [1 held for review](../REVIEW.md)._

| Domain | Findings |
| --- | --- |
| Supply Chain & Dependencies | 1 |
| Supply Chain | 1 |
| Malware & Wipers | 1 |
| Application Security | 1 |

## Supply Chain & Dependencies

- **[AsyncAPI npm compromise: import-time payload defeats --ignore-scripts](supply-chain-dependencies/2026-07-asyncapi-npm-compromise-import-time-payload-defeats-ignore-s.md)** · composite **74.88** · Jul 16, 2026 · 🔗 +2 sources  
  Import-time malware makes --ignore-scripts useless and a valid provenance attestation is not a trust signal when the pipeline itself is hijacked.  
  _[source](https://www.microsoft.com/en-us/security/blog/2026/07/15/unpacking-asyncapi-npm-supply-chain-compromise-import-time-payload-delivery/)_

## Supply Chain

- **[Phantom Squatting: attackers register the domains LLMs hallucinate](supply-chain/2026-07-phantom-squatting-attackers-register-the-domains-llms-halluc.md)** · composite **71.05** · Jun 30, 2026  
  LLM hallucinations are a predictable supply-chain attack surface: attackers pre-register the domains/packages models invent.  
  _[Palo Alto Networks Unit 42](https://unit42.paloaltonetworks.com/phantom-squatting-hallucinated-web-domains/)_

## Malware & Wipers

- **[GigaWiper: modular destructive malware that fakes ransomware](malware-wipers/2026-07-gigawiper-modular-destructive-malware-that-fakes-ransomware.md)** · composite **64.0** · Jul 9, 2026  
  Wiper malware is consolidating into modular platforms, and 'ransomware' may be undecryptable destruction in disguise — plan recovery accordingly.  
  _[Microsoft Security Blog](https://www.microsoft.com/en-us/security/blog/2026/07/09/gigawiper-anatomy-of-a-destructive-backdoor-assembled-from-multiple-malware/)_

## Application Security

- **[Kemp LoadMaster pre-auth RCE: uninitialized heap + missing null byte (CVE-2026-8037)](application-security/2026-06-kemp-loadmaster-pre-auth-rce-uninitialized-heap-missing-null.md)** · composite **58.85** · Jun 29, 2026  
  A minimal 'just null-terminate the buffer' patch can hide a pre-auth RCE — diff patches carefully, and treat missing null-termination next to attacker-controlled heap data as exploitable, not…  
  _[source](https://labs.watchtowr.com/enterprise-tech-in-shell-out-progress-kemp-loadmaster-uninitialized-heap-to-pre-auth-rce-cve-2026-8037/)_

---

[← Home](../README.md) · [Newsletter](../NEWSLETTER.md) · [Trends](../TRENDS.md) · [Review queue](../REVIEW.md) · [Learnings](../LEARNINGS.md)
