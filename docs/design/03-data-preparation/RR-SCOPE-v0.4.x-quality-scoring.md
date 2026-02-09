# v0.4.x Quality Scoring — Scope Breakdown

> **Version Range:** v0.4.0 through v0.4.2
> **Document Type:** Scope Breakdown (precedes individual design specifications)
> **Status:** DRAFT
> **Created:** 2026-02-09
> **Last Updated:** 2026-02-09
> **Parent:** RR-ROADMAP-validator-v0.0.1-to-v1.0.0.md
> **Research Basis:** v0.0.4b (content best practices & scoring rubric), v0.0.4c (anti-pattern catalog & severity model), v0.0.3b (gold standard calibration)
> **Consumes:** v0.3.x (`ValidationResult`, `ValidationDiagnostic`), v0.1.2a (`DiagnosticCode`, `Severity`), v0.1.2c (`ValidationLevel`), v0.1.2b (`QualityScore`, `QualityGrade`, `DimensionScore`, `QualityDimension`), `constants.py` (`AntiPatternCategory`, `AntiPatternID`, `ANTI_PATTERN_REGISTRY`)
> **Consumed By:** v0.5.x (CLI & Profiles), v0.6.x (Remediation Framework), v0.7.x (Ecosystem Integration), v0.8.x (Report Generation)

---

## 1. Purpose

Phase 4 builds the **quality scoring engine** — the component that reads a `ValidationResult` (produced by v0.3.x) and computes a 100-point composite quality score across three empirically-weighted dimensions. This is where diagnostic findings become a numeric grade, where the DS-QS-GATE gating rule is enforced, and where the file receives its final quality classification (EXEMPLARY through CRITICAL).

The scoring engine transforms the validator's raw findings into a single, comparable metric. The validator (v0.3.x) answers *"What's wrong with this file?"*; the scorer answers *"How good is this file, overall?"* The remediation framework (v0.6.x) will then answer *"What should the author do about it?"*

The composite score is computed from three dimensions with evidence-grounded weighting (DECISION-014):

| Dimension | Max Points | Weight | Role |
|-----------|-----------|--------|------|
| **Structural** (DS-QS-DIM-STR) | 30 | 30% | Gating — necessary but not sufficient |
| **Content** (DS-QS-DIM-CON) | 50 | 50% | Primary driver — strongest quality predictor |
| **Anti-Pattern** (DS-QS-DIM-APD) | 20 | 20% | Differentiator — path from STRONG to EXEMPLARY |

---

## 2. Scope Boundary: What the Scorer IS and IS NOT

### 2.1 The Scorer IS

A **score calculator** that reads the validated diagnostics and anti-pattern metadata from a `ValidationResult`, evaluates 30 validation criteria (DS-VC-STR-001 through STR-009, DS-VC-CON-001 through CON-013, DS-VC-APD-001 through APD-008), aggregates points across three dimensions, applies the DS-QS-GATE gating rule, assigns a letter grade, and populates a `QualityScore` model.

**Input:** A `ValidationResult` instance (from v0.3.x) containing all `ValidationDiagnostic` findings with diagnostic codes, severity levels, and anti-pattern metadata.
**Output:** A `QualityScore` with `total_score` (0–100), `grade` (EXEMPLARY–CRITICAL), `dimensions{}` (per-dimension `DimensionScore` breakdown), and per-check details for drill-down reporting.

### 2.2 The Scorer IS NOT

| Out of Scope | Why | Where It Lives |
|--------------|-----|----------------|
| **Evaluating validation checks** | The scorer reads diagnostic results already emitted by the validator. It does not re-run checks or inspect the `ParsedLlmsTxt` model directly. | v0.3.x (Validation Engine) |
| **Generating remediation guidance** | The scorer says *how good the file is*. The remediation framework says *what to do about it*. Score impact projections ("fixing this would gain +5 points") are a remediation feature, not a scoring feature. | v0.6.x (Remediation Framework) |
| **Formatting output** | The scorer produces a `QualityScore` model. Report generation formats that model into JSON, Markdown, HTML, etc. | v0.8.x (Report Generation) |
| **Ecosystem-level scoring** | The 5-dimension ecosystem health score (Completeness, Coverage, Consistency, Token Efficiency, Freshness) is a separate aggregate computed from multiple per-file scores. | v0.7.x (Ecosystem Integration) |
| **Evaluating L4-dependent criteria directly** | APD-001 (LLM Instructions), APD-002 (Concept Definitions), and APD-003 (Few-Shot Examples) depend on L4 validation which is deferred to v0.9.0. The scorer framework accommodates these criteria but they will score 0 until L4 checks are active. | v0.9.0 (Extended Validation) |
| **Applying validation profiles** | The scorer evaluates ALL 30 criteria. The profile system (v0.5.x) may filter which criteria are active or how results are surfaced. The scorer is profile-unaware. | v0.5.x (CLI & Profiles) |
| **Modifying the ValidationResult** | The scorer reads the validation result. It never mutates it. | Never |

### 2.3 Validation Criteria In Scope vs. Out of Scope

The scoring engine (v0.4.x) evaluates all **30 validation criteria** defined across the three ASoT scoring dimension standards. However, some criteria depend on diagnostic codes or features that are not yet available at v0.4.x:

**Fully Evaluable at v0.4.x (21 criteria):**

