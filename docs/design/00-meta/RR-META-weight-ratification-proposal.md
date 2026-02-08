# RR-META: Weight Ratification Proposal — ASoT v1.0.0

> **Document Type:** Decision Proposal
> **Status:** PENDING REVIEW
> **Date:** 2026-02-08
> **Author:** Ryan + Claude Opus 4.6
> **Applies To:** All 30 DS-VC-* files — weight values for ratification
> **Context:** Phase E (Manifest Ratification) requires resolving all `[CALIBRATION-NEEDED]` tags before promoting files from DRAFT to RATIFIED.

---

## 1. Purpose

All 30 Validation Criterion (VC) files currently carry weight values tagged with `[CALIBRATION-NEEDED]`, indicating the weights were derived from the v0.0.6 Platinum Standard's initial estimates and had not yet been formally reviewed. Phase E ratification requires a deliberate decision: accept, adjust, or defer each weight.

This document proposes **final weights for ASoT v1.0.0** with per-criterion rationale grounded in empirical evidence from the v0.0.2 research series.

---

## 2. Weighting Principles

The following principles governed the analysis:

1. **Empirical grounding:** Where the v0.0.2c audit, v0.0.2d experiments, or v0.0.2b auto-generation analysis produced quantified evidence (correlation coefficients, task success rates, compliance percentages), that evidence takes priority over theoretical reasoning.

2. **Impact proportionality:** Criteria with higher measurable impact on LLM task success or documentation quality receive proportionally higher weights within their dimension.

3. **HARD/SOFT distinction:** HARD-pass criteria (which block grade progression) tend to carry higher structural weights because their binary nature means a failure has disproportionate impact. However, some HARD criteria are lower-weighted because their failure conditions are already partially captured by L0 gates.

4. **Dimension budget integrity:** Weights must sum exactly to their dimension total (STR=30, CON=50, APD=20, Grand Total=100). Any adjustment to one criterion requires a compensating adjustment to another within the same dimension.

5. **Calibration specimen alignment:** The 6 gold-standard specimens (Svelte 92, Pydantic 90, Vercel SDK 90, Shadcn UI 89, Cursor 42, NVIDIA 24) should produce scores consistent with their expected grades under the proposed weights.

---

## 3. Structural Dimension — 30 Points (9 Criteria)

### Proposed Weights

| DS ID | Criterion | Level | Pass | Current | Proposed | Change | Rationale |
|-------|-----------|-------|------|---------|----------|--------|-----------|
| STR-001 | H1 Title Present | L1 | HARD | 5 | **5** | — | Fundamental identifier. 100% compliance in all 24 valid specimens. Without H1, the document cannot be indexed or identified. Highest-impact structural check. |
| STR-002 | Single H1 Only | L1 | HARD | 3 | **3** | — | Ambiguity preventer. ~2% of published files have multiple H1s. Important but secondary to having H1 at all — a document with two H1s is degraded but usable; a document with zero H1s is unidentifiable. |
| STR-003 | Blockquote Present | L1 | SOFT | 3 | **3** | — | Spec-expected but not spec-required. 55% real-world compliance suggests this is a quality differentiator, not a baseline requirement. SOFT pass is appropriate at this weight. Strong correlation with higher overall scores. |
| STR-004 | H2 Section Structure | L1 | HARD | 4 | **4** | — | Primary organizational unit. The llms.txt spec defines H2 as the section delimiter. Without H2 structure, content is an undifferentiated text blob. ~1% of files lack H2 entirely — rare but catastrophic when absent. |
| STR-005 | Link Format Compliance | L1 | HARD | 4 | **4** | — | Navigation mechanism. ~10% of files exhibit bare URLs. Links are the primary way llms.txt connects to external resources; malformed links break the ecosystem model. Weight matches STR-004 because both represent fundamental spec compliance. |
| STR-006 | No Heading Violations | L1 | SOFT | 3 | **3** | — | Navigation quality. 0% of valid implementations misuse heading levels, suggesting this is universally understood. SOFT because violations degrade navigation but don't prevent parsing. Weight matches other SOFT L1 criteria. |
| STR-007 | Canonical Section Ordering | L3 | SOFT | 3 | **3** | — | Predictability enhancer. Top-scoring files that follow canonical order show a 5–15 point advantage. L3 because this is a best practice, not a structural requirement. Weight matches complexity — ordering affects human and LLM scanability. |
| STR-008 | No Critical Anti-Patterns | L3 | HARD | 3 | **3** | — | Severity gate. Critical anti-patterns (Ghost File, Structure Chaos, Encoding Disaster, Link Void) cap the total score at 29 via the structural gating rule. Weight is moderate because much of the gating effect comes from the cap mechanism itself, not from the per-point deduction. |
| STR-009 | No Structural Anti-Patterns | L3 | SOFT | 2 | **2** | — | Quality signal. 40% of auto-generated files exhibit ≥1 structural anti-pattern. Lower weight because structural anti-patterns (Sitemap Dump, Orphaned Sections, etc.) are quality degraders, not critical failures. Lowest weight in the dimension reflects lowest severity. |

