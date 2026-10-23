"""AST Node definitions for WorldQuant BRAIN expressions."""
from abc import ABC, abstractmethod
from dataclasses import dataclass


class ExpressionNode(ABC):
    """Abstract base class for all AST expression nodes."""

    @abstractmethod
    def to_string(self) -> str:
        """Convert AST node back to a standardized string."""


@dataclass
class LiteralNode(ExpressionNode):
    """Represents numeric literals (e.g. 5, 0.01, -1.5) or string constants."""
    value: int | float | str

    def to_string(self) -> str:
        return str(self.value)


@dataclass
class FieldNode(ExpressionNode):
    """Represents a dataset field or variable name (e.g. close, volume, subindustry)."""
    name: str

    def to_string(self) -> str:
        return self.name.lower()


@dataclass
class FunctionCallNode(ExpressionNode):
    """Represents an operator/function call (e.g. ts_rank(close, 10))."""
    name: str
    args: list[ExpressionNode]

    def to_string(self) -> str:
        args_str = ", ".join(arg.to_string() for arg in self.args)
        return f"{self.name.lower()}({args_str})"


@dataclass
class BinaryOperationNode(ExpressionNode):
    """Represents a binary operator (e.g. a + b, x / y, a > b)."""
    operator: str
    left: ExpressionNode
    right: ExpressionNode

    def to_string(self) -> str:
        return f"({self.left.to_string()} {self.operator} {self.right.to_string()})"


@dataclass
class UnaryOperationNode(ExpressionNode):
    """Represents a unary operator (e.g. -x, !x)."""
    operator: str
    operand: ExpressionNode

    def to_string(self) -> str:
        return f"{self.operator}{self.operand.to_string()}"


@dataclass
class TernaryNode(ExpressionNode):
    """Represents a ternary conditional expression (condition ? true_expr : false_expr)."""
    condition: ExpressionNode
    true_expr: ExpressionNode
    false_expr: ExpressionNode

    def to_string(self) -> str:
        return (
            f"({self.condition.to_string()} ? "
            f"{self.true_expr.to_string()} : "
            f"{self.false_expr.to_string()})"
        )
