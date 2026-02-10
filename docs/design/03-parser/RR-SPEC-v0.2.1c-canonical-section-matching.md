# v0.2.1c — Canonical Section Matching

> **Version:** v0.2.1c
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Parent:** [RR-SPEC-v0.2.1-classification-metadata.md](RR-SPEC-v0.2.1-classification-metadata.md)
> **Grounding:** `constants.py` (`CanonicalSectionName`, `SECTION_NAME_ALIASES`, `CANONICAL_SECTION_ORDER`), DECISION-012 (11 canonical names from 450+ project analysis)
> **Depends On:** v0.2.0c (`ParsedLlmsTxt` with populated sections)
> **Module:** `src/docstratum/parser/section_matcher.py`
> **Tests:** `tests/test_parser_section_matcher.py`

---

## 1. Purpose

For each `ParsedSection` in a parsed document, attempt to match the section's `name` against the 11 canonical section names and their 32 aliases. Populate the `ParsedSection.canonical_name` field with the resolved canonical name or leave it as `None`.

This enrichment enables downstream consumers (validator, quality scorer) to reason about section identity without re-implementing alias resolution. The validator uses `canonical_name` to detect ordering violations (CHECK-008), duplicate sections (CHECK-007), and non-canonical naming (W002).

---

## 2. Interface Contract

```python
def match_canonical_sections(doc: ParsedLlmsTxt) -> None:
    """Match section names to canonical names and set canonical_name in-place.

    For each section in doc.sections, performs case-insensitive matching:
    1. Exact match against CanonicalSectionName enum values
    2. Alias match against SECTION_NAME_ALIASES keys
    3. If neither matches, canonical_name remains None

    This function mutates doc.sections in place. It does not return a value.

    Args:
        doc: ParsedLlmsTxt with populated sections.

    Example:
        >>> doc.sections[0].name = "Getting Started"
        >>> doc.sections[1].name = "quickstart"
        >>> doc.sections[2].name = "My Custom Section"
        >>> match_canonical_sections(doc)
        >>> doc.sections[0].canonical_name
        'Getting Started'
        >>> doc.sections[1].canonical_name
        'Getting Started'
        >>> doc.sections[2].canonical_name is None
        True
    """
```

---

## 3. Matching Algorithm

### 3.1 Precedence Rules

```
Input: section.name (string)

Step 1: Normalize
    key = section.name.strip().lower()

Step 2: Exact Match
    For each canonical in CanonicalSectionName:
        if key == canonical.value.lower():
            section.canonical_name = canonical.value
            STOP

Step 3: Alias Match
    if key in SECTION_NAME_ALIASES:
        section.canonical_name = SECTION_NAME_ALIASES[key].value
        STOP

Step 4: No Match
    section.canonical_name = None
```

### 3.2 Normalization Rules

| Operation                         | Example                                                            |
| --------------------------------- | ------------------------------------------------------------------ |
| Strip leading/trailing whitespace | `"  API Reference  "` → `"api reference"`                          |
| Lowercase for comparison          | `"API Reference"` → `"api reference"`                              |
| Internal whitespace preserved     | `"Getting Started"` → `"getting started"` (not `"gettingstarted"`) |
| No Unicode normalization          | `"Café Tips"` stays as-is                                          |

### 3.3 Implementation

```python
from docstratum.schema.constants import CanonicalSectionName, SECTION_NAME_ALIASES
from docstratum.schema.parsed import ParsedLlmsTxt


def match_canonical_sections(doc: ParsedLlmsTxt) -> None:
    """Match section names to canonical names, setting canonical_name in-place."""
    # Pre-compute lowercase canonical names for O(1) lookup
    canonical_lookup: dict[str, str] = {
        name.value.lower(): name.value
        for name in CanonicalSectionName
    }

    for section in doc.sections:
        key = section.name.strip().lower()

        # Priority 1: exact canonical match
        if key in canonical_lookup:
            section.canonical_name = canonical_lookup[key]
            continue

        # Priority 2: alias match
        if key in SECTION_NAME_ALIASES:
            section.canonical_name = SECTION_NAME_ALIASES[key].value
            continue

        # No match
        section.canonical_name = None
```

