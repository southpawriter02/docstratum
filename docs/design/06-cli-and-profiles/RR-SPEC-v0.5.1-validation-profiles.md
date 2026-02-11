# v0.5.1 — Validation Profiles

> **Version:** v0.5.1
> **Document Type:** Parent Design Specification (Validation Profiles)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SCOPE-v0.5.x-cli-and-profiles.md](RR-SCOPE-v0.5.x-cli-and-profiles.md)
> **Governing Specs:** RR-SPEC-v0.1.3-validation-profiles.md §2–§4, RR-SPEC-v0.1.3-output-tier-specification.md §4.2
> **Depends On:** v0.5.0 (CLI Foundation: `cli.py`, `cli_args.py`, `cli_exit_codes.py`, `cli_output.py`), v0.4.x (`QualityScore`, `QualityGrade`, `DimensionScore`), v0.3.x (`ValidationResult`, `ValidationDiagnostic`), v0.1.2a (`DiagnosticCode`, `Severity`)
> **Consumed By:** v0.5.2 (Profile Discovery & Configuration), v0.6.x (Remediation Framework), v0.7.x (Ecosystem Integration), v0.8.x (Report Generation)

---

## 1. Purpose

v0.5.1 builds the **Validation Profile system** — the `ValidationProfile` Pydantic model, the four built-in profile presets, the tag-based rule filtering engine, and single-level profile inheritance. After v0.5.1, the command-line interface built in v0.5.0 evolves from a hardcoded-defaults tool into a profile-aware validation engine: a user can run `docstratum validate --profile lint` and get behavior that differs meaningfully from `--profile full`.

Before v0.5.1, the CLI uses `CLI_DEFAULTS` — a hardcoded dictionary in `cli.py` that mirrors the `ci` profile. Every invocation behaves identically regardless of the `--profile` flag (which is parsed by v0.5.0b but not consumed). v0.5.1 replaces `CLI_DEFAULTS` with a loaded `ValidationProfile` instance, and introduces the filtering engine that makes each profile produce different validation behavior.

### 1.1 What v0.5.1 Is

A **profile definition and filtering layer** that:

1. **Defines the model** (`ValidationProfile`) — a 13-field Pydantic model capturing every configurable aspect of a validation run (levels, stages, tags, thresholds, output, inheritance).
2. **Ships 4 presets** (lint, ci, full, enterprise) — built-in profiles available without any YAML files on disk.
3. **Filters rules** — a pure-function engine that evaluates each diagnostic rule against the active profile's tags, level, and stage constraints.
4. **Resolves inheritance** — the `extends` field that allows a child profile to inherit from a base, flattened at load time with single-level restriction.

### 1.2 What v0.5.1 Is NOT

| Not This | Why | Where It Lives |
|----------|-----|----------------|
| Profile loading from disk | File I/O, YAML/JSON parsing, schema validation against files | v0.5.2a |
| Profile discovery precedence | CLI > project > user > built-in lookup chain | v0.5.2b |
| CLI override merging | Merging CLI flags into loaded profiles | v0.5.2c |
| Legacy format migration | Auto-detecting v0.2.4d config and converting | v0.5.2d |
| Executing validation checks | The profile says *which* checks to run; the validator (v0.3.x) runs them | v0.3.x |
| Computing quality scores | The scorer (v0.4.x) computes scores; the profile sets the pass threshold | v0.4.x |
| Rendering reports | Stage 6 consumes `output_tier`, `output_format`, `grouping_mode` | v0.8.x |

### 1.3 User Stories

> **US-1:** As a developer, I want to run `docstratum validate --profile lint` and have only L0–L1 structural checks execute, so that I get fast feedback during editing without waiting for content or ecosystem analysis.

> **US-2:** As a CI pipeline maintainer, I want a `ci` profile that enforces a minimum score threshold of 50 and outputs JSON, so that I can gate pull request merges on documentation quality with machine-parseable results.

> **US-3:** As a documentation team lead, I want a `full` profile that runs all checks at all levels and produces a comprehensive report, so that I can audit the complete quality of our llms.txt before release.

> **US-4:** As a team with custom needs, I want to create a profile that extends `full` with modified output settings, so that I don't have to duplicate the entire `full` configuration.

