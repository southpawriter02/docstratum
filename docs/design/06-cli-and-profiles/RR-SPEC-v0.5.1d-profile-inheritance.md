# v0.5.1d — Profile Inheritance

> **Version:** v0.5.1d
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.5.1-validation-profiles.md](RR-SPEC-v0.5.1-validation-profiles.md)
> **Grounding:** RR-SPEC-v0.1.3-validation-profiles.md §4.6 (Inheritance), DECISION-031 (single-level only)
> **Depends On:** v0.5.1a (`ValidationProfile` model), v0.5.1b (`get_builtin_profile` for base lookup)
> **Cross-Version Dependency:** v0.5.2b (Discovery Precedence) — resolved via callback injection
> **Module:** `src/docstratum/profiles/inheritance.py`
> **Tests:** `tests/test_profile_inheritance.py`

---

## 1. Purpose

Implement the single-level `extends` field that allows a child profile to inherit from a base profile. Profile inheritance is a convenience mechanism: a team that wants "the `full` profile but with HTML output" defines a minimal child profile that sets `extends="full"` and overrides only `output_format="html"` and `output_tier=4`, rather than duplicating the entire `full` configuration.

After v0.5.1d:

```python
from docstratum.profiles.inheritance import resolve_inheritance
from docstratum.profiles import get_builtin_profile

child = ValidationProfile(
    profile_name="html-full",
    description="Full analysis with HTML output",
    output_tier=4,
    output_format="html",
    extends="full",
)

resolved = resolve_inheritance(
    child=child,
    profile_resolver=get_builtin_profile,
    source_keys={"profile_name", "description", "output_tier", "output_format", "extends"},
)

# resolved has full's settings + child's overrides
assert resolved.max_validation_level == 4  # inherited from full
assert resolved.output_format == "html"    # child override
assert resolved.extends is None            # flattened — no extends reference
```

### 1.1 User Stories

> **US-1:** As a team with custom output needs, I want to create a profile that extends `full` with only 2–3 field overrides, so that I don't have to duplicate 10+ fields from the base profile.

> **US-2:** As a profile loader, I need inheritance to be resolved at load time (flattened) so that the rest of the pipeline operates on a complete profile with no unresolved references.

> **US-3:** As a developer, I want clear error messages when profile inheritance creates circular or multi-level chains, so that I can fix my profile configuration quickly.

---

## 2. Inheritance Rules

### 2.1 Resolution Algorithm

```
Input:  child_profile (ValidationProfile with extends set)
        profile_resolver (Callable[[str], ValidationProfile])
        source_keys (set[str] | None — keys explicitly set in child's source)
Output: resolved_profile (ValidationProfile with extends=None)

1. If child.extends is None → return child (no inheritance to resolve)

2. Load the base profile:
   base = profile_resolver(child.extends)
   If ValueError → raise InheritanceError("Base profile '{name}' not found")

3. Check for multi-level inheritance (DECISION-031):
   If base.extends is not None:
     raise InheritanceError(
       "Multi-level inheritance is not supported. "
       "Profile '{child.profile_name}' extends '{child.extends}', "
       "which itself extends '{base.extends}'. "
       "Maximum inheritance depth is 1."
     )

4. Build the resolved field set:
   For each field in ValidationProfile:
     If field is in source_keys (explicitly set by child):
       resolved[field] = child's value
     Else:
       resolved[field] = base's value

5. Override metadata:
   resolved.profile_name = child.profile_name  (always child's)
   resolved.description = child.description     (always child's)
   resolved.extends = None                      (flattened)

6. Construct and validate:
   resolved_profile = ValidationProfile(**resolved_fields)
   → Pydantic validates the resolved profile
   → Return resolved_profile
```

### 2.2 The "Explicitly Set" Problem

The key challenge is step 4: distinguishing "the child explicitly set `max_validation_level=4`" from "the child didn't specify `max_validation_level`, so it defaulted to 4."

Consider this child profile defined in YAML:

```yaml
# custom.yaml
profile_name: "html-full"
description: "Full analysis with HTML output"
output_format: "html"
output_tier: 4
extends: "full"
```

