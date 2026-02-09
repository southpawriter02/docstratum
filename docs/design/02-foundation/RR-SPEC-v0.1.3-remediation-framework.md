# v0.1.3 — Remediation Framework

> **Status:** DRAFT
> **Created:** 2026-02-09
> **Last Updated:** 2026-02-09
> **Governed By:** RR-META-documentation-backlog.md (Deliverable 2)
> **Depends On:** RR-SPEC-v0.1.3-output-tier-specification.md (Deliverable 1)
> **Feeds Into:** Deliverable 5 (Report Generation Stage)
> **ASoT Version:** 1.0.0
> **Traces To:** FR-004 (error reporting), Output Tier Spec §2.3 (Tier 3 data contract)

---

## 1. Purpose

This specification defines how the DocStratum validation engine transforms raw diagnostic output into **actionable, prioritized remediation guidance**. It is the engine behind Tier 3 (Remediation Playbook) of the output tier system defined in RR-SPEC-v0.1.3-output-tier-specification.md.

Every `DiagnosticCode` in `diagnostics.py` already carries a `remediation` field — a terse, one-line hint like "Add a single '# Title' as the first line of the file." Every anti-pattern in `ANTI_PATTERN_REGISTRY` has a `description` that implicitly suggests corrective action. The raw material for remediation guidance exists across the 38 diagnostic codes and 28 anti-patterns. What's missing is the **aggregation, prioritization, and sequencing logic** that transforms these individual hints into a coherent action plan.

This specification provides that logic. It defines five components:

1. **Priority Model** — How individual diagnostics are ranked by impact, not just severity
2. **Grouping Strategy** — How related diagnostics are consolidated into logical action items
3. **Remediation Templates** — Expanded prose guidance beyond the terse `remediation` hint
4. **Dependency Graph** — Which fixes are prerequisite to others
5. **Tier 3 / Tier 4 Boundary** — Where automated remediation ends and contextual intelligence begins

### 1.1 Relationship to Existing Artifacts

| Artifact | This Spec's Relationship |
|----------|-------------------------|
| `diagnostics.py` DiagnosticCode.remediation | Source material. Each code's one-line hint is the seed for remediation templates. This spec expands those seeds into full guidance. |
| `ANTI_PATTERN_REGISTRY` in constants.py | Source material. Anti-pattern descriptions inform the "why this matters" section of remediation templates. |
| Output Tier Spec §2.3 | Data contract. Defines the fields this framework must produce (`action_items`, `priority`, `effort_estimate`, `score_impact`, etc.). |
| Rule Registry (Deliverable 3, future) | Consumer. The Rule Registry will cross-reference diagnostic codes to the remediation framework for template lookup. |
| Report Generation Stage (Deliverable 5, future) | Consumer. Stage 6's Tier 3 renderer calls this framework to transform diagnostics into action items. |

---

## 2. Priority Model

### 2.1 Why Severity Alone Is Insufficient

The existing `Severity` enum (ERROR, WARNING, INFO) provides a coarse ordering: errors before warnings before info. But within a severity level, there's a wide range of actual impact. Consider two WARNING-severity diagnostics:

- **W009 (No Master Index):** Files with Master Index achieve 87% vs. 31% LLM success rate (per v0.0.4a research). This is arguably the single highest-impact documentation change a project can make.
- **W005 (Code Block No Language):** A code block without a language specifier. Helpful for syntax highlighting, but no measurable impact on LLM comprehension.

Both are WARNING severity. A priority model that treats them equally fails the consumer. The remediation framework must rank diagnostics by *impact on LLM consumption quality*, not just by severity.

### 2.2 Priority Levels

The framework defines four priority levels that overlay (but do not replace) the existing three severity levels:

| Priority | Definition | Typical Severity | Action Expectation |
|----------|-----------|-----------------|-------------------|
| `CRITICAL` | Blocks LLM consumption entirely. The documentation is unusable in its current state. | ERROR | Must fix immediately. No other fixes matter until these are resolved. |
| `HIGH` | Significantly degrades LLM comprehension or navigation. Measurable impact on success rates. | ERROR or WARNING | Fix within the current work cycle. These are the changes that move the quality score the most. |
| `MEDIUM` | Reduces quality but doesn't prevent consumption. Best-practice violations that accumulate. | WARNING | Fix when convenient. Batch these into a "quality pass" sprint. |
| `LOW` | Suggestions for excellence. The documentation works without these, but they push it from Strong to Exemplary. | WARNING or INFO | Address during polish phase or when the team has spare bandwidth. |

### 2.3 Priority Assignment Rules

Each diagnostic code is assigned a **default priority** based on its impact characteristics. The priority is static per code — it doesn't change based on how many times the diagnostic appears.

#### Factor 1: LLM Consumption Impact

Does fixing this diagnostic measurably improve how AI agents understand and navigate the documentation?

| Impact Level | Criteria | Priority Contribution |
|-------------|----------|----------------------|
| Blocking | Diagnostic prevents parsing, navigation, or basic comprehension | → CRITICAL |
| High | Research evidence links this to success rate changes (r > 0.3) | → HIGH |
| Moderate | Improves quality but no direct research evidence for success rate | → MEDIUM |
| Marginal | Nice-to-have, no measurable consumption impact | → LOW |

#### Factor 2: Gating Effect

Does this diagnostic gate other checks? If the file can't pass L0, none of the L1–L4 checks produce meaningful results.

| Gating Level | Criteria | Priority Contribution |
|-------------|----------|----------------------|
| Pipeline-gating | Failure prevents subsequent pipeline stages from running | → CRITICAL |
| Level-gating | Failure prevents the next validation level from being attempted | → promotes by +1 level |
| Non-gating | Failure is isolated to this specific check | → no adjustment |

#### Factor 3: Score Weight

How much does this diagnostic contribute to the quality score? Diagnostics in the Content dimension (50 points, 50% weight) have more score impact than diagnostics in the Anti-Pattern dimension (20 points, 20% weight).

This factor adjusts priority within a level but does not change the level itself.

#### Factor 4: Prevalence-Adjusted Effort

If a diagnostic appears many times in a single file (e.g., W003 on 30 different links), the remediation effort scales linearly but the priority should reflect the *aggregate* impact, not just one instance.

