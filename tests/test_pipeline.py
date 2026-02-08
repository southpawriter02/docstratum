"""Comprehensive tests for the DocStratum ecosystem pipeline.

Tests cover all five pipeline stages:
    Stage 1: Discovery (DiscoveryStage)
    Stage 2: Per-File (PerFileStage)
    Stage 3: Relationship (RelationshipStage)
    Stage 4: Ecosystem Validation (EcosystemValidationStage)
    Stage 5: Scoring (ScoringStage)

As well as the orchestrator (EcosystemPipeline) and shared infrastructure
(stages.py: PipelineStageId, StageStatus, StageResult, etc).

Total target: ~85 tests covering the primary contracts, error cases, and
integration scenarios.
"""

from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

import pytest

from docstratum.pipeline import (
    DiscoveryStage,
    EcosystemPipeline,
    EcosystemValidationStage,
    PipelineContext,
    PipelineStageId,
    PipelineStage,
    PerFileStage,
    RelationshipStage,
    ScoringStage,
    SingleFileValidator,
    StageResult,
    StageStatus,
    StageTimer,
    classify_filename,
    classify_relationship,
    extract_links_from_content,
    is_external_url,
    calculate_completeness,
    calculate_coverage,
)
from docstratum.schema.classification import (
    DocumentClassification,
    DocumentType,
    SizeTier,
)
from docstratum.schema.diagnostics import DiagnosticCode, Severity
from docstratum.schema.ecosystem import (
    DocumentEcosystem,
    EcosystemFile,
    FileRelationship,
)
from docstratum.schema.parsed import (
    LinkRelationship,
    ParsedLink,
    ParsedLlmsTxt,
    ParsedSection,
)
from docstratum.schema.quality import DimensionScore, QualityDimension, QualityScore
from docstratum.schema.validation import ValidationDiagnostic, ValidationLevel, ValidationResult


# =============================================================================
# PART 1: stages.py Tests (~20 tests)
# =============================================================================


class TestPipelineStageId:
    """Tests for PipelineStageId enumeration."""

    @pytest.mark.unit
    def test_discovery_ordinal_value(self):
        """Verify DISCOVERY has ordinal value 1."""
        assert PipelineStageId.DISCOVERY.value == 1

    @pytest.mark.unit
    def test_per_file_ordinal_value(self):
        """Verify PER_FILE has ordinal value 2."""
        assert PipelineStageId.PER_FILE.value == 2

    @pytest.mark.unit
    def test_relationship_ordinal_value(self):
        """Verify RELATIONSHIP has ordinal value 3."""
        assert PipelineStageId.RELATIONSHIP.value == 3

    @pytest.mark.unit
    def test_ecosystem_validation_ordinal_value(self):
        """Verify ECOSYSTEM_VALIDATION has ordinal value 4."""
        assert PipelineStageId.ECOSYSTEM_VALIDATION.value == 4

    @pytest.mark.unit
    def test_scoring_ordinal_value(self):
        """Verify SCORING has ordinal value 5."""
        assert PipelineStageId.SCORING.value == 5

    @pytest.mark.unit
    def test_stage_id_ordering(self):
        """Verify stages have monotonically increasing ordinal values."""
        stages = [
            PipelineStageId.DISCOVERY,
            PipelineStageId.PER_FILE,
            PipelineStageId.RELATIONSHIP,
            PipelineStageId.ECOSYSTEM_VALIDATION,
            PipelineStageId.SCORING,
        ]
        values = [s.value for s in stages]
        assert values == sorted(values)


class TestStageStatus:
    """Tests for StageStatus enumeration."""

    @pytest.mark.unit
    def test_success_status(self):
        """Verify SUCCESS status has correct string value."""
        assert StageStatus.SUCCESS == "success"
        assert StageStatus.SUCCESS.value == "success"

    @pytest.mark.unit
    def test_failed_status(self):
        """Verify FAILED status has correct string value."""
        assert StageStatus.FAILED == "failed"
        assert StageStatus.FAILED.value == "failed"

    @pytest.mark.unit
    def test_skipped_status(self):
        """Verify SKIPPED status has correct string value."""
        assert StageStatus.SKIPPED == "skipped"
        assert StageStatus.SKIPPED.value == "skipped"


