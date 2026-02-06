# v0.1.2a — Diagnostic Infrastructure: Error Codes, Constants, and Cross-Reference

> **Phase:** Foundation (v0.1.x)
> **Status:** DRAFT — Realigned to validation-engine pivot (2026-02-06)
> **Parent:** [v0.1.2 — Schema Definition](RR-SPEC-v0.1.2-schema-definition.md)
> **Goal:** Define the foundational "shared vocabulary" for the validation engine — the error code registry (`diagnostics.py`), canonical names, token budget tiers, anti-pattern registry (`constants.py`), and the cross-reference mapping between all three overlapping ID systems.
> **Traces to:** FR-008 (v0.0.5a); DECISION-012, -013, -016 (v0.0.4d); v0.0.1a enrichment (8E/11W/7I codes), v0.0.2c (450+ project analysis), v0.0.4a/b/c (structural/content/anti-pattern checks)

---

## Why This Sub-Part Exists

These two files (`diagnostics.py` and `constants.py`) form the **dependency root** of the entire schema hierarchy. Every other schema file may import from `diagnostics.py` (for `DiagnosticCode` and `Severity`) or `constants.py` (for `CanonicalSectionName`, `AntiPatternID`, etc.), but neither `diagnostics.py` nor `constants.py` imports from any other schema file.

The cross-reference mapping table resolves the many-to-many relationships between the three ID systems inherited from different research phases (v0.0.4a/b check IDs, v0.0.4c CHECK-NNN IDs, and the DiagnosticCode enum values).

---

## File 1: `src/docstratum/schema/diagnostics.py`

> **Traces to:** FR-008 (v0.0.5a); v0.0.1a enrichment pass; v0.0.4a/b/c check IDs

