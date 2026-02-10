# v0.3.5a — Test Execution Engine & Data Structures

> The engine that orchestrates side-by-side agent invocations, captures timing metrics, persists results, and handles failure modes with grace.

## Objective

Design and implement a robust test execution engine that:
- Runs baseline and DocStratum agents sequentially or concurrently with accurate timing
- Captures comprehensive performance and response data in strongly-typed dataclasses
- Persists results to disk for later analysis and historical tracking
- Handles retry logic and error scenarios gracefully
- Manages test sessions as logical groupings with metadata

## Scope Boundaries

- **In scope**: Execution engine, data structures (AgentResponse, ABTestResult), timing instrumentation, result persistence, retry logic, session management
- **Out of scope**: Test question design (v0.3.5b), statistical analysis (v0.3.5c), report generation (v0.3.5d), visualization (v0.4.x)
- **Constraints**: Must support both sync and async execution; timing precision ±10ms; persist to JSON/CSV formats; support batch mode and single-test mode

## Dependency Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   ABTestHarness                         │
│  (orchestrator, manages sessions, invokes engine)       │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│            TestExecutionEngine                          │
│  (core executor, timing, retry, persistence)           │
├──────────────────────────────────────────────────────────┤
│  • invoke_agent(question, model) → AgentResponse       │
│  • run_test(question) → ABTestResult                   │
│  • persist_result(result) → Path                        │
│  • load_session(session_id) → [ABTestResult]            │
└──────────────────┬──────────────────────┬───────────────┘
                   │                      │
        ┌──────────▼──────────┐  ┌────────▼─────────────┐
        │  AgentResponse      │  │  ABTestResult       │
        │  (timing + text)    │  │  (comparison data)  │
        └─────────────────────┘  └─────────────────────┘
```

## Content Sections

### 1. AgentResponse Dataclass Design

The `AgentResponse` captures a single agent invocation:

| Field | Type | Purpose |
|-------|------|---------|
| `response` | `str` | Raw text response from agent |
| `prompt_tokens` | `int` | Tokens in input (from model API) |
| `completion_tokens` | `int` | Tokens in output (from model API) |
| `total_tokens` | `int` | Sum of prompt + completion |
| `latency_ms` | `float` | End-to-end execution time in milliseconds |
| `model` | `str` | Model identifier (e.g., `claude-3-5-sonnet`) |
| `timestamp` | `datetime` | ISO 8601 timestamp of execution |
| `error` | `Optional[str]` | Error message if execution failed |
| `retry_count` | `int` | Number of retries attempted before success |

**Computed Properties:**

```python
@property
def total_tokens(self) -> int:
    """Sum of prompt and completion tokens."""
    return self.prompt_tokens + self.completion_tokens

@property
def tokens_per_ms(self) -> float:
    """Token generation rate (tokens/millisecond)."""
    if self.latency_ms == 0:
        return 0.0
    return self.completion_tokens / self.latency_ms

@property
def success(self) -> bool:
    """Was execution successful (no error)."""
    return self.error is None
```

**Serialization Methods:**

```python
def to_dict(self) -> dict:
    """Convert to dictionary for JSON serialization."""
    return {
        'response': self.response,
        'prompt_tokens': self.prompt_tokens,
        'completion_tokens': self.completion_tokens,
        'total_tokens': self.total_tokens,
        'latency_ms': self.latency_ms,
        'model': self.model,
        'timestamp': self.timestamp.isoformat(),
        'error': self.error,
        'retry_count': self.retry_count,
    }

@classmethod
def from_dict(cls, data: dict) -> 'AgentResponse':
    """Reconstruct from dictionary."""
    return cls(
        response=data['response'],
        prompt_tokens=data['prompt_tokens'],
        completion_tokens=data['completion_tokens'],
        latency_ms=data['latency_ms'],
        model=data['model'],
        timestamp=datetime.fromisoformat(data['timestamp']),
        error=data.get('error'),
        retry_count=data.get('retry_count', 0),
    )
