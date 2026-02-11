# v0.5.1c — Tag-Based Rule Filtering

> **Version:** v0.5.1c
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.5.1-validation-profiles.md](RR-SPEC-v0.5.1-validation-profiles.md)
> **Grounding:** RR-SPEC-v0.1.3-validation-profiles.md §4 (Module Composition Semantics), DECISION-029 (buffet model), DECISION-030 (OR semantics), DECISION-035 (bootstrap fallback)
> **Depends On:** v0.5.1a (`ValidationProfile` model), v0.3.x (`ValidationResult`, `ValidationDiagnostic`), v0.1.2a (`DiagnosticCode`, `Severity`)
> **Module:** `src/docstratum/profiles/filtering.py`
> **Tests:** `tests/test_profile_filtering.py`

---

## 1. Purpose

Implement the **"buffet" composition model** — the decision logic that determines which diagnostic rules execute for a given profile, and the post-execution step that applies severity overrides. This is the core engine that makes profiles actually *do something*: a `lint` profile that specifies `rule_tags_include=["structural"]` only has effect because the filtering engine evaluates each rule against that constraint.

After v0.5.1c:

```python
from docstratum.profiles.filtering import rule_executes, apply_severity_overrides

# Check if a specific rule should run given a profile
should_run = rule_executes(rule, profile)

# Apply severity overrides to a list of diagnostics
apply_severity_overrides(diagnostics, profile)
```

### 1.1 User Stories

> **US-1:** As the validation pipeline, I need a `rule_executes(rule, profile)` function that returns True/False, so that I can skip rules that don't match the active profile without evaluating them.

> **US-2:** As a CI maintainer, I want severity overrides (e.g., elevating W003 from WARNING to ERROR) to apply after validation but before exit code computation, so that the exit code reflects the adjusted severities.

> **US-3:** As a developer whose project doesn't have a Rule Registry yet, I want the filtering engine to operate in bootstrap mode — where tagless rules pass all inclusion checks — so that the `lint` profile doesn't accidentally filter out all rules.

---

## 2. Rule-Execution Decision Tree

A rule executes if **ALL** of these conditions are true:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Rule-Execution Decision Tree                  │
│                                                                 │
│ Input: rule (with .tags, .validation_level, .pipeline_stage)    │
│        profile (ValidationProfile)                              │
│                                                                 │
│ 1. TAG INCLUSION CHECK                                          │
│    │                                                            │
│    ├── profile.rule_tags_include is empty?                       │
│    │   └── YES → tag_included = True (empty = all)              │
│    │                                                            │
│    ├── rule.tags is empty? (bootstrap mode)                     │
│    │   └── YES → tag_included = True (DECISION-035 fallback)    │
│    │                                                            │
│    └── rule.tags ∩ profile.rule_tags_include ≠ ∅?               │
│        ├── YES → tag_included = True (OR semantics, DECISION-030)│
│        └── NO  → tag_included = False → SKIP RULE               │
│                                                                 │
│ 2. TAG EXCLUSION CHECK (always wins)                            │
│    │                                                            │
│    ├── rule.tags is empty?                                      │
│    │   └── YES → tag_excluded = False (nothing to exclude)      │
│    │                                                            │
│    └── rule.tags ∩ profile.rule_tags_exclude ≠ ∅?               │
│        ├── YES → tag_excluded = True → SKIP RULE                │
│        └── NO  → tag_excluded = False                           │
│                                                                 │
│ 3. LEVEL GATING                                                 │
│    │                                                            │
│    └── rule.validation_level <= profile.max_validation_level?    │
│        ├── YES → level_ok = True                                │
│        └── NO  → level_ok = False → SKIP RULE                  │
│                                                                 │
│ 4. STAGE GATING                                                 │
│    │                                                            │
│    └── rule.pipeline_stage in profile.enabled_stages?           │
│        ├── YES → stage_ok = True                                │
│        └── NO  → stage_ok = False → SKIP RULE                  │
│                                                                 │
│ RESULT: tag_included AND (NOT tag_excluded) AND level_ok AND    │
│         stage_ok → EXECUTE RULE                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.1 Semantic Details

