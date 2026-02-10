# v0.4.1b — Configuration Module & Sample Data

> This sub-part defines the configuration module (demo/config.py) with app constants, sample questions, and theming settings. It establishes the single source of truth for application-wide settings, curated example questions that showcase DocStratum's strengths, and CSS styling hooks for consistent visual presentation.

---

## Objective

Design and implement the configuration module that serves as the central repository for application constants, curated sample questions, and theme settings. This includes:
- Defining configuration constants (APP_TITLE, APP_SUBTITLE, APP_ICON, DEFAULT_LLMS_PATH, etc.)
- Curating sample questions that highlight DocStratum's unique capabilities
- Establishing theme and CSS configuration framework
- Integrating environment variable support for deployment flexibility
- Designing configuration validation patterns
- Planning extensibility for future settings (dark mode, API keys, model selection)

---

## Scope Boundaries

| Aspect | In Scope | Out of Scope |
|--------|----------|--------------|
| Constants | APP_TITLE, APP_SUBTITLE, APP_ICON, DEFAULT_LLMS_PATH, SAMPLE_QUESTIONS | Runtime configuration files (environment-specific) |
| Sample questions | Question text, category tags, explanation text | Question execution/processing logic |
| Theme | CSS class names, color palettes, font sizes | Actual CSS injection (covered in v0.4.1d) |
| Environment variables | Loading from .env, validation patterns | Specific environment file structure |
| Validation | Type hints, basic data validation | Complex schema validation with Pydantic |
| Extensibility | Structure for future settings (dark mode, model selection) | Implementation of future settings |

---

## Configuration Constants Design

### Application Constants Table

| Constant | Value | Purpose | Type |
|----------|-------|---------|------|
| **APP_TITLE** | "DocStratum" | Page title, headings, branding | str |
| **APP_SUBTITLE** | "Semantic translation layer for LLM agents" | Tagline, hero section | str |
| **APP_ICON** | "🌳" | Browser tab icon, logo | str |
| **APP_VERSION** | "0.4.1" | Version display, telemetry | str |
| **DEFAULT_LLMS_PATH** | "./data/llms.txt" | Default path to llms.txt file | str |
| **MAX_QUESTION_LENGTH** | 2000 | Input validation; prevent excessively long queries | int |
| **SPINNER_MESSAGE** | "Processing your question..." | User feedback during API calls | str |
| **ERROR_MESSAGE_TIMEOUT** | 5 | Error notification display duration (seconds) | int |

### Configuration Constants Code

```python
# demo/config.py

"""
Configuration module for The DocStratum Streamlit application.
Centralizes all application constants, sample questions, and theming.
"""

# ============================================================================
# Application Identity
# ============================================================================

APP_TITLE = "DocStratum"
APP_SUBTITLE = "Semantic translation layer for LLM agents"
APP_ICON = "🌳"
APP_VERSION = "0.4.1"

# ============================================================================
# File Paths & Defaults
# ============================================================================

DEFAULT_LLMS_PATH = "./data/llms.txt"
DATA_DIR = "./data"
CACHE_DIR = "./.cache"

# ============================================================================
# User Interaction Settings
# ============================================================================

MAX_QUESTION_LENGTH = 2000  # Prevent excessively long inputs
MIN_QUESTION_LENGTH = 3     # Require meaningful input

SPINNER_MESSAGE = "Processing your question..."
ERROR_MESSAGE_TIMEOUT = 5    # Seconds before error notification fades

# ============================================================================
# Theme Configuration
# ============================================================================

THEME = {
    "primary_color": "#1f77b4",      # DocStratum blue
    "secondary_color": "#2ca02c",    # DocStratum green
    "accent_color": "#ff7f0e",       # Accent orange
    "warning_color": "#d62728",      # Alert red
    "success_color": "#2ca02c",      # Success green
    "background_color": "#f8f9fa",   # Light gray
    "text_color": "#2c3e50",         # Dark text
    "border_color": "#e0e0e0",       # Light border
}

# CSS Classes used throughout the app
CSS_CLASSES = {
    "result_box": "result-box",
    "baseline_box": "baseline-box",
    "docstratum_box": "docstratum-box",
    "comparison_container": "comparison-container",
    "metrics_row": "metrics-row",
    "metric_card": "metric-card",
    "question_input": "question-input",
}

# ============================================================================
# Logging & Debugging
# ============================================================================

DEBUG_MODE = False  # Set to True for verbose logging
LOG_LEVEL = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

---

## Sample Questions Curation Strategy

### Sample Question Selection Criteria Matrix

| Criterion | Description | Example Questions |
|-----------|-------------|-------------------|
| **Breadth of domains** | Questions span multiple documentation types (API docs, tutorials, guides, FAQs) | Query about REST API, Django framework, Docker setup |
| **Highlight key strength** | Show DocStratum's ability to map semantic relationships across disparate docs | "How do I authenticate users across services?" (spans multiple API docs) |
| **Progressive complexity** | Start simple, increase difficulty to guide exploration | Simple lookup → cross-domain mapping → conceptual relationships |
| **Real user scenarios** | Address genuine use cases developers face | "What's the difference between async and sync in Python?" |
| **Demonstrate translation** | Show semantic understanding that raw keyword search misses | "How do I handle errors gracefully?" (translates across different frameworks' terminology) |
| **Showcase metadata** | Illustrate freshness, source diversity, and concept dependencies | Questions that benefit from "last updated" or "related concepts" metadata |

### Sample Questions Data Structure

```python
# demo/config.py (continued)

