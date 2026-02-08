# DS-VC-STR-005: Link Format Compliance

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VC-STR-005 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Platinum ID** | L1-05 |
| **Dimension** | Structural (30%) |
| **Level** | L1 — Structurally Valid |
| **Weight** | 4 / 30 structural points |
| **Pass Type** | HARD |
| **Measurability** | Fully measurable |
| **Provenance** | Official llms.txt spec: link list format `[title](url): description`; v0.0.1a formal grammar |

## Description

This criterion enforces that all links within the llms.txt file conform to valid Markdown link syntax: `[text](url)`. The llms.txt specification defines links as structured elements with a title/text component (in square brackets) and a URL component (in parentheses). Links may be followed by a colon and optional description.

Adherence to Markdown link syntax is foundational for automated parsing. AI agents rely on consistent link structure to extract reference information, verify URLs, and build dependency graphs. When links use non-standard formats—bare URLs without brackets, malformed Markdown, HTML `<a>` tags instead of Markdown syntax, or empty URL slots—parsers either skip the links or misinterpret them, degrading the document's utility.

This criterion checks **syntactic correctness** of links only. Whether a URL is semantically valid (non-empty, resolvable) is checked separately by DS-VC-CON-002 (URL Resolvability). URL *resolution* (HTTP 200 status) is a content-level concern; syntax is a structural concern.

## Pass Condition

All links within the file use valid Markdown link syntax `[text](url)`, with non-empty text and non-empty URL components:

```python
links = extract_markdown_links(file_content)  # Extracts [text](url) pairs
for link in links:
    assert link.text and link.text.strip(), "Link text must not be empty"
    assert link.url and link.url.strip(), "Link URL must not be empty"
    assert is_valid_url_syntax(link.url), "URL must be syntactically valid (no spaces, valid scheme if present)"
```

Valid URL syntax includes:
- Relative URLs: `../docs/api`, `/references/index`
- Absolute URLs with scheme: `https://example.com`, `http://docs.example.com/guide`
- URLs without scheme (inferred as relative): `docs/api-reference`
- No whitespace within the URL component

## Fail Condition

Links exhibit syntactic violations:

- **Empty URL slots:** `[Link text]()` — parentheses present but no URL
- **Empty text slots:** `[](https://example.com)` — square brackets present but no text
- **Malformed Markdown:** Missing brackets: `Link text (https://example.com)`, missing parentheses: `[Link text] https://example.com`
- **Bare URLs without Markdown:** Text containing `https://example.com` not wrapped in Markdown link syntax
- **HTML anchor tags:** `<a href="...">text</a>` instead of Markdown `[text](url)`
- **Whitespace in URL:** `[text]( https://example.com )` — spaces within the URL component (though some parsers tolerate leading/trailing whitespace in parentheses, this is not canonical)
- **Invalid URL syntax:** URLs with unencoded spaces: `[text](https://example.com/my document)`, or other characters that violate URI syntax

## Emitted Diagnostics

- **DS-DC-E006** (ERROR): Emitted when links with empty or malformed URLs are detected

## Related Anti-Patterns

- **DS-AP-CRIT-004** (Link Void): Files where all or most links are broken/malformed, rendering the link sections useless.
- **DS-AP-CONT-004** (Link Desert): Bare URL lists without Markdown link syntax or descriptions; related to format violations.

## Related Criteria

- **DS-VC-CON-001** (Non-empty Descriptions): Checks that the optional description part of links (after the colon) contains meaningful content.
- **DS-VC-CON-002** (URL Resolvability): Verifies that syntactically valid URLs are semantically resolvable (HTTP requests succeed).
- **DS-VC-STR-001** (H1 Title Present) through DS-VC-STR-004 (H2 Section Structure): Establish the document's hierarchical structure; links are elements within that structure.

## Calibration Notes

- **E006 fires for syntactic link issues**
- Most published llms.txt files use valid Markdown link syntax
- Auto-generated files occasionally produce malformed links:
  - Example: Flask auto-doc generator previously exported bare URLs
  - Example: Some Jupyter-to-Markdown exporters produce HTML anchors instead of Markdown links
- Svelte, Pydantic, Cursor, FastAPI: All use valid Markdown link syntax throughout
- NVIDIA llms.txt (score 24): Contains E006-triggering malformed links, contributing to its structural deficit
- Bare URL rate in audited files: ~10% of files with links exhibit at least one bare URL

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase C |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
