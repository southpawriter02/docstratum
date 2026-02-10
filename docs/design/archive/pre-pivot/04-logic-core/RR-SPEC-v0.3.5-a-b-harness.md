# v0.3.5 — A/B Harness

> **Task:** Build the comparison framework for running side-by-side tests.
> 

---

## Task Overview

---

## Implementation

### File: `core/[testing.py](http://testing.py)`

```python
"""A/B testing harness for comparing agents."""

import logging
import time
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

from schemas import LlmsTxt
from core.loader import load_llms_txt
from core.context import build_context_block
from core.agents import create_baseline_agent, create_docstratum_agent

logger = logging.getLogger(__name__)

@dataclass
class AgentResponse:
    """Response from a single agent."""
    response: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float
    model: str

@dataclass 
class ABTestResult:
    """Result of an A/B comparison test."""
    question: str
    baseline: AgentResponse
    docstratum: AgentResponse
    context_tokens: int
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def token_overhead(self) -> int:
        """Extra tokens used by DocStratum agent."""
        return self.docstratum.prompt_tokens - self.baseline.prompt_tokens
    
    @property
    def latency_diff_ms(self) -> float:
        """Latency difference (positive = DocStratum slower)."""
        return self.docstratum.latency_ms - self.baseline.latency_ms

class ABTestHarness:
    """Harness for running A/B comparison tests."""
    
    def __init__(
        self,
        llms_source: str,
        model: str = "gpt-4o-mini"
    ):
        """Initialize the test harness.
        
        Args:
            llms_source: Path to llms.txt file.
            model: Model to use for both agents.
        """
        self.llms = load_llms_txt(llms_source)
        self.context = build_context_block(self.llms)
        self.context_tokens = len(self.context) // 4  # Estimate
        
        self.baseline_agent = create_baseline_agent(model=model)
        self.docstratum_agent = create_docstratum_agent(self.context, model=model)
        
        self.results: list[ABTestResult] = []
        
        logger.info(f"Initialized A/B harness for {self.llms.site_name}")
    
    def run_test(self, question: str) -> ABTestResult:
        """Run a single A/B test.
        
        Args:
            question: The test question.
            
        Returns:
            ABTestResult with both responses.
        """
        logger.info(f"Running A/B test: {question[:50]}...")
        
        # Baseline
        start = time.perf_counter()
        baseline_raw = self.baseline_agent.invoke(question)
        baseline_latency = (time.perf_counter() - start) * 1000
        
        baseline = AgentResponse(
            response=baseline_raw['response'],
            prompt_tokens=baseline_raw['prompt_tokens'],
            completion_tokens=baseline_raw['completion_tokens'],
            latency_ms=baseline_latency,
            model=baseline_raw['model']
        )
        
        # DocStratum
        start = time.perf_counter()
        docstratum_raw = self.docstratum_agent.invoke(question)
        docstratum_latency = (time.perf_counter() - start) * 1000
        
        docstratum = AgentResponse(
            response=docstratum_raw['response'],
            prompt_tokens=docstratum_raw['prompt_tokens'],
            completion_tokens=docstratum_raw['completion_tokens'],
            latency_ms=docstratum_latency,
            model=docstratum_raw['model']
        )
        
        result = ABTestResult(
            question=question,
            baseline=baseline,
            docstratum=docstratum,
            context_tokens=self.context_tokens
        )
        
        self.results.append(result)
        return result
    
    def run_suite(self, questions: list[str]) -> list[ABTestResult]:
        """Run multiple tests."""
        return [self.run_test(q) for q in questions]
    
    def print_result(self, result: ABTestResult):
        """Pretty-print a single result."""
        print("\n" + "="*70)
        print(f"QUESTION: {result.question}")
        print("="*70)
        
        print("\n❌ BASELINE AGENT:")
        print("-"*35)
        print(result.baseline.response)
        print(f"\n[{result.baseline.prompt_tokens}+{result.baseline.completion_tokens} tokens, {result.baseline.latency_ms:.0f}ms]")
        
        print("\n✅ DOCSTRATUM AGENT:")
        print("-"*35)
        print(result.docstratum.response)
        print(f"\n[{result.docstratum.prompt_tokens}+{result.docstratum.completion_tokens} tokens, {result.docstratum.latency_ms:.0f}ms]")
        
        print("\n📊 COMPARISON:")
        print(f"   Context overhead: +{result.context_tokens} tokens")
        print(f"   Latency diff: {result.latency_diff_ms:+.0f}ms")

def run_ab_test(question: str, llms_source: str) -> ABTestResult:
    """Convenience function for single test."""
    harness = ABTestHarness(llms_source)
    return harness.run_test(question)
```

