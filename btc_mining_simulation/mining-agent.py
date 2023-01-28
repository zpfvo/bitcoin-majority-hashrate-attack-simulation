import argparse
import hashlib
import time
import sys
from random import randbytes
from btc_mining_simulation.models import BlockFoundEvent, Statistics, StatisticsEvent

DEFAULT_HASH_THRESHOLD = "00AFFFFF"
DEFAULT_HASH_TRHESHOLD_INT = int(DEFAULT_HASH_THRESHOLD, 16)

parser = argparse.ArgumentParser(prog="BTC Mining Simulation Agent")

parser.add_argument(
    "-n", "--name", help="Mining Agent Name (logging prefix)", default=""
)
parser.add_argument(
    "-hr", "--hashrate", help="Hashrate per second", default=400, type=float
)
parser.add_argument(
    "-thr",
    "--hash-threshold",
    default=DEFAULT_HASH_THRESHOLD,
    type=str,
    help="Threshold the the sh256-hash needs to be below of to find a block. (4 Bytes hex. Example: '00FFFFFF')",
)


class MiningAgent:
    def __init__(
        self, hash_rate: int, name: str = "", hash_threshold: int = DEFAULT_HASH_TRHESHOLD_INT
    ) -> None:
        self.running = False
        self.hash_count = 0
        self.block_count = 0
        self.hash_rate = hash_rate
        self.hash_interval = 1 / self.hash_rate
        self.name = name
        self.hash_threshold = hash_threshold
        self.program_start_time = time.monotonic()

    def run(self) -> None:
        statistics_interval_time = self.program_start_time
        current_statistics_hash_count = 0
        hash_interval_time = self.program_start_time
        time_error = 0
        while self.running:
            current_time = time.monotonic()
            time_delta = current_time - hash_interval_time
            if time_delta + time_error >= self.hash_interval:
                time_error = time_error + ((time_delta - self.hash_interval) * 1)
                hash_interval_time = current_time
                digest = int.from_bytes(
                    hashlib.sha256(randbytes(4)).digest()[:4], "big"
                )
                self.hash_count += 1
                if digest < self.hash_threshold:
                    self.block_count += 1
                    event = BlockFoundEvent(source=self.name)
                    print(event.json())

                # try:
                #     time.sleep(self.hash_interval - time_error * 10)
                # except Exception:
                #     pass
            if current_time - statistics_interval_time >= 1:
                current_statistics_hash_count = (
                    self.hash_count - current_statistics_hash_count
                )
                statistics_interval_time = current_time
                time_elapsed = current_time - self.program_start_time
                event = StatisticsEvent(
                    source=self.name,
                    payload=Statistics(
                        hashrate_s=current_statistics_hash_count / 1,
                        blocks_s=self.block_count / time_elapsed,
                        time_error=time_error,
                        block_count=self.block_count,
                    ),
                )
                current_statistics_hash_count = self.hash_count
                print(event.json())


if __name__ == "__main__":
    args = parser.parse_args()
    name = args.name
    hashrate = args.hashrate
    hash_threshold = int(args.hash_threshold, 16)
    print(
        f"Starting mining agent {name} with hashrate {hashrate}/s and hash threshold {hash_threshold:08X}. Waiting for START signal..."
    )
    ma = MiningAgent(hashrate, name=args.name, hash_threshold=hash_threshold)
    while ma.running == False:
        for line in sys.stdin:
            print(line)
            if 'START' in line:
                print()
                ma.running = True
                ma.program_start_time = time.monotonic()
                break
    try:
        ma.run()
    except KeyboardInterrupt:
        ma.running = False


    