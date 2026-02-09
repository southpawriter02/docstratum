# Documentation Backlog — Ecosystem Validator Architecture

> **Scope:** Pre-implementation design deliverables required before v0.2.x code work begins
> **Status:** ACTIVE
> **Created:** 2026-02-09
> **Last Updated:** 2026-02-09
> **Governed By:** RR-META-documentation-requirements.md
> **Context:** Emerged from architectural review of Gaps 1–3 identified during the v0.1.2c → v0.1.2d transition

---

## Purpose

This document is the canonical tracking artifact for outstanding design specifications that must be completed before the DocStratum validation engine can move from schema definition (v0.1.x) into data preparation and pipeline implementation (v0.2.x). Each deliverable addresses a specific architectural gap identified during the review of how the existing ASoT standards library (166 files, 146 standard elements) translates into an operational, maintainable ecosystem validator.

These deliverables are ordered by dependency — later items build on decisions made in earlier ones. Skipping ahead risks designing pipeline mechanics around assumptions that haven't been validated in writing.

---

## Dependency Chain

The deliverables form a logical sequence where each item feeds the next:

```
[1] Output Tier Specification
        │
        ├──→ [2] Remediation Framework
        │         │
        │         └──→ [5] Report Generation Stage Spec (S6)
        │
        └──→ [3] Unified Rule Registry
                  │
                  └──→ [4] Validation Profiles & Module Composition
                            │
                            └──→ [5] Report Generation Stage Spec (S6)
                                      │
                                      └──→ [6] Ecosystem Scoring Calibration Document
```

**Reading this diagram:** The Output Tier Specification (item 1) is the root dependency because it defines *what the validator delivers*. Everything downstream — how rules are registered, how profiles are composed, how reports are generated, and how ecosystem scores are calibrated — depends on that answer.

---

## Deliverable 1: Output Tier Specification

**Priority:** CRITICAL — Root dependency for all other deliverables
**Suggested Identifier:** `RR-SPEC-v0.1.3-output-tier-specification.md`
**Estimated Scope:** Medium (design spec, no code)
**Depends On:** Nothing — this is the anchor document
**Feeds Into:** Deliverables 2, 3, 4, 5

### Description

This specification defines **what the consumer of a DocStratum validation run actually receives**. The current pipeline ends at Stage 5 (Ecosystem Scoring), producing an `EcosystemScore` model — but there is no formal definition of how that score, along with the full diagnostic output, gets packaged and delivered to different consumer audiences.

The spec must answer four questions:

1. **What are the defined output tiers?** The current working model proposes four tiers, each serving a different audience and use case:
   - **Tier 1 — Pass/Fail Gate:** A binary result (exit code) for CI/CD pipelines. Did the validation pass the configured threshold? Yes or no. This maps to the existing `is_valid` property on `ValidationResult`.
   - **Tier 2 — Diagnostic Report:** A structured list of findings with codes, severities, messages, line numbers, and remediation hints. This is what `ValidationDiagnostic` produces today. The audience is technically literate documentation maintainers.
   - **Tier 3 — Remediation Playbook:** A prioritized action plan that goes beyond "here's what's wrong" to "here's what to do, in what order, and why." Groups diagnostics by priority, sequences them by dependency, and provides estimated effort. The audience is documentation teams and stakeholders.
   - **Tier 4 — Audience-Adapted Recommendations:** Contextualizes the remediation playbook with domain-specific guidance (e.g., "as a developer tools company with API documentation, you should prioritize X over Y"). The audience is enterprise or consulting consumers. This tier requires additional context input beyond what the pipeline produces today.

2. **What data does each tier require from the pipeline?** Map each tier to the specific pipeline stage outputs it consumes. Tier 1 needs only `ValidationResult.is_valid`. Tier 3 needs the full diagnostic set, quality scores, ecosystem scores, and the relationship graph.

3. **What format does each tier take?** Define the serialization format for each tier. Options include JSON (machine-readable for CI), Markdown (human-readable for reports), structured YAML (configuration-friendly), and HTML (for the Streamlit demo layer in v0.4.x).

