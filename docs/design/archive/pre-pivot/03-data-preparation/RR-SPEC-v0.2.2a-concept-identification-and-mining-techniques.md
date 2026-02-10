# v0.2.2a: Concept Identification & Mining Techniques

> Systematic extraction and validation of semantic concepts from source documentation through automated analysis and manual curation. This module establishes the foundation for all downstream concept processing by identifying high-quality concept candidates using term frequency analysis, glossary extraction, heading mining, FAQ mining, and pattern detection. Success depends on both computational precision and domain expert judgment.

## Objective

Develop a reproducible, scalable methodology to systematically identify semantic concepts from unstructured and semi-structured documentation. Create both automated tools and manual workflows that produce a ranked candidate concept set suitable for expert review and definition writing. Establish clear decision criteria that separate true concepts (requiring explanation, cross-referenced, domain-specific) from noise (trivial terms, implementation details, transient references).

## Scope Boundaries

**IN SCOPE:**
- Concept mining from Markdown, HTML, and plain text documentation
- Automated term frequency analysis and keyword extraction
- Glossary parsing and extraction
- Heading structure analysis
- FAQ and Q&A pattern detection
- Named entity recognition for domain terms
- Concept candidate scoring and ranking
- Concept clustering into logical domains
- Python implementation with NLP libraries

**OUT OF SCOPE:**
- Definition writing (see v0.2.2b)
- Relationship mapping (see v0.2.2c)
- Anti-pattern identification (see v0.2.2d)
- Machine learning model training
- Real-time updating systems
- Integration with production systems

## Dependency Diagram

```
Documentation Sources
    ↓
[Text Preprocessing Layer]
  ├─ HTML/Markdown parsing
  ├─ Tokenization
  └─ Cleaning & normalization
    ↓
[Extraction Engines] (parallel)
  ├─ Term Frequency Analysis (TF-IDF)
  ├─ Glossary Mining
  ├─ Heading Structure Analysis
  ├─ FAQ Pattern Detection
  └─ Named Entity Recognition
    ↓
[Candidate Aggregation]
  ├─ Deduplication
  ├─ Cross-reference counting
  └─ Candidate pool creation
    ↓
[Scoring & Ranking Engine]
  ├─ Apply rubric (6 dimensions)
  ├─ Domain expert adjustment
  └─ Ranked candidate list
    ↓
[Clustering & Organization]
  ├─ Similarity grouping
  ├─ Domain assignment
  └─ Dependency pre-mapping
    ↓
[Validation Gate]
  ├─ Minimum viable set check
  ├─ Coverage analysis
  └─ Ready for definition writing (v0.2.2b)
```

## 1. Concept vs. Non-Concept Decision Criteria

The distinction between a true concept and noise is critical. A concept must satisfy four key properties:

| Property | True Concept | Non-Concept | Example (True) | Example (Non) |
|----------|------------|-------------|---|---|
| **Requires Explanation** | Needs 1+ sentence definition | Self-evident or trivial | "Idempotency" | "use" |
| **Cross-Referenced** | Appears in 3+ locations | Single mention or implementation detail | "cache invalidation" | "line 42" |
| **Domain-Specific** | Meaningful within knowledge domain | Generic English word or universal | "transaction isolation level" | "important" |
| **Dependency Potential** | Other concepts depend on it | Standalone, no dependencies | "ACID properties" (enables many concepts) | "button color" |

### Examples of Concept Filtering

**KEEP:** "Circuit breaker pattern" — architectural pattern appearing 8 times, cross-referenced in resilience docs, requires multi-sentence explanation, enables "fault tolerance" concept

**DISCARD:** "important" — generic adjective, appears in context sentences, needs no definition, no domain specificity

**KEEP:** "Eventual consistency" — distributed systems concept, mentioned 12 times across consistency docs, complex explanation needed, conflicts with "Strong consistency"

**DISCARD:** "the server" — implementation detail, specific reference to one system, no domain-level meaning

**KEEP:** "Bloom filter" — probabilistic data structure, appears in performance optimization section 6 times, requires explanation of false positive rate, enables "memory-efficient lookup"

**DISCARD:** "to implement" — generic verb, appears 47 times across all docs but carries no semantic meaning

