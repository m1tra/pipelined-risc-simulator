from dataclasses import dataclass


@dataclass
class RegisterFile:
    r0: int
    r1: int
    r2: int
    r3: int
    r4: int
    r5: int
    r6: int
    r7: int
    r8: int
    r9: int
    r10: int
    r11: int
    r12: int
    r13: int
    r14: int
    r15: int
    
@dataclass
class InstructionFetchState:
    ir: int
    pc: int
    
@dataclass
class IFID:
    ir: int
    pc: int

@dataclass
class IDEX:
    imm: int
    rs1:int
    rs2:int
    rd:int
    
class Datapath:
    
    def __init__():
        pass
    
    