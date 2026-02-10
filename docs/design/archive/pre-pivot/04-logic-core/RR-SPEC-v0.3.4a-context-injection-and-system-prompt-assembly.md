# Context Injection & System Prompt Assembly

> **v0.3.4a DocStratum Agent — Logic Core**
> Defines how to inject DocStratum llms.txt context into the system prompt and assemble the enhanced prompt that gives the agent domain-specific knowledge.

## Objective

Design context injection that:
- Takes llms.txt content and assembles it into a system prompt
- Manages prompt size constraints (truncation/compression strategies)
- Includes context freshness information (generation timestamp)
- Provides dynamic prompt assembly from reusable components
- Maintains backward compatibility with baseline DocumentationAgent
- Enables side-by-side comparison of baseline vs. DocStratum responses

## Scope Boundaries

**INCLUDES:**
- Context block extraction from llms.txt
- System prompt assembly (role + context + instructions)
- Prompt size management and truncation strategies
- Context freshness tracking and timestamps
- Dynamic component-based prompt building
- Comparison framework (baseline vs. DocStratum)
- Complete create_docstratum_agent() implementation

**EXCLUDES:**
- Web scraping or content fetching
- llms.txt generation (covered in earlier phases)
- Behavioral verification (v0.3.4b covers this)
- Database storage of context
- Caching strategies

---

## Dependency Diagram

```
llms.txt (source documentation)
├── Parse into context_block
├── Extract metadata (version, updated_date)
└── Assemble into system prompt
    ├── HEADER: Role definition
    ├── CONTEXT: The llms.txt content (variable size)
    ├── INSTRUCTIONS: Behavioral rules specific to context
    └── EXAMPLES: Few-shot examples from actual domain

Context-injected System Prompt
└── Pass to DocumentationAgent
    └── Returns AgentResponse (from v0.3.3)
```

---

## 1. Context Block Extraction & Preparation

### Parsing llms.txt

```python
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class ContextMetadata:
    """Metadata about the context block"""
    source_url: Optional[str] = None
    generated_at: Optional[str] = None
    version: Optional[str] = None
    total_tokens: int = 0
    document_count: int = 0

def load_context_block(filepath: str) -> tuple[str, ContextMetadata]:
    """
    Load context block from llms.txt file.

    Args:
        filepath: Path to llms.txt file

    Returns:
        (context_content, metadata)
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Context file not found: {filepath}")

    content = path.read_text(encoding='utf-8')

    # Extract metadata from content (usually in header)
    metadata = _extract_metadata(content)

    return content, metadata

def _extract_metadata(content: str) -> ContextMetadata:
    """Extract metadata from context content"""
    import re

    metadata = ContextMetadata()

    # Try to extract URL
    url_match = re.search(r'^source[:\s]+(.+?)$', content, re.MULTILINE | re.IGNORECASE)
    if url_match:
        metadata.source_url = url_match.group(1).strip()

    # Try to extract generation date
    date_match = re.search(r'generated[:\s]+(\d{4}-\d{2}-\d{2})', content, re.IGNORECASE)
    if date_match:
        metadata.generated_at = date_match.group(1)

    # Try to extract version
    version_match = re.search(r'version[:\s]+v?(\d+\.\d+\.\d+)', content, re.IGNORECASE)
    if version_match:
        metadata.version = version_match.group(1)

    return metadata

# EXAMPLE: Using load_context_block
context, metadata = load_context_block("docs/llms.txt")
print(f"Context size: {len(context)} characters")
print(f"Generated: {metadata.generated_at}")
print(f"Source: {metadata.source_url}")
```

### Token Counting for Context

```python
def estimate_token_count(text: str) -> int:
    """
    Estimate token count for text using character-to-token ratio.

    OpenAI/Anthropic average: ~4 characters per token
    """
    return len(text) // 4

def count_context_tokens(context: str) -> int:
    """Count tokens in context block"""
    return estimate_token_count(context)

# EXAMPLE
context_tokens = count_context_tokens(context)
print(f"Context is ~{context_tokens} tokens")

if context_tokens > 5000:
    print("WARNING: Context is large. Consider compression strategies.")
```

---

## 2. System Prompt Assembly Structure

### Complete Prompt Structure

