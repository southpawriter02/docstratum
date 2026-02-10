# v0.4.2b — Response Card Rendering & Formatting

> **Task:** Implement the response card component with proper markdown rendering and metrics display. Establish robust rendering logic that handles diverse response content while maintaining consistent visual presentation and accessible metrics.

---

## Objective

Implement the render_response_card() component that transforms response data into visually consistent, properly formatted cards. This sub-part addresses markdown rendering considerations, metrics display design, visual distinction based on response type (baseline vs. enhanced), and comprehensive edge case handling. By establishing a robust card rendering system, we enable reliable display of complex response content with proper formatting while maintaining visual clarity and user accessibility.

---

## Scope Boundaries

| **In Scope** | **Out of Scope** |
|---|---|
| render_response_card() function implementation | CSS styling details or color values |
| Markdown rendering best practices and safety | Actual styling (handled in v0.4.2d) |
| Token and latency metric formatting | Backend token counting algorithms |
| Visual distinction logic (is_enhanced flag) | Data validation or response preprocessing |
| Edge case handling (long text, malformed markdown, missing data) | Performance optimization beyond component |
| Markdown sanitization for security | Caching or session state management |
| Formatting rules for code blocks, lists, links | Integration with response generation systems |
| Responsive layout within card container | Database schema or API design |

---

## Dependency Diagram

```
┌──────────────────────────────────────────────┐
│      render_response_card() Component         │
└────────┬─────────────────────────────────────┘
         │
         ├─ Input: response_data dict
         │         └─ text: str (markdown)
         │         └─ tokens: (prompt, completion) tuple
         │         └─ latency: float (seconds)
         │
         ├─ Processing Pipeline
         │  ├─ Markdown Sanitization (bleach lib)
         │  ├─ Markdown → HTML Conversion (mistune/markdown lib)
         │  ├─ Token Formatting (tokens_display_logic)
         │  └─ Latency Formatting (latency_display_logic)
         │
         ├─ Streamlit Rendering Functions
         │  ├─ st.markdown() — Card header + content
         │  ├─ st.metric() — Token and latency metrics
         │  ├─ st.divider() — Visual separators
         │  └─ st.container() — Card boundary (optional)
         │
         └─ Output: Rendered card in Streamlit
            └─ Visual distinction applied via is_enhanced flag
```

---

## 1. render_response_card() Implementation Details

### 1.1 Function Signature and Structure

```python
def render_response_card(
    response_data: dict,
    card_label: str,
    is_enhanced: bool = False,
    show_metrics: bool = True,
    max_height: str = "500px"
) -> None:
    """
    Render a single response card with markdown content and metrics.

    Args:
        response_data: Dict containing 'text', 'tokens', and 'latency'
        card_label: Label for card header ("Baseline", "DocStratum", etc.)
        is_enhanced: If True, apply enhanced styling (green border vs. red)
        show_metrics: If True, display token and latency metrics below content
        max_height: CSS max-height for scrollable content area (e.g., "500px")

    Raises:
        ValueError: If response_data missing required keys
        TypeError: If any parameter has incorrect type

    Side Effects:
        Renders card container, header, content, and metrics to Streamlit
    """
    # 1. Validate input parameters
    # 2. Sanitize markdown content
    # 3. Render card header with label
    # 4. Render markdown content with height constraint
    # 5. Render metrics row (if show_metrics=True)
    # 6. Apply visual distinction styling
```

### 1.2 Implementation Steps

```python
def render_response_card(
    response_data: dict,
    card_label: str,
    is_enhanced: bool = False,
    show_metrics: bool = True,
    max_height: str = "500px"
) -> None:
    """Render a response card with markdown and metrics."""

    # Step 1: Input validation
    required_keys = {"text", "tokens", "latency"}
    if not isinstance(response_data, dict):
        raise TypeError("response_data must be a dictionary")
    if not required_keys.issubset(response_data.keys()):
        missing = required_keys - set(response_data.keys())
        raise ValueError(f"response_data missing required keys: {missing}")

    # Step 2: Extract data with defaults
    markdown_text = response_data.get("text", "")
    tokens_tuple = response_data.get("tokens", (0, 0))
    latency_sec = response_data.get("latency", 0.0)

    # Step 3: Determine styling class based on is_enhanced
    card_style_class = "docstratum-card-enhanced" if is_enhanced else "baseline-card"

    # Step 4: Render card container with custom HTML/CSS
    st.markdown(
        f"""
        <div class="{card_style_class}">
            <div class="card-header">
                <h3>{card_label}</h3>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Step 5: Render markdown content in scrollable container
    st.markdown(
        f"""
        <div class="card-content" style="max-height: {max_height}; overflow-y: auto;">
            {markdown_text}
        </div>
        """,
        unsafe_allow_html=True
    )

    # Step 6: Render metrics if enabled
    if show_metrics:
        render_card_metrics(tokens_tuple, latency_sec)

    # Step 7: Render divider for visual separation
    st.divider()
```

