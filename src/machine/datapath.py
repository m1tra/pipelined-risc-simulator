from dataclasses import dataclass

# TODO вынести в конфиг
MEM_SIZE = 256


class RegisterFile:
    def __init__(self):
        self.regs: int = [0] * 16

    def read(self, n: int) -> int:
        return 0 if n == 0 else self.regs[n]

    def write(self, n: int, val: int) -> None:
        if n != 0:
            self.regs[n] = val


@dataclass
class IFID:
    ir: int
    pc4: int


@dataclass
class IDEX:
    imm: int
    rs1: int
    rs2: int
    rd: int


@dataclass
class FlagResiter:
    Z: bool
    N: bool
    V: bool
    C: bool


class Datapath:
    def __init__(self):
        self.mem = bytearray(MEM_SIZE)
        self.rf = RegisterFile
        self.pc = 0
        self.flags = FlagResiter
