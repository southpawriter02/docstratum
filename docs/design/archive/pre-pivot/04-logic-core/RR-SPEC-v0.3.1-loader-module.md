# v0.3.1 — Loader Module

> **Task:** Create the module that loads and parses `llms.txt` files into Python objects.
> 

---

## Task Overview

---

## Implementation

### File: `core/__init__.py`

```python
from .loader import load_llms_txt
from .context import build_context_block
from .agents import create_baseline_agent, create_docstratum_agent
from .testing import run_ab_test

__all__ = [
    'load_llms_txt',
    'build_context_block',
    'create_baseline_agent',
    'create_docstratum_agent',
    'run_ab_test'
]
```

### File: `core/[loader.py](http://loader.py)`

```python
"""Loader module for llms.txt files."""

import yaml
import logging
from pathlib import Path
from typing import Union

from schemas import LlmsTxt

logger = logging.getLogger(__name__)

def load_llms_txt(source: Union[str, Path, dict]) -> LlmsTxt:
    """Load and validate an llms.txt file.
    
    Args:
        source: Can be:
            - A file path (str or Path)
            - A URL to fetch (str starting with http)
            - A pre-loaded dictionary
    
    Returns:
        Validated LlmsTxt object.
        
    Raises:
        FileNotFoundError: If file doesn't exist.
        yaml.YAMLError: If YAML is malformed.
        pydantic.ValidationError: If schema validation fails.
    """
    if isinstance(source, dict):
        logger.debug("Loading from dictionary")
        data = source
    elif isinstance(source, (str, Path)):
        source_str = str(source)
        if source_str.startswith('http'):
            logger.info(f"Fetching from URL: {source_str}")
            data = _fetch_from_url(source_str)
        else:
            logger.info(f"Loading from file: {source_str}")
            data = _load_from_file(Path(source_str))
    else:
        raise TypeError(f"Unsupported source type: {type(source)}")
    
    llms = LlmsTxt(**data)
    logger.info(f"Loaded llms.txt: {llms.site_name} ({len(llms.pages)} pages)")
    return llms

def _load_from_file(path: Path) -> dict:
    """Load YAML from a local file."""
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def _fetch_from_url(url: str) -> dict:
    """Fetch YAML from a URL."""
    import requests
    
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return yaml.safe_load(response.text)
```

---

## Testing

### File: `tests/test_[loader.py](http://loader.py)`

```python
import pytest
from pathlib import Path
from core.loader import load_llms_txt
from schemas import LlmsTxt

class TestLoader:
    
    def test_load_from_file(self, tmp_path):
        """Should load from a file path."""
        llms_file = tmp_path / "test.txt"
        llms_file.write_text("""
schema_version: "1.0"
site_name: "Test Site"
site_url: "https://example.com"
last_updated: "2026-01-01"
pages:
  - url: "https://example.com/page"
    title: "Test Page"
    content_type: "reference"
    last_verified: "2026-01-01"
    summary: "A test page for validation."
""")
        
        result = load_llms_txt(llms_file)
        assert isinstance(result, LlmsTxt)
        assert result.site_name == "Test Site"
    
    def test_load_from_dict(self):
        """Should load from a dictionary."""
        data = {
            'schema_version': '1.0',
            'site_name': 'Dict Site',
            'site_url': 'https://example.com',
            'last_updated': '2026-01-01',
            'pages': [{
                'url': 'https://example.com/p',
                'title': 'Page',
                'content_type': 'tutorial',
                'last_verified': '2026-01-01',
                'summary': 'A test summary here.'
            }]
        }
        
        result = load_llms_txt(data)
        assert result.site_name == 'Dict Site'
    
    def test_missing_file_raises(self):
        """Should raise FileNotFoundError for missing files."""
        with pytest.raises(FileNotFoundError):
            load_llms_txt('/nonexistent/path.txt')
```

---

## 📂 Sub-Part Pages

[v0.3.1a — Source Resolution & Input Handling](RR-SPEC-v0.3.1a-source-resolution-and-input-handling.md) — Input type detection, path resolution, URL fetching with retry, error hierarchy, 15+ test cases

[v0.3.1b — YAML Parsing & Preprocessing](RR-SPEC-v0.3.1b-yaml-parsing-and-preprocessing.md) — SafeLoader enforcement, encoding detection, frontmatter extraction, error recovery, line tracking

[v0.3.1c — Pydantic Validation & Schema Enforcement](RR-SPEC-v0.3.1c-pydantic-validation-and-schema-enforcement.md) — Field validators, custom validators (ID format, circular refs), validation levels 0-4, partial validation mode

[v0.3.1d — Caching, Performance & Public API](RR-SPEC-v0.3.1d-caching-performance-and-public-api.md) — URL caching with TTL, lazy validation, public API design, module structure, convenience functions

---

## Acceptance Criteria

- [ ]  `load_llms_txt()` accepts file paths
- [ ]  `load_llms_txt()` accepts dictionaries
- [ ]  Returns validated `LlmsTxt` object
- [ ]  Raises appropriate errors for invalid input
- [ ]  All tests pass
- [ ]  **v0.3.1a:** All 3 input types handled with proper error hierarchy
- [ ]  **v0.3.1b:** YAML edge cases from v0.0.1a handled (encoding, BOM, frontmatter)
- [ ]  **v0.3.1c:** Validation levels 0-4 implemented with user-friendly error messages
- [ ]  **v0.3.1d:** URL cache with TTL reduces redundant fetches; public API documented