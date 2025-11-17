"""Cost calculation utilities."""

from dataclasses import dataclass
from typing import Optional
from config.settings import Config


@dataclass
class CostBreakdown:
    """Cost breakdown for an analysis."""
    outscraper_cost: float = 0.0
    claude_input_cost: float = 0.0
    claude_output_cost: float = 0.0
    claude_cache_write_cost: float = 0.0
    claude_cache_read_cost: float = 0.0
    
    @property
    def claude_total(self) -> float:
        """Total Claude API cost."""
        return (
            self.claude_input_cost + 
            self.claude_output_cost + 
            self.claude_cache_write_cost + 
            self.claude_cache_read_cost
        )
    
    @property
    def total(self) -> float:
        """Total cost."""
        return self.outscraper_cost + self.claude_total
    
    def __str__(self) -> str:
        """Human-readable cost breakdown."""
        return f"""Cost Breakdown:
  Outscraper:      ${self.outscraper_cost:.2f}
  Claude API:
    Input:         ${self.claude_input_cost:.2f}
    Output:        ${self.claude_output_cost:.2f}
    Cache Write:   ${self.claude_cache_write_cost:.2f}
    Cache Read:    ${self.claude_cache_read_cost:.2f}
    Subtotal:      ${self.claude_total:.2f}
  ─────────────────────────────
  TOTAL:           ${self.total:.2f}
"""


class CostCalculator:
    """Calculate costs for analysis runs."""
    
    @staticmethod
    def estimate_outscraper_cost(num_reviews: int) -> float:
        """
        Estimate Outscraper scraping cost.
        
        Args:
            num_reviews: Number of reviews to scrape
            
        Returns:
            Estimated cost in USD
        """
        return (num_reviews / 1000) * Config.OUTSCRAPER_PRICE_PER_1K
    
    @staticmethod
    def estimate_claude_cost(
        num_reviews: int,
        avg_input_tokens: int = 1800,
        avg_output_tokens: int = 600,
        cache_hit_rate: float = 0.98,
        cached_tokens: int = 1661
    ) -> CostBreakdown:
        """
        Estimate Claude API cost with prompt caching.
        
        Args:
            num_reviews: Number of reviews to analyze
            avg_input_tokens: Average input tokens per review
            avg_output_tokens: Average output tokens per review
            cache_hit_rate: Expected cache hit rate (0-1)
            cached_tokens: Number of tokens in cached prompt
            
        Returns:
            Cost breakdown
        """
        breakdown = CostBreakdown()
        
        if num_reviews == 0:
            return breakdown
        
        # First review creates cache
        first_review_input = avg_input_tokens
        breakdown.claude_cache_write_cost = (
            (first_review_input / 1_000_000) * 
            Config.CLAUDE_INPUT_PRICE * 
            Config.CLAUDE_CACHE_WRITE_MULTIPLIER
        )
        
        # Subsequent reviews use cache
        num_cached_reviews = num_reviews - 1
        num_cache_hits = int(num_cached_reviews * cache_hit_rate)
        num_cache_misses = num_cached_reviews - num_cache_hits
        
        # Cache hits (90% cheaper on cached portion)
        dynamic_tokens = avg_input_tokens - cached_tokens
        cache_hit_cost_per_review = (
            (cached_tokens / 1_000_000) * Config.CLAUDE_INPUT_PRICE * Config.CLAUDE_CACHE_READ_MULTIPLIER +
            (dynamic_tokens / 1_000_000) * Config.CLAUDE_INPUT_PRICE
        )
        breakdown.claude_cache_read_cost = num_cache_hits * cache_hit_cost_per_review
        
        # Cache misses (recreate cache)
        breakdown.claude_input_cost = num_cache_misses * (
            (avg_input_tokens / 1_000_000) * 
            Config.CLAUDE_INPUT_PRICE * 
            Config.CLAUDE_CACHE_WRITE_MULTIPLIER
        )
        
        # Output cost (same for all)
        breakdown.claude_output_cost = num_reviews * (
            (avg_output_tokens / 1_000_000) * 
            Config.CLAUDE_OUTPUT_PRICE
        )
        
        return breakdown
    
    @staticmethod
    def estimate_total_cost(
        num_reviews: int,
        include_outscraper: bool = True
    ) -> CostBreakdown:
        """
        Estimate total cost for an analysis.
        
        Args:
            num_reviews: Number of reviews
            include_outscraper: Whether to include scraping costs
            
        Returns:
            Complete cost breakdown
        """
        breakdown = CostCalculator.estimate_claude_cost(num_reviews)
        
        if include_outscraper:
            breakdown.outscraper_cost = CostCalculator.estimate_outscraper_cost(num_reviews)
        
        return breakdown