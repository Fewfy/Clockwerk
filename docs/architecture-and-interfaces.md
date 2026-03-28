# Clockwerk 目录结构与接口定义

## 设计目标

目录结构和接口设计遵循三个原则：

- 先支持仿真，再为真机保留扩展位
- 先支持规则决策，再为学习型高层策略预留替换点
- 安全层独立存在，不与普通决策逻辑混写
- 在线链路以 `C++` 为主，仿真训练和离线工具保留 `Python`

## 技术栈建议

在线系统：

- `C++17` 或 `C++20`
- `CMake`
- `ROS2`
- `Unitree SDK2`
- `yaml-cpp`
- `gtest`

仿真和训练：

- `Python`
- `Isaac Lab`
- `PyTorch`
- `pytest`

这样拆分的目的：

- 把性能敏感、时序敏感、部署敏感的模块放在 `C++`
- 把训练、评估、实验工具保留在更高效的 `Python` 环境

## 推荐目录结构

```text
clockwerk/
├── README.md
├── docs/
│   ├── development-plan.md
│   └── architecture-and-interfaces.md
├── CMakeLists.txt
├── configs/
│   ├── sim.yaml
│   ├── agent.yaml
│   ├── safety.yaml
│   └── skills.yaml
├── include/
│   └── clockwerk/
│       ├── core/
│       │   ├── types.hpp
│       │   ├── enums.hpp
│       │   ├── events.hpp
│       │   └── result.hpp
│       ├── runtime/
│       │   ├── loop.hpp
│       │   ├── scheduler.hpp
│       │   └── context.hpp
│       ├── perception/
│       │   ├── adapter.hpp
│       │   ├── estimator.hpp
│       │   └── fall_detector.hpp
│       ├── decision/
│       │   ├── agent.hpp
│       │   ├── state_machine.hpp
│       │   ├── rules.hpp
│       │   └── policy.hpp
│       ├── skills/
│       │   ├── skill.hpp
│       │   ├── stand_skill.hpp
│       │   ├── move_to_heading_skill.hpp
│       │   ├── avoid_obstacle_skill.hpp
│       │   ├── recover_skill.hpp
│       │   └── stop_skill.hpp
│       ├── safety/
│       │   ├── supervisor.hpp
│       │   ├── checks.hpp
│       │   └── limits.hpp
│       ├── robot/
│       │   ├── robot_adapter.hpp
│       │   ├── ros2_adapter.hpp
│       │   ├── sdk_adapter.hpp
│       │   └── sim_bridge_adapter.hpp
│       └── logging/
│           ├── events.hpp
│           ├── recorder.hpp
│           └── dashboard.hpp
├── src/
│   ├── app.cpp
│   ├── runtime/
│   ├── perception/
│   ├── decision/
│   ├── skills/
│   ├── safety/
│   ├── robot/
│   └── logging/
├── tools/
│   ├── train/
│   │   ├── train_policy.py
│   │   └── export_policy.py
│   ├── sim/
│   │   ├── launch_isaaclab.py
│   │   └── replay_log.py
│   └── analysis/
│       ├── evaluate_runs.py
│       └── plot_metrics.py
└── tests/
    ├── cpp/
    │   ├── test_state_machine.cpp
    │   ├── test_safety.cpp
    │   ├── test_skills.cpp
    │   └── test_robot_adapter.cpp
    └── python/
        ├── test_training_pipeline.py
        └── test_log_replay.py
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
- `C++` 和 `Python` 读取同一份配置时字段定义不一致

### `runtime/`

放主循环和调度逻辑。

目的：

- 控制系统执行节奏
- 统一处理采样、决策、技能执行和安全检查的顺序

可能遇到的问题：

- 主循环里塞太多业务逻辑
- 不同模块执行频率没有被清晰管理
- `ROS2 callback` 和主控制循环之间的线程关系不清楚

### `core/`

放系统共用的数据结构、枚举和返回结果。

目的：

- 给模块之间提供稳定的共享语言
- 防止到处传字典，接口越来越乱

可能遇到的问题：

- 类型设计过于复杂
- 各模块绕过类型直接传原始对象
- 内部结构体和 `ROS2 message` 重复定义

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
- 在线 `C++` 策略和离线 `Python` 策略输入语义不一致

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
- `ROS2`、SDK 和仿真桥接层的异常处理风格不一致

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
- `C++` 单测和 `Python` 仿真回归测试之间缺少共享用例

## 核心数据结构建议

下面的接口定义偏 `C++` 风格，但重点是职责，不是语法细节。

### `RobotObservation`

```cpp
struct Vec3 {
    double x;
    double y;
    double z;
};

struct RobotObservation {
    double timestamp_sec;
    Vec3 linear_velocity;
    Vec3 angular_velocity;
    Vec3 body_rpy;
    std::optional<double> obstacle_distance;
    bool is_fallen;
    bool command_alive;
    std::optional<std::string> current_skill;
};
```

目的：

- 统一高层可见观测
- 让决策层只依赖结构化状态

可能遇到的问题：

- 观测字段越来越多，最后变成原始传感器转储
- `None` 和异常值处理不统一

### `NavigationGoal`

```cpp
struct Vec2 {
    double x;
    double y;
};

