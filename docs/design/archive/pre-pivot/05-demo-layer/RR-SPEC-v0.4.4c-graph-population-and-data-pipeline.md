# v0.4.4c — Graph Population & Data Pipeline

> **Task:** Build the data pipeline for populating Neo4j from the DocStratum YAML/llms.txt data. This document specifies the populate_neo4j.py implementation design, data extraction patterns, clear-and-rebuild vs. incremental update strategies, batch import optimization, error handling and retry logic, population verification, and CLI interface.

---

## Objective

Design and implement a robust data pipeline (populate_neo4j.py) that extracts concepts and dependencies from the DocStratum YAML/llms.txt source files and populates Neo4j with optimized Concept nodes and DEPENDS_ON relationships. The pipeline must support multiple update strategies, include comprehensive error handling, verify data integrity, and provide a user-friendly CLI interface.

---

## Scope Boundaries

| Aspect | In Scope | Out of Scope |
|--------|----------|--------------|
| **Data Source** | core.loader.load_llms_txt(), YAML/Markdown parsing | Direct SQL, REST API sources |
| **Update Strategies** | Clear-and-rebuild, incremental append, selective replace | Time-travel versioning, A/B testing |
| **Batch Operations** | Batch import of nodes, bulk relationship creation | Streaming import, real-time sync |
| **Error Handling** | Validation, retries, rollback, detailed logging | Self-healing, ML-based correction |
| **Verification** | Query-based validation, count checks, integrity audits | Visual inspection, manual verification |
| **CLI Interface** | Command-line options, progress reporting, config files | Web UI, API endpoints, interactive REPL |
| **Performance** | Batch size optimization, transaction batching | Distributed graph partitioning, sharding |
| **Monitoring** | Success/failure logs, execution metrics | Real-time alerting, Prometheus metrics |

---

## Dependency Diagram

```
┌─────────────────────────────────────────────────┐
│   Core Loader (core.loader.load_llms_txt)       │
│  Reads YAML/llms.txt → Pydantic Models          │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│   Docker Infrastructure (v0.4.4b)               │
│  Neo4j 5 Community, ports 7474/7687            │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│   Graph Population (THIS DOCUMENT)               │
│  populate_neo4j.py: extract, validate, load    │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│   Visualization & Export (v0.4.4d)              │
│  Obsidian export, Streamlit graph display      │
└─────────────────────────────────────────────────┘
```

---

## 1. populate_neo4j.py Implementation Design

### 1.1 Architecture Overview

```python
# scripts/populate_neo4j.py

from neo4j import GraphDatabase
from pydantic import BaseModel, ValidationError
from core.loader import load_llms_txt
import logging
from typing import List, Dict, Tuple
from datetime import datetime
from dataclasses import dataclass

@dataclass
class PopulationMetrics:
    """Track population statistics"""
    concepts_created: int = 0
    concepts_updated: int = 0
    relationships_created: int = 0
    relationships_failed: int = 0
    execution_time_ms: float = 0.0
    errors: List[str] = None

class DocStratumNeo4jPopulator:
    """Main class for populating Neo4j with DocStratum concepts"""

    def __init__(self, uri: str, username: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.logger = logging.getLogger(__name__)
        self.metrics = PopulationMetrics()

    def close(self):
        self.driver.close()

    def populate(self, llms_txt_path: str, strategy: str = "clear-rebuild"):
        """Main entry point for population"""
        start_time = datetime.now()

        try:
            # 1. Load concepts from source
            concepts = load_llms_txt(llms_txt_path)
            self.logger.info(f"Loaded {len(concepts)} concepts from {llms_txt_path}")

            # 2. Execute population strategy
            if strategy == "clear-rebuild":
                self._clear_and_rebuild(concepts)
            elif strategy == "incremental":
                self._incremental_update(concepts)
            elif strategy == "selective":
                self._selective_replace(concepts)
            else:
                raise ValueError(f"Unknown strategy: {strategy}")

            # 3. Verify population
            self._verify_population(concepts)

            # 4. Report metrics
            end_time = datetime.now()
            self.metrics.execution_time_ms = (end_time - start_time).total_seconds() * 1000
            self._report_metrics()

        except Exception as e:
            self.logger.error(f"Population failed: {str(e)}", exc_info=True)
            raise

    # Implementation methods follow in sections below
```

