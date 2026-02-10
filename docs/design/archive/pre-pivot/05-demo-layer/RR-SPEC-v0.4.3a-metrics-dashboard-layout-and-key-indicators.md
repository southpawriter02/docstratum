# v0.4.3a — Metrics Dashboard Layout & Key Indicators

> **Task**: Design the metrics dashboard layout with key performance indicators for the DocStratum demo. This sub-part establishes the visual structure, component selection, and data presentation conventions for displaying the 4-column metrics row (Context Size, Token Overhead, Latency Diff, Quality Score) using Streamlit's st.metric() components with appropriate formatting and real-time updates.

---

## Objective

Establish a clear, consistent metrics dashboard design that presents the core performance indicators (Context Size, Token Overhead, Latency Diff, Quality Score) in a 4-column layout using Streamlit components. This file defines:

- Dashboard layout structure and component placement within app.py
- Key metric selection rationale and performance importance
- Streamlit st.metric() component configuration and styling
- Data formatting conventions (commas, +/- signs, percentages, units)
- Dashboard positioning in the application flow
- Real-time update strategy and data refresh mechanisms

---

## Scope Boundaries

| **In Scope** | **Out of Scope** |
|---|---|
| Dashboard layout design (4-column metrics row) | Implementing the quality scoring engine (see v0.4.3b) |
| Metric selection rationale and key performance indicators | Token breakdown visualization (see v0.4.3c) |
| st.metric() component configuration and styling | Cost calculation and estimation (see v0.4.3d) |
| Data formatting conventions and display standards | Advanced data visualization (charts, graphs) |
| Dashboard placement within app.py flow | Database integration or data persistence |
| Real-time update strategy and refresh mechanisms | Authentication or user-specific metrics |

---

## Dependency Diagram

```
┌─────────────────────────────────────────────────────────┐
│                  metrics.py Module                      │
│                                                         │
│  render_metrics_row()                                   │
│  ├─ Takes: ABTestResult data                           │
│  ├─ Returns: Streamlit columns with st.metric()        │
│  └─ Calls: _format_context_size()                      │
│             _format_token_overhead()                   │
│             _format_latency_diff()                     │
│             _format_quality_score()                    │
│                                                         │
│  Supporting Functions                                  │
│  ├─ _format_context_size() → "12,345 tokens"           │
│  ├─ _format_token_overhead() → "+5.2%"                │
│  ├─ _format_latency_diff() → "-125ms"                 │
│  └─ _format_quality_score() → "4/5"                   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  app.py Integration                     │
│                                                         │
│  Comparison Expander                                    │
│  ├─ Content Comparison Section                          │
│  ├─ Token Breakdown (v0.4.3c)                           │
│  ├─ Metrics Row (THIS SUB-PART)                        │
│  ├─ Cost Estimate (v0.4.3d)                            │
│  └─ Quality Analysis                                    │
└─────────────────────────────────────────────────────────┘
```

---

## 1. Dashboard Layout Design

### 1.1 Visual Structure

The metrics dashboard uses a **4-column layout** in Streamlit with equal width columns, each displaying one key metric using the `st.metric()` component. This layout is embedded within a Streamlit expander after the main comparison and token breakdown sections.

**ASCII Dashboard Wireframe:**

```
┌─────────────────────────────────────────────────────────────┐
│  📊 Metrics & Analysis                                  [▼] │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌─────────────────┤
│  │  CONTEXT SIZE  │  │ TOKEN OVERHEAD │  │  LATENCY DIFF   │
│  │   12,345 T     │  │     +5.2%      │  │   -125 ms       │
│  │   tokens       │  │   overhead     │  │   faster        │
│  └────────────────┘  └────────────────┘  └─────────────────┤
│                                                              │
│  ┌────────────────┐                                         │
│  │ QUALITY SCORE  │                                         │
│  │     4 / 5      │                                         │
│  │   Excellent    │                                         │
│  └────────────────┘                                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Dashboard Placement in App Flow

The metrics dashboard is positioned **within the "Metrics & Analysis" expander** in app.py, appearing after:

1. Content comparison section
2. Token breakdown table (st.dataframe)
3. **← METRICS ROW GOES HERE (v0.4.3a)**
4. Cost estimate display (v0.4.3d)

**Integration code structure:**

```python
# In app.py, within comparison expander
with st.expander("📊 Metrics & Analysis", expanded=False):
    # 1. Content comparison
    render_content_comparison(baseline_response, docstratum_response)

    st.divider()

    # 2. Token breakdown (v0.4.3c)
    render_token_breakdown(ab_test_result)

    st.divider()

    # 3. Metrics dashboard (v0.4.3a) ← THIS SUB-PART
    render_metrics_row(ab_test_result)

    st.divider()

    # 4. Cost estimation (v0.4.3d)
    render_cost_estimate(ab_test_result)
