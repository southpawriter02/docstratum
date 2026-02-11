# v0.5.2b — Discovery Precedence

> **Version:** v0.5.2b
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.5.2-discovery-and-configuration.md](RR-SPEC-v0.5.2-discovery-and-configuration.md)
> **Grounding:** RR-SPEC-v0.1.3-validation-profiles.md §5.1 (Discovery Order), §5.2 (Default Profile)
> **Depends On:** v0.5.2a (`load_profile_from_file`, `load_embedded_profiles`, `read_default_profile_name`, `ProfileLoadError`), v0.5.1b (`get_builtin_profile`, `list_builtin_profiles`, `is_builtin_profile`)
> **Module:** `src/docstratum/profiles/discovery.py`
> **Tests:** `tests/test_profile_discovery.py`

---

## 1. Purpose

Implement the **4-source profile discovery chain** — the resolution algorithm that transforms a profile specifier (a name like `"ci"` or a file path like `"./strict.yaml"`) into a fully loaded, validated `ValidationProfile` instance. The discovery chain defines *where* profiles are searched and *in what order*, ensuring deterministic resolution with clear "not found" diagnostics.

After v0.5.2b:

```bash
# Direct file path → Source 1 (CLI flag)
docstratum validate llms.txt --profile ./custom.yaml

# Name resolved via project config → Source 2
docstratum validate llms.txt --profile strict-ci
# Found in .docstratum.yml → profiles.strict-ci

# Name resolved via user config → Source 3
docstratum validate llms.txt --profile personal
# Found in ~/.docstratum/profiles/personal.yaml

# Name resolved via built-in → Source 4
docstratum validate llms.txt --profile lint
# Matched built-in profile "lint"

# No --profile flag → default
docstratum validate llms.txt
# Uses default_profile from .docstratum.yml, or "ci" if no config
```

### 1.1 User Stories

> **US-1:** As a developer running `--profile strict-ci`, I want the CLI to search my project's `.docstratum.yml` first, then my personal `~/.docstratum/profiles/`, then built-ins, so that project-level settings override personal ones, and personal ones override defaults.

> **US-2:** As a developer who provides `--profile ./custom.yaml`, I want it treated as a direct file path (no search chain), so that I can unambiguously load a specific file.

> **US-3:** As a developer who doesn't pass `--profile`, I want the CLI to check `.docstratum.yml` for a `default_profile` key, and fall back to `"ci"` if none is set, so that the tool works sensibly out of the box.

> **US-4:** As a developer who misspells a profile name, I want an error listing every location that was searched, so that I can figure out where the profile should exist.

---

## 2. Precedence Table

| Priority | Source | Trigger | Location | Notes |
|----------|--------|---------|----------|-------|
| 1 | **CLI flag (file path)** | `--profile` ends with `.yaml`, `.yml`, or `.json` | The literal file path | Direct load; no search chain |
| 2 | **Project config** | `--profile <name>` (no extension) | `.docstratum.yml` → `profiles.<name>` section | Searched in CWD, then parent directories (up to root) |
| 3 | **User config** | `--profile <name>` (no extension) | `~/.docstratum/profiles/<name>.yaml` or `.json` | User's home directory |
| 4 | **Built-in** | `--profile <name>` (no extension) | Package-bundled Python constants | `lint`, `ci`, `full`, `enterprise` |

### 2.1 `.docstratum.yml` Search Path

The discovery chain searches for `.docstratum.yml` starting from the current working directory and walking up to the filesystem root. This matches the convention used by tools like `.gitignore`, `.editorconfig`, and `pyproject.toml`.

**Walk algorithm:**

```python
def _find_config_file() -> Path | None:
    """Find .docstratum.yml by walking up from CWD."""
    current = Path.cwd().resolve()
    while True:
        candidate = current / ".docstratum.yml"
        if candidate.is_file():
            return candidate
        parent = current.parent
        if parent == current:
            return None  # reached root
        current = parent
```

