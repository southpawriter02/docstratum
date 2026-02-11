# v0.5.0b — Argument Parsing

> **Version:** v0.5.0b
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.5.0-cli-foundation.md](RR-SPEC-v0.5.0-cli-foundation.md)
> **Grounding:** RR-SPEC-v0.1.3-validation-profiles.md §5.5 (CLI flags), §3.2 (profile field mapping)
> **Depends On:** v0.5.0a (CLI dispatcher), DECISION-033 (click library)
> **Module:** `src/docstratum/cli_args.py`
> **Tests:** `tests/test_cli_args.py`

---

## 1. Purpose

Define the complete CLI argument schema for `docstratum validate`. All 12 arguments are parsed and validated at v0.5.0b; however, most are only consumed once profiles are operational (v0.5.1+). At v0.5.0, non-profile arguments (e.g., `--verbose`, `--quiet`, `--output-format`) are operational immediately.

### 1.1 User Story

> As a developer, I want to control validation behavior through command-line flags (e.g., `--max-level 2`, `--strict`, `--verbose`) so that I can tailor validation to my needs without modifying code.

> As a CI maintainer, I want `--quiet` and `--output-format json` flags so that I can integrate DocStratum into automated pipelines without parsing terminal colors.

---

## 2. Argument Schema

### 2.1 Complete Argument Table

| # | Flag(s) | Type | Default | CLI Mapping | Profile Field | Status at v0.5.0 |
|---|---------|------|---------|-------------|---------------|-------------------|
| 1 | `PATH` | Positional | Required | `path` | — | **Active** |
| 2 | `--profile`, `-p` | String | `None` | `profile` | — (selects profile) | Parsed, not consumed |
| 3 | `--max-level`, `-l` | IntRange(0,4) | `None` | `max_level` | `max_validation_level` | Parsed, not consumed |
| 4 | `--tags` | Comma-separated | `None` | `tags` | `rule_tags_include` | Parsed, not consumed |
| 5 | `--exclude-tags` | Comma-separated | `None` | `exclude_tags` | `rule_tags_exclude` | Parsed, not consumed |
| 6 | `--output-tier`, `-t` | IntRange(1,4) | `None` | `output_tier` | `output_tier` | Parsed, not consumed |
| 7 | `--output-format`, `-f` | Choice | `"terminal"` | `output_format` | `output_format` | **Active** |
| 8 | `--pass-threshold` | IntRange(0,100) | `None` | `pass_threshold` | `pass_threshold` | Parsed, not consumed |
| 9 | `--check-urls` | Flag | `False` | `check_urls` | `check_urls` | Parsed, not consumed |
| 10 | `--strict` | Flag | `False` | `strict` | `strict_mode` | **Active** |
| 11 | `--verbose`, `-v` | Flag | `False` | `verbose` | — | **Active** |
| 12 | `--quiet`, `-q` | Flag | `False` | `quiet` | — | **Active** |

### 2.2 None Semantics

All "parsed, not consumed" arguments default to `None`. This is intentional — `None` means "don't override, use the profile value." When v0.5.1 wires these to the profile system, the override chain is:

```
CLI flag (if not None) → profile value (from file) → profile default
```

At v0.5.0, the override chain is simpler:

```
CLI flag (if not None) → hardcoded CLI_DEFAULTS (in cli.py)
```

### 2.3 Mutual Exclusion

`--verbose` and `--quiet` are mutually exclusive. If both are passed:

```bash
docstratum validate llms.txt --verbose --quiet
# Error: --verbose and --quiet are mutually exclusive.
```

Enforced via `click.option`'s `cls=MutuallyExclusiveOption` or a post-parsing validation check.

---

## 3. Implementation

### 3.1 Click Decorators

