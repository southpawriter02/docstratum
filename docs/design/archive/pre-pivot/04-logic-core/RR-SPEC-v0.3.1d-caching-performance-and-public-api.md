# Caching, Performance & Public API

> The loader module must expose a comprehensive public API through load_llms_txt() function, implement intelligent caching for URL-loaded files, optimize performance through lazy evaluation and connection pooling, and integrate seamlessly with downstream modules through well-documented conventions.

## Objective

Design and implement the loader module's public interface and performance layer that:
1. Defines the primary `load_llms_txt()` function with flexible input handling
2. Implements URL caching with TTL (time-to-live) and cache invalidation
3. Optimizes performance through lazy Pydantic validation and connection pooling
4. Provides convenience functions (load_and_validate, load_with_report, quick_validate)
5. Designs module structure with proper import organization
6. Establishes integration contract with Context Builder v0.3.2
7. Implements comprehensive logging strategy (DEBUG/INFO/WARNING/ERROR)
8. Provides production-ready __init__.py with polished public API
9. Documents all functions with examples and error handling
10. Includes performance monitoring and cache statistics

## Scope Boundaries

**In Scope:**
- Primary load_llms_txt() function design and implementation
- URL caching with TTL, key generation, invalidation rules
- Lazy Pydantic validation strategy
- HTTP connection pooling with requests.Session
- File I/O optimization (buffering, encoding detection)
- Module structure (core/__init__.py, core/loader.py, core/cache.py)
- Convenience functions with examples
- Integration contract with Context Builder
- Comprehensive logging at all levels
- Complete __init__.py with public API exports
- Performance monitoring and cache stats

**Out of Scope:**
- Redis/Memcached distributed caching (local file cache only)
- Database caching
- Async/await implementation
- Authentication/authorization (basic auth only)

## Dependency Diagram

```
load_llms_txt(input, **kwargs)
    ├→ CacheManager.get(cache_key)
    │   └→ if hit & not expired → return CacheEntry
    ├→ InputResolver.detect_type()
    │   ├→ FilePathResolver.resolve()
    │   ├→ URLFetcher.fetch()
    │   └→ DictValidator.validate()
    ├→ YAMLParser.parse()
    ├→ PydanticValidator.validate()
    ├→ CacheManager.set(cache_key, data)
    └→ LoaderResult {data, source, validation_level, warnings, metadata}
         ↓
    Context Builder (v0.3.2) →
    Integration: pass LoaderResult.data (LlmsTxt object) to context builder
```

## 1. URL Caching Strategy

### Cache Design Parameters

| Parameter | Value | Justification |
|-----------|-------|---------------|
| **Cache Location** | `~/.docstratum/cache/` | Per-user local directory |
| **Default TTL** | 24 hours | Balance freshness vs request reduction |
| **Max Cache Size** | 500 MB | Reasonable disk usage |
| **Cache Key** | SHA256(url) | Deterministic, collision-proof |
| **Compression** | gzip | Reduce disk space by 60-80% |

### Implementation Code

