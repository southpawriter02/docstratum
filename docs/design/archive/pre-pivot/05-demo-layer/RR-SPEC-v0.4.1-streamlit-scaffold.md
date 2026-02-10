# v0.4.1 — Streamlit Scaffold

> **Task:** Set up the basic Streamlit application structure.
> 

---

## Task Overview

---

## Directory Structure

```
docstratum/
├── demo/
│   ├── __init__.py
│   ├── app.py           ← Main Streamlit app
│   ├── components.py    ← Reusable UI components
│   └── config.py        ← App configuration
└── ...
```

---

## Implementation

### File: `demo/[config.py](http://config.py)`

```python
"""Streamlit app configuration."""

APP_TITLE = "🗿 The DocStratum"
APP_SUBTITLE = "A/B Testing for AI-Ready Documentation"
APP_ICON = "🗿"

DEFAULT_LLMS_PATH = "data/llms.txt"

SAMPLE_QUESTIONS = [
    "Should I use OAuth2 or API keys for my server-side script?",
    "How do I authenticate my Python backend?",
    "What happens if my prompt is too long?",
]
```

### File: `demo/[app.py](http://app.py)`

```python
"""Main Streamlit application."""

import streamlit as st
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from demo.config import APP_TITLE, APP_SUBTITLE, APP_ICON, DEFAULT_LLMS_PATH, SAMPLE_QUESTIONS

# Page configuration (must be first Streamlit command)
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
.stTextInput > div > div > input {
    font-size: 1.1rem;
}
.result-box {
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
}
.baseline-box {
    background-color: #ffebee;
    border-left: 4px solid #f44336;
}
.docstratum-box {
    background-color: #e8f5e9;
    border-left: 4px solid #4caf50;
}
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.title(APP_TITLE)
    st.caption(APP_SUBTITLE)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        llms_path = st.text_input(
            "llms.txt path",
            value=DEFAULT_LLMS_PATH
        )
        st.divider()
        st.markdown("### Sample Questions")
        for q in SAMPLE_QUESTIONS:
            if st.button(q[:40] + "...", key=q):
                st.session_state.question = q
    
    # Main content
    question = st.text_input(
        "Ask a question about the documentation:",
        value=st.session_state.get('question', ''),
        placeholder="e.g., How do I authenticate my app?",
        key="question_input"
    )
    
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        run_test = st.button("🔬 Compare", type="primary", use_container_width=True)
    with col2:
        clear = st.button("🗑️ Clear", use_container_width=True)
    
    if clear:
        st.session_state.clear()
        st.rerun()
    
    if run_test and question:
        with st.spinner("Running A/B comparison..."):
            # Import here to avoid slow startup
            from core.testing import ABTestHarness
            
            try:
                harness = ABTestHarness(llms_path)
                result = harness.run_test(question)
                st.session_state.last_result = result
            except Exception as e:
                st.error(f"Error: {e}")
                return
    
    # Display results
    if 'last_result' in st.session_state:
        result = st.session_state.last_result
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("❌ Baseline Agent")
            st.markdown(result.baseline.response)
            st.caption(
                f"Tokens: {result.baseline.prompt_tokens} + {result.baseline.completion_tokens} | "
                f"Latency: {result.baseline.latency_ms:.0f}ms"
            )
        
        with col2:
            st.subheader("✅ DocStratum Agent")
            st.markdown(result.docstratum.response)
            st.caption(
                f"Tokens: {result.docstratum.prompt_tokens} + {result.docstratum.completion_tokens} | "
                f"Latency: {result.docstratum.latency_ms:.0f}ms"
            )
        
        # Metrics row
        st.divider()
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Context Tokens", f"{result.context_tokens:,}")
        m2.metric("Token Overhead", f"+{result.token_overhead:,}")
        m3.metric("Baseline Latency", f"{result.baseline.latency_ms:.0f}ms")
        m4.metric("DocStratum Latency", f"{result.docstratum.latency_ms:.0f}ms")

if __name__ == "__main__":
    main()
```

---

## Run Command

```bash
streamlit run demo/app.py
```

---

## 📂 Sub-Part Pages

[v0.4.1a — Application Architecture & Page Configuration](RR-SPEC-v0.4.1a-application-architecture-and-page-configuration.md)

[v0.4.1b — Configuration Module & Sample Data](RR-SPEC-v0.4.1b-configuration-module-and-sample-data.md)

[v0.4.1c — Session State & User Interaction Flow](RR-SPEC-v0.4.1c-session-state-and-user-interaction-flow.md)

[v0.4.1d — Custom Styling & Deployment Readiness](RR-SPEC-v0.4.1d-custom-styling-and-deployment-readiness.md)

---

## Acceptance Criteria

- [ ]  `streamlit run demo/[app.py](http://app.py)` starts without errors
- [ ]  Page title and icon display correctly
- [ ]  Text input accepts questions
- [ ]  Sample questions in sidebar
- [ ]  Compare button visible
- [ ]  v0.4.1a: Application architecture documented, page configuration validated
- [ ]  v0.4.1b: Configuration module complete with sample data and theming
- [ ]  v0.4.1c: Session state management implemented with interaction flows
- [ ]  v0.4.1d: Custom CSS applied, deployment readiness verified