# Diagnostic Codes Index

> **Parent:** [standards/](../README.md)
> **Type:** DS-DC-* (Diagnostic Code)
> **Total Expected:** 38 codes (10 Error, 18 Warning, 10 Info)

## Overview

Diagnostic codes are the specific error, warning, and informational messages emitted by the validation pipeline. Each code has a unique identifier, severity level, human-readable message, remediation hint, and mapping to the validation level and criteria that trigger it.

## Severity Groups

| Severity | Directory | Code Range | Count | Description |
|----------|-----------|------------|-------|-------------|
| ERROR | [errors/](errors/) | E001–E010 | 10 | Structural failures that prevent valid parsing |
| WARNING | [warnings/](warnings/) | W001–W018 | 18 | Deviations from best practices |
| INFO | [info/](info/) | I001–I010 | 10 | Observations and suggestions |

## Full Index

| DS Identifier | Code | Severity | Level | Message (first line) | Status |
|---------------|------|----------|-------|---------------------|--------|
| DS-DC-E001 | E001 | ERROR | L1 | No H1 title found | DRAFT |
| DS-DC-E002 | E002 | ERROR | L1 | Multiple H1 titles found | DRAFT |
| DS-DC-E003 | E003 | ERROR | L0 | File is not valid UTF-8 encoding | DRAFT |
| DS-DC-E004 | E004 | ERROR | L0 | File uses non-LF line endings | DRAFT |
| DS-DC-E005 | E005 | ERROR | L0 | File contains invalid Markdown syntax | DRAFT |
| DS-DC-E006 | E006 | ERROR | L1 | Links with empty or malformed URLs | DRAFT |
| DS-DC-E007 | E007 | ERROR | L0 | File is empty or contains only whitespace | DRAFT |
| DS-DC-E008 | E008 | ERROR | L0 | File exceeds maximum recommended size | DRAFT |
| DS-DC-E009 | E009 | ERROR | Ecosystem | Ecosystem has no llms.txt file | DRAFT |
| DS-DC-E010 | E010 | ERROR | Ecosystem | Ecosystem file not referenced by any other file | DRAFT |
| DS-DC-W001 | W001 | WARNING | L2 | No blockquote description found after H1 title | DRAFT |
| DS-DC-W002 | W002 | WARNING | L2 | Section name does not match canonical names | DRAFT |
| DS-DC-W003 | W003 | WARNING | L2 | Link entry has no description text | DRAFT |
| DS-DC-W004 | W004 | WARNING | L2 | File contains no code examples | DRAFT |
| DS-DC-W005 | W005 | WARNING | L2 | Code block without a language specifier | DRAFT |
| DS-DC-W006 | W006 | WARNING | L2 | Sections use identical description patterns | DRAFT |
| DS-DC-W007 | W007 | WARNING | L3 | No version or last-updated metadata found | DRAFT |
| DS-DC-W008 | W008 | WARNING | L2 | Sections do not follow canonical ordering | DRAFT |
| DS-DC-W009 | W009 | WARNING | L2 | No Master Index found as first H2 section | DRAFT |
| DS-DC-W010 | W010 | WARNING | L3 | File exceeds recommended token budget for tier | DRAFT |
| DS-DC-W011 | W011 | WARNING | L2 | Sections contain no meaningful content | DRAFT |
| DS-DC-W012 | W012 | WARNING | Ecosystem | Cross-file link references nonexistent file | DRAFT |
| DS-DC-W013 | W013 | WARNING | Ecosystem | Project needs llms-full.txt but none exists | DRAFT |
| DS-DC-W014 | W014 | WARNING | Ecosystem | llms-full.txt missing content from referenced files | DRAFT |
| DS-DC-W015 | W015 | WARNING | Ecosystem | H1 title differs between ecosystem files | DRAFT |
| DS-DC-W016 | W016 | WARNING | Ecosystem | Version metadata differs between files | DRAFT |
| DS-DC-W017 | W017 | WARNING | Ecosystem | Significant content duplication between files | DRAFT |
| DS-DC-W018 | W018 | WARNING | Ecosystem | One file consumes >70% of total ecosystem tokens | DRAFT |
| DS-DC-I001 | I001 | INFO | L4 | No LLM Instructions section found | DRAFT |
| DS-DC-I002 | I002 | INFO | L4 | No structured concept definitions found | DRAFT |
| DS-DC-I003 | I003 | INFO | L4 | No few-shot Q&A examples found | DRAFT |
| DS-DC-I004 | I004 | INFO | L4 | Relative URLs found in link entries | DRAFT |
| DS-DC-I005 | I005 | INFO | L4 | File classified as Type 2 Full | DRAFT |
| DS-DC-I006 | I006 | INFO | L4 | Optional sections not explicitly marked | DRAFT |
| DS-DC-I007 | I007 | INFO | L4 | Domain-specific jargon without definition | DRAFT |
| DS-DC-I008 | I008 | INFO | Ecosystem | No llms-instructions.txt or LLM Instructions section | DRAFT |
| DS-DC-I009 | I009 | INFO | Ecosystem | Index references categories with no detail page | DRAFT |
| DS-DC-I010 | I010 | INFO | Ecosystem | Ecosystem consists of just llms.txt | DRAFT |