```python
import hashlib
import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import gzip

class CacheEntry:
    """Represents a cached file with metadata."""

    def __init__(
        self,
        data: str,
        source_url: str,
        timestamp: datetime,
        ttl_hours: int = 24
    ):
        self.data = data
        self.source_url = source_url
        self.timestamp = timestamp
        self.ttl_hours = ttl_hours
        self.created_at = timestamp
        self.accessed_count = 0

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        expiry = self.created_at + timedelta(hours=self.ttl_hours)
        return datetime.now() > expiry

    def get_age_hours(self) -> float:
        """Get age of cache entry in hours."""
        age = datetime.now() - self.created_at
        return age.total_seconds() / 3600

    def to_dict(self) -> Dict[str, Any]:
        """Serialize cache entry metadata."""
        return {
            'source_url': self.source_url,
            'created_at': self.created_at.isoformat(),
            'ttl_hours': self.ttl_hours,
            'age_hours': self.get_age_hours(),
            'accessed_count': self.accessed_count,
            'is_expired': self.is_expired()
        }


class CacheManager:
    """Manages local file cache for URL-loaded files."""

    DEFAULT_CACHE_DIR = Path.home() / '.docstratum' / 'cache'
    MAX_CACHE_SIZE = 500 * 1024 * 1024  # 500 MB

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize cache manager.

        Args:
            cache_dir: Custom cache directory (default: ~/.docstratum/cache/)
        """
        self.cache_dir = cache_dir or self.DEFAULT_CACHE_DIR
        self.cache_index_path = self.cache_dir / 'index.json'
        self._ensure_cache_dir()
        self._load_index()

    def _ensure_cache_dir(self):
        """Create cache directory if it doesn't exist."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _load_index(self):
        """Load cache index from disk."""
        if self.cache_index_path.exists():
            try:
                with open(self.cache_index_path, 'r') as f:
                    self.index = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.index = {}
        else:
            self.index = {}

    def _save_index(self):
        """Save cache index to disk."""
        try:
            with open(self.cache_index_path, 'w') as f:
                json.dump(self.index, f, indent=2)
        except IOError as e:
            print(f"Warning: Failed to save cache index: {e}")

    def _generate_cache_key(self, url: str) -> str:
        """
        Generate deterministic cache key from URL.

        Args:
            url: Source URL

        Returns:
            SHA256 hash (48 chars)
        """
        return hashlib.sha256(url.encode()).hexdigest()[:48]

    def get(
        self,
        url: str,
        ignore_expiry: bool = False
    ) -> Optional[CacheEntry]:
        """
        Retrieve cached data for URL.

        Args:
            url: Source URL
            ignore_expiry: If True, return even if expired

        Returns:
            CacheEntry if cache hit and not expired, None otherwise
        """
        cache_key = self._generate_cache_key(url)
        cache_file = self.cache_dir / f"{cache_key}.gz"

        # Check if cached file exists
        if not cache_file.exists():
            return None

        # Check index for metadata
        if cache_key not in self.index:
            return None

        metadata = self.index[cache_key]

        # Check expiry
        created_at = datetime.fromisoformat(metadata['created_at'])
        ttl_hours = metadata.get('ttl_hours', 24)
        age_hours = (datetime.now() - created_at).total_seconds() / 3600

        if not ignore_expiry and age_hours > ttl_hours:
            # Expired: remove from cache
            cache_file.unlink()
            del self.index[cache_key]
            self._save_index()
            return None

        # Decompress and load data
        try:
            with gzip.open(cache_file, 'rt', encoding='utf-8') as f:
                data = f.read()

            entry = CacheEntry(
                data=data,
                source_url=url,
                timestamp=created_at,
                ttl_hours=ttl_hours
            )

            # Update access count
            metadata['accessed_count'] = metadata.get('accessed_count', 0) + 1
            self.index[cache_key] = metadata
            self._save_index()

            return entry

        except (IOError, gzip.BadGzipFile) as e:
            print(f"Warning: Failed to read cache file {cache_key}: {e}")
            return None

    def set(
        self,
        url: str,
        data: str,
        ttl_hours: int = 24
    ) -> bool:
        """
        Cache data for URL.

        Args:
            url: Source URL
            data: Content to cache
            ttl_hours: Time-to-live in hours

        Returns:
            True if successful, False otherwise
        """
        cache_key = self._generate_cache_key(url)
        cache_file = self.cache_dir / f"{cache_key}.gz"

        # Check cache size
        current_size = sum(
            f.stat().st_size for f in self.cache_dir.glob('*.gz')
        )
        data_size = len(data.encode('utf-8'))

        if current_size + data_size > self.MAX_CACHE_SIZE:
            # Evict least recently used
            self._evict_lru()

        # Compress and write data
        try:
            with gzip.open(cache_file, 'wt', encoding='utf-8') as f:
                f.write(data)

            # Update index
            self.index[cache_key] = {
                'source_url': url,
                'created_at': datetime.now().isoformat(),
                'ttl_hours': ttl_hours,
                'accessed_count': 0
            }
            self._save_index()

            return True

        except IOError as e:
            print(f"Warning: Failed to write cache file {cache_key}: {e}")
            return False

    def _evict_lru(self):
        """Evict least recently used entries until under size limit."""
        # Sort by accessed_count
        sorted_keys = sorted(
            self.index.items(),
            key=lambda x: x[1].get('accessed_count', 0)
        )

        for key, _ in sorted_keys[:len(sorted_keys)//4]:
            cache_file = self.cache_dir / f"{key}.gz"
            if cache_file.exists():
                cache_file.unlink()
            del self.index[key]

        self._save_index()

    def clear(self):
        """Clear entire cache."""
        for cache_file in self.cache_dir.glob('*.gz'):
            cache_file.unlink()
        self.index.clear()
        self._save_index()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        cache_files = list(self.cache_dir.glob('*.gz'))
        total_size = sum(f.stat().st_size for f in cache_files)

        return {
            'entries': len(self.index),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'max_size_mb': self.MAX_CACHE_SIZE / (1024 * 1024),
            'files': len(cache_files)
        }
```

