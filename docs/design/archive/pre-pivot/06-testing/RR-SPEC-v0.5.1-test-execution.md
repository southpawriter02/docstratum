# v0.5.1 — Test Execution

> **Task:** Execute the three validation tests and record results.
> 

---

## Task Overview

---

## Test Execution Checklist

### Test 1: Disambiguation Test

**Setup:**

```bash
python run_ab_test.py -q "Should I use OAuth2 or API keys for my server-side script?"
```

**Expected Baseline:**

- Generic explanation of both methods
- No clear recommendation
- May suggest either could work

**Expected DocStratum:**

- Direct recommendation: "Use API keys"
- Cites anti-pattern: "OAuth2 is NOT required for server-to-server"
- Links to authentication docs

**Execution:**

- [ ]  Test executed
- [ ]  Baseline response captured
- [ ]  DocStratum response captured
- [ ]  Screenshot saved: `docs/validation/test1.png`

**Result:** ⬜ PASS / ⬜ FAIL

**Notes:**

```
[Record observations here]
```

---

### Test 2: Freshness Test

**Setup:**

```bash
python run_ab_test.py -q "Is the /users/create endpoint still available?"
```

**Expected Baseline:**

- Confident answer based on training data
- No acknowledgment of uncertainty
- May provide outdated information

**Expected DocStratum:**

- References `last_verified` date
- Hedges: "According to documentation verified on [DATE]..."
- Directs to source URL for current status

**Execution:**

- [ ]  Test executed
- [ ]  Baseline response captured
- [ ]  DocStratum response captured
- [ ]  Screenshot saved: `docs/validation/test2.png`

**Result:** ⬜ PASS / ⬜ FAIL

**Notes:**

```
[Record observations here]
```

---

### Test 3: Few-Shot Adherence Test

**Setup:**

```bash
python run_ab_test.py -q "How do I add login to my React app?"
```

**Expected Baseline:**

- Generic React auth advice
- May suggest any auth library
- No specific structure

**Expected DocStratum:**

- Numbered steps (1, 2, 3...)
- Specific SDK installation command
- Code snippet with `ExampleAuth`
- Matches few-shot example format

**Execution:**

- [ ]  Test executed
- [ ]  Baseline response captured
- [ ]  DocStratum response captured
- [ ]  Screenshot saved: `docs/validation/test3.png`

**Result:** ⬜ PASS / ⬜ FAIL

**Notes:**

```
[Record observations here]
```

---

## Full Test Suite Command

```bash
# Run all three at once
python run_ab_test.py --suite > docs/validation/full_results.txt
```

---

## Acceptance Criteria

- [ ]  All 3 tests executed
- [ ]  Results documented in this page
- [ ]  Screenshots saved to `docs/validation/`
- [ ]  Pass/fail determined for each test