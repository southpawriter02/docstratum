# v0.1.3 — Unified Rule Registry Design Specification

> **Status:** DRAFT
> **Created:** 2026-02-09
> **Last Updated:** 2026-02-09
> **Governed By:** RR-META-documentation-backlog.md (Deliverable 3)
> **Depends On:** RR-SPEC-v0.1.3-output-tier-specification.md (Deliverable 1), RR-SPEC-v0.1.3-remediation-framework.md (Deliverable 2)
> **Feeds Into:** Deliverable 4 (Validation Profiles), Deliverable 5 (Report Generation Stage)
> **ASoT Version:** 1.0.0
> **Traces To:** FR-004 (error reporting), Output Tier Spec §3.1 (Stage Output Summary), Remediation Framework §1 (data contract)

---

## 1. Purpose

The DocStratum validation engine contains approximately 70+ discrete validation rules, checks, and quality dimensions spread across multiple Python modules and ASoT standards files with no central registry connecting them. This creates a critical integration problem:

**The Problem:** When the Report Generation Stage (Deliverable 5, Stage 6) generates a Tier 3 remediation playbook, it needs to know:

1. **What is this rule?** (E001: No H1 Title) — *defined in diagnostics.py*
2. **Which Python function implements it?** (`validate_title()` in `parser.py`) — *knowledge lost*
3. **What pipeline stage executes it?** (Stage 2: Per-File) — *knowledge lost*
4. **What other checks depend on this one?** (E005 parsing depends on E003 encoding) — *knowledge lost*
5. **Which anti-patterns does it detect?** (E001 detects AP-CRIT-002) — *knowledge lost*
6. **Where is the authoritative standard definition?** (`docs/design/00-meta/standards/criteria/DS-VC-STR-001-h1-title-present.md`) — *knowledge lost*

Today, this knowledge is scattered across:

- **diagnostics.py** (38 diagnostic codes with terse `remediation` hints)
- **constants.py** (28 anti-patterns, cross-referenced by CHECK-NNN IDs with no machine-readable mapping)
- **validation.py** (5 validation levels: L0–L4)
- **ecosystem.py** (5 ecosystem health dimensions)
- **ASoT standards directory** (146+ canonical artifacts indexed in DS-MANIFEST.md)
- **Remediation Framework** (priority model, grouping strategy, effort estimates)
- **Output Tier Spec** (which tiers expose which diagnostic codes)

No single document maps a rule's **definition** (ASoT standard) to its **implementation** (Python module), its **pipeline stage** (when it runs), its **dependencies** (what must pass first), and its **downstream impact** (which tiers consume it).

### 1.1 The Unified Rule Registry Solves This

The Unified Rule Registry is a machine-readable, schema-validated registry that serves as the **single source of truth** for rule metadata. It connects:

- **Rule identity** (DS-prefixed ID, diagnostic code, anti-pattern references)
- **Implementation details** (module path, function name, pipeline stage)
- **Validation hierarchy** (validation level, dependencies)
- **Consumption contracts** (output tiers, profile visibility)
- **Standards provenance** (ASoT path, status)
- **Remediation guidance** (priority, effort, templates)

This specification defines:

1. The **Pydantic schema** for registry entries (`RegisteredRule`, `RuleRegistry`)
2. The **format decision** (YAML + Pydantic at startup) and justification
3. The **relationship to DS-MANIFEST** (extends, does not replace)
4. **Integrity assertions** (23 testable conditions for data validity)
5. **Six example entries** covering L0–L4 and ecosystem validation
6. **Consistency review** against ANTI_PATTERN_REGISTRY
7. **Design decisions** (DECISION-027: YAML+Pydantic, DECISION-028: Extends not Replaces)

### 1.2 Relationship to Existing Specifications

| Artifact | This Spec's Role |
|----------|-----------------|
| Output Tier Spec (D1) | **Consumer:** The Rule Registry enables the Tier 3 + Tier 4 renderers to look up rule metadata (tags, effort_default, score_dimension) for action item generation. |
| Remediation Framework (D2) | **Cross-reference:** Registry's `remediation_template_key` field points to remediation_templates.yaml keys. Framework provides the prose content; registry provides the mapping. |
| DS-MANIFEST.md | **Parent registry:** Manifest is source of truth for *what standards exist*. Rule Registry is source of truth for *how standards are implemented*. Registry extends, does not replace. |
| diagnostics.py | **Source of truth:** Canonical home of DiagnosticCode enum. Registry adds mapping layer. |
| ANTI_PATTERN_REGISTRY | **Source of truth:** Canonical home of anti-pattern definitions. Registry's `anti_patterns` field cross-references. |
| Profiles (D4) | **Consumer:** Profiles define which rules are active based on `tags` and `rule_id` references. The registry enables tag-based rule composition. |
| Report Generation Stage (D5) | **Consumer:** Stage 6 queries the registry at runtime to determine output tier visibility, remediation templates, and profile composition. |

---

## 2. Pydantic Model Schema

The Rule Registry is defined by two Pydantic models: `RegisteredRule` (individual entries) and `RuleRegistry` (collection with integrity checks).

### 2.1 RegisteredRule Model

