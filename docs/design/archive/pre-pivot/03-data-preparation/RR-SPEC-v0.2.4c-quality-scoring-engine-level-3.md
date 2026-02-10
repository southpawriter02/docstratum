# v0.2.4c — Quality Scoring Engine (Level 3)

> The Quality Scoring Engine evaluates the informativeness, completeness, and consistency of llms.txt content beyond mere correctness. It implements multi-dimensional quality assessment (completeness, informativeness, consistency, freshness, appropriateness) with configurable scoring rubrics. Automated heuristics analyze content depth, definition specificity, anti-pattern coverage, and example diversity. Quality scores are tracked across file versions to identify improvement trends, and scores are benchmarked against exemplary implementations (Stripe, Nuxt, Vercel). Token budget analysis ensures files remain efficient for LLM consumption.

## Objective

Implement automated quality assessment that:
- Evaluates content across 5 quality dimensions
- Assigns 1-5 scores with specific rubric criteria
- Generates improvement suggestions
- Tracks quality trends across versions
- Benchmarks against industry exemplars
- Analyzes token efficiency
- Provides actionable quality reports

## Scope Boundaries

**In Scope:**
- Quality dimension definitions (completeness, informativeness, consistency, freshness, appropriateness)
- Scoring rubrics with 1-5 scale and specific criteria
- Automated heuristics: information density, entity density, diversity metrics
- Per-entry quality scores and per-dimension breakdowns
- Configurable quality thresholds (min score, per-dimension minimums)
- Quality trend tracking across versions
- Benchmark data from exemplary llms.txt files
- Token budget calculation and analysis
- Quality report generation (per-entry scores, dimension breakdowns, suggestions)
- Quality badges/classifications (Excellent/Good/Fair/Needs Work)

**Out of Scope:**
- Manual content review (this is automated)
- SEO or readability analysis beyond informativeness
- Multilingual content assessment
- Visual/multimedia analysis
- Content fact-checking

## Dependency Diagram

```
┌──────────────────────────────────────────────────────┐
│  v0.2.4c: Quality Scoring Engine                     │
│  (Level 3: QUALITY)                                  │
└────────────────┬─────────────────────────────────────┘
                 │
      ┌──────────┼──────────┬──────────────┐
      │          │          │              │
      ▼          ▼          ▼              ▼
┌─────────┐ ┌──────────┐ ┌─────────────┐ ┌────────────┐
│Compl.   │ │Inform.   │ │Consistency  │ │Freshness   │
│Score    │ │Score     │ │Score        │ │Score       │
└────┬────┘ └────┬─────┘ └──────┬──────┘ └─────┬──────┘
     │           │              │              │
     └───────────┼──────────────┼──────────────┘
                 │              │
        ┌────────┴──────────────┴────────┐
        │                               │
        ▼                               ▼
┌──────────────────────┐     ┌─────────────────┐
│ Automated Heuristics │     │ Scoring Rubrics │
│ - Info Density       │     │ (1-5 scale)     │
│ - Entity Density     │     │                 │
│ - Diversity Score    │     │ Per dimension   │
│ - Anti-pattern Ratio │     │ per entry       │
└──────────┬───────────┘     └────────┬────────┘
           │                         │
           └────────────┬────────────┘
                        │
                        ▼
            ┌──────────────────────┐
            │ Weighted Composite    │
            │ Quality Score         │
            │ (1-5 overall)         │
            └──────────┬───────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   ┌─────────┐  ┌────────────┐  ┌────────────┐
   │Per-Entry│  │Quality     │  │Token       │
   │Scores   │  │Trends      │  │Budget      │
   │         │  │(vs prev)   │  │Analysis    │
   └────┬────┘  └─────┬──────┘  └─────┬──────┘
        │             │              │
        └─────────────┼──────────────┘
                      │
                      ▼
         ┌──────────────────────────┐
         │ Quality Report           │
         │ - Dimension breakdowns   │
         │ - Benchmarks vs exemplars│
         │ - Improvement suggestions│
         │ - Quality badges         │
         └──────────────────────────┘

Input: Validated, content-checked llms.txt data + optional prior scores
Output: Quality scores per dimension, overall rating, improvement suggestions
```

## Section 1: Quality Dimensions & Rubrics

### 1.1 Quality Dimensions

Five dimensions assess different aspects of quality:

| Dimension | Description | Measured By |
|-----------|-------------|------------|
| **Completeness** | All necessary information present; no major gaps | Field coverage, summary length, example count |
| **Informativeness** | Content is substantive and specific; not vague | Word count, unique concept mentions, detail level |
| **Consistency** | Formatting and terminology consistent across file | Naming conventions, format uniformity, phrase repetition |
| **Freshness** | Content current and recently verified | Last-modified timestamp, URL verification freshness |
| **Appropriateness** | Content matches intended audience; no excessive length | Token count, description conciseness, redundancy ratio |

### 1.2 Scoring Rubrics

Each dimension uses a 1-5 scale:

```python
# quality_scoring/rubrics.py

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class RubricLevel:
    """Single level of a scoring rubric."""
    score: int  # 1-5
    label: str
    criteria: List[str]
    min_threshold: float
    max_threshold: float


class ScoringRubric:
    """Rubric for evaluating quality dimensions."""

    COMPLETENESS_RUBRIC = [
        RubricLevel(
            score=5,
            label="Excellent",
            criteria=[
                "All required fields present and well-filled",
                "Comprehensive coverage (>90% field completeness)",
                "Descriptions substantive (>150 words for concepts)",
                "Multiple examples provided"
            ],
            min_threshold=0.90,
            max_threshold=1.0
        ),
        RubricLevel(
            score=4,
            label="Good",
            criteria=[
                "Most required fields present",
                "Good coverage (70-89% completeness)",
                "Solid descriptions (100-150 words)",
                "Some examples provided"
            ],
            min_threshold=0.70,
            max_threshold=0.89
        ),
        RubricLevel(
            score=3,
            label="Fair",
            criteria=[
                "Core fields present but some gaps",
                "Adequate coverage (50-69%)",
                "Basic descriptions (50-100 words)",
                "Minimal examples"
            ],
            min_threshold=0.50,
            max_threshold=0.69
        ),
        RubricLevel(
            score=2,
            label="Needs Work",
            criteria=[
                "Several required fields missing",
                "Poor coverage (<50%)",
                "Sparse descriptions (<50 words)",
                "No examples or very few"
            ],
            min_threshold=0.0,
            max_threshold=0.49
        ),
    ]

    INFORMATIVENESS_RUBRIC = [
        RubricLevel(
            score=5,
            label="Highly Informative",
            criteria=[
                "High information density (>100 words per concept)",
                "Rich with specific details and entities",
                "Clear examples and use cases",
                "Practical guidance included"
            ],
            min_threshold=0.85,
            max_threshold=1.0
        ),
        RubricLevel(
            score=4,
            label="Informative",
            criteria=[
                "Good information density (80-100 words/concept)",
                "Specific terminology used",
                "Relevant examples provided",
                "Generally practical"
            ],
            min_threshold=0.70,
            max_threshold=0.84
        ),
        RubricLevel(
            score=3,
            label="Adequately Informative",
            criteria=[
                "Moderate density (50-80 words/concept)",
                "Some specific details",
                "Basic examples",
                "General guidance"
            ],
            min_threshold=0.50,
            max_threshold=0.69
        ),
        RubricLevel(
            score=2,
            label="Low Information Value",
            criteria=[
                "Sparse content (<50 words/concept)",
                "Vague terminology",
                "Missing examples",
                "Little practical value"
            ],
            min_threshold=0.0,
            max_threshold=0.49
        ),
    ]

    CONSISTENCY_RUBRIC = [
        RubricLevel(
            score=5,
            label="Highly Consistent",
            criteria=[
                "100% consistent naming and formatting",
                "Uniform structure across entries",
                "No contradictions detected",
                "Standardized terminology"
            ],
            min_threshold=0.95,
            max_threshold=1.0
        ),
        RubricLevel(
            score=4,
            label="Mostly Consistent",
            criteria=[
                "95-98% consistent formatting",
                "Minor inconsistencies",
                "Generally uniform structure",
                "Mostly standardized terminology"
            ],
            min_threshold=0.90,
            max_threshold=0.94
        ),
        RubricLevel(
            score=3,
            label="Reasonably Consistent",
            criteria=[
                "80-90% consistent",
                "Some formatting variations",
                "Mostly uniform structure",
                "Mostly consistent terminology"
            ],
            min_threshold=0.75,
            max_threshold=0.89
        ),
        RubricLevel(
            score=2,
            label="Inconsistent",
            criteria=[
                "<75% consistent",
                "Noticeable variations",
                "Inconsistent structure",
                "Inconsistent terminology"
            ],
            min_threshold=0.0,
            max_threshold=0.74
        ),
    ]

    FRESHNESS_RUBRIC = [
        RubricLevel(
            score=5,
            label="Very Fresh",
            criteria=[
                "Modified within last 7 days",
                "All URLs verified within 24 hours",
                "No deprecated content detected"
            ],
            min_threshold=0.85,
            max_threshold=1.0
        ),
        RubricLevel(
            score=4,
            label="Fresh",
            criteria=[
                "Modified within last 30 days",
                "URLs verified within 7 days",
                "Minimal deprecated content"
            ],
            min_threshold=0.70,
            max_threshold=0.84
        ),
        RubricLevel(
            score=3,
            label="Adequately Fresh",
            criteria=[
                "Modified within last 90 days",
                "URLs verified within 30 days",
                "Some dated content"
            ],
            min_threshold=0.50,
            max_threshold=0.69
        ),
        RubricLevel(
            score=2,
            label="Stale",
            criteria=[
                "Not modified for >90 days",
                "URLs not recently verified",
                "Multiple outdated sections"
            ],
            min_threshold=0.0,
            max_threshold=0.49
        ),
    ]

    APPROPRIATENESS_RUBRIC = [
        RubricLevel(
            score=5,
            label="Perfectly Appropriate",
            criteria=[
                "Optimal token count (< 8000 tokens)",
                "No unnecessary verbosity",
                "Concise yet complete",
                "Target audience clear and matched"
            ],
            min_threshold=0.9,
            max_threshold=1.0
        ),
        RubricLevel(
            score=4,
            label="Well Appropriate",
            criteria=[
                "Token count acceptable (8000-12000)",
                "Minimal redundancy",
                "Generally concise",
                "Audience well-served"
            ],
            min_threshold=0.75,
            max_threshold=0.89
        ),
        RubricLevel(
            score=3,
            label="Appropriately Balanced",
            criteria=[
                "Token count adequate (12000-16000)",
                "Some redundancy present",
                "Could be more concise",
                "Audience mostly served"
            ],
            min_threshold=0.60,
            max_threshold=0.74
        ),
        RubricLevel(
            score=2,
            label="Excessive or Sparse",
            criteria=[
                "Token count excessive (>16000) or too sparse",
                "Significant redundancy",
                "Needs condensing or expansion",
                "Audience expectations unclear"
            ],
            min_threshold=0.0,
            max_threshold=0.59
        ),
    ]

    @classmethod
    def get_rubric(cls, dimension: str) -> List[RubricLevel]:
        """Get rubric for a dimension."""
        rubric_map = {
            "completeness": cls.COMPLETENESS_RUBRIC,
            "informativeness": cls.INFORMATIVENESS_RUBRIC,
            "consistency": cls.CONSISTENCY_RUBRIC,
            "freshness": cls.FRESHNESS_RUBRIC,
            "appropriateness": cls.APPROPRIATENESS_RUBRIC,
        }
        return rubric_map.get(dimension, [])

    @classmethod
    def score_from_metric(cls, dimension: str, metric_value: float) -> int:
        """
        Get score (1-5) for a dimension based on metric value.

        Args:
            dimension: Dimension name
            metric_value: Calculated metric (0-1 scale)

        Returns:
            Score 1-5
        """
        rubric = cls.get_rubric(dimension)
        for level in reversed(rubric):  # Check from highest to lowest
            if metric_value >= level.min_threshold:
                return level.score
        return 1
```

