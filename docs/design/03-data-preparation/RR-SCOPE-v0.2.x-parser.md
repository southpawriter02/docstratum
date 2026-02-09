# v0.2.x Parser — Scope Breakdown

> **Version Range:** v0.2.0 through v0.2.2
> **Document Type:** Scope Breakdown (precedes individual design specifications)
> **Status:** DRAFT
> **Created:** 2026-02-09
> **Last Updated:** 2026-02-09
> **Parent:** RR-ROADMAP-validator-v0.0.1-to-v1.0.0.md
> **Research Basis:** v0.0.1a (ABNF grammar, reference parser, edge cases), v0.0.4a (structural checks)
> **Consumes:** v0.1.2a (`DiagnosticCode`, `constants.py`), v0.1.2b (`ParsedLlmsTxt`, `ParsedSection`, `ParsedLink`, `ParsedBlockquote`, `DocumentClassification`)
> **Consumed By:** v0.3.x (Validation Engine), v0.7.x (Ecosystem Integration via `SingleFileValidator` protocol)

---

## 1. Purpose

Phase 2 builds the **parser** — the component that reads a raw `llms.txt` Markdown file and transforms it into a populated `ParsedLlmsTxt` Pydantic model. The parser is the first piece of runtime logic in the system. Everything downstream (validation, scoring, remediation, ecosystem analysis) depends on this model being correctly and faithfully populated.

---

## 2. Scope Boundary: What the Parser IS and IS NOT

### 2.1 The Parser IS

A **structural extractor** that reads raw Markdown and populates the Pydantic models defined in v0.1.2b. Its contract:

**Input:** A file path or raw string containing Markdown content.
**Output:** A `ParsedLlmsTxt` instance with all extractable structure populated, plus file-level metadata (encoding, byte count, line count).

The parser follows the **"permissive input, strict output"** principle established in v0.0.1a: it accepts malformed, partial, or non-conformant files and extracts as much structure as possible. It never rejects a file outright — it always returns a `ParsedLlmsTxt`, even if that instance has `title = None`, `sections = []`, and other empty fields.

### 2.2 The Parser IS NOT

The parser is **not** a validator, scorer, classifier, or reporter. The following responsibilities belong to downstream phases and are explicitly **out of scope** for v0.2.x:

| Out of Scope | Why | Where It Lives |
|--------------|-----|----------------|
| **Emitting `DiagnosticCode` instances** | Diagnostic codes are the validator's output, not the parser's. The parser surfaces structural facts; the validator interprets those facts against rules. | v0.3.x (Validation Engine) |
| **Enforcing canonical section names** | The parser accepts any H2 text. Checking whether "quickstart" should be "Getting Started" is a validation rule (W002). | v0.3.3a |
| **Enforcing section ordering** | The parser preserves document order. Checking that Master Index comes before API Reference is a validation rule (W008). | v0.3.3e |
| **Validating URL reachability** | The parser performs syntactic URL validation only (`is_valid_url` boolean). DNS resolution and HTTP status checks are validation logic (E006). | v0.3.2b |
| **Enforcing link descriptions** | Descriptions are optional per the ABNF grammar (`[": " desc]`). Checking that they exist is a content quality rule (W003). | v0.3.2a |
| **Enforcing token budgets** | The parser computes `estimated_tokens` as a heuristic. Checking that the count falls within budget tiers is a validation rule (W010). | v0.3.3d |
| **Document type classification** | Type 1 Index vs. Type 2 Full classification uses the `TYPE_BOUNDARY_BYTES` threshold and structural heuristics. This is a post-parse enrichment step, not a parse step. | v0.2.1a (classification, which is post-parse enrichment) |
| **Anti-pattern detection** | The parser extracts structure. Determining that 15 bare links constitute a "Link Desert" is pattern recognition over the parsed output. | v0.3.4 |
| **Quality scoring** | The parser produces data. Computing a 0–100 composite score is an aggregation over validation results. | v0.4.x |
| **Content rewriting or normalization** | The parser does not strip whitespace, reformat links, normalize heading levels, or otherwise modify content. `raw_content` must be identical to the input. | Never |

### 2.3 The Gray Zone: Encoding and Line Endings

