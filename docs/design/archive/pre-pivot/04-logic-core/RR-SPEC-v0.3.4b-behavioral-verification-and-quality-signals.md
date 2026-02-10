# Behavioral Verification & Quality Signals

> **v0.3.4b DocStratum Agent — Logic Core**
> Defines how to automatically verify that DocStratum-enhanced responses exhibit expected behaviors and quality signals that differentiate them from the baseline agent.

## Objective

Create a verification framework that:
- Detects 5 key behavioral signals in DocStratum responses
- Scores responses on a 0-5 scale for each behavior
- Identifies false positives (baseline accidentally exhibiting behavior)
- Identifies false negatives (DocStratum failing to exhibit behavior)
- Provides actionable metrics for iterating prompt and context

## Scope Boundaries

**INCLUDES:**
- 5 key behavioral signals (with detection criteria)
- Automated verification checks (regex, NLP patterns)
- Behavioral scoring rubric (0-5 scales with examples)
- Verification test suite (20+ test scenarios)
- False positive/negative analysis
- BehaviorVerifier class with complete implementation
- Quality report generation

**EXCLUDES:**
- User satisfaction scoring (subjective)
- Cost/performance optimization
- Integration testing (covered in v0.3.4c)
- Long-term analytics storage
- Machine learning classifiers

---

## Dependency Diagram

```
AgentResponse (from v0.3.3c)
├── response.text
├── response.model
└── response.provider

→ BehaviorVerifier.analyze(response)
  ├── Check Signal 1: URL Citations
  ├── Check Signal 2: Anti-Pattern Mentions
  ├── Check Signal 3: Domain Terminology
  ├── Check Signal 4: Few-Shot Format Adherence
  └── Check Signal 5: Freshness Awareness

→ BehaviorScore (dataclass)
  ├── url_citations_score: 0-5
  ├── anti_pattern_score: 0-5
  ├── terminology_score: 0-5
  ├── format_score: 0-5
  ├── freshness_score: 0-5
  └── overall_score: 0-5 (average)
```

---

## 1. Five Key Behavioral Signals

### Signal 1: URL Citations

**Definition**: Response cites specific URLs from the documentation.

**Detection**: Look for URL patterns or reference syntax (markdown links, "source:", "documentation at").

```python
# EXAMPLES OF GOOD CITATIONS (DocStratum)
"""
As documented in https://docs.example.com/api/rest, a REST API uses...

According to [the REST guide](https://docs.example.com/guides/rest), the recommended approach...

See https://docs.example.com/api/rest#authentication for authentication details.
"""

# EXAMPLES OF NO CITATIONS (Baseline)
"""
REST APIs are commonly used for synchronous communication...

In general, best practices for API documentation include...

Typically, you would structure your API like this...
"""
```

**Why It Matters**: Shows the DocStratum agent is leveraging the injected context and directing users to authoritative sources.

### Signal 2: Anti-Pattern Mentions

**Definition**: Response explicitly mentions anti-patterns or common mistakes in the domain.

**Detection**: Keywords like "common pitfall", "anti-pattern", "don't", "avoid", "incorrect", "wrong approach".

```python
# EXAMPLES OF ANTI-PATTERN MENTIONS (DocStratum)
"""
A common mistake is... as noted in the documentation.

This is an anti-pattern in this domain: avoid hardcoding...

The incorrect approach would be..., but the proper way...

One pitfall to watch out for: many developers mistakenly...
"""

# EXAMPLES WITHOUT ANTI-PATTERNS (Baseline)
"""
You should structure your code like this...

The recommended approach is to use...

In general, it's good practice to...
"""
```

**Why It Matters**: Shows the agent has learned domain pitfalls and can help users avoid them.

### Signal 3: Domain Terminology

**Definition**: Response uses specific domain terminology from context, not generic terms.

**Detection**: Match against domain glossary extracted from llms.txt.

```python
# EXAMPLES WITH DOMAIN TERMINOLOGY (DocStratum)
"""
The event loop handles async operations asynchronously...

This follows the Repository pattern as described in...

The middleware chain processes requests through filters...

The ORM's lazy loading feature defers database queries...
"""

# EXAMPLES WITH GENERIC TERMINOLOGY (Baseline)
"""
The system handles operations in a non-blocking way...

This follows a pattern described in software engineering...

The system processes requests through multiple stages...

The library defers some database queries until accessed...
"""
```