---

## 4. Canonical Name Reference

### 4.1 The 11 Canonical Names

| #   | Canonical Name   | Order in 10-Step Sequence         |
| --- | ---------------- | --------------------------------- |
| 1   | Master Index     | 1                                 |
| 2   | LLM Instructions | 2                                 |
| 3   | Getting Started  | 3                                 |
| 4   | Core Concepts    | 4                                 |
| 5   | API Reference    | 5                                 |
| 6   | Examples         | 6                                 |
| 7   | Configuration    | 7                                 |
| 8   | Advanced Topics  | 8                                 |
| 9   | Troubleshooting  | 9                                 |
| 10  | FAQ              | 10                                |
| 11  | Optional         | (no fixed position — always last) |

### 4.2 The 32 Aliases

| Alias                        | Resolves To      |
| ---------------------------- | ---------------- |
| `table of contents`          | Master Index     |
| `toc`                        | Master Index     |
| `index`                      | Master Index     |
| `docs`                       | Master Index     |
| `documentation`              | Master Index     |
| `instructions`               | LLM Instructions |
| `agent instructions`         | LLM Instructions |
| `quickstart`                 | Getting Started  |
| `quick start`                | Getting Started  |
| `installation`               | Getting Started  |
| `setup`                      | Getting Started  |
| `concepts`                   | Core Concepts    |
| `key concepts`               | Core Concepts    |
| `fundamentals`               | Core Concepts    |
| `api`                        | API Reference    |
| `reference`                  | API Reference    |
| `endpoints`                  | API Reference    |
| `usage`                      | Examples         |
| `use cases`                  | Examples         |
| `tutorials`                  | Examples         |
| `recipes`                    | Examples         |
| `config`                     | Configuration    |
| `settings`                   | Configuration    |
| `options`                    | Configuration    |
| `advanced`                   | Advanced Topics  |
| `internals`                  | Advanced Topics  |
| `debugging`                  | Troubleshooting  |
| `common issues`              | Troubleshooting  |
| `known issues`               | Troubleshooting  |
| `frequently asked questions` | FAQ              |
| `supplementary`              | Optional         |
| `appendix`                   | Optional         |
| `extras`                     | Optional         |

---

## 5. Decision Tree: Section Name → Canonical Name

```
"Getting Started"
   → normalize → "getting started"
   → exact match: CanonicalSectionName.GETTING_STARTED.value.lower() == "getting started" ✅
   → canonical_name = "Getting Started"

"quickstart"
   → normalize → "quickstart"
   → exact match: no canonical name matches ❌
   → alias match: SECTION_NAME_ALIASES["quickstart"] = CanonicalSectionName.GETTING_STARTED ✅
   → canonical_name = "Getting Started"

"My Custom APIs"
   → normalize → "my custom apis"
   → exact match: ❌
   → alias match: ❌
   → canonical_name = None
```

---

## 6. Design Decisions

| Decision                                   | Choice  | Rationale                                                                                                                                                               |
| ------------------------------------------ | ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Mutate in-place                            | Yes     | `canonical_name` is a field on `ParsedSection`. Creating copies is wasteful for a single-field enrichment.                                                              |
| Case-insensitive matching                  | Yes     | Section names in the wild vary freely in capitalization: "API Reference", "api reference", "Api reference" should all match.                                            |
| No fuzzy matching                          | Correct | "Getting Start" (typo) does NOT match "Getting Started". Fuzzy matching is a v0.5.x candidate — it requires careful threshold design and could produce false positives. |
| No substring matching                      | Correct | "API Reference Guide" does NOT match "API Reference". Only exact and alias matches. Adding substring would also risk false positives.                                   |
| Doesn't flag non-canonical names           | Correct | That's W002 in the validator (v0.3.x). The parser enriches; it doesn't judge.                                                                                           |
| Doesn't detect duplicate canonical matches | Correct | Two sections both mapping to "Getting Started" is valid data. The validator (CHECK-007) flags it.                                                                       |

---

## 7. Edge Cases

