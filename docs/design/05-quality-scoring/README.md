# 05-quality-scoring — Quality Scoring (v0.4.x)

> **Purpose**: 100-point composite quality scoring engine

This phase implements the 3-dimension quality scoring pipeline (Structural 30%, Content 50%, Anti-Pattern 20%) that converts validation diagnostics into a numeric score (0–100), a letter grade (EXEMPLARY → CRITICAL), and per-dimension breakdown.

---

## 📚 Primary Reference

- [RR-SCOPE-v0.4.x-quality-scoring.md](RR-SCOPE-v0.4.x-quality-scoring.md) — Full scope breakdown
- [RR-ROADMAP (v0.4.x section)](../RR-ROADMAP-validator-v0.0.1-to-v1.0.0.md) — Version-level detail

## 🏗️ Roadmap Sub-Versions

| Version | Title                       | Deliverable                                                  |
| ------- | --------------------------- | ------------------------------------------------------------ |
| v0.4.0  | Dimension Scoring           | Structural, Content, and Anti-Pattern dimension calculations |
| v0.4.1  | Composite Scoring & Grading | Composite 0–100 score, grade assignment, per-check detail    |
| v0.4.2  | Scoring Calibration         | 6 gold standard specimens validated within ±3 points         |

## 🔗 Dependencies

- **Depends on**: v0.3.x Validation Engine (requires `ValidationResult` with diagnostics)
- **Depended on by**: v0.5.x CLI & Profiles (requires `QualityScore`)

---

## 🗺️ Next Phase

→ [06-cli-and-profiles/](../06-cli-and-profiles/) — CLI & Validation Profiles
