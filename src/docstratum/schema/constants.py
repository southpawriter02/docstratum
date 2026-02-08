"""Constants for the DocStratum validation engine.

Canonical section names (11), token budget tier definitions (3),
and the anti-pattern registry (28 patterns across 5 categories).

All values are derived from empirical research:
    - Section names: frequency analysis of 450+ projects (v0.0.2c, DECISION-012)
    - Token budgets: specimen analysis + gold standard calibration (v0.0.4a, DECISION-013)
    - Anti-patterns: 18 audited implementations + ecosystem survey (v0.0.4c, DECISION-016)

[v0.0.7] Ecosystem pivot extensions:
    - AntiPatternCategory gains ECOSYSTEM value (5 categories total)
    - AntiPatternID gains 6 ecosystem patterns AP_ECO_001 through AP_ECO_006
    - ANTI_PATTERN_REGISTRY gains 6 entries (22 → 28 total)

Traces to: FR-079 (ecosystem anti-pattern detection)
"""

import logging
from enum import StrEnum
from typing import NamedTuple

logger = logging.getLogger(__name__)


# ── Canonical Section Names ─────────────────────────────────────────────
# Derived from frequency analysis of 450+ llms.txt projects (v0.0.2c).
# The 10-step mandatory ordering sequence (v0.0.4a §6) uses these names.
# Non-canonical names trigger W002_NON_CANONICAL_SECTION_NAME.


class CanonicalSectionName(StrEnum):
    """The 11 standard section names validated across 450+ projects.

    These are ordered by the canonical 10-step sequence (v0.0.4a §6).
    Some names are aliases or variants of the same logical section;
    the validator normalizes to the primary name.

    Usage:
        from docstratum.schema.constants import CanonicalSectionName

        if section_name.lower() in CanonicalSectionName.values():
            # Known canonical name

    Example:
        >>> CanonicalSectionName.MASTER_INDEX
        <CanonicalSectionName.MASTER_INDEX: 'Master Index'>
    """

    MASTER_INDEX = "Master Index"
    LLM_INSTRUCTIONS = "LLM Instructions"
    GETTING_STARTED = "Getting Started"
    CORE_CONCEPTS = "Core Concepts"
    API_REFERENCE = "API Reference"
    EXAMPLES = "Examples"
    CONFIGURATION = "Configuration"
    ADVANCED_TOPICS = "Advanced Topics"
    TROUBLESHOOTING = "Troubleshooting"
    FAQ = "FAQ"
    OPTIONAL = "Optional"


# Mapping of common aliases to canonical names for normalization.
# The validator uses this to recognize non-standard but equivalent names.
SECTION_NAME_ALIASES: dict[str, CanonicalSectionName] = {
    "table of contents": CanonicalSectionName.MASTER_INDEX,
    "toc": CanonicalSectionName.MASTER_INDEX,
    "index": CanonicalSectionName.MASTER_INDEX,
    "docs": CanonicalSectionName.MASTER_INDEX,
    "documentation": CanonicalSectionName.MASTER_INDEX,
    "instructions": CanonicalSectionName.LLM_INSTRUCTIONS,
    "agent instructions": CanonicalSectionName.LLM_INSTRUCTIONS,
    "quickstart": CanonicalSectionName.GETTING_STARTED,
    "quick start": CanonicalSectionName.GETTING_STARTED,
    "installation": CanonicalSectionName.GETTING_STARTED,
    "setup": CanonicalSectionName.GETTING_STARTED,
    "concepts": CanonicalSectionName.CORE_CONCEPTS,
    "key concepts": CanonicalSectionName.CORE_CONCEPTS,
    "fundamentals": CanonicalSectionName.CORE_CONCEPTS,
    "api": CanonicalSectionName.API_REFERENCE,
    "reference": CanonicalSectionName.API_REFERENCE,
    "endpoints": CanonicalSectionName.API_REFERENCE,
    "usage": CanonicalSectionName.EXAMPLES,
    "use cases": CanonicalSectionName.EXAMPLES,
    "tutorials": CanonicalSectionName.EXAMPLES,
    "recipes": CanonicalSectionName.EXAMPLES,
    "config": CanonicalSectionName.CONFIGURATION,
    "settings": CanonicalSectionName.CONFIGURATION,
    "options": CanonicalSectionName.CONFIGURATION,
    "advanced": CanonicalSectionName.ADVANCED_TOPICS,
    "internals": CanonicalSectionName.ADVANCED_TOPICS,
    "debugging": CanonicalSectionName.TROUBLESHOOTING,
    "common issues": CanonicalSectionName.TROUBLESHOOTING,
    "known issues": CanonicalSectionName.TROUBLESHOOTING,
    "frequently asked questions": CanonicalSectionName.FAQ,
    "supplementary": CanonicalSectionName.OPTIONAL,
    "appendix": CanonicalSectionName.OPTIONAL,
    "extras": CanonicalSectionName.OPTIONAL,
}

