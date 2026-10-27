from worldquant_pipeline.expressions.parser import parse_expression
from worldquant_pipeline.expressions.validator import ExpressionValidator

validator = ExpressionValidator()

exprs = [
    # 1. Analyst Adjusted Net Income Yield (Forward Consensus Valuation)
    "group_rank(ts_rank(ts_backfill(adj_net_income_avg, 60) / close, 252), subindustry)",
    
    # 2. Inverted Variance Risk Premium with Subindustry Neutralization (option8)
    "group_rank(implied_volatility_mean_30 - historical_volatility_30, subindustry)",
    "0.85 * signed_power(group_rank(implied_volatility_mean_30 - historical_volatility_30, subindustry) - 0.5, 2) - 0.15 * group_rank(ts_delta(close, 3) / close, subindustry)",
    
    # 3. Dual-Engine: Operating Income Yield + Asset Solvency Compound
    "group_rank(ts_rank(operating_income / close, 252), subindustry) + group_rank(ts_backfill(assets, 60) / (ts_backfill(debt_lt, 60) + 1000), subindustry)"
]

for e in exprs:
    node = parse_expression(e)
    res = validator.validate_node(node)
    print(f"Valid: {res.is_valid} | {e}")
    if not res.is_valid:
        print("  Errors:", res.errors)