**Why It Matters**: Shows the agent understands domain-specific concepts and can communicate at the right level.

### Signal 4: Few-Shot Format Adherence

**Definition**: Response follows patterns/structure shown in few-shot examples from domain.

**Detection**: Check response structure matches documented format (e.g., code + explanation, step-by-step, pros/cons).

```python
# EXAMPLES OF FORMAT ADHERENCE (DocStratum)
"""
[Problem statement]
[Code example from docs pattern]
[Explanation of why this works]
[Link to relevant documentation]

In this domain, the pattern is:
1. [Step 1 with specific terminology]
2. [Step 2 with specific terminology]
3. [Step 3 with specific terminology]
"""

# EXAMPLES WITHOUT STRUCTURED FORMAT (Baseline)
"""
To solve this, you can:
- Option A: do this
- Option B: do that
- Option C: do the other

The first option is usually better because...
"""
```

**Why It Matters**: Shows the agent has internalized the documentation's teaching style and structure.

### Signal 5: Freshness Awareness

**Definition**: Response acknowledges context generation date or version-specific information.

**Detection**: Keywords like "as of", "in version", "current", "updated", "recently", date references.

```python
# EXAMPLES OF FRESHNESS AWARENESS (DocStratum)
"""
As of the current version (v2.5), the recommended approach is...

This feature was added in version 3.0. Before that, you would...

As of the last documentation update in February 2025, this pattern...

The current best practice, as documented recently, is...
"""

# EXAMPLES WITHOUT FRESHNESS (Baseline)
"""
The recommended approach is...

Typically, you would use...

This is considered best practice because...
"""
```

**Why It Matters**: Shows the agent is aware of context recency and can caveat its advice appropriately.

---

## 2. Automated Verification Checks

### Pattern-Based Detection

```python
import re
from typing import List, Tuple

class PatternDetector:
    """Detect behavioral signals using regex patterns"""

    # URL detection patterns
    URL_PATTERNS = [
        r'https?://[^\s\)]+',                    # Direct URLs
        r'\[([^\]]+)\]\(https?://[^\)]+\)',      # Markdown links
        r'(source|documentation|docs|ref)[:\s]+(https?://[^\s\)]+)',  # "source: URL"
        r'(see|check|visit)[:\s]+(https?://[^\s\)]+)',                # "see: URL"
    ]

    # Anti-pattern keywords
    ANTI_PATTERN_KEYWORDS = [
        r'\b(anti-?pattern|common\s+mistake|pitfall|avoid|don\'t|don\'t|incorrect|wrong\s+approach)\b',
        r'\b(not\s+recommended|not\s+the\s+way|incorrect|bad\s+practice)\b',
        r'\b(many\s+developers?\s+mistakenly|don\'t\s+use|don\'t\s+do)\b',
    ]

    # Domain-specific terms (loaded from context)
    DOMAIN_TERMS = []

    # Freshness keywords
    FRESHNESS_KEYWORDS = [
        r'\b(as\s+of|in\s+version|current|updated|recent|since|v\d+\.\d+)\b',
        r'\b(2024|2025|January|February|March|April|May|June|July|August|September|October|November|December)\b',
        r'\b(this\s+version|the\s+latest|as\s+documented)\b',
    ]

    @staticmethod
    def find_urls(text: str) -> List[str]:
        """Extract all URLs from text"""
        urls = []
        for pattern in PatternDetector.URL_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            urls.extend([m if isinstance(m, str) else m[0] for m in matches])
        return list(set(urls))  # Remove duplicates

    @staticmethod
    def find_anti_patterns(text: str) -> List[Tuple[str, str]]:
        """Find anti-pattern mentions with context"""
        matches = []
        for pattern in PatternDetector.ANTI_PATTERN_KEYWORDS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                # Get surrounding context (50 chars before/after)
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end]
                matches.append((match.group(), context))
        return matches

    @staticmethod
    def find_domain_terms(text: str, domain_terms: List[str]) -> List[str]:
        """Find domain-specific terminology usage"""
        found_terms = []
        for term in domain_terms:
            # Case-insensitive word-boundary search
            pattern = rf'\b{re.escape(term)}\b'
            if re.search(pattern, text, re.IGNORECASE):
                found_terms.append(term)
        return found_terms

    @staticmethod
    def find_freshness_indicators(text: str) -> List[str]:
        """Find freshness/recency indicators"""
        indicators = []
        for pattern in PatternDetector.FRESHNESS_KEYWORDS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                indicators.append(match.group())
        return indicators

    @staticmethod
    def extract_domain_terms_from_context(context: str) -> List[str]:
        """
        Extract domain terms from llms.txt context for later matching.

        Strategy: Pull terms from code examples and technical sections.
        """
        terms = []

        # Extract from code blocks
        code_pattern = r'```[a-z]*\n(.+?)\n```'
        for match in re.finditer(code_pattern, context, re.DOTALL | re.IGNORECASE):
            code = match.group(1)
            # Extract identifiers (camelCase, snake_case, PascalCase)
            identifiers = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', code)
            terms.extend(identifiers)

        # Extract from bold/emphasized text
        emphasized = re.findall(r'\*\*([^*]+)\*\*', context)
        terms.extend(emphasized)

        # Extract from headings
        headings = re.findall(r'^#+\s+(.+)$', context, re.MULTILINE)
        terms.extend([h.lower() for h in headings])

        return list(set([t for t in terms if len(t) > 3]))  # Unique, meaningful terms
```

