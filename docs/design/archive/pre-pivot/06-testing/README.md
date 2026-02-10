# 06-testing — Testing & Validation (v0.5.x)

> **Purpose**: Test execution, evidence capture, and metrics analysis

This phase validates the DocStratum's effectiveness through systematic behavioral testing, evidence collection, and quantitative analysis.

---

## 📚 Phase Structure

### v0.5.0 — Testing & Validation

- Overview of testing philosophy
- Test design principles
- Success criteria definition

### v0.5.1 — Test Execution

- Test suite implementation
- Automated test runner
- Manual verification procedures

### v0.5.2 — Evidence Capture

- Screenshot collection
- Response logging
- Metrics recording
- Video demonstrations

### v0.5.3 — Metrics Analysis

- Statistical analysis
- Comparative reporting
- Visualization generation
- Insights synthesis

---

## 🧪 Testing Philosophy

> **"Don't test if the code runs. Test if the output is useful."**

These are **behavioral tests**, not unit tests. We're validating:

- Agent response quality
- Citation accuracy
- Format adherence
- Hallucination prevention

---

## 🎯 The Three Validation Prompts

### Test 1: The Disambiguation Test

**Purpose**: Prove the agent can distinguish between similar concepts

**Example Question**:

> "What's the difference between OAuth2 and API keys?"

**Expected Behavior**:

- ❌ **Baseline**: Generic explanation, no specific guidance
- ✅ **DocStratum**: Cites anti-pattern from concept map, explains when to use each

**Success Criteria**:

- DocStratum agent references the `depends_on` relationship
- Cites specific documentation URLs
- Includes anti-pattern warning from concept map

---

### Test 2: The Freshness Test

**Purpose**: Prove the agent respects version/date information

**Example Question**:

> "What's the latest version of the API?"

**Expected Behavior**:

- ❌ **Baseline**: Guesses or says "I don't know"
- ✅ **DocStratum**: Cites `last_updated` timestamp from metadata

**Success Criteria**:

- DocStratum agent references the `last_verified` date
- Provides accurate version information
- Warns if information may be outdated

---

### Test 3: The Few-Shot Adherence Test

**Purpose**: Prove the agent follows the prescribed answer format

**Example Question**:

> "How do I add login to my React app?"

**Expected Behavior**:

- ❌ **Baseline**: Unstructured explanation
- ✅ **DocStratum**: Follows the exact format from few-shot examples (numbered steps, code block, source citation)

**Success Criteria**:

- Response matches few-shot example structure
- Includes code snippet
- Cites source pages
- Uses numbered steps

---

## 📊 Metrics Collection

### Quantitative Metrics

- **Token Count** — Input/output tokens for cost analysis
- **Citation Count** — Number of URLs referenced
- **Response Time** — Latency in seconds
- **Quality Score** — Composite score (0-10)

### Qualitative Metrics

- **Format Adherence** — Binary (matches few-shot format or not)
- **Hallucination Detection** — Binary (invented facts or not)
- **Completeness** — Binary (answers all parts of question or not)
- **Code Quality** — Binary (runnable code or not)

---

## 🔧 Evidence Artifacts

### Required Artifacts

1. **Test Results Table** (CSV/Markdown)
   - Question, Baseline Response, DocStratum Response, Metrics
2. **Screenshots** (PNG)
   - Side-by-side comparison in Streamlit UI
3. **Response Logs** (JSON)
   - Full agent responses with metadata
4. **Metrics Dashboard** (PNG/HTML)
   - Visualization of comparative metrics
5. **Demo Video** (MP4)
   - 2-minute walkthrough of A/B testing

---

## 🎯 Success Criteria

This testing phase is complete when:

- ✅ All three validation prompts pass
- ✅ DocStratum agent outperforms baseline on quality score
- ✅ Evidence artifacts are collected and documented
- ✅ Metrics analysis shows statistically significant improvement
- ✅ Demo video is recorded and polished
- ✅ Test results are reproducible

---

## 🗺️ Next Phase

After completing testing, proceed to:

- **`07-release/`** — Documentation polish and publication
