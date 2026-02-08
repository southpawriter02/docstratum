# v0.0.7 — Ecosystem Pivot: From Single-File Validator to Documentation Quality Platform

> **Phase:** Research & Discovery (v0.0.x) — Strategic Revision
> **Status:** DRAFT
> **Date Created:** 2026-02-07
> **Author:** Ryan + Claude Opus 4.6
> **Purpose:** Define the architectural pivot from validating a single llms.txt file to validating and scoring an entire AI-ready documentation ecosystem. Identifies what stays, what extends, what's new, and provides a phased migration plan that preserves all existing research investment.

---

## 1. The Pivot in One Paragraph

DocStratum was originally scoped as a **single-file validator** — you feed it one llms.txt file, it returns diagnostics and a quality score. The pivot redefines DocStratum as an **ecosystem-level documentation quality platform** — you feed it a project's entire AI-documentation surface (llms.txt, llms-full.txt, individual Markdown pages, instruction files), and it validates each file individually, validates the relationships between files, and produces both per-file scores and an aggregate ecosystem health score. The single-file validator becomes a *component* within the ecosystem validator, not a separate product that gets replaced.

---

## 2. Why Pivot Now

### 2.1 The Timing Argument

The codebase is light. The design documentation is the primary investment (~900 KB across 27 research documents, 11 foundation documents). A pivot now costs design-doc revisions and schema adjustments. A pivot at v0.6.0 (after all 32 MVP features are built) would cost a full rearchitecture of the validation pipeline, scoring system, and test infrastructure.

### 2.2 The Market Argument

Every existing tool in the llms.txt space (7+ validators, 12+ generators) operates on a single file. No tool validates the relationship between llms.txt and llms-full.txt. No tool checks whether the index file's links actually resolve to useful content. No tool assesses whether a project's total AI-documentation coverage is adequate. By pivoting to ecosystem-level validation, DocStratum doesn't just differentiate — it creates a category that doesn't exist yet.

### 2.3 The Technical Argument

