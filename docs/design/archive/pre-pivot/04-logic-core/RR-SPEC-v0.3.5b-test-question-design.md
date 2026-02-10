# v0.3.5b — Test Question Design & Suite Management

> A comprehensive question bank covering all validation categories, with suite configuration for flexible test composition.

## Objective

Design a diverse, principled set of test questions that:
- Validate DocStratum's ability to handle varied intent types and reasoning tasks
- Cover difficulty ranges (easy, medium, hard)
- Ensure questions are answerable from llms.txt content
- Support parameterized pytest testing
- Enable category-based test suite composition

## Scope Boundaries

- **In scope**: Test question design principles, 6+ question categories, expanded DEFAULT_QUESTIONS (3→20), question bank YAML, suite configuration, pytest parametrization
- **Out of scope**: Statistical significance testing (v0.3.5c), report generation (v0.3.5d), interactive question creation, dynamic question generation
- **Constraints**: All questions must be answerable from llms.txt; suite must support filtering by category/difficulty; YAML format for maintainability

## Dependency Diagram

```
┌──────────────────────────────────────────────────┐
│         question_bank.yaml                       │
│  (source of truth: 20+ questions with metadata)  │
└──────────────────┬───────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────┐
│       QuestionBank (loader + filter)             │
│  • load_yaml() → list[Question]                  │
│  • filter_by_category() → list[Question]         │
│  • filter_by_difficulty() → list[Question]       │
│  • random_sample() → list[Question]              │
└──────────────────┬───────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────┐
│       TestSuite (composition & execution)        │
│  • add_question(q) / add_suite(name)            │
│  • questions: list[Question]                    │
│  • run_suite() → list[ABTestResult]             │
└──────────────────┬───────────────────────────────┘
                   │
        ┌──────────▴──────────┐
        │                     │
   pytest.mark.             ABTestHarness
   parametrize              (executor)
```

## Content Sections

### 1. Test Question Design Principles

Effective A/B test questions follow these principles:

| Principle | Rationale | Example |
|-----------|-----------|---------|
| **Answerable from llms.txt** | Ensures fair comparison; both agents have access to context | "What is the DocStratum project's core mission?" |
| **Varied intent types** | Tests different reasoning patterns (recall, inference, synthesis) | Factual recall + multi-concept reasoning + error handling |
| **Difficulty range** | Easy questions ensure baseline success; hard questions reveal capability gaps | E2E format question (easy) vs ambiguous instruction (hard) |
| **Clear ground truth** | Metrics depend on having objective correctness reference | Questions with factual answers vs open-ended questions |
| **No leading language** | Avoid hints that could bias one agent's response | "How does DocStratum differ from the baseline?" → "Compare DocStratum and baseline" |
| **Realistic use cases** | Questions reflect actual user tasks in the domain | Documentation lookup, implementation guidance, decision support |
| **Length variation** | Short questions test precision; long questions test comprehension | 1-liner vs 3-paragraph scenario |

**Design Anti-patterns:**
- ❌ Questions with built-in answers: "DocStratum is better at X, which makes it superior, right?"
- ❌ Ambiguous ground truth: "Is this code elegant?" (subjective)
- ❌ Questions requiring real-time info: "What's the latest Claude model?" (changes frequently)
- ❌ Questions outside context: "What's the capital of France?" (not in llms.txt)

### 2. Question Categories (6-7 Types)

A comprehensive test suite covers these categories:

#### Category A: Disambiguation (Intent Clarification)

**Purpose:** Test ability to handle ambiguous requests and ask clarifying questions or infer intent.

| Difficulty | Question | Expected Behavior |
|---|---|---|
| Easy | "What is DocStratum?" | Both should identify core project name |
| Medium | "How do I measure success?" (in context of DocStratum) | Should infer "measuring DocStratum adoption/quality" |
| Hard | "Should we use it?" | Should clarify "for what purpose?" and enumerate tradeoffs |

#### Category B: Freshness / Context Awareness

**Purpose:** Verify agents understand current state of llms.txt (dates, versions, phases).

