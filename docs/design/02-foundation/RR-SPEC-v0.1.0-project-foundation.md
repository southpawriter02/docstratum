# v0.1.0 — Project Foundation

> **Phase:** Foundation (v0.1.x)
> **Status:** DRAFT — Realigned to validation-engine pivot (2026-02-06)
> **Phase Goal:** Establish the development environment, define the foundational validation schema, and create the Pydantic models that all downstream modules build upon.
> **Strategic Context:** DocStratum is a validation engine and semantic enrichment layer for llms.txt — NOT a generator. The research phase (v0.0.x) uncovered the "generation trap": 75+ tools already generate llms.txt files, but zero tools validate, score, or enrich them. This phase builds the foundation for that governance layer.
> **Research Basis:** v0.0.1–v0.0.5 (27 documents, 900+ KB of research synthesis)
> **Inherited Design Decisions:** DECISION-001 through DECISION-016 (v0.0.4d)

---

## The Pivot: From Generation Trap to Validation Engine

### Why This Phase Exists

The v0.0.x research program produced a single, unambiguous strategic conclusion: **the llms.txt ecosystem is saturated in generation and vacant in governance** (Finding 6, Consolidated Synthesis). Over 75 tools can create llms.txt files. Zero tools can formally validate one against the specification grammar. Zero tools score quality. Zero tools detect anti-patterns. Zero tools enrich files with concept definitions, few-shot examples, or LLM instructions.

DocStratum's v0.1.x foundation phase establishes the **validation-first architecture** — Pydantic models that represent not what a generated file *should* contain, but what an existing file *actually* contains, how well it conforms to the specification, and where it falls on a quality spectrum.

### What Changed from the Original v0.1.x

The original v0.1.x specs (pre-research) modeled llms.txt as a YAML-based data format for generation. The research revealed three problems with that approach:

1. **llms.txt is Markdown, not YAML** (DECISION-001, v0.0.4d). The official spec defines a Markdown file format (CommonMark 0.30 + GFM). Treating it as YAML misrepresents the format and limits interoperability with the 75+ tools that output Markdown.

2. **DocStratum should consume existing files, not define a new format** (v0.0.3d strategic positioning). The integration architecture is: accept llms.txt from any existing generator → validate → score → enrich → output to MCP consumers. This means the schema must model *parsed Markdown*, not a proprietary serialization.

3. **The value proposition is validation and scoring, not generation** (v0.0.3d, Gap T1 and T2). The 95-point conformance spread across 11 real-world specimens (5% to 100%) proves that files in the wild vary enormously in quality. A validator that can quantify that variance and provide actionable diagnostics is unprecedented in the ecosystem.

### The Adoption Paradox: Strategic Context

Every design decision in v0.1.x is informed by the **Adoption Paradox** (Finding 2, Consolidated Synthesis):

