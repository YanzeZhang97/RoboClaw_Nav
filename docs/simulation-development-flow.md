# Simulation Development Flow

## 目标

这份文档定义你接下来在 RoboClaw 中推进“仿真优先导航 Agent”的推荐开发顺序。

重点不是一次性做完 ROS、仿真、导航、skill、MCP，而是按依赖关系逐层落地，保证每一层都能独立验证。

## 当前前提

这份开发流程默认建立在下面的仓库前提之上：

- 当前 repo 还是 arm-first 的起点，已落地能力主要偏机械臂
- navigation 部分还没有完整实现
- 机械臂与导航目前可以独立推进
- 两条线最终会合并到同一个 RoboClaw repo 中

因此，这份文档的目标不是为 navigation 单独再造一套 Agent，而是让 navigation 作为新的能力域，接入 RoboClaw 共享的 embodied 架构：

- 共享 `agent`
- 共享 `tool`
- 共享状态/配置层，当前机械臂侧已演进为 `manifest`
- 共享 `skill`

换句话说，这份流程描述的是：如何在现有 arm-first 基础上，把 RoboClaw 逐步扩成一个同时容纳 manipulation 与 navigation 的 robot-agnostic embodied system。

一个额外的开发约束是：

- 在扩展 navigation 相关能力时，不应破坏现有机械臂部分的应用
- 对 `tool.py`、`manifest`、`service`、`AGENTS.md`、skill 的修改应优先采用增量扩展，而不是覆盖已有机械臂逻辑
- 每一阶段都应检查是否引入了对机械臂路径的行为回归

当前机械臂侧的实际代码结构已经演进为：

- `roboclaw/embodied/manifest/`：机械臂、手、相机等硬件绑定与持久化状态
- `roboclaw/embodied/hardware/`：硬件 scan / probe / discovery
- `roboclaw/embodied/service/`：setup、doctor、record、train 等 service/session 编排
- `roboclaw/embodied/engine/`：执行层与 command builder
- `roboclaw/embodied/tool.py`：Agent tool group dispatch

因此，仿真导航开发在当前阶段不应继续假设存在一个应直接扩展的 `roboclaw/embodied/setup.py`。

在只验证仿真的阶段，simulation/navigation 可以先使用隔离的 state/profile 文件；等仿真路径稳定后，再决定如何合并到统一 embodied manifest/service/tool 层。

## 总体策略

开发顺序应该是：

1. 先搭建 ROS 仿真环境
2. 再做 capability discovery
3. 再把 discovery 结果写入隔离的 simulation state
4. 再完成独立的 simulation / navigation service 和 tool slice
5. 再做 demo-only 的 Agent 接线
6. 再做第一个和第二个 demo
7. 最后再考虑主 tool 融合、AGENTS 规则、skill 和 MCP

不要反过来。

## 自然语言任务与 Capability Profile

对于用户自然语言任务，不应让 Agent 直接猜应该检查哪些 ROS topic、node、package 或 action。

推荐把中间层设计成 capability profile：

```text
用户自然语言任务
-> 解析任务类型和目标能力
-> 选择或生成 capability profile
-> 运行对应 doctor
-> 如果 ready，调用对应 tool
-> 如果 not ready，给出具体 blocker 和 next_steps
```

这里的 profile 是 doctor 的输入边界。

例如第一版 `turtlebot3_gazebo_nav2` profile 可以包含：

- 机器人类型：`turtlebot3`
- 仿真器：`gazebo`
- 关键 packages：`turtlebot3_gazebo`、`turtlebot3_navigation2`、`nav2_bringup`
- 关键 topics：`/cmd_vel`、`/odom`、`/scan`、`/tf`
- 关键 actions：`/navigate_to_pose`
- 关键 TF：`map -> odom`、`odom -> base_footprint`
- 关键 Nav2 nodes：`/bt_navigator`、`/controller_server`、`/planner_server`

