# DS-DD-007: CSV for Relationship Matrices (not JSON)

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DD-007 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Decision ID** | DECISION-007 |
| **Date Decided** | 2026-01-28 (v0.0.4d) |
| **Impact Area** | Content Structure (v0.3.x — data storage format for concept graphs; deferred from v0.1.x) |
| **Provenance** | v0.0.4d §Differentiators and Decision Log |

## Decision

**Concept relationship matrices are stored in CSV format rather than JSON. The standard format is fixed: `source_id,relationship_type,target_id` per row, with one relationship defined per line.**

## Context

The ASoT standards require modeling the relationships between documentation concepts (e.g., "AUTH-001 relates-to AUTH-002"). These concept graphs need to be stored in a format that is:
- **Human-readable** in standard text editors and version control systems
- **Version-control friendly** with clear git diffs that show exactly what changed
- **Easy to import** into spreadsheet applications for visualization and manual curation
- **Simple to parse** with standard Python libraries (csv module)

During v0.0.4c testing, relationship data was prototyped in both JSON and CSV formats. The CSV approach proved superior for collaborative editing and VCS workflows, where stakeholders often review relationship changes in pull requests.

This decision is **deferred from v0.1.x implementation** — the relationship matrix structure is designed now but actual storage in documentation sets is planned for v0.3.x after core generator and validator are stable.

## Alternatives Considered

| Option | Rationale For | Rationale Against |
|--------|---------------|-------------------|
| JSON | Nested structure; can represent complex metadata; widely used for configuration | Nesting complexity makes relationship lists hard to read in raw form; JSON diffs are verbose and difficult to review; spreadsheet import requires conversion; version control diffs are noisy |
| **CSV (Chosen)** | Flat, row-oriented format; human-readable in text editors; clear git diffs showing each row change; standard Python csv module; import directly into Excel/Sheets; simple parsing logic | Requires strict formatting; metadata must be encoded as separate columns; no nested structures; single delimiter shared across all columns |
| RDF (Resource Description Framework) | Semantically rich; standards-based; supports inference engines | Overkill for DocStratum use case; steep learning curve; requires specialized tooling; poor VCS readability |
| Graph Database (Neo4j) | Optimized for relationship queries; efficient traversal; powerful query language | Introduces external dependency; requires database setup; difficult to version control; not portable across environments; steep operational overhead |

## Rationale

CSV was chosen because it aligns with ASoT's philosophy of **portable, human-centric standards**. The format is:

1. **VCS-Friendly**: A changed relationship appears as a single modified line in git history, making PR reviews clear and auditable.
2. **Spreadsheet-Compatible**: Concept maintainers can open the CSV in Excel, visualize relationships, and spot gaps or errors visually.
3. **Low Friction**: No special tooling required to view or edit relationship data — any text editor works.
4. **Standardized**: The csv module is part of Python standard library; no extra dependencies.

The three-column format (source_id, relationship_type, target_id) is strict by design. This simplicity prevents schema creep and keeps the relationship matrix focused on its single purpose: expressing conceptual links.

## Impact on ASoT

This decision impacts several areas of the Content Structure validation criteria (v0.3.x):

- **DS-VC-CON-007** (Relationship Matrix Present): Files must include a CSV relationship matrix if they define multiple concepts
- **DS-VC-CON-008** (Relationship Validity): Relationships must reference valid concept IDs; validation parser will read CSV rows and cross-reference against concept registry
- **DS-VC-CON-010** (Graph Connectivity): Analysis of concept graphs depends on parsing the CSV relationship format; algorithms must handle the fixed three-column structure

The validator (v0.2.4+) and any future relationship analysis tools must implement CSV parsing. Export formats (e.g., to JSON for API responses) may transform CSV to other representations, but the canonical storage format remains CSV.

## Constraints Imposed

1. **Fixed Column Structure**: Exactly three columns: `source_id`, `relationship_type`, `target_id`. Column order is mandatory.
2. **Standard Delimiter**: Must use comma (U+002C) as the field delimiter. No other delimiters permitted.
3. **No Headers**: CSV files must not include a header row; the first line is data.
4. **Relationship Type Enumeration**: The `relationship_type` column must contain values from the `RelationshipType` enum (defined in `constants.py`). Invalid types cause validation errors.
5. **ID Validation**: Both `source_id` and `target_id` must exist in the active concept registry at validation time.
6. **Quoting Rules**: Fields containing commas must be quoted per RFC 4180. IDs should not contain commas.

## Related Decisions

- **DS-DD-005** (Relationship types enumeration and cardinality rules — stored and validated against CSV rows)
- **DS-DD-004** (Concept ID format — the IDs referenced in CSV columns must conform to this format)
- **DS-DD-009** (Validation pipeline includes CSV relationship parsing and validation)
- **DS-DD-016** (Severity classification — invalid relationships are classified as errors or warnings based on this decision)

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.3 |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
