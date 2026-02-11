# v0.5.2c — CLI Override Integration

> **Version:** v0.5.2c
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.5.2-discovery-and-configuration.md](RR-SPEC-v0.5.2-discovery-and-configuration.md)
> **Grounding:** RR-SPEC-v0.1.3-validation-profiles.md §5.5 (CLI Flag Composition), DECISION-032 (Shallow Overrides)
> **Depends On:** v0.5.0b (`CliArgs` — parsed CLI arguments), v0.5.2b (`discover_profile` — loaded profile), v0.5.1a (`ValidationProfile` model)
> **Module:** `src/docstratum/profiles/overrides.py`
> **Tests:** `tests/test_profile_overrides.py`

---

## 1. Purpose

Implement the final step in the profile resolution pipeline: merging CLI flag values into the loaded profile. When a user runs `docstratum validate llms.txt --profile ci --max-level 2`, the `ci` profile is loaded (via v0.5.2b) with `max_validation_level=3`, then this module overrides it to `max_validation_level=2` because the CLI flag was explicitly provided.

The merge uses **Replace semantics** (DECISION-032): each CLI flag replaces the profile's corresponding field entirely. There is no deep merging — `--tags structural` replaces the profile's `rule_tags_include` list, it does not append to it.

After v0.5.2c:

```bash
# Profile ci: max_validation_level=3, rule_tags_include=["structural","content","ecosystem"]
docstratum validate llms.txt --profile ci --max-level 2 --tags structural

# Result: max_validation_level=2, rule_tags_include=["structural"]
# Other ci fields unchanged: pass_threshold=50, output_format="json", etc.
```

### 1.1 User Stories

> **US-1:** As a developer, I want `--max-level 2` to temporarily lower the validation level without editing my profile file, so that I can get fast feedback during iterative editing.

> **US-2:** As a CI engineer, I want `--pass-threshold 80` to raise the threshold above the profile's default, so that I can enforce stricter quality gates for critical releases.

> **US-3:** As a developer who passes `--output-format json` without `--profile`, I want the default profile loaded and the format overridden, so that I can get machine-readable output without knowing which profile is active.

> **US-4:** As a developer who passes only `--max-level 2` with no `--profile`, I want the default profile's level overridden — creating an "inline profile" — rather than getting an error about missing profile.

---

## 2. Override Mapping

### 2.1 CLI Flag → Profile Field Mapping

| CLI Flag | CLI Arg Name | Profile Field | Type | Merge Behavior |
|----------|-------------|---------------|------|----------------|
| `--max-level` | `max_level` | `max_validation_level` | `int (0-4)` | Replace |
| `--tags` | `tags` | `rule_tags_include` | `list[str]` | Replace |
| `--exclude-tags` | `exclude_tags` | `rule_tags_exclude` | `list[str]` | Replace |
| `--output-tier` | `output_tier` | `output_tier` | `int (1-4)` | Replace |
| `--output-format` | `output_format` | `output_format` | `str` | Replace |
| `--pass-threshold` | `pass_threshold` | `pass_threshold` | `int (0-100)` | Replace |

### 2.2 Non-Mapped Flags

These CLI flags are NOT mapped to profile fields — they affect CLI behavior directly:

| CLI Flag | Effect | Why Not Mapped |
|----------|--------|---------------|
| `--profile` | Triggers profile discovery (v0.5.2b) | Not a profile *field* — it's a profile *selector* |
| `--check-urls` | Convenience flag for tag filtering | Maps to tag include/exclude, not a direct field (see §3.3) |
| `--strict` | Affects exit code logic (v0.5.0c) | CLI execution concern, not profile concern |
| `--verbose` | Affects terminal output (v0.5.0d) | CLI display concern, not profile concern |
| `--quiet` | Suppresses output (v0.5.0d) | CLI display concern, not profile concern |
| `--version` | Prints version and exits | Not a validation concern |
| `path` | Input file/directory | Not a profile concern |

### 2.3 Replace Semantics (DECISION-032)

**Replace, not merge.** When a CLI flag is provided:

```python
# Profile: rule_tags_include=["structural", "content", "ecosystem"]
# CLI:     --tags structural

# RESULT: rule_tags_include=["structural"]
# NOT:    rule_tags_include=["structural", "content", "ecosystem", "structural"]
```

