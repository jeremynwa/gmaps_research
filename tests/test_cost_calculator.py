"""Tests for cost calculator."""

import pytest
from src.utils.cost_calculator import CostCalculator, CostBreakdown


def test_outscraper_cost_basic():
    """Test basic outscraper cost calculation."""
    cost = CostCalculator.estimate_outscraper_cost(1000)
    assert cost > 0
    assert isinstance(cost, float)


def test_outscraper_cost_zero():
    """Test zero reviews cost."""
    cost = CostCalculator.estimate_outscraper_cost(0)
    assert cost == 0.0


def test_claude_cost_basic():
    """Test basic Claude cost calculation."""
    breakdown = CostCalculator.estimate_claude_cost(100)
    assert isinstance(breakdown, CostBreakdown)
    assert breakdown.claude_total > 0
    assert breakdown.claude_output_cost > 0


def test_claude_cost_zero_reviews():
    """Test Claude cost with zero reviews."""
    breakdown = CostCalculator.estimate_claude_cost(0)
    assert breakdown.claude_total == 0.0


def test_total_cost_with_outscraper():
    """Test total cost including outscraper."""
    breakdown = CostCalculator.estimate_total_cost(1000, include_outscraper=True)
    assert breakdown.outscraper_cost > 0
    assert breakdown.total > breakdown.claude_total


def test_total_cost_without_outscraper():
    """Test total cost without outscraper."""
    breakdown = CostCalculator.estimate_total_cost(1000, include_outscraper=False)
    assert breakdown.outscraper_cost == 0.0
    assert breakdown.total == breakdown.claude_total
