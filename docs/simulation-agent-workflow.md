# Simulation-First Agent Workflow

## 目标

这份文档定义 RoboClaw 在“先做仿真、再考虑真机”的阶段应该如何工作。

目标不是让大模型直接控制 Gazebo 或 ROS2，而是让 Agent 通过结构化工具和明确状态，完成：

- 识别当前仿真环境能力
- 判断导航栈是否可用
- 执行最小 smoke test
- 根据结果决定下一步

这符合当前 RoboClaw 的总体设计：

- `AgentLoop` 负责理解任务、调用工具、保存上下文
- `Tool` 负责和外部系统交互
- `manifest` / `state` 负责持久化环境事实
- `skill` 负责提供流程指导，而不是替代工具

## 当前仓库阶段说明

当前 repo 不是一个已经完整覆盖所有机器人形态的成品，而是一个正在演进中的统一 Agent 框架。

现状是：

- 当前已落地的 embodied 能力主要偏向机械臂场景
- 导航部分还没有完整实现
- 机械臂和导航目前可以独立推进开发
- 两条线后续会合并到同一个 repo 中

这份工作流基于下面的架构前提：

- RoboClaw 不应长期拆分成“机械臂 Agent”和“导航 Agent”两个彼此割裂的系统
- 目标是共享一套更通用的 embodied agent 架构，以适配不同类型的机器人
- 共享的核心层包括：`agent`、`tool`、状态/配置层、`skill`
- 差异应主要体现在不同能力域的 adapter、tool group 和 runtime facts 上，而不是复制一套新的 Agent 框架

同时，这种扩展必须满足一个约束：

- 当 navigation 能力接入共享架构时，不应破坏现有机械臂能力的使用路径
- 扩展 `tool`、`manifest` / `state`、`AGENTS`、`skill` 时，应默认采用增量式扩展，而不是覆盖或替换当前机械臂逻辑
- 如果引入新的 capability routing，也应保证原有机械臂任务仍能按已有流程工作

当前机械臂侧的状态层已经演进为 `roboclaw/embodied/manifest/`，并通过 `roboclaw/embodied/service/`、`roboclaw/embodied/engine/` 与 `roboclaw/embodied/tool.py` 形成现有工作路径。仿真导航在当前隔离阶段不应直接改写这条路径，而应先使用 `roboclaw/embodied/simulation/` 下的独立 state/profile 层，等仿真链路稳定后再决定如何合并。

因此，本文讨论的 simulation-first navigation workflow，不是要替换当前机械臂相关设计，而是要在现有 arm-first 起点上，把 RoboClaw 逐步扩展为一个同时容纳 navigation 与 manipulation 的 robot-agnostic embodied system。

## 核心原则

### 1. Simulation First

在导航能力落地前，默认优先在仿真环境验证：

- ROS graph 是否完整
- 传感器是否存在
- Nav2 是否 ready
- 基础导航任务是否能完成

### 2. Tools First, Skills Second

Agent 不应该只靠 skill 文本去猜仿真环境里有什么。

必须先有程序化能力探测工具，skill 再负责告诉 Agent 应该怎样使用这些工具。

职责边界如下：

- tool: 告诉 Agent 当前世界里有什么
- simulation state 或 embodied manifest: 记录当前环境配置和已发现能力
- skill: 告诉 Agent 在这些能力之上应该怎么完成任务
- agent: 负责编排、判断和汇总

这里还应满足一个工程约束：

- navigation tool 的引入不应改变原有机械臂 tool 的语义
- navigation state 字段的引入不应使已有机械臂 manifest 失效
- simulation/navigation skill 的加入不应覆盖机械臂 skill 或机械臂默认流程

### 2.5. CLI First, rclpy Later

在当前隔离开发阶段，可以先用 ROS 2 CLI 快速打通 navigation 和 discovery 的最小闭环。

例如：

