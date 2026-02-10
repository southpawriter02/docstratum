# v0.3.2b — Section Renderers & Markdown Generation

> **Phase**: v0.3.2 "Context Builder" | **Component**: Section Rendering
>
> **Stability**: DRAFT | **Target Release**: v0.3.2-alpha

## Objective

Implement a modular renderer architecture that transforms selected content into properly formatted markdown sections. The system provides dedicated renderer classes for each section type (header, concepts, pages, examples, footer), with consistent markdown generation rules, flexible templating, and comprehensive test coverage. Renderers handle concept dependencies, page type grouping, Q&A formatting, and dynamic instruction generation.

## Scope

This specification covers:
- **Renderer Architecture**: One renderer per section with consistent interface
- **Markdown Generation Rules**: Heading levels, list formatting, code blocks, links
- **Concept Rendering**: Definition format, dependency display, anti-pattern callouts
- **Page Rendering**: Content-type grouping, sort order, summaries, verification dates
- **Example Rendering**: Q&A format, visual separation, code preservation, citations
- **Footer Rendering**: Response guidelines, dynamic instructions based on content
- **Template System**: Jinja2/f-string templates for customization and consistency
- **Complete Implementation**: All 5 renderer classes with unified interface
- **Test Suite**: Comprehensive test coverage of all rendering scenarios

## Dependencies

- **v0.3.1 Loader Module**: Provides page/concept/example objects with metadata
- **v0.3.2a Token Budget**: Provides selected, budgeted content items
- **Python 3.9+**: Type hints, dataclasses, standard library
- **Jinja2** (optional): For advanced template customization
- **Markdown**: For validation (optional)

## Content Sections

### 1. Renderer Architecture

#### Base Renderer Interface

All renderers implement a consistent interface for unified context building.

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Any

@dataclass
class RenderContext:
    """Context information for rendering."""
    max_width: int = 80
    """Maximum line width for wrapped content."""

    include_metadata: bool = False
    """Include metadata (dates, sources, etc.)."""

    include_links: bool = True
    """Include URL/link references."""

    compact_mode: bool = False
    """Compact rendering (minimal whitespace)."""

    custom_variables: dict[str, Any] = None
    """Custom template variables."""

    def __post_init__(self):
        if self.custom_variables is None:
            self.custom_variables = {}


class SectionRenderer(ABC):
    """Abstract base for section renderers."""

    def __init__(self, context: Optional[RenderContext] = None):
        """
        Initialize renderer.

        Args:
            context: Rendering context (uses defaults if None)
        """
        self.context = context or RenderContext()

    @abstractmethod
    def render(self, data: Any) -> str:
        """
        Render section data to markdown.

        Args:
            data: Section-specific data

        Returns:
            Formatted markdown string
        """
        pass

    def _wrap_text(self, text: str, indent: int = 0) -> str:
        """
        Wrap text to max_width with indentation.

        Args:
            text: Text to wrap
            indent: Indentation level

        Returns:
            Wrapped text
        """
        if self.context.max_width <= 0:
            return text

        words = text.split()
        lines = []
        current_line = []
        indent_str = " " * indent

        for word in words:
            test_line = " ".join(current_line + [word])
            if len(indent_str + test_line) <= self.context.max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(indent_str + " ".join(current_line))
                current_line = [word]

        if current_line:
            lines.append(indent_str + " ".join(current_line))

        return "\n".join(lines)

    def _format_link(self, text: str, url: str) -> str:
        """Format markdown link."""
        if not self.context.include_links:
            return text
        return f"[{text}]({url})"

    def _format_code(self, code: str, language: str = "") -> str:
        """Format code block."""
        fence = "```"
        return f"{fence}{language}\n{code}\n{fence}"

    def _normalize_whitespace(self, text: str) -> str:
        """Remove excess whitespace."""
        lines = [line.rstrip() for line in text.split("\n")]
        return "\n".join(lines)
