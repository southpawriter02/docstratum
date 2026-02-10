# v0.4.1c — Session State & User Interaction Flow

> This sub-part implements Streamlit session state management and user interaction patterns for The DocStratum v0.4.1. It defines the state schema, user interaction flows (input → process → display), sidebar patterns, and error handling strategies that enable reactive, stateful behavior across Streamlit reruns.

---

## Objective

Design and implement session state management and user interaction flows that create a seamless, responsive experience. This includes:
- Understanding Streamlit session state fundamentals and rerun mechanics
- Designing a comprehensive state schema (question, results, UI state, error state)
- Implementing user interaction flows (text input → button → spinner → results)
- Creating sidebar interaction patterns (sample questions, config toggles)
- Designing state reset and clear functionality
- Handling error states gracefully
- Preventing race conditions and unexpected state transitions

---

## Scope Boundaries

| Aspect | In Scope | Out of Scope |
|--------|----------|--------------|
| Session state | State schema design, initialization, persistence across reruns | State persistence across browser sessions (storage required) |
| User interactions | Button clicks, text input, sidebar toggles, sample question selection | Advanced gesture input or keyboard shortcuts |
| State management | State reset, clear operations, state validation | Complex state machines or Redux-like patterns |
| Error handling | Error state capture, user-friendly messaging, recovery flows | Detailed error logging or telemetry |
| Interaction flows | Input validation, spinner display, results rendering | Animation or transition timing |
| Sidebar patterns | Sample question selection, config toggles | Sidebar customization or theming |
| State transitions | Valid transitions, prevented invalid states | State history or undo/redo functionality |

---

## Streamlit Session State Fundamentals

### What is Session State?

Streamlit's `session_state` is a dictionary-like object (`st.session_state`) that persists values across script reruns. When a user interacts with a widget (button click, text input, slider), Streamlit reruns the script from top to bottom, but values in `session_state` are preserved.

### Session State Lifecycle

```
┌─────────────────────────────────────┐
│ User opens app (first time)         │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│ Session state is initialized        │
│ (empty dict, or from cache)         │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│ Script runs, widgets render         │
│ Widgets use session_state if set    │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│ User interacts (click button, etc.) │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│ Streamlit detects widget change     │
│ Updates session_state[widget_key]   │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│ Script reruns from top              │
│ All session_state values preserved  │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│ Widgets re-render with new values   │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│ Return to "Await user interaction"  │
└─────────────────────────────────────┘
```

### Key Principles

| Principle | Explanation | Example |
|-----------|-------------|---------|
| **Persistence** | Values in session_state survive reruns | Store `user_question` in session_state so it persists when button is clicked |
| **Automatic sync** | Widget values sync with session_state | `st.text_input(..., key="question")` auto-updates `session_state.question` |
| **Top-to-bottom execution** | Script always reruns completely | Must initialize state early in script; can't access state values before they're set |
| **No async state** | Session state is per-browser-tab, not per-user | Each tab has its own session_state; closing tab loses state |
| **Callbacks pattern** | Functions can modify state before rerun | Use `st.button(..., on_click=callback_fn)` to update state and trigger logic |

---

## Session State Schema Design

### State Schema Table

| Key | Data Type | Initial Value | Purpose | Scope |
|-----|-----------|---------------|---------|-------|
| **question** | str | "" | Current user question | Global (shared across all interactions) |
| **last_result** | dict or None | None | Last computed result (baseline + DocStratum) | Global |
| **is_processing** | bool | False | Currently processing question | Render-level (shows spinner) |
| **has_error** | bool | False | Error occurred in last operation | Render-level (shows error message) |
| **error_message** | str | "" | Human-readable error text | Render-level |
| **show_results** | bool | False | Should results be displayed | Render-level |
| **selected_question** | str or None | None | Currently selected sample question | Sidebar state |
| **config_llms_path** | str | DEFAULT_LLMS_PATH | Path to llms.txt file | App config |
| **config_debug_mode** | bool | False | Enable debug output | App config |

### State Schema Code

