# v0.4.3b — Quality Scoring Engine & Heuristics

> **Task**: Implement the quality scoring engine with configurable heuristics for assessing the semantic quality of DocStratum-translated documentation. This sub-part defines a transparent, 5-point scoring rubric (URLs=1, code blocks=1, numbered steps=1, warnings/anti-patterns=1, length comparison=1) with detection logic, implementation patterns, and a clear enhancement roadmap for future LLM-as-judge and semantic similarity approaches.

---

## Objective

Establish a transparent, rule-based quality scoring system that evaluates DocStratum-translated documentation against five simple heuristic criteria. This file defines:

- Quality score design philosophy (simple, transparent, extensible)
- 5-point scoring rubric with clear acceptance criteria for each point
- `calculate_quality_score()` implementation and detection logic
- Scoring limitations and caveats (what this approach can and cannot do)
- Future enhancement roadmap (LLM-as-judge, semantic similarity)
- Score visualization and presentation options

---

## Scope Boundaries

| **In Scope** | **Out of Scope** |
|---|---|
| 5-point heuristic-based scoring rubric | LLM-as-judge implementation |
| Detection logic for each criterion (URLs, code, steps, warnings, length) | Semantic similarity calculations |
| Configurable heuristic weights and thresholds | Fine-tuned neural quality models |
| Transparency rules and scoring explanations | Machine learning model training |
| Score visualization in dashboard (v0.4.3a) | Comparison with human-annotated gold standard |
| Scoring limitations and caveats documentation | Production quality assurance workflows |
| Future enhancement roadmap | Integration with external quality APIs |

---

## Dependency Diagram

```
┌─────────────────────────────────────────────────────────┐
│          calculate_quality_score()                       │
│                                                         │
│  Input: baseline_text, docstratum_text                     │
│  Output: quality_score (float 0-5)                      │
│                                                         │
│  Heuristic Detectors (5 criteria):                      │
│  ├─ detect_urls() → 0 or 1                             │
│  ├─ detect_code_blocks() → 0 or 1                       │
│  ├─ detect_numbered_steps() → 0 or 1                    │
│  ├─ detect_warnings() → 0 or 1                          │
│  └─ detect_length_quality() → 0 or 1                    │
│                                                         │
│  Scoring Logic:                                         │
│  quality_score = sum(all_detectors)                     │
│  range: [0, 5]                                          │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│          Metrics Dashboard (v0.4.3a)                    │
│                                                         │
│  Quality Score Display:                                │
│  ├─ Value: "{score}/5"                                 │
│  ├─ Color coding: 0-2 (red), 3 (yellow), 4-5 (green)  │
│  └─ Tooltip: Explains individual criterion results     │
└─────────────────────────────────────────────────────────┘
```

---

## 1. Quality Score Design Philosophy

### 1.1 Core Principles

**Simple:**
- 5 independent binary criteria (each worth 0 or 1 point)
- Easy to calculate without ML models or complex algorithms
- Transparent rules that can be audited and explained to users
- No "black box" scoring that users cannot understand

**Transparent:**
- Each criterion has explicit detection logic
- Scoring explanation shows which criteria passed/failed
- Rules are visible in source code; not hidden in model weights
- Users can understand why a response scored 4/5 vs 3/5

**Extensible:**
- Criteria are independent; can add/remove/modify without affecting others
- Heuristics can be made configurable (e.g., adjust regex thresholds)
- Design supports migration to advanced techniques (LLM-as-judge, semantic similarity)
- Foundation for hybrid approaches (rules + ML for future iterations)

### 1.2 Why Heuristics Over ML?

| **Approach** | **Pros** | **Cons** | **Best For** |
|---|---|---|---|
| **Heuristics (v0.4.3b)** | Transparent, auditable, no training data needed | Limited to simple patterns | Explainability, demo phase |
| **LLM-as-Judge** | Nuanced evaluation, context-aware | Expensive API calls, black box | Production, complex quality |
| **Semantic Similarity** | Captures meaning, not just structure | Requires embeddings, complex setup | Comparing content similarity |
| **Fine-Tuned Model** | Optimized for domain, no API calls | Needs labeled training data | Long-term production systems |

