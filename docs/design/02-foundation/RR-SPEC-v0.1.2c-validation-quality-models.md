# v0.1.2c — Validation & Quality Models: Engine Output Schema

> **Phase:** Foundation (v0.1.x)
> **Status:** DRAFT — Realigned to validation-engine pivot (2026-02-06)
> **Parent:** [v0.1.2 — Schema Definition](RR-SPEC-v0.1.2-schema-definition.md)
> **Goal:** Define the output-side models that represent how the validation engine judges a file — the 5-level validation pipeline results (`validation.py`) and the 100-point composite quality scoring (`quality.py`).
> **Traces to:** FR-003, FR-004, FR-007 (v0.0.5a); DECISION-006, -014 (v0.0.4d); v0.0.1b (validation levels), v0.0.4b (quality scoring)

---

## Why This Sub-Part Exists

These two files represent the **output side** of the validation pipeline. After the engine classifies and parses a file (v0.1.2b), it produces two kinds of results: validation diagnostics (pass/fail at each level with specific findings) and quality scores (a 0–100 composite with dimensional breakdown). These models are the primary output of the `docstratum-validate` and `docstratum-score` commands.

Both models depend on `diagnostics.py` (v0.1.2a) for `DiagnosticCode` and `Severity`.

---

## File 5: `src/docstratum/schema/validation.py` — Validation Result Models

**Traces to:** FR-003 (5-level validation pipeline), FR-004 (error reporting with line numbers), v0.0.1b (validation level definitions)

