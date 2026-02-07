"""Quality scoring models for the DocStratum validation engine.

Implements the 100-point composite quality scoring pipeline from v0.0.4b.
Three dimensions with evidence-grounded weighting:

    Structural:   30 points (30%) -- Gating. CRITICAL failures cap total at 29.
    Content:      50 points (50%) -- Graduated. Weighted by quality predictors.
    Anti-Pattern: 20 points (20%) -- Deduction. Severity-weighted penalties.

Gold standard calibration (v0.0.4b S.11.3):
    Svelte:      92 (Exemplary)
    Pydantic:    90 (Exemplary)
    Vercel SDK:  90 (Exemplary)
    Shadcn UI:   89 (Strong)
    Cursor:      42 (Needs Work)
    NVIDIA:      24 (Critical)

Research basis:
    v0.0.4b S.Content Best Practices (quality predictors, scoring rubric)
    v0.0.4c S.Anti-Patterns Catalog (severity-weighted deductions)
    DECISION-014 (content quality as primary scoring weight)
"""

import logging
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


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
        EXEMPLARY: 90-100 points. Level 4 (DocStratum Extended).
        STRONG: 70-89 points. Level 3 (Best Practices).
        ADEQUATE: 50-69 points. Level 2 (Content Quality).
        NEEDS_WORK: 30-49 points. Level 1 (Structurally Complete).
        CRITICAL: 0-29 points. Level 0 (Parseable Only) or failed.
    """

    EXEMPLARY = "exemplary"
    STRONG = "strong"
    ADEQUATE = "adequate"
    NEEDS_WORK = "needs_work"
    CRITICAL = "critical"

    @classmethod
    def from_score(cls, score: int) -> "QualityGrade":
        """Determine the grade from a numeric score (0-100)."""
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
        """Dimension score as a percentage (0-100)."""
        if self.max_points == 0:
            return 0.0
        return (self.points / self.max_points) * 100


class QualityScore(BaseModel):
    """Composite quality score for an llms.txt file.

    The primary output of the ``docstratum-score`` command. Combines
    three dimension scores into a single 0-100 composite with a grade.

    Weighting (DECISION-014):
        Structural:   30% -- gating factor (necessary but not sufficient)
        Content:      50% -- primary driver (code examples r ~ 0.65)
        Anti-Pattern: 20% -- deduction mechanism

    Attributes:
        total_score: Composite score (0-100).
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
                    points=28.5, max_points=30,
                    checks_passed=18, checks_failed=2, checks_total=20,
                ),
                QualityDimension.CONTENT: DimensionScore(
                    dimension=QualityDimension.CONTENT,
                    points=46.0, max_points=50,
                    checks_passed=13, checks_failed=2, checks_total=15,
                ),
                QualityDimension.ANTI_PATTERN: DimensionScore(
                    dimension=QualityDimension.ANTI_PATTERN,
                    points=17.5, max_points=20,
                    checks_passed=20, checks_failed=2, checks_total=22,
                ),
            },
        )

    Traces to: FR-007 (quality assessment), DECISION-014 (weighting)
    """

    total_score: float = Field(
        ge=0,
        le=100,
        description="Composite quality score (0-100).",
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
