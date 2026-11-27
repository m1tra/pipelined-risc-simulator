from dataclasses import dataclass
from enum import Enum, auto
from typing import Literal

from machine.alu import AluOp

class AluLeftMux(Enum):
    RS1_VAL = auto()
    PC4 = auto()

class AluRightMux(Enum):
    RS2_VAL = auto()
    IMM = auto()

class MemSize(Enum):
    BYTE = auto()
    WORD = auto()

class Flags(Enum):
    N = auto()
    Z = auto()
    V = auto()
    C = auto()

class AddrMuxSignals(Enum):
    ALU = auto()
    PC = auto()

class PCMuxSignals(Enum):
    PC4 = auto()
    ALU = auto()

class RFWriteSignals(Enum):
    MEM = auto()
    PC4 = auto()
    ALU = auto()

@dataclass
class Controls:
    # aly
    operation: AluOp | Literal[False] = False
    sel_l_alu: AluLeftMux | Literal[False] = False
    sel_r_alu: AluRightMux | Literal[False] = False
    ld_flags: bool = False

    # mem
    sel_addr: AddrMuxSignals | Literal[False] = False
    mem_req: bool = False
    mem_size: MemSize | Literal[False] = False
    mem_we: bool = False

    # rf
    rf_req: bool = False
    rf_we: bool = False
    sel_write: RFWriteSignals | Literal[False] = False

    # ir
    ld_ir: bool = False

    # pc
    ld_pc: bool = False
    sel_pc: PCMuxSignals | Literal[False] = False

    halt: bool = False