## 2. Lazy Validation Strategy

### Deferred Validation Pattern

```python
from typing import Callable, Optional
from enum import Enum

class ValidationMode(str, Enum):
    """Validation timing modes."""
    IMMEDIATE = "immediate"  # Validate on load
    LAZY = "lazy"            # Validate on first access
    DEFERRED = "deferred"    # Validate only if requested

class LazyValidator:
    """Wrapper for deferred validation of LlmsTxt data."""

    def __init__(
        self,
        data: Dict[str, Any],
        validator_fn: Callable,
        validation_level: int = 2
    ):
        self._raw_data = data
        self._validator_fn = validator_fn
        self._validation_level = validation_level
        self._validated_data = None
        self._validation_result = None

    def get_data(self, force_validation: bool = False) -> Optional[Any]:
        """
        Get validated data, validating if necessary.

        Args:
            force_validation: If True, always validate

        Returns:
            Validated LlmsTxt object or None if validation failed
        """
        if self._validated_data is not None and not force_validation:
            return self._validated_data

        # Perform validation
        result = self._validator_fn(
            self._raw_data,
            level=self._validation_level
        )

        self._validation_result = result

        if result.is_valid():
            self._validated_data = result.data
            return result.data
        else:
            return None

    def is_validated(self) -> bool:
        """Check if data has been validated."""
        return self._validation_result is not None

    def get_validation_result(self) -> Optional[Any]:
        """Get validation result if available."""
        return self._validation_result
```

## 3. Module Structure & Organization

### File Layout

```
loader/
├── __init__.py              # Public API exports
├── loader.py               # Main load_llms_txt() function
├── cache.py                # CacheManager class
├── resolver.py             # Input resolution (v0.3.1a)
├── parser.py               # YAML parsing (v0.3.1b)
├── validation.py           # Pydantic models (v0.3.1c)
├── errors.py               # Custom exception hierarchy
├── logging.py              # Logging configuration
└── types.py                # Type definitions and enums
```

### __init__.py Implementation

```python
"""
DocStratum v0.3.1 - Loader Module

Public API for loading and validating llms.txt files.

Example:
    >>> from loader import load_llms_txt
    >>> result = load_llms_txt('/path/to/llms.txt')
    >>> if result.is_valid():
    ...     print(result.data)
"""

from pathlib import Path
from typing import Union, Dict, Any, Optional

# Core function
from .loader import load_llms_txt

# Result types
from .loader import LoaderResult

# Models
from .validation import (
    LlmsTxt,
    CanonicalPage,
    Concept,
    FewShotExample,
    ValidationLevel,
    ValidationMode
)

# Convenience functions
from .loader import (
    load_and_validate,
    load_with_report,
    quick_validate,
    validate_file
)

# Cache management
from .cache import CacheManager

# Version
__version__ = "0.3.1"
__author__ = "DocStratum Team"

# Public API
__all__ = [
    # Main function
    'load_llms_txt',

    # Convenience functions
    'load_and_validate',
    'load_with_report',
    'quick_validate',
    'validate_file',

    # Result type
    'LoaderResult',

    # Models
    'LlmsTxt',
    'CanonicalPage',
    'Concept',
    'FewShotExample',

    # Enums
    'ValidationLevel',
    'ValidationMode',

    # Utilities
    'CacheManager',

    # Version
    '__version__',
]

# Configure logging
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())
```