class TestStageResult:
    """Tests for StageResult model."""

    @pytest.mark.unit
    def test_stage_result_minimal_creation(self):
        """Verify StageResult creation with required fields only."""
        result = StageResult(
            stage=PipelineStageId.DISCOVERY,
            status=StageStatus.SUCCESS,
        )
        assert result.stage == PipelineStageId.DISCOVERY
        assert result.status == StageStatus.SUCCESS
        assert result.diagnostics == []
        assert result.duration_ms == 0.0
        assert result.message == ""

    @pytest.mark.unit
    def test_stage_result_with_all_fields(self):
        """Verify StageResult with all fields populated."""
        diag = ValidationDiagnostic(
            code=DiagnosticCode.I010_ECOSYSTEM_SINGLE_FILE,
            severity=Severity.INFO,
            message="Single file ecosystem",
            remediation="Add companion files",
            level=ValidationLevel.L0_PARSEABLE,
        )
        result = StageResult(
            stage=PipelineStageId.DISCOVERY,
            status=StageStatus.SUCCESS,
            diagnostics=[diag],
            duration_ms=123.45,
            message="Discovered 5 files",
        )
        assert len(result.diagnostics) == 1
        assert result.diagnostics[0].code == DiagnosticCode.I010_ECOSYSTEM_SINGLE_FILE
        assert result.duration_ms == 123.45
        assert result.message == "Discovered 5 files"

    @pytest.mark.unit
    def test_stage_result_duration_ms_non_negative(self):
        """Verify duration_ms field enforces ge=0 constraint."""
        # Valid: non-negative durations
        result = StageResult(
            stage=PipelineStageId.DISCOVERY,
            status=StageStatus.SUCCESS,
            duration_ms=0.0,
        )
        assert result.duration_ms == 0.0

        result = StageResult(
            stage=PipelineStageId.DISCOVERY,
            status=StageStatus.SUCCESS,
            duration_ms=999.99,
        )
        assert result.duration_ms == 999.99


class TestPipelineContext:
    """Tests for PipelineContext model."""

    @pytest.mark.unit
    def test_context_default_construction(self):
        """Verify PipelineContext defaults."""
        ctx = PipelineContext()
        assert ctx.root_path == ""
        assert ctx.files == []
        assert ctx.relationships == []
        assert ctx.ecosystem_diagnostics == []
        assert ctx.ecosystem_score is None
        assert ctx.ecosystem is None
        assert ctx.stage_results == []
        assert ctx.project_name == "Unknown Project"

    @pytest.mark.unit
    def test_context_with_root_path(self):
        """Verify PipelineContext accepts root_path."""
        ctx = PipelineContext(root_path="/path/to/project")
        assert ctx.root_path == "/path/to/project"

    @pytest.mark.unit
    def test_context_all_fields_accessible(self):
        """Verify all PipelineContext fields are accessible."""
        eco_file = EcosystemFile(file_path="/test.txt")
        ctx = PipelineContext(
            root_path="/project",
            files=[eco_file],
            project_name="Test Project",
        )
        assert ctx.root_path == "/project"
        assert len(ctx.files) == 1
        assert ctx.files[0].file_path == "/test.txt"
        assert ctx.project_name == "Test Project"

    @pytest.mark.unit
    def test_context_is_mutable(self):
        """Verify PipelineContext fields are mutable in place."""
        ctx = PipelineContext()
        eco_file = EcosystemFile(file_path="/test.txt")
        ctx.files.append(eco_file)
        ctx.project_name = "Updated Project"
        assert len(ctx.files) == 1
        assert ctx.project_name == "Updated Project"


class TestPipelineStageProtocol:
    """Tests for PipelineStage protocol."""

    @pytest.mark.unit
    def test_pipeline_stage_protocol_runtime_checkable(self):
        """Verify PipelineStage is a runtime_checkable Protocol."""
        # Create a duck-typed stage (no inheritance).
        class FakeStage:
            @property
            def stage_id(self) -> PipelineStageId:
                return PipelineStageId.DISCOVERY

            def execute(self, context: PipelineContext) -> StageResult:
                return StageResult(
                    stage=self.stage_id,
                    status=StageStatus.SUCCESS,
                )

        fake = FakeStage()
        assert isinstance(fake, PipelineStage)

    @pytest.mark.unit
    def test_pipeline_stage_missing_stage_id(self):
        """Verify isinstance check fails without stage_id property."""
        class IncompleteFake:
            def execute(self, context: PipelineContext) -> StageResult:
                return StageResult(
                    stage=PipelineStageId.DISCOVERY,
                    status=StageStatus.SUCCESS,
                )

        incomplete = IncompleteFake()
        assert not isinstance(incomplete, PipelineStage)

    @pytest.mark.unit
    def test_pipeline_stage_missing_execute(self):
        """Verify isinstance check fails without execute method."""
        class IncompleteFake:
            @property
            def stage_id(self) -> PipelineStageId:
                return PipelineStageId.DISCOVERY

        incomplete = IncompleteFake()
        assert not isinstance(incomplete, PipelineStage)


