"""Cache management for resumable analysis."""

import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class CacheManager:
    """Manage analysis cache for resumability."""

    def __init__(self, cache_file: Path):
        """
        Initialize cache manager.

        Args:
            cache_file: Path to cache file
        """
        self.cache_file = Path(cache_file)
        self.cache: Dict[str, Dict] = {}
        self.load_cache()

    def load_cache(self) -> None:
        """Load cache from file."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                logger.info("Cache loaded: %d entries", len(self.cache))
            except (json.JSONDecodeError, OSError) as e:
                logger.warning("Error loading cache: %s", e)
                self.cache = {}
        else:
            logger.info("New cache created")
            self.cache = {}

    def save_cache(self) -> None:
        """Save cache to file atomically."""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp_path = tempfile.mkstemp(
                dir=str(self.cache_file.parent),
                suffix='.tmp'
            )
            try:
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                    json.dump(self.cache, f, ensure_ascii=False, indent=2)
                os.replace(tmp_path, str(self.cache_file))
                logger.info(f"Cache saved: {len(self.cache)} entries")
            except Exception:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                raise
        except (OSError, PermissionError) as e:
            logger.error(f"Failed to save cache: {e}")

    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        return key in self.cache

    def get(self, key: str) -> Optional[Dict]:
        """Get value from cache."""
        return self.cache.get(key)

    def set(self, key: str, value: Dict) -> None:
        """Set value in cache."""
        self.cache[key] = value

    def clear(self) -> None:
        """Clear all cache."""
        self.cache = {}
        if self.cache_file.exists():
            self.cache_file.unlink()

    def size(self) -> int:
        """Get number of cached items."""
        return len(self.cache)
