# v0.4.3c — Token Analysis & Breakdown Display

> **Task**: Build the detailed token analysis display with comparison tables showing prompt vs completion tokens for baseline and DocStratum agents. This sub-part implements `render_token_breakdown()` using Streamlit's st.dataframe() component with formatted tables, overhead calculations, token efficiency metrics, and optional visualization (bar charts) that feed into the dashboard metrics (v0.4.3a) and cost estimation (v0.4.3d).

---

## Objective

Establish a transparent token analysis display that breaks down the token consumption of baseline and DocStratum responses by prompt (input) and completion (output) tokens. This file defines:

- Token breakdown data structure (prompt vs completion for both agents)
- `render_token_breakdown()` implementation using st.dataframe()
- Token comparison visualization options (tables, bar charts)
- Overhead calculation formula and display strategy
- Token efficiency metrics and ratios
- Data export considerations for production analysis

---

## Scope Boundaries

| **In Scope** | **Out of Scope** |
|---|---|
| Token breakdown data structure design | Advanced visualization (interactive charts, 3D plots) |
| `render_token_breakdown()` table rendering | Streaming token count (real-time token updates) |
| Prompt vs completion token separation | Token counting algorithm implementation |
| Overhead calculation formula | External token counting service integration |
| Token efficiency metrics (efficiency ratio) | Machine learning-based token prediction |
| Dataframe formatting and styling | Database storage of token data |
| Optional bar chart visualization | User-specific token quotas or limits |
| CSV export capability for analysis | Token rate limiting or throttling |

---

## Dependency Diagram

```
┌─────────────────────────────────────────────────────────┐
│          ABTestResult Data Model                        │
│                                                         │
│  ├─ context_tokens: int (baseline prompt tokens)        │
│  ├─ baseline_tokens: int (total baseline tokens)        │
│  ├─ docstratum_tokens: int (total DocStratum tokens)         │
│  ├─ token_overhead: int (docstratum - baseline)            │
│  │                                                      │
│  └─ Breakdown details:                                 │
│     ├─ baseline_prompt_tokens: int                      │
│     ├─ baseline_completion_tokens: int                  │
│     ├─ docstratum_prompt_tokens: int                       │
│     └─ docstratum_completion_tokens: int                   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│     render_token_breakdown()                            │
│                                                         │
│  1. Build dataframe from token data                     │
│  2. Format columns (with commas, +/- signs)            │
│  3. Render with st.dataframe()                         │
│  4. Optional: Bar chart comparison                      │
│  5. Optional: Export button (CSV)                       │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│     Metrics Dashboard (v0.4.3a)                         │
│                                                         │
│  ├─ Token Overhead metric (-+5.2%)                      │
│  ├─ Context Size metric (12,345 tokens)                │
│  └─ Shows aggregated token data                        │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│     Cost Estimation (v0.4.3d)                           │
│                                                         │
│  ├─ Uses token counts to calculate costs               │
│  ├─ Baseline cost = baseline_tokens × rate              │
│  ├─ DocStratum cost = docstratum_tokens × rate                │
│  └─ Overhead cost = token_overhead × rate               │
└─────────────────────────────────────────────────────────┘
```

---

## 1. Token Breakdown Data Structure

### 1.1 Data Model Definition