When a diagnostic code appears N times in a single file:
- The action item is presented once (not N times)
- The `affected_count` field indicates how many instances exist
- The effort estimate may be promoted (e.g., from QUICK_WIN to MODERATE) if N > threshold

### 2.4 Default Priority Assignments

The following table assigns a default priority to every diagnostic code. These defaults are static and embedded in the remediation framework. Profiles (Deliverable 4) may override these for specific use cases.

#### Errors (E001–E010)

| Code | Name | Default Priority | Rationale |
|------|------|:---:|-----------|
| E001 | No H1 Title | CRITICAL | Pipeline-gating: file cannot be identified without H1. All downstream checks depend on this. |
| E002 | Multiple H1 | CRITICAL | Parser ambiguity: which title is correct? Breaks document identity resolution. |
| E003 | Invalid Encoding | CRITICAL | Pipeline-gating: non-UTF-8 files may fail to parse at all. |
| E004 | Invalid Line Endings | HIGH | Parser compatibility: some parsers break on CR/CRLF, but most modern parsers handle it. Not pipeline-gating but widespread breakage risk. |
| E005 | Invalid Markdown | CRITICAL | Pipeline-gating: unparseable Markdown prevents all structural analysis. |
| E006 | Broken Links | HIGH | Navigation failure: links are the primary mechanism for AI agent traversal. Broken links strand the agent. |
| E007 | Empty File | CRITICAL | Pipeline-gating: Ghost File anti-pattern. No content to validate. |
| E008 | Exceeds Size Limit | HIGH | Not pipeline-gating (file still parses) but triggers Monolith Monster anti-pattern. Requires structural rework. |
| E009 | No Index File | CRITICAL | Ecosystem-gating: without llms.txt, the ecosystem has no entry point. |
| E010 | Orphaned Ecosystem File | HIGH | Content exists but is invisible to AI agents navigating via the index. Not pipeline-gating but represents wasted effort. |

#### Warnings (W001–W018)

| Code | Name | Default Priority | Rationale |
|------|------|:---:|-----------|
| W001 | Missing Blockquote | MEDIUM | 55% real-world compliance. Helpful context but not navigation-critical. Quick to add. |
| W002 | Non-Canonical Section Name | MEDIUM | Affects navigation consistency. AI agents may not recognize non-standard names. |
| W003 | Link Missing Description | HIGH | Descriptions are how AI agents decide which link to follow. Bare URLs force guessing. Research shows strong correlation with navigation success. |
| W004 | No Code Examples | HIGH | Strongest quality predictor (r ≈ 0.65 per v0.0.2c). Directly affects whether AI agents can generate working code. |
| W005 | Code No Language | LOW | Affects syntax highlighting and language-specific parsing, but AI agents can usually infer language from context. |
| W006 | Formulaic Descriptions | MEDIUM | Reduces AI agent's ability to distinguish between sections. Common in auto-generated files. |
| W007 | Missing Version Metadata | MEDIUM | AI agents can't assess freshness without version info. Important for accuracy but not for navigation. |
| W008 | Section Order Non-Canonical | LOW | Non-canonical ordering is confusing to humans but AI agents navigate by section name, not position. |
| W009 | No Master Index | HIGH | 87% vs. 31% LLM success rate (per v0.0.4a). Single highest-impact structural addition for navigation. |
| W010 | Token Budget Exceeded | MEDIUM | Degraded performance in smaller context windows. Important for broad compatibility but doesn't break consumption. |
| W011 | Empty Sections | MEDIUM | Placeholder sections waste tokens and confuse AI agents expecting content. |
| W012 | Broken Cross-File Link | HIGH | Ecosystem-level navigation failure. AI agent follows a link and hits a dead end. |
| W013 | Missing Aggregate | MEDIUM | Large projects benefit from llms-full.txt but can function without it. |
| W014 | Aggregate Incomplete | MEDIUM | Partial aggregate is better than none, but may mislead large-window models. |
| W015 | Inconsistent Project Name | MEDIUM | Confuses AI agents about project identity. Easy to fix but often overlooked. |
| W016 | Inconsistent Versioning | MEDIUM | Version drift indicates stale documentation. Affects freshness scoring. |
| W017 | Redundant Content | LOW | Token waste, but doesn't prevent consumption. Usually a symptom of poor planning. |
| W018 | Unbalanced Token Distribution | LOW | Architectural concern. Important for ecosystem health but doesn't block individual file consumption. |

#### Informational (I001–I010)

| Code | Name | Default Priority | Rationale |
|------|------|:---:|-----------|
| I001 | No LLM Instructions | HIGH | 0% current adoption (per v0.0.2) but the strongest quality differentiator. The single most impactful DocStratum-specific enhancement. Elevated from INFO severity to HIGH priority because of evidence-grounded impact. |
| I002 | No Concept Definitions | MEDIUM | Improves disambiguation and reduces hallucination. Part of the DocStratum three-layer architecture. |
| I003 | No Few-Shot Examples | MEDIUM | Improves response quality for ambiguous queries. Part of the DocStratum three-layer architecture. |
| I004 | Relative URLs Detected | LOW | May need resolution in some consumption contexts but not inherently broken. |
| I005 | Type 2 Full Detected | LOW | Informational classification. Not actionable unless the consumer wants to restructure. |
| I006 | Optional Sections Unmarked | LOW | Token optimization hint. Helpful but not impactful for most consumers. |
| I007 | Jargon Without Definition | MEDIUM | Domain-specific jargon causes hallucination when AI agents guess meanings. Important for accuracy. |
| I008 | No Instruction File | MEDIUM | Ecosystem-level version of I001. Instruction files are the strongest differentiator. |
| I009 | Content Coverage Gap | MEDIUM | Identifies areas where AI agents lack detailed documentation. Guides content planning. |
| I010 | Ecosystem Single File | LOW | Informational observation. Valid but limited — not actionable unless the consumer wants to expand. |

### 2.5 Priority Override Mechanism

Profiles (Deliverable 4) can override default priorities for specific diagnostic codes. This enables use cases like:

- A `strict` profile that promotes all MEDIUM priorities to HIGH
- An `ecosystem-focus` profile that promotes W012–W018 and I008–I010 to HIGH
- A `minimal` profile that demotes all INFO-severity codes to LOW regardless of default priority

Overrides are applied at profile load time, before the remediation framework processes diagnostics. The override mechanism is defined in the Profiles spec (Deliverable 4); this framework consumes the overridden priority, not the raw severity.

---

## 3. Grouping Strategy

### 3.1 The Problem with Flat Lists

A validation run on a 5-file ecosystem might produce 40+ diagnostics. Presenting these as a flat, linear list is barely more useful than the raw diagnostic output. The consumer needs structure — a way to see the forest, not just the trees.

Grouping transforms a flat diagnostic list into a structured set of **action items**, where each action item represents a coherent unit of work that a human can understand and execute.

### 3.2 Grouping Modes

The framework supports four grouping modes. The profile (Deliverable 4) selects which mode is active; the default is `by-priority`.

#### Mode 1: `by-priority` (Default)

Groups action items into four sections: CRITICAL, HIGH, MEDIUM, LOW. Within each section, items are sorted by score impact (highest first).

This mode answers: "What should I fix first to get the biggest quality improvement?"

```
## CRITICAL (2 action items — must fix immediately)
  1. Fix H1 title in llms.txt (E001) — Score impact: +8.5
  2. Resolve encoding issue in docs/api.md (E003) — Score impact: +6.0

## HIGH (4 action items — fix in current work cycle)
  1. Add descriptions to 12 bare links (W003 ×12) — Score impact: +5.4
  2. Add Master Index section (W009) — Score impact: +4.5
  ...
```

#### Mode 2: `by-level`

Groups action items by validation level: L0, L1, L2, L3, L4. Within each level, items are sorted by priority.

This mode answers: "What do I need to fix to reach the next validation level?"

```
## L0 — Parseable (1 action item)
  1. Fix encoding in docs/api.md (E003)

## L1 — Structural (3 action items)
  1. Fix H1 title in llms.txt (E001)
  2. Add Master Index section (W009)
  ...
```

#### Mode 3: `by-file`

Groups action items by file path. Within each file, items are sorted by priority.

This mode answers: "What needs to change in each file?" — ideal for multi-file ecosystems where different team members own different files.

```
## llms.txt (5 action items)
  1. Fix H1 title (E001) — CRITICAL
  2. Add Master Index (W009) — HIGH
  ...

## docs/api.md (2 action items)
  1. Fix encoding (E003) — CRITICAL
  2. Add code examples (W004) — HIGH
```

#### Mode 4: `by-effort`

Groups action items by effort estimate: QUICK_WIN, MODERATE, STRUCTURAL. Within each group, items are sorted by score impact.

This mode answers: "What can I fix right now in 10 minutes?" — ideal for sprint planning or quick improvements.

```
## QUICK_WIN (6 action items — minutes each)
  1. Add blockquote to llms.txt (W001) — Score impact: +1.5
  2. Add language to 3 code blocks (W005 ×3) — Score impact: +0.9
  ...

## MODERATE (3 action items — hours each)
  1. Add descriptions to 12 bare links (W003 ×12) — Score impact: +5.4
  ...
```

### 3.3 Consolidation Rules

Before grouping, the framework consolidates raw diagnostics into action items using these rules:

**Rule 1: Same Code, Same File → Consolidate**
If the same `DiagnosticCode` appears multiple times in the same file (e.g., W003 on lines 14, 18, and 22), consolidate into a single action item with:
- `affected_count`: number of instances (e.g., 3)
- `line_numbers`: list of all affected lines (e.g., [14, 18, 22])
- `effort_estimate`: may be promoted based on `affected_count` (see §4.3)

**Rule 2: Same Code, Different Files → Separate**
If the same `DiagnosticCode` appears in different files (e.g., W003 in llms.txt and W003 in docs/api.md), these are separate action items. They may have different priorities if the files have different roles (index file vs. content page).

**Rule 3: Anti-Pattern → Aggregate**
If multiple diagnostics collectively indicate a named anti-pattern (e.g., W003 ×15 triggers the "Link Desert" anti-pattern AP_CONT_004), the anti-pattern is noted in the action item's `anti_pattern` field. The anti-pattern description from `ANTI_PATTERN_REGISTRY` is included for context.

**Rule 4: Ecosystem Diagnostics → Own Group**
Diagnostics from the ecosystem validation stage (E009–E010, W012–W018, I008–I010) that don't have a `source_file` (they're ecosystem-level observations) are grouped under a synthetic "Ecosystem Health" file group in `by-file` mode.

---

## 4. Effort Estimation

### 4.1 Effort Tiers

As defined in the Output Tier Specification §2.3, effort estimates use three coarse-grained tiers:

| Tier | Time Signal | Criteria |
|------|------------|----------|
| `QUICK_WIN` | Minutes | Single-line or single-field change. No structural reorganization. No new content creation beyond a sentence or two. |
| `MODERATE` | Hours | Multi-line changes within a single file. Localized impact. May involve writing new descriptions, adding code examples, or restructuring a section. |
| `STRUCTURAL` | Days | Architectural changes affecting multiple files or requiring substantial new content. File decomposition, ecosystem restructuring, creating new files from scratch. |

### 4.2 Default Effort Assignments