This is intentional. Replace semantics are simpler to reason about: `--tags structural` means "only structural rules", not "add structural to whatever the profile says."

### 2.4 None = Don't Override

CLI arguments that are `None` (not provided by the user) are **not applied**. This is the core convention from v0.5.0b:

```python
# CliArgs after parsing "docstratum validate llms.txt --max-level 2":
args.max_level = 2           # User provided → override
args.tags = None             # Not provided → keep profile's value
args.output_format = None    # Not provided → keep profile's value
```

---

## 3. Implementation

### 3.1 Override Function

```python
# src/docstratum/profiles/overrides.py
"""CLI override merging — applies CLI flag values on top of loaded profiles.

Implements v0.5.2c.
Grounding: RR-SPEC-v0.1.3-validation-profiles.md §5.5.
DECISION-032: Shallow override semantics (Replace, not merge).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Optional

from docstratum.profiles.model import ValidationProfile

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OverrideResult:
    """Result of CLI override merging.

    Attributes:
        profile: The profile with overrides applied.
        overrides_applied: List of (field_name, old_value, new_value) tuples
            for each field that was overridden.
        is_inline: True if no --profile flag was provided but CLI flags
            modified the default profile.
    """
    profile: ValidationProfile
    overrides_applied: list[tuple[str, Any, Any]]
    is_inline: bool


# --- Override mapping registry ---
# Maps CLI argument names (from CliArgs) to profile field names.
# DECISION-032: All overrides use Replace semantics.

_CLI_TO_PROFILE_MAPPING: dict[str, str] = {
    "max_level": "max_validation_level",
    "tags": "rule_tags_include",
    "exclude_tags": "rule_tags_exclude",
    "output_tier": "output_tier",
    "output_format": "output_format",
    "pass_threshold": "pass_threshold",
}


def merge_cli_overrides(
    profile: ValidationProfile,
    cli_args: Any,
    *,
    is_inline: bool = False,
) -> OverrideResult:
    """Apply CLI flag overrides to a loaded profile.

    For each CLI argument that is not None, replaces the corresponding
    profile field. Arguments that are None are skipped (profile's
    value is preserved).

    Args:
        profile: The loaded ValidationProfile to modify.
        cli_args: The parsed CLI arguments (CliArgs namespace from v0.5.0b).
            Must have attributes matching _CLI_TO_PROFILE_MAPPING keys.
        is_inline: Set to True when no --profile flag was provided.
            When True and overrides are applied, the result is logged
            as an "inline profile".

    Returns:
        OverrideResult with the modified profile, applied overrides,
        and inline flag.

    Example:
        >>> from docstratum.profiles.builtins import get_builtin_profile
        >>> ci = get_builtin_profile("ci")
        >>> ci.max_validation_level
        3
        >>> # Simulate CliArgs with max_level=2
        >>> class Args:
        ...     max_level = 2
        ...     tags = None
        ...     exclude_tags = None
        ...     output_tier = None
        ...     output_format = None
        ...     pass_threshold = None
        >>> result = merge_cli_overrides(ci, Args())
        >>> result.profile.max_validation_level
        2
        >>> result.overrides_applied
        [('max_validation_level', 3, 2)]

    Grounding: RR-SPEC-v0.1.3-validation-profiles.md §5.5.
    Implements v0.5.2c.
    """
    overrides: list[tuple[str, Any, Any]] = []
    updates: dict[str, Any] = {}

    for cli_attr, profile_field in _CLI_TO_PROFILE_MAPPING.items():
        cli_value = getattr(cli_args, cli_attr, None)
        if cli_value is not None:
            old_value = getattr(profile, profile_field)
            updates[profile_field] = cli_value
            overrides.append((profile_field, old_value, cli_value))
            logger.info(
                "CLI override: %s = %r → %r (was %r)",
                profile_field,
                cli_value,
                cli_value,
                old_value,
            )

    # Handle --check-urls convenience flag
    if getattr(cli_args, "check_urls", False):
        overrides_applied_for_urls = _apply_check_urls_flag(
            profile, updates
        )
        overrides.extend(overrides_applied_for_urls)

    # Apply overrides
    if updates:
        # Create a new profile with the overridden fields
        profile_dict = profile.model_dump()
        profile_dict.update(updates)
        merged_profile = ValidationProfile(**profile_dict)

        if is_inline and overrides:
            logger.info(
                "Inline profile created: default '%s' + %d CLI override(s).",
                profile.profile_name,
                len(overrides),
            )
    else:
        merged_profile = profile
        logger.debug("No CLI overrides applied.")

    return OverrideResult(
        profile=merged_profile,
        overrides_applied=overrides,
        is_inline=is_inline and bool(overrides),
    )


def _apply_check_urls_flag(
    profile: ValidationProfile,
    updates: dict[str, Any],
) -> list[tuple[str, Any, Any]]:
    """Handle the --check-urls convenience flag.

    --check-urls maps to tag inclusion of "url-reachability" rules.
    Without --check-urls, the profile's existing tag configuration
    is preserved.

    Returns:
        List of (field_name, old_value, new_value) override tuples.
    """
    check_urls_overrides: list[tuple[str, Any, Any]] = []

    # If rule_tags_exclude already excludes url rules, remove them
    current_excludes = updates.get(
        "rule_tags_exclude",
        list(profile.rule_tags_exclude),
    )

    if "url-reachability" in current_excludes:
        new_excludes = [t for t in current_excludes if t != "url-reachability"]
        old_excludes = list(profile.rule_tags_exclude)
        updates["rule_tags_exclude"] = new_excludes
        check_urls_overrides.append(
            ("rule_tags_exclude", old_excludes, new_excludes)
        )
        logger.info(
            "CLI --check-urls: removed 'url-reachability' from "
            "rule_tags_exclude."
        )

    # If rule_tags_include is in use and doesn't include url rules, add them
    current_includes = updates.get(
        "rule_tags_include",
        list(profile.rule_tags_include),
    )
    if current_includes and "url-reachability" not in current_includes:
        old_includes = list(profile.rule_tags_include)
        new_includes = current_includes + ["url-reachability"]
        updates["rule_tags_include"] = new_includes
        check_urls_overrides.append(
            ("rule_tags_include", old_includes, new_includes)
        )
        logger.info(
            "CLI --check-urls: added 'url-reachability' to "
            "rule_tags_include."
        )

    return check_urls_overrides
```

