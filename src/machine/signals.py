from enum import Enum, auto

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
    