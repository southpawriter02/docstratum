# v0.2.1 — Classification & Metadata

> **Version:** v0.2.1
> **Document Type:** Design Specification (scope overview with sub-part breakdown)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SCOPE-v0.2.x-parser.md](RR-SCOPE-v0.2.x-parser.md)
> **Depends On:** [v0.2.0](RR-SPEC-v0.2.0-core-parser.md) (`ParsedLlmsTxt`, `FileMetadata`)
> **Consumes:** [v0.1.2a](../02-foundation/RR-SPEC-v0.1.2a-diagnostic-infrastructure.md) (`CanonicalSectionName`, `SECTION_NAME_ALIASES`, `TokenBudgetTier`), [v0.1.2b](../02-foundation/RR-SPEC-v0.1.2b-document-models.md) (`DocumentType`, `SizeTier`, `DocumentClassification`), [v0.1.2d](../02-foundation/) (`Metadata`)
> **Consumed By:** v0.2.2 (Parser Testing & Calibration), v0.3.x (Validation Engine)

---

## 1. Purpose

v0.2.1 enriches the `ParsedLlmsTxt` model produced by v0.2.0 with **post-parse classification and metadata**. These are structural enrichments that operate on the already-parsed model — they do not modify raw text or re-tokenize.

The enrichment pipeline adds four capabilities:

1. **Document type classification** — Is this a Type 1 Index, Type 2 Full, or something else?
2. **Size tier assignment** — Is this Minimal, Standard, Comprehensive, Full, or Oversized?
3. **Canonical section matching** — Which sections map to the 11 canonical names?
4. **Metadata extraction** — Does this file have YAML frontmatter?

These enrichments exist as a separate step from core parsing because:

- They are **optional** — a "fast parse" mode could skip them.
- They depend on the parsed structure being complete before running.
- They produce new model instances (`DocumentClassification`, `Metadata`) that are separate from `ParsedLlmsTxt`.
- The validator (v0.3.x) needs these enrichments to select which rules to apply.

### 1.1 User Stories

| ID       | As a...                  | I want to...                                     | So that...                                                                                   |
| -------- | ------------------------ | ------------------------------------------------ | -------------------------------------------------------------------------------------------- |
| US-021-1 | Validator developer      | Know the document type before running validation | I can apply the correct rule set (Type 1 gets ABNF rules; Type 2 gets size-only diagnostics) |
| US-021-2 | CLI user                 | See the detected size tier in the parse output   | I know if my file is approaching token budget limits                                         |
| US-021-3 | Quality scorer           | Have canonical section names already resolved    | I can score section naming without re-implementing alias lookup                              |
| US-021-4 | Pipeline consumer        | Get metadata from YAML frontmatter if present    | I can track provenance (generator, schema version, last updated)                             |
| US-021-5 | File without frontmatter | Still get a complete parse                       | Missing metadata is informational, not an error                                              |

---

## 2. Architecture

### 2.1 Module Structure

```
src/docstratum/parser/
├── __init__.py            # Updated: exports classify(), enrich()
├── io.py                  # (v0.2.0a — unchanged)
├── tokenizer.py           # (v0.2.0b — unchanged)
├── tokens.py              # (v0.2.0b — unchanged)
├── populator.py           # (v0.2.0c — unchanged)
├── classifier.py          # v0.2.1a/b — Document type + size tier
├── section_matcher.py     # v0.2.1c — Canonical section name matching
└── metadata.py            # v0.2.1d — YAML frontmatter extraction
```

### 2.2 Data Flow

```
  ┌────────────────────┐
  │  ParsedLlmsTxt     │  (from v0.2.0)
  │  + FileMetadata     │
  └─────────┬──────────┘
            │
  ┌─────────▼──────────┐
  │  v0.2.1a           │
  │  Document Type     │──── DocumentType
  │  Classification    │
  └─────────┬──────────┘
            │
  ┌─────────▼──────────┐
  │  v0.2.1b           │
  │  Size Tier         │──── SizeTier
  │  Assignment        │
  └─────────┬──────────┘
            │
  ┌─────────▼──────────┐
  │  v0.2.1c           │
  │  Canonical Section │──── ParsedSection.canonical_name
  │  Matching          │     (mutated in place)
  └─────────┬──────────┘
            │
  ┌─────────▼──────────┐
  │  v0.2.1d           │
  │  Metadata          │──── Metadata | None
  │  Extraction        │
  └────────────────────┘
            │
  ┌─────────▼──────────┐
  │  Output:           │
  │  - DocumentClassification
  │  - ParsedLlmsTxt (canonical_names set)
  │  - Metadata | None │
  └────────────────────┘
```

