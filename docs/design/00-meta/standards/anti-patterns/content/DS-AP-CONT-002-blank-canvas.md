# DS-AP-CONT-002: Blank Canvas

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-AP-CONT-002 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Registry ID** | AP-CONT-002 |
| **Category** | Content |
| **Check ID** | CHECK-011 |
| **Severity Impact** | Reduce content dimension score |
| **Provenance** | v0.0.4c §Anti-Patterns Catalog |

## Description

Sections contain only placeholder text ("TODO", "Coming soon", "TBD", "Work in progress") or are essentially empty with minimal meaningful content. This anti-pattern indicates incomplete documentation where sections exist structurally but provide no value to readers or LLM agents. It represents a commitment debt — the documentation claims to address a topic but fails to deliver.

## Detection Logic

```python
def detect_blank_canvas(sections):
    """
    Detect placeholder sections with minimal content.
    
    Algorithm:
    1. Define placeholder patterns: ["TODO", "Coming soon", "TBD", "WIP", "placeholder"]
    2. For each section:
       a. Check if content matches placeholder patterns (case-insensitive)
       b. Check if content length < 20 characters
       c. Check if section has heading but no body
    3. Flag as anti-pattern if condition met
    
    Returns: list of (section_id, reason, content)
    """
    import re
    
    placeholder_pattern = r'\b(TODO|Coming soon|TBD|WIP|Work in progress|placeholder)\b'
    flagged = []
    
    for section_id, content in sections:
        stripped = content.strip()
        if re.search(placeholder_pattern, stripped, re.IGNORECASE):
            flagged.append((section_id, "contains_placeholder", stripped))
        elif len(stripped) < 20 and stripped != "":
            flagged.append((section_id, "insufficient_content", stripped))
    
    return len(flagged) > 0, flagged
```

## Example (Synthetic)

```markdown
## Authentication

TODO: Write authentication guide

## Data Storage

Coming soon.

## Error Handling

TBD
```

All three sections are flagged: they contain placeholder text with no substantive content, blocking LLM agents from understanding these topics.

## Remediation

1. Complete all sections before publishing documentation
2. If a topic is not ready, remove the section entirely rather than leaving a placeholder
3. Use editorial review to ensure no sections remain incomplete
4. For long-term projects, maintain a separate roadmap or tracking document for planned content
5. Implement CI checks to prevent placeholder text from entering production docs

## Affected Criteria

- DS-VC-APD-004 (Content must be substantive)
- DS-VC-CON-003 (No Placeholder Content — placeholder text must be removed)

## Emitted Diagnostics

- DS-DC-W011 (EMPTY_SECTIONS — warning for sections with insufficient content)

## Related Anti-Patterns

- DS-AP-CRIT-001 (Ghost File — file-level equivalent where entire files are placeholders)
- DS-AP-STRUCT-002 (Orphaned Sections — sections with no connection to parent structure)

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.2 |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
