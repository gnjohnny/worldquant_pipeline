from worldquant_pipeline.expressions.parser import parse_expression
from worldquant_pipeline.expressions.validator import ExpressionValidator

validator = ExpressionValidator()

exprs = [
    # 1. Direct implementation of the hint: ratio with price (stock market moves)
    "ts_rank(operating_income / close, 252)",
    "ts_rank(operating_income / cap, 252)",
    
    # 2. Cross-sectional group rank within subindustry
    "group_rank(ts_rank(operating_income / close, 252), subindustry)",
    "group_rank(ts_rank(operating_income / cap, 252), subindustry)",
    
    # 3. With ts_backfill for quarterly safety
    "group_rank(ts_rank(ts_backfill(operating_income, 60) / close, 252), subindustry)",
    
    # 4. Global rank
    "rank(ts_rank(operating_income / close, 252))",
    "rank(ts_rank(operating_income / cap, 252))"
]

for e in exprs:
    node = parse_expression(e)
    res = validator.validate_node(node)
    print(f"Valid: {res.is_valid} | {e}")
    if not res.is_valid:
        print("  Errors:", res.errors)
