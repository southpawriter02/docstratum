# v0.5.2 — Profile Discovery & Configuration

> **Version:** v0.5.2
> **Document Type:** Parent Design Specification (Profile Discovery & Configuration)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SCOPE-v0.5.x-cli-and-profiles.md](RR-SCOPE-v0.5.x-cli-and-profiles.md)
> **Governing Specs:** RR-SPEC-v0.1.3-validation-profiles.md §5 (Discovery & Loading), §8 (Backward Compatibility)
> **Depends On:** v0.5.1 (ValidationProfile model, built-in profiles, filtering, inheritance), v0.5.0 (CLI Foundation: `cli.py`, `cli_args.py`, `cli_exit_codes.py`, `cli_output.py`), v0.4.x (`QualityScore`), v0.3.x (`ValidationResult`)
> **Consumed By:** v0.6.x (Remediation Framework), v0.7.x (Ecosystem Integration), v0.8.x (Report Generation)

---

## 1. Purpose

v0.5.2 builds the **profile loading pipeline** — the infrastructure that transforms a raw YAML or JSON file on disk into a resolved, validated `ValidationProfile` instance injected into the `PipelineContext`. After v0.5.2, the profile system is *fully operational*: a user can write a custom profile, save it as YAML, point the CLI at it, and have the validation engine governed entirely by that profile's configuration.

Before v0.5.2, profiles exist only as Python constants (the 4 built-ins from v0.5.1b). The `--profile` CLI flag resolves names against `get_builtin_profile()`. After v0.5.2:

```bash
# Load a custom profile from a YAML file
docstratum validate llms.txt --profile ./strict-ci.yaml

# Load a profile from .docstratum.yml (project config)
docstratum validate llms.txt --profile strict-ci

# Override profile fields from CLI flags
docstratum validate llms.txt --profile ci --max-level 2 --output-format markdown

# Use legacy v0.2.4d config (auto-migrated)
docstratum validate llms.txt  # reads .docstratum.yml with validation.level: 3
```

### 1.1 What v0.5.2 Is

A **profile I/O and resolution layer** that:

1. **Loads profiles from disk** (v0.5.2a) — reads YAML/JSON files, validates against the Pydantic schema, tracks `source_keys` for inheritance, resolves `extends`.
2. **Discovers profiles by name** (v0.5.2b) — implements the 4-source lookup chain (CLI > project > user > built-in) with exhaustive "not found" diagnostics.
3. **Merges CLI overrides** (v0.5.2c) — applies CLI flag values on top of the loaded profile using Replace semantics (DECISION-032).
4. **Migrates legacy config** (v0.5.2d) — auto-detects v0.2.4d `.docstratum.yml` format and converts it to a `ValidationProfile` with deprecation warnings.

### 1.2 What v0.5.2 Is NOT

| Not This | Why | Where It Lives |
|----------|-----|----------------|
| Defining the profile model | The `ValidationProfile` Pydantic model is v0.5.1a | v0.5.1a |
| Defining built-in presets | The 4 built-in profiles are v0.5.1b | v0.5.1b |
| Rule filtering | Tag-based filtering engine is v0.5.1c | v0.5.1c |
| Inheritance resolution logic | The resolver is v0.5.1d; v0.5.2a *calls* it | v0.5.1d |
| Profile editing / creation wizard | No interactive profile creation tool | Out of scope |
| Remote profile loading | Loading from URLs, registries, or package indices | Out of scope |
| Profile schema versioning | No `schema_version` field or migration pipeline | Future consideration |

### 1.3 User Stories

> **US-1:** As a developer, I want to create a `strict-ci.yaml` file with `pass_threshold: 80` and load it via `--profile ./strict-ci.yaml`, so that my team can share a stricter CI configuration without depending on built-in presets.

> **US-2:** As a team lead, I want to define project-specific profiles in `.docstratum.yml` under a `profiles:` section, so that all team members automatically use the same validation settings without explicit `--profile` flags.

> **US-3:** As an individual developer, I want to store personal profiles in `~/.docstratum/profiles/`, so that I can customize validation across all my projects without polluting project configuration.

> **US-4:** As a developer, I want CLI flags like `--max-level 2` to override the loaded profile's `max_validation_level`, so that I can temporarily adjust behavior without creating a new profile file.

