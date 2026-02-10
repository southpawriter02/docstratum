# Layer 2: Concept Entries & Graph Encoding

> **Core Purpose:** Transform concept extraction artifacts (v0.2.2) into rich Concept YAML entries that encode domain knowledge as a semantic graph. This layer establishes conceptual relationships, dependencies, and anti-patterns, enabling LLMs to understand not just what documentation exists, but how ideas connect and depend on each other.

## Objective

Create a structured concept graph that:
- Translates v0.2.2 concept extractions into complete Concept YAML entries
- Encodes relationship graphs (depends_on, related_pages) as flat YAML lists
- Defines concept IDs using hierarchical, hyphenated naming (e.g., `auth-oauth2-jwt`)
- Authors definitions that explain concepts in accessible, domain-aware language
- Documents anti-patterns (common misconceptions, misuses, traps)
- Validates graph consistency (no cycles, all dependencies exist, all URLs valid)
- Implements topological sorting for concept ordering

## Scope Boundaries

**IN:**
- Concept ID naming conventions (lowercase, hyphenated, hierarchical)
- Definition authoring guidelines (1-3 sentences, accessible, domain-aware)
- Relationship encoding in YAML (depends_on as flat list, graph reconstruction)
- Anti-pattern writing (multiline strings, special character escaping)
- Concept ordering strategy (topological sort by dependencies, then alphabetical)
- Graph consistency validation rules and error detection
- Pydantic validation code for concept graph integrity
- 5 complete worked examples with full relationship graph
- Python graph integrity checking script

**OUT:**
- Concept extraction algorithm (v0.2.2 responsibility)
- Page content rewriting or modification
- Few-shot example creation (Layer 3 responsibility)
- LLM fine-tuning or instruction generation

## Dependency Diagram

```
┌─────────────────────────────────────────┐
│   v0.2.2 Concept Extraction & Mapping   │
│   (produces: concepts.json w/ raw data) │
└────────────────┬────────────────────────┘
                 │
                 ↓
    ┌────────────────────────────────────┐
    │   Layer 1: Page Entries            │
    │   (valid pages[] list created)     │
    └────────────────┬───────────────────┘
                     │
                     ↓
    ┌────────────────────────────────────┐
    │   Layer 2: Concept Entries         │ ← YOU ARE HERE
    │   ├─ Concept ID design             │
    │   ├─ Definition authoring          │
    │   ├─ Relationship encoding         │
    │   ├─ Anti-pattern documentation    │
    │   └─ Graph validation              │
    └────────────────┬───────────────────┘
                     │
                     ↓
    ┌────────────────────────────────────┐
    │   Layer 3: Few-Shot Examples       │
    │   (references concepts & pages)    │
    └────────────────────────────────────┘
```

---

## 1. Concept ID Naming Conventions

### 1.1 ID Format Rules

Concept IDs uniquely identify a concept and encode hierarchy through hyphenation:

| Rule | Format | Example | Rationale |
|------|--------|---------|-----------|
| Case | lowercase only | `auth-oauth2` | Case-insensitive lookups, cleaner |
| Separator | hyphens, no underscores | `auth-oauth2` (not `auth_oauth2`) | Follows REST/URL conventions |
| Length | 3-50 chars | `auth`, `async-event-loops` | Readable, not abbreviations |
| Hierarchy | dot/hyphen separated (choose one) | `auth-oauth2-jwt` or `auth.oauth2.jwt` | Semantic nesting |
| Uniqueness | globally unique within llms.txt | No duplicates | Reference integrity |
| Start/end | alphanumeric only, no leading/trailing hyphens | `auth-oauth2` (not `-auth-` or `-oauth2`) | Valid YAML |

### 1.2 Hierarchical ID Design

Use hyphens to encode conceptual hierarchy:

```yaml
concepts:
  # Top-level concepts (no parent)
  - id: "authentication"
    name: "Authentication"
    ...

  # First-level children (depend on parent)
  - id: "authentication-basic"
    name: "HTTP Basic Authentication"
    depends_on:
      - "authentication"
    ...

  - id: "authentication-oauth2"
    name: "OAuth 2.0 Authentication"
    depends_on:
      - "authentication"
    ...

  # Second-level children (more specific)
  - id: "authentication-oauth2-jwt"
    name: "OAuth 2.0 with JWT Tokens"
    depends_on:
      - "authentication-oauth2"
      - "tokens-jwt"
    ...
```

**Naming Pattern:**
- Root concept: `auth`
- Child concepts: `auth-oauth2`, `auth-saml`
- Grandchild concepts: `auth-oauth2-jwt`, `auth-oauth2-refresh`

### 1.3 ID Generation Algorithm (Python)

