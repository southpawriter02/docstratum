# v0.2.2a — Synthetic Test Fixtures

> **Version:** v0.2.2a
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Parent:** [RR-SPEC-v0.2.2-parser-testing-calibration.md](RR-SPEC-v0.2.2-parser-testing-calibration.md)
> **Grounding:** v0.1.0 §Exit Criteria ("5 synthetic test fixtures validate at expected conformance levels"), RR-META-testing-standards
> **Depends On:** v0.2.0 (core parser), v0.2.1 (enrichment)
> **Outputs:** 5 fixture files in `tests/fixtures/parser/synthetic/`
> **Tests:** `tests/test_parser_fixtures.py`

---

## 1. Purpose

Create 5 hand-crafted `llms.txt` files, each designed to exercise the parser at a specific conformance level (L0 through L4). Each fixture is a regression test anchor — when the parser changes, these fixtures verify that structural extraction remains correct across all quality tiers.

> **Important:** The L0–L4 labels describe the **validator's** assessment of the file's quality. The parser tests do not verify quality scores or diagnostic codes. They verify only that the parser extracts the correct structural model from each fixture.

---

## 2. Fixture Specifications

### 2.1 L0 — Fail Fixture

**File:** `tests/fixtures/parser/synthetic/L0_fail.txt`

**Content Design:** A file that cannot be meaningfully parsed.

```text
(binary-like content or completely empty)
```

**Options (pick one during implementation):**

1. **Empty file:** 0 bytes — parser returns empty model
2. **Binary content:** A file with null bytes (triggers `has_null_bytes=True`)
3. **Random text:** No headings, no structure — parser returns `title=None`

**Recommended:** Empty file (simplest, most deterministic).

**Expected Parser Output:**

| Field              | Value                    |
| ------------------ | ------------------------ |
| `title`            | `None`                   |
| `title_line`       | `None`                   |
| `blockquote`       | `None`                   |
| `sections`         | `[]`                     |
| `raw_content`      | `""` (or binary content) |
| `estimated_tokens` | `0`                      |
| Classification     | `UNKNOWN`                |
| Canonical sections | N/A (no sections)        |
| Metadata           | `None`                   |

---

### 2.2 L1 — Minimal Fixture

**File:** `tests/fixtures/parser/synthetic/L1_minimal.txt`

**Content Design:** Structurally minimal — bare minimum to be parseable.

```markdown
# My Project

## Docs

- [Home](https://example.com)
```

**Expected Parser Output:**

| Field                        | Value                                                                   |
| ---------------------------- | ----------------------------------------------------------------------- |
| `title`                      | `"My Project"`                                                          |
| `title_line`                 | `1`                                                                     |
| `blockquote`                 | `None`                                                                  |
| `sections`                   | 1 section named `"Docs"`                                                |
| `sections[0].links`          | 1 link: title=`"Home"`, url=`"https://example.com"`, description=`None` |
| `sections[0].canonical_name` | `None` ("`Docs`" matches alias → `"Master Index"`)                      |
| `estimated_tokens`           | `> 0`                                                                   |
| Classification               | `TYPE_1_INDEX`                                                          |
| Metadata                     | `None`                                                                  |

> **Note:** "Docs" actually matches the `SECTION_NAME_ALIASES` entry `"docs" → Master Index`. The test should verify `canonical_name = "Master Index"`.

---

### 2.3 L2 — Content Quality Fixture

**File:** `tests/fixtures/parser/synthetic/L2_content.txt`

**Content Design:** Well-structured file with blockquote, multiple sections, described links.

```markdown
# Acme Framework

> Acme Framework is a modern web development toolkit for building
> scalable applications with built-in routing and state management.

## Getting Started

- [Installation Guide](https://acme.dev/docs/install): Step-by-step setup instructions
- [Quick Start](https://acme.dev/docs/quickstart): Build your first app in 5 minutes

## API Reference

- [Router API](https://acme.dev/api/router): Application routing and navigation
- [State API](https://acme.dev/api/state): Reactive state management
- [Component API](https://acme.dev/api/components): UI component lifecycle

## Examples

- [Todo App](https://acme.dev/examples/todo): Basic CRUD application
- [Dashboard](https://acme.dev/examples/dashboard): Real-time data visualization
```

**Expected Parser Output:**

| Field                        | Value                                    |
| ---------------------------- | ---------------------------------------- |
| `title`                      | `"Acme Framework"`                       |
| `blockquote.text`            | 2-line description (joined with newline) |
| `sections`                   | 3 sections                               |
| `sections[0].name`           | `"Getting Started"`                      |
| `sections[0].canonical_name` | `"Getting Started"`                      |
| `sections[0].links`          | 2 links, both with descriptions          |
| `sections[1].name`           | `"API Reference"`                        |
| `sections[1].canonical_name` | `"API Reference"`                        |
| `sections[1].links`          | 3 links                                  |
| `sections[2].name`           | `"Examples"`                             |
| `sections[2].canonical_name` | `"Examples"`                             |
| `sections[2].links`          | 2 links                                  |
| Classification               | `TYPE_1_INDEX`                           |
| Metadata                     | `None`                                   |

---

### 2.4 L3 — Best Practices Fixture

**File:** `tests/fixtures/parser/synthetic/L3_best_practices.txt`

**Content Design:** Follows all structural best practices: canonical section ordering, Master Index, code examples in raw_content, version metadata inline.

