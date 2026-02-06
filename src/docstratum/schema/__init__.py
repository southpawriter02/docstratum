"""DocStratum Schema Module — Public API.

Re-exports all public Pydantic models for the validation engine.
Import from this module rather than from submodules directly.

Model Categories:
    Parsed models       What an existing llms.txt file contains (Markdown AST)
    Validation models   What the validator reports (diagnostics, levels)
    Quality models      How good the file is (composite score, grades)
    Classification      What type of document it is (Type 1 vs. Type 2)
    Enrichment models   DocStratum-extended schema (concepts, few-shot, instructions)
    Constants           Canonical section names, token budget tiers, check IDs
"""

# TODO (v0.1.2): Add public API re-exports once schema submodules are implemented.
# See v0.1.1 §Package Initialization for the full re-export list.
