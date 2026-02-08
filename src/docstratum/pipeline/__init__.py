"""DocStratum Ecosystem Pipeline — the 5-stage validation pipeline for AI-facing documentation.

[v0.0.7] This package implements the ecosystem validation pipeline that
extends DocStratum from single-file validation to multi-file ecosystem
analysis. The pipeline operates in five stages:

    Stage 1: Discovery        — Scan project root, build file manifest
    Stage 2: Per-File         — Run L0–L4 single-file pipeline per file
    Stage 3: Relationship     — Extract links, classify, resolve targets
    Stage 4: Ecosystem        — Cross-file validation and anti-patterns
    Stage 5: Scoring          — Calculate Completeness + Coverage scores

Public API:
    EcosystemPipeline      — The main orchestrator (use this to run the pipeline)
    PipelineContext         — The context object that flows through stages
    PipelineStageId        — Stage identifiers for stop_after control
    StageResult            — Per-stage execution outcome
    StageStatus            — Success/Failed/Skipped status enum
    SingleFileValidator    — Protocol for plugging in the L0–L4 pipeline

    Stage classes (for advanced/custom pipelines):
        DiscoveryStage
        PerFileStage
        RelationshipStage
        EcosystemValidationStage
        ScoringStage

    Utility functions:
        classify_filename          — Classify a file by name → DocumentType
        extract_links_from_content — Regex-based Markdown link extraction
        is_external_url            — Check if a URL is external
        classify_relationship      — Classify a link's relationship type
        calculate_completeness     — Score the Completeness dimension
        calculate_coverage         — Score the Coverage dimension

Example:
    >>> from docstratum.pipeline import EcosystemPipeline, PipelineStageId
    >>> pipeline = EcosystemPipeline()
    >>> result = pipeline.run("/path/to/project")
    >>> result.ecosystem.file_count
    5
    >>> result.ecosystem_score.total_score
    82.5

Example (stop after discovery):
    >>> result = pipeline.run("/path/to/project", stop_after=PipelineStageId.DISCOVERY)
    >>> len(result.files)
    5
    >>> result.ecosystem is None  # Scoring didn't run
    True

Research basis:
    v0.0.7 §7 (The Ecosystem Validation Pipeline)

Traces to:
    FR-074 through FR-084 (ecosystem pipeline requirements)
"""

# ── Core pipeline infrastructure ────────────────────────────────────
from docstratum.pipeline.stages import (
    PipelineContext,
    PipelineStage,
    PipelineStageId,
    SingleFileValidator,
    StageResult,
    StageStatus,
    StageTimer,
)

# ── Stage implementations ───────────────────────────────────────────
from docstratum.pipeline.discovery import (
    DiscoveryStage,
    classify_filename,
)
from docstratum.pipeline.per_file import PerFileStage
from docstratum.pipeline.relationship import (
    RelationshipStage,
    classify_relationship,
    extract_links_from_content,
    is_external_url,
)
from docstratum.pipeline.ecosystem_validator import EcosystemValidationStage
from docstratum.pipeline.ecosystem_scorer import (
    ScoringStage,
    calculate_completeness,
    calculate_coverage,
)

# ── Orchestrator ────────────────────────────────────────────────────
from docstratum.pipeline.orchestrator import EcosystemPipeline

__all__ = [
    # Infrastructure
    "PipelineContext",
    "PipelineStage",
    "PipelineStageId",
    "SingleFileValidator",
    "StageResult",
    "StageStatus",
    "StageTimer",
    # Stages
    "DiscoveryStage",
    "PerFileStage",
    "RelationshipStage",
    "EcosystemValidationStage",
    "ScoringStage",
    # Orchestrator
    "EcosystemPipeline",
    # Utility functions
    "classify_filename",
    "classify_relationship",
    "extract_links_from_content",
    "is_external_url",
    "calculate_completeness",
    "calculate_coverage",
]