```

### 2. Markdown Generation Rules

#### Consistent Heading Levels

Headings follow a strict hierarchy to ensure proper nesting.

```python
class MarkdownFormatter:
    """Utilities for consistent markdown formatting."""

    HEADING_LEVELS = {
        "h1": "#",
        "h2": "##",
        "h3": "###",
        "h4": "####",
        "h5": "#####",
        "h6": "######"
    }

    @staticmethod
    def heading(level: int, text: str) -> str:
        """
        Format heading.

        Args:
            level: Heading level (1-6)
            text: Heading text

        Returns:
            Formatted markdown heading
        """
        if level < 1 or level > 6:
            level = 1
        marker = "#" * level
        return f"{marker} {text}"

    @staticmethod
    def subheading(text: str) -> str:
        """Format H3 subheading (used within sections)."""
        return f"### {text}"

    @staticmethod
    def unordered_list(items: list[str], indent: int = 0) -> str:
        """
        Format unordered list.

        Args:
            items: List items
            indent: Indentation level (0-3)

        Returns:
            Formatted list
        """
        indent_str = "  " * max(0, min(indent, 3))
        return "\n".join(f"{indent_str}- {item}" for item in items)

    @staticmethod
    def ordered_list(items: list[str], indent: int = 0, start: int = 1) -> str:
        """
        Format ordered list.

        Args:
            items: List items
            indent: Indentation level
            start: Starting number

        Returns:
            Formatted list
        """
        indent_str = "  " * max(0, min(indent, 3))
        lines = []
        for i, item in enumerate(items, start=start):
            lines.append(f"{indent_str}{i}. {item}")
        return "\n".join(lines)

    @staticmethod
    def code_block(code: str, language: str = "python") -> str:
        """
        Format code block with language.

        Args:
            code: Code content
            language: Language identifier

        Returns:
            Formatted code block
        """
        return f"```{language}\n{code}\n```"

    @staticmethod
    def inline_code(text: str) -> str:
        """Format inline code."""
        return f"`{text}`"

    @staticmethod
    def blockquote(text: str) -> str:
        """
        Format blockquote.

        Args:
            text: Quote text

        Returns:
            Formatted blockquote
        """
        lines = text.split("\n")
        quoted = "\n".join(f"> {line}" for line in lines)
        return quoted

    @staticmethod
    def link(text: str, url: str) -> str:
        """Format markdown link."""
        return f"[{text}]({url})"

    @staticmethod
    def bold(text: str) -> str:
        """Format bold text."""
        return f"**{text}**"

    @staticmethod
    def italic(text: str) -> str:
        """Format italic text."""
        return f"*{text}*"

    @staticmethod
    def emphasis(text: str) -> str:
        """Format emphasized text."""
        return f"***{text}***"

    @staticmethod
    def strikethrough(text: str) -> str:
        """Format strikethrough text."""
        return f"~~{text}~~"

    @staticmethod
    def horizontal_rule() -> str:
        """Format horizontal rule."""
        return "---"

    @staticmethod
    def line_break() -> str:
        """Format line break."""
        return "\n"
```

### 3. Header Renderer

#### HeaderRenderer Implementation

Renders brief introduction and model-specific information.

```python
@dataclass
class HeaderData:
    """Data for header section."""
    title: str
    """Document title."""

    description: str
    """Brief description."""

    model_info: Optional[str] = None
    """Target model information."""

    version: Optional[str] = None
    """llms.txt version."""

    date_generated: Optional[str] = None
    """Generation timestamp."""


