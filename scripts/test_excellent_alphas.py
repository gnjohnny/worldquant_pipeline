from worldquant_pipeline.expressions.parser import parse_expression
from worldquant_pipeline.expressions.validator import ExpressionValidator

validator = ExpressionValidator()

exprs = [
    # 1. Options Volatility Term Structure & Skew (option8)
    "group_rank((implied_volatility_mean_90 - implied_volatility_mean_30) / (implied_volatility_mean_30 + 0.001), subindustry)",
    "signed_power(group_rank((implied_volatility_mean_90 - implied_volatility_mean_30) / (implied_volatility_mean_30 + 0.001), subindustry) - 0.5, 2)",
    
    # 2. Multi-Factor Cashflow Efficiency + Analyst Revision (model16 - 100% coverage!)
    "group_rank(cashflow_efficiency_rank_derivative, subindustry) + group_rank(analyst_revision_rank_derivative, subindustry)",
    "signed_power(group_rank(cashflow_efficiency_rank_derivative, subindustry) - 0.5, 2) + signed_power(group_rank(analyst_revision_rank_derivative, subindustry) - 0.5, 2)",
    "group_rank(cashflow_efficiency_rank_derivative + analyst_revision_rank_derivative, subindustry)",
    
    # 3. Systematic Risk Decoupling (model51)
    "group_rank(-beta_last_60_days_spy, subindustry) * group_rank(-correlation_last_60_days_spy, subindustry)",
    "group_rank(-beta_last_60_days_spy / (beta_last_360_days_spy + 0.01), subindustry)",
    
    # 4. Pure EBITDA Cash Yield 170d in TOPSP500 (Building on Alpha 8)
    "ts_rank(ebitda / close, 170)",
    "ts_rank(ebitda / cap, 170)"
]

for e in exprs:
    node = parse_expression(e)
    res = validator.validate_node(node)
    print(f"Valid: {res.is_valid} | {e}")
    if not res.is_valid:
        print("  Errors:", res.errors)
