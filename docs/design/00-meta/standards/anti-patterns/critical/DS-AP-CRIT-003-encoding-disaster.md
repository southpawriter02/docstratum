# DS-AP-CRIT-003: Encoding Disaster

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-AP-CRIT-003 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Registry ID** | AP-CRIT-003 |
| **Category** | Critical |
| **Check ID** | CHECK-003 (v0.0.4c) |
| **Severity Impact** | Gate structural score at 29 — total quality score capped regardless of other dimensions |
| **Provenance** | v0.0.4c §Anti-Patterns Catalog; v0.0.4a §ENC-001, §ENC-002 |

## Description

Non-UTF-8 encoding or mixed line endings that break parsers. File may contain BOM markers, Windows CRLF line endings, Latin-1 or other legacy encodings that cause UnicodeDecodeError or garbled text when processed by tools expecting UTF-8.

## Detection Logic

```python
def detect_encoding_disaster(file_path: str) -> bool:
    """
    Detect invalid encoding or problematic line endings.
    
    Returns True if:
    - UTF-8 decode fails (UnicodeDecodeError), OR
    - BOM marker detected (EF BB BF), OR
    - CR (0x0D) bytes found indicating non-LF line endings
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        return True
    
    with open(file_path, 'rb') as f:
        raw_bytes = f.read()
    
    # Check for BOM
    if raw_bytes.startswith(b'\xef\xbb\xbf'):
        return True
    
    # Check for CR (CRLF or non-LF line endings)
    if b'\r' in raw_bytes:
        return True
    
    return False
```

## Example (Synthetic)

A file encoded in Latin-1 (cp1252) containing accented characters:
```
Café documentation — élève guide
Résumé: This file was saved with Windows cp1252 encoding
```

When processed by UTF-8 parser expecting: `with open(file, 'r', encoding='utf-8')` — UnicodeDecodeError raised.

## Remediation

1. Convert file to UTF-8 without BOM using `iconv`:
   ```bash
   iconv -f ISO-8859-1 -t UTF-8 input.md > output.md
   ```

2. Normalize line endings to LF:
   ```bash
   dos2unix filename.md
   # or
   sed -i 's/\r$//' filename.md
   ```

3. Verify result:
   ```bash
   file filename.md  # should show "UTF-8 Unicode text"
   ```

## Affected Criteria

- DS-VC-STR-008 (No Critical Anti-Patterns)

## Emitted Diagnostics

- **DS-DC-E003**: INVALID_ENCODING — non-UTF-8 content detected
- **DS-DC-E004**: INVALID_LINE_ENDINGS — non-LF line endings detected

## Related Anti-Patterns

- DS-AP-STRAT-001 (Automation Obsession — auto-generated files often have encoding issues)

## Change History

| ASoT Version | Date | Change |
|---|---|---|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.2 |