| Dimension | Criteria | Count |
|-----------|----------|-------|
| Structural | DS-VC-STR-001 through STR-009 | 9 |
| Content (L2) | DS-VC-CON-001 through CON-007 | 7 |
| Content (L3) | DS-VC-CON-008 through CON-013 | 6 |
| **Total** | | **22** |

> **Correction Note:** All 9 STR criteria and all 13 CON criteria (22 total) are fully evaluable because they map to L0–L3 diagnostic codes that v0.3.x emits. However, some criteria may report 0 points when their prerequisite diagnostic checks were skipped due to gate-on-failure (e.g., if L0 failed, L1–L3 checks were never run, so CON-008 through CON-013 have no data).

**Partially Evaluable at v0.4.x (5 criteria — APD dimension):**

| Criterion | Points | Issue | Workaround |
|-----------|--------|-------|------------|
| DS-VC-APD-001 | 3 | Checks for LLM Instructions (I001) — L4 code, not emitted until v0.9.0 | Score 0 until L4 active |
| DS-VC-APD-002 | 3 | Checks for Concept Definitions (I002) — L4 code | Score 0 until L4 active |
| DS-VC-APD-003 | 3 | Checks for Few-Shot Examples (I003) — L4 code | Score 0 until L4 active |
| DS-VC-APD-004 | 3 | Checks absence of 9 content anti-patterns — 2 depend on L4 (AP-CONT-003, AP-CONT-008) | Partial scoring; 7 of 9 patterns evaluable |
| DS-VC-APD-005 | 2 | Checks absence of 4 strategic anti-patterns — 1 depends on L4 (AP-STRAT-004) | Partial scoring; 3 of 4 patterns evaluable |

**Fully Deferred (4 criteria — evaluate to 0):**

| Criterion | Points | Reason | Deferred To |
|-----------|--------|--------|-------------|
| DS-VC-APD-001 | 3 | LLM Instructions section not validated until L4 | v0.9.0 |
| DS-VC-APD-002 | 3 | Concept Definitions not validated until L4 | v0.9.0 |
| DS-VC-APD-003 | 3 | Few-Shot Examples not validated until L4 | v0.9.0 |
| DS-VC-APD-008 | 2 | Jargon Defined or Linked depends on I007 (L4) | v0.9.0 |

> **Practical Impact:** Until v0.9.0 activates L4 checks, the APD dimension's effective maximum is **9 points out of 20** (APD-004: 3 + APD-005: 2 + APD-006: 2 + APD-007: 2 = 9 points; APD-001, APD-002, APD-003, and APD-008 all score 0 due to L4 dependencies). This means the effective composite maximum is approximately **89 points** (30 + 50 + 9), meaning **EXEMPLARY (≥90) is not achievable until v0.9.0** activates L4 checks. The highest attainable grade at v0.4.x is STRONG. The design spec for v0.4.0d should document this ceiling, and the calibration specimens (v0.4.2c) must account for it.

### 2.4 The Gray Zone: Partial Compliance Scoring

The ASoT scoring dimension standards (DS-QS-DIM-STR, DS-QS-DIM-CON, DS-QS-DIM-APD) all specify that criteria support "partial compliance → proportional points." However, the granularity of partial compliance is not fully defined:

- **Binary criteria** (e.g., STR-001 "H1 Title Present"): Pass = full points, fail = 0 points. No partial state exists.
- **Graduated criteria** (e.g., CON-001 "Non-Empty Link Descriptions"): If 80% of links have descriptions, does the file earn 80% of the 5-point allocation (4 points)? Or is there a threshold (≥90% = full, <90% = 0)?
- **Threshold-based criteria** (e.g., CON-002 "URL Resolvability ≥50%"): The spec defines a threshold. Above the threshold = full points? Or proportional between threshold and 100%?

The design specs for individual dimension scorers (v0.4.0b, v0.4.0c, v0.4.0d) must define the partial compliance formula for each criterion. The scope only requires that partial compliance be supported — it does not prescribe the formula. However, the scorer must produce results that calibrate correctly against the 6 gold standard specimens (v0.4.2c).

### 2.5 The Gray Zone: Skipped-Level Criteria

When gate-on-failure prevents higher levels from running (e.g., L0 fails, so L1–L3 checks are never evaluated), the scorer faces a question: what score do the unevaluated criteria receive?

Two approaches are possible:

1. **Score 0 for unevaluated criteria:** The file earns no points for checks that were never run. Simple, penalizing.
2. **Exclude unevaluated criteria from the denominator:** Adjust `max_points` to reflect only the criteria that were actually evaluated. More nuanced, but risks inflating scores for badly broken files.

The recommended approach is **option 1** (score 0), because:
- A file that fails L0 is fundamentally broken and should score near 0.
- The DS-QS-GATE gating rule already caps the score at 29 for critical failures, making the distinction moot for the most severe cases.
- Option 2 would require dynamic `max_points` adjustments that complicate the scoring model.

The design spec for v0.4.1a should finalize this decision.

---

## 3. Sub-Part Breakdown

### 3.1 v0.4.0 — Dimension Scoring

**Goal:** Implement the three independent dimension scorers. Each scorer reads the `ValidationResult` diagnostics, evaluates its assigned criteria, and produces a `DimensionScore` instance. The three scorers operate independently — no dimension depends on another's result.

---

#### v0.4.0a — Criteria-to-Diagnostic Mapping Registry

