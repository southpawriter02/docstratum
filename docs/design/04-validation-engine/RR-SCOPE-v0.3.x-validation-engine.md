# v0.3.x Validation Engine — Scope Breakdown

> **Version Range:** v0.3.0 through v0.3.5
> **Document Type:** Scope Breakdown (precedes individual design specifications)
> **Status:** DRAFT
> **Created:** 2026-02-09
> **Last Updated:** 2026-02-09
> **Parent:** RR-ROADMAP-validator-v0.0.1-to-v1.0.0.md
> **Research Basis:** v0.0.4a (structural checks), v0.0.4b (content checks), v0.0.4c (anti-pattern catalog)
> **Consumes:** v0.2.x (`ParsedLlmsTxt`, `DocumentClassification`, `Metadata`), v0.1.2a (`DiagnosticCode`, `Severity`, `constants.py`), v0.1.2c (`ValidationLevel`, `ValidationResult`, `ValidationDiagnostic`)
> **Consumed By:** v0.4.x (Quality Scoring), v0.6.x (Remediation Framework), v0.7.x (Ecosystem Integration)

---

## 1. Purpose

Phase 3 builds the **validation engine** — the component that inspects a parsed `ParsedLlmsTxt` model and produces a `ValidationResult` containing every diagnostic finding. This is where the 38 diagnostic codes get emitted, the 5 validation levels get evaluated, and the file's conformance profile is determined.

The validation engine is the core "intelligence" of the system. The parser (v0.2.x) extracts structure; the validator interprets that structure against rules. The scorer (v0.4.x) aggregates the validator's findings into a numeric grade. The validator sits between them and is the single component responsible for answering the question: *"What's wrong with this file?"*

---

## 2. Scope Boundary: What the Validator IS and IS NOT

### 2.1 The Validator IS

A **rule evaluator** that inspects the parsed model and file metadata, applies a set of checks organized by validation level (L0 → L1 → L2 → L3), and produces a `ValidationResult` containing all findings as `ValidationDiagnostic` instances.

**Input:** A `ParsedLlmsTxt` instance (from v0.2.x), its `DocumentClassification`, and file-level metadata (encoding, line endings, byte count).
**Output:** A `ValidationResult` with `level_achieved`, `diagnostics[]`, and `levels_passed{}`.

### 2.2 The Validator IS NOT

| Out of Scope | Why | Where It Lives |
|--------------|-----|----------------|
| **Computing quality scores** | Scoring aggregates diagnostics into points and grades. The validator emits findings; the scorer interprets them. | v0.4.x (Quality Scoring) |
| **Generating remediation guidance** | The validator says *what's wrong*. The remediation framework says *what to do about it*. | v0.6.x (Remediation Framework) |
| **Formatting output** | The validator produces a `ValidationResult` model. Report generation formats that model into JSON, Markdown, HTML, etc. | v0.8.x (Report Generation) |
| **Evaluating L4 (DocStratum Extended) checks** | L4 checks (I001, I002, I003, I006, I007) verify enrichment features (concept definitions, few-shot examples, LLM instructions). These are deferred because they require enrichment-aware logic not yet built. | v0.9.0 (Extended Validation) |
| **Evaluating ecosystem-level diagnostics** | E009, E010, W012–W018, I008–I010 are ecosystem codes emitted by the ecosystem pipeline (v0.1.4d), not the single-file validator. | v0.1.4d (existing), v0.7.x (ecosystem integration) |
| **Resolving URLs via HTTP** | Syntactic URL validation is in-scope (can the URL be parsed?). Reachability validation (does the URL respond with 200?) is optionally triggered but separated as a configurable check because it requires network access and introduces latency. | v0.3.2b (optional, behind a flag) |
| **Applying validation profiles** | The validator evaluates ALL applicable checks. The profile system (v0.5.x) filters which checks are active and which results are surfaced. The validator is profile-unaware. | v0.5.x (CLI & Profiles) |
| **Modifying the ParsedLlmsTxt model** | The validator reads the parsed model. It never mutates it. | Never |

### 2.3 Diagnostic Codes In Scope vs. Out of Scope

The validation engine (v0.3.x) is responsible for emitting **26 of the 38 diagnostic codes**. The remaining 12 are out of scope:

**In Scope (26 codes — single-file, L0–L3):**

| Level | Codes | Count |
|-------|-------|-------|
| L0 | E001, E002, E003, E004, E005, E006, E007, E008 | 8 |
| L1 | W001, W002 | 2 |
| L2 | W003, I004, I005 | 3 |
| L3 | W004, W005, W006, W007, W008, W009, W010, W011 | 8 |
| Anti-Pattern Detection | (uses same codes above, plus pattern-level metadata) | 0 new |
| **Total** | | **21 unique codes** |

> **Note on code count:** Some diagnostic codes appear at multiple levels (e.g., E006 is checked for format compliance at L0 and for URL resolution at L2). The 21 unique codes map to approximately 30 individual check implementations when accounting for these multi-level applications.

**Out of Scope (17 codes):**

| Category | Codes | Reason | Deferred To |
|----------|-------|--------|-------------|
| L4 Extended | I001, I002, I003, I006, I007 | Require enrichment-aware logic | v0.9.0 |
| Ecosystem | E009, E010, W012, W013, W014, W015, W016, W017, W018, I008, I009, I010 | Emitted by ecosystem pipeline, not single-file validator | v0.1.4d (existing) / v0.7.x |

### 2.4 The Gray Zone: Anti-Pattern Detection vs. Anti-Pattern Scoring

The validator **detects** anti-patterns and attaches metadata to diagnostics (e.g., "this W003 instance is part of the Link Desert anti-pattern AP-CONT-004"). The **scorer** (v0.4.x) uses that metadata to calculate the Anti-Pattern dimension score (DS-VC-APD-001 through APD-008).

