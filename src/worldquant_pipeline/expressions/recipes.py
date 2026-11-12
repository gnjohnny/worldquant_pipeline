"""Advanced quantitative alpha formula recipes and convexity generators.

Provides structural alternatives to flat linear sums, implementing:
1. Conditional Regime Switches (trade_when & market state conditioning)
2. Ratio Dispersion & Z-Score Spreads
3. Rolling Correlation & Lead-Lag Regressions
4. Volatility-Normalized Quality
5. Channel Breakout & Extremum Normalization
6. Discrete Bucket Neutralization
7. Vector Neutralized Orthogonal Residuals
8. Multiplicative Cross-Factor Synergy
"""


class AlphaRecipeGenerator:
    """Generates deterministic, AST-compliant WorldQuant BRAIN alpha expressions."""

    @staticmethod
    def conditional_regime_switch(
        regime_condition: str,
        offensive_factor: str,
        defensive_factor: str,
        group: str = "subindustry",
    ) -> str:
        """Create a regime-conditioned alpha switching between offensive and defensive factors.

        Uses trade_when(condition, alpha, exit) or ternary conditional logic to avoid
        forcing stationary parameters across all market regimes.
        """
        return (
            f"trade_when({regime_condition}, "
            f"group_rank({offensive_factor}, {group}), "
            f"group_rank({defensive_factor}, {group}))"
        )

    @staticmethod
    def ratio_dispersion_spread(
        factor_numerator: str,
        factor_denominator: str,
        group: str = "subindustry",
        epsilon: float = 0.001,
    ) -> str:
        """Create a continuous ratio spread standardized via group z-score.

        Preserves cross-sectional tails and informational dispersion rather than
        compressing everything into uniform percentile ranks.
        """
        ratio_expr = f"{factor_numerator} / ({factor_denominator} + {epsilon})"
        return f"group_zscore({ratio_expr}, {group})"

    @staticmethod
    def rolling_correlation_breakout(
        factor_x: str,
        factor_y: str,
        lookback: int = 20,
        group: str = "subindustry",
    ) -> str:
        """Create a time-series correlation anomaly alpha: group_rank(ts_corr(x, y, d), group).

        Measures co-movement decoupling between complementary factors (e.g., volume and returns,
        or option implied volatility and realized price moves).
        """
        return f"group_rank(ts_corr({factor_x}, {factor_y}, {lookback}), {group})"

    @staticmethod
    def lead_lag_regression(
        dependent_factor: str,
        independent_factor: str,
        lookback: int = 60,
        group: str = "subindustry",
    ) -> str:
        """Create a time-series regression sensitivity alpha via ts_regression.

        Extracts rolling beta or elasticity between two economic series.
        """
        return f"group_rank(ts_regression({dependent_factor}, {independent_factor}, {lookback}), {group})"

    @staticmethod
    def channel_breakout_normalization(
        value_field: str = "close",
        lookback: int = 20,
        group: str = "subindustry",
    ) -> str:
        """Create an extremum range oscillator via WorldQuant native ts_scale: (x - min) / (max - min).

        Evaluates where current price or metric sits within its rolling dynamic channel.
        """
        return f"group_rank(ts_scale({value_field}, {lookback}), {group})"

    @staticmethod
    def discrete_bucket_neutralization(
        factor: str,
        bucket_range: str = "0.1, 0.9, 0.1",
        group: str = "subindustry",
    ) -> str:
        """Create a discrete bucketed allocation stripping out extreme non-linear noise."""
        ranked = f"group_rank({factor}, {group})"
        return f"group_neutralize(bucket({ranked}, range=\"{bucket_range}\"), {group})"

    @staticmethod
    def multiplicative_synergy(
        factor_a: str,
        factor_b: str,
        group: str = "subindustry",
        reversal_overlay: bool = False,
        reversal_weight: float = 0.15,
        reversal_lookback: int = 3,
    ) -> str:
        """Create a multiplicative synergy alpha: rank(A) * rank(B).

        Acts as a soft logical AND condition where securities must exhibit strength in
        both factors simultaneously to receive heavy positive portfolio allocations.
        """
        synergy = f"group_rank({factor_a}, {group}) * group_rank({factor_b}, {group})"
        if not reversal_overlay:
            return f"group_rank({synergy}, {group})"
        main_weight = round(1.0 - reversal_weight, 2)
        return (
            f"{main_weight} * group_rank({synergy}, {group}) - "
            f"{reversal_weight} * group_rank(ts_delta(close, {reversal_lookback}) / close, {group})"
        )

    @staticmethod
    def zscore_blend(
        factor_a: str,
        factor_b: str,
        weight_a: float = 0.60,
        weight_b: float = 0.40,
        group: str = "subindustry",
    ) -> str:
        """Create a Z-Score standardized blend: w1 * group_zscore(A) + w2 * group_zscore(B)."""
        return f"{weight_a} * group_zscore({factor_a}, {group}) + {weight_b} * group_zscore({factor_b}, {group})"

    @staticmethod
    def volatility_scaled_signal(
        factor: str,
        vol_field: str = "parkinson_volatility_30",
        group: str = "subindustry",
    ) -> str:
        """Create a volatility-scaled alpha: group_zscore(factor, group) / (volatility + epsilon)."""
        return f"group_zscore({factor}, {group}) / ({vol_field} + 0.001)"

    @staticmethod
    def vector_orthogonal_residual(
        factor_signal: str,
        factor_benchmark: str,
        lookback: int = 60,
        group: str = "subindustry",
    ) -> str:
        """Create an orthogonal residual alpha via ts_regression residual (rettype=2)."""
        orthogonal = f"ts_regression({factor_signal}, {factor_benchmark}, {lookback})"
        return f"group_rank({orthogonal}, {group})"

    @staticmethod
    def ternary_regime_modulation(
        regime_field: str,
        driver_expr: str,
        regime_lookback: int = 60,
        threshold: float = 0.5,
        power_exp: float = 0.5,
        offset: float = 1.0,
    ) -> str:
        """Create a non-linear ternary regime-gated alpha (the 8-PASS blueprint).

        Uses long-horizon rolling sum (>=30d) on the condition to prevent turnover flicker,
        modulating a dimensionless driver expression.
        """
        condition = f"rank(ts_sum({regime_field}, {regime_lookback})) > {threshold}"
        driver_powered = f"power(rank({driver_expr}), {power_exp})"
        return f"{condition} ? {driver_powered} + {offset} : {driver_powered}"

    @staticmethod
    def volume_weighted_reversion(
        reversion_lookback: int = 3,
        volume_lookback: int = 60,
        group: str = "subindustry",
    ) -> str:
        """Create a volume-weighted short-term price reversion alpha.

        Exploits liquidity-exhausted price overreactions. Direction-locked with negative sign.
        """
        vol_ratio = f"volume / ts_mean(volume, {volume_lookback})"
        interaction = f"ts_delta(close, {reversion_lookback}) * rank({vol_ratio})"
        return f"-group_rank({interaction}, {group})"

    @staticmethod
    def decayed_ratio_spread(
        factor_numerator: str,
        factor_denominator: str,
        backfill_days: int = 60,
        decay_days: int = 12,
        group: str = "subindustry",
        epsilon: float = 1000.0,
    ) -> str:
        """Create a unit-safe, decay-smoothed fundamental or options ratio spread."""
        ratio_expr = (
            f"ts_backfill({factor_numerator}, {backfill_days}) / "
            f"(ts_backfill({factor_denominator}, {backfill_days}) + {epsilon})"
        )
        return f"group_rank(ts_decay_linear({ratio_expr}, {decay_days}), {group}) - 0.5"

    @staticmethod
    def cross_factor_orthogonal_spread(
        quality_factor: str,
        risk_factor: str,
        decay_days: int = 15,
        group: str = "subindustry",
    ) -> str:
        """Create an orthogonal factor spread (Long Quality / Short Risk) with linear decay."""
        spread = f"group_rank({quality_factor}, {group}) - group_rank({risk_factor}, {group})"
        return f"group_rank(ts_decay_linear({spread}, {decay_days}), {group}) - 0.5"

    @staticmethod
    def statistical_moment_anomaly(
        factor: str,
        lookback: int = 60,
        decay_days: int = 12,
        group: str = "subindustry",
        invert: bool = True,
    ) -> str:
        """Create a statistical skewness anomaly alpha capturing jump and tail risk."""
        sign_str = "-" if invert else ""
        return f"group_rank(ts_decay_linear({sign_str}ts_skewness({factor}, {lookback}), {decay_days}), {group}) - 0.5"

    @staticmethod
    def hyperbolic_tangent_compression(
        factor: str,
        decay_days: int = 12,
        group: str = "subindustry",
    ) -> str:
        """Compress extreme outliers non-linearly using tanh and smooth via linear decay."""
        compressed = f"tanh(group_zscore({factor}, {group}))"
        return f"group_rank(ts_decay_linear({compressed}, {decay_days}), {group}) - 0.5"