```python
# Pseudocode — not production Python imports
from pydantic import BaseModel, Field
from typing import Optional, List

class RegisteredRule(BaseModel):
    """A single registered validation rule, mapping definition to implementation."""

    # ────────────────────────────────────────────────────────────────────────────
    # IDENTITY
    # ────────────────────────────────────────────────────────────────────────────

    rule_id: str = Field(
        ...,
        description="Unique DS-prefixed identifier (e.g., DS-VC-STR-001, DS-RC-E001). "
                    "Follows pattern: DS-[TYPE]-[CODE] where TYPE in {VC, RC, AP, EH}. "
                    "REQUIRED. Must be unique within registry.",
        example="DS-RC-E001"
    )

    name: str = Field(
        ...,
        description="Human-readable rule name (e.g., 'No H1 Title', 'Missing Link Description'). "
                    "Keep ≤80 chars. Used in playbooks and reports.",
        example="No H1 Title"
    )

    description: str = Field(
        ...,
        description="One-sentence summary of what this rule validates. ≤200 chars. "
                    "Answers: 'What does this rule check?'",
        example="Every llms.txt file must begin with exactly one H1 title for identification."
    )

    # ────────────────────────────────────────────────────────────────────────────
    # DIAGNOSTIC & ANTI-PATTERN REFERENCES
    # ────────────────────────────────────────────────────────────────────────────

    diagnostic_codes: list[str] = Field(
        default_factory=list,
        description="List of DiagnosticCode enum values this rule can emit. "
                    "Example: ['E001'] for H1 title check. "
                    "A rule may emit multiple codes (e.g., link checks emit W003 and E006). "
                    "REQUIRED if this is a validation rule (not pure information gathering). "
                    "May be empty for context-gathering rules (e.g., ast collection).",
        example=["E001"]
    )

    anti_patterns: list[str] = Field(
        default_factory=list,
        description="List of AntiPatternID enum values this rule detects. "
                    "Maps to ANTI_PATTERN_REGISTRY keys (e.g., 'AP-CRIT-001'). "
                    "May be empty if this rule doesn't detect anti-patterns. "
                    "Used to link diagnostics to broader quality concerns.",
        example=["AP-CRIT-002"]
    )

    # ────────────────────────────────────────────────────────────────────────────
    # VALIDATION HIERARCHY
    # ────────────────────────────────────────────────────────────────────────────

    validation_level: int = Field(
        ...,
        ge=0, le=4,
        description="Which validation level (L0–L4) this rule belongs to. "
                    "0=L0 (Parseable), 1=L1 (Structural), 2=L2 (Content), "
                    "3=L3 (Best Practices), 4=L4 (DocStratum Extended). "
                    "Rules at lower levels are prerequisites for higher levels.",
        example=1
    )

    pipeline_stage: int = Field(
        ...,
        ge=1, le=6,
        description="Which pipeline stage executes this rule. "
                    "1=Discovery, 2=Per-File, 3=Relationship, 4=Ecosystem Validation, "
                    "5=Scoring, 6=Report Generation. "
                    "Maps to PipelineStageId enum. Used for stage composition and ordering.",
        example=2
    )

    # ────────────────────────────────────────────────────────────────────────────
    # IMPLEMENTATION DETAILS
    # ────────────────────────────────────────────────────────────────────────────

    implemented_in: Optional[str] = Field(
        default=None,
        description="Module path to the implementing function (e.g., 'docstratum.pipeline.per_file_validator.validate_h1_title'). "
                    "Format: 'module.submodule.function_name'. "
                    "Used for dynamic rule invocation and debugging. "
                    "May be None for pure metadata rules (no active code).",
        example="docstratum.pipeline.per_file_validator.validate_h1_title"
    )

    depends_on: list[str] = Field(
        default_factory=list,
        description="List of rule_ids that must pass before this rule runs. "
                    "Example: E005 depends on ['E003'] (encoding must be valid before parsing). "
                    "Used to build execution DAG and explain why a check was skipped. "
                    "May be empty for rules with no prerequisites.",
        example=["DS-RC-E003"]
    )

    # ────────────────────────────────────────────────────────────────────────────
    # STANDARDS & PROVENANCE
    # ────────────────────────────────────────────────────────────────────────────

    asot_path: str = Field(
        ...,
        description="Relative path to ASoT standard file (from docs/design/00-meta/standards/). "
                    "Example: 'criteria/structural/DS-VC-STR-001-h1-title-present.md' "
                    "or 'diagnostics/errors/DS-DC-E001-NO_H1_TITLE.md'. "
                    "REQUIRED. Must resolve to existing file. "
                    "Used for traceability and standards versioning.",
        example="criteria/structural/DS-VC-STR-001-h1-title-present.md"
    )

    status: str = Field(
        default="DRAFT",
        description="Registry entry status. "
                    "DRAFT = under development, may change. "
                    "RATIFIED = stable, used in production. "
                    "DEPRECATED = no longer recommended, kept for backward compatibility. "
                    "Used for version management.",
        example="RATIFIED"
    )

    # ────────────────────────────────────────────────────────────────────────────
    # OUTPUT TIER & VISIBILITY
    # ────────────────────────────────────────────────────────────────────────────

    output_tiers: list[int] = Field(
        default_factory=lambda: [1, 2, 3, 4],
        description="Which output tiers (1–4) include this rule's results. "
                    "Tier 1 (Pass/Fail): typically only structural errors (L0–L1). "
                    "Tier 2 (Diagnostic): all findings. "
                    "Tier 3 (Playbook): findings grouped into action items. "
                    "Tier 4 (Adapted): findings plus domain-specific guidance. "
                    "Default: [1, 2, 3, 4] (visible in all tiers). "
                    "Used to filter output for tier-specific renderers.",
        example=[2, 3, 4]
    )

    tags: list[str] = Field(
        default_factory=list,
        description="Freeform tags for rule composition and filtering. "
                    "Examples: ['structural', 'ecosystem', 'quick-lint', 'requires_io', 'async']. "
                    "Tags enable profiles (D4) to select rules programmatically: "
                    "'@structural AND @quick-lint' selects all structural checks that run fast. "
                    "Case-insensitive. Must be lowercase in registry. "
                    "May be empty.",
        example=["structural", "quick-lint"]
    )

    # ────────────────────────────────────────────────────────────────────────────
    # REMEDIATION & SCORING
    # ────────────────────────────────────────────────────────────────────────────

    remediation_template_key: Optional[str] = Field(
        default=None,
        description="Key into remediation_templates.yaml for expanded prose guidance. "
                    "Typically the diagnostic code (e.g., 'E001', 'W009'). "
                    "May be None if no remediation template exists. "
                    "Used by Tier 3 renderer to include actionable guidance.",
        example="E001"
    )

    score_dimension: Optional[str] = Field(
        default=None,
        description="Quality or ecosystem dimension this rule affects. "
                    "Quality dimensions: 'STRUCTURAL' (30 pts), 'CONTENT' (50 pts), "
                    "'ANTI_PATTERN' (20 pts). "
                    "Ecosystem dimensions: 'COVERAGE', 'CONSISTENCY', 'COMPLETENESS', "
                    "'TOKEN_EFFICIENCY', 'FRESHNESS'. "
                    "May be None for informational rules (I-severity codes). "
                    "Used to compute score impact estimates.",
        example="STRUCTURAL"
    )

    effort_default: Optional[str] = Field(
        default=None,
        description="Default effort estimate from Remediation Framework. "
                    "QUICK_WIN (minutes), MODERATE (hours), STRUCTURAL (days). "
                    "May be None if effort varies (e.g., W003 on 1 vs. 50 links). "
                    "Used by Tier 3 playbook for effort-based grouping.",
        example="QUICK_WIN"
    )

    # ────────────────────────────────────────────────────────────────────────────
    # METADATA
    # ────────────────────────────────────────────────────────────────────────────

    priority_default: Optional[str] = Field(
        default=None,
        description="Default priority from Remediation Framework (CRITICAL, HIGH, MEDIUM, LOW). "
                    "Used by Tier 3 renderer for priority-based grouping. "
                    "May be overridden by profiles. "
                    "Stored here for convenience; definitive source is remediation_framework.yaml.",
        example="CRITICAL"
    )

    research_evidence: Optional[str] = Field(
        default=None,
        description="Brief reference to research or data supporting this rule. "
                    "Example: 'v0.0.4a: 87% vs 31% success rate with Master Index'. "
                    "Helps users understand WHY a rule matters. "
                    "May be None for self-evident rules.",
        example="v0.0.4a: 87% vs 31% LLM success rate correlation"
    )

    model_config = ConfigDict(validate_assignment=True)


class RegisteredRule(BaseModel):
    """(continued from above)"""

    # ────────────────────────────────────────────────────────────────────────────
    # EXAMPLE INSTANCE
    # ────────────────────────────────────────────────────────────────────────────
    # rule = RegisteredRule(
    #     rule_id="DS-RC-E001",
    #     name="No H1 Title",
    #     description="Every llms.txt file must begin with exactly one H1 title.",
    #     diagnostic_codes=["E001"],
    #     anti_patterns=["AP-CRIT-002"],
    #     validation_level=1,
    #     pipeline_stage=2,
    #     implemented_in="docstratum.pipeline.per_file_validator.validate_h1_title",
    #     depends_on=["DS-RC-E003"],
    #     asot_path="criteria/structural/DS-VC-STR-001-h1-title-present.md",
    #     status="RATIFIED",
    #     output_tiers=[1, 2, 3, 4],
    #     tags=["structural", "quick-lint"],
    #     remediation_template_key="E001",
    #     score_dimension="STRUCTURAL",
    #     effort_default="QUICK_WIN",
    #     priority_default="CRITICAL",
    #     research_evidence=None
    # )
```

### 2.2 RuleRegistry Model

