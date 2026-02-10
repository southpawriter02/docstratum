# v0.4.2 — Side-by-Side View

> **Task:** Implement the comparison display with proper formatting.
> 

---

## Task Overview

---

## Enhanced Components

### File: `demo/[components.py](http://components.py)`

```python
"""Reusable UI components for the demo."""

import streamlit as st
from core.testing import ABTestResult

def render_response_card(
    title: str,
    response: str,
    tokens: tuple[int, int],
    latency_ms: float,
    is_enhanced: bool = False
):
    """Render a response card with styling."""
    icon = "✅" if is_enhanced else "❌"
    color = "green" if is_enhanced else "red"
    
    st.markdown(f"### {icon} {title}")
    
    # Response container
    with st.container():
        st.markdown(response)
    
    # Metrics
    cols = st.columns(3)
    cols[0].metric("Prompt", f"{tokens[0]:,}")
    cols[1].metric("Completion", f"{tokens[1]:,}")
    cols[2].metric("Latency", f"{latency_ms:.0f}ms")

def render_comparison(result: ABTestResult):
    """Render full side-by-side comparison."""
    st.markdown(f"### 🔍 Question")
    st.info(result.question)
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        render_response_card(
            title="Baseline Agent",
            response=result.baseline.response,
            tokens=(result.baseline.prompt_tokens, result.baseline.completion_tokens),
            latency_ms=result.baseline.latency_ms,
            is_enhanced=False
        )
    
    with col2:
        render_response_card(
            title="DocStratum Agent",
            response=result.docstratum.response,
            tokens=(result.docstratum.prompt_tokens, result.docstratum.completion_tokens),
            latency_ms=result.docstratum.latency_ms,
            is_enhanced=True
        )

def render_analysis(result: ABTestResult):
    """Render analysis section."""
    st.markdown("### 📈 Analysis")
    
    # Check for improvements
    checks = []
    
    # Citation check
    if "http" in result.docstratum.response and "http" not in result.baseline.response:
        checks.append(("✅", "DocStratum cites specific URLs"))
    
    # Anti-pattern check
    if any(word in result.docstratum.response.lower() for word in ['not', "don't", 'avoid', 'mistake']):
        checks.append(("✅", "DocStratum mentions anti-patterns"))
    
    # Code check
    if "```" in result.docstratum.response:
        checks.append(("✅", "DocStratum includes code examples"))
    
    if checks:
        for icon, text in checks:
            st.markdown(f"{icon} {text}")
    else:
        st.markdown("No clear improvements detected in this response.")
```

---

## Updated [`app.py`](http://app.py)

Replace the display section with:

```python
# Display results
if 'last_result' in st.session_state:
    result = st.session_state.last_result
    
    st.divider()
    
    # Import and use components
    from demo.components import render_comparison, render_analysis
    
    render_comparison(result)
    
    st.divider()
    
    render_analysis(result)
```

---

## Visual Improvements

### CSS Updates

```python
st.markdown("""
<style>
/* Response cards */
[data-testid="stVerticalBlock"] > div:has(> [data-testid="stMarkdown"] > h3:contains("Baseline")) {
    background: linear-gradient(to right, #fff5f5, #fff);
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #e53e3e;
}

[data-testid="stVerticalBlock"] > div:has(> [data-testid="stMarkdown"] > h3:contains("DocStratum")) {
    background: linear-gradient(to right, #f0fff4, #fff);
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #38a169;
}

/* Metrics */
[data-testid="stMetricValue"] {
    font-size: 1.5rem;
}
</style>
""", unsafe_allow_html=True)
```

---

## 📂 Sub-Part Pages

[v0.4.2a — Component Architecture & Reusable Patterns](RR-SPEC-v0.4.2a-component-architecture-and-reusable-patterns.md)

[v0.4.2b — Response Card Rendering & Formatting](RR-SPEC-v0.4.2b-response-card-rendering-and-formatting.md)

[v0.4.2c — Analysis Engine & Quality Signals](RR-SPEC-v0.4.2c-analysis-engine-and-quality-signals.md)

[v0.4.2d — Visual Design System & CSS Architecture](RR-SPEC-v0.4.2d-visual-design-system-and-css-architecture.md)

---

## Acceptance Criteria

- [ ]  Side-by-side columns display correctly
- [ ]  Responses are readable and formatted
- [ ]  Token counts show for both agents
- [ ]  Latency displays in milliseconds
- [ ]  Visual distinction between baseline/enhanced
- [ ]  v0.4.2a: Component architecture documented, reusable patterns established
- [ ]  v0.4.2b: Response cards render markdown correctly with metrics
- [ ]  v0.4.2c: Analysis engine detects citations, anti-patterns, and code blocks
- [ ]  v0.4.2d: CSS design system implemented with baseline/enhanced theming