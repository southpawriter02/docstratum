# v0.3.2a — Token Budget Engine & Priority System

> **Phase**: v0.3.2 "Context Builder" | **Component**: Token Budget Management
>
> **Stability**: DRAFT | **Target Release**: v0.3.2-alpha

## Objective

Implement a robust token budget management system that enables precise allocation of LLM context window space across context block sections. The Token Budget Engine provides token estimation (char/4 rough estimate + tiktoken precise counting), dynamic budget allocation with priority-based content selection, overflow handling with intelligent truncation, and comprehensive budget reporting for observability and debugging.

## Scope

This specification covers:
- **Token Estimation**: Character-based approximation and model-specific tokenization
- **Budget Allocation**: Dividing fixed token budget across 5 sections with configurable splits
- **Priority Selection**: Content prioritization when budget constraints require truncation
- **Dynamic Reallocation**: Redistributing unused tokens from small sections to larger ones
- **Overflow Handling**: Multiple truncation strategies (drop, summarize, ellipsis)
- **Budget Reporting**: Detailed per-section token accounting and metadata
- **Configuration Interface**: Flexible BudgetConfig dataclass for customization
- **Complete Implementation**: BudgetEngine class with token tracking and reallocation logic
- **Test Suite**: Comprehensive test coverage of all budget scenarios

## Dependencies

- **v0.3.1 Loader Module**: Provides LlmsTxt objects with pages, concepts, examples
- **Python 3.9+**: Type hints, dataclasses, standard library
- **tiktoken**: Optional; for precise token counting with GPT-series models
- **v0.3.2c Output Formats**: Integrates with format engines for section rendering

## Content Sections

### 1. Token Estimation Methods

#### Character-Based Approximation

The simplest estimation method divides character count by 4, reflecting the average English word tokenization ratio. Reliable for quick calculations and fallback scenarios.

```python
def estimate_tokens_char_based(text: str) -> int:
    """
    Estimate token count using character-based approximation.
    Assumes ~4 characters per token (English average).

    Args:
        text: Input text to estimate

    Returns:
        Estimated token count
    """
    return max(1, len(text) // 4)


class TokenEstimator:
    """Base token estimator with multiple strategies."""

    @staticmethod
    def char_based(text: str) -> int:
        """Char/4 approximation."""
        return max(1, len(text) // 4)
```

**Precision**: ±10-15% for typical English text
**Speed**: O(n) single pass
**Fallback**: Always available, no dependencies

#### TikToken Precise Counting

TikToken provides model-specific tokenization, crucial for GPT-3.5, GPT-4, and Claude models. When available, yields actual token counts.

```python
import tiktoken

class TokenEstimator:
    """Enhanced token estimator with tiktoken support."""

    def __init__(self, model: str = "gpt-3.5-turbo"):
        """
        Initialize with specific model tokenizer.

        Args:
            model: Model name (gpt-3.5-turbo, gpt-4, claude-2, etc.)
        """
        self.model = model
        try:
            self.encoder = tiktoken.encoding_for_model(model)
            self.precise = True
        except (ValueError, KeyError):
            self.encoder = None
            self.precise = False

    def estimate(self, text: str) -> int:
        """
        Estimate tokens using tiktoken if available, else char-based.

        Args:
            text: Input text

        Returns:
            Token count (precise or estimated)
        """
        if self.precise:
            try:
                return len(self.encoder.encode(text))
            except Exception:
                return self.char_based(text)
        return self.char_based(text)

    def estimate_batch(self, items: list[str]) -> list[int]:
        """Estimate multiple items efficiently."""
        return [self.estimate(item) for item in items]
```

**Precision**: 100% accurate for target model
**Speed**: O(n) encoding pass
**Availability**: Requires tiktoken + model in registry
**Fallback**: Automatic char-based fallback

#### Model-Specific Tokenizer Selection

Different models have different tokenization characteristics. The system supports pluggable tokenizers.

