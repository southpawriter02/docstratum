# DS-DD-011: Optional Sections Explicitly Marked

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DD-011 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Decision ID** | DECISION-011 |
| **Date Decided** | 2026-02-04 (v0.0.4d) |
| **Impact Area** | Validation Pipeline (diagnostic I006 OPTIONAL_SECTIONS_UNMARKED), Content Criteria |
| **Provenance** | v0.0.4a context-window analysis; AI coding assistant UX research §3.2 |

## Decision

**Optional sections in llms.txt files must be explicitly marked with an "Optional:" prefix in the heading and accompanied by a blockquote annotation that includes a token estimate and skip-safety statement. This enables context-aware consumption by LLM agents and allows graceful degradation when context windows are limited.**

## Context

During v0.0.4a research on context-window constraints for AI coding assistants, the team identified a critical consumption pattern: agents with limited remaining context need to make intelligent decisions about which content to preserve. The problem is that creators cannot distinguish between sections that are essential for agent reasoning (e.g., "Installation", "Architecture") and sections that provide supplementary depth (e.g., "Historical Context", "Advanced Troubleshooting").

Without explicit markers, agents either:
1. Include everything, consuming excessive tokens
2. Randomly omit sections, potentially removing critical information
3. Have no principled way to gracefully degrade when approaching token limits

The explicit marking pattern solves this by giving agents two pieces of information: what the author intended as optional, and a token estimate to help them make informed decisions about inclusion.

## Alternatives Considered

| Option | Rationale For | Rationale Against |
|--------|---------------|-------------------|
| No optional sections at all | Simpler for creators, no ambiguity, every section treated equally | Loses flexibility; forces authors to choose between comprehensive documentation and tight context budgets; some supplementary content is genuinely useful but not required |
| Unmarked optional (creator knows but consumer cannot tell) | Minimal overhead for documentation, authors can mentally track optionality | Agents have no signal; consumption decisions become arbitrary; defeats the purpose of having optional sections |
| Explicit marking with "Optional:" prefix + blockquote token estimate + skip-safety statement (CHOSEN) | Agents can reliably identify skippable content, token estimates enable principled prioritization, skip-safety annotation confirms section independence, authors signal intent clearly | Requires discipline from creators; blockquote annotation overhead (3-4 lines per optional section) |

## Rationale

The chosen option was selected because it provides the maximum signal to consumers with minimal friction on creators:

1. **LLM-agent utility:** Agents consuming llms.txt via MCP can now parse optional markers and make evidence-based decisions: "This section is 400 tokens, optional, and safe to skip. Do I have budget? If yes, include. If no, continue without."

2. **Author discipline is low-cost:** The overhead is 3-4 lines per optional section. The "Optional:" prefix is scannable by both humans and token-counting algorithms. The blockquote format is already standard in llms.txt files.

3. **Backward compatibility:** Files without optional sections remain valid (diagnostic I006 is advisory, not blocking). Files with unmarked optional content trigger diagnostic I006, signaling a missed opportunity rather than a violation.

4. **Empirical validation:** This pattern mirrors MCP tool descriptions, where capabilities are marked as "optional" or "experimental" with usage guidance. The pattern is proven in practice.

## Impact on ASoT

This decision directly determines:

- **Diagnostic I006** (OPTIONAL_SECTIONS_UNMARKED): Emitted when optional sections lack the explicit marker. This is an informational diagnostic that doesn't block validation but indicates a missed opportunity for graceful degradation. [CALIBRATION-NEEDED] Consider severity weighting if we want to make this more prominent in quality scoring.

- **Content Criteria Validation:** The presence of optional section markers becomes part of content richness scoring. Files that use optional sections strategically score higher in the "Accessibility for Context-Limited Consumption" sub-criterion.

- **Token Estimate Format:** The blockquote annotation must follow the format:
  ```
  > This section provides [description]. (~NNN tokens). Safe to skip if [condition].
  ```
  Example:
  ```
  ## Optional: Historical Context
  > This section provides background and project evolution. (~400 tokens). Safe to skip if optimizing for installation-only workflow.
  ```

## Constraints Imposed

1. **Optional sections must include token estimates:** The estimate should reflect the token count of that section alone, not the cumulative total. Estimates should be rounded to nearest 100 tokens for simplicity.

2. **Skip-safety statement is required:** The blockquote must explicitly state the safety/risk profile of skipping the section. Examples:
   - "Safe to skip if you only need API reference" (truly optional)
   - "Safe to skip for basic usage, recommended for advanced customization" (conditionally optional)
   - "Critical context if using feature X, safe to skip otherwise" (context-dependent)

3. **Optional sections must be self-contained:** A section marked optional must not be referenced by mandatory sections. Cross-references to optional sections in mandatory content are allowed but should include fallback text ("see Optional: X if available" or "X is documented in the optional Historical Context section").

4. **Diagnostic I006 activation:** Files with unadorned "Optional" headings (without the blockquote annotation) trigger I006. A tool can auto-generate the blockquote template if token estimates are available.

## Related Decisions

- **DS-DD-013** (Token Budget Tiers): Token budget tiers interact directly with optional section marking. A file targeting the Standard tier (3K tokens) may aggressively mark sections optional, while a Comprehensive tier file (12K) may have fewer optional sections. The optional marking pattern enables this flexibility.

- **DS-DD-010** (Master Index as Navigation Priority): The Master Index section is never optional — it is the navigation backbone. This decision constrains which sections can be marked optional.

- **DS-DD-003** (GFM as Standard): Optional section headings follow GFM heading syntax; the "Optional:" prefix is semantic markup, not a heading level change.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.3 |
