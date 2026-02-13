"""Canonical section name matcher for the DocStratum parser.

Implements v0.2.1c: for each ``ParsedSection`` in a document, attempts to
match the section's ``name`` against the 11 canonical section names and
their 32 aliases.  Populates ``ParsedSection.canonical_name`` in-place.

The matching algorithm:
    1. Normalize the section name (strip + lowercase)
    2. Exact match against CanonicalSectionName enum values
    3. Alias match against SECTION_NAME_ALIASES keys
    4. If neither matches, canonical_name remains None

Functions:
    match_canonical_sections: Match section names and set canonical_name in-place.

Related:
    - src/docstratum/schema/constants.py: CanonicalSectionName, SECTION_NAME_ALIASES
    - src/docstratum/schema/parsed.py: ParsedLlmsTxt, ParsedSection
    - docs/design/03-parser/RR-SPEC-v0.2.1c-canonical-section-matching.md: Design spec

Research basis:
    DECISION-012 (11 canonical names from 450+ project analysis)
"""

from __future__ import annotations

import logging

from docstratum.schema.constants import SECTION_NAME_ALIASES, CanonicalSectionName
from docstratum.schema.parsed import ParsedLlmsTxt

logger = logging.getLogger(__name__)


def match_canonical_sections(doc: ParsedLlmsTxt) -> None:
    """Match section names to canonical names and set canonical_name in-place.

    For each section in doc.sections, performs case-insensitive matching:
    1. Exact match against CanonicalSectionName enum values
    2. Alias match against SECTION_NAME_ALIASES keys
    3. If neither matches, canonical_name remains None

    This function mutates doc.sections in place. It does not return a value.

    Args:
        doc: ParsedLlmsTxt with populated sections.

    Example:
        >>> doc.sections[0].name = "Getting Started"
        >>> doc.sections[1].name = "quickstart"
        >>> doc.sections[2].name = "My Custom Section"
        >>> match_canonical_sections(doc)
        >>> doc.sections[0].canonical_name
        'Getting Started'
        >>> doc.sections[1].canonical_name
        'Getting Started'
        >>> doc.sections[2].canonical_name is None
        True
    """
    # Pre-compute lowercase canonical names for O(1) lookup
    canonical_lookup: dict[str, str] = {
        name.value.lower(): name.value for name in CanonicalSectionName
    }

    for section in doc.sections:
        key = section.name.strip().lower()

        # Priority 1: exact canonical match
        if key in canonical_lookup:
            section.canonical_name = canonical_lookup[key]
            logger.debug(
                "Section '%s' matched canonical name '%s'",
                section.name,
                section.canonical_name,
            )
            continue

        # Priority 2: alias match
        if key in SECTION_NAME_ALIASES:
            section.canonical_name = SECTION_NAME_ALIASES[key].value
            logger.debug(
                "Section '%s' matched alias -> '%s'",
                section.name,
                section.canonical_name,
            )
            continue

        # No match
        section.canonical_name = None
        logger.debug(
            "Section '%s' did not match any canonical name or alias",
            section.name,
        )
