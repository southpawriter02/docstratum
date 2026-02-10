# 06-cli-and-profiles — CLI & Profiles (v0.5.x)

> **Purpose**: User-facing command-line interface and configurable validation profiles

This phase builds the CLI entry point (`docstratum validate`) and the profile system that governs which rules execute, what output format is produced, and how pass/fail thresholds are evaluated.

---

## 📚 Primary Reference

- [RR-SCOPE-v0.5.x-cli-and-profiles.md](RR-SCOPE-v0.5.x-cli-and-profiles.md) — Full scope breakdown
- [RR-ROADMAP (v0.5.x section)](../RR-ROADMAP-validator-v0.0.1-to-v1.0.0.md) — Version-level detail

## 🏗️ Roadmap Sub-Versions

| Version | Title                             | Deliverable                                                            |
| ------- | --------------------------------- | ---------------------------------------------------------------------- |
| v0.5.0  | CLI Foundation                    | Entry point, argument parsing, exit codes, terminal output             |
| v0.5.1  | Validation Profiles               | Profile model, 4 built-in profiles, tag-based filtering, inheritance   |
| v0.5.2  | Profile Discovery & Configuration | Profile loading, discovery precedence, CLI overrides, legacy migration |

## 🔗 Dependencies

- **Depends on**: v0.4.x Quality Scoring (requires `QualityScore`)
- **Depended on by**: v0.6.x Remediation Framework

---

## 🗺️ Next Phase

→ [07-remediation/](../07-remediation/) — Remediation Framework
