# DS-DC-W005: CODE_NO_LANGUAGE

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DC-W005 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Code** | W005 |
| **Severity** | WARNING |
| **Validation Level** | L3 — Best Practices |
| **Check ID** | CNT-008 (v0.0.4b) |
| **Provenance** | v0.0.4b content checks; CommonMark fenced code block syntax |

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

## Triggering Criteria

- **DS-VC-CON-011**: (Code Language Specifiers)

Emitted by DS-VC-CON-011 when a fenced code block does not include a language specifier. Fires per unspecified block.
## Related Anti-Patterns

None directly related.

## Related Diagnostic Codes

**DS-DC-W004: NO_CODE_EXAMPLES** — W004 and W005 are sibling warnings: W004 fires when no code blocks exist at all, while W005 fires when code blocks exist but lack language tags. Both address code quality, but at different levels.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
| 0.0.0-scaffold | 2026-02-08 | Phase C backfill — added VC cross-references to Triggering Criteria section |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