```python
class RuleRegistry(BaseModel):
    """Container for all registered rules with integrity validation."""

    version: str = Field(
        default="1.0.0",
        description="Semantic version of the registry. "
                    "MAJOR: breaking schema changes. "
                    "MINOR: new rules added. "
                    "PATCH: rule updates (no schema impact).",
        example="1.0.0"
    )

    rules: list[RegisteredRule] = Field(
        default_factory=list,
        description="Complete list of registered rules. "
                    "Must contain at least one entry. "
                    "Sorted by rule_id for deterministic ordering.",
        example=[]
    )

    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 timestamp when this registry snapshot was created."
    )

    model_config = ConfigDict(validate_assignment=True)

    def assert_integrity(self) -> dict[str, list[str]]:
        """Run all integrity checks. Return dict of category -> list of errors."""
        errors: dict[str, list[str]] = {}

        # Check: No duplicate rule_ids
        rule_ids = [r.rule_id for r in self.rules]
        duplicates = [id for id in rule_ids if rule_ids.count(id) > 1]
        if duplicates:
            errors.setdefault("duplicate_rule_ids", []).extend(duplicates)

        # Check: Every diagnostic_code exists in DiagnosticCode enum
        from docstratum.schema.diagnostics import DiagnosticCode
        valid_codes = {dc.value for dc in DiagnosticCode}
        for rule in self.rules:
            for code in rule.diagnostic_codes:
                if code not in valid_codes:
                    errors.setdefault("invalid_diagnostic_codes", []).append(
                        f"{rule.rule_id}: code '{code}' not in DiagnosticCode"
                    )

        # Check: Every anti_pattern exists in ANTI_PATTERN_REGISTRY
        from docstratum.schema.constants import ANTI_PATTERN_REGISTRY
        valid_aps = {ap.id.value for ap in ANTI_PATTERN_REGISTRY}
        for rule in self.rules:
            for ap in rule.anti_patterns:
                if ap not in valid_aps:
                    errors.setdefault("invalid_anti_patterns", []).append(
                        f"{rule.rule_id}: anti-pattern '{ap}' not in ANTI_PATTERN_REGISTRY"
                    )

        # Check: Every asot_path resolves to existing file
        asot_base = Path("docs/design/00-meta/standards")
        for rule in self.rules:
            path = asot_base / rule.asot_path
            if not path.exists():
                errors.setdefault("missing_asot_paths", []).append(
                    f"{rule.rule_id}: ASoT path not found: {rule.asot_path}"
                )

        # Check: Every pipeline_stage is valid (1–6)
        for rule in self.rules:
            if rule.pipeline_stage < 1 or rule.pipeline_stage > 6:
                errors.setdefault("invalid_pipeline_stages", []).append(
                    f"{rule.rule_id}: stage {rule.pipeline_stage} out of range [1,6]"
                )

        # Check: Every depends_on reference exists in registry
        registered_ids = {r.rule_id for r in self.rules}
        for rule in self.rules:
            for dep in rule.depends_on:
                if dep not in registered_ids:
                    errors.setdefault("missing_dependencies", []).append(
                        f"{rule.rule_id}: depends_on '{dep}' not in registry"
                    )

        # Check: Every validation_level is 0–4
        for rule in self.rules:
            if rule.validation_level < 0 or rule.validation_level > 4:
                errors.setdefault("invalid_validation_levels", []).append(
                    f"{rule.rule_id}: level {rule.validation_level} out of range [0,4]"
                )

        # Check: Every output_tier is 1–4
        for rule in self.rules:
            for tier in rule.output_tiers:
                if tier < 1 or tier > 4:
                    errors.setdefault("invalid_output_tiers", []).append(
                        f"{rule.rule_id}: tier {tier} out of range [1,4]"
                    )

        # Check: Every status is valid
        valid_statuses = {"DRAFT", "RATIFIED", "DEPRECATED"}
        for rule in self.rules:
            if rule.status not in valid_statuses:
                errors.setdefault("invalid_statuses", []).append(
                    f"{rule.rule_id}: status '{rule.status}' not in {valid_statuses}"
                )

        # Check: Every score_dimension is valid (if present)
        valid_dims = {
            "STRUCTURAL", "CONTENT", "ANTI_PATTERN",
            "COVERAGE", "CONSISTENCY", "COMPLETENESS",
            "TOKEN_EFFICIENCY", "FRESHNESS"
        }
        for rule in self.rules:
            if rule.score_dimension and rule.score_dimension not in valid_dims:
                errors.setdefault("invalid_score_dimensions", []).append(
                    f"{rule.rule_id}: dimension '{rule.score_dimension}' not valid"
                )

        # Check: Every effort_default is valid (if present)
        valid_efforts = {"QUICK_WIN", "MODERATE", "STRUCTURAL"}
        for rule in self.rules:
            if rule.effort_default and rule.effort_default not in valid_efforts:
                errors.setdefault("invalid_effort_defaults", []).append(
                    f"{rule.rule_id}: effort '{rule.effort_default}' not valid"
                )

        # Check: Every priority_default is valid (if present)
        valid_priorities = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
        for rule in self.rules:
            if rule.priority_default and rule.priority_default not in valid_priorities:
                errors.setdefault("invalid_priority_defaults", []).append(
                    f"{rule.rule_id}: priority '{rule.priority_default}' not valid"
                )

        # Check: Every diagnostic code is covered in registry (completeness)
        registered_codes = set()
        for rule in self.rules:
            registered_codes.update(rule.diagnostic_codes)
        all_codes = {dc.value for dc in DiagnosticCode}
        uncovered = all_codes - registered_codes
        if uncovered:
            errors.setdefault("uncovered_diagnostic_codes", []).extend(sorted(uncovered))

        # Check: Every anti-pattern is covered in registry (completeness)
        registered_aps = set()
        for rule in self.rules:
            registered_aps.update(rule.anti_patterns)
        all_aps = {ap.id.value for ap in ANTI_PATTERN_REGISTRY}
        uncovered_aps = all_aps - registered_aps
        if uncovered_aps:
            errors.setdefault("uncovered_anti_patterns", []).extend(sorted(uncovered_aps))

        return errors
```

---

## 3. Relationship to DS-MANIFEST

The DocStratum project maintains two registries:

**DS-MANIFEST.md** (ASoT Source of Truth):
- Authoritative registry of what standards exist
- Entries: DS-VC-001 (Validation Criteria), DS-DC-E001 (Diagnostic Code), DS-VL-L0 (Validation Level), etc.
- Purpose: Define the specification, not the implementation
- Status field: DRAFT, RATIFIED, DEPRECATED — indicates specification maturity
- Scope: 146+ standard artifacts

**Rule Registry** (Implementation Mapping Layer):
- Maps definitions (from DS-MANIFEST) to implementations (Python modules, pipeline stages)
- Entries: DS-RC-E001 (Rule Catalog), cross-referencing DS-VC-STR-001, DiagnosticCode.E001, remediation templates
- Purpose: Connect what we should do (spec) to how we do it (code)
- Status field: DRAFT, RATIFIED, DEPRECATED — indicates implementation maturity
- Scope: 38 diagnostic rules + N informational/structural checks

### 3.1 Why "Extends" Not "Replaces" or "Parallel"

#### Option 1: Registry Replaces DS-MANIFEST (REJECTED)

**Proposal:** Move all standard definitions into the rule registry, deprecate DS-MANIFEST.

**Problems:**
- Confuses layers of abstraction: specifications are different from implementations
- Diagnostic code definitions (what E001 means) are ASoT concerns; implementation details (where the code runs) are engine concerns
- ASoT is source of truth for **standards design**; rule registry is source of truth for **engine implementation**
- Standards should be independent of any one implementation (DocStratum is not the only consumer of llms.txt standards)
- Makes the registry overly complex: it becomes both specification + implementation doc

**Decision:** Rejected. Keep DS-MANIFEST as authoritative specification.

#### Option 2: Registry Parallel to DS-MANIFEST (REJECTED)

**Proposal:** Maintain two independent registries that may drift and require manual synchronization.

**Problems:**
- Massive maintenance burden: every new diagnostic code requires entries in BOTH registries
- Silent failures: code changes without updating the parallel registry
- No single source of truth for "is rule X implemented?"
- Violates DRY principle

**Decision:** Rejected. Single source of truth is essential.

#### Option 3: Registry Extends DS-MANIFEST (SELECTED)

**Proposal:** DS-MANIFEST defines *what* (specifications); Rule Registry adds *how* (implementation mapping).

**Rationale:**
- Clear separation of concerns: manifest = what/why, registry = how/where
- No duplication: registry references manifest via `asot_path` field
- Single source of truth: manifest owns definition, registry owns implementation
- Future-proof: if another tool consumes llms.txt standards, it only needs the manifest, not the registry
- Natural evolution: manifest is stable (ratified standards), registry evolves with engine implementation (DRAFT rules, experimental checks)