class HeaderRenderer(SectionRenderer):
    """Renders header section with title and metadata."""

    def render(self, data: HeaderData) -> str:
        """
        Render header section.

        Args:
            data: Header data

        Returns:
            Formatted markdown header
        """
        lines = []

        # Title
        lines.append(MarkdownFormatter.heading(1, data.title))
        lines.append("")

        # Description
        if data.description:
            lines.append(data.description)
            lines.append("")

        # Metadata
        metadata_items = []
        if data.model_info:
            metadata_items.append(f"**Model**: {data.model_info}")
        if data.version:
            metadata_items.append(f"**Version**: {data.version}")
        if data.date_generated and self.context.include_metadata:
            metadata_items.append(f"**Generated**: {data.date_generated}")

        if metadata_items:
            lines.append(MarkdownFormatter.unordered_list(metadata_items))
            lines.append("")

        # Usage note
        lines.append(
            MarkdownFormatter.blockquote(
                "This context block contains curated project information. "
                "Use it to understand key concepts, dependencies, and examples."
            )
        )

        return "\n".join(lines)
```

### 4. Concepts Renderer

#### ConceptsRenderer Implementation

Renders concepts with definitions, dependencies, and anti-patterns.

```python
@dataclass
class ConceptData:
    """Represents a single concept."""
    term: str
    """Concept term/name."""

    definition: str
    """Concept definition."""

    dependencies: list[str] = None
    """Related concepts this depends on."""

    anti_patterns: list[str] = None
    """Common mistakes/anti-patterns."""

    examples: list[str] = None
    """Example usage."""

    core: bool = False
    """Whether this is a core concept."""

    depth: int = 0
    """Dependency depth (0 = no dependencies)."""

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.anti_patterns is None:
            self.anti_patterns = []
        if self.examples is None:
            self.examples = []


class ConceptsRenderer(SectionRenderer):
    """Renders concepts section with definitions and relationships."""

    def render(self, concepts: list[ConceptData]) -> str:
        """
        Render concepts section.

        Args:
            concepts: List of concepts to render

        Returns:
            Formatted markdown concepts section
        """
        if not concepts:
            return ""

        lines = []

        # Group by depth
        by_depth = {}
        for concept in concepts:
            depth = concept.depth if concept.depth is not None else 0
            if depth not in by_depth:
                by_depth[depth] = []
            by_depth[depth].append(concept)

        # Render by depth (foundational first)
        for depth in sorted(by_depth.keys()):
            depth_concepts = by_depth[depth]

            # Depth subheading if multiple depths
            if len(by_depth) > 1:
                if depth == 0:
                    lines.append(MarkdownFormatter.subheading("Core Concepts"))
                else:
                    lines.append(
                        MarkdownFormatter.subheading(
                            f"Concepts (Dependency Level {depth})"
                        )
                    )
                lines.append("")

            # Render each concept
            for concept in sorted(depth_concepts, key=lambda c: c.term):
                lines.append(self._render_concept(concept))
                lines.append("")

        return "\n".join(lines)

    def _render_concept(self, concept: ConceptData) -> str:
        """Render individual concept."""
        lines = []

        # Term (bold if core concept)
        if concept.core:
            lines.append(MarkdownFormatter.bold(concept.term))
        else:
            lines.append(MarkdownFormatter.inline_code(concept.term))

        # Definition
        if concept.definition:
            definition_indent = self._wrap_text(concept.definition, indent=2)
            lines.append(f"  {concept.definition}")

        # Dependencies
        if concept.dependencies:
            dep_text = MarkdownFormatter.unordered_list(
                concept.dependencies, indent=1
            )
            lines.append(f"  **Depends on**: {', '.join(concept.dependencies)}")

        # Anti-patterns
        if concept.anti_patterns:
            lines.append("")
            lines.append("  **Avoid**:")
            for pattern in concept.anti_patterns:
                lines.append(f"    - {pattern}")

        # Examples
        if concept.examples:
            lines.append("")
            lines.append("  **Example**:")
            for example in concept.examples:
                lines.append(f"    - {example}")

        return "\n".join(lines)
