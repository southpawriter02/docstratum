# v0.2.4e — Report Generation Stage Specification (Pipeline Stage 6)

> **Status:** DRAFT
> **Created:** 2026-02-09
> **Last Updated:** 2026-02-09
> **Governed By:** RR-META-documentation-backlog.md (Deliverable 5)
> **Depends On:** D1 (Output Tier Spec), D2 (Remediation Framework), D3 (Rule Registry), D4 (Profiles), v0.2.4d (Pipeline Orchestration)
> **Feeds Into:** Deliverable 6 (Ecosystem Scoring Calibration — indirectly)
> **ASoT Version:** 1.0.0
> **Traces To:** Output Tier Spec §3 (Pipeline Stage Mapping), v0.2.4d (Pipeline Orchestration)

---

## 1. Purpose

The Report Generation Stage (Stage 6) is the final synthesis point of the DocStratum validation pipeline. It is **architecturally distinct from stages 1–5** in a critical way: it adds no new validation logic. Instead, it is a **pure transformation layer** that takes the accumulated output of the prior five pipeline stages and formats it for the consumer based on the active validation profile's output tier and serialization format.

Stages 1–5 answer the question: "Is my documentation valid, and what needs to be fixed?"

Stage 6 answers the question: "How should I receive this answer—as a CI exit code, a detailed JSON report, a Markdown playbook, or an HTML presentation?"

This separation is intentional. It allows consumers to:

1. Run the same validation pipeline (Stages 1–5) once
2. Request multiple output formats without re-validation
3. Extend the system with new output formats without modifying validation logic
4. Compose output stages in various combinations with different profiles

### 1.1 Context from Output Tier Spec

The Output Tier Spec (Deliverable 1) defines four output tiers:

- **Tier 1** (Pass/Fail Gate) — CI/CD systems, exit code only
- **Tier 2** (Diagnostic Report) — Maintainers, full diagnostic list
- **Tier 3** (Remediation Playbook) — Teams, prioritized action plan
- **Tier 4** (Audience-Adapted Recommendations) — Enterprise, contextual guidance

This stage implements the pipeline interface that stages 1–5 feed into. It defines the renderer architecture for each tier and the serializer architecture for each format. Stage 6 ensures that every profile can request any valid (tier, format) combination from the compatibility matrix.

---

## 2. Stage 6 Interface

### 2.1 PipelineStageId Extension

The existing `PipelineStageId` IntEnum must be extended to include the Report Generation stage:

```python
# In pipelines/common.py or pipelines/models.py

from enum import IntEnum

class PipelineStageId(IntEnum):
    """Pipeline stage identifiers, in execution order."""
    DISCOVERY = 1              # Scan project root
    PER_FILE = 2               # Per-file validation (L0–L4)
    RELATIONSHIP = 3           # Extract links, classify, resolve
    ECOSYSTEM_VALIDATION = 4   # Cross-file validation
    SCORING = 5                # Ecosystem health scoring
    REPORT_GENERATION = 6      # Format output (new)
```

This ensures the stage has a canonical ID for use in `stage_results` lists, log messages, and configuration.

### 2.2 ReportGenerationStage Class

Define a new class conforming to the `PipelineStage` Protocol:

```python
# In pipelines/stages/report_generation_stage.py

from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import uuid

from pipelines.common import PipelineStage, PipelineContext, StageResult, PipelineStageId
from pipelines.models import ValidationProfile

@dataclass
class ReportArtifact:
    """The output of Stage 6: a formatted report."""
    tier: int                    # Output tier (1–4)
    format: str                  # Serialization format (json, markdown, yaml, html, terminal)
    content: str                 # The rendered artifact (JSON, Markdown, YAML, HTML text, or terminal-formatted string)
    metadata: "ReportMetadata"   # Report metadata for traceability

    def to_file(self, path: str) -> None:
        """Write artifact to file."""
        with open(path, 'w') as f:
            f.write(self.content)

    @property
    def is_stdout_format(self) -> bool:
        """Whether this format should be printed to stdout."""
        return self.format == 'terminal'


class ReportGenerationStage(PipelineStage):
    """
    Stage 6: Transform validated ecosystem data into a consumer-facing report.

    This stage:
    1. Reads profile from context.profile
    2. Determines output tier and format
    3. Selects appropriate tier renderer
    4. Selects appropriate format serializer
    5. Executes renderer → intermediate model
    6. Executes serializer → final artifact
    7. Stores result in context.report_artifact
    8. Returns a StageResult with success/failure status
    """

    def __init__(self):
        self.stage_id = PipelineStageId.REPORT_GENERATION

    @property
    def stage_id(self) -> PipelineStageId:
        """Return the stage ID."""
        return PipelineStageId.REPORT_GENERATION

    def execute(self, context: PipelineContext) -> StageResult:
        """
        Execute the report generation stage.

        Args:
            context: Pipeline context with all accumulated validation data

        Returns:
            StageResult with success/failure status and metadata
        """
        import time
        start_time = time.time()

        try:
            # Validate input
            if not context.profile:
                raise ValueError("PipelineContext.profile is required for Stage 6")

            # Extract tier and format from profile
            output_tier = context.profile.output_tier
            output_format = context.profile.output_format

            # Validate compatibility
            if not self._is_valid_combination(output_tier, output_format):
                raise ValueError(
                    f"Unsupported tier-format combination: "
                    f"Tier {output_tier} + {output_format} format"
                )

            # Generate metadata
            metadata = self._build_metadata(context, output_tier, output_format)

            # Get the appropriate renderer
            renderer = self._get_renderer(output_tier)

            # Render the intermediate data model
            intermediate = renderer.render(context)

            # Get the appropriate serializer
            serializer = self._get_serializer(output_format)

            # Serialize to final format
            serialized_content = serializer.serialize(intermediate, metadata)

            # Create the artifact
            artifact = ReportArtifact(
                tier=output_tier,
                format=output_format,
                content=serialized_content,
                metadata=metadata
            )

            # Store in context for downstream use
            context.report_artifact = artifact

            duration_ms = (time.time() - start_time) * 1000

            return StageResult(
                stage=self.stage_id,
                status="SUCCESS",
                diagnostics=[],
                duration_ms=duration_ms,
                message=f"Generated {output_format} report at Tier {output_tier}"
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return StageResult(
                stage=self.stage_id,
                status="FAILED",
                diagnostics=[str(e)],
                duration_ms=duration_ms,
                message=f"Report generation failed: {str(e)}"
            )

    def _is_valid_combination(self, tier: int, format_str: str) -> bool:
        """Check if this tier-format combination is valid per the Output Tier Spec."""
        # See §4.2 of Output Tier Spec for the compatibility matrix
        valid_combos = {
            1: ["json", "yaml", "terminal"],           # Tier 1
            2: ["json", "markdown", "yaml", "html", "terminal"],  # Tier 2
            3: ["json", "markdown", "html"],           # Tier 3
            4: ["json", "html"],                       # Tier 4
        }

        if tier not in valid_combos:
            return False

        return format_str in valid_combos[tier]

    def _build_metadata(self, context: PipelineContext, tier: int, format_str: str) -> "ReportMetadata":
        """Build report metadata for traceability."""
        return ReportMetadata(
            report_id=str(uuid.uuid4()),
            asot_version=context.asot_version or "1.0.0",
            engine_version=context.engine_version or "0.2.0",
            profile_name=context.profile.name,
            output_tier=tier,
            output_format=format_str,
            validated_at=datetime.utcnow().isoformat() + "Z",
            root_path=str(context.root_path),
            files_validated=len(context.files) if context.files else 0,
            stages_executed=[
                stage.name for stage in (context.stage_results or [])
                if stage.status in ["SUCCESS", "SKIPPED"]
            ],
            stages_skipped=[
                stage.name for stage in (context.stage_results or [])
                if stage.status == "SKIPPED"
            ],
            total_duration_ms=sum(
                stage.duration_ms for stage in (context.stage_results or [])
                if hasattr(stage, 'duration_ms')
            ) or 0.0,
            pass_threshold=getattr(context.profile, 'score_threshold', None)
        )

    def _get_renderer(self, tier: int) -> "TierRenderer":
        """Get the renderer for the specified tier."""
        renderer_class = TIER_RENDERERS.get(tier)
        if not renderer_class:
            raise ValueError(f"No renderer registered for Tier {tier}")
        return renderer_class()

    def _get_serializer(self, format_str: str) -> "FormatSerializer":
        """Get the serializer for the specified format."""
        serializer_class = FORMAT_SERIALIZERS.get(format_str)
        if not serializer_class:
            raise ValueError(f"No serializer registered for format '{format_str}'")
        return serializer_class()
```

### 2.3 PipelineContext Extension

Add the `report_artifact` field to `PipelineContext`:

```python
# In pipelines/models.py

from typing import Optional

class PipelineContext:
    # ... existing fields ...

    report_artifact: Optional[ReportArtifact] = None
    """The report artifact produced by Stage 6, if run."""
```

---

## 3. Report Metadata Schema

Every output artifact includes metadata for traceability. This schema is defined in the Output Tier Spec §5.1 and implemented here:

```python
# In pipelines/models.py

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ReportMetadata(BaseModel):
    """Metadata for all report artifacts."""

    report_id: str = Field(
        ...,
        description="Unique identifier for this report (UUID4)"
    )
    asot_version: str = Field(
        ...,
        description="ASoT version used for validation (semver)"
    )
    engine_version: str = Field(
        ...,
        description="DocStratum engine version (semver)"
    )
    profile_name: str = Field(
        ...,
        description="Validation profile name (e.g., 'lint', 'ci', 'full', 'enterprise')"
    )
    output_tier: int = Field(
        ...,
        ge=1, le=4,
        description="Output tier (1–4)"
    )
    output_format: str = Field(
        ...,
        description="Serialization format (json, markdown, yaml, html, terminal)"
    )
    validated_at: str = Field(
        ...,
        description="ISO 8601 timestamp when validation was performed"
    )
    root_path: str = Field(
        ...,
        description="Project root path or file path that was validated"
    )
    files_validated: int = Field(
        ...,
        ge=0,
        description="Number of files processed by the pipeline"
    )
    stages_executed: List[str] = Field(
        default_factory=list,
        description="Names of pipeline stages that executed successfully"
    )
    stages_skipped: List[str] = Field(
        default_factory=list,
        description="Names of pipeline stages that were skipped"
    )
    total_duration_ms: float = Field(
        ...,
        ge=0,
        description="Total pipeline execution time in milliseconds"
    )
    pass_threshold: Optional[int] = Field(
        default=None,
        description="Configured score threshold for pass/fail determination (None if not applicable)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "report_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "asot_version": "1.0.0",
                "engine_version": "0.2.4e",
                "profile_name": "full",
                "output_tier": 3,
                "output_format": "markdown",
                "validated_at": "2026-02-09T14:30:00Z",
                "root_path": "/home/user/project",
                "files_validated": 5,
                "stages_executed": ["DISCOVERY", "PER_FILE", "RELATIONSHIP", "ECOSYSTEM_VALIDATION", "SCORING"],
                "stages_skipped": [],
                "total_duration_ms": 2341.5,
                "pass_threshold": 50
            }
        }
```

---

## 4. Tier-Specific Renderers

