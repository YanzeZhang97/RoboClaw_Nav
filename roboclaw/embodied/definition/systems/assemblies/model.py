"""Assembly manifests compose robots, sensors, transports, and carriers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from roboclaw.embodied.execution.integration.carriers import ExecutionTarget


@dataclass(frozen=True)
class RobotAttachment:
    """Attach a robot manifest into one assembly."""

    attachment_id: str
    robot_id: str
    role: str = "primary"
    config: Any | None = None


@dataclass(frozen=True)
class SensorAttachment:
    """Attach a sensor manifest into one assembly."""

    attachment_id: str
    sensor_id: str
    mount: str
    config: Any | None = None
    optional: bool = False


@dataclass(frozen=True)
class Transform3D:
    """Rigid transform represented in XYZ translation + RPY rotation."""

    translation_xyz: tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation_rpy: tuple[float, float, float] = (0.0, 0.0, 0.0)


@dataclass(frozen=True)
class FrameTransform:
    """Frame relation used by assembly topology."""

    parent_frame: str
    child_frame: str
    transform: Transform3D = field(default_factory=Transform3D)
    static: bool = True
    notes: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ToolAttachment:
    """Attach a tool or end-effector to one robot attachment."""

    attachment_id: str
    robot_attachment_id: str
    tool_id: str
    mount_frame: str
    tcp_frame: str | None = None
    kind: str = "end_effector"
    notes: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ControlGroup:
    """Named control group spanning robot and sensor attachments."""

    id: str
    robot_attachment_ids: tuple[str, ...] = field(default_factory=tuple)
    sensor_attachment_ids: tuple[str, ...] = field(default_factory=tuple)
    mode_hints: tuple[str, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class AssemblyManifest:
    """Composed system definition."""

    id: str
    name: str
    description: str
    robots: tuple[RobotAttachment, ...]
    sensors: tuple[SensorAttachment, ...]
    execution_targets: tuple[ExecutionTarget, ...]
    default_execution_target_id: str | None = None
    frame_transforms: tuple[FrameTransform, ...] = field(default_factory=tuple)
    tools: tuple[ToolAttachment, ...] = field(default_factory=tuple)
    control_groups: tuple[ControlGroup, ...] = field(default_factory=tuple)
    default_control_group_id: str | None = None
    notes: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.robots:
            raise ValueError("Assembly manifest must contain at least one robot.")
        if not self.execution_targets:
            raise ValueError("Assembly manifest must declare at least one execution target.")

        target_ids = [target.id for target in self.execution_targets]
        if len(set(target_ids)) != len(target_ids):
            raise ValueError(f"Duplicate execution target ids in assembly '{self.id}'.")
        robot_attachment_ids = [robot.attachment_id for robot in self.robots]
        if len(set(robot_attachment_ids)) != len(robot_attachment_ids):
            raise ValueError(f"Duplicate robot attachment ids in assembly '{self.id}'.")
        sensor_attachment_ids = [sensor.attachment_id for sensor in self.sensors]
        if len(set(sensor_attachment_ids)) != len(sensor_attachment_ids):
            raise ValueError(f"Duplicate sensor attachment ids in assembly '{self.id}'.")
        frame_child_ids = [frame.child_frame for frame in self.frame_transforms]
        if len(set(frame_child_ids)) != len(frame_child_ids):
            raise ValueError(f"Duplicate frame child ids in assembly '{self.id}'.")
        tool_attachment_ids = [tool.attachment_id for tool in self.tools]
        if len(set(tool_attachment_ids)) != len(tool_attachment_ids):
            raise ValueError(f"Duplicate tool attachment ids in assembly '{self.id}'.")
        control_group_ids = [group.id for group in self.control_groups]
        if len(set(control_group_ids)) != len(control_group_ids):
            raise ValueError(f"Duplicate control group ids in assembly '{self.id}'.")

        robot_attachment_set = set(robot_attachment_ids)
        sensor_attachment_set = set(sensor_attachment_ids)
        for tool in self.tools:
            if tool.robot_attachment_id not in robot_attachment_set:
                raise ValueError(
                    f"Tool '{tool.attachment_id}' references unknown robot attachment "
                    f"'{tool.robot_attachment_id}' in assembly '{self.id}'."
                )
        for group in self.control_groups:
            missing_robots = set(group.robot_attachment_ids) - robot_attachment_set
            missing_sensors = set(group.sensor_attachment_ids) - sensor_attachment_set
            if missing_robots:
                raise ValueError(
                    f"Control group '{group.id}' references unknown robot attachments "
                    f"{sorted(missing_robots)} in assembly '{self.id}'."
                )
            if missing_sensors:
                raise ValueError(
                    f"Control group '{group.id}' references unknown sensor attachments "
                    f"{sorted(missing_sensors)} in assembly '{self.id}'."
                )

        default_target = self.default_execution_target_id or self.execution_targets[0].id
        if default_target not in target_ids:
            raise ValueError(
                f"Default execution target '{default_target}' is not defined in assembly '{self.id}'."
            )
        object.__setattr__(self, "default_execution_target_id", default_target)

        default_control_group = self.default_control_group_id
        if self.control_groups:
            resolved_group = default_control_group or self.control_groups[0].id
            if resolved_group not in control_group_ids:
                raise ValueError(
                    f"Default control group '{resolved_group}' is not defined in assembly '{self.id}'."
                )
            object.__setattr__(self, "default_control_group_id", resolved_group)
        elif default_control_group is not None:
            raise ValueError(
                f"Assembly '{self.id}' defines default control group '{default_control_group}' "
                "without any control groups."
            )

    def execution_target(self, target_id: str | None = None) -> ExecutionTarget:
        resolved_id = target_id or self.default_execution_target_id
        for target in self.execution_targets:
            if target.id == resolved_id:
                return target
        raise KeyError(f"Unknown execution target '{resolved_id}' for assembly '{self.id}'.")

    def control_group(self, group_id: str | None = None) -> ControlGroup:
        if not self.control_groups:
            raise KeyError(f"Assembly '{self.id}' has no control groups.")

        resolved_id = group_id or self.default_control_group_id
        for group in self.control_groups:
            if group.id == resolved_id:
                return group
        raise KeyError(f"Unknown control group '{resolved_id}' for assembly '{self.id}'.")
