# v0.4.1d — Custom Styling & Deployment Readiness

> This sub-part implements custom CSS styling for The DocStratum Streamlit application and prepares the project for Streamlit Cloud deployment. It covers custom CSS injection, class design patterns, Streamlit configuration, requirements management, and production smoke testing to ensure a polished, deployable application.

---

## Objective

Design and implement custom CSS styling and production-readiness infrastructure. This includes:
- Custom CSS injection via st.markdown(unsafe_allow_html=True)
- CSS class design patterns (.result-box, .baseline-box, .docstratum-box, etc.)
- Streamlit Cloud deployment configuration (.streamlit/config.toml)
- Requirements.txt management and dependency pinning
- Production smoke testing strategy
- Deployment checklist and verification procedures
- Health checks and basic functionality validation

---

## Scope Boundaries

| Aspect | In Scope | Out of Scope |
|--------|----------|--------------|
| CSS styling | Custom CSS injection, class design, color scheme | Advanced animations, JavaScript interactivity |
| CSS classes | .result-box, .baseline-box, .docstratum-box, .metrics-row, etc. | Bootstrap or Tailwind framework integration |
| Streamlit config | .streamlit/config.toml settings, client/server/logger sections | System-level configuration or environment variables |
| Requirements | requirements.txt, pinned versions, core dependencies | Development dependencies (pytest, black, etc.) |
| Deployment | Streamlit Cloud setup, secrets management, GitHub integration | Docker/Kubernetes deployment strategies |
| Testing | Smoke tests (visual, functional), basic health checks | Unit tests, integration tests, load testing |
| Readiness | Deployment checklist, pre-launch validation | Post-deployment monitoring or alerting |

---

## Custom CSS Injection via st.markdown()

### CSS Injection Pattern

Streamlit doesn't provide native theming APIs in v0.4.1, so custom CSS is injected via `st.markdown(..., unsafe_allow_html=True)`. This approach allows complete control over styling while maintaining Streamlit's reactive architecture.

### CSS Injection Best Practices

| Best Practice | Why | Example |
|---------------|-----|---------|
| **Scope CSS to unique classes** | Prevent conflicts with Streamlit's internal styles | Use `.docstratum-container` instead of `.container` |
| **Use CSS variables (custom properties)** | Enable theme switching and consistency | `--primary-color: #1f77b4;` |
| **Target wrapper divs** | Don't directly style Streamlit components | Wrap results in `<div class="docstratum-box">` |
| **Minimize specificity** | Easier to override; less brittle | Use single class selectors when possible |
| **Load CSS early** | Ensure styles apply before elements render | Place CSS injection early in app.py |

### CSS Injection Implementation Code

