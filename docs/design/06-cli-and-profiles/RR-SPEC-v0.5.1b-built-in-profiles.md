# v0.5.1b — Built-in Profiles

> **Version:** v0.5.1b
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.5.1-validation-profiles.md](RR-SPEC-v0.5.1-validation-profiles.md)
> **Grounding:** RR-SPEC-v0.1.3-validation-profiles.md §3 (4 Built-in Profiles)
> **Depends On:** v0.5.1a (`ValidationProfile` model)
> **Module:** `src/docstratum/profiles/builtins.py`
> **Tests:** `tests/test_builtin_profiles.py`

---

## 1. Purpose

Define the 4 built-in profiles — `lint`, `ci`, `full`, and `enterprise` — as Python constants that ship with the package. These are the "factory presets" available without any YAML files on disk, without any configuration, and without any file I/O. They represent the canonical use cases for the DocStratum validation engine.

After v0.5.1b:

```python
from docstratum.profiles import get_builtin_profile, list_builtin_profiles

profile = get_builtin_profile("lint")
assert profile.max_validation_level == 1
assert profile.enabled_stages == [1, 2]

names = list_builtin_profiles()
# ["ci", "enterprise", "full", "lint"]  (sorted alphabetically)
```

### 1.1 User Stories

> **US-1:** As the CLI dispatcher, I need a `get_builtin_profile("ci")` function that returns the default profile, so that the CLI can operate with profile-driven settings before the file-based loading infrastructure (v0.5.2) is built.

> **US-2:** As a developer, I want to run `list_builtin_profiles()` to see all available built-in profiles, so that I can discover what's available without reading documentation.

> **US-3:** As a CI maintainer, I want the `ci` profile to be the default when no `--profile` flag is provided, so that CI pipelines get reasonable machine-parseable output without configuration.

---

## 2. Profile Definitions

### 2.1 Profile Comparison Matrix

| Field | **lint** | **ci** | **full** | **enterprise** |
|-------|----------|--------|----------|----------------|
| `profile_name` | `"lint"` | `"ci"` | `"full"` | `"enterprise"` |
| `description` | "Quick structural lint — L0–L1 checks only, terminal output, no threshold." | "CI pipeline default — L0–L3 checks, score threshold 50, JSON output for machine parsing." | "Comprehensive validation — all levels, all stages, Markdown output for sharing." | "Enterprise audit — extends full with Tier 4 audience-adapted HTML output." |
| `max_validation_level` | `1` | `3` | `4` | `4` (inherited from `full`) |
| `enabled_stages` | `[1, 2]` | `[1, 2, 3, 4, 5]` | `[1, 2, 3, 4, 5, 6]` | `[1, 2, 3, 4, 5, 6]` (inherited) |
| `rule_tags_include` | `["structural"]` | `["structural", "content", "ecosystem"]` | `[]` (all) | `[]` (inherited) |
| `rule_tags_exclude` | `[]` | `["experimental", "docstratum-extended"]` | `[]` | `[]` (inherited) |
| `severity_overrides` | `{}` | `{}` | `{}` | `{}` (inherited) |
| `priority_overrides` | `{}` | `{}` | `{}` | `{}` (inherited) |
| `pass_threshold` | `None` | `50` | `None` | `None` (inherited) |
| `output_tier` | `2` | `1` | `3` | `4` (**overrides** full) |
| `output_format` | `"terminal"` | `"json"` | `"markdown"` | `"html"` (**overrides** full) |
| `grouping_mode` | `"by-priority"` | `"by-priority"` | `"by-priority"` | `"by-priority"` (inherited) |
| `extends` | `None` | `None` | `None` | `"full"` |

### 2.2 Per-Profile Design Rationale

#### lint — Maximum Speed

**Use case:** Editor integration, pre-commit hooks, quick sanity checks during editing.