# Canonical section ordering (position in the 10-step sequence).
# OPTIONAL has no fixed position — it is always last.
CANONICAL_SECTION_ORDER: dict[CanonicalSectionName, int] = {
    CanonicalSectionName.MASTER_INDEX: 1,
    CanonicalSectionName.LLM_INSTRUCTIONS: 2,
    CanonicalSectionName.GETTING_STARTED: 3,
    CanonicalSectionName.CORE_CONCEPTS: 4,
    CanonicalSectionName.API_REFERENCE: 5,
    CanonicalSectionName.EXAMPLES: 6,
    CanonicalSectionName.CONFIGURATION: 7,
    CanonicalSectionName.ADVANCED_TOPICS: 8,
    CanonicalSectionName.TROUBLESHOOTING: 9,
    CanonicalSectionName.FAQ: 10,
    # OPTIONAL has no fixed position — always last
}


# ── Token Budget Tiers ──────────────────────────────────────────────────
# Three enforced tiers with per-section allocations (DECISION-013).
# Files exceeding their tier budget trigger W010_TOKEN_BUDGET_EXCEEDED.


class TokenBudgetTier(NamedTuple):
    """Token budget tier definition.

    Attributes:
        name: Tier name for display.
        min_tokens: Lower bound of the token range (inclusive).
        max_tokens: Upper bound of the token range (inclusive).
        use_case: Description of when this tier applies.
        file_strategy: Recommended file organization (single, dual, multi).

    Example:
        >>> from docstratum.schema.constants import TOKEN_BUDGET_TIERS
        >>> TOKEN_BUDGET_TIERS["standard"].max_tokens
        4500
    """

    name: str
    min_tokens: int
    max_tokens: int
    use_case: str
    file_strategy: str


TOKEN_BUDGET_TIERS: dict[str, TokenBudgetTier] = {
    "standard": TokenBudgetTier(
        name="Standard",
        min_tokens=1_500,
        max_tokens=4_500,
        use_case="Small projects, <100 pages, <5 features",
        file_strategy="single",
    ),
    "comprehensive": TokenBudgetTier(
        name="Comprehensive",
        min_tokens=4_500,
        max_tokens=12_000,
        use_case="Medium projects, 100-500 pages, 5-20 features",
        file_strategy="dual (index + full)",
    ),
    "full": TokenBudgetTier(
        name="Full",
        min_tokens=12_000,
        max_tokens=50_000,
        use_case="Large projects, 500+ pages, 20+ features",
        file_strategy="multi (master + per-service)",
    ),
}

# Anti-pattern thresholds (v0.0.4a §Token Budget Architecture).
# These define zones where decomposition is recommended.
TOKEN_ZONE_OPTIMAL: int = 20_000  # No decomposition needed
TOKEN_ZONE_GOOD: int = 50_000  # Consider dual-file strategy
TOKEN_ZONE_DEGRADATION: int = 100_000  # Tiering strongly recommended
TOKEN_ZONE_ANTI_PATTERN: int = 500_000  # Exceeds all current context windows


# ── Anti-Pattern Registry ───────────────────────────────────────────────
# 28 named patterns across 5 severity categories (DECISION-016, v0.0.4c, v0.0.7).


