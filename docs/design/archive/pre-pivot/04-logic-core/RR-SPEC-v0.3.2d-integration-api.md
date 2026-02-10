# v0.3.2d — Integration API & Configuration

> **Phase**: v0.3.2 "Context Builder" | **Component**: Public API & Integration
>
> **Stability**: DRAFT | **Target Release**: v0.3.2-alpha

## Objective

Provide a unified, fluent public API (`build_context_block()`) for context generation that integrates all Context Builder components (token budget, renderers, output formats). The system offers a ContextConfig dataclass for comprehensive configuration, a builder pattern for intuitive fluent API usage, integration with v0.3.1 Loader output and v0.3.3/v0.3.4 Agent modules, detailed context block metadata, extensive logging/observability, and a complete integration test suite.

## Scope

This specification covers:
- **Public API**: `build_context_block()` as unified entry point
- **ContextConfig Dataclass**: All configuration options (token budget, format, sections, priorities)
- **Builder Pattern**: Fluent API for intuitive configuration
- **Loader Integration**: Accepts v0.3.1 LlmsTxt objects with pages, concepts, examples
- **Agent Integration**: Outputs serve as system prompts for v0.3.3/v0.3.4 agent modules
- **Context Block Metadata**: Generation timestamp, token counts, included/excluded sections, warnings
- **Logging & Observability**: Debug/info logging of all context building steps
- **Complete Implementation**: Public API with all integrations and configuration options
- **Integration Test Suite**: Tests covering all workflows and component interactions

## Dependencies

- **v0.3.1 Loader Module**: Provides `LlmsTxt` class with pages, concepts, examples
- **v0.3.2a Token Budget**: `BudgetEngine`, `BudgetConfig`, `BudgetReport`
- **v0.3.2b Renderers**: `RendererCoordinator`, section data classes
- **v0.3.2c Output Formats**: `FormatEngine`, `FormatOptions`, `OutputFormat`
- **Python 3.9+**: Dataclasses, type hints, logging, standard library

## Content Sections

### 1. ContextConfig Dataclass

#### Complete Configuration Options