SAMPLE_QUESTIONS = [
    {
        "id": "auth_crossservice",
        "question": "How do I implement authentication across multiple microservices?",
        "category": "Architecture",
        "difficulty": "intermediate",
        "explanation": (
            "This question showcases DocStratum's strength in mapping authentication patterns "
            "across different frameworks (Flask, Django, FastAPI). Raw keyword search would "
            "return framework-specific docs; DocStratum unifies the conceptual patterns."
        ),
        "expected_sources": [
            "flask_auth_docs",
            "django_auth_docs",
            "fastapi_security_docs",
        ],
    },
    {
        "id": "async_sync_python",
        "question": "What's the semantic difference between async and sync patterns in Python?",
        "category": "Concepts",
        "difficulty": "beginner",
        "explanation": (
            "Demonstrates DocStratum's concept map layer: different frameworks call this differently "
            "(asyncio, twisted, gevent, curio), but DocStratum identifies the underlying patterns."
        ),
        "expected_sources": [
            "python_asyncio_docs",
            "twisted_docs",
            "fastapi_async_docs",
        ],
    },
    {
        "id": "error_handling_patterns",
        "question": "How do different frameworks implement error handling strategies?",
        "category": "Patterns",
        "difficulty": "intermediate",
        "explanation": (
            "Tests the few-shot bank layer: DocStratum retrieves error handling Q&A pairs from multiple "
            "frameworks and synthesizes a unified response pattern."
        ),
        "expected_sources": [
            "django_error_handling",
            "fastapi_error_handling",
            "express_error_handling",
        ],
    },
    {
        "id": "database_orm_selection",
        "question": "Should I use an ORM or raw SQL for my new project?",
        "category": "Decision",
        "difficulty": "beginner",
        "explanation": (
            "Showcases DocStratum's ability to map trade-offs across documentation. Different docs "
            "frame this decision differently; DocStratum synthesizes a coherent perspective."
        ),
        "expected_sources": [
            "sqlalchemy_docs",
            "django_orm_docs",
            "prisma_docs",
        ],
    },
    {
        "id": "caching_strategies",
        "question": "What caching strategies should I implement for API performance?",
        "category": "Performance",
        "difficulty": "advanced",
        "explanation": (
            "Advanced question testing concept map depth. Caching appears across multiple contexts "
            "(HTTP, database, application), and DocStratum maps relationships between them."
        ),
        "expected_sources": [
            "redis_docs",
            "http_caching_specs",
            "django_cache_docs",
        ],
    },
    {
        "id": "containerization_choice",
        "question": "How do I decide between Docker containers and virtual environments?",
        "category": "DevOps",
        "difficulty": "beginner",
        "explanation": (
            "Tests DocStratum's freshness layer: this decision has evolved over time. DocStratum ranks "
            "sources by last-updated timestamp, surfacing current best practices."
        ),
        "expected_sources": [
            "docker_docs",
            "python_venv_docs",
            "kubernetes_docs",
        ],
    },
]

# Sample question metadata for UI rendering
SAMPLE_QUESTION_CATEGORIES = [
    "Architecture",
    "Concepts",
    "Patterns",
    "Decision",
    "Performance",
    "DevOps",
]

DIFFICULTY_LEVELS = ["beginner", "intermediate", "advanced"]
```

---

## Theme & CSS Configuration

### CSS Class Reference Table

| CSS Class | Purpose | Component | Properties |
|-----------|---------|-----------|------------|
| **.result-box** | Container for results display | Main results area | padding, border, rounded corners, shadow |
| **.baseline-box** | Left column (baseline result) | Results comparison | background, border-left accent |
| **.docstratum-box** | Right column (DocStratum result) | Results comparison | background, border-left accent |
| **.comparison-container** | Wrapper for side-by-side columns | Layout container | display: grid, gap |
| **.metrics-row** | Row displaying result metrics | Metrics display | display: flex, justify-content: space-around |
| **.metric-card** | Individual metric (sources, concepts, freshness) | Metrics | background, padding, border-radius |
| **.question-input** | Text input field styling | User input | border, focus state, placeholder |
| **.spinner-text** | Processing spinner message | Loading state | color, font-size |
| **.error-message** | Error notification styling | Error display | background-color (red), text-color, padding |
| **.success-message** | Success notification styling | Success display | background-color (green), text-color, padding |

### Theme Configuration Structure

```python
# demo/config.py (continued)