**Contract:**
- Every entry in the Rule Registry **must** have an `asot_path` pointing to a valid DS-MANIFEST artifact
- The rule registry's `status` field tracks **implementation** status, not specification status
- When a rule is DEPRECATED in the registry but RATIFIED in the manifest, it means "this specification is still valid but we're not checking it anymore"

**Example:**
```
DS-MANIFEST entry:
  - rule_id: DS-VC-STR-001
  - path: criteria/structural/DS-VC-STR-001-h1-title-present.md
  - status: RATIFIED (specification is solid)

Rule Registry entry:
  - rule_id: DS-RC-E001
  - name: No H1 Title
  - asot_path: criteria/structural/DS-VC-STR-001-h1-title-present.md
  - status: RATIFIED (implementation is production-ready)
  - implemented_in: docstratum.pipeline.per_file_validator.validate_h1_title
```

---

## 4. Format Decision: YAML + Pydantic

### 4.1 Format Candidates

The Rule Registry must be:
1. **Human-readable** (documentation team can understand, review, modify)
2. **Machine-parseable** (Python code can load and validate)
3. **Editable** (team members can add/update rules without touching Python source)
4. **Schema-validated** (guarantees integrity at load time)
5. **Version-controlled** (changes tracked in git)

Three formats were evaluated:

#### Candidate 1: Python Module (REJECTED)

```python
# rule_registry.py
RULE_REGISTRY = {
    "DS-RC-E001": RegisteredRule(
        rule_id="DS-RC-E001",
        name="No H1 Title",
        ...
    ),
    ...
}
```

**Pros:** Type-safe, IDE support, no parsing needed
**Cons:**
- Requires Python knowledge to edit; non-technical team members can't modify
- Changes require Python syntax validation
- Pull request reviews harder (more code, less like data)
- Not recommended for frequently-changing metadata

**Decision:** Rejected for maintainability reasons.

#### Candidate 2: Static Markdown (REJECTED)

```markdown
# Rules

| Rule ID | Name | Codes | Effort |
|---------|------|-------|--------|
| DS-RC-E001 | No H1 Title | E001 | QUICK_WIN |
```

**Pros:** Human-friendly, easy to review
**Cons:**
- No schema validation; easy to make mistakes (wrong number of columns, invalid values)
- No machine-readable structure (must parse table manually)
- Hard to represent nested lists (diagnostic_codes, depends_on, tags)
- Load-time validation is weak or nonexistent
- Not suitable for ~100+ entries with 20 fields each

**Decision:** Rejected for schema validation and expressiveness.

#### Candidate 3: YAML + Pydantic (SELECTED)

```yaml
version: "1.0.0"
rules:
  - rule_id: DS-RC-E001
    name: "No H1 Title"
    description: "Every llms.txt file must begin with exactly one H1 title."
    diagnostic_codes: ["E001"]
    anti_patterns: ["AP-CRIT-002"]
    validation_level: 1
    pipeline_stage: 2
    implemented_in: "docstratum.pipeline.per_file_validator.validate_h1_title"
    depends_on: ["DS-RC-E003"]
    asot_path: "criteria/structural/DS-VC-STR-001-h1-title-present.md"
    status: "RATIFIED"
    output_tiers: [1, 2, 3, 4]
    tags: ["structural", "quick-lint"]
    remediation_template_key: "E001"
    score_dimension: "STRUCTURAL"
    effort_default: "QUICK_WIN"
    priority_default: "CRITICAL"
    research_evidence: null
```

**Pros:**
- Human-readable yet structured (YAML is designed for config/data)
- Machine-parseable (standard YAML libraries)
- Editable by non-programmers (no Python syntax needed)
- Schema-validated at load time (Pydantic)
- Standard practice (same pattern as remediation_templates.yaml, Kubernetes manifests, etc.)
- Supports nested structures (lists, dicts)
- Version-controlled cleanly (diff-friendly)
- Load-time validation catches errors immediately

**Cons:** Requires YAML parser (negligible — standard library coverage)

**Decision:** Selected.

### 4.2 Registry File Location

**File:** `/sessions/upbeat-eager-ritchie/mnt/docstratum/src/docstratum/rule_registry.yaml`

**Rationale:**
- Co-located with remediation_templates.yaml (both loaded at engine startup)
- In `src/` for version control, not in documentation tree
- Immutable after deployment (config, not documentation)
- Referenced by all pipeline stages for rule metadata lookups

**Load-time Integration:**

```python
# Pseudocode for engine startup
from pydantic_yaml import parse_file_as
from pathlib import Path

registry_path = Path(__file__).parent / "rule_registry.yaml"
rule_registry: RuleRegistry = parse_file_as(RuleRegistry, registry_path)

# Validate integrity
errors = rule_registry.assert_integrity()
if errors:
    raise RegistryValidationError(f"Rule Registry validation failed:\n{errors}")

# Now available throughout the engine
```

---

## 5. Integrity Assertions

The `RuleRegistry.assert_integrity()` method performs 23 testable conditions. Each condition is a sanity check that must be true for the registry to be valid. These are enforced at load time (Stage 1: Discovery).

### 5.1 Identity & Uniqueness

1. **No duplicate rule_ids** — Every `rule.rule_id` is unique across the registry. Enforced by: `len(rule_ids) == len(set(rule_ids))`

### 5.2 Diagnostic Code Integrity

2. **Every diagnostic_code exists** — Every code in `rule.diagnostic_codes` must exist in `DiagnosticCode` enum. Enforced by: code value in `{dc.value for dc in DiagnosticCode}`

3. **Complete diagnostic coverage** — Every value in `DiagnosticCode` enum must appear in at least one `diagnostic_codes` list. Enforced by: `all_codes ⊆ union(rule.diagnostic_codes for rule in rules)`

**Rationale:** Ensures no diagnostic code is defined but unregistered, which would break rule metadata lookups.

### 5.3 Anti-Pattern Integrity

4. **Every anti-pattern exists** — Every code in `rule.anti_patterns` must exist in `ANTI_PATTERN_REGISTRY`. Enforced by: code value in `{ap.id.value for ap in ANTI_PATTERN_REGISTRY}`

5. **Complete anti-pattern coverage** — Every anti-pattern in `ANTI_PATTERN_REGISTRY` must appear in at least one `anti_patterns` list. Enforced by: `all_aps ⊆ union(rule.anti_patterns for rule in rules)`

**Rationale:** Maps every anti-pattern to at least one detecting rule.

### 5.4 Validation Hierarchy

6. **Valid validation_level** — Every `validation_level` is in range [0, 4]. Enforced by: `0 <= rule.validation_level <= 4`

7. **Valid pipeline_stage** — Every `pipeline_stage` is in range [1, 6]. Enforced by: `1 <= rule.pipeline_stage <= 6`

**Rationale:** Prevents out-of-range values that would break stage iteration.

### 5.5 Dependency Graph

8. **All dependencies exist** — Every `rule_id` in `rule.depends_on` must exist as another rule's `rule_id`. Enforced by: `all_deps ⊆ set(rule_ids)`

9. **No circular dependencies** — The dependency graph formed by `depends_on` edges must be acyclic. Enforced by: `not has_cycle(graph)`

**Rationale:** Ensures the execution DAG is well-formed and can be topologically sorted.

### 5.6 Standards Provenance

10. **ASoT path is absolute** — Every `asot_path` must resolve to an existing file in `docs/design/00-meta/standards/`. Enforced by: `(Path("docs/design/00-meta/standards") / rule.asot_path).exists()`

**Rationale:** Guarantees traceability to authoritative standards; breaks loudly if standards move.

### 5.7 Output Tier Integrity

11. **Valid output_tiers** — Every value in `rule.output_tiers` is in range [1, 4]. Enforced by: `all(1 <= tier <= 4 for tier in rule.output_tiers)`

