# DS-DD-015: AI Coding Assistants via MCP as Primary Target Consumer

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DD-015 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Decision ID** | DECISION-015 |
| **Date Decided** | 2026-02-05 (v0.0.4d) |
| **Impact Area** | Entire validation philosophy — all quality criteria, token budgets, content standards, and scoring are optimized for MCP consumption by coding assistants |
| **Provenance** | v0.0.3 Adoption Paradox study; MCP specification (Model Context Protocol, Linux Foundation stewardship since Nov 2025); confirmed adoption tracking via GitHub issue #47 |

## Decision

**DocStratum targets AI coding assistants accessed via MCP (Model Context Protocol) as the primary consumer. Search and chat LLMs (ChatGPT, Google Search, Gemini, Perplexity) are explicitly NOT the target, and no optimization effort is directed toward making llms.txt discoverable or consumable by those systems. Token budgets are sized for AI coding assistant context windows (3K–50K tokens). All quality scoring criteria are evaluated from the perspective of what makes coding assistants produce better output.**

## Context

The v0.0.3 research phase uncovered a pattern that fundamentally shaped the strategic direction of DocStratum: the **Adoption Paradox**.

**Grassroots adoption is real and growing:**
- 1,000–5,000 confirmed implementations across public and private repositories
- 75+ tools actively consuming llms.txt (Cursor, Claude Desktop, Windsurf, GitHub Copilot integrations, custom MCP servers)
- Notable adopters include open-source projects, independent developers, and small-to-medium enterprises

