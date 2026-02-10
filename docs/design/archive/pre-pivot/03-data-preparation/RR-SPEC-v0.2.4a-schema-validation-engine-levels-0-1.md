# v0.2.4a — Schema Validation Engine (Levels 0-1)

> The Schema Validation Engine is the gatekeeper of llms.txt integrity. It performs the foundational checks that ensure YAML syntax correctness (Level 0: SYNTAX) and validates structural conformance to the DocStratum data model (Level 1: STRUCTURE). By combining YAML parsing, encoding detection, frontmatter extraction, type validation, and field presence checking, this engine catches errors early—before content validation wastes resources on malformed data. Error messages are precise, actionable, and include line numbers with fix suggestions.

## Objective

Implement automated schema validation that catches syntax errors and structural violations in llms.txt files before downstream validators run. This validation layer:
- Detects YAML parsing errors with precise error locations
- Validates file encoding and frontmatter structure
- Enforces Pydantic schema compliance for all data types
- Generates clear, developer-friendly error messages
- Integrates with the error code registry (E001-E007 for schema errors)
- Enables fast feedback loops during file authoring

## Scope Boundaries

**In Scope:**
- YAML parsing and encoding detection (UTF-8, UTF-16, etc.)
- Frontmatter extraction and validation
- Pydantic model definition for all llms.txt data structures
- Level 0 (SYNTAX): Basic parsing without semantic errors
- Level 1 (STRUCTURE): Field presence, type validation, required fields
- Custom validators for domain-specific validation rules
- Error code mapping (E001-E007) and actionable error messages
- Comprehensive pytest test suite (10+ test cases)
- JSON schema generation from Pydantic models for IDE support

**Out of Scope:**
- Content validation (URLs, link existence)—Level 2 handles this
- Quality scoring—Level 3 handles this
- Concurrent operations—handled in Level 2
- Database operations—handled in optimization phases

## Dependency Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  v0.2.4a: Schema Validation Engine                          │
│  (Levels 0-1: SYNTAX & STRUCTURE)                           │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
   ┌─────────┐  ┌────────┐  ┌────────────┐
   │YAML     │  │Encoding│  │Frontmatter │
   │Parsing  │  │Detect  │  │Extraction  │
   └────┬────┘  └────┬───┘  └─────┬──────┘
        │            │            │
        └────────────┼────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │ Pydantic Models      │
          │ (MasterIndex,        │
          │  ConceptMap,         │
          │  FewShotBank)        │
          └──────────┬───────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
   ┌──────────┐ ┌──────────┐ ┌──────────┐
   │Field     │ │Type      │ │Required  │
   │Presence  │ │Validation│ │Field     │
   │Check     │ │         │ │Enforce   │
   └────┬─────┘ └────┬─────┘ └────┬─────┘
        │            │            │
        └────────────┼────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │ Error Code Registry  │
          │ (E001-E007, W001)    │
          └──────────┬───────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │ Validation Report    │
          │ (with line numbers & │
          │  fix suggestions)    │
          └──────────────────────┘

Input: Raw llms.txt files (YAML format)
Output: Validation results with errors/warnings, exit codes, pass/fail status
```

## Section 1: YAML Parsing & Encoding Detection

### 1.1 Overview

Robust YAML parsing requires handling multiple encodings and detecting encoding issues before parsing. This section covers:
- Encoding detection (UTF-8, UTF-16, CP1252, etc.)
- YAML parsing with error location tracking
- BOM (Byte Order Mark) handling
- Error recovery and reporting

### 1.2 Complete Python Implementation

```python
# schema_validation/level_0_syntax.py