```python
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from enum import Enum
import logging

# Import from v0.3.2 submodules
from docstratum.v0_3_2.token_budget import BudgetConfig
from docstratum.v0_3_2.output_formats import OutputFormat, FormatOptions


class PriorityMode(Enum):
    """Priority selection strategy."""
    AUTOMATIC = "automatic"       # Auto-select based on content
    CONCEPTS_FIRST = "concepts_first"  # Prioritize concept definitions
    EXAMPLES_FIRST = "examples_first"  # Prioritize examples
    BALANCED = "balanced"         # Even distribution


class InclusionMode(Enum):
    """How to include content."""
    ALL = "all"                   # Include everything
    SELECTIVE = "selective"       # Priority-based selection
    REQUIRED_ONLY = "required_only"  # Only core items


@dataclass
class ContextConfig:
    """Complete configuration for context building."""

    # Token Budget Settings
    max_tokens: int = 16000
    """Maximum tokens for context block."""

    token_budget_config: Optional[BudgetConfig] = None
    """Token budget configuration (uses default if None)."""

    # Output Format Settings
    output_format: OutputFormat = OutputFormat.MARKDOWN
    """Output format (markdown, xml, json, text)."""

    format_options: Optional[FormatOptions] = None
    """Format-specific options."""

    # Section Inclusion
    include_header: bool = True
    """Include header section."""

    include_concepts: bool = True
    """Include concepts section."""

    include_pages: bool = True
    """Include pages section."""

    include_examples: bool = True
    """Include examples section."""

    include_footer: bool = True
    """Include footer section."""

    # Content Selection
    inclusion_mode: InclusionMode = InclusionMode.SELECTIVE
    """Content inclusion strategy."""

    priority_mode: PriorityMode = PriorityMode.AUTOMATIC
    """Priority selection strategy."""

    max_concepts: Optional[int] = None
    """Maximum number of concepts (None = no limit)."""

    max_pages: Optional[int] = None
    """Maximum number of pages (None = no limit)."""

    max_examples: Optional[int] = None
    """Maximum number of Q&A examples (None = no limit)."""

    # Advanced Options
    enable_concept_injection: bool = True
    """Inject concept definitions where referenced."""

    enable_dynamic_reallocation: bool = True
    """Reallocate unused tokens between sections."""

    hybrid_mode: bool = True
    """Enable DocStratum Hybrid processing mode."""

    # Metadata & Logging
    include_generation_metadata: bool = True
    """Include generation timestamp, version, token count in output."""

    model_name: str = "unknown"
    """Target model name (for metadata and config)."""

    custom_footer: Optional[str] = None
    """Custom footer guidelines (appended to auto-generated)."""

    log_level: int = logging.INFO
    """Logging level (DEBUG, INFO, WARNING, ERROR)."""

    return_metadata: bool = True
    """Return context block metadata alongside output."""

    # Custom Options
    custom_context_variables: dict = field(default_factory=dict)
    """Custom template variables for advanced rendering."""

    def __post_init__(self):
        """Initialize defaults for optional fields."""
        if self.token_budget_config is None:
            self.token_budget_config = BudgetConfig(max_tokens=self.max_tokens)

        if self.format_options is None:
            self.format_options = FormatOptions(include_metadata=True)

    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            "max_tokens": self.max_tokens,
            "output_format": self.output_format.value,
            "include_header": self.include_header,
            "include_concepts": self.include_concepts,
            "include_pages": self.include_pages,
            "include_examples": self.include_examples,
            "include_footer": self.include_footer,
            "inclusion_mode": self.inclusion_mode.value,
            "priority_mode": self.priority_mode.value,
            "max_concepts": self.max_concepts,
            "max_pages": self.max_pages,
            "max_examples": self.max_examples,
            "hybrid_mode": self.hybrid_mode,
            "model_name": self.model_name,
        }

    def validate(self) -> list[str]:
        """
        Validate configuration.

        Returns:
            List of validation error messages (empty = valid)
        """
        errors = []

        if self.max_tokens < 500:
            errors.append("max_tokens must be at least 500")

        if self.max_concepts is not None and self.max_concepts < 1:
            errors.append("max_concepts must be at least 1 or None")

        if self.max_pages is not None and self.max_pages < 1:
            errors.append("max_pages must be at least 1 or None")

        if self.max_examples is not None and self.max_examples < 1:
            errors.append("max_examples must be at least 1 or None")

        return errors
```

### 2. Builder Pattern Implementation

#### ContextBuilder Fluent API

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from docstratum.v0_3_1.loader import LlmsTxt


