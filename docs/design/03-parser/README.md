# 03-parser — Parser (v0.2.x)

> **Purpose**: Markdown → Parsed Model

This phase implements the parser that reads raw `llms.txt` Markdown files and populates the Pydantic schema models defined in v0.1.x. It handles file I/O, tokenization, document type classification, metadata extraction, and parser testing/calibration.

---

## 📚 Primary Reference

- [RR-SCOPE-v0.2.x-parser.md](RR-SCOPE-v0.2.x-parser.md) — Full scope breakdown
- [RR-ROADMAP (v0.2.x section)](../RR-ROADMAP-validator-v0.0.1-to-v1.0.0.md) — Version-level detail

## 🏗️ Roadmap Sub-Versions

| Version | Title                        | Deliverable                                                                                            |
| ------- | ---------------------------- | ------------------------------------------------------------------------------------------------------ |
| v0.2.0  | Core Parser                  | Markdown → `ParsedLlmsTxt` with section splitting, link extraction, round-trip serialization           |
| v0.2.1  | Classification & Metadata    | Document type classification, size tier assignment, canonical section matching, metadata extraction    |
| v0.2.2  | Parser Testing & Calibration | Synthetic fixtures, real-world specimen parsing, edge case coverage, `SingleFileValidator` integration |

## 🔗 Dependencies

- **Depends on**: v0.1.x Foundation (schema models, pipeline infrastructure)
- **Depended on by**: v0.3.x Validation Engine (requires `ParsedLlmsTxt`)

---

## 🗺️ Next Phase

→ [04-validation-engine/](../04-validation-engine/) — L0–L3 Validation Checks
