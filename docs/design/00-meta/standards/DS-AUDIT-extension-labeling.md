# DS-AUDIT: Extension Labeling Audit

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-AUDIT-EXT-001 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.1.0 |
| **Story** | 2.5a (Extension Labeling Audit) |
| **Author** | Ryan (with Claude) |
| **Date** | February 16, 2026 |
| **Source of Truth** | `AnswerDotAI/llms-txt` reference implementation (`miniparse.py`, `core.py`) |
| **Analysis Basis** | `llms-txt-reference-repo-analysis.md` (February 14, 2026) |

---

## Purpose

This document audits every validation criterion, canonical section definition, and ABNF grammar rule in the DocStratum ASoT standards library and explicitly classifies each as **spec-compliant**, **spec-implied**, or a **DocStratum extension**. The purpose is transparency: anyone reading a DocStratum validation result should understand which findings reflect the llms.txt specification's requirements and which reflect DocStratum's opinionated additions.

---

## Classification Taxonomy

| Classification | Code | Definition | Color |
|----------------|------|------------|-------|
| **Spec-Compliant** | `SC` | Behavior directly follows from the spec text AND matches the reference parser (`miniparse.py`) behavior. If the reference parser checks it, it's spec-compliant. | 🟢 Green |
| **Spec-Implied** | `SI` | Reasonable inference the spec assumes but doesn't explicitly state. Not contradicted by the reference parser, but not actively checked by it either. Pre-specification assumptions that any Markdown parser would need. | 🟡 Yellow |
| **DocStratum Extension** | `EXT` | Goes beyond what the spec defines or the reference parser implements. DocStratum's value-add — opinionated quality criteria, best-practice enforcement, or structural rules that the spec intentionally leaves open. | 🔵 Blue |

**Key principle:** The reference parser (`miniparse.py`) is the behavioral ground truth. If the reference parser does something, it's `SC`. If the spec implies it but the parser doesn't enforce it, it's `SI`. If neither the spec nor the parser addresses it, it's `EXT`.

---

## Level 0: Parseable (Pre-Specification)

L0 is explicitly documented as "pre-specification" — criteria the spec assumes without stating. All L0 checks are classified as either `SI` (spec-implied) or `EXT` (extension), because the reference parser does not perform any of these checks; it simply assumes the input is valid text.

| Platinum ID | Name | Diagnostic Code | `spec_origin` | Rationale |
|-------------|------|-----------------|---------------|-----------|
| L0-01 | Valid UTF-8 Encoding | DS-DC-E003 | 🟡 `SI` | The spec doesn't state an encoding, but describes the format as Markdown. UTF-8 is the de facto standard for Markdown files. The reference parser assumes valid text input (Python `str`). DocStratum formalizes this assumption as a checkable gate. |
| L0-02 | Non-Empty Content | DS-DC-E007 | 🟡 `SI` | The spec describes a file with structure (H1, sections). An empty file is implicitly invalid. The reference parser would return an empty document from empty input but doesn't raise an error — DocStratum formalizes the failure mode. |
| L0-03 | Valid Markdown Syntax | DS-DC-E005 | 🟡 `SI` | The spec says "a markdown file" — valid Markdown is the implicit minimum. The reference parser uses regex on text, not a Markdown AST, so it doesn't validate Markdown syntax per se. DocStratum adds explicit CommonMark validation. |
| L0-04 | Under Maximum Token Limit | DS-DC-E008 | 🔵 `EXT` | **Extension.** The spec does not mention file size or token limits. The reference implementation's `get_sizes()` function measures token sizes but does not enforce limits. DocStratum's 100K token ceiling is an opinionated quality gate based on context window constraints observed in the benchmark study. |
| L0-05 | Line Feed Normalization | DS-DC-E004 | 🔵 `EXT` | **Extension.** The spec doesn't specify line endings. The reference parser uses Python's `str.splitlines()`, which handles CRLF, LF, and CR transparently. DocStratum's requirement for LF-only is a stricter normalization rule that goes beyond both spec and reference behavior. |

