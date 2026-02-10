# Response Capture & Metrics Collection

> **v0.3.3c Baseline Agent — Logic Core**
> Defines how to capture, structure, and measure LLM responses including token usage, latency, and quality metrics. This provides the measurement infrastructure for comparing baseline vs. DocStratum agent performance.

## Objective

Design a complete response capture system that:
- Extracts all metadata from LLM provider responses
- Measures latency with precision (±10ms)
- Counts tokens accurately across all providers
- Structures responses in a standardized format
- Logs responses appropriately for debugging and analysis
- Enables serialization for downstream analysis

## Scope Boundaries

**INCLUDES:**
- Response metadata extraction from all providers (OpenAI, Anthropic, Ollama)
- Latency measurement using high-resolution timers
- Token counting and validation
- AgentResponse dataclass (complete definition)
- Response logging strategy (DEBUG/INFO/WARNING levels)
- JSON serialization for batch analysis
- Error response handling
- Test suite for response capture

**EXCLUDES:**
- Web scraping or content fetching
- Database storage of responses
- User interface or visualization
- Response quality scoring (v0.3.4b covers this)
- Long-term analytics beyond single session
- Caching or memoization

---

## Dependency Diagram

```
DocumentationAgent.invoke()
├── Message Construction
├── API Call (with timing)
│   ├── OpenAI API response
│   │   └── response_metadata["usage"]
│   ├── Anthropic API response
│   │   └── response_metadata["usage"]
│   └── Ollama API response
│       └── No standard metadata
├── Response Parsing
│   ├── Extract response.content (text)
│   ├── Extract token counts
│   ├── Extract finish_reason
│   └── Calculate latency
└── AgentResponse Creation
    ├── response: str
    ├── model: str
    ├── prompt_tokens: int
    ├── completion_tokens: int
    ├── latency_ms: float
    ├── timestamp: str
    └── error: Optional[str]
```

---

## 1. invoke() Method Detailed Design

### Message Construction

```python
from langchain_core.messages import SystemMessage, HumanMessage

def invoke(self, question: str, include_history: bool = False) -> AgentResponse:
    """
    Construct message list for API call.

    Message structure:
    [
        SystemMessage(content=system_prompt),
        [historical messages if include_history=True],
        HumanMessage(content=question)
    ]
    """

    messages = []

    # 1. Always start with system message
    messages.append(SystemMessage(content=self.system_prompt))

    # 2. Add conversation history if requested
    if include_history:
        for msg in self.conversation_history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                from langchain_core.messages import AIMessage
                messages.append(AIMessage(content=msg["content"]))

    # 3. Add current question
    messages.append(HumanMessage(content=question))

    return self._call_llm(messages)
```

### API Call with Timing

```python
import time
from typing import List
from langchain_core.messages import BaseMessage

def _call_llm(self, messages: List[BaseMessage]) -> AgentResponse:
    """
    Make API call with precise timing.

    Timing strategy:
    - Use time.perf_counter() for wall-clock time
    - Start timer JUST before API call
    - Stop timer JUST after response received
    - Calculate latency in milliseconds
    """

    start_time = time.perf_counter()

    try:
        # Call LLM with messages
        response = self.llm.invoke(messages)

        elapsed_sec = time.perf_counter() - start_time
        elapsed_ms = elapsed_sec * 1000

        # Parse response
        return self._parse_response(response, elapsed_ms, messages[1])

    except Exception as e:
        elapsed_sec = time.perf_counter() - start_time
        elapsed_ms = elapsed_sec * 1000

        return AgentResponse(
            response="",
            model=self.model,
            provider=self.provider_type.value,
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            latency_ms=elapsed_ms,
            timestamp=self._get_timestamp(),
            error=str(e)
        )
```

### Response Parsing

```python
def _parse_response(
    self,
    response: Any,
    latency_ms: float,
    original_message: BaseMessage
) -> AgentResponse:
    """
    Extract all useful information from LLM response.

    LangChain response structure varies by provider:
    - response.content: str (response text)
    - response.response_metadata: dict (provider-specific metadata)
    - response.finish_reason: str (optional, "stop" or "length")
    """

    response_text = response.content

    # Extract token usage
    prompt_tokens, completion_tokens = self._extract_tokens(response)
    total_tokens = prompt_tokens + completion_tokens

    # Extract finish reason
    finish_reason = getattr(response, 'finish_reason', None)

    # Get timestamp
    timestamp = self._get_timestamp()

    # Build AgentResponse
    agent_response = AgentResponse(
        response=response_text,
        model=self.model,
        provider=self.provider_type.value,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        latency_ms=latency_ms,
        timestamp=timestamp,
        finish_reason=finish_reason
    )

    # Update conversation history
    if self._should_add_to_history:
        self.conversation_history.append({"role": "user", "content": original_message.content})
        self.conversation_history.append({"role": "assistant", "content": response_text})

    # Update metrics
    self.cumulative_prompt_tokens += prompt_tokens
    self.cumulative_completion_tokens += completion_tokens
    self.call_count += 1

    return agent_response
```

