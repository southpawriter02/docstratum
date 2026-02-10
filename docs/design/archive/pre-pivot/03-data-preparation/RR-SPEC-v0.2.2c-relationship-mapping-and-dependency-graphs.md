# v0.2.2c: Relationship Mapping & Dependency Graphs

> Systematic construction of semantic relationship graphs connecting concepts into a navigable concept map. This module transforms a flat set of defined concepts into an interconnected knowledge graph with explicit relationship types, dependency resolution, cycle detection, and quality metrics. The resulting graph enables LLMs to traverse concept relationships and understand context beyond individual definitions.

## Objective

Establish a comprehensive methodology for identifying, categorizing, and validating relationships between concepts. Create tools and processes for building and analyzing concept dependency graphs, detecting circular dependencies, assessing relationship strength, and visualizing the resulting concept map. Produce a machine-readable concept graph suitable for graph database storage and LLM consumption.

## Scope Boundaries

**IN SCOPE:**
- Complete taxonomy of 7 relationship types with definitions and examples
- Graph construction methodology (start with core concepts, add dependencies, add cross-references)
- Cycle detection algorithms and resolution strategies
- Graph visualization techniques (ASCII art, Mermaid diagrams, Cypher queries)
- Graph quality metrics (connectivity, depth, orphan detection, path analysis)
- Relationship strength assessment (strong/weak/implied categorization)
- Worked example: building full concept graph from 8+ concepts with 15+ relationships
- Python graph data structures and algorithms
- Neo4j integration (Cypher CREATE statements for graph database)

**OUT OF SCOPE:**
- Concept mining (see v0.2.2a)
- Definition writing (see v0.2.2b)
- Anti-pattern documentation (see v0.2.2d)
- Real-time graph updates
- Machine learning for relationship inference
- Graph visualization UI implementations

## Dependency Diagram

```
Defined Concepts (from v0.2.2b)
    ↓
[Relationship Type Classification]
  ├─ Identify applicable relationship types (7 types)
  ├─ Categorize each relationship
  └─ Assess relationship strength
    ↓
[Relationship Extraction]
  ├─ Implicit relationships (from definitions)
  ├─ Explicit relationships (domain knowledge)
  └─ Probable relationships (expert review)
    ↓
[Graph Construction]
  ├─ Create concept nodes
  ├─ Add relationship edges
  └─ Build adjacency structures
    ↓
[Cycle Detection & Resolution]
  ├─ Run topological sort
  ├─ Identify cycles
  └─ Resolve circular dependencies
    ↓
[Graph Quality Analysis]
  ├─ Compute connectivity metrics
  ├─ Detect orphaned concepts
  ├─ Analyze path properties
  └─ Flag anomalies
    ↓
[Visualization & Validation]
  ├─ Generate Mermaid diagrams
  ├─ Export Neo4j statements
  ├─ Create ASCII visualizations
  └─ Expert review
    ↓
[Final Concept Graph]
  └─ Ready for few-shot bank creation (v0.2.2d)
```

## 1. Complete Taxonomy of Relationship Types

Seven relationship types capture the semantic connections between concepts.

### 1.1 depends_on (Prerequisite Relationship)

**Definition:** Concept A depends on concept B means understanding A requires prior understanding of B.

**Direction:** Unidirectional (A → B means "B must be understood first")

**Strength:** strong / weak / implied

**When to use:**
- A cannot exist without B (strong)
- A is easier understood with knowledge of B (weak)
- A is theoretically possible without B but practically always requires it (implied)

**Examples:**

```
Authorization Code Flow depends_on OAuth 2.0 (strong)
  ↳ Cannot understand authorization_code_flow without OAuth framework

Connection Pooling depends_on Database Connection (strong)
  ↳ Pool is meaningless without connections

Lazy Loading depends_on Proxy Pattern (weak)
  ↳ Useful to know proxy pattern but not strictly required

Optimistic Locking depends_on Conflicts Detection (strong)
  ↳ The entire mechanism requires detecting conflicts
```

**Graph notation:**
```
A --depends_on--> B
```

---

### 1.2 see_also (Related Concepts)

**Definition:** Concept A is related to concept B; understanding A is enriched by knowledge of B, but neither requires the other.

**Direction:** Bidirectional (symmetric: A ↔ B)

**Strength:** strong / weak / tangential

**When to use:**
- Concepts frequently appear together in documentation (strong)
- Concepts solve similar problems with different approaches (strong)
- Concepts are loosely thematically related (weak)
- Concepts are tangentially connected (tangential)

**Examples:**

```
Pessimistic Locking see_also Optimistic Locking (strong)
  ↳ Both solve concurrency; readers should understand both approaches

Circuit Breaker see_also Timeout (strong)
  ↳ Often used together; circuit breaker decision based on timeout

Connection Pool see_also Thread Pool (strong)
  ↳ Same pattern applied to different resources

Cache see_also Memoization (weak)
  ↳ Similar concepts; memoization is a narrower case of caching

Buffer see_also Cache (tangential)
  ↳ Both store data temporarily; different purposes and semantics
```

**Graph notation:**
```
A --see_also--> B
B --see_also--> A
(or: A <--see_also--> B if truly symmetric)
```

