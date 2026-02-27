"""Tests for cache manager."""

import json
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
    cache1 = CacheManager(temp_cache_file)
    cache1.set("persistent_key", {"score": 90})
    cache1.save_cache()

    cache2 = CacheManager(temp_cache_file)
    assert cache2.exists("persistent_key")
    assert cache2.get("persistent_key") == {"score": 90}


def test_cache_clear(cache_manager):
    """Test clearing cache."""
    cache_manager.set("test_key", {"score": 85})
    assert cache_manager.size() == 1
    cache_manager.clear()
    assert cache_manager.size() == 0


def test_cache_nonexistent_key(cache_manager):
    """Test getting a nonexistent key returns None."""
    assert cache_manager.get("nonexistent") is None
    assert not cache_manager.exists("nonexistent")


def test_cache_overwrite_key(cache_manager):
    """Test overwriting an existing key."""
    cache_manager.set("key", {"score": 50})
    cache_manager.set("key", {"score": 90})
    assert cache_manager.get("key") == {"score": 90}
    assert cache_manager.size() == 1


def test_cache_save_creates_directory(tmp_path):
    """Test saving cache creates parent directory if needed."""
    nested_path = tmp_path / "subdir" / "deep" / "cache.json"
    cache = CacheManager(nested_path)
    cache.set("key", {"value": 1})
    cache.save_cache()
    assert nested_path.exists()


def test_cache_load_corrupted_file(tmp_path):
    """Test handling of corrupted cache file."""
    cache_file = tmp_path / "corrupted.json"
    cache_file.write_text("{invalid json content", encoding="utf-8")
    cache = CacheManager(cache_file)
    assert cache.size() == 0


def test_cache_large_dataset(cache_manager):
    """Test cache with many entries."""
    for i in range(100):
        cache_manager.set(f"key_{i}", {"score": i})
    assert cache_manager.size() == 100
    assert cache_manager.get("key_50") == {"score": 50}


def test_cache_concurrent_access(temp_cache_file):
    """Test concurrent cache access with threads."""
    import threading
    cache = CacheManager(temp_cache_file)
    errors = []

    def write_entries(start):
        try:
            for i in range(start, start + 20):
                cache.set(f"thread_key_{i}", {"value": i})
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=write_entries, args=(i * 20,)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0
    assert cache.size() == 100