```python
import re
from typing import Set

def generate_concept_id(concept_name: str, existing_ids: Set[str]) -> str:
    """
    Generate a hyphenated, lowercase concept ID from a name.

    Args:
        concept_name: Human-readable concept name (e.g., "HTTP Basic Authentication")
        existing_ids: Set of already-used IDs (prevent duplicates)

    Returns:
        Generated ID (e.g., "http-basic-authentication")

    Raises:
        ValueError if ID would conflict with existing_ids
    """

    # Step 1: Lowercase and strip whitespace
    id_candidate = concept_name.lower().strip()

    # Step 2: Remove articles and common words (optional, keeps ID shorter)
    # Uncomment if desired:
    # stop_words = {'the', 'a', 'an', 'and', 'or', 'is', 'for', 'in', 'of'}
    # words = [w for w in id_candidate.split() if w not in stop_words]
    # id_candidate = '-'.join(words)

    # Step 3: Replace spaces with hyphens
    id_candidate = re.sub(r'\s+', '-', id_candidate)

    # Step 4: Remove non-alphanumeric characters (keep hyphens)
    id_candidate = re.sub(r'[^a-z0-9\-]', '', id_candidate)

    # Step 5: Collapse multiple hyphens
    id_candidate = re.sub(r'-+', '-', id_candidate)

    # Step 6: Remove leading/trailing hyphens
    id_candidate = id_candidate.strip('-')

    # Step 7: Ensure not too long (truncate if necessary, but preserve meaning)
    if len(id_candidate) > 50:
        # Keep first words + last word for meaning
        parts = id_candidate.split('-')
        id_candidate = '-'.join(parts[:3] + [parts[-1]]) if len(parts) > 4 else id_candidate[:50]

    # Step 8: Check for conflicts
    if id_candidate in existing_ids:
        # Append numeric suffix if conflict
        counter = 1
        while f"{id_candidate}-{counter}" in existing_ids:
            counter += 1
        id_candidate = f"{id_candidate}-{counter}"

    return id_candidate

# Test cases:
existing = {"authentication", "authentication-oauth2"}
test_names = [
    "HTTP Basic Authentication",
    "OAuth 2.0",
    "JWT Tokens",
    "API Key Management",
]

for name in test_names:
    id_val = generate_concept_id(name, existing)
    print(f"'{name}' → '{id_val}'")

# Output:
# 'HTTP Basic Authentication' → 'http-basic-authentication'
# 'OAuth 2.0' → 'oauth-20'
# 'JWT Tokens' → 'jwt-tokens'
# 'API Key Management' → 'api-key-management'
```

---

## 2. Concept Definition Authoring

### 2.1 Definition Guidelines

A Concept definition explains the idea clearly in 1-3 sentences:

| Aspect | Guideline | Example |
|--------|-----------|---------|
| Length | 1-3 sentences, 50-200 words | (See examples below) |
| Audience | Intermediate developer (not CS PhD, not beginner) | Assume basic knowledge of topic domain |
| Voice | Active, declarative (not "This page discusses...") | "JWT tokens are..." not "JWT tokens are discussed in..." |
| Clarity | Explain the "what" and "why", not just "how" | "What is JWT and why use it?" not "How to implement JWT" |
| Domain specificity | Use terminology expected in documentation | "asymmetric key cryptography", not "fancy math stuff" |
| Examples | Optional inline, but prefer external examples in few-shot | Definition is concept, not tutorial |

### 2.2 Definition Examples by Content Type

**Type 1: Foundational Concept (No Dependencies)**
```yaml
- id: "http"
  name: "HTTP Protocol"
  definition: >
    HTTP (HyperText Transfer Protocol) is the stateless application protocol
    that powers web communication. It uses a request-response model where clients
    send requests to servers, which return responses with status codes and content.
```

**Type 2: Advanced Concept (Depends on Foundations)**
```yaml
- id: "authentication-oauth2"
  name: "OAuth 2.0"
  definition: >
    OAuth 2.0 is an open authorization framework that allows third-party
    applications to request access to user resources without handling passwords.
    It uses tokens (bearer tokens or JWT) instead of credentials, enabling secure
    delegation of access rights with fine-grained scopes.
  depends_on:
    - "authentication"
    - "tokens"
```

**Type 3: Pattern/Architecture Concept**
```yaml
- id: "architecture-microservices"
  name: "Microservices Architecture"
  definition: >
    Microservices is an architectural pattern that structures applications as
    loosely coupled, independently deployable services that communicate via APIs.
    Each service owns its data, scales independently, and is organized around
    business capabilities rather than technical layers.
```

**Type 4: Tool/Library Concept**
```yaml
- id: "orm-sqlalchemy"
  name: "SQLAlchemy Object-Relational Mapping"
  definition: >
    SQLAlchemy is a Python library that maps Python objects to database tables,
    allowing you to interact with databases using object-oriented code instead of
    raw SQL. It supports multiple backends (PostgreSQL, MySQL, SQLite) with
    automatic schema generation and migration.
```

### 2.3 Definition Quality Checklist

Evaluate each definition:

```
✓ Defines the concept clearly in 1-3 sentences?
✓ Uses domain-appropriate terminology without jargon?
✓ Explains "what" and "why", not just "how"?
✓ Avoids circular definition (doesn't use undefined terms)?
✓ Is actionable or explanatory (not just "exists")?
✓ Does NOT reference specific pages (that's related_pages field)?
✓ Is accurate to all documentation using this concept?
✓ Avoids marketing language or opinions?
```

