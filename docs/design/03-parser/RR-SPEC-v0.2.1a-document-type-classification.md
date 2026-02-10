# v0.2.1a — Document Type Classification

> **Version:** v0.2.1a
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Parent:** [RR-SPEC-v0.2.1-classification-metadata.md](RR-SPEC-v0.2.1-classification-metadata.md)
> **Grounding:** [v0.0.1a §6 Empirical Validation](../01-research/RR-SPEC-v0.0.1a-formal-grammar-and-parsing-rules.md) (lines 496–592), `classification.py` (`DocumentType`, `TYPE_BOUNDARY_BYTES`)
> **Depends On:** v0.2.0 (`ParsedLlmsTxt`, `FileMetadata`)
> **Module:** `src/docstratum/parser/classifier.py`
> **Tests:** `tests/test_parser_classifier.py`

---

## 1. Purpose

Inspect a parsed document and its file metadata to determine which `DocumentType` it belongs to. Classification is the first enrichment step — the validator uses the document type to select which rule set to apply.

---

## 2. Interface Contract

```python
def classify_document_type(
    doc: ParsedLlmsTxt,
    file_meta: FileMetadata,
) -> DocumentType:
    """Classify a parsed document into a DocumentType.

    Uses a multi-signal heuristic based on empirical findings from
    11 real-world specimens (v0.0.1a §6):
    - File size (byte count)
    - H1 header count (inferred from parsed structure)
    - Filename conventions
    - Content patterns

    Args:
        doc: Parsed document from v0.2.0.
        file_meta: File metadata from v0.2.0a.

    Returns:
        A DocumentType enum value.

    Example:
        >>> doc = parse_string("# My Project\\n> Desc\\n## Docs\\n- [API](/api)\\n")
        >>> meta = FileMetadata(byte_count=50, encoding='utf-8')
        >>> classify_document_type(doc, meta)
        <DocumentType.TYPE_1_INDEX: 'type_1_index'>
    """
```

---

## 3. Classification Decision Tree

```
Input: ParsedLlmsTxt + FileMetadata

1. Is file_meta.has_null_bytes == True?
   └── YES → UNKNOWN  (likely binary)

2. Is doc.title is None AND doc.sections == []?
   └── YES → UNKNOWN  (empty or unparseable)

3. Check filename conventions (from doc.source_filename):
   ├── Matches "llms-full.*" pattern → TYPE_2_FULL
   ├── Matches "llms-instructions.*" pattern → TYPE_4_INSTRUCTIONS
   └── Otherwise → continue

4. Check file size:
   └── file_meta.byte_count > TYPE_BOUNDARY_BYTES (256,000)?
       └── YES → TYPE_2_FULL

5. Check H1 count (structural signal):
   └── How many H1 tokens were in the original parse?
       ├── 0 or 1 → continue (normal for Type 1)
       └── >1 → TYPE_2_FULL (multiple H1s = inline documentation dump)

6. Check link density (secondary signal):
   └── Does the document have at least 1 section with at least 1 link?
       ├── YES → TYPE_1_INDEX  (curated link catalog)
       └── NO → Check if extensive prose content exists
           ├── YES (sections with raw_content but no links) → TYPE_2_FULL
           └── NO → TYPE_1_INDEX  (sparse but structurally conformant)

Default → TYPE_1_INDEX
```

### 3.1 H1 Count Detection

The `ParsedLlmsTxt` model captures only the **first** H1 as `title`. To detect multiple H1 headings, the classifier must scan `raw_content`:

````python
import re

def _count_h1_headings(raw_content: str) -> int:
    """Count H1 headings in raw content.

    Counts lines that start with '# ' (single hash + space).
    Lines starting with '## ' or '### ' are NOT counted.
    Lines inside code fences are NOT counted.

    Returns:
        Number of H1 headings found.
    """
    count = 0
    in_code_block = False
    for line in raw_content.splitlines():
        if line.startswith("```"):
            in_code_block = not in_code_block
            continue
        if not in_code_block and line.startswith("# ") and not line.startswith("## "):
            count += 1
    return count
````

### 3.2 Filename Pattern Matching

```python
import os

def _classify_by_filename(filename: str) -> DocumentType | None:
    """Classify document type based on filename conventions.

    Recognized patterns:
        llms-full.txt, llms-full.md     → TYPE_2_FULL
        llms-instructions.txt           → TYPE_4_INSTRUCTIONS

    Returns:
        DocumentType if filename matches a pattern, None otherwise.
    """
    basename = os.path.basename(filename).lower()
    name_without_ext = os.path.splitext(basename)[0]

    if name_without_ext == "llms-full":
        return DocumentType.TYPE_2_FULL
    if name_without_ext == "llms-instructions":
        return DocumentType.TYPE_4_INSTRUCTIONS

    return None
```

### 3.3 TYPE_3_CONTENT_PAGE