**OR Semantics for Inclusion (DECISION-030):**
- A rule is included if ANY of its tags matches ANY tag in `rule_tags_include`.
- The profile says `rule_tags_include=["structural", "content"]` — this means "rules tagged `structural` OR rules tagged `content` (or both)."
- This is **OR** semantics, not AND. It's a union, not an intersection.

**Exclusion Always Wins:**
- If a rule matches both an include tag AND an exclude tag, it is **excluded**.
- Example: A rule tagged `["structural", "experimental"]` with `include=["structural"]` and `exclude=["experimental"]` is excluded.
- This is the safety net for experimental rules inside stable categories.

**Empty Include = Include All:**
- An empty `rule_tags_include` list means "no tag filtering on the inclusion side."
- All rules pass the inclusion check (subject to exclusion, level, and stage checks).
- This is used by the `full` profile: include everything, exclude nothing.

**Bootstrap Fallback (DECISION-035):**
- If a rule has no tags (empty `tags` set), it is treated as matching all include lists.
- This prevents the `lint` profile (`include=["structural"]`) from matching zero rules when the Rule Registry hasn't been built.
- Tagless rules never match exclusion lists (no tags to match against).

**Level Gating is a Performance Optimization:**
- Rules above `max_validation_level` are not instantiated at all — they are skipped before evaluation.
- A rule at L2 will not run when `max_validation_level=1` (lint profile).
- Level gating operates independently of tags. Even if a rule's tags match, it's skipped if its level is too high.

**Stage Gating is an Orchestrator Concern:**
- Stages not in `enabled_stages` don't run. The CLI (v0.5.0a) or pipeline orchestrator checks this before invoking any rules in that stage.
- The `rule_executes()` function checks stage gating for completeness, but in practice the orchestrator will have already skipped the stage.

---

## 3. Implementation

### 3.1 Rule Protocol

The filtering engine needs to know a rule's tags, level, and stage. Rather than importing a concrete rule class (which may not exist yet), define a protocol:

```python
# src/docstratum/profiles/filtering.py
"""Tag-based rule filtering engine for the buffet composition model.

Determines which diagnostic rules execute for a given profile by
evaluating tag inclusion/exclusion, level gating, and stage gating.
Also applies post-execution severity overrides.

Implements v0.5.1c.
Grounding: RR-SPEC-v0.1.3-validation-profiles.md §4.
"""

from __future__ import annotations

import logging
from typing import Protocol, Sequence, runtime_checkable

from docstratum.profiles.model import ValidationProfile

logger = logging.getLogger(__name__)

# Track whether the bootstrap warning has been emitted this run
_bootstrap_warning_emitted: bool = False


@runtime_checkable
class FilterableRule(Protocol):
    """Protocol for rules that can be evaluated by the filtering engine.

    Any object with these three attributes can be filtered. This allows
    the filtering engine to operate on rules from v0.3.x without
    importing their concrete classes.

    Grounding: RR-SPEC-v0.1.3-validation-profiles.md §4.
    """

    @property
    def tags(self) -> set[str] | frozenset[str] | list[str]:
        """Tags assigned to this rule (e.g., 'structural', 'content')."""
        ...

    @property
    def validation_level(self) -> int:
        """Validation level of this rule (0–4)."""
        ...

    @property
    def pipeline_stage(self) -> int:
        """Pipeline stage this rule belongs to (1–6)."""
        ...
```

### 3.2 Core Filtering Function

