# v0.0.6 — The Platinum Standard: What DocStratum Validates Against

> **Phase:** Research & Discovery (v0.0.x) — Late Addition
> **Status:** DRAFT
> **Date Created:** 2026-02-07
> **Author:** Ryan + Claude Opus 4.6
> **Purpose:** Define the complete, authoritative standard that DocStratum validates against, with explicit provenance for every criterion, answering the foundational question: "What exactly are we measuring, and how did we arrive at each measurement?"

---

## 1. Why This Document Exists

During the v0.1.x Foundation phase, a critical question surfaced that had been implicitly answered across 27 research documents but never explicitly stated in one place:

> "What standards are we validating against, and how did we arrive upon them specifically?"

This is not an academic exercise. DocStratum is a **validator**. A validator without a clearly defined standard is a ruler without markings — it can tell you *something* is there, but not whether it measures up. The existing ecosystem of 7+ llms.txt validators all check against the bare-minimum specification (roughly 8–10 guidelines), which is inadequate for distinguishing between a file that technically passes and one that actually serves its intended purpose.

This document fills that gap. It defines the **Platinum Standard** — DocStratum's complete validation framework — as a layered model where each criterion has:

- A clear **definition** (what are we checking?)
- Explicit **provenance** (where did this criterion come from?)
- A **validation level** mapping (L0–L4)
- A **measurability assessment** (can we check this programmatically?)
- A **diagnostic code** mapping (which of our 26 codes covers it?)

---

## 2. The Problem with the Original Specification

### 2.1 What the Spec Actually Says

The llms.txt specification was proposed by Jeremy Howard (Answer.AI) in September 2024. It defines a Markdown-formatted file at `/llms.txt` intended to help LLMs use a website at inference time. The specification is intentionally minimal.

When rigorously enumerated, the spec defines approximately **10 guidelines** across two categories:

**Structural requirements (5–6):**

| # | Guideline | Measurability |
|---|-----------|---------------|
| S1 | File located at `/llms.txt` root path | Fully measurable (HTTP request) |
| S2 | H1 heading with project/product name | Fully measurable (Markdown parse) |
| S3 | Blockquote summary after H1 | Fully measurable (Markdown parse) |
| S4 | Optional body content in Markdown | Partially measurable (presence check) |
| S5 | H2 sections containing link lists in `[name](url): description` format | Fully measurable (Markdown parse + regex) |
| S6 | `## Optional` as reserved section name for skippable content | Fully measurable (string match) |

**Content guidelines (4):**

| # | Guideline | Measurability |
|---|-----------|---------------|
| C1 | Factual accuracy — all statements verifiable from public sources | **Not measurable programmatically** |
| C2 | No marketing hyperbole — avoid superlatives, buzzwords, unverifiable claims | Partially measurable (heuristic NLP) |
| C3 | No confidential information — no pricing, trade secrets, confidential data | **Not measurable programmatically** |
| C4 | Clear, concise language — avoid ambiguous terms or unexplained jargon | Partially measurable (readability metrics) |

### 2.2 Why This Is Inadequate

The specification's minimalism was deliberate — Jeremy Howard wanted low barriers to adoption. But this creates a critical gap for anyone trying to **validate quality**:

**Problem 1: Binary pass/fail is meaningless.** A file with an H1 heading, a one-word blockquote, and a single broken link "passes" the spec. A meticulously crafted file with 11 well-organized sections, code examples, concept definitions, and careful token budgeting also "passes" the spec. Yet these two files are worlds apart in utility. The spec cannot distinguish between them.

**Problem 2: The content guidelines are not machine-checkable.** "Factual accuracy" and "no confidential information" require human judgment (or at minimum, an LLM evaluator with access to ground truth). You cannot build a deterministic validator around them.

**Problem 3: The spec ignores the consumption side entirely.** It says nothing about how LLMs actually process these files, what token budgets matter, which structural patterns improve retrieval accuracy, or how section organization affects agent performance. This is like defining an HTML standard without considering how browsers render it.