> **Note:** TYPE_3_CONTENT_PAGE classification requires ecosystem context — knowing that a file is linked from an index file. This cannot be determined from a single file in isolation. For v0.2.1a, content pages are only classified when the caller provides an explicit hint. In single-file mode, content pages appear as TYPE_1_INDEX or UNKNOWN.
>
> Full content page classification arrives in v0.3.x (ecosystem validator).

---

## 4. Design Decisions

| Decision                               | Choice  | Rationale                                                                                                                                |
| -------------------------------------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Filename takes precedence over content | Yes     | A file named `llms-full.txt` is Type 2 regardless of its internal structure. The naming convention is the strongest signal.              |
| Byte size before H1 count              | Yes     | The size check is O(1) and eliminates the most obvious cases. H1 counting requires scanning raw_content.                                 |
| H1 count > 1 → TYPE_2_FULL             | Yes     | Empirically, all Type 1 specimens have exactly 1 H1 (v0.0.1a §6). Multiple H1s are definitive.                                           |
| No TYPE_3/4 in single-file mode        | Correct | Content page and instruction detection need ecosystem graph. The classifier flags these as TYPE_1_INDEX or TYPE_2_FULL based on content. |
| UNKNOWN only for truly unclassifiable  | Yes     | Binary files, empty files, files with null bytes. A text file with any parseable structure gets a Type 1 or Type 2 assignment.           |

---

## 5. Edge Cases

| Scenario                              | Classification      | Rationale                               |
| ------------------------------------- | ------------------- | --------------------------------------- |
| Empty file (0 bytes)                  | UNKNOWN             | No structure to classify                |
| File with title but no sections       | TYPE_1_INDEX        | Structurally minimal but conformant     |
| File with 2 H1s, 50 bytes             | TYPE_2_FULL         | Multiple H1s override size              |
| File named `llms-full.txt`, 100 bytes | TYPE_2_FULL         | Filename convention overrides size      |
| 300 KB file, 1 H1, 10 sections        | TYPE_2_FULL         | Exceeds TYPE_BOUNDARY_BYTES             |
| 200 KB file, 1 H1, 1000 links         | TYPE_1_INDEX        | Under threshold, single H1              |
| Binary file with null bytes           | UNKNOWN             | `has_null_bytes=True`                   |
| File named `llms-instructions.txt`    | TYPE_4_INSTRUCTIONS | Filename convention                     |
| Markdown file, no `.txt` extension    | TYPE_1_INDEX        | Extension doesn't affect classification |

---

## 6. Acceptance Criteria

- [ ] Binary files (null bytes) → `UNKNOWN`.
- [ ] Empty/unparseable files → `UNKNOWN`.
- [ ] `llms-full.*` filename → `TYPE_2_FULL` regardless of content.
- [ ] `llms-instructions.*` filename → `TYPE_4_INSTRUCTIONS`.
- [ ] Files > 256,000 bytes → `TYPE_2_FULL`.
- [ ] Files with >1 H1 heading → `TYPE_2_FULL`.
- [ ] Normal single-H1 files with sections and links → `TYPE_1_INDEX`.
- [ ] Classification does not emit diagnostics.
- [ ] Classification does not modify the `ParsedLlmsTxt` instance.
- [ ] Google-style docstrings; module references "Implements v0.2.1a".

---

## 7. Test Plan

### `tests/test_parser_classifier.py` (v0.2.1a section)

| Test                              | Input                                 | Expected                            |
| --------------------------------- | ------------------------------------- | ----------------------------------- |
| `test_classify_empty_file`        | title=None, sections=[], byte_count=0 | UNKNOWN                             |
| `test_classify_null_bytes`        | has_null_bytes=True                   | UNKNOWN                             |
| `test_classify_type1_minimal`     | 1 H1, 1 section, 1 link, 200 bytes    | TYPE_1_INDEX                        |
| `test_classify_type1_large`       | 1 H1, 20 sections, 200,000 bytes      | TYPE_1_INDEX                        |
| `test_classify_type2_by_size`     | 1 H1, 300,000 bytes                   | TYPE_2_FULL                         |
| `test_classify_type2_by_h1_count` | 3 H1s, 500 bytes                      | TYPE_2_FULL                         |
| `test_classify_type2_by_filename` | filename="llms-full.txt", 50 bytes    | TYPE_2_FULL                         |
| `test_classify_type4_by_filename` | filename="llms-instructions.txt"      | TYPE_4_INSTRUCTIONS                 |
| `test_classify_boundary_exact`    | byte_count=256,000 exactly            | TYPE_1_INDEX (≤ boundary)           |
| `test_classify_boundary_plus_one` | byte_count=256,001                    | TYPE_2_FULL (> boundary)            |
| `test_h1_count_with_code_blocks`  | `# Title` inside code fence           | Count = 0 for that line             |
| `test_h1_count_ignores_h2`        | `## Section`                          | Not counted as H1                   |
| `test_classify_no_links_sparse`   | 1 H1, 1 section, 0 links              | TYPE_1_INDEX                        |
| `test_does_not_modify_doc`        | Any input                             | `doc` instance unchanged after call |