**Design choices:**
- `max_validation_level=1`: Only L0 (parseable) and L1 (structural). Skips L2 (content), L3 (best practices), and L4 (extended). This is the fastest possible validation.
- `enabled_stages=[1, 2]`: Only Stages 1 (parsing) and 2 (single-file validation). No ecosystem scan (Stage 3–5), no report generation (Stage 6).
- `rule_tags_include=["structural"]`: Only rules tagged "structural" execute. In bootstrap mode (no Rule Registry), all rules pass inclusion (see DECISION-035).
- `pass_threshold=None`: No numeric threshold. The developer cares about error presence, not a score.
- `output_format="terminal"`: Colorized terminal output for rapid feedback.

**Expected behavior:**
```bash
docstratum validate llms.txt --profile lint
# Fast check: only structure and parseability
# Exit 0 if no L0/L1 errors, exit 1 if structural errors found
```

#### ci — The Default

**Use case:** CI/CD pipelines, pull request gates, automated quality checks.

**Design choices:**
- `max_validation_level=3`: L0–L3 (up to best practice warnings). L4 (extended) is excluded — CI shouldn't fail on optional/experimental checks.
- `enabled_stages=[1, 2, 3, 4, 5]`: All stages including ecosystem. Stage 6 (report generation) is excluded — CI uses JSON output, not formatted reports.
- `rule_tags_exclude=["experimental", "docstratum-extended"]`: Explicitly excludes unstable rules and DocStratum-specific extensions. This is the conservative, stable check set.
- `pass_threshold=50`: Enforces a minimum quality bar. Scores below 50 trigger exit code 5. This threshold is deliberately low — strict teams can override with `--pass-threshold 75`.
- `output_format="json"`: Machine-parseable output for CI tools. Pipes cleanly to `jq` or downstream analysis.
- `output_tier=1`: Summary tier — file, score, grade, pass/fail. Detailed diagnostics are available via `--verbose` or by switching to Tier 2.

**Expected behavior:**
```bash
docstratum validate llms.txt --profile ci
# JSON output to stdout, exit 0 if score >= 50 and no errors
# Exit 5 if score < 50, exit 1–2 if errors found
```

#### full — Show Me Everything

**Use case:** Documentation audits, pre-release quality reviews, comprehensive analysis.

**Design choices:**
- `max_validation_level=4`: All levels including L4 (extended validation). This activates advanced checks like semantic analysis, cross-reference validation, and community best practices (when available via v0.9.0).
- `enabled_stages=[1, 2, 3, 4, 5, 6]`: All stages including Stage 6 (report generation). At v0.5.x, Stage 6 is not yet operational — it will be skipped with a log message.
- `rule_tags_include=[]` (empty): Include all rules. No tag filtering — every available check runs.
- `rule_tags_exclude=[]` (empty): Exclude nothing. Even experimental rules run.
- `pass_threshold=None`: No threshold gate. The goal is a complete report, not a pass/fail gate.
- `output_format="markdown"`: Rendered Markdown for sharing in PRs, wikis, or documentation sites. At v0.5.x, Markdown output falls back to terminal with a warning.
- `output_tier=3`: Remediation tier — includes diagnostic details plus action items. At v0.5.x, Tier 3 falls back to Tier 2 behavior.

**Expected behavior:**
```bash
docstratum validate llms.txt --profile full
# Comprehensive analysis with all checks
# Terminal output (Markdown fallback at v0.5.x)
# Always produces output regardless of score
```

#### enterprise — Extends Full

**Use case:** Enterprise compliance, multi-audience reporting, formal audit documents.

**Design choices:**
- `extends="full"`: Inherits all settings from `full`. Only overrides output-related fields.
- `output_tier=4`: Audience-adapted tier. Requires the context profile system and audience adaptation engine (v0.8.x). At v0.5.x, falls back to Tier 3 → Tier 2 behavior.
- `output_format="html"`: Polished HTML report for stakeholders. At v0.5.x, HTML falls back to terminal with a warning.

**Expected behavior:**
```bash
docstratum validate llms.txt --profile enterprise
# Same checks as "full" profile
# HTML output (falls back to terminal at v0.5.x)
# Warning: "Tier 4 requires audience adaptation engine (v0.8.x)..."
```

---

## 3. Implementation

### 3.1 Storage Decision

**DECISION-038: Built-in profiles are defined as Python constants, not bundled YAML files.**