这个 profile 只代表一个导航仿真基线，不代表通用 embodied doctor。

后续可以继续扩展更多 profile，例如：

- `turtlebot4_gazebo_nav2`
- `slam_mapping`
- `simulation_bringup`
- `manipulation_arm`
- `camera_perception`

开发上应避免把所有 topic/action 名称硬编码进一个“万能 doctor”。

更推荐的方向是：

- `ros2/discovery.py` 提供底层 runtime facts
- `simulation/doctor.py` 或后续 profile registry 读取 profile 并生成 capability manifest
- Agent 负责根据任务类型、simulation state / manifest facts 和已发现 capability 选择 profile
- tool 负责执行 profile 检查后的 bringup、smoke test 或任务动作

当前 Phase 2 可以先实现固定的 TurtleBot3/Gazebo/Nav2 profile，等这条链路稳定后再抽象 profile registry。

## Demo 目标

推荐把近期目标明确拆成两个 demo：

### Demo 1: 自然语言触发的人在环地图导航

目标是让用户可以说出类似：

```text
机器人移动到厨房
```

但这一版不要求 Agent 已经具备真正的语义地图 grounding。

更现实的流程是：

1. Agent 先 discover 当前可用方法，例如“当前可用的是基于已有 SLAM 地图的导航”
2. Agent 向用户确认是否采用这条方法
3. Agent 启动仿真与导航模块，必要时等待用户同意再启动
4. Agent 启动 RViz，并提示用户做 `2D Pose Estimate`
5. Agent 在地图上给出候选目标点或等待用户确认目标点
6. Agent 再向用户确认“这里行不行”
7. 用户确认后，Agent 发送 goal pose，并汇报执行结果

因此，Demo 1 的本质是：

- 自然语言触发
- 人在环初始化与目标确认
- 基于已有 SLAM 地图的 Nav2 导航

这一版不要求：

- 自动 room name grounding
- 纯无人值守初始化
- 语义地图
- skill 作为前置条件

### Demo 2: 语义地图上的 room-to-room 导航

第二个 demo 再在 Demo 1 之上增加：

- 语义地图
- room / place label 到目标 pose 的 grounding
- 更少的人在环确认步骤

例如：

```text
机器人移动到厨房
```

在 Demo 2 中可以被解析成：

```text
厨房
-> semantic map label / region
-> candidate goal pose
-> user optional confirmation
-> navigation
```

因此，主 `tool.py` 的统一集成更适合放在 Demo 2 之后，而不是 Demo 1 之前。

## Phase 1: 搭 ROS 仿真环境

### 目标

先确保没有 Agent 参与时，仿真机器人本身就是可运行的。

### 你要完成的事

- 确定目标平台：TurtleBot3 或 TurtleBot4
- 选定仿真器：Gazebo 或对应官方推荐环境
- 跑通机器人模型、传感器、导航栈
- 准备最小可复现 launch
- 准备最小可复现的安装与启动入口，方便其他人测试

### 产出

建议建立一个独立 ROS workspace：

```text
robotics/
  ros_ws/
    src/
      roboclaw_tb_sim/
        launch/
        config/
        worlds/
        maps/
        rviz/
```

如果希望其他人能直接复现，建议把 ROS package 源码、配置和脚本纳入 repo 管理，但不要提交 workspace 的构建产物。

推荐同时在 repo 中提供：

```text
robotics/
  README.md
  ros_ws/
    src/
      roboclaw_tb_sim/
  scripts/
    install_system_deps.sh
    build_ws.sh
    run_sim.sh
  deps/
    apt.txt
    rosdep.yaml
```

其中：

- `robotics/ros_ws/src/` 放 ROS package 源码与 launch/config/maps/worlds
- `scripts/` 放标准化安装、构建、启动入口
- `deps/` 放系统依赖与 rosdep 依赖清单
- `build/`、`install/`、`log/` 等构建产物不应进入版本库

### 这一阶段的验证标准