Encoding detection and line ending normalization happen **during** parsing but produce information that the **validator** uses to emit diagnostics (E003 for invalid encoding, E004 for invalid line endings). The parser's responsibility is:

- **Detect** the encoding and line ending style (produce metadata).
- **Attempt** to read the file using UTF-8, falling back gracefully if it fails.
- **Normalize** line endings internally to LF for consistent tokenization.
- **Preserve** the original raw bytes/content for round-trip fidelity.

The parser does **not** decide whether CRLF line endings constitute an error — that judgment belongs to the validator. The parser simply records what it found and proceeds.

### 2.4 The Gray Zone: Empty and Unparseable Files

When the parser encounters a file it cannot meaningfully extract structure from (empty file, binary file, non-UTF-8 file), it still returns a `ParsedLlmsTxt` instance:

- `title = None`
- `blockquote = None`
- `sections = []`
- `raw_content` = whatever bytes could be decoded (or empty string)
- Additional metadata fields (see v0.2.0a) indicate the failure mode

The validator inspects these fields and emits the appropriate diagnostics (E003, E007, etc.). The parser does not emit those codes itself.

---

## 3. Sub-Part Breakdown

### 3.1 v0.2.0 — Core Parser

**Goal:** Read a raw `llms.txt` file and populate a `ParsedLlmsTxt` model with all extractable structure.

This is the heart of the parser — the component that takes raw text and produces the structured model that every downstream phase depends on. It implements the 5-phase parsing strategy defined in v0.0.1a §Reference Parser Design.

---

#### v0.2.0a — File I/O & Encoding Detection

**What it does:** Reads a file from disk (or accepts raw string input), detects encoding characteristics, normalizes line endings for internal processing, and produces a file-level metadata bundle that downstream phases can inspect.

**Inputs:**
- File path (string) **or** raw content (string/bytes)

**Outputs:**
- Raw content as a Python string (decoded from bytes if file path provided)
- File metadata: byte count, detected encoding (UTF-8 / UTF-8-BOM / other), line ending style (LF / CRLF / CR / mixed), BOM presence (boolean), null byte detection (boolean)

**Behavior:**
- Reads the file as bytes first, then attempts UTF-8 decoding.
- If UTF-8 decoding fails, records the failure in metadata and attempts Latin-1 fallback (per v0.0.1a edge case D2). The resulting string will be available for downstream inspection, but the metadata will flag the encoding issue.
- Strips UTF-8 BOM (`\xEF\xBB\xBF`) if present, records BOM presence in metadata.
- Scans for null bytes (`\x00`). If found, records in metadata (likely binary file, per v0.0.1a edge case D3).
- Detects line ending style by scanning for `\r\n`, `\r`, and `\n` patterns. Records the dominant style.
- Normalizes all line endings to `\n` (LF) for internal tokenization. The original raw bytes are preserved separately for round-trip fidelity if needed.

**What it does NOT do:**
- Does not reject files based on encoding (that's the validator's E003).
- Does not reject files based on line endings (that's the validator's E004).
- Does not reject files based on null bytes (that's the validator's judgment call).
- Does not parse any Markdown structure — that's the next sub-part.

**Grounding:** v0.0.1a §Edge Cases Category D (D1–D5), v0.0.4a §4 (File Format Requirements: UTF-8 only, LF only, no BOM).

---

#### v0.2.0b — Markdown Tokenization

**What it does:** Takes the decoded, line-ending-normalized string from v0.2.0a and breaks it into a stream of structural tokens: headings (H1, H2, H3+), blockquote lines, link entries, fenced code block boundaries, and plain text lines.

**Inputs:**
- Decoded string content (from v0.2.0a)

**Outputs:**
- Ordered sequence of tokens, each tagged with: token type (H1, H2, H3+, BLOCKQUOTE, LINK_ENTRY, CODE_FENCE, BLANK, TEXT), line number (1-indexed), raw text content