> **US-5:** As a developer whose project doesn't yet have a Rule Registry, I want the profile system to degrade gracefully — still operating on level and stage gating — rather than crashing on missing tag metadata.

---

## 2. Architecture

### 2.1 Module Map

```
src/docstratum/
├── profiles/                          ← NEW package
│   ├── __init__.py                    ← Package init, re-exports
│   ├── model.py                       ← ValidationProfile Pydantic model [v0.5.1a]
│   ├── builtins.py                    ← 4 built-in profile instances [v0.5.1b]
│   ├── filtering.py                   ← Tag-based rule filtering engine [v0.5.1c]
│   └── inheritance.py                 ← Profile inheritance resolver [v0.5.1d]
│
├── cli.py                             ← MODIFIED: replaces CLI_DEFAULTS with profile
├── cli_args.py                        ← READ: CliArgs parsed by v0.5.0b
├── cli_exit_codes.py                  ← READ: exit code mapper uses filtered result
├── cli_output.py                      ← READ: terminal output uses profile name
│
├── schema/
│   ├── validation.py                  ← ValidationResult, ValidationDiagnostic (READ)
│   ├── quality.py                     ← QualityScore, QualityGrade (READ)
│   ├── diagnostics.py                 ← DiagnosticCode, Severity (READ)
│   └── ...
├── pipeline/
│   └── stages.py                      ← PipelineContext (WRITE .profile field)
└── __init__.py                        ← __version__ (READ)
```

### 2.2 Module Placement Decision

**DECISION-034: Profiles as a separate package (`src/docstratum/profiles/`), not a single schema file.**

**Rationale:**
1. The profile system has four distinct concerns (model, presets, filtering, inheritance) — a single-file approach would produce a 400+ line monolith.
2. A `profiles/` package allows clean import boundaries: `from docstratum.profiles import ValidationProfile, get_builtin_profile, rule_executes`.
3. Future expansion (v0.5.2 adds loading, discovery, CLI overrides) fits naturally as additional modules in the same package.
4. The `schema/` directory is reserved for data models consumed across the pipeline — `ValidationProfile` is an input configuration model, not a pipeline data model.