This means a project at `/Users/dev/project/` with a `.docstratum.yml` in `project/` will find it regardless of whether the user runs `docstratum` from `project/`, `project/src/`, or `project/docs/`.

### 2.2 User Config Directory

The user config directory is `~/.docstratum/profiles/`. On each operating system:

| OS | Path |
|----|------|
| macOS | `/Users/<user>/.docstratum/profiles/` |
| Linux | `/home/<user>/.docstratum/profiles/` |
| Windows | `C:\Users\<user>\.docstratum\profiles\` |

The directory is **not auto-created**. If it doesn't exist, Source 3 is simply skipped. A future `docstratum init` command may create it.

---

## 3. Implementation

### 3.1 Types and Constants

```python
# src/docstratum/profiles/discovery.py
"""Profile discovery chain — resolves profile names to ValidationProfile instances.

Implements the 4-source lookup: CLI file path > project config >
user config > built-in. Provides exhaustive "not found" diagnostics.

Implements v0.5.2b.
Grounding: RR-SPEC-v0.1.3-validation-profiles.md §5.1–§5.2.
DECISION-041: Discovery chain as profile_resolver for inheritance.
"""

from __future__ import annotations

import logging
from enum import Enum
from pathlib import Path
from typing import Optional

from docstratum.profiles.builtins import (
    get_builtin_profile,
    is_builtin_profile,
    list_builtin_profiles,
)
from docstratum.profiles.loading import (
    ProfileError,
    ProfileLoadError,
    load_embedded_profiles,
    load_profile_from_file,
    read_default_profile_name,
)
from docstratum.profiles.model import ValidationProfile

logger = logging.getLogger(__name__)

# DECISION-041: Default profile name when no config exists.
DEFAULT_PROFILE_NAME: str = "ci"

# File extensions that indicate a file path (not a profile name).
_FILE_EXTENSIONS: frozenset[str] = frozenset({".yaml", ".yml", ".json"})

# Config file name.
_CONFIG_FILENAME: str = ".docstratum.yml"

# User config directory (relative to home).
_USER_PROFILES_DIR: str = ".docstratum/profiles"


class ProfileSource(Enum):
    """Tracks where a profile was loaded from.

    Used for logging, diagnostics, and error messages.
    """
    CLI_FILE = "cli_file"          # Direct file path via --profile
    PROJECT_CONFIG = "project"     # .docstratum.yml profiles: section
    USER_CONFIG = "user"           # ~/.docstratum/profiles/
    BUILTIN = "builtin"            # Package-bundled profile
    DEFAULT = "default"            # No --profile flag; resolved default


class ProfileNotFoundError(ProfileError):
    """Raised when a profile cannot be found in any source.

    Attributes:
        profile_spec: The profile specifier that was searched.
        searched_locations: Ordered list of (source, path, detail) tuples
            describing where was searched.
    """

    def __init__(
        self,
        profile_spec: str,
        searched_locations: list[tuple[str, str, str]],
    ):
        self.profile_spec = profile_spec
        self.searched_locations = searched_locations

        lines = [f"Profile '{profile_spec}' not found."]
        lines.append("Searched:")
        for i, (source, path, detail) in enumerate(searched_locations, 1):
            lines.append(f"  {i}. {source}: {path} ({detail})")
        message = "\n".join(lines)
        super().__init__(message)