import yaml
import io
import chardet
from typing import Tuple, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ParseResult:
    """Result of YAML parsing attempt."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    line_number: Optional[int] = None
    encoding: Optional[str] = None
    raw_error: Optional[Exception] = None


class EncodingDetector:
    """Detects file encoding with fallback chain."""

    PREFERRED_ENCODING = 'utf-8'
    FALLBACK_ENCODINGS = ['utf-8-sig', 'utf-16', 'cp1252', 'iso-8859-1']
    MIN_CONFIDENCE = 0.7

    @staticmethod
    def detect(file_path: Path) -> Tuple[str, float]:
        """
        Detect file encoding using chardet library.

        Returns:
            Tuple of (encoding, confidence)
        """
        with open(file_path, 'rb') as f:
            raw_data = f.read()

        # Check for BOM first
        if raw_data.startswith(b'\xef\xbb\xbf'):
            return 'utf-8-sig', 1.0
        if raw_data.startswith(b'\xff\xfe'):
            return 'utf-16', 1.0
        if raw_data.startswith(b'\xfe\xff'):
            return 'utf-16-be', 1.0

        # Use chardet for detection
        detected = chardet.detect(raw_data)
        encoding = detected.get('encoding', 'utf-8')
        confidence = detected.get('confidence', 0.0)

        # Validate detection by attempting to decode
        if confidence < EncodingDetector.MIN_CONFIDENCE:
            encoding = 'utf-8'  # Default fallback

        return encoding, confidence

    @staticmethod
    def read_file(file_path: Path) -> Tuple[str, str, Optional[ParseResult]]:
        """
        Read file content with encoding detection.

        Returns:
            Tuple of (content, detected_encoding, error_result_if_any)
        """
        try:
            encoding, confidence = EncodingDetector.detect(file_path)

            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()

            return content, encoding, None

        except UnicodeDecodeError as e:
            error_msg = (
                f"E001 | ENCODING ERROR: File encoding could not be determined. "
                f"Attempted: {e.encoding}. Line ~{e.start // 80}. "
                f"Fix: Save file as UTF-8 without BOM."
            )
            return "", "unknown", ParseResult(
                success=False,
                error=error_msg,
                line_number=e.start // 80,
                raw_error=e
            )
        except Exception as e:
            error_msg = f"E001 | FILE READ ERROR: {str(e)}"
            return "", "unknown", ParseResult(
                success=False,
                error=error_msg,
                raw_error=e
            )


class YAMLParser:
    """Robust YAML parser with detailed error reporting."""

    @staticmethod
    def parse(file_path: Path) -> ParseResult:
        """
        Parse YAML file with comprehensive error handling.

        Returns:
            ParseResult with success status and parsed data or error details
        """
        # Step 1: Read file with encoding detection
        content, encoding, read_error = EncodingDetector.read_file(file_path)
        if read_error:
            return read_error

        # Step 2: Extract frontmatter (YAML between --- markers)
        frontmatter, document = YAMLParser._extract_frontmatter(content)

        # Step 3: Parse YAML
        try:
            data = yaml.safe_load(document)

            if data is None:
                data = {}

            if not isinstance(data, dict):
                return ParseResult(
                    success=False,
                    error="E002 | STRUCTURE ERROR: Root document must be an object/dict, "
                          f"got {type(data).__name__} instead. Fix: Ensure top level is key: value pairs.",
                    encoding=encoding,
                    line_number=1
                )

            return ParseResult(
                success=True,
                data=data,
                encoding=encoding
            )

        except yaml.YAMLError as e:
            # Extract line number from error message
            line_number = None
            if hasattr(e, 'problem_mark') and e.problem_mark:
                line_number = e.problem_mark.line + 1

            error_msg = YAMLParser._format_yaml_error(e, line_number)
            return ParseResult(
                success=False,
                error=error_msg,
                encoding=encoding,
                line_number=line_number,
                raw_error=e
            )

    @staticmethod
    def _extract_frontmatter(content: str) -> Tuple[Optional[str], str]:
        """
        Extract YAML frontmatter (optional --- delimited section at start).

        Returns:
            Tuple of (frontmatter, remaining_document)
        """
        lines = content.split('\n', 1)

        # Check if first line is ---
        if lines[0].strip() == '---':
            remaining = lines[1] if len(lines) > 1 else ""
            # Find closing ---
            parts = remaining.split('\n---\n', 1)
            if len(parts) == 2:
                return parts[0], parts[1]

        return None, content

    @staticmethod
    def _format_yaml_error(error: yaml.YAMLError, line_number: Optional[int]) -> str:
        """Format YAML error with actionable message."""
        error_msg = str(error)

        if 'expected' in error_msg.lower():
            suggestion = "Fix: Check indentation (use 2 spaces, not tabs)"
        elif 'duplicate' in error_msg.lower():
            suggestion = "Fix: Remove duplicate key"
        elif 'mapping values' in error_msg.lower():
            suggestion = "Fix: Use 'key: value' format. No colon in keys without quotes."
        else:
            suggestion = "Fix: Validate YAML syntax using online validator"

        location = f"Line {line_number}" if line_number else "Unknown location"
        return (
            f"E003 | YAML PARSE ERROR: {error_msg}. {location}. {suggestion}"
        )
```

### 1.3 Test Cases for Level 0

```python
# tests/test_level_0_syntax.py

import pytest
import tempfile
from pathlib import Path
from schema_validation.level_0_syntax import YAMLParser, EncodingDetector, ParseResult


class TestYAMLParsing:
    """Test YAML parsing and encoding detection."""

    @pytest.fixture
    def temp_yaml(self):
        """Create temporary YAML file."""
        def _create(content: str, encoding: str = 'utf-8') -> Path:
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='.yml', delete=False, encoding=encoding
            ) as f:
                f.write(content)
                return Path(f.name)
        return _create

    def test_valid_simple_yaml(self, temp_yaml):
        """Level 0: Valid simple YAML should parse successfully."""
        content = "master_index:\n  version: 1.0\n  created: 2025-01-01"
        path = temp_yaml(content)

        result = YAMLParser.parse(path)

        assert result.success
        assert result.data['master_index']['version'] == 1.0
        assert result.encoding == 'utf-8'

    def test_valid_nested_structure(self, temp_yaml):
        """Level 0: Complex nested structure should parse."""
        content = """
