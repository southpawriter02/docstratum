# Layer 1: Page Entries & Summary Writing

> **Core Purpose:** Transform discovered documentation pages into CanonicalPage YAML entries with high-quality, information-dense summaries. This layer bridges the gap between raw site audit (v0.2.2) and semantic enrichment (v0.2.3), establishing page identity and context for LLM consumption.

## Objective

Create comprehensive, well-organized page entries that:
- Author each CanonicalPage field with consistent, validation-aware formatting
- Write summaries that maximize information density within the 280-character constraint
- Classify pages using content_type rules (tutorial, reference, concept, changelog, faq)
- Normalize and validate URLs for consistency and canonicality
- Order pages strategically (by type, dependency, importance) for LLM relevance ranking
- Establish clear decision trees for edge cases

## Scope Boundaries

**IN:**
- CanonicalPage field explanation and validation rules
- content_type classification system with decision tree
- 280-character summary writing methodology (verb-first, audience-aware)
- Summary quality scoring rubric (information density, actionability, specificity)
- Page ordering strategies (by content_type, dependency, importance)
- URL normalization and canonicalization rules
- 10+ worked examples (complete page entries from real sites)
- 10+ before/after summary pairs showing bad vs. good writing

**OUT:**
- Page discovery/audit logic (v0.2.2 responsibility)
- Concept extraction (Layer 2 responsibility)
- Few-shot example design (Layer 3 responsibility)
- SEO optimization or content strategy consulting

## Dependency Diagram

```
┌─────────────────────────────────────────┐
│   v0.2.2 Site Audit & Data Preparation │
│   (produces: discovered_pages.json)     │
└────────────────┬────────────────────────┘
                 │
                 ↓
    ┌────────────────────────────────────┐
    │   Layer 0: Metadata & Skeleton     │
    │   (creates empty llms.txt)         │
    └────────────────┬───────────────────┘
                     │
                     ↓
    ┌────────────────────────────────────┐
    │   Layer 1: Page Entries            │ ← YOU ARE HERE
    │   ├─ CanonicalPage authoring       │
    │   ├─ Summary writing               │
    │   ├─ URL normalization             │
    │   └─ Page ordering                 │
    └────────────────┬───────────────────┘
                     │
                     ↓
    ┌────────────────────────────────────┐
    │   Layer 2: Concept Entries         │
    │   (depends on pages[] being valid) │
    └────────────────────────────────────┘
                     │
                     ↓
    ┌────────────────────────────────────┐
    │   Layer 3: Few-Shot Examples       │
    │   (references pages list)          │
    └────────────────────────────────────┘
```

---

## 1. CanonicalPage Field Explanation & Validation

### 1.1 Field-by-Field Breakdown

| Field | Type | Required? | Rules | Example |
|-------|------|-----------|-------|---------|
| `url` | HttpUrl | Yes | HTTPS, no query params, canonical form | `"https://docs.python.org/3/tutorial/index.html"` |
| `title` | str | Yes | 5-200 chars, matches page `<title>`, no redundant words | `"Getting Started with Python"` |
| `content_type` | Literal | Yes | One of: tutorial, reference, concept, changelog, faq | `"tutorial"` |
| `last_verified` | date | Yes | ISO 8601 (YYYY-MM-DD), must be ≤ today | `"2025-02-05"` |
| `summary` | str | Yes | Max 280 chars, verb-first, information-dense, audience-aware | `"Step-by-step guide to installing Python..."` |

### 1.2 Detailed Field Validation

**url field:**
```yaml
url: "https://docs.example.com/guide/intro.html"

Rules:
  ✓ Protocol: HTTPS required (HTTP rejected or auto-upgraded)
  ✓ No query parameters: ?utm_source=email (remove)
  ✓ No URL fragments: #section (remove, but document anchor target separately if needed)
  ✓ Trailing slash: optional for paths, but consistent within site
  ✓ Case: match site's actual URL casing
  ✓ Duplicate slashes: collapse (example.com/// → example.com/)
  ✓ Must be publicly accessible (not behind auth/paywall)

Invalid Examples:
  ✗ http://example.com/page         (use HTTPS)
  ✗ https://example.com/page?ref=1  (strip query params)
  ✗ https://example.com/page#intro  (strip fragments)
```

