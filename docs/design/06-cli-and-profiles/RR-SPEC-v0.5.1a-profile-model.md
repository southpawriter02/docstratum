# v0.5.1a — Profile Model Implementation

> **Version:** v0.5.1a
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.5.1-validation-profiles.md](RR-SPEC-v0.5.1-validation-profiles.md)
> **Grounding:** RR-SPEC-v0.1.3-validation-profiles.md §2 (Full Model Definition), §4.2 (Format-Tier Compatibility)
> **Depends On:** Pydantic v2 (existing project dependency)
> **Module:** `src/docstratum/profiles/model.py`
> **Tests:** `tests/test_profile_model.py`

---

## 1. Purpose

Implement the `ValidationProfile` Pydantic v2 model — the 13-field configuration object that governs every aspect of a validation run. This model is the **central artifact of v0.5.x**: all downstream sub-parts (built-in profiles, filtering, inheritance, loading, discovery, CLI overrides) operate on `ValidationProfile` instances.

After v0.5.1a, the model can be constructed programmatically:

```python
from docstratum.profiles.model import ValidationProfile

profile = ValidationProfile(
    profile_name="custom",
    description="A custom CI profile with strict thresholds",
    max_validation_level=3,
    pass_threshold=75,
    output_format="json",
)
```

### 1.1 User Story

> **US-1:** As a developer implementing the profile system, I want a strongly-typed Pydantic model with validation constraints so that invalid configurations are caught at construction time rather than failing at runtime.

> **US-2:** As a future CLI user, I want the profile model to accept unknown output formats and grouping modes with warnings (not errors) so that profiles written for newer versions of DocStratum don't break on older versions.

---

## 2. Model Definition

### 2.1 Complete Field Table

| # | Field | Type | Default | Constraints | Description |
|---|-------|------|---------|-------------|-------------|
| 1 | `profile_name` | `str` | *required* | Non-empty, max 64 chars | Unique human-readable identifier |
| 2 | `description` | `str` | `""` | Max 500 chars | Purpose and use case explanation |
| 3 | `max_validation_level` | `int` | `4` | `0 ≤ x ≤ 4` | Highest L0–L4 level to execute |
| 4 | `enabled_stages` | `list[int]` | `[1, 2, 3, 4, 5]` | Min 1 item; each `1 ≤ x ≤ 6` | Pipeline stage IDs to run |
| 5 | `rule_tags_include` | `list[str]` | `[]` | Each tag non-empty, max 50 chars | Tags that activate rules (OR semantics, DECISION-030) |
| 6 | `rule_tags_exclude` | `list[str]` | `[]` | Each tag non-empty, max 50 chars | Tags that deactivate rules (always wins) |
| 7 | `severity_overrides` | `dict[str, str]` | `{}` | Keys = DiagnosticCode values; values = Severity names | DiagnosticCode → Severity mapping |
| 8 | `priority_overrides` | `dict[str, str]` | `{}` | Keys = DiagnosticCode values; values = Priority names | DiagnosticCode → Priority mapping (consumed by v0.6.x) |
| 9 | `pass_threshold` | `int | None` | `None` | `0 ≤ x ≤ 100` if not None | Minimum score to pass |
| 10 | `output_tier` | `int` | `2` | `1 ≤ x ≤ 4` | Output detail tier |
| 11 | `output_format` | `str` | `"terminal"` | Lenient — any string accepted | Serialization format |
| 12 | `grouping_mode` | `str` | `"by-priority"` | Lenient — any string accepted | Remediation grouping strategy |
| 13 | `extends` | `str | None` | `None` | Max 64 chars if set | Base profile name for single-level inheritance |

### 2.2 Known Output Formats

The following formats are recognized at v0.5.x. Others are accepted with a warning:

| Format | Status at v0.5.x | Full Support |
|--------|------------------|--------------|
| `"terminal"` | **Active** — renders colorized ANSI output | v0.5.0d |
| `"json"` | **Active** — serializes result as JSON to stdout | v0.5.0d |
| `"markdown"` | Stored, produces fallback warning | v0.8.x |
| `"yaml"` | Stored, produces fallback warning | v0.8.x |
| `"html"` | Stored, produces fallback warning | v0.8.x |