- 仿真可以启动
- 机器人能移动
- 关键传感器 topic 存在
- Nav2 可以工作
- 一个目标点可以被手动下发并完成
- 其他开发者可以根据 repo 中的说明完成依赖安装并跑起最小仿真

## Phase 2: 做 Environment Discovery

### 目标

让 RoboClaw 能以程序化方式知道仿真环境里有什么。

### 你要完成的事

新增一层 ROS2 discovery 代码，建议位置：

```text
roboclaw/embodied/ros2/
roboclaw/embodied/simulation/
```

推荐先实现：

- 系统依赖检查
- package 检查
- node 检查
- topic 检查
- action 检查
- service 检查
- TF 基础检查
- Nav2 ready 检查

### 建议模块

```text
roboclaw/embodied/ros2/discovery.py
roboclaw/embodied/simulation/doctor.py
```

### 实现路线说明

- 当前阶段可以先用 ROS 2 CLI 快速打通 discovery / doctor，例如 `ros2 pkg`、`ros2 node`、`ros2 topic`、`ros2 action`、`ros2 service`
- 但这只是 bootstrap 实现，不应被视为最终形态
- 稳定版本的目标应是逐步迁移到 `rclpy` / ROS 原生 client API
- 因此，`discovery.py`、`doctor.py`、后续 `nav2_client.py` 的接口应尽量保持与底层调用方式解耦，避免把 CLI 解析逻辑扩散到上层 service / tool

### 输出形式

输出结构化 dict 或 JSON，不要只输出面向人类的自由文本。

### 验证标准

- 在仿真运行时能输出稳定的 capability manifest
- 缺少组件时能给出可判断的错误信息
- 缺失依赖时能明确区分“环境未安装完成”和“导航能力本身异常”

## Phase 3: 新增 Simulation State/Profile

### 目标

把 discovery 得到的环境信息写入一个隔离的 simulation state。

当前阶段只测试仿真导航，不和机械臂部分融合。

因此，Phase 3 暂时不要改现有机械臂 `manifest`、`service` 或 `tool.py`。

这里先做一个 simulation-only state/profile 层，作为未来合并到统一 embodied manifest 的过渡层。

### 你要完成的事

新增：

```text
roboclaw/embodied/simulation/profiles.py
roboclaw/embodied/simulation/state.py
```

建议持久化到单独文件：

```text
~/.roboclaw/workspace/embodied/simulation_state.json
```

不要在这一阶段写入：

```text
~/.roboclaw/workspace/embodied/manifest.json
```

也暂时不要修改：

```text
roboclaw/embodied/manifest/
roboclaw/embodied/service/
roboclaw/embodied/tool.py
```

建议 `profiles.py` 负责 capability profile，例如：

- `turtlebot3_gazebo_nav2`
- 后续可扩展 `turtlebot4_gazebo_nav2`
- 后续可扩展 `slam_mapping`

建议 `state.py` 负责 simulation-only state，例如：

- 当前模式：`simulation`
- 当前 profile id：`turtlebot3_gazebo_nav2`
- 机器人类型
- 仿真器类型
- 关键 launch 文件路径
- 地图、world、config 路径
- 关键 topic/action/service 名称
- 已发现传感器
- 最近一次 discovery manifest
- 最近一次 doctor status / decision / next_steps

设计原则：

- 保留现有机械臂 `manifest`、`service`、`tool` 路径不变
- 不要求机械臂和导航当前共用一组字段名
- 当前阶段允许 simulation state 与 arm manifest 分离
- 但文件命名和 schema 应方便未来合并
- 新增字段应表达“能力域事实”而不是写死某一种机器人实现
- 应能区分静态配置与运行时 discovery 结果
- simulation state 的读写不能让已有机械臂 manifest 数据失效

### 最低建议接口

`state.py` 第一版可以只提供：

```text
load_simulation_state()
save_simulation_state()
default_simulation_state()
sync_from_doctor_manifest()
```

`profiles.py` 第一版可以只提供：

