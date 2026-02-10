# v0.4.1b — Gating Rule Application (DS-QS-GATE)

> **Version:** v0.4.1b
> **Document Type:** Sub-Part Design Specification
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.4.1-composite-scoring.md](RR-SPEC-v0.4.1-composite-scoring.md)
> **Depends On:** v0.4.1a (raw composite), v0.3.4a (critical anti-pattern detection)
> **Grounding:** DS-QS-GATE (full specification), DECISION-016 (severity classification)

---

## 1. Purpose

v0.4.1b implements the **DS-QS-GATE gating rule** — the single enforcement mechanism that prevents critically broken files from receiving passing grades regardless of their content scores.

### 1.1 The Gating Principle

A file containing any **critical anti-pattern** (AP-CRIT-001 through AP-CRIT-004) has its composite score capped at **29** — the maximum value that still maps to CRITICAL grade. This is a non-negotiable quality floor: no amount of good content can compensate for a fundamentally broken structure.

### 1.2 User Story

> As a file validator, I want files with critical anti-patterns to be forced into the CRITICAL grade so that dangerously broken files cannot masquerade as acceptable documentation.

### 1.3 The Four Critical Anti-Patterns

| ID          | Name              | Description                                          | Severity |
| ----------- | ----------------- | ---------------------------------------------------- | -------- |
| AP-CRIT-001 | Ghost File        | File contains no meaningful content                  | CRITICAL |
| AP-CRIT-002 | Structure Chaos   | File has no recognizable structure (no H1, no H2s)   | CRITICAL |
| AP-CRIT-003 | Encoding Disaster | File has encoding issues preventing reliable parsing | CRITICAL |
| AP-CRIT-004 | Link Void         | 100% of links are broken                             | CRITICAL |

---

## 2. Gating Logic

### 2.1 Decision Tree

```
Input: raw_total (float, 0–100), ValidationResult
    │
    ├── Scan ValidationResult.diagnostics[] for critical anti-pattern metadata
    │     │
    │     ├── Any diagnostic has anti-pattern ID ∈ {AP-CRIT-001, AP-CRIT-002,
    │     │     AP-CRIT-003, AP-CRIT-004}?
    │     │     │
    │     │     ├── YES: Critical anti-pattern detected
    │     │     │     ├── is_gated = True
    │     │     │     ├── final_total = min(raw_total, 29.0)
    │     │     │     └── Log: "DS-QS-GATE triggered: {pattern_id} detected,
    │     │     │             score capped at 29 (was {raw_total})"
    │     │     │
    │     │     └── NO: No critical anti-patterns
    │     │           ├── is_gated = False
    │     │           └── final_total = raw_total (unchanged)
    │     │
    │     └── Return (final_total, is_gated)
    │
    └── Note: Gating is BINARY — one critical pattern has the same
        effect as four. The cap is 29 regardless of how many trigger.
```

### 2.2 Implementation

