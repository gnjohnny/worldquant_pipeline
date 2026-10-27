from worldquant_pipeline.expressions.parser import parse_expression
from worldquant_pipeline.expressions.validator import ExpressionValidator

validator = ExpressionValidator()

exprs = [
    # 1. Cash Ratio Solvency
    "group_rank(ts_rank(ts_backfill(cash_st, 60) / (ts_backfill(debt_st, 60) + 1000), 252), subindustry)",
    
    # 2. Operating Cash Flow Yield Breakout
    "ts_rank(ts_backfill(fnd6_fopo, 60) / close, 170)",
    
    # 3. Variance Risk Premium
    "group_rank(historical_volatility_30 - implied_volatility_mean_30, subindustry)"
]

for e in exprs:
    node = parse_expression(e)
    res = validator.validate_node(node)
    print(f"Valid: {res.is_valid} | {e}")
    if not res.is_valid:
        print("  Errors:", res.errors)