**Behavior:**
- Uses line-by-line scanning, not full AST parsing. The `llms.txt` format is a constrained subset of Markdown — it does not require a full CommonMark parser. The ABNF grammar (v0.0.1a) defines the exact patterns to match:
  - `# ` at line start → H1 token
  - `## ` at line start → H2 token
  - `### ` (or more) at line start → H3+ token (treated as prose, not sections, per v0.0.1a edge case A7)
  - `> ` at line start → BLOCKQUOTE token
  - `- [` at line start → LINK_ENTRY token (potential link, syntax validated in v0.2.0c)
  - `` ``` `` at line start → CODE_FENCE token (toggles code block state)
  - Empty/whitespace-only → BLANK token
  - Everything else → TEXT token
- Within a fenced code block (between two CODE_FENCE tokens), all lines are tagged as TEXT regardless of their content. This prevents `# Title` inside a code example from being misidentified as an H1 heading.
- Line numbers are tracked as absolute 1-indexed positions in the original file.

**What it does NOT do:**
- Does not parse inline Markdown formatting (bold, italic, inline code). Those are preserved as raw text.
- Does not interpret link syntax beyond recognizing the `- [` prefix. Full link parsing happens in v0.2.0c.
- Does not use mistletoe or any external Markdown parser at this stage. The tokenizer is a purpose-built line scanner for the `llms.txt` grammar. (Note: The v0.1.1 spec lists mistletoe as a dependency. If the implementation finds that a full AST parser is necessary for correctness — particularly around nested code blocks or edge cases — the design spec for v0.2.0b should document that decision. The scope breakdown does not prescribe the implementation approach, only the input/output contract.)

**Grounding:** v0.0.1a §ABNF Grammar (lines 74–127), v0.0.1a §Reference Parser Design Phase 1–4.

---

#### v0.2.0c — Model Population

**What it does:** Walks the token stream from v0.2.0b and populates the `ParsedLlmsTxt`, `ParsedSection`, `ParsedLink`, and `ParsedBlockquote` Pydantic models defined in v0.1.2b.

**Inputs:**
- Token stream (from v0.2.0b)
- Source filename (string, for `ParsedLlmsTxt.source_filename`)

**Outputs:**
- Fully populated `ParsedLlmsTxt` instance

**Behavior (5-phase walk, per v0.0.1a §Reference Parser Design):**

**Phase 1 — H1 Title Extraction:**
- Scan for the first H1 token, skipping leading BLANK tokens.
- If found: extract title text (strip `# ` prefix), record line number. Populate `ParsedLlmsTxt.title` and `ParsedLlmsTxt.title_line`.
- If not found: set `title = None`, `title_line = None`. The parser does NOT emit E001 — it leaves the field empty for the validator to inspect.
- If multiple H1 tokens exist: use the first one. The parser does NOT emit E002 — it records the first and continues. (The validator will detect the second H1 in its own pass over the token stream or raw content.)

**Phase 2 — Blockquote Extraction:**
- After the H1 (or from the start if no H1), scan for consecutive BLOCKQUOTE tokens.
- If found: concatenate blockquote text (strip `> ` prefix), record line number of first blockquote line. Populate `ParsedBlockquote` with `text`, `line_number`, and `raw` (preserving `> ` prefix).
- If not found: set `ParsedLlmsTxt.blockquote = None`. The parser does NOT emit W001.
- Multi-line blockquotes: concatenate with newlines between stripped lines.

**Phase 3 — Body Content (optional):**
- Consume any TEXT, BLANK, or other non-H2 tokens between the blockquote and the first H2. This is "body content" — free-form prose that some files include between the description and the first section.
- This content is captured in `ParsedLlmsTxt.raw_content` but is not currently modeled as a separate field. (If a future version needs a `body` field, the design spec for v0.2.0c should evaluate whether to add one. The scope breakdown does not add new fields to existing models.)

**Phase 4 — Section & Link Extraction:**
- For each H2 token, create a new `ParsedSection`:
  - `name`: H2 text (strip `## ` prefix)
  - `line_number`: line position of the H2 token
  - `links`: populated by parsing LINK_ENTRY tokens within this section (see below)
  - `raw_content`: all raw text from this H2 to the next H2 (or EOF), including the H2 line itself
  - `canonical_name`: set to `None` (populated by v0.2.1c, not by the core parser)
  - `estimated_tokens`: computed in v0.2.0d
