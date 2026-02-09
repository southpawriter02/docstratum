# v0.1.3 — Output Tier Specification

> **Status:** DRAFT
> **Created:** 2026-02-09
> **Last Updated:** 2026-02-09
> **Governed By:** RR-META-documentation-backlog.md (Deliverable 1)
> **Depends On:** None — this is the root dependency for the ecosystem validator architecture
> **Feeds Into:** Deliverables 2 (Remediation Framework), 3 (Rule Registry), 4 (Profiles), 5 (Report Generation Stage)
> **ASoT Version:** 1.0.0
> **Traces To:** FR-004 (error reporting), NFR-006 (CLI output format), v0.2.4d (Pipeline Orchestration & Reporting)

---

## 1. Purpose

This specification defines the **output contract** of the DocStratum validation engine — what the consumer of a validation run actually receives. It is the authoritative answer to the question: "When I validate my `llms.txt` ecosystem, what do I get back?"

The current pipeline (5-stage ecosystem pipeline per v0.0.7) ends at Stage 5 (Ecosystem Scoring), which produces an `EcosystemScore` model. The existing v0.2.4d spec defines CLI output formatters (terminal, JSON, Markdown, HTML) for single-file validation. Neither document answers the higher-order question: **what level of analysis does the consumer receive, and how does it scale from a CI exit code to a consulting-grade remediation plan?**

This specification fills that gap by defining four output tiers, each serving a different audience and use case. Every downstream design deliverable — the Remediation Framework, the Rule Registry, the Validation Profiles, and the Report Generation Stage — references this document as the authoritative definition of what the pipeline produces.

### 1.1 Relationship to v0.2.4d

The existing v0.2.4d spec (Pipeline Orchestration & Reporting) defines the CLI interface, output formatters, exit codes, and configuration file format for a single-file validation pipeline. This specification does not supersede v0.2.4d. Instead, it provides the conceptual framework that v0.2.4d's formatters implement. Where v0.2.4d asks "how do we format the output?", this document asks "what level of output is appropriate for which consumer?"

Specifically:

- v0.2.4d's **terminal formatter** implements Tier 2 (Diagnostic Report) in human-readable form
- v0.2.4d's **JSON formatter** implements Tier 2 in machine-readable form
- v0.2.4d's **exit codes** (0=valid, 1=schema, 2=content, 3=warnings) implement Tier 1 (Pass/Fail Gate)
- v0.2.4d's **Markdown/HTML formatters** implement Tier 2 with richer presentation

This specification extends v0.2.4d by formalizing these as named tiers, adding two new tiers (Tier 3: Remediation Playbook, Tier 4: Audience-Adapted Recommendations), defining the data contract for each tier, and establishing the format-tier compatibility matrix.

---

## 2. The Four Output Tiers

The DocStratum validation engine produces output at one of four tiers. Each tier represents a progressively richer level of analysis, interpretation, and actionable guidance. Tiers are cumulative — Tier 3 includes everything in Tier 2, which includes everything in Tier 1.

### Tier Inheritance

```
Tier 1: Pass/Fail Gate
   └─ Tier 2: Diagnostic Report (includes Tier 1 data)
        └─ Tier 3: Remediation Playbook (includes Tier 2 data)
             └─ Tier 4: Audience-Adapted Recommendations (includes Tier 3 data)
```

This inheritance means the pipeline always produces the data for lower tiers. A Tier 3 consumer can extract Tier 1 data (the pass/fail signal) from the same pipeline run — they don't need to run the pipeline twice.

---

### 2.1 Tier 1 — Pass/Fail Gate

**Audience:** CI/CD pipelines, automated build systems, pre-commit hooks, GitHub Actions workflows
**Use Case:** "Did this documentation pass validation? Should I block the merge?"
**Interaction Model:** Non-interactive. Consumed by machines. No human reads this output directly.

#### What the Consumer Receives

A binary pass/fail signal with a numeric exit code. This is the simplest possible output — the consumer doesn't need to know *what* failed, only *whether* something failed.

#### Data Requirements

Tier 1 requires only the following data from the pipeline:

| Field | Source Model | Source Field | Description |
|-------|-------------|-------------|-------------|
| `passed` | `ValidationResult` | `.is_valid` (single-file) or threshold comparison (ecosystem) | Boolean: did the validation meet the configured threshold? |
| `exit_code` | Computed | See §2.1.1 | Integer exit code for shell consumption |
| `level_achieved` | `ValidationResult` | `.level_achieved` | Highest L0–L4 level where all checks pass |
| `total_score` | `QualityScore` / `EcosystemScore` | `.total_score` | Numeric 0–100 score (for threshold comparison) |
| `grade` | `QualityScore` / `EcosystemScore` | `.grade` | Quality grade enum value |
| `file_count` | `PipelineContext` | `len(.files)` | Number of files validated (ecosystem mode) |
| `error_count` | `ValidationResult` | `.total_errors` | Count of ERROR-severity diagnostics |
| `warning_count` | `ValidationResult` | `.total_warnings` | Count of WARNING-severity diagnostics |

#### 2.1.1 Exit Code Convention

Exit codes communicate the highest-severity issue encountered. They are an extension of the convention established in v0.2.4d §5:

| Exit Code | Meaning | Maps To |
|-----------|---------|---------|
| `0` | All checks pass at the configured threshold | `passed == True` |
| `1` | Structural errors (L0–L1 failures) | At least one E-severity diagnostic from L0 or L1 |
| `2` | Content errors (L2 failures) | At least one E-severity diagnostic from L2 |
| `3` | Best practice warnings (L3 failures) | At least one W-severity diagnostic from L3 |
| `4` | Ecosystem-level errors (E009, E010) | At least one ecosystem-level E-severity diagnostic |
| `5` | Score below configured threshold | `total_score < pass_threshold` |
| `10` | Internal pipeline error | Unhandled exception in any pipeline stage |

