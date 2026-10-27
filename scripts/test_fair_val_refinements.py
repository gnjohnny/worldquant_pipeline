from worldquant_pipeline.expressions.parser import parse_expression
from worldquant_pipeline.expressions.validator import ExpressionValidator

validator = ExpressionValidator()

exprs = [
    # 1. Candidate 1: Alpha 5 blueprint on the core prompt signal
    "0.85 * signed_power(group_rank((group_rank(fn_assets_fair_val_a, subindustry) > 0.5 ? 2.0 : 1.0) * (-group_rank(fnd2_ebitdm, subindustry) - group_rank(fnd2_ebitfr, subindustry)), subindustry) - 0.5, 2) - 0.15 * group_rank(ts_delta(close, 3) / close, subindustry)",
    
    # 2. Candidate 2: Operating earnings per unit of fair value asset with Alpha 5 stabilizer
    "0.85 * signed_power(group_rank((ts_backfill(fnd2_ebitdm, 60) + ts_backfill(fnd2_ebitfr, 60)) / (ts_backfill(fn_assets_fair_val_a, 252) + 1000), subindustry) - 0.5, 2) - 0.15 * group_rank(ts_delta(close, 3) / close, subindustry)",
    
    # 3. Candidate 3: Fair Value Asset Yield Trajectory (Alpha 8/9 Architecture)
    "group_rank(ts_rank(ts_backfill(fn_assets_fair_val_a, 252) / close, 252), subindustry)"
]

for e in exprs:
    node = parse_expression(e)
    res = validator.validate_node(node)
    print(f"Valid: {res.is_valid} | {e[:70]}...")
    if not res.is_valid:
        print("  Errors:", res.errors)
