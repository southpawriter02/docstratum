# Specs

Here is a detailed breakdown and expansion of each requested sub-page under **v0.0.1**, leveraging the completed work in your Notion spec, Wild Examples, and Stripe LLM documentation to create a structured, formalized understanding of missed steps and expansion opportunities.

---

# 📘 v0.0.1a — Formal Grammar & Parsing Rules

## 🔍 Overview

While the initial specification (v0.0.1) defines a file structure for `llms.txt`, it lacks formal grammar rules, parsing guidelines, and edge-case handling mechanisms. This omission creates ambiguity in how consumers (e.g., LLM loaders, validators) interpret and process these files.

## 🧾 Key Omissions from v0.0.1:

- No explicit grammar or syntax definition.
- Missing ordering requirements (e.g., H1 → blockquote → body → H2).
- Lack of parsing pseudocode or reference implementation.
- Undefined behavior for malformed documents (missing sections, out-of-order headers).

## 🛠️ Proposed Additions:

### 1. **Formal Grammar Definition**

Using ABNF (Augmented Backus-Naur Form), define a grammar for the file structure.

```
llms-txt = header-section file-list-sections

header-section = h1-title newline quoted-description newline newline

h1-title = "# " text newline

quoted-description = ">" *(text / newline) newline

file-list-sections = 1*(h2-section)

h2-section = h2-title newline file-entry *(newline file-entry) newline

h2-title = "## " text newline

file-entry = "- [" text "](" URI ")" [ " - " description ]

```

> This grammar enforces strict section ordering and helps build parsers that validate adherence to the format.
> 

### 2. **Parsing Pseudocode**

A simplified reference parser can be implemented as follows:

```python
def parse_llms_txt(file_content):
    lines = file_content.splitlines()

    if not lines[0].startswith("# "):
        raise ValueError("Missing H1 title")

    description_start = 1
    while lines[description_start].startswith(">"):
        description_start += 1

    if lines[description_start] != "":
        raise ValueError("Expected blank line after quoted description")

    file_sections = []
    current_section = None

    for i in range(description_start + 1, len(lines)):
        line = lines[i]

        if line.startswith("## "):
            current_section = {
                'title': line[3:],
                'files': []
            }
            file_sections.append(current_section)

        elif line.startswith("- [") and current_section:
            match = re.match(r'- \\[(.*?)\\]\\((.*?)\\)(?: - (.*))?$', line)
            if match:
                current_section['files'].append({
                    'text': match.group(1),
                    'url': match.group(2),
                    'description': match.group(3) or ""
                })

    return {
        'title': lines[0][2:],
        'description': '\\n'.join(lines[1:description_start]),
        'sections': file_sections
    }

```

> This pseudocode serves as a foundation for building robust validators and loaders.
> 

### 3. **Edge Case Handling**

Define expected behaviors when:

- The quoted description is missing or truncated.
- H2 sections appear before the main header.
- File entries are malformed (e.g., broken URLs).
- Empty or duplicate sections exist.

Each case should have:

- A formal rule (in grammar).
- An expected parser behavior.
- Error reporting strategies.

### 4. **Validation Implications**

This grammar directly feeds into the validator module (v0.2.x), ensuring that:

- All consumers parse consistently.
- Errors are detectable and actionable.
- Tooling can auto-generate templates or lint files.

---

# 📘 v0.0.1b — Spec Gap Analysis & Implications

## 🔍 Overview

The original spec lists eight undefined areas under "What the Spec does NOT Define." However, it doesn’t explore their practical implications. Addressing this gap provides evidence for future schema extensions in DocStratum (v0.1.2).

## 🧾 Gaps with Real-World Consequences

| Gap | Real Impact | Community Workaround |
| --- | --- | --- |
| **Max File Size** | Large token counts (e.g., 107M tokens) cause memory issues and slow processing. | Users manually split files or filter content. |
| **No Versioning** | Impossible to determine if a file is outdated; caching becomes unreliable. | Consumers use timestamps or external version control (e.g., Git). |
| **No File Type Restrictions** | Inclusion of non-textual formats (PDFs, binaries) leads to errors. | Manual filtering or preprocessing steps in tools like FastHTML. |
| **No Context Scope** | No way to indicate intended use (e.g., general knowledge vs fine-tuning). | Developers add tags or comments in the description. |
| **No Link Validation** | Broken links go undetected, leading to failed ingestion. | Tools like sitemap crawlers are used externally. |
| **No File Priority** | All files treated equally, regardless of importance. | Manual selection or weighting in pipelines. |
| **No Language Specification** | Multilingual datasets create ambiguity for model training. | Language detection is done post-ingestion. |
| **No Change Notification Mechanism** | Consumers must poll for changes, wasting resources. | Polling intervals or webhooks are added externally. |