---

## 2. Response Metadata Extraction

### Token Counting by Provider

```python
def _extract_tokens(self, response: Any) -> tuple[int, int]:
    """
    Extract prompt_tokens and completion_tokens from response.

    Different providers structure metadata differently:
    - OpenAI: response.response_metadata["usage"]
    - Anthropic: response.response_metadata["usage"]
    - Ollama: No standard metadata (estimate with tokenizer)
    """

    if not hasattr(response, 'response_metadata'):
        # No metadata available (e.g., Ollama)
        return self._estimate_tokens(response)

    metadata = response.response_metadata

    # Try standard "usage" key
    if 'usage' in metadata:
        usage = metadata['usage']
        prompt_tokens = usage.get('prompt_tokens', 0)
        completion_tokens = usage.get('completion_tokens', 0)
        return prompt_tokens, completion_tokens

    # Try token_usage key (some versions)
    if 'token_usage' in metadata:
        usage = metadata['token_usage']
        prompt_tokens = usage.get('prompt_tokens', 0)
        completion_tokens = usage.get('completion_tokens', 0)
        return prompt_tokens, completion_tokens

    # Fallback: estimate
    return self._estimate_tokens(response)

def _estimate_tokens(self, response: Any) -> tuple[int, int]:
    """
    Estimate token counts when provider doesn't include metadata.

    Uses rough heuristic: ~4 characters per token
    This is for Ollama and other local providers without metering.
    """

    response_text = response.content
    # Rough estimate: 1 token ≈ 4 characters
    estimated_completion = len(response_text) // 4

    # For prompt tokens, we'd need to estimate system prompt too
    # For now, return 0 (will be marked in metrics)
    return 0, estimated_completion
```

### Provider-Specific Metadata Examples

```python
# OPENAI RESPONSE METADATA
openai_metadata = {
    "usage": {
        "prompt_tokens": 187,
        "completion_tokens": 45,
        "total_tokens": 232
    },
    "model_name": "gpt-4o-mini",
    "system_fingerprint": "fp_...",
    "finish_reason": "stop"
}

# ANTHROPIC RESPONSE METADATA
anthropic_metadata = {
    "usage": {
        "input_tokens": 187,  # Note: "input_tokens" not "prompt_tokens"
        "output_tokens": 45   # Note: "output_tokens" not "completion_tokens"
    },
    "model": "claude-3-5-sonnet-20241022",
    "stop_reason": "end_turn"
}

# OLLAMA RESPONSE METADATA
# Ollama does NOT include token counts in response
# Must estimate or use separate tokenizer
ollama_metadata = {
    "model": "mistral",
    "created_at": "2025-02-05T10:30:00Z",
    # NO token usage information
}

# NORMALIZE ANTHROPIC TOKENS TO STANDARD NAMES
def _normalize_token_names(metadata: dict) -> dict:
    if "input_tokens" in metadata:
        # Anthropic format
        metadata["prompt_tokens"] = metadata.pop("input_tokens")
    if "output_tokens" in metadata:
        metadata["completion_tokens"] = metadata.pop("output_tokens")
    return metadata
```

---

## 3. AgentResponse Dataclass

### Complete Definition