**For v0.4.3**, heuristics are ideal because they:
1. Require no training data or LLM API calls
2. Provide clear, auditable scoring logic
3. Run instantly without latency overhead
4. Serve as baseline for future enhancement

---

## 2. 5-Point Scoring Rubric

### 2.1 Scoring Rubric Table

| **Criterion** | **Metric** | **Baseline Check** | **DocStratum Check** | **Score** | **Rationale** |
|---|---|---|---|---|---|
| **URLs** | Presence of reference links | Count URLs in baseline | Count URLs in DocStratum | +1 if DocStratum ≥ baseline | DocStratum should preserve/add references |
| **Code Blocks** | Presence of code examples | Count code blocks in baseline | Count code blocks in DocStratum | +1 if DocStratum ≥ baseline | Code examples should be retained |
| **Numbered Steps** | Presence of step-by-step instructions | Count numbered lists in baseline | Count numbered lists in DocStratum | +1 if DocStratum ≥ baseline | Steps guide users; must be preserved |
| **Warnings** | Presence of warnings/anti-patterns | Count warnings in baseline | Count warnings in DocStratum | +1 if DocStratum ≥ baseline | Critical safety info must be retained |
| **Length** | Response brevity vs quality | Check baseline/DocStratum length ratio | Ensure DocStratum not >1.5× longer | +1 if length ratio ≤ 1.5 | DocStratum adds minimal overhead |

### 2.2 Detailed Criterion Descriptions

**1. URLs / References (+1 point)**

**Purpose**: Ensure DocStratum preserves links to authoritative sources

**Baseline Check**:
```
URL_PATTERN = r'https?://[^\s]+'
baseline_urls = len(re.findall(URL_PATTERN, baseline_text))
```

**DocStratum Check**:
```
docstratum_urls = len(re.findall(URL_PATTERN, docstratum_text))
```

**Scoring Logic**:
- If `docstratum_urls >= baseline_urls`: **+1 point** ✓
- Otherwise: **0 points** ✗

**Example**:
```
Baseline (2 URLs):
"See https://docs.python.org and https://pydantic-docs.helpmanual.io for details."

DocStratum (2 URLs):
"For more information, visit https://docs.python.org and https://pydantic-docs.helpmanual.io"

Result: +1 point (equal URLs, semantically translated but references preserved)
```

---

**2. Code Blocks (+1 point)**

**Purpose**: Ensure DocStratum retains code examples for practical application

**Baseline Check**:
```
# Count both Markdown and indented code blocks
markdown_blocks = len(re.findall(r'```[\s\S]*?```', baseline_text))
indented_blocks = count_indented_blocks(baseline_text)
baseline_code = markdown_blocks + indented_blocks
```

**DocStratum Check**:
```
docstratum_code = markdown_blocks + indented_blocks  # Same logic
```

**Scoring Logic**:
- If `docstratum_code >= baseline_code`: **+1 point** ✓
- Otherwise: **0 points** ✗

**Example**:
```
Baseline (1 code block):
"To initialize Pydantic:
```python
from pydantic import BaseModel
class User(BaseModel):
    name: str
```"

DocStratum (1 code block):
"Initialize Pydantic using:
```python
from pydantic import BaseModel
class User(BaseModel):
    name: str
```"

Result: +1 point (code block retained with semantic translation)
```

---

**3. Numbered Steps (+1 point)**

**Purpose**: Preserve step-by-step instructions that guide users through procedures

**Baseline Check**:
```
# Match "1.", "2.", "3." patterns or "• Step 1:" patterns
step_pattern = r'(?:^|\n)(?:\d+\.|Step \d+:|•\s+\d+\.)'
baseline_steps = len(re.findall(step_pattern, baseline_text, re.MULTILINE))
```

**DocStratum Check**:
```
docstratum_steps = len(re.findall(step_pattern, docstratum_text, re.MULTILINE))
```

**Scoring Logic**:
- If `docstratum_steps >= baseline_steps`: **+1 point** ✓
- Otherwise: **0 points** ✗

**Example**:
```
Baseline (3 steps):
"1. Install the library
2. Import the module
3. Configure settings"

DocStratum (3 steps):
"Follow these steps:
1. Install the library
2. Import the module
3. Configure settings"

Result: +1 point (all steps preserved)
```

