# v0.3.4 — Single-File Anti-Pattern Detection

> **Version:** v0.3.4
> **Document Type:** Design Specification (scope overview with sub-part breakdown)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SCOPE-v0.3.x-validation-engine.md](../RR-SCOPE-v0.3.x-validation-engine.md)
> **Depends On:** v0.3.0–v0.3.3 (all L0–L3 diagnostics must be available), `ANTI_PATTERN_REGISTRY` from `constants.py`
> **Consumed By:** v0.3.5 (Pipeline Assembly), v0.4.x (Quality Scoring — DS-QS-GATE), v0.6.x (Remediation)

---

## 1. Purpose

v0.3.4 implements **single-file anti-pattern detection** — the aggregation layer that transforms individual diagnostics from L0–L3 into named behavioral patterns. While individual checks emit granular warnings (e.g., W003 per missing description), anti-pattern detection asks: _does the pattern of failures across this file indicate a systemic documentation problem?_

### 1.1 What Anti-Pattern Detection Adds

| Without v0.3.4                     | With v0.3.4                                                  |
| ---------------------------------- | ------------------------------------------------------------ |
| 15 × W003 (individual diagnostics) | 15 × W003 + **AP-CONT-004 (Link Desert)** annotation         |
| E007 (empty file)                  | E007 + **AP-CRIT-001 (Ghost File)** → gate score at 29       |
| W006 + many W003 + W004            | W006 + W003 + W004 + **AP-STRAT-001 (Automation Obsession)** |

Anti-patterns provide **actionable, consolidated remediation guidance** rather than a list of individual symptoms.

### 1.2 Scope: Single-File Only

The 22 single-file anti-patterns are in scope. The 6 ecosystem anti-patterns (AP-ECO-001 through AP-ECO-006) operate across multiple files and are deferred to v0.7.x.

### 1.3 User Stories

| ID       | As a...              | I want to...                                                 | So that...                                           |
| -------- | -------------------- | ------------------------------------------------------------ | ---------------------------------------------------- |
| US-034-1 | Documentation author | Know if my file matches a known anti-pattern                 | I can fix the root cause, not individual symptoms    |
| US-034-2 | CI pipeline          | Detect critical anti-patterns that cap the quality score     | I can flag files that are structurally unsalvageable |
| US-034-3 | Scorer               | Read anti-pattern metadata to apply DS-QS-GATE scoring rules | Critical patterns correctly cap score at 29          |
| US-034-4 | Remediation engine   | Group diagnostics by anti-pattern                            | I can generate consolidated fix suggestions          |
| US-034-5 | Documentation author | Know which anti-patterns are deferred (need L4)              | I understand the full scope of eventual detection    |

---

## 2. Architecture

### 2.1 Key Design Principle: Post-Hoc Aggregation

Anti-pattern detection does **not** run as part of the L0–L3 check pipeline. It runs **after** all level checks have completed, reading the collected diagnostics and applying pattern rules.

```
L0 checks → L1 checks → L2 checks → L3 checks → Anti-Pattern Detection
                                                        │
                                                        ├── v0.3.4a: Critical (4)
                                                        ├── v0.3.4b: Structural (5)
                                                        ├── v0.3.4c: Content (7 active + 2 deferred)
                                                        └── v0.3.4d: Strategic (3 active + 1 deferred)
```

### 2.2 Module Structure

```
src/docstratum/validation/
├── checks/
│   ├── l0_*.py – l3_*.py     # Individual checks (existing)
│   └── ...
├── anti_patterns/             # v0.3.4 — NEW package
│   ├── __init__.py
│   ├── detector.py            # Orchestrator: runs all detectors
│   ├── critical.py            # v0.3.4a — AP-CRIT-001–004
│   ├── structural.py          # v0.3.4b — AP-STRUCT-001–005
│   ├── content.py             # v0.3.4c — AP-CONT-001–009
│   └── strategic.py           # v0.3.4d — AP-STRAT-001–004
└── ...
```

### 2.3 Detection Interface

All detectors follow a uniform interface:

```python
@dataclass
class AntiPatternDetection:
    """Result of anti-pattern detection for a single pattern."""
    pattern_id: AntiPatternID
    pattern_name: str
    category: AntiPatternCategory
    detected: bool
    constituent_diagnostics: list[DiagnosticCode]
    context: dict[str, Any]


def detect(
    diagnostics: list[ValidationDiagnostic],
    parsed: ParsedLlmsTxt,
) -> list[AntiPatternDetection]:
    """Evaluate all anti-patterns in this category.

    Returns an AntiPatternDetection for each pattern, regardless
    of whether it was detected (detected=True/False). This enables
    comprehensive reporting.
    """
```

### 2.4 Data Flow

