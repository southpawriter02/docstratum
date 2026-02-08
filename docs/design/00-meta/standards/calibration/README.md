# Calibration Specimens Index

> **Parent:** [standards/](../README.md)
> **Type:** DS-CS-* (Calibration Specimen)
> **Total Expected:** 6 specimens

## Overview

Calibration specimens are real-world llms.txt files with known expected scores. They serve as the self-test mechanism for the validation pipeline: if the pipeline produces a score that differs from the expected score beyond a configured tolerance, it signals configuration drift or a regression.

## Index

| DS Identifier | Project | Expected Score | Expected Grade | Source URL | Status |
|---------------|---------|---------------|----------------|------------|--------|
| DS-CS-001 | Svelte | 92 | Exemplary | https://svelte.dev/llms.txt | DRAFT |
| DS-CS-002 | Pydantic | 90 | Exemplary | https://docs.pydantic.dev/llms.txt | DRAFT |
| DS-CS-003 | Vercel AI SDK | 90 | Exemplary | https://sdk.vercel.ai/llms.txt | DRAFT |
| DS-CS-004 | Shadcn UI | 89 | Strong | https://ui.shadcn.com/llms.txt | DRAFT |
| DS-CS-005 | Cursor | 42 | Needs Work | https://cursor.com/llms.txt | DRAFT |
| DS-CS-006 | NVIDIA | 24 | Critical | https://developer.nvidia.com/llms.txt | DRAFT |