### 2.3 Known Grouping Modes

| Mode | Status at v0.5.x | Full Support |
|------|------------------|--------------|
| `"by-priority"` | Stored, not consumed | v0.8.x |
| `"by-level"` | Stored, not consumed | v0.8.x |
| `"by-file"` | Stored, not consumed | v0.8.x |
| `"by-effort"` | Stored, not consumed | v0.8.x |

---

## 3. Implementation

### 3.1 Package Initialization

```python
# src/docstratum/profiles/__init__.py
"""DocStratum validation profile system.

Provides the ValidationProfile model, built-in profile presets,
tag-based rule filtering, and single-level profile inheritance.

Implements v0.5.1.
Grounding: RR-SPEC-v0.1.3-validation-profiles.md.
"""

from docstratum.profiles.model import ValidationProfile

__all__ = ["ValidationProfile"]
# Additional exports added by v0.5.1b, v0.5.1c, v0.5.1d
```

### 3.2 Profile Model

```python
# src/docstratum/profiles/model.py
"""ValidationProfile — Pydantic v2 model for validation run configuration.

Defines the 13-field model that governs every configurable aspect of a
validation run: levels, stages, tag filtering, severity/priority overrides,
score thresholds, output format/tier, and profile inheritance.

Implements v0.5.1a.
Grounding: RR-SPEC-v0.1.3-validation-profiles.md §2.
"""

from __future__ import annotations

import logging
import warnings
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

logger = logging.getLogger(__name__)

# --- Known values for lenient validation ---

KNOWN_OUTPUT_FORMATS: frozenset[str] = frozenset({
    "terminal", "json", "markdown", "yaml", "html",
})
# Grounding: RR-SPEC-v0.1.3-output-tier-specification.md §4.1

KNOWN_GROUPING_MODES: frozenset[str] = frozenset({
    "by-priority", "by-level", "by-file", "by-effort",
})
# Grounding: RR-SPEC-v0.1.3-validation-profiles.md §2.1

# Format-Tier compatibility matrix
# Grounding: RR-SPEC-v0.1.3-output-tier-specification.md §4.2
# True = supported, False = not supported
FORMAT_TIER_COMPATIBILITY: dict[int, frozenset[str]] = {
    1: frozenset({"terminal", "json"}),
    2: frozenset({"terminal", "json", "markdown", "yaml", "html"}),
    3: frozenset({"terminal", "json", "markdown", "html"}),
    4: frozenset({"json", "markdown", "html"}),
}


class ValidationProfile(BaseModel):
    """Configuration model for a validation run.

    Each field maps to a specific aspect of pipeline behavior:
    - **Level/stage gating:** Which checks run (max_validation_level, enabled_stages)
    - **Tag filtering:** Which rules are included/excluded (rule_tags_include/exclude)
    - **Override mapping:** How severity/priority are adjusted post-execution
    - **Threshold:** Minimum score to pass (pass_threshold)
    - **Output:** How results are rendered (output_tier, output_format, grouping_mode)
    - **Inheritance:** Base profile for field defaulting (extends)

    Implements v0.5.1a.
    Grounding: RR-SPEC-v0.1.3-validation-profiles.md §2.1.

    Example:
        >>> profile = ValidationProfile(
        ...     profile_name="ci",
        ...     description="CI pipeline profile",
        ...     max_validation_level=3,
        ...     pass_threshold=50,
        ...     output_format="json",
        ... )
        >>> profile.max_validation_level
        3

    Attributes:
        profile_name: Unique identifier for this profile (e.g., "ci", "lint").
        description: Human-readable explanation of the profile's purpose.
        max_validation_level: Highest L0–L4 level to execute (0=L0 only, 4=all).
        enabled_stages: Which pipeline stages run (1–6).
        rule_tags_include: Tags that activate rules (OR semantics). Empty = all.
        rule_tags_exclude: Tags that deactivate rules (always wins over include).
        severity_overrides: Map DiagnosticCode → Severity for post-execution override.
        priority_overrides: Map DiagnosticCode → Priority (consumed by v0.6.x).
        pass_threshold: Minimum score (0–100) to pass. None = no threshold.
        output_tier: Output detail level (1=summary, 2=diagnostic, 3=remediation, 4=audience).
        output_format: Serialization format ("terminal", "json", "markdown", "yaml", "html").
        grouping_mode: Remediation grouping strategy (consumed by v0.8.x).
        extends: Base profile name for single-level inheritance. None = standalone.
    """

    model_config = ConfigDict(
        # Profiles are not frozen — inheritance resolution creates modified copies.
        # Immutability is enforced by convention: profiles are not modified after
        # construction + inheritance resolution.
        extra="forbid",  # Reject unknown fields
        validate_default=True,
    )

    # --- Required fields ---

    profile_name: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="Unique human-readable identifier for this profile.",
    )

    # --- Optional fields with defaults ---

    description: str = Field(
        default="",
        max_length=500,
        description="Purpose and use case explanation.",
    )

    max_validation_level: int = Field(
        default=4,
        ge=0,
        le=4,
        description="Highest validation level to execute (0=L0, 4=L4).",
    )

    enabled_stages: list[int] = Field(
        default=[1, 2, 3, 4, 5],
        min_length=1,
        description="Pipeline stage IDs to execute (1–6).",
    )

    rule_tags_include: list[str] = Field(
        default_factory=list,
        description=(
            "Tags that activate rules. OR semantics: a rule matches if "
            "ANY of its tags appears in this list. Empty list = include all."
        ),
    )

    rule_tags_exclude: list[str] = Field(
        default_factory=list,
        description=(
            "Tags that deactivate rules. Exclusion always wins over inclusion."
        ),
    )

    severity_overrides: dict[str, str] = Field(
        default_factory=dict,
        description="Map DiagnosticCode value → Severity name.",
    )

    priority_overrides: dict[str, str] = Field(
        default_factory=dict,
        description="Map DiagnosticCode value → Priority name (consumed by v0.6.x).",
    )

    pass_threshold: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
        description="Minimum score (0–100) to pass. None = no threshold.",
    )

    output_tier: int = Field(
        default=2,
        ge=1,
        le=4,
        description="Output detail tier (1=summary, 2=diagnostic, 3=remediation, 4=audience).",
    )

    output_format: str = Field(
        default="terminal",
        description="Serialization format. Known: terminal, json, markdown, yaml, html.",
    )

    grouping_mode: str = Field(
        default="by-priority",
        description="Remediation grouping strategy. Known: by-priority, by-level, by-file, by-effort.",
    )

    extends: Optional[str] = Field(
        default=None,
        max_length=64,
        description="Base profile name for single-level inheritance.",
    )

    # --- Field validators ---

    @field_validator("enabled_stages")
    @classmethod
    def validate_enabled_stages(cls, v: list[int]) -> list[int]:
        """Validate that all stage IDs are in range 1–6.

        Raises:
            ValueError: If any stage ID is outside the valid range.
        """
        for stage_id in v:
            if not (1 <= stage_id <= 6):
                raise ValueError(
                    f"Stage ID {stage_id} is out of range. "
                    f"Valid range: 1–6."
                )
        # Deduplicate and sort for consistent behavior
        return sorted(set(v))

    @field_validator("rule_tags_include", "rule_tags_exclude")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Validate that all tag strings are non-empty and within length limits.

        Raises:
            ValueError: If any tag is empty or exceeds 50 characters.
        """
        validated = []
        for tag in v:
            stripped = tag.strip()
            if not stripped:
                raise ValueError(
                    "Empty tag strings are not allowed. "
                    "Remove empty entries from the tag list."
                )
            if len(stripped) > 50:
                raise ValueError(
                    f"Tag '{stripped[:20]}...' exceeds maximum length of 50 characters."
                )
            validated.append(stripped)
        return validated

    @field_validator("severity_overrides")
    @classmethod
    def validate_severity_overrides(cls, v: dict[str, str]) -> dict[str, str]:
        """Validate severity override values.

        Performs lenient validation: logs a warning for unknown severity
        names but does not reject them. This allows forward-compatible
        profiles that reference severity levels introduced in future versions.

        Returns:
            The input dictionary, unchanged.
        """
        known_severities = {"ERROR", "WARNING", "INFO", "HINT"}
        for code, severity in v.items():
            if severity.upper() not in known_severities:
                logger.warning(
                    "Unknown severity '%s' in severity_overrides for code '%s'. "
                    "Known severities: %s. This override will be stored but may "
                    "not be applied correctly.",
                    severity,
                    code,
                    ", ".join(sorted(known_severities)),
                )
        return v

    # --- Model-level validators ---

    @model_validator(mode="after")
    def validate_format_tier_compatibility(self) -> "ValidationProfile":
        """Warn on incompatible output_format / output_tier combinations.

        This validator implements lenient validation per SCOPE §2.6:
        invalid combinations produce a warning, not an error. The profile
        is still constructed successfully — the CLI handles fallback at
        render time.

        Grounding: RR-SPEC-v0.1.3-output-tier-specification.md §4.2.
        """
        # Warn on unknown output_format
        if self.output_format not in KNOWN_OUTPUT_FORMATS:
            logger.warning(
                "Unknown output_format '%s' in profile '%s'. "
                "Known formats: %s. This value will be stored but may "
                "produce a fallback at render time.",
                self.output_format,
                self.profile_name,
                ", ".join(sorted(KNOWN_OUTPUT_FORMATS)),
            )

        # Warn on unknown grouping_mode
        if self.grouping_mode not in KNOWN_GROUPING_MODES:
            logger.warning(
                "Unknown grouping_mode '%s' in profile '%s'. "
                "Known modes: %s. Falling back to 'by-priority'.",
                self.grouping_mode,
                self.profile_name,
                ", ".join(sorted(KNOWN_GROUPING_MODES)),
            )

        # Check format-tier compatibility (only for known formats)
        if self.output_format in KNOWN_OUTPUT_FORMATS:
            compatible_formats = FORMAT_TIER_COMPATIBILITY.get(
                self.output_tier, frozenset()
            )
            if (
                compatible_formats
                and self.output_format not in compatible_formats
            ):
                logger.warning(
                    "output_tier=%d + output_format='%s' is not a supported "
                    "combination in profile '%s'. Tier %d supports: %s. "
                    "The CLI will fall back to a compatible format at render time.",
                    self.output_tier,
                    self.output_format,
                    self.profile_name,
                    self.output_tier,
                    ", ".join(sorted(compatible_formats)),
                )

        return self

    # --- Convenience methods ---

    def has_tag_filtering(self) -> bool:
        """Return True if this profile uses tag-based filtering.

        A profile uses tag filtering if either rule_tags_include or
        rule_tags_exclude is non-empty. If both are empty, all rules
        pass the tag check (subject to level and stage gating).

        Returns:
            True if tag filtering is active.
        """
        return bool(self.rule_tags_include or self.rule_tags_exclude)

    def has_threshold(self) -> bool:
        """Return True if this profile enforces a pass threshold.

        Returns:
            True if pass_threshold is set (not None).
        """
        return self.pass_threshold is not None

    def stage_enabled(self, stage_id: int) -> bool:
        """Check whether a specific pipeline stage is enabled.

        Args:
            stage_id: Pipeline stage ID to check (1–6).

        Returns:
            True if the stage is in the enabled_stages list.
        """
        return stage_id in self.enabled_stages

    def to_summary_dict(self) -> dict[str, str | int | list | None]:
        """Return a human-readable summary of key profile settings.

        Intended for terminal header display and debug logging.
        Does not include severity/priority overrides (too verbose).

        Returns:
            Dictionary with key profile fields.
        """
        return {
            "name": self.profile_name,
            "max_level": self.max_validation_level,
            "stages": self.enabled_stages,
            "tags_include": self.rule_tags_include,
            "tags_exclude": self.rule_tags_exclude,
            "threshold": self.pass_threshold,
            "output_tier": self.output_tier,
            "output_format": self.output_format,
            "extends": self.extends,
        }
```