```python
# demo/components.py - CSS injection function

def inject_custom_css():
    """
    Inject custom CSS into the Streamlit app.
    Call this once at the top of app.py after set_page_config().
    """
    custom_css = """
    <style>
    /* ================================================================
       CSS Variables (Theme)
       ================================================================ */
    :root {
        --primary-color: #1f77b4;
        --secondary-color: #2ca02c;
        --accent-color: #ff7f0e;
        --warning-color: #d62728;
        --success-color: #2ca02c;
        --background-color: #f8f9fa;
        --text-color: #2c3e50;
        --text-light: #7f8c8d;
        --border-color: #e0e0e0;
        --border-radius: 8px;
        --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
        --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
        --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);
    }

    /* ================================================================
       Main Container & Layout
       ================================================================ */
    .main {
        background-color: var(--background-color);
        color: var(--text-color);
    }

    /* Streamlit header styling */
    .stTitle {
        color: var(--primary-color);
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    .stSubheader {
        color: var(--secondary-color);
        margin-top: 1.5rem;
    }

    /* ================================================================
       Result Containers
       ================================================================ */
    .result-box {
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        margin: 1rem 0;
        background-color: white;
        box-shadow: var(--shadow-sm);
        transition: box-shadow 0.3s ease;
    }

    .result-box:hover {
        box-shadow: var(--shadow-md);
    }

    /* Left column: baseline result */
    .baseline-box {
        border: 1px solid var(--border-color);
        border-left: 4px solid var(--accent-color);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        background-color: #fafafa;
    }

    .baseline-box h4 {
        color: var(--accent-color);
        font-weight: 600;
        margin-bottom: 1rem;
    }

    /* Right column: docstratum result */
    .docstratum-box {
        border: 1px solid var(--border-color);
        border-left: 4px solid var(--primary-color);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        background-color: #f0f5ff;
    }

    .docstratum-box h4 {
        color: var(--primary-color);
        font-weight: 600;
        margin-bottom: 1rem;
    }

    /* Comparison container (side-by-side layout) */
    .comparison-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
        margin: 2rem 0;
    }

    @media (max-width: 768px) {
        .comparison-container {
            grid-template-columns: 1fr;
        }
    }

    /* ================================================================
       Metrics Row
       ================================================================ */
    .metrics-row {
        display: flex;
        justify-content: space-around;
        flex-wrap: wrap;
        gap: 1rem;
        margin: 2rem 0;
        padding: 1.5rem;
        background-color: var(--background-color);
        border-radius: var(--border-radius);
    }

    .metric-card {
        flex: 1;
        min-width: 150px;
        text-align: center;
        padding: 1rem;
        background-color: white;
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-sm);
    }

    .metric-card h5 {
        font-size: 0.875rem;
        color: var(--text-light);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin: 0 0 0.5rem 0;
    }

    .metric-card .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--primary-color);
    }

    /* ================================================================
       Input & Form Elements
       ================================================================ */
    .question-input {
        border: 2px solid var(--border-color);
        border-radius: var(--border-radius);
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: border-color 0.3s ease;
    }

    .question-input:focus {
        border-color: var(--primary-color);
        outline: none;
        box-shadow: 0 0 0 3px rgba(31, 119, 180, 0.1);
    }

    /* Button styling */
    .stButton > button {
        background-color: var(--primary-color);
        color: white;
        border: none;
        border-radius: var(--border-radius);
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        transition: background-color 0.3s ease, box-shadow 0.3s ease;
    }

    .stButton > button:hover {
        background-color: #1a5fa0;
        box-shadow: var(--shadow-md);
    }

    /* Clear button (secondary style) */
    .stButton > button[kind="secondary"] {
        background-color: var(--text-light);
        color: white;
    }

    .stButton > button[kind="secondary"]:hover {
        background-color: #6c757d;
    }

    /* ================================================================
       Messages & Notifications
       ================================================================ */
    .stSuccess {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: var(--border-radius);
        padding: 1rem;
        color: #155724;
    }

    .stError {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: var(--border-radius);
        padding: 1rem;
        color: #721c24;
    }

    .stWarning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: var(--border-radius);
        padding: 1rem;
        color: #856404;
    }

    .stInfo {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: var(--border-radius);
        padding: 1rem;
        color: #0c5460;
    }

    /* ================================================================
       Sidebar Styling
       ================================================================ */
    .stSidebar {
        background-color: #f8f9fa;
    }

    .stSidebar .stButton > button {
        width: 100%;
        margin-bottom: 0.5rem;
    }

    .sidebar-header {
        color: var(--primary-color);
        font-weight: 700;
        margin-bottom: 1rem;
    }

    /* ================================================================
       Text & Typography
       ================================================================ */
    .stMarkdown a {
        color: var(--primary-color);
        text-decoration: none;
    }

    .stMarkdown a:hover {
        text-decoration: underline;
    }

    .stCaption {
        color: var(--text-light);
        font-size: 0.875rem;
    }

    /* ================================================================
       Spinner & Loading
       ================================================================ */
    .stSpinner > div {
        border-top-color: var(--primary-color);
    }

    /* ================================================================
       Dark Mode Support (Future)
       ================================================================ */
    @media (prefers-color-scheme: dark) {
        :root {
            --background-color: #1e1e1e;
            --text-color: #e0e0e0;
            --text-light: #a0a0a0;
        }

        .main {
            background-color: var(--background-color);
        }

        .result-box,
        .baseline-box,
        .docstratum-box,
        .metric-card {
            background-color: #2d2d2d;
            border-color: #444;
        }

        .docstratum-box {
            background-color: #1a2a4a;
        }

        .baseline-box {
            background-color: #3a2a1a;
        }
    }

    </style>
    """

    st.markdown(custom_css, unsafe_allow_html=True)
```

---

## CSS Class Reference Table

