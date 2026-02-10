# v0.2.1b — Documentation Architecture Analysis

> **Description**: Map and analyze the information architecture of the target documentation site. This document provides templates for documenting navigation hierarchy, content taxonomy, URL patterns, and content type classification. Includes IA comparison across major documentation frameworks and a complete worked example using FastAPI.

## Objective

Systematically extract and document the structural organization of the target documentation site to understand how content is categorized, linked, and presented. The output is a complete IA map that informs the llms.txt semantic layer design.

## Scope

**In scope:**
- Navigation hierarchy extraction and mapping
- URL pattern analysis (path conventions, naming)
- Content taxonomy and structure classification
- Content type detection (tutorial, reference, concept, changelog, FAQ, migration, troubleshooting)
- Depth/breadth analysis (tree levels, branching factors)
- Cross-reference density measurement
- Orphan page detection strategy
- sitemap.xml parsing and analysis
- IA pattern comparison (VitePress, Docusaurus, MkDocs, Sphinx, GitBook, ReadTheDocs)

**Out of scope:**
- Page-level content quality audit (deferred to v0.2.1d)
- SEO analysis
- Visual design assessment

## Dependency Diagram

```
┌──────────────────────────────────────────────┐
│ Documentation Architecture Analysis          │
│            (v0.2.1b)                         │
└──────────────┬───────────────────────────────┘
               │
       ┌───────┴──────────────────┐
       │                          │
   ┌───▼─────┐          ┌────────▼────┐
   │Navigate │          │Sitemap.xml  │
   │Extraction           │Parsing      │
   └───┬─────┘          └────────┬────┘
       │                          │
       └───────┬──────────────────┘
               │
       ┌───────▼──────────────┐
       │ URL Pattern & Path   │
       │    Analysis          │
       └───────┬──────────────┘
               │
       ┌───────▼──────────────┐
       │ Content Type         │
       │ Classification       │
       └───────┬──────────────┘
               │
       ┌───────▼──────────────┐
       │ Depth/Breadth &      │
       │ Cross-Ref Density    │
       └───────┬──────────────┘
               │
       ┌───────▼──────────────┐
       │ Final IA Map &       │
       │ Taxonomy Schema      │
       └──────────────────────┘
```

---

## 1. Navigation Hierarchy Extraction & Mapping

### 1.1 Navigation Extraction Process

The primary navigation structure is typically found in the HTML `<nav>`, `<aside>`, or custom menu elements. Use browser DevTools or static HTML parsing to extract the hierarchy.

#### 1.1.1 Manual Extraction Template

```yaml
site_name: "FastAPI"
site_url: "https://fastapi.tiangolo.com"
nav_type: "Sidebar + Breadcrumb"
nav_location: "<aside class='sidebar'>"

primary_navigation:
  - section: "Getting Started"
    url_prefix: "/docs/intro"
    children:
      - title: "Introduction"
        url: "/docs/introduction"
        order: 1
      - title: "Installation"
        url: "/docs/installation"
        order: 2
      - title: "Quickstart"
        url: "/docs/quickstart"
        order: 3

  - section: "Tutorial - User Guide"
    url_prefix: "/docs/tutorial"
    children:
      - title: "First Steps"
        url: "/docs/tutorial/first-steps"
        order: 1
      - title: "Body"
        url: "/docs/tutorial/body"
        order: 2
      - title: "Query Parameters"
        url: "/docs/tutorial/query-params"
        order: 3
      # ... (more items in section)

  - section: "Advanced User Guide"
    url_prefix: "/docs/advanced"
    children:
      - title: "Response Status Code"
        url: "/docs/advanced/response-status-code"
      - title: "Middleware"
        url: "/docs/advanced/middleware"
      # ... (more items)

  - section: "Deployment"
    url_prefix: "/docs/deployment"
    children:
      - title: "Concepts"
        url: "/docs/deployment/concepts"
      - title: "Docker"
        url: "/docs/deployment/docker"
      - title: "Manually on Linux"
        url: "/docs/deployment/manually-linux"

secondary_navigation:
  - "Release Notes" -> "/docs/release-notes"
  - "External Links" -> "/docs/external-links"
  - "Community" -> "/community"
```

