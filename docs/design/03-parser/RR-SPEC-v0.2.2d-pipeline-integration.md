# v0.2.2d — SingleFileValidator Integration

> **Version:** v0.2.2d
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Parent:** [RR-SPEC-v0.2.2-parser-testing-calibration.md](RR-SPEC-v0.2.2-parser-testing-calibration.md)
> **Grounding:** v0.1.4a (`SingleFileValidator` protocol), v0.1.4b (`PerFileStage`), FR-080 (per-file validation within ecosystem)
> **Depends On:** v0.2.0 (core parser), v0.2.1 (enrichment), v0.2.2a–c (must pass before merge)
> **Module:** `src/docstratum/parser/validator_adapter.py`
> **Tests:** `tests/test_parser_integration.py`

---

## 1. Purpose

Implement the `SingleFileValidator` protocol so the parser (v0.2.0) and enrichment (v0.2.1) can be plugged into the ecosystem pipeline's Stage 2 (`PerFileStage`). This is the **only production source code** in v0.2.2 — the other three sub-parts are test-only.

At this stage, only `parse()` and `classify()` are fully functional. `validate()` and `score()` return stub results because the validation engine (v0.3.x) and quality scorer (v0.4.x) are not yet implemented.

---

## 2. The SingleFileValidator Protocol

The protocol (v0.1.4a, `pipeline/stages.py` lines 293–363) defines 4 methods:

```python
class SingleFileValidator(Protocol):
    def parse(self, content: str, filename: str) -> ParsedLlmsTxt: ...
    def classify(self, parsed: ParsedLlmsTxt) -> DocumentClassification: ...
    def validate(self, parsed: ParsedLlmsTxt, classification: DocumentClassification) -> ValidationResult: ...
    def score(self, result: ValidationResult) -> QualityScore: ...
```

The `PerFileStage` calls these methods sequentially for each ecosystem file:

```
content → parse() → ParsedLlmsTxt
                         ↓
                    classify() → DocumentClassification
                         ↓
                    validate() → ValidationResult    ← STUB for v0.2.2d
                         ↓
                    score() → QualityScore            ← STUB for v0.2.2d
```

---

## 3. Implementation

### 3.1 `ParserAdapter`

```python
"""SingleFileValidator protocol implementation for the parser phase.

Adapts the v0.2.0 parser and v0.2.1 enrichment into the
SingleFileValidator interface required by the ecosystem pipeline.

At v0.2.2d, only ``parse()`` and ``classify()`` are functional.
``validate()`` and ``score()`` return empty stub results because
the validation engine (v0.3.x) and quality scorer (v0.4.x) are
not yet implemented.

Implements v0.2.2d.

Example:
    >>> from docstratum.parser.validator_adapter import ParserAdapter
    >>> from docstratum.pipeline.per_file import PerFileStage
    >>> adapter = ParserAdapter()
    >>> stage = PerFileStage(validator=adapter)
    >>> # Now the pipeline's Stage 2 will use the real parser
"""

from docstratum.parser import parse_string  # v0.2.0 public API
from docstratum.parser.classifier import classify_document  # v0.2.1a/b
from docstratum.parser.section_matcher import match_canonical_sections  # v0.2.1c
from docstratum.parser.metadata import extract_metadata  # v0.2.1d
from docstratum.schema.parsed import ParsedLlmsTxt
from docstratum.schema.classification import DocumentClassification
from docstratum.schema.validation import ValidationResult
from docstratum.schema.quality import QualityScore


class ParserAdapter:
    """Adapter implementing SingleFileValidator using the v0.2.0–v0.2.1 parser.

    This adapter wires the parser and enrichment modules into the
    protocol contract that the ecosystem pipeline expects.

    Attributes:
        None — stateless adapter.

    Example:
        >>> adapter = ParserAdapter()
        >>> parsed = adapter.parse("# Title\\n", "test.txt")
        >>> parsed.title
        'Title'
    """

    def parse(self, content: str, filename: str) -> ParsedLlmsTxt:
        """Parse raw content into a structured model.

        Calls the full parser pipeline: tokenize → populate → estimate.
        Then applies enrichment: canonical section matching + metadata.

        Args:
            content: Raw text content of the file.
            filename: The file's basename (e.g., "llms.txt").

        Returns:
            A fully populated ParsedLlmsTxt instance.
        """
        doc, file_meta = parse_string(content, filename=filename)

        # Apply enrichments (v0.2.1)
        match_canonical_sections(doc)
        doc.metadata = extract_metadata(content)

        return doc

    def classify(self, parsed: ParsedLlmsTxt) -> DocumentClassification:
        """Classify a parsed document by type and size.

        Args:
            parsed: The parsed representation from parse().

        Returns:
            DocumentClassification with document_type and size_tier.
        """
        # classify_document() needs FileMetadata — reconstruct minimal version
        # from the parsed document's properties.
        from docstratum.parser.io import FileMetadata

        file_meta = FileMetadata(
            byte_count=len(parsed.raw_content.encode("utf-8")),
            encoding="utf-8",
        )
        return classify_document(parsed, file_meta)

    def validate(
        self,
        parsed: ParsedLlmsTxt,
        classification: DocumentClassification,
    ) -> ValidationResult:
        """Stub: Return an empty validation result.

        The validation engine (v0.3.x) is not yet implemented.
        This stub allows the pipeline to complete without errors.

        Args:
            parsed: The parsed file content.
            classification: The file's classification.

        Returns:
            An empty ValidationResult with no diagnostics.
        """
        return ValidationResult(
            diagnostics=[],
            level_achieved=0,
        )

    def score(self, result: ValidationResult) -> QualityScore:
        """Stub: Return a zero quality score.

        The quality scorer (v0.4.x) is not yet implemented.
        This stub allows the pipeline to complete without errors.

        Args:
            result: The validation result.

        Returns:
            A QualityScore with zero values.
        """
        return QualityScore(
            total_score=0,
            grade="N/A",
        )
```