master_index:
  version: 1.0
  concept_map:
    entries:
      - id: "concept_1"
        name: "Test Concept"
        related_pages: ["page_1", "page_2"]
"""
        path = temp_yaml(content)

        result = YAMLParser.parse(path)

        assert result.success
        assert len(result.data['master_index']['concept_map']['entries']) == 1

    def test_invalid_yaml_syntax_missing_colon(self, temp_yaml):
        """Level 0: Missing colon should be caught."""
        content = "master_index\n  version: 1.0"
        path = temp_yaml(content)

        result = YAMLParser.parse(path)

        assert not result.success
        assert result.error.startswith("E003")
        assert "YAML PARSE ERROR" in result.error
        assert result.line_number is not None

    def test_invalid_yaml_bad_indentation(self, temp_yaml):
        """Level 0: Bad indentation should be caught."""
        content = "master_index:\n version: 1.0"  # Single space indent
        path = temp_yaml(content)

        result = YAMLParser.parse(path)

        assert not result.success
        assert "E003" in result.error

    def test_root_not_dict(self, temp_yaml):
        """Level 0: Root must be dict, not list or string."""
        content = "- item1\n- item2"
        path = temp_yaml(content)

        result = YAMLParser.parse(path)

        assert not result.success
        assert "E002" in result.error
        assert "must be an object/dict" in result.error

    def test_duplicate_keys(self, temp_yaml):
        """Level 0: Duplicate keys should be caught."""
        content = "version: 1.0\nversion: 2.0"
        path = temp_yaml(content)

        result = YAMLParser.parse(path)

        assert not result.success
        assert "E003" in result.error

    def test_encoding_utf8(self, temp_yaml):
        """Level 0: UTF-8 encoding detection."""
        content = "name: Test\ndescription: Café"
        path = temp_yaml(content, encoding='utf-8')

        result = YAMLParser.parse(path)

        assert result.success
        assert result.encoding in ['utf-8', 'utf-8-sig']

    def test_empty_file(self, temp_yaml):
        """Level 0: Empty file should parse to empty dict."""
        path = temp_yaml("")

        result = YAMLParser.parse(path)

        assert result.success
        assert result.data == {}

    def test_comments_handled(self, temp_yaml):
        """Level 0: YAML comments should be ignored."""
        content = "# This is a comment\nversion: 1.0\n# Another comment"
        path = temp_yaml(content)

        result = YAMLParser.parse(path)

        assert result.success
        assert result.data['version'] == 1.0
```

## Section 2: Pydantic Schema Models

### 2.1 Overview

Pydantic models define the expected structure of llms.txt files. Each model includes:
- Field type validation
- Required vs optional field enforcement
- Custom validators for domain rules
- JSON schema generation for IDE autocompletion

### 2.2 Complete Pydantic Models

```python
# schema_validation/models.py

from pydantic import BaseModel, Field, validator, root_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class LinkType(str, Enum):
    """Types of links in the llms.txt structure."""
    DOCUMENTATION = "documentation"
    EXAMPLE = "example"
    REFERENCE = "reference"
    TUTORIAL = "tutorial"
    API = "api"


class Page(BaseModel):
    """Represents a page entry in the Master Index."""

    id: str = Field(
        ...,
        description="Unique identifier for this page",
        min_length=1,
        max_length=256
    )
    title: str = Field(
        ...,
        description="Human-readable title",
        min_length=1,
        max_length=256
    )
    url: str = Field(
        ...,
        description="URL to the page",
        min_length=1
    )
    summary: str = Field(
        ...,
        description="Brief summary (50-150 words)",
        min_length=10,
        max_length=500
    )
    content_hash: Optional[str] = Field(
        None,
        description="SHA-256 hash for change detection"
    )
    last_verified: Optional[datetime] = Field(
        None,
        description="Last time URL was verified"
    )

    @validator('url')
    def validate_url(cls, v):
        """Validate URL format."""
        if not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError("URL must start with http:// or https://")
        return v

    @validator('id')
    def validate_id(cls, v):
        """Validate ID format."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("ID must be alphanumeric with underscores/hyphens")
        return v

    class Config:
        schema_extra = {
            "example": {
                "id": "page_1",
                "title": "Getting Started",
                "url": "https://example.com/docs/getting-started",
                "summary": "Learn the basics of our platform in under 5 minutes.",
                "last_verified": "2025-01-15T10:30:00Z"
            }
        }


