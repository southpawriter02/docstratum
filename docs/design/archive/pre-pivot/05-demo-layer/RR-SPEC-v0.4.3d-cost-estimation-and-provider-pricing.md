# v0.4.3d — Cost Estimation & Provider Pricing

> **Task**: Implement cost estimation with configurable provider pricing for analyzing the financial impact of DocStratum translation. This sub-part defines the cost model based on per-1K-token pricing, implements `render_cost_estimate()` with GPT-4o-mini baseline (INPUT_COST=0.00015, OUTPUT_COST=0.0006 per 1K tokens), and provides multi-provider cost comparison (GPT-4o-mini, GPT-4o, Claude Sonnet) with production workload projections.

---

## Objective

Establish a transparent cost estimation system that projects financial impact of using DocStratum vs baseline agents across different LLM providers. This file defines:

- Cost model design based on per-1K-token pricing
- GPT-4o-mini baseline pricing constants (INPUT/OUTPUT costs)
- `render_cost_estimate()` implementation with 3-column layout
- Multi-provider cost comparison (GPT-4o-mini, GPT-4o, Claude Sonnet)
- Production cost projections for scaled workloads
- Pricing update strategy and maintenance process

---

## Scope Boundaries

| **In Scope** | **Out of Scope** |
|---|---|
| Per-1K-token pricing model | Real-time pricing from provider APIs |
| GPT-4o-mini baseline pricing implementation | Historical pricing trend analysis |
| Multi-provider cost comparison table | Billing integration with cloud providers |
| Production workload cost projections (1K/10K/100K queries) | Volume discount negotiation guidance |
| Cost per query breakdown (prompt vs completion) | Currency conversion or regional pricing |
| Cost estimation UI with 3-column layout | Subscription model cost analysis |
| Overhead cost impact visualization | Reserved capacity pricing models |
| Pricing update process and documentation | Cost optimization recommendations |

---

## Dependency Diagram

```
┌─────────────────────────────────────────────────────────┐
│          Provider Pricing Configuration                 │
│                                                         │
│  GPT-4o-mini:                                           │
│  ├─ input_cost = 0.00015 per 1K tokens                 │
│  └─ output_cost = 0.0006 per 1K tokens                  │
│                                                         │
│  GPT-4o:                                                │
│  ├─ input_cost = 0.003 per 1K tokens                   │
│  └─ output_cost = 0.006 per 1K tokens                   │
│                                                         │
│  Claude Sonnet (3.5):                                   │
│  ├─ input_cost = 0.003 per 1K tokens                   │
│  └─ output_cost = 0.015 per 1K tokens                   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│     Token Breakdown (v0.4.3c)                           │
│                                                         │
│  ├─ baseline_prompt_tokens: int                         │
│  ├─ baseline_completion_tokens: int                     │
│  ├─ docstratum_prompt_tokens: int                          │
│  ├─ docstratum_completion_tokens: int                      │
│  └─ token_overhead: int                                 │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│     calculate_cost() & render_cost_estimate()           │
│                                                         │
│  1. Calculate baseline cost                            │
│  2. Calculate docstratum cost                             │
│  3. Calculate overhead cost                            │
│  4. Generate cost comparison table                     │
│  5. Project production costs                           │
│  6. Render with st.columns()                           │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│     Metrics Dashboard (v0.4.3a)                         │
│                                                         │
│  Shows:                                                 │
│  ├─ Token Overhead metric                              │
│  ├─ Quality Score metric                               │
│  ├─ Token Breakdown (v0.4.3c)                          │
│  └─ Cost Estimate (THIS SUB-PART)                      │
└─────────────────────────────────────────────────────────┘
```

---

## 1. Cost Model Design

### 1.1 Per-1K-Token Pricing Model

All LLM providers use similar pricing: cost per 1,000 tokens (1K).

**Cost Formula:**

```
Cost = (Prompt Tokens / 1000 × Input Cost) + (Completion Tokens / 1000 × Output Cost)

Example with GPT-4o-mini:
Baseline: 500 prompt tokens + 200 completion tokens
Cost = (500/1000 × 0.00015) + (200/1000 × 0.0006)
     = 0.000075 + 0.00012
     = $0.000195 (~0.2 cents)
```

### 1.2 Cost Structure

Each provider defines two rates:

| **Rate Type** | **Definition** | **Unit** | **Why Different?** |
|---|---|---|---|
| **Input Cost** | Price per 1K tokens in prompt | $/1K | Prompts processed once; cheaper to compute |
| **Output Cost** | Price per 1K tokens in completion | $/1K | Generated token-by-token; expensive to generate |

