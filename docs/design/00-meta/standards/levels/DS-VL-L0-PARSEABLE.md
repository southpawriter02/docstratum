# DS-VL-L0: Parseable

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VL-L0 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Level Number** | 0 |
| **Level Name** | Parseable |
| **Enum Value** | `ValidationLevel.L0_PARSEABLE` |
| **Question Answered** | "Can a machine read this file at all?" |
| **Provenance** | Implicit in spec; v0.0.1a formal grammar; v0.0.4a structural checks |

## Description

Level 0 is the foundation of the validation pipeline. It answers the most basic question: can this file be read and parsed as a Markdown document? A file that fails L0 cannot be evaluated at any higher level — it is the universal prerequisite for all other validation.

L0 criteria are **pre-specification** — the llms.txt spec assumes them without stating them explicitly. Any text-processing tool requires these properties to function.

## Criteria at This Level

> **Note:** L0 criteria do not have individual VC files in Phase A. They will be defined during Phase C. The checks are documented below by their Platinum Standard IDs.

| Platinum ID | Name | Pass Type | DS Identifier |
|-------------|------|-----------|---------------|
| L0-01 | Valid UTF-8 Encoding | HARD | Phase C |
| L0-02 | Non-Empty Content | HARD | Phase C |
| L0-03 | Valid Markdown Syntax | HARD | Phase C |
| L0-04 | Under Maximum Token Limit | HARD | Phase C |
| L0-05 | Line Feed Normalization | HARD | Phase C |

## Entry Conditions

None. L0 is the entry point of the pipeline. Every file starts here.

## Exit Criteria

**ALL** of the following must be true to pass L0:

1. File is valid UTF-8 encoding (no `UnicodeDecodeError`, no BOM)
2. File is non-empty (contains at least one non-whitespace character)
3. File parses as valid CommonMark Markdown (no fatal syntax errors)
4. File does not exceed 100,000 estimated tokens
5. File uses LF line endings (no CR or CRLF bytes)

If **any** of these fail, the file receives `level_achieved = L0_PARSEABLE` with `levels_passed[L0_PARSEABLE] = False`. No further validation proceeds.

## Diagnostic Codes at This Level

| DS Identifier | Severity | Fires When |
|---------------|----------|------------|
| DS-DC-E003 | ERROR | Invalid UTF-8 encoding |
| DS-DC-E004 | ERROR | Non-LF line endings |
| DS-DC-E005 | ERROR | Invalid Markdown syntax |
| DS-DC-E007 | ERROR | Empty or whitespace-only file |
| DS-DC-E008 | ERROR | Exceeds 100K token limit |

## Scoring Impact

L0 failures trigger the structural gating rule (DS-QS-CAP-structural-gating): the total quality score is capped at 29 (Critical grade). This is because a file that cannot be parsed provides zero value to an LLM agent, regardless of what content it might contain.

## Relationship to Other Levels

```
L0 (Parseable) ← YOU ARE HERE
  └─► L1 (Structural) — requires L0 pass
       └─► L2 (Content Quality) — requires L1 pass
            └─► L3 (Best Practices) — requires L2 pass
                 └─► L4 (DocStratum Extended) — requires L3 pass
```

L0 is the only level that is purely a gate. It has no "soft pass" criteria — everything at L0 is HARD.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase A example file |
