# v0.5.2a — Profile Loading

> **Version:** v0.5.2a
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.5.2-discovery-and-configuration.md](RR-SPEC-v0.5.2-discovery-and-configuration.md)
> **Grounding:** RR-SPEC-v0.1.3-validation-profiles.md §5.3 (Profile File Formats), §5.4 (Embedded Profiles)
> **Depends On:** v0.5.1a (`ValidationProfile` model), v0.5.1d (`resolve_inheritance`, `InheritanceError`)
> **Module:** `src/docstratum/profiles/loading.py`
> **Tests:** `tests/test_profile_loading.py`

---

## 1. Purpose

Implement the file-to-model layer: read a YAML or JSON file from disk, parse it, validate it against the `ValidationProfile` Pydantic schema, track which keys were explicitly provided in the source (for inheritance override detection), resolve `extends` if present, and return a ready-to-use `ValidationProfile` instance.

After v0.5.2a:

```python
from docstratum.profiles.loading import load_profile_from_file, load_profile_from_dict

# From a standalone YAML file
profile, source_keys = load_profile_from_file("./strict-ci.yaml")
assert profile.profile_name == "strict-ci"

# From an embedded dict (extracted from .docstratum.yml)
profile, source_keys = load_profile_from_dict(
    {"profile_name": "strict-ci", "pass_threshold": 80, "extends": "ci"},
    source_path=".docstratum.yml",
)
```

### 1.1 User Stories

> **US-1:** As a developer, I want to point `--profile ./strict-ci.yaml` at a file and have it validated immediately, so that typos in field names or out-of-range values are caught before validation runs.

> **US-2:** As the discovery chain (v0.5.2b), I need a low-level loading function that returns both the `ValidationProfile` and the set of source keys, so that I can pass them to `resolve_inheritance()` for accurate override detection.

> **US-3:** As a user embedding profiles in `.docstratum.yml`, I want the loader to accept a pre-parsed dictionary (not just file paths), so that the `.docstratum.yml` reader can extract a profile dict and delegate construction to the same loader.

---

## 2. Supported Formats

### 2.1 File Extensions

| Extension | Parser | Notes |
|-----------|--------|-------|
| `.yaml` | PyYAML `yaml.safe_load()` | YAML 1.1. Bare `yes`/`no` → boolean (document limitation). |
| `.yml` | PyYAML `yaml.safe_load()` | Alias for `.yaml`. |
| `.json` | `json.loads()` (stdlib) | Standard JSON. No comments. |

Unsupported extensions produce a `ProfileLoadError` with the message:

```
Unsupported profile file format: '.toml'. Supported formats: .yaml, .yml, .json.
```

### 2.2 Standalone Profile File Format

```yaml
# strict-ci.yaml
profile_name: "strict-ci"
description: "Strict CI — threshold 80, all warnings are errors"
max_validation_level: 3
enabled_stages: [1, 2, 3, 4, 5]
rule_tags_include: ["structural", "content", "ecosystem"]
rule_tags_exclude: ["experimental"]
severity_overrides:
  W003: "ERROR"
  W005: "ERROR"
pass_threshold: 80
output_tier: 1
output_format: "json"
extends: "ci"
```

**Minimum viable profile:**
```yaml
profile_name: "minimal"
```

All other fields use the `ValidationProfile` defaults if not specified.

### 2.3 Embedded Profile Format (in `.docstratum.yml`)

```yaml
# .docstratum.yml
default_profile: "strict-ci"

profiles:
  strict-ci:
    description: "Strict CI — threshold 80"
    pass_threshold: 80
    severity_overrides:
      W003: "ERROR"
    extends: "ci"

  team-full:
    description: "Full analysis for our team"
    output_format: "html"
    extends: "full"
```

**Embedded profile loading rules:**
1. The dictionary key (`strict-ci`) becomes the `profile_name` if `profile_name` is not explicitly provided in the dict.
2. If `profile_name` IS explicitly provided and differs from the key, the explicit value wins but a warning is logged.
3. Each profile dict is passed to `load_profile_from_dict()`.