---

## 4. Decision: Mutability vs. Frozen

**DECISION-037: `ValidationProfile` is NOT frozen (not `ConfigDict(frozen=True)`).**

**Rationale:**

Inheritance resolution (v0.5.1d) needs to create a copy of the base profile and overwrite fields from the child. With Pydantic v2's frozen models, this requires `model_copy(update={...})` which is clean but:

1. The `resolve_inheritance()` function needs to iterate over child fields and build an update dict — frozen or not, the process is the same.
2. Keeping the model mutable allows `apply_severity_overrides()` (v0.5.1c) to directly set values if ever applied to the profile itself (though currently it targets diagnostics, not the profile).

**Trade-off:** We lose compile-time immutability. We compensate with the convention that profiles are not modified after construction + inheritance resolution. The `to_summary_dict()` method produces a snapshot, not a live view.

**Future option:** If mutation bugs appear, switch to `ConfigDict(frozen=True)` and use `model_copy(update={...})` everywhere. This is a non-breaking change to the public API.

---

## 5. Workflow

### 5.1 Creating a Profile Programmatically

```python
# Minimal profile (only required field)
minimal = ValidationProfile(profile_name="minimal", description="Bare minimum")
assert minimal.max_validation_level == 4  # uses default
assert minimal.output_format == "terminal"  # uses default

# CI profile with explicit settings
ci = ValidationProfile(
    profile_name="ci",
    description="CI pipeline — JSON output, threshold 50",
    max_validation_level=3,
    enabled_stages=[1, 2, 3, 4, 5],
    rule_tags_include=["structural", "content", "ecosystem"],
    rule_tags_exclude=["experimental", "docstratum-extended"],
    pass_threshold=50,
    output_tier=1,
    output_format="json",
)

# Serialize to dict (for YAML/JSON export)
profile_dict = ci.model_dump(mode="json")
```