The YAML has 5 keys: `profile_name`, `description`, `output_format`, `output_tier`, `extends`. It does NOT set `max_validation_level`, `enabled_stages`, `pass_threshold`, etc. — those should be inherited from `full`.

But when loaded into a `ValidationProfile` Pydantic model, ALL fields have values (defaults fill in). There's no way to tell from the model alone that `max_validation_level=4` came from a default vs. an explicit YAML key.

**DECISION-039: Use `source_keys` to track explicitly-set fields.**

The profile loader (v0.5.2a) is responsible for tracking which YAML/JSON keys were present in the source file. This set of key names is passed to `resolve_inheritance()` as `source_keys`. Fields in `source_keys` are child overrides; fields NOT in `source_keys` are inherited from the base.

**Why not sentinel values?** Sentinel values (e.g., `UNSET = object()`) would require every field to have `Optional[UNSET | actual_type]`, complicating the Pydantic model and breaking type hints. The `source_keys` approach keeps the model clean.

**Why not read raw YAML?** The inheritance resolver should not re-parse YAML. It receives a `ValidationProfile` and a `source_keys` set — both constructed by the loader. This keeps concerns separated.

**Fallback when `source_keys` is None:** If `source_keys` is not provided (e.g., when resolving built-in profiles programmatically), ALL non-default fields of the child are treated as overrides. This uses Pydantic's ability to detect non-default values by comparing against a default-constructed instance:

```python
# Fallback for programmatic resolution (no source_keys)
default_profile = ValidationProfile(profile_name="_default")
child_overrides = {
    field_name
    for field_name in child.model_fields
    if getattr(child, field_name) != getattr(default_profile, field_name)
}
```

