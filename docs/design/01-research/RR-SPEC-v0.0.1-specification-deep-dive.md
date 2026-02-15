# v0.0.1 — Specification Deep Dive

> **Task:** Study the official llms.txt specification thoroughly and document key findings.
> 

---

## Task Overview

---

## Primary Resource

### [llmstxt.org](http://llmstxt.org)

**URL:** [https://llmstxt.org](https://llmstxt.org)

**Author:** Jeremy Howard ([fast.ai](http://fast.ai), [Answer.AI](http://Answer.AI))

**Published:** September 3, 2024

---

## 📋 Specification Summary

### Purpose

A proposal to standardize on using an `/llms.txt` file to provide information to help LLMs use a website **at inference time**.

### Problem Statement

> "Large language models increasingly rely on website information, but face a critical limitation: **context windows are too small** to handle most websites in their entirety. Converting complex HTML pages with navigation, ads, and JavaScript into LLM-friendly plain text is both difficult and imprecise."
> 

### Core Proposal

1. Add a `/llms.txt` markdown file to websites for LLM-friendly content
2. Provide brief background, guidance, and links to detailed markdown files
3. Optionally serve `.md` versions of HTML pages at the same URL + `.md`

---

## 📐 File Format Specification

### Location

- **Primary:** `/llms.txt` (root path of website)
- **Optional:** Can be in a subpath (e.g., `/docs/llms.txt`)

### Format

**Markdown** — specifically chosen because:

- Most widely understood by language models
- Human-readable AND machine-parseable
- Can be processed with standard programmatic tools (parsers, regex)

### Required Sections (in order)

### File List Format

```markdown
## Section Name

- [Link Title](URL): Optional notes about the file
- [Another Link](URL)
```

### Special Section: "Optional"

> **Important:** If an H2 section is named "Optional", the URLs there can be **skipped** when a shorter context is needed. Use for secondary/supplementary information.
> 

---

## 📝 Example from Spec

```markdown
# Title

> Optional description goes here

Optional details go here

## Section name

- [Link title](URL): Optional link details

## Optional

- [Link title](URL)
```

### Real Example (FastHTML)

```markdown
# FastHTML

> FastHTML is a python library which brings together Starlette, Uvicorn, HTMX, and fastcore's `FT` "FastTags" into a library for creating server-rendered hypermedia applications.

Important notes:

- Although parts of its API are inspired by FastAPI, it is *not* compatible with FastAPI syntax
- FastHTML is compatible with JS-native web components but not with React, Vue, or Svelte

## Docs

- [FastHTML quick start](URL): A brief overview of many FastHTML features
- [HTMX reference](URL): Brief description of all HTMX attributes...

## Examples

- [Todo list application](URL): Detailed walk-thru of a complete CRUD app...

## Optional

- [Starlette full documentation](URL): A subset of the Starlette documentation...
```

---

## 🔗 Companion Proposal: .md URLs

The spec also proposes:

- HTML pages should have a `.md` version at the same URL + `.md`
- Example: [`https://example.com/docs/intro`](https://example.com/docs/intro) → [`https://example.com/docs/intro.md`](https://example.com/docs/intro.md)
- For URLs without file names: append [`index.html.md`](http://index.html.md)

---

## 🛠️ Processing & Expansion

The spec does **NOT** mandate how to process the file. Examples include:

### FastHTML's Approach (Reference Implementation)

- Uses `llms_txt2ctx` CLI tool (from `AnswerDotAI/llms-txt` package)
- Creates XML-structured expanded files using fastcore's FT (FastTags): `<project>` root → `<section_name>` per H2 → `<doc>` per linked document
- Two versions: with/without Optional URLs (default is **without** — `optional=False`)
- Strips HTML comments and base64 images from fetched content
- Supports parallel document fetching via `n_workers`

### Reference Parser Behavior (from `miniparse.py`)

Analysis of the canonical Python parser reveals behavioral details not explicit in the spec text:

- **Blockquote capture is single-line.** The regex `^>\s*(?P<summary>.+?$)` matches only one line. Multi-line blockquotes are not handled by the reference parser.
- **Section splitting is H2-only.** The regex `^##\s*(.*?$)` creates sections at H2 headings exclusively. H3+ headings are content within the parent H2 section.
- **"Optional" matching is case-sensitive and exact.** The check `k != 'Optional'` (capital O) does not recognize aliases.
- **Link parsing regex:** `-\s*\[(?P<title>[^\]]+)\]\((?P<url>[^\)]+)\)(?::\s*(?P<desc>.*))?`
- **Freeform content** between the blockquote and first H2 is captured as a single "info" blob via `(?P<info>.*)` with `re.DOTALL`.

> **Implications for DocStratum:** Several of DocStratum's design decisions extend beyond the reference parser's behavior. Multi-line blockquote support, Optional section aliases (supplementary, appendix, extras), and H3 sub-section awareness are all DocStratum extensions. These should be explicitly labeled as such in the standards documentation to distinguish between "spec-compliant behavior" and "DocStratum-extended behavior."

---

## 🆚 Relationship to Existing Standards

### Key Distinction

> "`robots.txt` is generally used to let automated tools know what access to a site is considered acceptable... On the other hand, `llms.txt` information will often be used **on demand** when a user explicitly requests information about a topic."
> 

---

## 📚 Best Practices from Spec

<aside>

**Guidelines for effective llms.txt files:**

- Use concise, clear language
- Include brief, informative descriptions with links
- Avoid ambiguous terms or unexplained jargon
- Test with multiple LLMs to verify they can answer questions
</aside>

---

## 🌐 Ecosystem Resources

### Directories

- [llmstxt.site](http://llmstxt.site) — Community directory
- [directory.llmstxt.cloud](http://directory.llmstxt.cloud) — Another directory

### Tools & Integrations

---

## 🔍 Key Findings for DocStratum

### What the Spec DOES Define

- [x]  File location (`/llms.txt`)
- [x]  Basic structure (H1, blockquote, content, H2 file lists)
- [x]  Link format (`[Title](URL): notes`)
- [x]  Special "Optional" section meaning
- [x]  Markdown as the format

### What the Spec does NOT Define

- ❌ Maximum file size or token limit
- ❌ Required metadata fields
- ❌ Versioning scheme
- ❌ Validation schema
- ❌ Caching recommendations
- ❌ Multi-language support
- ❌ Concept/terminology definitions
- ❌ Example Q&A pairs
- ❌ Formal grammar or parsing rules (the reference parser is regex-based with no formal spec)
- ❌ Error handling for malformed input (the reference parser silently fails or crashes)
- ❌ Multi-line blockquote handling (reference parser only captures single-line)
- ❌ Sub-section semantics (H3+ headings are undefined — treated as content by reference parser)

### Opportunities for DocStratum

1. **Structured schema** — Add Pydantic validation
2. **Concept taxonomy** — Define key terms and relationships
3. **Anti-patterns** — Document what NOT to do
4. **Few-shot examples** — Include sample Q&A
5. **Extended metadata** — Version, last updated, maintainer

---

## ✅ Research Checklist

### Core Specification

- [x]  Read the full specification document
- [x]  Identify required vs optional sections
- [x]  Note the recommended file location (`/llms.txt`)
- [x]  Understand the Markdown-based format
- [x]  Document versioning information (none defined)

### Format Analysis

- [x]  File structure documented
- [x]  Section organization defined
- [x]  Metadata: minimal (just title required)
- [x]  Link format: `[Title](URL): notes`
- [x]  Max file size: NOT specified

### Philosophy & Intent

- [x]  Created to help LLMs use websites at inference time
- [x]  Solves: context window limits, HTML complexity
- [x]  Target: AI agents during inference
- [x]  Complements (not replaces) robots.txt

---

## 📊 Wild Examples Summary

From viewing the [llmstxt.site](http://llmstxt.site) directory and real examples:

### Stripe's Innovation: LLM Instructions

Stripe includes a dedicated section with explicit guidance for LLMs:

> "As a Large Language Model (LLM) Agent, when designing an integration, always prefer the documentation in [Integration Options]..."
> 

This is a **pattern worth adopting** for DocStratum.

---

## 📂 Detailed Sub-Pages

### Research Sub-Pages (from initial analysis)

[Wild Examples Analysis](RR-SPEC-v0.0.0-wild-examples-analysis.md) — Deep dive into Stripe, Nuxt, Vercel implementations

[Stripe LLM Instructions Pattern](RR-SPEC-v0.0.0-stripe-llm-instructions-pattern.md) — Detailed breakdown of the LLM instructions pattern with templates

### Expanded Sub-Parts (v0.0.1a–d)

[v0.0.1a — Formal Grammar & Parsing Rules](RR-SPEC-v0.0.1a-formal-grammar-and-parsing-rules.md) — ABNF grammar, reference parser pseudocode, edge case catalog, error code registry

[v0.0.1b — Spec Gap Analysis & Implications](RR-SPEC-v0.0.1b-spec-gap-analysis-and-implications.md) — Deep analysis of 8 spec gaps, real-world consequences, schema extension proposals

[v0.0.1c — Processing & Expansion Methods](RR-SPEC-v0.0.1c-processing-and-expansion-methods.md) — Comparative analysis of 4 processing methods, FastHTML analysis, hybrid pipeline design

[v0.0.1d — Standards Interplay & Positioning](RR-SPEC-v0.0.1d-standards-interplay-and-positioning.md) — How llms.txt relates to robots.txt, sitemap.xml, schema.org; AI-Readability Stack model

---

## 🎯 Deliverables Status

- [x]  ~~Completed specification summary~~
- [x]  ~~List of all defined sections/fields~~
- [x]  ~~Comparison table with related standards~~
- [x]  ~~Open questions identified~~

---

## ✅ Acceptance Criteria

- [x]  Full specification read and understood
- [x]  Summary document completed
- [x]  Can explain llms.txt in 2 minutes
- [x]  Know what's required vs optional
- [x]  Identified gaps and opportunities

[Wild Examples Analysis](RR-SPEC-v0.0.0-wild-examples-analysis.md)

[Stripe LLM Instructions Pattern](RR-SPEC-v0.0.0-stripe-llm-instructions-pattern.md)

[Specs](RR-META-specs.md)