### 1.2 Data Extraction Pattern

```python
def _extract_concepts(self, raw_data: Dict) -> List[Dict]:
    """Extract and validate concepts from raw YAML data"""
    extracted_concepts = []
    validation_errors = []

    for concept_id, concept_data in raw_data.items():
        try:
            # Normalize data structure
            normalized = {
                'id': concept_id,
                'name': concept_data.get('name', concept_id),
                'definition': concept_data.get('definition', ''),
                'layer': concept_data.get('layer', 'concept_map'),
                'category': concept_data.get('category', ''),
                'tags': concept_data.get('tags', []),
                'dependencies': concept_data.get('dependencies', []),
                'metadata': concept_data.get('metadata', {})
            }

            # Validate required fields
            if not normalized['id']:
                raise ValueError("Concept 'id' is required")
            if not normalized['name']:
                raise ValueError("Concept 'name' is required")

            extracted_concepts.append(normalized)

        except ValidationError as e:
            validation_errors.append({
                'concept_id': concept_id,
                'error': str(e)
            })
            self.logger.warning(f"Validation error for {concept_id}: {e}")

    if validation_errors:
        self.logger.warning(f"Extracted {len(extracted_concepts)} concepts with {len(validation_errors)} validation errors")
        self.metrics.errors = validation_errors

    return extracted_concepts
```

---

## 2. Data Extraction from core.loader.load_llms_txt()

### 2.1 Integration Pattern

```python
from core.loader import load_llms_txt
from core.models import Concept, ConceptMap, MasterIndex

def load_and_extract_concepts(llms_txt_path: str) -> Tuple[List[Dict], List[Tuple[str, str]]]:
    """
    Load DocStratum concepts and extract nodes + edges

    Returns:
        (concepts_list, dependencies_list)
        - concepts_list: List of concept dicts with id, name, definition, etc.
        - dependencies_list: List of (source_id, target_id) tuples
    """
    # Load from YAML/llms.txt
    docstratum = load_llms_txt(llms_txt_path)

    concepts = []
    dependencies = []

    # Extract from Master Index layer
    for concept in docstratum.master_index.concepts:
        concepts.append({
            'id': concept.id,
            'name': concept.name,
            'definition': concept.definition,
            'layer': 'master_index',
            'category': getattr(concept, 'category', ''),
            'metadata': concept.metadata or {}
        })

    # Extract from Concept Map layer
    for concept in docstratum.concept_map.concepts:
        concepts.append({
            'id': concept.id,
            'name': concept.name,
            'definition': concept.definition,
            'layer': 'concept_map',
            'category': getattr(concept, 'category', ''),
            'metadata': concept.metadata or {}
        })
        # Extract dependencies
        if hasattr(concept, 'dependencies') and concept.dependencies:
            for dep_id in concept.dependencies:
                dependencies.append((concept.id, dep_id))

    # Extract from Few-Shot Bank layer
    for concept in docstratum.few_shot_bank.concepts:
        concepts.append({
            'id': concept.id,
            'name': concept.name,
            'definition': concept.definition,
            'layer': 'few_shot_bank',
            'category': getattr(concept, 'category', ''),
            'metadata': concept.metadata or {}
        })
        if hasattr(concept, 'dependencies') and concept.dependencies:
            for dep_id in concept.dependencies:
                dependencies.append((concept.id, dep_id))

    return concepts, dependencies
```

### 2.2 Data Flow Diagram (ASCII)

```
┌──────────────────────┐
│  llms.txt / YAML     │
│  (on disk)           │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────────────┐
│ core.loader.load_llms_txt()          │
│ Parses YAML → Pydantic models        │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│ DocStratum object                   │
│ ├─ master_index: ConceptList         │
│ ├─ concept_map: ConceptList          │
│ └─ few_shot_bank: ConceptList        │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│ _extract_concepts()                  │
│ Normalize & validate each concept    │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│ Extracted Data Structures:           │
│ concepts[] = [                       │
│   {id, name, definition, layer, ...} │
│ ]                                    │
│ dependencies[] = [                   │
│   (source_id, target_id),            │
│   ...                                │
│ ]                                    │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│ Neo4j Population (sections 3-4)      │
│ Create nodes, create edges           │
└──────────────────────────────────────┘
```

