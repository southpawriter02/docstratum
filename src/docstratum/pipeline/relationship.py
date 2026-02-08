"""Stage 3: Relationship Mapping — extract links, classify, and resolve targets.

[v0.0.7] The Relationship Mapping stage builds the cross-file relationship graph.
For every file in the ecosystem, it extracts links (from the parsed model or raw
content), classifies each link's relationship type, and attempts to resolve
internal links to actual ecosystem files.

Relationship classification logic:
    - Source is TYPE_1_INDEX → target is .md content page → INDEXES
    - Source is TYPE_1_INDEX → target is llms-full.txt   → AGGREGATES
    - Source is TYPE_3_CONTENT_PAGE → target is another content page → REFERENCES
    - Target URL has a different host or is external     → EXTERNAL
    - Everything else                                    → UNKNOWN (for now)

Resolution logic:
    For each internal link (INDEXES, AGGREGATES, REFERENCES), the stage checks
    whether the target URL maps to an actual file in the ecosystem manifest.
    Resolution is by filename matching: if the URL's path component matches a
    discovered file's path (or basename), the relationship is marked as resolved
    and the ``target_file_id`` is set to the matched file's UUID.

Outputs:
    - ``context.relationships``: All FileRelationship edges for the ecosystem.
    - Each ``EcosystemFile.relationships``: Subset of edges originating from
      that file.
    - ``ParsedLink.relationship`` and ``ParsedLink.resolves_to`` updated on
      links in parsed models (if available).

Research basis:
    v0.0.7 §3.3  (Ecosystem Relationships)
    v0.0.7 §7.3  (Pipeline Stage 3: Relationship Mapping)

Traces to:
    FR-076 (link extraction and relationship mapping)
    FR-073 (ParsedLink extension — relationship, resolves_to, target_file_type)
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse

from docstratum.schema.classification import DocumentType
from docstratum.schema.ecosystem import EcosystemFile, FileRelationship
from docstratum.schema.parsed import LinkRelationship, ParsedLink

from docstratum.pipeline.stages import (
    PipelineContext,
    PipelineStageId,
    StageResult,
    StageStatus,
    StageTimer,
)

logger = logging.getLogger(__name__)


# ── Link Extraction from Raw Content ────────────────────────────────
# When parsed models aren't available (no SingleFileValidator provided),
# we fall back to regex-based link extraction from raw Markdown content.

# Markdown link pattern: [title](url) with optional description.
# Captures: group(1) = title text, group(2) = URL.
_MARKDOWN_LINK_PATTERN = re.compile(
    r"\[([^\]]+)\]\(([^)]+)\)"
)


def extract_links_from_content(content: str) -> list[ParsedLink]:
    """Extract Markdown links from raw content using regex.

    This is a fallback for when parsed models aren't available (i.e., the
    SingleFileValidator hasn't been implemented yet). It finds all ``[text](url)``
    patterns and returns them as ``ParsedLink`` instances.

    Args:
        content: Raw Markdown content of a file.

    Returns:
        List of ParsedLink objects extracted from the content. Line numbers
        are approximate (based on newline counting up to the match position).

    Example:
        >>> links = extract_links_from_content("See [API Docs](docs/api.md) for details.")
        >>> len(links)
        1
        >>> links[0].url
        'docs/api.md'
    """
    links: list[ParsedLink] = []

    for match in _MARKDOWN_LINK_PATTERN.finditer(content):
        title = match.group(1).strip()
        url = match.group(2).strip()

        # Calculate approximate line number.
        line_number = content[: match.start()].count("\n") + 1

        links.append(
            ParsedLink(
                title=title,
                url=url,
                line_number=line_number,
            )
        )

    return links


# ── URL Classification Helpers ──────────────────────────────────────


def is_external_url(url: str) -> bool:
    """Determine if a URL points outside the local ecosystem.

    A URL is considered external if it has a scheme (http, https, ftp, etc.)
    AND a network location (host). Relative paths and bare filenames are
    considered internal.

    Args:
        url: The URL or path to check.

    Returns:
        True if the URL is external, False if it's a local/relative path.

    Examples:
        >>> is_external_url("https://github.com/project/docs")
        True
        >>> is_external_url("docs/api-reference.md")
        False
        >>> is_external_url("/absolute/path/to/file.md")
        False
    """
    parsed = urlparse(url)
    return bool(parsed.scheme and parsed.netloc)


def _normalize_path(url: str, source_dir: str) -> str:
    """Normalize a relative URL to an absolute path for resolution.

    Resolves the URL relative to the source file's directory. This handles
    both relative paths (``docs/api.md``) and absolute paths (``/docs/api.md``).

    Args:
        url: The URL or relative path from a link.
        source_dir: The directory containing the source file.

    Returns:
        Normalized absolute path string.
    """
    # Strip any fragment or query string.
    clean_url = url.split("#")[0].split("?")[0]

    if os.path.isabs(clean_url):
        return os.path.normpath(clean_url)

    return os.path.normpath(os.path.join(source_dir, clean_url))


# ── Relationship Classification ─────────────────────────────────────


def classify_relationship(
    source_type: DocumentType,
    target_filename: str,
    is_external: bool,
) -> LinkRelationship:
    """Classify the relationship type between source and target.

    Uses the source file's type and the target's filename to determine
    the relationship category per v0.0.7 §3.3.

    Args:
        source_type: The DocumentType of the file containing the link.
        target_filename: Basename of the target file (e.g., "api.md").
        is_external: Whether the target URL is external.

    Returns:
        The classified LinkRelationship.

    Examples:
        >>> classify_relationship(DocumentType.TYPE_1_INDEX, "api.md", False)
        <LinkRelationship.INDEXES: 'indexes'>
        >>> classify_relationship(DocumentType.TYPE_1_INDEX, "llms-full.txt", False)
        <LinkRelationship.AGGREGATES: 'aggregates'>
        >>> classify_relationship(DocumentType.TYPE_3_CONTENT_PAGE, "guide.md", False)
        <LinkRelationship.REFERENCES: 'references'>
        >>> classify_relationship(DocumentType.TYPE_1_INDEX, "github.com", True)
        <LinkRelationship.EXTERNAL: 'external'>

    Traces to: FR-076 (link classification)
    """
    if is_external:
        return LinkRelationship.EXTERNAL

    target_lower = target_filename.lower()

    # Index file pointing to llms-full.txt → AGGREGATES.
    if source_type == DocumentType.TYPE_1_INDEX and target_lower == "llms-full.txt":
        return LinkRelationship.AGGREGATES

    # Index file pointing to content pages → INDEXES.
    if source_type == DocumentType.TYPE_1_INDEX:
        return LinkRelationship.INDEXES

    # Full/aggregate file pointing to content pages → AGGREGATES.
    if source_type == DocumentType.TYPE_2_FULL:
        return LinkRelationship.AGGREGATES

    # Content page pointing to another file → REFERENCES.
    if source_type == DocumentType.TYPE_3_CONTENT_PAGE:
        return LinkRelationship.REFERENCES

    # Instructions file pointing to other files → REFERENCES.
    if source_type == DocumentType.TYPE_4_INSTRUCTIONS:
        return LinkRelationship.REFERENCES

    return LinkRelationship.UNKNOWN


# ── Relationship Mapping Stage ──────────────────────────────────────


class RelationshipStage:
    """Stage 3: Build the cross-file relationship graph for the ecosystem.

    For each file in the ecosystem, this stage:
        1. Extracts links (from parsed models or raw content fallback).
        2. Classifies each link's relationship type (INDEXES, AGGREGATES,
           REFERENCES, EXTERNAL, UNKNOWN).
        3. Attempts to resolve internal links to ecosystem files by matching
           the target URL to discovered file paths.
        4. Creates FileRelationship edges and populates them into the context.

    The stage requires access to raw file contents for regex-based link
    extraction. It reads these from the PerFileStage's ``file_contents``
    dict, which must be passed in at construction time.

    Attributes:
        stage_id: Always ``PipelineStageId.RELATIONSHIP``.

    Example:
        >>> stage = RelationshipStage(file_contents={"id1": "# Title\\n[Link](api.md)"})
        >>> ctx = PipelineContext(files=[...])
        >>> result = stage.execute(ctx)
        >>> len(ctx.relationships) > 0
        True

    Traces to:
        FR-076 (link extraction and relationship mapping)
    """

    def __init__(self, file_contents: dict[str, str] | None = None) -> None:
        """Initialize the Relationship Mapping stage.

        Args:
            file_contents: Dict mapping file_id → raw content string.
                          If provided, used as fallback when parsed models
                          don't have links. Typically comes from
                          ``PerFileStage.file_contents``.
        """
        self._file_contents = file_contents if file_contents is not None else {}

    @property
    def stage_id(self) -> PipelineStageId:
        """The ordinal identifier for this stage."""
        return PipelineStageId.RELATIONSHIP

    def execute(self, context: PipelineContext) -> StageResult:
        """Build the relationship graph from all ecosystem files.

        Populates ``context.relationships`` with all FileRelationship edges
        and each ``EcosystemFile.relationships`` with edges originating from
        that file.

        Args:
            context: Pipeline context with ``files`` populated by Stages 1–2.

        Returns:
            StageResult with SUCCESS. This stage doesn't fail — unresolvable
            links are simply marked as unresolved (is_resolved=False).
        """
        timer = StageTimer()
        timer.start()

        all_relationships: list[FileRelationship] = []

        # Build a lookup from file path (and basename) to EcosystemFile
        # for resolution.
        path_to_file = self._build_file_lookup(context.files)

        logger.info(
            "Relationship mapping starting: %d files, %d in lookup",
            len(context.files),
            len(path_to_file),
        )

        for eco_file in context.files:
            # Extract links from parsed model or raw content.
            links = self._get_links(eco_file)

            file_relationships: list[FileRelationship] = []

            for link in links:
                relationship = self._build_relationship(
                    source_file=eco_file,
                    link=link,
                    path_lookup=path_to_file,
                    root_path=context.root_path,
                )
                file_relationships.append(relationship)

                # Update the link's ecosystem metadata if it's from a parsed model.
                link.relationship = relationship.relationship_type
                if relationship.is_resolved and relationship.target_file_id:
                    link.resolves_to = relationship.target_file_id
                    # Set target_file_type as string to avoid circular import.
                    target = path_to_file.get(relationship.target_file_id)
                    if target is not None:
                        link.target_file_type = target.file_type.value

            eco_file.relationships = file_relationships
            all_relationships.extend(file_relationships)

        context.relationships = all_relationships

        # Count resolution stats for logging.
        resolved = sum(1 for r in all_relationships if r.is_resolved)
        external = sum(
            1 for r in all_relationships
            if r.relationship_type == LinkRelationship.EXTERNAL
        )
        unresolved = len(all_relationships) - resolved - external

        elapsed = timer.stop()

        logger.info(
            "Relationship mapping complete: %d total (%d resolved, %d external, %d unresolved) in %.1fms",
            len(all_relationships),
            resolved,
            external,
            unresolved,
            elapsed,
        )

        return StageResult(
            stage=self.stage_id,
            status=StageStatus.SUCCESS,
            duration_ms=elapsed,
            message=(
                f"{len(all_relationships)} relationships: "
                f"{resolved} resolved, {external} external, {unresolved} unresolved"
            ),
        )

    # ── Private Methods ─────────────────────────────────────────────

    def _build_file_lookup(
        self, files: list[EcosystemFile]
    ) -> dict[str, EcosystemFile]:
        """Build a lookup table from file paths to EcosystemFile objects.

        Creates multiple lookup keys for each file to increase resolution
        success: the full path, the basename, and the lowercase basename.

        Args:
            files: All discovered EcosystemFile objects.

        Returns:
            Dict mapping various path representations to EcosystemFile.
        """
        lookup: dict[str, EcosystemFile] = {}

        for eco_file in files:
            fp = eco_file.file_path
            basename = os.path.basename(fp)

            # Full path.
            lookup[fp] = eco_file
            # Normalized full path.
            lookup[os.path.normpath(fp)] = eco_file
            # Basename only.
            lookup[basename] = eco_file
            # Lowercase basename.
            lookup[basename.lower()] = eco_file
            # File ID (for reverse lookups).
            lookup[eco_file.file_id] = eco_file

        return lookup

    def _get_links(self, eco_file: EcosystemFile) -> list[ParsedLink]:
        """Extract links from an ecosystem file.

        Prefers the parsed model's sections/links if available. Falls back
        to regex extraction from raw content.

        Args:
            eco_file: The EcosystemFile to extract links from.

        Returns:
            List of ParsedLink objects.
        """
        # If we have a parsed model with sections, extract links from it.
        if eco_file.parsed is not None and eco_file.parsed.sections:
            links: list[ParsedLink] = []
            for section in eco_file.parsed.sections:
                links.extend(section.links)
            return links

        # Fallback: extract from raw content if available.
        raw_content = self._file_contents.get(eco_file.file_id, "")
        if raw_content:
            return extract_links_from_content(raw_content)

        return []

    def _build_relationship(
        self,
        source_file: EcosystemFile,
        link: ParsedLink,
        path_lookup: dict[str, EcosystemFile],
        root_path: str,
    ) -> FileRelationship:
        """Build a FileRelationship from a source file and a link.

        Classifies the relationship type, attempts resolution, and creates
        the directed edge.

        Args:
            source_file: The file containing the link.
            link: The ParsedLink being processed.
            path_lookup: Dict for resolving target paths to EcosystemFile objects.
            root_path: The project root path for resolving relative URLs.

        Returns:
            A FileRelationship edge.
        """
        url = link.url
        external = is_external_url(url)

        # Determine target filename for classification.
        if external:
            target_filename = urlparse(url).path.split("/")[-1] or ""
        else:
            target_filename = os.path.basename(url.split("#")[0].split("?")[0])

        # Classify the relationship type.
        rel_type = classify_relationship(
            source_type=source_file.file_type,
            target_filename=target_filename,
            is_external=external,
        )

        # Attempt resolution for internal links.
        target_file_id = ""
        is_resolved = False

        if not external:
            resolved_file = self._resolve_link(
                url=url,
                source_file_path=source_file.file_path,
                root_path=root_path,
                path_lookup=path_lookup,
            )
            if resolved_file is not None:
                target_file_id = resolved_file.file_id
                is_resolved = True

        return FileRelationship(
            source_file_id=source_file.file_id,
            target_file_id=target_file_id,
            relationship_type=rel_type,
            source_line=link.line_number,
            target_url=url,
            is_resolved=is_resolved,
        )

    def _resolve_link(
        self,
        url: str,
        source_file_path: str,
        root_path: str,
        path_lookup: dict[str, EcosystemFile],
    ) -> EcosystemFile | None:
        """Attempt to resolve a link URL to an ecosystem file.

        Tries multiple resolution strategies:
            1. Direct match against basename.
            2. Normalized path relative to source file's directory.
            3. Normalized path relative to project root.

        Args:
            url: The link URL/path to resolve.
            source_file_path: Path of the file containing the link.
            root_path: Project root directory path.
            path_lookup: Dict for path → EcosystemFile resolution.

        Returns:
            The resolved EcosystemFile, or None if not found.
        """
        # Strip fragment and query from URL.
        clean_url = url.split("#")[0].split("?")[0]

        # Strategy 1: Direct basename match.
        basename = os.path.basename(clean_url)
        if basename in path_lookup:
            return path_lookup[basename]
        if basename.lower() in path_lookup:
            return path_lookup[basename.lower()]

        # Strategy 2: Resolve relative to source file's directory.
        source_dir = os.path.dirname(source_file_path)
        resolved = _normalize_path(clean_url, source_dir)
        if resolved in path_lookup:
            return path_lookup[resolved]

        # Strategy 3: Resolve relative to project root.
        resolved = _normalize_path(clean_url, root_path)
        if resolved in path_lookup:
            return path_lookup[resolved]

        # Strategy 4: Try the normalized path as-is.
        normalized = os.path.normpath(clean_url)
        if normalized in path_lookup:
            return path_lookup[normalized]

        logger.debug(
            "Could not resolve link: %s (from %s)", url, source_file_path
        )
        return None
