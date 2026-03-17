"""Adapter exports."""

from roboclaw.embodied.execution.integration.adapters.model import (
    AdapterBinding,
    AdapterLifecycleContract,
    AdapterOperation,
    DEFAULT_ADAPTER_LIFECYCLE,
    DependencyKind,
    DependencySpec,
    ErrorCategory,
    ErrorCodeSpec,
    OperationTimeout,
    TimeoutPolicy,
)
from roboclaw.embodied.execution.integration.adapters.protocols import EmbodiedAdapter
from roboclaw.embodied.execution.integration.adapters.registry import AdapterRegistry

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
    "OperationTimeout",
    "TimeoutPolicy",
]