The v0.0.6 Platinum Standard (Section 7.3, Open Question #2) already surfaced this: "How should multi-file strategies (llms.txt + llms-full.txt) be scored?" The answer isn't "separately." It's "as an ecosystem." A project with a perfect llms.txt but no llms-full.txt and broken links to nonexistent .md pages is not a well-documented project — but the single-file validator would score it as EXEMPLARY.

---

## 3. The Ecosystem Model

### 3.1 What Is a Documentation Ecosystem?

A **Documentation Ecosystem** is the complete set of AI-facing documentation files that a project publishes. It includes:

```
project-root/
├── llms.txt              ← Navigation Index (required)
├── llms-full.txt         ← Complete Content Dump (optional)
├── docs/
│   ├── getting-started.md   ← Individual content page
│   ├── api-reference.md     ← Individual content page
│   ├── concepts.md          ← Individual content page
│   └── examples.md          ← Individual content page
└── (other project files not part of the ecosystem)
```

The ecosystem has three layers that map to distinct consumption models:

| Layer | File(s) | Purpose | Consumption Model | Analogy |
|-------|---------|---------|-------------------|---------|
| **Navigation** | `llms.txt` | Tell the agent what exists and where to find it | MCP entry point; context injection for small windows | Card catalog |
| **Content** | Individual `.md` pages | Provide detailed information on specific topics | MCP on-demand fetch; RAG chunking | Individual chapters |
| **Aggregate** | `llms-full.txt` | Provide everything in one file for large-window models | Context injection for large windows | The whole book on one scroll |

**Key insight:** These layers are not independent files that happen to live in the same directory. They are **interdependent components of a single documentation system**. The index should reference the content pages. The aggregate should contain the content pages. The content pages should be self-contained enough to work when fetched individually by an agent.

### 3.2 File Types and Roles

| File Type | Role in Ecosystem | Required? | Validated By |
|-----------|-------------------|-----------|-------------|
| `llms.txt` | **Index** — Primary entry point for AI agents. Contains project overview and navigation links. | **Yes** (the ecosystem root) | Existing L0–L4 pipeline (Platinum Standard) |
| `llms-full.txt` | **Aggregate** — Complete content in one file. Enables single-request context injection. | No (recommended for projects with >4.5K tokens of documentation) | New: Aggregate validation rules |
| `*.md` content pages | **Content** — Detailed documentation on specific topics. Linked from the index. | No (but their absence limits the index's utility) | New: Content page validation rules |
| `llms-instructions.txt` | **Instructions** — Explicit behavioral guidance for AI agents (DO/DON'T patterns, priorities, warnings). | No (but strongly recommended; currently embedded as a section in llms.txt) | New: Instruction validation rules |

### 3.3 Relationship Types

Files in an ecosystem relate to each other in specific, validatable ways:

| Relationship | From → To | Meaning | Validatable Check |
|-------------|-----------|---------|-------------------|
| **INDEXES** | llms.txt → content page | The index links to this content page | Does the link resolve? Does the page exist? |
| **AGGREGATES** | llms-full.txt → content page | The aggregate contains this content page's text | Does the aggregate actually include this content? |
| **REFERENCES** | content page → content page | One page cross-references another | Does the cross-reference resolve? Is it reciprocal? |
| **INSTRUCTS** | llms-instructions.txt → all files | Instructions govern how agents should use all other files | Do instructions reference sections that actually exist? |
| **SUMMARIZES** | llms.txt blockquote → project | The blockquote summarizes the overall project | Is the summary consistent with the content pages? (Heuristic) |

---

## 4. New Schema Entities

### 4.1 What Stays Unchanged

The following existing models are **fully preserved** and continue to work exactly as designed. The pivot adds new models *around* them, not *replacing* them.

| Existing Model | Status | Rationale |
|---------------|--------|-----------|
| `ParsedBlockquote` | **Unchanged** | Still represents a blockquote within any file |
| `ParsedLink` | **Unchanged** (extended, see 4.2) | Still represents a link; gains optional relationship metadata |
| `ParsedSection` | **Unchanged** | Still represents an H2 section within any file |
| `ParsedLlmsTxt` | **Unchanged** (renamed conceptually, see 4.2) | Still represents a single parsed Markdown file |
| `DocumentType` | **Extended** | Gains new values for content pages and instruction files |
| `SizeTier` | **Unchanged** | Still applies per-file |
| `DocumentClassification` | **Unchanged** | Still applies per-file |
| `ValidationLevel` (L0–L4) | **Unchanged** | Still applies per-file; ecosystem level is separate |
| `ValidationDiagnostic` | **Extended** | Gains optional cross-file context |
| `ValidationResult` | **Unchanged** | Still represents per-file validation |
| `Severity` | **Unchanged** | ERROR / WARNING / INFO still applies |
| `DiagnosticCode` (26 codes) | **Extended** | New codes added for ecosystem-level checks |
| `QualityDimension` | **Extended** | Gains new ECOSYSTEM dimension |
| `QualityGrade` | **Unchanged** | Same 5 grades, same thresholds |
| `DimensionScore` | **Unchanged** | Still represents per-dimension scoring |
| `QualityScore` | **Unchanged** | Still represents per-file quality |
| `CanonicalSectionName` (11) | **Unchanged** | Still applies to sections within any file |
| `AntiPatternID` (22) | **Extended** | New ecosystem-level anti-patterns added |
| `AntiPatternEntry` | **Unchanged** | Same structure for new patterns |
| `TokenBudgetTier` | **Unchanged** | Still applies per-file |

**Summary:** 20 existing models survive the pivot. 6 are extended (new enum values or optional fields). 0 are deleted or replaced.

### 4.2 What Gets Extended

#### `DocumentType` — New Values

```python
class DocumentType(StrEnum):
    # Existing
    TYPE_1_INDEX = "type_1_index"         # llms.txt (curated index)
    TYPE_2_FULL = "type_2_full"           # llms-full.txt (complete dump)
    UNKNOWN = "unknown"

    # New
    TYPE_3_CONTENT_PAGE = "type_3_content_page"    # Individual .md page
    TYPE_4_INSTRUCTIONS = "type_4_instructions"    # llms-instructions.txt
```

**Rationale:** The classifier currently sorts files into Index vs Full vs Unknown. With ecosystem awareness, it also needs to identify content pages (linked from the index) and instruction files (behavioral guidance for agents). The classifier determines which validation rule set to apply.

#### `ParsedLink` — Optional Relationship Metadata

```python
class LinkRelationship(StrEnum):
    """How this link relates to the target within the ecosystem."""
    INDEXES = "indexes"           # Index → content page
    REFERENCES = "references"     # Content page → content page
    EXTERNAL = "external"         # Link to outside the ecosystem
    UNKNOWN = "unknown"           # Not yet classified

class ParsedLink(BaseModel):
    # Existing fields (unchanged)
    title: str
    url: str
    description: str | None = None
    line_number: int
    is_valid_url: bool = True

    # New (optional — backwards compatible)
    relationship: LinkRelationship = LinkRelationship.UNKNOWN
    resolves_to: str | None = None      # Resolved file path, if ecosystem-aware
    target_file_type: DocumentType | None = None  # What type of file the link points to
```

**Rationale:** When validating a single file, links are just URLs. When validating an ecosystem, links are *relationships* — they connect files to each other. Knowing that a link in llms.txt INDEXES a content page (vs. referencing an external site) enables cross-file validation. These fields are optional so the single-file pipeline is unaffected.

#### `ValidationDiagnostic` — Cross-File Context

```python
class ValidationDiagnostic(BaseModel):
    # Existing fields (unchanged)
    code: DiagnosticCode
    severity: Severity
    message: str
    remediation: str
    line_number: int | None = None
    column: int | None = None
    context: str | None = None
    level: ValidationLevel
    check_id: str | None = None

    # New (optional — backwards compatible)
    source_file: str | None = None   # Which file this diagnostic came from
    related_file: str | None = None  # Which other file is involved (for cross-file issues)
```

**Rationale:** When a link in llms.txt points to a content page that doesn't exist, the diagnostic needs to identify *both* files — the source (llms.txt, where the broken link lives) and the target (the missing content page). This enables the ecosystem validator to produce diagnostics that explain cross-file problems.

### 4.3 What's Entirely New

#### `EcosystemFile` — File Within the Ecosystem

```python
class EcosystemFile(BaseModel):
    """A single file within a documentation ecosystem."""
    file_id: str                            # UUID for cross-referencing
    file_path: str                          # Relative path from project root
    file_type: DocumentType                 # Type 1–4 or Unknown
    classification: DocumentClassification  # Size, tier, etc.
    parsed: ParsedLlmsTxt | None = None     # Parsed content (if parseable)
    validation: ValidationResult | None = None  # Per-file validation results
    quality: QualityScore | None = None     # Per-file quality score
    relationships: list[FileRelationship] = []  # How this file relates to others
```

**Rationale:** This wraps an existing parsed file with ecosystem-level metadata: its ID (for cross-referencing), its relationships to other files, and its per-file validation/quality results. It's the bridge between the single-file pipeline and the ecosystem pipeline.

#### `FileRelationship` — How Two Files Connect

```python
class FileRelationship(BaseModel):
    """A directed relationship between two files in the ecosystem."""
    source_file_id: str             # The file containing the reference
    target_file_id: str             # The file being referenced
    relationship_type: LinkRelationship  # INDEXES, AGGREGATES, REFERENCES, etc.
    source_line: int | None = None  # Line in source file where the relationship is declared
    target_url: str                 # The URL/path used to reference the target
    is_resolved: bool = False       # Whether the target was found and accessible
```

**Rationale:** Relationships are the core of ecosystem validation. A link in llms.txt that points to `docs/api-reference.md` creates an INDEXES relationship. The ecosystem validator checks whether that relationship is *resolved* (the file exists and is accessible) and whether the target file is *healthy* (it passes its own validation).

#### `DocumentEcosystem` — The Top-Level Entity

```python
class DocumentEcosystem(BaseModel):
    """A complete AI-ready documentation ecosystem for a project."""
    ecosystem_id: str                       # UUID
    project_name: str                       # From llms.txt H1 title
    root_file: EcosystemFile                # The llms.txt index (required)
    files: list[EcosystemFile]              # All files in the ecosystem
    relationships: list[FileRelationship]   # All cross-file relationships
    ecosystem_score: EcosystemScore | None = None  # Aggregate health score
    discovered_at: datetime                 # When the ecosystem was scanned

    @property
    def file_count(self) -> int:
        return len(self.files)

    @property
    def index_file(self) -> EcosystemFile:
        return self.root_file

    @property
    def aggregate_file(self) -> EcosystemFile | None:
        """The llms-full.txt file, if present."""
        return next((f for f in self.files if f.file_type == DocumentType.TYPE_2_FULL), None)

    @property
    def content_pages(self) -> list[EcosystemFile]:
        """All individual content pages."""
        return [f for f in self.files if f.file_type == DocumentType.TYPE_3_CONTENT_PAGE]

    @property
    def instruction_file(self) -> EcosystemFile | None:
        """The llms-instructions.txt file, if present."""
        return next((f for f in self.files if f.file_type == DocumentType.TYPE_4_INSTRUCTIONS), None)
```

**Rationale:** This is the new top-level entity. Where `ParsedLlmsTxt` was the root of the old single-file world, `DocumentEcosystem` is the root of the new ecosystem world. It contains all files, all relationships, and the aggregate health score. The single-file pipeline runs *within* this structure — each `EcosystemFile` gets its own `ValidationResult` and `QualityScore`.

#### `EcosystemScore` — Aggregate Health

```python
class EcosystemHealthDimension(StrEnum):
    """Dimensions of ecosystem-level quality."""
    COVERAGE = "coverage"           # Does the ecosystem cover all necessary areas?
    CONSISTENCY = "consistency"     # Do files agree with each other?
    COMPLETENESS = "completeness"   # Does every promise (link) lead to content?
    TOKEN_EFFICIENCY = "token_efficiency"  # Is content distributed optimally?
    FRESHNESS = "freshness"         # Are all files in sync (version-wise)?

class EcosystemScore(BaseModel):
    """Aggregate quality score for the entire documentation ecosystem."""
    total_score: float                  # 0–100 composite
    grade: QualityGrade                 # Reuses existing grade enum
    dimensions: dict[EcosystemHealthDimension, DimensionScore]
    per_file_scores: dict[str, QualityScore]  # file_id → per-file score
    file_count: int
    relationship_count: int
    broken_relationships: int
    scored_at: datetime
```

**Rationale:** The ecosystem score is *not* an average of per-file scores. It measures properties that only exist at the ecosystem level: coverage (are all documentation areas represented?), consistency (do files agree on project name, terminology, versioning?), completeness (does every link in the index lead to actual content?), token efficiency (is content distributed well across files, or is everything crammed into one?), and freshness (are all files up to date?).

---

## 5. New Diagnostic Codes

### 5.1 Ecosystem-Level Error Codes (E-series)

| Code | Name | Description | Severity |
|------|------|-------------|----------|
| E009 | NO_INDEX_FILE | Ecosystem has no llms.txt file (the required root) | ERROR |
| E010 | ORPHANED_ECOSYSTEM_FILE | A file in the ecosystem is not referenced by any other file | ERROR |

### 5.2 Ecosystem-Level Warning Codes (W-series)

| Code | Name | Description | Severity |
|------|------|-------------|----------|
| W012 | BROKEN_CROSS_FILE_LINK | A link in one file references another file that doesn't exist or is unreachable | WARNING |
| W013 | MISSING_AGGREGATE | Index file token count suggests a project large enough to benefit from llms-full.txt, but none exists | WARNING |
| W014 | AGGREGATE_INCOMPLETE | llms-full.txt does not contain content from all files referenced in the index | WARNING |
| W015 | INCONSISTENT_PROJECT_NAME | H1 title differs between files in the ecosystem | WARNING |
| W016 | INCONSISTENT_VERSIONING | Version metadata differs between files (one says v2.1, another says v2.0) | WARNING |
| W017 | REDUNDANT_CONTENT | Significant content duplication between files (>60% overlap) beyond expected index-to-full duplication | WARNING |
| W018 | UNBALANCED_TOKEN_DISTRIBUTION | One file consumes >70% of total ecosystem tokens while others are near-empty | WARNING |

### 5.3 Ecosystem-Level Informational Codes (I-series)

| Code | Name | Description | Severity |
|------|------|-------------|----------|
| I008 | NO_INSTRUCTION_FILE | No llms-instructions.txt or LLM Instructions section exists in the ecosystem | INFO |
| I009 | CONTENT_COVERAGE_GAP | The index references section categories (e.g., "API Reference") for which no detailed content page exists | INFO |
| I010 | ECOSYSTEM_SINGLE_FILE | The entire ecosystem consists of just llms.txt with no companion files. Valid but limited. | INFO |

### 5.4 Updated Totals

| Severity | Previous Count | New Count | Added |
|----------|---------------|-----------|-------|
| ERROR | 8 (E001–E008) | 10 (E001–E010) | +2 |
| WARNING | 11 (W001–W011) | 18 (W001–W018) | +7 |
| INFO | 7 (I001–I007) | 10 (I001–I010) | +3 |
| **Total** | **26** | **38** | **+12** |

---

## 6. New Anti-Patterns

### 6.1 Ecosystem Anti-Pattern Category

The existing 4 anti-pattern categories (CRITICAL, STRUCTURAL, CONTENT, STRATEGIC) apply to individual files. A new fifth category applies to ecosystems:

```python
class AntiPatternCategory(StrEnum):
    CRITICAL = "critical"
    STRUCTURAL = "structural"
    CONTENT = "content"
    STRATEGIC = "strategic"
    ECOSYSTEM = "ecosystem"  # NEW
```

### 6.2 Ecosystem Anti-Patterns

| ID | Name | Description | Severity |
|----|------|-------------|----------|
| AP_ECO_001 | **Index Island** | llms.txt exists but links to nothing — no content pages, no aggregate, just a dead-end index | ECOSYSTEM |
| AP_ECO_002 | **Phantom Links** | >30% of links in the index reference files that don't exist or return errors | ECOSYSTEM |
| AP_ECO_003 | **Shadow Aggregate** | llms-full.txt exists but its content doesn't match what the index promises — different sections, different project, or outdated content | ECOSYSTEM |
| AP_ECO_004 | **Duplicate Ecosystem** | Multiple llms.txt files exist in the same project root (e.g., llms.txt and LLMS.txt) creating ambiguity | ECOSYSTEM |
| AP_ECO_005 | **Token Black Hole** | One file consumes >80% of total ecosystem tokens, defeating the purpose of the multi-file strategy | ECOSYSTEM |
| AP_ECO_006 | **Orphan Nursery** | Multiple content pages exist but are not referenced from the index — useful content that agents can't discover | ECOSYSTEM |

### 6.3 Updated Anti-Pattern Totals

| Category | Previous Count | New Count |
|----------|---------------|-----------|
| CRITICAL | 4 | 4 |
| STRUCTURAL | 5 | 5 |
| CONTENT | 9 | 9 |
| STRATEGIC | 4 | 4 |
| ECOSYSTEM | 0 | 6 |
| **Total** | **22** | **28** |

---

## 7. The Ecosystem Validation Pipeline

### 7.1 How It Works

The ecosystem pipeline wraps the existing single-file pipeline, not replaces it:

```
INPUT: Project root directory (or URL)

    ↓

[DISCOVERY STAGE] — NEW
Scan the project root for AI-documentation files:
  - Look for llms.txt (required)
  - Look for llms-full.txt (optional)
  - Look for llms-instructions.txt (optional)
  - Follow links from llms.txt to discover content pages
  - Build a file manifest
  Returns: list[EcosystemFile] (unvalidated)

    ↓

[PER-FILE VALIDATION STAGE] — EXISTING (run once per file)
For each discovered file:
  ┌─────────────────────────────────────────────────────┐
  │ Existing single-file pipeline (unchanged):          │
  │   Parse → Classify → Validate (L0–L4) → Score      │
  │   Returns: ParsedLlmsTxt + ValidationResult +       │
  │            QualityScore per file                     │
  └─────────────────────────────────────────────────────┘
  Store results in EcosystemFile.parsed, .validation, .quality

    ↓

[RELATIONSHIP MAPPING STAGE] — NEW
Analyze links across all files:
  - Classify each link as INDEXES, REFERENCES, AGGREGATES, or EXTERNAL
  - Check whether each internal link resolves to another file in the ecosystem
  - Build the FileRelationship graph
  Returns: list[FileRelationship]

    ↓

[ECOSYSTEM VALIDATION STAGE] — NEW
Run ecosystem-level checks:
  - Coverage: Are all canonical section categories represented across the ecosystem?
  - Consistency: Do files agree on project name, version, terminology?
  - Completeness: Does every internal link resolve? Does the aggregate contain all content?
  - Anti-patterns: Check for Index Island, Phantom Links, Shadow Aggregate, etc.
  Returns: list[ValidationDiagnostic] (with ecosystem-level codes E009–E010, W012–W018, I008–I010)

    ↓

[ECOSYSTEM SCORING STAGE] — NEW
Calculate aggregate health score:
  - 5 dimensions: Coverage, Consistency, Completeness, Token Efficiency, Freshness
  - Each dimension scored independently
  - Composite score and grade assigned
  Returns: EcosystemScore

    ↓

OUTPUT: DocumentEcosystem (containing all files, relationships, per-file results, and ecosystem score)
```

### 7.2 The Critical Property: Backward Compatibility

A user who feeds DocStratum a single llms.txt file (with no project root, no companion files) gets exactly the same output they would have gotten before the pivot. The Discovery stage finds one file. The Per-File stage runs the existing L0–L4 pipeline on it. The Relationship Mapping stage finds external links only (no internal files to map to). The Ecosystem Validation stage emits I010 (single-file ecosystem — valid but limited). The Ecosystem Score reports a single-file ecosystem with a coverage gap.

**Nothing breaks for the single-file use case.** The ecosystem layer is additive.

---

## 8. Context Compression: A DocStratum Opportunity

### 8.1 What Context Compression Means

Context compression is the practice of encoding maximum information in minimum tokens while remaining machine-parseable. It's not a formalized standard — it's an emerging set of patterns that authors use (often unconsciously) when writing documentation optimized for LLM consumption.

DocStratum is uniquely positioned to both **detect** these patterns (in the validator) and **recommend** them (in the diagnostic remediations). No other tool in the ecosystem does this.

### 8.2 Compression Patterns to Detect and Reward

| Pattern | Description | Token Efficiency vs. Prose | Detection Method |
|---------|-------------|---------------------------|-----------------|
| **Structured tables** | Information organized in Markdown tables with headers | 3–5x more efficient | AST: count table nodes vs. paragraph nodes for similar content |
| **Code signatures** | Function/class signatures instead of prose explanations | 4–6x more efficient | AST: code blocks containing function definitions |
| **DO/DON'T pairs** | Explicit behavioral instructions for agents | 2–3x more efficient | Pattern matching: "DO:" / "DON'T:" or "✓" / "✗" patterns |
| **Key-value definitions** | `Term: definition` format for concepts | 2–4x more efficient | Pattern matching: definition-list patterns, colon-separated pairs |
| **Few-shot examples** | Input/output pairs demonstrating behavior | Most efficient teaching method | Heuristic: paired code blocks, Q&A patterns, "Example:" headers |
| **Hierarchical links** | Indented link lists showing relationship depth | N/A (structural, not compression) | AST: nested list items with links |

### 8.3 Anti-Compression Patterns to Flag

| Anti-Pattern | Description | Token Waste | Detection Method |
|-------------|-------------|-------------|-----------------|
| **Prose where tables would work** | Paragraph descriptions of tabular data (parameters, options, configs) | 3–5x wasteful | Heuristic: paragraphs containing repeated "the X parameter is Y" patterns |
| **Redundant introductions** | "In this section, we will discuss..." style padding | 100% waste | Pattern matching: common filler phrases |
| **Marketing in docs** | Superlatives, value propositions, competitive claims | 100% waste (from LLM perspective) | Existing: anti-pattern detection from v0.0.4c |
| **Duplicated definitions** | Same concept defined in multiple places within the ecosystem | Proportional to duplication | Cross-file: pairwise content similarity analysis |

### 8.4 Future: A Context Compression Score

As a future enhancement (post-MVP), DocStratum could calculate a **compression efficiency score** — a ratio of information density to token count. This would answer the question: "How much useful information per token does this ecosystem deliver?"

This is speculative and not part of the MVP pivot, but it's worth flagging as a differentiation opportunity that flows naturally from the ecosystem model.

---

## 9. Content Page Validation Rules

### 9.1 What Makes a Good Content Page?

Content pages (individual `.md` files linked from the index) serve a different purpose than the index itself. They're designed to be fetched individually by an MCP-based agent that followed a link from the index. This means they need to be:

1. **Self-contained** — Understandable without reading the index first
2. **Focused** — About one topic, not a grab-bag
3. **Token-budgeted** — Reasonable size for context injection (1K–8K tokens recommended)
4. **Cross-referenced** — Link back to related content and to the index

### 9.2 Content Page Validation Criteria

| ID | Criterion | Description | Diagnostic Code |
|----|-----------|-------------|-----------------|
| CP-01 | Has title | Content page must have an H1 heading | E001 (reused) |
| CP-02 | Self-contained opening | First paragraph should identify the topic without assuming prior context | New heuristic check |
| CP-03 | Reasonable size | Between 500 and 8,000 tokens | W010 (reused with adjusted thresholds) |
| CP-04 | No orphaned references | Links to other content pages should resolve within the ecosystem | W012 (ecosystem code) |
| CP-05 | Consistent terminology | Key terms should match definitions used in other ecosystem files | W015/W016 (ecosystem codes) |

---

## 10. Impact on Existing Design Documents

### 10.1 Documents That Stand As-Is

These research documents require **no changes** — their findings are still valid and still inform the pivot:

| Document | Why It Stands |
|----------|---------------|
| v0.0.0 — Research & Discovery | Initial questions still relevant |
| v0.0.1 — Specification Deep Dive | Spec analysis unchanged |
| v0.0.1a — Formal Grammar & Parsing Rules | Grammar applies per-file, unchanged |
| v0.0.1b — Spec Gap Analysis | All 8 gaps still valid; ecosystem addresses some |
| v0.0.1c — Processing & Expansion Methods | Processing methods still apply per-file |
| v0.0.1d — Standards Interplay & Positioning | Standards landscape unchanged |
| v0.0.2 — Wild Examples Audit | All specimen data still valid |
| v0.0.2a — Source Discovery & Collection | Collection methodology still valid |
| v0.0.2b — Individual Example Audits | Per-file audits still valid |
| v0.0.2c — Pattern Analysis & Statistics | Statistical findings still valid |
| v0.0.2d — Synthesis & Recommendations | Recommendations still valid |
| v0.0.3 — Ecosystem & Tooling Survey | Survey data still valid |
| v0.0.3a — Tools & Libraries Inventory | Tool inventory unchanged |
| v0.0.3b — Key Players & Community Pulse | Community data unchanged |
| v0.0.3c — Related Standards & Competing Approaches | Standards landscape unchanged |
| v0.0.4 — Best Practices Synthesis | Per-file best practices unchanged |
| v0.0.4a — Structural Best Practices | Structural rules apply per-file |
| v0.0.4b — Content Best Practices | Content rules apply per-file |
| v0.0.4c — Anti-Patterns Catalog | All 22 anti-patterns still valid; 6 new ones added |
| v0.0.4d — Differentiators & Decision Log | All 16 decisions still valid |
| v0.0.6 — Platinum Standard Definition | Per-file standard unchanged; ecosystem standard is additive |

### 10.2 Documents That Need Revision

| Document | What Changes | Effort |
|----------|-------------|--------|
| v0.0.3d — Gap Analysis & Opportunity Map | Add ecosystem-level opportunity; update market positioning | Low — add section |
| v0.0.5 — Requirements Definition | Add ecosystem-level functional requirements | Medium — new requirements |
| v0.0.5a — Functional Requirements | Add FR-070+ for ecosystem features | Medium — new section |
| v0.0.5b — Non-Functional Requirements | Add NFR for ecosystem scan performance | Low — add 2-3 NFRs |
| v0.0.5c — Scope Definition | Update in-scope to include ecosystem; move some OOS items in | Medium — scope revision |
| v0.0.5d — Success Criteria & MVP Definition | Add ecosystem acceptance test scenarios; revise feature count | Medium — new scenarios |
| v0.0.x — Consolidated Research Synthesis | Add Section 9: Ecosystem Pivot findings | Low — add section |

### 10.3 Foundation Documents That Need Revision

| Document | What Changes | Effort |
|----------|-------------|--------|
| v0.1.0 — Project Foundation | Update project description to reflect ecosystem scope | Low |
| v0.1.2 — Schema Definition | Add new entities (EcosystemFile, FileRelationship, DocumentEcosystem, EcosystemScore) | High — core schema work |
| v0.1.2a — Diagnostic Infrastructure | Add 12 new diagnostic codes | Medium |
| v0.1.2b — Document Models | Add ecosystem-level models; extend DocumentType, ParsedLink | High |
| v0.1.2c — Validation & Quality Models | Add EcosystemScore, EcosystemHealthDimension | Medium |
| v0.1.2d — Enrichment Models | Consider ecosystem-level enrichment | Low |
| v0.1.3 — Sample Data | Add multi-file test fixtures | Medium |
| v0.1.3a — Fixture Suite | Add ecosystem test fixtures (index + content pages + aggregate) | Medium |
| v0.1.3b — Test Infrastructure | Add ecosystem-level test helpers | Medium |

### 10.4 Meta Documents That Need Revision

| Document | What Changes | Effort |
|----------|-------------|--------|
| RR-META-specs.md | Add v0.0.6 and v0.0.7 references | Low |
| RR-META-llms-txt-architect.md | Update role description to include ecosystem awareness | Low |

---

## 11. Phased Migration Plan

### Phase 1: Design Doc Updates (Current Priority)

**Goal:** Bring all design documents up to date with the ecosystem vision.

1. Write this document (v0.0.7) — ✅ DONE
2. Revise v0.0.5c (Scope Definition) — add ecosystem in-scope items
3. Revise v0.0.5d (Success Criteria) — add ecosystem acceptance scenarios
4. Revise v0.0.5a (Functional Requirements) — add ecosystem FRs
5. Update v0.0.x (Consolidated Synthesis) — add ecosystem findings section
6. Update meta docs (specs, architect guide)

### Phase 2: Schema Extension

**Goal:** Extend the existing schema to support ecosystem entities.

1. Add `DocumentType.TYPE_3_CONTENT_PAGE` and `TYPE_4_INSTRUCTIONS`
2. Add `LinkRelationship` enum and extend `ParsedLink`
3. Add `EcosystemFile`, `FileRelationship`, `DocumentEcosystem` models
4. Add `EcosystemHealthDimension`, `EcosystemScore` models
5. Add 12 new diagnostic codes (E009–E010, W012–W018, I008–I010)
6. Add 6 new ecosystem anti-patterns (AP_ECO_001–006)
7. Extend `ValidationDiagnostic` with cross-file context fields
8. Update `__init__.py` exports

### Phase 3: Pipeline Extension

**Goal:** Build the ecosystem validation pipeline on top of the existing single-file pipeline.

1. Build the Discovery stage (scan project root, follow links, build manifest)
2. Run existing per-file pipeline on each discovered file (no changes to existing pipeline)
3. Build the Relationship Mapping stage (classify links, check resolution)
4. Build the Ecosystem Validation stage (coverage, consistency, completeness checks)
5. Build the Ecosystem Scoring stage (5 dimensions, composite score)

### Phase 4: Test Infrastructure

**Goal:** Validate the ecosystem pipeline with realistic multi-file fixtures.

1. Create ecosystem test fixtures (healthy ecosystem, broken links, missing aggregate, etc.)
2. Write per-file validation tests (ensuring backward compatibility)
3. Write cross-file validation tests (new ecosystem checks)
4. Write ecosystem scoring tests (calibrate against expectations)
5. Integration tests: single-file input still works identically

---

## 12. Open Questions

1. **How should the ecosystem be discovered?** Three options: (a) scan a local directory, (b) crawl from a URL starting at llms.txt, (c) accept a manifest file listing all ecosystem members. The crawler approach is most practical for the web case; the directory scan is most practical for the local/MCP case. Both should probably be supported.

2. **What file extensions qualify as content pages?** `.md` is obvious. What about `.mdx` (MDX)? `.txt`? `.rst` (reStructuredText)? For MVP, `.md` only seems right, with extension support later.

3. **How should the ecosystem score weight per-file scores vs. relationship scores?** One approach: 60% aggregate of per-file scores, 40% ecosystem-level dimensions. Another: ecosystem dimensions are independent and don't factor in per-file scores at all. The latter is simpler and avoids double-counting.

4. **Should DocStratum generate ecosystem reports?** Beyond just scoring, should it produce a Markdown or HTML report showing the full ecosystem graph, per-file scores, and remediation recommendations? This seems high-value but is MVP-scope-expanding.

5. **How does the ecosystem model handle monorepos?** A monorepo might have multiple independent llms.txt files (one per package). Are these separate ecosystems or sub-ecosystems? For MVP, treating each llms.txt as a separate ecosystem root seems simplest.

---

## 13. Revision History

| Date | Version | Change |
|------|---------|--------|
| 2026-02-07 | v0.0.7-draft | Initial draft — defines ecosystem pivot with new entities, diagnostic codes, anti-patterns, and migration plan |

---

## 14. Cross-References

| Document | Relevance |
|----------|-----------|
| v0.0.6 — Platinum Standard Definition | Per-file standard that the ecosystem wraps |
| v0.0.1b — Spec Gap Analysis | Gap #1 (file size) motivates per-file budgets; Gap #2 (metadata) motivates consistency checks |
| v0.0.2c — Pattern Analysis | Audit data informing ecosystem coverage expectations |
| v0.0.4c — Anti-Patterns Catalog | Base 22 patterns; extended with 6 ecosystem patterns |
| v0.0.5c — Scope Definition | Needs revision to include ecosystem scope |
| v0.0.5d — Success Criteria | Needs revision to include ecosystem acceptance scenarios |
| v0.1.2b — Document Models | Core models being extended |
| v0.1.2c — Validation & Quality Models | Quality models being extended |
