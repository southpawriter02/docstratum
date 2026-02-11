# v0.5.0d — Terminal Output

> **Version:** v0.5.0d
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.5.0-cli-foundation.md](RR-SPEC-v0.5.0-cli-foundation.md)
> **Grounding:** RR-SPEC-v0.1.3-output-tier-specification.md §3 (Tier 2 diagnostic report), RR-SCOPE-v0.5.x §4.4
> **Depends On:** v0.5.0b (`CliArgs.verbose`, `CliArgs.quiet`, `CliArgs.output_format`), v0.5.0c (`ExitCode`), v0.3.x (`ValidationResult`), v0.4.x (`QualityScore`)
> **Module:** `src/docstratum/cli_output.py`
> **Tests:** `tests/test_cli_output.py`

---

## 1. Purpose

Render a colorized, human-readable terminal summary of validation results. This is what the user **sees** after running `docstratum validate llms.txt`. The output must be informative, scannable, and opinionated about visual hierarchy.

### 1.1 User Story

> As a developer, I want to see a quick summary (score, grade, pass/fail) followed by actionable diagnostics, so that I can fix issues without scrolling through raw data.

> As a CI pipeline, I want `--output-format json` to emit structured JSON on stdout, so that I can parse the results programmatically.

> As a user on a terminal that doesn't support ANSI colors, I want `NO_COLOR=1` to suppress color codes, so that my terminal doesn't show garbage characters.

---

## 2. Output Layout

### 2.1 Terminal Mode (Default)

```
╭──────────────────────────────────────────────╮
│  DocStratum Validation Report                │
│  File: llms.txt                              │
╰──────────────────────────────────────────────╯

Score: 72.5 / 100   Grade: B   ✓ PASS

Levels:
  ✓ L0  Parseable
  ✓ L1  Structural
  ✗ L2  Content Quality       (3 errors)
  ✗ L3  Best Practices        (1 error, 2 warnings)

Dimensions:
  Structural    28.5 / 30   ▓▓▓▓▓▓▓▓▓░  95%
  Content       22.0 / 40   ▓▓▓▓▓░░░░░  55%
  Anti-Pattern  22.0 / 30   ▓▓▓▓▓▓▓░░░  73%

Diagnostics (4 errors, 2 warnings):
  ERROR  L2  E010  Empty description section        [line 15]
  ERROR  L2  E011  Description below minimum length  [line 15]
  ERROR  L2  E006  Broken external URL               [line 42]
  ERROR  L3  AP-CRIT-002  Duplicate entries detected [line 30]
  WARN   L3  W008  Non-canonical section order
  WARN   L3  W010  Missing code examples section

Use --verbose for remediation details.
```

### 2.2 Verbose Mode (`--verbose`)

Adds remediation text after each diagnostic:

```
Diagnostics (4 errors, 2 warnings):
  ERROR  L2  E010  Empty description section        [line 15]
    → Add a meaningful description paragraph after the blockquote.
      The description should be 50-300 words summarizing the project.

  ERROR  L2  E011  Description below minimum length  [line 15]
    → Expand the description to at least 50 words.
    ...
```

### 2.3 Quiet Mode (`--quiet`)

No output at all. Only the exit code is set. Useful for CI gates:

```bash
docstratum validate llms.txt --quiet && echo "PASS" || echo "FAIL"
```

### 2.4 JSON Mode (`--output-format json`)

```json
{
  "file": "llms.txt",
  "score": 72.5,
  "max_score": 100.0,
  "grade": "B",
  "passed": true,
  "exit_code": 2,
  "exit_code_name": "CONTENT_ERRORS",
  "levels": {
    "L0": {"passed": true, "errors": 0, "warnings": 0},
    "L1": {"passed": true, "errors": 0, "warnings": 0},
    "L2": {"passed": false, "errors": 3, "warnings": 0},
    "L3": {"passed": false, "errors": 1, "warnings": 2}
  },
  "dimensions": {
    "structural": {"points": 28.5, "max_points": 30.0},
    "content": {"points": 22.0, "max_points": 40.0},
    "anti_pattern": {"points": 22.0, "max_points": 30.0}
  },
  "diagnostics": [
    {
      "code": "E010",
      "severity": "ERROR",
      "level": "L2",
      "message": "Empty description section",
      "line_number": 15,
      "remediation": "Add a meaningful description paragraph...",
      "context": null
    }
  ],
  "engine_version": "0.1.0",
  "timestamp": "2026-02-10T17:30:00Z"
}
```

