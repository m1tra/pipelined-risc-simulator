# транслятор
from isa import Term
from token_types import Token, TokenType
from translator_dto import Conditional, Directive, Instruction, MacroCall, MacroDef, Statement

ESCAPES = {"n": "\n", "t": "\t", "0": "\0", "\\": "\\", "'": "'", '"': '"'}  # TODO вынести всё


def decode_quoted(text: str) -> str:
    body = text[1:-1]
    out = []
    i = 0
    while i < len(body):
        if body[i] == "\\":
            out.append(ESCAPES[body[i + 1]])
            i += 2
        else:
            out.append(body[i])
            i += 1
    return "".join(out)


def token_value(tok: Token) -> int | str:
    if tok.token == TokenType.NUMBER:
        return int(tok.text, 0)
    if tok.token == TokenType.CHAR:
        return ord(decode_quoted(tok.text))
    if tok.token == TokenType.STRING:
        return decode_quoted(tok.text)
    return tok.text


MACRO_DIRECTIVE = {
    ".macro",
    ".endm",
}

CONDITION_DIRECTIVE = {
    ".if",
    ".else",
    ".endif",
}


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

    def parse_macro(self, lines: list[list[Token]], index: int) -> tuple[Statement, int]:
        """
        .macro NAME arg1, arg2, ...

            ...

        .endm
        """

        header = lines[index]
        name = header[1].text
        params = [tok.text for tok in header[2:] if tok.token != TokenType.COMMA]

        body: list[Statement] = []
        index += 1

        while lines[index][0].text != ".endm":
            body.append(self.parse_line(lines[index]))
            index += 1

        term = Term(header[0].file, header[0].line_index, " ".join(t.text for t in header))

        return Statement(
            None,
            MacroDef(
                name,
                params,
                body,
            ),
            term,
        ), index + 1

    def parse_conditional(self, lines: list[list[Token]], index: int) -> tuple[Statement, int]:
        """
        .if VAL
            ...
        .else
            ...
        .endif
        """

        header = lines[index]
        condition = token_value(header[1])

        then_body: list[Statement] = []
        index += 1
        while lines[index][0].text not in (".else", ".endif"):
            then_body.append(self.parse_line(lines[index]))
            index += 1

        else_body: list[Statement] | None = None
        if lines[index][0].text == ".else":
            else_body = []
            index += 1
            while lines[index][0].text != ".endif":
                else_body.append(self.parse_line(lines[index]))
                index += 1

        term = Term(header[0].file, header[0].line_index, " ".join(t.text for t in header))
        return Statement(None, Conditional(condition, then_body, else_body), term), index + 1

    def parse(self) -> list[Statement]:
        lines = self.split_lines()
        statements = []
        i = 0
        while i < len(lines):
            head = lines[i][0]

            if head.token == TokenType.DIRECTIVE and head.text == ".macro":
                statement, i = self.parse_macro(lines, i)
            elif head.token == TokenType.DIRECTIVE and head.text == ".if":
                statement, i = self.parse_conditional(lines, i)
            else:
                statement = self.parse_line(lines[i])
                i += 1
            statements.append(statement)

        return statements

    def parse_instruction(self, head: Token, line):
        op = head.text
        operands = [tok for tok in line if tok.token != TokenType.COMMA]
        return Instruction(op, operands)

    def parse_directive(self, head, line):
        name = head.text
        args = [tok for tok in line[2:] if tok.token != TokenType.COMMA]
        return Directive(
            name,
            args,
        )

    def parse_macro_call(self, head: Token, line: list[Token]):
        name = line[1].text
        args = [tok for tok in line[2:] if tok.token != TokenType.COMMA]
        return MacroCall(name, args)

    def parse_line(self, line: list[Token]) -> Statement:
        label = None
        pos = 0

        if line[0].token == TokenType.IDENT and len(line) > 1 and line[1].token == TokenType.COLON:
            label = line[0].text
            pos = 2

        head = line[pos]
        body = None

        if head.token == TokenType.MNEMONIC:
            body = self.parse_instruction(head, line[pos + 1 :])
        if head.token == TokenType.DIRECTIVE:
            body = self.parse_directive(head, line[pos + 1 :])
        if head.token == TokenType.AT:
            body = self.parse_macro_call(head, line[pos + 1 :])

        return Statement(
            label,
            body,
            Term(
                head.file,
                head.line_index,
                " ".join(t.text for t in line),
            ),
        )