4. **Which tiers are in scope for v0.2.x–v0.3.x vs. v0.4.x+?** Tier 4 (audience-adapted) almost certainly belongs in v0.4.x or later. But the spec needs to explicitly draw that line so the pipeline architecture can accommodate future tiers without retrofitting.

### Why This Comes First

If we build the Rule Registry, profiles, or pipeline stages without knowing what output format they feed into, we risk designing internal data flows that don't align with the final deliverable shape. The Output Tier Specification is the contract between the pipeline and its consumers. Every other deliverable references this spec as the authoritative definition of "what the validator delivers."

### Exit Criteria

- [ ] Four output tiers formally defined with audience, use case, and data requirements
- [ ] Pipeline stage → tier data mapping documented
- [ ] Serialization format specified per tier
- [ ] Format-tier compatibility matrix defined (which formats are valid for which tiers)
- [ ] Scope boundaries drawn between v0.2.x–v0.3.x and v0.4.x+
- [ ] Reviewed against existing `ValidationResult` and `EcosystemScore` models for compatibility

---

## Deliverable 2: Remediation Framework

**Priority:** HIGH — Required before Deliverable 5 (Report Generation)
**Suggested Identifier:** `RR-SPEC-v0.1.3-remediation-framework.md`
**Estimated Scope:** Medium-Large (design spec with taxonomy and examples)
**Depends On:** Deliverable 1 (Output Tier Specification)
**Feeds Into:** Deliverable 5 (Report Generation Stage)

### Description

Every `DiagnosticCode` in `diagnostics.py` already carries a `remediation` field with a human-readable hint. Every anti-pattern in `ANTI_PATTERN_REGISTRY` has a description that implicitly suggests corrective action. The raw material for remediation guidance exists — what's missing is the **aggregation and prioritization logic** that transforms individual hints into a coherent action plan.

This specification defines how the validator moves from "here's what's wrong" to "here's what to do about it."

The framework must address:

1. **Remediation Priority Model:** How are individual diagnostics ranked when presented together? The current severity levels (ERROR, WARNING, INFO) provide a coarse ordering, but within a severity level, what determines sequence? Proposed factors include: gating impact (does this block LLM consumption entirely?), dependency (does fixing X automatically resolve Y?), effort estimation (quick wins vs. structural rework), and quality score impact (which fix moves the score the most?).

2. **Remediation Grouping Strategy:** Raw diagnostic output can contain dozens of findings. A playbook that lists them linearly is barely better than the raw list. The framework should define grouping strategies — by validation level (L0 fixes first, then L1, etc.), by file (all fixes for `llms.txt` before moving to `llms-full.txt`), by category (all structural fixes, then content, then anti-pattern), or by effort (quick wins first to build momentum).

3. **Remediation Templates:** Standardized prose templates for each diagnostic code that expand the terse `remediation` field into actionable guidance. For example, `E001-NO_H1_TITLE` currently says "Add an H1 title as the first line." The template version might say: "Your `llms.txt` file is missing an H1 title — this is the first thing an LLM parser looks for, and without it, the file cannot be identified. Add a line starting with `# ` followed by your project name as the very first line of the file. Example: `# MyProject`."

4. **Dependency-Aware Sequencing:** Some fixes are prerequisite to others. Fixing E001 (no H1 title) is a prerequisite for W009 (no Master Index) because the Master Index check assumes basic structural validity. The framework needs a dependency graph (or at minimum, a dependency matrix) that ensures the playbook doesn't tell users to fix downstream issues before upstream ones.

5. **Scope Boundary for Tier 3 vs. Tier 4:** The remediation framework covers Tier 3 (generic playbook). Tier 4 (audience-adapted) adds contextual intelligence on top. This spec must clearly define where Tier 3 ends and Tier 4 begins, so the framework doesn't overreach into domain-specific territory that isn't ready yet.

### Why This Comes Second

The Output Tier Specification (Deliverable 1) defines *that* Tier 3 exists and what data it requires. The Remediation Framework defines *how* Tier 3 works internally. Without Deliverable 1's tier definitions, we don't know the boundaries of what this framework needs to produce.

### Exit Criteria

