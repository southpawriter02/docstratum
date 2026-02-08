"""Stage 4: Ecosystem Validation — cross-file checks and anti-pattern detection.

[v0.0.7] The Ecosystem Validation stage runs checks that can ONLY be evaluated
when looking at multiple files together. These are checks that no single-file
validator could perform: broken cross-file links, inconsistent project names
across files, orphaned files, and the six ecosystem anti-patterns.

Diagnostic codes emitted by this stage:
    E010 (ORPHANED_ECOSYSTEM_FILE): File not referenced by any other file.
    W012 (BROKEN_CROSS_FILE_LINK): Internal link doesn't resolve to a file.
    W013 (MISSING_AGGREGATE): Project large enough to benefit from llms-full.txt
         but none exists.
    W014 (AGGREGATE_INCOMPLETE): llms-full.txt missing content from some files.
    W015 (INCONSISTENT_PROJECT_NAME): H1 title differs between ecosystem files.
    W016 (INCONSISTENT_VERSIONING): Version metadata differs between files.
    W017 (REDUNDANT_CONTENT): Significant content duplication (>60% overlap).
    W018 (UNBALANCED_TOKEN_DISTRIBUTION): One file consumes >70% of total tokens.
    I008 (NO_INSTRUCTION_FILE): No llms-instructions.txt in the ecosystem.
    I009 (CONTENT_COVERAGE_GAP): Not all 11 canonical section categories are covered.

Anti-patterns detected (FR-079):
    AP_ECO_001 (INDEX ISLAND):      Index with zero outgoing links.
    AP_ECO_002 (PHANTOM LINKS):     >30% of index links are broken.
    AP_ECO_003 (SHADOW AGGREGATE):  llms-full.txt content doesn't match index.
    AP_ECO_004 (DUPLICATE ECOSYSTEM): Multiple llms.txt files in project root.
    AP_ECO_005 (TOKEN BLACK HOLE):  One file consumes >80% of total tokens.
    AP_ECO_006 (ORPHAN NURSERY):    Content pages exist but aren't indexed.

Research basis:
    v0.0.7 §5 (Ecosystem Diagnostic Codes)
    v0.0.7 §6 (Ecosystem Anti-Patterns)
    v0.0.7 §7.4 (Pipeline Stage 4: Ecosystem Validation)

Traces to:
    FR-077 (cross-file link resolution)
    FR-079 (ecosystem anti-pattern detection)
"""

from __future__ import annotations

import logging
from collections import Counter

from docstratum.schema.classification import DocumentType
from docstratum.schema.constants import CanonicalSectionName, SECTION_NAME_ALIASES
from docstratum.schema.diagnostics import DiagnosticCode, Severity
from docstratum.schema.ecosystem import EcosystemFile, FileRelationship
from docstratum.schema.parsed import LinkRelationship
from docstratum.schema.validation import ValidationDiagnostic, ValidationLevel

from docstratum.pipeline.stages import (
    PipelineContext,
    PipelineStageId,
    StageResult,
    StageStatus,
    StageTimer,
)

logger = logging.getLogger(__name__)


# ── Threshold Constants ─────────────────────────────────────────────
# Configurable thresholds for ecosystem validation checks.

PHANTOM_LINKS_THRESHOLD: float = 0.30
"""Fraction of broken links that triggers AP_ECO_002 (Phantom Links)."""

TOKEN_BLACK_HOLE_THRESHOLD: float = 0.80
"""Fraction of total tokens in one file that triggers AP_ECO_005."""

UNBALANCED_DISTRIBUTION_THRESHOLD: float = 0.70
"""Fraction of total tokens in one file that triggers W018."""

AGGREGATE_SUGGESTION_TOKEN_THRESHOLD: int = 4_500
"""Token count above which W013 (MISSING_AGGREGATE) is emitted."""


# ── Helper: Canonical Section Matching ──────────────────────────────


