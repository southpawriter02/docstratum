# Layer 0: Metadata & File Skeleton

> **Core Purpose:** Establish the structural foundation of an llms.txt file through metadata headers, YAML skeleton definition, extended DocStratum metadata fields, and template generation automation. This layer ensures every llms.txt instance is machine-parseable, version-controlled, and traceable to its source documentation site.

## Objective

Create a standardized, production-ready file skeleton that:
- Defines the YAML frontmatter structure with validation rules for all metadata fields
- Establishes consistent comment conventions and section separators
- Implements DocStratum extended metadata (token estimates, cache TTL, maintainer tracking)
- Provides automated template generation from audit data
- Enables version control and diff-friendly formatting

## Scope Boundaries

**IN:**
- YAML file structure and comment conventions
- Metadata header design (schema_version, site_name, site_url, last_updated)
- Extended DocStratum metadata fields (token_estimate, has_full_version, maintainer, language, cache_ttl)
- File template generator (Python script)
- YAML style guide (quoting, multiline strings, dates, URLs)
- Version control strategy and commit message patterns
- Complete YAML examples of metadata sections

**OUT:**
- Page entry validation logic (covered in Layer 1)
- Concept graph construction (covered in Layer 2)
- Few-shot example quality assessment (covered in Layer 3)
- Site audit/discovery process (v0.2.2 responsibility)
- LLM training or fine-tuning procedures

## Dependency Diagram

```
┌─────────────────────────────────────────┐
│   v0.2.2 Site Audit & Data Preparation │
│   (produces: pages.json, concepts.json) │
└────────────────┬────────────────────────┘
                 │
                 ↓
    ┌────────────────────────────────────┐
    │   Layer 0: Metadata & Skeleton     │ ← YOU ARE HERE
    │   ├─ YAML structure definition     │
    │   ├─ Metadata field validation     │
    │   ├─ Template generator script     │
    │   └─ File skeleton creation        │
    └────────────┬───────────────────────┘
                 │
                 ↓
    ┌────────────────────────────────────┐
    │  Layer 1: Page Entries             │
    │  (CanonicalPage YAML authoring)    │
    └────────────────────────────────────┘
                 │
                 ↓
    ┌────────────────────────────────────┐
    │  Layer 2: Concept Entries          │
    │  (Concept graph YAML encoding)     │
    └────────────────────────────────────┘
                 │
                 ↓
    ┌────────────────────────────────────┐
    │  Layer 3: Few-Shot Examples        │
    │  (FewShotExample YAML & QA)        │
    └────────────────────────────────────┘
                 │
                 ↓
    ┌────────────────────────────────────┐
    │  Final llms.txt (v0.2.3 artifact)  │
    └────────────────────────────────────┘
```

---

## 1. File Structure & Comment Conventions

### 1.1 Top-Level File Layout

Every llms.txt file follows this structure:

```
[YAML Frontmatter Block]
[Blank Line]
# Metadata Section Comment
[Metadata fields]

# Pages Section Comment
[Pages array]

# Concepts Section Comment
[Concepts array]

# Few-Shot Examples Section Comment
[Few-shot examples array]
```

### 1.2 Comment Conventions

Use these patterns consistently:

| Type | Pattern | Example | Usage |
|------|---------|---------|-------|
| Section Header | `# [Section Name] Section` | `# Pages Section` | Separates major YAML sections |
| Subsection | `# [Detail]` | `# Dependency Graph Entries` | Organizes entries within sections |
| Field Explanation | `# [Field]: [brief rule]` | `# url: must include protocol` | Clarifies individual field constraints |
| Validation Note | `# @validate: [rule]` | `# @validate: length < 280` | Marks fields requiring validation |
| Version Note | `# @version: [semver]` | `# @version: >=0.2.3` | Indicates minimum schema version |

### 1.3 Section Separator Pattern

Use consistent delimiters between major sections:

```yaml
# ============================================================================
# PAGES SECTION
# ============================================================================
# @validate: array of CanonicalPage objects
# @version: >=0.2.0

pages:
  - url: ...
    title: ...

# ============================================================================
# CONCEPTS SECTION
# ============================================================================
# @validate: array of Concept objects
# @version: >=0.2.0

concepts:
  - id: ...
    name: ...
```