```python
def rule_executes(rule: FilterableRule, profile: ValidationProfile) -> bool:
    """Determine whether a rule should execute given a profile.

    Evaluates 4 conditions in sequence:
    1. Tag inclusion (OR semantics, DECISION-030)
    2. Tag exclusion (always wins)
    3. Level gating (max_validation_level)
    4. Stage gating (enabled_stages)

    A rule executes if ALL conditions pass.

    Args:
        rule: The rule to evaluate. Must have tags, validation_level,
              and pipeline_stage attributes.
        profile: The active validation profile.

    Returns:
        True if the rule should execute, False if it should be skipped.

    Example:
        >>> rule = SomeRule(tags={"structural"}, validation_level=1, pipeline_stage=2)
        >>> profile = get_builtin_profile("lint")
        >>> rule_executes(rule, profile)
        True

    Grounding: RR-SPEC-v0.1.3-validation-profiles.md §4.
    """
    global _bootstrap_warning_emitted

    rule_tags = set(rule.tags)  # Normalize to set for intersection ops

    # --- 1. Tag inclusion ---
    if not profile.rule_tags_include:
        # Empty include list → include all rules (no tag filter)
        tag_included = True
    elif not rule_tags:
        # Bootstrap mode (DECISION-035): rule has no tags
        # Treat as matching all include lists
        tag_included = True
        if not _bootstrap_warning_emitted:
            logger.warning(
                "Rule '%s' has no tags. Tag filtering is operating in "
                "bootstrap mode (Rule Registry not available). All "
                "tagless rules will pass inclusion checks.",
                _rule_name(rule),
            )
            _bootstrap_warning_emitted = True
    else:
        # OR semantics (DECISION-030): any overlap = included
        tag_included = bool(rule_tags & set(profile.rule_tags_include))

    # --- 2. Tag exclusion (always wins) ---
    if not rule_tags or not profile.rule_tags_exclude:
        # No tags to exclude or no exclusion list → not excluded
        tag_excluded = False
    else:
        tag_excluded = bool(rule_tags & set(profile.rule_tags_exclude))

    # --- 3. Level gating ---
    level_ok = rule.validation_level <= profile.max_validation_level

    # --- 4. Stage gating ---
    stage_ok = rule.pipeline_stage in profile.enabled_stages

    # --- Result ---
    executes = tag_included and not tag_excluded and level_ok and stage_ok

    if not executes:
        # Log the reason for skipping (DEBUG level)
        reasons = []
        if not tag_included:
            reasons.append(
                f"tag inclusion (rule tags {rule_tags} don't match "
                f"include list {profile.rule_tags_include})"
            )
        if tag_excluded:
            reasons.append(
                f"tag exclusion (rule tags {rule_tags} match "
                f"exclude list {profile.rule_tags_exclude})"
            )
        if not level_ok:
            reasons.append(
                f"level gating (rule level {rule.validation_level} > "
                f"max level {profile.max_validation_level})"
            )
        if not stage_ok:
            reasons.append(
                f"stage gating (rule stage {rule.pipeline_stage} not in "
                f"enabled stages {profile.enabled_stages})"
            )
        logger.debug(
            "Rule '%s' skipped: %s",
            _rule_name(rule),
            "; ".join(reasons),
        )

    return executes


def _rule_name(rule: FilterableRule) -> str:
    """Extract a displayable name from a rule.

    Tries `rule.name`, then `rule.code`, then falls back to the
    class name.
    """
    for attr in ("name", "code"):
        if hasattr(rule, attr):
            return str(getattr(rule, attr))
    return type(rule).__name__


def filter_rules(
    rules: Sequence[FilterableRule],
    profile: ValidationProfile,
) -> list[FilterableRule]:
    """Filter a sequence of rules, returning only those that should execute.

    This is a convenience wrapper around `rule_executes()` for bulk filtering.

    Args:
        rules: All available rules in the pipeline.
        profile: The active validation profile.

    Returns:
        List of rules that passed all filtering conditions.

    Example:
        >>> active_rules = filter_rules(all_rules, profile)
        >>> for rule in active_rules:
        ...     rule.execute(context)
    """
    result = [r for r in rules if rule_executes(r, profile)]
    logger.info(
        "Rule filtering: %d of %d rules active for profile '%s'.",
        len(result),
        len(rules),
        profile.profile_name,
    )
    return result


def reset_bootstrap_warning() -> None:
    """Reset the bootstrap warning flag.

    Called at the start of each validation run to allow the warning
    to be emitted once per run. Primarily used by tests.
    """
    global _bootstrap_warning_emitted
    _bootstrap_warning_emitted = False
```

### 3.3 Severity Override Application