---

## 3. Implementation

### 3.1 Error Types

```python
# src/docstratum/profiles/loading.py
"""Profile loader — reads YAML/JSON files and constructs ValidationProfile instances.

Handles standalone files (.yaml, .yml, .json) and embedded dicts from
.docstratum.yml. Tracks source_keys for inheritance override detection.

Implements v0.5.2a.
Grounding: RR-SPEC-v0.1.3-validation-profiles.md §5.3–§5.4.
DECISION-040: PyYAML for YAML parsing.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Callable, Optional

import yaml
from pydantic import ValidationError

from docstratum.profiles.inheritance import InheritanceError, resolve_inheritance
from docstratum.profiles.model import ValidationProfile

logger = logging.getLogger(__name__)


class ProfileError(Exception):
    """Base class for all profile-related errors."""
    pass


class ProfileLoadError(ProfileError):
    """Raised when a profile file cannot be loaded or validated.

    Attributes:
        source_path: The file path that was being loaded.
        field_errors: Per-field validation error details (if available).
    """

    def __init__(
        self,
        message: str,
        source_path: str | Path | None = None,
        field_errors: list[dict[str, Any]] | None = None,
    ):
        self.source_path = source_path
        self.field_errors = field_errors or []
        super().__init__(message)
```

### 3.2 Core Loading Functions

