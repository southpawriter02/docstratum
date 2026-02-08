"""Stage 5: Ecosystem Scoring — calculate aggregate health from all dimensions.

[v0.0.7] The Ecosystem Scoring stage calculates the aggregate health score for
the entire documentation ecosystem. It evaluates two primary dimensions that
can only be measured at the ecosystem level:

    Completeness (FR-081):
        What percentage of internal links (INDEXES, AGGREGATES) resolve to
        accessible, healthy files? Weighted by link importance:
            - INDEXES links (navigation → content): weight 1.0
            - AGGREGATES links (index → full): weight 1.0
            - REFERENCES links (content → content): weight 0.5

        Scoring bands:
            100% resolution → score ≥ 90
             50% resolution → score ≤ 50

    Coverage (FR-082):
        How many of the 11 canonical section categories are represented
        across the entire ecosystem (not just within the index file)?

        Scoring bands:
            11/11 categories → score ≥ 95
             8/11 categories → score ~73
             2/11 categories → score ≤ 25

The two dimensions are averaged equally (50/50 weight) to produce the
composite ecosystem score. The composite is then mapped to a QualityGrade
using the existing grade thresholds (Exemplary ≥ 90, Strong ≥ 70, etc.).

The three remaining dimensions (Consistency, Token Efficiency, Freshness)
are defined in the schema but reserved for future enhancement. They contribute
0 points in the current implementation but their slots exist in the score
model for forward compatibility.

Research basis:
    v0.0.7 §4.3  (EcosystemScore — Aggregate Health)
    v0.0.7 §7.5  (Pipeline Stage 5: Ecosystem Scoring)

Traces to:
    FR-081 (ecosystem Completeness scoring)
    FR-082 (ecosystem Coverage scoring)
"""

from __future__ import annotations

import logging
from datetime import datetime

from docstratum.schema.classification import DocumentType
from docstratum.schema.constants import CanonicalSectionName, SECTION_NAME_ALIASES
from docstratum.schema.ecosystem import (
    DocumentEcosystem,
    EcosystemFile,
    EcosystemHealthDimension,
    EcosystemScore,
    FileRelationship,
)
from docstratum.schema.parsed import LinkRelationship
from docstratum.schema.quality import (
    DimensionScore,
    QualityDimension,
    QualityGrade,
    QualityScore,
)

from docstratum.pipeline.stages import (
    PipelineContext,
    PipelineStageId,
    StageResult,
    StageStatus,
    StageTimer,
)

logger = logging.getLogger(__name__)


# ── Scoring Weights ─────────────────────────────────────────────────

# Relationship importance weights for Completeness scoring.
RELATIONSHIP_WEIGHTS: dict[LinkRelationship, float] = {
    LinkRelationship.INDEXES: 1.0,     # Primary navigation links
    LinkRelationship.AGGREGATES: 1.0,  # Aggregate inclusion links
    LinkRelationship.REFERENCES: 0.5,  # Cross-references (less critical)
    LinkRelationship.EXTERNAL: 0.0,    # External links don't affect score
    LinkRelationship.UNKNOWN: 0.0,     # Unclassified links ignored
}
"""Weight multipliers for each relationship type in Completeness scoring."""

# Dimension weights in the composite score.
COMPLETENESS_WEIGHT: float = 0.50
"""Weight of Completeness in the composite ecosystem score."""

COVERAGE_WEIGHT: float = 0.50
"""Weight of Coverage in the composite ecosystem score."""

# Total canonical section categories (constant from constants.py).
TOTAL_CANONICAL_CATEGORIES: int = 11
"""Number of canonical section categories defined in the specification."""


# ── Helper: Canonical Section Matching ──────────────────────────────


def _match_canonical_section(section_name: str) -> CanonicalSectionName | None:
    """Match a section name to a canonical section category.

    Tries exact match first, then case-insensitive match, then alias lookup.
    This is duplicated from ecosystem_validator.py to keep modules decoupled;
    a shared utility module can be introduced if more stages need it.

    Args:
        section_name: The section heading text (e.g., "API Reference").

    Returns:
        The matched CanonicalSectionName, or None if no match found.
    """
    lower = section_name.lower().strip()

    # Try direct enum match.
    for canonical in CanonicalSectionName:
        if canonical.value.lower() == lower:
            return canonical

    # Try alias lookup.
    return SECTION_NAME_ALIASES.get(lower)


# ── Completeness Scoring ────────────────────────────────────────────