---

**4. Warnings / Anti-Patterns (+1 point)**

**Purpose**: Ensure critical warnings and anti-pattern guidance are retained

**Baseline Check**:
```
# Match common warning indicators
warning_patterns = [
    r'\b(?:warning|caution|important|deprecated|don\'t|never)\b',
    r'\⚠️|\❌|⛔|🚫'
]
baseline_warnings = sum(
    len(re.findall(p, baseline_text, re.IGNORECASE))
    for p in warning_patterns
)
```

**DocStratum Check**:
```
docstratum_warnings = sum(
    len(re.findall(p, docstratum_text, re.IGNORECASE))
    for p in warning_patterns
)
```

**Scoring Logic**:
- If `docstratum_warnings >= baseline_warnings`: **+1 point** ✓
- Otherwise: **0 points** ✗

**Example**:
```
Baseline (1 warning):
"⚠️ WARNING: Do not modify the config file directly. Use the API instead."

DocStratum (1 warning):
"Important: To avoid issues, never modify the config file directly. Use the API instead."

Result: +1 point (warning preserved with different language)
```

---

**5. Length Quality (+1 point)**

**Purpose**: Ensure DocStratum doesn't bloat the response while adding semantic value

**Baseline Check**:
```
baseline_length = len(baseline_text)
docstratum_length = len(docstratum_text)
```

**DocStratum Check**:
```
length_ratio = docstratum_length / baseline_length if baseline_length > 0 else 1.0
```

**Scoring Logic**:
- If `length_ratio ≤ 1.5`: **+1 point** ✓ (DocStratum ≤ 1.5× longer)
- Otherwise: **0 points** ✗ (DocStratum > 1.5× longer = poor efficiency)

**Threshold Rationale**:
- 1.0x: DocStratum is same length as baseline (ideal)
- 1.25x: DocStratum is 25% longer (acceptable, adds value)
- 1.5x: DocStratum is 50% longer (limit; beyond this = bloat)
- 2.0x+: DocStratum doubles baseline length (fails; not efficient)

**Example**:
```
Baseline: 500 characters
DocStratum: 650 characters (1.3x)

Ratio check: 650/500 = 1.3 ≤ 1.5 → +1 point ✓

---

Baseline: 500 characters
DocStratum: 1000 characters (2.0x)

Ratio check: 1000/500 = 2.0 > 1.5 → 0 points ✗
```

---

## 3. Detection Logic Flowchart

```
calculate_quality_score(baseline_text, docstratum_text)
│
├─ [1] detect_urls()
│   ├─ Extract URLs using regex
│   ├─ Count in baseline vs DocStratum
│   └─ Return: 1 if DocStratum ≥ baseline, else 0
│
├─ [2] detect_code_blocks()
│   ├─ Find markdown ``` blocks
│   ├─ Find indented code blocks
│   └─ Return: 1 if DocStratum ≥ baseline, else 0
│
├─ [3] detect_numbered_steps()
│   ├─ Find numbered lists (1., 2., etc.)
│   ├─ Match "Step N:" patterns
│   └─ Return: 1 if DocStratum ≥ baseline, else 0
│
├─ [4] detect_warnings()
│   ├─ Search for warning keywords
│   ├─ Search for warning emojis
│   └─ Return: 1 if DocStratum ≥ baseline, else 0
│
├─ [5] detect_length_quality()
│   ├─ Calculate length ratio
│   └─ Return: 1 if ratio ≤ 1.5, else 0
│
└─ Sum all scores → Return total (0-5)
```

---

## 4. Implementation Reference

### 4.1 Complete Implementation

```python
# metrics.py - Quality Scoring Engine

import re
from typing import Tuple

class QualityScoringConfig:
    """Configurable quality scoring thresholds."""
    LENGTH_RATIO_THRESHOLD = 1.5
    MIN_URLS = 0
    MIN_CODE_BLOCKS = 0
    MIN_STEPS = 0
    MIN_WARNINGS = 0

