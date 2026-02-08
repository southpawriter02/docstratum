# DS-MANIFEST: DocStratum ASoT Registry

> **ASoT Version:** 1.0.0
> **Version Date:** 2026-02-08
> **Status:** RATIFIED — Phase E complete
> **Governed By:** RR-META-asot-implementation-strategy.md

---

## 1. ASoT Version

- **Current Version:** 1.0.0
- **Version Date:** 2026-02-08
- **Semantic Versioning:** MAJOR.MINOR.PATCH
  - **MAJOR:** Breaking changes (criteria removed, scoring weights changed, levels redefined)
  - **MINOR:** Additive changes (new criteria added, new diagnostic codes)
  - **PATCH:** Corrections (typos, clarifications, provenance updates)

## 2. File Registry

| DS Identifier | Type | Path | Status | Modified |
|---------------|------|------|--------|----------|
| DS-VC-STR-001 | VC | criteria/structural/DS-VC-STR-001-h1-title-present.md | RATIFIED | 2026-02-08 |
| DS-DC-E001 | DC | diagnostics/errors/DS-DC-E001-NO_H1_TITLE.md | RATIFIED | 2026-02-08 |
| DS-DC-W001 | DC | diagnostics/warnings/DS-DC-W001-MISSING_BLOCKQUOTE.md | RATIFIED | 2026-02-08 |
| DS-DC-I001 | DC | diagnostics/info/DS-DC-I001-NO_LLM_INSTRUCTIONS.md | RATIFIED | 2026-02-08 |
| DS-VL-L0 | VL | levels/DS-VL-L0-PARSEABLE.md | RATIFIED | 2026-02-08 |
| DS-DD-014 | DD | decisions/DS-DD-014-content-quality-primary-weight.md | RATIFIED | 2026-02-08 |
| DS-DD-001 | DD | decisions/DS-DD-001-markdown-over-json-yaml.md | RATIFIED | 2026-02-08 |
| DS-DD-002 | DD | decisions/DS-DD-002-three-layer-architecture.md | RATIFIED | 2026-02-08 |
| DS-DD-003 | DD | decisions/DS-DD-003-gfm-as-standard.md | RATIFIED | 2026-02-08 |
| DS-DD-004 | DD | decisions/DS-DD-004-concept-id-format.md | RATIFIED | 2026-02-08 |
| DS-DD-005 | DD | decisions/DS-DD-005-typed-directed-relationships.md | RATIFIED | 2026-02-08 |
| DS-DD-006 | DD | decisions/DS-DD-006-pydantic-for-schema-validation.md | RATIFIED | 2026-02-08 |
| DS-DD-007 | DD | decisions/DS-DD-007-csv-for-relationship-matrices.md | RATIFIED | 2026-02-08 |
| DS-DD-008 | DD | decisions/DS-DD-008-example-ids-linked-to-concepts.md | RATIFIED | 2026-02-08 |
| DS-DD-009 | DD | decisions/DS-DD-009-anti-pattern-detection-timing.md | RATIFIED | 2026-02-08 |
| DS-DD-010 | DD | decisions/DS-DD-010-master-index-priority.md | RATIFIED | 2026-02-08 |
| DS-DD-011 | DD | decisions/DS-DD-011-optional-sections-explicitly-marked.md | RATIFIED | 2026-02-08 |
| DS-DD-012 | DD | decisions/DS-DD-012-canonical-section-names.md | RATIFIED | 2026-02-08 |
| DS-DD-013 | DD | decisions/DS-DD-013-token-budget-tiers.md | RATIFIED | 2026-02-08 |
| DS-DD-015 | DD | decisions/DS-DD-015-mcp-as-target-consumer.md | RATIFIED | 2026-02-08 |
| DS-DD-016 | DD | decisions/DS-DD-016-four-category-anti-pattern-severity.md | RATIFIED | 2026-02-08 |
| DS-AP-CRIT-001 | AP | anti-patterns/critical/DS-AP-CRIT-001-ghost-file.md | RATIFIED | 2026-02-08 |
| DS-QS-DIM-STR | QS | scoring/DS-QS-DIM-STR-structural-dimension.md | RATIFIED | 2026-02-08 |
| DS-QS-DIM-CON | QS | scoring/DS-QS-DIM-CON-content-dimension.md | RATIFIED | 2026-02-08 |
| DS-QS-DIM-APD | QS | scoring/DS-QS-DIM-APD-anti-pattern-dimension.md | RATIFIED | 2026-02-08 |
| DS-QS-GRADE | QS | scoring/DS-QS-GRADE-thresholds.md | RATIFIED | 2026-02-08 |
| DS-QS-GATE | QS | scoring/DS-QS-GATE-structural-gating.md | RATIFIED | 2026-02-08 |
| DS-EH-COV | EH | ecosystem/DS-EH-COV-coverage.md | RATIFIED | 2026-02-08 |
| DS-EH-CONS | EH | ecosystem/DS-EH-CONS-consistency.md | RATIFIED | 2026-02-08 |
| DS-EH-COMP | EH | ecosystem/DS-EH-COMP-completeness.md | RATIFIED | 2026-02-08 |
| DS-EH-TOK | EH | ecosystem/DS-EH-TOK-token-efficiency.md | RATIFIED | 2026-02-08 |
| DS-EH-FRESH | EH | ecosystem/DS-EH-FRESH-freshness.md | RATIFIED | 2026-02-08 |
| DS-CS-001 | CS | calibration/DS-CS-001-svelte-exemplary.md | RATIFIED | 2026-02-08 |
| DS-CS-002 | CS | calibration/DS-CS-002-pydantic-exemplary.md | RATIFIED | 2026-02-08 |
| DS-CS-003 | CS | calibration/DS-CS-003-vercel-sdk-exemplary.md | RATIFIED | 2026-02-08 |
| DS-CS-004 | CS | calibration/DS-CS-004-shadcn-ui-strong.md | RATIFIED | 2026-02-08 |
| DS-CS-005 | CS | calibration/DS-CS-005-cursor-needs-work.md | RATIFIED | 2026-02-08 |
| DS-CS-006 | CS | calibration/DS-CS-006-nvidia-critical.md | RATIFIED | 2026-02-08 |
| DS-CN-001 | CN | canonical/DS-CN-001-master-index.md | RATIFIED | 2026-02-08 |
| DS-CN-002 | CN | canonical/DS-CN-002-llm-instructions.md | RATIFIED | 2026-02-08 |
| DS-CN-003 | CN | canonical/DS-CN-003-getting-started.md | RATIFIED | 2026-02-08 |
| DS-CN-004 | CN | canonical/DS-CN-004-core-concepts.md | RATIFIED | 2026-02-08 |
| DS-CN-005 | CN | canonical/DS-CN-005-api-reference.md | RATIFIED | 2026-02-08 |
| DS-CN-006 | CN | canonical/DS-CN-006-examples.md | RATIFIED | 2026-02-08 |
| DS-CN-007 | CN | canonical/DS-CN-007-configuration.md | RATIFIED | 2026-02-08 |
| DS-CN-008 | CN | canonical/DS-CN-008-advanced-topics.md | RATIFIED | 2026-02-08 |
| DS-CN-009 | CN | canonical/DS-CN-009-troubleshooting.md | RATIFIED | 2026-02-08 |
| DS-CN-010 | CN | canonical/DS-CN-010-faq.md | RATIFIED | 2026-02-08 |
| DS-CN-011 | CN | canonical/DS-CN-011-optional.md | RATIFIED | 2026-02-08 |
| DS-DC-E002 | DC | diagnostics/errors/DS-DC-E002-MULTIPLE_H1.md | RATIFIED | 2026-02-08 |
| DS-DC-E003 | DC | diagnostics/errors/DS-DC-E003-INVALID_ENCODING.md | RATIFIED | 2026-02-08 |
| DS-DC-E004 | DC | diagnostics/errors/DS-DC-E004-INVALID_LINE_ENDINGS.md | RATIFIED | 2026-02-08 |
| DS-DC-E005 | DC | diagnostics/errors/DS-DC-E005-INVALID_MARKDOWN.md | RATIFIED | 2026-02-08 |
| DS-DC-E006 | DC | diagnostics/errors/DS-DC-E006-BROKEN_LINKS.md | RATIFIED | 2026-02-08 |
| DS-DC-E007 | DC | diagnostics/errors/DS-DC-E007-EMPTY_FILE.md | RATIFIED | 2026-02-08 |
| DS-DC-E008 | DC | diagnostics/errors/DS-DC-E008-EXCEEDS_SIZE_LIMIT.md | RATIFIED | 2026-02-08 |
| DS-DC-E009 | DC | diagnostics/errors/DS-DC-E009-NO_INDEX_FILE.md | RATIFIED | 2026-02-08 |
| DS-DC-E010 | DC | diagnostics/errors/DS-DC-E010-ORPHANED_ECOSYSTEM_FILE.md | RATIFIED | 2026-02-08 |
| DS-DC-W002 | DC | diagnostics/warnings/DS-DC-W002-NON_CANONICAL_SECTION_NAME.md | RATIFIED | 2026-02-08 |
| DS-DC-W003 | DC | diagnostics/warnings/DS-DC-W003-LINK_MISSING_DESCRIPTION.md | RATIFIED | 2026-02-08 |
| DS-DC-W004 | DC | diagnostics/warnings/DS-DC-W004-NO_CODE_EXAMPLES.md | RATIFIED | 2026-02-08 |
| DS-DC-W005 | DC | diagnostics/warnings/DS-DC-W005-CODE_NO_LANGUAGE.md | RATIFIED | 2026-02-08 |
| DS-DC-W006 | DC | diagnostics/warnings/DS-DC-W006-FORMULAIC_DESCRIPTIONS.md | RATIFIED | 2026-02-08 |
| DS-DC-W007 | DC | diagnostics/warnings/DS-DC-W007-MISSING_VERSION_METADATA.md | RATIFIED | 2026-02-08 |
| DS-DC-W008 | DC | diagnostics/warnings/DS-DC-W008-SECTION_ORDER_NON_CANONICAL.md | RATIFIED | 2026-02-08 |
| DS-DC-W009 | DC | diagnostics/warnings/DS-DC-W009-NO_MASTER_INDEX.md | RATIFIED | 2026-02-08 |
| DS-DC-W010 | DC | diagnostics/warnings/DS-DC-W010-TOKEN_BUDGET_EXCEEDED.md | RATIFIED | 2026-02-08 |
| DS-DC-W011 | DC | diagnostics/warnings/DS-DC-W011-EMPTY_SECTIONS.md | RATIFIED | 2026-02-08 |
| DS-DC-W012 | DC | diagnostics/warnings/DS-DC-W012-BROKEN_CROSS_FILE_LINK.md | RATIFIED | 2026-02-08 |
| DS-DC-W013 | DC | diagnostics/warnings/DS-DC-W013-MISSING_AGGREGATE.md | RATIFIED | 2026-02-08 |
| DS-DC-W014 | DC | diagnostics/warnings/DS-DC-W014-AGGREGATE_INCOMPLETE.md | RATIFIED | 2026-02-08 |
| DS-DC-W015 | DC | diagnostics/warnings/DS-DC-W015-INCONSISTENT_PROJECT_NAME.md | RATIFIED | 2026-02-08 |
| DS-DC-W016 | DC | diagnostics/warnings/DS-DC-W016-INCONSISTENT_VERSIONING.md | RATIFIED | 2026-02-08 |
| DS-DC-W017 | DC | diagnostics/warnings/DS-DC-W017-REDUNDANT_CONTENT.md | RATIFIED | 2026-02-08 |
| DS-DC-W018 | DC | diagnostics/warnings/DS-DC-W018-UNBALANCED_TOKEN_DISTRIBUTION.md | RATIFIED | 2026-02-08 |
| DS-DC-I002 | DC | diagnostics/info/DS-DC-I002-NO_CONCEPT_DEFINITIONS.md | RATIFIED | 2026-02-08 |
| DS-DC-I003 | DC | diagnostics/info/DS-DC-I003-NO_FEW_SHOT_EXAMPLES.md | RATIFIED | 2026-02-08 |
| DS-DC-I004 | DC | diagnostics/info/DS-DC-I004-RELATIVE_URLS_DETECTED.md | RATIFIED | 2026-02-08 |
| DS-DC-I005 | DC | diagnostics/info/DS-DC-I005-TYPE_2_FULL_DETECTED.md | RATIFIED | 2026-02-08 |
| DS-DC-I006 | DC | diagnostics/info/DS-DC-I006-OPTIONAL_SECTIONS_UNMARKED.md | RATIFIED | 2026-02-08 |
| DS-DC-I007 | DC | diagnostics/info/DS-DC-I007-JARGON_WITHOUT_DEFINITION.md | RATIFIED | 2026-02-08 |
| DS-DC-I008 | DC | diagnostics/info/DS-DC-I008-NO_INSTRUCTION_FILE.md | RATIFIED | 2026-02-08 |
| DS-DC-I009 | DC | diagnostics/info/DS-DC-I009-CONTENT_COVERAGE_GAP.md | RATIFIED | 2026-02-08 |
| DS-DC-I010 | DC | diagnostics/info/DS-DC-I010-ECOSYSTEM_SINGLE_FILE.md | RATIFIED | 2026-02-08 |
| DS-VC-STR-002 | VC | criteria/structural/DS-VC-STR-002-single-h1-only.md | RATIFIED | 2026-02-08 |
| DS-VC-STR-003 | VC | criteria/structural/DS-VC-STR-003-blockquote-present.md | RATIFIED | 2026-02-08 |
| DS-VC-STR-004 | VC | criteria/structural/DS-VC-STR-004-h2-section-structure.md | RATIFIED | 2026-02-08 |
| DS-VC-STR-005 | VC | criteria/structural/DS-VC-STR-005-link-format-compliance.md | RATIFIED | 2026-02-08 |
| DS-VC-STR-006 | VC | criteria/structural/DS-VC-STR-006-no-heading-violations.md | RATIFIED | 2026-02-08 |
| DS-VC-STR-007 | VC | criteria/structural/DS-VC-STR-007-canonical-section-ordering.md | RATIFIED | 2026-02-08 |
| DS-VC-STR-008 | VC | criteria/structural/DS-VC-STR-008-no-critical-anti-patterns.md | RATIFIED | 2026-02-08 |
| DS-VC-STR-009 | VC | criteria/structural/DS-VC-STR-009-no-structural-anti-patterns.md | RATIFIED | 2026-02-08 |
| DS-VC-CON-001 | VC | criteria/content/DS-VC-CON-001-non-empty-descriptions.md | RATIFIED | 2026-02-08 |
| DS-VC-CON-002 | VC | criteria/content/DS-VC-CON-002-url-resolvability.md | RATIFIED | 2026-02-08 |
| DS-VC-CON-003 | VC | criteria/content/DS-VC-CON-003-no-placeholder-content.md | RATIFIED | 2026-02-08 |
| DS-VC-CON-004 | VC | criteria/content/DS-VC-CON-004-non-empty-sections.md | RATIFIED | 2026-02-08 |
| DS-VC-CON-005 | VC | criteria/content/DS-VC-CON-005-no-duplicate-sections.md | RATIFIED | 2026-02-08 |
| DS-VC-CON-006 | VC | criteria/content/DS-VC-CON-006-substantive-blockquote.md | RATIFIED | 2026-02-08 |
| DS-VC-CON-007 | VC | criteria/content/DS-VC-CON-007-no-formulaic-descriptions.md | RATIFIED | 2026-02-08 |
| DS-VC-CON-008 | VC | criteria/content/DS-VC-CON-008-canonical-section-names.md | RATIFIED | 2026-02-08 |
| DS-VC-CON-009 | VC | criteria/content/DS-VC-CON-009-master-index-present.md | RATIFIED | 2026-02-08 |
| DS-VC-CON-010 | VC | criteria/content/DS-VC-CON-010-code-examples-present.md | RATIFIED | 2026-02-08 |
| DS-VC-CON-011 | VC | criteria/content/DS-VC-CON-011-code-language-specifiers.md | RATIFIED | 2026-02-08 |
| DS-VC-CON-012 | VC | criteria/content/DS-VC-CON-012-token-budget-respected.md | RATIFIED | 2026-02-08 |
| DS-VC-CON-013 | VC | criteria/content/DS-VC-CON-013-version-metadata-present.md | RATIFIED | 2026-02-08 |
| DS-VC-APD-001 | VC | criteria/anti-pattern/DS-VC-APD-001-llm-instructions-section.md | RATIFIED | 2026-02-08 |
| DS-VC-APD-002 | VC | criteria/anti-pattern/DS-VC-APD-002-concept-definitions.md | RATIFIED | 2026-02-08 |
| DS-VC-APD-003 | VC | criteria/anti-pattern/DS-VC-APD-003-few-shot-examples.md | RATIFIED | 2026-02-08 |
| DS-VC-APD-004 | VC | criteria/anti-pattern/DS-VC-APD-004-no-content-anti-patterns.md | RATIFIED | 2026-02-08 |
| DS-VC-APD-005 | VC | criteria/anti-pattern/DS-VC-APD-005-no-strategic-anti-patterns.md | RATIFIED | 2026-02-08 |
| DS-VC-APD-006 | VC | criteria/anti-pattern/DS-VC-APD-006-token-optimized-structure.md | RATIFIED | 2026-02-08 |
| DS-VC-APD-007 | VC | criteria/anti-pattern/DS-VC-APD-007-relative-url-minimization.md | RATIFIED | 2026-02-08 |
| DS-VC-APD-008 | VC | criteria/anti-pattern/DS-VC-APD-008-jargon-defined-or-linked.md | RATIFIED | 2026-02-08 |
| DS-VL-L1 | VL | levels/DS-VL-L1-STRUCTURAL.md | RATIFIED | 2026-02-08 |
| DS-VL-L2 | VL | levels/DS-VL-L2-CONTENT_QUALITY.md | RATIFIED | 2026-02-08 |
| DS-VL-L3 | VL | levels/DS-VL-L3-BEST_PRACTICES.md | RATIFIED | 2026-02-08 |
| DS-VL-L4 | VL | levels/DS-VL-L4-DOCSTRATUM_EXTENDED.md | RATIFIED | 2026-02-08 |
| DS-AP-CRIT-002 | AP | anti-patterns/critical/DS-AP-CRIT-002-structure-chaos.md | RATIFIED | 2026-02-08 |
| DS-AP-CRIT-003 | AP | anti-patterns/critical/DS-AP-CRIT-003-encoding-disaster.md | RATIFIED | 2026-02-08 |
| DS-AP-CRIT-004 | AP | anti-patterns/critical/DS-AP-CRIT-004-link-void.md | RATIFIED | 2026-02-08 |
| DS-AP-STRUCT-001 | AP | anti-patterns/structural/DS-AP-STRUCT-001-sitemap-dump.md | RATIFIED | 2026-02-08 |
| DS-AP-STRUCT-002 | AP | anti-patterns/structural/DS-AP-STRUCT-002-orphaned-sections.md | RATIFIED | 2026-02-08 |
| DS-AP-STRUCT-003 | AP | anti-patterns/structural/DS-AP-STRUCT-003-duplicate-identity.md | RATIFIED | 2026-02-08 |
| DS-AP-STRUCT-004 | AP | anti-patterns/structural/DS-AP-STRUCT-004-section-shuffle.md | RATIFIED | 2026-02-08 |
| DS-AP-STRUCT-005 | AP | anti-patterns/structural/DS-AP-STRUCT-005-naming-nebula.md | RATIFIED | 2026-02-08 |
| DS-AP-CONT-001 | AP | anti-patterns/content/DS-AP-CONT-001-copy-paste-plague.md | RATIFIED | 2026-02-08 |
| DS-AP-CONT-002 | AP | anti-patterns/content/DS-AP-CONT-002-blank-canvas.md | RATIFIED | 2026-02-08 |
| DS-AP-CONT-003 | AP | anti-patterns/content/DS-AP-CONT-003-jargon-jungle.md | RATIFIED | 2026-02-08 |
| DS-AP-CONT-004 | AP | anti-patterns/content/DS-AP-CONT-004-link-desert.md | RATIFIED | 2026-02-08 |
| DS-AP-CONT-005 | AP | anti-patterns/content/DS-AP-CONT-005-outdated-oracle.md | RATIFIED | 2026-02-08 |
| DS-AP-CONT-006 | AP | anti-patterns/content/DS-AP-CONT-006-example-void.md | RATIFIED | 2026-02-08 |
| DS-AP-CONT-007 | AP | anti-patterns/content/DS-AP-CONT-007-formulaic-description.md | RATIFIED | 2026-02-08 |
| DS-AP-CONT-008 | AP | anti-patterns/content/DS-AP-CONT-008-silent-agent.md | RATIFIED | 2026-02-08 |
| DS-AP-CONT-009 | AP | anti-patterns/content/DS-AP-CONT-009-versionless-drift.md | RATIFIED | 2026-02-08 |
| DS-AP-STRAT-001 | AP | anti-patterns/strategic/DS-AP-STRAT-001-automation-obsession.md | RATIFIED | 2026-02-08 |
| DS-AP-STRAT-002 | AP | anti-patterns/strategic/DS-AP-STRAT-002-monolith-monster.md | RATIFIED | 2026-02-08 |
| DS-AP-STRAT-003 | AP | anti-patterns/strategic/DS-AP-STRAT-003-meta-documentation-spiral.md | RATIFIED | 2026-02-08 |
| DS-AP-STRAT-004 | AP | anti-patterns/strategic/DS-AP-STRAT-004-preference-trap.md | RATIFIED | 2026-02-08 |
| DS-AP-ECO-001 | AP | anti-patterns/ecosystem/DS-AP-ECO-001-index-island.md | RATIFIED | 2026-02-08 |
| DS-AP-ECO-002 | AP | anti-patterns/ecosystem/DS-AP-ECO-002-phantom-links.md | RATIFIED | 2026-02-08 |
| DS-AP-ECO-003 | AP | anti-patterns/ecosystem/DS-AP-ECO-003-shadow-aggregate.md | RATIFIED | 2026-02-08 |
| DS-AP-ECO-004 | AP | anti-patterns/ecosystem/DS-AP-ECO-004-duplicate-ecosystem.md | RATIFIED | 2026-02-08 |
| DS-AP-ECO-005 | AP | anti-patterns/ecosystem/DS-AP-ECO-005-token-black-hole.md | RATIFIED | 2026-02-08 |
| DS-AP-ECO-006 | AP | anti-patterns/ecosystem/DS-AP-ECO-006-orphan-nursery.md | RATIFIED | 2026-02-08 |