**title field:**
```yaml
title: "Getting Started with FastAPI"

Rules:
  ✓ Length: 5-200 characters
  ✓ Matches actual page <title> tag (may truncate long titles)
  ✓ No redundancy: avoid "FastAPI Guide to FastAPI"
  ✓ Proper grammar: Title Case for English
  ✓ No excessive punctuation: avoid "FastAPI??? Here's How!!!"
  ✓ Specific: "Getting Started" (good) vs. "Page" (bad)

Invalid Examples:
  ✗ "FastAPI"  (too generic, <5 chars effective)
  ✗ "FastAPI — FastAPI — FastAPI Getting Started Guide" (redundant)
  ✗ "getting started with fastapi" (should be "Getting Started with FastAPI")
```

**content_type field:**
Choices explained in detail in Section 2 (classification rules). Examples:
```yaml
content_type: "tutorial"    # Step-by-step learning path
content_type: "reference"   # API docs, function signatures
content_type: "concept"     # Explanation of domain idea
content_type: "changelog"   # Release notes, version history
content_type: "faq"         # Q&A, common questions
```

**last_verified field:**
```yaml
last_verified: "2025-02-05"

Rules:
  ✓ ISO 8601 format: YYYY-MM-DD
  ✓ Must be quoted (prevents YAML float parsing)
  ✓ Must be ≤ today's date
  ✓ Represents: "Last time we confirmed this URL is live and content accurate"

Update Protocol:
  - Regenerate: Re-check URL in browser, confirm page still exists
  - Update date: If URL/title/summary changes
  - Frequency: At least quarterly; more often for volatile docs

Validation Code (Python):
from datetime import date
from pydantic import validator

@validator('last_verified')
def validate_last_verified(cls, v):
    if v > date.today():
        raise ValueError(f"last_verified ({v}) cannot be in future")
    if (date.today() - v).days > 365:
        print(f"⚠ Warning: {v} is >1 year old, consider re-verification")
    return v
```

**summary field:**
Covered in detail in Section 3 (summary writing masterclass).

---

## 2. Content_Type Classification Rules

### 2.1 Classification Decision Tree

```
Start: "What is the primary purpose of this page?"

├─ Step-by-step learning path?
│  └─ YES → TUTORIAL
│     Examples: "Getting Started with Django", "5-Minute QuickStart"
│
├─ Reference material (API, functions, syntax)?
│  └─ YES → REFERENCE
│     Examples: "Function Reference", "API Documentation", "Configuration Options"
│
├─ Explanation of a concept or principle?
│  └─ YES → CONCEPT
│     Examples: "Understanding Decorators", "What is Middleware?", "How CORS Works"
│
├─ Release notes, version history, changelog?
│  └─ YES → CHANGELOG
│     Examples: "v2.0 Release Notes", "Breaking Changes in v3.0"
│
├─ Collection of Q&A or frequently asked questions?
│  └─ YES → FAQ
│     Examples: "Frequently Asked Questions", "Common Pitfalls"
│
└─ None of above / Multiple purposes
   └─ Choose primary purpose (see tiebreaker rules below)
```

### 2.2 Content Type Examples & Characteristics

| Type | Characteristics | Common Page Titles | Audience |
|------|-----------------|-------------------|----------|
| **tutorial** | Sequential steps, beginner-focused, "how to do X", hands-on | "Getting Started", "5-Minute Intro", "Step-by-Step Guide" | Learners, new users |
| **reference** | Comprehensive API docs, function signatures, syntax, exhaustive | "API Reference", "Class Documentation", "Configuration Options" | Developers, power users |
| **concept** | Explains "why" and "what", theoretical foundation, mental models | "Understanding Decorators", "How CORS Works", "Architecture Overview" | All users (conceptual depth) |
| **changelog** | Version history, release notes, breaking changes, migration guides | "v2.0 Release Notes", "Breaking Changes in v3", "Migration Guide" | Upgraders, maintainers |
| **faq** | Common questions, troubleshooting, quick answers, Q&A format | "Frequently Asked Questions", "Common Pitfalls", "Troubleshooting" | All users (problem-solvers) |