```python
# In data models (pydantic)

from pydantic import BaseModel

class TokenBreakdown(BaseModel):
    """Detailed token breakdown for a single agent response."""
    prompt_tokens: int
    completion_tokens: int

    @property
    def total_tokens(self) -> int:
        """Total tokens = prompt + completion."""
        return self.prompt_tokens + self.completion_tokens

class ABTestResult(BaseModel):
    """A/B test result with token breakdown."""
    # Metadata
    query: str
    baseline_model: str
    docstratum_model: str
    timestamp: str

    # Token counts
    context_tokens: int  # Baseline prompt tokens
    baseline_tokens: int  # Total baseline tokens (prompt + completion)
    docstratum_tokens: int  # Total DocStratum tokens (prompt + completion)
    token_overhead: int  # docstratum_tokens - baseline_tokens

    # Token breakdown details
    baseline_breakdown: TokenBreakdown
    docstratum_breakdown: TokenBreakdown

    # Latency and metrics
    latency_diff: float  # milliseconds
    baseline_metrics: dict
    docstratum_metrics: dict

    @property
    def token_overhead_pct(self) -> float:
        """Overhead as percentage of baseline."""
        if self.baseline_tokens == 0:
            return 0.0
        return (self.token_overhead / self.baseline_tokens) * 100

    @property
    def baseline_prompt_ratio(self) -> float:
        """Baseline prompt tokens as % of total."""
        if self.baseline_tokens == 0:
            return 0.0
        return (self.baseline_breakdown.prompt_tokens / self.baseline_tokens) * 100

    @property
    def docstratum_prompt_ratio(self) -> float:
        """DocStratum prompt tokens as % of total."""
        if self.docstratum_tokens == 0:
            return 0.0
        return (self.docstratum_breakdown.prompt_tokens / self.docstratum_tokens) * 100
```

### 1.2 Token Data Flow

```
Raw API Response (from LLM)
├─ Baseline API: {"usage": {"prompt_tokens": 500, "completion_tokens": 200}}
└─ DocStratum API: {"usage": {"prompt_tokens": 525, "completion_tokens": 210}}
        │
        ▼
Parse Token Counts
├─ baseline_prompt_tokens = 500
├─ baseline_completion_tokens = 200
├─ docstratum_prompt_tokens = 525
└─ docstratum_completion_tokens = 210
        │
        ▼
Calculate Totals
├─ baseline_tokens = 500 + 200 = 700
├─ docstratum_tokens = 525 + 210 = 735
├─ context_tokens = 500 (same as baseline prompt)
└─ token_overhead = 735 - 700 = 35
        │
        ▼
Store in ABTestResult
├─ baseline_breakdown: TokenBreakdown(prompt=500, completion=200)
├─ docstratum_breakdown: TokenBreakdown(prompt=525, completion=210)
└─ token_overhead: 35
```

---

## 2. Token Breakdown Table Layout

### 2.1 Dataframe Structure

The token breakdown is displayed as a simple 3-column table using st.dataframe():

| **Category** | **Baseline** | **DocStratum** |
|---|---|---|
| Prompt Tokens | 500 | 525 |
| Completion Tokens | 200 | 210 |
| **Total Tokens** | **700** | **735** |
| Overhead | — | +35 (+5.0%) |

### 2.2 Data Preparation

```python
# metrics.py - Token breakdown function

import pandas as pd
import streamlit as st
from typing import Optional

def prepare_token_breakdown_dataframe(ab_test_result: ABTestResult) -> pd.DataFrame:
    """
    Prepare token breakdown data for st.dataframe() display.

    Returns:
        DataFrame with rows: Prompt, Completion, Total, Overhead
    """
    baseline_prompt = ab_test_result.baseline_breakdown.prompt_tokens
    baseline_completion = ab_test_result.baseline_breakdown.completion_tokens
    baseline_total = ab_test_result.baseline_tokens

    docstratum_prompt = ab_test_result.docstratum_breakdown.prompt_tokens
    docstratum_completion = ab_test_result.docstratum_breakdown.completion_tokens
    docstratum_total = ab_test_result.docstratum_tokens

    # Calculate overhead
    prompt_overhead = docstratum_prompt - baseline_prompt
    completion_overhead = docstratum_completion - baseline_completion
    total_overhead = ab_test_result.token_overhead
    total_overhead_pct = ab_test_result.token_overhead_pct

    data = {
        'Category': [
            'Prompt Tokens',
            'Completion Tokens',
            'Total Tokens',
            'Overhead'
        ],
        'Baseline': [
            f"{baseline_prompt:,}",
            f"{baseline_completion:,}",
            f"{baseline_total:,}",
            '—'
        ],
        'DocStratum': [
            f"{docstratum_prompt:,}",
            f"{docstratum_completion:,}",
            f"{docstratum_total:,}",
            f"+{total_overhead:,} (+{total_overhead_pct:.1f}%)"
        ],
        'Difference': [
            f"+{prompt_overhead:,}" if prompt_overhead > 0 else f"{prompt_overhead:,}",
            f"+{completion_overhead:,}" if completion_overhead > 0 else f"{completion_overhead:,}",
            f"+{total_overhead:,}" if total_overhead > 0 else f"{total_overhead:,}",
            ''
        ]
    }

    df = pd.DataFrame(data)
    return df
```