---

## 3. Update Strategies: Clear-and-Rebuild vs. Incremental

### 3.1 Clear-and-Rebuild Strategy

**Approach:** Delete all existing nodes and relationships, then recreate from source.

**Use Cases:** Initial setup, schema changes, quarterly refreshes.

```python
def _clear_and_rebuild(self, concepts: List[Dict]):
    """Delete all existing data and rebuild from scratch"""

    with self.driver.session() as session:
        # Step 1: Delete all nodes and relationships
        self.logger.info("Clearing existing graph...")
        session.run("MATCH (n) DETACH DELETE n")

        # Step 2: Create unique constraints
        self.logger.info("Creating constraints...")
        session.run("""
            CREATE CONSTRAINT IF NOT EXISTS
            FOR (c:Concept) REQUIRE c.id IS UNIQUE
        """)

        # Step 3: Create indexes
        self.logger.info("Creating indexes...")
        self._create_indexes(session)

        # Step 4: Batch insert nodes
        self.logger.info(f"Creating {len(concepts)} concept nodes...")
        self._batch_insert_nodes(session, concepts)

        # Step 5: Create relationships
        self.logger.info("Creating relationships...")
        self._batch_create_relationships(session, concepts)

        self.logger.info("Clear-and-rebuild completed successfully")
```

**Advantages:**
- Simple, reliable, predictable
- Ensures no orphaned data
- Good for testing

**Disadvantages:**
- Downtime for graph queries during rebuild
- Not suitable for large production graphs
- Loses audit trail

### 3.2 Incremental Update Strategy

**Approach:** Add new concepts and relationships, skip existing ones.

**Use Cases:** Regular updates, append-only workflows.

```python
def _incremental_update(self, concepts: List[Dict]):
    """Add new concepts without removing existing ones"""

    with self.driver.session() as session:
        # Step 1: Determine which concepts are new
        existing_ids = self._get_existing_concept_ids(session)
        new_concepts = [c for c in concepts if c['id'] not in existing_ids]
        updated_concepts = [c for c in concepts if c['id'] in existing_ids]

        self.logger.info(f"Found {len(new_concepts)} new concepts, {len(updated_concepts)} existing")

        # Step 2: Insert new concepts
        if new_concepts:
            self.logger.info(f"Inserting {len(new_concepts)} new concepts...")
            self._batch_insert_nodes(session, new_concepts)
            self.metrics.concepts_created = len(new_concepts)

        # Step 3: Selectively update existing concepts
        if updated_concepts:
            self.logger.info(f"Updating {len(updated_concepts)} existing concepts...")
            self._selective_update_nodes(session, updated_concepts)
            self.metrics.concepts_updated = len(updated_concepts)

        # Step 4: Add missing relationships (idempotent)
        self.logger.info("Syncing relationships...")
        self._batch_create_relationships(session, concepts)

        self.logger.info("Incremental update completed successfully")
```

**Advantages:**
- Minimal downtime
- Preserves historical relationships
- Fast for small changes

**Disadvantages:**
- Complexity with deletions
- Potential for orphaned data
- May require manual cleanup

### 3.3 Selective Replace Strategy

**Approach:** Replace only specific concepts, preserve others.

**Use Cases:** Targeted fixes, layer-specific updates.

```python
def _selective_replace(self, concepts: List[Dict], target_layer: str = None):
    """Replace specific concepts (optionally filtered by layer)"""

    with self.driver.session() as session:
        if target_layer:
            # Delete only concepts in target layer
            self.logger.info(f"Removing concepts from layer: {target_layer}...")
            session.run(f"""
                MATCH (c:Concept {{layer: '{target_layer}'}})
                DETACH DELETE c
            """)
            # Only insert concepts from that layer
            filtered_concepts = [c for c in concepts if c['layer'] == target_layer]
        else:
            # Delete all and rebuild
            filtered_concepts = concepts
            session.run("MATCH (n) DETACH DELETE n")

        self.logger.info(f"Inserting {len(filtered_concepts)} concepts...")
        self._batch_insert_nodes(session, filtered_concepts)
        self._batch_create_relationships(session, filtered_concepts)

        self.logger.info("Selective replace completed successfully")
```

