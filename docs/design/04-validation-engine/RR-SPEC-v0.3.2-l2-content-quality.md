# v0.3.2 — L2 Validation (Content Quality)

> **Version:** v0.3.2
> **Document Type:** Design Specification (scope overview with sub-part breakdown)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SCOPE-v0.3.x-validation-engine.md](../RR-SCOPE-v0.3.x-validation-engine.md)
> **Depends On:** v0.3.1 (L1 Structural — must pass before L2 runs), v0.2.0 (`ParsedLlmsTxt`, `ParsedLink`, `ParsedSection`)
> **Consumed By:** v0.3.3 (L3 Best Practices), v0.3.4 (Anti-Pattern Detection), v0.3.5 (Pipeline Assembly)

---

## 1. Purpose

v0.3.2 implements the **L2 Content Quality** level — the third tier of the validation pipeline. L2 verifies that the documentation content is _meaningful and useful_, not just structurally present. While L0 ensures parseability and L1 ensures structural conventions, L2 asks: are the links described? Are the URLs resolvable? Are the sections populated? Is the blockquote substantive?

### 1.1 Key Property: Mixed Severities

L2 introduces a mix of diagnostic severities:

| Severity    | Codes                   | Gate Impact                   |
| ----------- | ----------------------- | ----------------------------- |
| **ERROR**   | E006 (URL reachability) | Can block L2 → L3 progression |
| **WARNING** | W003, W006, W011        | Does NOT block progression    |
| **INFO**    | I004, I005              | Does NOT block progression    |

> **L2 gate behavior:** L2 passes if no ERROR-severity diagnostics are emitted at L2. Since URL reachability (v0.3.2b) is the only ERROR-severity check and it is **gated behind a configuration flag** (`check_urls`, default `false`), **L2 effectively always passes in default configuration**. When `check_urls=true`, unreachable URLs block progression.

### 1.2 User Stories

| ID       | As a...              | I want to...                                                           | So that...                                        |
| -------- | -------------------- | ---------------------------------------------------------------------- | ------------------------------------------------- |
| US-032-1 | Documentation author | Know which links lack descriptions                                     | I can add context for readers and AI agents       |
| US-032-2 | Documentation author | Know which URLs are broken or unreachable                              | I can fix or remove dead links                    |
| US-032-3 | Documentation author | Know which sections are empty or contain placeholder text              | I can fill in missing content                     |
| US-032-4 | Documentation author | Know if my blockquote is too short or just repeats the title           | I can write a more meaningful project description |
| US-032-5 | Documentation author | Know if link descriptions follow formulaic patterns                    | I can rewrite them to be distinctive and useful   |
| US-032-6 | Validator developer  | Have content checks only fire after L1 passes                          | I can rely on structural parsing being sound      |
| US-032-7 | Scorer               | Read W003/W006/W011/I004/I005 diagnostics to compute content dimension | I can score content quality accurately            |
| US-032-8 | CI pipeline          | Optionally enable URL checking via a flag                              | I can balance speed vs thoroughness               |

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
├── l1_blockquote.py        # v0.3.1a
├── l1_section_names.py     # v0.3.1b
├── l1_section_structure.py # v0.3.1c
├── l1_link_format.py       # v0.3.1d
├── l2_description_quality.py   # v0.3.2a — NEW
├── l2_url_validation.py        # v0.3.2b — NEW
├── l2_section_content.py       # v0.3.2c — NEW
└── l2_blockquote_quality.py    # v0.3.2d — NEW
```

### 2.2 Check Interface

All checks follow the uniform interface established in v0.3.0. v0.3.2b additionally requires a configuration parameter:

```python
# Standard interface (v0.3.2a, v0.3.2c, v0.3.2d)
def check(
    parsed: ParsedLlmsTxt,
    classification: DocumentClassification,
    file_meta: FileMetadata,
) -> list[ValidationDiagnostic]:

# Extended interface (v0.3.2b only)
def check(
    parsed: ParsedLlmsTxt,
    classification: DocumentClassification,
    file_meta: FileMetadata,
    *,
    check_urls: bool = False,
    url_timeout: float = 5.0,
) -> list[ValidationDiagnostic]:
```

> [!IMPORTANT]
> v0.3.2b breaks the uniform check interface by adding keyword-only parameters. The v0.3.5a pipeline runner must handle this by passing configuration arguments specifically to the URL validation check. All other checks maintain the standard 3-argument signature.

### 2.3 Gate Behavior

```
L1 checks (v0.3.1a–d)
    │
    ├── ANY L1 ERROR? ──── Yes ──→ STOP. L1 failed. Skip L2–L3.
    │                                     levels_passed[L1] = False
    └── No ──→ L1 passed. Run L2 checks.
                  │
                  ├── v0.3.2a: description quality → 0..N W003
                  ├── v0.3.2b: URL validation → 0..N E006  (if check_urls=true)
                  │                              → 0 diagnostics (if check_urls=false, DEFAULT)
                  ├── v0.3.2c: section content → 0..N W011, 0..N W006, 0..1 I004, 0..1 I005
                  ├── v0.3.2d: blockquote quality → 0..1 W012
                  │
                  └── ANY L2 ERROR? ──── Possible! (v0.3.2b E006 when check_urls=true)
                                         ├── Yes → levels_passed[L2] = False
                                         │         WARNINGs/INFOs still recorded.
                                         │         L3 skipped.
                                         └── No  → levels_passed[L2] = True
                                                   Proceed to L3.
```

> In **default configuration** (`check_urls=false`), v0.3.2b emits nothing and L2 has no ERROR-severity codes. L2 effectively always passes. When `check_urls=true`, unreachable URLs trigger E006 (ERROR), which can block L2.

### 2.4 Data Flow

```
ParsedLlmsTxt.sections[].links[].description ── v0.3.2a ── 0..N W003
ParsedLlmsTxt.sections[].links[].url ────────── v0.3.2b ── 0..N E006
ParsedLlmsTxt.sections[] (content, links) ───── v0.3.2c ── 0..N W011
ParsedLlmsTxt.sections[].links[].description ── v0.3.2c ── 0..N W006
ParsedLlmsTxt.sections[].links[].url ────────── v0.3.2c ── 0..1 I004
DocumentClassification.document_type ─────────── v0.3.2c ── 0..1 I005
ParsedLlmsTxt.blockquote + title ────────────── v0.3.2d ── 0..1 W012
```

---

## 3. Sub-Part Breakdown

| Sub-Part                                              | Title                   | Code(s)                | Severity     | Criteria               | Planned Tests |
| ----------------------------------------------------- | ----------------------- | ---------------------- | ------------ | ---------------------- | ------------- |
| [v0.3.2a](RR-SPEC-v0.3.2a-description-quality.md)     | Description Quality     | W003                   | WARNING      | DS-VC-CON-001, CON-003 | 12            |
| [v0.3.2b](RR-SPEC-v0.3.2b-url-validation.md)          | URL Validation          | E006                   | ERROR        | DS-VC-CON-002          | 14            |
| [v0.3.2c](RR-SPEC-v0.3.2c-section-content-quality.md) | Section Content Quality | W011, W006, I004, I005 | WARNING/INFO | DS-VC-CON-004/005/007  | 16            |
| [v0.3.2d](RR-SPEC-v0.3.2d-blockquote-quality.md)      | Blockquote Quality      | W012                   | WARNING      | DS-VC-CON-006          | 9             |
| **Total**                                             |                         | **6 codes**            |              |                        | **51**        |

### 3.1 Diagnostic Code Inventory

| Code | Name                     | Severity | Level | Sub-Part | Criterion        | Status                                 |
| ---- | ------------------------ | -------- | ----- | -------- | ---------------- | -------------------------------------- |
| W003 | LINK_MISSING_DESCRIPTION | WARNING  | L2    | v0.3.2a  | CON-001, CON-003 | Existing                               |
| E006 | BROKEN_LINKS             | ERROR    | L2    | v0.3.2b  | CON-002          | Existing (reused from v0.3.0g/v0.3.1d) |
| W011 | EMPTY_SECTIONS           | WARNING  | L2    | v0.3.2c  | CON-004          | Existing                               |
| W006 | FORMULAIC_DESCRIPTIONS   | WARNING  | L2    | v0.3.2c  | CON-007          | Existing                               |
| I004 | RELATIVE_URLS_DETECTED   | INFO     | L2    | v0.3.2c  | —                | Existing                               |
| I005 | TYPE_2_FULL_DETECTED     | INFO     | L2    | v0.3.2c  | —                | Existing                               |
| W012 | TRIVIAL_BLOCKQUOTE       | WARNING  | L2    | v0.3.2d  | CON-006          | **NEW**                                |

> [!WARNING]
> **W012 (TRIVIAL_BLOCKQUOTE)** is a new diagnostic code not yet in `diagnostics.py`. CON-006 (Substantive Blockquote) currently has "no standalone diagnostic code." v0.3.2d introduces W012 to make blockquote quality failures explicit and actionable, expanding the registry from 40 to 41 codes.

### 3.2 Criteria Without Standalone Diagnostics

Three criteria map to this level but lack standalone diagnostic codes:

| Criterion     | Title                  | Resolution                                                                                                                                                                 |
| ------------- | ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DS-VC-CON-003 | No Placeholder Content | Covered by W003 context at v0.3.2a (placeholder = special case of missing description). Also feeds AP-CONT-002.                                                            |
| DS-VC-CON-005 | No Duplicate Sections  | Covered by v0.3.2c empty section check + AP-STRUCT-003 anti-pattern pipeline (v0.3.4b). No new code needed — duplication is an anti-pattern, not a per-section diagnostic. |
| DS-VC-CON-006 | Substantive Blockquote | Resolved by introducing **W012** (v0.3.2d).                                                                                                                                |

---

## 4. Workflows

### 4.1 Implementing an L2 Check

```
1. Create src/docstratum/validation/checks/l2_{name}.py
2. Define check() function following the Check Interface
3. Construct ValidationDiagnostic with:
   - code: DiagnosticCode.WXXX, EXXX, or IXXX
   - severity: Severity.WARNING, ERROR, or INFO
   - level: ValidationLevel.L2_CONTENT
   - all standard fields (message, remediation, check_id, etc.)