```python
"""Validation result models for the DocStratum validation engine.

Represents the output of the 5-level validation pipeline (L0–L4).
Each level builds on the previous:

    L0 — Parseable:           File can be read and parsed as Markdown.
    L1 — Structurally Valid:  H1 title exists, sections use H2, links are well-formed.
    L2 — Content Quality:     Descriptions are non-empty, URLs resolve, no placeholders.
    L3 — Best Practices:      Canonical names, Master Index, code examples, token budgets.
    L4 — DocStratum Extended: Concept definitions, few-shot examples, LLM instructions.

Research basis:
    v0.0.1b §Validation Level Definitions
    v0.0.4a §Structural Checks (20 checks → L0, L1)
    v0.0.4b §Content Checks (15 checks → L2, L3)
    v0.0.4c §Anti-Pattern Checks (22 checks → cross-level deductions)
"""

from datetime import datetime
from enum import IntEnum
from typing import Optional

from pydantic import BaseModel, Field

from docstratum.schema.diagnostics import DiagnosticCode, Severity


class ValidationLevel(IntEnum):
    """The 5-level validation pipeline.

    Levels are cumulative — achieving L3 means L0, L1, and L2 also pass.
    The highest level where ALL checks pass is the file's validation level.

    Attributes:
        L0_PARSEABLE: File can be read and parsed as Markdown.
        L1_STRUCTURAL: Basic structural elements present (H1, H2s, links).
        L2_CONTENT: Content quality checks pass (non-empty, resolving).
        L3_BEST_PRACTICES: Best practices followed (canonical names, examples).
        L4_DOCSTRATUM_EXTENDED: DocStratum enrichment present (concepts, few-shot).
    """

    L0_PARSEABLE = 0
    L1_STRUCTURAL = 1
    L2_CONTENT = 2
    L3_BEST_PRACTICES = 3
    L4_DOCSTRATUM_EXTENDED = 4


class ValidationDiagnostic(BaseModel):
    """A single validation finding (error, warning, or info).

    Produced by the validation pipeline for each check that fails or
    triggers a note. Includes the diagnostic code, source location,
    context snippet, and remediation hint.

    Attributes:
        code: The DiagnosticCode enum value (e.g., E001_NO_H1_TITLE).
        severity: Derived from the code prefix (ERROR, WARNING, INFO).
        message: Human-readable description of the finding.
        remediation: Suggested fix.
        line_number: Line in the source file where the issue was found (1-indexed).
        column: Column number if applicable (1-indexed), or None.
        context: Snippet of the surrounding source text for display.
        level: Which validation level this diagnostic belongs to.
        check_id: The v0.0.4 check ID (e.g., "STR-001", "CNT-007").

    Example:
        diagnostic = ValidationDiagnostic(
            code=DiagnosticCode.W001_MISSING_BLOCKQUOTE,
            severity=Severity.WARNING,
            message="No blockquote description found after the H1 title.",
            remediation="Add a '> description' blockquote after the H1.",
            line_number=2,
            level=ValidationLevel.L1_STRUCTURAL,
            check_id="STR-002",
        )
    """

    code: DiagnosticCode = Field(
        description="Diagnostic code from the error code registry.",
    )
    severity: Severity = Field(
        description="ERROR, WARNING, or INFO.",
    )
    message: str = Field(
        description="Human-readable finding description.",
    )
    remediation: str = Field(
        default="",
        description="Suggested fix for this issue.",
    )
    line_number: Optional[int] = Field(
        default=None,
        ge=1,
        description="Source line number (1-indexed). None for file-level issues.",
    )
    column: Optional[int] = Field(
        default=None,
        ge=1,
        description="Source column number (1-indexed). None if not applicable.",
    )
    context: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Source text snippet surrounding the issue.",
    )
    level: ValidationLevel = Field(
        description="Which validation level this diagnostic belongs to.",
    )
    check_id: Optional[str] = Field(
        default=None,
        description="v0.0.4 check ID (e.g., 'STR-001', 'CNT-007', 'CHECK-011').",
    )


class ValidationResult(BaseModel):
    """Complete output of the validation pipeline for a single file.

    Contains all diagnostics, the highest validation level achieved,
    and per-level pass/fail status. This is the primary output model
    of the `docstratum-validate` command.

    Attributes:
        level_achieved: Highest validation level where ALL checks pass.
        diagnostics: All findings (errors, warnings, info) from the pipeline.
        levels_passed: Dict mapping each level to pass/fail status.
        total_errors: Count of ERROR-severity diagnostics.
        total_warnings: Count of WARNING-severity diagnostics.
        total_info: Count of INFO-severity diagnostics.
        validated_at: Timestamp of validation.
        source_filename: File that was validated.

    Example:
        result = ValidationResult(
            level_achieved=ValidationLevel.L1_STRUCTURAL,
            diagnostics=[...],
            levels_passed={
                ValidationLevel.L0_PARSEABLE: True,
                ValidationLevel.L1_STRUCTURAL: True,
                ValidationLevel.L2_CONTENT: False,
                ValidationLevel.L3_BEST_PRACTICES: False,
                ValidationLevel.L4_DOCSTRATUM_EXTENDED: False,
            },
        )

    Traces to: FR-003 (5-level pipeline), FR-004 (error reporting)
    """

    level_achieved: ValidationLevel = Field(
        description="Highest level where all checks pass.",
    )
    diagnostics: list[ValidationDiagnostic] = Field(
        default_factory=list,
        description="All validation findings.",
    )
    levels_passed: dict[ValidationLevel, bool] = Field(
        default_factory=lambda: {level: False for level in ValidationLevel},
        description="Per-level pass/fail status.",
    )
    validated_at: datetime = Field(
        default_factory=datetime.now,
        description="When validation was performed.",
    )
    source_filename: str = Field(
        default="llms.txt",
        description="File that was validated.",
    )

    @property
    def total_errors(self) -> int:
        """Count of ERROR-severity diagnostics."""
        return sum(1 for d in self.diagnostics if d.severity == Severity.ERROR)

    @property
    def total_warnings(self) -> int:
        """Count of WARNING-severity diagnostics."""
        return sum(1 for d in self.diagnostics if d.severity == Severity.WARNING)

    @property
    def total_info(self) -> int:
        """Count of INFO-severity diagnostics."""
        return sum(1 for d in self.diagnostics if d.severity == Severity.INFO)

    @property
    def is_valid(self) -> bool:
        """Whether the file achieves at least L0 (parseable)."""
        return self.levels_passed.get(ValidationLevel.L0_PARSEABLE, False)

    @property
    def errors(self) -> list[ValidationDiagnostic]:
        """All ERROR-severity diagnostics."""
        return [d for d in self.diagnostics if d.severity == Severity.ERROR]

    @property
    def warnings(self) -> list[ValidationDiagnostic]:
        """All WARNING-severity diagnostics."""
        return [d for d in self.diagnostics if d.severity == Severity.WARNING]
```

