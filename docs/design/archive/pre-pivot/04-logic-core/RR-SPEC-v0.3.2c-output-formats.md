# v0.3.2c — Output Formats & Processing Modes

> **Phase**: v0.3.2 "Context Builder" | **Component**: Output Format Handling
>
> **Stability**: DRAFT | **Target Release**: v0.3.2-alpha

## Objective

Implement multiple output format engines that transform rendered context sections into different formats (markdown, XML, JSON, plain text) optimized for various downstream systems. The system supports the 4 processing modes from v0.0.1c (concatenation, XML wrapping, JSON output, plain text), the DocStratum Hybrid mode combining selective inclusion with concept injection and token budgeting, format-specific rendering rules, output validation, and comprehensive test coverage.

## Scope

This specification covers:
- **Format Engines**: Dedicated processors for markdown, XML, JSON, and plain text formats
- **Format-Specific Rules**: Markdown headings/lists, XML tags, JSON structure, plain text simplification
- **Processing Modes**: Standard markdown, XML-wrapped for RAG, JSON for programmatic, plain text for embedding
- **DocStratum Hybrid Mode**: Combines selective inclusion + concept injection + token budgeting + format selection
- **Format Selection Interface**: `output_format` parameter with validation
- **Post-Processing**: Whitespace normalization, line ending consistency, metadata injection
- **Format Validation**: Well-formed markdown/XML/JSON verification
- **Complete Implementation**: FormatEngine orchestrator with all 4 formats
- **Test Suite**: Comprehensive test coverage of all formats and modes

## Dependencies

- **v0.3.2b Section Renderers**: Provides rendered markdown sections
- **v0.3.2a Token Budget**: Provides token accounting and budget metadata
- **Python 3.9+**: Type hints, dataclasses, standard library
- **xml.etree.ElementTree** (stdlib): For XML generation and validation
- **json** (stdlib): For JSON output
- **markdown** (optional): For markdown validation

## Content Sections

### 1. Processing Modes Overview

#### Mode 1: Markdown Output (Default)

Standard markdown output optimized for LLM system prompts. Clean, human-readable, heading-based structure.

```python
"""
Markdown Output Example:

# Project Documentation

> This context contains curated project information.

## Concepts

### Core Concept 1
  Definition of core concept...

### Core Concept 2
  Definition of core concept 2...

## Pages

### Main Documentation
- [Page Title](url)
  Brief description
  Tags: `tag1`, `tag2`

## Examples

### Q&A Examples
**Q: What is the best practice for X?**

**A:** The best practice is...

```python
code_example()
```

## Response Guidelines

When responding, prioritize information from the included sections:
- concepts: Key definitions and anti-patterns
- pages: Index of relevant documentation
- examples: Q&A demonstrations
"""
```

**Use Cases**: LLM system prompts, prompt engineering, documentation
**Characteristics**: Human-readable, hierarchical, no special escaping
**Validation**: Proper heading nesting, list formatting

#### Mode 2: XML-Wrapped Output

XML-wrapped format for RAG systems and programmatic consumption. Structured with metadata attributes.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<llms_context>
  <metadata>
    <generated>2024-01-15T10:30:00Z</generated>
    <version>0.3.2</version>
    <token_count>12450</token_count>
    <model>gpt-4</model>
  </metadata>

  <section name="header">
    <title>Project Documentation</title>
    <description>Core project information</description>
  </section>

  <section name="concepts">
    <concept id="concept_1">
      <term>Core Concept 1</term>
      <definition>Definition text...</definition>
      <dependencies>
        <dependency>related_concept</dependency>
      </dependencies>
      <anti_patterns>
        <pattern>Common mistake 1</pattern>
      </anti_patterns>
    </concept>
  </section>

  <section name="pages">
    <page id="page_1" type="main">
      <title>Page Title</title>
      <url>https://example.com</url>
      <summary>Page summary...</summary>
      <tags>
        <tag>tag1</tag>
      </tags>
    </page>
  </section>

  <section name="examples">
    <example id="example_1" core="true">
      <question>What is best practice for X?</question>
      <answer>Answer text...</answer>
      <code language="python">code...</code>
      <source>page_1</source>
    </example>
  </section>