```python
"""Implements v0.4.1b — DS-QS-GATE gating rule."""

import logging

from docstratum.schema.constants import AntiPatternID
from docstratum.schema.validation import ValidationResult

logger = logging.getLogger(__name__)

# The four critical anti-patterns that trigger gating
CRITICAL_ANTI_PATTERNS: frozenset[AntiPatternID] = frozenset({
    AntiPatternID.AP_CRIT_001,  # Ghost File
    AntiPatternID.AP_CRIT_002,  # Structure Chaos
    AntiPatternID.AP_CRIT_003,  # Encoding Disaster
    AntiPatternID.AP_CRIT_004,  # Link Void
})

# The maximum score a gated file can receive
GATE_CAP: float = 29.0


def apply_gating(
    raw_total: float,
    result: ValidationResult,
    anti_pattern_results: dict | None = None,
) -> tuple[float, bool]:
    """Apply the DS-QS-GATE gating rule.

    Checks whether any critical anti-pattern (AP-CRIT-001 through
    AP-CRIT-004) was detected in the validation result. If so,
    caps the composite score at 29 (CRITICAL grade ceiling).

    Args:
        raw_total: Pre-gating composite score from v0.4.1a (0–100).
        result: ValidationResult from v0.3.x, inspected for AP-CRIT
                diagnostics.
        anti_pattern_results: Optional anti-pattern detection results
                from v0.3.4. If provided, checked for critical patterns.
                If not provided, critical patterns are detected from
                the diagnostic metadata.

    Returns:
        Tuple of (final_total, is_gated):
        - final_total: The (possibly capped) composite score.
        - is_gated: True if gating was triggered.

    Implements v0.4.1b. Grounding: DS-QS-GATE, DECISION-016.
    """
    detected = _detect_critical_anti_patterns(result, anti_pattern_results)

    if detected:
        logger.warning(
            "DS-QS-GATE triggered: critical anti-pattern(s) %s detected. "
            "Score capped at %.1f (was %.2f).",
            [p.value for p in detected],
            GATE_CAP,
            raw_total,
        )
        return min(raw_total, GATE_CAP), True

    return raw_total, False


def _detect_critical_anti_patterns(
    result: ValidationResult,
    anti_pattern_results: dict | None,
) -> list[AntiPatternID]:
    """Detect critical anti-patterns from validation results.

    Checks two sources:
    1. Anti-pattern results dict (from v0.3.4a detection stage)
    2. Diagnostic metadata (anti-pattern IDs on ValidationDiagnostic)

    Returns list of detected critical pattern IDs (empty if none).
    """
    detected: list[AntiPatternID] = []

    # Source 1: Anti-pattern results from v0.3.4a
    if anti_pattern_results:
        for ap_id in CRITICAL_ANTI_PATTERNS:
            if anti_pattern_results.get(ap_id.value, {}).get("detected", False):
                detected.append(ap_id)

    # Source 2: Diagnostic metadata (fallback / cross-check)
    # When v0.3.4a attaches anti_pattern_id to diagnostics,
    # we can also detect critical patterns from the diagnostic stream.
    # This is a secondary detection path for defense in depth.
    # Implementation detail deferred to v0.3.4a integration.

    return detected
```

### 2.3 Gating Behavior Table

| Pre-Gated Score | Critical AP Detected? | Final Score | Grade      | Notes                                   |
| --------------- | --------------------- | ----------- | ---------- | --------------------------------------- |
| 95.0            | Yes (AP-CRIT-001)     | 29.0        | CRITICAL   | High score meaningless with ghost file  |
| 42.0            | Yes (AP-CRIT-002)     | 29.0        | CRITICAL   | Score was above 29, capped              |
| 29.0            | Yes (AP-CRIT-003)     | 29.0        | CRITICAL   | Already at cap — no change              |
| 15.0            | Yes (AP-CRIT-004)     | 15.0        | CRITICAL   | Below cap — no change (min() preserves) |
| 0.0             | Yes (all four)        | 0.0         | CRITICAL   | Worst case, already at 0                |
| 95.0            | No                    | 95.0        | EXEMPLARY  | No gating applied                       |
| 29.5            | No                    | 29.5        | CRITICAL   | Below NEEDS_WORK threshold, not gated   |
| 30.0            | No                    | 30.0        | NEEDS_WORK | Barely above CRITICAL, not gated        |
| 89.0            | Yes (AP-CRIT-001)     | 29.0        | CRITICAL   | 60-point drop from gating               |

### 2.4 Gating is Non-Proportional

One critical pattern has the **same effect** as four. The cap is always 29, regardless of:

- How many critical patterns are detected (1 vs. 4)
- Which specific pattern triggered it
- How far above 29 the pre-gated score was

This simplicity is intentional (DECISION-016): critical anti-patterns represent _fundamental_ brokenness where gradations of severity are meaningless.

---

## 3. Side Effects

### 3.1 `is_gated` Flag

When gating triggers, the caller (`score_file()`) sets `DimensionScore(STRUCTURAL).is_gated = True`. This flag:

- Is readable by downstream consumers (remediation, reports)
- Does **not** modify the structural dimension's `points` — only the composite `total_score` is capped
- Signals to the user that the score was artificially limited

### 3.2 Logging

All gating events are logged at `WARNING` level because they represent a significant quality enforcement action:

```
2026-02-10 12:34:56 | WARNING  | docstratum.scoring.composite:apply_gating:42 | DS-QS-GATE triggered: critical anti-pattern(s) ['ap_crit_001'] detected. Score capped at 29.0 (was 78.50).
```

---

## 4. Edge Cases

