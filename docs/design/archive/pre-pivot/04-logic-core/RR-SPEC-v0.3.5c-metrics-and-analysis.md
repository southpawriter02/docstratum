# v0.3.5c — Metrics Calculation & Statistical Analysis

> Comprehensive metrics pipeline: per-question analysis, aggregate statistics, quality scoring, and significance testing.

## Objective

Design and implement a metrics calculation system that:
- Computes per-question metrics (token overhead, latency, response quality)
- Aggregates metrics across test suites (mean, median, std, CI)
- Scores response quality using LLM-as-judge or heuristic approaches
- Performs statistical significance testing (paired t-test, Wilcoxon signed-rank)
- Calculates confidence intervals and effect sizes
- Produces actionable insights about agent performance

## Scope Boundaries

- **In scope**: Per-question metrics, aggregate metrics, quality scoring (both approaches), statistical tests (parametric + non-parametric), confidence intervals, effect size, MetricsSummary dataclass, MetricsCalculator class
- **Out of scope**: Report visualization (v0.3.5d), interactive dashboards (v0.4.x), hypothesis generation, root cause analysis
- **Constraints**: Must support batch processing 20+ questions; quality scoring should complete in <60s per test suite; significance testing requires n >= 5 questions

## Dependency Diagram

```
┌───────────────────────────────────────────┐
│         list[ABTestResult]                │
│     (raw test execution results)          │
└──────────────────┬────────────────────────┘
                   │
┌──────────────────▼────────────────────────┐
│      MetricsCalculator                    │
│  • per_question_metrics()                 │
│  • aggregate_metrics()                    │
│  • score_response_quality()               │
│  • significance_test()                    │
└──────────────────┬────────────────────────┘
        ┌──────────┴────────┬────────────┐
        │                   │            │
   ┌────▼─────┐    ┌────────▼────┐  ┌───▼────────┐
   │Per-Q      │    │Aggregate    │  │Quality     │
   │Metrics    │    │Metrics      │  │Scores      │
   └───────────┘    └─────────────┘  └────────────┘
        │                   │              │
        └───────────────────┼──────────────┘
                            │
                    ┌───────▼──────────┐
                    │ MetricsSummary   │
                    │  (comprehensive) │
                    └──────────────────┘
```

## Content Sections

### 1. Per-Question Metrics

Each `ABTestResult` yields detailed per-question metrics:

```python
from dataclasses import dataclass
from typing import Optional
import re

@dataclass
class PerQuestionMetrics:
    """Metrics for a single test question."""

    question_id: str
    question_text: str

    # Token efficiency
    baseline_tokens: int
    docstratum_tokens: int
    token_overhead: int  # docstratum - baseline
    token_overhead_pct: float  # (overhead / baseline) * 100

    # Latency performance
    baseline_latency_ms: float
    docstratum_latency_ms: float
    latency_diff_ms: float  # docstratum - baseline
    latency_improvement_pct: float  # (diff / baseline) * 100

    # Response characteristics
    baseline_length: int  # character count
    docstratum_length: int
    length_ratio: float  # docstratum / baseline
    baseline_word_count: int
    docstratum_word_count: int

    # Quality indicators (computed)
    url_count_baseline: int
    url_count_docstratum: int
    code_block_count_baseline: int
    code_block_count_docstratum: int
    terminology_match_score: float  # 0.0-1.0

    # Execution health
    baseline_success: bool
    docstratum_success: bool
    baseline_retry_count: int
    docstratum_retry_count: int

    @classmethod
    def from_test_result(cls, result: ABTestResult) -> 'PerQuestionMetrics':
        """Extract metrics from ABTestResult."""

        # Token metrics
        token_overhead = result.token_overhead
        token_overhead_pct = result.token_overhead_pct

        # Latency metrics
        latency_diff = result.latency_diff_ms
        latency_improvement_pct = result.latency_improvement_pct

        # Response characteristics
        baseline_length = len(result.baseline.response)
        docstratum_length = len(result.docstratum.response)
        length_ratio = result.response_length_ratio
        baseline_words = len(result.baseline.response.split())
        docstratum_words = len(result.docstratum.response.split())

        # URL extraction
        url_pattern = r'https?://[^\s\)\]]+|www\.[^\s\)\]]+'
        baseline_urls = len(re.findall(url_pattern, result.baseline.response))
        docstratum_urls = len(re.findall(url_pattern, result.docstratum.response))

        # Code block extraction
        code_pattern = r'```[\s\S]*?```|`[^`]+`'
        baseline_code = len(re.findall(code_pattern, result.baseline.response))
        docstratum_code = len(re.findall(code_pattern, result.docstratum.response))

        # Terminology match (simple implementation)
        terminology_score = cls._compute_terminology_match(
            result.baseline.response,
            result.docstratum.response,
        )

        return cls(
            question_id=result.question,
            question_text=result.question[:100],
            baseline_tokens=result.baseline.total_tokens,
            docstratum_tokens=result.docstratum.total_tokens,
            token_overhead=token_overhead,
            token_overhead_pct=token_overhead_pct,
            baseline_latency_ms=result.baseline.latency_ms,
            docstratum_latency_ms=result.docstratum.latency_ms,
            latency_diff_ms=latency_diff,
            latency_improvement_pct=latency_improvement_pct,
            baseline_length=baseline_length,
            docstratum_length=docstratum_length,
            length_ratio=length_ratio,
            baseline_word_count=baseline_words,
            docstratum_word_count=docstratum_words,
            url_count_baseline=baseline_urls,
            url_count_docstratum=docstratum_urls,
            code_block_count_baseline=baseline_code,
            code_block_count_docstratum=docstratum_code,
            terminology_match_score=terminology_score,
            baseline_success=result.baseline.success,
            docstratum_success=result.docstratum.success,
            baseline_retry_count=result.baseline.retry_count,
            docstratum_retry_count=result.docstratum.retry_count,
        )

    @staticmethod
    def _compute_terminology_match(text1: str, text2: str) -> float:
        """Compute lexical overlap as a proxy for terminology match (0.0-1.0)."""

        # Extract words (lowercase, alphanumeric)
        words1 = set(re.findall(r'\b\w+\b', text1.lower()))
        words2 = set(re.findall(r'\b\w+\b', text2.lower()))

        if not words1 or not words2:
            return 0.0

        # Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def to_dict(self) -> dict:
        """Export metrics to dictionary."""
        return {
            'question_id': self.question_id,
            'token_overhead': self.token_overhead,
            'token_overhead_pct': f'{self.token_overhead_pct:.2f}%',
            'latency_diff_ms': f'{self.latency_diff_ms:.2f}',
            'latency_improvement_pct': f'{self.latency_improvement_pct:.2f}%',
            'length_ratio': f'{self.length_ratio:.2f}',
            'url_count_baseline': self.url_count_baseline,
            'url_count_docstratum': self.url_count_docstratum,
            'terminology_match_score': f'{self.terminology_match_score:.3f}',
            'baseline_success': self.baseline_success,
            'docstratum_success': self.docstratum_success,
        }
```

**Per-Question Metrics Table:**

| Metric | Formula | Interpretation |
|--------|---------|-----------------|
| `token_overhead` | docstratum_total - baseline_total | Negative = fewer tokens (good) |
| `token_overhead_pct` | (overhead / baseline) × 100 | Percentage difference |
| `latency_diff_ms` | docstratum_latency - baseline_latency | Negative = faster (good) |
| `latency_improvement_pct` | (diff / baseline) × 100 | Percentage improvement |
| `length_ratio` | docstratum_length / baseline_length | >1 = more verbose; <1 = more concise |
| `url_count_docstratum - url_count_baseline` | Citation difference | More citations = more grounded |
| `code_blocks_docstratum - code_blocks_baseline` | Code example difference | More examples = more helpful |
| `terminology_match_score` | Jaccard similarity | >0.8 = good semantic alignment |

### 2. Aggregate Metrics & Statistical Summaries

Roll up per-question metrics into suite-level aggregate statistics:

```python
from dataclasses import dataclass, field
from statistics import mean, median, stdev, quantiles
from typing import Optional
import numpy as np

@dataclass
class AggregateMetrics:
    """Suite-level aggregate metrics."""

    # Token efficiency aggregates
    mean_token_overhead: float
    median_token_overhead: int
    std_token_overhead: float
    min_token_overhead: int
    max_token_overhead: int

    # Latency aggregates
    mean_latency_diff_ms: float
    median_latency_diff_ms: float
    std_latency_diff_ms: float
    min_latency_diff_ms: float
    max_latency_diff_ms: float

    # Response length aggregates
    mean_length_ratio: float
    median_length_ratio: float
    min_length_ratio: float
    max_length_ratio: float

    # Citation & code quality
    total_urls_baseline: int
    total_urls_docstratum: int
    mean_url_count_baseline: float
    mean_url_count_docstratum: float
    total_code_blocks_baseline: int
    total_code_blocks_docstratum: int

    # Terminology consistency
    mean_terminology_match: float
    min_terminology_match: float
    max_terminology_match: float

    # Execution health
    total_tests: int
    successful_tests: int
    baseline_only_failures: int
    docstratum_only_failures: int
    both_failures: int
    success_rate: float

    # Percentile ranges (Q1, Q2/median, Q3)
    token_overhead_q1: int
    token_overhead_q3: int
    latency_diff_q1: float
    latency_diff_q3: float

    @classmethod
    def from_per_question_metrics(
        cls,
        metrics: list[PerQuestionMetrics],
    ) -> 'AggregateMetrics':
        """Calculate aggregate metrics from per-question metrics."""

        token_overheads = [m.token_overhead for m in metrics]
        latency_diffs = [m.latency_diff_ms for m in metrics]
        length_ratios = [m.length_ratio for m in metrics]
        terminology_scores = [m.terminology_match_score for m in metrics]

        # Token efficiency
        mean_token_overhead = mean(token_overheads) if token_overheads else 0
        median_token_overhead = int(median(token_overheads)) if token_overheads else 0
        std_token_overhead = stdev(token_overheads) if len(token_overheads) > 1 else 0

        # Latency
        mean_latency_diff = mean(latency_diffs) if latency_diffs else 0
        median_latency_diff = median(latency_diffs) if latency_diffs else 0
        std_latency_diff = stdev(latency_diffs) if len(latency_diffs) > 1 else 0

        # Response length
        mean_length_ratio = mean(length_ratios) if length_ratios else 1.0
        median_length_ratio = median(length_ratios) if length_ratios else 1.0

        # Percentiles
        if len(token_overheads) >= 4:
            q1, q3 = quantiles(token_overheads, n=4)[0], quantiles(token_overheads, n=4)[2]
        else:
            q1, q3 = min(token_overheads), max(token_overheads)

        if len(latency_diffs) >= 4:
            q1_lat, q3_lat = quantiles(latency_diffs, n=4)[0], quantiles(latency_diffs, n=4)[2]
        else:
            q1_lat, q3_lat = min(latency_diffs), max(latency_diffs)

        # Execution health
        total_tests = len(metrics)
        successful = sum(1 for m in metrics if m.baseline_success and m.docstratum_success)
        baseline_only_fail = sum(1 for m in metrics if not m.baseline_success and m.docstratum_success)
        docstratum_only_fail = sum(1 for m in metrics if m.baseline_success and not m.docstratum_success)
        both_fail = sum(1 for m in metrics if not m.baseline_success and not m.docstratum_success)
        success_rate = successful / total_tests if total_tests > 0 else 0

        # URLs and code
        total_urls_baseline = sum(m.url_count_baseline for m in metrics)
        total_urls_docstratum = sum(m.url_count_docstratum for m in metrics)
        mean_url_baseline = total_urls_baseline / total_tests if total_tests > 0 else 0
        mean_url_docstratum = total_urls_docstratum / total_tests if total_tests > 0 else 0
        total_code_baseline = sum(m.code_block_count_baseline for m in metrics)
        total_code_docstratum = sum(m.code_block_count_docstratum for m in metrics)

        # Terminology
        mean_terminology = mean(terminology_scores) if terminology_scores else 0

        return cls(
            mean_token_overhead=mean_token_overhead,
            median_token_overhead=median_token_overhead,
            std_token_overhead=std_token_overhead,
            min_token_overhead=min(token_overheads) if token_overheads else 0,
            max_token_overhead=max(token_overheads) if token_overheads else 0,
            mean_latency_diff_ms=mean_latency_diff,
            median_latency_diff_ms=median_latency_diff,
            std_latency_diff_ms=std_latency_diff,
            min_latency_diff_ms=min(latency_diffs) if latency_diffs else 0,
            max_latency_diff_ms=max(latency_diffs) if latency_diffs else 0,
            mean_length_ratio=mean_length_ratio,
            median_length_ratio=median_length_ratio,
            min_length_ratio=min(length_ratios) if length_ratios else 1.0,
            max_length_ratio=max(length_ratios) if length_ratios else 1.0,
            total_urls_baseline=total_urls_baseline,
            total_urls_docstratum=total_urls_docstratum,
            mean_url_count_baseline=mean_url_baseline,
            mean_url_count_docstratum=mean_url_docstratum,
            total_code_blocks_baseline=total_code_baseline,
            total_code_blocks_docstratum=total_code_docstratum,
            mean_terminology_match=mean_terminology,
            min_terminology_match=min(terminology_scores) if terminology_scores else 0,
            max_terminology_match=max(terminology_scores) if terminology_scores else 0,
            total_tests=total_tests,
            successful_tests=successful,
            baseline_only_failures=baseline_only_fail,
            docstratum_only_failures=docstratum_only_fail,
            both_failures=both_fail,
            success_rate=success_rate,
            token_overhead_q1=int(q1),
            token_overhead_q3=int(q3),
            latency_diff_q1=q1_lat,
            latency_diff_q3=q3_lat,
        )

    def to_dict(self) -> dict:
        """Export to dictionary for reporting."""
        return {
            'token_efficiency': {
                'mean_overhead': f'{self.mean_token_overhead:.0f} tokens',
                'median_overhead': f'{self.median_token_overhead} tokens',
                'std_overhead': f'{self.std_token_overhead:.0f}',
                'range': f'{self.min_token_overhead} to {self.max_token_overhead}',
            },
            'latency': {
                'mean_diff': f'{self.mean_latency_diff_ms:.2f} ms',
                'median_diff': f'{self.median_latency_diff_ms:.2f} ms',
                'std_diff': f'{self.std_latency_diff_ms:.2f}',
                'range': f'{self.min_latency_diff_ms:.2f} to {self.max_latency_diff_ms:.2f} ms',
            },
            'response_quality': {
                'mean_length_ratio': f'{self.mean_length_ratio:.2f}',
                'mean_url_count_baseline': f'{self.mean_url_count_baseline:.1f}',
                'mean_url_count_docstratum': f'{self.mean_url_count_docstratum:.1f}',
                'mean_code_examples_baseline': f'{self.total_code_blocks_baseline / self.total_tests:.1f}',
                'mean_code_examples_docstratum': f'{self.total_code_blocks_docstratum / self.total_tests:.1f}',
            },
            'execution_health': {
                'total_tests': self.total_tests,
                'success_rate': f'{self.success_rate * 100:.1f}%',
                'docstratum_only_failures': self.docstratum_only_failures,
                'baseline_only_failures': self.baseline_only_failures,
            },
        }
```

### 3. Quality Scoring: LLM-as-Judge vs Heuristics

Implement two approaches for response quality assessment:

```python
from typing import Literal
from abc import ABC, abstractmethod

class QualityScorer(ABC):
    """Base class for response quality scoring."""

    @abstractmethod
    def score(self, baseline_response: str, docstratum_response: str) -> dict:
        """Score responses. Returns dict with 'baseline', 'docstratum', 'winner'."""
        pass

class HeuristicQualityScorer(QualityScorer):
    """Simple heuristic-based scoring (fast, no API calls)."""

    def score(self, baseline_response: str, docstratum_response: str) -> dict:
        """Score based on observable response characteristics."""

        baseline_score = self._score_response(baseline_response)
        docstratum_score = self._score_response(docstratum_response)

        winner = 'docstratum' if docstratum_score > baseline_score else 'baseline' if baseline_score > docstratum_score else 'tie'

        return {
            'baseline_score': baseline_score,
            'docstratum_score': docstratum_score,
            'winner': winner,
            'reasoning': self._get_reasoning(baseline_score, docstratum_score),
        }

    def _score_response(self, response: str) -> float:
        """Calculate heuristic quality score (0.0-10.0)."""

        score = 0.0

        # Length score: prefer medium length (200-1000 chars, not too short/long)
        length = len(response)
        if 200 <= length <= 1000:
            score += 3.0
        elif 100 <= length <= 2000:
            score += 2.0
        elif length > 0:
            score += 1.0

        # Structure score: has lists/sections (indicated by newlines, bullets)
        lines = response.split('\n')
        if len(lines) > 5:
            score += 2.0
        elif len(lines) > 2:
            score += 1.0

        # Code examples present
        if '```' in response or '`' in response:
            score += 2.0

        # URLs/references present
        if 'http' in response or 'http' in response:
            score += 1.5

        # Completeness: response has conclusion/summary
        if any(word in response.lower() for word in ['conclusion', 'summary', 'in summary', 'therefore']):
            score += 1.5

        return min(score, 10.0)

    @staticmethod
    def _get_reasoning(baseline_score: float, docstratum_score: float) -> str:
        """Explain why one response scored higher."""
        if abs(baseline_score - docstratum_score) < 0.5:
            return "Responses are very similar in quality."
        diff = docstratum_score - baseline_score
        if diff > 0:
            return f"DocStratum response scores {diff:.1f} points higher on heuristic criteria."
        return f"Baseline response scores {abs(diff):.1f} points higher on heuristic criteria."

class LLMAsJudgeScorer(QualityScorer):
    """LLM-as-judge approach: use third LLM to rate quality (slower, more accurate)."""

    def __init__(self, llms_source, judge_model: str = 'claude-3-5-sonnet'):
        self.llms_source = llms_source
        self.judge_model = judge_model

    def score(self, baseline_response: str, docstratum_response: str, question: str = '') -> dict:
        """Use LLM to evaluate and compare responses."""

        prompt = f"""Compare these two responses to the question: "{question}"

BASELINE RESPONSE:
{baseline_response}

DOCSTRATUM RESPONSE:
{docstratum_response}

Rate each response on:
1. Accuracy (0-10): Does it correctly answer the question?
2. Completeness (0-10): Does it cover all important aspects?
3. Clarity (0-10): Is it well-structured and easy to understand?
4. Conciseness (0-10): Is it appropriately detailed without bloat?

Provide scores and indicate which response is superior overall."""

        try:
            evaluation = asyncio.run(
                self.llms_source.invoke(
                    question=prompt,
                    model=self.judge_model,
                )
            )

            # Parse LLM evaluation (simplified)
            docstratum_score = self._extract_docstratum_advantage(evaluation)

            return {
                'baseline_score': 5.0,  # Placeholder
                'docstratum_score': 5.0 + docstratum_score,
                'winner': 'docstratum' if docstratum_score > 0 else 'baseline' if docstratum_score < 0 else 'tie',
                'reasoning': evaluation[:200],
            }

        except Exception as e:
            return {
                'baseline_score': 0.0,
                'docstratum_score': 0.0,
                'winner': 'error',
                'reasoning': f'LLM evaluation failed: {str(e)}',
            }

    @staticmethod
    def _extract_docstratum_advantage(evaluation_text: str) -> float:
        """Extract numeric advantage from LLM evaluation (simplified)."""
        # In production, use structured output (JSON) from LLM
        # For now, heuristic detection
        if 'docstratum' in evaluation_text.lower() and 'better' in evaluation_text.lower():
            return 2.0
        elif 'baseline' in evaluation_text.lower() and 'better' in evaluation_text.lower():
            return -2.0
        return 0.0
```

### 4. Statistical Significance Testing

Implement paired statistical tests to determine if improvements are real:

```python
from scipy import stats
from dataclasses import dataclass

@dataclass
class SignificanceTestResult:
    """Results from statistical significance test."""

    test_name: str  # 'paired_t_test', 'wilcoxon_signed_rank'
    statistic: float
    p_value: float
    significant_at_05: bool  # p < 0.05
    significant_at_01: bool  # p < 0.01
    effect_size: float  # Cohen's d or rank-biserial correlation
    interpretation: str

    def summary(self) -> str:
        """Short text summary of significance."""
        if self.significant_at_01:
            return f'{self.test_name}: HIGHLY SIGNIFICANT (p={self.p_value:.4f}), d={self.effect_size:.2f}'
        elif self.significant_at_05:
            return f'{self.test_name}: SIGNIFICANT (p={self.p_value:.4f}), d={self.effect_size:.2f}'
        else:
            return f'{self.test_name}: NOT SIGNIFICANT (p={self.p_value:.4f}), d={self.effect_size:.2f}'

class StatisticalTester:
    """Conduct significance tests on A/B test results."""

    @staticmethod
    def paired_t_test(
        baseline_values: list[float],
        docstratum_values: list[float],
    ) -> SignificanceTestResult:
        """Paired t-test for metric improvement (parametric)."""

        if len(baseline_values) < 3:
            return SignificanceTestResult(
                test_name='paired_t_test',
                statistic=0.0,
                p_value=1.0,
                significant_at_05=False,
                significant_at_01=False,
                effect_size=0.0,
                interpretation='Insufficient samples (n < 3)',
            )

        # Compute paired differences
        differences = [r - b for b, r in zip(baseline_values, docstratum_values)]

        # t-test (one-sided: does DocStratum improve metric?)
        t_stat, p_value = stats.ttest_1samp(differences, 0, alternative='less')

        # Cohen's d effect size
        d = stats.ttest_ind(docstratum_values, baseline_values)[0] / len(baseline_values) ** 0.5

        interpretation = 'DocStratum likely performs better' if p_value < 0.05 else 'No significant difference'

        return SignificanceTestResult(
            test_name='paired_t_test',
            statistic=t_stat,
            p_value=p_value,
            significant_at_05=p_value < 0.05,
            significant_at_01=p_value < 0.01,
            effect_size=d,
            interpretation=interpretation,
        )

    @staticmethod
    def wilcoxon_signed_rank_test(
        baseline_values: list[float],
        docstratum_values: list[float],
    ) -> SignificanceTestResult:
        """Wilcoxon signed-rank test (non-parametric alternative)."""

        if len(baseline_values) < 3:
            return SignificanceTestResult(
                test_name='wilcoxon_signed_rank',
                statistic=0.0,
                p_value=1.0,
                significant_at_05=False,
                significant_at_01=False,
                effect_size=0.0,
                interpretation='Insufficient samples (n < 3)',
            )

        # Paired differences for ranking
        differences = [r - b for b, r in zip(baseline_values, docstratum_values)]

        # Wilcoxon signed-rank test
        w_stat, p_value = stats.wilcoxon(differences, alternative='less')

        # Rank-biserial correlation as effect size
        n = len(differences)
        effect_size = 1 - (2 * w_stat) / (n * (n + 1))

        interpretation = 'DocStratum likely performs better' if p_value < 0.05 else 'No significant difference'

        return SignificanceTestResult(
            test_name='wilcoxon_signed_rank',
            statistic=w_stat,
            p_value=p_value,
            significant_at_05=p_value < 0.05,
            significant_at_01=p_value < 0.01,
            effect_size=effect_size,
            interpretation=interpretation,
        )

    @staticmethod
    def confidence_interval_95(
        values: list[float],
        metric_name: str = 'metric',
    ) -> dict:
        """Calculate 95% confidence interval using t-distribution."""

        if len(values) < 2:
            return {'error': 'Need at least 2 samples'}

        mean = np.mean(values)
        std_err = np.std(values, ddof=1) / np.sqrt(len(values))
        t_critical = stats.t.ppf(0.975, len(values) - 1)
        margin_of_error = t_critical * std_err

        return {
            'metric': metric_name,
            'mean': mean,
            'ci_lower': mean - margin_of_error,
            'ci_upper': mean + margin_of_error,
            'margin_of_error': margin_of_error,
        }

    @staticmethod
    def cohens_d(group1: list[float], group2: list[float]) -> float:
        """Calculate Cohen's d effect size."""

        n1, n2 = len(group1), len(group2)
        var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)

        # Pooled standard deviation
        pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))

        if pooled_std == 0:
            return 0.0

        return (np.mean(group1) - np.mean(group2)) / pooled_std