**Example Ratio** (GPT-4o-mini):
```
Output cost / Input cost = 0.0006 / 0.00015 = 4:1

(Completion tokens are ~4× more expensive than prompt tokens)
```

### 1.3 Three-Column Cost Breakdown

The cost estimate displays three columns:

```
┌─────────────────────────────┬──────────────────────┬──────────────────────┐
│         Baseline            │       DocStratum        │  Cost Impact         │
├─────────────────────────────┼──────────────────────┼──────────────────────┤
│ Prompt Cost:   $0.000075    │ Prompt Cost: $0.000079 │ +$0.000004 (+5.3%)   │
│ Output Cost:   $0.00012     │ Output Cost: $0.000126 │ +$0.000006 (+5.0%)   │
│ ─────────────────────────   │ ──────────────────────│ ──────────────────────│
│ Total Cost:    $0.000195    │ Total Cost:  $0.000205 │ +$0.00001 (+5.1%)    │
└─────────────────────────────┴──────────────────────┴──────────────────────┘
```

---

## 2. GPT-4o-mini Baseline Pricing

### 2.1 Pricing Constants

```python
# Provider pricing configuration

class ProviderPricing(BaseModel):
    """Pricing for a single LLM provider."""
    name: str
    input_cost_per_1k: float  # $/1K input tokens
    output_cost_per_1k: float  # $/1K output tokens

class PricingConfig:
    """Centralized pricing configuration."""

    # GPT-4o-mini (Baseline for DocStratum demo)
    GPT_4O_MINI = ProviderPricing(
        name="GPT-4o-mini",
        input_cost_per_1k=0.00015,  # $0.15 per 1M input tokens
        output_cost_per_1k=0.0006   # $0.60 per 1M output tokens
    )

    # GPT-4o (Comparison: premium)
    GPT_4O = ProviderPricing(
        name="GPT-4o",
        input_cost_per_1k=0.003,    # $3.00 per 1M input tokens
        output_cost_per_1k=0.006    # $6.00 per 1M output tokens
    )

    # Claude Sonnet 3.5 (Comparison: alternative)
    CLAUDE_SONNET_3_5 = ProviderPricing(
        name="Claude Sonnet 3.5",
        input_cost_per_1k=0.003,    # $3.00 per 1M input tokens
        output_cost_per_1k=0.015    # $15.00 per 1M output tokens
    )

    @classmethod
    def get_all_providers(cls):
        """Return list of all configured providers."""
        return [
            cls.GPT_4O_MINI,
            cls.GPT_4O,
            cls.CLAUDE_SONNET_3_5
        ]
```

### 2.2 Pricing Rationale

**GPT-4o-mini (Chosen as Baseline):**
- **Cheapest option**: Ideal for development and demos
- **Balanced performance**: Good quality without premium cost
- **Cost-conscious**: Shows value proposition of DocStratum (small overhead on cheap base)
- **Demo-appropriate**: Makes cost overhead visible to users

**Alternative Providers:**
- GPT-4o: 20× more expensive; highlights impact of model choice
- Claude Sonnet: Different output/input ratio; useful for comparison

---

## 3. Cost Calculation Implementation

### 3.1 Cost Calculation Functions