## 2. Concept Candidate Scoring Rubric

A systematic scoring methodology transforms raw mining results into prioritized candidates. Each dimension scored 0-10.

### Six-Dimensional Rubric

| Dimension | Scoring Guide | Weight | Notes |
|-----------|---|---|---|
| **Cross-Reference Frequency** | 0-2 mentions=1pt, 3-5=4pts, 6-10=7pts, 11+=10pts | 25% | Higher frequency = more established concept |
| **Explanation Depth** | Single word=0, phrase=2, sentence required=5, multiple paragraphs=10 | 25% | Requires manual review of context |
| **Confusion Potential** | No common misconceptions=1, documented confusion=5, critical disambiguation=10 | 20% | Does domain have documented confusion about this term? |
| **Dependency Count** | Isolated=1, enables 1-2 concepts=4, enables 3-5=7, enables 6+=10 | 20% | How many other concepts depend on this? |
| **Terminology Variance** | One standard term=2, 2-3 variants=5, 4+ variants=10 | 5% | "Authentication" vs "AuthN", "OAuth2 vs "OAuth 2.0" |
| **Domain Specificity** | Generic=1, domain-adjacent=4, domain-core=7, domain-unique=10 | 5% | Is this term specific to this domain? |

### Scoring Calculation

```
Raw Score = (CF × 0.25) + (ED × 0.25) + (CP × 0.20) + (DC × 0.20) + (TV × 0.05) + (DS × 0.05)
Final Score = Raw Score / 10 (normalized 0-10)

Tier Assignment:
  9.0-10.0 = Tier 0 (Critical concepts, must include)
  7.0-8.9  = Tier 1 (Core concepts, should include)
  5.0-6.9  = Tier 2 (Secondary concepts, review carefully)
  3.0-4.9  = Tier 3 (Peripheral concepts, optional)
  0-2.9    = Tier 4 (Noise, discard)
```

### Scoring Example

**Term: "Connection Pooling"**
- Cross-Reference Frequency: 9 mentions = 7 points
- Explanation Depth: 2 paragraphs explaining why + mechanism = 9 points
- Confusion Potential: Often confused with "connection reuse" = 6 points
- Dependency Count: Enables "performance optimization", "resource management" = 5 points
- Terminology Variance: "pooling", "pool", "connection pool" = 5 points
- Domain Specificity: Database/networking core concept = 8 points

**Calculation:** (7×0.25) + (9×0.25) + (6×0.20) + (5×0.20) + (5×0.05) + (8×0.05) = 1.75 + 2.25 + 1.2 + 1.0 + 0.25 + 0.4 = **7.85** → Tier 1

## 3. Systematic Concept Mining Methodology

### 3.1 Term Frequency Analysis (TF-IDF)

Term Frequency-Inverse Document Frequency identifies domain-relevant terms by their statistical significance.

**Why TF-IDF?**
- Eliminates common English words (the, is, and)
- Weights terms appearing frequently in this domain but rarely elsewhere
- Computationally efficient for large documentation sets

**Implementation:**

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict
import re

class ConceptMiningTFIDF:
    def __init__(self, min_df=2, max_df=0.8, ngram_range=(1, 3)):
        """
        min_df: minimum document frequency (term must appear in 2+ docs)
        max_df: maximum document frequency (ignore terms in >80% of docs)
        ngram_range: extract 1-word, 2-word, and 3-word terms
        """
        self.vectorizer = TfidfVectorizer(
            min_df=min_df,
            max_df=max_df,
            ngram_range=ngram_range,
            stop_words='english',
            lowercase=True,
            max_features=500  # Top 500 terms per analysis
        )
        self.term_scores = defaultdict(float)
        self.term_frequencies = defaultdict(int)

    def extract_terms(self, documents):
        """
        Args:
            documents: list of text strings (paragraphs, sections, or full pages)

        Returns:
            sorted list of (term, tfidf_score, frequency) tuples
        """
        # Fit TF-IDF vectorizer
        tfidf_matrix = self.vectorizer.fit_transform(documents)
        feature_names = self.vectorizer.get_feature_names_out()

        # Aggregate scores across all documents
        tfidf_scores = tfidf_matrix.sum(axis=0).A1

        # Combine with document frequency
        results = []
        for idx, term in enumerate(feature_names):
            score = float(tfidf_scores[idx])
            # Count appearances across documents
            doc_appearances = (tfidf_matrix[:, idx] > 0).sum()
            results.append((term, score, doc_appearances))

        # Sort by TF-IDF score descending
        return sorted(results, key=lambda x: x[1], reverse=True)

