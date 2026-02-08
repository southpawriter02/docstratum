# DS-AP-ECO-005: Token Black Hole

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-AP-ECO-005 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Registry ID** | AP-ECO-005 |
| **Category** | Ecosystem |
| **Check ID** | CHECK-027 |
| **Severity Impact** | Ecosystem-level — affects EcosystemScore rather than per-file QualityScore |
| **Provenance** | v0.0.7 §6 (Ecosystem Anti-Patterns) |

## Description

A Token Black Hole occurs when one file consumes more than 80% of the total token budget of the ecosystem. The content distribution is extremely unbalanced, with one massive file dominating the token allocation while other files are starved. This creates a skewed representation of the project's knowledge base.

This is harmful to LLM agents because their context window is fixed and finite. If one file consumes 80%+ of tokens, an LLM agent that processes the ecosystem will either load that single file and have little room for other content, or will need to make painful trade-off decisions. The agent may inadvertently treat the massive file as the "true" content and marginalize other files, even if those files are equally important. This biases the agent's understanding of the project architecture.

## Detection Logic

```python
def detect_token_black_hole(project_root: str) -> bool:
    """
    Detect if one file consumes >80% of ecosystem tokens.
    
    Returns True if (max_file_tokens / total_ecosystem_tokens) > 0.80
    """
    all_files = discover_documentation_files(project_root)  # .md, .txt, etc.
    
    if len(all_files) == 0:
        return False
    
    file_tokens = {}
    total_tokens = 0
    
    for filepath in all_files:
        tokens = estimate_token_count(read_file(filepath))
        file_tokens[filepath] = tokens
        total_tokens += tokens
    
    if total_tokens == 0:
        return False
    
    max_tokens = max(file_tokens.values())
    token_ratio = max_tokens / total_tokens
    
    return token_ratio > 0.80
```

## Example (Synthetic)

Ecosystem structure:
```
docs/
├── README.md                 (2,000 tokens)
├── getting-started.md        (1,500 tokens)
├── api-reference.md          (1,200 tokens)
├── faq.md                    (800 tokens)
├── MASSIVE-SPECIFICATION.md  (150,000 tokens)
└── changelog.md              (500 tokens)
```

Total: ~157,000 tokens
MASSIVE-SPECIFICATION.md: 150,000 / 157,000 = 95.5% of budget. Trigger.

## Remediation

1. **Identify the black hole**: Use token counting to find the file(s) consuming excessive tokens.
2. **Decompose large files**: Split the massive file into multiple logically distinct files (e.g., separate sections into different documents).
3. **Create summaries**: For large files that contain detailed specifications, create a summarized version and link to the detailed version.
4. **Archive or defer**: If the file contains historical or rarely-used information, move it to an archive and reference it from the index rather than including it inline.
5. **Rebalance the ecosystem**: Ensure no single file exceeds 40-50% of the token budget.

## Affected Criteria

Ecosystem-level diagnostic — no per-file VC criterion. This anti-pattern affects EcosystemScore scoring, not individual QualityScore metrics.

## Emitted Diagnostics

- **DS-DC-W018** (UNBALANCED_TOKEN_DISTRIBUTION) — Fired when token distribution across files is heavily skewed.

## Related Anti-Patterns

- **DS-AP-STRAT-002** (Monolith Monster) — Per-file pattern where a single file exceeds size thresholds. Token Black Hole operates at the ecosystem level, considering the relative distribution across all files.
- **DS-AP-ECO-006** (Orphan Nursery) — Missing content vs. over-concentrated content. Both distort the ecosystem balance.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.2 |