---

## 3. Relationship Encoding in YAML

### 3.1 Fields: depends_on vs. related_pages

| Field | Purpose | Type | Example | Semantics |
|-------|---------|------|---------|-----------|
| `depends_on` | Concepts that must be understood first | list[concept_id] | `["authentication", "tokens"]` | Prerequisite: A depends_on B means "understand B before A" |
| `related_pages` | Documentation pages that explain this concept | list[url] | `["https://docs/auth-guide", "https://docs/oauth2-tutorial"]` | Reference: links to pages where concept appears |

### 3.2 Building the depends_on Graph

The depends_on list encodes prerequisite relationships:

```yaml
concepts:
  # Level 0: No prerequisites
  - id: "http"
    name: "HTTP Protocol"
    definition: "..."
    depends_on: []  # No prerequisites
    related_pages: ["https://docs/http-intro", "https://docs/http-methods"]

  # Level 1: Depends on HTTP
  - id: "authentication"
    name: "Authentication"
    definition: "..."
    depends_on:
      - "http"  # Must understand HTTP first
    related_pages: ["https://docs/auth-intro"]

  # Level 2: Depends on Level 1 concepts
  - id: "authentication-oauth2"
    name: "OAuth 2.0"
    definition: "..."
    depends_on:
      - "authentication"  # Prerequisite
      - "tokens"          # Also needs this
    related_pages: ["https://docs/oauth2-guide", "https://docs/oauth2-jwt"]

  # Level 3: Most specific
  - id: "authentication-oauth2-jwt"
    name: "OAuth 2.0 with JWT"
    definition: "..."
    depends_on:
      - "authentication-oauth2"
      - "tokens-jwt"
    related_pages: ["https://docs/jwt-tokens", "https://docs/oauth2-jwt-flow"]
```

### 3.3 Graph Reconstruction Algorithm

Given flat depends_on lists, reconstruct the dependency graph:

```python
from typing import Dict, Set, List
from dataclasses import dataclass

@dataclass
class Concept:
    id: str
    name: str
    definition: str
    depends_on: List[str]
    related_pages: List[str]

def build_dependency_graph(concepts: List[Concept]) -> Dict[str, Set[str]]:
    """
    Build graph representation from flat depends_on lists.

    Returns:
        graph[concept_id] = set of concept_ids it depends on
    """
    graph = {}
    for concept in concepts:
        graph[concept.id] = set(concept.depends_on)
    return graph

def get_ancestors(concept_id: str, graph: Dict[str, Set[str]]) -> Set[str]:
    """Get all transitive dependencies (full chain)."""
    ancestors = set()
    to_process = {concept_id}
    visited = set()

    while to_process:
        current = to_process.pop()
        if current in visited:
            continue
        visited.add(current)

        if current in graph:
            deps = graph[current]
            ancestors.update(deps)
            to_process.update(deps)

    return ancestors

def topological_sort(concepts: List[Concept]) -> List[Concept]:
    """
    Sort concepts so dependencies come before dependents.

    Ensures that when reading concepts sequentially,
    all prerequisites are already known.
    """
    graph = {c.id: set(c.depends_on) for c in concepts}
    id_to_concept = {c.id: c for c in concepts}

    # Kahn's algorithm
    in_degree = {id: len(deps) for id, deps in graph.items()}
    queue = [id for id, degree in in_degree.items() if degree == 0]
    sorted_ids = []

    while queue:
        queue.sort()  # Alphabetical for stability
        current_id = queue.pop(0)
        sorted_ids.append(current_id)

        # Find all concepts that depend on current
        for concept_id, deps in graph.items():
            if current_id in deps:
                in_degree[concept_id] -= 1
                if in_degree[concept_id] == 0:
                    queue.append(concept_id)

    if len(sorted_ids) != len(concepts):
        raise ValueError("Circular dependency detected in concept graph")

    return [id_to_concept[id] for id in sorted_ids]

# Example:
concepts = [
    Concept("http", "HTTP", "...", [], []),
    Concept("auth", "Authentication", "...", ["http"], []),
    Concept("oauth2", "OAuth 2.0", "...", ["auth"], []),
]

sorted_concepts = topological_sort(concepts)
# Result: http → auth → oauth2
```

### 3.4 YAML Graph Encoding Example