**Rationale:**
1. **Always available.** Python constants load without file I/O. No risk of a missing YAML file breaking the CLI.
2. **No file discovery needed.** The `get_builtin_profile()` function is a simple dictionary lookup, not a filesystem scan.
3. **Type-safe.** `ValidationProfile` instances are constructed at import time and validated by Pydantic. Invalid profiles fail at `import`, not at runtime.
4. **Version-controlled.** Changes to built-in profiles are visible in Git diffs as Python code changes, not YAML diffs.

**Alternative considered:** Bundled YAML files in `src/docstratum/profiles/builtins/`. Rejected because it introduces file I/O into a lookup that should be instant, and makes it harder to detect invalid profiles at import time.

**Trade-off:** Users cannot easily inspect built-in profiles as YAML files. Mitigation: `docstratum profile show lint` (future CLI subcommand, not part of v0.5.x scope) would dump the profile as YAML.

### 3.2 Module Code

```python
# src/docstratum/profiles/builtins.py
"""Built-in validation profiles — factory presets shipped with DocStratum.

Defines the 4 canonical profiles: lint, ci, full, enterprise.
These are always available without configuration or file I/O.

Implements v0.5.1b.
Grounding: RR-SPEC-v0.1.3-validation-profiles.md §3.
"""

from __future__ import annotations

from docstratum.profiles.model import ValidationProfile


# --- Profile Definitions ---
# Grounding: RR-SCOPE-v0.5.x §3.2 (v0.5.1b profile table)
# DECISION-038: Python constants, not YAML files


PROFILE_LINT = ValidationProfile(
    profile_name="lint",
    description=(
        "Quick structural lint — L0–L1 checks only, terminal output, "
        "no threshold. Designed for editor integration and pre-commit hooks."
    ),
    max_validation_level=1,
    enabled_stages=[1, 2],
    rule_tags_include=["structural"],
    rule_tags_exclude=[],
    severity_overrides={},
    priority_overrides={},
    pass_threshold=None,
    output_tier=2,
    output_format="terminal",
    grouping_mode="by-priority",
    extends=None,
)

PROFILE_CI = ValidationProfile(
    profile_name="ci",
    description=(
        "CI pipeline default — L0–L3 checks, score threshold 50, JSON output "
        "for machine parsing. Excludes experimental and extended rules."
    ),
    max_validation_level=3,
    enabled_stages=[1, 2, 3, 4, 5],
    rule_tags_include=["structural", "content", "ecosystem"],
    rule_tags_exclude=["experimental", "docstratum-extended"],
    severity_overrides={},
    priority_overrides={},
    pass_threshold=50,
    output_tier=1,
    output_format="json",
    grouping_mode="by-priority",
    extends=None,
)

PROFILE_FULL = ValidationProfile(
    profile_name="full",
    description=(
        "Comprehensive validation — all levels, all stages, Markdown output "
        "for sharing. No threshold. Runs every available check."
    ),
    max_validation_level=4,
    enabled_stages=[1, 2, 3, 4, 5, 6],
    rule_tags_include=[],
    rule_tags_exclude=[],
    severity_overrides={},
    priority_overrides={},
    pass_threshold=None,
    output_tier=3,
    output_format="markdown",
    grouping_mode="by-priority",
    extends=None,
)

PROFILE_ENTERPRISE = ValidationProfile(
    profile_name="enterprise",
    description=(
        "Enterprise audit — extends full with Tier 4 audience-adapted HTML "
        "output. Suitable for compliance reporting and stakeholder reviews."
    ),
    max_validation_level=4,
    enabled_stages=[1, 2, 3, 4, 5, 6],
    rule_tags_include=[],
    rule_tags_exclude=[],
    severity_overrides={},
    priority_overrides={},
    pass_threshold=None,
    output_tier=4,
    output_format="html",
    grouping_mode="by-priority",
    extends="full",
)

# --- Registry ---

_BUILTIN_PROFILES: dict[str, ValidationProfile] = {
    "lint": PROFILE_LINT,
    "ci": PROFILE_CI,
    "full": PROFILE_FULL,
    "enterprise": PROFILE_ENTERPRISE,
}

# The default profile when no --profile flag is provided and no
# .docstratum.yml default_profile key exists.
# Grounding: RR-SPEC-v0.1.3-validation-profiles.md §5.2.
DEFAULT_PROFILE_NAME: str = "ci"


def get_builtin_profile(name: str) -> ValidationProfile:
    """Look up a built-in profile by name.

    Args:
        name: Profile name (case-sensitive). One of: lint, ci, full, enterprise.

    Returns:
        A ValidationProfile instance for the requested profile.

    Raises:
        ValueError: If the name does not match any built-in profile.

    Example:
        >>> profile = get_builtin_profile("lint")
        >>> profile.max_validation_level
        1
    """
    profile = _BUILTIN_PROFILES.get(name)
    if profile is None:
        available = ", ".join(sorted(_BUILTIN_PROFILES.keys()))
        raise ValueError(
            f"Unknown built-in profile '{name}'. "
            f"Available profiles: {available}."
        )
    return profile


def list_builtin_profiles() -> list[str]:
    """Return a sorted list of all built-in profile names.

    Returns:
        Alphabetically sorted list of profile names.

    Example:
        >>> list_builtin_profiles()
        ['ci', 'enterprise', 'full', 'lint']
    """
    return sorted(_BUILTIN_PROFILES.keys())


def is_builtin_profile(name: str) -> bool:
    """Check whether a name corresponds to a built-in profile.

    Args:
        name: Profile name to check.

    Returns:
        True if the name matches a built-in profile.
    """
    return name in _BUILTIN_PROFILES


def get_default_profile() -> ValidationProfile:
    """Return the default profile (used when no --profile flag is provided).

    Returns:
        The default ValidationProfile (currently 'ci').

    Example:
        >>> profile = get_default_profile()
        >>> profile.profile_name
        'ci'
    """
    return get_builtin_profile(DEFAULT_PROFILE_NAME)
```