```

### 3.2 Discovery Function

```python
def discover_profile(
    profile_spec: str | None = None,
    *,
    config_search_dir: Path | None = None,
    _resolution_stack: set[str] | None = None,
) -> tuple[ValidationProfile, ProfileSource]:
    """Resolve a profile specifier to a ValidationProfile instance.

    This is the main entry point for profile resolution. It implements
    the 4-source lookup chain:

    1. CLI file path (if spec ends with .yaml/.yml/.json)
    2. Project config (.docstratum.yml → profiles.<name>)
    3. User config (~/.docstratum/profiles/<name>.yaml|.json)
    4. Built-in profiles (lint, ci, full, enterprise)

    If profile_spec is None, the default profile is resolved:
    - Check .docstratum.yml for default_profile key
    - Fall back to "ci"

    Args:
        profile_spec: Profile name or file path from --profile flag.
            None when --profile is not provided.
        config_search_dir: Starting directory for .docstratum.yml search.
            Defaults to CWD. Used for testing.
        _resolution_stack: Internal. Set of profile names currently being
            resolved (for circular dependency detection).

    Returns:
        A tuple of (ValidationProfile, ProfileSource) indicating the
        loaded profile and where it was found.

    Raises:
        FileNotFoundError: If profile_spec is a file path that doesn't exist.
        ProfileLoadError: If the profile file or config is malformed.
        ProfileNotFoundError: If the profile name cannot be found in
            any source.

    Example:
        >>> profile, source = discover_profile("lint")
        >>> profile.profile_name
        'lint'
        >>> source
        <ProfileSource.BUILTIN: 'builtin'>

        >>> profile, source = discover_profile("./custom.yaml")
        >>> source
        <ProfileSource.CLI_FILE: 'cli_file'>

        >>> profile, source = discover_profile(None)
        >>> profile.profile_name
        'ci'
        >>> source
        <ProfileSource.DEFAULT: 'default'>

    Grounding: RR-SPEC-v0.1.3-validation-profiles.md §5.1.
    """
    if _resolution_stack is None:
        _resolution_stack = set()

    start_dir = config_search_dir or Path.cwd()

    # --- Step 0: Resolve default when spec is None ---
    if profile_spec is None:
        return _resolve_default(start_dir, _resolution_stack)

    # --- Step 1: Is it a file path? ---
    if _is_file_path(profile_spec):
        return _resolve_from_file(profile_spec, _resolution_stack)

    # --- Step 2–4: Name-based resolution ---
    return _resolve_by_name(
        profile_spec, start_dir, _resolution_stack
    )


def _is_file_path(spec: str) -> bool:
    """Check if a profile spec looks like a file path.

    A spec is a file path if it ends with a supported extension.
    This matches the convention that profile names never contain dots
    (e.g., "ci", "lint"), while file paths always have extensions.
    """
    # Also treat paths with directory separators as file paths
    if "/" in spec or "\\" in spec:
        return True
    suffix = Path(spec).suffix.lower()
    return suffix in _FILE_EXTENSIONS
```

### 3.3 Internal Resolution Functions

```python
def _resolve_default(
    start_dir: Path,
    resolution_stack: set[str],
) -> tuple[ValidationProfile, ProfileSource]:
    """Resolve the default profile when no --profile flag is provided.

    1. Check .docstratum.yml for default_profile key
    2. Fall back to "ci"
    """
    config_path = _find_config_file(start_dir)

    if config_path is not None:
        default_name = read_default_profile_name(config_path)
        if default_name is not None:
            logger.info(
                "Default profile from %s: '%s'",
                config_path,
                default_name,
            )
            profile, source = _resolve_by_name(
                default_name, start_dir, resolution_stack
            )
            return profile, ProfileSource.DEFAULT
        else:
            logger.debug(
                "No default_profile key in %s. Using '%s'.",
                config_path,
                DEFAULT_PROFILE_NAME,
            )
    else:
        logger.debug(
            "No %s found. Using default profile '%s'.",
            _CONFIG_FILENAME,
            DEFAULT_PROFILE_NAME,
        )

    # Fall back to built-in default
    profile = get_builtin_profile(DEFAULT_PROFILE_NAME)
    return profile, ProfileSource.DEFAULT


def _resolve_from_file(
    spec: str,
    resolution_stack: set[str],
) -> tuple[ValidationProfile, ProfileSource]:
    """Resolve a profile from a direct file path."""
    file_path = Path(spec).resolve()

    # Build a resolver that recurses through the discovery chain
    # for inheritance (DECISION-041).
    def _resolver(name: str) -> ValidationProfile:
        if name in resolution_stack:
            from docstratum.profiles.inheritance import InheritanceError
            raise InheritanceError(
                f"Circular dependency detected: '{name}' is already "
                f"being resolved. Stack: {resolution_stack}"
            )
        resolution_stack.add(name)
        try:
            profile, _ = discover_profile(
                name,
                _resolution_stack=resolution_stack,
            )
            return profile
        finally:
            resolution_stack.discard(name)

    profile, _source_keys = load_profile_from_file(
        file_path,
        profile_resolver=_resolver,
    )
    logger.info(
        "Profile '%s' loaded from CLI file path: %s",
        profile.profile_name,
        file_path,
    )
    return profile, ProfileSource.CLI_FILE