### 2.3 Tiebreaker Rules (When Ambiguous)

**Scenario:** Page contains both tutorial steps AND API reference info
→ **Decision:** Classify by dominant section (>60% of content)

**Scenario:** "Release Notes" page includes migration tutorial
→ **Decision:** Use CHANGELOG (primary purpose is to document changes)

**Scenario:** Concept explanation followed by detailed examples
→ **Decision:** Use CONCEPT (purpose is understanding, not learning-by-doing)

**Scenario:** API docs with embedded "Getting Started" section
→ **Decision:** Use REFERENCE (primary purpose is API documentation)

### 2.4 Classification Validation (Python)

```python
from pydantic import BaseModel, Field, validator
from typing import Literal

class CanonicalPage(BaseModel):
    url: str
    title: str
    content_type: Literal["tutorial", "reference", "concept", "changelog", "faq"]
    last_verified: str
    summary: str

    @validator('content_type')
    def validate_content_type(cls, v):
        """Ensure content_type is one of the allowed values."""
        valid = {"tutorial", "reference", "concept", "changelog", "faq"}
        if v not in valid:
            raise ValueError(f"Invalid content_type: {v}. Must be one of {valid}")
        return v

# Example validation
page = CanonicalPage(
    url="https://docs.python.org/3/tutorial/index.html",
    title="The Python Tutorial",
    content_type="tutorial",  ✓ Valid
    last_verified="2025-02-05",
    summary="..."
)

# Invalid:
page = CanonicalPage(
    ...,
    content_type="guide",  ✗ Raises ValueError
)
```

---

## 3. Summary Writing Masterclass: The 280-Character Constraint

### 3.1 Understanding the Constraint

**Why 280 characters?**
- Similar to Twitter/X post length (fits one visual block)
- Equivalent to ~40-50 words of English text
- Compresses to single line on most LLM display
- Preserves information density (forces concision)

**Character counting:**
- Includes: letters, numbers, spaces, punctuation
- Excludes: YAML syntax (quotes, indentation)

```yaml
summary: "This page explains how to configure authentication in FastAPI by setting up API keys, OAuth2, and JWT tokens."
# 127 chars ✓ (well under 280)

summary: "Comprehensive guide covering JWT tokens, OAuth2 flows, password hashing, dependency injection for security, API key management, CORS configuration, and HTTPS requirements."
# 159 chars ✓ (still under 280)

summary: "This incredibly long summary attempts to describe every single aspect of the FastAPI authentication module including but not limited to JWT tokens, OAuth2, password hashing, dependency injection, API keys, CORS, HTTPS, HTTP headers, custom authentication schemes, token expiration, scopes, permissions, middleware integration, error handling, and security best practices which makes this summary completely unwieldy and difficult to parse for an LLM agent."
# 387 chars ✗ (exceeds 280 limit)
```

### 3.2 Summary Writing Formula: Verb-First, Audience-Aware

**Pattern 1: Action-Oriented (for tutorial, how-to)**
```
[Verb] [object] [outcome/benefit]

Examples:
✓ "Learn how to set up authentication in FastAPI with JWT tokens and OAuth2."
✓ "Install and configure PostgreSQL as your database layer."
✓ "Debug common errors in asyncio programming with practical examples."
```

**Pattern 2: Conceptual (for concept, explanation)**
```
[What] [is/are] [definition] [implication]

Examples:
✓ "Middleware functions intercept requests and responses, enabling cross-cutting concerns like authentication and logging."
✓ "Async/await is Python's syntax for writing concurrent code that doesn't block the event loop."
✓ "CORS policies control which domains can access your API endpoints from browsers."
```

**Pattern 3: Reference/Catalog (for reference, API docs)**
```
[Collection] [of] [what] [scope]

Examples:
✓ "Complete API reference for all Flask decorators, request handlers, and response utilities."
✓ "Comprehensive list of configuration options, environment variables, and CLI commands."
✓ "Documentation of all built-in methods for the List data structure."
```

**Pattern 4: Q&A/Troubleshooting (for faq, troubleshooting)**
```
[Question topic] — [concise answer/solution]

Examples:
✓ "Common authentication mistakes — how to avoid credential leaks, manage token expiration, and secure API keys."
✓ "Why is my async function slow? — identifying event loop blocking, optimizing I/O patterns, and using profilers."
```