def detect_urls(baseline: str, docstratum: str) -> int:
    """
    Criterion 1: URLs / References
    Score +1 if DocStratum preserves URL count from baseline.
    """
    url_pattern = r'https?://[^\s]+'
    baseline_urls = len(re.findall(url_pattern, baseline))
    docstratum_urls = len(re.findall(url_pattern, docstratum))

    return 1 if docstratum_urls >= baseline_urls else 0

def detect_code_blocks(baseline: str, docstratum: str) -> int:
    """
    Criterion 2: Code Blocks
    Score +1 if DocStratum preserves code block count from baseline.
    """
    # Markdown code blocks: ```...```
    markdown_pattern = r'```[\s\S]*?```'
    baseline_markdown = len(re.findall(markdown_pattern, baseline))
    docstratum_markdown = len(re.findall(markdown_pattern, docstratum))

    # Indented code blocks (4+ spaces at line start)
    def count_indented_blocks(text: str) -> int:
        lines = text.split('\n')
        count = 0
        in_block = False
        for line in lines:
            if re.match(r'    ', line):  # 4+ spaces
                if not in_block:
                    count += 1
                    in_block = True
            else:
                in_block = False
        return count

    baseline_indented = count_indented_blocks(baseline)
    docstratum_indented = count_indented_blocks(docstratum)

    baseline_total = baseline_markdown + baseline_indented
    docstratum_total = docstratum_markdown + docstratum_indented

    return 1 if docstratum_total >= baseline_total else 0

def detect_numbered_steps(baseline: str, docstratum: str) -> int:
    """
    Criterion 3: Numbered Steps
    Score +1 if DocStratum preserves numbered list count from baseline.
    """
    step_pattern = r'(?:^|\n)(?:\d+\.|Step \d+:|•\s+\d+\.)'
    baseline_steps = len(re.findall(step_pattern, baseline, re.MULTILINE))
    docstratum_steps = len(re.findall(step_pattern, docstratum, re.MULTILINE))

    return 1 if docstratum_steps >= baseline_steps else 0

def detect_warnings(baseline: str, docstratum: str) -> int:
    """
    Criterion 4: Warnings / Anti-Patterns
    Score +1 if DocStratum preserves warning content count from baseline.
    """
    warning_patterns = [
        r'\b(?:warning|caution|important|deprecated|don\'t|never|must not|should not)\b',
        r'⚠️|❌|⛔|🚫|🔴|💥'
    ]

    def count_warnings(text: str) -> int:
        total = 0
        for pattern in warning_patterns:
            total += len(re.findall(pattern, text, re.IGNORECASE))
        return total

    baseline_warnings = count_warnings(baseline)
    docstratum_warnings = count_warnings(docstratum)

    return 1 if docstratum_warnings >= baseline_warnings else 0

def detect_length_quality(baseline: str, docstratum: str, config: QualityScoringConfig = None) -> int:
    """
    Criterion 5: Length Quality
    Score +1 if DocStratum length ≤ 1.5× baseline length.
    """
    if config is None:
        config = QualityScoringConfig()

    baseline_length = len(baseline)
    docstratum_length = len(docstratum)

    if baseline_length == 0:
        return 1  # No content to bloat

    ratio = docstratum_length / baseline_length
    return 1 if ratio <= config.LENGTH_RATIO_THRESHOLD else 0

def calculate_quality_score(
    baseline_text: str,
    docstratum_text: str,
    config: QualityScoringConfig = None
) -> Tuple[float, dict]:
    """
    Calculate quality score for DocStratum translation.

    Returns:
        Tuple of (score: float 0-5, details: dict with individual criterion results)
    """
    if config is None:
        config = QualityScoringConfig()

    scores = {
        'urls': detect_urls(baseline_text, docstratum_text),
        'code_blocks': detect_code_blocks(baseline_text, docstratum_text),
        'numbered_steps': detect_numbered_steps(baseline_text, docstratum_text),
        'warnings': detect_warnings(baseline_text, docstratum_text),
        'length_quality': detect_length_quality(baseline_text, docstratum_text, config),
    }

    total_score = sum(scores.values())

    return float(total_score), scores

