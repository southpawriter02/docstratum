# DS-DD-013: Token Budget Tiers as First-Class Constraint

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DD-013 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Decision ID** | DECISION-013 |
| **Date Decided** | 2026-02-05 (v0.0.4d) |
| **Impact Area** | Validation Criteria (DS-VC-CON-012 Token Budget Respected), Constants (`constants.py` → `TOKEN_BUDGET_TIERS`, `SizeTier` enum), Quality Scoring (DS-QS-DIM-CON Content Dimension) |
| **Provenance** | v0.0.4a token distribution analysis; v0.0.1 curated-vs-raw comparison study; v0.0.2c ecosystem audit |

## Decision

**Token budgets are enforced as a first-class constraint through a three-tier system with per-section allocations, not as advisory guidelines or soft suggestions. The tiers are Standard (~3K tokens), Comprehensive (~12K tokens), and Full (~40K tokens), mapped to the three consumption patterns observed in gold standard files and validated against real-world usage data.**

## Context

During v0.0.4a research on file size distributions and token consumption patterns, the team quantified critical facts about the llms.txt ecosystem:

1. **Bimodal size distribution (v0.0.4a §2.1):** Projects fall into two distinct categories:
   - Type 1 (tight scope): 1.1–225 KB, serving focused tools (CLI, single-service APIs)
   - Type 2 (broad scope): 1.3–25 MB, serving complex platforms (monorepo frameworks, enterprise tooling)

2. **Quality is inversely correlated with raw size (v0.0.1):** In a head-to-head comparison, 8K of carefully curated, well-structured tokens consistently outperformed 200K of raw unfiltered content when consumed by LLM agents. The Cloudflare file (3.7M tokens) exists as a counter-example of "bigger is not better."

3. **No size governance in the wild (v0.0.2c):** The 450-project audit revealed that virtually no projects have explicit size budgets. Files grow organically without constraint, resulting in bloated documentation that agents struggle to process efficiently.

4. **Three distinct consumption patterns (v0.0.4a §4.1):** Gold standard files cluster around three size targets:
   - Pattern 1 (Getting Started focus): ~3K tokens
   - Pattern 2 (Reference + Getting Started): ~12K tokens
   - Pattern 3 (Exhaustive): ~40K tokens

The research showed these patterns map to real consumption strategies: agents with limited context choose Pattern 1, agents with moderate context choose Pattern 2, and agents with full context budgets choose Pattern 3.

## Alternatives Considered

| Option | Rationale For | Rationale Against |
|--------|---------------|-------------------|
| Advisory guidelines only (no enforcement) | Least restrictive, maximum creator freedom, no overhead | v0.0.2 audit shows zero specimens self-govern; the 3.7M-token Cloudflare file is the inevitable result; creators lack incentives; advisory guidelines are ignored in practice |
| Hard per-file token caps (e.g., max 40K tokens period) | Simple to understand, easy to enforce, prevents egregious violations | Too rigid; a 200-endpoint API legitimately needs more tokens than a CLI tool; one-size-fits-all caps ignore legitimate variation in scope; discourages ambitious but well-managed documentation |
| Tiered budgets with per-section allocations (CHOSEN) | Maps to three observed consumption patterns, per-section allocations prevent any single section from dominating and bloating the file, authors self-select tier based on project scope, flexibility accommodates legitimate variation while enforcing discipline | Requires authors to declare tier and respect allocations; adds overhead to the authoring process; tier selection can be ambiguous for mid-range projects; per-section allocations require prior planning |

## Rationale

The chosen option was selected based on converging evidence from multiple studies:

1. **Pattern validation:** Svelte's multi-tier documentation variants (small/medium/full modes) validate that three tiers is the natural granularity for different consumption strategies. Svelte scores highest (92) on the ASoT because it explicitly manages scope across three variants; this decision formalizes that pattern.

2. **Per-section allocations prevent section creep:** Without per-section budgets, authors can bloat any single section without realizing the cumulative impact on file size. With allocations (e.g., "Getting Started: max 1500 tokens", "API Reference: max 4000 tokens"), authors make visible trade-offs when editing.

