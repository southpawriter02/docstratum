# DS-AP-CRIT-002: Structure Chaos

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-AP-CRIT-002 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Registry ID** | AP-CRIT-002 |
| **Category** | Critical |
| **Check ID** | CHECK-002 (v0.0.4c) |
| **Severity Impact** | Gate structural score at 29 — total quality score capped regardless of other dimensions |
| **Provenance** | v0.0.4c §Anti-Patterns Catalog; v0.0.2c audit data |

## Description

File lacks recognizable Markdown structure (no headers, no sections). Raw text dump or HTML-only content that a Markdown parser cannot navigate. An LLM agent cannot extract structured information from such a file.

## Detection Logic

```python
def detect_structure_chaos(file_content: str) -> bool:
    """
    Detect absence of Markdown structure.
    
    Returns True if:
    - Zero H1 headings AND zero H2 headings present, OR
    - >80% of content is HTML tags rather than Markdown
    """
    h1_count = file_content.count("# ")
    h2_count = file_content.count("## ")
    
    if h1_count == 0 and h2_count == 0:
        return True
    
    html_tag_count = len(re.findall(r"<[^>]+>", file_content))
    total_chars = len(file_content)
    html_ratio = html_tag_count / total_chars if total_chars > 0 else 0
    
    return html_ratio > 0.80
```

## Example (Synthetic)

```
This is a documentation file about something important.
It contains only plain text paragraphs without any structure.
There are no headings, no sections, no links, nothing organized.
Just raw content dumped into a file without proper formatting.
A Markdown parser would struggle to extract meaningful structure.
An LLM agent cannot navigate this to understand document organization.
```

## Remediation

Add at minimum an H1 title and one H2 section with links. Structure content hierarchically:

1. Add H1 title at the top
2. Divide content into H2 sections
3. Add internal links where appropriate
4. Use list formatting for enumerated items
5. Add code blocks where code is present

## Affected Criteria

- DS-VC-STR-008 (No Critical Anti-Patterns)
- DS-VC-STR-001 (H1 Title Present)
- DS-VC-STR-004 (H2 Section Structure)

## Emitted Diagnostics

- **DS-DC-E001**: NO_H1_TITLE — when no H1 found

## Related Anti-Patterns

- DS-AP-CRIT-001 (Ghost File — empty vs structureless are related failure modes)
- DS-AP-STRUCT-002 (Orphaned Sections — partial structure vs no structure)

## Change History

| ASoT Version | Date | Change |
|---|---|---|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.2 |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
