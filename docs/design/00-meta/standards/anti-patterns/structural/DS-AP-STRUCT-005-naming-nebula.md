# DS-AP-STRUCT-005: Naming Nebula

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-AP-STRUCT-005 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Registry ID** | AP-STRUCT-005 |
| **Category** | Structural |
| **Check ID** | CHECK-009 |
| **Severity Impact** | Reduce structural dimension score |
| **Provenance** | v0.0.4c §Anti-Patterns Catalog |

## Description

Section names that are vague, inconsistent, or non-standard. Uses names like "Stuff", "Misc", "Other" instead of the 11 canonical names (Master Index, LLM Instructions, Getting Started, etc.). Makes navigation unpredictable for LLM agents. When section headers lack semantic clarity or deviate from established canonical names, knowledge graphs become fragmented, and agents cannot reliably predict content location across different documentation sets.

## Detection Logic

```python
def detect_naming_nebula(file_content):
    """
    Detects sections with vague, non-standard, or non-canonical names.
    
    Triggers if:
    - For each H2 section name, check if it matches any of the 11 CanonicalSectionNames
      or their aliases in SECTION_NAME_ALIASES
    - If non_canonical_count / total_sections > 0.5, trigger
    """
    import re
    
    # 11 Canonical section names
    CANONICAL_NAMES = {
        "master index",
        "llm instructions",
        "getting started",
        "overview",
        "installation",
        "configuration",
        "usage",
        "examples",
        "advanced topics",
        "api reference",
        "troubleshooting",
    }
    
    # 32 Common aliases and variations
    SECTION_NAME_ALIASES = {
        # Getting Started variants
        "quick start", "quickstart", "quick-start", "start", "introduction", "intro",
        "setup", "initial setup", "first steps",
        # Overview variants
        "about", "introduction", "what is", "overview",
        # Installation variants
        "install", "installation", "download", "setup",
        # Configuration variants
        "config", "settings", "configuration", "customize",
        # Usage variants
        "guide", "how to", "tutorials", "usage", "use cases",
        # Examples variants
        "samples", "examples", "recipes", "code samples",
        # Advanced variants
        "advanced", "deep dive", "internals", "architecture",
        # API variants
        "api", "endpoints", "reference", "sdk",
        # Troubleshooting variants
        "troubleshoot", "debug", "common issues", "faq",
        # Contributing variants
        "contribute", "contributing", "development",
        # Community variants
        "community", "support", "help", "resources",
    }
    
    # Extract all H2 section headers
    h2_pattern = r'^## (.+)$'
    section_names = re.findall(h2_pattern, file_content, re.MULTILINE)
    
    if len(section_names) == 0:
        return False, "No H2 sections found"
    
    def normalize_name(name):
        """Normalize for matching."""
        return name.lower().strip()
    
    def is_canonical_or_aliased(name):
        """Check if name is canonical or in aliases."""
        normalized = normalize_name(name)
        
        # Check if it's in canonical names
        if normalized in CANONICAL_NAMES:
            return True
        
        # Check if it's in aliases
        if normalized in SECTION_NAME_ALIASES:
            return True
        
        # Check for partial matches (e.g., "Getting Started" in "Getting Started Guide")
        for alias in SECTION_NAME_ALIASES:
            if alias in normalized or normalized in alias:
                return True
        
        return False
    
    # Count non-canonical sections
    non_canonical_count = 0
    non_canonical_sections = []
    
    for section_name in section_names:
        if not is_canonical_or_aliased(section_name):
            non_canonical_count += 1
            non_canonical_sections.append(section_name)
    
    non_canonical_ratio = non_canonical_count / len(section_names) if len(section_names) > 0 else 0
    
    if non_canonical_ratio > 0.5:
        return True, f"Naming nebula detected: {non_canonical_count}/{len(section_names)} sections have non-canonical names. Sections: {non_canonical_sections}"
    
    if non_canonical_ratio > 0.25:
        return True, f"Naming nebula detected (borderline): {non_canonical_count}/{len(section_names)} sections have non-canonical names. Sections: {non_canonical_sections}"
    
    return False, "Section names are adequately canonical"
```

## Example (Synthetic)

```markdown
# Our Documentation

## Stuff
Random collection of things.
- [Something](/docs/something)
- [Another Thing](/docs/another)

## Misc
Miscellaneous information.
- [Info](/docs/info)

## Other Stuff
More random content.

## Getting Started
Quick introduction.
- [Installation](/docs/install)

## Weird Section Title
Help and troubleshooting info.
- [FAQ](/docs/faq)
- [Support](/docs/support)
```

In this example, "Stuff", "Misc", "Other Stuff", and "Weird Section Title" are all non-canonical names that make navigation unpredictable.

## Remediation

1. **Audit section names**: List all H2 headers and classify each as canonical or non-canonical.

2. **Map to canonical names**: For each non-canonical section, determine which canonical name it best aligns with:
   - "Stuff" → "Overview" or "Getting Started"
   - "Misc" → "Examples" or "Usage"
   - "Other Stuff" → "Advanced Topics" or domain-specific canonical name

3. **Rename systematically**: Update section headers to use canonical or approved alias names.

4. **Document local variations**: If domain-specific names are necessary, document them in a style guide and ensure they appear consistently.

**Remediated Example:**

```markdown
# Our Documentation

## Overview
Introduction to our platform and core concepts.
- [What We Do](/docs/about)
- [Key Features](/docs/features)

## Getting Started
Quick setup and first steps.
- [Installation](/docs/install)
- [Your First Project](/docs/first-project)

## Usage
How to use the platform effectively.
- [Common Tasks](/docs/tasks)
- [Workflows](/docs/workflows)

## Examples
Real-world use cases and recipes.
- [Web Application Example](/docs/example-web)
- [CLI Tool Example](/docs/example-cli)
- [Advanced Scenario](/docs/example-advanced)

## Troubleshooting
Help, FAQs, and support.
- [FAQ](/docs/faq)
- [Common Issues](/docs/issues)
- [Support Contacts](/docs/support)

## Advanced Topics
Deep dives and optimization guides.
- [Architecture](/docs/architecture)
- [Performance Tuning](/docs/perf)
```

## Affected Criteria

- **DS-VC-STR-009**: No Structural Anti-Patterns — Non-canonical naming undermines structural clarity
- **DS-VC-CON-008**: Canonical Section Names — Section headers must use canonical or standardized names

## Emitted Diagnostics

- **DS-DC-W002** (NON_CANONICAL_SECTION_NAME) — Triggered when non-canonical section name ratio exceeds threshold

## Related Anti-Patterns

- **DS-AP-STRUCT-004** (Section Shuffle) — Canonical ordering is only effective when section names are canonical
- **DS-AP-STRUCT-003** (Duplicate Identity) — Non-canonical names increase the likelihood of duplicates and confusion

## Change History

| Version | Date | Description |
|---------|------|-------------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.2 |
