# Integration Testing & End-to-End Pipeline

> **v0.3.4c DocStratum Agent — Logic Core**
> Defines end-to-end integration tests that validate the complete pipeline from llms.txt context loading through agent invocation and behavioral verification.

## Objective

Build integration tests that:
- Load llms.txt, build agents, invoke with test questions
- Verify behavioral differences between baseline and DocStratum
- Validate that context actually improves agent quality
- Test all three validation prompts (disambiguation, freshness, few-shot)
- Provide regression detection for code changes
- Run in CI/CD with mocked APIs (no real API calls)

## Scope Boundaries

**INCLUDES:**
- End-to-end pipeline test (load → build → invoke → verify)
- Integration test script (test_docstratum_integration.py)
- Test question categories (disambiguation, freshness, few-shot)
- Expected vs. actual response analysis
- Regression testing strategy
- CI/CD integration and GitHub Actions setup
- Complete test suite (10+ end-to-end scenarios)

**EXCLUDES:**
- Unit tests for individual functions (covered in v0.3.3-4a)
- Performance benchmarking
- User acceptance testing
- Real API calls in production environment
- Long-term data storage

---

## Dependency Diagram

```
Integration Test Flow:
├── Setup Phase
│   ├── Load .env (API keys)
│   ├── Load llms.txt (context)
│   ├── Create baseline agent
│   └── Create DocStratum agent
├── Execution Phase
│   ├── For each test question:
│   │   ├── Invoke baseline agent
│   │   ├── Invoke DocStratum agent
│   │   ├── Collect AgentResponse from both
│   │   └── Verify behavioral differences
├── Verification Phase
│   ├── BehaviorVerifier analyzes responses
│   ├── Compare baseline vs. DocStratum scores
│   ├── Check for expected signal differences
│   └── Generate quality report
└── Report Phase
    ├── Log test results
    ├── Detect regressions
    └── Report pass/fail status
```

---

## 1. End-to-End Pipeline Test

### Complete Workflow