### 2.3 Parallelization Opportunities

Unlike v0.2.0 (strictly sequential), v0.2.1's sub-parts have partial independence:

```
v0.2.1a → v0.2.1b  (b needs the document type for classification assembly)
v0.2.1c             (independent — only mutates ParsedSection.canonical_name)
v0.2.1d             (independent — only reads raw_content for frontmatter)
```

In practice, all four run sequentially for simplicity, but v0.2.1c and v0.2.1d could run in parallel with v0.2.1a/b if performance optimization is ever needed.

---

## 3. Sub-Part Breakdown

| Sub-Part                                                   | Title                        | Input                                     | Output                                  | Module                      |
| ---------------------------------------------------------- | ---------------------------- | ----------------------------------------- | --------------------------------------- | --------------------------- |
| [v0.2.1a](RR-SPEC-v0.2.1a-document-type-classification.md) | Document Type Classification | `ParsedLlmsTxt`, `FileMetadata`           | `DocumentType`                          | `parser/classifier.py`      |
| [v0.2.1b](RR-SPEC-v0.2.1b-size-tier-assignment.md)         | Size Tier Assignment         | `estimated_tokens` (from `ParsedLlmsTxt`) | `SizeTier`, `DocumentClassification`    | `parser/classifier.py`      |
| [v0.2.1c](RR-SPEC-v0.2.1c-canonical-section-matching.md)   | Canonical Section Matching   | `ParsedLlmsTxt` (with populated sections) | Same instance with `canonical_name` set | `parser/section_matcher.py` |
| [v0.2.1d](RR-SPEC-v0.2.1d-metadata-extraction.md)          | Metadata Extraction          | `ParsedLlmsTxt.raw_content`               | `Metadata` or `None`                    | `parser/metadata.py`        |

---

## 4. Public API

```python
# src/docstratum/parser/__init__.py  (additions to v0.2.0 API)

from docstratum.parser.classifier import classify_document
from docstratum.parser.section_matcher import match_canonical_sections
from docstratum.parser.metadata import extract_metadata
from docstratum.schema.classification import DocumentClassification
from docstratum.schema.enrichment import Metadata


def parse_file(
    file_path: str,
    *,
    source_filename: str | None = None,
    enrich: bool = True,
) -> tuple[ParsedLlmsTxt, FileMetadata, DocumentClassification | None, Metadata | None]:
    """Parse and optionally enrich an llms.txt file.

    Args:
        file_path: Path to the file.
        source_filename: Override for the source_filename field.
        enrich: If True (default), run v0.2.1 enrichments
                (classification, section matching, metadata).
                If False, skip enrichments (fast parse mode).

    Returns:
        A tuple of (ParsedLlmsTxt, FileMetadata, DocumentClassification, Metadata).
        DocumentClassification and Metadata are None if enrich=False.

    Example:
        >>> doc, meta, classification, metadata = parse_file("llms.txt")
        >>> classification.document_type
        <DocumentType.TYPE_1_INDEX: 'type_1_index'>
        >>> classification.size_tier
        <SizeTier.STANDARD: 'standard'>
        >>> doc.sections[0].canonical_name
        'Master Index'
        >>> metadata
        None  # No YAML frontmatter in this file
    """
    content, file_meta = read_file(file_path)
    tokens = tokenize(content)
    filename = source_filename or _basename(file_path)
    doc = populate(tokens, raw_content=content, source_filename=filename)

    if not enrich:
        return doc, file_meta, None, None

    classification = classify_document(doc, file_meta)
    match_canonical_sections(doc)
    extracted_metadata = extract_metadata(doc.raw_content)

    return doc, file_meta, classification, extracted_metadata
```

### 4.1 API Design Decisions

| Decision                                                    | Choice                          | Rationale                                                                                                                                                                                           |
| ----------------------------------------------------------- | ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `enrich` flag on `parse_file()`                             | Default `True`                  | Fast parse mode is useful for pipeline stages that only need structure (e.g., link extraction). But the common case always wants enrichment.                                                        |
| `classify_document()` is standalone                         | Not embedded in `populate()`    | Classification depends on `FileMetadata` which is only available via `read_file()`, not `parse_string()`. Keeping it standalone allows string-only callers to skip classification.                  |
| `match_canonical_sections()` mutates in-place               | Yes                             | `canonical_name` is a field on `ParsedSection`; creating a new model instance for a single field change is wasteful.                                                                                |
| `DocumentClassification` and `Metadata` returned separately | Not embedded in `ParsedLlmsTxt` | These are enrichment outputs, not core parsed structure. The schema boundary is clear: `ParsedLlmsTxt` is what the parser sees; `DocumentClassification` and `Metadata` are what the enricher adds. |