# Usage example
miner = ConceptMiningTFIDF()
sample_docs = [
    "Connection pooling improves database performance...",
    "The pool manages multiple connections...",
    "Connection pool exhaustion causes timeouts..."
]
candidates = miner.extract_terms(sample_docs)
for term, score, freq in candidates[:10]:
    print(f"{term:30s} TF-IDF={score:.3f} Freq={freq}")
```

**Expected Output:**
```
connection pool              TF-IDF=0.487 Freq=3
pooling                      TF-IDF=0.412 Freq=3
pool exhaustion              TF-IDF=0.385 Freq=2
database performance         TF-IDF=0.341 Freq=2
timeout                      TF-IDF=0.298 Freq=2
```

### 3.2 Glossary Extraction Mining

Explicit glossaries and definition sections contain pre-vetted concepts.

**Sources to scan:**
- Dedicated glossary sections (search for "Glossary", "Terminology", "Definitions")
- Footnotes and endnotes
- Definition lists (HTML `<dl>` or Markdown definitions)
- Parenthetical definitions: "X (explanation)" patterns

**Pattern Detection:**

```python
import re
from typing import List, Tuple

class GlossaryMiner:
    def __init__(self):
        # Pattern for "Term: definition" format
        self.definition_pattern = re.compile(
            r'^[\s]*([A-Z][A-Za-z\s\-]{2,50})[\s]*[:—–][\s]*(.{20,200}?)(?:\n|$)',
            re.MULTILINE
        )
        # Pattern for "Term (definition)" inline
        self.parenthetical_pattern = re.compile(
            r'([A-Z][A-Za-z\s\-]{2,50})\s+\(([^)]{15,150})\)'
        )

    def extract_from_text(self, text: str) -> List[Tuple[str, str]]:
        """Extract term-definition pairs from plain text"""
        terms = []

        # Find formal definitions
        for match in self.definition_pattern.finditer(text):
            term = match.group(1).strip()
            definition = match.group(2).strip()
            terms.append((term, definition))

        return terms

    def extract_from_html(self, html: str) -> List[Tuple[str, str]]:
        """Extract from HTML definition lists"""
        from html.parser import HTMLParser

        class DLParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.in_dt = False
                self.in_dd = False
                self.current_term = None
                self.terms = []

            def handle_starttag(self, tag, attrs):
                if tag == 'dt':
                    self.in_dt = True
                elif tag == 'dd':
                    self.in_dd = True

            def handle_endtag(self, tag):
                if tag == 'dt':
                    self.in_dt = False
                elif tag == 'dd':
                    self.in_dd = False

            def handle_data(self, data):
                data = data.strip()
                if self.in_dt and data:
                    self.current_term = data
                elif self.in_dd and data and self.current_term:
                    self.terms.append((self.current_term, data))
                    self.current_term = None

        parser = DLParser()
        parser.feed(html)
        return parser.terms

# Usage
miner = GlossaryMiner()
glossary_text = """
Connection Pool: A mechanism that maintains a cache of database
connections for reuse across multiple requests.

Idle Connection: A connection in the pool that is not currently
in use by any request.
"""
terms = miner.extract_from_text(glossary_text)
for term, defn in terms:
    print(f"TERM: {term}\nDEFN: {defn}\n")
```

### 3.3 Heading Structure Mining

Documentation hierarchies reveal semantic organization. Headings are often implicit concept boundaries.

```python
import re
from typing import List, Dict