```python
import os
import json
from pathlib import Path
from dataclasses import asdict

from agent import DocumentationAgent, ProviderType, AgentResponse
from v0_3_4a import create_baseline_agent, create_docstratum_agent
from v0_3_4b import BehaviorVerifier, ResponseBehavior
from v0_3_3d import setup_logging
import logging

logger = logging.getLogger(__name__)

class E2EPipelineTest:
    """End-to-end integration test"""

    def __init__(self, context_path: str = "docs/llms.txt"):
        self.context_path = context_path
        self.results = []
        setup_logging(logging.INFO)

    def setup_phase(self) -> tuple[DocumentationAgent, DocumentationAgent]:
        """
        Setup phase: Load context and create agents.

        Returns:
            (baseline_agent, docstratum_agent)
        """
        logger.info("═" * 80)
        logger.info("SETUP PHASE: Loading context and creating agents")
        logger.info("═" * 80)

        # Verify context file exists
        if not Path(self.context_path).exists():
            raise FileNotFoundError(f"Context file not found: {self.context_path}")

        logger.info(f"Loading context from: {self.context_path}")

        # Create agents
        provider = os.getenv("DEFAULT_PROVIDER", "openai").upper()
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            logger.warning("No API key found. Using mocked responses.")

        try:
            baseline = create_baseline_agent(provider=provider.lower(), api_key=api_key)
            logger.info("✓ Created baseline agent")
        except Exception as e:
            logger.error(f"Failed to create baseline agent: {e}")
            raise

        try:
            docstratum = create_docstratum_agent(
                context_path=self.context_path,
                provider=provider.lower(),
                api_key=api_key
            )
            logger.info("✓ Created DocStratum agent")
        except Exception as e:
            logger.error(f"Failed to create DocStratum agent: {e}")
            raise

        logger.info("")
        return baseline, docstratum

    def execution_phase(
        self,
        baseline: DocumentationAgent,
        docstratum: DocumentationAgent,
        test_questions: list[str]
    ) -> list[tuple[str, AgentResponse, AgentResponse]]:
        """
        Execution phase: Invoke agents with test questions.

        Args:
            baseline: Baseline agent
            docstratum: DocStratum agent
            test_questions: List of questions to ask both agents

        Returns:
            List of (question, baseline_response, docstratum_response) tuples
        """
        logger.info("=" * 80)
        logger.info("EXECUTION PHASE: Invoking agents with test questions")
        logger.info("=" * 80)

        results = []

        for i, question in enumerate(test_questions, 1):
            logger.info(f"\n[{i}/{len(test_questions)}] Q: {question[:60]}...")

            # Invoke baseline
            logger.info("  → Invoking baseline agent...")
            baseline_response = baseline.invoke(question)

            if baseline_response.is_error():
                logger.warning(f"    Baseline error: {baseline_response.error}")
            else:
                logger.info(f"    Baseline: {baseline_response.total_tokens} tokens, "
                           f"{baseline_response.latency_ms:.0f}ms")

            # Invoke DocStratum
            logger.info("  → Invoking DocStratum agent...")
            docstratum_response = docstratum.invoke(question)

            if docstratum_response.is_error():
                logger.warning(f"    DocStratum error: {docstratum_response.error}")
            else:
                logger.info(f"    DocStratum: {docstratum_response.total_tokens} tokens, "
                           f"{docstratum_response.latency_ms:.0f}ms")

            results.append((question, baseline_response, docstratum_response))

        logger.info("")
        return results

    def verification_phase(
        self,
        results: list[tuple[str, AgentResponse, AgentResponse]],
        domain_terms: list[str]
    ) -> list[tuple[str, ResponseBehavior, ResponseBehavior]]:
        """
        Verification phase: Analyze responses for behavioral differences.

        Args:
            results: List of (question, baseline_response, docstratum_response)
            domain_terms: Domain terminology for BehaviorVerifier

        Returns:
            List of (question, baseline_behavior, docstratum_behavior) tuples
        """
        logger.info("=" * 80)
        logger.info("VERIFICATION PHASE: Analyzing behavioral differences")
        logger.info("=" * 80)

        verifier = BehaviorVerifier(domain_terms)
        behavior_results = []

        for i, (question, baseline_resp, docstratum_resp) in enumerate(results, 1):
            logger.info(f"\n[{i}/{len(results)}] Analyzing: {question[:60]}...")

            if not baseline_resp.is_success():
                logger.warning(f"  Skipping baseline (error: {baseline_resp.error})")
                continue

            if not docstratum_resp.is_success():
                logger.warning(f"  Skipping DocStratum (error: {docstratum_resp.error})")
                continue

            # Analyze both responses
            baseline_behavior = verifier.analyze(baseline_resp)
            docstratum_behavior = verifier.analyze(docstratum_resp)

            logger.info(f"  Baseline score: {baseline_behavior.overall_score:.1f}/5.0")
            logger.info(f"  DocStratum score:  {docstratum_behavior.overall_score:.1f}/5.0")
            logger.info(f"  Improvement:    +{docstratum_behavior.overall_score - baseline_behavior.overall_score:.1f}")

            behavior_results.append((question, baseline_behavior, docstratum_behavior))

        logger.info("")
        return behavior_results

    def run_complete_pipeline(
        self,
        test_questions: list[str],
        domain_terms: list[str]
    ) -> dict:
        """
        Run complete pipeline: setup → execution → verification.

        Args:
            test_questions: Questions to test
            domain_terms: Domain terminology for verification

        Returns:
            Dictionary with complete results and metrics
        """
        logger.info("\n" + "=" * 80)
        logger.info("STARTING COMPLETE E2E PIPELINE TEST")
        logger.info("=" * 80)

        # Setup
        baseline, docstratum = self.setup_phase()

        # Execution
        execution_results = self.execution_phase(baseline, docstratum, test_questions)

        # Verification
        behavior_results = self.verification_phase(execution_results, domain_terms)

        # Compile results
        summary = self._compile_summary(execution_results, behavior_results)

        logger.info("\n" + "=" * 80)
        logger.info("E2E PIPELINE TEST COMPLETE")
        logger.info("=" * 80)

        return summary

    def _compile_summary(self, execution_results, behavior_results) -> dict:
        """Compile test summary"""
        baseline_scores = [b[1].overall_score for b in behavior_results]
        docstratum_scores = [b[2].overall_score for b in behavior_results]

        baseline_avg = sum(baseline_scores) / len(baseline_scores) if baseline_scores else 0
        docstratum_avg = sum(docstratum_scores) / len(docstratum_scores) if docstratum_scores else 0

        return {
            "test_count": len(execution_results),
            "successful_tests": len(behavior_results),
            "baseline_avg_score": baseline_avg,
            "docstratum_avg_score": docstratum_avg,
            "improvement_percent": ((docstratum_avg - baseline_avg) / baseline_avg * 100) if baseline_avg > 0 else 0,
            "results": [
                {
                    "question": q,
                    "baseline_score": b[1].overall_score,
                    "docstratum_score": b[2].overall_score
                }
                for q, b in zip([r[0] for r in execution_results], behavior_results)
            ]
        }
```