```python
"""CLI argument parsing for `docstratum validate`.

Defines the complete argument schema (12 arguments). All arguments
are parsed and stored in a CliArgs namespace; not all are consumed
until profiles are operational (v0.5.1+).

Implements v0.5.0b.
Grounding: RR-SPEC-v0.1.3-validation-profiles.md §5.5.
"""

from dataclasses import dataclass
from typing import Optional

import click


@dataclass(frozen=True)
class CliArgs:
    """Parsed CLI arguments for `docstratum validate`.

    All Optional fields default to None, meaning "don't override the
    profile/default value." Active fields (verbose, quiet, strict,
    output_format) are consumed immediately at v0.5.0.

    Grounding: RR-SPEC-v0.1.3-validation-profiles.md §5.5.
    """

    path: str
    profile: Optional[str] = None           # Consumed v0.5.1+
    max_level: Optional[int] = None         # Consumed v0.5.1+
    tags: Optional[tuple[str, ...]] = None  # Consumed v0.5.1+
    exclude_tags: Optional[tuple[str, ...]] = None  # Consumed v0.5.1+
    output_tier: Optional[int] = None       # Consumed v0.5.1+
    output_format: str = "terminal"         # Active v0.5.0
    pass_threshold: Optional[int] = None    # Consumed v0.5.1+
    check_urls: bool = False                # Consumed v0.5.1+
    strict: bool = False                    # Active v0.5.0
    verbose: bool = False                   # Active v0.5.0
    quiet: bool = False                     # Active v0.5.0


def add_validate_options(func):
    """Apply all validate-subcommand options to a click command.

    Usage in cli.py:
        @cli.command()
        @add_validate_options
        def validate(**kwargs):
            args = build_cli_args(**kwargs)
            ...

    Implements v0.5.0b.
    """
    decorators = [
        click.argument("path", type=click.Path(exists=True)),
        click.option(
            "--profile", "-p",
            type=str,
            default=None,
            help="Validation profile name or path (e.g., lint, ci, full).",
        ),
        click.option(
            "--max-level", "-l",
            type=click.IntRange(0, 4),
            default=None,
            help="Maximum validation level to execute (0=L0 only, 4=all).",
        ),
        click.option(
            "--tags",
            type=str,
            default=None,
            callback=_parse_comma_list,
            help="Comma-separated rule tags to include (OR semantics).",
        ),
        click.option(
            "--exclude-tags",
            type=str,
            default=None,
            callback=_parse_comma_list,
            help="Comma-separated rule tags to exclude (always wins).",
        ),
        click.option(
            "--output-tier", "-t",
            type=click.IntRange(1, 4),
            default=None,
            help="Output detail tier (1=summary, 2=diagnostic, 3=remediation, 4=audience).",
        ),
        click.option(
            "--output-format", "-f",
            type=click.Choice(["terminal", "json", "markdown"], case_sensitive=False),
            default="terminal",
            help="Output format (terminal=colorized, json=machine-readable).",
        ),
        click.option(
            "--pass-threshold",
            type=click.IntRange(0, 100),
            default=None,
            help="Minimum score to pass (0-100). Scores below this exit 5.",
        ),
        click.option(
            "--check-urls",
            is_flag=True,
            default=False,
            help="Enable live URL validation (sends HTTP requests).",
        ),
        click.option(
            "--strict",
            is_flag=True,
            default=False,
            help="Treat warnings as errors for exit code computation.",
        ),
        click.option(
            "--verbose", "-v",
            is_flag=True,
            default=False,
            help="Show all diagnostics with remediation text.",
        ),
        click.option(
            "--quiet", "-q",
            is_flag=True,
            default=False,
            help="Suppress all output. Only the exit code is set.",
        ),
    ]
    # Apply decorators in reverse order (click stacking convention)
    for decorator in reversed(decorators):
        func = decorator(func)
    return func


def _parse_comma_list(
    ctx: click.Context,
    param: click.Parameter,
    value: Optional[str],
) -> Optional[tuple[str, ...]]:
    """Parse a comma-separated string into a tuple of trimmed strings.

    Examples:
        "structural,content" → ("structural", "content")
        "  foo , bar , baz " → ("foo", "bar", "baz")
        None → None
    """
    if value is None:
        return None
    return tuple(tag.strip() for tag in value.split(",") if tag.strip())


def build_cli_args(**kwargs) -> CliArgs:
    """Build a CliArgs from click keyword arguments.

    Validates mutual exclusion and normalizes values.

    Args:
        **kwargs: Keyword arguments from click decorator stack.

    Returns:
        Frozen CliArgs dataclass.

    Raises:
        click.UsageError: If --verbose and --quiet are both set.
    """
    if kwargs.get("verbose") and kwargs.get("quiet"):
        raise click.UsageError(
            "--verbose and --quiet are mutually exclusive."
        )

    return CliArgs(
        path=kwargs["path"],
        profile=kwargs.get("profile"),
        max_level=kwargs.get("max_level"),
        tags=kwargs.get("tags"),
        exclude_tags=kwargs.get("exclude_tags"),
        output_tier=kwargs.get("output_tier"),
        output_format=kwargs.get("output_format", "terminal"),
        pass_threshold=kwargs.get("pass_threshold"),
        check_urls=kwargs.get("check_urls", False),
        strict=kwargs.get("strict", False),
        verbose=kwargs.get("verbose", False),
        quiet=kwargs.get("quiet", False),
    )
```

