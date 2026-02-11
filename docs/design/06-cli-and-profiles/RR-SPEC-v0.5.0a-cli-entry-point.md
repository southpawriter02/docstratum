# v0.5.0a — CLI Entry Point

> **Version:** v0.5.0a
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.5.0-cli-foundation.md](RR-SPEC-v0.5.0-cli-foundation.md)
> **Grounding:** RR-ROADMAP v0.5.0a, pyproject.toml (no existing `[project.scripts]`)
> **Depends On:** v0.2.x (parser), v0.3.x (validation), v0.4.x (scoring)
> **Module:** `src/docstratum/cli.py`, `src/docstratum/__main__.py`
> **Tests:** `tests/test_cli_entry.py`

---

## 1. Purpose

Register `docstratum` as a console script entry point and create the top-level command dispatcher with a `validate` subcommand. This is the "front door" — the single function that all CLI invocations flow through.

After v0.5.0a:
- `pip install -e .` installs the `docstratum` console command
- `docstratum --version` prints the engine version
- `docstratum --help` shows available subcommands
- `docstratum validate llms.txt` invokes the validation pipeline

---

## 2. Changes Required

### 2.1 `pyproject.toml` — Entry Point Registration

```toml
[project.scripts]
docstratum = "docstratum.cli:main"
```

> **Note:** This requires `pip install -e .` (editable install) to activate. The entry point is not available via `python src/docstratum/cli.py` directly — it must be invoked as a console script or via `python -m docstratum`.

### 2.2 `src/docstratum/__main__.py` — Module Invocation Support

```python
"""Enable `python -m docstratum` invocation.

This module is the entry point for `python -m docstratum`. It simply
delegates to the CLI's main() function.

Implements v0.5.0a.
"""

from docstratum.cli import main

if __name__ == "__main__":
    main()
```

### 2.3 `src/docstratum/cli.py` — Command Dispatcher

```python
"""DocStratum CLI — command-line interface for llms.txt validation.

Entry point for the `docstratum` console command. Dispatches to
subcommands (currently only `validate`).

Implements v0.5.0a.
Grounding: RR-SPEC-v0.5.0-cli-foundation.md §2.
"""

import sys
from pathlib import Path

import click

from docstratum import __version__


@click.group()
@click.version_option(__version__, "--version", "-V", prog_name="docstratum")
def cli() -> None:
    """DocStratum — validation engine for llms.txt files.

    Validates, scores, and reports on llms.txt documentation files.
    Use 'docstratum validate <file>' to analyze a file.
    """
    pass


@cli.command()
@click.argument("path", type=click.Path(exists=True))
# Additional arguments defined in v0.5.0b (argument parsing)
# For v0.5.0a, only 'path' is required
def validate(path: str) -> None:
    """Validate an llms.txt file and report quality score.

    PATH is the file (or directory) to validate.

    Examples:
        docstratum validate llms.txt
        docstratum validate ./docs/llms.txt
    """
    input_path = Path(path)

    # Directory handling — forward-compatible (see parent spec §7)
    if input_path.is_dir():
        click.echo(
            "Warning: Directory validation requires ecosystem mode (v0.7.x). "
            "Scanning for llms.txt files...",
            err=True,
        )
        candidates = list(input_path.glob("llms.txt"))
        if len(candidates) == 1:
            input_path = candidates[0]
        elif len(candidates) == 0:
            click.echo("Error: No llms.txt found in directory.", err=True)
            sys.exit(10)
        else:
            click.echo(
                f"Found {len(candidates)} llms.txt files. "
                "Ecosystem mode required for multi-file validation. "
                "Validating first file only.",
                err=True,
            )
            input_path = candidates[0]

    # --- Pipeline orchestration ---
    # At v0.5.0, this uses hardcoded defaults.
    # v0.5.1+ replaces this with profile-driven configuration.

    try:
        # Step 1: Read and parse the file (v0.2.x)
        # Step 2: Classify the document (v0.2.1)
        # Step 3: Run validation pipeline (v0.3.x)
        # Step 4: Compute quality score (v0.4.x)
        # Step 5: Map exit code (v0.5.0c)
        # Step 6: Render terminal output (v0.5.0d)

        # Placeholder: actual pipeline wiring depends on v0.2.x–v0.4.x
        # being operational. The integration point is documented here.
        from docstratum.cli_exit_codes import compute_exit_code
        from docstratum.cli_output import render_terminal_output

        # The pipeline returns ValidationResult + QualityScore
        # These calls are pseudo-code until v0.2.x–v0.4.x are built:
        #
        # parsed = parse_llms_txt(read_file(input_path))
        # classification = classify_document(parsed)
        # result = validate_file(parsed, classification)
        # score = score_file(result)
        #
        # exit_code = compute_exit_code(result, score, strict=args.strict)
        # if not args.quiet:
        #     render_terminal_output(result, score, args)
        # sys.exit(exit_code)

        click.echo(
            f"Validating: {input_path}\n"
            f"(Pipeline stages v0.2.x–v0.4.x not yet operational)",
            err=True,
        )
        sys.exit(10)

    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(10)
    except Exception as e:
        click.echo(f"Pipeline error: {e}", err=True)
        import os
        if os.environ.get("DOCSTRATUM_DEBUG"):
            import traceback
            traceback.print_exc()
        sys.exit(10)


def main() -> None:
    """CLI entry point — called by console_scripts and __main__.py.

    Wraps the click group with a top-level exception handler
    for consistent error reporting.
    """
    try:
        cli(standalone_mode=False)
    except click.exceptions.Abort:
        sys.exit(1)
    except SystemExit as e:
        sys.exit(e.code)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(10)
```