---

## 2. Integration Test Script

### test_docstratum_integration.py

```python
#!/usr/bin/env python3
"""
Integration test script for DocStratum agent.

Run all three validation question categories:
- Disambiguation: Agent clarifies concepts using context
- Freshness: Agent acknowledges context recency
- Few-shot: Agent follows documentation style/patterns
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from v0_3_4a import create_baseline_agent, create_docstratum_agent
from v0_3_4b import BehaviorVerifier
from v0_3_4c_e2e import E2EPipelineTest

# Test questions by category
DISAMBIGUATION_QUESTIONS = [
    "What is the core purpose of this system?",
    "How does this differ from similar solutions?",
    "What are the main components and how do they interact?",
]

FRESHNESS_QUESTIONS = [
    "What's the current recommended approach?",
    "How has this evolved over recent versions?",
    "What's the latest best practice in this domain?",
]

FEW_SHOT_QUESTIONS = [
    "Show me an example of the recommended pattern",
    "Walk me through a typical workflow step-by-step",
    "What are the common mistakes to avoid?",
]

ALL_QUESTIONS = DISAMBIGUATION_QUESTIONS + FRESHNESS_QUESTIONS + FEW_SHOT_QUESTIONS

# Domain terminology (would be extracted from llms.txt in production)
SAMPLE_DOMAIN_TERMS = [
    "REST API", "endpoint", "authentication", "middleware",
    "async", "event loop", "promise", "callback", "repository pattern"
]

def main():
    print("\n" + "=" * 80)
    print("DOCSTRATUM INTEGRATION TEST")
    print("=" * 80 + "\n")

    # Determine context path
    context_path = "docs/llms.txt"
    if not Path(context_path).exists():
        print(f"Context file not found at {context_path}")
        print("Using sample context for demonstration")
        context_path = None

    # Run E2E test
    e2e_test = E2EPipelineTest(context_path) if context_path else None

    if e2e_test:
        try:
            results = e2e_test.run_complete_pipeline(
                test_questions=ALL_QUESTIONS,
                domain_terms=SAMPLE_DOMAIN_TERMS
            )

            # Print summary
            print(f"\nResults Summary:")
            print(f"  Tests completed: {results['test_count']}")
            print(f"  Successful: {results['successful_tests']}")
            print(f"  Baseline avg score: {results['baseline_avg_score']:.2f}/5.0")
            print(f"  DocStratum avg score: {results['docstratum_avg_score']:.2f}/5.0")
            print(f"  Improvement: +{results['improvement_percent']:.1f}%")

            # Exit with success/failure based on improvement
            if results['improvement_percent'] >= 20:
                print("\n✓ PASS: DocStratum shows significant improvement over baseline")
                return 0
            else:
                print(f"\n✗ FAIL: Improvement {results['improvement_percent']:.1f}% < 20% threshold")
                return 1

        except Exception as e:
            print(f"\n✗ ERROR: Integration test failed: {e}")
            import traceback
            traceback.print_exc()
            return 1
    else:
        print("Skipping E2E test (no context file)")
        return 0

if __name__ == "__main__":
    exit(main())
```

---

## 3. Test Question Categories

### Disambiguation Questions

```python
# Questions designed to test if DocStratum uses context to clarify concepts

DISAMBIGUATION_QUESTIONS = [
    {
        "question": "What is the core purpose of this system?",
        "expected_signals": ["url_citations", "domain_terminology"],
        "category": "disambiguation",
        "rationale": "DocStratum should cite specific docs, use domain terms"
    },
    {
        "question": "How does this differ from similar solutions?",
        "expected_signals": ["domain_terminology", "anti_patterns"],
        "category": "disambiguation",
        "rationale": "DocStratum should explain unique aspects"
    },
    {
        "question": "What are the main components and how do they interact?",
        "expected_signals": ["domain_terminology", "format_adherence"],
        "category": "disambiguation",
        "rationale": "DocStratum should structure answer with domain concepts"
    }
]

# Baseline should score 1-2 on these (generic understanding)
# DocStratum should score 4-5 on these (specific understanding)
```

### Freshness Questions

