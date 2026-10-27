from worldquant_pipeline.expressions.parser import parse_expression
from worldquant_pipeline.expressions.validator import ExpressionValidator

validator = ExpressionValidator()

exprs = [
    # 1. Single-line ternary form of the prompt expression
    "(group_rank(fn_assets_fair_val_a, industry) > 0.5 ? 2.0 : 1.0) * (-group_rank(fnd2_ebitdm, industry) - group_rank(fnd2_ebitfr, industry))",
    
    # 2. Continuous fundamental fair value ratio with backfill
    "group_rank(ts_backfill(fn_assets_fair_val_a, 252) / (ts_backfill(fnd2_ebitdm, 60) + ts_backfill(fnd2_ebitfr, 60) + 1000), industry)",
    
    # 3. 1-Year time series trajectory of fair value asset yield
    "group_rank(ts_rank(ts_backfill(fn_assets_fair_val_a, 252) / (ts_backfill(fnd2_ebitdm, 60) + ts_backfill(fnd2_ebitfr, 60) + 1000), 252), industry)"
]

for e in exprs:
    node = parse_expression(e)
    res = validator.validate_node(node)
    print(f"Valid: {res.is_valid} | {e}")
    if not res.is_valid:
        print("  Errors:", res.errors)
