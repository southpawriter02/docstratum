# DS-DD-003: GitHub Flavored Markdown (GFM) as Standard

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DD-003 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Decision ID** | DECISION-003 |
| **Date Decided** | 2026-01-12 (v0.0.4d) |
| **Impact Area** | Parser (`mistletoe` targeting CommonMark 0.30 + GFM) |
| **Provenance** | v0.0.4d §Differentiators and Decision Log |

## Decision

**GitHub Flavored Markdown (GFM) is the standardized Markdown flavor for ASoT. The canonical parser targets CommonMark 0.30 with GFM extensions. All ASoT validators and schema models assume GFM compatibility.**

## Context

The ASoT standards library needed to standardize which Markdown flavor to parse and validate against. Markdown itself has multiple widely-used variants: CommonMark (the base specification), GFM (GitHub's extensions), MultiMarkdown, Pandoc flavors, and others. Without standardization, validation would be inconsistent, and different tools would produce incompatible results.

Analysis of the llms.txt ecosystem showed that the vast majority of deployed projects use either CommonMark or GFM. GFM is particularly common in documentation projects hosted on GitHub (the primary platform for llms.txt projects). GFM adds several features absent from base CommonMark: tables (essential for API references and feature matrices), strikethrough, task lists, auto-linking of URLs, and slightly different handling of lists.

## Alternatives Considered

| Option | Rationale For | Rationale Against |
|--------|---------------|-------------------|
| CommonMark (Base Only) | Standardized specification, wide tooling support, focused scope | Lacks tables (critical for API documentation), no strikethrough, no task lists, limits expressiveness for structured content |
| MultiMarkdown | Powerful extensions, footnotes support, cross-references | Less widely adopted, fragmented tooling, adds complexity beyond GFM, not GitHub-native |
| Pandoc Markdown | Maximum flexibility, supports many output formats | Non-standard dialect, adds unnecessary complexity, heavy parser overhead, overkill for llms.txt use cases |
| **GFM (chosen)** | **GitHub-native, widely adopted in practice, includes tables (mandatory for API references), strikethrough and task lists support, most LLM training data includes GFM, CommonMark 0.30 compatible, excellent parser ecosystem, good balance of power and simplicity** | **Slightly less stable than pure CommonMark (subject to GitHub's changes), not all Markdown tools support all GFM features equally** |

## Rationale

GFM was selected as the standard because it represents the practical reality of modern documentation. Here's the breakdown:

**1. GitHub Native:** Most llms.txt projects are hosted on GitHub. Using GFM means the raw Markdown files render correctly on GitHub without any conversion or post-processing. This is a strong signal for adoption and usability.

**2. Tables Are Essential:** GFM tables enable clean API documentation, feature matrices, and comparison tables. Base CommonMark has no native table syntax, forcing authors to use code blocks or HTML (which is unreadable raw and breaks plain-text preservation). Many ASoT validation rules depend on tables (e.g., "API endpoints are documented in a table with Method, Path, Description columns").

**3. LLM Training Data:** Most large language models were trained on text that includes GFM, not vanilla CommonMark. LLMs recognize GFM syntax natively and parse it more reliably than obscure Markdown variants.

**4. Balance:** GFM extends CommonMark minimally and rationally. Unlike Pandoc or MultiMarkdown, GFM doesn't add features that rarely get used. The focus is on what authors actually need.

**5. Broad Ecosystem:** Parsers like `mistletoe`, `markdown-it`, and `markdown` all support CommonMark 0.30 + GFM. This ensures robust tool support and reduces vendor lock-in.

## Impact on ASoT

1. **Parser Specification:** The canonical ASoT parser is `mistletoe` (or equivalent) configured to parse CommonMark 0.30 with GFM extensions. This parser is the source of truth for what constitutes valid Markdown.

2. **Table Validation:** ASoT scoring includes rules that *require* certain content be in GFM table format:
   - API endpoint documentation must use GFM tables
   - Feature matrices and capability tables must use GFM format
   - Comparison tables (when present) must follow GFM syntax

3. **Schema Models:** The AST (abstract syntax tree) that schema models operate on includes GFM-specific nodes: `Table`, `TableRow`, `TableCell` (with alignment info), `Strikethrough`, `TaskListItem`.

4. **Validation Rules:** Validators check:
   - All tables are well-formed GFM syntax
   - Code block language tags are present and valid
   - Auto-linked URLs are properly recognized
   - Task lists (when used) follow GFM conventions

5. **Backward Compatibility:** If a project submits llms.txt in pure CommonMark (no GFM features), it remains valid ASoT — GFM is a superset of CommonMark, not a breaking change.

## Constraints Imposed

1. **Parser Requirements:** All Markdown parsing must use a CommonMark 0.30 + GFM compliant parser. Regex-based or ad-hoc parsing is not acceptable for ASoT compliance checking.

2. **Feature Compatibility:** ASoT validators may *require* GFM features (e.g., tables for APIs) but must not require vendor-specific extensions beyond GFM.

3. **Table Format Rigidity:** GFM table syntax is strict about alignment markers (`|`, `:`, `-`). Tools must validate exact syntax, not "loose" table-like structures.

4. **Code Block Language Tags:** All code blocks in ASoT-compliant documentation must include a language tag (e.g., ```python, ```json, ```bash). This is assumed for syntax highlighting and LLM understanding.

5. **No Vendor Extensions:** ASoT does not recognize GitHub-specific extensions beyond standard GFM (e.g., no GitHub's admonitions or custom blocks). All Markdown must be portable.

## Related Decisions

- **DS-DD-001:** Markdown over JSON/YAML — GFM is the Markdown flavor that replaces YAML/JSON
- **DS-DD-005:** Typed Directed Relationships — Concept relationships may be documented in GFM tables within Layer 2

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.3 |
