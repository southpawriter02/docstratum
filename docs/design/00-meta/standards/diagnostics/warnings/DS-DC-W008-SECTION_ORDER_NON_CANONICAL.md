# DS-DC-W008: SECTION_ORDER_NON_CANONICAL

| Field | Value |
|-------|-------|
| DS Identifier | DS-DC-W008 |
| Status | DRAFT |
| ASoT Version | 0.0.0-scaffold |
| Code | W008 |
| Severity | WARNING |
| Validation Level | L3 — Best Practices |
| Check ID | STR-004 (v0.0.4a) |
| Provenance | v0.0.4a structural checks; v0.0.2c frequency analysis of section ordering |

## Message

> Sections do not follow the canonical 10-step ordering.

## Remediation

> Reorder sections to match canonical sequence (see v0.0.4a §6).

## Description

The canonical 10-step section ordering represents an optimal sequence for reader comprehension and information flow. When sections appear in a non-canonical order, readers may struggle to locate information and the document becomes harder to navigate. Frequency analysis of effective documentation shows that the canonical ordering significantly improves readability and navigation efficiency.

Canonical ordering ensures that foundational concepts precede advanced topics, that navigation aids appear early, and that supporting materials follow main content. Deviating from this sequence forces readers to jump between sections or rely on search to locate related information.

### When This Code Fires

W008 fires when a file contains sections that do not appear in the canonical 10-step ordering defined in v0.0.4a §6. This includes cases where sections are missing (handled separately), but focuses on cases where sections are reordered.

### When This Code Does NOT Fire

W008 does not fire when all sections appear in the canonical order, or when the file is explicitly exempt from section ordering (e.g., free-form documents or files with non-standard structure justified by their purpose).

## Triggering Criterion

**DS-VC-STR-007: Canonical Section Ordering**

Files must organize sections in the canonical 10-step sequence. This criterion validates that section order is consistent across the ecosystem.

## Related Anti-Patterns

**DS-AP-STRUCT-004: Section Shuffle** — Sections appear in random or inconsistent order, degrading navigation and reader comprehension.

## Related Diagnostic Codes

**DS-DC-W002: NON_CANONICAL_SECTION_NAME** — W002 checks that section names are canonical, while W008 checks that canonical sections appear in canonical order. Both address structural consistency but focus on different aspects: names vs. ordering.

## Change History

| Version | Date | Notes |
|---------|------|-------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