```

### 5. Pages Renderer

#### PagesRenderer Implementation

Renders page index with content-type grouping and summaries.

```python
@dataclass
class PageData:
    """Represents a page in the index."""
    url: str
    """Page URL."""

    title: str
    """Page title."""

    summary: str
    """Brief summary."""

    content_type: str = "reference"
    """Type: 'main', 'core', 'guide', 'reference', 'example', 'deprecated'."""

    verification_date: Optional[str] = None
    """Last verification date."""

    relevance_score: float = 0.5
    """Relevance score (0-1)."""

    tags: list[str] = None
    """Topic tags."""

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class PagesRenderer(SectionRenderer):
    """Renders pages section with content-type grouping."""

    # Type display order and labels
    TYPE_ORDER = {
        "main": (0, "Main Documentation"),
        "core": (1, "Core Pages"),
        "guide": (2, "Guides & Tutorials"),
        "reference": (3, "Reference Material"),
        "example": (4, "Examples"),
        "deprecated": (5, "Deprecated/Legacy")
    }

    def render(self, pages: list[PageData]) -> str:
        """
        Render pages section.

        Args:
            pages: List of pages to render

        Returns:
            Formatted markdown pages section
        """
        if not pages:
            return ""

        lines = []

        # Group by content type
        by_type = {}
        for page in pages:
            ptype = page.content_type or "reference"
            if ptype not in by_type:
                by_type[ptype] = []
            by_type[ptype].append(page)

        # Sort types by predefined order
        sorted_types = sorted(
            by_type.keys(),
            key=lambda t: self.TYPE_ORDER.get(t, (999, t))[0]
        )

        # Render each type group
        for ptype in sorted_types:
            pages_in_type = by_type[ptype]

            # Type heading
            type_label = self.TYPE_ORDER.get(ptype, (999, ptype))[1]
            lines.append(MarkdownFormatter.subheading(type_label))
            lines.append("")

            # Sort pages within type by relevance
            sorted_pages = sorted(
                pages_in_type,
                key=lambda p: p.relevance_score,
                reverse=True
            )

            # Render each page
            for page in sorted_pages:
                lines.append(self._render_page(page))
                lines.append("")

        return "\n".join(lines)

    def _render_page(self, page: PageData) -> str:
        """Render individual page."""
        lines = []

        # Title + link
        if self.context.include_links:
            link_text = MarkdownFormatter.link(page.title, page.url)
            lines.append(f"- {link_text}")
        else:
            lines.append(f"- {page.title}")

        # Summary
        if page.summary:
            lines.append(f"  {page.summary}")

        # Tags
        if page.tags:
            tag_str = ", ".join(f"`{tag}`" for tag in page.tags)
            lines.append(f"  Tags: {tag_str}")

        # Verification date (if included in context)
        if page.verification_date and self.context.include_metadata:
            lines.append(f"  Verified: {page.verification_date}")

        return "\n".join(lines)
```

### 6. Examples Renderer

#### ExamplesRenderer Implementation

Renders Q&A pairs with code preservation and citations.

```python
@dataclass
class ExampleData:
    """Represents a Q&A example."""
    question: str
    """Question text."""

    answer: str
    """Answer text."""

    code: Optional[str] = None
    """Code example (optional)."""

    code_language: str = "python"
    """Programming language for code block."""

    source: Optional[str] = None
    """Source citation (page, section, etc.)."""

    tags: list[str] = None
    """Example tags."""

    core: bool = False
    """Whether this is a core example."""

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class ExamplesRenderer(SectionRenderer):
    """Renders examples section with Q&A pairs."""

    def render(self, examples: list[ExampleData]) -> str:
        """
        Render examples section.

        Args:
            examples: List of examples to render

        Returns:
            Formatted markdown examples section
        """
        if not examples:
            return ""

        lines = []

        # Group by core/extended
        core_examples = [e for e in examples if e.core]
        extended_examples = [e for e in examples if not e.core]

        # Render core examples
        if core_examples:
            lines.append(MarkdownFormatter.subheading("Core Examples"))
            lines.append("")
            for example in core_examples:
                lines.append(self._render_example(example))
                lines.append("")

        # Render extended examples
        if extended_examples:
            if core_examples:
                lines.append(MarkdownFormatter.subheading("Additional Examples"))
            lines.append("")
            for example in extended_examples:
                lines.append(self._render_example(example))
                lines.append("")

        return "\n".join(lines)

    def _render_example(self, example: ExampleData) -> str:
        """Render individual example."""
        lines = []

        # Question (bold)
        lines.append(MarkdownFormatter.bold(f"Q: {example.question}"))
        lines.append("")

        # Answer
        lines.append(f"**A:** {example.answer}")

        # Code block (if present)
        if example.code:
            lines.append("")
            code_block = MarkdownFormatter.code_block(
                example.code,
                example.code_language
            )
            lines.append(code_block)

        # Source citation
        if example.source and self.context.include_links:
            lines.append("")
            lines.append(f"*Source: {example.source}*")

        # Tags
        if example.tags:
            tag_str = ", ".join(f"`{tag}`" for tag in example.tags)
            lines.append(f"*Tags: {tag_str}*")

        return "\n".join(lines)