```

### 2. ABTestResult Dataclass Design

The `ABTestResult` represents a complete comparison of baseline vs DocStratum on a single question:

| Field | Type | Purpose |
|-------|------|---------|
| `question` | `str` | The input prompt/test question |
| `baseline` | `AgentResponse` | Response from baseline model |
| `docstratum` | `AgentResponse` | Response from DocStratum model |
| `context_tokens` | `int` | Tokens in llms.txt context (fixed per session) |
| `timestamp` | `datetime` | When test was executed |
| `session_id` | `str` | Links to parent TestSession |
| `metadata` | `dict` | Optional metadata (category, difficulty, etc.) |

**Computed Properties:**

```python
@property
def token_overhead(self) -> int:
    """Extra tokens required by DocStratum vs baseline.

    Returns:
        Negative value means DocStratum uses fewer tokens (improvement).
        Positive value means DocStratum uses more tokens (regression).
    """
    docstratum_total = self.docstratum.total_tokens
    baseline_total = self.baseline.total_tokens
    return docstratum_total - baseline_total

@property
def token_overhead_pct(self) -> float:
    """Percentage increase in tokens for DocStratum."""
    if self.baseline.total_tokens == 0:
        return 0.0
    return (self.token_overhead / self.baseline.total_tokens) * 100

@property
def latency_diff_ms(self) -> float:
    """Latency difference: DocStratum - Baseline.

    Returns:
        Negative value means DocStratum is faster (improvement).
        Positive value means DocStratum is slower (regression).
    """
    return self.docstratum.latency_ms - self.baseline.latency_ms

@property
def latency_improvement_pct(self) -> float:
    """Percentage improvement in latency for DocStratum."""
    if self.baseline.latency_ms == 0:
        return 0.0
    return (self.latency_diff_ms / self.baseline.latency_ms) * 100

@property
def response_length_ratio(self) -> float:
    """Ratio of DocStratum response length to baseline length."""
    if len(self.baseline.response) == 0:
        return 1.0
    return len(self.docstratum.response) / len(self.baseline.response)

@property
def both_successful(self) -> bool:
    """Did both agents complete without errors."""
    return self.baseline.success and self.docstratum.success
```

**Serialization Methods:**

```python
def to_dict(self) -> dict:
    """Convert to dictionary for JSON serialization."""
    return {
        'question': self.question,
        'baseline': self.baseline.to_dict(),
        'docstratum': self.docstratum.to_dict(),
        'context_tokens': self.context_tokens,
        'timestamp': self.timestamp.isoformat(),
        'session_id': self.session_id,
        'metadata': self.metadata,
        'token_overhead': self.token_overhead,
        'latency_diff_ms': self.latency_diff_ms,
    }

@classmethod
def from_dict(cls, data: dict) -> 'ABTestResult':
    """Reconstruct from dictionary."""
    return cls(
        question=data['question'],
        baseline=AgentResponse.from_dict(data['baseline']),
        docstratum=AgentResponse.from_dict(data['docstratum']),
        context_tokens=data['context_tokens'],
        timestamp=datetime.fromisoformat(data['timestamp']),
        session_id=data['session_id'],
        metadata=data.get('metadata', {}),
    )
```

### 3. Test Execution Flow & Ordering

The core execution flow demonstrates best practices for unbiased testing:

```
INPUT: Question → INITIALIZE TIMER
        ↓
    [BASELINE PHASE]
        ↓
    Invoke baseline agent with question
        ↓
    Record: response, tokens, latency
        ↓
    [CACHE RESET WINDOW]
        ↓
        [Wait 100ms to allow cache invalidation]
        ↓
    [DOCSTRATUM PHASE]
        ↓
    Invoke docstratum agent with question
        ↓
    Record: response, tokens, latency
        ↓
    [RESULT ASSEMBLY]
        ↓
    Create ABTestResult with both responses
        ↓
    PERSIST to JSON/CSV
        ↓
    OUTPUT: ABTestResult
```

**Execution Ordering Considerations:**

| Strategy | Pros | Cons | Recommendation |
|----------|------|------|-----------------|
| **Always baseline first** | Simple, consistent | May warm caches; KV cache bias | Use with cache-reset window |
| **Randomized order** | Reduces bias | Hard to reason about; async complexity | Use for 10+ questions |
| **Sequential with reset** | Balanced, simple | Slight latency increase | ✓ **Default for v0.3.5** |
| **Parallel execution** | Fastest total time | Response interference; cost scaling | Optional flag for rapid iteration |

**Implementation (Sequential):**

```python
import time
from datetime import datetime
from typing import Optional

