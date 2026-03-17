"""Integration-layer exports for embodied execution."""

from roboclaw.embodied.execution.integration.adapters import (
    AdapterBinding,
    AdapterRegistry,
    EmbodiedAdapter,
)
from roboclaw.embodied.execution.integration.carriers import ExecutionTarget
from roboclaw.embodied.execution.integration.transports import (
    Ros2ActionSpec,
    Ros2InterfaceBundle,
    Ros2ServiceSpec,
    Ros2TopicSpec,
    build_standard_ros2_contract,
    canonical_ros2_namespace,
)

__all__ = [
    "AdapterBinding",
    "AdapterRegistry",
    "EmbodiedAdapter",
    "ExecutionTarget",
    "Ros2ActionSpec",
    "Ros2InterfaceBundle",
    "Ros2ServiceSpec",
    "Ros2TopicSpec",
    "build_standard_ros2_contract",
    "canonical_ros2_namespace",
]
