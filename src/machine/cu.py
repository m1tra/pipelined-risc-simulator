from enum import Enum, auto


from common import Opcode
from isa import Instruction, decode
from machine.alu import AluOp, Flags
from machine.datapath import Datapath
from machine.signals import AddrMuxSignals, AluLeftMux, AluRightMux, Controls, MemSize, PCMuxSignals, RFWriteSignals


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
        
        flags: Flags = self.dp.flags
        
        
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
                    ld_flags=True
                )
                
            case Opcode.ADDI:
                alu_op = ALU_MAP[Opcode.ADD]
                return Controls(
                    operation=alu_op,
                    sel_r_alu=AluRightMux.IMM,
                    sel_l_alu=AluLeftMux.RS1_VAL,
                    ld_flags=True
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
            
            case (
                Opcode.BEQ
                | Opcode.BNE
                | Opcode.BLT
                | Opcode.BGE
                | Opcode.BLTU
                | Opcode.BGEU
            ):
                # jump b_t
                alu_op = ALU_MAP[Opcode.SUB]
                return Controls(
                    operation=alu_op,
                    sel_r_alu=AluRightMux.RS2_VAL,
                    sel_l_alu=AluLeftMux.RS1_VAL,
                    ld_flags=True
                )
            case Opcode.J:
                return Controls(
                    operation=AluOp.PASS_B,
                    sel_r_alu=AluRightMux.IMM,
                )
            # `call label` - `ra <- PC + 4`, затем `PC <- addr(label)` (вызов процедуры)
            case Opcode.CALL:
                return Controls(
                    operation=AluOp.PASS_B,
                    sel_r_alu=AluRightMux.IMM,
                )
            # Возврат по адресу из ra.
            case Opcode.RET:
                return Controls(
                    operation=AluOp.PASS_A,
                    sel_l_alu=AluLeftMux.RS1_VAL,
                )
            # Пустая инструкция.
            case Opcode.NOP:
                return Controls()
            
            # Остановка процессора.
            case Opcode.HALT:
                return Controls(halt=True)
            
            case Opcode.IRET | Opcode.EI | Opcode.DI:
                raise NotImplementedError(
                    "Прерывания пока не реализованы"
                )

            case _:
                raise ValueError(f"Неизвестный opcode: {opcode}")
            
    
    def memory(self, opcode: Opcode) -> Controls:
        match opcode:
            case Opcode.SW:
                return Controls(
                    mem_req=True,
                    mem_we=True,
                    sel_addr=AddrMuxSignals.ALU,
                    mem_size=MemSize.WORD,
                )
    
            case Opcode.SB:
                return Controls(
                    mem_req=True,
                    mem_we=True,
                    sel_addr=AddrMuxSignals.ALU,
                    mem_size=MemSize.BYTE,
                )
    
            case Opcode.LW:
                return Controls(
                    mem_req=True,
                    mem_we=False,
                    sel_addr=AddrMuxSignals.ALU,
                    mem_size=MemSize.WORD,
                )
    
            case Opcode.LBU:
                return Controls(
                    mem_req=True,
                    mem_we=False,
                    sel_addr=AddrMuxSignals.ALU,
                    mem_size=MemSize.BYTE,
                )
    
            case _:
                raise ValueError(
                    f"Инструкция {opcode} не работает с памятью"
                )
            
          
    
    def branch_target(self, opcode: Opcode, flags: Flags):
    
        match opcode:

            case Opcode.BEQ:
                taken = flags.Z
                
            case Opcode.BNE:
                taken =  not flags.Z
                
            case Opcode.BLT:
                taken = flags.N != flags.V

            case Opcode.BGE:
                taken = flags.N == flags.V
                
            case Opcode.BLTU:
                taken = not flags.C

            case Opcode.BGEU:
                taken = flags.C
            
        return Controls(
            operation=AluOp.PASS_B,
            sel_r_alu=AluRightMux.IMM,
            ld_pc=True,
            sel_pc=(
                PCMuxSignals.ALU
                if taken
                else PCMuxSignals.PC4
            )
        )
    
    def writeback(self, opcode: Opcode):
        
        match opcode:
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
                | Opcode.ADDI
                | Opcode.LUI
            ):
                return Controls(
                    rf_we=True,
                    rf_req=True,
                    ld_pc=True,
                    sel_pc=PCMuxSignals.PC4,
                    sel_write=RFWriteSignals.ALU
                )
            case (
                Opcode.LW 
                | Opcode.LBU
            ):
                return Controls(
                    rf_req=True,
                    rf_we=True,
                    ld_pc=True,
                    sel_pc=PCMuxSignals.PC4,
                    sel_write=RFWriteSignals.MEM
                )
        
            case (
                Opcode.SW 
                | Opcode.SB
                | Opcode.NOP
            ):
                return Controls(
                    ld_pc=True,
                    sel_pc=PCMuxSignals.PC4,
                )
            
            case Opcode.CALL:
                # TODO переделать логику для декода через костыль не получилось как с жампом нужно r15 в декод класть
                return Controls(
                    rf_req=True,
                    rf_we=True,
                    sel_write=RFWriteSignals.PC4,
                    ld_pc=True,
                    sel_pc=PCMuxSignals.ALU,
                    
                )
            
            case Opcode.J:
                # TODO класть r0 в жамп раз уж переделываю и call
                return Controls(
                    ld_pc=True,
                    sel_pc=PCMuxSignals.ALU,      
                )

            case Opcode.RET:
                # TODO переделать decode ra -> PC
                return Controls(
                    ld_pc=True,
                    sel_pc=PCMuxSignals.ALU,   
                )
    
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