```yaml
concepts:
  # Web fundamentals layer
  - id: "http"
    name: "HTTP Protocol"
    definition: "HTTP is the stateless request-response protocol powering web communication."
    depends_on: []
    related_pages:
      - "https://docs.example.com/http-intro"
      - "https://docs.example.com/http-methods"
    anti_patterns:
      - "HTTP is stateful (it isn't; state requires explicit mechanisms)"
      - "HTTP headers are limited (200+ standard headers defined)"

  - id: "tokens"
    name: "Security Tokens"
    definition: "Tokens are cryptographic credentials that authorize requests without transmitting passwords."
    depends_on: []
    related_pages:
      - "https://docs.example.com/tokens-intro"
    anti_patterns:
      - "Tokens replace passwords (they supplement, not replace auth)"
      - "All tokens are equally secure (implementations vary widely)"

  # Authentication layer (depends on web fundamentals)
  - id: "authentication"
    name: "Authentication"
    definition: "Authentication verifies user identity before granting access. Standard methods include password, multi-factor, and single sign-on approaches."
    depends_on:
      - "http"
    related_pages:
      - "https://docs.example.com/auth-overview"
      - "https://docs.example.com/auth-methods"
    anti_patterns:
      - "Authentication and authorization are the same (auth*n* verifies identity, auth*z* grants access)"

  # Advanced authentication layer (depends on authentication)
  - id: "authentication-oauth2"
    name: "OAuth 2.0"
    definition: "OAuth 2.0 is a delegation protocol allowing third-party apps to access user resources via tokens, without handling passwords."
    depends_on:
      - "authentication"
      - "tokens"
    related_pages:
      - "https://docs.example.com/oauth2-guide"
      - "https://docs.example.com/oauth2-flows"
    anti_patterns:
      - "OAuth is primarily for authentication (it's for authorization; use OpenID Connect for authentication)"
      - "OAuth tokens should live long (short-lived access + refresh tokens = secure)"

  # Most specific layer
  - id: "authentication-oauth2-jwt"
    name: "OAuth 2.0 with JWT Tokens"
    definition: "JWT tokens enable stateless OAuth 2.0 by encoding claims cryptographically, reducing server-side session storage."
    depends_on:
      - "authentication-oauth2"
      - "tokens-jwt"
    related_pages:
      - "https://docs.example.com/jwt-tokens"
      - "https://docs.example.com/oauth2-jwt-implementation"
    anti_patterns:
      - "JWT tokens are encrypted (they're signed but not encrypted; use JWE for encryption)"
      - "JWT payload is secret (it's Base64-encoded but readable; don't store sensitive data)"

  - id: "tokens-jwt"
    name: "JSON Web Tokens"
    definition: "JWT is a compact token format encoding claims as Base64url-encoded JSON segments, signed or encrypted, suitable for transmitting across HTTP."
    depends_on:
      - "tokens"
    related_pages:
      - "https://docs.example.com/jwt-intro"
      - "https://docs.example.com/jwt-signing"
    anti_patterns:
      - "JWT is inherently secure (it's only as secure as the signing key and verification)"
      - "All JWT payloads should be encrypted (only if containing sensitive data)"
```

---

## 4. Anti-Pattern Writing

### 4.1 Anti-Pattern Definition

An anti-pattern documents:
- Common misconceptions about the concept
- Dangerous or incorrect usage patterns
- Traps developers fall into
- Clarifications on what NOT to do

### 4.2 Anti-Pattern Format

Each anti-pattern is a concise (one-sentence) explanation of a mistake:

```yaml
anti_patterns:
  - "HTTP is stateful"  # Wrong assumption
  - "OAuth is for authentication"  # Common misunderstanding
  - "JWT tokens are encrypted"  # False security assumption
  - "Async code is always faster"  # Incorrect generalization
```

### 4.3 Anti-Pattern Writing Guide

| Component | Rule | Example |
|-----------|------|---------|
| Format | "Mistake claim (correction)" | "HTTP is stateful (use cookies/sessions for state)" |
| Length | Single sentence, max 120 chars | (Keep concise) |
| Claim | State the wrong belief | "JWT tokens are secret" |
| Correction | Provide the right understanding | "JWT payloads are Base64 but not encrypted" |
| Tone | Educational, not condescending | "Don't..." not "Never..." |

### 4.4 Multi-Line Anti-Pattern Strings (YAML Escaping)

For longer anti-patterns, use YAML block scalars:

```yaml
anti_patterns:
  # Single-line format
  - "OAuth is primarily for authentication (use OpenID Connect for that)"

  # Multi-line format (literal block)
  - |
    A common mistake is assuming async code is always faster.
    Async improves I/O throughput but doesn't parallelize CPU-bound work.
    Use threading or multiprocessing for CPU-bound tasks.

  # Special characters (these are auto-escaped in YAML)
  - "Don't use HTTP (use HTTPS) or store passwords in JWT (use hash + salt)"
```

**Character Escaping in YAML:**
```yaml
# These characters need escaping in quoted strings:
anti_patterns:
  - "Use \" double-quoted \" strings for special chars"
  - 'Use \' single-quoted \' strings to escape differently'
  - |
    Use literal blocks (|) to avoid escaping entirely
    for multi-line content with special characters!
```

---

## 5. Concept Completeness & Validation

### 5.1 Validation Rules

Every concept in the llms.txt must satisfy:

| Rule | Check | Error | Fix |
|------|-------|-------|-----|
| ID unique | No duplicate `id` values | Duplicate concept ID: "auth" | Rename one to "auth-2" or more specific |
| depends_on valid | Every depends_on target exists | Undefined dependency: "auth → nonexistent-concept" | Remove invalid ID or create missing concept |
| related_pages valid | Every URL in related_pages exists in pages[] | Orphaned page reference: "https://docs/unknown" | Remove URL or add page to pages[] |
| No cycles | Dependency graph is acyclic | Circular dependency: A → B → C → A | Remove one edge or redesign hierarchy |
| Definition non-empty | Every concept has a definition | Empty definition for "auth" | Author definition |
| Name non-empty | Every concept has a name | Empty name for ID "auth" | Provide human-readable name |

### 5.2 Validation Script (Python)

```python
from typing import Dict, Set, List
from pydantic import BaseModel, validator
import sys

class Concept(BaseModel):
    id: str
    name: str
    definition: str
    depends_on: List[str] = []
    related_pages: List[str] = []
    anti_patterns: List[str] = []

class CanonicalPage(BaseModel):
    url: str

class LlmsTxtValidator:
    def __init__(self, pages: List[CanonicalPage], concepts: List[Concept]):
        self.pages = pages
        self.concepts = concepts
        self.page_urls = {p.url for p in pages}
        self.concept_ids = {c.id for c in concepts}
        self.errors = []
        self.warnings = []

    def validate_unique_ids(self) -> bool:
        """Ensure no duplicate concept IDs."""
        seen = set()
        for concept in self.concepts:
            if concept.id in seen:
                self.errors.append(f"Duplicate concept ID: '{concept.id}'")
                return False
            seen.add(concept.id)
        return True

    def validate_dependencies_exist(self) -> bool:
        """Check that all depends_on targets exist."""
        valid = True
        for concept in self.concepts:
            for dep_id in concept.depends_on:
                if dep_id not in self.concept_ids:
                    self.errors.append(
                        f"Concept '{concept.id}' depends on undefined concept '{dep_id}'"
                    )
                    valid = False
        return valid

    def validate_page_references(self) -> bool:
        """Check that all related_pages URLs exist in pages list."""
        valid = True
        for concept in self.concepts:
            for url in concept.related_pages:
                if url not in self.page_urls:
                    self.errors.append(
                        f"Concept '{concept.id}' references undefined page: {url}"
                    )
                    valid = False
        return valid

    def detect_cycles(self) -> bool:
        """Use DFS to detect cycles in dependency graph."""
        def has_cycle(node, visiting, visited):
            visiting.add(node)
            for dep in self.get_concept(node).depends_on:
                if dep in visiting:
                    return True
                if dep not in visited and has_cycle(dep, visiting, visited):
                    return True
            visiting.remove(node)
            visited.add(node)
            return False

        visited = set()
        for concept in self.concepts:
            if concept.id not in visited:
                if has_cycle(concept.id, set(), visited):
                    self.errors.append(
                        f"Circular dependency detected involving '{concept.id}'"
                    )
                    return False
        return True

    def validate_non_empty_fields(self) -> bool:
        """Check required fields are non-empty."""
        valid = True
        for concept in self.concepts:
            if not concept.id or not concept.id.strip():
                self.errors.append("Concept has empty ID")
                valid = False
            if not concept.name or not concept.name.strip():
                self.errors.append(f"Concept '{concept.id}' has empty name")
                valid = False
            if not concept.definition or not concept.definition.strip():
                self.warnings.append(f"Concept '{concept.id}' has empty definition")
        return valid

    def topological_sort(self) -> List[str]:
        """Return concept IDs in dependency order."""
        from collections import defaultdict, deque

        graph = {c.id: set(c.depends_on) for c in self.concepts}
        in_degree = {id: len(deps) for id, deps in graph.items()}
        queue = deque([id for id, degree in in_degree.items() if degree == 0])
        sorted_ids = []

        while queue:
            current = queue.popleft()
            sorted_ids.append(current)

            for cid in self.concept_ids:
                if current in graph.get(cid, set()):
                    in_degree[cid] -= 1
                    if in_degree[cid] == 0:
                        queue.append(cid)

        return sorted_ids

    def get_concept(self, concept_id: str) -> Concept:
        """Retrieve concept by ID."""
        for c in self.concepts:
            if c.id == concept_id:
                return c
        raise ValueError(f"Concept '{concept_id}' not found")

    def run_all_checks(self) -> bool:
        """Run all validation checks and report results."""
        checks = [
            ("Unique IDs", self.validate_unique_ids),
            ("Dependencies exist", self.validate_dependencies_exist),
            ("Page references valid", self.validate_page_references),
            ("No cycles", self.detect_cycles),
            ("Non-empty fields", self.validate_non_empty_fields),
        ]

        all_pass = True
        for check_name, check_func in checks:
            result = check_func()
            status = "✓" if result else "✗"
            print(f"{status} {check_name}")
            if not result:
                all_pass = False

        if self.errors:
            print("\nErrors:")
            for error in self.errors:
                print(f"  ✗ {error}")

        if self.warnings:
            print("\nWarnings:")
            for warning in self.warnings:
                print(f"  ⚠ {warning}")

        return all_pass and not self.errors

# Example usage:
pages = [
    CanonicalPage(url="https://docs/auth-guide"),
    CanonicalPage(url="https://docs/oauth2-tutorial"),
]

concepts = [
    Concept(
        id="authentication",
        name="Authentication",
        definition="...",
        depends_on=[],
        related_pages=["https://docs/auth-guide"],
    ),
    Concept(
        id="oauth2",
        name="OAuth 2.0",
        definition="...",
        depends_on=["authentication"],
        related_pages=["https://docs/oauth2-tutorial"],
    ),
]

validator = LlmsTxtValidator(pages, concepts)
is_valid = validator.run_all_checks()

if is_valid:
    sorted_ids = validator.topological_sort()
    print(f"\nTopological order: {' → '.join(sorted_ids)}")
```

