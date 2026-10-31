"""Pre-simulation Mathematical Turnover Proxy & Friction Estimator (Gate G2)."""
from dataclasses import dataclass
from typing import ClassVar

from worldquant_pipeline.expressions.ast_nodes import (
    BinaryOperationNode,
    ExpressionNode,
    FieldNode,
    FunctionCallNode,
    KeywordArgNode,
    LiteralNode,
    TernaryNode,
    UnaryOperationNode,
)
from worldquant_pipeline.expressions.parser import parse_expression


@dataclass
class TurnoverEstimate:
    """Pre-simulation predicted turnover and friction classification."""
    estimated_turnover: float
    turnover_range: tuple[float, float]
    status: str  # "OPTIMAL", "ACCEPTABLE", "HIGH_RISK", "LOW_RISK"
    decay_used: int
    is_safe: bool
    warnings: list[str]
    recommendation: str | None = None


class TurnoverProxyCalculator:
    """Estimates turnover of an alpha expression prior to simulation on WorldQuant BRAIN."""

    # Baseline daily turnover rates of raw signal drivers without decay
    FAST_PRICE_FIELDS: ClassVar[set[str]] = {"returns", "ts_delta"}
    MEDIUM_PRICE_FIELDS: ClassVar[set[str]] = {"close", "open", "high", "low", "vwap", "volume"}
    SLOW_FUNDAMENTAL_PREFIXES = ("fnd6_", "actual_", "anl4_", "fscore_", "cashflow", "sales", "ebit")
    VOLATILITY_PREFIXES = ("implied_volatility", "historical_volatility", "parkinson_volatility", "beta_")

    @classmethod
    def estimate(cls, expr_str: str, decay: int = 4) -> TurnoverEstimate:
        """Estimate the expected turnover range for an expression given a simulation decay horizon."""
        try:
            node = parse_expression(expr_str)
        except Exception:  # noqa: BLE001
            return TurnoverEstimate(
                estimated_turnover=0.15,
                turnover_range=(0.05, 0.30),
                status="ACCEPTABLE",
                decay_used=decay,
                is_safe=True,
                warnings=["Could not parse expression AST for precise turnover estimation."],
            )

        has_fast_price_term = False
        fast_price_weight = 0.0
        has_fundamental_term = False
        has_volatility_term = False
        has_smoothing_op = False
        shortest_lookback = 999

        def inspect_ast(curr: ExpressionNode | None, current_weight: float = 1.0) -> None:
            nonlocal has_fast_price_term, fast_price_weight, has_fundamental_term
            nonlocal has_volatility_term, has_smoothing_op, shortest_lookback

            if curr is None:
                return

            if isinstance(curr, FieldNode):
                fname = curr.name.lower()
                if fname.startswith(cls.SLOW_FUNDAMENTAL_PREFIXES):
                    has_fundamental_term = True
                elif fname.startswith(cls.VOLATILITY_PREFIXES):
                    has_volatility_term = True
                elif fname in {"returns"}:
                    has_fast_price_term = True
                    fast_price_weight = max(fast_price_weight, current_weight)

            elif isinstance(curr, FunctionCallNode):
                op = curr.name.lower()
                if op in {"decay_linear", "ts_decay_linear"}:
                    has_smoothing_op = True

                if op == "ts_delta" and len(curr.args) > 1:
                    has_fast_price_term = True
                    fast_price_weight = max(fast_price_weight, current_weight)
                    if isinstance(curr.args[1], LiteralNode) and isinstance(curr.args[1].value, int):
                        shortest_lookback = min(shortest_lookback, curr.args[1].value)

                for a in curr.args:
                    inspect_ast(a, current_weight)

            elif isinstance(curr, BinaryOperationNode):
                # Detect linear combination weights, e.g., 0.85 * A - 0.15 * B
                if curr.operator in {"*", "/"}:
                    weight = current_weight
                    if isinstance(curr.left, LiteralNode) and isinstance(curr.left.value, (int, float)):
                        weight = abs(float(curr.left.value))
                        inspect_ast(curr.right, weight)
                        return
                    if isinstance(curr.right, LiteralNode) and isinstance(curr.right.value, (int, float)):
                        weight = abs(float(curr.right.value))
                        inspect_ast(curr.left, weight)
                        return
                inspect_ast(curr.left, current_weight)
                inspect_ast(curr.right, current_weight)

            elif isinstance(curr, UnaryOperationNode):
                inspect_ast(curr.operand, current_weight)
            elif isinstance(curr, KeywordArgNode):
                inspect_ast(curr.value, current_weight)
            elif isinstance(curr, TernaryNode):
                inspect_ast(curr.condition, current_weight)
                inspect_ast(curr.true_expr, current_weight)
                inspect_ast(curr.false_expr, current_weight)

        inspect_ast(node)

        # Base raw turnover estimation before decay scaling
        if has_fundamental_term and not has_fast_price_term:
            raw_turnover = 0.08  # Slow fundamental quarterly updates
        elif has_fundamental_term and has_fast_price_term:
            # Reversal overlay blended with fundamental
            reversal_intensity = min(fast_price_weight, 0.40)
            if shortest_lookback <= 2:
                raw_turnover = 0.08 + (reversal_intensity * 1.40)
            elif shortest_lookback <= 5:
                raw_turnover = 0.08 + (reversal_intensity * 0.90)
            else:
                raw_turnover = 0.08 + (reversal_intensity * 0.50)
        elif has_volatility_term:
            raw_turnover = 0.28
        elif has_fast_price_term:
            if shortest_lookback <= 2:
                raw_turnover = 0.75
            elif shortest_lookback <= 5:
                raw_turnover = 0.48
            else:
                raw_turnover = 0.32
        else:
            raw_turnover = 0.22

        if has_smoothing_op:
            raw_turnover *= 0.65

        # Decay dampening function: Turnover decreases asymptotically as decay increases
        # Empirical BRAIN relation: Turnover ~ raw / (1 + 0.38 * (decay - 1))
        decay_factor = 1.0 / (1.0 + 0.38 * max(decay - 1, 0))
        estimated_turnover = round(raw_turnover * decay_factor, 4)

        lower_bound = max(round(estimated_turnover * 0.78, 4), 0.005)
        upper_bound = min(round(estimated_turnover * 1.25, 4), 0.95)

        warnings: list[str] = []
        recommendation: str | None = None

        if upper_bound > 0.60:
            status = "HIGH_RISK"
            is_safe = False
            warnings.append(
                f"Gate G2 High Friction Warning: Estimated turnover ({estimated_turnover:.1%}, range {lower_bound:.1%}–{upper_bound:.1%}) "
                f"approaches or exceeds the maximum cutoff of 70%."
            )
            recommendation = (
                f"Increase simulation decay from {decay} to {decay + 2} or wrap high-frequency components in ts_decay_linear(..., 5)."
            )
        elif lower_bound < 0.01:
            status = "LOW_RISK"
            is_safe = False
            warnings.append(
                f"Gate G2 Inactivity Warning: Estimated turnover ({estimated_turnover:.1%}) is dangerously close to 1% minimum cutoff."
            )
            recommendation = "Add a 10%–15% short-term reversal overlay: -0.15 * group_rank(ts_delta(close, 3) / close, subindustry)."
        elif 0.06 <= estimated_turnover <= 0.22:
            status = "OPTIMAL"
            is_safe = True
        else:
            status = "ACCEPTABLE"
            is_safe = True

        return TurnoverEstimate(
            estimated_turnover=estimated_turnover,
            turnover_range=(lower_bound, upper_bound),
            status=status,
            decay_used=decay,
            is_safe=is_safe,
            warnings=warnings,
            recommendation=recommendation,
        )
