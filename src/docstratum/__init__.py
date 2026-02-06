"""DocStratum — Validation engine and semantic enrichment layer for llms.txt.

DocStratum validates, scores, and enriches llms.txt files. It is NOT a generator.
The llms.txt ecosystem has 75+ generation tools but zero formal validators.
DocStratum fills that governance vacuum.

Modules:
    schema      Pydantic models for parsed documents, validation results,
                quality scores, and the extended enrichment schema.

Architecture:
    Input:      Existing llms.txt Markdown files (from any of 75+ generators)
    Process:    Parse → Classify → Validate → Score → Enrich
    Output:     Validation diagnostics, quality scores, enriched content for MCP

Design Decisions:
    See docs/design/02-foundation/RR-SPEC-v0.1.0-project-foundation.md
    for the full design decision registry (DECISION-001 through DECISION-016).
"""

__version__ = "0.1.0"
__author__ = "Ryan"