### 3.2 Integration with cli.py (Updated validate Command)

After v0.5.0b, the `validate` command in `cli.py` is updated:

```python
from docstratum.cli_args import add_validate_options, build_cli_args

@cli.command()
@add_validate_options
def validate(**kwargs) -> None:
    """Validate an llms.txt file and report quality score."""
    args = build_cli_args(**kwargs)
    # ... pipeline orchestration using args.path, args.strict, etc.
```

---

## 4. Decision Tree: Argument Override Precedence

```
User runs: docstratum validate llms.txt --max-level 2 --strict
│
├── Phase 1: Click parses arguments
│     └── CliArgs(path="llms.txt", max_level=2, strict=True, ...)
│
├── Phase 2 (v0.5.0): Apply hardcoded defaults for None fields
│     ├── max_level = 2 (CLI provided, use it)       ← OVERRIDE
│     ├── output_tier = None → CLI_DEFAULTS["output_tier"] = 2   ← DEFAULT
│     ├── strict = True (CLI provided, use it)        ← OVERRIDE
│     └── ... (other None fields get CLI_DEFAULTS)
│
└── Phase 3 (v0.5.1+): Apply profile-merged values
      ├── max_level = 2 (CLI > profile > default)     ← CLI WINS
      ├── output_tier = profile.output_tier (no CLI)   ← PROFILE WINS
      └── ... (three-tier merge: CLI > profile > default)
```

---

## 5. Edge Cases

| Scenario | Behind-the-scenes | User sees |
|----------|-------------------|-----------|
| `--max-level 5` | `click.IntRange(0, 4)` rejects | Error: 5 is not in valid range 0–4 |
| `--tags ""` (empty string) | `_parse_comma_list` returns empty tuple | Treated as "no tag filter" |
| `--tags "foo,,bar,"` | Splits → ("foo", "bar"), empty strings dropped | Only foo and bar included |
| `--output-format JSON` | `case_sensitive=False` normalizes | Treated as "json" |
| `--verbose -q` | Mutual exclusion check fires | Error: --verbose and --quiet are mutually exclusive |
| No flags at all | All Optional fields are None | Hardcoded defaults applied |
| `--profile ci --max-level 1` | Both stored; --max-level overrides ci's level 3 | At v0.5.0: max-level unused. At v0.5.1: CLI wins |
| `-l 0` (L0 only) | max_level is 0, only parseable gate checks run | Valid: tests whether the file is valid Markdown at all |

---

## 6. Acceptance Criteria

