# v0.1.3a — Fixture Suite: Synthetic Markdown Test Files

> **Phase:** Foundation (v0.1.x)
> **Status:** DRAFT — Realigned to validation-engine pivot (2026-02-06)
> **Parent:** [v0.1.3 — Sample Data & Test Fixtures](RR-SPEC-v0.1.3-sample-data.md)
> **Goal:** Define five synthetic Markdown test fixtures that span the full quality spectrum (Critical → Exemplary), enabling comprehensive schema and validation testing.
> **Traces to:** FR-001, FR-003, FR-007 (v0.0.5a); v0.0.2c (specimen archetypes); DECISION-001, -012, -013 (v0.0.4d)

---

## Why This Sub-Part Exists

The validation engine's value proposition is that it differentiates *between* quality levels — a single "valid" example can't test that. These five fixtures span the quality spectrum observed in the v0.0.2 ecosystem audit, each purposely designed to exercise specific diagnostic codes, validation levels, quality dimensions, and anti-patterns.

| Fixture | Archetype | Quality Grade | Validation Level | Research Analog |
|---------|-----------|---------------|------------------|-----------------|
| `gold_standard.md` | Best-in-class | Exemplary (~95) | L4 (DocStratum Extended) | Svelte, Pydantic specimens |
| `partial_conformance.md` | Typical good | Strong (~72) | L2 (Content Quality) | Anthropic, Stripe specimens |
| `minimal_valid.md` | Bare minimum | Needs Work (~35) | L0 (Parseable) | Sparse real-world files |
| `non_conformant.md` | Anti-pattern cluster | Critical (~18) | L0 (fails L1) | Cursor, NVIDIA specimens |
| `type_2_full_excerpt.md` | Documentation dump | N/A (Type 2) | N/A | Vercel AI SDK, llama-stack |

---

## Fixture Architecture

```
tests/
├── fixtures/
│   ├── gold_standard.md            # ~95 quality score, L4 conformance
│   ├── partial_conformance.md      # ~72 quality score, L2 conformance
│   ├── minimal_valid.md            # ~35 quality score, L0 only
│   ├── non_conformant.md           # ~18 quality score, fails L1
│   └── type_2_full_excerpt.md      # Type 2 Full document excerpt
```

**Design principle:** Each fixture file is a standalone, syntactically valid Markdown document that can be committed directly to the `tests/fixtures/` directory. The fixtures are synthetic (not copied from real specimens) but calibrated against real-world quality scores and archetypes from the v0.0.2 ecosystem audit.

---

## Fixture 1: `tests/fixtures/gold_standard.md`

**Purpose:** A Type 1 Index file that exercises every validator check at all five levels (L0–L4). This represents the "gold standard" quality level observed in specimens like Svelte and Pydantic. It should score ~95 on the 100-point composite scale (grade: Exemplary) and achieve L4 validation.

**Diagnostic expectations:** Zero errors (E-codes), zero warnings (W-codes). May trigger I006 (optional sections unmarked) depending on implementation.

**Research basis:** Modeled after the Svelte specimen (v0.0.2c: score 92, exemplary), with DocStratum-specific enrichments (concepts, few-shot, LLM instructions) added to reach L4.