```python
# --- File extension detection ---

_YAML_EXTENSIONS: frozenset[str] = frozenset({".yaml", ".yml"})
_JSON_EXTENSIONS: frozenset[str] = frozenset({".json"})
_SUPPORTED_EXTENSIONS: frozenset[str] = _YAML_EXTENSIONS | _JSON_EXTENSIONS


def load_profile_from_file(
    path: str | Path,
    profile_resolver: Optional[Callable[[str], ValidationProfile]] = None,
) -> tuple[ValidationProfile, set[str]]:
    """Load a ValidationProfile from a YAML or JSON file.

    Reads the file, parses based on extension, validates via Pydantic,
    and resolves inheritance if `extends` is set.

    Args:
        path: Path to the profile file (.yaml, .yml, or .json).
        profile_resolver: Callback to resolve base profile names for
            inheritance. If None, inheritance resolution is skipped
            (the caller must resolve it separately).

    Returns:
        A tuple of (ValidationProfile, source_keys) where source_keys
        is the set of field names explicitly present in the source file.

    Raises:
        FileNotFoundError: If the file does not exist.
        ProfileLoadError: If the file format is unsupported, the file
            cannot be parsed, or the profile fails Pydantic validation.

    Example:
        >>> profile, keys = load_profile_from_file("./strict-ci.yaml")
        >>> profile.profile_name
        'strict-ci'
        >>> "pass_threshold" in keys
        True

    Grounding: RR-SPEC-v0.1.3-validation-profiles.md §5.3.
    """
    file_path = Path(path).resolve()

    # --- File existence check ---
    if not file_path.exists():
        raise FileNotFoundError(
            f"Profile file not found: {file_path}"
        )

    if not file_path.is_file():
        raise ProfileLoadError(
            f"Profile path is not a file: {file_path}",
            source_path=file_path,
        )

    # --- Extension check ---
    suffix = file_path.suffix.lower()
    if suffix not in _SUPPORTED_EXTENSIONS:
        raise ProfileLoadError(
            f"Unsupported profile file format: '{suffix}'. "
            f"Supported formats: {', '.join(sorted(_SUPPORTED_EXTENSIONS))}.",
            source_path=file_path,
        )

    # --- Read and parse ---
    logger.info("Loading profile from file: %s", file_path)

    try:
        raw_text = file_path.read_text(encoding="utf-8")
    except OSError as e:
        raise ProfileLoadError(
            f"Cannot read profile file: {file_path}. Error: {e}",
            source_path=file_path,
        ) from e

    try:
        if suffix in _YAML_EXTENSIONS:
            raw_dict = yaml.safe_load(raw_text)
        else:
            raw_dict = json.loads(raw_text)
    except yaml.YAMLError as e:
        raise ProfileLoadError(
            f"YAML parse error in {file_path}: {e}",
            source_path=file_path,
        ) from e
    except json.JSONDecodeError as e:
        raise ProfileLoadError(
            f"JSON parse error in {file_path}: {e}",
            source_path=file_path,
        ) from e

    # --- Validate parsed content ---
    if raw_dict is None:
        raise ProfileLoadError(
            f"Profile file is empty: {file_path}",
            source_path=file_path,
        )

    if not isinstance(raw_dict, dict):
        raise ProfileLoadError(
            f"Profile file must contain a YAML/JSON object (mapping), "
            f"not {type(raw_dict).__name__}: {file_path}",
            source_path=file_path,
        )

    # --- Delegate to dict loader ---
    return load_profile_from_dict(
        raw_dict,
        source_path=file_path,
        profile_resolver=profile_resolver,
    )


def load_profile_from_dict(
    raw_dict: dict[str, Any],
    source_path: str | Path | None = None,
    profile_name_fallback: str | None = None,
    profile_resolver: Optional[Callable[[str], ValidationProfile]] = None,
) -> tuple[ValidationProfile, set[str]]:
    """Construct a ValidationProfile from a parsed dictionary.

    This is the core construction function used by both file loading
    and embedded profile loading (.docstratum.yml).

    Args:
        raw_dict: Parsed dictionary of profile fields.
        source_path: Path to the source file (for error messages).
        profile_name_fallback: Name to use if `profile_name` is not
            explicitly provided in the dict (used by embedded profiles
            where the key name becomes the profile name).
        profile_resolver: Callback for inheritance resolution.

    Returns:
        A tuple of (ValidationProfile, source_keys).

    Raises:
        ProfileLoadError: If Pydantic validation fails or inheritance
            resolution fails.

    Example:
        >>> profile, keys = load_profile_from_dict(
        ...     {"profile_name": "test", "pass_threshold": 80},
        ...     source_path=".docstratum.yml",
        ... )
        >>> keys
        {'profile_name', 'pass_threshold'}
    """
    # --- Track source keys (DECISION-039) ---
    source_keys: set[str] = set(raw_dict.keys())
    logger.debug("Source keys from %s: %s", source_path or "<dict>", source_keys)

    # --- Apply profile_name fallback for embedded profiles ---
    if "profile_name" not in raw_dict and profile_name_fallback:
        raw_dict = {**raw_dict, "profile_name": profile_name_fallback}
        source_keys.add("profile_name")
        logger.debug(
            "Applied profile_name fallback: '%s'",
            profile_name_fallback,
        )
    elif "profile_name" in raw_dict and profile_name_fallback:
        # Explicit profile_name differs from key name
        if raw_dict["profile_name"] != profile_name_fallback:
            logger.warning(
                "Profile dict key '%s' differs from explicit profile_name '%s' "
                "in %s. Using explicit profile_name.",
                profile_name_fallback,
                raw_dict["profile_name"],
                source_path or "<dict>",
            )

    # --- Construct ValidationProfile via Pydantic ---
    try:
        profile = ValidationProfile(**raw_dict)
    except ValidationError as e:
        # Convert Pydantic errors to ProfileLoadError with context
        field_errors = []
        error_lines = []
        for error in e.errors():
            loc = " → ".join(str(l) for l in error["loc"])
            field_errors.append({
                "field": loc,
                "type": error["type"],
                "message": error["msg"],
            })
            error_lines.append(f"  {loc}: {error['msg']}")

        error_detail = "\n".join(error_lines)
        raise ProfileLoadError(
            f"Profile validation failed"
            f"{f' ({source_path})' if source_path else ''}:\n"
            f"{error_detail}",
            source_path=source_path,
            field_errors=field_errors,
        ) from e

    logger.info(
        "Profile '%s' constructed from %s (%d source keys).",
        profile.profile_name,
        source_path or "<dict>",
        len(source_keys),
    )

    # --- Resolve inheritance if extends is set ---
    if profile.extends is not None and profile_resolver is not None:
        try:
            profile = resolve_inheritance(
                child=profile,
                profile_resolver=profile_resolver,
                source_keys=source_keys,
            )
            logger.info(
                "Inheritance resolved for '%s' (extended '%s').",
                profile.profile_name,
                raw_dict.get("extends"),
            )
        except InheritanceError as e:
            raise ProfileLoadError(
                f"Inheritance resolution failed for profile "
                f"'{profile.profile_name}'"
                f"{f' ({source_path})' if source_path else ''}: {e}",
                source_path=source_path,
            ) from e
    elif profile.extends is not None and profile_resolver is None:
        logger.warning(
            "Profile '%s' has extends='%s' but no profile_resolver was "
            "provided. Inheritance will not be resolved.",
            profile.profile_name,
            profile.extends,
        )

    return profile, source_keys
```