```python
# demo/app.py - Initialize session state early

import streamlit as st
from config import DEFAULT_LLMS_PATH, APP_TITLE

# Initialize session state (must be at top of script)
def init_session_state():
    """Initialize all session state variables on first run."""
    if "question" not in st.session_state:
        st.session_state.question = ""

    if "last_result" not in st.session_state:
        st.session_state.last_result = None

    if "is_processing" not in st.session_state:
        st.session_state.is_processing = False

    if "has_error" not in st.session_state:
        st.session_state.has_error = False

    if "error_message" not in st.session_state:
        st.session_state.error_message = ""

    if "show_results" not in st.session_state:
        st.session_state.show_results = False

    if "selected_question" not in st.session_state:
        st.session_state.selected_question = None

    if "config_llms_path" not in st.session_state:
        st.session_state.config_llms_path = DEFAULT_LLMS_PATH

    if "config_debug_mode" not in st.session_state:
        st.session_state.config_debug_mode = False

# Call immediately after page config, before any widgets
init_session_state()
```

### State Access Pattern

```python
# Reading from session state
current_question = st.session_state.question

# Writing to session state
st.session_state.question = "What is authentication?"

# Checking if state exists
if "question" in st.session_state:
    # ... use the state

# Accessing with default
question = st.session_state.get("question", "")
```

---

## User Interaction Flow: Question Processing Pipeline

### Interaction Sequence Diagram

```
User Types Question
        │
        ▼
┌──────────────────────────┐
│ Text Input Widget        │
│ key="question"           │
│ Syncs to session_state   │
└────────────┬─────────────┘
             │
             ▼ (triggers rerun)
        Question in
      session_state?
             │
         Yes │
             ▼
┌──────────────────────────┐
│ Compare Button           │
│ on_click=on_compare()    │
│ Sets is_processing=True  │
└────────────┬─────────────┘
             │
             ▼ (triggers rerun)
┌──────────────────────────┐
│ Check is_processing flag │
│ Display spinner          │
│ Call resolve(question)   │
└────────────┬─────────────┘
             │
    ┌────────┴────────┐
    │ Success         │ Error
    │                 │
    ▼                 ▼
Process results  Set error state
Set last_result  Set has_error=True
Set is_processing= Set error_message
     False        Set is_processing=False
Set show_results=
     True (triggers rerun)
    │                 │
    └────────┬────────┘
             │
             ▼
    ┌──────────────────────────┐
    │ Check show_results       │
    │ Render results display   │
    │ OR show_results == False │
    │ Skip display             │
    └──────────────────────────┘
             │
             ▼
    ┌──────────────────────────┐
    │ Check has_error          │
    │ Display error message    │
    │ in red banner            │
    └──────────────────────────┘
             │
             ▼
    ┌──────────────────────────┐
    │ Clear Button             │
    │ on_click=on_clear()      │
    │ Resets all state         │
    └──────────────────────────┘
```

### Implementation Code: Interaction Flow

```python
# demo/app.py - Interaction flow implementation

def on_compare():
    """Callback when Compare button is clicked."""
    # Validate question
    if not st.session_state.question or len(st.session_state.question.strip()) == 0:
        st.session_state.has_error = True
        st.session_state.error_message = "Please enter a question before comparing."
        return

    if len(st.session_state.question) > MAX_QUESTION_LENGTH:
        st.session_state.has_error = True
        st.session_state.error_message = (
            f"Question is too long. Maximum {MAX_QUESTION_LENGTH} characters allowed."
        )
        return

    # Set processing flag (triggers spinner on next rerun)
    st.session_state.is_processing = True
    st.session_state.has_error = False
    st.session_state.error_message = ""

def on_clear():
    """Callback when Clear button is clicked."""
    st.session_state.question = ""
    st.session_state.last_result = None
    st.session_state.is_processing = False
    st.session_state.has_error = False
    st.session_state.error_message = ""
    st.session_state.show_results = False
    st.session_state.selected_question = None

def on_sample_question_select(question_text: str):
    """Callback when user selects a sample question."""
    st.session_state.question = question_text
    st.session_state.has_error = False
    st.session_state.error_message = ""
    st.session_state.show_results = False
    # Don't auto-run; let user click Compare button

# ============================================================================
# Main Content Area
# ============================================================================

col1, col2 = st.columns([3, 1], gap="medium")

with col1:
    question = st.text_input(
        "Ask a question:",
        key="question",
        placeholder="e.g., How do I implement authentication across services?",
        max_chars=MAX_QUESTION_LENGTH,
    )

with col2:
    compare_btn = st.button("Compare", on_click=on_compare)
    clear_btn = st.button("Clear", on_click=on_clear)

# ============================================================================
# Processing & Results
# ============================================================================

# Show spinner while processing
if st.session_state.is_processing:
    with st.spinner(SPINNER_MESSAGE):
        try:
            # Call resolve function (from core module)
            from src.docstratum.core.llm_resolver import resolve

            result = resolve(st.session_state.question)
            st.session_state.last_result = result
            st.session_state.show_results = True
            st.session_state.is_processing = False

        except Exception as e:
            st.session_state.has_error = True
            st.session_state.error_message = f"Error processing question: {str(e)}"
            st.session_state.is_processing = False

# Display results if available
if st.session_state.show_results and st.session_state.last_result:
    render_results(st.session_state.last_result)

# Display error message if error occurred
if st.session_state.has_error and st.session_state.error_message:
    st.error(st.session_state.error_message, icon="🚨")
```