class ContextBuilder:
    """
    Builder for fluent context block creation.

    Usage:
        context = (ContextBuilder(llms_txt)
            .with_budget(8000)
            .with_format("json")
            .include_concepts()
            .include_examples()
            .build())
    """

    def __init__(self, llms_txt: "LlmsTxt"):
        """
        Initialize builder.

        Args:
            llms_txt: Loaded llms.txt object from v0.3.1
        """
        self.llms_txt = llms_txt
        self.config = ContextConfig()
        self._logger = logging.getLogger(__name__)

    # Configuration Methods (chainable)

    def with_budget(self, tokens: int) -> "ContextBuilder":
        """Set maximum token budget."""
        self.config.max_tokens = tokens
        return self

    def with_format(self, format_name: str) -> "ContextBuilder":
        """
        Set output format.

        Args:
            format_name: 'markdown', 'xml', 'json', or 'text'
        """
        try:
            self.config.output_format = OutputFormat(format_name)
        except ValueError:
            raise ValueError(
                f"Unknown format: {format_name}. "
                f"Valid options: {[f.value for f in OutputFormat]}"
            )
        return self

    def with_model(self, model_name: str) -> "ContextBuilder":
        """Set target model name."""
        self.config.model_name = model_name
        return self

    def include_header(self, include: bool = True) -> "ContextBuilder":
        """Include/exclude header section."""
        self.config.include_header = include
        return self

    def include_concepts(self, include: bool = True) -> "ContextBuilder":
        """Include/exclude concepts section."""
        self.config.include_concepts = include
        return self

    def include_pages(self, include: bool = True) -> "ContextBuilder":
        """Include/exclude pages section."""
        self.config.include_pages = include
        return self

    def include_examples(self, include: bool = True) -> "ContextBuilder":
        """Include/exclude examples section."""
        self.config.include_examples = include
        return self

    def include_footer(self, include: bool = True) -> "ContextBuilder":
        """Include/exclude footer section."""
        self.config.include_footer = include
        return self

    def with_priority_mode(self, mode: str) -> "ContextBuilder":
        """
        Set priority selection mode.

        Args:
            mode: 'automatic', 'concepts_first', 'examples_first', 'balanced'
        """
        try:
            self.config.priority_mode = PriorityMode(mode)
        except ValueError:
            raise ValueError(f"Unknown priority mode: {mode}")
        return self

    def with_inclusion_mode(self, mode: str) -> "ContextBuilder":
        """
        Set inclusion mode.

        Args:
            mode: 'all', 'selective', 'required_only'
        """
        try:
            self.config.inclusion_mode = InclusionMode(mode)
        except ValueError:
            raise ValueError(f"Unknown inclusion mode: {mode}")
        return self

    def max_concepts(self, count: int) -> "ContextBuilder":
        """Limit number of concepts."""
        self.config.max_concepts = count
        return self

    def max_pages(self, count: int) -> "ContextBuilder":
        """Limit number of pages."""
        self.config.max_pages = count
        return self

    def max_examples(self, count: int) -> "ContextBuilder":
        """Limit number of examples."""
        self.config.max_examples = count
        return self

    def with_custom_footer(self, footer_text: str) -> "ContextBuilder":
        """Set custom footer text."""
        self.config.custom_footer = footer_text
        return self

    def enable_hybrid_mode(self, enable: bool = True) -> "ContextBuilder":
        """Enable/disable DocStratum Hybrid mode."""
        self.config.hybrid_mode = enable
        return self

    def enable_concept_injection(self, enable: bool = True) -> "ContextBuilder":
        """Enable/disable concept injection."""
        self.config.enable_concept_injection = enable
        return self

    def with_log_level(self, level: int) -> "ContextBuilder":
        """Set logging level."""
        self.config.log_level = level
        return self

    def build(self) -> "ContextBlock":
        """
        Build context block.

        Returns:
            ContextBlock with output and metadata

        Raises:
            ValueError: If configuration is invalid
        """
        # Validate configuration
        errors = self.config.validate()
        if errors:
            raise ValueError(f"Invalid configuration: {'; '.join(errors)}")

        # Build context
        return build_context_block(self.llms_txt, self.config)

    # Fluent shortcuts for common configurations

    def minimal(self) -> "ContextBuilder":
        """Configure for minimal context (just concepts and footer)."""
        return (self
            .with_budget(4000)
            .include_header(False)
            .include_concepts()
            .include_pages(False)
            .include_examples(False)
            .include_footer()
        )

    def balanced(self) -> "ContextBuilder":
        """Configure for balanced context (all sections)."""
        return (self
            .with_budget(16000)
            .include_header()
            .include_concepts()
            .include_pages()
            .include_examples()
            .include_footer()
            .with_priority_mode("balanced")
        )

    def comprehensive(self) -> "ContextBuilder":
        """Configure for comprehensive context (all sections, large budget)."""
        return (self
            .with_budget(32000)
            .include_header()
            .include_concepts()
            .include_pages()
            .include_examples()
            .include_footer()
            .with_priority_mode("automatic")
            .with_inclusion_mode("all")
        )
