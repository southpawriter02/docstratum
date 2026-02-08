# DS-VC-CON-005: No Duplicate Sections

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VC-CON-005 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Platinum ID** | L2-05 |
| **Dimension** | Content (50%) |
| **Level** | L2 — Content Quality |
| **Weight** | 3 / 50 content points [CALIBRATION-NEEDED] |
| **Pass Type** | SOFT |
| **Measurability** | Fully measurable |
| **Provenance** | v0.0.4c AP-STRUCT-003 (Duplicate Identity); v0.0.2c audit data |

## Description

This criterion enforces that all H2 section names are unique. Duplicate section headings (even with trivial variations in capitalization) create ambiguity and disrupt the file's logical structure. They typically signal auto-generation errors or refactoring artifacts left behind during documentation maintenance.

Duplicate sections confuse readers navigating the table of contents and create problems for programmatic tools that rely on section names as identifiers. The criterion uses case-insensitive comparison to catch near-duplicates like "API Reference" and "api reference."

This is a fully measurable criterion requiring only string comparison.

## Pass Condition

All H2 heading texts are unique in a case-insensitive comparison:

```python
h2_headings = extract_all_h2_headings(content)
h2_names = [h.text.strip().lower() for h in h2_headings]
assert len(h2_names) == len(set(h2_names))
```

Each H2 text, when lowercased and trimmed, must appear exactly once in the file.

## Fail Condition

Two or more H2 headings have identical text (case-insensitive). This includes:
- Exact duplicates: `## Installation` and `## Installation`
- Case variations: `## Installation` and `## installation`
- Trivial spacing variations: `## Installation` and `##  Installation` (after trimming)

Any duplicate heading pair triggers failure.

## Emitted Diagnostics

None directly. Duplicate section detection is covered by anti-pattern **DS-AP-STRUCT-003** (Duplicate Identity) in the anti-pattern detection pipeline rather than emitting a standalone diagnostic code.

## Related Anti-Patterns

- **DS-AP-STRUCT-003** (Duplicate Identity): Multiple sections with identical or near-identical names, creating ambiguity and signaling incomplete refactoring or auto-generation errors.

## Related Criteria

- **DS-VC-CON-008** (Canonical Section Names): Enforcing canonical naming conventions implicitly prevents duplicate sections by encouraging consistent naming patterns.
- **DS-VC-STR-009** (No Structural Anti-Patterns): Duplicate Identity is one of five structural anti-patterns detected at L1; this criterion provides a direct measurement at L2.

## Calibration Notes

Duplicate sections are uncommon in well-maintained documentation but occur in auto-generated files where template logic creates repeated sections. None of the 6 v0.0.2c calibration specimens exhibit this issue, suggesting it is a relatively rare failure mode.

However, the weight [CALIBRATION-NEEDED] should be refined once all 11 empirical specimens are scored in Phase C. If duplicate sections are indeed rare, the criterion's weight may be reduced relative to more common quality issues.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase C |