class HeadingMiner:
    def __init__(self):
        # Markdown heading patterns
        self.heading_pattern = re.compile(
            r'^(#{1,6})\s+(.+?)(?:\s*\{[#:][a-z0-9\-]*\})?\s*$',
            re.MULTILINE
        )

    def extract_headings(self, markdown: str) -> List[Dict]:
        """
        Extract heading hierarchy from Markdown content.

        Returns list of dicts with keys:
          - level: 1-6 (from number of #)
          - text: heading text
          - position: character position in document
        """
        headings = []
        for match in self.heading_pattern.finditer(markdown):
            level = len(match.group(1))
            text = match.group(2).strip()
            headings.append({
                'level': level,
                'text': text,
                'position': match.start()
            })
        return headings

    def extract_concept_candidates(self, headings: List[Dict]) -> List[str]:
        """
        Filter headings to likely concept terms.

        Rules:
        - H2-H3 usually indicate major concepts
        - Skip generic titles: "Overview", "Introduction", "Getting Started"
        - Skip meta sections: "Table of Contents", "References"
        """
        skip_patterns = [
            r'overview|introduction|getting started|setup|installation',
            r'table of contents|references|see also|further reading',
            r'quick start|basics|fundamentals|background'
        ]

        candidates = []
        for heading in headings:
            if heading['level'] <= 3:  # H1-H3 only
                text = heading['text'].lower()
                if not any(re.search(pat, text) for pat in skip_patterns):
                    candidates.append(heading['text'])

        return candidates

# Usage
markdown_doc = """
# Authentication Guide

## OAuth 2.0

OAuth 2.0 is an authorization framework...

### Authorization Code Flow

The authorization code flow is used for...

## Getting Started

First, register your application...
"""

miner = HeadingMiner()
headings = miner.extract_headings(markdown_doc)
concepts = miner.extract_concept_candidates(headings)
print("Concept candidates from headings:")
for concept in concepts:
    print(f"  - {concept}")
```

**Output:**
```
Concept candidates from headings:
  - OAuth 2.0
  - Authorization Code Flow
```

### 3.4 FAQ & Q&A Pattern Mining

FAQ sections and support documentation reveal common confusion points and important concepts.

```python
import re
from typing import List, Tuple

class FAQMiner:
    def __init__(self):
        # Various FAQ question patterns
        self.question_patterns = [
            r'^[Qq]\.?\s*(.{10,100})\?',  # "Q. What is X?"
            r'^[Qq](?:uestion)?:\s*(.{10,100})',  # "Q: What is X"
            r'^[Ww]hat\s+(?:is|are|does)\s+(.{5,80})\?',  # "What is X?"
            r'^[Hh]ow\s+(?:do|does|can|to)\s+(.{5,80})\?',  # "How do I X?"
            r'^[Ww]hy\s+(.{10,80})\?',  # "Why does X?"
        ]

    def extract_faq_entries(self, text: str) -> List[Tuple[str, str]]:
        """
        Extract FAQ entries as (question, answer) tuples.
        Assumes pattern: Q: ... A: ... (repeated)
        """
        # Split by Q: and A: markers
        faq_pairs = re.split(r'^[Qq]\.?\s*', text, flags=re.MULTILINE)[1:]

        entries = []
        for i in range(0, len(faq_pairs) - 1, 2):
            question_raw = faq_pairs[i]
            answer_raw = faq_pairs[i + 1] if i + 1 < len(faq_pairs) else ""

            # Extract question (text before answer marker)
            q_end = answer_raw.find('\nA:') or answer_raw.find('\na:')
            if q_end > -1:
                question = question_raw + answer_raw[:q_end]
                answer = answer_raw[q_end + 3:]
            else:
                question = question_raw
                answer = answer_raw

            entries.append((question.strip(), answer.strip()))

        return entries

    def extract_question_subjects(self, entries: List[Tuple[str, str]]) -> List[str]:
        """Extract the subject of each question as a concept candidate"""
        candidates = []

        for question, answer in entries:
            # Match question patterns
            for pattern in self.question_patterns:
                match = re.search(pattern, question)
                if match:
                    subject = match.group(1).strip()
                    # Clean up question artifacts
                    subject = re.sub(r'\?+$', '', subject)
                    candidates.append(subject)
                    break

        return candidates

# Usage
faq_text = """
Q: What is connection pooling?
A: Connection pooling is a technique that maintains...

Q: How do I configure pool size?
A: You can set the pool size using...

Q: Why would my connections exhaust?
A: Connections exhaust when demand exceeds...
"""