```

### 7. Footer Renderer

#### FooterRenderer Implementation

Renders response guidelines and dynamic instructions.

```python
@dataclass
class FooterData:
    """Data for footer section."""
    included_sections: list[str]
    """Sections included in context (e.g., ['concepts', 'pages', 'examples'])."""

    excluded_sections: list[str] = None
    """Sections excluded due to budget (optional)."""

    custom_guidelines: Optional[str] = None
    """Custom response guidelines."""

    model_name: Optional[str] = None
    """Target model name."""

    def __post_init__(self):
        if self.excluded_sections is None:
            self.excluded_sections = []


class FooterRenderer(SectionRenderer):
    """Renders footer with response guidelines and instructions."""

    def render(self, data: FooterData) -> str:
        """
        Render footer section.

        Args:
            data: Footer data

        Returns:
            Formatted markdown footer
        """
        lines = []

        lines.append(MarkdownFormatter.heading(2, "Response Guidelines"))
        lines.append("")

        # Dynamic guidelines based on included sections
        guidelines = self._generate_guidelines(
            data.included_sections,
            data.excluded_sections
        )
        lines.extend(guidelines)

        # Custom guidelines (if provided)
        if data.custom_guidelines:
            lines.append("")
            lines.append(data.custom_guidelines)

        # Footer note
        lines.append("")
        lines.append(MarkdownFormatter.italic(
            "This context was generated from an llms.txt knowledge base. "
            "Reference included materials when responding."
        ))

        return "\n".join(lines)

    def _generate_guidelines(
        self,
        included: list[str],
        excluded: list[str]
    ) -> list[str]:
        """
        Generate dynamic guidelines based on included content.

        Args:
            included: Included section names
            excluded: Excluded section names

        Returns:
            List of guideline lines
        """
        guidelines = []

        # General instruction
        guidelines.append(
            "When responding, prioritize information from the included sections below:"
        )
        guidelines.append("")

        # List included sections
        section_descriptions = {
            "header": "Brief introduction and model information",
            "concepts": "Key concepts, definitions, and anti-patterns",
            "pages": "Index of relevant documentation pages",
            "examples": "Q&A examples and few-shot demonstrations"
        }

        included_items = []
        for section in included:
            desc = section_descriptions.get(section, section)
            included_items.append(f"{section}: {desc}")

        guidelines.append(MarkdownFormatter.unordered_list(included_items))

        # If sections were excluded
        if excluded:
            guidelines.append("")
            guidelines.append(
                MarkdownFormatter.italic(
                    f"Note: {', '.join(excluded)} sections were excluded "
                    "due to context budget constraints."
                )
            )

        # General advice
        guidelines.append("")
        guidelines.append(
            MarkdownFormatter.unordered_list([
                "Use concept definitions to ground technical discussions",
                "Reference page summaries for reliable information",
                "Apply examples as patterns for similar scenarios",
                "When uncertain, cite the specific section you're referencing"
            ])
        )

        return guidelines
