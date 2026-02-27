"""Tests for JSON exporter."""

import json
import pytest
import pandas as pd
from pathlib import Path

from src.exporters.json_exporter import JSONExporter
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
    """Test basic JSON export."""
    output_path = tmp_path / "test_output.json"
    result_path = JSONExporter.export(sample_results_df, output_path=output_path)
    assert result_path.exists()

    with open(result_path, encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert len(data) == 2


def test_export_pretty(sample_results_df, tmp_path):
    """Test pretty JSON export."""
    output_path = tmp_path / "pretty.json"
    JSONExporter.export(sample_results_df, output_path=output_path, pretty=True)
    content = output_path.read_text(encoding="utf-8")
    assert "\n" in content  # pretty-printed has newlines


def test_export_compact(sample_results_df, tmp_path):
    """Test compact JSON export."""
    output_path = tmp_path / "compact.json"
    JSONExporter.export(sample_results_df, output_path=output_path, pretty=False)
    content = output_path.read_text(encoding="utf-8")
    # Compact JSON has no indentation
    lines = content.strip().split("\n")
    assert len(lines) == 1
