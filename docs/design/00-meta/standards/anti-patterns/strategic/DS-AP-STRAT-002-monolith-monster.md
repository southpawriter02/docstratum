# DS-AP-STRAT-002: Monolith Monster

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-AP-STRAT-002 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Registry ID** | AP-STRAT-002 |
| **Category** | Strategic |
| **Check ID** | CHECK-017 |
| **Severity Impact** | Deduction penalty — reduces anti-pattern detection dimension score |
| **Provenance** | v0.0.4c §Anti-Patterns Catalog |

## Description

Monolith Monster is a strategic anti-pattern where a single documentation file exceeds 100K tokens without decomposition. The file attempts to contain everything in one massive document, exceeding all current LLM context windows and making selective retrieval impossible. This creates a maintenance burden, poor readability, and breaks the tokenomics principle of respecting context budgets.

## Detection Logic

Estimate token count and measure against established thresholds:

```python
def detect_monolith_monster(file_content: str) -> bool:
    """
    Detects if a single file exceeds token budget thresholds.
    Uses character-to-token approximation: tokens ≈ chars / 4
    """
    # Approximate token count
    estimated_tokens = len(file_content) / 4
    
    # Token zones definition
    OPTIMAL_THRESHOLD = 20_000
    GOOD_THRESHOLD = 50_000
    DEGRADATION_THRESHOLD = 100_000
    
    # Classify and trigger if anti-pattern zone
    if estimated_tokens > DEGRADATION_THRESHOLD:
        return True  # Anti-pattern detected
    
    if estimated_tokens > GOOD_THRESHOLD:
        return "warning"  # Degradation zone
    
    if estimated_tokens > OPTIMAL_THRESHOLD:
        return "info"  # Good zone
    
    return False  # Optimal zone
```

Token zones for single documentation file:
- **Optimal**: <20K tokens
- **Good**: <50K tokens
- **Degradation**: <100K tokens
- **Anti-Pattern**: >100K tokens

## Example (Synthetic)

```markdown
# Complete API Reference

This massive document contains the entire API specification, all endpoints,
all data models, all error codes, all authentication methods, all rate limits,
all webhook events, all SDKs, all CLI tools, all migration guides, all
troubleshooting steps, all FAQ, and all appendices in a single 250K token file.

[Content continues for thousands of lines...]
```

## Remediation

- Decompose large files into logical modules (goal: <50K tokens per file)
- Create a parent index or overview document with links to subdomains
- Implement hierarchical organization: overview → feature → reference → examples
- Use cross-references and include statements to link related sections
- Establish a token budget per document type (e.g., guides: <30K, reference: <50K)
- Monitor file sizes during documentation reviews

## Affected Criteria

- DS-VC-APD-005 (No Strategic Anti-Patterns)
- DS-VC-CON-012 (Token Budget Respected)

## Emitted Diagnostics

- DS-DC-E008 (EXCEEDS_SIZE_LIMIT)
- DS-DC-W010 (TOKEN_BUDGET_EXCEEDED)

## Related Anti-Patterns

- DS-AP-ECO-005 (Token Black Hole — ecosystem-level version)

## Change History

| ASoT Version | Date | Change |
|---|---|---|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.2 |