### 3.3 Embedded Profile Loader (for `.docstratum.yml`)

```python
def load_embedded_profiles(
    config_path: str | Path,
    profile_resolver: Optional[Callable[[str], ValidationProfile]] = None,
) -> dict[str, tuple[ValidationProfile, set[str]]]:
    """Load all embedded profiles from a .docstratum.yml file.

    Reads the `profiles:` section of the config file and constructs
    a ValidationProfile for each entry.

    Args:
        config_path: Path to the .docstratum.yml file.
        profile_resolver: Callback for inheritance resolution.

    Returns:
        Dictionary mapping profile name → (ValidationProfile, source_keys).
        Empty dict if no `profiles:` section exists.

    Raises:
        FileNotFoundError: If the config file does not exist.
        ProfileLoadError: If the file is not valid YAML or any
            embedded profile fails validation.

    Example:
        >>> profiles = load_embedded_profiles(".docstratum.yml")
        >>> profiles["strict-ci"][0].pass_threshold
        80
    """
    config_file = Path(config_path).resolve()

    if not config_file.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_file}"
        )

    raw_text = config_file.read_text(encoding="utf-8")

    try:
        config = yaml.safe_load(raw_text)
    except yaml.YAMLError as e:
        raise ProfileLoadError(
            f"YAML parse error in {config_file}: {e}",
            source_path=config_file,
        ) from e

    if not isinstance(config, dict):
        raise ProfileLoadError(
            f"Configuration file must contain a YAML object: {config_file}",
            source_path=config_file,
        )

    profiles_section = config.get("profiles")
    if profiles_section is None:
        logger.debug("No 'profiles:' section in %s.", config_file)
        return {}

    if not isinstance(profiles_section, dict):
        raise ProfileLoadError(
            f"'profiles:' section must be a mapping, "
            f"not {type(profiles_section).__name__}: {config_file}",
            source_path=config_file,
        )

    result: dict[str, tuple[ValidationProfile, set[str]]] = {}

    for key, profile_dict in profiles_section.items():
        if not isinstance(profile_dict, dict):
            raise ProfileLoadError(
                f"Profile '{key}' in {config_file} must be a mapping, "
                f"not {type(profile_dict).__name__}.",
                source_path=config_file,
            )

        profile, source_keys = load_profile_from_dict(
            profile_dict,
            source_path=config_file,
            profile_name_fallback=str(key),
            profile_resolver=profile_resolver,
        )
        result[str(key)] = (profile, source_keys)

    logger.info(
        "Loaded %d embedded profile(s) from %s: %s",
        len(result),
        config_file,
        ", ".join(sorted(result.keys())),
    )

    return result


def read_default_profile_name(config_path: str | Path) -> str | None:
    """Read the default_profile key from .docstratum.yml.

    Args:
        config_path: Path to .docstratum.yml.

    Returns:
        The default_profile name, or None if not specified.
    """
    config_file = Path(config_path).resolve()

    if not config_file.exists():
        return None

    try:
        raw_text = config_file.read_text(encoding="utf-8")
        config = yaml.safe_load(raw_text)
    except (OSError, yaml.YAMLError):
        return None

    if not isinstance(config, dict):
        return None

    default = config.get("default_profile")
    if isinstance(default, str) and default.strip():
        return default.strip()

    return None
```

