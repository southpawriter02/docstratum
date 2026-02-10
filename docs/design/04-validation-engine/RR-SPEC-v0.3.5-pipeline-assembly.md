# v0.3.5 — Validation Pipeline Assembly

> **Version:** v0.3.5
> **Document Type:** Design Specification (scope overview with sub-part breakdown)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SCOPE-v0.3.x-validation-engine.md](../RR-SCOPE-v0.3.x-validation-engine.md)
> **Depends On:** v0.3.0–v0.3.4 (all checks + anti-pattern detection), v0.1.2c (`ValidationResult`, `ValidationDiagnostic`, `ValidationLevel`)
> **Consumed By:** v0.4.x (Quality Scoring), v0.6.x (Remediation), v0.7.x (Ecosystem Integration)

---

## 1. Purpose

v0.3.5 is the **integration layer** — it wires all individual checks (v0.3.0–v0.3.3) and anti-pattern detection (v0.3.4) into a sequential pipeline that produces a complete `ValidationResult`. This is where the validation engine becomes usable as a single function call: `validate_file(path) → ValidationResult`.

### 1.1 What v0.3.5 Adds

| Before v0.3.5                                           | After v0.3.5                                          |
| ------------------------------------------------------- | ----------------------------------------------------- |
| 18+ individual check functions scattered across modules | `validate_file()` → complete `ValidationResult`       |
| Manual orchestration required                           | Automatic L0→L1→L2→L3 sequencing with gate-on-failure |
| Diagnostics collected per-check                         | All diagnostics aggregated into single list           |
| Anti-pattern detection not wired in                     | Runs automatically after level checks                 |
| No validation level determination                       | `level_achieved` correctly computed                   |
| No regression tests against real files                  | 6 calibration specimens verified                      |

### 1.2 User Stories

| ID       | As a...              | I want to...                                                     | So that...                                               |
| -------- | -------------------- | ---------------------------------------------------------------- | -------------------------------------------------------- |
| US-035-1 | CLI user             | Call `validate_file("llms.txt")` and get a complete result       | I can validate any file with one function call           |
| US-035-2 | Scorer               | Receive a `ValidationResult` with all diagnostics aggregated     | I can compute quality scores                             |
| US-035-3 | CI pipeline          | Know the `level_achieved` for a file                             | I can gate releases on validation level                  |
| US-035-4 | Documentation author | See gate behavior (L0 fail → no further checks)                  | I fix parse errors before worrying about content quality |
| US-035-5 | Developer            | Trust that the pipeline produces correct results for known files | Calibration specimens serve as regression tests          |
| US-035-6 | QA                   | Verify ≥85% test coverage on the validation module               | I can trust the implementation                           |

---

## 2. Architecture

### 2.1 Module Structure

```
src/docstratum/validation/
├── __init__.py             # Public API: validate_file()
├── pipeline.py             # v0.3.5a — Level sequencing & gating
├── aggregator.py           # v0.3.5b — Diagnostic aggregation
├── checks/                 # v0.3.0–v0.3.3 (existing)
│   ├── l0_*.py
│   ├── l1_*.py
│   ├── l2_*.py
│   └── l3_*.py
└── anti_patterns/          # v0.3.4 (existing)
    ├── detector.py
    ├── critical.py
    ├── structural.py
    ├── content.py
    └── strategic.py

tests/validation/
├── test_pipeline.py        # v0.3.5a — Sequencing tests
├── test_aggregator.py      # v0.3.5b — Aggregation tests
├── test_gate_behavior.py   # v0.3.5c — Cross-level gate tests
├── test_diagnostic_completeness.py  # v0.3.5c — Field completeness
├── test_calibration.py     # v0.3.5d — Specimen regression tests
├── checks/                 # Per-check tests (existing)
└── anti_patterns/          # Anti-pattern tests (existing)
```

### 2.2 Execution Flow