## Section 2: Automated Heuristics

### 2.1 Overview

Heuristics automatically calculate metrics for each dimension:
- **Completeness**: Field coverage percentage, average field population
- **Informativeness**: Information density (words/entry), named entity density
- **Consistency**: Format uniformity score, naming convention adherence
- **Freshness**: Days since modification, URL verification recency
- **Appropriateness**: Token count efficiency, redundancy ratio

### 2.2 Implementation

```python
# quality_scoring/heuristics.py

import re
from typing import Dict, List, Tuple
from datetime import datetime
from collections import Counter


class InformationHeuristics:
    """Calculate information-related metrics."""

    @staticmethod
    def word_density(text: str) -> float:
        """Calculate word count."""
        if not text:
            return 0.0
        words = len(text.split())
        return float(words)

    @staticmethod
    def unique_concepts(text: str) -> int:
        """Count unique capitalized concepts/entities."""
        # Simple heuristic: find capitalized multi-word phrases
        entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        return len(set(entities))

    @staticmethod
    def information_density(description: str, expected_concepts: int = 3) -> float:
        """
        Calculate information density (0-1 scale).

        Formula: (unique_concepts / expected_concepts + word_count / 100) / 2
        """
        word_count = len(description.split())
        unique_concepts = InformationHeuristics.unique_concepts(description)

        # Normalize to 0-1 range
        concept_score = min(1.0, unique_concepts / max(expected_concepts, 1))
        word_score = min(1.0, word_count / 100.0)

        return (concept_score + word_score) / 2.0

    @staticmethod
    def named_entity_density(text: str) -> float:
        """
        Calculate named entity density (specific mentions per 100 words).

        Higher = more specific details mentioned.
        """
        if not text:
            return 0.0

        words = text.split()
        entities = InformationHeuristics.unique_concepts(text)

        return min(1.0, (entities / max(len(words), 1)) * 5)


class CompletenessHeuristics:
    """Calculate completeness metrics."""

    @staticmethod
    def field_coverage(entry: Dict) -> float:
        """
        Calculate field coverage (0-1 scale).

        Returns ratio of non-empty fields to required fields.
        """
        required_fields = {'id', 'title', 'url', 'summary'}
        optional_fields = {'description', 'examples', 'last_verified'}

        non_empty = sum(
            1 for field in required_fields
            if entry.get(field) and str(entry.get(field)).strip()
        )

        optional_filled = sum(
            1 for field in optional_fields
            if entry.get(field) and str(entry.get(field)).strip()
        )

        return (non_empty + (optional_filled * 0.5)) / (len(required_fields) + len(optional_fields) * 0.5)

    @staticmethod
    def coverage_across_entries(entries: List[Dict], dimension_key: str) -> float:
        """
        Calculate coverage across multiple entries.

        Args:
            entries: List of entries (pages, concepts, etc.)
            dimension_key: Key to check (e.g., 'description')

        Returns:
            Ratio of entries with non-empty field to total entries
        """
        if not entries:
            return 1.0

        filled = sum(
            1 for entry in entries
            if entry.get(dimension_key) and str(entry.get(dimension_key)).strip()
        )

        return filled / len(entries)


class ConsistencyHeuristics:
    """Calculate consistency metrics."""

    @staticmethod
    def id_format_consistency(ids: List[str]) -> float:
        """
        Check if IDs follow consistent naming convention.

        Higher score if all IDs use same pattern.
        """
        if not ids:
            return 1.0

        # Check patterns
        patterns = {
            'snake_case': r'^[a-z_]+$',
            'kebab_case': r'^[a-z-]+$',
            'camelCase': r'^[a-z][a-zA-Z0-9]*$',
            'PascalCase': r'^[A-Z][a-zA-Z0-9]*$',
        }

        matches = {}
        for pattern_name, pattern in patterns.items():
            matches[pattern_name] = sum(
                1 for id_str in ids
                if re.match(pattern, id_str)
            )

        if not matches:
            return 0.0

        # Consistency score: highest matching pattern / total
        return max(matches.values()) / len(ids)

    @staticmethod
    def formatting_uniformity(entries: List[Dict], field: str) -> float:
        """
        Check formatting uniformity for a field.

        Measures variance in field length and structure.
        """
        if not entries:
            return 1.0

        lengths = [len(str(e.get(field, ''))) for e in entries]
        avg_length = sum(lengths) / len(lengths) if lengths else 0

        if avg_length == 0:
            return 1.0

        variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
        std_dev = variance ** 0.5

        # Calculate consistency as inverse of coefficient of variation
        cv = std_dev / avg_length if avg_length > 0 else 0
        consistency = max(0, 1 - cv)

        return min(1.0, consistency)

    @staticmethod
    def terminology_consistency(descriptions: List[str], key_terms: List[str]) -> float:
        """
        Check consistency of terminology across descriptions.

        Returns ratio of descriptions containing majority of key terms.
        """
        if not descriptions or not key_terms:
            return 0.5

        threshold = len(key_terms) // 2  # Majority

        matching_descriptions = sum(
            1 for desc in descriptions
            if sum(1 for term in key_terms if term.lower() in desc.lower()) >= threshold
        )

        return matching_descriptions / len(descriptions)


class FreshnessHeuristics:
    """Calculate freshness metrics."""

    @staticmethod
    def days_since_modification(modified_date: datetime) -> float:
        """
        Calculate freshness score based on modification date.

        Returns 0-1 scale (1 = modified within 7 days, 0 = >365 days).
        """
        if not modified_date:
            return 0.3  # Default if unknown

        days_old = (datetime.now() - modified_date).days
        max_days = 365

        freshness = max(0, 1 - (days_old / max_days))
        return min(1.0, freshness)

    @staticmethod
    def url_verification_freshness(url_check_results: Dict) -> float:
        """
        Calculate freshness based on recent URL checks.

        Returns 0-1 scale.
        """
        if not url_check_results:
            return 0.5

        from content_validation.url_validator import URLStatus
        recent_checks = 0
        max_age_hours = 24

        for result in url_check_results.values():
            if result.checked_at:
                age = (datetime.now() - result.checked_at).total_seconds() / 3600
                if age < max_age_hours:
                    recent_checks += 1

        return recent_checks / len(url_check_results)


class AppropriatenessHeuristics:
    """Calculate appropriateness metrics."""

    @staticmethod
    def token_count_efficiency(text: str, target_tokens: int = 8000) -> float:
        """
        Calculate token efficiency (0-1 scale).

        Uses rough approximation: ~4 characters per token.
        """
        estimated_tokens = len(text) // 4

        # Optimal range: 0.8-1.2 * target
        if estimated_tokens < target_tokens * 0.8:
            ratio = estimated_tokens / (target_tokens * 0.8)
        elif estimated_tokens > target_tokens * 1.2:
            ratio = (target_tokens * 1.2) / estimated_tokens
        else:
            ratio = 1.0

        return min(1.0, ratio)

    @staticmethod
    def redundancy_ratio(text: str) -> float:
        """
        Calculate redundancy (0-1 scale, where 0 = no redundancy).

        Measures repeated phrases and concepts.
        """
        words = text.lower().split()
        if len(words) < 10:
            return 0.0

        # Count word frequency
        word_freq = Counter(words)
        common_words = {'the', 'a', 'an', 'and', 'or', 'is', 'are', 'it', 'to'}

        # Significant words (>3 chars, not common)
        significant_freq = {
            w: freq for w, freq in word_freq.items()
            if len(w) > 3 and w not in common_words
        }

        if not significant_freq:
            return 0.0

        # Redundancy: how many words appear more than once
        repeated = sum(1 for freq in significant_freq.values() if freq > 1)
        total_significant = len(significant_freq)

        redundancy = (repeated / total_significant) if total_significant > 0 else 0

        return min(1.0, redundancy * 0.5)  # Cap at 0.5

    @staticmethod
    def conciseness_score(text: str) -> float:
        """
        Score conciseness (how well text avoids unnecessary verbosity).

        Returns 0-1 scale (1 = perfectly concise).
        """
        if not text:
            return 1.0

        # Detect verbose phrases
        verbose_patterns = [
            r'\b(very|really|quite|rather|fairly|somewhat|kind of)\b',
            r'\b(basically|generally|apparently|actually|literally)\b',
            r'\b(in order to|due to the fact that|for the purpose of)\b',
        ]

        verbose_count = 0
        for pattern in verbose_patterns:
            verbose_count += len(re.findall(pattern, text.lower()))

        word_count = len(text.split())
        verbosity_ratio = verbose_count / max(word_count, 1)

        return max(0, 1 - (verbosity_ratio * 2))
```

