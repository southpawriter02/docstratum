# DS-DD-016: Four-Category Anti-Pattern Severity Classification

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DD-016 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Decision ID** | DECISION-016 |
| **Date Decided** | 2026-02-06 (v0.0.4d) |
| **Impact Area** | Anti-Pattern Detection (`constants.py` → `AntiPatternCategory` enum), Quality Scoring (DS-QS-DIM-APD Anti-Pattern Dimension), all 28+ AP standard files |
| **Provenance** | v0.0.4c anti-pattern taxonomy audit; quality scoring analysis (DS-DD-014); v0.0.7 ecosystem-level analysis |

## Decision

**Anti-patterns are classified into four primary severity categories aligned with quality scoring dimensions and remediation strategies: Critical (4 patterns — structural gating), Structural (5 patterns — structural integrity), Content (9 patterns — content quality), and Strategic (4 patterns — long-term value). An additional Ecosystem category (6 patterns, added in v0.0.7) detects aggregate health at the ecosystem level. Each category has distinct detection logic, scoring penalties, and remediation pathways.**

## Context

During v0.0.4c anti-pattern taxonomy work, the team identified 22 distinct anti-patterns across DocStratum audits. Later, v0.0.7 ecosystem-level research identified 6 additional patterns that don't fit the file-level categories, bringing the total to 28+.

The challenge was organizing these into a framework that:
1. Maps to actionable remediation priority (not all anti-patterns are equally urgent)
2. Aligns with the three quality scoring dimensions (Structural, Content, Anti-Pattern Detection)
3. Enables consistent penalty calculation and scoring
4. Supports different detection and remediation strategies

The solution was a four-category (later five-category) taxonomy that distinguishes not just severity, but also *kind of failure* and *fix strategy*.

## Alternatives Considered

| Option | Rationale For | Rationale Against |
|--------|---------------|-------------------|
| **Binary pass/fail** | Simplest model, no nuance required | Treats "empty file" (AP-CON-001) the same as "wrong section order" (AP-STRUCT-003) — wildly different severity; no prioritization guidance for creators; inflexible |
| **Three-tier (High/Medium/Low)** | Standard industry model, widely understood | Doesn't distinguish *type* of failure (structural vs. content), lumps different fix strategies into same tier, no alignment with quality scoring dimensions, doesn't enable per-category remediation |
| **Four-category (CHOSEN)** | Maps naturally to scoring dimensions (3 dimensions + anti-pattern detection itself = 4 categories), each category has distinct fix strategy (structural = reorganize, content = write better, strategic = rethink approach), enables per-category penalties aligned with DS-DD-014 weights | Requires discipline in categorizing new patterns, more complex than binary/ternary, potential ambiguity when a pattern touches multiple categories |
| **Five-category (expanded v0.0.7)** | Four-category model + ecosystem-level patterns for aggregate health (Index Island, Phantom Links, etc.) that don't fit file-level categories | Adds complexity; ecosystem patterns require different detection infrastructure (cross-file analysis vs. single-file); introduces new scoring dimension for ecosystem health [CALIBRATION-NEEDED] |

## Rationale

The four-category model was selected because it provides maximum alignment between anti-pattern severity, remediation strategy, and quality scoring:

1. **Alignment with quality dimensions (DS-DD-014):**
   - **Critical → Structural gating:** Files with critical anti-patterns have structural integrity so broken that content quality is irrelevant. Score capped at 29/100 regardless of content. (Structural dimension = 0, Content = 0, APD = 29)
   - **Structural → Structural dimension:** These anti-patterns degrade the structural dimension score (–3 to –8 points per pattern, configurable).
   - **Content → Content dimension:** These reduce the content dimension score (–2 to –6 points per pattern, [CALIBRATION-NEEDED]).
   - **Strategic → APD deduction:** These are direct deductions from the 20-point Anti-Pattern Detection dimension (–2 to –5 points per pattern, [CALIBRATION-NEEDED]).