```
list[ValidationDiagnostic] from L0–L3
        │
        ▼
┌─────────────────────────┐
│   AntiPatternDetector   │  ← Orchestrator
│                         │
│  ┌── critical.detect()  │ → 4 detections (CRIT-001–004)
│  ├── structural.detect()│ → 5 detections (STRUCT-001–005)
│  ├── content.detect()   │ → 9 detections (CONT-001–009)
│  └── strategic.detect() │ → 4 detections (STRAT-001–004)
│                         │
│  Total: 22 detections   │
└─────────────────────────┘
        │
        ▼
list[AntiPatternDetection]
        │
        ├── Attached to ValidationResult.anti_patterns
        ├── Critical patterns → set critical_anti_pattern_detected flag
        └── Scorer reads flag → DS-QS-GATE (cap at 29)
```

---

## 3. Sub-Part Breakdown

| Sub-Part                                               | Title                    | Patterns | Active | Deferred | Criterion     |
| ------------------------------------------------------ | ------------------------ | -------- | ------ | -------- | ------------- |
| [v0.3.4a](RR-SPEC-v0.3.4a-critical-anti-patterns.md)   | Critical Anti-Patterns   | 4        | 4      | 0        | DS-VC-STR-008 |
| [v0.3.4b](RR-SPEC-v0.3.4b-structural-anti-patterns.md) | Structural Anti-Patterns | 5        | 5      | 0        | DS-VC-STR-009 |
| [v0.3.4c](RR-SPEC-v0.3.4c-content-anti-patterns.md)    | Content Anti-Patterns    | 9        | 7      | 2        | DS-VC-APD-004 |
| [v0.3.4d](RR-SPEC-v0.3.4d-strategic-anti-patterns.md)  | Strategic Anti-Patterns  | 4        | 3      | 1        | DS-VC-APD-005 |
| **Total**                                              |                          | **22**   | **19** | **3**    |               |

### 3.1 Complete Anti-Pattern Inventory

| ID            | Name                  | Category   | Detection Rule                           | Active?     |
| ------------- | --------------------- | ---------- | ---------------------------------------- | ----------- |
| AP-CRIT-001   | Ghost File            | Critical   | E007 emitted                             | ✓           |
| AP-CRIT-002   | Structure Chaos       | Critical   | (E001 OR E002) AND no sections parseable | ✓           |
| AP-CRIT-003   | Encoding Disaster     | Critical   | E003 emitted                             | ✓           |
| AP-CRIT-004   | Link Void             | Critical   | E006 count / total links > 80%           | ✓           |
| AP-STRUCT-001 | Sitemap Dump          | Structural | All sections links-only AND W001         | ✓           |
| AP-STRUCT-002 | Orphaned Sections     | Structural | ≥3 sections with W011                    | ✓           |
| AP-STRUCT-003 | Duplicate Identity    | Structural | ≥2 sections same canonical_name          | ✓           |
| AP-STRUCT-004 | Section Shuffle       | Structural | W008 emitted                             | ✓           |
| AP-STRUCT-005 | Naming Nebula         | Structural | ≥50% sections with W002                  | ✓           |
| AP-CONT-001   | Copy-Paste Plague     | Content    | ≥3 sections >90% text similarity         | ✓           |
| AP-CONT-002   | Blank Canvas          | Content    | ≥2 sections with W011 + placeholders     | ✓           |
| AP-CONT-003   | Jargon Jungle         | Content    | I007 ≥5 times                            | ✗ (L4)      |
| AP-CONT-004   | Link Desert           | Content    | W003 / total links > 60%                 | ✓           |
| AP-CONT-005   | Outdated Oracle       | Content    | Deprecated API pattern heuristic         | ✓ (partial) |
| AP-CONT-006   | Example Void          | Content    | W004 emitted                             | ✓           |
| AP-CONT-007   | Formulaic Description | Content    | W006 emitted                             | ✓           |
| AP-CONT-008   | Silent Agent          | Content    | I001 emitted                             | ✗ (L4)      |
| AP-CONT-009   | Versionless Drift     | Content    | W007 emitted                             | ✓           |
| AP-STRAT-001  | Automation Obsession  | Strategic  | W006 + high W003 + W004                  | ✓ (partial) |
| AP-STRAT-002  | Monolith Monster      | Strategic  | E008 emitted                             | ✓           |
| AP-STRAT-003  | Meta-Doc Spiral       | Strategic  | Meta-keyword heuristic                   | ✓ (partial) |
| AP-STRAT-004  | Preference Trap       | Strategic  | Manipulative directive detection         | ✗ (L4)      |

### 3.2 Deferred Patterns Summary

| Pattern                        | Dependency                  | When Available |
| ------------------------------ | --------------------------- | -------------- |
| AP-CONT-003 (Jargon Jungle)    | I007 (L4 readability)       | v0.9.0         |
| AP-CONT-008 (Silent Agent)     | I001 (L4 LLM instructions)  | v0.9.0         |
| AP-STRAT-004 (Preference Trap) | L4 LLM instructions parsing | v0.9.0         |

> The detection framework returns `detected=False` for deferred patterns with a context note explaining the dependency. When L4 diagnostic codes are eventually emitted, the rules automatically activate.

---

## 4. Gate Behavior: DS-QS-GATE

Critical anti-patterns (v0.3.4a) trigger a scoring gate:

