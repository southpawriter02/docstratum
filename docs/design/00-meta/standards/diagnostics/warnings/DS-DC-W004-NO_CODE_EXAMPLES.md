# DS-DC-W004: NO_CODE_EXAMPLES

| Field | Value |
|-------|-------|
| DS Identifier | DS-DC-W004 |
| Status | DRAFT |
| ASoT Version | 0.0.0-scaffold |
| Code | W004 |
| Severity | WARNING |
| Validation Level | L3 — Best Practices |
| Check ID | CNT-007 (v0.0.4b) |
| Provenance | v0.0.4b content checks; v0.0.2c: code examples are strongest quality predictor (r~0.65) |

## Message

> File contains no code examples (no fenced code blocks found).

## Remediation

> Add code examples with language specifiers (```python, ```bash, etc.).

## Description

Code examples are the strongest predictor of documentation quality (r~0.65 correlation). They bridge the gap between abstract concepts and practical implementation, transforming theoretical guidance into actionable knowledge. A file without code examples misses the opportunity to demonstrate patterns, syntax, and real-world usage in a concrete way.

Even conceptual or architectural documentation benefits from code examples, such as configuration snippets, API calls, or pseudocode illustrating key principles. Without concrete examples, readers must infer implementation details or resort to external sources.

### When This Code Fires

W004 fires when a file contains no fenced code blocks (marked with triple backticks) at any level. This includes files that reference code concepts but provide no actual code samples.

### When This Code Does NOT Fire

W004 does not fire when a file contains at least one fenced code block, regardless of language or length. It also does not fire for files explicitly classified as non-technical (e.g., glossaries, index pages).

## Triggering Criterion

**DS-VC-CON-010: Code Examples Present**

Files should contain at least one code example to demonstrate the concepts being described. This criterion validates that practical, executable examples are present.

## Related Anti-Patterns

**DS-AP-CONT-006: Example Void** — A file or section that discusses technical concepts without providing any concrete code examples, leaving readers without practical guidance.

## Related Diagnostic Codes

**DS-DC-W005: CODE_NO_LANGUAGE** — W004 detects when no code blocks exist at all, while W005 detects code blocks that lack language specifiers. These are related but distinct: W004 addresses absence, W005 addresses incomplete formatting.

## Change History

| Version | Date | Notes |
|---------|------|-------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