- [ ] Priority model defined with ranked factors and tie-breaking rules
- [ ] Grouping strategy specified with at least two modes (e.g., by-level, by-effort)
- [ ] At least 5 remediation templates written as examples spanning E/W/I severity, with storage/reference mechanism defined (inline, external YAML, or registry-embedded)
- [ ] Dependency graph or matrix for the 38 existing diagnostic codes
- [ ] Tier 3 / Tier 4 boundary explicitly drawn
- [ ] Reviewed against existing `DiagnosticCode.remediation` fields for consistency

---

## Deliverable 3: Unified Rule Registry Design Specification

**Priority:** HIGH — Required before Deliverable 4 (Profiles) and Deliverable 5 (Report Generation)
**Suggested Identifier:** `RR-SPEC-v0.1.3-unified-rule-registry.md`
**Estimated Scope:** Medium (design spec with schema definition)
**Depends On:** Deliverable 1 (Output Tier Specification)
**Feeds Into:** Deliverables 4, 5

### Description

The validation engine currently distributes its rule definitions across multiple locations: 38 diagnostic codes in `diagnostics.py`, 28 anti-patterns in `constants.py`, 5 validation levels in `validation.py`, 5 ecosystem health dimensions in `ecosystem.py`, and 30 validation criteria in the ASoT `criteria/` directory. That's approximately 70+ discrete validation concerns (with ~146 total standard elements in the ASoT) spread across code modules and documentation files.

At the schema level, this distribution is clean — each concern lives in its natural module. But when a maintainer asks "what does CHECK-042 actually do, and where does it run?", they need a single point of truth that connects the rule *definition* (the ASoT standard file) to its *implementation* (the Python function that executes it), its *pipeline stage* (which of the 5 stages runs it), and its *dependencies* (other checks that must pass first).

The Rule Registry is that single point of truth. It is the "Master Index" for validation rules — the same pattern that `llms.txt` uses for documentation sections, applied reflexively to the validation engine itself.

The spec must define:

1. **Registry Schema:** A Pydantic model (or family of models) that represents a single registered rule. Proposed fields include:
   - `rule_id` — The stable DS-prefixed identifier (e.g., `DS-VC-STR-001`)
   - `diagnostic_codes` — List of diagnostic codes this rule can emit (e.g., `[E001, W009]`)
   - `validation_level` — Which L0–L4 level this rule belongs to
   - `pipeline_stage` — Which of the 5 (soon to be 6) pipeline stages executes this rule
   - `implemented_in` — Module path to the implementing function (e.g., `docstratum.pipeline.per_file:check_h1_title`)
   - `depends_on` — List of `rule_id` values that must pass before this rule runs
   - `asot_path` — Relative path to the ASoT standard file that defines this rule
   - `status` — DRAFT, RATIFIED, or DEPRECATED (mirrors the ASoT lifecycle)
   - `output_tiers` — Which output tiers (1–4) include this rule's results
   - `tags` — Freeform tags for module/buffet composition (e.g., `["structural", "ecosystem", "quick-lint"]`)

2. **Relationship to DS-MANIFEST:** The ASoT already has a manifest (`DS-MANIFEST.md`) that registers standard elements by DS identifier. The Rule Registry extends this by adding implementation metadata that the manifest doesn't track. The spec must define whether the Rule Registry *replaces* the manifest, *extends* it, or *lives alongside* it as a parallel artifact. (The recommended approach is "extends" — the manifest remains the source of truth for standard definitions, the Rule Registry adds the implementation mapping layer.)

3. **Runtime vs. Documentation:** The Rule Registry could be a static Markdown document (like the manifest), a Python module loaded at startup, or a YAML/TOML file parsed into Pydantic models. The spec must choose and justify the format. Given the project's schema-first philosophy, a Pydantic model that loads from YAML is the likely winner — it's both documentation and executable specification.

4. **Integrity Assertions:** The Rule Registry must be verifiable. Every `diagnostic_code` referenced must exist in `diagnostics.py`. Every `asot_path` must resolve to an actual file. Every `pipeline_stage` must be a valid `PipelineStageId`. These assertions should be expressible as unit tests.

### Why This Comes Third

The Output Tier Specification (Deliverable 1) defines the `output_tiers` field — without knowing what tiers exist, we can't tag rules by tier. The remediation framework (Deliverable 2) informs the `depends_on` field — without a dependency model, we can't express inter-rule dependencies.

