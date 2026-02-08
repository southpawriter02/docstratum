# DocStratum Research Synthesis — v0.0.x Consolidated Findings

> **Phase:** Research & Discovery (v0.0.x) — Complete
> **Scope:** v0.0.1 through v0.0.5 (5 phases, 17 sub-parts, 5 summaries, 27 total documents)
> **Date Completed:** 2026-02-06
> **Synthesized By:** Claude Opus 4.6
> **Purpose:** Single-source reference that consolidates all v0.0.x findings into an actionable, cross-referenced research report — the bridge between research and implementation.

---

## 1. Research Overview

### 1.1 What This Report Covers

Between 2026-02-05 and 2026-02-06, the DocStratum project completed a comprehensive research program spanning five sequential phases, each building on the findings of its predecessors. The program analyzed the `llms.txt` specification (published September 2024 by Jeremy Howard), its real-world ecosystem of implementations and tools, the surrounding standards landscape, and the strategic opportunity space for DocStratum — a project that aims to transform llms.txt from a simple page index into a semantically enriched documentation layer for AI agents.

This synthesis report distills approximately 900 KB of research documentation into a single reference document. It is organized around 8 key findings, each supported by evidence from multiple research phases, and concludes with prioritized recommendations and open questions.

### 1.2 Research Questions Answered

The v0.0.0 parent document posed 16 research questions across four dimensions: Specification, Ecosystem, Technical, and Strategic. All 16 have been answered with evidence:

**Specification questions** (answered by v0.0.1): The official spec defines a Markdown-based file format with an H1 title, blockquote description, H2 sections, and link lists. A formal ABNF grammar was defined, 8 specification gaps were identified and prioritized, and 28 edge cases were cataloged across four categories.

**Ecosystem questions** (answered by v0.0.2 and v0.0.3): 24 real-world implementations were audited across 6 categories, 5 implementation archetypes were identified, and quality predictors were quantified. 75+ tools exist in the ecosystem, but zero provide formal validation or semantic enrichment. Community sentiment is deeply polarized (~35% enthusiastic, ~30% cautious, ~25% skeptical, ~10% hostile).

**Technical questions** (answered by v0.0.1 and v0.0.4): The file format is Markdown (CommonMark 0.30 + GFM). Large documentation sites use tiered strategies (small/medium/full variants). AI agents consume these files primarily via MCP (Model Context Protocol) servers in coding assistants like Cursor, Claude Desktop, and Windsurf. 57 automated validation checks were defined, plus a 100-point composite quality scoring pipeline.

**Strategic questions** (answered by v0.0.3 and v0.0.5): llms.txt occupies Layer 5 (AI Content Delivery) of a 5-layer AI-Readability Stack. Related standards include robots.txt, sitemap.xml, schema.org, MCP, and ai.txt. The adoption trajectory is growing (1,000–5,000 substantive implementations), but critically, no major LLM provider has confirmed using llms.txt for web retrieval. The validated use case is AI coding assistants via MCP.

### 1.3 Methodology

The research program used five complementary methods:

1. **Specification analysis** (v0.0.1) — First-principles analysis of the official spec, producing a formal ABNF grammar, gap analysis, and processing method taxonomy. Theoretical analysis validated against 11 empirical specimens.

2. **Real-world audit** (v0.0.2) — Systematic audit of 18 implementations (later expanded to 24 with specimen data) using standardized audit forms with 9-item structural checklists and 4-dimension content ratings.

3. **Ecosystem survey** (v0.0.3) — Parallel research across npm, PyPI, crates.io, GitHub, and web search. Cataloged 75+ tools, 30 key players, 16 standards, and 25 consolidated gaps.

4. **Best practices synthesis** (v0.0.4) — Cross-referenced all prior findings into 57 automated checks, 22 anti-patterns, a 100-point scoring rubric, and 16 formal design decisions.

5. **Requirements definition** (v0.0.5) — Converted evidence into 68 functional requirements, 21 non-functional requirements, 6 constraints, 32 out-of-scope items, and a 32-feature MVP definition with testable success criteria.

An **empirical enrichment pass** on 2026-02-06 integrated conformance data from 11 real-world specimen files (collected via direct browser download) across all sub-parts, correcting several significant overestimates from the initial indirect-analysis phase.

### 1.4 Evidence Base Summary

| Source Type | Count | Coverage |
|-------------|-------|----------|
| Specification documents analyzed | 1 official spec + 6 related standards | Full spec coverage |
| Real-world implementations audited | 24 unique sites | 6 industry categories |
| Empirical specimen files analyzed (byte-level) | 11 files | 9 Type 1 Index + 2 Type 2 Full |
| Tools cataloged | 75+ | 7 tool categories |
| Key players verified | 30 | Specification, adoption, criticism |
| Standards compared | 16 | 5 layers of the AI-readable web |
| Unique ecosystem gaps identified | 25 | 4 severity levels |
| Automated validation checks defined | 57 | 3 dimensions (structural, content, anti-pattern) |
| Anti-patterns cataloged | 22 | 4 severity categories |
| Design decisions resolved | 16 | Format, architecture, validation, strategy |
| Functional requirements specified | 68 | 7 software modules |
| Non-functional requirements specified | 21 | 5 quality dimensions |

### 1.5 Confidence Levels

| Finding Category | Confidence | Basis |
|-----------------|------------|-------|
| Specification structure and gaps | **High** | ABNF grammar validated against 11 specimens; 3/11 at 100% conformance proves the grammar works |
| Quality predictors (code examples, size irrelevance) | **High** | Correlation analysis across 18 implementations; confirmed by enrichment pass |
| Adoption Paradox (no confirmed search LLM usage) | **High** | Google explicit rejection; 300K-domain study; Redocly analysis; server log analysis |
| MCP as validated transport | **High** | Direct observation: Cursor, Claude Desktop, Windsurf consume llms.txt via MCP |
| Tooling gap (zero formal validation) | **High** | Systematic survey of 75+ tools across 6 registries |
| Community sentiment distribution | **Medium** | Qualitative assessment from community channels; not randomly sampled |
| Token budget optimal ranges | **Medium** | Derived from specimen data and gold standard analysis; not A/B tested at scale |
| Competitive risk assessments | **Medium** | Based on current landscape; market dynamics could shift rapidly |

---

## 2. Key Findings

Eight major findings emerged from the research program. Each is supported by evidence from multiple phases and carries specific implications for DocStratum's design.