def get_quality_explanation(scores: dict) -> str:
    """
    Generate human-readable explanation of quality score.
    """
    criteria_map = {
        'urls': 'References/URLs',
        'code_blocks': 'Code Examples',
        'numbered_steps': 'Step-by-Step Instructions',
        'warnings': 'Warnings/Safety Info',
        'length_quality': 'Response Efficiency'
    }

    passed = [criteria_map[k] for k, v in scores.items() if v == 1]
    failed = [criteria_map[k] for k, v in scores.items() if v == 0]

    explanation = f"Quality Score: {sum(scores.values())}/5\n"
    explanation += f"Passed ({len(passed)}): {', '.join(passed) if passed else 'None'}\n"
    explanation += f"Failed ({len(failed)}): {', '.join(failed) if failed else 'None'}"

    return explanation
```

### 4.2 Integration with ABTestResult Model

```python
# In data model

from pydantic import BaseModel

class DocStratumMetrics(BaseModel):
    quality_score: float  # 0.0 to 5.0
    quality_details: dict  # {"urls": 1, "code_blocks": 1, ...}
    quality_explanation: str  # Human-readable explanation

class ABTestResult(BaseModel):
    context_tokens: int
    token_overhead: int
    baseline_tokens: int
    docstratum_tokens: int
    latency_diff: float
    baseline_metrics: dict
    docstratum_metrics: DocStratumMetrics
```

---

## 5. Scoring Limitations and Caveats

### 5.1 What This Approach Can Do

✓ **Strengths**:
- Detects presence/absence of structural elements (code, URLs, steps)
- Quick evaluation (microseconds; no API calls)
- Transparent and auditable scoring rules
- Excellent for demo/prototype phase
- Serves as baseline for comparing improvements

### 5.2 What This Approach Cannot Do

✗ **Limitations**:
- Cannot assess semantic correctness (whether meaning is preserved)
- Cannot evaluate code functionality (only detects presence)
- Cannot judge writing quality or clarity
- Cannot detect subtle information loss
- May miss warnings phrased differently than baseline
- Cannot account for intentional brevity (removing redundancy)
- Cannot assess whether URLs are still valid or relevant

### 5.3 Limitations Detail Table

| **Limitation** | **Example** | **Impact** | **Workaround (Future)** |
|---|---|---|---|
| **Semantic Correctness** | DocStratum translates concept A → B (both valid but different) | Score +1 even if meaning shifted | LLM-as-judge evaluation |
| **Code Functionality** | Code block exists but contains syntax error | Score +1 for having code block | Parse and validate code |
| **Writing Quality** | DocStratum more concise but less clear | Score +1 for efficiency | Readability metrics + LLM |
| **Subtle Loss** | DocStratum omits one edge case from warning | Count still matches baseline | Semantic similarity on warnings |
| **Paraphrased Warnings** | Baseline: "Don't do X"; DocStratum: "Avoid X" | May miss if regex too strict | Fuzzy matching or embedding similarity |
| **Removed Redundancy** | Baseline repeats concept; DocStratum removes duplication | Length ratio fails if >1.5× | Compression ratio aware scoring |
| **URL Validity** | DocStratum preserves link but target site changed | Count matches but link broken | Link validation service |

### 5.4 Scoring Edge Cases

**Empty Baseline / DocStratum:**
```python
# If baseline is empty, score all +1 (DocStratum matches empty)
if baseline_length == 0:
    return 5.0, {
        'urls': 1, 'code_blocks': 1, 'numbered_steps': 1,
        'warnings': 1, 'length_quality': 1
    }
```

**Very Short Responses:**
```python
# If either text < 50 chars, disable certain checks
def calculate_quality_score(baseline, docstratum, config=None):
    if len(baseline) < 50 or len(docstratum) < 50:
        # Skip code block check (too short for meaningful code)
        # Keep length ratio check
        pass
