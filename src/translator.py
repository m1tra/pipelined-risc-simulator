# транслятор
import copy
from pathlib import Path

from common import Term
from isa import convert_asm_inst_to_inst
from lexer import REGISTERS, Lexer
from token_types import Token, TokenType
from translator_dto import (
    Addr,
    AsmInstruction,
    Cell,
    Conditional,
    Directive,
    Equ,
    MacroCall,
    MacroDef,
    Operand,
    Statement,
)

ESCAPES = {"n": "\n", "t": "\t", "0": "\0", "\\": "\\", "'": "'", '"': '"'}

ADDR_OFFSET_INDEX = 3


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

    def parse_operand(self, group: list[Token]) -> Operand:
        first = group[0]

        if first.token == TokenType.LBRACKET:
            base = REGISTERS[group[1].text]
            offset: int | str = 0
            if len(group) > ADDR_OFFSET_INDEX:
                value = token_value(group[ADDR_OFFSET_INDEX])
                if group[2].token == TokenType.MINUS and isinstance(value, int):
                    value = -value
                offset = value
            return Addr(base, offset)

        if first.token == TokenType.REGISTER:
            return REGISTERS[first.text]
        if first.token == TokenType.MINUS:
            value = token_value(group[1])
            return -value if isinstance(value, int) else value
        return token_value(first)

    def parse_instruction(self, head: Token, line: list[Token]) -> AsmInstruction:
        groups: list[list[Token]] = [[]]
        for tok in line:
            if tok.token == TokenType.COMMA:
                groups.append([])
            else:
                groups[-1].append(tok)

        return AsmInstruction(head.text, [self.parse_operand(group) for group in groups])

    def parse_directive(self, head: Token, line: list[Token]) -> Directive | Equ:
        name = head.text

        args = [token_value(tok) for tok in line if tok.token != TokenType.COMMA]

        if name == ".equ":
            return Equ(str(args[0]), args[1])

        return Directive(
            name,
            args,
        )

    def parse_macro_call(self, line: list[Token]) -> MacroCall:
        name = line[0].text
        args = [token_value(tok) for tok in line[1:] if tok.token != TokenType.COMMA]
        return MacroCall(name, args)

    def parse_line(self, line: list[Token]) -> Statement:
        label = None
        pos = 0

        if line[0].token == TokenType.IDENT and len(line) > 1 and line[1].token == TokenType.COLON:
            label = line[0].text
            pos = 2

        anchor = line[pos] if pos < len(line) else line[0]
        body: AsmInstruction | Directive | Equ | MacroCall | None = None

        if pos < len(line):
            if anchor.token == TokenType.MNEMONIC:
                body = self.parse_instruction(anchor, line[pos + 1 :])
            elif anchor.token == TokenType.DIRECTIVE:
                body = self.parse_directive(anchor, line[pos + 1 :])
            elif anchor.token == TokenType.AT:
                body = self.parse_macro_call(line[pos + 1 :])
            else:
                msg = f"неожиданный токен {anchor.text!r}"
                raise SyntaxError(msg)

        return Statement(
            label,
            body,
            Term(
                anchor.file,
                anchor.line_index,
                " ".join(t.text for t in line),
            ),
        )

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


class Preprocessor:
    def __init__(self) -> None:
        self.macros: dict[str, MacroDef] = {}
        self.consts: dict[str, int | str] = {}
        self.counter = 0

    def change_operand(self, op: Operand, args: dict[str, int | str]) -> Operand:

        if isinstance(op, str) and op in args:
            return args[op]

        return op

    def substitute_statement(
        self,
        statement: Statement,
        args: dict[str, int | str],
        local_labels: set[str],
        suffix: str,
    ) -> None:

        if statement.label and statement.label in local_labels:
            statement.label += suffix

        body = statement.body

        if isinstance(body, AsmInstruction):
            body.operands = [self.change_operand(op, args) for op in body.operands]

        elif isinstance(body, Equ):
            if isinstance(body.value, str) and body.value in args:
                body.value = args[body.value]

        elif isinstance(body, (MacroCall, Directive)):
            body.args = [args.get(a, a) if isinstance(a, str) else a for a in body.args]

        elif isinstance(body, Conditional):
            if isinstance(body.condition, str) and body.condition in args:
                body.condition = args[body.condition]

            for s in body.then_body + (body.else_body or []):
                self.substitute_statement(s, args, local_labels, suffix)

    def expand_macro(self, call: MacroCall, definition: MacroDef, counter: int) -> list[Statement]:
        if len(call.args) != len(definition.params):
            msg = f"макрос {call.name}: ожидается {len(definition.params)} аргументов, получено {len(call.args)}"
            raise SyntaxError(msg)

        subst_args = dict(zip(definition.params, call.args, strict=True))
        local_labels = {s.label for s in definition.body if s.label}
        suffix = f"__m{counter}"

        expanded = []

        for statement in copy.deepcopy(definition.body):
            self.substitute_statement(statement, subst_args, local_labels, suffix)

            expanded.append(statement)

        return expanded

    def run(self, statements: list[Statement]) -> list[Statement]:
        out = []
        for statement in statements:
            match statement.body:
                case MacroDef() as m:
                    self.macros[m.name] = m
                case MacroCall() as call:
                    expanded = self.expand_macro(call, self.macros[call.name], self.counter)
                    self.counter += 1
                    out.extend(self.run(expanded))
                case Conditional() as c:
                    cond = self.consts.get(c.condition, c.condition) if isinstance(c.condition, str) else c.condition
                    out.extend(self.run(c.then_body if cond else (c.else_body or [])))
                case Equ() as e:
                    self.consts[e.name] = e.value
                case _:
                    out.append(statement)
        return out