---

## 2. Markdown Rendering Considerations

### 2.1 Markdown Safety and Sanitization

Streamlit's `st.markdown()` allows unsafe HTML via `unsafe_allow_html=True`, which is necessary for formatting but poses security risks if content is untrusted.

**Sanitization Strategy:**

```python
import bleach
from markdown import markdown

def sanitize_markdown(text: str) -> str:
    """
    Convert markdown to HTML and sanitize dangerous tags.

    Args:
        text: Raw markdown string

    Returns:
        Sanitized HTML string
    """
    # Convert markdown to HTML
    html = markdown(text, extensions=['tables', 'fenced_code', 'codehilite'])

    # Sanitize: allow safe tags only
    allowed_tags = [
        'p', 'br', 'span', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'strong', 'em', 'u', 'code', 'pre', 'blockquote',
        'a', 'ul', 'ol', 'li', 'table', 'thead', 'tbody', 'tr', 'th', 'td'
    ]
    allowed_attrs = {
        'a': ['href', 'title'],
        'code': ['class'],  # For syntax highlighting
        'pre': ['class']
    }

    sanitized = bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs)
    return sanitized
```

### 2.2 Code Block Rendering

Code blocks in markdown need special handling for syntax highlighting:

```python
def render_code_blocks(markdown_text: str) -> str:
    """
    Enhance code blocks with syntax highlighting.

    Args:
        markdown_text: Raw markdown with code blocks (triple backticks)

    Returns:
        Markdown with enhanced code block formatting
    """
    # Use Streamlit's built-in syntax highlighting
    # by converting markdown code blocks to HTML pre/code tags

    import re
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name
    from pygments.formatters import HtmlFormatter

    # Pattern for fenced code blocks: ```language ... ```
    code_block_pattern = r'```(\w+)?\n(.*?)\n```'

    def replace_code_block(match):
        language = match.group(1) or 'text'
        code = match.group(2)

        try:
            lexer = get_lexer_by_name(language)
            formatter = HtmlFormatter(style='default', noclasses=False)
            highlighted = highlight(code, lexer, formatter)
            return f'<div class="code-block">{highlighted}</div>'
        except:
            # Fallback if language not recognized
            return f'<pre><code>{code}</code></pre>'

    return re.sub(code_block_pattern, replace_code_block, markdown_text, flags=re.DOTALL)
```

### 2.3 Link Rendering

Links in responses should open in new tabs to maintain context:

```python
def process_links(html_content: str) -> str:
    """
    Add target="_blank" to all links for consistent behavior.

    Args:
        html_content: HTML string with links

    Returns:
        Modified HTML with target="_blank" on all links
    """
    import re

    # Add target="_blank" to all <a> tags
    def add_target_blank(match):
        tag = match.group(0)
        if 'target=' not in tag:
            tag = tag.replace('<a ', '<a target="_blank" ')
        return tag

    pattern = r'<a\s+[^>]*href=["\'][^"\']*["\'][^>]*>'
    return re.sub(pattern, add_target_blank, html_content)
```

### 2.4 List and Table Rendering

Lists and tables should render with proper formatting:

| Element | Markdown Example | Rendering Considerations |
|---|---|---|
| Unordered List | `- item 1\n- item 2` | Indent properly, use bullet points |
| Ordered List | `1. item 1\n2. item 2` | Number sequentially |
| Table | Pipe-delimited: `\| Header \| Data \|` | Use HTML table tags for consistency |
| Blockquote | `> quoted text` | Indent with left border |
| Line Break | `---` | Render as horizontal divider |

---

## 3. Token Display Formatting

### 3.1 Token Tuple Structure

Tokens are stored as `(prompt_tokens, completion_tokens)` tuple:

```python
def format_tokens_display(tokens_tuple: tuple) -> dict:
    """
    Format token counts for display.

    Args:
        tokens_tuple: (prompt_tokens: int, completion_tokens: int)

    Returns:
        Dict with formatted values for st.metric()
    """
    prompt_tokens, completion_tokens = tokens_tuple

    total_tokens = prompt_tokens + completion_tokens

    return {
        "prompt": prompt_tokens,
        "completion": completion_tokens,
        "total": total_tokens
    }
```

### 3.2 Token Display Pattern

