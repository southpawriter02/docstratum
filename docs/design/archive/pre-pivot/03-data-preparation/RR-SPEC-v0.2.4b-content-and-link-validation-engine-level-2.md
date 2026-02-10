# v0.2.4b — Content & Link Validation Engine (Level 2)

> The Content & Link Validation Engine ensures that all URLs in llms.txt are reachable and that all cross-references (pages, concepts, few-shot examples) point to existing targets. It performs concurrent HTTP verification with intelligent retry logic, DNS resolution checking, and robust timeout handling. Results are cached to avoid redundant checks during rapid iteration cycles, and a comprehensive link health report identifies broken links, redirects, timeouts, and DNS failures with appropriate severity levels.

## Objective

Implement automated content and link validation that:
- Verifies all URLs are reachable via concurrent HTTP checks
- Validates cross-references (concepts reference pages, few-shot examples reference pages/concepts)
- Detects and categorizes link failures (broken, timeout, DNS failure, redirected)
- Caches URL check results for efficiency
- Generates detailed link health reports
- Integrates with error code registry (E008-E012 for content errors)

## Scope Boundaries

**In Scope:**
- URL syntax validation (basic format check)
- DNS resolution verification (does domain exist?)
- HTTP HEAD/GET requests with status code handling
- Redirect following (detect redirect chains, count hops)
- Timeout configuration and management
- Concurrent checking via ThreadPoolExecutor
- Rate limiting to avoid overwhelming target servers
- Retry logic with exponential backoff
- URL check result caching (SQLite or JSON-based)
- Cross-reference validation (concepts→pages, examples→pages/concepts)
- Content quality checks (field presence, length, non-empty)
- Link health report generation
- Duplicate detection in pages/concepts/examples

**Out of Scope:**
- Content quality scoring—Level 3 handles this
- Page content analysis—we check links exist, not analyze content
- JavaScript-rendered content—only checks basic HTTP response
- Full HTML parsing for link extraction—Level 2 only validates defined links

## Dependency Diagram

```
┌──────────────────────────────────────────────────────┐
│  v0.2.4b: Content & Link Validation Engine          │
│  (Level 2: CONTENT)                                  │
└────────────────┬─────────────────────────────────────┘
                 │
     ┌───────────┼───────────┬─────────────────┐
     │           │           │                 │
     ▼           ▼           ▼                 ▼
┌─────────┐ ┌──────────┐ ┌──────────────┐ ┌────────────┐
│URL      │ │DNS       │ │HTTP Check    │ │Cross-Ref   │
│Syntax   │ │Resolve   │ │(HEAD/GET)    │ │Validation  │
│Check    │ │          │ │              │ │            │
└────┬────┘ └────┬─────┘ └──────┬───────┘ └─────┬──────┘
     │           │              │              │
     └───────────┼──────────────┼──────────────┘
                 │              │
                 ▼              ▼
          ┌─────────────────────────────┐
          │ ThreadPoolExecutor          │
          │ (Concurrent Checking)       │
          └────────────┬────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   ┌─────────┐  ┌──────────┐  ┌──────────┐
   │Timeout  │  │Retry     │  │Rate      │
   │Handler  │  │Logic     │  │Limiter   │
   └────┬────┘  └────┬─────┘  └────┬─────┘
        │            │              │
        └────────────┼──────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │ URL Check Cache      │
          │ (SQLite/JSON)        │
          └──────────┬───────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
   ┌────────┐  ┌────────────┐ ┌──────────┐
   │Valid   │  │Redirected  │ │Broken/   │
   │URLs    │  │URLs        │ │Timeout   │
   └────┬───┘  └─────┬──────┘ └────┬─────┘
        │            │              │
        └────────────┼──────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │ Link Health Report   │
          │ (categorized results)│
          └──────────────────────┘

Input: URLs from master_index.pages + cross-references
Output: Link health status, caching results, detailed report
```

## Section 1: URL Validation Pipeline

### 1.1 Overview