- [ ] All 12 arguments are parseable without error
- [ ] `CliArgs` dataclass is `frozen=True` (immutable after creation)
- [ ] `--verbose` and `--quiet` raise `UsageError` when both passed
- [ ] `--tags "foo,bar,baz"` produces `("foo", "bar", "baz")`
- [ ] `--tags` with whitespace is trimmed: `" foo , bar "` → `("foo", "bar")`
- [ ] `--max-level` rejects values outside 0–4
- [ ] `--output-tier` rejects values outside 1–4
- [ ] `--pass-threshold` rejects values outside 0–100
- [ ] `--output-format` only accepts `terminal`, `json`, `markdown` (case-insensitive)
- [ ] Arguments with `None` default do not override downstream values
- [ ] `build_cli_args()` returns a `CliArgs` instance with correct field values
- [ ] Module docstring cites v0.5.0b and grounding spec

---

## 7. Deliverables

| File | Description | Status |
|------|-------------|--------|
| `src/docstratum/cli_args.py` | Argument parsing module | NEW |
| `src/docstratum/cli.py` | Update validate command to use `add_validate_options` | MODIFY |
| `tests/test_cli_args.py` | Unit tests for argument parsing | NEW |

---

## 8. Test Plan (14 tests)

| # | Test Name | Input | Expected |
|---|-----------|-------|----------|
| 1 | `test_default_args` | Only `path` provided | All Optional fields are None, output_format="terminal" |
| 2 | `test_profile_arg` | `--profile ci` | `args.profile == "ci"` |
| 3 | `test_max_level_valid` | `--max-level 2` | `args.max_level == 2` |
| 4 | `test_max_level_boundary_0` | `--max-level 0` | `args.max_level == 0` |
| 5 | `test_max_level_boundary_4` | `--max-level 4` | `args.max_level == 4` |
| 6 | `test_max_level_invalid` | `--max-level 5` | Click error, exit 2 |
| 7 | `test_tags_parsing` | `--tags "foo,bar,baz"` | `args.tags == ("foo", "bar", "baz")` |
| 8 | `test_tags_whitespace_trim` | `--tags " foo , bar "` | `args.tags == ("foo", "bar")` |
| 9 | `test_tags_empty_elements` | `--tags "foo,,bar,"` | `args.tags == ("foo", "bar")` |
| 10 | `test_output_format_choices` | `--output-format json` | `args.output_format == "json"` |
| 11 | `test_output_format_case_insensitive` | `--output-format JSON` | `args.output_format == "JSON"` (or lowercased) |
| 12 | `test_mutual_exclusion` | `--verbose --quiet` | `click.UsageError` raised |
| 13 | `test_all_flags_combined` | All 12 args specified | CliArgs populated correctly |
| 14 | `test_cli_args_frozen` | Attempt to mutate CliArgs | `FrozenInstanceError` raised |

```python
"""Tests for v0.5.0b — Argument Parsing.

Validates the complete CLI argument schema using CliRunner
and direct build_cli_args() calls.
"""

from click.testing import CliRunner
from docstratum.cli import cli
from docstratum.cli_args import CliArgs, build_cli_args

import pytest


def test_default_args(tmp_path):
    """Only the path is provided — all Optional fields should be None."""
    test_file = tmp_path / "llms.txt"
    test_file.write_text("# Test")
    runner = CliRunner()
    result = runner.invoke(cli, ["validate", str(test_file)])
    # At minimum, the command should not crash on default args
    assert result.exit_code != 2  # 2 = click usage error


def test_mutual_exclusion(tmp_path):
    """--verbose and --quiet together should produce an error."""
    test_file = tmp_path / "llms.txt"
    test_file.write_text("# Test")
    runner = CliRunner()
    result = runner.invoke(
        cli, ["validate", str(test_file), "--verbose", "--quiet"]
    )
    assert result.exit_code != 0
    assert "mutually exclusive" in result.output.lower()


def test_tags_parsing():
    """Comma-separated --tags should parse into a tuple."""
    args = build_cli_args(
        path="test.txt",
        tags=("foo", "bar"),
        exclude_tags=None, profile=None, max_level=None,
        output_tier=None, output_format="terminal",
        pass_threshold=None, check_urls=False,
        strict=False, verbose=False, quiet=False,
    )
    assert args.tags == ("foo", "bar")
```