**L0 Summary:** 0 SC, 3 SI, 2 EXT.

---

## Level 1: Structural (Spec-Defined)

L1 is the first level that evaluates spec-defined structure. Most L1 criteria map directly to behaviors the reference parser enforces. This is the level with the highest proportion of spec-compliant classifications.

| DS Identifier | Platinum ID | Name | `spec_origin` | Rationale |
|---------------|-------------|------|---------------|-----------|
| DS-VC-STR-001 | L1-01 | H1 Title Present | 🟢 `SC` | **Spec-compliant.** The spec states files "should start with an H1." The reference parser (`miniparse.py`) uses `^# (.+)$` to extract the title and the document model requires it (`title` field). Both spec and reference parser expect exactly one H1 at the start. |
| DS-VC-STR-002 | L1-02 | Single H1 Only | 🟢 `SC` | **Spec-compliant.** The spec describes a single H1 as the document title. The reference parser extracts only the first `^# ` match and treats the rest of the document as sections. Multiple H1s would be structurally ambiguous. The reference parser's behavior implicitly enforces single-H1. |
| DS-VC-STR-003 | L1-03 | Blockquote Present | 🟡 `SI` | **Spec-implied.** The spec describes the blockquote ("followed by a blockquote") but the canonical sample file includes it as a pattern, not a hard requirement. The reference parser captures it via `^>\s*(?P<summary>.+?$)` but handles its absence gracefully (empty summary). Empirical data: 45% of production specimens omit it. DocStratum classifies this as SOFT for good reason. |
| DS-VC-STR-004 | L1-04 | H2 Section Structure | 🟢 `SC` | **Spec-compliant.** The spec requires "one or more markdown sections" delimited by H2 headers. The reference parser splits on `^##\s*(.*?$)` exclusively. At least one H2 section is structurally required by both spec and reference implementation. |
| DS-VC-STR-005 | L1-05 | Link Format Compliance | 🟢 `SC` | **Spec-compliant.** The spec defines the link format as `- [Title](URL): description`. The reference parser uses `-\s*\[(?P<title>[^\]]+)\]\((?P<url>[^\)]+)\)(?::\s*(?P<desc>.*))?` which matches this pattern exactly. Dash prefix required, brackets required, description optional. |
| DS-VC-STR-006 | L1-06 | No Heading Level Violations | 🔵 `EXT` | **Extension.** The spec does not prohibit H3+ headings. The reference parser treats H3+ as content within the current H2 section (they pass through as prose). DocStratum flags heading level jumps (e.g., H1→H3 without H2) as structural violations. This is a quality opinion about heading hierarchy, not a spec requirement. |

**L1 Summary:** 4 SC, 1 SI, 1 EXT.

---

## Level 2: Content Quality (DocStratum Quality Layer)

L2 evaluates content meaningfulness — entirely beyond what the reference parser checks. The reference parser performs zero content quality validation; it parses structure and returns results. All L2 criteria are DocStratum extensions.

