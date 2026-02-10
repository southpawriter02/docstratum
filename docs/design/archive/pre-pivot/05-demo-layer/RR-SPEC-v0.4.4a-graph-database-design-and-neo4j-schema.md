# v0.4.4a — Graph Database Design & Neo4j Schema

> **Task:** Design the Neo4j graph schema for representing the DocStratum concept map. This document specifies how Concept nodes and their DEPENDS_ON relationships map to Neo4j graph structures, including property schemas, Cypher query patterns, indexing strategies, and migration considerations.

---

## Objective

Establish a comprehensive Neo4j schema design that enables efficient storage, querying, and traversal of the DocStratum concept map. This includes mapping Pydantic data models to graph properties, defining node and relationship types, creating performance-critical indexes, and documenting Cypher patterns for common operations (concept lookup, dependency traversal, root/leaf detection).

---

## Scope Boundaries

| Aspect | In Scope | Out of Scope |
|--------|----------|--------------|
| **Node Types** | Concept nodes with complete property mapping | User nodes, execution logs, audit trails |
| **Relationship Types** | DEPENDS_ON edges between concepts | Temporal relationships, versioning edges |
| **Properties** | id, name, definition, layer, category, metadata | User permissions, access control, ownership |
| **Indexes** | Primary indexes on id, name; composite indexes for query optimization | Full-text search indexes, vector embeddings |
| **Query Patterns** | CRUD operations, traversal, path finding, root/leaf detection | Real-time streaming, incremental sync patterns |
| **Schema Evolution** | Initial schema design, migration playbook | Zero-downtime migrations, rolling upgrades |

---

## Dependency Diagram

```
┌─────────────────────────────────────────────────┐
│     Core Loader (core.loader)                  │
│  Loads YAML/llms.txt → Pydantic Models          │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│   Graph Database Design (THIS DOCUMENT)         │
│  Schema: Concept nodes, DEPENDS_ON edges       │
│  Properties: id, name, definition, layer, ...  │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│   Docker Infrastructure (v0.4.4b)               │
│  Neo4j 5 Community, ports 7474/7687            │
└─────────────────────────────────────────────────┘
```

---

## 1. Graph Data Modeling Fundamentals

### 1.1 Property Graph Model

Neo4j uses a **property graph model** consisting of:
- **Nodes**: Represent entities (concepts in our case)
- **Relationships**: Represent connections between nodes (dependencies)
- **Properties**: Key-value pairs attached to nodes and relationships
- **Labels**: Categorical markers for nodes (e.g., :Concept)

In the DocStratum context:
- Each **Concept** in the Master Index becomes a **Node** with label `:Concept`
- Each **DEPENDS_ON** relationship in the Concept Map becomes a **Relationship**
- Properties from Pydantic models are stored as node properties

### 1.2 Modeling Strategy for DocStratum

The DocStratum is fundamentally a **DAG (Directed Acyclic Graph)**:
- Nodes represent semantic concepts
- Edges represent dependency relationships (concept X depends on concept Y)
- No cycles (by semantic constraint)
- Multiple paths may exist between concepts

**Key Design Decisions:**
1. **Single Label for Concepts**: All concepts use `:Concept` label (no sub-labeling by layer)
2. **Layer as Property**: Store layer (Master Index, Concept Map, Few-Shot Bank) as a node property
3. **Flat Relationship Type**: Single `DEPENDS_ON` relationship type for all dependencies
4. **Metadata Flexibility**: Use JSON/nested properties for flexible concept metadata

---

## 2. Neo4j Schema Design

### 2.1 Node Schema: Concept Nodes

```
LABEL: :Concept

PROPERTIES:
├── id (String, unique)              # Unique identifier from YAML
├── name (String, required)          # Concept name/title
├── definition (String)              # Semantic definition
├── layer (String)                   # "master_index" | "concept_map" | "few_shot_bank"
├── category (String)                # Conceptual category/domain
├── created_at (DateTime)            # ISO 8601 timestamp
├── updated_at (DateTime)            # Last modification time
├── source_file (String)             # Reference to source YAML file
├── metadata (Map)                   # Flexible JSON: tags, attrs, etc.
└── embedding_id (String, optional)  # Reference to vector embedding
```

### 2.2 Relationship Schema: DEPENDS_ON

```
TYPE: DEPENDS_ON
DIRECTION: (source) -[DEPENDS_ON]-> (target)
  Meaning: source concept depends on target concept

PROPERTIES:
├── created_at (DateTime)            # When relationship was created
├── reason (String, optional)        # Why this dependency exists
├── strength (Float, optional)       # Confidence: 0.0 to 1.0
└── metadata (Map, optional)         # Additional context
```