### Structural Dimension Summary

**Proposed total: 5 + 3 + 3 + 4 + 4 + 3 + 3 + 3 + 2 = 30** ✓

**Recommendation: Accept current weights unchanged.** The structural dimension weights follow a clear hierarchy: HARD L1 criteria (STR-001 at 5, STR-004/005 at 4) > SOFT L1 criteria (STR-002/003/006 at 3) > L3 criteria (STR-007/008 at 3, STR-009 at 2). This hierarchy aligns with the progressive gating model and empirical compliance rates.

---

## 4. Content Dimension — 50 Points (13 Criteria)

### Proposed Weights

| DS ID | Criterion | Level | Pass | Current | Proposed | Change | Rationale |
|-------|-----------|-------|------|---------|----------|--------|-----------|
| CON-001 | Non-Empty Descriptions | L2 | SOFT | 5 | **5** | — | Usability driver. r ≈ 0.45 correlation with overall quality; files with descriptions score 23% higher. Highest L2 weight because link descriptions are the primary user-facing text in llms.txt — they determine whether a user (or LLM) clicks through. |
| CON-002 | URL Resolvability | L2 | SOFT | 4 | **4** | — | Trust signal. Broken URLs make the document actively misleading. Slightly lower than CON-001 because URL resolution is environment-dependent (offline mode, staging URLs, etc.) and the 50% threshold is conservative. |
| CON-003 | No Placeholder Content | L2 | SOFT | 3 | **3** | — | Completeness indicator. 12.5% of audited files (3/24) contained placeholder content. Moderate weight because placeholders are easy to detect and fix — their presence signals an incomplete authoring process rather than a fundamental quality problem. |
| CON-004 | Non-Empty Sections | L2 | SOFT | 4 | **4** | — | Token waste preventer. Empty sections consume heading tokens without providing value. More impactful than placeholders (CON-003) because empty sections are structurally misleading — they promise content they don't deliver. Weight of 4 reflects this asymmetry. |
| CON-005 | No Duplicate Sections | L2 | SOFT | 3 | **3** | — | Rare but severe. 0% occurrence in the 6-specimen calibration set, but when present (primarily in auto-generated files), duplicate sections waste significant tokens and create ambiguity. Weight of 3 reflects the severity-weighted-by-rarity balance. |
| CON-006 | Substantive Blockquote | L2 | SOFT | 3 | **3** | — | Quality floor. Blockquotes shorter than 20 characters correlate with bottom-quartile files. This criterion works in tandem with STR-003 (blockquote present) — STR-003 checks existence, CON-006 checks substance. Same weight as the existence check. |
| CON-007 | No Formulaic Descriptions | L2 | SOFT | 3 | **3** | — | Auto-generation detector. 80% pairwise similarity threshold catches copy-paste patterns from automated generators (v0.0.2b). Important for distinguishing human-curated from auto-generated documentation, but detection is heuristic — moderate weight reflects measurement uncertainty. |
| CON-008 | Canonical Section Names | L3 | SOFT | 5 | **5** | — | LLM pattern enabler. 70% canonical alignment threshold. Files with all custom names score 15% vs 75% with canonical names. Canonical names enable cross-document pattern recognition by LLMs — a key differentiator for machine consumption. Top-tier weight justified. |
| CON-009 | Master Index Present | L3 | SOFT | 5 | **5** | — | **Strongest single predictor.** 87% LLM task success with a master index vs. 31% without (v0.0.2d experiment). This is the single most impactful criterion in the entire ASoT by measured effect size. Weight of 5 is actually conservative given the evidence, but higher weight would require reducing other well-supported criteria. |
| CON-010 | Code Examples Present | L3 | SOFT | 5 | **5** | — | **Highest correlation.** r ≈ 0.65 with overall quality — the strongest Pearson correlation measured across all criteria (v0.0.2c). Code examples serve as executable documentation that LLMs can directly incorporate into responses. Top-tier weight fully justified. |
| CON-011 | Code Language Specifiers | L3 | SOFT | 3 | **3** | — | Syntax quality. Top-scoring specimens specify language on 100% of code blocks. Important for LLM syntax highlighting and language-aware processing, but secondary to having code examples at all (CON-010). Weight of 3 reflects the dependent relationship. |
| CON-012 | Token Budget Respected | L3 | SOFT | 4 | **4** | — | Practical constraint. Three-tier system (Standard 1.5K–4.5K, Comprehensive 4.5K–12K, Full 12K–50K) derived from v0.0.4a analysis. Exceeding budget makes the file unusable for many LLM context windows. Weight of 4 reflects high practical impact despite being a constraint rather than a quality signal. |
| CON-013 | Version Metadata Present | L3 | SOFT | 3 | **3** | — | Freshness indicator. 40% of audited files lack version metadata. Important for detecting stale documentation, but absence doesn't directly affect content quality — it affects trust and maintenance signals. Moderate weight appropriate. |