2. **Category definitions (v0.0.4c + v0.0.7 refinements):**

   **Critical (4 patterns — file-level gating):**
   - AP-CRIT-001: Ghost File (empty or near-empty file, essentially unusable)
   - AP-CRIT-002: Structure Chaos (headings malformed, no parseable sections)
   - AP-CRIT-003: Encoding Disaster (file encoding errors, binary corruption)
   - AP-CRIT-004: Link Void (100% of internal links are broken, file is navigation-dead)

   **Remedy:** These require fundamental file reconstruction. A file with any critical pattern is not salvageable through minor edits; it needs rework.

   **Structural (5 patterns — navigation/organization integrity):**
   - AP-STRUCT-001: Sitemap Dump (master index points to nonexistent sections)
   - AP-STRUCT-002: Orphaned Sections (sections exist but aren't referenced from index)
   - AP-STRUCT-003: Duplicate Identity (two sections with identical names)
   - AP-STRUCT-004: Section Shuffle (sections present but in chaotic order)
   - AP-STRUCT-005: Naming Nebula (widespread non-canonical section names)

   **Remedy:** These require reorganization and navigation fixes. Content can remain unchanged; the issue is structure/navigation.

   **Content (9 patterns — content quality degradation):**
   - AP-CON-001: Copy-Paste Plague (sections appear duplicated or boilerplate)
   - AP-CON-002: Blank Canvas (sections present but content is stub/placeholder)
   - AP-CON-003: Jargon Jungle (heavy use of undefined technical terms)
   - AP-CON-004: Link Desert (insufficient cross-references or internal navigation)
   - AP-CON-005: Outdated Oracle (content references outdated versions or deprecated APIs)
   - AP-CON-006: Example Void (documented APIs have no code examples)
   - AP-CON-007: Formulaic Description (descriptions are generic or template-like)
   - AP-CON-008: Silent Agent (no guidance for how LLM agents should use the section)
   - AP-CON-009: Versionless Drift (no version information, unclear which version of software docs apply to)

   **Remedy:** These require writing better content. Structure is fine; execution is poor.

   **Strategic (4 patterns — long-term design/approach issues):**
   - AP-STRAT-001: Automation Obsession (automated tooling generates content without human review)
   - AP-STRAT-002: Monolith Monster (file exceeds 100K tokens, too large to manage)
   - AP-STRAT-003: Meta-Documentation Spiral (documentation of documentation, high meta ratio)
   - AP-STRAT-004: Preference Trap (documentation encodes author preferences instead of universal patterns)

   **Remedy:** These require rethinking the approach to documentation. They're not immediately urgent but undermine long-term value.

   **Ecosystem (6 patterns, v0.0.7 addition — aggregate health):**
   - AP-ECO-001: Index Island (a single file is referenced by many but links back to none)
   - AP-ECO-002: Phantom Links (many files reference a section that exists in no file)
   - AP-ECO-003: Shadow Aggregate (multiple files duplicate the same content at ecosystem scale)
   - AP-ECO-004: Duplicate Ecosystem (files serve identical purpose, unclear which is authoritative)
   - AP-ECO-005: Token Black Hole (some files consume >50% of ecosystem token budget)
   - AP-ECO-006: Orphan Nursery (new projects have no ecosystem links or discovery mechanism)

   **Remedy:** These require cross-file coordination and ecosystem-level governance. Detection requires analyzing multiple files together.

3. **Penalty calculation alignment:** With the categorization, penalties can be applied consistently:
   - **Critical:** Score = 29 (file-level gate, no discussion)
   - **Structural:** Deduct N points from structural dimension (30 points available)
   - **Content:** Deduct M points from content dimension (50 points available)
   - **Strategic:** Deduct K points from anti-pattern dimension (20 points available)
   - **Ecosystem:** [CALIBRATION-NEEDED] — ecosystem-level scoring requires new dimension or aggregation logic

## Impact on ASoT

This decision directly determines:

- **`AntiPatternCategory` enum:** Defined in `constants.py` with 5 members:
  ```python
  class AntiPatternCategory(Enum):
      CRITICAL = "critical"
      STRUCTURAL = "structural"
      CONTENT = "content"
      STRATEGIC = "strategic"
      ECOSYSTEM = "ecosystem"
  ```

- **Quality scoring deductions (DS-DD-014):** Each anti-pattern detection results in a penalty calculated from its category:
  - Critical → file cap (29/100)
  - Structural → structural dimension deduction (–3 to –8 points, [CALIBRATION-NEEDED] per pattern)
  - Content → content dimension deduction (–2 to –6 points, [CALIBRATION-NEEDED] per pattern)
  - Strategic → APD dimension deduction (–2 to –5 points, [CALIBRATION-NEEDED] per pattern)
  - Ecosystem → [CALIBRATION-NEEDED] global aggregation logic

- **Validation pipeline:** Anti-pattern detection occurs at different stages:
  - Critical patterns: Detected early (pre-content analysis)
  - Structural/Content: Detected during content validation
  - Strategic: Detected during scoring phase
  - Ecosystem: Detected during cross-file audits (not part of single-file validation)

- **28+ standard AP files:** Each AP standard file (AP-CRIT-001.md, AP-STRUCT-005.md, AP-CON-003.md, etc.) references its category in the metadata section.

## Constraints Imposed

1. **Each pattern belongs to exactly one category:** Ambiguous patterns must be categorized based on their primary remediation strategy. If a pattern genuinely touches multiple categories, it should be split into two patterns.

2. **Category changes require ASoT version bump:** Moving a pattern from one category to another is a breaking change (changes scoring for all files). Requires MINOR version bump.

3. **Adding new categories requires scoring dimension alignment:** Any new category beyond the five (Critical, Structural, Content, Strategic, Ecosystem) must be aligned with scoring dimensions. This is a MAJOR version change.

4. **Ecosystem patterns require cross-file detection:** Ecosystem anti-patterns cannot be detected by single-file validators. A separate ecosystem audit tool or aggregation service is required.

5. **Penalty magnitude calibration:** The exact deduction values for each category and pattern are marked [CALIBRATION-NEEDED] pending empirical evaluation against gold standards.

## Related Decisions

- **DS-DD-009** (Anti-Pattern Detection Timing — hypothetical, referenced for context): Defines when during the validation pipeline each category is detected. Critical patterns detected first; ecosystem patterns detected last.

- **DS-DD-014** (Content Quality Weights): The 20-point Anti-Pattern Detection dimension is where anti-pattern penalties are applied. Strategic patterns reduce this dimension directly; other categories reduce Structural or Content dimensions.

- **All AP-* standard files (AP-CRIT-001 through AP-ECO-006):** Each standard file declares its category and penalty magnitude in the metadata.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.3 |
| 0.0.7 (future) | TBD | Ecosystem category and 6 ecosystem patterns added; ecosystem-level scoring dimension introduced |