### Finding 1: The Specification Is Sound but Incomplete — 8 Gaps Define the Opportunity

**Statement:** The official llms.txt specification (Jeremy Howard, September 2024) defines a workable file format, but leaves 8 significant gaps that create real-world problems. These gaps — not the spec's existing features — define DocStratum's entire value proposition.

**Evidence:**

- v0.0.1b identified and analyzed 8 specification gaps, ranked by priority:
  - **P0 Critical (5):** Concept/terminology definitions, few-shot Q&A pairs, validation schema, maximum file size, required metadata
  - **P1 Important (1):** Versioning scheme
  - **P2 Nice-to-have (2):** Caching recommendations, multi-language support
- The empirical enrichment pass (11 specimens) confirmed all 8 gaps as real and universally unaddressed: 0/11 specimens include structured metadata, concept definitions, or few-shot examples of any kind
- v0.0.3 found that 0 of 75+ tools address any of the P0 gaps

**Frequency:** Universal. No specimen or audited implementation addresses any P0 gap.

**Impact:** Critical. Without concept definitions, LLMs hallucinate domain terminology. Without file size guidance, files range from 1.1 KB to 25 MB with no consumer able to handle the upper end. Without validation schema, inconsistent implementations proliferate with no way to detect or correct errors.

**Confidence:** High — empirically validated across 24 implementations and 11 specimens.

**Implication for DocStratum:** The P0 gaps are the product. DocStratum's 3-layer architecture (Master Index → Concept Map → Few-Shot Bank) directly addresses three of five P0 gaps. The validation pipeline addresses the other two. This is where the project creates unique, defensible value that no other tool provides.

---

### Finding 2: The Adoption Paradox — Grassroots Growth, Zero Confirmed LLM Provider Usage

**Statement:** llms.txt has genuine grassroots adoption (1,000–5,000 substantive implementations, 844K detected by BuiltWith, 75+ tools), but no major search/chat LLM provider has confirmed using these files for web retrieval, training, or inference. Google has explicitly rejected the standard.

**Evidence:**

- **For adoption:** 1,300+ entries in llmtxt.app directory; 500+ in llmstxthub.com; 844K+ detected by BuiltWith (mostly auto-generated); 75+ tools across 7 categories; notable adopters include Anthropic, Cloudflare, Stripe, Vercel, Supabase, Shopify
- **Against LLM usage:** Google's John Mueller called it comparable to the discredited keywords meta tag; Google's Gary Illyes (July 2025): "Google doesn't support LLMs.txt and isn't planning to"; Search Engine Journal's 300,000-domain study found no correlation between llms.txt presence and AI citations; Redocly testing: "Unless you explicitly paste the llms.txt file into an LLM, it doesn't do anything"; server log analysis shows LLM crawlers (GPTBot, ClaudeBot, PerplexityBot) generally do NOT request /llms.txt files
- **Partial resolution:** AI coding assistants (Cursor, Claude Desktop, Windsurf) *do* actively consume llms.txt via MCP servers — this is the validated market

**Frequency:** This paradox is the central strategic reality of the entire ecosystem. Every tool builder, adopter, and critic references it directly or implicitly.

**Impact:** Existential for the market. If search/chat LLMs never adopt llms.txt, the standard's audience is permanently limited to developer tooling via MCP. This is still a viable and growing market, but it constrains the addressable opportunity.

**Confidence:** High — supported by explicit statements from Google, independent studies, and server log analysis. The *partial resolution* (MCP/coding assistants) is also high confidence based on direct observation.

**Implication for DocStratum:** Target AI coding assistants via MCP exclusively (DECISION-015). Do not build SEO-adjacent features. Do not optimize for crawler-based discovery. The validated market is developers using AI coding assistants; the unvalidated market is search/chat LLMs. DocStratum should build for the validated market while remaining transferable if the unvalidated market materializes.

---

### Finding 3: Quality Is Driven by Curation, Not Volume — File Size Does NOT Predict Quality

**Statement:** The strongest predictor of llms.txt quality is the presence of concrete code examples (r ≈ 0.65), followed by thoughtful section organization (r ≈ 0.60) and active maintenance signals (r ≈ 0.55). File size has near-zero correlation with quality (r ≈ −0.05). An 8K-token well-curated document outperforms a 200K-token raw dump.

**Evidence:**

- v0.0.2c correlation analysis across 18 implementations:
  - Concrete code examples: r ≈ 0.65 (Strong)
  - Organized sections (5–12): r ≈ 0.60 (Strong)
  - Active versioning: r ≈ 0.55 (Moderate)
  - Category (Framework > Enterprise): r ≈ 0.45 (Weak-Moderate)
  - File size: r ≈ −0.05 (Near-zero)
- v0.0.1c processing methods analysis demonstrated that selective inclusion with semantic enrichment yields better agent output than raw concatenation, regardless of total content volume
- Gold standard calibration (v0.0.4b): Svelte scores 92/100 at moderate size; NVIDIA scores 24/100 despite having a production implementation; Cloudflare's 3.7M-token file is flagged as an anti-pattern

**Frequency:** This finding applies across all 24 audited implementations. No counterexamples were found — no large-but-low-quality file scored well, and no small-but-well-curated file scored poorly.

**Impact:** Fundamental — this finding shapes DocStratum's entire philosophical approach. It validates the "Writer's Edge" thesis: a skilled technical writer with strong information architecture skills can outperform a sophisticated RAG pipeline by writing better source material.

**Confidence:** High — supported by quantitative correlation data and confirmed by gold standard calibration.

**Implication for DocStratum:** Token budgets should enforce *curation*, not comprehensiveness. The composite quality scoring pipeline weights content quality at 50% (the highest weight) because code examples — the strongest predictor — are a content quality metric. Structural compliance (30%) is a gating factor (necessary but not sufficient), and anti-pattern absence (20%) operates as a deduction mechanism.

---

### Finding 4: Two Distinct Document Types Exist — Type 1 Index vs. Type 2 Full

**Statement:** The ecosystem has evolved two fundamentally different document types sharing the `llms.txt` filename convention: Type 1 Index files (curated link catalogs, 1.1 KB–225 KB, 80–100% spec conformance) and Type 2 Full files (inline documentation dumps, 1.3 MB–25 MB, 5–15% spec conformance). The official ABNF grammar covers only Type 1. A bimodal size distribution with no specimens in the 225 KB – 1.3 MB gap confirms these are distinct paradigms, not a continuum.

**Evidence:**

