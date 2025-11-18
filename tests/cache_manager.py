"""Tests for cache manager."""

import pytest
from src.processors.cache_manager import CacheManager


def test_cache_init(temp_cache_file):
    """Test cache manager initialization."""
    cache = CacheManager(temp_cache_file)
    assert cache.size() == 0


def test_cache_set_get(cache_manager):
    """Test setting and getting cache values."""
    cache_manager.set("test_key", {"score": 85})
    
    assert cache_manager.exists("test_key")
    result = cache_manager.get("test_key")
    assert result == {"score": 85}


def test_cache_persistence(temp_cache_file):
    """Test cache persists across instances."""
    # Create cache and add data
    cache1 = CacheManager(temp_cache_file)
    cache1.set("persistent_key", {"score": 90})
    cache1.save_cache()
    
    # Create new instance and check data exists
    cache2 = CacheManager(temp_cache_file)
    assert cache2.exists("persistent_key")
    assert cache2.get("persistent_key") == {"score": 90}


def test_cache_clear(cache_manager):
    """Test clearing cache."""
    cache_manager.set("test_key", {"score": 85})
    assert cache_manager.size() == 1
    
    cache_manager.clear()
    assert cache_manager.size() == 0