### 2.3 Rendering Function

```python
def render_token_breakdown(ab_test_result: ABTestResult) -> None:
    """
    Render token breakdown table in Streamlit.
    """
    st.subheader("Token Breakdown")

    # Prepare dataframe
    df = prepare_token_breakdown_dataframe(ab_test_result)

    # Display with st.dataframe()
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            'Category': st.column_config.TextColumn(width='medium'),
            'Baseline': st.column_config.TextColumn(width='medium'),
            'DocStratum': st.column_config.TextColumn(width='medium'),
            'Difference': st.column_config.TextColumn(width='medium')
        }
    )

    # Summary info
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Baseline Total",
            f"{ab_test_result.baseline_tokens:,}",
            help="Total tokens used by baseline response"
        )

    with col2:
        st.metric(
            "DocStratum Total",
            f"{ab_test_result.docstratum_tokens:,}",
            help="Total tokens used by DocStratum response"
        )

    with col3:
        st.metric(
            "Overhead",
            f"+{ab_test_result.token_overhead:,}",
            f"{ab_test_result.token_overhead_pct:.1f}%",
            help="Additional tokens used by DocStratum"
        )
```

---

## 3. Token Comparison Visualization

### 3.1 Bar Chart Option

Optional visualization comparing token counts side-by-side:

```python
def render_token_comparison_chart(ab_test_result: ABTestResult) -> None:
    """
    Optional: Render token comparison as bar chart.
    """
    import matplotlib.pyplot as plt

    labels = ['Prompt', 'Completion', 'Total']
    baseline_vals = [
        ab_test_result.baseline_breakdown.prompt_tokens,
        ab_test_result.baseline_breakdown.completion_tokens,
        ab_test_result.baseline_tokens
    ]
    docstratum_vals = [
        ab_test_result.docstratum_breakdown.prompt_tokens,
        ab_test_result.docstratum_breakdown.completion_tokens,
        ab_test_result.docstratum_tokens
    ]

    x = range(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar([i - width/2 for i in x], baseline_vals, width, label='Baseline', color='#1f77b4')
    ax.bar([i + width/2 for i in x], docstratum_vals, width, label='DocStratum', color='#ff7f0e')

    ax.set_xlabel('Token Type')
    ax.set_ylabel('Token Count')
    ax.set_title('Token Breakdown: Baseline vs DocStratum')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    st.pyplot(fig)
```

### 3.2 Pie Chart Option (Breakdown)

Show composition of DocStratum tokens:

```python
def render_token_composition_pie(ab_test_result: ABTestResult) -> None:
    """
    Optional: Render DocStratum token composition as pie chart.
    """
    import matplotlib.pyplot as plt

    prompt = ab_test_result.docstratum_breakdown.prompt_tokens
    completion = ab_test_result.docstratum_breakdown.completion_tokens

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        [prompt, completion],
        labels=['Prompt', 'Completion'],
        autopct='%1.1f%%',
        colors=['#1f77b4', '#ff7f0e']
    )
    ax.set_title('DocStratum Token Composition')

    st.pyplot(fig)
```

---

## 4. Overhead Calculation Formula

### 4.1 Token Overhead Formula

