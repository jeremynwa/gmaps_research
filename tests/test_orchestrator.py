"""Tests for orchestrator."""

import pytest
import pandas as pd
from unittest.mock import Mock, patch

from src.processors.orchestrator import Orchestrator
from src.analyzers.mock_analyzer import MockAnalyzer
from config.settings import Config


def test_orchestrator_empty_reviews(mock_analyzer, tmp_path):
    """Test orchestrator with empty review list."""
    cache_file = tmp_path / "cache.json"
    orchestrator = Orchestrator(mock_analyzer, cache_file=cache_file)
    df = orchestrator.analyze([], verbose=False)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0


def test_orchestrator_all_short_reviews(mock_analyzer, tmp_path):
    """Test all reviews below minimum length get N/A scores."""
    cache_file = tmp_path / "cache.json"
    orchestrator = Orchestrator(mock_analyzer, cache_file=cache_file)
    reviews = [
        {'Establishment': 'Test', 'Site': 'Paris', 'Avis': 'Ok',
         'Auteur': 'User', 'Note': 3, 'Date de l avis': '2025-01-17', 'CDPF': 'short1'},
    ]
    df = orchestrator.analyze(reviews, verbose=False)
    assert len(df) == 1
    for criterion in Config.CRITERIA:
        assert df.iloc[0][criterion] == "N/A"


def test_orchestrator_single_review(mock_analyzer, tmp_path, sample_reviews):
    """Test with a single valid review."""
    cache_file = tmp_path / "cache.json"
    orchestrator = Orchestrator(mock_analyzer, cache_file=cache_file)
    df = orchestrator.analyze([sample_reviews[0]], max_workers=1, verbose=False)
    assert len(df) == 1
    assert 'Establishment' in df.columns
    for criterion in Config.CRITERIA:
        assert criterion in df.columns


def test_orchestrator_multiple_reviews(mock_analyzer, tmp_path, sample_reviews):
    """Test with multiple valid reviews."""
    cache_file = tmp_path / "cache.json"
    orchestrator = Orchestrator(mock_analyzer, cache_file=cache_file)
    df = orchestrator.analyze(sample_reviews, max_workers=2, verbose=False)
    assert len(df) == len(sample_reviews)


def test_orchestrator_cache_hit(mock_analyzer, tmp_path, sample_reviews):
    """Test that cached results are reused."""
    cache_file = tmp_path / "cache.json"
    orchestrator = Orchestrator(mock_analyzer, cache_file=cache_file)

    # First run
    df1 = orchestrator.analyze(sample_reviews, verbose=False)

    # Second run should use cache
    df2 = orchestrator.analyze(sample_reviews, verbose=False)
    assert len(df1) == len(df2)


def test_orchestrator_cache_disabled(mock_analyzer, tmp_path, sample_reviews):
    """Test with cache disabled."""
    cache_file = tmp_path / "cache.json"
    orchestrator = Orchestrator(mock_analyzer, cache_file=cache_file, use_cache=False)
    df = orchestrator.analyze(sample_reviews, verbose=False)
    assert len(df) == len(sample_reviews)


def test_orchestrator_cache_key_generation(mock_analyzer, tmp_path):
    """Test deterministic cache key creation."""
    cache_file = tmp_path / "cache.json"
    orchestrator = Orchestrator(mock_analyzer, cache_file=cache_file)
    review = {'CDPF': 'abc', 'Date de l avis': '2025-01-17', 'Auteur': 'User'}
    key1 = orchestrator._create_cache_key(review)
    key2 = orchestrator._create_cache_key(review)
    assert key1 == key2
    assert isinstance(key1, str)
    assert len(key1) > 0


def test_orchestrator_result_dataframe_columns(mock_analyzer, tmp_path, sample_reviews):
    """Test output DataFrame has all expected columns."""
    cache_file = tmp_path / "cache.json"
    orchestrator = Orchestrator(mock_analyzer, cache_file=cache_file)
    df = orchestrator.analyze(sample_reviews, verbose=False)

    # Should have original columns + all criteria
    for col in ['Establishment', 'Site', 'Avis', 'Auteur', 'Note', 'Date de l avis']:
        assert col in df.columns
    for criterion in Config.CRITERIA:
        assert criterion in df.columns
