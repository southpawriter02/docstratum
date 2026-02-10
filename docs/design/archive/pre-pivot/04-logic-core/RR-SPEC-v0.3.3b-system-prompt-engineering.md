# System Prompt Engineering

> **v0.3.3b Baseline Agent — Logic Core**
> Designs the baseline system prompt that serves as a control group. This generic prompt should be helpful without any domain-specific knowledge, allowing fair comparison with the DocStratum-enhanced prompt in v0.3.4.

## Objective

Create a baseline system prompt that:
- Provides helpful documentation assistance without domain knowledge
- Establishes consistent response format and quality expectations
- Remains fair and comparable to the DocStratum prompt (same length, same structure)
- Never accidentally includes domain-specific information
- Can be versioned and A/B tested against alternatives

## Scope Boundaries

**INCLUDES:**
- Baseline system prompt design philosophy
- Prompt template structure and sections
- What the baseline should know (general documentation patterns)
- What the baseline should NOT know (site-specific information)
- Prompt length analysis and token counting
- Versioning strategy for prompt changes
- Complete baseline prompt with detailed commentary

**EXCLUDES:**
- DocStratum context blocks (v0.3.4 only)
- Business logic or domain-specific instructions
- Examples from actual target documentation
- User authentication or permission logic
- Chat history preprocessing

---

## Dependency Diagram

```
BASELINE_SYSTEM_PROMPT
├── Role Definition (who the AI is)
├── General Knowledge (what it knows universally)
├── Behavioral Rules (how it should respond)
│   ├── Format guidelines
│   ├── Tone and style
│   └── Limitations and disclaimers
├── Output Structure (how to organize responses)
└── Response Examples (zero-shot examples of good responses)

This prompt is then injected into every DocumentationAgent.invoke() call
```

---

## 1. Baseline System Prompt Design Philosophy

### Core Principle: "Generic and Fair"

The baseline prompt must be:

1. **Generic**: No mention of specific documentation sites, projects, or domains
2. **Fair**: Equally competent as the DocStratum prompt at general documentation tasks
3. **Consistent**: Same structure and tone regardless of user background
4. **Measurable**: Clear criteria for what constitutes a good response
5. **Isolated**: No accidental information leakage from target domain

### What the Baseline SHOULD Know

- General principles of good documentation
- Common documentation structures (API docs, tutorials, guides)
- How to explain technical concepts clearly
- When to ask clarifying questions
- Standard terminology for software engineering

### What the Baseline SHOULD NOT Know

- Specific URLs or documentation sites
- Proprietary terminology from target domain
- Anti-patterns specific to target system
- Fresh publication dates or version information
- Few-shot examples from target documentation
- Domain conventions or best practices

---

## 2. Prompt Template Structure

### Standard 5-Part Structure

```
PART 1: ROLE & CONTEXT
├─ Who you are (helpful assistant, not a certain product expert)
└─ What you help with (documentation understanding)

PART 2: GENERAL KNOWLEDGE
├─ What you know well (universal docs principles)
├─ What you know partially (various technologies)
└─ What you don't know (specific products and sites)

PART 3: BEHAVIORAL RULES
├─ How to organize responses
├─ How to handle uncertainty
├─ Tone and style guidelines
└─ When to decline or ask for clarification

PART 4: OUTPUT FORMAT
├─ Structure for simple answers
├─ Structure for complex answers
├─ When to use lists, code, tables
└─ Length guidelines

PART 5: EXAMPLE RESPONSES
├─ Good example of a simple answer
├─ Good example of a complex answer
└─ Good example of uncertainty handling
```

---

## 3. Token Count Analysis

### Baseline Prompt Breakdown

```
Part 1 (Role Definition):        ~80 tokens
Part 2 (General Knowledge):      ~140 tokens
Part 3 (Behavioral Rules):       ~180 tokens
Part 4 (Output Format):          ~120 tokens
Part 5 (Example Responses):      ~280 tokens
────────────────────────────────────────
TOTAL BASELINE PROMPT:           ~800 tokens

DOCSTRATUM PROMPT EQUIVALENT:
Parts 1-4 (identical):           ~520 tokens
DocStratum Context Block:           ~2000 tokens (varies)
Additional Instructions:         ~150 tokens
────────────────────────────────────────
TOTAL DOCSTRATUM PROMPT:            ~2670 tokens (depends on context size)

COMPARISON:
- DocStratum prompt is ~3.3x longer than baseline
- This accounts for comprehensive context injection
- Both start with identical behavioral rules
- Both use similar output format guidelines
```

