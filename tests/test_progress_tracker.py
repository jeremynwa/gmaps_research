"""Tests for progress tracker."""

import pytest
from src.utils.progress_tracker import ProgressTracker, ProgressStats


def test_initial_state():
    """Test initial tracker state."""
    tracker = ProgressTracker(total=100)
    stats = tracker.get_stats()
    assert stats.total == 100
    assert stats.analyzed == 0
    assert stats.cache_hits == 0
    assert stats.errors == 0
    assert stats.skipped == 0


def test_increment_analyzed():
    """Test incrementing analyzed count."""
    tracker = ProgressTracker(total=10)
    tracker.increment()
    assert tracker.stats.analyzed == 1
    assert tracker.stats.cache_hits == 0


def test_increment_cached():
    """Test incrementing with cache hit."""
    tracker = ProgressTracker(total=10)
    tracker.increment(was_cached=True)
    assert tracker.stats.analyzed == 1
    assert tracker.stats.cache_hits == 1


def test_increment_error():
    """Test incrementing with error."""
    tracker = ProgressTracker(total=10)
    tracker.increment(was_error=True)
    assert tracker.stats.errors == 1
    assert tracker.stats.analyzed == 0


def test_increment_skipped():
    """Test incrementing with skipped."""
    tracker = ProgressTracker(total=10)
    tracker.increment(was_skipped=True)
    assert tracker.stats.skipped == 1
    assert tracker.stats.analyzed == 0


def test_percent_calculation():
    """Test percentage calculation."""
    tracker = ProgressTracker(total=100)
    for _ in range(25):
        tracker.increment()
    assert tracker.stats.percent == 25.0


def test_cache_hit_rate():
    """Test cache hit rate calculation."""
    tracker = ProgressTracker(total=10)
    tracker.increment(was_cached=True)
    tracker.increment(was_cached=True)
    tracker.increment(was_cached=False)
    assert abs(tracker.stats.cache_hit_rate - 66.67) < 0.1
