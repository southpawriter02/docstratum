# v0.1.3 — Sample Data & Test Fixtures: Validation Engine Test Suite (Parent Overview)

> **Phase:** Foundation (v0.1.x)
> **Status:** DRAFT — Realigned to validation-engine pivot (2026-02-06)
> **Parent:** [v0.1.0 — Project Foundation](RR-SPEC-v0.1.0-project-foundation.md)
> **Goal:** Provide a complete set of synthetic Markdown test fixtures at varying conformance levels, plus a pytest-based test infrastructure that validates all 7 schema files from v0.1.2 against known-good and known-bad inputs.
> **Traces to:** FR-001, FR-002, FR-003, FR-004, FR-007, FR-008, FR-011 (v0.0.5a); NFR-010 (≥80% test coverage); DECISION-001, -006, -012, -013, -016 (v0.0.4d)

---

## What Changed from the Original v0.1.3

The original v0.1.3 provided a **single YAML-based `llms.txt` sample file** and a trivial `validate.py` script that loaded it via `yaml.safe_load()`. This was the "generation trap" in miniature — it assumed the input format was YAML, validated against YAML-shaped Pydantic models, and offered no way to test edge cases, partial conformance, or failure modes.

The realigned v0.1.3 provides **five synthetic Markdown test fixtures** at distinct conformance levels, a **pytest infrastructure** (`conftest.py`) with fixture loaders and model factories, and **seven test modules** (one per schema file from v0.1.2). Every fixture is purpose-built to exercise specific diagnostic codes, validation levels, quality dimensions, and anti-patterns identified during the v0.0.x research phase.

**Why five fixtures instead of one?**

The validation engine's value proposition is that it differentiates *between* quality levels — a single "valid" example can't test that. The five fixtures span the quality spectrum observed in the v0.0.2 ecosystem audit:

| Fixture | Archetype | Quality Grade | Validation Level | Research Analog |
|---------|-----------|---------------|------------------|-----------------|
| `gold_standard.md` | Best-in-class | Exemplary (~95) | L4 (DocStratum Extended) | Svelte, Pydantic specimens |
| `partial_conformance.md` | Typical good | Strong (~72) | L2 (Content Quality) | Anthropic, Stripe specimens |
| `minimal_valid.md` | Bare minimum | Needs Work (~35) | L0 (Parseable) | Sparse real-world files |
| `non_conformant.md` | Anti-pattern cluster | Critical (~18) | L0 (fails L1) | Cursor, NVIDIA specimens |
| `type_2_full_excerpt.md` | Documentation dump | N/A (Type 2) | N/A | Vercel AI SDK, llama-stack |

---

## Sub-Parts

This specification was split into two sub-parts for maintainability. Each sub-part is a self-contained document.

| Sub-Part | Title | Scope |
|----------|-------|-------|
| [v0.1.3a](RR-SPEC-v0.1.3a-fixture-suite.md) | Fixture Suite | 5 synthetic Markdown fixtures, fixture architecture, fixture-to-schema expectation matrix |
| [v0.1.3b](RR-SPEC-v0.1.3b-test-infrastructure.md) | Test Infrastructure & Suites | `conftest.py` (fixture loaders + model factories) and 7 test modules (`test_diagnostics.py` through `test_enrichment.py`) |

**Dependency:** v0.1.3a defines the test data; v0.1.3b defines the test code that uses it. Both depend on v0.1.2 (schema files under test).

---

## Fixture Architecture

```
tests/
├── conftest.py                     # Shared fixtures, factories, utilities [v0.1.3b]
├── fixtures/
│   ├── gold_standard.md            # ~95 quality score, L4 conformance   [v0.1.3a]
│   ├── partial_conformance.md      # ~72 quality score, L2 conformance   [v0.1.3a]
│   ├── minimal_valid.md            # ~35 quality score, L0 only          [v0.1.3a]
│   ├── non_conformant.md           # ~18 quality score, fails L1         [v0.1.3a]
│   └── type_2_full_excerpt.md      # Type 2 Full document excerpt        [v0.1.3a]
├── test_diagnostics.py             # DiagnosticCode enum, severity       [v0.1.3b]
├── test_constants.py               # Canonical names, tiers, anti-patterns [v0.1.3b]
├── test_classification.py          # Document type + size tier            [v0.1.3b]
├── test_parsed.py                  # ParsedLlmsTxt model population      [v0.1.3b]
├── test_validation.py              # ValidationResult + ValidationDiagnostic [v0.1.3b]
├── test_quality.py                 # QualityScore + DimensionScore        [v0.1.3b]
└── test_enrichment.py              # Concept, FewShotExample, etc.        [v0.1.3b]
```