> **Note:** Registry will be populated as standard files are authored across Phases A–D.
> Phase A populates 9 example files (including 3 DC exemplars: E001, W001, I001).
> Phase B adds 35 new diagnostic codes, bringing the DC total to 38/38.
> Phase C adds 29 new validation criteria (STR-002 through STR-009, CON-001 through CON-013,
> APD-001 through APD-008). STR-001 already exists from Phase A.
> **Count reconciliation:** Strategy counts assume no overlap. Actual unique totals:
> Phase A = 9, Phase B = +35 (44 total), Phase C = +29 (73 total).
> Strategy §6.7 states "30 new entries; total = 77" but double-counts STR-001 (Phase A)
> and carries forward the Phase B inflation (47 → 44). Correct unique total: 73.
> Phase D adds ~69 supporting standards. Phase E ratifies all entries.

## 3. Integrity Assertions

These assertions are verified by the validation pipeline at startup. All must PASS before external validation proceeds.

| ID | Assertion | Expected | Status |
|----|-----------|----------|--------|
| IA-001 | Total RATIFIED standard files | 144 | PASS |
| IA-002 | RATIFIED VC (criteria) files | 30 | PASS |
| IA-003 | RATIFIED DC (diagnostic) files | 38 | PASS |
| IA-004 | RATIFIED AP (anti-pattern) files | 28 | PASS |
| IA-005 | RATIFIED DD (decision) files | 16 | PASS |
| IA-006 | RATIFIED CN (canonical name) files | 11 | PASS |
| IA-007 | RATIFIED VL (level) files | 5 | PASS |
| IA-008 | RATIFIED QS (scoring) files | 5 | PASS |
| IA-009 | RATIFIED EH (ecosystem) files | 5 | PASS |
| IA-010 | RATIFIED CS (calibration) files | 6 | PASS |
| IA-011 | Sum of STR dimension weights | 30 | PASS |
| IA-012 | Sum of CON dimension weights | 50 | PASS |
| IA-013 | Sum of APD dimension weights | 20 | PASS |
| IA-014 | Every DC file referenced by ≥1 VC file | True (with L0/ecosystem exceptions) | PASS |
| IA-015 | Every VC file references ≥1 DC file | True (with exceptions) | PASS |
| IA-016 | No broken DS identifier references | 0 broken | PASS |
| IA-017 | Calibration specimen count ≥ 5 | ≥5 | PASS |
| IA-018 | All calibration scores within 0–100 | True | PASS |
| IA-019 | Grade thresholds match code | True | PASS |
| IA-020 | No [TBD] tags in RATIFIED files | 0 occurrences | PASS |

