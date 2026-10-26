from worldquant_pipeline.expressions.parser import parse_expression
from worldquant_pipeline.expressions.validator import ExpressionValidator

validator = ExpressionValidator()

exprs = [
    '0.85 * signed_power(group_rank(group_neutralize(-ts_decay_linear(scl12_buzz, 5), bucket(rank(adv20), range="0, 1, 0.2")), subindustry) - 0.5, 2) - 0.15 * group_rank(ts_delta(close, 5) / close, subindustry)',
    '0.85 * signed_power(group_rank(ts_decay_linear(group_neutralize(-scl12_buzz, bucket(rank(volume), range="0, 1, 0.2")), 5), subindustry) - 0.5, 2) - 0.15 * group_rank(ts_delta(close, 5) / close, subindustry)',
    '0.85 * signed_power(group_rank(group_neutralize(-ts_decay_linear(scl12_buzz, 10), bucket(rank(adv20), range="0, 1, 0.2")), subindustry) - 0.5, 2) - 0.15 * group_rank(ts_delta(close, 5) / close, subindustry)',
    'group_rank(group_neutralize(-ts_decay_linear(scl12_buzz, 5), bucket(rank(adv20), range="0, 1, 0.2")), subindustry)'
]

for e in exprs:
    node = parse_expression(e)
    res = validator.validate_node(node)
    print(f"Valid: {res.is_valid} | Errors: {res.errors}")