### Exit Criteria

- [ ] Registry Pydantic model schema defined with all fields, types, and constraints
- [ ] Relationship to DS-MANIFEST explicitly documented (extends, replaces, or parallel)
- [ ] Format decision made and justified (YAML + Pydantic, static Markdown, or Python module)
- [ ] Integrity assertion specifications written (what must be true for the registry to be valid)
- [ ] At least 5 example registry entries written covering L0–L4 and multiple pipeline stages
- [ ] Reviewed against existing `ANTI_PATTERN_REGISTRY` for pattern consistency

---

## Deliverable 4: Validation Profiles & Module Composition Specification

**Priority:** HIGH — Required before Deliverable 5 (Report Generation)
**Suggested Identifier:** `RR-SPEC-v0.1.3-validation-profiles.md`
**Estimated Scope:** Medium (design spec with profile schema and examples)
**Depends On:** Deliverables 1, 3 (Output Tiers, Rule Registry)
**Feeds Into:** Deliverable 5

### Description

This specification defines the mechanism by which consumers configure *which* validation checks run and *what* output they receive. It resolves the "profiles vs. buffet modules" question by formalizing both as complementary layers of the same system.

The core insight is that **profiles are named module compositions**. A profile is a configuration artifact that specifies which rule modules are active, what severity overrides apply, what the pass/fail thresholds are, and which output tier to produce. A "buffet" selection is simply an anonymous profile defined inline by the consumer.

The spec must address:

1. **Profile Schema:** A Pydantic model representing a validation profile. Proposed fields include:
   - `profile_name` — Human-readable identifier (e.g., `"lint"`, `"ci"`, `"full"`, `"enterprise"`)
   - `description` — What this profile is for and who should use it
   - `max_validation_level` — The highest L0–L4 level to execute (e.g., `L2` for a lint pass)
   - `enabled_stages` — Which pipeline stages to run (e.g., stages 1–2 for single-file, stages 1–5 for ecosystem)
   - `rule_tags_include` — Tags from the Rule Registry that activate rules (e.g., `["structural", "content"]`)
   - `rule_tags_exclude` — Tags that deactivate rules even if included by level (e.g., `["experimental"]`)
   - `severity_overrides` — Map of diagnostic codes to overridden severities (e.g., promote W009 to ERROR for strict mode)
   - `pass_threshold` — Minimum quality score to pass (e.g., `50` for CI, `0` for lint)
   - `output_tier` — Which output tier to produce (1–4)
   - `output_format` — Serialization format for the output (JSON, Markdown, YAML, HTML)

2. **Built-In Profiles:** The spec should define 3–4 preset profiles that cover the most common use cases:
   - **`lint`** — Quick single-file check. L0–L1 only, stages 1–2, Tier 2 output, no score threshold. The "did I break anything obvious?" pass.
   - **`ci`** — CI/CD pipeline gate. L0–L3, stages 1–5, Tier 1 output (exit code), score threshold ≥50. The "is this good enough to merge?" gate.
   - **`full`** — Comprehensive validation. L0–L4, all stages, Tier 3 output (remediation playbook), no gating. The "show me everything" analysis.
   - **`enterprise`** — Audience-adapted. L0–L4, all stages, Tier 4 output, requires additional context input. The "consulting-grade" deliverable. (May be out of scope for v0.2.x.)

3. **Module Composition (The "Buffet"):** Beyond presets, consumers should be able to compose custom profiles by selecting individual rules or rule groups from the Rule Registry using tags. The spec must define:
   - How tags interact (AND vs. OR semantics for `rule_tags_include`)
   - How exclusions override inclusions
   - How custom profiles are loaded (YAML file in the project root? CLI flags? API parameters?)
   - Whether custom profiles can extend built-in profiles (e.g., `"extends": "ci"` with overrides)

4. **Integration with PipelineContext:** The existing `PipelineContext` in `pipeline/stages.py` is where the profile gets injected into the pipeline. The spec must define how `PipelineContext` gains a `profile` field and how each stage reads it to determine what to run.

5. **Profile Discovery:** Where do profiles live? Built-in profiles are part of the package. Custom profiles could be a `.docstratum.yml` file in the project root, a CLI argument, or an API parameter. The spec should define the lookup order and precedence.