def _resolve_by_name(
    name: str,
    start_dir: Path,
    resolution_stack: set[str],
) -> tuple[ValidationProfile, ProfileSource]:
    """Resolve a profile by name through the 3-source chain.

    Source 2: Project config (.docstratum.yml)
    Source 3: User config (~/.docstratum/profiles/)
    Source 4: Built-in

    Collects search diagnostics for error reporting.
    """
    searched: list[tuple[str, str, str]] = []

    # Guard against circular resolution
    if name in resolution_stack:
        from docstratum.profiles.inheritance import InheritanceError
        raise InheritanceError(
            f"Circular dependency detected: '{name}' is already "
            f"being resolved. Stack: {resolution_stack}"
        )

    # Build resolver for inheritance within discovered profiles
    def _resolver(base_name: str) -> ValidationProfile:
        resolution_stack.add(name)
        try:
            profile, _ = discover_profile(
                base_name,
                config_search_dir=start_dir,
                _resolution_stack=resolution_stack,
            )
            return profile
        finally:
            resolution_stack.discard(name)

    # --- Source 2: Project config (.docstratum.yml) ---
    config_path = _find_config_file(start_dir)
    if config_path is not None:
        try:
            embedded = load_embedded_profiles(
                config_path,
                profile_resolver=_resolver,
            )
            if name in embedded:
                profile, _source_keys = embedded[name]
                logger.info(
                    "Profile '%s' found in project config: %s",
                    name,
                    config_path,
                )
                return profile, ProfileSource.PROJECT_CONFIG
            else:
                profiles_section = "profiles" if embedded else "no 'profiles' section"
                searched.append((
                    _CONFIG_FILENAME,
                    str(config_path),
                    f"profile '{name}' not in {profiles_section}"
                    if embedded
                    else "no 'profiles' section",
                ))
        except ProfileLoadError as e:
            logger.warning(
                "Error reading project config %s: %s",
                config_path,
                e,
            )
            searched.append((
                _CONFIG_FILENAME,
                str(config_path),
                f"error: {e}",
            ))
    else:
        searched.append((
            _CONFIG_FILENAME,
            _CONFIG_FILENAME,
            "file not found",
        ))

    # --- Source 3: User config (~/.docstratum/profiles/) ---
    user_profiles_dir = Path.home() / _USER_PROFILES_DIR
    user_yaml = user_profiles_dir / f"{name}.yaml"
    user_yml = user_profiles_dir / f"{name}.yml"
    user_json = user_profiles_dir / f"{name}.json"

    for user_path in [user_yaml, user_yml, user_json]:
        if user_path.is_file():
            profile, _source_keys = load_profile_from_file(
                user_path,
                profile_resolver=_resolver,
            )
            logger.info(
                "Profile '%s' found in user config: %s",
                name,
                user_path,
            )
            return profile, ProfileSource.USER_CONFIG

    # Record what we searched
    if user_profiles_dir.is_dir():
        searched.append((
            "User config",
            str(user_profiles_dir),
            f"{name}.yaml/.yml/.json not found",
        ))
    else:
        searched.append((
            "User config",
            str(user_profiles_dir),
            "directory does not exist",
        ))

    # --- Source 4: Built-in ---
    if is_builtin_profile(name):
        profile = get_builtin_profile(name)
        logger.info("Profile '%s' resolved as built-in.", name)
        return profile, ProfileSource.BUILTIN

    available_builtins = ", ".join(sorted(list_builtin_profiles()))
    searched.append((
        "Built-in profiles",
        f"[{available_builtins}]",
        f"'{name}' is not a built-in",
    ))

    # --- Not found ---
    raise ProfileNotFoundError(name, searched)