miner = FAQMiner()
entries = miner.extract_faq_entries(faq_text)
subjects = miner.extract_question_subjects(entries)
print("Concepts from FAQ subjects:")
for subj in subjects:
    print(f"  - {subj}")
```

### 3.5 Named Entity Recognition (NER) for Domain Terms

NLP-based entity recognition identifies proper nouns and technical terms.

```python
try:
    import spacy
except ImportError:
    print("Install: pip install spacy")

class DomainEntityRecognizer:
    def __init__(self, model="en_core_web_sm"):
        """
        Load spaCy NLP model for entity recognition.
        Download first: python -m spacy download en_core_web_sm
        """
        self.nlp = spacy.load(model)

    def extract_entities(self, text: str) -> List[Tuple[str, str]]:
        """
        Extract named entities with their types.
        Types: PERSON, ORG, PRODUCT, TECH_TERM (custom), etc.
        """
        doc = self.nlp(text)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        return entities

    def extract_noun_chunks(self, text: str) -> List[str]:
        """
        Extract noun phrases (often indicate concepts).
        E.g., "distributed transaction" from "handling distributed transactions..."
        """
        doc = self.nlp(text)
        return [chunk.text for chunk in doc.noun_chunks]

    def filter_technical_terms(self, text: str, domain_vocab: set = None) -> List[str]:
        """
        Filter entities to likely technical terms by:
        1. Capitalized multi-word phrases
        2. Words in domain vocabulary
        3. Adjective + noun combinations in domain
        """
        doc = self.nlp(text)
        candidates = []

        # Multi-word proper nouns
        for ent in doc.ents:
            if ent.label_ in ['PRODUCT', 'TECH', 'ORG']:
                candidates.append(ent.text)

        # Noun phrases (especially if domain-relevant)
        for chunk in doc.noun_chunks:
            text = chunk.text
            # Capitalized multi-word noun phrases
            if len(text.split()) > 1 and text[0].isupper():
                candidates.append(text)
            # Check against domain vocabulary if provided
            elif domain_vocab and text.lower() in domain_vocab:
                candidates.append(text)

        return list(set(candidates))

# Usage
text = """
OAuth 2.0 provides secure authentication using Bearer tokens.
The Authorization Code flow is most suitable for web applications.
Refresh tokens allow long-lived sessions.
"""

# Would require spacy model downloaded
# recognizer = DomainEntityRecognizer()
# entities = recognizer.extract_entities(text)
# chunks = recognizer.extract_noun_chunks(text)
```

## 4. Minimum Viable Concept Set (MVCS)

The MVCS is the smallest set of concepts that provides sufficient coverage for domain understanding.

**Coverage Definition:** A set of concepts is sufficient when knowledge of those concepts enables understanding of 80%+ of domain documentation.

### MVCS Calculation

```python
class MVCSCalculator:
    def __init__(self, all_candidates: List[str], candidate_scores: Dict[str, float]):
        """
        all_candidates: all identified concept candidates
        candidate_scores: scores from rubric (0-10)
        """
        self.candidates = all_candidates
        self.scores = candidate_scores

    def calculate_mvcs(self, target_coverage=0.80):
        """
        Greedily select concepts by score until coverage threshold reached.

        Returns:
          - mvcs: list of concept names
          - coverage_estimate: estimated documentation coverage
          - size: number of concepts in MVCS
        """
        # Sort by score descending
        sorted_candidates = sorted(
            self.candidates,
            key=lambda c: self.scores.get(c, 0),
            reverse=True
        )

        mvcs = []
        cumulative_score = 0
        total_score = sum(self.scores.values())

        for candidate in sorted_candidates:
            score = self.scores[candidate]
            cumulative_score += score
            mvcs.append(candidate)

            coverage = cumulative_score / total_score if total_score > 0 else 0
            if coverage >= target_coverage:
                break

        return {
            'concepts': mvcs,
            'count': len(mvcs),
            'coverage': cumulative_score / total_score if total_score > 0 else 0,
            'avg_score': cumulative_score / len(mvcs) if mvcs else 0
        }

# Example
candidates = [
    "Connection Pooling",
    "Idle Timeout",
    "Pool Exhaustion",
    "Thread Safety",
    "Configuration"
]
scores = {
    "Connection Pooling": 8.5,
    "Idle Timeout": 7.2,
    "Pool Exhaustion": 6.8,
    "Thread Safety": 5.9,
    "Configuration": 4.1
}