### 3.3 Package Re-exports

```python
# Update src/docstratum/profiles/__init__.py
"""DocStratum validation profile system.

Provides the ValidationProfile model, built-in profile presets,
tag-based rule filtering, and single-level profile inheritance.

Implements v0.5.1.
Grounding: RR-SPEC-v0.1.3-validation-profiles.md.
"""

from docstratum.profiles.model import ValidationProfile
from docstratum.profiles.builtins import (
    get_builtin_profile,
    get_default_profile,
    is_builtin_profile,
    list_builtin_profiles,
    DEFAULT_PROFILE_NAME,
    PROFILE_LINT,
    PROFILE_CI,
    PROFILE_FULL,
    PROFILE_ENTERPRISE,
)

__all__ = [
    "ValidationProfile",
    "get_builtin_profile",
    "get_default_profile",
    "is_builtin_profile",
    "list_builtin_profiles",
    "DEFAULT_PROFILE_NAME",
    "PROFILE_LINT",
    "PROFILE_CI",
    "PROFILE_FULL",
    "PROFILE_ENTERPRISE",
]
```

### 3.4 CLI Integration (cli.py Update)

After v0.5.1b, `validate_command()` in `cli.py` is updated to use built-in profile lookup:

```python
# In cli.py → validate_command()

# BEFORE (v0.5.0):
# defaults = CLI_DEFAULTS
# max_level = args.max_level or defaults["max_validation_level"]

# AFTER (v0.5.1b):
from docstratum.profiles import get_builtin_profile, get_default_profile

if args.profile:
    try:
        profile = get_builtin_profile(args.profile)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(10)
else:
    profile = get_default_profile()

# Pipeline now uses profile.max_validation_level, profile.enabled_stages, etc.
# CLI overrides (--max-level, --tags) are NOT applied yet — that's v0.5.2c
```

> **Note:** At v0.5.1b, only built-in profiles are available. Custom profiles (from YAML/JSON) and CLI overrides come in v0.5.2. If `args.profile` is a filename (e.g., `./custom.yaml`), the CLI will raise `ValueError: Unknown built-in profile './custom.yaml'`. This is expected and will be resolved in v0.5.2b.

