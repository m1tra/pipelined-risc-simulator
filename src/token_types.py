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

    NEWLINE = "NEWLINE"
    EOF = "EOF"