```python
def apply_severity_overrides(
    diagnostics: list,
    profile: ValidationProfile,
) -> list[tuple[str, str, str]]:
    """Apply severity overrides from the profile to emitted diagnostics.

    Modifies diagnostic severity IN-PLACE (DECISION-036). This must be
    called AFTER all validation checks complete and BEFORE exit code
    computation, so that overrides affect the exit code.

    Args:
        diagnostics: List of ValidationDiagnostic instances (from v0.3.x).
            Each must have `.code` (with `.value` attribute) and `.severity`
            fields.
        profile: The active validation profile with severity_overrides.

    Returns:
        List of (code, old_severity, new_severity) tuples for each
        override applied. Useful for logging and testing.

    Raises:
        ValueError: If a severity override value cannot be converted to
            a valid Severity enum member.

    Example:
        >>> overrides_applied = apply_severity_overrides(diagnostics, profile)
        >>> for code, old, new in overrides_applied:
        ...     print(f"{code}: {old} → {new}")

    Grounding: RR-SPEC-v0.1.3-validation-profiles.md §4.
    DECISION-036: In-place mutation of severity, post-execution.
    """
    if not profile.severity_overrides:
        return []

    applied: list[tuple[str, str, str]] = []

    for diagnostic in diagnostics:
        # Extract the diagnostic code value
        # Handle both string codes and enum codes
        code_value = (
            diagnostic.code.value
            if hasattr(diagnostic.code, "value")
            else str(diagnostic.code)
        )

        override_severity = profile.severity_overrides.get(code_value)
        if override_severity is None:
            continue

        # Record the old severity for logging
        old_severity = (
            diagnostic.severity.value
            if hasattr(diagnostic.severity, "value")
            else str(diagnostic.severity)
        )

        # Apply the override
        try:
            # Import Severity enum from the schema module
            from docstratum.schema.diagnostics import Severity

            new_severity_enum = Severity(override_severity)
            diagnostic.severity = new_severity_enum
            new_severity = override_severity
        except (ValueError, ImportError) as e:
            logger.error(
                "Failed to apply severity override for %s: "
                "cannot convert '%s' to Severity enum. Error: %s",
                code_value,
                override_severity,
                e,
            )
            continue

        applied.append((code_value, old_severity, new_severity))
        logger.info(
            "Severity override applied: %s %s → %s (per profile '%s')",
            code_value,
            old_severity,
            new_severity,
            profile.profile_name,
        )

    if applied:
        logger.info(
            "Applied %d severity override(s) for profile '%s'.",
            len(applied),
            profile.profile_name,
        )

    return applied
```

### 3.4 Priority Override Note

`priority_overrides` are **stored on the profile but NOT consumed** at v0.5.1c. Priority overrides are consumed by the Remediation Framework (v0.6.x), which assigns priorities to diagnostics based on the remediation effort model. The filtering engine only applies severity overrides.

```python
# NOT IMPLEMENTED AT v0.5.1c:
# def apply_priority_overrides(diagnostics, profile):
#     """Consumed by v0.6.x (Remediation Framework)."""
#     pass
```

### 3.5 Package Re-exports

```python
# Update src/docstratum/profiles/__init__.py
# Add to existing exports:
from docstratum.profiles.filtering import (
    FilterableRule,
    apply_severity_overrides,
    filter_rules,
    rule_executes,
    reset_bootstrap_warning,
)

# Add to __all__:
__all__ = [
    # ... existing exports ...
    "FilterableRule",
    "apply_severity_overrides",
    "filter_rules",
    "rule_executes",
    "reset_bootstrap_warning",
]
```

---

## 4. Filtering Scenarios

### 4.1 Scenario Matrix

These scenarios illustrate how different profile configurations interact with different rule configurations:

| # | Profile | Rule Tags | Rule Level | Rule Stage | Result | Why |
|---|---------|-----------|------------|------------|--------|-----|
| 1 | lint (`include=["structural"], max_level=1, stages=[1,2]`) | `{"structural"}` | 1 | 2 | ✅ Execute | Tag matches, level OK, stage OK |
| 2 | lint | `{"content"}` | 1 | 2 | ❌ Skip | Tag "content" not in include list |
| 3 | lint | `{"structural"}` | 2 | 2 | ❌ Skip | Level 2 > max_level 1 |
| 4 | lint | `{"structural"}` | 1 | 3 | ❌ Skip | Stage 3 not in [1, 2] |
| 5 | ci (`include=["structural","content","ecosystem"], exclude=["experimental"]`) | `{"structural", "experimental"}` | 2 | 2 | ❌ Skip | Exclusion wins over inclusion |
| 6 | ci | `{"content"}` | 3 | 5 | ✅ Execute | Tag matches, level OK, stage OK |
| 7 | ci | `{"content"}` | 4 | 2 | ❌ Skip | Level 4 > max_level 3 |
| 8 | full (`include=[], exclude=[], max_level=4`) | `{"anything"}` | 4 | 6 | ✅ Execute | Empty include = all, no exclusion |
| 9 | full | `{}` (no tags) | 2 | 2 | ✅ Execute | Bootstrap mode: tagless = all inclusion |
| 10 | custom (`include=["structural"], exclude=[]`) | `{}` (no tags) | 1 | 1 | ✅ Execute | Bootstrap: tagless matches all |
| 11 | custom (`include=["structural"], exclude=["structural"]`) | `{"structural"}` | 1 | 1 | ❌ Skip | Exclusion wins |
| 12 | custom (`include=[], exclude=["experimental"]`) | `{"experimental", "content"}` | 1 | 1 | ❌ Skip | Exclusion of "experimental" |
| 13 | custom (`include=[], exclude=["experimental"]`) | `{"content"}` | 1 | 1 | ✅ Execute | "content" not excluded |

### 4.2 Severity Override Scenarios

| # | Diagnostic Code | Current Severity | Override | Result |
|---|----------------|-----------------|----------|--------|
| 1 | `E006` | `WARNING` | `{"E006": "ERROR"}` | `E006` becomes `ERROR` |
| 2 | `W003` | `WARNING` | `{"W003": "INFO"}` | `W003` becomes `INFO` (demoted) |
| 3 | `E001` | `ERROR` | `{}` (no override) | `E001` stays `ERROR` |
| 4 | `I004` | `INFO` | `{"I004": "ERROR"}` | `I004` becomes `ERROR` (promoted) |
| 5 | `E001` | `ERROR` | `{"E001": "FATAL"}` | Warning logged; override skipped (unknown severity) |

### 4.3 Exit Code Impact

Severity overrides modify exit codes because overrides are applied BEFORE `compute_exit_code()`:

```
Pipeline flow:
  v0.3.x → diagnostics (original severities)
  v0.5.1c → apply_severity_overrides() → diagnostics (modified severities)
  v0.5.0c → compute_exit_code(result) → uses modified severities
```

Example: A profile overrides `W003` from `WARNING` → `ERROR`. Without the override, W003 doesn't affect the exit code (warnings are ignored unless `--strict`). With the override, W003 is now an ERROR → exit code 2 (content error).

---

## 5. Workflow

### 5.1 Pipeline Integration

```python
# In cli.py → validate_command() — updated at v0.5.1c

from docstratum.profiles.filtering import (
    filter_rules,
    apply_severity_overrides,
    reset_bootstrap_warning,
)

# Reset for each validation run
reset_bootstrap_warning()

# Step 1: Filter rules based on profile
active_rules = filter_rules(all_rules, profile)

# Step 2: Execute only active rules
for rule in active_rules:
    rule.execute(context)

# Step 3: Apply severity overrides (AFTER execution, BEFORE exit code)
overrides_applied = apply_severity_overrides(
    result.diagnostics, profile
)

# Step 4: Compute exit code (uses modified severities)
exit_code = compute_exit_code(result, score, strict=args.strict)
```

### 5.2 Testing the Filtering Engine