```
Token Overhead (absolute) = DocStratum Total - Baseline Total
                          = (docstratum_prompt + docstratum_completion)
                            - (baseline_prompt + baseline_completion)

Token Overhead (%) = (Token Overhead / Baseline Total) × 100
                   = (docstratum_total - baseline_total) / baseline_total × 100

Example:
Baseline: 500 prompt + 200 completion = 700 total
DocStratum:  525 prompt + 210 completion = 735 total

Overhead (absolute) = 735 - 700 = 35 tokens
Overhead (%) = (35 / 700) × 100 = 5.0%
```

### 4.2 Per-Component Overhead

```
Prompt Overhead = DocStratum Prompt - Baseline Prompt
                = 525 - 500 = 25 tokens (5.0% increase)

Completion Overhead = DocStratum Completion - Baseline Completion
                    = 210 - 200 = 10 tokens (5.0% increase)

Total Overhead = 25 + 10 = 35 tokens
```

### 4.3 Implementation

```python
def calculate_overhead(ab_test_result: ABTestResult) -> dict:
    """Calculate token overhead metrics."""
    baseline_total = ab_test_result.baseline_tokens
    docstratum_total = ab_test_result.docstratum_tokens

    abs_overhead = docstratum_total - baseline_total
    pct_overhead = (abs_overhead / baseline_total * 100) if baseline_total > 0 else 0

    prompt_overhead = (
        ab_test_result.docstratum_breakdown.prompt_tokens -
        ab_test_result.baseline_breakdown.prompt_tokens
    )
    completion_overhead = (
        ab_test_result.docstratum_breakdown.completion_tokens -
        ab_test_result.baseline_breakdown.completion_tokens
    )

    return {
        'absolute_overhead': abs_overhead,
        'percentage_overhead': pct_overhead,
        'prompt_overhead': prompt_overhead,
        'completion_overhead': completion_overhead
    }
```

---

## 5. Token Efficiency Metrics

### 5.1 Efficiency Ratio

**Definition**: How many output tokens are produced per input token?

```
Efficiency Ratio = Completion Tokens / Prompt Tokens

Baseline Efficiency = baseline_completion / baseline_prompt
DocStratum Efficiency = docstratum_completion / docstratum_prompt

Example:
Baseline: 200 completion / 500 prompt = 0.40 (40% of prompt length)
DocStratum:  210 completion / 525 prompt = 0.40 (40% of prompt length)

Result: Same efficiency despite 5% token overhead (acceptable trade-off)
```

### 5.2 Token Efficiency Table

```python
def render_token_efficiency(ab_test_result: ABTestResult) -> None:
    """Display token efficiency metrics."""
    baseline_ratio = (
        ab_test_result.baseline_breakdown.completion_tokens /
        ab_test_result.baseline_breakdown.prompt_tokens
        if ab_test_result.baseline_breakdown.prompt_tokens > 0
        else 0.0
    )

    docstratum_ratio = (
        ab_test_result.docstratum_breakdown.completion_tokens /
        ab_test_result.docstratum_breakdown.prompt_tokens
        if ab_test_result.docstratum_breakdown.prompt_tokens > 0
        else 0.0
    )

    efficiency_data = {
        'Metric': [
            'Output/Input Ratio',
            'Prompt % of Total',
            'Completion % of Total'
        ],
        'Baseline': [
            f"{baseline_ratio:.2f}",
            f"{ab_test_result.baseline_prompt_ratio:.1f}%",
            f"{100 - ab_test_result.baseline_prompt_ratio:.1f}%"
        ],
        'DocStratum': [
            f"{docstratum_ratio:.2f}",
            f"{ab_test_result.docstratum_prompt_ratio:.1f}%",
            f"{100 - ab_test_result.docstratum_prompt_ratio:.1f}%"
        ]
    }

    df = pd.DataFrame(efficiency_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
```

### 5.3 Efficiency Metrics Table

| **Metric** | **Baseline** | **DocStratum** | **Interpretation** |
|---|---|---|---|
| Completion/Prompt Ratio | 0.40 | 0.40 | Equal efficiency |
| Prompt % of Total | 71.4% | 71.4% | Input-heavy both |
| Completion % of Total | 28.6% | 28.6% | Output proportion same |

