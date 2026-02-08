# v0.0.5a — Functional Requirements Specification

> **Sub-Part:** Define comprehensive functional requirements using formal requirement IDs (FR-###), organized by module, with acceptance tests and traceability to research (v0.0.x) and target implementation (v0.x.x).

---

> **REVISION NOTICE — v0.0.7 Ecosystem Pivot (2026-02-07)**
>
> This document was revised following the strategic pivot defined in `RR-SPEC-v0.0.7-ecosystem-pivot-specification.md`. A new module (Section 10: Ecosystem Discovery & Validation) was added containing 17 functional requirements (FR-069 through FR-085). Changes are marked with `[v0.0.7]` tags. Original requirements (FR-001 through FR-068) are unchanged.
>
> **Impact summary:** FR count 68 → 85. Module count 7 → 8. MUST count 32 → 45. SHOULD count 29 → 33. COULD count unchanged at 7. Coverage matrix updated.

---

## Sub-Part Overview

This sub-part converts the collective findings from four completed research phases — v0.0.1 (Specification Deep Dive), v0.0.2 (Wild Examples Audit), v0.0.3 (Ecosystem Survey), and v0.0.4 (Best Practices Synthesis) — into 68 formally identified functional requirements (FR-001 through FR-068). Requirements are organized across 7 software modules (Schema & Validation, Content Structure, Parser & Loader, Context Builder, Agent Integration, A/B Testing Harness, and Demo Layer) plus 3 cross-module concerns. Each requirement carries a unique ID, MoSCoW priority, acceptance test, research source trace, and target implementation module — forming a complete traceability chain from research evidence through specification to implementation target.

**Distribution:** 32 MUST requirements define the MVP, 29 SHOULD requirements strengthen quality and usability, and 7 COULD requirements represent stretch goals. All 68 requirements trace to at least one completed research phase and forward-map to a specific implementation module in v0.1.x–v0.6.x.

---

## Objective

This sub-part transforms the findings from v0.0.1–v0.0.4 research phases into a precise, implementable specification. Each functional requirement is formally identified, prioritized via MoSCoW, tied to acceptance tests, and traced to both the research that justified it and the implementation module that will fulfill it.

### Success Looks Like

- 30+ formally identified functional requirements (FR-001 through FR-035+)
- Clear module-level organization matching project architecture
- Every requirement has: ID, description, priority, acceptance test, source, target module
- Traceability in both directions: research → requirement and requirement → implementation
- No ambiguity about what "done" means for each feature

---

## Scope Boundaries

### In Scope

- Defining what DocStratum MUST do (functional behavior)
- Organizing requirements by software module
- Specifying acceptance tests for each requirement
- Tracing requirements to research sources and implementation targets
- MoSCoW prioritization across all requirements

### Out of Scope

- Non-functional aspects (NFRs are v0.0.5b)
- Scope boundaries (that's v0.0.5c)
- Success metrics and test scenarios (those are v0.0.5d)
- Implementation details or code design
- Detailed API signatures or database schema

---

## Dependencies

```
v0.0.1 — Specification Deep Dive (COMPLETED)
    ├── Base llms.txt spec structure
    ├── Official grammar and semantics
    └── Gap identification

v0.0.1a — Formal Grammar & Parsing Rules (COMPLETED)
    ├── ABNF grammar definitions
    ├── Validation levels 0–4
    ├── Error code registry
    └── Parser pseudocode

v0.0.1c — Context & Processing Patterns (COMPLETED)
    ├── Processing methods (discovery, synthesis, ranking)
    ├── Token budgeting concepts
    └── Hybrid pipeline architecture

v0.0.2 — Wild Examples Audit (COMPLETED)
    ├── Real-world llms.txt variations
    ├── Common patterns and anti-patterns
    └── Schema extension needs

v0.0.4 — Best Practices Synthesis (COMPLETED)
    ├── Recommended structure patterns
    ├── Agent integration patterns
    └── Quality indicators

                            v
v0.0.5a — Functional Requirements (THIS TASK)
                            │
        ┌───────────────────┼───────────────────┐
        v                   v                   v
    v0.1.0            v0.2.0              v0.3.0
  (Schema &        (Validation &      (Parsing &
   Validation)      Context Build)     Loading)
```

---

## 1. Requirements Organization by Module

### Module Hierarchy

```
DocStratum System
├── Schema & Validation (FR-001 to FR-012)
├── Content Structure (FR-013 to FR-025)
├── Parser & Loader (FR-026 to FR-031)
├── Context Builder (FR-032 to FR-038)
├── Agent Integration (FR-039 to FR-050)
├── A/B Testing Harness (FR-051 to FR-058)
└── Demo Layer (FR-059 to FR-065)
```

---

## 2. Schema & Validation Module (FR-001 to FR-012)

### Objective

Define the data structures and validation rules that ensure llms.txt files (both standard and extended) are syntactically correct, semantically valid, and type-safe throughout the system.

| ID | Requirement | Priority | Acceptance Test | Source | Target Module |
|---|---|---|---|---|---|
| FR-001 | Pydantic models for base llms.txt structure (LlmsTxtDocument, Section, FileEntry) | MUST | Define models with 3+ fields per model, instantiate with sample data, verify serialization | v0.0.1a (grammar) | v0.1.1 (Schema) |
| FR-002 | Extended DocStratum schema fields (concept_id, layer_num, few_shot_type) in FileEntry model | MUST | Add optional fields to FileEntry; parse extended llms.txt without error; verify backward compat | v0.0.2 (patterns) | v0.1.2 (Extended Schema) |
| FR-003 | Validation Level 0 (SYNTAX): Enforce valid line format and character encoding | MUST | Feed malformed entries (missing brackets, bad URLs) to validator; verify E-series errors generated | v0.0.1a (error codes) | v0.2.1 (Validator L0) |
| FR-004 | Validation Level 1 (STRUCTURE): Verify H1 title, at least one H2, and entry counts | MUST | Test files missing H1/H2; verify W-series warnings; empty sections flagged | v0.0.1a (grammar) | v0.2.1 (Validator L1) |
| FR-005 | Validation Level 2 (CONTENT): Check descriptions non-empty, URLs resolvable (optional check), no empty fields | SHOULD | Test URLs with live resolve; flag missing descriptions; verify partial URLs accepted with warning | v0.0.1 (spec) | v0.2.2 (Validator L2) |
| FR-006 | Validation Level 3 (QUALITY): Measure description length, diversity of sections, metadata completeness | SHOULD | Compute length stats; flag overly short/long descriptions; verify against quality thresholds | v0.0.4 (best practices) | v0.2.3 (Validator L3) |
| FR-007 | Validation Level 4 (DOCSTRATUM): Verify extended schema fields present, layer assignments valid, concept refs resolvable | MUST | Parse extended llms.txt; verify all concept_id refs exist; layer_num in range [0,2]; few_shot_type in enum | v0.0.2 (patterns) | v0.2.4 (Validator L4) |
| FR-008 | Error reporting with line numbers, error codes, severity levels, and human-readable messages | MUST | Generate 10+ error scenarios; verify each error includes line#, code (E/W/I), severity, message | v0.0.1a (error registry) | v0.2.1 (ErrorReporter) |
| FR-009 | Validation pipeline supports configuration (which levels to run, which checks to enable) | SHOULD | Create config; skip level 2 check; verify only L0–L1 run; modify thresholds and re-run | v0.0.4 (quality standards) | v0.2.5 (Config) |
| FR-010 | Per-section validation: Validate "Optional" sections semantically distinct (flag entries as non-required) | SHOULD | Parse llms.txt with "Optional" H2; verify entries in that section flagged; verify others not flagged | v0.0.1 (spec) | v0.2.2 (SemanticValidator) |
| FR-011 | Schema supports round-trip (parse → validate → serialize → re-parse with no loss) | MUST | Load llms.txt; serialize to JSON; deserialize; verify document identity | v0.0.1a (grammar) | v0.1.3 (Serialization) |
| FR-012 | Validation output includes summary (total issues, by severity, top 3 issues) | SHOULD | Run validator on 5 files; verify summary shows count and breakdown; top 3 listed | v0.0.4 (usability) | v0.2.6 (Reporting) |

---

## 3. Content Structure Module (FR-013 to FR-025)

### Objective

Implement the 3-layer architecture (Master Index, Concept Map, Few-Shot Bank) that transforms a standard llms.txt into a rich knowledge structure for agent use.

| ID | Requirement | Priority | Acceptance Test | Source | Target Module |
|---|---|---|---|---|---|
| FR-013 | Layer 0 (Master Index) implementation: URL index with metadata (domain, title, section, freshness) | MUST | Load llms.txt; extract 10+ entries; build index with title, URL, section, created_date fields | v0.0.1c (processing methods) | v0.3.2 (MasterIndexBuilder) |
| FR-014 | Layer 0: Assign freshness signals (evergreen, current, deprecated, archived) based on URL/description patterns | SHOULD | Parse entries with version numbers, date markers, deprecation notices; assign freshness; verify 80%+ accuracy on audit set | v0.0.4 (best practices) | v0.3.2 (FreshnessDetector) |
| FR-015 | Layer 0: URL canonicalization (resolve redirects, normalize trailing slash, strip tracking params) | SHOULD | Test 5+ URLs with redirects; verify canonical form extracted; verify tracking params stripped | v0.0.2 (patterns) | v0.3.2 (URLCanonicalizer) |
| FR-016 | Layer 1 (Concept Map) implementation: Extract concepts from descriptions and titles | MUST | Parse descriptions; identify 5–20 distinct concepts per llms.txt; assign IDs (concept_001, etc.) | v0.0.1c (concept extraction) | v0.4.1 (ConceptMapper) |
| FR-017 | Layer 1: Build concept graph with edges (depends_on, relates_to, conflicts_with, specializes) | SHOULD | Create 20+ concept pairs; assign relationship types; verify acyclic (no circular deps); serialize to DOT/JSON | v0.0.1c (relationship modeling) | v0.4.1 (GraphBuilder) |
| FR-018 | Layer 1: Define concept ambiguity resolution (homonym detection, context-specific definitions) | SHOULD | Identify terms appearing in multiple sections with different meanings; flag as ambiguous; flag context | v0.0.4 (disambiguation) | v0.4.2 (AmbiguityResolver) |
| FR-019 | Layer 1: Assign "authority" metadata to concepts (which entries are canonical definitions) | SHOULD | For each concept, identify primary entry; mark others as "references" or "uses"; verify one primary per concept | v0.0.4 (best practices) | v0.4.1 (AuthorityAssigner) |
| FR-020 | Layer 2 (Few-Shot Bank) implementation: Extract Q&A pairs from content and documentation | MUST | Parse 3+ llms.txt files; manually extract 5+ Q&A pairs per file; store with source/concept refs | v0.0.1c (few-shot patterns) | v0.5.1 (QAExtractor) |
| FR-021 | Layer 2: Categorize few-shot examples by type (definition, usage, comparison, error_handling, integration) | SHOULD | Tag 50+ extracted examples with type; verify distribution across all types; verify examples match intent | v0.0.4 (pattern library) | v0.5.1 (ExampleClassifier) |
| FR-022 | Layer 2: Support templated few-shot generation (slot-filling from concepts to create question variations) | COULD | Define template: "How do I [VERB] [CONCEPT]?"; generate 10+ variations by substituting slots | v0.0.1c (synthesis) | v0.5.2 (TemplateEngine) |
| FR-023 | Layer 2: Quality scoring for examples (clarity, relevance, completeness) on 0–10 scale | SHOULD | Score 20+ examples; compute distribution; flag low-scoring (<5) for review; identify common failure modes | v0.0.4 (quality) | v0.5.3 (QAScorer) |
| FR-024 | Three-layer integration: Resolve cross-layer references (entries → concepts → examples) | MUST | Navigate from FileEntry to concept to few-shot example; verify reference chain works bidirectionally | v0.0.1c (hybrid pipeline) | v0.3.3 (LayerLinker) |
| FR-025 | Export all three layers in JSON/YAML format, preserving structure and references | MUST | Serialize all layers to JSON; deserialize; verify no data loss; verify all references still valid | v0.0.1a (grammar) | v0.3.4 (Serializer) |

---

## 4. Parser & Loader Module (FR-026 to FR-031)

### Objective

Implement robust parsing of llms.txt files (both standard and extended) with comprehensive edge-case handling and error recovery.

| ID | Requirement | Priority | Acceptance Test | Source | Target Module |
|---|---|---|---|---|---|
| FR-026 | Parser: Load and parse standard llms.txt (RFC 3986 compliance) from URL or file path | MUST | Load 10+ llms.txt files from URLs and local paths; parse all successfully; verify no loss of data | v0.0.1a (grammar) | v0.3.1 (Loader) |
| FR-027 | Parser: Handle all line-ending variations (LF, CRLF, CR) transparently | MUST | Test files with each line ending type; verify consistent parsing and output | v0.0.1a (grammar) | v0.3.1 (LineNormalizer) |
| FR-028 | Parser: Recover from malformed entries (missing brackets, invalid URLs) with partial parsing | SHOULD | Feed 5+ malformed files; verify parser continues (returns partial results); verify no silent data loss | v0.0.1a (error recovery) | v0.3.1 (ErrorRecovery) |
| FR-029 | Parser: Support extended llms.txt with DocStratum schema fields (YAML front matter, structured metadata) | SHOULD | Create extended llms.txt with custom fields; parse successfully; verify extended fields preserved | v0.0.2 (extensions) | v0.3.1 (ExtendedParser) |
| FR-030 | Loader: Cache parsed files (by URL + hash) to avoid re-parsing; invalidation on TTL or manual force | SHOULD | Parse same URL twice; verify second load is from cache (timing < 10ms); force reload; verify fresh parse | v0.0.1c (token budgeting) | v0.3.1 (CacheManager) |
| FR-031 | Loader: Provide streaming/chunked access for large files to support memory-constrained agents | COULD | Parse 50MB+ file in chunks; load sections on-demand; verify streaming API works | v0.0.1c (token budgeting) | v0.3.1 (StreamLoader) |

---

## 5. Context Builder Module (FR-032 to FR-038)

### Objective

Transform parsed llms.txt and concept maps into optimized agent context, respecting token budgets and information relevance.

| ID | Requirement | Priority | Acceptance Test | Source | Target Module |
|---|---|---|---|---|---|
| FR-032 | Processing methods: Implement all v0.0.1c processing methods (discovery, synthesis, ranking, filtering) | MUST | Apply each method to 5+ llms.txt files; verify results are distinct and meaningful | v0.0.1c (processing methods) | v0.4.3 (ContextProcessor) |
| FR-033 | Token budgeting: Estimate tokens for each layer (Master Index, Concept Map, Few-Shot Bank) | MUST | Measure token count for each layer; store estimates; use in context selection algorithm | v0.0.1c (token budgeting) | v0.4.3 (TokenEstimator) |
| FR-034 | Hybrid pipeline: Combine layers (0, 1, 2) into single agent context respecting token budget | MUST | Load llms.txt; build all layers; pack into context w/ 4K token limit; verify relevance > baseline | v0.0.1c (hybrid pipeline) | v0.4.4 (PipelineOrchestrator) |
| FR-035 | Query-aware context selection: Given a query, select most relevant entries, concepts, examples | MUST | Feed 10+ test queries; verify top-3 results are relevant; compare with keyword match baseline | v0.0.4 (agent testing) | v0.4.4 (QuerySelector) |
| FR-036 | Context filtering: Remove low-utility entries (empty sections, duplicate concepts, low-quality examples) | SHOULD | Mark 20+ entries as low-utility; filter them; verify filtered context is 20–30% smaller | v0.0.4 (best practices) | v0.4.3 (ContextFilter) |
| FR-037 | Context ranking: Prioritize entries by relevance (freshness, authority, specificity) using configurable weights | SHOULD | Rank entries for 5+ queries; expose weights; modify weights; re-rank; verify results change appropriately | v0.0.4 (best practices) | v0.4.4 (Ranker) |
| FR-038 | Fallback context: If no entries match query, provide semantic fallback (related concepts, generalized examples) | COULD | Query for non-existent concept; verify agent still receives related context from concept map | v0.0.1c (synthesis) | v0.4.4 (FallbackSelector) |

---

## 6. Agent Integration Module (FR-039 to FR-050)

### Objective

Integrate DocStratum context into LLM agents and demonstrate improved performance through A/B testing.

| ID | Requirement | Priority | Acceptance Test | Source | Target Module |
|---|---|---|---|---|---|
| FR-039 | Baseline agent: Implement reference agent using raw llms.txt (no DocStratum enhancements) | MUST | Create LangChain agent with raw llms.txt prompt; verify it answers 5+ test queries | v0.0.4 (agent patterns) | v0.5.0 (BaselineAgent) |
| FR-040 | Enhanced agent: Implement DocStratum-enhanced agent with optimized context + system prompt injection | MUST | Create agent with full pipeline (layers 0–2); verify it can answer same 5+ queries with better accuracy | v0.0.4 (agent patterns) | v0.5.0 (DocStratumAgent) |
| FR-041 | System prompt injection: Design two distinct system prompts (generic vs. DocStratum-aware) | MUST | Write prompts; verify generic prompt does not reference concept map; DocStratum prompt does; both accepted by agent | v0.0.1c (agent patterns) | v0.5.1 (PromptDesigner) |
| FR-042 | Context window management: Cap context + prompt + query to model's max tokens; prefer quality over quantity | MUST | Build context; measure total tokens; if > limit, filter to fit; verify no truncation mid-sentence | v0.0.1c (token budgeting) | v0.4.3 (TokenManager) |
| FR-043 | Error handling in agent: If context load fails, degrade gracefully (use raw llms.txt); log error | SHOULD | Simulate context builder failure; verify agent continues with fallback; error logged | v0.0.4 (reliability) | v0.5.0 (ErrorHandler) |
| FR-044 | Support multiple LLM providers (OpenAI, Claude via Anthropic API, local via LiteLLM) | SHOULD | Create agents with 2+ different provider configs; verify both work; compare outputs | v0.0.4 (compatibility) | v0.5.0 (LLMProvider) |
| FR-045 | Agent configuration: Expose tunable parameters (model, temperature, top_p, context_layers) | SHOULD | Create config file; modify 3+ parameters; re-run agent; verify changes take effect | v0.0.4 (usability) | v0.5.0 (Config) |
| FR-046 | Retrieval strategy: Implement keyword search, semantic search (embedding-based), and hybrid | SHOULD | Test each strategy on 10+ queries; measure precision/recall; expose strategy choice in config | v0.0.1c (processing methods) | v0.4.4 (Retriever) |
| FR-047 | Few-shot in-context learning: Inject 3–5 Q&A examples before main agent query | MUST | Select 3 most relevant examples for query; prepend to agent prompt; verify agent references them | v0.0.1c (few-shot) | v0.5.1 (FewShotInjector) |
| FR-048 | Agent testing harness: Compare baseline vs. enhanced agent on same query set | MUST | Run both agents on 20+ test queries; measure accuracy, latency, token usage; display comparison | v0.0.4 (test harness) | v0.5.2 (TestHarness) |
| FR-049 | Trace and logging: Log all agent decisions (context selected, prompt used, model response, latency) | SHOULD | Run agent; inspect logs; verify trace includes decision info; exportable as JSON | v0.0.4 (debugging) | v0.5.2 (Logger) |
| FR-050 | Support agent templates (chatbot, Q&A bot, documentation copilot) with different prompt strategies | COULD | Implement 2 templates; compare outputs for same query; verify template effects visible | v0.0.4 (patterns) | v0.5.3 (Templates) |

---

## 7. A/B Testing Harness Module (FR-051 to FR-058)

### Objective

Implement rigorous A/B testing infrastructure to quantify DocStratum's impact on agent performance.

| ID | Requirement | Priority | Acceptance Test | Source | Target Module |
|---|---|---|---|---|---|
| FR-051 | Query runner: Load test queries from file; run each against baseline and enhanced agent | MUST | Load 20+ test queries; run both agents; collect results (response, latency, tokens) | v0.0.4 (test design) | v0.5.2 (QueryRunner) |
| FR-052 | Response comparison: Analyze baseline vs. enhanced responses for accuracy, completeness, relevance | MUST | Implement 3+ comparison metrics; score 20+ response pairs; show side-by-side diffs | v0.0.4 (test design) | v0.5.2 (ResponseAnalyzer) |
| FR-053 | Metrics collection: Capture accuracy (LLM judge score), latency, token usage, success rate | MUST | Run tests; collect all metrics; compute mean/std/percentiles; export as table | v0.0.4 (test design) | v0.5.2 (MetricsCollector) |
| FR-054 | Statistical significance: Compute p-values for accuracy improvements; verify not due to chance | SHOULD | Run 50+ test pairs; compute t-test p-value; flag as significant if p < 0.05 | v0.0.4 (test design) | v0.5.2 (StatisticsEngine) |
| FR-055 | Baseline definition: Establish quantitative baseline metrics (accuracy, latency, tokens) | MUST | Run baseline agent on 50+ queries; compute mean metrics; store as benchmark | v0.0.4 (test design) | v0.5.2 (BaselineRecorder) |
| FR-056 | Test query design: Include 4 test categories (disambiguation, freshness, few-shot, integration) | MUST | Create 5+ queries per category (20+ total); verify each tests intended capability | v0.0.4 (differentiators) | v0.5.2 (TestDesigner) |
| FR-057 | Test result export: Save results (queries, responses, scores, metrics) to JSON/CSV for analysis | MUST | Run tests; export to both formats; verify parseable; verify all data present | v0.0.4 (reporting) | v0.5.2 (Exporter) |
| FR-058 | Regression testing: Re-run baseline tests automatically to catch performance regressions | SHOULD | Store baseline results; modify code; re-run; compare; flag if regression > 5% | v0.0.4 (quality) | v0.5.2 (Regression Tester) |

---

## 8. Demo Layer Module (FR-059 to FR-065)

### Objective

Create a user-friendly Streamlit demo application that showcases DocStratum's value through interactive side-by-side agent comparison.

| ID | Requirement | Priority | Acceptance Test | Source | Target Module |
|---|---|---|---|---|---|
| FR-059 | Streamlit UI: Load llms.txt (URL or file upload); display parsed structure and validation results | MUST | Deploy Streamlit app; upload llms.txt; verify parsed structure displayed; validation results shown | v0.0.4 (demo) | v0.6.0 (StreamlitApp) |
| FR-060 | Side-by-side agent view: Show query input; run both agents; display responses in parallel columns | MUST | Type query in app; click "Run"; verify baseline response in left column, enhanced in right column | v0.0.4 (demo) | v0.6.0 (SideBySideView) |
| FR-061 | Metrics display: Show comparison metrics (accuracy, latency, tokens) with visual indicators (badges, charts) | SHOULD | Run demo query; display accuracy scores, latency in ms, token counts; use color to highlight winner | v0.0.4 (demo) | v0.6.0 (MetricsDisplay) |
| FR-062 | Concept map visualization: Interactive graph showing concepts and relationships | COULD | Render D3.js or Plotly graph; allow click-to-expand; show edges and node metadata on hover | v0.0.1c (concept map) | v0.6.0 (GraphVisualizer) |
| FR-063 | Few-shot examples sidebar: List few-shot examples relevant to current query | SHOULD | As user types query, update sidebar to show top 3 relevant examples; highlight matching concepts | v0.0.1c (few-shot) | v0.6.0 (ExamplesSidebar) |
| FR-064 | Settings panel: Allow user to adjust context layers, retrieval strategy, model, temperature | SHOULD | Expose toggles for Layer 0/1/2, choice of retrieval, model selection; verify changes affect agent output | v0.0.4 (usability) | v0.6.0 (SettingsPanel) |
| FR-065 | Session persistence: Save uploaded llms.txt and test queries to session; restore on page reload | COULD | Upload file; refresh page; verify file still present; run query; verify history restored | v0.0.4 (usability) | v0.6.0 (SessionManager) |

---

## 9. Cross-Module Requirements

| ID | Requirement | Priority | Acceptance Test | Source | Target Module |
|---|---|---|---|---|---|
| FR-066 | Dependency injection: All modules accept dependencies via constructor or config, support mocking | SHOULD | Instantiate module with mock dependency; verify behavior uses injected mock | v0.0.4 (testability) | v0.2.0 (DependencyInjection) |
| FR-067 | Logging: All modules log key decisions (loaded file, parsed entries, context selected) at INFO level | SHOULD | Run full pipeline; inspect logs; verify all key steps logged with relevant details | v0.0.4 (debugging) | v0.2.0 (Logger) |
| FR-068 | Telemetry: Optionally record anonymized metrics (file size, layer counts, query counts) | COULD | Enable telemetry; run demo; verify metrics recorded (optionally sent to analytics endpoint) | v0.0.4 (observability) | v0.2.0 (Telemetry) |

---

## [v0.0.7] 10. Ecosystem Discovery & Validation Module (FR-069 to FR-085)

> **Added:** 2026-02-07 per v0.0.7 Ecosystem Pivot Specification.
> **Rationale:** DocStratum's scope expanded from single-file validator to ecosystem-level documentation quality platform. These 17 requirements define the ecosystem layer that wraps the existing per-file pipeline.
> **Source:** v0.0.6 (Platinum Standard Definition), v0.0.7 (Ecosystem Pivot Specification)
> **Backward Compatibility:** All ecosystem FRs are additive. A single-file input MUST produce identical output to the pre-pivot design (see FR-083).

### 10.1 Ecosystem Schema Models (FR-069 to FR-073)

| ID | Requirement | Priority | Acceptance Test | Source | Target Module |
|---|---|---|---|---|---|
| FR-069 | `DocumentEcosystem` model: Top-level Pydantic model representing a complete documentation ecosystem with a root index file, file manifest, relationship graph, and aggregate health score | MUST | Instantiate `DocumentEcosystem` with 1 index + 2 content pages; verify `file_count == 3`, `index_file` returns the llms.txt, `content_pages` returns 2 pages, serialization round-trips to JSON | v0.0.7 (Section 4.3) | v0.1.2 (EcosystemSchema) |
| FR-070 | `EcosystemFile` model: Wraps a parsed file with ecosystem-level metadata including file ID, type classification, per-file validation results, per-file quality score, and relationship list | MUST | Create `EcosystemFile` from existing `ParsedLlmsTxt`; verify `file_id` is unique UUID, `file_type` matches classification, `validation` and `quality` fields accept existing model instances | v0.0.7 (Section 4.3) | v0.1.2 (EcosystemSchema) |
| FR-071 | `FileRelationship` model: Represents a directed relationship between two ecosystem files (INDEXES, REFERENCES, AGGREGATES, EXTERNAL) with source line, target URL, and resolution status | MUST | Create relationship from llms.txt link → content page; verify `relationship_type == INDEXES`, `is_resolved == True` when target exists, `is_resolved == False` when target missing | v0.0.7 (Section 4.3) | v0.1.2 (EcosystemSchema) |
| FR-072 | `EcosystemScore` model: Aggregate health score with per-dimension breakdown (Completeness, Coverage), per-file score map, and overall grade using existing `QualityGrade` enum | MUST | Score a 3-file ecosystem; verify `total_score` in 0–100 range, `grade` is valid `QualityGrade`, `dimensions` contains both `COMPLETENESS` and `COVERAGE` entries, `per_file_scores` has 3 entries | v0.0.7 (Section 4.3) | v0.1.2 (EcosystemSchema) |
| FR-073 | `LinkRelationship` enum and `ParsedLink` extension: Add optional `relationship`, `resolves_to`, and `target_file_type` fields to `ParsedLink` with safe defaults that preserve backward compatibility | MUST | Create `ParsedLink` without new fields — verify identical behavior to pre-pivot; create `ParsedLink` with `relationship=INDEXES` — verify field persists through serialization; existing tests MUST pass unchanged | v0.0.7 (Section 4.2) | v0.1.2 (ParsedModels) |

### 10.2 Ecosystem Discovery (FR-074 to FR-076)

| ID | Requirement | Priority | Acceptance Test | Source | Target Module |
|---|---|---|---|---|---|
| FR-074 | Directory-based ecosystem discovery: Given a project root directory, scan for `llms.txt` (required), `llms-full.txt` (optional), and `.md` files linked from the index; build file manifest | MUST | Point discovery at test directory containing llms.txt + 3 .md files + llms-full.txt; verify manifest contains all 5 files; point at directory with only llms.txt; verify manifest contains 1 file with I010 diagnostic | v0.0.7 (Section 7.1) | v0.3.1 (EcosystemDiscovery) |
| FR-075 | File type classification for ecosystem members: Classify discovered files as TYPE_1_INDEX, TYPE_2_FULL, TYPE_3_CONTENT_PAGE, or TYPE_4_INSTRUCTIONS using filename patterns and content heuristics | SHOULD | Discover 5-file ecosystem; verify llms.txt classified as TYPE_1_INDEX, llms-full.txt as TYPE_2_FULL, linked .md files as TYPE_3_CONTENT_PAGE; verify llms-instructions.txt (if present) classified as TYPE_4_INSTRUCTIONS | v0.0.7 (Section 3.2) | v0.3.1 (EcosystemClassifier) |
| FR-076 | Link extraction and relationship mapping: Extract all links from the index file, classify each as INDEXES (internal content page), REFERENCES (cross-page), AGGREGATES (index → full), or EXTERNAL (outside ecosystem), and build the `FileRelationship` graph | MUST | Index file with 5 links (3 internal .md, 1 external URL, 1 to llms-full.txt); verify 3 INDEXES relationships, 1 EXTERNAL, 1 AGGREGATES; verify graph has correct source/target file IDs | v0.0.7 (Section 3.3) | v0.3.1 (RelationshipMapper) |

### 10.3 Ecosystem Validation (FR-077 to FR-080)

| ID | Requirement | Priority | Acceptance Test | Source | Target Module |
|---|---|---|---|---|---|
| FR-077 | Cross-file link resolution: For each INDEXES and AGGREGATES relationship, verify the target file exists and is accessible; flag unresolved links as W012 (BROKEN_CROSS_FILE_LINK) with both source and target file context in the diagnostic | MUST | Ecosystem with 3 links: 2 resolved, 1 broken; verify 1 W012 diagnostic emitted with `source_file` and `related_file` populated; verify resolved links marked `is_resolved == True` | v0.0.7 (Section 5.2) | v0.2.7 (EcosystemValidator) |
| FR-078 | Ecosystem-level diagnostic codes: Implement all 12 new diagnostic codes (E009–E010, W012–W018, I008–I010) with severity, message, and remediation text following existing `DiagnosticCode` patterns | MUST | Enumerate all 12 new codes; verify each has correct severity prefix (E=ERROR, W=WARNING, I=INFO); verify `.message` and `.remediation` properties return non-empty strings; verify `DiagnosticCode` enum total is 38 | v0.0.7 (Section 5) | v0.2.7 (DiagnosticCodes) |
| FR-079 | Ecosystem anti-pattern detection: Implement detection for 6 ecosystem anti-patterns (AP_ECO_001 through AP_ECO_006) — Index Island, Phantom Links, Shadow Aggregate, Duplicate Ecosystem, Token Black Hole, Orphan Nursery | SHOULD | Run anti-pattern detection on 6 test fixtures (one per pattern); verify each fixture triggers exactly its target anti-pattern; verify clean ecosystem triggers zero ecosystem anti-patterns | v0.0.7 (Section 6.2) | v0.2.7 (EcosystemAntiPatterns) |
| FR-080 | Per-file validation within ecosystem: Run the existing L0–L4 single-file validation pipeline on each discovered file and store results in `EcosystemFile.validation` and `EcosystemFile.quality`; existing pipeline behavior MUST be unchanged | MUST | Validate a 3-file ecosystem; verify each file has its own `ValidationResult` and `QualityScore`; compare per-file results with standalone single-file validation — output MUST be identical | v0.0.7 (Section 7.1) | v0.2.7 (EcosystemPipeline) |

### 10.4 Ecosystem Scoring (FR-081 to FR-082)

| ID | Requirement | Priority | Acceptance Test | Source | Target Module |
|---|---|---|---|---|---|
| FR-081 | Ecosystem Completeness scoring: Calculate a 0–100 score measuring what percentage of internal links (INDEXES, AGGREGATES) resolve to accessible, healthy files; weight by link importance (index links > cross-reference links) | MUST | Ecosystem with 10 links: 8 resolved (6 healthy, 2 with warnings), 2 broken; verify Completeness score reflects resolution rate and target health; verify 100% resolution → score ≥ 90; verify 50% resolution → score ≤ 50 | v0.0.7 (Section 4.3) | v0.2.8 (EcosystemScorer) |
| FR-082 | Ecosystem Coverage scoring: Calculate a 0–100 score measuring how many of the 11 canonical section categories are represented across the ecosystem (not just within the index file); score rewards breadth of documentation coverage | SHOULD | Ecosystem covering 8 of 11 canonical categories → score ~73; ecosystem covering 11 of 11 → score ≥ 95; ecosystem with only 2 categories → score ≤ 25; verify score is independent of per-file quality scores | v0.0.7 (Section 4.3) | v0.2.8 (EcosystemScorer) |

### 10.5 Ecosystem Integration (FR-083 to FR-085)

| ID | Requirement | Priority | Acceptance Test | Source | Target Module |
|---|---|---|---|---|---|
| FR-083 | Backward-compatible single-file mode: When a single llms.txt file is provided (no project directory), the ecosystem layer wraps it transparently — discovery finds 1 file, per-file validation runs identically, I010 is emitted, ecosystem score reflects single-file limitations; ALL existing tests MUST pass without modification | MUST | Run full ecosystem pipeline on single file; diff per-file `ValidationResult` and `QualityScore` against standalone pipeline output — MUST be byte-identical; verify I010 (ECOSYSTEM_SINGLE_FILE) emitted; verify no E009 (no index) since the single file IS the index | v0.0.7 (Section 7.2) | v0.2.7 (EcosystemPipeline) |
| FR-084 | Ecosystem validation pipeline orchestration: Implement the 5-stage pipeline (Discovery → Per-File Validation → Relationship Mapping → Ecosystem Validation → Ecosystem Scoring) with each stage producing typed intermediate results; pipeline MUST be stoppable after any stage | MUST | Run pipeline on 5-file ecosystem; verify all 5 stages execute in order; stop after stage 3 (Relationship Mapping); verify stages 4–5 did not execute; verify partial results are available for stages 1–3 | v0.0.7 (Section 7.1) | v0.2.7 (EcosystemPipeline) |
| FR-085 | Ecosystem view in Streamlit demo: Add an "Ecosystem" tab or view to the Streamlit UI showing: file manifest with per-file grades, relationship graph (simple list or diagram), ecosystem health score with dimensional breakdown, and list of ecosystem-level diagnostics | SHOULD | Load ecosystem in demo; verify all discovered files listed with grades; verify relationships displayed; verify ecosystem score shown with Completeness and Coverage breakdowns; verify ecosystem diagnostics (W012, I010, etc.) displayed | v0.0.7 (Section 7.1) | v0.6.0 (EcosystemView) |

---

## [v0.0.7] 11. Requirement Coverage Matrix (Revised)

### By MoSCoW Category

| Category | Count (Original) | Count (v0.0.7 Revised) | FR IDs |
|---|---|---|---|
| **MUST** | 32 | 45 | FR-001–004, FR-007–008, FR-011, FR-013, FR-016, FR-020, FR-024–027, FR-032–035, FR-039–042, FR-047–048, FR-051–053, FR-055–057, FR-059–060, **[v0.0.7]** FR-069–074, FR-076–078, FR-080–081, FR-083–084 |
| **SHOULD** | 29 | 33 | FR-005–006, FR-009–010, FR-012, FR-014–015, FR-017–019, FR-021, FR-023, FR-028–030, FR-036–037, FR-043–046, FR-049, FR-054, FR-058, FR-061, FR-063–064, FR-066–067, **[v0.0.7]** FR-075, FR-079, FR-082, FR-085 |
| **COULD** | 7 | 7 | FR-022, FR-031, FR-038, FR-050, FR-062, FR-065, FR-068 |
| **TOTAL** | 68 | **85** | — |

### By Module

| Module | FR Range | Count | Key Deliverable |
|---|---|---|---|
| Schema & Validation | FR-001–012 | 12 | Validated Pydantic models + validation pipeline |
| Content Structure | FR-013–025 | 13 | 3-layer context (Master Index, Concepts, Examples) |
| Parser & Loader | FR-026–031 | 6 | Robust llms.txt loader with error recovery |
| Context Builder | FR-032–038 | 7 | Token-aware context assembly |
| Agent Integration | FR-039–050 | 12 | Baseline + enhanced agent with system prompts |
| A/B Testing | FR-051–058 | 8 | Test runner + metrics + statistical significance |
| Demo Layer | FR-059–065 | 7 | Streamlit app with side-by-side comparison |
| Cross-Module | FR-066–068 | 3 | Logging, DI, telemetry |

---

## 11. Traceability Examples

### From Research to Requirement

```
v0.0.1a (Grammar)
    ├─→ FR-001 (Pydantic models for structure)
    ├─→ FR-003 (Syntax validation)
    ├─→ FR-004 (Structure validation)
    └─→ FR-026 (Parser/Loader)

v0.0.1c (Processing Methods)
    ├─→ FR-016 (Concept extraction)
    ├─→ FR-032 (Processing methods)
    ├─→ FR-033 (Token budgeting)
    ├─→ FR-034 (Hybrid pipeline)
    └─→ FR-047 (Few-shot in context)

v0.0.4 (Best Practices)
    ├─→ FR-006 (Quality validation)
    ├─→ FR-014 (Freshness signals)
    ├─→ FR-019 (Authority metadata)
    ├─→ FR-041 (System prompts)
    └─→ FR-044 (Multiple LLM providers)
```

### From Requirement to Implementation

```
FR-001 (Pydantic models)
    ├─→ v0.1.1 (Schema module — build models)
    ├─→ v0.2.1 (Validation module — use models)
    ├─→ v0.3.1 (Loader — instantiate models)
    └─→ v0.6.0 (Demo — serialize/deserialize models)

FR-034 (Hybrid pipeline)
    ├─→ v0.3.2 (Builder — Layer 0)
    ├─→ v0.4.1 (Mapper — Layer 1)
    ├─→ v0.5.1 (Extractor — Layer 2)
    └─→ v0.4.4 (Orchestrator — combine layers)
```

---

## Deliverables

- [x] 85 formally identified functional requirements (FR-001 through FR-085) **[v0.0.7: was 68]**
- [x] Requirements organized by 8 software modules **[v0.0.7: was 7, added Ecosystem Discovery & Validation]**
- [x] Each requirement includes: ID, description, priority, acceptance test, source, target module
- [x] Traceability matrix connecting research to requirements and requirements to implementation
- [x] MoSCoW prioritization across all requirements
- [x] Coverage matrix showing distribution by priority and module
- [x] **[v0.0.7]** 17 ecosystem-level functional requirements (FR-069 through FR-085) traced to v0.0.6 and v0.0.7 research
- [x] **[v0.0.7]** Backward compatibility requirement (FR-083) ensuring single-file mode is byte-identical

---

## Acceptance Criteria

- [x] Every requirement has a unique ID (FR-###)
- [x] Every requirement includes acceptance test (specific, measurable, testable)
- [x] Every requirement is prioritized (MUST/SHOULD/COULD)
- [x] Every requirement is traced to at least one research source (v0.0.x)
- [x] Every requirement is traced to target implementation module (v0.x.x)
- [x] Requirements span all 7 planned modules
- [x] Coverage includes functional behaviors across all layers (validation, parsing, context building, agents, testing, demo)
- [x] Cross-module requirements documented
- [x] Document is self-contained and implementable

---

## Next Step

Once this sub-part is approved, proceed to:

**v0.0.5b — Non-Functional Requirements & Constraints**

This sub-part defines performance targets, usability standards, maintainability requirements, and technical constraints that will guide implementation decisions in v0.1–v0.6.