---

### 1.3 replaces (Obsolescence Relationship)

**Definition:** Concept A replaces concept B means A is the modern/recommended successor to B.

**Direction:** Unidirectional (A → B means "use A instead of B")

**Strength:** direct / functional / historical

**When to use:**
- A is direct successor with same functionality (direct)
- A and B solve same problem but with different approach (functional)
- B is deprecated but historically significant (historical)

**Examples:**

```
OAuth 2.0 replaces OAuth 1.0 (direct)
  ↳ OAuth 2.0 is official successor with same domain

Bearer Token replaces Basic Authentication (functional)
  ↳ Both do HTTP authentication; Bearer Token preferred for modern systems

Eventual Consistency replaces Immediate Consistency (historical)
  ↳ Distributed systems chose eventual consistency; immediate consistency
     remains valid in centralized systems
```

**Graph notation:**
```
A --replaces--> B
(or: B --deprecated_by--> A for same semantic)
```

---

### 1.4 conflicts_with (Mutual Exclusivity)

**Definition:** Concept A conflicts with concept B means you cannot simultaneously apply both in the same context.

**Direction:** Bidirectional (symmetric: A ↔ B)

**Strength:** strong / weak / conditional

**When to use:**
- A and B are mutually exclusive by design (strong)
- A and B can coexist but with careful coordination (weak)
- A and B conflict only under certain conditions (conditional)

**Examples:**

```
Strong Consistency conflicts_with Eventual Consistency (strong)
  ↳ Cannot guarantee both simultaneously in distributed system

Blocking I/O conflicts_with Non-blocking I/O (strong)
  ↳ Mutually exclusive operational modes

Optimistic Locking conflicts_with Pessimistic Locking (strong)
  ↳ Different strategies; cannot apply both to same data

Caching conflicts_with Real-time Data Requirement (conditional)
  ↳ Conflict only when consistency requirement < cache TTL
```

**Graph notation:**
```
A <--conflicts_with--> B
```

---

### 1.5 part_of (Composition Relationship)

**Definition:** Concept A is part of concept B means A is a component or module of the larger concept B.

**Direction:** Unidirectional (A → B means "A is a part of B")

**Strength:** structural / functional / conceptual

**When to use:**
- A is a structural component of B (structural)
- A is one of several mechanisms that together comprise B (functional)
- A is conceptually a component of B's domain (conceptual)

**Examples:**

```
Atomicity part_of ACID Properties (structural)
  ↳ Atomicity is one of four ACID properties

Authorization Code Flow part_of OAuth 2.0 (structural)
  ↳ Authorization_code_flow is one of several OAuth 2.0 grant types

Deadlock Detection part_of Lock Manager (functional)
  ↳ Lock manager contains deadlock detection mechanism

Cache Invalidation part_of Caching Strategy (conceptual)
  ↳ How to invalidate is part of overall caching approach
```

**Graph notation:**
```
A --part_of--> B
(or: B --contains--> A for inverse)
```

---

### 1.6 specializes (Generalization/Specialization)

**Definition:** Concept A specializes concept B means A is a specific instance or subtype of the general concept B.

**Direction:** Unidirectional (A → B means "A is a specialization of B")

**Strength:** direct / categorical / contextual

**When to use:**
- A is a strict subtype of B (direct)
- A is one category in a taxonomy of B (categorical)
- A is a specialized application of B (contextual)

**Examples:**

```
Bearer Token specializes Authentication Token (direct)
  ↳ Bearer token is one type of authentication token

Connection Pool specializes Resource Pool (categorical)
  ↳ Connection pool is a specific type of resource pool

Pessimistic Locking specializes Concurrency Control (contextual)
  ↳ Pessimistic locking is one approach to concurrency control

Read Replica specializes Database Replica (direct)
  ↳ Read replica is a type of replica with specific permissions
```

**Graph notation:**
```
A --specializes--> B
(or: B --generalizes--> A for inverse)
```

---

### 1.7 implements (Realization/Manifestation)

**Definition:** Concept A implements concept B means A is a concrete mechanism or algorithm that realizes the abstract concept B.

**Direction:** Unidirectional (A → B means "A realizes B")

**Strength:** direct / approximate / inspired_by

**When to use:**
- A directly realizes B with exact behavior (direct)
- A approximately realizes B with variations (approximate)
- A is inspired by B but not a pure implementation (inspired_by)

**Examples:**

```
MySQL Replication implements Asynchronous Replication (direct)
  ↳ MySQL replication is a concrete implementation of async replication

Vector Clock implements Happened-Before Ordering (direct)
  ↳ Vector clocks are algorithm realizing happened-before relationship

Exponential Backoff implements Retry Strategy (approximate)
  ↳ Exponential backoff is one realization of retry strategy

Redis implements Distributed Cache (direct)
  ↳ Redis is concrete implementation of distributed caching concept
```

**Graph notation:**
```
A --implements--> B
```

---

## 2. Graph Construction Methodology

### Step 1: Start with Core Concepts

Identify 3-5 foundational concepts that anchor the domain. Everything else relates to these.