---

## 4. Decision Tree: Profile Selection at v0.5.1b

```
User runs: docstratum validate llms.txt [--profile <name>]
│
├── --profile provided?
│   │
│   ├── YES → name in built-in registry?
│   │          │
│   │          ├── YES → use built-in profile
│   │          │
│   │          └── NO → ValueError: "Unknown built-in profile '<name>'"
│   │                   (v0.5.2b will add file/project/user lookup)
│   │
│   └── NO → use default profile ("ci")
│            (v0.5.2b will check .docstratum.yml for default_profile first)
│
├── Profile resolved → inject into PipelineContext
│
└── Pipeline runs with profile configuration
```

---

## 5. Enterprise Profile & Inheritance

The `enterprise` profile is the **only built-in that uses `extends`**. At v0.5.1b, the `extends="full"` field is set but inheritance is **not resolved** — that's v0.5.1d.

This means the `enterprise` profile at v0.5.1b is **fully expanded** in its Python constant (`PROFILE_ENTERPRISE` has all 13 fields explicitly set). The `extends="full"` field is metadata indicating the design relationship, but the runtime behavior is identical to a standalone profile.

When v0.5.1d lands, the inheritance resolver can verify that `enterprise`'s expanded values match what `full + overrides` would produce. If they diverge, the constant is wrong.

```python
# Verification (test in v0.5.1d):
resolved = resolve_inheritance(
    child=ValidationProfile(
        profile_name="enterprise",
        description="...",
        output_tier=4,
        output_format="html",
        extends="full",
    ),
    profile_resolver=get_builtin_profile,
    source_keys={"profile_name", "description", "output_tier", "output_format", "extends"},
)
assert resolved.max_validation_level == PROFILE_ENTERPRISE.max_validation_level
assert resolved.enabled_stages == PROFILE_ENTERPRISE.enabled_stages
```

---

## 6. Workflow

### 6.1 Using Built-in Profiles from CLI

```bash
# Use the lint profile (fast structural check)
docstratum validate llms.txt --profile lint

# Use the CI profile (default if --profile is omitted)
docstratum validate llms.txt --profile ci
docstratum validate llms.txt  # equivalent

# Use the full profile (comprehensive analysis)
docstratum validate llms.txt --profile full

# Use the enterprise profile (HTML output, falls back at v0.5.x)
docstratum validate llms.txt --profile enterprise
```

### 6.2 Using Built-in Profiles Programmatically

```python
from docstratum.profiles import (
    get_builtin_profile,
    list_builtin_profiles,
    is_builtin_profile,
    PROFILE_CI,
)

# List all available
for name in list_builtin_profiles():
    profile = get_builtin_profile(name)
    print(f"{name}: L0–L{profile.max_validation_level}, "
          f"stages {profile.enabled_stages}, "
          f"format={profile.output_format}")

# Output:
# ci: L0–L3, stages [1, 2, 3, 4, 5], format=json
# enterprise: L0–L4, stages [1, 2, 3, 4, 5, 6], format=html
# full: L0–L4, stages [1, 2, 3, 4, 5, 6], format=markdown
# lint: L0–L1, stages [1, 2], format=terminal

# Check if a name is built-in
assert is_builtin_profile("ci")
assert not is_builtin_profile("custom")

# Direct constant access
assert PROFILE_CI.pass_threshold == 50
```

### 6.3 Development Cycle

```bash
# Run tests for built-in profiles
pytest tests/test_builtin_profiles.py -v

# Type check
mypy src/docstratum/profiles/builtins.py

# Format + lint
black src/docstratum/profiles/builtins.py
ruff check src/docstratum/profiles/builtins.py
```

---

## 7. Edge Cases