```python
class ModelTokenizer(ABC):
    """Abstract base for model-specific tokenizers."""

    @abstractmethod
    def encode(self, text: str) -> list[int]:
        """Tokenize text into token IDs."""
        pass

    @abstractmethod
    def count(self, text: str) -> int:
        """Count tokens in text."""
        pass


class TikTokenizer(ModelTokenizer):
    """TikToken-based tokenizer for OpenAI models."""

    def __init__(self, model: str):
        self.encoder = tiktoken.encoding_for_model(model)

    def encode(self, text: str) -> list[int]:
        return self.encoder.encode(text)

    def count(self, text: str) -> int:
        return len(self.encode(text))


class CharBasedTokenizer(ModelTokenizer):
    """Fallback char-based tokenizer."""

    def encode(self, text: str) -> list[int]:
        # Return indices instead of actual token IDs
        words = text.split()
        return list(range(len(words)))

    def count(self, text: str) -> int:
        return max(1, len(text) // 4)
```

### 2. Token Budget Allocation Strategy

#### Default Budget Split

The recommended allocation distributes the fixed context window token budget across sections, optimized for typical llms.txt architecture:

```
Total Budget: 16,000 tokens (MAX_CONTEXT_CHARS / 4)

Header:        10% (1,600 tokens)   - Brief intro, model info, constraints
Concepts:      35% (5,600 tokens)   - Definitions, dependencies, anti-patterns
Pages:         25% (4,000 tokens)   - Index summaries, key page info
Examples:      25% (4,000 tokens)   - Q&A pairs, few-shot examples
Footer:         5% (800 tokens)     - Response guidelines, usage notes
```

**Rationale**:
- **Concepts first**: Definitions and dependencies are most critical
- **Pages/Examples equal**: Both inform effective prompt behavior
- **Small header/footer**: Brief framing and closure

#### BudgetConfig Dataclass

Flexible configuration allows custom splits and per-model budgets.

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class BudgetAllocation:
    """Allocation for a single section."""
    header: int = 1600
    concepts: int = 5600
    pages: int = 4000
    examples: int = 4000
    footer: int = 800

    @property
    def total(self) -> int:
        """Total tokens available."""
        return sum([self.header, self.concepts, self.pages,
                   self.examples, self.footer])

    def get_section(self, section: str) -> int:
        """Get allocation for named section."""
        return getattr(self, section.lower())

    def set_section(self, section: str, tokens: int) -> None:
        """Set allocation for named section."""
        setattr(self, section.lower(), tokens)


@dataclass
class BudgetConfig:
    """Configuration for token budgeting."""

    max_tokens: int = 16000
    """Maximum total tokens for context block."""

    allocation: Optional[BudgetAllocation] = None
    """Custom per-section allocation (None = default split)."""

    enable_reallocation: bool = True
    """Enable dynamic reallocation of unused tokens."""

    enable_overflow_handling: bool = True
    """Enable truncation when sections exceed budget."""

    truncation_strategy: str = "drop"
    """Strategy when overflow: 'drop', 'summarize', 'ellipsis'."""

    min_section_tokens: int = 100
    """Minimum tokens to reserve for each section."""

    tokenizer_model: str = "gpt-3.5-turbo"
    """Model for precise tokenization (if tiktoken available)."""

    fallback_to_char_based: bool = True
    """Fall back to char/4 estimation if tiktoken unavailable."""

    def get_allocation(self) -> BudgetAllocation:
        """Get effective allocation (custom or default)."""
        if self.allocation:
            return self.allocation

        # Calculate default split
        header_tokens = int(self.max_tokens * 0.10)
        concepts_tokens = int(self.max_tokens * 0.35)
        pages_tokens = int(self.max_tokens * 0.25)
        examples_tokens = int(self.max_tokens * 0.25)
        footer_tokens = int(self.max_tokens * 0.05)

        return BudgetAllocation(
            header=header_tokens,
            concepts=concepts_tokens,
            pages=pages_tokens,
            examples=examples_tokens,
            footer=footer_tokens
        )