**What it does:** Defines the authoritative mapping between the 30 validation criteria (DS-VC-*) and the diagnostic codes / anti-pattern IDs that feed into each criterion's evaluation. This registry is the "lookup table" that the dimension scorers use to determine which diagnostics are relevant to each criterion.

**Why this is a separate sub-part:** Every dimension scorer needs this mapping. Centralizing it avoids duplication and ensures consistency. When new diagnostic codes are added (e.g., L4 codes in v0.9.0), only the registry needs to be updated — the dimension scorers' logic remains unchanged.

**Registry Structure (per criterion):**

| Field | Type | Description |
|-------|------|-------------|
| `criterion_id` | str | DS-VC-STR-001, DS-VC-CON-001, etc. |
| `dimension` | QualityDimension | STRUCTURAL, CONTENT, or ANTI_PATTERN |
| `max_points` | float | Point allocation for this criterion |
| `validation_level` | ValidationLevel | L1, L2, L3, or L4 |
| `pass_type` | str | HARD or SOFT (from ASoT specs) |
| `diagnostic_codes` | list[DiagnosticCode] | Which diagnostic codes affect this criterion |
| `anti_pattern_ids` | list[AntiPatternID] | Which anti-pattern IDs affect this criterion (APD only) |
| `scoring_mode` | str | BINARY, GRADUATED, or THRESHOLD |

**Inputs:**
- DS-QS-DIM-STR (9 structural criteria with point allocations and level assignments)
- DS-QS-DIM-CON (13 content criteria with point allocations and level assignments)
- DS-QS-DIM-APD (8 anti-pattern criteria with point allocations)
- `DiagnosticCode` enum (38 codes — mapping each to its contributing criteria)
- `AntiPatternID` enum (28 patterns — mapping content and strategic patterns to APD-004 and APD-005)

**Output:** A static, importable registry (likely a module-level dictionary or a list of dataclass instances) that all three dimension scorers consume.

**Grounding:** DS-QS-DIM-STR (constituent criteria table), DS-QS-DIM-CON (constituent criteria table), DS-QS-DIM-APD (constituent criteria table), v0.3.x diagnostic code assignments.

---

#### v0.4.0b — Structural Dimension Scorer

**What it does:** Evaluates the 9 structural criteria (DS-VC-STR-001 through STR-009) and produces a `DimensionScore(STRUCTURAL)` with up to 30 points.

**Inputs:**
- `ValidationResult.diagnostics[]` — filtered to structural-relevant codes
- Anti-pattern metadata attached to diagnostics by v0.3.4
- Criteria registry (v0.4.0a)

**Criteria Evaluated:**

| Criterion | Points | Level | Key Diagnostics | Scoring Mode |
|-----------|--------|-------|-----------------|--------------|
| DS-VC-STR-001 | 5 | L1 | E001 (no H1) | BINARY |
| DS-VC-STR-002 | 3 | L1 | E002 (multiple H1) | BINARY |
| DS-VC-STR-003 | 3 | L1 | W001 (missing blockquote) | BINARY |
| DS-VC-STR-004 | 4 | L1 | E005 (invalid Markdown), section count heuristic | GRADUATED |
| DS-VC-STR-005 | 4 | L1 | E006 (broken links, syntactic) | GRADUATED |
| DS-VC-STR-006 | 3 | L1 | Heading nesting violations (heuristic from parsed structure) | GRADUATED |
| DS-VC-STR-007 | 3 | L3 | W008 (section order) | BINARY |
| DS-VC-STR-008 | 3 | L3 | AP-CRIT-001 through AP-CRIT-004 presence | BINARY |
| DS-VC-STR-009 | 2 | L3 | AP-STRUCT-001 through AP-STRUCT-005 presence | GRADUATED |

**Scoring Logic:**
- For each criterion, look up its diagnostic codes from the registry.
- Count how many of the relevant diagnostics were emitted in the `ValidationResult`.
- Apply the criterion's scoring mode (binary: 0 or full points; graduated: proportional points based on compliance rate).
- Sum all criterion points → `DimensionScore.points` (0–30).
- Set `DimensionScore.max_points = 30`.
- Populate `checks_passed`, `checks_failed`, `checks_total` from criterion-level results.

**What this does NOT do:**
- Does not apply the gating rule. DS-QS-GATE is applied at the composite level (v0.4.1b), not within the structural dimension scorer.
- Does not evaluate heading nesting beyond what the validator already detected. If the validator didn't emit a heading violation diagnostic, the scorer cannot independently detect one.

**Grounding:** DS-QS-DIM-STR (full specification), DS-VC-STR-001 through DS-VC-STR-009.

---

#### v0.4.0c — Content Dimension Scorer

**What it does:** Evaluates the 13 content criteria (DS-VC-CON-001 through CON-013) and produces a `DimensionScore(CONTENT)` with up to 50 points.

**Inputs:**
- `ValidationResult.diagnostics[]` — filtered to content-relevant codes
- Criteria registry (v0.4.0a)

**Criteria Evaluated:**

