"""Document type classification models for the DocStratum validation engine.

The research (v0.0.1a enrichment) established that llms.txt files fall into
two distinct types with a bimodal distribution and no overlap zone:

    Type 1 Index: Curated link catalogs (1.1 KB - 225 KB, 80-100% conformance)
    Type 2 Full: Inline documentation dumps (1.3 MB - 25 MB, 5-15% conformance)

The ~250 KB boundary serves as the classification heuristic threshold.
Classification happens BEFORE validation because different document types
receive different validation rule sets.
"""

import logging
from datetime import datetime
from enum import StrEnum
from typing import ClassVar

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class DocumentType(StrEnum):
    """Document type classification.

    Based on the bimodal distribution observed across 11 specimens (v0.0.1a).
    No specimens exist in the 225 KB - 1.3 MB range, confirming a natural boundary.

    [v0.0.7] Ecosystem pivot adds two new document types for files discovered
    within a documentation ecosystem: individual content pages linked from the
    index (TYPE_3_CONTENT_PAGE) and explicit AI-agent instruction files
    (TYPE_4_INSTRUCTIONS). These new types determine which validation rule set
    the pipeline applies to each file.

    Attributes:
        TYPE_1_INDEX: Curated link catalog following the spec's intended format.
                      Receives full ABNF-based structural validation.
        TYPE_2_FULL: Inline documentation dump (llms-full.txt convention).
                     Receives size-appropriate diagnostics only.
        UNKNOWN: Classification could not be determined (e.g., empty file).
        TYPE_3_CONTENT_PAGE: [v0.0.7] Individual Markdown content page linked
                             from the index file. Receives content page
                             validation rules (CP-01 through CP-05).
        TYPE_4_INSTRUCTIONS: [v0.0.7] Explicit behavioral guidance file for AI
                             agents (e.g., llms-instructions.txt). Receives
                             instruction-specific validation rules.

    Traces to: v0.0.7 §4.2 (DocumentType — New Values)
    """

    # ── Original types (unchanged) ───────────────────────────────────
    TYPE_1_INDEX = "type_1_index"
    TYPE_2_FULL = "type_2_full"
    UNKNOWN = "unknown"

    # ── [v0.0.7] Ecosystem types ─────────────────────────────────────
    TYPE_3_CONTENT_PAGE = "type_3_content_page"
    TYPE_4_INSTRUCTIONS = "type_4_instructions"


class SizeTier(StrEnum):
    """Token budget size tier (DECISION-013).

    Files are assigned to tiers based on estimated token count.
    Each tier has recommended token budgets and file strategies.

    Attributes:
        MINIMAL: Under 1,500 tokens. Very small files (stubs, placeholders).
        STANDARD: 1,500-4,500 tokens. Small projects, <100 pages.
        COMPREHENSIVE: 4,500-12,000 tokens. Medium projects, 100-500 pages.
        FULL: 12,000-50,000 tokens. Large projects, 500+ pages.
        OVERSIZED: Over 50,000 tokens. Exceeds recommended limits.
    """

    MINIMAL = "minimal"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    FULL = "full"
    OVERSIZED = "oversized"


class DocumentClassification(BaseModel):
    """Result of classifying an llms.txt file before validation.

    The classifier runs first in the pipeline, determining which
    validation rules to apply and which token budget tier to enforce.

    Attributes:
        document_type: Type 1 Index or Type 2 Full (or Unknown).
        size_bytes: Raw file size in bytes.
        estimated_tokens: Approximate token count (bytes / 4 heuristic).
        size_tier: Assigned token budget tier.
        filename: Original filename (for display/logging).
        classified_at: Timestamp of classification.

    Example:
        classification = DocumentClassification(
            document_type=DocumentType.TYPE_1_INDEX,
            size_bytes=19_456,
            estimated_tokens=4_864,
            size_tier=SizeTier.COMPREHENSIVE,
            filename="llms.txt",
        )
    """

    document_type: DocumentType = Field(
        description="Whether this file is a Type 1 Index or Type 2 Full document."
    )
    size_bytes: int = Field(ge=0, description="Raw file size in bytes.")
    estimated_tokens: int = Field(
        ge=0,
        description="Approximate token count. Heuristic: bytes / 4.",
    )
    size_tier: SizeTier = Field(
        description="Token budget tier based on estimated token count.",
    )
    filename: str = Field(
        default="llms.txt",
        description="Original filename for logging and display.",
    )
    classified_at: datetime = Field(
        default_factory=datetime.now,
        description="When classification was performed.",
    )

    # ── Classification boundaries ────────────────────────────────────
    # These are class-level constants used by the classifier logic
    # (implemented in v0.3.1, but defined here for schema reference).

    TYPE_BOUNDARY_BYTES: ClassVar[int] = 256_000
    """Byte threshold separating Type 1 from Type 2.
    Files above this are classified as Type 2 Full.
    Derived from: largest Type 1 specimen = Cloudflare at 225 KB;
    smallest Type 2 specimen = Vercel AI SDK at 1.3 MB.
    """