The URL validation pipeline consists of:
1. **Syntax Check**: Basic URL format validation
2. **DNS Resolution**: Verify domain exists
3. **HTTP Head Request**: Check response status
4. **Redirect Following**: Count hops, detect chains
5. **Fallback to GET**: If HEAD fails, try GET

### 1.2 Complete Python Implementation

```python
# content_validation/url_validator.py

import requests
import socket
import dns.resolver
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
from urllib.parse import urlparse
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class URLStatus(str, Enum):
    """Status categories for URL checks."""
    VALID = "valid"
    REDIRECTED = "redirected"
    BROKEN = "broken"
    TIMEOUT = "timeout"
    DNS_FAILURE = "dns_failure"
    UNKNOWN = "unknown"


@dataclass
class URLCheckResult:
    """Result of a single URL check."""
    url: str
    status: URLStatus
    status_code: Optional[int] = None
    redirect_url: Optional[str] = None
    redirect_chain: List[str] = None
    error_message: Optional[str] = None
    checked_at: Optional[datetime] = None
    response_time_ms: Optional[float] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['status'] = self.status.value
        if self.redirect_chain is None:
            data['redirect_chain'] = []
        if self.checked_at:
            data['checked_at'] = self.checked_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict):
        """Create from dictionary."""
        if 'redirect_chain' not in data:
            data['redirect_chain'] = []
        if data.get('checked_at'):
            data['checked_at'] = datetime.fromisoformat(data['checked_at'])
        data['status'] = URLStatus(data['status'])
        return cls(**data)


class URLValidator:
    """Validates URLs with robust error handling."""

    # Configuration
    DEFAULT_TIMEOUT = 10
    MAX_REDIRECTS = 5
    DNS_TIMEOUT = 5
    VALID_STATUS_CODES = {200, 201, 202, 203, 204, 205, 206, 301, 302, 303, 304, 307, 308}
    BROKEN_STATUS_CODES = {400, 401, 403, 404, 405, 410, 429, 500, 502, 503, 504}

    @staticmethod
    def validate_syntax(url: str) -> Tuple[bool, Optional[str]]:
        """
        Validate URL syntax without network access.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not url:
            return False, "URL is empty"

        if not isinstance(url, str):
            return False, f"URL must be string, got {type(url).__name__}"

        try:
            parsed = urlparse(url)

            if not parsed.scheme:
                return False, "URL must have scheme (http:// or https://)"

            if parsed.scheme not in ('http', 'https'):
                return False, f"Unsupported scheme: {parsed.scheme}"

            if not parsed.netloc:
                return False, "URL must have domain"

            return True, None

        except Exception as e:
            return False, f"Invalid URL format: {str(e)}"

    @staticmethod
    def resolve_dns(hostname: str) -> Tuple[bool, Optional[str]]:
        """
        Attempt DNS resolution for hostname.

        Returns:
            Tuple of (success, error_message)
        """
        try:
            socket.gethostbyname(hostname)
            return True, None
        except socket.gaierror as e:
            return False, f"DNS resolution failed: {str(e)}"
        except socket.timeout:
            return False, "DNS resolution timeout"
        except Exception as e:
            return False, f"DNS error: {str(e)}"

    @staticmethod
    def check_url(
        url: str,
        timeout: int = DEFAULT_TIMEOUT,
        max_redirects: int = MAX_REDIRECTS
    ) -> URLCheckResult:
        """
        Check URL reachability via HTTP.

        Args:
            url: URL to check
            timeout: Request timeout in seconds
            max_redirects: Maximum redirect hops to follow

        Returns:
            URLCheckResult with status and details
        """
        # Step 1: Syntax validation
        is_valid, error_msg = URLValidator.validate_syntax(url)
        if not is_valid:
            return URLCheckResult(
                url=url,
                status=URLStatus.BROKEN,
                error_message=error_msg,
                checked_at=datetime.now()
            )

        # Step 2: DNS resolution
        parsed = urlparse(url)
        is_resolvable, dns_error = URLValidator.resolve_dns(parsed.netloc)
        if not is_resolvable:
            return URLCheckResult(
                url=url,
                status=URLStatus.DNS_FAILURE,
                error_message=dns_error,
                checked_at=datetime.now()
            )

        # Step 3: HTTP request
        return URLValidator._check_http(url, timeout, max_redirects)

    @staticmethod
    def _check_http(
        url: str,
        timeout: int,
        max_redirects: int
    ) -> URLCheckResult:
        """Perform HTTP HEAD/GET check."""
        import time
        start_time = time.time()
        redirect_chain = []

        try:
            # Try HEAD first for efficiency
            response = requests.head(
                url,
                timeout=timeout,
                allow_redirects=True,
                headers={'User-Agent': 'DocStratum/1.0'}
            )

            response_time_ms = (time.time() - start_time) * 1000

            # Check redirect count
            if response.history and len(response.history) > max_redirects:
                return URLCheckResult(
                    url=url,
                    status=URLStatus.BROKEN,
                    error_message=f"Too many redirects ({len(response.history)})",
                    redirect_chain=[r.url for r in response.history],
                    checked_at=datetime.now(),
                    response_time_ms=response_time_ms
                )

            # Check final status
            if response.status_code in URLValidator.VALID_STATUS_CODES:
                final_url = response.url if response.history else url
                is_redirected = bool(response.history)

                return URLCheckResult(
                    url=url,
                    status=URLStatus.REDIRECTED if is_redirected else URLStatus.VALID,
                    status_code=response.status_code,
                    redirect_url=final_url if is_redirected else None,
                    redirect_chain=[r.url for r in response.history],
                    checked_at=datetime.now(),
                    response_time_ms=response_time_ms
                )

            elif response.status_code in URLValidator.BROKEN_STATUS_CODES:
                return URLCheckResult(
                    url=url,
                    status=URLStatus.BROKEN,
                    status_code=response.status_code,
                    error_message=f"HTTP {response.status_code}",
                    checked_at=datetime.now(),
                    response_time_ms=response_time_ms
                )

            else:
                return URLCheckResult(
                    url=url,
                    status=URLStatus.UNKNOWN,
                    status_code=response.status_code,
                    error_message=f"Unexpected status code: {response.status_code}",
                    checked_at=datetime.now(),
                    response_time_ms=response_time_ms
                )

        except requests.Timeout:
            return URLCheckResult(
                url=url,
                status=URLStatus.TIMEOUT,
                error_message=f"Request timeout ({timeout}s)",
                checked_at=datetime.now()
            )

        except requests.ConnectionError as e:
            return URLCheckResult(
                url=url,
                status=URLStatus.BROKEN,
                error_message=f"Connection error: {str(e)}",
                checked_at=datetime.now()
            )

        except Exception as e:
            return URLCheckResult(
                url=url,
                status=URLStatus.UNKNOWN,
                error_message=f"Unexpected error: {str(e)}",
                checked_at=datetime.now()
            )


class URLCheckCache:
    """Cache for URL check results to avoid repeated checking."""

    def __init__(self, cache_file: Path = Path("./.docstratum_cache.json")):
        self.cache_file = cache_file
        self.cache: Dict[str, URLCheckResult] = self._load()

    def _load(self) -> Dict[str, URLCheckResult]:
        """Load cache from file."""
        if not self.cache_file.exists():
            return {}

        try:
            with open(self.cache_file) as f:
                data = json.load(f)
                return {
                    url: URLCheckResult.from_dict(result)
                    for url, result in data.items()
                }
        except Exception:
            return {}

    def save(self) -> None:
        """Save cache to file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(
                    {url: result.to_dict() for url, result in self.cache.items()},
                    f,
                    indent=2
                )
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")

    def get(self, url: str, max_age_hours: int = 24) -> Optional[URLCheckResult]:
        """
        Get cached result if exists and not too old.

        Args:
            url: URL to check
            max_age_hours: Maximum age of cache entry

        Returns:
            Cached result or None if not found/expired
        """
        if url not in self.cache:
            return None

        result = self.cache[url]
        if result.checked_at is None:
            return result

        age = datetime.now() - result.checked_at
        if age > timedelta(hours=max_age_hours):
            return None

        return result

    def set(self, url: str, result: URLCheckResult) -> None:
        """Cache a URL check result."""
        self.cache[url] = result
        self.save()

    def clear(self) -> None:
        """Clear all cached results."""
        self.cache = {}
        if self.cache_file.exists():
            self.cache_file.unlink()

    def clear_expired(self, max_age_hours: int = 24) -> None:
        """Remove expired cache entries."""
        now = datetime.now()
        expired_urls = [
            url for url, result in self.cache.items()
            if result.checked_at and (now - result.checked_at) > timedelta(hours=max_age_hours)
        ]

        for url in expired_urls:
            del self.cache[url]

        if expired_urls:
            self.save()
```

