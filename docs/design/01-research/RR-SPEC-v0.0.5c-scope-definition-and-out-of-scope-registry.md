# v0.0.5c — Scope Definition & Out-of-Scope Registry

> **Sub-Part:** Define rigid scope boundaries, catalog out-of-scope items with detailed justifications, provide a "Scope Fence" decision tree for evaluating new ideas, and establish scope change management process.

---

> **REVISION NOTICE — v0.0.7 Ecosystem Pivot (2026-02-07)**
>
> This document was revised following the strategic pivot defined in `RR-SPEC-v0.0.7-ecosystem-pivot-specification.md`. DocStratum's scope expanded from **single-file llms.txt validator** to **ecosystem-level documentation quality platform**. Changes are marked with `[v0.0.7]` tags for traceability. The original scope boundaries (v0.6.0 MVP as single-file validator) remain valid as the *foundation* — the ecosystem layer is additive, not a replacement. The scope change was processed through the Part 5 Scope Change Management Process; see Part 14 (Scope Change Log) for the formal record.
>
> **Impact summary:** 3 sections revised (Parts 1, 2, 4), 1 section added (Part 14), 1 OOS item reclassified (OOS-G4 partial), 8 new OOS items added (Category H), 3 deferred features added. Total OOS count: 32 → 40.

---

## Sub-Part Overview

This sub-part complements v0.0.5a (Functional Requirements) and v0.0.5b (Non-Functional Requirements & Constraints) by drawing a hard perimeter around the v0.6.0 MVP — defining not only what DocStratum IS, but rigorously cataloging what it IS NOT and providing operational tooling to keep it that way during implementation. Drawing on scope risks surfaced across all four research phases — v0.0.1 (specification gaps inviting feature creep), v0.0.2 (wild variation suggesting unbounded scope), v0.0.3 (75+ ecosystem tools tempting integration sprawl), and v0.0.4 (best practices creating "nice-to-have" gravity) — this document establishes a formal scope defense system comprising 32 out-of-scope items (OOS-A1 through OOS-G5) across 7 exclusion categories, a "Scope Fence" decision tree for real-time feature evaluation, a deferred features registry preserving 11 valuable post-MVP ideas, a 5-step scope change management process, 7 explicit exclusion statements with rationale, and 5 health metrics for ongoing scope monitoring.

**Distribution:** 3 commercial/production exclusions (Category A), 5 full-platform exclusions (Category B), 5 ecosystem integration exclusions (Category C), 5 advanced ML/AI exclusions (Category D), 5 deployment/infrastructure exclusions (Category E), 4 historical/legacy exclusions (Category F), and 5 nice-to-have exclusions (Category G). All 32 items include: what the feature is, why it's excluded, when it becomes feasible, and what would need to change. The deferred features registry captures 11 items with estimated effort (4–30 hours each) and target versions (v1.5+ through v2.0+).

**Relationship to v0.0.5a and v0.0.5b:** Every OOS item was evaluated against the 68 functional requirements from v0.0.5a to confirm it does not overlap with any MUST or SHOULD requirement. The 6 hard constraints from v0.0.5b (CONST-001 through CONST-006) directly inform the exclusion rationale — particularly CONST-001 (solo developer), CONST-002 (portfolio scope), CONST-005 (v0.6.0 target), and CONST-006 (40–60 hour budget). The Scope Fence decision tree references FR IDs and MoSCoW priorities from v0.0.5a as its first evaluation filters.

## Objective

Scope creep is a primary risk on constrained projects (solo developer, 40–60 hour budget, portfolio-focused). This sub-part establishes clear, defensible scope boundaries and provides a structured process for evaluating new ideas. By the end, everyone understands what IS DocStratum and what IS NOT, and why.

### Success Looks Like

- Crystal-clear in-scope boundary statement (what DocStratum is)
- 15+ out-of-scope items with detailed justifications (what DocStratum is not)
- "Scope Fence" decision tree (flowchart for evaluating new features)
- Deferred features registry (valuable ideas for future versions)
- Scope change management process (how to handle new requests)
- All team members (you) agree on these boundaries
- Zero scope creep during implementation

---

## Scope Boundaries

### In Scope

- Defining the explicit in-scope boundary statement for DocStratum v0.6.0 MVP
- Cataloging out-of-scope items with detailed justifications across multiple categories
- Providing the "Scope Fence" decision tree for evaluating new feature ideas during implementation
- Building a deferred features registry for valuable post-MVP ideas
- Establishing a scope change management process to prevent ad-hoc scope expansion
- Defining explicit exclusion statements (what DocStratum is NOT)
- Providing scope health metrics for monitoring during v0.1–v0.6 implementation
- Mapping OOS items back to functional requirements (v0.0.5a) and constraints (v0.0.5b) for traceability

### Out of Scope

