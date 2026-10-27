from worldquant_pipeline.expressions.parser import parse_expression
from worldquant_pipeline.expressions.validator import ExpressionValidator

validator = ExpressionValidator()

exprs = [
    # 1. Baseline from user prompt
    "-rank(ebit / capex)",
    "-group_rank(ebit / capex, subindustry)",
    
    # 2. Inverted ratio (long reinvestment) with division stabilizer
    "group_rank(capex / (ebit + 1.0), subindustry)",
    "-group_rank(ebit / (capex + 1.0), subindustry)",
    
    # 3. With 60-day quarterly backfill
    "-group_rank(ts_backfill(ebit, 60) / (ts_backfill(capex, 60) + 1.0), subindustry)",
    "group_rank(ts_backfill(capex, 60) / (ts_backfill(ebit, 60) + 1000), subindustry)",
    
    # 4. 1-Year Time-Series Trajectory (The Operating Yield Lesson)
    "group_rank(ts_rank(ts_backfill(capex, 60) / (ts_backfill(ebit, 60) + 1000), 252), subindustry)",
    "-group_rank(ts_rank(ts_backfill(ebit, 60) / (ts_backfill(capex, 60) + 1.0), 252), subindustry)",
    
    # 5. Compound Blueprint
    "0.85 * signed_power(group_rank(ts_backfill(capex, 60) / (ts_backfill(ebit, 60) + 1000), subindustry) - 0.5, 2) - 0.15 * group_rank(ts_delta(close, 3) / close, subindustry)"
]

for e in exprs:
    node = parse_expression(e)
    res = validator.validate_node(node)
    print(f"Valid: {res.is_valid} | {e}")
    if not res.is_valid:
        print("  Errors:", res.errors)