```

### 3. Priority-Based Content Selection

#### Priority System

When budget constraints require truncation, items are selected by priority score.

```python
@dataclass
class ContentItem:
    """Represents a selectable content item."""
    id: str
    """Unique identifier."""

    text: str
    """Content text."""

    priority: float = 1.0
    """Priority score (0-1.0, where 1.0 = highest priority)."""

    category: str = "default"
    """Category for grouping (e.g., 'core', 'extended', 'optional')."""

    tokens: int = 0
    """Pre-calculated token count (optional)."""

    def __lt__(self, other: "ContentItem") -> bool:
        """Enable sorting by priority (descending)."""
        return self.priority > other.priority

    def __repr__(self) -> str:
        return f"ContentItem(id={self.id}, priority={self.priority}, tokens={self.tokens})"


class PrioritySelector:
    """Selects content items within token budget using priority."""

    def __init__(self, tokenizer: ModelTokenizer):
        """
        Initialize selector.

        Args:
            tokenizer: Token counter instance
        """
        self.tokenizer = tokenizer

    def select_items(
        self,
        items: list[ContentItem],
        budget: int
    ) -> tuple[list[ContentItem], int, list[ContentItem]]:
        """
        Select items to fit within budget using priority.

        Args:
            items: Candidate content items
            budget: Token budget to fill

        Returns:
            (selected_items, used_tokens, excluded_items)
        """
        # Sort by priority (descending)
        sorted_items = sorted(items)

        selected = []
        excluded = []
        used_tokens = 0

        for item in sorted_items:
            # Calculate tokens if not pre-calculated
            if item.tokens == 0:
                item.tokens = self.tokenizer.count(item.text)

            if used_tokens + item.tokens <= budget:
                selected.append(item)
                used_tokens += item.tokens
            else:
                excluded.append(item)

        return selected, used_tokens, excluded

    def select_by_category_priority(
        self,
        items: list[ContentItem],
        budget: int,
        category_priority: dict[str, int]
    ) -> tuple[list[ContentItem], dict[str, int]]:
        """
        Select items with category-based priority order.

        Args:
            items: Candidate items
            budget: Token budget
            category_priority: Category → priority (lower number = higher priority)
                Example: {'core': 0, 'extended': 1, 'optional': 2}

        Returns:
            (selected_items, category_token_counts)
        """
        # Group items by category
        by_category = {}
        for item in items:
            category = item.category
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(item)

        # Sort categories by priority
        sorted_categories = sorted(
            by_category.keys(),
            key=lambda c: category_priority.get(c, 999)
        )

        selected = []
        category_counts = {c: 0 for c in by_category.keys()}
        used_tokens = 0

        # Select from highest-priority categories first
        for category in sorted_categories:
            category_items = sorted(by_category[category])

            for item in category_items:
                if item.tokens == 0:
                    item.tokens = self.tokenizer.count(item.text)

                if used_tokens + item.tokens <= budget:
                    selected.append(item)
                    used_tokens += item.tokens
                    category_counts[category] += item.tokens

        return selected, category_counts
```

#### Content Selection Rules

The default priority order ensures most critical content is included first:

```python
class SelectionPriority:
    """Default priority scores for content types."""

    # Concepts section
    CORE_CONCEPT = 1.0          # Essential definitions
    DEPENDENT_CONCEPT = 0.95    # Concepts with dependencies
    ANTI_PATTERN = 0.85         # Common mistakes to avoid
    EXTENDED_CONCEPT = 0.75     # Additional context

    # Pages section
    CORE_PAGE = 1.0             # Critical pages (e.g., main docs)
    HIGH_VALUE_PAGE = 0.80      # High-priority content
    REFERENCE_PAGE = 0.60       # Reference material
    DEPRECATED_PAGE = 0.20      # Deprecated/legacy pages

    # Examples section
    CORE_EXAMPLE = 1.0          # Must-have examples
    RELATED_EXAMPLE = 0.75      # Contextually related examples
    EDGE_CASE_EXAMPLE = 0.50    # Edge case demonstrations

    @staticmethod
    def assign_priorities(
        concepts: list[dict],
        pages: list[dict],
        examples: list[dict]
    ) -> tuple[list[ContentItem], ...]:
        """
        Assign default priorities to all content.

        Returns:
            (concept_items, page_items, example_items)
        """
        # Assign concept priorities
        concept_items = [
            ContentItem(
                id=c.get("id", c.get("term", "unknown")),
                text=c.get("definition", ""),
                priority=SelectionPriority.CORE_CONCEPT
                    if c.get("core", False)
                    else SelectionPriority.EXTENDED_CONCEPT,
                category="concepts"
            )
            for c in concepts
        ]

        # Assign page priorities
        page_items = [
            ContentItem(
                id=p.get("url", p.get("title", "unknown")),
                text=p.get("summary", ""),
                priority=SelectionPriority.CORE_PAGE
                    if p.get("type") in ["main", "core"]
                    else SelectionPriority.REFERENCE_PAGE,
                category="pages"
            )
            for p in pages
        ]

        # Assign example priorities
        example_items = [
            ContentItem(
                id=e.get("id", f"example_{i}"),
                text=e.get("question", "") + "\n" + e.get("answer", ""),
                priority=SelectionPriority.CORE_EXAMPLE
                    if e.get("core", False)
                    else SelectionPriority.RELATED_EXAMPLE,
                category="examples"
            )
            for i, e in enumerate(examples)
        ]

        return concept_items, page_items, example_items
