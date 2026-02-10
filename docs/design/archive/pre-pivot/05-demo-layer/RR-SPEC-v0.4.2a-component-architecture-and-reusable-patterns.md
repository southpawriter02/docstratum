# v0.4.2a — Component Architecture & Reusable Patterns

> **Task:** Design the reusable UI component architecture for the comparison display. Establish composable, stateless component patterns that serve as the foundation for rendering side-by-side responses with proper parameterization and lifecycle management.

---

## Objective

Establish a robust, composable component architecture that enables flexible rendering of comparison UI elements. This sub-part defines the foundational design philosophy, component hierarchy, parameter patterns, and lifecycle considerations that will guide implementation of all rendering components in v0.4.2. By creating reusable, parameterized components, we enable consistent, maintainable UI code and facilitate easier testing and future extensions.

---

## Scope Boundaries

| **In Scope** | **Out of Scope** |
|---|---|
| Component design philosophy and principles | Actual HTML/CSS implementation |
| Component hierarchy architecture (nesting relationships) | Styling details or color specifications |
| Parameter/props design patterns and specifications | State management beyond component lifecycle |
| Streamlit component lifecycle and rendering flow | Backend data fetching or processing |
| Container/column layout strategy and grid systems | Database schema or data model design |
| Component testing approach and structure | Integration testing with production systems |
| Reusability patterns for DRY code | Performance optimization beyond architecture |

---

## Dependency Diagram

```
┌─────────────────────────────────────────────────────┐
│             Streamlit Application                    │
│  (Main entry point, app.py)                          │
└────────────────────┬────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
   ┌─────────┐  ┌─────────┐  ┌──────────┐
   │ render_ │  │ render_ │  │ render_  │
   │comparison│  │response_│  │ analysis │
   │()       │  │ card()  │  │()       │
   └────┬────┘  └────┬────┘  └────┬─────┘
        │             │            │
        └─────────────┼────────────┘
                      │
          ┌───────────┴───────────┐
          │                       │
          ▼                       ▼
     ┌─────────────┐      ┌──────────────┐
     │ Streamlit   │      │ ABTestResult │
     │ Container   │      │ Data Model   │
     │ Components  │      │              │
     └─────────────┘      └──────────────┘
```

---

## 1. Component Design Philosophy

The component architecture is built on five core principles:

### 1.1 Composability
Components are designed to work independently or be combined into larger structures. Each component encapsulates a single responsibility and can be reused in different contexts.

### 1.2 Statelessness
All components are stateless (functional). They accept input parameters and produce output without maintaining internal state. Streamlit's session_state manages any required state at the application level.

### 1.3 Parameterization
Components are highly parameterized to maximize reusability. Rather than hardcoding values, all configuration is passed as function parameters with sensible defaults.

### 1.4 Immutability
Component parameters are immutable. Once passed to a component, parameters are not modified by the component. Any changes require re-calling the component with new parameters.

### 1.5 Clarity
Component APIs are explicit and self-documenting. Parameter names clearly indicate purpose; return values are typed and documented.

---

## 2. Component Hierarchy

The comparison display uses a three-level component hierarchy:

```
Level 1 (Orchestration)
├── render_comparison()
│   ├── Accepts: comparison_data dict with baseline and docstratum responses
│   ├── Accepts: display_options dict with layout preferences
│   └── Responsibility: Create st.columns(2), orchestrate Levels 2 & 3

Level 2 (Composition)
├── render_response_card() [called once per column]
│   ├── Accepts: response data, label, styling flags
│   ├── Responsibility: Render single response with metrics
│   └── Internal calls: markdown rendering, metric formatting
│
└── render_analysis() [called below columns]
    ├── Accepts: both response objects for comparison
    ├── Responsibility: Detect and display quality signals
    └── Internal calls: signal detection functions

Level 3 (Primitives - Streamlit built-ins)
├── st.markdown() — Render markdown content
├── st.metric() — Display key metrics
├── st.divider() — Visual separators
└── st.columns() — Layout structure
```

### Hierarchy Rationale

- **Level 1 (render_comparison)**: Handles the two-column layout orchestration. Creates a container for the entire comparison view.
- **Level 2 (render_response_card, render_analysis)**: Domain-specific components that encapsulate response or analysis rendering logic.
- **Level 3 (Streamlit primitives)**: Native Streamlit components that Level 2 builds upon.

This hierarchy enables:
- Independent testing of Level 2 components
- Easy swapping of layout strategies at Level 1
- Clear separation of concerns (rendering vs. analysis)

---

## 3. Parameters & Props Design Pattern

### 3.1 Parameter Naming Convention

Parameters follow this naming convention for clarity:

```python
# Prefix conventions:
is_<boolean>    # Boolean flags (is_enhanced, is_selected)
<noun>_data     # Data payloads (response_data, comparison_data)
<verb>_options  # Configuration objects (display_options, style_options)
on_<event>      # Callbacks (on_click, on_select) [optional for v0.4.2]

# Examples:
is_enhanced: bool                    # Visual distinction flag
response_data: dict                  # Full response content
display_options: dict                # Layout and display preferences
```

