"""Pipeline stage contracts and shared context for the DocStratum ecosystem pipeline.

[v0.0.7] This module defines the foundational types that all five pipeline stages
share: the ``PipelineStage`` protocol (the interface every stage implements), the
``PipelineContext`` (the mutable state bag that flows through stages), and the
``StageResult`` (the typed outcome of executing a single stage).

Stage contract:
    Every stage receives a ``PipelineContext``, mutates it in place, and returns
    a ``StageResult`` describing what happened. The orchestrator (``orchestrator.py``)
    drives stage execution in sequence and can stop after any stage.

The five stages are:
    1. Discovery       — Scan project root, build file manifest
    2. Per-File        — Run L0–L4 single-file pipeline on each file
    3. Relationship    — Extract links, classify relationships, resolve targets
    4. Ecosystem       — Cross-file validation (broken links, consistency, anti-patterns)
    5. Scoring         — Calculate ecosystem-level Completeness + Coverage scores

Design decisions:
    - ``Protocol`` (not ABC) for ``PipelineStage``: stages are duck-typed, which
      allows third-party stages without inheritance coupling.
    - ``PipelineContext`` is a Pydantic model, not a dict: typed fields prevent
      the "stringly-typed context bag" anti-pattern.
    - ``StageResult`` captures duration and diagnostics for observability.
    - ``SingleFileValidator`` is a Protocol for the as-yet-unimplemented L0–L4
      pipeline. When the parser/validator are built in later phases, they just
      need to implement this interface — no changes to pipeline code required.

Research basis:
    v0.0.7 §7   (The Ecosystem Validation Pipeline)
    v0.0.7 §10  (Migration Plan — Phase 3: Pipeline Extension)

Traces to:
    FR-084 (pipeline orchestration — stoppable after any stage)
    FR-080 (per-file validation — pluggable SingleFileValidator)
    FR-083 (backward compatibility — single-file mode)
"""

from __future__ import annotations

import logging
import time
from enum import IntEnum, StrEnum
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, Field

from docstratum.schema.classification import DocumentClassification
from docstratum.schema.diagnostics import DiagnosticCode
from docstratum.schema.ecosystem import (
    DocumentEcosystem,
    EcosystemFile,
    EcosystemScore,
    FileRelationship,
)
from docstratum.schema.parsed import ParsedLlmsTxt
from docstratum.schema.quality import QualityScore
from docstratum.schema.validation import ValidationDiagnostic, ValidationResult

logger = logging.getLogger(__name__)


# ── Pipeline Stage Enumeration ──────────────────────────────────────
# Identifies each stage by name and ordinal for logging and stop-after.


class PipelineStageId(IntEnum):
    """Ordinal identifiers for the five ecosystem pipeline stages.

    The integer values define execution order. The orchestrator uses these
    to implement the ``stop_after`` parameter: if ``stop_after=RELATIONSHIP``,
    stages 4 (ECOSYSTEM_VALIDATION) and 5 (SCORING) are skipped.

    Attributes:
        DISCOVERY: Stage 1 — Scan project root, build file manifest.
        PER_FILE: Stage 2 — Run L0–L4 single-file pipeline on each file.
        RELATIONSHIP: Stage 3 — Extract links, classify, resolve targets.
        ECOSYSTEM_VALIDATION: Stage 4 — Cross-file checks and anti-patterns.
        SCORING: Stage 5 — Calculate ecosystem Completeness + Coverage scores.

    Traces to: FR-084 (pipeline orchestration)
    """

    DISCOVERY = 1
    PER_FILE = 2
    RELATIONSHIP = 3
    ECOSYSTEM_VALIDATION = 4
    SCORING = 5


class StageStatus(StrEnum):
    """Outcome status for a completed pipeline stage.

    Attributes:
        SUCCESS: Stage completed without errors. Warnings are allowed.
        FAILED: Stage encountered a fatal error and cannot continue.
                The orchestrator will halt the pipeline.
        SKIPPED: Stage was not executed (e.g., stop_after was reached,
                 or a required dependency stage failed).
    """

    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


# ── Stage Result ────────────────────────────────────────────────────
# Every stage returns one of these after execution.