---

## 2. YAML Frontmatter Design & Validation

### 2.1 Core Metadata Fields

The mandatory frontmatter appears at the top of every llms.txt file:

```yaml
# ============================================================================
# LLMS.TXT METADATA & VERSION CONTROL
# ============================================================================

schema_version: "0.2.3"
site_name: "Django Documentation"
site_url: "https://docs.djangoproject.com/"
last_updated: "2025-02-05"
```

### 2.2 Field Validation Rules

| Field | Type | Validation Rule | Example | Error Handling |
|-------|------|-----------------|---------|-----------------|
| `schema_version` | string | SemVer format (major.minor.patch) | `"0.2.3"` | Reject if not X.Y.Z |
| `site_name` | string | 3-100 chars, no leading/trailing spaces | `"Django Documentation"` | Trim and validate length |
| `site_url` | URL (HttpUrl) | HTTPS required, trailing slash optional | `"https://docs.django.io/"` | Normalize: convert HTTP→HTTPS if applicable |
| `last_updated` | date | ISO 8601 (YYYY-MM-DD), must be ≤ today | `"2025-02-05"` | Reject if future date |

### 2.3 Validation Code (Python/Pydantic)

```python
from pydantic import BaseModel, HttpUrl, Field, validator
from datetime import date

class LlmsTxtMetadata(BaseModel):
    schema_version: str = Field(..., regex=r'^\d+\.\d+\.\d+$')
    site_name: str = Field(..., min_length=3, max_length=100)
    site_url: HttpUrl
    last_updated: date

    @validator('site_name')
    def validate_site_name(cls, v):
        """Remove leading/trailing whitespace."""
        return v.strip()

    @validator('last_updated')
    def validate_last_updated(cls, v):
        """Ensure date is not in the future."""
        if v > date.today():
            raise ValueError(f"last_updated ({v}) cannot be in the future")
        return v

    @validator('site_url', pre=True)
    def validate_site_url(cls, v):
        """Normalize HTTP to HTTPS."""
        v_str = str(v)
        if v_str.startswith("http://"):
            v_str = v_str.replace("http://", "https://", 1)
        return v_str
```

---

## 3. Extended DocStratum Metadata Fields

### 3.1 Gap Analysis: v0.0.1b Requirements

The initial DocStratum gap analysis identified these extended fields needed for production use:

| Field | Purpose | Type | Required? | Example |
|-------|---------|------|-----------|---------|
| `token_estimate` | Approx. token count for LLM context | integer | No | `45000` |
| `has_full_version` | Indicates if full site snapshot exists | boolean | No | `true` |
| `maintainer` | Contact/team responsible for file | string | No | `"AI Docs Team"` |
| `language` | Primary documentation language | string | Yes | `"en"` |
| `cache_ttl` | Seconds before re-fetch recommended | integer | No | `604800` |

### 3.2 Extended Metadata Block (Full Example)

```yaml
# ============================================================================
# LLMS.TXT CORE METADATA
# ============================================================================

schema_version: "0.2.3"
site_name: "Django Documentation"
site_url: "https://docs.djangoproject.com/"
last_updated: "2025-02-05"

# ============================================================================
# DOCSTRATUM EXTENDED METADATA (v0.0.1b+)
# ============================================================================
# @validate: token_estimate > 0, cache_ttl in range [3600, 31536000]
# @version: >=0.2.3

token_estimate: 45000
has_full_version: true
maintainer: "django-foundation/docs-team"
language: "en"
cache_ttl: 604800  # 7 days in seconds
```

### 3.3 Field Validation Details

**token_estimate:**
- Range: 1 - 1,000,000
- Calculated: token count of all page + concept + few-shot content combined
- Tool: Use tiktoken with `cl100k_base` encoding
- Calculation script (see Section 5)

**has_full_version:**
- Boolean: whether a complete snapshot of the entire site exists
- Impacts: how aggressively the llms.txt can be cached
- If false: more frequent re-fetches recommended

**maintainer:**
- Format: `"organization/team"` or email
- Purpose: Tracking responsibility for updates
- Validation: Must be non-empty string