### 5.2 Handling Lenient Validation

```python
import logging

# Set up logging to see warnings
logging.basicConfig(level=logging.WARNING)

# Unknown format → warning logged, profile created successfully
future_profile = ValidationProfile(
    profile_name="future",
    description="Uses a format from the future",
    output_format="pdf",  # Unknown at v0.5.x
)
# WARNING: Unknown output_format 'pdf' in profile 'future'...

# Invalid tier-format combo → warning logged
bad_combo = ValidationProfile(
    profile_name="bad-combo",
    description="Tier 1 + Markdown (unsupported)",
    output_tier=1,
    output_format="markdown",
)
# WARNING: output_tier=1 + output_format='markdown' is not a supported combination...
```

### 5.3 Development Cycle

```bash
# Run tests for the profile model
pytest tests/test_profile_model.py -v

# Type check
mypy src/docstratum/profiles/model.py

# Format + lint
black src/docstratum/profiles/
ruff check src/docstratum/profiles/
```

---

## 6. Edge Cases

| Scenario | Input | Behavior |
|----------|-------|----------|
| Missing `profile_name` | `ValidationProfile(description="x")` | `ValidationError`: `profile_name` is required |
| Empty `profile_name` | `profile_name=""` | `ValidationError`: min_length=1 |
| `profile_name` too long | 65-char string | `ValidationError`: max_length=64 |
| `max_validation_level` = -1 | Out of range | `ValidationError`: ge=0 |
| `max_validation_level` = 5 | Out of range | `ValidationError`: le=4 |
| `enabled_stages` empty | `[]` | `ValidationError`: min_length=1 |
| `enabled_stages` with 0 | `[0, 1, 2]` | `ValidationError`: stage 0 out of range |
| `enabled_stages` with 7 | `[1, 7]` | `ValidationError`: stage 7 out of range |
| `enabled_stages` duplicates | `[1, 1, 2, 2]` | Deduplicated to `[1, 2]` |
| `enabled_stages` unordered | `[3, 1, 2]` | Sorted to `[1, 2, 3]` |
| `pass_threshold` = -1 | Out of range | `ValidationError`: ge=0 |
| `pass_threshold` = 101 | Out of range | `ValidationError`: le=100 |
| `pass_threshold` = None | No threshold | Valid — threshold enforcement skipped |
| `output_format` = "xml" | Unknown format | Warning logged, profile created successfully |
| `grouping_mode` = "by-author" | Unknown mode | Warning logged, profile created successfully |
| `output_tier=1, format="markdown"` | Incompatible | Warning logged, profile created |
| `output_tier=4, format="terminal"` | Incompatible | Warning logged, profile created |
| Tags with whitespace | `[" foo ", "bar"]` | Stripped to `["foo", "bar"]` |
| Empty tag element | `["", "bar"]` | `ValidationError`: empty tags not allowed |
| Tag > 50 chars | Very long tag string | `ValidationError`: exceeds max length |
| `severity_overrides` unknown severity | `{"E001": "FATAL"}` | Warning logged, stored as-is |
| Extra fields | `unknown_field="x"` | `ValidationError`: `extra="forbid"` |
| `extends` = empty string | `""` | Valid (treated as None by convention — loader normalizes) |

