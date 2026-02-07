"""Validation result models for the DocStratum validation engine.

Represents the output of the 5-level validation pipeline (L0-L4).
Each level builds on the previous:

    L0 -- Parseable:           File can be read and parsed as Markdown.
    L1 -- Structurally Valid:  H1 title exists, sections use H2, links are well-formed.
    L2 -- Content Quality:     Descriptions are non-empty, URLs resolve, no placeholders.
    L3 -- Best Practices:      Canonical names, Master Index, code examples, token budgets.
    L4 -- DocStratum Extended: Concept definitions, few-shot examples, LLM instructions.

Research basis:
    v0.0.1b S.Validation Level Definitions
    v0.0.4a S.Structural Checks (20 checks -> L0, L1)
    v0.0.4b S.Content Checks (15 checks -> L2, L3)
    v0.0.4c S.Anti-Pattern Checks (22 checks -> cross-level deductions)
"""

import logging
from datetime import datetime
from enum import IntEnum

from pydantic import BaseModel, Field

from docstratum.schema.diagnostics import DiagnosticCode, Severity

logger = logging.getLogger(__name__)


class ValidationLevel(IntEnum):
    """The 5-level validation pipeline.

    Levels are cumulative -- achieving L3 means L0, L1, and L2 also pass.
    The highest level where ALL checks pass is the file's validation level.

    Attributes:
        L0_PARSEABLE: File can be read and parsed as Markdown.
        L1_STRUCTURAL: Basic structural elements present (H1, H2s, links).
        L2_CONTENT: Content quality checks pass (non-empty, resolving).
        L3_BEST_PRACTICES: Best practices followed (canonical names, examples).
        L4_DOCSTRATUM_EXTENDED: DocStratum enrichment present (concepts, few-shot).
    """

    L0_PARSEABLE = 0
    L1_STRUCTURAL = 1
    L2_CONTENT = 2
    L3_BEST_PRACTICES = 3
    L4_DOCSTRATUM_EXTENDED = 4


class ValidationDiagnostic(BaseModel):
    """A single validation finding (error, warning, or info).

    Produced by the validation pipeline for each check that fails or
    triggers a note. Includes the diagnostic code, source location,
    context snippet, and remediation hint.

    Attributes:
        code: The DiagnosticCode enum value (e.g., E001_NO_H1_TITLE).
        severity: Derived from the code prefix (ERROR, WARNING, INFO).
        message: Human-readable description of the finding.
        remediation: Suggested fix.
        line_number: Line in the source file where the issue was found (1-indexed).
        column: Column number if applicable (1-indexed), or None.
        context: Snippet of the surrounding source text for display.
        level: Which validation level this diagnostic belongs to.
        check_id: The v0.0.4 check ID (e.g., "STR-001", "CNT-007").

    Example:
        diagnostic = ValidationDiagnostic(
            code=DiagnosticCode.W001_MISSING_BLOCKQUOTE,
            severity=Severity.WARNING,
            message="No blockquote description found after the H1 title.",
            remediation="Add a '> description' blockquote after the H1.",
            line_number=2,
            level=ValidationLevel.L1_STRUCTURAL,
            check_id="STR-002",
        )
    """

    code: DiagnosticCode = Field(
        description="Diagnostic code from the error code registry.",
    )
    severity: Severity = Field(
        description="ERROR, WARNING, or INFO.",
    )
    message: str = Field(
        description="Human-readable finding description.",
    )
    remediation: str = Field(
        default="",
        description="Suggested fix for this issue.",
    )
    line_number: int | None = Field(
        default=None,
        ge=1,
        description="Source line number (1-indexed). None for file-level issues.",
    )
    column: int | None = Field(
        default=None,
        ge=1,
        description="Source column number (1-indexed). None if not applicable.",
    )
    context: str | None = Field(
        default=None,
        max_length=500,
        description="Source text snippet surrounding the issue.",
    )
    level: ValidationLevel = Field(
        description="Which validation level this diagnostic belongs to.",
    )
    check_id: str | None = Field(
        default=None,
        description="v0.0.4 check ID (e.g., 'STR-001', 'CNT-007', 'CHECK-011').",
    )


class ValidationResult(BaseModel):
    """Complete output of the validation pipeline for a single file.

    Contains all diagnostics, the highest validation level achieved,
    and per-level pass/fail status. This is the primary output model
    of the ``docstratum-validate`` command.

    Attributes:
        level_achieved: Highest validation level where ALL checks pass.
        diagnostics: All findings (errors, warnings, info) from the pipeline.
        levels_passed: Dict mapping each level to pass/fail status.
        total_errors: Count of ERROR-severity diagnostics.
        total_warnings: Count of WARNING-severity diagnostics.
        total_info: Count of INFO-severity diagnostics.
        validated_at: Timestamp of validation.
        source_filename: File that was validated.

    Example:
        result = ValidationResult(
            level_achieved=ValidationLevel.L1_STRUCTURAL,
            diagnostics=[...],
            levels_passed={
                ValidationLevel.L0_PARSEABLE: True,
                ValidationLevel.L1_STRUCTURAL: True,
                ValidationLevel.L2_CONTENT: False,
                ValidationLevel.L3_BEST_PRACTICES: False,
                ValidationLevel.L4_DOCSTRATUM_EXTENDED: False,
            },
        )

    Traces to: FR-003 (5-level pipeline), FR-004 (error reporting)
    """

    level_achieved: ValidationLevel = Field(
        description="Highest level where all checks pass.",
    )
    diagnostics: list[ValidationDiagnostic] = Field(
        default_factory=list,
        description="All validation findings.",
    )
    levels_passed: dict[ValidationLevel, bool] = Field(
        default_factory=lambda: {level: False for level in ValidationLevel},
        description="Per-level pass/fail status.",
    )
    validated_at: datetime = Field(
        default_factory=datetime.now,
        description="When validation was performed.",
    )
    source_filename: str = Field(
        default="llms.txt",
        description="File that was validated.",
    )

    @property
    def total_errors(self) -> int:
        """Count of ERROR-severity diagnostics."""
        return sum(1 for d in self.diagnostics if d.severity == Severity.ERROR)

    @property
    def total_warnings(self) -> int:
        """Count of WARNING-severity diagnostics."""
        return sum(1 for d in self.diagnostics if d.severity == Severity.WARNING)

    @property
    def total_info(self) -> int:
        """Count of INFO-severity diagnostics."""
        return sum(1 for d in self.diagnostics if d.severity == Severity.INFO)

    @property
    def is_valid(self) -> bool:
        """Whether the file achieves at least L0 (parseable)."""
        return self.levels_passed.get(ValidationLevel.L0_PARSEABLE, False)

    @property
    def errors(self) -> list["ValidationDiagnostic"]:
        """All ERROR-severity diagnostics."""
        return [d for d in self.diagnostics if d.severity == Severity.ERROR]

    @property
    def warnings(self) -> list["ValidationDiagnostic"]:
        """All WARNING-severity diagnostics."""
        return [d for d in self.diagnostics if d.severity == Severity.WARNING]
