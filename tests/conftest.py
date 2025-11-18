"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path
import pandas as pd

from src.analyzers.mock_analyzer import MockAnalyzer
from src.processors.cache_manager import CacheManager
from config.settings import Config


@pytest.fixture
def sample_reviews():
    """Sample reviews for testing."""
    return [
        {
            'Establishment': 'Test Restaurant',
            'Site': 'Paris Gare de Lyon',
            'Avis': 'Excellent café et croissants frais!',
            'Auteur': 'Test User 1',
            'Note': 5,
            'Date de l avis': '2025-01-17',
            'CDPF': 'test_1'
        },
        {
            'Establishment': 'Test Restaurant',
            'Site': 'Paris Gare du Nord',
            'Avis': 'Service rapide mais un peu cher.',
            'Auteur': 'Test User 2',
            'Note': 3,
            'Date de l avis': '2025-01-16',
            'CDPF': 'test_2'
        },
    ]


@pytest.fixture
def mock_analyzer():
    """Mock analyzer instance."""
    return MockAnalyzer()


@pytest.fixture
def temp_cache_file(tmp_path):
    """Temporary cache file."""
    return tmp_path / "test_cache.json"


@pytest.fixture
def cache_manager(temp_cache_file):
    """Cache manager with temp file."""
    return CacheManager(temp_cache_file)


@pytest.fixture
def sample_csv_file(tmp_path, sample_reviews):
    """Create a temporary CSV file with sample data."""
    df = pd.DataFrame(sample_reviews)
    csv_file = tmp_path / "test_reviews.csv"
    df.to_csv(csv_file, index=False)
    return csv_file