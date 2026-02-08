# DS-DC-W003: LINK_MISSING_DESCRIPTION

| Field | Value |
|-------|-------|
| DS Identifier | DS-DC-W003 |
| Status | DRAFT |
| ASoT Version | 0.0.0-scaffold |
| Code | W003 |
| Severity | WARNING |
| Validation Level | L2 — Content Quality |
| Check ID | CNT-004 (v0.0.4b), CHECK-010 (v0.0.4c Link Desert) |
| Provenance | v0.0.4b content checks; v0.0.4c anti-patterns; v0.0.2c: descriptions have r~0.45 quality correlation |

## Message

> Link entry has no description text (bare URL only).

## Remediation

> Add a description after the link: '- [Title](url): Description of the page'.

## Description

Links without descriptions provide minimal context and force readers to click in order to understand what they will find. A bare URL conveys no semantic meaning and makes the documentation harder to scan. Research shows that descriptions of links have a moderate-to-strong correlation (r~0.45) with overall content quality, as they signal author effort and reduce cognitive load.

Context is essential for effective linking. Descriptions should explain why the link is relevant, what the reader will find, and how it relates to the current topic. Without this framing, links become orphaned references that fail to integrate with the surrounding narrative.

### When This Code Fires

W003 fires when a link appears in a markdown list or inline context with no accompanying description text. This includes bare URLs presented without markdown link syntax, and markdown links with no text following the URL.

### When This Code Does NOT Fire

W003 does not fire when a link includes descriptive text (e.g., '- [Title](url): Description of the page'), or when the link is part of a sentence that provides sufficient context.

## Triggering Criterion

**DS-VC-CON-001: Non-Empty Descriptions**

Links must include descriptive text that explains their relevance and content. This criterion validates that links are not presented as bare URLs.

## Related Anti-Patterns

**DS-AP-CONT-004: Link Desert** — An area of the documentation consisting primarily of bare links with no descriptions, creating a sparse, navigation-heavy experience.

## Related Diagnostic Codes

**DS-DC-E006: (E006 error — malformed URLs)** — E006 detects syntactically malformed URLs, while W003 detects missing descriptions. These are different problems with links; a link can be well-formed but lack a description.

## Change History

| Version | Date | Notes |
|---------|------|-------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
