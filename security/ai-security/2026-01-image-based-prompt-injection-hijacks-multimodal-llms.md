# Image-based prompt injection hijacks multimodal LLMs

**Track:** Security  ·  **Domain:** AI Security  ·  **Subtype:** Prompt Injection  
**Source:** [Cloud Security Alliance (CSA) Labs](https://labs.cloudsecurityalliance.org/research/csa-research-note-image-prompt-injection-multimodal-llm-2026/)  ·  **Disclosed:** Jan 2026  
**Scores:** 🆕 Newness 1 · ✨ Novelty 0 · 🎯 Relevance 0 · **Composite 0.3**

## Threat · Conditions · Mitigations

- **Threat —** Adversarial instructions are visually embedded in images (including steganographic or low-contrast text and QR codes) and interpreted as commands by multimodal models, hijacking behavior without any malicious text in the prompt.
- **Conditions —** Applies to multimodal LLMs that accept user- or web-supplied images, especially in agentic pipelines that screenshot pages or process uploaded media.
- **Mitigations —** Sanitize/normalize images before model ingestion; separate visual content from instruction channels; OCR-and-scan images for embedded instructions; restrict actions the model can take from image-derived content.

---

_Source: [https://labs.cloudsecurityalliance.org/research/csa-research-note-image-prompt-injection-multimodal-llm-2026/](https://labs.cloudsecurityalliance.org/research/csa-research-note-image-prompt-injection-multimodal-llm-2026/)_  ·  [← back to index](../README.md)