| DS Identifier | Platinum ID | Name | `spec_origin` | Rationale |
|---------------|-------------|------|---------------|-----------|
| DS-VC-CON-001 | L2-01 | Non-Empty Link Descriptions | 🔵 `EXT` | **Extension.** The spec says descriptions are optional (`: description` is in brackets in the grammar). The reference parser captures descriptions when present but does not flag their absence. DocStratum promotes descriptions as a quality signal based on empirical correlation data (r ~ 0.45 with overall quality). |
| DS-VC-CON-002 | L2-02 | URL Resolvability | 🔵 `EXT` | **Extension.** The spec does not require URLs to be reachable. The reference parser does not validate URLs. DocStratum adds HTTP reachability checks as a content quality measure — broken links provide zero value to an LLM agent. |
| DS-VC-CON-003 | L2-03 | No Placeholder Content | 🔵 `EXT` | **Extension.** The spec has no concept of placeholder detection. The reference parser treats all text content equally. DocStratum detects "TODO", "Coming soon", and similar patterns as content debt indicators. |
| DS-VC-CON-004 | L2-04 | Non-Empty Sections | 🔵 `EXT` | **Extension.** The spec doesn't explicitly require sections to have content. The reference parser includes empty sections in its output without flagging them. DocStratum warns about empty sections (heading with no entries or prose) as they waste tokens and confuse navigation. |
| DS-VC-CON-005 | L2-05 | No Duplicate Sections | 🔵 `EXT` | **Extension.** The spec doesn't prohibit duplicate section names. The reference parser would create two sections with the same name. DocStratum flags duplicates as likely structural errors that degrade LLM navigation. |
| DS-VC-CON-006 | L2-06 | Substantive Blockquote | 🔵 `EXT` | **Extension.** The spec describes the blockquote as "a short description" but doesn't define "substantive." The reference parser captures the blockquote text without evaluating it. DocStratum checks for minimum length and non-boilerplate content. |
| DS-VC-CON-007 | L2-07 | No Formulaic Descriptions | 🔵 `EXT` | **Extension.** The spec doesn't evaluate description quality. The reference parser treats all descriptions equally. DocStratum detects auto-generated patterns (e.g., Mintlify's "Learn about X" templates) that reduce information density — based on the v0.0.2c empirical audit finding that formulaic descriptions correlate with lower overall quality. |

**L2 Summary:** 0 SC, 0 SI, 7 EXT.

---

## Level 3: Best Practices (DocStratum Quality Layer)

L3 evaluates documentation best practices derived from empirical analysis of 450+ llms.txt files. None of these criteria exist in the spec or reference parser. All are DocStratum extensions.

### Structural Dimension Criteria at L3

| DS Identifier | Platinum ID | Name | `spec_origin` | Rationale |
|---------------|-------------|------|---------------|-----------|
| DS-VC-STR-007 | L3-06 | Canonical Section Ordering | 🔵 `EXT` | **Extension.** The spec does not define a canonical section order. The reference parser processes sections in document order without reordering or checking sequence. DocStratum's 10-step canonical ordering (Master Index → LLM Instructions → Getting Started → ... → Optional) is derived from empirical analysis of high-quality specimens and optimized for progressive disclosure to LLM agents. |
| DS-VC-STR-008 | L3-09 | No Critical Anti-Patterns | 🔵 `EXT` | **Extension.** The spec defines no anti-patterns. The reference parser does not detect anti-patterns. DocStratum's 4 critical anti-patterns (Ghost File, Structure Chaos, Encoding Disaster, Link Void) are severity classifications derived from empirical observation of files that provide zero or negative value to LLM agents. |
| DS-VC-STR-009 | L3-10 | No Structural Anti-Patterns | 🔵 `EXT` | **Extension.** Same rationale as STR-008. DocStratum's structural anti-pattern catalog (e.g., single-section dumps, heading chaos) reflects quality patterns the spec does not address. |

### Content Dimension Criteria at L3