## 🛠️ Implications for Schema Extension (v0.1.2)

Each of these gaps informs potential additions to the schema:

| Gap | Suggested Schema Enhancement |
| --- | --- |
| Max File Size | Introduce optional `max_tokens` field per file entry. |
| Versioning | Add a top-level `version` string or timestamp. |
| File Type Restrictions | Enforce MIME types via metadata or extension rules. |
| Context Scope | Introduce a `scope` field (e.g., "training", "context"). |
| Link Validation | Include a checksum or last-modified timestamp. |
| File Priority | Add a `priority` integer for sorting. |
| Language Specification | Include an optional `lang` attribute. |
| Change Notification | Support for WebSub or RSS feed generation. |

## 🧪 Evidence Base from Wild Examples

From the [Wild Examples](RR-SPEC-v0.0.0-wild-examples-analysis.md) analysis:

- Files with over 100 million tokens broke several ingestion tools.
- Many projects manually versioned files by including date prefixes.
- Some teams used YAML frontmatter to annotate scope and language.

These real-world patterns justify adding structured metadata fields in v0.1.2.

---

# 📘 v0.0.1c — Processing & Expansion Methods

## 🔍 Overview

The original spec briefly lists four processing methods but offers no analysis. Understanding how these are used in practice is critical for Context Builder design (v0.3.2) and tool interoperability.

## 🧾 Processing Methods Table

| Method | Description | Use Case | Tools |
| --- | --- | --- | --- |
| **Concatenation** | Append all files into one large text blob. | Simple embedding or fine-tuning inputs. | FastHTML, LangChain |
| **XML Wrapping** | Wrap each file in XML tags for structured parsing. | Retrieval-based RAG systems. | LlamaIndex, Pinecone |
| **Selective Inclusion** | Only include files matching criteria (e.g., by tag, size). | Reducing token count or targeting specific domains. | Custom scripts |
| **Summarization** | Generate summaries of each file to reduce length. | Context summarization for prompts. | Transformers, T5 |

## 🧠 Comparative Analysis

### 1. **Concatenation**

- ✅ Fast and simple.
- ❌ Loses document boundaries; hard to trace back source.
- 🔧 Used in FastHTML's `llms_txt2ctx`.

### 2. **XML Wrapping**

- ✅ Preserves structure and source info.
- ❌ Increases token overhead slightly.
- 🔧 Used in LlamaIndex for chunked retrieval.

### 3. **Selective Inclusion**

- ✅ Reduces noise and cost.
- ❌ Requires pre-processing rules or annotations.
- 🔧 Used in internal tools at Stripe and Anthropic.

### 4. **Summarization**

- ✅ Compresses long files into manageable chunks.
- ❌ Risk of losing important details.
- 🔧 Used in retrieval pipelines where full text is unnecessary.

## 🧪 FastHTML vs Alternatives

FastHTML’s `llms_txt2ctx` uses concatenation and basic filtering. Compared to more sophisticated tools:

- It lacks XML wrapping for structure preservation.
- No support for summarization pipelines.
- Does not expose filtering hooks (e.g., by language, size).

This suggests that FastHTML is best suited for minimal tooling environments but not scalable LLM ingestion pipelines.

## 🛠️ Implications for Context Builder (v0.3.2)

The Context Builder module should:

- Support all four processing modes.
- Allow configuration of filtering, chunking, and summarization strategies.
- Integrate with schema extensions (v0.1.2) to use metadata like `lang`, `priority`, and `scope`.

---

# 📘 v0.0.1d — Standards Interplay & Positioning

## 🔍 Overview

The spec compares `llms.txt` to robots.txt, sitemap.xml, and humans.txt but stops short of analyzing how they interact in practice. Understanding this interplay is key to positioning DocStratum in the broader ecosystem.

## 🧾 Comparison Recap

| Standard | Purpose | llms.txt Analogy |
| --- | --- | --- |
| **robots.txt** | Controls crawler access. | llms.txt controls LLM ingestion. |
| **sitemap.xml** | Lists crawlable URLs. | llms.txt lists useful files for LLMs. |
| **humans.txt** | Credits contributors. | llms.txt can credit authors or sources. |

## 🔗 Practical Interactions

### 1. **robots.txt Compliance**

- If a URL is disallowed in robots.txt, it should not appear in llms.txt.
- Many organizations auto-generate llms.txt from internal documentation, but ignore robots.txt restrictions — this creates compliance risks.

### 2. **sitemap.xml Integration**

- Sitemaps can be used to auto-generate llms.txt file lists.
- Crawlers that respect both standards can ensure only allowed and indexed pages are included.

### 3. **humans.txt Complementarity**

- llms.txt can reference humans.txt for attribution.
- This enhances transparency and community trust.

