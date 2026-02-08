# /llms.txt Architect

> **Technical Design Document v1.0** | Project Codename: *The DocStratum*
> 

> Author: Deftness | Status: Draft | Last Updated: February 5, 2026
> 

<aside>

**AI Collaborators:** Start here → [Agentic Instructions — AI Collaborator Guide](RR-META-agentic-instructions-ai-collaborator-guide.md)

</aside>

<aside>

**Session Memory:** [Memory Log — Session 001](RR-META-memory-log-session-001.md) — Project initialization, spec research, real-world analysis complete.

</aside>

---

# 1. Executive Summary & The "Writer's Edge"

## 1.1 The Problem: Context Collapse

AI agents browsing documentation websites face a critical failure mode I call **Context Collapse**—the systematic loss of meaning when an LLM encounters unstructured, navigation-heavy, or semantically ambiguous web content.

**Symptoms of Context Collapse:**

<aside>

**The Core Insight:** The problem is not the AI model's reasoning capability. The problem is the *input quality*. Garbage in, garbage out. Current websites were designed for *humans with eyes*, not for *language models with context windows*.

</aside>

## 1.2 The Solution: The DocStratum Architecture

**The DocStratum** is a hand-crafted `/llms.txt` file that acts as a **semantic translation layer** between a documentation website and any visiting AI agent.

It provides three things no sitemap or auto-generated index can:

1. **A Canonical Concept Map:** A human-curated taxonomy of the *ideas* in the documentation, not just the *files*.
2. **Explicit Relationship Declarations:** Statements like "Concept A *depends on* Concept B" that eliminate inference errors.
3. **Few-Shot Training Examples:** Pre-written prompt/response pairs that teach the agent the *correct* way to answer questions about this specific domain.

```
┌─────────────────────────────────────────────────────────────────┐
│                      THE DOCSTRATUM                           │
│                   (llms.txt Architecture)                       │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 1: MASTER INDEX          "What exists?"                  │
│  ├── Canonical URLs                                             │
│  ├── Content Type Tags (tutorial, reference, changelog)         │
│  └── Freshness Timestamps                                       │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 2: CONCEPT MAP            "How do things relate?"        │
│  ├── Core Concepts (Definitions)                                │
│  ├── Dependency Graph (A requires B)                            │
│  └── Anti-Concepts (Common Misconceptions)                      │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 3: FEW-SHOT BANK          "How should I answer?"         │
│  ├── Golden Q&A Pairs                                           │
│  ├── Code Snippet Templates                                     │
│  └── Error Pattern Recognition                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 1.3 The Differentiator: The Writer's Edge

This project is not an engineering flex. It is a **Technical Writing flex**.

<aside>

**The Thesis:** A Technical Writer with strong Information Architecture skills can outperform a sophisticated RAG pipeline by simply *writing better source material*. The DocStratum proves that **structure is a feature**.

</aside>

---

# 2. The Tech Stack (The "Right" Tools)

## 2.1 Recommended Stack

## 2.2 Justification: Why This Stack?

<aside>

**Design Principle:** Choose tools that *amplify writing*, not tools that *replace writing*. The goal is to make the human author's judgment the bottleneck, not the technology.

</aside>

### Why YAML/JSON for Schema?

- **Human-readable:** A writer can edit it without tooling.
- **Diff-friendly:** Git shows exactly what changed between versions.
- **Universal:** Every language and tool can parse it.

### Why Pydantic?

- **Declarative Validation:** Define the *rules* of a valid `llms.txt`, and Pydantic enforces them automatically.
- **Self-Documenting:** The Pydantic model *is* the schema documentation.
- **Error Messages:** Clear, actionable errors when validation fails.

### Why Neo4j?

- **Graph-Native:** Concept relationships (dependency, similarity, hierarchy) are naturally graph-shaped.
- **Cypher Query Language:** Ask questions like *"What concepts have no dependencies?"* in one line.
- **Free Tier:** Neo4j Aura's free tier is sufficient for a PoC.

### Why Obsidian?

- **Backlinks:** Automatically surfaces implicit relationships as you write.
- **Graph View:** See the "shape" of your concept map in real-time.
- **Markdown-Native:** The output is plain Markdown—no vendor lock-in.

### Why LangChain?

- **Agent Abstraction:** Test how a real agent *uses* the `llms.txt` file.
- **Prompt Templating:** Inject the `llms.txt` content into the agent's system prompt.
- **A/B Testing:** Run the same query with and without the DocStratum context.

### Why Streamlit?

- **Zero Frontend Code:** Build a web UI with pure Python.
- **Rapid Prototyping:** Go from script to shareable demo in under an hour.
- **Portfolio-Friendly:** Embed live demos in your portfolio.

---

# 3. Implementation Roadmap (The "Build")

## 3.1 Phase 1: Data Preparation

**Goal:** Transform raw documentation into a structured `llms.txt` file.

### Step 1.1: Source Audit

Select a target documentation site. For this PoC, I recommend using **your own project's documentation** or a well-known open-source project with permissive licensing (e.g., FastAPI, Streamlit, or Pydantic itself).

### Step 1.2: Schema Definition

Define the Pydantic model for the `llms.txt` file:

```python
# schemas/llms_schema.py
from pydantic import BaseModel, HttpUrl
from typing import Literal
from datetime import date

