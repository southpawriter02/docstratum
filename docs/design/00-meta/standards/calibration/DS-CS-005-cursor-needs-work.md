# DS-CS-005: Cursor — Needs Work

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-CS-005 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Project** | Cursor |
| **Expected Total Score** | 42 |
| **Expected Grade** | Needs Work (30–49) |
| **Source URL** | https://cursor.com/llms.txt |
| **Captured Date** | 2026-02-06 (v0.0.4b calibration) |
| **Provenance** | v0.0.4b §11.3 Gold Standard Calibration; v0.0.2c specimen analysis |

## Description

Cursor's llms.txt scores 42 points, firmly placing it in the **Needs Work tier**. The file is structurally parseable and technically valid, but exhibits significant content gaps that prevent it from reaching higher grades: sparse descriptions, minimal code examples, and some structural anti-patterns are evident. It represents a common "minimum viable" llms.txt implementation — technically compliant but lacking the depth and organization expected of Strong or Exemplary files. This specimen is essential for validating that the scoring pipeline correctly identifies files requiring improvement.

## Expected Per-Dimension Scores

| Dimension | Expected Points | Max Points | Percentage |
|-----------|----------------|------------|------------|
| Structural | ~15 | 30 | ~50% |
| Content | ~20 | 50 | ~40% |
| Anti-Pattern | ~7 | 20 | ~35% |
| **Total** | **~42** | **100** | **42%** |

## Per-Criterion Pass/Fail Expectations

### L0 Parseable Prerequisites

> **Note:** L0 criteria files will be defined in Phase C. All calibration specimens are expected to pass L0 — files that cannot be parsed are not published. Cursor passes all five L0 checks (valid UTF-8, non-empty, valid Markdown, proper token range, LF endings).

### Structural Criteria

| DS Identifier | Expected Result | Notes |
|---------------|----------------|-------|
| DS-VC-STR-001 | PASS | H1 "Cursor" present |
| DS-VC-STR-002 | PASS | Only one H1 (no duplicates) |
| DS-VC-STR-003 | FAIL | Blockquote missing or minimal |
| DS-VC-STR-004 | SOFT FAIL | Some sections missing H2 headers |
| DS-VC-STR-005 | SOFT FAIL | Some links lack proper Markdown formatting |
| DS-VC-STR-006 | SOFT FAIL | Minor heading violations |
| DS-VC-STR-007 | FAIL | Sections do not follow canonical ordering |
| DS-VC-STR-008 | SOFT FAIL | Minor structural anti-patterns present |
| DS-VC-STR-009 | SOFT FAIL | Possible anti-pattern hints detected |

### Content Criteria

| DS Identifier | Expected Result | Notes |
|---------------|----------------|-------|
| DS-VC-CON-001 | SOFT FAIL | Some links lack meaningful descriptions |
| DS-VC-CON-002 | SOFT FAIL | Some URLs may not resolve |
| DS-VC-CON-003 | SOFT FAIL | Placeholder content present |
| DS-VC-CON-004 | FAIL | Some sections have sparse content |
| DS-VC-CON-005 | PASS | No duplicate section names |
| DS-VC-CON-006 | FAIL | Blockquote is minimal or missing |
| DS-VC-CON-007 | FAIL | Many descriptions are formulaic |
| DS-VC-CON-008 | FAIL | Section names are non-canonical |
| DS-VC-CON-009 | SOFT FAIL | Master Index may be missing or incomplete |
| DS-VC-CON-010 | FAIL | Few or no code examples |
| DS-VC-CON-011 | SOFT FAIL | Code blocks lack language specifiers |
| DS-VC-CON-012 | PASS | Within token budget tier |
| DS-VC-CON-013 | FAIL | No version metadata |

### Anti-Pattern Detection Criteria

| DS Identifier | Expected Result | Notes |
|---------------|----------------|-------|
| DS-VC-APD-001 | FAIL (INFO) | No LLM Instructions section (0% ecosystem adoption) |
| DS-VC-APD-002 | FAIL (INFO) | No structured concept definitions |
| DS-VC-APD-003 | FAIL (INFO) | No few-shot examples |
| DS-VC-APD-004 | SOFT FAIL | Minor content anti-patterns present |
| DS-VC-APD-005 | SOFT FAIL | Minor strategic anti-patterns possible |
| DS-VC-APD-006 | FAIL | Unbalanced or sparse token distribution |
| DS-VC-APD-007 | SOFT FAIL | Mix of absolute and relative URLs |
| DS-VC-APD-008 | FAIL | Jargon used without definition |

## Self-Test Usage

When the pipeline runs its calibration self-test (Stage 3 of the self-validation loop), it processes Cursor's llms.txt and compares:

1. `|actual_total - 42| <= tolerance` (default tolerance: ±3 points)
2. `actual_grade == QualityGrade.NEEDS_WORK`
3. Expected anti-patterns are detected

If any comparison fails, the pipeline reports a calibration drift warning. Cursor serves as a mid-range validator, confirming that files with significant content gaps land in Needs Work, not higher grades.

## Staleness Risk

Cursor's llms.txt is actively maintained and likely to change as the tool evolves. The file may improve in future versions as the project matures. Re-validation should occur quarterly or when a calibration self-test fails. High risk of score drift due to expected improvements and active development.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.7 |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