---

## 3. Decision: `standalone_mode=False`

Click's default `standalone_mode=True` handles `SystemExit` internally and prevents the top-level exception handler from running. Setting `standalone_mode=False` gives our code control over all exit paths, ensuring consistent error handling and exit code semantics.

**Trade-off:** We must manually handle `click.exceptions.Abort` (Ctrl+C) and `SystemExit` (from `--help` and `--version`). This is a small cost for full control.

---

## 4. Workflow

### 4.1 Install and Run

```bash
# 1. Install in editable mode (registers console script)
pip install -e .

# 2. Verify installation
docstratum --version
# Output: docstratum, version 0.1.0

# 3. Run validation
docstratum validate llms.txt
# (At v0.5.0a, this prints a placeholder message and exits 10
#  because the pipeline is not yet wired)

# 4. Alternative invocation
python -m docstratum validate llms.txt
# (Identical behavior to console script)
```

### 4.2 Development Cycle

```bash
# After code changes, re-run (no re-install needed with -e):
docstratum validate tests/fixtures/valid_llms.txt

# Run tests
pytest tests/test_cli_entry.py -v

# Type check
mypy src/docstratum/cli.py src/docstratum/__main__.py

# Format + lint
black src/docstratum/cli.py src/docstratum/__main__.py
ruff check src/docstratum/cli.py src/docstratum/__main__.py
```

---

## 5. Acceptance Criteria

- [ ] `pyproject.toml` has `[project.scripts]` with `docstratum = "docstratum.cli:main"`
- [ ] `pip install -e .` succeeds without error
- [ ] `docstratum --version` prints `docstratum, version 0.1.0`
- [ ] `docstratum --help` prints help text with `validate` subcommand listed
- [ ] `docstratum validate --help` prints help text with `PATH` argument
- [ ] `python -m docstratum --version` prints identical output to `docstratum --version`
- [ ] `docstratum validate nonexistent.txt` exits with code 10 and a clear error message (via `click.Path(exists=True)`)
- [ ] `docstratum validate ./some-directory/` produces a directory-mode warning on stderr
- [ ] Unhandled exceptions exit with code 10 and print the error message
- [ ] `DOCSTRATUM_DEBUG=1 docstratum validate ...` prints full traceback on error
- [ ] `cli.py` module has a docstring citing v0.5.0a
- [ ] `__main__.py` module has a docstring citing v0.5.0a

---

## 6. Deliverables

| File | Description | Status |
|------|-------------|--------|
| `pyproject.toml` | Add `[project.scripts]`, add `click` dependency | MODIFY |
| `src/docstratum/__main__.py` | Module entry point for `python -m docstratum` | NEW |
| `src/docstratum/cli.py` | CLI dispatcher with `validate` subcommand | NEW |
| `tests/test_cli_entry.py` | Unit tests for CLI entry point | NEW |

---

## 7. Test Plan (8 tests)

| # | Test Name | Input | Expected |
|---|-----------|-------|----------|
| 1 | `test_version_flag` | `docstratum --version` | Prints version string, exit 0 |
| 2 | `test_help_flag` | `docstratum --help` | Prints help with "validate" listed, exit 0 |
| 3 | `test_validate_help` | `docstratum validate --help` | Prints validate subcommand help, exit 0 |
| 4 | `test_main_module_invocation` | `python -m docstratum --version` | Same output as test 1 |
| 5 | `test_validate_nonexistent_file` | `docstratum validate nofile.txt` | Exit code 2 (click's UsageError for non-existent path) |
| 6 | `test_validate_file_dispatches` | `docstratum validate <fixture>` | Validate subcommand invoked (even if pipeline not operational) |
| 7 | `test_directory_argument_warning` | `docstratum validate ./tests/` | Warning message on stderr, attempts fallback |
| 8 | `test_debug_env_traceback` | `DOCSTRATUM_DEBUG=1` + pipeline error | Traceback printed to stderr |

**Test infrastructure:**

```python
"""Tests for v0.5.0a — CLI Entry Point.

Uses click.testing.CliRunner for isolated CLI invocation
without subprocess overhead.
"""

from click.testing import CliRunner
from docstratum.cli import cli


def test_version_flag():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "docstratum" in result.output
    assert "0.1.0" in result.output  # or whatever __version__ is


def test_help_flag():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "validate" in result.output


def test_validate_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["validate", "--help"])
    assert result.exit_code == 0
    assert "PATH" in result.output
```