### 3.4 Strategy Comparison Table

| Aspect | Clear-Rebuild | Incremental | Selective |
|--------|---|---|---|
| **Data Loss Risk** | None (complete rebuild) | Low (only new/updates) | Low (by layer) |
| **Downtime** | Medium (all operations) | Low (only new data) | Low (target layer) |
| **Duplicate Prevention** | Automatic | Requires dedup logic | Requires filtering |
| **Performance** | O(n) | O(new items) | O(layer items) |
| **Rollback** | Simple (all or nothing) | Complex (mixed state) | Medium (by layer) |
| **Best For** | Initial load, testing | Production updates | Targeted fixes |

---

## 4. Batch Import Optimization

### 4.1 Batch Insert Nodes (Optimized)

```python
def _batch_insert_nodes(self, session, concepts: List[Dict], batch_size: int = 1000):
    """
    Batch insert concepts into Neo4j

    Optimal batch sizes:
    - 1000-5000 nodes: Best performance for typical use case
    - Larger batches: More memory overhead, minimal speed gain
    """
    total_concepts = len(concepts)

    for i in range(0, total_concepts, batch_size):
        batch = concepts[i:i+batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total_concepts + batch_size - 1) // batch_size

        self.logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} concepts)")

        # Build parameterized Cypher query
        cypher = """
        UNWIND $concepts AS concept
        CREATE (c:Concept {
            id: concept.id,
            name: concept.name,
            definition: concept.definition,
            layer: concept.layer,
            category: concept.category,
            created_at: datetime(),
            updated_at: datetime(),
            source_file: concept.source_file,
            metadata: concept.metadata
        })
        RETURN count(c) as created_count
        """

        try:
            result = session.run(cypher, concepts=batch)
            created = result.single()['created_count']
            self.metrics.concepts_created += created
            self.logger.debug(f"  ✓ Batch {batch_num}: Created {created} concepts")

        except Exception as e:
            self.logger.error(f"  ✗ Batch {batch_num} failed: {str(e)}", exc_info=True)
            # Retry with smaller batches on failure
            if batch_size > 100:
                self.logger.info(f"  Retrying batch {batch_num} with smaller batch size...")
                self._batch_insert_nodes(session, batch, batch_size=100)
            else:
                raise

    self.logger.info(f"Batch insert completed: {self.metrics.concepts_created} concepts created")
```

### 4.2 Batch Create Relationships (Optimized)

```python
def _batch_create_relationships(self, session, concepts: List[Dict], batch_size: int = 5000):
    """Batch create DEPENDS_ON relationships"""

    # Flatten all dependencies from all concepts
    all_dependencies = []
    for concept in concepts:
        for dep_id in concept.get('dependencies', []):
            all_dependencies.append({
                'source': concept['id'],
                'target': dep_id
            })

    if not all_dependencies:
        self.logger.info("No dependencies to create")
        return

    total_deps = len(all_dependencies)
    self.logger.info(f"Creating {total_deps} dependencies...")

    for i in range(0, total_deps, batch_size):
        batch = all_dependencies[i:i+batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total_deps + batch_size - 1) // batch_size

        cypher = """
        UNWIND $dependencies AS dep
        MATCH (source:Concept {id: dep.source})
        MATCH (target:Concept {id: dep.target})
        CREATE (source) -[rel:DEPENDS_ON {
            created_at: datetime(),
            strength: 1.0
        }]-> (target)
        RETURN count(rel) as created_count
        """

        try:
            result = session.run(cypher, dependencies=batch)
            created = result.single()['created_count']
            self.metrics.relationships_created += created
            self.logger.debug(f"Batch {batch_num}/{total_batches}: Created {created} relationships")

        except Exception as e:
            self.logger.warning(f"Batch {batch_num} partial failure: {str(e)}")
            # Log but continue - missing target concepts aren't fatal
            self.metrics.relationships_failed += len(batch)

    self.logger.info(f"Relationship creation completed: {self.metrics.relationships_created} created, {self.metrics.relationships_failed} failed")
```

