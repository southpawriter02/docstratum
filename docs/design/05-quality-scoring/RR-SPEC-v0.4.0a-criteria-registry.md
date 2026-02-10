# v0.4.0a — Criteria-to-Diagnostic Mapping Registry

> **Version:** v0.4.0a
> **Document Type:** Sub-Part Design Specification
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.4.0-dimension-scoring.md](RR-SPEC-v0.4.0-dimension-scoring.md)
> **Depends On:** ASoT scoring dimension standards (DS-QS-DIM-STR, DS-QS-DIM-CON, DS-QS-DIM-APD)

---

## 1. Purpose

v0.4.0a defines the **authoritative mapping** between the 30 validation criteria and the diagnostic codes / anti-pattern IDs that feed into each criterion's evaluation. This registry is the single source of truth consumed by all three dimension scorers.

### 1.1 Why a Separate Registry

- All three dimension scorers need the same mapping data.
- Centralizing avoids duplication and ensures consistency.
- When v0.9.0 adds L4 diagnostic codes, only the registry needs updating.

### 1.2 User Story

> As a developer, I want a single registry mapping criteria to diagnostics so that adding new codes or criteria doesn't require modifying scorer logic.

---

## 2. Registry Data Model

```python
"""Implements v0.4.0a — Criteria-to-Diagnostic Mapping Registry."""

from dataclasses import dataclass, field
from enum import StrEnum

from docstratum.schema.constants import AntiPatternID
from docstratum.schema.diagnostics import DiagnosticCode
from docstratum.schema.quality import QualityDimension
from docstratum.schema.validation import ValidationLevel


class ScoringMode(StrEnum):
    """How a criterion's points are calculated.

    Attributes:
        BINARY: Pass = full points, fail = 0.
        GRADUATED: compliance_rate × max_points (float).
        THRESHOLD: ≥ threshold → full, < threshold → 0.
    """
    BINARY = "binary"
    GRADUATED = "graduated"
    THRESHOLD = "threshold"


class PassType(StrEnum):
    """Whether violation blocks level progression.

    From ASoT specs. HARD = ERROR-severity, SOFT = WARNING-severity.
    """
    HARD = "hard"
    SOFT = "soft"


@dataclass(frozen=True)
class CriterionMapping:
    """Maps a single validation criterion to its diagnostic sources.

    Attributes:
        criterion_id: The canonical ID (e.g., "DS-VC-STR-001").
        name: Human-readable name.
        dimension: Which scoring dimension this belongs to.
        max_points: Point allocation for full compliance.
        validation_level: Which validation level evaluates this.
        pass_type: HARD (error-blocking) or SOFT (warning-only).
        diagnostic_codes: Which diagnostic codes affect this criterion.
        anti_pattern_ids: Which anti-pattern IDs affect this (APD only).
        scoring_mode: BINARY, GRADUATED, or THRESHOLD.
        threshold: For THRESHOLD mode, the compliance rate needed for full points.
        l4_dependent: True if this criterion depends on L4 codes (scores 0 until v0.9.0).

    Implements v0.4.0a.
    """
    criterion_id: str
    name: str
    dimension: QualityDimension
    max_points: float
    validation_level: ValidationLevel
    pass_type: PassType
    diagnostic_codes: list[DiagnosticCode] = field(default_factory=list)
    anti_pattern_ids: list[AntiPatternID] = field(default_factory=list)
    scoring_mode: ScoringMode = ScoringMode.BINARY
    threshold: float = 0.0
    l4_dependent: bool = False
```

---

## 3. Complete Registry

### 3.1 Structural Dimension (9 criteria, 30 points)

