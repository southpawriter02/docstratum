# v0.3.1d — Link Format Compliance

> **Version:** v0.3.1d
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Parent:** [RR-SPEC-v0.3.1-l1-structural.md](RR-SPEC-v0.3.1-l1-structural.md)
> **Grounding:** DS-VC-STR-005 (Link Format Compliance, 4 pts HARD), v0.0.4a §LNK-001/LNK-002, v0.0.1a ABNF grammar (`link = "-" SP link-entry`)
> **Depends On:** v0.2.0 (`ParsedLlmsTxt.sections`, `ParsedLink`), v0.3.0g (L0 syntactic link check for E006)
> **Module:** `src/docstratum/validation/checks/l1_link_format.py`
> **Tests:** `tests/test_validation_l1_link_format.py`

---

## 1. Purpose

Verify that all links in the document conform to the `[text](url)` format prescribed by the ABNF grammar. While v0.3.0g (L0) catches syntactically _broken_ links (empty/malformed URLs), this L1 check catches **structurally non-conformant** link patterns that the parser could extract but that violate the `llms.txt` specification:

| Check Layer  | What It Catches                                                                        | Code         |
| ------------ | -------------------------------------------------------------------------------------- | ------------ |
| v0.3.0g (L0) | Empty/malformed URL in `[text]()`                                                      | E006 (ERROR) |
| v0.3.1d (L1) | Empty link text in `[](url)`                                                           | E006 (ERROR) |
| v0.3.1d (L1) | Links with valid URL but no wrapping `[text](url)` format detected by parser heuristic | E006 (ERROR) |

### 1.1 Relationship to v0.3.0g

v0.3.0g and v0.3.1d both emit E006, but they check different aspects:

```
v0.3.0g: URL is present and syntactically valid?    (L0 — parseable gate)
v0.3.1d: Link TEXT is present and format is valid?   (L1 — structural compliance)
```

v0.3.0g runs at L0. If L0 passes, v0.3.1d runs at L1 to catch the remaining format violations. A link with a valid URL but empty text passes v0.3.0g but fails v0.3.1d.

### 1.2 Why E006 (Not a New Code)

The E006 code already covers "links with empty or malformed URLs" and "broken link syntax" (DS-DC-E006). Link text absence is in the same diagnostic family — it's a format violation, not a new class of issue. Reusing E006 avoids diagnostic code proliferation while keeping the severity appropriate (ERROR, since empty link text makes the link unnavigable).

---

## 2. Diagnostic Code

| Code | Severity | Message                                              | Remediation                                                                  |
| ---- | -------- | ---------------------------------------------------- | ---------------------------------------------------------------------------- |
| E006 | ERROR    | Section contains links with empty or malformed URLs. | Fix or remove links with empty href values. Ensure all URLs are well-formed. |

> **Note:** The message is the existing E006 message. The `context` field differentiates the specific sub-issue (empty text vs empty URL).

---

## 3. Check Logic

```python
"""L1 link format compliance check.

Verifies that all links have non-empty text components following
the [text](url) ABNF grammar. Complements v0.3.0g which checks
URL validity.

Implements v0.3.1d. Criterion: DS-VC-STR-005.
"""


def check(
    parsed: "ParsedLlmsTxt",
    classification: "DocumentClassification",
    file_meta: "FileMetadata",
) -> list[ValidationDiagnostic]:
    """Check that all links have non-empty text components.

    Iterates over every ParsedLink in every ParsedSection.
    Links with empty or whitespace-only title text violate
    the ABNF grammar requirement for link-entry.

    Args:
        parsed: The parsed file model with sections and links.
        classification: Not used by this check.
        file_meta: Not used by this check.

    Returns:
        List of E006 diagnostics, one per empty-text link.
    """
    diagnostics: list[ValidationDiagnostic] = []

    for section in parsed.sections:
        for link in section.links:
            if not link.title or not link.title.strip():
                diagnostics.append(
                    ValidationDiagnostic(
                        code=DiagnosticCode.E006_BROKEN_LINKS,
                        severity=Severity.ERROR,
                        message=DiagnosticCode.E006_BROKEN_LINKS.message,
                        remediation=DiagnosticCode.E006_BROKEN_LINKS.remediation,
                        level=ValidationLevel.L1_STRUCTURAL,
                        check_id="LNK-002",
                        line_number=link.line_number,
                        context=(
                            f"Link []({{link.url}}) has empty text. "
                            f"Expected: [{link.url.split('/')[-1] if link.url else '?'}]"
                            f"({link.url or '<empty>'})"
                        ),
                    )
                )

    return diagnostics
```