```

### 5. MetricsSummary Dataclass

Comprehensive summary combining all metric types:

```python
@dataclass
class MetricsSummary:
    """Complete metrics summary for a test session."""

    session_id: str
    suite_name: str
    timestamp: datetime

    # Per-question metrics
    per_question_metrics: list[PerQuestionMetrics]

    # Aggregates
    aggregate_metrics: AggregateMetrics

    # Quality scores
    quality_scores: dict  # question_id -> {baseline_score, docstratum_score, winner}

    # Statistical tests
    token_overhead_significance: SignificanceTestResult
    latency_diff_significance: SignificanceTestResult
    length_ratio_significance: SignificanceTestResult

    # Confidence intervals
    token_overhead_ci: dict
    latency_diff_ci: dict

    # Summary conclusions
    overall_winner: str  # 'docstratum', 'baseline', 'tie'
    key_findings: list[str]

    @classmethod
    def compute(
        cls,
        results: list[ABTestResult],
        session_id: str,
        suite_name: str = 'default',
        quality_scorer: QualityScorer = None,
    ) -> 'MetricsSummary':
        """Compute comprehensive metrics from test results."""

        # Per-question metrics
        per_q_metrics = [PerQuestionMetrics.from_test_result(r) for r in results]

        # Aggregates
        aggregate = AggregateMetrics.from_per_question_metrics(per_q_metrics)

        # Quality scores (optional)
        quality_scores = {}
        if quality_scorer:
            for result in results:
                quality_scores[result.question] = quality_scorer.score(
                    result.baseline.response,
                    result.docstratum.response,
                    result.question,
                )

        # Extract numeric lists for statistical tests
        token_overheads = [m.token_overhead for m in per_q_metrics]
        latency_diffs = [m.latency_diff_ms for m in per_q_metrics]
        length_ratios = [m.length_ratio for m in per_q_metrics]

        tester = StatisticalTester()

        # Significance tests
        token_sig = tester.paired_t_test(
            [m.baseline_tokens for m in per_q_metrics],
            [m.docstratum_tokens for m in per_q_metrics],
        )

        latency_sig = tester.wilcoxon_signed_rank_test(
            [m.baseline_latency_ms for m in per_q_metrics],
            [m.docstratum_latency_ms for m in per_q_metrics],
        )

        length_sig = tester.paired_t_test(
            [m.baseline_length for m in per_q_metrics],
            [m.docstratum_length for m in per_q_metrics],
        )

        # Confidence intervals
        token_overhead_ci = tester.confidence_interval_95(token_overheads, 'token_overhead')
        latency_diff_ci = tester.confidence_interval_95(latency_diffs, 'latency_diff_ms')

        # Determine overall winner
        overall_winner = cls._determine_winner(
            aggregate,
            token_sig,
            latency_sig,
            quality_scores,
        )

        # Key findings
        key_findings = cls._generate_findings(aggregate, token_sig, latency_sig)

        return cls(
            session_id=session_id,
            suite_name=suite_name,
            timestamp=datetime.utcnow(),
            per_question_metrics=per_q_metrics,
            aggregate_metrics=aggregate,
            quality_scores=quality_scores,
            token_overhead_significance=token_sig,
            latency_diff_significance=latency_sig,
            length_ratio_significance=length_sig,
            token_overhead_ci=token_overhead_ci,
            latency_diff_ci=latency_diff_ci,
            overall_winner=overall_winner,
            key_findings=key_findings,
        )

    @staticmethod
    def _determine_winner(
        aggregate: AggregateMetrics,
        token_sig: SignificanceTestResult,
        latency_sig: SignificanceTestResult,
        quality_scores: dict,
    ) -> str:
        """Determine overall winner based on multiple criteria."""

        points = {'baseline': 0, 'docstratum': 0}

        # Token efficiency
        if aggregate.mean_token_overhead < 0:
            points['docstratum'] += 2
        elif aggregate.mean_token_overhead > 0:
            points['baseline'] += 2

        # Latency
        if aggregate.mean_latency_diff_ms < 0:
            points['docstratum'] += 2
        elif aggregate.mean_latency_diff_ms > 0:
            points['baseline'] += 2

        # Statistical significance
        if token_sig.significant_at_05 and aggregate.mean_token_overhead < 0:
            points['docstratum'] += 1
        if latency_sig.significant_at_05 and aggregate.mean_latency_diff_ms < 0:
            points['docstratum'] += 1

        # Quality scores
        if quality_scores:
            docstratum_wins = sum(1 for s in quality_scores.values() if s['winner'] == 'docstratum')
            baseline_wins = sum(1 for s in quality_scores.values() if s['winner'] == 'baseline')
            if docstratum_wins > baseline_wins:
                points['docstratum'] += 1
            elif baseline_wins > docstratum_wins:
                points['baseline'] += 1

        if points['docstratum'] > points['baseline']:
            return 'docstratum'
        elif points['baseline'] > points['docstratum']:
            return 'baseline'
        return 'tie'

    @staticmethod
    def _generate_findings(
        aggregate: AggregateMetrics,
        token_sig: SignificanceTestResult,
        latency_sig: SignificanceTestResult,
    ) -> list[str]:
        """Generate human-readable key findings."""

        findings = []

        # Token efficiency
        if aggregate.mean_token_overhead < -10:
            findings.append(f"DocStratum is {abs(aggregate.mean_token_overhead):.0f} tokens more efficient on average")
        elif aggregate.mean_token_overhead > 10:
            findings.append(f"DocStratum requires {aggregate.mean_token_overhead:.0f} more tokens on average")

        # Latency
        if aggregate.mean_latency_diff_ms < -100:
            findings.append(f"DocStratum is {abs(aggregate.mean_latency_diff_ms):.0f}ms faster")
        elif aggregate.mean_latency_diff_ms > 100:
            findings.append(f"DocStratum is {aggregate.mean_latency_diff_ms:.0f}ms slower")

        # Significance
        if token_sig.significant_at_05:
            findings.append(f"Token efficiency difference is statistically significant (p={token_sig.p_value:.4f})")
        if latency_sig.significant_at_05:
            findings.append(f"Latency difference is statistically significant (p={latency_sig.p_value:.4f})")

        # Reliability
        if aggregate.docstratum_only_failures > 0:
            findings.append(f"DocStratum failed on {aggregate.docstratum_only_failures} questions")
        if aggregate.success_rate < 1.0:
            findings.append(f"Suite success rate: {aggregate.success_rate*100:.1f}%")

        return findings