| Criterion | Points | Level | Key Diagnostics | Scoring Mode |
|-----------|--------|-------|-----------------|--------------|
| DS-VC-CON-001 | 5 | L2 | W003 (link missing description) | GRADUATED (% of links with descriptions) |
| DS-VC-CON-002 | 4 | L2 | E006 (broken links, reachability) | GRADUATED (% of URLs resolving) |
| DS-VC-CON-003 | 3 | L2 | W011 (placeholder text) | GRADUATED (% of sections without placeholders) |
| DS-VC-CON-004 | 4 | L2 | W011 (empty sections) | GRADUATED (% of non-empty sections) |
| DS-VC-CON-005 | 3 | L2 | Duplicate section names (heuristic) | BINARY |
| DS-VC-CON-006 | 3 | L2 | Blockquote substantiveness (>20 chars per spec) | BINARY |
| DS-VC-CON-007 | 3 | L2 | W006 (formulaic descriptions) | BINARY |
| DS-VC-CON-008 | 5 | L3 | W002 (non-canonical names), compliance rate | GRADUATED (≥70% threshold for full points) |
| DS-VC-CON-009 | 5 | L3 | W009 (no Master Index) | BINARY |
| DS-VC-CON-010 | 5 | L3 | W004 (no code examples) | BINARY |
| DS-VC-CON-011 | 3 | L3 | W005 (code no language) | GRADUATED (% with specifiers) |
| DS-VC-CON-012 | 4 | L3 | W010 (token budget exceeded) | BINARY |
| DS-VC-CON-013 | 3 | L3 | W007 (missing version metadata) | BINARY |

**Scoring Logic:**
- Same pattern as structural scorer: look up diagnostic codes from registry, count occurrences, apply scoring mode, sum points.
- For graduated criteria, the compliance rate is calculated from the count of violations vs. the total number of items checked. Example: if 15 of 20 links have descriptions, compliance = 75%, and CON-001 earns `0.75 × 5 = 3.75` points.
- Points are stored as `float` (the `DimensionScore.points` field supports this).
- Populate `details[]` with per-criterion results for drill-down.

**Empirical Weighting Note:** The point allocations already embed empirical weighting (DECISION-014). Code examples (CON-010, 5 pts) and Master Index (CON-009, 5 pts) receive the highest allocations because they are the strongest quality predictors (r ≈ 0.65 and 87% vs. 31% task success, respectively). No additional weighting is applied at the scorer level.

**Grounding:** DS-QS-DIM-CON (full specification), DS-VC-CON-001 through DS-VC-CON-013, DECISION-014.

---

#### v0.4.0d — Anti-Pattern Dimension Scorer

**What it does:** Evaluates the 8 anti-pattern criteria (DS-VC-APD-001 through APD-008) and produces a `DimensionScore(ANTI_PATTERN)` with up to 20 points.

**Inputs:**
- `ValidationResult.diagnostics[]` — filtered to L4 and anti-pattern-relevant codes
- Anti-pattern metadata attached by v0.3.4 (anti_pattern_id on diagnostics)
- Criteria registry (v0.4.0a)

**Criteria Evaluated:**

| Criterion | Points | Level | Key Input | Available at v0.4.x? |
|-----------|--------|-------|-----------|----------------------|
| DS-VC-APD-001 | 3 | L4 | I001 absence (LLM Instructions present) | No — scores 0 until v0.9.0 |
| DS-VC-APD-002 | 3 | L4 | I002 absence (Concept Definitions present) | No — scores 0 until v0.9.0 |
| DS-VC-APD-003 | 3 | L4 | I003 absence (Few-Shot Examples present) | No — scores 0 until v0.9.0 |
| DS-VC-APD-004 | 3 | L4 | No content anti-patterns (AP-CONT-001–009) | Partial — 7 of 9 patterns detectable |
| DS-VC-APD-005 | 2 | L4 | No strategic anti-patterns (AP-STRAT-001–004) | Partial — 3 of 4 patterns detectable |
| DS-VC-APD-006 | 2 | L4 | No section >40% of total token budget | Yes |
| DS-VC-APD-007 | 2 | L4 | ≥90% of URLs are absolute | Yes |
| DS-VC-APD-008 | 2 | L4 | Jargon defined or linked | No — depends on I007 (L4) |

**Scoring Logic:**
- APD-001 through APD-003: Check whether the corresponding L4 diagnostic code (I001, I002, I003) was emitted. If L4 checks are not active (pre-v0.9.0), these codes will never appear in the `ValidationResult`, and these criteria score 0 by default. The scorer does not "fake" the absence of a diagnostic — if the code wasn't checked, the file gets no credit.
- APD-004: Count detected content anti-patterns (AP-CONT-001 through AP-CONT-009) from the anti-pattern metadata. Graduated scoring: `(patterns_absent / patterns_evaluable) × 3 points`. Patterns that depend on L4 codes (AP-CONT-003, AP-CONT-008) are excluded from the `patterns_evaluable` denominator until v0.9.0.
- APD-005: Same approach as APD-004 but for strategic anti-patterns (AP-STRAT-001 through AP-STRAT-004). AP-STRAT-004 excluded from denominator until v0.9.0.
- APD-006: Check the token distribution across sections. If any section exceeds 40% of the total token budget → partial or zero points. The validator (v0.3.x) does not emit a specific diagnostic for this; the scorer must compute it from the `ParsedLlmsTxt` sections' `estimated_tokens` values. This is the one case where the scorer reads the parsed model, not just the `ValidationResult`.
- APD-007: Count URLs classified as relative (I004 diagnostic instances) vs. total URLs. If ≥90% absolute → full points.
- APD-008: Check for I007 (jargon without definition). Same L4 dependency issue as APD-001–003.