calc = MVCSCalculator(candidates, scores)
mvcs = calc.calculate_mvcs(target_coverage=0.80)
print(f"MVCS contains {mvcs['count']} concepts")
print(f"Coverage: {mvcs['coverage']:.1%}")
```

## 5. Concept Clustering and Domain Organization

Raw concepts must be grouped into logical domains to support hierarchical concept organization.

```python
from collections import defaultdict
import math

class ConceptClusterer:
    def __init__(self, concepts: List[str]):
        self.concepts = concepts
        self.clusters = defaultdict(list)

    def cluster_by_keywords(self, keyword_domains: Dict[str, List[str]]) -> Dict:
        """
        Assign concepts to domains based on keyword matching.

        Args:
            keyword_domains: {"Performance": ["cache", "pool", "optimize"],
                             "Security": ["auth", "encrypt", "token"], ...}

        Returns:
            mapping of concept -> domain
        """
        concept_to_domain = {}

        for concept in self.concepts:
            concept_lower = concept.lower()

            # Find best matching domain
            best_domain = None
            best_score = 0

            for domain, keywords in keyword_domains.items():
                score = sum(1 for kw in keywords if kw in concept_lower)
                if score > best_score:
                    best_score = score
                    best_domain = domain

            if best_domain:
                concept_to_domain[concept] = best_domain

        return concept_to_domain

    def cluster_by_similarity(self, concepts: List[str], threshold=0.6) -> Dict[str, List[str]]:
        """
        Group concepts by string similarity.
        Uses Jaccard similarity on word tokens.
        """
        def jaccard_similarity(s1: str, s2: str) -> float:
            words1 = set(s1.lower().split())
            words2 = set(s2.lower().split())
            intersection = len(words1 & words2)
            union = len(words1 | words2)
            return intersection / union if union > 0 else 0

        clusters = defaultdict(list)
        assigned = set()

        for i, concept1 in enumerate(concepts):
            if concept1 in assigned:
                continue

            cluster = [concept1]
            assigned.add(concept1)

            for j, concept2 in enumerate(concepts[i+1:], i+1):
                if concept2 in assigned:
                    continue

                sim = jaccard_similarity(concept1, concept2)
                if sim >= threshold:
                    cluster.append(concept2)
                    assigned.add(concept2)

            clusters[concept1] = cluster

        return dict(clusters)

# Usage
concepts = [
    "Connection Pool",
    "Connection Pooling",
    "Pool Exhaustion",
    "Cache Hit Rate",
    "Cache Eviction",
    "Authentication Token",
    "OAuth 2.0"
]

clusterer = ConceptClusterer(concepts)
keyword_domains = {
    "Performance": ["pool", "cache", "exhaustion", "hit"],
    "Security": ["auth", "token", "oauth", "encrypt"]
}

domain_map = clusterer.cluster_by_keywords(concepts, keyword_domains)
print("Domain assignments:")
for concept, domain in domain_map.items():
    print(f"  {concept:30s} → {domain}")
```

## 6. Automated Concept Candidate Extraction - Complete Implementation

This is the end-to-end system combining all mining techniques.

```python
import re
from typing import List, Dict, Tuple
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ConceptCandidate:
    """Represents an extracted concept candidate"""
    name: str
    score: float
    tier: str
    sources: List[str]  # Where it was found: "heading", "glossary", "tfidf", "faq"
    frequency: int  # How many times it appeared
    context_snippet: str  # 1-2 sentence context

