"""Ecosystem-level models for the DocStratum validation engine.

[v0.0.7] These models represent the documentation ecosystem — the complete
set of AI-facing documentation files that a project publishes. Where the
single-file models (parsed.py, validation.py, quality.py) represent individual
files, these models represent the *relationships between files* and the
*aggregate health* of the documentation system as a whole.

The ecosystem has three layers:
    Navigation:  llms.txt — the index and entry point for AI agents
    Content:     Individual .md pages — detailed topic documentation
    Aggregate:   llms-full.txt — everything in one file for large-window models

Model hierarchy:
    DocumentEcosystem (top-level)
        ├── root_file: EcosystemFile (the llms.txt index)
        ├── files: list[EcosystemFile] (all ecosystem files)
        │   └── Each EcosystemFile wraps:
        │       ├── parsed: ParsedLlmsTxt (existing parser output)
        │       ├── validation: ValidationResult (existing per-file validation)
        │       ├── quality: QualityScore (existing per-file quality)
        │       └── relationships: list[FileRelationship]
        ├── relationships: list[FileRelationship] (all cross-file links)
        └── ecosystem_score: EcosystemScore (aggregate health)
            └── dimensions: dict[EcosystemHealthDimension, DimensionScore]

Research basis:
    v0.0.7 §3 (The Ecosystem Model)
    v0.0.7 §4.3 (New Schema Entities)
    v0.0.7 §7 (The Ecosystem Validation Pipeline)

Traces to:
    FR-069 (DocumentEcosystem model)
    FR-070 (EcosystemFile model)
    FR-071 (FileRelationship model)
    FR-072 (EcosystemScore model)
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from docstratum.schema.classification import DocumentClassification, DocumentType
from docstratum.schema.parsed import LinkRelationship, ParsedLlmsTxt
from docstratum.schema.quality import DimensionScore, QualityGrade, QualityScore
from docstratum.schema.validation import ValidationResult

logger = logging.getLogger(__name__)


# ── Helper: UUID Generation ──────────────────────────────────────────
# EcosystemFile and DocumentEcosystem use UUIDs for cross-referencing.
# Generating at construction time avoids requiring callers to manage IDs.


def _generate_uuid() -> str:
    """Generate a new UUID4 string for ecosystem entity identification.

    Returns:
        A string representation of a new UUID4 (e.g., "f47ac10b-58cc-...").
    """
    return str(uuid.uuid4())


# ── EcosystemHealthDimension ─────────────────────────────────────────
# The five dimensions of ecosystem-level quality assessment.


class EcosystemHealthDimension(StrEnum):
    """Dimensions of ecosystem-level quality.

    These dimensions measure properties that *only exist at the ecosystem level*
    — they cannot be assessed by looking at a single file in isolation. Each
    dimension contributes independently to the ``EcosystemScore`` composite.

    Attributes:
        COVERAGE: Does the ecosystem cover all necessary documentation areas?
                  Measured as the proportion of the 11 canonical section
                  categories represented across all ecosystem files.
        CONSISTENCY: Do files agree with each other on project name, version,
                     and terminology? Detects W015/W016 inconsistencies.
        COMPLETENESS: Does every promise (link) in the index lead to accessible,
                      healthy content? Measured as the resolution rate of
                      INDEXES and AGGREGATES relationships.
        TOKEN_EFFICIENCY: Is content distributed optimally across files, or is
                          everything crammed into one file? Detects W018
                          unbalanced distribution and AP_ECO_005 Token Black Hole.
        FRESHNESS: Are all files in sync version-wise? Detects W016
                   inconsistent versioning across ecosystem files.

    Example:
        >>> EcosystemHealthDimension.COMPLETENESS
        <EcosystemHealthDimension.COMPLETENESS: 'completeness'>

    Traces to: FR-072, v0.0.7 §4.3 (EcosystemScore — Aggregate Health)
    """

    COVERAGE = "coverage"
    CONSISTENCY = "consistency"
    COMPLETENESS = "completeness"
    TOKEN_EFFICIENCY = "token_efficiency"
    FRESHNESS = "freshness"


# ── FileRelationship ─────────────────────────────────────────────────
# Represents a directed edge in the ecosystem relationship graph.


class FileRelationship(BaseModel):
    """A directed relationship between two files in the documentation ecosystem.

    Relationships are the core of ecosystem validation. A link in llms.txt that
    points to ``docs/api-reference.md`` creates an INDEXES relationship. The
    ecosystem validator checks whether that relationship is *resolved* (the
    target file exists and is accessible) and whether the target file is
    *healthy* (it passes its own per-file validation).

    The relationship graph is built during the Relationship Mapping stage
    (Stage 3 of the ecosystem pipeline) and used during Ecosystem Validation
    (Stage 4) and Ecosystem Scoring (Stage 5).

    Attributes:
        source_file_id: UUID of the file containing the link/reference.
        target_file_id: UUID of the file being referenced, or empty string
                        if the target could not be identified (unresolved).
        relationship_type: The type of relationship (INDEXES, AGGREGATES,
                           REFERENCES, EXTERNAL, UNKNOWN). Uses
                           ``LinkRelationship`` enum from ``parsed.py``.
        source_line: Line number in the source file where the relationship
                     is declared (the link's location). None if not applicable.
        target_url: The URL or path string used to reference the target. This
                    is the raw URL from the ``ParsedLink``, before resolution.
        is_resolved: Whether the target file was found and is accessible within
                     the ecosystem. False for broken links, external links, or
                     unresolved references.

    Example:
        >>> rel = FileRelationship(
        ...     source_file_id="abc-123",
        ...     target_file_id="def-456",
        ...     relationship_type=LinkRelationship.INDEXES,
        ...     source_line=5,
        ...     target_url="docs/api-reference.md",
        ...     is_resolved=True,
        ... )
        >>> rel.is_resolved
        True

    Traces to: FR-071, v0.0.7 §4.3 (FileRelationship — How Two Files Connect)
    """

    source_file_id: str = Field(
        description="UUID of the file containing the link/reference.",
    )
    target_file_id: str = Field(
        default="",
        description=(
            "UUID of the referenced file. Empty string when the target "
            "could not be identified (e.g., broken link, external URL)."
        ),
    )
    relationship_type: LinkRelationship = Field(
        description=(
            "Type of relationship: INDEXES (index → content page), "
            "REFERENCES (page → page), EXTERNAL (link to outside ecosystem), "
            "or UNKNOWN (not yet classified)."
        ),
    )
    source_line: int | None = Field(
        default=None,
        ge=1,
        description=(
            "Line number in the source file where the relationship is "
            "declared. None if not applicable."
        ),
    )
    target_url: str = Field(
        description=(
            "The raw URL/path string used to reference the target. "
            "This is the URL from the ParsedLink before resolution."
        ),
    )
    is_resolved: bool = Field(
        default=False,
        description=(
            "Whether the target file was found and is accessible. "
            "False for broken links, external links, or unresolved refs."
        ),
    )


# ── EcosystemFile ────────────────────────────────────────────────────
# Wraps an existing parsed file with ecosystem-level metadata.


class EcosystemFile(BaseModel):
    """A single file within a documentation ecosystem.

    This model is the bridge between the single-file pipeline and the ecosystem
    pipeline. It wraps an existing ``ParsedLlmsTxt`` (the parser output) with
    ecosystem-level metadata: a unique ID for cross-referencing, the file's role
    in the ecosystem (its ``DocumentType``), its per-file validation and quality
    results, and its relationships to other files.

    Each ``EcosystemFile`` gets its own ``ValidationResult`` and ``QualityScore``
    from the existing single-file pipeline (unchanged). The ecosystem pipeline
    *adds* the relationship list and uses the per-file results as inputs to the
    aggregate ``EcosystemScore``.

    Attributes:
        file_id: Unique identifier (UUID4) for cross-referencing within the
                 ecosystem. Generated automatically at construction time.
        file_path: Relative path from the project root (e.g., "docs/api.md").
        file_type: Document type classification (TYPE_1_INDEX, TYPE_2_FULL,
                   TYPE_3_CONTENT_PAGE, TYPE_4_INSTRUCTIONS, or UNKNOWN).
        classification: Full classification result (size, tier, etc.).
                        None if classification hasn't run yet.
        parsed: Parsed content from the single-file parser. None if the file
                couldn't be parsed (e.g., binary file, encoding error).
        validation: Per-file validation results from the L0–L4 pipeline.
                    None if validation hasn't run yet.
        quality: Per-file quality score. None if scoring hasn't run yet.
        relationships: Directed relationships from this file to other
                       ecosystem files. Populated during Relationship Mapping.

    Example:
        >>> eco_file = EcosystemFile(
        ...     file_path="llms.txt",
        ...     file_type=DocumentType.TYPE_1_INDEX,
        ... )
        >>> eco_file.file_id  # auto-generated UUID
        'f47ac10b-58cc-...'

    Traces to: FR-070, v0.0.7 §4.3 (EcosystemFile — File Within the Ecosystem)
    """

    file_id: str = Field(
        default_factory=_generate_uuid,
        description="Unique UUID4 identifier for cross-referencing.",
    )
    file_path: str = Field(
        description="Relative path from the project root (e.g., 'docs/api.md').",
    )
    file_type: DocumentType = Field(
        default=DocumentType.UNKNOWN,
        description="Document type (TYPE_1_INDEX, TYPE_2_FULL, etc.).",
    )
    classification: DocumentClassification | None = Field(
        default=None,
        description="Full classification result. None before classification.",
    )
    parsed: ParsedLlmsTxt | None = Field(
        default=None,
        description="Parsed content. None if parsing failed or hasn't run.",
    )
    validation: ValidationResult | None = Field(
        default=None,
        description="Per-file validation results. None before validation.",
    )
    quality: QualityScore | None = Field(
        default=None,
        description="Per-file quality score. None before scoring.",
    )
    relationships: list[FileRelationship] = Field(
        default_factory=list,
        description=(
            "Directed relationships from this file to other ecosystem files. "
            "Populated during the Relationship Mapping stage."
        ),
    )


# ── EcosystemScore ───────────────────────────────────────────────────
# Aggregate quality score for the entire documentation ecosystem.


class EcosystemScore(BaseModel):
    """Aggregate quality score for the entire documentation ecosystem.

    The ecosystem score is *not* an average of per-file scores. It measures
    properties that only exist at the ecosystem level: coverage (are all
    documentation areas represented?), consistency (do files agree on project
    name, terminology, versioning?), completeness (does every link in the
    index lead to actual content?), token efficiency (is content distributed
    well across files?), and freshness (are all files up to date?).

    The composite score uses the same 0–100 scale and ``QualityGrade`` enum
    as per-file quality scores, enabling consistent reporting across both
    individual files and the ecosystem as a whole.

    Attributes:
        total_score: Composite ecosystem health score (0–100).
        grade: Quality grade (Exemplary, Strong, Adequate, Needs Work, Critical).
               Reuses the existing ``QualityGrade`` enum and thresholds.
        dimensions: Per-dimension score breakdown. Each ``EcosystemHealthDimension``
                    maps to a ``DimensionScore`` (reusing the existing model).
        per_file_scores: Map of file_id → per-file ``QualityScore``. Provides
                         drill-down from ecosystem to individual file quality.
        file_count: Total number of files in the ecosystem.
        relationship_count: Total number of relationships (edges in the graph).
        broken_relationships: Count of relationships where ``is_resolved`` is
                              False. Used to calculate the Completeness dimension.
        scored_at: Timestamp when ecosystem scoring was performed.

    Example:
        >>> score = EcosystemScore(
        ...     total_score=78.5,
        ...     grade=QualityGrade.STRONG,
        ...     dimensions={},
        ...     per_file_scores={},
        ...     file_count=5,
        ...     relationship_count=12,
        ...     broken_relationships=2,
        ... )
        >>> score.grade
        <QualityGrade.STRONG: 'strong'>

    Traces to: FR-072, v0.0.7 §4.3 (EcosystemScore — Aggregate Health)
    """

    total_score: float = Field(
        ge=0,
        le=100,
        description="Composite ecosystem health score (0–100).",
    )
    grade: QualityGrade = Field(
        description="Quality grade derived from total_score.",
    )
    dimensions: dict[EcosystemHealthDimension, DimensionScore] = Field(
        default_factory=dict,
        description="Per-dimension score breakdown.",
    )
    per_file_scores: dict[str, QualityScore] = Field(
        default_factory=dict,
        description="Map of file_id → per-file QualityScore for drill-down.",
    )
    file_count: int = Field(
        ge=0,
        description="Total number of files in the ecosystem.",
    )
    relationship_count: int = Field(
        ge=0,
        description="Total number of cross-file relationships.",
    )
    broken_relationships: int = Field(
        ge=0,
        description="Count of unresolved relationships (is_resolved == False).",
    )
    scored_at: datetime = Field(
        default_factory=datetime.now,
        description="When ecosystem scoring was performed.",
    )

    @property
    def resolution_rate(self) -> float:
        """Percentage of relationships that resolved successfully.

        Returns 100.0 when there are no relationships (vacuous truth).

        Returns:
            A float in the range [0.0, 100.0].
        """
        if self.relationship_count == 0:
            return 100.0
        resolved = self.relationship_count - self.broken_relationships
        return (resolved / self.relationship_count) * 100


# ── DocumentEcosystem ────────────────────────────────────────────────
# The top-level entity representing a complete documentation ecosystem.


class DocumentEcosystem(BaseModel):
    """A complete AI-ready documentation ecosystem for a project.

    This is the new top-level entity introduced by the v0.0.7 ecosystem pivot.
    Where ``ParsedLlmsTxt`` was the root of the single-file world,
    ``DocumentEcosystem`` is the root of the ecosystem world. It contains
    all discovered files, all cross-file relationships, and the aggregate
    ecosystem health score.

    The single-file pipeline runs *within* this structure — each
    ``EcosystemFile`` gets its own ``ValidationResult`` and ``QualityScore``.
    The ecosystem pipeline then layers cross-file validation and aggregate
    scoring on top.

    For single-file mode (FR-083), the ecosystem contains exactly one file
    (the llms.txt), zero internal relationships, and emits an I010 diagnostic.

    Attributes:
        ecosystem_id: Unique identifier (UUID4) for this ecosystem scan.
        project_name: Project name extracted from the llms.txt H1 title.
                      Defaults to "Unknown Project" if the title is absent.
        root_file: The llms.txt index file (required). This is always the
                   first file discovered and the ecosystem's entry point.
        files: All files in the ecosystem, including the root file. The root
               file is *also* included in this list for uniform iteration.
        relationships: All directed cross-file relationships. Built during
                       the Relationship Mapping stage.
        ecosystem_score: Aggregate health score. None before the Ecosystem
                         Scoring stage has run.
        discovered_at: Timestamp when the ecosystem was first scanned.

    Example:
        >>> eco = DocumentEcosystem(
        ...     project_name="Stripe",
        ...     root_file=EcosystemFile(
        ...         file_path="llms.txt",
        ...         file_type=DocumentType.TYPE_1_INDEX,
        ...     ),
        ...     files=[...],
        ... )
        >>> eco.file_count
        5

    Traces to: FR-069, v0.0.7 §4.3 (DocumentEcosystem — The Top-Level Entity)
    """

    ecosystem_id: str = Field(
        default_factory=_generate_uuid,
        description="Unique UUID4 identifier for this ecosystem scan.",
    )
    project_name: str = Field(
        default="Unknown Project",
        description=(
            "Project name from the llms.txt H1 title. "
            "Defaults to 'Unknown Project' if the title is absent."
        ),
    )
    root_file: EcosystemFile = Field(
        description="The llms.txt index file (required ecosystem entry point).",
    )
    files: list[EcosystemFile] = Field(
        default_factory=list,
        description=(
            "All files in the ecosystem (including root_file). "
            "Populated during the Discovery stage."
        ),
    )
    relationships: list[FileRelationship] = Field(
        default_factory=list,
        description=(
            "All directed cross-file relationships. "
            "Populated during the Relationship Mapping stage."
        ),
    )
    ecosystem_score: EcosystemScore | None = Field(
        default=None,
        description=(
            "Aggregate ecosystem health score. "
            "None before the Ecosystem Scoring stage."
        ),
    )
    discovered_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when the ecosystem was first scanned.",
    )

    # ── Computed Properties ──────────────────────────────────────────

    @property
    def file_count(self) -> int:
        """Total number of files in the ecosystem.

        Returns:
            The length of the ``files`` list.
        """
        return len(self.files)

    @property
    def index_file(self) -> EcosystemFile:
        """The llms.txt index file (alias for root_file).

        Returns:
            The ``root_file`` EcosystemFile instance.
        """
        return self.root_file

    @property
    def aggregate_file(self) -> EcosystemFile | None:
        """The llms-full.txt aggregate file, if present in the ecosystem.

        Returns:
            The first ``EcosystemFile`` with type TYPE_2_FULL, or None.
        """
        return next(
            (f for f in self.files if f.file_type == DocumentType.TYPE_2_FULL),
            None,
        )

    @property
    def content_pages(self) -> list[EcosystemFile]:
        """All individual content pages (TYPE_3_CONTENT_PAGE) in the ecosystem.

        Returns:
            A list of EcosystemFile instances classified as content pages.
        """
        return [
            f for f in self.files
            if f.file_type == DocumentType.TYPE_3_CONTENT_PAGE
        ]

    @property
    def instruction_file(self) -> EcosystemFile | None:
        """The llms-instructions.txt file, if present in the ecosystem.

        Returns:
            The first ``EcosystemFile`` with type TYPE_4_INSTRUCTIONS, or None.
        """
        return next(
            (f for f in self.files if f.file_type == DocumentType.TYPE_4_INSTRUCTIONS),
            None,
        )

    @property
    def is_single_file(self) -> bool:
        """Whether this ecosystem consists of only the index file.

        Single-file ecosystems emit I010 (ECOSYSTEM_SINGLE_FILE) during
        ecosystem validation. They are valid but limited.

        Returns:
            True if the ecosystem has exactly one file (the root).
        """
        return len(self.files) <= 1

    @property
    def resolved_relationship_count(self) -> int:
        """Count of relationships that resolved successfully.

        Returns:
            Number of FileRelationship entries where is_resolved is True.
        """
        return sum(1 for r in self.relationships if r.is_resolved)

    @property
    def broken_relationship_count(self) -> int:
        """Count of relationships that failed to resolve.

        Returns:
            Number of FileRelationship entries where is_resolved is False.
        """
        return sum(1 for r in self.relationships if not r.is_resolved)