- discovery 先通过 `ros2 pkg`、`ros2 node`、`ros2 topic`、`ros2 action`、`ros2 service`
- navigation 先通过 `ros2 action send_goal`

但这只是 bootstrap 路线，不应成为长期架构假设。

稳定版本的目标应是：

- 底层 ROS 交互逐步迁移到 `rclpy`
- 上层 `service` / `tool` 保持接口稳定
- CLI 解析逻辑收敛在 adapter/client 层，而不是扩散到 Agent workflow 本身

### 3. Runtime Facts Over Static Assumptions

即使用户说“这是 TurtleBot4 + Nav2 仿真”，Agent 也不应该直接假设：

- `/scan` 一定存在
- `navigate_to_pose` action 一定可用
- TF 一定闭合
- localization 一定正常

必须先探测，再执行。

### 4. Doctor Before Install

即使目标是“让别人尽量一键跑起来”，Agent 也不应默认直接修改系统环境。

更合理的原则是：

- 先 `doctor`
- 再输出结构化缺失项
- 需要系统级安装时先请求用户确认
- 优先调用 repo 中受控的安装入口，而不是临时拼接任意 shell 安装命令
- 安装完成后重新执行 `doctor`

例如，缺失项可以包括：

- apt 系统包
- rosdep 依赖
- ROS package
- launch / map / world / config 文件
- 环境变量或 source 步骤

### 5. Capability Profile Before Doctor

用户自然语言任务不应该直接映射到 ROS topic、node、action 名称。

更合理的路径是先把任务归类到能力域，再选择对应的 capability profile，最后用 profile 驱动 doctor 和后续工具调用。

推荐流程：

```text
用户自然语言任务
-> 解析任务类型和目标能力
-> 选择或生成 capability profile
-> 运行对应 doctor
-> 如果 ready，调用对应 tool
-> 如果 not ready，给出具体 blocker 和 next_steps
```

例如：

- “导航到目标点”应进入 `navigation` / `simulation_navigation` profile，而不是让 Agent 临时猜 `/scan`、`/odom`、`/navigate_to_pose`
- “检查仿真环境”应进入 `simulation` profile，并运行对应 doctor
- “夹取物体”应进入 `manipulation` profile，而不是误用 navigation doctor

第一版可以先提供一个固定 profile，例如 `turtlebot3_gazebo_nav2`。

后续再扩展为 profile registry：

- `turtlebot3_gazebo_nav2`
- `turtlebot4_gazebo_nav2`
- `slam_mapping`
- `manipulation_arm`
- `camera_perception`

因此，doctor 的职责不是理解自然语言，而是检查某个 capability profile 是否满足。

Agent 的职责是根据用户任务、state/manifest facts 和 runtime discovery 结果选择 profile，并根据 doctor 输出决定下一步。

## 建议工作流

### Phase 0: Environment Ready

先由开发者在 ROS 仿真环境中准备好：

- 机器人模型
- 仿真器
- 传感器插件
- 导航栈
- launch 文件

这一阶段不要求 Agent 参与配置生成。

但为了让其他开发者或测试者可以复现，repo 最好同时提供受控的安装与启动入口，例如：

- `robotics/README.md`
- `robotics/scripts/install_system_deps.sh`
- `robotics/scripts/build_ws.sh`
- `robotics/scripts/run_sim.sh`
- 可选的依赖清单，如 `apt.txt` 或 rosdep 配置

### Phase 1: Discovery

Agent 接到任务后，第一步不是导航，而是 discovery。

推荐暴露一个 `embodied_simulation(action="doctor")` 或等价工具，检查：

- 系统依赖是否满足
- ROS packages 是否安装
- 关键 launch 是否存在
- 关键 nodes 是否运行
- 关键 topics 是否在发布
- 关键 actions/services 是否存在
- TF 是否基本可用

建议输出一个机器可读的能力描述，例如：

