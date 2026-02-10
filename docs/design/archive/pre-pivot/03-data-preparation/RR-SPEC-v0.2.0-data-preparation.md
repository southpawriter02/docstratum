# v0.2.0 — Data Preparation

> **Phase Goal:** Audit a target documentation site, extract content, and transform it into a validated `llms.txt` file.
> 

---

## Phase Overview

---

## User Stories

### US-003: Source Site Selection

> **As a** portfolio developer,
> 

> **I want** to select an appropriate documentation site,
> 

> **So that** I have realistic data to demonstrate the project.
> 

**Acceptance Criteria:**

- [ ]  Site has at least 10 documentation pages
- [ ]  Site has permissive license (or is my own content)
- [ ]  Site has a mix of tutorials, references, and concepts

### US-004: Content Extraction

> **As a** technical writer,
> 

> **I want** to extract core concepts from documentation,
> 

> **So that** I can build a semantic concept map.
> 

**Acceptance Criteria:**

- [ ]  At least 5 `CanonicalPage` entries created
- [ ]  At least 3 `Concept` entries with relationships
- [ ]  At least 2 `FewShotExample` entries written

### US-005: Schema Validation

> **As a** developer,
> 

> **I want** the `llms.txt` to pass all validation rules,
> 

> **So that** downstream systems can rely on its structure.
> 

**Acceptance Criteria:**

- [ ]  `pydantic` validation passes
- [ ]  All URLs are reachable (200 OK)
- [ ]  All `depends_on` references resolve to valid concept IDs

---

## Workflow: Content Extraction

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  1. AUDIT    │───▶│  2. EXTRACT  │───▶│  3. WRITE    │
│   (Manual)   │    │   (Manual)   │    │   (Manual)   │
└──────────────┘    └──────────────┘    └──────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
  List all pages     Identify core       Draft YAML
  Note content       concepts & their    entries for
  types              relationships       each entity
       │                   │                   │
       ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  4. VALIDATE │◀───│  5. ITERATE  │◀───│  6. TEST     │
│   (Script)   │    │   (Manual)   │    │   (Script)   │
└──────────────┘    └──────────────┘    └──────────────┘
       │
       ▼
  Run Pydantic
  validation
```

---

## Decision Tree: Target Site Selection

```
                ┌─────────────────┐
                │ Do I have my    │
                │ own docs site?  │
                └────────┬────────┘
                         │
          ┌──────────────┴──────────────┐
          ▼                             ▼
       YES ✅                          NO
          │                             │
          ▼                             ▼
Use your own site           ┌─────────────────┐
(Ideal for portfolio)       │ Is the site     │
                            │ open-source?    │
                            └────────┬────────┘
                                     │
                      ┌──────────────┴──────────────┐
                      ▼                             ▼
                   YES ✅                          NO
                      │                             │
                      ▼                             ▼
             Use open-source docs:        ⚠️ Check license
             • FastAPI                    before proceeding
             • Streamlit
             • Pydantic
```

---

## Version Roadmap

---

## Testing Strategy

### Test: Schema Validation

```python
# tests/test_schema.py
import pytest
from schemas.llms_schema import LlmsTxt
import yaml

def test_valid_llms_txt_loads():
    """A valid llms.txt file should load without errors."""
    with open('examples/llms.txt') as f:
        data = yaml.safe_load(f)
    llms = LlmsTxt(**data)
    assert llms.site_name is not None

def test_invalid_content_type_raises():
    """An invalid content_type should raise ValidationError."""
    invalid_data = {
        'url': 'https://example.com',
        'title': 'Test',
        'content_type': 'INVALID_TYPE',  # Not in Literal
        'last_verified': '2026-01-01',
        'summary': 'Test summary'
    }
    with pytest.raises(Exception):
        from schemas.llms_schema import CanonicalPage
        CanonicalPage(**invalid_data)
```

---

## Exit Criteria

This phase is **COMPLETE** when:

- [ ]  Target documentation site selected and documented
- [ ]  `llms.txt` contains ≥5 pages, ≥3 concepts, ≥2 few-shot examples
- [ ]  `python [validate.py](http://validate.py) examples/llms.txt` returns success
- [ ]  All concept `depends_on` references are valid
- [ ]  All tests in `tests/test_[schema.py](http://schema.py)` pass

[v0.2.1 — Source Audit](RR-SPEC-v0.2.1-source-audit.md)
- v0.2.1a — Site Selection & Evaluation Framework
- v0.2.1b — Documentation Architecture Analysis
- v0.2.1c — Page Inventory & Content Cataloging
- v0.2.1d — Quality Assessment & Gap Identification

[v0.2.2 — Concept Extraction](RR-SPEC-v0.2.2-concept-extraction.md)
- v0.2.2a — Concept Identification & Mining Techniques
- v0.2.2b — Precision Definition Writing
- v0.2.2c — Relationship Mapping & Dependency Graphs
- v0.2.2d — Anti-Pattern Documentation & Misconception Mining

[v0.2.3 — YAML Authoring](RR-SPEC-v0.2.3-yaml-authoring.md)
- v0.2.3a — Layer 0 Metadata & File Skeleton
- v0.2.3b — Layer 1 Page Entries & Summary Writing
- v0.2.3c — Layer 2 Concept Entries & Graph Encoding
- v0.2.3d — Layer 3 Few-Shot Examples & Quality Assurance

[v0.2.4 — Validation Pipeline](RR-SPEC-v0.2.4-validation-pipeline.md)
- v0.2.4a — Schema Validation Engine (Levels 0-1)
- v0.2.4b — Content & Link Validation Engine (Level 2)
- v0.2.4c — Quality Scoring Engine (Level 3)
- v0.2.4d — Pipeline Orchestration & Reporting