"""Unit tests for WorldQuant BRAIN expression tokenizer, AST parser, and validator."""
import pytest

from worldquant_pipeline.exceptions import (
    ASTSyntaxError,
)
from worldquant_pipeline.expressions.ast_nodes import (
    BinaryOperationNode,
    FieldNode,
    FunctionCallNode,
    LiteralNode,
    TernaryNode,
)
from worldquant_pipeline.expressions.canonicalize import (
    canonicalize_expression,
    compute_expression_hash,
)
from worldquant_pipeline.expressions.parser import parse_expression
from worldquant_pipeline.expressions.tokenizer import Tokenizer, TokenType
from worldquant_pipeline.expressions.validator import ExpressionValidator


class TestTokenizer:
    def test_tokenize_basic_symbols(self):
        toks = Tokenizer("ts_rank(close, 10) + 0.5").tokenize()
        types = [t.type for t in toks]
        assert types == [
            TokenType.IDENTIFIER,
            TokenType.LPAREN,
            TokenType.IDENTIFIER,
            TokenType.COMMA,
            TokenType.NUMBER,
            TokenType.RPAREN,
            TokenType.PLUS,
            TokenType.NUMBER,
            TokenType.EOF,
        ]

    def test_tokenize_comparison_and_ternary(self):
        toks = Tokenizer("close >= open ? 1.0 : -1.0").tokenize()
        types = [t.type for t in toks]
        assert TokenType.GREATER_EQUAL in types
        assert TokenType.QUESTION in types
        assert TokenType.COLON in types

    def test_unexpected_character(self):
        with pytest.raises(ASTSyntaxError) as exc_info:
            Tokenizer("close @ 5").tokenize()
        assert "Unexpected character" in str(exc_info.value)


class TestParser:
    def test_parse_simple_field(self):
        node = parse_expression("close")
        assert isinstance(node, FieldNode)
        assert node.name == "close"

    def test_parse_binary_operator_precedence(self):
        # Multiplication must bind tighter than addition
        node = parse_expression("close + open * 2")
        assert isinstance(node, BinaryOperationNode)
        assert node.operator == "+"
        assert isinstance(node.left, FieldNode)
        assert isinstance(node.right, BinaryOperationNode)
        assert node.right.operator == "*"

    def test_parse_function_call(self):
        node = parse_expression("ts_rank(close, 10)")
        assert isinstance(node, FunctionCallNode)
        assert node.name == "ts_rank"
        assert len(node.args) == 2
        assert isinstance(node.args[0], FieldNode)
        assert isinstance(node.args[1], LiteralNode)
        assert node.args[1].value == 10

    def test_parse_nested_functions(self):
        node = parse_expression("group_rank(ts_delta(close, 5), subindustry)")
        assert isinstance(node, FunctionCallNode)
        assert node.name == "group_rank"
        assert len(node.args) == 2
        assert isinstance(node.args[0], FunctionCallNode)
        assert node.args[0].name == "ts_delta"

    def test_parse_ternary_expression(self):
        node = parse_expression("close > open ? returns : -returns")
        assert isinstance(node, TernaryNode)
        assert isinstance(node.condition, BinaryOperationNode)
        assert isinstance(node.true_expr, FieldNode)

    def test_syntax_error_unclosed_parenthesis(self):
        with pytest.raises(ASTSyntaxError):
            parse_expression("ts_rank(close, 10")

    def test_syntax_error_trailing_operator(self):
        with pytest.raises(ASTSyntaxError):
            parse_expression("close +")


class TestValidator:
    @pytest.fixture
    def validator(self):
        allowed_operators = {
            "ts_rank": {"arity": 2, "param_types": ["expression", "integer"]},
            "ts_delta": {"arity": 2, "param_types": ["expression", "integer"]},
            "group_rank": {"arity": 2, "param_types": ["expression", "group"]},
            "rank": {"arity": 1, "param_types": ["expression"]},
        }
        allowed_fields = {
            "close": {"permitted_use": True},
            "open": {"permitted_use": True},
            "volume": {"permitted_use": True},
            "returns": {"permitted_use": True},
            "subindustry": {"permitted_use": True},
        }
        return ExpressionValidator(allowed_operators=allowed_operators, allowed_fields=allowed_fields)

    def test_valid_expression_passes(self, validator):
        res = validator.validate_expression_string("group_rank(ts_delta(close, 5), subindustry)")
        assert res.is_valid is True
        assert len(res.errors) == 0
        assert "close" in res.referenced_fields
        assert "subindustry" in res.referenced_fields
        assert "group_rank" in res.referenced_operators
        assert "ts_delta" in res.referenced_operators

    def test_unknown_operator_rejected(self, validator):
        res = validator.validate_expression_string("my_custom_magic(close, 5)")
        assert res.is_valid is False
        assert any("Unknown or disallowed operator" in err for err in res.errors)

    def test_unknown_field_rejected(self, validator):
        res = validator.validate_expression_string("ts_rank(unknown_crypto_token, 10)")
        assert res.is_valid is False
        assert any("Unknown or unpermitted field" in err for err in res.errors)

    def test_operator_arity_mismatch(self, validator):
        res = validator.validate_expression_string("ts_rank(close)")  # Missing lookback d
        assert res.is_valid is False
        assert any("expects 2 arguments, but got 1" in err for err in res.errors)

    def test_invalid_negative_lookback(self, validator):
        res = validator.validate_expression_string("ts_rank(close, -5)")
        assert res.is_valid is False
        assert any("must be a positive integer" in err for err in res.errors)


class TestCanonicalizationAndDeduplication:
    def test_whitespace_insensitivity(self):
        expr1 = "ts_rank( close ,  10 )"
        expr2 = "ts_rank(close,10)"
        assert canonicalize_expression(expr1) == canonicalize_expression(expr2)
        assert compute_expression_hash(canonicalize_expression(expr1)) == compute_expression_hash(
            canonicalize_expression(expr2)
        )

    def test_commutative_addition_deduplication(self):
        expr1 = "close + volume"
        expr2 = "volume + close"
        c1 = canonicalize_expression(expr1)
        c2 = canonicalize_expression(expr2)
        assert c1 == c2
        assert compute_expression_hash(c1) == compute_expression_hash(c2)