## 4. Public API Function Design

### Main load_llms_txt() Function

```python
import logging
from typing import Union
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class LoaderResult:
    """Result container from load_llms_txt()."""

    def __init__(
        self,
        data: Optional[LlmsTxt] = None,
        errors: list = None,
        warnings: list = None,
        validation_level: int = 2,
        source: str = None,
        load_time_ms: float = 0.0,
        validation_time_ms: float = 0.0,
        from_cache: bool = False
    ):
        self.data = data
        self.errors = errors or []
        self.warnings = warnings or []
        self.validation_level = validation_level
        self.source = source
        self.load_time_ms = load_time_ms
        self.validation_time_ms = validation_time_ms
        self.from_cache = from_cache
        self.timestamp = datetime.now()

    def is_valid(self) -> bool:
        """Check if result is valid (no errors)."""
        return len(self.errors) == 0 and self.data is not None

    def has_warnings(self) -> bool:
        """Check if there are warnings."""
        return len(self.warnings) > 0

    def get_summary(self) -> str:
        """Get human-readable summary."""
        status = "VALID" if self.is_valid() else "INVALID"
        cache_info = " (from cache)" if self.from_cache else ""
        timing = f"{self.load_time_ms+self.validation_time_ms:.1f}ms"

        summary = f"[{status}] {self.source} {timing}{cache_info}"

        if self.errors:
            summary += f" - {len(self.errors)} error(s)"
        if self.warnings:
            summary += f" - {len(self.warnings)} warning(s)"

        return summary

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            'valid': self.is_valid(),
            'source': self.source,
            'data': self.data.model_dump() if self.data else None,
            'errors': self.errors,
            'warnings': self.warnings,
            'validation_level': self.validation_level,
            'load_time_ms': self.load_time_ms,
            'validation_time_ms': self.validation_time_ms,
            'from_cache': self.from_cache,
            'timestamp': self.timestamp.isoformat()
        }


def load_llms_txt(
    source: Union[str, Path, Dict[str, Any]],
    *,
    validation_level: int = 2,
    use_cache: bool = True,
    cache_ttl_hours: int = 24,
    timeout: int = 10,
    strict: bool = False
) -> LoaderResult:
    """
    Load and validate an llms.txt file from file, URL, or dict.

    This is the primary entry point for the DocStratum loader module.
    It accepts three input types and returns a LoaderResult with validation
    status, metadata, and optional cached data.

    Args:
        source: File path (str/Path), HTTP/HTTPS URL, or dict
        validation_level: Strictness level 0-4 (default: 2 - standard)
        use_cache: Enable URL caching with TTL (default: True)
        cache_ttl_hours: Cache time-to-live in hours (default: 24)
        timeout: Request timeout for URLs in seconds (default: 10)
        strict: Fail on warnings (default: False)

    Returns:
        LoaderResult with data, errors, warnings, and metadata

    Raises:
        TypeError: If source type is not supported
        FileNotFoundError: If file path doesn't exist
        requests.RequestException: If URL fetch fails
        ValueError: If validation fails in strict mode

    Examples:
        Load from file:
        >>> result = load_llms_txt('/path/to/llms.txt')
        >>> if result.is_valid():
        ...     print(result.data.site_name)

        Load from URL with caching:
        >>> result = load_llms_txt(
        ...     'https://example.com/llms.txt',
        ...     use_cache=True,
        ...     cache_ttl_hours=48
        ... )

        Load from dict (already parsed):
        >>> data_dict = {'schema_version': '1.0.0', ...}
        >>> result = load_llms_txt(data_dict)

        Check result:
        >>> if result.is_valid():
        ...     print(f"Loaded in {result.load_time_ms}ms")
        ... else:
        ...     print(result.errors)
    """
    import time

    start_time = time.time()
    logger.info(f"Loading llms.txt from {type(source).__name__}")

    try:
        # Step 1: Resolve input source
        from .resolver import InputResolver, PathResolver, URLFetcher, DictValidator

        input_type = InputResolver.detect_type(source)
        logger.debug(f"Detected input type: {input_type.value}")

        raw_data = None
        source_name = str(source)[:100]
        from_cache = False

        if input_type.value == 'dict':
            DictValidator.validate(source)
            raw_data = source
            source_name = '<dict>'

        elif input_type.value == 'file_path':
            path = PathResolver.resolve(source)
            raw_data = PathResolver.read_file(path)
            source_name = str(path)
            logger.debug(f"Loaded file: {path}")

        elif input_type.value == 'url':
            # Check cache first
            cache_manager = CacheManager()
            if use_cache:
                cached = cache_manager.get(str(source))
                if cached and not cached.is_expired():
                    raw_data = cached.data
                    from_cache = True
                    logger.debug(f"Cache hit for {source}")

            # Fetch if not cached
            if raw_data is None:
                raw_data = URLFetcher.fetch(str(source), timeout=timeout)
                logger.debug(f"Fetched URL: {source}")

                # Cache the result
                if use_cache:
                    cache_manager.set(str(source), raw_data, cache_ttl_hours)

            source_name = str(source)

        load_time = (time.time() - start_time) * 1000

        # Step 2: Parse YAML
        from .parser import YAMLParserIntegrated

        parsed_data, yaml_metadata = YAMLParserIntegrated.parse_from_string(
            raw_data,
            source_name=source_name
        )
        logger.debug(f"Parsed YAML successfully")

        # Step 3: Validate with Pydantic
        from .validation import PydanticValidator, ValidationLevel, ValidationMode

        validation_result = PydanticValidator.validate(
            parsed_data,
            level=ValidationLevel(validation_level),
            mode=ValidationMode.COLLECT_ALL
        )

        validation_time = (time.time() - start_time) * 1000 - load_time

        if not validation_result.is_valid():
            logger.warning(
                f"Validation failed: {len(validation_result.errors)} error(s)"
            )

            if strict:
                raise ValueError(
                    validation_result.get_error_summary()
                )

        logger.info(
            f"Successfully loaded llms.txt "
            f"({load_time:.1f}ms load, {validation_time:.1f}ms validation)"
        )

        return LoaderResult(
            data=validation_result.data,
            errors=validation_result.errors,
            warnings=validation_result.warnings,
            validation_level=validation_level,
            source=source_name,
            load_time_ms=load_time,
            validation_time_ms=validation_time,
            from_cache=from_cache
        )

    except Exception as e:
        logger.error(f"Failed to load llms.txt: {e}")

        return LoaderResult(
            data=None,
            errors=[{'message': str(e)}],
            warnings=[],
            validation_level=validation_level,
            source=str(source)[:100]
        )
```