| Difficulty | Question | Expected Behavior |
|---|---|---|
| Easy | "What version of DocStratum is described in this document?" | Direct recall: "v0.3.5" |
| Medium | "Which phase comes after v0.3.5?" | Scan structure, identify next phase logically |
| Hard | "What constraints should v0.4.x address based on v0.3.5 limitations?" | Infer from context |

#### Category C: Few-Shot Adherence

**Purpose:** Test ability to follow patterns and structured examples in llms.txt.

| Difficulty | Question | Expected Behavior |
|---|---|---|
| Easy | "List the 4 core components of v0.3.5" | Extract and format like examples in doc |
| Medium | "Create a test result entry following the ABTestResult pattern" | Follow dataclass structure with correct fields |
| Hard | "Design a new section following the doc's style guide" | Replicate H1+blockquote+objective+scope format |

#### Category D: Factual Recall

**Purpose:** Straight knowledge retrieval from llms.txt.

| Difficulty | Question | Expected Behavior |
|---|---|---|
| Easy | "What does A/B stand for in ABTestHarness?" | Direct: "A = baseline, B = DocStratum" (or similar) |
| Medium | "List all dataclass fields in AgentResponse" | Complete, accurate enumeration |
| Hard | "What is the computed property for token cost calculation?" | Identify correct formula and return type |

#### Category E: Multi-Concept Reasoning

**Purpose:** Require connecting multiple pieces of information.

| Difficulty | Question | Expected Behavior |
|---|---|---|
| Easy | "How are TestSession and ABTestResult related?" | Should identify composition relationship |
| Medium | "Why run the baseline first, then DocStratum?" | Should explain cache-reset window logic |
| Hard | "How would you optimize the test execution engine for 1000 questions?" | Should propose parallelization, batching, caching strategies |

#### Category F: Error Handling & Edge Cases

**Purpose:** Test graceful handling of unusual scenarios.

| Difficulty | Question | Expected Behavior |
|---|---|---|
| Easy | "What happens if an agent times out?" | Should reference retry_count and error field |
| Medium | "How should the harness handle a question that can't be answered?" | Should discuss graceful degradation, error recording |
| Hard | "Design a retry strategy that avoids cache pollution" | Should propose exponential backoff + cache-reset windows |

#### Category G: Anti-Pattern Detection

**Purpose:** Test ability to identify code/design smells.

| Difficulty | Question | Expected Behavior |
|---|---|---|
| Easy | "Is concurrent execution always faster than sequential?" | Should identify tradeoffs: faster but harder to debug |
| Medium | "What would break if we don't record retry_count?" | Should explain loss of debugging information, reproducibility issues |
| Hard | "What are the failure modes of randomized execution order?" | Should discuss statistical bias, flakiness, caching effects |

### 3. Expanded DEFAULT_QUESTIONS (3 → 20)

The original 3 questions are preserved and expanded:

```yaml
# Original 3 (v0.3.5 launch)
- id: q001
  text: "What is the DocStratum project's core mission?"
  category: disambiguation
  difficulty: easy

- id: q002
  text: "List all dataclass fields in AgentResponse and their purposes."
  category: factual_recall
  difficulty: medium

- id: q003
  text: "Why run baseline first before DocStratum? Explain the trade-offs of execution order strategies."
  category: multi_concept_reasoning
  difficulty: hard

# New questions (17 additional)
```

Full 20-question bank defined in Section 4 (YAML format).

### 4. Question Bank YAML Structure & 20-Question Set

**File: `question_bank.yaml`**

