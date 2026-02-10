# 05-demo-layer — Demo Layer (v0.4.x)

> **Purpose**: Streamlit UI, side-by-side comparison, metrics display, and optional Neo4j integration

This phase builds the visual demonstration layer that proves the DocStratum improves agent performance through interactive A/B testing and metrics visualization.

---

## 📚 Phase Structure

### v0.4.1 — Streamlit Scaffold

Core application architecture and configuration:

- **v0.4.1a** — Application Architecture & Page Configuration
- **v0.4.1b** — Configuration Module & Sample Data
- **v0.4.1c** — Session State & User Interaction Flow
- **v0.4.1d** — Custom Styling & Deployment Readiness

### v0.4.2 — Side-by-Side View

Interactive comparison interface:

- **v0.4.2a** — Component Architecture & Reusable Patterns
- **v0.4.2b** — Response Card Rendering & Formatting
- **v0.4.2c** — Analysis Engine & Quality Signals
- **v0.4.2d** — Visual Design System & CSS Architecture

### v0.4.3 — Metrics Display

Quantitative analysis dashboard:

- **v0.4.3a** — Metrics Dashboard Layout & Key Indicators
- **v0.4.3b** — Quality Scoring Engine & Heuristics
- **v0.4.3c** — Token Analysis & Breakdown Display
- **v0.4.3d** — Cost Estimation & Provider Pricing

### v0.4.4 — Neo4j Integration (Optional)

Graph visualization of concept relationships:

- **v0.4.4a** — Graph Database Design & Neo4j Schema
- **v0.4.4b** — Docker Infrastructure & Environment Setup
- **v0.4.4c** — Graph Population & Data Pipeline
- **v0.4.4d** — Visualization Alternatives & Obsidian Export

---

## 🎨 UI Architecture

### Main Interface

```
┌─────────────────────────────────────────────────────────────┐
│  🗿 The DocStratum — A/B Tester                           │
├─────────────────────────────────────────────────────────────┤
│  Ask a question: [_________________________________] [Test]  │
├──────────────────────────┬──────────────────────────────────┤
│  ❌ Baseline Agent       │  ✅ DocStratum-Enhanced Agent       │
│  ┌────────────────────┐  │  ┌────────────────────────────┐  │
│  │ Response text...   │  │  │ Response text...           │  │
│  │                    │  │  │                            │  │
│  └────────────────────┘  │  └────────────────────────────┘  │
│                          │                                  │
│  📊 Metrics:             │  📊 Metrics:                     │
│  - Tokens: 150           │  - Tokens: 180                   │
│  - Citations: 0          │  - Citations: 3                  │
│  - Quality: 6/10         │  - Quality: 9/10                 │
└──────────────────────────┴──────────────────────────────────┘
```

### Metrics Dashboard

- **Token Analysis** — Input/output token counts, cost estimation
- **Quality Signals** — Citation count, format adherence, hallucination detection
- **Response Comparison** — Side-by-side diff highlighting
- **Performance Metrics** — Latency, throughput, error rates

---

## 🔧 Key Components

### Streamlit App Structure

```python
# demo/app.py
import streamlit as st
from main import load_llms_txt, run_ab_test

st.title("🗿 The DocStratum — A/B Tester")

# Load the llms.txt
llms = load_llms_txt("llms.txt")

# User input
question = st.text_input("Ask a question about the documentation:")

if st.button("Compare"):
    with st.spinner("Running A/B test..."):
        results = run_ab_test(question, llms)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("❌ Baseline Agent")
        st.write(results["baseline"])

    with col2:
        st.subheader("✅ DocStratum-Enhanced Agent")
        st.write(results["docstratum"])
```

### Quality Scoring Heuristics

- **Citation Count** — Number of URLs referenced
- **Format Adherence** — Matches few-shot example structure
- **Completeness** — Answers all parts of the question
- **Hallucination Detection** — No invented URLs or facts
- **Code Quality** — Syntax highlighting, runnable examples

---

## 🎯 Success Criteria

This demo layer phase is complete when:

- ✅ Streamlit app runs locally without errors
- ✅ Side-by-side comparison displays both agent responses
- ✅ Metrics dashboard shows quantitative differences
- ✅ Quality scoring engine produces consistent scores
- ✅ Custom styling is applied (not default Streamlit theme)
- ✅ App is deployable to Streamlit Cloud or similar
- ✅ (Optional) Neo4j graph visualization is functional

---

## 🗺️ Next Phase

After completing demo layer, proceed to:

- **`06-testing/`** — Formal testing and evidence capture