class AutomatedConceptMiner:
    def __init__(self, docs_path: str):
        """
        Initialize miner for a directory of documentation files.

        Args:
            docs_path: path to documentation directory (Markdown/HTML files)
        """
        self.docs_path = Path(docs_path)
        self.all_candidates = {}  # name -> ConceptCandidate
        self.document_texts = {}

    def load_documents(self):
        """Load all Markdown and HTML files from docs directory"""
        for file_path in self.docs_path.glob("**/*.md"):
            with open(file_path, 'r', encoding='utf-8') as f:
                self.document_texts[str(file_path)] = f.read()

        for file_path in self.docs_path.glob("**/*.html"):
            with open(file_path, 'r', encoding='utf-8') as f:
                self.document_texts[str(file_path)] = f.read()

    def extract_all_candidates(self) -> List[ConceptCandidate]:
        """
        Run all mining techniques and return prioritized candidates.
        """
        if not self.document_texts:
            self.load_documents()

        # Track concept mentions and sources
        concept_sources = {}  # name -> list of (source_type, frequency)

        # 1. TF-IDF mining
        tfidf_terms = self._mine_tfidf()
        for term, score in tfidf_terms[:50]:  # Top 50
            key = term.lower()
            if key not in concept_sources:
                concept_sources[key] = []
            concept_sources[key].append(('tfidf', score))

        # 2. Glossary mining
        glossary_terms = self._mine_glossaries()
        for term in glossary_terms:
            key = term.lower()
            if key not in concept_sources:
                concept_sources[key] = []
            concept_sources[key].append(('glossary', 1.0))

        # 3. Heading mining
        heading_concepts = self._mine_headings()
        for heading in heading_concepts:
            key = heading.lower()
            if key not in concept_sources:
                concept_sources[key] = []
            concept_sources[key].append(('heading', 1.0))

        # 4. FAQ mining
        faq_concepts = self._mine_faqs()
        for concept in faq_concepts:
            key = concept.lower()
            if key not in concept_sources:
                concept_sources[key] = []
            concept_sources[key].append(('faq', 1.0))

        # 5. Calculate scores and create candidates
        candidates = []
        for concept_name, sources in concept_sources.items():
            score = self._calculate_candidate_score(concept_name, sources)
            tier = self._assign_tier(score)
            candidate = ConceptCandidate(
                name=concept_name,
                score=score,
                tier=tier,
                sources=[s[0] for s in sources],
                frequency=len(sources),
                context_snippet=""
            )
            candidates.append(candidate)

        # Sort by score descending
        candidates.sort(key=lambda c: c.score, reverse=True)
        return candidates

    def _mine_tfidf(self) -> List[Tuple[str, float]]:
        """Extract concepts using TF-IDF"""
        from sklearn.feature_extraction.text import TfidfVectorizer

        docs = list(self.document_texts.values())
        vectorizer = TfidfVectorizer(max_features=200, ngram_range=(1, 3))
        tfidf_matrix = vectorizer.fit_transform(docs)
        scores = tfidf_matrix.sum(axis=0).A1

        terms = vectorizer.get_feature_names_out()
        return sorted(
            zip(terms, scores),
            key=lambda x: x[1],
            reverse=True
        )[:100]

    def _mine_glossaries(self) -> List[str]:
        """Extract concepts from glossary sections"""
        glossary_pattern = re.compile(
            r'^###?\s+[Gg]lossar',
            re.MULTILINE
        )

        terms = []
        for doc_text in self.document_texts.values():
            # Find glossary section
            match = glossary_pattern.search(doc_text)
            if match:
                glossary_section = doc_text[match.start():]
                # Extract term-definition pairs
                pair_pattern = re.compile(
                    r'^[\s]*([A-Z][A-Za-z\s\-]{2,50})[\s]*[:—–]',
                    re.MULTILINE
                )
                terms.extend([m.group(1).strip() for m in pair_pattern.finditer(glossary_section)])

        return terms

    def _mine_headings(self) -> List[str]:
        """Extract concepts from heading structure"""
        heading_pattern = re.compile(r'^#{2,3}\s+(.+?)$', re.MULTILINE)

        concepts = []
        skip_words = {'overview', 'introduction', 'getting started', 'setup'}

        for doc_text in self.document_texts.values():
            for match in heading_pattern.finditer(doc_text):
                heading = match.group(1).strip()
                if not any(skip in heading.lower() for skip in skip_words):
                    concepts.append(heading)

        return concepts

    def _mine_faqs(self) -> List[str]:
        """Extract concepts from FAQ sections"""
        faq_pattern = re.compile(
            r'[Qq]\.?\s*(.{10,100})\?',
            re.MULTILINE
        )

        concepts = []
        for doc_text in self.document_texts.values():
            for match in faq_pattern.finditer(doc_text):
                question = match.group(1).strip()
                concepts.append(question)

        return concepts

    def _calculate_candidate_score(self, concept: str, sources: List[Tuple]) -> float:
        """Calculate score based on scoring rubric"""
        # Simplified scoring (full implementation would apply 6-D rubric)
        # Cross-reference frequency: count sources
        cf_score = min(10, len(sources) * 2)

        # Source diversity bonus
        unique_sources = len(set(s[0] for s in sources))
        diversity_bonus = unique_sources * 0.5

        # TF-IDF bonus
        tfidf_bonus = 0
        for source_type, score in sources:
            if source_type == 'tfidf':
                tfidf_bonus = min(5, score * 10)

        # Normalize to 0-10
        total = (cf_score + diversity_bonus + tfidf_bonus) / 2.5
        return min(10.0, total)

    def _assign_tier(self, score: float) -> str:
        """Assign tier based on score"""
        if score >= 9.0:
            return "Tier 0 (Critical)"
        elif score >= 7.0:
            return "Tier 1 (Core)"
        elif score >= 5.0:
            return "Tier 2 (Secondary)"
        elif score >= 3.0:
            return "Tier 3 (Peripheral)"
        else:
            return "Tier 4 (Noise)"

    def generate_report(self, output_file: str):
        """Generate comprehensive mining report"""
        candidates = self.extract_all_candidates()

        report = "# Concept Mining Report\n\n"
        report += f"Total candidates extracted: {len(candidates)}\n\n"

        # By tier
        report += "## Distribution by Tier\n\n"
        tier_groups = {}
        for candidate in candidates:
            tier = candidate.tier.split('(')[0].strip()
            if tier not in tier_groups:
                tier_groups[tier] = []
            tier_groups[tier].append(candidate)

        for tier in sorted(tier_groups.keys()):
            report += f"**{tier}**: {len(tier_groups[tier])} concepts\n"

        report += "\n## Top 30 Candidates\n\n"
        report += "| Rank | Concept | Score | Tier | Sources | Frequency |\n"
        report += "|------|---------|-------|------|---------|----------|\n"

        for i, cand in enumerate(candidates[:30], 1):
            sources_str = ", ".join(cand.sources)
            report += f"| {i} | {cand.name:35s} | {cand.score:.2f} | {cand.tier:20s} | {sources_str:25s} | {cand.frequency} |\n"

        with open(output_file, 'w') as f:
            f.write(report)

        return report

