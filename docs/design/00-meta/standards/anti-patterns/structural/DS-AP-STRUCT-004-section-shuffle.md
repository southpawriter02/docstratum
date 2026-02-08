# DS-AP-STRUCT-004: Section Shuffle

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-AP-STRUCT-004 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Registry ID** | AP-STRUCT-004 |
| **Category** | Structural |
| **Check ID** | CHECK-008 |
| **Severity Impact** | Reduce structural dimension score |
| **Provenance** | v0.0.4c §Anti-Patterns Catalog |

## Description

Sections in illogical order (e.g., Advanced Topics before Getting Started). Violates the canonical 10-step ordering sequence derived from frequency analysis of 450+ projects. When sections appear in non-canonical order, LLM agents and human readers navigate inefficiently, and onboarding flows break down. The canonical sequence reflects the natural progression from foundational to advanced content.

## Detection Logic

```python
def detect_section_shuffle(file_content):
    """
    Detects if sections are in illogical (non-canonical) order.
    
    Triggers if:
    - Map present sections to canonical positions (based on CANONICAL_POSITIONS dict)
    - Check if section order is monotonically non-decreasing
    - Count inversions (out-of-order pairs)
    - If inversions > 2, trigger
    """
    import re
    
    # Canonical section ordering (from frequency analysis of 450+ projects)
    CANONICAL_POSITIONS = {
        "master index": 1,
        "llm instructions": 2,
        "getting started": 3,
        "overview": 4,
        "installation": 5,
        "configuration": 6,
        "usage": 7,
        "examples": 8,
        "advanced topics": 9,
        "api reference": 10,
        "troubleshooting": 11,
        "faq": 12,
        "contributing": 13,
        "community": 14,
    }
    
    # Extract all H2 section headers in order
    h2_pattern = r'^## (.+)$'
    section_names = re.findall(h2_pattern, file_content, re.MULTILINE)
    
    if len(section_names) <= 1:
        return False, "Only 0 or 1 section found; no ordering issue"
    
    def normalize_name(name):
        """Normalize for matching against canonical names."""
        return name.lower().strip()
    
    # Map each present section to its canonical position
    section_positions = []
    for section_name in section_names:
        normalized = normalize_name(section_name)
        # Try exact match
        if normalized in CANONICAL_POSITIONS:
            pos = CANONICAL_POSITIONS[normalized]
        else:
            # Try partial matching (simple heuristic)
            pos = None
            for canonical, canonical_pos in CANONICAL_POSITIONS.items():
                if canonical in normalized or normalized in canonical:
                    pos = canonical_pos
                    break
            if pos is None:
                pos = 999  # Unknown sections go to end
        
        section_positions.append((section_name, pos))
    
    # Count inversions: pairs where position[i] > position[i+1]
    inversions = 0
    for i in range(len(section_positions) - 1):
        if section_positions[i][1] > section_positions[i + 1][1]:
            inversions += 1
    
    if inversions > 2:
        inv_details = "; ".join([
            f"{section_positions[i][0]} ({section_positions[i][1]}) before {section_positions[i+1][0]} ({section_positions[i+1][1]})"
            for i in range(len(section_positions) - 1)
            if section_positions[i][1] > section_positions[i + 1][1]
        ])
        return True, f"Section shuffle detected: {inversions} inversions found. {inv_details}"
    
    return False, "Sections are in logical order"
```

## Example (Synthetic)

```markdown
# Project Documentation

## Advanced Topics
Deep dives into advanced configuration and optimization.
- [Performance Tuning](/docs/perf)
- [Custom Extensions](/docs/extensions)

## Getting Started
Introduction to the project.
- [Installation](/docs/install)
- [Your First Project](/docs/first-project)

## API Reference
Complete API documentation.
- [Endpoints](/api/endpoints)

## Overview
What is this project?
- [Project Description](/docs/about)
```

This document violates canonical ordering: "Advanced Topics" should come AFTER "Getting Started", "Overview", and "Installation".

## Remediation

1. **Identify canonical sequence**: Reference the canonical 10-step ordering:
   1. Master Index
   2. LLM Instructions
   3. Getting Started
   4. Overview
   5. Installation
   6. Configuration
   7. Usage
   8. Examples
   9. Advanced Topics
   10. API Reference
   11. Troubleshooting / FAQ
   12. Contributing / Community

2. **Audit current order**: List sections as they appear and map to canonical positions.

3. **Reorder sections**: Reorganize markdown file to match canonical progression.

4. **Update internal links**: Ensure any cross-references between sections still point to the correct locations.

**Remediated Example:**

```markdown
# Project Documentation

## Overview
What is this project?
- [Project Description](/docs/about)
- [Key Features](/docs/features)

## Getting Started
Introduction and quick setup.
- [Installation](/docs/install)
- [Your First Project](/docs/first-project)
- [Basic Configuration](/docs/basic-config)

## Usage
How to use the project.
- [Core Concepts](/docs/concepts)
- [Common Tasks](/docs/tasks)

## Examples
Real-world usage examples.
- [Web Application](/docs/example-web)
- [CLI Tool](/docs/example-cli)

## Configuration
Detailed configuration reference.
- [Config Options](/docs/config-ref)
- [Advanced Settings](/docs/advanced-config)

## Advanced Topics
Deep dives and optimization.
- [Performance Tuning](/docs/perf)
- [Custom Extensions](/docs/extensions)

## API Reference
Complete API documentation.
- [Endpoints](/api/endpoints)
- [Authentication](/api/auth)

## Troubleshooting
Common issues and solutions.
- [FAQ](/docs/faq)
- [Error Codes](/docs/errors)

## Contributing
How to contribute.
- [Contribution Guide](/docs/contributing)
```

## Affected Criteria

- **DS-VC-STR-009**: No Structural Anti-Patterns — Section shuffle violates structural integrity
- **DS-VC-STR-007**: Canonical Section Ordering — Sections must follow the established canonical sequence

## Emitted Diagnostics

- **DS-DC-W008** (SECTION_ORDER_NON_CANONICAL) — Triggered when inversions exceed threshold

## Related Anti-Patterns

- **DS-AP-STRUCT-005** (Naming Nebula) — Non-standard section names make canonical ordering difficult to enforce

## Change History

| Version | Date | Description |
|---------|------|-------------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.2 |