</llms_context>
```

**Use Cases**: RAG pipelines, semantic search, XML-based processing
**Characteristics**: Structured, queryable, metadata-rich, precise escaping
**Validation**: Well-formed XML, proper nesting, attribute validity

#### Mode 3: JSON Output

JSON-structured format for programmatic consumption and API responses.

```json
{
  "metadata": {
    "generated": "2024-01-15T10:30:00Z",
    "version": "0.3.2",
    "token_count": 12450,
    "model": "gpt-4",
    "included_sections": ["header", "concepts", "pages", "examples", "footer"],
    "excluded_sections": []
  },
  "sections": {
    "header": {
      "title": "Project Documentation",
      "description": "Core project information",
      "model_info": "gpt-4",
      "version": "0.3.2"
    },
    "concepts": [
      {
        "id": "concept_1",
        "term": "Core Concept 1",
        "definition": "Definition text...",
        "dependencies": ["related_concept"],
        "anti_patterns": ["Common mistake 1"],
        "core": true,
        "depth": 0
      }
    ],
    "pages": [
      {
        "id": "page_1",
        "title": "Page Title",
        "url": "https://example.com",
        "summary": "Page summary...",
        "content_type": "main",
        "tags": ["tag1"],
        "relevance_score": 0.95
      }
    ],
    "examples": [
      {
        "id": "example_1",
        "question": "What is best practice for X?",
        "answer": "Answer text...",
        "code": "code...",
        "code_language": "python",
        "source": "page_1",
        "core": true
      }
    ],
    "footer": {
      "included_sections": ["header", "concepts", "pages", "examples", "footer"],
      "excluded_sections": []
    }
  }
}
```

**Use Cases**: APIs, web dashboards, programmatic processing
**Characteristics**: Structured, queryable, metadata-rich, strict validation
**Validation**: Valid JSON, required fields present, type correctness

#### Mode 4: Plain Text Output

Simplified plain text format for embeddings and basic consumption. No markdown, minimal formatting.

```
PROJECT DOCUMENTATION

Core project information.

CONCEPTS

Core Concept 1
Definition text...
Related: related_concept
Avoid: Common mistake 1

Core Concept 2
Definition text 2...

PAGES

