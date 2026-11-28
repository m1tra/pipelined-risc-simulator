from dataclasses import dataclass
from enum import IntEnum

MASK32 = 0xFFFFFFFF
SIGN_BIT = 1 << 31
MOD32 = 1 << 32


class AluOp(IntEnum):
    ADD = 0x00
    SUB = 0x01
    MUL = 0x02
    DIV = 0x03
    AND = 0x04
    OR = 0x05
    XOR = 0x06
    SLL = 0x07
    SRL = 0x08
    SRA = 0x09
    PASS_A = 0x0A  # think: ret - PC <- ra 
    PASS_B = 0x0B  # for jmp 


@dataclass
class Flags:
    Z: bool = False
    N: bool = False
    V: bool = False
    C: bool = False

def u32(x: int) -> int:
    return x & MASK32


def s32(x: int) -> int:
    x &= MASK32
    return x - MOD32 if x & SIGN_BIT else x


def _set_zn(flags: Flags, res: int) -> None:
    flags.Z = res == 0
    flags.N = bool(res & SIGN_BIT)


def alu(op: AluOp, a: int, b: int) -> tuple[int, Flags]:
    ua, ub = u32(a), u32(b)
    flags = Flags()
    res: int

    if op == AluOp.ADD:
        wide = ua + ub
        res = wide & MASK32
        flags.C = wide > MASK32
        flags.V = bool(~(ua ^ ub) & (ua ^ res) & SIGN_BIT)
        _set_zn(flags, res)

    elif op == AluOp.SUB:
        wide = ua - ub
        res = wide & MASK32
        flags.C = ua >= ub
        flags.V = bool((ua ^ ub) & (ua ^ res) & SIGN_BIT)
        _set_zn(flags, res)

    elif op == AluOp.MUL:
        res = (ua * ub) & MASK32
        _set_zn(flags, res)

    elif op == AluOp.DIV:
        res = 0 if ub == 0 else u32(int(s32(ua) / s32(ub)))
        _set_zn(flags, res)

    elif op == AluOp.AND:
        res = ua & ub
        _set_zn(flags, res)

    elif op == AluOp.OR:
        res = ua | ub
        _set_zn(flags, res)

    elif op == AluOp.XOR:
        res = ua ^ ub
        _set_zn(flags, res)

    elif op == AluOp.SLL:
        res = (ua << (ub & 31)) & MASK32
        _set_zn(flags, res)

    elif op == AluOp.SRL:
        res = ua >> (ub & 31)
        _set_zn(flags, res)

    elif op == AluOp.SRA:
        res = u32(s32(ua) >> (ub & 31))
        _set_zn(flags, res)

    elif op == AluOp.PASS_A:
        res = ua
        _set_zn(flags, res)

    elif op == AluOp.PASS_B:
        res = ub
        _set_zn(flags, res)

    else:
        raise ValueError(f"неизвестная операция: {op}")

    return res, flags
