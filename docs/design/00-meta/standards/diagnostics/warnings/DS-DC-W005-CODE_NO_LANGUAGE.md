# DS-DC-W005: CODE_NO_LANGUAGE

| Field | Value |
|-------|-------|
| DS Identifier | DS-DC-W005 |
| Status | DRAFT |
| ASoT Version | 0.0.0-scaffold |
| Code | W005 |
| Severity | WARNING |
| Validation Level | L3 — Best Practices |
| Check ID | CNT-008 (v0.0.4b) |
| Provenance | v0.0.4b content checks; CommonMark fenced code block syntax |

## Message

> Code block found without a language specifier.

## Remediation

> Add a language identifier after the opening triple backticks.

## Description

Language specifiers on fenced code blocks enable syntax highlighting, semantic understanding, and appropriate tooling. Without a language identifier, code is rendered as plain text, losing visual clarity and making it harder for readers to parse syntax. CommonMark and markdown processors use language specifiers to apply appropriate formatting and highlighting.

Specifying the language also allows for automated validation, linting, and code example extraction. When multiple languages appear in a file, clear language identifiers help readers quickly identify which examples apply to their context.

### When This Code Fires

W005 fires when a fenced code block is found without a language identifier. This means code appears between triple backticks with no language token after the opening backticks (e.g., ``` instead of ```python).

### When This Code Does NOT Fire

W005 does not fire when all code blocks include language specifiers (e.g., ```python, ```bash, ```javascript, etc.). It also does not fire for non-code fenced blocks where language specifiers are genuinely not applicable.

## Triggering Criterion

**DS-VC-CON-011: Code Language Specifiers**

All fenced code blocks must include a language identifier. This criterion validates that code is presented with proper syntax highlighting markup.

## Related Anti-Patterns

None directly related.

## Related Diagnostic Codes

**DS-DC-W004: NO_CODE_EXAMPLES** — W004 and W005 are sibling warnings: W004 fires when no code blocks exist at all, while W005 fires when code blocks exist but lack language tags. Both address code quality, but at different levels.

## Change History

| Version | Date | Notes |
|---------|------|-------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