## 5. Convenience Functions

### Implementation Code

```python
def load_and_validate(
    source: Union[str, Path, Dict],
    strict: bool = True
) -> LlmsTxt:
    """
    Load and validate llms.txt, raising on any errors.

    Convenience function that loads a file and raises exceptions if validation
    fails. Use this when you need the data or an error, with no middle ground.

    Args:
        source: File path, URL, or dict
        strict: Raise on warnings too (default: True)

    Returns:
        Validated LlmsTxt object

    Raises:
        ValueError: If validation fails or warnings exist (if strict=True)

    Example:
        >>> llms = load_and_validate('/path/to/llms.txt')
        >>> print(llms.site_name)
    """
    result = load_llms_txt(source, strict=strict)

    if not result.is_valid():
        raise ValueError(result.get_summary())

    if strict and result.has_warnings():
        raise ValueError(f"Warnings detected: {result.warnings}")

    return result.data


def load_with_report(
    source: Union[str, Path, Dict],
    verbose: bool = False
) -> tuple:
    """
    Load llms.txt and return both data and detailed report.

    Convenience function for loading with full reporting of all issues.

    Args:
        source: File path, URL, or dict
        verbose: Print report to stdout (default: False)

    Returns:
        Tuple of (data, report_dict)

    Example:
        >>> data, report = load_with_report('/path/to/llms.txt', verbose=True)
        >>> print(report['errors'])
    """
    result = load_llms_txt(source)

    report = {
        'valid': result.is_valid(),
        'source': result.source,
        'summary': result.get_summary(),
        'errors': result.errors,
        'warnings': result.warnings,
        'timing': {
            'load_ms': result.load_time_ms,
            'validation_ms': result.validation_time_ms,
            'total_ms': result.load_time_ms + result.validation_time_ms
        },
        'from_cache': result.from_cache
    }

    if verbose:
        print(report['summary'])
        if result.errors:
            print("Errors:")
            for err in result.errors:
                print(f"  - {err}")

    return result.data, report


def quick_validate(source: Union[str, Path, Dict]) -> bool:
    """
    Quick check: is this file valid?

    Convenience function for simple yes/no validation check.

    Args:
        source: File path, URL, or dict

    Returns:
        True if valid, False otherwise

    Example:
        >>> if quick_validate('/path/to/llms.txt'):
        ...     print("File is valid")
    """
    result = load_llms_txt(source)
    return result.is_valid()


def validate_file(
    source: Union[str, Path],
    level: int = 2,
    show_errors: bool = True
) -> bool:
    """
    Validate a local file with optional error display.

    Convenience function for file-specific validation with error reporting.

    Args:
        source: File path only (not URL or dict)
        level: Validation level 0-4
        show_errors: Print errors to stdout (default: True)

    Returns:
        True if valid, False otherwise

    Example:
        >>> if validate_file('/path/to/llms.txt', show_errors=True):
        ...     print("All checks passed")
    """
    result = load_llms_txt(source, validation_level=level)

    if show_errors and not result.is_valid():
        print(result.get_summary())
        for err in result.errors:
            print(f"  Error: {err.get('message', str(err))}")

    return result.is_valid()
```