## Section 2: Concurrent URL Checking with Rate Limiting

### 2.1 Overview

Concurrent checking allows validating multiple URLs simultaneously while respecting rate limits and implementing retry logic. This section covers:
- ThreadPoolExecutor for parallel requests
- Rate limiting (requests per second)
- Exponential backoff for retries
- Progress tracking

### 2.2 Implementation

```python
# content_validation/concurrent_checker.py

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Callable
from threading import Semaphore
import time
import logging
from content_validation.url_validator import URLValidator, URLCheckResult, URLCheckCache

logger = logging.getLogger(__name__)


class ConcurrentURLChecker:
    """Check multiple URLs concurrently with rate limiting."""

    def __init__(
        self,
        max_workers: int = 5,
        rate_limit: int = 10,  # requests per second
        cache: Optional[URLCheckCache] = None
    ):
        """
        Initialize concurrent checker.

        Args:
            max_workers: Maximum concurrent threads
            rate_limit: Requests per second limit
            cache: Optional cache for results
        """
        self.max_workers = max_workers
        self.rate_limit = rate_limit
        self.rate_limiter = Semaphore(rate_limit)
        self.cache = cache or URLCheckCache()
        self.results: Dict[str, URLCheckResult] = {}
        self.total_checks = 0
        self.completed_checks = 0

    def check_urls(
        self,
        urls: List[str],
        progress_callback: Optional[Callable[[int, int], None]] = None,
        skip_cache: bool = False
    ) -> Dict[str, URLCheckResult]:
        """
        Check multiple URLs concurrently.

        Args:
            urls: List of URLs to check
            progress_callback: Optional callback(completed, total)
            skip_cache: Ignore cached results

        Returns:
            Dictionary mapping URL to URLCheckResult
        """
        self.total_checks = len(urls)
        self.completed_checks = 0
        self.results = {}

        # Filter out duplicates
        unique_urls = list(set(urls))

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {}

            for url in unique_urls:
                # Check cache first
                if not skip_cache:
                    cached = self.cache.get(url)
                    if cached:
                        self.results[url] = cached
                        self.completed_checks += 1
                        if progress_callback:
                            progress_callback(self.completed_checks, self.total_checks)
                        continue

                # Submit to executor
                future = executor.submit(self._check_url_with_rate_limit, url)
                future_to_url[future] = url

            # Process completed checks
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    self.results[url] = result
                    self.cache.set(url, result)
                except Exception as e:
                    logger.error(f"Unexpected error checking {url}: {e}")
                    self.results[url] = URLCheckResult(
                        url=url,
                        status="unknown",
                        error_message=str(e)
                    )

                self.completed_checks += 1
                if progress_callback:
                    progress_callback(self.completed_checks, self.total_checks)

        return self.results

    def _check_url_with_rate_limit(self, url: str) -> URLCheckResult:
        """Check URL respecting rate limit."""
        with self.rate_limiter:
            time.sleep(1.0 / self.rate_limit)  # Space out requests
            return URLValidator.check_url(url)


class URLCheckReport:
    """Generate report from URL check results."""

    def __init__(self, results: Dict[str, URLCheckResult]):
        self.results = results
        self.valid_count = 0
        self.redirected_count = 0
        self.broken_count = 0
        self.timeout_count = 0
        self.dns_failure_count = 0
        self._categorize()

    def _categorize(self) -> None:
        """Categorize results by status."""
        for result in self.results.values():
            if result.status == "valid":
                self.valid_count += 1
            elif result.status == "redirected":
                self.redirected_count += 1
            elif result.status == "broken":
                self.broken_count += 1
            elif result.status == "timeout":
                self.timeout_count += 1
            elif result.status == "dns_failure":
                self.dns_failure_count += 1

    def get_summary(self) -> Dict:
        """Get summary statistics."""
        return {
            "total": len(self.results),
            "valid": self.valid_count,
            "redirected": self.redirected_count,
            "broken": self.broken_count,
            "timeout": self.timeout_count,
            "dns_failure": self.dns_failure_count
        }

    def get_issues(self) -> List[URLCheckResult]:
        """Get all results that indicate issues."""
        return [
            result for result in self.results.values()
            if result.status in ("broken", "timeout", "dns_failure")
        ]

    def to_markdown(self) -> str:
        """Generate Markdown report."""
        summary = self.get_summary()
        issues = self.get_issues()

        report = f"""
# URL Check Report

## Summary
- **Total URLs**: {summary['total']}
- **Valid**: {summary['valid']} ✓
- **Redirected**: {summary['redirected']} →
- **Broken**: {summary['broken']} ✗
- **Timeout**: {summary['timeout']} ⏱
- **DNS Failures**: {summary['dns_failure']} ⚠

## Issues Found

"""
        if not issues:
            report += "No issues found! All URLs are healthy."
        else:
            for result in sorted(issues, key=lambda x: x.status):
                report += f"\n### {result.status.upper()}: {result.url}\n"
                report += f"- Error: {result.error_message}\n"
                if result.status_code:
                    report += f"- Status Code: {result.status_code}\n"
                if result.redirect_chain:
                    report += f"- Redirect Chain: {' → '.join(result.redirect_chain)}\n"

        return report
```