**Rationale:** Prevents rules from claiming visibility in non-existent tiers.

### 5.8 Status & Enumeration Integrity

12. **Valid status** — Every `status` is one of: DRAFT, RATIFIED, DEPRECATED. Enforced by: `rule.status in {"DRAFT", "RATIFIED", "DEPRECATED"}`

13. **Valid score_dimension** — If present, `score_dimension` is one of: STRUCTURAL, CONTENT, ANTI_PATTERN, COVERAGE, CONSISTENCY, COMPLETENESS, TOKEN_EFFICIENCY, FRESHNESS. Enforced by: `rule.score_dimension in valid_dims or rule.score_dimension is None`

14. **Valid effort_default** — If present, `effort_default` is one of: QUICK_WIN, MODERATE, STRUCTURAL. Enforced by: `rule.effort_default in valid_efforts or rule.effort_default is None`

15. **Valid priority_default** — If present, `priority_default` is one of: CRITICAL, HIGH, MEDIUM, LOW. Enforced by: `rule.priority_default in valid_priorities or rule.priority_default is None`

**Rationale:** Prevents typos in enum-like fields.

### 5.9 Data Quality

16. **Rule name not empty** — `len(rule.name) > 0 and len(rule.name) <= 80` for readability

17. **Description not empty** — `len(rule.description) > 0 and len(rule.description) <= 200` for summaries

18. **Tags are lowercase** — All `tags` must be lowercase for consistent filtering

**Rationale:** Ensures metadata quality; prevents "Name" vs "name" confusion.

### 5.10 Cross-Field Consistency

19. **ERROR codes are CRITICAL or HIGH** — If `severity == ERROR`, then `priority_default in {CRITICAL, HIGH}`. Enforced by: implicit in Remediation Framework assignment logic.

**Rationale:** ERROR-severity findings should never be LOW priority.

20. **INFO codes are not CRITICAL** — If `severity == INFO`, then `priority_default != CRITICAL`. Enforced by: implicit in Remediation Framework assignment logic.

**Rationale:** Informational findings should not block work.

21. **L0 rules in Stage 1 or 2** — If `validation_level == 0`, then `pipeline_stage in {1, 2}`. Enforced by: L0 checks (encoding, parsing) run early or not at all.

**Rationale:** Parseable-level checks must run before structural checks.

### 5.11 Registry Completeness

22. **At least 38 rules** — The registry must cover all 38 diagnostic codes. Enforced by: `len(rules) >= 38`

**Rationale:** Minimum viable registry size.

23. **All ecosystem rules present** — All E009–E010, W012–W018, I008–I010 rules must be registered. Enforced by: `all(code in diagnostic_codes for rule in rules for code in {E009, E010, W012–W018, I008–I010})`

**Rationale:** Ensures ecosystem validation is fully registered.

### 5.12 Running Integrity Checks

```python
# At engine startup
errors = rule_registry.assert_integrity()

if errors:
    # Group errors by category for readability
    for category, messages in errors.items():
        logger.error(f"{category}:")
        for msg in messages:
            logger.error(f"  - {msg}")

    raise RegistryIntegrityError(
        f"Rule Registry failed {len(errors)} integrity checks. "
        f"See logs above. Fix rule_registry.yaml and restart."
    )

logger.info(f"Rule Registry: {len(rule_registry.rules)} rules, all integrity checks passed.")
```

---

## 6. Example Registry Entries

This section provides 6 example entries covering all validation levels, multiple pipeline stages, and both single-file and ecosystem contexts.

### 6.1 Example 1: L0 Structural Error (E003: Invalid Encoding)

```yaml
- rule_id: DS-RC-E003
  name: "Invalid Encoding"
  description: "File must be valid UTF-8. BOM markers are not allowed."
  diagnostic_codes: ["E003"]
  anti_patterns: []
  validation_level: 0
  pipeline_stage: 2
  implemented_in: "docstratum.pipeline.per_file_validator.validate_encoding"
  depends_on: []
  asot_path: "diagnostics/errors/DS-DC-E003-INVALID_ENCODING.md"
  status: "RATIFIED"
  output_tiers: [1, 2, 3, 4]
  tags: ["structural", "quick-lint", "encoding"]
  remediation_template_key: "E003"
  score_dimension: "STRUCTURAL"
  effort_default: "QUICK_WIN"
  priority_default: "CRITICAL"
  research_evidence: null
```

