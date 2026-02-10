# 08-ecosystem — Ecosystem Integration (v0.7.x)

> **Purpose**: Multi-file validation via the ecosystem pipeline

This phase wires the single-file validator into the existing ecosystem pipeline (built in v0.1.4) for cross-file analysis, activates the 3 reserved ecosystem health dimensions, and calibrates scoring against synthetic specimens.

---

## 📚 Primary Reference

- [RR-ROADMAP (v0.7.x section)](../RR-ROADMAP-validator-v0.0.1-to-v1.0.0.md) — Version-level detail
- Specification: [RR-SPEC-v0.1.3-ecosystem-scoring-calibration.md](../02-foundation/RR-SPEC-v0.1.3-ecosystem-scoring-calibration.md)

## 🏗️ Roadmap Sub-Versions

| Version | Title                           | Deliverable                                                                 |
| ------- | ------------------------------- | --------------------------------------------------------------------------- |
| v0.7.0  | SingleFileValidator Integration | Validator adapter, per-file result storage, end-to-end pipeline test        |
| v0.7.1  | Ecosystem Scoring Enhancement   | Consistency, Token Efficiency, Freshness dimensions + 5-dimension composite |
| v0.7.2  | Ecosystem Calibration           | Specimen scoring, sensitivity verification, CLI ecosystem mode              |

## 🔗 Dependencies

- **Depends on**: v0.6.x Remediation, v0.1.4 Ecosystem Pipeline Infrastructure
- **Depended on by**: v0.8.x Report Generation

---

## 🗺️ Next Phase

→ [09-reports/](../09-reports/) — Report Generation & Output Tiers