Each tier has a renderer that transforms `PipelineContext` data into a tier-specific intermediate model.

### 4.1 TierRenderer Protocol

Define the common interface:

```python
# In pipelines/renderers/renderer_protocol.py

from typing import Protocol, Dict, Any

class TierRenderer(Protocol):
    """Protocol for tier-specific renderers."""

    def render(self, context: "PipelineContext") -> Dict[str, Any]:
        """
        Transform pipeline data into a tier-specific intermediate model.

        Args:
            context: Validated pipeline context

        Returns:
            A dictionary representing the tier's data model. Structure varies by tier.
        """
        ...
```

### 4.2 Tier 1 Renderer (Pass/Fail Gate)

The simplest renderer. Produces a flat structure with just the essential pass/fail signal:

```python
# In pipelines/renderers/tier1_renderer.py

from typing import Dict, Any
from pipelines.common import PipelineContext

class Tier1Renderer:
    """Render Tier 1 output: pass/fail gate with exit code."""

    def render(self, context: PipelineContext) -> Dict[str, Any]:
        """
        Produce Tier 1 output.

        Returns:
            {
                "passed": bool,                    # Did validation pass?
                "exit_code": int,                  # Exit code (0, 1, 2, 3, 4, 5, 10)
                "level_achieved": str,             # Highest L0–L4 level passed
                "total_score": int,                # Overall score (0–100)
                "grade": str,                      # Grade enum value
                "file_count": int,                 # Number of files validated
                "error_count": int,                # Total ERROR diagnostics
                "warning_count": int,              # Total WARNING diagnostics
            }
        """
        # Determine pass/fail based on profile threshold
        if context.ecosystem_score:
            total_score = context.ecosystem_score.total_score
        elif context.files and context.files[0].quality:
            total_score = context.files[0].quality.total_score
        else:
            total_score = 0

        pass_threshold = getattr(context.profile, 'score_threshold', 50)
        passed = total_score >= pass_threshold

        # Compute exit code (from Output Tier Spec §2.1.1)
        exit_code = self._compute_exit_code(context, passed)

        # Aggregate counts
        error_count = 0
        warning_count = 0
        for file_info in (context.files or []):
            if file_info.validation:
                error_count += file_info.validation.total_errors
                warning_count += file_info.validation.total_warnings

        # Add ecosystem-level diagnostics
        if context.ecosystem_diagnostics:
            for diag in context.ecosystem_diagnostics:
                if diag.severity == "ERROR":
                    error_count += 1
                elif diag.severity == "WARNING":
                    warning_count += 1

        return {
            "passed": passed,
            "exit_code": exit_code,
            "level_achieved": self._compute_level_achieved(context),
            "total_score": total_score,
            "grade": self._compute_grade(total_score),
            "file_count": len(context.files) if context.files else 0,
            "error_count": error_count,
            "warning_count": warning_count,
        }

    def _compute_exit_code(self, context: PipelineContext, passed: bool) -> int:
        """Compute exit code per Output Tier Spec §2.1.1."""
        if passed:
            return 0

        # Check for lowest-severity (highest-priority) error condition
        for file_info in (context.files or []):
            if file_info.validation:
                for diag in file_info.validation.diagnostics:
                    if diag.severity == "ERROR":
                        if diag.code.startswith("E00"):  # L0–L1 errors
                            return 1
                        elif diag.code.startswith("E0"):  # L2 errors
                            return 2

        # Check ecosystem errors
        if context.ecosystem_diagnostics:
            for diag in context.ecosystem_diagnostics:
                if diag.severity == "ERROR":
                    return 4

        # Check quality threshold
        if context.ecosystem_score and context.ecosystem_score.total_score < 50:
            return 5

        # Warnings only
        return 3

    def _compute_level_achieved(self, context: PipelineContext) -> str:
        """Return highest L0–L4 level where all checks pass."""
        if not context.files:
            return "L0"

        min_level = 4
        for file_info in context.files:
            if file_info.validation:
                min_level = min(min_level, file_info.validation.level_achieved)

        return f"L{min_level}"

    def _compute_grade(self, score: int) -> str:
        """Map score to letter grade."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
```

### 4.3 Tier 2 Renderer (Diagnostic Report)

Extends Tier 1 with full diagnostic list and breakdowns:

```python
# In pipelines/renderers/tier2_renderer.py

from typing import Dict, Any, List
from pipelines.common import PipelineContext
from pipelines.renderers.tier1_renderer import Tier1Renderer

class Tier2Renderer(Tier1Renderer):
    """Render Tier 2 output: diagnostic report with full issue details."""

    def render(self, context: PipelineContext) -> Dict[str, Any]:
        """
        Produce Tier 2 output (includes all Tier 1 data).

        Returns:
            {
                ...Tier 1 data...,
                "diagnostics": [                      # All diagnostics, sorted
                    {
                        "code": "E001",                # Diagnostic code
                        "severity": "ERROR",           # ERROR, WARNING, or INFO
                        "message": "...",              # Human-readable description
                        "remediation": "...",          # Brief fix suggestion
                        "line_number": 15,             # Source line (1-indexed)
                        "column": 1,                   # Source column (optional)
                        "context": "...",              # Source text snippet
                        "level": 1,                    # Validation level (L0–L4)
                        "check_id": "schema-01",       # Cross-reference to check
                        "source_file": "llms.txt",     # File that emitted this (ecosystem)
                        "related_file": None,          # Cross-file reference target (optional)
                    },
                    # ... more diagnostics ...
                ],
                "levels_passed": {                     # Per-level pass/fail
                    "L0": True,
                    "L1": True,
                    "L2": True,
                    "L3": True,
                    "L4": False,
                },
                "quality_dimensions": {...},          # Per-dimension scores (Tier 2 data)
                "ecosystem_dimensions": {...},        # Ecosystem health by dimension
                "per_file_scores": {...},             # Map of file → quality score
                "relationships": {...},               # Cross-file relationship graph
            }
        """
        # Start with Tier 1 data
        result = super().render(context)

        # Collect and sort all diagnostics
        all_diagnostics = []

        # Per-file diagnostics
        for file_info in (context.files or []):
            if file_info.validation and file_info.validation.diagnostics:
                for diag in file_info.validation.diagnostics:
                    all_diagnostics.append({
                        "code": diag.code,
                        "severity": diag.severity,
                        "message": diag.message,
                        "remediation": diag.remediation,
                        "line_number": diag.line_number,
                        "column": getattr(diag, 'column', None),
                        "context": diag.context[:500] if diag.context else None,
                        "level": diag.level,
                        "check_id": getattr(diag, 'check_id', None),
                        "source_file": file_info.file_path,
                        "related_file": None,
                    })

        # Ecosystem diagnostics
        for diag in (context.ecosystem_diagnostics or []):
            all_diagnostics.append({
                "code": diag.code,
                "severity": diag.severity,
                "message": diag.message,
                "remediation": getattr(diag, 'remediation', None),
                "line_number": None,
                "column": None,
                "context": None,
                "level": getattr(diag, 'level', 4),
                "check_id": getattr(diag, 'check_id', None),
                "source_file": getattr(diag, 'source_file', None),
                "related_file": getattr(diag, 'related_file', None),
            })

        # Sort: by file → severity → line number → code
        all_diagnostics = sorted(
            all_diagnostics,
            key=lambda d: (
                d.get("source_file") or "",
                {"ERROR": 0, "WARNING": 1, "INFO": 2}.get(d.get("severity"), 3),
                d.get("line_number") or 0,
                d.get("code") or "",
            )
        )

        result["diagnostics"] = all_diagnostics

        # Per-level pass/fail
        result["levels_passed"] = self._compute_levels_passed(context)

        # Quality dimensions
        if context.ecosystem_score:
            result["quality_dimensions"] = [
                {
                    "name": dim.name,
                    "score": dim.score,
                    "max_score": dim.max_score,
                    "percentage": dim.percentage,
                }
                for dim in context.ecosystem_score.dimensions
            ]
        else:
            result["quality_dimensions"] = []

        # Per-file scores
        if context.ecosystem_score:
            result["per_file_scores"] = context.ecosystem_score.per_file_scores or {}
        else:
            result["per_file_scores"] = {}

        # Relationships
        result["relationships"] = {
            "total": len(context.relationships) if context.relationships else 0,
            "broken": sum(
                1 for r in (context.relationships or [])
                if not r.is_resolved
            ),
        }

        return result

    def _compute_levels_passed(self, context: PipelineContext) -> Dict[str, bool]:
        """Determine which levels passed."""
        levels_passed = {f"L{i}": True for i in range(5)}

        for file_info in (context.files or []):
            if file_info.validation:
                for diag in file_info.validation.diagnostics:
                    if diag.severity == "ERROR":
                        # Determine which level this affects
                        if diag.code.startswith("E00"):
                            levels_passed["L0"] = False
                            levels_passed["L1"] = False
                        elif diag.code.startswith("E0"):
                            levels_passed["L2"] = False

        return levels_passed
```

### 4.4 Tier 3 Renderer (Remediation Playbook)

Extends Tier 2 with action items from the Remediation Framework:

```python
# In pipelines/renderers/tier3_renderer.py

from typing import Dict, Any, List
from pipelines.common import PipelineContext
from pipelines.renderers.tier2_renderer import Tier2Renderer
from pipelines.remediation import RemediationFramework
from pipelines.models import RemediationPlaybook

class Tier3Renderer(Tier2Renderer):
    """Render Tier 3 output: remediation playbook with prioritized action items."""

    def __init__(self):
        self.remediation_framework = RemediationFramework()

    def render(self, context: PipelineContext) -> Dict[str, Any]:
        """
        Produce Tier 3 output (includes all Tier 2 data).

        Returns:
            {
                ...Tier 2 data...,
                "executive_summary": "...",           # 2–3 sentence overview
                "action_items": [                      # Prioritized, grouped, sequenced
                    {
                        "priority": "CRITICAL",        # CRITICAL, HIGH, MEDIUM, LOW
                        "group_label": "Structural Fixes",
                        "description": "...",          # Expanded prose guidance
                        "affected_diagnostics": ["E001", "E002"],  # Which codes this resolves
                        "effort_estimate": "QUICK_WIN",  # QUICK_WIN, MODERATE, STRUCTURAL
                        "score_impact": 15,            # Estimated score increase
                        "dependency": None,            # Action ID this depends on
                    },
                    # ... more action items ...
                ],
                "score_projection": {                  # If all CRITICAL/HIGH actions done
                    "current_score": 47,
                    "projected_score": 72,
                    "improvement": 25,
                },
                "anti_patterns_detected": [            # Named anti-patterns found
                    {
                        "pattern_id": "GHOST_FILE",
                        "description": "...",
                        "severity": "HIGH",
                        "instances": 2,
                    },
                ],
            }
        """
        # Start with Tier 2 data
        result = super().render(context)

        # Generate playbook using Remediation Framework
        playbook = self.remediation_framework.generate_playbook(
            context=context,
            grouping_mode=getattr(context.profile, 'grouping_mode', 'by-priority'),
            ordering_mode=getattr(context.profile, 'action_ordering', 'by-dependency')
        )

        # Extract action items (format as per Remediation Framework)
        action_items = []
        for action in playbook.action_items:
            action_items.append({
                "priority": action.priority,
                "group_label": action.group_label,
                "description": action.description,
                "affected_diagnostics": list(action.affected_diagnostic_codes),
                "effort_estimate": action.effort_estimate,
                "score_impact": action.estimated_score_impact,
                "dependency": action.dependency_action_id,
            })

        result["action_items"] = action_items

        # Executive summary
        result["executive_summary"] = self._generate_executive_summary(
            context, playbook
        )

        # Score projection
        result["score_projection"] = {
            "current_score": int(result.get("total_score", 0)),
            "projected_score": playbook.projected_score_if_all_critical_high_completed,
            "improvement": (
                playbook.projected_score_if_all_critical_high_completed -
                int(result.get("total_score", 0))
            ),
        }

        # Anti-patterns
        result["anti_patterns_detected"] = [
            {
                "pattern_id": ap.pattern_id,
                "description": ap.description,
                "severity": ap.severity,
                "instances": ap.instance_count,
            }
            for ap in playbook.detected_anti_patterns
        ]

        return result

    def _generate_executive_summary(
        self,
        context: PipelineContext,
        playbook: RemediationPlaybook
    ) -> str:
        """Generate a 2–3 sentence overview of documentation health."""
        score = int(context.ecosystem_score.total_score) if context.ecosystem_score else 0
        grade = self._compute_grade(score)

        critical_count = sum(
            1 for a in playbook.action_items
            if a.priority == "CRITICAL"
        )
        high_count = sum(
            1 for a in playbook.action_items
            if a.priority == "HIGH"
        )

        return (
            f"This documentation ecosystem scores {score}/100 ({grade} grade) and has "
            f"{critical_count} critical and {high_count} high-priority issues to address. "
            f"Completing the CRITICAL and HIGH actions will improve the score to "
            f"~{playbook.projected_score_if_all_critical_high_completed}/100. "
            f"Focus on structural fixes before content enhancements."
        )
```