| Case                                      | Behavior                                                | Rationale                                |
| ----------------------------------------- | ------------------------------------------------------- | ---------------------------------------- |
| Multiple critical APs detected            | Cap at 29 (same as single)                              | Binary gating — non-proportional         |
| Score already below 29 + gating triggered | Score unchanged, `is_gated = True`                      | `min()` preserves lower value            |
| Score exactly 29.0 + gating triggered     | Score = 29.0, `is_gated = True`                         | At boundary — no numerical change        |
| Score exactly 30.0 + gating triggered     | Score = 29.0 (from 30 → 29)                             | Drops from NEEDS_WORK to CRITICAL        |
| No diagnostics in ValidationResult        | No gating (no AP-CRIT possible)                         | Clean result = no gating                 |
| Anti-pattern results dict is None         | Fallback to diagnostic metadata scan                    | Defensive — works without v0.3.4 results |
| Non-critical anti-patterns only           | No gating applied                                       | Only AP-CRIT-001–004 trigger gate        |
| AP-STRUCT, AP-CONT, AP-STRAT patterns     | No gating (these affect dimension scores, not the gate) | By design — gating is CRIT-only          |

---

## 5. Deliverables

| File                                  | Description                                     |
| ------------------------------------- | ----------------------------------------------- |
| `src/docstratum/scoring/composite.py` | `apply_gating()` function (in composite module) |
| `tests/scoring/test_composite.py`     | Gating unit tests (v0.4.1b portion)             |

---

## 6. Test Plan (10 tests)

| #   | Test Name                                      | Input                                     | Expected                                      |
| --- | ---------------------------------------------- | ----------------------------------------- | --------------------------------------------- |
| 1   | `test_gating_caps_at_29`                       | Score 78.5, AP-CRIT-001 detected          | (29.0, True)                                  |
| 2   | `test_gating_all_four_critical`                | Score 95.0, all 4 AP-CRIT detected        | (29.0, True)                                  |
| 3   | `test_gating_score_below_cap`                  | Score 15.0, AP-CRIT-002 detected          | (15.0, True)                                  |
| 4   | `test_gating_score_at_cap`                     | Score 29.0, AP-CRIT-003 detected          | (29.0, True)                                  |
| 5   | `test_gating_score_at_30`                      | Score 30.0, AP-CRIT-004 detected          | (29.0, True)                                  |
| 6   | `test_no_gating_clean_result`                  | Score 85.0, no AP-CRIT                    | (85.0, False)                                 |
| 7   | `test_no_gating_non_critical_aps`              | Score 60.0, AP-STRUCT-001 only            | (60.0, False)                                 |
| 8   | `test_gating_each_critical_ap_independently`   | Score 50.0, each AP-CRIT-00N individually | All return (29.0, True)                       |
| 9   | `test_gating_sets_is_gated_on_structural`      | Via `score_file()` with AP-CRIT           | `str_score.is_gated == True`                  |
| 10  | `test_gating_does_not_modify_dimension_points` | Score 78.5, AP-CRIT-001 detected          | Dimension points unchanged, only total capped |

---

## 7. Changelog Requirements

```markdown
## [0.4.1b] - YYYY-MM-DD

**Gating Rule Application — DS-QS-GATE enforcement for critical anti-patterns.**

### Added

#### Gating Rule (`src/docstratum/scoring/composite.py`)

- `apply_gating()` — caps composite score at 29 when any critical anti-pattern (AP-CRIT-001–004) is detected (DS-QS-GATE)
- `CRITICAL_ANTI_PATTERNS` — frozen set of the 4 gating triggers
- `GATE_CAP = 29.0` — maximum score for gated files

### Notes

- **Gating is non-proportional:** 1 critical pattern has the same cap as 4.
- **Side effects:** Sets `DimensionScore(STRUCTURAL).is_gated = True`; logs at WARNING level.
- **Verification:** See test plan — each AP-CRIT tested independently.
```

---

## 8. Limitations

| Limitation                                  | Impact                                                   | Resolution Timeline     |
| ------------------------------------------- | -------------------------------------------------------- | ----------------------- |
| Detection depends on v0.3.4a implementation | If v0.3.4a doesn't attach AP-CRIT metadata, gating fails | v0.3.4a must ship first |
| No graduated gating (1 vs. 4 CRITs same)    | Intentional — critical = critical regardless of count    | Not planned             |
| Cap is hardcoded at 29.0                    | Not profile-configurable                                 | v0.5.x could override   |
| No "why was I gated" detail in QualityScore | Consumer must inspect ValidationResult separately        | v0.6.x (remediation)    |