---

## 6. Data Export and Analysis

### 6.1 CSV Export Function

```python
def export_token_breakdown_csv(ab_test_result: ABTestResult) -> str:
    """
    Export token breakdown as CSV for analysis.

    Returns:
        CSV string for download
    """
    import io

    buffer = io.StringIO()
    df = prepare_token_breakdown_dataframe(ab_test_result)
    df.to_csv(buffer, index=False)

    return buffer.getvalue()

def render_export_button(ab_test_result: ABTestResult) -> None:
    """Add CSV export button to Streamlit."""
    csv_data = export_token_breakdown_csv(ab_test_result)

    st.download_button(
        label="Download Token Breakdown (CSV)",
        data=csv_data,
        file_name="token_breakdown.csv",
        mime="text/csv",
        help="Export token breakdown for further analysis"
    )
```

### 6.2 Production Analysis Considerations

For production workloads, consider tracking:

```python
class TokenAnalyticsRecord(BaseModel):
    """Record for tracking token metrics over time."""
    timestamp: str
    query_id: str
    baseline_tokens: int
    docstratum_tokens: int
    token_overhead: int
    latency_ms: float
    cost_savings_dollars: float
    quality_score: float
```

Example aggregations:
- Daily token usage trends
- Average overhead per query type
- Efficiency ratios by model
- Cost-benefit analysis

---

## Deliverables Checklist

- [ ] Token breakdown data structure defined (TokenBreakdown, ABTestResult models)
- [ ] `prepare_token_breakdown_dataframe()` function implemented
- [ ] `render_token_breakdown()` function displays table using st.dataframe()
- [ ] Dataframe includes: Prompt, Completion, Total, Overhead rows
- [ ] Overhead column shows both absolute (+N) and percentage (+X.X%)
- [ ] Optional bar chart visualization implemented (token comparison)
- [ ] Optional pie chart for token composition (prompt vs completion)
- [ ] Token overhead calculation formula documented and implemented
- [ ] Per-component overhead (prompt, completion) calculated correctly
- [ ] Token efficiency metrics implemented (completion/prompt ratio)
- [ ] Efficiency table shows prompt/completion breakdown percentages
- [ ] CSV export function implemented with download button
- [ ] Data formatting uses thousands separators (commas)
- [ ] All calculations handle edge cases (zero division, empty data)

---

## Acceptance Criteria

- [ ] Token breakdown table renders correctly with 4 columns (Category, Baseline, DocStratum, Difference)
- [ ] Prompt tokens displayed with thousands separator (e.g., "525,000")
- [ ] Completion tokens displayed with thousands separator
- [ ] Total tokens row is bold or highlighted to show it's a sum
- [ ] Overhead row shows both absolute (+35) and percentage (+5.0%)
- [ ] Token overhead calculation correct: docstratum_total - baseline_total
- [ ] Overhead percentage calculation correct: overhead/baseline × 100
- [ ] Bar chart (optional) shows prompt, completion, and total side-by-side
- [ ] Pie chart (optional) shows DocStratum token composition (prompt vs completion)
- [ ] Efficiency metrics show completion/prompt ratio with 2 decimals
- [ ] All numbers match the ABTestResult data model values
- [ ] Export button generates valid CSV with proper headers
- [ ] No console errors or missing data in any table
- [ ] Dataframe uses container_width=True for responsive design
- [ ] Help text on metrics explains what each column means

---

## Next Step

→ **v0.4.3d — Cost Estimation & Provider Pricing**

Implement cost estimation using the token breakdown from this sub-part. Using the token counts (baseline_tokens, docstratum_tokens) and provider pricing (GPT-4o-mini: INPUT_COST=0.00015, OUTPUT_COST=0.0006 per 1K tokens), calculate and display production cost projections and multi-provider cost comparisons.

