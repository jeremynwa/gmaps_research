"""Simple script to run analysis - use this instead of the old file."""
import fix_paths  # Fix import paths

from pathlib import Path
from src.scrapers.csv_loader import CSVLoader
from src.analyzers.anthropic_analyzer import AnthropicAnalyzer
from src.processors.orchestrator import Orchestrator
from src.exporters.excel_exporter import ExcelExporter

# Configuration
INPUT_FILE = "data/input/BDD_reviews.xlsx"  # Change this to your file
MAX_WORKERS = 10

def main():
    print("🚀 Starting Analysis...\n")
    
    # 1. Load reviews
    print("📁 Loading reviews...")
    loader = CSVLoader()
    reviews = loader.scrape(INPUT_FILE)
    print(f"   Loaded {len(reviews)} reviews\n")
    
    # 2. Initialize analyzer
    print("🤖 Initializing Claude analyzer...")
    analyzer = AnthropicAnalyzer()
    
    # 3. Run analysis
    print("⚡ Running analysis...")
    orchestrator = Orchestrator(analyzer)
    results_df = orchestrator.analyze(reviews, max_workers=MAX_WORKERS)
    
    # 4. Export results
    print("\n💾 Exporting results...")
    output_file = ExcelExporter.export(results_df)
    
    print(f"\n✅ Done! Results saved to: {output_file}")

if __name__ == "__main__":
    main()