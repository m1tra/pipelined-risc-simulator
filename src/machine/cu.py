from enum import Enum, auto

from common import Opcode
from isa import Instruction, decode
from machine.alu import AluOp, Flags
from machine.datapath import Datapath
from machine.signals import AddrMuxSignals, AluLeftMux, AluRightMux, Controls, MemSize


ALU_MAP = {
    Opcode.ADD: AluOp.ADD,
    Opcode.SUB: AluOp.SUB,
    Opcode.MUL: AluOp.MUL,
    Opcode.DIV: AluOp.DIV,
    Opcode.AND: AluOp.AND,
    Opcode.OR: AluOp.OR,
    Opcode.XOR: AluOp.XOR,
    Opcode.SLL: AluOp.SLL,
    Opcode.SRL: AluOp.SRL,
    Opcode.SRA: AluOp.SRA,
}

BRANCHES = {
    Opcode.BEQ,
    Opcode.BNE,
    Opcode.BLT,
    Opcode.BGE,
    Opcode.BLTU,
    Opcode.BGEU,
}

LOAD_OPS = {Opcode.LW, Opcode.LBU}
STORE_OPS = {Opcode.SW, Opcode.SB}
INTERRUPT_OPS = {Opcode.EI, Opcode.DI, Opcode.IRET}

class State(Enum):
    FETCH = auto()
    DECODE = auto()
    EXECUTION = auto()
    MEMORY = auto()
    BRANCH_TARGET = auto()
    WRITEBACK = auto()

class ControlUnit:
    
    def __init__(self, dp: Datapath) -> None:
        self.dp = dp
        self.tick = 0
        self.state = State.FETCH
        self.halted = False
        self.signals = Controls()
        
    def step(self) -> None:
        if self.halted:
            raise StopIteration("Процессор остановлен")
    
        self.dp.begin_tick()
    
        inst = decode(self.dp.ir)
        self.dp.rd = inst.rd
        self.dp.rs1 = inst.rs1
        self.dp.rs2 = inst.rs2
        self.dp.imm = inst.imm
        
        opcode: Opcode = inst.opcode
        
        
        match self.state:
            case State.FETCH:
                controls = self.fetch()
            case State.DECODE:
                controls = self.decode()
            case State.EXECUTION:
                controls = self.execution(opcode)
            case State.MEMORY:
                controls = self.memory(inst)
            case State.BRANCH_TARGET:
                controls = self.branch_target(inst)
            case State.WRITEBACK:
                controls = self.writeback(inst)
            case _:
                raise AssertionError(self.state)
    
        self.signals = controls
        self.execute_controls(controls)
    
        self.tick += 1
    
        if controls.halt:
            self.halted = True
        else:
            self.state = self.next_state(inst)
            
    def next_state(inst):
        pass
     
              
    def fetch(self) -> Controls:
        return Controls(
            ld_ir=True,
            sel_addr=AddrMuxSignals.PC,
            mem_req=True,
            mem_size=MemSize.WORD,
        )
        
    
    def decode(self):
        
        return Controls(
            rf_req=True,
            rf_we=False
        )
        
    def execution(self, opcode: Opcode):
        
        match opcode:
            # add rd,rs1,rs2
            case (
                Opcode.ADD
                | Opcode.SUB
                | Opcode.MUL
                | Opcode.DIV
                | Opcode.AND
                | Opcode.OR
                | Opcode.XOR
                | Opcode.SLL
                | Opcode.SRL
                | Opcode.SRA
            ):
                alu_op = ALU_MAP[opcode]
                return Controls(
                    operation=alu_op,
                    sel_r_alu=AluRightMux.RS2_VAL,
                    sel_l_alu=AluLeftMux.RS1_VAL,
                    ld_flags=1
                )
                
            case Opcode.ADDI:
                alu_op = ALU_MAP[Opcode.ADD]
                return Controls(
                    operation=alu_op,
                    sel_r_alu=AluRightMux.IMM,
                    sel_l_alu=AluLeftMux.RS1_VAL,
                    ld_flags=1
                )
            case Opcode.LUI:
                # TODO
                pass
            
            # lw rd, [rs1+off] - rd <- mem32[rs1 + off] don't set flags TODO write it in README also in sw
            case Opcode.LW | Opcode.LBU:
                alu_op = ALU_MAP[Opcode.ADD]
                return Controls(
                    operation=alu_op,
                    sel_r_alu=AluRightMux.IMM,
                    sel_l_alu=AluLeftMux.RS1_VAL,
                )
            
            # sw rd, [rs1+off] - mem32[rs1 + off] <- rd
            case Opcode.SW | Opcode.SB:
                alu_op = ALU_MAP[Opcode.ADD]
                return Controls(
                    operation=alu_op,
                    sel_r_alu=AluRightMux.IMM,
                    sel_l_alu=AluLeftMux.RS1_VAL,
                )
            
    
    def memory(self):
        pass
    
    def branch_target(self):
        pass
    
    def writeback(self):
        pass
    
    def execute_controls(self, c: Controls):
        dp = self.dp
        
        #alu 
        # set alu right
        if c.sel_r_alu:
            dp.right_alu_mux(c.sel_r_alu)
        # set alu left
        if c.sel_l_alu:
            dp.left_alu_mux(c.sel_l_alu)
            
        #alu exec
        if c.operation:
            dp.alu_exec(
                c.operation,
                c.ld_flags
            )
        
        #mem req
        if c.mem_req:
            assert c.sel_addr
            assert c.mem_size
            
            dp.addr_mux(c.sel_addr)
            
            if c.mem_we:
                dp.mem_write(c.mem_size)
            else:
                dp.mem_read(c.mem_size)
                
        #pc
        if c.ld_pc:
            assert c.sel_pc
            
            dp.pc_mux(c.sel_pc)
            dp.pc_latch()   
        
        #ir
        if c.ld_ir:
            dp.ir_latch()
            
        #rf
        if c.rf_req:
            if c.rf_we:
                assert c.sel_write

                dp.write_rf_mux(c.sel_write)
                dp.write_rf()
            else:
                dp.rs1_mux()
                dp.rs2_mux()
                dp.read_rf()