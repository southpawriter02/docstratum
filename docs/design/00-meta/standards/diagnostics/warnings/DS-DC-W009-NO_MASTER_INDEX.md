# DS-DC-W009: NO_MASTER_INDEX

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DC-W009 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Code** | W009 |
| **Severity** | WARNING |
| **Validation Level** | L3 — Best Practices |
| **Check ID** | STR-003 (v0.0.4a), DECISION-010 |
| **Provenance** | DECISION-010 (Master Index as Navigation Root); v0.0.2c: 87% vs 31% LLM task success rate |

## Message

> No Master Index found as the first H2 section.

## Remediation

> Add a Master Index as the first H2 section with navigation links.

## Description

The Master Index serves as the navigation root for a document, enabling readers and tools to quickly locate sections and understand the document's structure. Research shows that documents with a Master Index achieve 87% LLM task success rate compared to 31% without one — a dramatic difference highlighting the critical importance of this navigational aid. The Master Index must appear as the first H2 section to establish a consistent location for navigation.

A well-structured Master Index with clear links transforms a document from a linear text into a navigable information space. This is especially important for longer documents, specifications, and reference material where readers need rapid access to specific sections.

### When This Code Fires

W009 fires when a file does not contain a Master Index section as the first H2-level heading. This includes files where a Master Index exists but is not the first H2, or files that lack a Master Index entirely.

### When This Code Does NOT Fire

W009 does not fire when a Master Index is present and is the first H2 section in the file, complete with navigation links to other major sections. It also does not fire for stub files or files explicitly exempt from index requirements.

## Triggering Criteria

- **DS-VC-CON-009**: (Master Index Present)

Emitted by DS-VC-CON-009 when no Master Index section is found as the first H2 section.
## Related Anti-Patterns

None directly related.

## Related Diagnostic Codes

**DS-DC-W002: NON_CANONICAL_SECTION_NAME** — Related in that the Master Index is itself a canonical section name (DS-CN-001); W002 checks that section names match the canonical set, of which Master Index is a critical member.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
| 0.0.0-scaffold | 2026-02-08 | Phase C backfill — added VC cross-references to Triggering Criteria section |
