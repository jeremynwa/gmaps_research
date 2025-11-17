"""Base analyzer interface."""

from abc import ABC, abstractmethod
from typing import Dict, Optional


class BaseAnalyzer(ABC):
    """Base class for review analyzers."""
    
    @abstractmethod
    def analyze_review(
        self,
        establishment: str,
        site: str,
        review_text: str,
        author: str,
        note: int,
        date: str
    ) -> Optional[Dict[str, any]]:
        """
        Analyze a single review.
        
        Args:
            establishment: Restaurant/establishment name
            site: Location/site name
            review_text: Review text content
            author: Review author
            note: Rating (1-5)
            date: Review date
            
        Returns:
            Dictionary with scores and keywords, or None if error
        """
        pass