```text
get_profile(profile_id)
default_profile()
list_profiles()
```

### 验证标准

- simulation state 可以持久化 profile、路径、关键接口和最近一次 discovery 结果
- simulation state 不会读写机械臂 `manifest.json`
- 不修改现有机械臂 `manifest`、`service`、`tool.py` 的行为
- 后续如果要合并，应能从 `simulation_state.json` 迁移到统一 embodied manifest/service schema

## Phase 4: 新增 Simulation Service / Tool Slice

### 目标

先把仿真环境操作整理成一个独立的 simulation vertical slice：`service.py + tool.py` 都先放在 `roboclaw/embodied/simulation/` 下。

这一步的重点不是立刻把 simulation 逻辑塞进现有主 `roboclaw/embodied/tool.py`，而是先保证 simulation 运行时能力有自己的服务边界和自己的 tool 入口。

原因是当前主 `tool.py` 默认会走 `EmbodiedService`，而 `EmbodiedService` 初始化时会触发机械臂 `manifest.ensure()`。在 simulation-only 阶段，这会把 navigation 路径错误地耦合到 arm manifest。

### 你要完成的事

新增：

- `roboclaw/embodied/simulation/service.py`
- `roboclaw/embodied/simulation/lifecycle.py`
- `roboclaw/embodied/simulation/tool.py`

建议先在 service 层提供：

- `state_show`
- `doctor`
- `bringup`
- `shutdown`
- `reset_world`

这里的 `doctor` 可以继续复用 `simulation/doctor.py`，但 `bringup/shutdown/reset_world` 应通过 simulation 自己的 lifecycle 入口实现，而不是依赖机械臂 `EmbodiedService`。

`simulation/tool.py` 第一版只需要服务 simulation demo，不需要立即注册进主 `roboclaw/embodied/tool.py`。

### 对应建议模块

```text
roboclaw/embodied/simulation/service.py
roboclaw/embodied/simulation/lifecycle.py
roboclaw/embodied/simulation/tool.py
roboclaw/embodied/simulation/doctor.py
```

可选补充：

```text
robotics/scripts/install_system_deps.sh
robotics/scripts/build_ws.sh
robotics/scripts/run_sim.sh
```

### 验证标准

- simulation slice 可以独立完成 state_show / doctor / bringup / shutdown / reset_world
- simulation service 不会触发机械臂 `manifest.ensure()` 或读写机械臂 `manifest.json`
- simulation demo 可以在不修改主 `roboclaw/embodied/tool.py` 的前提下运行
- Agent 或 CLI 后续接入时，不需要直接拼接原始 ROS shell 命令
- 新增 simulation slice 不会改变现有机械臂 tool group 的行为和语义
- 缺失系统依赖时，Agent 会先报告或引导安装，而不是盲目执行 bringup

## Phase 5A: 完成独立 Simulation / Navigation Slice

### 目标

先用独立的 `roboclaw/embodied/simulation/tool.py` 和后续独立 navigation 入口，把 simulation / navigation 的运行时能力补齐，暂时不要并入主 `roboclaw/embodied/tool.py`。

这一阶段的重点是先把 vertical slice 自己跑通，而不是提前处理 arm-first tool registry 的集成问题。

### 你要完成的事

继续使用独立的：

- `embodied_simulation`
- `embodied_navigation`

建议先完成：

- `state_show`
- `doctor`
- `bringup`
- `shutdown`
- `reset_world`
- `nav_status`
- `smoke_test`
- `navigate_to_pose`
- `follow_waypoints`
- `cancel_nav`
- `collect_metrics`

### 对应建议模块

```text
roboclaw/embodied/simulation/service.py
roboclaw/embodied/simulation/tool.py
roboclaw/embodied/navigation/nav2_client.py
roboclaw/embodied/navigation/smoke_test.py
roboclaw/embodied/navigation/evaluator.py
```

### 实现建议

