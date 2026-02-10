# v0.4.4 — Neo4j Integration (Optional)

> **Task:** Add optional graph visualization using Neo4j.
> 

---

## Task Overview

---

## Why This Is Optional

Neo4j adds complexity that may not be worth it for a weekend PoC:

- Requires separate database setup
- Additional Docker container
- Learning Cypher query language

**Recommendation:** Skip for v0.6.0 release. Add in v0.7.0 if time permits.

---

## Quick Setup (If Proceeding)

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  neo4j:
    image: neo4j:5-community
    ports:
      - "7474:7474"  # Browser
      - "7687:7687"  # Bolt
    environment:
      - NEO4J_AUTH=neo4j/password123
    volumes:
      - neo4j_data:/data

volumes:
  neo4j_data:
```

### Graph Population Script

```python
# scripts/populate_neo4j.py
from neo4j import GraphDatabase
from core.loader import load_llms_txt

def populate_graph(llms_path: str, neo4j_uri: str, user: str, password: str):
    llms = load_llms_txt(llms_path)
    driver = GraphDatabase.driver(neo4j_uri, auth=(user, password))
    
    with driver.session() as session:
        # Clear existing
        session.run("MATCH (n) DETACH DELETE n")
        
        # Create concepts
        for concept in llms.concepts:
            session.run(
                "CREATE (c:Concept {id: $id, name: $name, definition: $definition})",
                id=concept.id, name=concept.name, definition=concept.definition
            )
        
        # Create relationships
        for concept in llms.concepts:
            for dep_id in concept.depends_on:
                session.run(
                    """
                    MATCH (a:Concept {id: $from_id})
                    MATCH (b:Concept {id: $to_id})
                    CREATE (a)-[:DEPENDS_ON]->(b)
                    """,
                    from_id=concept.id, to_id=dep_id
                )
    
    driver.close()
    print(f"Populated graph with {len(llms.concepts)} concepts")

if __name__ == '__main__':
    populate_graph(
        'data/llms.txt',
        'bolt://localhost:7687',
        'neo4j',
        'password123'
    )
```

---

## Alternative: Obsidian Graph

For a simpler visualization:

1. Export concepts to Obsidian-compatible Markdown
2. Use Obsidian's built-in graph view
3. Screenshot for documentation

```python
# scripts/export_to_obsidian.py
def export_to_obsidian(llms_path: str, output_dir: str):
    from pathlib import Path
    from core.loader import load_llms_txt
    
    llms = load_llms_txt(llms_path)
    out = Path(output_dir)
    out.mkdir(exist_ok=True)
    
    for concept in llms.concepts:
        filename = f"{concept.name}.md"
        content = f"# {concept.name}\n\n{concept.definition}\n\n"
        
        if concept.depends_on:
            content += "## Dependencies\n"
            for dep in concept.depends_on:
                content += f"- [[{dep}]]\n"
        
        (out / filename).write_text(content)
    
    print(f"Exported {len(llms.concepts)} concepts to {output_dir}")
```

---

## 📂 Sub-Part Pages

[v0.4.4a — Graph Database Design & Neo4j Schema](RR-SPEC-v0.4.4a-graph-database-design-and-neo4j-schema.md)

[v0.4.4b — Docker Infrastructure & Environment Setup](RR-SPEC-v0.4.4b-docker-infrastructure-and-environment-setup.md)

[v0.4.4c — Graph Population & Data Pipeline](RR-SPEC-v0.4.4c-graph-population-and-data-pipeline.md)

[v0.4.4d — Visualization Alternatives & Obsidian Export](RR-SPEC-v0.4.4d-visualization-alternatives-and-obsidian-export.md)

---

## Acceptance Criteria (If Completed)

- [ ]  Neo4j container running
- [ ]  Concepts visible in Neo4j browser
- [ ]  Relationships displayed
- [ ]  Screenshot captured for docs

**OR (Alternative)**

- [ ]  Obsidian export working
- [ ]  Graph view screenshot captured

### Extended (Per Sub-Part)

- [ ]  v0.4.4a: Graph schema designed with Cypher query catalog
- [ ]  v0.4.4b: Docker infrastructure configured with health checks
- [ ]  v0.4.4c: Graph population pipeline tested with verification queries
- [ ]  v0.4.4d: Visualization alternative selected and implemented

---

## Phase v0.4.0 Complete Checklist

- [ ]  v0.4.1: Streamlit scaffold running
- [ ]  v0.4.2: Side-by-side display working
- [ ]  v0.4.3: Metrics dashboard complete
- [ ]  v0.4.4: (Optional) Graph visualization

**→ Ready to proceed to v0.5.0: Testing & Validation**