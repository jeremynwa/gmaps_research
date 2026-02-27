"""Tests for CSV loader."""

import pytest
import pandas as pd
from pathlib import Path

from src.scrapers.csv_loader import CSVLoader


def test_load_csv_basic(sample_csv_file):
    """Test loading a valid CSV file."""
    loader = CSVLoader()
    reviews = loader.scrape(str(sample_csv_file))
    assert len(reviews) == 2
    assert isinstance(reviews, list)
    assert isinstance(reviews[0], dict)


def test_load_excel_basic(sample_excel_file):
    """Test loading a valid Excel file."""
    loader = CSVLoader()
    reviews = loader.scrape(str(sample_excel_file))
    assert len(reviews) == 2


def test_load_nonexistent_file():
    """Test loading a nonexistent file raises error."""
    loader = CSVLoader()
    with pytest.raises(FileNotFoundError):
        loader.scrape("/nonexistent/file.csv")


def test_load_unsupported_format(tmp_path):
    """Test loading unsupported file format."""
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("hello", encoding="utf-8")
    loader = CSVLoader()
    with pytest.raises(ValueError, match="Unsupported file type"):
        loader.scrape(str(txt_file))


def test_load_max_reviews_limit(sample_csv_file):
    """Test limiting number of reviews."""
    loader = CSVLoader()
    reviews = loader.scrape(str(sample_csv_file), max_reviews=1)
    assert len(reviews) == 1


def test_load_empty_csv(tmp_path):
    """Test loading CSV with headers but no data rows."""
    csv_file = tmp_path / "empty.csv"
    df = pd.DataFrame(columns=['Establishment', 'Site', 'Avis', 'Auteur', 'Note', 'Date de l avis'])
    df.to_csv(csv_file, index=False)
    loader = CSVLoader()
    reviews = loader.scrape(str(csv_file))
    assert len(reviews) == 0


def test_validate_file_valid(sample_csv_file):
    """Test validating a valid file."""
    is_valid, error = CSVLoader.validate_file(Path(sample_csv_file))
    assert is_valid
    assert error is None


def test_validate_file_missing_columns(tmp_path):
    """Test validating a file with missing columns."""
    csv_file = tmp_path / "bad.csv"
    pd.DataFrame({"col1": [1], "col2": [2]}).to_csv(csv_file, index=False)
    is_valid, error = CSVLoader.validate_file(Path(csv_file))
    assert not is_valid
    assert "Missing" in error
