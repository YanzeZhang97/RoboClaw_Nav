"""Integration-layer exports for embodied execution."""

from roboclaw.embodied.execution.integration.adapters import (
    AdapterBinding,
    AdapterLifecycleContract,
    AdapterOperation,
    AdapterRegistry,
    DEFAULT_ADAPTER_LIFECYCLE,
    DependencyKind,
    DependencySpec,
    EmbodiedAdapter,
    ErrorCategory,
    ErrorCodeSpec,
    OperationTimeout,
    TimeoutPolicy,
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
    "AdapterLifecycleContract",
    "AdapterOperation",
    "AdapterRegistry",
    "DEFAULT_ADAPTER_LIFECYCLE",
    "DependencyKind",
    "DependencySpec",
    "EmbodiedAdapter",
    "ErrorCategory",
    "ErrorCodeSpec",
    "ExecutionTarget",
    "OperationTimeout",
    "Ros2ActionSpec",
    "Ros2InterfaceBundle",
    "Ros2ServiceSpec",
    "Ros2TopicSpec",
    "TimeoutPolicy",
    "build_standard_ros2_contract",
    "canonical_ros2_namespace",
]