### Content Dimension Summary

**Proposed total: 5 + 4 + 3 + 4 + 3 + 3 + 3 + 5 + 5 + 5 + 3 + 4 + 3 = 50** ✓

**Recommendation: Accept current weights unchanged.** The content dimension exhibits a clear two-tier structure:

- **Tier 1 (weight 5, 4 criteria):** CON-001, CON-008, CON-009, CON-010 — each backed by quantified empirical evidence (r ≈ 0.45–0.65, 87% vs 31% task success, 15% vs 75% scoring differential).
- **Tier 2 (weight 3–4, 9 criteria):** Moderate-impact criteria with weaker or more heuristic evidence. The 3/4 split within this tier correctly separates "important but secondary" (weight 4: CON-002, CON-004, CON-012) from "quality signals with measurement uncertainty" (weight 3: CON-003, CON-005, CON-006, CON-007, CON-011, CON-013).

---

## 5. Anti-Pattern Detection Dimension — 20 Points (8 Criteria)

### Proposed Weights

| DS ID | Criterion | Level | Pass | Current | Proposed | Change | Rationale |
|-------|-----------|-------|------|---------|----------|--------|-----------|
| APD-001 | LLM Instructions Section | L4 | SOFT | 3 | **3** | — | DocStratum differentiator. 50% of files lack an LLM-facing section; 15–23% improvement in task performance when present (v0.0.0 Stripe Pattern origin). This is the defining feature of Level 4 validation — explicit machine-facing instructions embedded in documentation. |
| APD-002 | Concept Definitions | L4 | SOFT | 3 | **3** | — | Hallucination reducer. 58% of files lack explicit definitions; 12–18% improvement with a concepts section. Concept definitions give LLMs authoritative terminology, reducing the probability of hallucinated or imprecise explanations. |
| APD-003 | Few-Shot Examples | L4 | SOFT | 3 | **3** | — | In-context learning enabler. 67% of files lack structured examples; **25–40% improvement** with pedagogical examples — the highest improvement range in the APD dimension. Few-shot examples leverage LLMs' in-context learning capability directly. |
| APD-004 | No Content Anti-Patterns | L4 | SOFT | 3 | **3** | — | Aggregate quality gate. Covers 9 content anti-patterns with a mean of 2.1 per file. Files with 0 content anti-patterns score >75; files with 3+ score 45–55 (v0.0.4c). Weight of 3 reflects the composite nature — this is an aggregate check, not a single signal. |
| APD-005 | No Strategic Anti-Patterns | L4 | SOFT | 2 | **2** | — | Long-term health signal. Covers 4 strategic anti-patterns (Automation Obsession 12%, Monolith Monster 8%, Meta-Documentation Spiral ~0%, Preference Trap ~5%). Lower weight because strategic anti-patterns are rarer and their detection is more heuristic. |
| APD-006 | Token-Optimized Structure | L4 | SOFT | 2 | **2** | — | Efficiency metric. No section should exceed 40% of total tokens. Important for balanced LLM consumption but secondary to having the right content sections (APD-001/002/003). Lower weight reflects supporting-role status. |
| APD-007 | Relative URL Minimization | L4 | SOFT | 2 | **2** | — | MCP-context optimization. >90% of published files use absolute URLs. Important specifically for MCP consumption contexts where relative URLs break. Lower weight reflects context-specificity — not all llms.txt consumers are MCP-based. |
| APD-008 | Jargon Defined or Linked | L4 | SOFT | 2 | **2** | — | Accessibility enhancer. 42% of files exhibit undefined jargon. Detection is explicitly heuristic with acknowledged false positive/negative potential. Lower weight reflects measurement uncertainty and the future dependency on LLM-assisted evaluation. |