### 4.3 Performance Tuning Parameters

```python
# Configuration constants for batch optimization
BATCH_OPTIMIZATION = {
    'node_batch_size': 1000,          # Concepts per batch
    'relationship_batch_size': 5000,  # Relationships per batch
    'retry_batch_size': 100,          # Smaller batch for retries
    'transaction_timeout_ms': 30000,  # 30 second timeout per batch
    'max_retries': 3,                 # Retry failed batches
    'parallel_batches': 1              # Sequential (1) vs parallel (>1)
}

# Monitor performance
PERF_THRESHOLDS = {
    'batch_duration_ms': 5000,        # Warn if batch takes >5s
    'memory_usage_mb': 500,           # Warn if memory >500MB
    'slow_query_ms': 1000             # Log queries slower than 1s
}
```

---

## 5. Error Handling & Retry Logic

### 5.1 Comprehensive Error Handler

```python
from tenacity import retry, stop_after_attempt, wait_exponential
from neo4j.exceptions import ServiceUnavailable, TransactionError

class PopulationError(Exception):
    """Base exception for population errors"""
    pass

class ValidationError(PopulationError):
    """Data validation error"""
    pass

class ConstraintError(PopulationError):
    """Neo4j constraint violation"""
    pass

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def _execute_with_retry(self, session, query, **parameters):
    """Execute query with automatic retry on transient failures"""
    try:
        result = session.run(query, **parameters)
        return result

    except ServiceUnavailable as e:
        self.logger.warning(f"Service temporarily unavailable: {e}")
        raise

    except TransactionError as e:
        self.logger.warning(f"Transaction error (will retry): {e}")
        raise

    except Exception as e:
        self.logger.error(f"Unexpected error: {e}", exc_info=True)
        raise PopulationError(f"Query execution failed: {str(e)}") from e
```

### 5.2 Error Recovery Strategies

```python
def _safe_batch_insert_with_fallback(self, session, concepts: List[Dict]):
    """Insert with fallback strategy for partial failures"""

    try:
        # Try batch insert
        self._batch_insert_nodes(session, concepts, batch_size=1000)

    except Exception as batch_error:
        self.logger.warning(f"Batch insert failed: {batch_error}")
        self.logger.info("Attempting individual inserts (slower)...")

        succeeded = 0
        failed = 0

        for concept in concepts:
            try:
                self._insert_single_concept(session, concept)
                succeeded += 1

            except ValidationError as e:
                self.logger.warning(f"Validation error for {concept['id']}: {e}")
                failed += 1

            except ConstraintError as e:
                self.logger.warning(f"Constraint error for {concept['id']}: {e}")
                # Skip duplicates in incremental mode
                failed += 1

        self.logger.info(f"Individual insert results: {succeeded} succeeded, {failed} failed")

        if failed > len(concepts) * 0.5:  # >50% failure rate
            raise PopulationError(f"Too many failures: {failed}/{len(concepts)}")

def _insert_single_concept(self, session, concept: Dict):
    """Insert single concept with validation"""
    # Validate required fields
    if not concept.get('id'):
        raise ValidationError("Concept 'id' is required")
    if not concept.get('name'):
        raise ValidationError("Concept 'name' is required")

    # Insert with duplicate handling
    result = session.run("""
        MERGE (c:Concept {id: $id})
        SET c.name = $name,
            c.definition = $definition,
            c.layer = $layer,
            c.category = $category,
            c.updated_at = datetime()
        RETURN c.id
    """, **concept)

    return result.single()[0]
```

### 5.3 Validation Error Catalog

| Error | Cause | Recovery | Example |
|-------|-------|----------|---------|
| **ValidationError** | Missing required field | Skip concept, log | `id` field is NULL |
| **ConstraintError** | Duplicate concept ID | Skip (merge mode) or error (replace mode) | Concept ID already exists |
| **ServiceUnavailable** | Neo4j temporarily down | Retry with exponential backoff | Connection refused |
| **TransactionError** | Query execution failed | Retry or fall back to smaller batch | Timeout, lock conflict |
| **IntegrityError** | Missing dependency target | Log warning, skip edge | Target concept not found |