```yaml
# DocStratum v0.3.5 Test Question Bank
# Version: 1.0
# Last updated: 2024-01-15
# Maintainer: DocStratum Development Team

metadata:
  version: "1.0"
  total_questions: 20
  categories:
    - disambiguation
    - freshness
    - few_shot_adherence
    - factual_recall
    - multi_concept_reasoning
    - error_handling
    - anti_pattern_detection

questions:

  - id: q001
    text: "What is the DocStratum project's core mission?"
    category: disambiguation
    difficulty: easy
    expected_behavior: "Identify that DocStratum is a Platinum Standard llms.txt architecture"
    ground_truth: "DocStratum is a standards-based architecture for building LLM agents with comprehensive documentation (llms.txt)"
    tags: [core, foundational]

  - id: q002
    text: "List all dataclass fields in AgentResponse and their purposes."
    category: factual_recall
    difficulty: medium
    expected_behavior: "Enumerate response, prompt_tokens, completion_tokens, latency_ms, model, timestamp, error, retry_count"
    ground_truth: "8 fields: response (str), prompt_tokens (int), completion_tokens (int), latency_ms (float), model (str), timestamp (datetime), error (Optional[str]), retry_count (int)"
    tags: [dataclass, structure]

  - id: q003
    text: "Why run baseline first before DocStratum? Explain the trade-offs of execution order strategies."
    category: multi_concept_reasoning
    difficulty: hard
    expected_behavior: "Should discuss cache warming, randomization, sequential-with-reset strategy"
    ground_truth: "Baseline-first is simple but may warm caches (biasing latency). Randomized order reduces bias but complicates async. Sequential-with-reset balances both."
    tags: [execution, bias, methodology]

  - id: q004
    text: "What version of DocStratum is described in this document?"
    category: freshness
    difficulty: easy
    expected_behavior: "Extract version identifier"
    ground_truth: "v0.3.5"
    tags: [metadata, version]

  - id: q005
    text: "What does the 'A' represent in 'ABTestResult'?"
    category: factual_recall
    difficulty: easy
    expected_behavior: "Baseline model"
    ground_truth: "The 'A' represents the baseline model in the A/B test comparison"
    tags: [naming, convention]

  - id: q006
    text: "How are TestSession and ABTestResult related?"
    category: multi_concept_reasoning
    difficulty: medium
    expected_behavior: "Should identify composition: TestSession contains multiple ABTestResult objects"
    ground_truth: "TestSession is a container that groups multiple ABTestResult objects with shared metadata and timeline"
    tags: [relationship, design]

  - id: q007
    text: "What happens if an agent invocation times out?"
    category: error_handling
    difficulty: easy
    expected_behavior: "Should reference retry logic and error recording"
    ground_truth: "The system retries with exponential backoff up to max_attempts, then returns AgentResponse with error field populated"
    tags: [failure-mode, recovery]

  - id: q008
    text: "Explain the purpose of the token_overhead computed property."
    category: factual_recall
    difficulty: medium
    expected_behavior: "Should identify that it measures efficiency difference"
    ground_truth: "token_overhead = docstratum_tokens - baseline_tokens; negative values indicate DocStratum uses fewer tokens (improvement)"
    tags: [metrics, efficiency]

  - id: q009
    text: "Design a retry strategy that avoids cache pollution when running sequential tests."
    category: error_handling
    difficulty: hard
    expected_behavior: "Should propose cache-reset windows or request clearance between invocations"
    ground_truth: "Use asyncio.sleep(100ms) between baseline and docstratum to allow KV cache invalidation; implement cache eviction headers if available"
    tags: [performance, cache-management]

  - id: q010
    text: "What are the three validation categories from the v0.3.5 design?"
    category: factual_recall
    difficulty: medium
    expected_behavior: "Should list: disambiguation, freshness, few-shot adherence"
    ground_truth: "Disambiguation (intent clarification), Freshness (context awareness), Few-Shot Adherence (pattern following)"
    tags: [validation, core-categories]

  - id: q011
    text: "Is concurrent execution always faster than sequential execution? Justify your answer."
    category: anti_pattern_detection
    difficulty: hard
    expected_behavior: "Should identify tradeoffs: faster overall but potential response interference, harder debugging"
    ground_truth: "Not always: concurrent is faster for wall-clock time (~33% speedup for 3 questions) but increases cost, may cause response interference, and complicates debugging"
    tags: [performance, tradeoff]

  - id: q012
    text: "What metrics should an A/B test capture to measure agent performance?"
    category: multi_concept_reasoning
    difficulty: medium
    expected_behavior: "Should list: token counts, latency, response quality, citation accuracy"
    ground_truth: "Per-question metrics: token_overhead, latency_diff_ms, response_length_ratio. Aggregate: mean/median/std, quality score, statistical significance"
    tags: [metrics, evaluation]

  - id: q013
    text: "How would you persist test results to enable historical trend analysis?"
    category: multi_concept_reasoning
    difficulty: medium
    expected_behavior: "Should mention: JSON/CSV formats, session grouping, timestamps"
    ground_truth: "Persist sessions as JSON with full results; export to CSV for analysis; use session_id + timestamp for trend queries across runs"
    tags: [persistence, analysis]

  - id: q014
    text: "What does the retry_count field in AgentResponse track?"
    category: factual_recall
    difficulty: easy
    expected_behavior: "Number of retry attempts before successful response"
    ground_truth: "retry_count records how many attempts were needed; 0 means first attempt succeeded, >0 indicates prior failures"
    tags: [reliability, observability]

  - id: q015
    text: "Describe the relationship between context_tokens in ABTestResult and llms.txt size."
    category: multi_concept_reasoning
    difficulty: hard
    expected_behavior: "Should explain context_tokens represents fixed llms.txt size, allowing token_overhead comparison"
    ground_truth: "context_tokens is constant per session and represents the prompt tokens from llms.txt; token_overhead = (prompt+completion for agent) - baseline; fixed context enables fair comparison"
    tags: [fairness, metrics]

  - id: q016
    text: "What would break if we removed the timestamp field from ABTestResult?"
    category: error_handling
    difficulty: medium
    expected_behavior: "Should identify loss of: temporal ordering, session correlation, trend analysis"
    ground_truth: "Loss of temporal ordering, inability to correlate results within sessions, no trend analysis, breaks causality for debugging"
    tags: [observability, data-integrity]

  - id: q017
    text: "Explain how pytest.mark.parametrize enables question bank testing."
    category: few_shot_adherence
    difficulty: hard
    expected_behavior: "Should describe parametrized test execution across question bank"
    ground_truth: "@pytest.mark.parametrize('question', question_bank) runs test_harness for each question; enables batch testing with individual pass/fail tracking"
    tags: [testing, framework]

  - id: q018
    text: "Design the latency_improvement_pct computed property formula."
    category: factual_recall
    difficulty: medium
    expected_behavior: "Should derive formula: (latency_diff_ms / baseline_latency_ms) * 100"
    ground_truth: "latency_improvement_pct = (docstratum_latency - baseline_latency) / baseline_latency * 100; negative % means faster (improvement)"
    tags: [metrics, calculation]

  - id: q019
    text: "How would you handle a situation where one agent succeeds but the other fails?"
    category: error_handling
    difficulty: medium
    expected_behavior: "Should record both responses; flag in both_successful property; include error in failed response"
    ground_truth: "both_successful property returns False; record success=True for passing agent and success=False for failing agent; use error field to document failure reason"
    tags: [partial-failure, robustness]

  - id: q020
    text: "What are the advantages and disadvantages of randomizing test execution order?"
    category: anti_pattern_detection
    difficulty: hard
    expected_behavior: "Should discuss statistical bias reduction vs repeatability loss vs async complexity"
    ground_truth: "Advantages: eliminates execution-order bias, reduces cache pollution. Disadvantages: non-deterministic results, harder debugging, async complexity increases"
    tags: [methodology, statistics]

# Test suite presets
suites:
  quick_validation:
    description: "Fast 5-question validation suite"
    questions: [q001, q004, q005, q014, q010]
    expected_runtime_ms: 10000

  core_coverage:
    description: "Comprehensive 12-question suite covering all categories"
    questions: [q001, q002, q003, q004, q006, q008, q010, q012, q013, q015, q017, q018]
    expected_runtime_ms: 24000

  full_suite:
    description: "All 20 questions for complete validation"
    questions: [q001, q002, q003, q004, q005, q006, q007, q008, q009, q010, q011, q012, q013, q014, q015, q016, q017, q018, q019, q020]
    expected_runtime_ms: 40000

  difficulty_easy:
    description: "Baseline validation with easy questions only"
    questions: [q001, q004, q005, q007, q014]
    expected_runtime_ms: 10000

  difficulty_medium:
    description: "Standard difficulty questions"
    questions: [q002, q006, q008, q010, q012, q013, q014, q016, q018, q019]
    expected_runtime_ms: 20000

  difficulty_hard:
    description: "Advanced reasoning and design questions"
    questions: [q003, q009, q011, q015, q017, q020]
    expected_runtime_ms: 12000

  category_factual:
    description: "Factual recall only"
    questions: [q002, q005, q008, q010, q014, q018]
    expected_runtime_ms: 12000

  category_reasoning:
    description: "Multi-concept reasoning only"
    questions: [q003, q006, q012, q013, q015]
    expected_runtime_ms: 10000
```

