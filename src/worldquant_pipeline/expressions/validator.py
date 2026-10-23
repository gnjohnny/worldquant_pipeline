"""Deterministic AST validator for WorldQuant BRAIN alpha expressions (Gate G1)."""
from dataclasses import dataclass, field

from worldquant_pipeline.config.settings import get_settings
from worldquant_pipeline.exceptions import (
    OperatorArityError,
    UnknownFieldError,
    UnknownOperatorError,
    WorldQuantPipelineError,
)
from worldquant_pipeline.expressions.ast_nodes import (
    BinaryOperationNode,
    ExpressionNode,
    FieldNode,
    FunctionCallNode,
    LiteralNode,
    TernaryNode,
    UnaryOperationNode,
)
from worldquant_pipeline.expressions.parser import parse_expression


@dataclass
class ASTValidationResult:
    """Detailed result of static AST validation."""
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    node_count: int = 0
    max_depth: int = 0
    referenced_fields: set[str] = field(default_factory=set)
    referenced_operators: set[str] = field(default_factory=set)


class ExpressionValidator:
    """Validates an AST against operator and data field whitelists."""

    def __init__(
        self,
        allowed_operators: dict[str, dict] | None = None,
        allowed_fields: dict[str, dict] | None = None,
        max_depth: int = 10,
    ) -> None:
        settings = get_settings()
        self.allowed_operators = (
            allowed_operators if allowed_operators is not None else settings.get_allowed_operators()
        )
        self.allowed_fields = (
            allowed_fields if allowed_fields is not None else settings.get_allowed_fields()
        )
        self.max_depth = max_depth

    def validate_node(self, node: ExpressionNode) -> ASTValidationResult:
        """Traverse AST and collect all errors, fields, and operators."""
        errors: list[str] = []
        fields: set[str] = set()
        operators: set[str] = set()
        node_count = 0

        def traverse(current: ExpressionNode, depth: int) -> int:
            nonlocal node_count
            node_count += 1
            max_d = depth

            if depth > self.max_depth:
                errors.append(f"Expression depth {depth} exceeds maximum allowed depth of {self.max_depth}.")

            if isinstance(current, FieldNode):
                field_name = current.name.lower()
                fields.add(field_name)
                if field_name not in self.allowed_fields:
                    errors.append(f"Unknown or unpermitted field '{field_name}'.")

            elif isinstance(current, FunctionCallNode):
                op_name = current.name.lower()
                operators.add(op_name)
                if op_name not in self.allowed_operators:
                    errors.append(f"Unknown or disallowed operator '{op_name}'.")
                else:
                    op_spec = self.allowed_operators[op_name]
                    expected_arity = op_spec.get("arity")
                    actual_arity = len(current.args)
                    if expected_arity is not None and actual_arity != expected_arity:
                        errors.append(
                            f"Operator '{op_name}' expects {expected_arity} arguments, but got {actual_arity}."
                        )

                    # Parameter type checks (e.g. lookback must be positive integer)
                    param_types = op_spec.get("param_types", [])
                    if len(param_types) == len(current.args):
                        for i, ptype in enumerate(param_types):
                            arg = current.args[i]
                            if ptype == "integer":
                                if isinstance(arg, LiteralNode):
                                    if not isinstance(arg.value, int) or arg.value <= 0:
                                        errors.append(
                                            f"Argument {i+1} for '{op_name}' must be a positive integer, got '{arg.value}'."
                                        )
                                elif isinstance(arg, UnaryOperationNode) and arg.operator == "-":
                                    errors.append(
                                        f"Argument {i+1} for '{op_name}' must be a positive integer, got negative expression."
                                    )

                for arg in current.args:
                    sub_d = traverse(arg, depth + 1)
                    max_d = max(max_d, sub_d)

            elif isinstance(current, BinaryOperationNode):
                d1 = traverse(current.left, depth + 1)
                d2 = traverse(current.right, depth + 1)
                max_d = max(max_d, d1, d2)

            elif isinstance(current, UnaryOperationNode):
                sub_d = traverse(current.operand, depth + 1)
                max_d = max(max_d, sub_d)

            elif isinstance(current, TernaryNode):
                d1 = traverse(current.condition, depth + 1)
                d2 = traverse(current.true_expr, depth + 1)
                d3 = traverse(current.false_expr, depth + 1)
                max_d = max(max_d, d1, d2, d3)

            return max_d

        tree_depth = traverse(node, 1)

        return ASTValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            node_count=node_count,
            max_depth=tree_depth,
            referenced_fields=fields,
            referenced_operators=operators,
        )

    def validate_expression_string(self, expr_str: str) -> ASTValidationResult:
        """Parse and validate an expression string."""
        node = parse_expression(expr_str)
        return self.validate_node(node)

    def validate_or_raise(self, expr_str: str) -> ASTValidationResult:
        """Parse and validate an expression string, raising typed exceptions on failure."""
        node = parse_expression(expr_str)
        result = self.validate_node(node)
        if not result.is_valid:
            # Raise specific domain exceptions if known
            first_err = result.errors[0]
            if "Unknown or disallowed operator" in first_err:
                raise UnknownOperatorError(first_err)
            if "Unknown or unpermitted field" in first_err:
                field_name = first_err.split("'")[1]
                raise UnknownFieldError(field_name)
            if "expects" in first_err and "arguments" in first_err:
                parts = first_err.split("'")
                op_name = parts[1] if len(parts) > 1 else "unknown"
                raise OperatorArityError(operator=op_name, expected=0, received=0)
            raise WorldQuantPipelineError("; ".join(result.errors))
        return result
