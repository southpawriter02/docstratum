# v0.4.3 — Metrics Display

> **Task:** Add comprehensive metrics and analysis to the demo.
> 

---

## Task Overview

---

## Metrics Dashboard

### File: `demo/[metrics.py](http://metrics.py)`

```python
"""Metrics and analysis components."""

import streamlit as st
from typing import Optional
from core.testing import ABTestResult

def render_metrics_row(result: ABTestResult):
    """Render key metrics in a row."""
    cols = st.columns(4)
    
    cols[0].metric(
        "📝 Context Size",
        f"{result.context_tokens:,} tokens",
        help="Tokens added to system prompt"
    )
    
    cols[1].metric(
        "📊 Token Overhead",
        f"+{result.token_overhead:,}",
        delta=f"{result.token_overhead / max(result.baseline.prompt_tokens, 1) * 100:.1f}%",
        delta_color="inverse"
    )
    
    latency_diff = result.docstratum.latency_ms - result.baseline.latency_ms
    cols[2].metric(
        "⏱️ Latency Diff",
        f"{latency_diff:+.0f}ms",
        help="Positive = DocStratum slower"
    )
    
    # Quality score (simple heuristic)
    quality_score = calculate_quality_score(result)
    cols[3].metric(
        "⭐ Quality Score",
        f"{quality_score}/5",
        help="Heuristic based on citations, structure, anti-patterns"
    )

def calculate_quality_score(result: ABTestResult) -> int:
    """Calculate a simple quality score for DocStratum response."""
    score = 0
    response = result.docstratum.response.lower()
    
    # Has URLs
    if "http" in response:
        score += 1
    
    # Has code blocks
    if "```" in response:
        score += 1
    
    # Has numbered steps
    if any(f"{i}." in response for i in range(1, 6)):
        score += 1
    
    # Mentions warnings/anti-patterns
    if any(word in response for word in ['note:', 'warning:', 'avoid', "don't", 'not']):
        score += 1
    
    # Longer than baseline
    if len(result.docstratum.response) > len(result.baseline.response):
        score += 1
    
    return min(score, 5)

def render_token_breakdown(result: ABTestResult):
    """Render detailed token breakdown."""
    st.markdown("### 🔢 Token Breakdown")
    
    data = {
        "Agent": ["Baseline", "DocStratum"],
        "Prompt Tokens": [result.baseline.prompt_tokens, result.docstratum.prompt_tokens],
        "Completion Tokens": [result.baseline.completion_tokens, result.docstratum.completion_tokens],
        "Total Tokens": [
            result.baseline.prompt_tokens + result.baseline.completion_tokens,
            result.docstratum.prompt_tokens + result.docstratum.completion_tokens
        ]
    }
    
    st.dataframe(data, use_container_width=True, hide_index=True)

def render_cost_estimate(result: ABTestResult):
    """Render cost estimate."""
    # GPT-4o-mini pricing (as of 2024)
    INPUT_COST = 0.00015  # per 1K tokens
    OUTPUT_COST = 0.0006  # per 1K tokens
    
    def calc_cost(prompt_tokens: int, completion_tokens: int) -> float:
        return (prompt_tokens / 1000 * INPUT_COST) + (completion_tokens / 1000 * OUTPUT_COST)
    
    baseline_cost = calc_cost(result.baseline.prompt_tokens, result.baseline.completion_tokens)
    docstratum_cost = calc_cost(result.docstratum.prompt_tokens, result.docstratum.completion_tokens)
    
    st.markdown("### 💰 Cost Estimate (GPT-4o-mini)")
    
    cols = st.columns(3)
    cols[0].metric("Baseline", f"${baseline_cost:.6f}")
    cols[1].metric("DocStratum", f"${docstratum_cost:.6f}")
    cols[2].metric("Difference", f"${docstratum_cost - baseline_cost:+.6f}")
```

---

## Integration

Add to [`app.py`](http://app.py):

```python
from demo.metrics import render_metrics_row, render_token_breakdown

# After render_comparison:
st.divider()
render_metrics_row(result)

with st.expander("📊 Detailed Token Analysis"):
    render_token_breakdown(result)
```

---

## 📂 Sub-Part Pages

[v0.4.3a — Metrics Dashboard Layout & Key Indicators](RR-SPEC-v0.4.3a-metrics-dashboard-layout-and-key-indicators.md)

[v0.4.3b — Quality Scoring Engine & Heuristics](RR-SPEC-v0.4.3b-quality-scoring-engine-and-heuristics.md)

[v0.4.3c — Token Analysis & Breakdown Display](RR-SPEC-v0.4.3c-token-analysis-and-breakdown-display.md)

[v0.4.3d — Cost Estimation & Provider Pricing](RR-SPEC-v0.4.3d-cost-estimation-and-provider-pricing.md)

---

## Acceptance Criteria

- [ ]  Metrics row displays 4 key metrics
- [ ]  Token breakdown shows comparison table
- [ ]  Quality score calculated
- [ ]  Metrics update with each test
- [ ]  v0.4.3a: Dashboard layout with 4-column key indicators implemented
- [ ]  v0.4.3b: Quality scoring engine with 5-point heuristic validated
- [ ]  v0.4.3c: Token analysis breakdown with comparison dataframe complete
- [ ]  v0.4.3d: Cost estimation with multi-provider pricing functional