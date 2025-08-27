"""
Unit tests for brand bible parsing functionality.
"""
import pytest
from utils.brand_bible_parser import BrandBibleParser


class TestBrandBibleParser:
    """Test cases for brand bible parsing."""

    def test_parser_initialization(self):
        """Test that parser can be initialized."""
        parser = BrandBibleParser()
        assert parser is not None

    def test_parse_valid_xml(self):
        """Test parsing valid XML brand bible."""
        sample_xml = """
        <brand>
            <name>Test Brand</name>
            <voice>Professional</voice>
        </brand>
        """

        parser = BrandBibleParser()
        result = parser.parse_xml(sample_xml)

        assert result is not None
        assert "name" in result or "voice" in result

    def test_parse_empty_xml(self):
        """Test parsing empty XML."""
        parser = BrandBibleParser()
        result = parser.parse_xml("")
        # Should handle gracefully
        assert result is not None
