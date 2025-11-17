"""Standalone cost estimation script."""

import sys
from src.utils.cost_calculator import CostCalculator


def main():
    """Estimate costs from command line."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/cost_estimator.py <num_reviews> [--with-scraping]")
        sys.exit(1)
    
    try:
        num_reviews = int(sys.argv[1])
    except ValueError:
        print("Error: Number of reviews must be an integer")
        sys.exit(1)
    
    include_scraping = "--with-scraping" in sys.argv
    
    cost = CostCalculator.estimate_total_cost(num_reviews, include_outscraper=include_scraping)
    
    print(f"\n{'='*50}")
    print(f"  Cost Estimation for {num_reviews:,} Reviews")
    print(f"{'='*50}")
    print(cost)
    
    if num_reviews >= 10000:
        print("💡 Tip: For large analyses (10k+ reviews), consider:")
        print("   • Running in batches")
        print("   • Using multiple API keys if available")
        print("   • Monitoring costs in real-time")


if __name__ == '__main__':
    main()