# DS-AP-ECO-001: Index Island

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-AP-ECO-001 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Registry ID** | AP-ECO-001 |
| **Category** | Ecosystem |
| **Check ID** | CHECK-023 |
| **Severity Impact** | Ecosystem-level — affects EcosystemScore rather than per-file QualityScore |
| **Provenance** | v0.0.7 §6 (Ecosystem Anti-Patterns) |

## Description

An Index Island occurs when `llms.txt` exists but contains no outbound links to content pages or aggregates. The index file is isolated, creating a dead-end entry point into the documentation ecosystem. LLM agents that follow the index discover zero paths forward, rendering the index structurally useless as a navigation device.

This is particularly harmful to LLM agents because they rely on the index as a discovery mechanism. If the index promises content but links nowhere, agents waste token budget attempting to parse a file that provides no directional guidance. The agent must either abandon the project or fallback to unstructured discovery, undermining the entire purpose of a structured ecosystem.

## Detection Logic

```python
def detect_index_island(llms_txt_path: str) -> bool:
    """
    Detect if llms.txt is an isolated island with no outbound links.
    
    Returns True if:
    - Total outbound links == 0, OR
    - All links are external URLs (no local content page references)
    """
    if not file_exists(llms_txt_path):
        return False  # Not an island if no index exists
    
    content = read_file(llms_txt_path)
    local_links = extract_local_links(content)  # Links like [text](file.md)
    
    if len(local_links) == 0:
        return True  # No local content references
    
    return False
```

## Example (Synthetic)

```markdown
# LLM Ecosystem Index

Welcome to our documentation. This index serves as your entry point.

## Overview

This project contains important documentation. For more information, 
visit our [external website](https://example.com).

---

*Index generated 2026-02-01*
```

In this example, `llms.txt` exists and is syntactically valid, but contains zero local references (e.g., no `[Documentation](docs/guide.md)` links). An LLM agent parsing this file learns nothing about the local content structure.

## Remediation

1. **Audit the index**: Ensure `llms.txt` contains at least one link to a local content file (e.g., `[Getting Started](./docs/getting-started.md)`).
2. **Add structural links**: Include links to key sections, guides, and API documentation that exist in the project.
3. **Validate links**: Before deployment, verify that all links in the index point to files that exist in the repository.
4. **Consider aggregates**: If the ecosystem is large, ensure `llms-full.txt` is referenced or generated to provide comprehensive coverage.

## Affected Criteria

Ecosystem-level diagnostic — no per-file VC criterion. This anti-pattern affects EcosystemScore scoring, not individual QualityScore metrics.

## Emitted Diagnostics

Related diagnostic codes:
- **DS-DC-E009** (NO_INDEX_FILE) — Fires when no index file exists at all. Index Island is the inverse: the index exists but is disconnected.

## Related Anti-Patterns

- **DS-AP-CRIT-001** (Ghost File) — Per-file pattern where a file exists but contains no useful content. Index Island affects the index file specifically.
- **DS-AP-ECO-006** (Orphan Nursery) — Content exists but isn't referenced. Index Island is stricter: no references at all.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.2 |