```python
from dataclasses import dataclass

# Create a mock rule for testing
@dataclass
class MockRule:
    tags: set[str]
    validation_level: int
    pipeline_stage: int

# Test OR inclusion semantics
rule = MockRule(tags={"structural", "content"}, validation_level=1, pipeline_stage=2)
profile = get_builtin_profile("lint")
assert rule_executes(rule, profile) is True  # "structural" matches

# Test exclusion wins
rule = MockRule(tags={"structural", "experimental"}, validation_level=3, pipeline_stage=2)
profile = get_builtin_profile("ci")
assert rule_executes(rule, profile) is False  # "experimental" excluded
```

### 5.3 Development Cycle

```bash
# Run filtering tests
pytest tests/test_profile_filtering.py -v

# Type check
mypy src/docstratum/profiles/filtering.py

# Format + lint
black src/docstratum/profiles/filtering.py
ruff check src/docstratum/profiles/filtering.py
```

---

## 6. Edge Cases

| Scenario | Input | Behavior |
|----------|-------|----------|
| Rule with no tags + include list | `rule.tags=set(), include=["structural"]` | ✅ Execute (bootstrap fallback) |
| Rule with no tags + exclude list | `rule.tags=set(), exclude=["structural"]` | ✅ Execute (nothing to exclude) |
| Rule with no tags + both lists | `rule.tags=set(), include=["structural"], exclude=["experimental"]` | ✅ Execute (bootstrap inclusion, nothing to exclude) |
| Rule matching include AND exclude | `rule.tags={"structural"}, include=["structural"], exclude=["structural"]` | ❌ Skip (exclusion wins) |
| Empty include + empty exclude | Both empty | ✅ Execute (no tag filter at all) |
| `max_validation_level=0` | Level 0 only | Only L0 rules (parseability gate) run |
| `enabled_stages=[6]` | Stage 6 only | Only report generation rules run (unusual) |
| Rule object missing attributes | `rule` without `.tags` | `AttributeError` — caller's responsibility to pass valid rules |
| Severity override to unknown enum | `{"E001": "CATASTROPHIC"}` | Warning logged, override skipped |
| Severity override to same value | `{"E001": "ERROR"}` for an ERROR diagnostic | Override applied (no-op logged) |
| Empty diagnostics list | `[]` | `apply_severity_overrides` returns `[]` |
| Empty severity_overrides | `{}` | `apply_severity_overrides` returns `[]` immediately |
| Multiple overrides on same diagnostic | `{"E001": "WARNING"}` with 3 E001 diagnostics | All 3 are overridden |
| `filter_rules` with empty rule list | `rules=[]` | Returns `[]` |
| Bootstrap warning emitted once | Multiple tagless rules | Warning printed for first rule only |

---

## 7. Acceptance Criteria

- [ ] `rule_executes(rule, profile)` returns `True` for rules matching all conditions
- [ ] OR semantics: rule with tags `{a, b}` matches profile with `include=[a]`
- [ ] Exclusion wins: rule with tags `{a, experimental}` is excluded even if `a` is included
- [ ] Empty include list = include all rules (subject to exclusion/level/stage)
- [ ] Level gating: rule at L3 is skipped when `max_validation_level=1`
- [ ] Stage gating: rule at stage 3 is skipped when `enabled_stages=[1, 2]`
- [ ] Bootstrap fallback: tagless rules pass all inclusion checks (DECISION-035)
- [ ] Bootstrap warning is emitted once per run, not per rule
- [ ] `reset_bootstrap_warning()` clears the warning flag for testing
- [ ] `filter_rules(rules, profile)` returns only matching rules
- [ ] `filter_rules` logs the count of active vs. total rules
- [ ] `apply_severity_overrides()` mutates `diagnostic.severity` in-place (DECISION-036)
- [ ] `apply_severity_overrides()` returns list of applied overrides
- [ ] `apply_severity_overrides()` logs each override at INFO level
- [ ] Unknown severity values in overrides produce an error log and are skipped
- [ ] Empty `severity_overrides` returns immediately with no work
- [ ] `FilterableRule` is a runtime-checkable protocol
- [ ] Module docstring cites v0.5.1c and grounding specs
- [ ] All public functions have Google-style docstrings

---

## 8. Deliverables

