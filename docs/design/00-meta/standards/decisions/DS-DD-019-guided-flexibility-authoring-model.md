# DS-DD-019: Guided Flexibility Authoring Model

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DD-019 |
| **Status** | DRAFT |
| **ASoT Version** | 1.1.0-scaffold |
| **Decision ID** | DECISION-019 |
| **Date Decided** | 2026-02-08 (v1.1.0) |
| **Impact Area** | All DS-* standard files — governs the compliance model for authoring new standards |
| **Provenance** | Phase E audit findings; observed template inconsistencies in AI-authored DS-* files during Phases C–D; user-directed strictness preference |

## Decision

**The ASoT standards library uses a three-tier compliance model — MUST, SHOULD, MAY — to govern how AI agents author new DS-* standard files and generate end-user llms.txt documentation. Structural rules and required elements are enforced (MUST), conventions and best practices are strongly recommended (SHOULD), and supplementary content has full creative latitude (MAY). This "guided flexibility" model balances consistency with prose quality.**

## Context

During Phases C through E of the ASoT migration, AI agents authored 144 standard files. While the overall quality was high, the Phase E comprehensive audit revealed several consistency issues attributable to the lack of formal authoring rules:

1. **Cross-reference hallucination**: DS-DD-006 referenced `DS-VC-ERR-001` (nonexistent), DS-DD-008 referenced future `DS-VC-ENR-*` criteria without marking them as planned
2. **Template drift**: QS dimension files (STR, CON, APD) had criteria tables that didn't match actual VC files — a structural compliance failure
3. **Stale content in prose sections**: DS-QS-DIM-CON's Rationale section cited wrong point values even after the criteria table was corrected
4. **Inconsistent contextual markers**: `[CALIBRATION-NEEDED]` tags appeared in two different formats (bare tags vs. contextual `[CALIBRATION-NEEDED: detail]`), causing the ratify script to miss 20 of 90 total tags

These issues share a common root cause: no formal specification of what is required vs. recommended vs. optional when authoring DS-* files. The AI agents had to learn the template by example, leading to inconsistent interpretation.

The user explicitly chose "Guided Flexibility" as the strictness model, rejecting both "Strict Templates" (too rigid, kills prose quality) and "Principle-Based" (too loose, invites the very inconsistencies observed during Phase E).

## Alternatives Considered

| Option | Rationale For | Rationale Against |
|--------|---------------|-------------------|
| **Strict Templates** | Maximum consistency; every file is structurally identical; trivially machine-parseable; eliminates all template drift | Kills prose quality — AI produces formulaic, wooden documentation; no room for context-specific explanations; discourages rich examples; treats all element types identically when they have different needs |
| **Principle-Based** | Maximum creative freedom; AI can adapt documentation to context; encourages natural writing; lowest overhead | Invites the exact inconsistencies observed during Phase E (cross-reference hallucination, missing sections, wrong metadata); no machine-parseable guarantees; relies entirely on AI judgment, which is demonstrably imperfect |
| **Guided Flexibility (Chosen)** | Structural backbone enforced (machine-parseable, consistent metadata), prose within that backbone has latitude (natural writing, rich examples, context-appropriate depth), three-tier model (MUST/SHOULD/MAY) gives AI clear self-assessment criteria | Requires formal specification of which elements fall in each tier; more complex than binary enforce/don't-enforce; tier boundaries may need periodic reassessment as the library evolves |

## Rationale

Guided Flexibility was selected because it addresses the observed failure modes while preserving prose quality:

1. **MUST-tier enforcement prevents the Phase E audit findings**: Metadata table fields, required section headings, identifier format, and cross-reference rules are non-negotiable. This directly prevents phantom references (DS-AP-STRAT-005) and template drift (DS-AP-STRAT-006).

2. **SHOULD-tier guidance improves baseline quality without rigidity**: Section ordering, prose tone conventions, and example depth expectations give AI agents a strong starting point while allowing contextual adaptation. A VC file describing a simple boolean check can be shorter than one describing a complex heuristic — the SHOULD tier permits this natural variation.

3. **MAY-tier latitude encourages richness**: Supplementary subsections (e.g., "Implementation Notes," "Edge Cases," "Performance Considerations"), diagrams, extended rationale, and additional cross-references make documentation more valuable when present. Making these optional prevents boilerplate padding when they're not contextually useful.

4. **RFC 2119 alignment**: The MUST/SHOULD/MAY terminology follows established industry convention (RFC 2119), making the model immediately understandable to technical audiences and AI agents alike.

## Impact on ASoT

This decision establishes the compliance tiers for all DS-* standard file authoring:

### MUST Tier (Enforced Structure)

These elements are **required in every DS-* file**. Absence constitutes a template drift violation (DS-AP-STRAT-006).

**Universal (all element types):**
- Metadata table with correct fields for the element type
- `## Description` section
- `## Change History` section with version table
- DS Identifier in metadata matches filename convention
- Status field set to DRAFT for new files, RATIFIED for ratified files
- ASoT Version field matches current scaffold or ratified version

**Type-specific required sections:**

| Type | Required Sections (beyond universal) |
|------|--------------------------------------|
| VC (Validation Criteria) | Pass Condition, Fail Condition, Emitted Diagnostics, Related Criteria, Calibration Notes |
| DC (Diagnostic Code) | Trigger Condition, Severity, Emitted By, Resolution |
| AP (Anti-Pattern) | Detection Logic, Example (Synthetic), Remediation, Affected Criteria |
| DD (Design Decision) | Decision, Context, Alternatives Considered, Rationale, Impact on ASoT, Constraints Imposed, Related Decisions |
| CN (Canonical Name) | Purpose, Detection, Aliases, Related Sections |
| VL (Validation Level) | Criteria at This Level, Entry Conditions, Exit Criteria, Scoring Impact |
| QS (Quality Scoring) | Specification (criteria table), Scoring Mechanism |
| EH (Ecosystem Health) | Metric Definition, Measurement, Thresholds, Related Patterns |
| CS (Calibration Specimen) | Source, Scores, Analysis |

### SHOULD Tier (Guided Elements)

These elements are **strongly recommended** and should be included unless there's a contextual reason to omit them. Their absence is not a violation but may reduce documentation quality.

- Section ordering follows the established convention for the element type (as listed in the MUST tier table)
- Prose tone is professional, precise, and structured per the project's writing standards (RR-META-agentic-instructions §7.2)
- Code examples in VC and AP files use Python with type hints and Google-style docstrings
- Cross-references to related DS-* files include both the identifier and the human-readable name on first mention (e.g., "DS-DD-014 (Content Quality Primary Weight)")
- Calibration Notes in VC files reference specific calibration specimens (DS-CS-*) with concrete scores
- Anti-pattern Detection Logic includes both the algorithm description and a runnable Python code block
- Change History entries follow the format: `| version | date | description |`

### MAY Tier (Creative Latitude)

These elements are **entirely optional** and left to the author's judgment. Their presence enriches the documentation; their absence is unremarkable.

- Supplementary subsections beyond the required set (e.g., "Implementation Notes," "Edge Cases," "Performance Considerations," "Historical Context")
- ASCII diagrams or Mermaid-compatible flowcharts
- Extended rationale beyond the minimum needed to justify the decision
- Additional cross-references to external resources, research papers, or project-level RR-META documents
- Illustrative code samples beyond the minimum required by the template
- Comparative tables that aren't part of the core specification
- Notes on future evolution or version roadmap connections

## Constraints Imposed

1. **Tier assignment is authoritative**: The MUST/SHOULD/MAY classification in this document is the definitive reference. When in doubt about whether an element is required, consult this document — not historical precedent from existing files.

2. **MUST-tier violations block ratification**: A DS-* file missing any MUST-tier element cannot be promoted from DRAFT to RATIFIED. The manifest ratification process (Phase E or equivalent) must verify MUST-tier compliance.

3. **Tier reassignment requires version bump**: Moving an element from SHOULD to MUST (or vice versa) changes the compliance contract and requires an ASoT MINOR version bump at minimum. Moving an element from MAY to MUST requires a MINOR bump with a migration plan for existing files.

4. **New element types follow the same model**: If a new DS-* element type is introduced (beyond VC, DC, AP, DD, CN, VL, QS, EH, CS), its required sections must be formally specified in a MUST-tier table update to this document before any files of that type are authored.

5. **Self-assessment is the first gate**: AI agents authoring DS-* files should self-assess against the MUST tier before declaring a file complete. This precedes any manifest integration or peer review.

## Related Decisions

- **DS-DD-017** (AI Authoring Workflow for ASoT Standards): The workflow document that operationalizes this compliance model into step-by-step authoring procedures
- **DS-DD-018** (AI Documentation Generation Workflow): Extends this model's principles to end-user llms.txt documentation generation
- **DS-DD-014** (Content Quality Primary Weight): The philosophical foundation — content quality matters more than structural perfection, which is why MUST is limited to structural concerns while prose quality lives in SHOULD/MAY

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 1.1.0-scaffold | 2026-02-08 | Initial draft — Phase F (AI Authoring Guidelines) |
