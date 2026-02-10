# v0.2.2b: Precision Definition Writing

> Writing concept definitions optimized for machine parsing, not human readability. Each definition must be unambiguous, domain-specific, free of pronouns, and enable accurate LLM reasoning. Definitions are parsed by downstream systems and must follow strict syntactic and semantic constraints. This module transforms identified concepts from v0.2.2a into precision definitions suitable for the concept map layer.

## Objective

Create a systematic methodology for writing definitions that prioritize machine parsability over human prose elegance. Establish strict quality standards, templates for different concept types, and validation checkpoints that ensure each definition is precise enough to enable reasoning systems to make correct inferences. Enable both automated validation and human review of definition quality.

## Scope Boundaries

**IN SCOPE:**
- Definition templates for 7 concept types (feature, pattern, configuration, data structure, workflow, error type, principle)
- Machine-parsable definition syntax rules
- Pronoun elimination and disambiguation techniques
- Definition length guidelines and justification
- Domain-specific vs. generic definition comparison
- Common anti-patterns and how to avoid them
- Definition validation frameworks (automated and human review)
- Peer review workflow for definitions
- Definition testing and validation against LLMs
- 15+ worked examples across concept types

**OUT OF SCOPE:**
- Concept mining (see v0.2.2a)
- Relationship mapping (see v0.2.2c)
- Anti-pattern documentation (see v0.2.2d)
- User-facing documentation generation
- Definition translations to other languages

## Dependency Diagram

```
Concept Candidates (from v0.2.2a)
    ↓
[Concept Type Classification]
  ├─ Classify each concept (feature, pattern, config, etc.)
  └─ Determine applicable template
    ↓
[Definition Draft]
  ├─ Apply template structure
  ├─ Write specification
  ├─ Eliminate pronouns
  └─ Validate syntax
    ↓
[Quality Rubric Assessment]
  ├─ Specificity check
  ├─ Completeness check
  ├─ Disambiguation check
  └─ Machine-parseability check
    ↓
[Validation Gate]
  ├─ Automated syntax validation
  ├─ Automated length checks
  └─ Flag anomalies
    ↓
[Peer Review]
  ├─ Domain expert review
  ├─ LLM reasoning test
  └─ Acceptance or revision
    ↓
[Final Definition Bank]
  └─ Ready for relationship mapping (v0.2.2c)
```

## 1. Definition Quality Rubric

A 4-dimensional rubric ensures machine-processable definitions. Each dimension is scored 0-10.

| Dimension | Scoring Criteria | Weight | Examples |
|-----------|---|---|---|
| **Specificity** | 0=overly generic, 5=domain-aware, 10=precisely scoped with boundaries | 30% | ❌ "Something related to databases" vs ✓ "Pessimistic locking prevents concurrent modifications by acquiring exclusive locks before reading data" |
| **Completeness** | 0=missing key aspects, 5=covers main concept, 10=includes mechanics, constraints, and use cases | 30% | ❌ "Cache: a fast storage" vs ✓ "Cache: temporary high-speed data storage that reduces access latency; invalidated by updates to source data or time-based expiration" |
| **Disambiguation** | 0=ambiguous, 5=distinguishes from similar concepts, 10=explicitly contrasts with common confusions | 25% | ❌ "Token: something used for authentication" vs ✓ "Bearer Token: an opaque credential string transmitted in HTTP Authorization headers; unlike API keys, bearer tokens are short-lived and scoped to specific resources" |
| **Machine-Parseability** | 0=prose narrative, 5=structured with clear subjects/predicates, 10=syntactically validated and free of ambiguous pronouns/references | 15% | ❌ "It does X which makes things better" vs ✓ "[Concept Name]: [subject] [action] [object/result]; [constraint]" |

### Calculation

```
Raw Score = (Specificity × 0.30) + (Completeness × 0.30) +
            (Disambiguation × 0.25) + (Machine-Parseability × 0.15)

Quality Tier:
  9.0-10.0 = Tier A (Production-ready, no revision needed)
  7.0-8.9  = Tier B (Acceptable, minor revisions possible)
  5.0-6.9  = Tier C (Needs revision, significant gaps)
  3.0-4.9  = Tier D (Major rewrite required)
  0-2.9    = Tier E (Reject, start over)
```

### Example Rubric Application

**Concept:** "Connection Pooling"

**Definition:** "Connection pooling maintains a cache of pre-established database connections that are reused across multiple application requests, reducing connection overhead and improving performance by eliminating repeated connection setup costs."

**Scoring:**
- Specificity: 8/10 (Domain-specific, mentions the mechanism and benefit, but missing failure modes)
- Completeness: 7/10 (Covers what it is and why, but lacks exhaustion/timeout details)
- Disambiguation: 6/10 (Could better distinguish from other caching strategies)
- Machine-Parseability: 8/10 (Clear structure with subject-action-object pattern)

**Calculation:** (8 × 0.30) + (7 × 0.30) + (6 × 0.25) + (8 × 0.15) = 2.4 + 2.1 + 1.5 + 1.2 = **7.2 → Tier B**