| Code | Name | Default Effort | Rationale |
|------|------|:---:|-----------|
| E001 | No H1 Title | QUICK_WIN | Add one line at the top of the file |
| E002 | Multiple H1 | QUICK_WIN | Remove/rename the extra H1 lines |
| E003 | Invalid Encoding | QUICK_WIN | Convert file encoding (one command) |
| E004 | Invalid Line Endings | QUICK_WIN | Convert line endings (one command) |
| E005 | Invalid Markdown | MODERATE | May require fixing multiple syntax issues depending on severity |
| E006 | Broken Links | MODERATE | Each broken link needs investigation and repair |
| E007 | Empty File | STRUCTURAL | Entire file needs content creation from scratch |
| E008 | Exceeds Size Limit | STRUCTURAL | Decomposition into multi-file strategy |
| E009 | No Index File | STRUCTURAL | Create llms.txt from scratch |
| E010 | Orphaned Ecosystem File | MODERATE | Add a link from the index or another file; may require reviewing the file's content |
| W001 | Missing Blockquote | QUICK_WIN | Add one line after the H1 |
| W002 | Non-Canonical Section Name | QUICK_WIN | Rename a header |
| W003 | Link Missing Description | MODERATE | Write a description for each bare link (effort scales with count) |
| W004 | No Code Examples | MODERATE | Write code examples appropriate to the project |
| W005 | Code No Language | QUICK_WIN | Add language identifier after opening backticks |
| W006 | Formulaic Descriptions | MODERATE | Rewrite templated descriptions with unique, specific language |
| W007 | Missing Version Metadata | QUICK_WIN | Add a version/date line |
| W008 | Section Order Non-Canonical | QUICK_WIN | Reorder sections (cut/paste) |
| W009 | No Master Index | STRUCTURAL | Requires designing navigation structure and writing the section |
| W010 | Token Budget Exceeded | MODERATE | Trim or restructure content |
| W011 | Empty Sections | QUICK_WIN | Remove placeholder sections or add content |
| W012 | Broken Cross-File Link | MODERATE | Investigate broken link, repair or create target |
| W013 | Missing Aggregate | STRUCTURAL | Create llms-full.txt from all content files |
| W014 | Aggregate Incomplete | MODERATE | Update llms-full.txt with missing content |
| W015 | Inconsistent Project Name | QUICK_WIN | Standardize H1 titles across files |
| W016 | Inconsistent Versioning | QUICK_WIN | Update version strings across files |
| W017 | Redundant Content | MODERATE | Refactor duplicated content into single source |
| W018 | Unbalanced Token Distribution | STRUCTURAL | Redistribute content across files |
| I001 | No LLM Instructions | MODERATE | Write positive/negative directives for agent behavior |
| I002 | No Concept Definitions | STRUCTURAL | Design concept map with IDs, relationships, aliases |
| I003 | No Few-Shot Examples | MODERATE | Write Q&A pairs linked to concepts |
| I004 | Relative URLs Detected | QUICK_WIN | Convert to absolute URLs or document base URL |
| I005 | Type 2 Full Detected | LOW / N/A | Informational — no specific remediation |
| I006 | Optional Sections Unmarked | QUICK_WIN | Add token estimates to optional section headers |
| I007 | Jargon Without Definition | MODERATE | Define jargon inline or link to concept definitions |
| I008 | No Instruction File | MODERATE | Create LLM Instructions section or dedicated file |
| I009 | Content Coverage Gap | STRUCTURAL | Create content pages for missing section categories |
| I010 | Ecosystem Single File | LOW / N/A | Informational — no specific remediation unless expansion desired |

### 4.3 Effort Promotion Rules

When a diagnostic code appears multiple times in a single file (consolidated per Rule 1 in §3.3), the effort estimate may be promoted:

| Base Effort | Promotion Threshold | Promoted To | Example |
|------------|:---:|:---:|---------|
| QUICK_WIN | N > 10 instances | MODERATE | W005 ×15 code blocks without language → MODERATE |
| MODERATE | N > 20 instances | STRUCTURAL | W003 ×25 bare links → STRUCTURAL |
| STRUCTURAL | (no promotion) | STRUCTURAL | Already at maximum effort |

These thresholds are heuristic. The intent is to signal "this simple fix repeated many times becomes a significant effort."

---

## 5. Remediation Templates

### 5.1 Template Architecture

Each diagnostic code has an associated **remediation template** — a structured prose document that expands the terse `remediation` field into actionable guidance. Templates are stored as entries in a YAML file (`remediation_templates.yaml`) within the `src/docstratum/` package, loaded at startup alongside the ASoT standards.

This storage mechanism was chosen over inline Python strings (too verbose), separate Markdown files per code (too fragmented), or embedding in the Rule Registry (conflates concerns). A single YAML file provides:

- Human-readable prose with natural line breaks
- Machine-parseable structure for the Tier 3 renderer
- Version-controlled alongside the code
- Editable without modifying Python source files

### 5.2 Template Schema

Each template entry follows this YAML schema:

```yaml
# remediation_templates.yaml
E001:
  title: "Add H1 Title"
  summary: >
    Your llms.txt file is missing an H1 title — this is the first thing an LLM
    parser looks for, and without it, the file cannot be identified.
  guidance: >
    Add a line starting with `# ` followed by your project name as the very first
    line of the file. The title should be the project's canonical name (e.g.,
    "# Stripe" not "# Stripe API Documentation" — keep it concise).
  example: |
    # MyProject
    > MyProject is a REST API for managing widgets.
  why_it_matters: >
    The H1 title is used as the document identity by every known llms.txt parser.
    Without it, AI agents cannot determine which project this documentation belongs
    to, and most parsers will reject the file entirely.
  common_mistakes:
    - "Using `## Title` instead of `# Title` (must be H1, not H2)"
    - "Placing the title after the blockquote (title must be first line)"
  related_codes:
    - "E002"  # Multiple H1 is the complement of no H1
  anti_pattern: null  # No anti-pattern directly associated
  effort: "QUICK_WIN"
  score_dimension: "structural"