**Yet search and chat LLMs show zero confirmed consumption:**
- Google explicitly rejects llms.txt for Search integration (Mueller & Illyes, July 2025 guidance: "We don't index llms.txt for ranking signals")
- No confirmed usage by ChatGPT or other search LLMs despite widespread ecosystem discussion
- Chat LLM consumption requires monolithic file structure (conflicting with DocStratum's modular architecture)
- Zero telemetry or adoption signals from search/chat systems

**MCP is the only validated transport mechanism:**
- Model Context Protocol (Linux Foundation stewardship since Nov 2025) provides the transport and protocol definition
- Cursor, Claude Desktop, and Windsurf have confirmed, active consumption of llms.txt via MCP
- MCP tools call structure maps naturally to DocStratum's 3-layer architecture (entry point → indexed sections → detailed references)
- Developers actively use MCP servers to expose llms.txt to their preferred IDE/editor

This evidence converged on a single conclusion: DocStratum should optimize for the consumption pattern that actually works, rather than hedging bets on a hypothetical search/chat LLM scenario that hasn't materialized despite 18+ months of ecosystem development.

## Alternatives Considered

| Option | Rationale For | Rationale Against |
|--------|---------------|-------------------|
| **Target search LLMs** | Massive potential market; integration with Google Search would unlock 1B+ users | Zero confirmed consumption despite mature ecosystem; Google explicitly rejects llms.txt; requires monolithic file structure (single .txt file) incompatible with DocStratum's modular design; relying on a platform (Google) that has no incentive to prioritize third-party formats |
| **Target both coding assistants and search LLMs** | Hedges bets; maximizes potential reach; no single-use-case risk | Requires conflicting design choices: coding assistants benefit from modular, context-aware files; search LLMs want monolithic, SEO-friendly files. Trying to serve both audiences dilutes focus and produces suboptimal results for both. The Kurzweil Principle applies: "To serve two masters is to serve neither" |
| **Target AI coding assistants via MCP** (CHOSEN) | Confirmed active consumption by Cursor, Claude Desktop, Windsurf; MCP provides validated transport and protocol; 3-layer architecture maps naturally to MCP tool call structure; developers actively use MCP; no conflict with modular design philosophy | Smaller addressable market than global search (1,000–5,000 known implementations vs. potential billions); requires developers to know about MCP and configure tools; market is younger and less proven than search/chat LLMs |

## Rationale

The chosen option was selected because it maximizes probability of creating genuine value where consumption is happening right now:

1. **Evidence-based pragmatism:** Rather than optimizing for a theoretical market (search/chat LLMs) that has shown no interest despite 18+ months of opportunity, DocStratum doubles down on a validated, active market. This is a classic "pick your battles" decision.

2. **MCP is a proven transport:** The Linux Foundation's stewardship of MCP (Nov 2025 onwards) signals the protocol is here to stay. Cursor, Claude Desktop, and Windsurf actively consume llms.txt via MCP, providing proof of concept and real-world validation.

3. **Architectural alignment:** DocStratum's 3-layer architecture (entry point → indexed sections → detailed references) maps naturally to how MCP tools are called:
   - Layer 1 (Master Index): Entry point, returned in the initial tool call
   - Layer 2 (Indexed sections): Individual sections retrieved by name
   - Layer 3 (Detailed references): Links within sections leading to full content

   Search/chat LLM consumption would require flattening this into a single monolithic file, losing the modularity advantage.

4. **Developer audience alignment:** Creators of llms.txt are developers. Developers use IDEs with MCP support (Cursor, Windsurf, Claude Desktop). The producer-consumer feedback loop is short and direct. Contrast with search LLMs, where the feedback loop involves platform decisions made by Google/OpenAI, over which creators have no control.

5. **Strategic positioning:** By explicitly targeting coding assistants via MCP, DocStratum becomes the enrichment and governance layer that makes LLM context actually useful for the use case that works. This is a stronger positioning than "hoping to be discovered by search LLMs."

## Impact on ASoT

This decision ripples across all quality criteria and scoring weights:

- **Token Budget Tiers (DS-DD-013):** Sized for coding assistant context windows (3K–50K), not search/chat windows. Standard tier (3K) reflects the Getting Started pattern for Cursor/Windsurf, where users want quick context. Full tier (40K) reflects comprehensive reference for Claude Desktop with larger context budgets.

- **Content Quality Weights (DS-DD-014):** The content dimension is weighted at 50% because coding assistants benefit most from rich, contextual content (code examples, detailed descriptions). Search LLMs would weight structure higher (they need to extract passages for snippets).

- **Canonical Section Names (DS-DD-012):** The 11 canonical sections are chosen based on what coding assistants need to reason about code (Architecture, Configuration, Examples, API Reference). A search-optimized version would include SEO-favorable sections (Overview, Getting Started from an SEO perspective, etc.).

- **Optional Sections (DS-DD-011):** Meaningful only for coding assistants with context budgets. Search/chat consumption would include all sections equally.

- **MCP tooling & validation:** All validators, formatters, and diagnostics are designed with MCP consumption in mind. For example, section size constraints assume MCP tool call response limits, not Search snippet length limits.

## Constraints Imposed

1. **No SEO optimization:** DocStratum does not include SEO-adjacent features (meta tags, keyword optimization, heading hierarchies for search engines, etc.). If a file happens to be discoverable by search engines via Google's web crawler, that's incidental; it's not a design goal.

2. **Monolithic file flattening is out of scope:** DocStratum explicitly rejects design choices that would optimize for monolithic consumption. The modular, layer-based architecture is a design principle, not a compromise.

3. **Consumer documentation emphasizes MCP:** All user-facing documentation, guides, and examples should emphasize MCP consumption first. Search/chat LLM consumption can be mentioned as "not a primary target" if asked, but shouldn't be promoted.

4. **Metrics and adoption tracking focus on MCP:** Success metrics track MCP consumption (number of MCP servers, adoption in IDEs, usage statistics from Cursor/Claude Desktop) rather than search engine visibility or chat LLM discovery.

5. **Future expansion only if demand shifts:** If and when search/chat LLMs demonstrate active consumption (confirmed telemetry, official statements from Google/OpenAI, etc.), the ASoT can be updated to hedge bets. Until then, maintain singular focus on MCP.

## Related Decisions

- **DS-DD-002** (Three-Layer Architecture): The 3-layer architecture is specifically designed for modular MCP consumption. Layers map to MCP tool call progression.

- **DS-DD-014** (Content Quality Weights): The 50% weighting for content is justified partly by the MCP/coding assistant target (as stated in that decision's rationale section).

- **DS-DD-013** (Token Budget Tiers): Budget tiers are sized for coding assistant context windows, which are an MCP consumption characteristic.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.3 |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
