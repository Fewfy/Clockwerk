# Clockwerk 目录结构与接口定义

## 设计目标

目录结构和接口设计遵循三个原则：

- 先支持仿真，再为真机保留扩展位
- 先支持规则决策，再为学习型高层策略预留替换点
- 安全层独立存在，不与普通决策逻辑混写

## 推荐目录结构

```text
clockwerk/
├── README.md
├── docs/
│   ├── development-plan.md
│   └── architecture-and-interfaces.md
├── configs/
│   ├── sim.yaml
│   ├── agent.yaml
│   ├── safety.yaml
│   └── skills.yaml
├── src/
│   └── clockwerk/
│       ├── __init__.py
│       ├── app.py
│       ├── runtime/
│       │   ├── loop.py
│       │   ├── scheduler.py
│       │   └── context.py
│       ├── core/
│       │   ├── types.py
│       │   ├── enums.py
│       │   ├── events.py
│       │   └── result.py
│       ├── perception/
│       │   ├── adapter.py
│       │   ├── estimator.py
│       │   └── fall_detector.py
│       ├── decision/
│       │   ├── agent.py
│       │   ├── state_machine.py
│       │   ├── rules.py
│       │   └── policy.py
│       ├── skills/
│       │   ├── base.py
│       │   ├── stand.py
│       │   ├── move_to_heading.py
│       │   ├── avoid_obstacle.py
│       │   ├── recover.py
│       │   └── stop.py
│       ├── safety/
│       │   ├── supervisor.py
│       │   ├── checks.py
│       │   └── limits.py
│       ├── robot/
│       │   ├── base.py
│       │   ├── sim_adapter.py
│       │   ├── ros2_adapter.py
│       │   └── sdk_adapter.py
│       ├── logging/
│       │   ├── events.py
│       │   ├── recorder.py
│       │   └── dashboard.py
│       └── testing/
│           ├── scenarios.py
│           ├── metrics.py
│           └── replay.py
└── tests/
    ├── test_state_machine.py
    ├── test_safety.py
    ├── test_skills.py
    └── test_robot_adapter.py
```

## 每个目录的职责

### `configs/`

放配置，不放逻辑。

目的：

- 把阈值、频率、技能参数、安全参数从代码里拆出来
- 便于说明系统是可调而不是硬编码

可能遇到的问题：

- 配置项过多，含义重复
- 配置命名不一致，后期难维护

### `runtime/`

放主循环和调度逻辑。

目的：

- 控制系统执行节奏
- 统一处理采样、决策、技能执行和安全检查的顺序

可能遇到的问题：

- 主循环里塞太多业务逻辑
- 不同模块执行频率没有被清晰管理

### `core/`

放系统共用的数据结构、枚举和返回结果。

目的：

- 给模块之间提供稳定的共享语言
- 防止到处传字典，接口越来越乱

可能遇到的问题：

- 类型设计过于复杂
- 各模块绕过类型直接传原始对象

### `perception/`

放传感器适配、状态估计和跌倒检测。

目的：

- 把原始观测整理成高层可消费的结构化状态
- 让高层决策不直接依赖原始传感器细节

可能遇到的问题：

- 状态估计和原始数据边界不清
- 跌倒检测阈值不稳定

### `decision/`

放高层决策逻辑。

目的：

- 负责从结构化状态中选择当前高层状态和目标技能
- 为规则版和学习版提供统一挂载点

可能遇到的问题：

- 状态机和策略逻辑混写
- 规则版和学习版接口不统一

### `skills/`

放技能封装。

目的：

- 把低层动作组织成可进入、可退出、可超时的技能
- 让高层只调技能，不直接调底层控制命令

可能遇到的问题：

- 技能粒度过大
- 技能没有显式退出条件

### `safety/`

放安全检查和保护逻辑。

目的：

- 独立实现急停、姿态限制、障碍保护、命令超时等能力
- 确保任何普通决策都能被安全层覆盖

可能遇到的问题：