| Scenario                          | Section Name                     | `canonical_name`                      |
| --------------------------------- | -------------------------------- | ------------------------------------- |
| Exact canonical name              | `"API Reference"`                | `"API Reference"`                     |
| Exact canonical, different case   | `"api reference"`                | `"API Reference"`                     |
| Alias match                       | `"quickstart"`                   | `"Getting Started"`                   |
| Alias match, mixed case           | `"QUICKSTART"`                   | `"Getting Started"`                   |
| Leading/trailing whitespace       | `"  FAQ  "`                      | `"FAQ"`                               |
| No match                          | `"My Custom Section"`            | `None`                                |
| Partial match (substring)         | `"API Reference Guide"`          | `None` (no substring matching)        |
| Typo                              | `"Getting Start"`                | `None` (no fuzzy matching)            |
| Empty section name                | `""`                             | `None`                                |
| Whitespace-only name              | `"   "`                          | `None`                                |
| Canonical name as alias of itself | `"FAQ"`                          | `"FAQ"` (matches as exact, not alias) |
| Two sections match same canonical | `["quickstart", "installation"]` | Both get `"Getting Started"`          |
| Section named after alias key     | `"toc"`                          | `"Master Index"`                      |

---

## 8. Acceptance Criteria

- [ ] All 11 canonical names matched when given exactly.
- [ ] All 11 canonical names matched case-insensitively.
- [ ] All 32 aliases resolved to the correct canonical name.
- [ ] All 32 aliases resolved case-insensitively.
- [ ] Leading/trailing whitespace stripped before matching.
- [ ] Non-matching section names get `canonical_name = None`.
- [ ] Empty section name → `canonical_name = None`.
- [ ] No new model instances created — mutation in-place only.
- [ ] No diagnostics emitted.
- [ ] No substring or fuzzy matching.
- [ ] Google-style docstrings; module references "Implements v0.2.1c".

---

## 9. Test Plan

### `tests/test_parser_section_matcher.py`

| Test                                    | Section Name Input               | Expected `canonical_name`                   |
| --------------------------------------- | -------------------------------- | ------------------------------------------- |
| `test_exact_canonical_master_index`     | `"Master Index"`                 | `"Master Index"`                            |
| `test_exact_canonical_api_reference`    | `"API Reference"`                | `"API Reference"`                           |
| `test_exact_canonical_faq`              | `"FAQ"`                          | `"FAQ"`                                     |
| `test_exact_canonical_case_insensitive` | `"api reference"`                | `"API Reference"`                           |
| `test_exact_canonical_mixed_case`       | `"Api Reference"`                | `"API Reference"`                           |
| `test_alias_quickstart`                 | `"quickstart"`                   | `"Getting Started"`                         |
| `test_alias_toc`                        | `"toc"`                          | `"Master Index"`                            |
| `test_alias_endpoints`                  | `"endpoints"`                    | `"API Reference"`                           |
| `test_alias_recipes`                    | `"recipes"`                      | `"Examples"`                                |
| `test_alias_debugging`                  | `"debugging"`                    | `"Troubleshooting"`                         |
| `test_alias_appendix`                   | `"appendix"`                     | `"Optional"`                                |
| `test_alias_case_insensitive`           | `"QUICKSTART"`                   | `"Getting Started"`                         |
| `test_no_match`                         | `"My Custom Section"`            | `None`                                      |
| `test_no_fuzzy_match`                   | `"Getting Start"`                | `None`                                      |
| `test_no_substring_match`               | `"API Reference Guide"`          | `None`                                      |
| `test_whitespace_stripped`              | `"  FAQ  "`                      | `"FAQ"`                                     |
| `test_empty_name`                       | `""`                             | `None`                                      |
| `test_whitespace_only_name`             | `"   "`                          | `None`                                      |
| `test_multiple_sections_same_canonical` | `["quickstart", "installation"]` | Both → `"Getting Started"`                  |
| `test_all_11_canonical_names`           | All 11 canonical values          | All 11 matched                              |
| `test_all_32_aliases`                   | All 32 alias keys                | All 32 resolved correctly                   |
| `test_mutates_in_place`                 | Any section                      | `section.canonical_name` set, same instance |
| `test_empty_sections_list`              | `doc.sections = []`              | No error, no-op                             |
