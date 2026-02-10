# Agent Architecture & Provider Abstraction

> **v0.3.3a Baseline Agent — Logic Core**
> Defines the DocumentationAgent class as a unified interface across multiple LLM providers (OpenAI, Anthropic Claude, Ollama). This document establishes the foundational architecture that v0.3.4 will extend with DocStratum context injection.

## Objective

Create a provider-agnostic DocumentationAgent class that:
- Encapsulates LLM provider selection and configuration logic
- Manages conversation state and context window constraints
- Collects standardized metrics (tokens, latency, model identification)
- Provides a clean invoke(question) interface regardless of provider
- Enables swappable provider implementations for comparative testing

## Scope Boundaries

**INCLUDES:**
- DocumentationAgent class with __init__, invoke(), and helper methods
- LLM provider abstraction layer (OpenAI, Anthropic, Ollama)
- Configuration management (model names, API keys, temperature defaults)
- Error handling for rate limits, network timeouts, missing credentials
- Response parsing and metric extraction
- Conversation history management

**EXCLUDES:**
- Business logic specific to documentation retrieval
- DocStratum context injection (handled in v0.3.4)
- Web scraping or content fetching
- Persistent storage/database operations
- User authentication beyond API key validation

## Dependency Diagram

```
DocumentationAgent (orchestrator)
├── LLMProvider (abstract base)
│   ├── OpenAIProvider
│   │   └── ChatOpenAI (from langchain-openai)
│   ├── AnthropicProvider
│   │   └── ChatAnthropic (from langchain-anthropic)
│   └── OllamaProvider
│       └── ChatOllama (from langchain-community)
├── Configuration (model, temperature, timeout)
├── ConversationHistory (list of HumanMessage, AIMessage)
└── AgentResponse (dataclass for structured output)
```

---

## 1. DocumentationAgent Class Design

### Why a Class, Not a Function

Using a class provides **state management** and **lifecycle control**:
- **Conversation History**: Maintains multi-turn context across invocations
- **Configuration State**: Stores model selection, temperature, API keys once at init
- **Provider Lifecycle**: Manages connection pooling, rate limit state
- **Metrics Aggregation**: Tracks cumulative token usage across invocations
- **Error Recovery**: Remembers previous failures for fallback logic

### Class Structure

