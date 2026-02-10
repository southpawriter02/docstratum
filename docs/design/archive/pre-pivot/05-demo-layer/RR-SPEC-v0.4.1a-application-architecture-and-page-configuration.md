# v0.4.1a — Application Architecture & Page Configuration

> This sub-part defines the Streamlit application architecture, page configuration, and module layout for The DocStratum v0.4.1. It establishes the foundational structure upon which all interactive components are built, ensuring optimal performance, maintainability, and adherence to Streamlit's execution model.

---

## Objective

Design and document the Streamlit application architecture that serves as the foundation for The DocStratum's interactive layer. This includes:
- Defining the Streamlit application lifecycle and execution model
- Configuring page-level settings (layout, sidebar behavior, page title/icon)
- Establishing module dependency graph and import strategy
- Documenting directory structure rationale and entry point design
- Providing clear guidance for module organization and lazy imports

---

## Scope Boundaries

| Aspect | In Scope | Out of Scope |
|--------|----------|--------------|
| Page configuration | `st.set_page_config()` settings, layout options, icon/title | Favicon files, CDN resources |
| Module structure | demo/, config.py, app.py, components.py organization | External dependency versions |
| Imports | Lazy imports, performance optimization patterns | Third-party library internals |
| Entry point | `streamlit run demo/app.py` setup and execution | Docker/container orchestration |
| Lifecycle | Streamlit reruns, initialization hooks, caching | State persistence across deployments |
| Dependency graph | Internal module relationships and flow | System-level dependencies |

---

## Streamlit Application Lifecycle & Execution Model

Streamlit re-executes your entire script from top to bottom on every user interaction (button clicks, text input, slider adjustments). Understanding this model is critical for building performant and maintainable applications.

### Key Lifecycle Phases

1. **Initialization Phase**: Script executes, imports load, page config sets
2. **Widget Render Phase**: Streamlit rerenders UI elements and collects user input
3. **Callback Phase**: User interactions trigger widget callbacks (if defined)
4. **Rerun Phase**: Script reruns with updated widget values in session state

### Execution Model Implications

| Phase | Characteristic | Implication |
|-------|----------------|-------------|
| **Top-to-bottom** | Script always executes sequentially from line 1 | Code order matters; sidebar widgets execute early |
| **Rerun on interaction** | Every button click or input change triggers full rerun | Use session state to preserve data across reruns |
| **No global state persistence** | Variables declared at module level reinitialize | Leverage `st.session_state` for persistence |
| **Caching opportunities** | `@st.cache_data` and `@st.cache_resource` prevent recomputation | Cache expensive operations (API calls, data loading) |
| **Stateless by default** | Each rerun starts fresh unless session state explicitly maintained | Initialize session state variables early |

### Streamlit Execution Diagram

```
┌─────────────────────────────────────┐
│   User Opens App / Interaction      │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│   1. Load config (set_page_config)  │
│      • Page title, icon, layout     │
│      • Sidebar behavior             │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│   2. Import Modules (top-to-bottom) │
│      • config.py (constants)        │
│      • components.py (UI elements)  │
│      • Initialize session state     │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│   3. Render Sidebar Widgets         │
│      • Config options               │
│      • Sample questions             │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│   4. Render Main Content Widgets    │
│      • Text input                   │
│      • Compare/Clear buttons        │
│      • Results display              │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│   5. Await User Interaction         │
│      (Script pauses here)           │
└────────────────┬────────────────────┘
                 │
      ┌──────────┴──────────┐
      │ User clicks/changes  │
      │ widget value?        │
      │                      │
      ▼                      │
┌─────────────────┐     No   │
│ Yes, rerun from │◄─────────┘
│ top (with new   │
│ session state)  │
└─────────────────┘
```

---

## Page Configuration Options & Rationale

### st.set_page_config() Settings Table

