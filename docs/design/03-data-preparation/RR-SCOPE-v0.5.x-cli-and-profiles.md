# v0.5.x CLI & Profiles — Scope Breakdown

> **Version Range:** v0.5.0 through v0.5.2
> **Document Type:** Scope Breakdown (precedes individual design specifications)
> **Status:** DRAFT
> **Created:** 2026-02-09
> **Last Updated:** 2026-02-09
> **Parent:** RR-ROADMAP-validator-v0.0.1-to-v1.0.0.md
> **Spec Basis:** RR-SPEC-v0.1.3-validation-profiles.md, RR-SPEC-v0.1.3-output-tier-specification.md
> **Consumes:** v0.4.x (`QualityScore`, `QualityGrade`, `DimensionScore`), v0.3.x (`ValidationResult`, `ValidationDiagnostic`), v0.2.x (`ParsedLlmsTxt`, `DocumentClassification`), v0.1.2a (`DiagnosticCode`, `Severity`), v0.1.2c (`ValidationLevel`), `constants.py` (all enums and registries)
> **Consumed By:** v0.6.x (Remediation Framework), v0.7.x (Ecosystem Integration), v0.8.x (Report Generation)
> **Key Decisions:** DECISION-029 (buffet composition), DECISION-030 (OR semantics), DECISION-031 (single-level inheritance), DECISION-032 (shallow CLI overrides)

---

## 1. Purpose

Phase 5 builds the **user-facing interface** — the CLI entry point and the validation profile system that governs what the pipeline does for a given run. This is where the internal validation and scoring machinery (v0.2.x through v0.4.x) becomes accessible to users: a developer runs `docstratum validate llms.txt` from the terminal and gets structured feedback. A CI system loads the `ci` profile and receives a machine-readable pass/fail gate. A documentation team loads the `full` profile and receives a comprehensive diagnostic report.

The CLI answers *"How do I invoke the validator?"* The profile system answers *"What does a successful validation look like for my use case?"*

Prior to v0.5.x, there is no CLI entry point. The `pyproject.toml` has no `[project.scripts]` section, no `cli.py` module exists, no `__main__.py` exists, and no profile YAML files exist on disk. The `ValidationProfile` Pydantic model is specified in RR-SPEC-v0.1.3-validation-profiles.md but not yet implemented as runtime code. Everything in v0.5.x is greenfield construction from specification blueprints.

The core architectural insight behind the profile system is the **"buffet" composition model** (DECISION-029): each diagnostic rule carries tags (`"structural"`, `"content"`, `"ecosystem"`, `"experimental"`, etc.), and a profile specifies which tags to include or exclude. This tag-based filtering — combined with level gating (`max_validation_level`), stage gating (`enabled_stages`), severity/priority overrides, a pass threshold, and output tier/format selection — produces a declarative specification of a validation run. A profile is essentially a named, reusable, inheritable buffet selection.

---

## 2. Scope Boundary: What the CLI & Profiles ARE and ARE NOT

### 2.1 The CLI & Profiles ARE