This fallback is less precise (a child that explicitly sets a field to its default value won't be detected as an override), but it's sufficient for programmatic use cases.

### 2.3 Restrictions

**Single Level Only (DECISION-031):**
- If the base profile has `extends` set (is not None), inheritance is rejected.
- No chaining: `enterprise → full → ci` is not allowed.
- Rationale: Multi-level inheritance creates debugging complexity ("where did this value come from?"). Single-level keeps the resolution transparent.

**No Circular Inheritance:**
- If profile A extends B and profile B extends A, report an error at resolution time.
- With single-level restriction, true circular references are impossible (A extends B, B has extends set → B is rejected as a base). However, the check is retained as a defensive guard.

**Base Must Exist:**
- If `profile_resolver(child.extends)` raises `ValueError`, the inheritance resolver converts it to a descriptive `InheritanceError`.

---

## 3. Implementation

### 3.1 Errors

```python
# src/docstratum/profiles/inheritance.py
"""Single-level profile inheritance resolver.

Implements the `extends` field: loads a base profile, merges child
overrides, and produces a flattened ValidationProfile with no
unresolved references.

Implements v0.5.1d.
Grounding: RR-SPEC-v0.1.3-validation-profiles.md §4.6.
DECISION-031: Single-level only (no chaining).
DECISION-039: source_keys for explicit field tracking.
"""

from __future__ import annotations

import logging
from typing import Callable, Optional

from docstratum.profiles.model import ValidationProfile

logger = logging.getLogger(__name__)


class InheritanceError(ValueError):
    """Raised when profile inheritance resolution fails.

    Possible causes:
    - Base profile not found
    - Multi-level inheritance detected (base has extends set)
    - Circular inheritance detected
    - Profile validation error after resolution
    """
    pass
```

### 3.2 Resolution Function

```python
# Metadata fields that always come from the child, never inherited
_CHILD_ONLY_FIELDS: frozenset[str] = frozenset({
    "profile_name",
    "description",
    "extends",
})


def resolve_inheritance(
    child: ValidationProfile,
    profile_resolver: Callable[[str], ValidationProfile],
    source_keys: Optional[set[str]] = None,
) -> ValidationProfile:
    """Resolve single-level profile inheritance.

    Loads the base profile via `profile_resolver`, merges child overrides,
    and returns a flattened ValidationProfile with `extends=None`.

    Args:
        child: The child profile with an `extends` reference.
        profile_resolver: Callback that resolves a profile name to a
            ValidationProfile instance. At v0.5.1, this is typically
            `get_builtin_profile`. At v0.5.2b, it's the full discovery
            chain.
        source_keys: Set of field names explicitly provided in the
            child's source (YAML/JSON keys). Fields in this set are
            child overrides; fields NOT in this set are inherited from
            the base. If None, falls back to default-comparison detection.

    Returns:
        A new ValidationProfile with all fields resolved and
        `extends=None`.

    Raises:
        InheritanceError: If the base profile is not found, multi-level
            inheritance is detected, or resolution produces an invalid
            profile.

    Example:
        >>> child = ValidationProfile(
        ...     profile_name="custom",
        ...     description="Custom profile",
        ...     output_format="html",
        ...     extends="full",
        ... )
        >>> resolved = resolve_inheritance(
        ...     child=child,
        ...     profile_resolver=get_builtin_profile,
        ...     source_keys={"profile_name", "description", "output_format", "extends"},
        ... )
        >>> resolved.max_validation_level  # inherited from 'full'
        4
        >>> resolved.output_format  # child override
        'html'
        >>> resolved.extends  # flattened
        None

    Grounding: RR-SPEC-v0.1.3-validation-profiles.md §4.6.
    DECISION-031: Single-level only.
    """
    # --- No inheritance to resolve ---
    if child.extends is None:
        logger.debug(
            "Profile '%s' has no extends — returning as-is.",
            child.profile_name,
        )
        return child

    base_name = child.extends

    # --- Guard: circular reference (defensive — should not happen
    #     with single-level restriction, but check anyway) ---
    if base_name == child.profile_name:
        raise InheritanceError(
            f"Circular inheritance detected: profile '{child.profile_name}' "
            f"extends itself."
        )

    # --- Load the base profile ---
    logger.info(
        "Resolving inheritance: '%s' extends '%s'.",
        child.profile_name,
        base_name,
    )

    try:
        base = profile_resolver(base_name)
    except (ValueError, FileNotFoundError) as e:
        raise InheritanceError(
            f"Base profile '{base_name}' not found for profile "
            f"'{child.profile_name}'. "
            f"Ensure the base profile exists and is accessible. "
            f"Original error: {e}"
        ) from e

    # --- Guard: multi-level inheritance (DECISION-031) ---
    if base.extends is not None:
        raise InheritanceError(
            f"Multi-level inheritance is not supported (DECISION-031). "
            f"Profile '{child.profile_name}' extends '{base_name}', "
            f"which itself extends '{base.extends}'. "
            f"Maximum inheritance depth is 1. "
            f"Flatten '{base_name}' by removing its 'extends' field, or "
            f"have '{child.profile_name}' extend '{base.extends}' directly."
        )

    # --- Determine which fields the child explicitly set ---
    if source_keys is not None:
        child_override_fields = source_keys - _CHILD_ONLY_FIELDS
        logger.debug(
            "Using source_keys for override detection: %s",
            child_override_fields,
        )
    else:
        # Fallback: compare child values against defaults
        child_override_fields = _detect_overrides_by_default_comparison(child)
        logger.debug(
            "Using default-comparison for override detection: %s",
            child_override_fields,
        )

    # --- Build resolved field dictionary ---
    resolved_fields: dict = {}

    for field_name in child.model_fields:
        if field_name in _CHILD_ONLY_FIELDS:
            # Always use child's value for metadata fields
            if field_name == "extends":
                resolved_fields[field_name] = None  # Flatten
            else:
                resolved_fields[field_name] = getattr(child, field_name)
        elif field_name in child_override_fields:
            # Child explicitly set this field — use child's value
            resolved_fields[field_name] = getattr(child, field_name)
            logger.debug(
                "  %s: using child value '%s' (explicit override)",
                field_name,
                getattr(child, field_name),
            )
        else:
            # Inherit from base
            resolved_fields[field_name] = getattr(base, field_name)
            logger.debug(
                "  %s: inheriting from base '%s' = '%s'",
                field_name,
                base_name,
                getattr(base, field_name),
            )

    # --- Construct and validate the resolved profile ---
    try:
        resolved = ValidationProfile(**resolved_fields)
    except Exception as e:
        raise InheritanceError(
            f"Inheritance resolution for '{child.profile_name}' produced "
            f"an invalid profile. Resolved fields: {resolved_fields}. "
            f"Error: {e}"
        ) from e

    logger.info(
        "Inheritance resolved: '%s' = '%s' + %d override(s). "
        "Extends field cleared (flattened).",
        resolved.profile_name,
        base_name,
        len(child_override_fields),
    )

    return resolved


def _detect_overrides_by_default_comparison(
    child: ValidationProfile,
) -> set[str]:
    """Detect which fields differ from defaults (fallback when source_keys unavailable).

    Creates a default-constructed ValidationProfile and compares each
    field. Fields that differ are considered overrides.

    This method is imprecise: a child that explicitly sets a field to
    its default value will NOT be detected as an override. This is
    acceptable for programmatic use cases where source_keys tracking
    is not available.

    Args:
        child: The child profile to analyze.

    Returns:
        Set of field names where the child's value differs from the default.
    """
    # Create a profile with only required fields to get all defaults
    default = ValidationProfile(profile_name="_default_comparison_sentinel")

    overrides: set[str] = set()
    for field_name in child.model_fields:
        if field_name in _CHILD_ONLY_FIELDS:
            continue
        child_value = getattr(child, field_name)
        default_value = getattr(default, field_name)
        if child_value != default_value:
            overrides.add(field_name)

    return overrides
```

### 3.3 Convenience Functions

```python
def resolve_if_needed(
    profile: ValidationProfile,
    profile_resolver: Callable[[str], ValidationProfile],
    source_keys: Optional[set[str]] = None,
) -> ValidationProfile:
    """Resolve inheritance if the profile has an extends field, otherwise return as-is.

    This is the primary entry point for the profile loading pipeline.
    It handles both standalone and extending profiles uniformly.

    Args:
        profile: A ValidationProfile, possibly with extends set.
        profile_resolver: Callback to resolve base profile names.
        source_keys: Keys explicitly set in the source (if available).

    Returns:
        A flattened ValidationProfile with extends=None.

    Raises:
        InheritanceError: If resolution fails.
    """
    if profile.extends is None:
        return profile
    return resolve_inheritance(profile, profile_resolver, source_keys)


def validate_inheritance_chain(
    profile_name: str,
    extends: Optional[str],
    profile_resolver: Callable[[str], ValidationProfile],
) -> list[str]:
    """Validate an inheritance chain without resolving it.

    Returns a list of validation issues. An empty list means the
    chain is valid.

    Useful for pre-validation (e.g., in a `docstratum check-profile` command).

    Args:
        profile_name: Name of the child profile.
        extends: Name of the base profile (or None).
        profile_resolver: Callback to resolve base profile names.

    Returns:
        List of validation issue descriptions. Empty = valid.
    """
    issues: list[str] = []

    if extends is None:
        return issues

    # Check self-reference
    if extends == profile_name:
        issues.append(
            f"Circular inheritance: '{profile_name}' extends itself."
        )
        return issues

    # Check base exists
    try:
        base = profile_resolver(extends)
    except (ValueError, FileNotFoundError):
        issues.append(
            f"Base profile '{extends}' not found."
        )
        return issues

    # Check multi-level
    if base.extends is not None:
        issues.append(
            f"Multi-level inheritance: '{extends}' extends '{base.extends}'. "
            f"Maximum depth is 1."
        )

    return issues
```

### 3.4 Package Re-exports

```python
# Update src/docstratum/profiles/__init__.py
# Add to existing exports:
from docstratum.profiles.inheritance import (
    InheritanceError,
    resolve_inheritance,
    resolve_if_needed,
    validate_inheritance_chain,
)

# Add to __all__:
__all__ = [
    # ... existing exports ...
    "InheritanceError",
    "resolve_inheritance",
    "resolve_if_needed",
    "validate_inheritance_chain",
]
```

---

## 4. Decision Tree: Inheritance Resolution Flow

```
Profile loaded (from YAML, JSON, or built-in)
│
├── profile.extends is None?
│   └── YES → Return profile as-is (no inheritance)
│
├── profile.extends == profile.profile_name?
│   └── YES → InheritanceError("Circular")
│
├── Resolve base profile:
│   profile_resolver(profile.extends)
│   │
│   ├── FOUND →
│   │   │
│   │   ├── base.extends is not None?
│   │   │   └── YES → InheritanceError("Multi-level, DECISION-031")
│   │   │
│   │   └── base.extends is None → proceed
│   │       │
│   │       ├── source_keys provided? (from YAML loader)
│   │       │   ├── YES → use source_keys for override detection
│   │       │   └── NO  → use default-comparison fallback
│   │       │
│   │       ├── For each field:
│   │       │   ├── Metadata field → use child's value
│   │       │   ├── In override set → use child's value
│   │       │   └── Not in override set → use base's value
│   │       │
│   │       ├── Set extends = None (flatten)
│   │       │
│   │       └── Construct resolved ValidationProfile
│   │           ├── Pydantic validates → return resolved
│   │           └── Validation fails → InheritanceError
│   │
│   └── NOT FOUND → InheritanceError("Base not found")
```

---

## 5. Worked Examples

### 5.1 Enterprise Extends Full (Built-in)

```python
# Enterprise profile as defined in v0.5.1b
child = ValidationProfile(
    profile_name="enterprise",
    description="Enterprise audit...",
    output_tier=4,
    output_format="html",
    extends="full",
)

# Source keys from the definition
source_keys = {
    "profile_name", "description", "output_tier",
    "output_format", "extends",
}

resolved = resolve_inheritance(
    child=child,
    profile_resolver=get_builtin_profile,
    source_keys=source_keys,
)

# Inherited from full:
assert resolved.max_validation_level == 4
assert resolved.enabled_stages == [1, 2, 3, 4, 5, 6]
assert resolved.rule_tags_include == []
assert resolved.rule_tags_exclude == []
assert resolved.severity_overrides == {}
assert resolved.priority_overrides == {}
assert resolved.pass_threshold is None
assert resolved.grouping_mode == "by-priority"

# Child overrides:
assert resolved.profile_name == "enterprise"
assert resolved.description == "Enterprise audit..."
assert resolved.output_tier == 4
assert resolved.output_format == "html"

# Flattened:
assert resolved.extends is None
```

### 5.2 Custom Profile Extending CI

```yaml
# custom-strict.yaml
profile_name: "strict-ci"
description: "CI with strict threshold and elevated E006"
pass_threshold: 80
severity_overrides:
  E006: "ERROR"
extends: "ci"
```

```python
source_keys = {
    "profile_name", "description", "pass_threshold",
    "severity_overrides", "extends",
}

child = ValidationProfile(
    profile_name="strict-ci",
    description="CI with strict threshold and elevated E006",
    pass_threshold=80,
    severity_overrides={"E006": "ERROR"},
    extends="ci",
)

resolved = resolve_inheritance(child, get_builtin_profile, source_keys)

# Inherited from ci:
assert resolved.max_validation_level == 3
assert resolved.output_format == "json"
assert resolved.output_tier == 1
assert resolved.rule_tags_exclude == ["experimental", "docstratum-extended"]

# Child overrides:
assert resolved.pass_threshold == 80
assert resolved.severity_overrides == {"E006": "ERROR"}

# Flattened:
assert resolved.extends is None
```

### 5.3 Error: Multi-Level Inheritance

```python
# Imagine enterprise (extends full) is used as a base
child = ValidationProfile(
    profile_name="super-enterprise",
    description="...",
    extends="enterprise",
)

# enterprise has extends="full" → multi-level detected
try:
    resolve_inheritance(child, get_builtin_profile)
except InheritanceError as e:
    assert "Multi-level inheritance is not supported" in str(e)
    assert "extends 'enterprise', which itself extends 'full'" in str(e)
```

### 5.4 Error: Circular Inheritance

```python
child = ValidationProfile(
    profile_name="loop",
    description="...",
    extends="loop",
)

try:
    resolve_inheritance(child, get_builtin_profile)
except InheritanceError as e:
    assert "Circular inheritance" in str(e)
```

### 5.5 Error: Base Not Found

```python
child = ValidationProfile(
    profile_name="orphan",
    description="...",
    extends="nonexistent-base",
)

try:
    resolve_inheritance(child, get_builtin_profile)
except InheritanceError as e:
    assert "Base profile 'nonexistent-base' not found" in str(e)
```

---

## 6. Workflow

### 6.1 Profile Loading Pipeline (v0.5.2 Preview)

At v0.5.2, the profile loading pipeline will call `resolve_if_needed()`:

```python
# v0.5.2a → v0.5.1d integration
raw_profile = load_profile_from_yaml(path)
source_keys = extract_yaml_keys(path)

# Resolve inheritance (flattens extends)
resolved_profile = resolve_if_needed(
    profile=raw_profile,
    profile_resolver=discovery_chain.resolve,
    source_keys=source_keys,
)

# resolved_profile is complete — inject into pipeline
context.profile = resolved_profile
```

### 6.2 Development Cycle

```bash
# Run inheritance tests
pytest tests/test_profile_inheritance.py -v

# Type check
mypy src/docstratum/profiles/inheritance.py

# Format + lint
black src/docstratum/profiles/inheritance.py
ruff check src/docstratum/profiles/inheritance.py
```

---

## 7. Edge Cases

| Scenario | Input | Behavior |
|----------|-------|----------|
| No `extends` | `extends=None` | Profile returned as-is |
| Self-extension | `extends="self-name"` | `InheritanceError` (circular) |
| Base not found | `extends="nonexistent"` | `InheritanceError` with search explanation |
| Multi-level | Base has `extends` set | `InheritanceError` with guidance |
| Child sets field to same value as base | `child.max_level=4, base.max_level=4` | If in source_keys → child wins (no-op). If not in source_keys → inherited (same result) |
| Child sets field to default value | `child.max_level=4` (default is 4) | Without source_keys: NOT detected as override. With source_keys: detected correctly |
| `source_keys` is empty set | No fields are overrides | All values inherited from base (except metadata) |
| `source_keys` contains all fields | All fields are overrides | Effectively no inheritance (child wins everywhere) |
| `source_keys` contains unknown field | `source_keys={"nonexistent"}` | Ignored — only known fields are iterated |
| Base profile has severity_overrides | `base.severity_overrides={"E001": "WARNING"}` | Inherited unless child overrides `severity_overrides` |
| Child overrides severity_overrides partially | Child sets `severity_overrides={"E006": "ERROR"}` | **Full replacement** — child's dict replaces base's dict (not merged). DECISION-032 (shallow overrides) |
| Both profiles have `pass_threshold` | Base=50, child=80 | Child's value (80) if in source_keys |
| Resolved profile fails validation | e.g., incompatible field combination | `InheritanceError` wrapping `ValidationError` |

### 7.1 Important: Dictionary Fields Use Replace Semantics

`severity_overrides`, `priority_overrides` — these are **replaced** entirely when overridden, following DECISION-032 (shallow overrides). There is no deep merge.

```yaml
# Base profile (ci):
severity_overrides:
  E001: WARNING
  E002: INFO

# Child profile:
severity_overrides:
  E006: ERROR
extends: "ci"

# Result (NOT merged — child replaces base):
severity_overrides:
  E006: ERROR  # Only child's overrides
# E001 and E002 are gone
```

This is consistent with how CLI overrides work (v0.5.2c). For complex override merging, users should define a complete `severity_overrides` dictionary.

---

## 8. Acceptance Criteria

- [ ] `resolve_inheritance(child, resolver, source_keys)` produces a flattened profile
- [ ] Flattened profile has `extends=None`
- [ ] Child's `profile_name` and `description` are always preserved
- [ ] Fields in `source_keys` use child's values
- [ ] Fields NOT in `source_keys` inherit from base
- [ ] When `source_keys` is None, fallback to default-comparison detection
- [ ] Multi-level inheritance raises `InheritanceError` with helpful message
- [ ] Circular inheritance (self-extends) raises `InheritanceError`
- [ ] Base not found raises `InheritanceError` with original error
- [ ] `resolve_if_needed()` returns profile as-is when `extends` is None
- [ ] `resolve_if_needed()` resolves inheritance when `extends` is set
- [ ] `validate_inheritance_chain()` returns empty list for valid chains
- [ ] `validate_inheritance_chain()` returns issues for invalid chains
- [ ] Dictionary fields (`severity_overrides`, `priority_overrides`) use replace semantics
- [ ] The `enterprise` built-in resolves correctly against `full`
- [ ] Resolved profiles pass Pydantic validation
- [ ] Module docstring cites v0.5.1d and grounding specs
- [ ] All public functions have Google-style docstrings

---

## 9. Deliverables

| File | Description | Status |
|------|-------------|--------|
| `src/docstratum/profiles/inheritance.py` | Inheritance resolver: `resolve_inheritance`, `resolve_if_needed`, `validate_inheritance_chain` | NEW |
| `src/docstratum/profiles/__init__.py` | Updated to re-export inheritance functions | MODIFY |
| `tests/test_profile_inheritance.py` | Unit tests for inheritance resolution | NEW |

---

## 10. Test Plan (18 tests)

### 10.1 Successful Resolution Tests

| # | Test Name | Input | Expected |
|---|-----------|-------|----------|
| 1 | `test_no_extends_returns_as_is` | `extends=None` | Profile unchanged |
| 2 | `test_simple_inheritance` | Child overrides `output_format`, extends `full` | `max_level=4` inherited, `output_format` overridden |
| 3 | `test_enterprise_resolves_correctly` | Enterprise extends full | Matches PROFILE_ENTERPRISE values |
| 4 | `test_extends_cleared` | Any extending profile | `resolved.extends is None` |
| 5 | `test_profile_name_preserved` | `child.profile_name="custom"` extends `ci` | `resolved.profile_name == "custom"` |
| 6 | `test_description_preserved` | Child has custom description | `resolved.description` is child's |
| 7 | `test_source_keys_override_detection` | `source_keys={"pass_threshold"}` | Only `pass_threshold` overridden |
| 8 | `test_source_keys_empty_inherits_all` | `source_keys=set()` | All non-metadata fields inherited |
| 9 | `test_fallback_default_comparison` | `source_keys=None`, child has non-default values | Non-default values detected as overrides |

### 10.2 Error Tests

| # | Test Name | Input | Expected |
|---|-----------|-------|----------|
| 10 | `test_circular_self_extends` | `extends=self_name` | `InheritanceError("Circular")` |
| 11 | `test_multi_level_rejected` | Base has `extends` set | `InheritanceError("Multi-level")` |
| 12 | `test_base_not_found` | `extends="nonexistent"` | `InheritanceError("not found")` |
| 13 | `test_invalid_resolved_profile` | Resolution produces invalid combo | `InheritanceError` wrapping validation error |

### 10.3 Edge Case Tests

| # | Test Name | Input | Expected |
|---|-----------|-------|----------|
| 14 | `test_dict_fields_replace_not_merge` | Child has partial `severity_overrides` | Child's dict replaces base's (no merge) |
| 15 | `test_child_sets_field_to_default` | `source_keys` includes field set to default | Child's default value used (not base's) |
| 16 | `test_resolve_if_needed_no_extends` | `extends=None` | Returns profile unchanged |
| 17 | `test_resolve_if_needed_with_extends` | `extends="full"` | Resolves inheritance |
| 18 | `test_validate_chain_reports_issues` | Various invalid chains | Correct issue descriptions |

