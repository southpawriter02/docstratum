# Warning Diagnostic Codes Index

> **Parent:** [diagnostics/](../README.md)
> **Severity:** WARNING
> **Code Range:** W001–W018
> **Count:** 18

## Overview

Warning codes represent deviations from best practices that degrade quality but do not break parsing. These map to validation levels L2 (Content Quality) and L3 (Best Practices). Warnings appear in results but do not block level progression (they affect the quality score instead).

## Index

| DS Identifier | Code | Message (first line) | Level | Check ID | Status |
|---------------|------|---------------------|-------|----------|--------|
| DS-DC-W001 | W001 | No blockquote description found after H1 title | L2 | STR-002 (v0.0.4a) | DRAFT |
| DS-DC-W002 | W002 | Section name does not match canonical names | L2 | NAM-001 (v0.0.4a) | DRAFT |
| DS-DC-W003 | W003 | Link entry has no description text | L2 | CNT-004 (v0.0.4b) | DRAFT |
| DS-DC-W004 | W004 | File contains no code examples | L2 | CNT-007 (v0.0.4b) | DRAFT |
| DS-DC-W005 | W005 | Code block without a language specifier | L2 | CNT-008 (v0.0.4b) | DRAFT |
| DS-DC-W006 | W006 | Sections use identical description patterns | L2 | CNT-005 (v0.0.4b) | DRAFT |
| DS-DC-W007 | W007 | No version or last-updated metadata found | L3 | CNT-015 (v0.0.4b) | DRAFT |
| DS-DC-W008 | W008 | Sections do not follow canonical ordering | L2 | STR-004 (v0.0.4a) | DRAFT |
| DS-DC-W009 | W009 | No Master Index found as first H2 section | L2 | STR-003 (v0.0.4a) | DRAFT |
| DS-DC-W010 | W010 | File exceeds recommended token budget for tier | L3 | SIZ-001 (v0.0.4a) | DRAFT |
| DS-DC-W011 | W011 | Sections contain no meaningful content | L2 | CHECK-011 (v0.0.4c) | DRAFT |
| DS-DC-W012 | W012 | Cross-file link references nonexistent file | Ecosystem | v0.0.7 §5.2 | DRAFT |
| DS-DC-W013 | W013 | Project needs llms-full.txt but none exists | Ecosystem | v0.0.7 §5.2 | DRAFT |
| DS-DC-W014 | W014 | llms-full.txt missing content from referenced files | Ecosystem | v0.0.7 §5.2 | DRAFT |
| DS-DC-W015 | W015 | H1 title differs between ecosystem files | Ecosystem | v0.0.7 §5.2 | DRAFT |
| DS-DC-W016 | W016 | Version metadata differs between files | Ecosystem | v0.0.7 §5.2 | DRAFT |
| DS-DC-W017 | W017 | Significant content duplication between files | Ecosystem | v0.0.7 §5.2 | DRAFT |
| DS-DC-W018 | W018 | One file consumes >70% of total ecosystem tokens | Ecosystem | v0.0.7 §5.2 | DRAFT |