```

### 3. Context Block Metadata

#### ContextBlockMetadata Structure

```python
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ContextBlockMetadata:
    """Metadata about generated context block."""

    generated: datetime
    """Timestamp of generation."""

    version: str = "0.3.2"
    """llms.txt version."""

    total_tokens: int = 0
    """Total tokens in context block."""

    max_tokens: int = 16000
    """Maximum allowed tokens."""

    utilization_percent: float = 0.0
    """Percentage of max_tokens used."""

    model: str = "unknown"
    """Target model name."""

    output_format: str = "markdown"
    """Output format used."""

    included_sections: list[str] = field(default_factory=list)
    """Sections included in output."""

    excluded_sections: list[str] = field(default_factory=list)
    """Sections excluded from output."""

    section_tokens: dict[str, int] = field(default_factory=dict)
    """Token count per section."""

    warnings: list[str] = field(default_factory=list)
    """Warnings generated during building."""

    errors: list[str] = field(default_factory=list)
    """Errors (if any) during building."""

    summary(self) -> str:
        """Generate human-readable summary."""
        lines = [
            f"Context Block Metadata (generated {self.generated.isoformat()})",
            f"Token usage: {self.total_tokens}/{self.max_tokens} "
            f"({self.utilization_percent:.1f}%)",
            f"Model: {self.model}",
            f"Format: {self.output_format}",
            "",
            "Included sections:",
        ]

        for section in self.included_sections:
            tokens = self.section_tokens.get(section, 0)
            lines.append(f"  - {section}: {tokens} tokens")

        if self.excluded_sections:
            lines.append("")
            lines.append("Excluded sections:")
            for section in self.excluded_sections:
                lines.append(f"  - {section}")

        if self.warnings:
            lines.append("")
            lines.append("Warnings:")
            for warning in self.warnings:
                lines.append(f"  - {warning}")

        return "\n".join(lines)


@dataclass
class ContextBlock:
    """Output of context building."""

    content: str
    """Generated context block content."""

    metadata: ContextBlockMetadata
    """Generation metadata."""

    def to_system_prompt(self) -> str:
        """Return content for use as LLM system prompt."""
        return self.content

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "metadata": {
                "generated": self.metadata.generated.isoformat(),
                "version": self.metadata.version,
                "total_tokens": self.metadata.total_tokens,
                "max_tokens": self.metadata.max_tokens,
                "utilization_percent": self.metadata.utilization_percent,
                "model": self.metadata.model,
                "output_format": self.metadata.output_format,
                "included_sections": self.metadata.included_sections,
                "excluded_sections": self.metadata.excluded_sections,
                "section_tokens": self.metadata.section_tokens,
                "warnings": self.metadata.warnings,
                "errors": self.metadata.errors,
            }
        }
```

### 4. Public API Implementation

#### build_context_block() Function

```python
import logging
from typing import Union, Optional


logger = logging.getLogger("docstratum.context_builder")


