# Phantom Squatting: attackers register the domains LLMs hallucinate

**Topic:** Product Security  ·  **Domain:** Supply Chain  
**Source:** [Palo Alto Networks Unit 42](https://unit42.paloaltonetworks.com/phantom-squatting-hallucinated-web-domains/)  ·  **Published:** Jun 30, 2026  ·  **Retrieved:** 2026-07-13  
**Scores:** 🆕 Newness 43 · ✨ Novelty 90 · 🎯 Relevance 86 · 🏛️ Credibility 50 · **Composite 71.05**  
**Tags:** `supply-chain`, `slopsquatting`, `hallucination`, `phishing`, `unit42`

> **Takeaway —** LLM hallucinations are a predictable supply-chain attack surface: attackers pre-register the domains/packages models invent.

## TL;DR

_The gist, not every detail — read the [full source](https://unit42.paloaltonetworks.com/phantom-squatting-hallucinated-web-domains/) for the complete write-up._

Unit 42 documented 'phantom squatting': LLMs consistently hallucinate web domains for legitimate brands, and adversaries register those nonexistent domains to intercept AI-generated traffic. Across 913 brands and 685,339 queries they found 13,229 malicious URLs and ~250,000 still-unregistered hallucinated domains — and predicted adversary registrations 18–51 days ahead.

## What to learn

- Hallucinated domains/packages are predictable — defenders can enumerate and pre-register or block them before attackers do — _"predict use of these domains from 18-51 days ahead of adversary registration"_ ✅
- AI coding assistants are being used to build the phishing kits that then exploit hallucinated targets — _"an attacker who leveraged an AI coding assistant to build a full phishing kit named Montana Empire"_ ✅

## Actionable leverage

**[tool]** Enumerate & monitor your brand's hallucinated domains — Query LLMs for your brand's URLs/packages at scale, then pre-register or block-list the hallucinated ones and monitor for adversary registration.

---

_Source: [https://unit42.paloaltonetworks.com/phantom-squatting-hallucinated-web-domains/](https://unit42.paloaltonetworks.com/phantom-squatting-hallucinated-web-domains/)_  ·  [← back to index](../README.md)