```python
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class ProviderType(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"

@dataclass
class AgentResponse:
    """Structured response from DocumentationAgent.invoke()"""
    response: str
    model: str
    provider: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float
    timestamp: str
    finish_reason: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "response": self.response,
            "model": self.model,
            "provider": self.provider,
            "tokens": {
                "prompt": self.prompt_tokens,
                "completion": self.completion_tokens,
                "total": self.total_tokens
            },
            "latency_ms": self.latency_ms,
            "timestamp": self.timestamp,
            "finish_reason": self.finish_reason,
            "error": self.error
        }

class DocumentationAgent:
    def __init__(
        self,
        system_prompt: str,
        provider: ProviderType = ProviderType.OPENAI,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        api_key: Optional[str] = None,
        timeout_sec: int = 30
    ):
        """
        Initialize DocumentationAgent with specified LLM provider.

        Args:
            system_prompt: System message for the agent (injected into every call)
            provider: Which LLM provider to use (OPENAI, ANTHROPIC, OLLAMA)
            model: Model name (if None, uses provider default)
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens in response
            api_key: API key for provider (or use env var)
            timeout_sec: API call timeout
        """
        self.system_prompt = system_prompt
        self.provider_type = provider
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout_sec = timeout_sec

        # Set model name based on provider if not specified
        self.model = model or self._get_default_model(provider)

        # Initialize conversation history
        self.conversation_history: List[Dict[str, str]] = []

        # Metrics tracking
        self.cumulative_prompt_tokens = 0
        self.cumulative_completion_tokens = 0
        self.call_count = 0

        # Initialize the actual LLM provider
        self.llm = self._initialize_provider(provider, api_key)

    def _get_default_model(self, provider: ProviderType) -> str:
        """Return default model name for each provider"""
        defaults = {
            ProviderType.OPENAI: "gpt-4o-mini",
            ProviderType.ANTHROPIC: "claude-3-5-sonnet-20241022",
            ProviderType.OLLAMA: "mistral"
        }
        return defaults[provider]

    def _initialize_provider(self, provider: ProviderType, api_key: Optional[str]):
        """Factory method to initialize correct provider"""
        if provider == ProviderType.OPENAI:
            return self._init_openai(api_key)
        elif provider == ProviderType.ANTHROPIC:
            return self._init_anthropic(api_key)
        elif provider == ProviderType.OLLAMA:
            return self._init_ollama()
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def _init_openai(self, api_key: Optional[str]):
        """Initialize OpenAI provider"""
        import os
        from langchain_openai import ChatOpenAI

        key = api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("OPENAI_API_KEY not provided and not in environment")

        return ChatOpenAI(
            model=self.model,
            api_key=key,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            timeout=self.timeout_sec
        )

    def _init_anthropic(self, api_key: Optional[str]):
        """Initialize Anthropic provider"""
        import os
        from langchain_anthropic import ChatAnthropic

        key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise ValueError("ANTHROPIC_API_KEY not provided and not in environment")

        return ChatAnthropic(
            model=self.model,
            api_key=key,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

    def _init_ollama(self):
        """Initialize Ollama local provider"""
        from langchain_community.chat_models import ChatOllama

        return ChatOllama(
            model=self.model,
            temperature=self.temperature,
            num_predict=self.max_tokens
        )

    def invoke(self, question: str, include_history: bool = False) -> AgentResponse:
        """
        Invoke the agent with a question.

        Args:
            question: User question or prompt
            include_history: If True, include conversation history in context

        Returns:
            AgentResponse dataclass with response and metrics
        """
        import time
        from datetime import datetime, timezone

        try:
            start_time = time.perf_counter()

            # Build message list
            messages = []

            # Add system prompt as first message
            messages.append({"role": "system", "content": self.system_prompt})

            # Add conversation history if requested
            if include_history:
                for msg in self.conversation_history:
                    messages.append(msg)

            # Add current question
            messages.append({"role": "user", "content": question})

            # Call LLM
            response = self.llm.invoke(messages)

            elapsed_ms = (time.perf_counter() - start_time) * 1000

            # Extract response text and metadata
            response_text = response.content

            # Parse token usage from response metadata
            prompt_tokens = 0
            completion_tokens = 0

            if hasattr(response, 'response_metadata'):
                metadata = response.response_metadata
                if 'usage' in metadata:
                    prompt_tokens = metadata['usage'].get('prompt_tokens', 0)
                    completion_tokens = metadata['usage'].get('completion_tokens', 0)
                elif 'token_usage' in metadata:
                    prompt_tokens = metadata['token_usage'].get('prompt_tokens', 0)
                    completion_tokens = metadata['token_usage'].get('completion_tokens', 0)

            total_tokens = prompt_tokens + completion_tokens

            # Update conversation history
            if include_history:
                self.conversation_history.append({"role": "user", "content": question})
                self.conversation_history.append({"role": "assistant", "content": response_text})

            # Update metrics
            self.cumulative_prompt_tokens += prompt_tokens
            self.cumulative_completion_tokens += completion_tokens
            self.call_count += 1

            # Build response
            return AgentResponse(
                response=response_text,
                model=self.model,
                provider=self.provider_type.value,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                latency_ms=elapsed_ms,
                timestamp=datetime.now(timezone.utc).isoformat(),
                finish_reason=getattr(response, 'finish_reason', None)
            )

        except Exception as e:
            return AgentResponse(
                response="",
                model=self.model,
                provider=self.provider_type.value,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                latency_ms=0,
                timestamp=datetime.now(timezone.utc).isoformat(),
                error=str(e)
            )

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []

    def get_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics across all invocations"""
        return {
            "call_count": self.call_count,
            "total_prompt_tokens": self.cumulative_prompt_tokens,
            "total_completion_tokens": self.cumulative_completion_tokens,
            "total_tokens": self.cumulative_prompt_tokens + self.cumulative_completion_tokens,
            "avg_tokens_per_call": (
                (self.cumulative_prompt_tokens + self.cumulative_completion_tokens) / self.call_count
                if self.call_count > 0 else 0
            )
        }
```

---

## 2. LLM Provider Decision Tree

When choosing a provider, consider:

| Factor | OpenAI | Anthropic | Ollama |
|--------|--------|-----------|--------|
| **API Cost** | $0.15/1M input, $0.60/1M output (GPT-4o mini) | $3/1M input, $15/1M output (Claude 3.5) | Free (local) |
| **Latency** | 500-2000ms | 1000-3000ms | 100-500ms (depends on hardware) |
| **Context Window** | 128K tokens | 200K tokens | Variable (Mistral: 32K) |
| **Quality on Documentation** | Excellent | Excellent | Good (Mistral), Fair (Llama 2) |
| **Setup Difficulty** | Easy (API key) | Easy (API key) | Medium (requires local setup) |
| **Privacy** | Data sent to OpenAI | Data sent to Anthropic | All local, no external calls |
| **Citation Behavior** | Good | Excellent | Variable |
| **Few-shot Learning** | Good | Excellent | Good |

**Decision Tree:**
- Need low cost + no privacy concerns? → **Ollama**
- Need best citation behavior + highest quality? → **Anthropic**
- Need balance of cost and quality? → **OpenAI**
- Testing multiple providers? → **Use DocumentationAgent with configurable provider**

---

## 3. Provider Configuration Details

### OpenAI Configuration

```python
# Model selection
OPENAI_MODELS = {
    "gpt-4o-mini": {"context": 128000, "cost_input": 0.15, "cost_output": 0.60},
    "gpt-4": {"context": 8192, "cost_input": 30, "cost_output": 60},
    "gpt-3.5-turbo": {"context": 16384, "cost_input": 0.50, "cost_output": 1.50}
}

# Recommended settings for documentation queries
OPENAI_DEFAULTS = {
    "temperature": 0.7,  # Balance precision with some creativity
    "max_tokens": 2048,  # Enough for detailed answers
    "top_p": 1.0,        # Don't truncate
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
}

# Timeout: 30 seconds for typical API calls
```

### Anthropic Configuration

```python
# Model selection
ANTHROPIC_MODELS = {
    "claude-3-5-sonnet-20241022": {
        "context": 200000,
        "cost_input": 3,
        "cost_output": 15,
        "strengths": ["citations", "reasoning", "few-shot"]
    },
    "claude-3-opus-20250219": {
        "context": 200000,
        "cost_input": 15,
        "cost_output": 75,
        "strengths": ["complex reasoning"]
    }
}

# Recommended settings for documentation queries
ANTHROPIC_DEFAULTS = {
    "temperature": 0.7,
    "max_tokens": 2048,
    "system": "<inject system prompt>",
    "stop_sequences": []
}

# Timeout: 30 seconds
```

### Ollama Configuration

```python
# Model selection (local)
OLLAMA_MODELS = {
    "mistral": {"context": 32768, "size": "7.3GB", "quality": "good"},
    "llama2": {"context": 4096, "size": "3.8GB", "quality": "fair"},
    "neural-chat": {"context": 4096, "size": "4.0GB", "quality": "good"}
}

# Setup required: ollama pull mistral

# Recommended settings
OLLAMA_DEFAULTS = {
    "temperature": 0.7,
    "num_predict": 2048,
    "num_thread": 4,  # CPU threads to use
    "repeat_penalty": 1.1
}

# Timeout: 30 seconds (or longer for slower hardware)
# Endpoint: http://localhost:11434 (default)
```

---

## 4. LangChain Integration

### Import Paths and Initialization

```python
# OpenAI
from langchain_openai import ChatOpenAI
chat = ChatOpenAI(
    model="gpt-4o-mini",
    api_key="sk-...",
    temperature=0.7,
    max_tokens=2048
)

# Anthropic
from langchain_anthropic import ChatAnthropic
chat = ChatAnthropic(
    model="claude-3-5-sonnet-20241022",
    api_key="sk-ant-...",
    temperature=0.7,
    max_tokens=2048
)

# Ollama
from langchain_community.chat_models import ChatOllama
chat = ChatOllama(
    model="mistral",
    base_url="http://localhost:11434",
    temperature=0.7,
    num_predict=2048
)

# Message format (consistent across all)
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
messages = [
    SystemMessage(content="You are a documentation assistant."),
    HumanMessage(content="What is REST API?"),
]
response = chat.invoke(messages)
```

---