| Scenario | Input | Behavior |
|----------|-------|----------|
| Lookup unknown profile | `get_builtin_profile("custom")` | `ValueError` with available profile list |
| Lookup with case mismatch | `get_builtin_profile("CI")` | `ValueError` — names are case-sensitive |
| Lookup with file path | `get_builtin_profile("./ci.yaml")` | `ValueError` — not a built-in name (v0.5.2b handles file paths) |
| Empty name | `get_builtin_profile("")` | `ValueError` |
| `list_builtin_profiles()` | No args | Returns `["ci", "enterprise", "full", "lint"]` |
| `is_builtin_profile("lint")` | Built-in name | `True` |
| `is_builtin_profile("custom")` | Non-built-in name | `False` |
| `get_default_profile()` | No args | Returns the `ci` profile |
| Module import | `from docstratum.profiles import PROFILE_LINT` | Direct constant access |
| Enterprise `extends` at v0.5.1b | `PROFILE_ENTERPRISE.extends` | `"full"` — metadata only, not resolved |

---

## 8. Acceptance Criteria

- [ ] `get_builtin_profile("lint")` returns a `ValidationProfile` with `max_validation_level=1`, `enabled_stages=[1, 2]`
- [ ] `get_builtin_profile("ci")` returns a profile with `pass_threshold=50`, `output_format="json"`
- [ ] `get_builtin_profile("full")` returns a profile with `max_validation_level=4`, all stages, no threshold
- [ ] `get_builtin_profile("enterprise")` returns a profile with `output_tier=4`, `output_format="html"`, `extends="full"`
- [ ] `get_builtin_profile("unknown")` raises `ValueError` listing available profiles
- [ ] `list_builtin_profiles()` returns `["ci", "enterprise", "full", "lint"]`
- [ ] `is_builtin_profile("ci")` returns `True`
- [ ] `is_builtin_profile("custom")` returns `False`
- [ ] `get_default_profile()` returns the `ci` profile
- [ ] `DEFAULT_PROFILE_NAME` is `"ci"`
- [ ] All 4 profile constants are valid `ValidationProfile` instances (Pydantic validation passes)
- [ ] All profile constants are accessible via `from docstratum.profiles import PROFILE_LINT` etc.
- [ ] The `enterprise` profile has `extends="full"` set (even though inheritance is not resolved at v0.5.1b)
- [ ] Module docstring cites v0.5.1b and grounding spec
- [ ] All public functions have Google-style docstrings

---

## 9. Deliverables

| File | Description | Status |
|------|-------------|--------|
| `src/docstratum/profiles/builtins.py` | 4 built-in profile definitions + lookup API | NEW |
| `src/docstratum/profiles/__init__.py` | Updated to re-export built-in functions and constants | MODIFY |
| `src/docstratum/cli.py` | Update `validate_command()` to use profile lookup | MODIFY |
| `tests/test_builtin_profiles.py` | Unit tests for built-in profiles | NEW |

---

## 10. Test Plan (16 tests)

| # | Test Name | Input | Expected |
|---|-----------|-------|----------|
| 1 | `test_lint_profile_values` | `get_builtin_profile("lint")` | `max_level=1, stages=[1,2], format="terminal"` |
| 2 | `test_ci_profile_values` | `get_builtin_profile("ci")` | `max_level=3, threshold=50, format="json"` |
| 3 | `test_full_profile_values` | `get_builtin_profile("full")` | `max_level=4, stages=[1..6], format="markdown"` |
| 4 | `test_enterprise_profile_values` | `get_builtin_profile("enterprise")` | `tier=4, format="html", extends="full"` |
| 5 | `test_lookup_unknown_raises` | `get_builtin_profile("unknown")` | `ValueError` with available list |
| 6 | `test_lookup_case_sensitive` | `get_builtin_profile("CI")` | `ValueError` |
| 7 | `test_lookup_empty_name` | `get_builtin_profile("")` | `ValueError` |
| 8 | `test_list_builtin_profiles` | `list_builtin_profiles()` | `["ci", "enterprise", "full", "lint"]` |
| 9 | `test_is_builtin_known` | `is_builtin_profile("ci")` | `True` |
| 10 | `test_is_builtin_unknown` | `is_builtin_profile("custom")` | `False` |
| 11 | `test_get_default_profile` | `get_default_profile()` | Returns ci profile |
| 12 | `test_all_profiles_valid` | Iterate all built-ins | All are valid `ValidationProfile` instances |
| 13 | `test_ci_excludes_experimental` | `PROFILE_CI.rule_tags_exclude` | Contains `"experimental"` |
| 14 | `test_lint_no_threshold` | `PROFILE_LINT.pass_threshold` | `None` |
| 15 | `test_full_all_stages` | `PROFILE_FULL.enabled_stages` | `[1, 2, 3, 4, 5, 6]` |
| 16 | `test_enterprise_extends_full` | `PROFILE_ENTERPRISE.extends` | `"full"` |