> **Implementation Note — APD-006 Model Access:** DS-VC-APD-006 (token distribution check) requires reading per-section `estimated_tokens` values from the parsed model — information not captured in the `ValidationResult`. This means either: (a) the scorer accepts `ParsedLlmsTxt` as an additional input alongside `ValidationResult`, or (b) the validator (v0.3.x) emits a new informational diagnostic with token distribution data. The design spec for v0.4.0d should resolve this. Option (a) is simpler; option (b) maintains the clean separation between validation and scoring.

> **Effective Maximum Score:** Until v0.9.0, the APD dimension's effective maximum is approximately 9 points (APD-004: 3 + APD-005: 2 + APD-006: 2 + APD-007: 2). APD-001, APD-002, APD-003, and APD-008 all score 0 due to L4 dependencies. This means the composite maximum is approximately 89 points (30 + 50 + 9), placing the ceiling at STRONG grade. EXEMPLARY (≥90) becomes achievable only when v0.9.0 activates L4 checks. Calibration specimens must account for this ceiling.

**Grounding:** DS-QS-DIM-APD (full specification), DS-VC-APD-001 through DS-VC-APD-008, DECISION-016.

---

### 3.2 v0.4.1 — Composite Scoring & Grading

**Goal:** Combine the three dimension scores into a single composite score, apply the gating rule, assign a grade, and populate the `QualityScore` output model. This is the integration sub-version for the scoring pipeline.

---

#### v0.4.1a — Composite Score Calculation

**What it does:** Sums the three dimension scores into a single 0–100 composite.

**Inputs:**
- `DimensionScore(STRUCTURAL)` from v0.4.0b
- `DimensionScore(CONTENT)` from v0.4.0c
- `DimensionScore(ANTI_PATTERN)` from v0.4.0d

**Calculation:**
```
total_score = structural.points + content.points + anti_pattern.points
```

Because the dimension point allocations already embed the 30/50/20 weighting (the max_points are 30, 50, and 20 respectively), no additional weighting multiplier is needed. The sum of dimension points IS the composite score.

**Boundary Behavior:**
- Minimum: 0 (all criteria fail across all dimensions)
- Maximum: 100 (all criteria pass with full compliance)
- Precision: `float` (individual criterion scores may produce fractional points via graduated scoring)

**What this does NOT do:**
- Does not apply gating — that's v0.4.1b.
- Does not assign a grade — that's v0.4.1c.
- The composite is the *raw* score before any enforcement mechanisms.

**Grounding:** DECISION-014 (30-50-20 weight model), `QualityScore.total_score` field definition.

---

#### v0.4.1b — Gating Rule Application (DS-QS-GATE)

**What it does:** Checks whether any critical anti-pattern was detected and, if so, caps the composite score at 29.

**Inputs:**
- The raw composite score from v0.4.1a
- The `critical_anti_pattern_detected` flag (or equivalent mechanism) from v0.3.4a's anti-pattern detection

**Logic:**
1. Check if the `ValidationResult` contains any diagnostics with critical anti-pattern metadata (AP-CRIT-001 through AP-CRIT-004).
2. If yes:
   - Set `DimensionScore(STRUCTURAL).is_gated = True`.
   - Apply cap: `total_score = min(total_score, 29)`.
3. If no:
   - Leave `total_score` unchanged.
   - `is_gated` remains `False`.

**Boundary Behavior:**
- If `total_score ≤ 29` AND gating is triggered: no change (score already in CRITICAL range).
- If `total_score > 29` AND gating is triggered: score forced to 29.
- Gating is non-proportional: one critical pattern has the same effect as four.

**Cap Value:** 29. This is the highest score that still maps to the CRITICAL grade, ensuring gated files never achieve NEEDS_WORK or above.

**What this does NOT do:**
- Does not detect critical anti-patterns itself. Detection happens in v0.3.4a. The scorer only reads the result.
- Does not modify individual dimension scores. The per-dimension points remain unchanged; only the composite `total_score` is capped.

**Grounding:** DS-QS-GATE (full specification), DECISION-016 (severity classification).

---

#### v0.4.1c — Grade Assignment

**What it does:** Maps the (possibly gated) composite score to a `QualityGrade` using the threshold table defined in DS-QS-GRADE.

**Inputs:**
- The final `total_score` (after gating, from v0.4.1b)

**Grade Thresholds:**

| Grade | Score Range | Validation Level Alignment |
|-------|-----------|---------------------------|
| EXEMPLARY | ≥ 90 | L4 (DocStratum Extended) |
| STRONG | 70–89 | L3 (Best Practices) |
| ADEQUATE | 50–69 | L2 (Content Quality) |
| NEEDS_WORK | 30–49 | L1 (Structural) |
| CRITICAL | 0–29 | L0 (Parseable Only) |

**Logic:**
- Use `QualityGrade.from_score(total_score)`, which already exists in `quality.py`.
- The method uses inclusive lower bounds (≥ 90 → EXEMPLARY, ≥ 70 → STRONG, etc.).
- A score of exactly 90 is EXEMPLARY; exactly 70 is STRONG; exactly 29.5 is CRITICAL (scores are float, threshold comparison is `>=`).