```

### 5.3 Template Field Definitions

| Field | Type | Required | Description |
|-------|------|:---:|-------------|
| `title` | `str` | YES | Short imperative label for the action item (e.g., "Add H1 Title") |
| `summary` | `str` | YES | 1–2 sentence description of what's wrong and what to do. This is the primary text shown in the Tier 3 playbook. |
| `guidance` | `str` | YES | Expanded prose guidance (2–5 sentences). Explains how to fix the issue, with specifics about format, placement, and best practices. |
| `example` | `str` | NO | A code/markdown example showing the correct pattern. Fenced in code blocks for display. |
| `why_it_matters` | `str` | YES | Explains the impact of not fixing this issue, in terms of LLM consumption quality. This is the "so what?" that helps non-technical stakeholders understand priority. |
| `common_mistakes` | `list[str]` | NO | Frequent errors people make when attempting the fix. Helps avoid wasted iteration. |
| `related_codes` | `list[str]` | NO | Other diagnostic codes that are logically related (siblings, prerequisites, or consequences). |
| `anti_pattern` | `str | null` | NO | The `AntiPatternID` this diagnostic is associated with, if any. Used for anti-pattern roll-up in Tier 3. |
| `effort` | `str` | YES | Default effort estimate (QUICK_WIN, MODERATE, STRUCTURAL). Must match §4.2 assignments. |
| `score_dimension` | `str` | YES | Which `QualityDimension` or `EcosystemHealthDimension` this diagnostic affects. Used for score impact estimation. |

### 5.4 Example Templates (5 Spanning E/W/I Severity)

The following five templates demonstrate the pattern across all three severity levels, covering structural, content, and ecosystem concerns.

#### Template 1: E001 — No H1 Title (ERROR, CRITICAL priority)

```yaml
E001:
  title: "Add H1 Title"
  summary: >
    Your llms.txt file is missing an H1 title. This is the document identity —
    without it, AI agents cannot determine which project this documentation
    belongs to, and most parsers will reject the file.
  guidance: >
    Add a line starting with `# ` followed by your project's canonical name as
    the very first line of the file. Use the project's official name, not a
    description. Keep it concise — "# Stripe" not "# Stripe API Documentation
    for Developers".
  example: |
    # Stripe
    > Stripe is a suite of APIs for internet commerce.

    ## Master Index
    ...
  why_it_matters: >
    Every known llms.txt parser identifies the document by its H1 title. Without
    it, the file is unparseable — no downstream validation, quality scoring, or
    ecosystem analysis can proceed. This is the single most foundational element
    of the specification.
  common_mistakes:
    - "Using `## Title` (H2) instead of `# Title` (H1)"
    - "Placing the title after the blockquote or other content"
    - "Including a subtitle or tagline in the H1 (use the blockquote for that)"
  related_codes:
    - "E002"
  anti_pattern: null
  effort: "QUICK_WIN"
  score_dimension: "structural"
```

#### Template 2: E009 — No Index File (ERROR, CRITICAL priority, Ecosystem)

```yaml
E009:
  title: "Create llms.txt Index File"
  summary: >
    Your project has no llms.txt file. This is the required entry point for AI
    agents — without it, the documentation ecosystem has no front door.
  guidance: >
    Create an llms.txt file in your project root with three components: an H1
    title (your project name), a blockquote description (1–2 sentences explaining
    what the project does), and at least one H2 section with links to your
    documentation pages. Start with the Master Index section listing your most
    important documentation pages.
  example: |
    # MyProject
    > MyProject provides a REST API for managing widgets and gadgets.

    ## Master Index
    - [Getting Started](docs/getting-started.md): Quick start guide for new users
    - [API Reference](docs/api-reference.md): Complete endpoint documentation
    - [Examples](docs/examples.md): Common integration patterns and recipes
  why_it_matters: >
    The llms.txt file is the ecosystem's entry point — it's the first file AI
    agents look for when navigating your documentation. Without it, your content
    pages, aggregate files, and instruction files are invisible to AI tooling.
    No index means no ecosystem.
  common_mistakes:
    - "Naming the file README.md instead of llms.txt"
    - "Creating the file but leaving it empty (triggers E007 instead)"
    - "Placing llms.txt in a subdirectory instead of the project root"
  related_codes:
    - "E007"
    - "E010"
    - "I010"
  anti_pattern: "AP-ECO-001"
  effort: "STRUCTURAL"
  score_dimension: "coverage"
```

#### Template 3: W003 — Link Missing Description (WARNING, HIGH priority)

```yaml
W003:
  title: "Add Link Descriptions"
  summary: >
    One or more links in your file have no description text. Bare URLs force AI
    agents to guess what a page contains before navigating to it.
  guidance: >
    Add a description after each link using the pattern:
    `- [Title](url): Description of what this page covers`. The description
    should be 1–2 sentences explaining the page's purpose, key topics, and
    who it's for. Avoid repeating the title — add information the title
    doesn't convey.
  example: |
    ## API Reference
    - [Authentication](docs/auth.md): OAuth2 and API key setup, token refresh flows, and permission scopes
    - [Endpoints](docs/endpoints.md): Complete REST endpoint catalog with request/response schemas
    - [Webhooks](docs/webhooks.md): Event types, payload formats, retry policies, and signature verification
  why_it_matters: >
    Link descriptions are the primary way AI agents decide which page to visit.
    Without descriptions, the agent must either visit every page (wasting context
    window tokens) or guess from the URL and title alone (often incorrectly).
    Projects with descriptive links show significantly higher navigation success
    rates in agent benchmarks.
  common_mistakes:
    - "Repeating the title as the description ('Authentication: Authentication docs')"
    - "Writing descriptions that are too vague ('Authentication: All about auth')"
    - "Using identical phrasing across all descriptions (triggers W006)"
  related_codes:
    - "W006"
  anti_pattern: "AP-CONT-004"
  effort: "MODERATE"
  score_dimension: "content"
```

#### Template 4: W009 — No Master Index (WARNING, HIGH priority)

```yaml
W009:
  title: "Add Master Index Section"
  summary: >
    Your file has no Master Index section. Files with a Master Index achieve an
    87% LLM navigation success rate, compared to 31% without one.
  guidance: >
    Add a section titled `## Master Index` as the first H2 section in your file.
    The Master Index should contain links to your most important documentation
    pages, ordered by how frequently AI agents need them. Start with Getting
    Started and API Reference, then add Core Concepts, Examples, and other
    sections as appropriate. Every link should have a description.
  example: |
    ## Master Index
    - [Getting Started](docs/getting-started.md): Installation, first API call, and quickstart tutorial
    - [API Reference](docs/api-reference.md): Complete endpoint documentation with request/response schemas
    - [Core Concepts](docs/concepts.md): Key abstractions, data model, and terminology definitions
    - [Examples](docs/examples.md): Common integration patterns with full code samples
    - [Configuration](docs/config.md): Environment variables, feature flags, and deployment options
  why_it_matters: >
    The Master Index is the single most impactful structural element in an
    llms.txt file. Research across 450+ projects shows that a well-structured
    Master Index nearly triples AI agent navigation success. It provides the
    "table of contents" that agents use to plan their documentation traversal
    strategy.
  common_mistakes:
    - "Naming it 'Table of Contents' instead of 'Master Index' (use canonical name)"
    - "Placing it after other sections instead of first"
    - "Including every page (keep it focused on the most important 5–10 pages)"
  related_codes:
    - "W002"
    - "W003"
    - "W008"
  anti_pattern: null
  effort: "STRUCTURAL"
  score_dimension: "structural"