Specifically:
- v0.3.4 detects the 16 single-file anti-patterns (4 critical + 5 structural + 5 content + 4 strategic — note: some of the 9 content anti-patterns and all 6 ecosystem anti-patterns are out of scope per Section 2.3).
- v0.3.4 does NOT compute the APD dimension score — it emits the diagnostics and attaches `anti_pattern_id` metadata.
- v0.4.x reads those diagnostics and computes the 20-point APD dimension.

### 2.5 The Gray Zone: URL Reachability

URL validation has two layers:

1. **Syntactic validation** (always in scope): Can the URL string be parsed as a valid URI per RFC 3986? This is fast, deterministic, and requires no network access. The `ParsedLink.is_valid_url` field from the parser provides this.

2. **Reachability validation** (conditionally in scope): Does the URL respond with an HTTP 2xx status? This requires network access, introduces latency (potentially seconds per URL), and may produce false negatives (rate limiting, auth-gated pages). This check is gated behind a configuration flag (`check_urls: bool`).

The design spec for v0.3.2b must define:
- The default state of `check_urls` (recommended: `false` for speed, `true` opt-in)
- Timeout behavior (recommended: 5s per URL, configurable)
- How HTTP errors are classified (404 = E006, 5xx = skip, timeout = skip)
- Whether results are cached within a single validation run

---

## 3. Sub-Part Breakdown

### 3.1 v0.3.0 — L0 Validation (Parseable Gate)

**Goal:** Determine whether the file can be read and parsed at all. L0 is a binary gate — if ANY L0 check fails, the pipeline stops. No further validation is meaningful on a file that cannot be parsed.

**Gate Behavior:** L0 failure caps the quality score at 29 (CRITICAL grade) per DS-QS-GATE. The validator records `level_achieved = L0_PARSEABLE` only if all L0 checks pass. If any fail, `level_achieved` reflects the failure state and `levels_passed[L0] = False`.

---

#### v0.3.0a — Encoding Validation

**What it checks:** Whether the file is valid UTF-8, using the encoding metadata produced by the parser's file I/O stage (v0.2.0a).

**Inputs:**
- File metadata from v0.2.0a: detected encoding, BOM presence, null byte detection

**Diagnostic Codes Emitted:**
- **E003 (INVALID_ENCODING):** File is not valid UTF-8. Emitted when the parser's encoding detection recorded a non-UTF-8 encoding or a decode failure.

**Check Logic:**
- If `encoding != "utf-8"` → emit E003 with metadata context (what encoding was detected, byte position of first invalid sequence)
- BOM presence alone is NOT an E003 — it is recorded as metadata and may be flagged as an informational observation in a future version, but the current diagnostic catalog does not assign a code to BOM-only issues.

**What it does NOT check:**
- Content quality, structure, or anything requiring parsed Markdown. This is purely an encoding gate.

**Grounding:** v0.0.4a §4 (ENC-001: UTF-8 encoding), DiagnosticCode.E003_INVALID_ENCODING.

---

#### v0.3.0b — Line Ending Validation

**What it checks:** Whether line endings are consistently LF (Unix-style).

**Inputs:**
- File metadata from v0.2.0a: detected line ending style (LF / CRLF / CR / mixed)

**Diagnostic Codes Emitted:**
- **E004 (INVALID_LINE_ENDINGS):** Non-LF line endings detected. Emitted when CRLF, CR, or mixed line endings are found.

**Check Logic:**
- If `line_ending_style != "LF"` → emit E004 with context (which style was detected, how many non-LF line endings found)

**Grounding:** v0.0.4a §4 (ENC-002: LF line endings only), DiagnosticCode.E004_INVALID_LINE_ENDINGS.

---

#### v0.3.0c — Markdown Parse Validation

**What it checks:** Whether the file parsed as valid Markdown — specifically, whether the parser (v0.2.x) was able to extract any meaningful structure at all.

**Inputs:**
- `ParsedLlmsTxt` instance from v0.2.x

**Diagnostic Codes Emitted:**
- **E005 (INVALID_MARKDOWN):** Markdown syntax prevents meaningful parsing. Emitted when the parser produced a result with no extractable H1 or H2 structure AND the file is not empty (empty files get E007 instead).

**Check Logic:**
- If `title is None` AND `len(sections) == 0` AND `len(raw_content) > 0` → emit E005. The file has content but it could not be parsed into any recognized `llms.txt` structure.
- This is a catch-all for files that are valid text but not valid `llms.txt` Markdown (e.g., a JSON file, a CSV file, a prose document with no headings).

**What this does NOT check:**
- A file with an H1 but malformed sections still passes E005 — it parsed partially. The structural checks (v0.3.1) catch the specifics.
- E001 (no H1) and E002 (multiple H1) are separate checks at L0, not rolled into E005.

**Grounding:** v0.0.4a §4 (MD-001: valid Markdown syntax), DiagnosticCode.E005_INVALID_MARKDOWN.

---

#### v0.3.0d — Empty File Detection

**What it checks:** Whether the file is empty or whitespace-only.

**Inputs:**
- `ParsedLlmsTxt.raw_content`

**Diagnostic Codes Emitted:**
- **E007 (EMPTY_FILE):** File is empty or contains only whitespace. Emitted when `len(raw_content.strip()) == 0`.

**Check Logic:**
- If `raw_content` is empty or whitespace-only → emit E007.
- E007 takes precedence over E005 — an empty file is a more specific diagnosis than "invalid Markdown."

**Grounding:** v0.0.4c §CHECK-001 (Ghost File anti-pattern), DiagnosticCode.E007_EMPTY_FILE.

---

#### v0.3.0e — Size Limit Enforcement

**What it checks:** Whether the file exceeds the hard token limit (100K tokens, the ANTI_PATTERN threshold).

**Inputs:**
- `ParsedLlmsTxt.estimated_tokens` (computed property from `raw_content`)

