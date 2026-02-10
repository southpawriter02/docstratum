# v0.2.2b — Real-World Specimen Parsing

> **Version:** v0.2.2b
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Parent:** [RR-SPEC-v0.2.2-parser-testing-calibration.md](RR-SPEC-v0.2.2-parser-testing-calibration.md)
> **Grounding:** DS-CS-001 through DS-CS-006 (6 CalibrationSpecimens), v0.0.2b (individual site audits)
> **Depends On:** v0.2.0 (core parser), v0.2.1 (enrichment)
> **Outputs:** 6 specimen files in `tests/fixtures/parser/specimens/`, 6 regression tests
> **Tests:** `tests/test_parser_specimens.py`

---

## 1. Purpose

Parse the 6 gold-standard calibration specimens and verify that the parser produces structurally correct output. These are regression tests — they anchor parser behavior against real-world files so that future parser changes don't break handling of production-quality documents.

> **Important:** These tests verify **parser correctness** (structural extraction), not **validation quality** (diagnostic codes) or **quality scores** (point values). Quality calibration is v0.4.2a.

---

## 2. Calibration Specimens

The 6 specimens were identified in v0.0.2b and serve as the project's gold-standard calibration set:

| ID        | Project       | Expected Score | Type          | Structural Profile                                           |
| --------- | ------------- | -------------- | ------------- | ------------------------------------------------------------ |
| DS-CS-001 | Svelte        | 92             | TYPE_1_INDEX  | H1, blockquote, multiple canonical sections, described links |
| DS-CS-002 | Pydantic      | 90             | TYPE_1_INDEX  | H1, blockquote, canonical sections, extensive API links      |
| DS-CS-003 | Vercel AI SDK | 90             | TYPE_1_INDEX  | H1, blockquote, well-organized sections                      |
| DS-CS-004 | Shadcn UI     | 89             | TYPE_1_INDEX  | H1, blockquote, canonical sections                           |
| DS-CS-005 | Cursor        | 42             | TYPE_1_INDEX  | H1, minimal structure, few or no descriptions                |
| DS-CS-006 | NVIDIA        | 24             | TYPE_2_FULL\* | Large file, likely > 256 KB, documentation dump              |

> \*NVIDIA's classification depends on its size at time of snapshot. If the specimen is > 256 KB, it classifies as TYPE_2_FULL.

---

## 3. Specimen Acquisition

### 3.1 Source

Specimens should be sourced by:

1. **Fetching** the current `llms.txt` from each project's public URL.
2. **Snapshotting** the content at a specific date.
3. **Committing** the snapshot to `tests/fixtures/parser/specimens/`.

### 3.2 Snapshot Convention

Each specimen file should include a header comment (prepended before the actual content for documentation, or stored in a companion `.meta` file):

```
# Specimen: DS-CS-001 Svelte
# Source: https://svelte.dev/llms.txt
# Snapshot Date: YYYY-MM-DD
# Byte Count: NNN
# Notes: Fetched from public URL, no modifications
```

> **Decision:** If prepending a comment violates the parse (it would be parsed as TEXT, not H1), store metadata in a companion `.meta.json` file instead.

### 3.3 Offline Requirement

All specimens are committed to the repository. Tests must NOT make network requests. If a specimen needs updating, the developer manually re-fetches and commits the new snapshot.

---

## 4. Test Strategy

Each specimen test follows the same pattern:

```python
import pytest
from pathlib import Path

from docstratum.parser import parse_file

SPECIMEN_DIR = Path(__file__).parent / "fixtures" / "parser" / "specimens"


class TestSpecimenParsing:
    """Regression tests for gold-standard calibration specimens.

    Each test verifies structural extraction, not quality scores.
    Implements v0.2.2b.
    """

    def test_svelte_ds_cs_001(self):
        """DS-CS-001: Svelte — high-quality Type 1 Index."""
        doc, meta, classification, metadata = parse_file(
            str(SPECIMEN_DIR / "svelte.txt")
        )

        # Structural assertions
        assert doc.title is not None
        assert doc.blockquote is not None
        assert len(doc.sections) > 0
        assert classification.document_type == DocumentType.TYPE_1_INDEX
        # No crash — the primary regression check
        assert doc.raw_content != ""

    # ... similar for other specimens ...
```