class CanonicalPage(BaseModel):
    url: HttpUrl
    title: str
    content_type: Literal["tutorial", "reference", "changelog", "concept", "faq"]
    last_verified: date
    summary: str  # Max 280 characters—Tweet-length.

class Concept(BaseModel):
    id: str  # e.g., "auth-oauth2"
    name: str
    definition: str  # One sentence. No pronouns.
    related_pages: list[str]  # List of CanonicalPage URLs
    depends_on: list[str]  # List of other Concept IDs
    anti_patterns: list[str]  # Common misconceptions

class FewShotExample(BaseModel):
    intent: str  # e.g., "How do I authenticate?"
    question: str
    ideal_answer: str
    source_pages: list[str]

class LlmsTxt(BaseModel):
    schema_version: str
    site_name: str
    site_url: HttpUrl
    last_updated: date
    pages: list[CanonicalPage]
    concepts: list[Concept]
    few_shot_examples: list[FewShotExample]
```

### Step 1.3: Before vs. After (Data Schema)

**BEFORE: Raw Sitemap (What Agents See Today)**

```xml
<!-- Typical sitemap.xml — No semantic value -->
<urlset>
  <url><loc>https://docs.example.com/getting-started</loc></url>
  <url><loc>https://docs.example.com/api/auth</loc></url>
  <url><loc>https://docs.example.com/api/users</loc></url>
  <url><loc>https://docs.example.com/changelog</loc></url>
  <!-- 200 more URLs with no context... -->
</urlset>
```

**AFTER: The DocStratum (`llms.txt`)**

```yaml
# llms.txt — The Platinum Standard
schema_version: "1.0"
site_name: "Example API Documentation"
site_url: "https://docs.example.com"
last_updated: "2026-02-05"

pages:
  - url: "https://docs.example.com/getting-started"
    title: "Getting Started Guide"
    content_type: "tutorial"
    last_verified: "2026-02-01"
    summary: "Step-by-step instructions to install the SDK and make your first API call in under 5 minutes."

  - url: "https://docs.example.com/api/auth"
    title: "Authentication Reference"
    content_type: "reference"
    last_verified: "2026-02-01"
    summary: "Complete reference for OAuth2 and API key authentication methods, including token refresh logic."

concepts:
  - id: "auth-oauth2"
    name: "OAuth2 Authentication"
    definition: "OAuth2 is the primary authentication method for user-facing applications that require access to user data."
    related_pages:
      - "https://docs.example.com/api/auth"
      - "https://docs.example.com/getting-started"
    depends_on:
      - "concept-api-keys"
    anti_patterns:
      - "OAuth2 is NOT required for server-to-server integrations. Use API keys instead."
      - "OAuth2 tokens expire after 1 hour. Do NOT hardcode tokens."

few_shot_examples:
  - intent: "User wants to authenticate a web application"
    question: "How do I add login to my React app?"
    ideal_answer: |
      To add OAuth2 login to a React app:
      1. Register your app at https://docs.example.com/api/auth#register
      2. Install the SDK: `npm install @example/auth-sdk`
      3. Initialize with your client ID:
```

import { ExampleAuth } from '@example/auth-sdk';

const auth = new ExampleAuth({ clientId: 'YOUR_CLIENT_ID' });

```
  4. Call `auth.login()` to trigger the OAuth2 flow.
  See the full tutorial: https://docs.example.com/getting-started
source_pages:
  - "https://docs.example.com/getting-started"
  - "https://docs.example.com/api/auth"
```

## 3.2 Phase 2: The Logic Core

**Goal:** Build a Python script that validates, loads, and serves the `llms.txt` to an AI agent.

### High-Level Logic Flow

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

### Pseudo-Code: Main Script

```python
# main.py — The DocStratum Engine

from schemas.llms_schema import LlmsTxt
from pathlib import Path
import yaml

# ─────────────────────────────────────────────────────────────────
# STEP 1: Load and Validate
# ─────────────────────────────────────────────────────────────────
def load_llms_txt(filepath: Path) -> LlmsTxt:
    """Load and validate the llms.txt file."""
    raw_data = yaml.safe_load(filepath.read_text())
    return LlmsTxt(**raw_data)  # Pydantic validates on instantiation