---

## 6. Population Verification Queries

### 6.1 Verification Query Catalog

```python
def _verify_population(self, expected_concepts: List[Dict]):
    """Comprehensive post-population verification"""

    with self.driver.session() as session:
        # 1. Count verification
        actual_count = self._verify_concept_count(session, len(expected_concepts))
        assert actual_count == len(expected_concepts), \
            f"Concept count mismatch: expected {len(expected_concepts)}, got {actual_count}"

        # 2. Layer distribution
        self._verify_layer_distribution(session, expected_concepts)

        # 3. Dependency coverage
        self._verify_dependencies(session, expected_concepts)

        # 4. Constraint validation
        self._verify_constraints(session)

        # 5. Graph integrity
        self._verify_graph_integrity(session)

        self.logger.info("All verification checks passed!")

def _verify_concept_count(self, session, expected_count: int) -> int:
    """Verify total concept count"""
    result = session.run("MATCH (c:Concept) RETURN count(c) as count")
    actual_count = result.single()['count']

    self.logger.info(f"Concept count verification: expected={expected_count}, actual={actual_count}")
    assert actual_count == expected_count, \
        f"Concept count mismatch: {actual_count} != {expected_count}"

    return actual_count

def _verify_layer_distribution(self, session, concepts: List[Dict]):
    """Verify concepts are distributed across layers"""
    expected_by_layer = {}
    for c in concepts:
        layer = c.get('layer', 'unknown')
        expected_by_layer[layer] = expected_by_layer.get(layer, 0) + 1

    result = session.run("""
        MATCH (c:Concept)
        RETURN c.layer as layer, count(c) as count
        ORDER BY layer
    """)

    actual_by_layer = {row['layer']: row['count'] for row in result}

    self.logger.info(f"Layer distribution: {actual_by_layer}")
    for layer, expected_count in expected_by_layer.items():
        actual_count = actual_by_layer.get(layer, 0)
        assert actual_count == expected_count, \
            f"Layer '{layer}' count mismatch: {actual_count} != {expected_count}"

def _verify_dependencies(self, session, concepts: List[Dict]):
    """Verify all dependency relationships are created"""
    expected_deps = sum(len(c.get('dependencies', [])) for c in concepts)

    result = session.run("MATCH () -[r:DEPENDS_ON]-> () RETURN count(r) as count")
    actual_deps = result.single()['count']

    self.logger.info(f"Dependency verification: expected={expected_deps}, actual={actual_deps}")
    # Some dependencies may reference non-existent concepts (dangling refs)
    assert actual_deps <= expected_deps, \
        f"More dependencies created than expected"

def _verify_constraints(self, session):
    """Verify Neo4j constraints are in place"""
    result = session.run("SHOW CONSTRAINTS YIELD name WHERE name LIKE '%Concept%'")
    constraints = list(result)

    self.logger.info(f"Found {len(constraints)} constraints on Concept")
    assert len(constraints) > 0, "No constraints found on Concept nodes"

def _verify_graph_integrity(self, session):
    """Check for common data integrity issues"""
    # Find nodes with missing required properties
    result = session.run("""
        MATCH (c:Concept)
        WHERE c.id IS NULL OR c.name IS NULL
        RETURN count(c) as count
    """)
    invalid_count = result.single()['count']
    assert invalid_count == 0, f"Found {invalid_count} concepts with missing required properties"

    # Check for duplicate IDs (should be prevented by constraint)
    result = session.run("""
        MATCH (c:Concept)
        WITH c.id as id, count(c) as cnt
        WHERE cnt > 1
        RETURN count(*) as duplicates
    """)
    duplicates = result.single()['duplicates']
    assert duplicates == 0, f"Found {duplicates} duplicate concept IDs"

    self.logger.info("Graph integrity checks passed")
```

### 6.2 Verification Report Template