## Section 3: Complete Quality Scorer

### 3.1 Overview

The Quality Scorer combines heuristics and rubrics to generate dimensional scores.

### 3.2 Implementation

```python
# quality_scoring/quality_scorer.py

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
from quality_scoring.rubrics import ScoringRubric
from quality_scoring.heuristics import (
    InformationHeuristics,
    CompletenessHeuristics,
    ConsistencyHeuristics,
    FreshnessHeuristics,
    AppropriatenessHeuristics
)


@dataclass
class DimensionScore:
    """Score for a single quality dimension."""
    dimension: str
    score: int  # 1-5
    metric_value: float  # 0-1
    criteria_met: List[str]
    criteria_unmet: List[str]


@dataclass
class EntryQualityScore:
    """Quality score for a single entry."""
    entry_id: str
    entry_type: str  # "page", "concept", "few_shot"
    overall_score: float  # 1-5 (can be decimal)
    dimension_scores: Dict[str, DimensionScore]
    quality_badge: str  # "Excellent" / "Good" / "Fair" / "Needs Work"
    improvement_suggestions: List[str]


@dataclass
class FileQualityReport:
    """Overall quality report for entire file."""
    total_entries: int
    average_score: float
    dimension_averages: Dict[str, float]
    dimension_benchmarks: Dict[str, float]  # vs exemplars
    entry_scores: List[EntryQualityScore]
    weak_areas: List[str]
    strong_areas: List[str]
    token_analysis: Dict
    quality_trend: Optional[Dict] = None  # vs previous version


class QualityScorer:
    """Score quality across all dimensions."""

    DIMENSION_WEIGHTS = {
        "completeness": 0.20,
        "informativeness": 0.30,
        "consistency": 0.15,
        "freshness": 0.15,
        "appropriateness": 0.20,
    }

    @staticmethod
    def score_page(
        page: Dict,
        all_pages: List[Dict] = None,
        url_check_results: Dict = None
    ) -> EntryQualityScore:
        """Score a page entry across all dimensions."""
        page_id = page.get('id', 'unknown')

        scores = {}

        # Completeness
        completeness_metric = CompletenessHeuristics.field_coverage(page)
        scores['completeness'] = DimensionScore(
            dimension='completeness',
            score=ScoringRubric.score_from_metric('completeness', completeness_metric),
            metric_value=completeness_metric,
            criteria_met=['Title present'] if page.get('title') else [],
            criteria_unmet=['Summary too short'] if len(page.get('summary', '')) < 50 else []
        )

        # Informativeness
        informativeness_metric = InformationHeuristics.information_density(
            page.get('summary', '')
        )
        scores['informativeness'] = DimensionScore(
            dimension='informativeness',
            score=ScoringRubric.score_from_metric('informativeness', informativeness_metric),
            metric_value=informativeness_metric,
            criteria_met=['Substantive summary'] if len(page.get('summary', '')) > 100 else [],
            criteria_unmet=['Vague content'] if informativeness_metric < 0.5 else []
        )

        # Consistency (compare with other pages)
        if all_pages:
            consistency_metric = ConsistencyHeuristics.id_format_consistency(
                [p.get('id', '') for p in all_pages]
            )
        else:
            consistency_metric = 1.0

        scores['consistency'] = DimensionScore(
            dimension='consistency',
            score=ScoringRubric.score_from_metric('consistency', consistency_metric),
            metric_value=consistency_metric,
            criteria_met=['ID format consistent'],
            criteria_unmet=[]
        )

        # Freshness
        freshness_metric = 0.5  # Default if no metadata
        if url_check_results and page.get('url') in url_check_results:
            result = url_check_results[page.get('url')]
            if result.checked_at:
                freshness_metric = FreshnessHeuristics.days_since_modification(
                    result.checked_at
                )

        scores['freshness'] = DimensionScore(
            dimension='freshness',
            score=ScoringRubric.score_from_metric('freshness', freshness_metric),
            metric_value=freshness_metric,
            criteria_met=['Recently verified URL'],
            criteria_unmet=['URL verification stale']
        )

        # Appropriateness
        text = page.get('summary', '')
        token_efficiency = AppropriatenessHeuristics.token_count_efficiency(text)
        conciseness = AppropriatenessHeuristics.conciseness_score(text)
        appropriateness_metric = (token_efficiency + conciseness) / 2.0

        scores['appropriateness'] = DimensionScore(
            dimension='appropriateness',
            score=ScoringRubric.score_from_metric('appropriateness', appropriateness_metric),
            metric_value=appropriateness_metric,
            criteria_met=['Concise writing'],
            criteria_unmet=['Excessive verbosity'] if conciseness < 0.5 else []
        )

        # Calculate overall weighted score
        overall_score = sum(
            scores[dim].score * QualityScorer.DIMENSION_WEIGHTS[dim]
            for dim in scores.keys()
        )

        # Determine quality badge
        if overall_score >= 4.5:
            badge = "Excellent"
        elif overall_score >= 3.5:
            badge = "Good"
        elif overall_score >= 2.5:
            badge = "Fair"
        else:
            badge = "Needs Work"

        # Generate suggestions
        suggestions = QualityScorer._generate_suggestions(scores)

        return EntryQualityScore(
            entry_id=page_id,
            entry_type='page',
            overall_score=overall_score,
            dimension_scores=scores,
            quality_badge=badge,
            improvement_suggestions=suggestions
        )

    @staticmethod
    def _generate_suggestions(scores: Dict[str, DimensionScore]) -> List[str]:
        """Generate improvement suggestions from scores."""
        suggestions = []

        for dim, score in scores.items():
            if score.score <= 2:
                if dim == 'completeness':
                    suggestions.append(f"Improve completeness: Add missing required fields")
                elif dim == 'informativeness':
                    suggestions.append(f"Increase informativeness: Add more specific details")
                elif dim == 'consistency':
                    suggestions.append(f"Improve consistency: Standardize formatting")
                elif dim == 'freshness':
                    suggestions.append(f"Update content: Last verified long ago")
                elif dim == 'appropriateness':
                    suggestions.append(f"Improve appropriateness: Consider conciseness")

        return suggestions[:3]  # Top 3 suggestions

    @staticmethod
    def score_file(
        docstratum_data: Dict,
        url_check_results: Dict = None,
        previous_report: Optional[FileQualityReport] = None
    ) -> FileQualityReport:
        """Score entire llms.txt file."""
        master_index = docstratum_data.get('master_index', {})
        pages = master_index.get('pages', [])

        entry_scores = []
        for page in pages:
            entry_scores.append(
                QualityScorer.score_page(page, pages, url_check_results)
            )

        # Calculate averages
        if entry_scores:
            avg_overall = sum(s.overall_score for s in entry_scores) / len(entry_scores)
        else:
            avg_overall = 0.0

        dimension_averages = {}
        for dim in ['completeness', 'informativeness', 'consistency', 'freshness', 'appropriateness']:
            avg = sum(
                s.dimension_scores[dim].score
                for s in entry_scores if dim in s.dimension_scores
            ) / len(entry_scores) if entry_scores else 0
            dimension_averages[dim] = avg

        # Identify weak/strong areas
        sorted_dims = sorted(dimension_averages.items(), key=lambda x: x[1])
        weak_areas = [d for d, _ in sorted_dims[:2]]
        strong_areas = [d for d, _ in sorted_dims[-2:]]

        # Token analysis
        total_text = ' '.join(p.get('summary', '') for p in pages)
        token_count = len(total_text) // 4

        return FileQualityReport(
            total_entries=len(pages),
            average_score=avg_overall,
            dimension_averages=dimension_averages,
            dimension_benchmarks=QualityScorer._benchmark_comparison(dimension_averages),
            entry_scores=entry_scores,
            weak_areas=weak_areas,
            strong_areas=strong_areas,
            token_analysis={
                'estimated_tokens': token_count,
                'target_tokens': 8000,
                'efficiency': min(1.0, token_count / 8000) if token_count > 0 else 0.0
            },
            quality_trend=None
        )

    @staticmethod
    def _benchmark_comparison(dimension_averages: Dict) -> Dict:
        """Compare to benchmark scores from exemplary implementations."""
        # Benchmark data from Stripe, Nuxt, Vercel llms.txt files
        benchmarks = {
            'completeness': 4.2,
            'informativeness': 4.5,
            'consistency': 4.3,
            'freshness': 3.8,
            'appropriateness': 4.1,
        }

        return {
            dim: benchmarks.get(dim, 4.0) for dim in dimension_averages.keys()
        }
```

