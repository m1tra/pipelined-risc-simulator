from enum import IntEnum
from typing import NamedTuple


class Term(NamedTuple):
    file: str
    line: int
    text: str


class Opcode(IntEnum):
    NOP = 0x00

    ADD = 0x01
    SUB = 0x02
    MUL = 0x03
    DIV = 0x04
    AND = 0x05
    OR = 0x06
    XOR = 0x07
    SLL = 0x08
    SRL = 0x09
    SRA = 0x0A

    ADDI = 0x0B

    LW = 0x0C
    SW = 0x0D
    LBU = 0x0E
    SB = 0x0F

    BEQ = 0x10
    BNE = 0x11
    BLT = 0x12
    BGE = 0x13
    BLTU = 0x14
    BGEU = 0x15

    LUI = 0x16

    J = 0x17
    CALL = 0x18
    RET = 0x19

    IRET = 0x1A
    EI = 0x1B
    DI = 0x1C

    HALT = 0x3F

    def __str__(self) -> str:
        return self.name.lower()
