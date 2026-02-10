# v0.5.2 — Evidence Capture

> **Task:** Capture screenshots, logs, and other evidence for documentation.
> 

---

## Task Overview

---

## Evidence Checklist

### Screenshots

- [ ]  `docs/validation/test1_comparison.png` — Disambiguation test side-by-side
- [ ]  `docs/validation/test2_comparison.png` — Freshness test side-by-side
- [ ]  `docs/validation/test3_comparison.png` — Few-shot test side-by-side
- [ ]  `docs/validation/streamlit_demo.png` — Full demo UI
- [ ]  `docs/validation/metrics_dashboard.png` — Metrics display

### Logs

- [ ]  `docs/validation/full_results.txt` — Complete test output
- [ ]  `docs/validation/token_usage.json` — Token counts per test

### Optional

- [ ]  `docs/validation/demo_[recording.mp](http://recording.mp)4` — Screen recording of demo
- [ ]  `docs/validation/concept_graph.png` — Neo4j or Obsidian graph

---

## Screenshot Guidelines

### For Streamlit

1. Set browser to 1280x800 resolution
2. Use light theme for readability
3. Capture full comparison view
4. Include metrics row

### For Terminal

```bash
# Use script to capture output
script -q docs/validation/session.txt
python run_ab_test.py --suite
exit
```

---

## File Organization

```
docs/
└── validation/
    ├── test1_comparison.png
    ├── test2_comparison.png
    ├── test3_comparison.png
    ├── streamlit_demo.png
    ├── metrics_dashboard.png
    ├── full_results.txt
    └── token_usage.json
```

---

## Token Usage Template

```json
// docs/validation/token_usage.json
{
  "tests": [
    {
      "name": "Disambiguation Test",
      "baseline": {
        "prompt_tokens": 0,
        "completion_tokens": 0
      },
      "docstratum": {
        "prompt_tokens": 0,
        "completion_tokens": 0
      }
    }
  ],
  "context_tokens": 0,
  "total_baseline_tokens": 0,
  "total_docstratum_tokens": 0
}
```

---

## Acceptance Criteria

- [ ]  All required screenshots captured
- [ ]  Screenshots are clear and readable
- [ ]  Full test log saved
- [ ]  Token usage documented
- [ ]  Files organized in `docs/validation/`