```
Neo4j Population Verification Report
====================================

Timestamp: 2024-01-20T14:30:00Z
Source File: docs/docstratum.yaml
Update Strategy: clear-rebuild

COUNTS:
  Concepts Loaded:        500
  Concepts Created:       500
  Relationships Created:  1,234
  Validation Errors:      0
  Failed Inserts:         0

LAYER DISTRIBUTION:
  master_index:           50 concepts
  concept_map:            300 concepts
  few_shot_bank:          150 concepts

GRAPH METRICS:
  Root Concepts:          15 (no incoming deps)
  Leaf Concepts:          42 (no outgoing deps)
  Max Dependency Depth:   7
  Average Dependencies:   2.47 per concept

VERIFICATION RESULTS:
  ✓ Concept count matches
  ✓ All constraints satisfied
  ✓ No duplicate IDs
  ✓ Required properties present
  ✓ Dependencies verified

EXECUTION TIME:
  Total: 3,245 ms
  Node insertion: 1,200 ms
  Relationship creation: 1,850 ms
  Verification: 195 ms

STATUS: SUCCESS
```

---

## 7. CLI Interface for Population Script

### 7.1 CLI Design (using Click)

```python
# scripts/populate_neo4j.py (with Click CLI)

import click
import os
from pathlib import Path

@click.group()
def cli():
    """Neo4j Population CLI for DocStratum"""
    pass

@cli.command()
@click.option('--uri', default='bolt://localhost:7687',
              help='Neo4j connection URI')
@click.option('--username', default='neo4j',
              help='Neo4j username')
@click.option('--password', default='password123',
              help='Neo4j password')
@click.option('--source', required=True, type=click.Path(exists=True),
              help='Path to llms.txt or YAML file')
@click.option('--strategy', type=click.Choice(['clear-rebuild', 'incremental', 'selective']),
              default='clear-rebuild',
              help='Population strategy')
@click.option('--target-layer', default=None,
              help='Target layer for selective strategy')
@click.option('--batch-size', default=1000, type=int,
              help='Batch size for imports')
@click.option('--verify', is_flag=True, default=True,
              help='Run verification after population')
@click.option('--dry-run', is_flag=True, default=False,
              help='Simulate without modifying database')
def populate(uri, username, password, source, strategy, target_layer, batch_size, verify, dry_run):
    """Populate Neo4j with concepts from source file"""

    click.echo(f"Neo4j Population Tool")
    click.echo(f"=====================")
    click.echo(f"URI: {uri}")
    click.echo(f"Source: {source}")
    click.echo(f"Strategy: {strategy}")
    click.echo(f"Batch Size: {batch_size}")
    click.echo(f"Dry Run: {dry_run}")
    click.echo()

    if dry_run:
        click.echo("⚠️  DRY RUN MODE - No changes will be made")
        click.echo()

    try:
        populator = DocStratumNeo4jPopulator(uri, username, password)

        if not dry_run:
            click.echo("🔄 Starting population...")
            with click.progressbar(length=100, label='Population Progress') as bar:
                populator.populate(source, strategy=strategy, target_layer=target_layer)
                bar.update(100)

            if verify:
                click.echo("✓ Verifying population...")
                populator._verify_population(populator.extracted_concepts)

        click.echo("✅ Population completed successfully!")
        click.echo(f"\nMetrics:")
        click.echo(f"  Concepts Created: {populator.metrics.concepts_created}")
        click.echo(f"  Relationships Created: {populator.metrics.relationships_created}")
        click.echo(f"  Execution Time: {populator.metrics.execution_time_ms:.0f}ms")

    except Exception as e:
        click.echo(f"❌ Population failed: {str(e)}", err=True)
        raise click.ClickException(str(e))

    finally:
        populator.close()

@cli.command()
@click.option('--uri', default='bolt://localhost:7687', help='Neo4j connection URI')
@click.option('--username', default='neo4j', help='Neo4j username')
@click.option('--password', default='password123', help='Neo4j password')
def verify(uri, username, password):
    """Verify existing Neo4j population"""

    with GraphDatabase.driver(uri, auth=(username, password)) as driver:
        with driver.session() as session:
            result = session.run("MATCH (c:Concept) RETURN count(c) as count")
            count = result.single()['count']
            click.echo(f"✓ Neo4j contains {count} concepts")

            result = session.run("MATCH () -[r:DEPENDS_ON]-> () RETURN count(r) as count")
            deps = result.single()['count']
            click.echo(f"✓ Neo4j contains {deps} dependency relationships")

@cli.command()
@click.option('--uri', default='bolt://localhost:7687', help='Neo4j connection URI')
@click.option('--username', default='neo4j', help='Neo4j username')
@click.option('--password', default='password123', help='Neo4j password')
@click.confirmation_option(prompt='Are you sure you want to clear all data?')
def clear(uri, username, password):
    """Clear all data from Neo4j"""

    with GraphDatabase.driver(uri, auth=(username, password)) as driver:
        with driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            click.echo("✓ All data cleared from Neo4j")

if __name__ == '__main__':
    cli()
```