def build_context_block(
    llms_txt: "LlmsTxt",
    config: Optional[Union[ContextConfig, dict]] = None
) -> ContextBlock:
    """
    Build context block from llms.txt object.

    Main entry point for context building. Orchestrates token budgeting,
    rendering, and format conversion.

    Args:
        llms_txt: Loaded LlmsTxt object from v0.3.1
        config: Configuration (ContextConfig or dict)

    Returns:
        ContextBlock with content and metadata

    Example:
        from docstratum.v0_3_1 import load_llms_txt
        from docstratum.v0_3_2 import build_context_block, ContextConfig

        # Load llms.txt
        llms = load_llms_txt("project_root/")

        # Build with default config
        context = build_context_block(llms)

        # Or with custom config
        config = ContextConfig(
            max_tokens=8000,
            output_format=OutputFormat.JSON,
            include_pages=False
        )
        context = build_context_block(llms, config)

        # Use as system prompt
        system_prompt = context.to_system_prompt()
    """

    # Normalize config
    if config is None:
        config = ContextConfig()
    elif isinstance(config, dict):
        config = ContextConfig(**config)

    # Setup logging
    logging.basicConfig(level=config.log_level)
    logger.info(f"Building context block for model: {config.model_name}")
    logger.debug(f"Configuration: {config.to_dict()}")

    # Validate inputs
    config_errors = config.validate()
    if config_errors:
        logger.error(f"Configuration errors: {config_errors}")
        raise ValueError(f"Invalid configuration: {'; '.join(config_errors)}")

    metadata = ContextBlockMetadata(
        generated=datetime.now(),
        model=config.model_name,
        max_tokens=config.max_tokens,
        output_format=config.output_format.value
    )

    warnings = []

    try:
        # Step 1: Extract content from llms_txt
        logger.info("Step 1: Extracting content from llms.txt")
        pages = llms_txt.pages if config.include_pages else []
        concepts = llms_txt.concepts if config.include_concepts else []
        examples = llms_txt.examples if config.include_examples else []

        logger.debug(
            f"Extracted: {len(pages)} pages, {len(concepts)} concepts, "
            f"{len(examples)} examples"
        )

        # Step 2: Apply content limits
        logger.info("Step 2: Applying content limits")
        if config.max_concepts is not None:
            concepts = concepts[:config.max_concepts]

        if config.max_pages is not None:
            pages = pages[:config.max_pages]

        if config.max_examples is not None:
            examples = examples[:config.max_examples]

        # Step 3: Token budgeting
        logger.info("Step 3: Applying token budget")
        budget_engine = BudgetEngine(config.token_budget_config)

        section_items = {
            "concepts": _to_content_items(concepts),
            "pages": _to_content_items(pages),
            "examples": _to_content_items(examples)
        }

        processed_items, budget_report = budget_engine.process_sections(
            section_items
        )

        logger.info(f"Token budget report:\n{budget_report.summary()}")
        metadata.section_tokens = {
            section: report.used
            for section, report in budget_report.sections.items()
        }

        # Step 4: Concept Injection (optional)
        if config.enable_concept_injection:
            logger.info("Step 4: Applying concept injection")
            processed_items = _inject_concepts(
                processed_items,
                llms_txt.concepts
            )

        # Step 5: Rendering
        logger.info("Step 5: Rendering sections")
        rendered = _render_sections(
            llms_txt,
            processed_items,
            config,
            metadata
        )

        # Step 6: Format conversion
        logger.info(f"Step 6: Converting to {config.output_format.value} format")
        format_engine = FormatEngine(
            config.output_format,
            config.format_options
        )

        context_content = format_engine.process(
            rendered,
            _to_format_metadata(metadata, config)
        )

        # Step 7: Validation
        logger.info("Step 7: Validating output")
        is_valid, validation_errors = format_engine.validate_output(
            context_content
        )

        if not is_valid:
            warnings.extend(
                f"Validation warning: {err}" for err in validation_errors
            )
            logger.warning(f"Validation warnings: {validation_errors}")

        # Update metadata
        metadata.total_tokens = len(context_content) // 4  # Rough estimate
        metadata.utilization_percent = (
            metadata.total_tokens / config.max_tokens * 100
        )
        metadata.included_sections = [
            s for s in ["header", "concepts", "pages", "examples", "footer"]
            if getattr(config, f"include_{s}", True)
        ]
        metadata.warnings = warnings

        logger.info(
            f"Context block built successfully. "
            f"Total tokens: {metadata.total_tokens}/{config.max_tokens}"
        )

        return ContextBlock(content=context_content, metadata=metadata)

    except Exception as e:
        logger.error(f"Error building context block: {str(e)}", exc_info=True)
        metadata.errors.append(str(e))
        raise


def build_context_block_from_builder(builder: ContextBuilder) -> ContextBlock:
    """
    Build context block using ContextBuilder.

    Args:
        builder: Configured ContextBuilder instance

    Returns:
        ContextBlock

    Example:
        context = (ContextBuilder(llms_txt)
            .with_budget(8000)
            .with_format("json")
            .include_concepts()
            .build())
    """
    return builder.build()
