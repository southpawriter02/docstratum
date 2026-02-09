# v0.1.3 — Validation Profiles & Module Composition Specification

> **Status:** DRAFT
> **Created:** 2026-02-09
> **Last Updated:** 2026-02-09
> **Governed By:** RR-META-documentation-backlog.md (Deliverable 4)
> **Depends On:** RR-SPEC-v0.1.3-output-tier-specification.md (Deliverable 1), RR-SPEC-v0.1.3-remediation-framework.md (Deliverable 2)
> **Feeds Into:** Deliverable 5 (Report Generation Stage), Deliverable 6 (Scoring Calibration)
> **ASoT Version:** 1.0.0
> **Traces To:** Output Tier Spec §4.3 (Default Formats by Profile), Remediation Framework §2.5 (Priority Override Mechanism), v0.2.4d §5.1 (.docstratum.yml Configuration)

---

## 1. Purpose

A **validation profile** is a named module composition that specifies which rule modules are active, what severity overrides apply, what pass/fail thresholds are enforced, and which output tier to produce. Profiles answer the question: "What does a successful validation look like for my use case?"

In the current pipeline (v0.0.7 ecosystem validation with v0.2.4d CLI), these concerns are scattered:

- The `.docstratum.yml` config file specifies a single `validation.level` (0–4) and `check_urls: true/false`
- The CLI has `--output-format` and `--verbose` flags
- There is no mechanism to:
  - Enable/disable specific diagnostic codes
  - Override severity or priority of individual diagnostics
  - Apply different output tiers to different contexts (CI vs. manual review)
  - Define named configurations for team reuse

This specification consolidates these concerns into a single, composable artifact: the **ValidationProfile**. A profile is a declarative specification of which rules are active and how they behave. The same rules can be combined into multiple profiles for different contexts: a "lint" profile for quick feedback, a "ci" profile for CI gates, a "full" profile for comprehensive analysis, and an "enterprise" profile for audience-adapted recommendations.

### 1.1 Core Insight: "The Buffet"

At the heart of the profile system is a simple idea: **module composition via tags**.

Each diagnostic rule in the Rule Registry (Deliverable 3) carries one or more tags: `"structural"`, `"content"`, `"ecosystem"`, `"experimental"`, etc. A validation profile specifies which tags to include and exclude. Rules matching included tags are active; rules matching excluded tags are inactive. This is the "buffet" model — a team walks through the metaphorical buffet line and picks which rule categories it wants to enforce.

An "inline profile" or "anonymous profile" is simply a buffet composition defined on the command line:

```bash
docstratum validate \
  --max-level 2 \
  --tags structural,content \
  --exclude-tags experimental
```

A "named profile" is the same composition stored in a file and referenced by name:

```bash
docstratum validate --profile lint
```

Profiles are not separate from the buffet model — **profiles are the buffet**, just with names and inheritance.

### 1.2 Relationship to Existing Artifacts

| Artifact | This Spec's Relationship |
|----------|-------------------------|
| `v0.2.4d` (.docstratum.yml) | This spec subsumes the old config format. A file with `validation.level: 3` and `check_urls: true` is equivalent to the `ci` profile. Backward compatibility is preserved via migration (§8). |
| `PipelineContext` in stages.py | This spec adds a new `profile: ValidationProfile \| None` field to PipelineContext. The orchestrator injects the loaded profile at the start of the run. |
| Rule Registry (Deliverable 3) | Profiles depend on the Rule Registry's `tags` field. Each rule must be tagged so that profile-level filtering works. |
| Output Tier Spec (Deliverable 1) | The `output_tier` field in a profile determines which tier the pipeline produces (Tier 1, 2, 3, or 4). |
| Remediation Framework (Deliverable 2) | Profiles can override the `priority` of any diagnostic code via `priority_overrides`. The profile's `grouping_mode` determines how remediation actions are organized. |
| Report Generation Stage (Deliverable 5) | Stage 6 reads `context.profile` to determine output format, grouping mode, and audience. |

---

## 2. ValidationProfile Pydantic Model Schema

### 2.1 Model Definition

