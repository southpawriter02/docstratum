# v0.5.0 — CLI Foundation

> **Version:** v0.5.0
> **Document Type:** Parent Design Specification (CLI Foundation)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SCOPE-v0.5.x-cli-and-profiles.md](RR-SCOPE-v0.5.x-cli-and-profiles.md)
> **Governing Specs:** RR-SPEC-v0.1.3-validation-profiles.md §5.5, RR-SPEC-v0.1.3-output-tier-specification.md §2.1.1
> **Depends On:** v0.4.x (`QualityScore`, `QualityGrade`, `DimensionScore`), v0.3.x (`ValidationResult`, `ValidationDiagnostic`), v0.2.x (`ParsedLlmsTxt`), v0.1.2a (`DiagnosticCode`, `Severity`)
> **Consumed By:** v0.5.1 (Validation Profiles), v0.5.2 (Profile Discovery), v0.6.x (Remediation), v0.7.x (Ecosystem CLI mode)

---

## 1. Purpose

v0.5.0 builds the **CLI Foundation** — the command-line entry point, argument parser, exit code mapper, and terminal formatter that allow a user to run `docstratum validate <path>` and receive structured feedback for the first time.

Before v0.5.0, the DocStratum engine has parsers (v0.2.x), validators (v0.3.x), and scorers (v0.4.x), but no user-facing invocation mechanism. A developer must write Python scripts importing internal modules to run validation. v0.5.0 changes that:

```bash
# After v0.5.0, this works:
docstratum validate llms.txt
# Exit code: 0 (pass) | 1-5 (various failures) | 10 (pipeline error)

# Also works:
python -m docstratum validate llms.txt
```

### 1.1 What v0.5.0 Is

A **functional CLI with hardcoded defaults**. The CLI can validate a single file, parse all arguments defined in the full v0.5.x spec, map pipeline results to process exit codes, and render a colorized terminal summary. Profile awareness is absent — v0.5.0 uses hardcoded defaults equivalent to the `ci` profile (`max_validation_level=3`, `enabled_stages=[1, 2]`).

### 1.2 What v0.5.0 Is NOT

| Not This | Why | Where It Lives |
|----------|-----|----------------|
| Profile-aware validation | Profiles require the `ValidationProfile` model and loading infrastructure | v0.5.1 |
| Profile discovery/loading | Requires YAML/JSON loader, precedence chain, and inheritance | v0.5.2 |
| Ecosystem dispatch (directory mode) | Requires ecosystem pipeline wiring | v0.7.x |
| Report generation | Requires Stage 6 and format renderers | v0.8.x |

### 1.3 User Story

> As a developer, I want to run `docstratum validate llms.txt` from my terminal and receive a score, grade, and list of diagnostics, so that I can assess the quality of my `llms.txt` file without writing custom Python scripts.

> As a CI pipeline, I want `docstratum validate llms.txt` to return a meaningful exit code (0 for pass, non-zero for failure) so that I can gate merges on documentation quality.

---

## 2. Architecture

### 2.1 Module Map

```
pyproject.toml                     ← [project.scripts] entry point
│
src/docstratum/
├── __main__.py                    ← python -m docstratum support [NEW]
├── cli.py                         ← main(), validate_command() [NEW]
├── cli_args.py                    ← argument parsing (click or argparse) [NEW]
├── cli_exit_codes.py              ← exit code mapping [NEW]
├── cli_output.py                  ← terminal formatter [NEW]
│
├── schema/
│   ├── validation.py              ← ValidationResult (READ)
│   ├── quality.py                 ← QualityScore, QualityGrade (READ)
│   ├── diagnostics.py             ← DiagnosticCode, Severity (READ)
│   └── ...
├── pipeline/
│   └── stages.py                  ← PipelineContext (READ + WRITE .profile field)
└── __init__.py                    ← __version__ (READ)
```

### 2.2 Data Flow

