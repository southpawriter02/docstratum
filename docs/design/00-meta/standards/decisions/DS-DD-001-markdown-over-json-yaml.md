# DS-DD-001: Markdown over JSON/YAML

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DD-001 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Decision ID** | DECISION-001 |
| **Date Decided** | 2026-01-10 (v0.0.4d) |
| **Impact Area** | Schema Models (all `src/docstratum/schema/*.py`) |
| **Provenance** | v0.0.4d §Differentiators and Decision Log |

## Decision

**The llms.txt format is a Markdown file (CommonMark 0.30 + GFM), not YAML or JSON. Schema models must represent parsed Markdown structure, not treat the format as a YAML or JSON data serialization.**

## Context

The ASoT standards library needed to select a primary serialization format for llms.txt. The official llms.txt specification (https://llms.txt) defines Markdown as the native format. Analysis of 450+ projects using llms.txt revealed that 95%+ use Markdown variants as the source format. Early implementation confusion arose from treating Markdown as a data serialization layer (comparing it to YAML or JSON), which misrepresents the format's narrative, human-readable nature and the parsed AST structure that schema models operate on.

## Alternatives Considered

| Option | Rationale For | Rationale Against |
|--------|---------------|-------------------|
| JSON | Machine-parseable, strict schema validation possible | Unreadable in raw form, poor for narrative content, no native support for code blocks and examples, breaks GitHub's native rendering |
| YAML | Hierarchical structure, human-friendly than JSON, reduces nesting | Verbose for long-form content, hard to include code blocks elegantly, indentation-sensitive errors, adds parsing complexity for marginal benefit |
| HTML | Rich formatting, widely supported | Not version-control friendly, verbose and hard to read raw, bloats repository size, lossy for plain-text preservation |
| Custom Format | Fully optimized for ASoT needs | High fragmentation risk, no ecosystem support, steep learning curve for contributors, reinventing wheels already solved |
| **Markdown (chosen)** | **Human readable in raw form, machine-parseable into AST, GitHub renders natively, code examples and headings native, narrative-friendly, 95%+ of llms.txt projects use variants, CommonMark is standardized, rich ecosystem of parsers** | **Loses some structural type enforcement that YAML/JSON provide, but schema validation compensates via parsed AST inspection** |

## Rationale

Markdown was selected because it balances three critical dimensions: **readability** (humans can open an llms.txt file and understand its structure without parsing), **machine-parseability** (well-defined CommonMark/GFM specifications enable reliable parsing), and **narrative capability** (Markdown supports headings, lists, code blocks, links, and other natural documentation patterns).

The schema model's job is not to enforce YAML structure but to validate the *parsed semantic content* of the Markdown. This distinction is crucial: the schema inspects the Markdown AST (abstract syntax tree) to ensure sections are present, code blocks are tagged, links are valid, and so on. This approach aligns with how 95%+ of deployed llms.txt projects actually structure their documentation.

Comparing Markdown to JSON/YAML is a category error. JSON and YAML are data serialization formats. Markdown is a markup language for narrative content. The ASoT standards library treats Markdown as a first-class narrative format, parsed into a semantic representation, not as a fallback for JSON.

## Impact on ASoT

1. **Parser Implementation:** All schema models in `src/docstratum/schema/*.py` must target the Markdown AST, not raw YAML/JSON parsing. The `Document` model represents a parsed Markdown tree with sections, blocks, and inline elements.

2. **Validation Criteria:** ASoT validation rules operate on Markdown semantic structure: section presence, heading hierarchy, code block language tags, link validity, GFM table format compliance.

3. **Schema Evolution:** The schema evolves based on what Markdown structures are required/recommended, not based on "how similar are we to JSON/YAML."

4. **Tooling:** The `mistletoe` parser (targeting CommonMark 0.30 + GFM) is the canonical parser. All validation tooling must use this parser to generate the AST.

## Constraints Imposed

1. **Parser Requirements:** All Markdown parsing must use a CommonMark 0.30 compliant parser with GFM extensions. No regex-based or line-by-line parsing is acceptable for ASoT compliance.

2. **Format Boundaries:** ASoT does not support mixing formats (e.g., Markdown with embedded YAML frontmatter for metadata). All metadata must be expressed in Markdown (e.g., as H1/H2 sections, tables, or structured text).

3. **Backward Compatibility:** If new Markdown features are needed, they must be CommonMark/GFM compatible. No vendor-specific extensions without strong justification.

4. **Tooling Ecosystem:** Schema models and validation rules tie to the CommonMark/GFM AST contract. Changes to the parser must be coordinated with schema updates.

## Related Decisions

- **DS-DD-003:** GitHub Flavored Markdown (GFM) as Standard — specifies which Markdown flavor the parser targets
- **DS-DD-002:** 3-Layer Architecture — depends on Markdown's narrative structure for layer definition

## Ecosystem Context: Parallel llms.txt Specifications

The llms.txt format is not governed by a single standards body. Multiple organizations have published specifications that extend the original proposal, each targeting different use cases. DocStratum's ASoT is designed to validate **software documentation** llms.txt files, but practitioners should be aware of the broader ecosystem when authoring or evaluating llms.txt content.

### The Original Proposal (llmstxt.org)

The llms.txt specification was published in September 2024 by Jeremy Howard (founder of fast.ai and Answer.AI). It defines a Markdown file located at `/llms.txt` in a website's root path containing: an H1 with the project or site name (required), a blockquote with a short summary, zero or more Markdown sections of detail, and zero or more H2-delimited sections containing file lists of URLs with optional descriptions. The specification is hosted at https://llmstxt.org and is the foundation that DocStratum's validation criteria are built against.

As of early 2026, over 844,000 websites have implemented some form of llms.txt (per BuiltWith tracking), including Anthropic, Cloudflare, Stripe, and Hugging Face. However, no major LLM provider has officially confirmed that their models read llms.txt at inference time — adoption is driven by forward-looking SEO strategy and documentation best practices rather than confirmed LLM consumption.

### AI Visibility Definition (365i — UK)

The 365i organization (https://www.ai-visibility.org.uk) published an extended llms.txt specification (Version 1.1.0, January 2026) as part of their broader "AI Visibility Definition" framework (currently at v1.3.2). Their specification explicitly adopts and extends the llmstxt.org convention, adding structured business identity use cases.

Key differences from the original proposal and from DocStratum's scope:

1. **Domain focus**: 365i targets business identity (consultancies, agencies, service providers), not software documentation. Their recommended sections include "Team," "Locations," "Certifications," "Awards," "Partners," and "Industries" — none of which overlap with DocStratum's canonical section names (DS-CN-001 through DS-CN-011: Master Index, LLM Instructions, API Reference, etc.).

2. **Content restrictions**: 365i defines explicit "Content Not Permitted" rules — no marketing hyperbole, superlatives ("best," "leading," "world-class"), pricing information, unverifiable claims, competitor references, testimonials, or personal data. This aligns closely with DocStratum's DS-AP-STRAT-004 (Preference Trap), which independently detects manipulative promotional language.

3. **Companion files**: 365i defines additional discovery files beyond llms.txt — including ai.txt (usage permissions), ai.json (machine-parseable interaction guidance), brand.txt (naming conventions), and identity.json (structured identity data). DocStratum does not validate these formats.

4. **Relationship to DocStratum**: The specifications are **complementary, not conflicting**. DocStratum's validation pipeline could score a 365i-compliant file — it would likely pass structural criteria (H1, blockquote, H2 sections, valid links) but score differently on content criteria that expect software-documentation sections. If DocStratum expands beyond software documentation, the 365i section taxonomy would be a valuable reference for defining domain-specific canonical names.

### Implications for DocStratum

The existence of domain-specific llms.txt extensions validates DocStratum's core thesis: that **documentation quality measurement** is an independent concern from **documentation content specification**. Different industries will define different section requirements, but all will benefit from structural validation, anti-pattern detection, and quality scoring. DocStratum's validation pipeline is designed to measure quality within a defined scope (software documentation), and its architecture — scored dimensions, configurable weights, extensible criteria — could accommodate additional domains in future versions.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.3 |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
| 1.1.0-scaffold | 2026-02-08 | Added Ecosystem Context section documenting parallel llms.txt specifications (llmstxt.org original, 365i AI Visibility Definition v1.1.0) and their relationship to DocStratum |