```

### 5. Helper Functions

#### Content Conversion & Rendering

```python
def _to_content_items(items: list) -> list:
    """
    Convert various item types to ContentItem for budgeting.

    Supports pages, concepts, and examples from v0.3.1.
    """
    from docstratum.v0_3_2.token_budget import ContentItem

    content_items = []

    for item in items:
        # Detect item type and assign priority
        priority = 1.0
        text = ""

        if hasattr(item, "definition"):  # Concept
            text = item.definition
            priority = 1.0 if getattr(item, "core", False) else 0.75
            item_id = getattr(item, "term", "unknown")

        elif hasattr(item, "url"):  # Page
            text = getattr(item, "summary", "")
            priority = 1.0 if getattr(item, "type") == "main" else 0.6
            item_id = getattr(item, "url", "unknown")

        elif hasattr(item, "question"):  # Example
            text = (getattr(item, "question", "") + "\n" +
                   getattr(item, "answer", ""))
            priority = 1.0 if getattr(item, "core", False) else 0.75
            item_id = getattr(item, "id", f"example_{id(item)}")

        if text:
            content_items.append(
                ContentItem(
                    id=item_id,
                    text=text,
                    priority=priority,
                    category=_get_item_category(item)
                )
            )

    return content_items


def _get_item_category(item) -> str:
    """Determine category of content item."""
    if hasattr(item, "definition"):
        return "concepts"
    elif hasattr(item, "url"):
        return "pages"
    elif hasattr(item, "question"):
        return "examples"
    return "default"


def _inject_concepts(
    section_items: dict,
    all_concepts: list
) -> dict:
    """Inject concept definitions where referenced."""
    # Placeholder: identify concept references and ensure definitions
    # are included in output
    return section_items


def _render_sections(
    llms_txt: "LlmsTxt",
    processed_items: dict,
    config: ContextConfig,
    metadata: ContextBlockMetadata
) -> str:
    """
    Render all sections using RendererCoordinator.

    Returns:
        Markdown content ready for format conversion
    """
    from docstratum.v0_3_2.section_renderers import (
        RendererCoordinator,
        RenderContext,
        HeaderData,
        ConceptData,
        PageData,
        ExampleData,
        FooterData
    )

    # Create render context
    render_context = RenderContext(
        include_metadata=config.include_generation_metadata,
        include_links=True,
        custom_variables=config.custom_context_variables
    )

    # Convert items to renderer data classes
    header_data = HeaderData(
        title="Knowledge Base Context",
        description=getattr(llms_txt, "description", ""),
        model_info=config.model_name,
        version="0.3.2",
        date_generated=metadata.generated.isoformat() if config.include_generation_metadata else None
    )

    concept_data = [
        ConceptData(
            term=getattr(c, "term", ""),
            definition=getattr(c, "definition", ""),
            dependencies=getattr(c, "dependencies", []),
            anti_patterns=getattr(c, "anti_patterns", []),
            core=getattr(c, "core", False)
        )
        for c in processed_items.get("concepts", [])
    ]

    page_data = [
        PageData(
            url=getattr(p, "url", ""),
            title=getattr(p, "title", ""),
            summary=getattr(p, "summary", ""),
            content_type=getattr(p, "type", "reference"),
            tags=getattr(p, "tags", [])
        )
        for p in processed_items.get("pages", [])
    ]

    example_data = [
        ExampleData(
            question=getattr(e, "question", ""),
            answer=getattr(e, "answer", ""),
            code=getattr(e, "code", None),
            source=getattr(e, "source", None),
            core=getattr(e, "core", False)
        )
        for e in processed_items.get("examples", [])
    ]

    footer_data = FooterData(
        included_sections=metadata.included_sections,
        custom_guidelines=config.custom_footer
    )

    # Use coordinator to render all sections
    coordinator = RendererCoordinator(render_context)

    sections = []

    if config.include_header:
        sections.append(coordinator.render_section("header", header_data))

    if config.include_concepts:
        sections.append(coordinator.render_section("concepts", concept_data))

    if config.include_pages:
        sections.append(coordinator.render_section("pages", page_data))

    if config.include_examples:
        sections.append(coordinator.render_section("examples", example_data))

    if config.include_footer:
        sections.append(coordinator.render_section("footer", footer_data))

    return "\n\n".join(sections)


