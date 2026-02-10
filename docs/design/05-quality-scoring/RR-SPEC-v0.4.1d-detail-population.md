# v0.4.1d — Per-Check Detail Population

> **Version:** v0.4.1d
> **Document Type:** Sub-Part Design Specification
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.4.1-composite-scoring.md](RR-SPEC-v0.4.1-composite-scoring.md)
> **Depends On:** v0.4.0b/c/d (raw `DimensionScore.details[]`), v0.4.0a (`CRITERIA_REGISTRY`)

---

## 1. Purpose

v0.4.1d defines the **schema and enrichment** of `DimensionScore.details[]` — the per-criterion breakdown that downstream consumers (remediation, reporting, CLI) rely on for drill-down analysis.

The dimension scorers (v0.4.0b/c/d) already populate `details[]` with basic fields. v0.4.1d formalizes the required key set and ensures consistency across all 30 criteria.

### 1.1 User Story

> As a remediation engine, I want every criterion's detail entry to have a consistent shape — including points, compliance rate, and diagnostic count — so that I can prioritize fixes by potential score impact without per-dimension special handling.

---

## 2. Detail Entry Schema

### 2.1 Required Keys

Every entry in `DimensionScore.details[]` **must** contain the following keys:

| Key                | Type    | Description                                                | Source             |
| ------------------ | ------- | ---------------------------------------------------------- | ------------------ |
| `check_id`         | `str`   | Criterion ID (e.g., `"DS-VC-STR-001"`)                     | `CriterionMapping` |
| `name`             | `str`   | Human-readable criterion name (e.g., `"H1 Title Present"`) | `CriterionMapping` |
| `passed`           | `bool`  | Whether the criterion passed (full points earned)          | Dimension scorer   |
| `weight`           | `float` | Maximum possible points for this criterion                 | `CriterionMapping` |
| `points`           | `float` | Points actually earned (0 to weight)                       | Dimension scorer   |
| `scoring_mode`     | `str`   | `"BINARY"`, `"GRADUATED"`, or `"THRESHOLD"`                | `CriterionMapping` |
| `compliance_rate`  | `float` | 0.0–1.0 compliance fraction (1.0 for binary pass)          | Dimension scorer   |
| `diagnostic_count` | `int`   | Number of relevant diagnostics found                       | Dimension scorer   |
| `level`            | `str`   | Validation level name (e.g., `"L1_STRUCTURAL"`)            | `CriterionMapping` |
| `dimension`        | `str`   | Dimension name (e.g., `"structural"`)                      | `CriterionMapping` |

### 2.2 Optional Keys

| Key                | Type        | Description                                  | Present When               |
| ------------------ | ----------- | -------------------------------------------- | -------------------------- |
| `l4_dependent`     | `bool`      | Whether criterion requires L4 checks         | APD criteria only          |
| `threshold`        | `float`     | Threshold value for THRESHOLD mode           | THRESHOLD criteria only    |
| `anti_pattern_ids` | `list[str]` | Anti-pattern IDs evaluated                   | APD-004, APD-005           |
| `impact_potential` | `float`     | Points recoverable if criterion fully passes | Always (= weight - points) |

### 2.3 Example Entry

```python
{
    "check_id": "DS-VC-CON-001",
    "name": "Link Descriptions",
    "passed": False,
    "weight": 5.0,
    "points": 3.75,
    "scoring_mode": "GRADUATED",
    "compliance_rate": 0.75,
    "diagnostic_count": 5,
    "level": "L2_CONTENT",
    "dimension": "content",
    "impact_potential": 1.25,
}
```

---

## 3. Enrichment Logic

### 3.1 What v0.4.1d Adds

The dimension scorers (v0.4.0b/c/d) already populate `check_id`, `passed`, `weight`, `points`, `compliance_rate`, `diagnostic_count`, and `level`. v0.4.1d adds:

| Key                | Source                                          | Logic                 |
| ------------------ | ----------------------------------------------- | --------------------- |
| `name`             | `CRITERIA_REGISTRY[check_id].name`              | Lookup from registry  |
| `scoring_mode`     | `CRITERIA_REGISTRY[check_id].scoring_mode.name` | Enum name as string   |
| `dimension`        | `DimensionScore.dimension.value`                | From parent dimension |
| `impact_potential` | `weight - points`                               | Derived calculation   |

### 3.2 Implementation

```python
"""Implements v0.4.1d — Per-Check Detail Population."""

from docstratum.schema.quality import DimensionScore
from docstratum.scoring.registry import CRITERIA_REGISTRY


def enrich_details(dimension_score: DimensionScore) -> DimensionScore:
    """Enrich detail entries with registry metadata.

    Adds `name`, `scoring_mode`, `dimension`, and `impact_potential`
    to each detail entry. Existing keys are preserved.

    Args:
        dimension_score: DimensionScore with raw details from v0.4.0.

    Returns:
        New DimensionScore with enriched details (model_copy).

    Implements v0.4.1d.
    """
    enriched = []
    for detail in dimension_score.details:
        check_id = detail.get("check_id")
        criterion = CRITERIA_REGISTRY.get(check_id)

        enriched_detail = {**detail}

        if criterion:
            enriched_detail.setdefault("name", criterion.name)
            enriched_detail.setdefault(
                "scoring_mode", criterion.scoring_mode.name
            )
        enriched_detail.setdefault(
            "dimension", dimension_score.dimension.value
        )

        weight = detail.get("weight", 0.0)
        points = detail.get("points", 0.0)
        enriched_detail["impact_potential"] = round(weight - points, 2)

        enriched.append(enriched_detail)

    return dimension_score.model_copy(update={"details": enriched})
```