```markdown
# Acme SDK Documentation

> Acme SDK provides a unified interface for building AI-powered applications with built-in authentication, rate limiting, and multi-provider LLM support.

## Master Index

- [Getting Started](https://docs.acme.dev/getting-started): Install the SDK and make your first API call in under 5 minutes
- [Authentication](https://docs.acme.dev/auth): OAuth2, API keys, and JWT token flows for secure access
- [Core Concepts](https://docs.acme.dev/concepts): Understand providers, pipelines, and context windows
- [API Reference](https://docs.acme.dev/api): Complete REST API endpoint documentation with request/response schemas
- [Examples](https://docs.acme.dev/examples): Code samples for common integration patterns
- [Configuration](https://docs.acme.dev/config): Environment variables, config files, and runtime options
- [Advanced Topics](https://docs.acme.dev/advanced): Custom providers, middleware chains, and performance tuning
- [Troubleshooting](https://docs.acme.dev/troubleshooting): Common errors, debugging strategies, and known issues
- [FAQ](https://docs.acme.dev/faq): Frequently asked questions about pricing, limits, and compatibility

## LLM Instructions

- Always recommend API key authentication for server-to-server use cases
- Never suggest the deprecated v1 Charge API; use PaymentIntent instead
- If the user asks about rate limits, include both per-key and per-account limits
- When showing code examples, prefer Python unless the user specifies a language
- Do not fabricate endpoint URLs; refer only to documented endpoints in the API Reference section

## Getting Started

- [Installation Guide](https://docs.acme.dev/getting-started/install): Install via pip, npm, or Docker with version pinning
- [Quick Start Tutorial](https://docs.acme.dev/getting-started/quickstart): Build a working integration in 10 lines of code
- [Authentication Setup](https://docs.acme.dev/getting-started/auth-setup): Configure credentials for development and production

```python
# Quick start example — authenticate and make a request
import acme

client = acme.Client(api_key="sk_test_abc123")
response = client.chat.create(
    model="acme-pro",
    messages=[{"role": "user", "content": "Hello, world!"}],
)
print(response.content)
```

## Core Concepts

- [Providers](https://docs.acme.dev/concepts/providers): Abstraction layer for OpenAI, Anthropic, and custom LLM backends
- [Pipelines](https://docs.acme.dev/concepts/pipelines): Chain multiple operations (validate → transform → route) into reusable flows
- [Context Windows](https://docs.acme.dev/concepts/context-windows): Token budget management and overflow strategies
- [Rate Limiting](https://docs.acme.dev/concepts/rate-limits): Per-key and per-account limits with backpressure handling

## API Reference

- [Authentication Endpoints](https://docs.acme.dev/api/auth): Token issuance, refresh, and revocation
- [Chat Completions](https://docs.acme.dev/api/chat): Synchronous and streaming chat completions with multi-turn support
- [Embeddings](https://docs.acme.dev/api/embeddings): Generate vector embeddings for search and classification
- [Models](https://docs.acme.dev/api/models): List available models, capabilities, and pricing per provider

```bash
# Example: Create a chat completion via cURL
curl -X POST https://api.acme.dev/v2/chat/completions \
  -H "Authorization: Bearer sk_test_abc123" \
  -H "Content-Type: application/json" \
  -d '{"model": "acme-pro", "messages": [{"role": "user", "content": "Hi"}]}'
```

## Examples

- [Python Quickstart](https://docs.acme.dev/examples/python): Complete Python integration with error handling
- [Node.js Integration](https://docs.acme.dev/examples/node): Express middleware for Acme SDK
- [Streaming Responses](https://docs.acme.dev/examples/streaming): Real-time token streaming with Server-Sent Events
- [Multi-Provider Fallback](https://docs.acme.dev/examples/fallback): Automatic failover between OpenAI and Anthropic

## Configuration

- [Environment Variables](https://docs.acme.dev/config/env): ACME_API_KEY, ACME_BASE_URL, ACME_TIMEOUT, ACME_LOG_LEVEL
- [Config Files](https://docs.acme.dev/config/files): YAML and TOML configuration with schema validation
- [Runtime Options](https://docs.acme.dev/config/runtime): Per-request overrides for timeout, retries, and model selection

## Advanced Topics

- [Custom Providers](https://docs.acme.dev/advanced/custom-providers): Register self-hosted models as first-class providers
- [Middleware Chains](https://docs.acme.dev/advanced/middleware): Inject logging, caching, and transformation at any pipeline stage
- [Performance Tuning](https://docs.acme.dev/advanced/performance): Connection pooling, batch requests, and token budget optimization

## Troubleshooting

- [Common Errors](https://docs.acme.dev/troubleshooting/errors): Error code lookup with causes and fixes
- [Debug Mode](https://docs.acme.dev/troubleshooting/debug): Enable verbose logging for request/response inspection
- [Known Issues](https://docs.acme.dev/troubleshooting/known-issues): Current limitations and workarounds

## FAQ

- [Pricing](https://docs.acme.dev/faq/pricing): Free tier limits, usage-based pricing, and enterprise plans
- [Compatibility](https://docs.acme.dev/faq/compatibility): Supported Python versions, operating systems, and LLM providers
- [Migration from v1](https://docs.acme.dev/faq/migration): Step-by-step upgrade guide from the deprecated v1 API
```