```python
from pydantic import BaseModel, Field
from typing import Optional

class ValidationProfile(BaseModel):
    """A named module composition specifying which rules are active and how they behave.

    Attributes:
        profile_name: Human-readable identifier for this profile. Must be unique
                      within a project or user's profile directory. Examples:
                      "lint", "ci", "full", "enterprise", "project-strict", etc.
                      Used as a lookup key when loading by name.

        description: Human-readable explanation of the profile's purpose and intended
                     use case. Examples: "Quick single-file check", "CI/CD pipeline gate",
                     "Comprehensive analysis with remediation playbook". Displayed in
                     help text and report metadata.

        max_validation_level: Highest L0–L4 validation level to execute (0-4).
                              Filters which rules run based on their assigned level.
                              Rules with level > max_validation_level are skipped.
                              Example: max_validation_level=1 only runs L0–L1 checks.
                              Default: 4 (run all levels).

        enabled_stages: List of PipelineStageId values that should execute.
                        Stages not in this list are skipped by the orchestrator.
                        Examples:
                          [1, 2] — Discovery + Per-File only (quick single-file check)
                          [1, 2, 3, 4, 5] — Full pipeline minus report generation
                          [1, 2, 3, 4, 5, 6] — All stages including report generation
                        Empty list means no stages run (invalid, should error).
                        Stages: 1=Discovery, 2=Per-File, 3=Relationship,
                        4=Ecosystem, 5=Scoring, 6=Report Generation (planned).

        rule_tags_include: List of tag strings that activate rules. Rules matching
                           ANY of these tags are included (OR semantics).
                           Empty list = include all rules (unless excluded below).
                           Example: ["structural", "content"] includes all rules
                           tagged "structural" OR "content" (or both).
                           Tags are case-sensitive strings defined by Rule Registry.

        rule_tags_exclude: List of tag strings that deactivate rules. Rules matching
                           ANY of these tags are excluded, regardless of include list.
                           (Exclusion always wins.) Empty list = no exclusions.
                           Example: ["experimental", "docstratum-extended"] excludes
                           all rules tagged "experimental" or "docstratum-extended".
                           This is how we enforce "no bleeding-edge rules in CI".

        severity_overrides: Mapping of DiagnosticCode → overridden Severity.
                            Allows elevating W-severity diagnostics to E (ERROR),
                            or demoting E to W. Applies to matching diagnostics globally.
                            Example:
                              {"W012": "ERROR", "W009": "ERROR"}
                            Means: treat W012 (Broken Cross-File Link) and W009
                            (No Master Index) as ERROR severity instead of WARNING.
                            Keys are DiagnosticCode string values (e.g., "W012", "E001").
                            Values are Severity enum values ("ERROR", "WARNING", "INFO").

        priority_overrides: Mapping of DiagnosticCode → overridden Priority level.
                            Overrides the default priority assigned by the Remediation
                            Framework. Used to elevate W003 (Link Missing Description)
                            from HIGH to CRITICAL in ecosystem-strict contexts.
                            Example:
                              {"W003": "CRITICAL", "W012": "CRITICAL"}
                            Keys are DiagnosticCode string values.
                            Values are Priority enum values from Remediation Framework:
                            "CRITICAL", "HIGH", "MEDIUM", "LOW".

        pass_threshold: Minimum quality score (0–100) required to pass validation.
                        If total_score < pass_threshold, validation fails.
                        None = no threshold (always pass if severity constraints met).
                        Example: pass_threshold=50 means you must achieve 50+ points.
                        Used by CI profiles to enforce minimum quality bars.

        output_tier: Which output tier (1-4) to produce.
                     1 = Pass/Fail Gate (machine-readable, exit code only)
                     2 = Diagnostic Report (full diagnostic list, human-readable)
                     3 = Remediation Playbook (diagnostics + actionable remediation)
                     4 = Audience-Adapted (Tier 3 + role-specific recommendations)
                     See Output Tier Spec §2 for full definitions.

        output_format: Serialization format for the report.
                       Valid values: "json", "markdown", "yaml", "html", "terminal"
                       "terminal" = human-readable text (colorized ANSI if terminal)
                       "json" = machine-readable JSON
                       "markdown" = GitHub-flavored Markdown
                       "html" = standalone HTML page
                       "yaml" = YAML representation
                       Determines Stage 6 report renderer to use.

        grouping_mode: How to organize remediation action items (Tier 3).
                       Valid values: "by-priority", "by-level", "by-file", "by-effort"
                       "by-priority" = CRITICAL first, then HIGH, MEDIUM, LOW
                       "by-level" = L0 errors first, then L1, L2, L3, L4
                       "by-file" = Group actions by source file
                       "by-effort" = QUICK_WIN first, then MODERATE, COMPLEX, EPIC
                       Controls Stage 6's grouping logic for Tier 3 output.

        extends: Base profile name to inherit from (optional).
                 If specified, all fields from the base profile are copied,
                 then the extending profile's explicitly-set fields override them.
                 Only one level of inheritance allowed (no chaining).
                 Example: extends="ci" means inherit all fields from the "ci"
                 profile, then override any fields set in this profile.
                 None = no inheritance (all fields are independent).
    """

    profile_name: str = Field(
        ...,
        description="Human-readable identifier for this profile.",
        examples=["lint", "ci", "full", "enterprise", "ecosystem-strict"]
    )
    description: str = Field(
        ...,
        description="Explanation of the profile's purpose and use case.",
        examples=["Quick single-file check for rapid feedback"]
    )
    max_validation_level: int = Field(
        default=4,
        ge=0,
        le=4,
        description="Highest validation level (0-4) to execute."
    )
    enabled_stages: list[int] = Field(
        default=[1, 2, 3, 4, 5],
        min_items=1,
        description="Pipeline stage IDs to execute (1-5, or 1-6 with Stage 6)."
    )
    rule_tags_include: list[str] = Field(
        default_factory=list,
        description="Tags that activate rules (OR semantics). Empty = include all."
    )
    rule_tags_exclude: list[str] = Field(
        default_factory=list,
        description="Tags that deactivate rules (always wins over include)."
    )
    severity_overrides: dict[str, str] = Field(
        default_factory=dict,
        description="DiagnosticCode → overridden Severity mapping."
    )
    priority_overrides: dict[str, str] = Field(
        default_factory=dict,
        description="DiagnosticCode → overridden Priority mapping."
    )
    pass_threshold: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
        description="Minimum quality score to pass (None = no threshold)."
    )
    output_tier: int = Field(
        default=2,
        ge=1,
        le=4,
        description="Which output tier to produce (1-4)."
    )
    output_format: str = Field(
        default="terminal",
        description="Serialization format: json, markdown, yaml, html, or terminal."
    )
    grouping_mode: str = Field(
        default="by-priority",
        description="Remediation grouping: by-priority, by-level, by-file, or by-effort."
    )
    extends: Optional[str] = Field(
        default=None,
        description="Base profile name to inherit from (single level only)."
    )

    class Config:
        """Pydantic model config."""
        # Allow arbitrary string values (not just a fixed enum).
        # Tag vocabulary is freeform and defined by Rule Registry.
        use_enum_values = False
        validate_assignment = True
        json_encoders = {
            # Ensure enums serialize by value, not name
        }

    def validate_format(self) -> None:
        """Validate output_format is a known formatter.

        Raises:
            ValueError: If output_format is not in the allowed set.

        Design note: We validate at runtime (not via Pydantic validator)
        because formatters are registered by Stage 6, which may not exist
        at profile definition time. This allows third-party formatters to
        be added without modifying the profile schema.
        """
        valid_formats = {"json", "markdown", "yaml", "html", "terminal"}
        if self.output_format not in valid_formats:
            raise ValueError(
                f"output_format must be one of {valid_formats}, "
                f"got {self.output_format!r}"
            )

    def validate_grouping_mode(self) -> None:
        """Validate grouping_mode is recognized.

        Raises:
            ValueError: If grouping_mode is not valid for Tier 3 rendering.
        """
        valid_modes = {"by-priority", "by-level", "by-file", "by-effort"}
        if self.grouping_mode not in valid_modes:
            raise ValueError(
                f"grouping_mode must be one of {valid_modes}, "
                f"got {self.grouping_mode!r}"
            )

    def __post_init_post_parse__(self) -> None:
        """Run custom validation after Pydantic parsing.

        Checks output_format and grouping_mode, which have runtime
        dependencies on Stage 6 (not yet implemented).
        """
        self.validate_format()
        self.validate_grouping_mode()
```

### 2.2 Design Notes on Fields

**`max_validation_level` as a gating mechanism:** This field replaces the old `.docstratum.yml` `validation.level` field. It acts as a stage gate, not just a filter. If `max_validation_level=1`, the pipeline skips all L2+ checks, which saves execution time. If `max_validation_level=4`, all checks run.

**Empty `rule_tags_include` = include all:** This design avoids the need for a special "ALL_TAGS" pseudo-tag. An empty include list logically means "activate all tags" (whitelist nothing, so nothing is filtered at the tag level). The exclude list then carves out exceptions.

**Exclusion precedence:** `rule_tags_exclude` always wins. If a rule is tagged both `"structural"` and `"experimental"`, and the profile includes `"structural"` but excludes `"experimental"`, the rule is excluded. This prevents the "unintended bloat" problem where teams include a broad category and forget about the experimental rules hiding inside it.

**Severity vs. Priority overrides:** These are separate concerns. `severity_overrides` changes the Severity enum (ERROR, WARNING, INFO) — the classification of how broken a check is. `priority_overrides` changes the Priority (CRITICAL, HIGH, MEDIUM, LOW) from the Remediation Framework — how urgent the fix is. A profile might promote W009 (No Master Index) from WARNING severity to ERROR severity AND from HIGH priority to CRITICAL priority, making it a double-elevated issue in CI.

**Stage gating instead of `stop_after`:** The `enabled_stages` field replaces the old `stop_after` parameter in the orchestrator. Stages not in the list are skipped. This is more flexible than a linear stop point and aligns with the modular design of the pipeline.

---

## 3. Built-In Profiles (4 Profiles)

DocStratum ships with four built-in profiles covering the most common use cases. These are bundled with the package and available without any additional configuration.

### 3.1 Profile: `lint`

**Purpose:** Quick single-file check for rapid feedback during development.

**Audience:** Individual developers, pre-commit hooks, IDE integrations.

**Use Case:** "I want to catch obvious structural errors before I commit."

```python
ValidationProfile(
    profile_name="lint",
    description="Quick single-file check with structural validation only.",
    max_validation_level=1,          # L0-L1 only (parseable + structural)
    enabled_stages=[1, 2],            # Discovery + Per-File only (skip relationship/ecosystem)
    rule_tags_include=["structural"], # Only structural rules (no content/ecosystem)
    rule_tags_exclude=[],             # No exclusions
    severity_overrides={},            # No severity tweaks
    priority_overrides={},            # No priority tweaks
    pass_threshold=None,              # No score threshold (just check severity)
    output_tier=2,                    # Diagnostic Report (enough detail for a dev)
    output_format="terminal",         # Human-readable text
    grouping_mode="by-level",         # Group errors by L0/L1
    extends=None                      # No inheritance
)
```

