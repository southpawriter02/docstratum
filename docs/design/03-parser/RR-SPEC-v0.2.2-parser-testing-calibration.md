# v0.2.2 — Parser Testing & Calibration

> **Version:** v0.2.2
> **Document Type:** Design Specification (scope overview with sub-part breakdown)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SCOPE-v0.2.x-parser.md](RR-SCOPE-v0.2.x-parser.md)
> **Depends On:** [v0.2.0](RR-SPEC-v0.2.0-core-parser.md) (core parser), [v0.2.1](RR-SPEC-v0.2.1-classification-metadata.md) (enrichment)
> **Consumed By:** v0.3.x (Validation Engine), v0.7.x (Ecosystem Integration)

---

## 1. Purpose

v0.2.2 is the capstone of the parser phase. It validates the parser (v0.2.0) and enrichment (v0.2.1) implementations against three tiers of test data and integrates the parser into the ecosystem pipeline via the `SingleFileValidator` protocol.

Unlike v0.2.0 and v0.2.1, which produce source code, v0.2.2 produces primarily **test infrastructure and integration code**:

1. **Synthetic fixtures** — 5 hand-crafted `.txt` files exercising each conformance level
2. **Real-world specimens** — 6 regression tests against gold-standard calibration files
3. **Edge case coverage** — 33 test cases from the v0.0.1a formal grammar spec
4. **Pipeline integration** — `SingleFileValidator` implementation wiring parser + classifier into the ecosystem pipeline

### 1.1 User Stories

| ID       | As a...            | I want to...                                      | So that...                                              |
| -------- | ------------------ | ------------------------------------------------- | ------------------------------------------------------- |
| US-022-1 | Parser developer   | Have synthetic fixtures at each conformance level | I can verify parser correctness at each structural tier |
| US-022-2 | Regression tester  | Parse real-world specimens without crashes        | I know the parser handles production-quality files      |
| US-022-3 | Spec author        | Have every documented edge case covered by a test | I can confirm the parser follows the formal grammar     |
| US-022-4 | Pipeline developer | Plug the parser into the ecosystem pipeline       | Stage 2 produces parsed models for downstream stages    |
| US-022-5 | CI system          | Run `pytest` and get a pass/fail for the parser   | Regressions are caught before merge                     |

---

## 2. Architecture

### 2.1 File Structure

```
tests/
├── fixtures/
│   ├── ecosystems/           # (existing — v0.1.4 ecosystem fixtures)
│   └── parser/               # NEW — v0.2.2a/b fixtures
│       ├── synthetic/
│       │   ├── L0_fail.txt
│       │   ├── L1_minimal.txt
│       │   ├── L2_content.txt
│       │   ├── L3_best_practices.txt
│       │   └── L4_extended.txt
│       └── specimens/
│           ├── svelte.txt          # DS-CS-001
│           ├── pydantic.txt        # DS-CS-002
│           ├── vercel_ai_sdk.txt   # DS-CS-003
│           ├── shadcn_ui.txt       # DS-CS-004
│           ├── cursor.txt          # DS-CS-005
│           └── nvidia.txt          # DS-CS-006
├── test_parser_fixtures.py       # v0.2.2a — synthetic fixture tests
├── test_parser_specimens.py      # v0.2.2b — specimen regression tests
├── test_parser_edge_cases.py     # v0.2.2c — 33 edge case tests
└── test_parser_integration.py    # v0.2.2d — pipeline integration tests

src/docstratum/parser/
└── validator_adapter.py          # v0.2.2d — SingleFileValidator implementation
```

### 2.2 Dependency Map

```
v0.2.0 (Core Parser) ──────────────────────┐
v0.2.1 (Classification & Metadata) ─────────┤
                                            ▼
                              ┌─────────────────────────┐
                              │      v0.2.2              │
                              │                          │
                              │  a: Synthetic Fixtures   │  ← independent
                              │  b: Specimen Parsing     │  ← independent
                              │  c: Edge Case Coverage   │  ← independent
                              │  d: Pipeline Integration │  ← depends on a–c passing
                              └─────────────────────────┘
```