**language:**
- ISO 639-1 code (2-3 chars)
- Examples: `"en"`, `"es"`, `"fr"`, `"de"`
- Validation: Must match ISO standard list

**cache_ttl:**
- Range: 3600 (1 hour) - 31536000 (1 year)
- Interpretation: How many seconds before re-fetch is recommended
- Default: 604800 (7 days)
- Validation: must be positive integer, within range

---

## 4. YAML Style Guide

### 4.1 Quoting Rules

| Content | Rule | Example | Note |
|---------|------|---------|------|
| Simple strings (alphanumeric) | Unquoted | `title: Getting Started` | No quotes needed |
| Strings with spaces | Quoted | `title: "Getting Started Tutorial"` | Use double quotes |
| Strings with special chars | Quoted | `content_type: "how-to"` | Hyphen OK unquoted if no spaces |
| URLs | Quoted | `url: "https://example.com/page"` | Always quote URLs |
| Numbers that are not numeric | Quoted | `version: "2.0"` | Quote if semantically a string |
| Empty/null values | Unquoted | `optional_field:` or `optional_field: null` | Explicit null preferred |

### 4.2 Multiline Strings

For summaries and definitions (>100 chars):

```yaml
# Literal block (preserves newlines) - use for code/structured text
definition: |
  A concept is a semantic unit that groups related documentation pages.
  It encodes domain knowledge about how ideas connect and depend on each other.
  Dependencies are directional: A depends_on B means understanding B first helps understand A.

# Folded block (folds newlines to spaces) - use for prose
summary: >
  This page explains how to configure authentication in Django REST Framework.
  It covers token-based auth, session auth, and custom authentication schemes.
```

**Key Rules:**
- `|` = literal block scalar (preserve newlines)
- `>` = folded block scalar (newlines → spaces)
- Indent content 2 spaces from the `|` or `>`
- Keep lines ≤ 120 characters for readability

### 4.3 Date Format

Always use ISO 8601:
```yaml
last_updated: "2025-02-05"  # YYYY-MM-DD, quoted
```

**Why quoted?** YAML parsers may interpret `2025-02-05` as a float (2025.02 minus 05). Quoting ensures string preservation.

### 4.4 URL Format

Always use complete URLs with protocol:

```yaml
url: "https://example.com/docs/page/"  # Include protocol, prefer HTTPS
site_url: "https://example.com/"       # Include trailing slash for domains
```

**Normalization Rules:**
1. Remove duplicate trailing slashes: `https://example.com///` → `https://example.com/`
2. Preserve single trailing slash for domain URLs
3. Preserve path structure (no trailing slash removal from paths)
4. No query parameters in canonical pages (covered in Layer 1)

### 4.5 Comment Pattern Standards

```yaml
# Standard comment (above field, explaining purpose)
summary: "..."

# Inline comment (after field, indicating constraint)
last_updated: "2025-02-05"  # Must be ≤ today's date

# Validation comment (flagging QA requirement)
summary: "..."  # @validate: length ≤ 280
```

---

## 5. File Template Generator Script

### 5.1 Input Data Structure

The generator consumes v0.2.2 audit output:

```json
{
  "audit_metadata": {
    "site_name": "Django Documentation",
    "site_url": "https://docs.djangoproject.com/",
    "audit_date": "2025-02-05",
    "maintainer": "django-foundation/docs-team"
  },
  "pages_summary": {
    "total_count": 150,
    "by_type": {"tutorial": 45, "reference": 80, "faq": 25},
    "total_tokens": 45000
  },
  "concepts_summary": {
    "total_count": 35
  }
}
```

### 5.2 Generator Script (Python)