```python
# Example: Connection Management Domain

CORE_CONCEPTS = [
    "Database Connection",      # Foundation: what is being pooled?
    "Connection Pool",          # Foundation: the pooling mechanism
    "Thread Safety",            # Foundation: constraint on access
    "Resource Management"       # Foundation: why we care about pooling
]
```

### Step 2: Identify Dependency Relationships

For each non-core concept, ask: "What core concept(s) must be understood first?"

```python
TIER_1_CONCEPTS = [
    "Idle Timeout",              # depends_on Database Connection
    "Pool Exhaustion",           # depends_on Connection Pool
    "Connection Leak",           # depends_on Resource Management
]

TIER_2_CONCEPTS = [
    "Max Pool Size",             # depends_on Connection Pool + Idle Timeout
    "Connection Recycling",      # depends_on Connection Pool + Idle Timeout
]
```

### Step 3: Add Cross-References

Add see_also relationships for concepts that appear together or solve similar problems.

```python
CROSS_REFERENCES = [
    ("Pessimistic Locking", "see_also", "Thread Safety"),
    ("Connection Pool", "see_also", "Thread Pool"),
    ("Resource Management", "see_also", "Garbage Collection"),
]
```

### Step 4: Add Composition Relationships

Identify part_of (components) and specializes (subtypes) relationships.

```python
COMPOSITION = [
    ("Atomicity", "part_of", "ACID Properties"),
    ("Bearer Token", "specializes", "Authentication Token"),
    ("Pessimistic Locking", "specializes", "Concurrency Control"),
]
```

### Step 5: Identify Conflicts and Replacements

Add conflicts_with and replaces relationships.

```python
CONFLICTS_AND_REPLACEMENTS = [
    ("Strong Consistency", "conflicts_with", "Eventual Consistency"),
    ("OAuth 2.0", "replaces", "OAuth 1.0"),
    ("Non-blocking I/O", "conflicts_with", "Blocking I/O"),
]
```

---

## 3. Cycle Detection and Resolution

Cycles occur when A depends on B, B depends on C, and C depends on A. These break LLM reasoning.

### 3.1 Cycle Detection Algorithm

```python
from collections import defaultdict, deque
from typing import Set, List, Tuple, Optional

class CycleDetector:
    def __init__(self, concepts: List[str]):
        self.concepts = set(concepts)
        self.graph = defaultdict(set)  # adjacency: concept -> [dependencies]
        self.cycles = []

    def add_relationship(self, concept_a: str, rel_type: str, concept_b: str):
        """Add a relationship to the graph."""
        if rel_type in ['depends_on', 'part_of', 'specializes', 'implements']:
            # These are directional relationships
            self.graph[concept_a].add(concept_b)

    def find_cycles_dfs(self) -> List[List[str]]:
        """
        Detect all cycles using depth-first search.

        Returns:
            List of cycles, each cycle is a list of concepts forming a loop.
        """
        visited = set()
        rec_stack = set()  # Recursion stack tracks current path
        cycles = []

        def dfs(node, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.graph[node]:
                if neighbor not in self.concepts:
                    continue  # Skip unknown concepts

                if neighbor not in visited:
                    dfs(neighbor, path[:])
                elif neighbor in rec_stack:
                    # Found a cycle: from neighbor back to neighbor
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)

            path.pop()
            rec_stack.remove(node)

        for concept in self.concepts:
            if concept not in visited:
                dfs(concept, [])

        # Remove duplicate cycles (same cycle starting at different points)
        self.cycles = self._deduplicate_cycles(cycles)
        return self.cycles

    def _deduplicate_cycles(self, cycles: List[List[str]]) -> List[List[str]]:
        """Remove duplicate cycles that are rotations of each other."""
        unique = []
        for cycle in cycles:
            cycle_normalized = self._normalize_cycle(cycle[:-1])  # Remove duplicate endpoint
            if not any(self._normalize_cycle(u[:-1]) == cycle_normalized for u in unique):
                unique.append(cycle)
        return unique

    def _normalize_cycle(self, cycle: List[str]) -> tuple:
        """Normalize cycle for comparison (find lexicographically smallest rotation)."""
        rotations = [tuple(cycle[i:] + cycle[:i]) for i in range(len(cycle))]
        return min(rotations)

    def report_cycles(self) -> str:
        """Generate human-readable cycle report."""
        if not self.cycles:
            return "✓ No cycles detected"

        report = f"⚠️  Found {len(self.cycles)} cycle(s):\n\n"
        for i, cycle in enumerate(self.cycles, 1):
            path = " → ".join(cycle)
            report += f"Cycle {i}: {path}\n"
        return report

# Example usage
detector = CycleDetector([
    "A", "B", "C", "D"
])
detector.add_relationship("A", "depends_on", "B")
detector.add_relationship("B", "depends_on", "C")
detector.add_relationship("C", "depends_on", "A")  # Creates cycle!
detector.add_relationship("D", "depends_on", "A")

cycles = detector.find_cycles_dfs()
print(detector.report_cycles())
```

**Output:**
```
⚠️  Found 1 cycle(s):

Cycle 1: A → B → C → A
```

### 3.2 Cycle Resolution Strategies

When cycles are detected, choose a resolution strategy:

