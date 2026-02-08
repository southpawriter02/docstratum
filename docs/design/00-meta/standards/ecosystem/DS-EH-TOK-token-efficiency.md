# DS-EH-TOK: Token Efficiency

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-EH-TOK |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Dimension** | Token Efficiency |
| **Enum Value** | `EcosystemHealthDimension.TOKEN_EFFICIENCY` |
| **Source Code** | `ecosystem.py` → `EcosystemHealthDimension.TOKEN_EFFICIENCY = "token_efficiency"` |
| **Provenance** | v0.0.7 §4.3 (EcosystemScore — Aggregate Health) |

## Description

Token Efficiency measures whether documentation content is distributed optimally across files, or whether it is concentrated in a monolithic file. An efficient ecosystem has balanced token distribution — no single file dominates by consuming more than 80% of total tokens.

When documentation is poorly distributed, LLMs face a critical limitation: they have finite context windows. A single massive file consumes disproportionate context, leaving insufficient tokens for other files, cross-references, and user interaction. This forces the model to either truncate content or abandon other ecosystem files entirely, reducing the richness of guidance available.

Token efficiency detects the Monolith Monster anti-pattern at the ecosystem level and surfaces unbalanced distributions via the W018 diagnostic.

## Measurement

Token efficiency is calculated using distribution analysis:

```
token_efficiency_score = (1 - gini_coefficient(file_token_counts)) × dimension_weight
```

Alternative formulation using Herfindahl index:

```
herfindahl_index = Σ(file_tokens / total_tokens)²
token_efficiency_score = (1 - herfindahl_index) × dimension_weight
```

Where:
- `gini_coefficient` = Statistical measure of distribution inequality (0 = perfect equality, 1 = perfect inequality)
- `herfindahl_index` = Concentration index (0 = perfect dispersion, 1 = perfect concentration)
- `file_token_counts` = Token count for each file in the ecosystem
- `dimension_weight` = Weighting factor applied to this dimension

**Red flags:**
- Single file >80% of total tokens: Critical inefficiency
- Single file >50% of total tokens: Poor distribution
- Balanced distribution (each file <20% of total): Optimal efficiency

A score of 1.0 indicates perfectly balanced token distribution across all files. A score of 0.2 indicates severe concentration (one file dominates).

## Why Token Efficiency Matters for LLMs

- **Context Window Constraints:** LLMs have limited context (e.g., 200K tokens). An ecosystem with balanced files allows the model to load multiple files without truncation. A monolithic file forces trade-offs.
- **Parallel Reasoning:** LLMs perform better when they can hold multiple perspectives in context simultaneously. Token efficiency enables this by ensuring no single file consumes the context budget.
- **Progressive Loading:** Well-distributed ecosystems allow LLMs to load content progressively (start with Getting Started, then drill into API Reference). Monolithic files force all-or-nothing loading.
- **Retrieval Quality:** When content is balanced, each file is more likely to fit entirely within retrieval windows. Monolithic files are truncated during retrieval, losing contextual edges.

## Related Anti-Patterns

- **DS-AP-ECO-005** (Token Black Hole): More than 80% of tokens concentrated in a single file, consuming ecosystem resources
- **DS-AP-STRAT-002** (Monolith Monster): A single file exceeding 100,000 tokens, indicating severely unbalanced architecture

## Related Diagnostic Codes

- **DS-DC-W018** (UNBALANCED_TOKEN_DISTRIBUTION): Fires when token distribution exceeds acceptable concentration thresholds

## Implementation Reference

Token efficiency calculation in `ecosystem.py`:
- Iterate over all `EcosystemFile` objects
- Count tokens in each file (or use estimated token count from file size heuristics)
- Calculate total tokens across all files
- Compute Gini coefficient or Herfindahl index of distribution
- Apply dimension weighting
- Generate diagnostics (W018) if concentration exceeds thresholds (>80% in single file)

Example token distribution analysis:
```
File A: 25K tokens (25%)
File B: 22K tokens (22%)
File C: 20K tokens (20%)
File D: 18K tokens (18%)
File E: 15K tokens (15%)
Total: 100K tokens
Distribution: Balanced → High efficiency score

vs.

File A: 80K tokens (80%)
File B: 20K tokens (20%)
Total: 100K tokens
Distribution: Concentrated → Low efficiency score
```


## Naming Reconciliation (D-DEC-03)

> **§7.7 Decision D-DEC-03:** The v0.0.7 research document and the `ecosystem.py` source code use different naming for the five ecosystem health dimensions. Per D-DEC-03, the code naming is authoritative (it was implemented after v0.0.7 and may have evolved the naming for good reasons), but both names are documented for traceability.

| v0.0.7 Name | Code Name | Resolution |
|-------------|-----------|------------|
| Capability | `EcosystemHealthDimension.TOKEN_EFFICIENCY` | Renamed |

**Full v0.0.7 ↔ Code mapping:**

| v0.0.7 | Code | Change |
|--------|------|--------|
| Coverage | COVERAGE | Unchanged |
| Coherence | CONSISTENCY | Renamed (clarity) |
| Completeness | COMPLETENESS | Unchanged |
| Consistency | FRESHNESS | Renamed (disambiguation) |
| Capability | TOKEN_EFFICIENCY | Renamed (measurability) |

**This dimension:** Renamed from v0.0.7 'Capability' to 'Token Efficiency'. The v0.0.7 research used 'Capability' to describe the ecosystem's capacity to serve AI agents effectively. During implementation, this was refined to 'Token Efficiency' because the primary measurable signal is token distribution across files — detecting the W018 (UNBALANCED_TOKEN_DISTRIBUTION) diagnostic and the AP-ECO-005 (Token Black Hole) anti-pattern. 'Token Efficiency' is concrete and measurable; 'Capability' was abstract and open to interpretation.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.6 |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