- Empirical specimen analysis (v0.0.1a enrichment): 9 of 11 specimens are Type 1 Index (Astro 2.6 KB, Resend 1.1 KB, OpenAI 19 KB, Deno 63 KB, Neon 68 KB, LangChain 82 KB, Docker 167 KB, Cloudflare 225 KB, Cursor 7.5 KB); 2 are Type 2 Full (Vercel AI SDK 1.3 MB, Anthropic claude-llms-full.txt 25 MB)
- Conformance analysis confirms the split: Type 1 files achieve 80–100% conformance; Type 2 files achieve only 5–15%
- The `llms-full.txt` naming convention (co-developed by Mintlify and Anthropic, November 2024) acknowledges this split informally, but provides no structural definition
- No specimens exist in the 225 KB – 1.3 MB range, confirming a natural boundary

**Frequency:** 100% of specimens fall cleanly into one type or the other. The bimodal distribution has no overlap zone.

**Impact:** High — architectural. DocStratum's parser must handle both types. The validation pipeline must classify documents before applying rules (Type 1 grammar doesn't apply to Type 2). The context builder must apply different processing strategies per type.

**Confidence:** High — based on direct byte-level analysis of 11 production files.

**Implication for DocStratum:** The parser/loader module needs a classification heuristic early in the pipeline. Type 1 files receive full ABNF validation. Type 2 files receive a different treatment (likely the concatenation or summarization processing methods from v0.0.1c). The ~250 KB boundary serves as the classification threshold.

---

### Finding 5: MCP Is the Validated Transport Layer — Not HTTP Crawlers

**Statement:** MCP (Model Context Protocol) is the empirically validated mechanism through which AI agents actually consume llms.txt content today. AI coding assistants — Cursor, Claude Desktop, and Windsurf — access llms.txt through MCP servers, making MCP the primary delivery pathway. This was added as Layer 0 of the AI-Readability Stack.

**Evidence:**

- v0.0.1d identified MCP as the transport mechanism: AI coding assistants consume llms.txt via MCP servers like LangChain's `mcpdoc`, `mcp-llms-txt-explorer`, and Context7 (Upstash)
- v0.0.3c analyzed MCP's architecture: a JSON-RPC-based protocol defining Resources, Tools, and Prompts. llms.txt sections map to MCP *Resources* — servers expose documentation sections for selective retrieval rather than serving the raw file
- The adoption paradox (Finding 2) eliminates HTTP crawling as the primary transport: server logs show LLM crawlers generally don't request /llms.txt
- Type 2 Full documents (1.3 MB–25 MB) are physically impractical for crawler-based discovery — their existence only makes sense in an MCP context where agents can selectively request subsections
- MCP moved to the Linux Foundation (AAIF) in November 2025, with backing from Anthropic, OpenAI, and Google — confirming its institutional staying power

**Frequency:** All confirmed llms.txt consumption cases traced during the research involve MCP-based delivery.

**Impact:** High — determines the entire output architecture. DocStratum's enriched output must be designed for MCP consumption, not static file serving to crawlers.

**Confidence:** High — based on direct observation of AI coding assistant behavior and MCP server architecture.

**Implication for DocStratum:** The critical path (v0.0.3d) terminates at "MCP server" — grammar → validator → enrichment → MCP server. The 3-layer architecture maps naturally to MCP tool calls: agents request Layer 1 (Master Index) for navigation, then selectively request Layer 2 (Concept Map) or Layer 3 (Few-Shot Bank) as needed. Token budgets are sized for coding assistant context windows (3K–50K), not search engine processing.

---

### Finding 6: The Tooling Ecosystem Is Saturated in Generation, Vacant in Governance

**Statement:** The llms.txt ecosystem has 75+ tools, but they are overwhelmingly concentrated in generation (20+ generators, 25+ framework plugins, 8+ free SaaS generators). Zero tools provide formal schema validation, semantic enrichment, CI/CD integration, quality scoring, or version management. The generation problem is solved; the governance problem is wide open.

**Evidence:**

- v0.0.3a cataloged 75+ tools across 7 categories with 5 feature comparison matrices:
  - Generation: 20+ standalone generators + 25+ framework plugins = 45+ tools
  - Validation: 6+ web validators, all using informal rules; zero support ABNF, JSON Schema, or Pydantic validation
  - Parsers/consumers: Only 3+ tools (llms-txt-rs, llms-txt-php, llms_txt2ctx)
  - MCP servers: 4+ (mcpdoc, mcp-llms-txt-explorer, Context7)
- The feature gap matrix (v0.0.3a) identifies 11 capabilities that no tool provides:
  - Formal ABNF/schema validation: 0 tools (CRITICAL)
  - Semantic enrichment: 0 tools (CRITICAL)
  - CI/CD-native validation: 0 tools (HIGH)
  - Multi-dimension quality scoring: 0 tools (HIGH)
  - Version management: 0 tools (HIGH)