| Strategy | When to Use | Approach | Example |
|----------|-------------|----------|---------|
| **Break Dependency** | One relationship is weaker or less critical | Change depends_on to see_also or remove | A see_also B (instead of depends on) |
| **Split Concept** | Cycle exists because concept conflates two ideas | Create two concepts, break cycle | "Transport Layer Security" → "TLS Encryption" + "TLS Certificate Validation" |
| **Introduce Intermediate** | Two concepts are interdependent at same level | Create abstraction both depend on | A & B both depend_on "Shared Protocol" |
| **Accept Mutual Reference** | Concepts are truly interdependent | Use see_also (bidirectional) instead of depends_on | A see_also B |

### 3.3 Worked Example: Cycle Resolution

**Original Problem:**
```
Authentication depends_on Cryptography
Cryptography depends_on Hashing
Hashing depends_on Authentication (because some auth uses hash-based tokens)
→ Cycle detected: Authentication → Cryptography → Hashing → Authentication
```

**Resolution Analysis:**
- "Hashing depends_on Authentication" is weak (hashing exists independently)
- Solution: Change to "Hashing see_also Authentication"

**Result:**
```
Authentication depends_on Cryptography
Cryptography depends_on Hashing
Hashing see_also Authentication
→ No cycle (see_also is not in dependency graph)
```

---

## 4. Graph Visualization Techniques

### 4.1 ASCII Art Visualization

Useful for small graphs (< 20 concepts). Shows hierarchy clearly.

```
Conceptual Hierarchy (ASCII Art):

TIER 0 (Foundational)
    │
    ├─ Database Connection
    │    │
    │    ├─┬─ Connection Pool
    │    │ │     │
    │    │ │     ├─ Pool Size Configuration
    │    │ │     ├─ Idle Timeout
    │    │ │     └─ Connection Recycling
    │    │ │
    │    │ └─ Thread Pool (see_also)
    │    │
    │    └─ Connection Leak
    │
    ├─ Thread Safety
    │    │
    │    └─┬─ Concurrency Control
    │      │     │
    │      │     ├─ Pessimistic Locking
    │      │     │     │
    │      │     │     └─ Deadlock
    │      │     │
    │      │     └─ Optimistic Locking (conflicts_with Pessimistic)
    │      │
    │      └─ Race Condition
    │
    └─ Resource Management
         │
         └─ Garbage Collection (see_also)


LEGEND:
  ├─  : part_of / depends_on
  │   : continuation
  ─┬─ : branching
  ♦   : see_also (bidirectional)
  ✗   : conflicts_with
  →   : replaces
```

### 4.2 Mermaid Diagram Visualization

Mermaid generates clear, code-based diagrams.

```
graph TD
    subgraph Foundations
        DB["Database Connection"]
        TS["Thread Safety"]
        RM["Resource Management"]
    end

    subgraph Pooling
        CP["Connection Pool"]
        TP["Thread Pool"]
        MAX["Max Pool Size"]
        IDLE["Idle Timeout"]
        REC["Connection Recycling"]
    end

    subgraph Concurrency
        CC["Concurrency Control"]
        PL["Pessimistic Locking"]
        OL["Optimistic Locking"]
        DL["Deadlock"]
        RC["Race Condition"]
    end

    subgraph Management
        GC["Garbage Collection"]
        CL["Connection Leak"]
    end

    DB -->|part_of| CP
    DB -->|part_of| TP
    TS -->|part_of| CC
    RM -->|contains| GC

    CP -->|depends_on| DB
    CP -->|depends_on| TS
    MAX -->|depends_on| CP
    IDLE -->|depends_on| CP
    REC -->|depends_on| IDLE

    CP -.->|see_also| TP

    CC -->|depends_on| TS
    PL -->|specializes| CC
    OL -->|specializes| CC
    DL -->|depends_on| PL
    RC -->|conflicts_with| TS

    CL -->|depends_on| RM

    PL -.->|see_also| OL

    style DB fill:#90EE90
    style TS fill:#90EE90
    style RM fill:#90EE90
```

**Mermaid Syntax Explanation:**
```
graph TD                  # Top-Down graph
  A["Label"]             # Node with label
  A -->|text| B          # Directed edge with label
  A -.->|text| B         # Dashed edge (weaker relationship)
  A <-->|text| B         # Bidirectional edge
  subgraph Name          # Group of related nodes
    ...
  end
  style A fill:#color    # Styling for visual distinction
```

### 4.3 Neo4j Cypher Visualization

For larger graphs, use graph databases.

```cypher
-- Create concept nodes
CREATE (conn:Concept {name: "Database Connection", tier: "0"})
CREATE (pool:Concept {name: "Connection Pool", tier: "1"})
CREATE (maxSize:Concept {name: "Max Pool Size", tier: "2"})
CREATE (idle:Concept {name: "Idle Timeout", tier: "2"})
CREATE (threadSafety:Concept {name: "Thread Safety", tier: "0"})

-- Create relationships
CREATE (pool)-[:DEPENDS_ON {strength: "strong"}]->(conn)
CREATE (pool)-[:DEPENDS_ON {strength: "strong"}]->(threadSafety)
CREATE (maxSize)-[:DEPENDS_ON {strength: "weak"}]->(pool)
CREATE (idle)-[:DEPENDS_ON {strength: "strong"}]->(pool)
CREATE (maxSize)-[:SEE_ALSO {strength: "strong"}]->(idle)

-- Query: Find all dependencies of Connection Pool
MATCH (pool:Concept {name: "Connection Pool"})-[:DEPENDS_ON]->(dep)
RETURN pool.name, dep.name

-- Query: Find all concepts depending on Connection Pool
MATCH (concept)-[:DEPENDS_ON]->(pool:Concept {name: "Connection Pool"})
RETURN concept.name

-- Query: Find all paths of length <= 3
MATCH path=(start:Concept)-[*..3]->(end:Concept)
WHERE start.name = "Max Pool Size"
RETURN path
```

