# DS-VC-CON-012: Token Budget Respected

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VC-CON-012 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Platinum ID** | L3-05 |
| **Dimension** | Content (50%) |
| **Level** | L3 — Best Practices |
| **Weight** | 4 / 50 content points [CALIBRATION-NEEDED] |
| **Pass Type** | SOFT |
| **Measurability** | Fully measurable |
| **Provenance** | DECISION-013: 3 token budget tiers established in v0.0.4a; v0.0.1b Gap #1 (maximum file size); empirical v0.0.4c finding: files above 50K tokens show degraded retrieval performance and LLM reasoning latency |

## Description

This criterion ensures that the llms.txt file respects a sensible token budget, falling within one of three recognized tiers: **Standard** (1,500–4,500 tokens), **Comprehensive** (4,500–12,000 tokens), or **Full** (12,000–50,000 tokens). The token tiers balance the need for thorough documentation against practical constraints on context window usage and retrieval performance.

Empirical testing in v0.0.4c revealed that files exceeding 50,000 tokens experience degraded retrieval performance, increased latency, and reduced reasoning quality when used with LLM agents. The three-tier system allows projects to choose an appropriate scope: small, focused projects can fit within Standard tier; moderately complex projects use Comprehensive; large, feature-rich projects use Full tier.

Files under 1,500 tokens are accepted as minimal but valid; they are not penalized. Files exceeding 50,000 tokens trigger a warning and indicate that decomposition or splitting into multiple llms.txt files may be beneficial (a Phase D concern).

## Pass Condition

The file's token count falls within one of the three recognized tiers:

```python
token_count = count_tokens(file_content, tokenizer='cl100k_base')

TIERS = [
    ("Standard", 1_500, 4_500),
    ("Comprehensive", 4_500, 12_000),
    ("Full", 12_000, 50_000),
]

in_tier = any(
    min_tokens <= token_count <= max_tokens
    for tier_name, min_tokens, max_tokens in TIERS
)

# Files under 1,500 tokens are acceptable (minimal but valid)
assert in_tier or token_count < 1_500
```

Token counts are measured using the OpenAI `cl100k_base` tokenizer (standard for GPT-3.5/GPT-4 models). Files with token counts between 1,500 and 50,000 pass; files below 1,500 also pass (no penalty).

## Fail Condition

Token count exceeds 50,000, the upper bound of the Full tier, indicating the file has grown beyond the practical retrieval and reasoning window:

- Token count between 50,000 and 100,000: W010 fires; file is in degradation zone
- Token count exceeds 100,000: Caught by L0 criterion E008 (Maximum Size Structural); considered structurally invalid

W010 fires once per file when the token count exceeds the highest tier (50,000 tokens).

## Emitted Diagnostics

- **DS-DC-W010** (WARNING): File exceeds recommended token budget for tier; consider decomposition or splitting into multiple files

## Related Anti-Patterns

- **DS-AP-STRAT-002** (Monolith Monster): A single file exceeding 100K tokens with no decomposition, covering multiple independent projects or features that should be separated.

## Related Criteria

- **DS-VC-APD-006** (Token-optimized Structure): L4 criterion for efficient token allocation and section prioritization across sections.
- **DS-VC-STR-008** (No Critical Anti-Patterns): Monolith Monster is an L0-level concern for extreme cases (>100K tokens); this criterion addresses the L3 best-practice tier.

## Calibration Notes

DECISION-013 established the three tiers based on v0.0.4a analysis of real-world files and empirical retrieval testing:

- **Standard tier (1,500–4,500 tokens):** Small, focused projects. Example: Svelte (~3,200 tokens) fits comfortably in this tier.
- **Comprehensive tier (4,500–12,000 tokens):** Moderately complex projects with multiple sections. Example: Pydantic (~4,800 tokens) occupies the lower Comprehensive range.
- **Full tier (12,000–50,000 tokens):** Large, feature-rich projects with extensive API reference and examples.

Empirical v0.0.4c finding: Turborepo's 116K-token file triggered degraded retrieval and reasoning quality in agent tests. The 50,000-token threshold was chosen to maximize content richness while maintaining practical performance.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase C |
