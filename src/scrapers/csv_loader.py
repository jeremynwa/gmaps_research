"""Load reviews from CSV/Excel files."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd

from src.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class CSVLoader(BaseScraper):
    """Load reviews from CSV or Excel files."""
    
    REQUIRED_COLUMNS = [
        'Establishment',
        'Site',
        'Avis',
        'Auteur',
        'Note',
        'Date de l avis'
    ]
    
    def scrape(
        self,
        query: str,  # File path in this case
        location: str = "",
        max_reviews: Optional[int] = None,
        **kwargs
    ) -> List[Dict]:
        """
        Load reviews from file.
        
        Args:
            query: Path to CSV or Excel file
            location: Not used (for interface compatibility)
            max_reviews: Limit number of reviews (None = all)
            **kwargs: Additional pandas read parameters
            
        Returns:
            List of review dictionaries
        """
        file_path = Path(query)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        logger.info("Loading reviews from: %s", file_path.name)
        
        # Load file based on extension
        if file_path.suffix.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path, **kwargs)
        elif file_path.suffix.lower() == '.csv':
            df = pd.read_csv(file_path, **kwargs)
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
        
        # Validate columns
        missing_cols = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            logger.warning("Missing columns: %s", missing_cols)
            logger.warning("Available columns: %s", df.columns.tolist())
        
        # Limit reviews if specified
        if max_reviews and max_reviews < len(df):
            df = df.head(max_reviews)
        
        logger.info("Loaded %d reviews", len(df))
        
        # Convert to list of dicts
        reviews = df.to_dict('records')
        
        return reviews
    
    @staticmethod
    def validate_file(file_path: Path) -> tuple[bool, Optional[str]]:
        """
        Validate if file has required columns.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if file_path.suffix.lower() in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path, nrows=1)
            elif file_path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path, nrows=1)
            else:
                return False, f"Unsupported file type: {file_path.suffix}"
            
            missing_cols = [col for col in CSVLoader.REQUIRED_COLUMNS if col not in df.columns]
            
            if missing_cols:
                return False, f"Missing required columns: {missing_cols}"
            
            return True, None
            
        except Exception as e:
            return False, str(e)