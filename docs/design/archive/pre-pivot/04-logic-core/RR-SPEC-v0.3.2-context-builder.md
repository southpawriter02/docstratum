# v0.3.2 — Context Builder

> **Task:** Create the function that transforms `LlmsTxt` into a prompt-ready context string.
> 

---

## Task Overview

---

## Design Decisions

---

## Implementation

### File: `core/[context.py](http://context.py)`

```python
"""Context builder for LLM system prompts."""

import logging
from typing import Optional
from schemas import LlmsTxt

logger = logging.getLogger(__name__)

# Rough token estimation: 1 token ≈ 4 characters
MAX_CONTEXT_CHARS = 16000  # ~4000 tokens

def build_context_block(
    llms: LlmsTxt,
    max_examples: int = 3,
    include_pages: bool = True,
    include_concepts: bool = True,
    include_examples: bool = True
) -> str:
    """Transform LlmsTxt into a system prompt context block.
    
    Args:
        llms: Validated LlmsTxt object.
        max_examples: Maximum few-shot examples to include.
        include_pages: Whether to include page summaries.
        include_concepts: Whether to include concept definitions.
        include_examples: Whether to include few-shot examples.
    
    Returns:
        Formatted markdown string for system prompt injection.
    """
    sections = []
    
    # Header
    sections.append(_build_header(llms))
    
    # Concepts (highest priority)
    if include_concepts and llms.concepts:
        sections.append(_build_concepts_section(llms))
    
    # Pages
    if include_pages and llms.pages:
        sections.append(_build_pages_section(llms))
    
    # Few-shot examples
    if include_examples and llms.few_shot_examples:
        sections.append(_build_examples_section(llms, max_examples))
    
    # Instructions footer
    sections.append(_build_footer())
    
    context = "\n\n".join(sections)
    
    # Warn if over budget
    if len(context) > MAX_CONTEXT_CHARS:
        logger.warning(
            f"Context block is {len(context)} chars (~{len(context)//4} tokens), "
            f"exceeds target of {MAX_CONTEXT_CHARS} chars"
        )
    
    logger.info(f"Built context: {len(context)} chars (~{len(context)//4} tokens)")
    return context

def _build_header(llms: LlmsTxt) -> str:
    """Build the header section."""
    return f"""# Documentation Context: {llms.site_name}

- **Source:** {llms.site_url}
- **Last Updated:** {llms.last_updated}
- **Schema Version:** {llms.schema_version}

> You are answering questions about {llms.site_name}. Use ONLY the information provided below. If the answer is not in this context, say "I don't have that information in the documentation.\""""

def _build_concepts_section(llms: LlmsTxt) -> str:
    """Build the concepts section."""
    lines = ["## Core Concepts\n"]
    
    for concept in llms.concepts:
        lines.append(f"### {concept.name}")
        lines.append(f"**Definition:** {concept.definition}\n")
        
        if concept.depends_on:
            deps = ", ".join(concept.depends_on)
            lines.append(f"**Prerequisites:** {deps}\n")
        
        if concept.anti_patterns:
            lines.append("**⚠️ Common Mistakes:**")
            for ap in concept.anti_patterns:
                lines.append(f"- {ap}")
            lines.append("")
    
    return "\n".join(lines)

def _build_pages_section(llms: LlmsTxt) -> str:
    """Build the pages section."""
    lines = ["## Documentation Pages\n"]
    
    # Group by content type
    by_type = {}
    for page in llms.pages:
        by_type.setdefault(page.content_type, []).append(page)
    
    for content_type, pages in by_type.items():
        lines.append(f"### {content_type.title()}s\n")
        for page in pages:
            lines.append(f"- **[{page.title}]({page.url})**")
            lines.append(f"  {page.summary}")
            lines.append(f"  *(Verified: {page.last_verified})*\n")
    
    return "\n".join(lines)

def _build_examples_section(llms: LlmsTxt, max_examples: int) -> str:
    """Build the few-shot examples section."""
    lines = ["## Example Q&A (Follow This Format)\n"]
    
    for example in llms.few_shot_examples[:max_examples]:
        lines.append(f"### Q: {example.question}")
        lines.append(f"**Intent:** {example.intent}\n")
        lines.append("**A:**")
        lines.append(example.ideal_answer)
        lines.append("")
        if example.source_pages:
            sources = ", ".join(example.source_pages)
            lines.append(f"*Sources: {sources}*\n")
        lines.append("---\n")
    
    return "\n".join(lines)

def _build_footer() -> str:
    """Build the instructions footer."""
    return """## Response Guidelines

1. **Cite sources:** Always reference the specific documentation URL.
2. **Follow format:** Structure answers like the examples above.
3. **Be precise:** Use exact terminology from the concepts.
4. **Warn about mistakes:** Mention relevant anti-patterns when applicable.
5. **Acknowledge limits:** If information isn't in this context, say so."""

def estimate_tokens(text: str) -> int:
    """Estimate token count (rough approximation)."""
    return len(text) // 4
```

