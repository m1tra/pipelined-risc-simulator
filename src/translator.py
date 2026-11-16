# транслятор
from lexer import Lexer
from token_types import Token, TokenType


class Parser:
    
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        
    def split_lines(self) -> list[list[Token]]:
        lines: list[list[Token]] = []
        current: list[Token] = []
        
        for token in self.tokens:
            if token.token == TokenType.NEWLINE:
                if current:
                    lines.append(current)
                    current = []
            else:
                current.append(token)
        if current:
            lines.append(current)
        return lines
    
    
    def pasrse(self):
        
        lines = self.split_lines(self.tokens)
        
        for line in lines:
            pass
            
            
            
src = """\
.equ LED, 0x10        ; порт вывода

start: li r1, 'A'
loop:  sw r1, [r2+LED]
       j loop
.pstr "a;b"
"""

lexer = Lexer(src, "sadf")


tokens = lexer.get_tokens()
print(tokens)

parser = Parser(tokens)
parser.pasrse()
