# v0.2.1 — Source Audit

> **Task:** Select and analyze a target documentation site for the `llms.txt` implementation.
> 

---

## Task Overview

---

## Workflow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 1. Select   │───▶│ 2. Audit    │───▶│ 3. Catalog  │───▶│ 4. Document │
│   site      │    │   structure │    │   pages     │    │   findings  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

---

## Site Selection Criteria

### Must Have

- [ ]  At least 10 documentation pages
- [ ]  Permissive license (MIT, Apache 2.0, CC-BY) OR your own content
- [ ]  Mix of content types (tutorials, references, concepts)
- [ ]  Publicly accessible (no auth required to read)

### Nice to Have

- [ ]  Active maintenance (updated within 6 months)
- [ ]  Clear information architecture
- [ ]  API documentation with examples
- [ ]  Changelog or version history

---

## Recommended Target Sites

---

## Audit Template

### Site Information

```yaml
# docs/SOURCE_AUDIT.md

site_name: "[NAME]"
site_url: "[URL]"
license: "[LICENSE]"
audit_date: "[DATE]"

# Site Structure
total_pages_estimated: 
section_count: 
max_nesting_depth: 

# Content Types Found
tutorials: 
references: 
concepts: 
faq: 
changelog: 
```

### Page Inventory

Create a spreadsheet or table:

---

## Audit Checklist

### Structure Analysis

- [ ]  Map the navigation hierarchy
- [ ]  Identify orphan pages (no nav links)
- [ ]  Note any circular references
- [ ]  Document external dependencies

### Content Analysis

- [ ]  Identify 5 core concepts
- [ ]  Map concept dependencies
- [ ]  Find existing code examples
- [ ]  Note any anti-patterns mentioned

### Quality Assessment

- [ ]  Check for broken links (use a crawler)
- [ ]  Verify code examples are current
- [ ]  Note any outdated information
- [ ]  Identify gaps in documentation

---

## Deliverables

- [ ]  `docs/SOURCE_[AUDIT.md](http://AUDIT.md)` — Completed audit document
- [ ]  Page inventory (10+ pages cataloged)
- [ ]  Concept map draft (5+ concepts identified)
- [ ]  Decision documented: "Selected [SITE] because [REASON]"

---

## 📂 Sub-Part Pages

[v0.2.1a — Site Selection & Evaluation Framework](RR-SPEC-v0.2.1a-site-selection-evaluation-framework.md) — Weighted scoring matrix, 6 candidate sites evaluated, license compatibility guide, automated pre-screening script

[v0.2.1b — Documentation Architecture Analysis](RR-SPEC-v0.2.1b-documentation-architecture-analysis.md) — Information architecture mapping, content type classification, URL pattern analysis, documentation framework comparison

[v0.2.1c — Page Inventory & Content Cataloging](RR-SPEC-v0.2.1c-page-inventory-content-cataloging.md) — Systematic crawling strategy, 18-field catalog schema, token estimation, priority scoring, Top 10 selection method

[v0.2.1d — Quality Assessment & Gap Identification](RR-SPEC-v0.2.1d-quality-assessment-gap-identification.md) — 5-dimension quality rubric, link health audit, code validation, content gap identification, competitive benchmarking

---

## Acceptance Criteria

- [ ]  Target site selected and documented
- [ ]  License verified as compatible
- [ ]  At least 10 pages identified for inclusion
- [ ]  At least 5 core concepts identified
- [ ]  Audit document committed to repo
- [ ]  **v0.2.1a:** Site selection decision documented with weighted scoring
- [ ]  **v0.2.1b:** Information architecture mapped with content type taxonomy
- [ ]  **v0.2.1c:** Page inventory with priority scores and token estimates
- [ ]  **v0.2.1d:** Quality audit report with gap analysis completed