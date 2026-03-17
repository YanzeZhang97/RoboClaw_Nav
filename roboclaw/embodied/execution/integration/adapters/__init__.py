"""Adapter exports."""

from roboclaw.embodied.execution.integration.adapters.model import AdapterBinding
from roboclaw.embodied.execution.integration.adapters.protocols import EmbodiedAdapter
from roboclaw.embodied.execution.integration.adapters.registry import AdapterRegistry

__all__ = [
    "AdapterBinding",
    "AdapterRegistry",
    "EmbodiedAdapter",
]