### 3.3 Information Density Scoring

Measure how much semantic value you pack into 280 characters:

| Score | Definition | Example | Chars | Density |
|-------|-----------|---------|-------|---------|
| **A+** | 3+ distinct concepts, specific verbs, actionable | "Configure JWT authentication, set token expiration, implement refresh tokens for FastAPI." | 89 | 0.033 concepts/char |
| **A** | 2-3 concepts, clear action, specific domain | "Learn to use decorators for defining API endpoints, request validation, and error handling." | 92 | 0.022 concepts/char |
| **B** | 1-2 concepts, somewhat generic, vague action | "Introduction to FastAPI and how it works for building web applications." | 76 | 0.013 concepts/char |
| **C** | <1 concrete concept, filler words, generic | "A guide to FastAPI that shows you some interesting stuff about building things." | 82 | <0.013 concepts/char |
| **F** | No actionable content, pure fluff | "This page is about FastAPI." | 28 | ~0 concepts/char |

**Improving Density:**
1. Cut filler: "that", "which", "interesting", "useful", "guide to" (implied)
2. Use strong verbs: not "discusses how to do X" but "Configure X"
3. Be specific: not "web development" but "JWT authentication"
4. Quantify when possible: "3 methods to X" > "ways to X"

### 3.4 Summary Quality Scoring Rubric

Score each summary on these 3 dimensions (1-5 scale):

**Dimension 1: Information Density (Weight: 40%)**
```
5 = 3+ distinct actionable concepts, all specific to page content
4 = 2-3 concepts, at least one specific, no filler
3 = 1-2 concepts, somewhat specific, minor filler ("interesting", "guide to")
2 = 1 concept or mostly generic, significant filler
1 = No actionable info, pure fluff
```

**Dimension 2: Actionability (Weight: 30%)**
```
5 = Reader knows exactly what they'll learn/do; clear next step
4 = Reader has good idea; minor ambiguity
3 = Reader gets general sense; some ambiguity
2 = Reader uncertain whether page is relevant; vague outcome
1 = No clear purpose or use case
```

**Dimension 3: Specificity (Weight: 30%)**
```
5 = Domain-specific terminology, exact topic, no generic language
4 = Mostly specific, 1-2 generic words ("web", "programming")
3 = Mix of specific and generic, reader must guess scope
2 = Mostly generic, few specific details
1 = Entirely generic ("page", "guide", "documentation")
```

**Calculation:**
```
Quality Score = (0.40 × Density) + (0.30 × Actionability) + (0.30 × Specificity)

Example Scoring:

Summary: "Configure JWT authentication, set token expiration, implement refresh tokens for FastAPI."
  Density: 5 (3 distinct concepts, all specific)
  Actionability: 5 (reader knows exact tasks)
  Specificity: 5 (JWT, token expiration, refresh tokens, FastAPI)
  → Score: (0.40 × 5) + (0.30 × 5) + (0.30 × 5) = 5.0 (Excellent)

Summary: "This page discusses various aspects of FastAPI including some features and capabilities."
  Density: 1 (no specific concepts)
  Actionability: 1 (reader doesn't know what to do)
  Specificity: 1 (no domain-specific terms)
  → Score: (0.40 × 1) + (0.30 × 1) + (0.30 × 1) = 1.0 (Poor)
```

**Target:** Aim for score ≥ 4.0 for all summaries.

---

## 4. Page Ordering Strategy

### 4.1 Primary Ordering: By Content Type

Group pages by content_type, then order within each group:

```yaml
pages:
  # TUTORIAL entries (5 pages)
  - url: "..."
    content_type: "tutorial"
    ...

  - url: "..."
    content_type: "tutorial"
    ...

  # REFERENCE entries (15 pages)
  - url: "..."
    content_type: "reference"
    ...

  # CONCEPT entries (8 pages)
  - url: "..."
    content_type: "concept"
    ...

  # FAQ entries (3 pages)
  - url: "..."
    content_type: "faq"
    ...

  # CHANGELOG entries (2 pages)
  - url: "..."
    content_type: "changelog"
    ...
```