| Setting | Value | Rationale |
|---------|-------|-----------|
| **page_title** | "DocStratum" | Appears in browser tab; reinforces brand identity |
| **page_icon** | "🌳" or ":evergreen_tree:" | Memorable visual identifier; aligns with "Root" metaphor |
| **layout** | "wide" | Maximizes horizontal space for side-by-side comparisons (baseline vs. DocStratum) |
| **initial_sidebar_state** | "expanded" | Encourages users to explore sample questions; makes config accessible |
| **menu_items** | Custom dict | Hides unnecessary menu items; customizes "About" section |

### Page Configuration Rationale

**Wide Layout**: The "wide" layout setting is chosen because v0.4.1 displays results in side-by-side columns (baseline output vs. DocStratum-enhanced output). A single-column layout would force results to stack vertically, reducing readability and context visibility.

**Expanded Sidebar**: The sidebar is expanded by default to surface sample questions prominently. Users unfamiliar with DocStratum's capabilities benefit from immediate access to curated example queries.

**Custom Menu**: The Streamlit menu (gear icon, top-right) is customized to remove debugging options and provide branded "About" and "Documentation" links.

### Page Configuration Code Template

```python
import streamlit as st

st.set_page_config(
    page_title="DocStratum",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/docstratum/issues",
        "Report a bug": "https://github.com/docstratum/issues",
        "About": "# DocStratum v0.4.1\nSemantic translation layer for LLM agents."
    }
)
```

---

## Module Dependency Graph & Organization

### Dependency Flow Diagram

```
┌──────────────────────────┐
│   demo/app.py            │
│   (Entry Point)          │
└────────────┬─────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌─────────────┐  ┌──────────────┐
│config.py    │  │components.py │
│(Constants)  │  │(UI Elements) │
└──────┬──────┘  └──────┬───────┘
       │                │
       │                ▼
       │         ┌──────────────────┐
       │         │ Core modules     │
       │         │ (llm_resolver,   │
       │         │  concept_map,    │
       │         │  few_shot_bank)  │
       │         └──────────────────┘
       │
       ▼
┌──────────────────────┐
│demo/__init__.py      │
│(Package marker)      │
└──────────────────────┘
```

### Module Organization Table

