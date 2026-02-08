# DocStratum Authoritative Source of Truth (ASoT)

> **Version:** 0.0.0-scaffold
> **Status:** SCAFFOLDING (Phase A in progress)
> **Last Updated:** 2026-02-08
> **Governed By:** RR-META-asot-implementation-strategy.md

---

## Overview

This directory contains the **Authoritative Source of Truth** (ASoT) for the DocStratum validation engine — a modular, hierarchically organized standards library that defines every validation criterion, diagnostic code, anti-pattern, design decision, and scoring parameter that the engine enforces.

The ASoT is not a single document. It is a structured collection of **atomic standard files**, each defining one element of the validation standard. Files are organized into logical directories, referenced by stable DS-prefixed identifiers, and governed by a version-pinned manifest.

## Directory Structure

| Directory | Contents | Count | Description |
|-----------|----------|-------|-------------|
| [criteria/](criteria/) | Validation Criteria | 30 | The checks the pipeline runs (DS-VC-*) |
| [diagnostics/](diagnostics/) | Diagnostic Codes | 38 | Error/warning/info codes emitted by checks (DS-DC-*) |
| [levels/](levels/) | Validation Levels | 5 | The L0–L4 tier definitions (DS-VL-*) |
| [scoring/](scoring/) | Quality Scoring | 5 | Dimension weights, grade thresholds, gating rules (DS-QS-*) |
| [calibration/](calibration/) | Calibration Specimens | 6 | Gold-standard files with expected scores (DS-CS-*) |
| [decisions/](decisions/) | Design Decisions | 16 | Inherited constraints from research phase (DS-DD-*) |
| [anti-patterns/](anti-patterns/) | Anti-Pattern Registry | 28 | Named patterns that degrade quality (DS-AP-*) |
| [ecosystem/](ecosystem/) | Ecosystem Health | 5 | Cross-file quality dimensions (DS-EH-*) |
| [canonical/](canonical/) | Canonical Names | 11 | Standard section names with aliases (DS-CN-*) |

**Total:** 146 standard files + 20 README indexes = **166 files** at full population.

## Key Documents

- **[DS-MANIFEST.md](DS-MANIFEST.md)** — The keystone. Version-pinned registry of all standard elements, integrity assertions, provenance map, and change log. The validation pipeline reads this file at startup.
- **[../RR-META-asot-implementation-strategy.md](../RR-META-asot-implementation-strategy.md)** — The implementation plan governing how this library is built.

## Naming Convention

All standard files follow the pattern: `DS-{TypeCode}-{SubCategory}-{Sequence}-{slug}.md`

| Prefix | Type | Example |
|--------|------|---------|
| `DS-VC-` | Validation Criterion | `DS-VC-STR-001-h1-title-present.md` |
| `DS-DC-` | Diagnostic Code | `DS-DC-E001-NO_H1_TITLE.md` |
| `DS-VL-` | Validation Level | `DS-VL-L0-PARSEABLE.md` |
| `DS-DD-` | Design Decision | `DS-DD-014-content-quality-primary-weight.md` |
| `DS-AP-` | Anti-Pattern | `DS-AP-CRIT-001-ghost-file.md` |
| `DS-EH-` | Ecosystem Health | `DS-EH-COV-coverage.md` |
| `DS-QS-` | Quality Scoring | `DS-QS-DIM-STR-structural.md` |
| `DS-CS-` | Calibration Specimen | `DS-CS-001-svelte-exemplary.md` |
| `DS-CN-` | Canonical Name | `DS-CN-001-master-index.md` |

## Status Lifecycle

Every standard element has an explicit status:

- **DRAFT** — Authored but not yet ratified. Visible in the registry but not enforced by the pipeline.
- **RATIFIED** — Approved and enforced. Changes require a manifest version bump.
- **DEPRECATED** — No longer enforced. Remains in the tree for historical reference.

## Cross-Reference Convention

Files reference each other using **DS identifiers** (e.g., `DS-DC-E001`), not file paths. This decouples logical identity from physical location. The manifest serves as the authoritative resolver mapping identifiers to paths.

## How to Use This Library

**For developers implementing the validation pipeline:**
1. Read `DS-MANIFEST.md` to get the current ASoT version and file registry.
2. Verify integrity assertions before running validation.
3. Load individual standard files on demand as the pipeline needs them.
4. Stamp all validation results with the ASoT version.

**For contributors modifying the standard:**
1. Edit the relevant standard file.
2. Update the manifest version (MINOR for additions, MAJOR for removals/weight changes, PATCH for corrections).
3. Update the change log in both the file and the manifest.
4. Run integrity assertions to verify consistency.