---

## Sidebar Interaction Patterns

### Sidebar Layout

```python
# demo/app.py - Sidebar rendering

with st.sidebar:
    st.header("📚 Sidebar")

    # ====================================================================
    # Section 1: Configuration
    # ====================================================================

    with st.expander("⚙️ Configuration", expanded=True):
        st.session_state.config_llms_path = st.text_input(
            "Path to llms.txt:",
            value=st.session_state.config_llms_path,
            key="llms_path_input",
        )

        st.session_state.config_debug_mode = st.checkbox(
            "Enable debug mode",
            value=st.session_state.config_debug_mode,
            key="debug_mode_toggle",
        )

    # ====================================================================
    # Section 2: Sample Questions
    # ====================================================================

    st.divider()
    st.subheader("💡 Sample Questions")

    for question in SAMPLE_QUESTIONS:
        col1, col2 = st.columns([4, 1], gap="small")

        with col1:
            if st.button(
                question["question"][:50] + "...",
                key=f"sample_q_{question['id']}",
                use_container_width=True,
            ):
                on_sample_question_select(question["question"])

        with col2:
            difficulty_emoji = {
                "beginner": "🟢",
                "intermediate": "🟡",
                "advanced": "🔴",
            }
            st.caption(difficulty_emoji.get(question["difficulty"], "❓"))

    # Optional: Show sample question details
    if st.session_state.selected_question:
        st.divider()
        selected_q = next(
            (q for q in SAMPLE_QUESTIONS if q["question"] == st.session_state.selected_question),
            None
        )
        if selected_q:
            st.info(selected_q["explanation"])

    # ====================================================================
    # Section 3: About
    # ====================================================================

    st.divider()
    st.caption(f"**{APP_TITLE}** v{APP_VERSION}")
    st.caption(APP_SUBTITLE)
```

---

## State Reset & Clear Functionality

### Clear State Implementation

```python
# demo/components.py - Reusable clear function

def clear_all_state():
    """Clear all user-facing state, preserving config."""
    st.session_state.question = ""
    st.session_state.last_result = None
    st.session_state.is_processing = False
    st.session_state.has_error = False
    st.session_state.error_message = ""
    st.session_state.show_results = False
    st.session_state.selected_question = None

def clear_results_only():
    """Clear only results, keeping question and config."""
    st.session_state.last_result = None
    st.session_state.show_results = False
    st.session_state.has_error = False
    st.session_state.error_message = ""

def reset_to_defaults():
    """Reset entire session state to defaults."""
    clear_all_state()
    # Also reset config if desired
    # st.session_state.config_llms_path = DEFAULT_LLMS_PATH
    # st.session_state.config_debug_mode = False
```

---

## Error State Handling

### Error Handling State Machine

```
┌──────────────────┐
│ No Error State   │
│ (has_error=False)│
└────────┬─────────┘
         │
   User interacts
    (question)
         │
         ▼
┌──────────────────┐
│ Processing       │
│ (is_processing   │
│  =True)          │
└────────┬─────────┘
         │
    ┌────┴────┐
    │ Success  │ Error
    │          │
    ▼          ▼
┌──────────┐ ┌──────────────────┐
│ Display  │ │ Error State      │
│ Results  │ │ (has_error=True) │
└──────────┘ │ (error_message   │
             │  = msg)          │
             └────────┬─────────┘
                      │
             User clicks Clear
                      │
                      ▼
             ┌──────────────────┐
             │ No Error State   │
             │ (reset)          │
             └──────────────────┘
```