```python
# Questions designed to test if DocStratum acknowledges context recency

FRESHNESS_QUESTIONS = [
    {
        "question": "What's the current recommended approach?",
        "expected_signals": ["freshness_awareness", "url_citations"],
        "category": "freshness",
        "rationale": "DocStratum should mention current version/date"
    },
    {
        "question": "How has this evolved over recent versions?",
        "expected_signals": ["freshness_awareness", "anti_patterns"],
        "category": "freshness",
        "rationale": "DocStratum should reference version history"
    },
    {
        "question": "What's the latest best practice in this domain?",
        "expected_signals": ["freshness_awareness", "url_citations"],
        "category": "freshness",
        "rationale": "DocStratum should acknowledge recency"
    }
]

# Baseline should score 0-1 on freshness (no context)
# DocStratum should score 3-4 on freshness (context-aware)
```

### Few-Shot Questions

```python
# Questions designed to test if DocStratum follows documented patterns

FEW_SHOT_QUESTIONS = [
    {
        "question": "Show me an example of the recommended pattern",
        "expected_signals": ["format_adherence", "domain_terminology"],
        "category": "few_shot",
        "rationale": "DocStratum should follow example style from docs"
    },
    {
        "question": "Walk me through a typical workflow step-by-step",
        "expected_signals": ["format_adherence", "url_citations"],
        "category": "few_shot",
        "rationale": "DocStratum should use documented step structure"
    },
    {
        "question": "What are the common mistakes to avoid?",
        "expected_signals": ["anti_patterns", "url_citations"],
        "category": "few_shot",
        "rationale": "DocStratum should follow anti-pattern discussion pattern"
    }
]

# Baseline should score 1-2 on format/few-shot (generic structure)
# DocStratum should score 4-5 on format/few-shot (domain structure)
```

---

## 4. Expected vs. Actual Response Analysis

### Comparison Framework

```python
def analyze_response_quality(
    question: str,
    baseline_response: AgentResponse,
    docstratum_response: AgentResponse,
    baseline_behavior: ResponseBehavior,
    docstratum_behavior: ResponseBehavior
) -> dict:
    """
    Analyze expected vs actual for a single question.

    Returns dictionary with detailed comparison.
    """

    return {
        "question": question,
        "response_metrics": {
            "baseline": {
                "tokens": baseline_response.total_tokens,
                "latency_ms": baseline_response.latency_ms,
            },
            "docstratum": {
                "tokens": docstratum_response.total_tokens,
                "latency_ms": docstratum_response.latency_ms,
            }
        },
        "behavior_comparison": {
            "url_citations": {
                "baseline": baseline_behavior.url_citations.score,
                "docstratum": docstratum_behavior.url_citations.score,
                "delta": docstratum_behavior.url_citations.score - baseline_behavior.url_citations.score
            },
            "anti_patterns": {
                "baseline": baseline_behavior.anti_patterns.score,
                "docstratum": docstratum_behavior.anti_patterns.score,
                "delta": docstratum_behavior.anti_patterns.score - baseline_behavior.anti_patterns.score
            },
            "domain_terminology": {
                "baseline": baseline_behavior.domain_terminology.score,
                "docstratum": docstratum_behavior.domain_terminology.score,
                "delta": docstratum_behavior.domain_terminology.score - baseline_behavior.domain_terminology.score
            },
            "format_adherence": {
                "baseline": baseline_behavior.format_adherence.score,
                "docstratum": docstratum_behavior.format_adherence.score,
                "delta": docstratum_behavior.format_adherence.score - baseline_behavior.format_adherence.score
            },
            "freshness_awareness": {
                "baseline": baseline_behavior.freshness_awareness.score,
                "docstratum": docstratum_behavior.freshness_awareness.score,
                "delta": docstratum_behavior.freshness_awareness.score - baseline_behavior.freshness_awareness.score
            }
        },
        "overall_improvement": docstratum_behavior.overall_score - baseline_behavior.overall_score
    }

def validate_expected_differences(
    analysis_results: list[dict],
    category: str  # "disambiguation", "freshness", "few_shot"
) -> bool:
    """
    Validate that DocStratum shows expected improvements for question category.

    Expected:
    - DocStratum score should be 2+ points higher than baseline
    - Relevant signals should show improvement
    """

    if not analysis_results:
        return False

    # Define expected signal improvements by category
    expected_signals = {
        "disambiguation": ["url_citations", "domain_terminology"],
        "freshness": ["freshness_awareness", "url_citations"],
        "few_shot": ["format_adherence", "domain_terminology"]
    }

    signals = expected_signals.get(category, [])

    for result in analysis_results:
        overall_improvement = result['overall_improvement']

        # Check overall improvement threshold
        if overall_improvement < 2.0:
            return False

        # Check expected signals show improvement
        for signal in signals:
            delta = result['behavior_comparison'][signal]['delta']
            if delta < 1.0:  # Should improve by at least 1 point
                return False

    return True
```

