from enum import Enum, IntEnum

OP_SHIFT = 26
RD_SHIFT = 22
RS1_SHIFT = 18
RS2_SHIFT = 14

MASK12 = 0xFFF
MASK18 = 0x3FFFF
MASK20 = 0xFFFFF
MASK26 = 0x3FFFFFF


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
    I = "I"  # noqa: E741
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


def encode_a(op: Opcode, rd: int, rs1: int, rs2: int) -> int:
    """op[31:26] rd[25:22] rs1[21:18] rs2[17:14] 0[13:0]"""
    return (op << OP_SHIFT) | (rd << RD_SHIFT) | (rs1 << RS1_SHIFT) | (rs2 << RS2_SHIFT)


def encode_i(op: Opcode, rd: int, rs1: int, imm12: int) -> int:
    """op[31:26] rd[25:22] rs1[21:18] 0[17:12] imm12[11:0]"""
    return (op << OP_SHIFT) | (rd << RD_SHIFT) | (rs1 << RS1_SHIFT) | (imm12 & MASK12)


def encode_ls(op: Opcode, rd: int, rs1: int, off18: int) -> int:
    """op[31:26] rd[25:22] rs1[21:18] off18[17:0]"""
    return (op << OP_SHIFT) | (rd << RD_SHIFT) | (rs1 << RS1_SHIFT) | (off18 & MASK18)


def encode_b(op: Opcode, rs1: int, rs2: int, off18: int) -> int:
    """op[31:26] rs1[25:22] rs2[21:18] off18[17:0]"""
    return (op << OP_SHIFT) | (rs1 << RD_SHIFT) | (rs2 << RS1_SHIFT) | (off18 & MASK18)


def encode_u(op: Opcode, rd: int, imm20: int) -> int:
    """op[31:26] rd[25:22] 0[21:20] imm20[19:0]"""
    return (op << OP_SHIFT) | (rd << RD_SHIFT) | (imm20 & MASK20)


def encode_j(op: Opcode, addr26: int) -> int:
    """op[31:26] addr26[25:0]"""
    return (op << OP_SHIFT) | (addr26 & MASK26)


def encode_n(op: Opcode) -> int:
    """op[31:26] 0[25:0]"""
    return op << OP_SHIFT