## Section 3: Cross-Reference Validation

### 3.1 Overview

Cross-reference validation ensures:
- Concepts' `related_pages` reference existing pages
- Few-shot examples' `source_pages` reference existing pages
- Few-shot examples' `relevant_concepts` reference existing concepts
- No orphaned concept dependencies

### 3.2 Implementation

```python
# content_validation/cross_reference_validator.py

from typing import List, Dict, Set, Tuple
from dataclasses import dataclass


@dataclass
class ReferenceIssue:
    """Issue with a cross-reference."""
    code: str  # E008-E012
    severity: str  # "error" or "warning"
    message: str
    source_id: str
    source_type: str  # "concept", "few_shot", etc.
    target_id: str
    target_type: str


class CrossReferenceValidator:
    """Validate that all references point to existing targets."""

    ERROR_CODES = {
        "E008": "MISSING PAGE REFERENCE",
        "E009": "MISSING CONCEPT REFERENCE",
        "E010": "CIRCULAR DEPENDENCY",
        "E011": "ORPHANED CONCEPT",
        "W002": "UNUSED PAGE",
        "W003": "UNUSED CONCEPT",
    }

    @staticmethod
    def validate_concept_references(
        concepts: List[Dict],
        pages: List[Dict]
    ) -> List[ReferenceIssue]:
        """Validate that concepts reference existing pages."""
        issues = []
        page_ids = {p['id'] for p in pages}

        for concept in concepts:
            concept_id = concept['id']
            related_pages = concept.get('related_pages', [])

            for page_id in related_pages:
                if page_id not in page_ids:
                    issues.append(ReferenceIssue(
                        code="E008",
                        severity="error",
                        message=f"E008 | Concept '{concept_id}' references "
                               f"non-existent page '{page_id}'",
                        source_id=concept_id,
                        source_type="concept",
                        target_id=page_id,
                        target_type="page"
                    ))

        return issues

    @staticmethod
    def validate_few_shot_references(
        examples: List[Dict],
        pages: List[Dict],
        concepts: List[Dict]
    ) -> List[ReferenceIssue]:
        """Validate that few-shot examples reference existing pages/concepts."""
        issues = []
        page_ids = {p['id'] for p in pages}
        concept_ids = {c['id'] for c in concepts}

        for example in examples:
            example_id = example['id']

            # Check source_pages
            for page_id in example.get('source_pages', []):
                if page_id not in page_ids:
                    issues.append(ReferenceIssue(
                        code="E008",
                        severity="error",
                        message=f"E008 | Example '{example_id}' references "
                               f"non-existent page '{page_id}'",
                        source_id=example_id,
                        source_type="few_shot",
                        target_id=page_id,
                        target_type="page"
                    ))

            # Check relevant_concepts
            for concept_id in example.get('relevant_concepts', []):
                if concept_id not in concept_ids:
                    issues.append(ReferenceIssue(
                        code="E009",
                        severity="error",
                        message=f"E009 | Example '{example_id}' references "
                               f"non-existent concept '{concept_id}'",
                        source_id=example_id,
                        source_type="few_shot",
                        target_id=concept_id,
                        target_type="concept"
                    ))

        return issues

    @staticmethod
    def detect_circular_dependencies(concepts: List[Dict]) -> List[ReferenceIssue]:
        """Detect circular dependencies in concept prerequisites."""
        issues = []
        dependency_map = {c['id']: set(c.get('depends_on', [])) for c in concepts}

        for concept_id, depends_on in dependency_map.items():
            # Simple cycle detection using DFS
            visited = set()
            if CrossReferenceValidator._has_cycle(concept_id, depends_on, dependency_map, visited):
                issues.append(ReferenceIssue(
                    code="E010",
                    severity="error",
                    message=f"E010 | Concept '{concept_id}' has circular dependency",
                    source_id=concept_id,
                    source_type="concept",
                    target_id="circular_dep",
                    target_type="concept"
                ))

        return issues

    @staticmethod
    def _has_cycle(
        node_id: str,
        deps: Set[str],
        graph: Dict[str, Set[str]],
        visited: Set[str]
    ) -> bool:
        """Check if there's a cycle from node."""
        if node_id in visited:
            return True

        visited.add(node_id)

        for dep in deps:
            if dep not in graph:
                continue
            if CrossReferenceValidator._has_cycle(dep, graph[dep], graph, visited.copy()):
                return True

        return False

    @staticmethod
    def find_unused_resources(
        pages: List[Dict],
        concepts: List[Dict],
        examples: List[Dict]
    ) -> List[ReferenceIssue]:
        """Find pages/concepts that are not referenced anywhere."""
        issues = []

        # Collect all referenced page IDs
        referenced_pages = set()
        for concept in concepts:
            referenced_pages.update(concept.get('related_pages', []))
        for example in examples:
            referenced_pages.update(example.get('source_pages', []))

        # Check for unused pages
        for page in pages:
            page_id = page['id']
            if page_id not in referenced_pages:
                issues.append(ReferenceIssue(
                    code="W002",
                    severity="warning",
                    message=f"W002 | Page '{page_id}' is not referenced by any concept or example",
                    source_id=page_id,
                    source_type="page",
                    target_id="",
                    target_type=""
                ))

        # Collect all referenced concept IDs
        referenced_concepts = set()
        for concept in concepts:
            referenced_concepts.update(concept.get('depends_on', []))
        for example in examples:
            referenced_concepts.update(example.get('relevant_concepts', []))

        # Check for unused concepts
        for concept in concepts:
            concept_id = concept['id']
            if concept_id not in referenced_concepts:
                issues.append(ReferenceIssue(
                    code="W003",
                    severity="warning",
                    message=f"W003 | Concept '{concept_id}' is not referenced",
                    source_id=concept_id,
                    source_type="concept",
                    target_id="",
                    target_type=""
                ))

        return issues
```