```python
"""Error code registry for the DocStratum validation engine.

Defines the complete diagnostic code catalog derived from the v0.0.1a
enrichment pass. Every validation finding references a DiagnosticCode
that includes the severity level, a human-readable message template,
and a remediation hint.

The code format follows the pattern: {SEVERITY_PREFIX}{NUMBER}
    E001–E008:  Errors (8 codes) — Structural failures that prevent valid parsing
    W001–W011:  Warnings (11 codes) — Deviations from best practices
    I001–I007:  Informational (7 codes) — Observations and suggestions

Research basis:
    v0.0.1a §Error Code Registry (enrichment pass)
    v0.0.4a §Structural Checks (ENC-001/002, STR-001–005, MD-001–003, etc.)
    v0.0.4b §Content Checks (CNT-001–015)
    v0.0.4c §Anti-Pattern Checks (CHECK-001–022)
"""

from enum import StrEnum


class Severity(StrEnum):
    """Diagnostic severity levels.

    Aligned with the three-tier output format mandated by NFR-006
    (clear CLI errors with severity + code + message + remediation).

    Attributes:
        ERROR: Structural failure that prevents valid parsing or breaks spec conformance.
               Maps to validation levels L0–L1 (parseable, structural).
        WARNING: Deviation from best practices that degrades quality but doesn't break parsing.
                 Maps to validation levels L2–L3 (content, best practices).
        INFO: Observation or suggestion for improvement. Non-blocking.
              Maps to validation level L4 (DocStratum extended).
    """

    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class DiagnosticCode(StrEnum):
    """Complete diagnostic code catalog for the validation engine.

    Every code has a unique identifier, severity, message template,
    and remediation hint. The code prefix indicates severity:
        E = Error, W = Warning, I = Info

    Codes are organized by validation dimension:
        E001–E008: Structural errors (v0.0.4a checks ENC-001/002, STR-001–005, MD-001, LNK-002)
        W001–W011: Quality warnings (v0.0.4a/b checks NAM-001, CNT-004–009, CNT-015, SIZ-001)
        I001–I007: Informational (v0.0.4b checks CNT-010–014, classification notes)

    Usage:
        from docstratum.schema.diagnostics import DiagnosticCode, Severity

        code = DiagnosticCode.E001_NO_H1_TITLE
        print(code.severity)      # Severity.ERROR
        print(code.message)       # "No H1 title found..."
        print(code.remediation)   # "Add a single H1 title..."
    """

    # ── ERRORS (E001–E008): Structural failures ──────────────────────────
    # These prevent the file from passing L1 (Structural) validation.

    E001_NO_H1_TITLE = "E001"
    """No H1 title found. Every llms.txt file MUST begin with exactly one H1 title.
    Maps to: STR-001 (v0.0.4a). Severity: ERROR.
    Remediation: Add a single '# Title' as the first line of the file."""

    E002_MULTIPLE_H1 = "E002"
    """Multiple H1 titles found. The spec requires exactly one H1.
    Maps to: STR-001 (v0.0.4a). Severity: ERROR.
    Remediation: Remove all but the first H1 title. Use H2 for section headers."""

    E003_INVALID_ENCODING = "E003"
    """File is not valid UTF-8 encoding.
    Maps to: ENC-001 (v0.0.4a). Severity: ERROR.
    Remediation: Convert the file to UTF-8 encoding. Remove any BOM markers."""

    E004_INVALID_LINE_ENDINGS = "E004"
    """File uses non-LF line endings (CR or CRLF detected).
    Maps to: ENC-002 (v0.0.4a). Severity: ERROR.
    Remediation: Convert line endings to LF (Unix-style). Most editors have this option."""

    E005_INVALID_MARKDOWN = "E005"
    """File contains invalid Markdown syntax that prevents parsing.
    Maps to: MD-001 (v0.0.4a). Severity: ERROR.
    Remediation: Fix Markdown syntax errors. Use a Markdown linter to identify issues."""

    E006_BROKEN_LINKS = "E006"
    """Section contains links with empty or malformed URLs.
    Maps to: LNK-002 (v0.0.4a), CHECK-004 (v0.0.4c Ghost File anti-pattern). Severity: ERROR.
    Remediation: Fix or remove links with empty href values. Ensure all URLs are well-formed."""

    E007_EMPTY_FILE = "E007"
    """File is empty or contains only whitespace.
    Maps to: CHECK-001 (v0.0.4c Ghost File anti-pattern). Severity: ERROR.
    Remediation: Add content to the file. At minimum: H1 title, blockquote, one H2 section."""

    E008_EXCEEDS_SIZE_LIMIT = "E008"
    """File exceeds the maximum recommended size (>100K tokens).
    Maps to: SIZ-003 (v0.0.4a), CHECK-003 (v0.0.4c Monolith Monster). Severity: ERROR.
    Remediation: Decompose into a tiered file strategy (index + full + per-section files)."""

    # ── WARNINGS (W001–W011): Quality deviations ────────────────────────
    # These prevent the file from achieving L3 (Best Practices) validation.

    W001_MISSING_BLOCKQUOTE = "W001"
    """No blockquote description found after the H1 title.
    Maps to: STR-002 (v0.0.4a). Severity: WARNING.
    Note: 55% real-world compliance (v0.0.2 enrichment), so this is a warning, not an error.
    Remediation: Add a '> description' blockquote immediately after the H1 title."""

    W002_NON_CANONICAL_SECTION_NAME = "W002"
    """Section name does not match any of the 11 canonical names.
    Maps to: NAM-001 (v0.0.4a). Severity: WARNING.
    Remediation: Use canonical names where possible (see CanonicalSectionName enum)."""

    W003_LINK_MISSING_DESCRIPTION = "W003"
    """Link entry has no description text (bare URL only).
    Maps to: CNT-004 (v0.0.4b), CHECK-010 (v0.0.4c Link Desert). Severity: WARNING.
    Remediation: Add a description after the link: '- [Title](url): Description of the page'."""

    W004_NO_CODE_EXAMPLES = "W004"
    """File contains no code examples (no fenced code blocks found).
    Maps to: CNT-007 (v0.0.4b). Severity: WARNING.
    Note: Code examples are the strongest quality predictor (r ~ 0.65, v0.0.2c).
    Remediation: Add code examples with language specifiers (```python, ```bash, etc.)."""

    W005_CODE_NO_LANGUAGE = "W005"
    """Code block found without a language specifier.
    Maps to: CNT-008 (v0.0.4b). Severity: WARNING.
    Remediation: Add a language identifier after the opening triple backticks."""

    W006_FORMULAIC_DESCRIPTIONS = "W006"
    """Multiple sections use identical or near-identical description patterns.
    Maps to: CNT-005 (v0.0.4b), CHECK-015 (v0.0.4c Formulaic Description). Severity: WARNING.
    Remediation: Write unique, specific descriptions for each section."""

    W007_MISSING_VERSION_METADATA = "W007"
    """No version or last-updated metadata found in the file.
    Maps to: CNT-015 (v0.0.4b). Severity: WARNING.
    Remediation: Add version metadata (e.g., 'Last updated: 2026-02-06')."""

    W008_SECTION_ORDER_NON_CANONICAL = "W008"
    """Sections do not follow the canonical 10-step ordering.
    Maps to: STR-004 (v0.0.4a). Severity: WARNING.
    Remediation: Reorder sections to match canonical sequence (see v0.0.4a §6)."""

    W009_NO_MASTER_INDEX = "W009"
    """No Master Index found as the first H2 section.
    Maps to: STR-003 (v0.0.4a), DECISION-010. Severity: WARNING.
    Note: Files with Master Index achieve 87% vs. 31% LLM success rate.
    Remediation: Add a Master Index as the first H2 section with navigation links."""

    W010_TOKEN_BUDGET_EXCEEDED = "W010"
    """File exceeds the recommended token budget for its tier.
    Maps to: SIZ-001 (v0.0.4a), DECISION-013. Severity: WARNING.
    Remediation: Trim content to stay within the tier's token budget."""

    W011_EMPTY_SECTIONS = "W011"
    """One or more sections contain no meaningful content (placeholder text only).
    Maps to: CHECK-011 (v0.0.4c Blank Canvas anti-pattern). Severity: WARNING.
    Remediation: Add content or remove empty sections. Placeholder sections waste tokens."""

    # ── INFORMATIONAL (I001–I007): Suggestions ──────────────────────────
    # These are non-blocking observations for L4 (DocStratum Extended).

    I001_NO_LLM_INSTRUCTIONS = "I001"
    """No LLM Instructions section found.
    Maps to: CNT-010 (v0.0.4b). Severity: INFO.
    Note: 0% current adoption (v0.0.2), but strongest quality differentiator.
    Remediation: Add an LLM Instructions section with positive/negative directives."""

    I002_NO_CONCEPT_DEFINITIONS = "I002"
    """No structured concept definitions found.
    Maps to: CNT-013 (v0.0.4b). Severity: INFO.
    Remediation: Add concept definitions with IDs, relationships, and aliases."""

    I003_NO_FEW_SHOT_EXAMPLES = "I003"
    """No few-shot Q&A examples found.
    Maps to: v0.0.1b Gap #2 (P0). Severity: INFO.
    Remediation: Add intent-tagged Q&A pairs linked to concepts."""

    I004_RELATIVE_URLS_DETECTED = "I004"
    """Relative URLs found in link entries (may need resolution).
    Maps to: LNK-003 (v0.0.4a). Severity: INFO.
    Remediation: Convert relative URLs to absolute or document the base URL."""

    I005_TYPE_2_FULL_DETECTED = "I005"
    """File classified as Type 2 Full (inline documentation dump, >250 KB).
    Maps to: Document Type Classification (v0.0.1a enrichment). Severity: INFO.
    Note: Type 2 files are not spec-conformant but are valid in MCP contexts.
    Remediation: Consider creating a Type 1 Index companion file."""

    I006_OPTIONAL_SECTIONS_UNMARKED = "I006"
    """Optional sections not explicitly marked with token estimates.
    Maps to: DECISION-011 (v0.0.4d). Severity: INFO.
    Remediation: Mark optional sections so consumers can skip them to save context."""

    I007_JARGON_WITHOUT_DEFINITION = "I007"
    """Domain-specific jargon used without inline definition.
    Maps to: CNT-014 (v0.0.4b). Severity: INFO.
    Remediation: Define jargon inline or link to a concept definition."""

    @property
    def severity(self) -> Severity:
        """Derive severity from the code prefix (E=Error, W=Warning, I=Info)."""
        prefix = self.value[0]
        return {
            "E": Severity.ERROR,
            "W": Severity.WARNING,
            "I": Severity.INFO,
        }[prefix]

    @property
    def code_number(self) -> int:
        """Extract the numeric portion of the code (e.g., E001 -> 1)."""
        return int(self.value[1:])

    @property
    def message(self) -> str:
        """Return the first line of the docstring as the message template."""
        doc = self.__class__.__dict__[self.name].__doc__
        if doc:
            return doc.strip().split("\n")[0]
        return f"Diagnostic {self.value}"

    @property
    def remediation(self) -> str:
        """Extract the remediation hint from the docstring."""
        doc = self.__class__.__dict__[self.name].__doc__
        if doc:
            for line in doc.strip().split("\n"):
                stripped = line.strip()
                if stripped.startswith("Remediation:"):
                    return stripped[len("Remediation:"):].strip()
        return "No remediation available."
```

