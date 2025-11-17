.PHONY: help install install-dev test lint format clean docker-build docker-run

help:
	@echo "ReviewInsight Core - Makefile Commands"
	@echo "======================================"
	@echo "install          - Install production dependencies"
	@echo "install-dev      - Install development dependencies"
	@echo "test             - Run tests with coverage"
	@echo "lint             - Run linting (flake8, mypy)"
	@echo "format           - Format code (black, isort)"
	@echo "clean            - Remove build artifacts"
	@echo "docker-build     - Build Docker image"
	@echo "docker-run       - Run in Docker container"
	@echo "estimate         - Estimate costs (usage: make estimate REVIEWS=2000)"

install:
	pip install -r requirements.txt
	pip install -e .

install-dev:
	pip install -r requirements.txt
	pip install -e ".[dev]"

test:
	pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

lint:
	flake8 src/ cli/ config/
	mypy src/ cli/ config/

format:
	black src/ cli/ config/ tests/
	isort src/ cli/ config/ tests/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docker-build:
	docker-compose build

docker-run:
	docker-compose up -d
	docker-compose exec reviewinsight bash

estimate:
	python scripts/cost_estimator.py $(REVIEWS)

analyze:
	python -m cli.main analyze --input $(INPUT) --workers $(WORKERS)

scrape:
	python -m cli.main scrape --name "$(NAME)" --location "$(LOCATION)" --max-reviews $(REVIEWS)