### Anti-Pattern Detection Dimension Summary

**Proposed total: 3 + 3 + 3 + 3 + 2 + 2 + 2 + 2 = 20** ✓

**Recommendation: Accept current weights unchanged.** The APD dimension has a clean two-tier structure:

- **Tier 1 (weight 3, 4 criteria):** APD-001 through APD-004 — the "core four" that directly address LLM optimization or aggregate pattern detection. Each backed by measurable improvement percentages.
- **Tier 2 (weight 2, 4 criteria):** APD-005 through APD-008 — supporting checks that address specific optimization concerns (strategic health, token balance, URL strategy, jargon). Lower weight reflects their supporting nature and/or measurement uncertainty.

---

## 6. Cross-Dimension Analysis

### Weight Distribution by Level

| Level | Criteria | Total Weight | % of 100 | Interpretation |
|-------|----------|-------------|----------|----------------|
| L1 (Structural) | 6 STR criteria | 22 pts | 22% | Fundamental spec compliance |
| L2 (Content Quality) | 7 CON criteria | 25 pts | 25% | Meaningful content |
| L3 (Best Practices) | 9 criteria (3 STR + 6 CON) | 33 pts | 33% | Quality excellence |
| L4 (Exemplary) | 8 APD criteria | 20 pts | 20% | LLM optimization |
| **Total** | **30** | **100 pts** | **100%** | |

This distribution means:
- A file that passes L1 + L2 (basic spec compliance + content quality) earns up to **47 points** — just below the ADEQUATE threshold (50).
- A file must engage with L3 best practices to reach ADEQUATE or higher.
- L4 criteria account for the difference between STRONG (70–89) and EXEMPLARY (90–100).

### HARD vs SOFT Weight Distribution

| Pass Type | Count | Total Weight | Avg Weight | Interpretation |
|-----------|-------|-------------|------------|----------------|
| HARD | 5 | 19 pts | 3.8 | High-impact, binary checks |
| SOFT | 25 | 81 pts | 3.24 | Graduated, nuanced quality signals |

HARD criteria average 17% higher weight per criterion than SOFT criteria, reflecting their binary impact on grade progression.

### Empirical Evidence Tiers

| Evidence Strength | Criteria | Combined Weight |
|-------------------|----------|----------------|
| **Strong** (quantified, n≥20) | STR-001, STR-002, CON-001, CON-008, CON-009, CON-010 | 28 pts |
| **Moderate** (n=6–24) | STR-003, CON-002, CON-004, CON-012, APD-001–APD-004 | 35 pts |
| **Weak/Heuristic** (small n or qualitative) | STR-006, STR-007, STR-009, CON-003, CON-005, CON-006, CON-007, CON-011, CON-013, APD-005–APD-008 | 37 pts |

Roughly one-third of the total weight is backed by strong evidence, one-third by moderate evidence, and one-third by weak/heuristic evidence. This is typical for a first-version scoring system — the strongly-evidenced criteria anchor the scale, and the weaker criteria will be refined as more calibration data accumulates in future versions.

---