---

## Design Decisions Applied

| ID | Decision | How Applied in v0.1.3 |
|----|----------|----------------------|
| DECISION-001 | Markdown over JSON/YAML | All test fixtures are Markdown files, not YAML — matching the validation engine's actual input format |
| DECISION-006 | Pydantic for Validation | conftest.py factories construct Pydantic v2 models; tests validate field constraints and computed properties |
| DECISION-012 | Canonical Section Names | gold_standard.md uses all 11 canonical names in correct order; partial_conformance.md uses aliases; non_conformant.md uses non-canonical names |
| DECISION-013 | Token Budget Tiers | Fixtures span multiple size tiers; type_2_full_generated_content factory produces a file exceeding the 256 KB boundary |
| DECISION-016 | 4-Category Anti-Patterns | non_conformant.md triggers patterns across structural, content, and strategic categories; test_constants.py validates all 22 registry entries |
| NFR-010 | ≥80% Test Coverage | Seven test modules cover all seven schema files; parametrized tests maximize code path coverage |

---

## Exit Criteria

- [ ] All 5 fixture files created in `tests/fixtures/`
- [ ] `conftest.py` defines fixture loaders for all 5 fixtures + generated Type 2 content
- [ ] `conftest.py` defines factory fixtures for all major schema models
- [ ] 7 test modules created (one per schema file from v0.1.2)
- [ ] All tests pass: `pytest tests/ -v` returns 0
- [ ] Test coverage ≥ 80% on `src/docstratum/schema/`: `pytest --cov=src/docstratum/schema tests/`
- [ ] gold_standard.md has H1, blockquote, 9+ canonical sections, links with descriptions, code examples
- [ ] non_conformant.md triggers at least 1 error code and 5+ warning codes
- [ ] type_2_full_generated_content factory produces content > 256 KB
- [ ] No test depends on external network access or file system state outside `tests/`

---

## Traceability Appendix

### Research Artifacts Consumed

| Artifact | What This Spec Uses From It |
|----------|-----------------------------|
| v0.0.1a (Formal Grammar) | ABNF grammar structure → fixture Markdown format; error codes → expected diagnostics per fixture |
| v0.0.2c (Ecosystem Audit) | Specimen archetypes (Svelte, Cursor, NVIDIA) → fixture quality calibration; 55% blockquote compliance → W001 fixture design |
| v0.0.4a (Structural Checks) | 20 structural checks → gold_standard exercising all; E001–E008 → non_conformant triggering subset |
| v0.0.4b (Content Checks) | Quality predictors → fixture content design (code examples, descriptions); gold standard scores → fixture score calibration |
| v0.0.4c (Anti-Patterns) | 22 patterns → non_conformant triggering 5+; CHECK IDs → test_constants validation |
| v0.0.5a (Functional Reqs) | FR-001, FR-002, FR-003, FR-004, FR-007, FR-008, FR-011 → schema model tests |
| v0.0.5b (Non-Functional Reqs) | NFR-010 (≥80% coverage) → test coverage target; NFR-006 (clear CLI errors) → diagnostic message tests |
| v0.1.2 (Schema Definition) | All 7 schema files → all 7 test modules + all factory fixtures in conftest.py |

### FR-to-Test Mapping

| FR ID | Description | Test Coverage |
|-------|------------|---------------|
| FR-001 | Pydantic models for base structure | `test_parsed.py`: ParsedLlmsTxt, ParsedSection, ParsedLink, ParsedBlockquote |
| FR-002 | Extended schema fields | `test_enrichment.py`: Concept, FewShotExample, LLMInstruction, Metadata |
| FR-003 | 5-level validation pipeline | `test_validation.py`: ValidationLevel, ValidationResult.levels_passed |
| FR-004 | Error reporting with line numbers | `test_validation.py`: ValidationDiagnostic.line_number, .context |
| FR-007 | Quality assessment framework | `test_quality.py`: QualityScore, DimensionScore, QualityGrade.from_score() |
| FR-008 | Error code registry | `test_diagnostics.py`: DiagnosticCode (26 codes), severity derivation, message/remediation |
| FR-011 | Schema round-trip serialization | `test_parsed.py`: model construction → property access → re-verification |