| File | Description | Status |
|------|-------------|--------|
| `src/docstratum/profiles/filtering.py` | Filtering engine: `rule_executes`, `filter_rules`, `apply_severity_overrides` | NEW |
| `src/docstratum/profiles/__init__.py` | Updated to re-export filtering functions | MODIFY |
| `tests/test_profile_filtering.py` | Unit tests for filtering and severity overrides | NEW |

---

## 9. Test Plan (24 tests)

### 9.1 Tag Filtering Tests

| # | Test Name | Input | Expected |
|---|-----------|-------|----------|
| 1 | `test_tag_inclusion_match` | Rule tags `{"structural"}`, include `["structural"]` | `True` |
| 2 | `test_tag_inclusion_no_match` | Rule tags `{"content"}`, include `["structural"]` | `False` |
| 3 | `test_tag_inclusion_or_semantics` | Rule tags `{"content"}`, include `["structural", "content"]` | `True` |
| 4 | `test_tag_inclusion_partial_overlap` | Rule tags `{"structural", "advanced"}`, include `["structural"]` | `True` |
| 5 | `test_tag_inclusion_empty_includes_all` | Rule tags `{"anything"}`, include `[]` | `True` |
| 6 | `test_tag_exclusion_wins` | Rule tags `{"structural", "experimental"}`, include `["structural"]`, exclude `["experimental"]` | `False` |
| 7 | `test_tag_exclusion_no_match` | Rule tags `{"structural"}`, exclude `["experimental"]` | `True` |
| 8 | `test_tag_exclusion_empty` | Rule tags `{"structural"}`, exclude `[]` | `True` |
| 9 | `test_both_lists_empty` | Rule tags `{"anything"}`, include `[]`, exclude `[]` | `True` |

### 9.2 Bootstrap Fallback Tests

| # | Test Name | Input | Expected |
|---|-----------|-------|----------|
| 10 | `test_bootstrap_tagless_with_include` | Rule tags `set()`, include `["structural"]` | `True` (bootstrap) |
| 11 | `test_bootstrap_tagless_with_empty_include` | Rule tags `set()`, include `[]` | `True` |
| 12 | `test_bootstrap_tagless_with_exclude` | Rule tags `set()`, exclude `["structural"]` | `True` (nothing to exclude) |
| 13 | `test_bootstrap_warning_once` | 3 tagless rules with include `["structural"]` | Warning logged once |

### 9.3 Level and Stage Gating Tests

| # | Test Name | Input | Expected |
|---|-----------|-------|----------|
| 14 | `test_level_gating_pass` | Level 1, `max_level=3` | `True` |
| 15 | `test_level_gating_fail` | Level 4, `max_level=3` | `False` |
| 16 | `test_level_gating_boundary` | Level 3, `max_level=3` | `True` |
| 17 | `test_stage_gating_pass` | Stage 2, `stages=[1, 2]` | `True` |
| 18 | `test_stage_gating_fail` | Stage 3, `stages=[1, 2]` | `False` |

### 9.4 Combined Filtering Tests

| # | Test Name | Input | Expected |
|---|-----------|-------|----------|
| 19 | `test_filter_rules_returns_matching` | Mixed rule set against lint profile | Only structural L0–L1 rules |
| 20 | `test_filter_rules_logs_count` | 10 rules, 4 match | Log shows "4 of 10 rules active" |

### 9.5 Severity Override Tests

| # | Test Name | Input | Expected |
|---|-----------|-------|----------|
| 21 | `test_severity_override_applied` | `{"E006": "ERROR"}` on WARNING diagnostic | Severity changed to ERROR |
| 22 | `test_severity_override_no_match` | `{"E999": "ERROR"}` on E006 diagnostic | No change |
| 23 | `test_severity_override_unknown_severity` | `{"E006": "FATAL"}` | Warning logged, override skipped |
| 24 | `test_severity_override_empty` | `{}` overrides | Returns `[]` immediately |