- 进程管理可以复用 `runner.py`
- 当前实现可以先用 CLI wrapper 打通最小 vertical slice，例如 `ros2 action send_goal`
- 但这只是过渡方案，最终目标仍应是 `rclpy` client
- 不建议长期完全依赖 `ros2 topic echo`、`ros2 action send_goal` 这类 shell CLI
- `service.py` / `tool.py` 不应感知底层是 CLI 还是 `rclpy`，迁移应主要收敛在 `nav2_client.py`、`discovery.py` 一层
- 第一个 demo 完成前，不要求 simulation tool group 进入主 tool registry

### 验证标准

- simulation / navigation slice 继续走独立 `SimulationService`，不会隐式触发 arm manifest 初始化
- 不修改主 `roboclaw/embodied/tool.py` 也能完成第一个导航 demo 的底层能力
- Agent 后续接入时，不需要重新设计底层 service / lifecycle

## Phase 5B: Demo-only Agent Integration

### 目标

让 Agent 能在不修改主 `roboclaw/embodied/tool.py` 的前提下调用独立的 simulation / navigation tools。

这一阶段的目标是做 demo-only 接线，而不是架构合并。

### 你要完成的事

- 让 Agent 能看到独立的 `embodied_simulation`
- 让 Agent 能看到独立的 `embodied_navigation`
- 允许通过 demo mode、单独 launcher 或单独 registry 挂载这些 tools
- 不要求并入主 `roboclaw/embodied/tool.py`
- 不要求改 arm-first 的 `EmbodiedService`

### 验证标准

- Agent 可以通过自然语言触发 simulation / navigation tool 调用
- demo-only 接线不需要改 arm 主路径
- simulation / navigation tools 继续走独立 service

## Phase 6: Demo 1 - 人在环地图导航

### 目标

完成第一个自然语言导航 demo：用户说“机器人移动到厨房”，Agent 在当前只有地图导航能力的情况下，通过人在环确认完成任务。

### 你要完成的事

- Agent 接收自然语言任务，例如“机器人移动到厨房”
- Agent 先 discover 当前有哪些方法可用
- 如果当前只有基于已有 SLAM 地图的导航，Agent 应明确告诉用户这一点，并询问是否采用这条方法
- Agent 在获得同意后执行 `doctor -> bringup`
- Agent 启动 RViz，并提示用户做 `2D Pose Estimate`
- Agent 在地图上给出候选目标点，或等待用户确认目标点
- Agent 向用户确认“这里行不行”
- 用户确认后，Agent 发送 goal pose 并汇报结果

### 验证标准

- Agent 可以用自然语言完成上述交互闭环
- Demo 1 不依赖 skill 也能成立
- Agent 不会假装已经理解“厨房”的精确语义位置，而是通过地图候选点和用户确认完成任务

## Phase 7: Demo 2 - 语义地图 Room-to-Room 导航

### 目标

在 Demo 1 的基础上增加语义地图，使自然语言地点真正映射到语义区域或房间。

### 你要完成的事

- 引入 semantic map 或 place label 层
- 支持 room / place name 到 candidate goal pose 的 grounding
- 让 Agent 能解释当前的 grounding 结果，并在需要时向用户确认
- 在“厨房”“房间 2”“会议室”等语义目标上执行导航

### 验证标准

- Agent 可以把自然语言地点映射成语义地图中的候选位置
- 用户确认步骤可以减少，但仍保留必要的安全确认
- Demo 2 跑通后，tool surface 才更接近长期稳定形态

## 下一阶段优化目标：错误路径 Token 与噪声控制

当前 demo 路径里，一个明确现象是：

- 成功路径 token 消耗很低
- 失败路径 token 消耗会明显升高

根因通常不是“报错”本身，而是：

- 长 ROS traceback 或 launch warning 被直接送进 Agent 上下文
- Agent 在错误状态下重复执行 doctor、bringup、解释、重试
- 本地可确定的问题被交给 LLM 做长篇诊断
- 退出、清理、孤儿进程回收没有在 `tool` / `service` / `lifecycle` 层完成