```

### 4. Dynamic Budget Reallocation

#### Reallocation Algorithm

When a section uses less than its allocated budget, remaining tokens can be redistributed to other sections.

```python
class BudgetReallocator:
    """Reallocates unused tokens between sections."""

    def __init__(self, allocation: BudgetAllocation, min_section: int = 100):
        """
        Initialize reallocator.

        Args:
            allocation: Initial budget allocation
            min_section: Minimum tokens to reserve per section
        """
        self.allocation = allocation
        self.min_section = min_section

    def reallocate(
        self,
        section_usage: dict[str, int]
    ) -> dict[str, int]:
        """
        Reallocate unused tokens.

        Args:
            section_usage: Actual usage per section (header, concepts, pages, examples, footer)

        Returns:
            Updated allocation with unused tokens redistributed
        """
        sections = ["header", "concepts", "pages", "examples", "footer"]

        # Calculate unused tokens per section
        unused = {}
        total_unused = 0

        for section in sections:
            used = section_usage.get(section, 0)
            allocated = getattr(self.allocation, section)
            section_unused = max(0, allocated - used)
            unused[section] = section_unused
            total_unused += section_unused

        if total_unused == 0:
            return {s: getattr(self.allocation, s) for s in sections}

        # Identify sections that need more tokens (those under their allocation)
        needing_tokens = [
            s for s in sections
            if section_usage.get(s, 0) > self.min_section
        ]

        if not needing_tokens:
            # No sections need reallocation
            return {s: getattr(self.allocation, s) for s in sections}

        # Redistribute unused tokens proportionally
        reallocated = {}
        tokens_per_section = total_unused // len(needing_tokens)

        for section in sections:
            current = getattr(self.allocation, section)
            if section in needing_tokens:
                reallocated[section] = current + tokens_per_section
            else:
                reallocated[section] = current

        return reallocated

    def reallocate_to_priority_section(
        self,
        section_usage: dict[str, int],
        priority_section: str
    ) -> dict[str, int]:
        """
        Reallocate unused tokens to a specific priority section.

        Args:
            section_usage: Actual usage per section
            priority_section: Section to prioritize (e.g., "concepts")

        Returns:
            Updated allocation with tokens moved to priority section
        """
        sections = ["header", "concepts", "pages", "examples", "footer"]

        # Calculate total unused
        total_unused = 0
        for section in sections:
            used = section_usage.get(section, 0)
            allocated = getattr(self.allocation, section)
            total_unused += max(0, allocated - used)

        # Add all unused to priority section
        reallocated = {}
        for section in sections:
            if section == priority_section:
                reallocated[section] = (
                    getattr(self.allocation, section) + total_unused
                )
            else:
                reallocated[section] = getattr(self.allocation, section)

        return reallocated
```

### 5. Overflow Handling & Truncation Strategies

#### Truncation Strategy Selection

Multiple strategies handle content that exceeds allocated budget.

```python
from enum import Enum
from typing import Callable

