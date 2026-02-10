# v0.4.2d — Visual Design System & CSS Architecture

> **Task:** Implement the visual design system with CSS theming for baseline vs enhanced distinction. Establish CSS injection strategy, gradient backgrounds, colored borders, responsive layout considerations, and dark mode compatibility to create a professional, accessible comparison interface.

---

## Objective

Implement the visual design system that provides clear, intuitive visual distinction between baseline and DocStratum responses. This sub-part defines the CSS injection strategy for Streamlit, establishes color palettes for baseline (red) and enhanced (green) styling, implements gradient backgrounds and border systems, documents Streamlit CSS selector patterns, addresses responsive design considerations, and ensures dark mode compatibility. By creating a cohesive visual design system, we enable users to quickly understand response quality differences while maintaining professional aesthetics and accessibility standards.

---

## Scope Boundaries

| **In Scope** | **Out of Scope** |
|---|---|
| CSS injection strategy using st.markdown() | HTML structure or DOM manipulation |
| Color palette definition for baseline vs enhanced | Color theory or UX research justification |
| Gradient background design and implementation | Animation or transition effects |
| Border and spacing system | Font selection or typography system |
| Streamlit CSS selector patterns ([data-testid]) | Custom CSS framework development |
| Responsive layout breakpoints and strategy | Accessibility audit or WCAG compliance |
| Dark mode CSS variables and overrides | Testing on actual devices |
| CSS custom properties (variables) system | Theme persistence or localStorage |
| Container styling and elevation system | Print stylesheet design |
| Visual emphasis and hierarchy techniques | Browser compatibility testing |

---

## Dependency Diagram

```
┌──────────────────────────────────────────────────────┐
│          CSS Architecture & Injection                 │
└────────────────┬─────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
   CSS Variables     Streamlit Context
   ├─ Colors        ├─ st.markdown()
   ├─ Spacing       ├─ unsafe_allow_html=True
   ├─ Breakpoints   └─ CSS selector strategy
   └─ Fonts
        │
        └─────────────────┬─────────────────┐
                          │                 │
                  ┌───────▼──────┐  ┌───────▼──────┐
                  │   Component  │  │    Response  │
                  │   Styling    │  │    Card      │
                  │              │  │    Styling   │
                  └──────────────┘  └──────────────┘

CSS Injection Flow:
1. Render <style> block via st.markdown()
   ├─ Define CSS variables (colors, spacing)
   ├─ Define component classes (.baseline-card, .docstratum-card-enhanced)
   ├─ Define responsive breakpoints
   └─ Define dark mode overrides

2. HTML elements reference CSS classes
   └─ Applied via st.markdown() with unsafe_allow_html=True

3. Streamlit renders styled components to browser
   └─ CSS variables computed at runtime
```

---

## 1. CSS Injection Strategy in Streamlit

### 1.1 Why CSS Injection?

Streamlit's theming system is limited for complex custom styling. CSS injection via `st.markdown(unsafe_allow_html=True)` provides full control:

**Advantages:**
- Full CSS3 support (gradients, custom properties, flexbox)
- Dynamic CSS generation based on application state
- Component-scoped styling (no global namespace pollution)
- Easy to maintain (CSS in one place)

**Risks & Mitigations:**
- Risk: XSS vulnerability if user content in CSS
- Mitigation: Never include user input directly in CSS; sanitize first
- Risk: CSS specificity conflicts
- Mitigation: Use BEM naming convention and !important sparingly

### 1.2 CSS Injection Mechanism