**Alternative considered:** `src/docstratum/schema/profile.py` (the SCOPE file's suggestion). Rejected because the profile system is more than a schema — it includes business logic (filtering, inheritance) that doesn't belong in the schema package.

### 2.3 Data Flow

```
┌─────────────────────────────────────┐
│ v0.5.0b: CliArgs                     │  Parsed CLI arguments
│   args.profile = "lint"              │  (or None for default)
│   args.max_level = None (not set)    │
│   args.tags = None (not set)         │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ v0.5.1b: Built-in Profile Lookup     │  builtins.py
│   get_builtin_profile("lint")        │
│   → ValidationProfile(              │
│       profile_name="lint",           │
│       max_validation_level=1,        │
│       enabled_stages=[1, 2],         │
│       rule_tags_include=["structural"]│
│     )                                │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ v0.5.1d: Inheritance Resolution      │  inheritance.py
│   (if extends is set, resolve)       │
│   enterprise → full + overrides      │
│   → Flattened ValidationProfile      │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ PipelineContext.profile =            │  Injected before pipeline runs
│   resolved ValidationProfile         │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ v0.5.1c: Rule Filtering Engine       │  filtering.py
│   for each rule in pipeline:         │
│     if rule_executes(rule, profile): │
│       execute(rule)                  │
│   for each diagnostic:              │
│     apply_severity_overrides(        │
│       diagnostic, profile)           │
└─────────────────────────────────────┘
                │
                ▼
         Pipeline continues to
         exit code (v0.5.0c) and
         terminal output (v0.5.0d)
```

### 2.4 Integration with v0.5.0

v0.5.1 modifies the `validate_command()` in `cli.py` to replace the `CLI_DEFAULTS` dictionary with a profile-driven configuration path:

```python
# BEFORE (v0.5.0):
defaults = CLI_DEFAULTS  # Hardcoded dict
max_level = args.max_level or defaults["max_validation_level"]

# AFTER (v0.5.1):
from docstratum.profiles import get_builtin_profile

profile = get_builtin_profile(args.profile or "ci")
# v0.5.2 replaces this with the full discovery chain
```

The `CLI_DEFAULTS` dictionary is preserved as a fallback for the case where no profile can be loaded (should never happen with built-ins, but defensive). The `validate_command()` function signature does not change — it still receives `CliArgs` from v0.5.0b.

### 2.5 PipelineContext Extension

A new `profile` field is added to `PipelineContext`:

```python
# In pipeline/stages.py (or pipeline/context.py)
class PipelineContext(BaseModel):
    """Runtime context for the validation pipeline."""
    # ... existing fields ...
    profile: Optional["ValidationProfile"] = None
    # Grounding: RR-SPEC-v0.1.3-validation-profiles.md §6.1
```

This is the **only modification** to a pre-existing model in v0.5.1. It is a documented amendment per RR-SPEC-v0.1.3 §6.1.

---

## 3. Sub-Part Breakdown

### 3.1 v0.5.1a — Profile Model Implementation

**Module:** `profiles/model.py`
**What it does:** Implements the `ValidationProfile` Pydantic v2 model with all 13 fields, validation rules, and lenient runtime validation for forward-compatible fields.
**Design Spec:** [RR-SPEC-v0.5.1a-profile-model.md](RR-SPEC-v0.5.1a-profile-model.md)

---

### 3.2 v0.5.1b — Built-in Profiles

**Module:** `profiles/builtins.py`
**What it does:** Defines the 4 built-in profiles (lint, ci, full, enterprise) as Python constants. Provides `get_builtin_profile(name)` and `list_builtin_profiles()` functions.
**Design Spec:** [RR-SPEC-v0.5.1b-built-in-profiles.md](RR-SPEC-v0.5.1b-built-in-profiles.md)

---

### 3.3 v0.5.1c — Tag-Based Rule Filtering

**Module:** `profiles/filtering.py`
**What it does:** Implements the "buffet" composition model — `rule_executes()` decision function and `apply_severity_overrides()` post-execution step. Includes Rule Registry fallback behavior.
**Design Spec:** [RR-SPEC-v0.5.1c-tag-filtering.md](RR-SPEC-v0.5.1c-tag-filtering.md)

---

### 3.4 v0.5.1d — Profile Inheritance

**Module:** `profiles/inheritance.py`
**What it does:** Resolves the single-level `extends` field by loading the base profile, comparing explicitly-set child fields against defaults, and producing a flattened `ValidationProfile`.
**Design Spec:** [RR-SPEC-v0.5.1d-profile-inheritance.md](RR-SPEC-v0.5.1d-profile-inheritance.md)

---

## 4. Dependency Chain

```
v0.5.1a (Profile Model)          ← no internal dependencies, pure Pydantic model
    │
    ├───────────┬───────────┐
    ▼           ▼           ▼
v0.5.1b      v0.5.1c      v0.5.1d
(Built-in    (Tag          (Inheritance)
 Profiles)    Filtering)
    │           │           │
    │           │           ├── Needs v0.5.2b for base profile lookup
    │           │           │   (resolved via callback injection)
    │           │           │
    └───────────┴───────────┘
                │
                ▼ (profiles defined, filterable, inheritable)
         v0.5.2 (Discovery & Configuration)
              Consumes v0.5.1a–d to load, discover,
              and merge profiles at runtime
```

**Parallelization:** v0.5.1b, v0.5.1c, and v0.5.1d can all be developed simultaneously once v0.5.1a is complete. They have no dependencies on each other.

**Cross-Version Dependency:** v0.5.1d (Inheritance) needs to look up the base profile by name, which requires the discovery chain (v0.5.2b). This is resolved by injecting a `profile_resolver` callback:

```python
# profiles/inheritance.py
def resolve_inheritance(
    child: ValidationProfile,
    profile_resolver: Callable[[str], ValidationProfile],
    source_keys: set[str] | None = None,
) -> ValidationProfile:
    """Resolve single-level inheritance.

    Args:
        child: The child profile with an `extends` reference.
        profile_resolver: Callback that resolves a profile name
            to a ValidationProfile. Injected by v0.5.2b.
        source_keys: Keys explicitly set in the child's source file.
            Used to distinguish "explicitly set to default" from "inherited".
    """
```

At v0.5.1, the `profile_resolver` is a simple built-in lookup (`get_builtin_profile`). At v0.5.2b, it's replaced with the full discovery chain.

**External Dependencies:**
- v0.3.x operational → `ValidationResult` for filtering to produce observable effects
- v0.4.x operational → `QualityScore` for threshold comparison
- **Rule Registry** (Deliverable 3) → soft dependency for tag filtering; degrades gracefully without it (see §5.1)
- **Pydantic v2** → already a project dependency per `pyproject.toml`

---

## 5. Key Design Decisions

### 5.1 Rule Registry Fallback (from SCOPE §2.3)

The tag-based filtering model depends on rules having `tags` attributes. Without the Rule Registry, rules have no tags.

**Fallback semantics (DECISION-035):**

| Scenario | Rule has tags? | `rule_tags_include` | Behavior |
|----------|----------------|---------------------|----------|
| Normal mode | Yes | `["structural"]` | Include only rules tagged "structural" |
| Normal mode | Yes | `[]` (empty) | Include all rules (no tag filter) |
| Bootstrap mode | No (empty tags) | `["structural"]` | **Include all rules** (fallback) |
| Bootstrap mode | No (empty tags) | `[]` (empty) | Include all rules |

The key fallback rule: **If a rule has no tags (empty tag set), it is treated as matching all include lists.** This prevents the `lint` profile from matching zero rules when the Rule Registry hasn't been built yet. Tag exclusion still operates — rules with empty tags never match an exclusion list (there are no tags to match against).

This fallback is logged as a `WARNING`:

```
WARNING: Rule 'E001' has no tags. Tag filtering is operating in bootstrap mode
(Rule Registry not available). All rules pass inclusion checks.
```

The warning is emitted **once per run** (not per rule) to avoid log spam.

### 5.2 Pydantic Version Confirmation

The project uses **Pydantic v2** (confirmed by existing `BaseModel`, `Field`, `model_dump` usage in `schema/` modules). The `ValidationProfile` model uses Pydantic v2 patterns:

- `@model_validator(mode='after')` instead of `__post_init_post_parse__`
- `Field(ge=0, le=4)` instead of separate validator methods
- `model_dump(mode="json")` for serialization
- `ConfigDict(frozen=True)` for immutability (optional — see v0.5.1a)

### 5.3 Output Format/Tier Compatibility Matrix

From RR-SPEC-v0.1.3-output-tier-specification.md §4.2, the profile model validates format-tier pairings at construction time:

| Tier \ Format | terminal | json | markdown | yaml | html |
|--------------|----------|------|----------|------|------|
| **1 (Summary)** | ✓ | ✓ | ✗ | ✗ | ✗ |
| **2 (Diagnostic)** | ✓ | ✓ | ✓ | ✓ | ✓ |
| **3 (Remediation)** | ✓ | ✓ | ✓ | ✗ | ✓ |
| **4 (Audience)** | ✗ | ✓ | ✓ | ✗ | ✓ |

Invalid combinations produce a **warning** (not an error), preserving lenient validation:

```
Warning: output_tier=1 + output_format='markdown' is not a supported combination.
Tier 1 (Summary) supports: terminal, json.
Falling back to 'terminal' output.
```

### 5.4 Severity Override Mutability

The SCOPE file (§5, severity override note) raises the question of whether `ValidationDiagnostic.severity` should be mutated in-place or whether a separate `displayed_severity` field should be used.

**DECISION-036: Mutate `severity` in-place, but only after all checks complete.**

**Rationale:**
1. A `displayed_severity` field would require changes to every downstream consumer (exit codes, terminal output, future report renderers) — they'd need to check `displayed_severity or severity`.
2. In-place mutation is safe because severity overrides are applied AFTER validation execution. The override does not affect whether a check runs or what it evaluates — it only changes the reported severity.
3. The mutation point is well-defined: `apply_severity_overrides()` runs exactly once, between rule execution and exit code computation.

**Guard:** The `apply_severity_overrides()` function logs each override for auditability:

```
INFO: Severity override applied: E006 WARNING → ERROR (per profile 'strict-ci')
```

---

## 6. Models

### 6.1 New Models Created

| Model | Module | Purpose |
|-------|--------|---------|
| `ValidationProfile` | `profiles/model.py` | 13-field Pydantic model — the central configuration artifact of v0.5.x |

### 6.2 Models Consumed (Not Modified)

| Model | Source | Read Fields | Purpose |
|-------|--------|-------------|---------|
| `ValidationResult` | `schema/validation.py` | `diagnostics`, `level_achieved`, `levels_passed` | Filtering reads diagnostics for severity overrides |
| `ValidationDiagnostic` | `schema/validation.py` | `code`, `severity`, `level` | Severity override target; level for level gating |
| `QualityScore` | `schema/quality.py` | `total_score` | Compared against `pass_threshold` |
| `DiagnosticCode` | `schema/diagnostics.py` | Code values | Severity override lookup key |
| `Severity` | `schema/diagnostics.py` | Enum values | Constructed from override strings |

### 6.3 Models Modified

| Model | Module | Field Added | Type | Purpose |
|-------|--------|-------------|------|---------|
| `PipelineContext` | `pipeline/stages.py` | `profile` | `ValidationProfile | None` | Carries the resolved profile through the pipeline |

---

## 7. Inline Documentation Requirements

All new modules in the `profiles/` package MUST include:

1. **Module docstring** — citing the spec version (e.g., `"""Implements v0.5.1a — Profile Model."""`)
2. **Function/method docstrings** — Google-style with Args, Returns, Raises, and Example sections
3. **Version traces** — `# Implements v0.5.1a` on key functions/classes
4. **Grounding comments** — `# Grounding: RR-SPEC-v0.1.3-validation-profiles.md §2.1` on design-critical logic
5. **Decision references** — `# DECISION-034: Profiles as separate package` on structural choices
6. **Type annotations** — Complete type hints on all public and private functions

---

## 8. Changelog Requirements

Upon completion of v0.5.1 (all 4 sub-parts), a changelog entry is required:

```markdown
## [0.5.1] — 2026-XX-XX

### Added
- `ValidationProfile` Pydantic v2 model with 13 configurable fields (v0.5.1a)
- Lenient runtime validation: unknown output formats and grouping modes produce
  warnings, not errors (v0.5.1a)
- Format-tier compatibility matrix validation with actionable warnings (v0.5.1a)
- 4 built-in profiles: lint (fast L0–L1), ci (default, threshold=50, JSON),
  full (all levels, Markdown), enterprise (extends full, Tier 4, HTML) (v0.5.1b)
- `get_builtin_profile()` and `list_builtin_profiles()` API (v0.5.1b)
- Tag-based rule filtering engine with OR-inclusion, exclusion-always-wins,
  level gating, and stage gating (v0.5.1c)
- Rule Registry bootstrap fallback: tagless rules pass all inclusion checks (v0.5.1c)
- Severity override application with audit logging (v0.5.1c)
- Single-level profile inheritance via `extends` field (v0.5.1d)
- Circular and multi-level inheritance detection with clear error messages (v0.5.1d)
- `PipelineContext.profile` field for profile-aware pipeline execution (v0.5.1)

### Changed
- `validate_command()` in `cli.py` now uses profile-driven configuration instead
  of `CLI_DEFAULTS` dictionary (v0.5.1)

### Decisions
- DECISION-034: Profiles implemented as `src/docstratum/profiles/` package
- DECISION-035: Tagless rules match all inclusion lists (bootstrap fallback)
- DECISION-036: Severity overrides mutate `ValidationDiagnostic.severity` in-place
```

---

## 9. Acceptance Criteria (v0.5.1 Composite)

All 4 sub-parts must pass their individual acceptance criteria. In addition:

- [ ] `from docstratum.profiles import ValidationProfile` works
- [ ] `from docstratum.profiles import get_builtin_profile, list_builtin_profiles` works
- [ ] `from docstratum.profiles import rule_executes, apply_severity_overrides` works
- [ ] `from docstratum.profiles import resolve_inheritance` works
- [ ] The `ValidationProfile` model has all 13 fields with correct types and defaults
- [ ] `ValidationProfile(profile_name="test", description="A test")` constructs with defaults
- [ ] Invalid `max_validation_level` (e.g., 5) raises `ValidationError`
- [ ] Invalid `pass_threshold` (e.g., 101) raises `ValidationError`
- [ ] Unknown `output_format` produces a warning but does not raise
- [ ] `get_builtin_profile("lint")` returns a valid `ValidationProfile` with `max_validation_level=1`
- [ ] `get_builtin_profile("unknown")` raises `ValueError`
- [ ] `list_builtin_profiles()` returns `["lint", "ci", "full", "enterprise"]`
- [ ] `rule_executes(rule, profile)` correctly applies OR inclusion semantics
- [ ] `rule_executes(rule, profile)` correctly applies exclusion-always-wins
- [ ] Tag filtering degrades gracefully when rules have no tags (bootstrap mode)
- [ ] `apply_severity_overrides()` modifies diagnostic severity and logs changes
- [ ] `resolve_inheritance(child, resolver)` produces a flattened profile with child overrides
- [ ] Circular inheritance (`A extends B extends A`) raises `ValueError`
- [ ] Multi-level inheritance (`A extends B extends C`) raises `ValueError`
- [ ] CLI `validate_command()` uses profile-driven settings instead of `CLI_DEFAULTS`
- [ ] `PipelineContext.profile` field is populated before pipeline execution
- [ ] `pytest --cov=docstratum.profiles --cov-fail-under=90` passes
- [ ] `black --check` and `ruff check` pass on all new code
- [ ] `mypy src/docstratum/profiles/` passes

---

## 10. Test Strategy

| Test Category | Location | Coverage Target | Description |
|---------------|----------|-----------------|-------------|
| Unit: Profile Model | `tests/test_profile_model.py` | ≥95% | Pydantic validation, defaults, edge cases |
| Unit: Built-in Profiles | `tests/test_builtin_profiles.py` | 100% | All 4 profiles, lookup, listing |
| Unit: Tag Filtering | `tests/test_profile_filtering.py` | 100% | OR semantics, exclusion, level/stage gating, bootstrap |
| Unit: Severity Overrides | `tests/test_severity_overrides.py` | ≥95% | Override application, audit logging |
| Unit: Inheritance | `tests/test_profile_inheritance.py` | 100% | Single-level, circular, multi-level, field resolution |
| Integration: Profile + CLI | `tests/test_cli_profile_integration.py` | ≥85% | CLI uses profile; different profiles produce different behavior |

**Total estimated tests:** ~50 tests across 6 test files.

---

## 11. Limitations

| Limitation | Impact | Resolution Version |
|------------|--------|--------------------|
| Profiles are only available as built-ins | Users cannot load custom profiles from YAML/JSON files | v0.5.2a (Profile Loading) |
| Profile discovery is built-in only | No project config, user config, or file path lookup | v0.5.2b (Discovery Precedence) |
| CLI overrides not applied to profiles | `--max-level 2` on `--profile ci` doesn't override the profile's level 3 | v0.5.2c (CLI Override Integration) |
| Tag filtering is in bootstrap mode | Without Rule Registry, all rules pass inclusion checks | Deliverable 3 (Rule Registry) |
| `output_format` fallback not fully operational | "markdown" and "html" formats produce warnings; only "terminal" and "json" render | v0.8.x (Report Generation) |
| `priority_overrides` stored but not consumed | Priority overrides require the Remediation Framework | v0.6.x |
| `grouping_mode` stored but not consumed | Grouping requires Report Generation | v0.8.x |
| `output_tier` partially interpreted | Only Tier 1 and Tier 2 produce output; Tier 3/4 fall back to Tier 2 | v0.6.x, v0.8.x |

---

## 12. What Comes Next

Upon completion of v0.5.1, the profile *system* is defined but the profile *loading pipeline* is not yet operational. A user can access built-in profiles by name, but cannot:

- Load custom profiles from YAML/JSON files
- Store profiles in `.docstratum.yml`
- Override profile fields from CLI flags
- Use legacy v0.2.4d configuration

These capabilities are delivered by **v0.5.2 — Profile Discovery & Configuration**, which builds upon the model, presets, filtering, and inheritance established here.
