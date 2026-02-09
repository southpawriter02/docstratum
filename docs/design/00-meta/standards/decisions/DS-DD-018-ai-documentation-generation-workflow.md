# DS-DD-018: AI Documentation Generation Workflow for llms.txt Files

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DD-018 |
| **Status** | DRAFT |
| **ASoT Version** | 1.1.0-scaffold |
| **Decision ID** | DECISION-018 |
| **Date Decided** | 2026-02-08 (v1.1.0) |
| **Impact Area** | End-user llms.txt documentation — governs how AI agents generate documentation files that the DocStratum validation pipeline will score |
| **Provenance** | DS-DD-002 (Three-Layer Architecture); DS-DD-014 (Content Quality Primary Weight); all 30 VC criteria; all 28 AP definitions; calibration specimen analysis (DS-CS-001 through DS-CS-006) |

## Decision

**AI agents generating end-user llms.txt documentation must follow a quality-aware five-phase workflow: (1) pre-generation assessment, (2) structural scaffolding using canonical sections, (3) content generation mapped to VC criteria, (4) anti-pattern self-audit, and (5) iterative refinement against quality gate targets. The minimum acceptable grade for AI-generated documentation is STRONG (≥70/100), with per-dimension floors of 25/30 Structural, 35/50 Content, and 15/20 Anti-Pattern Detection.**

## Context

The DocStratum validation pipeline scores llms.txt files across three dimensions (Structural 30%, Content 50%, Anti-Pattern Detection 20%) using 30 validation criteria. AI agents generating these files have access to the complete scoring rubric — an advantage human authors lack. This workflow leverages that advantage by mapping generation steps directly to the criteria that will evaluate them.

The calibration specimens (DS-CS-001 through DS-CS-006) provide concrete benchmarks:

| Specimen | Score | Grade | Key Characteristics |
|----------|-------|-------|---------------------|
| Svelte | 92 | EXEMPLARY | Rich examples, strong Master Index, canonical sections |
| Pydantic | 90 | EXEMPLARY | Comprehensive API coverage, concept definitions |
| NVIDIA | 24 | CRITICAL | Structure Chaos, Link Void — shows what to avoid |
| FastAPI | 78 | STRONG | Good structure, moderate content depth |
| LangChain | 65 | ADEQUATE | Structural issues, content gaps |
| Anthropic (Claude) | 85 | STRONG | Clean structure, strong LLM instructions section |

The top-scoring specimens share common patterns: they use canonical section names (DS-CN-001 through DS-CN-011), include explicit LLM instructions (DS-VC-APD-001), provide code examples (DS-VC-CON-010), and maintain a navigable Master Index (DS-VC-CON-009). The workflow encodes these patterns as systematic generation steps.

## Alternatives Considered

| Option | Rationale For | Rationale Against |
|--------|---------------|-------------------|
| **Freeform generation** | Maximum creative freedom; AI can adapt to any project's documentation style; no overhead | Ignores the scoring rubric entirely; produces inconsistent quality; likely to trigger multiple anti-patterns; no systematic way to ensure the generated file will score above a threshold |
| **Template-fill generation** | Guarantees structural compliance; every section is pre-defined; fastest generation | Produces formulaic documentation that scores well on structure but poorly on content; violates the spirit of DS-DD-014 (Content Quality Primary Weight); results in Formulaic Description anti-pattern (DS-AP-CONT-007) |
| **Quality-aware generation (Chosen)** | Maps generation steps to VC criteria; anti-pattern avoidance is built into the process; targets a specific quality grade; iterative refinement catches gaps before delivery | More complex than freeform; requires familiarity with all 30 VC criteria; refinement loop adds time; dimension floor targets may need adjustment based on project domain |

## Rationale

Quality-aware generation was selected because it transforms the validation pipeline's scoring rubric from a post-hoc evaluation tool into a pre-generation specification. Instead of writing documentation and then discovering its flaws, the AI agent writes documentation that is designed to satisfy each criterion from the start.

The calibration specimens prove this is achievable: Svelte (92) and Pydantic (90) demonstrate that human-authored documentation can reach EXEMPLARY grade. AI agents, with systematic access to the scoring rubric, should consistently produce STRONG (≥70) grade documentation.

The per-dimension floors (Structural ≥25/30, Content ≥35/50, APD ≥15/20) ensure balanced quality. A file that scores 30/30 on structure but 25/50 on content (total 65, ADEQUATE) is worse than one scoring 25/30 on structure and 40/50 on content (total 75, STRONG) — content matters more per DS-DD-014.

## Impact on ASoT

### The Five-Phase Generation Workflow

#### Phase 1: Pre-Generation Assessment

Before writing any documentation, establish the generation context:

1. **Identify the target project**: What software/library/framework is being documented? What is its primary use case?
2. **Inventory source material**: What documentation already exists? (README, API docs, tutorials, changelogs, code comments)
3. **Determine target grade**: Default is STRONG (≥70). For flagship projects or critical documentation, target EXEMPLARY (≥90).
4. **Identify the audience**: Who will consume this llms.txt? (LLM agents, developers, both)
5. **Assess token budget**: Estimate the target file size against DS-DD-013 token budget tiers.

