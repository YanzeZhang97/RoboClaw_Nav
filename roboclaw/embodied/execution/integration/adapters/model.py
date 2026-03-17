"""Adapter registration types."""

from __future__ import annotations

from dataclasses import dataclass, field

from roboclaw.embodied.definition.foundation.schema import TransportKind


@dataclass(frozen=True)
class AdapterBinding:
    """Static binding between an assembly and an implementation entrypoint."""

    id: str
    assembly_id: str
    transport: TransportKind
    implementation: str
    supported_targets: tuple[str, ...]
    notes: tuple[str, ...] = field(default_factory=tuple)