Exit codes are ordered by severity. If multiple conditions are true, the lowest exit code (highest severity) wins.

#### Pipeline Stages Required

**Minimum:** Stages 1–2 (Discovery + Per-File) for single-file Tier 1 output
**Full ecosystem:** Stages 1–5 (all stages) for ecosystem Tier 1 output with score threshold

Stage 6 (Report Generation) is technically not required for Tier 1 — the exit code can be computed directly from `PipelineContext` without a renderer. However, for consistency, Tier 1 output should flow through the same Stage 6 code path so that report metadata (ASoT version, timestamp, profile name) is captured.

---

### 2.2 Tier 2 — Diagnostic Report

**Audience:** Documentation maintainers, technical writers, developers reviewing their own `llms.txt` files
**Use Case:** "What's wrong with my documentation, and where exactly is each issue?"
**Interaction Model:** Semi-interactive. A human reads this output and acts on it. May be printed to terminal, saved to a file, or displayed in a code review interface.

#### What the Consumer Receives

A structured list of every validation finding, with enough context to locate and understand each issue. Think of it as compiler output: each entry identifies the file, line, severity, and a brief description. The consumer is expected to have enough domain knowledge to act on the findings without additional guidance about prioritization or sequencing.

#### Data Requirements

Tier 2 includes all Tier 1 data plus the following:

| Field | Source Model | Source Field | Description |
|-------|-------------|-------------|-------------|
| `diagnostics` | `ValidationResult` | `.diagnostics` | Full list of `ValidationDiagnostic` objects |
| Per diagnostic: `code` | `ValidationDiagnostic` | `.code` | DiagnosticCode enum value (e.g., `E001`, `W003`) |
| Per diagnostic: `severity` | `ValidationDiagnostic` | `.severity` | ERROR, WARNING, or INFO |
| Per diagnostic: `message` | `ValidationDiagnostic` | `.message` | Human-readable description |
| Per diagnostic: `remediation` | `ValidationDiagnostic` | `.remediation` | Brief fix suggestion |
| Per diagnostic: `line_number` | `ValidationDiagnostic` | `.line_number` | Source line (1-indexed) |
| Per diagnostic: `column` | `ValidationDiagnostic` | `.column` | Source column (1-indexed), if applicable |
| Per diagnostic: `context` | `ValidationDiagnostic` | `.context` | Source text snippet (≤500 chars) |
| Per diagnostic: `level` | `ValidationDiagnostic` | `.level` | Which L0–L4 level this belongs to |
| Per diagnostic: `check_id` | `ValidationDiagnostic` | `.check_id` | Cross-reference to ASoT check ID |
| Per diagnostic: `source_file` | `ValidationDiagnostic` | `.source_file` | [Ecosystem] Which file emitted this |
| Per diagnostic: `related_file` | `ValidationDiagnostic` | `.related_file` | [Ecosystem] Cross-file reference target |
| `levels_passed` | `ValidationResult` | `.levels_passed` | Per-level pass/fail map |
| `quality_dimensions` | `QualityScore` | `.dimensions` | Per-dimension score breakdown |
| `ecosystem_dimensions` | `EcosystemScore` | `.dimensions` | Per-dimension ecosystem health breakdown |
| `per_file_scores` | `EcosystemScore` | `.per_file_scores` | Map of file → quality score |
| `relationships` | `PipelineContext` | `.relationships` | Cross-file relationship graph |

#### Diagnostic Presentation Order

Diagnostics in Tier 2 are presented in a deterministic order for readability:

1. **Group by file** — In ecosystem mode, group all diagnostics for a file together
2. **Within each file, sort by severity** — ERROR first, then WARNING, then INFO
3. **Within each severity, sort by line number** — Top of file to bottom
4. **Within same line, sort by code** — Alphanumeric order (E001 before E002)

This ordering is a presentation concern, not a data concern. The underlying `diagnostics` list may be in any order; the Tier 2 renderer sorts for display.

#### Pipeline Stages Required

**Minimum:** Stages 1–2 (single-file diagnostics)
**Recommended:** Stages 1–5 (full ecosystem with cross-file diagnostics and scoring)

---

### 2.3 Tier 3 — Remediation Playbook

**Audience:** Documentation teams, project leads, stakeholders evaluating documentation health, consultants performing documentation audits
**Use Case:** "My documentation scored 47/100. What should I do about it, in what order, and how long will it take?"
**Interaction Model:** Fully interactive. A human (potentially non-technical) reads this as a report and uses it to plan work. May be shared with teams, attached to project planning tools, or presented in meetings.

#### What the Consumer Receives

A prioritized action plan that transforms the raw diagnostic output into a sequenced, grouped, effort-estimated set of remediation steps. Where Tier 2 says "here's what's wrong," Tier 3 says "here's what to do about it, starting with this, then this, and here's why."

The playbook is *not* a raw dump of diagnostics with nicer formatting. It is an *interpreted* artifact that adds three layers of intelligence on top of Tier 2:

1. **Prioritization** — Diagnostics are ranked by impact, not just severity. A W009 (no Master Index) with an 87% vs. 31% LLM success rate impact is more important than a W005 (code block missing language specifier), even though both are WARNING severity.

2. **Grouping** — Related diagnostics are consolidated into logical action items. If a file has W003 (link missing description) on 15 different links, the playbook presents this as a single action item ("Add descriptions to 15 bare links in llms.txt") rather than 15 separate findings.

