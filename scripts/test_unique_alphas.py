from worldquant_pipeline.expressions.parser import parse_expression
from worldquant_pipeline.expressions.validator import ExpressionValidator

validator = ExpressionValidator()

exprs = [
    # 1. Variance Risk Premium (option8)
    "group_rank(historical_volatility_30 - implied_volatility_mean_30, subindustry)",
    "group_rank((historical_volatility_30 - implied_volatility_mean_30) / (implied_volatility_mean_90 + 0.001), subindustry)",
    
    # 2. Low-Beta / Systematic Risk Anomaly (model51)
    "group_rank(-beta_last_60_days_spy, subindustry)",
    "group_rank(-beta_last_60_days_spy, subindustry) * group_rank(-(unsystematic_risk_last_30_days_spy / (unsystematic_risk_last_360_days_spy + 0.001)), subindustry)",
    
    # 3. Supply Chain Lead-Lag (pv13)
    "group_rank(ts_decay_linear(pv13_custretsig_retsig, 5), subindustry)",
    "group_rank(ts_decay_linear(pv13_custretsig_retsig, 5) - (ts_delta(close, 5) / close), subindustry)",
    
    # 4. Multi-Factor Acceleration Synergy (model16)
    "group_rank(cashflow_efficiency_rank_derivative, subindustry) + group_rank(analyst_revision_rank_derivative, subindustry)"
]

for e in exprs:
    node = parse_expression(e)
    res = validator.validate_node(node)
    print(f"Valid: {res.is_valid} | {e}")
    if not res.is_valid:
        print("  Errors:", res.errors)
