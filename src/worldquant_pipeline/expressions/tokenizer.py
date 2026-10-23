"""Tokenizer for WorldQuant BRAIN alpha expressions."""
from dataclasses import dataclass
from enum import Enum, auto
from typing import ClassVar

from worldquant_pipeline.exceptions import ASTSyntaxError


class TokenType(Enum):
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LOGICAL_AND = auto()
    LOGICAL_OR = auto()
    LOGICAL_NOT = auto()
    QUESTION = auto()
    COLON = auto()
    COMMA = auto()
    LPAREN = auto()
    RPAREN = auto()
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    value: str
    position: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, '{self.value}', pos={self.position})"


class Tokenizer:
    """Scans and tokenizes an alpha expression string."""

    # Multi-character symbols matched first
    OPERATORS_MAP: ClassVar[dict[str, TokenType]] = {
        "==": TokenType.EQUAL,
        "!=": TokenType.NOT_EQUAL,
        "<=": TokenType.LESS_EQUAL,
        ">=": TokenType.GREATER_EQUAL,
        "&&": TokenType.LOGICAL_AND,
        "||": TokenType.LOGICAL_OR,
        "+": TokenType.PLUS,
        "-": TokenType.MINUS,
        "*": TokenType.MULTIPLY,
        "/": TokenType.DIVIDE,
        "<": TokenType.LESS,
        ">": TokenType.GREATER,
        "!": TokenType.LOGICAL_NOT,
        "?": TokenType.QUESTION,
        ":": TokenType.COLON,
        ",": TokenType.COMMA,
        "(": TokenType.LPAREN,
        ")": TokenType.RPAREN,
    }

    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0
        self.length = len(text)

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []

        while self.pos < self.length:
            char = self.text[self.pos]

            # 1. Skip whitespace
            if char.isspace():
                self.pos += 1
                continue

            # 2. String literal: '...' or "..."
            if char in ("'", '"'):
                start_pos = self.pos
                quote_char = char
                self.pos += 1
                str_val = []
                while self.pos < self.length and self.text[self.pos] != quote_char:
                    str_val.append(self.text[self.pos])
                    self.pos += 1
                if self.pos >= self.length:
                    raise ASTSyntaxError("Unterminated string literal", position=start_pos)
                self.pos += 1  # Consume closing quote
                tokens.append(Token(TokenType.STRING, "".join(str_val), start_pos))
                continue

            # 3. Two-character operators
            if self.pos + 1 < self.length:
                two_char = self.text[self.pos : self.pos + 2]
                if two_char in self.OPERATORS_MAP:
                    tokens.append(Token(self.OPERATORS_MAP[two_char], two_char, self.pos))
                    self.pos += 2
                    continue

            # 4. Single-character operators
            if char in self.OPERATORS_MAP:
                tokens.append(Token(self.OPERATORS_MAP[char], char, self.pos))
                self.pos += 1
                continue

            # 5. Number literals (including decimal points)
            if char.isdigit() or (char == "." and self.pos + 1 < self.length and self.text[self.pos + 1].isdigit()):
                start_pos = self.pos
                while self.pos < self.length and (
                    self.text[self.pos].isdigit() or self.text[self.pos] == "." or self.text[self.pos] in "eE"
                ):
                    self.pos += 1
                val = self.text[start_pos : self.pos]
                tokens.append(Token(TokenType.NUMBER, val, start_pos))
                continue

            # 6. Identifiers (variable names, operator names)
            if char.isalpha() or char == "_":
                start_pos = self.pos
                while self.pos < self.length and (self.text[self.pos].isalnum() or self.text[self.pos] == "_"):
                    self.pos += 1
                val = self.text[start_pos : self.pos]
                tokens.append(Token(TokenType.IDENTIFIER, val, start_pos))
                continue

            raise ASTSyntaxError(
                f"Unexpected character '{char}' at position {self.pos}",
                position=self.pos,
                token=char,
            )

        tokens.append(Token(TokenType.EOF, "", self.pos))
        return tokens