- **Grassroots adoption is real:** 1,000–5,000 substantive implementations; 844K+ detected by BuiltWith; 75+ tools; notable adopters include Anthropic, Cloudflare, Stripe, Vercel, Supabase, Shopify.
- **Zero confirmed search/chat LLM usage:** Google explicitly rejects llms.txt (Mueller, Illyes July 2025); 300K-domain study shows no AI citation correlation; server logs show LLM crawlers don't request /llms.txt.
- **Validated market: AI coding assistants via MCP.** Cursor, Claude Desktop, and Windsurf actively consume llms.txt through MCP servers (LangChain's `mcpdoc`, `mcp-llms-txt-explorer`, Context7).

**Implication (DECISION-015):** DocStratum targets AI coding assistants via MCP exclusively. Token budgets are sized for coding assistant context windows (3K–50K tokens). Quality scoring prioritizes what makes coding assistants produce better output (code examples, concept definitions, LLM instructions). No SEO-adjacent features.

---

## Phase Overview

v0.1.x is structured as three tasks that build sequentially:

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  v0.1.1      │───▶│  v0.1.2      │───▶│  v0.1.3      │
│  Environment │    │  Schema      │    │  Sample Data  │
│  Setup       │    │  Definition  │    │  & Fixtures   │
└──────────────┘    └──────────────┘    └──────────────┘
     │                    │                    │
     ▼                    ▼                    ▼
  Python 3.11+      Pydantic models      Synthetic test
  Pydantic 2.x      for validation       fixtures at
  Markdown parser    engine: parsed       5 conformance
  pytest + Black     docs, diagnostics,   levels, plus
  + Ruff             quality scores,      validation test
                     error codes          suite
```

### Module Hierarchy (from v0.0.5a)

v0.1.x establishes the schema module. The full module hierarchy for reference:

| Module | Version | Purpose | v0.1.x Role |
|--------|---------|---------|-------------|
| **Schema & Validation** | v0.1.x–v0.2.x | Pydantic models + 5-level validation pipeline | **DEFINED HERE** |
| Content Structure | v0.3.x | 3-layer architecture (Master Index → Concept Map → Few-Shot Bank) | Models defined here; logic in v0.3.x |
| Parser & Loader | v0.3.x | Robust llms.txt Markdown parser with error recovery | Consumes models defined here |
| Context Builder | v0.4.x | Token-aware, query-relevant context assembly | Uses models from here + v0.3.x |
| Agent Integration | v0.5.x | Baseline + enhanced agents with system prompt injection | Downstream consumer |
| A/B Testing Harness | v0.5.x | Test infrastructure with baselines, categories, export | Downstream consumer |
| Demo Layer | v0.6.0 | Streamlit UI with side-by-side comparison | Downstream consumer |

---

## User Stories

### US-001: Validate an Existing llms.txt File

> **As a** developer maintaining documentation for a framework consumed by AI coding assistants,
>
> **I want** to validate my existing llms.txt file against the official specification grammar,
>
> **So that** I know whether it's structurally correct, which conformance level it achieves, and what specific issues need fixing.

**Acceptance Criteria:**

- [ ] Parser ingests a Markdown llms.txt file and produces a parsed document model
- [ ] Validator runs the parsed document through the 5-level validation pipeline (L0–L4)
- [ ] Validator produces a list of diagnostics (errors, warnings, info) with line numbers and remediation hints
- [ ] Validator reports the highest validation level achieved
- [ ] Invalid files produce actionable error messages, not stack traces

**Traces to:** FR-001, FR-003, FR-004, FR-007, FR-008 (v0.0.5a)

### US-002: Score the Quality of an llms.txt File

> **As a** documentation quality lead,
>
> **I want** a quantitative quality score for my llms.txt file on a 0–100 scale,
>
> **So that** I can benchmark against gold standards, track improvement over time, and prioritize fixes by impact.

**Acceptance Criteria:**

- [ ] Quality scorer produces a composite 0–100 score with dimensional breakdown (structural 30%, content 50%, anti-pattern 20%)
- [ ] Scorer assigns a grade: Exemplary (90–100), Strong (70–89), Adequate (50–69), Needs Work (30–49), Critical (0–29)
- [ ] Each dimension's score is itemized by individual check results
- [ ] Grade thresholds align with gold standard calibration (Svelte 92, NVIDIA 24 — v0.0.4b)

**Traces to:** FR-007, FR-009 (v0.0.5a); NFR-001 (v0.0.5b)

### US-003: Classify Document Type Before Validation

> **As** the DocStratum parser,
>
> **I want** to classify an input file as Type 1 Index or Type 2 Full before applying validation rules,
>
> **So that** I apply the correct grammar and produce appropriate diagnostics for each document type.

**Acceptance Criteria:**

- [ ] Classifier distinguishes Type 1 Index (curated link catalogs, ≤250 KB, spec-conformant) from Type 2 Full (inline documentation dumps, >250 KB, spec-incompatible)
- [ ] Type 1 files receive full ABNF-based structural validation
- [ ] Type 2 files receive size-appropriate diagnostics (info-level note about spec inapplicability, size/token estimates)
- [ ] Classification heuristic uses the ~250 KB boundary validated by the bimodal specimen distribution (Finding 4)

**Traces to:** FR-026 (v0.0.5a); empirical specimen data from v0.0.1a enrichment

---

## Design Decisions Inherited from v0.0.4d

All 16 design decisions from the research phase are listed here for traceability. Ten directly constrain v0.1.x implementation; six are deferred to downstream phases but are included for completeness. Full rationale is in `RR-SPEC-v0.0.4d`.

### Decisions Applied in v0.1.x (10)

| ID | Decision | Impact on v0.1.x |
|----|----------|-------------------|
| DECISION-001 | Markdown over JSON/YAML | Schema models represent parsed Markdown, not YAML data |
| DECISION-002 | 3-Layer Architecture (Master Index → Concept Map → Few-Shot Bank) | Extended schema models for Layers 2–3 defined in v0.1.2 enrichment.py |
| DECISION-003 | GitHub Flavored Markdown (GFM) as Standard | Parser targets CommonMark 0.30 + GFM; mistletoe selected in v0.1.1 |
| DECISION-004 | Concept ID Format (lowercase alphanumeric + hyphens) | `Concept.id` uses `^[a-z0-9-]+$` regex pattern in v0.1.2 enrichment.py |
| DECISION-005 | Typed Directed Relationships in Concept Graph | `RelationshipType` enum (5 types) defined in v0.1.2 enrichment.py |
| DECISION-006 | Pydantic for Schema Validation | All 7 schema files use Pydantic v2 BaseModel |
| DECISION-012 | Canonical Section Names (11 standard names from 450+ projects) | `CanonicalSectionName` enum + 30+ aliases in v0.1.2 constants.py |
| DECISION-013 | Token Budget Tiers as First-Class Constraint | `TokenBudgetTier`, `SizeTier`, and token zone thresholds in v0.1.2 |
| DECISION-015 | AI Coding Assistants via MCP as Primary Target | Token budgets sized for coding assistant context windows (3K–50K) |
| DECISION-016 | Four-Category Anti-Pattern Severity Classification | `AntiPatternCategory` enum + 22-entry registry in v0.1.2 constants.py |

### Decisions Referenced but Primarily Deferred (6)

These decisions influence specific v0.1.2 schema fields but their full implementation occurs in downstream phases.

| ID | Decision | v0.1.x Reference | Full Implementation |
|----|----------|-------------------|---------------------|
| DECISION-007 | CSV for Relationship Matrices (not JSON) | Not modeled in schema — concerns data storage format for concept graphs | v0.3.x (Content Structure) |
| DECISION-008 | Example IDs Linked to Concepts | `FewShotExample.concept_ids` field in v0.1.2 enrichment.py defines the schema link | v0.3.x (Content Structure) |
| DECISION-009 | Anti-Pattern Detection in v0.2.4 | Anti-pattern registry defined in v0.1.2 constants.py; detection logic deferred | v0.2.4 (Validation Pipeline) |
| DECISION-010 | Master Index Priority Over Content Completeness | Referenced in W009 diagnostic code (v0.1.2 diagnostics.py); 87% vs. 31% LLM success finding | v0.2.x (Validation Pipeline) |
| DECISION-011 | Optional Sections Explicitly Marked | Referenced in I006 diagnostic code (v0.1.2 diagnostics.py); token estimate annotations | v0.2.x (Validation Pipeline) |
| DECISION-014 | Content Quality as Primary Scoring Weight (50%) | `QualityDimension` weights (30/50/20) in v0.1.2 quality.py; `QualityGrade.from_score()` thresholds | v0.2.4 (Validation Pipeline) |

---

## Tech Stack (from CONST-003, v0.0.5b)

### Foundation Phase (v0.1.x)

| Dependency | Purpose | Version |
|------------|---------|---------|
| **Python** | Runtime | 3.11+ (NFR-014) |
| **Pydantic** | Schema validation | ≥2.0.0 (DECISION-006) |
| **PyYAML** | YAML frontmatter parsing | ≥6.0 |
| **mistletoe** | Markdown parsing (CommonMark) | ≥1.3.0 |
| **pytest** | Test framework | ≥8.0.0 |
| **pytest-cov** | Coverage reporting | ≥4.0.0 |
| **black** | Code formatting | ≥24.0.0 (NFR-011) |
| **ruff** | Linting | ≥0.5.0 (NFR-011) |
| **python-dotenv** | Environment variable loading | ≥1.0.0 |

### NOT in Foundation Phase (deferred to downstream modules)

| Dependency | Phase | Reason |
|------------|-------|--------|
| LangChain | v0.3.x–v0.5.x | Agent integration, not validation |
| OpenAI / Anthropic SDKs | v0.5.x | Agent integration, not validation |
| Streamlit | v0.6.0 | Demo layer, not validation |
| Neo4j | Post-MVP (OOS-G1) | Graph visualization, out of scope |

---

## Logging Strategy

Foundation phase logging follows the error code registry from v0.0.1a (8 errors, 11 warnings, 7 informational codes). The logging module integrates with the `DiagnosticCode` enum defined in v0.1.2.

```python
# docstratum/logging_config.py
import logging

def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure DocStratum logging with structured format.

    Format includes timestamp, severity (aligned to 8 chars),
    module name, and message. Designed for both human reading
    and machine parsing.
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger('docstratum')
```

---

## Version Roadmap

```
v0.1.x  Foundation     ← YOU ARE HERE
        ├── v0.1.1  Environment Setup (deps, project structure)
        ├── v0.1.2  Schema Definition (Pydantic models for validation engine)
        └── v0.1.3  Sample Data (synthetic test fixtures, validation test suite)

v0.2.x  Validation Pipeline
        ├── v0.2.1  Source Audit (site selection for enrichment testing)
        ├── v0.2.2  Concept Extraction (mining techniques)
        ├── v0.2.3  YAML Authoring (enrichment data format)
        └── v0.2.4  Validation Pipeline (5-level validation engine implementation)

v0.3.x  Logic Core
        ├── v0.3.1  Loader Module (Markdown parser with error recovery)
        ├── v0.3.2  Context Builder (token-aware assembly)
        ├── v0.3.3  Agent Architecture (provider abstraction)
        ├── v0.3.4  Rosetta Agent (context injection + system prompt assembly)
        └── v0.3.5  A/B Harness (test execution engine)

v0.4.x  Demo Layer (Streamlit UI)
v0.5.x  Testing & Validation (integration tests, evidence capture)
v0.6.0  Release (portfolio-ready)
```

---

## Exit Criteria

This phase is **COMPLETE** when:

- [ ] Python 3.11+ installed and verified
- [ ] Virtual environment with foundation-only dependencies (no LangChain, OpenAI, Streamlit)
- [ ] `black --check .` and `ruff check .` pass with zero violations (NFR-011)
- [ ] `python -c "from docstratum.schema import ParsedLlmsTxt, ValidationResult, QualityScore"` runs without error
- [ ] `pytest` returns exit code 0 with ≥80% coverage on schema module (NFR-010)
- [ ] 5 synthetic test fixtures validate at expected conformance levels
- [ ] All diagnostic codes in the error code registry have corresponding enum values
- [ ] Document Type Classification correctly identifies Type 1 vs. Type 2 on test fixtures

---

## Traceability Appendix: Research → v0.1.x → Implementation

This appendix maps the functional requirements from v0.0.5a that are fulfilled (or partially fulfilled) by v0.1.x, establishing the bidirectional traceability chain.

### Functional Requirements Addressed by v0.1.x

| FR ID | Description | MoSCoW | v0.1.x Deliverable | Status |
|-------|------------|--------|---------------------|--------|
| FR-001 | Pydantic models for base llms.txt structure | MUST | v0.1.2 — `ParsedLlmsTxt`, `ParsedSection`, `ParsedLink` | Schema defined |
| FR-002 | Extended schema fields (metadata, concepts, examples, instructions) | MUST | v0.1.2 — `Metadata`, `Concept`, `FewShotExample`, `LLMInstruction` models | Schema defined |
| FR-003 | 5-level validation pipeline (L0–L4) | MUST | v0.1.2 — `ValidationLevel` enum, `ValidationResult` model | Schema defined; logic in v0.2.4 |
| FR-004 | Validation error reporting with line numbers | MUST | v0.1.2 — `ValidationDiagnostic` model with line_number, column, context | Schema defined; population in v0.3.1 |
| FR-007 | Quality assessment framework | MUST | v0.1.2 — `QualityScore`, `DimensionScore`, `QualityGrade` models | Schema defined; scoring in v0.2.4 |
| FR-008 | Error code registry (structured diagnostics) | MUST | v0.1.2 — `DiagnosticCode` enum with all 26 codes (8E/11W/7I) | Fully defined |
| FR-011 | Schema round-trip (parse → validate → serialize → re-parse) | MUST | v0.1.3 — Test suite verifies round-trip on all fixtures | Tested |

### Research Artifacts Consumed by v0.1.x

| Research Artifact | Source | v0.1.x Consumer |
|-------------------|--------|-----------------|
| ABNF grammar | v0.0.1a | Validation rule definitions in v0.1.2 |
| Error code registry (8/11/7) | v0.0.1a enrichment | `DiagnosticCode` enum in v0.1.2 |
| 8 specification gaps | v0.0.1b | Extended schema models (Metadata, Concepts, Few-Shot) in v0.1.2 |
| Document Type Classification | v0.0.1a enrichment | `DocumentType` enum + classification model in v0.1.2 |
| 11 canonical section names | v0.0.2c | `CanonicalSectionName` enum in v0.1.2 |
| 57 automated checks | v0.0.4 | Check ID references in validation rule models in v0.1.2 |
| 100-point quality scoring | v0.0.4b | `QualityScore` model with dimensional weights in v0.1.2 |
| 22 anti-patterns | v0.0.4c | `AntiPatternID` enum in v0.1.2 |
| 11 specimen conformance data | v0.0.2 enrichment | Synthetic fixture calibration in v0.1.3 |

### Requirements NOT Addressed by v0.1.x (Downstream)

| FR ID | Description | Target Phase |
|-------|------------|-------------|
| FR-013 | Master Index layer construction | v0.3.x |
| FR-016 | Concept Map layer construction | v0.3.x |
| FR-020 | LLM Instructions as first-class component | v0.3.x |
| FR-026 | Robust Markdown parser with error recovery | v0.3.1 |
| FR-032–035 | Context Builder with token-aware assembly | v0.4.x |
| FR-039–042 | Baseline + enhanced agents | v0.5.x |
| FR-051–058 | A/B testing harness | v0.5.x |
| FR-059–060 | Streamlit demo | v0.6.0 |

---

## Sub-Task Links

- [v0.1.1 — Environment Setup](RR-SPEC-v0.1.1-environment-setup.md)
- [v0.1.2 — Schema Definition](RR-SPEC-v0.1.2-schema-definition.md) *(parent overview)*
  - [v0.1.2a — Diagnostic Infrastructure](RR-SPEC-v0.1.2a-diagnostic-infrastructure.md) — `diagnostics.py`, `constants.py`, cross-reference mapping
  - [v0.1.2b — Document Models](RR-SPEC-v0.1.2b-document-models.md) — `classification.py`, `parsed.py`
  - [v0.1.2c — Validation & Quality Models](RR-SPEC-v0.1.2c-validation-quality-models.md) — `validation.py`, `quality.py`
  - [v0.1.2d — Enrichment Models](RR-SPEC-v0.1.2d-enrichment-models.md) — `enrichment.py`
- [v0.1.3 — Sample Data & Test Fixtures](RR-SPEC-v0.1.3-sample-data.md) *(parent overview)*
  - [v0.1.3a — Fixture Suite](RR-SPEC-v0.1.3a-fixture-suite.md) — 5 Markdown fixtures + expectation matrix
  - [v0.1.3b — Test Infrastructure & Suites](RR-SPEC-v0.1.3b-test-infrastructure.md) — `conftest.py` + 7 test modules
