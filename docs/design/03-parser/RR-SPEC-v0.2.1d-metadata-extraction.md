# v0.2.1d — Metadata Extraction

> **Version:** v0.2.1d
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Parent:** [RR-SPEC-v0.2.1-classification-metadata.md](RR-SPEC-v0.2.1-classification-metadata.md)
> **Grounding:** [v0.0.1b §Gap Analysis Gap #5](../01-research/) (Required Metadata), `enrichment.py` (`Metadata` model — 7 fields)
> **Depends On:** v0.2.0 (`ParsedLlmsTxt.raw_content`)
> **Module:** `src/docstratum/parser/metadata.py`
> **Tests:** `tests/test_parser_metadata.py`
> **External Dependency:** `pyyaml`

---

## 1. Purpose

Check for YAML frontmatter at the top of the file and extract it into a `Metadata` model instance. Frontmatter is a de facto standard in documentation ecosystems (Hugo, Jekyll, Docusaurus) but is **not** part of the `llms.txt` spec. Its presence is informational — DocStratum uses it for provenance tracking, not validation gating.

> **Scope Clarification:** The RR-SCOPE-v0.2.x-parser.md noted that the `Metadata` model in `enrichment.py` was not yet implemented. As of v0.1.2d, the `Metadata` model **does exist** in `enrichment.py` with the following fields: `schema_version`, `site_name`, `site_url`, `last_updated`, `generator`, `docstratum_version`, `token_budget_tier`. No model amendments are needed — this sub-part implements the extraction logic only.

---

## 2. Interface Contract

```python
def extract_metadata(raw_content: str) -> Metadata | None:
    """Extract YAML frontmatter metadata from raw file content.

    Checks if the content starts with a YAML frontmatter block
    delimited by '---' lines. If present, parses the YAML and
    maps recognized keys to a Metadata model instance.

    Args:
        raw_content: Complete file content (decoded string).

    Returns:
        A Metadata instance if valid frontmatter is found, None otherwise.
        Returns None for:
        - No frontmatter delimiters
        - Malformed YAML (parse error)
        - Empty frontmatter block

    Example:
        >>> content = "---\\nsite_name: My Project\\ngenerator: docusaurus\\n---\\n# My Project\\n"
        >>> meta = extract_metadata(content)
        >>> meta.site_name
        'My Project'
        >>> meta.generator
        'docusaurus'
        >>> meta.schema_version
        '0.1.0'  # default

        >>> extract_metadata("# No frontmatter\\n")
        None
    """
```

---

## 3. Frontmatter Detection

### 3.1 Format

YAML frontmatter follows this structure:

```markdown
---
key1: value1
key2: value2
---

# Document Title
```

Rules:

1. The opening `---` must be the **first line** of the file (after optional leading whitespace/blank lines — see 3.2).
2. The closing `---` must appear on its own line.
3. Content between the delimiters is parsed as YAML.
4. Content after the closing `---` is the document body.

### 3.2 Detection Algorithm

```python
import yaml
from docstratum.schema.enrichment import Metadata


def extract_metadata(raw_content: str) -> Metadata | None:
    """Extract YAML frontmatter from raw content."""
    frontmatter_text = _extract_frontmatter_text(raw_content)
    if frontmatter_text is None:
        return None

    raw_dict = _parse_yaml(frontmatter_text)
    if raw_dict is None:
        return None

    return _map_to_metadata(raw_dict)


def _extract_frontmatter_text(content: str) -> str | None:
    """Extract the text between opening and closing --- delimiters.

    Returns:
        The text between delimiters, or None if no valid
        frontmatter block is found.
    """
    lines = content.splitlines(keepends=True)

    # Skip leading blank lines
    start_idx = 0
    while start_idx < len(lines) and lines[start_idx].strip() == "":
        start_idx += 1

    # Check for opening delimiter
    if start_idx >= len(lines) or lines[start_idx].strip() != "---":
        return None

    # Find closing delimiter
    body_start = start_idx + 1
    close_idx = None
    for i in range(body_start, len(lines)):
        if lines[i].strip() == "---":
            close_idx = i
            break

    if close_idx is None:
        return None  # No closing delimiter

    # Extract frontmatter text
    frontmatter_lines = lines[body_start:close_idx]
    return "".join(frontmatter_lines)


def _parse_yaml(text: str) -> dict | None:
    """Parse YAML text into a dictionary.

    Returns:
        A dictionary if parsing succeeds, None if:
        - YAML parse error
        - Result is not a dictionary (e.g., scalar or list)
        - Text is empty or whitespace-only
    """
    if not text.strip():
        return None

    try:
        result = yaml.safe_load(text)
    except yaml.YAMLError:
        return None

    if not isinstance(result, dict):
        return None

    return result
```

### 3.3 Metadata Field Mapping

```python
def _map_to_metadata(raw_dict: dict) -> Metadata:
    """Map frontmatter dictionary keys to Metadata model fields.

    Recognized keys (case-sensitive):
        schema_version      → Metadata.schema_version
        site_name           → Metadata.site_name
        site_url            → Metadata.site_url
        last_updated        → Metadata.last_updated
        generator           → Metadata.generator
        docstratum_version  → Metadata.docstratum_version
        token_budget_tier   → Metadata.token_budget_tier

    Unrecognized keys are silently ignored (permissive input).

    Returns:
        A Metadata instance with recognized fields populated.
        Fields not present in the frontmatter use Pydantic defaults.
    """
    known_fields = {
        "schema_version",
        "site_name",
        "site_url",
        "last_updated",
        "generator",
        "docstratum_version",
        "token_budget_tier",
    }

    filtered = {k: v for k, v in raw_dict.items() if k in known_fields}
    return Metadata(**filtered)
```

---

## 4. Design Decisions

| Decision                                 | Choice  | Rationale                                                                                                                                                                                 |
| ---------------------------------------- | ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `yaml.safe_load` (not `yaml.load`)       | Yes     | `safe_load` prevents arbitrary code execution from malicious YAML. There is no reason to use the unsafe variant for frontmatter.                                                          |
| Case-sensitive key matching              | Yes     | YAML keys are case-sensitive by spec. `site_name` ≠ `Site_Name`. This is consistent with Pydantic field naming.                                                                           |
| Unrecognized keys silently ignored       | Yes     | "Permissive input" — frontmatter may contain Hugo/Jekyll/Docusaurus-specific keys that DocStratum doesn't use.                                                                            |
| Leading blank lines allowed before `---` | Yes     | Some editors or generators may add a blank line before frontmatter. Being permissive here avoids false negatives.                                                                         |
| `pyyaml` as external dependency          | Yes     | PyYAML is the standard YAML parser for Python. No benefit to implementing a custom parser for this well-defined format.                                                                   |
| Returns `None` for malformed YAML        | Yes     | The parser does not raise exceptions. A broken frontmatter block is the same as no frontmatter — the document is parseable either way.                                                    |
| No `Metadata` validation                 | Correct | `schema_version` format, `site_url` validity, etc. are validator concerns, not parser concerns. The `Metadata` model may have Pydantic validators on its fields; those run automatically. |

---

## 5. Interaction with Tokenizer

YAML frontmatter lines within `---` delimiters are processed by the tokenizer (v0.2.0b) as regular TEXT tokens. The metadata extractor operates on `raw_content`, not on the token stream. This means:

- Frontmatter lines appear in `ParsedLlmsTxt.raw_content`.
- Frontmatter lines may appear in section `raw_content` if they occur before the first H2 (treated as body text by the populator).
- The metadata extractor re-parses `raw_content` independently. There is no coupling between token types and metadata extraction.

This duplication is intentional — it keeps the tokenizer simple (it doesn't need to know about YAML) and keeps the metadata extractor self-contained.

---

## 6. Edge Cases

| Scenario                            | Input                                         | Result                                               |
| ----------------------------------- | --------------------------------------------- | ---------------------------------------------------- |
| No frontmatter                      | `"# Title\n"`                                 | `None`                                               |
| Valid frontmatter                   | `"---\nsite_name: X\n---\n# Title"`           | `Metadata(site_name="X")`                            |
| Empty frontmatter                   | `"---\n---\n# Title"`                         | `None` (no content between delimiters)               |
| Whitespace-only frontmatter         | `"---\n  \n---\n# Title"`                     | `None`                                               |
| Malformed YAML                      | `"---\n: invalid:\n---\n# Title"`             | `None`                                               |
| YAML list instead of dict           | `"---\n- item1\n- item2\n---\n"`              | `None` (not a dict)                                  |
| YAML scalar instead of dict         | `"---\njust a string\n---\n"`                 | `None` (not a dict)                                  |
| No closing `---`                    | `"---\nsite_name: X\n# Title"`                | `None` (unclosed)                                    |
| Unrecognized keys only              | `"---\nhugo_theme: abc\n---\n"`               | `Metadata()` (all defaults)                          |
| Mixed recognized/unrecognized       | `"---\nsite_name: X\nhugo_theme: abc\n---\n"` | `Metadata(site_name="X")`                            |
| Leading blank lines                 | `"\n\n---\nsite_name: X\n---\n"`              | `Metadata(site_name="X")`                            |
| `---` inside content (not at start) | `"# Title\n---\nkey: val\n---\n"`             | `None` (must be at start)                            |
| All 7 recognized fields present     | Full frontmatter                              | All 7 fields populated                               |
| Unicode values                      | `"---\nsite_name: 日本語\n---\n"`             | `Metadata(site_name="日本語")`                       |
| Nested YAML values                  | `"---\nsite_name:\n  nested: val\n---\n"`     | Pydantic validation may reject (field expects `str`) |
| Integer value for string field      | `"---\nsite_name: 123\n---\n"`                | Pydantic coerces to `"123"`                          |

---

## 7. Metadata Model Reference

The `Metadata` model from `enrichment.py` has the following fields:

| Field                | Type          | Default   | Description                                |
| -------------------- | ------------- | --------- | ------------------------------------------ |
| `schema_version`     | `str`         | `"0.1.0"` | DocStratum schema version (semver pattern) |
| `site_name`          | `str \| None` | `None`    | Human-readable project/site name           |
| `site_url`           | `str \| None` | `None`    | Project website URL                        |
| `last_updated`       | `str \| None` | `None`    | Last updated date/timestamp                |
| `generator`          | `str \| None` | `None`    | Tool that generated this file              |
| `docstratum_version` | `str \| None` | `None`    | DocStratum version that produced this file |
| `token_budget_tier`  | `str \| None` | `None`    | Desired token budget tier name             |

---

## 8. Acceptance Criteria

- [ ] Valid YAML frontmatter extracted into a `Metadata` instance.
- [ ] Missing frontmatter → `None`.
- [ ] Malformed YAML → `None` (no exception raised).
- [ ] Empty frontmatter (`---\n---`) → `None`.
- [ ] Non-dict YAML (list, scalar) → `None`.
- [ ] Unclosed frontmatter → `None`.
- [ ] Frontmatter not at start of file → `None`.
- [ ] Leading blank lines before `---` accepted.
- [ ] All 7 recognized fields populated when present.
- [ ] Unrecognized keys silently ignored.
- [ ] Key matching is case-sensitive.
- [ ] `yaml.safe_load` used (not unsafe `yaml.load`).
- [ ] Unicode values pass through correctly.
- [ ] No diagnostics emitted.
- [ ] Google-style docstrings; module references "Implements v0.2.1d".

---

## 9. Test Plan

### `tests/test_parser_metadata.py`

| Test                                  | Input                                       | Expected                               |
| ------------------------------------- | ------------------------------------------- | -------------------------------------- |
| `test_no_frontmatter`                 | `"# Title\n"`                               | `None`                                 |
| `test_valid_frontmatter_single_field` | `"---\nsite_name: X\n---\n"`                | `Metadata(site_name="X")`              |
| `test_valid_frontmatter_all_fields`   | All 7 keys                                  | `Metadata` with all 7 populated        |
| `test_empty_frontmatter`              | `"---\n---\n"`                              | `None`                                 |
| `test_whitespace_only_frontmatter`    | `"---\n   \n---\n"`                         | `None`                                 |
| `test_malformed_yaml`                 | `"---\n: bad\n---\n"`                       | `None`                                 |
| `test_yaml_list`                      | `"---\n- a\n- b\n---\n"`                    | `None`                                 |
| `test_yaml_scalar`                    | `"---\njust text\n---\n"`                   | `None`                                 |
| `test_unclosed_frontmatter`           | `"---\nkey: val\n"`                         | `None`                                 |
| `test_frontmatter_not_at_start`       | `"# Title\n---\nkey: val\n---\n"`           | `None`                                 |
| `test_leading_blank_lines`            | `"\n\n---\nsite_name: X\n---\n"`            | `Metadata(site_name="X")`              |
| `test_unrecognized_keys_ignored`      | `"---\nhugo_theme: abc\n---\n"`             | `Metadata()` (defaults)                |
| `test_mixed_keys`                     | `"---\nsite_name: X\nhugo: y\n---\n"`       | `Metadata(site_name="X")`              |
| `test_unicode_values`                 | `"---\nsite_name: 日本語\n---\n"`           | `Metadata(site_name="日本語")`         |
| `test_default_schema_version`         | `"---\nsite_name: X\n---\n"`                | `meta.schema_version == "0.1.0"`       |
| `test_custom_schema_version`          | `"---\nschema_version: 0.2.0\n---\n"`       | `meta.schema_version == "0.2.0"`       |
| `test_uses_safe_load`                 | Malicious YAML                              | No code execution, returns `None`      |
| `test_triple_dash_in_body`            | `"---\nk: v\n---\ncontent with ---\n"`      | Only first block parsed                |
| `test_generator_field`                | `"---\ngenerator: docusaurus\n---\n"`       | `meta.generator == "docusaurus"`       |
| `test_token_budget_tier_field`        | `"---\ntoken_budget_tier: standard\n---\n"` | `meta.token_budget_tier == "standard"` |

---

## 10. Dependencies

| Dependency                  | Type                       | Purpose                                |
| --------------------------- | -------------------------- | -------------------------------------- |
| `pyyaml`                    | External (PyPI)            | YAML parsing via `yaml.safe_load()`    |
| `Metadata` model            | Internal (`enrichment.py`) | Output model for extracted metadata    |
| `ParsedLlmsTxt.raw_content` | Internal (v0.2.0)          | Input source for frontmatter detection |

### 10.1 PyYAML Version Constraint

```toml
# pyproject.toml
[project]
dependencies = [
    "pydantic>=2.0",
    "pyyaml>=6.0",   # v0.2.1d — YAML frontmatter parsing
]
```

---

## 11. Limitations

| Limitation                                  | Reason                                              | When Addressed   |
| ------------------------------------------- | --------------------------------------------------- | ---------------- |
| TOML frontmatter (`+++`) not supported      | Uncommon in `llms.txt` context                      | If demand exists |
| JSON frontmatter (`{...}`) not supported    | Uncommon in `llms.txt` context                      | If demand exists |
| No frontmatter content validation           | Parser extracts, validator validates                | v0.3.x           |
| Frontmatter not stripped from `raw_content` | Preserving original content for round-trip fidelity | By design        |
| Case-sensitive key matching                 | YAML spec requires case-sensitive keys              | By design        |