class TruncationStrategy(Enum):
    """Strategies for handling content overflow."""

    DROP = "drop"           # Drop lowest-priority items
    SUMMARIZE = "summarize" # Replace with summaries
    ELLIPSIS = "ellipsis"   # Truncate with ellipsis marker
    PRIORITY_CUT = "priority_cut"  # Keep only highest-priority items


class OverflowHandler:
    """Handles content overflow using configurable strategies."""

    def __init__(self, tokenizer: ModelTokenizer):
        """Initialize with tokenizer."""
        self.tokenizer = tokenizer

    def handle_overflow(
        self,
        items: list[ContentItem],
        budget: int,
        strategy: TruncationStrategy = TruncationStrategy.DROP
    ) -> tuple[list[ContentItem], list[ContentItem]]:
        """
        Handle items exceeding budget.

        Args:
            items: Content items to fit
            budget: Token budget
            strategy: Truncation strategy

        Returns:
            (included_items, excluded_items)
        """
        if strategy == TruncationStrategy.DROP:
            return self._drop_strategy(items, budget)
        elif strategy == TruncationStrategy.SUMMARIZE:
            return self._summarize_strategy(items, budget)
        elif strategy == TruncationStrategy.ELLIPSIS:
            return self._ellipsis_strategy(items, budget)
        elif strategy == TruncationStrategy.PRIORITY_CUT:
            return self._priority_cut_strategy(items, budget)
        else:
            return self._drop_strategy(items, budget)  # Default

    def _drop_strategy(
        self,
        items: list[ContentItem],
        budget: int
    ) -> tuple[list[ContentItem], list[ContentItem]]:
        """Drop lowest-priority items until under budget."""
        sorted_items = sorted(items)
        included = []
        used_tokens = 0

        for item in sorted_items:
            if item.tokens == 0:
                item.tokens = self.tokenizer.count(item.text)

            if used_tokens + item.tokens <= budget:
                included.append(item)
                used_tokens += item.tokens

        excluded = [i for i in items if i not in included]
        return included, excluded

    def _summarize_strategy(
        self,
        items: list[ContentItem],
        budget: int
    ) -> tuple[list[ContentItem], list[ContentItem]]:
        """Replace long items with summaries."""
        # Placeholder: summarization requires external service
        # For now, fall back to drop strategy
        return self._drop_strategy(items, budget)

    def _ellipsis_strategy(
        self,
        items: list[ContentItem],
        budget: int
    ) -> tuple[list[ContentItem], list[ContentItem]]:
        """Truncate items with ellipsis marker."""
        included = []
        used_tokens = 0
        excluded = []

        # Sort by priority
        sorted_items = sorted(items)

        for item in sorted_items:
            if item.tokens == 0:
                item.tokens = self.tokenizer.count(item.text)

            # Try to fit item with ellipsis
            ellipsis = " …"
            truncated_text = item.text + ellipsis
            truncated_tokens = self.tokenizer.count(truncated_text)

            if used_tokens + truncated_tokens <= budget:
                # Can fit with ellipsis
                included_item = ContentItem(
                    id=item.id,
                    text=truncated_text,
                    priority=item.priority,
                    category=item.category,
                    tokens=truncated_tokens
                )
                included.append(included_item)
                used_tokens += truncated_tokens
            else:
                excluded.append(item)

        return included, excluded

    def _priority_cut_strategy(
        self,
        items: list[ContentItem],
        budget: int
    ) -> tuple[list[ContentItem], list[ContentItem]]:
        """Keep items above priority threshold."""
        # Default threshold: 0.5 (50% priority)
        threshold = 0.5

        high_priority = [i for i in items if i.priority >= threshold]
        low_priority = [i for i in items if i.priority < threshold]

        included, excluded = self._drop_strategy(high_priority, budget)

        # excluded items go to total excluded list
        excluded.extend(low_priority)

        return included, excluded
