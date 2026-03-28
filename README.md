# Clockwerk

机器狗高层决策系统的项目骨架

文档入口：

- [开发计划](/home/yaof/dev/Clockwerk/docs/development-plan.md)
- [项目范围说明](/home/yaof/dev/Clockwerk/docs/project-scope.md)
- [目录结构与接口定义](/home/yaof/dev/Clockwerk/docs/architecture-and-interfaces.md)

推荐技术路线：

- 在线决策与机器人接入使用 `C++`
- 仿真训练、数据分析和实验工具使用 `Python`

参考与借鉴项目：

- `unitreerobotics/unitree_rl_lab`
  借鉴四足机器人在 Isaac Lab 中的训练与部署链路
- `unitreerobotics/unitree_sim_isaaclab`
  借鉴 Unitree 机器狗在仿真环境中的接入方式
- `unitreerobotics/unitree_ros2`
  借鉴真实机器人系统中的 `ROS2` 通信和控制接口组织方式
- `unitreerobotics/unitree_sdk2_python`
  借鉴 Unitree SDK 的设备接入思路和控制边界
- `leggedrobotics/legged_gym`
  借鉴四足机器人 locomotion、sim2real 和训练问题的典型拆分方式