```python
def render_card_metrics(tokens_tuple: tuple, latency_sec: float) -> None:
    """
    Render metrics row with tokens and latency.

    Args:
        tokens_tuple: (prompt_tokens, completion_tokens)
        latency_sec: Response latency in seconds
    """
    if tokens_tuple == (0, 0) or tokens_tuple is None:
        # Show placeholder if tokens unavailable
        st.metric("Tokens", "—")
    else:
        prompt_tokens, completion_tokens = tokens_tuple
        total = prompt_tokens + completion_tokens
        st.metric(
            label="Tokens",
            value=total,
            delta=None,
            help=f"Prompt: {prompt_tokens} | Completion: {completion_tokens}"
        )

    if latency_sec and latency_sec > 0:
        st.metric(
            label="Latency",
            value=f"{latency_sec:.2f}s",
            help="Response generation time"
        )
```

### 3.3 Token Formatting Rules

| Scenario | Display Format | Example |
|---|---|---|
| Valid tokens | `total` (help shows breakdown) | `125` (Help: "Prompt: 50 \| Completion: 75") |
| Zero tokens | `—` (em-dash) | `—` |
| Null/None tokens | `—` | `—` |
| Very large tokens | Abbreviated | `1.2k` (if > 1000) |

---

## 4. Latency Display Design

### 4.1 Latency Formatting

```python
def format_latency_display(latency_sec: float) -> str:
    """
    Format latency value for display with appropriate units.

    Args:
        latency_sec: Latency in seconds (float)

    Returns:
        Formatted string with appropriate units
    """
    if latency_sec is None or latency_sec == 0:
        return "—"

    if latency_sec < 0.001:
        return f"{latency_sec * 1_000_000:.1f}μs"
    elif latency_sec < 1:
        return f"{latency_sec * 1000:.1f}ms"
    elif latency_sec < 60:
        return f"{latency_sec:.2f}s"
    else:
        minutes = latency_sec / 60
        return f"{minutes:.1f}m"
```

### 4.2 Latency Display Rules

| Latency Range | Display Format | Example |
|---|---|---|
| < 1ms | Microseconds (μs) | `500μs` |
| 1ms - 1s | Milliseconds (ms) | `250.5ms` |
| 1s - 60s | Seconds (s) | `2.35s` |
| > 60s | Minutes (m) | `1.5m` |
| Null/0 | Em-dash | `—` |

---

## 5. Visual Distinction Logic (is_enhanced Flag)

### 5.1 Styling Strategy

The is_enhanced flag controls visual distinction between baseline and docstratum responses:

```python
def apply_card_styling(is_enhanced: bool, card_element_id: str) -> str:
    """
    Generate CSS class name based on enhancement status.

    Args:
        is_enhanced: Boolean flag for visual distinction
        card_element_id: Unique ID for this card element

    Returns:
        CSS class name to apply
    """
    if is_enhanced:
        return "card-docstratum-enhanced"  # Green border, highlight
    else:
        return "card-baseline"  # Red/muted border
```

### 5.2 Visual Distinction Elements

