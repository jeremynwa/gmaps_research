"""Orchestrator for managing analysis workflow."""

from __future__ import annotations

import logging
import time
import threading
from pathlib import Path
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd

from config.settings import Config
from src.analyzers.base import BaseAnalyzer
from src.processors.cache_manager import CacheManager
from src.utils.progress_tracker import ProgressTracker

logger = logging.getLogger(__name__)


class Orchestrator:
    """Orchestrate the analysis workflow."""
    
    def __init__(
        self,
        analyzer: BaseAnalyzer,
        cache_file: Optional[Path] = None,
        use_cache: bool = True
    ):
        """
        Initialize orchestrator.
        
        Args:
            analyzer: Analyzer instance to use
            cache_file: Path to cache file (uses Config.CACHE_FILE if None)
            use_cache: Whether to use caching
        """
        self.analyzer = analyzer
        self.use_cache = use_cache
        self.cache = CacheManager(cache_file or Config.CACHE_FILE)
        self.cache_lock = threading.Lock()
    
    def _create_cache_key(self, review: Dict) -> str:
        """Create unique cache key for a review."""
        cdpf = str(review.get('CDPF', ''))
        date = str(review.get('Date de l avis', ''))
        author = str(review.get('Auteur', ''))
        
        cache_key = f"{cdpf}_{date}_{author}"
        cache_key = cache_key.replace(' ', '_').replace('/', '_').replace(':', '_')
        
        return cache_key
    
    def _analyze_single_review(
        self,
        review: Dict,
        tracker: Optional[ProgressTracker] = None
    ) -> tuple[Dict, bool]:
        """
        Analyze a single review (thread-safe).
        
        Returns:
            Tuple of (result_dict, was_cached)
        """
        cache_key = self._create_cache_key(review)
        
        # Check cache
        if self.use_cache:
            with self.cache_lock:
                cached = self.cache.get(cache_key)
            if cached is not None:
                result = {**review, **cached}
                if tracker:
                    tracker.increment(was_cached=True)
                return result, True
        
        # Analyze
        establishment = str(review.get('Establishment', ''))
        site = str(review.get('Site', ''))
        review_text = str(review.get('Avis', ''))
        author = str(review.get('Auteur', ''))
        note = int(review.get('Note', 3))
        date = str(review.get('Date de l avis', ''))
        
        scores = {criterion: "N/A" for criterion in Config.CRITERIA}
        
        try:
            analysis_result = self.analyzer.analyze_review(
                establishment=establishment,
                site=site,
                review_text=review_text,
                author=author,
                note=note,
                date=date
            )
            
            if analysis_result:
                scores.update(analysis_result)
            
            # Cache result
            if self.use_cache:
                with self.cache_lock:
                    self.cache.set(cache_key, scores)
            
            if tracker:
                tracker.increment(was_cached=False)
            
            return {**review, **scores}, False
            
        except (ValueError, TypeError, KeyError) as e:
            logger.error("Error analyzing review: %s", e)
            if tracker:
                tracker.increment(was_error=True)
            return {**review, **scores}, False
    
    def analyze(
        self,
        reviews: List[Dict],
        max_workers: int = 10,
        save_every: int = 50,
        verbose: bool = True
    ) -> pd.DataFrame:
        """
        Analyze reviews with parallel processing and prompt caching optimization.
        
        Args:
            reviews: List of review dictionaries
            max_workers: Number of parallel workers
            save_every: Save cache every N reviews
            verbose: Print progress
            
        Returns:
            DataFrame with analysis results
        """
        total = len(reviews)
        
        if verbose:
            logger.info("ANALYSIS STARTING")
            logger.info("Total reviews: %d", total)
            logger.info("Workers: %d", max_workers)
            logger.info("Cache: %s", "Enabled" if self.use_cache else "Disabled")
        
        tracker = ProgressTracker(total)
        results = []
        
        # Filter reviews (skip empty/short ones)
        reviews_to_analyze = []
        for review in reviews:
            review_text = str(review.get('Avis', ''))
            if len(review_text.strip()) >= Config.MIN_REVIEW_LENGTH:
                reviews_to_analyze.append(review)
            else:
                # Add with N/A scores
                scores = {criterion: "N/A" for criterion in Config.CRITERIA}
                results.append({**review, **scores})
                tracker.increment(was_skipped=True)
        
        if verbose:
            logger.info("Reviews to analyze: %d", len(reviews_to_analyze))
            logger.info("Skipped (too short): %d", tracker.stats.skipped)
        
        if len(reviews_to_analyze) == 0:
            return pd.DataFrame(results)
        
        # ============================================================================
        # STEP 1: Analyze FIRST review alone to create cache
        # ============================================================================
        if verbose:
            logger.info("Initializing Anthropic cache...")
        
        first_review = reviews_to_analyze[0]
        result, was_cached = self._analyze_single_review(first_review, tracker)
        results.append(result)
        
        if verbose:
            establishment = first_review.get('Establishment', 'N/A')
            site = first_review.get('Site', 'N/A')
            logger.info("[1/%d] %s - %s", total, establishment, site)
            if was_cached:
                logger.info("From local cache")
            else:
                logger.info("Anthropic cache initialized!")
        
        # Wait for cache to propagate
        time.sleep(Config.CACHE_PROPAGATION_DELAY)
        
        # ============================================================================
        # STEP 2: Analyze rest in PARALLEL (uses cache!)
        # ============================================================================
        if len(reviews_to_analyze) > 1:
            if verbose:
                logger.info("Processing %d reviews with %d workers...", len(reviews_to_analyze) - 1, max_workers)
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all remaining reviews
                futures = {
                    executor.submit(self._analyze_single_review, review, tracker): review
                    for review in reviews_to_analyze[1:]
                }
                
                # Collect results
                for i, future in enumerate(as_completed(futures), start=2):
                    try:
                        result, was_cached = future.result(timeout=120)
                        results.append(result)
                        
                        if verbose and i % Config.PROGRESS_LOG_INTERVAL == 0:
                            review = futures[future]
                            establishment = review.get('Establishment', 'N/A')
                            site = review.get('Site', 'N/A')
                            logger.info("[%d/%d] %s - %s", i, total, establishment, site)
                            if was_cached:
                                logger.info("Cache hit")
                            else:
                                logger.info("Analyzed")
                        
                        # Save cache periodically
                        if i % save_every == 0 and self.use_cache:
                            with self.cache_lock:
                                self.cache.save_cache()
                            if verbose:
                                logger.info("Cache saved (%d/%d)", i, total)
                    
                    except (ValueError, TypeError, KeyError) as e:
                        logger.error("Error: %s", e)
                        review = futures[future]
                        scores = {criterion: "ERROR" for criterion in Config.CRITERIA}
                        results.append({**review, **scores})
        
        # Final cache save
        if self.use_cache:
            self.cache.save_cache()
        
        # Print final stats
        if verbose:
            logger.info("ANALYSIS COMPLETE")
            logger.info(tracker.get_stats())
        
        return pd.DataFrame(results)