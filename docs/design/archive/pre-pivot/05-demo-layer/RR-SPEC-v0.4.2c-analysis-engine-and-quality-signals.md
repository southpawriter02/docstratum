# v0.4.2c — Analysis Engine & Quality Signals

> **Task:** Build the automated analysis engine that detects quality improvements in DocStratum responses. Establish signal detection methodology, quality metrics, and extensibility patterns for identifying citations, anti-patterns, code examples, and other quality indicators.

---

## Objective

Implement the render_analysis() component that performs automated analysis of responses to detect and display quality signals. This sub-part defines the signal detection methodology, establishes a catalog of detectable signals (citations, anti-patterns, code examples, source quality), implements signal scoring algorithms, and provides extensibility patterns for adding new signal types. By creating a structured analysis engine, we enable comparative quality assessment that guides users toward more reliable responses while demonstrating DocStratum's semantic enhancement value.

---

## Scope Boundaries

| **In Scope** | **Out of Scope** |
|---|---|
| render_analysis() function implementation | Machine learning-based quality assessment |
| Citation detection (URL analysis) | Manual curation or expert review systems |
| Anti-pattern detection (keyword matching) | Statistical significance testing |
| Code example detection (code block presence) | Performance benchmarking of responses |
| Signal scoring methodology | User preference learning |
| Signal visualization and display | A/B testing statistical analysis |
| Extensibility patterns for new signals | Backend response evaluation systems |
| Signal detection accuracy considerations | Caching or state persistence |
| Rendering quality signal results | Integration with external grading services |
| Detection configuration and tuning | Database schema for signal storage |

---

## Dependency Diagram

```
┌─────────────────────────────────────────────────────┐
│           render_analysis() Component                │
└─────────────────────┬───────────────────────────────┘
                      │
    ┌─────────────────┼─────────────────┐
    │                 │                 │
    ▼                 ▼                 ▼
 Input Data      Signal Processors   Output Rendering
 ├─ baseline_    ├─ citation_         │
 │  response     │  detector()        ├─ Signal cards
 ├─ docstratum_     ├─ antipattern_      ├─ Signal scores
 │  response     │  detector()        ├─ Quality summary
 └─ config       ├─ code_example_     └─ Improvement %
                 │  detector()
                 ├─ source_quality_
                 │  detector()
                 └─ signal_scorer()

Signal Detectors (Parallel Processing)
├─ Citation Detector
│  └─ Input: Response text
│  └─ Detection: URL parsing, presence analysis
│  └─ Output: citation_count, confidence
│
├─ Anti-Pattern Detector
│  └─ Input: Response text
│  └─ Detection: Keyword matching against pattern library
│  └─ Output: patterns_found, severity
│
├─ Code Example Detector
│  └─ Input: Response text
│  └─ Detection: Code block counting (```)
│  └─ Output: code_block_count, languages
│
└─ Source Quality Detector
   └─ Input: Citations (URLs)
   └─ Detection: Domain reputation, TLD analysis
   └─ Output: source_quality_score
```

---

## 1. render_analysis() Design and Signal Detection

### 1.1 Function Signature

```python
def render_analysis(
    baseline_response: dict,
    docstratum_response: dict,
    analysis_config: dict = None,
    show_detailed: bool = True
) -> None:
    """
    Render quality signal analysis comparing baseline and docstratum responses.

    Args:
        baseline_response: Baseline response dict with 'text', 'tokens', 'latency'
        docstratum_response: DocStratum response dict with same structure
        analysis_config: Optional dict with signal detection parameters
        show_detailed: If True, show signal details; else show summary only

    Side Effects:
        Renders analysis section with detected signals to Streamlit

    Raises:
        ValueError: If responses missing required keys
        TypeError: If parameters have incorrect types
    """
    # 1. Validate inputs
    # 2. Initialize signal detector engine
    # 3. Detect signals in both responses
    # 4. Score signals and compute improvements
    # 5. Render signal comparison visualization
    # 6. Display quality metrics and summary
```

### 1.2 Analysis Execution Flow

```
1. Input validation
        ↓
2. Extract response texts
        ↓
3. Initialize signal detectors (citations, patterns, code, sources)
        ↓
4. Run detectors on baseline_response.text in parallel
        ↓
5. Run detectors on docstratum_response.text in parallel
        ↓