### 3.2 CLI Integration Point

```python
# In cli.py — validate_command() (modified in v0.5.2):
from docstratum.profiles.discovery import discover_profile
from docstratum.profiles.overrides import merge_cli_overrides

def validate_command(args):
    """Execute the validate subcommand.

    Profile resolution pipeline:
    1. Discover profile (v0.5.2b)
    2. Merge CLI overrides (v0.5.2c)
    3. Inject into PipelineContext

    Implements v0.5.2c integration.
    """
    # Step 1: Discover profile
    is_inline = args.profile is None
    profile, source = discover_profile(args.profile)

    # Step 2: Merge CLI overrides
    result = merge_cli_overrides(
        profile, args, is_inline=is_inline
    )

    # Step 3: Use resolved profile
    pipeline_profile = result.profile

    # Log override summary
    if result.overrides_applied:
        for field, old, new in result.overrides_applied:
            click.echo(
                f"   override: {field} = {new!r} (profile had: {old!r})",
                err=True,
            )

    # ... pipeline execution continues with pipeline_profile ...
```

### 3.3 Inline Profile Concept

When the user provides CLI flags but no `--profile`, an **inline profile** is created. This is the "anonymous profile" described in the SCOPE:

```bash
# No --profile → default "ci" loaded
# --max-level 2 + --output-format markdown → inline profile
docstratum validate llms.txt --max-level 2 --output-format markdown
```

The inline profile inherits all fields from the default profile (resolved by v0.5.2b) with the specified overrides applied. It is functionally identical to:

```yaml
# Anonymous equivalent profile
profile_name: "ci"  # inherited from default
max_validation_level: 2  # overridden by --max-level
output_format: "markdown"  # overridden by --output-format
# all other fields from "ci"
```

The terminal output header should reflect this:

```
DocStratum v0.1.0 | Profile: ci (inline, 2 overrides) | 2026-02-10 14:30:00
```

### 3.4 Package Re-exports

```python
# Update src/docstratum/profiles/__init__.py
from docstratum.profiles.overrides import (
    OverrideResult,
    merge_cli_overrides,
)

# Add to __all__:
__all__ = [
    # ... existing exports ...
    "OverrideResult",
    "merge_cli_overrides",
]
```

---

## 4. Decision Tree: Override Resolution