| DS Identifier | Platinum ID | Name | `spec_origin` | Rationale |
|---------------|-------------|------|---------------|-----------|
| DS-VC-CON-008 | L3-01 | Canonical Section Names | 🔵 `EXT` | **Extension.** The spec defines only "Optional" as a semantically special section name. The reference parser treats all section names equally (except checking `k != 'Optional'` for exclusion). DocStratum's 11-name canonical vocabulary (Master Index, LLM Instructions, Getting Started, Core Concepts, API Reference, Examples, Configuration, Advanced Topics, Troubleshooting, FAQ, Optional) is entirely DocStratum's contribution — a standardized taxonomy for LLM-optimized documentation structure. |
| DS-VC-CON-009 | L3-02 | Master Index Present | 🔵 `EXT` | **Extension.** Not in the spec. Not in the reference parser. DocStratum recommends a Master Index section as a navigational entry point for LLM agents — based on the pattern observed in high-quality specimens like Svelte and Pydantic. |
| DS-VC-CON-010 | L3-03 | Code Examples Present | 🔵 `EXT` | **Extension.** Not in the spec. The reference parser does not distinguish code blocks from other content. DocStratum flags the presence of code examples as the strongest single predictor of documentation quality (r ~ 0.65 in v0.0.2c audit). |
| DS-VC-CON-011 | L3-04 | Code Language Specifiers | 🔵 `EXT` | **Extension.** Not in the spec. DocStratum checks whether fenced code blocks include language identifiers (e.g., ` ```python ` vs. bare ` ``` `). Language specifiers improve LLM code comprehension. |
| DS-VC-CON-012 | L3-05 | Token Budget Respected | 🔵 `EXT` | **Extension.** The spec mentions that "a clean markdown file for important information about this project" should be provided but does not define size or token constraints. The reference implementation's `get_sizes()` measures tokens but does not enforce budgets. DocStratum's tiered token budget system is an opinionated quality framework. |
| DS-VC-CON-013 | L3-07 | Version Metadata Present | 🔵 `EXT` | **Extension.** Not in the spec. The reference parser does not look for version metadata. DocStratum recommends version or date information for freshness signaling to LLM agents and content management systems. |

**L3 Summary:** 0 SC, 0 SI, 9 EXT.

---

## Level 4: DocStratum Extended (Full Extension Layer)

L4 is by definition entirely DocStratum extensions. The level is named "DocStratum Extended" and its description explicitly states these features "go beyond the llms.txt specification." No further justification is needed per criterion, but the table is included for completeness.

| DS Identifier | Platinum ID | Name | `spec_origin` | Rationale |
|---------------|-------------|------|---------------|-----------|
| DS-VC-APD-001 | L4-01 | LLM Instructions Section | 🔵 `EXT` | Extension. Not in spec. Inspired by the Stripe llms.txt pattern (v0.0.0). |
| DS-VC-APD-002 | L4-02 | Concept Definitions | 🔵 `EXT` | Extension. Not in spec. DocStratum enrichment for in-context term definitions. |
| DS-VC-APD-003 | L4-03 | Few-Shot Examples | 🔵 `EXT` | Extension. Not in spec. Drawn from LLM prompting best practices. |
| DS-VC-APD-004 | L4-04 | No Content Anti-Patterns | 🔵 `EXT` | Extension. DocStratum anti-pattern catalog (v0.0.4c). |
| DS-VC-APD-005 | L4-05 | No Strategic Anti-Patterns | 🔵 `EXT` | Extension. DocStratum anti-pattern catalog (v0.0.4c). |
| DS-VC-APD-006 | L4-06 | Token-Optimized Structure | 🔵 `EXT` | Extension. DocStratum optimization guidance for context window efficiency. |
| DS-VC-APD-007 | L4-07 | Relative URL Minimization | 🔵 `EXT` | Extension. Spec implies absolute URLs (reference parser captures URLs as-is). DocStratum recommends absolute URLs for portability across LLM contexts where relative resolution may fail. |
| DS-VC-APD-008 | L4-08 | Jargon Defined or Linked | 🔵 `EXT` | Extension. Not in spec. DocStratum readability recommendation for cross-domain LLM access. |

**L4 Summary:** 0 SC, 0 SI, 8 EXT.

---

## Canonical Section Names (DS-CN-*)