---

## 7. Acceptance Criteria

- [ ] `ValidationProfile` is a Pydantic v2 `BaseModel` with all 13 fields
- [ ] `profile_name` is required; all other fields have defaults
- [ ] `max_validation_level` rejects values outside 0–4
- [ ] `enabled_stages` requires at least 1 stage, rejects IDs outside 1–6
- [ ] `enabled_stages` are deduplicated and sorted
- [ ] `pass_threshold` rejects values outside 0–100; accepts None
- [ ] `output_tier` rejects values outside 1–4
- [ ] Unknown `output_format` values produce a logged warning, not an error
- [ ] Unknown `grouping_mode` values produce a logged warning, not an error
- [ ] Incompatible format-tier combinations produce a logged warning, not an error
- [ ] Tags are stripped of whitespace; empty tags are rejected
- [ ] Unknown severity names in `severity_overrides` produce a warning
- [ ] Extra fields (not in the schema) are rejected (`extra="forbid"`)
- [ ] `has_tag_filtering()` returns True when tags are configured
- [ ] `has_threshold()` returns True when `pass_threshold` is not None
- [ ] `stage_enabled(n)` correctly checks the `enabled_stages` list
- [ ] `to_summary_dict()` returns a human-readable subset of fields
- [ ] `model_dump(mode="json")` produces a serializable dictionary
- [ ] Module docstring cites v0.5.1a and grounding spec
- [ ] All public methods have Google-style docstrings