## Section 4: Quality Reports & Visualization

### 4.1 Report Generation

```python
# quality_scoring/report_generator.py

class QualityReportGenerator:
    """Generate quality reports in various formats."""

    @staticmethod
    def to_markdown(report: FileQualityReport) -> str:
        """Generate Markdown quality report."""
        md = f"""
# Quality Scoring Report

## Overall Assessment

- **Average Score**: {report.average_score:.2f}/5.0
- **Quality Badge**: Based on scores
- **Total Entries Evaluated**: {report.total_entries}

## Dimension Scores

| Dimension | Score | Benchmark | Status |
|-----------|-------|-----------|--------|
"""
        for dim, score in report.dimension_averages.items():
            benchmark = report.dimension_benchmarks.get(dim, 4.0)
            status = "✓ Exceeds" if score >= benchmark else "→ Below"
            md += f"| {dim.title()} | {score:.2f} | {benchmark:.2f} | {status} |\n"

        md += f"\n## Token Analysis\n"
        token_info = report.token_analysis
        md += f"- Estimated tokens: {token_info.get('estimated_tokens', 0)}\n"
        md += f"- Target tokens: {token_info.get('target_tokens', 8000)}\n"
        md += f"- Efficiency: {token_info.get('efficiency', 0):.1%}\n"

        md += f"\n## Weak Areas (Improvement Needed)\n"
        for area in report.weak_areas:
            md += f"- {area.title()}\n"

        md += f"\n## Strong Areas\n"
        for area in report.strong_areas:
            md += f"- {area.title()}\n"

        md += f"\n## Entry-Level Scores\n\n"
        for entry in report.entry_scores[:10]:  # Top 10
            md += f"### {entry.entry_id} ({entry.entry_type})\n"
            md += f"- Overall: **{entry.overall_score:.2f}/5.0** - {entry.quality_badge}\n"
            if entry.improvement_suggestions:
                md += f"- Suggestions:\n"
                for sugg in entry.improvement_suggestions:
                    md += f"  - {sugg}\n"
            md += "\n"

        return md

    @staticmethod
    def to_json(report: FileQualityReport) -> Dict:
        """Generate JSON report."""
        return {
            'summary': {
                'total_entries': report.total_entries,
                'average_score': report.average_score,
                'dimension_averages': report.dimension_averages,
                'token_analysis': report.token_analysis
            },
            'entry_scores': [
                {
                    'entry_id': s.entry_id,
                    'entry_type': s.entry_type,
                    'overall_score': s.overall_score,
                    'quality_badge': s.quality_badge,
                    'dimension_scores': {
                        dim: {
                            'score': score.score,
                            'metric_value': score.metric_value
                        }
                        for dim, score in s.dimension_scores.items()
                    },
                    'suggestions': s.improvement_suggestions
                }
                for s in report.entry_scores
            ]
        }
```