4. Write tests in tests/test_validation_l2_{name}.py
5. Register check in runner.py L2_CHECKS list
```

### 4.2 Testing L2 Checks

```
1. Create ParsedLlmsTxt fixtures with various link/section states
2. Test W003 emission for missing/empty/placeholder descriptions
3. Test E006 emission for unreachable URLs (mock HTTP, test with check_urls=true and false)
4. Test W011 for empty sections (no links, no prose, only header)
5. Test W006 for formulaic descriptions (≥5 descriptions with >80% avg pairwise similarity)
6. Test I004 for relative URLs
7. Test I005 for Type 2 Full classification
8. Test W012 for blockquote quality (short, repetitive)
9. Verify all diagnostics have correct fields (code, severity, level, check_id)
10. Verify WARNINGs/INFOs don't block L2 gate
```

---

## 5. Acceptance Criteria

### 5.1 Functional

- [ ] All four check modules exist in `src/docstratum/validation/checks/`.
- [ ] W003 emitted per link with missing/empty/placeholder description.
- [ ] E006 emitted per unreachable URL when `check_urls=true`.
- [ ] No diagnostics emitted by v0.3.2b when `check_urls=false` (default).
- [ ] W011 emitted per empty section (no links, no prose, only header).
- [ ] W006 emitted when ≥5 descriptions show >80% avg pairwise similarity.
- [ ] I004 emitted once per file when relative URLs detected.
- [ ] I005 emitted once when `document_type == TYPE_2_FULL`.
- [ ] W012 emitted when blockquote exists but is trivial (<20 chars or >80% similarity with title).
- [ ] L2 checks only run when L1 has passed.
- [ ] L2 passes in default config (no ERROR codes when `check_urls=false`).
- [ ] L2 fails when E006 emitted (when `check_urls=true` and URLs are broken).
- [ ] All diagnostics include `code`, `severity`, `message`, `remediation`, `level`, `check_id`.

### 5.2 Non-Functional

- [ ] `pytest --cov=docstratum.validation --cov-fail-under=85` passes.
- [ ] `black --check` and `ruff check` pass.
- [ ] Google-style docstrings; modules reference "Implements v0.3.2x."
- [ ] URL validation uses `httpx` or `aiohttp` with configurable timeout.
- [ ] HTTP results cached within a single validation run (same URL checked once).

### 5.3 CHANGELOG Entry Template

```markdown
## [0.3.2] - YYYY-MM-DD

**L2 Validation — Content quality checks for link descriptions, URL reachability, section content, and blockquote quality.**

### Added

#### L2 Checks (`src/docstratum/validation/checks/`)

- W003 description quality: warns per link with missing or placeholder description (v0.3.2a)
- E006 URL validation: errors per unreachable URL when `check_urls=true` (v0.3.2b)
- W011 empty sections: warns per section with no meaningful content (v0.3.2c)
- W006 formulaic descriptions: warns when descriptions show >80% avg pairwise similarity (v0.3.2c)
- I004 relative URLs: informational alert when relative URLs detected (v0.3.2c)
- I005 Type 2 Full: informational alert when file exceeds 250KB (v0.3.2c)
- W012 blockquote quality: warns when blockquote is trivial — <20 chars or repeats title (v0.3.2d)

