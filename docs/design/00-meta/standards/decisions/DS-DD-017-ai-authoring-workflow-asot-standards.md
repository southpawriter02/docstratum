# DS-DD-017: AI Authoring Workflow for ASoT Standard Files

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DD-017 |
| **Status** | DRAFT |
| **ASoT Version** | 1.1.0-scaffold |
| **Decision ID** | DECISION-017 |
| **Date Decided** | 2026-02-08 (v1.1.0) |
| **Impact Area** | All future DS-* standard files — governs the end-to-end workflow for AI agents extending the ASoT library |
| **Provenance** | Phase E audit findings (cross-reference errors, template inconsistencies, missed calibration tags); Phase A–E workflow observations; DS-DD-019 (Guided Flexibility Authoring Model) |

## Decision

**AI agents extending the ASoT standards library must follow a formal seven-step authoring workflow: (1) identify the correct element type, (2) assign the next sequential identifier, (3) read a same-type exemplar for template reference, (4) author the file following DS-DD-019's MUST/SHOULD/MAY compliance tiers, (5) self-verify against a pre-integration checklist, (6) integrate with the manifest and README indexes, and (7) run cross-reference validation. This workflow is mandatory for all new DS-* files regardless of the authoring context.**

## Context

During Phases A through E, AI agents authored 144 DS-* standard files without a formal authoring workflow. The process was learned by example — each new file was modeled after existing files of the same type. While this approach worked for the initial migration (where a human was actively directing every file), it produced several categories of error that a formal workflow would have prevented:

1. **Identifier collision risk**: No formal protocol for determining the next available DS-* identifier. During Phase D, the agent consulted the manifest manually, but this was ad-hoc rather than systematic.

2. **Template inconsistency**: QS dimension files (Phase D.5) were authored with stale criteria tables because the agent used an earlier draft as a template rather than verifying against the authoritative VC files. A formal "read a same-type exemplar" step with currency verification would have caught this.

3. **Cross-reference errors**: Six phantom references were found during the Phase E audit (DS-VC-ERR-001, DS-DC-CRIT-001/002, DS-QS-CAP-structural-gating, and three others). A formal cross-reference validation step before declaring a file complete would have prevented all six.

4. **Manifest integration gaps**: During Phase D, 25 provenance map entries were missed because there was no checklist requiring all four manifest integration points (File Registry, Provenance Map, README index, Integrity Assertion update).

5. **Incomplete tag cleanup**: The ratification script missed 20 contextual `[CALIBRATION-NEEDED: ...]` tags because the tag format wasn't standardized. A formal authoring workflow would establish tag conventions upfront.

This workflow codifies what worked during Phases A–E while adding the guardrails that were missing.

## Alternatives Considered

| Option | Rationale For | Rationale Against |
|--------|---------------|-------------------|
| **No formal workflow (status quo)** | Minimal overhead; AI agents are flexible enough to learn by example; worked "well enough" for 144 files | Produced 6 phantom references, 3 stale criteria tables, 25 missing provenance entries, and 20 missed tags — the "pesky 1%" that required a full audit pass to catch |
| **Automated code generation from schema** | Zero template drift risk; programmatically generates skeleton from Pydantic models; guarantees metadata compliance | Produces lifeless documentation — no contextual prose, no nuanced examples, no rationale sections; fundamentally incompatible with the ASoT's emphasis on human/AI-readable standards; would require a separate "fill in the blanks" pass anyway |
| **Guided workflow with self-verification (Chosen)** | Preserves prose quality and contextual depth; structural compliance enforced through checklists; cross-reference validation catches hallucination; manifest integration is systematic rather than ad-hoc; compatible with DS-DD-019's MUST/SHOULD/MAY tiers | Requires discipline from the AI agent; adds overhead per file (estimated: 5–10 minutes of additional verification work); checklists must be maintained as the library evolves |

## Rationale

The guided workflow with self-verification was selected because it addresses every failure mode observed during Phases A–E while preserving the documentation quality that makes the ASoT standards library valuable. The key insight is that most errors occurred not during the writing phase but during the integration phase — when the file needed to connect to the broader library. A workflow that adds lightweight gates at integration points catches these errors before they propagate.

The seven steps are ordered to reflect the natural authoring process: understand → identify → reference → write → verify → integrate → validate. Each step has a clear deliverable and a failure condition that prevents progression to the next step.

## Impact on ASoT

### The Seven-Step Authoring Workflow

#### Step 1: Identify Element Type

Determine which of the 9 standard element types the new file belongs to:

| Type Code | Element Type | When to Use |
|-----------|-------------|-------------|
| VC | Validation Criteria | Defining a measurable quality check with pass/fail conditions |
| DC | Diagnostic Code | Defining an error, warning, or info code emitted by the validation pipeline |
| AP | Anti-Pattern | Documenting a pattern to avoid, with detection logic and remediation |
| DD | Design Decision | Recording an architectural or methodological choice with rationale |
| CN | Canonical Name | Standardizing a section name used across llms.txt files |
| VL | Validation Level | Defining a quality tier in the L0–L4 hierarchy |
| QS | Quality Scoring | Specifying a scoring dimension or gate mechanism |
| EH | Ecosystem Health | Defining a health metric measured across multiple llms.txt files |
| CS | Calibration Specimen | Documenting a reference llms.txt file with known scores |