### 4.1 Assertion Levels

Each specimen test asserts at three levels:

**Level 1 — No Crash (mandatory):**

- Parser does not raise exceptions.
- `doc` is a valid `ParsedLlmsTxt` instance.
- `classification` is a valid `DocumentClassification` instance.

**Level 2 — Structural Shape (mandatory):**

- `title` matches expected project name.
- `sections` count is within expected range.
- `blockquote` presence/absence matches expectation.

**Level 3 — Deep Properties (optional, specimen-specific):**

- Specific section names present.
- Link counts per section within expected ranges.
- `canonical_name` matches for known sections.

---

## 5. Expected Structural Properties

| Specimen      | Title Contains           | Sections ≥ | Has Blockquote | Has Links | Document Type               |
| ------------- | ------------------------ | ---------- | -------------- | --------- | --------------------------- |
| Svelte        | `"Svelte"`               | 3          | Yes            | Yes       | TYPE_1_INDEX                |
| Pydantic      | `"Pydantic"`             | 3          | Yes            | Yes       | TYPE_1_INDEX                |
| Vercel AI SDK | `"Vercel"` or `"AI SDK"` | 2          | Yes            | Yes       | TYPE_1_INDEX                |
| Shadcn UI     | `"shadcn"`               | 2          | Yes            | Yes       | TYPE_1_INDEX                |
| Cursor        | `"Cursor"`               | 1          | \*             | Yes       | TYPE_1_INDEX                |
| NVIDIA        | `"NVIDIA"`               | 1          | \*             | \*        | TYPE_1_INDEX or TYPE_2_FULL |

> `*` = depends on actual specimen content; assertion uses flexible check.

---

## 6. Acceptance Criteria

- [ ] 6 specimen files committed to `tests/fixtures/parser/specimens/`.
- [ ] Each specimen has a companion `.meta.json` with source URL and snapshot date.
- [ ] All 6 specimens parse without exceptions.
- [ ] Title text matches expected project name for each specimen.
- [ ] Section count is within expected range for each specimen.
- [ ] Blockquote presence matches expectation for high-quality specimens.
- [ ] No network access during tests.
- [ ] Tests do not assert quality scores or diagnostic codes.

---

## 7. Test Plan

### `tests/test_parser_specimens.py`

| Test                           | Specimen            | Key Assertions                                                             |
| ------------------------------ | ------------------- | -------------------------------------------------------------------------- |
| `test_svelte_ds_cs_001`        | `svelte.txt`        | title contains `"Svelte"`, ≥3 sections, blockquote present, TYPE_1_INDEX   |
| `test_pydantic_ds_cs_002`      | `pydantic.txt`      | title contains `"Pydantic"`, ≥3 sections, blockquote present, TYPE_1_INDEX |
| `test_vercel_ai_sdk_ds_cs_003` | `vercel_ai_sdk.txt` | title present, ≥2 sections, blockquote present, TYPE_1_INDEX               |
| `test_shadcn_ui_ds_cs_004`     | `shadcn_ui.txt`     | title present, ≥2 sections, blockquote present, TYPE_1_INDEX               |
| `test_cursor_ds_cs_005`        | `cursor.txt`        | title contains `"Cursor"`, ≥1 section, TYPE_1_INDEX                        |
| `test_nvidia_ds_cs_006`        | `nvidia.txt`        | title present, ≥1 section, no crash on potentially large file              |

---

## 8. Limitations

| Limitation                              | Reason                                               | When Addressed                                 |
| --------------------------------------- | ---------------------------------------------------- | ---------------------------------------------- |
| Expected scores not verified            | Quality scoring is v0.4.x                            | v0.4.2a — Specimen calibration                 |
| Diagnostic codes not verified           | Validation engine is v0.3.x                          | v0.3.5d — Specimen diagnostics                 |
| Structural expectations are approximate | Real-world files vary; exact counts would be brittle | Assertion ranges (≥N) rather than exact values |
| Specimens may become stale              | Source sites update their files                      | Periodic re-fetching required                  |