> **US-5:** As a user of the legacy v0.2.4d config format, I want the CLI to auto-detect my existing `.docstratum.yml` configuration and apply the equivalent profile settings, so that I don't have to immediately rewrite my configuration.

> **US-6:** As a developer, I want clear error messages when a profile file has invalid fields or a profile name is not found, listing all searched locations, so that I can debugconfiguration issues quickly.

---

## 2. Architecture

### 2.1 Module Map

```
src/docstratum/
├── profiles/                          ← Package (created in v0.5.1)
│   ├── __init__.py                    ← Re-exports (UPDATED in v0.5.2)
│   ├── model.py                       ← ValidationProfile model [v0.5.1a]
│   ├── builtins.py                    ← 4 built-in profiles [v0.5.1b]
│   ├── filtering.py                   ← Tag-based filtering [v0.5.1c]
│   ├── inheritance.py                 ← Inheritance resolver [v0.5.1d]
│   ├── loading.py                     ← File loader (YAML/JSON → VP) [v0.5.2a] NEW
│   ├── discovery.py                   ← 4-source discovery chain [v0.5.2b] NEW
│   ├── overrides.py                   ← CLI override merging [v0.5.2c] NEW
│   └── migration.py                   ← Legacy v0.2.4d migration [v0.5.2d] NEW
│
├── cli.py                             ← MODIFIED: uses discovery chain + overrides
├── cli_args.py                        ← READ: CliArgs from v0.5.0b
├── cli_exit_codes.py                  ← READ: exit code mapper
├── cli_output.py                      ← READ: terminal formatter
│
├── schema/
│   ├── validation.py                  ← ValidationResult (READ)
│   ├── quality.py                     ← QualityScore (READ)
│   └── ...
├── pipeline/
│   └── stages.py                      ← PipelineContext.profile (WRITE)
└── __init__.py                        ← __version__ (READ)
```

