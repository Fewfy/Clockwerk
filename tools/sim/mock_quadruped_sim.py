from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
import json
from pathlib import Path
from typing import TextIO


@dataclass
class VelocityCommand:
    linear_x: float = 0.0
    yaw_rate: float = 0.0


@dataclass
class SimObservation:
    step: int
    timestamp_sec: float
    position_x: float
    heading_rad: float
    linear_velocity_x: float
    obstacle_distance: float | None
    is_fallen: bool


class MockQuadrupedSim:
    """A deterministic fallback environment for decision-loop validation."""

    def __init__(
        self,
        *,
        control_dt: float,
        obstacle_positions: list[float],
        obstacle_threshold: float,
        fall_pitch_threshold: float,
        fall_reset_pitch: float = 0.0,
    ) -> None:
        self.control_dt = control_dt
        self.obstacle_positions = sorted(obstacle_positions)
        self.obstacle_threshold = obstacle_threshold
        self.fall_pitch_threshold = fall_pitch_threshold
        self.fall_reset_pitch = fall_reset_pitch
        self.reset()

    def reset(self) -> SimObservation:
        self.step_count = 0
        self.timestamp_sec = 0.0
        self.position_x = 0.0
        self.heading_rad = 0.0
        self.body_pitch = self.fall_reset_pitch
        self.linear_velocity_x = 0.0
        self.is_fallen = False
        return self.get_observation()

    def get_observation(self) -> SimObservation:
        return SimObservation(
            step=self.step_count,
            timestamp_sec=self.timestamp_sec,
            position_x=self.position_x,
            heading_rad=self.heading_rad,
            linear_velocity_x=self.linear_velocity_x,
            obstacle_distance=self._nearest_obstacle_distance(),
            is_fallen=self.is_fallen,
        )

    def step(self, command: VelocityCommand) -> SimObservation:
        if self.is_fallen:
            self.linear_velocity_x = 0.0
            self.timestamp_sec += self.control_dt
            self.step_count += 1
            return self.get_observation()

        obstacle_distance = self._nearest_obstacle_distance()
        if obstacle_distance is not None and obstacle_distance <= self.obstacle_threshold:
            self.linear_velocity_x = 0.0
        else:
            self.linear_velocity_x = max(min(command.linear_x, 1.0), -1.0)
            self.position_x += self.linear_velocity_x * self.control_dt

        self.heading_rad += command.yaw_rate * self.control_dt
        self.timestamp_sec += self.control_dt
        self.step_count += 1
        self.is_fallen = abs(self.body_pitch) >= self.fall_pitch_threshold
        return self.get_observation()

    def inject_fall(self, pitch_rad: float) -> SimObservation:
        self.body_pitch = pitch_rad
        self.is_fallen = abs(self.body_pitch) >= self.fall_pitch_threshold
        return self.get_observation()

    def write_log_record(
        self,
        stream: TextIO,
        *,
        command: VelocityCommand,
        observation: SimObservation,
        event: str,
    ) -> None:
        record = {
            "event": event,
            "command": asdict(command),
            "observation": asdict(observation),
        }
        stream.write(json.dumps(record, ensure_ascii=True) + "\n")

    def _nearest_obstacle_distance(self) -> float | None:
        candidates = [position - self.position_x for position in self.obstacle_positions if position >= self.position_x]
        if not candidates:
            return None
        return min(candidates)


def load_log(path: str | Path) -> list[dict]:
    records: list[dict] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            records.append(json.loads(line))
    return records
