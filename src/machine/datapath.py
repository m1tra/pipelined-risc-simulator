

# TODO в config
from isa import Instruction
from machine.alu import AluOp, Flags, alu, u32
from machine.signals import AddrMuxSignals, AluLeftMux, AluRightMux, MemSize, PCMuxSignals, RFWriteSignals

BYTE_MASK = 0xFF

MEM_SIZE = 4096
PORT_IN = 0xF0
PORT_OUT = 0xF4




class RegisterFile:

    def __init__(self) -> None:
        self.regs: list[int] = [0] * 16

    def read(self, n: int) -> int:
        return 0 if n == 0 else self.regs[n]

    def write(self, n: int, val: int) -> None:
        if n != 0:
            self.regs[n] = u32(val)
            
            
class Memory:

    def __init__(
        self,
        size: int = MEM_SIZE,
        *,
        input_port: int = 0,
        port_in: int = PORT_IN,
        port_out: int = PORT_OUT,
    ) -> None:

        self.memory: list[int] = [0] * size
        self.input_port = input_port & BYTE_MASK
        self.output_port: list[int] = []
        self.port_in = port_in
        self.port_out = port_out

        self.mem_read_data = 0
        self.mem_rdy = False

    def _check_ram_address(self, addr: int) -> None:
        if not 0 <= addr < len(self.memory):
            msg = f"Адрес вне памяти: {addr:#x}"
            raise IndexError(msg)

    def read_byte(self, addr: int) -> int:
        if addr == self.port_in:
            return self.input_port

        self._check_ram_address(addr)
        return self.memory[addr]

    def write_byte(self, addr: int, data: int) -> None:
        if addr == self.port_out:
            self.output_port.append(data & BYTE_MASK)
            return

        self._check_ram_address(addr)
        self.memory[addr] = data & BYTE_MASK

    def read_word(self, addr: int) -> int:
        return sum(self.read_byte(addr + i) << (8 * i) for i in range(4))

    def write_word(self, addr: int, data: int) -> None:
        for i in range(4):
            self.write_byte(addr + i, data >> (8 * i))

    def read(self, addr: int, size: MemSize) -> None:
        if size == MemSize.BYTE:
            self.mem_read_data = self.read_byte(addr)
        else:
            self.mem_read_data = self.read_word(addr)
        self.mem_rdy = True

    def write(self, addr: int, size: MemSize, data: int) -> None:
        if size == MemSize.BYTE:
            self.write_byte(addr, data)
        else:
            self.write_word(addr, data)
        self.mem_rdy = True

    def load_bytes(self, data: bytes, start: int = 0) -> None:
        end = start + len(data)
        if start < 0 or end > len(self.memory):
            msg = f"Программа не помещается в память: {start:#x}..{end:#x}"
            raise ValueError(msg)
        self.memory[start:end] = data
        

class Datapath:

    def __init__(self, mem_size: int = MEM_SIZE) -> None:
        self.mem = Memory(mem_size)
        self.rf = RegisterFile()

        self.pc = 0
        self.ir = 0
        self.flags = Flags()
        
        self.rs1 = 0
        self.rs2 = 0
        self.imm = 0
        self.rd = 0

        self.pc4 = 0
        
        self.rs1_val = 0
        self.rs2_val = 0
        self.rd_val = 0
        
        self.alu_left = 0
        self.alu_right = 0
        self.alu_result = 0
        
        self.mem_read_data = 0
        
        self.addr_bus = 0
        self.rf_write_bus = 0
        
        self.pc_bus = 0

    def begin_tick(self) -> None:
        self.mem.mem_rdy = False
        self.pc4 = u32(self.pc + 4)
        

    def rs1_mux(self) -> int:
        self.rs1_val = self.rf.read(self.rs1)
        return self.rs1_val

    def rs2_mux(self) -> int:
        self.rs2_val = self.rf.read(self.rs2)
        return self.rs2_val

    def left_alu_mux(self, sel_l_alu: AluLeftMux) -> None:
        if (sel_l_alu == AluLeftMux.RS1_VAL):
            self.alu_left = self.rs1_val
        elif (sel_l_alu == AluLeftMux.PC4):
            self.alu_left = self.pc4
    
    def right_alu_mux(self, sel_r_alu: AluRightMux) -> None:
        if (sel_r_alu == AluRightMux.RS2_VAL):
            self.alu_right = self.rs2_val
        elif (sel_r_alu == AluRightMux.IMM):
            self.alu_right = self.imm

    def alu_exec(self, operation: AluOp, ld_flags: bool) -> None:
        result, flags = alu(operation, self.alu_left, self.alu_right)
        self.alu_result = result
        if ld_flags:
            self.flags = flags
        
    def addr_mux(self, sel_addr:AddrMuxSignals) -> None:
        
        if (sel_addr == AddrMuxSignals.ALU):
            self.addr_bus = self.alu_result
        elif (sel_addr == AddrMuxSignals.PC):
            self.addr_bus = self.pc
            
    def mem_read(self, inst_size: MemSize) -> None:
        
        self.mem.read(self.addr_bus, inst_size)
        
        self.mem_read_data = self.mem.mem_read_data
        
    def mem_write(self, inst_size: MemSize) -> None:
        
        self.mem.write(self.addr_bus, inst_size, self.rd_val)
        
    def write_rf_mux(self, rf_write: RFWriteSignals):
        
       match rf_write:
            case RFWriteSignals.ALU:
                self.rf_write_bus = self.alu_result
            case RFWriteSignals.PC4:
                self.rf_write_bus = self.pc4
            case RFWriteSignals.MEM:
                self.rf_write_bus = self.mem_read_data
        
    
    def write_rf(self):
        # think 'bout rf_we also in mem
        self.rf.write(self.rd, self.rf_write_bus)
    
    def read_rf_rd(self):
        
        self.rd_val = self.rf.read(self.rd)
    
    def ir_latch(self):
    
        self.ir = self.mem_read_data
        

    def pc_mux(self, sel_pc: PCMuxSignals) -> None:
        if sel_pc == PCMuxSignals.PC4:
            self.pc_bus = self.pc4
        else:
            self.pc_bus = self.alu_result
            
    def pc_latch(self):
        self.pc = self.pc_bus