```
Input: profile (ValidationProfile), cli_args (CliArgs)
│
├── For each mapped CLI flag:
│   ├── max_level → max_validation_level
│   ├── tags → rule_tags_include
│   ├── exclude_tags → rule_tags_exclude
│   ├── output_tier → output_tier
│   ├── output_format → output_format
│   └── pass_threshold → pass_threshold
│
├── For each flag:
│   ├── Value is None?
│   │   └── YES → Skip (keep profile's value)
│   └── Value is not None?
│       └── REPLACE profile field with CLI value
│           Log: "CLI override: <field> = <new> (was <old>)"
│
├── --check-urls flag set?
│   └── YES → Adjust tag lists:
│       ├── Remove "url-reachability" from rule_tags_exclude
│       └── Add "url-reachability" to rule_tags_include (if non-empty)
│
├── Any overrides applied?
│   ├── YES → Construct new ValidationProfile with updates
│   │         Return OverrideResult(profile, overrides, is_inline)
│   └── NO → Return original profile unchanged
│
└── Output: OverrideResult
```

---

## 5. Workflow

### 5.1 Basic Override

```python
from docstratum.profiles.builtins import get_builtin_profile
from docstratum.profiles.overrides import merge_cli_overrides

# Load ci profile
ci = get_builtin_profile("ci")
assert ci.max_validation_level == 3
assert ci.rule_tags_include == ["structural", "content", "ecosystem"]
assert ci.pass_threshold == 50

# Simulate CLI args
class MockArgs:
    max_level = 2                  # Override
    tags = ["structural"]          # Override (Replace)
    exclude_tags = None            # Don't override
    output_tier = None             # Don't override
    output_format = None           # Don't override
    pass_threshold = 80            # Override
    check_urls = False

result = merge_cli_overrides(ci, MockArgs())

assert result.profile.max_validation_level == 2   # overridden
assert result.profile.rule_tags_include == ["structural"]  # replaced
assert result.profile.pass_threshold == 80         # overridden
assert result.profile.output_format == "json"      # kept from ci
assert result.profile.output_tier == 1             # kept from ci
assert len(result.overrides_applied) == 3
```

### 5.2 No Overrides (All Flags None)

```python
class NoOverrideArgs:
    max_level = None
    tags = None
    exclude_tags = None
    output_tier = None
    output_format = None
    pass_threshold = None
    check_urls = False

result = merge_cli_overrides(ci, NoOverrideArgs())

assert result.profile is ci  # same object, no copy
assert result.overrides_applied == []
assert result.is_inline is False
```

### 5.3 Inline Profile

```python
result = merge_cli_overrides(
    ci, MockArgs(), is_inline=True
)

assert result.is_inline is True  # CLI flags but no --profile
assert result.overrides_applied  # overrides were applied
```

### 5.4 --check-urls Flag

```python
class CheckUrlArgs:
    max_level = None
    tags = None
    exclude_tags = None
    output_tier = None
    output_format = None
    pass_threshold = None
    check_urls = True  # Convenience flag

# ci profile excludes "experimental" but not "url-reachability"
result = merge_cli_overrides(ci, CheckUrlArgs())
# If ci has non-empty rule_tags_include and url-reachability
# wasn't already there, it gets added
```

---

## 6. Edge Cases

| Scenario | Input | Behavior |
|----------|-------|----------|
| All flags None | No CLI flags provided | Profile returned unchanged |
| Single flag override | `--max-level 0` | Only `max_validation_level` overridden |
| All flags set | Every flag provided | All 6 profile fields overridden |
| Tags empty list | `--tags ""` (empty) | `rule_tags_include = []` (include all) |
| Tags single item | `--tags structural` | `rule_tags_include = ["structural"]` |
| Tags multiple items | `--tags structural,content` | `rule_tags_include = ["structural", "content"]` |
| Override to same value | `--max-level 3` on ci (already 3) | Override logged but value unchanged |
| Override threshold to None | Cannot — threshold is an int argument | Profile's threshold preserved |
| `--check-urls` + explicit tags | Both provided | Tags override first, then check-urls adjusts |
| `is_inline=True` but no overrides | No CLI flags, no --profile | `is_inline=False` (no overrides = not inline) |
| Profile is frozen/immutable | If future DECISION changes mutability | New profile instance created (model_dump + reconstruct) |
| CliArgs missing attribute | `getattr` returns None | No override applied for that flag |
| Override produces invalid profile | `--max-level 99` | Caught by v0.5.0b's click.IntRange(0,4) before reaching overrides |