```python
#!/usr/bin/env python3
"""
DocStratum LLMS.txt Template Generator (v0.2.3)

Usage:
    python generate_template.py --audit-data audit_output.json --output llms.txt

Input:
    Audit JSON from v0.2.2 site audit
Output:
    Pre-populated llms.txt skeleton with metadata, placeholders for pages/concepts/few-shots
"""

import json
import argparse
from datetime import date
from pathlib import Path
from typing import Dict, Any

YAML_TEMPLATE = '''# ============================================================================
# LLMS.TXT METADATA & VERSION CONTROL
# ============================================================================

schema_version: "0.2.3"
site_name: "{site_name}"
site_url: "{site_url}"
last_updated: "{last_updated}"

# ============================================================================
# DOCSTRATUM EXTENDED METADATA (v0.0.1b+)
# ============================================================================
# Token estimate calculated from page content + concept definitions + examples
# Cache TTL: 7 days (604800 seconds) — adjust based on update frequency

token_estimate: {token_estimate}
has_full_version: true
maintainer: "{maintainer}"
language: "en"
cache_ttl: 604800

# ============================================================================
# PAGES SECTION
# ============================================================================
# @validate: array of CanonicalPage objects
# @version: >=0.2.0
# Statistics: {pages_count} total pages ({pages_by_type})

pages:
  # Generated {pages_count} page entries — see Layer 1 for authoring guide
  # Placeholder entries below (replace with actual content from audit)
  - url: "PLACEHOLDER_URL_1"
    title: "PLACEHOLDER_TITLE_1"
    content_type: "tutorial"
    last_verified: "{date_today}"
    summary: "PLACEHOLDER: Write 280-char max summary — see Layer 1 guide"

  - url: "PLACEHOLDER_URL_2"
    title: "PLACEHOLDER_TITLE_2"
    content_type: "reference"
    last_verified: "{date_today}"
    summary: "PLACEHOLDER: Write 280-char max summary — see Layer 1 guide"

# [Continue with remaining {pages_remaining} page entries...]
# Follow ordering strategy: group by content_type, then alphabetical

# ============================================================================
# CONCEPTS SECTION
# ============================================================================
# @validate: array of Concept objects
# @version: >=0.2.0
# Statistics: {concepts_count} total concepts

concepts:
  # Generated {concepts_count} concept entries — see Layer 2 for authoring guide
  # Placeholder entries below (replace with actual content from audit)
  - id: "placeholder-concept-1"
    name: "Placeholder Concept 1"
    definition: >
      PLACEHOLDER: Write concept definition that explains what this concept means
      in the context of the documentation site. Should be 1-3 sentences.
    related_pages:
      - "PLACEHOLDER_URL_1"
      - "PLACEHOLDER_URL_2"
    depends_on: []
    anti_patterns:
      - "PLACEHOLDER: Common mistake or misunderstanding"

  - id: "placeholder-concept-2"
    name: "Placeholder Concept 2"
    definition: >
      PLACEHOLDER: Write concept definition.
    related_pages:
      - "PLACEHOLDER_URL_1"
    depends_on:
      - "placeholder-concept-1"
    anti_patterns: []

# [Continue with remaining {concepts_remaining} concept entries...]
# Follow ordering: topological sort by depends_on, then alphabetical

# ============================================================================
# FEW-SHOT EXAMPLES SECTION
# ============================================================================
# @validate: array of FewShotExample objects
# @version: >=0.2.0
# Placeholder structure only — see Layer 3 for design methodology

few_shot_examples:
  - intent: "getting-started"
    question: "PLACEHOLDER: How do I get started with [topic]?"
    ideal_answer: "PLACEHOLDER: Step-by-step answer with code examples if applicable"
    source_pages:
      - "PLACEHOLDER_URL_1"

  - intent: "how-to"
    question: "PLACEHOLDER: How do I accomplish [specific task]?"
    ideal_answer: "PLACEHOLDER: Step-by-step procedural answer"
    source_pages:
      - "PLACEHOLDER_URL_1"
      - "PLACEHOLDER_URL_2"

  - intent: "troubleshooting"
    question: "PLACEHOLDER: I'm getting [error]. What's wrong?"
    ideal_answer: "PLACEHOLDER: Diagnosis and solution"
    source_pages:
      - "PLACEHOLDER_URL_1"

# [Continue with remaining few-shot examples...]
# Target: 3-5 examples per intent type (getting-started, how-to, troubleshooting, etc.)
'''

def parse_pages_by_type(audit_data: Dict[str, Any]) -> str:
    """Format pages breakdown for display."""
    by_type = audit_data.get("pages_summary", {}).get("by_type", {})
    parts = [f"{k}={v}" for k, v in sorted(by_type.items())]
    return ", ".join(parts)

def generate_template(audit_file: str, output_file: str):
    """Generate llms.txt skeleton from audit data."""
    with open(audit_file, 'r') as f:
        audit = json.load(f)

    metadata = audit["audit_metadata"]
    pages_summary = audit["pages_summary"]
    concepts_summary = audit["concepts_summary"]

    context = {
        "site_name": metadata["site_name"],
        "site_url": metadata["site_url"],
        "last_updated": metadata["audit_date"],
        "date_today": str(date.today()),
        "token_estimate": pages_summary.get("total_tokens", 0),
        "maintainer": metadata.get("maintainer", "TEAM_NAME"),
        "pages_count": pages_summary["total_count"],
        "pages_by_type": parse_pages_by_type(audit),
        "pages_remaining": max(0, pages_summary["total_count"] - 2),
        "concepts_count": concepts_summary["total_count"],
        "concepts_remaining": max(0, concepts_summary["total_count"] - 2),
    }

    rendered = YAML_TEMPLATE.format(**context)

    with open(output_file, 'w') as f:
        f.write(rendered)

    print(f"✓ Generated skeleton: {output_file}")
    print(f"  Site: {context['site_name']}")
    print(f"  Pages: {context['pages_count']}")
    print(f"  Concepts: {context['concepts_count']}")
    print(f"  Token estimate: {context['token_estimate']}")
    print("\nNext steps:")
    print("  1. Replace PLACEHOLDER entries with actual content")
    print("  2. Follow Layer 1 guide for page authoring")
    print("  3. Follow Layer 2 guide for concept authoring")
    print("  4. Follow Layer 3 guide for few-shot examples")
    print("  5. Run: python validate_llms_txt.py --file llms.txt")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate llms.txt skeleton from audit data"
    )
    parser.add_argument(
        "--audit-data",
        required=True,
        help="Path to audit_output.json from v0.2.2"
    )
    parser.add_argument(
        "--output",
        default="llms.txt",
        help="Output file path (default: llms.txt)"
    )

    args = parser.parse_args()
    generate_template(args.audit_data, args.output)
```