---

## CLI Runner

### File: `run_ab_[test.py](http://test.py)`

```python
#!/usr/bin/env python
"""CLI for running A/B tests."""

import argparse
from core.testing import ABTestHarness

DEFAULT_QUESTIONS = [
    "Should I use OAuth2 or API keys for my server-side script?",
    "Is the /users/create endpoint still available?",
    "How do I add login to my React app?"
]

def main():
    parser = argparse.ArgumentParser(description='Run A/B tests')
    parser.add_argument('--llms', default='data/llms.txt', help='Path to llms.txt')
    parser.add_argument('--question', '-q', help='Single question to test')
    parser.add_argument('--suite', action='store_true', help='Run default test suite')
    args = parser.parse_args()
    
    harness = ABTestHarness(args.llms)
    
    if args.question:
        result = harness.run_test(args.question)
        harness.print_result(result)
    elif args.suite:
        for q in DEFAULT_QUESTIONS:
            result = harness.run_test(q)
            harness.print_result(result)
    else:
        print("Usage: python run_ab_test.py --question 'Your question here'")
        print("   or: python run_ab_test.py --suite")

if __name__ == '__main__':
    main()
```

---

## Usage

```bash
# Single question
python run_ab_test.py -q "How do I authenticate?"

# Full test suite
python run_ab_test.py --suite
```

---

## 📂 Sub-Part Pages

[v0.3.5a — Test Execution Engine & Data Structures](RR-SPEC-v0.3.5a-test-execution-engine.md) — ABTestResult/AgentResponse dataclasses, execution flow, concurrent option, retry logic, result persistence (JSON/CSV)

[v0.3.5b — Test Question Design & Suite Management](RR-SPEC-v0.3.5b-test-question-design.md) — 7 question categories, 20-question bank (YAML), QuestionBank class, SuiteBuilder, pytest parametrization

[v0.3.5c — Metrics Calculation & Statistical Analysis](RR-SPEC-v0.3.5c-metrics-and-analysis.md) — Per-question metrics, aggregate stats, LLM-as-judge scoring, paired t-test, Wilcoxon test, Cohen's d effect size

[v0.3.5d — CLI Interface & Report Generation](RR-SPEC-v0.3.5d-cli-and-reporting.md) — 4 CLI subcommands, terminal/markdown/HTML reports, JSON/CSV export, GitHub Actions integration, Streamlit data adapter

---

## Acceptance Criteria

- [ ]  `ABTestHarness` runs both agents
- [ ]  Results include token counts and latency
- [ ]  `run_ab_[test.py](http://test.py)` CLI works
- [ ]  Test suite runs all 3 validation questions
- [ ]  Results can be compared side-by-side
- [ ]  **v0.3.5a:** Test results persist to JSON/CSV and can be reloaded
- [ ]  **v0.3.5b:** 20-question bank covers all 7 categories
- [ ]  **v0.3.5c:** Statistical significance test returns p-value and effect size
- [ ]  **v0.3.5d:** CLI generates terminal, markdown, and HTML reports

---

## Phase v0.3.0 Complete Checklist

- [ ]  v0.3.1: Loader module working
- [ ]  v0.3.2: Context builder implemented
- [ ]  v0.3.3: Baseline agent responds
- [ ]  v0.3.4: DocStratum agent cites docs
- [ ]  v0.3.5: A/B harness compares both

**→ Ready to proceed to v0.4.0: Demo Layer**