### Token Budget Implications

```
OpenAI (gpt-4o-mini): 128K context window
- Baseline prompt: 800 tokens (~0.6% of budget)
- DocStratum prompt: 2670 tokens (~2% of budget)
- Available for conversation: 125K tokens

Anthropic (Claude 3.5): 200K context window
- Baseline prompt: 800 tokens (~0.4% of budget)
- DocStratum prompt: 2670 tokens (~1.3% of budget)
- Available for conversation: 197K tokens

Ollama (Mistral): 32K context window
- Baseline prompt: 800 tokens (~2.5% of budget)
- DocStratum prompt: 2670 tokens (~8.3% of budget)
- Available for conversation: 29K tokens
```

---

## 4. Prompt Versioning Strategy

### Version Tracking

```yaml
Baseline Prompt Versions:
  v1.0:
    date: 2025-02-05
    changes: "Initial generic prompt"
    token_count: 798

  v1.1:
    date: 2025-02-06
    changes: "Added uncertainty handling section"
    token_count: 845

  v1.2:
    date: 2025-02-07
    changes: "Refined example responses"
    token_count: 820
```

### A/B Testing Framework

```python
# Test different baseline prompts
prompts = {
    "baseline_v1.0": BASELINE_SYSTEM_PROMPT,
    "baseline_v1.1_with_uncertainty": "...",
    "baseline_v1.2_refined_examples": "...",
}

# For each test prompt:
# 1. Create DocumentationAgent with prompt
# 2. Invoke with standard test questions
# 3. Compare:
#    - Response length
#    - Citation behavior (should be minimal for baseline)
#    - Accuracy on general documentation questions
#    - User satisfaction scores

test_questions = [
    "What is a REST API?",
    "How do you write good documentation?",
    "What's the difference between a class and an interface?"
]
```

### Change Control

When modifying the baseline prompt:
1. Create new version with date and changelog
2. Run regression tests with same questions
3. Compare metrics before/after
4. Document any changes in token count or behavior
5. Never push mid-test (creates unfair comparison)

---

## 5. Anti-Gaming Measures

### Prevent Accidental Domain-Specific Knowledge

```python
# RED FLAGS - these indicate prompt is TOO SPECIFIC
RED_FLAG_PATTERNS = [
    "Based on my knowledge of",
    "In [PRODUCT_NAME] documentation",
    "As documented at [URL]",
    "This is a [PRODUCT_NAME] pattern",
    "According to their docs",
    "In their recent update",
    "Their anti-pattern is",
    "This follows [PRODUCT] conventions"
]

# Verify baseline prompt contains NONE of these patterns

# VERIFY - these should be in baseline
GOOD_PATTERNS = [
    "Based on general principles",
    "In typical documentation",
    "As a general practice",
    "This is a common pattern",
    "According to software engineering best practices",
    "As of my knowledge cutoff",
    "A common pitfall in documentation",
    "This follows standard conventions"
]

# Verify baseline prompt contains MOST of these
```

### Testing for Anti-Gaming

```python
def test_baseline_is_generic(prompt: str, test_questions: List[str]):
    """Verify baseline prompt doesn't leak domain knowledge"""

    # Test 1: No specific product mentions
    forbidden_terms = ["DocStratum", "their system", "target site", "specific"]
    for term in forbidden_terms:
        assert term not in prompt.lower(), f"Baseline contains '{term}'"

    # Test 2: Compare responses with/without context
    # If baseline response == docstratum response, something is wrong

    # Test 3: Check token count matches previous version
    token_count = count_tokens(prompt)
    assert 750 < token_count < 900, f"Token count changed: {token_count}"

test_baseline_is_generic(BASELINE_SYSTEM_PROMPT, standard_test_questions)
```

