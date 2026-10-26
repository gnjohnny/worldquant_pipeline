from worldquant_pipeline.expressions.parser import parse_expression
from worldquant_pipeline.expressions.validator import ExpressionValidator

validator = ExpressionValidator()

exprs = [
    'group_neutralize(-scl12_buzz, bucket(rank(volume), range="0, 1, 0.1"))',
    'group_neutralize(-scl12_buzz, bucket(rank(adv20), range="0, 1, 0.1"))',
    '-scl12_buzz / (volume / (adv20 + 0.001) + 0.001)',
    'group_rank(-scl12_buzz / (volume / (adv20 + 0.001) + 0.001), subindustry)',
    'ts_regression(-scl12_buzz, volume, 20)',
    'group_rank(ts_regression(-scl12_buzz, volume, 20), subindustry)',
    '0.85 * signed_power(group_rank(-scl12_buzz / (volume / (adv20 + 0.001) + 0.001), subindustry) - 0.5, 2) - 0.15 * group_rank(ts_delta(close, 3) / close, subindustry)'
]

for e in exprs:
    node = parse_expression(e)
    res = validator.validate_node(node)
    print(f"Valid: {res.is_valid} | {e}")