因此，下一阶段的优化目标应明确为：

- 把 deterministic 的错误处理尽量下沉到 `tool` / `service` / `lifecycle`
- 让 LLM 只接收短而结构化的错误结果，而不是整段 ROS 日志
- 保持成功路径短闭环，同时避免失败路径进入长诊断循环

推荐优化方向：

- `doctor`、`bringup`、`navigate_to_pose` 返回短结构化错误码，例如：
  - `python_abi_mismatch`
  - `model_not_found`
  - `nav_not_ready`
  - `orphan_process_detected`
- ROS / Gazebo / Nav2 的详细日志写入文件，并在结果里返回 `log_path`
- 工具默认不要把完整 traceback、warning flood、launch stdout 直接回灌给 Agent
- `exit`、`shutdown`、cleanup、daemon refresh、孤儿进程回收优先在本地处理，不走 LLM
- 在常见失败场景下，优先返回：
  - `decision`
  - `error_code`
  - `short_message`
  - `next_step`
  而不是长自然语言分析

这一阶段的验收标准可以是：

- 失败场景下的 Agent 回复仍保持简短
- 常见环境错误不会触发多轮长推理
- Demo 终端不会被 ROS warning / debug 日志覆盖
- 停留在等待用户输入时，不发生额外 token 消耗

## Phase 8: 主 Tool Layer 融合

### 目标

等 Demo 1 和 Demo 2 都稳定后，再把 simulation / navigation 并入主 tool registry。

这一阶段如果要改 `tool.py`，也应优先做“按能力域选择不同 service factory / adapter”的轻量改造，而不是继续把所有 dispatch 逻辑硬编码到 arm-first 分支里。

### 你要完成的事

- 把 `roboclaw/embodied/simulation/tool.py` 暴露的 simulation group 并入主 tool registry
- 让 simulation group 走 `SimulationService`
- 保持现有 arm group 继续走 `EmbodiedService`
- 在 `roboclaw/embodied/tool.py` 中新增或接入 `embodied_simulation`
- 在 `roboclaw/embodied/tool.py` 中新增或接入 `embodied_navigation`

### 验证标准

- 主 tool registry 可以同时暴露 arm 与 simulation group
- simulation tool group 仍走独立 `SimulationService`
- 新增 navigation tool group 不会影响现有机械臂控制、采集、训练相关能力

## Phase 9: 更新 Agent Rules

### 目标

在 tool surface 稳定后，再把正式的 navigation workflow 规则写入 Agent 侧文档。

### 你要完成的事

扩展：

- `roboclaw/templates/AGENTS.md`

补充 simulation/navigation workflow 规则，例如：

- 先 `state_show`
- 再 `doctor`
- 再 `bringup`
- 再 `smoke_test`
- 通过后才能执行正式导航任务

这里不是要覆盖现有机械臂 workflow，而是要补充“当任务属于 navigation / simulation 能力域时，Agent 应进入哪一条流程”。

建议明确：

- 保留现有机械臂流程规则
- 新增 simulation/navigation 流程规则
- Agent 需要基于 `runtime.mode`、用户任务类型、已发现 capability 来做流程分流
- 不同能力域共享同一套 Agent 框架，但不强行共享一条执行顺序

### 验证标准

- Agent 不会一上来直接发导航目标
- Agent 会优先检查环境能力
- Agent 不会因为引入 navigation workflow 而破坏现有机械臂 workflow
- 机械臂任务仍会优先进入原有机械臂流程，而不是误入 navigation workflow

## Phase 10: 加 Skill

### 目标

让 Agent 在 Demo 1 / Demo 2 已跑通后，更稳定地遵循仿真导航流程。

### 你要完成的事

新增 skill，例如：

```text
roboclaw/skills/navigation-sim/SKILL.md
```

这个 skill 应该写：

