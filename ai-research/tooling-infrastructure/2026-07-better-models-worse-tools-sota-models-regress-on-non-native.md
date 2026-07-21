# Better Models, Worse Tools: SOTA models regress on non-native tool schemas

**Topic:** AI Research  ·  **Domain:** Tooling & Infrastructure  
**Source:** [Simon Willison's Weblog](https://simonwillison.net/2026/Jul/4/better-models-worse-tools/#atom-everything)  ·  **Published:** Jul 4, 2026  ·  **Retrieved:** 2026-07-13  
**Scores:** 🆕 Newness 32 · ✨ Novelty 80 · 🎯 Relevance 90 · 🏛️ Credibility 55 · **Composite 67.25**  
**Tags:** `harness`, `tool-use`, `agents`, `claude-code`, `architecture`

> **Takeaway —** Newer ≠ better for YOUR tools: match your harness's tool schemas to what the target model was trained on.

## TL;DR

_The gist, not every detail — read the [full source](https://simonwillison.net/2026/Jul/4/better-models-worse-tools/#atom-everything) for the complete write-up._

Armin (building the Pi harness) found newer Claude models (Opus 4.8, Sonnet 5) invent made-up fields when calling Pi's custom edit tool — worse than older models — likely because they're RL-trained on Claude Code's built-in edit tool. Third-party harnesses with their own tool schemas get degraded tool-calling from the very newest models.

## What to learn

- A SOTA model can be WORSE at a custom tool schema than its older siblings if it was RL-trained on a different harness's tools — _"the SOTA models of the family are worse at this specific tool schema than their older siblings"_ ✅
- Align tool formats to the model — Claude is trained on str-replace edits, OpenAI on apply_patch — _"trained (presumably via Reinforcement Learning) to better use the edit tools that are baked into Claude Code"_ ✅

## Actionable leverage

**[harness]** Offer model-matched edit tools — In a multi-model harness, provide the edit-tool format each model was trained on (Claude str-replace, OpenAI apply_patch) instead of one custom schema, and validate/repair malformed tool calls.

---

_Source: [https://simonwillison.net/2026/Jul/4/better-models-worse-tools/#atom-everything](https://simonwillison.net/2026/Jul/4/better-models-worse-tools/#atom-everything)_  ·  [← back to index](../README.md)
