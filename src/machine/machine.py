import logging

from dataclasses import dataclass, field

from machine.cu import ControlUnit
from machine.datapath import Datapath

logger = logging.getLogger(__name__)

@dataclass
class SimulationResult:
    output: str
    ticks: int
    log: list[str] = field(default_factory=list)
    regs: list[int] = field(default_factory=list)
    mem: list[int] = field(default_factory=list)

class Machine:
    def __init__(self) -> None:
        self.dp = Datapath()
        self.cu = ControlUnit(self.dp)

    def load_program(self, program: bytes, start: int = 0) -> None:
        self.dp.mem.load_bytes(program, start)

    def run(self, max_ticks: int = 100_000) -> SimulationResult:
        for _ in range(max_ticks):
            if self.cu.halted:
                break
            self.cu.step()
        else:
            raise RuntimeError(f"limit max = {max_ticks} ticks ")

        mem = self.dp.mem
        result = SimulationResult(
            output="".join(chr(c) for c in mem.output_port),
            ticks=self.cu.tick,
            log=self.cu.compact_log,
            regs=self.dp.rf.regs.copy(),
            mem=mem.memory.copy(),
        )
        logger.info("simulation finished: %d ticks, output: %r", result.ticks, result.output)
        return result