```json
{
  "mode": "simulation",
  "robot": "turtlebot4",
  "simulator": "gazebo",
  "packages": {
    "nav2": true,
    "slam_toolbox": false
  },
  "sensors": ["lidar", "imu", "rgb_camera"],
  "topics": ["/cmd_vel", "/odom", "/scan", "/tf"],
  "actions": ["/navigate_to_pose"],
  "services": ["/reset_simulation"],
  "status": {
    "nav_ready": true,
    "tf_ready": true
  }
}
```

### Phase 2: State Sync

Discovery 完成后，Agent 应把关键环境信息同步到仿真专用 state。

在当前只验证仿真的阶段，建议先使用独立文件：

```text
~/.roboclaw/workspace/embodied/simulation_state.json
```

对应代码先放在：

```text
roboclaw/embodied/simulation/profiles.py
roboclaw/embodied/simulation/state.py
```

建议记录：

- 当前模式：`simulation` 或 `hardware`
- 当前 capability profile，例如 `turtlebot3_gazebo_nav2`
- 机器人类型：`turtlebot3` / `turtlebot4`
- 仿真器：`gazebo` / `ignition`
- 关键 topic/action/service 名称
- 地图、world、launch、config 路径
- 已发现传感器
- 最近一次 doctor manifest、status、decision、next_steps

这一步的意义是：

- 下次任务不必从零开始猜
- Agent 可以区分“上次已知能力”和“本次运行时探测结果”
- 同时保持现有机械臂 manifest/service/tool 路径不变，不因 navigation 扩展而失效

这个阶段暂时不要写入：

```text
~/.roboclaw/workspace/embodied/manifest.json
```

也暂时不要修改：

```text
roboclaw/embodied/manifest/
roboclaw/embodied/service/
roboclaw/embodied/tool.py
```

在这之后，如果要继续接 Agent tool 层，也不应默认让 simulation 复用当前 arm-first 的 `EmbodiedService` 初始化路径。当前 `EmbodiedService` 会绑定机械臂 `manifest` 生命周期，因此 simulation 更适合先有自己的 service / adapter / tool slice，再做薄集成。

### Phase 3: Bringup

如果仿真环境未运行，Agent 执行 bringup：

- 启动 simulator
- 启动 robot bringup
- 启动 navigation stack

这一层建议通过工具触发，而不是让 Agent 任意拼接 shell 命令。

如果 bringup 前 `doctor` 判定存在缺失依赖，Agent 应先进入安装引导，而不是继续尝试启动仿真。

推荐工具：

- `embodied_simulation(action="bringup")`
- `embodied_simulation(action="shutdown")`
- `embodied_simulation(action="reset_world")`

### Phase 4: Smoke Test

Bringup 完成后，不应直接开始复杂任务，而是先做最小 smoke test。

建议 smoke test 至少包含：

- `/cmd_vel` 可用
- `/odom` 正常更新
- `/scan` 或其他核心传感器正常发布
- `navigate_to_pose` action 可连接
- 一个短距离目标可成功到达

推荐工具：

- `embodied_navigation(action="smoke_test")`
- `embodied_navigation(action="nav_status")`

### Phase 5: Task Execution

只有在 smoke test 通过后，Agent 才执行用户真正想要的导航任务，例如：

- 导航到单个目标点
- 跟随 waypoints
- 执行区域巡航

推荐工具：

- `embodied_navigation(action="navigate_to_pose")`
- `embodied_navigation(action="follow_waypoints")`
- `embodied_navigation(action="cancel_nav")`

## Demo 范围建议

### Demo 1: 自然语言触发的人在环地图导航

第一版推荐把用户输入定义成：

```text
机器人移动到厨房
```

但这一版不要求 Agent 已经具备语义地图。

更合适的处理方式是：

1. Agent 先检查当前有哪些方法可用
2. 如果当前只有基于已有 SLAM 地图的导航，Agent 明确告诉用户这一点，并询问是否采用这条方法
3. 在用户同意后，Agent 执行 `doctor -> bringup`
4. Agent 启动 RViz，并提示用户做 `2D Pose Estimate`
5. Agent 通过地图候选点或 RViz 交互拿到目标位置
6. Agent 向用户确认“这里行不行”
7. 用户确认后，Agent 发送 goal pose