# Color Palette
COLORS = {
    # Primary brand colors
    "docstratum_blue": "#1f77b4",
    "docstratum_green": "#2ca02c",

    # Semantic colors
    "success": "#2ca02c",
    "warning": "#ff7f0e",
    "error": "#d62728",
    "info": "#1f77b4",

    # Neutral colors
    "white": "#ffffff",
    "light_gray": "#f8f9fa",
    "medium_gray": "#e0e0e0",
    "dark_gray": "#6c757d",
    "text_dark": "#2c3e50",
    "text_light": "#7f8c8d",

    # Background & surface
    "surface_light": "#f8f9fa",
    "surface_dark": "#ffffff",
}

# Typography
TYPOGRAPHY = {
    "font_family": "system-ui, -apple-system, sans-serif",
    "heading_size": "28px",
    "subheading_size": "20px",
    "body_size": "16px",
    "small_size": "12px",
    "line_height": "1.6",
    "letter_spacing": "0.5px",
}

# Spacing & Layout
SPACING = {
    "xs": "4px",
    "sm": "8px",
    "md": "16px",
    "lg": "24px",
    "xl": "32px",
    "xxl": "48px",
}

# Borders & Shadows
BORDERS = {
    "radius_sm": "4px",
    "radius_md": "8px",
    "radius_lg": "12px",
    "width_thin": "1px",
    "width_thick": "2px",
}

SHADOWS = {
    "sm": "0 1px 2px rgba(0,0,0,0.05)",
    "md": "0 4px 6px rgba(0,0,0,0.1)",
    "lg": "0 10px 15px rgba(0,0,0,0.1)",
}
```

---

## Environment Variable Integration

### Environment Variable Support Table

| Variable | Default Value | Purpose | Example |
|----------|---------------|---------|---------|
| **DOCSTRATUM_LLMS_PATH** | "./data/llms.txt" | Override default llms.txt path | DOCSTRATUM_LLMS_PATH=/var/data/llms.txt |
| **DOCSTRATUM_DEBUG** | False | Enable debug logging | DOCSTRATUM_DEBUG=true |
| **DOCSTRATUM_API_KEY** | (none) | API key for external LLM calls | DOCSTRATUM_API_KEY=sk-... |
| **DOCSTRATUM_LOG_LEVEL** | INFO | Logging verbosity | DOCSTRATUM_LOG_LEVEL=DEBUG |
| **DOCSTRATUM_CACHE_DIR** | ./.cache | Cache directory | DOCSTRATUM_CACHE_DIR=/tmp/cache |

### Environment Variable Loading Code

```python
# demo/config.py (continued)

import os
from pathlib import Path

def load_env_variable(name: str, default, cast_type=str):
    """
    Load environment variable with optional type casting.

    Args:
        name: Environment variable name
        default: Default value if not set
        cast_type: Type to cast value to (str, int, bool)

    Returns:
        Casted value or default
    """
    value = os.getenv(name, default)

    if cast_type == bool:
        return value.lower() in ("true", "1", "yes", "on")
    elif cast_type == int:
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    return value

# Override config with environment variables
LLMS_PATH = load_env_variable("DOCSTRATUM_LLMS_PATH", DEFAULT_LLMS_PATH)
DEBUG_MODE = load_env_variable("DOCSTRATUM_DEBUG", DEBUG_MODE, bool)
LOG_LEVEL = load_env_variable("DOCSTRATUM_LOG_LEVEL", LOG_LEVEL)
CACHE_DIR = load_env_variable("DOCSTRATUM_CACHE_DIR", CACHE_DIR)

# API configuration (if needed)
API_KEY = load_env_variable("DOCSTRATUM_API_KEY", None)
API_BASE_URL = load_env_variable("DOCSTRATUM_API_URL", "https://api.docstratum.dev")
```

---

## Configuration Validation

### Validation Patterns

```python
# demo/config.py (continued)

from pathlib import Path
from typing import List, Dict, Any

