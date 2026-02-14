"""Integration tests for ParserAdapter (v0.2.2d).

Tests the ``ParserAdapter`` class that bridges the parser pipeline to the
``SingleFileValidator`` protocol, verifying protocol satisfaction, parse
enrichments, classification, stub validation/scoring, and full pipeline
integration through the ``EcosystemPipeline`` orchestrator.

10 tests:
    - Protocol compliance (1)
    - Parse behavior (3: basic parse, enrichments, metadata)
    - Classify behavior (1)
    - Validate/Score stubs (2)
    - Full pipeline integration (3: single file, multi file, broken file)

See:
    - docs/design/03-parser/RR-SPEC-v0.2.2d-pipeline-integration.md
    - docs/design/00-meta/RR-META-testing-standards.md
"""

import os
import sys
from pathlib import Path

import pytest

from docstratum.parser.validator_adapter import ParserAdapter
from docstratum.pipeline.orchestrator import EcosystemPipeline
from docstratum.pipeline.stages import SingleFileValidator
from docstratum.schema.classification import DocumentClassification, DocumentType
from docstratum.schema.parsed import ParsedLlmsTxt
from docstratum.schema.quality import QualityGrade, QualityScore
from docstratum.schema.validation import ValidationLevel, ValidationResult

# ── Fixture directories ──────────────────────────────────────────────
ECOSYSTEMS_DIR = Path(__file__).parent / "fixtures" / "ecosystems"


class TestParserAdapter:
    """Unit-level tests for the ParserAdapter class (v0.2.2d)."""

    def test_adapter_satisfies_protocol(self):
        """ParserAdapter satisfies the SingleFileValidator runtime protocol.

        The ``SingleFileValidator`` protocol is ``@runtime_checkable``,
        so ``isinstance()`` verifies all four method signatures match.

        Grounding: v0.2.2d §6 — acceptance criterion 2.
        """
        # Arrange
        adapter = ParserAdapter()

        # Act & Assert
        assert isinstance(adapter, SingleFileValidator)

    def test_parse_returns_parsed_model(self):
        """parse() returns a ParsedLlmsTxt with title, sections, and links.

        Grounding: v0.2.2d §6 — acceptance criterion 3.
        """
        # Arrange
        adapter = ParserAdapter()
        content = (
            "# My Project\n"
            "\n"
            "> A test project description.\n"
            "\n"
            "## Docs\n"
            "\n"
            "- [API Reference](https://api.example.com): API docs\n"
        )

        # Act
        doc = adapter.parse(content, "llms.txt")

        # Assert
        assert isinstance(doc, ParsedLlmsTxt)
        assert doc.title == "My Project"
        assert doc.source_filename == "llms.txt"
        assert len(doc.sections) == 1
        assert doc.sections[0].name == "Docs"
        assert doc.total_links == 1

    def test_parse_applies_enrichments(self):
        """parse() applies canonical section matching enrichment.

        Sections whose names match a canonical name (or alias) should
        have their ``canonical_name`` field populated after parse().

        Grounding: v0.2.2d §6 — acceptance criterion 3 (enrichments).
        """
        # Arrange
        adapter = ParserAdapter()
        content = (
            "# Project\n"
            "\n"
            "> Description\n"
            "\n"
            "## Getting Started\n"
            "\n"
            "- [Guide](https://example.com): Intro guide\n"
        )

        # Act
        doc = adapter.parse(content, "llms.txt")

        # Assert — canonical_name populated by match_canonical_sections
        assert doc.sections[0].name == "Getting Started"
        assert doc.sections[0].canonical_name == "Getting Started"

    def test_parse_extracts_metadata(self):
        """parse() calls extract_metadata; result is stashed on adapter.

        ``ParsedLlmsTxt`` does not have a ``metadata`` field, so the
        extraction result is stored as ``_last_metadata`` on the adapter.
        The document itself should still parse correctly despite the
        YAML frontmatter being present.

        Grounding: v0.2.2d §6 — acceptance criterion 3 (enrichments).
        """
        # Arrange
        adapter = ParserAdapter()
        content = (
            "---\n"
            "site_name: Test Project\n"
            "generator: manual\n"
            "---\n"
            "# Test\n"
            "\n"
            "> A test document\n"
        )

        # Act
        doc = adapter.parse(content, "llms.txt")

        # Assert — metadata extracted and stashed
        assert adapter._last_metadata is not None
        assert adapter._last_metadata.site_name == "Test Project"
        assert adapter._last_metadata.generator == "manual"
        # Doc still parses correctly (frontmatter stripped before tokenizing)
        assert doc.title == "Test"

    def test_classify_returns_classification(self):
        """classify() returns a DocumentClassification with type and tier.

        Grounding: v0.2.2d §6 — acceptance criterion 4.
        """
        # Arrange
        adapter = ParserAdapter()
        content = (
            "# My App\n"
            "\n"
            "> App description\n"
            "\n"
            "## Docs\n"
            "\n"
            "- [API](https://api.example.com): API docs\n"
        )
        doc = adapter.parse(content, "llms.txt")

        # Act
        classification = adapter.classify(doc)

        # Assert
        assert isinstance(classification, DocumentClassification)
        assert classification.document_type == DocumentType.TYPE_1_INDEX
        assert classification.size_tier is not None
        assert classification.size_bytes > 0

    def test_validate_returns_stub(self):
        """validate() returns a stub ValidationResult with L0 and no diagnostics.

        Grounding: v0.2.2d §6 — acceptance criteria 5, 7.
        """
        # Arrange
        adapter = ParserAdapter()
        content = "# Test\n\n> Description\n"
        doc = adapter.parse(content, "llms.txt")
        classification = adapter.classify(doc)

        # Act
        result = adapter.validate(doc, classification)

        # Assert
        assert isinstance(result, ValidationResult)
        assert result.level_achieved == ValidationLevel.L0_PARSEABLE
        assert result.diagnostics == []

    def test_score_returns_stub(self):
        """score() returns a stub QualityScore with total_score=0 and CRITICAL grade.

        Grounding: v0.2.2d §6 — acceptance criterion 6.
        """
        # Arrange
        adapter = ParserAdapter()
        content = "# Test\n\n> Description\n"
        doc = adapter.parse(content, "llms.txt")
        classification = adapter.classify(doc)
        validation = adapter.validate(doc, classification)

        # Act
        quality = adapter.score(validation)

        # Assert
        assert isinstance(quality, QualityScore)
        assert quality.total_score == 0
        assert quality.grade == QualityGrade.CRITICAL
        assert len(quality.dimensions) == 3