## 🧠 Positioning llms.txt in the Ecosystem

### As a **Developer Experience Tool**

- Encourages structured, machine-readable documentation.
- Sits alongside READMEs and API docs.

### As a **LLM Data Discovery Layer**

- Acts as a curated, opinionated index for model-ready data.
- Bridges the gap between raw data and processed training inputs.

### As a **Governance Mechanism**

- Enforces visibility, compliance, and attribution.
- Supports internal governance policies (e.g., no PII in training sets).

## 🧭 Strategic Implications for DocStratum

DocStratum should:

- Encourage integration with existing web standards (robots.txt, sitemap.xml).
- Promote llms.txt as a **declarative interface** for LLM data governance.
- Provide tooling that auto-generates llms.txt from standard sources (e.g., GitHub, GitLab, Notion).

---

# 📌 Summary Table

| Sub-Page | Key Focus | Delivered Content |
| --- | --- | --- |
| **v0.0.1a** | Grammar & Parsing | Formal grammar, parsing pseudocode, edge-case handling |
| **v0.0.1b** | Spec Gaps & Impacts | Real-world implications of 8 spec gaps, schema extension justifications |
| **v0.0.1c** | Processing Methods | Comparative analysis of 4 methods, FastHTML vs alternatives |
| **v0.0.1d** | Standards Interplay | How llms.txt relates to robots.txt, sitemap.xml, humans.txt; positioning strategy |

---

# [v0.0.7] Ecosystem & Quality Standard Specifications

> **Added:** 2026-02-07. These standalone specifications were produced during the ecosystem pivot analysis, extending DocStratum's scope from single-file validator to ecosystem-level documentation quality platform.

## 📘 v0.0.6 — Platinum Standard Definition

### 🔍 Overview

Defines the complete validation standard that DocStratum measures against. The original llms.txt specification provides approximately 10 guidelines — insufficient for a comprehensive quality validator. This document establishes a 30-criterion, 5-level quality framework (L0 Parseable → L1 Structural → L2 Content Quality → L3 Best Practices → L4 Exemplary) with explicit provenance for every criterion, mapping to existing diagnostic codes, anti-patterns, and quality dimensions.

### 🧾 Key Contributions

- **5 quality levels** with measurable criteria at each level
- **30 total criteria** — subsumes the original spec at L1, extends far beyond at L3–L4
- **Provenance chain** — every criterion traces to a research phase document
- **Maps to existing infrastructure** — diagnostic codes, anti-patterns, quality scoring dimensions

---

## 📘 v0.0.7 — Ecosystem Pivot Specification

### 🔍 Overview

Defines the architectural pivot from single-file validator to ecosystem-level documentation quality platform. Introduces a 3-layer ecosystem model (Navigation → Content → Aggregate), 6 new schema entities, 12 new diagnostic codes, 6 ecosystem anti-patterns, a 5-stage pipeline, and a 4-phase migration plan. 100% backward compatible — single-file input produces byte-identical output.

### 🧾 Key Contributions

- **3-layer ecosystem model:** Navigation (llms.txt index), Content (individual .md pages), Aggregate (llms-full.txt)
- **6 new schema entities:** DocumentEcosystem, EcosystemFile, FileRelationship, EcosystemScore, EcosystemHealthDimension, LinkRelationship
- **12 new diagnostic codes** (E009–E010, W012–W018, I008–I010) — total now 38
- **6 ecosystem anti-patterns** (AP_ECO_001–006) — total now 28
- **5-stage pipeline:** Discovery → Per-File Validation → Relationship Mapping → Ecosystem Validation → Ecosystem Scoring
- **4-phase migration plan:** Design Docs → Schema Extension → Pipeline Extension → Test Infrastructure
- **Backward compatibility:** single-file mode produces byte-identical output to pre-pivot design

---

# 📌 Summary Table (Updated)

| Sub-Page | Key Focus | Delivered Content |
| --- | --- | --- |
| **v0.0.1a** | Grammar & Parsing | Formal grammar, parsing pseudocode, edge-case handling |
| **v0.0.1b** | Spec Gaps & Impacts | Real-world implications of 8 spec gaps, schema extension justifications |
| **v0.0.1c** | Processing Methods | Comparative analysis of 4 methods, FastHTML vs alternatives |
| **v0.0.1d** | Standards Interplay | How llms.txt relates to robots.txt, sitemap.xml, humans.txt; positioning strategy |
| **[v0.0.7] v0.0.6** | Platinum Standard | 30-criterion, 5-level quality framework for llms.txt validation |
| **[v0.0.7] v0.0.7** | Ecosystem Pivot | 3-layer ecosystem model, 6 schema entities, 12 diagnostic codes, 5-stage pipeline |