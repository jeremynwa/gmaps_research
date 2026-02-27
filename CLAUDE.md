# ReviewInsight Core

AI-powered restaurant review analysis engine. Analyzes Google Maps reviews using Claude Sonnet 4 with prompt caching (90% cost reduction), exports scored results to Excel/JSON.

## Architecture

```
cli/main.py -> src/analyzers/, scrapers/, processors/, exporters/, utils/ -> config/
```

- `cli/main.py` - Click CLI (analyze, scrape, estimate, config commands)
- `src/analyzers/` - AI analysis (AnthropicAnalyzer, MockAnalyzer extend BaseAnalyzer)
- `src/scrapers/` - Data ingestion (OutscraperScraper, CSVLoader extend BaseScraper)
- `src/processors/` - Orchestrator (threading, cache coordination) + CacheManager
- `src/exporters/` - ExcelExporter (2 sheets: Scores + Keywords), JSONExporter
- `src/utils/` - CostCalculator, ProgressTracker, GareNormalizer
- `config/` - Settings (API keys, constants, criteria) + Prompts (French analysis prompt)

## Commands

```bash
# Run tests
pytest tests/ --cov=src

# Format code
black src/ cli/ config/ tests/ && isort src/ cli/ config/ tests/

# Lint
flake8 src/ cli/ config/ && mypy src/ cli/ config/

# Run analysis (mock, no API calls)
python cli/main.py analyze --input data/input/reviews.csv --mock

# Run analysis (real)
python cli/main.py analyze --input data/input/reviews.csv --workers 10

# Scrape Google Maps
python cli/main.py scrape --name "McDonald's Paris" --location "Paris, France" --max-reviews 2000

# Cost estimate
python cli/main.py estimate --reviews 2000 --scraping
```

## Code Conventions

- Python 3.9+ (no `X | Y` union syntax; use `Optional[X]` and `Union[X, Y]`)
- Type hints on all public functions (use `typing.Any`, never bare `any`)
- Logging via `logging` module, never bare `print()`
- Constants in `config/settings.py`, never hardcoded magic numbers
- Line length: 100 (Black config in pyproject.toml)
- Import ordering: stdlib -> third-party -> local (enforced by isort)

## Testing

- Tests in `tests/` directory, files named `test_*.py`
- Use `pytest` with fixtures from `conftest.py`
- Mock external APIs (Anthropic, Outscraper) - never make real API calls in tests
- Target: every public method has at least one happy-path and one error-path test

## Key Design Decisions

- BaseAnalyzer ABC defines the analyzer contract; input validation lives in the base class
- CacheManager handles local JSON caching for resume support
- Orchestrator manages threading, cache coordination, and progress tracking
- Config class reads from environment/.env; never import `os.getenv` elsewhere
- All user-facing output goes through `rich` console or `logging`; no bare `print()`
- First review analyzed alone to initialize Anthropic prompt cache, then parallel
