# DS-VC-CON-006: Substantive Blockquote

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VC-CON-006 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Platinum ID** | L2-06 |
| **Dimension** | Content (50%) |
| **Level** | L2 — Content Quality |
| **Weight** | 3 / 50 content points [CALIBRATION-NEEDED] |
| **Pass Type** | SOFT |
| **Measurability** | Fully measurable |
| **Provenance** | v0.0.2c audit: blockquotes under 20 chars correlate with lowest-quality files |

## Description

This criterion checks the substance of blockquote content, assuming one exists. The blockquote (typically appearing right after the H1 title) serves as a one-line project description or tagline. A substantive blockquote conveys meaning and purpose; a trivial blockquote merely repeats the project name or contains generic text.

The v0.0.2c audit found that blockquotes under 20 characters correlate strongly with lowest-quality files (bottom quartile). Similarly, blockquotes that simply repeat the H1 title without adding information are a signal of incomplete curation.

This criterion only applies if a blockquote exists. The requirement that a blockquote be present is handled by a separate structural criterion (**DS-VC-STR-003**). Together, these criteria enforce: "If a blockquote exists, it should be meaningful."

## Pass Condition

If a blockquote exists, it must satisfy **both** of these conditions:

```python
if blockquote_exists:
    text = blockquote.text.strip()
    h1_title = extract_h1_title(content).text.strip()

    # Condition 1: Sufficient length
    assert len(text) >= 20  # [CALIBRATION-NEEDED]

    # Condition 2: Not merely repeating the title
    similarity = string_similarity(text, h1_title)
    assert similarity < 0.8  # [CALIBRATION-NEEDED]
```

If no blockquote exists, this criterion passes vacuously (the structural requirement is handled by **DS-VC-STR-003**).

The 20-character threshold and 0.8 similarity threshold are provisional [CALIBRATION-NEEDED] and should be refined against the 11 empirical specimens.

## Fail Condition

A blockquote exists but is trivial in one of two ways:

1. **Too short:** Fewer than 20 characters. Examples: `> MyProject`, `> A library`
2. **Merely repetitive:** Substantially repeats the H1 title without adding information. Example: `> MyProject is MyProject` (similarity > 0.8 with title)

The similarity check uses approximate string matching (e.g., Levenshtein distance or Jaro-Winkler) normalized to a 0–1 scale, where 1 = identical and 0 = completely different. A threshold of 0.8 catches near-repetitions while allowing minor rewording.

## Emitted Diagnostics

None — this is an informational criterion. No standalone diagnostic code is emitted. The absence of a blockquote is flagged by **DS-VC-STR-003** (Blockquote Present).

## Related Anti-Patterns

None directly identified in the current anti-pattern catalog.

## Related Criteria

- **DS-VC-STR-003** (Blockquote Present): Checks whether a blockquote exists at all; DS-VC-CON-006 checks the quality of that blockquote. Together they enforce: "A meaningful blockquote should exist."

## Calibration Notes

The 20-character threshold derives from v0.0.2c analysis. Blockquotes under 20 characters correlate with the lowest-quality files (bottom quartile). Exemplar data:

- **DS-CS-001 (Svelte):** "Cybernetically enhanced web apps" (32 characters) — substantive and passes
- **DS-CS-002 (Pydantic):** "Data validation using Python type annotations" (46 characters) — substantive and passes

The 0.8 similarity threshold [CALIBRATION-NEEDED] should be calibrated against the 11 empirical specimens. Early analysis suggests that files with blockquotes near-identical to the H1 title are a rare edge case but important to flag when detected.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase C |
