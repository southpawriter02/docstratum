# v0.3.4 — DocStratum Agent

> **Task:** Create the enhanced agent with full DocStratum context injection.
> 

---

## Task Overview

---

## Implementation

The `create_docstratum_agent()` function was already implemented in v0.3.3. This task focuses on integration testing.

---

## Integration Test

### File: `test_docstratum_[manual.py](http://manual.py)`

```python
"""Manual integration test for DocStratum agent."""

from core.loader import load_llms_txt
from core.context import build_context_block
from core.agents import create_docstratum_agent

def main():
    # Load llms.txt
    llms = load_llms_txt('data/llms.txt')
    print(f"Loaded: {llms.site_name}")
    
    # Build context
    context = build_context_block(llms)
    print(f"Context: {len(context)} chars")
    
    # Create agent
    agent = create_docstratum_agent(context)
    
    # Test questions
    questions = [
        "How do I authenticate my Python script?",
        "What's the difference between OAuth2 and API keys?",
        "What happens if my prompt is too long?"
    ]
    
    for q in questions:
        print(f"\n{'='*60}")
        print(f"Q: {q}")
        print('='*60)
        result = agent.invoke(q)
        print(f"\nA: {result['response']}")
        print(f"\n[Tokens: {result['prompt_tokens']} + {result['completion_tokens']}]")

if __name__ == '__main__':
    main()
```

---

## Expected Behavior Comparison

---

## Key Differences to Verify

- [ ]  DocStratum agent cites specific URLs
- [ ]  DocStratum agent mentions anti-patterns
- [ ]  DocStratum agent uses domain terminology
- [ ]  DocStratum agent follows few-shot format
- [ ]  DocStratum agent acknowledges verification dates

---

## 📂 Sub-Part Pages

[v0.3.4a — Context Injection & System Prompt Assembly](RR-SPEC-v0.3.4a-context-injection-and-system-prompt-assembly.md) — Context block injection strategy, prompt structure, size management, freshness tracking, DocStratumPromptBuilder

[v0.3.4b — Behavioral Verification & Quality Signals](RR-SPEC-v0.3.4b-behavioral-verification-and-quality-signals.md) — 5 behavioral signals, PatternDetector, scoring rubric (0-5), BehaviorVerifier class, false positive analysis

[v0.3.4c — Integration Testing & End-to-End Pipeline](RR-SPEC-v0.3.4c-integration-testing-and-end-to-end-pipeline.md) — E2E pipeline test, test question categories (disambiguation/freshness/few-shot), regression detection, CI workflow

[v0.3.4d — Multi-Provider Testing & Fallback Strategy](RR-SPEC-v0.3.4d-multi-provider-testing-and-fallback-strategy.md) — Cross-provider testing, prompt adjustments per model, fallback chain, cost analysis, provider recommendation

---

## Acceptance Criteria

- [ ]  DocStratum agent created with context
- [ ]  Agent responds with documentation-specific answers
- [ ]  Agent cites URLs from `llms.txt`
- [ ]  Agent mentions anti-patterns when relevant
- [ ]  Token counts tracked
- [ ]  **v0.3.4a:** Context injection produces valid system prompt under token limit
- [ ]  **v0.3.4b:** BehaviorVerifier detects all 5 quality signals with ≥80% accuracy
- [ ]  **v0.3.4c:** E2E pipeline passes all 3 validation test categories
- [ ]  **v0.3.4d:** Fallback chain handles primary provider failure gracefully