### 3.2 Component Parameter Specifications

#### render_comparison()

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| comparison_data | dict | Yes | — | Dict with 'baseline' and 'docstratum' response objects |
| display_options | dict | No | {} | Layout preferences (gap size, column widths, etc.) |
| show_analysis | bool | No | True | Whether to render analysis section below columns |

#### render_response_card()

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| response_data | dict | Yes | — | Response object with text, tokens, latency |
| card_label | str | Yes | — | Label for card (e.g., "Baseline", "DocStratum") |
| is_enhanced | bool | No | False | Visual styling flag (green border vs. red) |
| show_metrics | bool | No | True | Whether to display token/latency metrics |
| max_height | str | No | "500px" | CSS max-height for response container |

#### render_analysis()

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| baseline_response | dict | Yes | — | Baseline response object |
| docstratum_response | dict | Yes | — | DocStratum response object |
| analysis_config | dict | No | {} | Configuration for signal detection |

### 3.3 Return Value Pattern

All component functions return `None` in Streamlit (they render side effects). However, conceptually:

```python
def render_comparison(comparison_data, display_options=None, show_analysis=True):
    """
    Returns: None (renders to Streamlit)
    Side effects:
    - Renders two columns with response cards
    - Renders analysis section if show_analysis=True
    """
    pass

def render_response_card(response_data, card_label, is_enhanced=False,
                         show_metrics=True, max_height="500px"):
    """
    Returns: None (renders to Streamlit)
    Side effects:
    - Renders card container with response text and metrics
    """
    pass
```

---

## 4. Streamlit Component Lifecycle

Understanding Streamlit's execution model is critical for building correct components:

### 4.1 Rendering Flow

```
1. User interacts with app (or app re-runs)
                    ↓
2. Streamlit re-executes app.py from top to bottom
                    ↓
3. render_comparison() is called with current parameters
                    ↓
4. render_comparison() calls st.columns(2)
                    ↓
5. render_response_card() called in left column context
   └─ Renders markdown, metrics via st.markdown(), st.metric()
                    ↓
6. render_response_card() called in right column context
   └─ Renders markdown, metrics via st.markdown(), st.metric()
                    ↓
7. render_analysis() called below columns
   └─ Renders analysis section
                    ↓
8. Streamlit renders all queued elements to browser
```

### 4.2 Key Lifecycle Considerations

**Re-execution Model**
- Components must be re-execution safe (no side effects outside Streamlit)
- All component state comes from parameters; nothing persists between runs
- Use `@st.cache_data` for expensive computations outside components

**Context Management**
- `st.columns(2)` creates context managers; render_response_card() must be called within column context:
  ```python
  col1, col2 = st.columns(2)
  with col1:
      render_response_card(baseline_data, "Baseline")  # Renders in col1
  with col2:
      render_response_card(docstratum_data, "DocStratum")    # Renders in col2
  ```

**Widget Keys**
- Streamlit requires unique keys for interactive widgets; for v0.4.2 (display-only), not needed
- Future versions with interactive elements must include parameter for key prefix:
  ```python
  st.button("Expand", key=f"{card_label}_expand")
  ```

---

## 5. Container & Column Layout Strategy

### 5.1 Layout Grid System

The comparison view uses a grid-based layout:

```
┌──────────────────────────────────────────────────────────┐
│  Main Container (st.container or implicit)               │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Header Section (Title, Metadata)                   │  │
│  └────────────────────────────────────────────────────┘  │
│                                                           │
│  ┌────────────────────┬────────────────────────────────┐  │
│  │ Column 1 (Left)    │ Column 2 (Right)              │  │
│  │ Gap: "large"       │                               │  │
│  │ ┌──────────────┐   │ ┌──────────────────────────┐  │  │
│  │ │ Card Label   │   │ │ Card Label               │  │  │
│  │ │ ┌──────────┐ │   │ │ ┌──────────────────────┐ │  │  │
│  │ │ │Response  │ │   │ │ │ Response             │ │  │  │
│  │ │ │Text      │ │   │ │ │ Text (Long Form)     │ │  │  │
│  │ │ │          │ │   │ │ │                      │ │  │  │
│  │ │ └──────────┘ │   │ │ └──────────────────────┘ │  │  │
│  │ │ ┌──────────┐ │   │ │ ┌──────────────────────┐ │  │  │
│  │ │ │Metrics   │ │   │ │ │ Metrics              │ │  │  │
│  │ │ └──────────┘ │   │ │ └──────────────────────┘ │  │  │
│  │ └──────────────┘   │ └──────────────────────────┘  │  │
│  └────────────────────┴────────────────────────────────┘  │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Analysis Section (Quality Signals)                 │  │
│  │ ┌──────────────────────────────────────────────┐  │  │
│  │ │ Signal Detection Results                     │  │  │
│  │ └──────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

### 5.2 Column Configuration

```python
# render_comparison() layout logic
col1, col2 = st.columns(
    spec=[1, 1],          # Equal width columns
    gap="large"           # Large gap between columns (default: "medium")
)

