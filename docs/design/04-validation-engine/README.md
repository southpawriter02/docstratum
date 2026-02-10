# 04-validation-engine — Validation Engine (v0.3.x)

> **Purpose**: L0–L3 single-file validation with diagnostic emission

This phase implements the 4-level validation pipeline that checks `llms.txt` files for structural correctness, content quality, best practices adherence, and anti-pattern absence. It produces a `ValidationResult` with diagnostics, severity levels, and line-number references.

---

## 📚 Primary Reference

- [RR-SCOPE-v0.3.x-validation-engine.md](RR-SCOPE-v0.3.x-validation-engine.md) — Full scope breakdown
- [RR-ROADMAP (v0.3.x section)](../RR-ROADMAP-validator-v0.0.1-to-v1.0.0.md) — Version-level detail

## 🏗️ Roadmap Sub-Versions

| Version | Title                           | Deliverable                                                              |
| ------- | ------------------------------- | ------------------------------------------------------------------------ |
| v0.3.0  | L0 Validation (Parseable Gate)  | Encoding, line endings, Markdown parse, empty file, size limit           |
| v0.3.1  | L1 Validation (Structural)      | H1 title, blockquote, section structure, link format                     |
| v0.3.2  | L2 Validation (Content Quality) | Description quality, URL validation, section content, blockquote quality |
| v0.3.3  | L3 Validation (Best Practices)  | Canonical sections, master index, code examples, token budget, ordering  |
| v0.3.4  | Anti-Pattern Detection          | 22 single-file anti-patterns across 4 severity categories                |
| v0.3.5  | Pipeline Assembly               | Level sequencing, diagnostic aggregation, unit tests, calibration        |

## 🔗 Dependencies

- **Depends on**: v0.2.x Parser (requires `ParsedLlmsTxt`)
- **Depended on by**: v0.4.x Quality Scoring (requires `ValidationResult`)

---

## 🗺️ Next Phase

→ [05-quality-scoring/](../05-quality-scoring/) — 100-Point Quality Scoring System