```

### 8. Unified Renderer Coordinator

#### RendererCoordinator Class

Coordinates rendering of all sections.

```python
@dataclass
class CompleteContextData:
    """Data for complete context block."""
    header: HeaderData
    concepts: list[ConceptData]
    pages: list[PageData]
    examples: list[ExampleData]
    footer: FooterData


class RendererCoordinator:
    """Coordinates rendering of all sections."""

    def __init__(self, context: Optional[RenderContext] = None):
        """Initialize coordinator."""
        self.context = context or RenderContext()

        # Initialize renderers
        self.header_renderer = HeaderRenderer(self.context)
        self.concepts_renderer = ConceptsRenderer(self.context)
        self.pages_renderer = PagesRenderer(self.context)
        self.examples_renderer = ExamplesRenderer(self.context)
        self.footer_renderer = FooterRenderer(self.context)

    def render_all(self, data: CompleteContextData) -> str:
        """
        Render complete context block.

        Args:
            data: All section data

        Returns:
            Complete formatted context block
        """
        sections = []

        # Header
        if data.header:
            sections.append(self.header_renderer.render(data.header))

        # Concepts
        if data.concepts:
            sections.append(self.concepts_renderer.render(data.concepts))

        # Pages
        if data.pages:
            sections.append(self.pages_renderer.render(data.pages))

        # Examples
        if data.examples:
            sections.append(self.examples_renderer.render(data.examples))

        # Footer
        if data.footer:
            sections.append(self.footer_renderer.render(data.footer))

        # Join sections with double newline
        return "\n\n".join(sections)

    def render_section(self, section: str, data: Any) -> str:
        """
        Render single section.

        Args:
            section: Section name ('header', 'concepts', 'pages', 'examples', 'footer')
            data: Section data

        Returns:
            Rendered section
        """
        if section == "header":
            return self.header_renderer.render(data)
        elif section == "concepts":
            return self.concepts_renderer.render(data)
        elif section == "pages":
            return self.pages_renderer.render(data)
        elif section == "examples":
            return self.examples_renderer.render(data)
        elif section == "footer":
            return self.footer_renderer.render(data)
        else:
            raise ValueError(f"Unknown section: {section}")
```

## Deliverables

1. **SectionRenderer abstract base class**: Unified renderer interface
2. **RenderContext dataclass**: Configurable rendering options
3. **MarkdownFormatter utility class**: Consistent markdown generation
4. **HeaderRenderer class**: Renders introduction and metadata
5. **ConceptsRenderer class**: Renders concepts with dependencies and anti-patterns
6. **PagesRenderer class**: Renders page index with type grouping
7. **ExamplesRenderer class**: Renders Q&A pairs with code and citations
8. **FooterRenderer class**: Renders guidelines and dynamic instructions
9. **RendererCoordinator class**: Orchestrates multi-section rendering
10. **Complete test suite**: Renders all section types with various configurations

## Acceptance Criteria

- All renderers implement consistent SectionRenderer interface
- Markdown generation follows strict heading level hierarchy (H1 for title, H3 for sections, etc.)
- Concept rendering includes definitions, dependencies, and anti-pattern callouts
- Page rendering groups by content_type and sorts by relevance within groups
- Example rendering preserves code blocks and includes source citations
- Footer rendering generates dynamic instructions based on included sections
- MarkdownFormatter provides utilities for all common markdown elements
- RenderContext enables customization of rendering behavior (width, metadata, links, compact mode)
- RendererCoordinator successfully renders all sections in sequence
- Test suite covers all section types, edge cases, and custom rendering options
- Output is valid markdown with proper escaping and formatting

## Next Step

Proceed to **v0.3.2c — Output Formats & Processing Modes**, which takes rendered sections and converts them to multiple output formats (markdown, XML, JSON, plain text) using the DocStratum Hybrid approach.
