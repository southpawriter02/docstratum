# v0.2.2 — Concept Extraction

> **Task:** Identify and document the semantic concepts and their relationships from the source documentation.
> 

---

## Task Overview

---

## The Writer's Method

<aside>

**Key Insight:** This is where Technical Writing skills shine. You're not just listing terms—you're building a *knowledge graph* that captures how ideas relate to each other.

</aside>

---

## Workflow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 1. Identify │───▶│ 2. Define   │───▶│ 3. Map      │───▶│ 4. Document │
│   concepts  │    │   precisely │    │   relations │    │   anti-patt │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

---

## Step 1: Concept Identification

### What Makes a "Concept"?

A concept is NOT just any noun. It's an idea that:

- Requires explanation to understand
- Is referenced across multiple pages
- Has specific meaning in this domain
- Can be misunderstood (has anti-patterns)

### Mining Techniques

---

## Step 2: Precise Definitions

### Definition Rules

**DO:**

- Use one complete sentence
- Name the concept in the definition
- State what category it belongs to
- Be specific to THIS documentation

**DON'T:**

- Use pronouns (it, this, they)
- Use circular definitions
- Copy Wikipedia verbatim
- Assume prior knowledge

### Template

```
[CONCEPT NAME] is a [CATEGORY] that [DOES WHAT] for [PURPOSE].
```

### Examples

---

## Step 3: Relationship Mapping

### Relationship Types

### Graph Sketch

Draw a simple dependency graph:

```
               ┌─────────────────┐
               │   Credentials   │
               └────────┬────────┘
                        │
         ┌──────────────┴──────────────┐
         ▼                             ▼
┌─────────────────┐           ┌─────────────────┐
│    API Keys     │           │     OAuth2      │
│ (server-to-server)          │ (user-facing)   │
└────────┬────────┘           └────────┬────────┘
         │                             │
         │      ┌──────────────────────┘
         ▼      ▼
┌─────────────────┐
│   API Access    │
└─────────────────┘
```

---

## Step 4: Anti-Pattern Documentation

### What's an Anti-Pattern?

An anti-pattern is a **common mistake** users make. Documenting these:

- Prevents hallucinations (AI won't suggest wrong approaches)
- Shows expertise (you know the pitfalls)
- Saves user frustration

### Mining Anti-Patterns

Look for:

- "Don't do X"
- "Common mistake: ..."
- "Note: X is NOT the same as Y"
- FAQ entries about confusion
- Stack Overflow questions about the docs

### Template

```
"[CONCEPT] is NOT [COMMON MISCONCEPTION]. Instead, [CORRECT UNDERSTANDING]."
```

---

## Concept Documentation Template

```yaml
# For each concept, fill out:

- id: "concept-id-here"
  name: "Human-Readable Name"
  definition: "One sentence. No pronouns. Specific to this domain."
  related_pages:
    - "https://docs.example.com/page1"
    - "https://docs.example.com/page2"
  depends_on:
    - "prerequisite-concept-id"
  anti_patterns:
    - "This is NOT the same as [similar concept]."
    - "Do NOT [common mistake]."
```

---

## 📂 Sub-Part Pages

[v0.2.2a — Concept Identification & Mining Techniques](RR-SPEC-v0.2.2a-concept-identification-and-mining-techniques.md) — TF-IDF analysis, glossary extraction, heading mining, NLP-based concept candidate extraction

[v0.2.2b — Precision Definition Writing](RR-SPEC-v0.2.2b-precision-definition-writing.md) — Quality rubric, 7 definition templates by concept type, no-pronouns rule with 8+ before/after pairs

[v0.2.2c — Relationship Mapping & Dependency Graphs](RR-SPEC-v0.2.2c-relationship-mapping-and-dependency-graphs.md) — 7-type relationship taxonomy, graph construction, cycle detection, Mermaid/Neo4j visualization

[v0.2.2d — Anti-Pattern Documentation & Misconception Mining](RR-SPEC-v0.2.2d-anti-pattern-documentation-and-misconception-mining.md) — Mining sources, 5 classification categories, effectiveness scoring, LLM validation methodology

---

## Acceptance Criteria

- [ ]  At least 5 concepts identified
- [ ]  Each concept has a pronoun-free definition
- [ ]  Dependency graph sketched
- [ ]  At least 2 anti-patterns per concept (where applicable)
- [ ]  All concepts linked to related pages
- [ ]  **v0.2.2a:** Concept mining methodology applied with scored candidates
- [ ]  **v0.2.2b:** All definitions pass quality rubric (score ≥ 3.5/5.0)
- [ ]  **v0.2.2c:** Full relationship graph with cycle detection passed
- [ ]  **v0.2.2d:** Anti-patterns validated against LLM behavior