# v0.2.3 — YAML Authoring

> **Task:** Write the production `llms.txt` file for the target documentation site.
> 

---

## Task Overview

---

## Workflow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 1. Create   │───▶│ 2. Write    │───▶│ 3. Write    │───▶│ 4. Write    │
│   skeleton  │    │   pages     │    │   concepts  │    │   examples  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                │
                   ┌────────────────────────────────────────────┘
                   ▼
          ┌─────────────┐    ┌─────────────┐
          │ 5. Validate │───▶│ 6. Iterate  │
          │   schema    │    │   & refine  │
          └─────────────┘    └─────────────┘
```

---

## Writing Guidelines

### General

- Use 2-space indentation (YAML standard)
- Add comments for section headers
- Keep summaries under 280 characters
- Use consistent URL formats (no trailing slashes)

### Summaries (for pages)

- Start with a verb when possible
- Include the primary outcome
- Mention the target audience if specific
- Think "What will the reader learn?"

### Definitions (for concepts)

- Start with "[Concept name] is a..."
- One sentence only
- No pronouns (it, this, they)
- Domain-specific, not generic

### Ideal Answers (for few-shots)

- Structure with numbered steps
- Include code snippets when relevant
- Always cite source URLs
- End with warnings or notes if applicable

---

## YAML Skeleton

```yaml
# llms.txt — [SITE NAME]
# Generated: [DATE]
# Author: [YOUR NAME]

schema_version: "1.0"
site_name: "[SITE NAME]"
site_url: "[BASE URL]"
last_updated: "[YYYY-MM-DD]"

# ═══════════════════════════════════════════════════════════════════
# PAGES
# ═══════════════════════════════════════════════════════════════════

pages:
  # --- Tutorials ---
  - url: ""
    title: ""
    content_type: "tutorial"
    last_verified: ""
    summary: ""
  
  # --- References ---
  - url: ""
    title: ""
    content_type: "reference"
    last_verified: ""
    summary: ""
  
  # --- Concepts ---
  - url: ""
    title: ""
    content_type: "concept"
    last_verified: ""
    summary: ""

# ═══════════════════════════════════════════════════════════════════
# CONCEPTS
# ═══════════════════════════════════════════════════════════════════

concepts:
  - id: ""
    name: ""
    definition: ""
    related_pages: []
    depends_on: []
    anti_patterns: []

# ═══════════════════════════════════════════════════════════════════
# FEW-SHOT EXAMPLES
# ═══════════════════════════════════════════════════════════════════

few_shot_examples:
  - intent: ""
    question: ""
    ideal_answer: |
      [MULTI-LINE ANSWER]
    source_pages: []
```

---

## Quality Checklist

### Pages

- [ ]  At least 5 pages included
- [ ]  Mix of content types (tutorial, reference, concept)
- [ ]  All URLs are valid and accessible
- [ ]  Summaries are ≤280 characters
- [ ]  `last_verified` dates are accurate

### Concepts

- [ ]  At least 3 concepts defined
- [ ]  No pronouns in definitions
- [ ]  All `depends_on` IDs exist
- [ ]  At least 1 anti-pattern per concept
- [ ]  Related pages are linked

### Few-Shot Examples

- [ ]  At least 2 examples included
- [ ]  Questions reflect real user needs
- [ ]  Answers follow consistent format
- [ ]  Source pages are cited
- [ ]  Code snippets are syntactically valid

---

## Common YAML Errors

---

## Validation Command

```bash
# Validate after each major section
python validate.py data/llms.txt

# Expected output:
# ✅ Valid llms.txt file!
#    Site: [Your Site Name]
#    Pages: 5+
#    Concepts: 3+
#    Examples: 2+
```

---

## 📂 Sub-Part Pages

[v0.2.3a — Layer 0 Metadata & File Skeleton](RR-SPEC-v0.2.3a-layer-0-metadata-and-file-skeleton.md) — YAML frontmatter design, extended metadata fields, style guide, template generator script

[v0.2.3b — Layer 1 Page Entries & Summary Writing](RR-SPEC-v0.2.3b-layer-1-page-entries-and-summary-writing.md) — CanonicalPage field guide, content_type decision tree, 280-char summary masterclass, 10 before/after pairs

[v0.2.3c — Layer 2 Concept Entries & Graph Encoding](RR-SPEC-v0.2.3c-layer-2-concept-entries-and-graph-encoding.md) — Concept ID conventions, dependency graph encoding in YAML, topological ordering, Pydantic consistency checks

[v0.2.3d — Layer 3 Few-Shot Examples & Quality Assurance](RR-SPEC-v0.2.3d-layer-3-few-shot-examples-and-quality-assurance.md) — Intent taxonomy, question/answer authoring guides, few-shot testing methodology, 50+ item QA checklist

---

## Acceptance Criteria

- [ ]  `data/llms.txt` created for target site
- [ ]  ≥5 pages, ≥3 concepts, ≥2 examples
- [ ]  `python [validate.py](http://validate.py) data/llms.txt` passes
- [ ]  All URLs verified as accessible
- [ ]  File committed to git
- [ ]  **v0.2.3a:** Metadata section complete with extended DocStratum fields
- [ ]  **v0.2.3b:** All page summaries ≤280 chars and score ≥3.5 on quality rubric
- [ ]  **v0.2.3c:** Concept graph encoded with all dependencies resolving correctly
- [ ]  **v0.2.3d:** Few-shot examples cover all major intent types, final QA passed