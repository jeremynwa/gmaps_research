"""Tests for Excel exporter."""

import pytest
import pandas as pd
from pathlib import Path

from src.exporters.excel_exporter import ExcelExporter
from config.settings import Config


@pytest.fixture
def sample_results_df(sample_reviews):
    """Create a DataFrame with mock analysis results."""
    rows = []
    for review in sample_reviews:
        row = dict(review)
        for criterion in Config.CRITERIA:
            row[criterion] = 50 if "_score" in criterion else "test"
        rows.append(row)
    return pd.DataFrame(rows)


def test_export_basic(sample_results_df, tmp_path):
    """Test basic Excel export."""
    output_path = tmp_path / "test_output.xlsx"
    result_path = ExcelExporter.export(sample_results_df, output_path=output_path)
    assert result_path.exists()
    assert result_path.suffix == ".xlsx"


def test_export_two_sheets(sample_results_df, tmp_path):
    """Test Excel has Scores and Keywords sheets."""
    output_path = tmp_path / "test_sheets.xlsx"
    ExcelExporter.export(sample_results_df, output_path=output_path)

    xls = pd.ExcelFile(output_path)
    assert "Scores" in xls.sheet_names
    assert "Keywords" in xls.sheet_names


def test_export_auto_filename(sample_results_df, tmp_path):
    """Test auto-generated filename with timestamp."""
    # Patch Config.OUTPUT_DIR to use tmp_path
    import config.settings
    original = config.settings.Config.OUTPUT_DIR
    config.settings.Config.OUTPUT_DIR = tmp_path
    try:
        result_path = ExcelExporter.export(sample_results_df)
        assert result_path.exists()
        assert "ReviewInsight" in result_path.name
    finally:
        config.settings.Config.OUTPUT_DIR = original


def test_export_creates_directory(sample_results_df, tmp_path):
    """Test export creates parent directory if needed."""
    output_path = tmp_path / "subdir" / "output.xlsx"
    result_path = ExcelExporter.export(sample_results_df, output_path=output_path)
    assert result_path.exists()