**Diagnostic Codes Emitted:**
- **E008 (EXCEEDS_SIZE_LIMIT):** File exceeds 100,000 tokens. This is the Monolith Monster anti-pattern threshold (AP-STRAT-002 / CHECK-003).

**Check Logic:**
- If `estimated_tokens > 100_000` → emit E008 with context (actual token count, tier recommendation).
- The 100K threshold comes from `constants.py` `TOKEN_ZONES["DEGRADATION"]`. Files above this are too large for any current LLM context window and cannot be consumed as a single unit.

**What this does NOT check:**
- Token budget tier compliance (e.g., "this Standard-tier file should be under 4,500 tokens"). That's W010 at L3.
- This is only the hard upper limit — the anti-pattern threshold.

**Grounding:** v0.0.4a §SIZ-003, v0.0.4c §CHECK-003 (Monolith Monster), constants.py `TOKEN_ZONES`, DiagnosticCode.E008_EXCEEDS_SIZE_LIMIT.

---

#### v0.3.0f — H1 Title Validation

**What it checks:** Whether exactly one H1 title exists at the start of the document.

**Inputs:**
- `ParsedLlmsTxt.title`, `ParsedLlmsTxt.title_line`
- Raw content (for detecting multiple H1 headings)

**Diagnostic Codes Emitted:**
- **E001 (NO_H1_TITLE):** No H1 heading found. Emitted when `title is None`.
- **E002 (MULTIPLE_H1):** More than one H1 heading found. Emitted when scanning the raw content or token stream reveals additional `# ` lines beyond the first H1.