**Note on validation order:** CLI argument validation happens at parse time (v0.5.0b), not at override time. The `IntRange(0, 4)` constraint on `--max-level` is enforced by `click` before the value reaches `merge_cli_overrides()`. Therefore, this module does NOT need to re-validate range constraints — it trusts the parsed values.

---

## 7. Acceptance Criteria

- [ ] `merge_cli_overrides()` replaces `max_validation_level` when `max_level` is not None
- [ ] `merge_cli_overrides()` replaces `rule_tags_include` when `tags` is not None
- [ ] `merge_cli_overrides()` replaces `rule_tags_exclude` when `exclude_tags` is not None
- [ ] `merge_cli_overrides()` replaces `output_tier` when `output_tier` is not None
- [ ] `merge_cli_overrides()` replaces `output_format` when `output_format` is not None
- [ ] `merge_cli_overrides()` replaces `pass_threshold` when `pass_threshold` is not None
- [ ] CLI flags that are `None` do not override the profile's value
- [ ] `merge_cli_overrides()` returns the original profile object when no overrides are applied
- [ ] `OverrideResult.overrides_applied` lists all (field, old, new) tuples
- [ ] `OverrideResult.is_inline` is True when `is_inline=True` and overrides are applied
- [ ] `OverrideResult.is_inline` is False when `is_inline=True` but no overrides are applied
- [ ] `--check-urls` removes `url-reachability` from exclude list
- [ ] `--check-urls` adds `url-reachability` to include list (when non-empty)
- [ ] Replace semantics: `--tags structural` replaces `["structural", "content"]` with `["structural"]`
- [ ] Override logging includes field name, old value, and new value
- [ ] Module docstring cites v0.5.2c and DECISION-032
- [ ] All public functions have Google-style docstrings

---

## 8. Deliverables

| File | Description | Status |
|------|-------------|--------|
| `src/docstratum/profiles/overrides.py` | CLI override merging | NEW |
| `src/docstratum/profiles/__init__.py` | Updated to re-export override functions | MODIFY |
| `src/docstratum/cli.py` | Updated `validate_command()` to use override pipeline | MODIFY |
| `tests/test_profile_overrides.py` | Unit tests | NEW |

---

## 9. Test Plan (18 tests)

### 9.1 Individual Override Tests

| # | Test Name | CLI Flag | Expected |
|---|-----------|----------|----------|
| 1 | `test_override_max_level` | `max_level=2` | `max_validation_level` = 2 |
| 2 | `test_override_tags` | `tags=["structural"]` | `rule_tags_include` = ["structural"] |
| 3 | `test_override_exclude_tags` | `exclude_tags=["experimental"]` | `rule_tags_exclude` = ["experimental"] |
| 4 | `test_override_output_tier` | `output_tier=3` | `output_tier` = 3 |
| 5 | `test_override_output_format` | `output_format="markdown"` | `output_format` = "markdown" |
| 6 | `test_override_pass_threshold` | `pass_threshold=80` | `pass_threshold` = 80 |

### 9.2 None-Passthrough Tests

| # | Test Name | Setup | Expected |
|---|-----------|-------|----------|
| 7 | `test_none_flags_no_override` | All flags None | Profile unchanged, `overrides_applied=[]` |
| 8 | `test_none_preserves_value` | `max_level=None` on ci | `max_validation_level` stays 3 |
| 9 | `test_original_returned_when_no_changes` | All None | Same profile object returned |

### 9.3 Replace Semantics Tests

| # | Test Name | Setup | Expected |
|---|-----------|-------|----------|
| 10 | `test_tags_replace_not_append` | ci has 3 tags, `tags=["structural"]` | Only `["structural"]` |
| 11 | `test_tags_empty_replaces` | ci has 3 tags, `tags=[]` | Include all (empty) |

### 9.4 --check-urls Tests

| # | Test Name | Setup | Expected |
|---|-----------|-------|----------|
| 12 | `test_check_urls_adds_include` | Non-empty includes, `check_urls=True` | `url-reachability` added |
| 13 | `test_check_urls_removes_exclude` | `url-reachability` in excludes | Removed from excludes |
| 14 | `test_check_urls_noop_if_empty_includes` | Empty includes, `check_urls=True` | All rules included anyway |