### 3.4 Package Re-exports

```python
# Update src/docstratum/profiles/__init__.py
# Add to existing exports:
from docstratum.profiles.loading import (
    ProfileError,
    ProfileLoadError,
    load_profile_from_file,
    load_profile_from_dict,
    load_embedded_profiles,
    read_default_profile_name,
)

# Add to __all__:
__all__ = [
    # ... existing exports ...
    "ProfileError",
    "ProfileLoadError",
    "load_profile_from_file",
    "load_profile_from_dict",
    "load_embedded_profiles",
    "read_default_profile_name",
]
```

---

## 4. Decision Tree: File Loading Flow

```
Input: path (str | Path)
│
├── File exists?
│   └── NO → FileNotFoundError
│
├── Is a file (not directory)?
│   └── NO → ProfileLoadError("not a file")
│
├── Extension supported? (.yaml, .yml, .json)
│   └── NO → ProfileLoadError("unsupported format")
│
├── Read file content
│   └── FAIL → ProfileLoadError("cannot read")
│
├── Parse YAML or JSON
│   └── FAIL → ProfileLoadError("parse error")
│
├── Parsed result is a dict?
│   └── NO → ProfileLoadError("must be a mapping")
│
├── Parsed result is empty (None)?
│   └── YES → ProfileLoadError("file is empty")
│
├── Track source_keys = set(dict.keys())
│
├── Construct ValidationProfile(**dict)
│   └── FAIL → ProfileLoadError with field-level errors
│
├── profile.extends is set?
│   │
│   ├── YES + resolver provided → resolve_inheritance()
│   │   └── FAIL → ProfileLoadError("inheritance failed")
│   │
│   ├── YES + no resolver → WARNING logged, extends not resolved
│   │
│   └── NO → skip
│
└── Return (profile, source_keys)
```

---

## 5. Workflow

### 5.1 Loading a Standalone Profile

```yaml
# tests/fixtures/profiles/strict-ci.yaml
profile_name: "strict-ci"
description: "CI with strict threshold"
pass_threshold: 80
severity_overrides:
  W003: "ERROR"
extends: "ci"
```

```python
from docstratum.profiles.loading import load_profile_from_file
from docstratum.profiles.builtins import get_builtin_profile

profile, source_keys = load_profile_from_file(
    "./strict-ci.yaml",
    profile_resolver=get_builtin_profile,
)

assert profile.profile_name == "strict-ci"
assert profile.pass_threshold == 80
assert profile.max_validation_level == 3  # inherited from ci
assert profile.output_format == "json"     # inherited from ci
assert profile.extends is None             # flattened
assert source_keys == {
    "profile_name", "description", "pass_threshold",
    "severity_overrides", "extends",
}
```

### 5.2 Loading Embedded Profiles

```yaml
# .docstratum.yml
default_profile: "strict-ci"

profiles:
  strict-ci:
    description: "Strict CI"
    pass_threshold: 80
    extends: "ci"

  team-full:
    description: "Full for team"
    output_format: "html"
    extends: "full"
```

```python
from docstratum.profiles.loading import (
    load_embedded_profiles,
    read_default_profile_name,
)

# Read default
default = read_default_profile_name(".docstratum.yml")
assert default == "strict-ci"

# Load all embedded profiles
profiles = load_embedded_profiles(
    ".docstratum.yml",
    profile_resolver=get_builtin_profile,
)

strict_ci, keys = profiles["strict-ci"]
assert strict_ci.pass_threshold == 80
assert strict_ci.extends is None  # resolved

team_full, keys = profiles["team-full"]
assert team_full.output_format == "html"
```

### 5.3 Handling Errors

