# ReviewInsight Core

AI-powered restaurant review analysis engine using Claude Sonnet 4 with prompt caching.

## Features

- 🤖 Claude Sonnet 4 analysis with 90% cost reduction via prompt caching
- 🌍 Google Maps review scraping via Outscraper
- 📊 Excel export with multiple sheets (Scores + Keywords)
- 🔄 Resumable analysis with local caching
- ⚡ Parallel processing (configurable workers)
- 💰 Real-time cost tracking

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Run analysis

**From CSV:**
```bash
python cli/main.py analyze --input data/input/reviews.csv --output data/output/
```

**From Google Maps:**
```bash
python cli/main.py scrape --name "McDonald's Paris Nord" --location "Paris, France" --max-reviews 2000
```

**With competitors:**
```bash
python cli/main.py scrape --name "McDonald's Paris Nord" \
  --competitors "Burger King Paris" "KFC Paris" \
  --location "Paris, France" \
  --max-reviews 2000
```

## Configuration

Edit `config/settings.py` or set environment variables:
```python
ANTHROPIC_API_KEY=sk-ant-...
OUTSCRAPER_API_KEY=...
MAX_WORKERS=10
MAX_TOKENS=1000
```

## Cost Estimation
```bash
python scripts/cost_estimator.py --reviews 2000
```

Output:
```
Estimated costs for 2,000 reviews:
  Outscraper:  $3.00
  Claude API:  $8.00 (with caching)
  Total:       $11.00
```

## Project Structure

- `src/analyzers/` - AI analysis logic
- `src/scrapers/` - Data collection (Outscraper, CSV)
- `src/processors/` - Orchestration & caching
- `src/exporters/` - Excel/JSON export
- `cli/` - Command-line interface
- `tests/` - Unit tests

## API Usage
```python
from src.scrapers import OutscraperScraper
from src.analyzers import AnthropicAnalyzer
from src.processors import Orchestrator
from src.exporters import ExcelExporter

# 1. Scrape reviews
scraper = OutscraperScraper(api_key="...")
reviews = scraper.scrape("McDonald's Paris", max_reviews=2000)

# 2. Analyze
analyzer = AnthropicAnalyzer(api_key="...")
orchestrator = Orchestrator(analyzer)
results = orchestrator.analyze(reviews, max_workers=10)

# 3. Export
exporter = ExcelExporter()
exporter.export(results, "output.xlsx")
```

## Development

Run tests:
```bash
pytest tests/
```

Run with mock analyzer (no API calls):
```bash
python cli/main.py analyze --input data/input/reviews.csv --mock
```

## License

MIT