```python
"""Tests for v0.5.1d — Profile Inheritance.

Validates single-level inheritance resolution, error detection
(circular, multi-level, base not found), and field override semantics.
"""

import pytest

from docstratum.profiles.inheritance import (
    InheritanceError,
    resolve_inheritance,
    resolve_if_needed,
    validate_inheritance_chain,
)
from docstratum.profiles.model import ValidationProfile
from docstratum.profiles.builtins import (
    get_builtin_profile,
    PROFILE_ENTERPRISE,
    PROFILE_FULL,
)


class TestSuccessfulResolution:
    """Test cases where inheritance resolves correctly."""

    def test_no_extends_returns_as_is(self):
        """Profile without extends is returned unchanged."""
        profile = ValidationProfile(profile_name="standalone")
        resolved = resolve_inheritance(profile, get_builtin_profile)
        assert resolved.profile_name == "standalone"
        assert resolved.extends is None

    def test_enterprise_resolves_correctly(self):
        """Enterprise (extends full) should match its fully-expanded constant."""
        child = ValidationProfile(
            profile_name="enterprise",
            description=PROFILE_ENTERPRISE.description,
            output_tier=4,
            output_format="html",
            extends="full",
        )
        source_keys = {
            "profile_name", "description", "output_tier",
            "output_format", "extends",
        }
        resolved = resolve_inheritance(
            child, get_builtin_profile, source_keys
        )
        assert resolved.max_validation_level == PROFILE_FULL.max_validation_level
        assert resolved.enabled_stages == PROFILE_FULL.enabled_stages
        assert resolved.output_tier == 4
        assert resolved.output_format == "html"
        assert resolved.extends is None

    def test_source_keys_override_detection(self):
        """Only fields in source_keys should override the base."""
        child = ValidationProfile(
            profile_name="custom",
            description="Custom",
            pass_threshold=80,
            extends="ci",
        )
        source_keys = {
            "profile_name", "description", "pass_threshold", "extends",
        }
        resolved = resolve_inheritance(
            child, get_builtin_profile, source_keys
        )
        # pass_threshold is overridden
        assert resolved.pass_threshold == 80
        # output_format is inherited from ci
        assert resolved.output_format == "json"


class TestErrors:
    """Test error conditions in inheritance resolution."""

    def test_circular_self_extends(self):
        child = ValidationProfile(
            profile_name="loop",
            extends="loop",
        )
        with pytest.raises(InheritanceError, match="Circular"):
            resolve_inheritance(child, get_builtin_profile)

    def test_multi_level_rejected(self):
        child = ValidationProfile(
            profile_name="super",
            extends="enterprise",  # enterprise extends full
        )
        with pytest.raises(InheritanceError, match="Multi-level"):
            resolve_inheritance(child, get_builtin_profile)

    def test_base_not_found(self):
        child = ValidationProfile(
            profile_name="orphan",
            extends="nonexistent",
        )
        with pytest.raises(InheritanceError, match="not found"):
            resolve_inheritance(child, get_builtin_profile)


class TestEdgeCases:
    """Test edge cases and subtle behaviors."""

    def test_dict_fields_replace_not_merge(self):
        """severity_overrides should be replaced entirely, not merged."""
        # Create a mock base with severity_overrides
        def mock_resolver(name: str) -> ValidationProfile:
            return ValidationProfile(
                profile_name="base",
                severity_overrides={"E001": "WARNING", "E002": "INFO"},
            )

        child = ValidationProfile(
            profile_name="child",
            severity_overrides={"E006": "ERROR"},
            extends="base",
        )
        source_keys = {
            "profile_name", "severity_overrides", "extends",
        }
        resolved = resolve_inheritance(child, mock_resolver, source_keys)
        # Child replaces, not merges
        assert resolved.severity_overrides == {"E006": "ERROR"}
        assert "E001" not in resolved.severity_overrides
```

---

## 11. Limitations

| Limitation | Impact | Resolution |
|------------|--------|------------|
| Single-level only | Cannot chain: A → B → C | By design (DECISION-031); keeps resolution transparent |
| Replace semantics for dicts | Cannot override a single severity_overrides entry without re-specifying all | By design (DECISION-032); use full dict in child |
| Default-comparison fallback imprecise | Fields explicitly set to their default value are not detected as overrides | Use `source_keys` for precise detection (provided by v0.5.2a loader) |
| Base profile discovery limited | At v0.5.1, only built-in profiles can be bases | v0.5.2b (Discovery Precedence) provides full lookup |
| No inheritance for profile_name | Child always uses its own profile_name | By design — profile_name is identity |