### 4.5 Tier 4 Renderer (Audience-Adapted Recommendations)

Stub for now; full implementation deferred to v0.4.x:

```python
# In pipelines/renderers/tier4_renderer.py

from typing import Dict, Any
from pipelines.common import PipelineContext
from pipelines.renderers.tier3_renderer import Tier3Renderer

class Tier4Renderer(Tier3Renderer):
    """
    Render Tier 4 output: audience-adapted recommendations (STUB for v0.2.4e).

    Full implementation deferred to v0.4.x pending:
    - Calibration specimen corpus (Deliverable 6)
    - Context profile schema validation
    - Comparative analysis engine
    - Domain-specific template library

    For v0.2.4e, Tier 4 output is functionally identical to Tier 3,
    with a note that Tier 4-specific features will be added in v0.4.x.
    """

    def render(self, context: PipelineContext) -> Dict[str, Any]:
        """
        Produce Tier 4 output (includes all Tier 3 data + context injection point).

        In v0.2.4e, this returns Tier 3 data with metadata marking Tier 4 availability.
        In v0.4.x, will overlay context_profile data to generate domain-specific guidance.
        """
        # For v0.2.4e, defer to Tier 3 and add a note about v0.4.x enhancement
        result = super().render(context)

        # Add marker for v0.4.x context profile injection
        result["_tier4_note"] = (
            "Tier 4 audience-adapted recommendations are deferred to v0.4.x. "
            "Full implementation pending calibration specimens and context profile schema. "
            "In v0.4.x, this report will include domain-specific guidance tailored to "
            "your industry, project type, and documentation goals."
        )

        return result
```

---

## 5. Format Serializers

Each format has a serializer that transforms the intermediate data model into a consumer-facing string.

### 5.1 FormatSerializer Protocol

Define the common interface:

```python
# In pipelines/serializers/serializer_protocol.py

from typing import Protocol, Dict, Any

class FormatSerializer(Protocol):
    """Protocol for format-specific serializers."""

    def serialize(
        self,
        data: Dict[str, Any],
        metadata: "ReportMetadata"
    ) -> str:
        """
        Serialize the intermediate model into a format-specific string.

        Args:
            data: Tier-specific intermediate data (from renderer)
            metadata: Report metadata

        Returns:
            Serialized string (JSON, Markdown, YAML, HTML, or terminal-formatted)
        """
        ...
```

### 5.2 JSON Serializer

Structured JSON output per Pydantic conventions:

```python
# In pipelines/serializers/json_serializer.py

import json
from typing import Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum

class JsonSerializer:
    """Serialize intermediate data to JSON format."""

    def serialize(self, data: Dict[str, Any], metadata: "ReportMetadata") -> str:
        """Serialize to pretty-printed JSON."""
        # Prepare the output structure
        output = {
            "metadata": metadata.model_dump(mode="json"),
            **data
        }

        # Remove internal fields (start with _)
        output = {k: v for k, v in output.items() if not k.startswith("_")}

        # Serialize with custom handler for non-serializable types
        return json.dumps(
            output,
            indent=2,
            default=self._json_default,
            sort_keys=False
        )

    @staticmethod
    def _json_default(obj: Any) -> Any:
        """JSON encoder for non-serializable types."""
        if isinstance(obj, datetime):
            return obj.isoformat() + "Z"
        elif isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, Enum):
            return obj.value
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return str(obj)
```

### 5.3 Markdown Serializer

Generates a CommonMark document with GFM tables:

```python
# In pipelines/serializers/markdown_serializer.py

from typing import Dict, Any
import re

class MarkdownSerializer:
    """Serialize intermediate data to Markdown format."""

    def serialize(self, data: Dict[str, Any], metadata: "ReportMetadata") -> str:
        """Serialize to Markdown with GFM tables."""
        output = []

        # Metadata as YAML frontmatter
        output.append("---")
        output.append(f"report_id: {metadata.report_id}")
        output.append(f"asot_version: {metadata.asot_version}")
        output.append(f"engine_version: {metadata.engine_version}")
        output.append(f"profile_name: {metadata.profile_name}")
        output.append(f"output_tier: {metadata.output_tier}")
        output.append(f"validated_at: {metadata.validated_at}")
        output.append("---\n")

        # Title and summary
        output.append("# DocStratum Validation Report\n")

        passed = data.get("passed", False)
        status = "✓ PASSED" if passed else "✗ FAILED"
        output.append(f"**Status**: {status}\n")
        output.append(f"**Score**: {data.get('total_score', 0)}/100 ({data.get('grade', 'F')})\n")

        if "executive_summary" in data:
            output.append(f"\n## Executive Summary\n\n{data['executive_summary']}\n")

        # Diagnostics table (Tier 2+)
        if "diagnostics" in data and data["diagnostics"]:
            output.append("\n## Issues Found\n\n")
            output.append("| File | Severity | Code | Message | Line |\n")
            output.append("|------|----------|------|---------|------|\n")

            for diag in data["diagnostics"][:50]:  # Limit to 50 for readability
                file_name = diag.get("source_file", "").split("/")[-1]
                severity = diag.get("severity", "INFO")
                code = diag.get("code", "")
                message = diag.get("message", "").replace("|", "\\|")[:60]
                line = diag.get("line_number", "—")

                output.append(
                    f"| {file_name} | {severity} | {code} | {message}... | {line} |\n"
                )

            if len(data["diagnostics"]) > 50:
                output.append(
                    f"\n*(and {len(data['diagnostics']) - 50} more issues)*\n"
                )

        # Action items (Tier 3+)
        if "action_items" in data and data["action_items"]:
            output.append("\n## Remediation Action Items\n\n")

            for i, action in enumerate(data["action_items"], 1):
                priority = action.get("priority", "MEDIUM")
                label = action.get("group_label", "Action")
                effort = action.get("effort_estimate", "MODERATE")
                impact = action.get("score_impact", 0)
                description = action.get("description", "")

                output.append(f"### {priority}: {label}\n\n")
                output.append(f"**Effort**: {effort} | **Score Impact**: +{impact} points\n\n")
                output.append(f"{description}\n\n")

        # Score projection (Tier 3+)
        if "score_projection" in data:
            proj = data["score_projection"]
            output.append(f"\n## Score Projection\n\n")
            output.append(
                f"- **Current**: {proj['current_score']}/100\n"
                f"- **Projected** (after CRITICAL & HIGH): {proj['projected_score']}/100\n"
                f"- **Improvement**: +{proj['improvement']} points\n"
            )

        # Metadata footer
        output.append(f"\n---\n\n")
        output.append(f"*Generated at {metadata.validated_at}*\n")
        output.append(f"*Engine version: {metadata.engine_version}*\n")

        return "".join(output)
```

### 5.4 YAML Serializer

Similar structure to JSON but in YAML syntax:

```python
# In pipelines/serializers/yaml_serializer.py

import yaml
from typing import Dict, Any

class YamlSerializer:
    """Serialize intermediate data to YAML format."""

    def serialize(self, data: Dict[str, Any], metadata: "ReportMetadata") -> str:
        """Serialize to YAML."""
        output = {
            "metadata": metadata.model_dump(mode="json"),
            **{k: v for k, v in data.items() if not k.startswith("_")}
        }

        return yaml.dump(
            output,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
            width=100
        )
```

### 5.5 Terminal Serializer

ANSI-colored output for terminal consumption:

```python
# In pipelines/serializers/terminal_serializer.py

from typing import Dict, Any

class TerminalSerializer:
    """Serialize intermediate data to colored terminal output."""

    COLORS = {
        "RESET": "\033[0m",
        "BOLD": "\033[1m",
        "GREEN": "\033[32m",
        "RED": "\033[31m",
        "YELLOW": "\033[33m",
        "BLUE": "\033[34m",
    }

    def serialize(self, data: Dict[str, Any], metadata: "ReportMetadata") -> str:
        """Serialize to terminal format with ANSI colors."""
        output = []

        # Header
        output.append(f"{self.COLORS['BOLD']}DocStratum Validation Report{self.COLORS['RESET']}\n")
        output.append(f"Profile: {metadata.profile_name} | Tier: {metadata.output_tier}\n")
        output.append(f"Generated: {metadata.validated_at}\n")
        output.append("=" * 60 + "\n\n")

        # Status
        passed = data.get("passed", False)
        if passed:
            output.append(f"{self.COLORS['GREEN']}✓ VALIDATION PASSED{self.COLORS['RESET']}\n")
        else:
            output.append(f"{self.COLORS['RED']}✗ VALIDATION FAILED{self.COLORS['RESET']}\n")

        # Score
        score = data.get("total_score", 0)
        grade = data.get("grade", "F")
        output.append(f"Score: {score}/100 ({grade})\n")

        # Summary
        output.append(f"\nFiles: {data.get('file_count', 0)} | ")
        output.append(f"Errors: {data.get('error_count', 0)} | ")
        output.append(f"Warnings: {data.get('warning_count', 0)}\n")

        # Diagnostics (Tier 2)
        if "diagnostics" in data and data["diagnostics"]:
            output.append(f"\n{self.COLORS['BOLD']}Issues:{self.COLORS['RESET']}\n")
            for diag in data["diagnostics"][:10]:
                severity = diag.get("severity", "INFO")
                color = {
                    "ERROR": self.COLORS["RED"],
                    "WARNING": self.COLORS["YELLOW"],
                    "INFO": self.COLORS["BLUE"],
                }.get(severity, "")

                output.append(
                    f"  {color}{diag.get('code', '???')}{self.COLORS['RESET']}: "
                    f"{diag.get('message', '')}\n"
                )

            remaining = len(data["diagnostics"]) - 10
            if remaining > 0:
                output.append(f"  ... and {remaining} more\n")

        # Action items preview (Tier 3)
        if "action_items" in data and data["action_items"]:
            output.append(f"\n{self.COLORS['BOLD']}Top Actions:{self.COLORS['RESET']}\n")
            for action in data["action_items"][:3]:
                priority = action.get("priority", "MEDIUM")
                output.append(f"  [{priority}] {action.get('group_label', 'Action')}\n")

        return "".join(output)
```