- For each LINK_ENTRY token within a section, parse the link syntax:
  - Extract `title` from `[title]`
  - Extract `url` from `(url)`
  - Extract `description` from `: description` (if present after the closing paren)
  - Set `is_valid_url` via syntactic check (valid URI structure per RFC 3986, not reachability)
  - Record `line_number`
  - Set ecosystem fields to defaults: `relationship = UNKNOWN`, `resolves_to = None`, `target_file_type = None`
- Malformed link entries (missing closing paren, no URL, etc.) per v0.0.1a edge cases B1–B8:
  - The parser attempts best-effort extraction. If the `[title](url)` pattern cannot be matched at all, the line is treated as TEXT within the section's `raw_content`.
  - Partial matches (e.g., title extracted but URL malformed) are included in the links list with `is_valid_url = False`.
- H3+ tokens within a section are treated as TEXT (part of `raw_content`), not as sub-sections.
- CODE_FENCE tokens toggle a "code block" state; content within is TEXT.

**Phase 5 — Final Assembly:**
- Populate `ParsedLlmsTxt.raw_content` with the complete original file content (pre-normalization string from v0.2.0a, preserving original line endings for round-trip fidelity).
- Set `ParsedLlmsTxt.parsed_at` to current UTC timestamp.
- Set `ParsedLlmsTxt.source_filename` to the provided filename.

**What it does NOT do:**
- Does not emit any `DiagnosticCode` values. The parsed model's empty/None fields ARE the signal to the validator.
- Does not add new fields to the Pydantic models. The models are defined in v0.1.2b and are not modified by the parser.
- Does not validate content quality, section naming, URL reachability, or any other rule.

**Grounding:** v0.0.1a §Reference Parser Design (5 phases), v0.0.1a §Data Structures, v0.0.1a §Edge Cases Category A (A1–A10) and Category B (B1–B8).

---

#### v0.2.0d — Token Estimation

**What it does:** Computes `estimated_tokens` for each `ParsedSection` and for the `ParsedLlmsTxt` document as a whole.

**Inputs:**
- Populated `ParsedLlmsTxt` instance (from v0.2.0c)

**Outputs:**
- Same `ParsedLlmsTxt` instance with `estimated_tokens` fields populated on each `ParsedSection` and on the root model.

**Behavior:**
- Per-section: populate the `estimated_tokens` **stored field** on each `ParsedSection` instance using `len(raw_content) // 4`. This field has `default=0` and must be explicitly set by the parser after `raw_content` is populated.
- Document-level: `ParsedLlmsTxt.estimated_tokens` is a **computed property** (not a stored field) that calculates `len(self.raw_content) // 4` dynamically. The parser does NOT need to set this — it computes automatically from `raw_content`.
- The `// 4` heuristic is the convention established in the existing model code. v0.0.4a §5.3 uses a slightly different heuristic (`len(text) / 3.3`). The design spec for v0.2.0d should document the rationale for using `// 4` over `/ 3.3` as a deliberate decision, or reconcile the two. The scope breakdown does not change the existing model's approach.

**What it does NOT do:**
- Does not call an actual tokenizer (tiktoken, sentencepiece, etc.). That would add dependencies outside the foundation scope.
- Does not enforce token budget thresholds. Estimation is informational; enforcement is the validator's job (W010).

**Grounding:** v0.1.2b (`ParsedSection.estimated_tokens` field definition), v0.0.4a §5.3 (token estimation heuristic), constants.py `TokenBudgetTier`.

---

### 3.2 v0.2.1 — Classification & Metadata

**Goal:** Enrich the parsed model with document type classification, size tier assignment, canonical section name matching, and metadata extraction. These are **post-parse enrichments** — they operate on the already-populated `ParsedLlmsTxt` model, not on raw Markdown.

This sub-version exists as a separate step because classification and metadata extraction depend on the parsed structure being available. They are logically distinct from the core parser and could be skipped (e.g., in a "fast parse" mode) without breaking the pipeline.

---

#### v0.2.1a — Document Type Classification

**What it does:** Inspects a `ParsedLlmsTxt` instance and its file metadata to assign a `DocumentType` and populate a `DocumentClassification` model.