**Problem 4: The spec predates its own ecosystem.** When the spec was written (September 2024), essentially zero tools consumed llms.txt files. By 2026, the primary validated use case is AI coding assistants via MCP (Cursor, Claude Desktop, Windsurf). The spec was designed for a consumption model (web crawling by major LLM providers) that has *not materialized*. The actual consumption model (MCP servers feeding context to coding agents) has different requirements that the spec never anticipated.

**Problem 5: The ecosystem has no quality gradient.** Existing validators (llmstxtchecker.net, llmstxtvalidator.dev, llms.unusual.ai, etc.) all check roughly the same 5–8 structural rules. None of them assess content quality, anti-patterns, token efficiency, or LLM consumption readiness. The market is full of rulers with the same single marking.

### 2.3 The Competitor Landscape (as of February 2026)

| Validator | What It Checks | What It Misses |
|-----------|---------------|----------------|
| llmstxtchecker.net | H1, blockquote, link format | Content quality, anti-patterns, token budget, section naming |
| llmstxtvalidator.dev | H1, blockquote, link integrity, structure | Anti-patterns, token budget, code examples, LLM readiness |
| llms.unusual.ai | Structural lints, pass/fail with fixes | Quality scoring, content depth, semantic analysis |
| llmstxtvalidator.org | H1, formatting, basic compliance | Everything beyond basic structural compliance |
| rankability.com | Generation + basic validation | Not a validator — primarily a generator |
| rankray.com | Critical component checklist | Depth beyond checklist |
| **DocStratum (target)** | **L0–L4 pipeline, 26 diagnostic codes, 100-point quality score, 22 anti-patterns, 11 canonical sections, 3 token budget tiers** | **This document defines what "complete" means** |

---

## 3. The Platinum Standard: A Layered Model

### 3.1 Design Philosophy

The Platinum Standard is built on four principles:

1. **Layered progression, not binary compliance.** A file can be "good at Level 2" without meeting Level 4 criteria. Each level represents a meaningful quality threshold, not just a step toward an arbitrary finish line.

2. **Evidence-based criteria only.** Every criterion in the Platinum Standard traces to either the official specification, the v0.0.2 audit of 24 real-world implementations, the v0.0.4 best practices synthesis (57 checks), or empirical specimen analysis. No criterion exists because it "seems like a good idea."

3. **Programmatic measurability is required.** If a criterion cannot be checked by code (deterministic parser, regex, token counter, heuristic NLP), it is flagged as requiring human or LLM-assisted evaluation and is excluded from automated scoring. This keeps the validator honest.

4. **Consumer-centric, not author-centric.** The standard is designed around what makes an llms.txt file *useful to an LLM agent*, not what's easy for a human author to produce. This is a critical distinction: the spec was written from the author's perspective ("here's what you should put in the file"); the Platinum Standard is written from the consumer's perspective ("here's what makes the file actually work").

### 3.2 The Five Levels

Each level maps directly to the existing `ValidationLevel` enum in `src/docstratum/schema/validation.py`:

```
┌──────────────────────────────────────────────────────────────────────┐
│ L4 — EXEMPLARY (Platinum Standard)                                   │
│   "This file is optimized for LLM consumption"                       │
│   Concept definitions, few-shot examples, LLM instructions,         │
│   token-optimized structure                                          │
├──────────────────────────────────────────────────────────────────────┤
│ L3 — BEST PRACTICES                                                  │
│   "This file follows community best practices"                       │
│   Canonical section names, Master Index, code examples,              │
│   token budgets respected                                            │
├──────────────────────────────────────────────────────────────────────┤
│ L2 — CONTENT QUALITY                                                 │
│   "This file has meaningful content"                                 │
│   Non-empty descriptions, resolvable URLs, no placeholder text,     │
│   substantive sections                                               │
├──────────────────────────────────────────────────────────────────────┤
│ L1 — STRUCTURAL COMPLIANCE                                          │
│   "This file follows the spec's structure"                           │
│   H1 exists, sections use H2, links are well-formed Markdown        │
├──────────────────────────────────────────────────────────────────────┤
│ L0 — PARSEABLE                                                       │
│   "This file can be read"                                            │
│   Valid UTF-8, valid Markdown, non-empty, under size limit           │
└──────────────────────────────────────────────────────────────────────┘
```