### 2.3 ASCII Graph Schema Diagram

```
┌──────────────────────────────────────┐
│         :Concept                     │
├──────────────────────────────────────┤
│ id: String (unique)                  │
│ name: String                         │
│ definition: String                   │
│ layer: String (enum)                 │
│ category: String                     │
│ created_at: DateTime                 │
│ updated_at: DateTime                 │
│ source_file: String                  │
│ metadata: Map                        │
│ embedding_id: String                 │
└──────────────────────────────────────┘
              ▲
              │
         [DEPENDS_ON]
        created_at
        reason
        strength
        metadata
              │
              │
        (points to another
         :Concept node)
```

### 2.4 Property Type Reference Table

| Property | Type | Constraints | Example |
|----------|------|-----------|---------|
| `id` | String | Unique, NOT NULL | `"llm.concept.semantic_layer"` |
| `name` | String | NOT NULL, max 255 chars | `"Semantic Layer"` |
| `definition` | String | Optional, max 2000 chars | `"A layer that maps..."` |
| `layer` | String | Enum: `master_index`, `concept_map`, `few_shot_bank` | `"concept_map"` |
| `category` | String | Optional, indexed | `"architecture"` |
| `created_at` | DateTime | NOT NULL, auto-set | `"2024-01-15T10:30:00Z"` |
| `updated_at` | DateTime | NOT NULL, auto-set | `"2024-01-20T14:22:00Z"` |
| `source_file` | String | Optional | `"docs/master_index.yaml"` |
| `metadata` | Map | Optional, flexible JSON | `{"tags": ["core"], "severity": "high"}` |
| `embedding_id` | String | Optional, for vector queries | `"emb_123abc"` |
| `reason` (relationship) | String | Optional | `"Required for initialization"` |
| `strength` (relationship) | Float | 0.0 to 1.0 | `0.95` |

---

## 3. Property Mapping: Pydantic to Neo4j

### 3.1 Pydantic Model Structure

From `core.models.Concept` (typical):

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, List

class Concept(BaseModel):
    id: str                                # Maps to node.id
    name: str                              # Maps to node.name
    definition: Optional[str] = None       # Maps to node.definition
    layer: str                             # Maps to node.layer
    category: Optional[str] = None         # Maps to node.category
    tags: Optional[List[str]] = None       # Maps to node.metadata.tags
    dependencies: Optional[List[str]] = [] # Creates DEPENDS_ON relationships
    metadata: Optional[Dict] = {}          # Maps to node.metadata
```

### 3.2 Mapping Strategy

**Direct Property Mapping:**

```
Pydantic Field           Neo4j Node Property
─────────────────────────────────────────
id                  →    id (unique constraint)
name                →    name
definition          →    definition
layer               →    layer
category            →    category
tags[]              →    metadata.tags (array in map)
metadata            →    metadata (merged with other fields)
```

**Relationship Creation from Lists:**

```
For each dependency ID in concept.dependencies:
  CREATE (:Concept {id: source_id})
  -[DEPENDS_ON {created_at: now}]->
  (:Concept {id: target_id})
```

### 3.3 Mapping Logic Pseudocode

```
function mapConceptToNode(pydantic_concept):
    node_properties = {
        'id': pydantic_concept.id,
        'name': pydantic_concept.name,
        'definition': pydantic_concept.definition or '',
        'layer': pydantic_concept.layer,
        'category': pydantic_concept.category or '',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'source_file': pydantic_concept.get('source_file', ''),
        'metadata': {
            'tags': pydantic_concept.tags or [],
            'custom': pydantic_concept.metadata or {}
        }
    }
    return node_properties

function mapDependenciesToEdges(pydantic_concept):
    edges = []
    for dep_id in pydantic_concept.dependencies or []:
        edge = {
            'from': pydantic_concept.id,
            'to': dep_id,
            'type': 'DEPENDS_ON',
            'properties': {
                'created_at': datetime.now().isoformat(),
                'reason': 'Imported from YAML',
                'strength': 1.0
            }
        }
        edges.append(edge)
    return edges