```python
@dataclass
class SystemPromptComponents:
    """Components that make up the system prompt"""
    header: str              # Role definition
    context_block: str       # The actual llms.txt content
    behavioral_rules: str    # How to use the context
    output_format: str       # Formatting guidelines
    examples: str            # Few-shot examples
    freshness_notice: str    # Date and freshness info

def assemble_docstratum_prompt(
    context_block: str,
    metadata: Optional[ContextMetadata] = None,
    include_examples: bool = True
) -> str:
    """
    Assemble complete DocStratum system prompt.

    Args:
        context_block: The llms.txt content
        metadata: Optional metadata about the context
        include_examples: Whether to include few-shot examples

    Returns:
        Complete system prompt string
    """

    # Build components
    header = _build_header()
    behavioral = _build_behavioral_rules()
    output_fmt = _build_output_format()
    freshness = _build_freshness_notice(metadata)
    examples = _build_examples() if include_examples else ""

    # Assemble into final prompt
    prompt = f"""{header}

{freshness}

DOMAIN CONTEXT
────────────────────────────────────────────────────────────────────────
{context_block}

BEHAVIORAL RULES
────────────────────────────────────────────────────────────────────────
{behavioral}

OUTPUT FORMAT
────────────────────────────────────────────────────────────────────────
{output_fmt}

{examples if examples else ""}
"""

    return prompt.strip()

def _build_header() -> str:
    """Build role definition header"""
    return """You are an expert documentation assistant with comprehensive
knowledge of a specific domain. Your role is to help users understand
and work effectively with this domain's documentation, patterns, and
best practices.

You have access to the domain's llms.txt documentation context below,
which provides the authoritative source for all domain-specific
information."""

def _build_behavioral_rules() -> str:
    """Build context-specific behavioral rules"""
    return """1. CITE YOUR SOURCES
   When answering based on the context below, cite specific URLs
   from the documentation. Examples:
   - "According to [URL], ..."
   - "As shown in the docs at [URL], ..."
   - "[Resource](URL) demonstrates..."

2. REFERENCE DOMAIN TERMINOLOGY
   Use terminology and concepts from the provided context.
   Explain unfamiliar terms before using them.

3. ACKNOWLEDGE PATTERNS AND ANTI-PATTERNS
   If the context describes common patterns, mention them:
   - "The recommended approach is..."
   - "A common pitfall is..."
   - "Best practice in this domain is..."

4. MAINTAIN FRESHNESS AWARENESS
   Remember the context generation date. If relevant:
   - "As of [DATE], ..."
   - "In the current version (as of [DATE]), ..."
   - If you're unsure about updates, say so.

5. FOLLOW FEW-SHOT PATTERNS
   Match the style and depth demonstrated in the examples below.

6. HANDLE UNCERTAINTY ABOUT CONTEXT
   If something is not in the provided context:
   - Say "This isn't covered in the available documentation"
   - Don't invent details or guess
   - Suggest where the user might find the answer"""

def _build_output_format() -> str:
    """Build output format guidelines"""
    return """- Lead with the most relevant context citation
- Organize by domain concepts and structure
- Use code examples or diagrams from the context when relevant
- For complex answers, break into logical sections
- Always indicate confidence (citing sources vs. inference)
- Length: 300-1500 words depending on question complexity"""

def _build_freshness_notice(metadata: Optional[ContextMetadata]) -> str:
    """Build freshness/recency notice"""
    if not metadata or not metadata.generated_at:
        return "This context was provided from documentation sources."

    return f"""CONTEXT FRESHNESS
This domain context was generated on {metadata.generated_at}.
Please consider the possibility of updates after this date."""

def _build_examples() -> str:
    """Build few-shot examples (domain-specific)"""
    return """EXAMPLE: Answering with context citations
────────────────────────────────────────────────────────────────────────
User: "What is the recommended pattern for [concept]?"

You: "According to [URL], the recommended pattern is...
Here's how it differs from the anti-pattern of... [URL shows this]
The key benefit is... as explained in [URL]."

EXAMPLE: Handling out-of-context questions
────────────────────────────────────────────────────────────────────────
User: "How does [external topic] relate to this domain?"

You: "While [external topic] is important in general software, this
domain's documentation doesn't specifically address it. However, [URL]
describes the pattern used here, which handles [specific aspect].""""""
```

---

## 3. Prompt Size Management

### Handling Large Context Blocks