### 5. Test Suite Configuration & Composition

**QuestionBank and TestSuite classes:**

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List
import yaml
import random

@dataclass
class Question:
    """Represents a single test question."""

    id: str
    text: str
    category: str
    difficulty: str  # 'easy', 'medium', 'hard'
    expected_behavior: str
    ground_truth: str
    tags: List[str]

    def __repr__(self) -> str:
        return f"Question(id={self.id}, category={self.category}, difficulty={self.difficulty})"

class QuestionBank:
    """Loads and filters test questions from YAML."""

    def __init__(self, yaml_path: Path):
        self.yaml_path = Path(yaml_path)
        self.questions: dict[str, Question] = {}
        self.suites: dict[str, list[str]] = {}
        self._load_yaml()

    def _load_yaml(self):
        """Load question bank from YAML file."""
        with open(self.yaml_path, 'r') as f:
            data = yaml.safe_load(f)

        # Load individual questions
        for q_data in data.get('questions', []):
            question = Question(
                id=q_data['id'],
                text=q_data['text'],
                category=q_data['category'],
                difficulty=q_data['difficulty'],
                expected_behavior=q_data['expected_behavior'],
                ground_truth=q_data['ground_truth'],
                tags=q_data.get('tags', []),
            )
            self.questions[question.id] = question

        # Load suite definitions
        for suite_name, suite_data in data.get('suites', {}).items():
            self.suites[suite_name] = suite_data['questions']

    def get_question(self, question_id: str) -> Optional[Question]:
        """Retrieve a single question by ID."""
        return self.questions.get(question_id)

    def get_all_questions(self) -> list[Question]:
        """Get all questions in order."""
        return list(self.questions.values())

    def filter_by_category(self, category: str) -> list[Question]:
        """Filter questions by category."""
        return [q for q in self.questions.values() if q.category == category]

    def filter_by_difficulty(self, difficulty: str) -> list[Question]:
        """Filter questions by difficulty level."""
        return [q for q in self.questions.values() if q.difficulty == difficulty]

    def filter_by_tag(self, tag: str) -> list[Question]:
        """Filter questions by tag."""
        return [q for q in self.questions.values() if tag in q.tags]

    def random_sample(self, n: int) -> list[Question]:
        """Return random sample of N questions."""
        return random.sample(list(self.questions.values()), min(n, len(self.questions)))

    def get_suite(self, suite_name: str) -> list[Question]:
        """Get questions for a named suite."""
        question_ids = self.suites.get(suite_name, [])
        return [self.questions[qid] for qid in question_ids if qid in self.questions]

    def list_categories(self) -> set[str]:
        """Get all available categories."""
        return {q.category for q in self.questions.values()}

    def list_difficulties(self) -> set[str]:
        """Get all difficulty levels."""
        return {q.difficulty for q in self.questions.values()}