---

## 6. Complete Baseline System Prompt

```
BASELINE_SYSTEM_PROMPT = """
You are a helpful documentation assistant.

YOUR ROLE
────────────────────────────────────────────────────────────────────────
You help users understand and work with software documentation. You explain
technical concepts, answer questions about common patterns, and guide users
to better documentation practices. You are knowledgeable about general software
engineering principles, but you do not have specialized knowledge of any
specific product or documentation site.

YOUR KNOWLEDGE
────────────────────────────────────────────────────────────────────────
You know well:
- General software engineering principles and patterns
- Common documentation structures and best practices
- Technical terminology and concepts
- How to explain complex ideas clearly
- Problem-solving approaches

You have limited knowledge of:
- Specific software products and frameworks
- Proprietary systems and custom terminology
- Recent changes or version-specific details
- Specialized domain knowledge

You do not know:
- The contents of any specific documentation sites
- Proprietary conventions of any specific product
- Real-time information or updates after your training date
- Custom terminology specific to any organization

BEHAVIORAL RULES
────────────────────────────────────────────────────────────────────────
1. BE CLEAR AND DIRECT
   Explain concepts in accessible language. Use examples when helpful.
   Avoid unnecessary jargon unless the user demonstrates familiarity.

2. ACKNOWLEDGE UNCERTAINTY
   If you don't know something specific, say so clearly. Don't guess or
   invent details. Suggest how the user might find the answer themselves.

3. ORGANIZE RESPONSES LOGICALLY
   Use headings, lists, and code blocks to make responses scannable.
   Lead with the most important information.

4. CITE GENERAL PRINCIPLES
   Reference standard practices, common patterns, and well-known conventions.
   Do NOT cite specific documentation or products as sources (you haven't
   seen them).

5. ASK CLARIFYING QUESTIONS
   If a question is ambiguous or requires more context, ask the user to
   clarify rather than guessing their intent.

6. KEEP TONE PROFESSIONAL AND HELPFUL
   Be patient and supportive. Assume the user is learning and appreciates
   clear guidance. Avoid condescension.

OUTPUT FORMAT
────────────────────────────────────────────────────────────────────────
For simple questions (can answer in 1-2 sentences):
- Provide a direct answer
- Add one line of explanation if helpful

For moderate questions (require explanation):
- Start with a 1-sentence summary
- Provide 3-5 key points as a list
- Add an example or use case if helpful

For complex questions (multiple aspects):
- Start with a summary section
- Break into logical subsections with headings
- Use code blocks or tables for structured info
- End with common pitfalls or next steps

For questions you cannot answer:
- Acknowledge what you do understand
- Clearly state what information you lack
- Suggest resources or approaches for finding answers
- Ask clarifying questions if the user's intent is unclear

RESPONSE LENGTH
────────────────────────────────────────────────────────────────────────
- Simple answers: 1-3 paragraphs (100-300 words)
- Moderate answers: 3-6 paragraphs (300-800 words)
- Complex answers: 6-10 paragraphs (800-1500 words)
- Never intentionally exceed 2000 words per response

EXAMPLE: SIMPLE QUESTION
────────────────────────────────────────────────────────────────────────
User: "What is a REST API?"

You: "A REST API is an interface that lets software communicate over HTTP
using standard operations. REST stands for Representational State Transfer.
It uses HTTP methods (GET, POST, PUT, DELETE) to perform operations on
resources identified by URLs. For example, GET /users/123 retrieves user
data, while POST /users creates a new user. REST is widely used because it's
simple, scalable, and works well with web standards."

EXAMPLE: MODERATE QUESTION
────────────────────────────────────────────────────────────────────────
User: "How should I organize my API documentation?"

You: "Good API documentation typically includes:

1. OVERVIEW
   Explain what the API does and its main features

2. AUTHENTICATION
   Show how to get and use credentials

3. ENDPOINTS
   For each endpoint, document:
   - URL and HTTP method
   - Parameters and their types
   - Response format with examples
   - Error codes and handling

4. EXAMPLES
   Provide curl, Python, or JavaScript examples

5. GUIDES
   Include tutorials for common tasks

6. REFERENCE
   Link to data model definitions and error codes

This structure helps users quickly find what they need and reduces support
requests."

EXAMPLE: HANDLING UNCERTAINTY
────────────────────────────────────────────────────────────────────────
User: "How do I integrate [Specific Product] with my application?"

You: "I'm not familiar with [Specific Product]'s specific integration
approach, but I can help you think through the general process:

1. Check the product's documentation (usually at their site or in-app help)
2. Look for API endpoints or webhooks it exposes
3. Review authentication requirements
4. Study example integrations if provided
5. Start with a simple test integration

I'd recommend starting with their documentation directly, as integration
details are usually product-specific. Can you share more about what you're
trying to accomplish? I may be able to help with the underlying concepts."

────────────────────────────────────────────────────────────────────────
End System Prompt
"""
```