def _find_config_file(start_dir: Path) -> Path | None:
    """Find .docstratum.yml by walking up from start_dir.

    Searches the start directory and all parent directories up to
    the filesystem root.

    Returns:
        Path to .docstratum.yml, or None if not found.
    """
    current = start_dir.resolve()
    while True:
        candidate = current / _CONFIG_FILENAME
        if candidate.is_file():
            logger.debug("Config file found: %s", candidate)
            return candidate
        parent = current.parent
        if parent == current:
            return None  # Reached filesystem root
        current = parent
```

### 3.4 Package Re-exports

```python
# Update src/docstratum/profiles/__init__.py
# Add to existing exports:
from docstratum.profiles.discovery import (
    ProfileNotFoundError,
    ProfileSource,
    discover_profile,
    DEFAULT_PROFILE_NAME,
)

# Add to __all__:
__all__ = [
    # ... existing exports ...
    "ProfileNotFoundError",
    "ProfileSource",
    "discover_profile",
    "DEFAULT_PROFILE_NAME",
]
```

---

## 4. Decision Tree: Discovery Algorithm

```
Input: profile_spec (str | None)
│
├── profile_spec is None?
│   └── YES → _resolve_default()
│       │
│       ├── Find .docstratum.yml (walk up from CWD)
│       │   ├── FOUND → read default_profile key
│       │   │   ├── Key present → resolve by name (Steps 2–4)
│       │   │   └── Key absent → use "ci"
│       │   └── NOT FOUND → use "ci"
│       │
│       └── Return (profile, ProfileSource.DEFAULT)
│
├── profile_spec looks like a file path? (extension or separator)
│   └── YES → _resolve_from_file()
│       │
│       ├── File exists?
│       │   ├── YES → load_profile_from_file()
│       │   │   └── Return (profile, ProfileSource.CLI_FILE)
│       │   └── NO → FileNotFoundError
│       │
│       └── (no fallback search for file paths)
│
└── profile_spec is a name (no extension, no path separator)
    └── _resolve_by_name()
        │
        ├── Source 2: Check .docstratum.yml → profiles.<name>
        │   ├── Config found + name in profiles → Return (profile, PROJECT_CONFIG)
        │   └── Not found → continue
        │
        ├── Source 3: Check ~/.docstratum/profiles/<name>.yaml|.yml|.json
        │   ├── File found → load → Return (profile, USER_CONFIG)
        │   └── Not found → continue
        │
        ├── Source 4: Check built-in profiles
        │   ├── Name is built-in → Return (profile, BUILTIN)
        │   └── Not built-in → continue
        │
        └── ProfileNotFoundError (lists all searched locations)
```

---

## 5. Error Messages

### 5.1 Profile Not Found

When a name-based lookup exhausts all sources:

```
Error: Profile 'ecosystem-strict' not found.
Searched:
  1. .docstratum.yml: /Users/dev/project/.docstratum.yml (profile 'ecosystem-strict' not in profiles)
  2. User config: /Users/dev/.docstratum/profiles (ecosystem-strict.yaml/.yml/.json not found)
  3. Built-in profiles: [ci, enterprise, full, lint] ('ecosystem-strict' is not a built-in)
```

### 5.2 Config File Not Found

When no `.docstratum.yml` exists:

```
Error: Profile 'ecosystem-strict' not found.
Searched:
  1. .docstratum.yml: .docstratum.yml (file not found)
  2. User config: /Users/dev/.docstratum/profiles (directory does not exist)
  3. Built-in profiles: [ci, enterprise, full, lint] ('ecosystem-strict' is not a built-in)