- Functional behavior definitions (that's v0.0.5a)
- Non-functional quality targets and constraints (that's v0.0.5b)
- Success metrics, test scenarios, or MVP pass/fail criteria (that's v0.0.5d)
- Implementation details, code design, or API signatures
- Detailed cost/benefit analysis for deferred features (those are post-MVP planning concerns)
- Third-party platform evaluations or technology selection (fixed tech stack per CONST-003)

---

## Dependencies

```
v0.0.1–4 — Research Phase (COMPLETED)
    ├── v0.0.1: Specification gaps → features that could tempt scope creep
    ├── v0.0.2: Wild variation → unbounded implementation possibilities
    ├── v0.0.3: 75+ tools → integration sprawl risk
    └── v0.0.4: Best practices → "nice-to-have" gravity pull

v0.0.5a — Functional Requirements (COMPLETED)
    ├── 68 FRs define what IS in scope (FR-001 through FR-068)
    ├── MoSCoW priorities separate MUST from SHOULD/COULD
    └── 7 module boundaries constrain implementation surface

v0.0.5b — Non-Functional Requirements & Constraints (COMPLETED)
    ├── 6 hard constraints (CONST-001–006) define immovable boundaries
    ├── 21 NFRs with measurable targets constrain feasibility
    └── Trade-off resolutions inform scope vs. timeline decisions

                            v
v0.0.5c — Scope Definition & Out-of-Scope Registry (THIS TASK)
                            │
                            v
v0.0.5d — Success Criteria & MVP Definition
    ├── Uses scope boundaries to define pass/fail criteria
    ├── Uses deferred features to define stretch goals
    └── Uses Scope Fence to evaluate late-breaking requirements
                            │
        ┌───────────────────┼───────────────────┐
        v                   v                   v
    v0.1.0            v0.2.0              v0.3.0–v0.6.0
  (Foundation)      (Data Prep)        (Implementation)
  Scope Fence       Scope Fence         Scope Fence
  active during     active during       active during
  all phases        all phases          all phases
```

---

## Part 1: Explicit In-Scope Statement

### What DocStratum IS

**DocStratum is a research project and toolkit that:**

1. **Audits and formalizes** the existing `llms.txt` ecosystem (v0.0.1–4)
2. **Designs** an extended schema and validation framework for enhanced llms.txt (v0.0.5–1.x)
3. **Implements** reference tools:
   - Pydantic schema + validation pipeline
   - Formal grammar and parser
   - 3-layer context builder (Master Index, Concept Map, Few-Shot Bank)
   - A/B testing harness for agent performance evaluation
4. **[v0.0.7] Validates documentation ecosystems** — not just individual files, but the relationships between `llms.txt`, `llms-full.txt`, individual content pages, and instruction files:
   - Ecosystem discovery (scan a project for all AI-facing documentation)
   - Cross-file relationship mapping and link resolution
   - Ecosystem-level health scoring across 5 dimensions (Coverage, Consistency, Completeness, Token Efficiency, Freshness)
5. **Demonstrates** improved AI agent performance via:
   - Baseline agent (raw llms.txt)
   - Enhanced agent (DocStratum context)
   - Side-by-side comparison in Streamlit UI
6. **Publishes** everything (code, spec, findings) for community use

### Project Boundaries (v0.6.0 MVP — Revised v0.0.7)

**By release v0.6.0, the following WILL be complete:**

- ✅ Formal specification for extended llms.txt schema
- ✅ Validation pipeline (levels 0–4) with error reporting
- ✅ Parser/loader module for standard + extended llms.txt
- ✅ 3-layer context builder with token budgeting
- ✅ Baseline + enhanced agent comparison
- ✅ Streamlit demo with side-by-side view and metrics
- ✅ 20+ passing A/B test queries with statistical significance
- ✅ Comprehensive documentation (README, API docs, design docs)
- ✅ Clean, well-tested code (≥ 80% coverage on core modules)
- ✅ **[v0.0.7]** Ecosystem-aware schema (models for `DocumentEcosystem`, `EcosystemFile`, `FileRelationship`, `EcosystemScore`)
- ✅ **[v0.0.7]** Ecosystem discovery (scan project directory for `llms.txt`, `llms-full.txt`, linked `.md` content pages)
- ✅ **[v0.0.7]** Cross-file link resolution (verify that links in `llms.txt` resolve to actual content within the ecosystem)
- ✅ **[v0.0.7]** Ecosystem health score (at minimum: Completeness and Coverage dimensions)
- ✅ **[v0.0.7]** 38 diagnostic codes (26 per-file + 12 ecosystem-level) and 28 anti-patterns (22 per-file + 6 ecosystem)

**[v0.0.7] Note on scope expansion:** The ecosystem features represent an additive layer on top of the single-file validator, not a replacement. The single-file pipeline (L0–L4 validation, 100-point quality score, 26 diagnostic codes) is preserved in full. A user who provides only a single `llms.txt` file receives identical output to the pre-pivot design. The ecosystem features activate when a project directory or multi-file input is provided. This additive property is a hard requirement — see v0.0.7 Section 7.2 (Backward Compatibility).

### Technology Stack (Fixed)

- **Python 3.9+**
- **Pydantic** for schema validation
- **LangChain** for agent framework
- **Anthropic API** (Claude) + OpenAI API (GPT) for LLM calls
- **Streamlit** for web demo
- **pytest** for testing
- **Black + Ruff** for code quality

---

## Part 2: Out-of-Scope Registry

### Exclusion Categories

```
Category A: Commercial/Production (This is a portfolio project)
Category B: Full-Featured Platforms (Too large; out of scope)
Category C: Ecosystem Integration (Too many platforms; focus on proof-of-concept)
Category D: Advanced ML/AI (Beyond project goals)
Category E: Deployment & Infrastructure (Beyond portfolio scope)
Category F: Historical/Legacy Support (Focus on current standards)
Category G: Nice-to-Have Features (Deferred for timeline reasons)
Category H: Ecosystem Scope Boundaries [v0.0.7] (Ecosystem features beyond MVP)
```

---

## Out-of-Scope Items with Detailed Justifications

### **Category A: Commercial Products & Services**

| # | Feature | What It Is | Why Out of Scope | When Feasible | What Would Change |
|---|---|---|---|---|---|
| **OOS-A1** | **SaaS/Hosted Platform** | Cloud service hosting llms.txt files with web UI | Portfolio project; SaaS requires deployment infra, payment handling, user mgmt, 24/7 support | Post-v1.0 if community adopts project | Would need: cloud deployment (AWS/GCP), user auth, payment processing, SLA monitoring |
| **OOS-A2** | **Commercial Licensing** | Per-license pricing model for enterprise llms.txt generation | Not a product; free/open-source focus | Post-v1.0 if venture-backed | Would need: legal structure, sales infrastructure, customer support |
| **OOS-A3** | **Premium Tiers** | Freemium model with paid features (advanced context, priority support) | Portfolio project doesn't need monetization | Post-v1.0 with business model | Would need: payment infrastructure, feature gating, metrics tracking |

### **Category B: Full-Featured Platforms & Replacements**

| # | Feature | What It Is | Why Out of Scope | When Feasible | What Would Change |
|---|---|---|---|---|---|
| **OOS-B1** | **Web-Based Editor** | Full IDE for creating/editing llms.txt with live preview | Out of scope for this version; demo is read-only Streamlit app | v1.5+ if strong demand | Would need: JavaScript frontend, real-time collaboration, conflict resolution |
| **OOS-B2** | **Real-Time Sync** | Auto-sync llms.txt with source documentation (GitHub, Confluence, Notion) | Too many platforms; sync is complex (merge strategies, versioning) | v1.5+ with plugin architecture | Would need: platform-specific connectors, version control, conflict resolution |
| **OOS-B3** | **Documentation Auto-Generation** | Parse docs and auto-generate llms.txt | Requires domain-specific knowledge; can't be generic | v1.5+ with AI-driven generation | Would need: fine-tuned LLM, human review workflow, quality metrics |
| **OOS-B4** | **Full RAG Pipeline** | Vector DB + embedding service + retrieval | Out of scope; DocStratum provides structured context, not full RAG | v1.5+ as RAG integration guide | Would need: vector DB (Pinecone, Milvus), embedding model, retrieval service |
| **OOS-B5** | **GraphQL API** | API for querying llms.txt structure | Out of scope; REST/CLI are sufficient for demo | v1.5+ with production deployment | Would need: API design, GraphQL schema, caching, rate limiting |

### **Category C: Ecosystem Integration**

| # | Feature | What It Is | Why Out of Scope | When Feasible | What Would Change |
|---|---|---|---|---|---|
| **OOS-C1** | **Integration: Stripe Docs** | Special handling for Stripe's llms.txt specifically | Wrong approach; generalize parser instead | Never; instead generalize to all docs | Apply lessons from Stripe to generic validation |
| **OOS-C2** | **Integration: Confluence Plugin** | Confluence plugin to generate llms.txt | Too many platforms; integration requires platform expertise | v1.5+ with plugin architecture | Would need: platform SDK integration, plugin distribution |
| **OOS-C3** | **Integration: VS Code Extension** | VS Code extension for editing llms.txt with validation | Out of scope for core project; focus on Python library | v1.5+ with extension | Would need: TypeScript, VS Code API, marketplace submission |
| **OOS-C4** | **Integration: GitHub App** | GitHub app that validates PRs modifying llms.txt | Out of scope; focus on validation library, not CI/CD integration | v1.5+ with GitHub Actions example | Would need: GitHub API, webhook handling, app registration |
| **OOS-C5** | **Integration: Slack Bot** | Slack bot for querying llms.txt context | Out of scope; Streamlit demo is sufficient | v1.5+ if strong demand | Would need: Slack API, bot registration, message handling |

### **Category D: Advanced ML & AI Features**

| # | Feature | What It Is | Why Out of Scope | When Feasible | What Would Change |
|---|---|---|---|---|---|
| **OOS-D1** | **Embeddings & Semantic Search** | Use embeddings (OpenAI, Hugging Face) for semantic context matching | Nice-to-have but not essential; keyword search sufficient for MVP | v1.5+ with vector store | Would need: embedding API, vector DB, semantic similarity metrics |
| **OOS-D2** | **Fine-Tuned LLM** | Fine-tune custom model specifically for llms.txt understanding | Out of scope; use base models (GPT-4, Claude) | Post-v2.0 with sufficient training data | Would need: labeled dataset, compute budget, fine-tuning pipeline |
| **OOS-D3** | **Multi-Modal Content** | Support images, diagrams, video in llms.txt context | Out of scope; focus on text-based llms.txt | v2.0+ with media handling | Would need: media parsing, storage, serialization |
| **OOS-D4** | **Reinforcement Learning from Feedback** | Learn from user feedback to improve context selection | Out of scope; requires ongoing training loop | v2.0+ with user feedback infrastructure | Would need: feedback collection, retraining pipeline, model versioning |
| **OOS-D5** | **Language Model as Validator** | Use LLM to validate llms.txt quality instead of rules | Interesting but out of scope; rule-based validation is deterministic | v1.5+ with LLM judge module | Would need: LLM judge, fine-tuning, human evaluation datasets |

### **Category E: Deployment & Infrastructure**

| # | Feature | What It Is | Why Out of Scope | When Feasible | What Would Change |
|---|---|---|---|---|---|
| **OOS-E1** | **Docker Deployment** | Containerized DocStratum for easy deployment | Out of scope for portfolio; Dockerfile can be added later | v1.5+ for production use | Would need: Dockerfile, docker-compose, registry setup |
| **OOS-E2** | **Kubernetes Config** | K8s manifests for production deployment | Out of scope; portfolio doesn't need orchestration | v2.0+ for enterprise deployment | Would need: K8s expertise, service manifests, ingress config |
| **OOS-E3** | **Monitoring & Logging** | Production monitoring (Datadog, New Relic, CloudWatch) | Out of scope; local development doesn't need external monitoring | v1.5+ for production | Would need: monitoring SDK, log aggregation, alerting |
| **OOS-E4** | **Scalability: Horizontal Scaling** | Support multiple instances with load balancing | Out of scope for portfolio; single instance sufficient | v2.0+ for production traffic | Would need: load balancer, distributed caching, database |
| **OOS-E5** | **Backup & Disaster Recovery** | Automated backups, failover, recovery procedures | Out of scope; portfolio doesn't require SLA | v2.0+ for production | Would need: backup service, geographic redundancy, RTO/RPO planning |

### **Category F: Historical & Legacy Support**

| # | Feature | What It Is | Why Out of Scope | When Feasible | What Would Change |
|---|---|---|---|---|---|
| **OOS-F1** | **Python 3.7 Support** | Maintain backward compatibility with Python 3.7 | Python 3.7 EOL (June 2023); support modern versions | Never; 3.7 is EOL | No change; just focus on current versions |
| **OOS-F2** | **Support Old llms.txt Versions** | Handle outdated spec versions (if they existed) | Official spec is stable; no versioning needed | If spec evolves (v1.1, v1.2, etc.) | Would need: version detection, migration logic |
| **OOS-F3** | **Legacy LLM Models** | Support deprecated models (GPT-2, GPT-3, etc.) | Use latest stable models (GPT-4, Claude 3) | If old models are still used | Would need: fallback model logic, performance testing |
| **OOS-F4** | **Support Windows-Specific Issues** | Special handling for Windows-specific bugs (path separators, encoding) | Use cross-platform libraries (pathlib, UTF-8); general Windows support included | If strong Windows user base | Would need: Windows VM testing, special case handling |

### **Category G: Nice-to-Have Features**

| # | Feature | What It Is | Why Out of Scope | When Feasible | What Would Change |
|---|---|---|---|---|---|
| **OOS-G1** | **Neo4j Graph Visualization** | Interactive graph DB visualization of concept relationships | Out of scope; Streamlit charts sufficient for MVP | v1.5+ if graph visualization is critical | Would need: Neo4j server, D3.js/Cytoscape frontend |
| **OOS-G2** | **Multi-Language Documentation** | Support llms.txt files for Chinese, Spanish, Japanese docs | Out of scope; focus on English-language ecosystem | v2.0+ with i18n infrastructure | Would need: translation support, encoding handling |
| **OOS-G3** | **Analytics Dashboard** | Web dashboard tracking which concepts/examples are used | Out of scope; portfolio demo doesn't need usage analytics | v1.5+ with usage tracking | Would need: analytics DB, frontend dashboard, privacy handling |
| **OOS-G4** | **Batch Processing UI** | Web UI for batch-processing multiple llms.txt files | Out of scope; CLI sufficient for batch operations | v1.5+ with web UX | Would need: job queue, background processing, result storage |
| **OOS-G5** | **Mobile App** | iOS/Android app for accessing llms.txt on mobile | Out of scope; web demo is sufficient | v2.0+ if mobile access is critical | Would need: React Native or native development |

### **[v0.0.7] Category H: Ecosystem Scope Boundaries**

> These items define the outer boundary of the ecosystem pivot. They represent ecosystem features that are valuable but exceed the v0.6.0 MVP budget. The ecosystem features that ARE in scope (discovery, link resolution, basic health scoring) are defined in Part 1 above.

| # | Feature | What It Is | Why Out of Scope | When Feasible | What Would Change |
|---|---|---|---|---|---|
| **OOS-H1** | **Full 5-Dimension Ecosystem Scoring** | All 5 ecosystem health dimensions (Coverage, Consistency, Completeness, Token Efficiency, Freshness) fully implemented with calibrated weights | MVP includes 2 dimensions (Completeness, Coverage); remaining 3 require cross-file content analysis that exceeds time budget | v0.7.0 with ecosystem pipeline complete | Would need: content similarity analysis, version metadata extraction, token distribution calculator |
| **OOS-H2** | **Content Page Validation Rules** | Dedicated validation rule set for individual `.md` content pages (self-containment checks, topic focus, cross-reference integrity) | MVP validates content pages through cross-file link resolution; dedicated rules require per-page NLP analysis | v0.7.0 with content page validator | Would need: per-page parser, self-containment heuristics, topic coherence metrics |
| **OOS-H3** | **Instruction File Validation** | Dedicated validation for `llms-instructions.txt` files (DO/DON'T pattern detection, behavioral guidance quality checks) | MVP detects instruction sections within llms.txt (I001); standalone instruction files require new parser rules | v0.7.0 with instruction validator | Would need: instruction pattern parser, behavioral guidance quality metrics |
| **OOS-H4** | **URL Crawl-Based Discovery** | Discover ecosystem files by crawling from a URL (starting at `https://domain.com/llms.txt` and following links) | MVP uses local directory scanning only; URL crawling requires HTTP client, rate limiting, redirect handling | v0.8.0 with web crawling module | Would need: async HTTP client, rate limiter, redirect resolver, robots.txt respect |
| **OOS-H5** | **Context Compression Scoring** | Calculate a token-efficiency ratio measuring information density per token across the ecosystem | Novel metric with no precedent; requires calibration against ground truth | v1.0+ with compression research | Would need: information-theoretic analysis, ground truth dataset, calibration pipeline |
| **OOS-H6** | **Ecosystem Report Generation** | Produce a Markdown or HTML report visualizing the ecosystem graph, per-file scores, and remediation recommendations | Valuable but presentation-layer concern; CLI output sufficient for MVP | v0.8.0 with reporting module | Would need: graph visualization, HTML template, report renderer |
| **OOS-H7** | **Monorepo Sub-Ecosystem Support** | Handle monorepos with multiple independent `llms.txt` files as separate sub-ecosystems within one scan | MVP treats each `llms.txt` as a separate ecosystem root; sub-ecosystem relationships require graph modeling | v1.0+ with monorepo support | Would need: project boundary detection, sub-ecosystem linking, aggregate scoring across sub-ecosystems |
| **OOS-H8** | **Ecosystem Manifest File** | Accept a `docstratum.json` or `llms-manifest.json` file listing all ecosystem members explicitly, rather than relying on discovery | MVP discovers files automatically; manifest files require spec authoring and community adoption | v1.0+ if community requests it | Would need: manifest schema definition, parser, validation against discovered files |

---

## Part 3: Scope Fence — Decision Tree

### Evaluating New Feature Requests

When a new feature idea arises during implementation, use this decision tree to determine if it's in scope:

```
New Feature Idea Requested
    │
    ├─→ Is it listed in the Out-of-Scope Registry (OOS-A1 through OOS-G5)?
    │   ├─ YES → DECISION: Out of scope (explain category)
    │   └─ NO → Continue to next check
    │
    ├─→ Does it directly support one of the 7 main modules (v0.0.5a FR-001 through FR-065)?
    │   ├─ YES → DECISION: Likely in scope (assess priority: MUST/SHOULD/COULD)
    │   └─ NO → Continue to next check
    │
    ├─→ Does it enable the core demo or A/B testing?
    │   ├─ YES → DECISION: In scope if fits timeline
    │   └─ NO → Continue to next check
    │
    ├─→ Is it a "COULD have" per MoSCoW (nice-to-have)?
    │   ├─ YES → Only if time budget remaining > 5 hours
    │   └─ NO → Continue to next check
    │
    ├─→ Is it research-driven (justified by v0.0.1–4 findings)?
    │   ├─ YES → DECISION: Assess effort; consider deferring if > 4 hours
    │   └─ NO → Continue to next check
    │
    └─→ DEFAULT → DECISION: Out of scope; defer to post-v0.6.0 list
```

### Examples of Applying the Scope Fence

#### Example 1: Neo4j Graph Visualization

```
Question: "Should we add an interactive Neo4j graph visualization?"

Decision Tree:
├─ In OOS registry? YES → OOS-G1 (Neo4j Graph Visualization)
├─ Supports main module? NO (not in v0.0.5a requirements)
├─ Enables demo? Partially (nice visual, but not essential)
├─ COULD have? YES (NFR-062 is COULD)
├─ Research-driven? Not directly (v0.0.1c mentions concepts, but not visualization)
├─ Effort estimate? 6–8 hours for proper D3.js setup
│
└─ DECISION: Out of scope for v0.6.0
   Rationale: Defer to v1.5+ when graph visualization is critical feature
   Alternative: Use Streamlit st.graphviz_chart() for minimal graph view if time permits
```

#### Example 2: Confluence Plugin

```
Question: "Can we build a Confluence plugin to auto-generate llms.txt?"

Decision Tree:
├─ In OOS registry? YES → OOS-C2 (Integration: Confluence Plugin)
├─ Supports main module? NO (scope is platform-agnostic)
├─ Enables demo? NO
├─ COULD have? NO (not even listed as COULD)
├─ Research-driven? NO (research didn't focus on Confluence)
│
└─ DECISION: Out of scope; not in current roadmap
   Rationale: Scope is DocStratum library + Streamlit demo, not platform integrations
   Future: v1.5+ can establish plugin architecture if needed
```

#### Example 3: Streaming Parser (for Large Files)

```
Question: "Should we implement streaming/chunked parsing for >100MB files?"

Decision Tree:
├─ In OOS registry? NO
├─ Supports main module? Partially → FR-031 (COULD have streaming)
├─ Enables demo? NO (demo files are < 50KB)
├─ COULD have? YES → FR-031
├─ Research-driven? YES → v0.0.1c token budgeting
├─ Effort estimate? 3–4 hours for streaming API
├─ Time budget remaining? If > 4 hours → IN SCOPE
│
└─ DECISION: In scope IF time permits; otherwise defer
   Rationale: FR-031 is COULD; implement if core features complete early
   Alternative: Doc note "For files > 50MB, consider streaming (see FR-031)"
```

---

## Part 4: Deferred Features Registry

### Valuable Ideas for Future Versions

These are features that were considered valuable but are out of scope for v0.6.0 due to timeline/complexity. They are candidates for future versions (v1.0+).

| Feature | Category | Priority | Estimated Effort | Target Version | Rationale |
|---|---|---|---|---|---|
| Embeddings + semantic search | ML | SHOULD | 8–12 hours | v1.5+ | Improves context relevance; requires vector DB setup |
| Web-based editor | Platform | SHOULD | 10–15 hours | v1.5+ | Enables collaborative llms.txt creation; requires deployment |
| Neo4j visualization | UI | COULD | 6–8 hours | v1.5+ | Visually impressive; not essential for MVP |
| Documentation auto-generation | AI | SHOULD | 12–20 hours | v1.5+ | Valuable but requires fine-tuning; manual extraction works for MVP |
| Real-time sync with source docs | Integration | SHOULD | 15–25 hours | v2.0+ | Complex; requires per-platform connectors |
| Multi-language support | Localization | COULD | 10–15 hours | v2.0+ | Nice-to-have; focus on English ecosystem first |
| GraphQL API | Backend | COULD | 8–12 hours | v1.5+ | Production feature; REST/CLI sufficient for MVP |
| Docker/Kubernetes | Deployment | SHOULD | 6–10 hours | v1.5+ | For production; local dev + Streamlit sufficient for portfolio |
| Slack Bot integration | Integration | COULD | 4–6 hours | v1.5+ | Fun but not essential; web demo covers use cases |
| Performance benchmarking suite | QA | SHOULD | 4–6 hours | v1.5+ | Nice-to-have; basic latency testing covers MVP |
| LLM fine-tuning | AI | COULD | 20–30 hours | v2.0+ | Advanced; base models sufficient for MVP |
| **[v0.0.7]** Full ecosystem scoring (5 dimensions) | Ecosystem | SHOULD | 8–12 hours | v0.7.0 | 2 of 5 dimensions in MVP; remaining 3 need content analysis |
| **[v0.0.7]** Content page validator | Ecosystem | SHOULD | 6–10 hours | v0.7.0 | Per-page validation beyond link resolution |
| **[v0.0.7]** URL-based ecosystem discovery | Ecosystem | SHOULD | 8–12 hours | v0.8.0 | Web crawling from domain root; local-only in MVP |

---

## Part 5: Scope Change Management Process

### How to Handle New Requests (During Implementation)

If new requirements arise during v0.1–v0.6 implementation, follow this process:

#### Step 1: Document the Request

- **Source:** Who requested it (you, feedback, discovery)?
- **Title:** Clear name for the feature
- **Description:** What does it do?
- **Effort Estimate:** Rough hours needed (1–2 hours for a rough estimate)
- **Impact:** How does it affect existing features?

#### Step 2: Apply Scope Fence

Run the new feature through the Scope Fence decision tree (Part 3). Result:

- **Clearly In Scope:** Implement as part of the module
- **Clearly Out of Scope:** Add to Deferred Features Registry; document rationale
- **Ambiguous:** Escalate to Step 3

#### Step 3: Escalate (If Ambiguous)

If unclear, answer these questions:

1. **Does it advance the core research goal** (proving DocStratum improves agent performance)?
   - YES → Likely in scope
   - NO → Likely out of scope
2. **Can we deliver v0.6.0 MVP without it?**
   - YES → Probably out of scope for MVP (defer or COULD)
   - NO → Probably in scope
3. **Is estimated effort < 2 hours?**
   - YES → Consider adding as COULD if time permits
   - NO → Defer to post-v0.6.0

#### Step 4: Decision

- **APPROVED:** Add to implementation backlog; estimate effort; assign to appropriate module
- **DEFERRED:** Add to Deferred Features Registry with target future version
- **REJECTED:** Document rationale in rejected features log (for portfolio review)

#### Step 5: Log the Decision

Keep a "Scope Change Log" file documenting:

```
Date: 2026-02-XX
Feature: [Title]
Request From: [Source]
Decision: [APPROVED / DEFERRED / REJECTED]
Effort: [Hours]
Rationale: [Brief explanation]
```

---

## Part 6: Explicit Exclusions with Justifications

### What DocStratum IS NOT

1. **Not a replacement for the official llms.txt spec**
   - Justification: Official spec is stable; DocStratum extends it
   - How we handle it: Maintain full backward compatibility; reference official spec in all docs

2. **Not a commercial product**
   - Justification: Portfolio project; no monetization
   - How we handle it: Open source; community-driven; free forever

3. **Not a full RAG system**
   - Justification: RAG is complex; DocStratum provides structured context (simpler, sufficient)
   - How we handle it: Document how DocStratum integrates with RAG pipelines post-MVP

4. **Not an LLM platform**
   - Justification: We use existing APIs (OpenAI, Anthropic); don't train models
   - How we handle it: Abstract LLM provider via LiteLLM; support multiple models

5. **Not a documentation platform**
   - Justification: Too many platforms; we provide tools, not hosting
   - How we handle it: Reference implementations for Stripe, Nuxt, etc.; enable others to host

6. **Not a real-time collaboration tool**
   - Justification: Collaboration is complex; focus on individual use
   - How we handle it: Document how DocStratum integrates with Google Docs, Notion, etc.

7. **Not a machine learning research project**
   - Justification: We use off-the-shelf models; don't do research on new architectures
   - How we handle it: Focus on empirical testing of existing approaches

8. **[v0.0.7] Not a documentation generator or authoring tool**
   - Justification: DocStratum validates and scores documentation ecosystems; it does not create or edit documentation files. Generation is a fundamentally different product (see OOS-B3).
   - How we handle it: Provide diagnostic remediations that tell authors *what* to fix; the author makes the fixes.

9. **[v0.0.7] Not a web crawler or documentation scraper**
   - Justification: MVP ecosystem discovery operates on local directories only. URL-based crawling is deferred to v0.8.0 (OOS-H4). DocStratum does not index the web — it validates what you give it.
   - How we handle it: Accept local directory paths or explicit file lists as input. URL crawling is a deferred feature with its own complexity budget.

---

## Part 7: Scope Metrics & Health Checks

### Tracking Scope Throughout Implementation

Every 2 weeks, check:

| Metric | Target | Action if Failed |
|---|---|---|
| **Approved out-of-scope items documented** | ≥ 15 | Review decision tree; ensure clarity |
| **Deferred features in registry** | ≥ 5 | Ensure valuable ideas aren't lost |
| **Scope change requests handled** | ≤ 1 per week | If > 1/week, scope boundary might be unclear |
| **Estimated effort overrun** | ≤ 5% | If > 5%, modules need re-estimation |
| **Feature scope drift** | 0 items added to MVP | If any drift detected, apply decision tree immediately |

---

## Part 8: OOS-to-FR Traceability

### Objective

Every out-of-scope item exists in relation to one or more functional requirements from v0.0.5a. Some OOS items represent features that were considered and rejected; others represent extensions of existing FRs that exceed the v0.6.0 boundary. This matrix establishes bidirectional traceability so that during implementation, any "why didn't we include X?" question has a documented answer.

### Category A (Commercial) → FR Mapping

| OOS Item | Related FRs | Relationship | Rationale for Exclusion |
|----------|------------|--------------|------------------------|
| OOS-A1 (SaaS Platform) | FR-059–065 (Demo Layer) | Extension beyond | Demo is local Streamlit; SaaS requires deployment infra beyond CONST-002 (portfolio scope) |
| OOS-A2 (Commercial Licensing) | None directly | Orthogonal | Business concern, not functional requirement; CONST-002 makes this irrelevant |
| OOS-A3 (Premium Tiers) | FR-064 (Settings Panel) | Extension beyond | Settings are local config; premium tiers require user auth and payment — exceeds CONST-006 (time budget) |

### Category B (Platforms) → FR Mapping

| OOS Item | Related FRs | Relationship | Rationale for Exclusion |
|----------|------------|--------------|------------------------|
| OOS-B1 (Web Editor) | FR-059 (Streamlit UI) | Extension beyond | Streamlit is read-only demo; full editor requires JS frontend — exceeds CONST-003 (fixed tech stack) |
| OOS-B2 (Real-Time Sync) | FR-026 (Loader), FR-030 (Cache) | Extension beyond | Loader handles file/URL input; sync requires per-platform connectors — exceeds CONST-006 |
| OOS-B3 (Auto-Generation) | FR-020 (Few-Shot Bank), FR-016 (Concept Map) | Inverse approach | DocStratum validates/enriches; auto-generation requires domain-specific knowledge extraction |
| OOS-B4 (Full RAG) | FR-035 (Query-Aware Selection), FR-046 (Retrieval Strategy) | Extension beyond | FR-046 includes keyword + hybrid search; full RAG requires vector DB — exceeds scope |
| OOS-B5 (GraphQL API) | FR-025 (JSON/YAML Export) | Extension beyond | Export covers serialization; GraphQL requires API server infra — exceeds CONST-002 |

### Category C (Ecosystem Integration) → FR Mapping

| OOS Item | Related FRs | Relationship | Rationale for Exclusion |
|----------|------------|--------------|------------------------|
| OOS-C1 (Stripe Integration) | FR-026 (Loader) | Specialization | Loader is generic; Stripe-specific handling violates generalization principle |
| OOS-C2 (Confluence Plugin) | FR-026 (Loader) | Extension beyond | Loader accepts URL/file; platform plugins require SDK integration — exceeds scope |
| OOS-C3 (VS Code Extension) | FR-008 (Error Reporting) | Extension beyond | Errors are CLI/API; VS Code extension requires TypeScript — violates CONST-003 |
| OOS-C4 (GitHub App) | FR-003–007 (Validation) | Extension beyond | Validation is local library; CI/CD integration requires webhook handling — exceeds scope |
| OOS-C5 (Slack Bot) | FR-060 (Side-by-Side View) | Extension beyond | Demo view is Streamlit; Slack bot requires bot API registration — exceeds scope |

### Category D (Advanced ML) → FR Mapping

| OOS Item | Related FRs | Relationship | Rationale for Exclusion |
|----------|------------|--------------|------------------------|
| OOS-D1 (Embeddings) | FR-046 (Retrieval Strategy) | Extension beyond | FR-046 includes keyword + hybrid; embeddings require vector DB — COULD for post-MVP |
| OOS-D2 (Fine-Tuned LLM) | FR-039–040 (Agents) | Extension beyond | Agents use base models; fine-tuning requires labeled data + compute — exceeds CONST-006 |
| OOS-D3 (Multi-Modal) | FR-013–025 (Content Structure) | Extension beyond | Content layers are text-based; multi-modal requires media parsing — beyond project goals |
| OOS-D4 (RLHF) | FR-048 (Test Harness) | Extension beyond | Test harness measures quality; RLHF requires ongoing training loop — exceeds scope |
| OOS-D5 (LLM as Validator) | FR-003–007 (Validation Levels) | Alternative approach | Validation uses deterministic rules; LLM judge is non-deterministic — considered but deferred |

### Category E (Deployment) → FR Mapping

| OOS Item | Related FRs | Relationship | Rationale for Exclusion |
|----------|------------|--------------|------------------------|
| OOS-E1 (Docker) | FR-059 (Streamlit UI) | Extension beyond | Demo runs locally via `streamlit run`; Docker adds deployment complexity — CONST-002 |
| OOS-E2 (Kubernetes) | None directly | Orthogonal | Orchestration is production concern; portfolio demo doesn't need it |
| OOS-E3 (Monitoring) | FR-049 (Trace/Logging), FR-067 (Logging) | Extension beyond | Internal logging covers debugging; production monitoring requires external services |
| OOS-E4 (Horizontal Scaling) | None directly | Orthogonal | Single-user tool; scaling is production concern — CONST-001 (solo developer) |
| OOS-E5 (Backup/DR) | None directly | Orthogonal | Portfolio project; no data persistence requiring recovery |

### Category F (Legacy) → FR Mapping

| OOS Item | Related FRs | Relationship | Rationale for Exclusion |
|----------|------------|--------------|------------------------|
| OOS-F1 (Python 3.7) | All FRs (via NFR-014) | Constraint boundary | NFR-014 sets Python 3.9+ floor; 3.7 is EOL — no value in backward compatibility |
| OOS-F2 (Old llms.txt Versions) | FR-001–002 (Schema) | Non-applicable | Official spec is stable; no versioning exists yet — nothing to support |
| OOS-F3 (Legacy LLM Models) | FR-044 (LLM Providers) | Constraint boundary | NFR-015 targets current models; deprecated models offer no value for testing |
| OOS-F4 (Windows-Specific) | FR-026 (Loader) | Already handled | NFR-016 requires cross-OS via pathlib; special Windows handling is unnecessary |

### Category G (Nice-to-Have) → FR Mapping

| OOS Item | Related FRs | Relationship | Rationale for Exclusion |
|----------|------------|--------------|------------------------|
| OOS-G1 (Neo4j) | FR-017 (Concept Graph), FR-062 (Graph Viz) | Extension beyond | FR-017 builds graph in-memory; FR-062 is COULD; Neo4j adds server dependency — deferred |
| OOS-G2 (Multi-Language) | FR-026 (Loader) | Extension beyond | Loader handles UTF-8 text; multi-language requires i18n infrastructure — exceeds scope |
| OOS-G3 (Analytics Dashboard) | FR-061 (Metrics Display) | Extension beyond | FR-061 shows test metrics in Streamlit; analytics dashboard requires persistent DB |
| OOS-G4 (Batch Processing UI) | FR-059 (Streamlit UI) | Extension beyond | UI handles single file; batch requires job queue — CLI can batch via scripts |
| OOS-G5 (Mobile App) | FR-059 (Streamlit UI) | Extension beyond | Streamlit is web-accessible; native mobile app exceeds scope entirely |

### Coverage Summary

| Category | OOS Count | FRs Referenced | Primary Constraint |
|----------|-----------|---------------|-------------------|
| A: Commercial | 3 | 7 FRs | CONST-002 (portfolio scope) |
| B: Platforms | 5 | 8 FRs | CONST-003 (fixed tech stack), CONST-006 (time budget) |
| C: Integration | 5 | 5 FRs | CONST-003 (fixed tech stack), CONST-005 (v0.6.0 target) |
| D: Advanced ML | 5 | 8 FRs | CONST-006 (time budget), project goals |
| E: Deployment | 5 | 3 FRs | CONST-002 (portfolio scope) |
| F: Legacy | 4 | 4 FRs | NFR-014/015/016 (compatibility constraints) |
| G: Nice-to-Have | 5 | 6 FRs | CONST-005 (v0.6.0 target), CONST-006 (time budget) |
| **[v0.0.7]** H: Ecosystem Boundaries | 8 | TBD (pending FR-070+ definition in v0.0.5a revision) | CONST-005 (v0.6.0 target), CONST-006 (time budget) |
| **TOTAL** | **40** | **41+ unique FRs referenced** | **All 6 constraints invoked** |

---

## Part 9: Research-to-OOS Traceability

### Objective

Every out-of-scope decision is informed by research evidence from v0.0.1–v0.0.4. This section traces which research findings justify specific exclusion decisions, ensuring that scope boundaries are evidence-grounded rather than arbitrary.

### Research Phase → OOS Mapping

| Research Phase | Key Finding | OOS Items Informed | How It Informs Exclusion |
|---------------|-------------|-------------------|------------------------|
| v0.0.1 (Spec Deep Dive) | Official spec is stable; no versioning mechanism exists | OOS-F2 (Old Versions) | No legacy versions to support — exclusion is definitional |
| v0.0.1 (Spec Deep Dive) | 8 specification gaps identified (no validation, no schema, no quality metrics) | OOS-D5 (LLM Validator) | Gaps justify rule-based validation; LLM validation is an alternative approach, not a gap fill |
| v0.0.1c (Processing Methods) | 8K curated tokens outperforms 200K raw | OOS-B4 (Full RAG) | Structured context is sufficient; full RAG is overkill for the proven token budget model |
| v0.0.2 (Wild Examples) | File sizes range 159 bytes to 3.7M tokens | OOS-E4 (Horizontal Scaling) | Typical files are <50KB; scaling is a production concern, not a portfolio concern |
| v0.0.2 (Wild Examples) | 0% LLM Instructions adoption across 18 implementations | OOS-D2 (Fine-Tuned LLM) | No training data exists for llms.txt understanding; base models must suffice |
| v0.0.3 (Ecosystem Survey) | 75+ tools found; zero provide formal validation or scoring | OOS-C1–C5 (Integrations) | Ecosystem is fragmented; integrating with any single platform is wrong investment |
| v0.0.3 (Ecosystem Survey) | Adoption Paradox: grassroots adoption, zero search LLM consumption | OOS-A1–A3 (Commercial) | No validated revenue pathway; commercial products are premature |
| v0.0.3 (Ecosystem Survey) | MCP is the only validated consumption pathway | OOS-B5 (GraphQL API), OOS-C5 (Slack Bot) | API and bot integrations target wrong consumption model; MCP is the channel |
| v0.0.4 (Best Practices) | 57 automated checks define the quality surface area | OOS-D5 (LLM Validator) | Rule-based checks are deterministic and sufficient; LLM judge adds non-determinism |
| v0.0.4 (Best Practices) | 100-point composite scoring pipeline validated against gold standards | OOS-G3 (Analytics Dashboard) | Scoring pipeline exists; analytics dashboard is a presentation layer, not a quality concern |
| v0.0.4d (Differentiators) | DECISION-015: AI coding assistants via MCP as primary target | OOS-B1 (Web Editor), OOS-G5 (Mobile App) | Target audience uses IDEs, not web editors or mobile apps |
| v0.0.4d (Differentiators) | DECISION-013: Token budgets as first-class constraint | OOS-D3 (Multi-Modal) | Token budgets are text-calibrated; multi-modal content breaks the budgeting model |

---

## Part 10: Inputs from Previous Sub-Parts

| Source | What It Provides | Used In |
|--------|-----------------|---------|
| v0.0.1 — Specification Deep Dive | Specification gaps (8 identified); stable spec status; processing method options | OOS-F2 (no legacy versions); OOS-D5 (LLM validator alternative); Part 6 exclusion #1 (not a spec replacement) |
| v0.0.1c — Context & Processing Patterns | Token budgeting architecture; 8K curated > 200K raw finding; hybrid pipeline design | OOS-B4 (Full RAG not needed); OOS-D3 (multi-modal breaks token model); Scope Fence research-driven check |
| v0.0.2 — Wild Examples Audit | File size variance (159B–3.7M tokens); quality correlation data; 0% LLM Instructions adoption | OOS-E4 (scaling not needed for typical files); OOS-D2 (no training data for fine-tuning); Part 1 in-scope calibration |
| v0.0.3 — Ecosystem Survey | 75+ tools, zero validation/scoring; Adoption Paradox; MCP as validated transport | OOS-A1–A3 (commercial premature); OOS-C1–C5 (integration sprawl risk); OOS-B5 (GraphQL targets wrong model) |
| v0.0.4 — Best Practices Synthesis | 57 checks, 100-pt scoring, 22 anti-patterns, 16 design decisions, MUST/SHOULD/COULD framework | OOS-D5 (rules sufficient); OOS-G3 (scoring exists); Scope Fence decision tree node: "Is it research-driven?" |
| v0.0.5a — Functional Requirements | 68 FRs (FR-001–FR-068); MoSCoW priorities; 7 module boundaries; acceptance tests | Part 1 in-scope statement; Scope Fence decision tree nodes: "Does it support a main module?" and "Is it COULD have?"; OOS-to-FR traceability (Part 8) |
| v0.0.5b — Non-Functional Requirements & Constraints | 21 NFRs with targets; 6 hard constraints (CONST-001–006); trade-off resolutions; risk register | All OOS category rationales reference constraints; Scope Fence default decision; Part 5 change management escalation criteria |

---

## Part 11: Outputs to Next Sub-Part

| Output | Consumed By | How It's Used |
|--------|------------|---------------|
| 32 out-of-scope items (OOS-A1 through OOS-G5) | v0.0.5d (Success Criteria & MVP) | Defines what is explicitly excluded from MVP pass/fail criteria — if a feature appears in OOS, it cannot be a success criterion |
| In-scope boundary statement (Part 1) | v0.0.5d (Success Criteria) | The 9 in-scope deliverables become the basis for the MVP Definition of Done checklist |
| Deferred features registry (Part 4, 11 items) | v0.0.5d (Success Criteria) | Stretch goals in v0.0.5d are drawn from deferred features with lowest effort estimates |
| Scope Fence decision tree (Part 3) | v0.0.5d (Success Criteria) | Test scenarios in v0.0.5d reference the Scope Fence to validate that the demo covers only in-scope features |
| Scope change management process (Part 5) | v0.1.0+ (Implementation) | Active governance tool used throughout v0.1–v0.6 to evaluate any new feature idea before implementation |
| OOS-to-FR traceability (Part 8) | v0.1.0+ (Implementation) | When implementing a FR, developers can check if any related OOS items were considered and rejected — preventing accidental scope creep |
| Scope health metrics (Part 7) | v0.1.0+ (Implementation) | Biweekly scope health checks use these metrics to detect early signs of scope drift |

---

## Part 12: Limitations & Constraints

1. **OOS items are version-scoped, not permanent exclusions.** Every OOS item includes a "When Feasible" column indicating the version at which the feature becomes viable. The Deferred Features Registry (Part 4) captures the most valuable items with effort estimates for future planning. Exclusion from v0.6.0 does not imply the feature lacks value.

2. **Effort estimates in the Deferred Features Registry are rough.** The 4–30 hour estimates are order-of-magnitude approximations based on research-phase understanding. Actual effort may vary significantly once implementation context is available. These estimates should be refined during post-MVP planning, not used for scheduling.

3. **The Scope Fence decision tree is a heuristic, not an algorithm.** The tree provides structured guidance for evaluating new ideas, but ambiguous cases will arise. The escalation path (Part 5, Step 3) handles edge cases, but ultimately the developer (solo, per CONST-001) makes the final call. The tree reduces decision fatigue; it doesn't eliminate judgment.

4. **Category boundaries are pragmatic, not taxonomic.** Some OOS items could belong to multiple categories (e.g., OOS-D1 "Embeddings" could be Category B "Platform" or Category D "Advanced ML"). The assigned category reflects the primary reason for exclusion, not a formal classification system.

5. **Scope health metrics assume biweekly review cadence.** The metrics in Part 7 are designed for a sprint-style review cycle. If implementation proceeds in a different rhythm (e.g., daily bursts, weekly marathons), the monitoring cadence should adjust accordingly. The key is consistent review, not the specific interval.

6. **The OOS-to-FR traceability (Part 8) is not exhaustive.** Each OOS item is mapped to the most directly related FRs. Some OOS items have tangential relationships to additional FRs that are not captured. The mapping prioritizes clarity over completeness — the goal is to answer "why was this excluded?" not "what else could this have touched?"

---

## Part 13: User Stories

> As a **solo developer building DocStratum**, I need clearly defined scope boundaries with a structured decision process so that when I'm mid-implementation and think "wouldn't it be cool to also add X?" I have a documented, pre-committed answer that prevents me from derailing the project timeline. The Scope Fence decision tree is my first line of defense against the scope creep that kills solo projects.

> As a **solo developer managing my own time budget (CONST-006: 40–60 hours)**, I need a deferred features registry that captures good ideas without obligating me to implement them, so that I can say "not now, but documented for later" instead of either losing the idea or losing time implementing it prematurely. The registry preserves intellectual investment without spending implementation hours.

> As a **portfolio evaluator reviewing DocStratum**, I need evidence that the developer made deliberate, defensible scope decisions — not just "we ran out of time" but "we evaluated this against clear criteria and deferred it with rationale." The 32 OOS items with justifications, the Scope Fence decision tree, and the explicit exclusion statements demonstrate mature project management and engineering discipline.

---

## Deliverables

- [x] Clear, explicit in-scope statement (what DocStratum is)
- [x] 40+ out-of-scope items organized by 8 categories with detailed justifications **[v0.0.7: was 32/7]**
- [x] "Scope Fence" decision tree with 3 worked examples
- [x] Deferred features registry (14 valuable ideas for future versions with effort estimates) **[v0.0.7: was 11]**
- [x] Scope change management process (5-step procedure)
- [x] Explicit exclusions with rationales (9 "what DocStratum is NOT" statements) **[v0.0.7: was 7]**
- [x] Scope health metrics for monitoring (5 metrics with targets and failure actions)
- [x] OOS-to-FR traceability matrix mapping all 32 original OOS items to 41 unique functional requirements
- [x] Research-to-OOS traceability linking 12 key research findings to OOS decisions
- [x] Inputs from previous sub-parts documented (7 sources mapped to specific outputs)
- [x] Outputs to next sub-part documented (7 outputs mapped to consumers)
- [x] Limitations acknowledged with rationale (6 documented limitations)
- [x] User stories for 3 personas (developer, time-manager, evaluator)
- [x] **[v0.0.7]** Scope Change Log with formal record of ecosystem pivot (Part 14)
- [x] **[v0.0.7]** Category H: 8 ecosystem boundary OOS items (OOS-H1 through OOS-H8)
- [x] **[v0.0.7]** 3 ecosystem-related deferred features added to registry

---

## Acceptance Criteria

- [x] In-scope boundary is crystal clear (anyone can determine if a feature is in scope)
- [x] Every out-of-scope item includes: what it is, why excluded, when feasible, what would change
- [x] Scope Fence decision tree is usable (clear flow, 3 examples provided)
- [x] Deferred features are genuinely valuable (not trash ideas) with effort estimates
- [x] Scope change management process is lightweight (won't stall development)
- [x] Exclusions list provides confidence that scope is defensible
- [x] Project team (you) commits to these boundaries
- [x] Zero scope creep expected during v0.1–v0.6 with these safeguards
- [x] OOS-to-FR traceability complete (all 32 OOS items mapped to related FRs)
- [x] Research-to-OOS traceability complete (OOS decisions traced to v0.0.1–v0.0.4 evidence)
- [x] Inputs from previous sub-parts documented
- [x] Outputs to next sub-part documented
- [x] Limitations & constraints acknowledged
- [x] User stories defined for target personas
- [x] Document is self-contained and structurally consistent with v0.0.5a and v0.0.5b

---

## Part 14: Scope Change Log [v0.0.7]

> This section records formal scope changes processed through the Part 5 Scope Change Management Process.

### Scope Change #001: Ecosystem Pivot

```
Date: 2026-02-07
Feature: Ecosystem-Level Documentation Quality Platform
Request From: Ryan (project owner) — during v0.1.x Foundation phase
Decision: APPROVED
Effort: +15–25 hours on top of existing budget (schema: 4–6 hrs, pipeline: 10–15 hrs, tests: 3–5 hrs)
Rationale: See below
```

**Step 1 — Document the Request:**
During the v0.1.x Foundation phase, a foundational question surfaced: "What standards are we validating against?" The research to answer this question (v0.0.6 Platinum Standard) revealed that single-file validation, while necessary, is insufficient to assess the quality of a project's AI-ready documentation. The relationships between files (index → content pages → aggregate) are a quality dimension that no existing tool measures. Ryan directed the pivot: "I think we should evolve DocStratum into an ecosystem-level documentation quality platform."

**Step 2 — Apply Scope Fence:**
The Scope Fence decision tree was applied:
- In OOS registry? NO — ecosystem validation was not previously an OOS item (it was unanticipated)
- Supports main module? YES — directly extends Module 2 (Validation) and Module 5 (Quality Scoring)
- Enables demo? YES — ecosystem view is a compelling differentiator for the Streamlit demo
- Is it COULD have? No — this is a strategic direction change, not a nice-to-have
- Research-driven? YES — v0.0.6 and v0.0.7 provide comprehensive evidence
- **Result: Likely in scope**

**Step 3 — Escalate (Ambiguous):**
The scope expansion is substantial, so escalation questions were applied:
1. Does it advance the core research goal? YES — ecosystem validation is a category-creating differentiator
2. Can we deliver v0.6.0 MVP without it? YES for single-file, but the product would be undifferentiated
3. Estimated effort < 2 hours? NO — estimated at 15–25 additional hours
4. **Resolution:** Approve with phased implementation. Core ecosystem features (schema, discovery, link resolution, 2 of 5 scoring dimensions) in MVP. Advanced features (full scoring, content page validation, URL crawling, compression analysis) deferred to v0.7.0–v1.0+.

**Step 4 — Decision: APPROVED with scope boundaries.**

The following are IN SCOPE for v0.6.0 MVP:
- Ecosystem-aware schema models
- Directory-based ecosystem discovery
- Cross-file link resolution
- Basic ecosystem health score (Completeness + Coverage dimensions)
- 12 new ecosystem diagnostic codes
- 6 new ecosystem anti-patterns

The following are OUT OF SCOPE (added as Category H, OOS-H1 through OOS-H8):
- Full 5-dimension scoring, content page validation, instruction file validation, URL crawling, compression scoring, report generation, monorepo support, manifest files

**Step 5 — Logged:** This entry constitutes the formal log record.

---

## Next Step

Once this sub-part revision is approved, proceed to:

**v0.0.5a — Functional Requirements (Revision)** — Add ecosystem-level functional requirements (FR-070+).

**v0.0.5d — Success Criteria & MVP Definition (Revision)** — Add ecosystem acceptance scenarios and update the MVP Definition of Done checklist.
