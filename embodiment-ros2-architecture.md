# RoboClaw Embodied Stack 架构草案

## 1. 目标

这一版架构先解决三件事：

1. RoboClaw 的自然语言入口不再直接绑死某一个 driver。
2. 所有面向本体的最终执行统一收敛到 ROS2。
3. 真机与不同仿真环境对上层暴露同一套具身契约。

`SO101` 是第一份 robot manifest，不是最终唯一实现。

这一轮额外引入了 blueprint 风格的组合层，重点是组合和 override 能力，而不是把系统继续写成一个大而全的静态清单。

## 2. 总体分层

```text
用户/对话
    ↓
通用语义技能层
    ↓
embodied/
    ├── definition
    │   ├── foundation
    │   │   └── schema
    │   ├── components
    │   │   ├── robots
    │   │   └── sensors
    │   └── systems
    │       ├── assemblies
    │       ├── deployments
    │       └── simulators
    └── execution
        ├── integration
        │   ├── carriers
        │   ├── transports
        │   └── adapters
        ├── orchestration
        │   ├── runtime
        │   └── procedures
        └── observability
            └── telemetry
```

这里最重要的边界是：

- `roboclaw/embodied/` 是具身子域的总命名空间，不再把 robot-facing 结构平铺在 `roboclaw/` 根下。
- `definition/` 是静态定义平面，负责回答“系统是什么”。
- `definition/foundation/schema/` 只定义跨 robots/sensors/carriers/transports 的公共结构和枚举。
- `definition/components/robots/` 只定义本体自己的能力、primitive、默认安全边界，并按类型分组。
- `definition/components/sensors/` 只定义传感器自己的能力和通用初始化形态，不绑死某个本体。
- 具体是 wrist / head / overhead 这样的挂载位置，属于 assembly attachment，而不是 sensor type 本身。
- `definition/systems/assemblies/` 负责把本体、传感器、carrier、transport 组合成一个可运行系统。
- `definition/systems/deployments/` 负责现场配置，而不是把现场参数写死到 manifest。
- `definition/systems/simulators/` 负责 world/scenario，而不是只保留一个 sim target 枚举。
- `execution/` 是执行平面，负责回答“系统如何被驱动和观察”。
- `execution/integration/` 负责 carrier、transport、adapter 这些接入边界。
- `execution/orchestration/runtime/` 负责当前活跃会话、连接状态、目标选择和任务状态。
- `execution/orchestration/procedures/` 负责把连接、标定、移动、debug、复位变成稳定流程。
- `execution/observability/telemetry/` 负责状态、动作、错误、诊断和复盘事件。
- execution target 必须通过 ROS2 action/service/topic 落地，不允许上层绕过 ROS2 直接发 vendor SDK。
- `roboclaw/embodied/` 只保留 framework 协议和可复用定义，不承载某个用户现场的 assembly/deployment/adapter/scenario。
- 用户现场的具体具身文件应该由 agent 生成到 `~/.roboclaw/workspace/embodied/`。

## 3. 为什么用 ROS2 作为中间层

ROS2 在这个架构里不是“再加一个复杂系统”，而是统一执行语义的边界：

- 对真实本体，它隔离 vendor SDK、串口、网络、控制节点差异。
- 对仿真本体，它让 PyBullet、Gazebo、Isaac Sim 等后端都能暴露同一套接口。
- 对 RoboClaw，它让连接、调试、标定、动作执行、传感器读取都变成一致的 transport contract。

这意味着：

- RoboClaw agent 只需要理解 `connect / execute_primitive / sensor_snapshot / reset` 等通用接口。
- 每个本体接入者主要实现 ROS2 adapter node，而不是把 prompt、driver、视觉伺服逻辑全部写进一个 Python 文件。

## 4. 统一接入契约

现在接入不再只有“本体”一个概念，而是十三个独立层：

1. `RobotManifest`
2. `RobotConfig`
3. `SensorManifest`
4. `ExecutionTarget`
5. `ROS2 transport contract`
6. `AssemblyManifest`
7. `RuntimeSession`
8. `AdapterBinding`
9. `ProcedureDefinition`
10. `DeploymentProfile`
11. `TelemetryEvent`
12. `SimulatorWorld`
13. `SimulatorScenario`

这样才支持：

- 任意机器人挂任意传感器
- 同一机器人类型可以被实例化成不同 attachment/config
- 多机器人组合成一个 assembly
- 同一 assembly 切到 real/sim carrier
- 同一 carrier 通过统一 ROS2 contract 被 RoboClaw 调用
- 在不复制整个 manifest 的情况下派生一个 demo/实验 variant

共同接口分六层：

### 4.1 Robot 能力面

- `probe_env`
- `connect`
- `disconnect`
- `get_state`
- `get_health`
- `stop`
- `reset`
- `recover`
- `list_primitives`
- `execute_primitive`
- `list_calibration_targets`
- `start_calibration`
- `calibration_status`
- `cancel_calibration`
- `list_sensors`
- `sensor_snapshot`
- `debug_snapshot`

Robot 本身还要和实例配置分开：

- `RobotManifest` 定义能力、primitive 和安全边界
- `RobotConfig` 定义某个具体实例的 id、校准目录、frame 和 backend 参数
- `RobotAttachment` 把 robot type 和 robot instance 放进 assembly