---

## File 6: `src/docstratum/schema/quality.py` — Quality Scoring Models

**Traces to:** FR-007 (quality assessment framework), v0.0.4b (100-point composite scoring), DECISION-014 (content weight 50%)

```python
"""Quality scoring models for the DocStratum validation engine.

Implements the 100-point composite quality scoring pipeline from v0.0.4b.
Three dimensions with evidence-grounded weighting:

    Structural:   30 points (30%) — Gating. CRITICAL failures cap total at 29.
    Content:      50 points (50%) — Graduated. Weighted by quality predictors.
    Anti-Pattern: 20 points (20%) — Deduction. Severity-weighted penalties.

Gold standard calibration (v0.0.4b §11.3):
    Svelte:      92 (Exemplary)
    Pydantic:    90 (Exemplary)
    Vercel SDK:  90 (Exemplary)
    Shadcn UI:   89 (Strong)
    Cursor:      42 (Needs Work)
    NVIDIA:      24 (Critical)

Research basis:
    v0.0.4b §Content Best Practices (quality predictors, scoring rubric)
    v0.0.4c §Anti-Patterns Catalog (severity-weighted deductions)
    DECISION-014 (content quality as primary scoring weight)
"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class QualityDimension(StrEnum):
    """The three dimensions of the composite quality score.

    Attributes:
        STRUCTURAL: Structural compliance (30 points max).
                    Assessed by 20 checks from v0.0.4a.
                    Gating: CRITICAL anti-pattern failures cap the total at 29.
        CONTENT: Content quality (50 points max).
                 Assessed by 15 checks from v0.0.4b.
                 Strongest predictor: code examples (r ~ 0.65).
        ANTI_PATTERN: Anti-pattern absence (20 points max, deduction-based).
                      Assessed by 22 checks from v0.0.4c.
                      Each detected pattern reduces the score.
    """

    STRUCTURAL = "structural"
    CONTENT = "content"
    ANTI_PATTERN = "anti_pattern"


class QualityGrade(StrEnum):
    """Quality grade thresholds calibrated against gold standards.

    Each grade corresponds to a validation level and a score range.
    The thresholds were validated by ensuring gold standards (Svelte, Pydantic)
    score 90+ and known poor implementations (Cursor, NVIDIA) score below 50.

    Attributes:
        EXEMPLARY: 90–100 points. Level 4 (DocStratum Extended).
        STRONG: 70–89 points. Level 3 (Best Practices).
        ADEQUATE: 50–69 points. Level 2 (Content Quality).
        NEEDS_WORK: 30–49 points. Level 1 (Structurally Complete).
        CRITICAL: 0–29 points. Level 0 (Parseable Only) or failed.
    """

    EXEMPLARY = "exemplary"
    STRONG = "strong"
    ADEQUATE = "adequate"
    NEEDS_WORK = "needs_work"
    CRITICAL = "critical"

    @classmethod
    def from_score(cls, score: int) -> "QualityGrade":
        """Determine the grade from a numeric score (0–100)."""
        if score >= 90:
            return cls.EXEMPLARY
        elif score >= 70:
            return cls.STRONG
        elif score >= 50:
            return cls.ADEQUATE
        elif score >= 30:
            return cls.NEEDS_WORK
        else:
            return cls.CRITICAL


class DimensionScore(BaseModel):
    """Score for a single quality dimension.

    Attributes:
        dimension: Which dimension (structural, content, anti_pattern).
        points: Points earned in this dimension.
        max_points: Maximum possible points (30, 50, or 20).
        checks_passed: Number of checks that passed.
        checks_failed: Number of checks that failed.
        checks_total: Total number of checks evaluated.
        details: Per-check results for drill-down reporting.
        is_gated: Whether a CRITICAL failure capped the total score.
    """

    dimension: QualityDimension = Field(
        description="Quality dimension being scored.",
    )
    points: float = Field(
        ge=0,
        description="Points earned (0 to max_points).",
    )
    max_points: float = Field(
        ge=0,
        description="Maximum possible points for this dimension.",
    )
    checks_passed: int = Field(
        ge=0,
        description="Number of checks that passed.",
    )
    checks_failed: int = Field(
        ge=0,
        description="Number of checks that failed.",
    )
    checks_total: int = Field(
        ge=0,
        description="Total checks evaluated in this dimension.",
    )
    details: list[dict] = Field(
        default_factory=list,
        description="Per-check results: [{check_id, passed, weight, points}].",
    )
    is_gated: bool = Field(
        default=False,
        description="True if a CRITICAL anti-pattern capped the total score at 29.",
    )

    @property
    def percentage(self) -> float:
        """Dimension score as a percentage (0–100)."""
        if self.max_points == 0:
            return 0.0
        return (self.points / self.max_points) * 100


class QualityScore(BaseModel):
    """Composite quality score for an llms.txt file.

    The primary output of the `docstratum-score` command. Combines
    three dimension scores into a single 0–100 composite with a grade.

    Weighting (DECISION-014):
        Structural:   30% — gating factor (necessary but not sufficient)
        Content:      50% — primary driver (code examples r ~ 0.65)
        Anti-Pattern: 20% — deduction mechanism

    Attributes:
        total_score: Composite score (0–100).
        grade: Quality grade (Exemplary, Strong, Adequate, Needs Work, Critical).
        dimensions: Per-dimension score breakdown.
        scored_at: Timestamp of scoring.
        source_filename: File that was scored.

    Example:
        score = QualityScore(
            total_score=92,
            grade=QualityGrade.EXEMPLARY,
            dimensions={
                QualityDimension.STRUCTURAL: DimensionScore(
                    dimension=QualityDimension.STRUCTURAL,
                    points=28.5, max_points=30, ...),
                QualityDimension.CONTENT: DimensionScore(
                    dimension=QualityDimension.CONTENT,
                    points=46.0, max_points=50, ...),
                QualityDimension.ANTI_PATTERN: DimensionScore(
                    dimension=QualityDimension.ANTI_PATTERN,
                    points=17.5, max_points=20, ...),
            },
        )

    Traces to: FR-007 (quality assessment), DECISION-014 (weighting)
    """

    total_score: float = Field(
        ge=0,
        le=100,
        description="Composite quality score (0–100).",
    )
    grade: QualityGrade = Field(
        description="Quality grade derived from total_score.",
    )
    dimensions: dict[QualityDimension, DimensionScore] = Field(
        description="Per-dimension score breakdown.",
    )
    scored_at: datetime = Field(
        default_factory=datetime.now,
        description="When scoring was performed.",
    )
    source_filename: str = Field(
        default="llms.txt",
        description="File that was scored.",
    )
```

---

## Design Decisions Applied

| ID | Decision | How Applied in v0.1.2c |
|----|----------|----------------------|
| DECISION-006 | Pydantic for Validation | All models use Pydantic v2 `BaseModel` with `Field` constraints |
| DECISION-014 | Content Weight 50% | `QualityDimension` weights: structural 30, content 50, anti-pattern 20 |

---

## Exit Criteria

- [ ] `ValidationLevel`, `ValidationDiagnostic`, `ValidationResult` importable
- [ ] `QualityDimension`, `QualityGrade`, `DimensionScore`, `QualityScore` importable
- [ ] `QualityGrade.from_score()` returns correct grades at all thresholds
- [ ] `ValidationResult` computed properties (`total_errors`, `total_warnings`, `total_info`, `is_valid`, `errors`, `warnings`) work correctly
- [ ] `DimensionScore.percentage` handles zero `max_points`
- [ ] `black --check` and `ruff check` pass on both files