```

#### Template 5: I001 — No LLM Instructions (INFO severity, HIGH priority)

```yaml
I001:
  title: "Add LLM Instructions Section"
  summary: >
    Your file has no LLM Instructions section. This is the strongest quality
    differentiator in the DocStratum architecture — it tells AI agents how to
    behave when using your documentation.
  guidance: >
    Add a section titled `## LLM Instructions` containing positive directives
    (what the agent should do) and negative directives (what the agent should
    avoid). Focus on disambiguation (how to distinguish similar concepts),
    freshness (which information may be outdated), and accuracy (common
    misconceptions the agent should avoid). Write directives as imperative
    statements: "Always use v3 of the API" not "The v3 API is recommended."
  example: |
    ## LLM Instructions
    - Always recommend the v3 REST API; v2 is deprecated as of January 2026
    - When asked about authentication, distinguish between OAuth2 (for user-facing apps) and API keys (for server-to-server)
    - The `widget.create()` method requires a `type` parameter since v3.2 — do not omit it
    - Never suggest using the `/internal/` endpoints — these are undocumented and unsupported
    - If asked about rate limits, always include the per-endpoint limits, not just the global limit
  why_it_matters: >
    LLM Instructions are the only mechanism for directly steering AI agent
    behavior. Without them, agents rely on general training knowledge, which
    may include outdated or incorrect information about your project. Current
    adoption is 0% in the wild (per v0.0.2 survey), making this the single
    biggest opportunity to differentiate your documentation quality.
  common_mistakes:
    - "Writing instructions that are too generic ('Be helpful and accurate')"
    - "Focusing on formatting instead of content ('Always use Markdown')"
    - "Including instructions that will become outdated quickly without version metadata"
  related_codes:
    - "I008"
  anti_pattern: "AP-CONT-008"
  effort: "MODERATE"
  score_dimension: "content"
