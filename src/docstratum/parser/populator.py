"""Model populator for the DocStratum parser.

Implements v0.2.0c: walks the token stream produced by v0.2.0b and
populates a ``ParsedLlmsTxt`` instance through 5 sequential phases:

    1. H1 Title Extraction
    2. Blockquote Collection
    3. Body Content Consumption
    4. Section & Link Building (with code fence state tracking)
    5. Final Assembly (raw_content, source_filename, parsed_at)

The populator follows the reference parser design in v0.0.1a and uses
a cursor-based sequential walk -- each phase advances through the
token list from where the previous phase left off.

Functions:
    populate: Walk tokens and build a ParsedLlmsTxt instance.

Related:
    - src/docstratum/parser/tokenizer.py: Produces the token stream
    - src/docstratum/schema/parsed.py: Models populated by this module
    - docs/design/03-parser/RR-SPEC-v0.2.0c-model-population.md: Design spec

Research basis:
    v0.0.1a Reference Parser Phases 1-5 (lines 222-354)
    v0.0.1a Edge Cases A1-C10 (lines 369-412)
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from urllib.parse import urlparse

from docstratum.parser.tokens import Token, TokenType
from docstratum.schema.parsed import (
    ParsedBlockquote,
    ParsedLink,
    ParsedLlmsTxt,
    ParsedSection,
)

logger = logging.getLogger(__name__)

# Regex for full link entry parsing (tokenizer only checked "- [" prefix).
# Groups: (1) title, (2) URL, (3) optional description after ": "
LINK_PATTERN = re.compile(r"^- \[([^\]]*)\]\(([^)]*)\)(?::\s*(.*))?$")


def _is_syntactically_valid_url(url: str) -> bool:
    """Check if a URL is syntactically valid (not reachable).

    Rules:
        - Must have a scheme (http, https, ftp, etc.) AND netloc
        - OR start with ``/``, ``./``, or ``../`` (relative URLs)
        - Empty strings return False
        - Non-URL text returns False

    This is a SYNTACTIC check only. URL reachability is v0.3.2b.

    Args:
        url: The URL string to validate.

    Returns:
        True if the URL is syntactically valid, False otherwise.

    Example:
        >>> _is_syntactically_valid_url("https://example.com")
        True
        >>> _is_syntactically_valid_url("/docs/page")
        True
        >>> _is_syntactically_valid_url("not a url")
        False
    """
    if not url:
        return False

    # Relative URLs are valid
    if url.startswith(("/", "./", "../")):
        return True

    parsed = urlparse(url)
    return bool(parsed.scheme and parsed.netloc)


def _parse_link_entry(token: Token) -> ParsedLink | None:
    """Parse a LINK_ENTRY token into a ParsedLink.

    The tokenizer only checked the ``- [`` prefix. This function
    performs full regex parsing to extract title, URL, and optional
    description.

    Args:
        token: A Token with token_type == LINK_ENTRY.

    Returns:
        ParsedLink if the regex matches, None if the line is
        malformed (starts with ``- [`` but doesn't complete the pattern).

    Regex groups:
        group(1) = link title (content within ``[]``)
        group(2) = URL (content within ``()``)
        group(3) = description (content after ``:``) or None
    """
    match = LINK_PATTERN.match(token.raw_text)
    if not match:
        # Malformed link entry -- tokenizer flagged it as LINK_ENTRY
        # based on prefix, but full pattern doesn't match.
        logger.debug(
            "Malformed link entry at line %s: %s",
            token.line_number,
            token.raw_text,
        )
        return None

    title = match.group(1).strip()
    url = match.group(2).strip()
    description = match.group(3).strip() if match.group(3) else None

    return ParsedLink(
        title=title,
        url=url,
        description=description,
        line_number=token.line_number,
        is_valid_url=_is_syntactically_valid_url(url),
    )


def populate(
    tokens: list[Token],
    *,
    raw_content: str = "",
    source_filename: str = "llms.txt",
) -> ParsedLlmsTxt:
    """Populate a ParsedLlmsTxt model from a token stream.

    Walks the tokens through 5 phases: H1 extraction, blockquote
    extraction, body consumption, section/link building, and final
    assembly. Produces a fully populated model with safe defaults
    for any missing elements.

    Args:
        tokens: Ordered list of Token instances from tokenize().
        raw_content: Complete original file text (set as-is on
            ParsedLlmsTxt.raw_content).
        source_filename: Value for ParsedLlmsTxt.source_filename.

    Returns:
        A ParsedLlmsTxt instance. Always non-None.

    Example:
        >>> from docstratum.parser.tokenizer import tokenize
        >>> tokens = tokenize("# My App\\n> A tool\\n## API\\n- [Auth](https://api.com/auth): Auth docs\\n")
        >>> doc = populate(tokens, raw_content="...", source_filename="llms.txt")
        >>> doc.title
        'My App'
        >>> doc.sections[0].name
        'API'
    """
    logger.info("Populating model from %s tokens", len(tokens))

    doc = ParsedLlmsTxt()
    pos = 0
    total = len(tokens)

    # ── Phase 1: H1 Title Extraction ─────────────────────────────────
    # Advance past leading BLANK tokens, then look for the first H1.
    while pos < total and tokens[pos].token_type == TokenType.BLANK:
        pos += 1

    if pos < total and tokens[pos].token_type == TokenType.H1:
        doc.title = tokens[pos].raw_text.removeprefix("# ").strip()
        doc.title_line = tokens[pos].line_number
        pos += 1

    # ── Phase 2: Blockquote Extraction ───────────────────────────────
    # Skip BLANK tokens after H1, then collect consecutive BLOCKQUOTE tokens.
    while pos < total and tokens[pos].token_type == TokenType.BLANK:
        pos += 1

    bq_tokens: list[Token] = []
    while pos < total and tokens[pos].token_type == TokenType.BLOCKQUOTE:
        bq_tokens.append(tokens[pos])
        pos += 1

    if bq_tokens:
        text_lines: list[str] = []
        for bq_token in bq_tokens:
            if bq_token.raw_text == ">":
                text_lines.append("")
            elif bq_token.raw_text.startswith("> "):
                text_lines.append(bq_token.raw_text[2:])
            else:
                text_lines.append(bq_token.raw_text[1:])

        doc.blockquote = ParsedBlockquote(
            text="\n".join(text_lines),
            line_number=bq_tokens[0].line_number,
            raw="\n".join(t.raw_text for t in bq_tokens),
        )

    # ── Phase 3: Body Content Consumption ────────────────────────────
    # Consume all tokens that are NOT H2 -- body content between
    # blockquote and first section. Not stored separately.
    while pos < total and tokens[pos].token_type != TokenType.H2:
        # H1 tokens in the body are treated as text (spec A4)
        if tokens[pos].token_type == TokenType.H1:
            logger.debug(
                "Additional H1 at line %s treated as text",
                tokens[pos].line_number,
            )
        pos += 1

    # ── Phase 4: Section & Link Building ─────────────────────────────
    current_section: ParsedSection | None = None
    in_code_block = False

    while pos < total:
        token = tokens[pos]
        pos += 1

        if token.token_type == TokenType.H2:
            # Close any open code block from previous section
            in_code_block = False
            current_section = ParsedSection(
                name=token.raw_text.removeprefix("## ").strip(),
                line_number=token.line_number,
            )
            doc.sections.append(current_section)
            continue

        if current_section is None:
            # Tokens before first H2 in Phase 4 -- should not happen
            # since Phase 3 consumed them, but guard defensively.
            continue

        if token.token_type == TokenType.CODE_FENCE:
            in_code_block = not in_code_block
            # Append raw text to section content
            if current_section.raw_content:
                current_section.raw_content += "\n" + token.raw_text
            else:
                current_section.raw_content = token.raw_text
            continue

        if token.token_type == TokenType.LINK_ENTRY and not in_code_block:
            link = _parse_link_entry(token)
            if link is not None:
                current_section.links.append(link)
                # Also add to raw_content
                if current_section.raw_content:
                    current_section.raw_content += "\n" + token.raw_text
                else:
                    current_section.raw_content = token.raw_text
            else:
                # Malformed link -- treat as text content
                if current_section.raw_content:
                    current_section.raw_content += "\n" + token.raw_text
                else:
                    current_section.raw_content = token.raw_text
            continue

        # Any other token: append to section raw_content
        if current_section.raw_content:
            current_section.raw_content += "\n" + token.raw_text
        else:
            current_section.raw_content = token.raw_text

    # ── Phase 5: Final Assembly ──────────────────────────────────────
    doc.raw_content = raw_content
    doc.source_filename = source_filename
    doc.parsed_at = datetime.now()

    section_count = len(doc.sections)
    link_count = doc.total_links
    logger.info(
        "Populated model: %s sections, %s links",
        section_count,
        link_count,
    )

    return doc