---

## 6. Concept Ordering Strategy

### 6.1 Ordering Algorithm

Concepts are ordered by:
1. **Primary:** Topological sort (dependencies first)
2. **Secondary:** Alphabetical (same dependency level)

```yaml
concepts:
  # Level 0: No dependencies (alphabetical)
  - id: "async-programming"
    ...
  - id: "http"
    ...
  - id: "tokens"
    ...

  # Level 1: Depends on Level 0 (topologically ordered, then alphabetical)
  - id: "authentication"
    depends_on: ["http"]
    ...
  - id: "caching"
    depends_on: ["http"]
    ...

  # Level 2: Depends on Level 1
  - id: "authentication-oauth2"
    depends_on: ["authentication"]
    ...
```

### 6.2 Python Implementation

```python
def order_concepts(concepts: List[Concept]) -> List[Concept]:
    """
    Order concepts:
    1. Topologically (dependencies before dependents)
    2. Alphabetically within same level
    """
    from collections import deque, defaultdict

    # Build graph
    graph = {c.id: set(c.depends_on) for c in concepts}
    in_degree = {c.id: len(graph[c.id]) for c in concepts}
    id_to_concept = {c.id: c for c in concepts}

    # Kahn's algorithm with alphabetical ordering
    queue = deque(sorted([id for id, degree in in_degree.items() if degree == 0]))
    sorted_ids = []

    while queue:
        # Always pop from front (queue is pre-sorted)
        current = queue.popleft()
        sorted_ids.append(current)

        # Find dependents and decrement in-degree
        next_batch = []
        for cid, deps in graph.items():
            if current in deps:
                in_degree[cid] -= 1
                if in_degree[cid] == 0:
                    next_batch.append(cid)

        # Add next batch sorted alphabetically
        for cid in sorted(next_batch):
            queue.append(cid)

    return [id_to_concept[id] for id in sorted_ids]
```

---

## 7. Worked Example: 5 Complete Concept Entries with Graph

### 7.1 Example Domain: Authentication & Security (FastAPI Context)

