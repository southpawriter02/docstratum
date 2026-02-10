"""DocStratum Schema Module — Public API.

Re-exports all public Pydantic models for the validation engine.
Import from this module rather than from submodules directly.

Model Categories:
    Parsed models       What an existing llms.txt file contains (Markdown AST)
    Validation models   What the validator reports (diagnostics, levels)
    Quality models      How good the file is (composite score, grades)
    Classification      What type of document it is (Type 1-4)
    Ecosystem models    [v0.0.7] Documentation ecosystem entities and scoring
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
from docstratum.schema.ecosystem import (
    DocumentEcosystem,
    EcosystemFile,
    EcosystemHealthDimension,
    EcosystemScore,
    FileRelationship,
)
from docstratum.schema.enrichment import (
    Concept,
    ConceptRelationship,
    FewShotExample,
    LLMInstruction,
    Metadata,
    RelationshipType,
)
from docstratum.schema.parsed import (
    LinkRelationship,
    ParsedBlockquote,
    ParsedLink,
    ParsedLlmsTxt,
    ParsedSection,
)
from docstratum.schema.quality import (
    DimensionScore,
    QualityDimension,
    QualityGrade,
    QualityScore,
)
from docstratum.schema.validation import (
    ValidationDiagnostic,
    ValidationLevel,
    ValidationResult,
)

__all__ = [
    # Constants
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
    # [v0.1.2d] Enrichment models
    "Concept",
    "ConceptRelationship",
    # Diagnostics
    "DiagnosticCode",
    # Quality models
    "DimensionScore",
    # Classification
    "DocumentClassification",
    # [v0.0.7] Ecosystem models
    "DocumentEcosystem",
    "DocumentType",
    "EcosystemFile",
    "EcosystemHealthDimension",
    "EcosystemScore",
    "FewShotExample",
    "FileRelationship",
    "LLMInstruction",
    # Parsed models
    "LinkRelationship",
    "Metadata",
    "ParsedBlockquote",
    "ParsedLink",
    "ParsedLlmsTxt",
    "ParsedSection",
    "QualityDimension",
    "QualityGrade",
    "QualityScore",
    "RelationshipType",
    "Severity",
    "SizeTier",
    "TokenBudgetTier",
    # Validation models
    "ValidationDiagnostic",
    "ValidationLevel",
    "ValidationResult",
]
