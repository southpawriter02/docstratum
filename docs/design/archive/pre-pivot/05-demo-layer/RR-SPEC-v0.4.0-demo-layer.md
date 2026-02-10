# v0.4.0 — Demo Layer

> **Phase Goal:** Build the visual demonstration layer that showcases the before/after improvement.
> 

---

## Phase Overview

---

## User Stories

### US-009: Interactive Demo

> **As a** portfolio viewer,
> 

> **I want** to see a side-by-side comparison in a web UI,
> 

> **So that** I can understand the improvement visually.
> 

**Acceptance Criteria:**

- [ ]  Web UI loads without errors
- [ ]  User can type a question
- [ ]  Both responses display side-by-side
- [ ]  Clear visual distinction between baseline and enhanced

### US-010: Graph Visualization (Optional)

> **As a** technical reviewer,
> 

> **I want** to see the concept graph visually,
> 

> **So that** I can appreciate the information architecture.
> 

**Acceptance Criteria:**

- [ ]  Concepts displayed as nodes
- [ ]  `depends_on` relationships shown as edges
- [ ]  Interactive (click to see details)

---

## Wireframe: Streamlit UI

```
┌─────────────────────────────────────────────────────────────────────┐
│  🗿 THE DOCSTRATUM — A/B TESTER                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Ask a question about the documentation:                      │  │
│  │  [____________________________________________] [Compare]     │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌─────────────────────────┐    ┌─────────────────────────────┐    │
│  │  ❌ BASELINE AGENT      │    │  ✅ DOCSTRATUM AGENT           │    │
│  ├─────────────────────────┤    ├─────────────────────────────┤    │
│  │                         │    │                             │    │
│  │  Generic response       │    │  Specific response with     │    │
│  │  without citations...   │    │  URLs and formatting...     │    │
│  │                         │    │                             │    │
│  │                         │    │  📎 Sources:                │    │
│  │                         │    │  • docs.example.com/auth    │    │
│  │                         │    │  • docs.example.com/start   │    │
│  └─────────────────────────┘    └─────────────────────────────┘    │
│                                                                     │
│  ───────────────────────────────────────────────────────────────    │
│  📊 Token Usage: Baseline 142 | DocStratum 287 | Context 1,240        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Version Roadmap

---

## Decision Tree: Visualization Strategy

```
               ┌─────────────────────┐
               │  What is the primary │
               │  demo environment?   │
               └──────────┬──────────┘
                          │
       ┌──────────────────┼──────────────────┐
       ▼                  ▼                  ▼
┌───────────┐      ┌───────────┐      ┌───────────┐
│ Portfolio │      │  Live     │      │ Technical │
│  Website  │      │  Demo     │      │  Review   │
└─────┬─────┘      └─────┬─────┘      └─────┬─────┘
      │                  │                  │
      ▼                  ▼                  ▼
Streamlit Cloud    Local Streamlit    Terminal + 
(Deployed)         (Interactive)      Screenshots
      │                  │                  │
      └──────────────────┼──────────────────┘
                         ▼
               ✅ Build Streamlit first
               (Works for all scenarios)
```

---

## Code Template: Streamlit App

```python
# demo/app.py
import streamlit as st
import time

# Page config
st.set_page_config(
    page_title="The DocStratum",
    page_icon="🗿",
    layout="wide"
)

# Header
st.title("🗿 The DocStratum")
st.caption("A/B Testing for AI-Ready Documentation")

# Input
question = st.text_input(
    "Ask a question about the documentation:",
    placeholder="e.g., How do I authenticate my app?"
)

if st.button("Compare", type="primary"):
    with st.spinner("Running comparison..."):
        # Placeholder for actual A/B test
        time.sleep(1)
        results = run_ab_test(question)
    
    # Display results
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("❌ Baseline Agent")
        st.markdown(results['baseline'])
    
    with col2:
        st.subheader("✅ DocStratum Agent")
        st.markdown(results['docstratum'])
    
    # Metrics
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Baseline Tokens", results.get('baseline_tokens', 'N/A'))
    m2.metric("DocStratum Tokens", results.get('docstratum_tokens', 'N/A'))
    m3.metric("Context Tokens", results.get('context_tokens', 'N/A'))
