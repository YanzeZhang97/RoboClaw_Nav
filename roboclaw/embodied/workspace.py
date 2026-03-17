"""Workspace asset loading for embodied catalogs."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

from roboclaw.embodied.catalog import EmbodiedCatalog


def load_workspace_assets(catalog: EmbodiedCatalog, workspace: Path) -> EmbodiedCatalog:
    """Load workspace-generated embodied assets into an existing catalog."""

    root = workspace.expanduser().resolve() / "embodied"
    if not root.exists():
        return catalog

    _load_group(root / "robots", ("ROBOT", "ROBOTS"), catalog.robots.register)
    _load_group(root / "sensors", ("SENSOR", "SENSORS"), catalog.sensors.register)
    _load_group(root / "assemblies", ("ASSEMBLY", "ASSEMBLIES"), catalog.assemblies.register)
    _load_group(root / "adapters", ("ADAPTER", "ADAPTERS"), catalog.adapters.register)
    _load_group(root / "deployments", ("DEPLOYMENT", "DEPLOYMENTS"), catalog.deployments.register)
    _load_group(root / "simulators" / "worlds", ("WORLD", "WORLDS"), catalog.simulators.register_world)
    _load_group(
        root / "simulators" / "scenarios",
        ("SCENARIO", "SCENARIOS"),
        catalog.simulators.register_scenario,
    )
    return catalog


def _load_group(root: Path, export_names: tuple[str, str], registrar) -> None:
    if not root.exists():
        return
    for path in sorted(root.rglob("*.py")):
        if path.name == "__init__.py":
            continue
        module = _load_module(path)
        for item in _read_exports(module, *export_names):
            registrar(item)


def _read_exports(module: ModuleType, singular: str, plural: str) -> tuple[object, ...]:
    if hasattr(module, plural):
        value = getattr(module, plural)
        return tuple(value)
    if hasattr(module, singular):
        return (getattr(module, singular),)
    return ()


def _load_module(path: Path) -> ModuleType:
    module_name = "roboclaw_workspace_" + "_".join(path.with_suffix("").parts[-6:])
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load workspace module from '{path}'.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
