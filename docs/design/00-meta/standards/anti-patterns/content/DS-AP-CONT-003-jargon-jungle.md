# DS-AP-CONT-003: Jargon Jungle

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-AP-CONT-003 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Registry ID** | AP-CONT-003 |
| **Category** | Content |
| **Check ID** | CHECK-012 |
| **Severity Impact** | Reduce content dimension score |
| **Provenance** | v0.0.4c §Anti-Patterns Catalog |

## Description

Heavy use of domain-specific jargon and project-specific terminology without definitions, inline explanations, or glossary links. LLM agents cannot reliably infer the meanings of project-specific terms and must either make incorrect assumptions or halt processing. This anti-pattern isolates documentation from both human readers unfamiliar with the domain and autonomous agents lacking external context.

## Detection Logic

```python
def detect_jargon_jungle(content, common_dict):
    """
    Identify undefined jargon terms appearing multiple times.
    
    Algorithm:
    1. Tokenize content into words
    2. For each token:
       a. Check if in common English dictionary
       b. If not, check if used ≥3 times in content
       c. Check if followed by explanation (": ", "—", parenthetical def)
       d. Check if linked to glossary entry
    3. If undefined term appears ≥3 times, flag
    
    Returns: list of (term, frequency, has_definition)
    """
    import re
    from collections import Counter
    
    words = re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b', content)
    word_counts = Counter(words)
    
    def has_inline_definition(term, text):
        pattern = rf'{term}\s*(?::\s*|—\s*|\(.*?\))'
        return bool(re.search(pattern, text))
    
    jargon_terms = []
    for term, count in word_counts.items():
        if count >= 3 and term not in common_dict:
            has_def = has_inline_definition(term, content)
            if not has_def:
                jargon_terms.append((term, count, False))
    
    return len(jargon_terms) > 0, jargon_terms
```

## Example (Synthetic)

```markdown
The TSQL parser leverages AST transformation to normalize DSL queries before JIT compilation. 
The DAG resolver uses topological sorting to handle cyclic EDHOC dependencies. 
Configure TSQL options in the manifest; ensure EDHOC mitigation is enabled for TSQL instances.
```

Terms like TSQL, DSL, AST, DAG, EDHOC, and JIT appear without definitions. An LLM agent reading this may not understand the architecture or how to configure the system correctly.

## Remediation

1. Create or link to a glossary for domain-specific terms
2. Provide inline definitions the first time a new term appears
3. Use plain language explanations before introducing jargon
4. For acronyms, spell out the full form on first use: "Abstract Syntax Tree (AST)"
5. Consider restructuring sections to introduce foundational concepts before advanced terminology
6. Maintain a style guide emphasizing clarity over brevity

## Affected Criteria

- DS-VC-APD-004 (Content must be accessible)
- DS-VC-APD-008 (Jargon Defined or Linked — terminology must be contextualized)

## Emitted Diagnostics

- DS-DC-I007 (JARGON_WITHOUT_DEFINITION — informational notice for undefined terms)

## Related Anti-Patterns

- DS-AP-CONT-008 (Silent Agent — absence of LLM guidance compounds jargon comprehension problems)

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.2 |