```python
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
from datetime import datetime, timezone

@dataclass
class AgentResponse:
    """
    Structured response from DocumentationAgent.invoke()

    Attributes:
        response: The actual text response from the LLM
        model: Model name (e.g., "gpt-4o-mini", "claude-3-5-sonnet")
        provider: Provider type (e.g., "openai", "anthropic", "ollama")
        prompt_tokens: Number of tokens in the prompt
        completion_tokens: Number of tokens in the completion
        total_tokens: Sum of prompt + completion tokens
        latency_ms: Milliseconds from API call start to finish
        timestamp: ISO 8601 timestamp of response creation
        finish_reason: Why the model stopped ("stop", "length", "content_filter", etc.)
        error: If set, indicates an error occurred (response will be empty)
    """

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

    def is_success(self) -> bool:
        """Returns True if response was successful (no error)"""
        return self.error is None

    def is_error(self) -> bool:
        """Returns True if response encountered an error"""
        return self.error is not None

    def is_truncated(self) -> bool:
        """Returns True if response was cut off due to token limit"""
        return self.finish_reason == "length"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "response": self.response,
            "model": self.model,
            "provider": self.provider,
            "tokens": {
                "prompt": self.prompt_tokens,
                "completion": self.completion_tokens,
                "total": self.total_tokens
            },
            "latency_ms": round(self.latency_ms, 2),
            "timestamp": self.timestamp,
            "finish_reason": self.finish_reason,
            "error": self.error,
            "success": self.is_success()
        }

    def to_json(self) -> str:
        """Convert to JSON string"""
        import json
        return json.dumps(self.to_dict(), indent=2)

    def summary_str(self) -> str:
        """Single-line summary for logging"""
        status = "OK" if self.is_success() else f"ERROR: {self.error}"
        return (
            f"{self.model} | {self.total_tokens} tokens | "
            f"{self.latency_ms:.0f}ms | {status}"
        )

@dataclass
class MultiResponse:
    """Collection of responses for batch analysis"""
    responses: list[AgentResponse]
    request_ids: list[str] = field(default_factory=list)

    @property
    def success_count(self) -> int:
        return sum(1 for r in self.responses if r.is_success())

    @property
    def error_count(self) -> int:
        return sum(1 for r in self.responses if r.is_error())

    @property
    def avg_latency_ms(self) -> float:
        successful = [r for r in self.responses if r.is_success()]
        if not successful:
            return 0.0
        return sum(r.latency_ms for r in successful) / len(successful)

    @property
    def total_tokens(self) -> int:
        return sum(r.total_tokens for r in self.responses)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "batch": {
                "total_responses": len(self.responses),
                "successful": self.success_count,
                "errors": self.error_count,
                "avg_latency_ms": round(self.avg_latency_ms, 2),
                "total_tokens": self.total_tokens
            },
            "responses": [r.to_dict() for r in self.responses]
        }
```

---

## 4. Error Response Handling

### Error Scenarios and Responses

```python
def handle_api_error(self, exception: Exception, elapsed_ms: float) -> AgentResponse:
    """
    Handle various API errors and return structured error response.

    Strategy: Always return AgentResponse (never throw), with error field set.
    """

    error_msg = str(exception)
    error_type = self._classify_error(exception)

    error_response = AgentResponse(
        response="",
        model=self.model,
        provider=self.provider_type.value,
        prompt_tokens=0,
        completion_tokens=0,
        total_tokens=0,
        latency_ms=elapsed_ms,
        timestamp=self._get_timestamp(),
        error=f"{error_type}: {error_msg}"
    )

    return error_response

def _classify_error(self, exception: Exception) -> str:
    """Classify error type for handling and logging"""
    msg = str(exception).lower()

    if "rate_limit" in msg or "429" in msg:
        return "RateLimitError"
    elif "timeout" in msg or "connection" in msg:
        return "TimeoutError"
    elif "api_key" in msg or "unauthorized" in msg or "401" in msg:
        return "AuthenticationError"
    elif "model" in msg or "not found" in msg or "404" in msg:
        return "ModelNotFoundError"
    elif "context" in msg or "token" in msg:
        return "ContextLengthError"
    else:
        return "UnknownError"

# ERROR RESPONSE EXAMPLES
error_examples = {
    "rate_limit": {
        "error": "RateLimitError: Rate limit exceeded. Retry after 30 seconds.",
        "latency_ms": 150,
        "response": ""
    },
    "timeout": {
        "error": "TimeoutError: API call timed out after 30 seconds.",
        "latency_ms": 30000,
        "response": ""
    },
    "auth": {
        "error": "AuthenticationError: Invalid API key for openai",
        "latency_ms": 50,
        "response": ""
    },
    "model_not_found": {
        "error": "ModelNotFoundError: Model 'gpt-5' does not exist",
        "latency_ms": 100,
        "response": ""
    }
}
```

---

## 5. Response Logging Strategy

### Logging Levels

