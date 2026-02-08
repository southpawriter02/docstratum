"""Error code registry for the DocStratum validation engine.

Defines the complete diagnostic code catalog derived from the v0.0.1a
enrichment pass. Every validation finding references a DiagnosticCode
that includes the severity level, a human-readable message template,
and a remediation hint.

The code format follows the pattern: {SEVERITY_PREFIX}{NUMBER}
    E001-E008:  Errors (8 codes) — Structural failures that prevent valid parsing
    W001-W011:  Warnings (11 codes) — Deviations from best practices
    I001-I007:  Informational (7 codes) — Observations and suggestions

[v0.0.7] Ecosystem pivot extensions (12 new codes, total 38):
    E009-E010:  Errors (2 codes) — Ecosystem-level structural failures
    W012-W018:  Warnings (7 codes) — Ecosystem-level quality deviations
    I008-I010:  Informational (3 codes) — Ecosystem observations and suggestions

Updated totals: 10 ERROR, 18 WARNING, 10 INFO = 38 total codes.

Research basis:
    v0.0.1a §Error Code Registry (enrichment pass)
    v0.0.4a §Structural Checks (ENC-001/002, STR-001-005, MD-001-003, etc.)
    v0.0.4b §Content Checks (CNT-001-015)
    v0.0.4c §Anti-Pattern Checks (CHECK-001-022)
    v0.0.7 §5 (New Diagnostic Codes — ecosystem-level)

Traces to: FR-078 (12 new ecosystem diagnostic codes)
"""

import logging
from enum import StrEnum

logger = logging.getLogger(__name__)