```yaml
concepts:
  # ============================================================================
  # LAYER 0: Foundations (no dependencies)
  # ============================================================================

  - id: "http-protocol"
    name: "HTTP Protocol Basics"
    definition: >
      HTTP (HyperText Transfer Protocol) is a stateless request-response protocol
      that powers web communication. Clients send requests to servers, which process
      them and return responses with status codes (200, 404, 500, etc.) and content.
      HTTPS adds encryption via TLS for secure communication.
    depends_on: []
    related_pages:
      - "https://fastapi.tiangolo.com/deployment/"
      - "https://fastapi.tiangolo.com/tutorial/first-steps/"
    anti_patterns:
      - "HTTP is stateful (it's stateless; state requires explicit mechanisms like cookies)"
      - "HTTPS is only for passwords (it encrypts ALL communication, not just credentials)"
      - "HTTP headers can transmit unlimited data (browsers/servers have size limits)"

  - id: "cryptography-hashing"
    name: "Cryptographic Hashing"
    definition: >
      Hashing is a one-way cryptographic function that converts input data into
      a fixed-size irreversible hash. Two different inputs must produce different hashes
      (collision resistance). Hashing is used for password storage, data integrity checking,
      and digital signatures—never for encryption (which requires reversal).
    depends_on: []
    related_pages:
      - "https://fastapi.tiangolo.com/tutorial/security/"
    anti_patterns:
      - "Hashing is encryption (it's irreversible; encryption allows decryption)"
      - "Any hash function is secure (use bcrypt, scrypt, or Argon2; avoid MD5 or SHA1 for passwords)"
      - "Salting is optional (salts are essential to prevent rainbow table attacks)"

  # ============================================================================
  # LAYER 1: Authentication Concepts (depend on foundations)
  # ============================================================================

  - id: "authentication"
    name: "User Authentication"
    definition: >
      Authentication is the process of verifying a user's identity before granting access.
      Common methods include passwords (with salting/hashing), multi-factor authentication (MFA),
      and delegated authentication (OAuth, SAML). Authentication must be distinguished from
      authorization, which controls what authenticated users can do.
    depends_on:
      - "http-protocol"
      - "cryptography-hashing"
    related_pages:
      - "https://fastapi.tiangolo.com/tutorial/security/"
      - "https://fastapi.tiangolo.com/tutorial/security/first-steps/"
    anti_patterns:
      - "Authentication and authorization are the same (auth-N verifies identity; auth-Z grants permissions)"
      - "Passwords should be encrypted (they should be hashed irreversibly with salts)"
      - "HTTP Basic Auth is secure (only over HTTPS; credentials transmitted in every request)"

  - id: "tokens-security"
    name: "Security Tokens"
    definition: >
      Security tokens are cryptographic credentials that authorize API requests without
      transmitting passwords on every request. Common types include API keys (simple but limited),
      bearer tokens (used with OAuth), session tokens (cookies), and JWTs (self-contained claims).
      Tokens should be short-lived and revokable.
    depends_on:
      - "authentication"
    related_pages:
      - "https://fastapi.tiangolo.com/tutorial/security/first-steps/"
      - "https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/"
    anti_patterns:
      - "Tokens replace passwords (they supplement auth; passwords are still needed to issue tokens)"
      - "All tokens are equally secure (implementation and lifespan matter significantly)"
      - "Token secrets should be long-lived (use short-lived access tokens + refresh tokens)"

  # ============================================================================
  # LAYER 2: Advanced Authentication (depend on Layer 1)
  # ============================================================================

  - id: "oauth2"
    name: "OAuth 2.0 Authorization Framework"
    definition: >
      OAuth 2.0 is a delegation protocol enabling third-party applications to access
      user resources without handling passwords. It defines four flows (Authorization Code,
      Implicit, Client Credentials, Resource Owner Password) suited to different client types.
      OAuth is for authorization (delegated access), not authentication—combine with OpenID Connect
      for authentication.
    depends_on:
      - "authentication"
      - "tokens-security"
    related_pages:
      - "https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/"
      - "https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/"
    anti_patterns:
      - "OAuth is primarily for authentication (it's for authorization; use OpenID Connect for identity)"
      - "OAuth tokens live forever (implement token expiration and refresh token rotation)"
      - "OAuth replaces role-based access control (use OAuth for delegation + RBAC for fine-grained permissions)"

  - id: "jwt-tokens"
    name: "JSON Web Tokens (JWT)"
    definition: >
      JWT (JSON Web Token) is a compact, stateless token format that encodes claims
      (user ID, expiration, scopes) as Base64url-encoded JSON, optionally signed (JWS)
      or encrypted (JWE). JWTs enable distributed authentication without server-side session
      stores. The token structure is header.payload.signature, all readable but signed/encrypted
      for integrity and confidentiality.
    depends_on:
      - "tokens-security"
      - "cryptography-hashing"
    related_pages:
      - "https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/"
      - "https://fastapi.tiangolo.com/advanced/security/oauth2-jwt-bearer/"
    anti_patterns:
      - "JWT payloads are secret (they're Base64-encoded but readable; only sign/encrypt if using JWS/JWE)"
      - "JWTs are inherently secure (security depends on signing key strength, algorithm choice, and verification)"
      - "JWTs eliminate the need for HTTPS (transport layer encryption is still essential)"
```

### 7.2 Dependency Graph Visualization

```
http-protocol
    ↓
authentication ← cryptography-hashing
    ↓
tokens-security
    ↓
oauth2
    ↓
jwt-tokens (also depends on cryptography-hashing)
```

**Topological Order:**
1. `http-protocol` (no deps)
2. `cryptography-hashing` (no deps)
3. `authentication` (depends on 1, 2)
4. `tokens-security` (depends on 3)
5. `oauth2` (depends on 3, 4)
6. `jwt-tokens` (depends on 4, 2)

### 7.3 Graph Statistics

```
Total Concepts: 6
Max Dependency Depth: 3 (http-protocol → tokens-security → oauth2)
Most Referenced: authentication (depended on by 3 others)
Orphan Concepts: 0 (all connected)
Circular Dependencies: 0 ✓
```

---

## 8. Graph Integrity Checking Script