---

## 5. Graph Quality Metrics

### 5.1 Connectivity Metrics

| Metric | Definition | Calculation | Healthy Range | What It Means |
|--------|-----------|---|---|---|
| **Average In-Degree** | Average # of concepts depending on each concept | Sum(in_degree) / num_concepts | 1.5-3.0 | Higher = foundational concepts; too high indicates unclear structure |
| **Average Out-Degree** | Average # of concepts each concept depends on | Sum(out_degree) / num_concepts | 0.5-1.5 | Higher = many dependencies; good if distributed |
| **Density** | Percentage of possible edges present | actual_edges / (n × (n-1)) | 0.15-0.40 | Higher = tightly connected; too high = over-linked |
| **Connected Components** | # of disconnected subgraphs | Count connected regions | 1 | Should be 1; multiple = orphaned concepts |
| **Maximum Path Length** | Longest dependency chain | DFS from all roots | < 6 | Too deep = hard to understand; refactor |

### 5.2 Centrality Metrics

| Metric | Definition | Meaning |
|--------|-----------|---------|
| **Betweenness Centrality** | Concept acts as bridge between others | High = important intermediate concept; low = isolated or endpoint |
| **Closeness Centrality** | Average distance to other concepts | High = central to domain; low = peripheral |
| **Degree Centrality** | Total # of relationships | High = key concept; low = specialized concept |

### 5.3 Graph Quality Calculation

```python
from collections import defaultdict, deque
import statistics

class GraphQualityAnalyzer:
    def __init__(self, concepts: List[str], edges: List[Tuple[str, str, str]]):
        """
        Args:
            concepts: list of concept names
            edges: list of (source, relationship_type, target) tuples
        """
        self.concepts = set(concepts)
        self.edges = edges
        self.graph_in = defaultdict(list)   # node -> incoming edges
        self.graph_out = defaultdict(list)  # node -> outgoing edges

        for source, rel, target in edges:
            self.graph_in[target].append(source)
            self.graph_out[source].append(target)

    def compute_connectivity_metrics(self) -> dict:
        """Compute connectivity metrics for the graph."""
        in_degrees = [len(self.graph_in[c]) for c in self.concepts]
        out_degrees = [len(self.graph_out[c]) for c in self.concepts]

        total_edges = len(self.edges)
        possible_edges = len(self.concepts) * (len(self.concepts) - 1)
        density = total_edges / possible_edges if possible_edges > 0 else 0

        return {
            'num_concepts': len(self.concepts),
            'num_edges': total_edges,
            'avg_in_degree': statistics.mean(in_degrees) if in_degrees else 0,
            'avg_out_degree': statistics.mean(out_degrees) if out_degrees else 0,
            'max_in_degree': max(in_degrees) if in_degrees else 0,
            'max_out_degree': max(out_degrees) if out_degrees else 0,
            'density': density,
        }

    def find_orphaned_concepts(self) -> List[str]:
        """Find concepts with no relationships."""
        orphaned = []
        for concept in self.concepts:
            if len(self.graph_in[concept]) == 0 and len(self.graph_out[concept]) == 0:
                orphaned.append(concept)
        return orphaned

    def find_maximum_path_length(self) -> int:
        """Find longest dependency path in graph."""
        memo = {}

        def dfs_depth(node):
            if node in memo:
                return memo[node]
            if not self.graph_out[node]:
                return 0
            max_depth = 1 + max(dfs_depth(dep) for dep in self.graph_out[node])
            memo[node] = max_depth
            return max_depth

        max_length = 0
        for concept in self.concepts:
            max_length = max(max_length, dfs_depth(concept))

        return max_length

    def generate_quality_report(self) -> str:
        """Generate comprehensive quality report."""
        metrics = self.compute_connectivity_metrics()
        orphans = self.find_orphaned_concepts()
        max_path = self.find_maximum_path_length()

        report = "# Graph Quality Report\n\n"

        report += "## Connectivity Metrics\n\n"
        report += f"- Concepts: {metrics['num_concepts']}\n"
        report += f"- Relationships: {metrics['num_edges']}\n"
        report += f"- Density: {metrics['density']:.3f}\n"
        report += f"- Avg In-Degree: {metrics['avg_in_degree']:.2f}\n"
        report += f"- Avg Out-Degree: {metrics['avg_out_degree']:.2f}\n"
        report += f"- Max Path Length: {max_path}\n\n"

        # Quality assessment
        report += "## Quality Assessment\n\n"

        if metrics['density'] < 0.15:
            report += "⚠️  **Low density**: Graph is sparse; concepts may be under-linked\n"
        elif metrics['density'] > 0.40:
            report += "⚠️  **High density**: Graph is over-linked; consider refactoring\n"
        else:
            report += "✓ Density within healthy range\n"

        if max_path > 6:
            report += f"⚠️  **Deep hierarchy**: Maximum path length {max_path} > 6; consider refactoring\n"
        else:
            report += f"✓ Path length reasonable (max {max_path})\n"

        if orphans:
            report += f"⚠️  **Orphaned concepts** ({len(orphans)}): {', '.join(orphans)}\n"
        else:
            report += "✓ No orphaned concepts\n"

        return report

# Example
concepts = ["A", "B", "C", "D", "E"]
edges = [
    ("A", "depends_on", "B"),
    ("A", "depends_on", "C"),
    ("B", "depends_on", "D"),
    ("C", "depends_on", "E"),
]

analyzer = GraphQualityAnalyzer(concepts, edges)
print(analyzer.generate_quality_report())
```

