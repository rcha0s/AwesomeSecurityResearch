# Google brings Rust (memory safety) to the Pixel baseband

**Track:** Security  ·  **Domain:** Mobile Security  ·  **Subtype:** Platform / OS  
**Source:** [Google Online Security Blog](http://security.googleblog.com/2026/04/bringing-rust-to-pixel-baseband.html)  ·  **Disclosed:** Apr 2026  ·  **Retrieved:** 2026-07-13  
**Scores:** 🆕 Newness 10 · ✨ Novelty 66 · 🎯 Relevance 74 · **Composite 52.0**  
**Tags:** `rust`, `memory-safety`, `baseband`, `android`, `platform-security`

> **Takeaway —** Memory-safe languages are reaching the lowest, most security-critical layers — the baseband — meaningfully shrinking remote attack surface.

## Summary

Google is rewriting parts of the Pixel cellular baseband in Rust, bringing memory safety to one of the most attractive and hard-to-reach remote attack surfaces on a phone.

## What to learn

- Rewriting high-risk parsers in Rust removes whole classes of memory-corruption bugs at the baseband — _"Bringing Rust to the Pixel Baseband"_

## Actionable leverage

**[takeaway]** Favor memory-safe rewrites for remote parsers — Target memory-unsafe code on remotely-reachable attack surfaces first when planning Rust migrations.

---

_Source: [http://security.googleblog.com/2026/04/bringing-rust-to-pixel-baseband.html](http://security.googleblog.com/2026/04/bringing-rust-to-pixel-baseband.html)_  ·  [← back to index](../README.md)