v0.2.2a, b, and c are independent test suites — they can be implemented in any order. v0.2.2d depends on all three passing because the integration adapter should not be merged until the parser is proven correct.

---

## 3. Sub-Part Breakdown

| Sub-Part                                                  | Title                           | Type              | Output                                       |
| --------------------------------------------------------- | ------------------------------- | ----------------- | -------------------------------------------- |
| [v0.2.2a](RR-SPEC-v0.2.2a-synthetic-test-fixtures.md)     | Synthetic Test Fixtures         | Test Data + Tests | 5 fixture files, 5 test functions            |
| [v0.2.2b](RR-SPEC-v0.2.2b-real-world-specimen-parsing.md) | Real-World Specimen Parsing     | Test Data + Tests | 6 specimen files, 6 regression tests         |
| [v0.2.2c](RR-SPEC-v0.2.2c-edge-case-coverage.md)          | Edge Case Coverage              | Tests             | 33 test cases (A1–A10, B1–B8, C1–C10, D1–D5) |
| [v0.2.2d](RR-SPEC-v0.2.2d-pipeline-integration.md)        | SingleFileValidator Integration | Source + Tests    | `validator_adapter.py`, integration tests    |

---

## 4. Workflows

### 4.1 Fixture-Based Testing

```
1. Developer creates/updates parser code in v0.2.0 or v0.2.1
2. Runs: pytest tests/test_parser_fixtures.py
3. Each fixture is parsed end-to-end:
   read_file → tokenize → populate → estimate_tokens
   → classify_document → match_canonical_sections → extract_metadata
4. Assertions verify expected model fields
5. All 5 fixtures must pass before v0.2.2d merge
```

### 4.2 Specimen Regression

```
1. 6 specimen .txt files are checked into tests/fixtures/parser/specimens/
2. Runs: pytest tests/test_parser_specimens.py
3. Each specimen parsed end-to-end
4. Structural assertions verify:
   - Title text
   - Section count
   - Link count per section
   - Blockquote presence
   - No exceptions
5. Test failures indicate parser regressions
```

### 4.3 Edge Case Sweep

```
1. Runs: pytest tests/test_parser_edge_cases.py
2. Each of 33 edge cases defined as inline test data
3. Parser invoked with precisely crafted input
4. Assertions verify parser behavior matches v0.0.1a spec
5. Coverage report confirms all edge case categories addressed
```

### 4.4 Pipeline Integration

```
1. ParserAdapter implements SingleFileValidator protocol
2. PerFileStage injected with ParserAdapter instance
3. Pipeline run: Discovery → Parse → Relationship → Ecosystem Validation → Scoring
4. Integration test verifies:
   - EcosystemFile.parsed is populated
   - EcosystemFile.classification is populated
   - context.project_name extracted from index H1
   - No crashes on multi-file ecosystems
```

---

## 5. Acceptance Criteria

### 5.1 Functional

- [ ] 5 synthetic fixtures exist in `tests/fixtures/parser/synthetic/` and all parse correctly.
- [ ] 6 specimen files exist in `tests/fixtures/parser/specimens/` and all parse without crashes.
- [ ] All 33 edge cases from v0.0.1a (A1–A10, B1–B8, C1–C10, D1–D5) covered by tests.
- [ ] `ParserAdapter` implements the `SingleFileValidator` protocol.
- [ ] The ecosystem pipeline's Stage 2 (`PerFileStage`) successfully uses `ParserAdapter`.
- [ ] `EcosystemFile.parsed` is populated after Stage 2 runs with `ParserAdapter`.
- [ ] `context.project_name` is extracted from the index file's H1 title.

### 5.2 Non-Functional

- [ ] `pytest --cov=docstratum.parser --cov-fail-under=85` passes.
- [ ] No external network access required by any test (all fixtures/specimens are local).
- [ ] `black --check` and `ruff check` pass on all test code.
- [ ] Google-style docstrings on all test modules.