**Key property:** Each level fully contains the levels below it. A file at L3 necessarily passes L0, L1, and L2. A file that fails L1 cannot be evaluated at L2+.

---

## 4. Complete Criterion Registry

### 4.1 Level 0 — Parseable

**Question this level answers:** "Can a machine read this file at all?"

**Provenance:** These criteria derive from basic file-handling requirements that any text-processing tool would need. They are pre-specification — the spec assumes them without stating them.

| ID | Criterion | Description | Measurability | Diagnostic Code | Provenance |
|----|-----------|-------------|---------------|-----------------|------------|
| L0-01 | Valid UTF-8 encoding | File must be valid UTF-8 without BOM issues or encoding errors | Fully measurable (byte-level check) | E003 | Implicit in spec ("Markdown file") |
| L0-02 | Non-empty content | File must contain at least one non-whitespace character | Fully measurable (length check) | E007 | Logical prerequisite; anti-pattern AP-CRIT-001 (Ghost File) from v0.0.4c |
| L0-03 | Valid Markdown syntax | File must parse as valid CommonMark without fatal syntax errors | Fully measurable (mistletoe parser) | E005 | v0.0.1a formal grammar analysis |
| L0-04 | Under maximum token limit | File must not exceed 100,000 tokens | Fully measurable (tokenizer count) | E008 | v0.0.1b Gap #1 (max file size); v0.0.4c AP-STRAT-002 (Monolith Monster); empirical evidence: Turborepo's 116K-token file degrades retrieval |
| L0-05 | Line feed normalization | File should use LF (Unix-style) line endings, not CRLF or CR | Fully measurable (byte scan) | E004 | CommonMark spec requires consistent line endings; practical interop requirement |

**Level 0 exit criteria:** All 5 checks pass. If any E-code fires at this level, the file is not parseable and higher levels cannot be evaluated.

---

### 4.2 Level 1 — Structural Compliance

**Question this level answers:** "Does this file follow the llms.txt specification's structural requirements?"

**Provenance:** These criteria derive directly from the official specification and the formal ABNF grammar defined in v0.0.1a.

| ID | Criterion | Description | Measurability | Diagnostic Code | Provenance |
|----|-----------|-------------|---------------|-----------------|------------|
| L1-01 | H1 title present | File must begin with exactly one H1 (`#`) heading containing the project/product name | Fully measurable (AST node check) | E001 | Official spec: "The file should begin with an H1" (only required element) |
| L1-02 | Single H1 only | File must contain exactly one H1 heading, not multiple | Fully measurable (AST node count) | E002 | v0.0.1a ABNF grammar: `llms-txt = h1-title ...`; official spec implies single title; v0.0.2c audit: 100% of valid specimens use single H1 |
| L1-03 | Blockquote present | A blockquote (`>`) summary should appear after the H1 | Fully measurable (AST parse) | W001 | Official spec: "expected" section; v0.0.2c audit: 55% real-world compliance — low enough to warrant Warning, not Error |
| L1-04 | H2 section structure | Content sections must use H2 (`##`) headings | Fully measurable (heading level check) | — (structural prerequisite, no standalone code) | Official spec: "H2-delimited sections"; v0.0.1a grammar |
| L1-05 | Link format compliance | Links within sections must use Markdown format: `[title](url)` with optional `: description` | Fully measurable (regex + AST) | E006 (for broken/empty) | Official spec: link list format definition |
| L1-06 | No heading level violations | No H3+ headings used for primary sections (H3 only within section content) | Fully measurable (AST level check) | — (covered by structural scoring) | v0.0.1a grammar: sections are H2-delimited; v0.0.2c: 0% of valid implementations use H3 for sections |

**Level 1 exit criteria:** E001 and E002 must not fire. W001 is a warning (blockquote absence doesn't block progression). All links must parse as valid Markdown syntax (URLs need not resolve — that's L2).

---

### 4.3 Level 2 — Content Quality

**Question this level answers:** "Does this file contain meaningful, functional content?"

**Provenance:** These criteria derive from the v0.0.2 real-world audit (24 implementations), v0.0.4b content best practices (15 checks), and empirical specimen analysis.