```

---

## 4. Cypher Query Patterns for Common Operations

### 4.1 Query Catalog

| Operation | Cypher Pattern | Use Case |
|-----------|---|----------|
| **Find Concept by ID** | `MATCH (c:Concept {id: $id}) RETURN c` | Direct lookup |
| **Find Concept by Name** | `MATCH (c:Concept) WHERE c.name =~ $pattern RETURN c` | Search by name |
| **Get Direct Dependencies** | `MATCH (c:Concept {id: $id}) -[DEPENDS_ON]-> (dep) RETURN dep` | Immediate deps |
| **Get Dependents** | `MATCH (dep:Concept) -[DEPENDS_ON]-> (c:Concept {id: $id}) RETURN dep` | Reverse lookup |
| **Get All Transitive Dependencies** | `MATCH (c:Concept {id: $id}) -[DEPENDS_ON*]-> (dep) RETURN dep` | Full dependency tree |
| **Find Root Concepts** | `MATCH (c:Concept) WHERE NOT (c) <-[DEPENDS_ON]- () RETURN c` | No incoming edges |
| **Find Leaf Concepts** | `MATCH (c:Concept) WHERE NOT (c) -[DEPENDS_ON]-> () RETURN c` | No outgoing edges |
| **Find Paths Between Two** | `MATCH path = (a:Concept {id: $from}) -[DEPENDS_ON*]-> (b:Concept {id: $to}) RETURN path` | Dependency chains |
| **Get Concepts by Layer** | `MATCH (c:Concept) WHERE c.layer = $layer RETURN c` | Filter by layer |
| **Get Strongly Connected** | `MATCH (c1:Concept) -[DEPENDS_ON*]-> (c2:Concept) -[DEPENDS_ON*]-> (c1) RETURN c1, c2` | Cycles (should be 0) |

### 4.2 Detailed Query Examples

#### Find Concept by ID

```cypher
MATCH (c:Concept {id: "llm.semantic_layer"})
RETURN c.id, c.name, c.definition, c.layer, c.category
```

#### Get Direct Dependencies (1-hop)

```cypher
MATCH (c:Concept {id: $concept_id})
      -[dep:DEPENDS_ON]-> (dependency:Concept)
RETURN
    dependency.id,
    dependency.name,
    dependency.layer,
    dep.strength,
    dep.reason
ORDER BY dep.strength DESC
```

#### Get All Transitive Dependencies (depth: unlimited)

```cypher
MATCH (c:Concept {id: $concept_id})
      -[path:DEPENDS_ON*]-> (transitive:Concept)
RETURN
    transitive.id,
    transitive.name,
    length(path) as depth
ORDER BY depth ASC
```

#### Find Root Concepts (no incoming DEPENDS_ON)

```cypher
MATCH (c:Concept)
WHERE NOT (c) <-[:DEPENDS_ON]- ()
RETURN c.id, c.name, c.layer
ORDER BY c.name
```

#### Find All Concepts in Dependency Graph

```cypher
MATCH (c:Concept)
WHERE c.layer = "concept_map"
RETURN count(c) as concept_count
```

#### Get Dependency Depth of a Concept

```cypher
MATCH (c:Concept {id: $concept_id})
      -[path:DEPENDS_ON*]-> (deepest:Concept)
WHERE NOT (deepest) -[:DEPENDS_ON]-> ()
RETURN
    deepest.id,
    length(path) as max_depth
ORDER BY max_depth DESC
LIMIT 1
```

---

## 5. Index Strategy for Performance

### 5.1 Required Indexes

```
INDEX 1: PRIMARY UNIQUE INDEX
  Name: idx_concept_id_unique
  Entities: Node (:Concept)
  Properties: id
  Type: UNIQUE
  Rationale: Ensures no duplicate concept IDs; enables fast primary key lookups

INDEX 2: RANGE INDEX
  Name: idx_concept_name
  Entities: Node (:Concept)
  Properties: name
  Type: RANGE
  Rationale: Enables efficient name-based searches and sorting

INDEX 3: RANGE INDEX
  Name: idx_concept_layer
  Entities: Node (:Concept)
  Properties: layer
  Type: RANGE
  Rationale: Filters concepts by layer (master_index, concept_map, few_shot_bank)

INDEX 4: RANGE INDEX
  Name: idx_concept_category
  Entities: Node (:Concept)
  Properties: category
  Type: RANGE
  Rationale: Enables category-based filtering and exploration
```

### 5.2 Index Creation Cypher

```cypher
-- Create unique index on concept ID (primary key)
CREATE CONSTRAINT idx_concept_id_unique
IF NOT EXISTS
FOR (c:Concept) REQUIRE c.id IS UNIQUE;

-- Create range indexes for common filters
CREATE INDEX idx_concept_name
IF NOT EXISTS
FOR (c:Concept) ON (c.name);

CREATE INDEX idx_concept_layer
IF NOT EXISTS
FOR (c:Concept) ON (c.layer);

CREATE INDEX idx_concept_category
IF NOT EXISTS
FOR (c:Concept) ON (c.category);

