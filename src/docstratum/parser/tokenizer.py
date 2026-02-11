"""Markdown tokenizer for the DocStratum parser.

Implements v0.2.0b: takes a decoded, LF-normalized string (from v0.2.0a)
and breaks it into an ordered sequence of structural tokens. Each token
represents one logical line classified by its syntactic prefix.

The tokenizer uses line-by-line scanning — not full AST parsing — because
the ``llms.txt`` format is a constrained Markdown subset that does not
require a full CommonMark parser. See v0.0.1a §ABNF Grammar for the
exact productions matched.

Functions:
    tokenize: Classify each line of an llms.txt string into Token instances.

Related:
    - src/docstratum/parser/tokens.py: TokenType enum and Token model
    - src/docstratum/parser/io.py: Produces the decoded string this module consumes
    - docs/design/03-parser/RR-SPEC-v0.2.0b-markdown-tokenization.md: Design spec

Research basis:
    v0.0.1a §ABNF Grammar (lines 74-127)
    v0.0.1a §Reference Parser Design Phases 1-4
"""

from __future__ import annotations

import logging

from docstratum.parser.tokens import Token, TokenType

logger = logging.getLogger(__name__)


def _classify_line(line: str) -> TokenType:
    """Classify a single line by its prefix pattern.

    Uses priority-ordered prefix matching per v0.2.0b §4.
    The check order for headings is ``###`` → ``##`` → ``#``
    to prevent ``## Section`` from matching as H1.

    This function is only called for lines outside fenced code blocks.
    Lines inside code blocks are unconditionally classified as TEXT
    by the caller.

    Args:
        line: A single line of text (no trailing newline).

    Returns:
        The TokenType classification for this line.
    """
    # -- Headings: check deepest first to avoid false matches --
    # (v0.2.0b §4.2: ### → ## → # order is critical)
    if line.startswith("### ") or line.startswith("####"):
        return TokenType.H3_PLUS
    if line.startswith("## "):
        return TokenType.H2
    if line.startswith("# "):
        return TokenType.H1

    # -- Blockquote: "> " or bare ">" (edge case C2) --
    if line.startswith("> ") or line == ">":
        return TokenType.BLOCKQUOTE

    # -- Link entry: prefix-only check, full parsing in v0.2.0c --
    if line.startswith("- ["):
        return TokenType.LINK_ENTRY

    # -- Blank: empty or whitespace-only --
    if line.strip() == "":
        return TokenType.BLANK

    # -- Everything else is plain text --
    return TokenType.TEXT


def tokenize(content: str) -> list[Token]:
    """Tokenize a decoded llms.txt string into structural tokens.

    Scans the content line by line, classifying each line based on
    its prefix pattern. Lines within fenced code blocks are always
    classified as TEXT regardless of their content.

    Args:
        content: Decoded, LF-normalized Markdown content (from v0.2.0a).

    Returns:
        An ordered list of Token instances, one per line.
        Empty content returns an empty list.

    Example:
        >>> tokens = tokenize("# Title\\n> Desc\\n## Docs\\n- [Foo](https://foo.com)\\n")
        >>> [t.token_type for t in tokens]
        [<TokenType.H1: 'h1'>, <TokenType.BLOCKQUOTE: 'blockquote'>, <TokenType.H2: 'h2'>, <TokenType.LINK_ENTRY: 'link_entry'>]
    """
    # -- Handle empty input --
    if not content:
        logger.debug("Empty content, returning empty token list")
        return []

    lines = content.split("\n")

    # Trailing newline produces an empty final element — remove it
    # to avoid a spurious BLANK token. A file ending with "\n" has
    # its last real line before the newline; the empty string after
    # is an artifact of split(), not a real document line.
    if lines and lines[-1] == "":
        lines = lines[:-1]

    logger.info("Tokenizing %d lines", len(lines))

    tokens: list[Token] = []
    in_code_block = False

    for line_number, line in enumerate(lines, start=1):
        # -- Code fence detection (priority 1-2 per §4) --
        if line.startswith("```"):
            tokens.append(
                Token(
                    token_type=TokenType.CODE_FENCE,
                    line_number=line_number,
                    raw_text=line,
                )
            )
            in_code_block = not in_code_block
            continue

        # -- Inside code block: everything is TEXT (priority 1) --
        if in_code_block:
            tokens.append(
                Token(
                    token_type=TokenType.TEXT,
                    line_number=line_number,
                    raw_text=line,
                )
            )
            continue

        # -- Normal classification (priorities 3-9) --
        token_type = _classify_line(line)
        tokens.append(
            Token(
                token_type=token_type,
                line_number=line_number,
                raw_text=line,
            )
        )

    logger.info("Tokenized %d lines into %d tokens", len(lines), len(tokens))
    return tokens
