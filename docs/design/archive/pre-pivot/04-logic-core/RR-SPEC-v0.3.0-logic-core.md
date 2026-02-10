# v0.3.0 — Logic Core

> **Phase Goal:** Build the Python engine that transforms the `llms.txt` into a system prompt and integrates with LangChain.
> 

---

## Phase Overview

---

## User Stories

### US-006: Context Block Construction

> **As a** developer,
> 

> **I want** a function that transforms `llms.txt` into a prompt-ready string,
> 

> **So that** I can inject structured context into any LLM.
> 

**Acceptance Criteria:**

- [ ]  Function accepts `LlmsTxt` object
- [ ]  Output is a formatted string under 8000 tokens
- [ ]  Concepts, pages, and examples are all represented

### US-007: Agent Integration

> **As a** developer,
> 

> **I want** to create a LangChain agent with DocStratum context,
> 

> **So that** I can query it and compare to a baseline.
> 

**Acceptance Criteria:**

- [ ]  Agent can be instantiated with context block
- [ ]  Agent responds to documentation questions
- [ ]  Agent cites URLs from the `llms.txt`

### US-008: A/B Testing

> **As a** portfolio presenter,
> 

> **I want** to run side-by-side comparisons,
> 

> **So that** I can demonstrate measurable improvement.
> 

**Acceptance Criteria:**

- [ ]  Same question asked to both agents
- [ ]  Responses captured and returned
- [ ]  Results can be logged or displayed

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        LOGIC CORE ARCHITECTURE                       │
└─────────────────────────────────────────────────────────────────────┘

    ┌─────────────┐         ┌─────────────┐         ┌─────────────┐
    │  llms.txt   │────────▶│   Loader    │────────▶│  LlmsTxt    │
    │   (YAML)    │         │  (Pydantic) │         │  (Object)   │
    └─────────────┘         └─────────────┘         └──────┬──────┘
                                                          │
                                                          ▼
                                                   ┌─────────────┐
                                                   │   Context   │
                                                   │   Builder   │
                                                   └──────┬──────┘
                                                          │
                            ┌─────────────────────────────┴─────────┐
                            │                                       │
                            ▼                                       ▼
                     ┌─────────────┐                         ┌─────────────┐
                     │  Baseline   │                         │   DocStratum   │
                     │   Agent     │                         │    Agent    │
                     │ (No context)│                         │(With context)│
                     └──────┬──────┘                         └──────┬──────┘
                            │                                       │
                            ▼                                       ▼
                     ┌─────────────┐                         ┌─────────────┐
                     │  Response A │                         │  Response B │
                     └──────┬──────┘                         └──────┬──────┘
                            │                                       │
                            └───────────────┬───────────────────────┘
                                            ▼
                                     ┌─────────────┐
                                     │  Comparator │
                                     │   (A/B)     │
                                     └─────────────┘
```

---

## Version Roadmap

---

## Decision Tree: LLM Provider Selection

```
                ┌─────────────────┐
                │ Do you have an  │
                │ OpenAI API key? │
                └────────┬────────┘
                         │
          ┌──────────────┴──────────────┐
          ▼                             ▼
       YES ✅                          NO
          │                             │
          ▼                             ▼
Use OpenAI GPT-4o-mini      ┌─────────────────┐
(Recommended)               │ Do you want to  │
                            │ run locally?    │
                            └────────┬────────┘
                                     │
                      ┌──────────────┴──────────────┐
                      ▼                             ▼
                   YES                             NO
                      │                             │
                      ▼                             ▼
             Use Ollama + Llama3       Use Anthropic Claude
             (Free, local)             (API key required)
```

---

## Logging Configuration

```python
# Enhanced logging for the logic core
import logging

logger = logging.getLogger('docstratum.core')

# Log levels:
# DEBUG: Full context block content
# INFO:  Agent creation, query execution
# WARNING: Token limits approached
# ERROR: API failures, validation errors

def log_query(question: str, agent_type: str):
    logger.info(f"Query [{agent_type}]: {question[:50]}...")

def log_response(response: str, agent_type: str, tokens: int):
    logger.info(f"Response [{agent_type}]: {len(response)} chars, {tokens} tokens")
```

---

## Testing Strategy

### Test: Context Builder Output

```python
# tests/test_core.py
def test_context_builder_includes_concepts():
    """Context block should include all concept names."""
    llms = load_test_llms_txt()
    context = build_context_block(llms)
    
    for concept in llms.concepts:
        assert concept.name in context

def test_context_builder_under_token_limit():
    """Context block should be under 8000 tokens."""
    llms = load_test_llms_txt()
    context = build_context_block(llms)
    
    # Rough estimate: 1 token ≈ 4 chars
    estimated_tokens = len(context) / 4
    assert estimated_tokens < 8000
```

---

## Exit Criteria

This phase is **COMPLETE** when:

- [ ]  `load_llms_txt()` returns a valid `LlmsTxt` object
- [ ]  `build_context_block()` returns a string < 8000 tokens
- [ ]  `create_baseline_agent()` returns a working agent
- [ ]  `create_docstratum_agent()` returns a working agent with context
- [ ]  `run_ab_test()` returns both responses
- [ ]  All tests in `tests/test_[core.py](http://core.py)` pass

[v0.3.1 — Loader Module](RR-SPEC-v0.3.1-loader-module.md)
- v0.3.1a — Source Resolution & Input Handling
- v0.3.1b — YAML Parsing & Preprocessing
- v0.3.1c — Pydantic Validation & Schema Enforcement
- v0.3.1d — Caching, Performance & Public API

[v0.3.2 — Context Builder](RR-SPEC-v0.3.2-context-builder.md)
- v0.3.2a — Token Budget Engine & Priority System
- v0.3.2b — Section Renderers & Markdown Generation
- v0.3.2c — Output Formats & Processing Modes
- v0.3.2d — Integration API & Configuration

[v0.3.3 — Baseline Agent](RR-SPEC-v0.3.3-baseline-agent.md)
- v0.3.3a — Agent Architecture & Provider Abstraction
- v0.3.3b — System Prompt Engineering
- v0.3.3c — Response Capture & Metrics Collection
- v0.3.3d — Environment Setup & Dependency Management

[v0.3.4 — DocStratum Agent](RR-SPEC-v0.3.4-docstratum-agent.md)
- v0.3.4a — Context Injection & System Prompt Assembly
- v0.3.4b — Behavioral Verification & Quality Signals
- v0.3.4c — Integration Testing & End-to-End Pipeline
- v0.3.4d — Multi-Provider Testing & Fallback Strategy

[v0.3.5 — A/B Harness](RR-SPEC-v0.3.5-a-b-harness.md)
- v0.3.5a — Test Execution Engine & Data Structures
- v0.3.5b — Test Question Design & Suite Management
- v0.3.5c — Metrics Calculation & Statistical Analysis
- v0.3.5d — CLI Interface & Report Generation