```python
def manage_prompt_size(
    context_block: str,
    max_context_tokens: int = 10000
) -> str:
    """
    Manage context block size, applying strategies if too large.

    Strategies (in order):
    1. Use full context if it fits
    2. Truncate to most important sections
    3. Summarize sections
    4. Use fallback compression
    """

    context_tokens = count_context_tokens(context_block)

    if context_tokens <= max_context_tokens:
        return context_block  # Fits, use as-is

    # Strategy 1: Truncate to key sections
    truncated = _truncate_to_key_sections(context_block, max_context_tokens)
    if len(truncated) > len(context_block) * 0.7:  # Kept 70%+
        return truncated

    # Strategy 2: Compress with summarization
    compressed = _compress_with_summarization(context_block, max_context_tokens)
    return compressed

def _truncate_to_key_sections(context: str, max_tokens: int) -> str:
    """
    Keep only key sections (API reference, core concepts, examples).
    Remove less essential sections (changelog, deprecated features).
    """
    import re

    # Define section priorities
    priority_patterns = [
        (r'^## (Overview|Quick Start)', 1),
        (r'^## (API Reference|Documentation)', 1),
        (r'^## (Core Concepts|Fundamentals)', 1),
        (r'^## (Examples|Patterns)', 1),
        (r'^## (Best Practices|Guidelines)', 2),
        (r'^## (Integration|Installation)', 2),
        (r'^## (Changelog|Version History)', 5),
        (r'^## (Deprecated|Legacy)', 5),
    ]

    lines = context.split('\n')
    sections = []
    current_section = []
    current_priority = 999

    for line in lines:
        # Check if this is a new section header
        new_priority = None
        for pattern, priority in priority_patterns:
            if re.match(pattern, line):
                new_priority = priority
                break

        if new_priority is not None and current_section:
            # Save previous section if it's high priority
            if current_priority <= 2:
                sections.append(('\n'.join(current_section), current_priority))
            current_section = [line]
            current_priority = new_priority
        else:
            current_section.append(line)

    # Build truncated context keeping high-priority sections
    result_lines = []
    token_budget = max_tokens

    for section_text, priority in sorted(sections, key=lambda x: x[1]):
        section_tokens = estimate_token_count(section_text)
        if section_tokens < token_budget:
            result_lines.append(section_text)
            token_budget -= section_tokens
        elif token_budget > 500:  # Keep partial section if room
            result_lines.append(section_text[:token_budget * 4])
            break

    return '\n'.join(result_lines)

def _compress_with_summarization(context: str, max_tokens: int) -> str:
    """
    Compress context using bullet-point summarization.

    Converts sections into compact summaries while preserving key info.
    """

    # Split into sections
    sections = context.split('\n## ')

    compressed_parts = []
    token_budget = max_tokens

    for section in sections:
        lines = section.split('\n')
        header = lines[0]

        # For first section, keep more; for others, extract key points
        if len(compressed_parts) == 0:
            # Keep overview mostly intact
            compressed = '\n'.join(lines[:min(20, len(lines))])
        else:
            # Extract bullets and key sentences
            key_lines = []
            for line in lines:
                if line.startswith('-') or line.startswith('*'):
                    key_lines.append(line)
                elif line.startswith('#') or len(line) > 100:
                    key_lines.append(line)

            compressed = header + '\n' + '\n'.join(key_lines[:10])

        section_tokens = estimate_token_count(compressed)
        if section_tokens < token_budget:
            compressed_parts.append(compressed)
            token_budget -= section_tokens

    result = '\n## '.join(compressed_parts)
    return result
```

### Token Budget Monitoring

```python
def validate_prompt_size(prompt: str) -> dict[str, int]:
    """
    Validate that assembled prompt fits within budget.

    Returns metrics about prompt size.
    """
    total_tokens = estimate_token_count(prompt)

    return {
        "total_tokens": total_tokens,
        "characters": len(prompt),
        "lines": len(prompt.split('\n')),
        "fits_openai": total_tokens < 128000,
        "fits_anthropic": total_tokens < 200000,
        "fits_ollama": total_tokens < 32000,
    }

# EXAMPLE
prompt = assemble_docstratum_prompt(context)
metrics = validate_prompt_size(prompt)

print(f"Prompt size: {metrics['total_tokens']} tokens")
print(f"Fits in Ollama (32K)? {metrics['fits_ollama']}")

if not metrics['fits_openai']:
    print("WARNING: Prompt too large for OpenAI GPT-4!")
```

---

## 4. Dynamic Prompt Assembly

### Component-Based Building

