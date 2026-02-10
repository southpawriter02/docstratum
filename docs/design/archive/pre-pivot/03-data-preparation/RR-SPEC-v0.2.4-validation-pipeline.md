# v0.2.4 — Validation Pipeline

> **Task:** Create an automated validation script that checks schema compliance and data integrity.
> 

---

## Task Overview

---

## Workflow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 1. Schema   │───▶│ 2. URL      │───▶│ 3. Concept  │───▶│ 4. Report   │
│   validate  │    │   checker   │    │   graph     │    │   generate  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

---

## Enhanced Validator

### File: [`validate.py`](http://validate.py) (Updated)

```python
#!/usr/bin/env python
"""Comprehensive validator for llms.txt files.

Validates:
1. Schema compliance (Pydantic)
2. URL reachability (optional)
3. Concept graph integrity
4. Content quality metrics
"""

import sys
import yaml
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

from schemas import LlmsTxt
from pydantic import ValidationError

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of validation run."""
    is_valid: bool
    schema_errors: list[str]
    url_errors: list[str]
    graph_errors: list[str]
    warnings: list[str]
    metrics: dict

def validate_schema(data: dict) -> tuple[Optional[LlmsTxt], list[str]]:
    """Validate against Pydantic schema."""
    errors = []
    try:
        llms = LlmsTxt(**data)
        return llms, errors
    except ValidationError as e:
        for error in e.errors():
            loc = " → ".join(str(x) for x in error['loc'])
            errors.append(f"Schema: {loc}: {error['msg']}")
        return None, errors

def validate_urls(llms: LlmsTxt, check_urls: bool = False) -> list[str]:
    """Optionally verify all URLs are reachable."""
    if not check_urls:
        return []
    
    errors = []
    urls = [str(p.url) for p in llms.pages]
    urls.append(str(llms.site_url))
    
    def check_url(url: str) -> Optional[str]:
        try:
            resp = requests.head(url, timeout=5, allow_redirects=True)
            if resp.status_code >= 400:
                return f"URL {url} returned {resp.status_code}"
        except requests.RequestException as e:
            return f"URL {url} unreachable: {e}"
        return None
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(check_url, url): url for url in urls}
        for future in as_completed(futures):
            result = future.result()
            if result:
                errors.append(result)
    
    return errors

def validate_graph(llms: LlmsTxt) -> list[str]:
    """Validate concept dependency graph."""
    errors = []
    concept_ids = {c.id for c in llms.concepts}
    
    # Check for orphan dependencies
    for concept in llms.concepts:
        for dep in concept.depends_on:
            if dep not in concept_ids:
                errors.append(f"Graph: Concept '{concept.id}' depends on unknown '{dep}'")
    
    # Check for circular dependencies (simple check)
    def has_cycle(start_id: str, visited: set) -> bool:
        if start_id in visited:
            return True
        visited.add(start_id)
        concept = next((c for c in llms.concepts if c.id == start_id), None)
        if concept:
            for dep in concept.depends_on:
                if has_cycle(dep, visited.copy()):
                    return True
        return False
    
    for concept in llms.concepts:
        if has_cycle(concept.id, set()):
            errors.append(f"Graph: Circular dependency detected involving '{concept.id}'")
    
    return errors

def calculate_metrics(llms: LlmsTxt) -> dict:
    """Calculate quality metrics."""
    return {
        'total_pages': len(llms.pages),
        'total_concepts': len(llms.concepts),
        'total_examples': len(llms.few_shot_examples),
        'avg_summary_length': sum(len(p.summary) for p in llms.pages) / max(len(llms.pages), 1),
        'concepts_with_anti_patterns': sum(1 for c in llms.concepts if c.anti_patterns),
        'avg_dependencies': sum(len(c.depends_on) for c in llms.concepts) / max(len(llms.concepts), 1),
    }

def generate_warnings(llms: LlmsTxt) -> list[str]:
    """Generate quality warnings (non-fatal)."""
    warnings = []
    
    # Check for concepts without anti-patterns
    for c in llms.concepts:
        if not c.anti_patterns:
            warnings.append(f"Warning: Concept '{c.name}' has no anti-patterns")
    
    # Check for short summaries
    for p in llms.pages:
        if len(p.summary) < 50:
            warnings.append(f"Warning: Page '{p.title}' has very short summary")
    
    # Check for examples without code
    for ex in llms.few_shot_examples:
        if '```' not in ex.ideal_answer:
            warnings.append(f"Warning: Example '{ex.intent}' has no code snippet")
    
    return warnings

