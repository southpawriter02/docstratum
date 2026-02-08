# DS-AP-STRUCT-003: Duplicate Identity

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-AP-STRUCT-003 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Registry ID** | AP-STRUCT-003 |
| **Category** | Structural |
| **Check ID** | CHECK-007 |
| **Severity Impact** | Reduce structural dimension score |
| **Provenance** | v0.0.4c §Anti-Patterns Catalog |

## Description

Multiple sections with identical or near-identical names. Confuses navigation — an LLM agent cannot distinguish between two sections named "API" or "API Reference" and "API Docs". When section headers fail to provide unique, semantic identity, navigation systems cannot reliably route requests to the correct content, creating ambiguity in the knowledge structure.

## Detection Logic

```python
def detect_duplicate_identity(file_content):
    """
    Detects sections with duplicate or near-identical names.
    
    Triggers if:
    - Normalize section names (lowercase, strip whitespace)
    - Check for exact matches after normalization
    - Check for Levenshtein similarity > 0.85 between any two section names
    - If duplicates found, trigger
    """
    import re
    from difflib import SequenceMatcher
    
    # Extract all H2 section headers
    h2_pattern = r'^## (.+)$'
    section_names = re.findall(h2_pattern, file_content, re.MULTILINE)
    
    if len(section_names) <= 1:
        return False, "Only 0 or 1 section found; no duplicates possible"
    
    def normalize_name(name):
        """Normalize section name for comparison."""
        return name.lower().strip()
    
    def levenshtein_similarity(s1, s2):
        """Calculate similarity ratio between two strings (0 to 1)."""
        matcher = SequenceMatcher(None, s1, s2)
        return matcher.ratio()
    
    duplicates = []
    
    # Check for exact matches after normalization
    normalized = [normalize_name(name) for name in section_names]
    for i in range(len(normalized)):
        for j in range(i + 1, len(normalized)):
            if normalized[i] == normalized[j]:
                duplicates.append((section_names[i], section_names[j], "exact match"))
            elif levenshtein_similarity(normalized[i], normalized[j]) > 0.85:
                sim = levenshtein_similarity(normalized[i], normalized[j])
                duplicates.append((section_names[i], section_names[j], f"similarity {sim:.2f}"))
    
    if duplicates:
        dup_details = "; ".join([f"'{d[0]}' vs '{d[1]}' ({d[2]})" for d in duplicates])
        return True, f"Duplicate section names detected: {dup_details}"
    
    return False, "No duplicate section names detected"
```

## Example (Synthetic)

```markdown
# API Documentation

## API
Basic overview of our API.

## API Reference
Complete API reference documentation.

## API Docs
API documentation and examples.

## Getting Started
- [Installation](/docs/install)
- [Authentication](/docs/auth)

## Endpoints
Available API endpoints.
- [Users](/api/users)
- [Posts](/api/posts)
```

In this example, the first three sections ("API", "API Reference", "API Docs") are problematic duplicates. An LLM agent must disambiguate which section contains what information.

## Remediation

1. **Audit section names**: List all H2 headers and identify near-duplicates or exact duplicates.
2. **Establish naming conventions**: Define clear, distinct names for each section based on canonical patterns (e.g., "Getting Started", "API Reference", "Examples", "Troubleshooting").
3. **Consolidate or rename**: 
   - Merge closely related duplicates into a single section, or
   - Rename each to reflect distinct purposes (e.g., "API Overview" vs. "API Reference" vs. "API Examples")
4. **Validate uniqueness**: Ensure all section names are unique after normalization (lowercase, stripped whitespace).

**Remediated Example:**

```markdown
# API Documentation

## Overview
Basic overview of our API and key concepts.
- [What is our API?](/docs/overview)
- [Authentication](/docs/auth)
- [Rate Limiting](/docs/rate-limit)

## Getting Started
Quick start guide for new users.
- [Installation](/docs/install)
- [First Request](/docs/first-request)
- [Examples](/docs/examples)

## API Reference
Complete endpoint documentation and specifications.
- [Users Endpoints](/api/users)
- [Posts Endpoints](/api/posts)
- [Response Formats](/api/responses)

## Troubleshooting
Common issues and solutions.
- [FAQ](/docs/faq)
- [Error Codes](/docs/errors)
```

## Affected Criteria

- **DS-VC-STR-009**: No Structural Anti-Patterns — Duplicate identities undermine structural clarity
- **DS-VC-CON-005**: No Duplicate Sections — Each section must have a unique, unambiguous identity

## Emitted Diagnostics

Scored through structural dimension evaluation. No specific diagnostic codes emitted; severity is reflected in overall structural score reduction.

## Related Anti-Patterns

- **DS-AP-STRUCT-005** (Naming Nebula) — Vague, non-standard naming makes duplicates more likely; duplicate naming is the extreme manifestation

## Change History

| Version | Date | Description |
|---------|------|-------------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.2 |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