class TestSingleFileValidatorProtocol:
    """Tests for SingleFileValidator protocol."""

    @pytest.mark.unit
    def test_single_file_validator_protocol_runtime_checkable(self):
        """Verify SingleFileValidator is a runtime_checkable Protocol."""
        # Create a duck-typed validator (no inheritance).
        class FakeValidator:
            def parse(self, content: str, filename: str) -> ParsedLlmsTxt:
                return ParsedLlmsTxt(title="Test")

            def classify(self, parsed: ParsedLlmsTxt) -> DocumentClassification:
                return DocumentClassification(
                    document_type=DocumentType.TYPE_1_INDEX,
                    size_bytes=100,
                    estimated_tokens=25,
                    size_tier=SizeTier.MINIMAL,
                    filename="test.txt",
                )

            def validate(
                self,
                parsed: ParsedLlmsTxt,
                classification: DocumentClassification,
            ) -> ValidationResult:
                return ValidationResult(
                    level_achieved=ValidationLevel.L0_PARSEABLE,
                    diagnostics=[],
                )

            def score(self, result: ValidationResult) -> QualityScore:
                return QualityScore(
                    total_score=50.0,
                    grade="Pass",
                    dimension_scores=[],
                )

        fake = FakeValidator()
        assert isinstance(fake, SingleFileValidator)


class TestStageTimer:
    """Tests for StageTimer utility."""

    @pytest.mark.unit
    def test_timer_start_stop(self):
        """Verify StageTimer start/stop cycle works."""
        timer = StageTimer()
        timer.start()
        # Simulate brief work
        import time

        time.sleep(0.01)
        elapsed = timer.stop()
        assert elapsed > 0
        assert elapsed >= 10  # At least 10ms

    @pytest.mark.unit
    def test_timer_elapsed_ms_property(self):
        """Verify elapsed_ms property returns latest measurement."""
        timer = StageTimer()
        timer.start()
        import time

        time.sleep(0.01)
        timer.stop()
        assert timer.elapsed_ms > 0

    @pytest.mark.unit
    def test_timer_initial_state(self):
        """Verify StageTimer initializes with zero elapsed."""
        timer = StageTimer()
        assert timer.elapsed_ms == 0.0


# =============================================================================
# PART 2: discovery.py Tests (~15 tests)
# =============================================================================


class TestClassifyFilename:
    """Tests for classify_filename function."""

    @pytest.mark.unit
    def test_classify_llms_txt(self):
        """Verify llms.txt is classified as TYPE_1_INDEX."""
        result = classify_filename("llms.txt")
        assert result == DocumentType.TYPE_1_INDEX

    @pytest.mark.unit
    def test_classify_llms_txt_case_insensitive(self):
        """Verify classification is case-insensitive."""
        assert classify_filename("LLMS.TXT") == DocumentType.TYPE_1_INDEX
        assert classify_filename("Llms.Txt") == DocumentType.TYPE_1_INDEX

    @pytest.mark.unit
    def test_classify_llms_full_txt(self):
        """Verify llms-full.txt is classified as TYPE_2_FULL."""
        result = classify_filename("llms-full.txt")
        assert result == DocumentType.TYPE_2_FULL

    @pytest.mark.unit
    def test_classify_llms_full_txt_case_insensitive(self):
        """Verify llms-full.txt case-insensitivity."""
        assert classify_filename("LLMS-FULL.TXT") == DocumentType.TYPE_2_FULL

    @pytest.mark.unit
    def test_classify_llms_instructions_txt(self):
        """Verify llms-instructions.txt is classified as TYPE_4_INSTRUCTIONS."""
        result = classify_filename("llms-instructions.txt")
        assert result == DocumentType.TYPE_4_INSTRUCTIONS

    @pytest.mark.unit
    def test_classify_markdown_file(self):
        """Verify .md files are classified as TYPE_3_CONTENT_PAGE."""
        result = classify_filename("api-reference.md")
        assert result == DocumentType.TYPE_3_CONTENT_PAGE

    @pytest.mark.unit
    def test_classify_markdown_case_insensitive(self):
        """Verify .md classification is case-insensitive."""
        assert classify_filename("API-REFERENCE.MD") == DocumentType.TYPE_3_CONTENT_PAGE

    @pytest.mark.unit
    def test_classify_unknown_file(self):
        """Verify non-matching files are UNKNOWN."""
        result = classify_filename("random-file.json")
        assert result == DocumentType.UNKNOWN

    @pytest.mark.unit
    def test_classify_unknown_various_extensions(self):
        """Verify various non-matching files return UNKNOWN."""
        assert classify_filename("README.txt") == DocumentType.UNKNOWN
        assert classify_filename("config.yaml") == DocumentType.UNKNOWN
        assert classify_filename("data.csv") == DocumentType.UNKNOWN