```

### 5.3 File Path Not Found

When `--profile ./custom.yaml` points to a nonexistent file:

```
Error: Profile file not found: /Users/dev/project/custom.yaml
```

This is a `FileNotFoundError`, not a `ProfileNotFoundError` — we don't fall back to name lookup when the user explicitly specified a file path.

---

## 6. Workflow

### 6.1 End-to-End Discovery Example

```python
from docstratum.profiles.discovery import discover_profile, ProfileSource

# Built-in
profile, source = discover_profile("lint")
assert profile.profile_name == "lint"
assert source == ProfileSource.BUILTIN

# Default (no --profile)
profile, source = discover_profile(None)
assert profile.profile_name == "ci"  # or whatever default_profile is
assert source == ProfileSource.DEFAULT

# File path
profile, source = discover_profile("./strict-ci.yaml")
assert source == ProfileSource.CLI_FILE

# Not found
from docstratum.profiles.discovery import ProfileNotFoundError
try:
    discover_profile("nonexistent")
except ProfileNotFoundError as e:
    print(e)
    # Lists all searched locations
```

### 6.2 Discovery as Inheritance Resolver

The discovery chain is injected as the `profile_resolver` for inheritance (DECISION-041):

```yaml
# user-profile.yaml
profile_name: "user-strict"
pass_threshold: 90
extends: "full"     # "full" resolved via discovery chain
```

When `load_profile_from_file("user-profile.yaml")` encounters `extends: "full"`, the resolver calls `discover_profile("full")`, which finds the built-in `full` profile. This means a user can extend any profile from any source — not just built-ins.

### 6.3 Cross-Source Inheritance

```yaml
# .docstratum.yml
profiles:
  team-base:
    description: "Team baseline"
    pass_threshold: 60