---

## 5. Models Consumed and Populated

### 5.1 Models Populated (Not Modified)

v0.2.1 populates instances of existing models. It does not change their definitions.

| Model                          | Source Module              | How v0.2.1 Uses It                                               |
| ------------------------------ | -------------------------- | ---------------------------------------------------------------- |
| `DocumentClassification`       | `schema/classification.py` | **Created** by `classify_document()` with all 6 fields populated |
| `DocumentType`                 | `schema/classification.py` | **Selected** from 5 enum values based on heuristics              |
| `SizeTier`                     | `schema/classification.py` | **Selected** from 5 enum values based on token count thresholds  |
| `Metadata`                     | `schema/enrichment.py`     | **Created** from YAML frontmatter if present                     |
| `ParsedSection.canonical_name` | `schema/parsed.py`         | **Set** from `None` to matched canonical name string             |

### 5.2 Models Consumed (Read-Only)

| Model                  | Used By       | How                                                                            |
| ---------------------- | ------------- | ------------------------------------------------------------------------------ |
| `ParsedLlmsTxt`        | All sub-parts | Read `title`, `sections`, `raw_content`, `source_filename`, `estimated_tokens` |
| `FileMetadata`         | v0.2.1a       | Read `byte_count`, `encoding`, `has_null_bytes`                                |
| `CanonicalSectionName` | v0.2.1c       | Enum values for exact matching                                                 |
| `SECTION_NAME_ALIASES` | v0.2.1c       | Dict for alias resolution                                                      |
| `TokenBudgetTier`      | v0.2.1b       | Threshold values for tier assignment                                           |
| `TYPE_BOUNDARY_BYTES`  | v0.2.1a       | 256,000 byte threshold for Type 1 vs Type 2                                    |

---

## 6. Workflows

### 6.1 Full Parse + Enrichment

```
1. parse_file("llms.txt") called with enrich=True (default)
2. v0.2.0 pipeline runs: I/O → tokenize → populate → token estimation
3. classify_document(doc, file_meta):
   a. Count H1 appearances in parsed data
   b. Check byte_count against TYPE_BOUNDARY_BYTES
   c. Check filename conventions
   d. Assign DocumentType
   e. Compute estimated_tokens from doc.estimated_tokens
   f. Assign SizeTier based on token thresholds
   g. Return DocumentClassification(...)
4. match_canonical_sections(doc):
   a. For each section in doc.sections:
   b. Lowercase section.name and strip whitespace
   c. Check exact match against CanonicalSectionName enum values
   d. If no exact match, check against SECTION_NAME_ALIASES keys
   e. Set section.canonical_name = matched canonical name or None
5. extract_metadata(doc.raw_content):
   a. Check if raw_content starts with "---"
   b. Find closing "---"
   c. Parse YAML between fences
   d. Map recognized keys to Metadata fields
   e. Return Metadata instance or None
6. Return (doc, file_meta, classification, metadata)
```

### 6.2 Fast Parse (No Enrichment)

```
1. parse_file("llms.txt", enrich=False)
2. v0.2.0 pipeline runs normally
3. Classification, section matching, and metadata extraction skipped
4. Return (doc, file_meta, None, None)
```

---

## 7. Acceptance Criteria

### 7.1 Functional

- [ ] `classify_document()` returns a `DocumentClassification` with all 6 fields populated.
- [ ] Files ≤ 256,000 bytes with a single H1 → `TYPE_1_INDEX`.
- [ ] Files > 256,000 bytes → `TYPE_2_FULL`.
- [ ] Files with `llms-full.txt` filename → `TYPE_2_FULL` (regardless of size).
- [ ] Empty or binary files → `UNKNOWN`.
- [ ] Size tier assignment matches `TokenBudgetTier` thresholds.
- [ ] `match_canonical_sections()` resolves all 11 canonical names and 32 aliases.
- [ ] Section matching is case-insensitive.
- [ ] Non-matching section names get `canonical_name = None`.
- [ ] `extract_metadata()` parses valid YAML frontmatter into a `Metadata` instance.
- [ ] Missing frontmatter returns `None`.
- [ ] Malformed YAML returns `None` (no exception).
- [ ] `enrich=False` skips all enrichment steps.

### 7.2 Non-Functional

