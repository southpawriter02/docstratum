# Pre-Pivot Design Specifications — Archive

> **Archived:** 2026-02-10
> **Reason:** Project pivot from portfolio proof-of-concept to validator product

## Context

These specifications were authored during the **pre-pivot** phase of the DocStratum project, when the roadmap described a portfolio-oriented proof-of-concept pipeline:

```
v0.2.x  Data Preparation (Source Audit → YAML Authoring → Validation Pipeline)
v0.3.x  Logic Core (Loader → Context Builder → Agents → A/B Harness)
v0.4.x  Demo Layer (Streamlit → Side-by-Side → Metrics → Neo4j)
v0.5.x  Testing & Validation (Behavioral Tests → Evidence Capture)
v0.6.x  Documentation & Release (README → Recording → Publication)
```

The **ecosystem pivot** (v0.0.7) redirected the project toward a validator product with a different phase structure:

```
v0.2.x  Parser — Markdown → Parsed Model
v0.3.x  Validation Engine — L0–L3 Checks
v0.4.x  Quality Scoring — 100-Point System
v0.5.x  CLI & Profiles
v0.6.x  Remediation Framework
v0.7.x  Ecosystem Integration
v0.8.x  Report Generation & Output Tiers
v0.9.x  Extended Validation & Polish
v1.0.0  General Availability
```

The post-pivot roadmap ([RR-ROADMAP-validator-v0.0.1-to-v1.0.0.md](../../RR-ROADMAP-validator-v0.0.1-to-v1.0.0.md)) is now the **authoritative source of truth** for version assignments and phase definitions.

## Contents

| Directory              | Original Phase          | Spec Count | Version Range    |
| ---------------------- | ----------------------- | ---------- | ---------------- |
| `03-data-preparation/` | Data Preparation        | 23 files   | v0.2.0 – v0.2.4e |
| `04-logic-core/`       | Logic Core              | 29 files   | v0.3.0 – v0.3.5d |
| `05-demo-layer/`       | Demo Layer              | 23 files   | v0.4.0 – v0.4.4d |
| `06-testing/`          | Testing & Validation    | 5 files    | v0.5.0 – v0.5.3  |
| `07-release/`          | Documentation & Release | 7 files    | v0.6.0 – v0.6.5  |

## Status

These specifications are **preserved but inactive**. They represent substantial research and design work that may be valuable for future product extensions (the roadmap references "future product extensions" for FR-009 through FR-066). They are not part of the active development plan.