```

---

## Testing Strategy

### Test: UI Smoke Test

```python
# tests/test_demo.py
import subprocess
import time
import requests

def test_streamlit_app_starts():
    """Streamlit app should start without errors."""
    # Start the app
    process = subprocess.Popen(
        ['streamlit', 'run', 'demo/app.py', '--server.headless', 'true'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(5)  # Wait for startup
    
    try:
        response = requests.get('http://localhost:8501')
        assert response.status_code == 200
    finally:
        process.terminate()
```

---

## Exit Criteria

This phase is **COMPLETE** when:

- [ ]  `streamlit run demo/[app.py](http://app.py)` starts without errors
- [ ]  User can input a question and see results
- [ ]  Side-by-side comparison displays correctly
- [ ]  App runs for 5 minutes without crashing
- [ ]  Screenshot captured for portfolio

[v0.4.1 — Streamlit Scaffold](RR-SPEC-v0.4.1-streamlit-scaffold.md)

[v0.4.2 — Side-by-Side View](RR-SPEC-v0.4.2-side-by-side-view.md)

[v0.4.3 — Metrics Display](RR-SPEC-v0.4.3-metrics-display.md)

[v0.4.4 — Neo4j Integration (Optional)](RR-SPEC-v0.4.4-neo4j-integration-optional.md)

---

## 📂 All v0.4.x Sub-Part Pages

### v0.4.1 — Streamlit Scaffold

- [v0.4.1a — Application Architecture & Page Configuration](RR-SPEC-v0.4.1a-application-architecture-and-page-configuration.md)
- [v0.4.1b — Configuration Module & Sample Data](RR-SPEC-v0.4.1b-configuration-module-and-sample-data.md)
- [v0.4.1c — Session State & User Interaction Flow](RR-SPEC-v0.4.1c-session-state-and-user-interaction-flow.md)
- [v0.4.1d — Custom Styling & Deployment Readiness](RR-SPEC-v0.4.1d-custom-styling-and-deployment-readiness.md)

### v0.4.2 — Side-by-Side View

- [v0.4.2a — Component Architecture & Reusable Patterns](RR-SPEC-v0.4.2a-component-architecture-and-reusable-patterns.md)
- [v0.4.2b — Response Card Rendering & Formatting](RR-SPEC-v0.4.2b-response-card-rendering-and-formatting.md)
- [v0.4.2c — Analysis Engine & Quality Signals](RR-SPEC-v0.4.2c-analysis-engine-and-quality-signals.md)
- [v0.4.2d — Visual Design System & CSS Architecture](RR-SPEC-v0.4.2d-visual-design-system-and-css-architecture.md)

### v0.4.3 — Metrics Display

- [v0.4.3a — Metrics Dashboard Layout & Key Indicators](RR-SPEC-v0.4.3a-metrics-dashboard-layout-and-key-indicators.md)
- [v0.4.3b — Quality Scoring Engine & Heuristics](RR-SPEC-v0.4.3b-quality-scoring-engine-and-heuristics.md)
- [v0.4.3c — Token Analysis & Breakdown Display](RR-SPEC-v0.4.3c-token-analysis-and-breakdown-display.md)
- [v0.4.3d — Cost Estimation & Provider Pricing](RR-SPEC-v0.4.3d-cost-estimation-and-provider-pricing.md)

### v0.4.4 — Neo4j Integration (Optional)

- [v0.4.4a — Graph Database Design & Neo4j Schema](RR-SPEC-v0.4.4a-graph-database-design-and-neo4j-schema.md)
- [v0.4.4b — Docker Infrastructure & Environment Setup](RR-SPEC-v0.4.4b-docker-infrastructure-and-environment-setup.md)
- [v0.4.4c — Graph Population & Data Pipeline](RR-SPEC-v0.4.4c-graph-population-and-data-pipeline.md)
- [v0.4.4d — Visualization Alternatives & Obsidian Export](RR-SPEC-v0.4.4d-visualization-alternatives-and-obsidian-export.md)