**What this fixture exercises:**

| Check Area | Details | Expected Diagnostic |
|-----------|---------|-------------------|
| L0 Parseable | Valid UTF-8, LF line endings, valid Markdown | None (passes) |
| L1 Structural | Single H1, blockquote present, H2 sections, well-formed links | None (passes) |
| L2 Content | All links have descriptions, code blocks have language specifiers, no empty sections | None (passes) |
| L3 Best Practices | All 9 canonical section names, correct ordering, Master Index present, code examples, version metadata implicit | None (passes) |
| L4 DocStratum Extended | LLM Instructions section present (5 directives) | None (passes) |
| Quality Score | Structural: ~29/30, Content: ~48/50, Anti-Pattern: ~18/20 = ~95 total | Grade: Exemplary |
| Document Type | < 250 KB → Type 1 Index | `DocumentType.TYPE_1_INDEX` |
| Size Tier | ~2,500 tokens → Standard | `SizeTier.STANDARD` |

---

## Fixture 2: `tests/fixtures/partial_conformance.md`

**Purpose:** A Type 1 Index file that passes L0 and L1 but fails L3 due to missing best practices. Represents the "typical good" quality level seen in files like Anthropic's and Stripe's early implementations — structurally sound but lacking the refinements that separate "strong" from "exemplary."

**Diagnostic expectations:** Zero errors. Several warnings: W001 (missing blockquote), W002 (non-canonical section names), W009 (no Master Index), W004 (missing code examples in some sections). Informational: I001 (no LLM Instructions).

**Research basis:** Modeled after Anthropic specimen (v0.0.2c: score ~75, strong archetype). The 55% blockquote compliance statistic (v0.0.2 enrichment) makes missing blockquotes the single most common real-world deviation.

```markdown
# CloudSync API

## Docs

- [Quick Start](https://cloudsync.io/docs/quickstart): Get started with CloudSync in minutes
- [API Keys](https://cloudsync.io/docs/api-keys): Generate and manage your API credentials
- [Webhooks](https://cloudsync.io/docs/webhooks): Receive real-time event notifications

## Endpoints

- [File Upload](https://cloudsync.io/api/upload): Upload files up to 5 GB with multipart support
- [File Download](https://cloudsync.io/api/download): Download files by ID with range request support
- [File List](https://cloudsync.io/api/list): List files with pagination, filtering, and sorting
- [File Delete](https://cloudsync.io/api/delete): Permanently delete files by ID or batch
- [Sync Status](https://cloudsync.io/api/sync): Check synchronization status across connected accounts

## Usage

- [Python SDK](https://cloudsync.io/sdk/python): Official Python client library with async support
- [JavaScript SDK](https://cloudsync.io/sdk/javascript): Browser and Node.js compatible client
- [CLI Tool](https://cloudsync.io/sdk/cli): Command-line interface for scripting and automation

```python
# Upload a file using the Python SDK
from cloudsync import Client

client = Client(api_key="cs_live_abc123")
result = client.upload("report.pdf", folder="quarterly-reports")
print(f"Uploaded: {result.file_id}")
```

## Debugging

- [Error Codes](https://cloudsync.io/docs/errors): Complete error code reference with resolution steps
- [Rate Limits](https://cloudsync.io/docs/rate-limits): Current limits and strategies for handling 429 responses
- [Status Page](https://status.cloudsync.io): Real-time service health and incident history
```