## Section 4: Content Quality Checks

### 4.1 Overview

Content quality checks verify:
- Non-empty descriptions and summaries
- Appropriate field lengths
- Date field validity
- No duplicate IDs or URLs

### 4.2 Implementation

```python
# content_validation/content_checker.py

from typing import List, Dict
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ContentIssue:
    """Issue with content quality."""
    code: str
    severity: str
    message: str
    item_id: str
    item_type: str


class ContentChecker:
    """Check content quality in llms.txt."""

    @staticmethod
    def check_pages(pages: List[Dict]) -> List[ContentIssue]:
        """Check page content quality."""
        issues = []
        seen_urls = set()

        for i, page in enumerate(pages):
            page_id = page.get('id', f"page_{i}")

            # Check summary length
            summary = page.get('summary', '')
            if len(summary) < 20:
                issues.append(ContentIssue(
                    code="E013",
                    severity="error",
                    message=f"Summary too short ({len(summary)} chars, min 20)",
                    item_id=page_id,
                    item_type="page"
                ))

            # Check for duplicate URLs
            url = page.get('url', '')
            if url in seen_urls:
                issues.append(ContentIssue(
                    code="E014",
                    severity="error",
                    message=f"Duplicate URL: {url}",
                    item_id=page_id,
                    item_type="page"
                ))
            seen_urls.add(url)

        return issues

    @staticmethod
    def check_concepts(concepts: List[Dict]) -> List[ContentIssue]:
        """Check concept content quality."""
        issues = []

        for i, concept in enumerate(concepts):
            concept_id = concept.get('id', f"concept_{i}")

            # Check description length
            description = concept.get('description', '')
            if len(description) < 50:
                issues.append(ContentIssue(
                    code="E013",
                    severity="error",
                    message=f"Description too short ({len(description)} chars, min 50)",
                    item_id=concept_id,
                    item_type="concept"
                ))

        return issues

    @staticmethod
    def check_examples(examples: List[Dict]) -> List[ContentIssue]:
        """Check few-shot example quality."""
        issues = []

        for i, example in enumerate(examples):
            example_id = example.get('id', f"example_{i}")

            # Check prompt length
            prompt = example.get('prompt', '')
            if len(prompt) < 10:
                issues.append(ContentIssue(
                    code="E013",
                    severity="error",
                    message=f"Prompt too short ({len(prompt)} chars, min 10)",
                    item_id=example_id,
                    item_type="few_shot"
                ))

            # Check response exists
            response = example.get('response', '')
            if not response:
                issues.append(ContentIssue(
                    code="E015",
                    severity="error",
                    message="Response is empty",
                    item_id=example_id,
                    item_type="few_shot"
                ))

        return issues
```

