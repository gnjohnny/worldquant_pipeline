"""Expression canonicalization and SHA-256 deduplication hashing."""
import hashlib

from worldquant_pipeline.expressions.ast_nodes import (
    BinaryOperationNode,
    ExpressionNode,
    FieldNode,
    FunctionCallNode,
    KeywordArgNode,
    LiteralNode,
    TernaryNode,
    UnaryOperationNode,
)
from worldquant_pipeline.expressions.parser import parse_expression

COMMUTATIVE_OPERATORS = {"+", "*", "==", "!=", "&&", "||"}


def canonicalize_node(node: ExpressionNode) -> str:
    """Recursively convert an AST node into a canonical normalized string."""
    if isinstance(node, LiteralNode):
        if isinstance(node.value, float):
            # Normalize float formatting (strip trailing zeros if integer equivalent)
            if node.value.is_integer():
                return str(int(node.value))
            return f"{node.value:.6g}"
        if isinstance(node.value, str):
            return f'"{node.value}"'
        return str(node.value)

    if isinstance(node, KeywordArgNode):
        return f"{node.name.lower()}={canonicalize_node(node.value)}"

    if isinstance(node, FieldNode):
        return node.name.lower()

    if isinstance(node, FunctionCallNode):
        canonical_args = [canonicalize_node(arg) for arg in node.args]
        return f"{node.name.lower()}({', '.join(canonical_args)})"

    if isinstance(node, BinaryOperationNode):
        left_str = canonicalize_node(node.left)
        right_str = canonicalize_node(node.right)
        op = node.operator

        # Commutative sorting to catch simple inversions: a + b == b + a
        if op in COMMUTATIVE_OPERATORS and left_str > right_str:
            left_str, right_str = right_str, left_str

        return f"({left_str} {op} {right_str})"

    if isinstance(node, UnaryOperationNode):
        return f"{node.operator}{canonicalize_node(node.operand)}"

    if isinstance(node, TernaryNode):
        cond = canonicalize_node(node.condition)
        true_b = canonicalize_node(node.true_expr)
        false_b = canonicalize_node(node.false_expr)
        return f"({cond} ? {true_b} : {false_b})"

    return node.to_string()


def canonicalize_expression(expr_str: str) -> str:
    """Parse an expression string and return its canonical normalized representation."""
    ast = parse_expression(expr_str)
    return canonicalize_node(ast)


def compute_expression_hash(canonical_expr: str) -> str:
    """Compute the SHA-256 hash of a canonicalized expression string."""
    return hashlib.sha256(canonical_expr.strip().encode("utf-8")).hexdigest()
