"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path
import pandas as pd

from src.analyzers.mock_analyzer import MockAnalyzer
from src.processors.cache_manager import CacheManager


@pytest.fixture
def sample_reviews():
    """Sample reviews for testing."""
    return [
        {
            'Establishment': 'Test Restaurant',
            'Site': 'Paris Gare de Lyon',
            'Avis': 'Excellent cafe et croissants frais! Le service est rapide.',
            'Auteur': 'Test User 1',
            'Note': 5,
            'Date de l avis': '2025-01-17',
            'CDPF': 'test_1'
        },
        {
            'Establishment': 'Test Restaurant',
            'Site': 'Paris Gare du Nord',
            'Avis': 'Service rapide mais un peu cher pour la qualite proposee.',
            'Auteur': 'Test User 2',
            'Note': 3,
            'Date de l avis': '2025-01-16',
            'CDPF': 'test_2'
        },
    ]


@pytest.fixture
def sample_review_short():
    """A review that is too short to analyze."""
    return {
        'Establishment': 'Test', 'Site': 'Paris',
        'Avis': 'Good', 'Auteur': 'User',
        'Note': 5, 'Date de l avis': '2025-01-17', 'CDPF': 'short_1'
    }


@pytest.fixture
def sample_review_empty():
    """A review with empty text."""
    return {
        'Establishment': 'Test', 'Site': 'Paris',
        'Avis': '', 'Auteur': 'User',
        'Note': 5, 'Date de l avis': '2025-01-17', 'CDPF': 'empty_1'
    }


@pytest.fixture
def sample_review_nan():
    """A review with NaN text."""
    return {
        'Establishment': 'Test', 'Site': 'Paris',
        'Avis': 'nan', 'Auteur': 'User',
        'Note': 5, 'Date de l avis': '2025-01-17', 'CDPF': 'nan_1'
    }


@pytest.fixture
def sample_reviews_large():
    """50 sample reviews for load testing."""
    return [
        {
            'Establishment': f'Restaurant {i}',
            'Site': 'Paris Gare de Lyon',
            'Avis': f'This is review number {i} with enough text to pass the minimum length filter easily for testing.',
            'Auteur': f'User {i}',
            'Note': (i % 5) + 1,
            'Date de l avis': '2025-01-17',
            'CDPF': f'load_test_{i}'
        }
        for i in range(50)
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


@pytest.fixture
def sample_excel_file(tmp_path, sample_reviews):
    """Create a temporary Excel file with sample data."""
    df = pd.DataFrame(sample_reviews)
    excel_file = tmp_path / "test_reviews.xlsx"
    df.to_excel(excel_file, index=False)
    return excel_file


@pytest.fixture(autouse=True)
def env_isolation(monkeypatch):
    """Ensure tests never use real API keys."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OUTSCRAPER_API_KEY", raising=False)
