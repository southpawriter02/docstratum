# DS-AP-STRAT-006: Template Drift

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-AP-STRAT-006 |
| **Status** | DRAFT |
| **ASoT Version** | 1.1.0-scaffold |
| **Registry ID** | AP-STRAT-006 |
| **Category** | Strategic |
| **Check ID** | CHECK-024 |
| **Severity Impact** | Deduction penalty — reduces anti-pattern detection dimension score; undermines machine-parseability and ASoT consistency |
| **Provenance** | Phase E comprehensive audit (2026-02-08) — discovered QS dimension files with wrong criteria tables, DD files with fabricated section names; DS-DD-019 (Guided Flexibility Authoring Model) defines the authoritative template requirements |

## Description

Template Drift is an AI-specific strategic anti-pattern where an authored DS-* standard file deviates from the established template for its element type. Deviations include missing required sections, wrong metadata fields, sections in non-standard order, inconsistent formatting, or sections that don't match the type's specification.

This anti-pattern is distinct from content quality issues. A file with Template Drift may contain excellent prose — but if it's missing the `## Emitted Diagnostics` section that all VC files require, or if its metadata table uses `Decision Number` instead of `Decision ID`, it breaks the structural contract that downstream tools and human reviewers depend on.

During the Phase E audit, Template Drift manifested in several forms:

1. **QS dimension files with stale criteria tables** (DS-QS-DIM-STR, DS-QS-DIM-CON, DS-QS-DIM-APD): The criteria tables listed criteria that didn't match the actual VC files. The AI agent used an earlier draft as the template rather than verifying against the authoritative VC files — a form of structural drift where the section content contradicts the standard it represents.

2. **APD dimension with wrong scoring model** (DS-QS-DIM-APD): The file described a deduction-based scoring model when the actual model is criterion-based (additive). The agent propagated a template assumption that was fundamentally incorrect for this specific dimension.

3. **Inconsistent metadata field names**: Some files used `**Decision ID**` while the template specified `**Decision ID**` with specific bold-pipe formatting. While cosmetically minor, inconsistent field names break automated metadata extraction.

Template Drift is a strategic anti-pattern rather than a structural one because it reflects a *process failure* — the author didn't follow the authoring workflow (DS-DD-017) — rather than a *content failure*. The fix is process-level: follow the template, not "write better content."

## Detection Logic

Compare the authored file's section structure against the required-sections specification for its element type (as defined in DS-DD-019's MUST tier):

```python
import re
from typing import NamedTuple


class DriftViolation(NamedTuple):
    """A specific template compliance violation."""
    violation_type: str  # "missing_section", "extra_metadata", "wrong_order"
    expected: str
    actual: str
    severity: str  # "MUST" or "SHOULD"


# Required sections per element type (from DS-DD-019 MUST tier)
REQUIRED_SECTIONS: dict[str, list[str]] = {
    "VC": [
        "Description", "Pass Condition", "Fail Condition",
        "Emitted Diagnostics", "Related Criteria",
        "Calibration Notes", "Change History"
    ],
    "DC": [
        "Description", "Trigger Condition", "Severity",
        "Emitted By", "Resolution", "Change History"
    ],
    "AP": [
        "Description", "Detection Logic", "Example (Synthetic)",
        "Remediation", "Affected Criteria", "Change History"
    ],
    "DD": [
        "Decision", "Context", "Alternatives Considered",
        "Rationale", "Impact on ASoT", "Constraints Imposed",
        "Related Decisions", "Change History"
    ],
    "CN": [
        "Description", "Purpose", "Detection", "Aliases",
        "Related Sections", "Change History"
    ],
    "VL": [
        "Description", "Criteria at This Level", "Entry Conditions",
        "Exit Criteria", "Scoring Impact", "Change History"
    ],
    "QS": [
        "Description", "Specification", "Change History"
    ],
    "EH": [
        "Description", "Metric Definition", "Measurement",
        "Thresholds", "Related Patterns", "Change History"
    ],
    "CS": [
        "Description", "Source", "Scores",
        "Analysis", "Change History"
    ],
}

# Required metadata fields (universal)
UNIVERSAL_METADATA = ["DS Identifier", "Status", "ASoT Version"]


def detect_template_drift(
    file_content: str,
    element_type: str
) -> list[DriftViolation]:
    """
    Checks a DS-* file against its type's required template.

    Args:
        file_content: The full text of the DS-* standard file.
        element_type: One of "VC", "DC", "AP", "DD", "CN",
            "VL", "QS", "EH", "CS".

    Returns:
        List of DriftViolation tuples. Empty list means
        the file is template-compliant.
    """
    violations: list[DriftViolation] = []

    if element_type not in REQUIRED_SECTIONS:
        violations.append(DriftViolation(
            violation_type="unknown_type",
            expected=f"One of {list(REQUIRED_SECTIONS.keys())}",
            actual=element_type,
            severity="MUST"
        ))
        return violations

    # Extract H2 section headings from the file
    h2_pattern = re.compile(r'^## (.+)$', re.MULTILINE)
    actual_sections = [m.group(1).strip() for m in h2_pattern.finditer(file_content)]

    # Check for missing required sections
    required = REQUIRED_SECTIONS[element_type]
    for section in required:
        if section not in actual_sections:
            violations.append(DriftViolation(
                violation_type="missing_section",
                expected=f"## {section}",
                actual="(not found)",
                severity="MUST"
            ))

    # Check for required metadata fields
    for field in UNIVERSAL_METADATA:
        if field not in file_content:
            violations.append(DriftViolation(
                violation_type="missing_metadata",
                expected=f"| **{field}** |",
                actual="(not found)",
                severity="MUST"
            ))

    # Check for Change History table
    if "| ASoT Version | Date | Change |" not in file_content:
        violations.append(DriftViolation(
            violation_type="missing_change_history_table",
            expected="Standard Change History table format",
            actual="(not found or non-standard format)",
            severity="MUST"
        ))

    return violations
```