---

## Testing

### File: `tests/test_[context.py](http://context.py)`

```python
import pytest
from datetime import date
from core.context import build_context_block, estimate_tokens
from schemas import LlmsTxt, CanonicalPage, Concept

def make_test_llms():
    """Create a minimal LlmsTxt for testing."""
    return LlmsTxt(
        site_name="Test Site",
        site_url="https://example.com",
        last_updated=date(2026, 1, 1),
        pages=[
            CanonicalPage(
                url="https://example.com/page",
                title="Test Page",
                content_type="tutorial",
                last_verified=date(2026, 1, 1),
                summary="A test page summary."
            )
        ],
        concepts=[
            Concept(
                id="test-concept",
                name="Test Concept",
                definition="Test Concept is a concept used for testing.",
                anti_patterns=["Don't confuse with production."]
            )
        ]
    )

class TestContextBuilder:
    
    def test_includes_site_name(self):
        llms = make_test_llms()
        context = build_context_block(llms)
        assert "Test Site" in context
    
    def test_includes_concepts(self):
        llms = make_test_llms()
        context = build_context_block(llms)
        assert "Test Concept" in context
        assert "testing" in context.lower()
    
    def test_includes_anti_patterns(self):
        llms = make_test_llms()
        context = build_context_block(llms)
        assert "Common Mistakes" in context
    
    def test_under_token_limit(self):
        llms = make_test_llms()
        context = build_context_block(llms)
        tokens = estimate_tokens(context)
        assert tokens < 8000
    
    def test_can_exclude_sections(self):
        llms = make_test_llms()
        context = build_context_block(
            llms, 
            include_pages=False,
            include_concepts=False
        )
        assert "Test Page" not in context
        assert "Test Concept" not in context
```

---

## 📂 Sub-Part Pages

[v0.3.2a — Token Budget Engine & Priority System](RR-SPEC-v0.3.2a-token-budget-engine.md) — Token estimation methods, budget allocation strategy, priority-based selection, overflow handling, BudgetEngine class

[v0.3.2b — Section Renderers & Markdown Generation](RR-SPEC-v0.3.2b-section-renderers.md) — 5 renderer classes (Header/Concepts/Pages/Examples/Footer), markdown formatting rules, template system

[v0.3.2c — Output Formats & Processing Modes](RR-SPEC-v0.3.2c-output-formats.md) — 4 output formats (markdown/XML/JSON/text), DocStratum Hybrid mode, format validation, FormatEngine

[v0.3.2d — Integration API & Configuration](RR-SPEC-v0.3.2d-integration-api.md) — ContextConfig, builder pattern API, preset configurations, metadata tracking, logging

---

## Acceptance Criteria

- [ ]  `build_context_block()` returns formatted markdown
- [ ]  Output includes concepts, pages, and examples
- [ ]  Token count is under 8000
- [ ]  Anti-patterns are included
- [ ]  All tests pass
- [ ]  **v0.3.2a:** Token budget enforced with priority-based content selection
- [ ]  **v0.3.2b:** All 5 section renderers produce clean markdown
- [ ]  **v0.3.2c:** All 4 output formats produce valid, well-formed output
- [ ]  **v0.3.2d:** Fluent builder API works end-to-end with configuration presets