```python
STRUCTURAL_CRITERIA: list[CriterionMapping] = [
    CriterionMapping(
        criterion_id="DS-VC-STR-001",
        name="H1 Title Present",
        dimension=QualityDimension.STRUCTURAL,
        max_points=5.0,
        validation_level=ValidationLevel.L1_STRUCTURAL,
        pass_type=PassType.HARD,
        diagnostic_codes=[DiagnosticCode.E001_NO_H1_TITLE],
        scoring_mode=ScoringMode.BINARY,
    ),
    CriterionMapping(
        criterion_id="DS-VC-STR-002",
        name="Single H1 (No Duplicates)",
        dimension=QualityDimension.STRUCTURAL,
        max_points=3.0,
        validation_level=ValidationLevel.L1_STRUCTURAL,
        pass_type=PassType.HARD,
        diagnostic_codes=[DiagnosticCode.E002_MULTIPLE_H1],
        scoring_mode=ScoringMode.BINARY,
    ),
    CriterionMapping(
        criterion_id="DS-VC-STR-003",
        name="Project Summary Blockquote",
        dimension=QualityDimension.STRUCTURAL,
        max_points=3.0,
        validation_level=ValidationLevel.L1_STRUCTURAL,
        pass_type=PassType.SOFT,
        diagnostic_codes=[DiagnosticCode.W001_MISSING_BLOCKQUOTE],
        scoring_mode=ScoringMode.BINARY,
    ),
    CriterionMapping(
        criterion_id="DS-VC-STR-004",
        name="Valid Markdown Structure",
        dimension=QualityDimension.STRUCTURAL,
        max_points=4.0,
        validation_level=ValidationLevel.L1_STRUCTURAL,
        pass_type=PassType.HARD,
        diagnostic_codes=[DiagnosticCode.E005_INVALID_MARKDOWN],
        scoring_mode=ScoringMode.GRADUATED,
    ),
    CriterionMapping(
        criterion_id="DS-VC-STR-005",
        name="Link Syntax Validity",
        dimension=QualityDimension.STRUCTURAL,
        max_points=4.0,
        validation_level=ValidationLevel.L1_STRUCTURAL,
        pass_type=PassType.HARD,
        diagnostic_codes=[DiagnosticCode.E006_BROKEN_LINKS],
        scoring_mode=ScoringMode.GRADUATED,
    ),
    CriterionMapping(
        criterion_id="DS-VC-STR-006",
        name="Heading Hierarchy",
        dimension=QualityDimension.STRUCTURAL,
        max_points=3.0,
        validation_level=ValidationLevel.L1_STRUCTURAL,
        pass_type=PassType.SOFT,
        diagnostic_codes=[],  # Heuristic from parsed structure
        scoring_mode=ScoringMode.GRADUATED,
    ),
    CriterionMapping(
        criterion_id="DS-VC-STR-007",
        name="Canonical Section Ordering",
        dimension=QualityDimension.STRUCTURAL,
        max_points=3.0,
        validation_level=ValidationLevel.L3_BEST_PRACTICES,
        pass_type=PassType.SOFT,
        diagnostic_codes=[
            DiagnosticCode.W008_SECTION_ORDER_NON_CANONICAL,
        ],
        scoring_mode=ScoringMode.BINARY,
    ),
    CriterionMapping(
        criterion_id="DS-VC-STR-008",
        name="No Critical Anti-Patterns",
        dimension=QualityDimension.STRUCTURAL,
        max_points=3.0,
        validation_level=ValidationLevel.L3_BEST_PRACTICES,
        pass_type=PassType.HARD,
        anti_pattern_ids=[
            AntiPatternID.AP_CRIT_001,
            AntiPatternID.AP_CRIT_002,
            AntiPatternID.AP_CRIT_003,
            AntiPatternID.AP_CRIT_004,
        ],
        scoring_mode=ScoringMode.BINARY,
    ),
    CriterionMapping(
        criterion_id="DS-VC-STR-009",
        name="No Structural Anti-Patterns",
        dimension=QualityDimension.STRUCTURAL,
        max_points=2.0,
        validation_level=ValidationLevel.L3_BEST_PRACTICES,
        pass_type=PassType.SOFT,
        anti_pattern_ids=[
            AntiPatternID.AP_STRUCT_001,
            AntiPatternID.AP_STRUCT_002,
            AntiPatternID.AP_STRUCT_003,
            AntiPatternID.AP_STRUCT_004,
            AntiPatternID.AP_STRUCT_005,
        ],
        scoring_mode=ScoringMode.GRADUATED,
    ),
]
```

### 3.2 Content Dimension (13 criteria, 50 points)

