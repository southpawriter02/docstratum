"""Tests for the diagnostic infrastructure (diagnostics.py)."""

import pytest

from docstratum.schema.diagnostics import DiagnosticCode, Severity


@pytest.mark.unit
def test_diagnostic_code_counts():
    """Verify exact count of diagnostic codes by type (10E/18W/10I)."""
    errors = [c for c in DiagnosticCode if c.severity == Severity.ERROR]
    warnings = [c for c in DiagnosticCode if c.severity == Severity.WARNING]
    infos = [c for c in DiagnosticCode if c.severity == Severity.INFO]

    assert len(errors) == 10, f"Expected 10 errors, found {len(errors)}"
    assert len(warnings) == 18, f"Expected 18 warnings, found {len(warnings)}"
    assert len(infos) == 10, f"Expected 10 infos, found {len(infos)}"
    assert (
        len(DiagnosticCode) == 38
    ), f"Expected 38 total codes, found {len(DiagnosticCode)}"


@pytest.mark.unit
@pytest.mark.parametrize(
    "code,expected_severity",
    [
        (DiagnosticCode.E001_NO_H1_TITLE, Severity.ERROR),
        (DiagnosticCode.W001_MISSING_BLOCKQUOTE, Severity.WARNING),
        (DiagnosticCode.I001_NO_LLM_INSTRUCTIONS, Severity.INFO),
    ],
)
def test_severity_property(code, expected_severity):
    """Verify severity property logic across all types."""
    assert code.severity == expected_severity


@pytest.mark.unit
@pytest.mark.parametrize(
    "code,expected_number",
    [
        (DiagnosticCode.E001_NO_H1_TITLE, 1),
        (DiagnosticCode.E008_EXCEEDS_SIZE_LIMIT, 8),
        (DiagnosticCode.W011_EMPTY_SECTIONS, 11),
        (DiagnosticCode.I007_JARGON_WITHOUT_DEFINITION, 7),
    ],
)
def test_code_number_property(code, expected_number):
    """Verify numeric extraction from code values."""
    assert code.code_number == expected_number


@pytest.mark.unit
def test_message_content():
    """Verify all codes have valid, non-empty messages from docstrings."""
    for code in DiagnosticCode:
        msg = code.message
        assert msg, f"Code {code.name} has empty message"
        assert "\n" not in msg, f"Code {code.name} message contains newlines: {msg!r}"
        assert not msg.startswith(
            "Diagnostic "
        ), f"Code {code.name} missing docstring (got fallback)"


@pytest.mark.unit
def test_remediation_content():
    """Verify all codes have remediation hints."""
    for code in DiagnosticCode:
        rem = code.remediation
        assert rem, f"Code {code.name} has empty remediation"
        assert (
            rem != "No remediation available."
        ), f"Code {code.name} missing Remediation: line in docstring"


@pytest.mark.unit
def test_value_format():
    """Verify all enum values follow the letter + 3 digits format."""
    import re

    pattern = re.compile(r"^[EWI]\d{3}$")
    for code in DiagnosticCode:
        assert pattern.match(code.value), f"Invalid code format: {code.value}"