```python
def inject_css_variables() -> None:
    """
    Inject CSS variables and component styles into Streamlit.

    This should be called once at the top of app.py.
    """
    css_injection = """
    <style>
    /* CSS Variables (Custom Properties) */
    :root {
        /* Baseline (red) color scheme */
        --baseline-primary: #cc3333;
        --baseline-dark: #8b0000;
        --baseline-light: #ffcccc;
        --baseline-bg: #fafafa;

        /* Enhanced/DocStratum (green) color scheme */
        --docstratum-primary: #33aa33;
        --docstratum-dark: #006600;
        --docstratum-light: #ccffcc;
        --docstratum-bg: #f0f8f0;

        /* Neutral colors */
        --text-primary: #1a1a1a;
        --text-secondary: #666666;
        --border-light: #e0e0e0;
        --border-dark: #999999;

        /* Spacing system */
        --spacing-xs: 4px;
        --spacing-sm: 8px;
        --spacing-md: 16px;
        --spacing-lg: 24px;
        --spacing-xl: 32px;

        /* Border radius */
        --radius-sm: 4px;
        --radius-md: 8px;
        --radius-lg: 12px;

        /* Typography */
        --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto';
        --font-size-sm: 12px;
        --font-size-base: 14px;
        --font-size-lg: 16px;
        --font-size-xl: 20px;
        --font-weight-normal: 400;
        --font-weight-bold: 600;

        /* Shadows */
        --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.12);
        --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.15);
        --shadow-lg: 0 10px 20px rgba(0, 0, 0, 0.20);
    }

    /* Dark mode overrides */
    @media (prefers-color-scheme: dark) {
        :root {
            --text-primary: #ffffff;
            --text-secondary: #cccccc;
            --border-light: #444444;
            --border-dark: #666666;
            --baseline-bg: #1a1a1a;
            --docstratum-bg: #0a2a0a;
        }
    }
    </style>
    """

    st.markdown(css_injection, unsafe_allow_html=True)
```

### 1.3 Injection Placement

```python
# app.py
import streamlit as st
from components import inject_css_variables, render_comparison

# 1. Inject CSS at app startup (top of app.py)
inject_css_variables()

# 2. Configure page
st.set_page_config(page_title="DocStratum")

# 3. App content
st.title("Side-by-Side Comparison")

# 4. Use components (which reference injected CSS classes)
render_comparison(comparison_data)
```

---

## 2. Gradient Background Design

### 2.1 Baseline Gradient (Red)

The baseline response uses a red gradient to indicate standard responses:

```css
.baseline-card {
    background: linear-gradient(
        135deg,
        #fafafa 0%,
        #ffe6e6 50%,
        #ffcccc 100%
    );
    border: 2px solid #cc3333;
    border-radius: 8px;
    padding: 16px;
    box-shadow: 0 2px 4px rgba(204, 51, 51, 0.1);
}

.baseline-card .card-header {
    background: linear-gradient(
        90deg,
        #ffcccc 0%,
        #ffe6e6 100%
    );
    border-left: 4px solid #8b0000;
    padding: 12px;
    border-radius: 4px;
    margin: -16px -16px 12px -16px;
}

.baseline-card .card-header h3 {
    color: #8b0000;
    margin: 0;
    font-size: 16px;
    font-weight: 600;
}
```

### 2.2 Enhanced/DocStratum Gradient (Green)

The DocStratum response uses a green gradient to indicate enhanced responses:

```css
.docstratum-card-enhanced {
    background: linear-gradient(
        135deg,
        #f0f8f0 0%,
        #e6ffe6 50%,
        #ccffcc 100%
    );
    border: 2px solid #33aa33;
    border-radius: 8px;
    padding: 16px;
    box-shadow: 0 2px 4px rgba(51, 170, 51, 0.1);
}

.docstratum-card-enhanced .card-header {
    background: linear-gradient(
        90deg,
        #ccffcc 0%,
        #e6ffe6 100%
    );
    border-left: 4px solid #006600;
    padding: 12px;
    border-radius: 4px;
    margin: -16px -16px 12px -16px;
}

.docstratum-card-enhanced .card-header h3 {
    color: #006600;
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    font-weight: bold;
}
```

### 2.3 Gradient Reference

| Gradient | Start Color | Middle | End Color | Purpose |
|---|---|---|---|---|
| Baseline | #fafafa | #ffe6e6 | #ffcccc | Base response, subtle red tint |
| DocStratum | #f0f8f0 | #e6ffe6 | #ccffcc | Enhanced response, green tint |
| Header (Baseline) | #ffcccc | — | #ffe6e6 | Darker baseline header area |
| Header (DocStratum) | #ccffcc | — | #e6ffe6 | Darker docstratum header area |

---

## 3. Border & Spacing System

### 3.1 Border System

```css
/* Border width conventions */
.border-thin {
    border: 1px solid var(--border-light);
}

.border-standard {
    border: 2px solid;
}

.border-thick {
    border: 3px solid;
}

/* Border left accent (for headers, highlights) */
.border-left-accent {
    border-left: 4px solid;
}

/* Component-specific borders */
.baseline-card {
    border: 2px solid var(--baseline-primary);
}

.docstratum-card-enhanced {
    border: 2px solid var(--docstratum-primary);
}

/* Divider styling */
.divider {
    border: none;
    border-top: 1px solid var(--border-light);
    margin: var(--spacing-lg) 0;
}

@media (prefers-color-scheme: dark) {
    .divider {
        border-top-color: var(--border-dark);
    }
}
```