```

### 6. Budget Reporting & Observability

#### Budget Report Structure

Comprehensive reporting enables debugging and optimization.

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class SectionTokenReport:
    """Token usage report for a single section."""
    section: str
    allocated: int
    used: int
    items_included: int
    items_excluded: int

    @property
    def utilization(self) -> float:
        """Percentage of allocated budget used."""
        if self.allocated == 0:
            return 0.0
        return (self.used / self.allocated) * 100

    @property
    def headroom(self) -> int:
        """Unused tokens in this section."""
        return max(0, self.allocated - self.used)

    def __repr__(self) -> str:
        return (
            f"{self.section}: {self.used}/{self.allocated} tokens "
            f"({self.utilization:.1f}% used, {self.items_included} items)"
        )


@dataclass
class BudgetReport:
    """Complete budget usage report."""
    timestamp: datetime
    max_tokens: int
    sections: dict[str, SectionTokenReport]
    total_used: int
    reallocations_applied: int
    truncation_strategy_used: Optional[str]
    warnings: list[str] = field(default_factory=list)

    @property
    def total_allocated(self) -> int:
        """Total tokens allocated across all sections."""
        return sum(s.allocated for s in self.sections.values())

    @property
    def total_utilization(self) -> float:
        """Overall utilization percentage."""
        if self.total_allocated == 0:
            return 0.0
        return (self.total_used / self.total_allocated) * 100

    def get_section_report(self, section: str) -> Optional[SectionTokenReport]:
        """Get report for specific section."""
        return self.sections.get(section)

    def summary(self) -> str:
        """Generate human-readable summary."""
        lines = [
            f"Budget Report (generated {self.timestamp.isoformat()})",
            f"Total tokens: {self.total_used}/{self.max_tokens} "
            f"({self.total_utilization:.1f}% utilized)",
            "",
            "Per-section breakdown:"
        ]

        for section, report in self.sections.items():
            lines.append(f"  {report}")

        if self.warnings:
            lines.append("\nWarnings:")
            for warning in self.warnings:
                lines.append(f"  - {warning}")

        return "\n".join(lines)


class BudgetReporter:
    """Generates detailed budget reports."""

    @staticmethod
    def report(
        max_tokens: int,
        allocation: BudgetAllocation,
        section_usage: dict[str, tuple[int, int, int]],
        reallocations: int = 0,
        strategy: Optional[str] = None,
        warnings: Optional[list[str]] = None
    ) -> BudgetReport:
        """
        Generate budget report.

        Args:
            max_tokens: Maximum token budget
            allocation: Budget allocation per section
            section_usage: {section: (allocated, used, items_count)}
            reallocations: Number of reallocations applied
            strategy: Truncation strategy used (if any)
            warnings: Warning messages to include

        Returns:
            BudgetReport instance
        """
        sections = {}
        total_used = 0

        for section in ["header", "concepts", "pages", "examples", "footer"]:
            allocated, used, items_count = section_usage.get(
                section, (0, 0, 0)
            )

            sections[section] = SectionTokenReport(
                section=section,
                allocated=allocated,
                used=used,
                items_included=items_count,
                items_excluded=0  # Could track separately if needed
            )
            total_used += used

        return BudgetReport(
            timestamp=datetime.now(),
            max_tokens=max_tokens,
            sections=sections,
            total_used=total_used,
            reallocations_applied=reallocations,
            truncation_strategy_used=strategy,
            warnings=warnings or []
        )
```

### 7. BudgetEngine Implementation

#### Main Engine Class

Orchestrates all budget operations.

