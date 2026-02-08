# DS-VC-APD-005: No Strategic Anti-Patterns

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VC-APD-005 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Platinum ID** | L4-05 |
| **Dimension** | Anti-Pattern Detection (20%) |
| **Level** | L4 — Exemplary |
| **Weight** | 2 / 20 anti-pattern points [CALIBRATION-NEEDED] |
| **Pass Type** | SOFT |
| **Measurability** | Partially measurable |
| **Provenance** | v0.0.4c anti-pattern catalog; 4 strategic anti-patterns (2 measurable, 2 require judgment) |

## Description

This criterion verifies that the file avoids the 4 strategic anti-patterns. Strategic anti-patterns are architectural and scope-level issues that reflect problematic decisions in how the documentation is designed, organized, or positioned. They are rarer than content anti-patterns but potentially more consequential.

The 4 strategic anti-patterns are:

1. **DS-AP-STRAT-001** (Automation Obsession): Over-emphasis on automation, tooling, or programmatic access at the expense of human understanding. Documented features are inaccessible without complex automation.
2. **DS-AP-STRAT-002** (Monolith Monster): Excessive length (token bloat) that defeats the purpose of the documentation. A single 100K+ token file that should be split into multiple focused documents.
3. **DS-AP-STRAT-003** (Meta-Documentation Spiral): Self-referential or overly meta content (e.g., documentation about the documentation) that obscures rather than clarifies.
4. **DS-AP-STRAT-004** (Preference Trap): Trust laundering — claiming neutrality or authority while promoting specific tools, frameworks, or opinions without acknowledgment.

This is an **aggregate criterion**. It reports success when **none** of the 4 individual strategic anti-patterns are detected. Each has its own detection logic; this criterion combines all strategic-category results into a single composite check.

## Pass Condition

None of the 4 strategic anti-patterns are detected:

```python
strategic_patterns = [
    AP_STRAT_001,  # Automation Obsession
    AP_STRAT_002,  # Monolith Monster
    AP_STRAT_003,  # Meta-Documentation Spiral
    AP_STRAT_004,  # Preference Trap
]
for pattern in strategic_patterns:
    assert not pattern.detected
```

**Measurability note:** Detection varies by anti-pattern:
- **Monolith Monster (AP-STRAT-002)**: Fully measurable. Token count > 100K is an objective signal.
- **Automation Obsession (AP-STRAT-001)**: Partially measurable. Heuristic detection (phrase matching for "must automate", "requires script") may produce false positives.
- **Meta-Documentation Spiral (AP-STRAT-003)**: Partially measurable. Self-referential content detection (searching for phrases like "this document describes...") is heuristic.
- **Preference Trap (AP-STRAT-004)**: Partially measurable (heuristic). Trust laundering is difficult to detect programmatically and may require LLM-assisted evaluation in future versions.

## Fail Condition

Any one or more of the 4 strategic anti-patterns are detected. This is a SOFT criterion — detection applies deduction-based penalties to the Anti-Pattern Detection score but does not block progression. Penalties are weighted by the severity of the detected pattern.

## Emitted Diagnostics

This criterion does not emit its own diagnostic. Instead, it aggregates signals from the 4 individual strategic anti-patterns:
- DS-DC-W010 (WARNING): Automation Obsession indicators detected
- DS-DC-W011 (WARNING): Monolith Monster — file exceeds 100K tokens
- DS-DC-W012 (WARNING): Meta-Documentation Spiral — excessive self-reference
- DS-DC-W013 (WARNING): Preference Trap — trust laundering detected

## Related Anti-Patterns

All 4 strategic anti-patterns:
- **DS-AP-STRAT-001** (Automation Obsession)
- **DS-AP-STRAT-002** (Monolith Monster)
- **DS-AP-STRAT-003** (Meta-Documentation Spiral)
- **DS-AP-STRAT-004** (Preference Trap)

## Related Criteria

- **DS-VC-STR-008** (No Critical Anti-Patterns): Critical-severity counterpart. STR-008 checks for critical structural issues; APD-005 checks strategic architectural problems.
- **DS-VC-APD-004** (No Content Anti-Patterns): Content-severity counterpart. Together, APD-004, APD-005, and STR-008 form a comprehensive anti-pattern screening.
- **DS-VC-CON-012** (Token Budget Respected): File-level token budget. Monolith Monster (AP-STRAT-002) overlaps with CON-012; APD-005 is the specific strategic check.

## Calibration Notes

Strategic anti-patterns are the rarest and most severe. The v0.0.2c audit of 24 specimens found:

- **Monolith Monster**: 2 files (8%) exceeded 100K tokens
- **Automation Obsession**: 3 files (12%) showed over-emphasis on automation
- **Meta-Documentation Spiral**: 0 files (0%) — rare in published llms.txt
- **Preference Trap**: 4 files (17%) exhibited subtle trust laundering

Strategic anti-patterns are difficult to detect programmatically and often require human judgment:
- **Monolith Monster** is the most objectively detectable (pure token count > 100K)
- **Preference Trap** is the hardest to detect and may require LLM-assisted evaluation in future versions
- **Automation Obsession** and **Meta-Documentation Spiral** are partially detectable through pattern matching but produce heuristic results

Top-scoring specimens (Svelte, Pydantic) are free of all strategic anti-patterns, though they may not all be free of every content anti-pattern. The presence of strategic anti-patterns is a strong negative signal and generally indicates architectural problems that limit the file's usefulness.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase C exemplary criterion |