**Inputs:**
- `ParsedLlmsTxt` instance (from v0.2.0)
- File metadata from v0.2.0a (byte count, encoding info)

**Outputs:**
- `DocumentClassification` instance with `document_type`, `size_bytes`, `estimated_tokens`, `size_tier`, `filename`, `classified_at`

**Behavior:**
- **Type determination** uses the `TYPE_BOUNDARY_BYTES` threshold (256,000 bytes) from `classification.py`:
  - Files ≤ 256 KB with a single H1 → `TYPE_1_INDEX`
  - Files > 256 KB or with multiple H1 headings → `TYPE_2_FULL`
  - Files matching ecosystem naming conventions (e.g., content pages linked from an index) → `TYPE_3_CONTENT_PAGE` (v0.0.7)
  - Files matching instruction patterns → `TYPE_4_INSTRUCTIONS` (v0.0.7)
  - Files that cannot be classified → `UNKNOWN`
- **Size tier assignment** uses `TokenBudgetTier` thresholds from `constants.py`:
  - < 1,500 tokens → MINIMAL
  - 1,500–4,500 → STANDARD
  - 4,500–12,000 → COMPREHENSIVE
  - 12,000–50,000 → FULL
  - > 50,000 → OVERSIZED

**What it does NOT do:**
- Does not emit diagnostics. Classification is data enrichment, not validation.
- Does not decide what to DO about the classification (e.g., "Type 2 files should use different rules"). That's the validator's profile logic.

**Grounding:** v0.1.2b (`DocumentType`, `SizeTier`, `DocumentClassification`, `TYPE_BOUNDARY_BYTES`), v0.0.1a edge case A10 (Type 2 Full heuristic).

---

#### v0.2.1b — Size Tier Assignment

**What it does:** Assigns a `SizeTier` value based on the document's estimated token count.

**Note:** This is a focused sub-operation within classification. It is broken out as a separate sub-part because the tier thresholds may need calibration (the gap between the `// 4` parser heuristic and the `/ 3.3` v0.0.4a heuristic could shift tier boundaries). The design spec for v0.2.1b should document the calibration decision and threshold behavior at the boundaries.

**Inputs:**
- `estimated_tokens` from `ParsedLlmsTxt`

**Outputs:**
- `SizeTier` enum value

**Behavior:**
- Straightforward threshold comparison against the 5 `SizeTier` boundaries.
- Edge behavior at exact boundaries (e.g., exactly 4,500 tokens) should follow a documented convention (inclusive lower bound, exclusive upper bound, or similar).

**Grounding:** `constants.py` (`TokenBudgetTier`), `classification.py` (`SizeTier`).

---

#### v0.2.1c — Canonical Section Matching

**What it does:** For each `ParsedSection` in the parsed document, attempts to match the section's `name` against the 11 canonical section names and their 32 aliases defined in `constants.py`. Populates the `ParsedSection.canonical_name` field.

**Inputs:**
- `ParsedLlmsTxt` instance with populated sections

**Outputs:**
- Same instance with `ParsedSection.canonical_name` populated (or left `None` if no match)

**Behavior:**
- Case-insensitive matching against `CanonicalSectionName` enum values and `SECTION_NAME_ALIASES` dictionary.
- Alias resolution: if the section name matches an alias (e.g., "toc" → "Master Index", "quickstart" → "Getting Started"), the canonical name is set to the alias target.
- Exact match takes precedence over alias match.
- If no match is found, `canonical_name` remains `None`. The parser does NOT flag this — that's the validator's W002.
- Whitespace normalization: leading/trailing whitespace stripped before matching. Internal whitespace preserved for comparison.

**What it does NOT do:**
- Does not rewrite the section `name` field. The original name is preserved; `canonical_name` is an additional enrichment field.
- Does not enforce canonical naming. A section named "My Stuff" gets `canonical_name = None` and the parser moves on.
- Does not check for duplicate canonical names (e.g., two sections both mapping to "Getting Started"). That's a validator concern.

**Grounding:** `constants.py` (`CanonicalSectionName`, `SECTION_NAME_ALIASES`), DECISION-012 (11 canonical names from 450+ project analysis).