### 3.2 Spacing System

```css
/* Component spacing */
.card-header {
    padding: var(--spacing-md);
    margin-bottom: var(--spacing-md);
}

.card-content {
    padding: var(--spacing-md);
    margin-bottom: var(--spacing-sm);
}

.card-metrics {
    padding: var(--spacing-md);
    border-top: 1px solid var(--border-light);
}

/* Gap between columns */
.comparison-container {
    column-gap: var(--spacing-lg);
    row-gap: var(--spacing-lg);
}

/* Analysis section spacing */
.analysis-section {
    margin-top: var(--spacing-xl);
    padding-top: var(--spacing-lg);
    border-top: 1px solid var(--border-light);
}
```

### 3.3 Spacing Grid

| Size | Value | Usage |
|---|---|---|
| XS | 4px | Micro-spacing (lists, inline elements) |
| SM | 8px | Small spacing (between items) |
| MD | 16px | Medium spacing (component padding) |
| LG | 24px | Large spacing (section spacing) |
| XL | 32px | Extra large spacing (major sections) |

---

## 4. Streamlit CSS Selector Patterns

### 4.1 Selector Strategy

Streamlit renders components with generated CSS classes. To target elements reliably:

```python
# Strategy 1: Use custom HTML wrappers with explicit classes
st.markdown(
    f"""
    <div class="response-card baseline-card">
        <div class="card-header">Baseline Response</div>
        <div class="card-content">{response_text}</div>
    </div>
    """,
    unsafe_allow_html=True
)

# Strategy 2: Target Streamlit-generated elements (fragile, not recommended)
# ❌ .stMetric > div > div  (relies on internal structure)
# ✅ .response-card .metric-display  (use semantic classes instead)
```

### 4.2 Available Selectors

```css
/* Custom classes (most reliable) */
.baseline-card { }
.docstratum-card-enhanced { }
.card-header { }
.card-content { }
.response-card { }
.analysis-section { }
.signal-card { }
.metric-display { }

/* Streamlit widget classes (documented) */
.stMetric { }      /* st.metric() container */
.stDivider { }     /* st.divider() line */
.stMarkdown { }    /* st.markdown() container */
.stContainer { }   /* st.container() wrapper */

/* Pseudo-classes for states */
.baseline-card:hover { /* Hover effects */ }
.response-card:focus-within { /* Focus effects */ }
```

### 4.3 Data Attributes Strategy

```python
# Use data attributes for semantic targeting and configuration
def render_response_card_with_attrs(response_data, card_label, is_enhanced=False):
    card_type = "docstratum" if is_enhanced else "baseline"

    st.markdown(
        f"""
        <div class="response-card"
             data-type="{card_type}"
             data-label="{card_label}"
             data-enhanced="{str(is_enhanced).lower()}">
            <!-- Content -->
        </div>
        """,
        unsafe_allow_html=True
    )

# CSS can then use attribute selectors
css = """
<style>
[data-type="baseline"] {
    border-color: var(--baseline-primary);
}

[data-type="docstratum"] {
    border-color: var(--docstratum-primary);
}

[data-enhanced="true"] {
    font-weight: 600;
}
</style>
"""
```

---

## 5. Responsive Layout Considerations

### 5.1 Responsive Breakpoints

```css
/* Desktop-first approach */
:root {
    /* Large screens (>1200px) */
    --col-width-large: 1fr 1fr;
    --font-size-base: 16px;
    --padding-base: 24px;
}

/* Tablets (768px - 1199px) */
@media (max-width: 1199px) {
    :root {
        --col-width-large: 1fr 1fr;
        --font-size-base: 15px;
        --padding-base: 20px;
    }
}

/* Small tablets / large phones (576px - 767px) */
@media (max-width: 767px) {
    :root {
        --col-width-large: 1fr;  /* Single column */
        --font-size-base: 14px;
        --padding-base: 16px;
    }
}

/* Small phones (<576px) */
@media (max-width: 575px) {
    :root {
        --col-width-large: 1fr;
        --font-size-base: 13px;
        --padding-base: 12px;
    }
}
```

### 5.2 Two-Column Layout Responsiveness