```
validate_file(path: str | Path, check_urls: bool = False)
    │
    ├── 1. Load and parse (v0.2.0)
    │     └── parsed, classification, file_meta = parse_file(path)
    │
    ├── 2. L0 checks (v0.3.0a–g)
    │     └── all_l0_diagnostics = run_level_checks(L0, parsed, ...)
    │           │
    │           ├── ANY ERROR? → levels_passed[L0] = False
    │           │                 SKIP L1, L2, L3
    │           │                 JUMP to step 6 (anti-patterns)
    │           │
    │           └── No errors → levels_passed[L0] = True
    │
    ├── 3. L1 checks (v0.3.1a–d)
    │     └── all_l1_diagnostics = run_level_checks(L1, parsed, ...)
    │           │
    │           ├── ANY ERROR? → levels_passed[L1] = False
    │           │                 SKIP L2, L3
    │           │
    │           └── No errors → levels_passed[L1] = True
    │
    ├── 4. L2 checks (v0.3.2a–d)
    │     └── all_l2_diagnostics = run_level_checks(L2, parsed, ...)
    │           │
    │           ├── ANY ERROR? → levels_passed[L2] = False
    │           │                 SKIP L3
    │           │
    │           └── No errors → levels_passed[L2] = True
    │
    ├── 5. L3 checks (v0.3.3a–e)
    │     └── all_l3_diagnostics = run_level_checks(L3, parsed, ...)
    │           └── levels_passed[L3] = True (always — L3 has no ERRORs)
    │
    ├── 6. Anti-pattern detection (v0.3.4a–d)
    │     └── anti_patterns = detect_all(accumulated_diagnostics, parsed)
    │
    └── 7. Aggregate (v0.3.5b)
          └── result = aggregate(
                  diagnostics, levels_passed, anti_patterns,
                  source_filename, validated_at
              )
              return result  → ValidationResult
```

### 2.3 Check Registry

The pipeline needs a registry mapping levels to their check functions:

```python
CHECK_REGISTRY: dict[ValidationLevel, list[CheckFunction]] = {
    ValidationLevel.L0_PARSEABLE: [
        l0_encoding.check_encoding,
        l0_line_endings.check_line_endings,
        l0_markdown_parse.check_markdown_parse,
        l0_empty_file.check_empty_file,
        l0_size_limit.check_size_limit,
        l0_h1_title.check_h1_title,
        l0_link_format.check_link_format,
    ],
    ValidationLevel.L1_STRUCTURAL: [
        l1_blockquote.check_blockquote,
        l1_section_names.check_section_names,
        l1_link_presence.check_link_presence,
        l1_section_structure.check_section_structure,
    ],
    ValidationLevel.L2_CONTENT: [
        l2_description_quality.check_description_quality,
        l2_url_validation.check_url_validation,
        l2_section_content.check_section_content,
        l2_blockquote_quality.check_blockquote_quality,
    ],
    ValidationLevel.L3_BEST_PRACTICES: [
        l3_canonical_names.check_canonical_names,
        l3_master_index.check_master_index,
        l3_code_examples.check_code_examples,
        l3_token_budget_version.check_token_budget_and_version,
        l3_structural_practices.check_structural_practices,
    ],
}
```

---

## 3. Sub-Part Breakdown

| Sub-Part                                             | Title                           | Primary Output                         |
| ---------------------------------------------------- | ------------------------------- | -------------------------------------- |
| [v0.3.5a](RR-SPEC-v0.3.5a-level-sequencing.md)       | Level Sequencing & Gating       | `validate_file()` with gate-on-failure |
| [v0.3.5b](RR-SPEC-v0.3.5b-diagnostic-aggregation.md) | Diagnostic Aggregation          | Fully populated `ValidationResult`     |
| [v0.3.5c](RR-SPEC-v0.3.5c-validation-unit-tests.md)  | Validation Unit Tests           | ≥85% coverage, gate behavior tests     |
| [v0.3.5d](RR-SPEC-v0.3.5d-calibration-specimens.md)  | Calibration Specimen Validation | 6 regression tests                     |

---

## 4. Acceptance Criteria

### 4.1 Functional

