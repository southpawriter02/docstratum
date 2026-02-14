"""YAML frontmatter metadata extractor for the DocStratum parser.

Implements v0.2.1d: checks for YAML frontmatter at the top of a file and
extracts recognized keys into a ``Metadata`` model instance.  Frontmatter
is a de facto standard in documentation ecosystems (Hugo, Jekyll, Docusaurus)
but is not part of the llms.txt spec.  Its presence is informational --
DocStratum uses it for provenance tracking, not validation gating.

Functions:
    extract_metadata: Extract YAML frontmatter into a Metadata instance.

Related:
    - src/docstratum/schema/enrichment.py: Metadata model (7 fields)
    - docs/design/03-parser/RR-SPEC-v0.2.1d-metadata-extraction.md: Design spec

Research basis:
    v0.0.1b Gap Analysis Gap #5 (Required Metadata)
"""

from __future__ import annotations

import logging

import yaml

from docstratum.schema.enrichment import Metadata

logger = logging.getLogger(__name__)


def extract_metadata(raw_content: str) -> Metadata | None:
    """Extract YAML frontmatter metadata from raw file content.

    Checks if the content starts with a YAML frontmatter block
    delimited by '---' lines. If present, parses the YAML and
    maps recognized keys to a Metadata model instance.

    Args:
        raw_content: Complete file content (decoded string).

    Returns:
        A Metadata instance if valid frontmatter is found, None otherwise.
        Returns None for:
        - No frontmatter delimiters
        - Malformed YAML (parse error)
        - Empty frontmatter block

    Example:
        >>> content = "---\\nsite_name: My Project\\ngenerator: docusaurus\\n---\\n# My Project\\n"
        >>> meta = extract_metadata(content)
        >>> meta.site_name
        'My Project'
        >>> meta.generator
        'docusaurus'
        >>> meta.schema_version
        '0.1.0'

        >>> extract_metadata("# No frontmatter\\n")
    """
    frontmatter_text = _extract_frontmatter_text(raw_content)
    if frontmatter_text is None:
        return None

    raw_dict = _parse_yaml(frontmatter_text)
    if raw_dict is None:
        return None

    return _map_to_metadata(raw_dict)


def _extract_frontmatter_text(content: str) -> str | None:
    """Extract the text between opening and closing --- delimiters.

    The opening ``---`` must be the first non-blank line.  Leading
    blank lines are tolerated.

    Args:
        content: Raw file content.

    Returns:
        The text between delimiters, or None if no valid
        frontmatter block is found.
    """
    lines = content.splitlines(keepends=True)

    # Skip leading blank lines
    start_idx = 0
    while start_idx < len(lines) and lines[start_idx].strip() == "":
        start_idx += 1

    # Check for opening delimiter
    if start_idx >= len(lines) or lines[start_idx].strip() != "---":
        return None

    # Find closing delimiter
    body_start = start_idx + 1
    close_idx = None
    for i in range(body_start, len(lines)):
        if lines[i].strip() == "---":
            close_idx = i
            break

    if close_idx is None:
        return None  # No closing delimiter

    # Extract frontmatter text
    frontmatter_lines = lines[body_start:close_idx]
    return "".join(frontmatter_lines)


def _parse_yaml(text: str) -> dict | None:
    """Parse YAML text into a dictionary.

    Uses ``yaml.safe_load`` to prevent arbitrary code execution.

    Args:
        text: Raw YAML text from frontmatter block.

    Returns:
        A dictionary if parsing succeeds, None if:
        - YAML parse error
        - Result is not a dictionary (e.g., scalar or list)
        - Text is empty or whitespace-only
    """
    if not text.strip():
        return None

    try:
        result = yaml.safe_load(text)
    except yaml.YAMLError:
        logger.debug("YAML parse error in frontmatter")
        return None

    if not isinstance(result, dict):
        logger.debug("Frontmatter YAML is not a dict (got %s)", type(result).__name__)
        return None

    return result


def _map_to_metadata(raw_dict: dict) -> Metadata:
    """Map frontmatter dictionary keys to Metadata model fields.

    Recognized keys (case-sensitive):
        schema_version      -> Metadata.schema_version
        site_name           -> Metadata.site_name
        site_url            -> Metadata.site_url
        last_updated        -> Metadata.last_updated
        generator           -> Metadata.generator
        docstratum_version  -> Metadata.docstratum_version
        token_budget_tier   -> Metadata.token_budget_tier

    Unrecognized keys are silently ignored (permissive input).

    Args:
        raw_dict: Parsed YAML dictionary.

    Returns:
        A Metadata instance with recognized fields populated.
        Fields not present in the frontmatter use Pydantic defaults.
    """
    known_fields = {
        "schema_version",
        "site_name",
        "site_url",
        "last_updated",
        "generator",
        "docstratum_version",
        "token_budget_tier",
    }

    filtered = {k: v for k, v in raw_dict.items() if k in known_fields}

    logger.debug("Extracted metadata fields: %s", list(filtered.keys()))

    return Metadata(**filtered)
