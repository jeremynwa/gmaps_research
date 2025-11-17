"""Base scraper interface."""

from abc import ABC, abstractmethod
from typing import List, Dict


class BaseScraper(ABC):
    """Base class for review scrapers."""
    
    @abstractmethod
    def scrape(
        self,
        query: str,
        location: str = "",
        max_reviews: int = 1000,
        **kwargs
    ) -> List[Dict]:
        """
        Scrape reviews.
        
        Args:
            query: Search query (restaurant name, etc.)
            location: Location filter
            max_reviews: Maximum number of reviews to fetch
            **kwargs: Additional scraper-specific parameters
            
        Returns:
            List of review dictionaries
        """
        pass