class TestPipelineIntegration:
    """End-to-end pipeline integration tests with ParserAdapter (v0.2.2d)."""

    def test_pipeline_integration_single_file(self):
        """Full pipeline with ParserAdapter: single file has parsed data populated.

        Grounding: v0.2.2d §6 — acceptance criteria 8, 9.
        """
        # Arrange
        adapter = ParserAdapter()
        pipeline = EcosystemPipeline(validator=adapter)
        fixture_dir = ECOSYSTEMS_DIR / "single_file"

        # Act
        result = pipeline.run(str(fixture_dir))

        # Assert — file discovered and parsed
        assert len(result.files) >= 1
        index_files = [f for f in result.files if f.file_path.endswith("llms.txt")]
        assert len(index_files) == 1
        eco_file = index_files[0]
        assert eco_file.parsed is not None
        assert isinstance(eco_file.parsed, ParsedLlmsTxt)
        assert eco_file.parsed.title is not None
        # Classification also populated
        assert eco_file.classification is not None
        assert isinstance(eco_file.classification, DocumentClassification)

    def test_pipeline_integration_multi_file(self):
        """Full pipeline on healthy fixture: all files parsed, project_name extracted.

        The healthy fixture has 5 files. After running the pipeline with
        ``ParserAdapter``, every file should have ``parsed`` populated and
        ``context.project_name`` should be extracted from the index H1.

        Grounding: v0.2.2d §6 — acceptance criteria 9, 10, 11.
        """
        # Arrange
        adapter = ParserAdapter()
        pipeline = EcosystemPipeline(validator=adapter)
        fixture_dir = ECOSYSTEMS_DIR / "healthy"

        # Act
        result = pipeline.run(str(fixture_dir))

        # Assert — all files parsed
        assert len(result.files) == 5
        for eco_file in result.files:
            assert (
                eco_file.parsed is not None
            ), f"File {eco_file.file_path} was not parsed"

        # Assert — project name extracted from index file H1
        assert result.project_name == "DocStratum Project"

    def test_pipeline_no_crash_on_broken_file(self, tmp_path):
        """Pipeline with unreadable file completes without crash.

        Creates a minimal ecosystem where one file is unreadable. The
        pipeline should still complete, and the readable index file
        should be parsed successfully.

        Grounding: v0.2.2d §6 — acceptance criterion 11.
        """
        # Skip on Windows — chmod(0o000) doesn't work the same way
        if sys.platform == "win32":
            pytest.skip("File permissions test not supported on Windows")

        # Skip if running as root — root can read everything
        if os.getuid() == 0:
            pytest.skip("Cannot test permission denial as root")

        # Arrange — create a minimal ecosystem
        index_content = (
            "# Test Project\n"
            "\n"
            "> A test ecosystem\n"
            "\n"
            "## Docs\n"
            "\n"
            "- [Page](page.md): A content page\n"
        )
        (tmp_path / "llms.txt").write_text(index_content)
        broken_file = tmp_path / "page.md"
        broken_file.write_text("# Page\n\nSome content\n")
        broken_file.chmod(0o000)

        try:
            adapter = ParserAdapter()
            pipeline = EcosystemPipeline(validator=adapter)

            # Act
            result = pipeline.run(str(tmp_path))

            # Assert — pipeline completed (did not crash)
            assert len(result.stage_results) > 0

            # Assert — the index file was still parsed successfully
            index_files = [f for f in result.files if f.file_path.endswith("llms.txt")]
            assert len(index_files) == 1
            assert index_files[0].parsed is not None
        finally:
            # Restore permissions for cleanup
            broken_file.chmod(0o644)