class Concept(BaseModel):
    """Represents a concept in the Concept Map."""

    id: str = Field(
        ...,
        description="Unique concept identifier",
        min_length=1,
        max_length=256
    )
    name: str = Field(
        ...,
        description="Concept name",
        min_length=1,
        max_length=256
    )
    description: str = Field(
        ...,
        description="Detailed concept description",
        min_length=20,
        max_length=2000
    )
    related_pages: List[str] = Field(
        default_factory=list,
        description="List of page IDs related to this concept"
    )
    depends_on: List[str] = Field(
        default_factory=list,
        description="List of prerequisite concept IDs"
    )
    examples: Optional[List[str]] = Field(
        None,
        description="Code or text examples"
    )

    @validator('id')
    def validate_id(cls, v):
        """Validate concept ID."""
        if not v.replace('_', '').isalnum():
            raise ValueError("Concept ID must be alphanumeric with underscores")
        return v

    @validator('description')
    def validate_description_length(cls, v):
        """Ensure description is substantive."""
        word_count = len(v.split())
        if word_count < 5:
            raise ValueError(f"Description too short ({word_count} words), min 5")
        return v

    class Config:
        schema_extra = {
            "example": {
                "id": "authentication",
                "name": "Authentication",
                "description": "Comprehensive guide to user authentication mechanisms...",
                "related_pages": ["page_1", "page_2"],
                "depends_on": ["basic_concepts"]
            }
        }


class FewShot(BaseModel):
    """Represents a few-shot example in the Few-Shot Bank."""

    id: str = Field(
        ...,
        description="Unique example identifier",
        min_length=1
    )
    title: str = Field(
        ...,
        description="Example title",
        min_length=1,
        max_length=256
    )
    source_pages: List[str] = Field(
        ...,
        description="Page IDs this example comes from",
        min_items=1
    )
    prompt: str = Field(
        ...,
        description="Example prompt/question",
        min_length=10,
        max_length=1000
    )
    response: str = Field(
        ...,
        description="Expected response",
        min_length=10
    )
    relevant_concepts: List[str] = Field(
        default_factory=list,
        description="Concept IDs relevant to this example"
    )

    class Config:
        schema_extra = {
            "example": {
                "id": "auth_jwt_example",
                "title": "JWT Authentication Example",
                "source_pages": ["page_auth"],
                "prompt": "How do I authenticate using JWT tokens?",
                "response": "First, generate a token using..."
            }
        }