- [ ] No new fields added to any v0.1.x Pydantic model.
- [ ] No `DiagnosticCode` instances emitted by any enrichment function.
- [ ] `pytest --cov=docstratum.parser --cov-fail-under=85` passes.
- [ ] `black --check` and `ruff check` pass on all new code.
- [ ] Google-style docstrings on all public functions.
- [ ] Module docstrings reference the spec version (e.g., "Implements v0.2.1a").

### 7.3 CHANGELOG Entry Template

```markdown
## [0.2.1] - YYYY-MM-DD

**Classification & Metadata — Post-parse document enrichment.**

### Added

#### Classifier (`src/docstratum/parser/classifier.py`)

- `classify_document()` — Document type classification using H1 count, byte size, filename heuristics (v0.2.1a)
- `assign_size_tier()` — Token-based size tier assignment with 5-tier threshold matching (v0.2.1b)
- Produces `DocumentClassification` with `document_type`, `size_tier`, `size_bytes`, `estimated_tokens`

#### Section Matcher (`src/docstratum/parser/section_matcher.py`)

- `match_canonical_sections()` — Case-insensitive matching against 11 canonical names + 32 aliases (v0.2.1c)
- Populates `ParsedSection.canonical_name` in-place

#### Metadata Extractor (`src/docstratum/parser/metadata.py`)

- `extract_metadata()` — YAML frontmatter extraction with safe fallback on malformed input (v0.2.1d)
- Returns `Metadata` instance or `None`

#### Public API Updates (`src/docstratum/parser/__init__.py`)

- `parse_file()` gains `enrich=True` parameter for optional classification + metadata enrichment
- Returns 4-tuple: `(ParsedLlmsTxt, FileMetadata, DocumentClassification | None, Metadata | None)`

#### Tests (`tests/`)

- `tests/test_parser_classifier.py` — Type classification, size tier thresholds, boundary cases (v0.2.1a/b)
- `tests/test_parser_section_matcher.py` — Canonical name matching, alias resolution, case insensitivity (v0.2.1c)
- `tests/test_parser_metadata.py` — YAML frontmatter parsing, missing frontmatter, malformed YAML (v0.2.1d)
```

---

## 8. Dependencies

### 8.1 Internal

| Module                     | What v0.2.1 Uses                                                                                |
| -------------------------- | ----------------------------------------------------------------------------------------------- |
| `schema/classification.py` | `DocumentType`, `SizeTier`, `DocumentClassification`, `TYPE_BOUNDARY_BYTES`                     |
| `schema/constants.py`      | `CanonicalSectionName`, `SECTION_NAME_ALIASES`, `CANONICAL_SECTION_ORDER`, `TOKEN_BUDGET_TIERS` |
| `schema/enrichment.py`     | `Metadata`                                                                                      |
| `schema/parsed.py`         | `ParsedLlmsTxt`, `ParsedSection`                                                                |
| `parser/io.py`             | `FileMetadata`                                                                                  |

### 8.2 External (PyPI)

| Package  | Used By              | Purpose                  |
| -------- | -------------------- | ------------------------ |
| `pyyaml` | `parser/metadata.py` | YAML frontmatter parsing |

> **Note:** PyYAML is the only new external dependency introduced by v0.2.1. It is a widely-used, well-maintained library.

### 8.3 Limitations

| Limitation                            | Reason                                                           | When Addressed               |
| ------------------------------------- | ---------------------------------------------------------------- | ---------------------------- |
| Type 3/4 classification incomplete    | Content page and instruction detection require ecosystem context | v0.3.x ecosystem validator   |
| No duplicate canonical name detection | Parser enriches, doesn't validate                                | v0.3.x validator (W002)      |
| No section ordering validation        | Parser enriches, doesn't validate                                | v0.3.x validator (CHECK-008) |
| Frontmatter format limited to YAML    | TOML/JSON frontmatter not supported                              | If demand exists             |
| Metadata fields not validated         | e.g., `schema_version` not checked for valid semver              | v0.3.x validator             |

---

## 9. Sub-Part Specifications

Each sub-part has its own detailed design specification:

- [v0.2.1a — Document Type Classification](RR-SPEC-v0.2.1a-document-type-classification.md)
- [v0.2.1b — Size Tier Assignment](RR-SPEC-v0.2.1b-size-tier-assignment.md)
- [v0.2.1c — Canonical Section Matching](RR-SPEC-v0.2.1c-canonical-section-matching.md)
- [v0.2.1d — Metadata Extraction](RR-SPEC-v0.2.1d-metadata-extraction.md)
