# DS-CS-006: NVIDIA — Critical

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-CS-006 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Project** | NVIDIA |
| **Expected Total Score** | 24 |
| **Expected Grade** | Critical (0–29) |
| **Source URL** | https://developer.nvidia.com/llms.txt |
| **Captured Date** | 2026-02-06 (v0.0.4b calibration) |
| **Provenance** | v0.0.4b §11.3 Gold Standard Calibration; v0.0.2c specimen analysis |

## Description

NVIDIA's llms.txt scores 24 points, placing it squarely in the **Critical tier** — the lowest quality category. Despite being from a major technology company, the file exhibits fundamental structural and content problems that severely limit its utility for LLM consumption. The file appears to be primarily a **Sitemap Dump anti-pattern** (AP-STRUCT-001): a flat list of links with minimal organization, sparse or boilerplate descriptions, and no meaningful content aggregation. This specimen is essential for validating that the pipeline has sufficient discriminating power at the low end and correctly identifies fundamentally inadequate files.

## Expected Per-Dimension Scores

| Dimension | Expected Points | Max Points | Percentage |
|-----------|----------------|------------|------------|
| Structural | ~10 | 30 | ~33% |
| Content | ~10 | 50 | ~20% |
| Anti-Pattern | ~4 | 20 | ~20% |
| **Total** | **~24** | **100** | **24%** |

## Per-Criterion Pass/Fail Expectations

### L0 Parseable Prerequisites

> **Note:** L0 criteria files will be defined in Phase C. All calibration specimens are expected to pass L0 — files that cannot be parsed are not published. NVIDIA passes all five L0 checks (valid UTF-8, non-empty, valid Markdown, proper token range, LF endings), despite low overall quality.

### Structural Criteria

| DS Identifier | Expected Result | Notes |
|---------------|----------------|-------|
| DS-VC-STR-001 | PASS | H1 "NVIDIA" or similar present |
| DS-VC-STR-002 | SOFT FAIL | Multiple H1s or inconsistent heading structure |
| DS-VC-STR-003 | FAIL | Blockquote missing or inadequate |
| DS-VC-STR-004 | FAIL | Most sections lack H2 headers |
| DS-VC-STR-005 | FAIL | Many links use improper formatting |
| DS-VC-STR-006 | FAIL | Significant heading violations |
| DS-VC-STR-007 | FAIL | No canonical section ordering |
| DS-VC-STR-008 | FAIL | Critical anti-patterns detected |
| DS-VC-STR-009 | FAIL | Structural anti-patterns evident (Sitemap Dump) |

### Content Criteria

| DS Identifier | Expected Result | Notes |
|---------------|----------------|-------|
| DS-VC-CON-001 | FAIL | Most links have no descriptions or boilerplate only |
| DS-VC-CON-002 | FAIL | Many URLs may not resolve or are outdated |
| DS-VC-CON-003 | FAIL | Extensive placeholder or generic content |
| DS-VC-CON-004 | FAIL | Many sections lack substantive content |
| DS-VC-CON-005 | SOFT FAIL | Possible duplicate section names |
| DS-VC-CON-006 | FAIL | Blockquote missing or non-substantive |
| DS-VC-CON-007 | FAIL | Descriptions are entirely formulaic |
| DS-VC-CON-008 | FAIL | Section names are non-canonical and inconsistent |
| DS-VC-CON-009 | FAIL | No Master Index or severely incomplete |
| DS-VC-CON-010 | FAIL | No code examples |
| DS-VC-CON-011 | FAIL | No code blocks or improperly formatted |
| DS-VC-CON-012 | FAIL | Severely over or under token budget |
| DS-VC-CON-013 | FAIL | No version metadata |

### Anti-Pattern Detection Criteria

| DS Identifier | Expected Result | Notes |
|---------------|----------------|-------|
| DS-VC-APD-001 | FAIL (INFO) | No LLM Instructions section (0% ecosystem adoption) |
| DS-VC-APD-002 | FAIL (INFO) | No structured concept definitions |
| DS-VC-APD-003 | FAIL (INFO) | No few-shot examples |
| DS-VC-APD-004 | FAIL | Multiple content anti-patterns detected |
| DS-VC-APD-005 | FAIL | Critical strategic anti-patterns present |
| DS-VC-APD-006 | FAIL | Highly unbalanced token distribution (monolith) |
| DS-VC-APD-007 | FAIL | Predominantly relative or broken URLs |
| DS-VC-APD-008 | FAIL | Extensive unexplained jargon |

## Self-Test Usage

When the pipeline runs its calibration self-test (Stage 3 of the self-validation loop), it processes NVIDIA's llms.txt and compares:

1. `|actual_total - 24| <= tolerance` (default tolerance: ±3 points)
2. `actual_grade == QualityGrade.CRITICAL`
3. Critical anti-patterns are reliably detected

If any comparison fails, the pipeline reports a calibration drift warning. NVIDIA serves as the floor validator, confirming that fundamentally inadequate files are correctly identified and that the pipeline has discriminating power across the entire scoring spectrum.

## Staleness Risk

NVIDIA's llms.txt represents a snapshot of a low-quality implementation. If the company significantly redesigns the file, it may improve substantially. However, as of the capture date, it exemplifies common problems with auto-generated or unmaintained files. Re-validation should occur quarterly or when a calibration self-test fails. High risk of change due to potential future improvements or deprecation.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.7 |