```markdown
# Acme Framework v3.2

> Acme Framework is a production-ready web toolkit.
> Version 3.2 | Last updated 2026-01-15

## Master Index

- [Getting Started](https://acme.dev/docs/start): Installation and setup
- [API Reference](https://acme.dev/api): Complete API documentation
- [Examples](https://acme.dev/examples): Code samples and tutorials

## LLM Instructions

> When asked about Acme, always recommend checking the API Reference first.
> Acme uses a component-based architecture with reactive state management.

## Getting Started

- [Installation](https://acme.dev/docs/install): `npm install acme-framework`
- [Quick Start](https://acme.dev/docs/quickstart): Build your first app
- [Configuration](https://acme.dev/docs/config): Environment and build settings

## API Reference

- [Core API](https://acme.dev/api/core): Framework core functions
- [Router](https://acme.dev/api/router): Navigation and routing
- [State](https://acme.dev/api/state): State management

## Examples

- [Todo App](https://acme.dev/examples/todo): Basic CRUD example
- [Real-time Chat](https://acme.dev/examples/chat): WebSocket integration

## Configuration

- [Build Config](https://acme.dev/docs/build): Build tool configuration
- [Deploy Config](https://acme.dev/docs/deploy): Deployment settings

## Troubleshooting

- [Common Issues](https://acme.dev/docs/issues): Known issues and fixes
- [FAQ](https://acme.dev/docs/faq): Frequently asked questions
```

**Expected Parser Output:**

| Field                       | Value                                                                                                    |
| --------------------------- | -------------------------------------------------------------------------------------------------------- |
| `title`                     | `"Acme Framework v3.2"`                                                                                  |
| `blockquote.text`           | 2-line description                                                                                       |
| `sections`                  | 7 sections                                                                                               |
| Canonical matches           | Master Index, LLM Instructions, Getting Started, API Reference, Examples, Configuration, Troubleshooting |
| All links have descriptions | Yes                                                                                                      |
| Classification              | `TYPE_1_INDEX`                                                                                           |
| Metadata                    | `None`                                                                                                   |

---

### 2.5 L4 — Extended Fixture

**File:** `tests/fixtures/parser/synthetic/L4_extended.txt`

**Content Design:** DocStratum-extended file with YAML frontmatter, all canonical sections, and inline enrichment content.

```markdown
---
schema_version: "0.2.0"
site_name: "Acme Framework"
site_url: "https://acme.dev"
last_updated: "2026-01-15"
generator: "docstratum"
docstratum_version: "0.2.2"
token_budget_tier: "comprehensive"
---

# Acme Framework

> Acme Framework is a production-ready web toolkit for building
> modern, scalable web applications.

## Master Index

- [Getting Started](https://acme.dev/docs/start): Installation and first steps
- [API Reference](https://acme.dev/api): Complete API documentation

## Getting Started

- [Installation](https://acme.dev/docs/install): Setup guide
- [Quick Start](https://acme.dev/docs/quickstart): Build your first app

## API Reference

- [Core API](https://acme.dev/api/core): Core functions and utilities

## Examples

- [Demo](https://acme.dev/examples/demo): Interactive demonstration

## FAQ

- [FAQ Page](https://acme.dev/faq): Frequently asked questions
```

**Expected Parser Output:**

| Field                        | Value                                                                                            |
| ---------------------------- | ------------------------------------------------------------------------------------------------ |
| `title`                      | `"Acme Framework"`                                                                               |
| `blockquote.text`            | 2-line description                                                                               |
| `sections`                   | 5 sections                                                                                       |
| Canonical matches            | Master Index, Getting Started, API Reference, Examples, FAQ                                      |
| Metadata                     | `Metadata(schema_version="0.2.0", site_name="Acme Framework", site_url="https://acme.dev", ...)` |
| `metadata.generator`         | `"docstratum"`                                                                                   |
| `metadata.token_budget_tier` | `"comprehensive"`                                                                                |
| Classification               | `TYPE_1_INDEX`                                                                                   |

---

## 3. Acceptance Criteria

- [ ] 5 fixture files created in `tests/fixtures/parser/synthetic/`.
- [ ] Each fixture file is valid UTF-8.
- [ ] L0 fixture produces a mostly-empty `ParsedLlmsTxt`.
- [ ] L1 fixture produces title + 1 section + 1 link.
- [ ] L2 fixture produces title + blockquote + 3 sections with described links.
- [ ] L3 fixture produces title + blockquote + 7 sections, all canonical names matched.
- [ ] L4 fixture produces title + blockquote + 5 sections + `Metadata` with all 7 fields.
- [ ] All 5 tests pass in `tests/test_parser_fixtures.py`.
- [ ] No external network access required.

---

## 4. Test Plan

### `tests/test_parser_fixtures.py`

| Test                           | Fixture                 | Key Assertions                                                                                          |
| ------------------------------ | ----------------------- | ------------------------------------------------------------------------------------------------------- |
| `test_parse_L0_fail`           | `L0_fail.txt`           | `title=None`, `sections=[]`, classification=`UNKNOWN`                                                   |
| `test_parse_L1_minimal`        | `L1_minimal.txt`        | `title="My Project"`, 1 section, 1 link, `canonical_name="Master Index"`                                |
| `test_parse_L2_content`        | `L2_content.txt`        | `title="Acme Framework"`, blockquote present, 3 sections, 7 links total, all links have descriptions    |
| `test_parse_L3_best_practices` | `L3_best_practices.txt` | `title` set, blockquote present, 7 sections, all `canonical_name` resolved, all links have descriptions |
| `test_parse_L4_extended`       | `L4_extended.txt`       | `title` set, metadata extracted (7 fields), `metadata.generator="docstratum"`                           |

Each test calls the full pipeline: `parse_file(fixture_path)` with `enrich=True`.