**Required Revisions:** Add constraints (connection limit, idle timeout) and distinguish from request queuing.

## 2. Definition Templates by Concept Type

### 2.1 Feature Definition Template

**Use for:** Capabilities, functions, mechanisms, attributes

**Structure:**
```
[FEATURE_NAME] is [subject] that enables [capability] by [mechanism];
[constraint or tradeoff]; [common context].
```

**Rules:**
- "is" verb for definitional clarity (machine-parseable)
- Must include "enables" clause (explains purpose)
- One mechanism per definition
- Constraint is mandatory for features with limitations

**Example (Good):**
```
Lazy loading is a resource initialization pattern that defers data loading
until the resource is explicitly accessed; this reduces initial memory overhead
but increases latency on first access; commonly used for ORM relation loading.
```

**Example (Poor):**
```
Lazy loading defers loading of data in order to improve performance, which
helps a lot when you have relationships that might not be used.
```
(Issues: Pronouns "you", "which"; claims without justification; no machine structure)

---

### 2.2 Pattern Definition Template

**Use for:** Design patterns, architectures, anti-patterns, workflows

**Structure:**
```
[PATTERN_NAME] is a design approach for [domain] that [solves problem] by
[mechanism with multiple steps if needed]; [applicable context]; [tradeoff].
```

**Rules:**
- Must include problem being solved (not just the solution)
- Steps can be numbered if multi-stage
- Context must specify when pattern applies
- Tradeoff is mandatory (no pattern is universally optimal)

**Example (Good):**
```
Circuit breaker is a pattern for handling distributed failures that stops
sending requests to a failing service by monitoring error rates and switching
to an open state when failure threshold is exceeded; this prevents cascading
failures across services; tradeoff: introduces latency due to state transitions
and requires fallback behavior definition.
```

---

### 2.3 Configuration Definition Template

**Use for:** Settings, parameters, tuning variables, deployment options

**Structure:**
```
[CONFIG_NAME] is a parameter that controls [aspect] with values [type/range];
default is [value]; impacts [measurable consequence]; common values are [examples].
```

**Rules:**
- Must specify value type (integer, boolean, string, duration, etc.)
- Default value is mandatory if one exists
- Must describe measurable impact (not vague "performance")
- Examples must be realistic, not theoretical

**Example (Good):**
```
max_pool_size is a configuration parameter that controls the maximum number
of concurrent database connections in the pool; value is integer >= 1; default
is 10; impacts maximum request concurrency and memory usage; setting too low
causes request queuing, setting too high causes connection exhaustion on the
database server; common values: 5 (low concurrency), 10 (typical web app),
50+ (high-traffic services).
```

---

### 2.4 Data Structure Definition Template

**Use for:** Data formats, object types, data models, schemas

**Structure:**
```
[STRUCTURE_NAME] is a data representation for [domain] containing [key fields]
with [mutability/constraints]; serialized as [format]; [performance/constraint
characteristic].
```

**Rules:**
- Must list key fields (at least 3-5)
- Must specify mutability (immutable, append-only, mutable, etc.)
- Serialization format mandatory (JSON, protobuf, binary, etc.)
- Must include size/performance implications if relevant

**Example (Good):**
```
Bearer Token is a credential data structure containing: token string (opaque),
expiration timestamp, scopes list, subject identifier; immutable once issued;
serialized as JWT or opaque reference depending on implementation; typical size
500-2000 bytes; subject to revocation before expiration.
```

---

### 2.5 Workflow Definition Template

**Use for:** Processes, algorithms, sequences, state machines

**Structure:**
```
[WORKFLOW_NAME] is a [n-step] process for [goal] that proceeds as follows:
1) [step]; 2) [step]; ... n) [step]; pre-condition: [required state];
post-condition: [resulting state]; failure mode: [what goes wrong].
```

**Rules:**
- Must be numbered steps (enables machine parsing)
- Each step must be atomic (not "do several things")
- Pre/post conditions mandatory
- Failure mode mandatory (how does this break?)

**Example (Good):**
```
Authorization code flow is a 4-step OAuth 2.0 process for obtaining access
tokens from a resource server: 1) Client redirects user to authorization endpoint
with client_id and redirect_uri; 2) Resource owner authenticates and grants
consent; 3) Authorization server redirects back to client with authorization_code;
4) Client exchanges authorization_code for access_token by calling token endpoint
with client_secret; pre-condition: client is registered; post-condition: client
has valid access_token; failure mode: user denies consent or authorization_code
expires before exchange.
```

---

### 2.6 Error Type Definition Template

**Use for:** Exceptions, error codes, failure modes, edge cases

**Structure:**
```
[ERROR_NAME] is raised when [trigger condition]; indicates [semantic meaning];
client action: [recommended response]; root causes: [list of conditions that
cause this]; contrasts with: [related errors].
```

**Rules:**
- Trigger condition must be specific (not "something goes wrong")
- Must specify actionable client response (not just "handle it")
- Root causes are multiple possible conditions
- Must distinguish from similar errors

