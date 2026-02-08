# Validation Levels Index

> **Parent:** [standards/](../README.md)
> **Type:** DS-VL-* (Validation Level)
> **Total Expected:** 5 levels (L0–L4)

## Overview

Validation levels define the progressive quality tiers that the DocStratum pipeline evaluates against. The model is cumulative: achieving L3 means L0, L1, and L2 also pass. Each level has specific entry criteria, exit criteria, and a set of validation checks that must pass.

## Index

| DS Identifier | Level | Name | Criteria Count | Exit Criteria Summary | Status |
|---------------|-------|------|----------------|----------------------|--------|
| DS-VL-L0 | L0 | Parseable | 5 | All L0 criteria pass (HARD gate) | DRAFT |
| DS-VL-L1 | L1 | Structural | 6 | 4 HARD criteria pass (H1, single H1, H2 sections, link format) | DRAFT |
| DS-VL-L2 | L2 | Content Quality | 7 | All SOFT — evaluated, score-gated | DRAFT |
| DS-VL-L3 | L3 | Best Practices | 9 | 1 HARD (no critical anti-patterns) + 8 SOFT | DRAFT |
| DS-VL-L4 | L4 | DocStratum Extended | 8 | All SOFT — evaluated, score-gated | DRAFT |

## Level Hierarchy

```
L0 (Parseable)     → Can a machine read this file at all?
  └─► L1 (Structural)   → Does it follow the llms.txt spec structure?
       └─► L2 (Content Quality)  → Is the content meaningful and useful?
            └─► L3 (Best Practices) → Does it follow recommended patterns?
                 └─► L4 (Exemplary)   → Does it include advanced LLM-optimization?
```

Each level must pass before the next is evaluated. L0 failures cap the total score at 29 (CRITICAL grade).

## Criteria Distribution by Level

| Level | Structural (30pt) | Content (50pt) | Anti-Pattern (20pt) | Total Points |
|-------|-------------------|----------------|---------------------|--------------|
| L0 | 0 (gates only) | 0 | 0 | 0 |
| L1 | 22 pts (6 criteria) | 0 | 0 | 22 |
| L2 | 0 | 25 pts (7 criteria) | 0 | 25 |
| L3 | 8 pts (3 criteria) | 25 pts (6 criteria) | 0 | 33 |
| L4 | 0 | 0 | 20 pts (8 criteria) | 20 |
| **Total** | **30** | **50** | **20** | **100** |
