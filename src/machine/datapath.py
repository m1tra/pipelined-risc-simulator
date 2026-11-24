from dataclasses import dataclass

from machine.alu import AluOp, Flags, alu

BYTE_MASK = 0xFF

# TODO вынести в конфиг
MEM_SIZE = 256
PORT_IN = 0xF0
PORT_OUT = 0xF4

class RegisterFile:
    def __init__(self):
        self.regs: list[int] = [0] * 16

    def read(self, n: int) -> int:
        return 0 if n == 0 else self.regs[n]

    def write(self, n: int, val: int) -> None:
        if n != 0:
            self.regs[n] = val
            
            
class Memory:
    def __init__(self, size: int = MEM_SIZE) -> None:
        self.memory: list[int] = [0] * size
        self.input_port = 0
        self.output_port: list[int] = []
        
    def read_byte(self, addr: int) -> int:
        if addr == PORT_IN:
            return self.input_port
        return self.memory[addr]
    
    def write_byte(self, addr: int, data:int) ->  None:
        if addr == PORT_OUT:
            self.output_port.append(data & BYTE_MASK)
            return
        self.memory[addr] = data & BYTE_MASK 
        
    def read_word(self, add:int) -> int:
        pass 
        
    def write_word(self, addr: int, data:int) ->  None:
        pass

    

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


class Datapath:
    def __init__(self):
        self.mem = Memory(MEM_SIZE)
        self.rf = RegisterFile()
        self.pc = 0
        self.flags = Flags()
        
        
    def alu_exec(self, op: AluOp, a: int, b: int) -> int:
        res, self.flags = alu(op, a, b)
        return res
    
    def latch_pc():
        pass
        
    

    