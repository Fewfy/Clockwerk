from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SIM_DIR = REPO_ROOT / "tools" / "sim"
if str(SIM_DIR) not in sys.path:
    sys.path.insert(0, str(SIM_DIR))

from mock_quadruped_sim import MockQuadrupedSim
from mock_quadruped_sim import VelocityCommand
from mock_quadruped_sim import load_log


class MockQuadrupedSimTest(unittest.TestCase):
    def test_walks_on_flat_ground_until_obstacle(self) -> None:
        env = MockQuadrupedSim(
            control_dt=0.1,
            obstacle_positions=[1.0],
            obstacle_threshold=0.2,
            fall_pitch_threshold=1.0,
        )

        for _ in range(20):
            observation = env.step(VelocityCommand(linear_x=0.5))

        self.assertGreater(observation.position_x, 0.0)
        self.assertLessEqual(observation.obstacle_distance, 0.2)
        self.assertEqual(observation.linear_velocity_x, 0.0)

    def test_fall_can_be_detected_and_reset(self) -> None:
        env = MockQuadrupedSim(
            control_dt=0.1,
            obstacle_positions=[],
            obstacle_threshold=0.2,
            fall_pitch_threshold=1.0,
        )

        fallen = env.inject_fall(1.2)
        self.assertTrue(fallen.is_fallen)

        recovered = env.reset()
        self.assertFalse(recovered.is_fallen)
        self.assertEqual(recovered.position_x, 0.0)

    def test_launcher_and_replay_scripts_work_together(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "sim.jsonl"
            config_path = Path(tmpdir) / "sim.yaml"
            config_path.write_text(
                "\n".join(
                    [
                        "backend: mock",
                        "control_dt: 0.1",
                        "max_steps: 20",
                        "obstacle_positions:",
                        "  - 1.0",
                        "obstacle_threshold: 0.2",
                        "fall_pitch_threshold: 1.0",
                        "fall_reset_pitch: 0.0",
                        "default_goal_heading: 0.0",
                        "default_goal_speed: 0.5",
                        f"log_path: {log_path}",
                    ]
                ),
                encoding="utf-8",
            )

            launch = subprocess.run(
                [sys.executable, str(SIM_DIR / "launch_isaaclab.py"), "--config", str(config_path)],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("mock simulation completed", launch.stdout)

            records = load_log(log_path)
            self.assertGreaterEqual(len(records), 3)

            replay = subprocess.run(
                [sys.executable, str(SIM_DIR / "replay_log.py"), str(log_path)],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("records=", replay.stdout)
            self.assertIn("events=", replay.stdout)


if __name__ == "__main__":
    unittest.main()