---

## 3. Behavioral Scoring Rubric

### Score Scale (0-5)

```python
from dataclasses import dataclass
from enum import Enum

class ScoreLevel(Enum):
    NONE = 0         # Signal completely absent
    MINIMAL = 1      # Trace amounts, likely accidental
    WEAK = 2         # Present but infrequent or weak
    MODERATE = 3     # Clearly present, appropriate usage
    STRONG = 4       # Frequent, well-integrated
    EXCELLENT = 5    # Pervasive, perfectly integrated

@dataclass
class BehaviorScore:
    """Scoring for one behavioral signal"""
    signal_name: str
    score: int  # 0-5
    evidence: List[str]  # Examples supporting the score
    notes: str  # Explanation

    def __str__(self) -> str:
        level = ScoreLevel(self.score).name
        return f"{self.signal_name}: {self.score}/5 ({level})"

@dataclass
class ResponseBehavior:
    """Complete behavior analysis for a response"""
    url_citations: BehaviorScore
    anti_patterns: BehaviorScore
    domain_terminology: BehaviorScore
    format_adherence: BehaviorScore
    freshness_awareness: BehaviorScore

    @property
    def overall_score(self) -> float:
        """Average of all behavior scores"""
        scores = [
            self.url_citations.score,
            self.anti_patterns.score,
            self.domain_terminology.score,
            self.format_adherence.score,
            self.freshness_awareness.score
        ]
        return sum(scores) / len(scores)

    def summary(self) -> str:
        """One-line summary of response behavior"""
        return f"""
Overall: {self.overall_score:.1f}/5
- Citations: {self.url_citations.score}/5
- Anti-patterns: {self.anti_patterns.score}/5
- Terminology: {self.domain_terminology.score}/5
- Format: {self.format_adherence.score}/5
- Freshness: {self.freshness_awareness.score}/5
"""
```

### Scoring Criteria Examples

#### URL Citations Scoring

| Score | Criteria | Example |
|-------|----------|---------|
| **0** | No URLs cited | "REST APIs are useful..." |
| **1** | URL mentioned but vague | "See the docs for details" |
| **2** | 1 URL cited, no context | "https://example.com/docs" |
| **3** | 1-2 URLs clearly cited | "According to [docs](URL), ..." |
| **4** | 3+ URLs naturally integrated | Multiple source citations throughout |
| **5** | URLs contextually specific | Each section cites relevant URL |

#### Anti-Pattern Scoring

| Score | Criteria | Example |
|-------|----------|---------|
| **0** | No anti-patterns mentioned | Generic best practices only |
| **1** | Minimal mention, unclear | "Some people do it wrong" |
| **2** | 1-2 anti-patterns, basic | "Don't hardcode values" |
| **3** | 2-3 clear anti-patterns | "Common mistake: X. Avoid Y..." |
| **4** | 4+ domain-specific anti-patterns | Anti-patterns integrated naturally |
| **5** | Comprehensive anti-pattern coverage | Pitfalls explained with context |

#### Domain Terminology Scoring

| Score | Criteria | Example |
|-------|----------|---------|
| **0** | Only generic terms | "use system", "do operation" |
| **1** | 1-2 domain terms used | "the API" mixed with generic |
| **2** | 3-5 domain terms | Some domain language, mostly generic |
| **3** | 6-10 domain terms naturally | Good balance of specific/accessible |
| **4** | 10+ domain terms, precise | Fluent in domain terminology |
| **5** | Expert-level terminology | Sophisticated domain language |