```
┌─────────────────────────────┐
│ User runs:                   │
│ docstratum validate llms.txt │
└──────────────┬──────────────┘
               │
               ▼
┌──────────────────────────────┐
│ v0.5.0a: cli.py → main()    │ Dispatch to validate subcommand
│   Reads: sys.argv            │
│   Writes: nothing            │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ v0.5.0b: cli_args.py         │ Parse --profile, --max-level, --tags, etc.
│   Reads: sys.argv             │
│   Writes: CliArgs namespace   │ All CLI values stored; None = "don't override"
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ validate_command()           │ Orchestrates the pipeline
│   1. Read file from disk     │ (v0.2.0a: read_file())
│   2. Parse markdown          │ (v0.2.0b–c: parse_llms_txt())
│   3. Classify document       │ (v0.2.1: classify_document())
│   4. Run validation          │ (v0.3.x: validate_file())
│   5. Compute score           │ (v0.4.x: score_file())
│   6. Map exit code           │ (v0.5.0c)
│   7. Render terminal output  │ (v0.5.0d)
│   8. sys.exit(code)          │
└──────────────┬───────────────┘
               │
       ┌───────┴───────┐
       │               │
       ▼               ▼
┌──────────────┐ ┌──────────────────┐
│ v0.5.0c:     │ │ v0.5.0d:         │
│ Exit Code    │ │ Terminal Output   │
│ Mapper       │ │ Renderer          │
│              │ │                   │
│ Reads:       │ │ Reads:            │
│ - result     │ │ - result          │
│ - score      │ │ - score           │
│ - strict?    │ │ - verbose/quiet?  │
│              │ │ - output-format?  │
│ Returns: int │ │ Returns: None     │
│ (0–10)       │ │ (prints to stdout)│
└──────────────┘ └──────────────────┘
```

### 2.3 Hardcoded Defaults (v0.5.0 Only)

Until profiles are operational (v0.5.1+), the CLI uses these hardcoded defaults:

| Concern | Default Value | Equivalent Profile |
|---------|---------------|-------------------|
| `max_validation_level` | `3` | `ci` |
| `enabled_stages` | `[1, 2]` | Partial — CI runs all stages but v0.5.0 only has single-file support |
| `rule_tags_include` | `[]` (all) | — |
| `rule_tags_exclude` | `[]` (none) | — |
| `pass_threshold` | `None` | No threshold enforcement |
| `output_tier` | `2` | Diagnostic Report |
| `output_format` | `"terminal"` | — |

These defaults are extracted to a `CLI_DEFAULTS` constant dictionary (in `cli.py`) so that v0.5.1 can replace them with a loaded `ValidationProfile` without restructuring the CLI code.

---

## 3. Sub-Part Breakdown

### 3.1 v0.5.0a — CLI Entry Point

**Module:** `cli.py` + `__main__.py`
**What it does:** Registers the `docstratum` console script and creates the top-level command dispatcher with `validate` subcommand.
**Design Spec:** [RR-SPEC-v0.5.0a-cli-entry-point.md](RR-SPEC-v0.5.0a-cli-entry-point.md)

---

### 3.2 v0.5.0b — Argument Parsing

**Module:** `cli_args.py`
**What it does:** Defines the full CLI argument schema (12 arguments). All arguments are parsed and stored; their consumption by profiles happens in v0.5.1+.
**Design Spec:** [RR-SPEC-v0.5.0b-argument-parsing.md](RR-SPEC-v0.5.0b-argument-parsing.md)

---

### 3.3 v0.5.0c — Exit Codes

**Module:** `cli_exit_codes.py`
**What it does:** Maps pipeline results to process exit codes (0–5, 10) per the convention in RR-SPEC-v0.1.3-output-tier-specification.md §2.1.1.
**Design Spec:** [RR-SPEC-v0.5.0c-exit-codes.md](RR-SPEC-v0.5.0c-exit-codes.md)

---

### 3.4 v0.5.0d — Terminal Output

**Module:** `cli_output.py`
**What it does:** Renders a colorized terminal summary of the validation result: score, grade, level checklist, dimension breakdown, diagnostic listing.
**Design Spec:** [RR-SPEC-v0.5.0d-terminal-output.md](RR-SPEC-v0.5.0d-terminal-output.md)

---

## 4. Dependency Chain

```
v0.5.0a (Entry Point)          ← no internal dependencies, greenfield
    │
    ▼
v0.5.0b (Argument Parsing)    ← depends on v0.5.0a command structure
    │
    ├────────────┐
    ▼            ▼
v0.5.0c        v0.5.0d        ← both depend on v0.5.0b for parsed arguments
(Exit Codes)   (Terminal Out)  ← co-dependent: exit codes inform display,
                                 display renders score that exit code uses
```

**Parallelization:** v0.5.0c and v0.5.0d can be developed simultaneously after v0.5.0b is complete. They are co-dependent at integration time but independently testable.

**External Dependencies:**
- v0.3.x operational → `ValidationResult` with diagnostics
- v0.4.x operational → `QualityScore` with score, grade, dimensions
- v0.2.x operational → `ParsedLlmsTxt` (file parsing and token estimation)

---

## 5. CLI Library Decision

### 5.1 Options Considered

| Library | Pros | Cons |
|---------|------|------|
| `argparse` (stdlib) | Zero dependencies; batteries included; no pip install needed | Verbose decorator-less API; manual help formatting; no built-in color |
| `click` | Decorator-based; composable commands; built-in help formatting; rich ecosystem | Third-party dep (~100KB); different mental model from argparse |
| `typer` | Click + type hints; auto-complete; self-documenting | Heavier dep chain (click + typer + typing-extensions); may be overkill |