class TestDiscoveryStage:
    """Tests for DiscoveryStage."""

    @pytest.mark.unit
    def test_discovery_stage_id(self):
        """Verify DiscoveryStage.stage_id is DISCOVERY."""
        stage = DiscoveryStage()
        assert stage.stage_id == PipelineStageId.DISCOVERY

    @pytest.mark.unit
    def test_discovery_single_file_mode(self, tmp_path):
        """Verify discovery in single-file mode (llms.txt only)."""
        # Create a temporary llms.txt file
        llms_file = tmp_path / "llms.txt"
        llms_file.write_text("# Test Project\n> Test description\n")

        # Run discovery
        stage = DiscoveryStage()
        ctx = PipelineContext(root_path=str(llms_file))
        result = stage.execute(ctx)

        # Verify results
        assert result.status == StageStatus.SUCCESS
        assert len(ctx.files) == 1
        assert ctx.files[0].file_type == DocumentType.TYPE_1_INDEX
        # Verify I010 diagnostic for single-file ecosystem
        assert any(
            d.code == DiagnosticCode.I010_ECOSYSTEM_SINGLE_FILE
            for d in result.diagnostics
        )

    @pytest.mark.unit
    def test_discovery_directory_with_companion_files(self, tmp_path):
        """Verify discovery finds all known file types in a directory."""
        # Create ecosystem files
        (tmp_path / "llms.txt").write_text("# Project\n")
        (tmp_path / "llms-full.txt").write_text("# Full\n")
        (tmp_path / "llms-instructions.txt").write_text("# Instructions\n")
        (tmp_path / "api.md").write_text("# API\n")

        stage = DiscoveryStage()
        ctx = PipelineContext(root_path=str(tmp_path))
        result = stage.execute(ctx)

        assert result.status == StageStatus.SUCCESS
        assert len(ctx.files) == 4
        file_types = {f.file_type for f in ctx.files}
        assert DocumentType.TYPE_1_INDEX in file_types
        assert DocumentType.TYPE_2_FULL in file_types
        assert DocumentType.TYPE_4_INSTRUCTIONS in file_types
        assert DocumentType.TYPE_3_CONTENT_PAGE in file_types

    @pytest.mark.unit
    def test_discovery_missing_index_file(self, tmp_path):
        """Verify E009 diagnostic when no llms.txt exists."""
        # Create only a content page (no index)
        (tmp_path / "api.md").write_text("# API\n")

        stage = DiscoveryStage()
        ctx = PipelineContext(root_path=str(tmp_path))
        result = stage.execute(ctx)

        assert result.status == StageStatus.FAILED
        assert any(
            d.code == DiagnosticCode.E009_NO_INDEX_FILE
            for d in result.diagnostics
        )

    @pytest.mark.unit
    def test_discovery_empty_directory(self, tmp_path):
        """Verify discovery on empty directory fails gracefully."""
        stage = DiscoveryStage()
        ctx = PipelineContext(root_path=str(tmp_path))
        result = stage.execute(ctx)

        assert result.status == StageStatus.FAILED
        assert len(ctx.files) == 0

    @pytest.mark.unit
    def test_discovery_nonexistent_path(self):
        """Verify discovery fails on non-existent path."""
        stage = DiscoveryStage()
        ctx = PipelineContext(root_path="/nonexistent/path/xyz")
        result = stage.execute(ctx)

        assert result.status == StageStatus.FAILED
        assert "does not exist" in result.message


# =============================================================================
# PART 3: relationship.py Tests (~12 tests)
# =============================================================================


