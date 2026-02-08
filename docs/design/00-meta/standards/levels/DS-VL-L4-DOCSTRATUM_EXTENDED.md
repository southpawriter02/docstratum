# DS-VL-L4: DocStratum Extended

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VL-L4 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Level Number** | 4 |
| **Level Name** | DocStratum Extended |
| **Enum Value** | `ValidationLevel.L4_DOCSTRATUM_EXTENDED` |
| **Question Answered** | "Does this file include advanced LLM-optimization features?" |
| **Provenance** | v0.0.6 §3.5 (L4 DocStratum Extended Checks); v0.0.4d DocStratum enrichment; v0.0.0 Stripe Pattern; v0.0.1b Gap Analysis; v0.0.4c anti-pattern catalog |

## Description

Level 4 is the highest tier of the validation pipeline. It evaluates features that go beyond the llms.txt specification to optimize documentation specifically for LLM consumption. After L3 confirms adherence to best practices, L4 asks: has this file been intentionally designed for AI agents? Does it include LLM-specific instructions? Are domain concepts defined in-context? Are few-shot examples provided for common tasks? Is the content free from anti-patterns that degrade LLM performance?

L4 criteria represent the "DocStratum enrichment layer" — features inspired by the Stripe llms.txt pattern (v0.0.0) and validated through gap analysis (v0.0.1b). These are not part of the base llms.txt specification; they are DocStratum's value-add for projects that want to maximize AI agent effectiveness.

All L4 criteria operate within the **Anti-Pattern Detection dimension** (20 points) and use **SOFT** pass types. This reflects the aspirational nature of L4: these features are recommended for best-in-class documentation but are not required for the file to be useful. Files without L4 features can still achieve STRONG grades (70–89 points) through excellent L1–L3 compliance.

## Criteria at This Level

| DS Identifier | Platinum ID | Name | Weight | Dimension | Pass Type |
|---------------|-------------|------|--------|-----------|-----------|
| DS-VC-APD-001 | L4-01 | LLM Instructions Section | 3/20 | Anti-Pattern Detection | SOFT |
| DS-VC-APD-002 | L4-02 | Concept Definitions | 3/20 | Anti-Pattern Detection | SOFT |
| DS-VC-APD-003 | L4-03 | Few-Shot Examples | 3/20 | Anti-Pattern Detection | SOFT |
| DS-VC-APD-004 | L4-04 | No Content Anti-Patterns | 3/20 | Anti-Pattern Detection | SOFT |
| DS-VC-APD-005 | L4-05 | No Strategic Anti-Patterns | 2/20 | Anti-Pattern Detection | SOFT |
| DS-VC-APD-006 | L4-06 | Token-Optimized Structure | 2/20 | Anti-Pattern Detection | SOFT |
| DS-VC-APD-007 | L4-07 | Relative URL Minimization | 2/20 | Anti-Pattern Detection | SOFT |
| DS-VC-APD-008 | L4-08 | Jargon Defined or Linked | 2/20 | Anti-Pattern Detection | SOFT |

**Weight total at this level:** 20 of 20 anti-pattern detection points (the entire APD dimension is assessed at L4).

**Pass Type breakdown:** 0 HARD, 8 SOFT. All L4 criteria are soft — they contribute to reaching the EXEMPLARY threshold (90+ points) but no single L4 failure blocks anything. The EXEMPLARY grade requires strong performance across all three dimensions, making L4 the path to top scores.

## Entry Conditions

L3 must be evaluated. All prerequisite levels must be satisfied:

1. L0: File is parseable
2. L1: File has structural skeleton (all HARD criteria pass)
3. L2: Content quality criteria have been evaluated
4. L3: Best practice criteria have been evaluated, HARD gate (no critical anti-patterns) must pass

If the L3 HARD gate fails (critical anti-pattern detected), L4 is not evaluated because the score is already capped at 29.

## Exit Criteria

Because all L4 criteria are SOFT, L4 "exit" is purely score-based. A file achieves L4 when:

1. All prerequisite levels are satisfied (L0–L3 entry conditions met)
2. L4 criteria are evaluated

The EXEMPLARY grade (90+ points) requires high scores across all three dimensions, which practically means most L4 criteria must pass. Gold standard specimens (Svelte at 92, Pydantic at 90, Vercel SDK at 90) achieve EXEMPLARY by satisfying most L4 criteria.

## Diagnostic Codes at This Level

| DS Identifier | Severity | Fires When | Triggering Criterion |
|---------------|----------|------------|---------------------|
| DS-DC-I001 | INFO | No LLM Instructions section found | DS-VC-APD-001 |
| DS-DC-I002 | INFO | No Concept Definitions section found | DS-VC-APD-002 |
| DS-DC-I003 | INFO | No few-shot examples found | DS-VC-APD-003 |
| DS-DC-I004 | INFO | Relative URLs detected (prefer absolute) | DS-VC-APD-007 |
| DS-DC-I007 | INFO | Domain jargon used without definitions | DS-VC-APD-008 |

> **Note:** DS-VC-APD-004 (No Content Anti-Patterns), DS-VC-APD-005 (No Strategic Anti-Patterns), and DS-VC-APD-006 (Token-Optimized Structure) detect anti-pattern presence/absence through the anti-pattern detection system. Their results are reflected in scoring via the anti-pattern dimension rather than individual diagnostic codes.

## Scoring Impact

L4 criteria constitute the entire **Anti-Pattern Detection dimension** (20 points max). This dimension uses a deduction-based model:

- Start with 20 points (full credit assumed)
- Each detected anti-pattern or missing LLM-optimization feature reduces the score proportionally to its weight
- The 20-point maximum means L4 criteria can swing the total score by up to 20 points — enough to move a file from STRONG (70–89) to EXEMPLARY (90+) or vice versa

**The path to EXEMPLARY:** To score 90+, a file typically needs:

- ~28/30 structural points (L1 + L3 structural criteria)
- ~45/50 content points (L2 + L3 content criteria)
- ~17/20 anti-pattern points (L4 criteria)

This means files can tolerate some L4 SOFT failures and still achieve EXEMPLARY, but they need near-perfect L1–L3 compliance to compensate.

## Relationship to Other Levels

```
L0 (Parseable)
  └─► L1 (Structural)
       └─► L2 (Content Quality)
            └─► L3 (Best Practices)
                 └─► L4 (DocStratum Extended) ← YOU ARE HERE
```

L4 is the terminal level. It represents the highest aspirational standard for llms.txt documentation. Files that achieve strong L4 scores (most criteria passing) earn the EXEMPLARY grade and serve as reference implementations for the DocStratum documentation philosophy: documentation is not just for humans, it is a first-class interface for AI agents.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.1 |
