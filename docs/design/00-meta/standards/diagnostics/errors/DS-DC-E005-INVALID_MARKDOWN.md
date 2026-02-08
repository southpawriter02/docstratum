# DS-DC-E005: INVALID_MARKDOWN

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DC-E005 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Code** | E005 |
| **Severity** | ERROR |
| **Validation Level** | L0 — Parseable |
| **Check ID** | MD-001 (v0.0.4a) |
| **Provenance** | CommonMark spec; v0.0.4a structural checks |

## Message

> File contains invalid Markdown syntax that prevents parsing.

## Remediation

> Fix Markdown syntax errors. Use a Markdown linter to identify issues.

## Description

This error fires when the file contains Markdown syntax that violates the CommonMark specification and prevents the parser from successfully creating an abstract syntax tree (AST). Unlike minor style issues that trigger warnings, invalid Markdown is a blocking error that stops all downstream validation.

Common causes include unmatched delimiters (unclosed code blocks, mismatched parentheses in links), invalid list markers, and malformed HTML tags. A Markdown linter tool can quickly identify and locate these syntax violations.

### When This Code Fires

- The Markdown parser encounters syntax that does not conform to the CommonMark specification.
- The file fails to parse completely, preventing generation of an AST.
- This is a Phase C L0 check performed early in the validation pipeline (L0-03).

### When This Code Does NOT Fire

- The file is a valid Markdown document per CommonMark.
- All syntax elements (headings, lists, links, code blocks, etc.) are properly formed.
- The parser can successfully generate an AST representation.

## Triggering Criteria

L0 pipeline prerequisite gate — no formal VC criterion file. L0-03 (Valid Markdown Syntax) check documented in DS-VL-L0-PARSEABLE.md.
## Related Anti-Patterns

None directly.

## Related Diagnostic Codes

- DS-DC-E003 (encoding errors can also prevent parsing)

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
| 0.0.0-scaffold | 2026-02-08 | Phase C backfill — added VC cross-references to Triggering Criteria section |