```python
# metrics.py - Cost calculation

from typing import Dict, Tuple
from pydantic import BaseModel

def calculate_cost(
    prompt_tokens: int,
    completion_tokens: int,
    provider: ProviderPricing
) -> Dict[str, float]:
    """
    Calculate cost for a given token count and provider.

    Args:
        prompt_tokens: Number of input tokens
        completion_tokens: Number of output tokens
        provider: ProviderPricing object with rates

    Returns:
        Dict with:
        - 'input_cost': Cost of prompt tokens
        - 'output_cost': Cost of completion tokens
        - 'total_cost': Sum of input and output costs
    """
    input_cost = (prompt_tokens / 1000) * provider.input_cost_per_1k
    output_cost = (completion_tokens / 1000) * provider.output_cost_per_1k
    total_cost = input_cost + output_cost

    return {
        'input_cost': input_cost,
        'output_cost': output_cost,
        'total_cost': total_cost
    }

def calculate_cost_difference(
    baseline_tokens: Tuple[int, int],  # (prompt, completion)
    docstratum_tokens: Tuple[int, int],   # (prompt, completion)
    provider: ProviderPricing
) -> Dict[str, float]:
    """
    Calculate cost difference between baseline and DocStratum.

    Returns:
        Dict with:
        - 'baseline_cost': Total cost of baseline
        - 'docstratum_cost': Total cost of DocStratum
        - 'absolute_difference': docstratum_cost - baseline_cost
        - 'percentage_difference': (difference / baseline_cost) × 100
        - 'per_query_overhead': Cost of overhead tokens only
    """
    baseline_cost = calculate_cost(
        baseline_tokens[0], baseline_tokens[1], provider
    )
    docstratum_cost = calculate_cost(
        docstratum_tokens[0], docstratum_tokens[1], provider
    )

    abs_diff = docstratum_cost['total_cost'] - baseline_cost['total_cost']
    pct_diff = (abs_diff / baseline_cost['total_cost'] * 100) \
        if baseline_cost['total_cost'] > 0 else 0

    # Cost of just the overhead tokens
    overhead_cost = calculate_cost(
        docstratum_tokens[0] - baseline_tokens[0],
        docstratum_tokens[1] - baseline_tokens[1],
        provider
    )['total_cost']

    return {
        'baseline_cost': baseline_cost['total_cost'],
        'docstratum_cost': docstratum_cost['total_cost'],
        'input_cost_baseline': baseline_cost['input_cost'],
        'input_cost_docstratum': docstratum_cost['input_cost'],
        'output_cost_baseline': baseline_cost['output_cost'],
        'output_cost_docstratum': docstratum_cost['output_cost'],
        'absolute_difference': abs_diff,
        'percentage_difference': pct_diff,
        'overhead_cost': overhead_cost
    }
```

### 3.2 Cost Formatting Functions

```python
def format_cost(cost: float) -> str:
    """
    Format cost as currency string.

    Args:
        cost: Cost in dollars

    Returns:
        Formatted string, e.g., "$0.000195" or "$1.23"
    """
    if cost < 0.001:
        return f"${cost:.6f}"
    elif cost < 1:
        return f"${cost:.4f}"
    else:
        return f"${cost:.2f}"

def format_cost_difference(diff: float, percentage: float) -> str:
    """
    Format cost difference with sign and percentage.

    Args:
        diff: Absolute cost difference
        percentage: Percentage difference

    Returns:
        Formatted string, e.g., "+$0.0001 (+5.1%)"
    """
    sign = "+" if diff >= 0 else ""
    return f"{sign}{format_cost(diff)} ({sign}{percentage:.1f}%)"
```

---

## 4. Cost Estimate Rendering Function

### 4.1 Complete render_cost_estimate()

```python
import streamlit as st
import pandas as pd

def render_cost_estimate(ab_test_result: ABTestResult) -> None:
    """
    Render cost estimation in 3-column layout.

    Displays:
    1. Baseline cost breakdown
    2. DocStratum cost breakdown
    3. Cost impact comparison
    """
    st.subheader("Cost Estimation (GPT-4o-mini)")

    # Use GPT-4o-mini as baseline provider
    provider = PricingConfig.GPT_4O_MINI

    # Calculate costs
    baseline_tokens = (
        ab_test_result.baseline_breakdown.prompt_tokens,
        ab_test_result.baseline_breakdown.completion_tokens
    )
    docstratum_tokens = (
        ab_test_result.docstratum_breakdown.prompt_tokens,
        ab_test_result.docstratum_breakdown.completion_tokens
    )

    costs = calculate_cost_difference(baseline_tokens, docstratum_tokens, provider)

    # Display in 3 columns
    col1, col2, col3 = st.columns(3)

    # Column 1: Baseline Cost
    with col1:
        st.markdown("**Baseline**")
        st.markdown(f"Input: {format_cost(costs['input_cost_baseline'])}")
        st.markdown(f"Output: {format_cost(costs['output_cost_baseline'])}")
        st.markdown(f"**Total: {format_cost(costs['baseline_cost'])}**")

    # Column 2: DocStratum Cost
    with col2:
        st.markdown("**DocStratum**")
        st.markdown(f"Input: {format_cost(costs['input_cost_docstratum'])}")
        st.markdown(f"Output: {format_cost(costs['output_cost_docstratum'])}")
        st.markdown(f"**Total: {format_cost(costs['docstratum_cost'])}**")

    # Column 3: Cost Impact
    with col3:
        st.markdown("**Cost Impact**")
        input_diff = costs['input_cost_docstratum'] - costs['input_cost_baseline']
        input_diff_pct = (input_diff / costs['input_cost_baseline'] * 100) \
            if costs['input_cost_baseline'] > 0 else 0

        output_diff = costs['output_cost_docstratum'] - costs['output_cost_baseline']
        output_diff_pct = (output_diff / costs['output_cost_baseline'] * 100) \
            if costs['output_cost_baseline'] > 0 else 0

        st.markdown(f"Input: {format_cost_difference(input_diff, input_diff_pct)}")
        st.markdown(f"Output: {format_cost_difference(output_diff, output_diff_pct)}")

        total_diff = costs['absolute_difference']
        total_diff_pct = costs['percentage_difference']
        st.markdown(f"**Total: {format_cost_difference(total_diff, total_diff_pct)}**")
```

