# v0.3.0 — L0 Validation (Parseable Gate)

> **Version:** v0.3.0
> **Document Type:** Design Specification (scope overview with sub-part breakdown)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SCOPE-v0.3.x-validation-engine.md](RR-SCOPE-v0.3.x-validation-engine.md)
> **Depends On:** v0.2.0 (core parser — `ParsedLlmsTxt`), v0.2.1 (enrichment — `DocumentClassification`), v0.1.2a (`DiagnosticCode`, `Severity`), v0.1.2c (`ValidationLevel`, `ValidationDiagnostic`, `ValidationResult`)
> **Consumed By:** v0.3.1 (L1 Structural), v0.3.5 (Pipeline Assembly), v0.4.x (Quality Scoring)

---

## 1. Purpose

v0.3.0 implements the **L0 Parseable Gate** — the first and most critical validation level. L0 is a binary gate: if ANY L0 check emits an ERROR-severity diagnostic, the entire validation pipeline stops. No L1–L3 checks execute. The file's `level_achieved` stays at the failure state and the quality score is capped at 29 (CRITICAL grade) per DS-QS-GATE.

L0 answers one question: **"Can this file be consumed by an LLM at all?"**

### 1.1 User Stories

| ID       | As a...              | I want to...                                                 | So that...                                                     |
| -------- | -------------------- | ------------------------------------------------------------ | -------------------------------------------------------------- |
| US-030-1 | Documentation author | Know immediately if my file cannot be parsed                 | I can fix encoding/format issues before worrying about quality |
| US-030-2 | CI pipeline          | Gate on parseability before running expensive content checks | Failed files fail fast without wasting compute                 |
| US-030-3 | LLM consumer         | Know that a file passing L0 is structurally consumable       | I can trust the file has a coherent identity (H1 title)        |
| US-030-4 | Validator developer  | Have each L0 check isolated and independently testable       | I can reason about and debug individual checks                 |

### 1.2 What L0 Checks

| Sub-Part | Diagnostic Code | Severity | What It Checks                             |
| -------- | --------------- | -------- | ------------------------------------------ |
| v0.3.0a  | E003            | ERROR    | Encoding is valid UTF-8                    |
| v0.3.0b  | E004            | ERROR    | Line endings are LF                        |
| v0.3.0c  | E005            | ERROR    | File contains parseable Markdown structure |
| v0.3.0d  | E007            | ERROR    | File is not empty                          |
| v0.3.0e  | E008            | ERROR    | File does not exceed 100K token hard limit |
| v0.3.0f  | E001, E002      | ERROR    | Exactly one H1 title exists                |
| v0.3.0g  | E006            | ERROR    | Links use valid `[text](url)` syntax       |

---

## 2. Architecture

### 2.1 Module Structure

```
src/docstratum/validation/
├── __init__.py               # Public API: validate()
├── checks/
│   ├── __init__.py
│   ├── l0_encoding.py        # v0.3.0a — E003
│   ├── l0_line_endings.py    # v0.3.0b — E004
│   ├── l0_markdown_parse.py  # v0.3.0c — E005
│   ├── l0_empty_file.py      # v0.3.0d — E007
│   ├── l0_size_limit.py      # v0.3.0e — E008
│   ├── l0_h1_title.py        # v0.3.0f — E001, E002
│   └── l0_link_format.py     # v0.3.0g — E006
└── runner.py                 # Level sequencing (v0.3.5a, stubbed here)
```

### 2.2 Check Interface

Every check follows the same contract:

```python
from docstratum.schema.validation import ValidationDiagnostic


def check(
    parsed: ParsedLlmsTxt,
    classification: DocumentClassification,
    file_meta: FileMetadata,
) -> list[ValidationDiagnostic]:
    """Run this check and return zero or more diagnostics.

    Args:
        parsed: The parsed file model from v0.2.x.
        classification: The document classification from v0.2.1.
        file_meta: File-level metadata (encoding, line endings, byte count).

    Returns:
        Empty list if check passes, or one-or-more diagnostics if check fails.
    """
    ...
```

Each check module exposes a single `check()` function. The runner (v0.3.5a) calls each check and collects the results. This design allows checks to be:

- **Independently testable** — call `check()` with a fixture, assert diagnostics
- **Independently deployable** — add a new check by adding a module
- **Composable** — the runner doesn't know about individual check logic

### 2.3 Precedence Rules

Two precedence rules govern L0 check execution:

1. **E007 > E005:** If the file is empty (E007), do NOT also emit E005 (invalid Markdown). An empty file is a more specific diagnosis.
2. **E001 ⊕ E002:** These are mutually exclusive — a file cannot have both "no H1" and "multiple H1."

These precedences are enforced either within the individual check modules or by the runner during aggregation.

### 2.4 Data Flow

