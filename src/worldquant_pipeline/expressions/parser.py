"""Recursive-descent parser for WorldQuant BRAIN alpha expressions."""

from worldquant_pipeline.exceptions import ASTSyntaxError
from worldquant_pipeline.expressions.ast_nodes import (
    BinaryOperationNode,
    ExpressionNode,
    FieldNode,
    FunctionCallNode,
    LiteralNode,
    TernaryNode,
    UnaryOperationNode,
)
from worldquant_pipeline.expressions.tokenizer import Token, Tokenizer, TokenType


class Parser:
    """Parses a stream of tokens into an AST."""

    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.current = 0

    def parse(self) -> ExpressionNode:
        """Parse full expression and ensure entire input is consumed."""
        if self._is_at_end() or self._peek().type == TokenType.EOF:
            raise ASTSyntaxError("Empty expression cannot be parsed")
        node = self._expression()
        if not self._is_at_end() and self._peek().type != TokenType.EOF:
            extra = self._peek()
            raise ASTSyntaxError(
                f"Unexpected token '{extra.value}' after complete expression",
                position=extra.position,
                token=extra.value,
            )
        return node

    # --- Grammar Rules ---

    def _expression(self) -> ExpressionNode:
        return self._ternary()

    def _ternary(self) -> ExpressionNode:
        expr = self._logical_or()
        if self._match(TokenType.QUESTION):
            true_expr = self._expression()
            self._consume(TokenType.COLON, "Expected ':' in ternary operator")
            false_expr = self._expression()
            return TernaryNode(condition=expr, true_expr=true_expr, false_expr=false_expr)
        return expr

    def _logical_or(self) -> ExpressionNode:
        expr = self._logical_and()
        while self._match(TokenType.LOGICAL_OR):
            op = self._previous().value
            right = self._logical_and()
            expr = BinaryOperationNode(operator=op, left=expr, right=right)
        return expr

    def _logical_and(self) -> ExpressionNode:
        expr = self._comparison()
        while self._match(TokenType.LOGICAL_AND):
            op = self._previous().value
            right = self._comparison()
            expr = BinaryOperationNode(operator=op, left=expr, right=right)
        return expr

    def _comparison(self) -> ExpressionNode:
        expr = self._additive()
        comparison_types = (
            TokenType.EQUAL,
            TokenType.NOT_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
        )
        while self._match(*comparison_types):
            op = self._previous().value
            right = self._additive()
            expr = BinaryOperationNode(operator=op, left=expr, right=right)
        return expr

    def _additive(self) -> ExpressionNode:
        expr = self._multiplicative()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            op = self._previous().value
            right = self._multiplicative()
            expr = BinaryOperationNode(operator=op, left=expr, right=right)
        return expr

    def _multiplicative(self) -> ExpressionNode:
        expr = self._unary()
        while self._match(TokenType.MULTIPLY, TokenType.DIVIDE):
            op = self._previous().value
            right = self._unary()
            expr = BinaryOperationNode(operator=op, left=expr, right=right)
        return expr

    def _unary(self) -> ExpressionNode:
        if self._match(TokenType.MINUS):
            if self._match(TokenType.NUMBER):
                val_str = self._previous().value
                val = float(val_str) if "." in val_str or "e" in val_str.lower() else int(val_str)
                return LiteralNode(value=-val)
            operand = self._unary()
            return UnaryOperationNode(operator="-", operand=operand)
        if self._match(TokenType.LOGICAL_NOT):
            operand = self._unary()
            return UnaryOperationNode(operator="!", operand=operand)
        return self._primary()

    def _primary(self) -> ExpressionNode:
        # 1. Number literal
        if self._match(TokenType.NUMBER):
            val_str = self._previous().value
            val = float(val_str) if "." in val_str or "e" in val_str.lower() else int(val_str)
            return LiteralNode(value=val)

        # 2. String literal
        if self._match(TokenType.STRING):
            return LiteralNode(value=self._previous().value)

        # 3. Identifier: function call or field
        if self._match(TokenType.IDENTIFIER):
            name = self._previous().value
            if self._match(TokenType.LPAREN):
                # Function call
                args: list[ExpressionNode] = []
                if not self._check(TokenType.RPAREN):
                    args.append(self._expression())
                    while self._match(TokenType.COMMA):
                        args.append(self._expression())
                self._consume(TokenType.RPAREN, f"Expected ')' after arguments for '{name}'")
                return FunctionCallNode(name=name, args=args)
            return FieldNode(name=name)

        # 4. Grouping (parenthesized expression)
        if self._match(TokenType.LPAREN):
            expr = self._expression()
            self._consume(TokenType.RPAREN, "Expected ')' to close expression")
            return expr

        token = self._peek()
        raise ASTSyntaxError(
            f"Unexpected token '{token.value}' at position {token.position}",
            position=token.position,
            token=token.value,
        )

    # --- Helper Methods ---

    def _match(self, *types: TokenType) -> bool:
        for t in types:
            if self._check(t):
                self._advance()
                return True
        return False

    def _check(self, token_type: TokenType) -> bool:
        if self._is_at_end():
            return False
        return self._peek().type == token_type

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _is_at_end(self) -> bool:
        return self.current >= len(self.tokens) or self.tokens[self.current].type == TokenType.EOF

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]

    def _consume(self, token_type: TokenType, error_message: str) -> Token:
        if self._check(token_type):
            return self._advance()
        token = self._peek()
        raise ASTSyntaxError(f"{error_message} (found '{token.value}')", position=token.position, token=token.value)


def parse_expression(expression_str: str) -> ExpressionNode:
    """Tokenize and parse a WorldQuant BRAIN alpha expression string into an AST."""
    tokenizer = Tokenizer(expression_str)
    tokens = tokenizer.tokenize()
    parser = Parser(tokens)
    return parser.parse()