class AntiPatternCategory(StrEnum):
    """Anti-pattern severity categories (DECISION-016).

    The original four categories map to the per-file composite scoring pipeline.
    [v0.0.7] The fifth category (ECOSYSTEM) maps to ecosystem-level validation
    and affects the EcosystemScore rather than per-file QualityScore.

        CRITICAL: Gate the structural score (cap total at 29)
        STRUCTURAL: Reduce the structural dimension
        CONTENT: Reduce the content dimension
        STRATEGIC: Deduction-based penalties
        ECOSYSTEM: [v0.0.7] Ecosystem-level patterns affecting aggregate health

    Example:
        >>> AntiPatternCategory.CRITICAL
        <AntiPatternCategory.CRITICAL: 'critical'>
        >>> AntiPatternCategory.ECOSYSTEM
        <AntiPatternCategory.ECOSYSTEM: 'ecosystem'>

    Traces to: v0.0.7 §6.1 (Ecosystem Anti-Pattern Category)
    """

    CRITICAL = "critical"
    STRUCTURAL = "structural"
    CONTENT = "content"
    STRATEGIC = "strategic"
    ECOSYSTEM = "ecosystem"  # [v0.0.7] New — ecosystem-level patterns


class AntiPatternID(StrEnum):
    """All 28 anti-patterns cataloged in v0.0.4c and v0.0.7.

    Format: AP-{CATEGORY}-{NUMBER}
    Each maps to a CHECK-{NNN} automated detection rule.

    [v0.0.7] Added 6 ecosystem anti-patterns (AP-ECO-001 through AP-ECO-006)
    that detect documentation ecosystem structural problems.

    Example:
        >>> AntiPatternID.AP_CRIT_001
        <AntiPatternID.AP_CRIT_001: 'AP-CRIT-001'>
        >>> AntiPatternID.AP_ECO_001
        <AntiPatternID.AP_ECO_001: 'AP-ECO-001'>

    Traces to: FR-079, v0.0.7 §6.2 (Ecosystem Anti-Patterns)
    """

    # Critical (4) — prevent LLM consumption entirely
    AP_CRIT_001 = "AP-CRIT-001"  # Ghost File
    AP_CRIT_002 = "AP-CRIT-002"  # Structure Chaos
    AP_CRIT_003 = "AP-CRIT-003"  # Encoding Disaster
    AP_CRIT_004 = "AP-CRIT-004"  # Link Void

    # Structural (5) — break navigation
    AP_STRUCT_001 = "AP-STRUCT-001"  # Sitemap Dump
    AP_STRUCT_002 = "AP-STRUCT-002"  # Orphaned Sections
    AP_STRUCT_003 = "AP-STRUCT-003"  # Duplicate Identity
    AP_STRUCT_004 = "AP-STRUCT-004"  # Section Shuffle
    AP_STRUCT_005 = "AP-STRUCT-005"  # Naming Nebula

    # Content (9) — degrade quality
    AP_CONT_001 = "AP-CONT-001"  # Copy-Paste Plague
    AP_CONT_002 = "AP-CONT-002"  # Blank Canvas
    AP_CONT_003 = "AP-CONT-003"  # Jargon Jungle
    AP_CONT_004 = "AP-CONT-004"  # Link Desert
    AP_CONT_005 = "AP-CONT-005"  # Outdated Oracle
    AP_CONT_006 = "AP-CONT-006"  # Example Void
    AP_CONT_007 = "AP-CONT-007"  # Formulaic Description
    AP_CONT_008 = "AP-CONT-008"  # Silent Agent
    AP_CONT_009 = "AP-CONT-009"  # Versionless Drift

    # Strategic (4) — undermine long-term value
    AP_STRAT_001 = "AP-STRAT-001"  # Automation Obsession
    AP_STRAT_002 = "AP-STRAT-002"  # Monolith Monster
    AP_STRAT_003 = "AP-STRAT-003"  # Meta-Documentation Spiral
    AP_STRAT_004 = "AP-STRAT-004"  # Preference Trap

    # [v0.0.7] Ecosystem (6) — ecosystem-level structural problems
    AP_ECO_001 = "AP-ECO-001"  # Index Island
    AP_ECO_002 = "AP-ECO-002"  # Phantom Links
    AP_ECO_003 = "AP-ECO-003"  # Shadow Aggregate
    AP_ECO_004 = "AP-ECO-004"  # Duplicate Ecosystem
    AP_ECO_005 = "AP-ECO-005"  # Token Black Hole
    AP_ECO_006 = "AP-ECO-006"  # Orphan Nursery


