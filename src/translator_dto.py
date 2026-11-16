from __future__ import annotations

from dataclasses import dataclass

from isa import Opcode, Term


@dataclass
class Addr:
    base: int
    offset: int | str


Operand = int | str | Addr


@dataclass
class Instruction:
    op: Opcode | str
    operands: list[Operand]


@dataclass
class Directive:
    name: str
    args: list[int | str]


@dataclass
class MacroCall:
    name: str
    args: list[int | str]


@dataclass
class MacroDef:
    name: str
    params: list[str]
    body: list[Statement]


@dataclass
class Conditional:
    condition: int | str
    then_body: list[Statement]
    else_body: list[Statement] | None


@dataclass
class Statement:
    label: str | None
    body: Instruction | Directive | MacroCall | MacroDef | Conditional
    term: Term
