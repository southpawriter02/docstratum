# DS-AP-CONT-006: Example Void

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-AP-CONT-006 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Registry ID** | AP-CONT-006 |
| **Category** | Content |
| **Check ID** | CHECK-015 |
| **Severity Impact** | Reduce content dimension score |
| **Provenance** | v0.0.4c §Anti-Patterns Catalog |

## Description

Technical documentation lacks code examples despite addressing a software project. Code examples represent one of the strongest quality predictors (correlation r~0.65 in v0.0.2c audit data). This anti-pattern forces both human developers and LLM agents to imagine implementation details without concrete reference points, increasing the likelihood of misunderstanding or incorrect implementation.

## Detection Logic

```python
def detect_example_void(content):
    """
    Identify technical files with no code examples.
    
    Algorithm:
    1. Search for fenced code blocks: ``` or ~~~ markers
    2. Count fenced code blocks in content
    3. If count == 0, trigger anti-pattern
    4. Note: inline `code` (backtick) does not count as example
    5. Scope: only files with technical keywords (API, config, function, class, etc.)
    
    Returns: (triggered, code_block_count)
    """
    import re
    
    # Match fenced code blocks
    fenced_pattern = r'```|~~~'
    matches = re.findall(fenced_pattern, content)
    code_block_count = len(matches) // 2  # Opening + closing pair
    
    # Check for technical keywords
    technical_keywords = r'\b(API|function|method|class|module|library|code|config|syntax|implementation|example|usage)\b'
    has_technical_content = bool(re.search(technical_keywords, content, re.IGNORECASE))
    
    triggered = has_technical_content and code_block_count == 0
    return triggered, code_block_count
```

## Example (Synthetic)

```markdown
## Integration Guide

To integrate the payment module, you need to instantiate the PaymentProcessor class 
and call its process() method with a transaction object. The method returns a 
ProcessingResult containing status and transaction ID.

Configuration is handled through environment variables. You should also implement 
error handling for declined transactions and timeouts.

See the API reference for detailed parameter documentation.
```

This section describes API integration but provides zero code examples. A developer must guess the correct syntax for instantiation, method invocation, error handling, and configuration.

## Remediation

1. Add practical code examples for every major feature or API endpoint documented
2. Include working, tested code snippets (not pseudocode) when possible
3. Show both success and error handling paths
4. Provide examples in the primary language of the project; include secondary languages if widely used
5. For configuration topics, include sample config files or environment variable examples
6. Test all code examples to ensure they remain valid through product updates
7. Consider adding a style guide for consistent example formatting and quality

## Affected Criteria

- DS-VC-APD-004 (Content must include practical guidance)
- DS-VC-CON-010 (Code Examples Present — technical content requires example code)

## Emitted Diagnostics

- DS-DC-W004 (NO_CODE_EXAMPLES — warning for technical files without code blocks)

## Related Anti-Patterns

- DS-AP-CONT-008 (Silent Agent — absence of LLM instructions often correlates with absence of examples)

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.2 |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
