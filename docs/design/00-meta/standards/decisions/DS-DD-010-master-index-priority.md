# DS-DD-010: Master Index Priority Over Content Completeness

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DD-010 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Decision ID** | DECISION-010 |
| **Date Decided** | 2026-02-03 (v0.0.4d) |
| **Impact Area** | Validation Criteria (DS-VC-CON-009 Master Index Present; diagnostic W009), Scoring |
| **Provenance** | v0.0.4d §Differentiators and Decision Log |

## Decision

**The Master Index (Layer 1 of the 3-layer architecture) is prioritized over raw content completeness. Documentation with a clear, comprehensive Master Index achieves better LLM interaction outcomes than documentation with complete content but poor navigation structure.**

## Context

During v0.0.2 audit of real-world documentation sets, a striking pattern emerged: documentation quality (in terms of LLM usefulness) was not primarily correlated with **how much** information was present, but rather with **how well that information was organized and discoverable**.

The audit compared two documentation sets:
- **Set A**: 87% of LLM queries successfully answered (Master Index present, well-organized, ~60% of possible content)
- **Set B**: 31% of LLM queries successfully answered (No Master Index, comprehensive content ~95%, but scattered and hard to navigate)

This 56-point gap was decisive. It revealed that **navigation is more valuable than completeness**. An LLM encountering Set A's Master Index immediately understands the documentation structure and can find relevant sections efficiently. The same LLM encountering Set B's content without structure becomes overwhelmed, makes poor section selections, and fails to answer questions it could have answered with proper guidance.

This insight directly challenged the intuition that "more content is always better." It led to the 3-layer architecture (Master Index → Key Sections → Detail) and established the Master Index as the foundation of the ASoT standard.

## Alternatives Considered

| Option | Rationale For | Rationale Against |
|--------|---------------|-------------------|
| Content Completeness Priority | Try to document everything exhaustively; aim for 100% coverage of all topics | LLM gets lost in information overload; no clear entry points; even with complete content, 31% success rate in audit; increased maintenance burden; contradicts audit evidence |
| **Master Index Priority (Chosen)** | Master Index provides 20% of content but 80% of utility (per v0.0.2 audit); clear entry points enable efficient LLM navigation; reduces noise; lower maintenance burden; backed by empirical evidence (87% success rate) | Intentionally defers some detailed content; requires discipline to avoid feature creep; not intuitive to documentation authors trained in traditional completeness-first approaches |
| Balanced Approach (Both equally) | Attempts to maximize both navigation and coverage; sounds optimal | In practice, leads to neither being done well; dilutes focus; adds significant maintenance burden; audit evidence shows the tradeoff is real — must choose |
| Content-First with Optional Navigation | Prioritize complete content; add Master Index as "nice-to-have" afterward | Master Index becomes an afterthought and is often incomplete or poorly maintained; undermines its effectiveness; contradicts audit evidence showing navigation is primary |

## Rationale

The Master Index priority decision is grounded in **empirical evidence from v0.0.2 audit**. The 87% vs. 31% LLM success rate is not a minor difference — it represents a 2.8x improvement in utility. This gap was consistent across multiple documentation sets and query types, indicating a systematic advantage rather than noise.

The mechanism is clear: An LLM (or any reader) encountering the Master Index first develops a **mental model of the documentation structure**. Subsequent lookups are directed and efficient. Without the Master Index, the reader has no such model and resorts to random or greedy search strategies, which fail more often.

This principle extends beyond LLMs. Human documentation users benefit equally from clear navigation — think of how you use a textbook: you first scan the table of contents to find the chapter you need, then go to that chapter. The table of contents is more important than having every topic mentioned somewhere in the book.

Therefore, the ASoT standard treats the Master Index not as a nice feature but as a **foundational requirement**. Content can be deferred to v0.3.x, but a strong Master Index must be present from v0.1.x.

## Impact on ASoT

This decision has far-reaching implications for validation criteria and scoring:

### Validation Criteria
- **DS-VC-CON-009** (Master Index Present): Files must include a Master Index section at the top level. This is a hard requirement, not optional.
- **DS-VC-CON-011** (Master Index Completeness): The Master Index must reference all major sections. Sections that exist but are not mentioned in the Master Index are considered "orphaned" and trigger diagnostic W010.
- **DS-VC-CON-012** (Section Titles Match Master Index): Section titles in the document must exactly match references in the Master Index. Mismatches are errors (E011).

### Scoring
- **Layer 1 Weight**: The Master Index's presence and quality carry significant weight in overall documentation scores
- **Content Completeness Weight**: Complete content is scored lower than navigation quality
- **Missing Master Index Penalty**: Files without a Master Index receive substantial score reduction (currently -20 points)

### Deferred Content Handling
Files with incomplete content but strong Master Index emit informational diagnostic I009: "Content deferred; Master Index provides navigation roadmap." This signals that the documentation is under construction but well-organized.

## Constraints Imposed

1. **Master Index Mandatory**: All documentation sets must include a Master Index. Absence triggers diagnostic W009 and fails DS-VC-CON-009.
2. **Master Index First**: The Master Index must appear first in the file (after title/metadata). No preamble before the Master Index.
3. **Section Reference Format**: Master Index must use a standard format (numbered or bulleted list of section titles with optional brief descriptions).
4. **One Master Index Per Document**: Each documentation set has exactly one Master Index. Multiple indices are considered errors.
5. **Consistency Requirement**: Every top-level section referenced in the Master Index must exist in the document. Dangling references trigger validation errors (E009).
6. **No Orphaned Sections**: Every top-level section in the document must be referenced in the Master Index. Orphaned sections trigger diagnostic W010.

## Related Decisions

- **DS-DD-002** (3-Layer Architecture: Layer 1 is the Master Index, emphasizing its foundational role)
- **DS-DD-012** (Canonical section names: Master Index must reference sections by canonical names)
- **DS-DD-005** (Relationship types: Master Index enables efficient navigation of concept relationships)
- **DS-DD-016** (Severity classification: Missing Master Index is classified as warning/error per this decision)

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.3 |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
