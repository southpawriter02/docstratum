"""Tests for validation result models (validation.py)."""

import pytest
from pydantic import ValidationError

from docstratum.schema.diagnostics import DiagnosticCode, Severity
from docstratum.schema.validation import (
    ValidationDiagnostic,
    ValidationLevel,
    ValidationResult,
)

# ── ValidationLevel ──────────────────────────────────────────────────


@pytest.mark.unit
def test_validation_level_values():
    """Verify ValidationLevel has exactly 5 members with correct int values."""
    assert len(ValidationLevel) == 5
    assert ValidationLevel.L0_PARSEABLE == 0
    assert ValidationLevel.L1_STRUCTURAL == 1
    assert ValidationLevel.L2_CONTENT == 2
    assert ValidationLevel.L3_BEST_PRACTICES == 3
    assert ValidationLevel.L4_DOCSTRATUM_EXTENDED == 4


@pytest.mark.unit
def test_validation_level_is_int_enum():
    """Verify ValidationLevel members are comparable to plain integers."""
    assert isinstance(ValidationLevel.L0_PARSEABLE, int)
    assert ValidationLevel.L2_CONTENT > ValidationLevel.L1_STRUCTURAL


# ── ValidationDiagnostic ─────────────────────────────────────────────


@pytest.mark.unit
def test_validation_diagnostic_creation_required_fields():
    """Verify construction with required fields and defaults."""
    # Arrange / Act
    diag = ValidationDiagnostic(
        code=DiagnosticCode.E001_NO_H1_TITLE,
        severity=Severity.ERROR,
        message="No H1 title found.",
        level=ValidationLevel.L1_STRUCTURAL,
    )

    # Assert
    assert diag.code == DiagnosticCode.E001_NO_H1_TITLE
    assert diag.severity == Severity.ERROR
    assert diag.message == "No H1 title found."
    assert diag.remediation == ""
    assert diag.line_number is None
    assert diag.column is None
    assert diag.context is None
    assert diag.level == ValidationLevel.L1_STRUCTURAL
    assert diag.check_id is None


@pytest.mark.unit
def test_validation_diagnostic_creation_all_fields():
    """Verify construction with all fields explicitly set."""
    diag = ValidationDiagnostic(
        code=DiagnosticCode.W001_MISSING_BLOCKQUOTE,
        severity=Severity.WARNING,
        message="No blockquote description found.",
        remediation="Add a '> description' blockquote after the H1.",
        line_number=2,
        column=1,
        context="> Missing blockquote here",
        level=ValidationLevel.L1_STRUCTURAL,
        check_id="STR-002",
    )

    assert diag.remediation == "Add a '> description' blockquote after the H1."
    assert diag.line_number == 2
    assert diag.column == 1
    assert diag.context == "> Missing blockquote here"
    assert diag.check_id == "STR-002"


@pytest.mark.unit
def test_validation_diagnostic_rejects_invalid_line_number():
    """Verify line_number enforces ge=1 constraint."""
    with pytest.raises(ValidationError):
        ValidationDiagnostic(
            code=DiagnosticCode.E001_NO_H1_TITLE,
            severity=Severity.ERROR,
            message="Test",
            level=ValidationLevel.L0_PARSEABLE,
            line_number=0,
        )


@pytest.mark.unit
def test_validation_diagnostic_rejects_invalid_column():
    """Verify column enforces ge=1 constraint."""
    with pytest.raises(ValidationError):
        ValidationDiagnostic(
            code=DiagnosticCode.E001_NO_H1_TITLE,
            severity=Severity.ERROR,
            message="Test",
            level=ValidationLevel.L0_PARSEABLE,
            column=0,
        )


# ── ValidationResult ─────────────────────────────────────────────────


def _make_diagnostic(
    code: DiagnosticCode,
    severity: Severity,
    level: ValidationLevel = ValidationLevel.L1_STRUCTURAL,
) -> ValidationDiagnostic:
    """Helper to create a minimal ValidationDiagnostic."""
    return ValidationDiagnostic(
        code=code,
        severity=severity,
        message=f"Test diagnostic for {code.value}",
        level=level,
    )


@pytest.mark.unit
def test_validation_result_defaults():
    """Verify default values for optional fields."""
    result = ValidationResult(level_achieved=ValidationLevel.L0_PARSEABLE)

    assert result.level_achieved == ValidationLevel.L0_PARSEABLE
    assert result.diagnostics == []
    assert len(result.levels_passed) == 5
    assert all(v is False for v in result.levels_passed.values())
    assert result.source_filename == "llms.txt"