### 5.3 CHANGELOG Entry Template

```markdown
## [0.2.2] - YYYY-MM-DD

**Parser Testing & Calibration — Comprehensive validation of the parser pipeline.**

### Added

#### Synthetic Test Fixtures (`tests/fixtures/parser/synthetic/`)

- 5 hand-crafted fixtures: L0 (fail), L1 (minimal), L2 (content), L3 (best practices), L4 (extended) (v0.2.2a)
- Each fixture validates specific parser capabilities at increasing structural complexity

#### Specimen Regression Tests (`tests/test_parser_specimens.py`)

- 6 regression tests against gold-standard calibration specimens: Svelte, Pydantic, Vercel AI SDK, Shadcn UI, Cursor, NVIDIA (v0.2.2b)
- Structural assertions: title, section count, link count, blockquote presence

#### Edge Case Coverage (`tests/test_parser_edge_cases.py`)

- 33 test cases covering v0.0.1a edge case catalog (v0.2.2c)
- Category A (structural, 10): empty file, no H1, multiple H1, code fences, etc.
- Category B (link format, 8): malformed URLs, empty titles, bare URLs, etc.
- Category C (content, 10): unicode, multiline blockquotes, trailing whitespace, etc.
- Category D (encoding, 5): BOM, non-UTF-8, null bytes, CRLF, CR-only

#### Pipeline Integration (`src/docstratum/parser/validator_adapter.py`)

- `ParserAdapter` implementing `SingleFileValidator` protocol (v0.2.2d)
- parse() and classify() fully functional; validate() and score() return stub results
- Integration test confirms end-to-end pipeline: Discovery → Parse → Relationships
```

---

## 6. Dependencies

| Module                      | What v0.2.2 Uses                                     |
| --------------------------- | ---------------------------------------------------- |
| `parser/io.py`              | v0.2.0a — `read_file()`, `read_string()`             |
| `parser/tokenizer.py`       | v0.2.0b — `tokenize()`                               |
| `parser/populator.py`       | v0.2.0c — `populate()`                               |
| `parser/classifier.py`      | v0.2.1a/b — `classify_document()`                    |
| `parser/section_matcher.py` | v0.2.1c — `match_canonical_sections()`               |
| `parser/metadata.py`        | v0.2.1d — `extract_metadata()`                       |
| `pipeline/stages.py`        | `SingleFileValidator` protocol, `PipelineContext`    |
| `pipeline/per_file.py`      | `PerFileStage`                                       |
| `schema/ecosystem.py`       | `EcosystemFile`                                      |
| `schema/parsed.py`          | All parsed models                                    |
| `schema/classification.py`  | `DocumentClassification`, `DocumentType`, `SizeTier` |
| `schema/enrichment.py`      | `Metadata`                                           |

### 6.1 Limitations

| Limitation                              | Reason                                                     | When Addressed                                    |
| --------------------------------------- | ---------------------------------------------------------- | ------------------------------------------------- |
| `validate()` and `score()` return stubs | Validator (v0.3.x) and scorer (v0.4.x) not yet implemented | v0.3.x, v0.4.x                                    |
| Specimen content may drift              | Real-world sites update their `llms.txt` over time         | Specimens are snapshots; regenerated periodically |
| No performance benchmarks               | v0.2.2 focuses on correctness, not speed                   | v0.5.x if needed                                  |

---

## 7. Sub-Part Specifications

Each sub-part has its own detailed design specification:

- [v0.2.2a — Synthetic Test Fixtures](RR-SPEC-v0.2.2a-synthetic-test-fixtures.md)
- [v0.2.2b — Real-World Specimen Parsing](RR-SPEC-v0.2.2b-real-world-specimen-parsing.md)
- [v0.2.2c — Edge Case Coverage](RR-SPEC-v0.2.2c-edge-case-coverage.md)
- [v0.2.2d — Pipeline Integration](RR-SPEC-v0.2.2d-pipeline-integration.md)