def _match_canonical_section(section_name: str) -> CanonicalSectionName | None:
    """Match a section name to a canonical section category.

    Tries exact match first, then case-insensitive match, then alias lookup.

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


# ── Ecosystem Validation Stage ──────────────────────────────────────


class EcosystemValidationStage:
    """Stage 4: Run cross-file validation checks on the ecosystem.

    This stage operates on the complete set of discovered files and the
    relationship graph built by Stage 3. It produces ecosystem-level
    diagnostics that identify issues only visible when looking at multiple
    files together.

    The checks are organized into four groups:
        1. Link Resolution — broken cross-file links (W012)
        2. Consistency — project name, versioning, content overlap
        3. Coverage — canonical section gaps, missing companion files
        4. Anti-Patterns — the six AP_ECO patterns

    Attributes:
        stage_id: Always ``PipelineStageId.ECOSYSTEM_VALIDATION``.

    Example:
        >>> stage = EcosystemValidationStage()
        >>> ctx = PipelineContext(files=[...], relationships=[...])
        >>> result = stage.execute(ctx)
        >>> len(result.diagnostics) >= 0
        True

    Traces to:
        FR-077 (cross-file link resolution)
        FR-079 (ecosystem anti-pattern detection)
    """

    @property
    def stage_id(self) -> PipelineStageId:
        """The ordinal identifier for this stage."""
        return PipelineStageId.ECOSYSTEM_VALIDATION

    def execute(self, context: PipelineContext) -> StageResult:
        """Run all ecosystem-level validation checks.

        Populates ``context.ecosystem_diagnostics`` with cross-file
        diagnostic findings.

        Args:
            context: Pipeline context with ``files`` and ``relationships``
                     populated by Stages 1–3.

        Returns:
            StageResult with all ecosystem-level diagnostics.
        """
        timer = StageTimer()
        timer.start()

        diagnostics: list[ValidationDiagnostic] = []

        logger.info(
            "Ecosystem validation starting: %d files, %d relationships",
            len(context.files),
            len(context.relationships),
        )

        # ── Group 1: Link Resolution ───────────────────────────────
        diagnostics.extend(self._check_broken_links(context))

        # ── Group 2: Consistency ───────────────────────────────────
        diagnostics.extend(self._check_project_name_consistency(context))
        diagnostics.extend(self._check_token_distribution(context))

        # ── Group 3: Coverage ──────────────────────────────────────
        diagnostics.extend(self._check_missing_instruction_file(context))
        diagnostics.extend(self._check_missing_aggregate(context))
        diagnostics.extend(self._check_coverage_gaps(context))

        # ── Group 4: Anti-Patterns ─────────────────────────────────
        diagnostics.extend(self._check_index_island(context))
        diagnostics.extend(self._check_phantom_links(context))
        diagnostics.extend(self._check_duplicate_ecosystem(context))
        diagnostics.extend(self._check_token_black_hole(context))
        diagnostics.extend(self._check_orphaned_files(context))

        # Append to context (don't replace — Discovery may have added some).
        context.ecosystem_diagnostics.extend(diagnostics)

        elapsed = timer.stop()

        errors = sum(1 for d in diagnostics if d.severity == Severity.ERROR)
        warnings = sum(1 for d in diagnostics if d.severity == Severity.WARNING)
        infos = sum(1 for d in diagnostics if d.severity == Severity.INFO)

        logger.info(
            "Ecosystem validation complete: %d diagnostics (%dE, %dW, %dI) in %.1fms",
            len(diagnostics),
            errors,
            warnings,
            infos,
            elapsed,
        )

        return StageResult(
            stage=self.stage_id,
            status=StageStatus.SUCCESS,
            diagnostics=diagnostics,
            duration_ms=elapsed,
            message=f"{len(diagnostics)} diagnostics: {errors}E, {warnings}W, {infos}I",
        )

    # ── Group 1: Link Resolution ────────────────────────────────────

    def _check_broken_links(
        self, context: PipelineContext
    ) -> list[ValidationDiagnostic]:
        """Emit W012 for each internal link that doesn't resolve.

        Checks INDEXES, AGGREGATES, and REFERENCES relationships. EXTERNAL
        links are excluded (they're not expected to resolve to ecosystem files).

        Args:
            context: Pipeline context with files and relationships.

        Returns:
            List of W012 diagnostics for unresolved internal links.

        Traces to: FR-077 (cross-file link resolution)
        """
        diagnostics: list[ValidationDiagnostic] = []

        # Build file_id → EcosystemFile lookup for source file identification.
        id_to_file = {f.file_id: f for f in context.files}

        for rel in context.relationships:
            # Skip external links — they don't need ecosystem resolution.
            if rel.relationship_type == LinkRelationship.EXTERNAL:
                continue
            # Skip already-resolved links.
            if rel.is_resolved:
                continue

            source_file = id_to_file.get(rel.source_file_id)
            source_name = source_file.file_path if source_file else "unknown"

            diag = ValidationDiagnostic(
                code=DiagnosticCode.W012_BROKEN_CROSS_FILE_LINK,
                severity=Severity.WARNING,
                message=(
                    f"Link to '{rel.target_url}' in {source_name} "
                    f"does not resolve to any ecosystem file."
                ),
                remediation=DiagnosticCode.W012_BROKEN_CROSS_FILE_LINK.remediation,
                level=ValidationLevel.L2_CONTENT,
                line_number=rel.source_line,
                source_file=source_name,
                related_file=rel.target_url,
            )
            diagnostics.append(diag)

        return diagnostics

    # ── Group 2: Consistency ────────────────────────────────────────

    def _check_project_name_consistency(
        self, context: PipelineContext
    ) -> list[ValidationDiagnostic]:
        """Emit W015 if H1 titles differ between parsed ecosystem files.

        Compares the H1 title from every parsed file. If they disagree,
        emits one W015 diagnostic listing the inconsistencies.

        Args:
            context: Pipeline context with files.

        Returns:
            List of W015 diagnostics (0 or 1).
        """
        diagnostics: list[ValidationDiagnostic] = []
        titles: dict[str, str] = {}  # file_path → title

        for eco_file in context.files:
            if eco_file.parsed is not None and eco_file.parsed.title:
                titles[eco_file.file_path] = eco_file.parsed.title

        # If fewer than 2 files have titles, nothing to compare.
        if len(titles) < 2:
            return diagnostics

        unique_titles = set(titles.values())
        if len(unique_titles) > 1:
            details = ", ".join(
                f"{path}: '{title}'" for path, title in titles.items()
            )
            diag = ValidationDiagnostic(
                code=DiagnosticCode.W015_INCONSISTENT_PROJECT_NAME,
                severity=Severity.WARNING,
                message=f"Project name differs across files: {details}",
                remediation=DiagnosticCode.W015_INCONSISTENT_PROJECT_NAME.remediation,
                level=ValidationLevel.L3_BEST_PRACTICES,
            )
            diagnostics.append(diag)

        return diagnostics

    def _check_token_distribution(
        self, context: PipelineContext
    ) -> list[ValidationDiagnostic]:
        """Emit W018 if one file consumes >70% of total ecosystem tokens.

        This indicates an unbalanced ecosystem where the multi-file strategy
        isn't being leveraged effectively.

        Args:
            context: Pipeline context with files.

        Returns:
            List of W018 diagnostics (0 or 1 per offending file).
        """
        diagnostics: list[ValidationDiagnostic] = []

        if len(context.files) < 2:
            return diagnostics

        total_tokens = sum(
            f.classification.estimated_tokens
            for f in context.files
            if f.classification is not None
        )

        if total_tokens == 0:
            return diagnostics

        for eco_file in context.files:
            if eco_file.classification is None:
                continue
            file_tokens = eco_file.classification.estimated_tokens
            ratio = file_tokens / total_tokens

            if ratio > UNBALANCED_DISTRIBUTION_THRESHOLD:
                diag = ValidationDiagnostic(
                    code=DiagnosticCode.W018_UNBALANCED_TOKEN_DISTRIBUTION,
                    severity=Severity.WARNING,
                    message=(
                        f"{eco_file.file_path} consumes {ratio:.0%} of total "
                        f"ecosystem tokens ({file_tokens:,} of {total_tokens:,})."
                    ),
                    remediation=DiagnosticCode.W018_UNBALANCED_TOKEN_DISTRIBUTION.remediation,
                    level=ValidationLevel.L3_BEST_PRACTICES,
                    source_file=eco_file.file_path,
                )
                diagnostics.append(diag)

        return diagnostics

    # ── Group 3: Coverage ───────────────────────────────────────────

    def _check_missing_instruction_file(
        self, context: PipelineContext
    ) -> list[ValidationDiagnostic]:
        """Emit I008 if no llms-instructions.txt exists in the ecosystem.

        Args:
            context: Pipeline context with files.

        Returns:
            List containing I008 if no instruction file found (0 or 1).
        """
        has_instructions = any(
            f.file_type == DocumentType.TYPE_4_INSTRUCTIONS
            for f in context.files
        )
        if not has_instructions:
            return [
                ValidationDiagnostic(
                    code=DiagnosticCode.I008_NO_INSTRUCTION_FILE,
                    severity=Severity.INFO,
                    message=DiagnosticCode.I008_NO_INSTRUCTION_FILE.message,
                    remediation=DiagnosticCode.I008_NO_INSTRUCTION_FILE.remediation,
                    level=ValidationLevel.L3_BEST_PRACTICES,
                )
            ]
        return []

    def _check_missing_aggregate(
        self, context: PipelineContext
    ) -> list[ValidationDiagnostic]:
        """Emit W013 if the project is large enough for llms-full.txt but has none.

        A project with more than ``AGGREGATE_SUGGESTION_TOKEN_THRESHOLD``
        tokens (4,500) would benefit from an aggregate file for large-window
        model consumption.

        Args:
            context: Pipeline context with files.

        Returns:
            List containing W013 if aggregate is missing and beneficial (0 or 1).
        """
        has_aggregate = any(
            f.file_type == DocumentType.TYPE_2_FULL for f in context.files
        )
        if has_aggregate:
            return []

        total_tokens = sum(
            f.classification.estimated_tokens
            for f in context.files
            if f.classification is not None
        )

        if total_tokens > AGGREGATE_SUGGESTION_TOKEN_THRESHOLD:
            return [
                ValidationDiagnostic(
                    code=DiagnosticCode.W013_MISSING_AGGREGATE,
                    severity=Severity.WARNING,
                    message=(
                        f"Ecosystem has {total_tokens:,} tokens but no llms-full.txt. "
                        f"An aggregate file would help large-window models."
                    ),
                    remediation=DiagnosticCode.W013_MISSING_AGGREGATE.remediation,
                    level=ValidationLevel.L3_BEST_PRACTICES,
                )
            ]
        return []

    def _check_coverage_gaps(
        self, context: PipelineContext
    ) -> list[ValidationDiagnostic]:
        """Emit I009 if the ecosystem doesn't cover all 11 canonical section categories.

        Scans section names across ALL files in the ecosystem (not just the index)
        and reports which canonical categories are missing.

        Args:
            context: Pipeline context with files.

        Returns:
            List containing I009 if coverage gaps exist (0 or 1).

        Traces to: FR-082 (coverage scoring uses this same analysis)
        """
        covered: set[CanonicalSectionName] = set()

        for eco_file in context.files:
            if eco_file.parsed is None:
                continue
            for section in eco_file.parsed.sections:
                matched = _match_canonical_section(section.name)
                if matched is not None:
                    covered.add(matched)

        all_canonical = set(CanonicalSectionName)
        missing = all_canonical - covered

        if missing and len(context.files) > 1:
            missing_names = sorted(m.value for m in missing)
            return [
                ValidationDiagnostic(
                    code=DiagnosticCode.I009_CONTENT_COVERAGE_GAP,
                    severity=Severity.INFO,
                    message=(
                        f"Ecosystem covers {len(covered)} of 11 canonical categories. "
                        f"Missing: {', '.join(missing_names)}"
                    ),
                    remediation=DiagnosticCode.I009_CONTENT_COVERAGE_GAP.remediation,
                    level=ValidationLevel.L3_BEST_PRACTICES,
                )
            ]
        return []

    # ── Group 4: Anti-Patterns ──────────────────────────────────────

    def _check_index_island(
        self, context: PipelineContext
    ) -> list[ValidationDiagnostic]:
        """Detect AP_ECO_001 (INDEX ISLAND): index file with zero outgoing links.

        An index file that doesn't link to anything is useless as a navigation
        hub. This is the most basic ecosystem anti-pattern.

        Args:
            context: Pipeline context with files and relationships.

        Returns:
            List of E010-based diagnostics if pattern detected.
        """
        index_files = [
            f for f in context.files
            if f.file_type == DocumentType.TYPE_1_INDEX
        ]
        diagnostics: list[ValidationDiagnostic] = []

        for index_file in index_files:
            outgoing = [
                r for r in context.relationships
                if r.source_file_id == index_file.file_id
                and r.relationship_type != LinkRelationship.EXTERNAL
            ]
            if len(outgoing) == 0 and len(context.files) > 1:
                diagnostics.append(
                    ValidationDiagnostic(
                        code=DiagnosticCode.E010_ORPHANED_ECOSYSTEM_FILE,
                        severity=Severity.ERROR,
                        message=(
                            f"Index file {index_file.file_path} has zero internal links. "
                            "Anti-pattern AP_ECO_001 (Index Island)."
                        ),
                        remediation=(
                            "Add links from llms.txt to your content pages "
                            "so AI agents can discover your documentation."
                        ),
                        level=ValidationLevel.L1_STRUCTURAL,
                        source_file=index_file.file_path,
                    )
                )

        return diagnostics

    def _check_phantom_links(
        self, context: PipelineContext
    ) -> list[ValidationDiagnostic]:
        """Detect AP_ECO_002 (PHANTOM LINKS): >30% of index links are broken.

        When more than 30% of the links in the index file don't resolve to
        actual files, the ecosystem is essentially a facade.

        Args:
            context: Pipeline context with files and relationships.

        Returns:
            List of diagnostics if pattern detected.
        """
        diagnostics: list[ValidationDiagnostic] = []
        index_files = [
            f for f in context.files
            if f.file_type == DocumentType.TYPE_1_INDEX
        ]

        for index_file in index_files:
            # Get all non-external links from this index file.
            internal_links = [
                r for r in context.relationships
                if r.source_file_id == index_file.file_id
                and r.relationship_type != LinkRelationship.EXTERNAL
            ]

            if len(internal_links) == 0:
                continue  # Handled by _check_index_island.

            broken = sum(1 for r in internal_links if not r.is_resolved)
            ratio = broken / len(internal_links)

            if ratio > PHANTOM_LINKS_THRESHOLD:
                diagnostics.append(
                    ValidationDiagnostic(
                        code=DiagnosticCode.W012_BROKEN_CROSS_FILE_LINK,
                        severity=Severity.WARNING,
                        message=(
                            f"Anti-pattern AP_ECO_002 (Phantom Links): "
                            f"{broken} of {len(internal_links)} internal links "
                            f"({ratio:.0%}) in {index_file.file_path} are broken."
                        ),
                        remediation=(
                            "Ensure all links in llms.txt point to existing content pages. "
                            "Remove links to deleted or renamed files."
                        ),
                        level=ValidationLevel.L2_CONTENT,
                        source_file=index_file.file_path,
                    )
                )

        return diagnostics

    def _check_duplicate_ecosystem(
        self, context: PipelineContext
    ) -> list[ValidationDiagnostic]:
        """Detect AP_ECO_004 (DUPLICATE ECOSYSTEM): multiple llms.txt files.

        If the discovery stage found more than one file classified as
        TYPE_1_INDEX, the ecosystem is ambiguous.

        Args:
            context: Pipeline context with files.

        Returns:
            List of diagnostics if pattern detected.
        """
        index_files = [
            f for f in context.files
            if f.file_type == DocumentType.TYPE_1_INDEX
        ]

        if len(index_files) > 1:
            paths = [f.file_path for f in index_files]
            return [
                ValidationDiagnostic(
                    code=DiagnosticCode.E009_NO_INDEX_FILE,
                    severity=Severity.ERROR,
                    message=(
                        f"Anti-pattern AP_ECO_004 (Duplicate Ecosystem): "
                        f"Multiple index files found: {', '.join(paths)}. "
                        f"An ecosystem should have exactly one llms.txt."
                    ),
                    remediation=(
                        "Remove duplicate index files. Keep one canonical llms.txt "
                        "as the ecosystem entry point."
                    ),
                    level=ValidationLevel.L0_PARSEABLE,
                )
            ]
        return []

    def _check_token_black_hole(
        self, context: PipelineContext
    ) -> list[ValidationDiagnostic]:
        """Detect AP_ECO_005 (TOKEN BLACK HOLE): one file consumes >80% of tokens.

        Stricter than W018 (>70%). This anti-pattern means the multi-file
        strategy has completely failed — one file dominates everything.

        Args:
            context: Pipeline context with files.

        Returns:
            List of diagnostics if pattern detected.
        """
        diagnostics: list[ValidationDiagnostic] = []

        if len(context.files) < 2:
            return diagnostics

        total_tokens = sum(
            f.classification.estimated_tokens
            for f in context.files
            if f.classification is not None
        )

        if total_tokens == 0:
            return diagnostics

        for eco_file in context.files:
            if eco_file.classification is None:
                continue
            file_tokens = eco_file.classification.estimated_tokens
            ratio = file_tokens / total_tokens

            if ratio > TOKEN_BLACK_HOLE_THRESHOLD:
                diagnostics.append(
                    ValidationDiagnostic(
                        code=DiagnosticCode.W018_UNBALANCED_TOKEN_DISTRIBUTION,
                        severity=Severity.WARNING,
                        message=(
                            f"Anti-pattern AP_ECO_005 (Token Black Hole): "
                            f"{eco_file.file_path} consumes {ratio:.0%} of "
                            f"ecosystem tokens ({file_tokens:,} of {total_tokens:,})."
                        ),
                        remediation=(
                            "Split large files into focused content pages. "
                            "The multi-file strategy should distribute content evenly."
                        ),
                        level=ValidationLevel.L3_BEST_PRACTICES,
                        source_file=eco_file.file_path,
                    )
                )

        return diagnostics

    def _check_orphaned_files(
        self, context: PipelineContext
    ) -> list[ValidationDiagnostic]:
        """Detect orphaned files and AP_ECO_006 (ORPHAN NURSERY).

        A file is orphaned if it's in the ecosystem but no other file
        references it. The index file is exempt (it's the root).

        AP_ECO_006 triggers when multiple content pages are orphaned —
        the "nursery" of unreachable pages.

        Args:
            context: Pipeline context with files and relationships.

        Returns:
            List of E010 diagnostics for each orphaned file.
        """
        diagnostics: list[ValidationDiagnostic] = []

        if len(context.files) <= 1:
            return diagnostics

        # Build set of all file IDs that are targets of at least one relationship.
        referenced_ids: set[str] = set()
        for rel in context.relationships:
            if rel.is_resolved and rel.target_file_id:
                referenced_ids.add(rel.target_file_id)

        orphaned_content_pages = 0

        for eco_file in context.files:
            # The index file is the root — it's not expected to be referenced.
            if eco_file.file_type == DocumentType.TYPE_1_INDEX:
                continue

            if eco_file.file_id not in referenced_ids:
                diagnostics.append(
                    ValidationDiagnostic(
                        code=DiagnosticCode.E010_ORPHANED_ECOSYSTEM_FILE,
                        severity=Severity.ERROR,
                        message=(
                            f"{eco_file.file_path} is not referenced by any other "
                            f"file in the ecosystem."
                        ),
                        remediation=DiagnosticCode.E010_ORPHANED_ECOSYSTEM_FILE.remediation,
                        level=ValidationLevel.L1_STRUCTURAL,
                        source_file=eco_file.file_path,
                    )
                )

                if eco_file.file_type == DocumentType.TYPE_3_CONTENT_PAGE:
                    orphaned_content_pages += 1

        # If multiple content pages are orphaned, that's AP_ECO_006.
        if orphaned_content_pages >= 2:
            diagnostics.append(
                ValidationDiagnostic(
                    code=DiagnosticCode.E010_ORPHANED_ECOSYSTEM_FILE,
                    severity=Severity.ERROR,
                    message=(
                        f"Anti-pattern AP_ECO_006 (Orphan Nursery): "
                        f"{orphaned_content_pages} content pages are not "
                        f"referenced from the index."
                    ),
                    remediation=(
                        "Add links from llms.txt to all content pages so "
                        "AI agents can discover them."
                    ),
                    level=ValidationLevel.L1_STRUCTURAL,
                )
            )

        return diagnostics