---

## File 2: `src/docstratum/schema/constants.py`

> **Traces to:** DECISION-012 (v0.0.4d); DECISION-013 (v0.0.4d); DECISION-016 (v0.0.4d); v0.0.2c (450+ project analysis), v0.0.4a (token budget definitions), v0.0.4c (anti-pattern catalog)

```python
"""Constants for the DocStratum validation engine.

Canonical section names (11), token budget tier definitions (3),
and the anti-pattern registry (22 patterns across 4 categories).

All values are derived from empirical research:
    - Section names: frequency analysis of 450+ projects (v0.0.2c, DECISION-012)
    - Token budgets: specimen analysis + gold standard calibration (v0.0.4a, DECISION-013)
    - Anti-patterns: 18 audited implementations + ecosystem survey (v0.0.4c, DECISION-016)
"""

from enum import StrEnum
from typing import NamedTuple


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

# Canonical section ordering (position in the 10-step sequence)
CANONICAL_SECTION_NAMES: dict[CanonicalSectionName, int] = {
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
        use_case="Medium projects, 100–500 pages, 5–20 features",
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

# Anti-pattern thresholds (v0.0.4a §Token Budget Architecture)
TOKEN_ZONE_OPTIMAL = 20_000  # No decomposition needed
TOKEN_ZONE_GOOD = 50_000  # Consider dual-file strategy
TOKEN_ZONE_DEGRADATION = 100_000  # Tiering strongly recommended
TOKEN_ZONE_ANTI_PATTERN = 500_000  # Exceeds all current context windows


# ── Anti-Pattern Registry ───────────────────────────────────────────────
# 22 named patterns across 4 severity categories (DECISION-016, v0.0.4c).


class AntiPatternCategory(StrEnum):
    """Anti-pattern severity categories (DECISION-016).

    The four categories map to the composite scoring pipeline:
        CRITICAL: Gate the structural score (cap total at 29)
        STRUCTURAL: Reduce the structural dimension
        CONTENT: Reduce the content dimension
        STRATEGIC: Deduction-based penalties
    """

    CRITICAL = "critical"
    STRUCTURAL = "structural"
    CONTENT = "content"
    STRATEGIC = "strategic"


class AntiPatternID(StrEnum):
    """All 22 anti-patterns cataloged in v0.0.4c.

    Format: AP-{CATEGORY}-{NUMBER}
    Each maps to a CHECK-{NNN} automated detection rule.
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


class AntiPatternEntry(NamedTuple):
    """Registry entry for an anti-pattern.

    Attributes:
        id: Unique anti-pattern identifier.
        name: Human-readable name.
        category: Severity category (critical/structural/content/strategic).
        check_id: Corresponding CHECK-NNN from v0.0.4c.
        description: One-line description of the pattern.
    """

    id: AntiPatternID
    name: str
    category: AntiPatternCategory
    check_id: str
    description: str


ANTI_PATTERN_REGISTRY: list[AntiPatternEntry] = [
    # Critical
    AntiPatternEntry(AntiPatternID.AP_CRIT_001, "Ghost File", AntiPatternCategory.CRITICAL, "CHECK-001", "Empty or near-empty file that exists but provides no value"),
    AntiPatternEntry(AntiPatternID.AP_CRIT_002, "Structure Chaos", AntiPatternCategory.CRITICAL, "CHECK-002", "File lacks recognizable Markdown structure (no headers, no sections)"),
    AntiPatternEntry(AntiPatternID.AP_CRIT_003, "Encoding Disaster", AntiPatternCategory.CRITICAL, "CHECK-003", "Non-UTF-8 encoding or mixed line endings that break parsers"),
    AntiPatternEntry(AntiPatternID.AP_CRIT_004, "Link Void", AntiPatternCategory.CRITICAL, "CHECK-004", "All or most links are broken, empty, or malformed"),
    # Structural
    AntiPatternEntry(AntiPatternID.AP_STRUCT_001, "Sitemap Dump", AntiPatternCategory.STRUCTURAL, "CHECK-005", "Entire sitemap dumped as flat link list with no organization"),
    AntiPatternEntry(AntiPatternID.AP_STRUCT_002, "Orphaned Sections", AntiPatternCategory.STRUCTURAL, "CHECK-006", "Sections with headers but no links or content"),
    AntiPatternEntry(AntiPatternID.AP_STRUCT_003, "Duplicate Identity", AntiPatternCategory.STRUCTURAL, "CHECK-007", "Multiple sections with identical or near-identical names"),
    AntiPatternEntry(AntiPatternID.AP_STRUCT_004, "Section Shuffle", AntiPatternCategory.STRUCTURAL, "CHECK-008", "Sections in illogical order (e.g., Advanced before Getting Started)"),
    AntiPatternEntry(AntiPatternID.AP_STRUCT_005, "Naming Nebula", AntiPatternCategory.STRUCTURAL, "CHECK-009", "Section names that are vague, inconsistent, or non-standard"),
    # Content
    AntiPatternEntry(AntiPatternID.AP_CONT_001, "Copy-Paste Plague", AntiPatternCategory.CONTENT, "CHECK-010", "Large blocks of content duplicated from other sources without curation"),
    AntiPatternEntry(AntiPatternID.AP_CONT_002, "Blank Canvas", AntiPatternCategory.CONTENT, "CHECK-011", "Sections with placeholder text or no meaningful content"),
    AntiPatternEntry(AntiPatternID.AP_CONT_003, "Jargon Jungle", AntiPatternCategory.CONTENT, "CHECK-012", "Heavy use of domain jargon without definitions"),
    AntiPatternEntry(AntiPatternID.AP_CONT_004, "Link Desert", AntiPatternCategory.CONTENT, "CHECK-013", "Links without descriptions (bare URL lists)"),
    AntiPatternEntry(AntiPatternID.AP_CONT_005, "Outdated Oracle", AntiPatternCategory.CONTENT, "CHECK-014", "Content references deprecated or outdated information"),
    AntiPatternEntry(AntiPatternID.AP_CONT_006, "Example Void", AntiPatternCategory.CONTENT, "CHECK-015", "No code examples despite being a technical project"),
    AntiPatternEntry(AntiPatternID.AP_CONT_007, "Formulaic Description", AntiPatternCategory.CONTENT, "CHECK-019", "Auto-generated descriptions with identical patterns (Mintlify risk)"),
    AntiPatternEntry(AntiPatternID.AP_CONT_008, "Silent Agent", AntiPatternCategory.CONTENT, "CHECK-020", "No LLM-facing guidance despite being an AI documentation file"),
    AntiPatternEntry(AntiPatternID.AP_CONT_009, "Versionless Drift", AntiPatternCategory.CONTENT, "CHECK-021", "No version or date metadata, impossible to assess freshness"),
    # Strategic
    AntiPatternEntry(AntiPatternID.AP_STRAT_001, "Automation Obsession", AntiPatternCategory.STRATEGIC, "CHECK-016", "Fully auto-generated with no human curation or review"),
    AntiPatternEntry(AntiPatternID.AP_STRAT_002, "Monolith Monster", AntiPatternCategory.STRATEGIC, "CHECK-017", "Single file exceeding 100K tokens with no decomposition"),
    AntiPatternEntry(AntiPatternID.AP_STRAT_003, "Meta-Documentation Spiral", AntiPatternCategory.STRATEGIC, "CHECK-018", "File documents itself or the llms.txt standard rather than the project"),
    AntiPatternEntry(AntiPatternID.AP_STRAT_004, "Preference Trap", AntiPatternCategory.STRATEGIC, "CHECK-022", "Content crafted to manipulate LLM behavior (trust laundering)"),
]
```

