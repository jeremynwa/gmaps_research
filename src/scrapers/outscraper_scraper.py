"""Google Maps scraper using Outscraper API."""

from typing import List, Dict, Optional
from outscraper import ApiClient

from config.settings import Config
from src.scrapers.base import BaseScraper


class OutscraperScraper(BaseScraper):
    """Scrape Google Maps reviews using Outscraper."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Outscraper client.
        
        Args:
            api_key: Outscraper API key (uses Config.OUTSCRAPER_API_KEY if None)
        """
        self.client = ApiClient(api_key=api_key or Config.OUTSCRAPER_API_KEY)
    
    def scrape(
        self,
        query: str,
        location: str = "",
        max_reviews: int = 1000,
        language: str = "fr",
        **kwargs
    ) -> List[Dict]:
        """
        Scrape Google Maps reviews.
        
        Args:
            query: Restaurant name or Google Maps URL
            location: Location filter (e.g., "Paris, France")
            max_reviews: Maximum reviews to fetch
            language: Language code (default: fr)
            **kwargs: Additional Outscraper parameters
            
        Returns:
            List of review dictionaries with standardized format
        """
        print(f"🔍 Scraping Google Maps: {query}")
        if location:
            print(f"   📍 Location: {location}")
        print(f"   📊 Max reviews: {max_reviews}")
        
        try:
            # Build search query
            if location and location not in query:
                search_query = f"{query}, {location}"
            else:
                search_query = query
            
            # Call Outscraper API
            results = self.client.google_maps_reviews(
                search_query,
                reviews_limit=max_reviews,
                language=language,
                **kwargs
            )
            
            if not results or len(results) == 0:
                print(f"   ⚠️ No results found")
                return []
            
            # Extract and standardize reviews
            reviews = []
            for place in results:
                place_name = place.get('name', query)
                place_address = place.get('full_address', location)
                
                for review in place.get('reviews_data', []):
                    reviews.append({
                        'Establishment': place_name,
                        'Site': place_address,
                        'Avis': review.get('review_text', ''),
                        'Auteur': review.get('author_title', 'Anonymous'),
                        'Note': review.get('review_rating', 3),
                        'Date de l avis': review.get('review_datetime_utc', ''),
                        'CDPF': f"{place_name}_{review.get('review_id', '')}",
                        # Additional metadata
                        'review_likes': review.get('review_likes', 0),
                        'owner_answer': review.get('owner_answer', ''),
                        'owner_answer_timestamp': review.get('owner_answer_timestamp_datetime_utc', ''),
                    })
            
            print(f"   ✅ Scraped {len(reviews)} reviews")
            return reviews
            
        except Exception as e:
            print(f"   ❌ Error scraping: {str(e)}")
            return []
    
    def scrape_multiple(
        self,
        queries: List[str],
        location: str = "",
        max_reviews_per_query: int = 1000,
        **kwargs
    ) -> Dict[str, List[Dict]]:
        """
        Scrape multiple restaurants/competitors.
        
        Args:
            queries: List of restaurant names
            location: Location filter
            max_reviews_per_query: Max reviews per restaurant
            **kwargs: Additional parameters
            
        Returns:
            Dictionary mapping query to reviews
        """
        results = {}
        
        for query in queries:
            print(f"\n{'='*60}")
            reviews = self.scrape(
                query=query,
                location=location,
                max_reviews=max_reviews_per_query,
                **kwargs
            )
            results[query] = reviews
        
        return results