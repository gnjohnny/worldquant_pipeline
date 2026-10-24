"""Unit tests for Model domain and fundamental fields AST validation."""
import pytest

from worldquant_pipeline.config.settings import get_settings
from worldquant_pipeline.expressions.validator import ExpressionValidator


@pytest.fixture
def validator() -> ExpressionValidator:
    """Initialize ExpressionValidator with loaded settings."""
    settings = get_settings()
    return ExpressionValidator(
        allowed_operators=settings.get_allowed_operators(),
        allowed_fields=settings.get_allowed_fields(),
    )


def test_fundamental_operating_income_validation(validator: ExpressionValidator) -> None:
    """Verify operating_income / cap expressions pass Gate G1."""
    expr = "group_rank(operating_income / cap, subindustry)"
    res = validator.validate_expression_string(expr)
    assert res.is_valid, f"Validation failed: {res.errors}"
    assert "operating_income" in res.referenced_fields
    assert "cap" in res.referenced_fields
    assert "subindustry" in res.referenced_fields


def test_model_derivative_rank_validation(validator: ExpressionValidator) -> None:
    """Verify Model domain 11/2025 derivative fields pass Gate G1."""
    expr1 = "group_rank(cashflow_efficiency_rank_derivative + relative_valuation_rank_derivative, subindustry)"
    res1 = validator.validate_expression_string(expr1)
    assert res1.is_valid, f"Validation failed: {res1.errors}"
    assert "cashflow_efficiency_rank_derivative" in res1.referenced_fields
    assert "relative_valuation_rank_derivative" in res1.referenced_fields

    expr2 = "group_rank(analyst_revision_rank_derivative, subindustry) * -rank(ts_rank(close, 20))"
    res2 = validator.validate_expression_string(expr2)
    assert res2.is_valid, f"Validation failed: {res2.errors}"
    assert "analyst_revision_rank_derivative" in res2.referenced_fields

    expr3 = "group_rank(multi_factor_acceleration_score_derivative, subindustry)"
    res3 = validator.validate_expression_string(expr3)
    assert res3.is_valid, f"Validation failed: {res3.errors}"
    assert "multi_factor_acceleration_score_derivative" in res3.referenced_fields


def test_model_systematic_risk_metrics_validation(validator: ExpressionValidator) -> None:
    """Verify Systematic Risk Metrics fields pass Gate G1."""
    expr = "rank(unsystematic_risk_last_60_days) - rank(beta_last_60_days_spy)"
    res = validator.validate_expression_string(expr)
    assert res.is_valid, f"Validation failed: {res.errors}"
    assert "unsystematic_risk_last_60_days" in res.referenced_fields
    assert "beta_last_60_days_spy" in res.referenced_fields


def test_option_vrp_alpha_validation(validator: ExpressionValidator) -> None:
    """Verify submitted Option Volatility Risk Premium alpha passes Gate G1."""
    expr = "group_rank(ts_backfill(implied_volatility_call_720 / parkinson_volatility_120, 120), subindustry)"
    res = validator.validate_expression_string(expr)
    assert res.is_valid, f"Validation failed: {res.errors}"
    assert "implied_volatility_call_720" in res.referenced_fields
    assert "parkinson_volatility_120" in res.referenced_fields
    assert "subindustry" in res.referenced_fields
    assert "ts_backfill" in res.referenced_operators
    assert "group_rank" in res.referenced_operators


def test_model_catalog_completeness() -> None:
    """Verify all 40 Model domain fields and operating_income are in settings."""
    settings = get_settings()
    fields = settings.get_allowed_fields()

    # Fundamental
    assert "operating_income" in fields

    # Fundamental Scores (24 fields)
    expected_fscores = [
        "analyst_revision_rank_derivative",
        "cashflow_efficiency_rank_derivative",
        "composite_factor_score_derivative",
        "earnings_certainty_rank_derivative",
        "growth_potential_rank_derivative",
        "multi_factor_acceleration_score_derivative",
        "multi_factor_static_score_derivative",
        "relative_valuation_rank_derivative",
        "fscore_bfl_growth",
        "fscore_bfl_momentum",
        "fscore_bfl_profitability",
        "fscore_bfl_quality",
        "fscore_bfl_surface",
        "fscore_bfl_surface_accel",
        "fscore_bfl_total",
        "fscore_bfl_value",
        "fscore_growth",
        "fscore_momentum",
        "fscore_profitability",
        "fscore_quality",
        "fscore_surface",
        "fscore_surface_accel",
        "fscore_total",
        "fscore_value",
    ]
    for f in expected_fscores:
        assert f in fields, f"Missing field: {f}"

    # Systematic Risk Metrics (16 fields)
    expected_risk = [
        "beta_last_30_days_spy",
        "beta_last_60_days_spy",
        "beta_last_90_days_spy",
        "beta_last_360_days_spy",
        "correlation_last_30_days_spy",
        "correlation_last_60_days_spy",
        "correlation_last_90_days_spy",
        "correlation_last_360_days_spy",
        "systematic_risk_last_30_days",
        "systematic_risk_last_60_days",
        "systematic_risk_last_90_days",
        "systematic_risk_last_360_days",
        "unsystematic_risk_last_30_days",
        "unsystematic_risk_last_60_days",
        "unsystematic_risk_last_90_days",
        "unsystematic_risk_last_360_days",
    ]
    for f in expected_risk:
        assert f in fields, f"Missing field: {f}"