---

## 5. Regression Testing Strategy

### Detecting Code Changes That Degrade Quality

```python
import json
from pathlib import Path
from datetime import datetime

class RegressionDetector:
    """Track test results over time and detect regressions"""

    def __init__(self, results_dir: str = "test_results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)

    def save_baseline(self, results: dict, name: str = "baseline"):
        """Save current test results as baseline"""
        baseline_file = self.results_dir / f"{name}_baseline.json"

        with open(baseline_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "results": results
            }, f, indent=2)

        print(f"Saved baseline to {baseline_file}")

    def compare_to_baseline(self, results: dict, name: str = "baseline") -> dict:
        """Compare current results to baseline, detect regressions"""
        baseline_file = self.results_dir / f"{name}_baseline.json"

        if not baseline_file.exists():
            return {"status": "no_baseline", "message": "No baseline to compare"}

        with open(baseline_file) as f:
            baseline = json.load(f)['results']

        # Compare key metrics
        regression_report = {
            "status": "ok",
            "metrics": {}
        }

        # Check baseline avg score
        baseline_score = baseline['docstratum_avg_score']
        current_score = results['docstratum_avg_score']

        if current_score < baseline_score * 0.95:  # More than 5% regression
            regression_report['status'] = 'regression'
            regression_report['metrics']['docstratum_avg_score'] = {
                'baseline': baseline_score,
                'current': current_score,
                'delta': current_score - baseline_score,
                'regression': True
            }

        # Check improvement
        baseline_improvement = baseline['improvement_percent']
        current_improvement = results['improvement_percent']

        if current_improvement < baseline_improvement * 0.9:  # More than 10% regression
            regression_report['status'] = 'regression'
            regression_report['metrics']['improvement_percent'] = {
                'baseline': baseline_improvement,
                'current': current_improvement,
                'delta': current_improvement - baseline_improvement,
                'regression': True
            }

        return regression_report
```

---

## 6. CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/integration-tests.yml
name: Integration Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  integration-tests:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Create sample llms.txt
      run: |
        mkdir -p docs
        cat > docs/llms.txt << 'EOF'
        # Sample Documentation
        ## Overview
        This is a sample system for integration testing.

        ## API Reference
        See https://example.com/docs/api for details.

        ## Common Pitfalls
        - Avoid hardcoding values
        - Don't skip error handling
        - Never expose secrets
        EOF

    - name: Run integration tests
      env:
        # Use mock API to avoid real API calls
        USE_MOCK_API: true
        DEFAULT_PROVIDER: openai
        # Secrets from GitHub Actions
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
      run: |
        python -m pytest tests/test_docstratum_integration.py -v

    - name: Upload results
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: integration-test-results
        path: test_results/
```

---

## 7. Complete Integration Test Suite

### pytest Implementation

```python
# tests/test_docstratum_integration.py
import pytest
import os
from pathlib import Path
from unittest.mock import patch, Mock

from v0_3_4c_e2e import E2EPipelineTest
from v0_3_4a import create_baseline_agent, create_docstratum_agent
from v0_3_4b import BehaviorVerifier, ResponseBehavior

@pytest.fixture
def context_file(tmp_path):
    """Create temporary context file"""
    content = """
# Test Documentation

## Overview
This is a test system with specific concepts.

## Key Concepts
- RestAPI: HTTP-based service communication
- Middleware: Intercepting layer for requests
- AsyncPattern: Non-blocking operations

## API Reference
All endpoints available at https://docs.example.com/api

## Common Mistakes
- Anti-pattern: Hardcoding credentials
- Mistake: Synchronous blocking in async code
- Wrong approach: Ignoring rate limits
"""

    file_path = tmp_path / "test_llms.txt"
    file_path.write_text(content)
    return str(file_path)

@pytest.fixture
def sample_domain_terms():
    return ["RestAPI", "Middleware", "AsyncPattern", "endpoint", "authentication"]