### Why This Comes Fourth

The Rule Registry (Deliverable 3) defines the `tags` field that profiles use for module composition. The Output Tier Specification (Deliverable 1) defines the `output_tier` field. Without both, the profile schema is incomplete.

### Exit Criteria

- [ ] Profile Pydantic model schema defined with all fields
- [ ] 3–4 built-in profiles fully specified with all field values
- [ ] Module composition semantics defined (tag interaction, exclusion precedence, inheritance)
- [ ] Custom profile loading mechanism specified (file format, discovery order with explicit precedence rules, CLI integration)
- [ ] Integration point with `PipelineContext` documented
- [ ] At least one example custom profile written showing buffet-style composition

---

## Deliverable 5: Report Generation Stage Specification (Pipeline Stage 6)

**Priority:** MEDIUM — Required before v0.2.x pipeline implementation
**Suggested Identifier:** `RR-SPEC-v0.2.4e-report-generation-stage.md`
**Estimated Scope:** Large (full pipeline stage design spec)
**Depends On:** Deliverables 1, 2, 3, 4 (all prior deliverables)
**Feeds Into:** Deliverable 6 (indirectly, via calibration requirements)

### Description

The current 5-stage ecosystem pipeline (Discovery → Per-File → Relationship → Ecosystem Validation → Ecosystem Scoring) ends at scoring. This specification defines **Stage 6: Report Generation** — a presentation layer that transforms pipeline results into a consumable artifact based on the selected profile's output tier and format.

Stage 6 is architecturally distinct from stages 1–5: it adds no new validation logic. It is a pure transformation layer that takes the accumulated pipeline output and formats it for the consumer. This separation preserves the clean boundary between validation (stages 1–5) and presentation (stage 6).

The spec must define:

1. **Stage 6 Interface:** Like all pipeline stages, Stage 6 must conform to the existing stage interface — it receives a `PipelineContext`, produces a `StageResult`, and can be skipped if the profile doesn't require it (e.g., Tier 1 output might skip report generation entirely and just return an exit code).

2. **Tier-Specific Renderers:** Each output tier requires a different rendering strategy:
   - **Tier 1 Renderer:** Evaluates `ValidationResult.is_valid` against the profile's `pass_threshold` and produces a pass/fail signal. Minimal logic.
   - **Tier 2 Renderer:** Serializes the diagnostic list into the requested format (JSON, Markdown, YAML). Includes code, severity, message, line number, remediation hint, and source file for each diagnostic.
   - **Tier 3 Renderer:** Consumes the Remediation Framework (Deliverable 2) to produce a prioritized action plan. Groups diagnostics, sequences by dependency, adds effort estimates, and formats as a structured report.
   - **Tier 4 Renderer:** Extends Tier 3 with audience-specific context. This renderer likely needs additional input (industry, documentation goals, audience profile) that the pipeline doesn't currently provide. The spec must define how this context gets injected.

3. **Format Serializers:** Independent of the tier, the output can be serialized in multiple formats. The spec should define serializers for:
   - **JSON** — Machine-readable, for CI/CD integration and API consumers
   - **Markdown** — Human-readable, for documentation review workflows
   - **YAML** — Configuration-friendly, for tools that consume structured data
   - **HTML** — Browser-renderable, for the Streamlit demo layer (v0.4.x)

4. **Report Metadata:** Every report should include a metadata header with: ASoT version used, profile name, timestamp, files validated, pipeline stages executed, and total execution time. This provides traceability from the report back to the exact validation configuration that produced it.

5. **Extensibility:** The renderer architecture should allow new tiers and formats to be added without modifying existing code. A registry pattern (similar to the Rule Registry) where renderers register themselves by tier and format is the likely approach.

### Why This Comes Fifth

Stage 6 is the synthesis point where all prior deliverables converge. It consumes: the tier definitions (Deliverable 1), the remediation framework (Deliverable 2), the rule metadata from the registry (Deliverable 3), and the profile configuration (Deliverable 4). It cannot be designed without all four.

### Exit Criteria