**Example (Good):**
```
ConnectionPoolExhausted is raised when the application attempts to acquire a
connection from the pool but all connections are in use and no new connections
can be created because the pool size limit has been reached; indicates that the
application is under load exceeding configured concurrency capacity; client action:
implement exponential backoff retry or reject incoming requests with HTTP 503
Service Unavailable; root causes: (1) max_pool_size too low for current traffic,
(2) slow database queries holding connections too long, (3) connection leak from
unclosed resources; contrasts with: ConnectTimeout (network layer failure) and
ConnectionTimeoutException (acquired but then times out).
```

---

### 2.7 Principle/Concept Definition Template

**Use for:** Guidelines, requirements, theoretical concepts, properties

**Structure:**
```
[PRINCIPLE_NAME] is the requirement that [property must hold] in [domain/context];
achieved through [mechanisms]; violation indicates [consequence]; related to:
[connected principles].
```

**Rules:**
- Must be a property/requirement, not a suggestion
- Mechanisms are HOW it's achieved (not what it is)
- Violation consequence must be concrete
- Related principles for graph context

**Example (Good):**
```
Idempotency is the requirement that repeating the same operation produces
identical results regardless of how many times the operation is executed;
achieved through: (1) operations that don't change state on repeat execution
(side-effect free), or (2) operations that are explicitly tracked to detect
and suppress duplicates; violation indicates non-deterministic behavior and
broken distributed systems; related to: atomicity, durability, exactly-once semantics.
```

## 3. The "No Pronouns" Rule with Before/After Examples

Pronouns are ambiguous for machine parsing. Pronouns must be replaced with explicit references.

### Pronoun Elimination Rules

| Pronoun Type | Pattern | Replacement | Example |
|--------------|---------|-----------|---------|
| **he/she/it** | Subject unclear | Use concept name or "the [noun]" | ❌ "It enables X" → ✓ "Cache invalidation enables X" |
| **their/his/her** | Possessive unclear | Use [Concept]'s or "of [noun]" | ❌ "...when their timeout expires" → ✓ "...when the idle connection timeout expires" |
| **which/that** | Antecedent clause references | Use relative clause with explicit subject | ❌ "Connection pooling, which improves..." → ✓ "Connection pooling improves..." (remove relative clause or restructure) |
| **they/them** | Multiple referents | Specify plural clearly | ❌ "Transactions use locks; they prevent..." → ✓ "Transactions use locks; locks prevent..." |
| **this/that** | Demonstrative vague | Use specific noun phrase | ❌ "This requires care" → ✓ "Connection leak prevention requires care" |

### 8 Detailed Before/After Examples

**Example 1: Subject Pronoun "it"**
```
BEFORE:
"Lazy loading is a technique where it defers the loading of data until it is
explicitly accessed, which makes it faster initially."

ISSUES:
- "it defers" - unclear what defers
- "it is explicitly accessed" - unclear what is accessed
- "it faster" - unclear what becomes faster
- "which makes" - unclear antecedent

AFTER:
"Lazy loading is a technique that defers data loading until the data is
explicitly accessed; this reduces initial memory allocation overhead and
startup time."

FIXES:
- Removed ambiguous "it" by restructuring as "technique that defers..."
- Explicit "data loading" and "data is accessed"
- Replaced vague "faster" with specific "reduces initial memory allocation"
- Removed "which makes" relative clause
```

---

**Example 2: Possessive Pronoun "their"**
```
BEFORE:
"When services fail, their dependencies should implement retry logic because
they need to handle the transient failures properly."

ISSUES:
- "their dependencies" - whose dependencies?
- "they need" - who needs?
- Vague "handle properly"

AFTER:
"When a service fails, dependent services should implement retry logic to
distinguish transient failures (network hiccup) from permanent failures (service down)."

FIXES:
- "their dependencies" → "dependent services" (explicit role)
- "they need" → removed (restructured to indicate why)
- "handle properly" → specific distinction between transient and permanent
```

---

**Example 3: Relative Pronoun "which"**
```
BEFORE:
"Optimistic locking uses version numbers to detect concurrent modifications,
which is less resource-intensive than pessimistic locking."

ISSUES:
- "which is" - unclear what property "which" refers to
- Could refer to "version numbers" or "detect concurrent modifications"

AFTER:
"Optimistic locking uses version numbers to detect concurrent modifications
after they occur; this approach consumes fewer lock resources than pessimistic
locking but requires retry logic for conflicting transactions."

FIXES:
- Removed "which is" and separated clauses
- Made the comparison explicit with specific differences
- Added what's different about the resource consumption
```

---

**Example 4: Demonstrative "this/that"**
```
BEFORE:
"Connection pooling manages a cache of connections. This is important because
it reduces overhead."

ISSUES:
- "This" - refers to entire previous sentence, ambiguous for machines
- "it reduces" - unclear what reduces what

AFTER:
"Connection pooling manages a cache of pre-established database connections
that are reused across requests, reducing connection initialization overhead."

FIXES:
- Eliminated demonstrative by combining into single sentence
- "it reduces" → "reducing" (participle makes subject clear)
- Added specificity: "pre-established" and "across requests"
```

---

