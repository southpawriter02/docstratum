# 04-logic-core — Logic Core (v0.3.x)

> **Purpose**: Loader module, context builder, agent implementations, and A/B testing harness

This phase implements the core Python logic that loads, validates, and serves `/llms.txt` content to AI agents, including baseline and DocStratum-enhanced agent implementations.

---

## 📚 Phase Structure

### v0.3.1 — Loader Module

YAML loading, parsing, and validation:

- **LOADER_MODULE_INDEX** — Module architecture overview
- **v0.3.1a** — Source Resolution and Input Handling
- **v0.3.1b** — YAML Parsing and Preprocessing
- **v0.3.1c** — Pydantic Validation and Schema Enforcement
- **v0.3.1d** — Caching, Performance, and Public API

### v0.3.2 — Context Builder

Transform `/llms.txt` into system prompt context:

- **v0.3.2a** — Token Budget Engine
- **v0.3.2b** — Section Renderers
- **v0.3.2c** — Output Formats (plain text, XML, JSON)
- **v0.3.2d** — Integration API

### v0.3.3 — Baseline Agent

Standard LangChain agent without DocStratum context:

- **v0.3.3a** — Agent Architecture & Provider Abstraction
- **v0.3.3b** — System Prompt Engineering
- **v0.3.3c** — Response Capture & Metrics Collection
- **v0.3.3d** — Environment Setup & Dependency Management

### v0.3.4 — DocStratum Agent

Enhanced agent with DocStratum context injection:

- **v0.3.4a** — Context Injection & System Prompt Assembly
- **v0.3.4b** — Behavioral Verification & Quality Signals
- **v0.3.4c** — Integration Testing & End-to-End Pipeline
- **v0.3.4d** — Multi-Provider Testing & Fallback Strategy

### v0.3.5 — A/B Harness

Automated testing framework for comparing agents:

- **v0.3.5a** — Test Execution Engine
- **v0.3.5b** — Test Question Design
- **v0.3.5c** — Metrics and Analysis
- **v0.3.5d** — CLI and Reporting

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    DOCSTRATUM PIPELINE                         │
└──────────────────────────────────────────────────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  1. LOAD & VALIDATE │
                    │    (llms.txt file)  │
                    └──────────┬──────────┘
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
    ┌─────────────────────┐         ┌─────────────────────┐
    │ 2A. BUILD CONCEPT   │         │ 2B. INDEX FEW-SHOT  │
    │     GRAPH (Neo4j)   │         │     EXAMPLES        │
    └──────────┬──────────┘         └──────────┬──────────┘
               │                               │
               └───────────────┬───────────────┘
                               ▼
                    ┌─────────────────────┐
                    │ 3. CONSTRUCT SYSTEM │
                    │    PROMPT CONTEXT   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ 4. INJECT INTO      │
                    │    LANGCHAIN AGENT  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ 5. QUERY & COMPARE  │
                    │    (A/B Testing)    │
                    └─────────────────────┘
```

---

## 🔧 Key Components

### Loader Module

```python
def load_llms_txt(filepath: Path) -> LlmsTxt:
    """Load and validate the llms.txt file."""
    raw_data = yaml.safe_load(filepath.read_text())
    return LlmsTxt(**raw_data)  # Pydantic validates on instantiation
```

### Context Builder

```python
def build_context_block(llms: LlmsTxt) -> str:
    """Transform the llms.txt into a system prompt injection."""
    # Section 1: Site Overview
    # Section 2: Concept Definitions
    # Section 3: Few-Shot Examples
    return "\n".join(context_parts)
```

### Agent Factory

```python
def create_docstratum_agent(context_block: str):
    """Create a LangChain agent with DocStratum context."""
    system_prompt = f"""You are a documentation assistant.

{context_block}

When answering questions:
1. Cite specific URLs from the documentation.
2. Follow the format shown in the examples above.
3. If the answer is not in the documentation, say so explicitly.
"""
    return agent
```

### A/B Test Runner

```python
def run_ab_test(question: str, llms: LlmsTxt):
    """Compare baseline agent vs. DocStratum-enhanced agent."""
    baseline_response = baseline_agent.invoke(question)
    docstratum_response = docstratum_agent.invoke(question)
    return {"baseline": baseline_response, "docstratum": docstratum_response}
```

---

## 🎯 Success Criteria

This logic core phase is complete when:

- ✅ Loader module validates `/llms.txt` files with Pydantic
- ✅ Context builder generates token-budgeted system prompts
- ✅ Baseline agent runs without errors
- ✅ DocStratum agent successfully injects context
- ✅ A/B harness produces quantitative comparison metrics
- ✅ All components have unit tests
- ✅ Integration tests pass end-to-end

---

## 🗺️ Next Phase

After completing logic core, proceed to:

- **`05-demo-layer/`** — Streamlit UI and visualization