```python
CONTENT_CRITERIA: list[CriterionMapping] = [
    CriterionMapping("DS-VC-CON-001", "Non-Empty Link Descriptions",
        QualityDimension.CONTENT, 5.0, ValidationLevel.L2_CONTENT,
        PassType.SOFT, [DiagnosticCode.W003_LINK_MISSING_DESCRIPTION],
        scoring_mode=ScoringMode.GRADUATED),
    CriterionMapping("DS-VC-CON-002", "URL Resolvability",
        QualityDimension.CONTENT, 4.0, ValidationLevel.L2_CONTENT,
        PassType.SOFT, [DiagnosticCode.E006_BROKEN_LINKS],
        scoring_mode=ScoringMode.GRADUATED),
    CriterionMapping("DS-VC-CON-003", "No Placeholder Text",
        QualityDimension.CONTENT, 3.0, ValidationLevel.L2_CONTENT,
        PassType.SOFT, [DiagnosticCode.W011_EMPTY_SECTIONS],
        scoring_mode=ScoringMode.GRADUATED),
    CriterionMapping("DS-VC-CON-004", "Non-Empty Sections",
        QualityDimension.CONTENT, 4.0, ValidationLevel.L2_CONTENT,
        PassType.SOFT, [DiagnosticCode.W011_EMPTY_SECTIONS],
        scoring_mode=ScoringMode.GRADUATED),
    CriterionMapping("DS-VC-CON-005", "No Duplicate Section Names",
        QualityDimension.CONTENT, 3.0, ValidationLevel.L2_CONTENT,
        PassType.SOFT, [],
        scoring_mode=ScoringMode.BINARY),
    CriterionMapping("DS-VC-CON-006", "Substantive Blockquote",
        QualityDimension.CONTENT, 3.0, ValidationLevel.L2_CONTENT,
        PassType.SOFT, [],
        scoring_mode=ScoringMode.BINARY),
    CriterionMapping("DS-VC-CON-007", "No Formulaic Descriptions",
        QualityDimension.CONTENT, 3.0, ValidationLevel.L2_CONTENT,
        PassType.SOFT, [DiagnosticCode.W006_FORMULAIC_DESCRIPTION],
        scoring_mode=ScoringMode.BINARY),
    CriterionMapping("DS-VC-CON-008", "Canonical Section Names",
        QualityDimension.CONTENT, 5.0, ValidationLevel.L3_BEST_PRACTICES,
        PassType.SOFT, [DiagnosticCode.W002_NON_CANONICAL_SECTION_NAME],
        scoring_mode=ScoringMode.GRADUATED, threshold=0.70),
    CriterionMapping("DS-VC-CON-009", "Master Index Present",
        QualityDimension.CONTENT, 5.0, ValidationLevel.L3_BEST_PRACTICES,
        PassType.SOFT, [DiagnosticCode.W009_NO_MASTER_INDEX],
        scoring_mode=ScoringMode.BINARY),
    CriterionMapping("DS-VC-CON-010", "Code Examples Present",
        QualityDimension.CONTENT, 5.0, ValidationLevel.L3_BEST_PRACTICES,
        PassType.SOFT, [DiagnosticCode.W004_NO_CODE_EXAMPLES],
        scoring_mode=ScoringMode.BINARY),
    CriterionMapping("DS-VC-CON-011", "Code Language Specifiers",
        QualityDimension.CONTENT, 3.0, ValidationLevel.L3_BEST_PRACTICES,
        PassType.SOFT, [DiagnosticCode.W005_CODE_NO_LANGUAGE_SPECIFIER],
        scoring_mode=ScoringMode.GRADUATED),
    CriterionMapping("DS-VC-CON-012", "Token Budget Respected",
        QualityDimension.CONTENT, 4.0, ValidationLevel.L3_BEST_PRACTICES,
        PassType.SOFT, [DiagnosticCode.W010_TOKEN_BUDGET_EXCEEDED],
        scoring_mode=ScoringMode.BINARY),
    CriterionMapping("DS-VC-CON-013", "Version Metadata Present",
        QualityDimension.CONTENT, 3.0, ValidationLevel.L3_BEST_PRACTICES,
        PassType.SOFT, [DiagnosticCode.W007_MISSING_VERSION_METADATA],
        scoring_mode=ScoringMode.BINARY),
]
```

### 3.3 Anti-Pattern Dimension (8 criteria, 20 points)