| DS Identifier | Canonical Name | `spec_origin` | Rationale |
|---------------|---------------|---------------|-----------|
| DS-CN-001 | Master Index | 🔵 `EXT` | Not in spec. DocStratum canonical vocabulary. |
| DS-CN-002 | LLM Instructions | 🔵 `EXT` | Not in spec. Inspired by Stripe pattern. |
| DS-CN-003 | Getting Started | 🔵 `EXT` | Not in spec. Common documentation pattern, formalized by DocStratum. |
| DS-CN-004 | Core Concepts | 🔵 `EXT` | Not in spec. DocStratum canonical vocabulary. |
| DS-CN-005 | API Reference | 🔵 `EXT` | Not in spec. Common documentation pattern, formalized by DocStratum. |
| DS-CN-006 | Examples | 🔵 `EXT` | Not in spec. DocStratum canonical vocabulary. |
| DS-CN-007 | Configuration | 🔵 `EXT` | Not in spec. DocStratum canonical vocabulary. |
| DS-CN-008 | Advanced Topics | 🔵 `EXT` | Not in spec. DocStratum canonical vocabulary. |
| DS-CN-009 | Troubleshooting | 🔵 `EXT` | Not in spec. DocStratum canonical vocabulary. |
| DS-CN-010 | FAQ | 🔵 `EXT` | Not in spec. DocStratum canonical vocabulary. |
| DS-CN-011 | Optional | 🟢 `SC` | **Spec-compliant.** The spec defines "Optional" as a semantically special section. The reference parser checks `k != 'Optional'` (case-sensitive, exact match) to exclude Optional content by default. |
| DS-CN-011 | Optional **aliases** (supplementary, appendix, extras) | 🔵 `EXT` | **Extension.** The reference parser matches `'Optional'` exactly (case-sensitive, no aliases). DocStratum's alias normalization is a usability extension that allows alternative names to be treated as Optional content. The reference parser would NOT recognize "Supplementary" or "Appendix" as Optional. |

**Canonical Names Summary:** 1 SC (Optional itself), 0 SI, 11 EXT (10 canonical names + Optional aliases).

---

## ABNF Grammar Extension Points

The ABNF grammar defined in `RR-SPEC-v0.0.1a` is itself a DocStratum formalization — the spec provides no formal grammar. The grammar aims to faithfully represent the spec's informal structure description, but several rules extend beyond the reference parser's actual behavior.

| Grammar Rule | Location | `spec_origin` | Extension Details |
|-------------|----------|---------------|-------------------|
| `blockquote-desc = 1*blockquote-line` | §1, lines 96–101 | 🔵 `EXT` | **Multi-line blockquote.** The reference parser captures only a single-line blockquote via `^>\s*(?P<summary>.+?$)`. The ABNF allows `1*blockquote-line` (one or more lines), which is a deliberate superset. **Already annotated** in the grammar with an inline comment. |
| `CRLF = %x0D.0A / %x0A` | §1, line 130 | 🟢 `SC` | **Permissive line endings.** Both the grammar and the reference parser (via Python `splitlines()`) accept CRLF and LF. This is behavioral parity. Note: DocStratum's *L0-05 validation criterion* is stricter than both (requires LF-only), which is the extension. |
| `section-name` matching | §2, line 319 | 🔵 `EXT` | **Case-insensitive Optional matching.** The parsing pseudocode uses `section_name.lower() == "optional"`, which matches case-insensitively. The reference parser uses `k != 'Optional'` (case-sensitive, capital O). DocStratum's pseudocode is more permissive than the reference. This should be noted as a deliberate usability extension. |
| Grammar Notes §6 | §1, line 141 | 🟡 `SI` | **H3+ nesting.** The grammar notes that H3 headers appear in real-world files as sub-section organizers. The reference parser treats H3+ as content (prose within the current H2 section), which is faithful to the spec's H2-only section splitting. The grammar does not structurally define H3+, consistent with both spec and reference. |
| Grammar Note §5 | §1, line 140 | 🔵 `EXT` | **Type 1/Type 2 classification.** The document type classification (Index vs. Full) is entirely a DocStratum contribution. The spec does not distinguish between llms.txt and llms-full.txt structural patterns. The reference implementation handles both via the same parser entry point. |