@dataclass
class TestSuite:
    """Represents a collection of questions to test."""

    name: str
    questions: List[Question]
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    @property
    def count(self) -> int:
        """Number of questions in suite."""
        return len(self.questions)

    @property
    def category_breakdown(self) -> dict[str, int]:
        """Count questions by category."""
        breakdown = {}
        for q in self.questions:
            breakdown[q.category] = breakdown.get(q.category, 0) + 1
        return breakdown

    @property
    def difficulty_breakdown(self) -> dict[str, int]:
        """Count questions by difficulty."""
        breakdown = {}
        for q in self.questions:
            breakdown[q.difficulty] = breakdown.get(q.difficulty, 0) + 1
        return breakdown

    def add_question(self, question: Question):
        """Add a single question."""
        self.questions.append(question)

    def add_questions(self, questions: list[Question]):
        """Add multiple questions."""
        self.questions.extend(questions)

    def remove_question(self, question_id: str):
        """Remove a question by ID."""
        self.questions = [q for q in self.questions if q.id != question_id]

    def to_dict(self) -> dict:
        """Export suite configuration."""
        return {
            'name': self.name,
            'count': self.count,
            'questions': [q.id for q in self.questions],
            'category_breakdown': self.category_breakdown,
            'difficulty_breakdown': self.difficulty_breakdown,
            'metadata': self.metadata,
        }