6. Aggregate detected signals into signal dictionaries
        ↓
7. Score signals (presence, quality, improvement)
        ↓
8. Calculate improvement metrics
        ↓
9. Render signal cards with visual indicators
        ↓
10. Display overall quality summary
```

### 1.3 Detector Architecture

```python
class SignalDetector:
    """Base class for signal detectors."""

    def detect(self, text: str) -> dict:
        """
        Detect signals in text.

        Args:
            text: Response text to analyze

        Returns:
            Dict with detection results: {
                'signal_type': str,
                'detected': bool,
                'count': int,
                'details': dict,
                'confidence': float (0.0-1.0)
            }
        """
        raise NotImplementedError

class CitationDetector(SignalDetector):
    """Detects citations and source references."""

    def detect(self, text: str) -> dict:
        # Implementation in section 2

class AntiPatternDetector(SignalDetector):
    """Detects problematic patterns and language."""

    def detect(self, text: str) -> dict:
        # Implementation in section 3

class CodeExampleDetector(SignalDetector):
    """Detects code blocks and examples."""

    def detect(self, text: str) -> dict:
        # Implementation in section 4

class SourceQualityDetector(SignalDetector):
    """Evaluates quality of cited sources."""

    def detect(self, text: str) -> dict:
        # Implementation in section 5
```

---

## 2. Citation Detection (URL Presence Analysis)

### 2.1 Citation Detection Strategy

Citations indicate responses grounded in external sources. Detecting citations suggests responses are evidence-based.

```python
import re
from urllib.parse import urlparse

class CitationDetector(SignalDetector):
    """Detect citations, links, and source references."""

    # URL pattern: matches http/https URLs
    URL_PATTERN = r'https?://[^\s\)\]\}]+'

    # Markdown link pattern: [text](url)
    MARKDOWN_LINK_PATTERN = r'\[([^\]]+)\]\(([^\)]+)\)'

    # Reference pattern: (source: url) or similar
    REFERENCE_PATTERN = r'\((?:source|see|ref|reference):\s*([^\)]+)\)'

    def detect(self, text: str) -> dict:
        """
        Detect citations in response text.

        Args:
            text: Response text to analyze

        Returns:
            Detection result dict
        """
        citations = self._find_citations(text)

        return {
            'signal_type': 'citations',
            'detected': len(citations) > 0,
            'count': len(citations),
            'details': {
                'urls': citations,
                'domains': [self._extract_domain(url) for url in citations]
            },
            'confidence': 0.95 if citations else 0.0
        }

    def _find_citations(self, text: str) -> list:
        """Extract all citations from text."""
        citations = []

        # Find standard URLs
        urls = re.findall(self.URL_PATTERN, text)
        citations.extend(urls)

        # Find markdown links
        markdown_links = re.findall(self.MARKDOWN_LINK_PATTERN, text)
        citations.extend([url for _, url in markdown_links])

        # Find reference citations
        references = re.findall(self.REFERENCE_PATTERN, text)
        citations.extend(references)

        # Remove duplicates
        return list(set(citations))

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            # Remove www. prefix
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except:
            return url
```

### 2.2 Citation Quality Metrics

| Citation Type | Quality Indicator | Confidence |
|---|---|---|
| Academic domain (.edu, .org) | High authority | 0.95 |
| Standard domain (.com, .net) | Medium authority | 0.80 |
| Government domain (.gov) | High authority | 0.95 |
| Personal blog, wiki | Lower authority | 0.60 |
| GitHub, technical repos | High for tech | 0.90 |

### 2.3 Citation Detection Examples

```python
# Example 1: Standard URL
text = "For more information, see https://example.com/docs"
# Detected: ['https://example.com/docs']

# Example 2: Markdown link
text = "Read this [helpful guide](https://guide.example.com)"
# Detected: ['https://guide.example.com']

# Example 3: Reference notation
text = "According to research (source: https://study.example.edu)"
# Detected: ['https://study.example.edu']