**Rationale for Type Ordering:**
1. TUTORIAL first (new users read tutorials)
2. REFERENCE second (developers query references)
3. CONCEPT third (conceptual depth)
4. FAQ fourth (problem-solving)
5. CHANGELOG last (historical, not primary entry points)

### 4.2 Secondary Ordering: Within Each Type

**Within TUTORIAL:** By dependency (prerequisites first)
```
1. "Getting Started" (no prerequisites)
2. "Installing Dependencies"
3. "Your First Application"
4. "Advanced Patterns"
```

**Within REFERENCE:** By importance/frequency of use
```
1. "Core API Functions" (most queried)
2. "Decorators"
3. "Configuration Options"
4. "Edge Cases & Exceptions"
```

**Within CONCEPT:** By abstraction level (low-level first)
```
1. "What is HTTP?" (foundational)
2. "Request/Response Cycle"
3. "Middleware Architecture"
4. "Advanced Patterns"
```

**Within FAQ/CHANGELOG:** By recency (newest first)

### 4.3 Page Ordering Algorithm (Python)

```python
from typing import List
from enum import Enum

class ContentType(Enum):
    TUTORIAL = 1
    REFERENCE = 2
    CONCEPT = 3
    FAQ = 4
    CHANGELOG = 5

def order_pages(pages: List[dict]) -> List[dict]:
    """
    Order pages:
    1. Primary: by content_type (tutorial → changelog)
    2. Secondary: alphabetically by title within type
    3. Tertiary: by last_verified date (newest first)
    """

    def sort_key(page):
        content_type_order = {
            "tutorial": 1,
            "reference": 2,
            "concept": 3,
            "faq": 4,
            "changelog": 5,
        }

        # Convert last_verified to sortable format (reverse for newest first)
        date_sort = page.get("last_verified", "2000-01-01")

        return (
            content_type_order.get(page["content_type"], 99),
            page.get("title", "").lower(),
            date_sort,  # Newest first (reversed later)
        )

    return sorted(pages, key=sort_key)

# Example usage:
pages = [
    {"title": "Getting Started", "content_type": "tutorial", "last_verified": "2025-01-15"},
    {"title": "API Reference", "content_type": "reference", "last_verified": "2025-02-01"},
    {"title": "FAQ", "content_type": "faq", "last_verified": "2025-01-01"},
]

ordered = order_pages(pages)
# Result: Getting Started (tutorial), API Reference (reference), FAQ (faq)
```

---

## 5. URL Normalization & Canonicalization Rules

### 5.1 Normalization Checklist

Apply these transformations to every discovered URL:

| Rule | Transform | Before | After | Reason |
|------|-----------|--------|-------|--------|
| HTTPS | HTTP → HTTPS | `http://example.com` | `https://example.com` | Security standard |
| Protocol | Add protocol if missing | `example.com/page` | `https://example.com/page` | URL validity |
| Trailing slash (domain) | Ensure single | `example.com///` | `example.com/` | Canonicality |
| Trailing slash (path) | Remove from endpoints | `example.com/page/` | `example.com/page` | Consistency |
| Query params | Remove tracking | `example.com?utm_source=x` | `example.com` | Canonicality |
| Fragments | Remove anchors | `example.com#section` | `example.com` | Anchor handling |
| Whitespace | Strip leading/trailing | ` example.com ` | `example.com` | Data quality |
| Case | Preserve site's actual case | `Example.COM/Page` | `example.com/page` | Accuracy |
| Duplicates | Collapse `/` | `example.com//page` | `example.com/page` | Validity |

### 5.2 URL Normalization Script (Python)

