# DS-VL-L2: Content Quality

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VL-L2 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Level Number** | 2 |
| **Level Name** | Content Quality |
| **Enum Value** | `ValidationLevel.L2_CONTENT` |
| **Question Answered** | "Is the content meaningful and useful for an LLM agent?" |
| **Provenance** | v0.0.6 §3.3 (L2 Content Quality Checks); v0.0.4b content checks; v0.0.2c empirical audit |

## Description

Level 2 evaluates whether the file's content is meaningful, substantive, and useful — not just structurally correct. After L1 confirms the structural skeleton (H1, H2 sections, valid links), L2 asks: is there real content behind those structures? Are the link descriptions informative? Do the URLs actually resolve? Are the sections populated with genuine content rather than placeholders?

L2 is where content quality separates structurally valid files from genuinely useful ones. A file that passes L1 but fails L2 has the right shape but empty or misleading content — like a building with walls but no rooms. L2 catches common "content debt" patterns: bare URL lists, placeholder text like "TODO" or "Coming soon", empty sections, duplicate sections, and auto-generated boilerplate descriptions.

All L2 criteria operate within the **Content dimension** (50 points) and use **SOFT** pass types — they reduce the quality score proportionally but do not gate progression by themselves. However, collectively, if too many L2 criteria fail, the score will fall below the ADEQUATE threshold (50 points).

## Criteria at This Level

| DS Identifier | Platinum ID | Name | Weight | Dimension | Pass Type |
|---------------|-------------|------|--------|-----------|-----------|
| DS-VC-CON-001 | L2-01 | Non-Empty Link Descriptions | 5/50 | Content | SOFT |
| DS-VC-CON-002 | L2-02 | URL Resolvability | 4/50 | Content | SOFT |
| DS-VC-CON-003 | L2-03 | No Placeholder Content | 3/50 | Content | SOFT |
| DS-VC-CON-004 | L2-04 | Non-Empty Sections | 4/50 | Content | SOFT |
| DS-VC-CON-005 | L2-05 | No Duplicate Sections | 3/50 | Content | SOFT |
| DS-VC-CON-006 | L2-06 | Substantive Blockquote | 3/50 | Content | SOFT |
| DS-VC-CON-007 | L2-07 | No Formulaic Descriptions | 3/50 | Content | SOFT |

**Weight total at this level:** 25 of 50 content points (the remaining 25 content points are assessed at L3).

**Pass Type breakdown:** 0 HARD, 7 SOFT. All L2 criteria are soft — they degrade the score but do not individually block progression. This reflects the graduated nature of content quality: a file with some placeholder text is worse than one without, but it's not a structural failure.

## Entry Conditions

L1 must pass. All HARD criteria at L1 must be satisfied:

1. Exactly one H1 heading present (DS-VC-STR-001)
2. No additional H1 headings (DS-VC-STR-002)
3. At least one H2 section exists (DS-VC-STR-004)
4. All links use valid Markdown format (DS-VC-STR-005)

If L1 fails (any HARD criterion fails), L2 is not evaluated.

## Exit Criteria

Because all L2 criteria are SOFT, L2 exit is determined by aggregate scoring rather than individual pass/fail gates. A file "achieves" L2 when:

1. All L1 HARD criteria pass (entry condition), AND
2. L2 criteria are evaluated (even if some fail)

The quality score from L2 criteria determines whether the file's total score reaches the ADEQUATE threshold (≥50). If L2 criteria collectively drag the score below 50, the grade will be NEEDS_WORK or CRITICAL even though the file technically "achieves" L2 level.

> **Design note:** The `level_achieved` field in `ValidationResult` reflects the highest level where checks were *evaluated*, not where all checks *passed*. For L2, all SOFT criteria are evaluated; their failures reduce the score but do not prevent L2 from being "achieved" for the purpose of level progression.

## Diagnostic Codes at This Level

| DS Identifier | Severity | Fires When | Triggering Criterion |
|---------------|----------|------------|---------------------|
| DS-DC-W003 | WARNING | Link has no description text (bare URL) | DS-VC-CON-001 |
| DS-DC-E006 | ERROR | URL does not resolve (404, timeout, DNS failure) | DS-VC-CON-002 |
| DS-DC-W011 | WARNING | Section has heading but no content | DS-VC-CON-004 |
| DS-DC-W006 | WARNING | Link descriptions follow auto-generated patterns | DS-VC-CON-007 |

> **Note:** DS-VC-CON-003 (No Placeholder Content), DS-VC-CON-005 (No Duplicate Sections), and DS-VC-CON-006 (Substantive Blockquote) detect content quality issues that are reflected in scoring but do not have individually named diagnostic codes in the current `diagnostics.py` registry. Their failures are captured through the content dimension scoring.

## Scoring Impact

L2 criteria contribute to the **Content dimension** (50 points max). The 7 criteria at this level account for 25 of 50 content points. Content is the highest-weighted dimension (50% of the total score), making L2 the most impactful level for the overall quality grade.

Key scoring behaviors at L2:

- **Non-Empty Link Descriptions** (5 points) is the highest-weighted L2 criterion because empirical data (v0.0.2c) shows that descriptive links correlate strongly with overall documentation quality (r ~ 0.45).
- **URL Resolvability** (4 points) uses E006 severity (ERROR) because broken links directly prevent LLM agents from accessing referenced content.
- **No Formulaic Descriptions** (3 points) targets auto-generated content patterns (especially Mintlify-style "Learn about X" templates) that reduce information density.

## Relationship to Other Levels

```
L0 (Parseable)
  └─► L1 (Structural) — must pass first
       └─► L2 (Content Quality) ← YOU ARE HERE
            └─► L3 (Best Practices) — requires L2 evaluation
                 └─► L4 (DocStratum Extended) — requires L3 evaluation
```

L2 bridges the gap between structural compliance (L1) and best-practice adherence (L3). A file that achieves L2 has both correct structure and meaningful content — it is genuinely useful to an LLM agent, even if it doesn't follow all recommended patterns.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.1 |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