```css
.comparison-columns {
    display: grid;
    grid-template-columns: var(--col-width-large);
    gap: var(--spacing-lg);
    width: 100%;
}

/* Tablet: maintain two columns but reduce gap */
@media (max-width: 1199px) {
    .comparison-columns {
        gap: var(--spacing-md);
    }
}

/* Mobile: stack columns vertically */
@media (max-width: 767px) {
    .comparison-columns {
        grid-template-columns: 1fr;
        gap: var(--spacing-lg);
    }

    .response-card {
        max-height: 400px;
    }
}
```

### 5.3 Responsive Typography

```css
/* Base typography */
.card-header h3 {
    font-size: var(--font-size-xl);
    line-height: 1.3;
}

.card-content {
    font-size: var(--font-size-base);
    line-height: 1.6;
}

/* Tablet adjustments */
@media (max-width: 1199px) {
    .card-header h3 {
        font-size: 18px;
    }
}

/* Mobile adjustments */
@media (max-width: 767px) {
    .card-header h3 {
        font-size: 16px;
    }

    .card-content {
        font-size: 13px;
    }
}
```

### 5.4 Responsive Breakpoint Table

| Breakpoint | Width | Device | Grid | Font |
|---|---|---|---|---|
| Large Desktop | >1200px | Desktop | 1fr 1fr | 16px |
| Desktop | 1000-1199px | Laptop | 1fr 1fr | 15px |
| Tablet | 768-999px | Tablet | 1fr 1fr (narrow) | 14px |
| Small Mobile | 576-767px | Large Phone | 1fr (stack) | 14px |
| Mobile | <576px | Small Phone | 1fr (stack) | 13px |

---

## 6. Dark Mode Compatibility

### 6.1 Dark Mode CSS Variables

```css
/* Light mode (default) */
:root {
    --text-primary: #1a1a1a;
    --text-secondary: #666666;
    --bg-primary: #ffffff;
    --bg-secondary: #f5f5f5;
    --border-color: #e0e0e0;
}

/* Dark mode */
@media (prefers-color-scheme: dark) {
    :root {
        --text-primary: #ffffff;
        --text-secondary: #cccccc;
        --bg-primary: #1a1a1a;
        --bg-secondary: #2a2a2a;
        --border-color: #444444;
    }

    /* Darker baseline gradient in dark mode */
    .baseline-card {
        background: linear-gradient(
            135deg,
            #2a1a1a 0%,
            #3d1515 50%,
            #4d1515 100%
        );
    }

    /* Darker docstratum gradient in dark mode */
    .docstratum-card-enhanced {
        background: linear-gradient(
            135deg,
            #0a2a0a 0%,
            #153d15 50%,
            #154d15 100%
        );
    }
}
```

### 6.2 Dark Mode Color Adjustments

| Element | Light Mode | Dark Mode | Contrast Ratio |
|---|---|---|---|
| Text on Baseline | #8b0000 | #ff6666 | 4.5:1 ✓ |
| Text on DocStratum | #006600 | #66ff66 | 4.5:1 ✓ |
| Border Baseline | #cc3333 | #ff5555 | 3.5:1 ✓ |
| Border DocStratum | #33aa33 | #55ff55 | 3.5:1 ✓ |

### 6.3 Dark Mode Testing

```python
def test_dark_mode_contrast():
    """Verify WCAG AA contrast ratios in dark mode."""
    # Use WebAIM contrast checker for validation
    # Minimum 4.5:1 for normal text
    # Minimum 3:1 for large text
    pass
```

---

## 7. Complete CSS Architecture Template

### 7.1 Full CSS Injection Code

