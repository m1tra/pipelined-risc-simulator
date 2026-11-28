# модель процессора
from machine.cu import ControlUnit
from machine.datapath import MEM_SIZE, Datapath


class Machine:
    def __init__(
        self,
    ):
        self.dp = Datapath()
        self.cu = ControlUnit(self.dp)
    
    def load_program(
        self,
        program: bytes,
        start: int = 0
    ):
        self.dp.mem.load_bytes(program, start)

        
    def run(self, max_ticks: int = 100_000) -> None:
        for i in range(max_ticks):
            print(i)
            print(self.cu.state)
            print(self.cu.signals)
            

            if self.cu.halted:
                print(self.dp.mem.mem_dump()[0:20])
                print(self.dp.rf.rf_dump())
                return
            
            self.cu.step()
                   
        raise RuntimeError(
            f"Превышен лимит в {max_ticks} тактов"
        ) 
    
