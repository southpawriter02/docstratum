# DS-AP-STRUCT-002: Orphaned Sections

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-AP-STRUCT-002 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Registry ID** | AP-STRUCT-002 |
| **Category** | Structural |
| **Check ID** | CHECK-006 |
| **Severity Impact** | Reduce structural dimension score |
| **Provenance** | v0.0.4c §Anti-Patterns Catalog |

## Description

Sections with headers but no links or content. Empty H2 sections that exist as structural shells without useful content for LLM navigation. These orphaned sections create the illusion of organization while providing no actual navigational value or information, confusing agents about the true structure of the documentation.

## Detection Logic

```python
def detect_orphaned_sections(file_content):
    """
    Detects orphaned sections in a markdown file.
    
    Triggers if:
    - For each H2 section, check if it contains zero links AND content < 20 chars
    - If orphaned_count / total_sections > 0.5, trigger
    """
    import re
    
    # Split by H2 headers
    h2_pattern = r'^## (.+)$'
    sections = re.split(h2_pattern, file_content, flags=re.MULTILINE)
    
    # sections[0] is content before first H2, then alternates: [header, content, header, content, ...]
    total_sections = (len(sections) - 1) // 2
    if total_sections == 0:
        return False, "No H2 sections found"
    
    orphaned_count = 0
    orphaned_sections = []
    
    for i in range(1, len(sections), 2):
        section_header = sections[i]
        section_content = sections[i + 1] if i + 1 < len(sections) else ""
        
        # Check for links in this section
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        links = re.findall(link_pattern, section_content)
        link_count = len(links)
        
        # Check content length (stripped of whitespace)
        content_length = len(section_content.strip())
        
        # Orphaned if no links AND content < 20 chars
        if link_count == 0 and content_length < 20:
            orphaned_count += 1
            orphaned_sections.append(section_header.strip())
    
    orphan_ratio = orphaned_count / total_sections if total_sections > 0 else 0
    
    if orphan_ratio > 0.5:
        return True, f"Orphaned sections detected: {orphaned_count}/{total_sections} sections empty. Sections: {orphaned_sections}"
    
    return False, "No significant orphaned section pattern detected"
```

## Example (Synthetic)

```markdown
# Documentation

## Getting Started
Quick introduction to the project.
- [Installation Guide](/docs/install)
- [Quick Start](/docs/quickstart)

## Advanced Topics

## Configuration
Learn how to configure the system.
- [Configuration Reference](/docs/config)

## API Reference

## Troubleshooting
Common issues and solutions.
- [FAQ](/docs/faq)
- [Error Codes](/docs/errors)

## Community

## Contributing

```

In this example, the sections "Advanced Topics", "API Reference", "Community", and "Contributing" are all orphaned — they have no links and minimal or no content.

## Remediation

1. **Audit empty sections**: Review all H2 headers and identify which ones lack substantial content or links.
2. **Fill or remove**: For each orphaned section, either:
   - Add relevant links and descriptive content, or
   - Remove the header entirely if it's not needed
3. **Merge when appropriate**: If an orphaned section is closely related to an adjacent section, consider merging them.
4. **Ensure content thresholds**: Every section should contain either:
   - At least one link, OR
   - At least a brief description (50+ characters) explaining the section's purpose

**Remediated Example:**

```markdown
# Documentation

## Getting Started
Quick introduction to the project.
- [Installation Guide](/docs/install)
- [Quick Start](/docs/quickstart)

## Configuration & Advanced Topics
Learn how to configure and customize the system for advanced use cases.
- [Configuration Reference](/docs/config)
- [Advanced Configuration](/docs/advanced-config)
- [API Reference](/docs/api)

## Troubleshooting & Support
Common issues, solutions, and community resources.
- [FAQ](/docs/faq)
- [Error Codes](/docs/errors)
- [Discussions](https://github.com/org/repo/discussions)

## Contributing
We welcome contributions! Please read our contribution guidelines and community standards before submitting pull requests.
- [Contribution Guide](/docs/contributing)
- [Code of Conduct](/docs/conduct)
```

## Affected Criteria

- **DS-VC-STR-009**: No Structural Anti-Patterns — Orphaned sections violate structural integrity
- **DS-VC-CON-004**: Non-Empty Sections — All sections must contain meaningful content or links

## Emitted Diagnostics

- **DS-DC-W011** (EMPTY_SECTIONS) — Triggered when orphaned section count exceeds threshold

## Related Anti-Patterns

- **DS-AP-CRIT-001** (Ghost File) — File-level emptiness versus section-level emptiness; orphaned sections are a scaled version
- **DS-AP-CONT-002** (Blank Canvas) — Placeholder content versus no content at all

## Change History

| Version | Date | Description |
|---------|------|-------------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.2 |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