# ─────────────────────────────────────────────────────────────────
# STEP 2: Build Context Block
# ─────────────────────────────────────────────────────────────────
def build_context_block(llms: LlmsTxt) -> str:
    """Transform the llms.txt into a system prompt injection."""
    
    context_parts = []
    
    # Section 1: Site Overview
    context_parts.append(f"# Documentation Context: {llms.site_name}")
    context_parts.append(f"Source: {llms.site_url}")
    context_parts.append(f"Last Updated: {llms.last_updated}\n")
    
    # Section 2: Concept Definitions
    context_parts.append("## Core Concepts")
    for concept in llms.concepts:
        context_parts.append(f"- **{concept.name}**: {concept.definition}")
        if concept.anti_patterns:
            context_parts.append(f"  - ⚠️ Anti-pattern: {concept.anti_patterns[0]}")
    
    # Section 3: Few-Shot Examples
    context_parts.append("\n## Example Q&A (Follow this format)")
    for example in llms.few_shot_examples[:3]:  # Limit to save tokens
        context_parts.append(f"**Q:** {example.question}")
        context_parts.append(f"**A:** {example.ideal_answer}\n")
    
    return "\n".join(context_parts)

# ─────────────────────────────────────────────────────────────────
# STEP 3: Create Enhanced Agent
# ─────────────────────────────────────────────────────────────────
def create_docstratum_agent(context_block: str):
    """Create a LangChain agent with DocStratum context."""
    from langchain_openai import ChatOpenAI
    from langchain.agents import AgentExecutor, create_react_agent
    
    system_prompt = f"""You are a documentation assistant.
    
{context_block}

When answering questions:
1. Cite specific URLs from the documentation.
2. Follow the format shown in the examples above.
3. If the answer is not in the documentation, say so explicitly.
"""
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    # ... (agent setup continues)
    return agent

# ─────────────────────────────────────────────────────────────────
# STEP 4: A/B Test Runner
# ─────────────────────────────────────────────────────────────────
def run_ab_test(question: str, llms: LlmsTxt):
    """Compare baseline agent vs. DocStratum-enhanced agent."""
    
    # Baseline: No context
    baseline_agent = create_baseline_agent()
    baseline_response = baseline_agent.invoke(question)
    
    # Enhanced: With DocStratum
    context_block = build_context_block(llms)
    docstratum_agent = create_docstratum_agent(context_block)
    docstratum_response = docstratum_agent.invoke(question)
    
    return {
        "question": question,
        "baseline": baseline_response,
        "docstratum": docstratum_response
    }
```

## 3.3 Phase 3: The Demo

**Goal:** Build a visual proof that the DocStratum improves agent performance.

### Option A: Streamlit Side-by-Side Comparison

```python
# demo/app.py — Streamlit Demo
import streamlit as st
from main import load_llms_txt, run_ab_test

st.title("🗿 The DocStratum — A/B Tester")

# Load the llms.txt
llms = load_llms_txt("llms.txt")

# User input
question = st.text_input("Ask a question about the documentation:")

if st.button("Compare"):
    with st.spinner("Running A/B test..."):
        results = run_ab_test(question, llms)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("❌ Baseline Agent")
        st.write(results["baseline"])
    
    with col2:
        st.subheader("✅ DocStratum-Enhanced Agent")
        st.write(results["docstratum"])
