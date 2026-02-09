# DS-AP-STRAT-005: Phantom Reference

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-AP-STRAT-005 |
| **Status** | DRAFT |
| **ASoT Version** | 1.1.0-scaffold |
| **Registry ID** | AP-STRAT-005 |
| **Category** | Strategic |
| **Check ID** | CHECK-023 |
| **Severity Impact** | Deduction penalty — reduces anti-pattern detection dimension score; can cascade into cross-reference integrity failures (IA-016) |
| **Provenance** | Phase E comprehensive audit (2026-02-08) — discovered 6 phantom references across DS-DD-006, DS-DD-008, DS-VC-STR-008, DS-VL-L0, and DS-VL-L1; DS-DD-017 (AI Authoring Workflow) Step 5 and Step 7 guard against this pattern |

## Description

Phantom Reference is an AI-specific strategic anti-pattern where a document contains cross-references to DS-* identifiers that do not exist in the ASoT manifest. This is the documentation equivalent of a "dangling pointer" in software — a reference that resolves to nothing, breaking the integrity of the cross-reference graph.

This anti-pattern is particularly insidious in AI-authored documentation because Large Language Models are prone to generating plausible-sounding identifiers that follow the naming convention but were never actually created. During the Phase E audit of the DocStratum ASoT, six phantom references were discovered across five files — all authored by an AI agent during Phases C and D:

1. **DS-VC-ERR-001** in DS-DD-006: A completely fabricated validation criteria identifier. No `ERR` dimension exists in the VC numbering scheme.
2. **DS-DC-CRIT-001** and **DS-DC-CRIT-002** in DS-VC-STR-008: Diagnostic code identifiers that should have been anti-pattern identifiers (`DS-AP-CRIT-001`, `DS-AP-CRIT-002`). The AI confused the DC and AP prefix conventions.
3. **DS-QS-CAP-structural-gating** in DS-VL-L0 and DS-VL-L1: A quality scoring identifier using a non-standard slug format. The correct identifier was `DS-QS-GATE`.
4. **DS-VC-ENR-001** through **DS-VC-ENR-004** in DS-DD-008: Forward references to validation criteria for a v0.3.x enrichment layer that hasn't been built yet. These were not phantom in intent (the author knew they were future), but they lacked the `*(planned — vX.Y.Z)*` marker that distinguishes legitimate forward references from phantom ones.

The common thread: in every case, the AI agent generated an identifier that *looked right* based on the naming convention but either didn't exist, used the wrong prefix, or referenced a future standard without marking it appropriately.

## Detection Logic

Parse all `DS-{TYPE}-*` identifier patterns from the document body and verify each against the DS-MANIFEST.md File Registry:

```python
import re
from pathlib import Path
from typing import NamedTuple


class PhantomRef(NamedTuple):
    """A cross-reference that doesn't resolve to a registered DS-* identifier."""
    identifier: str
    line_number: int
    context: str  # surrounding text for human review


# Matches DS-{TYPE}-{OPTIONAL_CATEGORY}-{ID} patterns
DS_ID_PATTERN = re.compile(
    r'DS-(?:VC|DC|AP|DD|CN|VL|QS|EH|CS)'
    r'(?:-[A-Z]+)*'
    r'-(?:[A-Z]?\d+|L\d|DIM-[A-Z]+|GATE)',
    re.IGNORECASE
)

# Matches the planned marker that exempts forward references
PLANNED_MARKER = re.compile(
    r'\*\(planned\s*—?\s*v[\d.]+[a-z]?\)\*',
    re.IGNORECASE
)


def detect_phantom_references(
    file_content: str,
    manifest_identifiers: set[str]
) -> list[PhantomRef]:
    """
    Scans a document for DS-* identifiers not in the manifest.

    Args:
        file_content: The full text of the document being checked.
        manifest_identifiers: Set of all DS-* identifiers registered
            in DS-MANIFEST.md File Registry.

    Returns:
        List of PhantomRef tuples for each unresolvable reference.
        Empty list means the document is clean.
    """
    phantoms: list[PhantomRef] = []
    lines = file_content.split('\n')

    for line_num, line in enumerate(lines, start=1):
        # Skip Change History tables (contain historical identifiers)
        if '0.0.0-scaffold' in line or 'Change History' in line:
            continue

        for match in DS_ID_PATTERN.finditer(line):
            identifier = match.group(0).upper()

            # Check if the identifier is in the manifest
            if identifier in manifest_identifiers:
                continue

            # Check if it has a planned marker nearby
            # (within the same line or the immediately following line)
            context_window = line
            if line_num < len(lines):
                context_window += ' ' + lines[line_num]

            if PLANNED_MARKER.search(context_window):
                continue  # legitimate forward reference

            phantoms.append(PhantomRef(
                identifier=identifier,
                line_number=line_num,
                context=line.strip()[:120]
            ))

    return phantoms
```