# ~/.docstratum/profiles/personal.yaml
profile_name: "personal"
extends: "team-base"     # Extends from project config!
pass_threshold: 70
```

The discovery chain resolves `"team-base"` via project config, enabling cross-source inheritance. This is possible because the resolver walks the entire chain.

---

## 7. Edge Cases

| Scenario | Behavior |
|----------|----------|
| `--profile ci` in a project with no `.docstratum.yml` | Skips Source 2/3, resolves via Source 4 (built-in) |
| `--profile lint` in a project with `.docstratum.yml` defining `lint` | Source 2 wins (project config overrides built-in) |
| `--profile lint.yaml` (name with extension but no path separator) | Treated as file path → `FileNotFoundError` if not found |
| `--profile profiles/lint.yaml` (relative path) | Treated as file path (has separator) |
| `--profile LINT` | Case-sensitive name; doesn't match built-in `"lint"` → `ProfileNotFoundError` |
| No `--profile`, `.docstratum.yml` has `default_profile: "full"` | Resolves `"full"` via discovery chain |
| No `--profile`, `.docstratum.yml` has `default_profile: "nonexistent"` | `ProfileNotFoundError` for `"nonexistent"` |
| No `--profile`, no `.docstratum.yml` | Default `"ci"` from built-in |
| `.docstratum.yml` in parent directory | Found by upward walk |
| `.docstratum.yml` in home directory | Found (walk eventually reaches home) |
| Multiple `.docstratum.yml` in ancestors | First one found wins (closest to CWD) |
| Profile extends itself | Circular dependency detected by `_resolution_stack` |
| Profile A extends B, B extends A | Circular dependency detected |
| `~/.docstratum/profiles/` does not exist | Source 3 skipped; no error |
| Both `name.yaml` and `name.json` in user dir | `.yaml` checked first (wins) |
| Empty `.docstratum.yml` | `read_default_profile_name` returns `None`; `load_embedded_profiles` returns `{}` |
| `.docstratum.yml` with broken YAML | Warning logged; Source 2 skipped with error detail |

---

## 8. Acceptance Criteria

- [ ] `discover_profile("lint")` resolves the built-in lint profile
- [ ] `discover_profile("./custom.yaml")` loads from the file path
- [ ] `discover_profile(None)` resolves the default profile (`ci`)
- [ ] `discover_profile(None)` uses `default_profile` from `.docstratum.yml` when available
- [ ] Project config (`.docstratum.yml`) takes precedence over user config
- [ ] User config (`~/.docstratum/profiles/`) takes precedence over built-in
- [ ] `ProfileNotFoundError` lists all searched locations
- [ ] File-path specs (with extension or separator) do not fall back to name lookup
- [ ] `.docstratum.yml` is found by walking up from CWD
- [ ] `ProfileSource` enum correctly tracks the resolution source
- [ ] Circular inheritance via discovery chain is detected
- [ ] Broken `.docstratum.yml` produces a warning, not a crash (Source 2 skipped)
- [ ] Case-sensitive name matching (no automatic lowercasing)
- [ ] `discover_profile` works as `profile_resolver` for inheritance (DECISION-041)
- [ ] All error messages are actionable (include paths, names, suggestions)
- [ ] Module docstring cites v0.5.2b and grounding specs
- [ ] All public functions have Google-style docstrings

---

## 9. Deliverables

| File | Description | Status |
|------|-------------|--------|
| `src/docstratum/profiles/discovery.py` | Discovery chain implementation | NEW |
| `src/docstratum/profiles/__init__.py` | Updated to re-export discovery functions | MODIFY |
| `tests/test_profile_discovery.py` | Unit tests for discovery | NEW |
| `tests/fixtures/discovery/` | Test fixture directory structure | NEW |
| `tests/fixtures/discovery/.docstratum.yml` | Project config with profiles + default | NEW |
| `tests/fixtures/discovery/custom.yaml` | Direct file path test fixture | NEW |

---

## 10. Test Plan (20 tests)

### 10.1 Default Resolution Tests

| # | Test Name | Setup | Expected |
|---|-----------|-------|----------|
| 1 | `test_default_no_config` | No `.docstratum.yml` | Built-in `ci`, `ProfileSource.DEFAULT` |
| 2 | `test_default_from_config` | `.docstratum.yml` with `default_profile: "full"` | Built-in `full`, `ProfileSource.DEFAULT` |
| 3 | `test_default_config_no_key` | `.docstratum.yml` without `default_profile` | Built-in `ci`, `ProfileSource.DEFAULT` |
| 4 | `test_default_config_nonexistent_name` | `default_profile: "nope"` | `ProfileNotFoundError` |

### 10.2 File Path Resolution Tests

| # | Test Name | Setup | Expected |
|---|-----------|-------|----------|
| 5 | `test_file_path_yaml` | `--profile ./p.yaml` (exists) | Loaded profile, `CLI_FILE` |
| 6 | `test_file_path_json` | `--profile ./p.json` (exists) | Loaded profile, `CLI_FILE` |
| 7 | `test_file_path_not_found` | `--profile ./missing.yaml` | `FileNotFoundError` |
| 8 | `test_relative_path_with_dir` | `--profile subdir/p.yaml` | Treated as file path |
| 9 | `test_name_with_extension` | `--profile lint.yaml` | Treated as file path (not name) |

### 10.3 Name Resolution Tests

| # | Test Name | Setup | Expected |
|---|-----------|-------|----------|
| 10 | `test_name_builtin` | `--profile lint` | Built-in `lint`, `BUILTIN` |
| 11 | `test_name_project_config` | `.docstratum.yml` with `profiles.custom` | `custom`, `PROJECT_CONFIG` |
| 12 | `test_name_user_config` | `~/.docstratum/profiles/personal.yaml` | `personal`, `USER_CONFIG` |
| 13 | `test_name_project_overrides_builtin` | `.docstratum.yml` defines `lint` | Project's `lint`, `PROJECT_CONFIG` |
| 14 | `test_name_not_found` | Name matches nothing | `ProfileNotFoundError` with locations |
| 15 | `test_name_case_sensitive` | `--profile LINT` | Not found (no auto-lowercase) |

### 10.4 Config Search Tests

| # | Test Name | Setup | Expected |
|---|-----------|-------|----------|
| 16 | `test_config_walk_up` | `.docstratum.yml` in parent dir | Found via walk |
| 17 | `test_config_closest_wins` | `.docstratum.yml` in CWD and parent | CWD wins |
| 18 | `test_config_broken_yaml` | Malformed `.docstratum.yml` | Warning logged, Source 2 skipped |

### 10.5 Inheritance via Discovery Tests

| # | Test Name | Setup | Expected |
|---|-----------|-------|----------|
| 19 | `test_file_extends_builtin` | File with `extends: "full"` | Inherits from built-in `full` |
| 20 | `test_circular_detection` | A extends B extends A | `InheritanceError` or `ProfileLoadError` |

```python
"""Tests for v0.5.2b — Discovery Precedence.

Validates the 4-source discovery chain, default resolution, config
file walking, and inheritance via the discovery chain.
"""