---

## 4. Verification Test Suite

### Test Structure

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class VerificationTest:
    """One verification test case"""
    question: str
    expected_signals: List[str]  # Which signals should be present
    context_hint: Optional[str] = None  # Hint about what context is relevant
    difficulty: str = "moderate"  # easy, moderate, hard

class VerificationTestSuite:
    """Complete suite of behavioral verification tests"""

    TESTS = [
        # EASY: Should definitely work
        VerificationTest(
            question="What is the core purpose of this system?",
            expected_signals=["url_citations", "domain_terminology"],
            difficulty="easy"
        ),

        VerificationTest(
            question="What are the main components?",
            expected_signals=["domain_terminology", "format_adherence"],
            difficulty="easy"
        ),

        # MODERATE: Should work well
        VerificationTest(
            question="How should I get started with this?",
            expected_signals=["url_citations", "format_adherence", "anti_patterns"],
            difficulty="moderate"
        ),

        VerificationTest(
            question="What's the best way to handle authentication?",
            expected_signals=["url_citations", "anti_patterns", "domain_terminology"],
            difficulty="moderate"
        ),

        VerificationTest(
            question="What are common mistakes when using this?",
            expected_signals=["anti_patterns", "url_citations", "freshness_awareness"],
            difficulty="moderate"
        ),

        # HARD: Should still do well
        VerificationTest(
            question="How does this compare to alternatives?",
            expected_signals=["domain_terminology", "anti_patterns"],
            difficulty="hard"
        ),

        VerificationTest(
            question="What's changed recently in this domain?",
            expected_signals=["freshness_awareness", "url_citations"],
            difficulty="hard"
        ),

        # BOUNDARY CASES
        VerificationTest(
            question="Tell me a joke about this domain",
            expected_signals=[],  # Shouldn't claim domain expertise for non-questions
            difficulty="hard"
        ),

        VerificationTest(
            question="How does this relate to quantum computing?",
            expected_signals=["freshness_awareness"],  # Only acknowledge limits
            difficulty="hard"
        ),
    ]

    @classmethod
    def run_all(cls, agent, domain_terms: List[str]) -> List[Tuple[str, ResponseBehavior]]:
        """Run all tests against an agent"""
        verifier = BehaviorVerifier(domain_terms)
        results = []

        for test in cls.TESTS:
            response = agent.invoke(test.question)
            behavior = verifier.analyze(response, test.expected_signals)
            results.append((test.question, behavior))

        return results
