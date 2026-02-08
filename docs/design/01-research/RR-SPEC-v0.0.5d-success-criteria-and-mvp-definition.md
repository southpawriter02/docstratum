# v0.0.5d — Success Criteria & MVP Definition

> **Sub-Part:** Define measurable success criteria, precise MVP feature checklist, acceptance tests, quantitative metrics, demo scenario script, and "Definition of Done" checklist that must be satisfied before v0.6.0 release.

---

> **REVISION NOTICE — v0.0.7 Ecosystem Pivot (2026-02-07)**
>
> This document was revised following the strategic pivot defined in `RR-SPEC-v0.0.7-ecosystem-pivot-specification.md`. Changes include: Module 8 (Ecosystem Discovery & Validation) added to MVP Feature Checklist with 13 MUST features (FR-069–074, FR-076–078, FR-080–081, FR-083–084); Test Scenario 5 (Ecosystem Validation) added; ecosystem performance metrics added to Part 3; Definition of Done updated with ecosystem gates; stretch goals expanded with ecosystem SHOULD features. Changes are marked with `[v0.0.7]` tags. Original content (Modules 1–7, Test Scenarios 1–4) is unchanged.
>
> **Impact summary:** MVP MUST features 32 → 45. Test scenarios 4 → 5. Modules 7 → 8. DoD checklist expanded with ecosystem dimension. Stretch goals expanded with 4 ecosystem SHOULD features.
>
> **Note:** v0.0.5a's revision header originally stated "MUST count 32 → 44" — this was a counting error (44 + 33 + 7 = 84 ≠ 85 total FRs). Corrected to 45 MUST during consistency review (2026-02-07). The correct count is 45 MUST, verified by enumerating the individual section priorities across all 8 modules.

---

## Sub-Part Overview

This sub-part is the capstone of the v0.0.5 requirements definition series — converting the 85 functional requirements from v0.0.5a **[v0.0.7: was 68]**, the 21 non-functional requirements and 6 constraints from v0.0.5b, and the 40 out-of-scope items and scope defense system from v0.0.5c **[v0.0.7: was 32]** into a precise, testable definition of "done" for the DocStratum v0.6.0 MVP. Drawing on performance targets from v0.0.1c (token budgeting, hybrid pipeline architecture), quality standards from v0.0.4b (100-point composite scoring, content quality predictors), agent testing patterns from v0.0.4d (DECISION-015: AI coding assistants via MCP), scope boundaries from v0.0.5c (in-scope statement, deferred features registry), **[v0.0.7]** platinum standard validation criteria from v0.0.6, and ecosystem pivot architecture from v0.0.7, this document establishes 45 MVP features organized across 8 modules **[v0.0.7: was 32 features across 7 modules]** with acceptance tests, 5 test scenarios **[v0.0.7: was 4]** with executable pseudocode, quantitative success metrics with statistical significance requirements, a timed demo scenario script, and a comprehensive Definition of Done checklist.