class StageResult(BaseModel):
    """Typed outcome of executing a single pipeline stage.

    The orchestrator inspects ``status`` after each stage to decide whether
    to continue, halt, or skip remaining stages. Duration and diagnostics
    are captured for observability and debugging.

    Attributes:
        stage: Which pipeline stage produced this result.
        status: Whether the stage succeeded, failed, or was skipped.
        diagnostics: Ecosystem-level diagnostics emitted by this stage.
                     Per-file diagnostics live in each EcosystemFile's
                     ``validation`` field, not here.
        duration_ms: Wall-clock execution time in milliseconds.
        message: Human-readable summary of what happened (for logging).

    Example:
        >>> result = StageResult(
        ...     stage=PipelineStageId.DISCOVERY,
        ...     status=StageStatus.SUCCESS,
        ...     message="Discovered 5 files in /project/docs",
        ... )
        >>> result.status == StageStatus.SUCCESS
        True

    Traces to: FR-084 (pipeline orchestration — typed intermediate results)
    """

    stage: PipelineStageId = Field(
        description="Which pipeline stage produced this result."
    )
    status: StageStatus = Field(
        description="Outcome status: success, failed, or skipped."
    )
    diagnostics: list[ValidationDiagnostic] = Field(
        default_factory=list,
        description="Ecosystem-level diagnostics emitted by this stage.",
    )
    duration_ms: float = Field(
        default=0.0,
        ge=0,
        description="Wall-clock execution time in milliseconds.",
    )
    message: str = Field(
        default="",
        description="Human-readable summary for logging.",
    )


# ── Pipeline Context ────────────────────────────────────────────────
# The mutable state bag that flows through all five stages.


class PipelineContext(BaseModel):
    """Mutable context passed through all five pipeline stages.

    Each stage reads from and writes to this context. The context accumulates
    state as the pipeline progresses:

        After Stage 1 (Discovery):
            - ``root_path`` is set
            - ``files`` contains unvalidated EcosystemFile entries
        After Stage 2 (Per-File):
            - Each file in ``files`` has ``.parsed``, ``.validation``, ``.quality``
        After Stage 3 (Relationship):
            - ``relationships`` contains all cross-file edges
            - Each file's ``.relationships`` list is populated
        After Stage 4 (Ecosystem Validation):
            - ``ecosystem_diagnostics`` contains cross-file diagnostic codes
        After Stage 5 (Scoring):
            - ``ecosystem_score`` is populated
            - ``ecosystem`` is the final assembled DocumentEcosystem

    Attributes:
        root_path: Absolute path to the project root directory being scanned.
                   For single-file mode, this is the directory containing the
                   llms.txt file.
        files: Discovered ecosystem files. Populated by Stage 1, enriched by
               Stage 2 with per-file results.
        relationships: All cross-file link relationships. Populated by Stage 3.
        ecosystem_diagnostics: Ecosystem-level diagnostics from Stage 4.
                               Separate from per-file diagnostics.
        ecosystem_score: Aggregate health score from Stage 5.
        ecosystem: The final assembled DocumentEcosystem model. Built in
                   Stage 5 from all accumulated context.
        stage_results: Results from each completed stage, for introspection.
        project_name: Project name extracted from llms.txt H1 title. Set
                      during Stage 1 or Stage 2.

    Traces to: FR-084 (typed intermediate results available after each stage)
    """

    root_path: str = Field(
        default="",
        description="Absolute path to the project root directory.",
    )
    files: list[EcosystemFile] = Field(
        default_factory=list,
        description="Discovered ecosystem files.",
    )
    relationships: list[FileRelationship] = Field(
        default_factory=list,
        description="All cross-file link relationships.",
    )
    ecosystem_diagnostics: list[ValidationDiagnostic] = Field(
        default_factory=list,
        description="Ecosystem-level diagnostics from cross-file validation.",
    )
    ecosystem_score: EcosystemScore | None = Field(
        default=None,
        description="Aggregate ecosystem health score.",
    )
    ecosystem: DocumentEcosystem | None = Field(
        default=None,
        description="The final assembled DocumentEcosystem.",
    )
    stage_results: list[StageResult] = Field(
        default_factory=list,
        description="Results from each completed stage.",
    )
    project_name: str = Field(
        default="Unknown Project",
        description="Project name from llms.txt H1 title.",
    )


# ── Pipeline Stage Protocol ─────────────────────────────────────────
# Every stage implements this interface. The orchestrator iterates over
# a list of PipelineStage objects and calls execute() on each.