Main Documentation
Page Title (https://example.com)
Page summary...
Tags: tag1, tag2

EXAMPLES

Q: What is best practice for X?
A: Answer text...

Code:
code...

RESPONSE GUIDELINES

When responding, prioritize information from the included sections:
- concepts: Key definitions and anti-patterns
- pages: Index of relevant documentation
- examples: Q&A demonstrations
```

**Use Cases**: Embeddings, simple text search, accessibility
**Characteristics**: No formatting, whitespace-based structure, easy to parse
**Validation**: Readability, no invalid characters, clean whitespace

### 2. Format Engine Architecture

#### FormatProcessor Base Class

Unified interface for all format processors.

```python
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Any
import json
import xml.etree.ElementTree as ET

class OutputFormat(Enum):
    """Available output formats."""
    MARKDOWN = "markdown"
    XML = "xml"
    JSON = "json"
    TEXT = "text"


@dataclass
class FormatOptions:
    """Options for format processing."""
    pretty_print: bool = True
    """Pretty-print output (indentation, spacing)."""

    include_metadata: bool = True
    """Include metadata in output."""

    normalize_whitespace: bool = True
    """Normalize whitespace (remove excess)."""

    validate: bool = True
    """Validate output format."""

    encoding: str = "utf-8"
    """Output encoding."""

    custom_options: dict[str, Any] = None
    """Format-specific custom options."""

    def __post_init__(self):
        if self.custom_options is None:
            self.custom_options = {}


@dataclass
class FormatMetadata:
    """Metadata to include in output."""
    generated: str
    """ISO timestamp of generation."""

    version: str = "0.3.2"
    """llms.txt version."""

    token_count: int = 0
    """Total tokens in output."""

    model: str = "unknown"
    """Target model."""

    included_sections: list[str] = None
    """Sections included in context."""

    excluded_sections: list[str] = None
    """Sections excluded from context."""

    def __post_init__(self):
        if self.included_sections is None:
            self.included_sections = []
        if self.excluded_sections is None:
            self.excluded_sections = []


class FormatProcessor(ABC):
    """Abstract base for format processors."""

    def __init__(self, options: Optional[FormatOptions] = None):
        """
        Initialize processor.

        Args:
            options: Format options
        """
        self.options = options or FormatOptions()

    @abstractmethod
    def process(self, content: str, metadata: Optional[FormatMetadata] = None) -> str:
        """
        Process content to target format.

        Args:
            content: Input content (typically markdown)
            metadata: Optional metadata to include

        Returns:
            Formatted output
        """
        pass

    @abstractmethod
    def validate(self, output: str) -> tuple[bool, list[str]]:
        """
        Validate output format.

        Args:
            output: Output to validate

        Returns:
            (is_valid, error_messages)
        """
        pass

    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace."""
        if not self.options.normalize_whitespace:
            return text

        # Remove trailing whitespace
        lines = [line.rstrip() for line in text.split("\n")]

        # Remove multiple blank lines (keep max 2)
        result = []
        blank_count = 0
        for line in lines:
            if line == "":
                blank_count += 1
                if blank_count <= 2:
                    result.append(line)
            else:
                blank_count = 0
                result.append(line)

        return "\n".join(result)

    def _normalize_line_endings(self, text: str) -> str:
        """Normalize line endings to LF."""
        return text.replace("\r\n", "\n").replace("\r", "\n")
```

### 3. Markdown Format Processor

#### MarkdownProcessor Implementation

Processes content as markdown with optional post-processing.

```python
class MarkdownProcessor(FormatProcessor):
    """Processes content as markdown format."""

    def process(self, content: str, metadata: Optional[FormatMetadata] = None) -> str:
        """
        Process to markdown.

        Args:
            content: Input content (typically already markdown)
            metadata: Optional metadata to prepend

        Returns:
            Markdown-formatted output
        """
        output_lines = []

        # Metadata comment (optional)
        if metadata and self.options.include_metadata:
            output_lines.append(self._format_metadata_comment(metadata))
            output_lines.append("")

        # Main content
        output_lines.append(content)

        output = "\n".join(output_lines)

        # Post-processing
        if self.options.normalize_whitespace:
            output = self._normalize_whitespace(output)

        output = self._normalize_line_endings(output)

        return output

    def validate(self, output: str) -> tuple[bool, list[str]]:
        """
        Validate markdown format.

        Args:
            output: Markdown to validate

        Returns:
            (is_valid, error_messages)
        """
        errors = []

        # Check for balanced code fences
        fence_count = output.count("```")
        if fence_count % 2 != 0:
            errors.append("Unbalanced code fences (```)")

        # Check for balanced brackets
        bracket_pairs = [
            ("[", "]"),
            ("(", ")"),
            ("{", "}")
        ]

        for open_br, close_br in bracket_pairs:
            if output.count(open_br) != output.count(close_br):
                errors.append(
                    f"Unbalanced brackets: {open_br}/{close_br}"
                )

        return len(errors) == 0, errors

    def _format_metadata_comment(self, metadata: FormatMetadata) -> str:
        """Format metadata as markdown comment."""
        lines = [
            "<!-- llms.txt Context Block -->",
            f"<!-- Generated: {metadata.generated} -->",
            f"<!-- Version: {metadata.version} -->",
            f"<!-- Tokens: {metadata.token_count} -->",
            f"<!-- Model: {metadata.model} -->",
            "<!-- -->",
        ]
        return "\n".join(lines)
```

### 4. XML Format Processor

#### XMLProcessor Implementation

Processes content as XML with structured tags.

```python
class XMLProcessor(FormatProcessor):
    """Processes content as XML format."""

    def process(self, content: str, metadata: Optional[FormatMetadata] = None) -> str:
        """
        Process to XML.

        Args:
            content: Input content (markdown to parse)
            metadata: Optional metadata

        Returns:
            XML-formatted output
        """
        # Create root element
        root = ET.Element("llms_context")
        root.set("version", "0.3.2")

        # Add metadata
        if metadata:
            metadata_elem = ET.SubElement(root, "metadata")
            self._add_metadata_xml(metadata_elem, metadata)

        # Parse markdown into sections and add to XML
        # This is a simplified implementation
        sections = self._parse_sections(content)
        for section_name, section_content in sections.items():
            self._add_section_xml(root, section_name, section_content)

        # Generate XML string
        xml_str = ET.tostring(root, encoding="unicode")

        # Pretty-print if requested
        if self.options.pretty_print:
            xml_str = self._pretty_print_xml(xml_str)

        # Normalize line endings
        xml_str = self._normalize_line_endings(xml_str)

        return xml_str

    def validate(self, output: str) -> tuple[bool, list[str]]:
        """
        Validate XML format.

        Args:
            output: XML to validate

        Returns:
            (is_valid, error_messages)
        """
        errors = []

        try:
            ET.fromstring(output)
        except ET.ParseError as e:
            errors.append(f"XML parse error: {str(e)}")

        return len(errors) == 0, errors

    def _add_metadata_xml(
        self,
        parent: ET.Element,
        metadata: FormatMetadata
    ) -> None:
        """Add metadata to XML element."""
        ET.SubElement(parent, "generated").text = metadata.generated
        ET.SubElement(parent, "version").text = metadata.version
        ET.SubElement(parent, "token_count").text = str(metadata.token_count)
        ET.SubElement(parent, "model").text = metadata.model

        sections = ET.SubElement(parent, "included_sections")
        for section in metadata.included_sections:
            ET.SubElement(sections, "section").text = section

        if metadata.excluded_sections:
            excluded = ET.SubElement(parent, "excluded_sections")
            for section in metadata.excluded_sections:
                ET.SubElement(excluded, "section").text = section

    def _parse_sections(self, content: str) -> dict[str, str]:
        """
        Parse markdown into sections.

        Simple implementation: split by H2 headers.

        Args:
            content: Markdown content

        Returns:
            {section_name: section_content}
        """
        sections = {}
        current_section = "header"
        current_content = []

        for line in content.split("\n"):
            if line.startswith("## "):
                # New section
                if current_section:
                    sections[current_section] = "\n".join(current_content)
                current_section = line[3:].lower().strip()
                current_content = []
            else:
                current_content.append(line)

        if current_section:
            sections[current_section] = "\n".join(current_content)

        return sections

    def _add_section_xml(
        self,
        parent: ET.Element,
        section_name: str,
        content: str
    ) -> None:
        """Add section to XML."""
        section = ET.SubElement(parent, "section")
        section.set("name", section_name)
        section.text = content.strip()

    def _pretty_print_xml(self, xml_str: str, indent: str = "  ") -> str:
        """Pretty-print XML."""
        try:
            import xml.dom.minidom as minidom
            dom = minidom.parseString(xml_str)
            return dom.toprettyxml(indent=indent)
        except Exception:
            return xml_str
```

### 5. JSON Format Processor

#### JSONProcessor Implementation

Processes content as structured JSON.

```python
class JSONProcessor(FormatProcessor):
    """Processes content as JSON format."""

    def process(self, content: str, metadata: Optional[FormatMetadata] = None) -> str:
        """
        Process to JSON.

        Args:
            content: Input content (markdown to parse)
            metadata: Optional metadata

        Returns:
            JSON-formatted output
        """
        output = {}

        # Add metadata
        if metadata:
            output["metadata"] = self._metadata_to_dict(metadata)

        # Parse sections
        sections = self._parse_sections(content)
        output["sections"] = sections

        # Serialize to JSON
        if self.options.pretty_print:
            json_str = json.dumps(output, indent=2, ensure_ascii=False)
        else:
            json_str = json.dumps(output, ensure_ascii=False)

        # Normalize line endings
        json_str = self._normalize_line_endings(json_str)

        return json_str

    def validate(self, output: str) -> tuple[bool, list[str]]:
        """
        Validate JSON format.

        Args:
            output: JSON to validate

        Returns:
            (is_valid, error_messages)
        """
        errors = []

        try:
            json.loads(output)
        except json.JSONDecodeError as e:
            errors.append(f"JSON parse error: {str(e)}")

        return len(errors) == 0, errors

    def _metadata_to_dict(self, metadata: FormatMetadata) -> dict:
        """Convert metadata to dictionary."""
        return {
            "generated": metadata.generated,
            "version": metadata.version,
            "token_count": metadata.token_count,
            "model": metadata.model,
            "included_sections": metadata.included_sections,
            "excluded_sections": metadata.excluded_sections
        }

    def _parse_sections(self, content: str) -> dict[str, Any]:
        """Parse markdown sections to structured JSON."""
        sections = {}
        current_section = None
        current_content = []

        for line in content.split("\n"):
            if line.startswith("## "):
                # New section
                if current_section:
                    sections[current_section] = {
                        "content": "\n".join(current_content).strip()
                    }
                current_section = line[3:].lower().strip()
                current_content = []
            else:
                current_content.append(line)

        if current_section:
            sections[current_section] = {
                "content": "\n".join(current_content).strip()
            }

        return sections
```

### 6. Plain Text Format Processor

#### TextProcessor Implementation

Processes content as plain text.

```python
class TextProcessor(FormatProcessor):
    """Processes content as plain text format."""

    def process(self, content: str, metadata: Optional[FormatMetadata] = None) -> str:
        """
        Process to plain text.

        Args:
            content: Input content (markdown to convert)
            metadata: Optional metadata (not included in plain text)

        Returns:
            Plain text output
        """
        # Remove markdown formatting
        text = self._remove_markdown(content)

        # Post-processing
        if self.options.normalize_whitespace:
            text = self._normalize_whitespace(text)

        text = self._normalize_line_endings(text)

        return text

    def validate(self, output: str) -> tuple[bool, list[str]]:
        """
        Validate plain text format.

        Args:
            output: Text to validate

        Returns:
            (is_valid, error_messages)
        """
        errors = []

        # Check for common issues
        if "\x00" in output:
            errors.append("Contains null bytes")

        return len(errors) == 0, errors

    def _remove_markdown(self, text: str) -> str:
        """Remove markdown formatting."""
        import re

        # Remove HTML comments
        text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)

        # Remove headings but keep text
        text = re.sub(r"^#+\s+(.+)$", r"\1", text, flags=re.MULTILINE)

        # Remove bold/italic but keep text
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
        text = re.sub(r"\*(.+?)\*", r"\1", text)
        text = re.sub(r"__(.+?)__", r"\1", text)
        text = re.sub(r"_(.+?)_", r"\1", text)

        # Remove links but keep text
        text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)

        # Remove code blocks but keep content
        text = re.sub(r"```(.+?)```", r"\1", text, flags=re.DOTALL)
        text = re.sub(r"`(.+?)`", r"\1", text)

        # Remove blockquotes but keep text
        text = re.sub(r"^>\s+(.+)$", r"\1", text, flags=re.MULTILINE)

        # Remove lists but keep text
        text = re.sub(r"^[\s]*[-*+]\s+(.+)$", r"\1", text, flags=re.MULTILINE)
        text = re.sub(r"^[\s]*\d+\.\s+(.+)$", r"\1", text, flags=re.MULTILINE)

        # Remove horizontal rules
        text = re.sub(r"^---+$", "", text, flags=re.MULTILINE)

        return text
```

### 7. FormatEngine Orchestrator

#### FormatEngine Implementation

Coordinates format processing.

```python
class FormatEngine:
    """Orchestrates format processing."""

    def __init__(self, format_type: OutputFormat, options: Optional[FormatOptions] = None):
        """
        Initialize engine.

        Args:
            format_type: Output format
            options: Format options
        """
        self.format_type = format_type
        self.options = options or FormatOptions()

        # Select processor
        if format_type == OutputFormat.MARKDOWN:
            self.processor = MarkdownProcessor(self.options)
        elif format_type == OutputFormat.XML:
            self.processor = XMLProcessor(self.options)
        elif format_type == OutputFormat.JSON:
            self.processor = JSONProcessor(self.options)
        elif format_type == OutputFormat.TEXT:
            self.processor = TextProcessor(self.options)
        else:
            raise ValueError(f"Unknown format: {format_type}")

    def process(
        self,
        content: str,
        metadata: Optional[FormatMetadata] = None
    ) -> str:
        """
        Process content to target format.

        Args:
            content: Input content
            metadata: Optional metadata

        Returns:
            Formatted output
        """
        output = self.processor.process(content, metadata)

        # Validate
        if self.options.validate:
            is_valid, errors = self.processor.validate(output)
            if not is_valid:
                raise ValueError(
                    f"Format validation failed: {', '.join(errors)}"
                )

        return output

    def validate_output(self, output: str) -> tuple[bool, list[str]]:
        """Validate formatted output."""
        return self.processor.validate(output)
```

### 8. DocStratum Hybrid Mode

#### HybridProcessor Implementation

Combines multiple processing techniques.

```python
@dataclass
class HybridConfig:
    """Configuration for DocStratum Hybrid mode."""
    enable_selective_inclusion: bool = True
    """Include only highest-priority items."""

    enable_concept_injection: bool = True
    """Inject concept definitions into relevant sections."""

    enable_token_budgeting: bool = True
    """Apply token budget constraints."""

    enable_format_optimization: bool = True
    """Optimize content for target format."""

    target_format: OutputFormat = OutputFormat.MARKDOWN
    """Target output format."""

    max_tokens: int = 16000
    """Maximum tokens for output."""

    priority_threshold: float = 0.5
    """Minimum priority score for inclusion."""


class HybridProcessor:
    """
    DocStratum Hybrid mode: combines selective inclusion, concept injection,
    token budgeting, and format optimization.
    """

    def __init__(self, config: HybridConfig):
        """Initialize hybrid processor."""
        self.config = config
        self.format_engine = FormatEngine(
            config.target_format,
            FormatOptions(include_metadata=True)
        )

    def process(
        self,
        content_items: dict[str, list],
        metadata: FormatMetadata
    ) -> str:
        """
        Process content using hybrid approach.

        Args:
            content_items: {section: [items]} with priority scores
            metadata: Generation metadata

        Returns:
            Formatted output
        """
        processed_items = content_items.copy()

        # Step 1: Selective inclusion (priority filtering)
        if self.config.enable_selective_inclusion:
            processed_items = self._apply_selective_inclusion(processed_items)

        # Step 2: Concept injection (enhance context)
        if self.config.enable_concept_injection:
            processed_items = self._inject_concepts(processed_items)

        # Step 3: Token budgeting (fit within budget)
        if self.config.enable_token_budgeting:
            processed_items = self._apply_token_budget(processed_items)

        # Step 4: Format optimization (format-specific tweaks)
        if self.config.enable_format_optimization:
            processed_items = self._optimize_for_format(processed_items)

        # Render to markdown (intermediate format)
        markdown_content = self._render_sections(processed_items)

        # Step 5: Convert to target format
        output = self.format_engine.process(markdown_content, metadata)

        return output

    def _apply_selective_inclusion(self, items: dict[str, list]) -> dict[str, list]:
        """Apply priority-based filtering."""
        filtered = {}
        for section, items_list in items.items():
            filtered[section] = [
                item for item in items_list
                if getattr(item, "priority", 1.0) >= self.config.priority_threshold
            ]
        return filtered

    def _inject_concepts(self, items: dict[str, list]) -> dict[str, list]:
        """Inject concept definitions where relevant."""
        # Placeholder: concept injection logic
        # In full implementation, would identify concept references
        # and ensure definitions are included
        return items

    def _apply_token_budget(self, items: dict[str, list]) -> dict[str, list]:
        """Apply token budget constraints."""
        # Placeholder: token budgeting logic
        # In full implementation, would use BudgetEngine from v0.3.2a
        return items

    def _optimize_for_format(self, items: dict[str, list]) -> dict[str, list]:
        """Optimize content for target format."""
        if self.config.target_format == OutputFormat.JSON:
            # Ensure all items have serializable fields
            pass
        elif self.config.target_format == OutputFormat.XML:
            # Escape special characters
            pass
        elif self.config.target_format == OutputFormat.TEXT:
            # Simplify content for plain text
            pass
        return items

    def _render_sections(self, items: dict[str, list]) -> str:
        """Render processed items to markdown."""
        # Placeholder: use RendererCoordinator from v0.3.2b
        return ""
```

## Deliverables

1. **OutputFormat enum**: Available format types
2. **FormatOptions dataclass**: Configuration for format processing
3. **FormatMetadata dataclass**: Metadata to include in output
4. **FormatProcessor abstract base**: Unified processor interface
5. **MarkdownProcessor class**: Markdown format processing
6. **XMLProcessor class**: XML format processing with validation
7. **JSONProcessor class**: JSON format processing with validation
8. **TextProcessor class**: Plain text format processing
9. **FormatEngine orchestrator**: Coordinates format selection and processing
10. **HybridProcessor class**: Implements DocStratum Hybrid mode
11. **Complete test suite**: All 4 formats + hybrid mode with various scenarios

## Acceptance Criteria

- OutputFormat enum provides all 4 format options (markdown, xml, json, text)
- FormatOptions enables configuration of pretty-printing, metadata, whitespace, validation
- All format processors implement consistent FormatProcessor interface
- Markdown processor outputs clean, heading-based markdown
- XML processor generates well-formed, queryable XML with metadata
- JSON processor produces valid JSON with structured sections
- Text processor removes markdown formatting while preserving content
- Format validation detects issues (unbalanced brackets, invalid XML/JSON, etc.)
- DocStratum Hybrid mode combines selective inclusion + concept injection + token budgeting
- HybridProcessor processes content through all optimization steps
- FormatEngine successfully converts content between all formats
- Test suite covers all 4 formats, edge cases, invalid inputs, and hybrid mode scenarios
- Output is well-formed and valid for each format type

## Next Step

Proceed to **v0.3.2d — Integration API & Configuration**, which provides the public `build_context_block()` function, ContextConfig dataclass, builder pattern for fluent API, and integration with Loader (v0.3.1) and Agent modules (v0.3.3/v0.3.4).