**Example 5: Plural Pronoun "they"**
```
BEFORE:
"Transactions provide ACID properties. They ensure data consistency because
they prevent concurrent corruption."

ISSUES:
- First "they" = transactions or ACID properties?
- Second "they" = same antecedent as first?
- "prevent concurrent corruption" is vague

AFTER:
"Transactions ensure ACID properties (Atomicity, Consistency, Isolation, Durability)
by executing as all-or-nothing operations that prevent concurrent modifications
from producing inconsistent data states."

FIXES:
- Removed plural "they" by restructuring with clear causality
- Explicit what "they" (transactions) do
- Specific "prevent concurrent modifications" instead of "prevent corruption"
```

---

**Example 6: Ambiguous "it" in Technical Context**
```
BEFORE:
"Caching improves performance by storing data locally. It works because it
reduces network trips. However, it becomes stale if it is not refreshed."

ISSUES:
- Four instances of "it" with multiple possible referents
- "becomes stale" lacks specificity
- "not refreshed" is passive

AFTER:
"Caching improves performance by storing frequently-accessed data locally,
reducing network latency from repeated remote fetches; cached data becomes
inconsistent with source data if invalidation does not occur before source
data modification."

FIXES:
- "it" subjects → removed or made explicit
- "becomes stale" → "becomes inconsistent with source data"
- "not refreshed" → "invalidation does not occur before modification"
```

---

**Example 7: "this" without Clear Antecedent**
```
BEFORE:
"Implementing distributed consensus is complex. This is why most systems use
alternative approaches instead of implementing it from scratch."

ISSUES:
- "This is why" - unclear what "this" refers to (complexity? implementing? both?)
- "it from scratch" - unclear what "it" refers to

AFTER:
"Distributed consensus algorithms are computationally complex; therefore, most
systems rely on proven implementations (Raft, Paxos) rather than building consensus
from first principles."

FIXES:
- Removed "This is why" construction
- Explicit: "because distributed consensus is complex"
- "it from scratch" → "building consensus from first principles"
```

---

**Example 8: Mixed Pronoun Confusion**
```
BEFORE:
"Rate limiting protects services from overload. When they exceed the limit,
it rejects extra requests. This prevents them from being overwhelmed. However,
it can cause client errors if it is not configured carefully."

ISSUES:
- "they exceed" - services or requests?
- "it rejects" - what is "it"?
- "them from being overwhelmed" - what are "them"?
- "it can cause" - what causes?
- "it is not configured" - what should be configured?

AFTER:
"Rate limiting protects services from overload by rejecting requests that exceed
configured throughput thresholds; this prevents server resource exhaustion and
cascading failures; rate limit thresholds must be configured based on service
capacity to avoid rejecting legitimate traffic during traffic spikes."

FIXES:
- Explicit subjects: "Rate limiting protects", "by rejecting requests"
- Clear what triggers rejection: "exceed configured throughput thresholds"
- "them from being overwhelmed" → "prevents server resource exhaustion"
- Restructured final clause to be explicit about configuration impact
```

## 4. Definition Length Guidelines

### Why One Sentence Is Ideal

One sentence ensures:
1. **Machine parsability**: Single semantic unit (subject-verb-object structure)
2. **Unambiguous references**: No pronouns across sentence boundaries
3. **Concept isolation**: Definition focuses on ONE concept, not related concepts
4. **Cognitive load**: LLMs process single sentences with less hallucination risk

**Maximum 1 sentence** for:
- Simple concepts (feature flags, tokens, basic configurations)
- Concepts with dedicated relationship mapping (relationships in v0.2.2c)
- Concepts that are primarily definitional (no complex mechanisms)

### When Two Sentences Are Acceptable

Two sentences permitted **only** when:
1. First sentence: Definition and primary purpose
2. Second sentence: Constraint, tradeoff, or critical context

**Two-sentence structure:**
```
[Sentence 1]: [CONCEPT] is [definition]; [primary mechanism or purpose].
[Sentence 2]: [Constraint/Tradeoff/Critical context]; [impact or consequence].
```

**Example (Good):**
```
Connection pooling maintains a cache of pre-established database connections
reused across application requests, reducing connection overhead and initialization
latency. Connection exhaustion occurs when all pooled connections are in use and
connection limit is reached, requiring exponential backoff or request rejection.
```

**Maximum 2 sentences** for:
- Concepts with significant tradeoffs or constraints
- Concepts that have common failure modes needing documentation
- Workflow concepts describing sequential steps (can use numbered sub-steps within second sentence)

### When Three+ Sentences Are Required

Reject the definition and require rewrite. If concept genuinely requires 3+ sentences:
- **Split into multiple concepts** (parent concept + child concepts)
- **Use relationship mapping** instead (see v0.2.2c)
- **Move detailed mechanics to anti-patterns** (see v0.2.2d)

**Example of improper 3-sentence definition:**
```
REJECT THIS:
"OAuth 2.0 is an authorization framework... The authorization code flow is...
Client credentials flow is different because..."

CORRECT APPROACH:
Define OAuth 2.0 in 1 sentence.
Define Authorization Code Flow as separate concept in 1 sentence.
Define Client Credentials Flow as separate concept in 1 sentence.
Map relationships: OAuth 2.0 → implements {Authorization Code Flow, Client Credentials Flow}
```