class Severity(StrEnum):
    """Diagnostic severity levels.

    Aligned with the three-tier output format mandated by NFR-006
    (clear CLI errors with severity + code + message + remediation).

    Attributes:
        ERROR: Structural failure that prevents valid parsing or breaks spec conformance.
               Maps to validation levels L0-L1 (parseable, structural).
        WARNING: Deviation from best practices that degrades quality but doesn't break parsing.
                 Maps to validation levels L2-L3 (content, best practices).
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
        E001-E008: Structural errors (v0.0.4a checks ENC-001/002, STR-001-005, MD-001, LNK-002)
        W001-W011: Quality warnings (v0.0.4a/b checks NAM-001, CNT-004-009, CNT-015, SIZ-001)
        I001-I007: Informational (v0.0.4b checks CNT-010-014, classification notes)
        [v0.0.7] E009-E010: Ecosystem errors (ecosystem structural failures)
        [v0.0.7] W012-W018: Ecosystem warnings (ecosystem quality deviations)
        [v0.0.7] I008-I010: Ecosystem info (ecosystem observations)

    Usage:
        from docstratum.schema.diagnostics import DiagnosticCode

        code = DiagnosticCode.E001_NO_H1_TITLE
        print(code.severity)      # Severity.ERROR
        print(code.message)       # "No H1 title found..."
        print(code.remediation)   # "Add a single H1 title..."

    Example:
        >>> code = DiagnosticCode.E001_NO_H1_TITLE
        >>> code.severity
        <Severity.ERROR: 'ERROR'>
        >>> code.value
        'E001'
    """

    def __new__(cls, value: str, doc: str = "") -> "DiagnosticCode":
        """Initialize enum member with docstring attached."""
        member = str.__new__(cls, value)
        member._value_ = value
        member.__doc__ = doc.strip()
        return member

    # ── ERRORS (E001-E008): Structural failures ──────────────────────────
    # These prevent the file from passing L1 (Structural) validation.

    E001_NO_H1_TITLE = (
        "E001",
        """No H1 title found. Every llms.txt file MUST begin with exactly one H1 title.
        Maps to: STR-001 (v0.0.4a). Severity: ERROR.
        Remediation: Add a single '# Title' as the first line of the file.""",
    )

    E002_MULTIPLE_H1 = (
        "E002",
        """Multiple H1 titles found. The spec requires exactly one H1.
        Maps to: STR-001 (v0.0.4a). Severity: ERROR.
        Remediation: Remove all but the first H1 title. Use H2 for section headers.""",
    )

    E003_INVALID_ENCODING = (
        "E003",
        """File is not valid UTF-8 encoding.
        Maps to: ENC-001 (v0.0.4a). Severity: ERROR.
        Remediation: Convert the file to UTF-8 encoding. Remove any BOM markers.""",
    )

    E004_INVALID_LINE_ENDINGS = (
        "E004",
        """File uses non-LF line endings (CR or CRLF detected).
        Maps to: ENC-002 (v0.0.4a). Severity: ERROR.
        Remediation: Convert line endings to LF (Unix-style). Most editors have this option.""",
    )

    E005_INVALID_MARKDOWN = (
        "E005",
        """File contains invalid Markdown syntax that prevents parsing.
        Maps to: MD-001 (v0.0.4a). Severity: ERROR.
        Remediation: Fix Markdown syntax errors. Use a Markdown linter to identify issues.""",
    )

    E006_BROKEN_LINKS = (
        "E006",
        """Section contains links with empty or malformed URLs.
        Maps to: LNK-002 (v0.0.4a), CHECK-004 (v0.0.4c Ghost File anti-pattern). Severity: ERROR.
        Remediation: Fix or remove links with empty href values. Ensure all URLs are well-formed.""",
    )

    E007_EMPTY_FILE = (
        "E007",
        """File is empty or contains only whitespace.
        Maps to: CHECK-001 (v0.0.4c Ghost File anti-pattern). Severity: ERROR.
        Remediation: Add content to the file. At minimum: H1 title, blockquote, one H2 section.""",
    )

    E008_EXCEEDS_SIZE_LIMIT = (
        "E008",
        """File exceeds the maximum recommended size (>100K tokens).
        Maps to: SIZ-003 (v0.0.4a), CHECK-003 (v0.0.4c Monolith Monster). Severity: ERROR.
        Remediation: Decompose into a tiered file strategy (index + full + per-section files).""",
    )

    # ── WARNINGS (W001-W011): Quality deviations ────────────────────────
    # These prevent the file from achieving L3 (Best Practices) validation.

    W001_MISSING_BLOCKQUOTE = (
        "W001",
        """No blockquote description found after the H1 title.
        Maps to: STR-002 (v0.0.4a). Severity: WARNING.
        Note: 55% real-world compliance (v0.0.2 enrichment), so this is a warning, not an error.
        Remediation: Add a '> description' blockquote immediately after the H1 title.""",
    )

    W002_NON_CANONICAL_SECTION_NAME = (
        "W002",
        """Section name does not match any of the 11 canonical names.
        Maps to: NAM-001 (v0.0.4a). Severity: WARNING.
        Remediation: Use canonical names where possible (see CanonicalSectionName enum).""",
    )

    W003_LINK_MISSING_DESCRIPTION = (
        "W003",
        """Link entry has no description text (bare URL only).
        Maps to: CNT-004 (v0.0.4b), CHECK-010 (v0.0.4c Link Desert). Severity: WARNING.
        Remediation: Add a description after the link: '- [Title](url): Description of the page'.""",
    )

    W004_NO_CODE_EXAMPLES = (
        "W004",
        """File contains no code examples (no fenced code blocks found).
        Maps to: CNT-007 (v0.0.4b). Severity: WARNING.
        Note: Code examples are the strongest quality predictor (r ~ 0.65, v0.0.2c).
        Remediation: Add code examples with language specifiers (```python, ```bash, etc.).""",
    )

    W005_CODE_NO_LANGUAGE = (
        "W005",
        """Code block found without a language specifier.
        Maps to: CNT-008 (v0.0.4b). Severity: WARNING.
        Remediation: Add a language identifier after the opening triple backticks.""",
    )

    W006_FORMULAIC_DESCRIPTIONS = (
        "W006",
        """Multiple sections use identical or near-identical description patterns.
        Maps to: CNT-005 (v0.0.4b), CHECK-015 (v0.0.4c Formulaic Description). Severity: WARNING.
        Remediation: Write unique, specific descriptions for each section.""",
    )

    W007_MISSING_VERSION_METADATA = (
        "W007",
        """No version or last-updated metadata found in the file.
        Maps to: CNT-015 (v0.0.4b). Severity: WARNING.
        Remediation: Add version metadata (e.g., 'Last updated: 2026-02-06').""",
    )

    W008_SECTION_ORDER_NON_CANONICAL = (
        "W008",
        """Sections do not follow the canonical 10-step ordering.
        Maps to: STR-004 (v0.0.4a). Severity: WARNING.
        Remediation: Reorder sections to match canonical sequence (see v0.0.4a §6).""",
    )

    W009_NO_MASTER_INDEX = (
        "W009",
        """No Master Index found as the first H2 section.
        Maps to: STR-003 (v0.0.4a), DECISION-010. Severity: WARNING.
        Note: Files with Master Index achieve 87% vs. 31% LLM success rate.
        Remediation: Add a Master Index as the first H2 section with navigation links.""",
    )

    W010_TOKEN_BUDGET_EXCEEDED = (
        "W010",
        """File exceeds the recommended token budget for its tier.
        Maps to: SIZ-001 (v0.0.4a), DECISION-013. Severity: WARNING.
        Remediation: Trim content to stay within the tier's token budget.""",
    )

    W011_EMPTY_SECTIONS = (
        "W011",
        """One or more sections contain no meaningful content (placeholder text only).
        Maps to: CHECK-011 (v0.0.4c Blank Canvas anti-pattern). Severity: WARNING.
        Remediation: Add content or remove empty sections. Placeholder sections waste tokens.""",
    )

    # ── INFORMATIONAL (I001-I007): Suggestions ──────────────────────────
    # These are non-blocking observations for L4 (DocStratum Extended).

    I001_NO_LLM_INSTRUCTIONS = (
        "I001",
        """No LLM Instructions section found.
        Maps to: CNT-010 (v0.0.4b). Severity: INFO.
        Note: 0% current adoption (v0.0.2), but strongest quality differentiator.
        Remediation: Add an LLM Instructions section with positive/negative directives.""",
    )

    I002_NO_CONCEPT_DEFINITIONS = (
        "I002",
        """No structured concept definitions found.
        Maps to: CNT-013 (v0.0.4b). Severity: INFO.
        Remediation: Add concept definitions with IDs, relationships, and aliases.""",
    )

    I003_NO_FEW_SHOT_EXAMPLES = (
        "I003",
        """No few-shot Q&A examples found.
        Maps to: v0.0.1b Gap #2 (P0). Severity: INFO.
        Remediation: Add intent-tagged Q&A pairs linked to concepts.""",
    )

    I004_RELATIVE_URLS_DETECTED = (
        "I004",
        """Relative URLs found in link entries (may need resolution).
        Maps to: LNK-003 (v0.0.4a). Severity: INFO.
        Remediation: Convert relative URLs to absolute or document the base URL.""",
    )

    I005_TYPE_2_FULL_DETECTED = (
        "I005",
        """File classified as Type 2 Full (inline documentation dump, >250 KB).
        Maps to: Document Type Classification (v0.0.1a enrichment). Severity: INFO.
        Note: Type 2 files are not spec-conformant but are valid in MCP contexts.
        Remediation: Consider creating a Type 1 Index companion file.""",
    )

    I006_OPTIONAL_SECTIONS_UNMARKED = (
        "I006",
        """Optional sections not explicitly marked with token estimates.
        Maps to: DECISION-011 (v0.0.4d). Severity: INFO.
        Remediation: Mark optional sections so consumers can skip them to save context.""",
    )

    I007_JARGON_WITHOUT_DEFINITION = (
        "I007",
        """Domain-specific jargon used without inline definition.
        Maps to: CNT-014 (v0.0.4b). Severity: INFO.
        Remediation: Define jargon inline or link to a concept definition.""",
    )

    # ── [v0.0.7] ECOSYSTEM ERRORS (E009-E010): Ecosystem structural failures ─
    # These indicate fundamental ecosystem-level problems. Emitted by the
    # Ecosystem Validation stage (Stage 4 of the ecosystem pipeline).

    E009_NO_INDEX_FILE = (
        "E009",
        """Ecosystem has no llms.txt file (the required root).
        Maps to: v0.0.7 §5.1 (Ecosystem-Level Error Codes). Severity: ERROR.
        Note: An ecosystem without an index file has no entry point for AI agents.
        Remediation: Create an llms.txt file in the project root with an H1 title and section links.""",
    )

    E010_ORPHANED_ECOSYSTEM_FILE = (
        "E010",
        """A file in the ecosystem is not referenced by any other file.
        Maps to: v0.0.7 §5.1 (Ecosystem-Level Error Codes). Severity: ERROR.
        Note: Orphaned files exist in the ecosystem but are invisible to AI agents navigating via the index.
        Remediation: Add a link to this file from llms.txt or from another content page.""",
    )

    # ── [v0.0.7] ECOSYSTEM WARNINGS (W012-W018): Ecosystem quality deviations ─
    # These indicate ecosystem-level quality issues that degrade the
    # documentation system's effectiveness for AI agents.

    W012_BROKEN_CROSS_FILE_LINK = (
        "W012",
        """A link in one file references another file that doesn't exist or is unreachable.
        Maps to: v0.0.7 §5.2 (Ecosystem-Level Warning Codes). Severity: WARNING.
        Note: Cross-file diagnostic — includes source_file and related_file context.
        Remediation: Fix the broken link URL or create the missing target file.""",
    )

    W013_MISSING_AGGREGATE = (
        "W013",
        """Index file token count suggests a project large enough to benefit from llms-full.txt, but none exists.
        Maps to: v0.0.7 §5.2 (Ecosystem-Level Warning Codes). Severity: WARNING.
        Note: Threshold is >4,500 tokens of documentation (Comprehensive tier).
        Remediation: Create an llms-full.txt file containing the full content of all documentation pages.""",
    )

    W014_AGGREGATE_INCOMPLETE = (
        "W014",
        """llms-full.txt does not contain content from all files referenced in the index.
        Maps to: v0.0.7 §5.2 (Ecosystem-Level Warning Codes). Severity: WARNING.
        Note: The aggregate should be a superset of all content pages for large-window model consumption.
        Remediation: Regenerate llms-full.txt to include content from all ecosystem files.""",
    )

    W015_INCONSISTENT_PROJECT_NAME = (
        "W015",
        """H1 title differs between files in the ecosystem.
        Maps to: v0.0.7 §5.2 (Ecosystem-Level Warning Codes). Severity: WARNING.
        Note: Inconsistent naming confuses AI agents about project identity.
        Remediation: Ensure all files use the same project name in their H1 title.""",
    )

    W016_INCONSISTENT_VERSIONING = (
        "W016",
        """Version metadata differs between files (e.g., one says v2.1, another says v2.0).
        Maps to: v0.0.7 §5.2 (Ecosystem-Level Warning Codes). Severity: WARNING.
        Note: Version drift indicates stale documentation that may provide outdated guidance.
        Remediation: Update all files to reflect the current version number.""",
    )

    W017_REDUNDANT_CONTENT = (
        "W017",
        """Significant content duplication between files (>60% overlap) beyond expected index-to-full duplication.
        Maps to: v0.0.7 §5.2 (Ecosystem-Level Warning Codes). Severity: WARNING.
        Note: Redundancy wastes context window tokens and risks inconsistency.
        Remediation: Refactor duplicated content into a single source and cross-reference.""",
    )

    W018_UNBALANCED_TOKEN_DISTRIBUTION = (
        "W018",
        """One file consumes >70% of total ecosystem tokens while others are near-empty.
        Maps to: v0.0.7 §5.2 (Ecosystem-Level Warning Codes). Severity: WARNING.
        Note: Defeats the purpose of a multi-file strategy.
        Remediation: Distribute content more evenly across files or consolidate into fewer files.""",
    )

    # ── [v0.0.7] ECOSYSTEM INFORMATIONAL (I008-I010): Observations ───────────
    # Non-blocking suggestions for ecosystem improvement.

    I008_NO_INSTRUCTION_FILE = (
        "I008",
        """No llms-instructions.txt or LLM Instructions section exists in the ecosystem.
        Maps to: v0.0.7 §5.3 (Ecosystem-Level Informational Codes). Severity: INFO.
        Note: Instruction files are the strongest quality differentiator for agent behavior.
        Remediation: Add an LLM Instructions section to llms.txt or create a dedicated llms-instructions.txt file.""",
    )

    I009_CONTENT_COVERAGE_GAP = (
        "I009",
        """The index references section categories for which no detailed content page exists.
        Maps to: v0.0.7 §5.3 (Ecosystem-Level Informational Codes). Severity: INFO.
        Note: Coverage gaps indicate areas where AI agents will lack detailed documentation.
        Remediation: Create content pages for the missing section categories.""",
    )

    I010_ECOSYSTEM_SINGLE_FILE = (
        "I010",
        """The entire ecosystem consists of just llms.txt with no companion files.
        Maps to: v0.0.7 §5.3 (Ecosystem-Level Informational Codes). Severity: INFO.
        Note: Valid but limited — single-file ecosystems cannot leverage multi-file strategies.
        Remediation: Consider adding llms-full.txt and individual content pages for deeper coverage.""",
    )

    @property
    def severity(self) -> Severity:
        """Derive severity from the code prefix (E=Error, W=Warning, I=Info).

        Returns:
            The Severity enum value corresponding to this code's prefix.

        Example:
            >>> DiagnosticCode.E001_NO_H1_TITLE.severity
            <Severity.ERROR: 'ERROR'>
        """
        prefix = self.value[0]
        return {
            "E": Severity.ERROR,
            "W": Severity.WARNING,
            "I": Severity.INFO,
        }[prefix]

    @property
    def code_number(self) -> int:
        """Extract the numeric portion of the code (e.g., E001 -> 1).

        Returns:
            The integer portion of the diagnostic code.

        Example:
            >>> DiagnosticCode.W011_EMPTY_SECTIONS.code_number
            11
        """
        return int(self.value[1:])

    @property
    def message(self) -> str:
        """Return the first line of the docstring as the message template.

        Returns:
            The human-readable message for this diagnostic code.

        Example:
            >>> DiagnosticCode.E007_EMPTY_FILE.message
            'File is empty or contains only whitespace.'
        """
        if self.__doc__:
            return self.__doc__.split("\n")[0]
        return f"Diagnostic {self.value}"

    @property
    def remediation(self) -> str:
        """Extract the remediation hint from the docstring.

        Returns:
            The remediation guidance for this diagnostic code.

        Example:
            >>> DiagnosticCode.E007_EMPTY_FILE.remediation
            'Add content to the file. At minimum: H1 title, blockquote, one H2 section.'
        """
        if self.__doc__:
            for line in self.__doc__.split("\n"):
                stripped = line.strip()
                if stripped.startswith("Remediation:"):
                    # Use standard string slice for performance after check
                    return stripped[12:].strip()
        return "No remediation available."