class AntiPatternEntry(NamedTuple):
    """Registry entry for an anti-pattern.

    Attributes:
        id: Unique anti-pattern identifier.
        name: Human-readable name.
        category: Severity category (critical/structural/content/strategic).
        check_id: Corresponding CHECK-NNN from v0.0.4c.
        description: One-line description of the pattern.

    Example:
        >>> from docstratum.schema.constants import ANTI_PATTERN_REGISTRY
        >>> ANTI_PATTERN_REGISTRY[0].name
        'Ghost File'
    """

    id: AntiPatternID
    name: str
    category: AntiPatternCategory
    check_id: str
    description: str


ANTI_PATTERN_REGISTRY: list[AntiPatternEntry] = [
    # Critical (4)
    AntiPatternEntry(
        AntiPatternID.AP_CRIT_001,
        "Ghost File",
        AntiPatternCategory.CRITICAL,
        "CHECK-001",
        "Empty or near-empty file that exists but provides no value",
    ),
    AntiPatternEntry(
        AntiPatternID.AP_CRIT_002,
        "Structure Chaos",
        AntiPatternCategory.CRITICAL,
        "CHECK-002",
        "File lacks recognizable Markdown structure (no headers, no sections)",
    ),
    AntiPatternEntry(
        AntiPatternID.AP_CRIT_003,
        "Encoding Disaster",
        AntiPatternCategory.CRITICAL,
        "CHECK-003",
        "Non-UTF-8 encoding or mixed line endings that break parsers",
    ),
    AntiPatternEntry(
        AntiPatternID.AP_CRIT_004,
        "Link Void",
        AntiPatternCategory.CRITICAL,
        "CHECK-004",
        "All or most links are broken, empty, or malformed",
    ),
    # Structural (5)
    AntiPatternEntry(
        AntiPatternID.AP_STRUCT_001,
        "Sitemap Dump",
        AntiPatternCategory.STRUCTURAL,
        "CHECK-005",
        "Entire sitemap dumped as flat link list with no organization",
    ),
    AntiPatternEntry(
        AntiPatternID.AP_STRUCT_002,
        "Orphaned Sections",
        AntiPatternCategory.STRUCTURAL,
        "CHECK-006",
        "Sections with headers but no links or content",
    ),
    AntiPatternEntry(
        AntiPatternID.AP_STRUCT_003,
        "Duplicate Identity",
        AntiPatternCategory.STRUCTURAL,
        "CHECK-007",
        "Multiple sections with identical or near-identical names",
    ),
    AntiPatternEntry(
        AntiPatternID.AP_STRUCT_004,
        "Section Shuffle",
        AntiPatternCategory.STRUCTURAL,
        "CHECK-008",
        "Sections in illogical order (e.g., Advanced before Getting Started)",
    ),
    AntiPatternEntry(
        AntiPatternID.AP_STRUCT_005,
        "Naming Nebula",
        AntiPatternCategory.STRUCTURAL,
        "CHECK-009",
        "Section names that are vague, inconsistent, or non-standard",
    ),
    # Content (9)
    AntiPatternEntry(
        AntiPatternID.AP_CONT_001,
        "Copy-Paste Plague",
        AntiPatternCategory.CONTENT,
        "CHECK-010",
        "Large blocks of content duplicated from other sources without curation",
    ),
    AntiPatternEntry(
        AntiPatternID.AP_CONT_002,
        "Blank Canvas",
        AntiPatternCategory.CONTENT,
        "CHECK-011",
        "Sections with placeholder text or no meaningful content",
    ),
    AntiPatternEntry(
        AntiPatternID.AP_CONT_003,
        "Jargon Jungle",
        AntiPatternCategory.CONTENT,
        "CHECK-012",
        "Heavy use of domain jargon without definitions",
    ),
    AntiPatternEntry(
        AntiPatternID.AP_CONT_004,
        "Link Desert",
        AntiPatternCategory.CONTENT,
        "CHECK-013",
        "Links without descriptions (bare URL lists)",
    ),
    AntiPatternEntry(
        AntiPatternID.AP_CONT_005,
        "Outdated Oracle",
        AntiPatternCategory.CONTENT,
        "CHECK-014",
        "Content references deprecated or outdated information",
    ),
    AntiPatternEntry(
        AntiPatternID.AP_CONT_006,
        "Example Void",
        AntiPatternCategory.CONTENT,
        "CHECK-015",
        "No code examples despite being a technical project",
    ),
    AntiPatternEntry(
        AntiPatternID.AP_CONT_007,
        "Formulaic Description",
        AntiPatternCategory.CONTENT,
        "CHECK-019",
        "Auto-generated descriptions with identical patterns (Mintlify risk)",
    ),
    AntiPatternEntry(
        AntiPatternID.AP_CONT_008,
        "Silent Agent",
        AntiPatternCategory.CONTENT,
        "CHECK-020",
        "No LLM-facing guidance despite being an AI documentation file",
    ),
    AntiPatternEntry(
        AntiPatternID.AP_CONT_009,
        "Versionless Drift",
        AntiPatternCategory.CONTENT,
        "CHECK-021",
        "No version or date metadata, impossible to assess freshness",
    ),
    # Strategic (4)
    AntiPatternEntry(
        AntiPatternID.AP_STRAT_001,
        "Automation Obsession",
        AntiPatternCategory.STRATEGIC,
        "CHECK-016",
        "Fully auto-generated with no human curation or review",
    ),
    AntiPatternEntry(
        AntiPatternID.AP_STRAT_002,
        "Monolith Monster",
        AntiPatternCategory.STRATEGIC,
        "CHECK-017",
        "Single file exceeding 100K tokens with no decomposition",
    ),
    AntiPatternEntry(
        AntiPatternID.AP_STRAT_003,
        "Meta-Documentation Spiral",
        AntiPatternCategory.STRATEGIC,
        "CHECK-018",
        "File documents itself or the llms.txt standard rather than the project",
    ),
    AntiPatternEntry(
        AntiPatternID.AP_STRAT_004,
        "Preference Trap",
        AntiPatternCategory.STRATEGIC,
        "CHECK-022",
        "Content crafted to manipulate LLM behavior (trust laundering)",
    ),
    # [v0.0.7] Ecosystem (6) — ecosystem-level structural problems
    AntiPatternEntry(
        AntiPatternID.AP_ECO_001,
        "Index Island",
        AntiPatternCategory.ECOSYSTEM,
        "CHECK-023",
        "llms.txt exists but links to nothing — no content pages, no aggregate",
    ),
    AntiPatternEntry(
        AntiPatternID.AP_ECO_002,
        "Phantom Links",
        AntiPatternCategory.ECOSYSTEM,
        "CHECK-024",
        ">30% of links in the index reference files that don't exist or return errors",
    ),
    AntiPatternEntry(
        AntiPatternID.AP_ECO_003,
        "Shadow Aggregate",
        AntiPatternCategory.ECOSYSTEM,
        "CHECK-025",
        "llms-full.txt content doesn't match what the index promises",
    ),
    AntiPatternEntry(
        AntiPatternID.AP_ECO_004,
        "Duplicate Ecosystem",
        AntiPatternCategory.ECOSYSTEM,
        "CHECK-026",
        "Multiple llms.txt files in the same project root creating ambiguity",
    ),
    AntiPatternEntry(
        AntiPatternID.AP_ECO_005,
        "Token Black Hole",
        AntiPatternCategory.ECOSYSTEM,
        "CHECK-027",
        "One file consumes >80% of total ecosystem tokens",
    ),
    AntiPatternEntry(
        AntiPatternID.AP_ECO_006,
        "Orphan Nursery",
        AntiPatternCategory.ECOSYSTEM,
        "CHECK-028",
        "Content pages exist but are not referenced from the index",
    ),
]