```
ParsedLlmsTxt ─────────┐
DocumentClassification ──┤
FileMetadata ────────────┤
                         ▼
                  ┌──────────────────┐
                  │   L0 Runner      │
                  │                  │
                  │  check_encoding()│──── 0..1 diagnostics
                  │  check_line_end()│──── 0..1 diagnostics
                  │  check_markdown()│──── 0..1 diagnostics
                  │  check_empty()   │──── 0..1 diagnostics
                  │  check_size()    │──── 0..1 diagnostics
                  │  check_h1()      │──── 0..2 diagnostics
                  │  check_links()   │──── 0..N diagnostics
                  │                  │
                  └──────────────────┘
                         │
                         ▼
               list[ValidationDiagnostic]
               (all L0 findings)
```

---

## 3. Sub-Part Breakdown

| Sub-Part                                                | Title                              | Codes              | Planned Tests |
| ------------------------------------------------------- | ---------------------------------- | ------------------ | ------------- |
| [v0.3.0a](RR-SPEC-v0.3.0a-encoding-validation.md)       | Encoding Validation                | E003               | 5             |
| [v0.3.0b](RR-SPEC-v0.3.0b-line-ending-validation.md)    | Line Ending Validation             | E004               | 5             |
| [v0.3.0c](RR-SPEC-v0.3.0c-markdown-parse-validation.md) | Markdown Parse Validation          | E005               | 6             |
| [v0.3.0d](RR-SPEC-v0.3.0d-empty-file-detection.md)      | Empty File Detection               | E007               | 4             |
| [v0.3.0e](RR-SPEC-v0.3.0e-size-limit-enforcement.md)    | Size Limit Enforcement             | E008               | 5             |
| [v0.3.0f](RR-SPEC-v0.3.0f-h1-title-validation.md)       | H1 Title Validation                | E001, E002         | 7             |
| [v0.3.0g](RR-SPEC-v0.3.0g-link-format-validation.md)    | Link Format Validation (Syntactic) | E006               | 8             |
| **Total**                                               |                                    | **7 unique codes** | **40**        |

---

## 4. Workflows

### 4.1 Implementing a Check

```
1. Create src/docstratum/validation/checks/l0_{name}.py
2. Define check() function following the Check Interface (§2.2)
3. Construct ValidationDiagnostic with:
   - code: DiagnosticCode.EXXX
   - severity: Severity.ERROR (all L0 codes are ERROR)
   - message: DiagnosticCode.EXXX.message  (from enum docstring)
   - remediation: DiagnosticCode.EXXX.remediation
   - level: ValidationLevel.L0_PARSEABLE
   - line_number: where applicable
   - check_id: the v0.0.4 check ID (e.g., "ENC-001")
   - context: relevant source snippet (max 500 chars)
4. Write tests in tests/test_validation_l0_{name}.py
5. Register check in runner.py L0_CHECKS list
```

### 4.2 Testing a Check

```
1. Import check function from checks module
2. Create a ParsedLlmsTxt fixture that triggers the check
3. Create a ParsedLlmsTxt fixture that does NOT trigger the check
4. Call check() with each fixture
5. Assert: triggering fixture → returns 1+ diagnostics with correct code
6. Assert: non-triggering fixture → returns empty list
7. Assert: diagnostic fields populated correctly (severity, message, level, etc.)
```

### 4.3 End-to-End L0 Validation

```
1. Parse file using v0.2.0 parse_file()
2. Pass ParsedLlmsTxt + DocumentClassification + FileMetadata to L0 runner
3. L0 runner executes all 7 checks
4. L0 runner applies precedence rules (E007 > E005)
5. If any ERROR diagnostic → levels_passed[L0] = False → stop
6. If no errors → levels_passed[L0] = True → proceed to L1
```

---

## 5. Acceptance Criteria

### 5.1 Functional

- [ ] All 7 check modules exist in `src/docstratum/validation/checks/`.
- [ ] Each check module exposes a `check()` function matching the interface in §2.2.
- [ ] E003 emitted for non-UTF-8 files.
- [ ] E004 emitted for non-LF line endings.
- [ ] E005 emitted for unparseable content (non-empty, no Markdown structure).
- [ ] E007 emitted for empty/whitespace-only files.
- [ ] E008 emitted for files exceeding 100K tokens.
- [ ] E001 emitted when no H1 title exists.
- [ ] E002 emitted when multiple H1 titles exist.
- [ ] E001 and E002 are mutually exclusive.
- [ ] E006 emitted for each link with malformed/empty URL.
- [ ] E007 takes precedence over E005 (empty file does not also emit "invalid Markdown").
- [ ] All diagnostics include `code`, `severity`, `message`, `remediation`, `level`, `check_id`.
- [ ] `line_number` populated for all diagnostics where a specific source line is identifiable.

### 5.2 Non-Functional

- [ ] `pytest --cov=docstratum.validation --cov-fail-under=85` passes.
- [ ] `black --check` and `ruff check` pass on all new code.
- [ ] Google-style docstrings on all modules, classes, and functions.
- [ ] Each module references "Implements v0.3.0x" in its docstring.

### 5.3 CHANGELOG Entry Template