```python
class DocStratumPromptBuilder:
    """Build DocStratum prompts with reusable components"""

    def __init__(self):
        self.header: str = ""
        self.context: str = ""
        self.rules: str = ""
        self.format: str = ""
        self.examples: str = ""
        self.metadata: Optional[ContextMetadata] = None

    def with_header(self, header: str) -> 'DocStratumPromptBuilder':
        """Set role definition header"""
        self.header = header
        return self

    def with_context(self, context: str) -> 'DocStratumPromptBuilder':
        """Set domain context (llms.txt content)"""
        self.context = context
        return self

    def with_context_from_file(self, filepath: str) -> 'DocStratumPromptBuilder':
        """Load context from llms.txt file"""
        self.context, self.metadata = load_context_block(filepath)
        return self

    def with_rules(self, rules: str) -> 'DocStratumPromptBuilder':
        """Set behavioral rules"""
        self.rules = rules
        return self

    def with_default_rules(self) -> 'DocStratumPromptBuilder':
        """Use built-in behavioral rules"""
        self.rules = _build_behavioral_rules()
        return self

    def with_format(self, format: str) -> 'DocStratumPromptBuilder':
        """Set output format guidelines"""
        self.format = format
        return self

    def with_default_format(self) -> 'DocStratumPromptBuilder':
        """Use built-in output format"""
        self.format = _build_output_format()
        return self

    def with_examples(self, examples: str) -> 'DocStratumPromptBuilder':
        """Set few-shot examples"""
        self.examples = examples
        return self

    def with_default_examples(self) -> 'DocStratumPromptBuilder':
        """Use built-in examples"""
        self.examples = _build_examples()
        return self

    def build(self) -> str:
        """Assemble all components into final prompt"""
        if not self.header:
            self.header = _build_header()
        if not self.rules:
            self.rules = _build_behavioral_rules()
        if not self.format:
            self.format = _build_output_format()

        freshness = _build_freshness_notice(self.metadata)

        prompt = f"""{self.header}

{freshness}

DOMAIN CONTEXT
────────────────────────────────────────────────────────────────────────
{self.context}

BEHAVIORAL RULES
────────────────────────────────────────────────────────────────────────
{self.rules}

OUTPUT FORMAT
────────────────────────────────────────────────────────────────────────
{self.format}
"""

        if self.examples:
            prompt += f"\n{self.examples}\n"

        return prompt.strip()

# EXAMPLE: Using the builder
prompt = (DocStratumPromptBuilder()
    .with_context_from_file("docs/llms.txt")
    .with_default_rules()
    .with_default_format()
    .with_default_examples()
    .build())
```

---

## 5. Baseline vs. DocStratum Comparison

### Side-by-Side Structure

```python
def compare_prompts(baseline_prompt: str, docstratum_prompt: str) -> dict:
    """
    Compare baseline and DocStratum prompts.

    Returns metrics showing differences.
    """

    baseline_tokens = estimate_token_count(baseline_prompt)
    docstratum_tokens = estimate_token_count(docstratum_prompt)

    return {
        "baseline": {
            "tokens": baseline_tokens,
            "characters": len(baseline_prompt),
            "lines": len(baseline_prompt.split('\n'))
        },
        "docstratum": {
            "tokens": docstratum_tokens,
            "characters": len(docstratum_prompt),
            "lines": len(docstratum_prompt.split('\n'))
        },
        "difference": {
            "tokens_added": docstratum_tokens - baseline_tokens,
            "percent_increase": ((docstratum_tokens - baseline_tokens) / baseline_tokens * 100)
                                if baseline_tokens > 0 else 0,
            "context_injection_size": docstratum_tokens - baseline_tokens
        }
    }

# EXAMPLE
from v0_3_3b import BASELINE_SYSTEM_PROMPT

comparison = compare_prompts(BASELINE_SYSTEM_PROMPT, docstratum_prompt)
print(f"Baseline: {comparison['baseline']['tokens']} tokens")
print(f"DocStratum: {comparison['docstratum']['tokens']} tokens")
print(f"Increase: {comparison['difference']['percent_increase']:.1f}%")
```

### Prompt Structure Comparison

| Element | Baseline (v0.3.3) | DocStratum (v0.3.4) |
|---------|-------------------|------------------|
| **Header (role)** | Generic assistant | Expert in domain |
| **Context block** | (none) | Full llms.txt |
| **Behavioral rules** | Universal (6 rules) | Same + context-specific |
| **Citations** | General (optional) | Required + URL format |
| **Terminology** | General | Domain-specific |
| **Freshness info** | (none) | "Generated on DATE" |
| **Examples** | Generic | Domain examples |
| **Token budget** | ~800 | ~2600-3600 |

