import argparse
import json
from pathlib import Path
from typing import Any

from .detector import Detector
from .enums import Mode, Server, Tool
from .report import render

def _load(scenario: str) -> list[dict[str, Any]]:
    path = Path("recordings") / f"{scenario}.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

def demo(scenario: str, mode: Mode) -> str:
    detector = Detector(mode)
    for record in _load(scenario):
        call = detector.feed(Server(record["server"]), Tool(record["tool"]), record["args"], record["result"])
        if call.is_egress:
            detector.blocks(call)
    return render(detector)

def main() -> None:
    parser = argparse.ArgumentParser(prog="cyclops")
    sub = parser.add_subparsers(dest="command", required=True)
    demo_cmd = sub.add_parser("demo")
    demo_cmd.add_argument("--scenario", default="poisoned")
    demo_cmd.add_argument("--mode", type=Mode, choices=list(Mode), default=Mode.DETECT)
    attack_cmd = sub.add_parser("attack")
    attack_cmd.add_argument("--mode", type=Mode, choices=list(Mode), default=Mode.PREVENT)
    attack_cmd.add_argument("--scenario", default="poisoned")
    args = parser.parse_args()
    if args.command == "demo":
        print(demo(args.scenario, args.mode))
    elif args.command == "attack":
        from .redteam import main as attack_main
        attack_main(args.mode, args.scenario)

if __name__ == "__main__":
    main()
