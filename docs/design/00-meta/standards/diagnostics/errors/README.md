# Error Diagnostic Codes Index

> **Parent:** [diagnostics/](../README.md)
> **Severity:** ERROR
> **Code Range:** E001–E010
> **Count:** 10

## Overview

Error codes represent structural failures that prevent valid parsing or break spec conformance. These map to validation levels L0 (Parseable) and L1 (Structural). When an error fires, it indicates a fundamental problem that blocks progression to higher validation levels.

## Index

| DS Identifier | Code | Message (first line) | Level | Check ID | Status |
|---------------|------|---------------------|-------|----------|--------|
| DS-DC-E001 | E001 | No H1 title found | L1 | STR-001 (v0.0.4a) | DRAFT |
| DS-DC-E002 | E002 | Multiple H1 titles found | L1 | STR-001 (v0.0.4a) | DRAFT |
| DS-DC-E003 | E003 | File is not valid UTF-8 encoding | L0 | ENC-001 (v0.0.4a) | DRAFT |
| DS-DC-E004 | E004 | File uses non-LF line endings | L0 | ENC-002 (v0.0.4a) | DRAFT |
| DS-DC-E005 | E005 | File contains invalid Markdown syntax | L0 | MD-001 (v0.0.4a) | DRAFT |
| DS-DC-E006 | E006 | Links with empty or malformed URLs | L1 | LNK-002 (v0.0.4a) | DRAFT |
| DS-DC-E007 | E007 | File is empty or contains only whitespace | L0 | CHECK-001 (v0.0.4c) | DRAFT |
| DS-DC-E008 | E008 | File exceeds maximum recommended size | L0 | SIZ-003 (v0.0.4a) | DRAFT |
| DS-DC-E009 | E009 | Ecosystem has no llms.txt file | Ecosystem | v0.0.7 §5.1 | DRAFT |
| DS-DC-E010 | E010 | Ecosystem file not referenced by any other file | Ecosystem | v0.0.7 §5.1 | DRAFT |
