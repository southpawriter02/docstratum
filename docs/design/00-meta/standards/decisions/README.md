# Design Decisions Index

> **Parent:** [standards/](../README.md)
> **Type:** DS-DD-* (Design Decision)
> **Total Expected:** 16 decisions (DECISION-001 through DECISION-016)

## Overview

Design decisions document the inherited constraints from the v0.0.x research phase that govern how the validation engine is built. Each decision records the choice made, the alternatives considered, the rationale, and the impact on validation criteria and scoring.

## Index

| DS Identifier | Decision ID | Title | Impact Area | Status |
|---------------|-------------|-------|-------------|--------|
| DS-DD-001 | DECISION-001 | Markdown over JSON/YAML | Schema Models | DRAFT |
| DS-DD-002 | DECISION-002 | 3-Layer Architecture | Content Structure (v0.3.x) | DRAFT |
| DS-DD-003 | DECISION-003 | GFM as Standard | Parser (mistletoe) | DRAFT |
| DS-DD-004 | DECISION-004 | Concept ID Format | Content Enrichment (enrichment.py) | DRAFT |
| DS-DD-005 | DECISION-005 | Typed Directed Relationships | Content Enrichment (RelationshipType) | DRAFT |
| DS-DD-006 | DECISION-006 | Pydantic for Schema Validation | All Schema Models | DRAFT |
| DS-DD-007 | DECISION-007 | CSV for Relationship Matrices | Content Structure (v0.3.x) | DRAFT |
| DS-DD-008 | DECISION-008 | Example IDs Linked to Concepts | Content Enrichment (FewShotExample) | DRAFT |
| DS-DD-009 | DECISION-009 | Anti-Pattern Detection in v0.2.4 | Validation Pipeline (v0.2.4) | DRAFT |
| DS-DD-010 | DECISION-010 | Master Index Priority | Content Criteria / Scoring | DRAFT |
| DS-DD-011 | DECISION-011 | Optional Sections Explicitly Marked | Validation Pipeline (I006) | DRAFT |
| DS-DD-012 | DECISION-012 | Canonical Section Names | Constants (CanonicalSectionName) | DRAFT |
| DS-DD-013 | DECISION-013 | Token Budget Tiers | Constants (TOKEN_BUDGET_TIERS) | DRAFT |
| DS-DD-014 | DECISION-014 | Content Quality Primary Weight | Scoring / Quality | DRAFT |
| DS-DD-015 | DECISION-015 | MCP as Target Consumer | Entire Validation Philosophy | DRAFT |
| DS-DD-016 | DECISION-016 | Four-Category Anti-Pattern Severity | Anti-Pattern Detection (AntiPatternCategory) | DRAFT |