**Output**: A mental model (or written brief) of what the final document should contain and who it serves.

#### Phase 2: Structural Scaffolding

Build the structural skeleton using canonical sections, targeting full Structural dimension compliance:

**Step 2.1 — H1 Title** (DS-VC-STR-001, 5 pts, HARD):
```markdown
# {Project Name}
```
One and only one H1. Must match the project's canonical name.

**Step 2.2 — Blockquote Description** (DS-VC-STR-003, 3 pts, SOFT):
```markdown
> {One-paragraph summary of the project, its purpose, and its primary audience.}
```

**Step 2.3 — H2 Section Structure** (DS-VC-STR-004, 4 pts, HARD):
Build sections using canonical names from DS-CN-001 through DS-CN-011:

```markdown
## Master Index
## LLM Instructions
## Getting Started
## Core Concepts
## API Reference
## Examples
## Configuration
## Advanced Topics
## Troubleshooting
## FAQ
## Optional
```

Not all sections are required for every project. Include sections that are relevant to the target project and audience. At minimum, include: Master Index (DS-CN-001), one content section, and optionally LLM Instructions (DS-CN-002).

**Step 2.4 — Link Format Compliance** (DS-VC-STR-005, 4 pts, HARD):
All links use valid Markdown format: `[display text](URL)`

**Step 2.5 — Heading Hierarchy** (DS-VC-STR-006, 3 pts, SOFT):
No heading level violations. H2 follows H1, H3 follows H2. No skipping levels.

**Step 2.6 — Uniqueness Checks** (DS-VC-STR-002, 3 pts, HARD):
Verify: exactly one H1, no duplicate H2 section names.

**Structural dimension target**: ≥25/30 (allows for minor SOFT criteria imperfections).

#### Phase 3: Content Generation

Fill in the structural skeleton with substantive content, targeting Content dimension compliance. Map each content section to the relevant VC criteria:

**High-value criteria (5 pts each — prioritize these):**

| Criterion | Section | Generation Guidance |
|-----------|---------|---------------------|
| DS-VC-CON-008 (Canonical Section Names) | All sections | Use exact canonical names from DS-CN-001–011; avoid synonyms |
| DS-VC-CON-009 (Master Index Present) | Master Index | Comprehensive index of all URLs, content types, and freshness dates; this is the single strongest quality predictor |
| DS-VC-CON-010 (Code Examples Present) | Examples, API Reference | Include runnable code examples; code examples (r ≈ 0.65) are the strongest single quality predictor |

**Medium-value criteria (3–4 pts each):**

| Criterion | Section | Generation Guidance |
|-----------|---------|---------------------|
| DS-VC-CON-001 (Non-Empty Descriptions) | All sections | ≥50% of sections must have substantive text (not just links or headings) |
| DS-VC-CON-002 (Substantive Blockquote) | H1 blockquote | ≥2 sentences describing the project's purpose and audience |
| DS-VC-CON-003 (Internal Consistency) | All sections | Section names in body match H2 headings; no orphaned references |
| DS-VC-CON-004 (URL Reachability) | Master Index, all links | All URLs should be verifiable; do not invent URLs |
| DS-VC-CON-005 (Freshness Signals) | Master Index | Include dates, version numbers, or other freshness indicators |
| DS-VC-CON-006 (Audience Relevance) | LLM Instructions | Explicitly address the target audience |
| DS-VC-CON-007 (Section Depth) | Core Concepts, API Reference | Each section should have substantive content, not just stubs |
| DS-VC-CON-011 (Cross-References) | All sections | Link between related sections; avoid Link Desert (DS-AP-CONT-004) |
| DS-VC-CON-012 (Concept Definitions) | Core Concepts | Define key terms on first use |
| DS-VC-CON-013 (Version Information) | FAQ, Master Index | Include version-specific context |

**Content dimension target**: ≥35/50 (STRONG grade contribution).

#### Phase 4: Anti-Pattern Self-Audit

Before finalizing, systematically check for all 28 anti-patterns. The most common AI-generated documentation anti-patterns are:

**Critical — must not trigger (score capped at 29):**

| Anti-Pattern | What AI Agents Commonly Get Wrong |
|---|---|
| DS-AP-CRIT-001 (Ghost File) | Generating a structural skeleton with no actual content |
| DS-AP-CRIT-002 (Structure Chaos) | Markdown syntax errors, missing headings |
| DS-AP-CRIT-004 (Link Void) | Generating placeholder URLs that don't resolve |

**Content — most frequent in AI output:**

