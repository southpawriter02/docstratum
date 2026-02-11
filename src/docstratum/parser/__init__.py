"""Parser package for the DocStratum validation engine.

Implements the parser pipeline that reads raw llms.txt Markdown files
and transforms them into populated Pydantic models. The parser is the
first piece of runtime logic in the system — everything downstream
(validation, scoring, remediation, ecosystem analysis) depends on the
models it produces.

Modules:
    io          File I/O, encoding detection, and line ending normalization (v0.2.0a).
    tokens      Token type enum and Token model (v0.2.0b).
    tokenizer   Line-by-line Markdown tokenizer (v0.2.0b).

Implementation Status:
    - [x] File I/O & Encoding Detection (v0.2.0a)
    - [x] Markdown Tokenization (v0.2.0b)
    - [ ] Model Population (v0.2.0c)
    - [ ] Token Estimation (v0.2.0d)

Related:
    - src/docstratum/schema/parsed.py: Pydantic models this package populates
    - docs/design/03-parser/: Design specifications for this package
"""

from docstratum.parser.io import FileMetadata, read_bytes, read_file, read_string
from docstratum.parser.tokenizer import tokenize
from docstratum.parser.tokens import Token, TokenType

__all__ = [
    "FileMetadata",
    "Token",
    "TokenType",
    "read_bytes",
    "read_file",
    "read_string",
    "tokenize",
]