```

---

## 5. BehaviorVerifier Class

### Complete Implementation

```python
class BehaviorVerifier:
    """Analyze and score agent response behaviors"""

    def __init__(self, domain_terms: List[str], context_block: str = ""):
        self.domain_terms = domain_terms
        self.context_block = context_block
        self.detector = PatternDetector()

    def analyze(
        self,
        response: 'AgentResponse',
        expected_signals: Optional[List[str]] = None
    ) -> ResponseBehavior:
        """
        Analyze response for all behavioral signals.

        Args:
            response: AgentResponse from agent.invoke()
            expected_signals: Which signals we expect (for scoring context)

        Returns:
            ResponseBehavior with scores for all signals
        """

        text = response.response

        # Analyze each signal
        citations_score = self._score_url_citations(text)
        anti_pattern_score = self._score_anti_patterns(text)
        terminology_score = self._score_domain_terminology(text)
        format_score = self._score_format_adherence(text)
        freshness_score = self._score_freshness_awareness(text)

        # Build behavior object
        behavior = ResponseBehavior(
            url_citations=citations_score,
            anti_patterns=anti_pattern_score,
            domain_terminology=terminology_score,
            format_adherence=format_score,
            freshness_awareness=freshness_score
        )

        return behavior

    def _score_url_citations(self, text: str) -> BehaviorScore:
        """Score URL citation presence and quality"""
        urls = self.detector.find_urls(text)

        if len(urls) == 0:
            evidence = ["No URLs found in response"]
            score = 0
        elif len(urls) == 1:
            # Check if URL is generic vs. specific
            if "example.com" in urls[0] or "http" not in str(urls[0]):
                score = 1
            else:
                score = 3
            evidence = urls
        else:  # Multiple URLs
            score = 4 if len(urls) >= 3 else 3
            evidence = urls[:3]  # Show first 3

        return BehaviorScore(
            signal_name="URL Citations",
            score=score,
            evidence=evidence,
            notes=f"Found {len(urls)} URL(s) in response"
        )

    def _score_anti_patterns(self, text: str) -> BehaviorScore:
        """Score anti-pattern mentions"""
        anti_patterns = self.detector.find_anti_patterns(text)

        if len(anti_patterns) == 0:
            score = 0
            evidence = ["No anti-pattern keywords detected"]
        elif len(anti_patterns) == 1:
            score = 2
            evidence = [anti_patterns[0][0]]
        elif len(anti_patterns) <= 3:
            score = 3
            evidence = [ap[0] for ap in anti_patterns[:3]]
        else:
            score = 4
            evidence = [ap[0] for ap in anti_patterns[:5]]

        return BehaviorScore(
            signal_name="Anti-Pattern Mentions",
            score=score,
            evidence=evidence,
            notes=f"Found {len(anti_patterns)} anti-pattern mention(s)"
        )

    def _score_domain_terminology(self, text: str) -> BehaviorScore:
        """Score domain terminology usage"""
        found_terms = self.detector.find_domain_terms(text, self.domain_terms)

        if len(found_terms) == 0:
            score = 0
        elif len(found_terms) <= 2:
            score = 2
        elif len(found_terms) <= 5:
            score = 3
        elif len(found_terms) <= 10:
            score = 4
        else:
            score = 5

        return BehaviorScore(
            signal_name="Domain Terminology",
            score=score,
            evidence=found_terms[:5],  # Show first 5
            notes=f"Found {len(found_terms)} domain term(s) out of {len(self.domain_terms)} total"
        )

    def _score_format_adherence(self, text: str) -> BehaviorScore:
        """Score response format/structure quality"""
        score = 0
        evidence = []

        # Check for structured sections
        has_headings = bool(re.search(r'^(#+|##|###)', text, re.MULTILINE))
        has_lists = bool(re.search(r'^[\s]*[-*]\s', text, re.MULTILINE))
        has_code = bool(re.search(r'```', text))
        has_numbers = bool(re.search(r'^\d+\.', text, re.MULTILINE))

        structure_elements = [
            ("Headings", has_headings),
            ("Lists", has_lists),
            ("Code blocks", has_code),
            ("Numbered items", has_numbers),
        ]

        for name, present in structure_elements:
            if present:
                score += 1
                evidence.append(name)

        # Normalize to 0-5 scale
        score = min(5, score)

        return BehaviorScore(
            signal_name="Format Adherence",
            score=score,
            evidence=evidence,
            notes=f"Found {len(evidence)} structural element(s)"
        )

    def _score_freshness_awareness(self, text: str) -> BehaviorScore:
        """Score freshness/recency awareness"""
        indicators = self.detector.find_freshness_indicators(text)

        if len(indicators) == 0:
            score = 0
            evidence = ["No freshness indicators found"]
        elif len(indicators) == 1:
            score = 2
            evidence = indicators
        elif len(indicators) <= 3:
            score = 3
            evidence = indicators
        else:
            score = 4
            evidence = indicators[:3]

        return BehaviorScore(
            signal_name="Freshness Awareness",
            score=score,
            evidence=evidence,
            notes=f"Found {len(indicators)} freshness indicator(s)"
        )
```

---

## 6. False Positive/Negative Analysis

### Identifying Edge Cases

```python
def identify_false_positives(
    baseline_behaviors: List[ResponseBehavior],
    test_suite: VerificationTestSuite
) -> List[str]:
    """
    Identify cases where baseline accidentally scores high.

    Returns list of problem cases and recommendations.
    """
    issues = []

    for i, behavior in enumerate(baseline_behaviors):
        test = test_suite.TESTS[i]

        # Check if baseline scores too high on unexpected signals
        for signal_name in test.expected_signals:
            signal = getattr(behavior, signal_name.lower().replace("-", "_"))
            if signal.score >= 3:  # Unexpectedly high
                issues.append(
                    f"Test '{test.question}': "
                    f"Baseline scored {signal.score}/5 on {signal_name} "
                    f"(expected low due to no context)"
                )

    return issues

