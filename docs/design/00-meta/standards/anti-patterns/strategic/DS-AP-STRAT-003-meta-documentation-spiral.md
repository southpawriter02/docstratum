# DS-AP-STRAT-003: Meta-Documentation Spiral

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-AP-STRAT-003 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Registry ID** | AP-STRAT-003 |
| **Category** | Strategic |
| **Check ID** | CHECK-018 |
| **Severity Impact** | Deduction penalty — reduces anti-pattern detection dimension score |
| **Provenance** | v0.0.4c §Anti-Patterns Catalog |

## Description

Meta-Documentation Spiral occurs when a documentation file documents itself or the llms.txt standard rather than the actual project. Content explains what llms.txt is, how to write llms.txt files, or meta-commentary about the documentation format itself — instead of documenting the actual project's API, features, and usage. This creates a self-referential loop that wastes token budget and provides no value to users seeking to understand the project.

## Detection Logic

Scan for meta-references and measure content proportion:

```python
def detect_meta_documentation_spiral(content: str) -> bool:
    """
    Detects if content is meta-documentation rather than project documentation.
    Triggers if >30% of content contains meta-references.
    """
    meta_keywords = [
        "this llms.txt file",
        "this document describes",
        "llms.txt standard",
        "documentation format",
        "how to write",
        "this section explains",
        "the following section",
        "meta-commentary",
        "documentation itself"
    ]
    
    # Count lines containing meta-references
    lines = content.split('\n')
    meta_line_count = 0
    
    for line in lines:
        for keyword in meta_keywords:
            if keyword.lower() in line.lower():
                meta_line_count += 1
                break
    
    meta_ratio = meta_line_count / len(lines) if lines else 0
    
    return meta_ratio > 0.30
```

## Example (Synthetic)

```markdown
# Documentation Guide

This llms.txt file documents how to write llms.txt files.

## What is llms.txt?

The llms.txt standard is a way to document projects for language models.
This document describes the llms.txt format and how to use it.

## How to Write This Document

When you write this type of document, you should follow the llms.txt standard.
This section explains the meta-structure of such documentation.

## Document Structure

The following section describes the structure of documentation files like this one.
Each section should be written according to the llms.txt specification.

## More About Documentation Format

The documentation format used in this file follows best practices for the llms.txt
standard. This document itself is an example of such a file.
```

## Remediation

- Focus documentation on the **project**, not the documentation standard
- Document actual features, APIs, and workflows users care about
- Use only necessary meta-information (scope, audience) in headers
- Remove explanations of the llms.txt format from project documentation
- If documenting the standard itself, create a separate `/meta/` or `/standards/` directory
- Conduct content audits to identify self-referential passages and rewrite them to be user-focused

## Affected Criteria

- DS-VC-APD-005 (No Strategic Anti-Patterns)

## Emitted Diagnostics

None specific — scored through APD dimension.

## Related Anti-Patterns

- DS-AP-CONT-001 (Copy-Paste Plague — pasting llms.txt spec content)

## Change History

| ASoT Version | Date | Change |
|---|---|---|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.2 |