### 5.6 HTML Serializer (Deferred to v0.4.x)

Stub for now:

```python
# In pipelines/serializers/html_serializer.py

from typing import Dict, Any

class HtmlSerializer:
    """
    Serialize intermediate data to HTML format (DEFERRED TO v0.4.x).

    Full implementation requires:
    - Embeddable CSS framework
    - Interactive elements (collapsible sections, score gauges)
    - Self-contained document (no external dependencies)

    For v0.2.4e, raises NotImplementedError with clear message.
    """

    def serialize(self, data: Dict[str, Any], metadata: "ReportMetadata") -> str:
        """HTML serialization not yet implemented."""
        raise NotImplementedError(
            "HTML serialization is deferred to v0.4.x. "
            "Use JSON, Markdown, or YAML format in v0.2.4e. "
            "See RR-SPEC-v0.2.4e §5.6 for timeline."
        )
```

---

## 6. Extensibility: Renderer & Serializer Registration

The system uses a registry pattern for composability:

```python
# In pipelines/renderers/__init__.py and pipelines/serializers/__init__.py

from pipelines.renderers.tier1_renderer import Tier1Renderer
from pipelines.renderers.tier2_renderer import Tier2Renderer
from pipelines.renderers.tier3_renderer import Tier3Renderer
from pipelines.renderers.tier4_renderer import Tier4Renderer

from pipelines.serializers.json_serializer import JsonSerializer
from pipelines.serializers.markdown_serializer import MarkdownSerializer
from pipelines.serializers.yaml_serializer import YamlSerializer
from pipelines.serializers.html_serializer import HtmlSerializer
from pipelines.serializers.terminal_serializer import TerminalSerializer

# Global registries (defined in report_generation_stage.py)

TIER_RENDERERS = {
    1: Tier1Renderer,
    2: Tier2Renderer,
    3: Tier3Renderer,
    4: Tier4Renderer,
}

FORMAT_SERIALIZERS = {
    "json": JsonSerializer,
    "markdown": MarkdownSerializer,
    "yaml": YamlSerializer,
    "html": HtmlSerializer,
    "terminal": TerminalSerializer,
}

# Third-party extensions can register like this:
# TIER_RENDERERS[5] = CustomRenderer
# FORMAT_SERIALIZERS["custom_format"] = CustomSerializer
```

This pattern allows new tiers and formats to be added without modifying existing code.

---

## 7. Integration with Existing Pipeline

### 7.1 EcosystemPipeline Modification

The `EcosystemPipeline.run()` method must be updated to include Stage 6:

```python
# In pipelines/orchestrator.py (existing file)

from pipelines.stages.report_generation_stage import ReportGenerationStage

class EcosystemPipeline:
    """Complete 6-stage validation pipeline."""

    STAGES = [
        DiscoveryStage(),
        PerFileStage(),
        RelationshipStage(),
        EcosystemValidationStage(),
        ScoringStage(),
        ReportGenerationStage(),  # NEW: Stage 6
    ]

    def run(
        self,
        root_path: str,
        profile: ValidationProfile,
        stop_after: Optional[int] = None
    ) -> PipelineContext:
        """
        Run the complete ecosystem validation pipeline.

        Args:
            root_path: Project root directory
            profile: Validation profile (contains output_tier, output_format, etc.)
            stop_after: Optional stage ID to stop after (for early termination)

        Returns:
            PipelineContext with all accumulated data, including report_artifact if Stage 6 ran
        """
        context = PipelineContext(root_path=root_path, profile=profile)

        for stage in self.STAGES:
            # Skip if stop_after is set
            if stop_after and stage.stage_id > stop_after:
                result = StageResult(
                    stage=stage.stage_id,
                    status="SKIPPED",
                    diagnostics=[],
                    duration_ms=0,
                    message=f"Skipped per stop_after={stop_after}"
                )
                context.stage_results.append(result)
                continue

            # Execute stage
            result = stage.execute(context)
            context.stage_results.append(result)

            # Fail fast on critical errors (but allow Stage 6 to run for diagnostics)
            if result.status == "FAILED" and stage.stage_id < 6:
                break

        return context
```

### 7.2 Skip Conditions

Stage 6 skip conditions:

- **Normal skip**: If `stop_after < 6`, Stage 6 is skipped
- **Failure handling**: Stage 6 failure does NOT invalidate Stages 1–5 results. The pipeline continues and returns both validation results AND the failure message from Stage 6

### 7.3 Profile Integration

Profiles (Deliverable 4) control Stage 6 behavior:

```python
# In pipelines/models.py (ValidationProfile)

class ValidationProfile(BaseModel):
    """Validation profile configuration."""

    name: str                           # e.g., "lint", "ci", "full", "enterprise"
    output_tier: int = Field(ge=1, le=4)  # Output tier (1–4)
    output_format: str                  # Format (json, markdown, yaml, html, terminal)
    grouping_mode: str = "by-priority"  # For Tier 3+ (by-priority, by-level, by-file, by-effort)
    action_ordering: str = "by-dependency"  # For Tier 3+ (by-dependency, by-priority)
    # ... other fields ...
```