### 4.2 Sensor 定义面

- `sensor_id`
- `kind`
- `mount_points`
- `default_topic_name`
- `notes`

### 4.3 ROS2 传输面

标准 service：

- `connect`
- `disconnect`
- `stop`
- `reset`
- `recover`
- `list_calibration_targets`
- `sensor_snapshot`
- `debug_snapshot`

标准 action：

- `execute_primitive`
- `start_calibration`

标准 topic：

- `state`
- `health`
- `events`
- `joint_states`

### 4.4 Runtime 面

- `session_id`
- `assembly_id`
- `target_id`
- `deployment_id`
- `adapter_id`
- `status`
- `active_tasks`
- `last_error`

### 4.5 Procedure 面

- `connect_default`
- `calibrate_default`
- `move_default`
- `debug_default`
- `reset_default`

### 4.6 Deployment / Telemetry / Simulator 面

- deployment 持有现场连接参数和 sensor 配置
- telemetry 持有状态快照、动作 trace、错误与诊断
- simulator 持有 world 与 scenario

## 5. 真机与仿真的关系

关键原则：上层技能不要知道自己面对的是“真机”还是“哪个 simulator”，只知道当前 assembly 选中了哪个 `execution_target_id`。

例如一个 workspace 里的 assembly 可以同时声明：

- `real`
- `sim_pybullet`
- `sim_gazebo`
- `sim_isaac`

这四个 target：

- primitive 名字一致
- ROS2 action/service 名字一致
- 状态 topic 结构一致
- 只有 target 侧的具体 node 和底层 backend 不同

这样第一个版图要做的“连接、校准、移动、debug、复位”，都可以直接写成跨本体流程。

## 6. SO101 robot manifest 的定位

SO101 这一版 manifest 主要承担三件事：

1. 把当前 demo 里已经存在的有效能力抽成标准 primitive。
2. 不再把某个机器人专属命名的相机和 real/sim target 塞进 robot 定义里。
3. 为后续 xArm、Piper、人形本体提供第一份 robot 接入模板。

SO101 当前应保留在 robot 层的能力：

- joint motion
- cartesian delta
- gripper open/close
- wrist spin
- named pose save/go
- scan panorama
- calibration
- torque lock/release
- camera 相关能力通过通用 sensor type + assembly attachment 暴露

而以下能力应该上移到 assembly/语义技能层，不要继续塞进 robot：

- touch target
- pick target
- 环视总结
- 实验成功失败判定
- 场景恢复策略

## 7. 与后续四块版图的关系

### 7.1 通用具身入口版图

直接消费 assembly、ROS2 contract 和 primitives。

### 7.2 跨本体技能底座版图

技能只依赖 capability families，例如：

- 有 `CARTESIAN_MOTION` 才能执行 `向前一点`
- 有 `END_EFFECTOR` 才能执行 `夹爪开/关`
- 有 `CAMERA` 才能执行 `看一下`

### 7.3 研究助手版图

依赖 assembly 暴露的 `events/state/debug_snapshot/sensor_snapshot` 这些统一 trace 接口。

### 7.4 本体接入范式版图

robot manifest + sensor manifest + assembly manifest + ROS2 contract 本身就是接入模板。

## 8. 当前代码落点

这一轮先新增：

- `roboclaw/embodied/definition/foundation/schema/`
- `roboclaw/embodied/definition/components/robots/`
- `roboclaw/embodied/definition/components/sensors/`
- `roboclaw/embodied/definition/systems/assemblies/`
- `roboclaw/embodied/definition/systems/deployments/`
- `roboclaw/embodied/definition/systems/simulators/`
- `roboclaw/embodied/execution/integration/carriers/`
- `roboclaw/embodied/execution/integration/transports/ros2/`
- `roboclaw/embodied/execution/integration/adapters/`
- `roboclaw/embodied/execution/orchestration/runtime/`
- `roboclaw/embodied/execution/orchestration/procedures/`
- `roboclaw/embodied/execution/observability/telemetry/`

它们先把“静态分层 + 运行分层”一起固定下来。

同时约束也变了：

- framework 级具身协议和通用定义进入 `roboclaw/embodied/`
- 用户现场生成的 setup 文件进入 `~/.roboclaw/workspace/embodied/`
- agent 通过 bootstrap 文件、always-on skill 和 workspace `_templates/` 来学习如何生成这些 setup 文件
- runtime 通过 `build_catalog(workspace)` 把 workspace 下的 `ROBOT/SENSOR/ASSEMBLY/DEPLOYMENT/ADAPTER/WORLD/SCENARIO` 导出重新合并回 embodied catalog
- `roboclaw/` 根下不再新增新的 robot-facing 平铺目录
- 旧的 `schema/ robots/ sensors/ carriers/ transports/ assemblies/` 顶层位置视为废弃路径，不再继续扩展

下一轮再继续做两件事：

1. 把 bridge/runtime 真正接到 `RuntimeSession + AdapterBinding + DeploymentProfile` 上。
2. 把 SO101 的现有 driver 按 adapter 实现整理，并定义对应 ROS2 node 的输入输出。