3. **Sequencing** — Action items are ordered by dependency. Structural fixes (L0–L1) come before content fixes (L2–L3) because structural failures may mask content issues. Within a level, quick wins (single-line fixes) are sequenced before structural rework.

#### Data Requirements

Tier 3 includes all Tier 2 data plus the following:

| Field | Source | Description |
|-------|--------|-------------|
| `action_items` | Remediation Framework (Deliverable 2) | Prioritized, grouped, sequenced list of remediation steps |
| Per action: `priority` | Computed | CRITICAL, HIGH, MEDIUM, LOW — based on impact, not just severity |
| Per action: `group_label` | Computed | Human-readable category (e.g., "Structural Fixes", "Content Enrichment") |
| Per action: `description` | Remediation template | Expanded prose guidance (beyond the terse `remediation` hint) |
| Per action: `affected_diagnostics` | Cross-reference | Which diagnostic codes this action resolves |
| Per action: `effort_estimate` | Heuristic | Estimated effort: QUICK_WIN (minutes), MODERATE (hours), STRUCTURAL (days) |
| Per action: `score_impact` | Computed | Estimated score increase if this action is completed |
| Per action: `dependency` | Dependency graph | Which other actions must be completed first |
| `executive_summary` | Computed | 2–3 sentence overview of documentation health and top priorities |
| `score_projection` | Computed | Estimated score if all CRITICAL and HIGH actions are completed |
| `anti_patterns_detected` | `ANTI_PATTERN_REGISTRY` cross-ref | Named anti-patterns found, with descriptions |

#### Grouping Modes

The playbook supports multiple grouping strategies. The default is by-priority, but profiles can override this:

| Mode | Groups By | Best For |
|------|-----------|----------|
| `by-priority` (default) | CRITICAL → HIGH → MEDIUM → LOW | General-purpose remediation planning |
| `by-level` | L0 → L1 → L2 → L3 → L4 | Developers who think in validation levels |
| `by-file` | Per-file action groups | Multi-file ecosystems where ownership varies |
| `by-effort` | QUICK_WIN → MODERATE → STRUCTURAL | Sprint planning, "what can we fix this week?" |

#### Effort Estimation Heuristics

Effort estimates are coarse-grained by design — they communicate relative effort, not precise time commitments. The heuristics are:

| Effort | Criteria | Examples |
|--------|----------|---------|
| `QUICK_WIN` | Single-line or single-field change, no structural impact | Add missing blockquote (W001), fix code block language (W005), add version metadata (W007) |
| `MODERATE` | Multi-line changes within a single file, localized impact | Write link descriptions for a section (W003), add code examples (W004), reorder sections (W008) |
| `STRUCTURAL` | Architectural changes affecting multiple files or requiring new content | Create Master Index (W009), decompose monolith (E008), create llms-full.txt (W013), resolve orphaned files (E010) |

#### Score Impact Estimation

Each action item carries an estimated score impact — how many points the quality score would increase if this action were completed. This is a projection, not a guarantee.

The estimation works by mapping each resolved diagnostic to its scoring dimension and weight:

1. Identify which `QualityDimension` or `EcosystemHealthDimension` the diagnostic affects
2. Look up the dimension's maximum points (e.g., Structural = 30 points)
3. Calculate the per-check weight within that dimension (e.g., 30 points ÷ 20 structural checks = 1.5 points per check)
4. Sum the per-check weights for all diagnostics resolved by this action

This produces a reasonable estimate without requiring a full pipeline re-run.

#### Pipeline Stages Required

**Required:** Stages 1–5 (full ecosystem pipeline). Tier 3 cannot be produced from partial pipeline runs because it needs quality scores, ecosystem scores, and the relationship graph to compute priorities, groupings, and score projections.

**Stage 6:** The Tier 3 renderer in Stage 6 consumes the Remediation Framework (Deliverable 2) to transform diagnostics into action items.

---

### 2.4 Tier 4 — Audience-Adapted Recommendations

**Audience:** Enterprise customers, consulting engagements, organizations evaluating documentation maturity across multiple projects
**Use Case:** "We're a developer tools company with 12 API endpoints. How should we prioritize our documentation strategy for AI consumption?"
**Interaction Model:** Deliverable-grade report. Shared with leadership, attached to SOWs, used in documentation strategy planning. May be PDF or polished HTML.

#### What the Consumer Receives

Everything in Tier 3, plus contextual intelligence that tailors the recommendations to the consumer's specific domain, documentation goals, and audience. Where Tier 3 says "add a Master Index section," Tier 4 says "as an API-heavy product, your Master Index should prioritize endpoint groupings and authentication flow — here's an example structure based on similar projects that scored EXEMPLARY."

#### Data Requirements

Tier 4 includes all Tier 3 data plus the following:

| Field | Source | Description |
|-------|--------|-------------|
| `context_profile` | Consumer-provided input | Domain, industry, documentation goals, audience, project size |
| `comparative_analysis` | Calibration specimens + registry | How this ecosystem compares to similar projects in the calibration set |
| `domain_recommendations` | Context-aware generator | Recommendations tailored to the consumer's industry and use case |
| `exemplar_references` | Calibration specimens | Specific examples from high-scoring projects in similar domains |
| `maturity_assessment` | Computed | Documentation maturity level relative to industry benchmarks |
| `roadmap` | Computed | Phased improvement plan (30/60/90 day) with milestones and expected score progression |

#### Context Profile Schema