```

### Option B: Terminal Output (Lightweight)

```
╔══════════════════════════════════════════════════════════════════╗
║                   DOCSTRATUM A/B TEST                          ║
╠══════════════════════════════════════════════════════════════════╣
║ QUESTION: How do I refresh an OAuth2 token?                      ║
╠══════════════════════════════════════════════════════════════════╣
║ BASELINE AGENT:                                                  ║
║ "To refresh an OAuth2 token, you typically call the /token       ║
║ endpoint with a refresh_token grant type..." [GENERIC]           ║
╠══════════════════════════════════════════════════════════════════╣
║ DOCSTRATUM AGENT:                                                   ║
║ "To refresh a token in the Example API:                          ║
║ 1. Call POST https://api.example.com/oauth/token                 ║
║ 2. Include `grant_type=refresh_token` and your refresh token     ║
║ 3. Tokens expire after 1 hour (see anti-pattern note)            ║
║ Source: https://docs.example.com/api/auth#token-refresh"         ║
╚══════════════════════════════════════════════════════════════════╝
```

### Option C: Neo4j Graph Visualization

Export the concept graph to Neo4j and screenshot the visual representation of dependencies.

---

# 4. Testing & Validation Strategy

## 4.1 Validation Framework

<aside>

**Testing Philosophy:** Don't test if the code *runs*. Test if the *output is useful*. These are behavioral tests, not unit tests.

</aside>

## 4.2 Three Validation Prompts

### Test 1: The Disambiguation Test

**Purpose:** Prove the agent can distinguish between similar concepts.

### Test 2: The Freshness Test

**Purpose:** Prove the agent respects version/date information.

### Test 3: The Few-Shot Adherence Test

**Purpose:** Prove the agent follows the prescribed answer format.

---

# 5. Documentation & Deliverables

## 5.1 Repository Artifacts

Your GitHub repository should include:

## 5.2 Architecture Diagram Checklist

Include these diagrams (create with Mermaid, Excalidraw, or [draw.io](http://draw.io)):

- [ ]  **System Context Diagram:** Shows the `llms.txt` file, the agent, and the documentation site.
- [ ]  **Data Flow Diagram:** Shows how data moves from YAML → Pydantic → System Prompt → Agent.
- [ ]  **Concept Graph Sample:** A Neo4j screenshot or Obsidian graph view showing concept relationships.

## 5.3 Resume Bullet Points

After completing this project, add these to your resume:

- **Architected a semantic indexing protocol (`llms.txt`)** that improved AI agent task completion rates on documentation sites by reducing context pollution and eliminating navigation-induced hallucinations.
- **Designed and implemented a Pydantic-validated schema** for machine-readable documentation, enabling deterministic validation of AI-ready content structures.
- **Built an A/B testing harness using LangChain and Streamlit** to quantitatively demonstrate the impact of structured few-shot examples on LLM response accuracy.

---

# 6. Learning Outcomes

By completing The DocStratum, you will gain practical experience in:

## Technical Concepts

## Tools & Frameworks

- **Pydantic:** Data validation and settings management.
- **LangChain:** LLM application framework.
- **Neo4j (Cypher):** Graph database queries.
- **Streamlit:** Rapid web app prototyping.
- **YAML/JSON Schema:** Declarative data structure definition.

## Soft Skills

- Translating abstract AI problems into concrete, testable hypotheses.
- Writing documentation that serves as both human reference and machine input.
- Communicating technical architecture decisions to non-technical stakeholders.

---

<aside>

**Next Steps:** 

1. Fork a starter template or create a new repository.
2. Define your target documentation site.
3. Draft your first `llms.txt` file in Obsidian.
4. Validate with Pydantic.
5. Build the Streamlit demo.
6. Record a 2-minute demo video for your portfolio.
</aside>

---

*Document Version: 1.1 | Status: Ready for Implementation*

> **[v0.0.7] Ecosystem Pivot Note (2026-02-07):** DocStratum's scope has been expanded from single-file llms.txt validator to ecosystem-level documentation quality platform. The core architecture (3-layer context, validation pipeline, quality scoring) remains unchanged. New capabilities include: multi-file ecosystem discovery, cross-file link resolution, ecosystem health scoring, and 12 new diagnostic codes. All implementation targets (v0.1.x–v0.6.0) are unchanged; ecosystem features are integrated into existing modules (v0.1.2 for schema, v0.2.7–v0.2.8 for pipeline, v0.6.0 for demo). See `RR-SPEC-v0.0.6-platinum-standard-definition.md` and `RR-SPEC-v0.0.7-ecosystem-pivot-specification.md` for full specifications.

[Agentic Instructions — AI Collaborator Guide](RR-META-agentic-instructions-ai-collaborator-guide.md)

[Memory Log — Session 001](RR-META-memory-log-session-001.md)

[v0.0.0 — Research & Discovery](RR-SPEC-v0.0.0-research-and-discovery.md)

[v0.1.0 — Project Foundation](RR-SPEC-v0.1.0-project-foundation.md)

[v0.2.0 — Data Preparation](RR-SPEC-v0.2.0-data-preparation.md)

[v0.3.0 — Logic Core](RR-SPEC-v0.3.0-logic-core.md)

[v0.4.0 — Demo Layer](RR-SPEC-v0.4.0-demo-layer.md)

[v0.5.0 — Testing & Validation](RR-SPEC-v0.5.0-testing-and-validation.md)

[v0.6.0 — Documentation & Release](RR-SPEC-v0.6.0-documentation-and-release.md)

**[v0.0.7] Ecosystem & Quality Standard Specifications:**

[v0.0.6 — Platinum Standard Definition](RR-SPEC-v0.0.6-platinum-standard-definition.md)

[v0.0.7 — Ecosystem Pivot Specification](RR-SPEC-v0.0.7-ecosystem-pivot-specification.md)