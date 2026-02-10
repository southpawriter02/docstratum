# v0.3.1 — L1 Validation (Structural)

> **Version:** v0.3.1
> **Document Type:** Design Specification (scope overview with sub-part breakdown)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SCOPE-v0.3.x-validation-engine.md](RR-SCOPE-v0.3.x-validation-engine.md)
> **Depends On:** v0.3.0 (L0 Parseable Gate — must pass before L1 runs), v0.2.1c (canonical section matching)
> **Consumed By:** v0.3.2 (L2 Content Quality), v0.3.4b (Structural Anti-Patterns), v0.3.5 (Pipeline Assembly)

---

## 1. Purpose

v0.3.1 implements the **L1 Structural Validation** level — the second tier of the validation pipeline. L1 verifies that the file follows the structural conventions of the `llms.txt` specification beyond bare parseability: does it have a description blockquote? Do its sections use recognized names? Is the heading hierarchy valid? Do links have proper text?

### 1.1 Key Property: Mostly WARNINGs, One ERROR

Three of four L1 checks emit **WARNING**-severity diagnostics (W001, W002, W019, W020). However, v0.3.1d emits **E006** (ERROR) for links with empty text — a HARD structural failure per DS-VC-STR-005.

> **WARNINGs do NOT block level progression.** A file that triggers W001, W002, W019, W020 still passes L1 and proceeds to L2. But **E006 at L1 blocks progression** — a file with empty-text links fails L1.

L1 "passes" as long as no ERROR-severity diagnostics are emitted at L1. Most files pass L1 since empty-text links are rare, but the gate is no longer unconditional. The WARNINGs are quality observations that impact the downstream quality score (v0.4.x) and feed anti-pattern detection (v0.3.4b), but they do not gate pipeline progression.

### 1.2 User Stories

| ID       | As a...              | I want to...                                                         | So that...                                          |
| -------- | -------------------- | -------------------------------------------------------------------- | --------------------------------------------------- |
| US-031-1 | Documentation author | Know if my blockquote description is missing                         | I can add it to improve LLM comprehension           |
| US-031-2 | Documentation author | Know which section names are non-canonical                           | I can rename them to match the recommended standard |
| US-031-3 | Validator developer  | Have structural checks only fire after L0 passes                     | I can rely on `parsed.title` being non-None         |
| US-031-4 | Scorer               | Read W001/W002/W019/W020 diagnostics to compute structural dimension | I can deduct points for missing conventions         |
| US-031-5 | Documentation author | Know if my heading hierarchy uses H3+ where H2 is expected           | I can fix the heading levels                        |
| US-031-6 | Documentation author | Know if any links have empty text                                    | I can add meaningful link labels                    |

---

## 2. Architecture

### 2.1 Module Structure

```
src/docstratum/validation/checks/
├── l0_encoding.py          # v0.3.0a
├── l0_line_endings.py      # v0.3.0b
├── l0_markdown_parse.py    # v0.3.0c
├── l0_empty_file.py        # v0.3.0d
├── l0_size_limit.py        # v0.3.0e
├── l0_h1_title.py          # v0.3.0f
├── l0_link_format.py       # v0.3.0g
├── l1_blockquote.py        # v0.3.1a — NEW
├── l1_section_names.py     # v0.3.1b — NEW
├── l1_section_structure.py # v0.3.1c — NEW
└── l1_link_format.py       # v0.3.1d — NEW
```

### 2.2 Check Interface

Both checks follow the same uniform interface established in v0.3.0:

```python
def check(
    parsed: ParsedLlmsTxt,
    classification: DocumentClassification,
    file_meta: FileMetadata,
) -> list[ValidationDiagnostic]:
```

### 2.3 Gate Behavior

```
L0 checks (v0.3.0a–g)
    │
    ├── ANY L0 ERROR? ──── Yes ──→ STOP. L0 failed. Skip L1–L3.
    │                                     levels_passed[L0] = False
    └── No ──→ L0 passed. Run L1 checks.
                  │
                  ├── v0.3.1a: check blockquote → 0..1 W001
                  ├── v0.3.1b: check section names → 0..N W002
                  ├── v0.3.1c: check H2 structure / orphan H3+ → 0..1 W019, 0..N W020
                  ├── v0.3.1d: check link text → 0..N E006
                  │
                  └── ANY L1 ERROR? ──── Possible! (v0.3.1d emits E006 ERROR)
                                         ├── Yes → levels_passed[L1] = False
                                         │         WARNINGs still recorded.
                                         │         L2–L3 skipped.
                                         └── No  → levels_passed[L1] = True
                                                   Proceed to L2.
```

