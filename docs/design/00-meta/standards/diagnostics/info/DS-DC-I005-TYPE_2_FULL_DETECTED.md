# DS-DC-I005: TYPE_2_FULL_DETECTED

| Field | Value |
|-------|-------|
| DS Identifier | DS-DC-I005 |
| Status | DRAFT |
| ASoT Version | 0.0.0-scaffold |
| Code | I005 |
| Severity | INFO |
| Validation Level | L4 — DocStratum Extended |
| Check ID | Document Type Classification (v0.0.1a enrichment) |
| Provenance | v0.0.1a document type classification; TYPE_BOUNDARY_BYTES=256000 |

## Message

> File classified as Type 2 Full (inline documentation dump, >250 KB).

## Remediation

> Consider creating a Type 1 Index companion file.

## Description

This informational code indicates that the document has been classified as a **Type 2 Full** document—a single, comprehensive file containing extensive inline documentation, typically exceeding 250 KB in size. Type 2 Full files are legitimate document forms but present context and navigation challenges, especially for AI agents with limited token budgets.

Type 2 Full documents consolidate all content into one file, prioritizing completeness and self-containedness over modular structure. While this approach simplifies single-file consumption, it can overwhelm agents during initial indexing and requires readers to scan or search for specific information. Creating a companion **Type 1 Index** file (a structured outline with links to sections within the Type 2 Full document) improves navigation and enables agents to make selective content choices based on token budgets.

**When This Code Fires:**
- The document is classified as Type 2 Full (comprehensive, single-file format).
- File size exceeds approximately 250 KB (TYPE_BOUNDARY_BYTES=256000).

**When This Code Does NOT Fire:**
- The document is a Type 1 Index or other modular format.
- File size is under the Type 2 threshold.

## Triggering Criterion

No direct VC criterion per §5.7 (classification-level observation).

## Related Anti-Patterns

None directly identified.

## Related Diagnostic Codes

- **DS-DC-E008** (FILE_SIZE_LIMIT_EXCEEDED): More severe size issue; E008 fires for >100K tokens, I005 fires for Type 2 classification at >250 KB.

## Change History

| Version | Date | Notes |
|---------|------|-------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