### 9.5 Inline Profile Tests

| # | Test Name | Setup | Expected |
|---|-----------|-------|----------|
| 15 | `test_inline_with_overrides` | `is_inline=True`, overrides applied | `is_inline=True` |
| 16 | `test_inline_no_overrides` | `is_inline=True`, no overrides | `is_inline=False` |

### 9.6 Integration Tests

| # | Test Name | Setup | Expected |
|---|-----------|-------|----------|
| 17 | `test_multiple_overrides` | 3 flags set | All 3 fields overridden |
| 18 | `test_override_result_logging` | Override applied | Log message includes field/value |

```python
"""Tests for v0.5.2c — CLI Override Integration.

Validates Replace semantics, None passthrough, inline profiles,
--check-urls mapping, and override result tracking.
"""

import pytest

from docstratum.profiles.builtins import get_builtin_profile
from docstratum.profiles.overrides import merge_cli_overrides, OverrideResult


class MockArgs:
    """Mock CliArgs for testing."""
    def __init__(self, **kwargs):
        self.max_level = kwargs.get("max_level")
        self.tags = kwargs.get("tags")
        self.exclude_tags = kwargs.get("exclude_tags")
        self.output_tier = kwargs.get("output_tier")
        self.output_format = kwargs.get("output_format")
        self.pass_threshold = kwargs.get("pass_threshold")
        self.check_urls = kwargs.get("check_urls", False)


class TestIndividualOverrides:
    """Test each CLI flag override individually."""

    def test_override_max_level(self):
        ci = get_builtin_profile("ci")
        result = merge_cli_overrides(ci, MockArgs(max_level=2))
        assert result.profile.max_validation_level == 2
        assert len(result.overrides_applied) == 1
        assert result.overrides_applied[0] == (
            "max_validation_level", 3, 2
        )

    def test_override_tags_replace(self):
        ci = get_builtin_profile("ci")
        original_tags = list(ci.rule_tags_include)
        assert len(original_tags) > 1  # ci has multiple tags

        result = merge_cli_overrides(
            ci, MockArgs(tags=["structural"])
        )
        assert result.profile.rule_tags_include == ["structural"]

    def test_override_pass_threshold(self):
        ci = get_builtin_profile("ci")
        result = merge_cli_overrides(
            ci, MockArgs(pass_threshold=80)
        )
        assert result.profile.pass_threshold == 80


class TestNonePassthrough:
    """Test that None values don't override profile fields."""

    def test_all_none(self):
        ci = get_builtin_profile("ci")
        result = merge_cli_overrides(ci, MockArgs())
        assert result.profile is ci  # Same object
        assert result.overrides_applied == []

    def test_none_preserves_value(self):
        ci = get_builtin_profile("ci")
        result = merge_cli_overrides(ci, MockArgs())
        assert result.profile.max_validation_level == 3


class TestInlineProfile:
    """Test inline profile tracking."""

    def test_inline_with_overrides(self):
        ci = get_builtin_profile("ci")
        result = merge_cli_overrides(
            ci, MockArgs(max_level=2), is_inline=True
        )
        assert result.is_inline is True

    def test_inline_no_overrides(self):
        ci = get_builtin_profile("ci")
        result = merge_cli_overrides(
            ci, MockArgs(), is_inline=True
        )
        assert result.is_inline is False
```

---

## 10. Limitations

| Limitation | Impact | Resolution |
|------------|--------|------------|
| No deep merge for dicts | Cannot override single `severity_overrides` entry from CLI | By design (DECISION-032). Write a profile file for complex overrides. |
| No `--enabled-stages` flag | Cannot override enabled stages from CLI | Not in v0.5.0b argument schema. Future consideration. |
| No `--grouping-mode` flag | Cannot override grouping from CLI | Not in v0.5.0b argument schema. |
| No `--severity-override` flag | Cannot add severity overrides from CLI | Complex dict; use profile files. |
| No `--priority-override` flag | Cannot add priority overrides from CLI | Complex dict; use profile files. |
| `--check-urls` tag name is provisional | `"url-reachability"` may change when Rule Registry is built | Updated in Deliverable 3 mapping. |
| No undo/reset | Cannot reset a profile field to its default from CLI | Use a different profile or explicit value. |