---

## 8. Deliverables

| File | Description | Status |
|------|-------------|--------|
| `src/docstratum/profiles/__init__.py` | Package init, re-exports `ValidationProfile` | NEW |
| `src/docstratum/profiles/model.py` | `ValidationProfile` Pydantic model | NEW |
| `tests/test_profile_model.py` | Unit tests for model validation | NEW |

---

## 9. Test Plan (22 tests)

| # | Test Name | Input | Expected |
|---|-----------|-------|----------|
| 1 | `test_minimal_construction` | `profile_name="test"` | Profile created with all defaults |
| 2 | `test_all_fields_explicit` | All 13 fields provided | Profile created with explicit values |
| 3 | `test_profile_name_required` | No `profile_name` | `ValidationError` |
| 4 | `test_profile_name_empty` | `profile_name=""` | `ValidationError` |
| 5 | `test_profile_name_max_length` | 65-char string | `ValidationError` |
| 6 | `test_max_level_boundaries` | 0 and 4 | Both valid |
| 7 | `test_max_level_out_of_range` | -1 and 5 | Both `ValidationError` |
| 8 | `test_enabled_stages_valid` | `[1, 2, 3]` | Accepted |
| 9 | `test_enabled_stages_empty` | `[]` | `ValidationError` |
| 10 | `test_enabled_stages_out_of_range` | `[0]`, `[7]` | Both `ValidationError` |
| 11 | `test_enabled_stages_deduplicated` | `[1, 1, 2, 2]` | `[1, 2]` |
| 12 | `test_enabled_stages_sorted` | `[3, 1, 2]` | `[1, 2, 3]` |
| 13 | `test_pass_threshold_valid` | 0, 50, 100 | All valid |
| 14 | `test_pass_threshold_none` | `None` | Valid (no threshold) |
| 15 | `test_pass_threshold_out_of_range` | -1, 101 | Both `ValidationError` |
| 16 | `test_output_format_known` | `"terminal"`, `"json"` | No warnings |
| 17 | `test_output_format_unknown` | `"xml"` | Warning logged, profile created |
| 18 | `test_grouping_mode_unknown` | `"by-author"` | Warning logged, profile created |
| 19 | `test_format_tier_incompatible` | `tier=1, format="markdown"` | Warning logged, profile created |
| 20 | `test_tags_whitespace_stripped` | `[" foo ", "bar "]` | `["foo", "bar"]` |
| 21 | `test_tags_empty_rejected` | `["", "bar"]` | `ValidationError` |
| 22 | `test_extra_fields_rejected` | `unknown_field="x"` | `ValidationError` |