# Gap options: "small", "medium", "large"
# This parameter is passed via display_options dict
```

### 5.3 Container Nesting Strategy

```python
def render_comparison(comparison_data, display_options=None, show_analysis=True):
    display_options = display_options or {}

    # Optional: Explicit container for entire comparison
    with st.container(border=False):  # Streamlit 1.22+

        # Column layout
        col1, col2 = st.columns([1, 1], gap=display_options.get("gap", "large"))

        with col1:
            render_response_card(
                comparison_data["baseline"],
                "Baseline",
                is_enhanced=False
            )

        with col2:
            render_response_card(
                comparison_data["docstratum"],
                "DocStratum",
                is_enhanced=True
            )

    # Analysis section (outside columns, full width)
    if show_analysis:
        st.divider()
        render_analysis(
            comparison_data["baseline"],
            comparison_data["docstratum"],
            analysis_config=display_options.get("analysis_config", {})
        )
```

---

## 6. Component Testing Approach

### 6.1 Testing Strategy

Components are tested at two levels:

**Unit Testing** (Python)
- Test component logic without Streamlit (parameter validation, data transformation)
- Mock Streamlit rendering functions
- Verify parameter handling and edge cases

**Integration Testing** (Streamlit Testing Framework)
- Test components in actual Streamlit context
- Verify rendering output and layout
- Use `streamlit.testing.v1` (Streamlit 1.25+)

### 6.2 Test Structure

```python
# tests/test_components.py

def test_render_response_card_with_valid_data():
    """Test render_response_card accepts valid parameters"""
    response_data = {
        "text": "Sample response",
        "tokens": (10, 20),
        "latency": 1.5
    }
    # In actual test, would use Streamlit testing harness
    # to verify rendering output

def test_render_response_card_missing_metrics():
    """Test render_response_card handles missing metrics gracefully"""
    response_data = {
        "text": "Sample response",
        "tokens": None,
        "latency": None
    }
    # Verify graceful degradation

def test_render_comparison_column_layout():
    """Test render_comparison creates two-column layout"""
    comparison_data = {
        "baseline": {...},
        "docstratum": {...}
    }
    # Verify st.columns(2) is called with correct parameters
```

### 6.3 Testing Tools

- **pytest**: Unit testing framework
- **streamlit.testing.v1**: Streamlit's built-in testing harness
- **unittest.mock**: Mock Streamlit functions for isolated unit tests

### 6.4 Component Contract

Each component has a explicit contract:

```python
def render_response_card(response_data: dict, card_label: str,
                         is_enhanced: bool = False,
                         show_metrics: bool = True,
                         max_height: str = "500px") -> None:
    """
    Render a single response card with metrics and styling.

    Args:
        response_data: Dict with keys 'text', 'tokens' (tuple), 'latency' (float)
        card_label: Display label for the card (e.g., "Baseline", "DocStratum")
        is_enhanced: If True, apply enhanced styling (green border)
        show_metrics: If True, display token and latency metrics
        max_height: CSS max-height for scrollable content area

    Raises:
        ValueError: If response_data missing required keys
        TypeError: If card_label is not a string

    Side Effects:
        Renders markdown and metrics to Streamlit
    """
    # Implementation
```

---

## Deliverables Checklist

- [ ] Component design philosophy documented with 5 core principles
- [ ] Three-level component hierarchy defined with ASCII diagram
- [ ] Parameter naming conventions established
- [ ] Parameter specification tables for all three main components
- [ ] Streamlit component lifecycle flowchart created
- [ ] Container/column layout grid system documented with ASCII diagram
- [ ] Component testing approach defined with unit and integration strategies
- [ ] Component contracts (docstrings) template created
- [ ] Dependency diagram showing component relationships

---

## Acceptance Criteria

- [ ] All five design principles are clearly explained with rationale
- [ ] Component hierarchy clearly shows Level 1 → 2 → 3 structure
- [ ] Parameter tables include all required and optional parameters with defaults
- [ ] Lifecycle flowchart shows re-execution model and context management
- [ ] Layout grid diagram accurately represents two-column plus analysis structure
- [ ] Testing approach includes both unit and integration test types
- [ ] Each component has explicit parameter specifications and type hints
- [ ] Documentation is implementation-agnostic (design before code)
- [ ] All diagrams are in ASCII format and render correctly

---

## Next Step

→ **v0.4.2b — Response Card Rendering & Formatting**

Implement the render_response_card() component with markdown rendering, token/latency display, and visual distinction logic. Use the component architecture patterns defined here as the foundation.
