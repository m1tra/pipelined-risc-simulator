from enum import Enum, IntEnum


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


class Format(Enum):
    
    A = "A"
    I = "I"
    LS = "LS"
    B = "B"
    U = "U"
    J = "J"
    NONE = "N"


OPCODE_FORMAT: dict[Opcode, Format] = {
    Opcode.NOP: Format.NONE,
    Opcode.ADD: Format.A,
    Opcode.SUB: Format.A,
    Opcode.MUL: Format.A,
    Opcode.DIV: Format.A,
    Opcode.AND: Format.A,
    Opcode.OR: Format.A,
    Opcode.XOR: Format.A,
    Opcode.SLL: Format.A,
    Opcode.SRL: Format.A,
    Opcode.SRA: Format.A,
    Opcode.ADDI: Format.I,
    Opcode.LW: Format.LS,
    Opcode.SW: Format.LS,
    Opcode.LBU: Format.LS,
    Opcode.SB: Format.LS,
    Opcode.BEQ: Format.B,
    Opcode.BNE: Format.B,
    Opcode.BLT: Format.B,
    Opcode.BGE: Format.B,
    Opcode.BLTU: Format.B,
    Opcode.BGEU: Format.B,
    Opcode.LUI: Format.U,
    Opcode.J: Format.J,
    Opcode.CALL: Format.J,
    Opcode.RET: Format.NONE,
    Opcode.IRET: Format.NONE,
    Opcode.EI: Format.NONE,
    Opcode.DI: Format.NONE,
    Opcode.HALT: Format.NONE,
}
