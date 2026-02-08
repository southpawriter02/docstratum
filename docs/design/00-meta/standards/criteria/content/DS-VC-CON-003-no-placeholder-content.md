# DS-VC-CON-003: No Placeholder Content

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VC-CON-003 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Platinum ID** | L2-03 |
| **Dimension** | Content (50%) |
| **Level** | L2 — Content Quality |
| **Weight** | 3 / 50 content points |
| **Pass Type** | SOFT |
| **Measurability** | Fully measurable |
| **Provenance** | v0.0.4c anti-pattern catalog; v0.0.2b: 3 of 24 audited files contained placeholder content; AP-CONT-002 (Blank Canvas) |

## Description

This criterion verifies that the documentation does not contain placeholder text or template markers indicating incomplete or unfinished sections. Placeholder content signals that the file has not been reviewed for publication and diminishes user trust.

Common placeholder patterns include `TODO`, `FIXME`, `XXX`, `Lorem ipsum`, templated markers like `[INSERT HERE]`, and framework-generated stubs like `<your text here>`. When present, these patterns indicate the documentation is a draft or template rather than a finished product.

The v0.0.2b audit found that 3 of 24 audited files (12.5%) contained placeholder content. While this is relatively uncommon, its presence is severe — it signals incomplete or abandoned documentation. When discovered, placeholder content typically appears alongside other quality issues.

This criterion is fully measurable via pattern matching and can be applied offline without network access.

## Pass Condition

No placeholder patterns detected anywhere in the file content:

```python
PLACEHOLDER_PATTERNS = [
    r'\bTODO\b', r'\bFIXME\b', r'\bXXX\b',
    r'Lorem ipsum', r'\[INSERT.*?\]', r'\[PLACEHOLDER\]',
    r'\[TBD\]', r'<your.*?here>', r'example\.com',
    r'foo\.bar', r'placeholder'
]
for pattern in PLACEHOLDER_PATTERNS:
    assert not re.search(pattern, content, re.IGNORECASE)
```

The check is case-insensitive to catch variations like `todo`, `Todo`, and `TODO`.

## Fail Condition

One or more placeholder patterns found anywhere in the file. Any match triggers criterion failure.

**Edge cases:**
- `example.com` in a code example showing URL format (e.g., "Use the format `https://example.com/api`") might semantically be acceptable. A context-aware heuristic should check whether `example.com` appears in a code block or as documentation for URL structure — if so, it may be whitelisted.
- Placeholder patterns in code samples or literal blocks may be legitimate (e.g., a tutorial showing a `TODO` comment in sample code). The validator may need to distinguish between Markdown code blocks and general content.

## Emitted Diagnostics

None directly. Placeholder detection is covered by anti-pattern **DS-AP-CONT-002** (Blank Canvas) in the anti-pattern detection pipeline rather than emitting a standalone diagnostic code.

## Related Anti-Patterns

- **DS-AP-CONT-002** (Blank Canvas): Sections with placeholder text, template markers, or no meaningful content. Detecting placeholders is the primary signal for this anti-pattern.

## Related Criteria

- **DS-VC-CON-004** (Non-empty Sections): Empty sections (lacking content) are a related but distinct issue from placeholder content. A section might have placeholder text and thus be "non-empty" but semantically useless.
- **DS-VC-CON-006** (Substantive Blockquote): Blockquotes containing placeholder text would fail both criteria — first for being placeholder content, and second for not being substantive.

## Calibration Notes

The v0.0.2b audit found placeholder content in 12.5% of sampled files, making it relatively uncommon but important to detect. This is often a signal of auto-generated documentation or incompletely drafted files.

The PLACEHOLDER_PATTERNS list should be refined based on patterns discovered in the 11 empirical specimens. Additional patterns (e.g., locale-specific placeholder strings) may emerge during Phase C calibration.

The `example.com` and `foo.bar` patterns are included because they commonly appear as placeholder URLs in documentation templates, though context-aware filtering may reduce false positives.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase C |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
