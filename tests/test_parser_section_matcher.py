"""Tests for the parser section matcher module (v0.2.1c).

Tests cover canonical section matching: exact matches (case-insensitive),
alias resolution, whitespace normalization, non-matching names, and
in-place mutation semantics.
See RR-META-testing-standards for naming conventions and fixture patterns.
"""

from docstratum.parser.section_matcher import match_canonical_sections
from docstratum.schema.constants import SECTION_NAME_ALIASES, CanonicalSectionName
from docstratum.schema.parsed import ParsedLlmsTxt, ParsedSection

# ── Helpers ──────────────────────────────────────────────────────────


def _make_doc(section_names: list[str]) -> ParsedLlmsTxt:
    """Create a ParsedLlmsTxt with sections having the given names."""
    doc = ParsedLlmsTxt()
    doc.title = "Test"
    doc.sections = [
        ParsedSection(name=name, line_number=i + 1)
        for i, name in enumerate(section_names)
    ]
    doc.raw_content = ""
    doc.source_filename = "llms.txt"
    return doc


# ── Exact Canonical Matching ────────────────────────────────────────


class TestExactCanonical:
    """Tests for exact canonical name matching."""

    def test_exact_canonical_master_index(self):
        """Verify 'Master Index' matches exactly."""
        doc = _make_doc(["Master Index"])
        match_canonical_sections(doc)
        assert doc.sections[0].canonical_name == "Master Index"

    def test_exact_canonical_api_reference(self):
        """Verify 'API Reference' matches exactly."""
        doc = _make_doc(["API Reference"])
        match_canonical_sections(doc)
        assert doc.sections[0].canonical_name == "API Reference"

    def test_exact_canonical_faq(self):
        """Verify 'FAQ' matches exactly."""
        doc = _make_doc(["FAQ"])
        match_canonical_sections(doc)
        assert doc.sections[0].canonical_name == "FAQ"

    def test_exact_canonical_case_insensitive(self):
        """Verify 'api reference' (lowercase) matches 'API Reference'."""
        doc = _make_doc(["api reference"])
        match_canonical_sections(doc)
        assert doc.sections[0].canonical_name == "API Reference"

    def test_exact_canonical_mixed_case(self):
        """Verify 'Api Reference' (mixed case) matches 'API Reference'."""
        doc = _make_doc(["Api Reference"])
        match_canonical_sections(doc)
        assert doc.sections[0].canonical_name == "API Reference"


# ── Alias Matching ──────────────────────────────────────────────────


class TestAliasMatching:
    """Tests for alias resolution."""

    def test_alias_quickstart(self):
        """Verify 'quickstart' resolves to 'Getting Started'."""
        doc = _make_doc(["quickstart"])
        match_canonical_sections(doc)
        assert doc.sections[0].canonical_name == "Getting Started"

    def test_alias_toc(self):
        """Verify 'toc' resolves to 'Master Index'."""
        doc = _make_doc(["toc"])
        match_canonical_sections(doc)
        assert doc.sections[0].canonical_name == "Master Index"

    def test_alias_endpoints(self):
        """Verify 'endpoints' resolves to 'API Reference'."""
        doc = _make_doc(["endpoints"])
        match_canonical_sections(doc)
        assert doc.sections[0].canonical_name == "API Reference"

    def test_alias_recipes(self):
        """Verify 'recipes' resolves to 'Examples'."""
        doc = _make_doc(["recipes"])
        match_canonical_sections(doc)
        assert doc.sections[0].canonical_name == "Examples"

    def test_alias_debugging(self):
        """Verify 'debugging' resolves to 'Troubleshooting'."""
        doc = _make_doc(["debugging"])
        match_canonical_sections(doc)
        assert doc.sections[0].canonical_name == "Troubleshooting"

    def test_alias_appendix(self):
        """Verify 'appendix' resolves to 'Optional'."""
        doc = _make_doc(["appendix"])
        match_canonical_sections(doc)
        assert doc.sections[0].canonical_name == "Optional"

    def test_alias_case_insensitive(self):
        """Verify 'QUICKSTART' (uppercase) resolves to 'Getting Started'."""
        doc = _make_doc(["QUICKSTART"])
        match_canonical_sections(doc)
        assert doc.sections[0].canonical_name == "Getting Started"