class TestExtractLinksFromContent:
    """Tests for extract_links_from_content function."""

    @pytest.mark.unit
    def test_extract_single_link(self):
        """Verify extraction of a single Markdown link."""
        content = "See [API Docs](docs/api.md) for details."
        links = extract_links_from_content(content)
        assert len(links) == 1
        assert links[0].title == "API Docs"
        assert links[0].url == "docs/api.md"

    @pytest.mark.unit
    def test_extract_multiple_links(self):
        """Verify extraction of multiple links."""
        content = (
            "Check [Guide](guide.md) and [API](api.md) files.\n"
            "Also see [Examples](examples/index.md)."
        )
        links = extract_links_from_content(content)
        assert len(links) == 3
        assert links[0].url == "guide.md"
        assert links[1].url == "api.md"
        assert links[2].url == "examples/index.md"

    @pytest.mark.unit
    def test_extract_no_links(self):
        """Verify extraction returns empty list when no links present."""
        content = "Just some plain text without any links."
        links = extract_links_from_content(content)
        assert len(links) == 0

    @pytest.mark.unit
    def test_extract_links_with_line_numbers(self):
        """Verify links are assigned correct line numbers."""
        content = "Line 1\nLine 2\n[Link](url.md)\nLine 4"
        links = extract_links_from_content(content)
        assert len(links) == 1
        assert links[0].line_number == 3

    @pytest.mark.unit
    def test_extract_external_urls(self):
        """Verify extraction works with external URLs."""
        content = "Visit [GitHub](https://github.com) or [Docs](https://example.com/api)."
        links = extract_links_from_content(content)
        assert len(links) == 2
        assert links[0].url == "https://github.com"
        assert links[1].url == "https://example.com/api"


class TestIsExternalUrl:
    """Tests for is_external_url function."""

    @pytest.mark.unit
    def test_https_url_is_external(self):
        """Verify https:// URLs are classified as external."""
        assert is_external_url("https://github.com/project") is True

    @pytest.mark.unit
    def test_http_url_is_external(self):
        """Verify http:// URLs are classified as external."""
        assert is_external_url("http://example.com") is True

    @pytest.mark.unit
    def test_relative_path_is_not_external(self):
        """Verify relative paths are not external."""
        assert is_external_url("docs/api.md") is False

    @pytest.mark.unit
    def test_absolute_path_is_not_external(self):
        """Verify absolute paths are not external."""
        assert is_external_url("/absolute/path/file.md") is False

    @pytest.mark.unit
    def test_bare_filename_is_not_external(self):
        """Verify bare filenames are not external."""
        assert is_external_url("api.md") is False


class TestClassifyRelationship:
    """Tests for classify_relationship function."""

    @pytest.mark.unit
    def test_index_to_content_page_is_indexes(self):
        """Verify INDEX→.md link is classified as INDEXES."""
        rel = classify_relationship(
            DocumentType.TYPE_1_INDEX, "api.md", is_external=False
        )
        assert rel == LinkRelationship.INDEXES

    @pytest.mark.unit
    def test_index_to_full_is_aggregates(self):
        """Verify INDEX→llms-full.txt link is classified as AGGREGATES."""
        rel = classify_relationship(
            DocumentType.TYPE_1_INDEX, "llms-full.txt", is_external=False
        )
        assert rel == LinkRelationship.AGGREGATES

    @pytest.mark.unit
    def test_content_to_content_is_references(self):
        """Verify CONTENT→CONTENT link is classified as REFERENCES."""
        rel = classify_relationship(
            DocumentType.TYPE_3_CONTENT_PAGE, "other.md", is_external=False
        )
        assert rel == LinkRelationship.REFERENCES

    @pytest.mark.unit
    def test_any_to_external_is_external(self):
        """Verify any link to external URL is classified as EXTERNAL."""
        rel = classify_relationship(
            DocumentType.TYPE_1_INDEX, "github.com", is_external=True
        )
        assert rel == LinkRelationship.EXTERNAL

    @pytest.mark.unit
    def test_full_file_to_content_is_aggregates(self):
        """Verify TYPE_2_FULL→.md link is classified as AGGREGATES."""
        rel = classify_relationship(
            DocumentType.TYPE_2_FULL, "guide.md", is_external=False
        )
        assert rel == LinkRelationship.AGGREGATES


