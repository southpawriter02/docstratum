"""Tests for the parser metadata extraction module (v0.2.1d).

Tests cover YAML frontmatter detection, parsing, and field mapping:
valid frontmatter, empty/malformed YAML, unclosed blocks, non-dict
results, unrecognized keys, leading blank lines, and safe_load usage.
See RR-META-testing-standards for naming conventions and fixture patterns.
"""

from unittest.mock import patch

from docstratum.parser.metadata import extract_metadata

# ── No Frontmatter ──────────────────────────────────────────────────


class TestNoFrontmatter:
    """Tests for inputs that should return None."""

    def test_no_frontmatter(self):
        """Verify plain Markdown returns None."""
        assert extract_metadata("# Title\n") is None

    def test_empty_frontmatter(self):
        """Verify empty block (---\\n---) returns None."""
        assert extract_metadata("---\n---\n") is None

    def test_whitespace_only_frontmatter(self):
        """Verify whitespace-only block returns None."""
        assert extract_metadata("---\n   \n---\n") is None

    def test_malformed_yaml(self):
        """Verify malformed YAML returns None."""
        assert extract_metadata("---\n: bad\n---\n") is None

    def test_yaml_list(self):
        """Verify YAML list (not dict) returns None."""
        assert extract_metadata("---\n- a\n- b\n---\n") is None

    def test_yaml_scalar(self):
        """Verify YAML scalar (not dict) returns None."""
        assert extract_metadata("---\njust text\n---\n") is None

    def test_unclosed_frontmatter(self):
        """Verify unclosed frontmatter (no closing ---) returns None."""
        assert extract_metadata("---\nkey: val\n") is None

    def test_frontmatter_not_at_start(self):
        """Verify --- not at start of file returns None."""
        assert extract_metadata("# Title\n---\nkey: val\n---\n") is None


# ── Valid Frontmatter ───────────────────────────────────────────────


class TestValidFrontmatter:
    """Tests for valid frontmatter extraction."""

    def test_valid_frontmatter_single_field(self):
        """Verify single recognized field is extracted."""
        meta = extract_metadata("---\nsite_name: X\n---\n")
        assert meta is not None
        assert meta.site_name == "X"

    def test_valid_frontmatter_all_fields(self):
        """Verify all 7 recognized fields are populated."""
        content = (
            "---\n"
            "schema_version: 0.2.0\n"
            "site_name: My Project\n"
            "site_url: https://example.com\n"
            "last_updated: '2026-02-13'\n"
            "generator: docusaurus\n"
            "docstratum_version: 0.2.0\n"
            "token_budget_tier: standard\n"
            "---\n"
            "# My Project\n"
        )
        meta = extract_metadata(content)
        assert meta is not None
        assert meta.schema_version == "0.2.0"
        assert meta.site_name == "My Project"
        assert meta.site_url == "https://example.com"
        assert meta.last_updated == "2026-02-13"
        assert meta.generator == "docusaurus"
        assert meta.docstratum_version == "0.2.0"
        assert meta.token_budget_tier == "standard"

    def test_default_schema_version(self):
        """Verify schema_version defaults to '0.1.0' when not in frontmatter."""
        meta = extract_metadata("---\nsite_name: X\n---\n")
        assert meta is not None
        assert meta.schema_version == "0.1.0"

    def test_custom_schema_version(self):
        """Verify custom schema_version is used."""
        meta = extract_metadata("---\nschema_version: 0.2.0\n---\n")
        assert meta is not None
        assert meta.schema_version == "0.2.0"

    def test_generator_field(self):
        """Verify generator field is extracted."""
        meta = extract_metadata("---\ngenerator: docusaurus\n---\n")
        assert meta is not None
        assert meta.generator == "docusaurus"

    def test_token_budget_tier_field(self):
        """Verify token_budget_tier field is extracted."""
        meta = extract_metadata("---\ntoken_budget_tier: standard\n---\n")
        assert meta is not None
        assert meta.token_budget_tier == "standard"


# ── Key Handling ────────────────────────────────────────────────────


class TestKeyHandling:
    """Tests for key filtering and case sensitivity."""

    def test_unrecognized_keys_ignored(self):
        """Verify unrecognized keys are silently ignored."""
        meta = extract_metadata("---\nhugo_theme: abc\n---\n")
        assert meta is not None
        # All fields should be defaults
        assert meta.site_name is None

    def test_mixed_keys(self):
        """Verify recognized keys extracted, unrecognized ignored."""
        meta = extract_metadata("---\nsite_name: X\nhugo_theme: y\n---\n")
        assert meta is not None
        assert meta.site_name == "X"


# ── Edge Cases ──────────────────────────────────────────────────────


class TestEdgeCases:
    """Tests for edge cases."""

    def test_leading_blank_lines(self):
        """Verify leading blank lines before --- are accepted."""
        meta = extract_metadata("\n\n---\nsite_name: X\n---\n")
        assert meta is not None
        assert meta.site_name == "X"

    def test_unicode_values(self):
        """Verify Unicode values pass through correctly."""
        meta = extract_metadata("---\nsite_name: 日本語\n---\n")
        assert meta is not None
        assert meta.site_name == "日本語"

    def test_triple_dash_in_body(self):
        """Verify --- in document body doesn't affect extraction."""
        content = "---\nsite_name: X\n---\ncontent with ---\nmore content\n"
        meta = extract_metadata(content)
        assert meta is not None
        assert meta.site_name == "X"


# ── Safety ──────────────────────────────────────────────────────────


class TestSafety:
    """Tests for safe YAML loading."""

    def test_uses_safe_load(self):
        """Verify yaml.safe_load is used, not yaml.load."""
        with patch("docstratum.parser.metadata.yaml.safe_load") as mock_safe:
            mock_safe.return_value = {"site_name": "X"}
            meta = extract_metadata("---\nsite_name: X\n---\n")
            mock_safe.assert_called_once()
            assert meta is not None