```python
class BudgetEngine:
    """
    Main orchestrator for token budgeting.

    Manages estimation, allocation, selection, reallocation, and reporting.
    """

    def __init__(self, config: BudgetConfig):
        """
        Initialize engine.

        Args:
            config: Budget configuration
        """
        self.config = config

        # Initialize tokenizer
        if config.fallback_to_char_based:
            try:
                self.tokenizer = TikTokenizer(config.tokenizer_model)
            except Exception:
                self.tokenizer = CharBasedTokenizer()
        else:
            self.tokenizer = CharBasedTokenizer()

        # Initialize components
        self.allocator = BudgetAllocation()
        self.selector = PrioritySelector(self.tokenizer)
        self.reallocator = BudgetReallocator(
            self.config.get_allocation(),
            self.config.min_section_tokens
        )
        self.overflow = OverflowHandler(self.tokenizer)

    def estimate_tokens(self, text: str) -> int:
        """Estimate tokens in text."""
        return self.tokenizer.count(text)

    def allocate_budget(self) -> BudgetAllocation:
        """Get effective budget allocation."""
        return self.config.get_allocation()

    def select_content(
        self,
        items: list[ContentItem],
        section_budget: int
    ) -> tuple[list[ContentItem], int]:
        """
        Select items within budget.

        Args:
            items: Candidate items
            section_budget: Token budget for this section

        Returns:
            (selected_items, used_tokens)
        """
        selected, used, excluded = self.selector.select_items(
            items, section_budget
        )
        return selected, used

    def handle_overflow(
        self,
        items: list[ContentItem],
        budget: int
    ) -> tuple[list[ContentItem], list[ContentItem]]:
        """Handle items exceeding budget."""
        strategy = TruncationStrategy(self.config.truncation_strategy)
        return self.overflow.handle_overflow(items, budget, strategy)

    def build_budget_report(
        self,
        section_usage: dict[str, tuple[int, int, int]],
        reallocations: int = 0,
        strategy_used: Optional[str] = None,
        warnings: Optional[list[str]] = None
    ) -> BudgetReport:
        """Generate comprehensive budget report."""
        return BudgetReporter.report(
            self.config.max_tokens,
            self.config.get_allocation(),
            section_usage,
            reallocations,
            strategy_used,
            warnings
        )

    def process_sections(
        self,
        sections_data: dict[str, list[ContentItem]]
    ) -> tuple[dict[str, list[ContentItem]], BudgetReport]:
        """
        Process all sections with budgeting.

        Args:
            sections_data: {section: [items]}

        Returns:
            (processed_sections, report)
        """
        allocation = self.allocate_budget()
        section_usage = {}
        processed = {}
        warnings = []
        reallocations = 0

        # Process each section
        for section in ["header", "concepts", "pages", "examples", "footer"]:
            items = sections_data.get(section, [])
            budget = getattr(allocation, section)

            # Select items
            selected, used = self.select_content(items, budget)
            processed[section] = selected
            section_usage[section] = (budget, used, len(selected))

            if len(selected) < len(items):
                warnings.append(
                    f"{section}: {len(items) - len(selected)} items "
                    f"excluded due to budget constraints"
                )

        # Optionally reallocate unused tokens
        if self.config.enable_reallocation:
            reallocated = self.reallocator.reallocate(
                {k: v[1] for k, v in section_usage.items()}
            )
            reallocations = 1  # Simplified tracking

        # Generate report
        report = self.build_budget_report(
            section_usage,
            reallocations,
            self.config.truncation_strategy,
            warnings
        )

        return processed, report
```

## Deliverables

1. **TokenEstimator class**: Character-based and TikToken-based estimation
2. **BudgetAllocation dataclass**: Per-section budget definition
3. **BudgetConfig dataclass**: Configurable budget settings
4. **PrioritySelector class**: Content selection using priority scores
5. **BudgetReallocator class**: Dynamic token reallocation logic
6. **OverflowHandler class**: Multiple truncation strategies
7. **SectionTokenReport & BudgetReport dataclasses**: Detailed reporting
8. **BudgetEngine class**: Main orchestrator for all budget operations
9. **Complete test suite**: Token estimation, allocation, selection, reallocation, overflow, reporting
10. **Integration guide**: How to integrate with v0.3.2c output formats

## Acceptance Criteria

- Token estimation supports both char/4 and tiktoken-based counting
- Budget allocation splits tokens according to configured percentages
- Priority-based selection respects priority scores and category priority
- Dynamic reallocation correctly redistributes unused tokens
- All three overflow strategies (drop, summarize, ellipsis) are implemented
- Budget reports provide accurate per-section and total utilization metrics
- BudgetEngine coordinates all components in correct sequence
- Test suite covers all estimation methods, allocation scenarios, selection strategies, and reallocation cases
- Configuration is flexible and testable with dataclasses
- Backward-compatible with v0.3.1 loader output and v0.3.2c format engines

## Next Step

Proceed to **v0.3.2b — Section Renderers & Markdown Generation**, which consumes the selected, budgeted content and renders it into formatted sections (markdown, XML, JSON, or plain text).