### 5.3 Usage Example

```bash
# Assuming audit_output.json from v0.2.2 exists
python generate_template.py --audit-data audit_output.json --output llms.txt

# Output:
# ✓ Generated skeleton: llms.txt
#   Site: Django Documentation
#   Pages: 150
#   Concepts: 35
#   Token estimate: 45000
#
# Next steps:
#   1. Replace PLACEHOLDER entries with actual content
#   ...
```

---

## 6. Version Control Strategy for llms.txt Files

### 6.1 Git Workflow for llms.txt

The llms.txt file is version-controlled alongside documentation source:

```
repository/
├── docs/
│   ├── pages/
│   ├── llms.txt          ← Main production file (v0.2.3 artifact)
│   └── llms.txt.backup   ← Previous version (optional, for recovery)
└── .gitignore
    # llms.txt is TRACKED (unlike audit data)
```

### 6.2 Meaningful Commit Messages

Use this format for llms.txt commits:

```
Format:
  [LAYER] [ACTION]: [Brief description] [Scope marker]

Examples:
  L0 [metadata]: Update maintainer and cache_ttl values
  L1 [pages]: Add 12 new tutorial entries for v2.0 release
  L2 [concepts]: Refactor dependency graph — add 3 new concepts
  L3 [few-shot]: Expand troubleshooting examples (intent coverage 95%→100%)
  FULL [release]: Ship v0.2.3 llms.txt for production — all layers complete

Format Details:
  - [LAYER]: L0=Metadata, L1=Pages, L2=Concepts, L3=Few-shot, FULL=Release
  - [ACTION]: update|add|refactor|fix|ship
  - Scope: precise change area
  - Body: explain WHY (not WHAT) — what changed is in git diff
```

### 6.3 Diff-Friendly Formatting

To enable clear git diffs, follow these conventions:

**One page per block:**
```yaml
pages:
  - url: "https://example.com/page1/"
    title: "Title 1"
    content_type: "tutorial"
    last_verified: "2025-02-05"
    summary: "Summary text here"

  - url: "https://example.com/page2/"
    title: "Title 2"
    ...
```

**Benefits:**
- Git diff shows exactly which page entries changed
- Line-by-line comparison readable
- Merge conflicts easier to resolve

**Avoid:**
```yaml
pages: [
  {url: "...", title: "..."}, {url: "...", title: "..."}
]
```
(Flow-style YAML makes diffs unreadable)

### 6.4 Git Hooks for Validation

Add a pre-commit hook to validate llms.txt before commit:

```bash
#!/bin/bash
# .git/hooks/pre-commit

if git diff --cached --name-only | grep -q "llms.txt"; then
    echo "Validating llms.txt..."
    python validate_llms_txt.py --file llms.txt
    if [ $? -ne 0 ]; then
        echo "Validation failed. Fix errors and try again."
        exit 1
    fi
fi
exit 0
```

---

## Complete YAML Example: Fully Populated Metadata Section

```yaml
# ============================================================================
# LLMS.TXT METADATA & VERSION CONTROL
# ============================================================================
# This section establishes file identity, versioning, and cache behavior
# for the DocStratum semantic translation layer.

schema_version: "0.2.3"
site_name: "FastAPI Documentation"
site_url: "https://fastapi.tiangolo.com/"
last_updated: "2025-02-05"

# ============================================================================
# DOCSTRATUM EXTENDED METADATA (v0.0.1b+)
# ============================================================================
# Extended fields for production llms.txt management and LLM consumption.
# @validate: token_estimate > 0, cache_ttl in [3600, 31536000]
# @version: >=0.2.3

token_estimate: 52000
has_full_version: true
maintainer: "tiangolo/fastapi-docs-team"
language: "en"
cache_ttl: 604800

# ============================================================================
# USAGE NOTES FOR LLM AGENTS
# ============================================================================
# This llms.txt file is optimized for AI agent consumption via Claude and similar LLMs.
# - Total tokens: ~52,000 (fits within most context windows)
# - Update frequency: Weekly (cache_ttl=7 days recommended)
# - Last rebuild: 2025-02-05 (comprehensive site audit)
# - Maintenance: fastapi-docs-team reviews updates quarterly

# Key semantic sections:
#  1. pages[] — 45 CanonicalPage entries (tutorials, references, FAQs)
#  2. concepts[] — 28 Concept entries with dependency graph
#  3. few_shot_examples[] — 15 intent-based examples (getting-started, how-to, etc.)
#
# For integration guidance, see:
# https://docstratum.dev/integration/llms-txt-consumption

```

---

## Deliverables Checklist

- [ ] YAML metadata validation rules documented with examples
- [ ] File template generator script (generate_template.py) created and tested
- [ ] Template passes generation on real audit data (5+ test sites)
- [ ] YAML style guide with quoting/formatting rules finalized
- [ ] Extended DocStratum metadata fields (token_estimate, cache_ttl, etc.) defined
- [ ] Complete YAML example of metadata section (300+ chars)
- [ ] Git workflow and commit message patterns documented
- [ ] Pre-commit hook validation script created
- [ ] Diff-friendly formatting guidelines established
- [ ] All code examples tested and syntax-verified
- [ ] Documentation passes readability review (Flesch score ≥60)

---

## Acceptance Criteria

1. **Completeness:** All 6 sections present with 3+ examples each
2. **Validation:** Pydantic schema validates all metadata fields correctly
3. **Generation:** Template generator produces valid YAML for 5+ real sites
4. **Style Consistency:** All examples follow documented YAML style guide
5. **Git Integration:** Pre-commit hook catches validation errors 100% of time
6. **Clarity:** Layer 0 document is self-contained and requires no external references

---

## Next Step Pointer

→ **Layer 1: Page Entries & Summary Writing** (v0.2.3b)

Layer 1 consumes the skeleton created here and populates it with actual page entries. You will:
- Author CanonicalPage YAML for each discovered documentation page
- Apply the 280-character summary constraint with information density focus
- Classify content_type (tutorial, reference, concept, changelog, faq)
- Normalize URLs and validate page ordering