```

**No Detectable Elements:**
```python
# If baseline has no URLs, code, steps, or warnings (5/5 possible)
# But text is very short, length check becomes primary
# This prevents inflated scores for simple content
```

---

## 6. Future Enhancement Path

### 6.1 Evolution Roadmap

**Phase 1 (Current - v0.4.3b)**: Heuristic-Based (Simple, Transparent)
- 5-point binary rubric
- Regex-based detection
- No external API calls or ML models
- Good for: Demo, quick feedback, explainability

**Phase 2 (v0.5.0)**: Enhanced Heuristics + Fuzzy Matching
- Implement fuzzy string matching for paraphrased content
- Add readability metrics (Flesch-Kincaid, BLEU score comparison)
- Introduce configurable weights per criterion
- Good for: More nuanced scoring, production prototypes

**Phase 3 (v0.6.0)**: LLM-as-Judge (Nuanced, Context-Aware)
- Use Claude or GPT-4 to evaluate quality
- Prompt: "Compare these two versions; rate quality on 1-5"
- More expensive (API calls) but much more accurate
- Good for: Production systems, complex domain knowledge

**Phase 4 (v1.0.0)**: Hybrid Approach (Fast + Accurate)
- Use heuristics for fast initial score
- Use LLM-as-judge for borderline cases (scores 2-3)
- Cache LLM results to reduce API calls
- Good for: Production at scale with cost control

### 6.2 LLM-as-Judge Prompt (Future)

```python
QUALITY_JUDGE_PROMPT = """
You are evaluating a semantic translation of documentation.

Original (Baseline):
{baseline_text}

Translation (DocStratum):
{docstratum_text}

Rate the quality of the translation on a scale of 1-5:
1. Poor: Lost critical information or introduced errors
2. Fair: Missing some important details or clarity issues
3. Good: Preserved meaning; minor detail loss acceptable
4. Excellent: Excellent translation with minimal loss
5. Outstanding: Improved clarity while preserving all information

Provide your rating and brief justification (2-3 sentences).
"""
```

### 6.3 Semantic Similarity (Future)

```python
# Using embeddings to measure semantic preservation
from sentence_transformers import SentenceTransformer

def calculate_semantic_similarity(baseline: str, docstratum: str) -> float:
    """
    Compare semantic meaning using embeddings.
    Returns: 0.0 (completely different) to 1.0 (identical meaning)
    """
    model = SentenceTransformer('all-MiniLM-L6-v2')
    baseline_embedding = model.encode(baseline)
    docstratum_embedding = model.encode(docstratum)

    from sklearn.metrics.pairwise import cosine_similarity
    similarity = cosine_similarity([baseline_embedding], [docstratum_embedding])[0][0]

    return float(similarity)
```

---

## Deliverables Checklist

- [ ] Quality score design philosophy documented (simple, transparent, extensible)
- [ ] 5-point scoring rubric fully defined with examples
- [ ] Each criterion has clear detection logic and threshold rules
- [ ] Scoring limitations and caveats documented with examples
- [ ] `calculate_quality_score()` function implemented and tested
- [ ] Helper detection functions implemented (URLs, code, steps, warnings, length)
- [ ] Quality explanation function for transparent user feedback
- [ ] Edge case handling for empty/short content
- [ ] Configurable scoring thresholds via QualityScoringConfig
- [ ] Integration with ABTestResult data model
- [ ] Future enhancement roadmap documented
- [ ] LLM-as-judge prompt template provided

---

## Acceptance Criteria

- [ ] Quality scores range from 0.0 to 5.0 (one point per criterion)
- [ ] URL detection correctly counts links in baseline and DocStratum
- [ ] Code block detection finds both markdown and indented code blocks
- [ ] Numbered steps detection finds numeric lists and "Step N:" patterns
- [ ] Warnings detection finds keywords and emoji indicators (case-insensitive)
- [ ] Length ratio correctly calculated; scores +1 only if ratio ≤ 1.5
- [ ] `calculate_quality_score()` returns tuple of (score, details_dict)
- [ ] Quality explanation is human-readable and shows passed/failed criteria
- [ ] Edge cases (empty baseline, very short text) handled gracefully
- [ ] Configuration object allows customizable thresholds
- [ ] All detection functions have unit tests with example cases
- [ ] No false positives on normal text without quality elements

---

## Next Step

→ **v0.4.3c — Token Analysis & Breakdown Display**

Build the detailed token analysis display showing the breakdown of prompt vs completion tokens for both baseline and DocStratum agents. This sub-part implements `render_token_breakdown()` using st.dataframe() with formatted tables, overhead calculations, and token efficiency metrics that feed into the cost estimation (v0.4.3d).