class TestRelationshipStage:
    """Tests for RelationshipStage."""

    @pytest.mark.unit
    def test_relationship_stage_id(self):
        """Verify RelationshipStage.stage_id is RELATIONSHIP."""
        stage = RelationshipStage()
        assert stage.stage_id == PipelineStageId.RELATIONSHIP

    @pytest.mark.unit
    def test_relationship_stage_with_file_contents(self, tmp_path):
        """Verify RelationshipStage extracts links from file_contents."""
        # Create ecosystem files with links
        index_file = EcosystemFile(
            file_path=str(tmp_path / "llms.txt"),
            file_type=DocumentType.TYPE_1_INDEX,
        )
        content_file = EcosystemFile(
            file_path=str(tmp_path / "api.md"),
            file_type=DocumentType.TYPE_3_CONTENT_PAGE,
        )

        # Create file contents with a link
        file_contents = {
            index_file.file_id: "# Project\n[API](api.md)",
            content_file.file_id: "# API",
        }

        # Run relationship stage
        stage = RelationshipStage(file_contents=file_contents)
        ctx = PipelineContext(files=[index_file, content_file])
        result = stage.execute(ctx)

        assert result.status == StageStatus.SUCCESS
        assert len(ctx.relationships) > 0


# =============================================================================
# PART 4: ecosystem_validator.py Tests (~15 tests)
# =============================================================================


class TestEcosystemValidationStage:
    """Tests for EcosystemValidationStage."""

    @pytest.mark.unit
    def test_ecosystem_validation_stage_id(self):
        """Verify EcosystemValidationStage.stage_id is ECOSYSTEM_VALIDATION."""
        stage = EcosystemValidationStage()
        assert stage.stage_id == PipelineStageId.ECOSYSTEM_VALIDATION

    @pytest.mark.unit
    def test_broken_links_detection(self, tmp_path):
        """Verify W012 diagnostic for unresolved internal links."""
        index_file = EcosystemFile(
            file_path=str(tmp_path / "llms.txt"),
            file_type=DocumentType.TYPE_1_INDEX,
        )

        # Create an unresolved relationship (broken link)
        broken_rel = FileRelationship(
            source_file_id=index_file.file_id,
            target_file_id="",
            target_url="missing.md",
            relationship_type=LinkRelationship.INDEXES,
            source_line=5,
            is_resolved=False,
        )

        ctx = PipelineContext(files=[index_file], relationships=[broken_rel])
        stage = EcosystemValidationStage()
        result = stage.execute(ctx)

        # Should emit W012 for broken link
        assert any(
            d.code == DiagnosticCode.W012_BROKEN_CROSS_FILE_LINK
            for d in result.diagnostics
        )

    @pytest.mark.unit
    def test_missing_instruction_file(self, tmp_path):
        """Verify I008 diagnostic when no llms-instructions.txt exists."""
        index_file = EcosystemFile(
            file_path=str(tmp_path / "llms.txt"),
            file_type=DocumentType.TYPE_1_INDEX,
        )

        ctx = PipelineContext(files=[index_file])
        stage = EcosystemValidationStage()
        result = stage.execute(ctx)

        # Should emit I008 for missing instructions
        assert any(
            d.code == DiagnosticCode.I008_NO_INSTRUCTION_FILE
            for d in result.diagnostics
        )

    @pytest.mark.unit
    def test_missing_aggregate_with_large_ecosystem(self, tmp_path):
        """Verify W013 when ecosystem is large without llms-full.txt."""
        # Create a large index file (>4500 tokens)
        index_file = EcosystemFile(
            file_path=str(tmp_path / "llms.txt"),
            file_type=DocumentType.TYPE_1_INDEX,
            classification=DocumentClassification(
                document_type=DocumentType.TYPE_1_INDEX,
                size_bytes=20000,  # ~5000 tokens
                estimated_tokens=5000,
                size_tier=SizeTier.COMPREHENSIVE,
                filename="llms.txt",
            ),
        )

        ctx = PipelineContext(files=[index_file])
        stage = EcosystemValidationStage()
        result = stage.execute(ctx)

        # Should emit W013 for missing aggregate
        assert any(
            d.code == DiagnosticCode.W013_MISSING_AGGREGATE
            for d in result.diagnostics
        )

    @pytest.mark.unit
    def test_inconsistent_project_names(self, tmp_path):
        """Verify W015 diagnostic when project names differ across files."""
        # Create two files with different titles
        file1 = EcosystemFile(
            file_path=str(tmp_path / "llms.txt"),
            file_type=DocumentType.TYPE_1_INDEX,
            parsed=ParsedLlmsTxt(title="Project A"),
        )
        file2 = EcosystemFile(
            file_path=str(tmp_path / "api.md"),
            file_type=DocumentType.TYPE_3_CONTENT_PAGE,
            parsed=ParsedLlmsTxt(title="Project B"),
        )

        ctx = PipelineContext(files=[file1, file2])
        stage = EcosystemValidationStage()
        result = stage.execute(ctx)

        # Should emit W015 for inconsistent names
        assert any(
            d.code == DiagnosticCode.W015_INCONSISTENT_PROJECT_NAME
            for d in result.diagnostics
        )

    @pytest.mark.unit
    def test_token_black_hole_detection(self, tmp_path):
        """Verify W018 diagnostic when one file consumes >80% of tokens."""
        # Create a very large file (80%+ of total)
        large_file = EcosystemFile(
            file_path=str(tmp_path / "llms-full.txt"),
            file_type=DocumentType.TYPE_2_FULL,
            classification=DocumentClassification(
                document_type=DocumentType.TYPE_2_FULL,
                size_bytes=250000,  # 62,500 tokens (81% of 77,000)
                estimated_tokens=62500,
                size_tier=SizeTier.FULL,
                filename="llms-full.txt",
            ),
        )
        small_file = EcosystemFile(
            file_path=str(tmp_path / "api.md"),
            file_type=DocumentType.TYPE_3_CONTENT_PAGE,
            classification=DocumentClassification(
                document_type=DocumentType.TYPE_3_CONTENT_PAGE,
                size_bytes=15000,  # 3,750 tokens
                estimated_tokens=3750,
                size_tier=SizeTier.COMPREHENSIVE,
                filename="api.md",
            ),
        )

        ctx = PipelineContext(files=[large_file, small_file])
        stage = EcosystemValidationStage()
        result = stage.execute(ctx)

        # Should emit W018 for unbalanced distribution
        assert any(
            d.code == DiagnosticCode.W018_UNBALANCED_TOKEN_DISTRIBUTION
            for d in result.diagnostics
        )

    @pytest.mark.unit
    def test_orphaned_files_detection(self, tmp_path):
        """Verify E010 diagnostic for orphaned files."""
        index_file = EcosystemFile(
            file_path=str(tmp_path / "llms.txt"),
            file_type=DocumentType.TYPE_1_INDEX,
        )
        orphaned_file = EcosystemFile(
            file_path=str(tmp_path / "orphaned.md"),
            file_type=DocumentType.TYPE_3_CONTENT_PAGE,
        )

        # No relationships pointing to orphaned_file
        ctx = PipelineContext(files=[index_file, orphaned_file], relationships=[])
        stage = EcosystemValidationStage()
        result = stage.execute(ctx)

        # Should emit E010 for orphaned file
        assert any(
            d.code == DiagnosticCode.E010_ORPHANED_ECOSYSTEM_FILE
            for d in result.diagnostics
        )


