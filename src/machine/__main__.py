from pathlib import Path
from machine.machine import Machine

def main():
    m = Machine()
    m.load_program(Path("out/out.bin").read_bytes())
    m.run()

if __name__ == "__main__":
    main()