因此，Demo 1 的重点是：

- 自然语言触发
- 人在环初始化
- 人在环目标确认
- 地图导航

它不要求：

- 自动 room / place grounding
- skill 作为前置条件
- 主 tool registry 已经与 arm 融合

### Demo 2: 语义地图上的 room-to-room 导航

第二版再把“厨房”这类语义地点真正映射到 semantic map：

```text
厨房
-> semantic map label / region
-> candidate goal pose
-> optional user confirmation
-> navigation
```

因此，主 `roboclaw/embodied/tool.py` 的统一集成更适合放在 Demo 2 之后。

### Phase 6: Evaluation

任务执行后，Agent 不应只看“是否返回 success”。

还应评估：

- 到达成功率
- 超时次数
- 平均误差
- 恢复行为次数
- 是否发生明显碰撞或卡死

推荐工具：

- `embodied_navigation(action="collect_metrics")`

### Phase 7: Decision

Agent 根据评估结果决定下一步：

- 继续仿真测试
- 调整配置
- 标记“仿真验证通过”
- 进入未来的真机准备阶段

无论进入哪一步，workflow 都不应把 navigation 分支的状态判断错误地套用到机械臂任务上。

如果失败原因是环境依赖不满足，`decision` 也可以明确落到“需要安装或修复环境”这一类，而不是笼统地归为导航失败。

## 下一阶段优化目标：让错误处理先发生在工具层

当前 demo 路径已经暴露出一个实际问题：

- 成功路径很省 token
- 报错路径会迅速放大 token 消耗

从 workflow 角度看，核心原因是：

- tool 返回给 Agent 的错误文本过长
- ROS warning / traceback 噪声进入了聊天终端或上下文
- 本地可确定的问题没有先在 `service` / `lifecycle` 层完成诊断与清理
- Agent 被迫进入“读取长错误 -> 解释 -> 重试 -> 再解释”的循环

因此，下一阶段应把优化目标明确为：

- 优先让错误在 `simulation/tool.py`、`simulation/service.py`、`simulation/lifecycle.py`、`navigation/service.py` 这一层被归类和压缩
- Agent 只接收短结构化结果，并负责用户沟通与下一步决策

推荐约束：

- 常见错误优先返回 `error_code`、`decision`、`short_message`、`next_step`
- 详细 ROS / Gazebo / Nav2 日志进入文件，不直接冲进聊天终端
- `exit`、`shutdown`、cleanup、孤儿进程回收优先走本地逻辑
- 对 Python ABI、模型名错误、Nav2 未 ready、孤儿进程残留等高频问题，优先在工具层返回确定性 blocker

理想结果是：

- 用户只看到简短明确的 blocker
- Agent 在失败场景下不会进行多轮长推理
- 等待用户输入时不会产生额外 token 消耗

## 推荐工具分层

在接入主 Agent tool 之前，建议先有一层 simulation service / tool slice：

- `roboclaw/embodied/simulation/service.py`
- `roboclaw/embodied/simulation/lifecycle.py`
- `roboclaw/embodied/simulation/tool.py`

这层负责 `state_show`、`doctor`、`bringup`、`shutdown`、`reset_world`，并保持与机械臂 `manifest` 路径隔离。

推荐把这个阶段明确拆成两步：

- 先做 demo-only 的 Agent integration，让 Agent 能看到独立 `roboclaw/embodied/simulation/tool.py`
- 等 Demo 1 和 Demo 2 都稳定后，再把它并入主 `roboclaw/embodied/tool.py`

也就是说，在 Demo 1 和 Demo 2 完成之前，不要求 simulation tool group 进入 arm-first 的主 tool registry。

### `embodied_simulation`

负责仿真环境生命周期和能力探测：