### 3.3 Decision Tree

```
Input: DimensionScore with details[]
    │
    For each detail entry:
    │
    ├── Look up check_id in CRITERIA_REGISTRY
    │     ├── Found: add name, scoring_mode from registry
    │     └── Not found: skip registry enrichment (log warning)
    │
    ├── Add dimension from parent DimensionScore
    │
    ├── Calculate impact_potential = weight - points
    │
    └── Preserve all existing keys (setdefault, not overwrite)
    │
    Return model_copy with enriched details
```

---

## 4. Consistency Guarantees

### 4.1 All 30 Criteria Represented

After enrichment, the combined `details[]` across all three `DimensionScore` instances must contain exactly **30 entries** — one per criterion in `CRITERIA_REGISTRY`:

| Dimension    | Count  | Criteria Range            |
| ------------ | ------ | ------------------------- |
| STRUCTURAL   | 9      | DS-VC-STR-001 through 009 |
| CONTENT      | 13     | DS-VC-CON-001 through 013 |
| ANTI_PATTERN | 8      | DS-VC-APD-001 through 008 |
| **Total**    | **30** |                           |

### 4.2 Sorting

Details within each dimension are ordered by criterion ID (ascending). This is enforced by the registry iteration order in v0.4.0b/c/d.

### 4.3 Impact Potential Usage

`impact_potential` enables remediation prioritization:

```
Sort criteria by impact_potential DESC → highest-impact fixes first
```

| Criterion | Weight | Points | Impact | Priority        |
| --------- | ------ | ------ | ------ | --------------- |
| CON-001   | 5.0    | 0.0    | 5.0    | Fix first       |
| CON-008   | 5.0    | 3.57   | 1.43   | Lower           |
| STR-001   | 5.0    | 5.0    | 0.0    | Already passing |

---

## 5. Edge Cases

| Case                               | Behavior                                  | Rationale                       |
| ---------------------------------- | ----------------------------------------- | ------------------------------- |
| check_id not in registry           | name/scoring_mode not added; log warning  | Defensive — unknown criteria    |
| Empty details list                 | Returns empty enriched list               | No criteria to enrich           |
| points > weight (should not occur) | impact_potential is negative              | Bug in dimension scorer         |
| Existing name key in detail        | setdefault preserves existing             | Dimension scorer takes priority |
| L4-dependent criterion scores 0    | impact_potential = weight (full recovery) | Accurately reflects potential   |

---

## 6. Test Plan (8 tests)

| #   | Test Name                            | Input                          | Expected                                  |
| --- | ------------------------------------ | ------------------------------ | ----------------------------------------- |
| 1   | `test_enrichment_adds_name`          | Detail without `name`          | `name` populated from registry            |
| 2   | `test_enrichment_adds_scoring_mode`  | Detail without `scoring_mode`  | `scoring_mode` = "BINARY" or "GRADUATED"  |
| 3   | `test_enrichment_adds_dimension`     | Detail without `dimension`     | `dimension` = "structural"                |
| 4   | `test_enrichment_calculates_impact`  | weight=5, points=3.75          | `impact_potential` = 1.25                 |
| 5   | `test_enrichment_zero_impact`        | weight=5, points=5.0           | `impact_potential` = 0.0                  |
| 6   | `test_enrichment_preserves_existing` | Detail with `name` already set | Existing `name` not overwritten           |
| 7   | `test_enrichment_all_30_criteria`    | Full scoring pipeline output   | 9 + 13 + 8 = 30 detail entries total      |
| 8   | `test_enrichment_returns_model_copy` | Any DimensionScore             | Original unchanged; new instance returned |

---

## 7. Deliverables

| File                                  | Description                                       |
| ------------------------------------- | ------------------------------------------------- |
| `src/docstratum/scoring/composite.py` | `enrich_details()` function (in composite module) |
| `tests/scoring/test_composite.py`     | Detail enrichment tests (v0.4.1d portion)         |

---

## 8. Changelog Requirements

```markdown
## [0.4.1d] - YYYY-MM-DD

**Per-Check Detail Population — Enriches details[] with registry metadata.**

### Added

#### Detail Enrichment (`src/docstratum/scoring/composite.py`)

- `enrich_details()` — adds `name`, `scoring_mode`, `dimension`, `impact_potential` to each `DimensionScore.details[]` entry

### Notes

- **Schema:** 10 required keys + 4 optional keys per detail entry (documented in v0.4.1d spec).
- **Impact potential:** `weight - points` for remediation prioritization.
```