def validate(filepath: str, check_urls: bool = False) -> ValidationResult:
    """Run full validation pipeline."""
    path = Path(filepath)
    
    if not path.exists():
        return ValidationResult(
            is_valid=False,
            schema_errors=[f"File not found: {filepath}"],
            url_errors=[], graph_errors=[], warnings=[],
            metrics={}
        )
    
    # Load YAML
    try:
        with open(path) as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return ValidationResult(
            is_valid=False,
            schema_errors=[f"YAML error: {e}"],
            url_errors=[], graph_errors=[], warnings=[],
            metrics={}
        )
    
    # Validate schema
    llms, schema_errors = validate_schema(data)
    if not llms:
        return ValidationResult(
            is_valid=False,
            schema_errors=schema_errors,
            url_errors=[], graph_errors=[], warnings=[],
            metrics={}
        )
    
    # Run additional validations
    url_errors = validate_urls(llms, check_urls)
    graph_errors = validate_graph(llms)
    warnings = generate_warnings(llms)
    metrics = calculate_metrics(llms)
    
    is_valid = not (schema_errors or graph_errors)
    # URL errors are warnings, not failures
    
    return ValidationResult(
        is_valid=is_valid,
        schema_errors=schema_errors,
        url_errors=url_errors,
        graph_errors=graph_errors,
        warnings=warnings,
        metrics=metrics
    )

def print_report(result: ValidationResult):
    """Print formatted validation report."""
    print("\n" + "="*60)
    print("LLMS.TXT VALIDATION REPORT")
    print("="*60)
    
    status = "✅ VALID" if result.is_valid else "❌ INVALID"
    print(f"\nStatus: {status}")
    
    if result.schema_errors:
        print("\n❌ Schema Errors:")
        for e in result.schema_errors:
            print(f"   {e}")
    
    if result.graph_errors:
        print("\n❌ Graph Errors:")
        for e in result.graph_errors:
            print(f"   {e}")
    
    if result.url_errors:
        print("\n⚠️  URL Issues:")
        for e in result.url_errors:
            print(f"   {e}")
    
    if result.warnings:
        print("\n⚠️  Warnings:")
        for w in result.warnings:
            print(f"   {w}")
    
    if result.metrics:
        print("\n📊 Metrics:")
        for k, v in result.metrics.items():
            print(f"   {k}: {v:.1f}" if isinstance(v, float) else f"   {k}: {v}")
    
    print("\n" + "="*60)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Validate llms.txt files')
    parser.add_argument('filepath', help='Path to llms.txt file')
    parser.add_argument('--check-urls', action='store_true', help='Verify URLs are reachable')
    args = parser.parse_args()
    
    result = validate(args.filepath, args.check_urls)
    print_report(result)
    sys.exit(0 if result.is_valid else 1)
```

---

## Usage

```bash
# Basic validation (fast)
python validate.py data/llms.txt

# With URL checking (slower)
python validate.py data/llms.txt --check-urls
```

---

## Sample Output

```
============================================================
LLMS.TXT VALIDATION REPORT
============================================================

Status: ✅ VALID

⚠️  Warnings:
   Warning: Concept 'context-window' has no anti-patterns
   Warning: Example 'authenticate backend' has no code snippet

📊 Metrics:
   total_pages: 5
   total_concepts: 3
   total_examples: 2
   avg_summary_length: 142.4
   concepts_with_anti_patterns: 2
   avg_dependencies: 0.7

============================================================
```

---

## 📂 Sub-Part Pages

[v0.2.4a — Schema Validation Engine (Levels 0-1)](v0.2.4a%20%E2%80%94%20Schema%20Validation%20Engine%20(Levels%200-1).md) — YAML parsing, encoding detection, Pydantic models, 15+ test cases, error codes E001-E007

[v0.2.4b — Content & Link Validation Engine (Level 2)](v0.2.4b%20%E2%80%94%20Content%20&%20Link%20Validation%20Engine%20(Level%202).md) — URL pipeline (syntax→DNS→HTTP), concurrent checking, cross-reference validation, result caching

[v0.2.4c — Quality Scoring Engine (Level 3)](v0.2.4c%20%E2%80%94%20Quality%20Scoring%20Engine%20(Level%203).md) — 5 quality dimensions, scoring rubrics, 20+ automated heuristics, benchmark comparison, quality badges

[v0.2.4d — Pipeline Orchestration & Reporting](RR-SPEC-v0.2.4d-pipeline-orchestration-and-reporting.md) — CLI entry point, .docstratum.yml config, 4 output formats, GitHub Actions workflow, pre-commit hooks, Makefile

---

## Acceptance Criteria

- [ ]  [`validate.py`](http://validate.py) runs without errors
- [ ]  Schema validation catches malformed YAML
- [ ]  Graph validation detects orphan dependencies
- [ ]  Metrics are calculated and displayed
- [ ]  `python [validate.py](http://validate.py) data/llms.txt` returns exit code 0
- [ ]  **v0.2.4a:** Level 0-1 validation catches all E-series errors with line numbers
- [ ]  **v0.2.4b:** URL checker handles concurrent requests with rate limiting
- [ ]  **v0.2.4c:** Quality scores match benchmark expectations (Stripe ≥ 4.0)
- [ ]  **v0.2.4d:** CI/CD pipeline configured and running in GitHub Actions

---

## Phase v0.2.0 Complete Checklist

- [ ]  v0.2.1: Source site audited
- [ ]  v0.2.2: Concepts extracted and mapped
- [ ]  v0.2.3: `llms.txt` authored
- [ ]  v0.2.4: Validation pipeline working

**→ Ready to proceed to v0.3.0: Logic Core**