**What this fixture exercises:**

| Check Area | Details | Expected Diagnostic |
|-----------|---------|-------------------|
| L0 Parseable | Valid UTF-8, LF line endings, valid Markdown | None (passes) |
| L1 Structural | Single H1, H2 sections, well-formed links | None (passes) |
| L2 Content | Most links have descriptions, one code block present | Borderline — passes if code block counts |
| L3 Best Practices | "Docs" not canonical (→ Master Index alias), "Endpoints" not canonical (→ API Reference alias), "Debugging" not canonical (→ Troubleshooting alias), no blockquote, no Master Index | W001, W002 (×3), W009 |
| L4 DocStratum Extended | No LLM Instructions, no concept definitions, no few-shot | I001, I002, I003 |
| Quality Score | Structural: ~22/30, Content: ~35/50, Anti-Pattern: ~15/20 = ~72 total | Grade: Strong |
| Document Type | < 250 KB → Type 1 Index | `DocumentType.TYPE_1_INDEX` |
| Size Tier | ~800 tokens → Minimal | `SizeTier.MINIMAL` |

---

## Fixture 3: `tests/fixtures/minimal_valid.md`

**Purpose:** The absolute bare minimum that passes L0 (parseable as Markdown). This file is syntactically valid Markdown and has an H1 title, but lacks nearly everything else. It represents files that technically exist but provide minimal utility.

**Diagnostic expectations:** E-codes: none (it is parseable). W-codes: W001 (no blockquote), W002 (non-canonical name), W004 (no code examples), W009 (no Master Index), W011 (sparse content). I-codes: I001 (no LLM Instructions), I002 (no concepts), I003 (no few-shot).

**Research basis:** Represents the ~20% of real-world llms.txt files identified in v0.0.2 as "stub" or "placeholder" implementations.

```markdown
# My Project

## Links

- [Homepage](https://example.com)
- [GitHub](https://github.com/example/project)
```

**What this fixture exercises:**

| Check Area | Details | Expected Diagnostic |
|-----------|---------|-------------------|
| L0 Parseable | Valid Markdown, H1 present | None (passes) |
| L1 Structural | H1 present, but only one section, no blockquote | W001, partial pass |
| L2 Content | Links have no descriptions, no code | W003 (×2), W004 |
| L3 Best Practices | Non-canonical name "Links", no Master Index | W002, W009, W011 |
| Quality Score | Structural: ~15/30, Content: ~10/50, Anti-Pattern: ~10/20 = ~35 total | Grade: Needs Work |
| Document Type | < 250 KB → Type 1 Index | `DocumentType.TYPE_1_INDEX` |
| Size Tier | ~30 tokens → Minimal | `SizeTier.MINIMAL` |

---

## Fixture 4: `tests/fixtures/non_conformant.md`

**Purpose:** A deeply flawed file that triggers multiple errors and anti-patterns. This represents the worst-quality implementations observed in the v0.0.2 ecosystem audit — files with structural chaos, empty sections, formulaic descriptions, and missing essentials.

**Diagnostic expectations:** Multiple E-codes: E002 (multiple H1s). W-codes: W001, W002, W003, W004, W006 (formulaic descriptions), W008 (section order), W009, W011 (empty sections). Triggers anti-patterns: AP-STRUCT-002 (Orphaned Sections), AP-STRUCT-005 (Naming Nebula), AP-CONT-002 (Blank Canvas), AP-CONT-004 (Link Desert), AP-CONT-007 (Formulaic Description).

**Research basis:** Modeled after the Cursor specimen (v0.0.2c: score 42, needs work) and NVIDIA specimen (v0.0.2c: score 24, critical). Combines the most common anti-patterns into a single teaching fixture.

