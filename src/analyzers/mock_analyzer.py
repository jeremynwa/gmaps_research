"""Mock analyzer for testing without API calls."""

import random
from typing import Any, Dict, Optional

from config.settings import Config
from src.analyzers.base import BaseAnalyzer


class MockAnalyzer(BaseAnalyzer):
    """Mock analyzer that returns random scores (for testing)."""

    def _analyze_review_impl(
        self,
        establishment: str,
        site: str,
        review_text: str,
        author: str,
        note: int,
        date: str
    ) -> Optional[Dict[str, Any]]:
        """Return mock analysis results."""

        # Generate random scores
        result = {}
        for criterion in Config.CRITERIA:
            if "_score" in criterion:
                # Random score (multiple of 10)
                result[criterion] = random.choice([10, 20, 30, 40, 50, 60, 70, 80, 90, 100, "N/A"])
            elif "_keyword" in criterion:
                # Random keyword
                keywords = ["cafe", "sandwich", "personnel", "service", "N/A"]
                result[criterion] = random.choice(keywords)

        return result