# Example 4: Multiple citations
text = """
Research from https://source1.com and [source 2](https://source2.org)
shows that (source: https://source3.com) this is valid.
"""
# Detected: ['https://source1.com', 'https://source2.org', 'https://source3.com']
```

---

## 3. Anti-Pattern Detection (Keyword Matching)

### 3.1 Anti-Pattern Library

Anti-patterns are indicators of lower-quality responses. Detecting their absence is a positive signal.

```python
class AntiPatternDetector(SignalDetector):
    """Detect problematic patterns and anti-patterns in responses."""

    # Anti-pattern keyword groups
    ANTI_PATTERNS = {
        "uncertainty": [
            "i don't know",
            "i'm not sure",
            "unclear",
            "not entirely certain",
            "hard to say"
        ],
        "hallucination_risk": [
            "probably",
            "maybe",
            "might be",
            "possibly",
            "could potentially"
        ],
        "vague_language": [
            "sort of",
            "kind of",
            "somewhat",
            "seems like",
            "appears to"
        ],
        "deflection": [
            "depends on context",
            "it depends",
            "varies by",
            "there's no universal answer",
            "this is subjective"
        ],
        "incomplete": [
            "beyond the scope",
            "outside my expertise",
            "you should ask",
            "you'll need to",
            "consult an expert"
        ]
    }

    def detect(self, text: str) -> dict:
        """
        Detect anti-patterns in response.

        Args:
            text: Response text to analyze

        Returns:
            Detection result dict
        """
        text_lower = text.lower()
        found_patterns = {}

        for pattern_group, keywords in self.ANTI_PATTERNS.items():
            matches = []
            for keyword in keywords:
                if keyword in text_lower:
                    matches.append(keyword)

            if matches:
                found_patterns[pattern_group] = {
                    'count': len(matches),
                    'keywords': matches
                }

        has_antipatterns = len(found_patterns) > 0

        return {
            'signal_type': 'anti_patterns',
            'detected': has_antipatterns,
            'count': len(found_patterns),
            'details': found_patterns,
            'confidence': 0.85 if has_antipatterns else 0.0
        }
```

### 3.2 Anti-Pattern Severity Scoring

```python
def score_antipattern_severity(patterns: dict) -> float:
    """
    Score severity of detected anti-patterns.

    Args:
        patterns: Dict of detected anti-patterns from detector

    Returns:
        Severity score (0.0 = no issues, 1.0 = severe)
    """
    severity_weights = {
        "uncertainty": 0.7,        # Most problematic
        "hallucination_risk": 0.8,
        "vague_language": 0.5,
        "deflection": 0.6,
        "incomplete": 0.7
    }

    if not patterns:
        return 0.0

    # Calculate weighted average
    total_weight = sum(severity_weights.get(k, 0.5) * v['count']
                       for k, v in patterns.items())
    max_weight = sum(w for w in severity_weights.values())

    return min(total_weight / max_weight, 1.0)
```

### 3.3 Anti-Pattern Detection Examples

```python
# Example 1: No anti-patterns
text = "Python uses indentation to define code blocks."
# Detected: No patterns found, confidence: 0.0

# Example 2: Uncertainty anti-pattern
text = "I'm not sure, but it might be that Python uses indentation."
# Detected: ['uncertainty', 'hallucination_risk']
# Severity: 0.75

# Example 3: Deflection anti-pattern
text = "It depends on context, but generally Python uses indentation."
# Detected: ['deflection']
# Severity: 0.6
```

---

## 4. Code Example Detection (Code Block Presence)

### 4.1 Code Block Detection

```python
import re