```python
# Missing file
try:
    load_profile_from_file("./nonexistent.yaml")
except FileNotFoundError as e:
    print(e)  # "Profile file not found: /path/to/nonexistent.yaml"

# Invalid YAML
try:
    load_profile_from_file("./broken.yaml")
except ProfileLoadError as e:
    print(e)  # "YAML parse error in /path/to/broken.yaml: ..."

# Validation error
try:
    load_profile_from_dict({"profile_name": "bad", "max_validation_level": 99})
except ProfileLoadError as e:
    print(e)
    # "Profile validation failed:
    #   max_validation_level: Input should be less than or equal to 4"
    print(e.field_errors)
    # [{"field": "max_validation_level", "type": "less_than_equal", ...}]
```

### 5.4 Development Cycle

```bash
# Run loading tests
pytest tests/test_profile_loading.py -v

# Type check
mypy src/docstratum/profiles/loading.py

# Format + lint
black src/docstratum/profiles/loading.py
ruff check src/docstratum/profiles/loading.py
```

---

## 6. Edge Cases

| Scenario | Input | Behavior |
|----------|-------|----------|
| File not found | `load_profile_from_file("./x.yaml")` | `FileNotFoundError` |
| Directory instead of file | `load_profile_from_file("./profiles/")` | `ProfileLoadError("not a file")` |
| Unsupported extension | `load_profile_from_file("./p.toml")` | `ProfileLoadError("unsupported format")` |
| Empty YAML file | File content is `""` | `ProfileLoadError("file is empty")` |
| YAML with only `---` | File content is `---\n` | `ProfileLoadError("file is empty")` — `yaml.safe_load("---\n")` returns `None` |
| YAML with a scalar | File content is `"hello"` | `ProfileLoadError("must be a mapping")` |
| YAML with a list | File content is `- item` | `ProfileLoadError("must be a mapping")` |
| Profile missing `profile_name` | `{"max_level": 3}` | `ProfileLoadError` from Pydantic |
| Unknown field | `{"profile_name": "t", "unknown": 1}` | `ProfileLoadError` (extra fields forbidden) |
| `extends` with no resolver | `{"profile_name": "t", "extends": "ci"}`, resolver=None | Warning logged, `extends` not resolved |
| `extends` base not found | `extends: "nonexistent"` | `ProfileLoadError("inheritance failed")` |
| Embedded profile key ≠ profile_name | Key="foo", `profile_name: "bar"` | Warning logged, "bar" wins |
| Embedded profile key = profile_name | Key="foo", `profile_name: "foo"` | No warning, "foo" used |
| Embedded profile no profile_name | Key="foo", no `profile_name` field | `profile_name` inferred as "foo" |
| `default_profile` not a string | `default_profile: 42` | `read_default_profile_name()` returns `None` |
| `default_profile` empty string | `default_profile: ""` | `read_default_profile_name()` returns `None` |
| `.docstratum.yml` no `profiles:` section | Config has only `default_profile:` | `load_embedded_profiles()` returns `{}` |
| JSON profile with comments | `// comment` in JSON | `ProfileLoadError` — JSON doesn't support comments |
| YAML `yes`/`no` as boolean | `check_urls: yes` | PyYAML reads as `True` — Pydantic may reject if it expects string |
| UTF-8 BOM in file | BOM at start of YAML | PyYAML handles BOM; no issue |
| Very large profile file | >1MB YAML | Loaded normally; no size limit enforced |

---

## 7. Acceptance Criteria