---

## 6. Relationship Strength Assessment

Not all relationships have equal importance. Classify each relationship.

### Strength Levels

| Level | Definition | Usage | Example |
|-------|-----------|-------|---------|
| **Strong** | Concept cannot reasonably be understood without other concept | Hard requirement for understanding | Authentication depends_on (strong) Cryptography |
| **Weak** | Relationship exists but understanding is possible without it | Nice-to-have context | Cache see_also Memoization |
| **Implied** | Relationship exists but is indirect or contextual | May surface only in advanced usage | Circuit Breaker implements (implied) Fault Tolerance Pattern |

### Strength Assessment Questions

For each relationship, answer these questions to determine strength:

```
1. Can A be understood without knowing B?
   → Yes, completely → Weak
   → Yes, partially → Weak
   → No → Strong

2. Does B appear in A's definition?
   → Yes → Strong
   → No → Weak

3. How often do A and B appear together in documentation?
   → Always together → Strong
   → Sometimes together → Weak
   → Rarely together → Implied

4. Would an LLM make errors reasoning about A without knowing B?
   → Yes, critical errors → Strong
   → Yes, minor errors → Weak
   → No → Weak
```

---

## 7. Worked Example: Building a Complete Concept Graph

Starting from scratch, we'll build a concept graph for "Database Transactions and Concurrency Control."

### 7.1 Concepts (from v0.2.2a & v0.2.2b)

```
TIER 0 (Foundational):
  1. Database Transaction
  2. Concurrency Control
  3. Data Consistency

TIER 1 (Core):
  4. ACID Properties
  5. Pessimistic Locking
  6. Optimistic Locking
  7. Deadlock
  8. Isolation Level

SUPPORTING:
  9. Version Number
  10. Lock Manager
  11. Conflict Detection
  12. Rollback
```

### 7.2 Relationship Extraction

```python
relationships = [
    # Core dependencies (depends_on, strong)
    ("ACID Properties", "depends_on", "Database Transaction", "strong"),
    ("Pessimistic Locking", "depends_on", "Concurrency Control", "strong"),
    ("Optimistic Locking", "depends_on", "Concurrency Control", "strong"),
    ("Isolation Level", "depends_on", "Concurrency Control", "strong"),

    # Part-of relationships
    ("Atomicity", "part_of", "ACID Properties", "strong"),
    ("Consistency", "part_of", "ACID Properties", "strong"),
    ("Isolation", "part_of", "ACID Properties", "strong"),
    ("Durability", "part_of", "ACID Properties", "strong"),

    # Specializes relationships
    ("Pessimistic Locking", "specializes", "Concurrency Control", "strong"),
    ("Optimistic Locking", "specializes", "Concurrency Control", "strong"),

    # See also (cross-references)
    ("Pessimistic Locking", "see_also", "Optimistic Locking", "strong"),
    ("Lock Manager", "see_also", "Deadlock", "strong"),
    ("Version Number", "see_also", "Optimistic Locking", "strong"),

    # Implements
    ("Lock Manager", "implements", "Pessimistic Locking", "strong"),
    ("Version Number", "implements", "Optimistic Locking", "strong"),
    ("Conflict Detection", "implements", "Optimistic Locking", "strong"),

    # Conflicts
    ("Pessimistic Locking", "conflicts_with", "Optimistic Locking", "strong"),
    ("Deadlock", "conflicts_with", "Isolation", "strong"),

    # Depends (weak)
    ("Pessimistic Locking", "depends_on", "Lock Manager", "weak"),
    ("Optimistic Locking", "depends_on", "Version Number", "weak"),
    ("Deadlock", "depends_on", "Pessimistic Locking", "strong"),
    ("Rollback", "depends_on", "Database Transaction", "strong"),
]
```

### 7.3 Graph Construction