```python
"""Tests for v0.5.1c — Tag-Based Rule Filtering.

Validates the buffet composition model: tag inclusion (OR semantics),
exclusion (always wins), level gating, stage gating, bootstrap
fallback, and severity override application.
"""

from dataclasses import dataclass

import pytest

from docstratum.profiles.filtering import (
    rule_executes,
    filter_rules,
    apply_severity_overrides,
    reset_bootstrap_warning,
)
from docstratum.profiles.model import ValidationProfile


@dataclass
class MockRule:
    """Test stub implementing FilterableRule protocol."""
    tags: set[str]
    validation_level: int
    pipeline_stage: int
    name: str = "mock_rule"


def make_profile(**overrides) -> ValidationProfile:
    """Create a profile with defaults, overriding specified fields."""
    defaults = {
        "profile_name": "test",
        "max_validation_level": 4,
        "enabled_stages": [1, 2, 3, 4, 5],
        "rule_tags_include": [],
        "rule_tags_exclude": [],
    }
    defaults.update(overrides)
    return ValidationProfile(**defaults)


class TestTagInclusion:
    """Test OR-semantics tag inclusion filtering."""

    def test_tag_inclusion_match(self):
        rule = MockRule(tags={"structural"}, validation_level=1, pipeline_stage=2)
        profile = make_profile(rule_tags_include=["structural"])
        assert rule_executes(rule, profile) is True

    def test_tag_inclusion_no_match(self):
        rule = MockRule(tags={"content"}, validation_level=1, pipeline_stage=2)
        profile = make_profile(rule_tags_include=["structural"])
        assert rule_executes(rule, profile) is False

    def test_tag_inclusion_or_semantics(self):
        rule = MockRule(tags={"content"}, validation_level=1, pipeline_stage=2)
        profile = make_profile(rule_tags_include=["structural", "content"])
        assert rule_executes(rule, profile) is True

    def test_empty_include_includes_all(self):
        rule = MockRule(tags={"anything"}, validation_level=1, pipeline_stage=2)
        profile = make_profile(rule_tags_include=[])
        assert rule_executes(rule, profile) is True


class TestTagExclusion:
    """Test exclusion-always-wins semantics."""

    def test_exclusion_wins_over_inclusion(self):
        rule = MockRule(
            tags={"structural", "experimental"},
            validation_level=1,
            pipeline_stage=2,
        )
        profile = make_profile(
            rule_tags_include=["structural"],
            rule_tags_exclude=["experimental"],
        )
        assert rule_executes(rule, profile) is False


class TestBootstrapFallback:
    """Test behavior when rules have no tags (Rule Registry absent)."""

    def setup_method(self):
        reset_bootstrap_warning()

    def test_tagless_matches_include_list(self):
        rule = MockRule(tags=set(), validation_level=1, pipeline_stage=2)
        profile = make_profile(rule_tags_include=["structural"])
        assert rule_executes(rule, profile) is True

    def test_tagless_not_excluded(self):
        rule = MockRule(tags=set(), validation_level=1, pipeline_stage=2)
        profile = make_profile(rule_tags_exclude=["structural"])
        assert rule_executes(rule, profile) is True


class TestLevelGating:
    """Test max_validation_level enforcement."""

    def test_level_within_max(self):
        rule = MockRule(tags={"structural"}, validation_level=1, pipeline_stage=2)
        profile = make_profile(max_validation_level=3)
        assert rule_executes(rule, profile) is True

    def test_level_exceeds_max(self):
        rule = MockRule(tags={"structural"}, validation_level=4, pipeline_stage=2)
        profile = make_profile(max_validation_level=3)
        assert rule_executes(rule, profile) is False
```

---

## 10. Limitations

| Limitation | Impact | Resolution |
|------------|--------|------------|
| `priority_overrides` not consumed | Priority overrides stored but not applied | v0.6.x (Remediation Framework) |
| Bootstrap mode for all rules | Without Rule Registry, tag filtering can't distinguish rule categories | Deliverable 3 (Rule Registry) |
| `FilterableRule` protocol not enforced at import | Rules must match protocol at runtime | Caller's responsibility |
| Severity override atomic per-diagnostic | No way to override severity for a diagnostic code only at a specific level | Future enhancement |
| Global `_bootstrap_warning_emitted` | Not thread-safe for concurrent validation | Single-threaded CLI assumption |