async def invoke_agent(
    self,
    question: str,
    model: str,
    llms_source: LLMSource,
    max_retries: int = 3,
) -> AgentResponse:
    """Invoke a single agent with retry logic and timing."""

    for attempt in range(max_retries):
        try:
            start_time = time.perf_counter()

            # Invoke agent via llms_source API
            response_text = await llms_source.invoke(
                question=question,
                model=model,
            )

            elapsed_ms = (time.perf_counter() - start_time) * 1000

            # Extract token counts from response metadata
            prompt_tokens = llms_source.last_prompt_tokens
            completion_tokens = llms_source.last_completion_tokens

            return AgentResponse(
                response=response_text,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                latency_ms=elapsed_ms,
                model=model,
                timestamp=datetime.utcnow(),
                error=None,
                retry_count=attempt,
            )

        except Exception as e:
            if attempt == max_retries - 1:
                # Final attempt failed
                return AgentResponse(
                    response='',
                    prompt_tokens=0,
                    completion_tokens=0,
                    latency_ms=0.0,
                    model=model,
                    timestamp=datetime.utcnow(),
                    error=str(e),
                    retry_count=attempt,
                )
            # Wait before retry (exponential backoff)
            await asyncio.sleep(2 ** attempt)

async def run_test(
    self,
    question: str,
    session_id: str,
    randomize_order: bool = False,
) -> ABTestResult:
    """Run a single test comparing baseline and DocStratum."""

    models = ['baseline_model', 'docstratum_model']
    if randomize_order:
        import random
        random.shuffle(models)

    responses = {}

    for model in models:
        responses[model] = await self.invoke_agent(
            question=question,
            model=model,
        )
        # Cache reset window
        await asyncio.sleep(0.1)

    result = ABTestResult(
        question=question,
        baseline=responses['baseline_model'],
        docstratum=responses['docstratum_model'],
        context_tokens=self.context_tokens,
        timestamp=datetime.utcnow(),
        session_id=session_id,
        metadata={},
    )

    # Persist immediately
    self.persist_result(result)

    return result
```

### 4. Concurrent Execution Option

For rapid iteration, use ThreadPoolExecutor or asyncio to parallelize:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def run_test_concurrent(
    self,
    question: str,
    session_id: str,
) -> ABTestResult:
    """Run both agents in parallel using asyncio.gather()."""

    baseline_coro = self.invoke_agent(
        question=question,
        model='baseline_model',
    )

    docstratum_coro = self.invoke_agent(
        question=question,
        model='docstratum_model',
    )

    # Run both concurrently
    baseline_resp, docstratum_resp = await asyncio.gather(
        baseline_coro,
        docstratum_coro,
        return_exceptions=False,
    )

    result = ABTestResult(
        question=question,
        baseline=baseline_resp,
        docstratum=docstratum_resp,
        context_tokens=self.context_tokens,
        timestamp=datetime.utcnow(),
        session_id=session_id,
        metadata={},
    )

    self.persist_result(result)
    return result

# Usage flag in ABTestHarness.run_test():
def run_test(
    self,
    question: str,
    concurrent: bool = False,
) -> ABTestResult:
    """Run test with optional concurrency."""
    session_id = self.current_session.session_id

    if concurrent:
        return asyncio.run(self.run_test_concurrent(question, session_id))
    else:
        return asyncio.run(self.run_test(question, session_id))
```

**Performance Comparison:**
- Sequential: ~6 seconds for 3 questions (2 sec × 3 invocations)
- Concurrent: ~4 seconds for 3 questions (2 sec per pair + overhead)
- Speedup: ~33% faster for N questions in parallel mode

### 5. Retry Logic & Error Handling

Implement graceful degradation with exponential backoff:

