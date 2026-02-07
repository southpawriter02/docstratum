"""DocStratum Schema Module — Public API.

Re-exports all public Pydantic models for the validation engine.
Import from this module rather than from submodules directly.

Model Categories:
    Parsed models       What an existing llms.txt file contains (Markdown AST)
    Validation models   What the validator reports (diagnostics, levels)
    Quality models      How good the file is (composite score, grades)
    Classification      What type of document it is (Type 1 vs. Type 2)
    Enrichment models   DocStratum-extended schema (concepts, few-shot, instructions)
    Constants           Canonical section names, token budget tiers, check IDs
"""

from docstratum.schema.classification import (
    DocumentClassification,
    DocumentType,
    SizeTier,
)
from docstratum.schema.constants import (
    ANTI_PATTERN_REGISTRY,
    CANONICAL_SECTION_ORDER,
    SECTION_NAME_ALIASES,
    TOKEN_BUDGET_TIERS,
    TOKEN_ZONE_ANTI_PATTERN,
    TOKEN_ZONE_DEGRADATION,
    TOKEN_ZONE_GOOD,
    TOKEN_ZONE_OPTIMAL,
    AntiPatternCategory,
    AntiPatternEntry,
    AntiPatternID,
    CanonicalSectionName,
    TokenBudgetTier,
)
from docstratum.schema.diagnostics import DiagnosticCode, Severity
from docstratum.schema.parsed import (
    ParsedBlockquote,
    ParsedLink,
    ParsedLlmsTxt,
    ParsedSection,
)

__all__ = [
    "ANTI_PATTERN_REGISTRY",
    "CANONICAL_SECTION_ORDER",
    "SECTION_NAME_ALIASES",
    "TOKEN_BUDGET_TIERS",
    "TOKEN_ZONE_ANTI_PATTERN",
    "TOKEN_ZONE_DEGRADATION",
    "TOKEN_ZONE_GOOD",
    "TOKEN_ZONE_OPTIMAL",
    "AntiPatternCategory",
    "AntiPatternEntry",
    "AntiPatternID",
    "CanonicalSectionName",
    "DiagnosticCode",
    "DocumentClassification",
    "DocumentType",
    "ParsedBlockquote",
    "ParsedLink",
    "ParsedLlmsTxt",
    "ParsedSection",
    "Severity",
    "SizeTier",
    "TokenBudgetTier",
]