-- Create composite index for layer + category (optional, common filter combo)
CREATE INDEX idx_concept_layer_category
IF NOT EXISTS
FOR (c:Concept) ON (c.layer, c.category);
```

### 5.3 Index Performance Reference

| Index | Query Type | Typical Query Time | Without Index |
|-------|-----------|------------------|---|
| `idx_concept_id_unique` | Point lookup by ID | <1ms | O(n) full scan |
| `idx_concept_name` | Name prefix search | 5-50ms (corpus size dependent) | O(n) scan |
| `idx_concept_layer` | Filter by layer | 1-5ms | O(n) scan |
| `idx_concept_category` | Filter by category | 5-20ms | O(n) scan |
| `idx_concept_layer_category` | Multi-filter query | 1-10ms | O(n) scan |

### 5.4 Index Monitoring

```cypher
-- Check all indexes on Concept nodes
SHOW INDEXES YIELD name, entityType, labelsOrTypes, properties
WHERE labelsOrTypes = ['Concept']
RETURN *;

-- Get index usage statistics (Neo4j Enterprise feature)
SHOW INDEX YIELD name, usage
ORDER BY usage.trackedSince DESC;
```

---

## 6. Schema Migration Considerations

### 6.1 Migration Scenarios

#### Scenario A: Adding a New Property to All Concepts

```cypher
-- Add new optional property to all existing concepts
MATCH (c:Concept)
SET c.new_property = 'default_value'
RETURN count(c) as updated_count;
```

#### Scenario B: Renaming a Relationship Type

```cypher
-- Create new relationships with new type
MATCH (c1:Concept) -[r:OLD_REL_TYPE]-> (c2:Concept)
CREATE (c1) -[new_r:NEW_REL_TYPE]-> (c2)
SET new_r = r
WITH r
DELETE r
RETURN count(new_r) as migrated_count;
```

#### Scenario C: Splitting a Property into Multiple Properties

```cypher
-- Example: split 'metadata' object into typed properties
MATCH (c:Concept)
WHERE c.metadata IS NOT NULL
SET c.tags = c.metadata.tags,
    c.importance = c.metadata.importance
RETURN count(c) as updated_count;
```

#### Scenario D: Removing Outdated Concepts

```cypher
-- Soft delete by marking deprecated
MATCH (c:Concept {layer: 'few_shot_bank'})
WHERE c.created_at < datetime("2023-01-01")
SET c.deprecated = true,
    c.deprecation_date = datetime()
RETURN count(c) as deprecated_count;

-- Hard delete (use with caution)
MATCH (c:Concept {deprecated: true})
DELETE c;
```

### 6.2 Zero-Downtime Migration Strategy

1. **Phase 1 (Write New Structure)**
   - Deploy code that writes to both old and new schema
   - Continue reading from old schema
   - Run migration script in background to backfill existing data

2. **Phase 2 (Read New Structure)**
   - Deploy code that reads from new schema
   - Continue writing to both structures for safety

3. **Phase 3 (Cleanup)**
   - Verify no reads/writes to old schema
   - Remove old schema cleanup from code
   - Optionally delete old data

---

## Deliverables Checklist

- [ ] Neo4j schema design documented with node labels and properties
- [ ] Property mapping from Pydantic models to Neo4j nodes complete
- [ ] Relationship schema (:DEPENDS_ON) defined with property constraints
- [ ] ASCII diagram of graph schema created and reviewed
- [ ] Property type reference table with constraints completed
- [ ] Cypher query catalog with 9+ common operations documented
- [ ] Detailed Cypher examples provided for key operations (find, traverse, roots, leaves)
- [ ] Index strategy defined with 4+ indexes specified
- [ ] Index creation Cypher scripts tested and validated
- [ ] Schema migration scenarios documented with examples
- [ ] Migration safeguards and best practices established

---

## Acceptance Criteria

- [ ] Schema supports all DocStratum concepts with required metadata
- [ ] All indexed properties resolve in <10ms for 10k+ node graphs
- [ ] Cypher queries execute dependency traversals in <100ms (depth ≤5)
- [ ] No breaking changes to existing Pydantic model structure
- [ ] Migration scripts tested on a copy of production schema
- [ ] Documentation includes examples for each indexed query pattern
- [ ] Schema is validated against typical DocStratum data (200-500 concepts)
- [ ] Constraint enforcement prevents data integrity issues
- [ ] Index naming follows consistent convention
- [ ] Design supports future additions (embeddings, audit fields)

---

## Next Step

→ **v0.4.4b — Docker Infrastructure & Environment Setup**

Implement the Docker Compose configuration for Neo4j 5 Community with proper volume management, port mapping, authentication, and health checks.