```python
ANTI_PATTERN_CRITERIA: list[CriterionMapping] = [
    CriterionMapping("DS-VC-APD-001", "LLM Instructions Present",
        QualityDimension.ANTI_PATTERN, 3.0,
        ValidationLevel.L4_DOCSTRATUM_EXTENDED,
        PassType.SOFT, [], scoring_mode=ScoringMode.BINARY,
        l4_dependent=True),
    CriterionMapping("DS-VC-APD-002", "Concept Definitions Present",
        QualityDimension.ANTI_PATTERN, 3.0,
        ValidationLevel.L4_DOCSTRATUM_EXTENDED,
        PassType.SOFT, [], scoring_mode=ScoringMode.BINARY,
        l4_dependent=True),
    CriterionMapping("DS-VC-APD-003", "Few-Shot Examples Present",
        QualityDimension.ANTI_PATTERN, 3.0,
        ValidationLevel.L4_DOCSTRATUM_EXTENDED,
        PassType.SOFT, [], scoring_mode=ScoringMode.BINARY,
        l4_dependent=True),
    CriterionMapping("DS-VC-APD-004", "No Content Anti-Patterns",
        QualityDimension.ANTI_PATTERN, 3.0,
        ValidationLevel.L4_DOCSTRATUM_EXTENDED,
        PassType.SOFT,
        anti_pattern_ids=[
            AntiPatternID.AP_CONT_001, AntiPatternID.AP_CONT_002,
            AntiPatternID.AP_CONT_003, AntiPatternID.AP_CONT_004,
            AntiPatternID.AP_CONT_005, AntiPatternID.AP_CONT_006,
            AntiPatternID.AP_CONT_007, AntiPatternID.AP_CONT_008,
            AntiPatternID.AP_CONT_009,
        ],
        scoring_mode=ScoringMode.GRADUATED),
    CriterionMapping("DS-VC-APD-005", "No Strategic Anti-Patterns",
        QualityDimension.ANTI_PATTERN, 2.0,
        ValidationLevel.L4_DOCSTRATUM_EXTENDED,
        PassType.SOFT,
        anti_pattern_ids=[
            AntiPatternID.AP_STRAT_001, AntiPatternID.AP_STRAT_002,
            AntiPatternID.AP_STRAT_003, AntiPatternID.AP_STRAT_004,
        ],
        scoring_mode=ScoringMode.GRADUATED),
    CriterionMapping("DS-VC-APD-006", "Balanced Token Distribution",
        QualityDimension.ANTI_PATTERN, 2.0,
        ValidationLevel.L4_DOCSTRATUM_EXTENDED,
        PassType.SOFT, [], scoring_mode=ScoringMode.BINARY),
    CriterionMapping("DS-VC-APD-007", "Absolute URL Prevalence",
        QualityDimension.ANTI_PATTERN, 2.0,
        ValidationLevel.L4_DOCSTRATUM_EXTENDED,
        PassType.SOFT, [], scoring_mode=ScoringMode.THRESHOLD,
        threshold=0.90),
    CriterionMapping("DS-VC-APD-008", "Jargon Defined or Linked",
        QualityDimension.ANTI_PATTERN, 2.0,
        ValidationLevel.L4_DOCSTRATUM_EXTENDED,
        PassType.SOFT, [], scoring_mode=ScoringMode.BINARY,
        l4_dependent=True),
]
```

### 3.4 Convenience Accessors

```python
# Combined registry
CRITERIA_REGISTRY: list[CriterionMapping] = (
    STRUCTURAL_CRITERIA + CONTENT_CRITERIA + ANTI_PATTERN_CRITERIA
)

def get_criteria_by_dimension(
    dimension: QualityDimension,
) -> list[CriterionMapping]:
    """Return criteria for a given dimension."""
    return [c for c in CRITERIA_REGISTRY if c.dimension == dimension]

def get_criterion(criterion_id: str) -> CriterionMapping | None:
    """Look up a single criterion by ID."""
    for c in CRITERIA_REGISTRY:
        if c.criterion_id == criterion_id:
            return c
    return None
```

---

## 4. Deliverables

| File                                 | Description              |
| ------------------------------------ | ------------------------ |
| `src/docstratum/scoring/registry.py` | Criteria registry module |
| `tests/scoring/test_registry.py`     | Unit tests               |

---

## 5. Test Plan (8 tests)

| #   | Test Name                        | Assertion                                    |
| --- | -------------------------------- | -------------------------------------------- |
| 1   | `test_registry_has_30_criteria`  | `len(CRITERIA_REGISTRY) == 30`               |
| 2   | `test_structural_9_criteria`     | 9 STR criteria, sum 30 points                |
| 3   | `test_content_13_criteria`       | 13 CON criteria, sum 50 points               |
| 4   | `test_anti_pattern_8_criteria`   | 8 APD criteria, sum 20 points                |
| 5   | `test_total_points_100`          | Sum of all max_points == 100                 |
| 6   | `test_l4_dependent_count`        | 4 criteria marked `l4_dependent=True`        |
| 7   | `test_get_criteria_by_dimension` | Returns correct subset                       |
| 8   | `test_get_criterion_by_id`       | Returns matching criterion, None for missing |
