"""Tests for analyzers."""

import pytest
from src.analyzers.mock_analyzer import MockAnalyzer
from config.settings import Config


def test_mock_analyzer_basic():
    """Test mock analyzer returns results."""
    analyzer = MockAnalyzer()
    
    result = analyzer.analyze_review(
        establishment="Test Restaurant",
        site="Paris",
        review_text="Great coffee and fast service!",
        author="Test User",
        note=5,
        date="2025-01-17"
    )
    
    assert result is not None
    assert isinstance(result, dict)
    assert len(result) == len(Config.CRITERIA)


def test_mock_analyzer_empty_review():
    """Test mock analyzer handles empty reviews."""
    analyzer = MockAnalyzer()
    
    result = analyzer.analyze_review(
        establishment="Test Restaurant",
        site="Paris",
        review_text="",
        author="Test User",
        note=5,
        date="2025-01-17"
    )
    
    assert result is not None
    # All scores should be N/A
    for key, value in result.items():
        assert value == "N/A"


def test_mock_analyzer_short_review():
    """Test mock analyzer handles short reviews."""
    analyzer = MockAnalyzer()
    
    result = analyzer.analyze_review(
        establishment="Test Restaurant",
        site="Paris",
        review_text="Good",  # Too short
        author="Test User",
        note=5,
        date="2025-01-17"
    )
    
    assert result is not None
    for key, value in result.items():
        assert value == "N/A"