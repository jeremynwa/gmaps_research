"""Quick single review analysis script."""

from src.analyzers.anthropic_analyzer import AnthropicAnalyzer
from config.prompts import RESTAURANT_ANALYSIS_PROMPT


def main():
    """Analyze a single review quickly."""
    
    # Example review
    review_text = """
    Excellent café ! Le croissant était frais et le service très rapide.
    Le personnel est vraiment sympathique. Peut-être un peu cher mais 
    la qualité est au rendez-vous. Je recommande !
    """
    
    print("\n🔍 Analyzing single review...\n")
    print(f"Review: {review_text.strip()}\n")
    
    # Initialize analyzer
    analyzer = AnthropicAnalyzer()
    
    # Analyze
    result = analyzer.analyze_review(
        establishment="Paul",
        site="Paris Gare de Lyon",
        review_text=review_text,
        author="Test User",
        note=5,
        date="2025-01-17"
    )
    
    print("📊 Results:")
    print("-" * 50)
    
    if result:
        # Print scores
        for key, value in result.items():
            if "_score" in key:
                criterion_name = key.replace("_score", "")
                keyword_key = f"{criterion_name}_keyword"
                keyword = result.get(keyword_key, "N/A")
                
                if value != "N/A":
                    print(f"  {criterion_name}: {value}/100 (keyword: {keyword})")
    else:
        print("  ❌ Analysis failed")


if __name__ == '__main__':
    main()