### 7.2 CLI Usage Examples

```bash
# Basic population with default settings
python scripts/populate_neo4j.py populate --source docs/docstratum.yaml

# Population with custom Neo4j connection
python scripts/populate_neo4j.py populate \
  --uri bolt://production-neo4j:7687 \
  --username neo4j \
  --password $(cat /etc/docstratum/neo4j_password) \
  --source docs/docstratum.yaml

# Incremental update (add new concepts only)
python scripts/populate_neo4j.py populate \
  --source docs/docstratum.yaml \
  --strategy incremental

# Selective layer update
python scripts/populate_neo4j.py populate \
  --source docs/docstratum.yaml \
  --strategy selective \
  --target-layer concept_map

# Dry run (preview without making changes)
python scripts/populate_neo4j.py populate \
  --source docs/docstratum.yaml \
  --dry-run

# Verify existing population
python scripts/populate_neo4j.py verify

# Clear all data (with confirmation)
python scripts/populate_neo4j.py clear
```

### 7.3 CLI Output Example

```
Neo4j Population Tool
=====================
URI: bolt://localhost:7687
Source: docs/docstratum.yaml
Strategy: clear-rebuild
Batch Size: 1000

🔄 Starting population...
Population Progress  [████████████████████████████████████████] 100%

✓ Verifying population...
✓ Constraint check passed
✓ Concept count verified (500/500)
✓ Layer distribution verified
✓ Dependency verification passed
✓ Graph integrity checks passed

✅ Population completed successfully!

Metrics:
  Concepts Created: 500
  Relationships Created: 1,234
  Execution Time: 3,245ms
```

---

## Deliverables Checklist

- [ ] DocStratumNeo4jPopulator class implemented with core methods
- [ ] Data extraction from core.loader.load_llms_txt() implemented
- [ ] Clear-and-rebuild strategy fully implemented
- [ ] Incremental update strategy fully implemented
- [ ] Selective replace strategy fully implemented
- [ ] Batch insert nodes with configurable batch size
- [ ] Batch create relationships with dependency handling
- [ ] Error handling and retry logic with exponential backoff
- [ ] Fallback to individual inserts on batch failure
- [ ] Comprehensive verification queries implemented
- [ ] Verification report generation implemented
- [ ] Click CLI with populate, verify, and clear commands
- [ ] CLI help text and documentation complete
- [ ] All usage examples tested and working
- [ ] Data flow diagram (ASCII) created

---

## Acceptance Criteria

- [ ] `populate_neo4j.py populate` successfully loads 500+ concepts in <5 seconds
- [ ] All concepts created with correct properties (id, name, definition, layer)
- [ ] Relationships created correctly for all dependencies
- [ ] Clear-and-rebuild removes all existing data and rebuilds cleanly
- [ ] Incremental mode skips existing concepts and only adds new ones
- [ ] Selective mode updates specific layers without affecting others
- [ ] Batch inserts with 1000-concept batches complete successfully
- [ ] Error handling gracefully handles missing dependencies (dangling refs)
- [ ] Retries work for transient failures (ServiceUnavailable)
- [ ] Verification passes 100% of checks after population
- [ ] Verification report shows accurate counts and metrics
- [ ] CLI provides clear feedback with progress reporting
- [ ] Dry-run mode shows what would be done without making changes
- [ ] Clear command requires confirmation before deletion
- [ ] All CLI commands handle connection errors gracefully

---

## Next Step

→ **v0.4.4d — Visualization Alternatives & Obsidian Export**

Implement visualization strategies including Neo4j Browser, Obsidian export (export_to_obsidian.py), and Streamlit-native visualization alternatives.