```
Any AP-CRIT-* detected = True
    │
    └── ValidationResult.critical_anti_pattern_detected = True
              │
              └── Scorer (v0.4.x) reads flag → cap total score at 29
                                                 → grade = CRITICAL
```

Non-critical anti-patterns do **not** gate scoring. They reduce dimension-specific scores but allow full grade range.

---

## 5. Acceptance Criteria

### 5.1 Functional

- [ ] Anti-pattern detection package exists at `src/docstratum/validation/anti_patterns/`.
- [ ] `AntiPatternDetection` dataclass defined.
- [ ] `AntiPatternDetector` orchestrator runs all 4 category detectors.
- [ ] All 19 active patterns implemented with correct detection logic.
- [ ] 3 deferred patterns return `detected=False` with dependency context.
- [ ] Critical anti-patterns set `critical_anti_pattern_detected` flag.
- [ ] Each detection includes `pattern_id`, `pattern_name`, `category`, `detected`, `constituent_diagnostics`, `context`.

### 5.2 Non-Functional

- [ ] `pytest --cov=docstratum.validation.anti_patterns --cov-fail-under=85` passes.
- [ ] `black --check` and `ruff check` pass.
- [ ] Google-style docstrings; modules reference "Implements v0.3.4x."

### 5.3 CHANGELOG Entry Template

```markdown
## [0.3.4] - YYYY-MM-DD

**Anti-Pattern Detection — aggregate L0–L3 diagnostics into 22 named behavioral patterns (19 active, 3 deferred to L4).**

### Added

#### Anti-Pattern Detection (`src/docstratum/validation/anti_patterns/`)

- Critical (4): Ghost File, Structure Chaos, Encoding Disaster, Link Void — cap score at 29
- Structural (5): Sitemap Dump, Orphaned Sections, Duplicate Identity, Section Shuffle, Naming Nebula
- Content (7 active / 2 deferred): Copy-Paste Plague, Blank Canvas, Link Desert, Outdated Oracle, Example Void, Formulaic Description, Versionless Drift
- Strategic (3 active / 1 deferred): Automation Obsession, Monolith Monster, Meta-Documentation Spiral
- `AntiPatternDetection` dataclass and `AntiPatternDetector` orchestrator
```

---

## 6. Dependencies

| Module                  | What v0.3.4 Uses                                                                    |
| ----------------------- | ----------------------------------------------------------------------------------- |
| `schema/constants.py`   | `ANTI_PATTERN_REGISTRY`, `AntiPatternID`, `AntiPatternCategory`, `AntiPatternEntry` |
| `schema/diagnostics.py` | All diagnostic codes (E001–E008, W001–W012, I001–I005)                              |
| `schema/validation.py`  | `ValidationDiagnostic`, `ValidationResult`                                          |
| `schema/parsed.py`      | `ParsedLlmsTxt`, `ParsedSection`, `ParsedLink`                                      |
| `schema/constants.py`   | `CANONICAL_SECTION_ORDER`, `TOKEN_ZONES`                                            |

### 6.1 Limitations

| Limitation                   | Reason                                                       | When Addressed                    |
| ---------------------------- | ------------------------------------------------------------ | --------------------------------- |
| 3 patterns deferred          | Depend on L4 diagnostic codes (I001, I007)                   | v0.9.0                            |
| Some patterns use heuristics | Outdated Oracle, Meta-Doc Spiral rely on keyword matching    | By design (pattern matching)      |
| No multi-file detection      | Ecosystem patterns (AP-ECO-\*) require cross-file analysis   | v0.7.x                            |
| Text similarity is basic     | Copy-Paste Plague uses simple ratio, not semantic similarity | Future: embedding-based detection |

---

## 7. Design Decisions

| Decision                                 | Choice         | Rationale                                                                                           |
| ---------------------------------------- | -------------- | --------------------------------------------------------------------------------------------------- |
| Post-hoc aggregation (not inline)        | Yes            | Anti-patterns aggregate across levels; running them inline would couple detection to check ordering |
| Return all 22 detections (detected/not)  | Yes            | Comprehensive reporting; deferred patterns have `detected=False`                                    |
| Critical patterns gate score at 29       | Per DS-QS-GATE | Files with critical anti-patterns cannot exceed CRITICAL grade                                      |
| No new diagnostic codes                  | Correct        | Anti-patterns aggregate existing codes; they don't emit new diagnostics                             |
| Deferred patterns return False + context | Yes            | Framework is forward-compatible; rules activate when L4 codes appear                                |
| Separate package (`anti_patterns/`)      | Yes            | Clean separation from level-based checks; independent test suite                                    |

---

## 8. Sub-Part Specifications

- [v0.3.4a — Critical Anti-Patterns](RR-SPEC-v0.3.4a-critical-anti-patterns.md)
- [v0.3.4b — Structural Anti-Patterns](RR-SPEC-v0.3.4b-structural-anti-patterns.md)
- [v0.3.4c — Content Anti-Patterns](RR-SPEC-v0.3.4c-content-anti-patterns.md)
- [v0.3.4d — Strategic Anti-Patterns](RR-SPEC-v0.3.4d-strategic-anti-patterns.md)