## 5. Domain-Specific vs. Generic Definitions

Definitions must be domain-specific. Generic definitions fail to enable correct LLM reasoning in domain context.

### Comparison Table

| Aspect | Generic Definition | Domain-Specific Definition | Impact |
|--------|---|---|---|
| **Vocabulary** | Uses common English words | Uses domain terminology | LLM can map to related domain concepts |
| **Context** | Applies anywhere | Applies in specific context | LLM doesn't overgeneralize to irrelevant contexts |
| **Constraints** | None or universal | Domain-specific constraints | LLM knows when definition doesn't apply |
| **Related Terms** | Doesn't reference related concepts | References domain neighbors | LLM can navigate concept graph |
| **Mechanism** | Vague or theoretical | Concrete to domain | LLM can reason about "why" not just "what" |

### Detailed Examples

**Example 1: Cache (Generic vs. Domain-Specific)**

```
GENERIC (POOR):
"Cache: a thing that stores data for quick access."
  - Problem: Could apply to anything (RAM, disk, browser cache, human memory)
  - Missing: What data? In what domain? What's the speed characteristic?
  - LLM Impact: Might confuse cache with buffer, temporary file, or memoization

DOMAIN-SPECIFIC (GOOD):
"Cache (in database systems): a fast-access memory layer that stores frequently-accessed
data to avoid repeated disk I/O; invalidated when source data changes or after configurable
time-to-live expiration."
  - Context: "in database systems" clarifies scope
  - Specific: "fast-access memory layer", "disk I/O" (domain context)
  - Constraint: "invalidated when source data changes" (domain-specific invalidation rule)
  - LLM can reason: why caches matter (I/O cost), when they break (staleness)
```

---

**Example 2: Token (Generic vs. Domain-Specific)**

```
GENERIC (POOR):
"Token: something that represents something else."
  - Missing: Which domain? In what context? What does it represent?
  - Could mean: game token, transit token, authentication token, parsing token, etc.

DOMAIN-SPECIFIC (GOOD):
"Bearer Token (in OAuth 2.0 and HTTP authentication): an opaque credential string
transmitted in HTTP Authorization headers with format 'Authorization: Bearer <token>';
subject to expiration and revocation; compared to API keys, bearer tokens are short-lived
and scoped to specific resources."
  - Context: "in OAuth 2.0 and HTTP authentication"
  - Specific: "opaque credential string", "transmitted in HTTP Authorization headers"
  - Format: "Authorization: Bearer <token>" (concrete, parseable format)
  - Constraint: "subject to expiration and revocation"
  - Disambiguation: Contrasts with API keys (common confusion)
```

---

**Example 3: Lock (Generic vs. Domain-Specific)**

```
GENERIC (POOR):
"Lock: prevents something from being accessed."

DOMAIN-SPECIFIC (GOOD):
"Lock (in database concurrency control): a mechanism that grants exclusive or shared
access to a resource, preventing concurrent modifications when exclusive lock is held;
deadlock occurs when multiple transactions hold locks in circular dependency; implemented
via lock manager or optimistic version-checking in different isolation levels."
  - Domain: "in database concurrency control"
  - Types: "exclusive or shared" (concurrency-specific)
  - Problem it solves: "preventing concurrent modifications"
  - Failure mode: "deadlock occurs when..." (domain-specific failure)
  - Implementation variants: "lock manager or optimistic version-checking"
  - Relationship: "in different isolation levels" (links to related concept)
```

## 6. Common Definition Anti-Patterns

### Anti-Pattern 1: Circular Definitions

**Pattern:** Definition of A references B, definition of B references A, or A is defined in terms of itself.

```
CIRCULAR (REJECT):
"Authentication: the process of verifying that the user is authenticated."
"Identifier: something that identifies something."

FIX:
"Authentication: the process of verifying that a claimed identity matches
known credentials (password, certificate, token) via cryptographic or other
verification mechanisms."

"Identifier: a unique reference (name, number, URI, UUID) that distinguishes
one entity from others in a given domain."
```

### Anti-Pattern 2: Vague Definitions

**Pattern:** Definition uses imprecise qualifiers (very, often, usually, many, some, things, stuff).

```
VAGUE (REJECT):
"Caching: storing some data in a fast place to make things faster."
"Timeout: when things take too long and you have to stop waiting."

FIX:
"Caching: storing frequently-accessed data in fast-access memory (RAM) to
reduce latency of repeated requests; cache hit: requested data is in cache;
cache miss: requested data is not in cache."

"Timeout: a maximum duration threshold beyond which an in-progress operation
is forcibly terminated; exceeded timeout indicates operation failure and
triggers error handling or retry logic."
```

### Anti-Pattern 3: Over-Inclusive Definitions

**Pattern:** Definition is so broad it applies to many unrelated concepts.

