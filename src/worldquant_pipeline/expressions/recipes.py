"""Advanced quantitative alpha formula recipes and convexity generators.

Provides structural alternatives to flat linear sums, implementing:
1. Multiplicative Cross-Factor Synergy (soft AND conditions)
2. Z-Score Standardization Blends
3. Volatility-Adjusted Momentum & Yield
4. Vector Neutralized Orthogonal Residuals
5. Convex Decile Asymmetric Weighting
"""


class AlphaRecipeGenerator:
    """Generates deterministic, AST-compliant WorldQuant BRAIN alpha expressions."""

    @staticmethod
    def multiplicative_synergy(
        factor_a: str,
        factor_b: str,
        group: str = "subindustry",
        reversal_overlay: bool = True,
        reversal_weight: float = 0.15,
        reversal_lookback: int = 3,
    ) -> str:
        """Create a multiplicative synergy alpha: rank(A) * rank(B).

        Acts as a soft logical AND condition where securities must exhibit strength in
        both factors simultaneously to receive heavy positive portfolio allocations.
        """
        synergy = f"group_rank({factor_a}, {group}) * group_rank({factor_b}, {group})"
        if not reversal_overlay:
            return synergy
        main_weight = round(1.0 - reversal_weight, 2)
        return (
            f"{main_weight} * group_rank({synergy}, {group}) - "
            f"{reversal_weight} * group_rank(ts_delta(close, {reversal_lookback}) / close, {group})"
        )

    @staticmethod
    def zscore_blend(
        factor_a: str,
        factor_b: str,
        weight_a: float = 0.70,
        weight_b: float = 0.30,
        reversal_overlay: bool = True,
        group: str = "subindustry",
    ) -> str:
        """Create a Z-Score standardized blend: w1 * zscore(A) + w2 * zscore(B).

        Preserves fat tails and informational dispersion across securities rather than
        compressing signals into uniform distributions.
        """
        raw_blend = f"{weight_a} * zscore({factor_a}) + {weight_b} * zscore({factor_b})"
        if not reversal_overlay:
            return raw_blend
        return (
            f"0.85 * group_rank({raw_blend}, {group}) - "
            f"0.15 * group_rank(ts_delta(close, 3) / close, {group})"
        )

    @staticmethod
    def volatility_scaled_signal(
        factor: str,
        vol_field: str = "parkinson_volatility_30",
        group: str = "subindustry",
        reversal_overlay: bool = True,
    ) -> str:
        """Create a volatility-scaled alpha: factor / (volatility + epsilon).

        Penalizes volatile, noisy securities and concentrates capital into steady,
        high-conviction compounders.
        """
        scaled = f"{factor} / ({vol_field} + 0.001)"
        if not reversal_overlay:
            return f"group_rank({scaled}, {group})"
        return (
            f"0.85 * signed_power(group_rank({scaled}, {group}) - 0.5, 2) - "
            f"0.15 * group_rank(ts_delta(close, 3) / close, {group})"
        )

    @staticmethod
    def vector_orthogonal_residual(
        factor_signal: str,
        factor_benchmark: str,
        group: str = "subindustry",
        reversal_overlay: bool = True,
    ) -> str:
        """Create an orthogonal residual alpha via vector_neut(signal, benchmark).

        Projects the signal into the null space of the benchmark factor, stripping out
        unwanted systematic factor exposure.
        """
        orthogonal = f"vector_neut({factor_signal}, {factor_benchmark})"
        if not reversal_overlay:
            return f"group_rank({orthogonal}, {group})"
        return (
            f"0.85 * group_rank({orthogonal}, {group}) - "
            f"0.15 * group_rank(ts_delta(close, 3) / close, {group})"
        )

    @staticmethod
    def convex_decile_power(
        factor: str,
        group: str = "subindustry",
        power: int = 2,
        reversal_weight: float = 0.15,
        reversal_lookback: int = 3,
    ) -> str:
        """Standard high-Sharpe signed power formulation on group rank."""
        main_weight = round(1.0 - reversal_weight, 2)
        return (
            f"{main_weight} * signed_power(group_rank({factor}, {group}) - 0.5, {power}) - "
            f"{reversal_weight} * group_rank(ts_delta(close, {reversal_lookback}) / close, {group})"
        )