```python
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from typing import Optional

def normalize_url(url: str) -> str:
    """
    Normalize URL to canonical form.

    Args:
        url: Raw URL string from site audit

    Returns:
        Normalized URL suitable for llms.txt
    """

    # Step 1: Strip whitespace
    url = url.strip()

    # Step 2: Add https:// if protocol missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    # Step 3: Upgrade HTTP to HTTPS
    if url.startswith('http://'):
        url = url.replace('http://', 'https://', 1)

    # Step 4: Parse URL components
    parsed = urlparse(url)

    # Step 5: Reconstruct without query parameters and fragments
    # (fragments contain anchor links; we'll document them separately if needed)
    normalized = urlunparse((
        parsed.scheme,
        parsed.netloc.lower(),  # Lowercase domain
        parsed.path,
        parsed.params,
        '',  # Remove query string
        ''   # Remove fragment
    ))

    # Step 6: Collapse duplicate slashes (but not in ://)
    while '//' in normalized.replace('://', '', 1):
        normalized = normalized.replace('//', '/', 1)

    # Step 7: Fix scheme collapse (restore ://)
    if ':///' in normalized:
        normalized = normalized.replace(':///', '://', 1)

    # Step 8: Handle trailing slashes
    # Keep for domain root, remove for paths
    if normalized.count('/') == 2:  # Only ://
        normalized += '/'
    else:
        # Remove trailing slash from path (but not from domain)
        if normalized.endswith('/') and normalized.count('/') > 3:
            normalized = normalized.rstrip('/')

    return normalized

# Test cases:
test_urls = [
    ("http://example.com", "https://example.com/"),
    ("example.com/page?utm_source=email", "https://example.com/page"),
    ("https://example.com/page/", "https://example.com/page"),
    ("https://EXAMPLE.COM/Page", "https://example.com/Page"),
    ("https://example.com//page///", "https://example.com/page"),
    (" https://example.com ", "https://example.com"),
]

for raw, expected in test_urls:
    result = normalize_url(raw)
    status = "✓" if result == expected else "✗"
    print(f"{status} {raw:40} → {result}")
    if result != expected:
        print(f"  Expected: {expected}")
```

### 5.3 Handling Special URL Cases

**Anchor links / Fragment identifiers:**
If a page has major sections with anchors (e.g., `/api#authentication`), create separate entries if:
- The section is substantial (100+ words)
- It's a common entry point (multiple references from LLMs)
- Otherwise, include in main URL without fragment

```yaml
# ✓ Good: Major sections get separate entries
- url: "https://docs.example.com/api/auth/"
  title: "Authentication API"
  ...

# ✗ Avoid: Fragment-only URLs
- url: "https://docs.example.com/api#authentication"
  title: "..."
```

**Versioned URLs:**
If documentation has version branches (e.g., `/docs/v2/` vs `/docs/v3/`), include LATEST stable version:
```yaml
# ✓ Prefer current version
url: "https://docs.example.com/v3/tutorial/"

# ✗ Avoid outdated versions (unless changelog-relevant)
url: "https://docs.example.com/v1/tutorial/"
```

---

## 6. Worked Example: 10 Complete Page Entries

### 6.1 Real Documentation Site: FastAPI

