"""Cache management for resumable analysis."""

import json
from pathlib import Path
from typing import Dict, Optional


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
                print(f"✅ Cache chargé: {len(self.cache)} entrées")
            except Exception as e:
                print(f"⚠️ Erreur chargement cache: {e}")
                self.cache = {}
        else:
            print(f"📝 Nouveau cache créé")
            self.cache = {}
    
    def save_cache(self) -> None:
        """Save cache to file."""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Erreur sauvegarde cache: {e}")
    
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