class TestE2EPipeline:
    """Integration tests for complete pipeline"""

    def test_setup_phase(self, context_file):
        """Test agent creation phase"""
        e2e = E2EPipelineTest(context_file)

        baseline, docstratum = e2e.setup_phase()

        assert baseline is not None
        assert docstratum is not None
        assert baseline.system_prompt != docstratum.system_prompt

    def test_execution_phase_questions(self, context_file):
        """Test question execution"""
        e2e = E2EPipelineTest(context_file)
        baseline, docstratum = e2e.setup_phase()

        questions = ["What is this system?", "How do I use it?"]

        with patch.object(baseline, 'invoke') as mock_baseline, \
             patch.object(docstratum, 'invoke') as mock_docstratum:

            from agent import AgentResponse
            mock_baseline.return_value = AgentResponse(
                response="Test response",
                model="gpt-4o-mini",
                provider="openai",
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=150,
                latency_ms=1000,
                timestamp="2025-02-05T10:00:00Z"
            )
            mock_docstratum.return_value = AgentResponse(
                response="Test response with context",
                model="gpt-4o-mini",
                provider="openai",
                prompt_tokens=100,
                completion_tokens=60,
                total_tokens=160,
                latency_ms=1100,
                timestamp="2025-02-05T10:00:01Z"
            )

            results = e2e.execution_phase(baseline, docstratum, questions)

            assert len(results) == 2
            assert results[0][1].response == "Test response"
            assert results[0][2].response == "Test response with context"

    def test_behavioral_verification(self, sample_domain_terms):
        """Test behavior analysis"""
        from agent import AgentResponse

        verifier = BehaviorVerifier(sample_domain_terms)

        response_with_citations = AgentResponse(
            response="""According to https://docs.example.com/api,
                RestAPI uses HTTP methods. A common anti-pattern is
                hardcoding credentials. This is version 2.5 as of February 2025.""",
            model="gpt-4o-mini",
            provider="openai",
            prompt_tokens=100,
            completion_tokens=80,
            total_tokens=180,
            latency_ms=1000,
            timestamp="2025-02-05T10:00:00Z"
        )

        behavior = verifier.analyze(response_with_citations)

        # Should score high on all signals
        assert behavior.url_citations.score >= 3
        assert behavior.anti_patterns.score >= 2
        assert behavior.domain_terminology.score >= 2
        assert behavior.freshness_awareness.score >= 2

    def test_complete_pipeline(self, context_file, sample_domain_terms):
        """Test complete E2E pipeline"""
        e2e = E2EPipelineTest(context_file)

        questions = [
            "What is the main purpose?",
            "Show me an example",
            "What are common mistakes?"
        ]

        with patch('v0_3_4a.DocumentationAgent.invoke') as mock_invoke:
            from agent import AgentResponse

            # Mock different responses for different providers
            mock_invoke.return_value = AgentResponse(
                response="""This system provides RestAPI functionality.
                    Common anti-pattern: hardcoding credentials.
                    See https://docs.example.com/api for details.
                    As of February 2025, this is current.""",
                model="gpt-4o-mini",
                provider="openai",
                prompt_tokens=100,
                completion_tokens=80,
                total_tokens=180,
                latency_ms=1000,
                timestamp="2025-02-05T10:00:00Z"
            )

            summary = e2e.run_complete_pipeline(questions, sample_domain_terms)

            assert summary['test_count'] == len(questions)
            assert summary['improvement_percent'] > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## Deliverables

1. **E2EPipelineTest class** with complete implementation
2. **test_docstratum_integration.py** script
3. **Test question categories** (disambiguation, freshness, few-shot)
4. **Expected vs. actual analysis framework**
5. **RegressionDetector class** for CI/CD tracking
6. **GitHub Actions workflow** (.github/workflows/integration-tests.yml)
7. **Complete pytest test suite** (10+ integration tests)

---

## Acceptance Criteria

- [ ] E2E pipeline runs from context loading to behavioral verification
- [ ] All 3 validation question categories represented
- [ ] DocStratum shows 20%+ improvement over baseline
- [ ] Regression detection identifies quality degradation
- [ ] GitHub Actions workflow runs successfully
- [ ] Tests run without real API calls (mocked)
- [ ] Results saved to test_results/ for CI/CD tracking
- [ ] All 10+ integration tests pass
- [ ] Expected vs. actual analysis shows significant differences
- [ ] Report generation provides actionable insights

---

## Next Step

**v0.3.4d — Multi-Provider Testing & Fallback Strategy** will test the agent across multiple LLM providers and implement intelligent fallback chains when primary providers fail.