```yaml
pages:
  # ============================================================================
  # TUTORIAL ENTRIES (Primary learning path)
  # ============================================================================

  - url: "https://fastapi.tiangolo.com/tutorial/"
    title: "Tutorial — User Guide"
    content_type: "tutorial"
    last_verified: "2025-02-05"
    summary: "Step-by-step introduction covering installation, first application, path parameters, query parameters, request bodies, response models, form data, and dependency injection."

  - url: "https://fastapi.tiangolo.com/tutorial/first-steps/"
    title: "First Steps"
    content_type: "tutorial"
    last_verified: "2025-02-05"
    summary: "Create your first FastAPI application with a GET endpoint, return JSON, and run the development server with automatic API documentation."

  - url: "https://fastapi.tiangolo.com/tutorial/request-body/"
    title: "Request Body"
    content_type: "tutorial"
    last_verified: "2025-02-05"
    summary: "Accept JSON request bodies using Pydantic models with automatic validation, serialization, and OpenAPI documentation generation."

  - url: "https://fastapi.tiangolo.com/advanced/"
    title: "Advanced User Guide"
    content_type: "tutorial"
    last_verified: "2025-02-05"
    summary: "Advanced patterns including custom response classes, custom exception handlers, middleware, GraphQL integration, and production deployment."

  # ============================================================================
  # REFERENCE ENTRIES (API documentation)
  # ============================================================================

  - url: "https://fastapi.tiangolo.com/tutorial/security/"
    title: "Security"
    content_type: "reference"
    last_verified: "2025-02-05"
    summary: "Comprehensive guide to authentication and authorization: API keys, HTTP basic auth, OAuth2 with JWT, scopes, dependencies, and CORS configuration."

  - url: "https://fastapi.tiangolo.com/reference/"
    title: "API Reference"
    content_type: "reference"
    last_verified: "2025-02-05"
    summary: "Complete API documentation for FastAPI, Starlette, Pydantic modules, including decorators, request/response classes, and utilities."

  - url: "https://fastapi.tiangolo.com/deployment/"
    title: "Deployment"
    content_type: "reference"
    last_verified: "2025-02-05"
    summary: "Deployment guides for production environments: Docker, Kubernetes, systemd, Nginx, AWS, Heroku, GCP, with HTTPS, caching, and monitoring."

  # ============================================================================
  # CONCEPT ENTRIES (Conceptual understanding)
  # ============================================================================

  - url: "https://fastapi.tiangolo.com/learn/"
    title: "Learn"
    content_type: "concept"
    last_verified: "2025-02-05"
    summary: "Conceptual foundation for FastAPI: understanding ASGI servers, async/await, type hints, OpenAPI specification, and how FastAPI leverages Python features."

  # ============================================================================
  # FAQ ENTRIES (Common questions)
  # ============================================================================

  - url: "https://fastapi.tiangolo.com/help/"
    title: "Help — Getting Help"
    content_type: "faq"
    last_verified: "2025-02-05"
    summary: "Common questions about troubleshooting, debugging, performance optimization, getting help from community, and reporting issues."

  # ============================================================================
  # CHANGELOG ENTRIES (Version history)
  # ============================================================================

  - url: "https://fastapi.tiangolo.com/release-notes/"
    title: "Release Notes"
    content_type: "changelog"
    last_verified: "2025-02-05"
    summary: "Version history, breaking changes, migration guides, new features, deprecations from FastAPI releases including v0.1 to v0.120+."
```

---

## 7. Before & After: Summary Writing Examples

### 7.1 Bad vs. Good Summary Pairs (10 Examples)

| # | Page Context | Bad Summary | Good Summary | Issues Fixed |
|---|---|---|---|---|
| 1 | Django Authentication Tutorial | "This page is about authentication." | "Configure user authentication with Django's built-in auth system: user models, password hashing, login views, and permissions." | Generic → specific, added action verbs |
| 2 | Python asyncio Reference | "Learn about async stuff." | "Master async/await syntax, event loops, coroutines, tasks, futures, and task cancellation for concurrent Python programming." | Vague → concrete concepts, actionable |
| 3 | PostgreSQL Indexes Concept | "Indexes help databases work faster." | "Indexes accelerate query performance by creating sorted data structures; understand B-tree indexes, hash indexes, and when to use each." | Simplified → nuanced, educational |
| 4 | Flask Setup Guide | "A guide to Flask." | "Install Flask, create your first application, set up routes, render templates, debug with the development server, and handle static files." | Title-like → action steps |
| 5 | Kubernetes Concepts | "Kubernetes is a container orchestration platform used in cloud computing environments that helps manage and deploy applications." | "Understand Kubernetes architecture: pods, services, deployments, StatefulSets, ingress, and networking for container orchestration." | Wordy → dense, specific |
| 6 | Node.js File I/O | "This page discusses file operations." | "Read, write, and manage files using Node.js fs module: synchronous vs. asynchronous APIs, streams, and error handling." | Generic → specific APIs, context |
| 7 | Docker Networking FAQ | "Questions about Docker networking." | "Docker networking: overlay networks, host networking, port binding, DNS resolution, multi-container communication, and network drivers." | Question-focused → concept list |
| 8 | React Hooks Changelog | "Version 3.0 released with improvements." | "React Hooks v3.0: new useReducer hook, context performance improvements, breaking API changes, and migration guide from v2." | Vague → specific changes, version |
| 9 | SQL Transactions Tutorial | "How to use transactions in databases." | "Implement ACID transactions: BEGIN, COMMIT, ROLLBACK, savepoints, isolation levels, deadlock handling, and distributed transactions." | Abstract → concrete SQL, actionable |
| 10 | AWS S3 Reference Docs | "Information about AWS S3 storage service." | "S3 API reference: bucket operations, object CRUD, presigned URLs, access control, server-side encryption, cross-region replication, and versioning." | Generic AWS → specific S3 APIs |

