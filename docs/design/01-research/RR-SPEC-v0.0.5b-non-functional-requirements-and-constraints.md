# v0.0.5b — Non-Functional Requirements & Constraints

> **Sub-Part:** Define all non-functional requirements (performance, usability, maintainability, compatibility, security) and hard constraints that will guide implementation decisions and quality standards.

---

> **REVISION NOTICE — v0.0.7 Ecosystem Pivot (2026-02-07)**
>
> This document was revised following the strategic pivot defined in `RR-SPEC-v0.0.7-ecosystem-pivot-specification.md`. A new section (§5a: Ecosystem Performance Requirements) was added containing 4 non-functional requirements (NFR-022 through NFR-025) for ecosystem discovery time, pipeline throughput, memory overhead, and link resolution accuracy. Quality standards (§9) and risk mitigation (§10) were updated with ecosystem-specific targets. Changes are marked with `[v0.0.7]` tags. Original NFRs (NFR-001 through NFR-021) and constraints (CONST-001 through CONST-006) are unchanged.
>
> **Impact summary:** NFR count 21 → 25. Quality dimensions unchanged (5). New entries in per-module quality standards (Module 8), risk register (+2 ecosystem risks), and traceability matrix (NFR-022–025 → ecosystem FRs).

---

## Sub-Part Overview

This sub-part complements v0.0.5a (Functional Requirements) by defining HOW WELL the system must perform and what immovable boundaries constrain its implementation. Drawing on performance insights from v0.0.1c (token budgeting, processing pipelines), quality standards from v0.0.4b (content scoring, description quality), usability patterns from v0.0.2 (error handling in real-world files), ecosystem constraints from v0.0.3 (MCP transport, provider compatibility), **[v0.0.7]** platinum standard validation criteria from v0.0.6, and ecosystem pivot architecture from v0.0.7, this document establishes 25 formally identified non-functional requirements (NFR-001 through NFR-025) **[v0.0.7: was 21]** across 5 quality dimensions (Performance, Usability, Maintainability, Compatibility, Security) plus 6 hard constraints (CONST-001 through CONST-006) from project scope.

**Distribution:** 2 MUST requirements define critical performance gates, 23 SHOULD requirements establish professional quality standards **[v0.0.7: was 19]**, and 0 COULD requirements — all NFRs are treated as essential quality attributes. All 25 NFRs include measurable targets (ms, MB, %, coverage thresholds) and explicit verification methods. The 6 hard constraints document immovable boundaries from the project's nature as a solo-developer portfolio piece with a fixed tech stack and 40–60 hour time budget.

**Relationship to v0.0.5a:** Each NFR constrains one or more functional requirements from v0.0.5a. For example, NFR-001 (parse time < 500ms) constrains FR-026 (parser implementation) and FR-003–004 (validation levels 0–1). NFR-010 (test coverage ≥ 80%) applies across all 85 functional requirements **[v0.0.7: was 68]**. **[v0.0.7]** NFR-022–025 (ecosystem performance) constrain the ecosystem module FRs (FR-069–085). The traceability section (§11) maps every NFR to the FRs it governs and the research phases that justify its target values.

---

## Objective

While v0.0.5a defines WHAT the system must do (functionality), this sub-part defines HOW WELL it must do it and what constraints are immovable. Non-functional requirements establish performance targets, quality standards, deployment constraints, and technical boundaries.

### Success Looks Like