3. **Tier selection is self-governing:** Projects naturally fit into tiers:
   - **Standard (3K):** CLI tools, simple libraries, single-service APIs
   - **Comprehensive (12K):** Multi-service platforms, moderate API surfaces, projects needing both getting started + reference
   - **Full (40K):** Monorepo frameworks, enterprise platforms, projects with 100+ endpoints, extensive configuration

   Selecting a tier is a one-time decision that reflects project scope.

4. **Empirical allocation targets (from v0.0.4a §4.2):**
   - **Standard tier allocation:**
     - Getting Started: 1500 tokens
     - API Reference: 1000 tokens
     - Concepts: 500 tokens

   - **Comprehensive tier allocation:**
     - Getting Started: 3000 tokens
     - API Reference: 4000 tokens
     - Configuration: 2000 tokens
     - Examples: 2000 tokens
     - Advanced Topics: 1000 tokens

   - **Full tier allocation:**
     - Getting Started: 4000 tokens
     - API Reference: 10000 tokens
     - Architecture: 5000 tokens
     - Configuration: 5000 tokens
     - Examples: 5000 tokens
     - Advanced Topics: 3000 tokens
     - Troubleshooting: 3000 tokens
     - Contributing: 2000 tokens
     - Concepts: 2000 tokens

These allocations are derived from the gold standard analysis and can be adjusted empirically.

## Impact on ASoT

This decision directly determines:

- **DS-VC-CON-012** (Token Budget Respected): Validates that the file declares a tier (`SizeTier` in metadata), and that the token count of each section remains within its allocated budget. Diagnostic output specifies which sections are over budget and by how much.

- **`TOKEN_BUDGET_TIERS` constant:** Defined in `constants.py`, mapping tier names to per-section token allocations and cumulative totals.

- **`SizeTier` enum:** Defined in `constants.py` with three members:
  ```python
  class SizeTier(Enum):
      STANDARD = "standard"      # ~3K tokens
      COMPREHENSIVE = "comprehensive"  # ~12K tokens
      FULL = "full"              # ~40K tokens
  ```

- **Quality scoring interaction (DS-DD-014):** Files that exceed their tier budget receive a content dimension score penalty [CALIBRATION-NEEDED: define penalty magnitude]. The penalty is proportional to overage: 10% overage = 5-point deduction, 20% overage = 10-point deduction, etc.

- **Anti-pattern AP-STRAT-002 (Monolith Monster):** Triggered when a file exceeds 100K tokens regardless of declared tier. This is a structural issue indicating the documentation is too large to manage effectively.

## Constraints Imposed

1. **Tier declaration is mandatory:** llms.txt metadata must include a `tier` field with one of the three enum values. Files without declared tier trigger validation error.

2. **Section allocations are guidelines with soft enforcement:** If a section exceeds its allocation by 1–10%, the file is still valid but scores lower in the content dimension. If a section exceeds by >10%, it's flagged as a diagnostic warning and the quality penalty increases.

3. **Per-section allocations can be overridden by authors:** An author can annotate a section with `<!-- @token-budget: 2500 -->` to increase that section's budget locally. This override is recorded in metadata and visible to validators and consumers.

4. **Tier selection is not immutable:** Authors can change their tier (e.g., from Standard to Comprehensive if scope expands), but each change is recorded in the change history. Frequent tier changes (>3 per year) are flagged as an anti-pattern suggesting poor scope management.

5. **Token counting methodology:** Tokens are counted using a configurable tokenizer (default: OpenAI's `cl100k_base` from tiktoken). Validation tools must specify which tokenizer was used. Different tokenizers may produce different counts [CALIBRATION-NEEDED: define tolerance for tokenizer variance].

## Related Decisions

- **DS-DD-011** (Optional Sections Explicitly Marked): Optional section marking interacts directly with token budgets. Optional sections are included in per-section allocations but are explicitly skippable, allowing agents to stay within their context window by omitting optional content.

- **DS-DD-014** (Content Quality Weights): Content dimension scoring (50 points) is where token budget violations are penalized. Files within budget score higher on content dimension.

- **DS-DD-010** (Master Index as Navigation Priority): The Master Index section size is not budgeted separately; it's carved out of the Getting Started or Architecture allocation depending on file structure.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.3 |
