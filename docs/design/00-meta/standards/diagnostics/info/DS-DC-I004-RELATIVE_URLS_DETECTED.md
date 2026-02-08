# DS-DC-I004: RELATIVE_URLS_DETECTED

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DC-I004 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Code** | I004 |
| **Severity** | INFO |
| **Validation Level** | L4 — DocStratum Extended |
| **Check ID** | LNK-003 (v0.0.4a) |
| **Provenance** | v0.0.4a link checks; AI agent URL resolution challenges |

## Message

> Relative URLs found in link entries (may need resolution).

## Remediation

> Convert relative URLs to absolute or document the base URL.

## Description

This informational code indicates that the document contains relative URLs (e.g., `./doc.md`, `../other/page`) in link entries. While relative URLs can be valid in certain contexts (e.g., local file systems, version-controlled repositories), they present challenges for AI agents and external consumers who may not have access to the document's base path or directory structure.

Relative URLs can cause broken links when documents are moved, shared outside their original context, or consumed by agents unfamiliar with the directory structure. Converting relative URLs to absolute URLs—or explicitly documenting the base URL context—improves portability and clarity, especially for automated link validation and AI-driven documentation systems.

**When This Code Fires:**
- One or more URLs in the document use relative path syntax (`./`, `../`, or relative file references).
- The base URL context is not explicitly documented.

**When This Code Does NOT Fire:**
- All URLs are absolute (beginning with `http://`, `https://`, or a documented base).
- Relative URLs are accompanied by explicit base URL documentation.

## Triggering Criteria

- **DS-VC-APD-007**: (Relative URL Minimization)

Emitted by DS-VC-APD-007 when relative URLs are detected in link entries.
## Related Anti-Patterns

None directly identified.

## Related Diagnostic Codes

- **DS-DC-E006** (BROKEN_MALFORMED_LINKS): More severe link issues; E006 fires for broken/malformed links.
- **DS-DC-W003** (MISSING_LINK_DESCRIPTIONS): Different link issue; W003 addresses missing context/descriptions.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
| 0.0.0-scaffold | 2026-02-08 | Phase C backfill — added VC cross-references to Triggering Criteria section |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