---

#### v0.2.1d — Metadata Extraction

**What it does:** Checks for YAML frontmatter at the top of the file and extracts it as a raw dictionary.

> **Implementation Prerequisite:** The `Metadata` Pydantic model is specified in v0.1.2d but has not yet been implemented in code (`enrichment.py` does not exist). Before this sub-part can be implemented, the `Metadata` model must be created — either as part of this sub-part's implementation (with a documented v0.1.2 amendment) or as a prerequisite task. The design spec for v0.2.1d must address this gap.

**Inputs:**
- Raw file content (from `ParsedLlmsTxt.raw_content`)

**Outputs:**
- A raw dictionary of frontmatter key-value pairs (or `None` if no frontmatter found)
- Once `enrichment.py` is implemented: a `Metadata` instance populated from the dictionary

**Behavior:**
- Checks if the file begins with `---` followed by YAML content followed by `---`. This is the standard YAML frontmatter convention.
- If present, parses the YAML content using PyYAML into a raw dictionary.
- Once the `Metadata` model exists, maps recognized fields to model properties: `schema_version`, `site_name`, `site_url`, `last_updated`, `generator`, `docstratum_version`, `token_budget_tier`.
- Unrecognized YAML keys are silently ignored (permissive input).
- Malformed YAML (parse errors) results in `None` — the parser does not raise exceptions for bad frontmatter.
- If no frontmatter is present, returns `None`.

**What it does NOT do:**
- Does not require frontmatter. Most existing `llms.txt` files do not have it (0% adoption per v0.0.2c).
- Does not validate metadata content (e.g., checking that `schema_version` is a valid semver string). That's validation logic.
- Does not inject metadata into the parsed model's `raw_content`. The frontmatter lines are already part of the raw content.

