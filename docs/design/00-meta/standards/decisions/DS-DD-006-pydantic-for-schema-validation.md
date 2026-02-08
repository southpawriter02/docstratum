# DS-DD-006: Pydantic for Schema Validation

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DD-006 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Decision ID** | DECISION-006 |
| **Date Decided** | 2026-01-25 (v0.0.4d) |
| **Impact Area** | All Schema Models (`src/docstratum/schema/*.py` — all 7 files use Pydantic v2 BaseModel) |
| **Provenance** | v0.0.4d §Differentiators and Decision Log |

## Decision

**Pydantic v2 is the designated schema validation framework for all DocStratum models. All schema files must use Pydantic BaseModel as the base class, with strict type validation and human-readable error messages.**

## Context

DocStratum needed a programmatic validation framework to ensure schema consistency across all model definitions. The framework had to support Python type hints natively, provide clear validation errors, handle complex nested models, and integrate seamlessly with the existing Python ecosystem. Early prototyping showed that a robust schema validation layer was critical to prevent malformed input from propagating through the documentation generation pipeline.

The decision to standardize on Pydantic v2 was driven by three key requirements:
1. **Type Safety**: Full support for Python type hints and modern type annotation syntax
2. **Developer Experience**: Clear, actionable error messages that help developers understand validation failures
3. **Extensibility**: Support for custom validators, computed fields, and complex nested model hierarchies

## Alternatives Considered

| Option | Rationale For | Rationale Against |
|--------|---------------|-------------------|
| JSON Schema | Portable across languages; industry-standard format; declarative syntax | Verbose and difficult to maintain in Python; poor integration with Python type hints; weak error messaging; requires separate schema file maintenance |
| Zod (TypeScript) | Excellent developer experience; powerful runtime validation | TypeScript/JavaScript-focused; poor Python ecosystem integration; adds non-standard toolchain to Python project |
| Custom Validation | Full control over validation logic; no external dependencies | Brittle and hard to maintain at scale; inconsistent error messages; duplicates work already solved by libraries; increases test burden |
| **Pydantic v2 (Chosen)** | Strong runtime type validation; native Python integration; excellent error messages; supports nested models and inheritance; extensive ecosystem support; active maintenance; JSON schema export capability | Requires external dependency; slight learning curve for custom validators |

## Rationale

Pydantic v2 was selected because it provides the best balance of type safety, developer experience, and maintainability for a Python-based documentation standards library. The framework's integration with Python's type hints means schema definitions serve as living documentation. Pydantic's error messages are specifically designed to guide developers toward correct usage, which is critical in an educational context where DocStratum is teaching documentation standards.

The v2 upgrade was chosen specifically for its performance improvements, stricter validation by default, and cleaner API. Early adoption ensures the project benefits from the latest validation capabilities and community support.

## Impact on ASoT

This decision affects all schema validation criteria in the ASoT standards:
- **DS-VC-STR-001** (Schema Validity): All models must pass Pydantic v2 validation
- **DS-VC-STR-002** (Type Consistency): Type hints in schema files are enforced at runtime via Pydantic
- **DS-VC-ERR-001** (Error Message Quality): Validation errors must be human-readable and suggest corrections — a Pydantic strength

The validation pipeline (v0.2.4+) will depend on Pydantic models for all detection and analysis operations. Any changes to Pydantic usage patterns must maintain backward compatibility with existing validation criteria.

## Constraints Imposed

1. **Minimum Version Requirement**: All DocStratum installations must require Pydantic ≥2.0.0. Pinned in `requirements.txt` to ensure consistency.
2. **BaseModel Inheritance**: All schema models must inherit from `pydantic.BaseModel`. No exceptions.
3. **Validation Strictness**: Default Pydantic validation behavior must not be relaxed (e.g., no `validate_default=False` without documentation).
4. **Error Handling**: Validation errors caught from Pydantic must be converted to human-readable format before surfacing to end users.
5. **JSON Schema Export**: All models must support `.model_json_schema()` for documentation and client-side validation.

## Related Decisions

- **DS-DD-001**: Core architecture decisions that establish the role of schema validation
- **DS-DD-009**: Validation pipeline built on top of Pydantic models for anti-pattern detection
- **DS-DD-016**: Severity classification system uses Pydantic models for configuration

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.3 |