def _to_format_metadata(
    metadata: ContextBlockMetadata,
    config: ContextConfig
) -> "FormatMetadata":
    """Convert ContextBlockMetadata to FormatMetadata."""
    from docstratum.v0_3_2.output_formats import FormatMetadata

    return FormatMetadata(
        generated=metadata.generated.isoformat(),
        version=metadata.version,
        token_count=metadata.total_tokens,
        model=metadata.model,
        included_sections=metadata.included_sections,
        excluded_sections=metadata.excluded_sections
    )
```

### 6. Logging & Observability

#### Context Building Observability

```python
class ContextBuildingObserver:
    """Observes and logs context building process."""

    def __init__(self, log_level: int = logging.INFO):
        """Initialize observer."""
        self.logger = logging.getLogger("docstratum.context_builder")
        self.logger.setLevel(log_level)

        # Add console handler if not present
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(log_level)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log_build_start(self, config: ContextConfig):
        """Log start of context building."""
        self.logger.info(
            f"Building context block: model={config.model_name}, "
            f"format={config.output_format.value}, "
            f"max_tokens={config.max_tokens}"
        )

    def log_content_extraction(self, pages: int, concepts: int, examples: int):
        """Log content extraction."""
        self.logger.debug(
            f"Extracted content: {pages} pages, "
            f"{concepts} concepts, {examples} examples"
        )

    def log_budget_report(self, report):
        """Log token budget report."""
        self.logger.info(f"Token budget:\n{report.summary()}")

    def log_section_rendered(self, section: str, token_count: int):
        """Log section rendering."""
        self.logger.debug(f"Rendered section: {section} ({token_count} tokens)")

    def log_format_conversion(self, source_format: str, target_format: str):
        """Log format conversion."""
        self.logger.debug(f"Converting from {source_format} to {target_format}")

    def log_build_complete(self, metadata: ContextBlockMetadata):
        """Log completion of context building."""
        self.logger.info(
            f"Context block complete: {metadata.total_tokens} tokens, "
            f"{metadata.utilization_percent:.1f}% utilized"
        )
        if metadata.warnings:
            self.logger.warning(f"Warnings: {metadata.warnings}")
```

## Deliverables

1. **ContextConfig dataclass**: Complete configuration options
2. **ContextBuilder class**: Fluent API for configuration
3. **ContextBlockMetadata dataclass**: Generation metadata
4. **ContextBlock dataclass**: Output with content + metadata
5. **build_context_block() public function**: Main entry point
6. **build_context_block_from_builder() function**: Builder shortcut
7. **Helper functions**: Content conversion, rendering, format metadata
8. **ContextBuildingObserver class**: Logging and observability
9. **Complete integration**: All v0.3.2a/b/c components coordinated
10. **Integration test suite**: All workflows and component interactions

## Acceptance Criteria

- ContextConfig provides all necessary configuration options
- ContextBuilder implements fluent API with all chainable methods
- Builder shortcuts (minimal, balanced, comprehensive) work correctly
- build_context_block() integrates all submodules in correct sequence
- Metadata accurately captures generation details, tokens, warnings
- ContextBlock provides content and metadata in consistent structure
- Logging at DEBUG level shows all internal steps
- Logging at INFO level shows high-level progress
- Config validation catches invalid settings
- Integration with v0.3.1 Loader (llms_txt input) works correctly
- Integration with v0.3.3/v0.3.4 Agent modules (system prompt output) works
- Test suite covers all configuration combinations and workflows
- ContextBuilder fluent API enables intuitive usage patterns
- Error handling provides clear, actionable error messages
- Output metadata enables debugging and optimization

## Next Step

Complete Phase v0.3.2 "Context Builder" with all 4 documentation files. Begin Phase v0.3.3 "Reasoning Agent" for agent-specific prompt engineering and multi-step reasoning.
