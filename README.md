# The Rosetta Root

> Don't just auto-generate a sitemap. Hand-craft the "Platinum Standard" llms.txt file.

A semantic translation layer for AI agents browsing documentation. The Rosetta Root is a hand-crafted `/llms.txt` architecture designed to eliminate **context collapse** — the systematic loss of meaning when LLMs encounter unstructured, navigation-heavy, or semantically ambiguous web content.

---

## The Problem

AI agents reading documentation websites today face input quality issues, not reasoning issues. Pages designed for humans with eyes fail for language models with context windows. The result: navigation pollution, ambiguous terminology, missing relationships, and inconsistent formatting all degrade agent performance.

## The Approach

The Rosetta Root provides three layers of structured context that no sitemap or auto-generated index can:

- **Master Index** — Canonical URLs, content types, and freshness timestamps. Answers: *"What exists?"*
- **Concept Map** — Definitions, dependency graphs, and anti-patterns. Answers: *"How do things relate?"*
- **Few-Shot Bank** — Golden Q&A pairs, code templates, and error patterns. Answers: *"How should I answer?"*

The core thesis: a Technical Writer with strong Information Architecture skills can outperform a sophisticated RAG pipeline by simply writing better source material. **Structure is a feature.**

## What This Project Builds

A toolkit for authoring, validating, and demonstrating the effectiveness of hand-crafted `/llms.txt` files. The system includes schema validation, context assembly within token budgets, side-by-side agent comparison (baseline vs. Rosetta-enhanced), and quality metrics — all designed to prove that curated structure beats engineering complexity.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.11+ |
| Schema & Validation | Pydantic |
| LLM Integration | LangChain, LiteLLM |
| LLM Providers | OpenAI, Anthropic |
| Demo Interface | Streamlit |
| Testing | pytest, pytest-cov |
| Code Quality | Black, Ruff |

## Project Status

**Phase**: Foundation (v0.1.x)
**Status**: Active Development

## Documentation

Full specifications, research, and implementation roadmap live in [`docs/`](docs/README.md).

## License

MIT