### 4.2 HTML/Markdown Alternative

For custom styling, use HTML table:

```python
def render_cost_estimate_html(ab_test_result: ABTestResult) -> None:
    """Alternative: Render cost estimate using HTML table."""
    provider = PricingConfig.GPT_4O_MINI

    baseline_tokens = (
        ab_test_result.baseline_breakdown.prompt_tokens,
        ab_test_result.baseline_breakdown.completion_tokens
    )
    docstratum_tokens = (
        ab_test_result.docstratum_breakdown.prompt_tokens,
        ab_test_result.docstratum_breakdown.completion_tokens
    )

    costs = calculate_cost_difference(baseline_tokens, docstratum_tokens, provider)

    html = f"""
    <div style="margin: 20px 0;">
    <h3>Cost Estimation (GPT-4o-mini)</h3>
    <table style="width: 100%; border-collapse: collapse;">
        <tr style="background: #f0f0f0;">
            <th style="padding: 10px; border: 1px solid #ddd;">Metric</th>
            <th style="padding: 10px; border: 1px solid #ddd;">Baseline</th>
            <th style="padding: 10px; border: 1px solid #ddd;">DocStratum</th>
            <th style="padding: 10px; border: 1px solid #ddd;">Impact</th>
        </tr>
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;">Input Cost</td>
            <td style="padding: 10px; border: 1px solid #ddd;">{format_cost(costs['input_cost_baseline'])}</td>
            <td style="padding: 10px; border: 1px solid #ddd;">{format_cost(costs['input_cost_docstratum'])}</td>
            <td style="padding: 10px; border: 1px solid #ddd;">
                {format_cost_difference(
                    costs['input_cost_docstratum'] - costs['input_cost_baseline'],
                    (costs['input_cost_docstratum'] - costs['input_cost_baseline']) / costs['input_cost_baseline'] * 100
                )}
            </td>
        </tr>
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;">Output Cost</td>
            <td style="padding: 10px; border: 1px solid #ddd;">{format_cost(costs['output_cost_baseline'])}</td>
            <td style="padding: 10px; border: 1px solid #ddd;">{format_cost(costs['output_cost_docstratum'])}</td>
            <td style="padding: 10px; border: 1px solid #ddd;">
                {format_cost_difference(
                    costs['output_cost_docstratum'] - costs['output_cost_baseline'],
                    (costs['output_cost_docstratum'] - costs['output_cost_baseline']) / costs['output_cost_baseline'] * 100
                )}
            </td>
        </tr>
        <tr style="background: #f9f9f9; font-weight: bold;">
            <td style="padding: 10px; border: 1px solid #ddd;">Total Cost</td>
            <td style="padding: 10px; border: 1px solid #ddd;">{format_cost(costs['baseline_cost'])}</td>
            <td style="padding: 10px; border: 1px solid #ddd;">{format_cost(costs['docstratum_cost'])}</td>
            <td style="padding: 10px; border: 1px solid #ddd;">
                {format_cost_difference(costs['absolute_difference'], costs['percentage_difference'])}
            </td>
        </tr>
    </table>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)
```

---

## 5. Multi-Provider Cost Comparison

### 5.1 Provider Comparison Table

