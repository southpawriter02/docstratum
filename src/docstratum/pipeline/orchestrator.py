"""Ecosystem Pipeline Orchestrator — the 5-stage pipeline runner.

[v0.0.7] The orchestrator drives the five ecosystem pipeline stages in sequence:

    1. Discovery         → Scan project root, build file manifest
    2. Per-File          → Run L0–L4 single-file pipeline on each file
    3. Relationship      → Extract links, classify, resolve targets
    4. Ecosystem         → Cross-file validation (broken links, anti-patterns)
    5. Scoring           → Calculate Completeness + Coverage scores

Key features:
    - **Stoppable**: The ``stop_after`` parameter halts the pipeline after any
      stage, returning partial results. This supports incremental analysis
      (e.g., "just discover files" or "discover + validate, don't score").
    - **Pluggable Validator**: The ``SingleFileValidator`` protocol allows the
      per-file stage to delegate to any validator implementation. When no
      validator is provided, files are read from disk but not validated.
    - **Backward Compatible**: Single-file input (path to llms.txt) produces
      identical per-file results to running the single-file pipeline alone.
    - **Observable**: Each stage produces a ``StageResult`` with timing and
      diagnostics, stored in ``PipelineContext.stage_results``.

Entry points:
    - ``EcosystemPipeline.run(root_path)`` — Full pipeline from directory.
    - ``EcosystemPipeline.run(file_path)`` — Single-file mode.
    - ``EcosystemPipeline.run(root_path, stop_after=PipelineStageId.RELATIONSHIP)``
      — Stop after Stage 3.

Research basis:
    v0.0.7 §7 (The Ecosystem Validation Pipeline)
    v0.0.7 §10 (Migration Plan — Phase 3: Pipeline Extension)

Traces to:
    FR-084 (pipeline orchestration — stoppable after any stage)
    FR-083 (backward-compatible single-file mode)
"""

from __future__ import annotations

import logging
import time

from docstratum.schema.ecosystem import DocumentEcosystem

from docstratum.pipeline.stages import (
    PipelineContext,
    PipelineStageId,
    SingleFileValidator,
    StageResult,
    StageStatus,
    StageTimer,
)
from docstratum.pipeline.discovery import DiscoveryStage
from docstratum.pipeline.per_file import PerFileStage
from docstratum.pipeline.relationship import RelationshipStage
from docstratum.pipeline.ecosystem_validator import EcosystemValidationStage
from docstratum.pipeline.ecosystem_scorer import ScoringStage

logger = logging.getLogger(__name__)