**Grounding:** v0.1.2d (`Metadata` model specification — not yet implemented), v0.0.1b §Gap Analysis (Gap #5: Required Metadata).

---

### 3.3 v0.2.2 — Parser Testing & Calibration

**Goal:** Validate the parser against synthetic fixtures and real-world specimens. Integrate the parser into the ecosystem pipeline via the `SingleFileValidator` protocol.

---

#### v0.2.2a — Synthetic Test Fixtures

**What it does:** Creates 5 synthetic `llms.txt` files, each designed to exercise the parser at a specific conformance level (L0 fail, L1, L2, L3, L4).

**Outputs:**
- 5 `.txt` test fixture files in the `tests/fixtures/` directory
- Each fixture has a companion assertion file or inline test expectations documenting what the parser should extract from it

**Fixture Design:**
- **L0 Fail fixture:** A file that cannot be meaningfully parsed — binary content, non-UTF-8 encoding, or empty. Parser should return a mostly-empty `ParsedLlmsTxt`.
- **L1 fixture:** Structurally minimal: one H1, one H2 with one link. No blockquote, no descriptions. Parser should extract title, one section, one link.
- **L2 fixture:** Content-quality file: H1, blockquote, multiple sections with described links. Parser should extract all structure faithfully.
- **L3 fixture:** Best-practices file: canonical section names, Master Index, code examples, version metadata. Parser should extract everything and canonical name matching (v0.2.1c) should populate `canonical_name` fields.
- **L4 fixture:** DocStratum-extended file: YAML frontmatter, concept definitions, few-shot examples, LLM instructions. Parser should extract frontmatter metadata; enrichment content exists in `raw_content` for downstream interpretation.

**What it does NOT do:**
- These fixtures do not test validation logic. The L0/L1/L2/L3/L4 labels describe the expected *validator* assessment, but the parser tests only verify that structure is correctly extracted — not that diagnostic codes are correctly emitted.

**Grounding:** v0.1.0 §Exit Criteria ("5 synthetic test fixtures validate at expected conformance levels"), RR-META-testing-standards.

---

#### v0.2.2b — Real-World Specimen Parsing

**What it does:** Parses the 6 gold standard calibration specimens (Svelte, Pydantic, Vercel AI SDK, Shadcn UI, Cursor, NVIDIA) and verifies that the parsed output matches expected structure.

**Outputs:**
- 6 regression tests, each asserting specific structural properties of the parsed output:
  - Title text matches expected project name
  - Section count matches expected
  - Link count per section matches expected
  - Blockquote presence/absence matches expected
  - No parser crashes or unhandled exceptions

**What it does NOT do:**
- Does not verify quality scores (that's v0.4.2a).
- Does not verify diagnostic code emission (that's v0.3.5d).
- Does not require network access to fetch the specimens. Specimens should be checked into the test fixtures directory or fetched once and cached.

**Grounding:** DS-CS-001 through DS-CS-006 (6 calibration specimens), v0.0.2b (individual site audits with structural analysis).

---

#### v0.2.2c — Edge Case Coverage

**What it does:** Implements test cases for all edge cases documented in v0.0.1a §Edge Cases.

**Outputs:**
- Test cases covering v0.0.1a edge case categories:
  - **Category A (Structural, 10 cases):** Empty file, blank-only file, no H1, multiple H1, H2 before H1, no H2 sections, H3+ headers, empty H2 section, fenced code blocks, Type 2 Full documents.
  - **Category B (Link Format, 8 cases):** Missing closing paren, empty URL, relative URL, malformed URL, duplicate URLs, empty title, non-list links, bare URLs.
  - **Category C (Content, 10 cases):** Multiline blockquotes, unicode content, long lines, mixed indentation, trailing whitespace, nested lists, entries without descriptions, etc.
  - **Category D (Encoding, 5 cases):** UTF-8 BOM, non-UTF-8, null bytes, Windows CRLF, Mac CR-only.

**What it does NOT do:**
- Does not test validation behavior. Tests verify that the parser produces the correct model output for each edge case — not that the right diagnostic codes are emitted.

**Grounding:** v0.0.1a §Edge Cases (A1–A10, B1–B8, C1–C10, D1–D5).

---

#### v0.2.2d — SingleFileValidator Integration

**What it does:** Implements the `SingleFileValidator` protocol (defined in v0.1.4a) so the parser can be plugged into the ecosystem pipeline's Stage 2 (`PerFileStage`).

**Inputs:**
- File path and raw content (as provided by the ecosystem pipeline)

**Outputs:**
- `ParsedLlmsTxt` instance stored on the `EcosystemFile` in `PipelineContext`

**Behavior:**
- The `SingleFileValidator` protocol defines a `validate(file_path, content) → result` contract.
- At this stage (v0.2.2d), the implementation only performs **parsing** (v0.2.0) and **classification** (v0.2.1). It does NOT yet perform validation (v0.3.x) or scoring (v0.4.x).
- The ecosystem pipeline's Stage 2 calls this for each discovered file. The parsed output is stored on the `EcosystemFile` object for downstream stages to consume.
- This creates a functional (but incomplete) end-to-end pipeline: Discovery → Parse → Relationships → Ecosystem Validation → Ecosystem Scoring. Stages 3–5 already exist (v0.1.4c–f) and can operate on the parsed output.

**What it does NOT do:**
- Does not produce a `ValidationResult` or `QualityScore`. Those come in v0.3.x and v0.4.x respectively. The `SingleFileValidator` protocol may need to return a partial result or the protocol's return type may need to accommodate a "parse only" mode. The design spec for v0.2.2d should document how partial results are handled.

**Grounding:** v0.1.4a (`SingleFileValidator` protocol, `PipelineContext`), v0.1.4b (`PerFileStage` calling convention), FR-080 (per-file validation within ecosystem).

---

## 4. Dependency Map

```
v0.2.0a (File I/O)
    │
    ▼
v0.2.0b (Tokenization)
    │
    ▼
v0.2.0c (Model Population)
    │
    ├──► v0.2.0d (Token Estimation) [modifies ParsedSection.estimated_tokens in-place]
    │
    ▼
v0.2.1 (Post-Parse Enrichments) ◄── all operate on the populated ParsedLlmsTxt
    │
    ├── v0.2.1a (Classification) [independent]
    ├── v0.2.1b (Size Tier) [independent, uses estimated_tokens from v0.2.0d]
    ├── v0.2.1c (Canonical Matching) [independent]
    └── v0.2.1d (Metadata Extraction) [independent, REQUIRES enrichment.py to exist]
         │
         ▼
v0.2.2 (Testing & Calibration)
    │
    ├── v0.2.2a (Fixtures) [independent]
    ├── v0.2.2b (Specimens) [independent]
    ├── v0.2.2c (Edge Cases) [independent]
    └── v0.2.2d (SingleFileValidator) [depends on all of 2a-2c passing]
```

**Parallelization opportunities:**
- v0.2.1a, v0.2.1b, v0.2.1c, and v0.2.1d are independent post-parse enrichments. They can be implemented and tested in any order. Note: v0.2.1b uses `estimated_tokens` which v0.2.0d populates, so v0.2.0d should complete before v0.2.1b. v0.2.1d requires `enrichment.py` to be created (see prerequisite note).
- v0.2.2a–c are independent test suites. They can be written in any order, but all must pass before v0.2.2d (integration).

---

## 5. Models Consumed (Not Modified)

The parser consumes the following models from v0.1.2. It populates instances of these models but does **not** add, remove, or modify any fields.

| Model | Source Module | Parser's Role | Notes |
|-------|-------------|---------------|-------|
| `ParsedLlmsTxt` | `schema/parsed.py` | Populates all fields | `estimated_tokens` is a computed property — no explicit set needed |
| `ParsedSection` | `schema/parsed.py` | Populates all fields except `canonical_name` (v0.2.1c enrichment) | `estimated_tokens` is a stored field (default=0) — must be explicitly set |
| `ParsedLink` | `schema/parsed.py` | Populates core fields; ecosystem fields default to safe values | |
| `ParsedBlockquote` | `schema/parsed.py` | Populates all fields | |
| `DocumentClassification` | `schema/classification.py` | Populates via v0.2.1a | |
| `DocumentType` | `schema/classification.py` | Used by v0.2.1a | |
| `SizeTier` | `schema/classification.py` | Used by v0.2.1b | |
| `CanonicalSectionName` | `schema/constants.py` | Used by v0.2.1c | |
| `Metadata` | `schema/enrichment.py` | Populates via v0.2.1d | **NOT YET IMPLEMENTED** — specified in v0.1.2d but `enrichment.py` does not exist. Must be created before v0.2.1d. |
| `LinkRelationship` | `schema/parsed.py` | Default value (UNKNOWN) only | |

**If any sub-part discovers that a model field is missing or insufficient**, the finding must be documented in that sub-part's design spec and escalated as a potential v0.1.2 amendment — not silently added during parser implementation.

---

## 6. Exit Criteria

v0.2.x is complete when:

- [ ] A file path or raw string can be passed to the parser and a `ParsedLlmsTxt` instance is returned.
- [ ] The 5 synthetic test fixtures parse correctly with all expected fields populated.
- [ ] The 6 calibration specimens parse without crashes and produce structurally correct output.
- [ ] All 33 edge cases from v0.0.1a (A1–A10, B1–B8, C1–C10, D1–D5) are covered by tests.
- [ ] `DocumentClassification` is correctly assigned for Type 1 and Type 2 documents.
- [ ] `canonical_name` is correctly matched for all 11 canonical names and all 32 aliases.
- [ ] YAML frontmatter is correctly extracted when present.
- [ ] The `SingleFileValidator` protocol is implemented and the ecosystem pipeline's Stage 2 calls the parser successfully.
- [ ] `pytest --cov=docstratum.parser --cov-fail-under=85` passes.
- [ ] `black --check` and `ruff check` pass on all new code.
- [ ] No new fields have been added to any v0.1.2 Pydantic model without a documented amendment.

---

## 7. What Comes Next

The parser's output (`ParsedLlmsTxt`) is the input to:

- **v0.3.x (Validation Engine):** Inspects the parsed model and emits `DiagnosticCode` instances for every rule violation found. This is where E001 (NO_H1_TITLE), W001 (MISSING_BLOCKQUOTE), W003 (LINK_MISSING_DESCRIPTION), and all other diagnostic codes get emitted.
- **v0.7.x (Ecosystem Integration):** Wires the parser + validator into the ecosystem pipeline's `SingleFileValidator` protocol for multi-file analysis.