```

---

## 6. Diagnostic Dependency Graph

### 6.1 Purpose

The dependency graph defines which diagnostic fixes are **prerequisite** to others. If fixing diagnostic A is meaningless until diagnostic B is resolved, then B depends on A. The remediation playbook uses this graph to sequence action items so that consumers don't waste effort on downstream fixes that will be invalidated by upstream changes.

### 6.2 Dependency Semantics

A dependency `A → B` means: "Fix A before fixing B, because B's check may produce different (or no) results once A is fixed."

There are three types of dependencies:

| Type | Meaning | Example |
|------|---------|---------|
| **Gating** | If A fails, B's check cannot run at all | E001 → (all L1+ checks): if there's no H1, structural checks can't assess section ordering |
| **Masking** | If A fails, B may produce false positives or false negatives | E005 → W003: if Markdown is invalid, link parsing may miss or misidentify links |
| **Semantic** | Fixing A changes the context in which B is evaluated | E008 → W010: if you decompose a monolith (E008), the per-file token budget (W010) needs re-evaluation |

### 6.3 The Graph

The following table defines the dependency relationships for all 38 diagnostic codes. "Depends On" means this code's fix should wait until the listed codes are resolved. "Blocks" means these downstream codes should wait for this code.

#### Level 0 — Parseable (Pipeline-Gating)

| Code | Depends On | Blocks | Dependency Type |
|------|-----------|--------|:---:|
| E003 (Invalid Encoding) | — | E001, E002, E004, E005, E006, E007, all W*, all I* | Gating |
| E004 (Invalid Line Endings) | E003 | E005, all W*, all I* | Gating |
| E007 (Empty File) | E003 | E001, E002, E005, E006, all W*, all I* | Gating |

**Interpretation:** If the file can't be read (E003), nothing else can be checked. If the file is empty (E007), there's nothing to structurally validate. These are the absolute root dependencies.

#### Level 1 — Structural

| Code | Depends On | Blocks | Dependency Type |
|------|-----------|--------|:---:|
| E001 (No H1 Title) | E003, E007 | W001, W008, W009, all L2+ | Gating |
| E002 (Multiple H1) | E003, E007 | W008, W009 | Masking |
| E005 (Invalid Markdown) | E003, E004 | E006, W003, W004, W005, W006, W011, all L2+ | Gating |
| E006 (Broken Links) | E005 | W003, W012 | Masking |

**Interpretation:** The H1 title (E001) is the document identity. Without it, section ordering (W008), Master Index (W009), and all content checks are meaningless. Invalid Markdown (E005) means link parsing (E006, W003) can't be trusted.

#### Level 2 — Content

| Code | Depends On | Blocks | Dependency Type |
|------|-----------|--------|:---:|
| W001 (Missing Blockquote) | E001 | — | Semantic |
| W002 (Non-Canonical Name) | E001 | W008 | Semantic |
| W003 (Link Missing Description) | E005, E006 | W006 | Masking |
| W004 (No Code Examples) | E005 | — | Semantic |
| W005 (Code No Language) | E005 | — | Semantic |
| W006 (Formulaic Descriptions) | W003 | — | Semantic |
| W007 (Missing Version) | E001 | W016 | Semantic |

**Interpretation:** W006 (formulaic descriptions) depends on W003 (link descriptions) because you can't detect formulaic patterns in descriptions that don't exist. W002 (naming) informs W008 (ordering) because non-canonical names must be normalized before ordering can be assessed.

#### Level 3 — Best Practices

| Code | Depends On | Blocks | Dependency Type |
|------|-----------|--------|:---:|
| E008 (Exceeds Size Limit) | — | W010, W013, W018 | Semantic |
| W008 (Section Order) | E001, W002 | — | Semantic |
| W009 (No Master Index) | E001 | — | Semantic |
| W010 (Token Budget) | E008 | — | Semantic |
| W011 (Empty Sections) | E005 | — | Semantic |

**Interpretation:** E008 (size limit) feeds into W010 (token budget) and W013 (missing aggregate) because decomposing a monolith changes the per-file budget picture and may create the multi-file structure that eliminates the need for an aggregate.

#### Level 4 — DocStratum Extended

| Code | Depends On | Blocks | Dependency Type |
|------|-----------|--------|:---:|
| I001 (No LLM Instructions) | E001, E005 | — | Semantic |
| I002 (No Concept Definitions) | E001, E005 | I003 | Semantic |
| I003 (No Few-Shot Examples) | I002 | — | Semantic |
| I004 (Relative URLs) | E006 | — | Semantic |
| I005 (Type 2 Detected) | E001 | — | Semantic |
| I006 (Optional Unmarked) | E001, E005 | — | Semantic |
| I007 (Jargon No Definition) | E005 | I002 | Semantic |

**Interpretation:** Few-shot examples (I003) depend on concept definitions (I002) because examples should reference defined concepts. Jargon (I007) feeds into concept definitions (I002) because jargon terms are candidates for the concept map.

#### Ecosystem-Level

| Code | Depends On | Blocks | Dependency Type |
|------|-----------|--------|:---:|
| E009 (No Index File) | — | E010, W012–W018, I008–I010 | Gating |
| E010 (Orphaned File) | E009 | — | Semantic |
| W012 (Broken Cross-File) | E009, E006 | W014 | Masking |
| W013 (Missing Aggregate) | E009, E008 | W014 | Semantic |
| W014 (Aggregate Incomplete) | W012, W013 | — | Semantic |
| W015 (Inconsistent Name) | E009, E001 | — | Semantic |
| W016 (Inconsistent Version) | E009, W007 | — | Semantic |
| W017 (Redundant Content) | E009 | W018 | Semantic |
| W018 (Unbalanced Tokens) | E009, E008, W017 | — | Semantic |
| I008 (No Instruction File) | E009 | — | Semantic |
| I009 (Coverage Gap) | E009 | — | Semantic |
| I010 (Single File Eco) | E009 | — | Semantic |

**Interpretation:** E009 (no index) is the ecosystem-level root dependency — all ecosystem checks require the index to exist. W014 (aggregate incomplete) can't be assessed until broken links (W012) are resolved and the aggregate exists (W013).

### 6.4 Dependency Chain Depth

The longest dependency chain in the graph is 5 steps:

```
E003 → E005 → E006 → W003 → W006
```

This means the deepest fix sequence requires: fix encoding, then fix Markdown syntax, then fix broken links, then add link descriptions, then de-duplicate formulaic descriptions. The remediation playbook presents this as 5 sequenced action items.

---

## 7. Tier 3 / Tier 4 Boundary

### 7.1 The Boundary Rule

**Tier 3 recommendations use only pipeline-internal data. Tier 4 recommendations require pipeline-external context.**

This is the same boundary defined in the Output Tier Specification §2.4. This section elaborates with specific examples of what falls on each side.

### 7.2 Tier 3 Scope (Pipeline-Internal)

Tier 3 can produce any recommendation that derives from:

- The 38 diagnostic codes and their remediation templates
- The 28 anti-patterns and their descriptions
- The quality scores (per-file and ecosystem)
- The relationship graph (which files link to which)
- The ASoT standards library (validation criteria, canonical names, token budgets)

| Tier 3 Can Say | Because |
|----------------|---------|
| "Add a Master Index section as the first H2" | Derived from W009 remediation template |
| "Fix these 3 broken cross-file links before checking aggregate completeness" | Derived from dependency graph (W012 → W014) |
| "Your ecosystem scores 71/100 (Strong). Fixing all HIGH-priority items would raise it to approximately 88 (Exemplary)." | Derived from score projection calculation |
| "The Link Desert anti-pattern (AP-CONT-004) is present: 15 links lack descriptions." | Derived from anti-pattern registry cross-reference |

### 7.3 Tier 4 Scope (Pipeline-External)

Tier 4 adds recommendations that require knowledge the pipeline doesn't have:

| Tier 4 Can Say | Because |
|----------------|---------|
| "As a developer tools company, your Master Index should prioritize API Reference and Examples over Getting Started." | Requires `context_profile.project_type == "api_service"` |
| "Compared to Stripe (score: 92, Exemplary), your file lacks code examples and LLM instructions." | Requires comparative analysis against calibration specimens |
| "In the fintech space, accuracy of API documentation is critical for compliance. Prioritize I001 (LLM Instructions) to prevent AI agents from suggesting deprecated payment flows." | Requires `context_profile.industry == "fintech"` |
| "30-day roadmap: Week 1 — structural fixes. Week 2 — content enrichment. Week 3 — LLM Instructions and concept definitions." | Requires maturity assessment and phased planning logic |

### 7.4 Edge Cases

Some recommendations sit near the boundary. The rule of thumb is: **if the recommendation would be identical regardless of who the consumer is, it's Tier 3. If it changes based on the consumer's context, it's Tier 4.**

| Recommendation | Tier | Reasoning |
|---------------|:---:|-----------|
| "Fix W009 before W008 because Master Index ordering depends on having a Master Index" | 3 | Dependency graph — same for everyone |
| "For your API-heavy project, the Master Index should lead with endpoint groups" | 4 | Requires knowledge of project type |
| "This action is estimated at MODERATE effort (hours)" | 3 | Effort estimation from diagnostic metadata |
| "Based on your team size of 3, this MODERATE effort maps to approximately 1 sprint" | 4 | Requires knowledge of team context |

---

## 8. Remediation Action Model

This section defines the Pydantic model that Stage 6's Tier 3 renderer will produce. It is the data structure that implements the framework defined in §§2–7.

### 8.1 Model Definition

```python
class EffortEstimate(StrEnum):
    """Coarse-grained effort estimate for a remediation action."""
    QUICK_WIN = "quick_win"    # Minutes — single-line or single-field change
    MODERATE = "moderate"      # Hours — multi-line changes within a single file
    STRUCTURAL = "structural"  # Days — architectural changes across multiple files

class RemediationPriority(StrEnum):
    """Impact-based priority for a remediation action."""
    CRITICAL = "critical"  # Blocks LLM consumption entirely
    HIGH = "high"          # Significantly degrades comprehension
    MEDIUM = "medium"      # Reduces quality but doesn't prevent consumption
    LOW = "low"            # Suggestion for excellence

