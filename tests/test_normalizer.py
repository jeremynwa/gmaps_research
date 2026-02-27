"""Tests for gare normalizer."""

import pytest
from src.utils.normalizer import GareNormalizer


def test_normalize_known_mapping():
    """Test normalizing a known station code."""
    result = GareNormalizer.normalize("PARIS-GDL")
    assert result == "Paris Gare de Lyon"


def test_normalize_with_fr_prefix():
    """Test normalizing with FR prefix."""
    result = GareNormalizer.normalize("FR PARIS-GDL")
    assert result == "Paris Gare de Lyon"


def test_normalize_with_suffix():
    """Test normalizing code with extra text."""
    result = GareNormalizer.normalize("PARIS-GDL MCDO")
    assert result == "Paris Gare de Lyon"


def test_normalize_unknown():
    """Test normalizing unknown location returns as-is."""
    result = GareNormalizer.normalize("SOME-UNKNOWN-PLACE")
    assert result == "SOME-UNKNOWN-PLACE"


def test_normalize_empty():
    """Test normalizing empty string returns Unknown."""
    assert GareNormalizer.normalize("") == "Unknown"
    assert GareNormalizer.normalize(None) == "Unknown"


def test_normalize_multiple_stations():
    """Test normalizing various stations."""
    assert GareNormalizer.normalize("LYON-PART-DIEU") == "Lyon Part-Dieu"
    assert GareNormalizer.normalize("MARSEILLE") == "Marseille Saint-Charles"
    assert GareNormalizer.normalize("FR NICE") == "Nice Ville"