| CSS Class | Element Type | Purpose | Key Properties |
|-----------|--------------|---------|-----------------|
| **.result-box** | Container | Generic result container | padding, border, shadow, rounded corners |
| **.baseline-box** | Container | Left column (baseline output) | border-left accent, background color |
| **.docstratum-box** | Container | Right column (DocStratum output) | border-left accent, background color |
| **.comparison-container** | Layout | Side-by-side columns wrapper | display: grid, gap, responsive |
| **.metrics-row** | Container | Metrics display row | display: flex, justify-content, gap |
| **.metric-card** | Card | Individual metric (sources, freshness) | flex, text-align, padding, shadow |
| **.question-input** | Input | Text input field | border, padding, focus state |
| **.stButton** | Component | Button styling | background-color, border-radius, hover |
| **.stSuccess** | Alert | Success message | background-color, border, color |
| **.stError** | Alert | Error message | background-color, border, color |
| **.stWarning** | Alert | Warning message | background-color, border, color |
| **.stInfo** | Alert | Info message | background-color, border, color |
| **.stSidebar** | Container | Sidebar background | background-color, padding |
| **.sidebar-header** | Text | Sidebar section header | color, font-weight, margin |

---

## Streamlit Cloud Deployment Configuration

### .streamlit/config.toml Template

```toml
# .streamlit/config.toml
# Configuration for Streamlit Cloud and local deployment

# ========================================================================
# Client Configuration
# ========================================================================
[client]
# Show warning about uncaught script errors
showErrorDetails = true

# Logger format
logger.level = "info"

# Code editor font size (default: 14)
codeBlockDefaultHeight = 300

# ========================================================================
# Server Configuration
# ========================================================================
[server]
# Enable CORS (for requests from different domains)
enableCORS = false

# Allow running the app without a headless browser (local only)
headless = true

# Port for local development
port = 8501

# Max message size for WebSocket (in MB)
maxMessageSize = 200

# ========================================================================
# Browser Configuration
# ========================================================================
[browser]
# Gather usage stats anonymously
gatherUsageStats = true

# ========================================================================
# Logger Configuration
# ========================================================================
[logger]
# Logging level: "error", "warning", "info", "debug"
level = "info"

# Log message format
messageFormat = "%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s"

# ========================================================================
# Theme Configuration
# ========================================================================
[theme]
# Primary color
primaryColor = "#1f77b4"

# Background color
backgroundColor = "#f8f9fa"

# Secondary background color
secondaryBackgroundColor = "#ffffff"

# Text color
textColor = "#2c3e50"

# Font family
font = "sans serif"

# ========================================================================
# Runtime Configuration
# ========================================================================
[client.toolbarMode]
# "minimal" hides most toolbar items; "developer" shows all
mode = "minimal"
```

### Deployment Environment Setup

```bash
# .streamlit/secrets.toml (local development only, never commit)
# For Streamlit Cloud, set secrets via web interface

# Example secrets (if needed for API keys, database URLs, etc.)
# OPENAI_API_KEY = "sk-..."
# LLMS_PATH = "/var/data/llms.txt"
```

---

## Requirements.txt Management

### Requirements.txt with Pinned Versions

```
# requirements.txt
# The DocStratum v0.4.1 Streamlit Demo Dependencies

# ========================================================================
# Core Dependencies
# ========================================================================

# Streamlit framework
streamlit==1.28.1

# Data processing
pydantic==2.5.0
pyyaml==6.0.1
pandas==2.1.3

# ========================================================================
# LLM & AI Integrations
# ========================================================================

# LangChain for LLM orchestration
langchain==0.1.0
langchain-openai==0.0.5
langchain-community==0.0.10

# OpenAI API (if not using LangChain)
openai==1.3.5

# ========================================================================
# Database (Optional)
# ========================================================================

# Neo4j graph database (optional, for concept mapping)
# neo4j==5.14.1

# ========================================================================
# Utilities
# ========================================================================

# Environment variable management
python-dotenv==1.0.0

# Type checking & validation
typing-extensions==4.8.0

# ========================================================================
# Development Dependencies (Optional, not for deployment)
# ========================================================================

# Uncomment for local development only
# pytest==7.4.3
# black==23.11.0
# flake8==6.1.0
# mypy==1.7.0
```

### Dependency Management Best Practices

| Practice | Why | Example |
|----------|-----|---------|
| **Pin all versions** | Prevent breaking changes in production | `streamlit==1.28.1` not `streamlit>=1.0` |
| **Use compatible releases** | Allow patch updates only | `streamlit==1.28.*` allows 1.28.5, not 1.29.0 |
| **Group by purpose** | Easier to understand dependencies | Core, AI, Database, Utilities sections |
| **Comment version rationale** | Help future maintainers | `# 2.0+ breaks session_state` |
| **Separate dev dependencies** | Keep production lean | Use `requirements-dev.txt` for test tools |
| **Test dependencies before pinning** | Avoid version conflicts | Test in venv before committing |

