# 07-remediation — Remediation Framework (v0.6.x)

> **Purpose**: Actionable, prioritized remediation guidance

This phase transforms raw diagnostics into a sequenced "playbook" — not just "what's wrong" but "what to do, in what order, and why." It implements impact-based priority assignment, same-code consolidation, effort estimation, and YAML-stored remediation templates.

---

## 📚 Primary Reference

- [RR-ROADMAP (v0.6.x section)](../RR-ROADMAP-validator-v0.0.1-to-v1.0.0.md) — Version-level detail
- Specification: [RR-SPEC-v0.1.3-remediation-framework.md](../02-foundation/RR-SPEC-v0.1.3-remediation-framework.md)

## 🏗️ Roadmap Sub-Versions

| Version | Title                         | Deliverable                                                                            |
| ------- | ----------------------------- | -------------------------------------------------------------------------------------- |
| v0.6.0  | Priority Model                | Impact-based priority assignment for all 38 diagnostic codes                           |
| v0.6.1  | Grouping & Effort Estimation  | Same-code consolidation, anti-pattern aggregation, effort estimation, score projection |
| v0.6.2  | Remediation Templates         | YAML templates for all error, warning, and info codes                                  |
| v0.6.3  | Dependency Graph & Sequencing | Prerequisite ordering, topological sort, playbook assembly                             |

## 🔗 Dependencies

- **Depends on**: v0.5.x CLI & Profiles
- **Depended on by**: v0.7.x Ecosystem Integration

---

## 🗺️ Next Phase

→ [08-ecosystem/](../08-ecosystem/) — Ecosystem Integration
