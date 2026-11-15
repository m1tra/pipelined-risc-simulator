from dataclasses import dataclass

from isa import Opcode
from token_types import TokenType

DIRECTIVES = {
    ".text", ".data", ".org", ".equ", ".word", ".byte",
    ".space", ".pstr", ".global", ".extern",
    ".macro", ".endm", ".if", ".else", ".endif",
}

REGISTERS = {**{f"r{i}": i for i in range(16)}, "sp": 14, "ra": 15}

MNEMONICS = {str(op) for op in Opcode} | {"li", "la", "mv"}

PUNCT = {
    ":": TokenType.COLON, ",": TokenType.COMMA,
    "[": TokenType.LBRACKET, "]": TokenType.RBRACKET,
    "+": TokenType.PLUS, "-": TokenType.MINUS, "@": TokenType.AT,
}

STOP = set(" \t;'\"") | set(PUNCT) # не относится к токенам

@dataclass
class Token:
    token: TokenType
    text: str
    line_index: int
    file: str


class Lexer:
    def __init__(self, source, file):
        self.file = file
        self.source = source
        self.line_index = 0
        self.lines = source.splitlines()
        self.tokens: Token = []
        
    def classify(self, text: str) -> TokenType:
        
        if text in PUNCT:       return PUNCT[text]
        if text in DIRECTIVES:  return TokenType.DIRECTIVE
        if text in REGISTERS:   return TokenType.REGISTER
        if text in MNEMONICS:   return TokenType.MNEMONIC
        if text[0].isdigit():   return TokenType.NUMBER
        if text[0] == "'":      return TokenType.CHAR
        if text[0] == '"':      return TokenType.STRING

        return TokenType.IDENT
        
    def get_tokens_in_line(self):

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
                self.tokens.append(
                    Token(
                        self.classify(letter),
                        letter,
                        self.line_index,
                        self.file
                    )
                )
                pos += 1
                continue
                
            if letter in "'\"":
                start = pos
                pos += 1
                while pos < len(line) and line[pos] != letter:
                    pos += 2 if line[pos] == "\\" else 1
                pos += 1
                text = line[start:pos]
                self.tokens.append(
                    Token(
                        self.classify(text), 
                        text,
                        self.line_index,
                        self.file)
                    )
                continue
            
            start = pos
            while pos < len(line) and line[pos] not in STOP:
                pos += 1
            text = line[start:pos]
            self.tokens.append(Token(
                self.classify(text), 
                text,
                self.line_index,
                self.file
            ))
            

            
        self.tokens.append(Token(TokenType.NEWLINE, "\n", self.line_index, self.file))
    
    def get_tokens(self):
        for _ in self.lines:
            self.get_tokens_in_line()
            self.line_index+=1
        return self.tokens
        
            

        
src = """\
.equ LED, 0x10        ; порт вывода

start: li r1, 'A'
loop:  sw r1, [r2+LED]
       j loop
.pstr "a;b"
"""

lexer = Lexer(src,"asdfg")
for i in lexer.get_tokens():
    print(i.text)