### Alternative: requirements-dev.txt

```
# requirements-dev.txt
# Development dependencies (not for deployment)

# Include production requirements
-r requirements.txt

# Testing
pytest==7.4.3
pytest-cov==4.1.0

# Code quality
black==23.11.0
flake8==6.1.0
pylint==3.0.3
mypy==1.7.0

# Documentation
sphinx==7.2.6
sphinx-rtd-theme==2.0.0

# Debugging
ipdb==0.13.13
ipython==8.17.2
```

---

## Smoke Testing Strategy

### Smoke Test Checklist

```python
# tests/test_smoke.py
# Quick smoke tests to verify basic functionality before deployment

import streamlit as st
from pathlib import Path

def test_imports():
    """Test that all modules can be imported."""
    try:
        from config import APP_TITLE, SAMPLE_QUESTIONS
        from components import inject_custom_css
        from src.docstratum.core.llm_resolver import resolve
        assert APP_TITLE == "DocStratum"
        assert len(SAMPLE_QUESTIONS) > 0
        print("✅ Imports successful")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        raise

def test_config_validation():
    """Test that configuration is valid."""
    try:
        from config import validate_config
        assert validate_config()
        print("✅ Configuration validation passed")
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        raise

def test_paths():
    """Test that required directories and files exist or can be created."""
    try:
        required_dirs = ["demo", "src/docstratum", "tests", ".streamlit"]
        for dir_path in required_dirs:
            p = Path(dir_path)
            assert p.exists() and p.is_dir(), f"Missing directory: {dir_path}"
        print("✅ Directory structure valid")
    except Exception as e:
        print(f"❌ Path validation failed: {e}")
        raise

def test_css_injection():
    """Test that CSS injection doesn't error."""
    try:
        from components import inject_custom_css
        # Don't actually inject CSS outside of Streamlit context,
        # but verify the function exists and is callable
        assert callable(inject_custom_css)
        print("✅ CSS injection function available")
    except Exception as e:
        print(f"❌ CSS injection test failed: {e}")
        raise

def test_sample_questions():
    """Test that sample questions are well-formed."""
    try:
        from config import SAMPLE_QUESTIONS, DIFFICULTY_LEVELS
        for i, q in enumerate(SAMPLE_QUESTIONS):
            assert "question" in q, f"Question {i} missing 'question' field"
            assert "category" in q, f"Question {i} missing 'category' field"
            assert "difficulty" in q, f"Question {i} missing 'difficulty' field"
            assert len(q["question"]) > 0, f"Question {i} is empty"
            assert q["difficulty"] in DIFFICULTY_LEVELS, f"Question {i} has invalid difficulty"
        print(f"✅ All {len(SAMPLE_QUESTIONS)} sample questions valid")
    except Exception as e:
        print(f"❌ Sample question validation failed: {e}")
        raise

if __name__ == "__main__":
    print("Running smoke tests...")
    test_imports()
    test_config_validation()
    test_paths()
    test_css_injection()
    test_sample_questions()
    print("\n✅ All smoke tests passed!")
```

### Running Smoke Tests

```bash
# From project root
python tests/test_smoke.py

# Expected output:
# Running smoke tests...
# ✅ Imports successful
# ✅ Configuration validation passed
# ✅ Directory structure valid
# ✅ CSS injection function available
# ✅ All 6 sample questions valid
#
# ✅ All smoke tests passed!
```

---

## Deployment Checklist

### Pre-Deployment Verification

- [ ] All imports resolve without errors (test_imports passes)
- [ ] Configuration validates correctly (test_config_validation passes)
- [ ] Directory structure is complete (test_paths passes)
- [ ] All sample questions are valid (test_sample_questions passes)
- [ ] CSS injection function available (test_css_injection passes)
- [ ] No hardcoded API keys or secrets in code
- [ ] .gitignore includes `.streamlit/secrets.toml` and `__pycache__`
- [ ] requirements.txt is complete and tested
- [ ] All dependencies install without conflicts
- [ ] README.md is updated with deployment instructions
- [ ] GitHub repository is public (for Streamlit Cloud)
- [ ] Latest code is committed and pushed to main branch