**Distribution:** 45 MUST features define the minimum viable product (from v0.0.5a's MoSCoW analysis) **[v0.0.7: was 32 MUST; 13 ecosystem MUST features added from FR-069–084]**. 5 test scenarios cover the primary differentiators: disambiguation (concept map value), freshness (temporal awareness), few-shot adherence (example-driven output quality), integration (end-to-end pipeline reliability), and **[v0.0.7]** ecosystem validation (multi-file discovery, cross-file link resolution, and ecosystem health scoring). Quantitative targets are calibrated against NFR thresholds from v0.0.5b: parse time < 500ms, context build < 2s, agent latency ≤ 12s, memory < 200MB, test coverage ≥ 80%, **[v0.0.7]** ecosystem discovery < 3s, ecosystem scoring < 1s. The Definition of Done checklist spans 5 dimensions: Code & Implementation, Documentation, Demo & Testing, Success Metrics, and Portfolio Presentation — plus a Scope & Constraints gate referencing v0.0.5c boundaries — **[v0.0.7]** with ecosystem-specific items added to each dimension.

**Relationship to v0.0.5a, v0.0.5b, v0.0.5c, v0.0.6, and v0.0.7:** Every MVP feature in Part 1 traces directly to a MUST-priority functional requirement from v0.0.5a. Every quantitative target in Part 3 traces to an NFR from v0.0.5b. Every stretch goal in Part 8 is drawn from the deferred features registry in v0.0.5c or from SHOULD/COULD requirements in v0.0.5a. The Definition of Done checklist (Part 6) references v0.0.5c's scope boundaries as an explicit release gate — no out-of-scope features may be added to the MVP without passing the Scope Fence decision tree. **[v0.0.7]** Ecosystem MVP features (Module 8) trace to v0.0.6 (Platinum Standard Definition) and v0.0.7 (Ecosystem Pivot Specification). Ecosystem stretch goals trace to SHOULD-priority FRs in v0.0.5a Section 10.

---

## Objective

This sub-part converts the research, functional requirements, non-functional requirements, and scope definitions into a precise, testable success definition. By the end, we have an unambiguous answer to: "Is v0.6.0 done?" and "Does DocStratum succeed?"

### Success Looks Like

- Exact MVP feature checklist (every feature that MUST work)
- Acceptance tests for each MVP feature (specific, executable test scenarios)
- Quantitative success metrics (accuracy %, latency ms, test pass rates)
- Qualitative success criteria (code quality, documentation, portfolio value)
- Stretch goals with effort estimates (do these if time permits)
- Demo scenario script (the exact 2-minute flow for portfolio presentation)
- "Definition of Done" checklist (conditions for release)

---

## Scope Boundaries

### In Scope

- Defining the precise MVP feature list
- Writing acceptance tests for each feature
- Setting quantitative success targets (metrics)
- Establishing qualitative criteria (code quality, docs)
- Creating demo scenario script
- Building "Definition of Done" checklist
- Identifying stretch goals and their effort estimates

### Out of Scope

- Implementation details (that's v0.1–v0.6)
- Non-functional requirements (that's v0.0.5b)
- Out-of-scope items (that's v0.0.5c)
- Feature design or architecture (that's v0.1–v0.6)

---

## Dependencies

```
v0.0.5a — Functional Requirements (FR-001 through FR-085) [v0.0.7: was FR-068]
    ├─ Establishes what features exist
    ├─ Prioritizes each as MUST/SHOULD/COULD
    └─ [v0.0.7] Includes 17 ecosystem FRs (FR-069–085)

v0.0.5b — Non-Functional Requirements (NFR-001 through NFR-021)
    ├─ Sets performance targets (parse time, latency, memory)
    ├─ Defines quality standards (test coverage, docs)
    └─ Establishes constraints (Python version, providers)

v0.0.5c — Scope Definition (In-scope + OOS Registry)
    ├─ Confirms MVP scope is locked
    ├─ Ensures focus on core features
    └─ [v0.0.7] Expanded to 40 OOS items across 8 categories

v0.0.6 — Platinum Standard Definition [v0.0.7: NEW]
    ├─ 30-criterion, 5-level quality framework (L0–L4)
    └─ Establishes what DocStratum validates against

v0.0.7 — Ecosystem Pivot Specification [v0.0.7: NEW]
    ├─ 3-layer ecosystem model (Navigation, Content, Aggregate)
    ├─ 6 new schema entities + 12 diagnostic codes
    └─ 4-phase migration plan

                            v
v0.0.5d — Success Criteria (THIS TASK)
                            │
                            v
        Ready for v0.1–v0.6 Implementation
```

---

## Part 1: MVP Feature Checklist

### The Exact List of Features That MUST Work

The MVP is v0.6.0. Every feature marked **MUST** in v0.0.5a must work. Every feature marked **SHOULD** is nice-to-have but not required for success.

#### Module 1: Schema & Validation (7 MUST features)

| Feature | FR ID | Acceptance Criteria | Test Method |
|---|---|---|---|
| Pydantic models for base llms.txt (Document, Section, Entry) | FR-001 | Models instantiate from sample llms.txt; serialize to JSON; deserialize correctly | Unit test: instantiate 3+ models; verify fields accessible |
| Extended DocStratum schema fields | FR-002 | FileEntry accepts optional concept_id, layer_num, few_shot_type; backward compatible | Unit test: parse extended + standard llms.txt; verify no data loss |
| Validation Level 0 (SYNTAX) | FR-003 | Parser rejects invalid line format; generates E-series error codes | Test 5+ malformed entries; verify errors include line numbers and codes |
| Validation Level 1 (STRUCTURE) | FR-004 | Validator checks H1 title, H2 sections, entry counts; generates W-series warnings | Test 5+ structural violations; verify warnings are non-blocking |
| Validation Level 4 (DOCSTRATUM) | FR-007 | Validator checks concept_id refs, layer_num range, few_shot_type enum | Test extended llms.txt with invalid refs; verify validation fails correctly |
| Error reporting with line numbers | FR-008 | Every error includes: line#, code (E/W/I), severity, human-readable message | Generate 10+ error scenarios; verify all 4 fields present |
| Schema round-trip (parse → validate → serialize → re-parse) | FR-011 | Load llms.txt; serialize to JSON; deserialize; verify document identity with no data loss | Unit test: load 5+ files; JSON round-trip; compare input vs. output fields |

#### Module 2: Content Structure (5 MUST features)

| Feature | FR ID | Acceptance Criteria | Test Method |
|---|---|---|---|
| Layer 0 (Master Index) implementation | FR-013 | Parse llms.txt; build index with title, URL, section, freshness metadata | Load 5 real llms.txt files; verify index has ≥ 80% coverage |
| Layer 1 (Concept Map) implementation | FR-016 | Extract concepts from descriptions; assign unique IDs; verify no duplicates | Parse 5 llms.txt files; extract 50+ total concepts; verify IDs unique |
| Layer 2 (Few-Shot Bank) implementation | FR-020 | Extract or manually create 5+ Q&A pairs per llms.txt; store with references | Load 3 llms.txt files; verify each has ≥ 5 Q&A examples available |
| Three-layer cross-reference resolution | FR-024 | Navigate from FileEntry → concept → few-shot example; bidirectional reference chain works | Integration test: trace from entry to concept to example and back; verify all links resolve |
| Export all three layers in JSON/YAML format | FR-025 | Serialize all layers to JSON; deserialize; verify no data loss; all references still valid | Serialize 5+ documents; re-load; compare reference integrity before and after |

#### Module 3: Parser & Loader (2 MUST features)

| Feature | FR ID | Acceptance Criteria | Test Method |
|---|---|---|---|
| Load and parse standard llms.txt from URL or file | FR-026 | Parser handles 10+ real llms.txt files without errors | Load 10 real files; verify all parse successfully |
| Handle all line-ending variations (LF, CRLF, CR) | FR-027 | Parser normalizes line endings; output consistent regardless of input | Test same content with LF, CRLF, CR; verify identical parse results |

#### Module 4: Context Builder (4 MUST features)

| Feature | FR ID | Acceptance Criteria | Test Method |
|---|---|---|---|
| Processing methods (discovery, synthesis, ranking, filtering) | FR-032 | Implement all 4 methods; apply to 5+ llms.txt; results are distinct | Test each method independently; verify different outputs |
| Token budgeting | FR-033 | Estimate tokens for each layer; build context within 4K token budget | Measure token counts; verify context assembled stays ≤ 4K total |
| Hybrid pipeline combining all 3 layers | FR-034 | Assemble Master Index + Concepts + Examples into single agent context | Build context from 5 llms.txt files; verify all layers represented |
| Query-aware context selection | FR-035 | Given a query, select most relevant entries, concepts, and examples from all layers | Feed 10+ test queries; verify top-3 results are relevant; compare with keyword match baseline |

#### Module 5: Agent Integration (6 MUST features)

| Feature | FR ID | Acceptance Criteria | Test Method |
|---|---|---|---|
| Baseline agent (raw llms.txt) | FR-039 | LangChain agent answers 5+ test queries using raw llms.txt | Run agent on 5 queries; verify answers are sensible |
| Enhanced agent (DocStratum context) | FR-040 | LangChain agent answers same 5+ queries using optimized context + system prompt | Run agent on 5 queries; verify answers are sensible |
| System prompt injection (2 distinct prompts) | FR-041 | Generic prompt (no concept refs); DocStratum prompt (concept-aware); both accepted by agent | Verify both prompts parse without syntax errors; agent executes both |
| Context window management | FR-042 | Cap context + prompt + query ≤ model max tokens; prefer quality over quantity | Build oversized context; verify it's filtered to fit; check no truncation mid-sentence |
| Few-shot in-context learning | FR-047 | Inject 3–5 Q&A examples before main agent query; agent references them in response | Select 3 most relevant examples for query; prepend to agent prompt; verify agent references them |
| Agent testing harness (baseline vs. enhanced comparison) | FR-048 | Compare baseline vs. enhanced agent on same query set; measure accuracy, latency, token usage | Run both agents on 20+ test queries; display comparison table with all metrics |

#### Module 6: A/B Testing Harness (6 MUST features)

| Feature | FR ID | Acceptance Criteria | Test Method |
|---|---|---|---|
| Query runner (baseline vs. enhanced on same queries) | FR-051 | Load 20+ test queries; run both agents; collect responses | Run all 20 queries; verify both agents complete; results exported |
| Response comparison (accuracy, completeness, relevance) | FR-052 | Implement 3+ comparison metrics; score response pairs; show diffs | Score 20+ response pairs; display side-by-side with scores |
| Metrics collection (accuracy, latency, tokens, success rate) | FR-053 | Capture all metrics; compute mean/std/percentiles; export to table | Collect metrics for all 20 queries; export to CSV + JSON |
| Baseline definition (quantitative benchmark) | FR-055 | Run baseline agent on 50+ queries; compute mean metrics; store as benchmark reference | Run baseline agent; compute mean accuracy, latency, token usage; persist as versioned benchmark |
| Test query design (4-category coverage) | FR-056 | Include 5+ queries per category (disambiguation, freshness, few-shot, integration); 20+ total | Create query bank; verify each query tests intended capability; verify category distribution balanced |
| Test result export (JSON/CSV for analysis) | FR-057 | Save results (queries, responses, scores, metrics) to JSON and CSV; verify parseable | Run tests; export both formats; re-import; verify all data fields present and correct |

#### Module 7: Demo Layer (2 MUST features)

| Feature | FR ID | Acceptance Criteria | Test Method |
|---|---|---|---|
| Streamlit UI (load llms.txt, display structure) | FR-059 | Upload llms.txt to app; verify parsed structure displayed; validation results shown | Upload 5 files; verify parsing succeeds; validation visible |
| Side-by-side agent view (query input, both agents' responses) | FR-060 | Type query; click "Run"; baseline response in left column, enhanced in right | Type 5 queries; verify both responses appear in correct columns |

> **Note on FR-061 (Metrics display):** FR-061 is classified as SHOULD priority in v0.0.5a, not MUST. However, the Demo Scenario Script (Part 5) relies on metrics being visible for the portfolio presentation. FR-061 is listed as a high-priority stretch goal in Part 8 — if implemented, it significantly enhances the demo impact. The demo can function without it (side-by-side text comparison is sufficient), but metrics add quantitative evidence to the qualitative comparison.

#### [v0.0.7] Module 8: Ecosystem Discovery & Validation (13 MUST features)

| Feature | FR ID | Acceptance Criteria | Test Method |
|---|---|---|---|
| `DocumentEcosystem` top-level model | FR-069 | Model instantiates with 1 index + 2 content pages; `file_count == 3`; JSON round-trip serialization | Unit test: instantiate with 3 files; verify fields; serialize and deserialize; compare |
| `EcosystemFile` model wrapping parsed files | FR-070 | Wraps `ParsedLlmsTxt` with ecosystem metadata; unique UUID per file; accepts existing validation/quality instances | Unit test: create from parsed file; verify file_id unique, file_type correct, validation attached |
| `FileRelationship` directed relationship model | FR-071 | Represents INDEXES/REFERENCES/AGGREGATES/EXTERNAL links; `is_resolved` tracks whether target exists | Unit test: create relationships; verify type enum; test resolved=True vs resolved=False |
| `EcosystemScore` aggregate health model | FR-072 | Score in 0–100 range; `QualityGrade` enum; Completeness + Coverage dimensions; per-file score map | Unit test: score 3-file ecosystem; verify range, grade, 2 dimensions, 3 per-file entries |
| `LinkRelationship` enum + `ParsedLink` extension | FR-073 | New optional fields on `ParsedLink`; backward compatible (existing tests pass unchanged) | Unit test: create ParsedLink without new fields (identical behavior); create with new fields (persist through serialization) |
| Directory-based ecosystem discovery | FR-074 | Scan project root; find llms.txt (required) + llms-full.txt + linked .md files; build manifest | Integration test: test directory with 5 files; verify manifest complete; test with single file → I010 emitted |
| Link extraction and relationship mapping | FR-076 | Extract links from index; classify as INDEXES/REFERENCES/AGGREGATES/EXTERNAL; build relationship graph | Unit test: index with 5 links (3 internal, 1 external, 1 to llms-full.txt); verify classification correct |
| Cross-file link resolution | FR-077 | Verify target files exist for INDEXES/AGGREGATES links; flag broken links as W012 | Integration test: 3 links (2 resolved, 1 broken); verify 1 W012 with source/target context |
| 12 new ecosystem diagnostic codes | FR-078 | E009–E010, W012–W018, I008–I010 implemented; correct severity prefixes; non-empty messages | Unit test: enumerate all 12; verify severity, message, remediation; verify enum total is 38 |
| Per-file validation within ecosystem | FR-080 | Run existing L0–L4 pipeline on each discovered file; store results in `EcosystemFile`; output identical to standalone | Integration test: validate 3-file ecosystem; compare per-file results with standalone — MUST be identical |
| Ecosystem Completeness scoring | FR-081 | 0–100 score measuring link resolution rate weighted by importance; 100% resolution → ≥ 90; 50% → ≤ 50 | Unit test: 10 links (8 resolved, 2 broken); verify score reflects resolution rate and target health |
| Backward-compatible single-file mode | FR-083 | Single-file input wraps transparently; per-file output byte-identical to pre-pivot; I010 emitted; all existing tests pass | Regression test: diff ecosystem-wrapped single-file output against standalone output — MUST be byte-identical |
| 5-stage ecosystem pipeline orchestration | FR-084 | Discovery → Per-File Validation → Relationship Mapping → Ecosystem Validation → Ecosystem Scoring; stoppable after any stage | Integration test: run 5-file ecosystem; verify all 5 stages; stop after stage 3 → stages 4–5 skipped; partial results available |

> **Note on ecosystem SHOULD features:** FR-075 (file type classification heuristics), FR-079 (anti-pattern detection), FR-082 (coverage scoring), and FR-085 (Streamlit ecosystem view) are classified as SHOULD in v0.0.5a. They are listed as stretch goals in Part 8. The ecosystem MVP is functional without them — type classification uses filename patterns only (no content heuristics), anti-patterns are deferred, coverage scoring is deferred, and the Streamlit view can be added post-MVP.

### MVP Feature Summary

| Category | Count (Original) | Count (v0.0.7 Revised) | FR IDs |
|---|---|---|---|
| **MUST (MVP)** | 32 | **45** | FR-001, FR-002, FR-003, FR-004, FR-007, FR-008, FR-011, FR-013, FR-016, FR-020, FR-024, FR-025, FR-026, FR-027, FR-032, FR-033, FR-034, FR-035, FR-039, FR-040, FR-041, FR-042, FR-047, FR-048, FR-051, FR-052, FR-053, FR-055, FR-056, FR-057, FR-059, FR-060, **[v0.0.7]** FR-069, FR-070, FR-071, FR-072, FR-073, FR-074, FR-076, FR-077, FR-078, FR-080, FR-081, FR-083, FR-084 |
| **SHOULD (important, not MVP-blocking)** | 29 | **33** | FR-005, FR-006, FR-009, FR-010, FR-012, FR-014, FR-015, FR-017, FR-018, FR-019, FR-021, FR-023, FR-028, FR-029, FR-030, FR-036, FR-037, FR-043, FR-044, FR-045, FR-046, FR-049, FR-054, FR-058, FR-061, FR-063, FR-064, FR-066, FR-067, **[v0.0.7]** FR-075, FR-079, FR-082, FR-085 |
| **COULD (stretch goals)** | 7 | **7** | FR-022, FR-031, FR-038, FR-050, FR-062, FR-065, FR-068 |

### MVP Module Distribution

| Module | MUST Count | FR IDs | Key Deliverable |
|---|---|---|---|
| Schema & Validation | 7 | FR-001–004, FR-007–008, FR-011 | Validated Pydantic models + round-trip serialization |
| Content Structure | 5 | FR-013, FR-016, FR-020, FR-024, FR-025 | 3-layer context with cross-references + JSON/YAML export |
| Parser & Loader | 2 | FR-026, FR-027 | Robust llms.txt loader with line-ending normalization |
| Context Builder | 4 | FR-032–035 | Token-aware, query-relevant context assembly |
| Agent Integration | 6 | FR-039–042, FR-047, FR-048 | Baseline + enhanced agents with few-shot injection + testing harness |
| A/B Testing | 6 | FR-051–053, FR-055–057 | Full test infrastructure with baselines, categories, and export |
| Demo Layer | 2 | FR-059, FR-060 | Streamlit app with side-by-side comparison |
| **[v0.0.7]** Ecosystem Discovery & Validation | **13** | FR-069–074, FR-076–078, FR-080–081, FR-083–084 | Ecosystem schema models + discovery + cross-file validation + pipeline orchestration |
| **TOTAL** | **45** | — | **[v0.0.7: was 32]** |

---

## Part 2: Test Scenarios & Acceptance Tests

### Test Scenario 1: Disambiguation Test

**Goal:** Verify the agent can resolve ambiguous terminology using the concept map.

#### Scenario Description

Many documentation systems use terms that have multiple meanings. Example: "**context**" means different things in:

- LLM context (token window)
- Agent context (background info)
- Deployment context (environment)
- Business context (situation)

The DocStratum concept map should disambiguate by providing context-specific definitions.

#### Test Steps

```
1. Load an llms.txt file with multiple uses of "context"
   Input: sample_llms.txt (3 sections: "Agent Design", "Deployment", "Architecture")

2. Run baseline agent with query: "What is context?"
   Expected: Generic answer (possibly ambiguous)

3. Run enhanced agent with same query
   Expected: Disambiguation; agent references concept map and says:
   "In this documentation, 'context' has these meanings:
   - Agent context: Information provided to the agent (Section: Agent Design)
   - Deployment context: Environment where code runs (Section: Deployment)
   - Architectural context: System relationships (Section: Architecture)"

4. Verify baseline agent answer is less specific
   Metric: Baseline mentions 1–2 meanings; Enhanced mentions 3+ with references

5. Human evaluator scores accuracy: 0–10
   Pass: Enhanced > Baseline by ≥ 2 points
```

#### Acceptance Test (Specific & Measurable)

```python
# test_disambiguation.py

def test_disambiguation_improvement():
    """Enhanced agent should disambiguate better than baseline."""
    query = "What is context?"

    baseline_response = baseline_agent.query(query)
    enhanced_response = enhanced_agent.query(query)

    baseline_meanings = count_distinct_meanings(baseline_response)
    enhanced_meanings = count_distinct_meanings(enhanced_response)

    baseline_score = evaluate_response(baseline_response, ground_truth)
    enhanced_score = evaluate_response(enhanced_response, ground_truth)

    assert enhanced_meanings >= baseline_meanings, \
        f"Enhanced should mention more meanings: {baseline_meanings} vs {enhanced_meanings}"

    assert enhanced_score > baseline_score + 1, \
        f"Enhanced score should exceed baseline by ≥ 2 pts: {baseline_score} vs {enhanced_score}"

    # Verify concept references are present in enhanced response
    assert "concept map" in enhanced_response.lower() or \
           any(ref in enhanced_response for ref in ["Section:", "definition", "relates to"]), \
        "Enhanced response should reference concept relationships"
```

#### Success Criteria

- [x] Enhanced agent mentions ≥ 3 distinct meanings of ambiguous terms
- [x] Enhanced agent provides context (which section/use case for each meaning)
- [x] Human evaluator scores enhanced response ≥ 2 points higher than baseline
- [x] Concept references visible in enhanced response

---

### Test Scenario 2: Freshness Test

**Goal:** Verify the agent correctly identifies which information is current vs. deprecated.

#### Scenario Description

Documentation often contains:

- **Current:** "Use the new v2 API (current as of Feb 2025)"
- **Deprecated:** "The v1 API is no longer supported (deprecated as of Jan 2024)"
- **Evergreen:** "Core concepts that never change"

Baseline agent might confuse deprecated advice with current best practices. Enhanced agent should use freshness signals from the concept map.

#### Test Steps

```
1. Load an llms.txt file with entries marked with freshness signals
   Input: sample_llms.txt with explicit versioning/dates

2. Run baseline agent with query: "How do I authenticate?"
   Expected: May mention deprecated v1 method if it appears early in file

3. Run enhanced agent with same query
   Expected: Prioritizes current v2 authentication method; notes v1 is deprecated

4. Verify enhanced agent explicitly marks information age
   Metric: Enhanced mentions "current as of [date]" or "deprecated as of [date]"

5. Human evaluator scores practical usefulness: 0–10
   Pass: Enhanced answer would prevent developer mistakes
```

#### Acceptance Test

```python
# test_freshness.py

def test_freshness_signals_applied():
    """Enhanced agent should prioritize current over deprecated."""
    query = "How do I authenticate?"

    baseline_response = baseline_agent.query(query)
    enhanced_response = enhanced_agent.query(query)

    # Extract suggested approach from each response
    baseline_method = extract_primary_method(baseline_response)
    enhanced_method = extract_primary_method(enhanced_response)

    # Verify enhanced response marks freshness
    freshness_markers = ["current", "deprecated", "evergreen", "as of", "v2", "v1"]
    enhanced_has_freshness = any(m in enhanced_response.lower() for m in freshness_markers)

    assert enhanced_has_freshness, \
        "Enhanced response should include freshness signals"

    # Verify enhanced avoids recommending deprecated methods
    assert "deprecated" not in enhanced_method.lower(), \
        f"Enhanced should not recommend deprecated method: {enhanced_method}"

    # If both recommend same method, enhanced should add freshness context
    if baseline_method == enhanced_method:
        assert len(enhanced_response) > len(baseline_response) * 1.2, \
            "Enhanced should add freshness context even if recommending same method"
```

#### Success Criteria

- [x] Enhanced agent explicitly marks information as current/deprecated/evergreen
- [x] Enhanced agent prioritizes current methods over deprecated ones
- [x] Enhanced response includes date or version information
- [x] Baseline and enhanced agree on core advice (no contradictions)

---

### Test Scenario 3: Few-Shot Adherence Test

**Goal:** Verify the agent follows the patterns in few-shot examples.

#### Scenario Description

DocStratum provides few-shot examples (Q&A pairs) that demonstrate the desired response style:

- Example 1: "How do I [task]?" → Concise answer (2–3 sentences)
- Example 2: "What is [concept]?" → Definition + example
- Example 3: "When should I use [feature]?" → Comparison with alternatives

Baseline agent may not follow these patterns. Enhanced agent should.

#### Test Steps

```
1. Load an llms.txt file with documented few-shot examples
   Input: sample_llms.txt with 5+ Q&A pairs

2. Run baseline agent with queries matching the few-shot patterns
   Query 1: "How do I [task]?"
   Query 2: "What is [concept]?"
   Query 3: "When should I use [feature]?"

3. Run enhanced agent with same queries
   Expected: Responses follow the documented patterns

4. Evaluate response style consistency
   Metric: Enhanced responses match few-shot pattern in 80%+ of queries

5. Human evaluator assesses consistency: 0–10
   Pass: Enhanced responses feel cohesive and well-structured
```

#### Acceptance Test

```python
# test_few_shot_adherence.py

def test_few_shot_examples_followed():
    """Enhanced agent should follow few-shot example patterns."""

    # Load few-shot examples
    few_shot_examples = load_few_shot_bank("sample_llms.txt")

    # Test queries matching example patterns
    test_queries = [
        ("How do I use the API?", "how_pattern"),
        ("What is authentication?", "what_pattern"),
        ("When should I use caching?", "when_pattern"),
    ]

    for query, pattern_type in test_queries:
        baseline_resp = baseline_agent.query(query)
        enhanced_resp = enhanced_agent.query(query)

        # Analyze response structure
        baseline_style = analyze_response_style(baseline_resp)
        enhanced_style = analyze_response_style(enhanced_resp)

        # Compute style similarity to few-shot examples
        baseline_similarity = compute_style_similarity(baseline_style, few_shot_examples)
        enhanced_similarity = compute_style_similarity(enhanced_style, few_shot_examples)

        # Enhanced should be more similar to few-shot patterns
        assert enhanced_similarity > baseline_similarity * 1.15, \
            f"{pattern_type}: Enhanced not following few-shot patterns well enough"

    # Verify few-shot examples are present in context
    context_used = enhanced_agent.get_context_used()
    assert context_used["few_shot_count"] >= 3, \
        "Enhanced agent should use at least 3 few-shot examples"
```

#### Success Criteria

- [x] Enhanced agent responses follow documented patterns in 80%+ of queries
- [x] Enhanced agent includes at least 3 few-shot examples in context
- [x] Response structure (intro, details, conclusion) is consistent
- [x] Human evaluator notes enhanced responses feel "more polished"

---

### Test Scenario 4: Integration Test (Happy Path)

**Goal:** Verify the complete end-to-end flow works for a realistic use case.

#### Test Steps

```
1. Start with a real llms.txt file (Stripe, Nuxt, or Vercel)
   Input: Fetch actual llms.txt from API

2. Run full pipeline:
   a. Load and parse file
   b. Validate (L0–L4)
   c. Build 3 layers (Master Index, Concepts, Examples)
   d. Create both agent contexts
   e. Run both agents on 5 test queries
   f. Collect metrics and compare

3. Verify all steps complete without errors
   Expected: No exceptions; all metrics collected

4. Check metrics make sense
   Baseline accuracy: 40–70% (typical LLM on unoptimized context)
   Enhanced accuracy: 60–85% (should improve by 10–25 pts)
   Latency increase: ≤ 4 seconds (acceptable overhead)

5. Verify demo runs without errors
   Expected: Streamlit app loads; can upload file; agents respond
```

#### Acceptance Test

```python
# test_integration_happy_path.py

def test_end_to_end_pipeline():
    """Full pipeline should work end-to-end without errors."""

    # Load real llms.txt
    llms_txt_url = "https://docs.stripe.com/llms.txt"
    document = loader.load_from_url(llms_txt_url)

    # Validate
    validator = ValidationPipeline()
    errors = validator.validate(document, levels=[0, 1, 2, 3, 4])
    assert not any(e.severity == Severity.ERROR for e in errors), \
        f"Validation errors: {errors}"

    # Build layers
    context = context_builder.build_context(document)
    assert context.layers[0].entries > 0, "Layer 0 should have entries"
    assert context.layers[1].concepts > 0, "Layer 1 should have concepts"
    assert context.layers[2].examples > 0, "Layer 2 should have examples"

    # Run agents
    test_queries = [
        "How do I authenticate with the Stripe API?",
        "What is the difference between test and live mode?",
        "When should I use webhooks?",
        "How do I handle errors in the API?",
        "What are the rate limits?",
    ]

    baseline_results = []
    enhanced_results = []

    for query in test_queries:
        baseline_resp = baseline_agent.query(query)
        enhanced_resp = enhanced_agent.query(query)

        baseline_results.append({
            "query": query,
            "response": baseline_resp,
            "tokens": count_tokens(baseline_resp),
            "latency": baseline_resp.latency,
        })

        enhanced_results.append({
            "query": query,
            "response": enhanced_resp,
            "tokens": count_tokens(enhanced_resp),
            "latency": enhanced_resp.latency,
        })

    # Verify all queries completed
    assert len(baseline_results) == len(test_queries), "Baseline should complete all queries"
    assert len(enhanced_results) == len(test_queries), "Enhanced should complete all queries"

    # Compute aggregate metrics
    baseline_avg_latency = mean([r["latency"] for r in baseline_results])
    enhanced_avg_latency = mean([r["latency"] for r in enhanced_results])

    # Verify latency increase is acceptable (< 4s)
    latency_increase = enhanced_avg_latency - baseline_avg_latency
    assert latency_increase <= 4.0, \
        f"Latency increase too high: {latency_increase}s (baseline: {baseline_avg_latency}s)"

    print(f"✓ End-to-end test passed")
    print(f"  Baseline latency: {baseline_avg_latency:.2f}s")
    print(f"  Enhanced latency: {enhanced_avg_latency:.2f}s")
    print(f"  Overhead: {latency_increase:.2f}s")
```

#### Success Criteria

- [x] Pipeline completes without errors (no exceptions)
- [x] All validation levels pass on real llms.txt files
- [x] All 3 layers built successfully (entries > 0)
- [x] Both agents respond to all 5 test queries
- [x] Enhanced agent latency overhead ≤ 4 seconds
- [x] Metrics collected and exported successfully

---

### [v0.0.7] Test Scenario 5: Ecosystem Validation Test

**Goal:** Verify the ecosystem pipeline discovers multi-file documentation, resolves cross-file links, detects broken references, and produces a meaningful health score.

#### Scenario Description

Real-world projects publish documentation across multiple files: an `llms.txt` index file linking to individual `.md` content pages, an optional `llms-full.txt` aggregation, and possibly instruction files. The ecosystem pipeline must discover all files, map relationships between them, validate cross-file link integrity, and score overall ecosystem health. A broken link (index references a file that doesn't exist) should be flagged, and an ecosystem with full coverage should score higher than one with gaps.

#### Test Steps

```
1. Set up a test ecosystem directory with:
   - llms.txt (index file with 5 links: 3 to .md pages, 1 to llms-full.txt, 1 external URL)
   - 3 .md content pages (matching 3 of the 5 links)
   - llms-full.txt (matching 1 of the 5 links)
   - 1 broken link target (file referenced in llms.txt but NOT present)
   Expected: 5 total files discovered; 1 broken link detected

2. Run ecosystem discovery (Stage 1)
   Expected: File manifest contains 4 files (llms.txt, 3 .md, llms-full.txt)
   Expected: I010 NOT emitted (multi-file ecosystem, not single-file)
   Expected: Discovery completes in < 3 seconds

3. Run per-file validation (Stage 2)
   Expected: Each file has independent ValidationResult and QualityScore
   Expected: Per-file results identical to standalone validation (FR-080, FR-083)

4. Run relationship mapping (Stage 3)
   Expected: 5 FileRelationship objects created
   Expected: 3 INDEXES (index → .md pages), 1 AGGREGATES (index → full), 1 EXTERNAL

5. Run ecosystem validation (Stage 4)
   Expected: W012 (BROKEN_CROSS_FILE_LINK) emitted for the missing file
   Expected: W012 diagnostic includes source_file (llms.txt) and target URL

6. Run ecosystem scoring (Stage 5)
   Expected: Completeness score < 100 (4 of 5 links resolved = ~80%)
   Expected: EcosystemScore has grade, dimensions, per-file score map

7. Run same pipeline on single-file input (regression check)
   Expected: I010 (ECOSYSTEM_SINGLE_FILE) emitted
   Expected: Per-file output byte-identical to standalone pipeline (FR-083)
```

#### Acceptance Test

```python
# test_ecosystem_validation.py

def test_ecosystem_discovery_and_validation():
    """Ecosystem pipeline should discover files, resolve links, and score health."""

    # Set up test ecosystem
    ecosystem_dir = create_test_ecosystem(
        index_links=5,  # 3 .md + 1 full + 1 external
        content_pages=3,
        has_full=True,
        broken_links=1,  # 1 link target missing
    )

    # Run full ecosystem pipeline
    pipeline = EcosystemPipeline()
    result = pipeline.run(ecosystem_dir)

    # Stage 1: Discovery
    assert result.manifest.file_count == 4, \
        f"Expected 4 files, got {result.manifest.file_count}"
    assert result.manifest.index_file is not None, \
        "Must discover index file (llms.txt)"

    # Stage 2: Per-file validation
    for eco_file in result.manifest.files:
        assert eco_file.validation is not None, \
            f"File {eco_file.file_id} missing validation results"
        assert eco_file.quality is not None, \
            f"File {eco_file.file_id} missing quality score"

    # Stage 3: Relationship mapping
    relationships = result.relationships
    indexes_count = sum(1 for r in relationships if r.relationship_type == "INDEXES")
    aggregates_count = sum(1 for r in relationships if r.relationship_type == "AGGREGATES")
    external_count = sum(1 for r in relationships if r.relationship_type == "EXTERNAL")

    assert indexes_count == 3, f"Expected 3 INDEXES, got {indexes_count}"
    assert aggregates_count == 1, f"Expected 1 AGGREGATES, got {aggregates_count}"
    assert external_count == 1, f"Expected 1 EXTERNAL, got {external_count}"

    # Stage 4: Ecosystem validation
    w012_diagnostics = [d for d in result.diagnostics if d.code == "W012"]
    assert len(w012_diagnostics) == 1, \
        f"Expected 1 W012 (broken link), got {len(w012_diagnostics)}"
    assert w012_diagnostics[0].source_file is not None, \
        "W012 must include source_file context"

    # Stage 5: Ecosystem scoring
    assert 0 <= result.score.total_score <= 100, \
        f"Score out of range: {result.score.total_score}"
    assert result.score.total_score < 100, \
        "Score should be < 100 due to broken link"
    assert "COMPLETENESS" in result.score.dimensions, \
        "Must include COMPLETENESS dimension"
    assert len(result.score.per_file_scores) == 4, \
        f"Expected 4 per-file scores, got {len(result.score.per_file_scores)}"

    print(f"✓ Ecosystem validation passed")
    print(f"  Files discovered: {result.manifest.file_count}")
    print(f"  Relationships mapped: {len(relationships)}")
    print(f"  Broken links detected: {len(w012_diagnostics)}")
    print(f"  Ecosystem score: {result.score.total_score:.1f} ({result.score.grade})")


def test_single_file_backward_compatibility():
    """Single-file input must produce byte-identical output to pre-pivot pipeline."""

    single_file = load_test_file("sample_llms.txt")

    # Run standalone (pre-pivot) pipeline
    standalone_result = standalone_pipeline.validate(single_file)
    standalone_quality = standalone_pipeline.score(single_file)

    # Run ecosystem pipeline on single file
    eco_result = EcosystemPipeline().run_single_file(single_file)

    # Verify byte-identical per-file output
    assert eco_result.files[0].validation == standalone_result, \
        "Ecosystem-wrapped validation must be identical to standalone"
    assert eco_result.files[0].quality == standalone_quality, \
        "Ecosystem-wrapped quality must be identical to standalone"

    # Verify I010 emitted
    i010_diagnostics = [d for d in eco_result.diagnostics if d.code == "I010"]
    assert len(i010_diagnostics) == 1, \
        "Must emit I010 (ECOSYSTEM_SINGLE_FILE) for single-file input"
```

#### Success Criteria

- [x] Discovery finds all files in a multi-file ecosystem (index + content pages + full)
- [x] Per-file validation results are identical to standalone pipeline (byte-identical)
- [x] Relationship mapping correctly classifies INDEXES, AGGREGATES, and EXTERNAL links
- [x] Broken cross-file links detected and flagged as W012 with source context
- [x] Ecosystem score reflects link resolution rate (broken link → score < 100)
- [x] Single-file backward compatibility preserved (I010 emitted, output identical)
- [x] Full 5-stage pipeline completes without errors on multi-file ecosystem

---

## Part 3: Quantitative Success Metrics

### Performance Metrics

| Metric | Baseline Target | Enhanced Target | Verification |
|---|---|---|---|
| **Agent accuracy (0–100%)** | 50–65% | 70–85% | LLM judge scores responses on test queries (20+ total) |
| **Parse time (typical file)** | < 500ms | < 500ms | Measure with timeit on 10+ real files |
| **Context build time** | N/A | < 2s | Measure end-to-end (layers 0–2) on 10+ files |
| **Agent response latency** | 5–8s | 8–12s | Measure wall-clock time for 20 test queries (p50, p95) |
| **Memory usage (peak)** | < 150MB | < 200MB | Profile with memory_profiler on largest file |
| **Test coverage (core modules)** | N/A | ≥ 80% | Run pytest with coverage on validation, parsing, context building |
| **[v0.0.7] Ecosystem discovery time** | N/A | < 3s (≤ 20 files) | Measure with timeit on test ecosystems of varying size |
| **[v0.0.7] Ecosystem pipeline total time** | N/A | < 10s (≤ 20 files) | Measure all 5 stages end-to-end on test ecosystems |
| **[v0.0.7] Ecosystem memory overhead** | N/A | < 50MB additional | Profile ecosystem pipeline vs single-file on same files |

### Quality Metrics

| Metric | Target | Verification |
|---|---|---|
| **Code style compliance** | 100% Black + Ruff | Run linters in CI; no violations |
| **Documentation coverage** | 100% public API documented | Every function has docstring + example |
| **Validation accuracy (L0–L4)** | ≥ 90% on test set | Run validator on 20 test files; compare output to expected |
| **Few-shot relevance** | 80%+ of examples relevant to queries | Evaluate similarity between selected examples and test queries |
| **Demo responsiveness** | < 200ms for UI interactions | Measure Streamlit widget response time |
| **Concept map connectivity** | ≥ 50% of concepts have relationships | Verify edges_count ≥ 0.5 * concepts_count |
| **[v0.0.7] Ecosystem discovery time** | < 3s for ≤ 20 files | Measure discovery on test ecosystems of 1, 5, 10, 20 files |
| **[v0.0.7] Ecosystem scoring time** | < 1s per ecosystem | Measure scoring on 5+ test ecosystems |
| **[v0.0.7] Cross-file link resolution accuracy** | 100% (no false positives/negatives) | Test with known-good and known-broken links; verify zero misclassification |
| **[v0.0.7] Backward compatibility (single-file)** | 100% byte-identical output | Diff ecosystem-wrapped vs standalone on 10+ files; zero differences |

### A/B Test Statistical Significance

| Metric | Target | Verification |
|---|---|---|
| **Accuracy improvement p-value** | p < 0.05 | Run t-test on accuracy scores (20+ queries); report p-value |
| **Minimum effect size** | Δ ≥ 5 percentage points | (Enhanced accuracy) - (Baseline accuracy) ≥ 5 pts |
| **Sample size** | ≥ 20 queries | Ensure at least 20 queries in A/B test |
| **Confidence interval (95%)** | Accuracy CI doesn't include 0 | Compute CI on accuracy difference |

---

## Part 4: Qualitative Success Criteria

| Criterion | Definition | Verification |
|---|---|---|
| **Code Quality** | Code is clean, readable, well-organized; follows Python conventions | Code review check: style compliant, functions < 50 lines, clear variable names |
| **Documentation Quality** | README is complete; modules have docstrings; examples provided | Human review: can a new developer understand the project in < 30 minutes? |
| **Portfolio Value** | Project demonstrates technical depth and communication skills | Portfolio reviewer assessment: impressive? Well-structured? Clear business value? |
| **Runnable Demo** | Streamlit app works; can upload llms.txt; agents respond cleanly | Demo test: fresh clone of repo; `streamlit run` works immediately |
| **Error Handling** | Errors are graceful; don't crash; provide remediation | Test 10 error scenarios; verify all have actionable error messages |
| **Reproducibility** | Results are deterministic; can re-run tests and get same results | Run tests twice; verify same results (unless randomized by design) |

---

## Part 5: Demo Scenario Script

### The 2-Minute Portfolio Presentation

**Goal:** Demonstrate DocStratum's value in a clear, impressive 2-minute flow.

#### Setup (30 seconds)

```
Presenter: "Let me show you DocStratum, a project I built to improve how LLMs
understand documentation."

[Screen shows: DocStratum GitHub repo with nice README]

"The problem: When LLMs browse documentation, they lose context. Navigation,
sidebars, and unrelated content pollute the content. DocStratum fixes this by
creating a structured index, concept map, and few-shot examples."

[Show diagram: Master Index → Concept Map → Few-Shot Bank]
```

#### Demo Part 1: Load & Parse (20 seconds)

```
Presenter: "Let's start by loading a real documentation site—Stripe's docs."

[Demo screen shows Streamlit app]
[Click: "Upload or Enter URL"]
[Input: "https://docs.stripe.com/llms.txt"]
[Screen shows: Parsed structure, sections, entries, validation results]

Presenter: "The system parsed 50+ entries, identified 20 concepts, and created
few-shot examples. All validation passed (green checkmarks)."

[Point to: Layer 0 (30 entries), Layer 1 (18 concepts), Layer 2 (15 examples)]
```

#### Demo Part 2: Side-by-Side Agent Comparison (60 seconds)

```
Presenter: "Now, let's see how baseline vs. enhanced agents answer the same
question."

[Click: Query input field]
[Type: "How do I authenticate with the Stripe API?"]
[Click: "Compare Agents"]

[Screen shows: Side-by-side responses]

Left Column (Baseline):
"To authenticate with the Stripe API, use your API key. Set the Authorization
header to 'Bearer [key]'. See the authentication section for details."

Right Column (Enhanced):
"Stripe uses API key authentication. Two modes:

1. Test Key (sk_test_...): Development/testing
2. Live Key (sk_live_...): Production

For requests, include in Authorization header: 'Bearer [key]'

Related: Verify mode (Section: Security), Rate limits (Section: API Overview)"

Metrics shown below:
Baseline: Accuracy 6/10 | Latency 5.2s | Tokens: 200
Enhanced: Accuracy 8/10 | Latency 7.8s | Tokens: 380

Presenter: "The enhanced agent provides more context and explicitly disambiguates
test vs. live keys—something the baseline missed. The concept map and few-shot
examples improve accuracy by ~30%."

[Click: "Show Concept Map"]
[Shows: Interactive graph or table of authentication-related concepts]
```

#### Demo Part 3: A/B Test Results (30 seconds)

```
Presenter: "Here are the aggregate results from 20 test queries:"

[Screen shows: Metrics table]

| Metric | Baseline | Enhanced | Improvement |
|---|---|---|---|
| Accuracy | 58% | 75% | +17 pts |
| Latency | 5.2s | 7.8s | +2.6s |
| Test Pass Rate | 60% | 85% | +25% |

[Chart showing: Accuracy comparison (bar chart or scatter plot)]

Presenter: "Across 20 real-world queries, the enhanced agent improved accuracy
by 17 percentage points—statistically significant (p < 0.05). The 2.6-second
latency overhead is acceptable for the improvement."
```

#### Closing (10 seconds)

```
Presenter: "DocStratum proves that structured context matters. By hand-crafting
an index, concept map, and few-shot examples, we can significantly improve
LLM performance on documentation tasks. The code is open-source on GitHub, and
the specification is ready for community use."

[Show: GitHub repo + stars badge]
```

#### Full Script (Timed)

```
0:00–0:30   Setup + Problem statement
0:30–0:50   Demo Part 1: Load & Parse (show Streamlit UI)
0:50–2:00   Demo Part 2: Side-by-side agents (show responses + metrics)
2:00–2:30   Demo Part 3: A/B test results (show aggregate metrics)
2:30–2:45   Closing: Impact + call to action
```

#### Technical Requirements for Demo

- [ ] Streamlit app deployed or running locally (fresh clone must work)
- [ ] Sample llms.txt available (e.g., Stripe, Nuxt, or custom)
- [ ] Both agents responding (baseline + enhanced)
- [ ] Metrics visible and reasonable
- [ ] No errors or crashes during demo
- [ ] Demo completes in < 3 minutes (comfortable pacing)

---

## Part 6: Definition of Done (D.O.D.) Checklist

### Conditions for v0.6.0 Release

The project is **DONE** when ALL of the following are true:

#### Code & Implementation

- [ ] All 45 MUST features (from Part 1) are implemented and tested **[v0.0.7: was 32]**
- [ ] All code passes Black + Ruff linters (zero violations)
- [ ] Core modules (validation, parsing, context) have ≥ 80% test coverage
- [ ] Unit tests pass (pytest with -v flag, 0 failures)
- [ ] Integration tests pass (end-to-end pipeline on 5+ real llms.txt files)
- [ ] **[v0.0.7]** Ecosystem integration tests pass (multi-file ecosystem on 3+ test fixtures)
- [ ] **[v0.0.7]** Single-file backward compatibility test passes (byte-identical output, FR-083)
- [ ] No console errors or warnings during test runs
- [ ] Code review complete (even self-review is okay for solo project)

#### Documentation

- [ ] README.md is complete and professional
  - [ ] Problem statement (context collapse)
  - [ ] Solution overview (3-layer architecture)
  - [ ] Quick start (clone, install, run)
  - [ ] Feature highlights
  - [ ] Architecture diagram
  - [ ] Contributing guidelines
- [ ] API documentation (docstrings) covers all public functions
- [ ] Design documents (v0.0.1–v0.0.7 specs) are published **[v0.0.7: was v0.0.5]**
- [ ] Examples provided for:
  - [ ] Loading and parsing llms.txt
  - [ ] Building context layers
  - [ ] Running both agents
  - [ ] Launching Streamlit demo

#### Demo & Testing

- [ ] Streamlit demo app runs without errors (`streamlit run app.py`)
- [ ] Demo accepts file upload and URL input
- [ ] Demo shows parsed structure, validation results, side-by-side agents
- [ ] Metrics display correctly (accuracy, latency, tokens)
- [ ] 20+ test queries pass with expected metrics
- [ ] A/B test shows statistically significant improvement (p < 0.05)
- [ ] Demo scenario script runs without issues (2-minute flow is clean)
- [ ] **[v0.0.7]** Ecosystem test scenario (Test Scenario 5) passes all acceptance criteria
- [ ] **[v0.0.7]** Ecosystem discovery completes in < 3s for test fixtures (≤ 20 files)
- [ ] **[v0.0.7]** W012 diagnostics correctly flag all broken cross-file links in test fixtures

#### Success Metrics Met

- [ ] Agent accuracy improvement: ≥ 5 percentage points (baseline 50–65%, enhanced 70–85%)
- [ ] Parse time: < 500ms for typical files
- [ ] Context build time: < 2 seconds
- [ ] Agent latency overhead: ≤ 4 seconds
- [ ] Memory usage: < 200MB peak
- [ ] Test coverage: ≥ 80% on core modules
- [ ] Validation accuracy: ≥ 90% on test files
- [ ] **[v0.0.7]** Ecosystem discovery time: < 3s for ≤ 20 files
- [ ] **[v0.0.7]** Ecosystem pipeline total time: < 10s for ≤ 20 files
- [ ] **[v0.0.7]** Backward compatibility: 100% byte-identical single-file output
- [ ] **[v0.0.7]** Cross-file link resolution: 100% accuracy (no false positives/negatives)

#### Portfolio Presentation

- [ ] Code is clean, readable, and well-structured
- [ ] No hard-coded credentials or secrets in code
- [ ] GitHub repo is public and well-organized
- [ ] README is polished and professional
- [ ] Demo is impressive and runs reliably
- [ ] Can explain the project in < 3 minutes

#### Scope & Constraints Respected

- [ ] No out-of-scope features added (v0.0.5c boundaries maintained, including 8 ecosystem OOS items **[v0.0.7]**)
- [ ] Scope change process was followed for any changes
- [ ] Time budget respected (≤ 60 hours)
- [ ] Tech stack unchanged (Pydantic, LangChain, Streamlit, Anthropic API)
- [ ] Research-driven design maintained (all features justified by v0.0.1–4, v0.0.6, v0.0.7)
- [ ] **[v0.0.7]** Ecosystem features limited to MVP scope (no full 5-dimension scoring, no content page validation, no URL crawl discovery — see v0.0.5c Category H)

---

## Part 7: Definition of Almost Done (Warning Signs)

### When to Worry (Before Release)

**DO NOT RELEASE** if any of these are true:

- [ ] Any of the 45 MUST features is missing or partially working **[v0.0.7: was 32]**
- [ ] Test coverage < 75% on core modules
- [ ] A/B test shows no significant improvement (p ≥ 0.05)
- [ ] Demo crashes or shows errors
- [ ] Code has lint violations (Black/Ruff failures)
- [ ] Performance targets not met (parse > 500ms, context > 2s)
- [ ] Error handling is poor (no line numbers, unclear messages)
- [ ] Documentation is incomplete or hard to follow
- [ ] GitHub repo has unrelated files or mess
- [ ] Any security issues (credentials, unsafe input handling)
- [ ] **[v0.0.7]** Single-file backward compatibility broken (ecosystem-wrapped output differs from standalone)
- [ ] **[v0.0.7]** Ecosystem discovery takes > 5s on test fixtures (≤ 20 files)
- [ ] **[v0.0.7]** Cross-file link resolution has false positives or negatives
- [ ] **[v0.0.7]** Ecosystem pipeline crashes or silently drops files during discovery

---

## Part 8: Stretch Goals (If Time Permits)

### Nice-to-Have Features with Effort Estimates

| Feature | Effort | Priority | Effort OK? | Notes |
|---|---|---|---|---|
| FR-061: Metrics display (accuracy, latency, tokens w/ visual indicators) | 2–3 hours | SHOULD | Only if ≥ 4 hours remain | **Highest-impact stretch goal** — demo script (Part 5) relies on visible metrics; significantly enhances portfolio presentation |
| FR-067: Cross-module logging (key decisions at INFO level) | 2–3 hours | SHOULD | Only if ≥ 4 hours remain | Important for debugging and traceability; strengthens code quality narrative for portfolio |
| FR-014: Freshness signal detection | 2–3 hours | SHOULD | Only if ≥ 5 hours remain | Nice visual indicator; supports Test Scenario 2 (Freshness Test) |
| FR-019: Authority assignment | 2–3 hours | SHOULD | Only if ≥ 5 hours remain | Mark canonical definitions per concept |
| FR-005: Content validation (L2) | 2–3 hours | SHOULD | Only if ≥ 5 hours remain | Check descriptions non-empty; URL resolution |
| FR-062: Concept map graph visualization | 4–6 hours | COULD | Only if ≥ 8 hours remain | Visually impressive but not essential |
| FR-031: Streaming parser | 3–4 hours | COULD | Only if ≥ 6 hours remain | For very large files (>50MB) |
| FR-050: Agent templates | 3–5 hours | COULD | Only if ≥ 8 hours remain | Chatbot vs Q&A vs copilot modes |
| Write blog post | 2–4 hours | COULD | Only if ≥ 6 hours remain | "How we built DocStratum" |
| Record video demo | 2–3 hours | COULD | Only if ≥ 5 hours remain | Screencast walkthrough |
| **[v0.0.7]** FR-085: Streamlit ecosystem view (file manifest, relationships, health score) | 3–4 hours | SHOULD | Only if ≥ 6 hours remain | Ecosystem tab in demo; significantly enhances portfolio for ecosystem narrative |
| **[v0.0.7]** FR-079: Ecosystem anti-pattern detection (6 patterns: Index Island, Phantom Links, etc.) | 2–3 hours | SHOULD | Only if ≥ 5 hours remain | Detection rules for AP_ECO_001–006; strengthens diagnostic depth |
| **[v0.0.7]** FR-082: Ecosystem Coverage scoring (11 canonical categories across ecosystem) | 2–3 hours | SHOULD | Only if ≥ 4 hours remain | Second health dimension; Completeness (FR-081) alone is sufficient for MVP |
| **[v0.0.7]** FR-075: File type classification heuristics (content analysis beyond filename) | 1–2 hours | SHOULD | Only if ≥ 3 hours remain | Filename patterns are sufficient for MVP; content heuristics add robustness |

### Decision Rule for Stretch Goals

**Only add a stretch goal if:**

1. All 32 MUST features are complete and tested
2. Highest-impact SHOULD features prioritized first (FR-061 → FR-067 → FR-014 → others)
3. Test coverage ≥ 80% on core modules
4. Time remaining > effort estimate + 30% buffer
5. The stretch goal doesn't risk breaking existing features

---

## Part 9: Inputs from Previous Sub-Parts

| Source | What It Provides | Used In |
|--------|-----------------|---------|
| v0.0.1 — Specification Deep Dive | 8 specification gaps with P0/P1/P2 priority; ABNF grammar defining parser behavior; 28 edge cases; bimodal document type classification (Type 1 Index vs Type 2 Full); 11 empirical specimen conformance data | Test Scenario 4 (integration with real llms.txt files); demo scenario (Stripe as example); acceptance test design (parse real files without errors) |
| v0.0.1c — Context & Processing Patterns | 6-phase hybrid pipeline architecture; token budgeting strategy ("8K curated > 200K raw"); processing method tradeoff matrix; pipeline configuration interface | Part 3 quantitative metrics (context build < 2s, token budget ≤ 4K); MVP features FR-032–035 acceptance criteria; demo Part 2 timing budget |
| v0.0.2 — Wild Examples Audit | 18 audited implementations + 6 specimen expansions; quality predictors (r ≈ 0.65 for code examples, r ≈ −0.05 for size); 5 archetypes; gold standards (Svelte 5/5, Pydantic 5/5); 15 best practices; 12 anti-patterns | Test Scenario 1 (disambiguation relies on concept map value); Part 4 qualitative criteria (code quality, documentation quality); demo scenario pacing and content selection |
| v0.0.3 — Ecosystem Survey | Adoption Paradox (grassroots adoption, zero confirmed LLM provider usage); 75+ tools with zero formal validation; MCP as validated transport; 25 consolidated gaps; DECISION-015 (AI coding assistants via MCP as primary target) | Part 5 demo positioning ("DocStratum improves agent performance"); Part 4 portfolio value criteria; strategic framing of success metrics (target coding assistants, not search LLMs) |
| v0.0.4 — Best Practices Synthesis | 57 automated checks; 100-point composite quality scoring; 22 anti-patterns with detection rules; 16 design decisions; token budget architecture (4 tiers); MUST/SHOULD/COULD framework | Part 3 quantitative metrics (validation accuracy ≥ 90%); Part 1 acceptance test design (validation levels referenced); Part 6 DoD code quality standards (Black + Ruff compliance) |
| v0.0.5a — Functional Requirements | 68 FRs (FR-001–FR-068) with MoSCoW priorities; 32 MUST, 29 SHOULD, 7 COULD; module-level organization; acceptance tests per FR; traceability to research and implementation | Part 1 MVP Feature Checklist (all 32 MUST features); Part 8 stretch goals (drawn from SHOULD/COULD); MVP Module Distribution table; Test Scenario acceptance tests reference FR acceptance criteria |
| v0.0.5b — Non-Functional Requirements & Constraints | 21 NFRs with measurable targets; 6 hard constraints (CONST-001–006); per-module quality targets; trade-off resolutions; risk mitigation strategies | Part 3 quantitative metrics (NFR-001: < 500ms, NFR-002: < 2s, NFR-003: < 8s, NFR-004: < 12s, NFR-005: < 200MB, NFR-010: ≥ 80%); Part 6 DoD success metrics thresholds; Part 7 warning signs (performance target failures) |
| v0.0.5c — Scope Definition & Out-of-Scope Registry | 40 OOS items across 8 categories **[v0.0.7: was 32 across 7]**; in-scope boundary statement (9 deliverables + ecosystem additions); deferred features registry (14 items **[v0.0.7: was 11]**); Scope Fence decision tree; scope change management process | Part 6 DoD "Scope & Constraints Respected" gate; Part 8 stretch goals (informed by deferred features registry effort estimates); Part 7 warning signs (scope drift detection); **[v0.0.7]** ecosystem OOS items (Category H) gate ecosystem scope creep |
| **[v0.0.7]** v0.0.6 — Platinum Standard Definition | 30-criterion, 5-level quality framework (L0 Parseable → L4 Exemplary); explicit provenance for every criterion; maps to existing diagnostic codes, anti-patterns, and quality dimensions | **[v0.0.7]** Part 1 Module 8 validation criteria (what ecosystem validation measures against); Part 3 quality metrics (validation accuracy targets); Part 6 DoD (quality standards) |
| **[v0.0.7]** v0.0.7 — Ecosystem Pivot Specification | 3-layer ecosystem model (Navigation, Content, Aggregate); 6 new schema entities; 12 new diagnostic codes (E009–E010, W012–W018, I008–I010); 6 new anti-patterns (AP_ECO_001–006); 5-stage pipeline architecture; 4-phase migration plan; backward compatibility requirements | **[v0.0.7]** Part 1 Module 8 (all 13 MUST features); Test Scenario 5 (ecosystem validation); Part 3 ecosystem metrics; Part 6 DoD ecosystem gates; Part 8 ecosystem stretch goals |

---

## Part 10: Outputs to Next Phase

| Output | Consumed By | How It's Used |
|--------|------------|---------------|
| 45 MVP features with acceptance tests (Part 1) **[v0.0.7: was 32]** | v0.1.0–v0.6.0 (Implementation) | Each implementation module knows exactly which features must pass which acceptance tests before the module is complete; **[v0.0.7]** includes 13 ecosystem features for Module 8 |
| 5 test scenarios with executable pseudocode (Part 2) **[v0.0.7: was 4]** | v0.5.x (Testing & Validation) | Test scenarios become the integration test suite; pseudocode translates directly to pytest fixtures; **[v0.0.7]** Test Scenario 5 covers ecosystem discovery, validation, and scoring |
| Quantitative success metrics with targets (Part 3) | v0.5.x (Testing & Validation) | Metrics targets become CI/CD quality gates; performance benchmarks run automatically |
| A/B test statistical significance requirements (Part 3) | v0.5.x (Testing & Validation) | p < 0.05 requirement shapes sample size decisions; minimum 20 queries established |
| Demo scenario script with timing (Part 5) | v0.6.0 (Demo Layer) | Streamlit UI design must support the exact 2-minute flow; all referenced features must work for the demo |
| Definition of Done checklist (Part 6) | v0.6.0 (Release Gate) | Release manager (solo developer) uses this checklist as the final release gate; every unchecked item blocks release |
| Warning signs list (Part 7) | v0.1.0–v0.6.0 (Continuous) | Early warning system; any warning sign triggers remediation before further feature work |
| Stretch goals with effort estimates (Part 8) | v0.5.x–v0.6.0 (If Time Permits) | Decision rule gates stretch goal implementation; FR-061 and FR-067 are highest priority if time allows |
| Test Query Bank — 20 sample questions (Appendix) | v0.5.x (Testing) | Starting point for the formal test query set; covers 20 distinct capability areas |
| **[v0.0.7]** Ecosystem test fixtures specification (Test Scenario 5) | v0.2.7–v0.2.8 (Ecosystem Implementation) | Defines the exact structure of test ecosystems (multi-file, single-file, broken links) that implementation modules must create as test fixtures |
| **[v0.0.7]** Ecosystem performance targets (Part 3) | v0.2.7–v0.2.8 (Ecosystem Implementation) | Discovery < 3s, pipeline < 10s, memory overhead < 50MB — implementation must meet these thresholds |
| **[v0.0.7]** Backward compatibility specification (FR-083, Test Scenario 5) | v0.2.7 (EcosystemPipeline) | Byte-identical output requirement becomes regression test; any ecosystem change must not alter single-file behavior |

---

## Part 11: Limitations & Constraints

1. **Accuracy metrics depend on LLM judge quality.** Part 3 defines agent accuracy as an LLM judge score (0–100%). The reliability of this metric depends on the judge model's ability to consistently evaluate response quality. Judge model selection (GPT-4, Claude) is an implementation decision deferred to v0.5.x. Variability in judge scoring may require calibration runs and inter-rater reliability checks before accepting A/B test results as statistically significant.

2. **Baseline performance targets are estimates.** Part 3 targets baseline accuracy at 50–65% and enhanced accuracy at 70–85%. These ranges are informed by v0.0.4's quality predictor analysis and general LLM benchmark data, but actual performance depends on the specific llms.txt files used, the query complexity, and the LLM provider's response quality. Targets will be validated and potentially adjusted during v0.5.x (Testing & Validation).

3. **Demo scenario script assumes specific UI layout.** Part 5 scripts a precise 2-minute flow with left/right columns, metrics badges, and concept map visualization. The actual Streamlit implementation may require layout adjustments based on widget capabilities. The script is a target to aim for, not a rigid specification — if a particular visual element (e.g., concept graph) is deferred (OOS-G1), the demo should gracefully omit it and emphasize available features.

4. **Statistical significance requires sufficient query diversity.** Part 3 requires p < 0.05 from a t-test on 20+ queries. If the test query set lacks diversity (e.g., all queries test the same capability), the p-value may be misleading. The 4-category test design (FR-056) mitigates this, but the 20-query minimum is the floor, not the ceiling — 50+ queries (per FR-055) provide more reliable significance.

5. **Definition of Done is strict by design.** Part 6's checklist is intentionally comprehensive. In a solo-developer context (CONST-001), some items may require pragmatic interpretation — for example, "code review complete (even self-review is okay for solo project)" acknowledges that external code review is infeasible. The DoD reflects aspirational professional quality, not bureaucratic compliance.

6. **Stretch goal effort estimates are pre-implementation approximations.** Part 8's effort estimates (2–6 hours per feature) are based on research-phase understanding of complexity. Actual implementation effort may be higher if dependent features reveal unexpected integration challenges. The 30% buffer in the decision rule partially mitigates this risk.

7. **Test Scenario 4 depends on external API availability.** The integration happy-path test (Part 2, Scenario 4) fetches a real llms.txt file from a production URL (e.g., Stripe). If the URL is unavailable at test time (CDN blocking, site changes, domain migration), the test must fall back to a locally cached specimen file. This limitation was already identified in v0.0.2a (CDN/WAF protections) and the Loader module (FR-030: caching) provides the mitigation.

8. **[v0.0.7] Ecosystem test scenarios use synthetic fixtures, not real-world ecosystems.** Test Scenario 5 creates controlled test directories with known file counts, link structures, and intentional broken links. Real-world documentation ecosystems may have unexpected structures (nested directories, symlinks, non-standard filenames) that synthetic fixtures don't capture. The discovery module (FR-074) should be tested against at least one real-world project directory in addition to synthetic fixtures once implementation begins.

9. **[v0.0.7] Ecosystem scoring uses only 2 of 5 planned health dimensions.** The MVP implements Completeness (FR-081) and optionally Coverage (FR-082, SHOULD priority). The full 5-dimension model (Completeness, Coherence, Coverage, Freshness, Navigability) defined in v0.0.7 Section 4.3 is deferred to post-MVP (OOS-H1). The 2-dimension model provides a meaningful health signal but cannot detect all ecosystem quality issues (e.g., stale content pages, poor navigability).

10. **[v0.0.7] Backward compatibility testing is limited to output comparison.** FR-083 requires byte-identical output for single-file inputs. "Byte-identical" is measured by comparing serialized `ValidationResult` and `QualityScore` objects. Internal implementation details (e.g., timing, memory allocation, intermediate data structures) may differ between ecosystem-wrapped and standalone execution. This is acceptable — the contract is output equivalence, not implementation equivalence.

---

## Part 12: User Stories

> As a **solo developer building DocStratum**, I need a precise, unambiguous "Definition of Done" checklist so that I can answer "Is v0.6.0 ready to release?" with a binary yes/no by walking through the checklist — eliminating the subjective "feels done" trap that causes solo projects to either ship prematurely (missing features, broken tests) or never ship at all (perfectionism spiral, scope creep into stretch goals).

> As a **solo developer managing my own quality bar (CONST-006: 40–60 hours)**, I need quantitative success metrics with specific numeric targets (accuracy ≥ 5 percentage points improvement, parse time < 500ms, p-value < 0.05) so that I can make evidence-based decisions about whether DocStratum actually works — not just whether it runs without errors. The metrics transform "I think it's better" into "it is measurably better, with statistical confidence."

> As a **portfolio evaluator reviewing DocStratum**, I need to see a convincing 2-minute demo that shows DocStratum's value clearly — not a feature tour, but a side-by-side comparison proving that structured context improves LLM performance. The demo scenario script (Part 5) is designed for this audience: problem statement (30s), live demo (80s), aggregate results with statistical significance (30s), closing with impact statement (10s). The A/B test results are the "proof slide" — without statistically significant improvement, the portfolio narrative collapses.

---

## Deliverables

- [x] MVP feature checklist (45 MUST features with acceptance tests, aligned to v0.0.5a) **[v0.0.7: was 32]**
- [x] Test scenarios with specific, measurable steps (5 scenarios × 4+ acceptance tests each) **[v0.0.7: was 4]**
- [x] Acceptance tests in pseudocode/Python (runnable tests for each scenario)
- [x] Quantitative success metrics with targets (traceable to v0.0.5b NFRs + **[v0.0.7]** ecosystem performance targets)
- [x] Qualitative success criteria (6 dimensions with rubrics)
- [x] Demo scenario script (2-minute timed walkthrough with section transitions)
- [x] Definition of Done checklist (5 dimensions + scope gate, **[v0.0.7]** expanded with ecosystem items)
- [x] Warning signs and stretch goals with effort estimates and decision rules (**[v0.0.7]** 4 ecosystem stretch goals + 4 ecosystem warning signs added)
- [x] Inputs from Previous Sub-Parts (traceability to v0.0.1–v0.0.7) **[v0.0.7: was v0.0.5c]**
- [x] Outputs to Next Phase (traceability to v0.1.0–v0.6.0, **[v0.0.7]** including ecosystem implementation targets)
- [x] Limitations & Constraints (10 documented) **[v0.0.7: was 7]**
- [x] User Stories (3 personas: solo developer, quality manager, portfolio evaluator)

---

## Acceptance Criteria

- [x] Every MUST feature from v0.0.5a is included in MVP checklist (all 45: 7+5+2+4+6+6+2+13) **[v0.0.7: was 32: 7+5+2+4+6+6+2]**
- [x] No SHOULD or COULD features are misclassified as MUST (FR-061, FR-067, FR-075, FR-079, FR-082, FR-085 correctly in stretch goals)
- [x] Every MVP feature has acceptance test (specific, measurable, testable)
- [x] Test scenarios are realistic (based on real llms.txt use cases from v0.0.2 specimens + **[v0.0.7]** synthetic ecosystem fixtures)
- [x] Quantitative metrics have targets (ms, %, points) traceable to v0.0.5b NFRs + **[v0.0.7]** ecosystem performance targets
- [x] Qualitative criteria are well-defined (6 dimensions with verification methods)
- [x] Demo scenario is timed and scripted (actually fits in 2–3 minutes)
- [x] D.O.D. checklist is comprehensive and unambiguous (5 dimensions + scope gate + **[v0.0.7]** ecosystem items)
- [x] Stretch goals are genuinely optional (not blocking release); decision rule gates implementation
- [x] Document structure is consistent with v0.0.5a/b/c (includes Inputs, Outputs, Limitations, User Stories)
- [x] Can answer "Is v0.6.0 done?" with a binary yes/no using the DoD checklist alone
- [x] **[v0.0.7]** Ecosystem MVP features (Module 8) trace to v0.0.6 and v0.0.7 research
- [x] **[v0.0.7]** Backward compatibility test (FR-083) is explicit in Test Scenario 5 and DoD checklist
- [x] **[v0.0.7]** Ecosystem stretch goals (4 SHOULD features) have effort estimates and priority order

---

## Next Step

Once this sub-part is approved:

**v0.1.0 — Project Foundation (Implementation Begins)**

Armed with completed v0.0 research and v0.0.5 requirements, implementation can begin with full confidence in scope, design, and success criteria.

---

## [v0.0.7] Part 13: Revision Change Log

### Change Record: v0.0.7 Ecosystem Pivot (2026-02-07)

| Section | Change | Justification |
|---|---|---|
| Sub-Part Overview | Updated FR count (68→85), MVP features (32→45), modules (7→8), test scenarios (4→5) | Reflects v0.0.7 ecosystem pivot additions |
| Dependencies | Added v0.0.6 and v0.0.7 as new upstream dependencies | New research phases inform ecosystem features |
| Part 1: MVP Feature Checklist | Added Module 8 with 13 MUST ecosystem features (FR-069–074, FR-076–078, FR-080–081, FR-083–084) | Ecosystem discovery, validation, and scoring are MVP requirements |
| Part 1: MVP Summary | Updated category counts (MUST 32→45, SHOULD 29→33); added Module 8 to distribution table | Reflects new ecosystem FRs from v0.0.5a Section 10 |
| Part 2: Test Scenarios | Added Test Scenario 5 (Ecosystem Validation) with 7 test steps and 2 acceptance tests | Ecosystem pipeline needs dedicated integration test coverage |
| Part 3: Quantitative Metrics | Added 7 ecosystem metrics (discovery time, pipeline time, memory, link accuracy, backward compatibility) | Ecosystem pipeline needs measurable performance targets |
| Part 6: DoD Checklist | Added 8 ecosystem items across Code, Demo, Metrics, and Scope dimensions | DoD must cover all MVP features including ecosystem |
| Part 7: Warning Signs | Added 4 ecosystem warning signs (backward compatibility, discovery time, link resolution, pipeline stability) | Ecosystem failures must block release |
| Part 8: Stretch Goals | Added 4 ecosystem SHOULD features (FR-085, FR-079, FR-082, FR-075) with effort estimates | Ecosystem SHOULD features are genuinely optional post-MVP |
| Part 9: Inputs | Added v0.0.6 and v0.0.7 rows; updated v0.0.5c row (32→40 OOS, 7→8 categories) | Traceability to new research phases |
| Part 10: Outputs | Added 3 ecosystem output rows (test fixtures, performance targets, backward compatibility spec) | Implementation needs ecosystem-specific guidance |
| Part 11: Limitations | Added 3 ecosystem limitations (#8 synthetic fixtures, #9 partial scoring dimensions, #10 output-only backward compat) | Known constraints of ecosystem MVP scope |
| Deliverables | Updated counts (32→45 MVP, 4→5 scenarios, 7→10 limitations) | Reflects expanded scope |
| Acceptance Criteria | Added 3 ecosystem acceptance criteria | Ensures ecosystem additions are verifiable |

> **Traceability:** All changes trace to `RR-SPEC-v0.0.7-ecosystem-pivot-specification.md` Section 10.2 (Design Document Revision Schedule) which identified v0.0.5d as a "REVISE" document. Changes are limited to additive ecosystem content — no original content was modified.

---

## Appendix: Test Query Bank (20 Sample Questions)

### For A/B Testing

```
1.  How do I authenticate with the API?
2.  What is the difference between test and live mode?
3.  When should I use webhooks?
4.  How do I handle errors in the API?
5.  What are the rate limits?
6.  How do I implement pagination?
7.  What is the difference between these two API endpoints?
8.  How do I validate webhook signatures?
9.  What is the versioning strategy?
10. How do I migrate from v1 to v2 API?
11. Can I use this feature with [specific technology]?
12. What is the cost/pricing model?
13. How do I debug a failed API request?
14. What are the security best practices?
15. How do I implement idempotency?
16. What happens if I exceed the rate limit?
17. Can I use this in a production environment?
18. How do I set up local development?
19. What are the dependencies for this library?
20. How do I contribute to this project?
```

These represent: authentication, mode/env differences, features, error handling, constraints, pagination, endpoint comparison, webhooks, versioning, migration, compatibility, pricing, debugging, security, idempotency, limits, production readiness, setup, dependencies, contribution.