## Example (Synthetic)

A design decision file that references identifiers that don't exist:

```markdown
# DS-DD-020: Hypothetical Decision

## Impact on ASoT

This decision affects the following validation criteria:
- **DS-VC-STR-001** (H1 Title Present): Correct — exists in manifest
- **DS-VC-SEC-001** (Section Validation): PHANTOM — no "SEC" dimension exists
- **DS-VC-ERR-001** (Error Message Quality): PHANTOM — no "ERR" dimension exists
- **DS-DC-CRIT-001** (Critical Pattern Detected): PHANTOM — should be DS-AP-CRIT-001

The upcoming enrichment layer will define:
- **DS-VC-ENR-001** (Example Presence): PHANTOM — missing planned marker

Correct forward reference format:
- **DS-VC-ENR-001** *(planned — v0.3.x)* (Example Presence): CLEAN
```

In this example, three references are phantom (SEC-001, ERR-001, DC-CRIT-001), one is a phantom that should have a planned marker (ENR-001 without marker), and two are clean (STR-001 exists, ENR-001 with planned marker is a legitimate forward reference).

## Remediation

1. **Verify before writing**: Before including any `DS-*` identifier in a document, check DS-MANIFEST.md File Registry to confirm it exists
2. **Use planned markers for forward references**: If referencing a standard that doesn't exist yet but is planned, use the format `*(planned — vX.Y.Z)*` immediately after the identifier
3. **Fix prefix confusion**: When the identifier uses the wrong type prefix (e.g., `DS-DC-CRIT-*` instead of `DS-AP-CRIT-*`), correct the prefix rather than inventing a new identifier
4. **Remove fabricated identifiers**: If the identifier doesn't correspond to any existing or planned standard, remove the reference entirely and rephrase the surrounding text
5. **Run cross-reference validation**: After authoring, execute DS-DD-017 Step 7 (cross-reference validation) to catch any phantoms programmatically

## Affected Criteria

- DS-VC-APD-005 (No Strategic Anti-Patterns)

## Emitted Diagnostics

None specific — scored through APD dimension. Detection is performed during DS-DD-017 Step 7 (cross-reference validation) and Integrity Assertion IA-016 (cross-reference integrity).

## Related Anti-Patterns

- DS-AP-STRAT-006 (Template Drift): Often co-occurs with Phantom Reference — an AI agent that drifts from the template may also hallucinate identifiers in unfamiliar sections
- DS-AP-CONT-004 (Link Desert): The opposite problem — insufficient cross-references. Phantom Reference is about wrong references; Link Desert is about missing references
- DS-AP-ECO-002 (Phantom Links): The ecosystem-level counterpart — Phantom Links detects many files referencing a section that exists in no file; Phantom Reference detects a single file referencing identifiers that don't exist in the manifest

## Change History

| ASoT Version | Date | Change |
|---|---|---|
| 1.1.0-scaffold | 2026-02-08 | Initial draft — Phase F (AI Authoring Guidelines) |