---

## Aggregate Classification Summary

| Level | Total Criteria | 🟢 SC | 🟡 SI | 🔵 EXT |
|-------|---------------|-------|-------|--------|
| L0 (Parseable) | 5 | 0 | 3 | 2 |
| L1 (Structural) | 6 | 4 | 1 | 1 |
| L2 (Content Quality) | 7 | 0 | 0 | 7 |
| L3 (Best Practices) | 9 | 0 | 0 | 9 |
| L4 (DocStratum Extended) | 8 | 0 | 0 | 8 |
| **Validation Criteria Total** | **35** | **4** | **4** | **27** |
| Canonical Names | 12 | 1 | 0 | 11 |
| ABNF Rules | 5 | 1 | 1 | 3 |
| **Grand Total** | **52** | **6** | **5** | **41** |

### What This Tells Us

**Only 4 of 35 validation criteria are spec-compliant.** These are the L1 structural checks that directly match the reference parser's behavior: H1 present, single H1, H2 sections, and link format. Everything else is either an implicit assumption the spec doesn't state (4 criteria) or a DocStratum extension (27 criteria).

**This is by design.** The llms.txt spec is deliberately minimal — the canonical parser is 20 lines of Python. It defines a file format, not a quality framework. DocStratum's entire value proposition is the 27 extensions: the content quality checks, the best-practice patterns, the anti-pattern detection, the canonical vocabulary, and the tiered validation system. Without those extensions, "validation" would be: "Does it have an H1, at least one H2, and properly formatted links?" — a check that takes four regex matches.

**The extension labeling makes DocStratum more credible, not less.** By being transparent about what's spec-compliant and what's opinionated, DocStratum allows consumers to choose their validation depth. A tool that only wants spec compliance can run L0–L1. A tool that wants DocStratum's quality framework enables L2–L4. The labeling makes this choice explicit.

---

## Implications for Implementation

1. **Validation output should include `spec_origin` per criterion.** When DocStratum reports that a file fails DS-VC-CON-008 (Canonical Section Names), the report should note `spec_origin: EXT` so the consumer knows this is a DocStratum recommendation, not a spec violation.

2. **"Spec compliance" mode should be possible.** A consumer who only cares about spec compliance should be able to run DocStratum with a flag that limits checks to `SC` and `SI` criteria. This is effectively L0–L1 with STR-006 excluded.

3. **Documentation should distinguish levels clearly.** L0–L1 are "Does this file conform to the llms.txt specification?" L2–L4 are "Does this file meet DocStratum's quality standards?" The language in reports and CLI output should reflect this distinction.

4. **The ABNF grammar's multi-line blockquote rule should remain as-is.** It's a useful extension — multi-line blockquotes are valid Markdown and should be supported — but the annotation noting it's an extension beyond reference behavior must be preserved.

5. **The case-insensitive Optional matching in the pseudocode should be documented.** It's a usability improvement over the reference parser's case-sensitive match, but it should be labeled as a deliberate extension so implementers know they're diverging from the canonical behavior.

---

## Acceptance Criteria Checklist (Story 2.5a)

- [x] Every validation criterion in the ASoT standards library has a `spec_origin` classification — **52 items classified across criteria, canonical names, and grammar rules**
- [x] The ABNF grammar's extension points are annotated — **5 extension points identified; multi-line blockquote already annotated inline; case-insensitive matching and Type classification identified as new annotation targets**
- [x] A summary document maps each extension to its rationale — **This document; every EXT classification includes a rationale field**
- [ ] DS-CN-011 (Optional section) updated to note that alias support is a DocStratum extension — **Pending: Task 2.5a.4**

---

## Change History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | February 16, 2026 | Initial audit. 52 items classified. Story 2.5a Tasks 2.5a.1 and 2.5a.2 complete. |