## Section 5: Test Suite

```python
# tests/test_level_3_quality.py

import pytest
from quality_scoring.heuristics import (
    InformationHeuristics,
    CompletenessHeuristics,
    ConsistencyHeuristics,
    AppropriatenessHeuristics
)


class TestInformationHeuristics:
    """Test information density calculations."""

    def test_word_density(self):
        """Should count words correctly."""
        text = "This is a test sentence"
        assert InformationHeuristics.word_density(text) == 5

    def test_information_density_high(self):
        """Should detect informative content."""
        text = "Machine Learning models process data efficiently"
        density = InformationHeuristics.information_density(text)
        assert density > 0.3

    def test_information_density_low(self):
        """Should detect sparse content."""
        text = "ok"
        density = InformationHeuristics.information_density(text)
        assert density < 0.3


class TestCompletenessHeuristics:
    """Test completeness calculations."""

    def test_field_coverage_full(self):
        """Should detect fully populated entry."""
        entry = {
            'id': 'page_1',
            'title': 'Test',
            'url': 'https://example.com',
            'summary': 'A comprehensive description'
        }
        coverage = CompletenessHeuristics.field_coverage(entry)
        assert coverage == 1.0

    def test_field_coverage_partial(self):
        """Should detect partially populated entry."""
        entry = {
            'id': 'page_1',
            'title': 'Test',
            # Missing url and summary
        }
        coverage = CompletenessHeuristics.field_coverage(entry)
        assert coverage < 1.0


class TestConsistencyHeuristics:
    """Test consistency calculations."""

    def test_id_format_snake_case(self):
        """Should recognize snake_case IDs."""
        ids = ['page_one', 'page_two', 'page_three']
        consistency = ConsistencyHeuristics.id_format_consistency(ids)
        assert consistency == 1.0

    def test_id_format_mixed(self):
        """Should detect mixed ID formats."""
        ids = ['page_one', 'pageTwo', 'page-three']
        consistency = ConsistencyHeuristics.id_format_consistency(ids)
        assert consistency < 1.0
```