### 5.2 Decision: `click`

**DECISION-033: Use `click` for CLI implementation.**

**Rationale:**
1. **Composable subcommands.** The `validate` subcommand is the first of several — future versions may add `docstratum check-profile`, `docstratum init`, `docstratum config`. `click`'s `@cli.group()` / `@cli.command()` model handles this cleanly.
2. **Type conversion built in.** `click.IntRange(0, 4)` for `--max-level`, `click.Choice(["json", "terminal", ...])` for `--output-format` — these reduce manual validation boilerplate.
3. **Help generation.** `click` auto-generates `--help` output from docstrings and parameter metadata. This pairs well with the spec-heavy approach (parameter descriptions become the help text).
4. **Ecosystem alignment.** `click` is widely used in Python CLI tools (Flask, Black, pip-tools). It's a stable, maintained library with strong community support.
5. **Minimal weight.** `click` has no transitive dependencies beyond the stdlib. At ~100KB, it adds negligible overhead.

**Alternative consideration:** If `click` is rejected in favor of zero-dependency purity, all spec logic holds — the argument parsing module swaps from click decorators to `argparse.ArgumentParser`, but the argument names, types, defaults, and override semantics are identical. The design spec for v0.5.0b defines the argument schema in a library-agnostic way and provides both a click and argparse implementation strategy.

### 5.3 Dependency Addition

```toml
# pyproject.toml — add to dependencies
dependencies = [
    "pydantic>=2.0,<3.0",
    "click>=8.0,<9.0",
]
```

---

## 6. Models Consumed (Not Modified)

| Model | Source | Read Fields | Purpose |
|-------|--------|-------------|---------|
| `ValidationResult` | `schema/validation.py` | `diagnostics`, `level_achieved`, `levels_passed`, `total_errors`, `total_warnings` | Exit code + terminal display |
| `ValidationDiagnostic` | `schema/validation.py` | `code`, `severity`, `message`, `remediation`, `line_number`, `context`, `level` | Terminal diagnostic listing |
| `QualityScore` | `schema/quality.py` | `total_score`, `grade`, `dimensions` | Score/grade display + threshold comparison |
| `QualityGrade` | `schema/quality.py` | Grade enum value | Colorized grade display |
| `DimensionScore` | `schema/quality.py` | `points`, `max_points`, `details` | Dimension breakdown display |
| `DiagnosticCode` | `schema/diagnostics.py` | Code values | Severity override lookup |
| `Severity` | `schema/diagnostics.py` | Enum values | Exit code classification |
| `ValidationLevel` | `schema/validation.py` | Level values | Exit code priority logic |

**No new models created in v0.5.0.** The `ValidationProfile` model is created in v0.5.1a, not here.

---

## 7. Directory Argument Handling (Forward Design)

At v0.5.0, the CLI **accepts** directory arguments but cannot process them:

```bash
docstratum validate ./docs/    # Accepted, but produces a warning
```

**Behavior:**

```python
if input_path.is_dir():
    click.echo(
        "Warning: Directory validation requires ecosystem mode (v0.7.x). "
        "Scanning for llms.txt files...",
        err=True,
    )
    # Attempt to find a single llms.txt in the directory
    candidates = list(input_path.glob("llms.txt"))
    if len(candidates) == 1:
        input_path = candidates[0]  # Validate the single file
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
```

This forward-compatible approach means the CLI infrastructure is ready for v0.7.x to plug in ecosystem dispatch without changing argument parsing.

---

## 8. Error Handling Strategy

### 8.1 Error Categories

| Category | Example | Handling | Exit Code |
|----------|---------|----------|-----------|
| **User error** | File not found, invalid argument value | Clear error message + usage hint | 10 |
| **Pipeline error** | Exception during validation/scoring | Catch at top level, print traceback if `--verbose` | 10 |
| **Validation failure** | E001 found in file | Normal flow → exit code 1–5 | 1–5 |
| **Score below threshold** | Score 42 < threshold 50 | Normal flow → exit code 5 | 5 |
| **Clean pass** | No errors, score above threshold | Normal flow → exit code 0 | 0 |

### 8.2 Top-Level Exception Handler

```python
def main():
    """DocStratum CLI entry point."""
    try:
        cli()  # click group dispatcher
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(10)
    except Exception as e:
        click.echo(f"Pipeline error: {e}", err=True)
        if os.environ.get("DOCSTRATUM_DEBUG"):
            import traceback
            traceback.print_exc()
        sys.exit(10)
```

---

## 9. Inline Documentation Requirements