Tier 4 requires additional input that the pipeline does not produce. This input is provided by the consumer (or pre-configured in the profile):

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `industry` | `str` | Domain category | `"developer_tools"`, `"fintech"`, `"healthcare"` |
| `project_type` | `str` | What the project is | `"api_service"`, `"sdk"`, `"cli_tool"`, `"framework"` |
| `documentation_goals` | `list[str]` | What the documentation should achieve | `["enable_api_integration", "reduce_support_tickets"]` |
| `target_audience` | `list[str]` | Who reads the documentation | `["developers", "devops", "data_scientists"]` |
| `estimated_project_size` | `str` | Rough size | `"small"` (<10 endpoints), `"medium"` (10–50), `"large"` (50+) |
| `comparison_set` | `list[str]` | Projects to compare against | `["stripe", "twilio", "pydantic"]` |

#### Scope Boundary: Tier 3 vs. Tier 4

The boundary between Tier 3 and Tier 4 is defined by **whether the recommendation requires knowledge external to the pipeline output**.

- **Tier 3** uses only pipeline-internal data: diagnostics, scores, the relationship graph, and the ASoT standards library. Any recommendation that can be derived from these sources belongs in Tier 3.
- **Tier 4** uses pipeline-external data: the consumer's industry, goals, audience, and comparative benchmarks. Any recommendation that requires this context belongs in Tier 4.

This boundary is important because Tier 3 is fully automatable — it can be produced by the pipeline without human intervention. Tier 4 requires human input (the context profile) and may benefit from human review of the generated recommendations.

#### Pipeline Stages Required

**Required:** Stages 1–5 plus the Tier 4-specific context injection mechanism.
**Stage 6:** The Tier 4 renderer is an extension of the Tier 3 renderer that overlays the context profile onto the remediation playbook.

---

## 3. Pipeline Stage → Tier Data Mapping

This section formally maps which pipeline stages produce the data required by each tier. This is the **data contract** — the guarantee that the pipeline provides what each tier needs.

### 3.1 Stage Output Summary

| Stage | Pipeline Stage ID | Primary Output | Model |
|-------|-------------------|---------------|-------|
| S1: Discovery | `PipelineStageId.DISCOVERY` | File manifest | `list[EcosystemFile]` (with `file_path`, `file_type`, `classification`) |
| S2: Per-File | `PipelineStageId.PER_FILE` | Per-file validation + quality | `EcosystemFile.parsed`, `.validation`, `.quality` |
| S3: Relationship | `PipelineStageId.RELATIONSHIP` | Cross-file link graph | `list[FileRelationship]` |
| S4: Ecosystem Validation | `PipelineStageId.ECOSYSTEM_VALIDATION` | Ecosystem diagnostics | `list[ValidationDiagnostic]` (ecosystem-level codes E009–E010, W012–W018, I008–I010) |
| S5: Scoring | `PipelineStageId.SCORING` | Ecosystem health score | `EcosystemScore` (total_score, grade, dimensions, per_file_scores) |
| S6: Report Generation | (new, Deliverable 5) | Formatted output | Tier-specific artifact (see §4) |

### 3.2 Tier → Stage Dependency Matrix