> v0.3.1d introduces E006 (ERROR) at L1 for links with empty text. This means L1 is **no longer unconditionally permissive**. Most files pass (empty-text links are rare), but the gate is live. All WARNINGs (W001, W002, W019, W020) are always recorded regardless of L1 pass/fail.

### 2.4 Data Flow

```
ParsedLlmsTxt.blockquote ──────────────── v0.3.1a ──── 0..1 W001
ParsedLlmsTxt.sections[].canonical_name ── v0.3.1b ──── 0..N W002
ParsedLlmsTxt.sections (count) ──────────── v0.3.1c ──── 0..1 W019
ParsedLlmsTxt.raw_content (headings) ────── v0.3.1c ──── 0..N W020
ParsedLlmsTxt.sections[].links[].title ──── v0.3.1d ──── 0..N E006
```

---

## 3. Sub-Part Breakdown

| Sub-Part                                                   | Title                   | Code(s)     | Severity | Criterion         | Planned Tests |
| ---------------------------------------------------------- | ----------------------- | ----------- | -------- | ----------------- | ------------- |
| [v0.3.1a](RR-SPEC-v0.3.1a-blockquote-presence.md)          | Blockquote Presence     | W001        | WARNING  | DS-VC-STR-003     | 4             |
| [v0.3.1b](RR-SPEC-v0.3.1b-section-name-validation.md)      | Section Name Validation | W002        | WARNING  | DS-VC-STR-008     | 9             |
| [v0.3.1c](RR-SPEC-v0.3.1c-section-structure-validation.md) | Section Structure       | W019, W020  | WARNING  | DS-VC-STR-004/006 | 9             |
| [v0.3.1d](RR-SPEC-v0.3.1d-link-format-compliance.md)       | Link Format Compliance  | E006        | ERROR    | DS-VC-STR-005     | 9             |
| **Total**                                                  |                         | **5 codes** |          |                   | **31**        |

---

## 4. Workflows

### 4.1 Implementing an L1 Check

```
1. Create src/docstratum/validation/checks/l1_{name}.py
2. Define check() function following the Check Interface
3. Construct ValidationDiagnostic with:
   - code: DiagnosticCode.WXXX or EXXX
   - severity: Severity.WARNING or ERROR (v0.3.1d uses ERROR)
   - level: ValidationLevel.L1_STRUCTURAL
   - all standard fields (message, remediation, check_id, etc.)
4. Write tests in tests/test_validation_l1_{name}.py
5. Register check in runner.py L1_CHECKS list
```

### 4.2 Testing L1 Checks

```
1. Create ParsedLlmsTxt fixture WITH blockquote → W001 not emitted
2. Create ParsedLlmsTxt fixture WITHOUT blockquote → W001 emitted
3. Create ParsedLlmsTxt with canonical section names → W002 not emitted
4. Create ParsedLlmsTxt with non-canonical names → W002 emitted
5. Verify all WARNING diagnostics have correct fields
6. Verify WARNINGs do NOT appear in errors list (only in warnings list)
```

---

## 5. Acceptance Criteria

### 5.1 Functional

- [ ] All four check modules exist in `src/docstratum/validation/checks/`.
- [ ] W001 emitted when `parsed.blockquote is None`.
- [ ] W002 emitted per section where `canonical_name is None`.
- [ ] W019 emitted when `parsed.sections` is empty.
- [ ] W020 emitted per orphan H3+ heading.
- [ ] E006 emitted per link with empty/whitespace-only text.
- [ ] W001/W002/W019/W020 use `severity=WARNING`, `level=L1_STRUCTURAL`.
- [ ] E006 uses `severity=ERROR`, `level=L1_STRUCTURAL`.
- [ ] L1 checks only run when L0 has passed (no ERROR diagnostics at L0).
- [ ] L1 passes when no E006 emitted — `levels_passed[L1] = True`.
- [ ] L1 fails when any E006 emitted — `levels_passed[L1] = False`. WARNINGs still recorded.
- [ ] All diagnostics include `code`, `severity`, `message`, `remediation`, `level`, `check_id`.

### 5.2 Non-Functional

