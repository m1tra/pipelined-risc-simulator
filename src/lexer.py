from isa import Opcode
from token_types import Token, TokenType

DIRECTIVES = {
    ".text",
    ".data",
    ".org",
    ".equ",
    ".word",
    ".byte",
    ".space",
    ".pstr",
    ".global",
    ".extern",
    ".macro",
    ".endm",
    ".if",
    ".else",
    ".endif",
}

REGISTERS = {**{f"r{i}": i for i in range(16)}, "sp": 14, "ra": 15}

MNEMONICS = {str(op) for op in Opcode} | {"li", "la", "mv"}

PUNCT = {
    ":": TokenType.COLON,
    ",": TokenType.COMMA,
    "[": TokenType.LBRACKET,
    "]": TokenType.RBRACKET,
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "@": TokenType.AT,
}

STOP = set(" \t;'\"") | set(PUNCT)

class Lexer:
    def __init__(self, source: str, file: str) -> None:
        self.file = file
        self.source = source
        self.line_index = 0
        self.lines = source.splitlines()
        self.tokens: list[Token] = []

    def classify(self, text: str) -> TokenType:
        result = TokenType.IDENT
        if text in PUNCT:
            result = PUNCT[text]
        elif text in DIRECTIVES:
            result = TokenType.DIRECTIVE
        elif text in REGISTERS:
            result = TokenType.REGISTER
        elif text in MNEMONICS:
            result = TokenType.MNEMONIC
        elif text[0].isdigit():
            result = TokenType.NUMBER
        elif text[0] == "'":
            result = TokenType.CHAR
        elif text[0] == '"':
            result = TokenType.STRING
        return result

    def get_tokens_in_line(self) -> None:
        pos = 0
        line = self.lines[self.line_index]

        while pos < len(line):
            letter = line[pos]

            if letter in " \t":
                pos += 1
                continue
            if letter == ";":
                break
            if letter in PUNCT:
                self.tokens.append(Token(self.classify(letter), letter, self.line_index, self.file))
                pos += 1
                continue
            if letter in "'\"":
                start = pos
                pos += 1
                while pos < len(line) and line[pos] != letter:
                    pos += 2 if line[pos] == "\\" else 1
                pos += 1
                text = line[start:pos]
                self.tokens.append(Token(self.classify(text), text, self.line_index, self.file))
                continue

            start = pos
            while pos < len(line) and line[pos] not in STOP:
                pos += 1
            text = line[start:pos]
            self.tokens.append(Token(self.classify(text), text, self.line_index, self.file))

        self.tokens.append(Token(TokenType.NEWLINE, "\n", self.line_index, self.file))

    def get_tokens(self) -> list[Token]:
        for _ in self.lines:
            self.get_tokens_in_line()
            self.line_index += 1
        return self.tokens