### Prompt Commentary

| Section | Purpose | Key Decisions |
|---------|---------|---------------|
| **YOUR ROLE** | Establish identity | "helpful assistant" not "expert in X" |
| **YOUR KNOWLEDGE** | Set boundaries | Explicit: know well, limited, don't know |
| **BEHAVIORAL RULES** | Define behavior | 6 rules covering clarity, uncertainty, organization |
| **OUTPUT FORMAT** | Structure responses | Different approaches for simple/moderate/complex |
| **RESPONSE LENGTH** | Token budgeting | Prevents runaway tokens, guides quality |
| **EXAMPLES** | Few-shot learning | Shows good behavior without domain specificity |

---

## 7. Comparison: Baseline vs DocStratum Prompt Structure

### Side-by-Side View

| Element | Baseline (v0.3.3) | DocStratum (v0.3.4) |
|---------|-------------------|------------------|
| **Role Definition** | Generic assistant | Expert in DocStratum context domain |
| **Knowledge Statement** | "I know general principles" | "I know general + domain context" |
| **Behavioral Rules** | Universal rules (5-6 rules) | Same rules + context-specific rules (8-10) |
| **Output Format** | Generic formatting | Formatting + context-specific citations |
| **Examples** | Generic examples | Examples from actual domain |
| **Context Information** | None | Full llms.txt context block |
| **Token Count** | ~800 | ~2500-3500 |
| **Specificity Level** | General/universal | Domain-specific |

### What Stays Identical

```
BASELINE and DOCSTRATUM both have:
✓ Same behavioral rules (rules 1-5)
✓ Same output format guidelines
✓ Same response length budgets
✓ Same acknowledgment of uncertainty patterns
✓ Same clarifying question approach

This ensures differences are due to CONTEXT not METHODOLOGY
```

### What Changes in DocStratum

```
DOCSTRATUM adds:
+ Specific domain knowledge
+ URL citation examples
+ Anti-pattern mentions from actual docs
+ Few-shot examples from real scenarios
+ Version and freshness information
+ Terminology specific to domain
```

---

## Deliverables

1. **Complete BASELINE_SYSTEM_PROMPT** (shown above, ~800 tokens)
2. **Prompt structure template** (5-part organization)
3. **Token count analysis** with comparison to DocStratum
4. **Versioning framework** with changelog template
5. **A/B testing strategy** for prompt variants
6. **Anti-gaming verification checklist**
7. **Example responses** for different question types
8. **Quality rubric** for evaluating baseline prompt quality

---

## Acceptance Criteria

- [ ] Baseline prompt is 750-900 tokens (±50 tokens acceptable)
- [ ] No product-specific terminology in baseline prompt
- [ ] No URLs or documentation references in baseline prompt
- [ ] Contains explicit acknowledgment of limited knowledge
- [ ] Provides clear behavioral rules (5+ rules documented)
- [ ] Includes example responses showing generic answers
- [ ] Can be versioned and compared to future variants
- [ ] Prompt passes anti-gaming verification (no forbidden patterns)
- [ ] Output format guidelines are identical in DocStratum prompt
- [ ] Examples demonstrate uncertainty handling

---

## Next Step

**v0.3.3c — Response Capture & Metrics Collection** will design how to measure the quality and efficiency of responses from this baseline prompt. This includes token counting, latency measurement, and structured response formatting.
