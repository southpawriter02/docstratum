# DS-AP-CONT-001: Copy-Paste Plague

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-AP-CONT-001 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Registry ID** | AP-CONT-001 |
| **Category** | Content |
| **Check ID** | CHECK-010 |
| **Severity Impact** | Reduce content dimension score |
| **Provenance** | v0.0.4c §Anti-Patterns Catalog |

## Description

Large blocks of content are duplicated from other sources without curation or recontextualization. This anti-pattern represents a failure to synthesize and integrate external material into a cohesive documentation narrative. The documentation becomes bloated with redundant sections that provide no incremental value, and LLM agents must navigate through duplicative information to extract unique insights.

## Detection Logic

```python
def detect_copy_paste_plague(content_sections):
    """
    Detect large duplicated blocks using similarity hashing.
    
    Algorithm:
    1. Split content into sections (by ## or ###)
    2. For each section pair, compute content similarity hash
    3. If similarity > 0.60 (60% overlap), flag as duplicate
    4. Trigger anti-pattern if >1 pair detected
    
    Returns: list of (section_id1, section_id2, similarity_score)
    """
    import hashlib
    from difflib import SequenceMatcher
    
    similarities = []
    for i, section_a in enumerate(content_sections):
        for j, section_b in enumerate(content_sections[i+1:], start=i+1):
            ratio = SequenceMatcher(None, section_a, section_b).ratio()
            if ratio > 0.60:
                similarities.append((i, j, ratio))
    
    return len(similarities) > 0, similarities
```

## Example (Synthetic)

```markdown
## Getting Started

This section explains how to set up the project. First, clone the repository:
```bash
git clone https://github.com/example/project.git
cd project
npm install
```

Then configure your environment variables in a `.env` file.

## Quick Start Guide

This section explains how to set up the project. First, clone the repository:
```bash
git clone https://github.com/example/project.git
cd project
npm install
```

Then configure your environment variables in a `.env` file.
```

The "Getting Started" and "Quick Start Guide" sections are nearly identical (>90% overlap). This forces readers and agents to process redundant information.

## Remediation

1. Audit all documentation sections for content overlap
2. Consolidate duplicated material into a single, authoritative section
3. Link to that section from other related contexts rather than duplicating
4. Add unique context or examples to each section if multiple treatments are necessary
5. Document the intentional distinction between similar sections in a preamble

## Affected Criteria

- DS-VC-APD-004 (Content must be unique and non-redundant)

## Emitted Diagnostics

None specific; reported via general content quality metrics.

## Related Anti-Patterns

- DS-AP-STRAT-001 (Automation Obsession — automated content generation often produces copy-paste artifacts)

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.2 |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