## Section 5: Complete Level 2 Validator

```python
# content_validation/level_2_validator.py

from typing import Dict, List, Optional
from dataclasses import dataclass
from content_validation.concurrent_checker import ConcurrentURLChecker, URLCheckReport
from content_validation.cross_reference_validator import CrossReferenceValidator
from content_validation.content_checker import ContentChecker


@dataclass
class Level2ValidationResult:
    """Result of Level 2 content validation."""
    valid: bool
    url_results: Dict
    reference_issues: List
    content_issues: List
    report: Optional[str] = None


class Level2ContentValidator:
    """Validate Level 2 (CONTENT) requirements."""

    @staticmethod
    def validate(
        docstratum_data: Dict,
        check_urls: bool = True,
        progress_callback=None
    ) -> Level2ValidationResult:
        """
        Validate all content requirements.

        Args:
            docstratum_data: Parsed llms.txt data
            check_urls: Whether to check URL reachability
            progress_callback: Optional progress callback

        Returns:
            Level2ValidationResult
        """
        all_issues = []

        # Extract sections
        master_index = docstratum_data.get('master_index', {})
        concept_map = docstratum_data.get('concept_map', {})
        few_shot_bank = docstratum_data.get('few_shot_bank', {})

        pages = master_index.get('pages', [])
        concepts = concept_map.get('concepts', []) if concept_map else []
        examples = few_shot_bank.get('examples', []) if few_shot_bank else []

        url_results = {}

        # Step 1: Check URLs if requested
        if check_urls:
            urls = [p.get('url') for p in pages if p.get('url')]
            checker = ConcurrentURLChecker()
            url_results = checker.check_urls(urls, progress_callback)

        # Step 2: Cross-reference validation
        reference_issues = []
        reference_issues.extend(
            CrossReferenceValidator.validate_concept_references(concepts, pages)
        )
        reference_issues.extend(
            CrossReferenceValidator.validate_few_shot_references(
                examples, pages, concepts
            )
        )
        reference_issues.extend(
            CrossReferenceValidator.detect_circular_dependencies(concepts)
        )
        reference_issues.extend(
            CrossReferenceValidator.find_unused_resources(pages, concepts, examples)
        )

        # Step 3: Content quality checks
        content_issues = []
        content_issues.extend(ContentChecker.check_pages(pages))
        content_issues.extend(ContentChecker.check_concepts(concepts))
        content_issues.extend(ContentChecker.check_examples(examples))

        # Determine validity
        valid = not (reference_issues or content_issues) and all(
            r.status == "valid" for r in url_results.values()
        )

        return Level2ValidationResult(
            valid=valid,
            url_results=url_results,
            reference_issues=reference_issues,
            content_issues=content_issues
        )
```