class CodeExampleDetector(SignalDetector):
    """Detect code examples, blocks, and technical content."""

    # Fenced code block pattern: ```language ... ```
    FENCED_CODE_PATTERN = r'```(\w*)\n(.*?)\n```'

    # Inline code pattern: `code`
    INLINE_CODE_PATTERN = r'`[^`]+`'

    # Keyword patterns for specific languages
    LANGUAGE_KEYWORDS = {
        'python': ['def ', 'import ', 'class ', 'if __name__'],
        'javascript': ['function ', 'const ', 'let ', 'async '],
        'sql': ['SELECT ', 'FROM ', 'WHERE ', 'INSERT '],
        'html': ['<html>', '<body>', '<div>', '<script>'],
        'bash': ['#!/bin/bash', '$', 'echo ', 'for ']
    }

    def detect(self, text: str) -> dict:
        """
        Detect code examples in response.

        Args:
            text: Response text to analyze

        Returns:
            Detection result dict
        """
        # Find fenced code blocks
        fenced_blocks = re.findall(self.FENCED_CODE_PATTERN, text, re.DOTALL)
        fenced_count = len(fenced_blocks)

        # Find inline code
        inline_code = re.findall(self.INLINE_CODE_PATTERN, text)
        inline_count = len(inline_code)

        # Detect languages
        languages = self._detect_languages(fenced_blocks)

        has_code = fenced_count > 0 or inline_count > 0

        return {
            'signal_type': 'code_examples',
            'detected': has_code,
            'count': fenced_count,
            'details': {
                'fenced_blocks': fenced_count,
                'inline_code': inline_count,
                'languages': languages,
                'total_code_elements': fenced_count + inline_count
            },
            'confidence': 0.95 if has_code else 0.0
        }

    def _detect_languages(self, fenced_blocks: list) -> list:
        """Detect programming languages in code blocks."""
        languages = []

        for lang_hint, block_content in fenced_blocks:
            if lang_hint:
                # Language was explicitly specified
                languages.append(lang_hint.lower())
            else:
                # Try to infer from content
                inferred = self._infer_language(block_content)
                if inferred:
                    languages.append(inferred)

        return list(set(languages))  # Remove duplicates

    def _infer_language(self, code_content: str) -> str:
        """Infer programming language from code content."""
        content_lower = code_content.lower()

        for lang, keywords in self.LANGUAGE_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw.lower() in content_lower)
            if matches >= 2:  # At least 2 keywords match
                return lang

        return None
```

### 4.2 Code Example Quality Scoring

```python
def score_code_example_quality(code_detection: dict) -> float:
    """
    Score quality of code examples.

    Args:
        code_detection: Detection result from CodeExampleDetector

    Returns:
        Quality score (0.0 = no code, 1.0 = high quality)
    """
    details = code_detection['details']

    fenced_count = details['fenced_blocks']
    inline_count = details['inline_code']
    language_count = len(details['languages'])

    # Scoring logic:
    # - Fenced blocks with language specification: high quality
    # - Inline code: lower weight
    # - Multiple languages: shows comprehensive examples

    fenced_score = min(fenced_count * 0.4, 1.0)  # Each block: +0.4
    inline_score = min(inline_count * 0.1, 0.3)  # Each inline: +0.1, max 0.3
    language_bonus = min(language_count * 0.1, 0.3)  # Variety bonus

    total_score = fenced_score + inline_score + language_bonus

    return min(total_score, 1.0)
```

### 4.3 Code Detection Examples

```python
# Example 1: Fenced code block
text = """
Here's how to use Python:

```python
def hello_world():
    print("Hello, World!")
```

This function prints a greeting.
"""
# Detected: fenced_blocks=1, languages=['python'], inline_code=0

# Example 2: Multiple examples
text = """
JavaScript function:
```javascript
function add(a, b) {
  return a + b;
}
```

Or using Python:
```python
def add(a, b):
    return a + b
```
"""
# Detected: fenced_blocks=2, languages=['javascript', 'python']

# Example 3: Inline code
text = "Use `console.log()` to debug JavaScript."
# Detected: fenced_blocks=0, inline_code=1
```

---

## 5. Source Quality Detector

### 5.1 Source Quality Scoring

```python
class SourceQualityDetector(SignalDetector):
    """Evaluate quality of cited sources."""

    # Authority scores by domain type
    DOMAIN_AUTHORITY = {
        '.edu': 0.95,      # Educational institutions
        '.gov': 0.95,      # Government
        '.org': 0.85,      # Organizations
        '.ac.uk': 0.95,    # UK academic
        '.ac.jp': 0.95,    # Japan academic
        '.com': 0.70,      # Commercial (varies)
        '.io': 0.70,       # Tech/startup
        '.co.uk': 0.75,    # UK commercial
    }

    # Trusted domains (high reputation)
    TRUSTED_DOMAINS = [
        'github.com',
        'stackoverflow.com',
        'wikipedia.org',
        'medium.com',
        'arxiv.org',
        'researchgate.net',
        'docs.python.org',
        'developer.mozilla.org',
        'www.w3.org',
        'openai.com'
    ]

    # Unreliable patterns
    UNRELIABLE_PATTERNS = [
        'random',
        'spam',
        'clickbait',
        'temporary',
        'cache'
    ]

    def detect(self, text: str) -> dict:
        """
        Evaluate quality of sources cited in text.

        Args:
            text: Response text with potential citations

        Returns:
            Detection result dict
        """
        # Find URLs using CitationDetector
        citation_detector = CitationDetector()
        citation_result = citation_detector.detect(text)

        if not citation_result['detected']:
            return {
                'signal_type': 'source_quality',
                'detected': False,
                'count': 0,
                'details': {'sources': [], 'average_quality': 0.0},
                'confidence': 0.0
            }

        domains = citation_result['details']['domains']
        quality_scores = [self._score_domain(domain) for domain in domains]

        return {
            'signal_type': 'source_quality',
            'detected': True,
            'count': len(domains),
            'details': {
                'sources': domains,
                'quality_scores': quality_scores,
                'average_quality': sum(quality_scores) / len(quality_scores) if quality_scores else 0.0,
                'high_quality_count': sum(1 for s in quality_scores if s >= 0.85)
            },
            'confidence': 0.90
        }

    def _score_domain(self, domain: str) -> float:
        """Score quality of a single domain."""
        domain_lower = domain.lower()

        # Check trusted domains
        if domain_lower in self.TRUSTED_DOMAINS:
            return 0.95

        # Check TLD authority
        for tld, score in self.DOMAIN_AUTHORITY.items():
            if domain_lower.endswith(tld):
                # Adjust down if unreliable pattern detected
                for pattern in self.UNRELIABLE_PATTERNS:
                    if pattern in domain_lower:
                        return score * 0.5

                return score

        # Unknown domain
        return 0.60