| Anti-Pattern | What AI Agents Commonly Get Wrong |
|---|---|
| DS-AP-CONT-007 (Formulaic Description) | Generic, template-like descriptions that could apply to any project |
| DS-AP-CONT-008 (Silent Agent) | Forgetting to include LLM Instructions section |
| DS-AP-CONT-006 (Example Void) | Describing APIs without code examples |
| DS-AP-CONT-001 (Copy-Paste Plague) | Repeating the same phrasing across multiple sections |
| DS-AP-CONT-003 (Jargon Jungle) | Using technical terms without defining them |

**Strategic — process-level risks:**

| Anti-Pattern | What AI Agents Commonly Get Wrong |
|---|---|
| DS-AP-STRAT-001 (Automation Obsession) | Over-relying on generated content without human review |
| DS-AP-STRAT-003 (Meta-Documentation Spiral) | Documenting the documentation process instead of the project |

**Self-audit checklist:**
- [ ] File has substantive content (not just headings and links) — no Ghost File
- [ ] All links use valid Markdown syntax and point to real URLs — no Link Void
- [ ] Descriptions are project-specific, not generic — no Formulaic Description
- [ ] LLM Instructions section is present (if targeting STRONG+) — no Silent Agent
- [ ] Code examples are included for API sections — no Example Void
- [ ] No large blocks of repeated text — no Copy-Paste Plague
- [ ] Technical terms are defined on first use — no Jargon Jungle
- [ ] Section names use canonical names — no Naming Nebula (DS-AP-STRUCT-005)

#### Phase 5: Iterative Refinement

If the self-audit reveals quality gaps, refine iteratively:

```
┌──────────────────────────────────┐
│ Generate / Refine                │
└──────────────┬───────────────────┘
               ▼
┌──────────────────────────────────┐
│ Self-score against 30 VC criteria│
│ (estimate per-dimension scores)  │
└──────────────┬───────────────────┘
               ▼
┌──────────────────────────────────┐
│ Score ≥ target grade?            │
│   YES → Deliver                  │
│   NO  → Identify weakest         │
│         dimension → Refine       │
└──────────────────────────────────┘
```

**Refinement priority** (highest impact per effort):
1. Add Master Index if missing (CON-009: +5 pts)
2. Add code examples if missing (CON-010: +5 pts)
3. Add LLM Instructions section if missing (APD-001: prevents Silent Agent)
4. Use canonical section names (CON-008: +5 pts)
5. Add substantive descriptions to stub sections (CON-001: +5 pts)

**Quality gate targets (minimum for delivery):**

| Dimension | Floor | Ceiling | Target (STRONG) |
|-----------|-------|---------|-----------------|
| Structural | 25/30 | 30/30 | 27/30 |
| Content | 35/50 | 50/50 | 40/50 |
| Anti-Pattern | 15/20 | 20/20 | 17/20 |
| **Total** | **75** | **100** | **84** |

## Constraints Imposed

1. **Minimum grade is STRONG (≥70)**: AI-generated documentation that scores below STRONG should not be delivered without explicit human approval and documented rationale for the lower grade.

2. **Per-dimension floors are enforced**: A file scoring 30/30 Structural but 20/50 Content (total 60, ADEQUATE) fails the Content floor (35/50) and must be refined, even though the total score might be acceptable for some use cases.

3. **No fabricated URLs**: AI agents must not invent URLs. If the actual URL is unknown, use a placeholder format: `[Section Name](https://example.com/placeholder)` and note it requires human verification.

4. **LLM Instructions section is strongly recommended**: For any documentation targeting STRONG grade or above, include the LLM Instructions section (DS-CN-002). This directly addresses the Silent Agent anti-pattern (DS-AP-CONT-008) and is a key differentiator in calibration specimen scoring.

5. **Self-audit is not optional**: Phase 4 (anti-pattern self-audit) must be performed before delivery. The checklist is the minimum; thorough audits may check all 28 anti-patterns.

6. **Human review before publication**: AI-generated documentation should be reviewed by a human before being published or served to downstream consumers. This addresses the Automation Obsession anti-pattern (DS-AP-STRAT-001).

## Related Decisions

- **DS-DD-017** (AI Authoring Workflow for ASoT Standards): The parallel workflow for extending the ASoT library itself (authoring new DS-* files)
- **DS-DD-019** (Guided Flexibility Authoring Model): The compliance tier model that underpins both workflows
- **DS-DD-002** (Three-Layer Architecture): Master Index / Concept Map / Few-Shot Bank — the structural model for llms.txt files
- **DS-DD-010** (Master Index Priority): Why the Master Index is the highest-value section
- **DS-DD-012** (Canonical Section Names): The 11 canonical section names used in Phase 2 scaffolding
- **DS-DD-013** (Token Budget Tiers): File size constraints for generated documentation
- **DS-DD-014** (Content Quality Primary Weight): Why Content dimension (50%) outweighs Structure (30%) — content quality is the priority
- **DS-DD-015** (MCP as Target Consumer): The end consumer of generated documentation is an LLM agent via MCP

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 1.1.0-scaffold | 2026-02-08 | Initial draft — Phase F (AI Authoring Guidelines) |