- [ ] `load_profile_from_file()` loads a valid YAML profile and returns `(ValidationProfile, source_keys)`
- [ ] `load_profile_from_file()` loads a valid JSON profile
- [ ] `load_profile_from_file()` raises `FileNotFoundError` for missing files
- [ ] `load_profile_from_file()` raises `ProfileLoadError` for unsupported extensions
- [ ] `load_profile_from_file()` raises `ProfileLoadError` for invalid YAML/JSON
- [ ] `load_profile_from_file()` raises `ProfileLoadError` with field-level errors for invalid profiles
- [ ] Source keys are accurately tracked (keys present in raw dict, not Pydantic defaults)
- [ ] `extends` is resolved when `profile_resolver` is provided
- [ ] `extends` produces a warning (not error) when `profile_resolver` is None
- [ ] `load_profile_from_dict()` accepts a pre-parsed dictionary
- [ ] `load_profile_from_dict()` applies `profile_name_fallback` when `profile_name` is absent
- [ ] `load_profile_from_dict()` warns when fallback name differs from explicit name
- [ ] `load_embedded_profiles()` loads all profiles from `.docstratum.yml` `profiles:` section
- [ ] `load_embedded_profiles()` returns empty dict when no `profiles:` section exists
- [ ] `read_default_profile_name()` reads the `default_profile` key
- [ ] `read_default_profile_name()` returns `None` when key is absent or file is missing
- [ ] `ProfileLoadError` includes `source_path` and `field_errors` attributes
- [ ] All error messages include the file path
- [ ] Module docstring cites v0.5.2a and grounding specs
- [ ] All public functions have Google-style docstrings

---

## 8. Deliverables

| File | Description | Status |
|------|-------------|--------|
| `src/docstratum/profiles/loading.py` | Profile file loader + embedded loader | NEW |
| `src/docstratum/profiles/__init__.py` | Updated to re-export loading functions | MODIFY |
| `tests/test_profile_loading.py` | Unit tests for file and dict loading | NEW |
| `tests/fixtures/profiles/` | Test fixture directory with sample profiles | NEW |
| `tests/fixtures/profiles/valid-minimal.yaml` | Minimal valid YAML profile | NEW |
| `tests/fixtures/profiles/valid-full.yaml` | Full YAML profile with all fields | NEW |
| `tests/fixtures/profiles/valid-with-extends.yaml` | Profile with `extends` | NEW |
| `tests/fixtures/profiles/valid.json` | Valid JSON profile | NEW |
| `tests/fixtures/profiles/invalid-field.yaml` | Profile with out-of-range field | NEW |
| `tests/fixtures/profiles/broken-yaml.yaml` | Malformed YAML | NEW |
| `tests/fixtures/docstratum-with-profiles.yml` | Embedded profiles config | NEW |

---

## 9. Test Plan (22 tests)

### 9.1 File Loading Tests

| # | Test Name | Input | Expected |
|---|-----------|-------|----------|
| 1 | `test_load_yaml_file` | Valid `.yaml` file | Profile loaded, correct values |
| 2 | `test_load_yml_file` | Valid `.yml` file | Profile loaded (alias) |
| 3 | `test_load_json_file` | Valid `.json` file | Profile loaded |
| 4 | `test_source_keys_tracked` | YAML with 3 fields | `source_keys` = those 3 field names |
| 5 | `test_extends_resolved` | Profile with `extends: "ci"` | Inheritance resolved, `extends=None` |
| 6 | `test_extends_no_resolver` | Profile with `extends`, no resolver | Warning logged, `extends` not resolved |
| 7 | `test_file_not_found` | Non-existent path | `FileNotFoundError` |
| 8 | `test_unsupported_extension` | `.toml` file | `ProfileLoadError` |
| 9 | `test_empty_file` | Empty YAML | `ProfileLoadError` |
| 10 | `test_yaml_parse_error` | Broken YAML syntax | `ProfileLoadError` |
| 11 | `test_json_parse_error` | Broken JSON | `ProfileLoadError` |
| 12 | `test_validation_error_detail` | `max_validation_level: 99` | `ProfileLoadError` with `field_errors` |
| 13 | `test_scalar_not_dict` | YAML file with just `"hello"` | `ProfileLoadError("must be a mapping")` |

### 9.2 Dict Loading Tests