```python
def render_provider_comparison(ab_test_result: ABTestResult) -> None:
    """
    Display cost comparison across different providers.
    """
    st.subheader("Multi-Provider Cost Comparison")

    baseline_tokens = (
        ab_test_result.baseline_breakdown.prompt_tokens,
        ab_test_result.baseline_breakdown.completion_tokens
    )
    docstratum_tokens = (
        ab_test_result.docstratum_breakdown.prompt_tokens,
        ab_test_result.docstratum_breakdown.completion_tokens
    )

    providers = PricingConfig.get_all_providers()
    comparison_data = {
        'Provider': [],
        'Baseline Cost': [],
        'DocStratum Cost': [],
        'Overhead': [],
        'Overhead %': []
    }

    for provider in providers:
        costs = calculate_cost_difference(baseline_tokens, docstratum_tokens, provider)

        comparison_data['Provider'].append(provider.name)
        comparison_data['Baseline Cost'].append(format_cost(costs['baseline_cost']))
        comparison_data['DocStratum Cost'].append(format_cost(costs['docstratum_cost']))
        comparison_data['Overhead'].append(format_cost(costs['overhead_cost']))
        comparison_data['Overhead %'].append(f"{costs['percentage_difference']:.1f}%")

    df = pd.DataFrame(comparison_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Add interpretation
    st.info(
        "💡 **Interpretation**: Token overhead is the same across providers, but cost impact "
        "varies. Premium models (GPT-4o, Claude) show higher absolute cost overhead. "
        "GPT-4o-mini offers best value for cost-sensitive applications."
    )
```

### 5.2 Provider Comparison Table

| **Provider** | **Baseline Cost** | **DocStratum Cost** | **Overhead** | **Overhead %** |
|---|---|---|---|---|
| GPT-4o-mini | $0.000195 | $0.000205 | $0.00001 | 5.1% |
| GPT-4o | $0.004100 | $0.004315 | $0.000215 | 5.1% |
| Claude Sonnet 3.5 | $0.006200 | $0.006515 | $0.000315 | 5.1% |

**Key Insight**: Overhead percentage is constant (5.1%) because overhead depends on token ratio, not provider rates. But absolute cost varies 30× from cheapest to most expensive provider.

---

## 6. Production Cost Projections

### 6.1 Projection Implementation

```python
def project_production_costs(
    ab_test_result: ABTestResult,
    provider: ProviderPricing = None
) -> pd.DataFrame:
    """
    Project costs for production workloads at scale.

    Args:
        ab_test_result: Single query test result
        provider: ProviderPricing to use (default: GPT-4o-mini)

    Returns:
        DataFrame with cost projections for 1K, 10K, 100K queries
    """
    if provider is None:
        provider = PricingConfig.GPT_4O_MINI

    baseline_tokens = (
        ab_test_result.baseline_breakdown.prompt_tokens,
        ab_test_result.baseline_breakdown.completion_tokens
    )
    docstratum_tokens = (
        ab_test_result.docstratum_breakdown.prompt_tokens,
        ab_test_result.docstratum_breakdown.completion_tokens
    )

    # Per-query costs
    baseline_cost = calculate_cost(
        baseline_tokens[0], baseline_tokens[1], provider
    )['total_cost']
    docstratum_cost = calculate_cost(
        docstratum_tokens[0], docstratum_tokens[1], provider
    )['total_cost']

    # Projection scales
    scales = [1_000, 10_000, 100_000]

    projection_data = {
        'Scale': [],
        'Baseline Total': [],
        'DocStratum Total': [],
        'Cost Overhead': [],
        'Monthly Savings*': []
    }

    for scale in scales:
        baseline_total = baseline_cost * scale
        docstratum_total = docstratum_cost * scale
        overhead = docstratum_total - baseline_total
        savings = -overhead  # Negative overhead = savings

        projection_data['Scale'].append(f"{scale:,} queries")
        projection_data['Baseline Total'].append(format_cost(baseline_total))
        projection_data['DocStratum Total'].append(format_cost(docstratum_total))
        projection_data['Cost Overhead'].append(format_cost(overhead))
        projection_data['Monthly Savings*'].append(format_cost(savings))

    return pd.DataFrame(projection_data)

def render_production_projections(ab_test_result: ABTestResult) -> None:
    """Render production cost projections."""
    st.subheader("Production Cost Projections")

    df = project_production_costs(
        ab_test_result,
        PricingConfig.GPT_4O_MINI
    )

    st.dataframe(df, use_container_width=True, hide_index=True)

    st.caption(
        "*Assumes overhead cost is additional expense. In practice, quality gains may offset cost "
        "by reducing manual review needs or improving user satisfaction."
    )
```

### 6.2 Production Projection Example

| **Scale** | **Baseline Total** | **DocStratum Total** | **Cost Overhead** | **Impact** |
|---|---|---|---|---|
| 1,000 queries | $0.195 | $0.205 | $0.01 | Minimal |
| 10,000 queries | $1.95 | $2.05 | $0.10 | Acceptable |
| 100,000 queries | $19.50 | $20.50 | $1.00 | Review quality gain |