```python
#!/usr/bin/env python3
"""
Concept Graph Integrity Checker

Usage:
    python validate_concept_graph.py --llms-file llms.txt

Checks:
    - No duplicate IDs
    - All dependencies exist
    - All page references valid
    - No circular dependencies
    - Topological ordering correct
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, Set, List

def load_llms_txt(filepath: str) -> Dict:
    """Load and parse llms.txt YAML file."""
    with open(filepath, 'r') as f:
        return yaml.safe_load(f)

def check_unique_ids(concepts: List[Dict]) -> bool:
    """Verify no duplicate concept IDs."""
    ids = [c['id'] for c in concepts]
    if len(ids) != len(set(ids)):
        duplicates = [id for id in set(ids) if ids.count(id) > 1]
        print(f"✗ Duplicate concept IDs: {duplicates}")
        return False
    print("✓ All concept IDs are unique")
    return True

def check_dependencies_exist(concepts: List[Dict]) -> bool:
    """Verify all depends_on targets exist."""
    concept_ids = {c['id'] for c in concepts}
    valid = True

    for concept in concepts:
        for dep_id in concept.get('depends_on', []):
            if dep_id not in concept_ids:
                print(f"✗ {concept['id']} depends on undefined concept '{dep_id}'")
                valid = False

    if valid:
        print("✓ All dependencies are defined")
    return valid

def check_page_references(concepts: List[Dict], pages: List[Dict]) -> bool:
    """Verify all related_pages URLs exist in pages list."""
    page_urls = {p['url'] for p in pages}
    valid = True

    for concept in concepts:
        for url in concept.get('related_pages', []):
            if url not in page_urls:
                print(f"✗ {concept['id']} references undefined page: {url}")
                valid = False

    if valid:
        print("✓ All page references are valid")
    return valid

def detect_cycles(concepts: List[Dict]) -> bool:
    """Detect circular dependencies using DFS."""
    graph = {c['id']: set(c.get('depends_on', [])) for c in concepts}

    def has_cycle(node, visiting, visited):
        visiting.add(node)
        for dep in graph.get(node, set()):
            if dep in visiting:
                return True
            if dep not in visited and has_cycle(dep, visiting, visited):
                return True
        visiting.remove(node)
        visited.add(node)
        return False

    visited = set()
    for concept in concepts:
        if concept['id'] not in visited:
            if has_cycle(concept['id'], set(), visited):
                print(f"✗ Circular dependency detected involving '{concept['id']}'")
                return False

    print("✓ No circular dependencies")
    return True

def check_topological_ordering(concepts: List[Dict]) -> bool:
    """Verify concepts are in valid topological order."""
    concept_ids = [c['id'] for c in concepts]
    graph = {c['id']: set(c.get('depends_on', [])) for c in concepts}

    for i, concept_id in enumerate(concept_ids):
        for dep_id in graph[concept_id]:
            dep_index = concept_ids.index(dep_id) if dep_id in concept_ids else -1
            if dep_index > i:
                print(f"⚠ {concept_id} (position {i}) depends on {dep_id} (position {dep_index}) — not in topological order")
                return False

    print("✓ Concepts are in valid topological order")
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_concept_graph.py --llms-file <path>")
        sys.exit(1)

    llms_file = sys.argv[sys.argv.index('--llms-file') + 1]

    if not Path(llms_file).exists():
        print(f"Error: File not found: {llms_file}")
        sys.exit(1)

    data = load_llms_txt(llms_file)
    concepts = data.get('concepts', [])
    pages = data.get('pages', [])

    print(f"Validating {len(concepts)} concepts, {len(pages)} pages...\n")

    checks = [
        ("Unique IDs", lambda: check_unique_ids(concepts)),
        ("Dependencies defined", lambda: check_dependencies_exist(concepts)),
        ("Page references", lambda: check_page_references(concepts, pages)),
        ("No cycles", lambda: detect_cycles(concepts)),
        ("Topological order", lambda: check_topological_ordering(concepts)),
    ]

    results = [check() for _, check in checks]

    print(f"\n{'='*50}")
    if all(results):
        print("✓ All checks passed!")
        sys.exit(0)
    else:
        print("✗ Some checks failed. Review errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## Deliverables Checklist

- [ ] Concept ID naming conventions documented (3+ hierarchy examples)
- [ ] ID generation algorithm implemented and tested
- [ ] Definition authoring guidelines with 4+ types of concepts
- [ ] depends_on vs related_pages semantics clearly explained
- [ ] Graph reconstruction algorithm (Python) implemented and tested
- [ ] Anti-pattern writing guidelines with 10+ examples
- [ ] Validation script tests all 5 rules (unique IDs, deps exist, pages exist, no cycles, non-empty)
- [ ] Topological sort algorithm implemented and validated
- [ ] 5 complete worked examples with full relationship graph
- [ ] Graph visualization/statistics provided for worked example
- [ ] Graph integrity checking script complete and tested
- [ ] All code examples syntax-verified and runnable

---

## Acceptance Criteria

1. **Completeness:** All 8 sections present with working code examples
2. **Correctness:** Topological sort handles cyclic graphs (error) and acyclic (ordered)
3. **Validation:** Graph integrity script catches 100% of documented errors
4. **Examples:** 5 worked examples are internally consistent (all refs exist, no cycles)
5. **Clarity:** Decision trees and algorithms are unambiguous
6. **Actionability:** An author can design a concept graph after reading section 1-2

---

## Next Step Pointer

→ **Layer 3: Few-Shot Examples & Quality Assurance** (v0.2.3d)

Layer 3 consumes validated concepts and pages, creating curated few-shot examples for LLM prompt context. You will:
- Design intent taxonomy (getting-started, how-to, troubleshooting, comparison, migration, explanation)
- Write natural language questions and ideal answers
- Validate few-shot source_pages against pages list
- Test few-shot effectiveness (measure LLM improvement with vs. without examples)
- Run final QA checklist for complete llms.txt file