- 15+ formally identified non-functional requirements (NFR-001 through NFR-015+)
- Performance targets expressed in measurable units (ms, MB, token count, accuracy %)
- Usability standards tied to user workflows (CLI, errors, documentation)
- Maintainability targets (code quality, test coverage, dependency management)
- Security requirements protecting sensitive data and system integrity
- Compatibility matrix defining supported platforms and versions
- Verification methods for each NFR (how we'll test it)

---

## Scope Boundaries

### In Scope

- Performance targets (latency, throughput, memory, token usage)
- Usability standards (CLI design, error messages, documentation quality)
- Maintainability metrics (code quality, test coverage, technical debt)
- Compatibility requirements (Python versions, LLM providers, OS support)
- Security constraints (no secrets, input validation, URL safety)
- Hard constraints from project scope (solo developer, portfolio, time budget)

### Out of Scope

- Functional behavior (that's v0.0.5a)
- Scope boundaries (that's v0.0.5c)
- Success metrics and test scenarios (those are v0.0.5d)
- Detailed implementation strategies
- Third-party service SLAs (we don't control external APIs)

---

## Dependencies

```
v0.0.1–4 — Research Phase (COMPLETED)
    ├── Validated that validation levels 0-4 are feasible
    ├── Confirmed agent integration is possible
    ├── Identified performance constraints (token budgets)
    └── Established quality standards from real-world audit

                            v
v0.0.5b — Non-Functional Requirements (THIS TASK)
                            │
        ┌───────────────────┼───────────────────┐
        v                   v                   v
    v0.1.0            v0.2.0              v0.3.0
  (Schema &        (Validation &      (Parsing &
   Validation)      Context Build)     Loading)
```

---

## 1. Performance Requirements (NFR-001 to NFR-005)

### Objective

Define speed and resource usage targets across all operations. These are critical for agent usability (LLMs have timeout limits) and developer experience (fast feedback loops).

| ID | Requirement | Target | Verification Method | Priority | Notes |
|---|---|---|---|---|---|
| NFR-001 | **Parse time (single llms.txt file)** | < 500ms for typical files (≤ 50KB) | Benchmark with 20+ real files; measure wall-clock time | MUST | Includes file load, tokenization, and validation L0–L1 |
| NFR-002 | **Context build time (all 3 layers)** | < 2s for typical llms.txt (≤ 100 entries) | Benchmark with 10+ files; measure end-to-end time | MUST | May vary by file complexity (concept count, relationship count) |
| NFR-003 | **Agent response latency (baseline)** | < 8s for typical query | Measure 20+ test queries; report p50, p95, p99 | SHOULD | Includes context fetch + LLM call; exclude human input time |
| NFR-004 | **Agent response latency (enhanced with DocStratum context)** | < 12s for typical query | Measure 20+ test queries; report p50, p95, p99 | SHOULD | Acceptable overhead: +4s from additional context processing |
| NFR-005 | **Memory usage (peak, single llms.txt)** | < 200MB for typical files | Profile with memory_profiler; test with largest known file | SHOULD | Excludes LLM model weights (in external API) |

### Performance Context

The performance targets are calibrated to agent use cases:

- **Parse time (500ms):** Agents often make queries in real-time; > 1s feels slow to users
- **Context build (2s):** Token budgets require on-demand context assembly; users tolerate 2s waits
- **Agent response (8–12s):** LLM API calls typically take 3–8s; our overhead should not dominate
- **Memory (200MB):** Assume agent runs on modest hardware; avoid OOM errors

---

## 2. Usability Requirements (NFR-006 to NFR-009)

### Objective

Define quality standards for human-facing workflows. The system serves two user categories: (1) developers integrating DocStratum into agents, and (2) portfolio viewers evaluating the project.

| ID | Requirement | Target | Verification Method | Priority | Notes |
|---|---|---|---|---|---|
| NFR-006 | **CLI error messages** | Clear, actionable, include line/code reference | 100% of errors include: severity, code, message, remediation | SHOULD | Example: "E003 (line 42): Missing H2 section. Every llms.txt requires at least one '## Section' header." |
| NFR-007 | **Documentation coverage** | Every public API documented with docstrings + examples | 100% of modules + functions have docstrings; README covers main flows | SHOULD | Use Google-style docstrings; include example code blocks |
| NFR-008 | **Validation error output** | Max 1 error message per issue; group related issues | Validation output < 100 lines for typical file; top issues highlighted | SHOULD | Avoid overwhelming developers with 50+ errors for one root cause |
| NFR-009 | **Demo UI responsiveness** | UI elements respond within 200ms to user input | All Streamlit widgets respond in < 200ms (excluding external API calls) | SHOULD | Buttons, toggles, dropdowns should feel snappy |

### Usability Context

These standards reflect two audiences:

- **Developers:** Need precise error messages, comprehensive docs, clear API contracts
- **Portfolio viewers:** See clean UI, impressive demo, professional error handling

---

## 3. Maintainability Requirements (NFR-010 to NFR-013)

### Objective

Define code quality and sustainability standards. These ensure the project remains understandable and modifiable as features are added.

| ID | Requirement | Target | Verification Method | Priority | Notes |
|---|---|---|---|---|---|
| NFR-010 | **Test coverage** | ≥ 80% line coverage for core modules (validation, parsing, context building) | Run pytest with coverage; generate coverage report | SHOULD | Accept < 80% for demo/UI code; require ≥ 80% for data processing |
| NFR-011 | **Code style consistency** | 100% compliance with Black (formatter) + Ruff (linter) | Run Black + Ruff in CI; fail build if violations detected | SHOULD | Reduces review friction; ensures consistent code appearance |
| NFR-012 | **Dependency management** | Minimize direct dependencies; pin versions in requirements.txt | Use only required dependencies; justify each; pin versions for reproducibility | SHOULD | Direct deps target: < 15 (excluding dev deps) |
| NFR-013 | **Documentation-to-code ratio** | Substantial comments in complex modules (parsing, context building) | Every function > 20 lines includes docstring; complex algorithms include inline comments | SHOULD | Goal: code understandable without hunting for external docs |

### Maintainability Context

These standards ensure the project is:

- **Testable:** Comprehensive tests catch regressions and enable confident refactoring
- **Readable:** Consistent style and documentation reduce cognitive load
- **Sustainable:** Minimal dependencies ease updates and reduce supply-chain risk
- **Understandable:** Well-commented code and clear structure support future work

---

## 4. Compatibility Requirements (NFR-014 to NFR-018)

### Objective

Define which platforms, versions, and services the system must support.

| ID | Requirement | Target | Verification Method | Priority | Notes |
|---|---|---|---|---|---|
| NFR-014 | **Python version support** | Python 3.9+ | Test on 3.9, 3.10, 3.11, 3.12 in CI | SHOULD | Drop support for 3.8 (EOL); target recent stable releases |
| NFR-015 | **LLM provider compatibility** | OpenAI (GPT-4, GPT-3.5), Claude (via Anthropic API), local via LiteLLM | Test agent with 2+ providers; verify output quality | SHOULD | Use LiteLLM abstraction layer to reduce provider-specific code |
| NFR-016 | **Operating system support** | Linux, macOS, Windows | Test on each OS (CI matrices or manual spot checks) | SHOULD | Use cross-platform path handling; test file I/O on each OS |
| NFR-017 | **URL handling (HTTP/HTTPS)** | Support HTTPS; reject HTTP except localhost | All real URLs must use HTTPS; warn on HTTP in non-test contexts | SHOULD | Protects user data from MITM attacks |
| NFR-018 | **Input validation** | Reject invalid URLs, oversized files, malformed JSON | Validate all external inputs; max file size 50MB; validate JSON before parsing | SHOULD | Prevent security issues and resource exhaustion |

### Compatibility Context

- **Python versions:** Support recent versions (3.9–3.12); assume modern features available
- **LLM providers:** Abstract via LiteLLM; enable swapping providers without code changes
- **Operating systems:** Use pathlib (not os.path); test on Linux, macOS, Windows
- **Security:** HTTPS-only for real domains; reject malicious inputs

---

## 5. Security Requirements (NFR-019 to NFR-021)

### Objective

Protect user data and system integrity. DocStratum processes documentation files, which may contain sensitive information.

| ID | Requirement | Target | Verification Method | Priority | Notes |
|---|---|---|---|---|---|
| NFR-019 | **No credentials in llms.txt** | Detect and warn if llms.txt contains API keys, tokens, passwords | Scan for common secret patterns (regex); warn user if detected | SHOULD | Example pattern: `api_key=sk-.*` |
| NFR-020 | **URL validation** | Validate all URLs before fetching; reject dangerous protocols | Whitelist http/https only; parse with urllib; validate scheme/netloc | SHOULD | Prevent SSRF attacks (local file access via URLs) |
| NFR-021 | **Input sanitization** | Sanitize file paths and URLs before using in commands or logs | Never use unsanitized user input in shell commands; escape special chars in logs | SHOULD | Prevent injection attacks; ensure logs are safe to view |

### Security Context

DocStratum is a portfolio project, not handling sensitive production data. However, good security practices are:

- **Expected in professional code:** Demonstrate security awareness
- **Easy to implement:** Validation + sanitization are straightforward
- **Good for users:** Protect developers who use DocStratum

---

## [v0.0.7] 5a. Ecosystem Performance Requirements (NFR-022 to NFR-025)

### Objective

Define speed, accuracy, and resource usage targets for the ecosystem pipeline introduced in v0.0.7. These requirements complement the single-file performance targets (NFR-001–005) and ensure the ecosystem layer does not degrade the existing user experience. The ecosystem pipeline (discovery → per-file validation → relationship mapping → ecosystem validation → ecosystem scoring) introduces new computational overhead that must be bounded.

| ID | Requirement | Target | Verification Method | Priority | Notes |
|---|---|---|---|---|---|
| NFR-022 | **Ecosystem discovery time (directory scan + manifest build)** | < 3s for ecosystems with ≤ 20 files | Benchmark on 5+ test ecosystems of 1, 5, 10, 20 files; measure wall-clock discovery time | SHOULD | Includes filesystem scan, file classification, and manifest construction; excludes file content parsing |
| NFR-023 | **Ecosystem pipeline total time (all 5 stages)** | < 10s for ecosystems with ≤ 20 files | Benchmark on 5+ test ecosystems; measure end-to-end time from discovery through ecosystem scoring | SHOULD | Individual per-file validation still constrained by NFR-001 (< 500ms each); total = NFR-022 + (files × NFR-001) + relationship mapping + ecosystem scoring |
| NFR-024 | **Ecosystem memory overhead** | < 50MB additional over single-file peak | Profile ecosystem pipeline with memory_profiler; compare peak memory against single-file mode on same files | SHOULD | Ecosystem metadata (relationships, scores, diagnostics) should not multiply memory usage; most data is per-file (already within NFR-005 budget) |
| NFR-025 | **Cross-file link resolution accuracy** | 100% — zero false positives and zero false negatives | Test with 10+ ecosystem fixtures containing known-good and known-broken links; verify every link classified correctly | SHOULD | A false positive (healthy link flagged as broken) erodes user trust; a false negative (broken link missed) defeats the ecosystem value proposition; tolerance is zero |

### Ecosystem Performance Context

The ecosystem pipeline wraps the existing single-file pipeline with 4 additional stages. Performance targets are derived from the following rationale:

- **Discovery time (3s):** Directory scanning is I/O-bound; 20 files × 200ms per stat is worst case ~4s, so 3s target assumes typical filesystem latency. For single-file input, discovery is trivially fast (< 100ms).
- **Pipeline total (10s):** If per-file validation takes < 500ms (NFR-001) and there are 20 files, per-file validation alone could consume 10s. The 10s total budget allows for up to 15 files at full NFR-001 budgets plus ~2.5s for ecosystem-specific stages (relationship mapping, scoring). For ecosystems > 15 files, per-file validation should average well below 500ms (most content pages are simpler than index files).
- **Memory overhead (50MB):** The ecosystem metadata model adds `DocumentEcosystem`, `EcosystemFile` wrappers, `FileRelationship` graph, and `EcosystemScore`. For 20 files, this is approximately: 20 × (EcosystemFile overhead ~500KB) + relationship graph (~100KB) + scoring (~50KB) ≈ 10.15MB. The 50MB budget provides 5× headroom.
- **Link resolution accuracy (100%):** Unlike quality scoring (which is inherently subjective), link resolution is binary: the file either exists or it doesn't. There is no acceptable error rate for this check.

---

## 6. Hard Constraints (from Agentic Instructions & Project Scope)

### Objective

Document immovable boundaries that define what the project is and is not.

| ID | Constraint | Rationale | Impact | Notes |
|---|---|---|---|---|
| CONST-001 | **Solo developer** | Project is portfolio piece; no team collaboration | Implementation must support single-author workflows; no complex branching/PR merging | Affects testing strategy: emphasize comprehensive unit tests over integration tests |
| CONST-002 | **Portfolio project scope** | Not a commercial product; goal is to demonstrate capabilities | No production deployment, no SaaS infrastructure, no 24/7 support | Focus on code quality + documentation; demo can be MVP quality |
| CONST-003 | **Fixed tech stack** | Pydantic, LangChain, Streamlit, Anthropic API are chosen | Do not propose alternatives (FastAPI, Hugging Face Transformers, etc.) unless asked | Enables focused learning and professional expertise |
| CONST-004 | **Research-driven design** | All design decisions must be justified by v0.0.1–4 research | Implement what's been researched; don't speculate about unvalidated features | Maintains project coherence; avoids scope creep |
| CONST-005 | **v0.6.0 target release** | Project scope ends at MVP (v0.6.0); future versions out of scope | Define v0.6.0 feature list precisely in v0.0.5d; do not add to scope mid-project | Protects timeline; enables clear success criteria |
| CONST-006 | **Time budget: 40-60 hours** | Solo developer with competing commitments | Estimate carefully; prioritize ruthlessly; cut low-value features | Affects which SHOULDs/COULDs get implemented |

---

## 7. Quality Attributes Summary

### Matrix: NFRs by Quality Dimension

| Quality Dimension | NFRs | Key Targets |
|---|---|---|
| **Performance** | NFR-001–005 | Parse < 500ms, context < 2s, agent latency < 12s, memory < 200MB |
| **[v0.0.7] Ecosystem Performance** | NFR-022–025 | Discovery < 3s, pipeline < 10s, memory overhead < 50MB, link resolution 100% accurate |
| **Usability** | NFR-006–009 | Clear errors, complete docs, clean UI, responsive widgets |
| **Maintainability** | NFR-010–013 | Test coverage ≥ 80%, Black + Ruff compliant, minimal deps, well-documented |
| **Compatibility** | NFR-014–018 | Python 3.9+, multi-provider LLM support, cross-OS, HTTPS-only, input validated |
| **Security** | NFR-019–021 | No credentials exposed, URLs validated, inputs sanitized |
| **Constraints** | CONST-001–006 | Solo dev, portfolio scope, fixed tech stack, research-driven, v0.6.0 release, 40–60 hour budget |

---

## 8. Trade-Off Analysis

Given time and resource constraints, here are explicit trade-offs:

### Performance vs. Feature Completeness

| Trade-Off | Decision | Rationale |
|---|---|---|
| **Optimize for latency or for accuracy?** | Latency (parse < 500ms, context < 2s) | Agents have timeout budgets; fast feedback loop is essential |
| **Support streaming or bulk mode?** | Bulk mode (load entire llms.txt); streaming is COULD | Simpler implementation; acceptable for typical file sizes |
| **Cache aggressively or keep fresh?** | Cache with TTL (24h default); manual invalidate option | Reduces redundant parsing; balances freshness with performance |

### Features vs. Documentation

| Trade-Off | Decision | Rationale |
|---|---|---|
| **Implement FR-050 (agent templates) or focus on core features?** | Defer templates to post-MVP | Core agents (baseline + enhanced) are sufficient for demo |
| **Implement FR-062 (graph visualization) or basic UI?** | Simple UI (tables + text); defer fancy graphs | Streamlit can display results effectively without D3.js complexity |
| **Write blog post or focus on code?** | Focus on code + comprehensive README | Portfolio evaluators value clean code more than external content |

### Scope vs. Timeline

| Trade-Off | Decision | Rationale |
|---|---|---|
| **Support 5 LLM providers or 2?** | 2 providers (OpenAI, Claude); multi-provider via LiteLLM abstraction | Cover main use cases; LiteLLM enables future expansion without refactoring |
| **Deploy Streamlit or run locally?** | Local Streamlit demo | Deployment adds infrastructure complexity; portfolio can include `streamlit run` instructions |
| **Implement all validation levels (0–4) or core levels (0–2)?** | All levels (0–4); COULD features can be skipped | Research has validated all levels; important for completeness |

---

## 9. Definition of Quality for Each Module

### By Module: Quality Standards

| Module | Performance Target | Test Coverage Target | Documentation Standard |
|---|---|---|---|
| **Schema & Validation** | Parse < 500ms | ≥ 85% | Every validator function has docstring + example |
| **Content Structure** | Context build < 2s | ≥ 80% | Every layer (Master Index, Concepts, Examples) explained with diagrams |
| **Parser & Loader** | File load < 200ms | ≥ 85% | Grammar reference + pseudocode included |
| **Context Builder** | Pipeline < 1.5s | ≥ 75% | Token budgeting algorithm documented with examples |
| **Agent Integration** | LLM call < 8–12s | ≥ 70% (integration tests okay) | System prompts + LangChain integration documented |
| **A/B Testing** | All tests complete < 5 min for 50 queries | ≥ 70% | Test design + metrics explained; statistical methods justified |
| **Demo Layer** | UI response < 200ms | ≥ 60% (UI code has lower bar) | User guide + settings explained; example workflow documented |
| **[v0.0.7] Ecosystem Discovery & Validation** | Discovery < 3s, pipeline < 10s, link accuracy 100% | ≥ 80% | Ecosystem schema models documented; pipeline stages explained; diagnostic codes with remediation; test fixtures documented |

---

## 10. Risk Mitigation

### Key Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **Performance regression (new feature slows parsing)** | Medium | High | Automated performance regression tests in CI; establish baseline early |
| **LLM API outages (OpenAI/Anthropic down)** | Low | High | Graceful degradation; provide offline demo data; document fallback |
| **Scope creep (new requirements discovered mid-project)** | High | High | Rigorous scope boundary definition (v0.0.5c); require explicit approval for out-of-scope work |
| **Token budget exhausted (context too large)** | Medium | High | Implement token budgeting early (FR-033); prioritize filtering over completeness |
| **Test coverage gaps (critical code untested)** | Medium | Medium | Measure coverage in CI; require ≥ 80% before release; identify gaps early |
| **Documentation falls behind code** | High | Medium | Write docs alongside code; README as living document; examples in code comments |
| **[v0.0.7] Ecosystem pipeline breaks single-file backward compat** | Medium | Critical | FR-083 regression test suite; byte-identical output comparison; run on every CI build |
| **[v0.0.7] Ecosystem discovery I/O overhead on slow filesystems** | Low | Medium | Discovery scan is I/O-bound; mitigate with lazy file reading (stat before read); test on network drives if accessible |

---

## 11. NFR-to-FR Traceability Matrix

### Objective

Every non-functional requirement constrains one or more functional requirements from v0.0.5a. This matrix establishes bidirectional traceability, ensuring that when a functional requirement is implemented, the corresponding quality targets are also enforced.

### Performance NFRs → Functional Requirements

| NFR | Constrains FRs | Rationale | Research Source |
|-----|----------------|-----------|----------------|
| NFR-001 (Parse time < 500ms) | FR-026 (Parser/Loader), FR-003 (Validation L0), FR-004 (Validation L1) | Parsing and L0–L1 validation are synchronous operations that block the agent pipeline; must complete within agent timeout budgets | v0.0.1a (grammar complexity), v0.0.1c (processing methods) |
| NFR-002 (Context build < 2s) | FR-013 (Layer 0), FR-016 (Layer 1), FR-020 (Layer 2), FR-024 (cross-layer integration), FR-034 (hybrid pipeline) | All three layers must be assembled within the context build budget; the hybrid pipeline orchestrates this constraint | v0.0.1c (token budgeting, hybrid pipeline architecture) |
| NFR-003 (Baseline latency < 8s) | FR-039 (baseline agent), FR-048 (test harness) | Establishes the control group timing ceiling; test harness must measure and report this | v0.0.4 (agent testing patterns) |
| NFR-004 (Enhanced latency < 12s) | FR-040 (enhanced agent), FR-034 (hybrid pipeline), FR-042 (context window management) | The +4s overhead budget must accommodate context injection, layer selection, and few-shot prepending without exceeding agent timeout | v0.0.1c (token budgeting), v0.0.4 (agent patterns) |
| NFR-005 (Memory < 200MB) | FR-026 (loader), FR-031 (streaming), FR-025 (JSON/YAML export) | Loader must not load entire large files into memory; streaming (FR-031 COULD) is the mitigation path | v0.0.2 (file size variance: 159 bytes to 3.7M tokens observed) |

### Usability NFRs → Functional Requirements

| NFR | Constrains FRs | Rationale | Research Source |
|-----|----------------|-----------|----------------|
| NFR-006 (CLI error messages) | FR-008 (error reporting), FR-003–007 (all validation levels) | Every validation error must include severity, code, message, and remediation; the error reporter (FR-008) is the implementing FR | v0.0.1a (error code registry: E-series, W-series, I-series) |
| NFR-007 (Documentation coverage) | FR-066 (dependency injection), FR-067 (logging), all public-facing FRs | 100% docstring coverage requirement applies to every module's public API surface | v0.0.4 (usability standards), project philosophy (docs-first) |
| NFR-008 (Validation error grouping) | FR-012 (validation summary), FR-008 (error reporting) | Summary must group related issues and cap output at 100 lines for typical files | v0.0.2 (observed: some files generate 50+ raw errors for one root cause) |
| NFR-009 (Demo UI responsiveness) | FR-059 (Streamlit UI), FR-060 (side-by-side view), FR-064 (settings panel) | All Streamlit widgets must respond within 200ms; API call latency is excluded from this target | v0.0.4 (demo requirements) |

### Maintainability NFRs → Functional Requirements

| NFR | Constrains FRs | Rationale | Research Source |
|-----|----------------|-----------|----------------|
| NFR-010 (Test coverage ≥ 80%) | All 45 MUST FRs (core modules) **[v0.0.7: was 32]**; relaxed for FR-059–065 (demo layer: ≥ 60%); **[v0.0.7]** ecosystem module (FR-069–085) held to ≥ 80% | Core data processing (validation, parsing, context building, **[v0.0.7]** ecosystem discovery and validation) must have high coverage to prevent regressions; UI code has lower bar | v0.0.4 (quality standards), CONST-006 (time budget limits) |
| NFR-011 (Black + Ruff compliance) | All FRs that produce Python code | 100% style compliance reduces review friction and ensures consistent appearance across all modules | v0.0.4 (maintainability best practices) |
| NFR-012 (Dependency management < 15 direct deps) | FR-044 (multi-provider via LiteLLM), FR-039–040 (agents via LangChain), FR-059 (demo via Streamlit) | Each major framework (LangChain, Streamlit, Pydantic, LiteLLM) counts as one dependency; must justify every addition | v0.0.3 (ecosystem survey: supply-chain risk analysis) |
| NFR-013 (Documentation-to-code ratio) | FR-032 (processing methods), FR-034 (hybrid pipeline), FR-035 (query-aware selection) | Complex algorithmic modules (context building, ranking, filtering) require inline comments explaining the "why" behind decisions | Project philosophy (Writer's Edge: structure is a feature) |

### Compatibility NFRs → Functional Requirements

| NFR | Constrains FRs | Rationale | Research Source |
|-----|----------------|-----------|----------------|
| NFR-014 (Python 3.9+) | All FRs | No use of 3.8-only features; leverage type hints, match statements (3.10+) with fallbacks | v0.0.3 (ecosystem: most tools target 3.9+) |
| NFR-015 (Multi-provider LLM) | FR-044 (LLM providers), FR-039–040 (agents) | LiteLLM abstraction must be the only provider touchpoint; agents must not contain provider-specific code | v0.0.4 (DECISION-015: MCP-first, but not provider-locked) |
| NFR-016 (Cross-OS) | FR-026 (loader: file paths), FR-025 (serializer: JSON/YAML export) | Use pathlib exclusively; test file I/O on Linux, macOS, Windows in CI | v0.0.3 (user base is cross-platform developers) |
| NFR-017 (HTTPS-only) | FR-026 (URL loading), FR-015 (URL canonicalization), FR-005 (URL resolution) | All real URLs must use HTTPS; HTTP allowed only for localhost during testing | v0.0.4 (security best practices) |
| NFR-018 (Input validation) | FR-026 (loader), FR-003 (syntax validation), FR-028 (error recovery) | Max file size 50MB; validate JSON before parsing; reject URLs with dangerous protocols | v0.0.2 (observed: Cloudflare's 3.7M-token file as cautionary example) |

### Security NFRs → Functional Requirements

| NFR | Constrains FRs | Rationale | Research Source |
|-----|----------------|-----------|----------------|
| NFR-019 (No credentials in llms.txt) | FR-003 (syntax validation), FR-006 (quality validation) | Scan for common secret patterns (regex) during validation; warn user if detected | v0.0.4 (security: Preference Trap anti-pattern risk) |
| NFR-020 (URL validation) | FR-026 (loader), FR-005 (URL resolution), FR-015 (URL canonicalization) | Whitelist http/https only; parse with urllib; validate scheme/netloc before any fetch | v0.0.4 (security: SSRF prevention) |
| NFR-021 (Input sanitization) | FR-026 (loader), FR-049 (trace/logging), FR-067 (cross-module logging) | Never use unsanitized user input in shell commands; escape special chars in logs | v0.0.4 (security: injection prevention) |

### [v0.0.7] Ecosystem Performance NFRs → Functional Requirements

| NFR | Constrains FRs | Rationale | Research Source |
|-----|----------------|-----------|----------------|
| NFR-022 (Ecosystem discovery < 3s) | FR-074 (directory discovery), FR-075 (file type classification), FR-076 (link extraction) | Discovery is the first pipeline stage and must complete quickly to avoid blocking downstream stages; filesystem I/O is the bottleneck | v0.0.7 (Section 7.1: pipeline architecture) |
| NFR-023 (Ecosystem pipeline < 10s) | FR-084 (pipeline orchestration), FR-080 (per-file validation), FR-077 (cross-file resolution), FR-081 (completeness scoring) | Total pipeline time = sum of all 5 stages; per-file validation is the dominant cost (bounded by NFR-001 × file count) | v0.0.7 (Section 7.1), NFR-001 (parse time constraint) |
| NFR-024 (Ecosystem memory overhead < 50MB) | FR-069 (DocumentEcosystem model), FR-070 (EcosystemFile wrappers), FR-071 (FileRelationship graph), FR-072 (EcosystemScore) | Ecosystem metadata structures add memory on top of per-file models; must not push total memory beyond acceptable limits for developer machines | v0.0.7 (Section 4.3), NFR-005 (base memory constraint) |
| NFR-025 (Link resolution accuracy 100%) | FR-077 (cross-file link resolution), FR-078 (diagnostic codes — W012 accuracy) | Link resolution is a binary check (file exists or doesn't); any error directly undermines the ecosystem validation value proposition | v0.0.7 (Section 5.2: W012 specification) |

### Coverage Summary

| Quality Dimension | NFR Count | FRs Constrained | Primary Research Source |
|-------------------|-----------|-----------------|----------------------|
| Performance | 5 | 15 unique FRs | v0.0.1c (processing methods, token budgeting) |
| **[v0.0.7] Ecosystem Performance** | **4** | **10 unique FRs** | **v0.0.7 (ecosystem pipeline architecture)** |
| Usability | 4 | 9 unique FRs | v0.0.1a (error registry), v0.0.4 (demo requirements) |
| Maintainability | 4 | All 85 FRs (via code standards) **[v0.0.7: was 68]** | v0.0.4 (quality standards) |
| Compatibility | 5 | 12 unique FRs | v0.0.3 (ecosystem), v0.0.4 (DECISION-015) |
| Security | 3 | 8 unique FRs | v0.0.4 (anti-patterns, security practices) |
| **TOTAL** | **25 [v0.0.7: was 21]** | **All 85 FRs covered [v0.0.7: was 68]** | **v0.0.1–v0.0.7 (complete research chain)** |

---

## 12. Inputs from Previous Sub-Parts

| Source | What It Provides | Used In |
|--------|-----------------|---------|
| v0.0.1a — Formal Grammar & Parsing Rules | Parsing complexity analysis; error code registry (E/W/I series); validation level definitions | NFR-001 (parse time calibration), NFR-006 (error message format) |
| v0.0.1c — Context & Processing Patterns | Token budgeting concepts; hybrid pipeline architecture; processing method timing estimates | NFR-002 (context build time), NFR-004 (enhanced agent latency), NFR-005 (memory limits) |
| v0.0.2 — Wild Examples Audit | File size variance data (159B to 3.7M tokens); real-world error patterns; quality correlation analysis | NFR-005 (memory calibration), NFR-008 (error grouping rationale), NFR-018 (max file size) |
| v0.0.3 — Ecosystem Survey | Provider compatibility landscape; Python version support across tools; cross-platform usage patterns | NFR-014 (Python version), NFR-015 (LLM providers), NFR-016 (OS support) |
| v0.0.4 — Best Practices Synthesis | Quality scoring pipeline (57 checks); anti-pattern severity classification; security recommendations; demo requirements | NFR-006–009 (usability), NFR-010–013 (maintainability), NFR-019–021 (security) |
| v0.0.5a — Functional Requirements | 85 functional requirements (FR-001 to FR-085) organized by 8 modules **[v0.0.7: was 68 across 7]**; MoSCoW priorities; acceptance tests | NFR-to-FR traceability (§11); per-module quality targets (§9) |
| **[v0.0.7]** v0.0.6 — Platinum Standard Definition | 30-criterion, 5-level quality framework (L0–L4); validation criteria provenance | Informs what the ecosystem validation pipeline measures against; quality targets for validation accuracy |
| **[v0.0.7]** v0.0.7 — Ecosystem Pivot Specification | 3-layer ecosystem model; 5-stage pipeline architecture; 6 new schema entities; 12 diagnostic codes; backward compatibility requirements | NFR-022–025 targets (ecosystem performance); risk register (backward compat risk); per-module quality standards (Module 8) |

---

## 13. Outputs to Next Sub-Part

| Output | Consumed By | How It's Used |
|--------|------------|---------------|
| 25 NFRs with measurable targets **[v0.0.7: was 21]** | v0.0.5c (Scope Definition) | NFR targets constrain what's in scope — features that can't meet NFRs are candidates for deferral; **[v0.0.7]** ecosystem NFRs constrain ecosystem scope |
| 6 hard constraints | v0.0.5c (Scope Definition) | CONST-001–006 define the immovable boundaries that the scope fence must respect |
| Per-module quality targets (§9) | v0.0.5d (Success Criteria & MVP) | Quality standards become pass/fail criteria for the MVP definition |
| Trade-off resolutions (§8) | v0.0.5d (Success Criteria) | Resolved trade-offs inform which stretch goals are realistic given constraints |
| Risk mitigation strategies (§10) | v0.0.5d (Success Criteria) | Risk register feeds into test scenario design and the Definition of Done |
| NFR-to-FR traceability (§11) | v0.1.0+ (Implementation) | Every implementation module knows which quality targets it must meet alongside its functional requirements |

---

## 14. Limitations & Constraints

1. **NFR targets are estimates, not guarantees.** Performance targets (NFR-001 through NFR-005) are calibrated against agent use cases and real-world file data from v0.0.2, but actual performance depends on hardware, network latency, and LLM provider response times. Targets will be validated and potentially adjusted during v0.5.x (Testing & Validation).

2. **Third-party SLA exclusion.** NFR-003 and NFR-004 (agent response latency) include LLM API call time, which is controlled by external providers (OpenAI, Anthropic). The measurable targets assume typical API response times (3–8s). Provider outages or rate limiting are outside project control and handled via graceful degradation (FR-043).

3. **Cross-OS testing is best-effort.** NFR-016 requires Linux, macOS, and Windows support, but CONST-001 (solo developer) limits testing to the developer's available platforms. CI matrix testing (GitHub Actions) mitigates this but may not catch all platform-specific issues.

4. **Security requirements are defensive, not comprehensive.** NFR-019–021 address the most likely attack vectors (credential exposure, SSRF, injection), but DocStratum is a portfolio project (CONST-002), not a security-critical production system. A full security audit is out of scope.

5. **Memory target assumes typical files.** NFR-005 (< 200MB) targets typical llms.txt files (≤ 50KB). The extreme case (Cloudflare's 3.7M-token file from v0.0.2) would require streaming (FR-031, COULD priority) to stay within budget.

6. **Test coverage relaxation for UI code.** NFR-010 relaxes the ≥ 80% target to ≥ 60% for the Demo Layer (FR-059–065) because Streamlit widget testing requires integration-level tooling that is disproportionately expensive for a portfolio demo.

7. **[v0.0.7] Ecosystem pipeline total time target assumes homogeneous file sizes.** NFR-023 (< 10s for ≤ 20 files) assumes most content pages are simpler and faster to validate than the index file. If an ecosystem contains 20 files all as complex as a dense llms.txt index, total time could exceed 10s (20 × 500ms = 10s for per-file validation alone, excluding ecosystem-specific stages). The mitigation path is parallel per-file validation, which is deferred to post-MVP.

8. **[v0.0.7] Link resolution accuracy (100%) applies only to filesystem-based resolution.** NFR-025 guarantees zero false positives/negatives for local file existence checks (does the file exist on disk?). It does not guarantee resolution accuracy for external URLs (which may be behind CDNs, require authentication, or be temporarily down). External URL link checking is deferred (OOS-H5 in v0.0.5c).

---

## 15. User Story

> As a **solo developer building DocStratum**, I need clearly defined non-functional requirements with measurable targets so that I can make informed trade-off decisions during implementation (e.g., "Is this optimization worth the complexity?"), establish automated quality gates in CI (test coverage, style compliance, performance benchmarks), and demonstrate professional engineering rigor to portfolio reviewers who evaluate not just what the code does but how well it does it.

> As a **developer integrating DocStratum into an agent**, I need performance guarantees (parse < 500ms, context build < 2s) and compatibility assurances (Python 3.9+, multi-provider LLM support, cross-OS) so that I can confidently use DocStratum in my agent pipeline without worrying about timeouts, memory exhaustion, or platform incompatibilities.

> As a **portfolio evaluator reviewing DocStratum**, I need evidence of professional quality standards (test coverage, code style, documentation, security practices) so that I can assess the developer's engineering maturity beyond just feature completeness.

---

## Deliverables

- [x] 25 formally identified non-functional requirements (NFR-001 through NFR-025) **[v0.0.7: was 21]**
- [x] Performance requirements with specific targets (latency ms, memory MB, coverage %)
- [x] **[v0.0.7]** Ecosystem performance requirements with specific targets (discovery < 3s, pipeline < 10s, memory overhead < 50MB, link accuracy 100%)
- [x] Usability standards tied to user workflows (developer + portfolio audiences)
- [x] Maintainability metrics (test coverage, style, documentation)
- [x] Compatibility matrix (Python, LLM providers, OS)
- [x] Security requirements protecting data integrity
- [x] 6 hard constraints from project scope (CONST-001 through CONST-006)
- [x] Trade-off analysis across performance/features/scope (9 explicit trade-offs resolved)
- [x] Per-module quality standards (8 modules with performance, coverage, and documentation targets) **[v0.0.7: was 7]**
- [x] Risk mitigation strategies (8 risks with likelihood/impact/mitigation) **[v0.0.7: was 6]**
- [x] NFR-to-FR traceability matrix mapping all 25 NFRs to the 85 functional requirements they constrain **[v0.0.7: was 21 NFRs to 68 FRs]**
- [x] Research source traceability linking NFRs to v0.0.1–v0.0.7 evidence base **[v0.0.7: was v0.0.4]**
- [x] Inputs/Outputs documentation connecting v0.0.5b to adjacent sub-parts
- [x] Limitations acknowledged with rationale (8 documented limitations) **[v0.0.7: was 6]**
- [x] User stories for 3 personas (developer, integrator, evaluator)

---

## Acceptance Criteria

- [x] Every NFR has unique ID (NFR-###)
- [x] Every NFR includes measurable target (ms, MB, %, coverage)
- [x] Every NFR includes verification method (how we test it)
- [x] Performance targets are realistic for agent use cases (calibrated to LLM timeouts)
- [x] Usability standards reflect both developer and portfolio audiences
- [x] Maintainability targets support code quality (tests, style, docs)
- [x] Compatibility covers main platforms/versions/providers
- [x] Security requirements address data protection and input validation
- [x] Hard constraints documented and ratified
- [x] Trade-offs explicitly analyzed and resolved
- [x] NFR-to-FR traceability matrix complete (all 25 NFRs mapped to FRs they constrain) **[v0.0.7: was 21]**
- [x] Research source traceability complete (all NFRs traced to v0.0.1–v0.0.7) **[v0.0.7: was v0.0.4]**
- [x] **[v0.0.7]** Ecosystem performance NFRs have measurable targets and verification methods
- [x] **[v0.0.7]** Ecosystem NFR-to-FR traceability covers all 4 new NFRs → ecosystem FRs
- [x] Inputs from previous sub-parts documented
- [x] Outputs to next sub-part documented
- [x] Limitations & constraints acknowledged
- [x] User stories defined for target personas
- [x] Document is self-contained and implementable

---

## Next Step

Once this sub-part is approved, proceed to:

**v0.0.5c — Scope Definition & Out-of-Scope Registry**

This sub-part defines explicit scope boundaries and the "Scope Fence" decision tree for evaluating new feature ideas during implementation.