#### New Diagnostic Codes (`src/docstratum/schema/diagnostics.py`)

- W012_TRIVIAL_BLOCKQUOTE — DS-VC-CON-006 criterion
```

---

## 6. Dependencies

| Module                       | What v0.3.2 Uses                                                                                                                                                                                        |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `schema/parsed.py`           | `ParsedLlmsTxt.blockquote`, `ParsedLlmsTxt.title`, `ParsedSection.raw_content`, `ParsedLink.description/url`                                                                                            |
| `schema/diagnostics.py`      | `W003_LINK_MISSING_DESCRIPTION`, `E006_BROKEN_LINKS`, `W011_EMPTY_SECTIONS`, `W006_FORMULAIC_DESCRIPTIONS`, `I004_RELATIVE_URLS_DETECTED`, `I005_TYPE_2_FULL_DETECTED`, `W012_TRIVIAL_BLOCKQUOTE` (NEW) |
| `schema/validation.py`       | `ValidationDiagnostic`, `ValidationLevel.L2_CONTENT`                                                                                                                                                    |
| `schema/classification.py`   | `DocumentClassification.document_type`, `DocumentType.TYPE_2_FULL`                                                                                                                                      |
| `schema/constants.py`        | `PLACEHOLDER_PATTERNS` (constant list for placeholder detection)                                                                                                                                        |
| External: `httpx` (optional) | HTTP HEAD/GET for URL reachability (v0.3.2b only, behind flag)                                                                                                                                          |

### 6.1 Limitations

| Limitation                                   | Reason                                             | When Addressed                |
| -------------------------------------------- | -------------------------------------------------- | ----------------------------- |
| URL reachability off by default              | Network dependency, latency, false negatives       | By design (opt-in flag)       |
| No semantic description quality analysis     | Heuristic only; full NLP is v2.x                   | v2.0+ (if ever)               |
| Formulaic detection requires ≥5 descriptions | Insufficient sample size below 5                   | By design (statistical floor) |
| Blockquote similarity uses simple ratio      | Levenshtein/Jaro-Winkler is sufficient for v0.3.2d | By design                     |
| Placeholder patterns are regex-based         | May false-positive on code examples with "TODO"    | Future: code-block-aware scan |
| Duplicate section detection deferred         | CON-005 handled by AP-STRUCT-003 in v0.3.4b        | v0.3.4b                       |

---

## 7. Design Decisions

| Decision                                       | Choice | Rationale                                                                                                                |
| ---------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------ |
| WARNING for W003/W006/W011/W012                | Yes    | Content quality issues are advisory. Blocking on missing descriptions would reject 40%+ of real-world files.             |
| ERROR for E006 (URL reachability) at L2        | Yes    | Unreachable URLs are a HARD failure. But gated behind `check_urls=false` to avoid network dependency by default.         |
| L2 gate depends on `check_urls` flag           | Yes    | Default off → L2 effectively always passes. Enables CI pipelines to opt in.                                              |
| Placeholder detection in W003 (not standalone) | Yes    | Placeholders in link descriptions are a subset of "missing description" quality. One code (W003) with context variation. |
| W012 as new code (not enhanced W001)           | Yes    | W001 checks _existence_ (L1). W012 checks _quality_ (L2). Different levels, different concerns. Cleaner separation.      |
| Formulaic detection ≥5 threshold               | Yes    | Below 5 descriptions, pairwise similarity is statistically unreliable. Vacuous pass for small files.                     |
| I004/I005 as INFO severity                     | Yes    | Relative URLs and Type 2 size are observations, not actionable quality failures. They inform downstream processing.      |
| HTTP HEAD with GET fallback                    | Yes    | HEAD is lightweight but some servers return 405. GET fallback captures more responses at cost of bandwidth.              |
| URL result caching per validation run          | Yes    | Same URL appearing in multiple sections should be checked once. Avoids redundant network calls and rate limiting.        |

---

## 8. Sub-Part Specifications

- [v0.3.2a — Description Quality](RR-SPEC-v0.3.2a-description-quality.md)
- [v0.3.2b — URL Validation](RR-SPEC-v0.3.2b-url-validation.md)
- [v0.3.2c — Section Content Quality](RR-SPEC-v0.3.2c-section-content-quality.md)
- [v0.3.2d — Blockquote Quality](RR-SPEC-v0.3.2d-blockquote-quality.md)