| ID | Criterion | Description | Measurability | Diagnostic Code | Provenance |
|----|-----------|-------------|---------------|-----------------|------------|
| L2-01 | Non-empty descriptions | Links should have non-empty descriptions (the `: description` part) | Fully measurable (string length check) | W003 | v0.0.4b CHECK-CNT-003; v0.0.2c audit: files with descriptions score 23% higher |
| L2-02 | URL resolvability | URLs in links should return HTTP 200 (or acceptable redirect) when accessed | Measurable with caveats (HTTP HEAD request; rate limiting, auth-gated URLs may false-positive) | E006 | Official spec implicit (links should be usable); v0.0.4c AP-CRIT-004 (Link Void) |
| L2-03 | No placeholder content | File must not contain placeholder text ("TODO", "Lorem ipsum", "[INSERT HERE]", template markers) | Fully measurable (pattern matching) | — (covered by anti-pattern AP-CONT-002 Blank Canvas) | v0.0.4c anti-pattern catalog; v0.0.2b: 3 of 24 audited files contained placeholder content |
| L2-04 | Non-empty sections | H2 sections must contain at least one link or one paragraph of content | Fully measurable (child node count) | W011 | v0.0.4c AP-STRUCT-002 (Orphaned Sections); v0.0.2c audit data |
| L2-05 | No duplicate sections | Section names must be unique (no two H2 headings with identical text) | Fully measurable (set comparison) | — (covered by AP-STRUCT-003 Duplicate Identity) | v0.0.4c anti-pattern catalog |
| L2-06 | Substantive blockquote | If a blockquote exists, it should contain a meaningful description (>20 characters, not just the project name repeated) | Fully measurable (length + similarity check) | — (informational) | v0.0.2c audit: blockquotes under 20 chars correlate with lowest-quality files |
| L2-07 | No formulaic descriptions | Link descriptions should not all follow identical boilerplate patterns | Measurable (heuristic: pairwise similarity > 80% across 5+ descriptions) | W006 | v0.0.4c AP-CONT-007 (Formulaic Description); v0.0.2b: auto-generated files often produce identical patterns |

**Level 2 exit criteria:** No critical anti-patterns (AP-CRIT-*) detected. E006 does not fire for >50% of links. No placeholder content detected.

---

### 4.4 Level 3 — Best Practices

**Question this level answers:** "Does this file follow the community best practices that empirically correlate with quality?"

**Provenance:** These criteria derive entirely from DocStratum's original research — the v0.0.2 audit of 450+ projects, the v0.0.4 best practices synthesis, and the v0.0.4d design decision log. **None of these criteria appear in the official spec.** They represent the empirical knowledge layer that DocStratum adds.