### 2.2 Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ User runs:                                                       │
│   docstratum validate llms.txt --profile strict-ci --max-level 2 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────┐
│ v0.5.0b: CliArgs                      │  Parsed CLI arguments
│   args.profile = "strict-ci"          │
│   args.max_level = 2                  │
│   args.output_format = None           │
└──────────────────────────┬───────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│ v0.5.2b: Discovery Chain                                      │
│   discover_profile("strict-ci")                               │
│                                                               │
│   1. Is "strict-ci" a file path? (.yaml/.yml/.json suffix)    │
│      → NO (no file extension)                                 │
│   2. Check .docstratum.yml → profiles.strict-ci               │
│      → FOUND → v0.5.2a: load from embedded dict               │
│   3. (not reached) ~/.docstratum/profiles/strict-ci.yaml      │
│   4. (not reached) Built-in registry                          │
│                                                               │
│   → Returns: ValidationProfile(profile_name="strict-ci", ...) │
│              + source_keys={"profile_name", "pass_threshold",  │
│                              "output_format", "extends"}       │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────┐
│ v0.5.1d: Inheritance Resolution                   │
│   If profile.extends is set:                      │
│     resolve_inheritance(profile, discovery_chain,  │
│                         source_keys)              │
│   → Flattened ValidationProfile (extends=None)    │
└──────────────────────────┬───────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────┐
│ v0.5.2c: CLI Override Merging                     │
│   merge_cli_overrides(profile, args)              │
│   args.max_level = 2 (not None → override)        │
│   args.output_format = None (keep profile's value) │
│   → ValidationProfile with max_validation_level=2  │
└──────────────────────────┬───────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────┐
│ PipelineContext.profile = resolved_profile         │
│   Pipeline executes with profile-driven settings   │
└──────────────────────────────────────────────────┘
```

### 2.3 Integration with v0.5.1

v0.5.2 consumes every component of v0.5.1:

| v0.5.1 Component | How v0.5.2 Uses It |
|-------------------|-------------------|
| `ValidationProfile` (v0.5.1a) | Target type for loading. The loader constructs `ValidationProfile` instances from parsed dicts. |
| `get_builtin_profile` (v0.5.1b) | Priority 4 in the discovery chain. Also used as the `profile_resolver` callback for inheritance. |
| `is_builtin_profile` (v0.5.1b) | Discovery chain checks before searching files. |
| `list_builtin_profiles` (v0.5.1b) | "Not found" error messages list available built-ins. |
| `resolve_inheritance` (v0.5.1d) | Called by the loader after profile construction. The discovery chain provides the `profile_resolver` callback. |
| `InheritanceError` (v0.5.1d) | Caught by the loader and re-raised as a `ProfileLoadError` with context. |

### 2.4 Integration with v0.5.0

v0.5.2 modifies `cli.py` → `validate_command()` to replace the v0.5.1 built-in-only lookup with the full pipeline:

```python
# BEFORE (v0.5.1):
from docstratum.profiles import get_builtin_profile
profile = get_builtin_profile(args.profile or "ci")

# AFTER (v0.5.2):
from docstratum.profiles.discovery import discover_profile
from docstratum.profiles.overrides import merge_cli_overrides

profile = discover_profile(args.profile)        # v0.5.2b
profile = merge_cli_overrides(profile, args)     # v0.5.2c
# Pipeline now uses the fully resolved, overridden profile
```

The `CLI_DEFAULTS` dictionary (introduced in v0.5.0, kept as fallback in v0.5.1) is now **removed**. It is no longer needed — the discovery chain always produces a valid `ValidationProfile`, even when no `--profile` flag is provided (it falls back to the `ci` built-in or `default_profile` from `.docstratum.yml`).

---

## 3. Sub-Part Breakdown

### 3.1 v0.5.2a — Profile Loading

**Module:** `profiles/loading.py`
**What it does:** Reads a YAML/JSON file (or an embedded profile dict from `.docstratum.yml`), constructs a `ValidationProfile`, tracks `source_keys` for inheritance, and resolves `extends`.
**Design Spec:** [RR-SPEC-v0.5.2a-profile-loading.md](RR-SPEC-v0.5.2a-profile-loading.md)

---

### 3.2 v0.5.2b — Discovery Precedence

**Module:** `profiles/discovery.py`
**What it does:** Implements the 4-source lookup chain (CLI flag > project config > user config > built-in) that resolves a profile name or file path to a `ValidationProfile`.
**Design Spec:** [RR-SPEC-v0.5.2b-discovery-precedence.md](RR-SPEC-v0.5.2b-discovery-precedence.md)

---

### 3.3 v0.5.2c — CLI Override Integration

**Module:** `profiles/overrides.py`
**What it does:** Merges CLI flag values into the loaded profile using shallow Replace semantics (DECISION-032).
**Design Spec:** [RR-SPEC-v0.5.2c-cli-override-integration.md](RR-SPEC-v0.5.2c-cli-override-integration.md)

---

### 3.4 v0.5.2d — Legacy Format Migration

**Module:** `profiles/migration.py`
**What it does:** Auto-detects the v0.2.4d `.docstratum.yml` configuration format and converts it to a `ValidationProfile` with deprecation warnings.
**Design Spec:** [RR-SPEC-v0.5.2d-legacy-format-migration.md](RR-SPEC-v0.5.2d-legacy-format-migration.md)

---

## 4. Dependency Chain

```
v0.5.2a (Profile Loading)       ← depends on v0.5.1a (model) + v0.5.1d (inheritance)
    │
    ▼
v0.5.2b (Discovery Chain)      ← depends on v0.5.2a + v0.5.1b (built-ins)
    │
    ▼
v0.5.2c (CLI Overrides)        ← depends on v0.5.0b (parsed args) + v0.5.2b (loaded profile)
    │
    ▼
v0.5.2d (Legacy Migration)     ← depends on v0.5.2a (loading infrastructure)
                                   (can be developed in parallel with v0.5.2c)
```

**Parallelization:** v0.5.2c (CLI Overrides) and v0.5.2d (Legacy Migration) can be developed simultaneously once v0.5.2b is complete. v0.5.2d only depends on the loading function from v0.5.2a, not on the discovery chain, so it can even start once v0.5.2a is done.

**External Dependencies:**
- **PyYAML** — for YAML profile parsing. The design spec for v0.5.2a confirms the YAML library choice (see §5.1).
- **Pydantic v2** — already a project dependency. Used for `ValidationProfile` construction and validation.
- **v0.5.1** — complete. All profile model, built-in, filtering, and inheritance components must be operational.

---

## 5. Key Design Decisions

### 5.1 YAML Library Choice

**DECISION-040: Use PyYAML (`pyyaml`) for YAML profile parsing.**

**Rationale:**
1. **Already a dependency.** PyYAML is listed in `pyproject.toml` (used by other parts of the project).
2. **Minimal API surface.** Profile loading needs `yaml.safe_load()` only — no roundtrip editing, no comment preservation, no YAML 1.2 features.
3. **Widely available.** PyYAML is the most-installed YAML library on PyPI, reducing friction for users.

**Alternative considered:** `ruamel.yaml` — provides YAML 1.2 compliance, comment preservation, and roundtrip editing. Overkill for read-only profile loading. Would be needed if v0.5.2 implemented a `docstratum init` command that generates YAML files — but that's out of scope.

**Trade-off:** PyYAML only supports YAML 1.1 (e.g., `yes`/`no` → boolean). Profile files should avoid bare `yes`/`no` values. The loader will document this limitation.

### 5.2 Profile Source Key Tracking

**DECISION-039 (continued from v0.5.1d):** The loader tracks which YAML/JSON keys were explicitly present in the source file and passes this as `source_keys` to `resolve_inheritance()`. This enables accurate override detection during inheritance resolution.

Implementation: after parsing the raw YAML/JSON dictionary, record `set(raw_dict.keys())` before passing it to `ValidationProfile(**raw_dict)`.

### 5.3 Discovery Chain as Profile Resolver

**DECISION-041: The discovery chain (`discover_profile`) doubles as the `profile_resolver` callback for inheritance.**

When the loader encounters `extends="full"` in a file-based profile, it needs to resolve "full" to a `ValidationProfile`. Rather than hardcoding `get_builtin_profile`, the loader receives the discovery chain's resolve function. This allows a file-based profile to extend another file-based profile (e.g., a user profile extending a project profile), not just built-ins.

```python
# In discovery.py:
def discover_profile(spec: str | None) -> ValidationProfile:
    ...
    # When loading from file:
    profile = load_profile_from_file(
        path,
        profile_resolver=discover_profile,  # Recursive!
    )
```

**Guard against infinite recursion:** The discovery chain maintains a `_resolution_stack: set[str]` of profile names currently being resolved. If a name appears twice, it's a circular dependency → `InheritanceError`.

### 5.4 Error Types

**DECISION-042: All profile loading/discovery errors are subclasses of `ProfileError`.**

```python
class ProfileError(Exception):
    """Base class for all profile-related errors."""
    pass

class ProfileLoadError(ProfileError):
    """Raised when a profile file cannot be loaded or validated."""
    pass

class ProfileNotFoundError(ProfileError):
    """Raised when a profile cannot be found in any source."""
    pass

class ProfileMigrationWarning(UserWarning):
    """Emitted when legacy format is auto-migrated."""
    pass
```

This hierarchy allows the CLI to catch `ProfileError` at the top level and produce a consistent error format, while specific handlers can catch subtypes for targeted recovery.

### 5.5 CLI_DEFAULTS Removal

**DECISION-043: `CLI_DEFAULTS` is removed in v0.5.2.**

The `CLI_DEFAULTS` dictionary was introduced in v0.5.0 as a temporary hardcoded profile equivalent. In v0.5.1 it was kept as a fallback. In v0.5.2, the discovery chain always produces a valid `ValidationProfile` (worst case: the `ci` built-in), making `CLI_DEFAULTS` dead code.

Removal is documented in the changelog as a **Changed** entry. Any tests that reference `CLI_DEFAULTS` are updated.

---

## 6. Models

### 6.1 New Types Created

| Type | Module | Purpose |
|------|--------|---------|
| `ProfileError` | `profiles/loading.py` | Base exception for profile errors |
| `ProfileLoadError` | `profiles/loading.py` | File loading / validation failure |
| `ProfileNotFoundError` | `profiles/discovery.py` | Profile not found in any source |
| `ProfileMigrationWarning` | `profiles/migration.py` | Legacy format deprecation warning |
| `ProfileSource` | `profiles/discovery.py` | Enum tracking where a profile was loaded from |
| `LoadedProfile` | `profiles/loading.py` | Container pairing `ValidationProfile` with `source_keys` + `source` metadata |

### 6.2 Models Consumed (Not Modified)

| Model | Source | How v0.5.2 Uses It |
|-------|--------|-------------------|
| `ValidationProfile` | `profiles/model.py` | Constructed from parsed dicts; validated by Pydantic |
| `CliArgs` | `cli_args.py` | Read by override merging (v0.5.2c) |
| `PipelineContext` | `pipeline/stages.py` | `.profile` field populated with resolved profile |

### 6.3 Models Modified

None. v0.5.2 does not modify any existing models. The `PipelineContext.profile` field was added in v0.5.1; v0.5.2 just writes to it.

---

## 7. Inline Documentation Requirements

All new modules in v0.5.2 MUST include:

1. **Module docstring** — citing the spec version (e.g., `"""Implements v0.5.2a — Profile Loading."""`)
2. **Function/method docstrings** — Google-style with Args, Returns, Raises, and Example sections
3. **Version traces** — `# Implements v0.5.2a` on key functions/classes
4. **Grounding comments** — `# Grounding: RR-SPEC-v0.1.3-validation-profiles.md §5.3` on design-critical logic
5. **Decision references** — `# DECISION-040: PyYAML for YAML parsing` on structural choices
6. **Type annotations** — Complete type hints on all public and private functions
7. **Error context** — All exceptions must include the source path (for file errors), the field name (for validation errors), or the search sequence (for "not found" errors)

---

## 8. Changelog Requirements

Upon completion of v0.5.2 (all 4 sub-parts), a changelog entry is required:

```markdown
## [0.5.2] — 2026-XX-XX

### Added
- Profile loading from YAML and JSON files with full Pydantic validation (v0.5.2a)
- Embedded profile loading from `.docstratum.yml` `profiles:` section (v0.5.2a)
- Source key tracking for precise inheritance override detection (v0.5.2a)
- 4-source profile discovery chain: CLI flag > project config > user config >
  built-in, with exhaustive "not found" diagnostics (v0.5.2b)
- `default_profile` key in `.docstratum.yml` for project-level default (v0.5.2b)
- User profile directory: `~/.docstratum/profiles/` (v0.5.2b)
- CLI flag override merging with Replace semantics (v0.5.2c)
- Inline profile construction when CLI flags override defaults (v0.5.2c)
- Auto-migration of legacy v0.2.4d `.docstratum.yml` format with deprecation
  warning (v0.5.2d)
- `ProfileError`, `ProfileLoadError`, `ProfileNotFoundError` exception hierarchy
- `ProfileSource` enum for tracking profile provenance

### Changed
- `validate_command()` in `cli.py` now uses the full discovery chain instead
  of built-in-only lookup (v0.5.2b)
- Removed `CLI_DEFAULTS` dictionary — superseded by discovery chain (DECISION-043)

### Decisions
- DECISION-040: PyYAML for YAML profile parsing
- DECISION-041: Discovery chain doubles as inheritance profile_resolver
- DECISION-042: ProfileError exception hierarchy
- DECISION-043: CLI_DEFAULTS removal
```

---

## 9. Acceptance Criteria (v0.5.2 Composite)

All 4 sub-parts must pass their individual acceptance criteria. In addition:

- [ ] `docstratum validate llms.txt --profile ./custom.yaml` loads a YAML profile
- [ ] `docstratum validate llms.txt --profile ./custom.json` loads a JSON profile
- [ ] A YAML profile with `extends: "full"` inherits all `full` fields with child overrides
- [ ] A JSON profile with invalid fields produces a `ProfileLoadError` with field-level messages
- [ ] A missing profile file produces a `FileNotFoundError` with the full path
- [ ] `docstratum validate llms.txt --profile strict-ci` discovers the profile via the 4-source chain
- [ ] Discovery checks `.docstratum.yml`, `~/.docstratum/profiles/`, and built-ins in order
- [ ] Profile not found produces an error listing all searched locations
- [ ] `default_profile: "full"` in `.docstratum.yml` changes the default from `ci`
- [ ] When no `--profile` flag and no `.docstratum.yml`, default is `ci`
- [ ] `--max-level 2` on `--profile ci` overrides `max_validation_level` from 3 to 2
- [ ] `--tags structural` on `--profile ci` replaces `rule_tags_include` (not appends)
- [ ] CLI flags that are `None` (not provided) do not override profile values
- [ ] Legacy `.docstratum.yml` with `validation.level: 3` auto-migrates to `ci` profile behavior
- [ ] Legacy migration emits a deprecation warning with migration guidance
- [ ] Legacy migration produces correct profile when `check_urls: false`
- [ ] Mixed legacy/new format: `profiles:` section takes precedence over `validation:` section
- [ ] `ProfileError` hierarchy is importable from `docstratum.profiles`
- [ ] `cli.py` no longer references `CLI_DEFAULTS`
- [ ] `pytest --cov=docstratum.profiles --cov-fail-under=90` passes
- [ ] `black --check` and `ruff check` pass on all new code
- [ ] `mypy src/docstratum/profiles/` passes

---

## 10. Test Strategy

| Test Category | Location | Coverage Target | Description |
|---------------|----------|-----------------|-------------|
| Unit: File Loading | `tests/test_profile_loading.py` | ≥95% | YAML/JSON parsing, validation errors, source key tracking |
| Unit: Embedded Loading | `tests/test_profile_loading_embedded.py` | ≥90% | `.docstratum.yml` embedded profiles |
| Unit: Discovery Chain | `tests/test_profile_discovery.py` | 100% | All 4 sources, precedence, not-found diagnostics |
| Unit: CLI Overrides | `tests/test_profile_overrides.py` | 100% | Each CLI flag, None passthrough, Replace semantics |
| Unit: Legacy Migration | `tests/test_profile_migration.py` | 100% | All legacy fields, deprecation warnings, edge cases |
| Integration: Full Pipeline | `tests/test_profile_pipeline_integration.py` | ≥85% | End-to-end: CLI → discovery → loading → inheritance → overrides → pipeline |

**Total estimated tests:** ~60 tests across 6 test files.

**Test fixtures:** YAML and JSON profile files stored in `tests/fixtures/profiles/` for deterministic testing. Includes valid profiles, invalid profiles, profiles with inheritance, and legacy configs.

---

## 11. Limitations

| Limitation | Impact | Resolution Version |
|------------|--------|-------------------|
| No remote profile loading | Cannot load from URLs, package registries, or CDNs | Out of scope |
| No profile schema versioning | No `schema_version` field to detect format changes | Future consideration |
| No `docstratum init` command | Users must manually create profile files | Future CLI subcommand |
| No `docstratum check-profile` command | Profile validation is only done at load time | Future CLI subcommand |
| PyYAML limitation: YAML 1.1 only | Bare `yes`/`no` interpreted as booleans | Document in profile authoring guide |
| No deep merge for dict overrides | Cannot override a single `severity_overrides` entry from CLI | By design (DECISION-032) |
| Legacy migration is runtime-only | Does not modify the user's `.docstratum.yml` | By design — automatic rewriting is too invasive |
| User config dir not auto-created | `~/.docstratum/profiles/` must exist for user profiles | Documented; `docstratum init` can create it later |

---

## 12. What Comes Next

Upon completion of v0.5.2, the **full v0.5.x scope is complete** — the CLI, profile model, filtering engine, inheritance, loading, discovery, CLI overrides, and legacy migration are all operational. The exit criteria from RR-SCOPE-v0.5.x §6 should all be satisfied.

The profile system now feeds into:

- **v0.6.x (Remediation Framework):** Reads `profile.priority_overrides` to adjust diagnostic priorities. The `grouping_mode` field becomes consumed.
- **v0.7.x (Ecosystem Integration):** Wires ecosystem pipeline into CLI dispatch. `enabled_stages` with Stage 3–5 activated triggers multi-file validation.
- **v0.8.x (Report Generation):** Stage 6 consumes `output_tier`, `output_format`, and `grouping_mode`. The `"markdown"`, `"yaml"`, and `"html"` formats become fully operational.
- **v0.9.0 (Extended Validation):** L4 checks activate. The `full` and `enterprise` profiles (which set `max_validation_level=4`) automatically run L4 rules.