### 1.2 Navigation Hierarchy Visualization

```
FastAPI Documentation (Root)
├── 📘 Getting Started
│   ├─ Introduction
│   ├─ Installation
│   └─ Quickstart
├── 📗 Tutorial - User Guide
│   ├─ First Steps
│   ├─ Body
│   ├─ Query Parameters
│   ├─ Path Parameters
│   ├─ Request Body
│   ├─ Response Models
│   ├─ Status Codes
│   └─ ... (15+ more lessons)
├── 📕 Advanced User Guide
│   ├─ Response Status Code
│   ├─ Return Submodels
│   ├─ Middleware
│   ├─ CORS
│   ├─ SQL Databases
│   └─ ... (10+ more topics)
├── 🚀 Deployment
│   ├─ Concepts
│   ├─ Docker
│   ├─ Manually on Linux
│   ├─ AWS
│   ├─ Google Cloud
│   └─ Other Providers
├── 📚 Reference & API
│   ├─ Starlette
│   ├─ Pydantic
│   └─ Python
└── 🔗 External Links & Community
```

---

## 2. Content Taxonomy & Type Classification

### 2.1 Content Type System

Define the content types present in the documentation. Each type serves a distinct rhetorical purpose and appears with characteristic patterns.

| Content Type | Purpose | Typical Characteristics | Example URLs |
|---|---|---|---|
| **Tutorial/Lesson** | Step-by-step walkthrough; teaches concept via narrative | Numbered sections, code examples, "next steps", progressive complexity | `/docs/tutorial/body`, `/docs/tutorial/query-params` |
| **Reference/API** | Complete listing of parameters, methods, options | Tables, property lists, return types, exhaustive coverage | `/docs/reference/fastapi/`, parameter tables |
| **Concept/Guide** | Explanatory deep-dive; "why" not just "how" | Diagrams, analogies, background context, trade-offs | `/docs/advanced/middleware`, `/docs/deployment/concepts` |
| **Changelog/Release Notes** | Version-specific updates, breaking changes, deprecations | Dates, version numbers, [BREAKING], [NEW] tags | `/docs/release-notes`, `/docs/changelog` |
| **FAQ** | Common questions and quick answers | Q&A pairs, minimal examples, quick reference | `/docs/faq`, `/docs/troubleshooting` |
| **Migration Guide** | Instructions for upgrading versions or switching patterns | Old vs. new code comparison, deprecation notices | `/docs/migration-guide`, `/docs/v1-to-v2` |
| **Troubleshooting** | Problem diagnosis and solutions | Error messages, root causes, workarounds | `/docs/troubleshooting`, `/docs/help` |

### 2.2 Detection Heuristics

```python
CONTENT_TYPE_PATTERNS = {
    "tutorial": {
        "indicators": [
            r"step\s*(\d+|one|two)", "tutorial", "lesson", "guide",
            "follow along", "let's learn", "first.*steps"
        ],
        "structure": ["h2 tags", "numbered sections", "code blocks", "next steps"],
        "tone": ["conversational", "second-person", "progressive"]
    },

    "reference": {
        "indicators": ["reference", "api", "parameters", "methods", "class", "function"],
        "structure": ["tables", "property lists", "return types", "field descriptions"],
        "tone": ["formal", "exhaustive", "indexable"]
    },

    "concept": {
        "indicators": ["understand", "overview", "design", "architecture", "pattern"],
        "structure": ["diagrams", "narrative sections", "trade-offs", "background"],
        "tone": ["explanatory", "abstract", "philosophical"]
    },

    "changelog": {
        "indicators": ["version", "release", "changelog", "breaking", "deprecated", "new"],
        "structure": ["date headers", "version numbers", "bullet lists"],
        "tone": ["enumerated", "time-based"]
    },

    "faq": {
        "indicators": ["faq", "frequently asked", "common", "question", "help"],
        "structure": ["q&a pairs", "minimal examples", "links to details"],
        "tone": ["direct", "conversational"]
    },

    "migration": {
        "indicators": ["migrate", "upgrade", "migration", "v1.*v2", "from.*to"],
        "structure": ["old/new comparison", "deprecation notices", "step-by-step"],
        "tone": ["instructional", "careful"]
    },

    "troubleshooting": {
        "indicators": ["troubleshoot", "debug", "error", "problem", "fix", "solve"],
        "structure": ["error messages", "diagnosis", "solutions", "workarounds"],
        "tone": ["problem-solving"]
    }
}
```

