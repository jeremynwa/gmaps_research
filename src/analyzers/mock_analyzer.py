"""Mock analyzer for testing without API calls."""

import random
from typing import Dict, Optional

from config.settings import Config
from src.analyzers.base import BaseAnalyzer


class MockAnalyzer(BaseAnalyzer):
    """Mock analyzer that returns random scores (for testing)."""
    
    def analyze_review(
        self,
        establishment: str,
        site: str,
        review_text: str,
        author: str,
        note: int,
        date: str
    ) -> Optional[Dict[str, any]]:
        """Return mock analysis results."""
        
        # Skip empty reviews
        if not review_text or str(review_text).strip() == "" or len(str(review_text).strip()) < 20:
            return {criterion: "N/A" for criterion in Config.CRITERIA}
        
        # Generate random scores
        result = {}
        for criterion in Config.CRITERIA:
            if "_score" in criterion:
                # Random score (multiple of 10)
                result[criterion] = random.choice([10, 20, 30, 40, 50, 60, 70, 80, 90, 100, "N/A"])
            elif "_keyword" in criterion:
                # Random keyword
                keywords = ["café", "sandwich", "personnel", "service", "N/A"]
                result[criterion] = random.choice(keywords)
        
        return result