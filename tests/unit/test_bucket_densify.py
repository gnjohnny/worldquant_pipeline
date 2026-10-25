"""Unit tests for bucket(), densify(), and keyword argument support."""
from worldquant_pipeline.expressions.ast_nodes import (
    FunctionCallNode,
    KeywordArgNode,
    LiteralNode,
)
from worldquant_pipeline.expressions.canonicalize import (
    canonicalize_expression,
    compute_expression_hash,
)
from worldquant_pipeline.expressions.parser import parse_expression
from worldquant_pipeline.expressions.tokenizer import Tokenizer, TokenType
from worldquant_pipeline.expressions.validator import ExpressionValidator


def test_tokenize_keyword_assignment():
    tokens = Tokenizer('bucket(rank(cap), range="0, 1, 0.1")').tokenize()
    types = [t.type for t in tokens]
    assert TokenType.ASSIGN in types
    assert TokenType.STRING in types


def test_parse_bucket_with_keyword_arg():
    ast = parse_expression('bucket(rank(cap), range="0, 1, 0.1")')
    assert isinstance(ast, FunctionCallNode)
    assert ast.name == "bucket"
    assert len(ast.args) == 2
    assert isinstance(ast.args[1], KeywordArgNode)
    assert ast.args[1].name == "range"
    assert isinstance(ast.args[1].value, LiteralNode)
    assert ast.args[1].value.value == "0, 1, 0.1"


def test_parse_densify():
    ast = parse_expression("densify(subindustry)")
    assert isinstance(ast, FunctionCallNode)
    assert ast.name == "densify"
    assert len(ast.args) == 1


def test_validator_bucket_and_densify():
    v = ExpressionValidator()
    # Candidate 1: Size-decile neutralized volume shock
    expr1 = 'group_neutralize(-(ts_delta(close, 3) / close) * ts_rank(volume, 60), densify(bucket(rank(cap), range="0, 1, 0.1")))'
    res1 = v.validate_expression_string(expr1)
    assert res1.is_valid is True
    assert len(res1.errors) == 0
    assert "cap" in res1.referenced_fields
    assert "close" in res1.referenced_fields
    assert "volume" in res1.referenced_fields
    assert "bucket" in res1.referenced_operators
    assert "densify" in res1.referenced_operators
    assert "group_neutralize" in res1.referenced_operators

    # Candidate 2: Volatility-decile neutralized VRP
    expr2 = 'group_neutralize(ts_backfill(implied_volatility_call_720 / parkinson_volatility_120, 120), densify(bucket(rank(parkinson_volatility_120), range="0, 1, 0.1")))'
    res2 = v.validate_expression_string(expr2)
    assert res2.is_valid is True
    assert len(res2.errors) == 0
    assert "implied_volatility_call_720" in res2.referenced_fields
    assert "parkinson_volatility_120" in res2.referenced_fields

    # Candidate 3: Liquidity-decile neutralized factor acceleration
    expr3 = 'group_neutralize(multi_factor_acceleration_score_derivative, densify(bucket(rank(ts_mean(volume, 20)), range="0, 1, 0.1")))'
    res3 = v.validate_expression_string(expr3)
    assert res3.is_valid is True
    assert len(res3.errors) == 0
    assert "multi_factor_acceleration_score_derivative" in res3.referenced_fields


def test_validator_refined_bucket_candidates():
    v = ExpressionValidator()
    # Variation A: group_rank within volatility buckets
    e_a = 'group_rank(ts_backfill(implied_volatility_call_720 / parkinson_volatility_120, 120), densify(bucket(rank(parkinson_volatility_120), range="0, 1, 0.1")))'
    res_a = v.validate_expression_string(e_a)
    assert res_a.is_valid is True

    # Variation B: rank of group_neutralized signal
    e_b = 'rank(group_neutralize(ts_backfill(implied_volatility_call_720 / parkinson_volatility_120, 120), densify(bucket(rank(parkinson_volatility_120), range="0, 1, 0.1"))))'
    res_b = v.validate_expression_string(e_b)
    assert res_b.is_valid is True

    # Variation C: Dual neutralization with subindustry ranking
    e_c = 'group_rank(group_neutralize(ts_backfill(implied_volatility_call_720 / parkinson_volatility_120, 120), densify(bucket(rank(parkinson_volatility_120), range="0, 1, 0.1"))), subindustry)'
    res_c = v.validate_expression_string(e_c)
    assert res_c.is_valid is True


    # Variation D: group_rank with backfilled parkinson vol in bucket
    e_d = 'group_rank(ts_backfill(implied_volatility_call_720 / parkinson_volatility_120, 120), densify(bucket(rank(ts_backfill(parkinson_volatility_120, 120)), range="0, 1, 0.1")))'
    res_d = v.validate_expression_string(e_d)
    assert res_d.is_valid is True

    # Variation E: group_rank with market cap bucket
    e_e = 'group_rank(ts_backfill(implied_volatility_call_720 / parkinson_volatility_120, 120), densify(bucket(rank(cap), range="0, 1, 0.1")))'
    res_e = v.validate_expression_string(e_e)
    assert res_e.is_valid is True


def test_validator_bucket_invalid_arguments():
    v = ExpressionValidator()
    # Missing range argument
    res_missing = v.validate_expression_string("bucket(rank(cap))")
    assert res_missing.is_valid is False
    assert any("expects 2 arguments, but got 1" in e for e in res_missing.errors)

    # Invalid range argument (must be string)
    res_int = v.validate_expression_string("bucket(rank(cap), 10)")
    assert res_int.is_valid is False
    assert any("must be a string" in e for e in res_int.errors)


def test_canonicalize_bucket_keyword():
    expr_a = 'bucket( rank( cap ) , range = "0, 1, 0.1" )'
    expr_b = 'bucket(rank(cap), range="0, 1, 0.1")'
    canon_a = canonicalize_expression(expr_a)
    canon_b = canonicalize_expression(expr_b)
    assert canon_a == canon_b
    assert canon_a == 'bucket(rank(cap), range="0, 1, 0.1")'
    assert compute_expression_hash(canon_a) == compute_expression_hash(canon_b)