- [ ] Stage 6 interface defined conforming to existing `StageResult` / `PipelineContext` patterns
- [ ] Tier-specific renderer specifications for Tiers 1–3 (Tier 4 can be stubbed)
- [ ] Format serializer specifications for JSON, Markdown, YAML (HTML deferred to v0.4.x)
- [ ] Report metadata schema defined
- [ ] Extensibility mechanism specified (renderer registration pattern)
- [ ] Integration with the existing 5-stage pipeline documented (sequencing, skip conditions)
- [ ] Reviewed against existing `orchestrator.py` for compatibility

---

## Deliverable 6: Ecosystem Scoring Calibration Document

**Priority:** MEDIUM — Required before ecosystem scoring is trusted in production
**Suggested Identifier:** `RR-SPEC-v0.1.3-ecosystem-scoring-calibration.md`
**Estimated Scope:** Large (calibration methodology, specimen analysis, weight justification)
**Depends On:** Deliverables 1, 5 (Output Tiers, Report Generation — to know how scores are presented)
**Feeds Into:** ASoT ecosystem health standard files (DS-EH-*)

### Description

The single-file quality scoring system (Structural 30%, Content 50%, Anti-Pattern 20%) is well-calibrated — it was validated against 450+ real-world projects, and 6 calibration specimens (DS-CS-001 through DS-CS-006) provide anchored expected scores at each grade level.

The ecosystem-level scoring system has 5 health dimensions (Coverage, Consistency, Completeness, Token Efficiency, Freshness) defined in the ASoT (DS-EH-COV through DS-EH-FRESH), but **lacks equivalent calibration evidence**. The dimension weights, grade boundaries, and expected score distributions for "healthy" vs. "degraded" ecosystems have not been empirically validated.

This document provides that calibration by paralleling the methodology used for single-file scoring:

1. **Dimension Weight Justification:** For each of the 5 ecosystem health dimensions, document:
   - What the dimension measures and why it matters for LLM consumption
   - The proposed weight (as a percentage of the total ecosystem score)
   - The evidence basis for that weight (empirical data, expert judgment, or theoretical reasoning)
   - Known edge cases where the weight may not apply (e.g., single-file ecosystems where Coverage is meaningless)

2. **Calibration Specimens:** Identify or construct at least 4 ecosystem specimens spanning the grade range:
   - One EXEMPLARY ecosystem (multi-file, well-linked, consistent)
   - One STRONG ecosystem (minor gaps but fundamentally sound)
   - One NEEDS_WORK ecosystem (significant structural or content issues)
   - One CRITICAL ecosystem (broken links, orphaned files, inconsistencies)
   - For each specimen, document the expected total score, per-dimension scores, and the reasoning that links the ecosystem's characteristics to its scores

3. **Grade Boundary Calibration:** Do the same grade thresholds used for single-file scoring (EXEMPLARY ≥90, STRONG ≥70, ADEQUATE ≥50, NEEDS_WORK ≥30, CRITICAL <30) apply at the ecosystem level? Or do ecosystem scores naturally distribute differently, requiring adjusted boundaries? The calibration document must propose grade boundaries and justify them against the specimen analysis.

4. **Interaction with Single-File Scores:** An ecosystem contains multiple files, each with its own quality score. How do individual file scores roll up into the ecosystem score? Is the ecosystem score purely a function of the 5 health dimensions, or do per-file quality scores contribute directly? The current model (`EcosystemScore` has a `per_file_scores` field) suggests both are tracked, but the aggregation formula isn't defined.

5. **Sensitivity Analysis:** If a single file in a 10-file ecosystem has a CRITICAL quality score, how much does that drag down the ecosystem score? The calibration document should include sensitivity scenarios that help maintainers understand how individual file quality affects ecosystem health.

### Why This Comes Last

Calibration depends on knowing how scores are consumed (Deliverable 1) and how they're presented in reports (Deliverable 5). Calibrating a scoring system that nobody knows how to read or act on is premature optimization. Additionally, the calibration specimens may need to be constructed as test fixtures, and the fixture format depends on decisions made in Deliverables 3–5.

### Exit Criteria

