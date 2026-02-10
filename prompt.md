You are implementing a specific version spec for the DocStratum project — a **validation engine and semantic enrichment layer** for llms.txt files. DocStratum does NOT generate llms.txt files; it validates, scores, and enriches existing ones.

## Your Assignment

**Target spec:** `__SPEC_PATH__`
<!-- Example: docs/design/02-foundation/RR-SPEC-v0.1.2a-diagnostic-infrastructure.md -->

Read the target spec thoroughly before writing any code. If the target has sub-parts (a, b, c, d), read them ALL first.

## Mandatory Pre-Reading

Before writing any code, read these documents **in this order**:

1. **The target spec** (and all its sub-parts if they exist)
2. **The parent spec** (linked in the target's `> Parent:` header line)
3. **Research artifacts referenced by the spec** (listed in its `> Traces to:` header line or Traceability Appendix). Key research documents live in `docs/design/01-research/`:
   - `RR-SPEC-v0.0.x-consolidated-research-synthesis.md` — 8 key findings, 16 design decisions, master traceability
   - `RR-SPEC-v0.0.5-summary.md` — 68 FRs, 21 NFRs, 6 constraints
   - `RR-SPEC-v0.0.4d-rosetta-root-differentiators-and-decision-log.md` — DECISION-001 through DECISION-016
4. **Engineering standards** in `docs/design/00-meta/`:
   - `RR-META-testing-standards.md` — pytest, AAA pattern, naming (`test_{method}_{scenario}_{result}`), per-module coverage targets
   - `RR-META-logging-standards.md` — stdlib `logging` only, `%s` formatting, level contract, no `print()` in `src/`
   - `RR-META-commenting-standards.md` — Google-style docstrings, type hints on all public signatures, TODO format: `# TODO (vX.Y.Z): description`
   - `RR-META-documentation-requirements.md` — CHANGELOG format, terminology table, writing style
   - `RR-META-development-workflow.md` — commit format, self-review checklist, phase transition rules

## Project Context

- Design specs live in `docs/design/`, organized by phase (`00-meta` through `06-testing`)
- Spec filenames follow: `RR-SPEC-v{X}.{Y}.{Z}-{slug}.md` (versions) and `RR-SPEC-v{X}.{Y}.{Z}{letter}-{slug}.md` (sub-parts)
- The project was realigned during the v0.0.x research phase from a "generation" approach to a **validation engine** pivot — see v0.1.0 §The Pivot for context
- Some specs predate the pivot (v0.2.x–v0.6.x) and have NOT yet been realigned — treat their content with caution and flag any conflicts with the realigned v0.1.x specs
- The tech stack per phase is documented in v0.1.0 §Tech Stack. **Foundation phase (v0.1.x)** uses: Python 3.11+, Pydantic ≥2.0, PyYAML ≥6.0, mistletoe ≥1.3, pytest ≥8.0, black, ruff, python-dotenv. Do not add dependencies without asking.

## Rules

### Scope — No Fabrication

1. **Only implement what the spec describes.** Do not add features, modules, utilities, or abstractions not explicitly documented in the target spec. If it's not in a spec, it doesn't exist.
2. **Do not pull work forward from future versions.** If the spec references a capability delivered later (e.g., "v0.2.4 will implement detection logic"), acknowledge it in a TODO comment but do not implement it.
3. **If the spec is ambiguous, ask me.** Do not guess or interpret liberally. Flag the ambiguity, quote the conflicting or unclear passage, and wait for clarification.
4. **Do not modify spec documents.** Specs are read-only inputs. If you think a spec is wrong or inconsistent, tell me — don't edit it.
5. **Do not add dependencies** beyond what the spec or existing `requirements.txt` / `pyproject.toml` calls for. If you believe one is needed, ask first.
6. **Do not refactor existing code** unless the spec explicitly calls for it.
7. **Honor the traceability chain.** Every model, field, enum value, constant, and test should be traceable to a specific FR, NFR, DECISION, or research finding. If you can't find the source, ask before inventing.

### Quality Standards

8. **Read the engineering standards before writing code** (see §Mandatory Pre-Reading above).
9. **Tests are not optional.** Every deliverable includes tests written alongside implementation. Follow AAA pattern (Arrange-Act-Assert). If a test spec exists (v0.1.3b), implement those exact tests. If not, write tests that cover the spec's Exit Criteria.
10. **Logging is not optional.** Every module uses `logging.getLogger(__name__)` and logs key operations at INFO level. No `print()` in source modules.
11. **Docstrings are not optional.** Every public module, class, and function gets a Google-style docstring with Args, Returns, Raises, and Example sections. Include research basis references where applicable (e.g., `Research basis: v0.0.4b §Content Best Practices`).
12. **Format and lint.** Run `black` and `ruff check` on all changed files before declaring the task complete.
13. **Inline comments should be meaningful.** Explain *why*, not *what*. Reference research artifacts, DECISION IDs, or FR IDs where the design rationale is non-obvious.

### Process

14. **Check the spec's parent document and dependency chain** — verify those prerequisites exist before starting. For v0.1.2 sub-parts, the dependency order is: v0.1.2a → v0.1.2b → v0.1.2c → v0.1.2d.
15. **Work through Exit Criteria as a checklist.** Each checkbox is a unit of work. Satisfy them in order.
16. **Commit with version-prefixed messages:** `{type}(v{X}.{Y}.{Z}): imperative description`
    - Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`
    - Examples: `feat(v0.1.2a): implement DiagnosticCode enum with 26 error codes`
    - For sub-parts, use the sub-part version: `feat(v0.1.2a):` not `feat(v0.1.2):`
17. **Create only the files and directories the spec defines.** If the spec says `src/docstratum/schema/diagnostics.py`, create exactly that path. Do not create adjacent files "for convenience."

### Finishing

18. When done, **summarize**: which Exit Criteria are satisfied (with evidence), which are not (and why), and what the next version/sub-part should pick up.
19. Run the **self-review checklist** from `RR-META-development-workflow.md` before declaring the task complete.
20. **Cross-reference check:** Confirm that any new enum values, model classes, or constants match what the spec defines — count them. If the spec says "26 diagnostic codes" and you have 25, that's a bug, not a rounding error.

## Start

1. Read the target spec now.
2. Read its sub-parts (a, b, c, d) if they exist in the same directory.
3. Read the parent spec's §Design Decisions Applied and §Exit Criteria sections.
4. Read the research artifacts referenced in the spec's `> Traces to:` line.
5. Tell me your implementation plan before writing any code. The plan should list:
   - Files to create (exact paths)
   - Key classes/enums/constants to implement (with counts from the spec)
   - Dependencies on other sub-parts or modules
   - Any ambiguities or concerns you want to flag