### 7.2 Detailed Critique of 3 Examples

**Example 1: Django Authentication**

❌ **Bad Summary:**
```
"This page is about authentication."
```
Problems:
- Generic (doesn't differentiate from 100 other auth pages)
- No action verb (reader doesn't know what they'll learn)
- No specificity (no mention of "Django", "password hashing", etc.)
- Quality score: 1.2/5.0 (Poor)

✅ **Good Summary:**
```
"Configure user authentication with Django's built-in auth system: user models, password hashing, login views, and permissions."
```
Improvements:
- Action verb: "Configure" (specific, task-oriented)
- Domain specificity: "Django", "user models", "password hashing"
- Enumerated concepts: 4 distinct topics reader will learn
- Audience: Developers building auth systems
- Quality score: 4.8/5.0 (Excellent)

---

**Example 5: Kubernetes Concepts**

❌ **Bad Summary:**
```
"Kubernetes is a container orchestration platform used in cloud computing environments that helps manage and deploy applications."
```
Problems:
- Overly long (104 chars) and still vague
- Filler words: "used in", "helps", "that"
- No specific concepts (pods, services, ingress?)
- Generic definition language (not action-oriented)
- Quality score: 1.8/5.0 (Poor)

✅ **Good Summary:**
```
"Understand Kubernetes architecture: pods, services, deployments, StatefulSets, ingress, and networking for container orchestration."
```
Improvements:
- Tight (120 chars), densely informative
- Action: "Understand" signals conceptual depth
- Specific components: pods, services, deployments, StatefulSets, ingress
- Addresses: architecture, networking
- Quality score: 4.7/5.0 (Excellent)

---

**Example 7: Docker Networking FAQ**

❌ **Bad Summary:**
```
"Questions and answers about Docker networking features."
```
Problems:
- Format-focused (says "Q&A" rather than content)
- No specifics (which networking features?)
- No actionable outcome
- Passive voice ("Questions about")
- Quality score: 2.1/5.0 (Poor)

✅ **Good Summary:**
```
"Docker networking: overlay networks, host networking, port binding, DNS resolution, multi-container communication, and network drivers."
```
Improvements:
- Active voice (presents topics directly)
- Specific networking types: overlay, host, bridge (implied)
- Operational concerns: port binding, DNS, multi-container
- Covers both conceptual (network drivers) and practical (port binding)
- Quality score: 4.9/5.0 (Excellent)

---

## Deliverables Checklist

- [ ] CanonicalPage field validation rules documented with 5+ examples
- [ ] Content_type classification decision tree finalized
- [ ] 280-character constraint explained with formula and examples
- [ ] Summary quality scoring rubric (3 dimensions × 5-point scale) created
- [ ] 10+ before/after summary pairs reviewed and scored
- [ ] Page ordering algorithm implemented and tested
- [ ] URL normalization script tested on 20+ real URLs
- [ ] 10 complete worked example page entries written for real site
- [ ] All code examples tested for syntax and logic correctness
- [ ] Examples demonstrate all 5 content_type classifications
- [ ] Documentation passes readability review

---

## Acceptance Criteria

1. **Completeness:** All 7 sections present with working examples
2. **Clarity:** Decision trees and rules are unambiguous
3. **Rigor:** Quality scoring is reproducible; 10+ trained authors score similarly
4. **Actionability:** Authors can write high-quality summaries after reading section 3
5. **Validation:** Normalization script handles 95%+ of real-world URLs correctly
6. **Examples:** Worked examples span all content types and score ≥4.0 on rubric

---

## Next Step Pointer

→ **Layer 2: Concept Entries & Graph Encoding** (v0.2.3c)

Layer 2 consumes the validated page list from Layer 1 and creates the concept graph. You will:
- Extract semantic relationships between pages (depends_on, related_pages)
- Author Concept YAML entries with definitions and anti-patterns
- Encode concept dependency graphs in flat YAML lists
- Validate graph consistency (topological sort, no cycles)