A **user-facing interface and run-configuration layer** that accepts command-line arguments, discovers and loads a validation profile, injects that profile into the `PipelineContext`, orchestrates pipeline stage execution (respecting the profile's `enabled_stages`), filters rules by tag and level, applies severity and priority overrides to emitted diagnostics, evaluates the pass/fail threshold against the `QualityScore`, maps the outcome to a process exit code, and renders a basic terminal summary.

**Input:** Command-line arguments (`docstratum validate <path> [--profile <name>] [--max-level <int>] ...`), profile files (YAML/JSON), project configuration (`.docstratum.yml`), user configuration (`~/.docstratum/profiles/`).
**Output:** A process exit code (0–10), terminal summary output (file name, score, grade, diagnostic counts), and the `PipelineContext` enriched with the loaded `ValidationProfile`.

### 2.2 The CLI & Profiles ARE NOT

| Out of Scope | Why | Where It Lives |
|--------------|-----|----------------|
| **Executing validation checks** | The CLI orchestrates the pipeline; the validator (v0.3.x) executes individual checks. The profile tells the pipeline *which* checks to run, but the CLI never evaluates a diagnostic rule directly. | v0.3.x (Validation Engine) |
| **Computing quality scores** | The scorer (v0.4.x) computes `QualityScore`. The CLI reads the score for threshold comparison and terminal display. | v0.4.x (Quality Scoring) |
| **Generating remediation guidance** | The remediation framework (v0.6.x) transforms diagnostics into prioritized action items. The CLI may eventually render them, but it does not produce them. | v0.6.x (Remediation Framework) |
| **Rendering formatted reports** | Stage 6 (Report Generation, v0.8.x) renders `QualityScore` and diagnostics into JSON, Markdown, HTML documents. The CLI produces a minimal terminal summary (v0.5.0d) but full report rendering is a later phase. | v0.8.x (Report Generation) |
| **Implementing the Rule Registry** | The profile system depends on rules having `tags` fields for filtering. The Rule Registry (Deliverable 3 in the documentation backlog) defines these tags. The CLI loads whatever tags exist; it does not define the tag vocabulary or the rules themselves. | Deliverable 3 (Rule Registry) |
| **Modifying any input models** | The CLI reads `ValidationResult`, `QualityScore`, etc. It never mutates them. The only model it writes to is `PipelineContext.profile`. | Never |
| **Ecosystem-level scoring** | The ecosystem pipeline (v0.7.x) handles multi-file validation orchestration. The CLI dispatches to the ecosystem pipeline when a directory is provided, but the ecosystem scoring logic lives in v0.7.x. | v0.7.x (Ecosystem Integration) |

### 2.3 The Rule Registry Dependency Gap

The tag-based filtering model (v0.5.1c) depends on diagnostic rules being tagged with categories like `"structural"`, `"content"`, `"ecosystem"`, and `"experimental"`. This tag vocabulary and per-rule tag assignment is defined by the **Rule Registry** (Deliverable 3 in RR-META-documentation-backlog.md).

At v0.5.x, the Rule Registry may not yet be implemented as a formal data structure. The scope therefore defines two modes:

1. **With Rule Registry (nominal):** The filtering engine queries the registry for all rules, checks each rule's `tags` set against the profile's `rule_tags_include` and `rule_tags_exclude`, and activates or deactivates rules accordingly. This is the full buffet model described in RR-SPEC-v0.1.3-validation-profiles.md §4.

2. **Without Rule Registry (bootstrap):** If the Rule Registry is not yet implemented, tag-based filtering cannot operate. In this case, the filtering engine falls back to **level gating only** — the profile's `max_validation_level` controls which checks run. Tags are ignored (treated as empty). This is a graceful degradation that preserves the CLI and profile infrastructure while waiting for the Rule Registry to be built.

The design spec for v0.5.1c should define this fallback behavior explicitly. The scope requires that tag filtering *works correctly when tags are available* and *degrades gracefully when they are not*.

### 2.4 The Stage 6 Forward Reference

The `ValidationProfile` model includes `output_tier` (1–4), `output_format` ("json", "markdown", "yaml", "html", "terminal"), and `grouping_mode` ("by-priority", "by-level", "by-file", "by-effort"). These fields configure Stage 6 (Report Generation), which is not built until v0.8.x.

At v0.5.x, the CLI handles these fields as follows:

- **`output_tier`:** Stored on the profile but not fully interpreted. The CLI produces Tier 1 data (pass/fail, exit code, score, grade) and Tier 2 data (diagnostic list) for terminal display. Tier 3 (Remediation Playbook) and Tier 4 (Audience-Adapted) require v0.6.x and v0.8.x respectively.
- **`output_format`:** Respected for "terminal" (default) — the CLI renders colored ANSI output. For "json", the CLI serializes the pipeline result as JSON to stdout. Other formats ("markdown", "yaml", "html") are stored on the profile for future Stage 6 consumption but produce a warning: "Format '{format}' requires Stage 6 (Report Generation), which is not yet available. Falling back to terminal output."
- **`grouping_mode`:** Stored on the profile. Not consumed until v0.8.x.

This forward-compatible design means profiles written for v0.5.x will work without modification when v0.8.x enables Stage 6.

**Format-Tier Compatibility Constraint:** Not all format-tier combinations are valid. RR-SPEC-v0.1.3-output-tier-specification.md §4.2 defines a compatibility matrix — for example, Tier 1 + Markdown is "Not Supported" (a pass/fail gate doesn't warrant a document), and Tier 3 + YAML is "Not Supported" (a remediation playbook is prose, not configuration data). At v0.5.x, the CLI should validate the profile's `output_tier` / `output_format` pairing against this matrix and warn on invalid combinations. The warning should suggest a compatible format (e.g., "Tier 3 + YAML is not supported. Consider using Markdown (the primary format for Tier 3) or JSON.").

### 2.5 The Gray Zone: Ecosystem vs. Single-File Invocation

The CLI accepts both single files and directories:

```bash
docstratum validate llms.txt           # Single-file mode
docstratum validate ./docs/            # Ecosystem mode (directory)
```

At v0.5.x, the scope focuses on **single-file validation** (Stages 1–2, with optional 3–5 if the profile enables them). Full ecosystem orchestration is wired in v0.7.x. However, the CLI argument parsing (v0.5.0b) and profile stage gating (v0.5.1c) must support both modes from the start — the infrastructure is built now, even if the ecosystem pipeline integration comes later.

Specifically:
- `enabled_stages=[1, 2]` → single-file validation only.
- `enabled_stages=[1, 2, 3, 4, 5]` → ecosystem validation (but ecosystem stages may be no-ops if the ecosystem pipeline is not yet wired into the CLI dispatch).

The design spec for v0.5.0a should define how directory arguments are handled at v0.5.x (recommended: accept the argument, dispatch to the ecosystem pipeline if available, log a warning if ecosystem stages are not yet operational).

### 2.6 The Gray Zone: Profile Validation Strictness

The `ValidationProfile` model has fields that reference entities not yet implemented: `rule_tags_include` references tag names that only exist in the Rule Registry; `enabled_stages` references Stage 6 which doesn't exist; `grouping_mode` references the remediation grouping logic in v0.8.x.

Two approaches to validation:

1. **Strict validation:** Reject unknown tags, unknown stage IDs, and unknown grouping modes at load time. Breaks forward-compatibility — a profile written for v0.8.x features can't load in v0.5.x.
2. **Lenient validation:** Accept unknown values with a warning. Forward-compatible — profiles written for future versions load in current versions without error.

The recommended approach is **lenient validation with warnings** (option 2), because:
- Profiles are meant to be version-stable — a team writes one profile and uses it across CLI upgrades.
- Unknown tags simply mean no rules match that tag, which is harmless.
- Unknown stage IDs are skipped (already the behavior in the orchestrator).
- Unknown grouping modes fall back to the default ("by-priority").

The design spec for v0.5.2a should formalize this.

---

## 3. Sub-Part Breakdown

### 3.1 v0.5.0 — CLI Foundation

**Goal:** Provide a basic command-line interface that allows a user to run `docstratum validate <path>` and receive structured output. This sub-version creates the CLI entry point, argument parser, exit code mapping, and minimal terminal formatter. No profile awareness yet — v0.5.0 uses hardcoded defaults equivalent to the `ci` profile.

---

#### v0.5.0a — CLI Entry Point

**What it does:** Registers `docstratum` as a console script entry point in `pyproject.toml` and creates the top-level command dispatcher with a `validate` subcommand.

**Changes Required:**

1. **`pyproject.toml`:** Add `[project.scripts]` section:
   ```toml
   [project.scripts]
   docstratum = "docstratum.cli:main"
   ```

2. **`src/docstratum/cli.py`:** New module containing the `main()` function that:
   - Parses top-level arguments (subcommand dispatch)
   - Routes to `validate_command()` for the `validate` subcommand
   - Handles `--version` (reads `__version__` from `__init__.py`)
   - Handles `--help`

3. **`src/docstratum/__main__.py`:** New module enabling `python -m docstratum`:
   ```python
   from docstratum.cli import main
   main()
   ```

**Pipeline Integration:**
- The `validate_command()` function creates a `PipelineContext`, invokes the validation pipeline (v0.3.x) and scoring pipeline (v0.4.x) on the specified file, and passes the result to the terminal formatter (v0.5.0d).
- At v0.5.0, the pipeline is invoked with hardcoded defaults: `max_validation_level=3`, `enabled_stages=[1, 2]`, no tag filtering. Profile-aware invocation comes in v0.5.1.

**What this does NOT do:**
- Does not parse profile arguments — that's v0.5.0b.
- Does not dispatch to ecosystem mode for directory arguments — that's deferred (see §2.5).
- Does not create any models or modify existing schemas.

**Grounding:** RR-ROADMAP v0.5.0a, pyproject.toml (no existing `[project.scripts]`).

---

#### v0.5.0b — Argument Parsing

**What it does:** Defines the full CLI argument schema for the `validate` subcommand. All arguments are parsed and stored; their consumption by profiles happens in v0.5.1–v0.5.2.

**Arguments:**

| Argument | Type | Default | Description | Maps To (Profile Field) |
|----------|------|---------|-------------|------------------------|
| `path` | positional | (required) | File or directory path to validate | N/A (pipeline input) |
| `--profile` | str | `None` | Profile name ("ci") or file path ("./my.yaml") | Profile loading trigger |
| `--max-level` | int (0–4) | `None` | Override `max_validation_level` | `max_validation_level` |
| `--tags` | CSV str | `None` | Override `rule_tags_include` | `rule_tags_include` |
| `--exclude-tags` | CSV str | `None` | Override `rule_tags_exclude` | `rule_tags_exclude` |
| `--output-tier` | int (1–4) | `None` | Override `output_tier` | `output_tier` |
| `--output-format` | str | `None` | Override `output_format` | `output_format` |
| `--pass-threshold` | int (0–100) | `None` | Override `pass_threshold` | `pass_threshold` |
| `--check-urls` | flag | `False` | Enable URL reachability checks (v0.3.2b) | Legacy mapping |
| `--strict` | flag | `False` | Treat L3 warnings as exit-code failures (exit code 3) | Affects exit code logic |
| `--verbose` | flag | `False` | Increase terminal output detail | Affects terminal formatter |
| `--quiet` | flag | `False` | Suppress all output except exit code | Tier 1 behavior |
| `--version` | flag | — | Print version and exit | N/A |

**Design Notes:**

- **CLI library choice:** The spec does not prescribe `argparse` vs. `click` vs. `typer`. The design spec for v0.5.0b should decide. `click` is recommended for its decorator-based API and built-in help generation; `argparse` is acceptable if zero additional dependencies are preferred.
- **CSV parsing for `--tags`:** `--tags structural,content` parses to `["structural", "content"]`. Whitespace around commas is stripped.
- **`None` means "don't override":** When a CLI argument is `None`, the profile's value is used. When present, the CLI value overrides the profile's value (DECISION-032: shallow overrides).
- **`--check-urls` is a legacy convenience flag:** It maps to the `check_urls` behavior defined in v0.3.2b. The profile system does not have an explicit `check_urls` field — this is handled via tag inclusion/exclusion of URL-related rules. The mapping is: `--check-urls` → include rules tagged `"url-reachability"`. **Note:** This mapping is provisional — the `"url-reachability"` tag name depends on the Rule Registry (Deliverable 3) defining it. If the Rule Registry uses a different tag name, update this mapping.
- **`--strict` elevates warnings to exit-code significance:** Without `--strict`, L3 warnings (W-severity) do not affect the exit code — the process exits 0 unless errors exist or the score is below threshold. With `--strict`, any L3 WARNING triggers exit code 3. This matches the convention in RR-SPEC-v0.1.3-output-tier-specification.md §2.1.1.

**Grounding:** RR-SPEC-v0.1.3-validation-profiles.md §5.5 (CLI Flag Composition), DECISION-032 (shallow overrides).

---

#### v0.5.0c — Exit Codes

**What it does:** Maps pipeline results to process exit codes following the convention defined in RR-SPEC-v0.1.3-output-tier-specification.md §2.1.1.

**Exit Code Table:**

| Code | Meaning | Condition |
|------|---------|-----------|
| `0` | Pass | All checks pass at configured threshold; `total_score >= pass_threshold` (or no threshold set) |
| `1` | Structural errors | At least one ERROR-severity diagnostic from L0 or L1 |
| `2` | Content errors | At least one ERROR-severity diagnostic from L2 |
| `3` | Best practice warnings | At least one WARNING-severity diagnostic from L3 (only when `--strict` treats warnings as errors; otherwise warnings don't affect exit code) |
| `4` | Ecosystem errors | At least one ecosystem-level ERROR diagnostic (E009, E010) |
| `5` | Score below threshold | `total_score < pass_threshold` AND no ERROR-severity diagnostics (if ERROR diagnostics exist, exit code 1–4 takes precedence) |
| `10` | Pipeline error | Unhandled exception in any pipeline stage |

**Precedence Logic:**
- Exit codes are ordered by severity. If multiple conditions are true, the **lowest non-zero exit code** wins (highest severity).
- Code 0 is returned only if NO error conditions are true.
- Code 10 supersedes all others (pipeline crash).

**Implementation:**
```
1. If unhandled exception occurred → return 10
2. If any L0/L1 ERROR diagnostics → return 1
3. If any L2 ERROR diagnostics → return 2
4. If any WARNING diagnostics from L3 AND strict mode → return 3
5. If any ecosystem ERROR diagnostics → return 4
6. If pass_threshold set AND total_score < pass_threshold → return 5
7. Return 0
```

**What this does NOT do:**
- Does not define new exit codes beyond 0–5 and 10. Future phases may add codes but the CLI reserves 6–9 for that purpose.
- Does not handle ecosystem exit codes until the ecosystem pipeline is wired in (v0.7.x). At v0.5.x, code 4 is architecturally defined but never emitted.

**Grounding:** RR-SPEC-v0.1.3-output-tier-specification.md §2.1.1 (Exit Code Convention), RR-ROADMAP v0.5.0c.

---

#### v0.5.0d — Terminal Output

**What it does:** Renders a basic, colorized terminal summary of the validation result. This is the minimal Tier 2 terminal renderer — enough for a developer to understand what happened without drowning in data.

**Output Structure:**

```
DocStratum v0.1.0 | Profile: ci | 2026-02-09 14:30:00

llms.txt ····················· 78 / 100 (STRONG)
  ✓ L0 Parseable        ✓ L1 Structural
  ✓ L2 Content           ✓ L3 Best Practices

  Structural:   28 / 30  (93%)
  Content:      36 / 50  (73%)
  Anti-Pattern: 14 / 20  (70%)

  2 errors · 4 warnings · 1 info

  E006  line 14  Broken link: https://docs.example.com/missing
  E006  line 22  Broken link: https://docs.example.com/old-api
  W003  line 8   Link missing description
  W003  line 12  Link missing description
  W003  line 18  Link missing description
  W003  line 25  Link missing description
  I004  line 31  Relative URL detected: ./api/endpoints
```

**Formatting Rules:**

- **Header line:** Engine version, active profile name, timestamp.
- **Score line:** Filename, score out of 100, grade in parentheses. Grades are colorized: EXEMPLARY/STRONG = green, ADEQUATE = yellow, NEEDS_WORK = orange, CRITICAL = red.
- **Level checklist:** Per-level pass/fail with ✓ (green) or ✗ (red).
- **Dimension breakdown:** Three rows showing per-dimension points, max, and percentage.
- **Summary counts:** Error, warning, info counts.
- **Diagnostic list:** Sorted by severity (ERROR first), then by line number. Each entry: code, line number, brief message. Truncated to top 20 diagnostics if there are more than 20 (with a "...and N more" footer).

**Colorization:**
- Uses ANSI escape codes. Respects `NO_COLOR` environment variable (if set, output is monochrome).
- Falls back to monochrome when stdout is not a TTY (e.g., piped to a file).

**`--verbose` mode:**
- Shows all diagnostics (no truncation to 20).
- Includes `remediation` text for each diagnostic.
- Includes per-criterion `DimensionScore.details[]` breakdown.

**`--quiet` mode:**
- Suppresses all output. Only the exit code communicates the result. This is Tier 1 behavior without any terminal rendering.

**JSON output mode (`--output-format json`):**
- Instead of the terminal format above, serializes the `QualityScore` and `ValidationResult` as JSON to stdout. Uses Pydantic `.model_dump(mode="json")`.
- This is a minimal Tier 2 JSON renderer, not the full Stage 6 renderer. It provides enough machine-readable data for CI consumption.

**What this does NOT do:**
- Does not render Markdown, HTML, or YAML output — those require Stage 6 (v0.8.x). If the user requests these formats, the CLI warns and falls back to terminal or JSON.
- Does not render Tier 3 (Remediation Playbook) content — that requires v0.6.x.
- Does not render ecosystem-level output — that requires v0.7.x.

**Grounding:** RR-SPEC-v0.1.3-output-tier-specification.md §4.1 (Terminal format), v0.2.4d terminal formatter conventions.

---

### 3.2 v0.5.1 — Validation Profiles

**Goal:** Implement the `ValidationProfile` Pydantic model, define the 4 built-in profiles, and build the tag-based rule filtering engine. After this sub-version, users can run `docstratum validate --profile lint` and get profile-controlled behavior.

---

#### v0.5.1a — Profile Model Implementation

**What it does:** Implements the `ValidationProfile` Pydantic model from RR-SPEC-v0.1.3-validation-profiles.md §2.1 as runtime Python code.

**New Module:** `src/docstratum/schema/profile.py` (or `src/docstratum/profiles/model.py` — the design spec should decide on module location).

**Model Fields (from spec):**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `profile_name` | `str` | (required) | Unique human-readable identifier |
| `description` | `str` | (required) | Purpose and use case explanation |
| `max_validation_level` | `int` (0–4) | `4` | Highest L0–L4 level to execute |
| `enabled_stages` | `list[int]` | `[1, 2, 3, 4, 5]` | Pipeline stage IDs to run |
| `rule_tags_include` | `list[str]` | `[]` | Tags that activate rules (OR semantics) |
| `rule_tags_exclude` | `list[str]` | `[]` | Tags that deactivate rules (always wins) |
| `severity_overrides` | `dict[str, str]` | `{}` | DiagnosticCode → Severity mapping |
| `priority_overrides` | `dict[str, str]` | `{}` | DiagnosticCode → Priority mapping |
| `pass_threshold` | `int | None` | `None` | Minimum score (0–100) to pass |
| `output_tier` | `int` (1–4) | `2` | Output tier to produce |
| `output_format` | `str` | `"terminal"` | Serialization format |
| `grouping_mode` | `str` | `"by-priority"` | Remediation grouping strategy |
| `extends` | `str | None` | `None` | Base profile name for inheritance |

**Validation Rules (Pydantic validators):**

- `max_validation_level`: `ge=0, le=4`
- `enabled_stages`: min 1 item; each item `ge=1, le=6`
- `pass_threshold`: `ge=0, le=100` if not None
- `output_tier`: `ge=1, le=4`
- `output_format`: Lenient — accept any string; runtime validation warns on unknown formats (see §2.6)
- `grouping_mode`: Lenient — accept any string; runtime validation warns on unknown modes

**Spec Deviation Notes:**

The ASoT spec (RR-SPEC-v0.1.3 §2.1) defines `validate_format()` and `validate_grouping_mode()` as separate methods called from `__post_init_post_parse__`. The implementation should use Pydantic v2 `@model_validator(mode='after')` instead, because `__post_init_post_parse__` is a Pydantic v1 pattern. The design spec for v0.5.1a should confirm the Pydantic version in use (the project uses Python 3.11+ per `pyproject.toml`, and the existing models use Pydantic's `BaseModel`, `Field`, and `model_dump` — suggesting Pydantic v2).

**What this does NOT do:**
- Does not load profiles from disk — that's v0.5.2a.
- Does not resolve inheritance — that's v0.5.1d.
- Does not filter rules — that's v0.5.1c.

**Grounding:** RR-SPEC-v0.1.3-validation-profiles.md §2 (full model definition).

---

#### v0.5.1b — Built-in Profiles

**What it does:** Defines the 4 built-in profiles as `ValidationProfile` instances that ship with the package. These are the "factory presets" available without any configuration.

**Profile Definitions:**

| Profile | `max_level` | `enabled_stages` | `tags_include` | `tags_exclude` | `threshold` | `output_tier` | `output_format` | `extends` |
|---------|------------|-------------------|----------------|----------------|-------------|--------------|-----------------|-----------|
| **lint** | 1 | [1, 2] | ["structural"] | [] | None | 2 | terminal | None |
| **ci** | 3 | [1, 2, 3, 4, 5] | ["structural", "content", "ecosystem"] | ["experimental", "docstratum-extended"] | 50 | 1 | json | None |
| **full** | 4 | [1, 2, 3, 4, 5, 6] | [] | [] | None | 3 | markdown | None |
| **enterprise** | 4 | [1, 2, 3, 4, 5, 6] | [] | [] | None | 4 | html | full |

**Storage:** Built-in profiles are defined as Python code (factory functions or module-level constants), not as YAML files on disk. This ensures they are always available, cannot be accidentally deleted, and load without file I/O.

**Alternative approach:** Store as YAML files bundled with the package (e.g., `src/docstratum/profiles/builtins/lint.yaml`). This makes them editable and inspectable by users. The design spec for v0.5.1b should decide between Python constants and bundled YAML.

**Specific Profile Notes:**

- **lint:** Maximum speed. Stages 1–2 only (no ecosystem scan). L0–L1 only (parseable + structural). No score threshold — the developer cares about error presence, not a numeric score. Terminal output for rapid feedback.
- **ci:** The default profile when none is specified. Ecosystem-aware (stages 1–5) but excludes experimental and L4 rules. Threshold of 50 enforces a minimum quality bar. JSON output for machine parsing. This matches the v0.2.4d `validation.level: 3` behavior.
- **full:** Everything enabled. All levels, all stages (including Stage 6 when available), all tags. Markdown output for a rich, shareable report. No threshold — always produces output. This is the "show me everything" mode.
- **enterprise:** Extends `full`. Overrides `output_tier` to 4 (Audience-Adapted) and `output_format` to HTML. Tier 4 requires the context profile system and audience adaptation engine, which are deferred to v0.4.x+ per the output tier spec. At v0.5.x, the `enterprise` profile is defined but its Tier 4 rendering falls back to Tier 3 behavior with a warning.

**Grounding:** RR-SPEC-v0.1.3-validation-profiles.md §3 (4 built-in profiles).

---

#### v0.5.1c — Tag-Based Rule Filtering

**What it does:** Implements the "buffet" composition model — the decision logic that determines which diagnostic rules execute for a given profile.

**Rule-Execution Decision Tree:**

A rule executes if ALL of these conditions are true:

```
1. Tag inclusion:   (rule_tags_include == []) OR (rule.tags ∩ rule_tags_include ≠ ∅)
2. Tag exclusion:   NOT (rule.tags ∩ rule_tags_exclude ≠ ∅)
3. Level gating:    rule.validation_level <= max_validation_level
4. Stage gating:    rule.pipeline_stage in enabled_stages
```

**Semantic Details:**

- **OR semantics for inclusion (DECISION-030):** A rule is included if ANY of its tags matches ANY tag in `rule_tags_include`. "Enable structural AND content" means "enable rules tagged structural OR rules tagged content (or both)."
- **Exclusion always wins:** If a rule matches both an include tag and an exclude tag, it is excluded. This is the "experimental rule inside a structural category" safety net.
- **Empty include = include all:** An empty `rule_tags_include` list means no tag filtering — all rules pass the inclusion check (subject to exclusion and level/stage checks).
- **Level gating is a performance optimization:** Rules above `max_validation_level` are skipped entirely (not evaluated and reported as "skipped" — simply not instantiated). This saves time for the `lint` profile.
- **Stage gating is an orchestrator concern:** Stages not in `enabled_stages` don't run at all. The CLI (v0.5.0a) or orchestrator respects this before any rules execute.

**Implementation:**

The filtering engine is a pure function:

```python
def rule_executes(rule, profile: ValidationProfile) -> bool:
    """Determine whether a rule should run given a profile."""
    # 1. Tag inclusion
    tag_included = (
        not profile.rule_tags_include
        or bool(set(rule.tags) & set(profile.rule_tags_include))
    )
    # 2. Tag exclusion (always wins)
    tag_excluded = bool(set(rule.tags) & set(profile.rule_tags_exclude))
    # 3. Level gating
    level_ok = rule.validation_level <= profile.max_validation_level
    # 4. Stage gating
    stage_ok = rule.pipeline_stage in profile.enabled_stages
    return tag_included and not tag_excluded and level_ok and stage_ok
```

**Severity Override Application:**

After rule execution produces diagnostics, the filtering engine applies `severity_overrides`:

```python
for diagnostic in result.diagnostics:
    override = profile.severity_overrides.get(diagnostic.code.value)
    if override:
        diagnostic.severity = Severity(override)
```

This happens AFTER rule execution but BEFORE exit code computation (v0.5.0c), so that severity overrides affect the exit code.

**Priority Override Application:**

`priority_overrides` are stored on the profile but not consumed until the Remediation Framework (v0.6.x) assigns priorities. The filtering engine does not apply priority overrides — it only applies severity overrides.

**Fallback Without Rule Registry (see §2.3):**

If rules do not have `tags` attributes (Rule Registry not yet built), the filtering engine treats all rules as having an empty tag set. This means:
- `rule_tags_include=["structural"]` matches no rules (no rules have tags).
- `rule_tags_include=[]` matches all rules (empty include = include all).
- Level gating and stage gating still operate normally.

In practice, this means the `lint` profile (which uses `rule_tags_include=["structural"]`) would match no rules in bootstrap mode. To handle this, the fallback should treat empty-tag rules as matching all include lists. The design spec for v0.5.1c must define the exact fallback semantics.

**Grounding:** RR-SPEC-v0.1.3-validation-profiles.md §4 (Module Composition Semantics), DECISION-029 through DECISION-031.

---

#### v0.5.1d — Profile Inheritance

**What it does:** Implements the single-level `extends` field that allows a child profile to inherit from a base profile.

**Inheritance Rules:**

1. Load the base profile by name (using the discovery precedence chain from v0.5.2b).
2. Copy all fields from the base to the child.
3. For each field explicitly set in the child profile, override the base value.
4. The result is a resolved `ValidationProfile` with no `extends` reference (inheritance is flattened at load time).

**"Explicitly set" detection:**

The key challenge is distinguishing "the child explicitly set `max_validation_level=4`" from "the child didn't specify `max_validation_level`, so it defaulted to 4." Both produce the same value in the Pydantic model.

Two approaches:
1. **Track which fields were explicitly provided in the YAML/JSON source.** Compare the raw YAML keys against the model fields. Keys present in the source are "explicitly set"; absent keys inherit from the base.
2. **Use a sentinel value (e.g., `UNSET`).** Fields default to `UNSET` instead of their normal defaults. After loading, any field that is still `UNSET` inherits from the base.

The design spec for v0.5.1d should decide between these approaches. Option 1 is recommended because it keeps the Pydantic model clean (no sentinel values) and works naturally with YAML parsing.

**Restrictions:**

- **Single level only (DECISION-031):** If the base profile itself has `extends`, that's an error. No chaining: "enterprise" → "full" → "ci" is not allowed.
- **No circular inheritance:** If profile A extends B and profile B extends A, report an error at load time.
- **Base must exist:** If the base profile cannot be found via the discovery precedence chain, report a clear error with the search locations attempted.

**Grounding:** RR-SPEC-v0.1.3-validation-profiles.md §4.6 (Inheritance), DECISION-031.

---

### 3.3 v0.5.2 — Profile Discovery & Configuration

**Goal:** Implement the profile loading pipeline — from raw YAML/JSON on disk to a resolved, validated `ValidationProfile` instance injected into the `PipelineContext`. This sub-version handles file I/O, schema validation, discovery precedence, CLI override merging, and backward compatibility with the v0.2.4d configuration format.

---

#### v0.5.2a — Profile Loading

**What it does:** Loads a `ValidationProfile` from a YAML or JSON file, validates it against the schema, and returns a `ValidationProfile` instance.

**Supported File Formats:**

| Format | Extension | Parser |
|--------|-----------|--------|
| YAML | `.yaml`, `.yml` | `PyYAML` or `ruamel.yaml` |
| JSON | `.json` | `json` (stdlib) |

**Loading Steps:**

1. Read the file from disk.
2. Parse YAML or JSON based on file extension.
3. Construct a `ValidationProfile` from the parsed dictionary.
4. Run Pydantic validation (type checking, range constraints).
5. Run lenient runtime validation: warn on unknown `output_format`, warn on unknown `grouping_mode`, warn on unknown tags (if Rule Registry is available to check against).
6. If `extends` is set, resolve inheritance (v0.5.1d) — this requires calling back into the discovery chain (v0.5.2b) to find the base profile.
7. Return the resolved `ValidationProfile`.

**Error Handling:**

- File not found → `FileNotFoundError` with clear message.
- YAML/JSON parse error → `ValueError` with line number context (if available).
- Pydantic validation error → `ValueError` with field-level error messages.
- Inheritance error → `ValueError` with explanation (base not found, circular, etc.).

**Embedded Profile Loading:**

In addition to standalone files, profiles can be embedded in `.docstratum.yml` under a `profiles:` key. The loader handles both formats:

```yaml
# Standalone file (lint.yaml)
profile_name: "lint"
max_validation_level: 1
...

# Embedded in .docstratum.yml
profiles:
  lint:
    description: "Quick check"
    max_validation_level: 1
    ...
```

When loading from `.docstratum.yml`, the loader extracts the named profile's dictionary from the `profiles:` section and constructs a `ValidationProfile`. The `profile_name` is inferred from the dictionary key if not explicitly provided.

**Grounding:** RR-SPEC-v0.1.3-validation-profiles.md §5.3 (Profile File Formats), §5.4 (Embedded Profiles).

---

#### v0.5.2b — Discovery Precedence

**What it does:** Implements the profile discovery chain — the four-source lookup that resolves a profile name or path to a `ValidationProfile` instance.

**Precedence Order (highest to lowest):**

| Priority | Source | Trigger | Example |
|----------|--------|---------|---------|
| 1 | **CLI flag** | `--profile <path-or-name>` | `--profile ./custom.yaml` or `--profile lint` |
| 2 | **Project config** | `.docstratum.yml` `profiles:` section | `.docstratum.yml → profiles.lint` |
| 3 | **User config** | `~/.docstratum/profiles/` directory | `~/.docstratum/profiles/lint.yaml` |
| 4 | **Built-in** | Package-bundled profiles | "lint", "ci", "full", "enterprise" |

**Resolution Algorithm:**

```
Input: profile_spec (str | None)
Output: ValidationProfile

1. If profile_spec is None:
   a. Check .docstratum.yml for default_profile key → use that name
   b. If no default_profile → use "ci"
   c. Proceed to step 2 with the resolved name

2. If profile_spec ends with .yaml/.yml/.json:
   a. Treat as file path
   b. Load from file (v0.5.2a) → return
   c. If file not found → error

3. If profile_spec is a name (no file extension):
   a. Check .docstratum.yml → profiles.{name} → return if found
   b. Check ~/.docstratum/profiles/{name}.yaml → return if found
   c. Check ~/.docstratum/profiles/{name}.json → return if found
   d. Check built-in profiles → return if found
   e. If not found in any source → error with all locations tried
```

**Default Profile:**

When no `--profile` flag is provided and no `.docstratum.yml` exists (or it has no `default_profile` key), the CLI uses `"ci"` as the default. This matches the most common use case: a CI system running validation without explicit configuration.

The default can be overridden in `.docstratum.yml`:

```yaml
default_profile: "full"
```

**Error Messages:**

When a profile is not found, the error message lists all locations searched:

```
Error: Profile 'ecosystem-strict' not found.
Searched:
  1. CLI flag: not a file path
  2. .docstratum.yml: no 'profiles' section (file not found)
  3. ~/.docstratum/profiles/ecosystem-strict.yaml: file not found
  4. ~/.docstratum/profiles/ecosystem-strict.json: file not found
  5. Built-in profiles: not one of [lint, ci, full, enterprise]
```

**Grounding:** RR-SPEC-v0.1.3-validation-profiles.md §5.1 (Discovery Order), §5.2 (Default Profile).

---

#### v0.5.2c — CLI Override Integration

**What it does:** Merges CLI flag values into the loaded profile, applying shallow field-level overrides (DECISION-032).

**Override Logic:**

1. Load the profile (from v0.5.2b — may be built-in, project, user, or CLI-specified).
2. For each CLI flag that was explicitly provided (not `None`):
   - Override the corresponding profile field.
3. Return the merged profile.

**Override Mapping:**

| CLI Flag | Profile Field | Merge Behavior |
|----------|--------------|----------------|
| `--max-level` | `max_validation_level` | Replace |
| `--tags` | `rule_tags_include` | Replace (not append) |
| `--exclude-tags` | `rule_tags_exclude` | Replace (not append) |
| `--output-tier` | `output_tier` | Replace |
| `--output-format` | `output_format` | Replace |
| `--pass-threshold` | `pass_threshold` | Replace |

**"Replace" semantics:** CLI flags fully replace the profile's value, not merge with it. `--tags structural` on a profile that has `rule_tags_include=["structural", "content", "ecosystem"]` results in `rule_tags_include=["structural"]`, not `["structural", "content", "ecosystem", "structural"]`.

**Inline profiles:** If no `--profile` flag is provided but other CLI flags are specified, the CLI constructs an "inline profile" by loading the default profile and applying overrides. This is the "anonymous profile" concept from the spec:

```bash
# This creates an inline profile: default "ci" + overrides
docstratum validate llms.txt --max-level 2 --output-format markdown
```

**What this does NOT do:**
- Does not support deep merging of dictionaries (DECISION-032). You cannot override a single entry in `severity_overrides` from the CLI. For complex overrides, write a profile file.

**Grounding:** RR-SPEC-v0.1.3-validation-profiles.md §5.5 (CLI Flag Composition), DECISION-032.

---

#### v0.5.2d — Legacy Format Migration

**What it does:** Auto-detects and converts the legacy v0.2.4d `.docstratum.yml` configuration format to a `ValidationProfile`.

**Legacy Format (v0.2.4d):**

```yaml
validation:
  level: 3
  check_urls: true
output:
  format: terminal
  verbose: false
```

**Detection Logic:**

A `.docstratum.yml` file is legacy if it contains a `validation:` key but no `profiles:` key. If both are present, the `profiles:` section takes precedence and the legacy keys are ignored with a deprecation warning.

**Migration Mapping:**

| Legacy Field | Profile Field | Mapping |
|-------------|--------------|---------|
| `validation.level` = 0 or 1 | `profile_name` | "lint" |
| `validation.level` = 2 or 3 | `profile_name` | "ci" |
| `validation.level` = 4 | `profile_name` | "full" |
| `validation.check_urls` | — | If `false`, adds `"url-reachability"` to `rule_tags_exclude` |
| `output.format` | `output_format` | Direct mapping ("terminal", "json", "markdown", "html") |
| `output.verbose` | — | Stored as CLI context (not a profile field) |

**User Warning:**

When legacy format is detected, the CLI emits a deprecation warning:

```
Warning: .docstratum.yml uses deprecated config format (v0.2.4d).
Equivalent profile: "ci" (validation.level=3).
Update to the new format:
  default_profile: "ci"
  profiles:
    ci:
      max_validation_level: 3
      ...
See: https://docstratum.readthedocs.io/profiles/
```

**What this does NOT do:**
- Does not modify the user's `.docstratum.yml` file. Migration is runtime-only (read the old format, use the equivalent profile). Automatic file rewriting is too invasive.
- Does not handle edge cases where legacy and new formats are mixed in unexpected ways. The design spec for v0.5.2d should define behavior for ambiguous cases.

**Grounding:** RR-SPEC-v0.1.3-validation-profiles.md §8 (Backward Compatibility).

---

## 4. Dependency Map

```
v0.5.0 (CLI Foundation) ─── greenfield construction, no profile awareness
    │
    ├── v0.5.0a (Entry Point)       [no dependencies — creates pyproject.toml entry + cli.py]
    │       ↓
    ├── v0.5.0b (Argument Parsing)  [depends on v0.5.0a — needs command structure]
    │       ↓
    ├── v0.5.0c (Exit Codes)        [depends on v0.5.0b — needs parsed arguments]
    │       ↕
    └── v0.5.0d (Terminal Output)   [depends on v0.5.0b — needs parsed arguments]
              │                      v0.5.0c and v0.5.0d are co-dependent:
              │                      exit codes inform terminal display, terminal
              │                      display renders the score that determines exit code
              │
              ▼ (basic CLI operational)
v0.5.1 (Validation Profiles) ─── profile-aware pipeline
    │
    ├── v0.5.1a (Profile Model)      [no internal dependencies — pure Pydantic model]
    │       ↓
    ├── v0.5.1b (Built-in Profiles)  [depends on v0.5.1a — needs ValidationProfile class]
    │       ↕
    ├── v0.5.1c (Tag Filtering)      [depends on v0.5.1a — needs profile fields to filter on]
    │       ↕                         (can be developed in parallel with v0.5.1b)
    └── v0.5.1d (Inheritance)        [depends on v0.5.1a — needs model for field resolution]
              │                       (also needs v0.5.2b for base profile lookup, creating
              │                        a cross-version dependency)
              │
              ▼ (profiles defined and filterable)
v0.5.2 (Discovery & Configuration)
    │
    ├── v0.5.2a (Profile Loading)    [depends on v0.5.1a — needs model to validate against]
    │       ↓
    ├── v0.5.2b (Discovery Chain)    [depends on v0.5.2a + v0.5.1b — needs loading + built-ins]
    │       ↓
    ├── v0.5.2c (CLI Overrides)      [depends on v0.5.0b + v0.5.2b — needs parsed args + loaded profile]
    │       ↓
    └── v0.5.2d (Legacy Migration)   [depends on v0.5.2a — needs profile loading infrastructure]
              │
              ▼ (full profile system operational)
     → Feeds into v0.6.x (Remediation Framework consumes profile.priority_overrides)
     → Feeds into v0.7.x (Ecosystem pipeline wired into CLI dispatch)
     → Feeds into v0.8.x (Stage 6 reads profile.output_tier, output_format, grouping_mode)
```

**Parallelization Opportunities:**

- v0.5.0c and v0.5.0d can be developed simultaneously (they're co-dependent but address different concerns).
- v0.5.1b, v0.5.1c, and v0.5.1d can be developed in parallel once v0.5.1a is complete.
- v0.5.2d (Legacy Migration) is independent of v0.5.2b and v0.5.2c and can be developed in parallel.

**Cross-Version Dependency:**

v0.5.1d (Profile Inheritance) depends on v0.5.2b (Discovery Precedence) to resolve the base profile name. This creates a circular dependency between v0.5.1 and v0.5.2. The recommended resolution: implement inheritance resolution as a callback injected by the discovery chain, allowing v0.5.1d to define the inheritance logic without hardcoding the lookup mechanism.

**External Dependencies:**

- v0.3.x must be operational (producing `ValidationResult`) for the CLI to validate files.
- v0.4.x must be operational (producing `QualityScore`) for the CLI to display scores, enforce thresholds, and compute exit codes.
- The **Rule Registry** (Deliverable 3) is a soft dependency. Tag-based filtering (v0.5.1c) degrades gracefully without it (see §2.3).
- **PyYAML** (or `ruamel.yaml`) is required for YAML profile loading. The design spec for v0.5.2a should confirm which YAML library to use and whether it's already a project dependency.

---

## 5. Models Consumed (Not Modified)

| Model | Source Module | CLI/Profile's Role | Notes |
|-------|-------------|-------------------|-------|
| `ValidationResult` | `schema/validation.py` | Reads `diagnostics[]`, `level_achieved`, `levels_passed{}`, `total_errors`, `total_warnings` for exit code computation and terminal display | |
| `ValidationDiagnostic` | `schema/validation.py` | Reads `code`, `severity`, `message`, `remediation`, `line_number`, `context`, `level` for terminal diagnostic listing. Applies `severity_overrides` by mutating `severity` field. | Only field the CLI writes to on an existing model |
| `QualityScore` | `schema/quality.py` | Reads `total_score`, `grade`, `dimensions{}` for terminal display and threshold comparison | |
| `QualityGrade` | `schema/quality.py` | Reads grade value for colorized display | |
| `DimensionScore` | `schema/quality.py` | Reads `points`, `max_points`, `details[]` for dimension breakdown display | |
| `DiagnosticCode` | `schema/diagnostics.py` | References code values for severity override lookup | |
| `Severity` | `schema/diagnostics.py` | Constructs from override strings to apply severity overrides | |
| `ValidationLevel` | `schema/validation.py` | Reads level for exit code priority logic and level gating | |
| `DocumentClassification` | `schema/classification.py` | Read by the pipeline (not directly by CLI) during validation | |

**New Model Created:**

| Model | Module | Purpose |
|-------|--------|---------|
| `ValidationProfile` | `schema/profile.py` (new) | The profile configuration model — the primary artifact of v0.5.x |

**PipelineContext Extension:**

| Field Added | Type | Purpose |
|-------------|------|---------|
| `profile` | `ValidationProfile | None` | Injected by the CLI before pipeline execution. Read by stages for filtering. |

> **Severity Override Mutability Note:** The CLI applies severity overrides by mutating `ValidationDiagnostic.severity` in-place (see v0.5.1c). This is the one case where the CLI modifies a model created by a prior phase. The mutation happens after all validation checks have completed — it does not affect check evaluation, only the reported severity. The design spec for v0.5.1c should confirm this is acceptable or propose an immutable alternative (e.g., a `displayed_severity` field).

---

## 6. Exit Criteria

v0.5.x is complete when:

- [ ] `docstratum validate <file>` can be run from the terminal and produces a score, grade, and diagnostic listing.
- [ ] `python -m docstratum validate <file>` works identically to the console script.
- [ ] `docstratum --version` prints the engine version.
- [ ] All CLI arguments from §3.1 (v0.5.0b) are parsed without error.
- [ ] Exit codes 0, 1, 2, 5, and 10 are emitted for the correct conditions (codes 3 and 4 are architecturally defined but may not be exercisable until v0.7.x).
- [ ] Terminal output includes: header (version, profile, timestamp), score/grade, level checklist, dimension breakdown, diagnostic summary counts, and sorted diagnostic listing.
- [ ] `--quiet` suppresses all terminal output.
- [ ] `--verbose` shows all diagnostics with remediation text.
- [ ] `--output-format json` serializes the result as JSON to stdout.
- [ ] The `ValidationProfile` Pydantic model is implemented with all 13 fields from §3.2 (v0.5.1a).
- [ ] All 4 built-in profiles (lint, ci, full, enterprise) are defined and loadable by name.
- [ ] `--profile lint` restricts validation to L0–L1 structural checks.
- [ ] `--profile ci` runs L0–L3 with a score threshold of 50.
- [ ] `--profile full` runs all levels with no threshold.
- [ ] Tag-based rule filtering correctly applies OR semantics for inclusion and exclusion-always-wins.
- [ ] Level gating (`max_validation_level`) prevents higher-level checks from executing.
- [ ] Stage gating (`enabled_stages`) prevents unlisted stages from executing.
- [ ] Severity overrides modify diagnostic severity before exit code computation.
- [ ] Single-level profile inheritance works: `enterprise` extends `full` with overrides.
- [ ] Circular and multi-level inheritance are detected and reported as errors.
- [ ] Profile loading works from: CLI file path, `.docstratum.yml` `profiles:` section, `~/.docstratum/profiles/` directory, and built-in.
- [ ] Discovery precedence is correct: CLI > project > user > built-in.
- [ ] CLI flag overrides (`--max-level`, `--tags`, etc.) correctly override loaded profile fields.
- [ ] Legacy v0.2.4d `.docstratum.yml` format is auto-detected and migrated with a deprecation warning.
- [ ] Unknown output formats and grouping modes produce warnings, not errors (lenient validation).
- [ ] Output format fallback works: requesting "markdown" or "html" at v0.5.x produces a warning and falls back to terminal or JSON.
- [ ] `pytest --cov=docstratum.cli --cov-fail-under=85` passes.
- [ ] `black --check` and `ruff check` pass on all new code.
- [ ] No new fields have been added to any pre-existing Pydantic model without a documented amendment (the new `PipelineContext.profile` field IS a documented amendment per RR-SPEC-v0.1.3 §6.1).

---

## 7. What Comes Next

The CLI and profile system are the user-facing gateway. Their output shapes the experience for every subsequent phase:

- **v0.6.x (Remediation Framework):** Reads `profile.priority_overrides` to adjust remediation priority for diagnostics. The CLI's terminal output may be extended to display Tier 3 action items once the remediation framework produces them. The `grouping_mode` field (stored on the profile since v0.5.x) is consumed by the remediation framework's grouping logic.

- **v0.7.x (Ecosystem Integration):** Wires the ecosystem pipeline into the CLI's dispatch logic. When the user passes a directory argument (`docstratum validate ./docs/`), the CLI invokes the full 5-stage ecosystem pipeline instead of single-file validation. Exit code 4 (ecosystem errors) becomes exercisable. Profiles with `enabled_stages=[1, 2, 3, 4, 5]` trigger the ecosystem path.

- **v0.8.x (Report Generation):** Implements Stage 6, which reads `profile.output_tier`, `profile.output_format`, and `profile.grouping_mode` to render the appropriate report. Formats "markdown", "yaml", and "html" become functional (currently they produce a fallback warning). The `full` profile's Tier 3 Markdown output and the `enterprise` profile's Tier 4 HTML output become fully operational.

- **v0.9.0 (Extended Validation):** Activates L4 checks. The `full` and `enterprise` profiles (which set `max_validation_level=4`) automatically start running L4 rules. The `ci` profile (L0–L3) remains unaffected. Tags like `"docstratum-extended"` (excluded by `ci`) become populated with L4-specific rules.
