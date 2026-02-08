"""Stage 1: Ecosystem Discovery — scan a project root for AI-facing documentation.

[v0.0.7] The Discovery stage is the entry point of the ecosystem pipeline. Given
a project root directory, it scans for the canonical AI-facing files:

    Required:
        llms.txt             — The index and entry point for AI agents (TYPE_1_INDEX)

    Optional:
        llms-full.txt        — Complete content in one file for large-window models (TYPE_2_FULL)
        llms-instructions.txt — Behavioral guidance for AI agents (TYPE_4_INSTRUCTIONS)
        *.md linked from     — Individual content pages (TYPE_3_CONTENT_PAGE)
        llms.txt

The stage also supports single-file mode: if a single llms.txt file path is
provided (instead of a project directory), the stage wraps it in a 1-file
ecosystem and emits I010 (ECOSYSTEM_SINGLE_FILE).

File classification uses filename pattern matching:
    - ``llms.txt``              → TYPE_1_INDEX
    - ``llms-full.txt``         → TYPE_2_FULL
    - ``llms-instructions.txt`` → TYPE_4_INSTRUCTIONS
    - ``*.md`` (linked)         → TYPE_3_CONTENT_PAGE
    - Anything else             → UNKNOWN

Error conditions:
    E009 (NO_INDEX_FILE)       — No llms.txt found in the project root.
    I010 (ECOSYSTEM_SINGLE_FILE) — Only llms.txt exists; valid but limited.

Research basis:
    v0.0.7 §3.1  (The Ecosystem Model — Three Layers)
    v0.0.7 §7.1  (Pipeline Stage 1: Discovery)

Traces to:
    FR-074 (directory-based ecosystem discovery)
    FR-075 (file type classification for ecosystem members)
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from pydantic import BaseModel, Field

from docstratum.schema.classification import DocumentClassification, DocumentType, SizeTier
from docstratum.schema.diagnostics import DiagnosticCode
from docstratum.schema.ecosystem import EcosystemFile
from docstratum.schema.validation import Severity, ValidationDiagnostic, ValidationLevel

from docstratum.pipeline.stages import (
    PipelineContext,
    PipelineStageId,
    StageResult,
    StageStatus,
    StageTimer,
)

logger = logging.getLogger(__name__)


# ── Well-Known Filenames ────────────────────────────────────────────
# Canonical filenames recognized by the Discovery stage.
# Case-insensitive matching is used (see _classify_filename).

INDEX_FILENAME: str = "llms.txt"
"""The required root index file (TYPE_1_INDEX)."""

FULL_FILENAME: str = "llms-full.txt"
"""The optional aggregate content dump (TYPE_2_FULL)."""

INSTRUCTIONS_FILENAME: str = "llms-instructions.txt"
"""The optional behavioral instructions file (TYPE_4_INSTRUCTIONS)."""

# Content page extensions that the discovery stage follows from the index.
CONTENT_PAGE_EXTENSIONS: frozenset[str] = frozenset({".md", ".markdown"})
"""File extensions recognized as content pages when linked from the index."""


# ── File Classification ─────────────────────────────────────────────


def classify_filename(filename: str) -> DocumentType:
    """Classify a file by its filename into a DocumentType.

    Uses case-insensitive matching against the well-known filenames defined
    in the llms.txt ecosystem specification. Files not matching any known
    pattern are classified as UNKNOWN.

    Args:
        filename: The file's basename (e.g., "llms.txt", "api-reference.md").
                  Must be a filename only, not a full path.

    Returns:
        The DocumentType classification for this file.

    Examples:
        >>> classify_filename("llms.txt")
        <DocumentType.TYPE_1_INDEX: 'type_1_index'>
        >>> classify_filename("llms-full.txt")
        <DocumentType.TYPE_2_FULL: 'type_2_full'>
        >>> classify_filename("api-reference.md")
        <DocumentType.TYPE_3_CONTENT_PAGE: 'type_3_content_page'>
        >>> classify_filename("llms-instructions.txt")
        <DocumentType.TYPE_4_INSTRUCTIONS: 'type_4_instructions'>
        >>> classify_filename("random-file.json")
        <DocumentType.UNKNOWN: 'unknown'>

    Traces to: FR-075 (file type classification)
    """
    lower = filename.lower()

    if lower == INDEX_FILENAME:
        return DocumentType.TYPE_1_INDEX

    if lower == FULL_FILENAME:
        return DocumentType.TYPE_2_FULL

    if lower == INSTRUCTIONS_FILENAME:
        return DocumentType.TYPE_4_INSTRUCTIONS

    # Check extension for content pages. Only files linked from the index
    # should be classified as TYPE_3_CONTENT_PAGE, but at the filename level
    # we use extension as a heuristic. The caller (discovery logic) refines
    # this by only classifying linked files.
    _, ext = os.path.splitext(lower)
    if ext in CONTENT_PAGE_EXTENSIONS:
        return DocumentType.TYPE_3_CONTENT_PAGE

    return DocumentType.UNKNOWN


def _estimate_size_tier(size_bytes: int) -> SizeTier:
    """Estimate the SizeTier for a file based on byte count.

    Uses the same heuristic thresholds as the classification module:
        MINIMAL:         < 500 bytes
        STANDARD:        500 – 5,000 bytes
        COMPREHENSIVE:   5,000 – 20,000 bytes
        FULL:            20,000 – 256,000 bytes
        OVERSIZED:       > 256,000 bytes

    Args:
        size_bytes: File size in bytes.

    Returns:
        The estimated SizeTier.
    """
    if size_bytes < 500:
        return SizeTier.MINIMAL
    elif size_bytes < 5_000:
        return SizeTier.STANDARD
    elif size_bytes < 20_000:
        return SizeTier.COMPREHENSIVE
    elif size_bytes <= 256_000:
        return SizeTier.FULL
    else:
        return SizeTier.OVERSIZED


def _estimate_tokens(size_bytes: int) -> int:
    """Rough token estimate from byte count.

    Uses the standard heuristic of ~4 characters per token for English text.
    Since Markdown is predominantly English text, this is a reasonable
    approximation until the actual tokenizer is available.

    Args:
        size_bytes: File size in bytes (assuming UTF-8).

    Returns:
        Estimated token count.
    """
    return max(1, size_bytes // 4)


# ── Discovery Stage ─────────────────────────────────────────────────


class DiscoveryStage:
    """Stage 1: Scan a project root directory for AI-facing documentation files.

    The Discovery stage builds the initial file manifest for the ecosystem
    pipeline. It finds the required index file (llms.txt), optional companion
    files (llms-full.txt, llms-instructions.txt), and any content pages
    (.md files) present in the same directory.

    In single-file mode (path points directly to a file), the stage wraps
    that file in a 1-file ecosystem.

    Emitted diagnostics:
        E009 (NO_INDEX_FILE):       No llms.txt found in the project root.
        I010 (ECOSYSTEM_SINGLE_FILE): Only llms.txt found; valid but limited.

    Attributes:
        stage_id: Always ``PipelineStageId.DISCOVERY``.

    Example:
        >>> stage = DiscoveryStage()
        >>> ctx = PipelineContext(root_path="/path/to/project")
        >>> result = stage.execute(ctx)
        >>> result.status == StageStatus.SUCCESS
        True
        >>> len(ctx.files) > 0
        True

    Traces to:
        FR-074 (directory-based ecosystem discovery)
        FR-075 (file type classification for ecosystem members)
    """

    @property
    def stage_id(self) -> PipelineStageId:
        """The ordinal identifier for this stage."""
        return PipelineStageId.DISCOVERY

    def execute(self, context: PipelineContext) -> StageResult:
        """Scan the project root and build the file manifest.

        Populates ``context.files`` with ``EcosystemFile`` entries and
        ``context.project_name`` with the project name (if extractable).

        Args:
            context: Pipeline context. ``context.root_path`` must be set
                     to a valid directory or file path.

        Returns:
            StageResult with SUCCESS if at least one file found (even if
            only the index), or FAILED if no index file exists.
        """
        timer = StageTimer()
        timer.start()
        diagnostics: list[ValidationDiagnostic] = []

        root = Path(context.root_path)
        logger.info("Discovery stage starting: root_path=%s", root)

        # ── Determine scan mode ────────────────────────────────────
        # If root_path points to a file, use single-file mode.
        # If it points to a directory, scan for all ecosystem files.

        if root.is_file():
            # Single-file mode: wrap the file in a 1-file ecosystem.
            logger.info("Single-file mode: %s", root.name)
            files, diags = self._discover_single_file(root)
            diagnostics.extend(diags)
            context.root_path = str(root.parent)
        elif root.is_dir():
            # Directory mode: scan for all known files.
            logger.info("Directory mode: scanning %s", root)
            files, diags = self._discover_directory(root)
            diagnostics.extend(diags)
        else:
            # Path doesn't exist or is not accessible.
            logger.error("Root path does not exist: %s", root)
            elapsed = timer.stop()
            return StageResult(
                stage=self.stage_id,
                status=StageStatus.FAILED,
                diagnostics=[],
                duration_ms=elapsed,
                message=f"Root path does not exist: {root}",
            )

        # ── Check for index file ───────────────────────────────────
        has_index = any(
            f.file_type == DocumentType.TYPE_1_INDEX for f in files
        )
        if not has_index:
            diag = ValidationDiagnostic(
                code=DiagnosticCode.E009_NO_INDEX_FILE,
                severity=Severity.ERROR,
                message=DiagnosticCode.E009_NO_INDEX_FILE.message,
                remediation=DiagnosticCode.E009_NO_INDEX_FILE.remediation,
                level=ValidationLevel.L0_PARSEABLE,
            )
            diagnostics.append(diag)
            logger.warning("No llms.txt index file found in %s", root)

        # ── Populate context ───────────────────────────────────────
        context.files = files
        context.ecosystem_diagnostics.extend(diagnostics)

        elapsed = timer.stop()
        status = StageStatus.FAILED if not has_index else StageStatus.SUCCESS
        file_types = [f.file_type.value for f in files]

        logger.info(
            "Discovery complete: %d files found (%s) in %.1fms",
            len(files),
            ", ".join(file_types),
            elapsed,
        )

        return StageResult(
            stage=self.stage_id,
            status=status,
            diagnostics=diagnostics,
            duration_ms=elapsed,
            message=f"Discovered {len(files)} file(s): {', '.join(file_types)}",
        )

    # ── Private Methods ─────────────────────────────────────────────

    def _discover_single_file(
        self, file_path: Path
    ) -> tuple[list[EcosystemFile], list[ValidationDiagnostic]]:
        """Wrap a single file in a 1-file ecosystem manifest.

        Args:
            file_path: Path to the single file (expected to be llms.txt).

        Returns:
            Tuple of (files, diagnostics). Always returns exactly 1 file.
            Emits I010 if the file is a valid index.
        """
        diagnostics: list[ValidationDiagnostic] = []
        file_type = classify_filename(file_path.name)

        eco_file = self._build_ecosystem_file(file_path, file_type)

        # Emit I010 if this is a valid single-file ecosystem.
        if file_type == DocumentType.TYPE_1_INDEX:
            diag = ValidationDiagnostic(
                code=DiagnosticCode.I010_ECOSYSTEM_SINGLE_FILE,
                severity=Severity.INFO,
                message=DiagnosticCode.I010_ECOSYSTEM_SINGLE_FILE.message,
                remediation=DiagnosticCode.I010_ECOSYSTEM_SINGLE_FILE.remediation,
                level=ValidationLevel.L0_PARSEABLE,
                source_file=str(file_path.name),
            )
            diagnostics.append(diag)
            logger.info("Single-file ecosystem: %s", file_path.name)

        return [eco_file], diagnostics

    def _discover_directory(
        self, directory: Path
    ) -> tuple[list[EcosystemFile], list[ValidationDiagnostic]]:
        """Scan a directory for all known ecosystem files.

        Scans the directory (non-recursively) for:
            1. llms.txt (required)
            2. llms-full.txt (optional)
            3. llms-instructions.txt (optional)
            4. *.md files (potential content pages)

        Args:
            directory: Path to the project root directory.

        Returns:
            Tuple of (files, diagnostics).
        """
        diagnostics: list[ValidationDiagnostic] = []
        files: list[EcosystemFile] = []

        # Collect all files in the directory (non-recursive).
        try:
            dir_entries = sorted(directory.iterdir())
        except PermissionError:
            logger.error("Permission denied reading directory: %s", directory)
            return files, diagnostics

        # Track what we find for single-file ecosystem detection.
        found_index = False
        companion_count = 0

        for entry in dir_entries:
            if not entry.is_file():
                continue

            file_type = classify_filename(entry.name)

            # We only discover files that match known ecosystem types.
            # UNKNOWN files are ignored unless linked from the index
            # (link-following is handled by Stage 3: Relationship Mapping).
            if file_type == DocumentType.UNKNOWN:
                continue

            eco_file = self._build_ecosystem_file(entry, file_type)
            files.append(eco_file)

            if file_type == DocumentType.TYPE_1_INDEX:
                found_index = True
                logger.info("Found index file: %s", entry.name)
            else:
                companion_count += 1
                logger.info("Found companion file: %s (%s)", entry.name, file_type.value)

        # If we have an index but no companions, emit I010.
        if found_index and companion_count == 0:
            diag = ValidationDiagnostic(
                code=DiagnosticCode.I010_ECOSYSTEM_SINGLE_FILE,
                severity=Severity.INFO,
                message=DiagnosticCode.I010_ECOSYSTEM_SINGLE_FILE.message,
                remediation=DiagnosticCode.I010_ECOSYSTEM_SINGLE_FILE.remediation,
                level=ValidationLevel.L0_PARSEABLE,
                source_file=INDEX_FILENAME,
            )
            diagnostics.append(diag)
            logger.info("Single-file ecosystem detected (no companions)")

        return files, diagnostics

    def _build_ecosystem_file(
        self, file_path: Path, file_type: DocumentType
    ) -> EcosystemFile:
        """Create an EcosystemFile from a filesystem path.

        Populates the file_path, file_type, and a minimal classification
        based on file size. The parsed, validation, and quality fields are
        left as None — those are populated by Stage 2 (Per-File Validation).

        Args:
            file_path: Absolute path to the file on disk.
            file_type: The classified DocumentType.

        Returns:
            An EcosystemFile with auto-generated UUID and basic metadata.
        """
        # Get file size for classification.
        try:
            size_bytes = file_path.stat().st_size
        except OSError:
            size_bytes = 0

        classification = DocumentClassification(
            document_type=file_type,
            size_bytes=size_bytes,
            estimated_tokens=_estimate_tokens(size_bytes),
            size_tier=_estimate_size_tier(size_bytes),
            filename=file_path.name,
        )

        return EcosystemFile(
            file_path=str(file_path),
            file_type=file_type,
            classification=classification,
        )
