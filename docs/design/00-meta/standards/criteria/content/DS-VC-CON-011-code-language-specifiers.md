# DS-VC-CON-011: Code Language Specifiers

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VC-CON-011 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Platinum ID** | L3-04 |
| **Dimension** | Content (50%) |
| **Level** | L3 — Best Practices |
| **Weight** | 3 / 50 content points |
| **Pass Type** | SOFT |
| **Measurability** | Fully measurable |
| **Provenance** | v0.0.4b; practical principle: language hints enable syntax-aware processing by LLM agents and syntax highlighters; improves readability and correctness inference |

## Description

This criterion ensures that all fenced code blocks include a language identifier (e.g., ```python, ```bash, ```javascript) immediately following the opening triple backticks. Language specifiers enable both syntax highlighters and LLM agents to apply language-specific parsing, semantic analysis, and correctness checking to the code content.

Language specifiers are a low-cost quality improvement with high practical value. When an LLM agent encounters a code block labeled ```python, it can apply Python-specific reasoning: variable types, library availability, syntax rules, common idioms. Without a language hint, the agent must either guess or treat the block as generic text, degrading accuracy.

Recognized language identifiers include: python, bash, javascript, typescript, json, yaml, html, css, shell, java, go, rust, c, cpp, and other standard language abbreviations. The criterion does not penalize unknown or domain-specific language identifiers, as long as some identifier is present.

## Pass Condition

All fenced code blocks include a non-empty language specifier:

```python
code_blocks = [
    node for node in ast_nodes
    if node.type == 'fenced_code_block'
]

for block in code_blocks:
    assert block.language is not None and block.language.strip() != ''

# Alternatively, a ratio-based check (all or nothing):
specified_count = sum(1 for b in code_blocks if b.language and b.language.strip())
assert specified_count == len(code_blocks) or len(code_blocks) == 0
```

Files with zero code blocks trivially pass this criterion (prerequisite is CON-010). Files with one or more blocks must specify a language for each block.

## Fail Condition

Any fenced code block opens with triple backticks alone (``` or ```\n) with no language identifier following. Failing scenarios include:

- Code block: ` ``` ` (bare fence with no language)
- Mixed blocks: some with language (```python), some without (```)
- Blocks with only whitespace after opening fence (``` \n)

W005 fires once per code block that lacks a language identifier.

## Emitted Diagnostics

- **DS-DC-W005** (WARNING): Emitted once per fenced code block without a language specifier

## Related Anti-Patterns

None directly—this is a quality detail and formatting best practice rather than a behavioral anti-pattern.

## Related Criteria

- **DS-VC-CON-010** (Code Examples Present): Code blocks must exist before they can be checked for language specifiers. CON-010 is a prerequisite; CON-011 is a refinement on CON-010.
- **DS-VC-APD-003** (Few-shot Examples): Structured, pedagogical examples (L4) typically include properly specified code blocks with language hints.

## Calibration Notes

Language specifiers are a zero-friction improvement. Top-scoring specimens consistently specify languages on all code blocks. Files without specifiers still function but lose syntax-highlighting benefits and agent-side language detection. Empirically, files with all code blocks specified (100% compliance) are perceived as more polished and professional. The criterion is lenient on language name validity—any non-empty string is acceptable, allowing for domain-specific or legacy language names.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase C |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