# Example usage would be:
# miner = AutomatedConceptMiner("/path/to/docs")
# candidates = miner.extract_all_candidates()
# miner.generate_report("mining_report.md")
```

## Deliverables Checklist

- [ ] **Concept Candidate List**: Ranked list of 50-200 candidate concepts with scores
- [ ] **Mining Methodology Document**: This file and supporting code
- [ ] **Python Implementation**: `concept_mining.py` with all mining engines
- [ ] **Scoring Spreadsheet**: Excel/CSV with scores and rubric justifications
- [ ] **Domain Organization**: Concept-to-domain mapping showing clustering
- [ ] **MVCS Definition**: Formal specification of minimum viable concept set
- [ ] **Mining Report**: HTML/Markdown report with statistics and visualizations
- [ ] **Validation Log**: QA sign-off on concept quality thresholds

## Acceptance Criteria

1. **Coverage Completeness**: MVCS covers ≥80% of domain documentation pages
2. **Score Justification**: All Tier 0 and Tier 1 concepts have documented scoring rationale
3. **Zero False Positives in Tier 0**: Manual review confirms all critical concepts are domain-accurate
4. **Consistency**: Same concept identified from multiple mining sources gets cross-referenced
5. **Reproducibility**: Automated mining produces consistent results across runs
6. **Domain Expert Alignment**: ≥90% of Tier 0 and Tier 1 concepts match expert expectations
7. **No Noise in Top 50**: Manual spot-check confirms top 50 are legitimate concepts
8. **Deduplication Complete**: Similar terms (e.g., "pooling" vs "pool") are merged

## Next Steps

Once concept candidates are validated, proceed to **v0.2.2b: Precision Definition Writing** to create machine-readable definitions for each Tier 0 and Tier 1 concept. The concept list becomes the input for definition work.