---

## Cross-Reference: Validation Check IDs → Diagnostic Codes → Anti-Pattern IDs

The validation engine uses three overlapping ID systems inherited from different research phases. This mapping table makes the relationships explicit so that any finding can be traced from its v0.0.4a/b/c check ID through the diagnostic code it triggers to the anti-pattern it may indicate.

**How to read this table:** A validation check (left column) produces a diagnostic code (middle column) when it fires. Some diagnostics also indicate an anti-pattern (right column) — anti-patterns are quality scoring deductions, while diagnostic codes are validation pipeline outputs. Not every diagnostic code has a corresponding anti-pattern, and not every anti-pattern has a single diagnostic code trigger.

| v0.0.4a/b/c Check ID | DiagnosticCode | Anti-Pattern ID | Relationship |
|-----------------------|----------------|-----------------|-------------|
| **Structural checks (v0.0.4a)** | | | |
| ENC-001 (UTF-8 encoding) | E003_INVALID_ENCODING | AP-CRIT-003 (Encoding Disaster) | Encoding failure → error + critical anti-pattern |
| ENC-002 (LF line endings) | E004_INVALID_LINE_ENDINGS | AP-CRIT-003 (Encoding Disaster) | Line ending failure → error + critical anti-pattern |
| STR-001 (single H1 title) | E001_NO_H1_TITLE, E002_MULTIPLE_H1 | AP-CRIT-002 (Structure Chaos) | H1 violations → error + critical anti-pattern |
| STR-002 (blockquote present) | W001_MISSING_BLOCKQUOTE | — | Warning only; 55% compliance makes it non-gating |
| STR-003 (Master Index first) | W009_NO_MASTER_INDEX | — | Warning; DECISION-010 justifies priority |
| STR-004 (section ordering) | W008_SECTION_ORDER_NON_CANONICAL | AP-STRUCT-004 (Section Shuffle) | Non-canonical order → warning + structural anti-pattern |
| MD-001 (valid Markdown syntax) | E005_INVALID_MARKDOWN | AP-CRIT-002 (Structure Chaos) | Parse failure → error + critical anti-pattern |
| LNK-002 (well-formed URLs) | E006_BROKEN_LINKS | AP-CRIT-004 (Link Void) | Broken links → error + critical anti-pattern |
| LNK-003 (absolute vs. relative) | I004_RELATIVE_URLS_DETECTED | — | Informational only |
| NAM-001 (canonical names) | W002_NON_CANONICAL_SECTION_NAME | AP-STRUCT-005 (Naming Nebula) | Non-canonical → warning + structural anti-pattern |
| SIZ-001 (token budget tier) | W010_TOKEN_BUDGET_EXCEEDED | AP-STRAT-002 (Monolith Monster) | Budget exceeded → warning; extreme cases → strategic anti-pattern |
| SIZ-003 (max size 100K tokens) | E008_EXCEEDS_SIZE_LIMIT | AP-STRAT-002 (Monolith Monster) | Hard limit → error + strategic anti-pattern |
| **Content checks (v0.0.4b)** | | | |
| CNT-004 (link descriptions) | W003_LINK_MISSING_DESCRIPTION | AP-CONT-004 (Link Desert) | Missing descriptions → warning + content anti-pattern |
| CNT-005 (unique descriptions) | W006_FORMULAIC_DESCRIPTIONS | AP-CONT-007 (Formulaic Description) | Repetitive patterns → warning + content anti-pattern |
| CNT-007 (code examples present) | W004_NO_CODE_EXAMPLES | AP-CONT-006 (Example Void) | No code → warning + content anti-pattern |
| CNT-008 (language specifiers) | W005_CODE_NO_LANGUAGE | — | Warning only; no dedicated anti-pattern |
| CNT-010 (LLM Instructions) | I001_NO_LLM_INSTRUCTIONS | AP-CONT-008 (Silent Agent) | Missing instructions → info + content anti-pattern |
| CNT-013 (concept definitions) | I002_NO_CONCEPT_DEFINITIONS | — | Informational only; L4 extended feature |
| CNT-014 (jargon definitions) | I007_JARGON_WITHOUT_DEFINITION | AP-CONT-003 (Jargon Jungle) | Undefined jargon → info + content anti-pattern |
| CNT-015 (version metadata) | W007_MISSING_VERSION_METADATA | AP-CONT-009 (Versionless Drift) | No version → warning + content anti-pattern |
| **Anti-pattern checks (v0.0.4c)** | | | |
| CHECK-001 (Ghost File) | E007_EMPTY_FILE | AP-CRIT-001 (Ghost File) | Empty file → error + critical anti-pattern |
| CHECK-002 (Structure Chaos) | E001/E002/E005 (structural errors) | AP-CRIT-002 (Structure Chaos) | Aggregate of multiple structural errors |
| CHECK-003 (Encoding Disaster) | E003/E004 (encoding errors) | AP-CRIT-003 (Encoding Disaster) | Aggregate of encoding errors |
| CHECK-004 (Link Void) | E006_BROKEN_LINKS | AP-CRIT-004 (Link Void) | All/most links broken |
| CHECK-005 (Sitemap Dump) | — (detected by link-to-section ratio heuristic) | AP-STRUCT-001 (Sitemap Dump) | No dedicated diagnostic; heuristic-based |
| CHECK-006 (Orphaned Sections) | W011_EMPTY_SECTIONS | AP-STRUCT-002 (Orphaned Sections) | Empty sections → warning + structural anti-pattern |
| CHECK-007 (Duplicate Identity) | — (detected by name similarity analysis) | AP-STRUCT-003 (Duplicate Identity) | No dedicated diagnostic; heuristic-based |
| CHECK-008 (Section Shuffle) | W008_SECTION_ORDER_NON_CANONICAL | AP-STRUCT-004 (Section Shuffle) | Same as STR-004 |
| CHECK-009 (Naming Nebula) | W002_NON_CANONICAL_SECTION_NAME | AP-STRUCT-005 (Naming Nebula) | Same as NAM-001 |
| CHECK-010 (Copy-Paste Plague) | — (detected by content similarity analysis) | AP-CONT-001 (Copy-Paste Plague) | No dedicated diagnostic; heuristic-based |
| CHECK-011 (Blank Canvas) | W011_EMPTY_SECTIONS | AP-CONT-002 (Blank Canvas) | Same diagnostic as CHECK-006, different anti-pattern |
| CHECK-012 (Jargon Jungle) | I007_JARGON_WITHOUT_DEFINITION | AP-CONT-003 (Jargon Jungle) | Same as CNT-014 |
| CHECK-013 (Link Desert) | W003_LINK_MISSING_DESCRIPTION | AP-CONT-004 (Link Desert) | Same as CNT-004 |
| CHECK-014 (Outdated Oracle) | — (detected by date heuristic) | AP-CONT-005 (Outdated Oracle) | No dedicated diagnostic; requires date parsing |
| CHECK-015 (Example Void) | W004_NO_CODE_EXAMPLES | AP-CONT-006 (Example Void) | Same as CNT-007 |
| CHECK-016 (Automation Obsession) | — (detected by signature patterns) | AP-STRAT-001 (Automation Obsession) | No dedicated diagnostic; Mintlify/Yoast signatures |
| CHECK-017 (Monolith Monster) | E008_EXCEEDS_SIZE_LIMIT | AP-STRAT-002 (Monolith Monster) | Same as SIZ-003 |
| CHECK-018 (Meta-Documentation Spiral) | — (detected by self-referential content) | AP-STRAT-003 (Meta-Documentation Spiral) | No dedicated diagnostic; content analysis |
| CHECK-019 (Formulaic Description) | W006_FORMULAIC_DESCRIPTIONS | AP-CONT-007 (Formulaic Description) | Same as CNT-005 |
| CHECK-020 (Silent Agent) | I001_NO_LLM_INSTRUCTIONS | AP-CONT-008 (Silent Agent) | Same as CNT-010 |
| CHECK-021 (Versionless Drift) | W007_MISSING_VERSION_METADATA | AP-CONT-009 (Versionless Drift) | Same as CNT-015 |
| CHECK-022 (Preference Trap) | — (detected by manipulation patterns) | AP-STRAT-004 (Preference Trap) | No dedicated diagnostic; behavioral analysis |

