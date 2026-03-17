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
class AssemblyManifest:
    """Composed system definition."""

    id: str
    name: str
    description: str
    robots: tuple[RobotAttachment, ...]
    sensors: tuple[SensorAttachment, ...]
    execution_targets: tuple[ExecutionTarget, ...]
    default_execution_target_id: str | None = None
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

        default_target = self.default_execution_target_id or self.execution_targets[0].id
        if default_target not in target_ids:
            raise ValueError(
                f"Default execution target '{default_target}' is not defined in assembly '{self.id}'."
            )
        object.__setattr__(self, "default_execution_target_id", default_target)

    def execution_target(self, target_id: str | None = None) -> ExecutionTarget:
        resolved_id = target_id or self.default_execution_target_id
        for target in self.execution_targets:
            if target.id == resolved_id:
                return target
        raise KeyError(f"Unknown execution target '{resolved_id}' for assembly '{self.id}'.")