## Example (Synthetic)

A validation criteria file with Template Drift:

```markdown
# DS-VC-STR-010: Hypothetical Criterion

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VC-STR-010 |
| **Status** | DRAFT |
| **ASoT Version** | 1.1.0-scaffold |
| **Weight** | 3 / 30 structural points |

## Overview                      ← DRIFT: should be "## Description"

This criterion checks for hypothetical structural properties.

## How It Works                  ← DRIFT: non-standard section name

The check operates by scanning...

## When It Fails                 ← DRIFT: should be "## Fail Condition"

Failure occurs when...

## Change History                ← OK: present and correct

| ASoT Version | Date | Change |
|--------------|------|--------|
| 1.1.0-scaffold | 2026-02-08 | Initial draft |
```

**Missing required sections**: Pass Condition, Fail Condition (wrong name used), Emitted Diagnostics, Related Criteria, Calibration Notes

**Non-standard sections**: "Overview" (should be "Description"), "How It Works" (not in template), "When It Fails" (should be "Fail Condition")

**Missing metadata**: Platinum ID, Dimension, Level, Pass Type, Measurability, Provenance

## Remediation

1. **Read the type template before writing**: DS-DD-017 Step 3 (read same-type exemplar) exists specifically to prevent Template Drift. Follow it.
2. **Consult DS-DD-019 MUST tier**: The authoritative list of required sections per type is in DS-DD-019's Impact on ASoT section. When in doubt, check that table.
3. **Add missing sections**: Insert any required sections that are absent. Even if a section has minimal content (e.g., "## Emitted Diagnostics\n\nNone specific — scored through dimension."), its presence maintains template compliance.
4. **Rename non-standard sections**: If a section covers the right topic but uses the wrong heading, rename it to match the template (e.g., "Overview" → "Description", "When It Fails" → "Fail Condition").
5. **Verify metadata fields**: Compare the file's metadata table against other files of the same type. All type-specific fields must be present.
6. **Run self-verification checklist**: DS-DD-017 Step 5 includes MUST-tier section verification. Use it before declaring the file complete.

## Affected Criteria

- DS-VC-APD-005 (No Strategic Anti-Patterns)

## Emitted Diagnostics

None specific — scored through APD dimension. Detection is performed during DS-DD-017 Step 5 (pre-integration checklist) and can be automated as part of manifest integrity assertions.

## Related Anti-Patterns

- DS-AP-STRAT-005 (Phantom Reference): Often co-occurs — an agent that drifts from the template may also hallucinate identifiers to fill unfamiliar sections
- DS-AP-STRUCT-005 (Naming Nebula): The llms.txt counterpart — Naming Nebula detects non-canonical section names in end-user documentation; Template Drift detects non-standard sections in DS-* standard files
- DS-AP-CONT-007 (Formulaic Description): The opposite extreme — Formulaic Description is about content being too generic, while Template Drift is about structure being too creative. The Guided Flexibility model (DS-DD-019) balances these: MUST-tier structure with MAY-tier content

## Change History

| ASoT Version | Date | Change |
|---|---|---|
| 1.1.0-scaffold | 2026-02-08 | Initial draft — Phase F (AI Authoring Guidelines) |
