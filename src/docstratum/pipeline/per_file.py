"""Stage 2: Per-File Validation — run L0–L4 single-file pipeline on each file.

[v0.0.7] The Per-File Validation stage iterates over every file discovered in
Stage 1 and runs the existing single-file pipeline on each: Parse → Classify →
Validate → Score. The results are stored in each ``EcosystemFile``'s ``.parsed``,
``.validation``, and ``.quality`` fields.

The actual L0–L4 validation logic is NOT implemented in this module — that will
be built in a later phase. Instead, this stage delegates to a pluggable
``SingleFileValidator`` implementation. If no validator is provided, the stage
reads each file's raw content and stores it for later processing, but skips
the parse/validate/score steps.

Backward compatibility guarantee (FR-083):
    When a ``SingleFileValidator`` is provided, the per-file results MUST be
    byte-identical to running the single-file pipeline in isolation. The
    ecosystem wrapper is transparent — it doesn't alter per-file behavior.

Read strategy:
    Each file is read from disk using its ``file_path`` from the EcosystemFile
    created by Stage 1. The raw content is stored as ``_raw_content`` on the
    context for Stage 3 (Relationship Mapping) to use for link extraction.

Research basis:
    v0.0.7 §7.2  (Pipeline Stage 2: Per-File Validation)

Traces to:
    FR-080 (per-file validation within ecosystem)
    FR-083 (backward-compatible single-file mode)
"""

from __future__ import annotations

import logging
from pathlib import Path

from docstratum.schema.classification import DocumentType
from docstratum.schema.ecosystem import EcosystemFile

from docstratum.pipeline.stages import (
    PipelineContext,
    PipelineStageId,
    SingleFileValidator,
    StageResult,
    StageStatus,
    StageTimer,
)

logger = logging.getLogger(__name__)


class PerFileStage:
    """Stage 2: Run the single-file validation pipeline on each ecosystem file.

    This stage wraps the existing L0–L4 pipeline, running it once per file
    discovered in Stage 1. It's designed as a thin delegation layer: the
    actual validation logic lives in a ``SingleFileValidator`` implementation
    that is injected at construction time.

    If no validator is provided, the stage still reads each file's raw content
    from disk and stores it in the context's ``file_contents`` dict. This
    allows downstream stages (especially Stage 3: Relationship Mapping) to
    access file content without re-reading from disk.

    Attributes:
        stage_id: Always ``PipelineStageId.PER_FILE``.
        validator: The injected SingleFileValidator, or None if not available.

    Example:
        >>> stage = PerFileStage()  # No validator — read-only mode
        >>> ctx = PipelineContext(root_path="/project", files=[...])
        >>> result = stage.execute(ctx)
        >>> result.status == StageStatus.SUCCESS
        True

    Traces to:
        FR-080 (per-file validation within ecosystem)
        FR-083 (byte-identical results in single-file mode)
    """

    def __init__(self, validator: SingleFileValidator | None = None) -> None:
        """Initialize the Per-File Validation stage.

        Args:
            validator: An optional SingleFileValidator implementation.
                       If provided, each file is parsed, classified,
                       validated, and scored. If None, files are only
                       read from disk (content stored for later stages).
        """
        self._validator = validator
        # Internal storage for raw file contents, keyed by file_id.
        # Downstream stages can access this via the stage instance.
        self.file_contents: dict[str, str] = {}

    @property
    def stage_id(self) -> PipelineStageId:
        """The ordinal identifier for this stage."""
        return PipelineStageId.PER_FILE

    def execute(self, context: PipelineContext) -> StageResult:
        """Run per-file validation on all discovered ecosystem files.

        For each file in ``context.files``:
            1. Read the raw content from disk.
            2. If a validator is available: parse → classify → validate → score.
            3. Store results in the EcosystemFile's fields.

        Also extracts the project name from the index file's H1 title
        (if available after parsing) and sets ``context.project_name``.

        Args:
            context: Pipeline context with ``files`` populated by Stage 1.

        Returns:
            StageResult with SUCCESS if all files were processed, or
            FAILED if critical I/O errors occurred.
        """
        timer = StageTimer()
        timer.start()

        files_processed = 0
        files_failed = 0
        self.file_contents.clear()

        logger.info(
            "Per-file stage starting: %d files to process", len(context.files)
        )

        for eco_file in context.files:
            success = self._process_file(eco_file)
            if success:
                files_processed += 1
            else:
                files_failed += 1

        # Extract project name from the index file's parsed H1 title.
        for eco_file in context.files:
            if (
                eco_file.file_type == DocumentType.TYPE_1_INDEX
                and eco_file.parsed is not None
            ):
                context.project_name = eco_file.parsed.title
                logger.info("Project name: %s", context.project_name)
                break

        elapsed = timer.stop()

        status = StageStatus.SUCCESS if files_failed == 0 else StageStatus.SUCCESS
        # Note: We still return SUCCESS even if some files failed to read.
        # The ecosystem validator (Stage 4) will flag unreadable files.
        # We only return FAILED if ALL files failed.
        if files_processed == 0 and files_failed > 0:
            status = StageStatus.FAILED

        message = (
            f"Processed {files_processed} file(s)"
            + (f", {files_failed} failed" if files_failed > 0 else "")
        )

        logger.info(
            "Per-file stage complete: %s in %.1fms", message, elapsed
        )

        return StageResult(
            stage=self.stage_id,
            status=status,
            duration_ms=elapsed,
            message=message,
        )

    # ── Private Methods ─────────────────────────────────────────────

    def _process_file(self, eco_file: EcosystemFile) -> bool:
        """Process a single ecosystem file: read, optionally validate.

        Args:
            eco_file: The EcosystemFile to process. Modified in place.

        Returns:
            True if the file was read successfully, False otherwise.
        """
        file_path = Path(eco_file.file_path)

        # ── Step 1: Read raw content from disk ─────────────────────
        try:
            raw_content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            logger.warning(
                "Failed to read %s: %s", eco_file.file_path, exc
            )
            return False

        # Store raw content for downstream stages.
        self.file_contents[eco_file.file_id] = raw_content

        # ── Step 2: Run validator if available ─────────────────────
        if self._validator is not None:
            try:
                # Parse
                parsed = self._validator.parse(raw_content, file_path.name)
                eco_file.parsed = parsed

                # Classify
                classification = self._validator.classify(parsed)
                eco_file.classification = classification

                # Validate
                validation = self._validator.validate(parsed, classification)
                eco_file.validation = validation

                # Score
                quality = self._validator.score(validation)
                eco_file.quality = quality

                logger.info(
                    "Validated %s: level=%s, score=%s",
                    file_path.name,
                    validation.level_achieved.name if validation else "N/A",
                    quality.total_score if quality else "N/A",
                )
            except Exception as exc:
                # If the validator fails for one file, log and continue.
                # The file's parsed/validation/quality will remain None.
                logger.warning(
                    "Validator failed for %s: %s", eco_file.file_path, exc
                )
        else:
            logger.debug(
                "No validator provided — skipping parse/validate for %s",
                file_path.name,
            )

        return True