```python
def inject_complete_design_system() -> None:
    """Inject complete CSS design system."""

    css = """
    <style>
    /* ========== CSS Variables ========== */
    :root {
        /* Color schemes */
        --baseline-primary: #cc3333;
        --baseline-dark: #8b0000;
        --baseline-light: #ffcccc;
        --baseline-bg: #fafafa;

        --docstratum-primary: #33aa33;
        --docstratum-dark: #006600;
        --docstratum-light: #ccffcc;
        --docstratum-bg: #f0f8f0;

        --text-primary: #1a1a1a;
        --text-secondary: #666666;
        --border-light: #e0e0e0;
        --border-dark: #999999;

        /* Spacing */
        --spacing-xs: 4px;
        --spacing-sm: 8px;
        --spacing-md: 16px;
        --spacing-lg: 24px;
        --spacing-xl: 32px;

        /* Typography */
        --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto';
        --font-size-sm: 12px;
        --font-size-base: 14px;
        --font-size-lg: 16px;
        --font-size-xl: 20px;
    }

    @media (prefers-color-scheme: dark) {
        :root {
            --text-primary: #ffffff;
            --text-secondary: #cccccc;
            --border-light: #444444;
            --baseline-bg: #1a1a1a;
            --docstratum-bg: #0a2a0a;
        }
    }

    /* ========== Component Styling ========== */
    .baseline-card {
        background: linear-gradient(135deg, #fafafa 0%, #ffe6e6 50%, #ffcccc 100%);
        border: 2px solid var(--baseline-primary);
        border-radius: 8px;
        padding: 16px;
        color: var(--text-primary);
    }

    .docstratum-card-enhanced {
        background: linear-gradient(135deg, #f0f8f0 0%, #e6ffe6 50%, #ccffcc 100%);
        border: 2px solid var(--docstratum-primary);
        border-radius: 8px;
        padding: 16px;
        color: var(--text-primary);
    }

    .card-header {
        padding: var(--spacing-md);
        margin: calc(-1 * var(--spacing-md)) calc(-1 * var(--spacing-md)) var(--spacing-md) calc(-1 * var(--spacing-md));
        border-radius: 6px 6px 0 0;
        border-left: 4px solid;
    }

    .baseline-card .card-header {
        background: linear-gradient(90deg, #ffcccc 0%, #ffe6e6 100%);
        border-left-color: var(--baseline-dark);
    }

    .baseline-card .card-header h3 {
        color: var(--baseline-dark);
        margin: 0;
        font-size: var(--font-size-lg);
        font-weight: 600;
    }

    .docstratum-card-enhanced .card-header {
        background: linear-gradient(90deg, #ccffcc 0%, #e6ffe6 100%);
        border-left-color: var(--docstratum-dark);
    }

    .docstratum-card-enhanced .card-header h3 {
        color: var(--docstratum-dark);
        margin: 0;
        font-size: var(--font-size-lg);
        font-weight: 700;
    }

    .card-content {
        max-height: 500px;
        overflow-y: auto;
        font-size: var(--font-size-base);
        line-height: 1.6;
    }

    .comparison-columns {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: var(--spacing-lg);
    }

    .analysis-section {
        margin-top: var(--spacing-xl);
        padding-top: var(--spacing-lg);
        border-top: 1px solid var(--border-light);
    }

    /* ========== Responsive Design ========== */
    @media (max-width: 1199px) {
        .comparison-columns {
            gap: var(--spacing-md);
        }
    }

    @media (max-width: 767px) {
        .comparison-columns {
            grid-template-columns: 1fr;
        }

        .card-header h3 {
            font-size: var(--font-size-base);
        }

        .card-content {
            max-height: 400px;
        }
    }

    /* ========== Dark Mode ========== */
    @media (prefers-color-scheme: dark) {
        .baseline-card {
            background: linear-gradient(135deg, #2a1a1a 0%, #3d1515 50%, #4d1515 100%);
            border-color: #ff6666;
        }

        .docstratum-card-enhanced {
            background: linear-gradient(135deg, #0a2a0a 0%, #153d15 50%, #154d15 100%);
            border-color: #66ff66;
        }

        .baseline-card .card-header {
            background: linear-gradient(90deg, #4d1515 0%, #3d1515 100%);
        }

        .baseline-card .card-header h3 {
            color: #ff6666;
        }

        .docstratum-card-enhanced .card-header {
            background: linear-gradient(90deg, #154d15 0%, #153d15 100%);
        }

        .docstratum-card-enhanced .card-header h3 {
            color: #66ff66;
        }
    }
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)
```

---

## Deliverables Checklist

- [ ] CSS injection strategy documented with Streamlit pattern
- [ ] CSS variables system implemented for colors, spacing, typography
- [ ] Baseline gradient (red) design implemented
- [ ] Enhanced/DocStratum gradient (green) design implemented
- [ ] Border system with styling conventions documented
- [ ] Spacing system with grid-based values
- [ ] Streamlit CSS selector patterns documented
- [ ] Data attribute strategy for semantic targeting
- [ ] Responsive breakpoint strategy for 5 device sizes
- [ ] Dark mode CSS variables and overrides
- [ ] Dark mode color contrast verification (WCAG AA)
- [ ] Complete CSS architecture template provided
- [ ] Visual design mockup (ASCII) created

---

## Acceptance Criteria

