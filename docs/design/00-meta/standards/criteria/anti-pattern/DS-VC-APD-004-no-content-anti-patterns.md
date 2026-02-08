# DS-VC-APD-004: No Content Anti-Patterns

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VC-APD-004 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Platinum ID** | L4-04 |
| **Dimension** | Anti-Pattern Detection (20%) |
| **Level** | L4 — Exemplary |
| **Weight** | 3 / 20 anti-pattern points [CALIBRATION-NEEDED] |
| **Pass Type** | SOFT |
| **Measurability** | Fully measurable |
| **Provenance** | v0.0.4c anti-pattern catalog; 9 content anti-patterns with detection rules |

## Description

This criterion verifies that the file is free of all 9 content anti-patterns. The content anti-patterns are the most prevalent category of quality issues in llms.txt files. They include missing elements (examples, definitions, descriptions), outdated content, broken references, problematic stylistic choices, and lack of agent-facing guidance.

The 9 content anti-patterns are:

1. **DS-AP-CONT-001** (Copy-Paste Plague): Verbatim duplication of content, boilerplate, or unattributed quotations
2. **DS-AP-CONT-002** (Blank Canvas): Placeholder text ("TBD", "coming soon") without substantive content
3. **DS-AP-CONT-003** (Jargon Jungle): Heavy domain-specific terminology without definitions
4. **DS-AP-CONT-004** (Link Desert): Minimal external links or references despite relevance
5. **DS-AP-CONT-005** (Outdated Oracle): Version mismatches, deprecated APIs, or stale timestamps
6. **DS-AP-CONT-006** (Example Void): No code examples despite being a technical project
7. **DS-AP-CONT-007** (Formulaic Description): Generic, templated descriptions with no substance
8. **DS-AP-CONT-008** (Silent Agent): No LLM-facing guidance despite being an AI documentation file
9. **DS-AP-CONT-009** (Versionless Drift): Missing or unclear version metadata

This is an **aggregate criterion**. It reports success when **none** of the 9 individual content anti-patterns are detected. Each individual anti-pattern has its own detection logic (defined in the anti-pattern registry); this criterion combines all content-category results into a single composite check.

## Pass Condition

None of the 9 content anti-patterns are detected:

```python
content_patterns = [
    AP_CONT_001,  # Copy-Paste Plague
    AP_CONT_002,  # Blank Canvas
    AP_CONT_003,  # Jargon Jungle
    AP_CONT_004,  # Link Desert
    AP_CONT_005,  # Outdated Oracle
    AP_CONT_006,  # Example Void
    AP_CONT_007,  # Formulaic Description
    AP_CONT_008,  # Silent Agent
    AP_CONT_009,  # Versionless Drift
]
for pattern in content_patterns:
    assert not pattern.detected
```

The result is a composite signal: either **all 9 pass** (file is free of content anti-patterns) or at least one fails (file exhibits content quality issues).

## Fail Condition

Any one or more of the 9 content anti-patterns are detected. Detection severity varies by individual anti-pattern. This is a SOFT criterion — detection reduces the Anti-Pattern Detection dimension score but does not block progression. Each anti-pattern's individual detection is documented in its registry entry.

## Emitted Diagnostics

This criterion does not emit its own diagnostic. Instead, it aggregates diagnostic signals from the 9 individual content anti-patterns:
- DS-DC-W001 (WARNING): Copy-Paste Plague detected
- DS-DC-W002 (WARNING): Blank Canvas detected
- DS-DC-I002 (INFO): No structured concept definitions found (Jargon Jungle)
- DS-DC-W004 (WARNING): Minimal external references (Link Desert)
- DS-DC-W005 (WARNING): Version metadata missing or unclear (Outdated Oracle / Versionless Drift)
- DS-DC-W006 (WARNING): No code examples found (Example Void)
- DS-DC-W007 (WARNING): Formulaic, generic description (Formulaic Description)
- DS-DC-I001 (INFO): No LLM Instructions section found (Silent Agent)
- DS-DC-W009 (WARNING): Versionless Drift indicators detected

## Related Anti-Patterns

All 9 content anti-patterns:
- **DS-AP-CONT-001** (Copy-Paste Plague)
- **DS-AP-CONT-002** (Blank Canvas)
- **DS-AP-CONT-003** (Jargon Jungle)
- **DS-AP-CONT-004** (Link Desert)
- **DS-AP-CONT-005** (Outdated Oracle)
- **DS-AP-CONT-006** (Example Void)
- **DS-AP-CONT-007** (Formulaic Description)
- **DS-AP-CONT-008** (Silent Agent)
- **DS-AP-CONT-009** (Versionless Drift)

## Related Criteria

- **DS-VC-STR-008** (No Critical Anti-Patterns): Critical-severity counterpart. STR-008 checks for critical structural issues; APD-004 checks content quality.
- **DS-VC-APD-005** (No Strategic Anti-Patterns): Strategic-severity counterpart. Together, APD-004, APD-005, and STR-008 form a comprehensive anti-pattern screening.
- **DS-VC-CON-001 through DS-VC-CON-007**: Individual content checks that overlap with anti-pattern detection. For example, CON-010 (Code Examples Present) overlaps with AP-CONT-006 (Example Void).

## Calibration Notes

Content anti-patterns are by far the most common category of quality issues. The v0.0.2c audit of 24 specimens found:

- **Mean anti-patterns per file: 2.1 content anti-patterns**
- **Range: 0–5 content anti-patterns**
- **Files with 0 content anti-patterns: 6 (25%)** — these consistently scored above 75
- **Files with 1–2 content anti-patterns: 12 (50%)** — average score 65
- **Files with 3+ content anti-patterns: 6 (25%)** — average score 45–55

Top-scoring specimens (Svelte 92, Pydantic 90) are free of all 9 content anti-patterns. Files scoring below 50 typically exhibit 4+ content anti-patterns. This criterion directly correlates with overall quality.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase C exemplary criterion |