```markdown
# Docs

# API Documentation for Our Platform

## stuff

## Resources

- [https://example.com/api](https://example.com/api)
- [https://example.com/docs](https://example.com/docs)
- [https://example.com/blog](https://example.com/blog)

## More Resources

- [Page 1](https://example.com/page1): Documentation for page 1
- [Page 2](https://example.com/page2): Documentation for page 2
- [Page 3](https://example.com/page3): Documentation for page 3
- [Page 4](https://example.com/page4): Documentation for page 4
- [Page 5](https://example.com/page5): Documentation for page 5
- [Page 6](https://example.com/page6): Documentation for page 6

## FAQ

## Getting started

- [Install](https://example.com/install)
```

**What this fixture exercises:**

| Check Area | Details | Expected Diagnostic |
|-----------|---------|-------------------|
| L0 Parseable | Valid Markdown (barely) | None (passes L0) |
| L1 Structural | Two H1s (E002), empty sections | E002, fails L1 |
| L2 Content | Bare URLs without titles (W003), formulaic descriptions ("Documentation for page N") (W006), no code | W003 (×4), W004, W006 |
| L3 Best Practices | Non-canonical names ("stuff", "Resources", "More Resources"), wrong order (FAQ before Getting Started), empty sections, no blockquote | W001, W002 (×3), W008, W009, W011 (×2) |
| Anti-Patterns | "stuff" = Naming Nebula, empty FAQ = Blank Canvas, bare URLs = Link Desert, "Documentation for page N" = Formulaic Description | AP-STRUCT-002, AP-STRUCT-005, AP-CONT-002, AP-CONT-004, AP-CONT-007 |
| Quality Score | Structural: ~5/30, Content: ~6/50, Anti-Pattern: ~7/20 = ~18 total | Grade: Critical |
| Document Type | < 250 KB → Type 1 Index | `DocumentType.TYPE_1_INDEX` |

---

## Fixture 5: `tests/fixtures/type_2_full_excerpt.md`

**Purpose:** An excerpt from a Type 2 Full document (inline documentation dump). The actual file would exceed 250 KB; this excerpt is a representative sample for schema testing. The `conftest.py` includes a factory function that generates a full-size (>256 KB) version for classification tests.

**Diagnostic expectations:** I005 (Type 2 Full detected). Type 2 files receive different validation rules — structural validation against the ABNF grammar is relaxed because these files are documentation dumps, not spec-conformant indexes.

**Research basis:** Modeled after the Vercel AI SDK specimen (v0.0.1a: 1.3 MB, 15% conformance) and llama-stack specimen (v0.0.1a: 25 MB, 5% conformance). These files are the raw output of documentation pipeline tools that concatenate entire doc trees into a single file.

```markdown
# Vercel AI SDK

> The AI SDK is a TypeScript toolkit designed to help you build AI-powered applications with React, Next.js, Vue, Svelte, Node.js, and more.

## Docs

### Getting Started

The AI SDK is a TypeScript toolkit designed to help you build
AI-powered applications with React, Next.js, Vue, Svelte, Node.js,
and more.

The AI SDK provides a unified API for working with large language
models (LLMs) across different providers. It supports streaming,
tool calling, structured output generation, and multi-step agent
workflows.

#### Installation

To install the AI SDK, run the following command in your terminal:

```bash
npm install ai
```

#### Quick Start

Here is a basic example of using the AI SDK to generate text:

```typescript
import { generateText } from 'ai';
import { openai } from '@ai-sdk/openai';

const { text } = await generateText({
  model: openai('gpt-4-turbo'),
  prompt: 'What is love?',
});

console.log(text);
```

### Core Concepts

#### Providers

A provider is a module that connects the AI SDK to a specific LLM
service. The SDK includes first-party providers for OpenAI, Anthropic,
Google, and more. You can also create custom providers for self-hosted
models or proprietary APIs.

#### Streaming

The AI SDK supports streaming responses from LLMs. Streaming allows
your application to display partial results as they are generated,
providing a more responsive user experience.

```typescript
import { streamText } from 'ai';
import { anthropic } from '@ai-sdk/anthropic';