### Error Handling Code

```python
# demo/app.py - Error handling

def handle_error(error: Exception, user_message: str = None):
    """Handle errors gracefully."""
    st.session_state.has_error = True
    st.session_state.is_processing = False

    if user_message:
        st.session_state.error_message = user_message
    else:
        st.session_state.error_message = (
            f"An error occurred: {str(error)}. Please try again."
        )

    # Log error if debug mode enabled
    if st.session_state.config_debug_mode:
        st.session_state.error_message += f"\n\nDebug: {type(error).__name__}"

# Usage in try/except blocks
try:
    result = resolve(question)
except ValueError as e:
    handle_error(e, "Please check your question format and try again.")
except ConnectionError as e:
    handle_error(e, "Connection error. Please check your internet and try again.")
except Exception as e:
    handle_error(e)

# Display error with auto-dismiss (if desired)
if st.session_state.has_error:
    st.error(st.session_state.error_message, icon="🚨")

    # Optional: Auto-clear error after timeout
    # This would require st.session_state callbacks or similar
```

---

## State Validation & Invariants

### State Validation Function

```python
# demo/components.py - State validation

def validate_state() -> bool:
    """
    Validate that session state is in a consistent state.
    Returns True if valid, False otherwise.

    Invariants:
    - If is_processing=True, has_error must be False
    - If show_results=True, last_result must not be None
    - If has_error=True, error_message must not be empty
    - question must be a string
    """
    # Invariant 1: Can't be processing and have error simultaneously
    if st.session_state.is_processing and st.session_state.has_error:
        st.session_state.is_processing = False  # Processing takes precedence
        return False

    # Invariant 2: Can't show results without having results
    if st.session_state.show_results and st.session_state.last_result is None:
        st.session_state.show_results = False
        return False

    # Invariant 3: Error message must exist if error flag is set
    if st.session_state.has_error and not st.session_state.error_message:
        st.session_state.error_message = "An unknown error occurred."
        return False

    # Invariant 4: Question must be string
    if not isinstance(st.session_state.question, str):
        st.session_state.question = ""
        return False

    return True

# Call validate_state() at start of app
validate_state()
```

---

## Preventing Race Conditions

### Race Condition Prevention

```python
# demo/app.py - Safe state transitions

def safe_compare():
    """
    Safe comparison function that prevents multiple simultaneous requests.
    """
    # Prevent multiple clicks while processing
    if st.session_state.is_processing:
        st.warning("Please wait, already processing...")
        return

    # Validate state
    if not validate_state():
        st.error("Session state is inconsistent. Please try again.")
        return

    # Now safe to proceed
    on_compare()

# Use this in button instead of on_compare directly
st.button("Compare", on_click=safe_compare)
```

---

## Deliverables Checklist

- [ ] Session state schema documented with all keys and purposes
- [ ] init_session_state() function implemented
- [ ] State access patterns documented and exemplified
- [ ] Interaction sequence diagram created (ASCII art)
- [ ] Question processing flow implemented (input → compare → spinner → results)
- [ ] on_compare() callback function implemented with validation
- [ ] on_clear() callback function implemented
- [ ] on_sample_question_select() callback function implemented
- [ ] Sidebar rendering code with configuration and sample questions
- [ ] Error handling state machine documented
- [ ] Error handling code implemented with user-friendly messaging
- [ ] State validation function implemented (invariants)
- [ ] Race condition prevention implemented

---

## Acceptance Criteria

- [ ] App initializes without state-related errors
- [ ] Entering a question and clicking Compare shows spinner
- [ ] After processing, results display correctly
- [ ] Clicking Clear resets all state variables
- [ ] Selecting a sample question populates the input field
- [ ] Error messages display when validation fails
- [ ] Rapid clicking Compare button doesn't create multiple requests
- [ ] All state variables persist across Streamlit reruns
- [ ] Session state schema matches implementation
- [ ] State invariants are enforced (can't be processing + error simultaneously)
- [ ] Error state can be cleared by clicking Clear or selecting new question
- [ ] Debug mode checkbox updates state correctly

---

## Next Step

Proceed to **v0.4.1d — Custom Styling & Deployment Readiness** to implement custom CSS styling via st.markdown, configure Streamlit Cloud deployment settings, and prepare for production use.