```python
class ExecutionError(Exception):
    """Raised when test execution fails."""
    pass

class RetryPolicy:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay_ms: int = 100,
        backoff_factor: float = 2.0,
        timeout_ms: int = 30000,
    ):
        self.max_attempts = max_attempts
        self.initial_delay_ms = initial_delay_ms
        self.backoff_factor = backoff_factor
        self.timeout_ms = timeout_ms

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for attempt N."""
        return (self.initial_delay_ms * (self.backoff_factor ** attempt)) / 1000

class TestExecutionEngine:
    """Core engine managing test execution with retries."""

    def __init__(self, retry_policy: RetryPolicy = None):
        self.retry_policy = retry_policy or RetryPolicy()
        self.execution_stats = ExecutionStats()

    async def invoke_agent_with_retry(
        self,
        question: str,
        model: str,
    ) -> AgentResponse:
        """Invoke agent with retry logic."""

        last_error = None

        for attempt in range(self.retry_policy.max_attempts):
            try:
                response = await asyncio.wait_for(
                    self._invoke_agent_internal(question, model),
                    timeout=self.retry_policy.timeout_ms / 1000,
                )

                if attempt > 0:
                    self.execution_stats.record_retry_success(model, attempt)

                return response

            except asyncio.TimeoutError as e:
                last_error = f'Timeout after {self.retry_policy.timeout_ms}ms'
                self.execution_stats.record_timeout(model)

            except Exception as e:
                last_error = str(e)
                self.execution_stats.record_error(model, e)

            # Wait before retry
            if attempt < self.retry_policy.max_attempts - 1:
                delay = self.retry_policy.get_delay(attempt)
                await asyncio.sleep(delay)

        # All retries exhausted
        return AgentResponse(
            response='',
            prompt_tokens=0,
            completion_tokens=0,
            latency_ms=0.0,
            model=model,
            timestamp=datetime.utcnow(),
            error=f'Failed after {self.retry_policy.max_attempts} attempts: {last_error}',
            retry_count=self.retry_policy.max_attempts,
        )

class ExecutionStats:
    """Track execution statistics for monitoring."""

    def __init__(self):
        self.total_invocations = 0
        self.successful_invocations = 0
        self.failed_invocations = 0
        self.retry_count = {}
        self.timeouts = {}
        self.errors_by_type = {}

    def record_success(self, model: str):
        self.successful_invocations += 1

    def record_error(self, model: str, error: Exception):
        self.failed_invocations += 1
        error_type = type(error).__name__
        self.errors_by_type[error_type] = self.errors_by_type.get(error_type, 0) + 1

    def record_retry_success(self, model: str, attempt: int):
        self.retry_count[attempt] = self.retry_count.get(attempt, 0) + 1

    def success_rate(self) -> float:
        total = self.successful_invocations + self.failed_invocations
        if total == 0:
            return 0.0
        return self.successful_invocations / total
```

### 6. Test Session Management & Persistence

Group multiple tests into logical sessions with full audit trail:

```python
from dataclasses import dataclass, field
from pathlib import Path
import json
import csv

@dataclass
class TestSession:
    """Represents a collection of related tests."""

    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    baseline_model: str = 'claude-baseline'
    docstratum_model: str = 'claude-docstratum'
    llms_source_path: str = ''
    results: list[ABTestResult] = field(default_factory=list)
    environment: dict = field(default_factory=dict)
    notes: str = ''

    @property
    def duration_ms(self) -> float:
        """Total session duration."""
        end = self.end_time or datetime.utcnow()
        return (end - self.start_time).total_seconds() * 1000

    @property
    def test_count(self) -> int:
        return len(self.results)

    @property
    def success_rate(self) -> float:
        if not self.results:
            return 0.0
        successful = sum(1 for r in self.results if r.both_successful)
        return successful / len(self.results)

    def to_dict(self) -> dict:
        return {
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'baseline_model': self.baseline_model,
            'docstratum_model': self.docstratum_model,
            'llms_source_path': self.llms_source_path,
            'environment': self.environment,
            'notes': self.notes,
            'results': [r.to_dict() for r in self.results],
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'TestSession':
        session = cls(
            session_id=data['session_id'],
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else None,
            baseline_model=data.get('baseline_model', 'claude-baseline'),
            docstratum_model=data.get('docstratum_model', 'claude-docstratum'),
            llms_source_path=data.get('llms_source_path', ''),
            environment=data.get('environment', {}),
            notes=data.get('notes', ''),
        )
        session.results = [ABTestResult.from_dict(r) for r in data.get('results', [])]
        return session

class ResultPersistence:
    """Handle persistence of results to disk."""

    def __init__(self, results_dir: Path = Path('./results')):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True, parents=True)
        self.sessions_file = self.results_dir / 'sessions.json'

    def save_result(self, result: ABTestResult) -> Path:
        """Save single test result to JSON."""
        filename = f'{result.session_id}__{result.timestamp.isoformat()}.json'
        filepath = self.results_dir / filename

        with open(filepath, 'w') as f:
            json.dump(result.to_dict(), f, indent=2)

        return filepath

    def save_session(self, session: TestSession) -> Path:
        """Save complete session."""
        filename = f'session__{session.session_id}.json'
        filepath = self.results_dir / filename

        with open(filepath, 'w') as f:
            json.dump(session.to_dict(), f, indent=2)

        return filepath

    def save_session_csv(self, session: TestSession) -> Path:
        """Export session results to CSV."""
        filename = f'session__{session.session_id}.csv'
        filepath = self.results_dir / filename

        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    'question',
                    'baseline_tokens',
                    'docstratum_tokens',
                    'token_overhead',
                    'baseline_latency_ms',
                    'docstratum_latency_ms',
                    'latency_diff_ms',
                    'response_length_ratio',
                ],
            )
            writer.writeheader()

            for result in session.results:
                writer.writerow({
                    'question': result.question[:80],
                    'baseline_tokens': result.baseline.total_tokens,
                    'docstratum_tokens': result.docstratum.total_tokens,
                    'token_overhead': result.token_overhead,
                    'baseline_latency_ms': f'{result.baseline.latency_ms:.2f}',
                    'docstratum_latency_ms': f'{result.docstratum.latency_ms:.2f}',
                    'latency_diff_ms': f'{result.latency_diff_ms:.2f}',
                    'response_length_ratio': f'{result.response_length_ratio:.2f}',
                })

        return filepath

    def load_session(self, session_id: str) -> Optional[TestSession]:
        """Load session from disk."""
        filepath = self.results_dir / f'session__{session_id}.json'

        if not filepath.exists():
            return None

        with open(filepath, 'r') as f:
            data = json.load(f)

        return TestSession.from_dict(data)

    def list_sessions(self) -> list[str]:
        """List all available session IDs."""
        sessions = []
        for filepath in self.results_dir.glob('session__*.json'):
            session_id = filepath.stem.replace('session__', '')
            sessions.append(session_id)
        return sorted(sessions)
```

## Deliverables

1. **AgentResponse dataclass** (120 lines)
   - All fields with type hints
   - Computed properties (total_tokens, tokens_per_ms, success)
   - Serialization methods (to_dict, from_dict)
   - ISO 8601 timestamp handling
   - Error field for failure tracking

2. **ABTestResult dataclass** (140 lines)
   - Baseline and DocStratum AgentResponse fields
   - Context tokens and session tracking
   - Computed properties (token_overhead, latency_diff_ms, response_length_ratio)
   - Serialization with nested AgentResponse support

3. **TestExecutionEngine class** (250 lines)
   - `invoke_agent()` with timing and token capture
   - `run_test()` with sequential execution and cache-reset window
   - `run_test_concurrent()` using asyncio.gather()
   - Retry logic with configurable backoff
   - Execution statistics tracking

4. **TestSession dataclass** (80 lines)
   - Session metadata and lifecycle
   - Results collection
   - Computed properties (duration_ms, test_count, success_rate)
   - Serialization support

5. **ResultPersistence class** (160 lines)
   - JSON persistence for individual results and sessions
   - CSV export for analysis
   - Session loading and listing
   - Directory management

6. **ExecutionStats and RetryPolicy classes** (100 lines)
   - Configurable retry behavior
   - Execution monitoring
   - Error tracking by type

## Acceptance Criteria

- [ ] AgentResponse captures all timing/token data with ±10ms precision
- [ ] ABTestResult computed properties match expected formulas
- [ ] Sequential execution runs baseline, waits 100ms, runs docstratum
- [ ] Concurrent mode completes in ~50% less time (3 questions: <4s vs >6s)
- [ ] Retry logic implements exponential backoff (100ms, 200ms, 400ms)
- [ ] All results persist to JSON/CSV without data loss
- [ ] Sessions load correctly from disk with full history
- [ ] Error cases (timeout, API failure) return AgentResponse with error field set
- [ ] Execution stats track retry counts and error types accurately
- [ ] Results remain consistent across sequential runs (deterministic for fixed inputs)

## Next Step

→ Proceed to **v0.3.5b — Test Question Design & Suite Management** to define the question bank, categories, and suite configuration system.