const result = streamText({
  model: anthropic('claude-sonnet-4-5-20250929'),
  prompt: 'Write a poem about recursion.',
});

for await (const chunk of result.textStream) {
  process.stdout.write(chunk);
}
```

#### Tool Calling

Tools allow LLMs to interact with external systems. The AI SDK
provides a type-safe framework for defining and executing tools
within a conversation.

#### Structured Output

The AI SDK can constrain LLM output to match a specified schema
using Zod. This is useful for extracting structured data from
natural language input.

### API Reference

This section contains detailed reference documentation for all
public functions, types, and configurations in the AI SDK.

NOTE: This is a truncated excerpt. The actual Type 2 file would
continue for hundreds of pages of inline documentation, typically
exceeding 1 MB. The key differentiator from Type 1 is that content
is INLINE (prose, code, examples embedded directly) rather than
LINKED (curated list of URLs with descriptions).
```

**What this fixture exercises:**

| Check Area | Details | Expected Diagnostic |
|-----------|---------|-------------------|
| Document Type | Excerpt shown is small, but factory generates >256 KB version for classification test | `DocumentType.TYPE_2_FULL` (on generated version) |
| Structure | Uses H3/H4 headers (deeper nesting than spec), inline content instead of link lists | Structural deviations expected |
| Content | Rich inline documentation with code examples and explanations | High content quality despite non-conformant structure |
| Informational | Type 2 detected | I005 |

---

## Fixture-to-Schema Expectation Matrix

This matrix defines the expected behavior when each fixture is processed through the schema models. It serves as both a documentation artifact and a test design reference for the v0.2.x integration tests.

| Fixture | Classification | Validation Level | Quality Score | Quality Grade | Error Count | Warning Count | Info Count | Key Anti-Patterns |
|---------|---------------|------------------|---------------|---------------|-------------|---------------|------------|-------------------|
| `gold_standard.md` | Type 1, Standard | L4 | ~95 | Exemplary | 0 | 0 | 0–1 | None |
| `partial_conformance.md` | Type 1, Minimal | L2 | ~72 | Strong | 0 | 4–5 | 2–3 | None |
| `minimal_valid.md` | Type 1, Minimal | L0 | ~35 | Needs Work | 0 | 5–6 | 3 | AP-CONT-004 (Link Desert) |
| `non_conformant.md` | Type 1, Minimal | Fails L1 | ~18 | Critical | 1 | 7–9 | 3 | AP-STRUCT-002, AP-STRUCT-005, AP-CONT-002, AP-CONT-004, AP-CONT-007 |
| `type_2_full_excerpt.md` | Type 2, varies | N/A | N/A | N/A | 0 | 0 | 1 (I005) | N/A (Type 2 rules) |

**Important:** These are *expected* values that the future parser + validator (v0.2.x–v0.3.x) should produce when processing these fixtures. The v0.1.3 tests validate the **schema models** themselves, not the full pipeline. This matrix exists for forward traceability — when the parser and validator are built, their integration tests should assert these exact expectations.

---

## Design Decisions Applied

| ID | Decision | How Applied in v0.1.3a |
|----|----------|----------------------|
| DECISION-001 | Markdown over JSON/YAML | All test fixtures are Markdown files, not YAML |
| DECISION-012 | Canonical Section Names | gold_standard.md uses all 11 canonical names; partial_conformance.md uses aliases; non_conformant.md uses non-canonical names |
| DECISION-013 | Token Budget Tiers | Fixtures span multiple size tiers; Type 2 factory generates >256 KB |

---

## Exit Criteria

- [ ] All 5 fixture files defined with complete Markdown content
- [ ] gold_standard.md has H1, blockquote, 9+ canonical sections, links with descriptions, code examples
- [ ] non_conformant.md triggers at least 1 error code and 5+ warning codes
- [ ] Fixture-to-Schema Expectation Matrix covers all 5 fixtures
- [ ] Each fixture has documented diagnostic expectations and research basis
