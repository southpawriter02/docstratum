# DS-AP-ECO-003: Shadow Aggregate

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-AP-ECO-003 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Registry ID** | AP-ECO-003 |
| **Category** | Ecosystem |
| **Check ID** | CHECK-025 |
| **Severity Impact** | Ecosystem-level — affects EcosystemScore rather than per-file QualityScore |
| **Provenance** | v0.0.7 §6 (Ecosystem Anti-Patterns) |

## Description

A Shadow Aggregate exists when `llms-full.txt` (the comprehensive aggregate file) contains content that doesn't match what the index (`llms.txt`) promises. The aggregate file may be missing sections that the index lists, or it may include sections not referenced from the index, creating an inconsistency between the declared and actual content.

This is harmful to LLM agents because they may choose to ingest either the index or the aggregate depending on token budget and context window. If these two files tell different stories about what content exists, the agent has no reliable source of truth. The agent may make incorrect decisions about what content is available, leading to incomplete exploration or wasted tokens on sections that don't exist in the aggregate.

## Detection Logic

```python
def detect_shadow_aggregate(llms_txt_path: str, llms_full_txt_path: str) -> bool:
    """
    Detect if llms-full.txt content doesn't match what llms.txt promises.
    
    Returns True if >30% of index sections are missing from aggregate
    (or vice versa: aggregate has sections not in index).
    """
    if not file_exists(llms_txt_path) or not file_exists(llms_full_txt_path):
        return False
    
    index_content = read_file(llms_txt_path)
    aggregate_content = read_file(llms_full_txt_path)
    
    index_sections = extract_section_headings(index_content)
    aggregate_sections = extract_section_headings(aggregate_content)
    
    # Calculate coverage mismatch
    missing_from_aggregate = set(index_sections) - set(aggregate_sections)
    extra_in_aggregate = set(aggregate_sections) - set(index_sections)
    
    max_sections = max(len(index_sections), len(aggregate_sections))
    if max_sections == 0:
        return False
    
    mismatch_count = len(missing_from_aggregate) + len(extra_in_aggregate)
    mismatch_ratio = mismatch_count / max_sections
    
    return mismatch_ratio > 0.30
```

## Example (Synthetic)

**llms.txt:**
```markdown
# Ecosystem Index

- [Introduction](./intro.md)
- [Getting Started](./getting-started.md)
- [API Reference](./api-reference.md)
- [Examples](./examples.md)
```

**llms-full.txt:**
```markdown
# Full Aggregate

## Introduction
Content from intro.md...

## Getting Started
Content from getting-started.md...

## Legacy Documentation (Deprecated)
Content from legacy guide...

# (Missing: API Reference and Examples)
```

In this example, the aggregate is missing "API Reference" and "Examples" (50% mismatch > 30% threshold). Trigger.

## Remediation

1. **Validate consistency**: After building aggregates, compare section headings from index to aggregate.
2. **Update the aggregate**: If content was recently added to the index, regenerate the aggregate or manually add the missing sections.
3. **Deprecate or remove**: If the aggregate is stale, either update it or remove the file to avoid confusion.
4. **Document versioning**: If the aggregate represents a snapshot from a previous release, clearly label it and don't mix it with the current index.
5. **Automate generation**: Use tooling to generate the aggregate automatically from the index to ensure consistency.

## Affected Criteria

Ecosystem-level diagnostic — no per-file VC criterion. This anti-pattern affects EcosystemScore scoring, not individual QualityScore metrics.

## Emitted Diagnostics

- **DS-DC-W014** (AGGREGATE_INCOMPLETE) — Fired when the aggregate file is missing content or is otherwise inconsistent.

## Related Anti-Patterns

- **DS-AP-ECO-001** (Index Island) — No aggregate or no links at all vs. mismatched aggregate. Both undermine ecosystem cohesion.
- **DS-AP-CRIT-002** (Stale Content) — Per-file pattern where content becomes outdated. Shadow Aggregate affects the aggregate file's consistency.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.2 |