- 安全策略散落在多个模块
- 保护规则和业务决策互相冲突

### `robot/`

放仿真和真机的统一适配层。

目的：

- 屏蔽 Isaac Lab、ROS2、SDK2 等平台差异
- 支持后续替换部署目标

可能遇到的问题：

- 不同平台的控制语义并不完全一致
- 时间戳、坐标系、控制频率容易混乱

### `logging/`

放事件记录和调试面板。

目的：

- 保证系统可观测
- 为失败分析和回归定位提供依据

可能遇到的问题：

- 只记结果，不记原因
- 日志太多，抓不到关键切换点

### `testing/`

放测试场景和指标工具。

目的：

- 固定回归验证方式
- 支持场景复现和失败重放

可能遇到的问题：

- 场景和指标定义不稳定
- 测试不能覆盖异常路径

## 核心数据结构建议

下面的接口定义偏 Python 风格，但重点是职责，不是语法细节。

### `RobotObservation`

```python
from dataclasses import dataclass


@dataclass
class RobotObservation:
    timestamp: float
    linear_velocity: tuple[float, float, float]
    angular_velocity: tuple[float, float, float]
    body_rpy: tuple[float, float, float]
    obstacle_distance: float | None
    is_fallen: bool
    command_alive: bool
    current_skill: str | None
```

目的：

- 统一高层可见观测
- 让决策层只依赖结构化状态

可能遇到的问题：

- 观测字段越来越多，最后变成原始传感器转储
- `None` 和异常值处理不统一

### `NavigationGoal`

```python
from dataclasses import dataclass


@dataclass
class NavigationGoal:
    target_heading: float | None
    target_position: tuple[float, float] | None
    max_speed: float
```

目的：

- 给高层任务输入一个稳定表示
- 同时支持“朝某个方向走”和“去某个点”

可能遇到的问题：

- 同时给 heading 和 position，但优先级没定义
- 坐标系约定不一致

### `DecisionContext`

```python
from dataclasses import dataclass


@dataclass
class DecisionContext:
    observation: RobotObservation
    goal: NavigationGoal | None
    active_state: str
    active_skill: str | None
```

目的：

- 给高层决策一个完整上下文
- 避免 agent 去主动拉取多个模块状态

可能遇到的问题：

- context 过大，变成万能对象
- active state 和 active skill 语义重叠

### `DecisionOutput`

```python
from dataclasses import dataclass


@dataclass
class DecisionOutput:
    next_state: str
    requested_skill: str
    reason: str
```

目的：

- 不只输出“做什么”，还输出“为什么”
- 方便日志记录和问题复盘

可能遇到的问题：

- `reason` 写得太随意，失去调试价值
- 状态和技能不一致

### `SafetyEvent`

```python
from dataclasses import dataclass


@dataclass
class SafetyEvent:
    triggered: bool
    level: str
    code: str
    message: str
```

目的：

- 给安全层一个标准输出
- 让 runtime 可以统一处理保护逻辑

可能遇到的问题：

- 等级定义不清晰
- 触发后缺少解除条件

## 核心接口定义

### `RobotAdapter`

```python
from typing import Protocol


class RobotAdapter(Protocol):
    def connect(self) -> None: ...
    def disconnect(self) -> None: ...
    def get_observation(self) -> RobotObservation: ...
    def send_velocity_command(self, vx: float, vy: float, wz: float) -> None: ...
    def send_skill_command(self, skill_name: str, params: dict | None = None) -> None: ...
    def emergency_stop(self) -> None: ...
    def reset(self) -> None: ...
```

目的：

- 把平台差异封装在同一个边界后面
- 支持仿真版和真机版共用上层逻辑

可能遇到的问题：

- `send_velocity_command()` 和 `send_skill_command()` 语义冲突
- `reset()` 在仿真和真机上的含义不一致

### `PerceptionAdapter`

```python
from typing import Protocol


class PerceptionAdapter(Protocol):
    def update(self, raw_observation: RobotObservation) -> RobotObservation: ...
```