---

## 3. Color Scheme

### 3.1 ANSI Color Mapping

| Element | Color | ANSI Code | Condition |
|---------|-------|-----------|-----------|
| Grade A/A+ | Bright Green | `\033[92m` | — |
| Grade B | Green | `\033[32m` | — |
| Grade C | Yellow | `\033[33m` | — |
| Grade D | Red | `\033[31m` | — |
| Grade F | Bright Red | `\033[91m` | — |
| PASS | Bright Green | `\033[92m` | exit_code == 0 |
| FAIL | Bright Red | `\033[91m` | exit_code != 0 |
| ERROR | Red | `\033[31m` | — |
| WARNING | Yellow | `\033[33m` | — |
| INFO | Cyan | `\033[36m` | — |
| Level ✓ | Green | `\033[32m` | Level passed |
| Level ✗ | Red | `\033[31m` | Level failed |
| Score bar ▓ | Green/Yellow/Red | — | Based on percentage |
| Remediation arrow | Dim | `\033[2m` | Verbose mode only |
| Box border | Dim | `\033[2m` | Header box |

### 3.2 `NO_COLOR` Environment Variable

If the `NO_COLOR` environment variable is set (any value), all ANSI escape codes are suppressed. This follows the [no-color.org](https://no-color.org) convention.

```python
import os

NO_COLOR = bool(os.environ.get("NO_COLOR"))
```

Additionally, if stdout is not a TTY (e.g., piped to a file), colors are suppressed automatically:

```python
import sys

if not sys.stdout.isatty():
    NO_COLOR = True
```

---

## 4. Implementation

```python
"""Terminal output renderer for the DocStratum CLI.

Renders validation results as colorized terminal output, JSON,
or markdown (future).

Implements v0.5.0d.
Grounding: RR-SPEC-v0.1.3-output-tier-specification.md §3.
"""

import json
import os
import sys
from datetime import datetime, timezone
from typing import Optional

from docstratum import __version__
from docstratum.cli_exit_codes import ExitCode
from docstratum.schema.diagnostics import Severity
from docstratum.schema.quality import QualityScore
from docstratum.schema.validation import ValidationDiagnostic, ValidationResult


# --- Color Utilities ---


def _use_color() -> bool:
    """Determine whether ANSI color output is appropriate.

    Respects NO_COLOR env var and non-TTY stdout.
    See: https://no-color.org
    """
    if os.environ.get("NO_COLOR"):
        return False
    return sys.stdout.isatty()


class _Color:
    """ANSI color codes, disabled when color is not appropriate."""

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled

    def _code(self, code: str) -> str:
        return code if self.enabled else ""

    @property
    def reset(self) -> str:
        return self._code("\033[0m")

    @property
    def bold(self) -> str:
        return self._code("\033[1m")

    @property
    def dim(self) -> str:
        return self._code("\033[2m")

    @property
    def red(self) -> str:
        return self._code("\033[31m")

    @property
    def green(self) -> str:
        return self._code("\033[32m")

    @property
    def yellow(self) -> str:
        return self._code("\033[33m")

    @property
    def cyan(self) -> str:
        return self._code("\033[36m")

    @property
    def bright_red(self) -> str:
        return self._code("\033[91m")

    @property
    def bright_green(self) -> str:
        return self._code("\033[92m")


# --- Render Functions ---


def render_terminal_output(
    file_path: str,
    result: ValidationResult,
    score: Optional[QualityScore],
    exit_code: ExitCode,
    *,
    verbose: bool = False,
    quiet: bool = False,
    output_format: str = "terminal",
) -> None:
    """Render pipeline results to stdout.

    Dispatches to the appropriate renderer based on output_format.

    Args:
        file_path: Path to the validated file.
        result: Validation pipeline result.
        score: Quality score (None if scoring skipped).
        exit_code: Computed exit code.
        verbose: Show remediation text for each diagnostic.
        quiet: Suppress all output.
        output_format: One of "terminal", "json", "markdown".

    Implements v0.5.0d.
    """
    if quiet:
        return

    if output_format == "json":
        _render_json(file_path, result, score, exit_code)
    elif output_format == "markdown":
        # Reserved for v0.8.x
        _render_terminal(file_path, result, score, exit_code, verbose)
    else:
        _render_terminal(file_path, result, score, exit_code, verbose)


def _render_terminal(
    file_path: str,
    result: ValidationResult,
    score: Optional[QualityScore],
    exit_code: ExitCode,
    verbose: bool,
) -> None:
    """Render the colorized terminal layout.

    Layout order:
    1. Header box with file name
    2. Score/grade/pass-fail line
    3. Level checklist
    4. Dimension breakdown bars
    5. Diagnostic listing (sorted by severity, then level)
    6. Footer hint (--verbose)
    """
    c = _Color(enabled=_use_color())

    # 1. Header box
    print(f"{c.dim}╭{'─' * 46}╮{c.reset}")
    print(f"{c.dim}│{c.reset}  {c.bold}DocStratum Validation Report{c.reset}{'':>17}{c.dim}│{c.reset}")
    print(f"{c.dim}│{c.reset}  File: {file_path:<39}{c.dim}│{c.reset}")
    print(f"{c.dim}╰{'─' * 46}╯{c.reset}")
    print()

    # 2. Score line
    if score:
        grade_color = _grade_color(c, score.grade)
        pass_fail = (
            f"{c.bright_green}✓ PASS{c.reset}"
            if exit_code == ExitCode.PASS
            else f"{c.bright_red}✗ FAIL{c.reset}"
        )
        print(
            f"Score: {c.bold}{score.total_score:.1f}{c.reset} / 100   "
            f"Grade: {grade_color}{c.bold}{score.grade}{c.reset}   "
            f"{pass_fail}"
        )
    else:
        print(f"Score: {c.dim}(scoring skipped){c.reset}")
    print()

    # 3. Level checklist
    _render_level_checklist(c, result)
    print()

    # 4. Dimension breakdown
    if score and score.dimensions:
        _render_dimension_bars(c, score)
        print()

    # 5. Diagnostics
    _render_diagnostics(c, result, verbose)


def _grade_color(c: _Color, grade: str) -> str:
    """Return the ANSI color code for a quality grade."""
    grade_colors = {
        "A+": c.bright_green,
        "A": c.bright_green,
        "B": c.green,
        "C": c.yellow,
        "D": c.red,
        "F": c.bright_red,
    }
    return grade_colors.get(grade, c.reset)


def _render_level_checklist(c: _Color, result: ValidationResult) -> None:
    """Render the L0–L3 level pass/fail checklist."""
    print("Levels:")
    level_names = {
        "L0_PARSEABLE": "L0  Parseable",
        "L1_STRUCTURAL": "L1  Structural",
        "L2_CONTENT": "L2  Content Quality",
        "L3_BEST_PRACTICES": "L3  Best Practices",
    }
    for level_key, label in level_names.items():
        errors = sum(
            1 for d in result.diagnostics
            if d.level.name == level_key and d.severity == Severity.ERROR
        )
        warnings = sum(
            1 for d in result.diagnostics
            if d.level.name == level_key and d.severity == Severity.WARNING
        )
        if errors > 0:
            summary = f"({errors} error{'s' if errors > 1 else ''})"
            if warnings > 0:
                summary = f"({errors} error{'s' if errors > 1 else ''}, {warnings} warning{'s' if warnings > 1 else ''})"
            print(f"  {c.red}✗{c.reset} {label:<25} {summary}")
        elif warnings > 0:
            summary = f"({warnings} warning{'s' if warnings > 1 else ''})"
            print(f"  {c.yellow}~{c.reset} {label:<25} {summary}")
        else:
            print(f"  {c.green}✓{c.reset} {label}")


def _render_dimension_bars(c: _Color, score: QualityScore) -> None:
    """Render dimension score progress bars."""
    print("Dimensions:")
    for dim in score.dimensions:
        pct = (dim.points / dim.max_points * 100) if dim.max_points > 0 else 0
        bar_filled = int(pct / 10)
        bar_empty = 10 - bar_filled
        bar_color = c.green if pct >= 70 else (c.yellow if pct >= 40 else c.red)
        bar = f"{bar_color}{'▓' * bar_filled}{'░' * bar_empty}{c.reset}"
        name = dim.dimension.name.replace("_", " ").title()
        print(f"  {name:<15} {dim.points:>5.1f} / {dim.max_points:<5.1f} {bar}  {pct:.0f}%")


def _render_diagnostics(
    c: _Color,
    result: ValidationResult,
    verbose: bool,
) -> None:
    """Render the sorted diagnostic listing."""
    if not result.diagnostics:
        print(f"{c.green}No diagnostics — clean file!{c.reset}")
        return

    errors = sum(1 for d in result.diagnostics if d.severity == Severity.ERROR)
    warnings = sum(1 for d in result.diagnostics if d.severity == Severity.WARNING)
    header_parts = []
    if errors:
        header_parts.append(f"{errors} error{'s' if errors > 1 else ''}")
    if warnings:
        header_parts.append(f"{warnings} warning{'s' if warnings > 1 else ''}")
    print(f"Diagnostics ({', '.join(header_parts)}):")

    # Sort: ERROR before WARNING before INFO, then by level, then by line_number
    sorted_diags = sorted(
        result.diagnostics,
        key=lambda d: (
            _severity_sort_key(d.severity),
            _level_sort_key(d.level),
            d.line_number or 0,
        ),
    )

    for diag in sorted_diags:
        severity_color = {
            Severity.ERROR: c.red,
            Severity.WARNING: c.yellow,
        }.get(diag.severity, c.cyan)

        severity_label = diag.severity.name[:5].ljust(5)
        level_label = diag.level.name.split("_")[0]  # "L0", "L1", etc.
        code_str = str(diag.code.name) if hasattr(diag.code, 'name') else str(diag.code)
        line_str = f"  [line {diag.line_number}]" if diag.line_number else ""

        print(
            f"  {severity_color}{severity_label}{c.reset}  "
            f"{level_label}  {code_str}  {diag.message}{line_str}"
        )

        if verbose and diag.remediation:
            print(f"    {c.dim}→ {diag.remediation}{c.reset}")
            print()

    if not verbose and (errors + warnings) > 0:
        print(f"\n{c.dim}Use --verbose for remediation details.{c.reset}")


def _severity_sort_key(severity: Severity) -> int:
    """Sort key: ERROR=0, WARNING=1, INFO=2."""
    return {Severity.ERROR: 0, Severity.WARNING: 1}.get(severity, 2)


def _level_sort_key(level) -> int:
    """Sort key by validation level ordinal."""
    return getattr(level, "value", 0) if hasattr(level, "value") else 0


# --- JSON Renderer ---


def _render_json(
    file_path: str,
    result: ValidationResult,
    score: Optional[QualityScore],
    exit_code: ExitCode,
) -> None:
    """Render pipeline results as JSON to stdout.

    Output is a single JSON object with all results flattened
    for easy machine consumption.

    Implements v0.5.0d (JSON mode).
    """
    output = {
        "file": file_path,
        "score": score.total_score if score else None,
        "max_score": 100.0,
        "grade": score.grade if score else None,
        "passed": exit_code == ExitCode.PASS,
        "exit_code": int(exit_code),
        "exit_code_name": exit_code.name,
        "levels": _build_level_summary(result),
        "dimensions": _build_dimension_summary(score) if score else {},
        "diagnostics": [
            {
                "code": str(d.code.name) if hasattr(d.code, 'name') else str(d.code),
                "severity": d.severity.name,
                "level": d.level.name.split("_")[0],
                "message": d.message,
                "line_number": d.line_number,
                "remediation": d.remediation,
                "context": d.context if hasattr(d, 'context') else None,
            }
            for d in result.diagnostics
        ],
        "engine_version": __version__,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    print(json.dumps(output, indent=2))


def _build_level_summary(result: ValidationResult) -> dict:
    """Build per-level error/warning counts."""
    level_names = ["L0_PARSEABLE", "L1_STRUCTURAL", "L2_CONTENT", "L3_BEST_PRACTICES"]
    summary = {}
    for level_key in level_names:
        errors = sum(
            1 for d in result.diagnostics
            if d.level.name == level_key and d.severity == Severity.ERROR
        )
        warnings = sum(
            1 for d in result.diagnostics
            if d.level.name == level_key and d.severity == Severity.WARNING
        )
        short_name = level_key.split("_")[0]
        summary[short_name] = {
            "passed": errors == 0,
            "errors": errors,
            "warnings": warnings,
        }
    return summary


def _build_dimension_summary(score: QualityScore) -> dict:
    """Build per-dimension point summary."""
    return {
        dim.dimension.name.lower(): {
            "points": dim.points,
            "max_points": dim.max_points,
        }
        for dim in score.dimensions
    }
```

---

## 5. Decision: Diagnostic Sort Order

Diagnostics are sorted by:
1. **Severity** — ERROR first, then WARNING, then INFO
2. **Level** — L0 first, then L1, L2, L3 (most fundamental issues first)
3. **Line number** — ascending (top of file first)

**Rationale:** Developers should see the most critical issues at the top. Within the same severity, lower-level issues (e.g., "file is not UTF-8") precede higher-level issues (e.g., "description is too short") because structural integrity must be fixed before content quality matters.

---

## 6. Decision: Progress Bar Character Set

```
▓░   (Standard Unicode block elements)
```

**Rationale:** These characters render correctly in all modern terminals (macOS Terminal, iTerm2, Windows Terminal, most Linux terminals). They provide clear visual contrast between filled and empty portions. Fallback to `#.` characters is available via the `_Color` class when Unicode is not supported (detected via locale).

---

## 7. Edge Cases

| Scenario | Behavior | Rationale |
|----------|----------|-----------|
| Score is None (scoring skipped) | Display "(scoring skipped)" instead of score line | Pipeline may halt before scoring |
| No diagnostics | Print "No diagnostics — clean file!" in green | Positive reinforcement |
| File path > 39 chars | Path truncated with `...` prefix in header box | Keep box width fixed |
| 100+ diagnostics | All shown (no limit at v0.5.0) | Developers need full picture; paging deferred |
| `--output-format markdown` | Falls back to terminal renderer | Markdown renderer deferred to v0.8.x |
| Redirect to file (`> report.txt`) | Colors auto-suppressed (not a TTY) | Prevents ANSI garbage in files |
| `NO_COLOR=1` | Colors suppressed | no-color.org convention |
| Grade is empty string | No color applied, grade displayed as-is | Defensive rendering |
| Dimension with 0 max_points | Shows 0.0 / 0.0 with empty bar | Avoid division by zero |

---

## 8. Acceptance Criteria

- [ ] Terminal mode renders header box, score line, level checklist, dimension bars, and diagnostic listing
- [ ] `--verbose` shows remediation text beneath each diagnostic
- [ ] `--quiet` produces no output (empty stdout)
- [ ] `--output-format json` emits valid JSON to stdout
- [ ] JSON output includes all fields: file, score, grade, passed, exit_code, levels, dimensions, diagnostics, engine_version, timestamp
- [ ] Colors are suppressed when `NO_COLOR` is set
- [ ] Colors are suppressed when stdout is not a TTY
- [ ] Diagnostics are sorted by severity → level → line_number
- [ ] Grade is colorized according to the color table
- [ ] PASS/FAIL indicator matches exit code
- [ ] Dimension bars render correctly for 0%, 50%, 100%
- [ ] "No diagnostics" message shown for clean files
- [ ] Module docstring cites v0.5.0d and grounding spec

---

## 9. Deliverables

| File | Description | Status |
|------|-------------|--------|
| `src/docstratum/cli_output.py` | Terminal and JSON renderers | NEW |
| `tests/test_cli_output.py` | Unit and snapshot tests | NEW |

---

## 10. Test Plan (16 tests)

| # | Test Name | Input | Expected |
|---|-----------|-------|----------|
| 1 | `test_quiet_mode_empty` | quiet=True | stdout is empty |
| 2 | `test_terminal_header_box` | Any result | Output contains "DocStratum Validation Report" |
| 3 | `test_score_display` | score=72.5 | Output contains "72.5 / 100" |
| 4 | `test_grade_display` | grade="B" | Output contains "B" |
| 5 | `test_pass_indicator` | exit_code=PASS | Output contains "✓ PASS" |
| 6 | `test_fail_indicator` | exit_code=CONTENT_ERRORS | Output contains "✗ FAIL" |
| 7 | `test_level_checklist_all_pass` | No diagnostics | All levels show ✓ |
| 8 | `test_level_checklist_l2_fail` | L2 error | L0 ✓, L1 ✓, L2 ✗ |
| 9 | `test_dimension_bars` | 3 dimensions | Three bar lines rendered |
| 10 | `test_diagnostics_sorted` | E+W at various levels | ERROR before WARNING, L0 before L3 |
| 11 | `test_verbose_shows_remediation` | verbose=True | Remediation text with → arrow |
| 12 | `test_no_verbose_shows_hint` | verbose=False, has diagnostics | "Use --verbose" hint displayed |
| 13 | `test_no_diagnostics_clean` | Empty diagnostics | "No diagnostics — clean file!" |
| 14 | `test_json_output_valid` | output_format="json" | `json.loads()` succeeds |
| 15 | `test_json_output_fields` | output_format="json" | All required fields present |
| 16 | `test_no_color_env` | NO_COLOR=1 | No ANSI escape codes in output |

```python
"""Tests for v0.5.0d — Terminal Output.

Tests rendering logic using captured stdout. Uses monkeypatch
for NO_COLOR and TTY detection.

Implements v0.5.0d test plan.
"""

import json
import os
from io import StringIO
from unittest.mock import patch

import pytest

from docstratum.cli_exit_codes import ExitCode
from docstratum.cli_output import render_terminal_output


def _make_result(diagnostics=None):
    """Create minimal ValidationResult."""
    from docstratum.schema.validation import ValidationResult, ValidationLevel
    from docstratum.schema.diagnostics import Severity
    return ValidationResult(
        diagnostics=diagnostics or [],
        level_achieved=ValidationLevel.L3_BEST_PRACTICES,
        levels_passed=[],
        total_errors=sum(1 for d in (diagnostics or []) if d.severity == Severity.ERROR),
        total_warnings=sum(1 for d in (diagnostics or []) if d.severity == Severity.WARNING),
    )


def _make_score(total=72.5, grade="B"):
    """Create minimal QualityScore."""
    from docstratum.schema.quality import QualityScore
    return QualityScore(total_score=total, grade=grade, dimensions=[])


def test_quiet_mode_empty(capsys):
    """--quiet should produce no output."""
    result = _make_result()
    score = _make_score()
    render_terminal_output("test.txt", result, score, ExitCode.PASS, quiet=True)
    captured = capsys.readouterr()
    assert captured.out == ""


def test_json_output_valid(capsys):
    """JSON mode should produce valid JSON."""
    result = _make_result()
    score = _make_score()
    render_terminal_output(
        "test.txt", result, score, ExitCode.PASS, output_format="json"
    )
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["file"] == "test.txt"
    assert data["score"] == 72.5
    assert data["grade"] == "B"
    assert data["passed"] is True


def test_no_color_env(capsys, monkeypatch):
    """NO_COLOR env should suppress ANSI codes."""
    monkeypatch.setenv("NO_COLOR", "1")
    result = _make_result()
    score = _make_score()
    render_terminal_output("test.txt", result, score, ExitCode.PASS)
    captured = capsys.readouterr()
    assert "\033[" not in captured.out
```

---

## 11. Dependencies

| Dependency | Source | Used For |
|------------|--------|----------|
| `json` | stdlib | JSON serialization |
| `datetime` | stdlib | Timestamp in JSON output |
| `os` | stdlib | `NO_COLOR` env var |
| `sys` | stdlib | TTY detection |
| `docstratum.__version__` | Internal | Engine version in JSON |
| `ExitCode` | v0.5.0c | Pass/fail determination |
| `ValidationResult` | v0.3.x | Diagnostic data |
| `QualityScore` | v0.4.x | Score/grade data |
| `Severity` | v0.1.2a | Severity classification |

No external dependencies — this module uses only stdlib and internal schema models.

---

## 12. Limitations

| Limitation | Impact | Resolution |
|------------|--------|------------|
| No pagination for large diagnostic lists | Terminal may scroll extensively | Future: limit to top 20 with `--verbose` for full list |
| No markdown output format | `--output-format markdown` falls back to terminal | v0.8.x report generation |
| No audience-adapted output (Tier 4) | Output not tailored to persona | v0.8.x+ |
| Header box width fixed at 48 chars | Long filenames truncated | Could be dynamic in future |
| No interactive mode | No drill-down into individual diagnostics | Not planned for CLI |
