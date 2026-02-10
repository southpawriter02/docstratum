# v0.3.3 — Baseline Agent

> **Task:** Create a LangChain agent without DocStratum context as the control group.
> 

---

## Task Overview

---

## Implementation

### File: `core/[agents.py](http://agents.py)`

```python
"""Agent factory for baseline and enhanced agents."""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
logger = logging.getLogger(__name__)

BASELINE_SYSTEM_PROMPT = """You are a helpful documentation assistant.

When answering questions:
- Be concise and accurate
- If you don't know something, say so
- Provide code examples when relevant
"""

class DocumentationAgent:
    """A simple agent for answering documentation questions."""
    
    def __init__(
        self,
        system_prompt: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.0,
        api_key: Optional[str] = None
    ):
        """Initialize the agent.
        
        Args:
            system_prompt: The system message for the agent.
            model: OpenAI model name.
            temperature: Sampling temperature (0 = deterministic).
            api_key: OpenAI API key (defaults to env var).
        """
        self.system_prompt = system_prompt
        self.model_name = model
        
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key or os.getenv("OPENAI_API_KEY")
        )
        self.parser = StrOutputParser()
        
        logger.info(f"Initialized agent with model: {model}")
    
    def invoke(self, question: str) -> dict:
        """Ask the agent a question.
        
        Args:
            question: The user's question.
            
        Returns:
            Dictionary with response and metadata.
        """
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=question)
        ]
        
        logger.debug(f"Invoking agent with: {question[:50]}...")
        
        response = self.llm.invoke(messages)
        parsed = self.parser.invoke(response)
        
        return {
            'response': parsed,
            'model': self.model_name,
            'prompt_tokens': response.response_metadata.get('token_usage', {}).get('prompt_tokens', 0),
            'completion_tokens': response.response_metadata.get('token_usage', {}).get('completion_tokens', 0),
        }

def create_baseline_agent(
    model: str = "gpt-4o-mini",
    temperature: float = 0.0
) -> DocumentationAgent:
    """Create a baseline agent without DocStratum context.
    
    This agent has only a generic system prompt and no
    documentation-specific context.
    
    Returns:
        Configured DocumentationAgent.
    """
    logger.info("Creating baseline agent (no context)")
    return DocumentationAgent(
        system_prompt=BASELINE_SYSTEM_PROMPT,
        model=model,
        temperature=temperature
    )

def create_docstratum_agent(
    context_block: str,
    model: str = "gpt-4o-mini",
    temperature: float = 0.0
) -> DocumentationAgent:
    """Create an enhanced agent with DocStratum context.
    
    Args:
        context_block: The context from build_context_block().
        
    Returns:
        Configured DocumentationAgent with context.
    """
    logger.info(f"Creating DocStratum agent ({len(context_block)} chars context)")
    return DocumentationAgent(
        system_prompt=context_block,
        model=model,
        temperature=temperature
    )
```

---

## Environment Setup

### File: `.env`

```bash
# Copy from .env.example and fill in
OPENAI_API_KEY=sk-your-actual-key-here
```

---

## Manual Test

```python
# test_agents_manual.py (not in pytest)
from core.agents import create_baseline_agent

agent = create_baseline_agent()
result = agent.invoke("How do I authenticate with OAuth2?")
print(result['response'])
print(f"Tokens: {result['prompt_tokens']} + {result['completion_tokens']}")
```

---

## 📂 Sub-Part Pages

[v0.3.3a — Agent Architecture & Provider Abstraction](RR-SPEC-v0.3.3a-agent-architecture-and-provider-abstraction.md) — DocumentationAgent class, multi-provider support (OpenAI/Anthropic/Ollama), provider decision tree, error handling

[v0.3.3b — System Prompt Engineering](RR-SPEC-v0.3.3b-system-prompt-engineering.md) — Baseline prompt design, 5-part structure, anti-gaming measures, prompt versioning, token analysis

[v0.3.3c — Response Capture & Metrics Collection](RR-SPEC-v0.3.3c-response-capture-and-metrics-collection.md) — invoke() design, AgentResponse dataclass, latency measurement, error handling, JSON serialization

[v0.3.3d — Environment Setup & Dependency Management](RR-SPEC-v0.3.3d-environment-setup-and-dependency-management.md) — .env strategy, API key security, requirements.txt, mock testing, CI/CD setup

---

## Acceptance Criteria

- [ ]  `create_baseline_agent()` returns working agent
- [ ]  Agent responds to questions
- [ ]  Response includes token counts
- [ ]  Agent uses generic system prompt
- [ ]  API key loaded from environment
- [ ]  **v0.3.3a:** Multi-provider abstraction supports OpenAI, Anthropic, and Ollama
- [ ]  **v0.3.3b:** Baseline prompt is generic enough for fair A/B comparison
- [ ]  **v0.3.3c:** Token counts and latency captured in structured AgentResponse
- [ ]  **v0.3.3d:** Tests pass without real API keys (mocked)