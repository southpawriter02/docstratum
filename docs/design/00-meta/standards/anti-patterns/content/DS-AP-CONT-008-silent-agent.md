# DS-AP-CONT-008: Silent Agent

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-AP-CONT-008 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Registry ID** | AP-CONT-008 |
| **Category** | Content |
| **Check ID** | CHECK-020 |
| **Severity Impact** | Reduce content dimension score |
| **Provenance** | v0.0.4c; v0.0.0 Stripe Pattern; v0.0.1b Gap Analysis |

## Description

Documentation contains substantive content but provides no LLM-facing guidance or instructions for autonomous agents. This anti-pattern is a critical gap in AI-native documentation: files are written for human readers without signals or context to help LLM agents navigate, interpret, or reason about the material. Agents must either guess intended usage or defer processing, severely limiting the documentation's value in agent-driven workflows.

## Detection Logic

```python
def detect_silent_agent(content):
    """
    Identify files lacking LLM-facing guidance sections.
    
    Algorithm:
    1. Define LLM instruction section headers (case-insensitive):
       - "LLM Instructions"
       - "Instructions"
       - "Agent Instructions"
       - "For LLM Agents"
       - "AI Guidance"
    2. Search for these headers in content
    3. Check if match found in first 80% of content (not epilogue)
    4. If no match, trigger anti-pattern
    5. Requirement: section must have >20 chars of substantive content
    
    Returns: (triggered, has_llm_section, section_preview)
    """
    import re
    
    llm_section_headers = [
        r'##\s+LLM Instructions',
        r'##\s+Instructions(?!\s+for)',
        r'##\s+Agent Instructions',
        r'##\s+For LLM Agents',
        r'##\s+AI Guidance',
        r'##\s+For Agents'
    ]
    
    for header_pattern in llm_section_headers:
        match = re.search(header_pattern, content, re.IGNORECASE)
        if match:
            section_start = match.end()
            section_content = content[section_start:section_start+200]
            if len(section_content.strip()) > 20:
                return False, True, section_content[:100]
    
    # Check if file has substantive content (>500 chars)
    if len(content.strip()) > 500:
        return True, False, None
    
    return False, False, None
```

## Example (Synthetic)

```markdown
# Deployment Architecture

## Overview
This document describes the multi-region deployment strategy used in production.

## Regions
The system runs in us-east-1, eu-west-1, and ap-southeast-1 with active-active failover.

## Configuration
Set the REGION environment variable and deploy using the standard CI/CD pipeline.

## Monitoring
CloudWatch dashboards track deployment health across all regions.
```

This file contains useful information but provides no guidance for agents. What should an agent do with this information? How should it be interpreted in context of other documentation? No instructions provided.

## Remediation

1. Add an "LLM Instructions" or "For Agents" section to all technical documentation
2. Provide explicit guidance on:
   - How agents should interpret this content
   - What actions agents should take based on this information
   - Prerequisites or dependencies the agent should understand
   - Edge cases or caveats agents should consider
3. Example remediation:
   ```markdown
   ## For Agents
   
   This document describes the deployment topology. When assisting users with:
   - Deployment choices: reference the multi-region strategy
   - Regional selection: prioritize us-east-1 for latency-sensitive workloads
   - Configuration: emphasize REGION environment variable setup
   - Troubleshooting: check CloudWatch dashboards via the monitoring section
   ```
4. Include this practice in documentation templates and style guides
5. Implement CI checks to flag files without LLM guidance sections

## Affected Criteria

- DS-VC-APD-004 (Content must be LLM-compatible)
- DS-VC-APD-001 (LLM Instructions Section — this section is mandatory for AI-native docs)

## Emitted Diagnostics

- DS-DC-I001 (NO_LLM_INSTRUCTIONS — informational notice for missing agent guidance)

## Related Anti-Patterns

- DS-AP-CONT-003 (Jargon Jungle — jargon becomes harder to understand without agent guidance)
- DS-AP-CONT-006 (Example Void — absence of guidance often correlates with absence of examples)

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.2 |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
