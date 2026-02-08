# DS-VC-CON-010: Code Examples Present

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VC-CON-010 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Platinum ID** | L3-03 |
| **Dimension** | Content (50%) |
| **Level** | L3 — Best Practices |
| **Weight** | 5 / 50 content points |
| **Pass Type** | SOFT |
| **Measurability** | Fully measurable |
| **Provenance** | v0.0.4b; v0.0.2c pattern analysis: code examples are the strongest single predictor of quality score (r ≈ 0.65) across 450+ projects |

## Description

This criterion verifies that the llms.txt file contains at least one fenced code block (triple backticks with or without a language specifier). Code examples are the most powerful signal of documentation quality and practical utility. They provide concrete, runnable demonstrations of the concepts, patterns, and APIs described in the prose sections.

In v0.0.2c correlation analysis, the presence of code examples showed the strongest single correlation with quality scores (r ≈ 0.65). Files without any code examples rarely achieve quality scores above 60, whereas files with multiple, well-chosen examples routinely score above 85. Code examples enable LLM agents to ground abstract descriptions in concrete syntax, improving reasoning and task completion accuracy.

Inline code (single backticks) is not counted—only fenced code blocks (triple backticks) qualify, as they are presumed to be substantive, runnable examples.

## Pass Condition

The file contains at least one fenced code block:

```python
code_blocks = [
    node for node in ast_nodes
    if node.type == 'fenced_code_block'
]
assert len(code_blocks) >= 1
```

Fenced code blocks are identified by opening and closing triple backticks (```). Inline code (single backticks) does not count toward this criterion. Files with zero fenced code blocks fail; files with one or more pass.

## Fail Condition

The file contains zero fenced code blocks anywhere in its content. Failing scenarios include:

- File is purely prose with no code examples
- File contains only inline code snippets (single backticks) but no fenced blocks
- File references external code examples but does not embed any directly

W004 fires once when no code examples are detected.

## Emitted Diagnostics

- **DS-DC-W004** (WARNING): Emitted when the file contains no fenced code blocks

## Related Anti-Patterns

- **DS-AP-CONT-006** (Example Void): No code examples despite being a technical project documentation file, resulting in abstract, hard-to-apply descriptions.

## Related Criteria

- **DS-VC-CON-011** (Code Language Specifiers): If code blocks exist (as verified by CON-010), they should specify a language identifier (e.g., ```python, ```bash). This is the natural follow-up criterion.
- **DS-VC-APD-003** (Few-shot Examples): L4 criterion for structured, pedagogical example patterns (e.g., question/answer pairs with code solutions).

## Calibration Notes

Code examples show the strongest single correlation with quality scores (r ≈ 0.65) from v0.0.2c analysis of 450+ projects. Top-scoring specimens include:
- **Svelte** (quality score 92): Contains 15+ code examples across multiple languages
- **Pydantic** (quality score 90): Includes 8+ illustrative code blocks

Files without code examples score below 60% on average. The presence of even a single well-chosen example lifts quality perception significantly. Files with multiple diverse examples (e.g., JavaScript, Python, YAML) score highest.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase C |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