from pathlib import Path

import pytest

from docstratum.profiles.discovery import (
    ProfileNotFoundError,
    ProfileSource,
    discover_profile,
    _find_config_file,
)


class TestDefaultResolution:
    """Test default profile resolution (no --profile flag)."""

    def test_default_no_config(self, tmp_path, monkeypatch):
        """No .docstratum.yml → default 'ci'."""
        monkeypatch.chdir(tmp_path)
        profile, source = discover_profile(
            None, config_search_dir=tmp_path
        )
        assert profile.profile_name == "ci"
        assert source == ProfileSource.DEFAULT

    def test_default_from_config(self, tmp_path, monkeypatch):
        """default_profile key in .docstratum.yml → that profile."""
        config = tmp_path / ".docstratum.yml"
        config.write_text("default_profile: full\n")
        monkeypatch.chdir(tmp_path)
        profile, source = discover_profile(
            None, config_search_dir=tmp_path
        )
        assert profile.profile_name == "full"
        assert source == ProfileSource.DEFAULT


class TestFilePathResolution:
    """Test direct file path resolution."""

    def test_file_path_yaml(self, tmp_path):
        yaml_file = tmp_path / "custom.yaml"
        yaml_file.write_text('profile_name: "custom"\n')
        profile, source = discover_profile(str(yaml_file))
        assert profile.profile_name == "custom"
        assert source == ProfileSource.CLI_FILE

    def test_file_path_not_found(self):
        with pytest.raises(FileNotFoundError):
            discover_profile("./nonexistent.yaml")


class TestNameResolution:
    """Test name-based resolution through the 3-source chain."""

    def test_name_builtin(self, tmp_path):
        profile, source = discover_profile(
            "lint", config_search_dir=tmp_path
        )
        assert profile.profile_name == "lint"
        assert source == ProfileSource.BUILTIN

    def test_name_not_found(self, tmp_path):
        with pytest.raises(ProfileNotFoundError) as exc_info:
            discover_profile("nonexistent", config_search_dir=tmp_path)
        # Should list all searched locations
        assert len(exc_info.value.searched_locations) >= 3


class TestConfigWalkUp:
    """Test .docstratum.yml upward directory search."""

    def test_config_in_parent(self, tmp_path):
        config = tmp_path / ".docstratum.yml"
        config.write_text("default_profile: ci\n")
        subdir = tmp_path / "src" / "app"
        subdir.mkdir(parents=True)
        found = _find_config_file(subdir)
        assert found == config.resolve()
```

---

## 11. Limitations

| Limitation | Impact | Resolution |
|------------|--------|------------|
| No symlink resolution for `.docstratum.yml` | Symlinked config files work (resolved by `Path.resolve()`) but not explicitly tested | Low risk |
| No XDG_CONFIG_HOME support | User config hardcoded to `~/.docstratum/profiles/` | Future: respect `XDG_CONFIG_HOME` |
| No concurrent discovery | If multiple threads discover simultaneously, `_resolution_stack` is per-call | Thread-safe (each call gets its own stack) |
| Project config search walks to root | In deep directory trees, many `stat()` calls | Negligible overhead; capped by tree depth |
| No caching | Repeated discovery calls re-read files from disk | Future: add a discovery cache for performance |
| Case-sensitive names | `--profile LINT` does not match `lint` | By design; matches filesystem conventions |
