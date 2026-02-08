# DS-AP-ECO-006: Orphan Nursery

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-AP-ECO-006 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Registry ID** | AP-ECO-006 |
| **Category** | Ecosystem |
| **Check ID** | CHECK-028 |
| **Severity Impact** | Ecosystem-level — affects EcosystemScore rather than per-file QualityScore |
| **Provenance** | v0.0.7 §6 (Ecosystem Anti-Patterns) |

## Description

An Orphan Nursery occurs when documentation files exist in the project but are not referenced from the main index (`llms.txt`). These content pages are present but invisible to LLM agents that rely on the index as their entry point. If more than 30% of discovered content is unreferenced, the ecosystem suffers from incomplete documentation discovery.

This is harmful to LLM agents because they operate within token budgets and follow navigation paths defined by the index. An agent that enters via the index will never discover orphaned content, even if it contains critical information. The orphaned files waste storage and may become stale or contradictory to indexed content. From the agent's perspective, they don't exist, creating a false sense that the documentation is complete when it is not.

## Detection Logic

```python
def detect_orphan_nursery(project_root: str, llms_txt_path: str) -> bool:
    """
    Detect if >30% of content files are not referenced from index.
    
    Returns True if (orphaned_count / discovered_count) > 0.30
    """
    if not file_exists(llms_txt_path):
        return False  # No index to compare against
    
    # Discover all content files in typical documentation directories
    doc_dirs = ['docs/', 'documentation/', 'guides/', 'content/']
    discovered_files = []
    for doc_dir in doc_dirs:
        if directory_exists(doc_dir):
            discovered_files.extend(find_markdown_files(doc_dir))
    
    if len(discovered_files) == 0:
        return False
    
    # Extract all referenced files from index
    index_content = read_file(llms_txt_path)
    referenced_files = extract_file_references(index_content)
    
    # Find orphaned files
    orphaned = set(discovered_files) - set(referenced_files)
    
    orphan_ratio = len(orphaned) / len(discovered_files)
    return orphan_ratio > 0.30
```

## Example (Synthetic)

Project structure:
```
project/
├── llms.txt                    # Index file
├── docs/
    ├── getting-started.md      # Referenced in index
    ├── api-reference.md        # Referenced in index
    ├── advanced-guide.md       # NOT referenced (orphaned)
    ├── troubleshooting.md      # NOT referenced (orphaned)
    ├── internal-design.md      # NOT referenced (orphaned)
    └── deprecated-old-guide.md # NOT referenced (orphaned)
```

llms.txt content:
```markdown
# Index
- [Getting Started](./docs/getting-started.md)
- [API Reference](./docs/api-reference.md)
```

Discovered files: 6
Referenced files: 2
Orphaned files: 4
Orphan ratio: 4/6 = 66.7% > 30%. Trigger.

## Remediation

1. **Discover orphaned files**: Use the detection logic to identify all unreferenced documentation.
2. **Review and categorize**: Determine whether orphaned files are:
   - Actively maintained but forgotten from index (add to index)
   - Deprecated or obsolete (remove or archive)
   - Internal or specialized (decide if they should be indexed)
3. **Update the index**: For files that should be discoverable, add links from llms.txt.
4. **Archive or remove**: For obsolete content, move to a separate `_archive/` directory or delete.
5. **Document rationale**: If some files intentionally remain hidden, document why and consider if this is the right approach.

## Affected Criteria

Ecosystem-level diagnostic — no per-file VC criterion. This anti-pattern affects EcosystemScore scoring, not individual QualityScore metrics.

## Emitted Diagnostics

- **DS-DC-E010** (ORPHANED_ECOSYSTEM_FILE) — Fired when content files exist but are not referenced from the index.

## Related Anti-Patterns

- **DS-AP-ECO-001** (Index Island) — No links at all vs. missing some links. Index Island is stricter; Orphan Nursery indicates partial referencing.
- **DS-AP-CRIT-001** (Ghost File) — Per-file pattern where a file exists but has no useful content. Orphan Nursery is about existence but lack of discoverability.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.2 |