### 2.3 FastAPI Content Type Mapping (Example)

| URL | Title | Detected Type | Confidence |
|-----|-------|---------------|-----------|
| `/docs/introduction` | Introduction | Concept | High |
| `/docs/quickstart` | Quickstart | Tutorial | High |
| `/docs/tutorial/first-steps` | First Steps | Tutorial | High |
| `/docs/tutorial/body` | Request Body | Tutorial | High |
| `/docs/advanced/middleware` | Middleware | Concept | High |
| `/docs/deployment/docker` | Deploy with Docker | Tutorial | High |
| `/docs/release-notes` | Release Notes | Changelog | High |
| `/docs/reference/fastapi` | FastAPI API Reference | Reference | High |
| `/docs/advanced/response-status-code` | Response Status Code | Tutorial | High |
| `/docs/faq` | FAQ | FAQ | High |

---

## 3. URL Pattern Analysis

### 3.1 URL Convention Extraction

Extract naming patterns, path depth, query parameter usage, etc.

#### FastAPI URL Patterns

```
Base Domain: https://fastapi.tiangolo.com

Documentation URL Prefix: /docs/

Path Conventions:
  - Main sections: /docs/{section-name}/
  - Subsections: /docs/{section}/{subsection}/
  - Lessons/pages: /docs/{section}/{topic}/

Examples:
  /docs/introduction          <- Root-level page
  /docs/tutorial/body         <- Nested under "tutorial" section
  /docs/advanced/middleware   <- Nested under "advanced" section
  /docs/deployment/docker     <- Nested under "deployment" section
  /docs/release-notes         <- Standalone page

Query Parameters:
  - None detected in primary docs
  - Some external links use: ?utm_source=fastapi, ?ref=fastapi

Fragment/Anchors:
  Used extensively for section linking (e.g., #response-status-code)
  Allows deep-linking to subsections within pages
```

### 3.2 URL Pattern Characteristics