class MasterIndex(BaseModel):
    """Root structure for llms.txt Master Index."""

    version: str = Field(
        ...,
        description="Schema version (semantic versioning)",
        regex=r'^\d+\.\d+\.\d+$'
    )
    created: datetime = Field(
        ...,
        description="File creation timestamp"
    )
    modified: Optional[datetime] = Field(
        None,
        description="Last modification timestamp"
    )
    pages: List[Page] = Field(
        default_factory=list,
        description="All pages in the repository"
    )

    @validator('pages')
    def validate_page_ids_unique(cls, v):
        """Ensure all page IDs are unique."""
        ids = [p.id for p in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate page IDs found")
        return v

    class Config:
        schema_extra = {
            "example": {
                "version": "1.0.0",
                "created": "2025-01-01T00:00:00Z",
                "pages": []
            }
        }


class ConceptMap(BaseModel):
    """Concept Map section of llms.txt."""

    version: str = Field(..., description="Concept map version")
    concepts: List[Concept] = Field(
        default_factory=list,
        description="All concepts"
    )

    @validator('concepts')
    def validate_concept_ids_unique(cls, v):
        """Ensure all concept IDs are unique."""
        ids = [c.id for c in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate concept IDs found")
        return v

    class Config:
        schema_extra = {"example": {"version": "1.0.0", "concepts": []}}


class FewShotBank(BaseModel):
    """Few-Shot Bank section of llms.txt."""

    version: str = Field(..., description="Few-shot bank version")
    examples: List[FewShot] = Field(
        default_factory=list,
        description="All few-shot examples"
    )

    class Config:
        schema_extra = {"example": {"version": "1.0.0", "examples": []}}


class DocStratumFile(BaseModel):
    """Complete llms.txt file structure (Platinum Standard)."""

    master_index: MasterIndex = Field(..., description="Master Index section")
    concept_map: Optional[ConceptMap] = Field(
        None,
        description="Concept Map section (Level 4)"
    )
    few_shot_bank: Optional[FewShotBank] = Field(
        None,
        description="Few-Shot Bank section (Level 4)"
    )
    llm_instructions: Optional[str] = Field(
        None,
        description="Instructions for LLM consumption (Level 4)"
    )

    class Config:
        title = "DocStratum llms.txt Platinum Standard"
        schema_extra = {
            "description": "Complete llms.txt file conforming to Platinum Standard"
        }
```

## Section 3: Level 1 (STRUCTURE) Validation

### 3.1 Overview

Level 1 validation enforces structural requirements using Pydantic models. This includes:
- Field presence checking (required vs optional)
- Type validation
- Nested model validation
- Custom field validators

### 3.2 Complete Level 1 Implementation

```python
# schema_validation/level_1_structure.py

from typing import List, Dict, Any, Tuple
from pydantic import ValidationError
from schema_validation.models import DocStratumFile, Page, Concept, FewShot
from dataclasses import dataclass


@dataclass
class ValidationIssue:
    """Single validation issue."""
    code: str
    severity: str  # "error" or "warning"
    message: str
    path: str  # Dot notation path to field
    line_number: Optional[int] = None
    suggestion: Optional[str] = None


@dataclass
class StructureValidationResult:
    """Result of Level 1 structure validation."""
    valid: bool
    issues: List[ValidationIssue]
    parsed_data: Optional[DocStratumFile] = None


class Level1StructureValidator:
    """Validates Level 1 (STRUCTURE) requirements."""

    ERROR_CODES = {
        "E004": "MISSING REQUIRED FIELD",
        "E005": "INVALID FIELD TYPE",
        "E006": "INVALID FIELD VALUE",
        "E007": "MODEL VALIDATION ERROR",
        "W001": "OPTIONAL FIELD WITH INVALID VALUE",
    }

    @staticmethod
    def validate(parsed_data: Dict[str, Any]) -> StructureValidationResult:
        """
        Validate Level 1 structure using Pydantic models.

        Args:
            parsed_data: Parsed YAML dictionary from Level 0

        Returns:
            StructureValidationResult with issues and parsed model if valid
        """
        issues = []

        # Attempt to parse using Pydantic
        try:
            docstratum_file = DocStratumFile(**parsed_data)
            return StructureValidationResult(
                valid=True,
                issues=[],
                parsed_data=docstratum_file
            )

        except ValidationError as e:
            # Parse validation errors
            for error in e.errors():
                issue = Level1StructureValidator._convert_pydantic_error(error)
                issues.append(issue)

            return StructureValidationResult(
                valid=False,
                issues=issues,
                parsed_data=None
            )

    @staticmethod
    def _convert_pydantic_error(error: Dict[str, Any]) -> ValidationIssue:
        """Convert Pydantic ValidationError to ValidationIssue."""

        loc = error.get('loc', ())
        path = '.'.join(str(x) for x in loc)
        error_type = error.get('type', 'unknown')
        message = error.get('msg', 'Unknown error')

        # Map error types to error codes
        if error_type == 'value_error.missing':
            code = "E004"
            suggestion = f"Add required field '{loc[-1]}'"
        elif error_type in ['type_error.integer', 'type_error.string']:
            code = "E005"
            suggestion = f"Field '{loc[-1]}' has wrong type. {message}"
        elif 'string_pattern_mismatch' in error_type or 'string_too_short' in error_type:
            code = "E006"
            suggestion = f"Field '{loc[-1]}' has invalid format. {message}"
        else:
            code = "E007"
            suggestion = str(message)

        return ValidationIssue(
            code=code,
            severity="error",
            message=f"{code} | {Level1StructureValidator.ERROR_CODES.get(code, 'VALIDATION')} "
                   f"at {path}: {message}",
            path=path,
            suggestion=suggestion
        )

    @staticmethod
    def validate_pages_required(master_index: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate that at least some pages are defined."""
        issues = []
        pages = master_index.get('pages', [])

        if not pages:
            issues.append(ValidationIssue(
                code="W001",
                severity="warning",
                message="W001 | No pages defined in master_index",
                path="master_index.pages",
                suggestion="Add at least one page to master_index"
            ))

        return issues

    @staticmethod
    def validate_concepts_reference_pages(
        concept_map: Dict[str, Any],
        page_ids: set
    ) -> List[ValidationIssue]:
        """Validate that concepts reference existing pages."""
        issues = []

        if not concept_map:
            return issues

        concepts = concept_map.get('concepts', [])

        for i, concept in enumerate(concepts):
            related_pages = concept.get('related_pages', [])
            for page_id in related_pages:
                if page_id not in page_ids:
                    issues.append(ValidationIssue(
                        code="E006",
                        severity="error",
                        message=f"E006 | Concept '{concept.get('id')}' references "
                               f"non-existent page '{page_id}'",
                        path=f"concept_map.concepts[{i}].related_pages",
                        suggestion=f"Remove '{page_id}' or add it to master_index.pages"
                    ))

        return issues

    @staticmethod
    def validate_few_shot_references(
        few_shot_bank: Dict[str, Any],
        page_ids: set,
        concept_ids: set
    ) -> List[ValidationIssue]:
        """Validate that few-shot examples reference existing pages/concepts."""
        issues = []

        if not few_shot_bank:
            return issues

        examples = few_shot_bank.get('examples', [])

        for i, example in enumerate(examples):
            source_pages = example.get('source_pages', [])
            for page_id in source_pages:
                if page_id not in page_ids:
                    issues.append(ValidationIssue(
                        code="E006",
                        severity="error",
                        message=f"E006 | Example '{example.get('id')}' references "
                               f"non-existent page '{page_id}'",
                        path=f"few_shot_bank.examples[{i}].source_pages",
                        suggestion=f"Add '{page_id}' to master_index.pages"
                    ))

            relevant_concepts = example.get('relevant_concepts', [])
            for concept_id in relevant_concepts:
                if concept_id not in concept_ids:
                    issues.append(ValidationIssue(
                        code="E006",
                        severity="error",
                        message=f"E006 | Example '{example.get('id')}' references "
                               f"non-existent concept '{concept_id}'",
                        path=f"few_shot_bank.examples[{i}].relevant_concepts",
                        suggestion=f"Add '{concept_id}' to concept_map.concepts"
                    ))

        return issues
```

### 3.3 Test Cases for Level 1

```python
# tests/test_level_1_structure.py

import pytest
from datetime import datetime
from schema_validation.level_1_structure import Level1StructureValidator


class TestLevel1Structure:
    """Test Level 1 structure validation."""

    def test_valid_minimal_structure(self):
        """Level 1: Minimal valid structure should pass."""
        data = {
            "master_index": {
                "version": "1.0.0",
                "created": datetime.now(),
                "pages": []
            }
        }

        result = Level1StructureValidator.validate(data)

        assert result.valid
        assert len(result.issues) == 0
        assert result.parsed_data is not None

    def test_missing_required_master_index(self):
        """Level 1: Missing master_index should fail."""
        data = {}

        result = Level1StructureValidator.validate(data)

        assert not result.valid
        assert any(issue.code == "E004" for issue in result.issues)

    def test_missing_required_version(self):
        """Level 1: Missing version in master_index should fail."""
        data = {
            "master_index": {
                "created": datetime.now(),
                "pages": []
            }
        }

        result = Level1StructureValidator.validate(data)

        assert not result.valid
        assert any("version" in issue.path for issue in result.issues)

    def test_invalid_version_format(self):
        """Level 1: Invalid version format should fail."""
        data = {
            "master_index": {
                "version": "1.0",  # Should be X.Y.Z
                "created": datetime.now(),
                "pages": []
            }
        }

        result = Level1StructureValidator.validate(data)

        assert not result.valid

    def test_valid_with_pages(self):
        """Level 1: Valid structure with pages should pass."""
        data = {
            "master_index": {
                "version": "1.0.0",
                "created": datetime.now(),
                "pages": [
                    {
                        "id": "page_1",
                        "title": "Getting Started",
                        "url": "https://example.com",
                        "summary": "This is a comprehensive guide to getting started."
                    }
                ]
            }
        }

        result = Level1StructureValidator.validate(data)

        assert result.valid

    def test_invalid_page_missing_summary(self):
        """Level 1: Page missing summary should fail."""
        data = {
            "master_index": {
                "version": "1.0.0",
                "created": datetime.now(),
                "pages": [
                    {
                        "id": "page_1",
                        "title": "Test",
                        "url": "https://example.com"
                        # Missing summary
                    }
                ]
            }
        }

        result = Level1StructureValidator.validate(data)

        assert not result.valid

    def test_duplicate_page_ids(self):
        """Level 1: Duplicate page IDs should fail."""
        data = {
            "master_index": {
                "version": "1.0.0",
                "created": datetime.now(),
                "pages": [
                    {
                        "id": "page_1",
                        "title": "Test 1",
                        "url": "https://example.com/1",
                        "summary": "A comprehensive guide."
                    },
                    {
                        "id": "page_1",
                        "title": "Test 2",
                        "url": "https://example.com/2",
                        "summary": "Another comprehensive guide."
                    }
                ]
            }
        }

        result = Level1StructureValidator.validate(data)

        assert not result.valid
```

## Section 4: Error Code Registry Integration

### 4.1 Error Codes Mapping

The validation engine integrates with the error code registry from v0.0.1a:

| Code | Severity | Description | Recovery |
|------|----------|-------------|----------|
| E001 | ERROR | File encoding error or not readable | Save as UTF-8 without BOM |
| E002 | ERROR | Root must be object/dict, not list | Fix YAML root structure |
| E003 | ERROR | YAML syntax error | Check indentation and colons |
| E004 | ERROR | Required field missing | Add required field |
| E005 | ERROR | Field type mismatch | Fix field type/format |
| E006 | ERROR | Invalid field value | Fix field value per spec |
| E007 | ERROR | Pydantic validation failure | Fix validation error |
| W001 | WARNING | No pages in master_index | Add at least one page |

## Section 5: Error Message Design

### 5.1 Error Message Format

All error messages follow this format:

```
{CODE} | {CATEGORY}: {MESSAGE}. {LOCATION}. {SUGGESTION}
```

**Example:**
```
E004 | MISSING FIELD: Required field 'summary' is missing.
      At master_index.pages[0].
      Fix: Add summary field with 50-150 word description.
```

### 5.2 Error Message Examples

```python
# Missing required field
"E004 | MISSING FIELD: Required field 'title' at master_index.pages[0]. "
"Fix: Add 'title: Your Page Title' to the page entry."

# Type mismatch
"E005 | TYPE MISMATCH: Field 'created' should be datetime, got string. "
"At master_index.created. Fix: Use ISO format: 2025-01-15T10:30:00Z"

# Invalid reference
"E006 | INVALID REFERENCE: Page 'page_999' referenced by concept "
"'auth_concept' does not exist. At concept_map.concepts[0].related_pages. "
"Fix: Change page_999 to existing page ID or add the page to master_index."

# YAML syntax
"E003 | YAML PARSE ERROR: expected '<scalar>', but found '-'. "
"Line 12. Fix: Check indentation (use 2 spaces consistently)."
```

## Section 6: Complete Integration Test

```python
# tests/test_integration_levels_0_1.py

import pytest
import tempfile
from pathlib import Path
from schema_validation.level_0_syntax import YAMLParser
from schema_validation.level_1_structure import Level1StructureValidator


class TestIntegrationLevel0And1:
    """Integration tests for Levels 0 and 1."""

    @pytest.fixture
    def valid_llms_txt(self):
        """Create valid llms.txt content."""
        return """
master_index:
  version: 1.0.0
  created: 2025-01-15T10:30:00Z
  pages:
    - id: page_getting_started
      title: Getting Started
      url: https://example.com/docs
      summary: Learn the basics of our platform in under 5 minutes.
    - id: page_api_reference
      title: API Reference
      url: https://api.example.com/docs
      summary: Complete API documentation with examples and endpoint reference.

concept_map:
  version: 1.0.0
  concepts:
    - id: authentication
      name: Authentication
      description: >
        Learn how authentication works in our system, including JWT tokens,
        OAuth flows, and session management.
      related_pages: [page_getting_started]

few_shot_bank:
  version: 1.0.0
  examples:
    - id: auth_jwt
      title: JWT Authentication
      source_pages: [page_api_reference]
      prompt: How do I authenticate with JWT?
      response: Send your token in the Authorization header.
      relevant_concepts: [authentication]
"""

    def test_full_validation_pipeline_valid(self, valid_llms_txt):
        """Test complete validation of valid file."""
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.yml', delete=False
        ) as f:
            f.write(valid_llms_txt)
            path = Path(f.name)

        try:
            # Level 0: Parse YAML
            parse_result = YAMLParser.parse(path)
            assert parse_result.success

            # Level 1: Validate structure
            validation_result = Level1StructureValidator.validate(
                parse_result.data
            )
            assert validation_result.valid
            assert len(validation_result.issues) == 0

        finally:
            path.unlink()

    def test_full_validation_pipeline_invalid(self):
        """Test complete validation of invalid file."""
        invalid_content = """
master_index:
  version: 1.0  # Wrong format
  created: 2025-01-15
  pages:
"""
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.yml', delete=False
        ) as f:
            f.write(invalid_content)
            path = Path(f.name)

        try:
            # Level 0: Parse YAML
            parse_result = YAMLParser.parse(path)
            assert parse_result.success  # YAML is valid

            # Level 1: Validate structure
            validation_result = Level1StructureValidator.validate(
                parse_result.data
            )
            assert not validation_result.valid
            assert any(issue.code == "E006" for issue in validation_result.issues)

        finally:
            path.unlink()
```

## Deliverables Checklist

- [x] YAML Parser with encoding detection (Level 0: SYNTAX)
- [x] Pydantic model definitions for all llms.txt structures
- [x] Level 1 (STRUCTURE) validator with field presence and type checking
- [x] Error code registry (E001-E007, W001) integrated
- [x] Error message generator with line numbers and suggestions
- [x] 10+ comprehensive pytest test cases
- [x] Custom validators for domain-specific rules (ID format, description length)
- [x] JSON schema generation support (via Pydantic Config)
- [x] Integration tests for Levels 0 and 1

## Acceptance Criteria

1. **YAML Parsing**: All valid YAML parses without error; invalid YAML reports precise line numbers
2. **Encoding Detection**: UTF-8 (with/without BOM), UTF-16, and CP1252 handled gracefully
3. **Pydantic Validation**: All Pydantic validation errors convert to clear error messages
4. **Error Messages**: Every error includes code, location, and actionable fix suggestion
5. **Test Coverage**: All 10+ test cases pass; coverage of valid/invalid inputs for each level
6. **Error Codes**: E001-E007 and W001 correctly applied; no unmapped errors
7. **Integration**: Level 0 output feeds seamlessly into Level 1 validator
8. **Performance**: Validation < 500ms for typical 50-page llms.txt file

## Next Steps

1. **→ v0.2.4b**: Content & Link Validation Engine (Level 2)
   - Build URL validation pipeline with concurrent checking
   - Implement cross-reference validation (concepts reference pages, etc.)
   - Create link health report format

2. **→ v0.2.4c**: Quality Scoring Engine (Level 3)
   - Implement scoring rubrics for completeness, informativeness, etc.
   - Create quality trend tracking
   - Generate quality reports with improvement suggestions

3. **→ v0.2.4d**: Pipeline Orchestration & Reporting
   - Integrate all validation levels into single CLI
   - Create output formats (terminal, JSON, Markdown, HTML)
   - Add CI/CD integration (GitHub Actions, pre-commit hooks)