This matrix shows which stages each tier **requires** (must have run successfully) and which are **optional** (enhance the output but aren't strictly necessary).

| | S1 Discovery | S2 Per-File | S3 Relationship | S4 Eco Validation | S5 Scoring | S6 Report Gen |
|--|:--:|:--:|:--:|:--:|:--:|:--:|
| **Tier 1** (Pass/Fail) | REQUIRED | REQUIRED | optional | optional | optional | optional |
| **Tier 2** (Diagnostic) | REQUIRED | REQUIRED | REQUIRED | REQUIRED | REQUIRED | REQUIRED |
| **Tier 3** (Playbook) | REQUIRED | REQUIRED | REQUIRED | REQUIRED | REQUIRED | REQUIRED |
| **Tier 4** (Adapted) | REQUIRED | REQUIRED | REQUIRED | REQUIRED | REQUIRED | REQUIRED |

**Notes on Tier 1 optionality:**

- Tier 1 with only S1–S2 produces a single-file pass/fail based on `ValidationResult.is_valid`. This is sufficient for a pre-commit hook that checks basic structural validity.
- Tier 1 with S1–S5 produces an ecosystem-level pass/fail based on `EcosystemScore.total_score >= pass_threshold`. This is needed for CI/CD gates that enforce minimum quality scores.
- The profile (Deliverable 4) controls which stages run. A `lint` profile running Tier 1 may skip S3–S5. A `ci` profile running Tier 1 may include S3–S5 for score-based gating.

### 3.3 Data Flow Diagram

```
S1: Discovery
│  Output: files[]
│          ├── file_path
│          ├── file_type
│          └── classification
▼
S2: Per-File
│  Output: files[] enriched with:
│          ├── .parsed (ParsedLlmsTxt)
│          ├── .validation (ValidationResult)
│          │   ├── .level_achieved ──────────────────► Tier 1: exit_code
│          │   ├── .is_valid ────────────────────────► Tier 1: passed
│          │   ├── .diagnostics[] ───────────────────► Tier 2: diagnostic list
│          │   │   └── per item: code, severity,
│          │   │       message, remediation,
│          │   │       line_number, context
│          │   ├── .total_errors ────────────────────► Tier 1: error_count
│          │   └── .total_warnings ──────────────────► Tier 1: warning_count
│          └── .quality (QualityScore)
│              ├── .total_score ─────────────────────► Tier 1: total_score
│              ├── .grade ───────────────────────────► Tier 1: grade
│              └── .dimensions ──────────────────────► Tier 2: quality_dimensions
▼
S3: Relationship
│  Output: relationships[]
│          ├── source_file_id
│          ├── target_file_id
│          ├── relationship_type ────────────────────► Tier 2: relationships
│          ├── target_url
│          └── is_resolved
▼
S4: Ecosystem Validation
│  Output: ecosystem_diagnostics[]
│          └── (E009–E010, W012–W018, I008–I010) ──► Tier 2: diagnostics (appended)
▼
S5: Scoring
│  Output: ecosystem_score
│          ├── .total_score ─────────────────────────► Tier 1: total_score (ecosystem)
│          ├── .grade ───────────────────────────────► Tier 1: grade (ecosystem)
│          ├── .dimensions ──────────────────────────► Tier 2: ecosystem_dimensions
│          ├── .per_file_scores ─────────────────────► Tier 2: per_file_scores
│          ├── .relationship_count
│          └── .broken_relationships
▼
S6: Report Generation
│  Input: PipelineContext (all accumulated data)
│  Input: Profile configuration (output_tier, output_format)
│  Input: [Tier 4 only] Context profile
│  Output: Tier-specific artifact
│          ├── Tier 1: exit_code + summary JSON
│          ├── Tier 2: diagnostic report
│          ├── Tier 3: remediation playbook ─────────► Requires Remediation Framework
│          └── Tier 4: audience-adapted report ──────► Requires context profile
```

---

## 4. Output Formats

Each tier can be serialized in multiple formats. Not all formats are appropriate for all tiers — the compatibility matrix below defines valid combinations.

### 4.1 Format Definitions

#### JSON (Machine-Readable)

Structured JSON output suitable for consumption by CI/CD tools, dashboards, APIs, and other programs. All model fields are serialized using Pydantic's `.model_dump(mode="json")` conventions: enums as string values, datetimes as ISO 8601 strings, UUIDs as strings.

**MIME type:** `application/json`
**File extension:** `.json`

#### Markdown (Human-Readable Document)

A Markdown document suitable for inclusion in pull requests, project documentation, or reading in any Markdown renderer. Uses standard CommonMark with GFM tables. Does not include interactive elements.

**MIME type:** `text/markdown`
**File extension:** `.md`

#### YAML (Configuration-Friendly)

Structured YAML output suitable for piping into other tools, storing as configuration artifacts, or processing with YAML-aware tooling. Follows the same field structure as JSON but in YAML syntax.

**MIME type:** `application/x-yaml`
**File extension:** `.yaml`

#### HTML (Browser-Renderable)

A self-contained HTML document with embedded CSS for visual presentation. Intended for the Streamlit demo layer (v0.4.x) and for sharing reports via browser. May include interactive elements (collapsible sections, score gauges) in the v0.4.x implementation.

**MIME type:** `text/html`
**File extension:** `.html`

#### Terminal (Interactive CLI)

Colored terminal output using ANSI escape codes. Not a file format — streamed to stdout. Includes progress indicators for long-running validation. Follows the v0.2.4d terminal formatter conventions.

**MIME type:** N/A (stdout only)
**File extension:** N/A

### 4.2 Format-Tier Compatibility Matrix

This matrix defines which format-tier combinations are valid. "Primary" means this is the default or most natural format for this tier. "Supported" means the combination is valid but not the default. "Not Supported" means the combination is architecturally inappropriate.

| | JSON | Markdown | YAML | HTML | Terminal |
|--|:--:|:--:|:--:|:--:|:--:|
| **Tier 1** (Pass/Fail) | **Primary** | Not Supported | Supported | Not Supported | Supported |
| **Tier 2** (Diagnostic) | **Primary** | Supported | Supported | Supported | **Primary** |
| **Tier 3** (Playbook) | Supported | **Primary** | Not Supported | Supported | Not Supported |
| **Tier 4** (Adapted) | Supported | Supported | Not Supported | **Primary** | Not Supported |

**Rationale for "Not Supported" entries:**

- **Tier 1 + Markdown/HTML:** A pass/fail signal doesn't warrant a document. The consumer wants an exit code, not a report.
- **Tier 3 + YAML:** A remediation playbook is prose with structure, not data. YAML serialization of prose action items would be semantically awkward and unhelpful.
- **Tier 3 + Terminal:** Playbooks are too long for terminal output. The consumer should save to a file.
- **Tier 4 + YAML:** Same rationale as Tier 3 + YAML — audience-adapted recommendations are narrative documents, not configuration data.
- **Tier 4 + Terminal:** Same rationale as Tier 3 + Terminal.

### 4.3 Default Formats by Profile

Profiles (Deliverable 4) will define default output tiers and formats. For reference, the anticipated defaults are:

| Profile | Default Tier | Default Format |
|---------|-------------|----------------|
| `lint` | Tier 2 | Terminal |
| `ci` | Tier 1 | JSON |
| `full` | Tier 3 | Markdown |
| `enterprise` | Tier 4 | HTML |

These defaults are overridable by the consumer. A CI pipeline using the `ci` profile could request Tier 2 + JSON if it wants diagnostics, not just pass/fail.

---

## 5. Report Metadata Schema

Every output artifact (regardless of tier or format) includes a metadata header that provides traceability from the report back to the exact pipeline configuration that produced it.

### 5.1 Metadata Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `report_id` | `str` (UUID4) | Unique identifier for this report | `"a1b2c3d4-e5f6-7890-abcd-ef1234567890"` |
| `asot_version` | `str` (semver) | ASoT version used for validation | `"1.0.0"` |
| `engine_version` | `str` (semver) | DocStratum engine version | `"0.2.0"` |
| `profile_name` | `str` | Validation profile used | `"full"` |
| `output_tier` | `int` (1–4) | Which tier was requested | `3` |
| `output_format` | `str` | Serialization format | `"markdown"` |
| `validated_at` | `str` (ISO 8601) | When validation was performed | `"2026-02-09T14:30:00Z"` |
| `root_path` | `str` | Project root or file path that was validated | `"/home/user/project"` |
| `files_validated` | `int` | Number of files processed | `5` |
| `stages_executed` | `list[str]` | Which pipeline stages ran | `["DISCOVERY", "PER_FILE", "RELATIONSHIP", "ECOSYSTEM_VALIDATION", "SCORING"]` |
| `stages_skipped` | `list[str]` | Which pipeline stages were skipped | `[]` |
| `total_duration_ms` | `float` | Total pipeline execution time | `1234.5` |
| `pass_threshold` | `int \| None` | Configured score threshold for pass/fail | `50` |

### 5.2 Metadata Placement by Format

| Format | Metadata Location |
|--------|------------------|
| JSON | Top-level `"metadata"` key in the root object |
| Markdown | YAML frontmatter block at the top of the document |
| YAML | Top-level `metadata` key |
| HTML | `<meta>` tags in `<head>` plus visible header section |
| Terminal | First 3 lines of output (version, profile, timestamp) |

---

## 6. Scope Boundaries

### 6.1 In Scope for v0.2.x–v0.3.x

The following tiers, formats, and features must be implemented during the Data Preparation (v0.2.x) and Logic Core (v0.3.x) phases:

| Item | Version Target | Notes |
|------|---------------|-------|
| Tier 1 (Pass/Fail Gate) | v0.2.4 | Extension of existing v0.2.4d exit code convention |
| Tier 2 (Diagnostic Report) | v0.2.4 | Extension of existing v0.2.4d formatters |
| Tier 3 (Remediation Playbook) | v0.3.x | Requires Remediation Framework (Deliverable 2) |
| JSON format | v0.2.4 | Primary format for Tiers 1–2 |
| Markdown format | v0.2.4 | Primary format for Tier 3 |
| YAML format | v0.2.4 | Secondary format for Tiers 1–2 |
| Terminal format | v0.2.4 | Primary interactive format for Tier 2 |
| Report metadata | v0.2.4 | All formats include metadata |
| Exit codes (0–10) | v0.2.4 | Extension of v0.2.4d §5 |
| Stage 6 interface definition | v0.3.x | Per Deliverable 5 (Report Generation Stage) |

### 6.2 Deferred to v0.4.x+

The following items are architecturally defined in this spec but will not be implemented until the Demo Layer phase or later:

| Item | Deferred To | Rationale |
|------|------------|-----------|
| Tier 4 (Audience-Adapted) | v0.4.x+ | Requires context profile system and comparative analysis engine |
| HTML format | v0.4.x | Streamlit demo layer handles HTML rendering |
| Tier 4 context profile ingestion | v0.4.x+ | Needs UI or API for context input |
| Comparative analysis against calibration specimens | v0.4.x+ | Depends on calibration document (Deliverable 6) |
| Score projection in Tier 3 | v0.3.x (stretch) | Requires scoring sensitivity model from Deliverable 6 |

### 6.3 Explicitly Out of Scope

| Item | Reason |
|------|--------|
| Real-time streaming validation | Future enhancement — current pipeline is batch-oriented |
| Database persistence of reports | Future optimization — reports are ephemeral artifacts |
| Report diffing (compare two runs) | Future feature — useful but not foundational |
| IDE plugin integration | Different delivery channel — uses Tier 2 data but has its own presentation |
| Webhook/notification delivery | Future CI/CD enhancement |

---

## 7. Model Compatibility Review

This section validates that the four output tiers are compatible with the existing Pydantic models in `src/docstratum/schema/`.

### 7.1 Tier 1 Compatibility

| Required Field | Source | Model Exists? | Field Exists? | Notes |
|---------------|--------|:--:|:--:|-------|
| `passed` | `ValidationResult.is_valid` | YES | YES | Currently checks L0 only; profiles may override threshold |
| `exit_code` | Computed from diagnostics | N/A | N/A | New computation, no model change needed |
| `level_achieved` | `ValidationResult.level_achieved` | YES | YES | Direct mapping |
| `total_score` | `QualityScore.total_score` | YES | YES | Direct mapping |
| `grade` | `QualityScore.grade` | YES | YES | Direct mapping |
| `error_count` | `ValidationResult.total_errors` | YES | YES | Computed property |
| `warning_count` | `ValidationResult.total_warnings` | YES | YES | Computed property |

**Verdict:** Tier 1 is fully compatible with existing models. No schema changes required.

### 7.2 Tier 2 Compatibility

| Required Field | Source | Model Exists? | Field Exists? | Notes |
|---------------|--------|:--:|:--:|-------|
| `diagnostics[]` | `ValidationResult.diagnostics` | YES | YES | List of ValidationDiagnostic |
| Per-diagnostic fields | `ValidationDiagnostic.*` | YES | YES | All 11 fields present (9 original + 2 ecosystem) |
| `levels_passed` | `ValidationResult.levels_passed` | YES | YES | Direct mapping |
| `quality_dimensions` | `QualityScore.dimensions` | YES | YES | Dict of QualityDimension → DimensionScore |
| `ecosystem_dimensions` | `EcosystemScore.dimensions` | YES | YES | Dict of EcosystemHealthDimension → DimensionScore |
| `per_file_scores` | `EcosystemScore.per_file_scores` | YES | YES | Dict of file_id → QualityScore |
| `relationships` | `PipelineContext.relationships` | YES | YES | List of FileRelationship |

**Verdict:** Tier 2 is fully compatible with existing models. No schema changes required.

### 7.3 Tier 3 Compatibility

| Required Field | Source | Model Exists? | Field Exists? | Notes |
|---------------|--------|:--:|:--:|-------|
| `action_items[]` | Remediation Framework | NO | NO | **New model needed** — `RemediationAction` or similar |
| `executive_summary` | Computed | NO | NO | **New field** — generated by Tier 3 renderer |
| `score_projection` | Computed | NO | NO | **New field** — requires scoring sensitivity model |
| `anti_patterns_detected` | `ANTI_PATTERN_REGISTRY` cross-ref | Partial | Partial | Registry exists; cross-referencing from diagnostics is new |

**Verdict:** Tier 3 requires new models. These will be defined in the Remediation Framework (Deliverable 2) and the Report Generation Stage (Deliverable 5). No changes to *existing* models are needed — the new models compose with them.

### 7.4 Tier 4 Compatibility

| Required Field | Source | Model Exists? | Field Exists? | Notes |
|---------------|--------|:--:|:--:|-------|
| `context_profile` | Consumer input | NO | NO | **New model needed** — `ContextProfile` |
| `comparative_analysis` | Calibration specimens | NO | NO | **New model needed** — deferred to v0.4.x+ |
| `domain_recommendations` | Context-aware generator | NO | NO | **New model needed** — deferred to v0.4.x+ |
| `maturity_assessment` | Computed | NO | NO | **New model needed** — deferred to v0.4.x+ |
| `roadmap` | Computed | NO | NO | **New model needed** — deferred to v0.4.x+ |

**Verdict:** Tier 4 requires substantial new modeling work, which is expected given its deferred scope. All Tier 4 models are additive — they do not modify existing models.

### 7.5 Summary

| Tier | Existing Models Sufficient? | New Models Needed? | Existing Models Modified? |
|------|:--:|:--:|:--:|
| Tier 1 | YES | No | No |
| Tier 2 | YES | No | No |
| Tier 3 | Partial | Yes (Remediation) | No |
| Tier 4 | No | Yes (Context, Comparative) | No |

**Key architectural finding:** No existing models need to be modified. All four tiers compose with the existing schema through new models that reference existing ones. This validates the schema-first design philosophy — the existing models are stable building blocks.

---

## 8. JSON Schema Examples

Concrete examples of what each tier's JSON output looks like, to make the contract tangible.

### 8.1 Tier 1 Example (Pass/Fail Gate)

```json
{
  "metadata": {
    "report_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "asot_version": "1.0.0",
    "engine_version": "0.2.0",
    "profile_name": "ci",
    "output_tier": 1,
    "output_format": "json",
    "validated_at": "2026-02-09T14:30:00Z",
    "root_path": "/home/user/project",
    "files_validated": 3,
    "stages_executed": ["DISCOVERY", "PER_FILE", "RELATIONSHIP", "ECOSYSTEM_VALIDATION", "SCORING"],
    "stages_skipped": [],
    "total_duration_ms": 842.3,
    "pass_threshold": 50
  },
  "result": {
    "passed": true,
    "exit_code": 0,
    "level_achieved": "L3_BEST_PRACTICES",
    "total_score": 78.5,
    "grade": "strong",
    "file_count": 3,
    "error_count": 0,
    "warning_count": 4
  }
}
```

### 8.2 Tier 2 Example (Diagnostic Report — Abbreviated)

```json
{
  "metadata": { "...": "same as Tier 1" },
  "result": { "...": "same as Tier 1" },
  "diagnostics": [
    {
      "code": "W003",
      "severity": "WARNING",
      "message": "Link entry has no description text (bare URL only).",
      "remediation": "Add a description after the link: '- [Title](url): Description of the page'.",
      "line_number": 14,
      "column": null,
      "context": "- [API Reference](https://docs.example.com/api)",
      "level": "L2_CONTENT",
      "check_id": "CNT-004",
      "source_file": "llms.txt",
      "related_file": null
    },
    {
      "code": "W012",
      "severity": "WARNING",
      "message": "A link in one file references another file that doesn't exist or is unreachable.",
      "remediation": "Fix the broken link URL or create the missing target file.",
      "line_number": 22,
      "column": null,
      "context": "- [Advanced Topics](docs/advanced.md): Deep dive into advanced features",
      "level": "L2_CONTENT",
      "check_id": null,
      "source_file": "llms.txt",
      "related_file": "docs/advanced.md"
    }
  ],
  "quality": {
    "total_score": 78.5,
    "grade": "strong",
    "dimensions": {
      "structural": { "points": 28.0, "max_points": 30, "percentage": 93.3 },
      "content": { "points": 36.5, "max_points": 50, "percentage": 73.0 },
      "anti_pattern": { "points": 14.0, "max_points": 20, "percentage": 70.0 }
    }
  },
  "ecosystem": {
    "total_score": 72.0,
    "grade": "strong",
    "dimensions": {
      "coverage": { "points": 18.0, "max_points": 20, "percentage": 90.0 },
      "consistency": { "points": 15.0, "max_points": 20, "percentage": 75.0 },
      "completeness": { "points": 16.0, "max_points": 20, "percentage": 80.0 },
      "token_efficiency": { "points": 12.0, "max_points": 20, "percentage": 60.0 },
      "freshness": { "points": 11.0, "max_points": 20, "percentage": 55.0 }
    },
    "file_count": 3,
    "relationship_count": 8,
    "broken_relationships": 1,
    "resolution_rate": 87.5
  },
  "levels_passed": {
    "L0_PARSEABLE": true,
    "L1_STRUCTURAL": true,
    "L2_CONTENT": true,
    "L3_BEST_PRACTICES": true,
    "L4_DOCSTRATUM_EXTENDED": false
  }
}
```

### 8.3 Tier 3 Example (Remediation Playbook — Abbreviated)

```json
{
  "metadata": { "...": "same as above, output_tier: 3" },
  "result": { "...": "same as Tier 1" },
  "diagnostics": [ "...full Tier 2 diagnostic list..." ],
  "quality": { "...": "same as Tier 2" },
  "ecosystem": { "...": "same as Tier 2" },
  "executive_summary": "Your documentation ecosystem scores 78/100 (Strong). Two high-priority actions would push you to Exemplary: adding link descriptions across all sections and resolving the broken cross-file reference to docs/advanced.md. Total estimated effort: 2–4 hours.",
  "score_projection": {
    "current_score": 78.5,
    "projected_after_critical": 78.5,
    "projected_after_high": 88.0,
    "projected_after_all": 94.0
  },
  "action_items": [
    {
      "priority": "HIGH",
      "group_label": "Content Enrichment",
      "description": "Add descriptions to 3 bare links in llms.txt. Link descriptions are the primary way AI agents understand what a page contains before navigating to it. Each description should be 1–2 sentences explaining the page's purpose and content.",
      "affected_diagnostics": ["W003", "W003", "W003"],
      "effort_estimate": "MODERATE",
      "score_impact": 4.5,
      "dependency": null,
      "affected_files": ["llms.txt"],
      "line_numbers": [14, 18, 22]
    },
    {
      "priority": "HIGH",
      "group_label": "Ecosystem Integrity",
      "description": "Resolve the broken cross-file link on line 22 of llms.txt. The link references docs/advanced.md, which does not exist in the ecosystem. Either create the missing file or update the link to point to an existing resource.",
      "affected_diagnostics": ["W012"],
      "effort_estimate": "STRUCTURAL",
      "score_impact": 5.0,
      "dependency": null,
      "affected_files": ["llms.txt"],
      "line_numbers": [22]
    }
  ],
  "anti_patterns_detected": [
    {
      "id": "AP_CON_005",
      "name": "Link Desert",
      "category": "CONTENT",
      "description": "Multiple links lack descriptive text, forcing AI agents to guess page content from URLs alone."
    }
  ]
}
```

---

## 9. Design Decisions

### DECISION-020: Four-Tier Output Model

**Context:** The pipeline needs to serve consumers ranging from CI bots to enterprise consultants.
**Decision:** Four cumulative output tiers, each adding a layer of analysis and interpretation.
**Rationale:** A single "report" format either overwhelms CI consumers or underwhelms consulting consumers. Tiered output lets the same pipeline serve both. Cumulative design means no data is lost — a Tier 3 report includes all Tier 2 data.
**Alternatives Considered:** Single configurable report with verbosity levels; separate pipelines per audience. Both rejected because they either conflate presentation with analysis or duplicate pipeline logic.

### DECISION-021: Format-Tier Compatibility Matrix

**Context:** Not all format-tier combinations are meaningful.
**Decision:** Explicitly define valid and invalid combinations rather than allowing arbitrary mixing.
**Rationale:** Rendering a remediation playbook (prose + action items + effort estimates) in YAML would be semantically incoherent. Rendering a pass/fail signal in HTML is wasteful. Explicit constraints prevent misuse and simplify renderer implementation.
**Trade-off:** Less flexibility for edge cases. Mitigated by allowing profiles to override defaults — if a consumer genuinely needs Tier 3 in YAML, they can define a custom profile, but it won't be a built-in option.

### DECISION-022: Tier 3 Requires Full Pipeline

**Context:** Could Tier 3 (remediation playbook) be produced from a partial pipeline run?
**Decision:** No. Tier 3 requires all five pipeline stages to have completed successfully.
**Rationale:** Score projections need the quality score (S5). Ecosystem-aware grouping needs the relationship graph (S3). Anti-pattern detection needs ecosystem validation (S4). Allowing partial Tier 3 output would produce misleading recommendations. Better to fail clearly ("Tier 3 requires full pipeline") than to produce a partial playbook the consumer might trust.

### DECISION-023: Report Metadata on Every Artifact

**Context:** Reports may be shared, archived, or compared across runs.
**Decision:** Every output artifact includes a metadata header with ASoT version, profile name, timestamp, and execution details.
**Rationale:** Without metadata, a report is unmoored — you can't tell when it was generated, what standards it was validated against, or what configuration produced it. This is the same principle as embedding EXIF data in photos or version headers in compiled binaries.

---

## 10. Open Questions for Downstream Deliverables

These questions are captured here for resolution in the deliverables that depend on this specification:

1. **Remediation Framework (Deliverable 2):** How are effort estimates calibrated? The QUICK_WIN / MODERATE / STRUCTURAL tiers defined in §2.3 are heuristic — what's the evidence basis? Should effort estimates be based on diagnostic code metadata, file size, or number of affected lines?

2. **Rule Registry (Deliverable 3):** Should the `output_tiers` field on each rule indicate which tiers the rule's results appear in? Or is this derivable from the tier → stage mapping in §3.2?

3. **Profiles (Deliverable 4):** Can a profile override the format-tier compatibility matrix? If an enterprise consumer needs Tier 3 in YAML for programmatic consumption, should the profile allow this as an escape hatch?

4. **Report Generation Stage (Deliverable 5):** Should Stage 6 produce a single artifact or a bundle? For Tier 2 in JSON + Markdown simultaneously (common in CI), does the consumer run the pipeline twice or does Stage 6 produce both in one pass?

5. **Ecosystem Calibration (Deliverable 6):** The score projection in Tier 3 (§2.3) depends on a sensitivity model that maps individual check completions to score changes. This model comes from calibration. Can Tier 3 ship with coarse projections before calibration is complete, or should score projection be deferred?

---

*This specification is the root dependency for the DocStratum ecosystem validator architecture. All downstream deliverables (Remediation Framework, Rule Registry, Profiles, Report Generation Stage, Ecosystem Calibration) reference this document as the authoritative definition of what the pipeline delivers.*