**Implementation Note:** The existing `QualityGrade.from_score()` method accepts `int`, not `float`. Since graduated scoring produces fractional points, the design spec should determine whether to round the composite score to an integer before grade assignment (recommended: `round()` to nearest int) or to update the method signature to accept `float`.

**Grounding:** DS-QS-GRADE (full specification), `quality.py` → `QualityGrade.from_score()`.

---

#### v0.4.1d — Per-Check Detail Population

**What it does:** Populates the `DimensionScore.details[]` list with per-criterion drill-down data, enabling downstream consumers (remediation, reports) to see exactly which criteria passed, failed, and how many points each earned.

**Inputs:**
- The per-criterion evaluation results from each dimension scorer (v0.4.0b, v0.4.0c, v0.4.0d)

**Detail Record Structure:**

Each entry in `details[]` follows the schema already defined by `DimensionScore.details` as `list[dict]` with keys `{check_id, passed, weight, points}`:

| Key | Type | Description |
|-----|------|-------------|
| `check_id` | str | Criterion ID (e.g., "DS-VC-STR-001") |
| `passed` | bool | Whether the criterion is fully satisfied |
| `weight` | float | Maximum points for this criterion |
| `points` | float | Points actually earned |

**Additional Fields (Recommended):**
- `compliance_rate` (float, 0.0–1.0): For graduated criteria, the raw compliance percentage.
- `diagnostic_count` (int): Number of relevant diagnostics that affected this criterion.
- `level` (str): The validation level this criterion belongs to (L1, L2, L3, L4).

**What this enables:**
- Remediation framework (v0.6.x) can sort criteria by point deficit (weight - points) to prioritize fixes.
- Report generation (v0.8.x) can render per-criterion breakdowns.
- CLI output (v0.5.x) can show "top 5 things to fix" based on potential score gain.

**Grounding:** `DimensionScore.details` field definition in `quality.py`.

---

### 3.3 v0.4.2 — Scoring Calibration & Testing

**Goal:** Validate the scoring engine against the 6 gold standard calibration specimens, test boundary behavior at grade thresholds, and establish regression baselines. This is the confidence sub-version — it proves the scorer works correctly before downstream phases depend on it.

---

#### v0.4.2a — Dimension Scorer Unit Tests

**What it does:** Comprehensive unit tests for each of the three dimension scorers (v0.4.0b, v0.4.0c, v0.4.0d).

**Test Categories:**
- **Per-criterion tests:** Each of the 30 criteria tested independently with mock `ValidationResult` fixtures that trigger full compliance, partial compliance, and zero compliance.
- **Graduated scoring tests:** Verify that fractional points are calculated correctly for graduated criteria (e.g., 75% compliance on a 5-point criterion = 3.75 points).
- **Zero-data tests:** Verify behavior when the `ValidationResult` contains no diagnostics (e.g., a file that passed all validation checks should score near-maximum).
- **Skipped-level tests:** Verify that when L0 fails (and L1–L3 were never evaluated), the dimension scorers handle the absence of higher-level diagnostics correctly (scoring 0 for unevaluated criteria per Section 2.5).
- **APD L4-dependency tests:** Verify that APD-001 through APD-003 score 0 when L4 codes are absent, and score correctly when L4 codes are eventually present.

**Coverage Target:** ≥90% on the scoring module (higher than validation because scoring has fewer branches but more numerical precision requirements).

**Grounding:** RR-META-testing-standards.

---

#### v0.4.2b — Composite & Gating Unit Tests

**What it does:** Unit tests for the composite calculation (v0.4.1a), gating rule (v0.4.1b), grade assignment (v0.4.1c), and detail population (v0.4.1d).

**Test Categories:**
- **Composite arithmetic:** Verify that `total_score = structural + content + anti_pattern` with various dimension score combinations.
- **Gating tests:** Verify all four critical anti-patterns independently trigger the cap at 29. Verify that non-critical patterns do NOT trigger gating. Verify that scores already below 29 are unchanged by gating.
- **Grade boundary tests:** Verify exact threshold behavior: score 89 → STRONG, score 90 → EXEMPLARY, score 69 → ADEQUATE, score 70 → STRONG, score 29 → CRITICAL, score 30 → NEEDS_WORK.
- **Float precision tests:** Verify that fractional scores (e.g., 89.5) are handled correctly at grade boundaries.
- **Detail completeness tests:** Verify that every criterion appears in `details[]` with all required fields populated.

**Grounding:** DS-QS-GATE, DS-QS-GRADE, `QualityGrade.from_score()`.

---

#### v0.4.2c — Calibration Specimen Scoring

**What it does:** Runs the complete scoring pipeline (v0.3.x → v0.4.x) on the 6 gold standard calibration specimens and verifies that scores fall within expected ranges.

**Expected Results:**

| Specimen | Expected Score | Expected Grade | Tolerance |
|----------|---------------|----------------|-----------|
| Svelte (DS-CS-001) | 92 | EXEMPLARY | ±3 |
| Pydantic (DS-CS-002) | 90 | EXEMPLARY | ±3 |
| Vercel AI SDK (DS-CS-003) | 90 | EXEMPLARY | ±3 |
| Shadcn UI (DS-CS-004) | 89 | STRONG | ±3 |
| Cursor (DS-CS-005) | 42 | NEEDS_WORK | ±3 |
| NVIDIA (DS-CS-006) | 24 | CRITICAL | ±3 |