### 3.1 What v0.3.1d Detects (vs What It Does Not)

| Scenario                                           | v0.3.0g (L0)            | v0.3.1d (L1)                       |
| -------------------------------------------------- | ----------------------- | ---------------------------------- |
| `[Title](https://example.com)` — fully valid       | Pass                    | Pass                               |
| `[Title]()` — empty URL                            | E006                    | Not checked (L0 already caught it) |
| `[](https://example.com)` — empty text             | Pass                    | **E006**                           |
| `[  ](https://example.com)` — whitespace-only text | Pass                    | **E006**                           |
| `[Title](bad url)` — malformed URL                 | E006                    | Not checked (L0 already caught it) |
| Bare URL not in Markdown link syntax               | Not extracted by parser | Not detected (parser limitation)   |

> **Note on bare URLs:** The parser only extracts `[text](url)` links. Bare URLs (`https://example.com` without Markdown wrapping) are not represented as `ParsedLink` objects and thus are invisible to both v0.3.0g and v0.3.1d. Detection of bare URLs would require a raw content scan and is deferred to v0.3.4a (anti-pattern detection for AP-CONT-004 Link Desert).

### 3.2 Decision: ERROR Severity at L1

E006 is ERROR severity. This is atypical for L1 (which otherwise emits only WARNINGs via W001, W002, W019, W020). E006 at L1 means **an L1 ERROR exists that can block level progression**.

This is intentional: link format compliance (DS-VC-STR-005) is a HARD criterion. A link with empty text is structurally broken — it provides no navigational information.

### 3.3 Impact on L1 Gate Behavior

With v0.3.1d added, L1 is no longer unconditionally permissive:

```
L1 checks:
  v0.3.1a: W001 (blockquote)    → WARNING
  v0.3.1b: W002 (section names) → WARNING
  v0.3.1c: W019/W020 (structure)→ WARNING
  v0.3.1d: E006 (link text)     → ERROR  ← can block!

If ANY E006 emitted at L1 → levels_passed[L1] = False
```

> [!WARNING]
> This changes the L1 gate dynamics documented in the v0.3.1 scope overview. The scope overview must be updated to reflect that v0.3.1d introduces an ERROR-severity check. L1 no longer "always passes."

---

## 4. Acceptance Criteria

- [ ] `check()` returns empty list when all links have non-empty text.
- [ ] `check()` returns E006 for each link with empty `title`.
- [ ] `check()` returns E006 for each link with whitespace-only `title`.
- [ ] Multiple empty-text links produce multiple E006 diagnostics.
- [ ] E006 uses `level=L1_STRUCTURAL`, `check_id="LNK-002"`.
- [ ] E006 `context` shows the URL and suggests expected text.
- [ ] Links with valid text and valid URL produce no diagnostics.
- [ ] Files with zero links produce zero diagnostics.

---

## 5. Test Plan

### `tests/test_validation_l1_link_format.py`

| Test                              | Input                          | Expected                           |
| --------------------------------- | ------------------------------ | ---------------------------------- |
| `test_all_links_have_text_passes` | 3 links, all with `title`      | `[]`                               |
| `test_empty_title_fails`          | 1 link with `title=""`         | `[E006]`                           |
| `test_whitespace_title_fails`     | 1 link with `title="  "`       | `[E006]`                           |
| `test_none_title_fails`           | 1 link with `title=None`       | `[E006]`                           |
| `test_multiple_empty_text`        | 3 links, 2 empty text          | 2 × E006                           |
| `test_mixed_valid_invalid`        | 2 valid + 1 empty text         | 1 × E006                           |
| `test_no_links_passes`            | Sections but no links          | `[]`                               |
| `test_e006_level_is_l1`           | Empty text link                | E006 with `level=L1_STRUCTURAL`    |
| `test_e006_context_shows_url`     | Link `[](https://example.com)` | `context` contains `"example.com"` |

---

## 6. Design Decisions

| Decision                     | Choice | Rationale                                                       |
| ---------------------------- | ------ | --------------------------------------------------------------- |
| Reuse E006 (not a new code)  | Yes    | Empty link text is the same diagnostic family as broken links   |
| ERROR at L1                  | Yes    | DS-VC-STR-005 is HARD; empty text makes links non-navigable     |
| One E006 per empty-text link | Yes    | Consistent with v0.3.0g (one per broken link)                   |
| Bare URL detection deferred  | Yes    | Parser doesn't extract bare URLs; needs raw scan (v0.3.4a)      |
| `check_id="LNK-002"`         | Yes    | Differentiates from v0.3.0g `check_id="LNK-001"` (URL validity) |