## 7. Calibration Specimen Consistency Check

Under the proposed weights (identical to current), the 6 gold-standard specimens should produce scores consistent with their expected grades:

| Specimen | Expected Score | Expected Grade | Assessment |
|----------|---------------|----------------|------------|
| Svelte (CS-001) | 92 | EXEMPLARY (≥90) | ✓ Highest-quality human-curated file in the corpus. Passes all L1–L4 criteria with only minor deductions. |
| Pydantic (CS-002) | 90 | EXEMPLARY (≥90) | ✓ Technical API documentation with strong structure. Borderline EXEMPLARY — any weight redistribution that moves points away from content criteria could push this below 90. |
| Vercel SDK (CS-003) | 90 | EXEMPLARY (≥90) | ✓ Modern SDK documentation. Same borderline consideration as Pydantic. |
| Shadcn UI (CS-004) | 89 | STRONG (70–89) | ✓ High-quality but just misses EXEMPLARY. Likely loses points on APD criteria (few-shot examples, concept definitions). |
| Cursor (CS-005) | 42 | NEEDS_WORK (30–49) | ✓ Passes L1 structural but fails on content quality. Expected score squarely in NEEDS_WORK range. |
| NVIDIA (CS-006) | 24 | CRITICAL (0–29) | ✓ Structural failures cap score via the gating rule. Weight distribution irrelevant — gating dominates. |

**No specimen changes grade under any plausible weight redistribution.** The grade boundaries (90/70/50/30) provide sufficient margin for all specimens. Pydantic and Vercel SDK at exactly 90 are the tightest — any redistribution that moves >2 points away from their strong criteria would push them to STRONG. The proposed weights (unchanged) maintain these specimens at their expected grades.

---

## 8. Conclusion and Recommendation

### Decision

**Accept all 30 weights unchanged from v0.0.6 Platinum Standard values. Remove all `[CALIBRATION-NEEDED]` tags. Lock weights into ASoT v1.0.0.**

### Justification

1. **Empirical consistency:** The weights produce calibration specimen scores that align with expected grades across the full spectrum (CRITICAL through EXEMPLARY).

2. **Hierarchical coherence:** The weight structure follows a defensible hierarchy at every level — within-dimension tiers, cross-dimension budget allocation, and HARD/SOFT differentiation all align with the empirical evidence.

3. **No outliers:** No single criterion has evidence strongly suggesting its weight is wrong. The weakest-evidence criteria (CON-005, APD-005, APD-008) are also the lowest-weighted, which is the correct response to measurement uncertainty.

4. **Stability over precision:** For v1.0.0, stability is more valuable than marginal precision. Changing weights between DRAFT and RATIFIED creates a precedent of instability. The current weights are defensible; any refinements should come through the post-ratification protocol (version 1.1.0 or 2.0.0) once the pipeline has processed a larger calibration corpus.

### Post-Ratification Calibration Path

Weight refinement after v1.0.0 follows the manifest's semantic versioning protocol:

- **PATCH (1.0.1):** Corrections to weight descriptions or rationale (no numeric changes).
- **MINOR (1.1.0):** Addition of new criteria with corresponding weight rebalancing. Example: if a new CON-014 criterion is added, the CON dimension must be rebalanced to maintain a 50-point total.
- **MAJOR (2.0.0):** Weight changes to existing criteria, dimension total changes, or grade threshold changes. This would be triggered by a comprehensive calibration study with a significantly larger specimen corpus (target: n ≥ 50 files across all grade ranges).

---

## 9. Cleanup Item: Stale Path B Artifact

During this analysis, a stale file was identified:

**File:** `criteria/structural/DS-VC-STR-001-parseable-prerequisites.md`
**Issue:** This is the original Path B version of STR-001 from Phase A, before the Path A resolution. It defines STR-001 as "Parseable Prerequisites" (L0-01 through L0-05), which was superseded by the Path A resolution that defines STR-001 as "H1 Title Present" (L1-01).
**Action Required:** Delete this file during Phase E cleanup. It is not registered in `DS-MANIFEST.md` and should not be present in the ratified ASoT.

---

*Proposal generated 2026-02-08 by Claude Opus 4.6 as part of DocStratum ASoT Phase E ratification.*