```

### 5.2 Source Quality Scoring Examples

```python
# Example 1: High quality academic source
domain = "mit.edu"
# Score: 0.95 (matches .edu TLD)

# Example 2: Trusted developer resource
domain = "developer.mozilla.org"
# Score: 0.95 (in TRUSTED_DOMAINS)

# Example 3: Commercial source
domain = "example.com"
# Score: 0.70 (matches .com TLD)

# Example 4: Unreliable pattern
domain = "random-spam-site.net"
# Score: 0.35 (contains "spam", scored down from base)
```

---

## 6. Signal Scoring Methodology

### 6.1 Improvement Scoring

```python
def compute_improvement_score(baseline_signals: dict, docstratum_signals: dict) -> float:
    """
    Compute overall improvement score comparing responses.

    Args:
        baseline_signals: Signal detection results for baseline
        docstratum_signals: Signal detection results for docstratum

    Returns:
        Improvement score (0.0 = no improvement, 1.0 = maximum improvement)
    """
    weights = {
        'citations': 0.25,      # Presence of citations
        'code_examples': 0.25,  # Presence of code examples
        'anti_patterns': 0.30,  # Absence of anti-patterns
        'source_quality': 0.20  # Quality of sources
    }

    improvements = {}

    # Citations: more is better
    baseline_citations = baseline_signals.get('citations', {}).get('count', 0)
    docstratum_citations = docstratum_signals.get('citations', {}).get('count', 0)
    improvements['citations'] = (docstratum_citations - baseline_citations) / max(baseline_citations, 1)

    # Code examples: more is better
    baseline_code = baseline_signals.get('code_examples', {}).get('count', 0)
    docstratum_code = docstratum_signals.get('code_examples', {}).get('count', 0)
    improvements['code_examples'] = (docstratum_code - baseline_code) / max(baseline_code, 1)

    # Anti-patterns: fewer is better
    baseline_antipatterns = baseline_signals.get('anti_patterns', {}).get('count', 0)
    docstratum_antipatterns = docstratum_signals.get('anti_patterns', {}).get('count', 0)
    improvements['anti_patterns'] = (baseline_antipatterns - docstratum_antipatterns) / max(baseline_antipatterns, 1)

    # Source quality: higher quality is better
    baseline_source_quality = baseline_signals.get('source_quality', {}).get('details', {}).get('average_quality', 0)
    docstratum_source_quality = docstratum_signals.get('source_quality', {}).get('details', {}).get('average_quality', 0)
    improvements['source_quality'] = docstratum_source_quality - baseline_source_quality

    # Compute weighted average
    weighted_sum = sum(
        improvements.get(signal, 0) * weights[signal]
        for signal in weights
    )

    # Clamp to [0, 1] range
    return max(0.0, min(weighted_sum, 1.0))