```

---

## 2. Key Metric Selection Rationale

### 2.1 The 4-Column Metrics

Each metric answers a critical performance question:

| **Metric** | **Question Answered** | **Importance** | **Target Audience** |
|---|---|---|---|
| **Context Size** | How many tokens did the prompt contain? | Understanding baseline complexity | All stakeholders |
| **Token Overhead** | How much extra did DocStratum add? | Cost impact assessment | Product/Eng teams |
| **Latency Diff** | How fast is DocStratum compared to baseline? | Performance impact | Eng/Ops teams |
| **Quality Score** | How good is the DocStratum response? | Feature effectiveness | Product/Users |

### 2.2 Why These 4 Metrics?

**Context Size (Tokens)**
- **Purpose**: Establishes the baseline complexity of the prompt
- **Use case**: Understanding whether the overhead is acceptable for the prompt size
- **Insight**: Larger prompts may have higher absolute overhead but lower percentage overhead

**Token Overhead (%)**
- **Purpose**: Quantifies the efficiency cost of DocStratum's semantic translation
- **Use case**: Deciding whether DocStratum is cost-effective for production
- **Insight**: Overhead < 10% is typically acceptable; > 20% requires optimization

**Latency Difference (ms)**
- **Purpose**: Measures latency impact of the additional processing
- **Use case**: Evaluating real-time application suitability
- **Insight**: Negative values (faster) show DocStratum's efficiency benefits

**Quality Score (1-5)**
- **Purpose**: Summarizes content quality improvement via transparent heuristic
- **Use case**: Assessing value delivered by semantic translation
- **Insight**: Calculated by v0.4.3b; presented here with visual indicator

---

## 3. Streamlit st.metric() Component Usage

### 3.1 Component Configuration

The `st.metric()` function displays a metric with optional delta (change indicator). Each metric uses:

```python
st.metric(
    label="METRIC NAME",
    value=formatted_value,
    delta=delta_value,                  # Optional change indicator
    delta_color="inverse",              # "normal", "inverse", or "off"
    help="Tooltip explaining the metric"
)
```

### 3.2 Metric-Specific Configurations

**Context Size Metric:**

```python
st.metric(
    label="Context Size",
    value=f"{ab_test_result.context_tokens:,}",
    help="Number of tokens in the baseline prompt"
)
```

**Token Overhead Metric:**

```python
overhead_pct = (ab_test_result.token_overhead / ab_test_result.context_tokens) * 100

st.metric(
    label="Token Overhead",
    value=f"+{overhead_pct:.1f}%",
    delta=f"+{ab_test_result.token_overhead} tokens",
    delta_color="inverse",  # Red = cost; inverse makes red normal for comparison
    help="Additional tokens added by DocStratum semantic translation"
)
```

**Latency Difference Metric:**

```python
# latency_diff is negative when DocStratum is faster
st.metric(
    label="Latency Diff",
    value=f"{ab_test_result.latency_diff:.0f}ms",
    delta="faster" if ab_test_result.latency_diff < 0 else "slower",
    delta_color="normal",  # Green = faster (negative)
    help="Latency difference: negative = DocStratum faster"
)
```

**Quality Score Metric:**

```python
quality = ab_test_result.docstratum_metrics.quality_score  # 0-5 score

st.metric(
    label="Quality Score",
    value=f"{quality:.1f}/5",
    help="Quality assessment based on 5-point heuristic (see Quality Scoring Engine)"
)
```

---

## 4. Metric Formatting Conventions

### 4.1 Formatting Standards Table

| **Metric** | **Format Pattern** | **Example** | **Rationale** |
|---|---|---|---|
| Context Size | `{value:,} tokens` | `12,345 tokens` | Thousands separator for readability |
| Token Overhead | `+{pct:.1f}%` | `+5.2%` | 1 decimal place; always show +/- |
| Latency Diff | `{value:.0f}ms` | `-125ms` | No decimals; show +/- and unit |
| Quality Score | `{score:.1f}/5` | `4.0/5` | 1 decimal place; clear denominator |

### 4.2 Formatting Implementation

```python
# metrics.py formatting helper functions

def format_context_size(tokens: int) -> str:
    """Format context size with thousands separator."""
    return f"{tokens:,}"

def format_token_overhead(overhead: int, context_tokens: int) -> tuple[str, str]:
    """
    Format token overhead as percentage and absolute value.
    Returns: (value_str, delta_str) for st.metric()
    """
    pct = (overhead / context_tokens * 100) if context_tokens > 0 else 0
    return f"+{pct:.1f}%", f"+{overhead} tokens"

def format_latency_diff(latency_ms: float) -> tuple[str, str]:
    """
    Format latency difference with sign.
    Returns: (value_str, delta_str) for st.metric()
    """
    sign = "-" if latency_ms < 0 else "+" if latency_ms > 0 else ""
    value_str = f"{sign}{abs(latency_ms):.0f}ms"
    delta_str = "faster" if latency_ms < 0 else "slower" if latency_ms > 0 else "same"
    return value_str, delta_str

def format_quality_score(score: float) -> str:
    """Format quality score on 1-5 scale."""
    return f"{score:.1f}/5"
