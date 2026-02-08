# DS-AP-STRAT-001: Automation Obsession

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-AP-STRAT-001 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Registry ID** | AP-STRAT-001 |
| **Category** | Strategic |
| **Check ID** | CHECK-016 |
| **Severity Impact** | Deduction penalty — reduces anti-pattern detection dimension score |
| **Provenance** | v0.0.4c §Anti-Patterns Catalog |

## Description

Automation Obsession occurs when documentation is fully auto-generated with no human curation or review. The file was produced by a tool (Mintlify, Sphinx, auto-doc) and published without human editing. This results in formulaic descriptions lacking customization, context, or domain-specific insight. The documentation becomes a sterile, template-driven artifact rather than a thoughtful guide for users.

## Detection Logic

Combine multiple signals to identify this anti-pattern:

```python
def detect_automation_obsession(content: str, links: List[str]) -> bool:
    """
    Detects if documentation is auto-generated with no human curation.
    Triggers if 3+ of 4 signals are present.
    """
    signals = 0
    
    # Signal 1: Formulaic descriptions (>70% boilerplate)
    boilerplate_ratio = calculate_boilerplate_ratio(content)
    if boilerplate_ratio > 0.70:
        signals += 1
    
    # Signal 2: No blockquote or only generic blockquotes
    blockquotes = extract_blockquotes(content)
    if len(blockquotes) == 0 or all_generic(blockquotes):
        signals += 1
    
    # Signal 3: No code examples or insufficient examples
    code_blocks = extract_code_blocks(content)
    if len(code_blocks) < 2:
        signals += 1
    
    # Signal 4: Identical link description patterns (low variance)
    link_variance = measure_link_description_variance(links)
    if link_variance < 0.3:
        signals += 1
    
    return signals >= 3
```

## Example (Synthetic)

```markdown
# API Documentation

This document provides documentation for the API.

## Overview

The API is a set of endpoints that allow you to interact with our service.

## Getting Started

To get started with the API, you will need credentials. See [Getting Started](../getting-started).

## Endpoints

The API provides the following endpoints:

- [Users Endpoint](../endpoints/users) - Manage users
- [Products Endpoint](../endpoints/products) - Manage products
- [Orders Endpoint](../endpoints/orders) - Manage orders

## Response Format

Responses are in JSON format. See [Response Format](../format/json).

## Error Handling

Errors are returned as JSON. See [Error Handling](../errors/handling).
```

## Remediation

- Audit auto-generation workflows; require human review before publication
- Add custom context, examples, and insights specific to your project
- Include domain-specific blockquotes, warnings, or cautions
- Provide at least 2-3 substantial code examples per major section
- Vary link text and descriptions to show purposeful curation
- Document rationale for architectural decisions, not just facts

## Affected Criteria

- DS-VC-APD-005 (No Strategic Anti-Patterns)

## Emitted Diagnostics

None specific — scored through APD dimension.

## Related Anti-Patterns

- DS-AP-CONT-007 (Formulaic Description)
- DS-AP-CONT-006 (Example Void)
- DS-AP-STRUCT-001 (Sitemap Dump)

## Change History

| ASoT Version | Date | Change |
|---|---|---|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.2 |
