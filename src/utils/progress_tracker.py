"""Progress tracking utilities."""

import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ProgressStats:
    """Statistics for analysis progress."""
    total: int
    analyzed: int = 0
    cache_hits: int = 0
    errors: int = 0
    skipped: int = 0
    start_time: float = field(default_factory=time.time)
    
    @property
    def percent(self) -> float:
        """Percentage complete."""
        if self.total == 0:
            return 0.0
        return (self.analyzed / self.total) * 100
    
    @property
    def elapsed_seconds(self) -> float:
        """Elapsed time in seconds."""
        return time.time() - self.start_time
    
    @property
    def elapsed_formatted(self) -> str:
        """Formatted elapsed time."""
        seconds = int(self.elapsed_seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    
    @property
    def eta_seconds(self) -> Optional[float]:
        """Estimated time remaining in seconds."""
        if self.analyzed == 0:
            return None
        
        rate = self.analyzed / self.elapsed_seconds
        remaining = self.total - self.analyzed
        
        if rate == 0:
            return None
        
        return remaining / rate
    
    @property
    def eta_formatted(self) -> str:
        """Formatted ETA."""
        eta = self.eta_seconds
        if eta is None:
            return "Unknown"
        
        seconds = int(eta)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m"
        else:
            return f"{secs}s"
    
    @property
    def cache_hit_rate(self) -> float:
        """Cache hit rate percentage."""
        if self.analyzed == 0:
            return 0.0
        return (self.cache_hits / self.analyzed) * 100
    
    def __str__(self) -> str:
        """Human-readable progress."""
        return f"""Progress: {self.analyzed}/{self.total} ({self.percent:.1f}%)
  Cache hits: {self.cache_hits} ({self.cache_hit_rate:.1f}%)
  Errors: {self.errors}
  Skipped: {self.skipped}
  Elapsed: {self.elapsed_formatted}
  ETA: {self.eta_formatted}
"""


class ProgressTracker:
    """Track progress of analysis."""
    
    def __init__(self, total: int):
        self.stats = ProgressStats(total=total)
    
    def increment(self, was_cached: bool = False, was_error: bool = False, was_skipped: bool = False):
        """Increment progress counters."""
        if was_skipped:
            self.stats.skipped += 1
        elif was_error:
            self.stats.errors += 1
        else:
            self.stats.analyzed += 1
            if was_cached:
                self.stats.cache_hits += 1
    
    def get_stats(self) -> ProgressStats:
        """Get current statistics."""
        return self.stats