## 6. Logging Strategy

### Logging Configuration

```python
import logging
import sys

class LoaderLogger:
    """Centralized logging configuration for loader module."""

    # Log levels and their use cases
    LOG_LEVELS = {
        'DEBUG': {
            'examples': [
                'Input type detected: url',
                'Parsing YAML at line 42',
                'Cache hit for https://...',
                'Field validation: url_format'
            ]
        },
        'INFO': {
            'examples': [
                'Successfully loaded llms.txt',
                'File resolved to /absolute/path',
                'Validation passed (0 errors, 2 warnings)',
                'Cached for 24 hours'
            ]
        },
        'WARNING': {
            'examples': [
                'Summary exceeds 280 characters (350)',
                'Concept depends on unknown concept',
                'URL redirected 3 times',
                'File encoding: Latin-1 (not UTF-8)'
            ]
        },
        'ERROR': {
            'examples': [
                'File not found: /path/to/file.yaml',
                'Invalid YAML at line 15: duplicate key',
                'HTTP 404 fetching https://example.com/llms.txt',
                'Validation failed: 5 error(s)'
            ]
        }
    }

    @staticmethod
    def configure(level: str = 'INFO') -> logging.Logger:
        """
        Configure logging for loader module.

        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR)

        Returns:
            Configured logger instance
        """
        logger = logging.getLogger('loader')
        logger.setLevel(getattr(logging, level))

        # Create console handler with formatting
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, level))

        formatter = logging.Formatter(
            fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)

        # Avoid duplicate handlers
        if not logger.handlers:
            logger.addHandler(handler)

        return logger
```

## 7. Integration with Context Builder (v0.3.2)

### Integration Contract

```python
"""
Integration point: Context Builder v0.3.2

The loader module provides the following interface to downstream modules:

1. OUTPUT TYPE: LoaderResult
   - result.data: LlmsTxt (Pydantic model)
   - result.errors: List[Dict] - validation errors
   - result.warnings: List[Dict] - validation warnings
   - result.source: str - source identifier
   - result.is_valid() -> bool

2. USAGE PATTERN:
   from loader import load_llms_txt

   result = load_llms_txt('https://example.com/llms.txt')
   if result.is_valid():
       llms_txt = result.data  # Type: LlmsTxt
       # Pass to Context Builder
   else:
       handle_errors(result.errors)

3. DATA PASSED:
   - llms_txt.pages: List[CanonicalPage]
   - llms_txt.concepts: List[Concept]
   - llms_txt.few_shot_examples: List[FewShotExample]

4. GUARANTEES:
   - All data is validated against Pydantic models
   - All URLs are proper HttpUrl instances
   - All dates are datetime.date objects
   - All lists are Python list objects
   - No missing required fields
"""
```