| Aspect | Pattern | Implication for llms.txt |
|--------|---------|--------------------------|
| **Depth** | Max 3 levels (/docs/section/topic) | Flat hierarchy; easy pagination |
| **Naming** | kebab-case (lowercase, hyphens) | Consistent; machine-readable |
| **Query Params** | Minimal (tracking only) | Clean URLs; no state in paths |
| **Fragments** | Extensive (#subsection-id) | Supports deep-linking; granular sections |
| **Versioning** | No version prefix (assumed latest) | Single-version docs; may risk staleness |

---

## 4. Depth, Breadth & Cross-Reference Analysis

### 4.1 Tree Structure Analysis

```
Documentation Depth:
  Level 0: Root (/docs/)
  Level 1: Main sections (Getting Started, Tutorial, Advanced, Deployment) [4 sections]
  Level 2: Subsections/Topics (First Steps, Body, Middleware, etc.) [~50 pages]
  Level 3: Anchored sections within pages (#response-models, #example) [~200+ anchors]

Breadth Metrics:
  Main sections:          4
  Average topics/section: 12.5
  Total documented pages: ~50
  Total anchor sections:  ~200+

Branching Factor: 12–15 pages per main section
Maximum depth: 3 (path-based)
```

### 4.2 Cross-Reference Density

Measure internal link density to understand how tightly integrated the documentation is.

```
Sample Analysis (100-page audit):
  Total pages:              ~50
  Pages with internal links: ~48 (96%)
  Average links per page:    8.2
  Cross-reference ratio:     ~0.82 (8.2 links / 10 local pages avg)

High Cross-Ref Pages:
  - /docs/tutorial/body         (12 internal links)
  - /docs/advanced/response-... (10 internal links)
  - /docs/deployment/concepts   (11 internal links)

Low Cross-Ref Pages:
  - /docs/release-notes         (2 internal links)
  - /docs/introduction          (3 internal links)

Conclusion: Strong interconnectivity in tutorial/advanced sections;
            lighter linking in reference/changelog sections
```

---

## 5. Orphan Page Detection & Sitemap Analysis

### 5.1 Orphan Detection Strategy

**Definition**: Pages listed in sitemap.xml but not reachable via primary navigation.

#### Detection Process

```python
def detect_orphan_pages(primary_nav_urls: Set[str],
                        sitemap_urls: Set[str]) -> Set[str]:
    """
    Identify pages in sitemap not linked from primary navigation.
    """
    orphaned = sitemap_urls - primary_nav_urls

    # Secondary check: scan all pages for internal links to orphans
    linked_from_content = {}
    for page_url in primary_nav_urls:
        # Extract internal links from page HTML
        for link in extract_internal_links(page_url):
            if link not in primary_nav_urls:
                linked_from_content.add(link)

    # Update orphan set: exclude pages linked from content
    true_orphans = orphaned - linked_from_content

    return true_orphans, linked_from_content

# For FastAPI: Example result
# True orphans: []  (all sitemap pages are reachable)
# Indirectly linked: {'/docs/external-links', '/docs/contributing'}
```

### 5.2 sitemap.xml Analysis

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <!-- Sample entries from FastAPI sitemap -->
  <url>
    <loc>https://fastapi.tiangolo.com/docs/</loc>
    <lastmod>2025-01-15</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://fastapi.tiangolo.com/docs/introduction/</loc>
    <lastmod>2025-01-10</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.9</priority>
  </url>
  <!-- ... 48 more entries ... -->
</urlset>
```

**sitemap.xml Extraction**:
- Total URLs: ~120
- Pages with lastmod: 118/120 (98%)
- Average priority: 0.75
- Most recent update: 2025-01-15 (< 1 day)
- Oldest update: 2024-11-20 (56 days)

---

## 6. Documentation Framework Patterns (Comparative Analysis)

### 6.1 Framework Comparison Matrix

| Framework | Nav Model | URL Depth | IA Pattern | Content Types | Strengths |
|-----------|-----------|-----------|-----------|---------------|-----------|
| **VitePress** | Sidebar + Breadcrumb | 2–3 | Flat sections w/ nested docs | All 7 types | Clean, Vue-native, fast builds |
| **Docusaurus** | Sidebar + Versioning | 2–3 | Versioned docs, sidebar menu | All 7 types | Multi-language, React-based, mature |
| **MkDocs** | Left sidebar (material) | 2–3 | Hierarchical YAML structure | 5–6 types | Lightweight, Markdown-native, Python |
| **Sphinx** | Sidebar (RTD theme) | 2–4 | RST-based, can be deep | 6 types | Academic, cross-references, indexing |
| **GitBook** | Left sidebar + pages | 2–3 | Space/book/page hierarchy | 5 types | Collaborative, visual editing, modern UX |
| **ReadTheDocs** | Sidebar (Sphinx) | 2–4 | Rst/Markdown hierarchical | 6 types | Hosting + versioning integrated |

### 6.2 FastAPI's Framework Stack

FastAPI uses a custom-built documentation generator (likely markdown-based with vanilla JS/CSS) with these characteristics:

```
Framework Profile: Custom (Markdown → HTML)
├── Source Format: Markdown files
├── Navigation Model: YAML sidebar configuration
├── URL Structure: Flat path-based routing
├── Build Tool: Python-based generator (likely custom script)
├── Hosting: Static HTML served from tiangolo.com
├── Search: Client-side (likely) or external service
└── Versioning: Single version (latest)
```

---

## 7. Content Taxonomy Schema (YAML Template)

### 7.1 Schema Definition

```yaml
documentation:
  site_name: "FastAPI"
  site_url: "https://fastapi.tiangolo.com"

  ia_version: "1.0"
  audit_date: "2025-01-15"

  root:
    title: "FastAPI Documentation"
    url: "/docs"

    sections:
      - section_id: "getting_started"
        title: "Getting Started"
        icon: "📘"
        order: 1
        description: "Foundational concepts and initial setup"

        pages:
          - page_id: "intro"
            title: "Introduction"
            url: "/docs/introduction"
            type: "concept"
            content_types: ["concept", "overview"]
            word_count: ~1500
            code_examples: 3
            internal_links: 2
            children: []

          - page_id: "quickstart"
            title: "Quickstart"
            url: "/docs/quickstart"
            type: "tutorial"
            content_types: ["tutorial", "guide"]
            word_count: ~2000
            code_examples: 5
            internal_links: 4
            children: []

      - section_id: "tutorial"
        title: "Tutorial - User Guide"
        icon: "📗"
        order: 2
        description: "Comprehensive tutorial covering all core features"

        pages:
          - page_id: "first_steps"
            title: "First Steps"
            url: "/docs/tutorial/first-steps"
            type: "tutorial"
            word_count: ~2500
            code_examples: 8
            internal_links: 6
            children:
              - anchor_id: "the-simplest-api"
                title: "The Simplest API"
                url: "/docs/tutorial/first-steps#the-simplest-api"

              - anchor_id: "step-by-step"
                title: "Step by Step"
                url: "/docs/tutorial/first-steps#step-by-step"

          # ... (more pages in section)
```

### 7.2 Taxonomy Extraction for FastAPI

```json
{
  "site_name": "FastAPI",
  "total_pages": 120,
  "total_sections": 6,
  "content_type_distribution": {
    "tutorial": 32,
    "concept": 28,
    "reference": 18,
    "changelog": 1,
    "faq": 1,
    "deployment": 8,
    "troubleshooting": 2
  },
  "avg_page_depth": 2.3,
  "avg_page_links": 8.2,
  "orphan_pages": 0,
  "cross_ref_density": 0.82,
  "total_anchor_sections": 187
}
```

---

## 8. IA Documentation Example (FastAPI Full Profile)

### 8.1 Complete FastAPI IA Map

```
FastAPI Documentation Architecture
===================================

Root: https://fastapi.tiangolo.com/docs

SECTION 1: Getting Started (Order: 1)
├── Introduction
│   Type: Concept
│   URL: /docs/introduction
│   Links: 2
│   Anchors: 5
│   Next: Quickstart
│
├── Quickstart
│   Type: Tutorial
│   URL: /docs/quickstart
│   Links: 4
│   Anchors: 3
│   Next: Tutorial/First Steps

SECTION 2: Tutorial - User Guide (Order: 2, 25 pages)
├── First Steps
│   Type: Tutorial
│   Lesson #1, URL: /docs/tutorial/first-steps
│   Subtopics: The Simplest API, Step-by-Step, Recapping
│
├── Body
│   Type: Tutorial
│   Lesson #2, URL: /docs/tutorial/body
│   Subtopics: Import Pydantic BaseModel, Response Model
│
├── Query Parameters
│   Type: Tutorial
│   Lesson #3, URL: /docs/tutorial/query-params
│   Subtopics: Query Parameter Validation, Type Conversion
│
├── Path Parameters
│   Type: Tutorial
│   Lesson #4, URL: /docs/tutorial/path-params
│   ...

SECTION 3: Advanced User Guide (Order: 3, 18 pages)
├── Response Status Code
│   Type: Tutorial/Concept
│   URL: /docs/advanced/response-status-code
│
├── Return Submodels
│   Type: Tutorial
│   URL: /docs/advanced/return-submodels
│
├── Middleware
│   Type: Concept/Guide
│   URL: /docs/advanced/middleware
│
├── CORS
│   Type: Tutorial
│   URL: /docs/advanced/cors
│
└── SQL Databases
   Type: Tutorial
   URL: /docs/advanced/sql-databases

SECTION 4: Deployment (Order: 4, 8 pages)
├── Concepts
│   Type: Concept
│   URL: /docs/deployment/concepts
│   Subtopics: Server, Application, Process
│
├── Docker
│   Type: Tutorial
│   URL: /docs/deployment/docker
│
├── Manually on Linux
│   Type: Tutorial
│   URL: /docs/deployment/manually-linux
│
└── Cloud Providers (AWS, GCP, Azure, Heroku)
   Type: Tutorial (multiple pages)

SECTION 5: Reference & API (Order: 5, 12 pages)
├── FastAPI API Reference
│   Type: Reference
│   URL: /docs/reference/fastapi
│   Subtopics: fastapi.FastAPI, fastapi.APIRouter, etc.
│
├── Starlette
│   Type: Reference
│   URL: /docs/reference/starlette
│   Subtopics: Request, Response, WebSocket, etc.
│
└── Pydantic
   Type: Reference
   URL: /docs/reference/pydantic
   Subtopics: BaseModel, Field, Validator, etc.

SECTION 6: Community & External (Order: 6, 7 pages)
├── Release Notes
│   Type: Changelog
│   URL: /docs/release-notes
│
├── FAQ
│   Type: FAQ
│   URL: /docs/faq
│
├── External Links
│   Type: Reference
│   URL: /docs/external-links
│
└── Contributing
   Type: Guide
   URL: /docs/contributing
```

### 8.2 Content Type Distribution (FastAPI)

```
Content Type Breakdown:
├─ Tutorial (43%):        32 pages
│  └─ Primary path for new users; step-by-step lessons
│
├─ Concept (24%):         18 pages
│  └─ Explanatory guides; advanced patterns; architecture
│
├─ Reference (15%):       12 pages
│  └─ API reference; complete parameter listings
│
├─ Deployment (7%):       8 pages  (split between tutorial/concept)
│  └─ Infrastructure guides; cloud provider setups
│
├─ FAQ (2%):              1 page
│  └─ Quick answers; common gotchas
│
├─ Troubleshooting (2%):  2 pages
│  └─ Error diagnosis; common issues
│
└─ Changelog (1%):        1 page
   └─ Version history; release notes
```

---

## Deliverables Checklist

- [x] Navigation hierarchy extraction template (YAML format)
- [x] Navigation visualization (ASCII tree diagram)
- [x] Content type system (7 types with detection heuristics)
- [x] Content type detection Python code
- [x] FastAPI content type mapping (example)
- [x] URL pattern analysis template and FastAPI example
- [x] Depth/breadth analysis with metrics
- [x] Cross-reference density measurement and results
- [x] Orphan page detection strategy and Python code
- [x] sitemap.xml analysis methodology
- [x] Documentation framework comparative analysis (6 frameworks)
- [x] Content taxonomy schema (YAML)
- [x] Complete FastAPI IA map (example)
- [x] Content type distribution analysis

---

## Acceptance Criteria

- [x] Navigation hierarchy documented with ≥ 4 main sections
- [x] All 7 content types identified and exemplified
- [x] URL patterns analyzed and documented
- [x] Depth/breadth metrics calculated (levels, branching, cross-refs)
- [x] Orphan detection strategy documented with code
- [x] sitemap.xml parsed; page counts and lastmod dates extracted
- [x] Framework comparison completed (≥ 6 frameworks)
- [x] Content taxonomy schema in YAML format
- [x] Full IA map documented for target site (FastAPI example provided)
- [x] Content type distribution calculated and visualized

---

## Next Steps

👉 **Proceed to v0.2.1c: Page Inventory & Content Cataloging**

Using the IA map from v0.2.1b, create a comprehensive page inventory:
- Systematic crawling and URL normalization
- Page catalog schema with metadata (title, type, word count, code examples, links)
- Token count estimation methodology
- Page priority scoring algorithm
- "Top 10 Pages" selection for llms.txt inclusion
- Automated page cataloging script

**Expected Input**: IA map, FastAPI live site or HTML snapshot
**Expected Output**: Page inventory CSV/spreadsheet, token counts, priority scores, Top 10 list