```

### 6.2 Signal Scoring Table

| Signal | Baseline Score | DocStratum Score | Improvement | Weight |
|---|---|---|---|---|
| Citations | 0 urls | 3 urls | +3 | 25% |
| Code Examples | 0 blocks | 2 blocks | +2 | 25% |
| Anti-Patterns | 3 found | 1 found | -2 (good) | 30% |
| Source Quality | 0.60 avg | 0.90 avg | +0.30 | 20% |
| **Overall** | — | — | **+1.33** | — |

---

## 7. Extensibility for New Signal Types

### 7.1 Adding New Signals

New signal types can be added by:

1. Creating a new SignalDetector subclass
2. Registering it in the signal detector registry
3. Updating scoring weights

```python
# Example: Add a new "technical_accuracy" signal

class TechnicalAccuracyDetector(SignalDetector):
    """Detect technical accuracy indicators."""

    CORRECT_PATTERNS = [
        "RFC",
        "ISO",
        "IETF",
        "official specification"
    ]

    INCORRECT_PATTERNS = [
        "deprecated",
        "no longer supported",
        "outdated",
        "legacy only"
    ]

    def detect(self, text: str) -> dict:
        text_lower = text.lower()
        correct_count = sum(1 for p in self.CORRECT_PATTERNS if p.lower() in text_lower)
        incorrect_count = sum(1 for p in self.INCORRECT_PATTERNS if p.lower() in text_lower)

        return {
            'signal_type': 'technical_accuracy',
            'detected': correct_count > 0 or incorrect_count > 0,
            'count': correct_count,
            'details': {
                'correct_indicators': correct_count,
                'incorrect_indicators': incorrect_count,
                'accuracy_ratio': correct_count / max(correct_count + incorrect_count, 1)
            },
            'confidence': 0.75
        }

# Register in detector registry
SIGNAL_DETECTORS = [
    CitationDetector(),
    AntiPatternDetector(),
    CodeExampleDetector(),
    SourceQualityDetector(),
    TechnicalAccuracyDetector(),  # New detector
]
```

### 7.2 Signal Registration Pattern

```python
class SignalDetectorRegistry:
    """Registry for all signal detectors."""

    def __init__(self):
        self.detectors = {}

    def register(self, detector: SignalDetector):
        """Register a new signal detector."""
        self.detectors[detector.detect().__get__('signal_type')] = detector

    def detect_all(self, text: str) -> dict:
        """Run all registered detectors on text."""
        results = {}
        for signal_type, detector in self.detectors.items():
            results[signal_type] = detector.detect(text)
        return results

# Usage
registry = SignalDetectorRegistry()
registry.register(CitationDetector())
registry.register(CodeExampleDetector())
# ... register all detectors

baseline_signals = registry.detect_all(baseline_text)
docstratum_signals = registry.detect_all(docstratum_text)
```

---

## Deliverables Checklist

- [ ] render_analysis() function implemented with full signature
- [ ] CitationDetector class implemented with URL pattern matching
- [ ] AntiPatternDetector class with keyword library
- [ ] CodeExampleDetector class with language inference
- [ ] SourceQualityDetector class with domain authority scoring
- [ ] SignalDetector base class and inheritance pattern
- [ ] Signal scoring methodology and improvement computation
- [ ] Rendering of signal comparison visualization
- [ ] Extensibility pattern for adding new detectors
- [ ] Signal detector registry implementation
- [ ] Configuration system for detector parameters
- [ ] Test cases for each detector type
- [ ] Documentation of detection accuracy limitations

---

## Acceptance Criteria

- [ ] render_analysis() accepts baseline and docstratum responses
- [ ] Citation detector finds URLs with 90%+ accuracy
- [ ] Anti-pattern detector identifies uncertainty language
- [ ] Code detector identifies fenced blocks and languages
- [ ] Source quality detector scores domains appropriately
- [ ] Improvement score reflects actual quality differences
- [ ] Signal visualization shows comparison clearly
- [ ] New detectors can be added without modifying core code
- [ ] Detection results include confidence scores
- [ ] All detectors are stateless and re-execution safe
- [ ] Signal detectors run in parallel for performance
- [ ] Detection configuration is externalized (not hardcoded)

---

## Next Step

→ **v0.4.2d — Visual Design System & CSS Architecture**

Implement the visual design system with CSS theming, gradient backgrounds, colored borders for baseline (red) vs. enhanced (green) distinction, and responsive layout considerations. Use the analysis results from this component to drive visual prominence.