**Check Logic:**
- If `title is None` → emit E001 with line_number=1 (expected location).
- If title exists but additional H1 headings are found → emit E002 with line_number of the second H1 and context showing the duplicate.
- E001 and E002 are mutually exclusive per file (you can't have "no H1" and "multiple H1" simultaneously).

**Why H1 is at L0, not L1:** Every downstream check assumes the document has an identity (the H1 title). Without it, section extraction, canonical name matching, and ecosystem identification all become ambiguous. The v0.0.1a reference parser design treats H1 absence as a parsing failure, and the ABNF grammar defines `title` as a required production. This is a structural prerequisite, not merely a best practice.

**Grounding:** v0.0.4a §STR-001, v0.0.1a §ABNF Grammar (`title = "#" SP title-text CRLF`), DiagnosticCode.E001_NO_H1_TITLE, DiagnosticCode.E002_MULTIPLE_H1.

---

#### v0.3.0g — Link Format Validation (Syntactic)

**What it checks:** Whether links use valid `[text](url)` syntax with parseable URLs.

**Inputs:**
- All `ParsedLink` instances across all `ParsedSection` objects
- `ParsedLink.is_valid_url` flag (set by parser)

**Diagnostic Codes Emitted:**
- **E006 (BROKEN_LINKS):** Link has empty or syntactically malformed URL. Emitted for each link where `is_valid_url == False` or where the URL is empty/missing.

**Check Logic:**
- For each `ParsedLink` in all sections: if `is_valid_url == False` or `url` is empty → emit E006 with line_number and context (the raw link text).
- This is **syntactic** link validation only. URL reachability (HTTP resolution) is a separate check at L2 (v0.3.2b).
- A file with >80% broken links triggers the "Link Void" critical anti-pattern (CHECK-004), detected in v0.3.4a.

**Grounding:** v0.0.4a §LNK-001, §LNK-002, DiagnosticCode.E006_BROKEN_LINKS.

---

### 3.2 v0.3.1 — L1 Validation (Structural)

**Goal:** Verify that the file follows the structural conventions of the `llms.txt` specification — blockquote, section structure, and naming. L1 checks assume the file passed L0 (is parseable with a valid H1).

**Gate Behavior:** L1 checks are skipped if L0 failed. `levels_passed[L1]` is set to `True` only if all L1 checks pass (no ERROR-severity diagnostics at this level). WARNING-severity findings (W001, W002) do NOT prevent L1 from passing — they are quality observations, not structural failures.

---

#### v0.3.1a — Blockquote Presence

**What it checks:** Whether a description blockquote exists after the H1 title.

**Inputs:**
- `ParsedLlmsTxt.blockquote` (None if missing)

**Diagnostic Codes Emitted:**
- **W001 (MISSING_BLOCKQUOTE):** No blockquote description found after H1. WARNING severity — blockquotes have only 55% real-world compliance (v0.0.2c), so absence is flagged but does not block validation.

**Check Logic:**
- If `blockquote is None` → emit W001.

**Grounding:** v0.0.4a §STR-002, v0.0.4b §CNT-002, DiagnosticCode.W001_MISSING_BLOCKQUOTE.

---

#### v0.3.1b — Section Name Validation

**What it checks:** Whether section names match the 11 canonical names or their 32 aliases.

**Inputs:**
- All `ParsedSection.canonical_name` values (populated by v0.2.1c)

**Diagnostic Codes Emitted:**
- **W002 (NON_CANONICAL_SECTION_NAME):** Section name does not match any canonical name or alias. Emitted once per non-matching section.

**Check Logic:**
- For each section: if `canonical_name is None` → emit W002 with line_number and context (the actual section name, plus a suggestion of the closest canonical name if a fuzzy match is feasible).
- Fuzzy matching is a NICE-TO-HAVE, not a requirement. The design spec for v0.3.1b should decide whether to include it. At minimum, the diagnostic `context` field should show the section name and list the 11 canonical options.

**Grounding:** v0.0.4a §NAM-001, DECISION-012, DiagnosticCode.W002_NON_CANONICAL_SECTION_NAME.

---

### 3.3 v0.3.2 — L2 Validation (Content Quality)

**Goal:** Verify that the documentation content is meaningful and useful — not just structurally present but substantively valuable. L2 checks assume L1 passed (structure is sound).

**Gate Behavior:** L2 checks are skipped if L1 failed (any L0/L1 ERROR). WARNING-severity findings do not prevent L2 from passing.

---

#### v0.3.2a — Link Description Quality

**What it checks:** Whether links have descriptions, and whether those descriptions are substantive (not placeholders).

**Inputs:**
- All `ParsedLink.description` values across all sections

**Diagnostic Codes Emitted:**
- **W003 (LINK_MISSING_DESCRIPTION):** Link has no description or description is empty/trivial. Emitted once per offending link.

**Check Logic:**
- For each link: if `description is None` or `description.strip() == ""` → emit W003.
- Placeholder detection: if description matches known placeholder patterns ("TBD", "TODO", "Lorem ipsum", "Description here", etc.) → emit W003 with context noting the placeholder.
- The list of placeholder patterns should be defined as a constant (not hardcoded in the check logic) so it can be extended without modifying the check.

**Scoring Impact:** DS-VC-CON-001 (5 points). Research shows link descriptions correlate with quality at r ≈ 0.45.

**Grounding:** v0.0.4b §CNT-004, DS-VC-CON-001, DiagnosticCode.W003_LINK_MISSING_DESCRIPTION.

---

#### v0.3.2b — URL Reachability (Optional)

**What it checks:** Whether linked URLs actually resolve to accessible pages.

**Inputs:**
- All `ParsedLink.url` values where `is_valid_url == True` (syntactically valid URLs from L0)
- Configuration flag: `check_urls: bool` (default: `false`)

**Diagnostic Codes Emitted:**
- **E006 (BROKEN_LINKS):** URL returns HTTP 4xx or cannot be resolved. Same code as syntactic link failures (v0.3.0g), but with different context: the diagnostic message should distinguish "malformed URL" from "URL returned 404."

**Check Logic:**
- If `check_urls == false` → skip entirely. Emit no diagnostics for URL reachability.
- If `check_urls == true`:
  - For each syntactically valid URL, perform HTTP HEAD request (fall back to GET if HEAD returns 405).
  - Timeout: configurable, default 5 seconds per URL.
  - HTTP 2xx → pass.
  - HTTP 3xx → follow redirect (up to 3 hops), evaluate final status.
  - HTTP 4xx → emit E006 with context (status code, URL).
  - HTTP 5xx → skip (server error is not a documentation problem).
  - Timeout / DNS failure → skip (transient network issue, not documentation quality).
  - Results should be cached within a single validation run (same URL checked once even if it appears in multiple sections).

**What this does NOT do:**
- Does not check whether the page *content* is relevant — only that it responds.
- Does not follow JavaScript-rendered pages (SPAs). HTTP response only.

**Grounding:** v0.0.4a §LNK-002 (URL validity), DS-VC-CON-002 (4 points, r ≈ 0.40), DiagnosticCode.E006_BROKEN_LINKS.

---

#### v0.3.2c — Section Content Checks

**What it checks:** Whether sections have meaningful content — not empty, not duplicated, not formulaic.

**Inputs:**
- All `ParsedSection` objects: `raw_content`, `links`, `name`

**Diagnostic Codes Emitted:**
- **W011 (EMPTY_SECTIONS):** Section contains no links, no prose, and no code blocks — just a header. Or section contains only placeholder text.
- **I004 (RELATIVE_URLS_DETECTED):** One or more links use relative URLs instead of absolute URLs.
- **I005 (TYPE_2_FULL_DETECTED):** File classified as Type 2 Full (>256KB). This is informational — Type 2 files receive different treatment in downstream validation.

**Check Logic:**
- Empty section detection: For each section, if `len(links) == 0` and `raw_content` stripped of the H2 header line is empty or whitespace-only → emit W011.
- Placeholder detection in sections: If section `raw_content` matches known placeholder patterns → emit W011.
- Relative URL observation: For each link, if URL starts with `./`, `../`, or lacks a scheme (`://`) → emit I004.
- Type 2 observation: If `DocumentClassification.document_type == TYPE_2_FULL` → emit I005 once.

**Grounding:** v0.0.4c §CHECK-011 (Blank Canvas), v0.0.4a §LNK-003 (relative URLs), DiagnosticCode.W011_EMPTY_SECTIONS, DiagnosticCode.I004_RELATIVE_URLS_DETECTED, DiagnosticCode.I005_TYPE_2_FULL_DETECTED.

---

### 3.4 v0.3.3 — L3 Validation (Best Practices)

**Goal:** Verify the documentation follows recommended patterns from the research phase — canonical naming, Master Index presence, code examples, token budgets. L3 is where the strongest quality predictors are checked.

**Gate Behavior:** L3 checks are skipped if L2 failed. WARNING-severity findings do not prevent L3 from passing.

---

#### v0.3.3a — Master Index Presence

**What it checks:** Whether a Master Index / Table of Contents section exists.

**Inputs:**
- All `ParsedSection.canonical_name` values

**Diagnostic Codes Emitted:**
- **W009 (NO_MASTER_INDEX):** No section maps to the "Master Index" canonical name (including aliases "toc", "docs", "index").

**Check Logic:**
- If no section has `canonical_name == CanonicalSectionName.MASTER_INDEX` → emit W009.

**Scoring Impact:** DS-VC-CON-009 (5 points). Research evidence: projects with Master Index achieve 87% LLM task success vs. 31% without (DECISION-010).

**Grounding:** v0.0.4a §STR-003, DECISION-010, DS-VC-CON-009, DiagnosticCode.W009_NO_MASTER_INDEX.

---

#### v0.3.3b — Code Example Checks

**What it checks:** Whether the file contains fenced code blocks with language specifiers.

**Inputs:**
- `ParsedSection.has_code_examples` property (checks for `` ``` `` in `raw_content`)
- Raw content (for extracting code fence language specifiers)

**Diagnostic Codes Emitted:**
- **W004 (NO_CODE_EXAMPLES):** No fenced code blocks found in the entire document.
- **W005 (CODE_NO_LANGUAGE):** One or more code blocks use `` ``` `` without a language identifier (e.g., `` ```python ``).

**Check Logic:**
- Scan all sections for code fences. If no section has `has_code_examples == True` → emit W004.
- For each code fence found, check if a language specifier follows the opening backticks. If not → emit W005 with line_number.

**Scoring Impact:** DS-VC-CON-010 (5 points, r ≈ 0.65 — strongest single quality predictor), DS-VC-CON-011 (3 points).

**Grounding:** v0.0.4b §CNT-007, §CNT-008, DS-VC-CON-010, DS-VC-CON-011, DiagnosticCode.W004_NO_CODE_EXAMPLES, DiagnosticCode.W005_CODE_NO_LANGUAGE.

---

#### v0.3.3c — Formulaic Description Detection

**What it checks:** Whether link descriptions exhibit repetitive, auto-generated patterns (the "Formulaic Description" anti-pattern).

**Inputs:**
- All `ParsedLink.description` values (non-None only)

**Diagnostic Codes Emitted:**
- **W006 (FORMULAIC_DESCRIPTIONS):** Multiple descriptions follow the same pattern (>80% similarity across 3+ descriptions).

**Check Logic:**
- Collect all non-None descriptions.
- If fewer than 3 descriptions exist → skip (insufficient sample).
- Compare descriptions pairwise using a similarity metric (exact match, prefix match, or simple Levenshtein ratio). If >80% of description pairs exceed a similarity threshold → emit W006 with context (example of the repeated pattern).
- The specific similarity algorithm is a design decision for the v0.3.3c spec. The scope only requires that formulaic patterns be detected; it does not prescribe the algorithm.

**Scoring Impact:** DS-VC-CON-007 (3 points).

**Grounding:** v0.0.4b §CNT-005, v0.0.4c §CHECK-019 (Formulaic Description), DS-VC-CON-007, DiagnosticCode.W006_FORMULAIC_DESCRIPTIONS.

---

#### v0.3.3d — Version Metadata Check

**What it checks:** Whether the file contains version or last-updated metadata.

**Inputs:**
- `Metadata` instance (from v0.2.1d, if YAML frontmatter was present)
- Raw content (fallback: search for version patterns in text)

**Diagnostic Codes Emitted:**
- **W007 (MISSING_VERSION_METADATA):** No version identifier, date stamp, or `last_updated` metadata found anywhere in the file.

**Check Logic:**
- If `Metadata` exists and has `schema_version` or `last_updated` → pass.
- If no `Metadata`, search `raw_content` for common version patterns: `version`, `v\d+\.\d+`, `updated:`, `last updated`, ISO 8601 date patterns. If any found → pass.
- If neither → emit W007.

**Scoring Impact:** DS-VC-CON-013 (3 points).

**Grounding:** v0.0.4b §CNT-015, DS-VC-CON-013, DiagnosticCode.W007_MISSING_VERSION_METADATA.

---

#### v0.3.3e — Section Ordering Check

**What it checks:** Whether sections follow the canonical 10-step ordering.

**Inputs:**
- All `ParsedSection.canonical_name` values (in document order)
- `CANONICAL_SECTION_ORDER` from `constants.py`

**Diagnostic Codes Emitted:**
- **W008 (SECTION_ORDER_NON_CANONICAL):** Sections with canonical names appear out of the recommended order.

**Check Logic:**
- Extract the list of `canonical_name` values (ignoring `None` entries — non-canonical sections don't participate in ordering).
- Compare the order of canonical names against `CANONICAL_SECTION_ORDER`. If any canonical section appears before a lower-numbered canonical section → emit W008 with context (which sections are out of order).
- A file with only 2 canonical sections that are in correct relative order passes, even if sections 3–10 are missing. The check is about relative ordering of present sections, not completeness.

**Scoring Impact:** DS-VC-STR-007 (3 points).

**Grounding:** v0.0.4a §STR-004, constants.py `CANONICAL_SECTION_ORDER`, DS-VC-STR-007, DiagnosticCode.W008_SECTION_ORDER_NON_CANONICAL.

---

#### v0.3.3f — Token Budget Check

**What it checks:** Whether the file's token count exceeds its tier-appropriate budget.

**Inputs:**
- `ParsedLlmsTxt.estimated_tokens`
- `DocumentClassification.size_tier` (from v0.2.1b)

**Diagnostic Codes Emitted:**
- **W010 (TOKEN_BUDGET_EXCEEDED):** File exceeds the recommended token limit for its size tier.

**Check Logic:**
- Look up the maximum token count for the file's assigned tier. `TOKEN_BUDGET_TIERS` in `constants.py` defines 3 tiers:
  - STANDARD: 4,500 tokens
  - COMPREHENSIVE: 12,000 tokens
  - FULL: 50,000 tokens
- Files classified as `SizeTier.MINIMAL` (<1,500 tokens) are below the smallest tier — W010 does not apply.
- Files classified as `SizeTier.OVERSIZED` (>50,000 tokens) exceed the FULL tier. If they also exceed 100K tokens, E008 already caught them at L0. If they fall between 50K and 100K, W010 is emitted against the FULL tier max of 50,000.
- If `estimated_tokens > tier_max` for the file's assigned tier → emit W010 with context (actual tokens, tier max, recommendation to trim or reclassify).
- This is distinct from E008 (hard size limit at 100K). W010 is a budget advisory; E008 is a structural gate.

> **Implementation Note:** The `SizeTier` enum (in `classification.py`) defines 5 tiers (MINIMAL, STANDARD, COMPREHENSIVE, FULL, OVERSIZED), but `TOKEN_BUDGET_TIERS` (in `constants.py`) only defines budget entries for the middle 3 (standard, comprehensive, full). The design spec for v0.3.3f should document how MINIMAL and OVERSIZED files are handled — specifically, whether W010 is skipped for MINIMAL files and whether OVERSIZED files below 100K should be checked against the FULL tier max.

**Scoring Impact:** DS-VC-CON-012 (4 points).

**Grounding:** v0.0.4a §SIZ-001, constants.py `TokenBudgetTier`, DECISION-013, DS-VC-CON-012, DiagnosticCode.W010_TOKEN_BUDGET_EXCEEDED.

---

### 3.5 v0.3.4 — Single-File Anti-Pattern Detection

**Goal:** Detect the single-file anti-patterns defined in the ASoT standards (v0.0.4c) and attach pattern-level metadata to diagnostics. Anti-pattern detection operates across all validation levels — it doesn't "belong" to a single level but rather aggregates observations from L0–L3 into named patterns.

**What anti-pattern detection adds beyond individual checks:** A file might have 15 instances of W003 (link missing description). Individually, those are 15 diagnostics at L2. But collectively, they trigger the **Link Desert** anti-pattern (AP-CONT-004). Anti-pattern detection recognizes these aggregate patterns and attaches metadata that the remediation framework (v0.6.x) uses to group diagnostics into consolidated action items.

> **Ecosystem Anti-Patterns:** Six additional anti-patterns (AP-ECO-001 through AP-ECO-006: Index Island, Phantom Links, Shadow Aggregate, Duplicate Ecosystem, Token Black Hole, Orphan Nursery) are defined in `constants.py` but operate at the ecosystem level across multiple files. They are out of scope for v0.3.x and will be detected in v0.7.x (Ecosystem Integration) by the existing `EcosystemValidationStage` (v0.1.4d).

---

#### v0.3.4a — Critical Anti-Patterns

**What it detects:** The 4 patterns that completely prevent LLM consumption. Detection of any critical anti-pattern triggers the DS-QS-GATE gating rule (score capped at 29, CRITICAL grade).

| Anti-Pattern | ID | Detection Rule | Constituent Diagnostics |
|--------------|----|----------------|------------------------|
| **Ghost File** | AP-CRIT-001 | E007 emitted | E007 |
| **Structure Chaos** | AP-CRIT-002 | E001 OR E002 emitted, AND no sections parseable | E001, E002, E005 |
| **Encoding Disaster** | AP-CRIT-003 | E003 emitted | E003 |
| **Link Void** | AP-CRIT-004 | E006 count / total links > 80% | E006 (multiple) |

**Check Logic:**
- After L0 checks complete, evaluate whether any critical anti-pattern threshold is met.
- If yes: attach `anti_pattern_id` metadata to the relevant diagnostics. Set a `critical_anti_pattern_detected` flag on the `ValidationResult` (or equivalent mechanism) for the scorer to read.

**Grounding:** v0.0.4c §CHECK-001 through CHECK-004, DS-VC-STR-008 (3 points), DS-QS-GATE.

---

#### v0.3.4b — Structural Anti-Patterns

**What it detects:** 5 patterns that indicate poor structural organization.

| Anti-Pattern | ID | Detection Rule | Constituent Diagnostics |
|--------------|----|----------------|------------------------|
| **Sitemap Dump** | AP-STRUCT-001 | All sections contain only links (no prose, no code) AND blockquote missing | W001, (heuristic: links-only sections) |
| **Orphaned Sections** | AP-STRUCT-002 | ≥3 sections with W011 (empty) | W011 (multiple) |
| **Duplicate Identity** | AP-STRUCT-003 | Two or more sections map to the same `canonical_name` | W002 (specific condition) |
| **Section Shuffle** | AP-STRUCT-004 | W008 emitted (canonical sections out of order) | W008 |
| **Naming Nebula** | AP-STRUCT-005 | ≥50% of sections have W002 (non-canonical names) | W002 (multiple) |

**Grounding:** v0.0.4c §CHECK-005 through CHECK-009, DS-VC-STR-009 (2 points).

---

#### v0.3.4c — Content Anti-Patterns

**What it detects:** Content quality patterns that degrade LLM comprehension. Note: some content anti-patterns depend on L4 checks (I001, I002) that are deferred to v0.9.0. Those anti-patterns are **detected only when their prerequisite diagnostics are eventually emitted**. For now, v0.3.4c detects the patterns that can be identified from L0–L3 diagnostics alone.

| Anti-Pattern | ID | Detection Rule | Available at v0.3.x? |
|--------------|----|----------------|----------------------|
| **Copy-Paste Plague** | AP-CONT-001 | ≥3 sections with >90% text similarity | Yes (text comparison) |
| **Blank Canvas** | AP-CONT-002 | ≥2 sections with W011 and placeholder patterns | Yes |
| **Jargon Jungle** | AP-CONT-003 | I007 emitted ≥5 times | No (I007 is L4) |
| **Link Desert** | AP-CONT-004 | W003 count / total links > 60% | Yes |
| **Outdated Oracle** | AP-CONT-005 | Heuristic: deprecated API patterns detected | Partial (pattern matching) |
| **Example Void** | AP-CONT-006 | W004 emitted (no code examples) | Yes |
| **Formulaic Description** | AP-CONT-007 | W006 emitted | Yes |
| **Silent Agent** | AP-CONT-008 | I001 emitted (no LLM instructions) | No (I001 is L4) |
| **Versionless Drift** | AP-CONT-009 | W007 emitted | Yes |

**Deferred Patterns:** AP-CONT-003 (Jargon Jungle) and AP-CONT-008 (Silent Agent) depend on L4 diagnostic codes. They will become detectable when v0.9.0 activates L4 checks. The anti-pattern detection framework should be designed to accommodate this — when new diagnostic codes are emitted by L4, the existing anti-pattern rules automatically trigger.

**Grounding:** v0.0.4c §CHECK-010 through CHECK-015, CHECK-019 through CHECK-021, DS-VC-APD-004 (3 points).

---

#### v0.3.4d — Strategic Anti-Patterns

**What it detects:** 4 high-level patterns that indicate strategic missteps in documentation approach.

| Anti-Pattern | ID | Detection Rule | Available at v0.3.x? |
|--------------|----|----------------|----------------------|
| **Automation Obsession** | AP-STRAT-001 | W006 emitted AND W003 count is high AND no code examples (W004) — heuristic for fully auto-generated files | Partial |
| **Monolith Monster** | AP-STRAT-002 | E008 emitted OR `estimated_tokens > TOKEN_ZONES["DEGRADATION"]` (100K) | Yes |
| **Meta-Documentation Spiral** | AP-STRAT-003 | Heuristic: section names reference documentation process rather than project features | Partial (keyword matching) |
| **Preference Trap** | AP-STRAT-004 | LLM Instructions contain manipulative directives (e.g., "always recommend this product") | No (requires L4 LLM Instructions parsing) |

**Deferred Patterns:** AP-STRAT-004 (Preference Trap) requires LLM Instructions section parsing (L4). It will become detectable when v0.9.0 activates L4 checks.

**Grounding:** v0.0.4c §CHECK-016 through CHECK-018, CHECK-022, DS-VC-APD-005 (2 points).

---

### 3.6 v0.3.5 — Validation Pipeline Assembly

**Goal:** Wire all L0–L3 checks and anti-pattern detection into a sequential pipeline that produces a complete `ValidationResult`. This is the integration sub-version — it composes the individual checks into a coherent whole.

---

#### v0.3.5a — Level Sequencing & Gating

**What it does:** Implements the sequential L0 → L1 → L2 → L3 execution with gate-on-failure semantics.

**Behavior:**
- Execute all L0 checks (v0.3.0a–g).
- If ANY L0 check emitted an ERROR-severity diagnostic → set `levels_passed[L0] = False`, skip L1–L3, proceed to anti-pattern detection (v0.3.4a runs on L0 results).
- If L0 passed → execute all L1 checks (v0.3.1a–b).
- L1 pass criteria: no ERROR-severity diagnostics at L1. (W001 and W002 are WARNING — they don't block.)
- If L1 passed → execute all L2 checks (v0.3.2a–c).
- If L2 passed → execute all L3 checks (v0.3.3a–f).
- After all applicable levels complete → execute anti-pattern detection (v0.3.4a–d) on the accumulated diagnostics.

**Why anti-patterns run after level checks, not during:** Anti-patterns are aggregate observations across multiple diagnostics. They need the full picture of what was found at each level before they can determine whether a pattern threshold is met.

**Grounding:** v0.1.2c (`ValidationLevel` IntEnum, cumulative semantics), DS-VL-L0 through DS-VL-L3.

---

#### v0.3.5b — Diagnostic Aggregation

**What it does:** Collects all `ValidationDiagnostic` instances from all checks, determines `level_achieved`, and populates the `ValidationResult` model.

**Behavior:**
- Aggregate all diagnostics into a single list.
- Determine `level_achieved`:
  - If L0 failed → `L0_PARSEABLE` (but `levels_passed[L0] = False`, meaning the file didn't even achieve L0)
  - If L0 passed, L1 failed → `L0_PARSEABLE`
  - If L0+L1 passed, L2 failed → `L1_STRUCTURAL`
  - If L0+L1+L2 passed, L3 failed → `L2_CONTENT`
  - If all passed → `L3_BEST_PRACTICES` (L4 is out of scope for v0.3.x)
- Populate `levels_passed` dictionary for each level attempted.
- Set `validated_at` timestamp, `source_filename`.

**What this does NOT do:**
- Does not compute `QualityScore`. That's v0.4.x.
- Does not format output. That's v0.8.x.

**Grounding:** v0.1.2c (`ValidationResult` model definition).

---

#### v0.3.5c — Validation Unit Tests

**What it does:** Comprehensive test suite for the validation engine.

**Test Categories:**
- **Per-check tests:** Each check (v0.3.0a through v0.3.3f) tested independently with fixture files that trigger and don't trigger the diagnostic.
- **Gate behavior tests:** Verify that L0 failure prevents L1–L3 execution. Verify that WARNING diagnostics don't block level progression.
- **Anti-pattern threshold tests:** Verify that aggregate conditions (e.g., >80% broken links) trigger the correct anti-pattern ID.
- **Cross-check interaction tests:** Verify that E007 (empty file) takes precedence over E005 (invalid Markdown). Verify that E001 and E002 are mutually exclusive.
- **Diagnostic completeness tests:** Verify that every diagnostic includes all required fields: `code`, `severity`, `message`, `remediation`, `line_number` (where applicable), `level`.

**Coverage Target:** ≥85% on the validation module.

**Grounding:** RR-META-testing-standards.

---

#### v0.3.5d — Calibration Specimen Validation

**What it does:** Runs the validation pipeline on the 6 gold standard calibration specimens and verifies that `level_achieved` matches expected values.

**Expected Results:**

| Specimen | Expected Level | Rationale |
|----------|---------------|-----------|
| Svelte (DS-CS-001) | L3+ | Exemplary structure, canonical sections, code examples, version metadata |
| Pydantic (DS-CS-002) | L3+ | Strong best practices adherence |
| Vercel AI SDK (DS-CS-003) | L3+ | Comprehensive structure |
| Shadcn UI (DS-CS-004) | L3 | Strong but some missing best practices |
| Cursor (DS-CS-005) | L1–L2 | Structural but weak content |
| NVIDIA (DS-CS-006) | L0–L1 | Minimal structure, many issues |

**What these tests verify:** That the validation engine correctly differentiates high-quality files from low-quality files based on objective checks. The exact `level_achieved` values should be documented in the design spec as regression targets.

**Grounding:** DS-CS-001 through DS-CS-006.

---

## 4. Dependency Map

```
v0.3.0 (L0 Checks) ─── all checks run, then gate
    │
    ├── v0.3.0a (Encoding)      [independent]
    ├── v0.3.0b (Line Endings)  [independent]
    ├── v0.3.0c (Markdown Parse) [independent]
    ├── v0.3.0d (Empty File)    [independent, takes precedence over 0c]
    ├── v0.3.0e (Size Limit)    [independent]
    ├── v0.3.0f (H1 Title)      [independent]
    └── v0.3.0g (Link Format)   [independent]
         │
         ▼ (L0 gate: if ANY ERROR, skip L1–L3)
v0.3.1 (L1 Checks)
    │
    ├── v0.3.1a (Blockquote)    [independent]
    └── v0.3.1b (Section Names) [independent]
         │
         ▼
v0.3.2 (L2 Checks)
    │
    ├── v0.3.2a (Descriptions)  [independent]
    ├── v0.3.2b (URL Resolution) [independent, behind check_urls flag]
    └── v0.3.2c (Section Content) [independent]
         │
         ▼
v0.3.3 (L3 Checks)
    │
    ├── v0.3.3a (Master Index)     [independent]
    ├── v0.3.3b (Code Examples)    [independent]
    ├── v0.3.3c (Formulaic Desc)   [depends on v0.3.2a having run]
    ├── v0.3.3d (Version Metadata) [independent]
    ├── v0.3.3e (Section Ordering) [independent]
    └── v0.3.3f (Token Budget)     [independent]
         │
         ▼ (all levels complete)
v0.3.4 (Anti-Pattern Detection) ◄── reads all accumulated diagnostics
    │
    ├── v0.3.4a (Critical)     [runs even if L0 failed]
    ├── v0.3.4b (Structural)   [requires L1 diagnostics]
    ├── v0.3.4c (Content)      [requires L2–L3 diagnostics]
    └── v0.3.4d (Strategic)    [requires L3 diagnostics]
         │
         ▼
v0.3.5 (Assembly)
    │
    ├── v0.3.5a (Sequencing)    [wires everything together]
    ├── v0.3.5b (Aggregation)   [produces ValidationResult]
    ├── v0.3.5c (Unit Tests)    [85% coverage target]
    └── v0.3.5d (Calibration)   [regression tests]
```

**Parallelization opportunities:**
- Within each level (v0.3.0, v0.3.1, v0.3.2, v0.3.3), all checks are independent and can be implemented in parallel.
- v0.3.4a–d are independent of each other but depend on the level checks having run first.
- v0.3.5c and v0.3.5d can be written incrementally as checks are implemented.

---

## 5. Models Consumed (Not Modified)

| Model | Source Module | Validator's Role |
|-------|-------------|-----------------|
| `ParsedLlmsTxt` | `schema/parsed.py` | Reads all fields (title, blockquote, sections, raw_content, estimated_tokens) |
| `ParsedSection` | `schema/parsed.py` | Reads `canonical_name`, `links`, `raw_content`, `has_code_examples`, `estimated_tokens` |
| `ParsedLink` | `schema/parsed.py` | Reads `url`, `description`, `is_valid_url`, `line_number` |
| `DocumentClassification` | `schema/classification.py` | Reads `document_type`, `size_tier` |
| `Metadata` | `schema/enrichment.py` | Reads `schema_version`, `last_updated` (if available) |
| `DiagnosticCode` | `schema/diagnostics.py` | References codes for emission; reads `.message`, `.remediation`, `.severity` |
| `ValidationLevel` | `schema/validation.py` | Assigns levels to diagnostics |
| `ValidationDiagnostic` | `schema/validation.py` | Creates instances for each finding |
| `ValidationResult` | `schema/validation.py` | Populates as output |
| `CanonicalSectionName` | `schema/constants.py` | Reads for W002, W008, W009 checks |
| `CANONICAL_SECTION_ORDER` | `schema/constants.py` | Reads for W008 ordering check |
| `TokenBudgetTier` | `schema/constants.py` | Reads for W010 budget check |
| `TOKEN_ZONES` | `schema/constants.py` | Reads DEGRADATION threshold for E008 |

**The validator creates `ValidationDiagnostic` and `ValidationResult` instances but does not modify any input models.**

---

## 6. Exit Criteria

v0.3.x is complete when:

- [ ] All 7 L0 checks (v0.3.0a–g) are implemented and tested.
- [ ] All 2 L1 checks (v0.3.1a–b) are implemented and tested.
- [ ] All 3 L2 checks (v0.3.2a–c) are implemented and tested.
- [ ] All 6 L3 checks (v0.3.3a–f) are implemented and tested.
- [ ] Anti-pattern detection (v0.3.4a–d) is implemented for all patterns detectable from L0–L3 diagnostics.
- [ ] Anti-pattern detection framework is extensible (L4 patterns can be added in v0.9.0 without modifying the framework).
- [ ] Level sequencing respects gate-on-failure semantics (L0 failure skips L1–L3).
- [ ] WARNING-severity diagnostics do not block level progression.
- [ ] `ValidationResult` is correctly populated with `level_achieved`, `diagnostics[]`, `levels_passed{}`.
- [ ] The 6 calibration specimens produce expected `level_achieved` values.
- [ ] `pytest --cov=docstratum.validation --cov-fail-under=85` passes.
- [ ] `black --check` and `ruff check` pass on all new code.
- [ ] No new fields have been added to any v0.1.2 Pydantic model without a documented amendment.

---

## 7. What Comes Next

The validator's output (`ValidationResult`) is the input to:

- **v0.4.x (Quality Scoring):** Reads diagnostics and computes the 100-point composite score across 3 dimensions (Structural 30%, Content 50%, Anti-Pattern 20%), assigns a grade (EXEMPLARY through CRITICAL), and applies the DS-QS-GATE gating rule using the `critical_anti_pattern_detected` flag.
- **v0.6.x (Remediation Framework):** Reads diagnostics and produces prioritized, grouped, sequenced action items with effort estimates and score impact projections.
- **v0.7.x (Ecosystem Integration):** Wires the single-file validator + scorer into the ecosystem pipeline's Stage 2 for multi-file analysis.