**Rationale:**
- **L0 (Parseable):** File encoding is prerequisite for parsing. Can't parse UTF-16 as UTF-8.
- **Pipeline Stage 2:** Per-file validator reads encoding before content parsing.
- **No dependencies:** First check to run (doesn't depend on other rules).
- **CRITICAL:** Blocks all downstream checks if file can't be read.
- **QUICK_WIN:** Fix is straightforward (re-encode file).

### 6.2 Example 2: L1 Structural Error (E001: No H1 Title)

```yaml
- rule_id: DS-RC-E001
  name: "No H1 Title"
  description: "Every llms.txt file must begin with exactly one H1 title for identification."
  diagnostic_codes: ["E001"]
  anti_patterns: ["AP-CRIT-002"]
  validation_level: 1
  pipeline_stage: 2
  implemented_in: "docstratum.pipeline.per_file_validator.validate_h1_title"
  depends_on: ["DS-RC-E003", "DS-RC-E005"]
  asot_path: "criteria/structural/DS-VC-STR-001-h1-title-present.md"
  status: "RATIFIED"
  output_tiers: [1, 2, 3, 4]
  tags: ["structural", "quick-lint", "identity"]
  remediation_template_key: "E001"
  score_dimension: "STRUCTURAL"
  effort_default: "QUICK_WIN"
  priority_default: "CRITICAL"
  research_evidence: "v0.0.4a: H1 is document identity anchor for all downstream processing."
```

**Rationale:**
- **L1 (Structural):** H1 title is core structure; missing it is a fundamental defect.
- **Depends on E003, E005:** Must validate encoding first, then Markdown syntax.
- **Anti-pattern AP-CRIT-002:** Detects "Ghost File" anti-pattern (no title = invisible to AI).
- **CRITICAL:** Without H1, document has no identity; all processing fails.
- **Visible in all tiers:** Structural errors always show up in pass/fail (Tier 1) and diagnostics (Tier 2).

### 6.3 Example 3: L2 Content Quality (W003: Link Missing Description)

```yaml
- rule_id: DS-RC-W003
  name: "Link Missing Description"
  description: "Every link must have descriptive anchor text (not bare URL)."
  diagnostic_codes: ["W003"]
  anti_patterns: []
  validation_level: 2
  pipeline_stage: 2
  implemented_in: "docstratum.pipeline.per_file_validator.validate_link_descriptions"
  depends_on: ["DS-RC-E006"]
  asot_path: "criteria/content/DS-VC-CNT-003-link-descriptions.md"
  status: "RATIFIED"
  output_tiers: [2, 3, 4]
  tags: ["content", "navigation", "ai-comprehension"]
  remediation_template_key: "W003"
  score_dimension: "CONTENT"
  effort_default: null
  priority_default: "HIGH"
  research_evidence: "v0.0.4a: Bare URLs force AI agents to guess link purpose. Strong correlation (r≈0.52) with navigation success."
```

**Rationale:**
- **L2 (Content):** Functional but not optimized. Link works but lacks context.
- **Depends on E006:** Must validate links exist before checking descriptions.
- **effort_default: null:** Effort varies wildly: 1 bare link = QUICK_WIN, 50 bare links = MODERATE.
- **output_tiers [2,3,4]:** Not critical enough for Tier 1 (pass/fail), but essential for playbook (Tier 3).
- **HIGH priority:** Research shows measurable impact on LLM comprehension (strong correlation).
- **Visibility:** Playbooks (Tier 3) group these as "Add descriptions to N bare links" action item.

### 6.4 Example 4: L3 Best Practices (W009: No Master Index)

```yaml
- rule_id: DS-RC-W009
  name: "No Master Index"
  description: "Add a Master Index section listing all top-level sections and files for navigation."
  diagnostic_codes: ["W009"]
  anti_patterns: ["AP-STR-003"]
  validation_level: 3
  pipeline_stage: 2
  implemented_in: "docstratum.pipeline.per_file_validator.validate_master_index"
  depends_on: ["DS-RC-E001"]
  asot_path: "canonical/DS-CN-001-master-index.md"
  status: "RATIFIED"
  output_tiers: [2, 3, 4]
  tags: ["structural", "navigation", "ai-comprehension", "ecosystem-recommended"]
  remediation_template_key: "W009"
  score_dimension: "CONTENT"
  effort_default: "MODERATE"
  priority_default: "HIGH"
  research_evidence: "v0.0.4a: 87% vs 31% LLM success rate with vs without Master Index. Single highest-impact structural addition."
```

**Rationale:**
- **L3 (Best Practices):** Optional by spec, but research-backed best practice.
- **Highest research backing:** 87% vs 31% success rate is the strongest evidence in the framework.
- **effort_default: MODERATE:** Creating a well-structured index takes hours, not minutes.
- **ecosystem-recommended tag:** Playbooks may recommend this for multi-file ecosystems.
- **score_dimension: CONTENT:** Adds value by improving comprehension, not by fixing structure.

### 6.5 Example 5: L4 DocStratum Extended (I001: No LLM Instructions)

```yaml
- rule_id: DS-RC-I001
  name: "No LLM Instructions"
  description: "Add [llm] instructions block at end of file with system prompt, constraints, and examples."
  diagnostic_codes: ["I001"]
  anti_patterns: []
  validation_level: 4
  pipeline_stage: 2
  implemented_in: "docstratum.pipeline.per_file_validator.validate_llm_instructions"
  depends_on: ["DS-RC-E001"]
  asot_path: "canonical/DS-CN-002-llm-instructions.md"
  status: "RATIFIED"
  output_tiers: [2, 3, 4]
  tags: ["docstratum-extended", "ai-optimization", "optional", "high-impact"]
  remediation_template_key: "I001"
  score_dimension: null
  effort_default: "STRUCTURAL"
  priority_default: "HIGH"
  research_evidence: "v0.0.2: 0% current adoption but strongest estimated quality differentiator. Elevated from INFO to HIGH priority based on impact modeling."
```

**Rationale:**
- **L4 (DocStratum Extended):** Three-layer architecture (standard, code examples, LLM instructions).
- **score_dimension: null:** Informational code; doesn't fit standard scoring dimensions, but estimated to be highest-impact feature.
- **effort_default: STRUCTURAL:** Creating good LLM instructions requires significant thought and testing.
- **HIGH priority despite INFO severity:** Remediation Framework elevates this based on impact evidence, not severity.
- **zero current adoption:** Highlights that this is aspirational/forward-looking.

### 6.6 Example 6: Ecosystem Validation (E009: No Index File)

```yaml
- rule_id: DS-RC-E009
  name: "No Index File"
  description: "Ecosystem must have a top-level llms.txt file as entry point. Index file missing or not named correctly."
  diagnostic_codes: ["E009"]
  anti_patterns: ["AP-CRIT-001"]
  validation_level: 1
  pipeline_stage: 4
  implemented_in: "docstratum.pipeline.ecosystem_validator.validate_index_file"
  depends_on: []
  asot_path: "diagnostics/errors/DS-DC-E009-NO_INDEX_FILE.md"
  status: "RATIFIED"
  output_tiers: [1, 2, 3, 4]
  tags: ["ecosystem", "structural", "entry-point"]
  remediation_template_key: "E009"
  score_dimension: "COVERAGE"
  effort_default: "QUICK_WIN"
  priority_default: "CRITICAL"
  research_evidence: "v0.0.7: No entry point = ecosystem is invisible to AI agents. Core structural requirement."
```

**Rationale:**
- **L1 (Structural) + Pipeline Stage 4 (Ecosystem):** Different from per-file L1 checks. Runs after all files are discovered.
- **No depends_on:** Ecosystem checks run after per-file validation, so they don't depend on specific per-file rules.
- **CRITICAL + QUICK_WIN:** Either the index exists or it doesn't (binary check), and creating one is fast.
- **score_dimension: COVERAGE:** Ecosystem dimension (not per-file quality dimension).
- **Visible in all tiers:** Missing index blocks entire ecosystem validation.

---

## 7. Anti-Pattern Registry Consistency Review

### 7.1 Cross-Reference Mapping

The Rule Registry's `anti_patterns` field cross-references `ANTI_PATTERN_REGISTRY` using `AntiPatternID` enum values. This section confirms naming conventions align.

#### Anti-Pattern ID Format

`ANTI_PATTERN_REGISTRY` (in `constants.py`) defines anti-patterns with IDs like:

```python
class AntiPatternID(StrEnum):
    AP_CRIT_001 = "AP-CRIT-001"  # Ghost File
    AP_CRIT_002 = "AP-CRIT-002"  # Monolith Monster
    AP_STR_001 = "AP-STR-001"    # Orphaned Subtree
    # ... etc
```

The enum **value** (e.g., `"AP-CRIT-001"`) is what appears in the Rule Registry's `anti_patterns` lists. The enum **name** (e.g., `AP_CRIT_001`) is for Python code.

#### Anti-Pattern Coverage

All 28 anti-patterns from `ANTI_PATTERN_REGISTRY` must appear in at least one rule's `anti_patterns` list. Mapping:

| Anti-Pattern | Detected By Rule | Rationale |
|--------------|-----------------|-----------|
| AP-CRIT-001 (Ghost File) | DS-RC-E007 (Empty File) | Empty files are the primary ghost file indicator |
| AP-CRIT-002 (No Identity) | DS-RC-E001 (No H1 Title) | Missing H1 prevents document identification |
| AP-CRIT-003 (Orphaned Subtree) | DS-RC-E010 (Orphaned File) | Ecosystem-level: file exists but not linked |
| AP-CRIT-004 (Inaccessible) | DS-RC-E006 (Broken Links) | Broken links make content unreachable |
| AP-STR-001 (Section Soup) | DS-RC-W002 (Non-Canonical) | Inconsistent structure is main symptom |
| AP-STR-002 (Unclear Hierarchy) | DS-RC-W002 (Non-Canonical) | Non-canonical names indicate unclear hierarchy |
| AP-STR-003 (No Wayfinding) | DS-RC-W009 (No Master Index) | Master Index is explicit wayfinding |
| AP-QUA-001 (Content Redundancy) | DS-RC-W017 (Redundant Content) | Direct detection |
| AP-QUA-002 (Incomplete Examples) | DS-RC-W004 (No Code Examples) | Code examples are completeness indicator |
| AP-QUA-003 (Poor Link Descriptions) | DS-RC-W003 (Link Missing Description) | Direct detection |
| AP-QUA-004 (Unversioned) | DS-RC-W016 (Inconsistent Versioning) | Version metadata indicates versioning practice |
| AP-QUA-005 (Context Loss) | DS-RC-W006 (Formulaic Descriptions) | Formulaic text loses context |
| AP-QUA-006 (Stale Content) | DS-RC-W016 (Inconsistent Versioning) | Version drift indicates staleness |
| AP-ECO-001 (No Coherence) | DS-RC-W015 (Inconsistent Project Name) | Project name consistency is coherence indicator |
| AP-ECO-002 (Token Waste) | DS-RC-W010 (Token Budget Exceeded) | Excess tokens indicate waste |
| AP-ECO-003 (Poor Coverage) | DS-RC-E009 (No Index File) | Index presence indicates good coverage |
| AP-ECO-004 (Fragmentation) | DS-RC-W012 (Broken Cross-File Link) | Broken cross-file links indicate fragmentation |
| AP-ECO-005 (No Aggregation) | DS-RC-W013 (Missing Aggregate) | Direct detection |
| ... (10 more) | ... | ... |

### 7.2 CHECK-NNN to Rule Mapping

The `ANTI_PATTERN_REGISTRY` includes a `check_id` field (e.g., `CHECK-001`) that maps to implementation. The Rule Registry replaces this with `implemented_in` field (module path). Consistency check:

**For each anti-pattern with check_id:**
- The check_id references an old implementation location
- The Rule Registry provides the new location
- Both should detect the same anti-pattern

Example:
```python
# ANTI_PATTERN_REGISTRY
AntiPatternEntry(
    AntiPatternID.AP_CRIT_001,
    "Ghost File",
    AntiPatternCategory.CRITICAL,
    "Empty or placeholder file with no substantive content.",
    check_id="CHECK-001",
    asot_path="anti-patterns/critical/DS-AP-CRIT-001-ghost-file.md"
)

# Rule Registry (new)
- rule_id: DS-RC-E007
  name: "Empty File"
  anti_patterns: ["AP-CRIT-001"]
  implemented_in: "docstratum.pipeline.per_file_validator.validate_empty_file"
  # check_id is no longer needed; implemented_in is more precise
```

### 7.3 Consistency Assertions

The registry's `assert_integrity()` method includes checks:

**Assert 4:** Every anti-pattern in `rule.anti_patterns` exists in `ANTI_PATTERN_REGISTRY`

**Assert 5:** Every anti-pattern in `ANTI_PATTERN_REGISTRY` appears in at least one `rule.anti_patterns`

These ensure 1:1 or M:1 mapping (multiple rules can detect same anti-pattern, but every anti-pattern is detected by at least one rule).

---

## 8. Design Decisions

### DECISION-027: YAML + Pydantic for Rule Registry Format

**Title:** Rule Registry Format: YAML + Pydantic vs. Python Module vs. Markdown Table

**Context:** The Rule Registry must be machine-readable, human-editable, schema-validated at load time, and version-controlled. Three formats were evaluated.

**Decision:** Use YAML for data (rule_registry.yaml in src/docstratum/) loaded into Pydantic models at engine startup.

**Rationale:**
- YAML is human-readable yet structured, suitable for ~100 entries with 20 fields each
- Pydantic provides schema validation, preventing invalid registries at load time
- Team members can edit YAML without Python knowledge
- Same pattern as remediation_templates.yaml (DECISION-025)
- Load-time validation catches errors immediately, not in production
- YAML is version-control friendly (clean diffs, reviewable PRs)

**Alternatives Rejected:**
- Python module: Requires code knowledge, harder to review as data
- Markdown table: No schema validation, poor expressiveness for nested fields

**Implementation:**
- File: `src/docstratum/rule_registry.yaml`
- Loader: `pydantic_yaml.parse_file_as(RuleRegistry, path)`
- Validation: `RuleRegistry.assert_integrity()` at Stage 1 startup
- Error handling: If validation fails, engine refuses to start (loud failure)

**Implications:**
- No breaking changes to Python source for registry updates
- Profile specs (D4) can reference rules by tag without recompilation
- Report Generation Stage (D5) queries registry at runtime for tier visibility

**Status:** ACTIVE (as of 2026-02-09)

---

### DECISION-028: Rule Registry Extends DS-MANIFEST, Does Not Replace

**Title:** Rule Registry Relationship to DS-MANIFEST: Extends vs. Replaces vs. Parallel

**Context:** DocStratum maintains two registries: DS-MANIFEST (authoritative specifications) and the new Rule Registry (implementation mapping). The relationship between them must be clear to prevent confusion and duplication.

**Decision:** Rule Registry **extends** DS-MANIFEST. Manifest owns specifications; registry owns implementation.

**Rationale:**
- **Separation of concerns:** What/why (manifest) vs. how/where (registry)
- **No duplication:** Registry references manifest via `asot_path`, no data duplication
- **Single source of truth:** Each type of information has one owner
- **Future-proof:** Future tools consuming llms.txt standards only need manifest, not registry
- **Natural evolution:** Manifest is stable (ratified), registry evolves with implementation

**Why Not Replace:**
- Confuses specification design (ASoT concern) with implementation engineering (engine concern)
- Would require registry to include all specification details (standards design rationale, examples, etc.), making it bloated
- ASoT should be independent of any one implementation

**Why Not Parallel:**
- Massive maintenance burden: every change requires updates in both
- Silent failures: code changes without parallel registry update
- Violates DRY principle

**Contract:**
- Every Rule Registry entry **must** have valid `asot_path` to manifest artifact
- Registry `status` field tracks implementation maturity, not specification maturity
- Manifest `status` is immutable; registry `status` can change as implementation matures

**Example:**
```
Rule ID: DS-RC-E001
Status: RATIFIED (implementation ready)
asot_path: criteria/structural/DS-VC-STR-001-h1-title-present.md
  └─ Points to DS-MANIFEST entry with Status: RATIFIED (spec is solid)

Rule ID: DS-RC-EXP-001 (experimental)
Status: DRAFT (under development)
asot_path: criteria/experimental/DS-VC-EXP-001-new-check.md
  └─ Points to DS-MANIFEST entry with Status: DRAFT (spec also under review)
```

**Status:** ACTIVE (as of 2026-02-09)

---

## 9. Open Questions for Downstream Deliverables

### Deliverable 4: Validation Profiles

1. **Rule reference in profiles:** Should profiles reference rules by `rule_id` (e.g., `DS-RC-E001`) or by `tags` (e.g., `@structural AND @quick-lint`)? Or both?
   - Recommendation: Both. `rule_ids` for explicit inclusion, `tags` for implicit composition.
   - Example: `{rules: ["DS-RC-E001"], tags: ["@quick-lint"]}`

2. **Tag-based rule filtering:** What tag syntax do profiles use?
   - Recommendation: Simple set operations: `@tag1 AND @tag2 NOT @tag3`

3. **Profile inheritance:** Can profiles extend other profiles?
   - Out of scope for this spec, but Rule Registry's tag system enables it.

### Deliverable 5: Report Generation Stage

4. **Registry queries at runtime:** Does Stage 6 query the registry to determine what data to include in reports?
   - Example: Tier 3 renderer asks "which rules have `output_tiers` including 3?" and includes only those.
   - Answer: Yes, highly likely. Registry enables dynamic output composition.

5. **Remediation template lookup:** How does Stage 6 map from diagnostic code (E001) to remediation template?
   - Recommendation: Use `remediation_template_key` field from registry.
   - Query: `rule for rule in registry.rules if "E001" in rule.diagnostic_codes` → use `rule.remediation_template_key`

6. **Score impact computation:** Should registry include per-rule score weights for easier impact calculation?
   - Current approach: Remediation Framework defines impacts; registry points to template.
   - Future enhancement: Add optional `estimated_score_impact: float` field?

### Deliverable 6: Scoring & Calibration

7. **Rule-level weight customization:** Can scoring profiles override rule weights?
   - Example: `strict` profile doubles weight of E-severity codes.
   - Registry enables this via `score_dimension` field.

8. **Score dimension hierarchies:** Do nested dimensions make sense for complex ecosystems?
   - Example: STRUCTURAL → {ENCODING, MARKDOWN, HEADERS}
   - Out of scope for this spec.

---

## 10. Backward Compatibility & Migration

### Current State (Before Registry)

Today, rule metadata is scattered:
- Diagnostic codes: `diagnostics.py` (DiagnosticCode enum)
- Implementation: Various validator modules
- Anti-patterns: `constants.py` (ANTI_PATTERN_REGISTRY)
- Remediation hints: diagnostics.py (Severity.remediation field)

### Migration Path

**Phase 1 (Immediate):** Create rule_registry.yaml by reverse-engineering existing code.

**Phase 2 (Parallel):** Both systems active; engine loads registry but doesn't require it yet.

**Phase 3 (Cutover):** Report Generation Stage (D5) uses registry by default. Old code paths deprecated.

**Phase 4 (Cleanup):** Remove scattered metadata from Python source; registry is sole source.

### Compatibility Notes

- Existing profiles (if any) should continue working during Phase 2
- Rule IDs are new; don't conflict with existing identifiers
- YAML file can be extended without breaking Python code

---

## 11. Closing

The Unified Rule Registry Design Specification completes the foundation layer's infrastructure specifications (Deliverables 1–3). It provides the metadata layer needed for Validation Profiles (D4) and Report Generation Stage (D5) to function reliably.

By centralizing rule metadata into a schema-validated, version-controlled registry, DocStratum achieves:

1. **Single source of truth** for rule definitions, implementations, dependencies, and consumption contracts
2. **Composability** — profiles can select rules by tag, not just hardcoded lists
3. **Traceability** — every rule points back to its authoritative standard (ASoT)
4. **Integrity** — load-time validation prevents misconfigurations
5. **Maintainability** — updates don't require code changes

The registry extends (does not replace) DS-MANIFEST, respecting the separation between specifications and implementation. Its YAML + Pydantic format balances human readability with machine validation, following established patterns in the project.

Next steps:
1. Create rule_registry.yaml with initial ~40 entries (diagnostic codes + ecosystem checks)
2. Implement RuleRegistry.assert_integrity() in validation infrastructure
3. Use registry in Profiles spec (D4) for tag-based rule composition
4. Query registry in Report Generation Stage (D5) for dynamic output tier filtering

---

## Appendix A: Registry Bootstrap Entries

A sample of the first entries to be created in rule_registry.yaml:

```yaml
version: "1.0.0"
rules:
  # L0: Encoding & Parsing
  - rule_id: DS-RC-E003
    name: "Invalid Encoding"
    description: "File must be valid UTF-8 encoded."
    diagnostic_codes: ["E003"]
    anti_patterns: []
    validation_level: 0
    pipeline_stage: 2
    implemented_in: "docstratum.pipeline.per_file_validator.validate_encoding"
    depends_on: []
    asot_path: "diagnostics/errors/DS-DC-E003-INVALID_ENCODING.md"
    status: "RATIFIED"
    output_tiers: [1, 2, 3, 4]
    tags: ["structural", "encoding", "quick-lint"]
    remediation_template_key: "E003"
    score_dimension: "STRUCTURAL"
    effort_default: "QUICK_WIN"
    priority_default: "CRITICAL"
    research_evidence: null

  - rule_id: DS-RC-E005
    name: "Invalid Markdown"
    description: "File must be valid Markdown syntax."
    diagnostic_codes: ["E005"]
    anti_patterns: []
    validation_level: 0
    pipeline_stage: 2
    implemented_in: "docstratum.pipeline.per_file_validator.validate_markdown_syntax"
    depends_on: ["DS-RC-E003"]
    asot_path: "diagnostics/errors/DS-DC-E005-INVALID_MARKDOWN.md"
    status: "RATIFIED"
    output_tiers: [1, 2, 3, 4]
    tags: ["structural", "parsing", "quick-lint"]
    remediation_template_key: "E005"
    score_dimension: "STRUCTURAL"
    effort_default: "QUICK_WIN"
    priority_default: "CRITICAL"
    research_evidence: null

  # L1: Structural
  - rule_id: DS-RC-E001
    name: "No H1 Title"
    description: "Every llms.txt file must begin with exactly one H1 title for identification."
    diagnostic_codes: ["E001"]
    anti_patterns: ["AP-CRIT-002"]
    validation_level: 1
    pipeline_stage: 2
    implemented_in: "docstratum.pipeline.per_file_validator.validate_h1_title"
    depends_on: ["DS-RC-E003", "DS-RC-E005"]
    asot_path: "criteria/structural/DS-VC-STR-001-h1-title-present.md"
    status: "RATIFIED"
    output_tiers: [1, 2, 3, 4]
    tags: ["structural", "identity", "quick-lint"]
    remediation_template_key: "E001"
    score_dimension: "STRUCTURAL"
    effort_default: "QUICK_WIN"
    priority_default: "CRITICAL"
    research_evidence: "v0.0.4a: H1 is document identity anchor for all downstream processing."

  # ... (additional entries for E002, E004, E006, E007, E008, E009, E010, etc.)

  # L2: Content
  - rule_id: DS-RC-W003
    name: "Link Missing Description"
    description: "Every link must have descriptive anchor text."
    diagnostic_codes: ["W003"]
    anti_patterns: ["AP-QUA-003"]
    validation_level: 2
    pipeline_stage: 2
    implemented_in: "docstratum.pipeline.per_file_validator.validate_link_descriptions"
    depends_on: ["DS-RC-E006"]
    asot_path: "criteria/content/DS-VC-CNT-003-link-descriptions.md"
    status: "RATIFIED"
    output_tiers: [2, 3, 4]
    tags: ["content", "navigation", "ai-comprehension"]
    remediation_template_key: "W003"
    score_dimension: "CONTENT"
    effort_default: null
    priority_default: "HIGH"
    research_evidence: "v0.0.4a: Strong correlation (r≈0.52) between link descriptions and navigation success."

  # L3: Best Practices
  - rule_id: DS-RC-W009
    name: "No Master Index"
    description: "Add a Master Index section listing all top-level sections and files."
    diagnostic_codes: ["W009"]
    anti_patterns: ["AP-STR-003"]
    validation_level: 3
    pipeline_stage: 2
    implemented_in: "docstratum.pipeline.per_file_validator.validate_master_index"
    depends_on: ["DS-RC-E001"]
    asot_path: "canonical/DS-CN-001-master-index.md"
    status: "RATIFIED"
    output_tiers: [2, 3, 4]
    tags: ["structural", "navigation", "ai-comprehension", "ecosystem-recommended"]
    remediation_template_key: "W009"
    score_dimension: "CONTENT"
    effort_default: "MODERATE"
    priority_default: "HIGH"
    research_evidence: "v0.0.4a: 87% vs 31% LLM success rate with vs without Master Index."

  # L4: DocStratum Extended
  - rule_id: DS-RC-I001
    name: "No LLM Instructions"
    description: "Add [llm] instructions block at end of file."
    diagnostic_codes: ["I001"]
    anti_patterns: []
    validation_level: 4
    pipeline_stage: 2
    implemented_in: "docstratum.pipeline.per_file_validator.validate_llm_instructions"
    depends_on: ["DS-RC-E001"]
    asot_path: "canonical/DS-CN-002-llm-instructions.md"
    status: "RATIFIED"
    output_tiers: [2, 3, 4]
    tags: ["docstratum-extended", "ai-optimization", "optional", "high-impact"]
    remediation_template_key: "I001"
    score_dimension: null
    effort_default: "STRUCTURAL"
    priority_default: "HIGH"
    research_evidence: "v0.0.2: Estimated strongest quality differentiator based on impact modeling."

  # Ecosystem Validation
  - rule_id: DS-RC-E009
    name: "No Index File"
    description: "Ecosystem must have a top-level llms.txt file as entry point."
    diagnostic_codes: ["E009"]
    anti_patterns: ["AP-CRIT-001"]
    validation_level: 1
    pipeline_stage: 4
    implemented_in: "docstratum.pipeline.ecosystem_validator.validate_index_file"
    depends_on: []
    asot_path: "diagnostics/errors/DS-DC-E009-NO_INDEX_FILE.md"
    status: "RATIFIED"
    output_tiers: [1, 2, 3, 4]
    tags: ["ecosystem", "structural", "entry-point"]
    remediation_template_key: "E009"
    score_dimension: "COVERAGE"
    effort_default: "QUICK_WIN"
    priority_default: "CRITICAL"
    research_evidence: "v0.0.7: No entry point = ecosystem is invisible to AI agents."

  # ... (additional entries for remaining codes)
```

---

**End of Specification**

*This specification is a DRAFT and subject to review before ratification. See the documentation backlog (RR-META-documentation-backlog.md) for implementation timeline.*
