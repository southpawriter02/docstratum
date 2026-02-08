# DS-VL-L1: Structural

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VL-L1 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Level Number** | 1 |
| **Level Name** | Structural |
| **Enum Value** | `ValidationLevel.L1_STRUCTURAL` |
| **Question Answered** | "Does this file follow the llms.txt spec structure?" |
| **Provenance** | v0.0.6 §3.2 (L1 Structural Checks); v0.0.4a structural checks; v0.0.1a ABNF grammar |

## Description

Level 1 validates the structural skeleton of an llms.txt file. After L0 confirms the file is parseable Markdown, L1 asks: does this file conform to the structural expectations defined by the llms.txt specification? Specifically, L1 checks for the presence of an H1 title, the absence of duplicate H1 elements, the presence of a blockquote description, proper H2-delimited section structure, well-formed links, and correct heading hierarchy.

L1 is the first level that evaluates **spec-defined** structure. While L0 checks pre-specification assumptions (valid encoding, non-empty content), L1 checks what the llms.txt specification actually requires. Files that pass L1 are structurally navigable by an LLM agent — they have a recognizable title, sections, and links.

## Criteria at This Level

| DS Identifier | Platinum ID | Name | Weight | Dimension | Pass Type |
|---------------|-------------|------|--------|-----------|-----------|
| DS-VC-STR-001 | L1-01 | H1 Title Present | 5/30 | Structural | HARD |
| DS-VC-STR-002 | L1-02 | Single H1 Only | 3/30 | Structural | HARD |
| DS-VC-STR-003 | L1-03 | Blockquote Present | 3/30 | Structural | SOFT |
| DS-VC-STR-004 | L1-04 | H2 Section Structure | 4/30 | Structural | HARD |
| DS-VC-STR-005 | L1-05 | Link Format Compliance | 4/30 | Structural | HARD |
| DS-VC-STR-006 | L1-06 | No Heading Level Violations | 3/30 | Structural | SOFT |

**Weight total at this level:** 22 of 30 structural points (the remaining 8 structural points are assessed at L3).

**Pass Type breakdown:** 4 HARD, 2 SOFT. A file can pass L1 with SOFT criterion failures (W001 blockquote missing, heading violations warned) but HARD failures (no H1, multiple H1, no sections, broken link format) block progression to L2.

## Entry Conditions

L0 must pass. All five L0 prerequisite gates must be satisfied:

1. File is valid UTF-8 encoding (no E003)
2. File is non-empty (no E007)
3. File parses as valid Markdown (no E005)
4. File is under 100,000 estimated tokens (no E008)
5. File uses LF line endings (no E004)

If L0 fails, L1 is not evaluated. The file's `level_achieved` stays at `L0_PARSEABLE` with `levels_passed[L0_PARSEABLE] = False`.

## Exit Criteria

**ALL HARD criteria** at this level must pass to achieve L1:

1. File contains exactly one H1 heading (`# Title`) — DS-VC-STR-001 (HARD)
2. No additional H1 headings exist — DS-VC-STR-002 (HARD)
3. At least one H2 section exists — DS-VC-STR-004 (HARD)
4. All links use valid Markdown link format `[text](url)` — DS-VC-STR-005 (HARD)

SOFT criteria (DS-VC-STR-003, DS-VC-STR-006) are evaluated and emitted as warnings but do not block L1 achievement. A file can achieve L1 without a blockquote and with heading level violations, but those issues reduce its quality score.

## Diagnostic Codes at This Level

| DS Identifier | Severity | Fires When | Triggering Criterion |
|---------------|----------|------------|---------------------|
| DS-DC-E001 | ERROR | No H1 heading found | DS-VC-STR-001 |
| DS-DC-E002 | ERROR | Multiple H1 headings found | DS-VC-STR-002 |
| DS-DC-W001 | WARNING | No blockquote description after H1 | DS-VC-STR-003 |
| DS-DC-E006 | ERROR | Malformed or broken link syntax | DS-VC-STR-005 |

> **Note:** DS-VC-STR-004 (H2 Section Structure) and DS-VC-STR-006 (No Heading Level Violations) detect structural issues that contribute to the overall structural dimension score but do not have individually named diagnostic codes in the current `diagnostics.py` registry. Their failures are captured as part of the structural validation pass/fail and reflected in the dimension score.

## Scoring Impact

L1 criteria contribute to the **Structural dimension** (30 points max). The 6 criteria at this level account for 22 of 30 structural points. Specifically:

- **HARD criteria failures** at L1 trigger the structural gating rule (DS-QS-GATE): if any critical structural element is missing (no H1, no sections), the total quality score is capped at 29 (CRITICAL grade).
- **SOFT criteria failures** at L1 reduce the structural dimension score proportionally but do not trigger the gate.

## Relationship to Other Levels

```
L0 (Parseable) — must pass first
  └─► L1 (Structural) ← YOU ARE HERE
       └─► L2 (Content Quality) — requires L1 pass
            └─► L3 (Best Practices) — requires L2 pass
                 └─► L4 (DocStratum Extended) — requires L3 pass
```

L1 builds directly on L0. Once a file is confirmed parseable (L0), L1 validates the structural skeleton. L1 is the minimum level for a file to be considered "structurally valid" — it can be navigated by an LLM agent even if the content quality is poor.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.1 |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