def identify_false_negatives(
    docstratum_behaviors: List[ResponseBehavior],
    test_suite: VerificationTestSuite
) -> List[str]:
    """
    Identify cases where DocStratum fails to score high.

    Returns list of problem cases and recommendations.
    """
    issues = []

    for i, behavior in enumerate(docstratum_behaviors):
        test = test_suite.TESTS[i]

        # Check if DocStratum scores low on expected signals
        for signal_name in test.expected_signals:
            signal = getattr(behavior, signal_name.lower().replace("-", "_"))
            if signal.score <= 2:  # Unexpectedly low
                issues.append(
                    f"Test '{test.question}': "
                    f"DocStratum scored {signal.score}/5 on {signal_name} "
                    f"(expected high for: {signal_name})"
                )

    return issues
```

---

## 7. Quality Report Generation

### Report Template

```python
def generate_quality_report(
    baseline_results: List[Tuple[str, ResponseBehavior]],
    docstratum_results: List[Tuple[str, ResponseBehavior]]
) -> str:
    """Generate comprehensive quality comparison report"""

    report = """
═══════════════════════════════════════════════════════════════════════════════
                    BEHAVIORAL VERIFICATION REPORT
                    v0.3.3 Baseline vs v0.3.4 DocStratum
═══════════════════════════════════════════════════════════════════════════════

EXECUTIVE SUMMARY
────────────────────────────────────────────────────────────────────────────────
"""

    # Calculate averages
    baseline_avg = sum(r[1].overall_score for r in baseline_results) / len(baseline_results)
    docstratum_avg = sum(r[1].overall_score for r in docstratum_results) / len(docstratum_results)
    improvement = ((docstratum_avg - baseline_avg) / baseline_avg * 100) if baseline_avg > 0 else 0

    report += f"""
Baseline Overall Score:  {baseline_avg:.2f}/5.0
DocStratum Overall Score:   {docstratum_avg:.2f}/5.0
Improvement:             +{improvement:.1f}%

"""

    # By-signal analysis
    report += """DETAILED SIGNAL ANALYSIS
────────────────────────────────────────────────────────────────────────────────

"""

    signals = ["url_citations", "anti_patterns", "domain_terminology", "format_adherence", "freshness_awareness"]

    for signal in signals:
        baseline_scores = [getattr(r[1], signal).score for r in baseline_results]
        docstratum_scores = [getattr(r[1], signal).score for r in docstratum_results]

        baseline_mean = sum(baseline_scores) / len(baseline_scores)
        docstratum_mean = sum(docstratum_scores) / len(docstratum_scores)

        report += f"""
{signal.upper().replace("_", " ")}
  Baseline: {baseline_mean:.2f}/5.0
  DocStratum:  {docstratum_mean:.2f}/5.0
  Delta:    {docstratum_mean - baseline_mean:+.2f}

"""

    report += """
TEST-BY-TEST RESULTS
────────────────────────────────────────────────────────────────────────────────
"""

    for (question, baseline_behavior), (_, docstratum_behavior) in zip(baseline_results, docstratum_results):
        report += f"""
Q: {question}
  Baseline: {baseline_behavior.overall_score:.1f}/5.0
  DocStratum:  {docstratum_behavior.overall_score:.1f}/5.0
  Difference: {docstratum_behavior.overall_score - baseline_behavior.overall_score:+.1f}

"""

    report += """
═══════════════════════════════════════════════════════════════════════════════
"""

    return report
```

---

## Deliverables

1. **Five behavioral signals** defined with detection criteria
2. **PatternDetector class** with regex patterns for all signals
3. **BehaviorScore and ResponseBehavior dataclasses**
4. **Scoring rubric** with 0-5 scale for each signal
5. **VerificationTestSuite** with 20+ test cases
6. **BehaviorVerifier class** with complete scoring implementation
7. **False positive/negative detection functions**
8. **Quality report generation**

---

## Acceptance Criteria

- [ ] All 5 behavioral signals have clear detection criteria
- [ ] BehaviorVerifier.analyze() returns ResponseBehavior for any response
- [ ] Scoring is consistent (same input → same score)
- [ ] Baseline responses score 0-1 on domain-specific signals
- [ ] DocStratum responses score 3+ on domain-specific signals
- [ ] False positive cases are identified and documented
- [ ] False negative cases are identified and documented
- [ ] Quality report shows significant improvement (DocStratum > Baseline)
- [ ] All 20+ test cases run without errors
- [ ] Overall score accurately averages 5 signals

---

## Next Step

**v0.3.4c — Integration Testing & End-to-End Pipeline** will use these behavioral verification checks to build a complete integration test suite that validates the entire baseline → DocStratum pipeline.