## 5. Agent Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│ INITIALIZE                                              │
│ DocumentationAgent(system_prompt, provider, model, ...) │
│ - Validate API key                                      │
│ - Initialize LLM client                                 │
│ - Set up conversation history                           │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ READY STATE                                             │
│ - System prompt loaded                                  │
│ - Metrics initialized                                   │
│ - Ready to accept questions                             │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ INVOKE                                                  │
│ agent.invoke(question, include_history=True)            │
│ - Build message list (system + history + question)      │
│ - Call LLM API                                          │
│ - Parse response and metadata                           │
│ - Update metrics                                        │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ RETURN RESPONSE                                         │
│ AgentResponse(response, model, tokens, latency, ...)    │
│ - Response text                                         │
│ - Token counts                                          │
│ - Latency in milliseconds                               │
│ - Timestamp and provider info                           │
└────────────────────┬────────────────────────────────────┘
                     ↓
│ Loop back to INVOKE for next question,
│ or call clear_history() to reset,
│ or call get_metrics() to inspect totals
```

---

## 6. Error Handling & Resilience

### Common Error Scenarios

```python
class AgentError(Exception):
    """Base exception for agent errors"""
    pass

class APIKeyError(AgentError):
    """Raised when API key is missing or invalid"""
    pass

class RateLimitError(AgentError):
    """Raised when API rate limit exceeded"""
    pass

class TimeoutError(AgentError):
    """Raised when API call times out"""
    pass

class ModelNotFoundError(AgentError):
    """Raised when specified model doesn't exist"""
    pass

# Error handling in invoke()
def invoke(self, question: str, include_history: bool = False) -> AgentResponse:
    try:
        # ... call LLM ...
    except Exception as e:
        error_type = self._classify_error(e)

        if error_type == "rate_limit":
            # Could implement exponential backoff retry
            return AgentResponse(..., error="Rate limited. Retry in 30s.")
        elif error_type == "timeout":
            return AgentResponse(..., error="API timeout. Check network.")
        elif error_type == "api_key":
            return AgentResponse(..., error="Invalid API key.")
        else:
            return AgentResponse(..., error=str(e))

def _classify_error(self, exception: Exception) -> str:
    """Classify exception type for appropriate handling"""
    msg = str(exception).lower()
    if "rate_limit" in msg or "429" in msg:
        return "rate_limit"
    elif "timeout" in msg:
        return "timeout"
    elif "api_key" in msg or "unauthorized" in msg:
        return "api_key"
    else:
        return "unknown"
```

### Retry Logic Example

```python
import time

def invoke_with_retry(
    self,
    question: str,
    max_retries: int = 3,
    backoff_factor: float = 2.0
) -> AgentResponse:
    """Invoke with automatic retry on rate limit"""
    for attempt in range(max_retries):
        response = self.invoke(question)

        if response.error is None:
            return response  # Success

        if "rate_limit" not in response.error:
            return response  # Don't retry non-rate-limit errors

        if attempt < max_retries - 1:
            wait_sec = (backoff_factor ** attempt)
            time.sleep(wait_sec)

    return response  # Return last attempt result
```

---

## Deliverables

1. **DocumentationAgent class** (complete implementation above)
   - __init__() with all parameters
   - invoke() returning AgentResponse
   - Provider initialization methods
   - Metrics aggregation
   - Error handling

2. **Provider initialization methods**
   - _init_openai()
   - _init_anthropic()
   - _init_ollama()

3. **AgentResponse dataclass**
   - All required fields (response, model, tokens, latency, etc.)
   - to_dict() method for serialization

4. **Provider comparison table** (shown above)

5. **Configuration examples** for all three providers

6. **Error handling framework** with classification logic

---

## Acceptance Criteria

- [ ] DocumentationAgent can be instantiated with each provider type
- [ ] invoke() returns AgentResponse with correct token counts from each provider
- [ ] Latency is measured accurately (within 50ms of actual API latency)
- [ ] Conversation history is maintained correctly when include_history=True
- [ ] Metrics aggregation tracks cumulative tokens across multiple invocations
- [ ] API key validation happens at initialization time
- [ ] Errors are caught and returned as AgentResponse with error field set
- [ ] All three providers (OpenAI, Anthropic, Ollama) produce identical AgentResponse structure
- [ ] System prompt is injected into every invoke() call
- [ ] Provider can be swapped by changing a single parameter

---

## Next Step

**v0.3.3b — System Prompt Engineering** will design the baseline system prompt that this DocumentationAgent will use. The baseline prompt must be generic enough to ensure fair comparison with the DocStratum-enhanced prompt in v0.3.4.