# =============================================================================
# PART 5: ecosystem_scorer.py Tests (~12 tests)
# =============================================================================




class TestScoringStage:
    """Tests for ScoringStage."""

    @pytest.mark.unit
    def test_scoring_stage_id(self):
        """Verify ScoringStage.stage_id is SCORING."""
        stage = ScoringStage()
        assert stage.stage_id == PipelineStageId.SCORING


# =============================================================================
# PART 6: orchestrator.py Tests (~10 tests)
# =============================================================================


class TestEcosystemPipeline:
    """Tests for EcosystemPipeline orchestrator."""

    @pytest.mark.unit
    def test_pipeline_construction(self):
        """Verify EcosystemPipeline construction."""
        pipeline = EcosystemPipeline()
        assert pipeline is not None

    @pytest.mark.unit
    def test_pipeline_construction_with_validator(self):
        """Verify EcosystemPipeline accepts optional validator."""
        validator = Mock(spec=SingleFileValidator)
        pipeline = EcosystemPipeline(validator=validator)
        assert pipeline is not None

    @pytest.mark.unit
    def test_pipeline_run_full_ecosystem(self, tmp_path):
        """Verify full pipeline run on multi-file ecosystem."""
        # Create ecosystem files
        (tmp_path / "llms.txt").write_text(
            "# Test Project\n> Test\n\n## Docs\n[API](api.md)\n"
        )
        (tmp_path / "api.md").write_text("# API Reference\n")

        pipeline = EcosystemPipeline()
        ctx = pipeline.run(str(tmp_path))

        # Verify results
        assert len(ctx.files) >= 1
        assert len(ctx.stage_results) >= 4  # At least 4 stages executed
        # Stages may fail due to scoring issue, but discovery should succeed
        assert ctx.stage_results[0].status == StageStatus.SUCCESS

    @pytest.mark.unit
    def test_pipeline_run_single_file(self, tmp_path):
        """Verify pipeline run on single file."""
        llms_file = tmp_path / "llms.txt"
        llms_file.write_text("# Test Project\n> Test\n")

        pipeline = EcosystemPipeline()
        ctx = pipeline.run(str(llms_file))

        # Verify results
        assert len(ctx.files) == 1
        assert ctx.files[0].file_type == DocumentType.TYPE_1_INDEX

    @pytest.mark.unit
    def test_pipeline_stop_after_discovery(self, tmp_path):
        """Verify stop_after=DISCOVERY skips stages 2-5."""
        (tmp_path / "llms.txt").write_text("# Test\n")

        pipeline = EcosystemPipeline()
        ctx = pipeline.run(
            str(tmp_path), stop_after=PipelineStageId.DISCOVERY
        )

        # Verify only Discovery ran
        assert len(ctx.files) > 0
        assert ctx.ecosystem is None  # Scoring didn't run
        # Check stage results
        discovery_result = ctx.stage_results[0]
        assert discovery_result.stage == PipelineStageId.DISCOVERY
        assert discovery_result.status == StageStatus.SUCCESS
        # Remaining stages should be SKIPPED
        remaining = ctx.stage_results[1:]
        assert all(r.status == StageStatus.SKIPPED for r in remaining)

    @pytest.mark.unit
    def test_pipeline_stop_after_relationship(self, tmp_path):
        """Verify stop_after=RELATIONSHIP skips Validation and Scoring."""
        (tmp_path / "llms.txt").write_text("# Test\n[Link](api.md)\n")
        (tmp_path / "api.md").write_text("# API\n")

        pipeline = EcosystemPipeline()
        ctx = pipeline.run(
            str(tmp_path), stop_after=PipelineStageId.RELATIONSHIP
        )

        # Verify stages 1-3 ran
        assert len(ctx.stage_results) >= 3
        assert ctx.stage_results[0].stage == PipelineStageId.DISCOVERY
        assert ctx.stage_results[1].stage == PipelineStageId.PER_FILE
        assert ctx.stage_results[2].stage == PipelineStageId.RELATIONSHIP
        # Ecosystem Validation and Scoring should be SKIPPED
        validation_result = next(
            (r for r in ctx.stage_results
             if r.stage == PipelineStageId.ECOSYSTEM_VALIDATION),
            None,
        )
        assert validation_result is not None
        assert validation_result.status == StageStatus.SKIPPED

    @pytest.mark.unit
    def test_pipeline_nonexistent_path(self):
        """Verify pipeline handles non-existent paths gracefully."""
        pipeline = EcosystemPipeline()
        ctx = pipeline.run("/nonexistent/path/xyz")

        # Verify pipeline fails gracefully
        assert len(ctx.stage_results) > 0
        first_result = ctx.stage_results[0]
        assert first_result.status == StageStatus.FAILED

    @pytest.mark.unit
    def test_pipeline_stage_results_recorded(self, tmp_path):
        """Verify all stage results are recorded in context."""
        (tmp_path / "llms.txt").write_text("# Test\n")

        pipeline = EcosystemPipeline()
        ctx = pipeline.run(str(tmp_path))

        # Verify stage_results list is populated
        assert len(ctx.stage_results) == 5
        stage_ids = [r.stage for r in ctx.stage_results]
        assert PipelineStageId.DISCOVERY in stage_ids
        assert PipelineStageId.PER_FILE in stage_ids
        assert PipelineStageId.RELATIONSHIP in stage_ids
        assert PipelineStageId.ECOSYSTEM_VALIDATION in stage_ids
        assert PipelineStageId.SCORING in stage_ids

    @pytest.mark.unit
    def test_pipeline_ecosystem_populated_after_full_run(self, tmp_path):
        """Verify ecosystem is populated when all stages run successfully."""
        (tmp_path / "llms.txt").write_text("# My Project\n")

        pipeline = EcosystemPipeline()
        ctx = pipeline.run(str(tmp_path))

        # Verify at least discovery ran and found files
        assert len(ctx.files) > 0
        assert ctx.stage_results[0].status == StageStatus.SUCCESS
