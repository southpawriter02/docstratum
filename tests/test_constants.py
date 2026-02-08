"""Tests for schema constants (constants.py)."""

import pytest

from docstratum.schema.constants import (
    ANTI_PATTERN_REGISTRY,
    CANONICAL_SECTION_ORDER,
    SECTION_NAME_ALIASES,
    TOKEN_BUDGET_TIERS,
    TOKEN_ZONE_ANTI_PATTERN,
    TOKEN_ZONE_DEGRADATION,
    TOKEN_ZONE_GOOD,
    TOKEN_ZONE_OPTIMAL,
    AntiPatternCategory,
    AntiPatternID,
    CanonicalSectionName,
)


@pytest.mark.unit
def test_canonical_section_names_count():
    """Verify exactly 11 canonical section names."""
    assert len(CanonicalSectionName) == 11


@pytest.mark.unit
def test_section_name_aliases_validity():
    """Verify all aliases map to valid canonical names."""
    for alias, canonical in SECTION_NAME_ALIASES.items():
        assert isinstance(alias, str)
        assert alias.lower() == alias, f"Alias '{alias}' must be lowercase"
        assert isinstance(canonical, CanonicalSectionName)


@pytest.mark.unit
def test_canonical_section_order():
    """Verify ordering dict covers all sections except OPTIONAL."""
    assert len(CANONICAL_SECTION_ORDER) == 10
    assert CanonicalSectionName.OPTIONAL not in CANONICAL_SECTION_ORDER
    # Ensure values are unique 1-10
    positions = sorted(CANONICAL_SECTION_ORDER.values())
    assert positions == list(range(1, 11))


@pytest.mark.unit
def test_token_budget_tiers():
    """Verify token budget tiers consistency."""
    assert len(TOKEN_BUDGET_TIERS) == 3
    for _, tier in TOKEN_BUDGET_TIERS.items():
        assert tier.min_tokens < tier.max_tokens
        assert tier.file_strategy in [
            "single",
            "dual (index + full)",
            "multi (master + per-service)",
        ]


@pytest.mark.unit
def test_token_zones_ordering():
    """Verify token zone thresholds increase logicallly."""
    assert TOKEN_ZONE_OPTIMAL < TOKEN_ZONE_GOOD
    assert TOKEN_ZONE_GOOD < TOKEN_ZONE_DEGRADATION
    assert TOKEN_ZONE_DEGRADATION < TOKEN_ZONE_ANTI_PATTERN


@pytest.mark.unit
def test_anti_pattern_counts():
    """Verify exactly 28 anti-patterns across 5 categories."""
    assert len(AntiPatternID) == 28
    assert len(AntiPatternCategory) == 5
    assert len(ANTI_PATTERN_REGISTRY) == 28


@pytest.mark.unit
def test_anti_pattern_registry_integrity():
    """Verify registry entries match IDs and Checks."""
    # Check for duplicate IDs
    ids = [entry.id for entry in ANTI_PATTERN_REGISTRY]
    assert len(ids) == len(set(ids)), "Duplicate AntiPatternIDs in registry"

    for entry in ANTI_PATTERN_REGISTRY:
        assert isinstance(entry.id, AntiPatternID)
        assert isinstance(entry.category, AntiPatternCategory)
        assert entry.check_id.startswith(
            "CHECK-"
        ), f"Invalid check ID: {entry.check_id}"
        assert entry.description, "Empty description"