class Translator:
    def __init__(self, statements: list[Statement], consts: dict[str, int | str] | None = None) -> None:
        self.statements = statements
        self.consts = consts or {}
        self.section = ".text"
        self.cells: list[Cell] = []
        self.labels: dict[str, tuple[str, int]] = {}
        self.base: dict[str, int] = {}

    def place(self, st: Statement, ptr: dict[str, int]) -> None:
        match st.body:
            case Directive(name=".text"):
                self.section = ".text"
            case Directive(name=".data"):
                self.section = ".data"
            case Directive(name=".org", args=[a]):
                ptr[self.section] = self.resolve(a)
            case AsmInstruction():
                self.cells.append(Cell(self.section, ptr[self.section], 4, None, st))
                ptr[self.section] += 4
            case Directive(name=".word", args=args):
                self.cells.append(Cell(self.section, ptr[self.section], 4 * len(args), None, st))
                ptr[self.section] += 4 * len(args)
            case Directive(name=".byte", args=args):
                self.cells.append(Cell(self.section, ptr[self.section], len(args), None, st))
                ptr[self.section] += len(args)
            case Directive(name=".pstr", args=[str() as s]):
                self.cells.append(Cell(self.section, ptr[self.section], len(s) + 1, None, st))
                ptr[self.section] += len(s) + 1
            case Directive(name=".space", args=[n]):
                ptr[self.section] += self.resolve(n)
            case Directive(name=name) if name in {".word", ".byte", ".pstr", ".space", ".org"}:
                msg = f"некорректные аргументы директивы {name}: {st.body.args!r}"
                raise SyntaxError(msg)

    def walk1(self) -> None:

        ptr = {".text": 0, ".data": 0}

        for st in self.statements:
            if st.label:
                self.labels[st.label] = (self.section, ptr[self.section])

            self.place(st, ptr)

        self.base = {".text": 0, ".data": (ptr[".text"] + 3) & ~3}

    def resolve(self, value: int | str) -> int:
        if isinstance(value, int):
            return value
        if value in self.consts:
            const = self.consts[value]
            if isinstance(const, int):
                return const
            value = const
        if value in self.labels:
            seg, off = self.labels[value]
            return self.base[seg] + off
        msg = f"неизвестный символ {value!r}"
        raise ValueError(msg)

    def resolve_operand(self, op: Operand) -> Operand:
        if isinstance(op, str):
            return self.resolve(op)
        if isinstance(op, Addr) and isinstance(op.offset, str):
            op.offset = self.resolve(op.offset)
        return op

    def walk2(self) -> None:

        for cell in self.cells:
            cell_body = cell.statement.body

            match cell_body:
                case AsmInstruction() as inst:
                    inst.operands = [self.resolve_operand(o) for o in inst.operands]
                    cell.blob = convert_asm_inst_to_inst(inst).to_bytes(4, "little")
                case Directive(name=".word", args=args):
                    cell.blob = b"".join(self.resolve(a).to_bytes(4, "little") for a in args)
                case Directive(name=".byte", args=args):
                    cell.blob = bytes(self.resolve(a) & 0xFF for a in args)
                case Directive(name=".pstr", args=[str() as s]):
                    cell.blob = bytes([len(s)]) + s.encode("ascii")
                case Directive() as d:
                    msg = f"не могу закодировать директиву {d.name}: аргументы {d.args!r}"
                    raise ValueError(msg)


class DumpFiles:
    def __init__(self, cells: list[Cell], base: dict[str, int]) -> None:
        self.cells = cells
        self.base = base

    def addr_of(self, cell: Cell) -> int:
        return self.base[cell.segment] + cell.offset

    def to_bin(self, path: str = "out/out.bin") -> None:
        size = max((self.addr_of(c) + c.size for c in self.cells), default=0)
        image = bytearray(size)
        for cell in self.cells:
            addr = self.addr_of(cell)
            blob = cell.blob or b""
            image[addr : addr + cell.size] = blob
        Path(path).write_bytes(image)

    def to_listing(self, path: str = "out/listing.txt") -> None:
        lines = []
        for cell in self.cells:
            addr = self.addr_of(cell)
            hexs = cell.blob.hex(" ") if cell.blob else ""
            lines.append(f"{addr:08x} - {hexs} - {cell.statement.term.text}")
        Path(path).write_text("\n".join(lines) + "\n")


def main() -> None:
    src = """\
.equ LED, 0x10

.data
.byte 0x20
.word 0x233
.word LED
msg: .pstr "hello"

.text
.org 0x100
.macro check value
    addi r1, r2, 3
.endm

start: sw r1, [r2-4]

j start

@check 222
"""

    lexer = Lexer(src, "example.asm")
    tokens = lexer.get_tokens()

    parser = Parser(tokens)

    preprocessor = Preprocessor()
    statements = preprocessor.run(parser.parse())

    translator = Translator(statements, preprocessor.consts)
    translator.walk1()
    translator.walk2()

    files_instance = DumpFiles(translator.cells, translator.base)
    files_instance.to_listing()
    files_instance.to_bin()


if __name__ == "__main__":
    main()
