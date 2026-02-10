# 09-reports — Report Generation & Output Tiers (v0.8.x)

> **Purpose**: Rich, formatted reports at all 4 output tiers in all supported formats

This phase implements report rendering across 4 tiers (Pass/Fail, Diagnostic, Playbook, Audience-Adapted) and 5 formats (JSON, YAML, Markdown, HTML, Terminal), plus report metadata for audit trails.

---

## 📚 Primary Reference

- [RR-ROADMAP (v0.8.x section)](../RR-ROADMAP-validator-v0.0.1-to-v1.0.0.md) — Version-level detail
- Specification: [RR-SPEC-v0.1.3-output-tier-specification.md](../02-foundation/RR-SPEC-v0.1.3-output-tier-specification.md)

## 🏗️ Roadmap Sub-Versions

| Version | Title                                | Deliverable                                                                         |
| ------- | ------------------------------------ | ----------------------------------------------------------------------------------- |
| v0.8.0  | Tier 1 & Tier 2 Output               | JSON/YAML pass/fail, terminal/Markdown/HTML diagnostic reports                      |
| v0.8.1  | Tier 3 Output (Remediation Playbook) | Markdown, JSON, and HTML playbook renderers                                         |
| v0.8.2  | Tier 4 Output (Audience-Adapted)     | Context profiles, comparative analysis, domain recommendations, maturity assessment |
| v0.8.3  | Report Metadata & Traceability       | Report ID, engine version, profile, timestamps on all output                        |

## 🔗 Dependencies

- **Depends on**: v0.7.x Ecosystem Integration
- **Depended on by**: v0.9.x Extended Validation & Polish

---

## 🗺️ Next Phase

→ [10-extended/](../10-extended/) — Extended Validation & Polish