- [ ] `pytest --cov=docstratum.validation --cov-fail-under=85` passes.
- [ ] `black --check` and `ruff check` pass.
- [ ] Google-style docstrings; modules reference "Implements v0.3.1x".

### 5.3 CHANGELOG Entry Template

```markdown
## [0.3.1] - YYYY-MM-DD

**L1 Validation — Structural checks for blockquote, section naming, heading hierarchy, and link format.**

### Added

#### L1 Checks (`src/docstratum/validation/checks/`)

- W001 blockquote presence: warns when blockquote description is missing after H1 (v0.3.1a)
- W002 section name validation: warns per section with non-canonical name (v0.3.1b)
- W019 no H2 sections: warns when file has no navigable section structure (v0.3.1c)
- W020 heading level violation: warns per H3+ heading used as top-level section divider (v0.3.1c)
- E006 link format compliance: errors per link with empty text component (v0.3.1d)

#### New Diagnostic Codes (`src/docstratum/schema/diagnostics.py`)

- W019_NO_H2_SECTIONS — DS-VC-STR-004 criterion
- W020_HEADING_LEVEL_VIOLATION — DS-VC-STR-006 criterion
```

---

## 6. Dependencies

| Module                  | What v0.3.1 Uses                                                                                                                                     |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `schema/parsed.py`      | `ParsedLlmsTxt.blockquote`, `ParsedSection.canonical_name`, `ParsedSection.name`, `ParsedLink.title`, `raw_content`                                  |
| `schema/diagnostics.py` | `W001_MISSING_BLOCKQUOTE`, `W002_NON_CANONICAL_SECTION_NAME`, `W019_NO_H2_SECTIONS` (NEW), `W020_HEADING_LEVEL_VIOLATION` (NEW), `E006_BROKEN_LINKS` |
| `schema/validation.py`  | `ValidationDiagnostic`, `ValidationLevel.L1_STRUCTURAL`                                                                                              |
| `schema/constants.py`   | `CanonicalSectionName` (11 names), `SECTION_NAME_ALIASES` (32 aliases)                                                                               |

### 6.1 Limitations

| Limitation                                     | Reason                                               | When Addressed                |
| ---------------------------------------------- | ---------------------------------------------------- | ----------------------------- |
| No fuzzy matching for section name suggestions | Scope defers this as NICE-TO-HAVE                    | Potentially v0.3.1b or v0.5.x |
| WARNINGs don't gate                            | L1 WARNINGs are permissive by design                 | By design (never gated)       |
| E006 can block L1                              | v0.3.1d introduces ERROR severity at L1              | By design (HARD criterion)    |
| No duplicate canonical name detection          | Same canonical name appearing twice is AP-STRUCT-003 | v0.3.4b                       |
| Bare URLs not detected                         | Parser only extracts [text](url) links               | v0.3.4a (Link Desert AP)      |

---

## 7. Design Decisions

| Decision                                  | Choice | Rationale                                                                                                                            |
| ----------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| WARNING for W001/W002/W019/W020           | Yes    | Research shows 55% blockquote compliance. Non-canonical names, missing H2s, orphan H3s are quality signals, not structural failures. |
| ERROR for E006 at L1                      | Yes    | DS-VC-STR-005 is HARD: empty link text breaks navigability. Links are useless without text.                                          |
| L1 gate is live (not unconditional)       | Yes    | v0.3.1d E006 can block. Most files pass — empty-text links are rare.                                                                 |
| W002 emitted per section                  | Yes    | Each non-canonical section is independently diagnosable with its own line number and context.                                        |
| W019/W020 in same check module            | Yes    | DS-VC-STR-004 and STR-006 are complementary (H2 exists / H3+ not misused). Natural code pairing.                                     |
| Canonical name list in diagnostic context | Yes    | Helps authors fix the name without looking up documentation.                                                                         |
| New codes W019/W020                       | Yes    | STR-004 and STR-006 previously had no diagnostic codes — implicit scoring is opaque.                                                 |

---

## 8. Sub-Part Specifications

- [v0.3.1a — Blockquote Presence](RR-SPEC-v0.3.1a-blockquote-presence.md)
- [v0.3.1b — Section Name Validation](RR-SPEC-v0.3.1b-section-name-validation.md)
- [v0.3.1c — Section Structure Validation](RR-SPEC-v0.3.1c-section-structure-validation.md)
- [v0.3.1d — Link Format Compliance](RR-SPEC-v0.3.1d-link-format-compliance.md)
