import argparse
import asyncio
import os
from btc_mining_simulation.models import Event, BlockFoundEvent
from pydantic import parse_obj_as
import json
from btc_mining_simulation import __version__

DEFAULT_DIFFICULTY = "00AFFFFF"
MAX_BLOCK_BAR_SIZE = 80

parser = argparse.ArgumentParser(prog="BTC Mining Simulation Controller")

parser.add_argument(
    "-mhr",
    "--majority-hashrate-percent",
    help="How big is the fraction of the majority hashrate? Default '0.51' equates to 51 percent",
    default=0.51,
    type=float,
)
parser.add_argument(
    "-hr",
    "--hashrate",
    help="Total hashrate per s. Default 1000",
    default=1000,
    type=int,
)
parser.add_argument(
    "-thr",
    "--hash-threshold",
    default=DEFAULT_DIFFICULTY,
    type=str,
    help=f"Max hash value in HEX (4 Bytes). Default '{DEFAULT_DIFFICULTY}'",
)






class MiningController:
    def __init__(
        self, majority_hashrate_percent: float, total_hashrate: int, hash_threshold: str
    ) -> None:
        self.majority_hashrate_percent = majority_hashrate_percent
        self.total_hashrate = total_hashrate
        self.hash_threshold = hash_threshold
        self.process_handles: dict[str, asyncio.subprocess.Process] = {}

        self.majority_hashrate = total_hashrate * majority_hashrate_percent
        self.minority_hashrate = total_hashrate - self.majority_hashrate
        print(f"MiningController {__version__}")
        print(
            f"Total Hashrate {self.total_hashrate}/s Majority {self.majority_hashrate}/s Minority {self.minority_hashrate}/s"
        )

        self.majority_statistics = None
        self.minority_statistics = None
        self.majority_block_count = 0
        self.minority_block_count = 0

    async def read_subprocess_stdout(self, proc: asyncio.subprocess.Process):
        while proc.returncode is None:
            line = await proc.stdout.readline()
            line = line.decode().strip()
            try:
                event = parse_obj_as(Event, json.loads(line))
            except Exception:
                if line:
                    print(f"{line}")
                continue

            match (event):
                case BlockFoundEvent:
                    if event.source == "majority":
                        self.majority_block_count += 1
                    if event.source == "minority":
                        self.minority_block_count += 1
            
            print("\033[2A", end="") # Move Up 2 lines
            print("\033[J", end="") # Clear till end of screen
            padding = max(max(self.majority_block_count, self.minority_block_count) - MAX_BLOCK_BAR_SIZE, 0)
            print(f"Majority {self.majority_block_count:3d}: " + "#" * (self.majority_block_count - padding))
            print(f"Minority {self.minority_block_count:3d}: " + "#" * (self.minority_block_count - padding))

    async def start_minig_agent(self, name: str, hashrate: float):
        proc = await asyncio.create_subprocess_exec(
            "poetry",
            "run",
            "python",
            "btc_mining_simulation/mining-agent.py",
            "-n",
            f"{name}",
            "-hr",
            f"{hashrate}",
            "-thr",
            self.hash_threshold,
            stdout=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
            env={"PYTHONUNBUFFERED": "1"},
        )
        self.process_handles[name] = proc
        await self.read_subprocess_stdout(proc)

    async def send_start_to_mining_agents(self):
        await asyncio.sleep(3)
        print('Starting simulation now.')
        for name, proc in self.process_handles.items():
            proc.stdin.write('START\n'.encode())

    async def run(self):
        print("Spinning up Mining Agents")
        majority_agent_task = asyncio.create_task(
            self.start_minig_agent("majority", self.majority_hashrate)
        )
        minority_agent_task = asyncio.create_task(
            self.start_minig_agent("minority", self.minority_hashrate)
        )
        send_start_to_mining_agents_task = asyncio.create_task(self.send_start_to_mining_agents())
        await asyncio.gather(majority_agent_task, minority_agent_task, send_start_to_mining_agents_task)


if __name__ == "__main__":
    args = parser.parse_args()
    mc = MiningController(
        args.majority_hashrate_percent, args.hashrate, args.hash_threshold
    )
    try:
        asyncio.run(mc.run())
    except KeyboardInterrupt:
        pass