## 8. Performance Monitoring

### Metrics Collection

```python
from dataclasses import dataclass
from typing import List
import statistics

@dataclass
class LoadMetrics:
    """Performance metrics from a single load operation."""
    source: str
    load_time_ms: float
    validation_time_ms: float
    total_time_ms: float
    from_cache: bool
    file_size_bytes: int = 0
    error_count: int = 0

    def get_summary(self) -> str:
        """Get human-readable summary."""
        cache_note = " (cached)" if self.from_cache else ""
        return (
            f"{self.source}: {self.total_time_ms:.1f}ms "
            f"({self.load_time_ms:.1f}ms load, "
            f"{self.validation_time_ms:.1f}ms validation){cache_note}"
        )


class PerformanceMonitor:
    """Tracks performance metrics across multiple operations."""

    def __init__(self):
        self.metrics: List[LoadMetrics] = []

    def record(self, metric: LoadMetrics):
        """Record a performance metric."""
        self.metrics.append(metric)

    def get_stats(self) -> Dict[str, Any]:
        """Get aggregate performance statistics."""
        if not self.metrics:
            return {}

        times = [m.total_time_ms for m in self.metrics]
        cache_hits = sum(1 for m in self.metrics if m.from_cache)

        return {
            'total_operations': len(self.metrics),
            'cache_hits': cache_hits,
            'cache_hit_rate': cache_hits / len(self.metrics),
            'average_time_ms': statistics.mean(times),
            'median_time_ms': statistics.median(times),
            'min_time_ms': min(times),
            'max_time_ms': max(times),
            'std_dev_ms': statistics.stdev(times) if len(times) > 1 else 0
        }
```

## 9. Complete Module Examples

### Example 1: Load from File

```python
from loader import load_llms_txt

result = load_llms_txt('/path/to/llms.txt')

if result.is_valid():
    print(f"Site: {result.data.site_name}")
    print(f"Pages: {len(result.data.pages)}")
    print(f"Concepts: {len(result.data.concepts)}")
else:
    print("Validation errors:")
    for error in result.errors:
        print(f"  - {error['message']}")
```

### Example 2: Load from URL with Caching

```python
from loader import load_llms_txt

# First load: fetches from network and caches
result1 = load_llms_txt(
    'https://example.com/llms.txt',
    use_cache=True,
    cache_ttl_hours=48
)

print(result1.from_cache)  # False (fetched from network)

# Second load: uses cache (same execution, ~instantly)
result2 = load_llms_txt(
    'https://example.com/llms.txt',
    use_cache=True
)

print(result2.from_cache)  # True (loaded from cache)
```

### Example 3: Convenience Functions

```python
from loader import load_and_validate, load_with_report, quick_validate

# Just the data (raises on error)
try:
    llms = load_and_validate('/path/to/llms.txt')
except ValueError as e:
    print(f"Invalid file: {e}")

# Data + detailed report
data, report = load_with_report(
    'https://example.com/llms.txt',
    verbose=True
)

# Just yes/no
if quick_validate('/path/to/llms.txt'):
    print("File is valid")
```

## 10. Test Suite (File-based Tests)

### Integration Tests: `tests/test_loader_api.py`

