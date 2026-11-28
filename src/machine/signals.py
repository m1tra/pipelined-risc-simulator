from dataclasses import dataclass
from enum import Enum, auto

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
    #alu
    operation: AluOp | None = None
    sel_l_alu: AluLeftMux | None = None
    sel_r_alu: AluRightMux | None = None
    ld_flags: bool = False

    #mem
    sel_addr: AddrMuxSignals | None = None
    mem_req: bool = False
    mem_size: MemSize | None = None
    mem_we: bool = False

    #rf
    rf_req: bool = False
    rf_we: bool = False
    sel_write: RFWriteSignals | None = None

    #ir
    ld_ir: bool = False

    #pc
    ld_pc: bool = False
    sel_pc: PCMuxSignals | None = None

    halt: bool = False