struct NavigationGoal {
    std::optional<double> target_heading;
    std::optional<Vec2> target_position;
    double max_speed;
};
```

目的：

- 给高层任务输入一个稳定表示
- 同时支持“朝某个方向走”和“去某个点”

可能遇到的问题：

- 同时给 heading 和 position，但优先级没定义
- 坐标系约定不一致

### `DecisionContext`

```cpp
struct DecisionContext {
    RobotObservation observation;
    std::optional<NavigationGoal> goal;
    std::string active_state;
    std::optional<std::string> active_skill;
};
```

目的：

- 给高层决策一个完整上下文
- 避免 agent 去主动拉取多个模块状态

可能遇到的问题：

- context 过大，变成万能对象
- active state 和 active skill 语义重叠

### `DecisionOutput`

```cpp
struct DecisionOutput {
    std::string next_state;
    std::string requested_skill;
    std::string reason;
};
```

目的：

- 不只输出“做什么”，还输出“为什么”
- 方便日志记录和问题复盘

可能遇到的问题：

- `reason` 写得太随意，失去调试价值
- 状态和技能不一致

### `SafetyEvent`

```cpp
struct SafetyEvent {
    bool triggered;
    std::string level;
    std::string code;
    std::string message;
};
```

目的：

- 给安全层一个标准输出
- 让 runtime 可以统一处理保护逻辑

可能遇到的问题：

- 等级定义不清晰
- 触发后缺少解除条件

## 核心接口定义

### `RobotAdapter`

```cpp
class RobotAdapter {
public:
    virtual ~RobotAdapter() = default;
    virtual void Connect() = 0;
    virtual void Disconnect() = 0;
    virtual RobotObservation GetObservation() = 0;
    virtual void SendVelocityCommand(double vx, double vy, double wz) = 0;
    virtual void SendSkillCommand(const std::string& skill_name) = 0;
    virtual void EmergencyStop() = 0;
    virtual void Reset() = 0;
};
```

目的：

- 把平台差异封装在同一个边界后面
- 支持仿真版和真机版共用上层逻辑

可能遇到的问题：

- `send_velocity_command()` 和 `send_skill_command()` 语义冲突
- `reset()` 在仿真和真机上的含义不一致

### `PerceptionAdapter`

```cpp
class PerceptionAdapter {
public:
    virtual ~PerceptionAdapter() = default;
    virtual RobotObservation Update(const RobotObservation& raw_observation) = 0;
};
```

目的：

- 对原始观测做轻量整理和归一化
- 让上层拿到稳定格式

可能遇到的问题：

- 命名叫 adapter，但实际做了太多状态估计逻辑

### `StateEstimator`

```cpp
class StateEstimator {
public:
    virtual ~StateEstimator() = default;
    virtual RobotObservation Estimate(const RobotObservation& observation) = 0;
};
```

目的：

- 把姿态判定、跌倒判定等推断逻辑显式独立出来

可能遇到的问题：

- 估计器直接改写原始观测字段，语义不清

### `DecisionAgent`

```cpp
class DecisionAgent {
public:
    virtual ~DecisionAgent() = default;
    virtual DecisionOutput Decide(const DecisionContext& context) = 0;
};
```

目的：

- 给规则决策和更复杂的策略实现提供统一入口

可能遇到的问题：

- 规则版输出技能，学习版输出动作，接口失配

### `Skill`

```cpp
class Skill {
public:
    virtual ~Skill() = default;
    virtual std::string Name() const = 0;
    virtual bool CanEnter(const DecisionContext& context) const = 0;
    virtual void OnEnter(const DecisionContext& context) = 0;
    virtual void Step(const DecisionContext& context, RobotAdapter& robot) = 0;
    virtual bool ShouldExit(const DecisionContext& context) const = 0;
    virtual void OnExit(const DecisionContext& context) = 0;
};
```

目的：

- 标准化技能生命周期
- 让 runtime 能统一调度不同技能

可能遇到的问题：

- `step()` 里掺入状态切换逻辑
- `should_exit()` 只考虑成功，不考虑超时和失败

### `SafetySupervisor`

```cpp
class SafetySupervisor {
public:
    virtual ~SafetySupervisor() = default;
    virtual std::optional<SafetyEvent> Evaluate(const DecisionContext& context) = 0;
};
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

- `CMakeLists.txt`
- `include/clockwerk/core/types.hpp`
- `include/clockwerk/decision/state_machine.hpp`
- `include/clockwerk/skills/skill.hpp`
- `include/clockwerk/safety/supervisor.hpp`
- `include/clockwerk/robot/robot_adapter.hpp`
- `src/app.cpp`
- `src/decision/state_machine.cpp`
- `src/skills/stand_skill.cpp`
- `src/skills/move_to_heading_skill.cpp`
- `src/skills/recover_skill.cpp`
- `src/skills/stop_skill.cpp`
- `src/safety/supervisor.cpp`
- `src/robot/sim_bridge_adapter.cpp`

目的：

- 优先做出一个能运行的最小闭环
- 把复杂模块延后，不在第一阶段过度设计

可能遇到的问题：

- 过早把所有目录都实现一遍
- 为未来需求写太多空壳代码

## 后续扩展方向

- 在 `decision/policy.hpp` 和 `src/decision/policy.cpp` 中接入更复杂的高层策略
- 在 `robot/ros2_adapter.hpp` 和 `src/robot/ros2_adapter.cpp` 中接入 `ROS2 topic` 和 `service`
- 在 `robot/sdk_adapter.hpp` 和 `src/robot/sdk_adapter.cpp` 中对接 `Unitree SDK2`
- 在 `tools/sim/replay_log.py` 中加入失败回放
- 在 `logging/dashboard.hpp` 和 `src/logging/dashboard.cpp` 中加入在线状态面板

目的：

- 让系统从学习项目逐步成长为可演示的工程原型

可能遇到的问题：

- 过早对接真机，调试复杂度陡增
- 没有先把仿真链路跑稳，就开始扩展能力
