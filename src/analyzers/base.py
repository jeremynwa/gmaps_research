"""Base analyzer interface."""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from config.settings import Config

logger = logging.getLogger(__name__)


class BaseAnalyzer(ABC):
    """Base class for review analyzers."""

    def analyze_review(
        self,
        establishment: str,
        site: str,
        review_text: str,
        author: str,
        note: int,
        date: str,
    ) -> Optional[Dict[str, Any]]:
        """Analyze a single review with input validation.

        Returns:
            Dictionary with scores and keywords, or None if error
        """
        # Skip empty reviews
        if not review_text or str(review_text).strip() == "" or str(review_text).lower() == "nan":
            return {criterion: "N/A" for criterion in Config.CRITERIA}

        # Skip very short reviews
        if len(str(review_text).strip()) < Config.MIN_REVIEW_LENGTH:
            return {criterion: "N/A" for criterion in Config.CRITERIA}

        return self._analyze_review_impl(
            establishment, site, review_text, author, note, date
        )

    @abstractmethod
    def _analyze_review_impl(
        self,
        establishment: str,
        site: str,
        review_text: str,
        author: str,
        note: int,
        date: str,
    ) -> Optional[Dict[str, Any]]:
        """Subclass implementation. Called only for valid reviews."""
        pass