## 4. Provenance Map

| DS Identifier | Primary Source | Secondary Sources |
|---------------|---------------|-------------------|
| DS-VC-STR-001 | RR-SPEC-v0.0.6 §L1-01; llms.txt spec §1 | diagnostics.py (E001), v0.0.2c audit |
| DS-DC-E001 | diagnostics.py → DiagnosticCode.NO_H1_TITLE | RR-SPEC-v0.0.6 §L1-01 |
| DS-DC-W001 | diagnostics.py → DiagnosticCode.MISSING_BLOCKQUOTE | RR-SPEC-v0.0.6 §L2-01 |
| DS-DC-I001 | diagnostics.py → DiagnosticCode.NO_LLM_INSTRUCTIONS | RR-SPEC-v0.0.6 §L4-02 |
| DS-VL-L0 | validation.py → ValidationLevel.PARSEABLE | RR-SPEC-v0.0.6 §3.1 |
| DS-DD-014 | RR-SPEC-v0.0.6 §5 (Scoring Methodology) | quality.py (QualityDimension weights) |
| DS-DD-001 | v0.0.4d §Decision Log — DECISION-001 | Schema Models (all schema/*.py) |
| DS-DD-002 | v0.0.4d §Decision Log — DECISION-002 | Content Structure (enrichment.py) |
| DS-DD-003 | v0.0.4d §Decision Log — DECISION-003 | Parser (mistletoe, CommonMark 0.30 + GFM) |
| DS-DD-004 | v0.0.4d §Decision Log — DECISION-004 | Content Enrichment (Concept.id) |
| DS-DD-005 | v0.0.4d §Decision Log — DECISION-005 | Content Enrichment (RelationshipType enum) |
| DS-DD-006 | v0.0.4d §Decision Log — DECISION-006 | All Schema Models (Pydantic v2 BaseModel) |
| DS-DD-007 | v0.0.4d §Decision Log — DECISION-007 | Content Structure (deferred to v0.3.x) |
| DS-DD-008 | v0.0.4d §Decision Log — DECISION-008 | Content Enrichment (FewShotExample.concept_ids) |
| DS-DD-009 | v0.0.4d §Decision Log — DECISION-009 | Validation Pipeline (v0.2.4 timing) |
| DS-DD-010 | v0.0.4d §Decision Log — DECISION-010 | Content Criteria (W009, Master Index) |
| DS-DD-011 | v0.0.4d §Decision Log — DECISION-011 | Validation Pipeline (I006 diagnostic) |
| DS-DD-012 | v0.0.4d §Decision Log — DECISION-012 | Constants (CanonicalSectionName, SECTION_NAME_ALIASES) |
| DS-DD-013 | v0.0.4d §Decision Log — DECISION-013 | Constants (TOKEN_BUDGET_TIERS, SizeTier) |
| DS-DD-015 | v0.0.4d §Decision Log — DECISION-015 | Entire Validation Philosophy (MCP target) |
| DS-DD-016 | v0.0.4d §Decision Log — DECISION-016 | Anti-Pattern Detection (AntiPatternCategory enum) |
| DS-AP-CRIT-001 | constants.py → ANTI_PATTERN_REGISTRY["ghost_file"] | RR-SPEC-v0.0.6 §4.3 |
| DS-CS-001 | v0.0.2c frequency analysis | https://svelte.dev/llms.txt |
| DS-CN-001 | constants.py → CanonicalSectionName.MASTER_INDEX | v0.0.2c frequency analysis (87% adoption) |
| DS-DC-E002 | diagnostics.py → DiagnosticCode.MULTIPLE_H1 | llms.txt spec §1; v0.0.1a ABNF grammar |
| DS-DC-E003 | diagnostics.py → DiagnosticCode.INVALID_ENCODING | v0.0.4a §ENC-001 |
| DS-DC-E004 | diagnostics.py → DiagnosticCode.INVALID_LINE_ENDINGS | v0.0.4a §ENC-002 |
| DS-DC-E005 | diagnostics.py → DiagnosticCode.INVALID_MARKDOWN | v0.0.4a §MD-001 |
| DS-DC-E006 | diagnostics.py → DiagnosticCode.BROKEN_LINKS | v0.0.4a §LNK-002; v0.0.4c §CHECK-004 |
| DS-DC-E007 | diagnostics.py → DiagnosticCode.EMPTY_FILE | v0.0.4c §CHECK-001 (Ghost File) |
| DS-DC-E008 | diagnostics.py → DiagnosticCode.EXCEEDS_SIZE_LIMIT | v0.0.4a §SIZ-003; v0.0.4c §CHECK-003 |
| DS-DC-E009 | diagnostics.py → DiagnosticCode.NO_INDEX_FILE | v0.0.7 §5.1 |
| DS-DC-E010 | diagnostics.py → DiagnosticCode.ORPHANED_ECOSYSTEM_FILE | v0.0.7 §5.1 |
| DS-DC-W002 | diagnostics.py → DiagnosticCode.NON_CANONICAL_SECTION_NAME | v0.0.4a §NAM-001 |
| DS-DC-W003 | diagnostics.py → DiagnosticCode.LINK_MISSING_DESCRIPTION | v0.0.4b §CNT-004; v0.0.4c §CHECK-010 |
| DS-DC-W004 | diagnostics.py → DiagnosticCode.NO_CODE_EXAMPLES | v0.0.4b §CNT-007; v0.0.2c audit (r~0.65) |
| DS-DC-W005 | diagnostics.py → DiagnosticCode.CODE_NO_LANGUAGE | v0.0.4b §CNT-008 |
| DS-DC-W006 | diagnostics.py → DiagnosticCode.FORMULAIC_DESCRIPTIONS | v0.0.4b §CNT-005; v0.0.4c §CHECK-015 |
| DS-DC-W007 | diagnostics.py → DiagnosticCode.MISSING_VERSION_METADATA | v0.0.4b §CNT-015 |
| DS-DC-W008 | diagnostics.py → DiagnosticCode.SECTION_ORDER_NON_CANONICAL | v0.0.4a §STR-004 |
| DS-DC-W009 | diagnostics.py → DiagnosticCode.NO_MASTER_INDEX | v0.0.4a §STR-003; DECISION-010 |
| DS-DC-W010 | diagnostics.py → DiagnosticCode.TOKEN_BUDGET_EXCEEDED | v0.0.4a §SIZ-001; DECISION-013 |
| DS-DC-W011 | diagnostics.py → DiagnosticCode.EMPTY_SECTIONS | v0.0.4c §CHECK-011 (Blank Canvas) |
| DS-DC-W012 | diagnostics.py → DiagnosticCode.BROKEN_CROSS_FILE_LINK | v0.0.7 §5.2 |
| DS-DC-W013 | diagnostics.py → DiagnosticCode.MISSING_AGGREGATE | v0.0.7 §5.2 |
| DS-DC-W014 | diagnostics.py → DiagnosticCode.AGGREGATE_INCOMPLETE | v0.0.7 §5.2 |
| DS-DC-W015 | diagnostics.py → DiagnosticCode.INCONSISTENT_PROJECT_NAME | v0.0.7 §5.2 |
| DS-DC-W016 | diagnostics.py → DiagnosticCode.INCONSISTENT_VERSIONING | v0.0.7 §5.2 |
| DS-DC-W017 | diagnostics.py → DiagnosticCode.REDUNDANT_CONTENT | v0.0.7 §5.2 |
| DS-DC-W018 | diagnostics.py → DiagnosticCode.UNBALANCED_TOKEN_DISTRIBUTION | v0.0.7 §5.2 |
| DS-DC-I002 | diagnostics.py → DiagnosticCode.NO_CONCEPT_DEFINITIONS | v0.0.4b §CNT-013 |
| DS-DC-I003 | diagnostics.py → DiagnosticCode.NO_FEW_SHOT_EXAMPLES | v0.0.1b Gap #2 (P0) |
| DS-DC-I004 | diagnostics.py → DiagnosticCode.RELATIVE_URLS_DETECTED | v0.0.4a §LNK-003 |
| DS-DC-I005 | diagnostics.py → DiagnosticCode.TYPE_2_FULL_DETECTED | v0.0.1a enrichment (Document Type Classification) |
| DS-DC-I006 | diagnostics.py → DiagnosticCode.OPTIONAL_SECTIONS_UNMARKED | DECISION-011 (v0.0.4d) |
| DS-DC-I007 | diagnostics.py → DiagnosticCode.JARGON_WITHOUT_DEFINITION | v0.0.4b §CNT-014 |
| DS-DC-I008 | diagnostics.py → DiagnosticCode.NO_INSTRUCTION_FILE | v0.0.7 §5.3 |
| DS-DC-I009 | diagnostics.py → DiagnosticCode.CONTENT_COVERAGE_GAP | v0.0.7 §5.3 |
| DS-DC-I010 | diagnostics.py → DiagnosticCode.ECOSYSTEM_SINGLE_FILE | v0.0.7 §5.3 |
| DS-VC-STR-002 | RR-SPEC-v0.0.6 §L1-02; v0.0.1a ABNF grammar | diagnostics.py (E002), v0.0.2c audit |
| DS-VC-STR-003 | RR-SPEC-v0.0.6 §L1-03; official spec (blockquote "expected") | diagnostics.py (W001), v0.0.2c audit (55% compliance) |
| DS-VC-STR-004 | RR-SPEC-v0.0.6 §L1-04; official spec ("H2-delimited sections") | v0.0.1a ABNF grammar |
| DS-VC-STR-005 | RR-SPEC-v0.0.6 §L1-05; official spec (link format) | diagnostics.py (E006), v0.0.1a formal grammar |
| DS-VC-STR-006 | RR-SPEC-v0.0.6 §L1-06; v0.0.1a grammar | v0.0.2c audit (0% H3 section usage) |
| DS-VC-STR-007 | RR-SPEC-v0.0.6 §L3-06; v0.0.4a CHECK-STR-008 | diagnostics.py (W008), constants.py (CANONICAL_SECTION_ORDER) |
| DS-VC-STR-008 | RR-SPEC-v0.0.6 §L3-09; v0.0.4c anti-pattern catalog | constants.py (AP-CRIT-001 through AP-CRIT-004), DECISION-016 |
| DS-VC-STR-009 | RR-SPEC-v0.0.6 §L3-10; v0.0.4c anti-pattern catalog | constants.py (AP-STRUCT-001 through AP-STRUCT-005) |
| DS-VC-CON-001 | RR-SPEC-v0.0.6 §L2-01; v0.0.4b CHECK-CNT-003 | diagnostics.py (W003), v0.0.2c audit (r~0.45) |
| DS-VC-CON-002 | RR-SPEC-v0.0.6 §L2-02; official spec (links usable) | diagnostics.py (E006), v0.0.4c AP-CRIT-004 |
| DS-VC-CON-003 | RR-SPEC-v0.0.6 §L2-03; v0.0.4c anti-pattern catalog | v0.0.2b audit (12.5% placeholder rate), AP-CONT-002 |
| DS-VC-CON-004 | RR-SPEC-v0.0.6 §L2-04; v0.0.4c AP-STRUCT-002 | diagnostics.py (W011), v0.0.2c audit |
| DS-VC-CON-005 | RR-SPEC-v0.0.6 §L2-05; v0.0.4c AP-STRUCT-003 | v0.0.2c audit |
| DS-VC-CON-006 | RR-SPEC-v0.0.6 §L2-06; v0.0.2c audit | v0.0.2c: <20 char blockquotes in bottom quartile |
| DS-VC-CON-007 | RR-SPEC-v0.0.6 §L2-07; v0.0.4c AP-CONT-007 | diagnostics.py (W006), v0.0.2b auto-generation patterns |
| DS-VC-CON-008 | RR-SPEC-v0.0.6 §L3-01; DECISION-012 | diagnostics.py (W002), constants.py (CanonicalSectionName, SECTION_NAME_ALIASES) |
| DS-VC-CON-009 | RR-SPEC-v0.0.6 §L3-02; v0.0.4a CHECK-STR-009 | diagnostics.py (W009), v0.0.2d (87% vs 31% task success) |
| DS-VC-CON-010 | RR-SPEC-v0.0.6 §L3-03; v0.0.4b | diagnostics.py (W004), v0.0.2c (r~0.65 quality correlation) |
| DS-VC-CON-011 | RR-SPEC-v0.0.6 §L3-04; v0.0.4b | diagnostics.py (W005) |
| DS-VC-CON-012 | RR-SPEC-v0.0.6 §L3-05; DECISION-013 | diagnostics.py (W010), constants.py (TOKEN_BUDGET_TIERS) |
| DS-VC-CON-013 | RR-SPEC-v0.0.6 §L3-07; v0.0.1b Gap #2 | diagnostics.py (W007), v0.0.4c AP-CONT-009 |
| DS-VC-APD-001 | RR-SPEC-v0.0.6 §L4-01; v0.0.0 Stripe Pattern | diagnostics.py (I001), v0.0.4d DECISION-002 |
| DS-VC-APD-002 | RR-SPEC-v0.0.6 §L4-02; v0.0.1b Gap #7 | diagnostics.py (I002), v0.0.4d DECISION-002 Layer 2, AP-CONT-003 |
| DS-VC-APD-003 | RR-SPEC-v0.0.6 §L4-03; v0.0.4d DECISION-002 Layer 3 | diagnostics.py (I003), in-context learning research |
| DS-VC-APD-004 | RR-SPEC-v0.0.6 §L4-04; v0.0.4c anti-pattern catalog | constants.py (AP-CONT-001 through AP-CONT-009) |
| DS-VC-APD-005 | RR-SPEC-v0.0.6 §L4-05; v0.0.4c anti-pattern catalog | constants.py (AP-STRAT-001 through AP-STRAT-004) |
| DS-VC-APD-006 | RR-SPEC-v0.0.6 §L4-06; v0.0.4a token allocation | v0.0.2c (balanced distribution in top files) |
| DS-VC-APD-007 | RR-SPEC-v0.0.6 §L4-07; practical (MCP consumption) | diagnostics.py (I004), v0.0.4a link checks |
| DS-VC-APD-008 | RR-SPEC-v0.0.6 §L4-08; v0.0.4c AP-CONT-003 | diagnostics.py (I007), v0.0.1b Gap #7 |
| DS-VL-L1 | validation.py → ValidationLevel.L1_STRUCTURAL | RR-SPEC-v0.0.6 §3.2; v0.0.4a structural checks |
| DS-VL-L2 | validation.py → ValidationLevel.L2_CONTENT | RR-SPEC-v0.0.6 §3.3; v0.0.4b content checks |
| DS-VL-L3 | validation.py → ValidationLevel.L3_BEST_PRACTICES | RR-SPEC-v0.0.6 §3.4; v0.0.4a/b/c best practice checks |
| DS-VL-L4 | validation.py → ValidationLevel.L4_DOCSTRATUM_EXTENDED | RR-SPEC-v0.0.6 §3.5; v0.0.4d DocStratum enrichment |
| DS-AP-CRIT-002 | constants.py → ANTI_PATTERN_REGISTRY[AP-CRIT-002] | v0.0.4c §Anti-Patterns Catalog; v0.0.2c audit |
| DS-AP-CRIT-003 | constants.py → ANTI_PATTERN_REGISTRY[AP-CRIT-003] | v0.0.4c §Anti-Patterns; v0.0.4a §ENC-001, §ENC-002 |
| DS-AP-CRIT-004 | constants.py → ANTI_PATTERN_REGISTRY[AP-CRIT-004] | v0.0.4c §Anti-Patterns; v0.0.4a §LNK-002 |
| DS-AP-STRUCT-001 | constants.py → ANTI_PATTERN_REGISTRY[AP-STRUCT-001] | v0.0.4c §Anti-Patterns Catalog |
| DS-AP-STRUCT-002 | constants.py → ANTI_PATTERN_REGISTRY[AP-STRUCT-002] | v0.0.4c §Anti-Patterns Catalog |
| DS-AP-STRUCT-003 | constants.py → ANTI_PATTERN_REGISTRY[AP-STRUCT-003] | v0.0.4c §Anti-Patterns Catalog |
| DS-AP-STRUCT-004 | constants.py → ANTI_PATTERN_REGISTRY[AP-STRUCT-004] | v0.0.4c §Anti-Patterns; constants.py (CANONICAL_SECTION_ORDER) |
| DS-AP-STRUCT-005 | constants.py → ANTI_PATTERN_REGISTRY[AP-STRUCT-005] | v0.0.4c §Anti-Patterns; constants.py (CanonicalSectionName, SECTION_NAME_ALIASES) |
| DS-AP-CONT-001 | constants.py → ANTI_PATTERN_REGISTRY[AP-CONT-001] | v0.0.4c §Anti-Patterns Catalog |
| DS-AP-CONT-002 | constants.py → ANTI_PATTERN_REGISTRY[AP-CONT-002] | v0.0.4c §Anti-Patterns Catalog |
| DS-AP-CONT-003 | constants.py → ANTI_PATTERN_REGISTRY[AP-CONT-003] | v0.0.4c §Anti-Patterns; v0.0.4b §CNT-014 |
| DS-AP-CONT-004 | constants.py → ANTI_PATTERN_REGISTRY[AP-CONT-004] | v0.0.4c §Anti-Patterns; v0.0.4b §CNT-004 |
| DS-AP-CONT-005 | constants.py → ANTI_PATTERN_REGISTRY[AP-CONT-005] | v0.0.4c §Anti-Patterns Catalog |
| DS-AP-CONT-006 | constants.py → ANTI_PATTERN_REGISTRY[AP-CONT-006] | v0.0.4c §Anti-Patterns; v0.0.4b §CNT-007 (r~0.65) |
| DS-AP-CONT-007 | constants.py → ANTI_PATTERN_REGISTRY[AP-CONT-007] | v0.0.4c; v0.0.4b §CNT-005; v0.0.2b auto-generation patterns |
| DS-AP-CONT-008 | constants.py → ANTI_PATTERN_REGISTRY[AP-CONT-008] | v0.0.4c; v0.0.0 Stripe Pattern; v0.0.1b Gap Analysis |
| DS-AP-CONT-009 | constants.py → ANTI_PATTERN_REGISTRY[AP-CONT-009] | v0.0.4c; v0.0.1b Gap #2 |
| DS-AP-STRAT-001 | constants.py → ANTI_PATTERN_REGISTRY[AP-STRAT-001] | v0.0.4c §Anti-Patterns Catalog |
| DS-AP-STRAT-002 | constants.py → ANTI_PATTERN_REGISTRY[AP-STRAT-002] | v0.0.4c §Anti-Patterns; v0.0.4a §SIZ-003 |
| DS-AP-STRAT-003 | constants.py → ANTI_PATTERN_REGISTRY[AP-STRAT-003] | v0.0.4c §Anti-Patterns Catalog |
| DS-AP-STRAT-004 | constants.py → ANTI_PATTERN_REGISTRY[AP-STRAT-004] | v0.0.4c §Anti-Patterns Catalog |
| DS-AP-ECO-001 | constants.py → ANTI_PATTERN_REGISTRY[AP-ECO-001] | v0.0.7 §6 (Ecosystem Anti-Patterns) |
| DS-AP-ECO-002 | constants.py → ANTI_PATTERN_REGISTRY[AP-ECO-002] | v0.0.7 §6 (Ecosystem Anti-Patterns) |
| DS-AP-ECO-003 | constants.py → ANTI_PATTERN_REGISTRY[AP-ECO-003] | v0.0.7 §6 (Ecosystem Anti-Patterns) |
| DS-AP-ECO-004 | constants.py → ANTI_PATTERN_REGISTRY[AP-ECO-004] | v0.0.7 §6 (Ecosystem Anti-Patterns) |
| DS-AP-ECO-005 | constants.py → ANTI_PATTERN_REGISTRY[AP-ECO-005] | v0.0.7 §6 (Ecosystem Anti-Patterns) |
| DS-AP-ECO-006 | constants.py → ANTI_PATTERN_REGISTRY[AP-ECO-006] | v0.0.7 §6 (Ecosystem Anti-Patterns) |
| DS-CN-002 | constants.py → CanonicalSectionName.LLM_INSTRUCTIONS | v0.0.4d DECISION-002 Layer 1 |
| DS-CN-003 | constants.py → CanonicalSectionName.GETTING_STARTED | v0.0.2c frequency audit (78% adoption) |
| DS-CN-004 | constants.py → CanonicalSectionName.CORE_CONCEPTS | v0.0.2c frequency audit (40% adoption) |
| DS-CN-005 | constants.py → CanonicalSectionName.API_REFERENCE | v0.0.2c frequency audit (61% adoption) |
| DS-CN-006 | constants.py → CanonicalSectionName.EXAMPLES | v0.0.2c frequency audit (54% adoption) |
| DS-CN-007 | constants.py → CanonicalSectionName.CONFIGURATION | v0.0.2c frequency audit (58% adoption) |
| DS-CN-008 | constants.py → CanonicalSectionName.ADVANCED_TOPICS | v0.0.2c frequency audit (42% adoption) |
| DS-CN-009 | constants.py → CanonicalSectionName.TROUBLESHOOTING | v0.0.2c frequency audit (52% adoption) |
| DS-CN-010 | constants.py → CanonicalSectionName.FAQ | v0.0.2c frequency audit (45% adoption) |
| DS-CN-011 | constants.py → CanonicalSectionName.OPTIONAL | DECISION-011 (optional sections explicitly marked) |
| DS-QS-DIM-STR | quality.py → QualityDimension.STRUCTURAL (weight=30) | DECISION-014; v0.0.4b structural checks |
| DS-QS-DIM-CON | quality.py → QualityDimension.CONTENT (weight=50) | DECISION-014; v0.0.2c correlation analysis |
| DS-QS-DIM-APD | quality.py → QualityDimension.ANTI_PATTERN (weight=20) | DECISION-014; DECISION-016 |
| DS-QS-GRADE | quality.py → QualityGrade enum, from_score() method | DECISION-014; thresholds 90/70/50/30 |
| DS-QS-GATE | quality.py → DimensionScore.is_gated; structural gating cap at 29 | DECISION-016; AP-CRIT-001–004 |
| DS-EH-COV | ecosystem.py → EcosystemHealthDimension.COVERAGE | v0.0.7 §5.1 (file_coverage_ratio) |
| DS-EH-CONS | ecosystem.py → EcosystemHealthDimension.CONSISTENCY | v0.0.7 §5.2 (cross-file consistency) |
| DS-EH-COMP | ecosystem.py → EcosystemHealthDimension.COMPLETENESS | v0.0.7 §5.3 (section completeness) |
| DS-EH-TOK | ecosystem.py → EcosystemHealthDimension.TOKEN_EFFICIENCY | v0.0.7 §5.4 (token budget utilization) |
| DS-EH-FRESH | ecosystem.py → EcosystemHealthDimension.FRESHNESS | v0.0.7 §5.5 (documentation age tracking) |
| DS-CS-002 | v0.0.2c frequency analysis | https://docs.pydantic.dev/llms.txt |
| DS-CS-003 | v0.0.2c frequency analysis | https://sdk.vercel.ai/llms.txt |
| DS-CS-004 | v0.0.2c frequency analysis | https://ui.shadcn.com/llms.txt |
| DS-CS-005 | v0.0.2c frequency analysis | https://docs.cursor.com/llms.txt |
| DS-CS-006 | v0.0.2c frequency analysis | https://docs.nvidia.com/llms.txt |

> **Note:** Provenance map fully populated — 144 entries matching File Registry. Phase E ratification complete.

## 5. Change Log

| ASoT Version | Date | Change | Affected Identifiers |
|--------------|------|--------|---------------------|
| 0.0.0-scaffold | 2026-02-08 | Initial scaffolding — directory tree and manifest structure created | None (structure only) |
| 0.0.0-scaffold | 2026-02-08 | Phase A example files authored (9 DRAFT entries) | DS-VC-STR-001, DS-DC-E001, DS-DC-W001, DS-DC-I001, DS-VL-L0, DS-DD-014, DS-AP-CRIT-001, DS-CS-001, DS-CN-001 |
| 0.0.0-scaffold | 2026-02-08 | Path A resolution: DS-VC-STR-001 reverted from compound "Parseable Prerequisites" (L0) to atomic "H1 Title Present" (L1-01). L0 criteria deferred to Phase C. Updated DS-DC-E001, DS-VL-L0, DS-AP-CRIT-001, DS-CS-001 references. | DS-VC-STR-001, DS-DC-E001, DS-VL-L0, DS-AP-CRIT-001, DS-CS-001 |
| 0.0.0-scaffold | 2026-02-08 | Phase B complete: 35 new diagnostic code files authored (E002–E010, W002–W018, I002–I010). Total DC files: 38/38. All README indexes updated. Error file slugs corrected. Warning Code field values normalized from enum names to short codes. | DS-DC-E002 through DS-DC-E010, DS-DC-W002 through DS-DC-W018, DS-DC-I002 through DS-DC-I010 |
| 0.0.0-scaffold | 2026-02-08 | Phase B audit fixes: (1) Bold formatting added to metadata field names in 35 files per Template B.2, (2) "Triggering Criterion" normalized to "Triggering Criteria" in 19 files, (3) Change History columns corrected from "Version/Date/Notes" to "ASoT Version/Date/Change" in 35 files. Count reconciliation note added to registry (44 unique entries, not 47 per §5.7.5 due to 3 shared DC exemplars). | All Phase B DC files (E002–E010, W002–W018, I002–I010) |
| 0.0.0-scaffold | 2026-02-08 | Phase C complete: 29 new validation criterion files authored (STR-002 through STR-009, CON-001 through CON-013, APD-001 through APD-008). 4 criteria README indexes updated. DS-VL-L0 updated to clarify L0 criteria are pipeline prerequisite gates (no VC files) per Path A resolution. Weight accounting: STR=30, CON=50, APD=20 (all). Total registry entries: 73. | DS-VC-STR-002 through DS-VC-STR-009, DS-VC-CON-001 through DS-VC-CON-013, DS-VC-APD-001 through DS-VC-APD-008, DS-VL-L0 |
| 0.0.0-scaffold | 2026-02-08 | Phase D.1 complete: 4 new validation level files authored (L1–L4). Levels README index updated with complete 5-level table and criteria distribution matrix. Each level file documents criteria, entry/exit conditions, diagnostic codes, and scoring impact per VL-L0 template. Total registry entries: 77. | DS-VL-L1, DS-VL-L2, DS-VL-L3, DS-VL-L4 |
| 0.0.0-scaffold | 2026-02-08 | Phase D.2 complete: 27 new anti-pattern files authored (3 critical, 5 structural, 9 content, 4 strategic, 6 ecosystem). 6 anti-pattern README indexes updated. Each file documents detection logic, synthetic examples, remediation, and cross-references per Template B.3. Critical README data error corrected (AP-CONT-001 → AP-CRIT-001). Total registry entries: 104. | DS-AP-CRIT-002 through DS-AP-CRIT-004, DS-AP-STRUCT-001 through DS-AP-STRUCT-005, DS-AP-CONT-001 through DS-AP-CONT-009, DS-AP-STRAT-001 through DS-AP-STRAT-004, DS-AP-ECO-001 through DS-AP-ECO-006 |
| 0.0.0-scaffold | 2026-02-08 | Phase D.3 complete: 15 new design decision files authored (DD-001 through DD-016, minus existing DD-014). Decisions README index updated with all 16 entries. Each file documents the decision, context, alternatives considered, rationale, ASoT impact, and constraints per DD-014 exemplar template. Total registry entries: 119. | DS-DD-001 through DS-DD-013, DS-DD-015, DS-DD-016 |
| 0.0.0-scaffold | 2026-02-08 | Phase D.4 complete: 10 new canonical name files authored (CN-002 through CN-011). Canonical README index updated with all 11 entries. Each file documents the section name, position, aliases, and related criteria per CN-001 exemplar template. | DS-CN-002 through DS-CN-011 (10 new) |
| 0.0.0-scaffold | 2026-02-08 | Phase D.5 complete: 5 new quality scoring framework files authored (3 dimensions, 1 grade thresholds, 1 gating rule). Scoring README index updated. Each file documents scoring logic, weight, criteria mappings, and implementation reference. | DS-QS-DIM-STR, DS-QS-DIM-CON, DS-QS-DIM-APD, DS-QS-GRADE, DS-QS-GATE |
| 0.0.0-scaffold | 2026-02-08 | Phase D.6 complete: 5 new ecosystem health dimension files authored (Coverage, Consistency, Completeness, Token Efficiency, Freshness). Ecosystem README index updated. Each file documents the measurement approach and related anti-patterns. | DS-EH-COV, DS-EH-CONS, DS-EH-COMP, DS-EH-TOK, DS-EH-FRESH |
| 0.0.0-scaffold | 2026-02-08 | Phase D.7 complete: 5 new calibration specimen files authored (Pydantic 90, Vercel SDK 90, Shadcn UI 89, Cursor 42, NVIDIA 24). Calibration README index updated. Full quality spectrum coverage from Critical to Exemplary. Total registry entries: 144. Phase D complete. | DS-CS-002 through DS-CS-006 (5 new) |
| 1.0.0 | 2026-02-08 | Phase E ratification — all 144 files promoted from DRAFT to RATIFIED, version stamped 1.0.0. Integrity fixes: (1) 3 QS dimension files rewritten with correct criteria tables (STR had wrong weights summing to 27, CON had stale criteria set, APD had incorrect deduction-based model), (2) 25 missing provenance entries added (CN-002–011, CS-002–006, all QS, all EH), (3) IA-001 expected count corrected from 146 to 144, (4) IA-014 updated to document L0/ecosystem DC exceptions, (5) DS-CONST-004 broken reference in DD-012 replaced with correct constants.py citation, (6) stale Path B artifact (DS-VC-STR-001-parseable-prerequisites.md) deleted, (7) 70 tags removed from 30 VC files per weight ratification proposal, (8) all 20 integrity assertions verified PASS. | All 144 DS-* files |