class SuiteBuilder:
    """Fluent interface for building custom test suites."""

    def __init__(self, question_bank: QuestionBank, name: str = 'custom'):
        self.question_bank = question_bank
        self.name = name
        self.questions: list[Question] = []

    def with_category(self, category: str) -> 'SuiteBuilder':
        """Add all questions in category."""
        self.questions.extend(self.question_bank.filter_by_category(category))
        return self

    def with_difficulty(self, difficulty: str) -> 'SuiteBuilder':
        """Add all questions at difficulty level."""
        self.questions.extend(self.question_bank.filter_by_difficulty(difficulty))
        return self

    def with_tag(self, tag: str) -> 'SuiteBuilder':
        """Add all questions with tag."""
        self.questions.extend(self.question_bank.filter_by_tag(tag))
        return self

    def with_random_sample(self, n: int) -> 'SuiteBuilder':
        """Add N random questions."""
        self.questions.extend(self.question_bank.random_sample(n))
        return self

    def with_suite(self, suite_name: str) -> 'SuiteBuilder':
        """Add pre-defined suite."""
        self.questions.extend(self.question_bank.get_suite(suite_name))
        return self

    def build(self) -> TestSuite:
        """Build the TestSuite."""
        # Remove duplicates while preserving order
        seen = set()
        unique_questions = []
        for q in self.questions:
            if q.id not in seen:
                unique_questions.append(q)
                seen.add(q.id)

        return TestSuite(
            name=self.name,
            questions=unique_questions,
            metadata={'built_with': 'SuiteBuilder'},
        )
```

### 6. Pytest Parametrization & Question Quality Criteria

**Parametrized test execution with pytest:**

```python
import pytest
from pathlib import Path

# Load question bank at test collection time
QUESTION_BANK = QuestionBank(Path('./question_bank.yaml'))

@pytest.fixture
def ab_test_harness():
    """Fixture providing ABTestHarness instance."""
    # Initialize harness with llms_source and models
    return ABTestHarness(
        llms_source=LLMSource('./llms.txt'),
        baseline_model='claude-3-5-sonnet',
        docstratum_model='claude-3-5-sonnet',
    )

@pytest.mark.parametrize(
    'question',
    QUESTION_BANK.get_all_questions(),
    ids=lambda q: q.id,
)
def test_question_answerable(ab_test_harness, question: Question):
    """Test that both agents can answer the question."""
    result = ab_test_harness.run_test(question.text)

    # Basic success criteria
    assert result.both_successful, f"Question {question.id}: One or both agents failed"
    assert len(result.baseline.response) > 0, f"Question {question.id}: Baseline returned empty"
    assert len(result.docstratum.response) > 0, f"Question {question.id}: DocStratum returned empty"

@pytest.mark.parametrize(
    'question',
    QUESTION_BANK.filter_by_difficulty('easy'),
    ids=lambda q: q.id,
)
def test_easy_questions_token_efficient(ab_test_harness, question: Question):
    """Test that easy questions don't consume excessive tokens."""
    result = ab_test_harness.run_test(question.text)

    # Easy questions should use < 500 tokens
    assert result.baseline.total_tokens < 500, f"Question {question.id}: Baseline used too many tokens"
    assert result.docstratum.total_tokens < 500, f"Question {question.id}: DocStratum used too many tokens"

