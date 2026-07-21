# ShadowPickle: pickle-VM import tricks evade ten model scanners and four model hubs

**Topic:** AI Security  ·  **Domain:** Model Supply Chain  
**Source:** [source](https://arxiv.org/abs/2607.17503)  ·  **Author:** Pradhan, Nambiar, Soremekun  ·  **Published:** Jul 20, 2026  ·  **Retrieved:** 2026-07-21  
**Scores:** 🆕 Newness 32 · ✨ Novelty 68 · 🎯 Relevance 84 · 🏛️ Credibility 58 · **Composite 62.22**  
**Tags:** `model-supply-chain`, `pickle`, `deserialization`, `scanner-evasion`, `huggingface`  
**Verification:** ✓ independently verified · closest prior art: Malicious pickles in ML model hubs are a well-established attack class (pickle RCE documented since at least 2022, incl. Rehberger's ML Attack Series). The delta is the specific external-module-import evasion primitive plus a measured evasion rate across ten scanners and an injectable benchmark, rather than a new concept.

> **Takeaway —** A clean model-scanner result is weak evidence - prefer non-executable formats and sandbox deserialization of any third-party model.

## TL;DR

_The gist, not every detail — read the [full source](https://arxiv.org/abs/2607.17503) for the complete write-up._

ShadowPickle presents three stealthy pickle-deserialization attacks that abuse the Pickle VM's external module import mechanism to execute payloads at load time while evading scanners. The reported evaluation evades ten state-of-the-art scanners and four model hubs, with the 'Overwritten' variant reaching a 63% evasion rate.

## What to learn

- The pickle VM's external module import mechanism is the bypass primitive; evading ten scanners and four hubs is consistent with - though the abstract does not itself argue - hub scanning being weak evidence of artifact safety. — _"These attacks leverage the external module import mechanism of the Pickle Virtual Machine (VM) to execute malicious payloads during deserialization."_ ✅
- Evasion is measured, not asserted: the 'Overwritten' variant reports a 63% aggregate evasion rate across the scanner suite (the abstract gives no per-scanner breakdown), so treat scanner coverage as probabilistic, not a gate. — _"SHADOWPICKLE (Overwritten) has a 63% evasion rate across scanners, and up to 50% higher evasion rates than existing attacks."_ ✅
- The authors describe PickleBench, a harness that injects these attacks into arbitrary benign models; the abstract does not state whether it is publicly released. — _"we provide PICKLEBENCH, a dynamic and extensible benchmark for automatically injecting SHADOWPICKLE into arbitrary benign PTM models"_ ✅

## Threat · Conditions · Mitigations

- **Threat —** An attacker publishes a pre-trained model to a hub whose pickle payload executes on deserialization in the consumer's environment while passing hub and third-party scanners.
- **Conditions —** Any pipeline that loads pickle-format pre-trained models from a hub and treats a scanner verdict as sufficient assurance.
- **Mitigations —** The abstract says the authors give security recommendations but does not enumerate them. Independent of the paper, standard practice applies: prefer non-executable formats such as safetensors and deserialize untrusted models only in a sandbox.

## Actionable leverage

**[tool]** Regression-test your model scanner with PickleBench — If PickleBench is released, run your model-scanning gate against injected variants of your own known-good models to measure real evasion rate before relying on it in CI. Independent of the paper: where the format allows, migrate ingestion to safetensors and make pickle loading an explicitly sandboxed, opt-in path.

---

_Source: [https://arxiv.org/abs/2607.17503](https://arxiv.org/abs/2607.17503)_  ·  [← back to index](../README.md)