- [ ] `validate_file(path)` exists and returns `ValidationResult`.
- [ ] L0 failure prevents L1–L3 execution.
- [ ] L1 failure prevents L2–L3 execution.
- [ ] L2 failure prevents L3 execution.
- [ ] WARNING diagnostics do NOT block level progression.
- [ ] Anti-pattern detection runs after all level checks.
- [ ] `level_achieved` correctly reflects highest passed level.
- [ ] `levels_passed` dict correctly populated for each level.
- [ ] `validated_at` and `source_filename` populated.
- [ ] All diagnostics from all levels aggregated in single list.
- [ ] 6 calibration specimens produce expected `level_achieved`.

### 4.2 Non-Functional

- [ ] `pytest --cov=docstratum.validation --cov-fail-under=85` passes.
- [ ] `black --check` and `ruff check` pass.
- [ ] Google-style docstrings; modules reference "Implements v0.3.5x."

### 4.3 CHANGELOG Entry Template

```markdown
## [0.3.5] - YYYY-MM-DD

**Validation Pipeline Assembly — wires L0–L3 checks and anti-pattern detection into a sequential pipeline.**

### Added

#### Pipeline (`src/docstratum/validation/`)

- `validate_file()` public API — single entry point for file validation
- Level sequencing with gate-on-failure (L0 fail → skip L1–L3)
- Diagnostic aggregation into `ValidationResult`
- Anti-pattern detection (v0.3.4) wired as post-hoc step
- Check registry mapping levels to check functions
- 85%+ test coverage on validation module
- 6 calibration specimen regression tests (DS-CS-001–006)
```

---

## 5. Dependencies

| Module                                  | What v0.3.5 Uses                                              |
| --------------------------------------- | ------------------------------------------------------------- |
| `validation/checks/l0_*.py` – `l3_*.py` | All check functions (v0.3.0–v0.3.3)                           |
| `validation/anti_patterns/detector.py`  | `AntiPatternDetector.detect_all()` (v0.3.4)                   |
| `schema/validation.py`                  | `ValidationResult`, `ValidationDiagnostic`, `ValidationLevel` |
| `schema/parsed.py`                      | `ParsedLlmsTxt`, input to all checks                          |
| `schema/classification.py`              | `DocumentClassification`, input to checks                     |
| `parser/`                               | `parse_file()` (v0.2.0), produces `ParsedLlmsTxt`             |
| `tests/fixtures/calibration/`           | 6 gold standard specimen files (DS-CS-001–006)                |

### 5.1 Limitations

| Limitation                             | Reason                           | When Addressed |
| -------------------------------------- | -------------------------------- | -------------- |
| No L4 checks                           | L4 is out of v0.3.x scope        | v0.9.0         |
| No quality score                       | Scoring is v0.4.x                | v0.4.0         |
| No output formatting                   | CLI/JSON output is v0.8.x        | v0.8.0         |
| `check_urls` passed through to L2 only | Only v0.3.2b uses this parameter | By design      |

---

## 6. Design Decisions

| Decision                                      | Choice                                    | Rationale                                                                           |
| --------------------------------------------- | ----------------------------------------- | ----------------------------------------------------------------------------------- |
| Single `validate_file()` entry point          | Yes                                       | Consumers should not need to know about individual check functions                  |
| Check registry (dict of level→functions)      | Yes                                       | Extensible — add L4 checks later without modifying pipeline logic                   |
| Anti-patterns run regardless of gate failures | Partial: v0.3.4a runs even on L0 failures | Critical anti-patterns (Ghost File, Encoding Disaster) are detectable from L0 alone |
| `check_urls=False` default                    | Yes                                       | URL checking is opt-in at the pipeline level, passed through to L2                  |
| Calibration specimens as regression tests     | Yes                                       | Ensures pipeline correctness against known-quality files                            |
| 85% coverage target                           | Per project standard                      | `RR-META-testing-standards`                                                         |

---

## 7. Sub-Part Specifications

- [v0.3.5a — Level Sequencing & Gating](RR-SPEC-v0.3.5a-level-sequencing.md)
- [v0.3.5b — Diagnostic Aggregation](RR-SPEC-v0.3.5b-diagnostic-aggregation.md)
- [v0.3.5c — Validation Unit Tests](RR-SPEC-v0.3.5c-validation-unit-tests.md)
- [v0.3.5d — Calibration Specimen Validation](RR-SPEC-v0.3.5d-calibration-specimens.md)