```

### 4.3 Sign and Symbol Conventions

- **Tokens**: Always use thousands separator (`,`)
- **Percentages**: Always show `+` or `-` prefix; format to 1 decimal place
- **Latency**: Always show `+` or `-` prefix and unit (`ms`)
- **Quality**: Use `/5` denominator; always 1 decimal place

---

## 5. Dashboard Placement and App Flow Integration

### 5.1 Placement Context

The metrics dashboard is placed **within the Comparison Expander** to keep all A/B test results grouped together. This organization:

1. **Reduces cognitive load**: All comparison data in one place
2. **Maintains visual hierarchy**: Dashboard expands after token breakdown
3. **Supports progressive disclosure**: Users expand section only if interested
4. **Enables future grouping**: Cost, tokens, and quality metrics all together

### 5.2 Section Ordering Rationale

```
Comparison Expander
├─ Content Comparison (what changed?)
│  └─ Shows original vs. translated text
│
├─ Token Breakdown (how many tokens?)
│  └─ Table: baseline vs. docstratum tokens
│
├─ Metrics Dashboard ← THIS SUB-PART (key indicators)
│  └─ 4-column layout: Context, Overhead, Latency, Quality
│
└─ Cost Estimate (what's the cost?)
   └─ Price breakdown for both agents
```

This ordering follows a **measurement narrative**: context → overhead → performance → quality → cost.

### 5.3 Code Integration Point

```python
# In app.py, st.metric() renders in columns
with st.expander("📊 Metrics & Analysis", expanded=False):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Context Size",
            value=f"{ab_test_result.context_tokens:,}"
        )

    with col2:
        overhead_val, overhead_delta = format_token_overhead(
            ab_test_result.token_overhead,
            ab_test_result.context_tokens
        )
        st.metric(
            label="Token Overhead",
            value=overhead_val,
            delta=overhead_delta,
            delta_color="inverse"
        )

    with col3:
        latency_val, latency_delta = format_latency_diff(
            ab_test_result.latency_diff
        )
        st.metric(
            label="Latency Diff",
            value=latency_val,
            delta=latency_delta,
            delta_color="normal"
        )

    with col4:
        st.metric(
            label="Quality Score",
            value=format_quality_score(
                ab_test_result.docstratum_metrics.quality_score
            )
        )
```

---

## 6. Real-Time Update Strategy

### 6.1 Data Refresh Mechanisms

The metrics dashboard supports real-time updates through Streamlit's reactive architecture:

**Automatic Updates:**
- Metrics refresh whenever `ABTestResult` object changes
- No explicit refresh button needed (Streamlit reruns script on input change)
- User interaction (changing prompt, model, etc.) triggers automatic rerun

**Data Flow:**

```
User Input Change
        │
        ▼
A/B Test Execution
        │
        ▼
ABTestResult Object Updated
        │
        ▼
render_metrics_row() Called
        │
        ▼
st.metric() Components Rerender
```

### 6.2 Caching Strategy (Optional)

For expensive calculations, use `@st.cache_data`:

```python
@st.cache_data(ttl=3600)  # Cache for 1 hour
def format_token_overhead_cached(overhead: int, context_tokens: int) -> tuple[str, str]:
    """Cache overhead formatting calculations."""
    pct = (overhead / context_tokens * 100) if context_tokens > 0 else 0
    return f"+{pct:.1f}%", f"+{overhead} tokens"
```

### 6.3 Update Frequency Considerations

| **Scenario** | **Update Frequency** | **Rationale** |
|---|---|---|
| User modifies prompt | Immediate | Triggers new A/B test |
| Model selection changes | Immediate | New model = different tokens |
| Demo loads page | Immediate | Initial data load |
| Large corpus selection | Delayed (1-2s) | Allows debouncing |

---

## Deliverables Checklist

- [ ] Dashboard layout design complete (4-column metrics row)
- [ ] Metric selection rationale documented with importance assessment
- [ ] st.metric() component configuration finalized for each metric
- [ ] Data formatting conventions established (commas, +/-, percentages, units)
- [ ] Dashboard placement in app.py structure defined
- [ ] Real-time update strategy documented
- [ ] Formatting helper functions implemented in metrics.py
- [ ] Integration code example provided
- [ ] ASCII wireframe/diagram created
- [ ] Metrics specification table completed

---

## Acceptance Criteria

- [ ] 4-column layout renders correctly in Streamlit with equal-width columns
- [ ] All four metrics display with appropriate formatting (Context Size, Token Overhead, Latency Diff, Quality Score)
- [ ] Token Overhead shows percentage with +/- sign; includes delta value
- [ ] Latency Diff shows negative values for faster performance; includes direction indicator
- [ ] Quality Score displays as "X.X/5" format from v0.4.3b scoring engine
- [ ] Metrics update in real-time when ABTestResult object changes
- [ ] All help text is clear and explains metric importance
- [ ] No console errors or Streamlit warnings during rendering
- [ ] Dashboard layout matches wireframe design
- [ ] Formatting conventions are consistent across all four metrics

---

## Next Step

→ **v0.4.3b — Quality Scoring Engine & Heuristics**

Implement the `calculate_quality_score()` function that powers the Quality Score metric. This sub-part defines the 5-point scoring heuristic (URLs, code blocks, numbered steps, warnings/anti-patterns, length comparison) and provides the transparency rules that make quality assessment user-understandable.