**Rationale:**
- Executes only Stages 1–2 to avoid scanning cross-file relationships (slow).
- Filters to `"structural"` tag to skip content/ecosystem checks (developer doesn't care yet).
- `output_tier=2` gives enough detail (message, location, remediation) without overwhelming info.
- `grouping_mode="by-level"` sorts by validation level, which matches the developer's mental model of "fix structural first, then content."
- No `pass_threshold` because developers care about severity, not a score.

**Execution time:** ~200ms for a typical project (no ecosystem scan).

---

### 3.2 Profile: `ci`

**Purpose:** CI/CD pipeline gate for automated quality enforcement.

**Audience:** CI/CD systems (GitHub Actions, GitLab CI, Jenkins), merge gates, automated checks.

**Use Case:** "Should this PR merge? Is the documentation good enough?"

```python
ValidationProfile(
    profile_name="ci",
    description="CI/CD pipeline gate with ecosystem validation and quality threshold.",
    max_validation_level=3,                      # L0-L3 (parseable through best practices)
    enabled_stages=[1, 2, 3, 4, 5],             # Full pipeline, no report generation
    rule_tags_include=["structural", "content", "ecosystem"],  # Core rules only
    rule_tags_exclude=["experimental", "docstratum-extended"],  # No bleeding-edge
    severity_overrides={},                       # No severity tweaks
    priority_overrides={},                       # Use default priorities
    pass_threshold=50,                           # Must achieve 50+ score to pass
    output_tier=1,                               # Pass/Fail Gate (exit code only)
    output_format="json",                        # Machine-readable
    grouping_mode="by-priority",                 # (Unused for Tier 1, but set)
    extends=None                                 # No inheritance
)
```

**Rationale:**
- Executes all stages 1–5 to perform full ecosystem validation (catches cross-file issues).
- Includes core rule tags ("structural", "content", "ecosystem"), excludes experimental.
- `max_validation_level=3` skips L4 (DocStratum-extended) since not all teams use it yet.
- `pass_threshold=50` enforces a minimum quality bar (50% of max possible score).
- `output_tier=1` (Pass/Fail) means the consumer only gets a binary signal and exit code.
- `output_format="json"` for machine parsing (CI systems expect structured output).

**Exit code semantics:**
- `0` = documentation passed all checks and score ≥ 50
- `1` = structural errors (E001–E008)
- `2` = content errors (none in this case, as max_validation_level=3 doesn't run L4)
- `3` = best-practice warnings (L3)
- `4` = ecosystem errors (E009, E010)
- `5` = score < 50 (threshold not met)

**Execution time:** ~2–5 seconds for a typical project (includes ecosystem scan).

---

### 3.3 Profile: `full`

**Purpose:** Comprehensive validation with actionable remediation guidance.

**Audience:** Documentation teams, project maintainers, quality audits.

**Use Case:** "Show me everything broken and how to fix it."

```python
ValidationProfile(
    profile_name="full",
    description="Comprehensive validation with remediation playbook for all levels.",
    max_validation_level=4,                   # All levels (L0-L4 including DocStratum-extended)
    enabled_stages=[1, 2, 3, 4, 5, 6],       # Full pipeline including report generation
    rule_tags_include=[],                     # Empty = include all tags (whitelist all)
    rule_tags_exclude=[],                     # No exclusions (include experimental)
    severity_overrides={},                    # No overrides
    priority_overrides={},                    # Use defaults
    pass_threshold=None,                      # No threshold (always produce output)
    output_tier=3,                            # Remediation Playbook (actionable)
    output_format="markdown",                 # Rich formatting for human reading
    grouping_mode="by-priority",              # CRITICAL → HIGH → MEDIUM → LOW
    extends=None                              # No inheritance
)
```

**Rationale:**
- `max_validation_level=4` runs all checks, including L4 (concepts, few-shot examples, LLM instructions).
- Includes Stage 6 (Report Generation) to render a polished, actionable report.
- `rule_tags_include=[]` means all rules are activated (no filtering).
- `output_tier=3` (Remediation Playbook) provides action items with effort estimates and grouping.
- `output_format="markdown"` for rich formatting: headers, lists, code blocks, links.
- `grouping_mode="by-priority"` sorts fixes by impact (CRITICAL first, then HIGH, etc.).
- `pass_threshold=None` means the pipeline always produces a report (no early exit).

**Output example:** Markdown document with sections:
```
# Remediation Playbook for Project X
## CRITICAL (Must Fix Immediately)
### E001: No H1 Title
- **Affected files:** 2
- **Effort:** Quick Win (5 min)
- **Action:** Add `# Project Name` as the first line of each file.

### W009: No Master Index
- **Affected count:** 1 file
- **Effort:** Moderate (30 min)
- **Action:** Create a master index listing all pages with navigation.

## HIGH (Fix This Cycle)
...
```

**Execution time:** ~5–10 seconds for a typical project (includes report generation).

---

### 3.4 Profile: `enterprise`

**Purpose:** Audience-adapted recommendations for stakeholder reporting.

**Audience:** Leadership, product teams, compliance auditors, non-technical stakeholders.

**Use Case:** "Show me the quality of our documentation in business terms."

```python
ValidationProfile(
    profile_name="enterprise",
    description="Audience-adapted tier with business-focused recommendations and metrics.",
    max_validation_level=4,                   # All levels
    enabled_stages=[1, 2, 3, 4, 5, 6],       # Full pipeline with report generation
    rule_tags_include=[],                     # Include all tags
    rule_tags_exclude=[],                     # No exclusions
    severity_overrides={},                    # No overrides
    priority_overrides={},                    # Use defaults
    pass_threshold=None,                      # No threshold
    output_tier=4,                            # Audience-Adapted (role-specific)
    output_format="html",                     # Interactive HTML dashboard
    grouping_mode="by-priority",              # Same grouping as full
    extends="full"                            # Inherit from full, then override
)
```

**Rationale:**
- `extends="full"` means inherit all of the `full` profile's settings, then override specific fields.
- `output_tier=4` (Audience-Adapted) transforms Tier 3 output into business-focused language.
  - **For leadership:** "Your documentation quality score is 72/100. Here's what that means for user adoption."
  - **For product:** "API reference is 85% complete. You have X critical gaps blocking integrations."
  - **For compliance:** "All documentation meets regulatory requirements. Exceptions: Y."
- `output_format="html"` produces an interactive dashboard with charts, metrics, filtering.
- Intended for v0.4.x (not v0.1.3) — Tier 4 audiences and HTML rendering are future scope.

**Execution time:** ~10–15 seconds (includes report generation + audience adaptation).

---

## 4. Module Composition Semantics ("The Buffet")

This section defines the rule-filtering semantics that make the profile system work. It is the operational heart of the specification.

### 4.1 Tag Interaction: OR Semantics for Inclusion

**Rule:** A rule is **included** if its tags have **any overlap** with `rule_tags_include`.

**Definition:** For each rule in the Rule Registry with tags `T_rule`:

```
rule_included = (rule_tags_include == []) OR (T_rule ∩ rule_tags_include ≠ ∅)
```

In plain English:
- If `rule_tags_include` is empty, all rules are included (unless excluded below).
- If `rule_tags_include` is non-empty, a rule is included if **at least one** of its tags appears in the list.

**Example:** Profile specifies `rule_tags_include=["structural", "content"]`.

| Rule | Tags | Included? |
|------|------|-----------|
| E001: No H1 Title | `["structural"]` | YES (matches "structural") |
| W001: Missing Blockquote | `["structural"]` | YES (matches "structural") |
| W004: No Code Examples | `["content"]` | YES (matches "content") |
| W003: Link Missing Description | `["content", "navigation"]` | YES (matches "content") |
| I001: No LLM Instructions | `["docstratum-extended"]` | NO (doesn't match either) |

**Rationale for OR:** AND semantics would require a rule to have multiple tags simultaneously to activate, making broad categories impossible. OR semantics allow a team to say "enable all structural checks" without knowing which exact rules exist.

### 4.2 Exclusion Precedence: `rule_tags_exclude` Always Wins

**Rule:** If a rule's tags have **any overlap** with `rule_tags_exclude`, the rule is **excluded**, regardless of `rule_tags_include`.

**Definition:** For each rule with tags `T_rule`:

```
rule_excluded = T_rule ∩ rule_tags_exclude ≠ ∅
```

If `rule_excluded = True`, the rule does not run, period.

**Example:** Profile specifies:
```
rule_tags_include=["structural", "content", "ecosystem"]
rule_tags_exclude=["experimental"]
```

| Rule | Tags | Included? | Excluded? | Final? |
|------|------|-----------|-----------|--------|
| E001: No H1 Title | `["structural"]` | YES | NO | ✓ RUN |
| E011: Experimental Parser Check | `["structural", "experimental"]` | YES | YES | ✗ SKIP |
| W009: No Master Index | `["ecosystem"]` | YES | NO | ✓ RUN |
| I001: No LLM Instructions | `["docstratum-extended"]` | NO | NO | ✗ SKIP |

The rule "E011: Experimental Parser Check" is excluded even though it matches "structural" (included), because it also matches "experimental" (excluded). Exclusion wins.

**Rationale:** Teams often want to say "run almost everything, except these bleeding-edge rules." Exclusion precedence makes that easy without requiring an explicit allowlist of hundreds of stable rules.

### 4.3 Level Gating: `max_validation_level` as a Pipeline Filter

**Rule:** Rules with `level > max_validation_level` are skipped, regardless of tags.

**Definition:** For each rule with assigned `validation_level`:

```
rule_skipped_by_level = rule.validation_level > max_validation_level
```

**Example:** Profile specifies `max_validation_level=1` (L0–L1 only).

| Rule | Validation Level | Tag Match? | Level OK? | Final? |
|------|------------------|------------|-----------|--------|
| E001: No H1 Title | L0 | YES | YES | ✓ RUN |
| W001: Missing Blockquote | L1 | YES | YES | ✓ RUN |
| W004: No Code Examples | L2 | YES | NO | ✗ SKIP |
| W009: No Master Index | L3 | YES | NO | ✗ SKIP |
| I001: No LLM Instructions | L4 | YES | NO | ✗ SKIP |

The "lint" profile uses `max_validation_level=1` to skip L2–L4 checks, keeping execution time down. This is a **performance gate**, not a quality gate. It's checked before rules run, so the orchestrator doesn't even instantiate L2+ checks.

**Rationale:** Validation levels in DocStratum correspond to cumulative prerequisites (L0 before L1, L1 before L2, etc.). Skipping high levels is both a performance optimization and a clarity mechanism for different audiences.

### 4.4 Stage Gating: `enabled_stages` Skips Stages

**Rule:** Pipeline stages not in `enabled_stages` are skipped by the orchestrator.

**Definition:** For each stage with `stage_id`:

```
stage_executed = stage_id in enabled_stages
```

**Example:** Profile specifies `enabled_stages=[1, 2]`.

| Stage | ID | Enabled? | Action |
|-------|----|-----------|---------|
| Discovery | 1 | YES | ✓ Execute |
| Per-File | 2 | YES | ✓ Execute |
| Relationship | 3 | NO | ✗ Skip |
| Ecosystem | 4 | NO | ✗ Skip |
| Scoring | 5 | NO | ✗ Skip |

The "lint" profile skips stages 3–5 entirely, making it fast (no ecosystem scanning).

**Rationale:** Stages are computationally expensive (especially Stages 3–5 for large ecosystems). Profiles can opt out of expensive stages for quick feedback loops.

### 4.5 Combining All Filters: The Rule-Execution Decision Tree

A rule executes if **all** of these conditions are true:

```
1. Tag inclusion: T_rule ∩ rule_tags_include ≠ ∅  OR  rule_tags_include == []
2. Exclusion: NOT (T_rule ∩ rule_tags_exclude ≠ ∅)
3. Level: rule.validation_level ≤ max_validation_level
4. Stage: rule.pipeline_stage in enabled_stages
```

In pseudocode:

```python
def rule_executes(rule, profile):
    # Check tag inclusion
    tag_included = (
        profile.rule_tags_include == [] or
        bool(rule.tags & set(profile.rule_tags_include))
    )

    # Check exclusion (always overrides inclusion)
    tag_excluded = bool(rule.tags & set(profile.rule_tags_exclude))

    # Check level gating
    level_ok = rule.validation_level <= profile.max_validation_level

    # Check stage gating
    stage_ok = rule.pipeline_stage in profile.enabled_stages

    # All must be true
    return tag_included and not tag_excluded and level_ok and stage_ok
```

### 4.6 Inheritance: Single-Level with Field Override

**Rule:** A profile can inherit from a base profile via the `extends` field. All fields are copied from the base, then the extending profile's explicitly-set fields override them.

**Definition:** For each field `f` in the extending profile:

```
final_value(f) = value_from_extending_profile(f)
                 if f is explicitly set in extending_profile
                 else value_from_base_profile(f)
```

**Example:** `enterprise` extends `full`:

```python
# Base profile: full
profile_full = ValidationProfile(
    profile_name="full",
    ...
    output_tier=3,
    output_format="markdown",
    grouping_mode="by-priority",
    ...
)

# Extending profile: enterprise
profile_enterprise = ValidationProfile(
    profile_name="enterprise",
    extends="full",
    output_tier=4,              # Override
    output_format="html",       # Override
    # All other fields inherited from full
)

# Result after resolution:
profile_enterprise.max_validation_level  # Inherited: 4
profile_enterprise.enabled_stages        # Inherited: [1, 2, 3, 4, 5, 6]
profile_enterprise.output_tier           # Overridden: 4
profile_enterprise.output_format         # Overridden: "html"
```

**Restrictions:**
- Only one level of inheritance allowed (no chaining: `enterprise` extends `full` extends `ci`).
- The base profile must exist (either built-in or previously loaded from disk).
- Circular inheritance is not allowed (profile cannot extend itself, directly or indirectly).

**Rationale:** Single-level inheritance keeps the mental model simple. Complex inheritance chains become hard to debug when a field is overridden 3 levels up. If teams need complex sharing, they can generate profiles programmatically.

---

## 5. Custom Profile Loading and Discovery

This section defines how profiles are discovered and loaded at runtime. Profiles can come from multiple sources with explicit precedence rules.

### 5.1 Profile Discovery Order (Precedence from High to Low)

The orchestrator searches for profiles in this order, stopping at the first match:

1. **CLI flag: `--profile <path>`** (Highest precedence)
   - Direct path to a YAML/JSON profile file: `--profile ./my-profile.yaml`
   - CLI flags override individual fields of the loaded profile

2. **Project config: `.docstratum.yml` → `profiles:` section**
   - YAML mapping of profile name → configuration
   - Local to the project, checked into version control
   - Allows a team to define shared profiles

3. **User config: `~/.docstratum/profiles/` directory**
   - Directory of YAML/JSON files (one per profile)
   - User's home directory: `~/.docstratum/profiles/lint.yaml`
   - Allows per-developer customizations

4. **Built-in profiles: Shipped with package**
   - "lint", "ci", "full", "enterprise"
   - Lowest precedence
   - Always available

**Example resolution flow:**

```
User runs:
  docstratum validate --profile mystyle.yaml

Orchestrator searches:
  1. Load from --profile flag: ./mystyle.yaml (if exists) → ✓ FOUND, use it
     (Don't check other locations)

User runs:
  docstratum validate --profile ecosystem-strict

Orchestrator searches:
  1. --profile flag not provided (skip)
  2. .docstratum.yml → profiles.ecosystem-strict (if exists) → ✓ FOUND, use it
  3. (Don't check user config or built-in)

User runs:
  docstratum validate

Orchestrator searches:
  1. No --profile flag (use default "ci")
  2. .docstratum.yml → profiles.ci (if exists) → ✓ FOUND, use it
  3. ~/.docstratum/profiles/ci.yaml (if exists) → ✓ FOUND, use it
  4. Built-in "ci" profile → ✓ FOUND, use it
```

### 5.2 Default Profile

If no profile is specified and none is found, the orchestrator uses `"ci"` as the default. This matches the mental model of "CI is the safest, most restrictive mode."

```bash
docstratum validate  # Implicitly uses "ci" profile
```

Override the default by setting a profile in `.docstratum.yml`:

```yaml
# .docstratum.yml
default_profile: "full"  # All validation runs by default
```

### 5.3 Profile File Formats

Profiles are stored in YAML or JSON format (file extension determines format). The schema is the same as the Python `ValidationProfile` model.

**YAML Format (Recommended)**

```yaml
# lint.yaml
profile_name: "lint"
description: "Quick single-file check"
max_validation_level: 1
enabled_stages: [1, 2]
rule_tags_include:
  - "structural"
rule_tags_exclude: []
severity_overrides: {}
priority_overrides: {}
pass_threshold: null
output_tier: 2
output_format: "terminal"
grouping_mode: "by-level"
extends: null
```

**JSON Format (Machine-Generated)**

```json
{
  "profile_name": "lint",
  "description": "Quick single-file check",
  "max_validation_level": 1,
  "enabled_stages": [1, 2],
  "rule_tags_include": ["structural"],
  "rule_tags_exclude": [],
  "severity_overrides": {},
  "priority_overrides": {},
  "pass_threshold": null,
  "output_tier": 2,
  "output_format": "terminal",
  "grouping_mode": "by-level",
  "extends": null
}
```

### 5.4 Embedded Profiles in `.docstratum.yml`

Projects can define multiple named profiles inline in `.docstratum.yml`:

```yaml
# .docstratum.yml at project root

default_profile: "ci"

profiles:
  lint:
    description: "Quick check"
    max_validation_level: 1
    enabled_stages: [1, 2]
    rule_tags_include: ["structural"]
    # ... other fields use defaults

  ci:
    description: "CI gate"
    max_validation_level: 3
    enabled_stages: [1, 2, 3, 4, 5]
    rule_tags_include: ["structural", "content", "ecosystem"]
    rule_tags_exclude: ["experimental"]
    pass_threshold: 50
    output_tier: 1
    output_format: "json"

  full:
    description: "Full analysis"
    max_validation_level: 4
    enabled_stages: [1, 2, 3, 4, 5, 6]
    output_tier: 3
    output_format: "markdown"

  ecosystem-strict:
    extends: "ci"
    description: "Strict ecosystem validation"
    max_validation_level: 3
    rule_tags_include: ["structural", "content", "ecosystem"]
    rule_tags_exclude: ["docstratum-extended"]
    severity_overrides:
      W012: "ERROR"  # Broken cross-file link
      W009: "ERROR"  # No master index
    priority_overrides:
      W003: "CRITICAL"
      W012: "CRITICAL"
    pass_threshold: 70
    output_tier: 2
    output_format: "json"
    grouping_mode: "by-file"
```

### 5.5 CLI Flag Composition with Profiles

CLI flags allow inline overrides of a loaded profile's fields. A profile is loaded first, then CLI flags are applied on top.

```bash
# Load "ci" profile, then override output format
docstratum validate --profile ci --output-format markdown

# Load "ci", override level and tags
docstratum validate \
  --profile ci \
  --max-level 2 \
  --tags structural,content \
  --exclude-tags experimental,docstratum-extended

# Define an inline profile entirely via CLI flags
docstratum validate \
  --max-level 3 \
  --tags structural,ecosystem \
  --output-tier 2 \
  --output-format markdown
```

**Supported CLI Flags for Profile Overrides:**

| Flag | Maps To | Type | Example |
|------|---------|------|---------|
| `--max-level <int>` | `max_validation_level` | int (0-4) | `--max-level 2` |
| `--tags <csv>` | `rule_tags_include` | CSV string | `--tags structural,content` |
| `--exclude-tags <csv>` | `rule_tags_exclude` | CSV string | `--exclude-tags experimental` |
| `--output-tier <int>` | `output_tier` | int (1-4) | `--output-tier 3` |
| `--output-format <str>` | `output_format` | string | `--output-format json` |
| `--pass-threshold <int>` | `pass_threshold` | int (0-100) or null | `--pass-threshold 60` |

**Design note:** CLI flags are applied as field-level overrides, not full profile replacement. This allows `--profile ci --max-level 2` to load the "ci" profile and then lower the level, without re-specifying all other fields.

### 5.6 Profile Validation During Load

When a profile is loaded (from CLI, `.docstratum.yml`, or disk), the orchestrator validates:

1. All required fields are present (Pydantic validation).
2. `enabled_stages` is non-empty (at least one stage must run).
3. `output_format` is recognized (or warn about unknown formatters).
4. `grouping_mode` is valid (by-priority, by-level, by-file, by-effort).
5. If `extends` is specified, the base profile exists and loads successfully.
6. No circular inheritance (e.g., A extends B, B extends A).

Errors are reported with a clear message:

```
Error loading profile 'ecosystem-strict':
  - Field 'output_format' has invalid value 'ascii' (expected: json, markdown, yaml, html, terminal)
  - Base profile 'ci' not found in ~/.docstratum/profiles/ or .docstratum.yml
```

---

## 6. Integration with PipelineContext

The profile system integrates with the existing pipeline via a new field on `PipelineContext` and changes to the orchestrator's execution logic.

### 6.1 PipelineContext Extension

A new optional field is added to the `PipelineContext` model in `stages.py`:

```python
class PipelineContext(BaseModel):
    """Mutable context passed through all five pipeline stages.

    ... (existing docstring) ...

    Attributes:
        ... (existing fields) ...

        profile: The loaded validation profile for this run. Set by the
                 orchestrator before executing any stages. Stages read
                 profile.max_validation_level, profile.rule_tags_*,
                 profile.enabled_stages to filter which rules execute.
                 Used by Stage 6 to determine output format and grouping.
                 None in legacy single-file mode (backward compat).

    Traces to: Validation Profiles Spec §6 (Integration)
    """

    # ... (existing fields) ...

    profile: Optional[ValidationProfile] = Field(
        default=None,
        description="The loaded validation profile for this run."
    )
```

### 6.2 Orchestrator Flow with Profiles

The `EcosystemPipeline` orchestrator is modified to:

1. **Load the profile** before executing stages
2. **Inject the profile** into the context
3. **Use `enabled_stages`** to determine which stages to run
4. **Preserve backward compatibility** with the legacy `stop_after` parameter

```python
class EcosystemPipeline:
    """Orchestrator for the five-stage ecosystem validation pipeline.

    Modified to support profiles and stage filtering.
    """

    def run(
        self,
        root_path: str,
        profile: str | ValidationProfile | None = None,
        stop_after: int | None = None,  # Legacy parameter
    ) -> PipelineContext:
        """Execute the pipeline with profile-based filtering.

        Args:
            root_path: Project root directory to validate.
            profile: Profile name (e.g., "ci"), file path, or ValidationProfile object.
                     If None, uses default "ci" profile.
            stop_after: [Deprecated] Legacy parameter. If provided, overrides
                        profile.enabled_stages. For backward compatibility only.

        Returns:
            The final PipelineContext with all accumulated results.

        Flow:
            1. Load profile (from name, file, or use provided object)
            2. Create PipelineContext with profile injected
            3. For each stage in [1, 2, 3, 4, 5, 6]:
                 a. If stage.id not in profile.enabled_stages, skip
                 b. Execute stage(context)
                 c. If stage fails, handle error (log, skip subsequent stages, etc.)
            4. Return context
        """

        # Step 1: Load and normalize profile
        if isinstance(profile, str):
            # Profile is a name ("ci") or file path ("./my-profile.yaml")
            loaded_profile = self.load_profile(profile)
        elif isinstance(profile, ValidationProfile):
            # Profile object provided directly
            loaded_profile = profile
        else:
            # profile is None, use default
            loaded_profile = self.load_profile("ci")

        # Step 2: Handle legacy stop_after parameter
        if stop_after is not None:
            # stop_after overrides profile.enabled_stages
            # stop_after=2 means run stages 1-2
            loaded_profile.enabled_stages = list(range(1, stop_after + 1))

        # Step 3: Create context with profile injected
        context = PipelineContext(
            root_path=root_path,
            profile=loaded_profile,
        )

        # Step 4: Execute stages
        stages = self._build_stages()  # Stages 1-6 in order

        for stage in stages:
            # Check if stage is enabled
            if stage.stage_id not in loaded_profile.enabled_stages:
                # Log skip
                logger.info(f"Skipping stage {stage.stage_id} (not in enabled_stages)")
                context.stage_results.append(
                    StageResult(
                        stage=stage.stage_id,
                        status=StageStatus.SKIPPED,
                        message="Stage not in enabled_stages"
                    )
                )
                continue

            # Execute stage
            logger.info(f"Executing stage {stage.stage_id}...")
            try:
                result = stage.execute(context)
                context.stage_results.append(result)

                if result.status == StageStatus.FAILED:
                    logger.error(f"Stage {stage.stage_id} failed: {result.message}")
                    break  # Stop on first failure
            except Exception as e:
                logger.exception(f"Stage {stage.stage_id} raised exception: {e}")
                context.stage_results.append(
                    StageResult(
                        stage=stage.stage_id,
                        status=StageStatus.FAILED,
                        message=f"Exception: {e}"
                    )
                )
                break

        return context

    def load_profile(self, profile_spec: str) -> ValidationProfile:
        """Load a profile by name or file path.

        Args:
            profile_spec: Profile name ("ci", "full") or file path ("./my.yaml", "~/.docstratum/profiles/custom.yaml")

        Returns:
            Loaded ValidationProfile.

        Raises:
            FileNotFoundError: If profile not found in any source.
            ValueError: If profile is invalid (bad inheritance, etc.).
        """
        # Try as file path first
        if profile_spec.endswith(".yaml") or profile_spec.endswith(".json"):
            return self._load_profile_from_file(profile_spec)

        # Try as project config profile name
        project_config = self._load_docstratum_yml()
        if project_config and "profiles" in project_config:
            if profile_spec in project_config["profiles"]:
                return ValidationProfile(**project_config["profiles"][profile_spec])

        # Try as user config
        user_profile_path = Path.home() / ".docstratum" / "profiles" / f"{profile_spec}.yaml"
        if user_profile_path.exists():
            return self._load_profile_from_file(str(user_profile_path))

        # Try as built-in profile
        builtin_profiles = {
            "lint": self._builtin_lint_profile(),
            "ci": self._builtin_ci_profile(),
            "full": self._builtin_full_profile(),
            "enterprise": self._builtin_enterprise_profile(),
        }
        if profile_spec in builtin_profiles:
            return builtin_profiles[profile_spec]

        raise FileNotFoundError(
            f"Profile '{profile_spec}' not found. "
            f"Searched: CLI flag, .docstratum.yml, ~/.docstratum/profiles/, built-in profiles."
        )
```

### 6.3 Stage-Level Rule Filtering

Each pipeline stage (Stages 2–5) reads the profile to filter which rules it executes. The Per-File stage (Stage 2) is the primary consumer of the filtering logic:

```python
class PerFileValidationStage(PipelineStage):
    """Stage 2: Run L0–L4 single-file pipeline on each file."""

    def execute(self, context: PipelineContext) -> StageResult:
        """Run per-file validation, filtering rules by profile."""

        profile = context.profile  # Loaded by orchestrator
        assert profile is not None, "Profile must be injected by orchestrator"

        timer = StageTimer()
        timer.start()

        # For each file in context.files
        for file in context.files:
            # Get rules to execute for this file
            rules = self._get_active_rules(profile)

            # Run each rule
            for rule in rules:
                # Rule object has: code, validation_level, tags, pipeline_stage

                # Check: level gating
                if rule.validation_level > profile.max_validation_level:
                    continue

                # Check: tag inclusion
                tag_included = (
                    profile.rule_tags_include == [] or
                    bool(rule.tags & set(profile.rule_tags_include))
                )
                if not tag_included:
                    continue

                # Check: tag exclusion
                tag_excluded = bool(rule.tags & set(profile.rule_tags_exclude))
                if tag_excluded:
                    continue

                # All checks passed, execute rule
                result = rule.check(file)
                file.validation.diagnostics.append(result)

        # Apply severity overrides
        for diag in file.validation.diagnostics:
            if diag.code.value in profile.severity_overrides:
                diag.severity = Severity(profile.severity_overrides[diag.code.value])

        duration = timer.stop()
        return StageResult(
            stage=self.stage_id,
            status=StageStatus.SUCCESS,
            message=f"Validated {len(context.files)} files",
            duration_ms=duration,
        )

    def _get_active_rules(self, profile: ValidationProfile) -> list[Rule]:
        """Fetch all rules from Rule Registry."""
        # This is a placeholder. In the actual implementation,
        # this would query the Rule Registry (Deliverable 3).
        pass
```

### 6.4 Report Generation with Profile Directives

Stage 6 (Report Generation, planned for Deliverable 5) reads the profile to determine output format, grouping mode, and audience:

```python
class ReportGenerationStage(PipelineStage):
    """Stage 6: Generate formatted report output (future)."""

    def execute(self, context: PipelineContext) -> StageResult:
        """Render output based on profile's tier and format."""

        profile = context.profile
        assert profile is not None

        # Select renderer based on output_tier
        if profile.output_tier == 1:
            renderer = Tier1PassFailRenderer()
        elif profile.output_tier == 2:
            renderer = Tier2DiagnosticRenderer()
        elif profile.output_tier == 3:
            renderer = Tier3RemediationRenderer(grouping_mode=profile.grouping_mode)
        elif profile.output_tier == 4:
            renderer = Tier4AudienceAdaptedRenderer()

        # Select formatter based on output_format
        formatter = self._get_formatter(profile.output_format)

        # Render and format
        tier_output = renderer.render(context)
        formatted = formatter.format(tier_output)

        # Apply priority overrides (if Tier 3+)
        if profile.output_tier >= 3:
            self._apply_priority_overrides(formatted, profile.priority_overrides)

        return StageResult(
            stage=self.stage_id,
            status=StageStatus.SUCCESS,
            message=f"Generated {profile.output_format} report (tier {profile.output_tier})",
        )
```

---

## 7. Example Custom Profile: Buffet-Style Composition

Here is a complete, working example of a custom profile that demonstrates module composition ("the buffet"):

```yaml
# ecosystem-strict.yaml
# A custom profile for strict ecosystem validation with elevated standards.
#
# Use case: A team that publishes documentation with strict cross-file
# consistency requirements (e.g., API reference + guides must always
# link correctly and stay in sync).
#
# Run: docstratum validate --profile ecosystem-strict.yaml
#

profile_name: "ecosystem-strict"
description: |
  Strict ecosystem validation with elevated standards for cross-file
  links, navigation structure, and consistency. Designed for teams
  with multi-file documentation ecosystems that require high reliability.

extends: "ci"  # Start with the CI profile, then customize below

# Validation coverage: Run all checks up to L3 (best practices)
# This inherits from "ci" (max_validation_level: 3)
max_validation_level: 3

# Stages: Full pipeline (discover, per-file, relationships, ecosystem, scoring)
# This inherits from "ci" (enabled_stages: [1, 2, 3, 4, 5])
enabled_stages: [1, 2, 3, 4, 5]

# Rules: Include structural, content, and ecosystem rules
# Exclude experimental (bleeding-edge) and docstratum-extended (L4) rules
rule_tags_include:
  - "structural"      # E001–E008, W001–W008
  - "content"         # W004, W005, W006, W007
  - "ecosystem"       # E009, E010, W009, W012–W018

rule_tags_exclude:
  - "experimental"    # Don't run unstable rules
  - "docstratum-extended"  # Don't require L4 features yet

# Severity overrides: Elevate certain warnings to errors in ecosystem context
# These are the issues that matter most for multi-file consistency
severity_overrides:
  "W012": "ERROR"     # Broken cross-file link → ERROR (was WARNING)
  "W009": "ERROR"     # No Master Index → ERROR (was WARNING)
  "W003": "ERROR"     # Link missing description → ERROR (was WARNING)
  #
  # Rationale: In an ecosystem, broken links and missing descriptions
  # strand the AI agent. These are showstoppers, not best-practice nits.

# Priority overrides: Escalate critical ecosystem issues
# These define what the team tackles first in remediation
priority_overrides:
  "W003": "CRITICAL"  # Bare links are critical in ecosystem context
  "W012": "CRITICAL"  # Broken cross-file links are critical
  "W009": "CRITICAL"  # Master index absence is critical
  #
  # Rationale: Fix navigation first; everything else follows.

# Pass threshold: Must achieve 70/100 to pass
# (ci profile default is 50; we're stricter)
pass_threshold: 70

# Output: Tier 2 diagnostic report in JSON for CI consumption
output_tier: 2
output_format: "json"

# Grouping: Organize action items by source file
# (easier to coordinate fixes across a distributed team)
grouping_mode: "by-file"


# === Example Output ===
#
# When run on a typical project, ecosystem-strict produces:
#
# {
#   "profile": "ecosystem-strict",
#   "status": "FAILED",
#   "total_score": 52,
#   "passed": false,
#   "failure_reason": "Score 52 below threshold 70",
#   "errors": [
#     {
#       "code": "W012",
#       "file": "api-reference.md",
#       "line": 15,
#       "message": "Link to ../missing-page.md does not exist",
#       "severity": "ERROR",       # Overridden from WARNING
#       "remediation": "Fix the link target or remove the link"
#     },
#     {
#       "code": "W009",
#       "file": "llms.txt",
#       "line": -1,
#       "message": "No Master Index found",
#       "severity": "ERROR",       # Overridden from WARNING
#       "remediation": "Create a master index listing all files"
#     }
#   ],
#   "files_validated": 5,
#   "by_file": {
#     "llms.txt": {
#       "errors": ["W009"],
#       "warnings": []
#     },
#     "api-reference.md": {
#       "errors": ["W012"],
#       "warnings": ["W004"]
#     },
#     ...
#   }
# }
```

**How to use this profile:**

```bash
# Option 1: Store in .docstratum.yml
docstratum validate --profile ecosystem-strict

# Option 2: Store as a file
cp ecosystem-strict.yaml ~/.docstratum/profiles/
docstratum validate --profile ecosystem-strict

# Option 3: Use directly from file
docstratum validate --profile ./ecosystem-strict.yaml

# Option 4: Override a field on the command line
docstratum validate --profile ecosystem-strict --pass-threshold 80
```

---

## 8. Backward Compatibility with .docstratum.yml

The existing v0.2.4d `.docstratum.yml` format is subsumed by the profile system. Old config files are automatically migrated to equivalent profiles.

### 8.1 Legacy Config Format (v0.2.4d)

```yaml
# Old-style .docstratum.yml (v0.2.4d)
validation:
  level: 3
  check_urls: true
output:
  format: terminal
  verbose: false
```

### 8.2 Migration to Profiles

The orchestrator detects legacy config and converts it to a profile:

```python
def migrate_legacy_config(docstratum_yml: dict) -> ValidationProfile:
    """Migrate v0.2.4d config format to ValidationProfile."""

    validation_config = docstratum_yml.get("validation", {})
    output_config = docstratum_yml.get("output", {})

    legacy_level = validation_config.get("level", 3)
    check_urls = validation_config.get("check_urls", True)
    output_format = output_config.get("format", "terminal")

    # Map legacy level to profile
    if legacy_level == 0:
        return load_profile("lint")
    elif legacy_level == 1:
        return load_profile("lint")
    elif legacy_level == 2:
        return load_profile("ci")
    elif legacy_level == 3:
        return load_profile("ci")
    elif legacy_level == 4:
        return load_profile("full")

    # The "check_urls" field is implicit in the "ecosystem" tag
    # If check_urls: false, we exclude "ecosystem" rules
    # (Note: Not yet implemented; reserved for future use)
```

**Mapping:**

| v0.2.4d `level` | Equivalent Profile | Notes |
|---|---|---|
| `0` | `lint` | L0 only, structural focus |
| `1` | `lint` | L0–L1, structural focus |
| `2` | `ci` | L0–L2, ecosystem validation included |
| `3` | `ci` | L0–L3, ecosystem validation included |
| `4` | `full` | L0–L4, all features enabled |

### 8.3 Automatic Detection and Warning

If the orchestrator detects a legacy `.docstratum.yml`:

```
Warning: .docstratum.yml uses deprecated config format (v0.2.4d).
Migrating to profile system (v0.1.3+).

Old format:
  validation:
    level: 3
    check_urls: true

Equivalent profile:
  - name: "ci"
  - max_validation_level: 3
  - enabled_stages: [1, 2, 3, 4, 5]

Update your .docstratum.yml to use the new format to silence this warning.
See: https://docstratum.readthedocs.io/profiles/

For now, we'll use the "ci" profile. No changes to behavior.
```

### 8.4 New Config Format (Profiles)

Projects should update `.docstratum.yml` to use the new profile syntax:

```yaml
# New-style .docstratum.yml (v0.1.3+)
default_profile: "ci"

profiles:
  lint:
    description: "Quick check"
    max_validation_level: 1
    enabled_stages: [1, 2]
    rule_tags_include: ["structural"]

  ci:
    description: "CI gate"
    max_validation_level: 3
    enabled_stages: [1, 2, 3, 4, 5]
    rule_tags_include: ["structural", "content", "ecosystem"]
    rule_tags_exclude: ["experimental"]
    pass_threshold: 50
    output_tier: 1
    output_format: "json"

  full:
    description: "Full validation"
    max_validation_level: 4
    enabled_stages: [1, 2, 3, 4, 5, 6]
    output_tier: 3
    output_format: "markdown"
```

---

## 9. Design Decisions

### DECISION-029: Profiles Are Named Module Compositions (Not Separate)

**Decision:** A profile is not a separate layer on top of the buffet model. A profile IS a buffet composition with a name and optional inheritance. An inline profile defined via CLI is just an anonymous profile.

**Alternative Rejected:** Profiles as separate configuration objects, orthogonal to rule filtering.

**Rationale:** Simplicity. A single mental model (buffet of rules, aggregated into profiles) is easier to teach and implement than two separate systems. Profiles become a convenience for reuse, not a fundamental architectural layer.

**Trade-off:** Custom profiles must be written in YAML/JSON, not programmatically generated (unless the user writes code). This is acceptable since profiles are human-created configurations, not dynamic rule sets.

---

### DECISION-030: OR Semantics for Tag Inclusion (Not AND)

**Decision:** A rule is included if its tags have ANY overlap with `rule_tags_include`. We use OR, not AND, semantics.

**Alternative Rejected:** AND semantics — a rule must match ALL tags in the include list.

**Rationale:** OR makes it possible to activate broad categories ("enable all structural rules") without enumerating every rule. AND would require listing every rule individually, defeating the purpose of tagging.

**Trade-off:** It becomes impossible to say "only rules tagged BOTH 'structural' AND 'navigation'" using tag filters alone. If needed, such filtering can be added via rule-level configuration or explicit exclusions.

---

### DECISION-031: Single-Level Inheritance Only (No Chaining)

**Decision:** A profile can extend one base profile, but that base profile cannot extend another. No inheritance chains.

**Alternative Rejected:** Multi-level inheritance chains (A extends B extends C extends built-in "ci").

**Rationale:** Simplicity and debuggability. When a field is overridden, you know exactly which profile to check — the direct base. With chaining, you have to trace through multiple levels, which is error-prone.

**Trade-off:** Complex sharing requires generating profiles programmatically. Most teams won't hit this limit.

---

### DECISION-032: Profile Field Overrides Via CLI Are Shallow, Not Deep

**Decision:** CLI flags override individual top-level fields (e.g., `--max-level 2` overrides `max_validation_level`), not nested structures. You cannot do `--severity-overrides.W012=ERROR`.

**Alternative Rejected:** Deep merging of nested structures (e.g., dictionaries) via CLI.

**Rationale:** CLI argument parsing becomes complex and error-prone with nested overrides. Top-level field overrides are simple and cover most use cases.

**Trade-off:** For complex overrides, users must write a profile file instead of a CLI one-liner.

---

## 10. Open Questions for Downstream Deliverables

### Report Generation Stage (Deliverable 5)

1. **How does Stage 6 access the active profile?** Through `PipelineContext.profile` ✓ (answered in §6)
2. **Does Stage 6 need to validate that the profile's `output_tier` and `output_format` are compatible?** (e.g., Tier 4 only works with HTML, not JSON)
3. **How does Stage 6 handle profiles with `enabled_stages` that don't include Stage 6 itself?** (e.g., `enabled_stages=[1,2,3,4,5]` but the user asked for Tier 3 output)

### Scoring Calibration (Deliverable 6)

4. **Should profiles be able to override score dimension weights?** (e.g., "emphasize ecosystem health over content quality") Or is that scope for a future v0.2.x feature?
5. **How do `pass_threshold` and score override interact?** If a profile overrides priorities/severities, should the score recalibration be automatic?

### Rule Registry (Deliverable 3)

6. **Should the Rule Registry's `tags` vocabulary be formalized as an enum?** Or is freeform string-based tagging acceptable?
7. **What is the minimum set of tags every rule must have?** (e.g., all rules must be tagged "structural", "content", or "ecosystem", with optional "experimental"?)
8. **Can a rule have no tags?** (Probably not — it would be invisible to all profiles.)

### Configuration & Environment

9. **Should profiles support environment variable substitution?** (e.g., `pass_threshold: ${PASS_THRESHOLD:50}`)
10. **Should there be a way to globally disable certain tags across all profiles?** (e.g., a team-wide setting "no experimental rules")

---

## 11. Testing Strategy (Informational)

This section outlines the test coverage expected for the profile system, for use by Deliverable 6 and beyond.

### Unit Tests (Rule Filtering Logic)

- Tag inclusion (OR semantics)
- Tag exclusion (precedence over inclusion)
- Level gating (max_validation_level)
- Stage gating (enabled_stages)
- Combined decision tree (all four filters together)
- Inheritance (single level, base resolution)

### Integration Tests (Profile Loading)

- Load profile by name (built-in)
- Load profile by name (from `.docstratum.yml`)
- Load profile by name (from `~/.docstratum/profiles/`)
- Load profile by file path (absolute, relative)
- Load profile by file path (YAML, JSON)
- CLI flag overrides (--max-level, --tags, --exclude-tags, etc.)
- Inheritance resolution (extends field)
- Circular inheritance detection
- Missing base profile error
- Invalid YAML/JSON error

### End-to-End Tests (Pipeline Integration)

- Profile is injected into PipelineContext
- Stages respect enabled_stages
- Rules are filtered by profile
- Severity overrides are applied
- Priority overrides are used by Tier 3 renderer
- Exit code reflects profile's pass_threshold
- Report output format matches profile.output_format

### Backward Compatibility Tests

- v0.2.4d `.docstratum.yml` is migrated correctly
- Legacy `validation.level` maps to correct profile
- Legacy output.format maps to correct output_format
- Migration warning is logged

---

## 12. Glossary

| Term | Definition |
|------|-----------|
| **Buffet (Module Composition)** | The act of selecting which rule modules (tags) to activate and deactivate. A profile is a named buffet with optional overrides. |
| **Profile** | A named configuration artifact specifying which rules are active, what overrides apply, and what output to produce. |
| **Inline Profile** | An anonymous profile defined entirely via CLI flags (no name, not saved to disk). |
| **Named Profile** | A profile with a name, stored in a file or embedded in `.docstratum.yml`. |
| **Rule Tag** | A string label attached to diagnostic rules (e.g., "structural", "ecosystem", "experimental"). Used for filtering. |
| **Validation Level** | One of L0–L4. Represents cumulative stages of validation (Parseable → Structural → Content → Best Practices → DocStratum-Extended). |
| **Pipeline Stage** | One of the six stages (Discovery, Per-File, Relationship, Ecosystem, Scoring, Report Generation). Stages are executed in order and can be skipped. |
| **Severity Override** | A mapping of diagnostic code to severity (ERROR, WARNING, INFO), applied on top of the code's default severity. |
| **Priority Override** | A mapping of diagnostic code to priority (CRITICAL, HIGH, MEDIUM, LOW), applied on top of the Remediation Framework's default. |
| **Pass Threshold** | A minimum quality score (0–100) required to pass validation. If score < threshold, validation fails. |
| **Output Tier** | One of 1–4, representing the level of analysis and guidance (Pass/Fail → Diagnostic → Remediation → Audience-Adapted). |
| **Grouping Mode** | The organization strategy for remediation actions (by-priority, by-level, by-file, by-effort). |

---

## 13. References and Cited Documents

| Reference | Document | Notes |
|-----------|----------|-------|
| Output Tier Spec | RR-SPEC-v0.1.3-output-tier-specification.md | Defines the four output tiers (Tier 1–4) referenced by profile's `output_tier` field. |
| Remediation Framework | RR-SPEC-v0.1.3-remediation-framework.md | Defines the priority model and action items system referenced by `priority_overrides` and `grouping_mode`. |
| Rule Registry | RR-SPEC-v0.1.3-unified-rule-registry.md (Deliverable 3) | Defines the `tags` field on rules, which profiles consume. |
| Report Generation Stage | (Deliverable 5, future) | Stage 6 reads `PipelineContext.profile` to determine output format and audience. |
| Diagnostic Codes | docstratum/schema/diagnostics.py (source) | The 38 diagnostic codes (E001–E010, W001–W018, I001–I010) that can be filtered and overridden by profiles. |
| Pipeline Stages | docstratum/pipeline/stages.py (source) | Defines `PipelineStageId` (1–5) and `PipelineContext`. Profiles inject rules into the stage execution logic. |
| Legacy Config | v0.2.4d Pipeline Orchestration & Reporting (CHANGELOG.md) | Documents the old `.docstratum.yml` format that profiles replace. |

---

## 14. Revision History

| Version | Date | Change |
|---------|------|--------|
| v0.1.3 | 2026-02-09 | Initial specification. Defines ValidationProfile model, four built-in profiles (lint, ci, full, enterprise), module composition semantics, custom profile loading, and PipelineContext integration. |

---

## 15. Closing Statement

The validation profile system is the bridge between the diagnostic engine (38 diagnostic codes, 5 validation levels) and the end user. It answers the question: "Which of these checks matter to me, and what does success look like?"

By composing rules into named profiles, DocStratum empowers teams to:
- **Rapid feedback loops** via the "lint" profile (quick per-file checks)
- **CI/CD gates** via the "ci" profile (ecosystem-aware, threshold-based)
- **Comprehensive analysis** via the "full" profile (all checks, actionable remediation)
- **Stakeholder reporting** via the "enterprise" profile (audience-adapted language)

Profiles are composable, inheritable, and overridable, accommodating both standardized team practices and edge cases. The same rule set yields different behavior depending on context — a principle that scales from personal development workflows to organization-wide quality standards.

---

**End of Specification**
