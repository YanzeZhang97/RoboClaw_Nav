"""Assembly exports."""

from roboclaw.embodied.definition.systems.assemblies.blueprint import AssemblyBlueprint, compose_assemblies
from roboclaw.embodied.definition.systems.assemblies.model import AssemblyManifest, RobotAttachment, SensorAttachment
from roboclaw.embodied.definition.systems.assemblies.registry import AssemblyRegistry

__all__ = [
    "AssemblyBlueprint",
    "AssemblyManifest",
    "AssemblyRegistry",
    "RobotAttachment",
    "SensorAttachment",
    "compose_assemblies",
]