```
OVER-INCLUSIVE (REJECT):
"Performance: a measure of how well something works."
  - Applies to: humans, cars, databases, algorithms, organizations, everything

FIX (separate domain-specific definitions):
"Performance (in database systems): the measurable latency and throughput of
query execution; measured via response time, queries-per-second (QPS), and
percentile latency (p50, p99)."

"Performance (in network systems): the measurable throughput (Mbps) and latency
(milliseconds) of data transmission; impacted by bandwidth, packet loss, and
buffering."
```

### Anti-Pattern 4: Definition by Etymology

**Pattern:** Explains word origin instead of domain concept.

```
ETYMOLOGY-ONLY (REJECT):
"Cache: comes from French 'cacher' meaning to hide."
"Mutex: abbreviation of 'mutual exclusion'."

FIX:
"Cache: a fast-access memory layer that stores copies of frequently-accessed
data to reduce latency of repeated requests from slower storage."

"Mutex: a synchronization primitive that ensures only one thread can execute
protected code at a time, preventing race conditions in multi-threaded access
to shared resources."
```

### Anti-Pattern 5: Definitional Chain

**Pattern:** Definition assumes reader knows other undefined terms.

```
CHAIN (REJECT):
"Optimistic locking: uses version vectors to detect conflicts in MVCC systems."
  - Assumes knowledge of: version vectors, MVCC, conflicts (undefined)

FIX:
"Optimistic locking: a concurrency control approach that allows concurrent
reads without holding locks; detects write conflicts using version numbers,
and retries transactions that conflict with concurrent modifications."
  - Explicit: what it allows (concurrent reads)
  - Explicit: how it detects (version numbers)
  - Explicit: consequence (retries on conflict)
```

### Anti-Pattern 6: Negative-Only Definition

**Pattern:** Defines by what it is NOT, without saying what it IS.

```
NEGATIVE (REJECT):
"Asynchronous: not synchronous."
"Non-blocking: not blocking."

FIX:
"Asynchronous operation: an operation that returns control to the caller
before execution completes; completion is signaled via callback, promise,
or future; contrasted with synchronous operation which blocks caller until
completion."

"Non-blocking I/O: input/output operations that return immediately with
partial data or status, allowing the calling thread to continue execution;
contrasted with blocking I/O which suspends the calling thread until
operation completes."
```

### Anti-Pattern 7: Example-Based Definition

**Pattern:** Defines by example only, without the actual definition.

```
EXAMPLE-ONLY (REJECT):
"Cache: like a browser cache storing web pages, or a database cache storing
query results."
  - No actual definition of what caching is or why it works

FIX:
"Cache: a fast-access memory layer that stores copies of frequently-accessed
data to reduce latency and I/O load; examples include browser HTTP caches
(storing web pages), database caches (storing query results), and CPU caches
(storing memory values)."
```

### Anti-Pattern 8: Subjective Definition

**Pattern:** Includes opinions or subjective qualities instead of objective facts.

```
SUBJECTIVE (REJECT):
"A well-designed API is one that is easy to use and makes developers happy."
"NoSQL databases are great because they are flexible."

FIX:
"API design principle: interfaces should minimize required parameters, use
consistent naming conventions, and provide clear error messages; enables
developers to correctly use the API without extensive documentation."

"NoSQL database: a database management system that uses flexible schema models
(document, key-value, graph) instead of fixed relational schemas; enables
schema evolution without migration operations."
```

## 7. Definition Validation Checklist

Every definition must pass this checklist before peer review.

### Automated Checks (via script)

```python
def validate_definition(concept_name: str, definition: str) -> dict:
    """Automated validation of definition quality."""
    issues = []

    # Check 1: Length (1-2 sentences)
    sentences = definition.split(';')
    if len(sentences) > 3:
        issues.append("❌ TOO LONG: More than 2 sentences")

    # Check 2: Pronoun detection
    pronouns = ['it ', 'it,', 'they ', 'they,', 'them ', 'their ', 'this ', 'that ']
    for pronoun in pronouns:
        if pronoun.lower() in definition.lower():
            issues.append(f"⚠️  PRONOUN: Contains '{pronoun.strip()}'")

    # Check 3: Vague qualifiers
    vague = ['very', 'often', 'usually', 'many', 'some', 'stuff', 'things', 'basically']
    for word in vague:
        if word in definition.lower():
            issues.append(f"⚠️  VAGUE: Contains '{word}'")

    # Check 4: Passive voice (problematic for machine parsing)
    passive_indicators = [' is done', ' is created', ' is made', ' is taken']
    for indicator in passive_indicators:
        if indicator in definition.lower():
            issues.append(f"⚠️  PASSIVE: Consider active voice instead")

    # Check 5: Domain specificity (should reference domain-specific terms)
    if len(definition.split()) < 15:
        issues.append("⚠️  SHORT: Definition may lack domain specificity (< 15 words)")

    # Check 6: Definition must start with concept name or related term
    if not definition.startswith(concept_name) and concept_name not in definition[:50]:
        issues.append("⚠️  CLARITY: Definition should reference the concept early")

    # Check 7: Must include constraint or context
    constraint_words = [';', 'when', 'if', 'constraint', 'requires', 'assumes']
    has_constraint = any(word in definition for word in constraint_words)
    if not has_constraint:
        issues.append("⚠️  CONSTRAINT: Consider adding constraint or context")

    return {
        'concept': concept_name,
        'validation_passed': len(issues) == 0,
        'issues': issues,
        'word_count': len(definition.split()),
        'sentence_count': len(definition.split(';'))
    }

# Example usage
result = validate_definition(
    "Connection Pooling",
    "Connection pooling maintains a cache of pre-established connections reused "
    "across requests; this reduces connection initialization overhead and latency."
)
print(f"Valid: {result['validation_passed']}")
for issue in result['issues']:
    print(f"  {issue}")
```