# ── Non-Matching ────────────────────────────────────────────────────


class TestNoMatch:
    """Tests for names that should NOT match."""

    def test_no_match(self):
        """Verify custom name gets canonical_name = None."""
        doc = _make_doc(["My Custom Section"])
        match_canonical_sections(doc)
        assert doc.sections[0].canonical_name is None

    def test_no_fuzzy_match(self):
        """Verify typo 'Getting Start' does NOT match."""
        doc = _make_doc(["Getting Start"])
        match_canonical_sections(doc)
        assert doc.sections[0].canonical_name is None

    def test_no_substring_match(self):
        """Verify 'API Reference Guide' does NOT match."""
        doc = _make_doc(["API Reference Guide"])
        match_canonical_sections(doc)
        assert doc.sections[0].canonical_name is None


# ── Whitespace Handling ─────────────────────────────────────────────


class TestWhitespace:
    """Tests for whitespace normalization."""

    def test_whitespace_stripped(self):
        """Verify '  FAQ  ' (leading/trailing) matches 'FAQ'."""
        doc = _make_doc(["  FAQ  "])
        match_canonical_sections(doc)
        assert doc.sections[0].canonical_name == "FAQ"

    def test_empty_name(self):
        """Verify empty string gets canonical_name = None."""
        doc = _make_doc([""])
        match_canonical_sections(doc)
        assert doc.sections[0].canonical_name is None

    def test_whitespace_only_name(self):
        """Verify whitespace-only name gets canonical_name = None."""
        doc = _make_doc(["   "])
        match_canonical_sections(doc)
        assert doc.sections[0].canonical_name is None


# ── Multi-Section and Edge Cases ────────────────────────────────────


class TestMultiSection:
    """Tests for multi-section scenarios and edge cases."""

    def test_multiple_sections_same_canonical(self):
        """Verify two aliases of the same canonical both resolve."""
        doc = _make_doc(["quickstart", "installation"])
        match_canonical_sections(doc)
        assert doc.sections[0].canonical_name == "Getting Started"
        assert doc.sections[1].canonical_name == "Getting Started"

    def test_empty_sections_list(self):
        """Verify no error when doc.sections is empty."""
        doc = _make_doc([])
        match_canonical_sections(doc)  # should not raise
        assert doc.sections == []


# ── Comprehensive Coverage ──────────────────────────────────────────


class TestComprehensiveCoverage:
    """Tests for all 11 canonical names and all 32 aliases."""

    def test_all_11_canonical_names(self):
        """Verify all 11 canonical names match when given exactly."""
        names = [name.value for name in CanonicalSectionName]
        doc = _make_doc(names)
        match_canonical_sections(doc)
        for i, name in enumerate(names):
            assert (
                doc.sections[i].canonical_name == name
            ), f"Canonical name '{name}' did not match"

    def test_all_32_aliases(self):
        """Verify all 32 aliases resolve to their correct canonical name."""
        alias_keys = list(SECTION_NAME_ALIASES.keys())
        doc = _make_doc(alias_keys)
        match_canonical_sections(doc)
        for i, alias_key in enumerate(alias_keys):
            expected = SECTION_NAME_ALIASES[alias_key].value
            assert doc.sections[i].canonical_name == expected, (
                f"Alias '{alias_key}' should resolve to '{expected}', "
                f"got '{doc.sections[i].canonical_name}'"
            )


# ── Mutation Semantics ──────────────────────────────────────────────


class TestMutation:
    """Tests that match_canonical_sections mutates in-place."""

    def test_mutates_in_place(self):
        """Verify same section instance has canonical_name set."""
        doc = _make_doc(["FAQ"])
        original_section = doc.sections[0]
        match_canonical_sections(doc)
        assert doc.sections[0] is original_section
        assert original_section.canonical_name == "FAQ"
