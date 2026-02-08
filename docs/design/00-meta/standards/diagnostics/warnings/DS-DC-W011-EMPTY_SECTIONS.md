# DS-DC-W011: EMPTY_SECTIONS

| Field | Value |
|-------|-------|
| DS Identifier | DS-DC-W011 |
| Status | DRAFT |
| ASoT Version | 0.0.0-scaffold |
| Code | W011 |
| Severity | WARNING |
| Validation Level | L2 — Content Quality |
| Check ID | CHECK-011 (v0.0.4c Blank Canvas anti-pattern) |
| Provenance | v0.0.4c anti-patterns catalog; v0.0.2b audit data |

## Message

> One or more sections contain no meaningful content (placeholder text only).

## Remediation

> Add content or remove empty sections. Placeholder sections waste tokens.

## Description

Empty sections represent incomplete work, wasted space, and broken promises to readers. A section heading signals to readers that meaningful content will follow; when they encounter only placeholder text (e.g., "TBD", "Coming soon", or empty content), their trust is broken and cognitive effort is wasted. Placeholder sections consume tokens and visual real estate without providing value.

When a section is not yet ready for publication, it should either be removed entirely, completed, or explicitly marked as under construction if its inclusion serves a documented purpose. Placeholder sections that exist solely because a template included them represent a failure of editorial discipline.

### When This Code Fires

W011 fires when one or more sections contain only placeholder text, whitespace, or no meaningful content. This includes sections with only TBD, empty statements, or other indicators that the section was intended as a template stub but was never completed.

### When This Code Does NOT Fire

W011 does not fire when all sections contain substantive content, even if sections are brief. It also does not fire for sections explicitly marked as placeholders in a formal "Under Construction" or "Draft" status context.

## Triggering Criterion

**DS-VC-CON-004: Non-Empty Sections**

All sections must contain meaningful content. Placeholder sections are not acceptable. This criterion validates that sections are complete and substantive.

## Related Anti-Patterns

**DS-AP-CONT-002: Blank Canvas** — A section-level manifestation of emptiness, where section headings exist but contain no substantive content, creating a skeletal document.

## Related Diagnostic Codes

**DS-DC-E007: (E007 error — entire file empty)** — E007 detects when an entire file is empty at the L0 level, which is a critical error. W011 detects when individual sections within a file are empty at the L2 content quality level. E007 is blocking; W011 is an advisory warning about incomplete sections.

## Change History

| Version | Date | Notes |
|---------|------|-------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