目的：

- 对原始观测做轻量整理和归一化
- 让上层拿到稳定格式

可能遇到的问题：

- 命名叫 adapter，但实际做了太多状态估计逻辑

### `StateEstimator`

```python
from typing import Protocol


class StateEstimator(Protocol):
    def estimate(self, observation: RobotObservation) -> RobotObservation: ...
```

目的：

- 把姿态判定、跌倒判定等推断逻辑显式独立出来

可能遇到的问题：

- 估计器直接改写原始观测字段，语义不清

### `DecisionAgent`

```python
from typing import Protocol


class DecisionAgent(Protocol):
    def decide(self, context: DecisionContext) -> DecisionOutput: ...
```

目的：

- 给规则决策和更复杂的策略实现提供统一入口

可能遇到的问题：

- 规则版输出技能，学习版输出动作，接口失配

### `Skill`

```python
from typing import Protocol


class Skill(Protocol):
    name: str

    def can_enter(self, context: DecisionContext) -> bool: ...
    def on_enter(self, context: DecisionContext) -> None: ...
    def step(self, context: DecisionContext, robot: RobotAdapter) -> None: ...
    def should_exit(self, context: DecisionContext) -> bool: ...
    def on_exit(self, context: DecisionContext) -> None: ...
```

目的：

- 标准化技能生命周期
- 让 runtime 能统一调度不同技能

可能遇到的问题：

- `step()` 里掺入状态切换逻辑
- `should_exit()` 只考虑成功，不考虑超时和失败

### `SafetySupervisor`

```python
from typing import Protocol


class SafetySupervisor(Protocol):
    def evaluate(self, context: DecisionContext) -> SafetyEvent | None: ...
```

目的：

- 让安全检查和普通决策彻底解耦

可能遇到的问题：

- 一个周期触发多个保护，但没有优先级

## 运行时主循环建议

建议主循环顺序固定为：

1. 从 `RobotAdapter` 获取观测
2. 经过 `PerceptionAdapter` 和 `StateEstimator`
3. 构造 `DecisionContext`
4. 先执行 `SafetySupervisor`
5. 若安全通过，再执行 `DecisionAgent`
6. 将输出映射到技能层
7. 执行当前技能
8. 记录日志和关键事件

目的：

- 保证安全检查总是先于普通决策
- 保证每个周期的顺序固定，便于调试

可能遇到的问题：

- 技能执行时间过长，拖慢主循环
- 日志写入阻塞实时控制

## 最小实现优先级

如果要快速起步，建议先只实现这些文件：

- `src/clockwerk/app.py`
- `src/clockwerk/core/types.py`
- `src/clockwerk/decision/state_machine.py`
- `src/clockwerk/skills/base.py`
- `src/clockwerk/skills/stand.py`
- `src/clockwerk/skills/move_to_heading.py`
- `src/clockwerk/skills/recover.py`
- `src/clockwerk/skills/stop.py`
- `src/clockwerk/safety/supervisor.py`
- `src/clockwerk/robot/base.py`
- `src/clockwerk/robot/sim_adapter.py`

目的：

- 优先做出一个能运行的最小闭环
- 把复杂模块延后，不在第一阶段过度设计

可能遇到的问题：

- 过早把所有目录都实现一遍
- 为未来需求写太多空壳代码

## 后续扩展方向

- 在 `decision/policy.py` 中接入学习型高层策略
- 在 `robot/ros2_adapter.py` 中接入 ROS2 topic 和 service
- 在 `robot/sdk_adapter.py` 中对接 Unitree SDK2
- 在 `testing/replay.py` 中加入失败回放
- 在 `logging/dashboard.py` 中加入在线状态面板

目的：

- 让系统从学习项目逐步成长为可演示的工程原型

可能遇到的问题：

- 过早对接真机，调试复杂度陡增
- 没有先把仿真链路跑稳，就开始扩展能力
