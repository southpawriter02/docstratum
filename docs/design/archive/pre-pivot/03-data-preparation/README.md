# 03-data-preparation — Data Preparation (v0.2.x)

> **Purpose**: Source auditing, concept extraction, YAML authoring, and validation pipeline

This phase transforms raw documentation into structured, validated `/llms.txt` files through systematic auditing, concept mining, and multi-layer authoring.

---

## 📚 Phase Structure

### v0.2.1 — Source Audit

Systematic evaluation and cataloging of target documentation:

- **v0.2.1a** — Site Selection & Evaluation Framework
- **v0.2.1b** — Documentation Architecture Analysis
- **v0.2.1c** — Page Inventory & Content Cataloging
- **v0.2.1d** — Quality Assessment & Gap Identification

### v0.2.2 — Concept Extraction

Mining and defining core concepts from documentation:

- **v0.2.2a** — Concept Identification & Mining Techniques
- **v0.2.2b** — Precision Definition Writing
- **v0.2.2c** — Relationship Mapping & Dependency Graphs
- **v0.2.2d** — Anti-Pattern Documentation & Misconception Mining

### v0.2.3 — YAML Authoring

Four-layer authoring process for `/llms.txt` files:

- **v0.2.3a** — Layer 0: Metadata and File Skeleton
- **v0.2.3b** — Layer 1: Page Entries and Summary Writing
- **v0.2.3c** — Layer 2: Concept Entries and Graph Encoding
- **v0.2.3d** — Layer 3: Few-Shot Examples and Quality Assurance

### v0.2.4 — Validation Pipeline

Multi-level validation and quality scoring:

- **v0.2.4a** — Schema Validation Engine (Levels 0-1)
- **v0.2.4b** — Content & Link Validation Engine (Level 2)
- **v0.2.4c** — Quality Scoring Engine (Level 3)
- **v0.2.4d** — Pipeline Orchestration & Reporting

---

## 🔍 Key Concepts

### The Four-Layer Architecture

**Layer 0: Metadata**

- Schema version
- Site name and URL
- Last updated timestamp

**Layer 1: Page Index**

- Canonical URLs
- Content type tags (tutorial, reference, changelog, concept, FAQ)
- Freshness timestamps
- Tweet-length summaries (max 280 chars)

**Layer 2: Concept Map**

- Concept IDs and names
- One-sentence definitions (no pronouns)
- Dependency graphs (`depends_on` relationships)
- Anti-patterns and misconceptions

**Layer 3: Few-Shot Bank**

- Intent classification
- Example questions
- Ideal answers
- Source page citations

---

## 🎯 Quality Standards

### Concept Definitions

- **One sentence maximum**
- **No pronouns** (avoid "it", "this", "that")
- **Active voice preferred**
- **Precise terminology**

### Few-Shot Examples

- **Realistic user questions**
- **Complete, actionable answers**
- **Explicit source citations**
- **Code snippets where applicable**

### Summaries

- **280 characters maximum** (tweet-length)
- **Action-oriented** (what the user will learn/do)
- **No marketing fluff**

---

## 🔧 Key Deliverables

### Source Audit Artifacts

- Site selection evaluation matrix
- Documentation architecture diagram
- Complete page inventory (CSV/spreadsheet)
- Quality assessment report

### Concept Extraction Artifacts

- Concept taxonomy (hierarchical list)
- Dependency graph (Mermaid/Neo4j visualization)
- Anti-pattern catalog
- Misconception registry

### YAML Authoring Artifacts

- Complete `/llms.txt` file(s)
- Validation reports
- Quality scores
- Change logs

### Validation Pipeline

- Schema validator (Pydantic)
- Link checker
- Content quality scorer
- Automated reporting

---

## 🎯 Success Criteria

This data preparation phase is complete when:

- ✅ Target documentation site is fully audited
- ✅ Core concepts are extracted and defined
- ✅ Dependency graph is complete and validated
- ✅ `/llms.txt` file passes all validation levels
- ✅ Quality score meets minimum threshold (TBD in v0.0.5d)
- ✅ Few-shot examples cover key user intents

---

## 🗺️ Next Phase

After completing data preparation, proceed to:

- **`04-logic-core/`** — Loader module and agent implementation