```python
"""Tests for v0.5.1b — Built-in Profiles.

Validates the 4 built-in profile definitions, lookup API,
and profile field values.
"""

import pytest

from docstratum.profiles.builtins import (
    PROFILE_CI,
    PROFILE_ENTERPRISE,
    PROFILE_FULL,
    PROFILE_LINT,
    DEFAULT_PROFILE_NAME,
    get_builtin_profile,
    get_default_profile,
    is_builtin_profile,
    list_builtin_profiles,
)
from docstratum.profiles.model import ValidationProfile


class TestProfileValues:
    """Test that each built-in profile has the correct field values."""

    def test_lint_profile_values(self):
        profile = get_builtin_profile("lint")
        assert profile.profile_name == "lint"
        assert profile.max_validation_level == 1
        assert profile.enabled_stages == [1, 2]
        assert profile.rule_tags_include == ["structural"]
        assert profile.rule_tags_exclude == []
        assert profile.pass_threshold is None
        assert profile.output_tier == 2
        assert profile.output_format == "terminal"

    def test_ci_profile_values(self):
        profile = get_builtin_profile("ci")
        assert profile.profile_name == "ci"
        assert profile.max_validation_level == 3
        assert profile.enabled_stages == [1, 2, 3, 4, 5]
        assert "structural" in profile.rule_tags_include
        assert "experimental" in profile.rule_tags_exclude
        assert profile.pass_threshold == 50
        assert profile.output_tier == 1
        assert profile.output_format == "json"

    def test_full_profile_values(self):
        profile = get_builtin_profile("full")
        assert profile.max_validation_level == 4
        assert profile.enabled_stages == [1, 2, 3, 4, 5, 6]
        assert profile.rule_tags_include == []
        assert profile.rule_tags_exclude == []
        assert profile.pass_threshold is None
        assert profile.output_tier == 3
        assert profile.output_format == "markdown"

    def test_enterprise_profile_values(self):
        profile = get_builtin_profile("enterprise")
        assert profile.output_tier == 4
        assert profile.output_format == "html"
        assert profile.extends == "full"


class TestLookupAPI:
    """Test the profile lookup functions."""

    def test_lookup_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown built-in profile"):
            get_builtin_profile("unknown")

    def test_list_builtin_profiles(self):
        names = list_builtin_profiles()
        assert names == ["ci", "enterprise", "full", "lint"]

    def test_is_builtin_known(self):
        assert is_builtin_profile("ci") is True

    def test_is_builtin_unknown(self):
        assert is_builtin_profile("custom") is False

    def test_get_default_profile(self):
        profile = get_default_profile()
        assert profile.profile_name == "ci"

    def test_all_profiles_are_valid(self):
        """Every built-in must be a valid ValidationProfile."""
        for name in list_builtin_profiles():
            profile = get_builtin_profile(name)
            assert isinstance(profile, ValidationProfile)
```

---

## 11. Limitations

| Limitation | Impact | Resolution |
|------------|--------|------------|
| Only 4 profiles available | Users cannot define custom profiles | v0.5.2a (Profile Loading) |
| `enterprise.extends` is not resolved | The `extends="full"` is metadata, not functional inheritance | v0.5.1d (Inheritance) |
| Names are case-sensitive | `"CI"` doesn't match `"ci"` | By design; case-insensitive lookup adds ambiguity |
| File paths rejected | `get_builtin_profile("./ci.yaml")` raises ValueError | v0.5.2b (Discovery Precedence) |
| Profiles are snapshots | Changing a profile constant requires a code release | By design; user customization via YAML in v0.5.2 |
