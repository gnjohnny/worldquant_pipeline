"""Unit tests verifying registration and AST validation of Quant_data BRAIN fields."""
import pytest

from worldquant_pipeline.config.settings import get_settings
from worldquant_pipeline.expressions.validator import ExpressionValidator


@pytest.fixture
def validator() -> ExpressionValidator:
    """Initialize ExpressionValidator with fresh settings."""
    settings = get_settings()
    # Invalidate cache if needed
    settings._allowed_fields = None
    return ExpressionValidator(
        allowed_operators=settings.get_allowed_operators(),
        allowed_fields=settings.get_allowed_fields(),
    )


def test_quant_data_catalog_count() -> None:
    """Verify all 332 approved fields are loaded into settings."""
    settings = get_settings()
    settings._allowed_fields = None
    fields = settings.get_allowed_fields()
    assert len(fields) >= 332, f"Expected at least 332 fields, got {len(fields)}"


def test_analyst_domain_expressions(validator: ExpressionValidator) -> None:
    """Verify analyst consensus and revision fields pass Gate G1 AST validation."""
    # Earnings surprise proxy: actual vs forecast mean normalized by price
    expr1 = "group_rank((actual_eps_value_quarterly - anl4_afv4_eps_mean) / close, subindustry)"
    res1 = validator.validate_expression_string(expr1)
    assert res1.is_valid, f"Validation failed: {res1.errors}"
    assert "actual_eps_value_quarterly" in res1.referenced_fields
    assert "anl4_afv4_eps_mean" in res1.referenced_fields

    # Cash flow revision and analyst buy recommendation conviction
    expr2 = "rank(anl4_afv4_cfps_median) * rank(anl4_buy)"
    res2 = validator.validate_expression_string(expr2)
    assert res2.is_valid, f"Validation failed: {res2.errors}"
    assert "anl4_afv4_cfps_median" in res2.referenced_fields
    assert "anl4_buy" in res2.referenced_fields


def test_relationship_domain_expressions(validator: ExpressionValidator) -> None:
    """Verify relationship and competitor network fields pass Gate G1 AST validation."""
    # Competitor PageRank vs Customer Return Signal
    expr = "group_rank(pv13_com_page_rank * pv13_custretsig_retsig, sector)"
    res = validator.validate_expression_string(expr)
    assert res.is_valid, f"Validation failed: {res.errors}"
    assert "pv13_com_page_rank" in res.referenced_fields
    assert "pv13_custretsig_retsig" in res.referenced_fields


def test_option_analytics_expressions(validator: ExpressionValidator) -> None:
    """Verify call breakeven and option surface fields pass Gate G1 AST validation."""
    # Call breakeven premium ratio
    expr = "group_rank((call_breakeven_10 - close) / close, subindustry)"
    res = validator.validate_expression_string(expr)
    assert res.is_valid, f"Validation failed: {res.errors}"
    assert "call_breakeven_10" in res.referenced_fields
    assert "close" in res.referenced_fields


def test_volatility_domain_expressions(validator: ExpressionValidator) -> None:
    """Verify term-structure volatility fields pass Gate G1 AST validation."""
    # Volatility term-structure curve slope (short vs long term)
    expr = "group_rank(historical_volatility_20 / historical_volatility_180, subindustry)"
    res = validator.validate_expression_string(expr)
    assert res.is_valid, f"Validation failed: {res.errors}"
    assert "historical_volatility_20" in res.referenced_fields
    assert "historical_volatility_180" in res.referenced_fields