| Module | Responsibility | Dependencies |
|--------|-----------------|--------------|
| **demo/__init__.py** | Package initialization; version info | None |
| **demo/config.py** | Constants, app configuration, sample questions | None (stdlib only) |
| **demo/app.py** | Main entry point, page config, layout, state management | config.py, components.py, core modules |
| **demo/components.py** | Reusable UI components, custom widgets | config.py, core modules |
| **core/*** | LLM resolution, concept mapping, few-shot banking | External (LangChain, Pydantic, YAML) |

---

## Directory Structure Rationale

### Full Directory Layout

```
docstratum/
├── docs/
│   └── v0.4.1/
│       ├── v0.4.1a — Application Architecture.md
│       ├── v0.4.1b — Configuration Module.md
│       ├── v0.4.1c — Session State.md
│       └── v0.4.1d — Custom Styling.md
├── demo/
│   ├── __init__.py
│   ├── app.py
│   ├── config.py
│   └── components.py
├── src/
│   ├── docstratum/
│   │   ├── core/
│   │   │   ├── llm_resolver.py
│   │   │   ├── concept_map.py
│   │   │   └── few_shot_bank.py
│   │   ├── models/
│   │   │   └── llms_file.py
│   │   └── utils/
│   │       └── yaml_parser.py
│   └── __init__.py
├── tests/
│   ├── test_config.py
│   ├── test_app.py
│   └── test_core.py
├── .streamlit/
│   └── config.toml
├── requirements.txt
├── pyproject.toml
└── README.md
```

### Rationale for Structure

| Directory | Rationale |
|-----------|-----------|
| **demo/** | Isolated Streamlit app; keeps UI separate from core logic; easy to swap or upgrade UI layer |
| **src/docstratum/** | Core business logic lives in proper Python package structure; reusable across different UIs |
| **.streamlit/** | Streamlit configuration separate from Python code; environment-specific overrides |
| **tests/** | Mirror structure of src/ and demo/ for test organization and discovery |

---

## Import Strategy & Lazy Imports for Performance

### Import Principles

1. **Eager imports (at top of app.py)**: Streamlit modules, config, components
2. **Lazy imports (inside functions/callbacks)**: Heavy third-party libraries (LangChain, OpenAI, Neo4j)
3. **Cache expensive imports**: Use `@st.cache_resource` for singleton imports

### Import Optimization Table

| Library | Import Style | Reason |
|---------|--------------|--------|
| streamlit | Eager (top-level) | Required for all Streamlit apps; lightweight |
| config | Eager (top-level) | Small module; sets constants throughout app |
| components | Eager (top-level) | Defines UI element functions; lightweight |
| langchain | Lazy (in callbacks) | Heavy dependency; only needed when processing questions |
| openai | Lazy (in callbacks) | Network-dependent; slow to import; only used on demand |
| neo4j | Lazy (optional, in callbacks) | Only imported if Neo4j is enabled in config |

### Code Example: Lazy Import Pattern

```python
# demo/app.py - Eager imports at top
import streamlit as st
from config import APP_TITLE, SAMPLE_QUESTIONS
from components import render_sidebar

# Later, inside a callback or function
def process_question(question: str):
    # Lazy import - only executed when called
    from src.docstratum.core.llm_resolver import resolve

    result = resolve(question)
    return result

# Alternative: Cache the import
@st.cache_resource
def get_llm_resolver():
    from src.docstratum.core.llm_resolver import LLMResolver
    return LLMResolver()

resolver = get_llm_resolver()
```

---

## Application Entry Point Design

### Entry Point Command

```bash
streamlit run demo/app.py
```

### Why This Entry Point Structure?

1. **Explicit demo/ package**: Signals that demo is the Streamlit app; keeps it separate from core logic
2. **Clear entry file (app.py)**: Immediately obvious that app.py is the main entry point
3. **config.py imported explicitly**: No magic imports; dependencies are visible

### Entry Point Execution Flow

```
1. User runs: streamlit run demo/app.py
   ↓
2. Streamlit loads demo/app.py
   ↓
3. app.py imports config.py (constants)
   ↓
4. app.py imports components.py (UI functions)
   ↓
5. app.py executes st.set_page_config()
   ↓
6. app.py initializes session state
   ↓
7. app.py renders sidebar (config, sample questions)
   ↓
8. app.py renders main content (input, buttons, results)
   ↓
9. Streamlit awaits user interaction
   ↓
10. User clicks button or enters text → Rerun from step 5
```

### demo/__init__.py Template

```python
"""
The DocStratum - Streamlit Demo Application
v0.4.1: Streamlit Scaffold

A semantic translation layer between documentation websites and AI agents.
"""

__version__ = "0.4.1"
__author__ = "DocStratum Team"
__description__ = "Interactive Streamlit demo for The DocStratum"
```

---

## Deliverables Checklist

- [ ] Page configuration (`st.set_page_config()`) documented with all options
- [ ] Streamlit lifecycle diagram created (ASCII art)
- [ ] Module dependency graph established and documented
- [ ] Directory structure rationale documented
- [ ] Import strategy (eager vs. lazy) defined
- [ ] demo/__init__.py template provided
- [ ] Entry point execution flow diagram created
- [ ] All rationale explanations included for each architectural decision
- [ ] Code examples provided for configuration and imports
- [ ] Performance implications noted for each design choice

---

## Acceptance Criteria

- [ ] Page opens without errors when running `streamlit run demo/app.py`
- [ ] Page title "DocStratum" appears in browser tab
- [ ] Page icon (🌳) displays in browser tab
- [ ] Layout is set to "wide" (verified by inspecting full-width rendering space)
- [ ] Sidebar is expanded on initial load
- [ ] Custom menu items appear in Streamlit menu (gear icon, top-right)
- [ ] Module imports follow lazy/eager pattern as documented
- [ ] No circular import dependencies exist
- [ ] All referenced files in module structure exist or have creation tasks
- [ ] Performance is acceptable (page loads in <2 seconds on typical connection)

---

## Next Step

Proceed to **v0.4.1b — Configuration Module & Sample Data** to design the configuration constants (APP_TITLE, APP_SUBTITLE, SAMPLE_QUESTIONS) and theme/CSS settings.