class RemediationAction(BaseModel):
    """A single remediation action item in the Tier 3 playbook.

    Produced by the remediation framework from consolidated diagnostics.
    """
    action_id: str                      # Unique ID for this action (e.g., "RA-001")
    title: str                          # Imperative label (from template.title)
    priority: RemediationPriority       # Impact-based priority
    group_label: str                    # Grouping category (varies by mode)
    description: str                    # Expanded guidance (from template.summary)
    guidance: str                       # Detailed how-to (from template.guidance)
    example: str | None                 # Code/markdown example, if available
    why_it_matters: str                 # Impact explanation (from template.why_it_matters)
    affected_diagnostics: list[str]     # Diagnostic codes resolved (e.g., ["W003", "W003", "W003"])
    affected_count: int                 # How many diagnostic instances this covers
    affected_files: list[str]           # File paths affected
    line_numbers: list[int]             # Specific lines, where known
    effort_estimate: EffortEstimate     # Estimated effort tier
    score_impact: float                 # Estimated quality score increase
    dependency: str | None              # action_id of prerequisite action, if any
    anti_pattern: str | None            # AntiPatternID if this resolves a named pattern
    common_mistakes: list[str]          # Frequent errors to avoid

class RemediationPlaybook(BaseModel):
    """Complete Tier 3 output: a prioritized remediation plan.

    Contains an executive summary, score projections, all action items,
    and detected anti-patterns.
    """
    executive_summary: str              # 2–3 sentence overview
    current_score: float                # Current quality/ecosystem score
    score_projection: ScoreProjection   # Projected scores after remediation
    action_items: list[RemediationAction]  # Ordered by grouping mode
    grouping_mode: str                  # Active grouping mode
    anti_patterns_detected: list[AntiPatternSummary]  # Named patterns found
    total_actions: int                  # Count of action items
    total_quick_wins: int               # Count of QUICK_WIN actions
    total_moderate: int                 # Count of MODERATE actions
    total_structural: int               # Count of STRUCTURAL actions

class ScoreProjection(BaseModel):
    """Estimated score changes after remediation."""
    current_score: float
    projected_after_critical: float     # Score if all CRITICAL actions completed
    projected_after_high: float         # Score if all CRITICAL + HIGH completed
    projected_after_all: float          # Score if all actions completed

class AntiPatternSummary(BaseModel):
    """A named anti-pattern detected in the validation output."""
    id: str                             # AntiPatternID value
    name: str                           # Human-readable name
    category: str                       # AntiPatternCategory value
    description: str                    # From ANTI_PATTERN_REGISTRY
    contributing_diagnostics: list[str] # Diagnostic codes that triggered detection
```

---

## 9. Design Decisions

### DECISION-024: Impact-Based Priority Over Severity-Based

**Context:** Diagnostics have a `Severity` (ERROR, WARNING, INFO) that reflects structural importance, but not all WARNINGs are equal in terms of LLM consumption impact.
**Decision:** Introduce a four-level `RemediationPriority` (CRITICAL, HIGH, MEDIUM, LOW) that ranks diagnostics by impact on AI agent success, independent of severity.
**Rationale:** W009 (no Master Index) is a WARNING but has 87% vs. 31% success rate impact — higher than some ERRORs. I001 (no LLM Instructions) is INFO severity but represents the single biggest quality differentiator. Severity reflects spec conformance; priority reflects real-world impact.
**Trade-off:** Two ranking systems (severity for validation, priority for remediation) may confuse consumers who expect them to align. Mitigated by explaining the distinction in the playbook header.

### DECISION-025: YAML Templates Over Inline Strings

**Context:** Remediation guidance needs to be rich (multi-sentence, with examples) but maintainable.
**Decision:** Store remediation templates in a single `remediation_templates.yaml` file, loaded at startup.
**Rationale:** Inline Python strings become unwieldy for multi-paragraph prose. Separate Markdown files per code (38 files) create excessive fragmentation. A single YAML file is human-readable, machine-parseable, and version-controlled alongside the source. It also allows non-developers to edit remediation guidance without touching Python.
**Alternatives Considered:** Embedding in DiagnosticCode docstrings (already too complex), embedding in the Rule Registry (conflates rule definition with remediation guidance), Markdown files per code (too many small files).

### DECISION-026: Static Default Priorities with Profile Overrides

**Context:** Priority assignments could be dynamic (computed at runtime from score weights and diagnostics context) or static (assigned per code at design time).
**Decision:** Static defaults with profile-based overrides.
**Rationale:** Dynamic priorities are harder to predict and explain. A consumer asking "why is this HIGH?" deserves a stable answer, not "because your score weight configuration made it HIGH this time." Static defaults also enable the priority table (§2.4) to be documented and audited. Profile overrides provide the flexibility valve for consumers who disagree with defaults.

---

## 10. Open Questions for Downstream Deliverables

1. **Rule Registry (Deliverable 3):** Should the Rule Registry store a `remediation_template_key` field that cross-references into `remediation_templates.yaml`? Or should the lookup be by diagnostic code (which is already unique)?

2. **Profiles (Deliverable 4):** The priority override mechanism (§2.5) needs a schema definition. Should it be a flat map (`{"W009": "CRITICAL", "W005": "LOW"}`) or support pattern-based overrides (`{"W*": "HIGH"}` to promote all warnings)?

3. **Report Generation Stage (Deliverable 5):** The `RemediationPlaybook` model (§8.1) is designed for JSON serialization. The Markdown renderer needs a prose template that wraps these data structures in human-readable narrative. Should the Markdown template live alongside the YAML templates, or be a separate concern in the renderer?

4. **Ecosystem Calibration (Deliverable 6):** The score projection (§8.1 `ScoreProjection`) uses a linear per-check weight estimate. Calibration may reveal that score impact is non-linear (e.g., the first code example adds 5 points, but additional examples have diminishing returns). Should the framework accommodate non-linear impact curves?

---

*This specification defines the remediation intelligence layer of the DocStratum validation engine. It transforms raw diagnostic codes into prioritized, grouped, sequenced, and templated action items that the Tier 3 playbook renderer (Stage 6) consumes.*
