from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from translate.common import Opcode, Term


@dataclass
class Addr:
    base: int
    offset: int | str


Operand = int | str | Addr


@dataclass
class AsmInstruction:
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
class Equ:
    name: str
    value: int | str


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
    body: AsmInstruction | Directive | MacroCall | MacroDef | Conditional | Equ | None
    term: Term


@dataclass
class Cell:
    segment: str
    offset: int
    size: int
    blob: bytes | None
    statement: Statement
