# Validation Criteria Index

> **Parent:** [standards/](../README.md)
> **Type:** DS-VC-* (Validation Criterion)
> **Total Expected:** 30 criteria across 3 dimensions

## Overview

Validation criteria define the specific checks that the DocStratum pipeline runs against llms.txt files. Each criterion has an unambiguous pass/fail condition, a quality dimension assignment, a scoring weight, and cross-references to the diagnostic codes it emits.

## Dimensions

| Dimension | Directory | Weight | Criteria Count |
|-----------|-----------|--------|----------------|
| Structural | [structural/](structural/) | 30% (30 points) | 9 |
| Content | [content/](content/) | 50% (50 points) | 13 |
| Anti-Pattern Detection | [anti-pattern/](anti-pattern/) | 20% (20 points) | 8 |

## Full Index

| DS Identifier | Platinum ID | Name | Dimension | Level | Status |
|---------------|-------------|------|-----------|-------|--------|
| DS-VC-STR-001 | L1-01 | H1 Title Present | Structural | L1 | DRAFT |
| DS-VC-STR-002 | L1-02 | Single H1 Only | Structural | L1 | DRAFT |
| DS-VC-STR-003 | L1-03 | Blockquote Present | Structural | L1 | DRAFT |
| DS-VC-STR-004 | L1-04 | H2 Section Structure | Structural | L1 | DRAFT |
| DS-VC-STR-005 | L1-05 | Link Format Compliance | Structural | L1 | DRAFT |
| DS-VC-STR-006 | L1-06 | No Heading Violations | Structural | L1 | DRAFT |
| DS-VC-STR-007 | L3-06 | Canonical Section Ordering | Structural | L3 | DRAFT |
| DS-VC-STR-008 | L3-09 | No Critical Anti-Patterns | Structural | L3 | DRAFT |
| DS-VC-STR-009 | L3-10 | No Structural Anti-Patterns | Structural | L3 | DRAFT |
| DS-VC-CON-001 | L2-01 | Non-empty Descriptions | Content | L2 | DRAFT |
| DS-VC-CON-002 | L2-02 | URL Resolvability | Content | L2 | DRAFT |
| DS-VC-CON-003 | L2-03 | No Placeholder Content | Content | L2 | DRAFT |
| DS-VC-CON-004 | L2-04 | Non-empty Sections | Content | L2 | DRAFT |
| DS-VC-CON-005 | L2-05 | No Duplicate Sections | Content | L2 | DRAFT |
| DS-VC-CON-006 | L2-06 | Substantive Blockquote | Content | L2 | DRAFT |
| DS-VC-CON-007 | L2-07 | No Formulaic Descriptions | Content | L2 | DRAFT |
| DS-VC-CON-008 | L3-01 | Canonical Section Names | Content | L3 | DRAFT |
| DS-VC-CON-009 | L3-02 | Master Index Present | Content | L3 | DRAFT |
| DS-VC-CON-010 | L3-03 | Code Examples Present | Content | L3 | DRAFT |
| DS-VC-CON-011 | L3-04 | Code Language Specifiers | Content | L3 | DRAFT |
| DS-VC-CON-012 | L3-05 | Token Budget Respected | Content | L3 | DRAFT |
| DS-VC-CON-013 | L3-07 | Version Metadata Present | Content | L3 | DRAFT |
| DS-VC-APD-001 | L4-01 | LLM Instructions Section | Anti-Pattern | L4 | DRAFT |
| DS-VC-APD-002 | L4-02 | Concept Definitions | Anti-Pattern | L4 | DRAFT |
| DS-VC-APD-003 | L4-03 | Few-shot Examples | Anti-Pattern | L4 | DRAFT |
| DS-VC-APD-004 | L4-04 | No Content Anti-Patterns | Anti-Pattern | L4 | DRAFT |
| DS-VC-APD-005 | L4-05 | No Strategic Anti-Patterns | Anti-Pattern | L4 | DRAFT |
| DS-VC-APD-006 | L4-06 | Token-optimized Structure | Anti-Pattern | L4 | DRAFT |
| DS-VC-APD-007 | L4-07 | Relative URL Minimization | Anti-Pattern | L4 | DRAFT |
| DS-VC-APD-008 | L4-08 | Jargon Defined or Linked | Anti-Pattern | L4 | DRAFT |
