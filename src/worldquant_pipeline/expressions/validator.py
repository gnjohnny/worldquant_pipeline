"""Deterministic AST validator for WorldQuant BRAIN alpha expressions (Gate G1)."""
from dataclasses import dataclass, field

from worldquant_pipeline.config.settings import get_settings
from worldquant_pipeline.exceptions import (
    ASTSyntaxError,
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
    KeywordArgNode,
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
    warnings: list[str] = field(default_factory=list)
    node_count: int = 0
    max_depth: int = 0
    referenced_fields: set[str] = field(default_factory=set)
    referenced_operators: set[str] = field(default_factory=set)


def extract_fields_from_node(node: ExpressionNode) -> set[str]:
    """Helper to extract all field names referenced within an AST subtree."""
    res: set[str] = set()

    def _extract(n: ExpressionNode | None) -> None:
        if n is None:
            return
        if isinstance(n, FieldNode):
            res.add(n.name.lower())
        elif isinstance(n, FunctionCallNode):
            for a in n.args:
                _extract(a)
        elif isinstance(n, KeywordArgNode):
            _extract(n.value)
        elif isinstance(n, UnaryOperationNode):
            _extract(n.operand)
        elif isinstance(n, BinaryOperationNode):
            _extract(n.left)
            _extract(n.right)
        elif isinstance(n, TernaryNode):
            _extract(n.condition)
            _extract(n.true_expr)
            _extract(n.false_expr)

    _extract(node)
    return res


def infer_node_unit(node: ExpressionNode, allowed_fields: dict[str, dict]) -> str:
    """Infer the physical unit dimension of an AST node.

    Returns:
        'price': currency / price quantities (close, open, USD)
        'shares': share volume quantities (volume, shares)
        'dimensionless': ratios, ranks, z-scores, counts, scalars
    """
    if isinstance(node, LiteralNode):
        return "dimensionless"

    if isinstance(node, FieldNode):
        fname = node.name.lower()
        finfo = allowed_fields.get(fname, {})
        u = str(finfo.get("unit") or finfo.get("unit_type") or "").lower()
        if u in {"usd", "price"}:
            return "price"
        if u in {"shares", "volume"}:
            return "shares"
        return "dimensionless"

    if isinstance(node, FunctionCallNode):
        op = node.name.lower()
        # Normalizing / ranking operators ALWAYS strip physical dimensions:
        if op in {
            "rank",
            "group_rank",
            "ts_rank",
            "group_zscore",
            "zscore",
            "scale",
            "group_scale",
            "normalize",
            "quantile",
            "ts_scale",
            "ts_zscore",
            "ts_corr",
            "correlation",
            "trade_when",
            "sign",
            "densify",
            "bucket",
        }:
            return "dimensionless"

        # Unit-preserving functions inherit from the primary operand:
        if op in {
            "ts_mean",
            "ts_sum",
            "ts_median",
            "ts_max",
            "ts_min",
            "ts_decay_linear",
            "decay_linear",
            "ts_backfill",
            "ts_delay",
            "ts_delta",
            "ts_std_dev",
            "ts_stddev",
            "abs",
            "min",
            "max",
            "floor",
            "ceil",
            "round",
        } and len(node.args) > 0:
            return infer_node_unit(node.args[0], allowed_fields)

        return "dimensionless"

    if isinstance(node, UnaryOperationNode):
        return infer_node_unit(node.operand, allowed_fields)

    if isinstance(node, BinaryOperationNode):
        if node.operator in {"+", "-"}:
            u_left = infer_node_unit(node.left, allowed_fields)
            u_right = infer_node_unit(node.right, allowed_fields)
            if u_left in {"price", "shares"}:
                return u_left
            if u_right in {"price", "shares"}:
                return u_right
            return "dimensionless"

        if node.operator == "/":
            u_left = infer_node_unit(node.left, allowed_fields)
            u_right = infer_node_unit(node.right, allowed_fields)
            if u_left == u_right and u_left in {"price", "shares"}:
                return "dimensionless"  # e.g. close / ts_delay(close, 5) is dimensionless
            return "dimensionless"

        if node.operator == "*":
            u_left = infer_node_unit(node.left, allowed_fields)
            u_right = infer_node_unit(node.right, allowed_fields)
            if u_left in {"price", "shares"} and u_right == "dimensionless":
                return u_left
            if u_right in {"price", "shares"} and u_left == "dimensionless":
                return u_right
            return "dimensionless"

        return "dimensionless"

    if isinstance(node, TernaryNode):
        u_true = infer_node_unit(node.true_expr, allowed_fields)
        u_false = infer_node_unit(node.false_expr, allowed_fields)
        if u_true == u_false:
            return u_true
        return "dimensionless"

    return "dimensionless"


def find_condition_lookback(node: ExpressionNode) -> int:
    """Find maximum time-series lookback window within a condition expression."""
    max_lb = 0
    if isinstance(node, FunctionCallNode):
        op = node.name.lower()
        if op in {
            "ts_sum",
            "ts_mean",
            "ts_decay_linear",
            "decay_linear",
            "ts_median",
            "ts_std_dev",
            "ts_stddev",
            "ts_max",
            "ts_min",
            "ts_backfill",
        }:
            for a in node.args[1:]:
                if isinstance(a, LiteralNode) and isinstance(a.value, int):
                    max_lb = max(max_lb, a.value)
        for a in node.args:
            max_lb = max(max_lb, find_condition_lookback(a))
    elif isinstance(node, BinaryOperationNode):
        max_lb = max(find_condition_lookback(node.left), find_condition_lookback(node.right))
    elif isinstance(node, UnaryOperationNode):
        max_lb = find_condition_lookback(node.operand)
    return max_lb


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
        warnings: list[str] = []
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
                    if expected_arity is not None:
                        if isinstance(expected_arity, (list, tuple, set)):
                            if actual_arity not in expected_arity:
                                errors.append(
                                    f"Operator '{op_name}' expects one of {list(expected_arity)} arguments, but got {actual_arity}."
                                )
                        elif actual_arity != expected_arity:
                            errors.append(
                                f"Operator '{op_name}' expects {expected_arity} arguments, but got {actual_arity}."
                            )

                    # Parameter type checks (e.g. lookback must be positive integer)
                    param_types = op_spec.get("param_types", [])
                    check_count = min(len(param_types), len(current.args))
                    for i in range(check_count):
                        ptype = param_types[i]
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
                        elif ptype == "number":
                            if isinstance(arg, LiteralNode) and not isinstance(arg.value, (int, float)):
                                errors.append(
                                    f"Argument {i+1} for '{op_name}' must be a numeric value, got '{arg.value}'."
                                )
                        elif ptype == "string":
                            val_node = arg.value if isinstance(arg, KeywordArgNode) else arg
                            if not (isinstance(val_node, LiteralNode) and isinstance(val_node.value, str)):
                                errors.append(
                                    f"Argument {i+1} for '{op_name}' must be a string or keyword string parameter."
                                )
                        elif ptype == "group":
                            val_node = arg.value if isinstance(arg, KeywordArgNode) else arg
                            # Groups in BRAIN are fields (subindustry), function calls (densify(x)), or strings
                            if not (
                                isinstance(val_node, (FieldNode, FunctionCallNode))
                                or (isinstance(val_node, LiteralNode) and isinstance(val_node.value, str))
                            ):
                                errors.append(
                                    f"Argument {i+1} for '{op_name}' must be a group identifier or expression."
                                )

                    # Event-type compatibility checks (Operator ts_backfill does not support event inputs)
                    if op_name in {"ts_backfill"} and len(current.args) > 0:
                        first_arg_fields = extract_fields_from_node(current.args[0])
                        for f_k in first_arg_fields:
                            field_info = self.allowed_fields.get(f_k, {})
                            if field_info.get("is_event", False) or f_k in {
                                "anl4_buy",
                                "anl4_sell",
                                "anl4_hold",
                                "anl4_strong_buy",
                                "anl4_strong_sell",
                                "anl4_underperform",
                                "anl4_outperform",
                            }:
                                errors.append(
                                    f"Operator '{op_name}' does not support event inputs ('{f_k}'). "
                                    f"Event inputs require event-specific aggregations and cannot be directly backfilled."
                                )

                for arg in current.args:
                    sub_d = traverse(arg, depth + 1)
                    max_d = max(max_d, sub_d)

            elif isinstance(current, KeywordArgNode):
                sub_d = traverse(current.value, depth + 1)
                max_d = max(max_d, sub_d)

            elif isinstance(current, BinaryOperationNode):
                # Physical unit compatibility check for addition and subtraction
                if current.operator in {"+", "-"}:
                    u_left = infer_node_unit(current.left, self.allowed_fields)
                    u_right = infer_node_unit(current.right, self.allowed_fields)

                    # Adding dimensionless scalar to physical unit triggers BRAIN platform warning
                    if u_left in {"price", "shares"} and u_right == "dimensionless":
                        warnings.append(
                            f"Incompatible unit warning for '{current.operator}': combining physical dimension '{u_left}' with dimensionless '{u_right}'. Wrap field in rank/group_rank or normalize to avoid BRAIN platform unit warnings."
                        )
                    elif u_right in {"price", "shares"} and u_left == "dimensionless":
                        warnings.append(
                            f"Incompatible unit warning for '{current.operator}': combining dimensionless '{u_left}' with physical dimension '{u_right}'. Wrap field in rank/group_rank or normalize to avoid BRAIN platform unit warnings."
                        )
                    elif u_left in {"price", "shares"} and u_right in {"price", "shares"} and u_left != u_right:
                        warnings.append(
                            f"Incompatible unit warning for '{current.operator}': combining physical unit '{u_left}' with '{u_right}'."
                        )

                d1 = traverse(current.left, depth + 1)
                d2 = traverse(current.right, depth + 1)
                max_d = max(max_d, d1, d2)

            elif isinstance(current, UnaryOperationNode):
                sub_d = traverse(current.operand, depth + 1)
                max_d = max(max_d, sub_d)

            elif isinstance(current, TernaryNode):
                cond_lb = find_condition_lookback(current.condition)
                if cond_lb < 20:
                    warnings.append(
                        f"Condition stability warning: condition lookback of {cond_lb}d is less than the 20d minimum. "
                        f"Unsmoothed ternary conditions flicker daily, causing excessive turnover (>70%). Wrap condition in ts_sum(..., >=20) or ts_mean(..., >=20)."
                    )
                d1 = traverse(current.condition, depth + 1)
                d2 = traverse(current.true_expr, depth + 1)
                d3 = traverse(current.false_expr, depth + 1)
                max_d = max(max_d, d1, d2, d3)

            return max_d

        tree_depth = traverse(node, 1)

        return ASTValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            node_count=node_count,
            max_depth=tree_depth,
            referenced_fields=fields,
            referenced_operators=operators,
        )

    def validate_expression_string(self, expr_str: str) -> ASTValidationResult:
        """Parse and validate an expression string (supporting single and multi-statement expressions)."""
        if ";" in expr_str:
            stmts = [s.strip() for s in expr_str.split(";") if s.strip()]
            all_errors: list[str] = []
            all_warnings: list[str] = []
            all_fields: set[str] = set()
            all_operators: set[str] = set()
            total_nodes = 0
            max_depth = 0
            local_vars: set[str] = set()

            for stmt in stmts:
                expr_to_parse = stmt
                if "=" in stmt and not any(op in stmt for op in ["==", "!=", "<=", ">="]):
                    parts = stmt.split("=", 1)
                    var_name = parts[0].strip().lower()
                    local_vars.add(var_name)
                    expr_to_parse = parts[1].strip()

                scoped_fields = dict(self.allowed_fields)
                for lv in local_vars:
                    scoped_fields[lv] = {"category": "local_var", "unit": "dimensionless"}

                scoped_validator = ExpressionValidator(
                    allowed_operators=self.allowed_operators,
                    allowed_fields=scoped_fields,
                    max_depth=self.max_depth,
                )
                try:
                    node = parse_expression(expr_to_parse)
                    sub_res = scoped_validator.validate_node(node)
                    all_errors.extend(sub_res.errors)
                    all_warnings.extend(sub_res.warnings)
                    total_nodes += sub_res.node_count
                    max_depth = max(max_depth, sub_res.max_depth)
                    all_fields.update(sub_res.referenced_fields - local_vars)
                    all_operators.update(sub_res.referenced_operators)
                except ASTSyntaxError as e:
                    all_errors.append(f"Syntax error in '{stmt}': {e}")
                except WorldQuantPipelineError as e:
                    all_errors.append(f"Error parsing '{stmt}': {e}")

            return ASTValidationResult(
                is_valid=len(all_errors) == 0,
                errors=all_errors,
                warnings=all_warnings,
                node_count=total_nodes,
                max_depth=max_depth,
                referenced_fields=all_fields,
                referenced_operators=all_operators,
            )

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
