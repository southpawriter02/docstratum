# DS-DC-E006: BROKEN_LINKS

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DC-E006 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Code** | E006 |
| **Severity** | ERROR |
| **Validation Level** | L1 — Structurally Valid (also emitted at L2 by DS-VC-CON-002) |
| **Check ID** | LNK-002 (v0.0.4a), CHECK-004 (v0.0.4c) |
| **Provenance** | Markdown link syntax; v0.0.4a/c structural checks |

## Message

> Section contains links with empty or malformed URLs.

## Remediation

> Fix or remove links with empty href values. Ensure all URLs are well-formed.

## Description

This error fires when a document contains links (in standard Markdown or HTML syntax) that have empty, null, or severely malformed URL destinations. A link without a valid href is non-functional and breaks user navigation. The link syntax itself may be valid Markdown, but the underlying URL data is invalid or missing.

This check is performed at both L1 (structural validation) and L2 (content validation) stages. L1 catches links with empty href attributes or obvious syntax violations. L2 catches broken cross-file references and external URLs that fail resolution.

### When This Code Fires

- A link element (Markdown `[text](url)` or HTML `<a href="">`) has an empty href value.
- A link has a href that is malformed (e.g., contains invalid characters that break URL parsing).
- This check occurs at L1 (STR-005) and again at L2 (CON-002) with different granularity.

### When This Code Does NOT Fire

- All links in the document have valid, non-empty href values.
- Link destinations are well-formed (valid URLs, local file references, or anchors).
- Links are properly removed or updated during editing rather than left empty.

## Triggering Criteria

- **DS-VC-STR-005**: (Link Format Compliance)
- **DS-VC-CON-002**: (URL Resolvability)

Emitted by DS-VC-STR-005 for syntactically malformed links and by DS-VC-CON-002 for links that fail HTTP resolution.
## Related Anti-Patterns

- DS-AP-CRIT-004 (Link Void)

## Related Diagnostic Codes

- DS-DC-W003 (bare links without descriptions — related but different: E006 detects malformed or empty URLs; W003 detects properly formed links that lack descriptive text)

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
| 0.0.0-scaffold | 2026-02-08 | Phase C backfill — added VC cross-references to Triggering Criteria section |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