- 仿真导航任务的推荐步骤
- 缺少关键接口时的降级规则
- smoke test 的通过条件
- 常见错误和排查顺序

### 不要让 skill 做的事

- 替代 runtime discovery
- 假设 topic/action 一定存在
- 管理 ROS 进程

### 验证标准

- Agent 在复杂任务里更稳定地走正确流程
- 但即使去掉 skill，工具链本身仍然可用

## Phase 11: 再考虑 MCP

### 目标

只有在内部 adapter 稳定后，再决定是否抽成外部服务。

### 适合引入 MCP 的场景

- ROS bridge 想独立运行
- 需要远程连接仿真机或机器人机
- 需要跨项目复用
- 想给其他 agent 或前端暴露统一接口

### 当前阶段建议

先不要把 MCP 放在关键路径里。

先做 repo 内原生实现，再考虑抽象成 MCP。

## 最小可行开发顺序

如果你想最快看到结果，建议按下面顺序推进：

1. 在 `robotics/ros_ws/` 跑通 TurtleBot 仿真
2. 补 `robotics/README.md` 与安装/构建/启动脚本
3. 写 `discovery.py`，生成 capability manifest
4. 新增隔离的 `simulation/profiles.py` 与 `simulation/state.py`
5. 新增 `simulation/service.py` 与 `simulation/lifecycle.py`
6. 用独立 `simulation/tool.py` 和 navigation 入口补齐 vertical slice
7. 做 demo-only 的 Agent 接线
8. 跑通 Demo 1
9. 跑通 Demo 2
10. 再把 `embodied_simulation` / `embodied_navigation` 接入主 tool layer
11. 更新 `AGENTS.md`
12. 最后加 `navigation-sim` skill

## 第一版完成标准

第一版不需要覆盖所有导航能力，只要做到：

- Agent 能检查仿真环境是否 ready
- Agent 能发现关键传感器和导航接口
- Agent 能启动仿真
- Agent 能执行一个最小导航 smoke test
- Agent 能输出结构化结果和下一步建议
- 第一个 demo 可以在没有 skill 的情况下，通过自然语言 + 人在环确认完成
- 在引入以上能力后，现有机械臂主路径不发生明显回归
- 其他开发者可以依据 repo 内文档与脚本完成依赖安装、构建和最小仿真启动

建议第一版就定义一个最小结构化输出，至少包含：

- environment summary
- smoke test result
- navigation status
- collected metrics
- decision
- next steps

例如：

```json
{
  "environment": {
    "mode": "simulation",
    "robot": "turtlebot4",
    "simulator": "gazebo",
    "nav_ready": true,
    "tf_ready": true
  },
  "smoke_test": {
    "passed": true,
    "checks": {
      "cmd_vel": true,
      "odom": true,
      "scan": true,
      "navigate_to_pose": true
    }
  },
  "metrics": {
    "goal_reached": true,
    "timeout_count": 0,
    "recovery_count": 0
  },
  "decision": "simulation_validated",
  "next_steps": [
    "run waypoint navigation test"
  ]
}
```

`decision` 第一版至少应支持：

- `blocked`
- `needs_reconfiguration`
- `ready_for_smoke_test`
- `simulation_validated`
- `needs_more_simulation`

达到这一步，才适合继续推进更复杂的导航任务和后续真机路径。

## External References

可以记录一些外部项目作为后续参考，但不要让它们进入当前关键路径。

- `ROS-LLM`: https://github.com/Auromix/ROS-LLM

当前判断：

- 这个项目更偏“自然语言交互 + LLM 控制 ROS”，适合作为后续 Phase 4/5 之后的参考
- 可以借鉴它对 ROS 能力封装、机器人接口适配、LLM 交互入口的组织方式
- 当前 Phase 2/3 仍应优先完成 `discovery -> doctor -> simulation state/profile`
- 不建议在当前阶段把它的 OpenAI / AWS / Whisper / chat pipeline 直接引入本 repo