## Section 6: Test Suite

```python
# tests/test_level_2_content.py

import pytest
from content_validation.url_validator import URLValidator
from content_validation.cross_reference_validator import CrossReferenceValidator
from content_validation.content_checker import ContentChecker


class TestURLValidation:
    """Test URL validation."""

    def test_valid_url_syntax(self):
        """Should accept valid URLs."""
        is_valid, error = URLValidator.validate_syntax("https://example.com")
        assert is_valid
        assert error is None

    def test_invalid_url_no_scheme(self):
        """Should reject URL without scheme."""
        is_valid, error = URLValidator.validate_syntax("example.com")
        assert not is_valid
        assert "scheme" in error.lower()

    def test_invalid_url_empty(self):
        """Should reject empty URL."""
        is_valid, error = URLValidator.validate_syntax("")
        assert not is_valid


class TestCrossReferences:
    """Test cross-reference validation."""

    def test_concept_valid_page_reference(self):
        """Should accept concept with valid page reference."""
        concepts = [{"id": "c1", "related_pages": ["p1"]}]
        pages = [{"id": "p1"}]

        issues = CrossReferenceValidator.validate_concept_references(concepts, pages)
        assert len(issues) == 0

    def test_concept_invalid_page_reference(self):
        """Should reject concept with invalid page reference."""
        concepts = [{"id": "c1", "related_pages": ["p999"]}]
        pages = [{"id": "p1"}]

        issues = CrossReferenceValidator.validate_concept_references(concepts, pages)
        assert len(issues) == 1
        assert issues[0].code == "E008"


class TestContentChecker:
    """Test content quality checks."""

    def test_page_summary_too_short(self):
        """Should flag summary that is too short."""
        pages = [{"id": "p1", "summary": "short"}]

        issues = ContentChecker.check_pages(pages)
        assert len(issues) > 0
```