def calculate_completeness(
    relationships: list[FileRelationship],
) -> DimensionScore:
    """Calculate the Completeness dimension score.

    Completeness measures what percentage of internal links resolve to
    accessible ecosystem files, weighted by link importance.

    Formula:
        completeness = (sum of weights for resolved links) / (sum of all weights)
        score = completeness * 100

    The weight for each link is determined by its relationship type:
        INDEXES: 1.0, AGGREGATES: 1.0, REFERENCES: 0.5

    If there are no scoreable relationships (all external or no links),
    Completeness defaults to 100 (nothing to break = fully complete).

    Args:
        relationships: All FileRelationship edges from the ecosystem.

    Returns:
        DimensionScore for the Completeness dimension.

    Traces to: FR-081 (ecosystem Completeness scoring)
    """
    total_weight = 0.0
    resolved_weight = 0.0
    checks_passed = 0
    checks_failed = 0

    for rel in relationships:
        weight = RELATIONSHIP_WEIGHTS.get(rel.relationship_type, 0.0)
        if weight == 0.0:
            continue  # Skip external/unknown links.

        total_weight += weight

        if rel.is_resolved:
            resolved_weight += weight
            checks_passed += 1
        else:
            checks_failed += 1

    # If no internal links exist, Completeness is perfect (vacuously true).
    if total_weight == 0.0:
        score = 100.0
    else:
        score = (resolved_weight / total_weight) * 100.0

    # Map to points: Completeness is scored out of 100 points.
    points = score
    max_points = 100.0

    return DimensionScore(
        dimension=QualityDimension.STRUCTURAL,  # Reusing closest dimension
        points=points,
        max_points=max_points,
        checks_passed=checks_passed,
        checks_failed=checks_failed,
        checks_total=checks_passed + checks_failed,
        details=[{
            "resolved_weight": round(resolved_weight, 2),
            "total_weight": round(total_weight, 2),
            "resolution_percentage": round(score, 1),
        }],
        is_gated=False,
    )


# ── Coverage Scoring ────────────────────────────────────────────────


def calculate_coverage(
    files: list[EcosystemFile],
) -> DimensionScore:
    """Calculate the Coverage dimension score.

    Coverage measures how many of the 11 canonical section categories are
    represented across ALL files in the ecosystem (not just the index).

    Formula:
        coverage = (categories_found / 11) * 100

    This score rewards breadth of documentation coverage and is independent
    of per-file quality scores (no double-counting).

    Args:
        files: All EcosystemFile objects in the ecosystem.

    Returns:
        DimensionScore for the Coverage dimension.

    Traces to: FR-082 (ecosystem Coverage scoring)
    """
    covered: set[CanonicalSectionName] = set()

    for eco_file in files:
        if eco_file.parsed is None:
            continue
        for section in eco_file.parsed.sections:
            matched = _match_canonical_section(section.name)
            if matched is not None:
                covered.add(matched)

    categories_found = len(covered)
    score = (categories_found / TOTAL_CANONICAL_CATEGORIES) * 100.0

    return DimensionScore(
        dimension=QualityDimension.CONTENT,  # Reusing closest dimension
        points=score,
        max_points=100.0,
        checks_passed=categories_found,
        checks_failed=TOTAL_CANONICAL_CATEGORIES - categories_found,
        checks_total=TOTAL_CANONICAL_CATEGORIES,
        details=[{
            "categories_found": categories_found,
            "total_categories": TOTAL_CANONICAL_CATEGORIES,
            "covered": sorted(c.value for c in covered),
            "missing": sorted(
                c.value for c in set(CanonicalSectionName) - covered
            ),
        }],
        is_gated=False,
    )


# ── Composite Scoring ───────────────────────────────────────────────


def calculate_composite_score(
    completeness: DimensionScore,
    coverage: DimensionScore,
) -> float:
    """Calculate the weighted composite ecosystem score.

    Combines Completeness and Coverage using the configured weights
    (currently 50/50).

    Args:
        completeness: The Completeness dimension score.
        coverage: The Coverage dimension score.

    Returns:
        Composite score in the range [0, 100].
    """
    weighted = (
        completeness.points * COMPLETENESS_WEIGHT
        + coverage.points * COVERAGE_WEIGHT
    )
    # Clamp to [0, 100].
    return max(0.0, min(100.0, weighted))


# ── Ecosystem Scoring Stage ─────────────────────────────────────────