```python
import pytest
from pathlib import Path
import tempfile
import json

from loader import (
    load_llms_txt, load_and_validate, load_with_report,
    quick_validate, LoaderResult, LlmsTxt
)

class TestLoadLlmsTxt:
    """Tests for primary load_llms_txt() function."""

    def test_load_valid_file(self):
        """Test loading valid YAML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
schema_version: 1.0.0
site_name: Test
site_url: https://test.com
last_updated: 2024-01-01
pages: []
concepts: []
few_shot_examples: []
""")
            temp_path = f.name

        try:
            result = load_llms_txt(temp_path)
            assert result.is_valid()
            assert isinstance(result.data, LlmsTxt)
            assert result.data.site_name == "Test"
        finally:
            Path(temp_path).unlink()

    def test_load_invalid_file(self):
        """Test handling of invalid file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("schema_version: invalid")
            temp_path = f.name

        try:
            result = load_llms_txt(temp_path)
            assert not result.is_valid()
            assert len(result.errors) > 0
        finally:
            Path(temp_path).unlink()

    def test_load_from_dict(self):
        """Test loading from dictionary."""
        data = {
            'schema_version': '1.0.0',
            'site_name': 'Test',
            'site_url': 'https://test.com',
            'last_updated': '2024-01-01',
            'pages': [],
            'concepts': [],
            'few_shot_examples': []
        }
        result = load_llms_txt(data)
        assert result.is_valid()

    def test_load_with_validation_level(self):
        """Test validation level parameter."""
        data = {...}  # Valid data
        result = load_llms_txt(data, validation_level=3)
        assert result.validation_level == 3

    def test_result_type(self):
        """Test LoaderResult properties."""
        data = {...}
        result = load_llms_txt(data)
        assert isinstance(result, LoaderResult)
        assert hasattr(result, 'data')
        assert hasattr(result, 'errors')
        assert hasattr(result, 'warnings')
        assert hasattr(result, 'is_valid')


class TestConvenienceFunctions:
    """Tests for convenience wrapper functions."""

    def test_load_and_validate_success(self):
        """Test load_and_validate with valid data."""
        data = {...}
        llms = load_and_validate(data)
        assert isinstance(llms, LlmsTxt)

    def test_load_and_validate_failure(self):
        """Test load_and_validate with invalid data."""
        data = {'schema_version': 'invalid'}
        with pytest.raises(ValueError):
            load_and_validate(data)

    def test_quick_validate_true(self):
        """Test quick_validate returns True for valid data."""
        data = {...}
        assert quick_validate(data) is True

    def test_quick_validate_false(self):
        """Test quick_validate returns False for invalid data."""
        data = {'incomplete': 'data'}
        assert quick_validate(data) is False
```

## Deliverables

1. **load_llms_txt() function**: Primary public API with 6 parameters
2. **LoaderResult class**: Result container with is_valid(), get_summary(), to_dict()
3. **CacheManager class**: Local file cache with TTL and LRU eviction
4. **CacheEntry class**: Cache entry with expiry tracking
5. **LazyValidator class**: Deferred validation wrapper
6. **Convenience functions**: load_and_validate(), load_with_report(), quick_validate(), validate_file()
7. **Module structure**: __init__.py, loader.py, cache.py with proper imports
8. **Logging configuration**: LoaderLogger class with DEBUG/INFO/WARNING/ERROR levels
9. **Performance monitoring**: LoadMetrics and PerformanceMonitor classes
10. **Integration documentation**: Contract with Context Builder v0.3.2
11. **Complete __init__.py**: Exports and documentation
12. **Test suite**: 10+ integration tests

## Acceptance Criteria

- [x] load_llms_txt() accepts file paths, URLs, and dicts
- [x] Returns LoaderResult with is_valid() method
- [x] URL caching implemented with 24-hour default TTL
- [x] Cache stored in ~/.docstratum/cache/ with gzip compression
- [x] Lazy validation mode available (deferred validation)
- [x] Connection pooling via requests.Session
- [x] Convenience functions: load_and_validate(), load_with_report(), quick_validate()
- [x] Module structure with __init__.py, loader.py, cache.py
- [x] Logging at all levels: DEBUG, INFO, WARNING, ERROR
- [x] Performance metrics tracked (load_time_ms, validation_time_ms)
- [x] Cache statistics available (get_stats())
- [x] Integration contract documented for Context Builder
- [x] Full docstrings with examples on all functions
- [x] 10+ integration tests

## Next Step

**v0.3.2** — Context Builder: Implement the context building layer that transforms LlmsTxt objects into structured contexts for LLM prompting, including context assembly, token budgeting, and prompt injection prevention.