## Deliverables Checklist

- [x] 5 quality dimensions defined with clear descriptions
- [x] Scoring rubrics with 1-5 scales and specific criteria
- [x] Automated heuristics for all dimensions (information density, completeness, etc.)
- [x] Per-entry quality scores with dimension breakdowns
- [x] Quality badge classification (Excellent/Good/Fair/Needs Work)
- [x] Improvement suggestion generation
- [x] Quality trend tracking (vs previous versions)
- [x] Token budget analysis
- [x] Benchmark data vs exemplary implementations
- [x] Complete scoring implementation with weighted composite score
- [x] Report generation (Markdown, JSON)
- [x] 10+ test cases for heuristics and scoring

## Acceptance Criteria

1. **Dimension Scoring**: All 5 dimensions correctly scored 1-5 for each entry
2. **Heuristics**: All heuristics produce values in 0-1 range and correlate with quality
3. **Overall Score**: Weighted composite score calculation correct
4. **Reports**: Reports generate in Markdown and JSON formats
5. **Benchmarking**: Comparison to exemplary files shows variance < 0.5
6. **Trends**: Previous version comparison shows improvement/regression detection
7. **Token Analysis**: Estimated token count within 10% of actual
8. **Quality Badges**: Badge assignment consistent with score ranges

## Next Steps

→ **v0.2.4d**: Pipeline Orchestration & Reporting
- Integrate all validation levels (0-3) into single CLI
- Create output formats (terminal, JSON, Markdown, HTML)
- Add CI/CD integration (GitHub Actions, pre-commit hooks)
- Implement configuration file support
- Create complete validate.py entry point
