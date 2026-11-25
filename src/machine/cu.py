from common import Opcode
from isa import Instruction, decode
from machine.alu import AluOp
from machine.datapath import Datapath


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

RA = 15

class ControlUnit:
    def __init__(self, dp: Datapath) -> None:
        self.dp = dp
        self.tick = 0

    def run_instruction(self) -> None:
        dp = self.dp

        # такт 1 (IF): выборка
        ir = dp.mem.read_word(dp.pc)
        dp.latch_pc(dp.pc + 4)
        self.tick += 1

        # такт 2 (ID): декод + чтение регистров
        inst = decode(ir)
        # 
        rs1_val = dp.rf.read(inst.rs1)
        rs2_val = dp.rf.read(inst.rs2)
        imm = inst.imm
        self.tick += 1
        
        # такт 3 (EX): исполнение
        match inst.opcode:
            case op if op in ALU_MAP:
                dp.rf.write(inst.rd, dp.alu_exec(ALU_MAP[op], rs1_val, rs2_val))

            case Opcode.ADDI:
                dp.rf.write(inst.rd, dp.alu_exec(AluOp.ADD, rs1_val, imm))

            case Opcode.LUI:
                dp.rf.write(inst.rd, (imm << 12) & 0xFFFFFFFF)

            case Opcode.LW:
                addr = dp.alu_exec(AluOp.ADD, rs1_val, imm)
                dp.rf.write(inst.rd, dp.mem.read_word(addr))

            case Opcode.SW:
                addr = dp.alu_exec(AluOp.ADD, rs1_val, imm)
                dp.mem.write_word(addr, dp.rf.read(inst.rd))

            case Opcode.LBU:
                addr = dp.alu_exec(AluOp.ADD, rs1_val, imm)
                dp.rf.write(inst.rd, dp.mem.read_byte(addr))

            case Opcode.SB:
                addr = dp.alu_exec(AluOp.ADD, rs1_val, imm)
                dp.mem.write_byte(addr, dp.rf.read(inst.rd))

            case Opcode.BEQ | Opcode.BNE | Opcode.BLT | Opcode.BGE | Opcode.BLTU | Opcode.BGEU:
                dp.alu_exec(AluOp.SUB, rs1_val, rs2_val)
                f = dp.flags
                taken = {
                    Opcode.BEQ: f.Z,
                    Opcode.BNE: not f.Z,
                    Opcode.BLT: f.N != f.V,
                    Opcode.BGE: f.N == f.V,
                    Opcode.BLTU: not f.C,
                    Opcode.BGEU: f.C,
                }[inst.opcode]
                if taken:
                    dp.latch_pc(imm)

            case Opcode.J:
                dp.latch_pc(imm)

            case Opcode.CALL:
                dp.rf.write(RA, dp.pc)
                dp.latch_pc(imm)

            case Opcode.RET:
                dp.latch_pc(dp.alu_exec(AluOp.PASS_A, dp.rf.read(RA), 0))

            case Opcode.NOP:
                pass

            case Opcode.HALT:
                raise StopIteration

            case Opcode.EI | Opcode.DI | Opcode.IRET:
                pass  # TODO: прерывания

            case _:
                raise ValueError(f"unknown opcode {inst.opcode}")

        self.tick += 1