**Key observations:**

- **26 diagnostic codes** map to **22 anti-patterns** through **~35 validation check IDs** — a many-to-many relationship.
- **7 anti-patterns have no dedicated diagnostic code** (CHECK-005, -007, -010, -014, -016, -018, -022). These require heuristic detection logic that will be implemented in v0.2.4. Their anti-pattern registry entries exist in v0.1.2, but their detection is deferred.
- **Some diagnostics map to multiple anti-patterns** (e.g., W011 maps to both Orphaned Sections and Blank Canvas — same symptom, different severity interpretation depending on whether the section has a header vs. placeholder text).
- The v0.0.4a/b check IDs (structural prefix format like `STR-001`, `CNT-004`) represent the original research taxonomy. The CHECK-NNN IDs (v0.0.4c) represent the anti-pattern catalog. Both systems are preserved in the diagnostic code docstrings for full traceability.

---

## Design Decisions Applied

| ID | Decision | How Applied in v0.1.2a |
|----|----------|----------------------|
| DECISION-012 | Canonical Section Names (11 standard names from 450+ projects) | `CanonicalSectionName` enum with 11 names + alias mapping |
| DECISION-013 | Token Budget Tiers as First-Class Constraint | `TokenBudgetTier`, token zone thresholds |
| DECISION-016 | Four-Category Anti-Pattern Severity Classification | `AntiPatternCategory` enum + 22-entry registry |

---

## Exit Criteria

- [ ] All 26 diagnostic codes (8E/11W/7I) defined in `DiagnosticCode` enum
- [ ] `DiagnosticCode.severity` property returns correct `Severity` for all codes
- [ ] All 11 canonical section names defined in `CanonicalSectionName` enum
- [ ] All 22 anti-patterns defined in `ANTI_PATTERN_REGISTRY`
- [ ] Cross-reference mapping table covers all ~35 validation check IDs
- [ ] `black --check src/docstratum/schema/diagnostics.py src/docstratum/schema/constants.py` passes
- [ ] `ruff check src/docstratum/schema/diagnostics.py src/docstratum/schema/constants.py` passes