**Failure condition**: If the content doesn't cleanly fit one type, it may need to be split into multiple files or reconsidered. Hybrid files (e.g., a DD that's also a VC) are not permitted — each file is exactly one type.

#### Step 2: Assign Identifier

Consult DS-MANIFEST.md File Registry to determine the next sequential identifier:

1. Open DS-MANIFEST.md
2. Filter the File Registry table to the target type
3. Find the highest existing number for the type (and category, if applicable)
4. Increment by 1
5. Construct the full identifier: `DS-{TYPE}-{CATEGORY?}-{NNN}`

**Naming conventions:**

| Type | Format | Example |
|------|--------|---------|
| VC | `DS-VC-{DIM}-{NNN}` | DS-VC-STR-010, DS-VC-CON-014 |
| DC | `DS-DC-{SEVERITY}{NNN}` | DS-DC-E011, DS-DC-W019 |
| AP | `DS-AP-{CATEGORY}-{NNN}` | DS-AP-STRAT-005, DS-AP-CONT-010 |
| DD | `DS-DD-{NNN}` | DS-DD-017, DS-DD-020 |
| CN | `DS-CN-{NNN}` | DS-CN-012 |
| VL | `DS-VL-L{N}` | DS-VL-L5 |
| QS | `DS-QS-{SUBTYPE}` | DS-QS-DIM-ENR |
| EH | `DS-EH-{NNN}` | DS-EH-006 |
| CS | `DS-CS-{NNN}` | DS-CS-007 |

**Filename convention**: `{DS-IDENTIFIER}-{human-readable-slug}.md`

Example: `DS-DD-017-ai-authoring-workflow-asot-standards.md`

**Failure condition**: If the identifier already exists in the File Registry, the assignment is invalid. Re-check the manifest.

#### Step 3: Read Same-Type Exemplar

Before writing, read at least one existing file of the same type to internalize the template:

1. Select a RATIFIED file of the same type (prefer recent, well-reviewed files)
2. Note all section headings and their order
3. Note the metadata table fields
4. Note the prose style and depth
5. Verify the exemplar against DS-DD-019's MUST tier for that type — do not propagate any exemplar errors

**Recommended exemplars by type:**

| Type | Recommended Exemplar | Rationale |
|------|---------------------|-----------|
| VC | DS-VC-STR-008 (No Critical Anti-Patterns) | Composite criterion with rich cross-references |
| DC | DS-DC-E001 (No H1 Title) | Clean, concise error code with clear trigger |
| AP | DS-AP-STRAT-004 (Preference Trap) | Full detection logic, synthetic example, remediation |
| DD | DS-DD-016 (Four-Category Severity) | Comprehensive alternatives table, detailed rationale |
| CN | DS-CN-001 (Master Index) | Canonical name with aliases and detection logic |
| VL | DS-VL-L1 (Structural) | Full criteria table, entry/exit conditions |
| QS | DS-QS-DIM-STR (Structural Dimension) | Criteria table aligned with VC files |
| EH | Any DS-EH-* file | All follow the same pattern |
| CS | Any DS-CS-* file | All follow the same pattern |

**Failure condition**: If the exemplar itself has known issues (noted in the manifest or audit records), choose a different exemplar.

#### Step 4: Author the File

Write the file following DS-DD-019's three-tier compliance model:

1. **MUST tier first**: Create the metadata table and all required sections for the element type. Fill in every required field. If a value is genuinely unknown, use a placeholder with a `TODO(vX.Y.Z)` marker — never leave fields blank or use `[CALIBRATION-NEEDED]`.

2. **SHOULD tier next**: Follow section ordering conventions, apply the project's prose tone (professional, precise, structured, actionable), include code examples with Python type hints, and provide cross-references with both identifier and human-readable name on first mention.

3. **MAY tier last**: Add supplementary content as contextually appropriate — extended rationale, diagrams, edge cases, implementation notes.

**Cross-referencing rules:**
- Only reference DS identifiers that exist in the current DS-MANIFEST.md File Registry
- For references to planned/future standards, use the format: `**DS-VC-ENR-001** *(planned — v0.3.x)*`
- Never invent identifiers — this constitutes a Phantom Reference (DS-AP-STRAT-005)
- When referencing a DS-* file for the first time in the document, include both the identifier and the human-readable name: e.g., "DS-DD-014 (Content Quality Primary Weight)"

**Version stamping:**
- Status: `DRAFT`
- ASoT Version: The next minor scaffold version (e.g., `1.1.0-scaffold`)
- Change History: Single entry — `| {version} | {date} | Initial draft — {phase/context} |`

#### Step 5: Self-Verify (Pre-Integration Checklist)