---

## 6. Complete create_docstratum_agent() Factory

### Implementation

```python
def create_docstratum_agent(
    context_path: str,
    provider: str = "openai",
    model: Optional[str] = None,
    temperature: float = 0.7,
    api_key: Optional[str] = None,
    max_context_tokens: int = 10000
) -> DocumentationAgent:
    """
    Factory function to create a DocStratum-enhanced agent.

    Args:
        context_path: Path to llms.txt file
        provider: LLM provider ("openai", "anthropic", "ollama")
        model: Model name (uses provider default if None)
        temperature: Sampling temperature (0.0-1.0)
        api_key: API key (uses env var if None)
        max_context_tokens: Maximum tokens for context (applies truncation)

    Returns:
        DocumentationAgent configured with DocStratum context

    Example:
        agent = create_docstratum_agent("docs/llms.txt", provider="openai")
        response = agent.invoke("How do I use this?")
        print(response.response)
    """

    # Load and prepare context
    context_block, metadata = load_context_block(context_path)
    context_block = manage_prompt_size(context_block, max_context_tokens)

    # Build DocStratum system prompt
    system_prompt = (DocStratumPromptBuilder()
        .with_context(context_block)
        .with_default_rules()
        .with_default_format()
        .with_default_examples()
        .build())

    # Map string provider to enum
    from agent import ProviderType
    provider_enum = ProviderType[provider.upper()]

    # Create and return agent
    return DocumentationAgent(
        system_prompt=system_prompt,
        provider=provider_enum,
        model=model,
        temperature=temperature,
        api_key=api_key
    )

def create_baseline_agent(
    temperature: float = 0.7,
    provider: str = "openai",
    model: Optional[str] = None,
    api_key: Optional[str] = None
) -> DocumentationAgent:
    """
    Factory function to create baseline (control group) agent.

    This agent has NO domain context, making it the control for
    comparing against the DocStratum agent.

    Args:
        temperature: Sampling temperature
        provider: LLM provider
        model: Model name
        api_key: API key

    Returns:
        DocumentationAgent with baseline system prompt
    """

    from v0_3_3b import BASELINE_SYSTEM_PROMPT
    from agent import ProviderType

    provider_enum = ProviderType[provider.upper()]

    return DocumentationAgent(
        system_prompt=BASELINE_SYSTEM_PROMPT,
        provider=provider_enum,
        model=model,
        temperature=temperature,
        api_key=api_key
    )

# EXAMPLE: Create both agents for comparison
baseline_agent = create_baseline_agent()
docstratum_agent = create_docstratum_agent("docs/llms.txt")

# Ask same question to both
question = "What are the core concepts in this domain?"

baseline_response = baseline_agent.invoke(question)
docstratum_response = docstratum_agent.invoke(question)

print("BASELINE:")
print(baseline_response.response)
print("\nDOCSTRATUM:")
print(docstratum_response.response)
```

---

## Deliverables

1. **Context loading and parsing** (load_context_block)
2. **Token counting** (estimate_token_count, validate_prompt_size)
3. **Prompt assembly** (assemble_docstratum_prompt)
4. **Size management** (truncation, compression strategies)
5. **Dynamic builder** (DocStratumPromptBuilder class)
6. **Factory functions** (create_docstratum_agent, create_baseline_agent)
7. **Comparison framework** (compare_prompts)
8. **Freshness tracking** (metadata extraction and notices)

---

## Acceptance Criteria

- [ ] load_context_block() successfully parses llms.txt files
- [ ] Context is counted in tokens accurately (±10%)
- [ ] Assembled prompt contains all required sections
- [ ] Prompt size never exceeds provider context window
- [ ] DocStratumPromptBuilder produces valid prompts
- [ ] create_docstratum_agent() returns DocumentationAgent instance
- [ ] Baseline and DocStratum prompts differ only in context/rules
- [ ] Freshness metadata is included in prompt
- [ ] Comparison framework shows expected size differences
- [ ] Truncation strategy preserves key sections

---

## Next Step

**v0.3.4b — Behavioral Verification & Quality Signals** will define how to verify that DocStratum responses exhibit the expected enhanced behaviors (citations, domain terminology, few-shot patterns).
