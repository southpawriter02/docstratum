# DS-VC-CON-001: Non-empty Link Descriptions

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VC-CON-001 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Platinum ID** | L2-01 |
| **Dimension** | Content (50%) |
| **Level** | L2 — Content Quality |
| **Weight** | 5 / 50 content points [CALIBRATION-NEEDED] |
| **Pass Type** | SOFT |
| **Measurability** | Fully measurable |
| **Provenance** | v0.0.4b CHECK-CNT-003; v0.0.2c audit: files with descriptions score 23% higher; v0.0.2c: descriptions have r~0.45 quality correlation |

## Description

This criterion ensures that links within the documentation include meaningful descriptions. Rather than bare URLs with no context, links should contain the `: description` part that explains to readers why they should follow the link. Link descriptions are a signal of curation and human attention to the documentation experience.

Links are fundamental navigational elements in llms.txt files. A bare URL (e.g., `[https://example.com]`) provides no semantic information to the reader, whereas a descriptive link (e.g., `[Example Site: comprehensive reference guide]`) immediately communicates the link's purpose. The v0.0.2c audit found that files with descriptive links score 23% higher overall and show a quality correlation of r~0.45 with description presence.

This criterion measures the proportion of links that have substantive descriptions (non-whitespace text after the URL). A documentation file should not force readers to click blind. The criterion is lenient with small files (1–2 links) but enforces a meaningful proportion for larger collections.

## Pass Condition

A sufficient proportion of links include non-empty description text after the URL:

```python
links = extract_all_markdown_links(content)
descriptions_with_text = [
    link for link in links
    if link.description and link.description.strip()
]
description_ratio = len(descriptions_with_text) / len(links) if links else 1.0
assert description_ratio >= 0.5  # [CALIBRATION-NEEDED: threshold]
```

**Edge case handling:** Files with 1–2 total links are evaluated more leniently — a single bare link does not automatically fail the criterion. The description must be more than whitespace (i.e., `.strip()` must return non-empty string).

## Fail Condition

More than half of the links in the file are bare URLs with no description text. A single bare link does not fail the criterion; the criterion evaluates the overall pattern.

- Example failure pattern: a file with 10 links where 7 are bare URLs (70% bare) would fail.
- Example pass pattern: a file with 10 links where 4 are bare URLs (40% bare) would pass.

Edge case: files with only 1–2 links receive implicit leniency because sample sizes are too small to determine a robust pattern.

## Emitted Diagnostics

- **DS-DC-W003** (WARNING): Link entry has no description text (bare URL only). Fires per-link, not per-file, allowing for granular visibility into which links lack descriptions.

## Related Anti-Patterns

- **DS-AP-CONT-004** (Link Desert): An area within the documentation consisting primarily of bare links with no descriptions, creating a poor user experience and reducing link discoverability.

## Related Criteria

- **DS-VC-STR-005** (Link Format Compliance): Checks link syntax correctness; DS-VC-CON-001 checks link content quality. A link can be syntactically valid but still lack a description.
- **DS-VC-CON-007** (No Formulaic Descriptions): Descriptions must exist AND be substantive. CON-001 enforces existence; CON-007 enforces variety and meaning.

## Calibration Notes

v0.0.2c empirical data shows description presence correlates with quality at r~0.45:

- **DS-CS-001 (Svelte):** 92/92 links have descriptions — 100% descriptive (EXEMPLAR).
- **DS-CS-002 (Pydantic):** 87/89 links have descriptions — 97.8% descriptive.
- Files scoring below 50 typically have >60% bare links.

The 50% threshold [CALIBRATION-NEEDED] should be refined against the 11 empirical specimens once Phase C scoring is complete.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase C |
