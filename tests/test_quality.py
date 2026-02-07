"""Tests for quality scoring models (quality.py)."""

import pytest
from pydantic import ValidationError

from docstratum.schema.quality import (
    DimensionScore,
    QualityDimension,
    QualityGrade,
    QualityScore,
)

# ── QualityDimension ─────────────────────────────────────────────────


@pytest.mark.unit
def test_quality_dimension_values():
    """Verify QualityDimension has exactly 3 members with correct string values."""
    assert len(QualityDimension) == 3
    assert QualityDimension.STRUCTURAL == "structural"
    assert QualityDimension.CONTENT == "content"
    assert QualityDimension.ANTI_PATTERN == "anti_pattern"


# ── QualityGrade ─────────────────────────────────────────────────────


@pytest.mark.unit
def test_quality_grade_values():
    """Verify QualityGrade has exactly 5 members with correct string values."""
    assert len(QualityGrade) == 5
    assert QualityGrade.EXEMPLARY == "exemplary"
    assert QualityGrade.STRONG == "strong"
    assert QualityGrade.ADEQUATE == "adequate"
    assert QualityGrade.NEEDS_WORK == "needs_work"
    assert QualityGrade.CRITICAL == "critical"


@pytest.mark.unit
@pytest.mark.parametrize(
    "score,expected_grade",
    [
        (100, QualityGrade.EXEMPLARY),
        (95, QualityGrade.EXEMPLARY),
        (90, QualityGrade.EXEMPLARY),
        (89, QualityGrade.STRONG),
        (70, QualityGrade.STRONG),
        (69, QualityGrade.ADEQUATE),
        (50, QualityGrade.ADEQUATE),
        (49, QualityGrade.NEEDS_WORK),
        (30, QualityGrade.NEEDS_WORK),
        (29, QualityGrade.CRITICAL),
        (0, QualityGrade.CRITICAL),
    ],
)
def test_quality_grade_from_score(score: int, expected_grade: QualityGrade):
    """Exit Criterion 3: from_score returns correct grades at all thresholds."""
    assert QualityGrade.from_score(score) == expected_grade


# ── DimensionScore ───────────────────────────────────────────────────


def _make_dimension_score(
    dimension: QualityDimension = QualityDimension.STRUCTURAL,
    points: float = 25.0,
    max_points: float = 30.0,
    checks_passed: int = 18,
    checks_failed: int = 2,
    checks_total: int = 20,
) -> DimensionScore:
    """Helper to create a DimensionScore with sensible defaults."""
    return DimensionScore(
        dimension=dimension,
        points=points,
        max_points=max_points,
        checks_passed=checks_passed,
        checks_failed=checks_failed,
        checks_total=checks_total,
    )


@pytest.mark.unit
def test_dimension_score_creation():
    """Verify DimensionScore construction with all fields."""
    score = _make_dimension_score()

    assert score.dimension == QualityDimension.STRUCTURAL
    assert score.points == 25.0
    assert score.max_points == 30.0
    assert score.checks_passed == 18
    assert score.checks_failed == 2
    assert score.checks_total == 20
    assert score.details == []
    assert score.is_gated is False


@pytest.mark.unit
def test_dimension_score_percentage():
    """Exit Criterion 5: percentage computes correctly."""
    score = _make_dimension_score(points=15.0, max_points=30.0)

    assert score.percentage == pytest.approx(50.0)


@pytest.mark.unit
def test_dimension_score_percentage_full():
    """Verify percentage is 100% when points equal max_points."""
    score = _make_dimension_score(points=30.0, max_points=30.0)

    assert score.percentage == pytest.approx(100.0)


@pytest.mark.unit
def test_dimension_score_percentage_zero_max_points():
    """Exit Criterion 5: percentage handles zero max_points gracefully."""
    score = _make_dimension_score(points=0, max_points=0)

    assert score.percentage == 0.0


@pytest.mark.unit
def test_dimension_score_rejects_negative_points():
    """Verify points enforces ge=0 constraint."""
    with pytest.raises(ValidationError):
        _make_dimension_score(points=-1.0)


@pytest.mark.unit
def test_dimension_score_is_gated():
    """Verify is_gated can be set to True."""
    score = DimensionScore(
        dimension=QualityDimension.STRUCTURAL,
        points=20.0,
        max_points=30.0,
        checks_passed=15,
        checks_failed=5,
        checks_total=20,
        is_gated=True,
    )

    assert score.is_gated is True


# ── QualityScore ─────────────────────────────────────────────────────


def _make_quality_score(total: float = 92.0) -> QualityScore:
    """Helper to create a QualityScore with realistic dimensions."""
    return QualityScore(
        total_score=total,
        grade=QualityGrade.from_score(int(total)),
        dimensions={
            QualityDimension.STRUCTURAL: _make_dimension_score(
                dimension=QualityDimension.STRUCTURAL,
                points=28.5,
                max_points=30.0,
            ),
            QualityDimension.CONTENT: _make_dimension_score(
                dimension=QualityDimension.CONTENT,
                points=46.0,
                max_points=50.0,
                checks_passed=13,
                checks_failed=2,
                checks_total=15,
            ),
            QualityDimension.ANTI_PATTERN: _make_dimension_score(
                dimension=QualityDimension.ANTI_PATTERN,
                points=17.5,
                max_points=20.0,
                checks_passed=20,
                checks_failed=2,
                checks_total=22,
            ),
        },
    )


@pytest.mark.unit
def test_quality_score_creation():
    """Verify QualityScore construction with dimension breakdown."""
    score = _make_quality_score()

    assert score.total_score == 92.0
    assert score.grade == QualityGrade.EXEMPLARY
    assert len(score.dimensions) == 3
    assert score.source_filename == "llms.txt"


@pytest.mark.unit
def test_quality_score_dimensions_accessible():
    """Verify individual dimensions are accessible by key."""
    score = _make_quality_score()

    structural = score.dimensions[QualityDimension.STRUCTURAL]
    assert structural.points == 28.5
    assert structural.max_points == 30.0

    content = score.dimensions[QualityDimension.CONTENT]
    assert content.points == 46.0

    anti = score.dimensions[QualityDimension.ANTI_PATTERN]
    assert anti.points == 17.5


@pytest.mark.unit
def test_quality_score_rejects_invalid_total():
    """Verify total_score enforces 0-100 range."""
    with pytest.raises(ValidationError):
        QualityScore(
            total_score=101,
            grade=QualityGrade.EXEMPLARY,
            dimensions={},
        )

    with pytest.raises(ValidationError):
        QualityScore(
            total_score=-1,
            grade=QualityGrade.CRITICAL,
            dimensions={},
        )


@pytest.mark.unit
def test_quality_models_importable_from_schema():
    """Exit Criterion 2: All quality models importable from public API."""
    from docstratum import schema

    assert schema.QualityDimension is QualityDimension
    assert schema.QualityGrade is QualityGrade
    assert schema.DimensionScore is DimensionScore
    assert schema.QualityScore is QualityScore