- ~60% of tools are v0.x experimental, signaling rapid growth but low maturity
- Mintlify auto-generates llms.txt for thousands of sites, but produces formulaic, low-information-density defaults — the "Mintlify Homogeneity" risk (v0.0.2d anti-pattern #5)

**Frequency:** The generation-governance gap is universal across the ecosystem. No tool in any category addresses any CRITICAL gap.

**Impact:** High — this gap defines DocStratum's entire product positioning. DocStratum should NOT build another generator (saturated market); it should build the enrichment and governance layer that sits between existing generators and existing consumers.

**Confidence:** High — based on systematic survey of npm, PyPI, crates.io, GitHub, WordPress plugins, and web search.

**Implication for DocStratum:** The integration architecture positions DocStratum as middleware: accept llms.txt from any of the 75+ existing generators → validate → score → enrich → output to consumers via MCP. This avoids competing with the saturated generation market while filling the governance vacuum.

---

### Finding 7: Structural Compliance Is Lower Than Expected — Blockquote at 55%, Not 100%

**Statement:** The initial audit (v0.0.2, based on indirect sources) estimated near-universal baseline compliance. The empirical enrichment pass revealed that indirect estimation systematically overestimates compliance by 30–45% on individual structural elements. Blockquote compliance is 55% (6/11 specimens), not the previously assumed 100%. H1 uniqueness is 82% (Cursor has 2 H1s). Link list format compliance is 89% for Type 1 (Cursor uses bare URLs).

**Evidence:**

- v0.0.2 original estimates (18 sites, indirect): H1 title 100%, Blockquote 100%, Link format 100%, H2 headers 100%
- Empirical specimen data (11 files, direct): H1 uniqueness 82%, Blockquote **55%**, Link format 89% (Type 1 only), H2 headers 100% (Type 1 only)
- Missing blockquote specimens: Cloudflare, Cursor, Docker, LangChain, Resend — 5 of 11, spanning multiple categories
- The conformance range across specimens is 5%–100% (a 95-point spread), demonstrating enormous quality variance

**Frequency:** The overcounting pattern was consistent across multiple structural elements, not an isolated anomaly. Only H2 headers remained at 100% after correction.

**Impact:** Medium-High — affects parser design and validation severity. Blockquote should be treated as "strongly recommended" rather than "mandatory baseline" in the DocStratum schema, because enforcing it as mandatory would reject nearly half of real-world files.

**Confidence:** High — based on direct byte-level analysis of production files. The correction magnitude (100% → 55%) is large enough to have design implications.

**Implication for DocStratum:** The parser follows the "permissive input, strict output" principle (DECISION from v0.0.1a). Missing blockquotes generate warnings, not errors. The validation pipeline accommodates real-world deviations gracefully, returning partial results with annotations rather than rejecting files outright. The 95-point conformance spread (5% to 100%) validates the need for a multi-level quality scoring system rather than a binary pass/fail validator.

---

### Finding 8: LLM Instructions Adoption Is at 0% — The Largest Untapped Opportunity

**Statement:** Explicit LLM Instructions — positive, negative, and conditional directives that guide agent behavior — are used by precisely one known implementation (Stripe, excluded from the audit sample) and zero of the 18 audited or 11 specimen implementations. This is the single largest gap between what would improve LLM output quality and what the ecosystem actually implements.

**Evidence:**

- v0.0.2 audit: 0/18 implementations include an LLM Instructions section
- Empirical specimens: 0/11 specimens include any form of LLM Instructions
- The "Optional" section (the spec's only mechanism for lower-priority content) has similarly low adoption: 0/11 specimens, 11% (2/18) in the original audit (only Svelte and FastHTML)
- Stripe's implementation (analyzed in v0.0.1, excluded from v0.0.2 audit to avoid duplication) is the only known real-world example of explicit LLM Instructions, including directives like "always default to the latest API version" and "PaymentIntent ≠ Charge"
- v0.0.4b identified LLM Instructions as a P0 requirement and elevated it to the COULD tier in the MUST/SHOULD/COULD framework — meaning it's the key differentiator for Exemplary (90–100 score) files

**Frequency:** 0% adoption across 29 unique implementations (18 audited + 11 specimens, accounting for 5 overlapping entries). Universal absence.

**Impact:** High — LLM Instructions directly improve agent output quality by preventing common mistakes (negative directives), encouraging best practices (positive directives), and handling conditional logic (version-dependent behavior). Their absence means every llms.txt file today leaves agent behavior guidance entirely to chance.

**Confidence:** High — the sample is large enough (29 unique sites) to confirm that this is genuinely not adopted, not merely rare.

**Implication for DocStratum:** LLM Instructions are DocStratum's most visible differentiator. They're the feature that makes the before/after agent comparison in the demo most dramatic. The content structure module (FR-020) defines LLM Instructions as a first-class component of the 3-layer architecture, and the A/B testing harness (FR-051–058) is designed to measure the quality improvement they produce.

---

## 3. The Ecosystem Landscape

### 3.1 The AI-Readability Stack

The research established a layered model for how AI agents interact with web documentation. DocStratum spans Layers 3–5, with MCP operating at the transport layer (Layer 0).

```
Layer 5: Agent Instructions      — LLM behavior guidance, few-shot examples       [DocStratum]
Layer 4: Semantic Understanding  — Concept definitions, schema.org mapping         [DocStratum]
Layer 3: Content Curation        — llms.txt curated index                          [DocStratum]
Layer 2: Content Discovery       — sitemap.xml, all pages
Layer 1: Access Control          — robots.txt, ai.txt permissions
Layer 0: Transport & Delivery    — MCP (Anthropic/Linux Foundation), HTTP/HTTPS
```

Stripe is the only known implementation that operates across all three DocStratum layers (3–5), but it does so in unstructured prose rather than machine-parseable structure. DocStratum's goal is to formalize what Stripe demonstrates informally.

### 3.2 Standards Landscape

16 standards were analyzed across the 5-layer taxonomy. The critical relationships:

- **MCP** — Complementary transport layer. llms.txt sections map to MCP Resources. MCP servers already serve llms.txt content. This is the primary integration target.
- **robots.txt (RFC 9309)** — Same discovery pattern (root-level file), different purpose. DocStratum must respect robots.txt disallows.
- **security.txt (RFC 9116)** — Best precedent for standardization pathway (~5 years from proposal to RFC). However, llms.txt faces Google's active opposition, which security.txt did not.
- **ai.txt** — Closest direct competitor, but addresses permissions (who can use content) rather than content delivery (how to present content). Complementary.
- **Context7 (Upstash)** — Overlapping use case for coding assistant documentation. Managed SaaS vs. open static file. Medium competitive risk.
- **Vercel inline** — `<script type="text/llms.txt">` in HTML `<head>` solves staleness by embedding content but loses single-file discoverability. An emerging variant.

### 3.3 Governance Vulnerability

llms.txt has the weakest governance of any standard in its maturity range: single author (Jeremy Howard), no standards body, no RFC process, no official community channels. The specification repository has 555+ GitHub stars and 30+ forks but no formal working group or contribution process.

This is the standard's greatest organizational vulnerability. DocStratum cannot rely on an official spec update to fix governance and quality gaps. The `docstratum-validate` tool must become the *de facto* quality standard through adoption and utility, because the *de jure* standard is stagnant under single-author control.

### 3.4 Community Sentiment

```
Enthusiastic adoption    ~35%    Developer tools, AI companies       "It works for Cursor and Claude"
Cautious observation     ~30%    Enterprise, mid-market               "Interesting but unproven ROI"
Active skepticism        ~25%    SEO community, Google                "No AI system actually uses it"
Hostile/dismissive       ~10%    Standards purists, Hacker News       "Another standard nobody asked for"
```

The community is not neatly divided — it's polarized by *use case*. Those using llms.txt for AI coding assistants (the validated market) are enthusiastic. Those evaluating it for SEO or search LLM visibility (the unvalidated market) are skeptical or hostile. Both groups are correct within their context.

---

## 4. Implementation Archetypes

The v0.0.2 audit identified five distinct approaches to llms.txt implementation. These archetypes provide a classification vocabulary for the ecosystem.

### Archetype 1: The Bare Index (Score: 2–3)

Minimal file serving as a link index with lightweight or no descriptions. Examples: Cursor (20% conformance, 7.5 KB), NVIDIA (minimal visibility, 2/5 score). Works as navigational scaffolding but insufficient for LLM consumption — agents must constantly fetch external links to understand context.

### Archetype 2: The Comprehensive Guide (Score: 4)

Large, single-file documentation with extensive inline content. Examples: Cloudflare (225 KB index + 3.7M-token full file), LangChain (82 KB), Shopify (100–250K estimated). Excellent completeness but size becomes problematic. The effective strategy is per-product decomposition (separate modular files), not monolithic generation.

### Archetype 3: The Tiered System (Score: 4–5)

Multiple files at different detail levels. Examples: Svelte (small/medium/full), Anthropic (llms.txt + llms-full.txt). The highest-scoring archetype. Svelte's dedicated guidance page ("which tier should I use?") is the model best practice.

### Archetype 4: The LLM-Optimized (Score: 5 potential)

Specifically designed for AI agent consumption with explicit LLM affordances. No fully mature examples exist (Stripe excluded from audit), but emerging approximations include Shadcn UI (AI-Ready architecture with `processMdxForLLMs` pipeline), Vercel AI SDK (agent patterns), and PydanticAI (type-driven patterns). Represents the frontier — DocStratum aims to standardize this archetype.

### Archetype 5: The Stub/Broken (Score: 1–2)

Minimal, incomplete, or abandoned implementations. Example: NVIDIA. Even a basic index provides more value than a stub that erodes trust.

### Gold Standard Implementations

| Implementation | Score | Distinguishing Feature |
|----------------|-------|----------------------|
| **Svelte** (Primary) | 5/5, 92/100 composite | Multi-tier variants + dedicated guidance page + performance warnings |
| **Shadcn UI** | 5/5, 89/100 composite | AI-Ready architecture with `processMdxForLLMs` pipeline |
| **Pydantic** | 5/5, 90/100 composite | Concept-first organization; cross-cutting concerns as first-class sections |
| **Vercel AI SDK** | 5/5, 90/100 composite | Full-stack reference architecture; streaming-first; composable |
| **Astro** (Empirical) | 100% conformance | Smallest gold standard at 2.6 KB — micro tier reference |
| **OpenAI** (Empirical) | 100% conformance | Compact reference at 19 KB with perfect spec adherence |
| **Deno** (Empirical) | 100% conformance | Medium-scale reference at 63 KB with perfect spec adherence |

All gold standards share three properties: they organize by concepts rather than alphabetically, they include concrete code examples, and they demonstrate intentional curation. None are the largest files in the sample.

---

## 5. Opportunity Areas

Based on the 8 key findings, DocStratum occupies a unique position in the ecosystem. The following opportunity areas are prioritized by impact and feasibility.

### 5.1 Formal Validation — The Foundation (CRITICAL, Zero Competition)

No tool in the ecosystem provides formal schema validation against a defined grammar. All 6+ existing validators use informal rule checking. DocStratum's Pydantic-based validation pipeline with 5 levels (L0 Parseable → L4 DocStratum Extended) and an error code registry (8 errors, 11 warnings, 7 informational codes) is genuinely unprecedented. The 95-point conformance spread across specimens (5%–100%) proves the need is real.

### 5.2 Semantic Enrichment — The Differentiator (CRITICAL, Zero Competition)

No tool injects concept definitions, few-shot examples, or LLM instructions into llms.txt files. DocStratum's 3-layer architecture (Master Index → Concept Map → Few-Shot Bank) directly addresses three P0 specification gaps that zero implementations have attempted. This is the "moat" — the capability that transforms DocStratum from a validator into a semantic translation layer.

### 5.3 Quality Scoring — The Measurable Value Proposition (HIGH, Zero Competition)

The 100-point composite scoring pipeline (30% structural + 50% content + 20% anti-pattern) provides a quantifiable quality metric for llms.txt files. No existing tool offers anything beyond basic format checking. Gold standard calibration (Svelte 92, NVIDIA 24) demonstrates that the scoring system produces meaningful differentiation. This becomes the basis for a potential certification/badge program.

### 5.4 CI/CD Integration — The Developer Workflow Hook (HIGH, Zero Competition)

No validator provides exit codes, SARIF output, or GitHub Actions integration. For the validated market (developers using AI coding assistants), CI/CD integration makes `docstratum-validate` part of the documentation pipeline — the same way ESLint is part of the code pipeline. This is the adoption vector.

### 5.5 Anti-Pattern Detection — The Quality Safety Net (MEDIUM-HIGH)

22 cataloged anti-patterns with automated detection rules and remediation strategies. The "Preference Trap" (AP-STRAT-004) is an emerging threat: research by Duane Forrester shows carefully crafted llms.txt content makes LLMs 2.5× more likely to recommend targeted content. DocStratum's integrity verification can help mitigate "trust laundering."

### 5.6 Tiered Generation Standardization (MEDIUM)

Only 1 of 75+ tools supports tiered output (4hse/astro). Svelte's gold-standard pattern (small/medium/full) is the model, but no tooling standard exists for token budgets, tier definitions, or variant naming. DocStratum can formalize what gold standards do informally.

---

## 6. Recommendations

### 6.1 Strategic Recommendations

**R1: Target AI coding assistants via MCP exclusively.** The Adoption Paradox (Finding 2) makes the validated market clear: developers using Cursor, Claude Desktop, and Windsurf via MCP. Do not build SEO-adjacent features, sitemap pinging, or crawler hint optimization. Build for IDE context injection, MCP Resource exposure, and CI/CD pipeline validation.

**R2: Position DocStratum as enrichment middleware, not a generator.** The integration architecture accepts llms.txt from any of the 75+ existing generators, validates it, scores it, enriches it, and outputs it to consumers. This avoids the saturated generation market (Finding 6) while filling the governance vacuum.

**R3: Use the "Writer's Edge" philosophy as the marketing narrative.** The finding that curation beats volume (Finding 3) is counterintuitive and memorable. "A Technical Writer with strong Information Architecture skills can outperform a sophisticated RAG pipeline by simply writing better source material" is a compelling thesis that differentiates DocStratum from engineering-heavy approaches.

**R4: Publish the ABNF grammar as a standalone community resource.** No formal grammar exists outside DocStratum's research. Publishing it establishes technical authority and creates a dependency that validators can adopt (Phase 1 of the roadmap, v0.0.3d).

### 6.2 Architectural Recommendations

**R5: Implement the critical path: grammar → validator → enrichment → MCP server.** This is the minimum viable flow that delivers unique value at each stage. Everything else is parallel or downstream.

**R6: Design the parser as "permissive input, strict output."** Accept formatting variations gracefully, return partial results with error annotations, normalize to canonical form. Missing blockquotes get warnings, not errors. Relative URLs get warnings with resolution hints. This is validated by the 55% blockquote compliance reality (Finding 7).

**R7: Enforce token budgets as a first-class constraint, not advisory guidance.** Three tiers: Standard (1.5K–4.5K tokens), Comprehensive (4.5K–12K), Full (12K–50K). Per-section allocations prevent any single section from dominating. Anti-pattern threshold: no file exceeding 100K tokens.

**R8: Implement Document Type Classification early in the pipeline.** The bimodal distribution (Finding 4) means the parser must detect Type 1 vs. Type 2 before applying validation rules. The ~250 KB boundary serves as the classification heuristic threshold.

### 6.3 Implementation Recommendations

**R9: Start with the Schema & Validation module (FR-001–012).** This is where the most research investment has been made (ABNF grammar, gap analysis, validation levels, error code registry), and it has the clearest path from research to code. Pydantic models with 5-level validation deliver immediate value.

**R10: Build the A/B testing harness (FR-051–058) as a first-class module, not an afterthought.** The entire project's thesis — that structured context improves agent output — must be empirically demonstrated. The harness requires ≥20 test queries with statistical significance (p < 0.05) to be convincing as a portfolio piece.

**R11: Keep the demo scenario under 3 minutes.** The v0.0.5d demo script specifies a 2-minute-45-second flow: problem statement → load/parse → side-by-side agents → A/B test results → closing. Every feature must be justified by its contribution to this demo.

**R12: Use the Scope Fence decision tree for every feature idea during implementation.** The 40–60 hour time budget (CONST-006) demands ruthless prioritization. 32 out-of-scope items and 11 deferred features are already documented — the scope boundaries are pre-committed.

---

## 7. Risk Assessment

### 7.1 Execution Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Specification changes break DocStratum's grammar | Medium | High | Grammar is backward-compatible; validation levels allow graceful degradation |
| No adopters for validation tooling | Low-Medium | High | Target developer workflow integration (CI/CD); reduce adoption friction |
| Enrichment pipeline quality insufficient | Medium | High | A/B testing harness provides quantitative feedback; iterate based on data |
| MCP ecosystem shifts away from llms.txt | Low | Medium | Validation/enrichment patterns transfer to any AI-readable format |
| Scope creep into generator building | Medium | Medium | Scope Fence decision tree + 32 pre-committed OOS items |
| 40–60 hour time budget insufficient | Medium | Medium | 32 MUST features precisely defined; SHOULD/COULD only if surplus time |

### 7.2 Market Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Adoption paradox deepens permanently | Medium | High | Focus on validated market (coding assistants); value proposition holds regardless |
| Google launches proprietary alternative | Low | High | Google Vertex AI Grounding already exists; confirms problem is real |
| Context7 (Upstash) captures coding assistant market | Medium | Medium | Context7 is managed SaaS; DocStratum is open-source tooling — different value props |
| llms.txt declared "dead" by community | Low | High | Standard survived "is it dead?" debate wave in mid-2025; developer adoption continues |
| Auto-generated files flood ecosystem with low quality | High | Medium-Low | Actually benefits DocStratum — quality scoring becomes more valuable |
| WAF/CDN blocking prevents tool from fetching llms.txt files | High | Medium | Fetcher must implement robust request headers and retry logic (v0.0.2a finding) |

### 7.3 Honest Limitations

These are things DocStratum cannot solve:

- **Cannot make LLM providers consume llms.txt.** The adoption paradox persists regardless of tool quality. DocStratum optimizes the validated pathway (MCP/coding assistants), not the unvalidated one (search/chat LLMs).
- **Cannot fix the governance gap.** No tool substitutes for institutional standards governance. DocStratum can become a de facto quality standard through utility, but it cannot force a de jure standardization process.
- **Cannot prevent gaming/abuse.** The Preference Trap and trust laundering risks grow as adoption scales. Cross-validation (comparing llms.txt content to actual page content) mitigates but does not eliminate this vector.
- **Statistical caveats.** The 24-site audit and 11-specimen set are diverse but not randomly sampled. Correlation values are approximations. Findings should be treated as strong directional indicators, not precise measurements.

---

## 8. Open Questions

These questions were not answered by the v0.0.x research program and represent areas for future investigation.

### 8.1 Unresolved Technical Questions

1. **How do Type 2 Full documents perform when served via MCP?** The research identified Type 2 as viable only through MCP, but no performance benchmarks exist for serving 1.3 MB–25 MB documents through MCP resource endpoints. Are MCP servers doing subsection extraction, or serving the entire file?

2. **What is the actual token overhead of the 3-layer enrichment?** The research estimates a +4 second latency overhead for the enhanced agent (NFR-004), but this has not been empirically measured. The overhead depends on layer sizes, injection strategy, and LLM provider.

3. **How effective are LLM Instructions at scale?** Stripe's implementation is the only reference point. The finding that LLM Instructions improve agent output is theoretically strong but empirically untested beyond a single case.

### 8.2 Unresolved Strategic Questions

4. **Will any major LLM provider adopt llms.txt for web retrieval within the next 12 months?** OpenAI crawlers have been observed requesting /llms.txt (but OpenAI hasn't confirmed usage). Anthropic requested llms-full.txt support from Mintlify (internal interest). If either confirms usage, the adoption paradox partially resolves and the addressable market expands dramatically.

5. **How will the Vercel inline pattern (`<script type="text/llms.txt">`) evolve?** This variant solves the staleness problem by embedding content in HTML but loses single-file discoverability. If it gains adoption, DocStratum's parser may need to support HTML `<head>` extraction.

6. **What happens when Yoast SEO's llms.txt reaches millions of WordPress sites?** Yoast added built-in generation in June 2025 with access to millions of sites. This could dramatically expand adoption counts while simultaneously flooding the ecosystem with low-quality auto-generated files — increasing the value of quality scoring but also increasing noise.

### 8.3 Suggested Follow-Up Research

- **Performance benchmarking:** Measure actual latency overhead of 3-layer enrichment across different LLM providers and file sizes
- **LLM Instructions A/B testing:** Controlled experiment comparing agent output quality with and without structured instructions across multiple documentation domains
- **MCP consumption analysis:** Instrument an MCP server serving DocStratum-enriched content to measure which layers agents actually request and how often
- **Longitudinal adoption tracking:** Monitor the ~15→105 site trajectory (independent crawl, v0.0.3b) over 6–12 months to detect acceleration, plateau, or decline

---

## 9. Research Phase Completeness

### 9.1 Phase Completion Status

| Phase | Title | Documents | Sub-Parts | Acceptance Criteria | Status |
|-------|-------|-----------|-----------|---------------------|--------|
| v0.0.1 | Specification Deep Dive | 6 | 4 (a–d) | 35/35 (25 original + 10 enrichment) | COMPLETE |
| v0.0.2 | Wild Examples Audit | 6 | 4 (a–d) | 28/28 + enrichment | COMPLETE |
| v0.0.3 | Ecosystem & Tooling Survey | 6 | 4 (a–d) | 55/64 (9 Nice deferred) | COMPLETE |
| v0.0.4 | Best Practices Synthesis | 5 | 4 (a–d) | All phase + sub-part criteria | COMPLETE |
| v0.0.5 | Requirements Definition | 6 | 4 (a–d) | 52/52 | COMPLETE |
| **[v0.0.7]** v0.0.6 | Platinum Standard Definition | 1 | — | Standalone spec | COMPLETE |
| **[v0.0.7]** v0.0.7 | Ecosystem Pivot Specification | 1 | — | Standalone spec | COMPLETE |
| **Total** | — | **31 [v0.0.7: was 29]** | **20** | — | **ALL COMPLETE** |

### 9.2 Deliverables Inventory

**Specification Artifacts:**
- Formal ABNF grammar for llms.txt (v0.0.1a)
- Error code registry: 8 errors, 11 warnings, 7 informational codes (v0.0.1a, enriched)
- 28 edge cases across 4 categories (v0.0.1a)
- 8 specification gaps with P0/P1/P2 classification (v0.0.1b)
- 4 processing methods with 9-dimension tradeoff matrix (v0.0.1c)
- AI-Readability Stack model with 6 layers (v0.0.1d, enriched)

**Ecosystem Artifacts:**
- 24-source catalog with standardized audit forms (v0.0.2a/b)
- 5 implementation archetypes (v0.0.2c)
- Quality predictor correlation data (v0.0.2c)
- 7 gold standard implementations (v0.0.2d, enriched)
- 11 canonical section names with frequency data (v0.0.2c)
- 75+ tool catalog with 5 feature comparison matrices (v0.0.3a)
- 30 verified key players (v0.0.3b)
- 16 standards comparison across 5 layers (v0.0.3c)
- 25 consolidated ecosystem gaps (v0.0.3d)
- 3-phase prioritized roadmap (v0.0.3d)

**Best Practices Artifacts:**
- 20 structural validation checks (v0.0.4a)
- 15 content quality checks with 100-point rubric (v0.0.4b)
- 22 anti-patterns with detection rules and remediation (v0.0.4c)
- 16 formal design decisions with full rationale (v0.0.4d)
- MUST/SHOULD/COULD best practices framework (v0.0.4 consolidated)
- Token budget architecture with 3 tiers (v0.0.4a)
- 6 technical innovations (v0.0.4d)

**Requirements Artifacts:**
- 85 functional requirements with MoSCoW priority and acceptance tests (v0.0.5a) **[v0.0.7: was 68]**
- 25 non-functional requirements with measurable targets (v0.0.5b) **[v0.0.7: was 21]**
- 6 hard constraints (v0.0.5b)
- 9 trade-off resolutions (v0.0.5b)
- 40 out-of-scope items with justifications (v0.0.5c) **[v0.0.7: was 32]**
- Scope Fence decision tree + 5-step scope change process (v0.0.5c)
- 14 deferred features registry (v0.0.5c) **[v0.0.7: was 11]**
- 45 MVP features with acceptance tests (v0.0.5d) **[v0.0.7: was 32]**
- 5 test scenarios with executable pseudocode (v0.0.5d) **[v0.0.7: was 4]**
- Definition of Done: 36+ checks across 6 dimensions (v0.0.5d) **[v0.0.7: expanded with ecosystem items]**
- 2-minute demo scenario script (v0.0.5d)

**[v0.0.7] Ecosystem & Quality Standard Artifacts:**
- 30-criterion, 5-level Platinum Standard quality framework (v0.0.6)
- 3-layer ecosystem model: Navigation, Content, Aggregate (v0.0.7)
- 6 new schema entities: DocumentEcosystem, EcosystemFile, FileRelationship, EcosystemScore, EcosystemHealthDimension, LinkRelationship (v0.0.7)
- 12 new diagnostic codes (E009–E010, W012–W018, I008–I010) bringing total to 38 (v0.0.7)
- 6 new ecosystem anti-patterns (AP_ECO_001–006) bringing total to 28 (v0.0.7)
- 5-stage ecosystem pipeline architecture (v0.0.7)
- 4-phase migration plan from single-file to ecosystem (v0.0.7)
- Backward compatibility specification: single-file byte-identical output (v0.0.7)

### 9.3 Forward Traceability: Research → Implementation

| Research Artifact | Implementation Target | Version |
|-------------------|----------------------|---------|
| ABNF grammar (v0.0.1a) | Parser/Loader module | v0.3.x |
| Schema extensions (v0.0.1b) | Pydantic models | v0.1.x |
| Hybrid pipeline (v0.0.1c) | Context Builder | v0.4.x |
| Error code registry (v0.0.1a) | Logging + diagnostics | v0.2.x |
| Validation levels L0–L4 (v0.0.1b/v0.0.4a) | Validation pipeline | v0.2.x |
| 57 automated checks (v0.0.4) | `docstratum-validate` | v0.2.x |
| 22 anti-patterns (v0.0.4c) | `docstratum-lint` | v0.2.x |
| 100-point scoring (v0.0.4b) | `docstratum-score` | v0.2.x |
| Token budget tiers (v0.0.4a) | Generator output constraints | v0.4.x |
| 3-layer architecture (v0.0.4d) | Content Structure module | v0.3.x/v0.4.x |
| A/B test scenarios (v0.0.5d) | Integration test suite | v0.5.x |
| Demo script (v0.0.5d) | Streamlit UI | v0.6.0 |
| **[v0.0.7]** Platinum Standard (v0.0.6) | Validation criteria reference | v0.2.x |
| **[v0.0.7]** Ecosystem schema entities (v0.0.7) | Ecosystem Pydantic models | v0.1.2 |
| **[v0.0.7]** Ecosystem pipeline (v0.0.7) | EcosystemPipeline orchestrator | v0.2.7 |
| **[v0.0.7]** Ecosystem scoring (v0.0.7) | EcosystemScorer | v0.2.8 |
| **[v0.0.7]** 12 new diagnostic codes (v0.0.7) | Diagnostics enum expansion | v0.2.7 |
| **[v0.0.7]** Backward compatibility spec (v0.0.7) | Regression test suite | v0.2.7 |

---

## 10. Summary: The One-Paragraph Thesis

The llms.txt specification defines a workable but incomplete file format for making documentation AI-readable. Its ecosystem is growing rapidly (75+ tools, 1,000–5,000 substantive implementations) but is built on a fragile foundation: zero formal validation, zero semantic enrichment, zero quality scoring, and a governance structure consisting of a single author with no standards body. The critical strategic reality is the Adoption Paradox — grassroots adoption is real, but no major search/chat LLM provider has confirmed using these files. The only validated consumption pathway is AI coding assistants (Cursor, Claude Desktop, Windsurf) via MCP. DocStratum fills this vacuum as an enrichment and governance layer that transforms llms.txt from a structural page index into a semantically enriched documentation layer, targeting the validated developer tooling market. Its defensibility rests on capabilities that zero other tools provide: formal validation against a defined grammar, semantic enrichment (concept definitions, few-shot examples, LLM instructions), multi-dimension quality scoring, and CI/CD-native integration. The core thesis, validated by the research: 8K tokens of curated concepts and examples outperform 200K tokens of raw page dumps. Structure is a feature.

---

## Source Documents

### Phase Summaries (Primary References)

- [v0.0.1 Summary — Specification Deep Dive](RR-SPEC-v0.0.1-summary.md)
- [v0.0.2 Summary — Wild Examples Audit](RR-SPEC-v0.0.2-summary.md)
- [v0.0.3 Summary — Ecosystem & Tooling Survey](RR-SPEC-v0.0.3-summary.md)
- [v0.0.4 Summary — Best Practices Synthesis](RR-SPEC-v0.0.4-summary.md)
- [v0.0.5 Summary — Requirements Definition](RR-SPEC-v0.0.5-summary.md)

### Sub-Part Documents (Detailed References)

**v0.0.1 — Specification Deep Dive:**
- [v0.0.1a — Formal Grammar & Parsing Rules](RR-SPEC-v0.0.1a-formal-grammar-and-parsing-rules.md)
- [v0.0.1b — Spec Gap Analysis & Implications](RR-SPEC-v0.0.1b-spec-gap-analysis-and-implications.md)
- [v0.0.1c — Processing & Expansion Methods](RR-SPEC-v0.0.1c-processing-and-expansion-methods.md)
- [v0.0.1d — Standards Interplay & Positioning](RR-SPEC-v0.0.1d-standards-interplay-and-positioning.md)

**v0.0.2 — Wild Examples Audit:**
- [v0.0.2a — Source Discovery & Collection](RR-SPEC-v0.0.2a-source-discovery-and-collection.md)
- [v0.0.2b — Individual Example Audits](RR-SPEC-v0.0.2b-individual-example-audits.md)
- [v0.0.2c — Pattern Analysis & Statistics](RR-SPEC-v0.0.2c-pattern-analysis-and-statistics.md)
- [v0.0.2d — Synthesis & Recommendations](RR-SPEC-v0.0.2d-synthesis-and-recommendations.md)

**v0.0.3 — Ecosystem & Tooling Survey:**
- [v0.0.3a — Tools & Libraries Inventory](RR-SPEC-v0.0.3a-tools-and-libraries-inventory.md)
- [v0.0.3b — Key Players & Community Pulse](RR-SPEC-v0.0.3b-key-players-and-community-pulse.md)
- [v0.0.3c — Related Standards & Competing Approaches](RR-SPEC-v0.0.3c-related-standards-and-competing-approaches.md)
- [v0.0.3d — Gap Analysis & Opportunity Map](RR-SPEC-v0.0.3d-gap-analysis-and-opportunity-map.md)

**v0.0.4 — Best Practices Synthesis:**
- [v0.0.4a — Structural Best Practices](RR-SPEC-v0.0.4a-structural-best-practices.md)
- [v0.0.4b — Content Best Practices](RR-SPEC-v0.0.4b-content-best-practices.md)
- [v0.0.4c — Anti-Patterns Catalog](RR-SPEC-v0.0.4c-anti-patterns-catalog.md)
- [v0.0.4d — Differentiators & Decision Log](RR-SPEC-v0.0.4d-rosetta-root-differentiators-and-decision-log.md)

**v0.0.5 — Requirements Definition:**
- [v0.0.5a — Functional Requirements Specification](RR-SPEC-v0.0.5a-functional-requirements-specification.md)
- [v0.0.5b — Non-Functional Requirements & Constraints](RR-SPEC-v0.0.5b-non-functional-requirements-and-constraints.md)
- [v0.0.5c — Scope Definition & Out-of-Scope Registry](RR-SPEC-v0.0.5c-scope-definition-and-out-of-scope-registry.md)
- [v0.0.5d — Success Criteria & MVP Definition](RR-SPEC-v0.0.5d-success-criteria-and-mvp-definition.md)

**[v0.0.7] Ecosystem & Quality Standard Specifications:**
- [v0.0.6 — Platinum Standard Definition](RR-SPEC-v0.0.6-platinum-standard-definition.md)
- [v0.0.7 — Ecosystem Pivot Specification](RR-SPEC-v0.0.7-ecosystem-pivot-specification.md)

### Supporting Documents

- [v0.0.0 — Research & Discovery](RR-SPEC-v0.0.0-research-and-discovery.md) — Phase overview and original 16 research questions
- [v0.0.0 — Stripe LLM Instructions Pattern](RR-SPEC-v0.0.0-stripe-llm-instructions-pattern.md) — Early analysis of the Stripe reference implementation
- [v0.0.0 — Wild Examples Analysis](RR-SPEC-v0.0.0-wild-examples-analysis.md) — Initial ecosystem observations
- [01-research/README.md](README.md) — Research directory index