def validate_config() -> bool:
    """
    Validate configuration on startup.
    Returns True if all validations pass, raises exception otherwise.
    """
    errors = []

    # Validate file paths
    try:
        llms_path = Path(LLMS_PATH)
        if not llms_path.exists():
            errors.append(f"LLMS file not found: {LLMS_PATH}")
    except Exception as e:
        errors.append(f"Invalid LLMS_PATH: {e}")

    # Validate string lengths
    if len(APP_TITLE) == 0 or len(APP_TITLE) > 100:
        errors.append(f"APP_TITLE must be 1-100 chars, got {len(APP_TITLE)}")

    # Validate sample questions
    if not SAMPLE_QUESTIONS or len(SAMPLE_QUESTIONS) == 0:
        errors.append("SAMPLE_QUESTIONS cannot be empty")

    for i, q in enumerate(SAMPLE_QUESTIONS):
        if not q.get("question") or len(q["question"]) < MIN_QUESTION_LENGTH:
            errors.append(f"Sample question {i} is invalid or too short")
        if not q.get("category"):
            errors.append(f"Sample question {i} missing category")
        if q.get("difficulty") not in DIFFICULTY_LEVELS:
            errors.append(f"Sample question {i} has invalid difficulty level")

    # Raise if any errors
    if errors:
        error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
        raise ValueError(error_msg)

    return True

# Run validation on import (optional, can be called explicitly)
# validate_config()
```

---

## Extensibility for Future Settings

### Future Settings Structure

```python
# demo/config.py (continued)

# ============================================================================
# FUTURE: Theme Mode (Light/Dark)
# ============================================================================

THEME_MODE = load_env_variable("DOCSTRATUM_THEME_MODE", "light")  # "light" or "dark"

# Theme mode variants (to be implemented in v0.5.0)
THEME_VARIANTS = {
    "light": {
        "background": "#ffffff",
        "text": "#2c3e50",
        "surface": "#f8f9fa",
    },
    "dark": {
        "background": "#1e1e1e",
        "text": "#e0e0e0",
        "surface": "#2d2d2d",
    },
}

# ============================================================================
# FUTURE: Model Selection
# ============================================================================

DEFAULT_MODEL = load_env_variable("DOCSTRATUM_DEFAULT_MODEL", "gpt-4")

AVAILABLE_MODELS = [
    "gpt-4",
    "gpt-3.5-turbo",
    "claude-3-opus",
    "claude-3-sonnet",
    "gemini-pro",
]

# ============================================================================
# FUTURE: Feature Flags
# ============================================================================

FEATURE_FLAGS = {
    "enable_neo4j": load_env_variable("DOCSTRATUM_NEO4J_ENABLED", False, bool),
    "enable_caching": load_env_variable("DOCSTRATUM_CACHE_ENABLED", True, bool),
    "enable_analytics": load_env_variable("DOCSTRATUM_ANALYTICS_ENABLED", False, bool),
    "enable_multi_language": False,  # Coming in v0.5.0
    "enable_dark_mode": False,       # Coming in v0.5.0
}

# ============================================================================
# FUTURE: API Configuration
# ============================================================================

API_CONFIG = {
    "timeout": load_env_variable("DOCSTRATUM_API_TIMEOUT", 30, int),
    "max_retries": load_env_variable("DOCSTRATUM_MAX_RETRIES", 3, int),
    "retry_delay": load_env_variable("DOCSTRATUM_RETRY_DELAY", 1, int),
    "rate_limit": load_env_variable("DOCSTRATUM_RATE_LIMIT", 100, int),
}
```

---

## Deliverables Checklist

- [ ] Configuration constants table created with all required settings
- [ ] Sample questions curated with diverse categories and difficulty levels
- [ ] Sample question selection criteria matrix documented
- [ ] Theme configuration structure established (colors, typography, spacing)
- [ ] CSS class reference table created for all UI elements
- [ ] Environment variable loading function implemented
- [ ] Configuration validation function implemented
- [ ] Future extensibility structure planned (theme mode, model selection, feature flags)
- [ ] Code examples provided for all configuration patterns
- [ ] All environment variables documented with examples

---

## Acceptance Criteria

- [ ] demo/config.py can be imported without errors
- [ ] All constants are accessible via import (e.g., `from config import APP_TITLE`)
- [ ] SAMPLE_QUESTIONS list contains at least 4 questions with complete metadata
- [ ] Sample questions cover at least 3 different categories
- [ ] Theme colors are defined and accessible
- [ ] CSS class names match those used in app.py and components.py
- [ ] Environment variables override defaults when set
- [ ] validate_config() function passes without errors
- [ ] Configuration values fit within documented constraints (string lengths, value ranges)
- [ ] No circular imports or external dependencies in config.py (stdlib + typing only)

---

## Next Step

Proceed to **v0.4.1c — Session State & User Interaction Flow** to design Streamlit session state management, user interaction patterns, and the question processing pipeline.