```python
class ConceptGraph:
    def __init__(self):
        self.concepts = {}  # name -> metadata
        self.edges = []     # (source, target, rel_type, strength)

    def add_concept(self, name: str, tier: str, definition: str):
        self.concepts[name] = {
            'tier': tier,
            'definition': definition,
            'in_degree': 0,
            'out_degree': 0
        }

    def add_relationship(self, source: str, rel_type: str, target: str, strength: str):
        if source in self.concepts and target in self.concepts:
            self.edges.append((source, target, rel_type, strength))
            self.concepts[source]['out_degree'] += 1
            self.concepts[target]['in_degree'] += 1

    def to_mermaid(self) -> str:
        """Generate Mermaid diagram."""
        mermaid = "graph TD\n"

        # Group by tier
        tiers = {}
        for name, meta in self.concepts.items():
            tier = meta['tier']
            if tier not in tiers:
                tiers[tier] = []
            tiers[tier].append(name)

        # Create subgraphs for tiers
        for tier in sorted(tiers.keys()):
            mermaid += f"\n    subgraph {tier}\n"
            for concept in tiers[tier]:
                mermaid += f'        {concept.replace(" ", "_")}["{concept}"]\n'
            mermaid += "    end\n"

        # Add edges
        for source, target, rel_type, strength in self.edges:
            source_id = source.replace(" ", "_")
            target_id = target.replace(" ", "_")

            # Styling based on relationship type
            style_map = {
                'depends_on': '-->',
                'see_also': '-.->',
                'conflicts_with': '- x -',
                'part_of': '==>',
                'specializes': '-- sp -->',
                'implements': '-- impl -->'
            }

            arrow = style_map.get(rel_type, '-->')
            mermaid += f"    {source_id} {arrow} {target_id}\n"

        return mermaid

# Build the graph
graph = ConceptGraph()

# Add concepts
concepts_list = [
    ("Database Transaction", "TIER 0", "Atomic unit of work..."),
    ("Concurrency Control", "TIER 0", "Mechanism for handling concurrent access..."),
    ("Data Consistency", "TIER 0", "State where data satisfies constraints..."),
    ("ACID Properties", "TIER 1", "Atomicity, Consistency, Isolation, Durability"),
    ("Pessimistic Locking", "TIER 1", "Acquires locks before accessing data..."),
    ("Optimistic Locking", "TIER 1", "Detects conflicts after the fact..."),
    ("Deadlock", "TIER 1", "Circular wait for locks..."),
    ("Isolation Level", "TIER 1", "Controls degree of isolation..."),
    ("Version Number", "SUPPORTING", "Tracks data versions..."),
    ("Lock Manager", "SUPPORTING", "Manages lock acquisition/release..."),
    ("Conflict Detection", "SUPPORTING", "Identifies conflicting updates..."),
    ("Rollback", "SUPPORTING", "Reverses transaction effects..."),
]

for name, tier, defn in concepts_list:
    graph.add_concept(name, tier, defn)

# Add relationships
for source, rel, target, strength in relationships:
    graph.add_relationship(source, rel, target, strength)

# Generate Mermaid
print(graph.to_mermaid())
```

### 7.4 Graph Diagram Output

```mermaid
graph TD
    subgraph TIER_0
        Database_Transaction["Database Transaction"]
        Concurrency_Control["Concurrency Control"]
        Data_Consistency["Data Consistency"]
    end

    subgraph TIER_1
        ACID_Properties["ACID Properties"]
        Pessimistic_Locking["Pessimistic Locking"]
        Optimistic_Locking["Optimistic Locking"]
        Deadlock["Deadlock"]
        Isolation_Level["Isolation Level"]
    end

    subgraph SUPPORTING
        Version_Number["Version Number"]
        Lock_Manager["Lock Manager"]
        Conflict_Detection["Conflict Detection"]
        Rollback["Rollback"]
    end

    ACID_Properties --> Database_Transaction
    Pessimistic_Locking --> Concurrency_Control
    Optimistic_Locking --> Concurrency_Control
    Isolation_Level --> Concurrency_Control

    Pessimistic_Locking -.-> Optimistic_Locking
    Lock_Manager -.-> Deadlock
    Version_Number -.-> Optimistic_Locking

    Lock_Manager ==> Pessimistic_Locking
    Version_Number ==> Optimistic_Locking
    Conflict_Detection ==> Optimistic_Locking

    Pessimistic_Locking -x Optimistic_Locking
    Deadlock -x Isolation_Level

    Pessimistic_Locking --> Lock_Manager
    Optimistic_Locking --> Version_Number
    Deadlock --> Pessimistic_Locking
    Rollback --> Database_Transaction
```

---

## 8. Python Graph Data Structure

Complete implementation for graph operations:

```python
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict, deque
import json

class ConceptGraph:
    """Complete concept graph implementation."""

    def __init__(self):
        self.concepts = {}  # name -> {definition, tier, ...}
        self.edges = {}     # (source, target) -> {rel_type, strength}
        self.adj_in = defaultdict(set)   # node -> incoming nodes
        self.adj_out = defaultdict(set)  # node -> outgoing nodes

    def add_concept(self, name: str, definition: str, tier: str = "0"):
        """Add a concept node."""
        self.concepts[name] = {
            'definition': definition,
            'tier': tier
        }

    def add_relationship(self, source: str, target: str, rel_type: str, strength: str = "strong"):
        """Add a directed edge between concepts."""
        if source not in self.concepts or target not in self.concepts:
            raise ValueError(f"Concept not found: {source} or {target}")

        key = (source, target)
        self.edges[key] = {'rel_type': rel_type, 'strength': strength}
        self.adj_out[source].add(target)
        self.adj_in[target].add(source)

    def get_dependencies(self, concept: str) -> Dict[str, str]:
        """Get all concepts that this concept depends on."""
        deps = {}
        for target in self.adj_out[concept]:
            edge = self.edges[(concept, target)]
            if edge['rel_type'] == 'depends_on':
                deps[target] = edge['strength']
        return deps

    def get_dependents(self, concept: str) -> Dict[str, str]:
        """Get all concepts that depend on this concept."""
        dependents = {}
        for source in self.adj_in[concept]:
            edge = self.edges[(source, concept)]
            if edge['rel_type'] == 'depends_on':
                dependents[source] = edge['strength']
        return dependents

    def get_related(self, concept: str) -> Dict[str, str]:
        """Get all concepts related by see_also."""
        related = {}
        for target in self.adj_out[concept]:
            edge = self.edges[(concept, target)]
            if edge['rel_type'] == 'see_also':
                related[target] = edge['strength']
        for source in self.adj_in[concept]:
            edge = self.edges[(source, concept)]
            if edge['rel_type'] == 'see_also':
                related[source] = edge['strength']
        return related

    def topological_sort(self) -> Optional[List[str]]:
        """
        Perform topological sort on dependency graph.
        Returns None if cycle exists.
        """
        in_degree = {c: 0 for c in self.concepts}

        # Calculate in-degrees considering only depends_on
        for source, target in self.edges:
            if self.edges[(source, target)]['rel_type'] == 'depends_on':
                in_degree[target] += 1

        # Queue of nodes with no incoming dependencies
        queue = deque([c for c in self.concepts if in_degree[c] == 0])
        sorted_list = []

        while queue:
            node = queue.popleft()
            sorted_list.append(node)

            for dependent in list(self.adj_out[node]):
                edge = self.edges[(node, dependent)]
                if edge['rel_type'] == 'depends_on':
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)

        # Check if all nodes were processed (no cycle)
        if len(sorted_list) != len(self.concepts):
            return None  # Cycle detected

        return sorted_list

    def export_to_neo4j(self) -> str:
        """Export as Neo4j Cypher CREATE statements."""
        cypher = "// DocStratum Concept Graph - Neo4j Import\n\n"

        # Create concepts
        for name, meta in self.concepts.items():
            defn = meta['definition'].replace('"', '\\"')
            tier = meta['tier']
            cypher += f'CREATE (:{name.replace(" ", "_")}:Concept {{name: "{name}", definition: "{defn}", tier: "{tier}"}})\n'

        cypher += "\n// Relationships\n\n"

        # Create relationships
        for (source, target), edge in self.edges.items():
            source_id = source.replace(" ", "_")
            target_id = target.replace(" ", "_")
            rel_type = edge['rel_type'].upper()
            strength = edge['strength']
            cypher += f'MATCH (a:Concept {{name: "{source}"}}), (b:Concept {{name: "{target}"}})\n'
            cypher += f'CREATE (a)-[:{rel_type} {{strength: "{strength}"}}]->(b)\n'

        return cypher

    def to_json(self) -> str:
        """Export graph as JSON."""
        graph_data = {
            'concepts': self.concepts,
            'edges': [
                {
                    'source': source,
                    'target': target,
                    'rel_type': edge['rel_type'],
                    'strength': edge['strength']
                }
                for (source, target), edge in self.edges.items()
            ]
        }
        return json.dumps(graph_data, indent=2)
```

---

## Deliverables Checklist

- [ ] **Relationship Taxonomy Document**: All 7 types with definitions, examples, and syntax
- [ ] **Cycle Detection Implementation**: Python script identifying and reporting cycles
- [ ] **Graph Quality Metrics**: Automated calculator with connectivity, centrality, path analysis
- [ ] **Visualization Tools**: Mermaid generator, ASCII renderer, Neo4j exporter
- [ ] **Complete Concept Graph**: 50+ concepts with 100+ relationships, no cycles
- [ ] **Quality Report**: Metrics showing density, path length, orphaned concepts
- [ ] **Neo4j Import File**: Cypher statements for graph database storage
- [ ] **Graph Data Structure**: Python implementation supporting all operations

## Acceptance Criteria

1. **Zero Cycles**: Topological sort succeeds; dependency graph is acyclic
2. **All Concepts Linked**: No orphaned concepts (100% connectivity)
3. **Relationship Typing**: 100% of relationships have explicit type from taxonomy
4. **Strength Assessment**: All strong/weak classifications documented with rationale
5. **Graph Density**: 0.15-0.40 (not sparse, not over-linked)
6. **Path Length**: Maximum dependency chain < 6 levels
7. **Mermaid Validity**: Diagram generates without errors
8. **Neo4j Validity**: Cypher statements execute without errors
9. **Quality Metrics**: Report documents all health indicators

## Next Steps

Once the concept graph is complete and validated, proceed to **v0.2.2d: Anti-Pattern Documentation & Misconception Mining** to add anti-pattern coverage that prevents LLM misunderstanding at concept boundaries.