```markdown
## [0.3.0] - YYYY-MM-DD

**L0 Validation — Parseable Gate for the validation engine.**

### Added

#### Validation Infrastructure (`src/docstratum/validation/`)

- Check interface: `check(parsed, classification, file_meta) -> list[ValidationDiagnostic]` — uniform contract for all validation checks

#### L0 Checks (`src/docstratum/validation/checks/`)

- E003 encoding validation: rejects non-UTF-8 files (v0.3.0a)
- E004 line ending validation: rejects non-LF line endings (v0.3.0b)
- E005 markdown parse validation: rejects files with no parseable structure (v0.3.0c)
- E007 empty file detection: rejects empty/whitespace-only files, with E007>E005 precedence (v0.3.0d)
- E008 size limit enforcement: rejects files exceeding 100K tokens (v0.3.0e)
- E001/E002 H1 title validation: requires exactly one H1 heading (v0.3.0f)
- E006 link format validation: detects syntactically malformed `[text](url)` links (v0.3.0g)
```

---

## 6. Dependencies

| Module                     | What v0.3.0 Uses                                              |
| -------------------------- | ------------------------------------------------------------- |
| `schema/diagnostics.py`    | `DiagnosticCode` enum (E001–E008), `Severity` enum            |
| `schema/validation.py`     | `ValidationLevel`, `ValidationDiagnostic`, `ValidationResult` |
| `schema/parsed.py`         | `ParsedLlmsTxt`, `ParsedSection`, `ParsedLink`                |
| `schema/classification.py` | `DocumentClassification`                                      |
| `schema/constants.py`      | `TOKEN_ZONES["DEGRADATION"]` (100K threshold)                 |
| `parser/io.py`             | `FileMetadata` (encoding, line_ending_style, has_null_bytes)  |

### 6.1 FileMetadata Dependency

The L0 checks consume a `FileMetadata` instance produced by v0.2.0a (`parser/io.py`). This model contains:

| Field               | Type   | Used By                |
| ------------------- | ------ | ---------------------- |
| `encoding`          | `str`  | v0.3.0a (E003)         |
| `line_ending_style` | `str`  | v0.3.0b (E004)         |
| `byte_count`        | `int`  | — (informational)      |
| `has_null_bytes`    | `bool` | v0.3.0a (E003 context) |

> **Note:** `FileMetadata` is defined by v0.2.0a and is NOT a Pydantic model in the schema package — it's a parser-internal dataclass. The validator receives it as a parameter.

### 6.2 Limitations

| Limitation                         | Reason                                                            | When Addressed       |
| ---------------------------------- | ----------------------------------------------------------------- | -------------------- |
| No level sequencing                | v0.3.0 only implements L0; the runner is not yet wired            | v0.3.5a              |
| No `ValidationResult` assembly     | Individual checks return diagnostic lists; aggregation is v0.3.5b | v0.3.5b              |
| E006 is syntactic only             | URL reachability (HTTP resolution) is v0.3.2b                     | v0.3.2b              |
| No anti-pattern detection          | Anti-patterns aggregate across levels; v0.3.0 only runs L0        | v0.3.4               |
| `FileMetadata` not yet implemented | v0.2.0a hasn't been built yet                                     | v0.2.0a (dependency) |

---

## 7. Design Decisions

| Decision                              | Choice | Rationale                                                                   |
| ------------------------------------- | ------ | --------------------------------------------------------------------------- |
| One module per check                  | Yes    | Isolation, testability, discoverability                                     |
| Uniform `check()` interface           | Yes    | Composability — runner doesn't know check internals                         |
| All L0 codes are ERROR                | Yes    | L0 is a gate; warnings would not block pipeline                             |
| E007 > E005 precedence                | Yes    | "Empty file" is more specific than "invalid Markdown"                       |
| E001 ⊕ E002 mutual exclusion          | Yes    | Logically impossible to have both                                           |
| `line_number` optional in diagnostics | Yes    | File-level checks (encoding, empty) have no specific line                   |
| `check_id` maps to v0.0.4 check IDs   | Yes    | Traceability to research documents                                          |
| Checks receive all 3 inputs           | Yes    | Some checks need only `parsed`, but uniform signature avoids special-casing |

---

## 8. Sub-Part Specifications

- [v0.3.0a — Encoding Validation](RR-SPEC-v0.3.0a-encoding-validation.md)
- [v0.3.0b — Line Ending Validation](RR-SPEC-v0.3.0b-line-ending-validation.md)
- [v0.3.0c — Markdown Parse Validation](RR-SPEC-v0.3.0c-markdown-parse-validation.md)
- [v0.3.0d — Empty File Detection](RR-SPEC-v0.3.0d-empty-file-detection.md)
- [v0.3.0e — Size Limit Enforcement](RR-SPEC-v0.3.0e-size-limit-enforcement.md)
- [v0.3.0f — H1 Title Validation](RR-SPEC-v0.3.0f-h1-title-validation.md)
- [v0.3.0g — Link Format Validation](RR-SPEC-v0.3.0g-link-format-validation.md)