| Element | Baseline (is_enhanced=False) | DocStratum (is_enhanced=True) |
|---|---|---|
| Border Color | Red (#cc3333) or muted | Green (#33aa33) |
| Border Width | 2px | 2px |
| Background | Light gray tint | Light green tint |
| Header Text Color | Dark red | Dark green |
| Highlight Accent | Subtle | More prominent |
| Label Font | Regular | Bold or highlighted |

### 5.3 Implementation Pattern

```python
# In CSS (injected via st.markdown with unsafe_allow_html=True)
css_injection = """
<style>
.baseline-card {
    border: 2px solid #cc3333;
    background-color: #fafafa;
    border-radius: 8px;
    padding: 16px;
}

.baseline-card .card-header h3 {
    color: #8b0000;
    margin-top: 0;
}

.docstratum-card-enhanced {
    border: 2px solid #33aa33;
    background-color: #f0f8f0;
    border-radius: 8px;
    padding: 16px;
}

.docstratum-card-enhanced .card-header h3 {
    color: #006600;
    margin-top: 0;
    font-weight: bold;
}
</style>
"""

st.markdown(css_injection, unsafe_allow_html=True)
```

---

## 6. Edge Cases & Robustness

### 6.1 Edge Case Handling Matrix

| Edge Case | Scenario | Handling Strategy | Example |
|---|---|---|---|
| Empty response | response_data["text"] == "" | Display placeholder message | "No response generated" |
| Very long response | text > 10,000 characters | Apply max-height, enable scroll | Scrollable container with "500px" max-height |
| Malformed markdown | Invalid markdown syntax (mismatched ```) | Sanitize and render as plain text | Raw text with basic formatting |
| Missing tokens | tokens_tuple is None | Show "—" placeholder | `—` |
| Missing latency | latency_sec is None or 0 | Show "—" placeholder | `—` |
| Special characters | Unicode, emojis in text | Render safely via HTML encoding | Properly encoded HTML entities |
| Code blocks without language | ` ``` code ``` ` | Use default syntax coloring | Basic gray background |
| Deeply nested lists | 5+ level nesting | Render with indentation limits | Capped at 4 levels |
| Large data URLs | Base64 encoded images | Limit size or show placeholder | "Image too large to display" |
| HTML injection attempts | `<script>alert('xss')</script>` | Bleach sanitization strips tags | Content displayed as text |

### 6.2 Empty Response Handling

```python
def handle_empty_response(response_data: dict) -> bool:
    """
    Check if response is effectively empty.

    Args:
        response_data: Response data dict

    Returns:
        True if response is empty and should show placeholder
    """
    text = response_data.get("text", "").strip()
    if not text or len(text) == 0:
        st.info("No response content generated")
        return True
    return False
```

### 6.3 Very Long Response Handling

```python
def truncate_preview(text: str, max_chars: int = 5000) -> str:
    """
    Truncate long text with indication.

    Args:
        text: Full response text
        max_chars: Maximum characters to display

    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_chars:
        return text

    truncated = text[:max_chars]
    # Find last complete sentence
    last_period = truncated.rfind(".")
    if last_period > max_chars * 0.8:
        truncated = truncated[:last_period + 1]

    return truncated + "\n\n*[Response truncated — see full response below]*"
```

### 6.4 Malformed Markdown Recovery

```python
def sanitize_markdown_safe(text: str) -> str:
    """
    Attempt markdown parsing with fallback to plain text.

    Args:
        text: Raw markdown text that may be malformed

    Returns:
        Safe HTML for rendering
    """
    try:
        # Attempt markdown conversion
        html = markdown(text, extensions=['tables', 'fenced_code'])
        sanitized = bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS)
        return sanitized
    except Exception as e:
        # Log error for debugging
        print(f"Markdown parsing error: {e}")
        # Fallback: return as preformatted text
        import html
        return f"<pre>{html.escape(text)}</pre>"
```

---

## 7. Implementation Checklist

### Phase 1: Core Rendering
- [ ] Implement render_response_card() function signature with validation
- [ ] Implement markdown sanitization using bleach library
- [ ] Implement token formatting and display logic
- [ ] Implement latency formatting and display logic
- [ ] Implement card header rendering with label

### Phase 2: Content Rendering
- [ ] Implement code block syntax highlighting
- [ ] Implement link processing (target="_blank")
- [ ] Implement list and table rendering
- [ ] Implement markdown to HTML conversion pipeline

### Phase 3: Visual Distinction
- [ ] Implement is_enhanced styling logic
- [ ] Define CSS classes for baseline vs. enhanced cards
- [ ] Integrate CSS injection with st.markdown()
- [ ] Test visual distinction in both states

### Phase 4: Edge Case Handling
- [ ] Implement empty response detection and placeholder
- [ ] Implement long response truncation and scrolling
- [ ] Implement malformed markdown recovery
- [ ] Implement special character safe rendering

### Phase 5: Testing
- [ ] Unit tests for formatting functions
- [ ] Integration tests with Streamlit
- [ ] Edge case scenario testing
- [ ] Markdown rendering validation

---

## Deliverables Checklist

- [ ] render_response_card() function implemented with full documentation
- [ ] Markdown sanitization module with bleach integration
- [ ] Code block syntax highlighting implemented
- [ ] Token formatting and display logic implemented
- [ ] Latency formatting and display logic implemented
- [ ] Visual distinction styling implemented (baseline vs. enhanced)
- [ ] CSS injection strategy for Streamlit documented
- [ ] Edge case handling for all identified scenarios
- [ ] Security measures for markdown content documented
- [ ] Test cases for edge cases created

---

## Acceptance Criteria

- [ ] render_response_card() accepts all documented parameters
- [ ] Markdown content renders safely without XSS vulnerabilities
- [ ] Token display shows proper formatting with fallbacks
- [ ] Latency display uses appropriate units (μs, ms, s, m)
- [ ] is_enhanced flag visually distinguishes baseline (red) from docstratum (green)
- [ ] Long responses (>5000 chars) render with scrolling
- [ ] Empty responses show informative placeholder
- [ ] Malformed markdown renders without errors
- [ ] All links open in new tabs (_blank)
- [ ] Code blocks render with syntax highlighting
- [ ] Function documentation includes type hints and examples
- [ ] All edge cases are handled gracefully
- [ ] Component is stateless and re-execution safe

---

## Next Step

→ **v0.4.2c — Analysis Engine & Quality Signals**

Implement the render_analysis() component that detects and displays quality signals (citations, anti-patterns, code examples) by comparing baseline and docstratum responses. Build on the render_response_card() implementation to create automated analysis.
