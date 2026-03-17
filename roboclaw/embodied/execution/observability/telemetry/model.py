"""Telemetry and trace records for embodied systems."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

try:
    from enum import StrEnum
except ImportError:  # pragma: no cover - Python < 3.11 fallback for local tooling.
    class StrEnum(str, Enum):
        """Fallback for Python versions without enum.StrEnum."""


class TelemetryKind(StrEnum):
    """Telemetry event category."""

    STATE = "state"
    ACTION = "action"
    ERROR = "error"
    SENSOR = "sensor"
    DIAGNOSTIC = "diagnostic"


@dataclass(frozen=True)
class TelemetryEvent:
    """One structured telemetry event."""

    kind: TelemetryKind
    source: str
    message: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StateSnapshot:
    """Normalized runtime state snapshot."""

    assembly_id: str
    target_id: str
    status: str
    joints: dict[str, float] = field(default_factory=dict)
    sensors: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ActionTrace:
    """Action execution trace."""

    action: str
    status: str
    request: dict[str, Any] = field(default_factory=dict)
    result: dict[str, Any] = field(default_factory=dict)