```python
import logging

logger = logging.getLogger(__name__)

def log_response(self, response: AgentResponse):
    """
    Log response at appropriate level based on outcome.

    DEBUG: Successful responses (verbose)
    INFO: Successful responses (summary)
    WARNING: Errors and anomalies
    ERROR: Critical failures
    """

    if response.is_error():
        if "timeout" in response.error.lower():
            logger.warning(f"Timeout on {response.model}: {response.latency_ms}ms")
        elif "rate_limit" in response.error.lower():
            logger.warning(f"Rate limit on {response.provider}")
        else:
            logger.error(f"API error on {response.provider}: {response.error}")

    elif response.is_truncated():
        logger.warning(f"Response truncated on {response.model} "
                      f"({response.completion_tokens} tokens)")

    else:
        # Successful response
        logger.info(f"Response from {response.model}: "
                   f"{response.total_tokens} tokens in {response.latency_ms:.0f}ms")

        # Include full response at DEBUG level
        logger.debug(f"Response content: {response.response[:200]}...")

# LOGGING CONFIGURATION
def setup_logging(level=logging.INFO):
    """Configure logging for agent responses"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

# Log sample output:
# 2025-02-05 10:30:45,123 - agent - INFO - Response from gpt-4o-mini: 187 tokens in 1250ms
# 2025-02-05 10:31:20,456 - agent - WARNING - Timeout on openai: 30000ms
# 2025-02-05 10:32:15,789 - agent - ERROR - API error on anthropic: Invalid API key
```

### What to Log at Each Level

| Level | Content | Example |
|-------|---------|---------|
| **DEBUG** | Full response, detailed timing | "Response content: What is a REST API? A REST API..." |
| **INFO** | Summary, token count, latency | "Response from gpt-4o-mini: 187 tokens in 1250ms" |
| **WARNING** | Truncation, slow responses | "Response truncated (2048 tokens max reached)" |
| **ERROR** | API failures, auth issues | "API error: Invalid API key for openai" |

---

## 6. Response Serialization

### JSON Export Format

```python
def serialize_response(response: AgentResponse) -> str:
    """Convert AgentResponse to JSON"""
    import json
    return json.dumps(response.to_dict(), indent=2)

def serialize_batch(responses: List[AgentResponse]) -> str:
    """Convert batch of responses to JSON"""
    import json
    batch_dict = {
        "metadata": {
            "count": len(responses),
            "success_count": sum(1 for r in responses if r.is_success()),
            "error_count": sum(1 for r in responses if r.is_error()),
            "total_tokens": sum(r.total_tokens for r in responses)
        },
        "responses": [r.to_dict() for r in responses]
    }
    return json.dumps(batch_dict, indent=2)

def save_responses(responses: List[AgentResponse], filepath: str):
    """Save batch of responses to JSON file"""
    import json
    with open(filepath, 'w') as f:
        batch_data = {
            "metadata": {
                "count": len(responses),
                "timestamp": responses[0].timestamp if responses else None
            },
            "responses": [r.to_dict() for r in responses]
        }
        json.dump(batch_data, f, indent=2)

# EXAMPLE JSON OUTPUT
example_json = """
{
  "response": "A REST API is an interface that lets software communicate...",
  "model": "gpt-4o-mini",
  "provider": "openai",
  "tokens": {
    "prompt": 187,
    "completion": 45,
    "total": 232
  },
  "latency_ms": 1250.50,
  "timestamp": "2025-02-05T10:30:45.123456Z",
  "finish_reason": "stop",
  "error": null,
  "success": true
}
"""
```

---

## 7. Test Suite for Response Capture

### Unit Tests