- [ ] All 5 ecosystem health dimensions have documented weights with evidence basis
- [ ] At least 4 calibration specimens defined with expected total and per-dimension scores
- [ ] Grade boundaries proposed and justified (same as single-file or adjusted)
- [ ] Aggregation formula defined (how per-file scores interact with ecosystem dimensions)
- [ ] At least 2 sensitivity scenarios documented
- [ ] Reviewed against existing DS-EH-* standard files for consistency
- [ ] Reviewed against existing DS-CS-* calibration specimens for methodological alignment

---

## Summary Table

| # | Deliverable | Priority | Identifier | Depends On | Feeds Into |
|---|-------------|----------|------------|------------|------------|
| 1 | Output Tier Specification | CRITICAL | `RR-SPEC-v0.1.3-output-tier-specification.md` | — | 2, 3, 4, 5 |
| 2 | Remediation Framework | HIGH | `RR-SPEC-v0.1.3-remediation-framework.md` | 1 | 5 |
| 3 | Unified Rule Registry | HIGH | `RR-SPEC-v0.1.3-unified-rule-registry.md` | 1 | 4, 5 |
| 4 | Validation Profiles & Module Composition | HIGH | `RR-SPEC-v0.1.3-validation-profiles.md` | 1, 3 | 5 |
| 5 | Report Generation Stage (S6) | MEDIUM | `RR-SPEC-v0.2.4e-report-generation-stage.md` | 1, 2, 3, 4 | 6 |
| 6 | Ecosystem Scoring Calibration | MEDIUM | `RR-SPEC-v0.1.3-ecosystem-scoring-calibration.md` | 1, 5 | ASoT DS-EH-* |

---

## Parallelization Notes

While the dependency chain is strictly sequential at the design level, some work can proceed in parallel:

- **Deliverables 2 and 3 can be drafted concurrently** after Deliverable 1 is complete, since they don't depend on each other directly. Deliverable 2 (Remediation) informs the `depends_on` field in Deliverable 3 (Rule Registry), but this field can be stubbed during initial drafting and back-filled.
- **Deliverable 6 (Calibration) can begin specimen collection** while Deliverables 3–5 are being written, since the calibration methodology is largely independent of the pipeline architecture. The specimen *format* depends on pipeline decisions, but the *analysis* of real-world ecosystems does not.

---

## Relationship to Existing Documentation

This backlog does **not** supersede or replace any existing design specifications. It identifies new deliverables that fill gaps between the completed ASoT standards library (v1.0.0) and the upcoming pipeline implementation phases (v0.2.x–v0.3.x).

The deliverables integrate into the existing documentation tree as follows:

- Deliverables 1–4 and 6 are `v0.1.3` specs, extending the Foundation phase with pre-implementation design work
- Deliverable 5 is a `v0.2.4e` spec, extending the existing Data Preparation validation pipeline specs (v0.2.4a–d) with a sixth stage

All deliverables follow the established naming convention (`RR-SPEC-{version}-{slug}.md`) and will be tracked in the CHANGELOG upon completion.

---

## Decision Points Requiring Future Resolution

Several open questions emerged during the architectural review that this backlog captures but does not resolve. These will be addressed within the relevant deliverable:

1. **Profiles vs. Buffet — Interaction Semantics (Deliverable 4):** When a profile includes tags via `rule_tags_include` and the consumer also specifies individual rule exclusions, what takes precedence? AND semantics? OR semantics? This is a design decision that Deliverable 4 must make.

2. **Tier 4 Context Injection (Deliverables 1, 5):** Tier 4 (audience-adapted recommendations) requires domain context that the pipeline doesn't produce. How does this context enter the system? CLI argument? Configuration file? API parameter? This is a design decision that Deliverable 1 scopes and Deliverable 5 implements.

3. **Rule Registry Format (Deliverable 3):** YAML + Pydantic (documentation and code), pure Python module (code only), or extended DS-MANIFEST (documentation only)? Each has trade-offs. Deliverable 3 must make this call.

4. **Ecosystem Calibration Methodology (Deliverable 6):** The single-file calibration used real-world projects. Ecosystem calibration may need to use constructed specimens (since real-world multi-file `llms.txt` ecosystems are rare). Is synthetic calibration acceptable, or do we need to find real examples? Deliverable 6 must address this.

---

*This document is maintained as part of the DocStratum project's docs-first development methodology. It should be updated as deliverables are completed, new gaps are identified, or priorities shift.*
