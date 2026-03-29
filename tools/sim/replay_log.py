from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from mock_quadruped_sim import load_log


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Replay and summarize Clockwerk simulation logs.")
    parser.add_argument("log_path", help="Path to the JSONL simulation log.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    log_path = Path(args.log_path)
    records = load_log(log_path)
    events = Counter(record["event"] for record in records)
    last_observation = records[-1]["observation"] if records else {}

    print(f"records={len(records)}")
    print(f"events={dict(events)}")
    print(f"final_position_x={last_observation.get('position_x')}")
    print(f"final_is_fallen={last_observation.get('is_fallen')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
