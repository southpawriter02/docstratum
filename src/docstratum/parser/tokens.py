"""Token type definitions for the DocStratum parser.

Implements v0.2.0b: defines the structural token types recognized by the
llms.txt tokenizer and the ``Token`` Pydantic model that carries each
classified line through the parser pipeline.

Classes:
    TokenType: StrEnum of 8 structural line classifications.
    Token: Pydantic model representing one tokenized line.

Related:
    - src/docstratum/parser/tokenizer.py: Produces Token instances
    - docs/design/03-parser/RR-SPEC-v0.2.0b-markdown-tokenization.md: Design spec

Research basis:
    v0.0.1a §ABNF Grammar (lines 74-127) -- grammar productions mapped to token types
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class TokenType(StrEnum):
    """Structural token types recognized by the llms.txt tokenizer.

    These map directly to the ABNF grammar productions in v0.0.1a:
        H1         → h1-title
        H2         → h2-title (file-list-section header)
        H3_PLUS    → Not in grammar (treated as prose, per edge case A7)
        BLOCKQUOTE → blockquote-line
        LINK_ENTRY → file-entry
        CODE_FENCE → Not in grammar (fenced code block delimiter)
        BLANK      → blank-line
        TEXT       → content-line / paragraph

    Example:
        >>> TokenType.H1
        <TokenType.H1: 'h1'>
        >>> TokenType.H1.value
        'h1'
    """

    H1 = "h1"
    H2 = "h2"
    H3_PLUS = "h3_plus"
    BLOCKQUOTE = "blockquote"
    LINK_ENTRY = "link_entry"
    CODE_FENCE = "code_fence"
    BLANK = "blank"
    TEXT = "text"


class Token(BaseModel):
    """A single tokenized line from an llms.txt file.

    Each Token represents one logical line from the source document,
    classified by its syntactic prefix. The tokenizer produces an
    ordered list of these, preserving document order and 1-indexed
    line numbers.

    Attributes:
        token_type: The structural classification of this line.
        line_number: 1-indexed line number in the original file.
        raw_text: The complete original line text (no prefix stripping).

    Example:
        >>> token = Token(token_type=TokenType.H1, line_number=1, raw_text="# My Project")
        >>> token.token_type
        <TokenType.H1: 'h1'>
        >>> token.line_number
        1
    """

    token_type: TokenType = Field(description="Structural classification of this line.")
    line_number: int = Field(
        ge=1, description="1-indexed line number in the source file."
    )
    raw_text: str = Field(description="Complete original line text.")
