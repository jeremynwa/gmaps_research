"""Orchestrator for managing analysis workflow."""

import time
import threading
from pathlib import Path
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

from config.settings import Config
from src.analyzers.base import BaseAnalyzer
from src.processors.cache_manager import CacheManager
from src.utils.progress_tracker import ProgressTracker


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
                if self.cache.exists(cache_key):
                    cached = self.cache.get(cache_key)
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
            
        except Exception as e:
            print(f"   ❌ Error analyzing review: {str(e)}")
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
            print(f"\n🚀 ANALYSIS STARTING")
            print(f"📊 Total reviews: {total}")
            print(f"⚡ Workers: {max_workers}")
            print(f"💾 Cache: {'Enabled' if self.use_cache else 'Disabled'}")
        
        tracker = ProgressTracker(total)
        results = []
        
        # Filter reviews (skip empty/short ones)
        reviews_to_analyze = []
        for review in reviews:
            review_text = str(review.get('Avis', ''))
            if len(review_text.strip()) >= 20:
                reviews_to_analyze.append(review)
            else:
                # Add with N/A scores
                scores = {criterion: "N/A" for criterion in Config.CRITERIA}
                results.append({**review, **scores})
                tracker.increment(was_skipped=True)
        
        if verbose:
            print(f"📝 Reviews to analyze: {len(reviews_to_analyze)}")
            print(f"⏭️  Skipped (too short): {tracker.stats.skipped}\n")
        
        if len(reviews_to_analyze) == 0:
            return pd.DataFrame(results)
        
        # ============================================================================
        # STEP 1: Analyze FIRST review alone to create cache
        # ============================================================================
        if verbose:
            print("🔄 Initializing Anthropic cache...")
        
        first_review = reviews_to_analyze[0]
        result, was_cached = self._analyze_single_review(first_review, tracker)
        results.append(result)
        
        if verbose:
            establishment = first_review.get('Establishment', 'N/A')
            site = first_review.get('Site', 'N/A')
            print(f"[1/{total}] {establishment} - {site}")
            if was_cached:
                print(f"   💾 From local cache")
            else:
                print(f"   📝 Anthropic cache initialized!\n")
        
        # Wait for cache to propagate
        time.sleep(5)
        
        # ============================================================================
        # STEP 2: Analyze rest in PARALLEL (uses cache!)
        # ============================================================================
        if len(reviews_to_analyze) > 1:
            if verbose:
                print(f"⚡ Processing {len(reviews_to_analyze) - 1} reviews with {max_workers} workers...\n")
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all remaining reviews
                futures = {
                    executor.submit(self._analyze_single_review, review, tracker): review
                    for review in reviews_to_analyze[1:]
                }
                
                # Collect results
                for i, future in enumerate(futures, start=2):
                    try:
                        result, was_cached = future.result()
                        results.append(result)
                        
                        if verbose and i % 10 == 0:
                            review = futures[future]
                            establishment = review.get('Establishment', 'N/A')
                            site = review.get('Site', 'N/A')
                            print(f"[{i}/{total}] {establishment} - {site}")
                            if was_cached:
                                print(f"   💾 Cache")
                            else:
                                print(f"   ✅ Analyzed")
                        
                        # Save cache periodically
                        if i % save_every == 0 and self.use_cache:
                            with self.cache_lock:
                                self.cache.save_cache()
                            if verbose:
                                print(f"\n   💾 Cache saved ({i}/{total})\n")
                    
                    except Exception as e:
                        print(f"   ❌ Error: {str(e)}")
                        review = futures[future]
                        scores = {criterion: "ERROR" for criterion in Config.CRITERIA}
                        results.append({**review, **scores})
        
        # Final cache save
        if self.use_cache:
            self.cache.save_cache()
        
        # Print final stats
        if verbose:
            print(f"\n✅ ANALYSIS COMPLETE")
            print(tracker.get_stats())
        
        return pd.DataFrame(results)