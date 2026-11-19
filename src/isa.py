from dataclasses import dataclass
from enum import Enum

from translator_dto import Addr, AsmInstruction
from common import Opcode

OP_SHIFT = 26
RD_SHIFT = 22
RS1_SHIFT = 18
RS2_SHIFT = 14

MASK12 = 0xFFF
MASK18 = 0x3FFFF
MASK20 = 0xFFFFF
MASK26 = 0x3FFFFFF

OP_MASK = 0x3F
REG_MASK = 0x0F



class Format(Enum):
    A = "A"
    I = "I"  # noqa: E741
    LS = "LS"
    B = "B"
    U = "U"
    J = "J"
    NONE = "N"


@dataclass
class Instruction:
    opcode: Opcode
    rd: int = 0
    rs1: int = 0
    rs2: int = 0
    imm: int = 0


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


def sign_extend(word: int, size: int) -> int:
    sign_pos = 1 << (size - 1)
    return (word ^ sign_pos) - sign_pos

def convert_asm_inst_to_inst(inst: AsmInstruction) -> int:
    if isinstance(inst.op, str):
        inst.op = Opcode[inst.op.upper()]
    return encode(inst)


def _imm(value: int | str, what: str) -> int:
    if isinstance(value, str):
        msg = f"неразрешённая метка/символ {value!r} в поле {what}"
        raise ValueError(msg)
    return value


def encode(instruction: AsmInstruction) -> int:  # noqa: PLR0911
    op = instruction.op
    operands = instruction.operands

    match OPCODE_FORMAT[op]:
        case Format.A:
            rd, rs1, rs2 = operands
            return encode_a(op, rd, rs1, rs2)
        case Format.I:
            rd, rs1, imm = operands
            return encode_i(op, rd, rs1, _imm(imm, "imm12"))
        case Format.LS:
            rd, addr = operands
            if not isinstance(addr, Addr):
                msg = f"{op}: второй операнд должен быть адресом [base+off], получено {addr!r}"
                raise TypeError(msg)
            return encode_ls(op, rd, addr.base, _imm(addr.offset, "offset"))
        case Format.B:
            rs1, rs2, off = operands
            return encode_b(op, rs1, rs2, _imm(off, "offset"))
        case Format.U:
            rd, imm = operands
            return encode_u(op, rd, _imm(imm, "imm20"))
        case Format.J:
            (addr,) = operands
            return encode_j(op, _imm(addr, "addr26"))
        case Format.NONE:
            return encode_n(op)
    msg = f"неизвестный формат для {op}"
    raise ValueError(msg)

def decode(word: int) -> Instruction:  # noqa: PLR0911
    op = Opcode((word >> OP_SHIFT) & OP_MASK)
    fmt = OPCODE_FORMAT.get(op)

    rd = (word >> RD_SHIFT) & 0xF
    rs1 = (word >> RS1_SHIFT) & 0xF
    rs2 = (word >> RS2_SHIFT) & 0xF

    match fmt:
        case Format.A:
            return Instruction(op, rd, rs1, rs2)
        case Format.I:
            return Instruction(op, rd, rs1, imm=sign_extend(word & MASK12, 12))
        case Format.LS:
            return Instruction(op, rd, rs1, imm=sign_extend(word & MASK18, 18))
        case Format.B:
            return Instruction(op, rs1=rd, rs2=rs1, imm=sign_extend(word & MASK18, 18))
        case Format.U:
            return Instruction(op, rd, imm=word & MASK20)
        case Format.J:
            return Instruction(op, imm=word & MASK26)
        case Format.NONE:
            return Instruction(op)
        case _:
            msg = f"неизвестный опкод {op}"
            raise ValueError(msg)


def to_bytes(words: list[int]) -> bytes:
    buf = bytearray()
    for word in words:
        buf.extend(word.to_bytes(4, "little"))

    return bytes(buf)


def from_bytes(data: bytes) -> list[int]:
    return [int.from_bytes(data[i : i + 4], "little") for i in range(0, len(data), 4)]