class EcosystemPipeline:
    """Orchestrator for the 5-stage ecosystem validation pipeline.

    Executes stages in sequence, passing a shared ``PipelineContext`` through
    each. The pipeline can be stopped after any stage via ``stop_after``, and
    stage results are captured for observability.

    Construction:
        Accepts an optional ``SingleFileValidator`` for the per-file stage.
        If not provided, files are read from disk but parsing/validation/scoring
        is skipped.

    Attributes:
        validator: The optional SingleFileValidator implementation.

    Example:
        >>> pipeline = EcosystemPipeline()
        >>> result = pipeline.run("/path/to/project")
        >>> result.ecosystem is not None  # True if all stages ran
        True

    Example (stop after Discovery):
        >>> pipeline = EcosystemPipeline()
        >>> result = pipeline.run("/path/to/project", stop_after=PipelineStageId.DISCOVERY)
        >>> len(result.files) > 0  # Files discovered
        True
        >>> result.ecosystem is None  # Scoring didn't run
        True

    Traces to:
        FR-084 (pipeline orchestration)
        FR-083 (backward-compatible single-file mode)
    """

    def __init__(self, validator: SingleFileValidator | None = None) -> None:
        """Initialize the ecosystem pipeline.

        Args:
            validator: Optional SingleFileValidator implementation for the
                      per-file stage. If None, files are read from disk but
                      not validated — the schema models will have
                      ``parsed=None``, ``validation=None``, ``quality=None``.
        """
        self._validator = validator

    def run(
        self,
        root_path: str,
        stop_after: PipelineStageId | None = None,
    ) -> PipelineContext:
        """Execute the ecosystem pipeline on a project root or single file.

        Runs stages 1 through 5 (or up to ``stop_after``) in sequence.
        Each stage mutates the shared ``PipelineContext``. If any stage fails,
        subsequent stages are skipped.

        Args:
            root_path: Absolute path to the project root directory or a
                      single llms.txt file. Directory mode scans for all
                      ecosystem files; file mode wraps a single file.
            stop_after: Optional stage ID to stop after. If provided,
                       stages with higher ordinal values are skipped.
                       Example: ``PipelineStageId.RELATIONSHIP`` skips
                       Ecosystem Validation and Scoring.

        Returns:
            The completed PipelineContext containing all results accumulated
            through the executed stages. Access key fields:
                - ``.files``: Discovered ecosystem files
                - ``.relationships``: Cross-file relationships
                - ``.ecosystem_diagnostics``: Ecosystem-level diagnostics
                - ``.ecosystem_score``: Aggregate health score
                - ``.ecosystem``: Final DocumentEcosystem model
                - ``.stage_results``: Per-stage outcome records

        Traces to: FR-084 (pipeline orchestration — stoppable after any stage)
        """
        overall_timer = StageTimer()
        overall_timer.start()

        context = PipelineContext(root_path=root_path)

        logger.info(
            "Ecosystem pipeline starting: root_path=%s, stop_after=%s",
            root_path,
            stop_after.name if stop_after else "None (full run)",
        )

        # ── Build the stage sequence ───────────────────────────────
        # Stages are instantiated fresh for each run to avoid state leaks.
        per_file_stage = PerFileStage(validator=self._validator)

        stages = [
            DiscoveryStage(),
            per_file_stage,
            RelationshipStage(file_contents=per_file_stage.file_contents),
            EcosystemValidationStage(),
            ScoringStage(),
        ]

        # ── Execute stages in sequence ─────────────────────────────
        for stage in stages:
            stage_id = stage.stage_id

            # Check if we should stop before this stage.
            if stop_after is not None and stage_id > stop_after:
                # Create a SKIPPED result for this stage.
                skipped_result = StageResult(
                    stage=stage_id,
                    status=StageStatus.SKIPPED,
                    message=f"Skipped (stop_after={stop_after.name})",
                )
                context.stage_results.append(skipped_result)
                logger.info(
                    "Skipping stage %d (%s): stop_after=%s",
                    stage_id.value,
                    stage_id.name,
                    stop_after.name,
                )
                continue

            # Check if a previous stage failed.
            if context.stage_results and context.stage_results[-1].status == StageStatus.FAILED:
                skipped_result = StageResult(
                    stage=stage_id,
                    status=StageStatus.SKIPPED,
                    message="Skipped due to previous stage failure",
                )
                context.stage_results.append(skipped_result)
                logger.info(
                    "Skipping stage %d (%s): previous stage failed",
                    stage_id.value,
                    stage_id.name,
                )
                continue

            # Execute the stage.
            logger.info(
                "Executing stage %d: %s", stage_id.value, stage_id.name
            )
            try:
                result = stage.execute(context)
            except Exception as exc:
                logger.error(
                    "Stage %d (%s) raised an exception: %s",
                    stage_id.value,
                    stage_id.name,
                    exc,
                )
                result = StageResult(
                    stage=stage_id,
                    status=StageStatus.FAILED,
                    message=f"Exception: {exc}",
                )

            context.stage_results.append(result)

            logger.info(
                "Stage %d (%s) completed: status=%s, duration=%.1fms — %s",
                stage_id.value,
                stage_id.name,
                result.status.value,
                result.duration_ms,
                result.message,
            )

        # ── Pipeline summary ───────────────────────────────────────
        elapsed = overall_timer.stop()
        completed = sum(
            1 for r in context.stage_results if r.status == StageStatus.SUCCESS
        )
        failed = sum(
            1 for r in context.stage_results if r.status == StageStatus.FAILED
        )
        skipped = sum(
            1 for r in context.stage_results if r.status == StageStatus.SKIPPED
        )

        logger.info(
            "Ecosystem pipeline complete: %d succeeded, %d failed, %d skipped in %.1fms",
            completed,
            failed,
            skipped,
            elapsed,
        )

        return context