- `state_show`
- `doctor`
- `bringup`
- `shutdown`
- `reset_world`

### `embodied_navigation`

负责导航能力和任务执行：

- `nav_status`
- `smoke_test`
- `navigate_to_pose`
- `follow_waypoints`
- `cancel_nav`
- `collect_metrics`

当前这一层允许先通过独立的 CLI wrapper 打通，例如 `nav2_client.py` 先封装 `ros2 action send_goal`。

但长期目标仍应是把这一层迁移为 `rclpy` client，而不改变上层 `NavigationService` 和 tool 接口。

## Skills 在工作流里的角色

Skill 应该在工具层稳定后再加入。

Demo 1 不需要把 skill 当作硬前置条件。只要：

- Agent 能调用独立的 simulation / navigation tools
- 有最小的流程约束
- 允许人在环初始化与目标确认

自然语言交互就可以完成第一个 demo。

一个 `navigation-sim` skill 的职责应该是：

- 告诉 Agent 优先走 `doctor -> bringup -> smoke_test -> task`
- 提醒 Agent 不要跳过 capability discovery
- 指导 Agent 在接口缺失时如何降级

Skill 不应该替代：

- 依赖安装检查
- topic/action 探测
- Nav2 状态检查
- 仿真进程管理
- 任务执行

## MCP 在工作流里的角色

第一版仿真工作流不必依赖 MCP。

更合适的顺序是：

1. 先在 repo 内部实现 Python/ROS2 adapter
2. 等接口稳定后，再考虑是否抽成外部 MCP server

只有在下面这些情况出现时，MCP 才明显更有价值：

- ROS bridge 需要独立部署
- 需要远程连另一台机器人机
- 需要跨仓库复用
- 需要用稳定协议屏蔽 ROS 实现细节

## 文件落点建议

### Agent 侧代码

放在：

- `roboclaw/embodied/simulation/`
- `roboclaw/embodied/simulation/profiles.py`
- `roboclaw/embodied/simulation/state.py`
- `roboclaw/embodied/simulation/service.py`
- `roboclaw/embodied/simulation/lifecycle.py`
- `roboclaw/embodied/simulation/tool.py`
- `roboclaw/embodied/navigation/`
- `roboclaw/embodied/ros2/`

### ROS 生态文件

单独放一个 ROS workspace，例如：

- `robotics/ros_ws/src/roboclaw_tb_sim/launch/`
- `robotics/ros_ws/src/roboclaw_tb_sim/config/`
- `robotics/ros_ws/src/roboclaw_tb_sim/worlds/`
- `robotics/ros_ws/src/roboclaw_tb_sim/maps/`

不要把 ROS launch/world/config 文件塞进：

- `roboclaw/skills/`
- `roboclaw/embodied/tool.py`
- 顶层 `bridge/` 目录

## 总结

当前阶段最合理的仿真优先工作流是：

1. 先由 ROS 环境提供可运行的仿真系统
2. 再由 Agent 通过 discovery tool 获取环境事实
3. 把事实同步到隔离的 simulation state
4. 用结构化 tool 执行 bringup、smoke test 和导航任务
5. 最后才用 skill 提升 Agent 的流程意识和任务质量

这条路径与 RoboClaw 当前的设计思路一致，也最适合后续扩展到真机。

## External References

可以记录一些外部项目作为后续参考，但不应让它们改变当前 workflow 的阶段边界。

- `ROS-LLM`: https://github.com/Auromix/ROS-LLM

当前判断：

- 它更偏“LLM 与 ROS 的自然语言控制框架”，而不是当前最需要的 capability discovery / doctor / state 同步层
- 后续如果要做更强的自然语言任务入口、ROS-side adapter 或对话式机器人控制，可以参考它的组织方式
- 当前 workflow 仍应保持 `doctor -> state sync -> bringup -> smoke test -> task`
- 在仿真环境事实和导航 readiness 没稳定前，不建议直接引入它的上层依赖和交互栈