| # | Test Name | Input | Expected |
|---|-----------|-------|----------|
| 14 | `test_load_dict_minimal` | `{"profile_name": "t"}` | Profile with defaults |
| 15 | `test_load_dict_with_fallback_name` | No `profile_name`, fallback="foo" | `profile_name="foo"` |
| 16 | `test_load_dict_name_mismatch_warns` | Key="foo", `profile_name="bar"` | Warning logged |

### 9.3 Embedded Profile Tests

| # | Test Name | Input | Expected |
|---|-----------|-------|----------|
| 17 | `test_embedded_profiles_loaded` | `.docstratum.yml` with 2 profiles | Both loaded |
| 18 | `test_embedded_no_profiles_section` | Config without `profiles:` | Returns `{}` |
| 19 | `test_embedded_profile_name_inferred` | No explicit `profile_name` | Inferred from key |
| 20 | `test_read_default_profile_name` | `default_profile: "full"` | Returns `"full"` |
| 21 | `test_read_default_absent` | No `default_profile` key | Returns `None` |
| 22 | `test_read_default_file_missing` | Non-existent `.docstratum.yml` | Returns `None` |

```python
"""Tests for v0.5.2a — Profile Loading.

Validates file-based and dict-based profile loading, source key
tracking, inheritance resolution, and error handling.
"""

from pathlib import Path

import pytest

from docstratum.profiles.loading import (
    ProfileLoadError,
    load_profile_from_file,
    load_profile_from_dict,
    load_embedded_profiles,
    read_default_profile_name,
)
from docstratum.profiles.builtins import get_builtin_profile

FIXTURES = Path(__file__).parent / "fixtures" / "profiles"


class TestFileLoading:
    """Test loading profiles from YAML/JSON files."""

    def test_load_yaml_file(self):
        profile, keys = load_profile_from_file(FIXTURES / "valid-minimal.yaml")
        assert profile.profile_name == "minimal"
        assert "profile_name" in keys

    def test_source_keys_tracked(self):
        profile, keys = load_profile_from_file(FIXTURES / "valid-full.yaml")
        # All explicitly set fields should be in source_keys
        assert "max_validation_level" in keys
        assert "pass_threshold" in keys

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_profile_from_file("./nonexistent.yaml")

    def test_unsupported_extension(self, tmp_path):
        toml_file = tmp_path / "profile.toml"
        toml_file.write_text("[profile]\nname = 'test'\n")
        with pytest.raises(ProfileLoadError, match="Unsupported"):
            load_profile_from_file(toml_file)

    def test_validation_error_includes_detail(self, tmp_path):
        bad_file = tmp_path / "bad.yaml"
        bad_file.write_text("profile_name: test\nmax_validation_level: 99\n")
        with pytest.raises(ProfileLoadError) as exc_info:
            load_profile_from_file(bad_file)
        assert exc_info.value.field_errors
        assert any(
            "max_validation_level" in e["field"]
            for e in exc_info.value.field_errors
        )


class TestEmbeddedLoading:
    """Test loading embedded profiles from .docstratum.yml."""

    def test_embedded_profiles_loaded(self):
        profiles = load_embedded_profiles(
            FIXTURES / ".." / "docstratum-with-profiles.yml",
            profile_resolver=get_builtin_profile,
        )
        assert "strict-ci" in profiles

    def test_no_profiles_section(self, tmp_path):
        config = tmp_path / ".docstratum.yml"
        config.write_text("default_profile: ci\n")
        result = load_embedded_profiles(config)
        assert result == {}
```

---

## 10. Limitations

| Limitation | Impact | Resolution |
|------------|--------|------------|
| PyYAML YAML 1.1 only | Bare `yes`/`no` → booleans; YAML 1.2 features unsupported | Document in profile authoring guide |
| No JSON comments | JSON profiles cannot contain comments | Use YAML if comments are needed |
| No schema version detection | Cannot detect profiles written for future schema versions | Future consideration |
| No file locking | Concurrent writes to profile files may cause parse errors | Unlikely in practice; OS-level concern |
| No streaming parser | Entire file loaded into memory | Profiles are small (< a few KB) |
