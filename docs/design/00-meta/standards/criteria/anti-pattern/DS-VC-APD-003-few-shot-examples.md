# DS-VC-APD-003: Few-Shot Examples

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VC-APD-003 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Platinum ID** | L4-03 |
| **Dimension** | Anti-Pattern Detection (20%) |
| **Level** | L4 — Exemplary |
| **Weight** | 3 / 20 anti-pattern points [CALIBRATION-NEEDED] |
| **Pass Type** | SOFT |
| **Measurability** | Heuristic |
| **Provenance** | v0.0.4d DECISION-002 Layer 3 (Few-Shot Bank); in-context learning research: 1–3 examples dramatically improve LLM task performance; v0.0.1b Gap #2 |

## Description

This criterion checks that the file contains at least one pedagogical example that demonstrates typical usage in a way a consuming LLM can learn from. Few-shot examples are the third and highest layer of semantic enrichment in the v0.0.4d 3-Layer Architecture (DECISION-002). They provide concrete instantiations of abstract concepts, dramatically improving agent task performance through in-context learning.

Research on in-context learning (scaling laws, prompt engineering studies) consistently shows that presenting 1–3 well-chosen examples before asking an LLM to solve a problem improves task completion rates by 15–40%. Few-shot examples can take several forms:

- Question/answer pairs (Q&A format)
- Input/output examples (code transformations, API calls)
- Before/after comparisons (refactoring, migrations)
- Scenario-based walkthroughs (use-case narratives)
- Code snippets paired with explanatory text

This criterion rewards files that include structured, pedagogically sound examples alongside conceptual explanations and instructions.

## Pass Condition

The file contains at least one recognizable few-shot example pattern:

```python
FEW_SHOT_PATTERNS = [
    r'(?i)#+\s*examples?',                    # Example/Examples header
    r'(?i)(?:input|question|before)\s*:.*(?:output|answer|after)\s*:',  # I/O pairs
    r'```[\s\S]*?```[\s\S]*?```',            # Paired code blocks (2+ in sequence)
    r'(?i)(?:for example|e\.g\.|such as)',    # Inline example phrases
]
has_examples = any(
    re.search(p, content)
    for p in FEW_SHOT_PATTERNS
)

# Also check for Examples/Usage/Use Cases section with code blocks
h2_sections = parse_h2_headings(content)
has_examples_section = any(
    s.name.lower() in {
        'examples', 'usage', 'use cases', 'tutorials',
        'recipes', 'sample code', 'code examples'
    }
    and any(child.type == 'fenced_code_block' for child in s.children)
    for s in h2_sections
)

assert has_examples or has_examples_section
```

**Note:** Pattern detection is heuristic. The validator searches for recognizable structural markers of examples. [CALIBRATION-NEEDED: refinement of pattern sensitivity and false positive reduction].

## Fail Condition

The file contains **no** recognizable few-shot examples:

- No "Examples", "Usage", or "Use Cases" section exists
- No section headers with "example" in the name
- No question/answer or input/output paired content
- No code blocks are present despite being a technical project
- All content is descriptive or procedural without concrete demonstrations

**Gate behavior:** This is a SOFT criterion at L4. Failure reduces the Anti-Pattern Detection score but does not block progression.

## Emitted Diagnostics

- **DS-DC-I003** (INFO): Emitted when no few-shot Q&A or example patterns are found. Suggests adding an "Examples" or "Usage" section with concrete code samples.

## Related Anti-Patterns

- **DS-AP-CONT-006** (Example Void): No code examples despite being a technical project. APD-003 directly counters this anti-pattern by verifying the presence of pedagogical examples.

## Related Criteria

- **DS-VC-CON-010** (Code Examples Present): Checks for the simple **presence** of any code block. APD-003 checks for **structured, pedagogical** examples (paired code blocks, Q&A examples, etc.). CON-010 is foundational; APD-003 is aspirational.
- **DS-VC-APD-001** (LLM Instructions Section): Instructions paired with examples create the most effective LLM-facing content.
- **DS-VC-APD-002** (Concept Definitions): Concepts followed by examples reinforce understanding.

## Calibration Notes

Research on in-context learning consistently shows dramatic improvements with few-shot examples. The v0.0.4d 3-Layer Architecture (DECISION-002) places few-shot examples as the highest enrichment level, reflecting their importance to LLM task performance.

In the v0.0.2c audit:
- **16 files (67%)** contained no structured few-shot examples
- **5 files (21%)** had examples but presented in unstructured ways (scattered, unlabeled)
- **3 files (12%)** had explicit "Examples" or "Usage" sections with clear pedagogical structure
- Files with structured few-shot examples showed the most dramatic improvement in agent task completion (average improvement: 25–40%)

Very few current llms.txt files include structured few-shot examples. The top-scoring specimens (Svelte 92, Pydantic 90) both include clear "Examples" sections with problem/solution pairs or input/output demonstrations. This criterion recognizes that exemplary files go beyond description to provide concrete learning material for consuming agents.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase C exemplary criterion |