```python
"""Tests for v0.5.1a — Profile Model Implementation.

Validates the ValidationProfile Pydantic model: field constraints,
lenient validation (warnings for unknown formats), and edge cases.
"""

import logging

import pytest
from pydantic import ValidationError

from docstratum.profiles.model import ValidationProfile


class TestProfileConstruction:
    """Test ValidationProfile construction and defaults."""

    def test_minimal_construction(self):
        """Only profile_name is required; all other fields use defaults."""
        profile = ValidationProfile(profile_name="test")
        assert profile.profile_name == "test"
        assert profile.description == ""
        assert profile.max_validation_level == 4
        assert profile.enabled_stages == [1, 2, 3, 4, 5]
        assert profile.rule_tags_include == []
        assert profile.rule_tags_exclude == []
        assert profile.severity_overrides == {}
        assert profile.priority_overrides == {}
        assert profile.pass_threshold is None
        assert profile.output_tier == 2
        assert profile.output_format == "terminal"
        assert profile.grouping_mode == "by-priority"
        assert profile.extends is None

    def test_all_fields_explicit(self):
        """All 13 fields can be set explicitly."""
        profile = ValidationProfile(
            profile_name="custom",
            description="Custom profile",
            max_validation_level=2,
            enabled_stages=[1, 2],
            rule_tags_include=["structural"],
            rule_tags_exclude=["experimental"],
            severity_overrides={"E001": "WARNING"},
            priority_overrides={"E001": "LOW"},
            pass_threshold=75,
            output_tier=3,
            output_format="markdown",
            grouping_mode="by-level",
            extends="full",
        )
        assert profile.max_validation_level == 2
        assert profile.pass_threshold == 75
        assert profile.extends == "full"


class TestFieldValidation:
    """Test field-level constraint enforcement."""

    def test_profile_name_required(self):
        """profile_name must be provided."""
        with pytest.raises(ValidationError):
            ValidationProfile()  # type: ignore

    def test_profile_name_empty(self):
        """Empty profile_name is rejected."""
        with pytest.raises(ValidationError):
            ValidationProfile(profile_name="")

    def test_max_level_out_of_range(self):
        """max_validation_level outside 0–4 is rejected."""
        with pytest.raises(ValidationError):
            ValidationProfile(profile_name="t", max_validation_level=5)
        with pytest.raises(ValidationError):
            ValidationProfile(profile_name="t", max_validation_level=-1)

    def test_enabled_stages_empty_rejected(self):
        """Empty enabled_stages is rejected (min 1 stage)."""
        with pytest.raises(ValidationError):
            ValidationProfile(profile_name="t", enabled_stages=[])


class TestLenientValidation:
    """Test warning-only validation for forward-compatible fields."""

    def test_unknown_output_format_warns(self, caplog):
        """Unknown output_format should warn, not raise."""
        with caplog.at_level(logging.WARNING):
            profile = ValidationProfile(
                profile_name="t", output_format="pdf"
            )
        assert profile.output_format == "pdf"
        assert "Unknown output_format" in caplog.text

    def test_format_tier_incompatible_warns(self, caplog):
        """Incompatible format-tier combo should warn, not raise."""
        with caplog.at_level(logging.WARNING):
            profile = ValidationProfile(
                profile_name="t",
                output_tier=1,
                output_format="markdown",
            )
        assert profile.output_tier == 1
        assert "not a supported combination" in caplog.text
```

---

## 10. Limitations

| Limitation | Impact | Resolution |
|------------|--------|------------|
| Model only — not loadable from files | Must be constructed programmatically | v0.5.2a (Profile Loading) |
| No inheritance resolution | `extends` field stored but not processed | v0.5.1d (Inheritance) |
| No runtime format fallback | Warning logged but no automatic format switch | v0.5.0d / v0.8.x |
| `severity_overrides` lenient on values | Unknown severities stored but won't match enum | v0.5.1c validates at application time |
