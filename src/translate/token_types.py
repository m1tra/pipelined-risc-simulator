from dataclasses import dataclass
from enum import StrEnum


class TokenType(StrEnum):
    IDENT = "IDENT"

    NUMBER = "NUMBER"
    CHAR = "CHAR"
    STRING = "STRING"

    REGISTER = "REGISTER"
    MNEMONIC = "MNEMONIC"
    DIRECTIVE = "DIRECTIVE"

    COLON = "COLON"
    COMMA = "COMMA"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    PLUS = "PLUS"
    MINUS = "MINUS"
    AT = "AT"

    MACRO = "AT" + "IDENT"

    NEWLINE = "NEWLINE"
    EOF = "EOF"


@dataclass
class Token:
    token: TokenType
    text: str
    line_index: int
    file: str