| ID | Criterion | Description | Measurability | Diagnostic Code | Provenance |
|----|-----------|-------------|---------------|-----------------|------------|
| L3-01 | Canonical section names | Section names should match one of the 11 canonical names (or a recognized alias from the 32-alias mapping) | Fully measurable (string match against `CanonicalSectionName` + `SECTION_NAME_ALIASES`) | W002 | **DECISION-012**: 11 canonical names derived from frequency analysis of 450+ projects in v0.0.2c |
| L3-02 | Master Index present | File should contain a section functioning as a master index (typically the first H2 section, linking to key resources) | Fully measurable (section name match + link density check) | W009 | v0.0.4a CHECK-STR-009; v0.0.2d finding: Master Index presence correlates with 87% vs 31% LLM task success rate |
| L3-03 | Code examples present | At least one fenced code block (```) should appear somewhere in the file | Fully measurable (AST node type check) | W004 | v0.0.4b; v0.0.2c pattern analysis: code examples are the strongest single predictor of quality score (r ≈ 0.65) |
| L3-04 | Code blocks have language specifiers | Fenced code blocks should specify a language (```python, ```bash, etc.) | Fully measurable (regex on fence opening) | W005 | v0.0.4b; practical: language hints enable syntax-aware processing by LLM agents |
| L3-05 | Token budget respected | Total file size should fall within appropriate tier: Standard (1.5K–4.5K), Comprehensive (4.5K–12K), or Full (12K–50K) | Fully measurable (tokenizer count + tier classification) | W010 | **DECISION-013**: 3 token budget tiers from v0.0.4a; v0.0.1b Gap #1; empirical: files above 50K tokens show degraded retrieval performance |
| L3-06 | Canonical section ordering | Sections should follow the recommended order (Master Index → LLM Instructions → Getting Started → Core Concepts → API Reference → Examples → ...) | Fully measurable (ordinal comparison against `CANONICAL_SECTION_ORDER`) | W008 | v0.0.4a CHECK-STR-008; v0.0.2c: consistent ordering correlates with higher structural scores |
| L3-07 | Version metadata present | File should contain version information (in blockquote, in a dedicated section, or via a link to a changelog) | Measurable (pattern matching for version strings, "v1.2.3", "version:", date stamps) | W007 | v0.0.1b Gap #2 (metadata); v0.0.4c AP-CONT-009 (Versionless Drift); practical: agents need to know if content is current |
| L3-08 | Optional section used appropriately | If present, `## Optional` section should contain genuinely supplementary content, not core documentation | Partially measurable (section name match; content criticality is subjective) | — (informational) | Official spec: `## Optional` is reserved; v0.0.4a usage guidelines |
| L3-09 | No critical anti-patterns | File must not exhibit any of the 4 critical anti-patterns (Ghost File, Structure Chaos, Encoding Disaster, Link Void) | Fully measurable (composite check) | — (covered by AP-CRIT-001 through AP-CRIT-004) | v0.0.4c anti-pattern catalog with severity classification |
| L3-10 | No structural anti-patterns | File should not exhibit structural anti-patterns (Sitemap Dump, Orphaned Sections, Duplicate Identity, Section Shuffle, Naming Nebula) | Fully measurable (composite heuristic checks) | — (covered by AP-STRUCT-001 through AP-STRUCT-005) | v0.0.4c anti-pattern catalog |

**Level 3 exit criteria:** ≥70% of sections use canonical names (or aliases). At least one code example present. Token count within one of the three budget tiers. No critical anti-patterns. Quality score ≥ 70 (STRONG grade).

---

### 4.5 Level 4 — Exemplary (The Platinum Standard)

**Question this level answers:** "Is this file optimized for LLM consumption — does it actively help an AI agent succeed?"

**Provenance:** These criteria represent DocStratum's most forward-looking research. They derive from the v0.0.0 Stripe LLM Instructions Pattern analysis, the v0.0.4d design decisions on semantic enrichment, and the core thesis that *structure is a feature*. **These criteria go significantly beyond anything the community currently validates.**

| ID | Criterion | Description | Measurability | Diagnostic Code | Provenance |
|----|-----------|-------------|---------------|-----------------|------------|
| L4-01 | LLM Instructions section | File should contain an explicit section addressing AI agents directly — telling them how to use the documentation, what to prioritize, and what to avoid | Fully measurable (section name match for "LLM Instructions" or alias) | I001 | v0.0.0 Stripe LLM Instructions Pattern; v0.0.4d DECISION-002 (3-Layer Architecture); Stripe's implementation demonstrated measurable improvement in agent task completion |
| L4-02 | Concept definitions | File should define key concepts, terms, and domain-specific vocabulary that an LLM would need to understand the project | Measurable (presence check for definition patterns: "X is...", "X refers to...", glossary sections) | I002 | v0.0.1b Gap #7; v0.0.4d DECISION-002 Layer 2 (Concept Map); v0.0.4c AP-CONT-003 (Jargon Jungle) |
| L4-03 | Few-shot examples | File should contain at least one example that demonstrates typical usage in a way an LLM could learn from (question/answer pair, input/output example, before/after comparison) | Measurable (heuristic: paired code blocks, Q&A patterns, "Example:" headers) | I003 | v0.0.4d DECISION-002 Layer 3 (Few-Shot Bank); research on in-context learning suggests 1–3 examples dramatically improve LLM task performance |
| L4-04 | No content anti-patterns | File should be free of all 9 content anti-patterns (Copy-Paste Plague, Blank Canvas, Jargon Jungle, Link Desert, Outdated Oracle, Example Void, Formulaic Description, Silent Agent, Versionless Drift) | Fully measurable (composite detection) | — (covered by AP-CONT-001 through AP-CONT-009) | v0.0.4c anti-pattern catalog |
| L4-05 | No strategic anti-patterns | File should avoid the 4 strategic anti-patterns (Automation Obsession, Monolith Monster, Meta-Documentation Spiral, Preference Trap) | Partially measurable (token count for Monolith; others require judgment) | — (covered by AP-STRAT-001 through AP-STRAT-004) | v0.0.4c anti-pattern catalog |
| L4-06 | Token-optimized structure | File should allocate tokens efficiently: high-value sections (Getting Started, Core Concepts, API Reference) should contain more content than low-value sections; no section should consume >40% of total tokens | Fully measurable (per-section token count + ratio calculation) | — (L4 enrichment metric) | v0.0.4a token allocation guidelines; v0.0.2c: top-scoring files show balanced token distribution across sections |
| L4-07 | Relative URL minimization | File should prefer absolute URLs over relative URLs, since consuming agents may not have base URL context | Fully measurable (URL scheme check) | I004 | Practical: MCP-based consumption often strips base URL context; relative URLs break when file is consumed outside web context |
| L4-08 | Jargon is defined or linked | Domain-specific terms that appear in the file should either be defined inline, linked to a glossary, or appear in a Concept Definitions section | Partially measurable (heuristic: flag terms that appear only once and have no definition pattern nearby) | I007 | v0.0.4c AP-CONT-003 (Jargon Jungle); v0.0.1b Gap #7 |

**Level 4 exit criteria:** LLM Instructions section present. At least 3 concept definitions. At least 1 few-shot example. Zero anti-patterns across all 4 categories. Quality score ≥ 90 (EXEMPLARY grade).

---

## 5. Provenance Summary

This section provides a bird's-eye view of where each criterion comes from, so that the question "how did we arrive at this?" has a single-lookup answer.

### 5.1 By Source

| Source | Criteria Count | Coverage |
|--------|---------------|----------|
| **Official llms.txt specification** (Jeremy Howard, Sept 2024) | 8 criteria | L0-01 (implicit), L1-01, L1-02, L1-03, L1-04, L1-05, L2-02 (implicit), L3-08 |
| **v0.0.1a Formal ABNF Grammar** | 4 criteria | L0-03, L1-02, L1-04, L1-06 |
| **v0.0.1b Spec Gap Analysis** (8 gaps) | 6 criteria | L0-04, L3-05, L3-07, L4-02, L4-07, L4-08 |
| **v0.0.2 Real-World Audit** (24 implementations, 11 specimens) | 9 criteria | L1-03, L2-01, L2-03, L2-06, L2-07, L3-01, L3-02, L3-06, L4-06 |
| **v0.0.4 Best Practices Synthesis** (57 checks) | 12 criteria | L2-04, L2-05, L3-01–L3-10, L4-01–L4-08 |
| **v0.0.4c Anti-Pattern Catalog** (22 patterns) | 7 criteria | L0-02, L2-03, L2-05, L3-09, L3-10, L4-04, L4-05 |
| **v0.0.4d Design Decisions** (16 decisions) | 5 criteria | L3-01, L3-05, L4-01, L4-02, L4-03 |
| **v0.0.0 Stripe Pattern Analysis** | 1 criterion | L4-01 |
| **Practical/engineering requirements** | 3 criteria | L0-01, L0-05, L4-07 |

### 5.2 By Measurability

| Measurability | Count | Percentage |
|---------------|-------|------------|
| Fully measurable (deterministic code check) | 22 | 73% |
| Measurable with heuristics (pattern matching, NLP) | 6 | 20% |
| Partially measurable (requires judgment for edge cases) | 2 | 7% |
| Not programmatically measurable | 0 | 0% |

**Note:** The Platinum Standard deliberately excludes the original spec's unmeasurable content guidelines (C1: factual accuracy, C3: no confidential information). These are real concerns, but they cannot be validated by a deterministic tool. They belong in a separate "human review checklist," not in an automated validator.

---

## 6. Mapping to Existing DocStratum Infrastructure

### 6.1 Diagnostic Code Coverage

The existing 26 diagnostic codes (8 Errors, 11 Warnings, 7 Informational) cover the Platinum Standard as follows:

| Platinum Standard Level | Diagnostic Codes Used | Coverage |
|------------------------|----------------------|----------|
| L0 — Parseable | E003, E004, E005, E007, E008 | 5 of 5 criteria covered |
| L1 — Structural | E001, E002, W001, E006 | 4 of 6 criteria have codes; 2 are structural prerequisites without standalone codes |
| L2 — Content Quality | W003, W006, W011, E006 | 4 of 7 criteria have codes; 3 are covered by anti-pattern detection |
| L3 — Best Practices | W002, W004, W005, W007, W008, W009, W010 | 7 of 10 criteria have codes; 3 are composite anti-pattern checks |
| L4 — Exemplary | I001, I002, I003, I004, I007 | 5 of 8 criteria have codes; 3 are composite/enrichment metrics |

**Conclusion:** The existing diagnostic infrastructure covers the Platinum Standard well. No new diagnostic codes are needed for the initial implementation. The 5 criteria without standalone codes are handled by anti-pattern detection or composite scoring.

### 6.2 Quality Score Dimension Mapping

| Quality Dimension | Weight | Platinum Criteria Covered |
|-------------------|--------|--------------------------|
| **Structural** (30 pts) | 30% | L0-01 through L1-06, L3-06, L3-09, L3-10 |
| **Content** (50 pts) | 50% | L2-01 through L2-07, L3-01 through L3-08, L4-01 through L4-08 |
| **Anti-Pattern** (20 pts) | 20% | Deductions for violations of L2-03, L2-05, L3-09, L3-10, L4-04, L4-05 |

### 6.3 Anti-Pattern Registry Coverage

All 22 anti-patterns from the existing `AntiPatternRegistry` map to specific Platinum Standard criteria:

| Anti-Pattern Category | Count | Platinum Standard Level |
|-----------------------|-------|------------------------|
| Critical (AP-CRIT-*) | 4 | L0 (Ghost File, Encoding Disaster) and L2 (Structure Chaos, Link Void) |
| Structural (AP-STRUCT-*) | 5 | L2 and L3 |
| Content (AP-CONT-*) | 9 | L2, L3, and L4 |
| Strategic (AP-STRAT-*) | 4 | L4 |

---

## 7. What This Means for Implementation

### 7.1 The Validator's Contract

With the Platinum Standard defined, the DocStratum validator now has a clear contract:

> **Given** an llms.txt file as input,
> **When** the validator processes it through the L0–L4 pipeline,
> **Then** it returns:
> 1. The highest validation level achieved (L0–L4)
> 2. A list of diagnostic findings (26 possible codes, each with severity, message, and remediation)
> 3. A 100-point quality score with dimensional breakdown
> 4. A quality grade (EXEMPLARY / STRONG / ADEQUATE / NEEDS_WORK / CRITICAL)
> 5. A list of detected anti-patterns (from 22 possible)

This is no longer "validating against the spec." It's validating against a **comprehensive, evidence-based quality standard** that subsumes the spec (at L1) and extends far beyond it (at L3–L4).

### 7.2 How This Answers the Original Question

**Q: "What standards are we validating against?"**

**A:** The Platinum Standard, a 5-level quality framework comprising 30 measurable criteria organized into progressive tiers:
- L0 (5 criteria): Can a machine read this file?
- L1 (6 criteria): Does it follow the spec's structure?
- L2 (7 criteria): Does it contain meaningful content?
- L3 (10 criteria): Does it follow empirically-validated best practices?
- L4 (8 criteria): Is it optimized for LLM consumption?

**Q: "How did we arrive upon them specifically?"**

**A:** Through a research program comprising:
- Formal grammar analysis of the official spec (v0.0.1a)
- Gap analysis of 8 specification omissions (v0.0.1b)
- Real-world audit of 24 implementations and 11 empirical specimens (v0.0.2)
- Ecosystem survey of 75+ tools and 30 key players (v0.0.3)
- Best practices synthesis yielding 57 automated checks and 22 anti-patterns (v0.0.4)
- Requirements definition with 68 functional requirements (v0.0.5)
- Calibration against gold-standard files (Svelte: 92, Pydantic: 90, NVIDIA: 24)

Every criterion in the Platinum Standard traces back to one or more of these evidence sources. Nothing is included "because it seemed like a good idea."

### 7.3 What the Platinum Standard Is NOT

To prevent scope creep and maintain intellectual honesty:

1. **It is not an official extension of the llms.txt specification.** DocStratum does not claim to modify or replace the official spec. The Platinum Standard is DocStratum's internal quality framework that *includes* spec compliance as one of its layers (L1).

2. **It is not a guarantee of LLM performance.** A file scoring 100/100 on the Platinum Standard is structurally excellent, but we cannot guarantee that any specific LLM will process it better than a file scoring 50. The criteria are based on the best available evidence, not on controlled experiments with proprietary LLM architectures.

3. **It is not static.** As the llms.txt ecosystem evolves, the Platinum Standard should evolve with it. If major LLM providers begin consuming llms.txt files and publish consumption requirements, those requirements should be incorporated. The provenance tracking in Section 5 exists precisely to make updates traceable.

4. **It is not prescriptive about content topics.** The standard says nothing about *what* a project should document — only about *how* documentation should be structured and presented for LLM consumption. A well-structured file about a terrible product still scores high.

---

## 8. Open Questions

The following questions remain unresolved and may inform future revisions:

1. **Should L2 URL resolvability be synchronous or deferred?** HTTP HEAD checks are slow and rate-limited. Should the validator offer both a "fast mode" (skip URL checks) and a "thorough mode" (check all URLs)?

2. **How should multi-file strategies (llms.txt + llms-full.txt) be scored?** The current standard treats each file independently. Should there be cross-file criteria (e.g., "llms-full.txt must contain everything linked from llms.txt")?

3. **Should there be a "Type 2 Full" variant of the Platinum Standard?** The current criteria are optimized for Type 1 Index files (the dominant format). Type 2 Full files (inline documentation dumps) may need different criteria.

4. **What is the right threshold for heuristic checks?** Criteria like L2-07 (formulaic descriptions, >80% pairwise similarity) use arbitrary thresholds. These should be calibrated against the 11 empirical specimens.

5. **Should LLM-assisted evaluation be a separate layer?** Some criteria that were excluded (factual accuracy, confidential information detection) could be checked by an LLM evaluator. Should this be an optional "L5" or a separate evaluation track?

---

## 9. Revision History

| Date | Version | Change |
|------|---------|--------|
| 2026-02-07 | v0.0.6-draft | Initial draft — defines the Platinum Standard with 30 criteria across 5 levels |

---

## 10. Cross-References

| Document | Relevance |
|----------|-----------|
| `v0.0.1a` — Formal Grammar & Parsing Rules | Source for L0 and L1 structural criteria |
| `v0.0.1b` — Spec Gap Analysis & Implications | Source for gap-filling criteria (L3, L4) |
| `v0.0.2c` — Pattern Analysis & Statistics | Empirical evidence for best practice criteria |
| `v0.0.2d` — Synthesis & Recommendations | Gold standard calibration data |
| `v0.0.4a` — Structural Best Practices | Source for L3 structural criteria |
| `v0.0.4b` — Content Best Practices | Source for L2 and L3 content criteria |
| `v0.0.4c` — Anti-Patterns Catalog | Source for anti-pattern criteria across all levels |
| `v0.0.4d` — Differentiators & Decision Log | Source for L4 enrichment criteria and design decisions |
| `v0.0.5d` — Success Criteria & MVP Definition | Validation that Platinum Standard aligns with MVP scope |
| `v0.0.x` — Consolidated Research Synthesis | Master reference for all research findings |
| `src/docstratum/schema/validation.py` | Implementation of ValidationLevel (L0–L4) |
| `src/docstratum/schema/diagnostics.py` | Implementation of 26 diagnostic codes |
| `src/docstratum/schema/constants.py` | Implementation of canonical names, token budgets, anti-patterns |
| `src/docstratum/schema/quality.py` | Implementation of 100-point quality scoring |