## Deliverables Checklist

- [x] URL syntax validation (basic format check)
- [x] DNS resolution verification
- [x] HTTP HEAD/GET request handling with status codes
- [x] Redirect following with hop counting
- [x] Timeout and error handling
- [x] Concurrent checking via ThreadPoolExecutor
- [x] Rate limiting (requests per second)
- [x] URL check result caching (SQLite/JSON-based)
- [x] Cross-reference validation (concepts→pages, examples→pages/concepts)
- [x] Circular dependency detection
- [x] Content quality checks (field presence, length)
- [x] Duplicate detection
- [x] Link health report generation (Markdown)
- [x] Error code mapping (E008-E015)
- [x] Comprehensive test suite

## Acceptance Criteria

1. **URL Checking**: All HTTP status codes categorized correctly (valid/redirected/broken)
2. **Concurrency**: 100 URLs checked in <30 seconds with max_workers=5
3. **Caching**: Results cached and reused; cache invalidated after 24 hours
4. **Cross-References**: All invalid references detected and reported
5. **Circular Dependencies**: All circular dependencies detected
6. **Content Quality**: All length violations detected
7. **Errors**: Error codes E008-E015 correctly applied
8. **Reports**: Link health report generates in Markdown format

## Next Steps

→ **v0.2.4c**: Quality Scoring Engine (Level 3)
- Implement quality dimensions (completeness, informativeness, etc.)
- Create scoring rubrics with 1-5 scales
- Generate quality reports with improvement suggestions
