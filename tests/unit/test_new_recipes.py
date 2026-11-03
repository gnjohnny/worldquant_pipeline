"""Unit tests verifying diverse non-templated alpha recipe architectures."""
import pytest

from worldquant_pipeline.expressions.recipes import AlphaRecipeGenerator
from worldquant_pipeline.expressions.validator import ExpressionValidator


@pytest.fixture
def validator():
    return ExpressionValidator()


class TestNewRecipes:
    """Verify newly added formula architectures pass Gate G1 AST validation."""

    def test_conditional_regime_switch(self, validator):
        expr = AlphaRecipeGenerator.conditional_regime_switch(
            regime_condition="historical_volatility_30 > 0.25",
            offensive_factor="actual_cashflow_per_share_value_quarterly",
            defensive_factor="cash_st",
            group="subindustry",
        )
        res = validator.validate_expression_string(expr)
        assert res.is_valid is True
        assert "trade_when" in res.referenced_operators

    def test_ratio_dispersion_spread(self, validator):
        expr = AlphaRecipeGenerator.ratio_dispersion_spread(
            factor_numerator="ts_backfill(anl4_cfo_value, 60)",
            factor_denominator="close",
            group="subindustry",
        )
        res = validator.validate_expression_string(expr)
        assert res.is_valid is True
        assert "group_zscore" in res.referenced_operators

    def test_rolling_correlation_breakout(self, validator):
        expr = AlphaRecipeGenerator.rolling_correlation_breakout(
            factor_x="close",
            factor_y="volume",
            lookback=20,
            group="subindustry",
        )
        res = validator.validate_expression_string(expr)
        assert res.is_valid is True
        assert "ts_corr" in res.referenced_operators

    def test_lead_lag_regression(self, validator):
        expr = AlphaRecipeGenerator.lead_lag_regression(
            dependent_factor="close",
            independent_factor="ts_backfill(anl4_afv4_median_eps, 60)",
            lookback=60,
            group="subindustry",
        )
        res = validator.validate_expression_string(expr)
        assert res.is_valid is True
        assert "ts_regression" in res.referenced_operators

    def test_channel_breakout_normalization(self, validator):
        expr = AlphaRecipeGenerator.channel_breakout_normalization(
            value_field="close",
            lookback=20,
            group="subindustry",
        )
        res = validator.validate_expression_string(expr)
        assert res.is_valid is True
        assert "ts_scale" in res.referenced_operators

    def test_discrete_bucket_neutralization(self, validator):
        expr = AlphaRecipeGenerator.discrete_bucket_neutralization(
            factor="actual_cashflow_per_share_value_quarterly",
            bucket_range="0.1, 0.9, 0.1",
            group="subindustry",
        )
        res = validator.validate_expression_string(expr)
        assert res.is_valid is True
        assert "bucket" in res.referenced_operators