```

## Deliverables

1. **PerQuestionMetrics dataclass** (180 lines)
   - All per-question metric fields
   - Computation from ABTestResult
   - Terminology match calculation
   - URL/code block extraction

2. **AggregateMetrics dataclass** (200 lines)
   - Token, latency, length aggregates
   - Percentile calculations
   - Execution health summary
   - Citation and code quality rollup

3. **QualityScorer base class + Implementations** (220 lines)
   - HeuristicQualityScorer (no API calls, fast)
   - LLMAsJudgeScorer (high accuracy, slower)
   - Both score() methods with reasoning

4. **StatisticalTester class** (180 lines)
   - Paired t-test
   - Wilcoxon signed-rank test
   - Confidence interval calculation (95%)
   - Cohen's d effect size
   - SignificanceTestResult dataclass

5. **MetricsSummary dataclass** (150 lines)
   - Comprehensive metrics aggregation
   - Winner determination logic
   - Key findings generation
   - compute() class method

6. **Complete MetricsCalculator integration** (100 lines)
   - Orchestrate metrics computation
   - Quality scoring orchestration
   - Result persistence

## Acceptance Criteria

- [ ] PerQuestionMetrics compute all 14+ metrics correctly
- [ ] Terminology match score is Jaccard similarity (0.0-1.0)
- [ ] AggregateMetrics correctly compute mean/median/std/min/max/quantiles
- [ ] HeuristicQualityScorer completes in <1s per suite
- [ ] LLMAsJudgeScorer handles API failures gracefully
- [ ] Paired t-test requires n >= 3 samples
- [ ] Wilcoxon test is non-parametric (no normality assumption)
- [ ] 95% CI uses t-distribution (not z-distribution)
- [ ] Cohen's d handles edge cases (zero std dev)
- [ ] SignificanceTestResult p-values are in range [0.0, 1.0]
- [ ] MetricsSummary.overall_winner uses multi-criteria scoring
- [ ] Key findings are specific and actionable
- [ ] All dataclasses serialize to JSON/dict without errors
- [ ] Statistical tests work correctly with 20-question test suites

## Next Step

→ Proceed to **v0.3.5d — CLI Interface & Report Generation** to build the command-line interface, report generators, and export formats.