class ScoringStage:
    """Stage 5: Calculate ecosystem-level health scores and assemble the final model.

    This is the terminal stage of the ecosystem pipeline. It:
        1. Calculates Completeness score from the relationship graph.
        2. Calculates Coverage score from section analysis.
        3. Combines into a composite score and grade.
        4. Builds per-file score map.
        5. Assembles the final ``DocumentEcosystem`` model.

    After this stage, ``context.ecosystem`` contains the fully populated
    top-level model ready for downstream consumers.

    Attributes:
        stage_id: Always ``PipelineStageId.SCORING``.

    Example:
        >>> stage = ScoringStage()
        >>> ctx = PipelineContext(files=[...], relationships=[...])
        >>> result = stage.execute(ctx)
        >>> ctx.ecosystem is not None
        True
        >>> ctx.ecosystem_score is not None
        True

    Traces to:
        FR-081 (Completeness scoring)
        FR-082 (Coverage scoring)
    """

    @property
    def stage_id(self) -> PipelineStageId:
        """The ordinal identifier for this stage."""
        return PipelineStageId.SCORING

    def execute(self, context: PipelineContext) -> StageResult:
        """Calculate ecosystem scores and assemble the DocumentEcosystem.

        Populates ``context.ecosystem_score`` and ``context.ecosystem``.

        Args:
            context: Pipeline context with files, relationships, and
                     diagnostics populated by Stages 1–4.

        Returns:
            StageResult with the final scoring summary.
        """
        timer = StageTimer()
        timer.start()

        logger.info(
            "Scoring stage starting: %d files, %d relationships",
            len(context.files),
            len(context.relationships),
        )

        # ── Step 1: Calculate dimension scores ─────────────────────
        completeness = calculate_completeness(context.relationships)
        coverage = calculate_coverage(context.files)

        # ── Step 2: Calculate composite score ──────────────────────
        composite = calculate_composite_score(completeness, coverage)
        grade = QualityGrade.from_score(int(composite))

        # ── Step 3: Build dimension map ────────────────────────────
        dimensions: dict[EcosystemHealthDimension, DimensionScore] = {
            EcosystemHealthDimension.COMPLETENESS: completeness,
            EcosystemHealthDimension.COVERAGE: coverage,
            # Reserved for future dimensions — not scored yet.
            # EcosystemHealthDimension.CONSISTENCY: ...,
            # EcosystemHealthDimension.TOKEN_EFFICIENCY: ...,
            # EcosystemHealthDimension.FRESHNESS: ...,
        }

        # ── Step 4: Build per-file score map ───────────────────────
        per_file_scores: dict[str, QualityScore] = {}
        for eco_file in context.files:
            if eco_file.quality is not None:
                per_file_scores[eco_file.file_id] = eco_file.quality

        # ── Step 5: Count relationship stats ───────────────────────
        broken = sum(
            1 for r in context.relationships
            if r.relationship_type != LinkRelationship.EXTERNAL
            and not r.is_resolved
        )

        # ── Step 6: Assemble EcosystemScore ────────────────────────
        ecosystem_score = EcosystemScore(
            total_score=round(composite, 1),
            grade=grade,
            dimensions=dimensions,
            per_file_scores=per_file_scores,
            file_count=len(context.files),
            relationship_count=len(context.relationships),
            broken_relationships=broken,
        )

        context.ecosystem_score = ecosystem_score

        # ── Step 7: Assemble DocumentEcosystem ─────────────────────
        # Find the root file (index).
        root_file = next(
            (f for f in context.files if f.file_type == DocumentType.TYPE_1_INDEX),
            context.files[0] if context.files else None,
        )

        if root_file is not None:
            context.ecosystem = DocumentEcosystem(
                project_name=context.project_name,
                root_file=root_file,
                files=context.files,
                relationships=context.relationships,
                ecosystem_score=ecosystem_score,
            )

        elapsed = timer.stop()

        logger.info(
            "Scoring complete: %.1f (%s), completeness=%.1f, coverage=%.1f in %.1fms",
            composite,
            grade.value,
            completeness.points,
            coverage.points,
            elapsed,
        )

        return StageResult(
            stage=self.stage_id,
            status=StageStatus.SUCCESS,
            duration_ms=elapsed,
            message=(
                f"Score: {composite:.1f} ({grade.value}), "
                f"Completeness: {completeness.points:.1f}, "
                f"Coverage: {coverage.points:.1f}"
            ),
        )