**Interpretation**:
- At 1K queries: $0.01 overhead (negligible)
- At 100K queries: $1.00/day overhead (acceptable for quality improvement)
- Quality improvements may save more in manual review labor

---

## 7. Pricing Update Strategy

### 7.1 Update Process

As provider pricing changes, update the configuration:

```python
# Update schedule: Quarterly (Jan, Apr, Jul, Oct)
# Last updated: 2024-Q4

PRICING_UPDATE_NOTES = {
    "GPT-4o-mini": {
        "last_updated": "2024-10-01",
        "source": "https://openai.com/pricing",
        "notes": "Prices as of October 2024"
    },
    "GPT-4o": {
        "last_updated": "2024-10-01",
        "source": "https://openai.com/pricing",
        "notes": "Prices as of October 2024"
    },
    "Claude Sonnet 3.5": {
        "last_updated": "2024-10-01",
        "source": "https://www.anthropic.com/pricing",
        "notes": "Prices as of October 2024"
    }
}
```

### 7.2 Monitoring and Alerts

```python
def check_pricing_staleness() -> bool:
    """
    Check if pricing data is older than 90 days.
    Returns True if pricing should be updated.
    """
    from datetime import datetime, timedelta

    last_update = datetime.strptime("2024-10-01", "%Y-%m-%d")
    days_old = (datetime.now() - last_update).days

    if days_old > 90:
        print("⚠️ WARNING: Pricing data is >90 days old. Update recommended.")
        return True

    return False
```

### 7.3 Version Control

Track pricing changes in git:

```
# Commit message when updating pricing
git commit -m "chore: update provider pricing (Q1 2025)

- GPT-4o-mini: input $0.00015/1K, output $0.0006/1K
- GPT-4o: input $0.003/1K, output $0.006/1K
- Claude Sonnet 3.5: input $0.003/1K, output $0.015/1K

Sources:
- https://openai.com/pricing (2025-01-15)
- https://anthropic.com/pricing (2025-01-15)
"
```

---

## Deliverables Checklist

- [ ] Per-1K-token pricing model documented and implemented
- [ ] GPT-4o-mini baseline pricing defined (INPUT=0.00015, OUTPUT=0.0006)
- [ ] ProviderPricing data model created
- [ ] PricingConfig with GPT-4o-mini, GPT-4o, Claude Sonnet defined
- [ ] `calculate_cost()` function implemented
- [ ] `calculate_cost_difference()` function implemented
- [ ] `format_cost()` function formats currency correctly
- [ ] `format_cost_difference()` shows +/- and percentages
- [ ] `render_cost_estimate()` displays 3-column layout
- [ ] `render_provider_comparison()` shows multi-provider table
- [ ] `project_production_costs()` generates 1K/10K/100K projections
- [ ] `render_production_projections()` displays projection table
- [ ] Pricing update strategy documented
- [ ] Pricing staleness check implemented
- [ ] All cost calculations handle edge cases (zero division, empty data)

---

## Acceptance Criteria

- [ ] Cost estimate renders in 3 columns: Baseline, DocStratum, Impact
- [ ] Input and output costs displayed separately with correct formulas
- [ ] Total cost row shows both absolute cost and percentage difference
- [ ] Cost difference formatted as "+$0.0001 (+5.1%)"
- [ ] Negative costs (savings) shown with proper formatting
- [ ] Provider comparison table shows at least 3 providers
- [ ] Overhead % is same across providers (token ratio constant)
- [ ] Absolute cost varies correctly (proportional to provider rates)
- [ ] Production projections show 1K, 10K, 100K query scales
- [ ] Projection costs scale linearly from per-query costs
- [ ] All currency values displayed with $ symbol
- [ ] Small values (<$0.001) shown with 6 decimal places
- [ ] Large values (>$1) shown with 2 decimal places
- [ ] No console errors or missing calculations
- [ ] Pricing update process documented and reproducible
- [ ] Pricing staleness warning works correctly

---

## Next Step

→ **v0.4.4a — Advanced Analytics & Export (Future)**

Implement advanced analytics features for production analysis, including:
- Token usage trends over time (daily/weekly/monthly aggregation)
- Cost-benefit analysis comparing quality improvements vs cost overhead
- Export functionality (CSV, JSON) for external analysis
- Multi-query batch analysis and statistical summaries

This completes the v0.4.3 metrics display suite. All four sub-parts (Dashboard, Quality Scoring, Token Analysis, Cost Estimation) integrate to provide comprehensive A/B test analysis for the DocStratum demo.