- [ ] CSS injection loads without errors in Streamlit
- [ ] Baseline cards display red gradient border and background
- [ ] DocStratum cards display green gradient border and background
- [ ] Headers show distinct color for each type (dark red vs dark green)
- [ ] Spacing follows 4px grid system consistently
- [ ] Layout responds correctly at 5 breakpoints (>1200px, 1000-1199px, 768-999px, 576-767px, <576px)
- [ ] Mobile layout stacks columns vertically
- [ ] Dark mode displays appropriate color adjustments
- [ ] Dark mode text contrast meets WCAG AA minimum 4.5:1
- [ ] All CSS uses custom properties (variables) for maintainability
- [ ] No hardcoded colors outside of CSS variables
- [ ] CSS selectors use custom classes (not Streamlit internals)
- [ ] Gradients render without banding on all browsers
- [ ] Card borders are clearly visible in both light and dark mode

---

## 7.2 Visual Mockup (ASCII)

### Light Mode Desktop

```
┌─────────────────────────────────────────────────────────────────────┐
│  DocStratum — Side-by-Side Comparison                              │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────┬──────────────────────────────┐
│  Baseline Response            │  DocStratum Response       │
│  ┌─────────────────────────┐  │  ┌─────────────────────────┐ │
│  │ Red gradient header     │  │  │ Green gradient header   │ │
│  │ Dark red left border    │  │  │ Dark green left border  │ │
│  └─────────────────────────┘  │  └─────────────────────────┘ │
│                               │                               │
│  Content with red tint        │  Content with green tint      │
│  Red border 2px               │  Green border 2px             │
│  Light gray background        │  Light green background       │
│                               │                               │
│  Tokens: 150  Latency: 2.35s  │  Tokens: 175  Latency: 2.10s │
│                               │                               │
└──────────────────────────────┴──────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  Analysis & Quality Signals                                          │
│                                                                      │
│  Citations:         2 found (DocStratum)  vs  0 found (Baseline)       │
│  Code Examples:     1 block (DocStratum)  vs  0 blocks (Baseline)      │
│  Anti-Patterns:     0 found (DocStratum)  vs  2 found (Baseline)       │
│                                                                      │
│  Quality Improvement: +35%                                          │
└─────────────────────────────────────────────────────────────────────┘
```

### Mobile View (Single Column)

```
┌─────────────────────────────────────┐
│  Baseline Response                   │
│  ┌──────────────────────────────┐   │
│  │ Red gradient header           │   │
│  └──────────────────────────────┘   │
│                                      │
│  Content with red tint               │
│  Tokens: 150  Latency: 2.35s         │
│                                      │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  DocStratum Response               │
│  ┌──────────────────────────────┐   │
│  │ Green gradient header         │   │
│  └──────────────────────────────┘   │
│                                      │
│  Content with green tint             │
│  Tokens: 175  Latency: 2.10s         │
│                                      │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  Analysis & Quality Signals          │
│                                      │
│  Citations:    +2 (DocStratum)          │
│  Code:         +1 (DocStratum)          │
│  Quality:      +35% improvement      │
│                                      │
└─────────────────────────────────────┘
```

---

## Next Step

→ **v0.5.0 — Deployment & Integration**

Integrate all four v0.4.2 sub-parts into a unified side-by-side comparison feature. Perform end-to-end testing, create user documentation, and prepare for production deployment. Validate that all components work together seamlessly with proper styling, analysis, and responsive behavior.

---

## Color Palette Quick Reference

### Primary Colors

```
Baseline Red:
- Primary: #cc3333 (medium red)
- Dark: #8b0000 (dark red, text)
- Light: #ffcccc (light red, backgrounds)
- Very Light: #ffe6e6 (header gradients)

DocStratum Green:
- Primary: #33aa33 (medium green)
- Dark: #006600 (dark green, text)
- Light: #ccffcc (light green, backgrounds)
- Very Light: #e6ffe6 (header gradients)
```

### Semantic Colors

```
Text Primary: #1a1a1a (light mode) / #ffffff (dark mode)
Text Secondary: #666666 (light mode) / #cccccc (dark mode)
Border Light: #e0e0e0 (light mode) / #444444 (dark mode)
Border Dark: #999999 (light mode) / #666666 (dark mode)
```

### Gradients

```
Baseline: linear-gradient(135deg, #fafafa 0%, #ffe6e6 50%, #ffcccc 100%)
DocStratum: linear-gradient(135deg, #f0f8f0 0%, #e6ffe6 50%, #ccffcc 100%)
Header Baseline: linear-gradient(90deg, #ffcccc 0%, #ffe6e6 100%)
Header DocStratum: linear-gradient(90deg, #ccffcc 0%, #e6ffe6 100%)
```