### Manual Checks (by domain expert)

- [ ] **Domain Accuracy**: Definition is correct for this domain (expert judgment)
- [ ] **No Jargon Overload**: Uses technical terms but defines unusual ones
- [ ] **Machine Testable**: Can ask an LLM "is X true of this concept?" and get consistent answer
- [ ] **Contrast Quality**: If definition references similar concept, distinction is clear
- [ ] **Completeness**: Includes HOW/WHY not just WHAT
- [ ] **No Contradiction**: Doesn't conflict with other definitions in domain
- [ ] **Logical Structure**: Subject-Verb-Object structure is clear
- [ ] **Constraint Justified**: If constraints are mentioned, they're explained as to why

## 8. Definition Peer Review Process

### Review Workflow

```
Definition Draft
    ↓
[Automated Validation Script]
  ├─ All checks pass? → Proceed to expert review
  └─ Checks fail? → Return to writer with issues
    ↓
[Expert Domain Review]
  ├─ Is definition accurate?
  ├─ Does it match domain practice?
  ├─ Does it distinguish from related concepts?
  └─ Is anything ambiguous?
    ↓
[LLM Reasoning Test] (optional but recommended)
  ├─ Ask LLM: "Based on this definition, is X true?"
  ├─ Compare answer to expert expectation
  └─ If LLM misinterprets, clarify definition
    ↓
[Approval or Revision]
  ├─ Approved: Definition accepted
  └─ Revision needed: Return to writer with feedback
```

### Review Comments Template

```
Definition under review: [CONCEPT_NAME]

Automated validation: [PASS/FAIL with specific issues if any]

Expert review:
- Accuracy: [Correct/Incorrect/Minor issue] - [explanation]
- Domain specificity: [Too generic/Appropriate/Too narrow]
- Clarity: [Clear/Ambiguous - point out ambiguity]
- Completeness: [Complete/Missing aspect: ___]
- Distinction: [Clear from related concepts/Could be confused with ___]

LLM reasoning test (if performed):
- Test query: [What did we ask the LLM?]
- LLM response: [What did it answer?]
- Expected: [What should it have answered?]
- Verdict: [Correct/Incorrect interpretation]

Recommendation: [APPROVE / REQUEST REVISION / REJECT]

If revision requested:
- Specific changes needed: [...]
- Rationale: [...]
```

## 9. Fifteen Example Definitions Across Concept Types

### Feature Examples

**Example 1: Lazy Loading (Feature)**
```
Lazy loading is a resource initialization technique that defers loading
until the resource is explicitly accessed; this reduces initial memory overhead
and startup latency at the cost of increased latency on first access.
```

**Example 2: Caching (Feature)**
```
Caching is a technique that stores copies of frequently-accessed data in
fast-access memory (RAM) to reduce latency of repeated access; cache
invalidation occurs when source data changes, requiring removal of stale copies
to maintain consistency.
```

### Pattern Examples

**Example 3: Circuit Breaker Pattern**
```
Circuit breaker is a pattern for distributed systems that stops sending requests
to a failing service by monitoring error rates and opening the circuit when failure
threshold is exceeded (typically 50% error rate over 10 requests); transitions to
half-open state after timeout to attempt recovery; reduces cascading failures
across service dependencies.
```

**Example 4: Eventual Consistency Pattern**
```
Eventual consistency is a pattern for distributed systems accepting temporary
data inconsistency across replicas to improve availability and partition tolerance;
all replicas eventually converge to identical state after writes cease, distinguished
from strong consistency which guarantees immediate identical state across all replicas.
```

### Configuration Examples

**Example 5: max_pool_size**
```
max_pool_size is an integer parameter (minimum 1) controlling the maximum
number of concurrent database connections in the pool; default is 10; impacts
maximum request concurrency and memory overhead; values too low cause request
queuing, values too high cause connection exhaustion on database server; typical
ranges: 5 (low traffic), 10-20 (standard web application), 50+ (high-traffic services).
```

**Example 6: idle_connection_timeout**
```
idle_connection_timeout is a duration parameter (format: seconds or milliseconds)
controlling how long a connection can remain unused in the pool before automatic
closure; default is 300 seconds; values too low cause frequent reconnection overhead,
values too high cause resource exhaustion if clients disappear; typical range:
300-900 seconds.
```

### Data Structure Examples

**Example 7: Bearer Token**
```
Bearer token is an opaque credential string transmitted in HTTP Authorization
header with format 'Authorization: Bearer <token>'; contains: token string,
expiration timestamp, scopes list, subject identifier; immutable once issued;
subject to revocation and expiration; typically 500-2000 bytes when JWT-encoded.
```