> **Important Caveat:** The expected scores above were calibrated assuming ALL 30 criteria are fully evaluable. Since APD-001 through APD-003 score 0 until v0.9.0, the actual scores at v0.4.x will be **up to 11 points lower** than the reference values (9 points from APD-001–003, plus 2 points from APD-008, all L4-dependent). The calibration test should account for this by applying an adjustment factor or by defining v0.4.x-specific expected ranges.

**Per-Dimension Validation:**
- Beyond total score, verify that per-dimension scores are reasonable (e.g., Svelte should score near-maximum on Structural, NVIDIA should score near-minimum).
- Verify that NVIDIA triggers the DS-QS-GATE gating rule (expected: critical anti-patterns detected).
- Verify that Cursor does NOT trigger gating (it has problems, but not critical-level failures).

**Grounding:** DS-CS-001 through DS-CS-006 (calibration specimen specifications).

---

#### v0.4.2d — Boundary & Regression Tests

**What it does:** Targeted tests for edge cases and grade boundary behavior to establish regression baselines.

**Test Scenarios:**
- **Perfect score:** A mock `ValidationResult` with zero diagnostics → expect 100 points (or ~91 with L4 ceiling), EXEMPLARY grade.
- **Zero score:** A mock `ValidationResult` with all possible diagnostics triggered → expect near-0 points, CRITICAL grade.
- **Gating at exactly 29:** Construct a scenario where pre-gated score is exactly 30 (the boundary) and a critical pattern is detected → expect final score 29, CRITICAL grade.
- **Gating at exactly 29 from above:** Pre-gated score of 91 with gating → expect 29.
- **Empty ValidationResult:** A `ValidationResult` with `diagnostics=[]` and `levels_passed={L0: True, L1: True, L2: True, L3: True}` → expect high score.
- **L0-only failure:** `ValidationResult` where only L0 was attempted and failed → expect near-0, CRITICAL.
- **Float rounding:** Score of 89.5 → verify grade assignment (STRONG or EXEMPLARY, depending on rounding decision).
- **Single dimension failure:** One dimension scores 0 while others score maximum → verify composite and grade are correct.

**Regression Baseline:**
- Record the exact `QualityScore` output for each calibration specimen as a JSON fixture.
- Future changes to the scoring engine must produce results within the ±3 tolerance of these baselines.
- CI integration: `pytest --cov=docstratum.scoring --cov-fail-under=90` passes.

**Grounding:** DS-QS-GRADE (boundary behavior), DS-QS-GATE (cap behavior), RR-META-testing-standards.

---

## 4. Dependency Map

```
v0.4.0 (Dimension Scoring) ─── three independent scorers, one shared registry
    │
    ├── v0.4.0a (Criteria Registry)     [no dependencies — built from ASoT specs]
    │       ↓
    ├── v0.4.0b (Structural Scorer)     [depends on v0.4.0a registry]
    ├── v0.4.0c (Content Scorer)        [depends on v0.4.0a registry]
    └── v0.4.0d (Anti-Pattern Scorer)   [depends on v0.4.0a registry]
              │
              ▼ (all three dimensions scored)
v0.4.1 (Composite & Grading) ─── sequential pipeline
    │
    ├── v0.4.1a (Composite Calculation) [depends on v0.4.0b, v0.4.0c, v0.4.0d]
    │       ↓
    ├── v0.4.1b (Gating Rule)           [depends on v0.4.1a + v0.3.4a anti-pattern flags]
    │       ↓
    ├── v0.4.1c (Grade Assignment)      [depends on v0.4.1b — needs gated score]
    │       ↓
    └── v0.4.1d (Detail Population)     [depends on v0.4.0b, v0.4.0c, v0.4.0d — needs per-criterion data]
              │
              ▼ (scoring pipeline complete)
v0.4.2 (Calibration & Testing)
    │
    ├── v0.4.2a (Dimension Unit Tests)   [can be written alongside v0.4.0]
    ├── v0.4.2b (Composite Unit Tests)   [can be written alongside v0.4.1]
    ├── v0.4.2c (Calibration Specimens)  [requires v0.4.1 complete + v0.3.x operational]
    └── v0.4.2d (Boundary & Regression)  [requires v0.4.1 complete]
```

**Parallelization Opportunities:**
- v0.4.0b, v0.4.0c, and v0.4.0d are independent of each other and can be implemented in parallel once v0.4.0a is complete.
- v0.4.2a and v0.4.2b can be developed incrementally alongside their respective implementation sub-parts.
- v0.4.1d can be developed in parallel with v0.4.1b/v0.4.1c since it reads from the dimension scorers, not from the composite.

**External Dependencies:**
- v0.3.x must be fully operational (producing `ValidationResult` instances) before v0.4.2c calibration tests can run.
- The `QualityScore`, `QualityGrade`, `DimensionScore`, and `QualityDimension` models from `quality.py` (v0.1.2b) are consumed as-is. No model changes are anticipated, but see Section 5 for potential field naming issues.

---

## 5. Models Consumed (Not Modified)

