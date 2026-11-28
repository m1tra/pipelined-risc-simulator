import argparse
import logging
from pathlib import Path

from machine.machine import Machine

def main() -> None:
    parser = argparse.ArgumentParser(description="cpu model")
    parser.add_argument("binary", type=Path, help="code (.bin)")
    parser.add_argument("--log", type=Path, default=None, help="journal")
    args = parser.parse_args()

    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if args.log:
        handlers.append(logging.FileHandler(args.log, mode="w", encoding="utf-8"))
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(message)s",
        handlers=handlers,
        force=True,
    )

    m = Machine()
    m.load_program(args.binary.read_bytes())
    result = m.run()

    print("output:", repr(result.output))
    print("ticks:", result.ticks)
    print("--- compact log ---")
    print("\n".join(result.log))

if __name__ == "__main__":
    main()