@pytest.mark.unit
def test_validation_result_total_errors():
    """Exit Criterion 4: total_errors counts ERROR-severity diagnostics."""
    result = ValidationResult(
        level_achieved=ValidationLevel.L0_PARSEABLE,
        diagnostics=[
            _make_diagnostic(DiagnosticCode.E001_NO_H1_TITLE, Severity.ERROR),
            _make_diagnostic(DiagnosticCode.E002_MULTIPLE_H1, Severity.ERROR),
            _make_diagnostic(DiagnosticCode.W001_MISSING_BLOCKQUOTE, Severity.WARNING),
            _make_diagnostic(DiagnosticCode.I001_NO_LLM_INSTRUCTIONS, Severity.INFO),
        ],
    )

    assert result.total_errors == 2


@pytest.mark.unit
def test_validation_result_total_warnings():
    """Exit Criterion 4: total_warnings counts WARNING-severity diagnostics."""
    result = ValidationResult(
        level_achieved=ValidationLevel.L0_PARSEABLE,
        diagnostics=[
            _make_diagnostic(DiagnosticCode.E001_NO_H1_TITLE, Severity.ERROR),
            _make_diagnostic(DiagnosticCode.W001_MISSING_BLOCKQUOTE, Severity.WARNING),
            _make_diagnostic(
                DiagnosticCode.W002_NON_CANONICAL_SECTION_NAME, Severity.WARNING
            ),
            _make_diagnostic(
                DiagnosticCode.W003_LINK_MISSING_DESCRIPTION, Severity.WARNING
            ),
        ],
    )

    assert result.total_warnings == 3


@pytest.mark.unit
def test_validation_result_total_info():
    """Exit Criterion 4: total_info counts INFO-severity diagnostics."""
    result = ValidationResult(
        level_achieved=ValidationLevel.L0_PARSEABLE,
        diagnostics=[
            _make_diagnostic(DiagnosticCode.I001_NO_LLM_INSTRUCTIONS, Severity.INFO),
            _make_diagnostic(DiagnosticCode.I002_NO_CONCEPT_DEFINITIONS, Severity.INFO),
        ],
    )

    assert result.total_info == 2


@pytest.mark.unit
def test_validation_result_is_valid_true():
    """Exit Criterion 4: is_valid is True when L0 passes."""
    result = ValidationResult(
        level_achieved=ValidationLevel.L1_STRUCTURAL,
        levels_passed={
            ValidationLevel.L0_PARSEABLE: True,
            ValidationLevel.L1_STRUCTURAL: True,
            ValidationLevel.L2_CONTENT: False,
            ValidationLevel.L3_BEST_PRACTICES: False,
            ValidationLevel.L4_DOCSTRATUM_EXTENDED: False,
        },
    )

    assert result.is_valid is True


@pytest.mark.unit
def test_validation_result_is_valid_false():
    """Exit Criterion 4: is_valid is False when L0 fails."""
    result = ValidationResult(
        level_achieved=ValidationLevel.L0_PARSEABLE,
        levels_passed={level: False for level in ValidationLevel},
    )

    assert result.is_valid is False


@pytest.mark.unit
def test_validation_result_errors_property():
    """Exit Criterion 4: errors returns only ERROR-severity diagnostics."""
    error = _make_diagnostic(DiagnosticCode.E001_NO_H1_TITLE, Severity.ERROR)
    warning = _make_diagnostic(DiagnosticCode.W001_MISSING_BLOCKQUOTE, Severity.WARNING)

    result = ValidationResult(
        level_achieved=ValidationLevel.L0_PARSEABLE,
        diagnostics=[error, warning],
    )

    assert result.errors == [error]
    assert len(result.errors) == 1


@pytest.mark.unit
def test_validation_result_warnings_property():
    """Exit Criterion 4: warnings returns only WARNING-severity diagnostics."""
    error = _make_diagnostic(DiagnosticCode.E001_NO_H1_TITLE, Severity.ERROR)
    warning = _make_diagnostic(DiagnosticCode.W001_MISSING_BLOCKQUOTE, Severity.WARNING)
    info = _make_diagnostic(DiagnosticCode.I001_NO_LLM_INSTRUCTIONS, Severity.INFO)

    result = ValidationResult(
        level_achieved=ValidationLevel.L0_PARSEABLE,
        diagnostics=[error, warning, info],
    )

    assert result.warnings == [warning]
    assert len(result.warnings) == 1


@pytest.mark.unit
def test_validation_result_empty_diagnostics():
    """Verify computed properties handle empty diagnostics list."""
    result = ValidationResult(level_achieved=ValidationLevel.L4_DOCSTRATUM_EXTENDED)

    assert result.total_errors == 0
    assert result.total_warnings == 0
    assert result.total_info == 0
    assert result.errors == []
    assert result.warnings == []


@pytest.mark.unit
def test_validation_models_importable_from_schema():
    """Exit Criterion 1: All validation models importable from public API."""
    from docstratum import schema

    assert schema.ValidationLevel is ValidationLevel
    assert schema.ValidationDiagnostic is ValidationDiagnostic
    assert schema.ValidationResult is ValidationResult