### 3.2 Design Decisions

| Decision                                   | Choice | Rationale                                                                                                                                                           |
| ------------------------------------------ | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Stateless adapter                          | Yes    | No mutable state between calls. Each file is independent.                                                                                                           |
| Reconstruct `FileMetadata` in `classify()` | Yes    | The `SingleFileValidator.parse()` signature doesn't return `FileMetadata`, but `classify_document()` needs it. Re-encoding the raw_content gives byte_count.        |
| Stubs return minimal valid models          | Yes    | Stubs must satisfy Pydantic validation on `ValidationResult` and `QualityScore`. Fields use safe defaults.                                                          |
| `level_achieved=0` for stub validation     | Yes    | Level 0 means "not validated" — semantically accurate for a stub.                                                                                                   |
| `grade="N/A"` for stub scoring             | Yes    | Clearly signals that scoring has not been performed.                                                                                                                |
| Apply enrichments inside `parse()`         | Yes    | The protocol caller expects `parse()` to return a fully enriched model. Enrichments (canonical matching, metadata) are lightweight and should run with every parse. |
| `parse_string()` over `parse_file()`       | Yes    | The protocol receives `content: str`, not a file path. `parse_string()` is the correct entry point.                                                                 |

---

## 4. `FileMetadata` Reconstruction

The `classify()` method needs `FileMetadata` but only has the `ParsedLlmsTxt`. This creates a slight impedance mismatch:

| Property         | Available From                     | Accurate?                            |
| ---------------- | ---------------------------------- | ------------------------------------ |
| `byte_count`     | `len(raw_content.encode('utf-8'))` | Yes — same content that was parsed   |
| `encoding`       | Hardcoded `'utf-8'`                | Approximate — original encoding lost |
| `has_null_bytes` | Not available                      | Cannot detect post-decode            |

**Decision:** Accept this approximation. The byte count is correct for classification purposes (the size check). `has_null_bytes` is relevant only for UNKNOWN classification, which the parser's structural analysis would also catch (title=None, sections=[]).

**Alternative considered:** Storing `FileMetadata` on `ParsedLlmsTxt` as an optional field. Rejected — this would require modifying a v0.1.2 model, violating the "no model amendments" constraint.

Long-term fix: In v0.3.x, when `validate()` is implemented, the protocol signature may be revised to pass `FileMetadata` alongside content.

---

## 5. Integration with PerFileStage

```python
# In application code or ecosystem pipeline entry point:

from docstratum.parser.validator_adapter import ParserAdapter
from docstratum.pipeline.orchestrator import EcosystemPipelineOrchestrator

adapter = ParserAdapter()
pipeline = EcosystemPipelineOrchestrator(validator=adapter)

# Now running the pipeline will:
# Stage 1: Discover files
# Stage 2: Parse + Classify each file (real), Validate + Score (stubs)
# Stage 3: Map relationships
# Stage 4: Ecosystem validation
# Stage 5: Ecosystem scoring
```

After Stage 2 with `ParserAdapter`:

| `EcosystemFile` field | State                                                     |
| --------------------- | --------------------------------------------------------- |
| `parsed`              | Populated `ParsedLlmsTxt`                                 |
| `classification`      | Populated `DocumentClassification`                        |
| `validation_result`   | Stub `ValidationResult(diagnostics=[], level_achieved=0)` |
| `quality_score`       | Stub `QualityScore(total_score=0, grade="N/A")`           |
| `raw_content`         | Populated by `PerFileStage` from disk                     |

---

## 6. Acceptance Criteria

- [ ] `ParserAdapter` class exists in `src/docstratum/parser/validator_adapter.py`.
- [ ] `ParserAdapter` satisfies `isinstance(adapter, SingleFileValidator)` (runtime checkable).
- [ ] `parse()` returns a fully enriched `ParsedLlmsTxt`.
- [ ] `classify()` returns a valid `DocumentClassification`.
- [ ] `validate()` returns a stub `ValidationResult` with no diagnostics.
- [ ] `score()` returns a stub `QualityScore` with zero/N/A values.
- [ ] Stubs do not raise exceptions.
- [ ] `PerFileStage` successfully uses `ParserAdapter` in an integration test.
- [ ] `EcosystemFile.parsed` is populated after pipeline run.
- [ ] `context.project_name` is extracted from index file H1 title.
- [ ] Multi-file ecosystems parse without crashes.
- [ ] Google-style docstrings; module references "Implements v0.2.2d".

---

## 7. Test Plan

### `tests/test_parser_integration.py`

| Test                                    | Description                                                 | Key Assertions                                                |
| --------------------------------------- | ----------------------------------------------------------- | ------------------------------------------------------------- |
| `test_adapter_satisfies_protocol`       | `isinstance(ParserAdapter(), SingleFileValidator)`          | Returns `True`                                                |
| `test_parse_returns_parsed_model`       | `adapter.parse(simple_content, "test.txt")`                 | `ParsedLlmsTxt` with `title` set                              |
| `test_parse_applies_enrichments`        | `adapter.parse(content_with_canonical_sections, ...)`       | `canonical_name` populated                                    |
| `test_parse_extracts_metadata`          | `adapter.parse(content_with_frontmatter, ...)`              | `metadata` is `Metadata` instance                             |
| `test_classify_returns_classification`  | `adapter.classify(parsed)`                                  | `DocumentClassification` with `document_type` and `size_tier` |
| `test_validate_returns_stub`            | `adapter.validate(parsed, classification)`                  | `diagnostics=[]`, `level_achieved=0`                          |
| `test_score_returns_stub`               | `adapter.score(result)`                                     | `total_score=0`, `grade="N/A"`                                |
| `test_pipeline_integration_single_file` | Full pipeline run with 1 file                               | `EcosystemFile.parsed` populated                              |
| `test_pipeline_integration_multi_file`  | Full pipeline run with `tests/fixtures/ecosystems/healthy/` | All files parsed, `project_name` extracted                    |
| `test_pipeline_no_crash_on_broken_file` | Pipeline with unreadable file                               | Pipeline completes, file marked as failed                     |

---

## 8. Limitations

| Limitation                                     | Reason                                            | When Addressed                    |
| ---------------------------------------------- | ------------------------------------------------- | --------------------------------- |
| `validate()` is a stub                         | Validation engine not yet implemented             | v0.3.x                            |
| `score()` is a stub                            | Quality scorer not yet implemented                | v0.4.x                            |
| `FileMetadata` reconstructed in `classify()`   | Protocol signature doesn't include `FileMetadata` | v0.3.x protocol revision          |
| `has_null_bytes` not available in `classify()` | Post-decode, null bytes cannot be detected        | Structural analysis compensates   |
| No caching between `parse()` and `classify()`  | Each call re-processes from scratch               | Performance optimization deferred |

---

## 9. Dependencies

| Module                         | Purpose in v0.2.2d               |
| ------------------------------ | -------------------------------- |
| `parser/` (all v0.2.0 modules) | `parse_string()`                 |
| `parser/classifier.py`         | `classify_document()`            |
| `parser/section_matcher.py`    | `match_canonical_sections()`     |
| `parser/metadata.py`           | `extract_metadata()`             |
| `pipeline/stages.py`           | `SingleFileValidator` protocol   |
| `pipeline/per_file.py`         | `PerFileStage`                   |
| `pipeline/orchestrator.py`     | `EcosystemPipelineOrchestrator`  |
| `schema/validation.py`         | `ValidationResult` (stub output) |
| `schema/quality.py`            | `QualityScore` (stub output)     |
