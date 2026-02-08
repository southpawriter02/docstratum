# DS-DD-012: Canonical Section Names (Frequency-Driven)

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DD-012 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Decision ID** | DECISION-012 |
| **Date Decided** | 2026-02-04 (v0.0.4d) |
| **Impact Area** | Validation Criteria (DS-VC-CON-008 Canonical Section Names), Constants (`constants.py` → `CanonicalSectionName` enum with 11 canonical names and 32 aliases in `SECTION_NAME_ALIASES`) |
| **Provenance** | v0.0.2c frequency audit of 450+ projects; DS-CONST-004 §Enumerated Values |

## Decision

**Eleven canonical section names are standardized across the ASoT ecosystem based on frequency analysis of 450+ projects. The `CanonicalSectionName` enum in `constants.py` defines the authoritative standard names, and the `SECTION_NAME_ALIASES` mapping (32 variations) automatically resolves common alternative names to their canonical forms during validation.**

## Context

During the v0.0.2c audit phase, the team analyzed section naming patterns across 450+ open-source projects to understand how documentation creators actually organize their llms.txt files. The analysis revealed a fragmented ecosystem where the same concept is named differently across projects:

- "Getting Started" vs. "Getting Going" vs. "Quick Start" vs. "Installation" (all serving the same purpose)
- "API Documentation" vs. "API Reference" vs. "Function Reference" vs. "SDK Reference"
- "Configuration Guide" vs. "Configuration" vs. "Setup" vs. "Options"

This fragmentation creates two problems:
1. **Validation inconsistency:** Files are valid or invalid depending on arbitrary naming choices, not content quality.
2. **Agent difficulty:** LLM agents consuming llms.txt files cannot reliably locate sections by expected name, making navigation brittle.

The solution was to identify the most-used names empirically and standardize on those, while maintaining an alias mapping for backward compatibility and flexibility.

## Alternatives Considered

| Option | Rationale For | Rationale Against |
|--------|---------------|-------------------|
| Top 20 most-frequent names from audit | More granular standardization, higher coverage without aliases | Too many names to enforce meaningfully; creators would still encounter variation; increases cognitive load; anti-pattern AP-STRUCT-005 becomes harder to detect (too many valid names) |
| Project-specific section names (no standardization) | Maximum flexibility, no overhead for creators | Destroys validation consistency; agents have no predictable navigation; impossible to detect naming anti-patterns; ecosystem fragmentation persists |
| Top 11 most-frequent names from 450-project audit + 32-alias mapping (CHOSEN) | Balances standardization with flexibility; covers ~85% of observed projects natively, remaining 15% via aliases; enables anti-pattern detection for naming chaos; empirically grounded in actual usage | Requires discipline to map new names to canonical forms; some projects may feel forced into a canon that doesn't match their culture; alias maintenance overhead |

## Rationale

The chosen option was selected because it maximizes both standardization and pragmatism:

1. **Empirical grounding:** The 11 canonical names were selected from the v0.0.2c audit results, ranked by frequency of appearance across 450+ projects. This ensures the canon reflects actual practice, not theoretical ideals.

2. **Frequency-ranked canonical list (from v0.0.2c audit):**
   1. Getting Started (78% of sampled projects)
   2. Architecture (65%)
   3. API Reference (61%)
   4. Configuration (58%)
   5. Examples (54%)
   6. Troubleshooting (52%)
   7. FAQ (45%)
   8. Advanced Topics (42%)
   9. Concepts (40%)
   10. Best Practices (38%)
   11. Contributing (35%)

3. **Alias mapping provides backward compatibility:** The `SECTION_NAME_ALIASES` dictionary maps 32 common variations to their canonical forms. For example:
   - "Quick Start" → "Getting Started"
   - "Setup" → "Getting Started" or "Configuration" (context-dependent)
   - "API Docs" → "API Reference"
   - "Troubleshooting Guide" → "Troubleshooting"

   This means existing projects don't need to rename sections; the validation system normalizes on their behalf.

4. **Anti-pattern detection becomes possible:** With a canonical set, the anti-pattern AP-STRUCT-005 (Naming Nebula) can detect widespread use of non-canonical names within a file or across an ecosystem. This provides signal to creators that their naming choice is an outlier.

5. **Agent navigation becomes reliable:** Agents can look for known canonical section names and build predictable navigation heuristics. If a section name is not canonical, agents can attempt alias resolution before concluding the section doesn't exist.

## Impact on ASoT

This decision directly determines:

- **DS-VC-CON-008** (Canonical Section Names): Validates that section headings in llms.txt files use canonical names or valid aliases. Non-canonical names are flagged but do not block validation (they're caught by anti-pattern detection instead).

- **`CanonicalSectionName` enum:** Defined in `constants.py` with 11 members:
  ```python
  class CanonicalSectionName(Enum):
      GETTING_STARTED = "Getting Started"
      ARCHITECTURE = "Architecture"
      API_REFERENCE = "API Reference"
      CONFIGURATION = "Configuration"
      EXAMPLES = "Examples"
      TROUBLESHOOTING = "Troubleshooting"
      FAQ = "FAQ"
      ADVANCED_TOPICS = "Advanced Topics"
      CONCEPTS = "Concepts"
      BEST_PRACTICES = "Best Practices"
      CONTRIBUTING = "Contributing"
  ```

- **`SECTION_NAME_ALIASES` mapping:** A dictionary mapping 32 common variations to their canonical equivalents. This mapping is consulted during validation; if a section name appears in aliases, it's normalized to the canonical form before further processing.

- **Anti-pattern AP-STRUCT-005 (Naming Nebula):** Triggered when a file uses more than 3 non-canonical section names or when the ratio of non-canonical to canonical names exceeds a threshold [CALIBRATION-NEEDED: set threshold empirically]. This signals that the file's naming scheme is chaotic.

## Constraints Imposed

1. **Adoption rules:**
   - MUST use canonical names when the canonical name applies to the content.
   - ALLOWED to add custom sections that don't map to any canonical name (e.g., "Deployment Architecture", "Performance Tuning" as project-specific deep dives).
   - AVOID reinventing names (e.g., using "Getting Going" instead of "Getting Started" when the latter is canonical).

2. **Alias mapping is unidirectional:** A non-canonical name maps to one canonical form. If a name is ambiguous (e.g., "Setup" could be "Getting Started" or "Configuration"), the mapping must choose the most likely target based on frequency in the training corpus.

3. **New canonical names require ASoT version bump:** Adding a new canonical name to the enum requires a MINOR version bump because it changes validation behavior for existing files. Removing a canonical name requires a MAJOR version bump.

4. **Alias additions are backward-compatible:** Adding new entries to `SECTION_NAME_ALIASES` can be done without a version bump because it only broadens the set of accepted names; it doesn't make previously-valid files invalid.

5. **Diagnostic output:** When a non-canonical name is encountered, the diagnostic output includes the canonical form or alias suggestion. Example: "Section 'Quick Start' is not canonical; consider 'Getting Started' (aliased equivalent) for consistency."

## Related Decisions

- **DS-DD-003** (GFM as Standard): Canonical section names are expressed as GFM headings (level 2 or level 3, depending on nesting). The `CanonicalSectionName` enum defines the text; heading level is a separate constraint.

- **DS-DD-010** (Master Index as Navigation Priority): The Master Index is not part of the canonical section name list (it's a special, always-present navigation structure). Other canonical sections may be referenced by the Master Index.

- **AP-STRUCT-005** (Naming Nebula): Anti-pattern that detects chaotic or non-canonical naming schemes. This decision enables that anti-pattern to be defined with concrete criteria.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.3 |
