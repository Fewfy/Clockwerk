from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

from mock_quadruped_sim import MockQuadrupedSim
from mock_quadruped_sim import VelocityCommand


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch Clockwerk simulation backend.")
    parser.add_argument(
        "--config",
        default=str(Path(__file__).resolve().parents[2] / "configs" / "sim.yaml"),
        help="Path to the simulation config YAML.",
    )
    return parser.parse_args()


def load_config(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def run_mock_backend(config: dict[str, Any]) -> Path:
    env = MockQuadrupedSim(
        control_dt=float(config["control_dt"]),
        obstacle_positions=[float(value) for value in config["obstacle_positions"]],
        obstacle_threshold=float(config["obstacle_threshold"]),
        fall_pitch_threshold=float(config["fall_pitch_threshold"]),
        fall_reset_pitch=float(config.get("fall_reset_pitch", 0.0)),
    )

    log_path = Path(config["log_path"])
    log_path.parent.mkdir(parents=True, exist_ok=True)

    with log_path.open("w", encoding="utf-8") as handle:
        observation = env.reset()
        env.write_log_record(
            handle,
            command=VelocityCommand(),
            observation=observation,
            event="reset",
        )

        command = VelocityCommand(
            linear_x=float(config.get("default_goal_speed", 0.4)),
            yaw_rate=float(config.get("default_goal_heading", 0.0)),
        )

        max_steps = int(config["max_steps"])
        for _ in range(max_steps):
            observation = env.step(command)
            env.write_log_record(
                handle,
                command=command,
                observation=observation,
                event="step",
            )

            if observation.obstacle_distance is not None and observation.obstacle_distance <= float(config["obstacle_threshold"]):
                break

        observation = env.inject_fall(float(config["fall_pitch_threshold"]) + 0.1)
        env.write_log_record(
            handle,
            command=VelocityCommand(),
            observation=observation,
            event="fall",
        )

        observation = env.reset()
        env.write_log_record(
            handle,
            command=VelocityCommand(),
            observation=observation,
            event="post_fall_reset",
        )

    return log_path


def main() -> int:
    args = parse_args()
    config = load_config(args.config)
    backend = config.get("backend", "mock")

    if backend == "isaaclab":
        raise NotImplementedError(
            "Isaac Lab backend is not wired yet. Use backend=mock for the current repeatable validation loop."
        )

    log_path = run_mock_backend(config)
    print(f"mock simulation completed, log written to {log_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