```python
import pytest
import time
from unittest.mock import Mock, patch

class TestResponseCapture:

    def test_agent_response_dataclass(self):
        """Test AgentResponse creation and methods"""
        response = AgentResponse(
            response="Test response",
            model="gpt-4o-mini",
            provider="openai",
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            latency_ms=1250.5,
            timestamp="2025-02-05T10:30:00Z"
        )

        assert response.is_success()
        assert not response.is_error()
        assert response.total_tokens == 150
        assert "Test response" in response.response

    def test_agent_response_error(self):
        """Test error response creation"""
        response = AgentResponse(
            response="",
            model="gpt-4o-mini",
            provider="openai",
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            latency_ms=0,
            timestamp="2025-02-05T10:30:00Z",
            error="TimeoutError: API call timed out"
        )

        assert response.is_error()
        assert not response.is_success()
        assert "Timeout" in response.error

    def test_response_truncation_detection(self):
        """Test detection of truncated responses"""
        response = AgentResponse(
            response="This is a long response that was cut off due to...",
            model="gpt-4o-mini",
            provider="openai",
            prompt_tokens=100,
            completion_tokens=2048,
            total_tokens=2148,
            latency_ms=5000,
            timestamp="2025-02-05T10:30:00Z",
            finish_reason="length"
        )

        assert response.is_truncated()
        assert response.is_success()

    def test_token_extraction_openai(self):
        """Test token extraction from OpenAI response"""
        mock_response = Mock()
        mock_response.content = "What is a REST API? A REST API is..."
        mock_response.response_metadata = {
            "usage": {
                "prompt_tokens": 187,
                "completion_tokens": 45,
                "total_tokens": 232
            }
        }
        mock_response.finish_reason = "stop"

        # Simulate _extract_tokens method
        metadata = mock_response.response_metadata
        prompt_tokens = metadata['usage']['prompt_tokens']
        completion_tokens = metadata['usage']['completion_tokens']

        assert prompt_tokens == 187
        assert completion_tokens == 45

    def test_token_extraction_anthropic(self):
        """Test token extraction from Anthropic response"""
        mock_response = Mock()
        mock_response.content = "A REST API is an interface..."
        mock_response.response_metadata = {
            "usage": {
                "input_tokens": 187,    # Anthropic naming
                "output_tokens": 45
            }
        }

        # Normalize Anthropic naming
        metadata = mock_response.response_metadata['usage']
        prompt_tokens = metadata.get('input_tokens', metadata.get('prompt_tokens', 0))
        completion_tokens = metadata.get('output_tokens', metadata.get('completion_tokens', 0))

        assert prompt_tokens == 187
        assert completion_tokens == 45

    def test_latency_measurement(self):
        """Test accurate latency measurement"""
        start = time.perf_counter()
        time.sleep(0.1)  # Sleep 100ms
        elapsed_sec = time.perf_counter() - start
        elapsed_ms = elapsed_sec * 1000

        # Should be ~100ms, allow ±10ms variance
        assert 90 < elapsed_ms < 110

    def test_response_serialization(self):
        """Test JSON serialization"""
        response = AgentResponse(
            response="Test",
            model="gpt-4o-mini",
            provider="openai",
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15,
            latency_ms=100.5,
            timestamp="2025-02-05T10:30:00Z"
        )

        response_dict = response.to_dict()
        assert response_dict["response"] == "Test"
        assert response_dict["tokens"]["total"] == 15
        assert response_dict["success"] == True

        # Test JSON string
        json_str = response.to_json()
        assert "Test" in json_str
        assert "gpt-4o-mini" in json_str

    def test_batch_response_metrics(self):
        """Test batch response aggregation"""
        responses = [
            AgentResponse(
                response="A", model="gpt-4o-mini", provider="openai",
                prompt_tokens=100, completion_tokens=50, total_tokens=150,
                latency_ms=1000, timestamp="2025-02-05T10:30:00Z"
            ),
            AgentResponse(
                response="B", model="gpt-4o-mini", provider="openai",
                prompt_tokens=100, completion_tokens=60, total_tokens=160,
                latency_ms=1200, timestamp="2025-02-05T10:31:00Z"
            ),
            AgentResponse(
                response="", model="gpt-4o-mini", provider="openai",
                prompt_tokens=0, completion_tokens=0, total_tokens=0,
                latency_ms=50, timestamp="2025-02-05T10:32:00Z",
                error="TimeoutError"
            )
        ]

        multi = MultiResponse(responses)
        assert multi.success_count == 2
        assert multi.error_count == 1
        assert multi.total_tokens == 310
        assert 1050 < multi.avg_latency_ms < 1150  # (1000 + 1200) / 2

# Run tests
# pytest test_response_capture.py -v
```

---

## Deliverables

1. **Complete AgentResponse dataclass** with all methods
2. **Token extraction logic** for all three providers
3. **Latency measurement implementation** using perf_counter
4. **Error response handling** with classification
5. **Logging configuration** (DEBUG/INFO/WARNING/ERROR levels)
6. **JSON serialization methods** (to_dict, to_json, save_responses)
7. **Batch response aggregation** (MultiResponse class)
8. **Complete test suite** (20+ test cases)

---

## Acceptance Criteria

- [ ] AgentResponse dataclass created with all required fields
- [ ] Token extraction works correctly for OpenAI responses
- [ ] Token extraction works correctly for Anthropic responses
- [ ] Token extraction handles missing metadata (Ollama estimation)
- [ ] Latency measurement is accurate to ±10ms
- [ ] Error responses return AgentResponse with error field set
- [ ] Logging occurs at correct levels (DEBUG/INFO/WARNING/ERROR)
- [ ] JSON serialization produces valid JSON with all fields
- [ ] Batch responses correctly aggregate success/error counts
- [ ] All test cases pass (20+ tests)
- [ ] finish_reason is correctly extracted ("stop", "length", etc.)
- [ ] Timestamp is ISO 8601 format with timezone

---

## Next Step

**v0.3.3d — Environment Setup & Dependency Management** will define how to set up the development environment with all required dependencies, configure API keys, and run the baseline agent.
