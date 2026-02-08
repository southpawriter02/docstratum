# DS-DD-009: Anti-Pattern Detection in v0.2.4

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DD-009 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Decision ID** | DECISION-009 |
| **Date Decided** | 2026-02-02 (v0.0.4d) |
| **Impact Area** | Validation Pipeline (v0.2.4; anti-pattern registry defined in `constants.py`, detection logic deferred) |
| **Provenance** | v0.0.4d §Differentiators and Decision Log |

## Decision

**Anti-pattern detection is implemented in v0.2.4, positioned after generator stability (v0.2.3) but before auto-fix tools (v0.3.0). The anti-pattern registry is defined in v0.1.2 `constants.py`, but detection logic is deferred to v0.2.4.**

## Context

DocStratum aims to provide automated quality feedback on documentation. A critical question is: when should detection tooling be built relative to generation and fixing capabilities?

The answer depends on understanding the cost-benefit tradeoff:
- **Too Early** (v0.1.0): Without a stable baseline of correctly-generated files, detection rules are speculative and prone to false positives
- **Too Late** (v0.3.0): Delays quality feedback to users, allowing bad patterns to accumulate before being caught
- **Just Right** (v0.2.4): After generation is stable and known-good examples exist, detection rules can be grounded in real examples

The decision to implement detection in v0.2.4 reflects a **staged quality improvement approach**:

| Phase | Version | Goal | Deliverable |
|-------|---------|------|-------------|
| Generate | v0.1.0–v0.1.x | Create valid files | Generator produces spec-compliant documentation |
| Stabilize | v0.2.0–v0.2.3 | Refine generation | Generator output is consistent; audit examples collected |
| Detect | v0.2.4 | Find problems | Validator detects anti-patterns with low false-positive rate |
| Lint | v0.2.5 | Offline analysis | Linter CLI tool provides local feedback without full validation |
| Fix | v0.3.0 | Resolve problems | Auto-fix tools correct detected problems |

## Alternatives Considered

| Option | Rationale For | Rationale Against |
|--------|---------------|-------------------|
| v0.1.0 (Immediate Detection) | Early feedback loop; catches problems as they emerge; developers learn standards quickly | Generator output is unproven; detection rules are speculative; high false-positive rate; distracts from getting generator right first |
| **v0.2.4 (After Stabilization, Chosen)** | Stable baseline exists; real examples provide ground truth for rules; detection is grounded and reliable; early enough to prevent accumulation of bad patterns; detection informs v0.3.0 fixes | Delays quality feedback compared to v0.1.0; requires two-phase release cycle |
| v0.3.0 (After Auto-Fix) | Implement detection and fixes together; unified tooling; simpler project structure | Delays quality feedback significantly; accumulation of bad patterns in user docs; fixing before detection risks false "repairs" to valid files |
| v0.3.5+ (Much Later) | No advantages | Unacceptable delay; defeats purpose of automated quality feedback |

## Rationale

v0.2.4 was chosen because it aligns with DocStratum's core value: **learning standards through feedback, not enforcement**.

By v0.2.3, the generator produces stable, valid output. Audit data from v0.0.4c shows consistent patterns: what does correct generation look like? With that baseline, v0.2.4 detection rules can be:
1. **Grounded in Reality**: Rules match actual mistakes observed in documentation, not theoretical problems
2. **Low False-Positive Rate**: Calibrated against known-good examples, reducing noise
3. **Early Enough**: Prevents accumulation of anti-patterns before v0.3.0 fixes are available
4. **Actionable**: Users get feedback with time to correct issues before auto-fix arrives

This staging also provides a **learning opportunity for the project**. v0.2.4 implementation will reveal which anti-patterns are most common and costly. That evidence informs v0.3.0 auto-fix priorities.

## Impact on ASoT

This decision establishes the **timeline for all quality criteria**:

- **v0.2.4+**: All validation criteria (DS-VC-*) become machine-checkable. Files can be validated against the standard.
- **v0.2.4+**: Anti-pattern registry (`constants.py`) is frozen at v0.2.4; further additions require ASoT version bump.
- **v0.3.0+**: Auto-fix rules (DS-AF-*) map to specific anti-patterns and remediation strategies.

The validator (v0.2.4) is built on Pydantic models (DS-DD-006) and schema validation. Detection logic uses the same validation infrastructure as the generator, ensuring consistency.

## Constraints Imposed

1. **Registry Finalization**: The anti-pattern registry in `constants.py` must be finalized and frozen before v0.2.4 release. Post-v0.2.4 changes require ASoT minor version bump (e.g., v0.0.5).
2. **Ground Truth Examples**: v0.2.4 detection rules must be calibrated against documented examples of violations. Every anti-pattern rule must reference at least one real example from audit data.
3. **False-Positive Threshold** [CALIBRATION-NEEDED: target rate]: Detection rules should achieve <5% false-positive rate measured against a holdout test set of v0.2.3 generator output.
4. **Message Quality**: Detected anti-patterns must include actionable messages. Not "invalid" but "Title missing capitalization in section XXX — should be 'Basic Overview' not 'basic overview'".
5. **No Auto-Remediation**: v0.2.4 detection must not automatically fix issues. Reporting only; fixes are v0.3.0+.
6. **Backward Compatibility**: Anti-pattern detection must not break parsing of valid v0.1.x or v0.2.x files. Rules detect problems; they don't reject correct files.

## Related Decisions

- **DS-DD-006** (Pydantic BaseModel used for all detection schemas)
- **DS-DD-001** (Generator/Validator/Fixer architecture — v0.2.4 implements the Validator phase)
- **DS-DD-016** (Severity classification — detected anti-patterns are classified as E/W/I based on this decision)
- **DS-DD-012** (Canonical section names — detection rules validate section structure)

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.3 |
