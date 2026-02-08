# DS-VC-APD-006: Token-Optimized Structure

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VC-APD-006 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Platinum ID** | L4-06 |
| **Dimension** | Anti-Pattern Detection (20%) |
| **Level** | L4 — Exemplary |
| **Weight** | 2 / 20 anti-pattern points |
| **Pass Type** | SOFT |
| **Measurability** | Fully measurable |
| **Provenance** | v0.0.4a token allocation guidelines; v0.0.2c: top-scoring files show balanced token distribution across sections |

## Description

This criterion checks that tokens are allocated efficiently across sections. The rationale is pragmatic: in a context-limited environment (LLM inference with finite token budgets), authors should maximize value per token. Sections that provide high value to consuming agents (Getting Started, Core Concepts, API Reference) should contain more content than low-value sections (FAQ, Troubleshooting).

An unbalanced token distribution suggests poor editorial priorities. For example, a file where Troubleshooting consumes 50% of tokens while Getting Started has only 200 tokens is poorly optimized for typical agent consumption patterns. Similarly, a single section that dominates the file (>40% of tokens) may indicate that the file should be split into multiple focused documents, risking the Monolith Monster anti-pattern.

This criterion does not enforce a specific token allocation (e.g., "Getting Started must have exactly 20% of tokens"). Instead, it uses a heuristic threshold to detect imbalance: no single section should consume more than 40% of the file's total tokens. This leaves room for variation while catching obviously skewed distributions.

## Pass Condition

Token distribution across sections is balanced:

```python
h2_sections = parse_h2_headings(content)
section_tokens = {
    s.name: count_tokens(s.content)
    for s in h2_sections
}
total_tokens = sum(section_tokens.values())

if total_tokens > 0:
    max_section_ratio = max(section_tokens.values()) / total_tokens
    assert max_section_ratio <= 0.40  # No section > 40% of total
```

Additionally, the validator may (aspirationally) check that high-value sections collectively contain more tokens than low-value sections, but this is a heuristic preference rather than a hard requirement:

```python
# Aspirational heuristic (not enforced)
HIGH_VALUE_SECTIONS = {'getting started', 'core concepts', 'api reference'}
LOW_VALUE_SECTIONS = {'faq', 'troubleshooting', 'appendix'}

high_value_tokens = sum(
    t for s, t in section_tokens.items()
    if s.lower() in HIGH_VALUE_SECTIONS
)
low_value_tokens = sum(
    t for s, t in section_tokens.items()
    if s.lower() in LOW_VALUE_SECTIONS
)

# Suggestion (not assertion): high_value_tokens >= low_value_tokens
```

## Fail Condition

Token distribution is unbalanced:

- Any single section consumes more than 40% of the file's total tokens
- High-value sections (Getting Started, Core Concepts) collectively contain significantly fewer tokens than low-value sections (FAQ, Troubleshooting)
- The distribution suggests the file should be split into multiple focused documents

**Gate behavior:** This is a SOFT criterion at L4. Failure reduces the Anti-Pattern Detection score but does not block progression.

## Emitted Diagnostics

No standalone diagnostic code is emitted. APD-006 is an L4 enrichment metric without a dedicated DS-DC code.

## Related Anti-Patterns

- **DS-AP-STRAT-002** (Monolith Monster): Extreme token imbalance at the file level. Files with one section >40% of tokens may indicate that a split is needed.
- **DS-AP-STRUCT-001** (Sitemap Dump): Flat link lists without hierarchical structure may consume excessive tokens relative to other content.

## Related Criteria

- **DS-VC-CON-012** (Token Budget Respected): File-level token budget (e.g., "total file should be < 50K tokens"). APD-006 checks section-level distribution; CON-012 checks aggregate file size.
- **DS-VC-STR-007** (Canonical Section Ordering): Section ordering and token allocation are complementary structural concerns. Well-ordered sections with balanced token distribution reflect thoughtful editorial decisions.

## Calibration Notes

The v0.0.2c audit found that top-scoring files exhibit balanced token distribution. Top specimens allocate tokens roughly as follows:

- **Svelte (score 92)**: Getting Started (22%), Core Concepts (25%), API Reference (28%), Examples (15%), Other (10%) — no section dominates
- **Pydantic (score 90)**: Similar balance with roughly 20–25% per major section
- **Lower-scoring files (50–60)**: Often show one section >45% (e.g., a massive API Reference with minimal Getting Started)

The 40% threshold is empirically derived from top-scoring specimens. Files with balanced distribution (no section >40%) consistently score higher on agent task completion. This criterion rewards thoughtful editorial prioritization and structural discipline.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase C exemplary criterion |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