@runtime_checkable
class PipelineStage(Protocol):
    """Interface that every pipeline stage must implement.

    Stages are duck-typed via ``Protocol``: any class with a matching
    ``stage_id`` property and ``execute()`` method satisfies this contract.
    No inheritance required.

    The orchestrator calls ``execute(context)`` and inspects the returned
    ``StageResult`` to decide whether to continue.

    Example:
        >>> class MyStage:
        ...     @property
        ...     def stage_id(self) -> PipelineStageId:
        ...         return PipelineStageId.DISCOVERY
        ...     def execute(self, context: PipelineContext) -> StageResult:
        ...         # ... do work, mutate context ...
        ...         return StageResult(
        ...             stage=self.stage_id,
        ...             status=StageStatus.SUCCESS,
        ...         )

    Traces to: FR-084 (pipeline orchestration — each stage produces typed results)
    """

    @property
    def stage_id(self) -> PipelineStageId:
        """The ordinal identifier for this stage."""
        ...

    def execute(self, context: PipelineContext) -> StageResult:
        """Execute this stage, mutating context in place.

        Args:
            context: The mutable pipeline context. Read inputs from it,
                     write outputs back to it.

        Returns:
            A StageResult describing the outcome.
        """
        ...


# ── Single-File Validator Protocol ──────────────────────────────────
# Defines the interface for the L0–L4 single-file pipeline that will
# be built in later phases. The Per-File stage (Stage 2) delegates to
# an object implementing this protocol.


@runtime_checkable
class SingleFileValidator(Protocol):
    """Interface for the L0–L4 single-file validation pipeline.

    This protocol defines what the Per-File Validation stage (Stage 2)
    expects from the underlying single-file pipeline. When the parser
    and validator are implemented in later phases, they implement this
    interface — no changes to pipeline code are needed.

    The four methods correspond to the four conceptual steps of the
    single-file pipeline: Parse → Classify → Validate → Score.

    Example:
        >>> class MyValidator:
        ...     def parse(self, content: str, filename: str) -> ParsedLlmsTxt: ...
        ...     def classify(self, parsed: ParsedLlmsTxt) -> DocumentClassification: ...
        ...     def validate(self, parsed: ParsedLlmsTxt, classification: DocumentClassification) -> ValidationResult: ...
        ...     def score(self, result: ValidationResult) -> QualityScore: ...

    Traces to: FR-080 (per-file validation within ecosystem)
    """

    def parse(self, content: str, filename: str) -> ParsedLlmsTxt:
        """Parse raw file content into a structured model.

        Args:
            content: Raw text content of the file.
            filename: The file's name (e.g., "llms.txt").

        Returns:
            Parsed representation of the file.
        """
        ...

    def classify(self, parsed: ParsedLlmsTxt) -> DocumentClassification:
        """Classify a parsed file by type and size.

        Args:
            parsed: The parsed file content.

        Returns:
            Classification with document type and size tier.
        """
        ...

    def validate(
        self,
        parsed: ParsedLlmsTxt,
        classification: DocumentClassification,
    ) -> ValidationResult:
        """Run L0–L4 validation on a parsed file.

        Args:
            parsed: The parsed file content.
            classification: The file's type/size classification.

        Returns:
            Validation result with diagnostic codes and level achieved.
        """
        ...

    def score(self, result: ValidationResult) -> QualityScore:
        """Calculate the quality score from validation results.

        Args:
            result: The validation result to score.

        Returns:
            Quality score with per-dimension breakdown and grade.
        """
        ...


# ── Timer Helper ────────────────────────────────────────────────────
# Utility for measuring stage execution time.


class StageTimer:
    """Simple wall-clock timer for measuring stage execution duration.

    Usage:
        >>> timer = StageTimer()
        >>> timer.start()
        >>> # ... do work ...
        >>> elapsed = timer.stop()
        >>> elapsed > 0
        True
    """

    def __init__(self) -> None:
        self._start: float = 0.0
        self._elapsed_ms: float = 0.0

    def start(self) -> None:
        """Record the start time."""
        self._start = time.perf_counter()

    def stop(self) -> float:
        """Record the stop time and return elapsed milliseconds.

        Returns:
            Elapsed time in milliseconds since ``start()`` was called.
        """
        self._elapsed_ms = (time.perf_counter() - self._start) * 1000.0
        return self._elapsed_ms

    @property
    def elapsed_ms(self) -> float:
        """The most recently measured elapsed time in milliseconds."""
        return self._elapsed_ms