| Model | Source Module | Scorer's Role | Notes |
|-------|-------------|--------------|-------|
| `ValidationResult` | `schema/validation.py` | Primary input — reads `diagnostics[]`, `level_achieved`, `levels_passed{}` | |
| `ValidationDiagnostic` | `schema/validation.py` | Reads `code`, `severity`, `level`, `check_id`, anti-pattern metadata | Anti-pattern metadata attachment mechanism TBD in v0.3.4 |
| `DiagnosticCode` | `schema/diagnostics.py` | Used to match diagnostics to criteria via the registry | |
| `Severity` | `schema/diagnostics.py` | Used to filter ERROR vs WARNING vs INFO findings | |
| `ValidationLevel` | `schema/validation.py` | Used to determine which criteria apply when levels are skipped | |
| `QualityScore` | `schema/quality.py` | Populates as output — `total_score`, `grade`, `dimensions{}`, `scored_at`, `source_filename` | |
| `QualityGrade` | `schema/quality.py` | Uses `from_score()` for grade assignment | Method signature accepts `int`, may need `float` support |
| `DimensionScore` | `schema/quality.py` | Populates per-dimension — `dimension`, `points`, `max_points`, `checks_passed/failed/total`, `details[]`, `is_gated` | |
| `QualityDimension` | `schema/quality.py` | Enum key for the `dimensions{}` dictionary | |
| `AntiPatternID` | `schema/constants.py` | Used by APD scorer to identify which patterns were detected | |
| `AntiPatternCategory` | `schema/constants.py` | Used to classify patterns by severity tier | |
| `ANTI_PATTERN_REGISTRY` | `schema/constants.py` | Used to enumerate patterns for APD-004 and APD-005 evaluation | |

> **Field Naming Observation:** The ASoT scoring dimension specs (DS-QS-DIM-STR, DS-QS-DIM-CON, DS-QS-DIM-APD) reference `earned_points` in their Python interface examples. The actual `DimensionScore` model in `quality.py` uses `points` (not `earned_points`). This is a documentation-vs-code asymmetry. The scorer should use the actual field name (`points`). The design spec for v0.4.0a should note this discrepancy and recommend either updating the ASoT specs or renaming the field — but the scope does not require resolving it now.

> **CompositeScore Reference:** The DS-QS-GATE specification references a `CompositeScore` class and `CompositeScore.apply_gating()` method. This class does not exist in the current `quality.py` — only `QualityScore` exists. The scorer should use `QualityScore` as the output model. The design spec for v0.4.1a should determine whether to implement the composite pipeline within the `QualityScore` model or as a separate orchestration function.

**The scorer creates `QualityScore` and `DimensionScore` instances but does not modify any input models.**

---

## 6. Exit Criteria

v0.4.x is complete when:

- [ ] The criteria-to-diagnostic mapping registry (v0.4.0a) is implemented with all 30 criteria mapped.
- [ ] The Structural Dimension scorer (v0.4.0b) correctly evaluates all 9 STR criteria and produces `DimensionScore(STRUCTURAL)`.
- [ ] The Content Dimension scorer (v0.4.0c) correctly evaluates all 13 CON criteria and produces `DimensionScore(CONTENT)`.
- [ ] The Anti-Pattern Dimension scorer (v0.4.0d) correctly evaluates all 8 APD criteria, handling L4 dependencies gracefully (scoring 0 for unevaluable criteria).
- [ ] Graduated scoring produces fractional points (not just binary 0/full) for applicable criteria.
- [ ] The composite score calculation (v0.4.1a) correctly sums dimension points to produce a 0–100 score.
- [ ] The DS-QS-GATE gating rule (v0.4.1b) correctly caps the score at 29 when any critical anti-pattern is detected.
- [ ] Grade assignment (v0.4.1c) maps scores to grades per DS-QS-GRADE thresholds.
- [ ] Per-check details (v0.4.1d) are populated for all 30 criteria with `check_id`, `passed`, `weight`, `points`.
- [ ] All 6 calibration specimens produce scores within ±3 of expected values (after adjusting for L4 ceiling).
- [ ] Grade boundary tests pass at all thresholds (29/30, 49/50, 69/70, 89/90).
- [ ] Gating tests pass for all 4 critical anti-patterns independently.
- [ ] The scorer is extensible — when v0.9.0 adds L4 diagnostic codes, the APD scorer automatically evaluates APD-001 through APD-003 without framework changes.
- [ ] `pytest --cov=docstratum.scoring --cov-fail-under=90` passes.
- [ ] `black --check` and `ruff check` pass on all new code.
- [ ] No new fields have been added to any v0.1.2 Pydantic model without a documented amendment.

---

## 7. What Comes Next

The scorer's output (`QualityScore`) is the input to:

- **v0.5.x (CLI & Profiles):** Formats the `QualityScore` for terminal display. The profile system may filter which criteria are shown or active, but it reads the scorer's output — it does not modify it. Exit codes map to grades (0 = EXEMPLARY/STRONG, 1 = ADEQUATE/NEEDS_WORK, 2 = CRITICAL).
- **v0.6.x (Remediation Framework):** Reads the per-criterion details from `DimensionScore.details[]` to compute score impact projections ("fixing W003 on 5 links would gain +3.75 points on CON-001"). Prioritizes remediation actions by potential point gain.
- **v0.7.x (Ecosystem Integration):** Wires the single-file scorer into the ecosystem pipeline's Stage 2. Per-file `QualityScore` instances feed into the ecosystem-level aggregate score.
- **v0.8.x (Report Generation):** Formats `QualityScore` into JSON, Markdown, and HTML reports with per-dimension and per-criterion breakdowns.