Before integrating with the manifest, verify every item on this checklist:

**Metadata Compliance:**
- [ ] DS Identifier in metadata table matches filename
- [ ] Status is DRAFT
- [ ] ASoT Version is the current scaffold version
- [ ] All type-specific metadata fields are populated (no blanks)

**MUST-Tier Sections:**
- [ ] All required sections for this element type are present (per DS-DD-019)
- [ ] Description section is non-empty and substantive
- [ ] Change History table has at least one entry

**Cross-Reference Integrity:**
- [ ] Every `DS-*` identifier referenced in the file body exists in DS-MANIFEST.md, OR is explicitly marked as `*(planned — vX.Y.Z)*`
- [ ] No `DS-DC-CRIT-*` patterns (these should be `DS-AP-CRIT-*` — a known historical error pattern)
- [ ] No `DS-QS-CAP-*` patterns (these should be `DS-QS-GATE` or similar — another known error pattern)

**Content Quality:**
- [ ] No `[CALIBRATION-NEEDED]` tags — use `TODO(vX.Y.Z): description` in code blocks or omit the information
- [ ] No placeholder text (e.g., "TBD", "TODO", "fill in later") in prose sections
- [ ] Code examples (if any) have language tags on code blocks

**Failure condition**: Any unchecked item blocks progression to Step 6. Fix the issue and re-verify.

#### Step 6: Manifest Integration

Update DS-MANIFEST.md with four integration points:

1. **File Registry**: Add a new row to the File Registry table:
   ```
   | {DS Identifier} | {Type} | {relative-path} | DRAFT | {date} |
   ```

2. **Provenance Map**: Add a new row to the Provenance Map table:
   ```
   | {DS Identifier} | {provenance description} |
   ```

3. **README Index**: Add the file to the appropriate type directory's README.md index table.

4. **Integrity Assertion IA-001**: Update the expected file count (increment by 1 per new file).

**Failure condition**: If any integration point is missed, the file is "orphaned" — it exists on disk but isn't tracked by the manifest. Run a manifest reconciliation check.

#### Step 7: Cross-Reference Validation

After integration, validate the file's cross-references against the updated manifest:

1. Extract all `DS-*` identifier patterns from the new file
2. For each identifier, verify it exists in the (now-updated) DS-MANIFEST.md File Registry
3. For planned references, verify the `*(planned — vX.Y.Z)*` marker is present
4. Verify no other files in the library have broken references to the new file's identifier (this would indicate a forward reference that was waiting for this file)

**Failure condition**: Any unresolvable reference requires correction before the file is considered complete.

## Constraints Imposed

1. **Workflow is mandatory for all new DS-* files**: No exceptions. Even single-file additions must follow all seven steps. The overhead is minimal (Steps 1–3 take <5 minutes) and the error prevention value is high.

2. **Self-verification (Step 5) precedes integration (Step 6)**: Do not add the file to the manifest until it passes the pre-integration checklist. This prevents partially-complete files from polluting the registry.

3. **Manifest is the single source of truth for identifiers**: The File Registry in DS-MANIFEST.md is the authoritative list of all DS-* identifiers. Do not rely on filesystem `ls` commands or README indexes — these are derived from the manifest, not the other way around.

4. **No invented identifiers**: Cross-references must point to identifiers that exist in the manifest or are explicitly marked as planned. This is enforced by DS-AP-STRAT-005 (Phantom Reference).

5. **Template compliance is enforced by DS-DD-019**: The required sections for each element type are defined in DS-DD-019's MUST tier table. This document (DS-DD-017) defines the *workflow*; DS-DD-019 defines the *template rules*.

6. **One file, one type**: Every DS-* file is exactly one element type. If content spans multiple types, split it into separate files with cross-references.

7. **Tag conventions**: Use `TODO(vX.Y.Z): description` for future work items in code blocks. Do not use `[CALIBRATION-NEEDED]` or any bracket-tag format — these are deprecated as of v1.0.0 ratification.

## Related Decisions

- **DS-DD-019** (Guided Flexibility Authoring Model): Defines the MUST/SHOULD/MAY compliance tiers that Step 4 enforces
- **DS-DD-018** (AI Documentation Generation Workflow): The parallel workflow for generating end-user llms.txt files (as opposed to extending the ASoT itself)
- **DS-DD-012** (Canonical Section Names): Section naming conventions that apply to end-user llms.txt files generated using the workflow
- **DS-DD-014** (Content Quality Primary Weight): The philosophical basis for why prose quality matters — content over structure
- **DS-DD-016** (Four-Category Anti-Pattern Severity): Category assignment rules for new AP files created through this workflow
- **DS-AP-STRAT-005** (Phantom Reference): The anti-pattern this workflow's Step 5 and Step 7 specifically guard against
- **DS-AP-STRAT-006** (Template Drift): The anti-pattern this workflow's Step 3 and Step 4 specifically guard against

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 1.1.0-scaffold | 2026-02-08 | Initial draft — Phase F (AI Authoring Guidelines) |