@pytest.fixture(params=['quick_validation', 'core_coverage', 'full_suite'])
def test_suite(request):
    """Run multiple pre-defined suites."""
    suite_name = request.param
    return QUESTION_BANK.get_suite(suite_name)

def test_suite_completeness(ab_test_harness, test_suite: list[Question]):
    """Verify all questions in a suite are answerable."""
    results = ab_test_harness.run_suite(
        [q.text for q in test_suite],
        suite_name='_'.join([q.category for q in test_suite[:3]]),
    )

    success_count = sum(1 for r in results if r.both_successful)
    success_rate = success_count / len(results) if results else 0

    assert success_rate >= 0.95, f"Suite {len(test_suite)}: {success_rate*100:.1f}% success rate"

# Quality assessment helpers
def assess_question_quality(question: Question) -> dict:
    """Assess question quality across multiple dimensions."""

    return {
        'id': question.id,
        'answerable_from_context': len(question.ground_truth) > 20,  # Heuristic
        'has_clear_ground_truth': bool(question.ground_truth),
        'has_expected_behavior': bool(question.expected_behavior),
        'difficulty_reasonable': question.difficulty in ['easy', 'medium', 'hard'],
        'category_valid': question.category in [
            'disambiguation', 'freshness', 'few_shot_adherence',
            'factual_recall', 'multi_concept_reasoning', 'error_handling', 'anti_pattern_detection'
        ],
        'has_tags': len(question.tags) > 0,
    }

def quality_report(question_bank: QuestionBank) -> str:
    """Generate quality report for all questions."""

    report = []
    for q in question_bank.get_all_questions():
        quality = assess_question_quality(q)
        all_pass = all(quality.values())
        status = '✓' if all_pass else '✗'

        report.append(f"{status} {q.id}: {list(quality.values())}")

    return '\n'.join(report)
```

## Deliverables

1. **Question Design Principles document** (150 lines)
   - 6+ design principles with rationale
   - 4+ design anti-patterns
   - Realistic use case guidance

2. **7-Category Question Framework** (100 lines)
   - Disambiguation, Freshness, Few-Shot Adherence, Factual Recall
   - Multi-Concept Reasoning, Error Handling, Anti-Pattern Detection
   - Difficulty examples for each category

3. **20-Question Bank (YAML)** (200 lines)
   - Expanded DEFAULT_QUESTIONS (3 → 20)
   - Full metadata per question (id, text, category, difficulty, expected_behavior, ground_truth, tags)
   - 8+ preset suite configurations (quick_validation, core_coverage, full_suite, by_category, by_difficulty)

4. **QuestionBank class** (180 lines)
   - YAML loading
   - Filtering: by_category(), by_difficulty(), by_tag(), random_sample()
   - Suite retrieval and metadata queries

5. **TestSuite dataclass & SuiteBuilder** (140 lines)
   - Suite composition with metadata
   - Category/difficulty breakdowns
   - Fluent builder interface for custom suite creation

6. **Pytest Parametrization** (80 lines)
   - @pytest.mark.parametrize over question bank
   - Suite-level parametrization
   - Quality assessment helpers

## Acceptance Criteria

- [ ] 20 questions defined with all metadata fields populated
- [ ] Each question is answerable from llms.txt content alone
- [ ] Questions cover all 7 categories with balanced distribution
- [ ] Difficulty ranges from easy to hard with realistic progression
- [ ] Ground truth answers are specific and verifiable
- [ ] All 8 preset suites load and execute without errors
- [ ] Filtering methods return correct subsets (by_category, by_difficulty, by_tag)
- [ ] random_sample() produces deterministic results with seed
- [ ] SuiteBuilder produces suites without duplicate questions
- [ ] Parametrized tests run all questions with proper error reporting
- [ ] Question quality report identifies all well-formed questions
- [ ] YAML file is valid and loads without errors
- [ ] Suite expected_runtime_ms estimates are accurate (±20%)

## Next Step

→ Proceed to **v0.3.5c — Metrics Calculation & Statistical Analysis** to define per-question metrics, aggregate metrics, quality scoring, and statistical significance testing.