All new modules MUST include:

1. **Module docstring** — citing the spec version implemented (e.g., `"""Implements v0.5.0a — CLI Entry Point."""`)
2. **Function docstrings** — Google-style with Args, Returns, Raises
3. **Version traces** — `# Implements v0.5.0a` on key functions
4. **Grounding comments** — `# Grounding: RR-SPEC-v0.1.3-output-tier-specification §2.1.1` on design-critical logic

---

## 10. Changelog Requirements

Upon completion of v0.5.0 (all 4 sub-parts), a changelog entry is required:

```markdown
## [0.5.0] — 2026-XX-XX

### Added
- CLI entry point: `docstratum validate <path>` console script (v0.5.0a)
- `python -m docstratum` support via `__main__.py` (v0.5.0a)
- Full argument parsing: --profile, --max-level, --tags, --exclude-tags,
  --output-tier, --output-format, --pass-threshold, --check-urls, --strict,
  --verbose, --quiet, --version (v0.5.0b)
- Exit code mapping (0=pass, 1=structural, 2=content, 3=warnings[strict],
  4=ecosystem, 5=score-below-threshold, 10=pipeline-error) (v0.5.0c)
- Terminal output renderer with colorized score/grade, level checklist,
  dimension breakdown, sorted diagnostic listing (v0.5.0d)
- JSON output mode via `--output-format json` (v0.5.0d)
- `--quiet` mode (exit code only) and `--verbose` mode (full diagnostics) (v0.5.0d)
- `NO_COLOR` environment variable respected for monochrome output (v0.5.0d)

### Dependencies
- Added `click>=8.0,<9.0` for CLI framework (DECISION-033)
```

---

## 11. Acceptance Criteria (v0.5.0 Composite)

All 4 sub-parts must pass their individual acceptance criteria (see sub-part specs). In addition:

- [ ] `pip install -e .` registers the `docstratum` console script
- [ ] `docstratum validate <file>` produces a terminal summary and exit code
- [ ] `python -m docstratum validate <file>` produces identical output
- [ ] `docstratum --version` prints the engine version
- [ ] `docstratum --help` displays top-level help
- [ ] `docstratum validate --help` displays validate subcommand help
- [ ] All CLI arguments from v0.5.0b are parsed without error (even if not consumed by profiles yet)
- [ ] Exit codes match the precedence table in v0.5.0c
- [ ] Terminal output matches the layout specification in v0.5.0d
- [ ] `--quiet` suppresses all output
- [ ] `--verbose` shows all diagnostics with remediation
- [ ] `--output-format json` serializes result as JSON
- [ ] Directory argument produces a graceful warning and attempts single-file fallback
- [ ] `pytest --cov=docstratum --cov-fail-under=85` passes for CLI modules
- [ ] `black --check` and `ruff check` pass on all new code
- [ ] `mypy src/docstratum/cli.py src/docstratum/cli_args.py src/docstratum/cli_exit_codes.py src/docstratum/cli_output.py` passes

---

## 12. Test Strategy

| Test Category | Location | Coverage Target | Description |
|---------------|----------|-----------------|-------------|
| Unit: Entry Point | `tests/test_cli_entry.py` | ≥85% | Test `main()` dispatch, `--version`, `--help` |
| Unit: Arg Parsing | `tests/test_cli_args.py` | ≥90% | Test all 12 arguments, defaults, edge cases |
| Unit: Exit Codes | `tests/test_cli_exit_codes.py` | 100% | Test all 7 exit code conditions |
| Unit: Terminal Output | `tests/test_cli_output.py` | ≥85% | Test formatted output rendering |
| Integration: End-to-End | `tests/test_cli_integration.py` | ≥80% | Full CLI invocation via `click.testing.CliRunner` |

**Test tooling:** Use `click.testing.CliRunner` for integration tests — it captures stdout, stderr, and exit codes without subprocess overhead.

---

## 13. Limitations

| Limitation | Impact | Resolution Version |
|------------|--------|-------------------|
| No profile loading — hardcoded defaults only | Users cannot customize validation behavior | v0.5.1 (profile model), v0.5.2 (loading) |
| No ecosystem/directory validation | Directory arguments produce a fallback warning | v0.7.x (ecosystem CLI mode) |
| No Tier 3/4 output | Remediation playbooks and audience-adapted reports require later phases | v0.6.x (remediation), v0.8.x (reports) |
| No Stage 6 renderers | Markdown/HTML/YAML formats not available | v0.8.x (report generation) |
| Tag filtering is a no-op | Rule Registry not yet built — tags are empty | Deliverable 3 (Rule Registry) |
| Severity overrides not applied | Profile system not yet operational | v0.5.1c (filtering engine) |