---

## 8. Renderer-Serializer Compatibility Validation

The `ReportGenerationStage.execute()` method validates the (tier, format) combination against the matrix from Output Tier Spec §4.2:

| Tier | JSON | Markdown | YAML | HTML | Terminal |
|------|:--:|:--:|:--:|:--:|:--:|
| 1 | Primary | — | Supported | — | Supported |
| 2 | Primary | Supported | Supported | Supported | Primary |
| 3 | Supported | Primary | — | Supported | — |
| 4 | Supported | Supported | — | Primary | — |

If an invalid combination is requested, `ReportGenerationStage.execute()` raises a `ValueError` and returns a FAILED `StageResult`.

---

## 9. Design Decisions

**DECISION-033: Stage 6 is pure presentation (no new validation logic)**

Rationale: Validation should be deterministic and agnostic to output format. Creating a new renderer must not require changes to validation logic. This separation enables the same validation run to produce multiple output formats without duplication.

**DECISION-034: Renderer registration pattern over class hierarchy**

Rationale: Inheritance chains (Tier1Renderer → Tier2Renderer → Tier3Renderer) create tight coupling and make it hard to swap implementations. The registry pattern allows each renderer to be independent, third-party extensions to register without modifying the core, and testing to inject mock renderers.

**DECISION-035: Report metadata is mandatory even for Tier 1**

Rationale: Traceability is essential. Every report must be identifiable back to the exact profile, engine version, and timestamp that produced it. This enables auditing, debugging, and reproducibility.

---

## 10. Open Questions & Future Work

### 10.1 Calibration & Scoring Sensitivity (Deliverable 6)

Score projections in Tier 3 assume linear relationships between diagnostics and score impact. Deliverable 6 (Ecosystem Scoring Calibration) will validate these assumptions against the calibration specimen corpus and refine the heuristics if needed.

### 10.2 Multi-Format Output in Single Pass

Should Stage 6 support producing multiple formats in one pass? For example:

```python
context.profile.output_formats = ["json", "markdown", "html"]
result = pipeline.run(root_path, profile)
# Returns multiple report_artifacts?
```

This is deferred to v0.3.x pending performance analysis.

### 10.3 Report Caching

Should Stage 6 cache reports for identical inputs? Hash the (root_path, profile, stages_executed, diagnostics) tuple, and return a cached artifact if the hash matches?

This is deferred to v0.3.x pending adoption analysis.

### 10.4 Context Profile Injection for Tier 4

Tier 4 requires a `context_profile` parameter (domain, industry, goals, etc.). How should this be provided?

- Via CLI flag: `--context '{"industry": "fintech", "project_type": "api"}'`
- Via .docstratum.yml: `context_profile:` section
- Via Python API: `profile.context_profile = ...`

This is specified in v0.4.x context profile schema.

---

## 11. Closing Paragraph

The Report Generation Stage completes the DocStratum validation pipeline as a closed system. Stages 1–5 produce comprehensive diagnostic and scoring data; Stage 6 renders that data into consumer-appropriate formats for CI/CD, developers, teams, and enterprises.

By separating validation (Stages 1–5) from presentation (Stage 6), the architecture ensures that:

1. Validation remains pure, deterministic, and format-agnostic
2. New output formats can be added without touching validation logic
3. Consumers can request multiple formats from a single pipeline run
4. Testing and debugging are simplified (renderers and serializers have no side effects)

This specification provides the contracts, patterns, and implementation guidance for Stage 6. Combined with the four prior deliverables, the complete output contract of the DocStratum engine is now defined and ready for implementation through v0.2.4e and beyond.

---

## Appendix A: Format-Tier Compatibility Matrix (Reference)

| Tier | JSON | Markdown | YAML | HTML | Terminal |
|------|------|----------|------|------|----------|
| **Tier 1** (Pass/Fail) | **Primary** | Not Supported | Supported | Not Supported | Supported |
| **Tier 2** (Diagnostic) | **Primary** | Supported | Supported | Supported | **Primary** |
| **Tier 3** (Playbook) | Supported | **Primary** | Not Supported | Supported | Not Supported |
| **Tier 4** (Adapted) | Supported | Supported | Not Supported | **Primary** | Not Supported |

Per Output Tier Spec §4.2.

---

## Appendix B: PipelineStageId Values Reference

For cross-reference with existing code and logs:

```python
class PipelineStageId(IntEnum):
    DISCOVERY = 1
    PER_FILE = 2
    RELATIONSHIP = 3
    ECOSYSTEM_VALIDATION = 4
    SCORING = 5
    REPORT_GENERATION = 6  # v0.2.4e
```

---

## Appendix C: Example Stage 6 Execution

Given a `PipelineContext` from Stages 1–5 and a `ValidationProfile` with `output_tier=3, output_format="markdown"`:

```python
from pipelines.stages.report_generation_stage import ReportGenerationStage
from pipelines.models import ValidationProfile

# Profile requests Tier 3 (Remediation Playbook) in Markdown format
profile = ValidationProfile(
    name="full",
    output_tier=3,
    output_format="markdown"
)

# Run Stages 1–5 (existing)
pipeline = EcosystemPipeline()
context = pipeline.run(root_path="/my/project", profile=profile)

# Stage 6 is included in the pipeline.run() call above.
# After execution, context.report_artifact contains the Markdown report:

artifact = context.report_artifact
print(artifact.content)  # Markdown text with playbook
print(artifact.metadata.report_id)  # Unique report ID

# Save to file
artifact.to_file("remediation_plan.md")
```

---

**End of Specification**