**Example 8: Transaction Record**
```
Transaction record is an immutable data structure containing: unique transaction ID,
start timestamp, end timestamp, isolation level, read set (resources read),
write set (resources modified), commit status (pending/committed/aborted); size
varies 100-10000 bytes depending on operation complexity; enables ACID guarantees
through serialization of concurrent operations.
```

### Workflow Examples

**Example 9: OAuth 2.0 Authorization Code Flow**
```
Authorization code flow is a 4-step OAuth 2.0 workflow: 1) Client redirects user
to authorization endpoint with client_id, redirect_uri, and scopes; 2) Resource
owner authenticates and grants consent; 3) Authorization server redirects to
redirect_uri with authorization_code (expires in 10 minutes); 4) Client exchanges
authorization_code for access_token by calling token endpoint with client_secret;
designed for server-side applications where client can securely store client_secret.
```

**Example 10: Connection Pool Acquisition Workflow**
```
Connection pool acquisition is a 3-step workflow: 1) Application calls pool.getConnection();
2a) If idle connection exists, return immediately, or 2b) If pool below max_pool_size,
create new connection and return, or 2c) If pool at max, wait for available connection
(timeout configurable); 3) Application uses connection and calls close() to return
to pool; failure mode: timeout if no connection becomes available within timeout interval.
```

### Error Type Examples

**Example 11: ConnectionPoolExhausted**
```
ConnectionPoolExhausted is raised when the application attempts to acquire a
connection but the pool has exhausted all available connections (all in-use and
pool size at maximum); indicates application request rate exceeds configured
concurrency capacity; client action: implement exponential backoff retry (2s, 4s, 8s),
increase max_pool_size, or reject incoming requests with HTTP 503 Service Unavailable;
root causes: (1) max_pool_size too low, (2) slow database queries holding connections,
(3) connection leak from unclosed resources.
```

**Example 12: StaleDataError**
```
StaleDataError is raised when cached data is accessed but source data has been
modified since cache creation; indicates cache invalidation failure; client action:
implement cache refresh by calling invalidate() or wait for time-based expiration;
distinguish from CacheHit (data matches source) and CacheMiss (data not in cache);
root causes: (1) cache TTL too long, (2) invalidation mechanism not triggered,
(3) concurrent modification not propagated to all caches.
```

### Principle/Concept Examples

**Example 13: Idempotency**
```
Idempotency is the requirement that repeating the same operation produces identical
results regardless of execution count; achieved via: (1) stateless operations without
side effects, or (2) operations tracked to detect and suppress duplicate execution;
violation enables non-deterministic behavior and broken distributed transactions;
critical for network retries where operation may execute multiple times.
```

**Example 14: ACID Properties**
```
ACID properties are the set of four requirements guaranteeing reliable transactions:
Atomicity (all-or-nothing execution), Consistency (valid state transitions), Isolation
(no interference between concurrent transactions), Durability (committed data survives
failures); tradeoff: ACID guarantees limit concurrency and performance compared to
weaker consistency models.
```

**Example 15: CAP Theorem**
```
CAP theorem is the principle that distributed systems can guarantee at most two
of three properties: Consistency (all replicas identical), Availability (all nodes
respond), Partition tolerance (system functions despite network partitions); real
systems must choose CP or AP since network partitions happen; examples: relational
databases choose CP (availability limited), NoSQL databases often choose AP (eventual
consistency).
```

## Deliverables Checklist

- [ ] **Definition Quality Rubric**: Documented 4-dimensional scoring system
- [ ] **7 Definition Templates**: With structure, rules, and examples for each concept type
- [ ] **Pronoun Elimination Guide**: 8 before/after examples with detailed fixes
- [ ] **Length Guidelines Document**: Justification for 1-2 sentence limits
- [ ] **Anti-Pattern Reference**: 8 documented anti-patterns with examples
- [ ] **Validation Script**: Automated checker for definition quality
- [ ] **Peer Review Process**: Documented workflow with review template
- [ ] **Complete Definition Bank**: 50+ definitions for Tier 0 and Tier 1 concepts
- [ ] **Validation Report**: Statistics on definition quality scores

## Acceptance Criteria

1. **100% Machine Parsable**: Zero pronouns or ambiguous references in Tier A definitions
2. **Domain Accuracy**: ≥95% of definitions approved by domain experts
3. **Length Compliance**: 100% of Tier A definitions are 1 sentence; Tier B definitions justify 2 sentences
4. **No Anti-Patterns**: Automated check shows zero instances of circular, vague, or over-inclusive definitions
5. **LLM Reasoning Accuracy**: LLM correctly answers 90%+ of test questions based on definitions
6. **Consistency**: Same concept used consistently across all definitions (no terminology variation)
7. **Completeness**: All Tier 0 and Tier 1 concepts have definitions
8. **Peer Review**: 100% of definitions reviewed and approved before acceptance

## Next Steps

Once definitions are validated and peer-reviewed, proceed to **v0.2.2c: Relationship Mapping & Dependency Graphs** to establish connections between concepts and create the concept map layer.
