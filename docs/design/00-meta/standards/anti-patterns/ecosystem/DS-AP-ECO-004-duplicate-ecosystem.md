# DS-AP-ECO-004: Duplicate Ecosystem

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-AP-ECO-004 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Registry ID** | AP-ECO-004 |
| **Category** | Ecosystem |
| **Check ID** | CHECK-026 |
| **Severity Impact** | Ecosystem-level — affects EcosystemScore rather than per-file QualityScore |
| **Provenance** | v0.0.7 §6 (Ecosystem Anti-Patterns) |

## Description

A Duplicate Ecosystem occurs when multiple `llms.txt` files exist in the same project root, creating ambiguity about which index file is authoritative. When an LLM agent enters a project, it needs a single, clear entry point. Multiple index files introduce uncertainty: Which index should the agent follow? Are they versions of each other? Are they intended for different audiences?

This is harmful to LLM agents because it violates the principle of single entry point. Instead of having a clear, canonical navigation path, the agent must guess or have heuristics to select the "correct" index. This burns tokens on disambiguation and introduces the risk that the agent follows a non-canonical or stale index, missing critical content or following outdated guidance.

## Detection Logic

```python
def detect_duplicate_ecosystem(project_root: str) -> bool:
    """
    Detect if multiple llms.txt files exist at project root.
    
    Returns True if count of llms*.txt files exceeds expected:
    - Expected: 1 (llms.txt) + optional 1 (llms-full.txt) + optional 1 (llms-instructions.txt)
    - More than 3 is always a duplicate.
    - Multiple primary indices (e.g., llms.txt and llms-v2.txt) trigger.
    """
    root_files = list_files(project_root)
    llms_pattern_files = [f for f in root_files if re.match(r'llms.*\.txt$', f)]
    
    # Filter for main indices (not just numbered variants)
    primary_indices = [f for f in llms_pattern_files 
                       if f in ['llms.txt', 'llms-full.txt', 'llms-instructions.txt']]
    
    # If we see unexpected variations (llms-v2.txt, llms-backup.txt, etc.), flag
    unexpected = [f for f in llms_pattern_files if f not in primary_indices]
    
    if len(unexpected) > 0:
        return True  # Unexpected variants detected
    
    return False  # Expected structure
```

## Example (Synthetic)

```
project-root/
├── llms.txt                    # Main index
├── llms-full.txt              # Aggregate (expected)
├── llms-v2.txt                # Alternate index (unexpected!)
├── llms-instructions.txt       # Instructions (expected)
└── docs/
    └── content.md
```

Three index files with different names create confusion. Which should an agent follow? Is `llms-v2.txt` outdated? Trigger.

## Remediation

1. **Audit existing indices**: Determine which index is authoritative and which are obsolete.
2. **Consolidate or remove**: If multiple indices exist for different purposes, rename them to fit the expected pattern (llms.txt, llms-full.txt, llms-instructions.txt).
3. **Document intent**: If intentional variants are necessary (e.g., for different LLM models), document this clearly and provide heuristics for selection.
4. **Archive old versions**: Move deprecated indices to an archive directory or prefix with `_deprecated-` to signal they should not be used.
5. **Enforce CI/CD**: Add a lint rule to prevent multiple indices from being committed.

## Affected Criteria

Ecosystem-level diagnostic — no per-file VC criterion. This anti-pattern affects EcosystemScore scoring, not individual QualityScore metrics.

## Emitted Diagnostics

No specific diagnostic code for this pattern. Flagged at the ecosystem level during scoring.

## Related Anti-Patterns

- **DS-AP-STRUCT-003** (Duplicate Identity) — Section-level duplication vs. file-level. Both create ambiguity about which version is canonical.
- **DS-AP-ECO-001** (Index Island) — Single malformed index vs. multiple indices. Both undermine clarity.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.2 |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
