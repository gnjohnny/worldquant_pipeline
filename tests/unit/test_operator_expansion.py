"""Unit tests verifying expanded WorldQuant BRAIN operator suite."""
import pytest

from worldquant_pipeline.expressions.validator import ExpressionValidator


@pytest.fixture
def validator():
    return ExpressionValidator()


class TestExpandedOperators:
    """Verify newly whitelisted WorldQuant BRAIN operators parse and validate cleanly."""

    def test_time_series_correlation_and_covariance(self, validator):
        res1 = validator.validate_expression_string("ts_corr(close, volume, 20)")
        assert res1.is_valid is True
        assert "ts_corr" in res1.referenced_operators

        res2 = validator.validate_expression_string("ts_covariance(close, vwap, 30)")
        assert res2.is_valid is True

    def test_rolling_extremum_and_quantiles(self, validator):
        res_scale = validator.validate_expression_string("ts_scale(high, 20)")
        assert res_scale.is_valid is True

        res_median = validator.validate_expression_string("ts_median(close, 10)")
        assert res_median.is_valid is True

        res_zscore = validator.validate_expression_string("ts_zscore(close, 20)")
        assert res_zscore.is_valid is True

    def test_flexible_regression_operator(self, validator):
        # 3-arg version
        res3 = validator.validate_expression_string("ts_regression(close, volume, 60)")
        assert res3.is_valid is True

    def test_group_operators(self, validator):
        res_gz = validator.validate_expression_string("group_zscore(close, subindustry)")
        assert res_gz.is_valid is True

        res_gm = validator.validate_expression_string("group_mean(volume, subindustry)")
        assert res_gm.is_valid is True

        res_gs = validator.validate_expression_string("group_std_dev(close, sector)")
        assert res_gs.is_valid is True

    def test_conditional_trade_when(self, validator):
        res_tw = validator.validate_expression_string(
            "trade_when(close > vwap, group_rank(close, subindustry), -group_rank(close, subindustry))"
        )
        assert res_tw.is_valid is True
        assert "trade_when" in res_tw.referenced_operators

    def test_math_elementwise_operators(self, validator):
        res_exp = validator.validate_expression_string("exp(close)")
        assert res_exp.is_valid is True

        res_sqrt = validator.validate_expression_string("sqrt(volume)")
        assert res_sqrt.is_valid is True

        res_min = validator.validate_expression_string("min(close, open)")
        assert res_min.is_valid is True

        res_max = validator.validate_expression_string("max(close, vwap)")
        assert res_max.is_valid is True

        res_clamp = validator.validate_expression_string("clamp(close, 10, 100)")
        assert res_clamp.is_valid is True