### Streamlit Cloud Deployment Steps

```bash
# 1. Push latest code to GitHub
git add .
git commit -m "v0.4.1: Streamlit Scaffold ready for deployment"
git push origin main

# 2. Go to Streamlit Cloud: https://streamlit.io/cloud
# 3. Click "New app" → "Deploy an existing repo"
# 4. Select:
#    - Repository: docstratum
#    - Branch: main
#    - Main file path: demo/app.py

# 5. Set secrets (if needed) in Streamlit Cloud dashboard
# 6. App deploys automatically

# 7. Verify app is live: https://docstratum.streamlit.app
```

### Post-Deployment Verification

```python
# Manual smoke test in deployed app

# 1. Verify page loads (check title "DocStratum" in tab)
# 2. Type a sample question in input field
# 3. Click "Compare" button
# 4. Verify spinner appears
# 5. Verify results display after processing
# 6. Click "Clear" button
# 7. Verify state resets
# 8. Select a sample question from sidebar
# 9. Verify question populates input field
# 10. Check console (F12) for JavaScript errors
# 11. Check error messages are readable
# 12. Test responsive layout on mobile (F12 → Mobile)
# 13. Verify CSS classes are applied (inspect element)
# 14. Check that error/warning messages display correctly
```

---

## Deliverables Checklist

- [ ] Custom CSS code created and documented
- [ ] CSS injection function (inject_custom_css) implemented
- [ ] CSS class reference table with all classes documented
- [ ] CSS variables defined for theming (colors, spacing, shadows)
- [ ] Dark mode CSS included (media query)
- [ ] Responsive design CSS (media queries for mobile)
- [ ] .streamlit/config.toml template created
- [ ] requirements.txt created with pinned versions
- [ ] requirements-dev.txt created for development
- [ ] Smoke test suite implemented (test_smoke.py)
- [ ] Deployment checklist documented
- [ ] Post-deployment verification steps documented
- [ ] GitHub deployment workflow documented
- [ ] Security checklist (no hardcoded secrets)
- [ ] Performance considerations documented

---

## Acceptance Criteria

- [ ] CSS injection executes without errors
- [ ] All CSS classes render correctly in app
- [ ] Result boxes display with correct colors and styling
- [ ] Metrics row displays horizontally and responsively
- [ ] Input field focuses and shows focus state
- [ ] Buttons are clickable and show hover state
- [ ] Error/warning messages display in correct colors
- [ ] Sidebar styling is applied correctly
- [ ] Layout is responsive on mobile devices
- [ ] .streamlit/config.toml is valid TOML
- [ ] requirements.txt installs without conflicts (test with `pip install -r requirements.txt`)
- [ ] Smoke tests pass: `python tests/test_smoke.py`
- [ ] No hardcoded secrets found in codebase
- [ ] App deploys to Streamlit Cloud without errors
- [ ] Deployed app is accessible at public URL
- [ ] All CSS styling works correctly in deployed app
- [ ] Dark mode CSS applies when system prefers dark mode

---

## Next Step

**v0.4.1 Complete!** Proceed to **v0.4.2a — Component Library & Reusable Widgets** to design and implement a library of reusable Streamlit components for displaying results, metrics, and interactive visualizations.

---

## Deployment Quick Reference

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run app locally
streamlit run demo/app.py

# App opens at http://localhost:8501
```

### Streamlit Cloud Deployment

```bash
# 1. Ensure code is on GitHub (main branch)
# 2. Visit https://streamlit.io/cloud
# 3. Deploy from main branch at demo/app.py
# 4. App lives at https://docstratum.streamlit.app
```

### Environment Variables (Streamlit Cloud)

In the Streamlit Cloud dashboard, set secrets:

```toml
# Streamlit Cloud Secrets
DOCSTRATUM_DEBUG = "false"
DOCSTRATUM_LLMS_PATH = "./data/llms.txt"
DOCSTRATUM_THEME_MODE = "light"
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| CSS not applying | Check `unsafe_allow_html=True` is set in st.markdown() |
| Import errors | Verify all modules in requirements.txt are installed |
| Session state issues | Check init_session_state() is called early in app.py |
| Dark mode not applying | Ensure CSS media query `@media (prefers-color-scheme: dark)` is present |
| Deployment fails | Check GitHub branch is main, no API keys in code, requirements.txt is valid |

