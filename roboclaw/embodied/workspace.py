"""Workspace asset loading for embodied catalogs."""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from types import ModuleType

from roboclaw.embodied.catalog import EmbodiedCatalog

try:
    from enum import StrEnum
except ImportError:  # pragma: no cover - Python < 3.11 fallback for local tooling.
    class StrEnum(str, Enum):
        """Fallback for Python versions without enum.StrEnum."""


WORKSPACE_SCHEMA_VERSION = "1.0"
SUPPORTED_WORKSPACE_SCHEMA_VERSIONS = (WORKSPACE_SCHEMA_VERSION,)


class WorkspaceAssetKind(StrEnum):
    """Supported workspace asset kinds."""

    ROBOT = "robot"
    SENSOR = "sensor"
    ASSEMBLY = "assembly"
    ADAPTER = "adapter"
    DEPLOYMENT = "deployment"
    WORLD = "world"
    SCENARIO = "scenario"


class WorkspaceExportConvention(StrEnum):
    """Export variable convention for one workspace asset file."""

    AUTO = "AUTO"
    ROBOT = "ROBOT"
    ROBOTS = "ROBOTS"
    SENSOR = "SENSOR"
    SENSORS = "SENSORS"
    ASSEMBLY = "ASSEMBLY"
    ASSEMBLIES = "ASSEMBLIES"
    ADAPTER = "ADAPTER"
    ADAPTERS = "ADAPTERS"
    DEPLOYMENT = "DEPLOYMENT"
    DEPLOYMENTS = "DEPLOYMENTS"
    WORLD = "WORLD"
    WORLDS = "WORLDS"
    SCENARIO = "SCENARIO"
    SCENARIOS = "SCENARIOS"


class WorkspaceMigrationPolicy(StrEnum):
    """How loader should handle unsupported schema versions."""

    STRICT = "strict"
    ACCEPT_UNSUPPORTED = "accept_unsupported"


class WorkspaceIssueLevel(StrEnum):
    """Validation issue severity."""

    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True)
class WorkspaceAssetContract:
    """Metadata contract for one workspace asset module."""

    kind: WorkspaceAssetKind
    schema_version: str = WORKSPACE_SCHEMA_VERSION
    export_convention: WorkspaceExportConvention = WorkspaceExportConvention.AUTO
    migration_policy: WorkspaceMigrationPolicy = WorkspaceMigrationPolicy.STRICT
    notes: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.schema_version.strip():
            raise ValueError("Workspace asset schema_version cannot be empty.")


@dataclass(frozen=True)
class WorkspaceValidationIssue:
    """One static validation issue for workspace loading."""

    level: WorkspaceIssueLevel
    code: str
    path: str
    message: str


@dataclass(frozen=True)
class WorkspaceLoadReport:
    """Validation and staging report for workspace assets."""

    root: str
    schema_version: str = WORKSPACE_SCHEMA_VERSION
    loaded_counts: dict[WorkspaceAssetKind, int] = field(default_factory=dict)
    issues: tuple[WorkspaceValidationIssue, ...] = field(default_factory=tuple)

    @property
    def has_errors(self) -> bool:
        return any(issue.level == WorkspaceIssueLevel.ERROR for issue in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(issue.level == WorkspaceIssueLevel.WARNING for issue in self.issues)


@dataclass(frozen=True)
class _WorkspaceGroupSpec:
    kind: WorkspaceAssetKind
    relative_dir: tuple[str, ...]
    singular_export: WorkspaceExportConvention
    plural_export: WorkspaceExportConvention

    @property
    def exports(self) -> tuple[str, str]:
        return (self.singular_export.value, self.plural_export.value)

    @property
    def allowed_conventions(self) -> tuple[WorkspaceExportConvention, ...]:
        return (WorkspaceExportConvention.AUTO, self.singular_export, self.plural_export)


@dataclass(frozen=True)
class _StagedAsset:
    kind: WorkspaceAssetKind
    asset_id: str
    path: Path
    value: object


_GROUP_SPECS = (
    _WorkspaceGroupSpec(
        kind=WorkspaceAssetKind.ROBOT,
        relative_dir=("robots",),
        singular_export=WorkspaceExportConvention.ROBOT,
        plural_export=WorkspaceExportConvention.ROBOTS,
    ),
    _WorkspaceGroupSpec(
        kind=WorkspaceAssetKind.SENSOR,
        relative_dir=("sensors",),
        singular_export=WorkspaceExportConvention.SENSOR,
        plural_export=WorkspaceExportConvention.SENSORS,
    ),
    _WorkspaceGroupSpec(
        kind=WorkspaceAssetKind.ASSEMBLY,
        relative_dir=("assemblies",),
        singular_export=WorkspaceExportConvention.ASSEMBLY,
        plural_export=WorkspaceExportConvention.ASSEMBLIES,
    ),
    _WorkspaceGroupSpec(
        kind=WorkspaceAssetKind.ADAPTER,
        relative_dir=("adapters",),
        singular_export=WorkspaceExportConvention.ADAPTER,
        plural_export=WorkspaceExportConvention.ADAPTERS,
    ),
    _WorkspaceGroupSpec(
        kind=WorkspaceAssetKind.DEPLOYMENT,
        relative_dir=("deployments",),
        singular_export=WorkspaceExportConvention.DEPLOYMENT,
        plural_export=WorkspaceExportConvention.DEPLOYMENTS,
    ),
    _WorkspaceGroupSpec(
        kind=WorkspaceAssetKind.WORLD,
        relative_dir=("simulators", "worlds"),
        singular_export=WorkspaceExportConvention.WORLD,
        plural_export=WorkspaceExportConvention.WORLDS,
    ),
    _WorkspaceGroupSpec(
        kind=WorkspaceAssetKind.SCENARIO,
        relative_dir=("simulators", "scenarios"),
        singular_export=WorkspaceExportConvention.SCENARIO,
        plural_export=WorkspaceExportConvention.SCENARIOS,
    ),
)


def inspect_workspace_assets(workspace: Path) -> WorkspaceLoadReport:
    """Inspect workspace assets with static checks and duplicate detection."""

    root = workspace.expanduser().resolve() / "embodied"
    staged, report = _collect_workspace_assets(root)
    del staged
    return report


def load_workspace_assets(catalog: EmbodiedCatalog, workspace: Path) -> EmbodiedCatalog:
    """Load workspace-generated embodied assets into an existing catalog."""

    root = workspace.expanduser().resolve() / "embodied"
    staged_assets, report = _collect_workspace_assets(root)
    report = _check_catalog_conflicts(catalog, staged_assets, report)

    if report.has_errors:
        raise ValueError(_format_workspace_errors(report))

    for asset in staged_assets:
        _register_staged_asset(catalog, asset)
    return catalog


def _collect_workspace_assets(root: Path) -> tuple[list[_StagedAsset], WorkspaceLoadReport]:
    counts = {spec.kind: 0 for spec in _GROUP_SPECS}
    if not root.exists():
        return [], WorkspaceLoadReport(root=str(root), loaded_counts=counts)

    issues: list[WorkspaceValidationIssue] = []
    staged_assets: list[_StagedAsset] = []

    for spec in _GROUP_SPECS:
        group_assets = _load_group(root.joinpath(*spec.relative_dir), spec, issues)
        staged_assets.extend(group_assets)
        counts[spec.kind] = len(group_assets)

    report = WorkspaceLoadReport(
        root=str(root),
        loaded_counts=counts,
        issues=tuple(issues),
    )
    return staged_assets, report


def _load_group(
    root: Path,
    spec: _WorkspaceGroupSpec,
    issues: list[WorkspaceValidationIssue],
) -> list[_StagedAsset]:
    if not root.exists():
        return []

    staged: list[_StagedAsset] = []
    seen_ids: dict[str, Path] = {}
    for path in sorted(root.rglob("*.py")):
        if path.name == "__init__.py":
            continue

        module = _try_load_module(path, issues)
        if module is None:
            continue

        contract = _read_asset_contract(module, spec, path, issues)
        if contract is None:
            continue

        exports = _read_exports(module, spec, contract, path, issues)
        if not exports:
            continue

        for item in exports:
            asset_id = _read_asset_id(item)
            if asset_id is None:
                issues.append(
                    WorkspaceValidationIssue(
                        level=WorkspaceIssueLevel.ERROR,
                        code="ASSET_ID_MISSING",
                        path=str(path),
                        message=(
                            f"{spec.kind.value} export must define a non-empty string 'id' attribute."
                        ),
                    )
                )
                continue

            if asset_id in seen_ids:
                issues.append(
                    WorkspaceValidationIssue(
                        level=WorkspaceIssueLevel.ERROR,
                        code="DUPLICATE_ASSET_ID",
                        path=str(path),
                        message=(
                            f"Duplicate {spec.kind.value} id '{asset_id}' also defined in "
                            f"'{seen_ids[asset_id]}'."
                        ),
                    )
                )
                continue

            seen_ids[asset_id] = path
            staged.append(
                _StagedAsset(
                    kind=spec.kind,
                    asset_id=asset_id,
                    path=path,
                    value=item,
                )
            )

    return staged


def _read_asset_contract(
    module: ModuleType,
    spec: _WorkspaceGroupSpec,
    path: Path,
    issues: list[WorkspaceValidationIssue],
) -> WorkspaceAssetContract | None:
    if hasattr(module, "WORKSPACE_ASSET"):
        value = getattr(module, "WORKSPACE_ASSET")
        if not isinstance(value, WorkspaceAssetContract):
            issues.append(
                WorkspaceValidationIssue(
                    level=WorkspaceIssueLevel.ERROR,
                    code="INVALID_WORKSPACE_ASSET_TYPE",
                    path=str(path),
                    message="WORKSPACE_ASSET must be an instance of WorkspaceAssetContract.",
                )
            )
            return None
        contract = value
    else:
        contract = WorkspaceAssetContract(kind=spec.kind)

    if contract.kind != spec.kind:
        issues.append(
            WorkspaceValidationIssue(
                level=WorkspaceIssueLevel.ERROR,
                code="ASSET_KIND_MISMATCH",
                path=str(path),
                message=(
                    f"WORKSPACE_ASSET.kind '{contract.kind.value}' does not match folder kind "
                    f"'{spec.kind.value}'."
                ),
            )
        )
        return None

    if contract.export_convention not in spec.allowed_conventions:
        issues.append(
            WorkspaceValidationIssue(
                level=WorkspaceIssueLevel.ERROR,
                code="INVALID_EXPORT_CONVENTION",
                path=str(path),
                message=(
                    f"Export convention '{contract.export_convention.value}' is invalid for "
                    f"{spec.kind.value}; use one of {tuple(item.value for item in spec.allowed_conventions)}."
                ),
            )
        )
        return None

    if contract.schema_version not in SUPPORTED_WORKSPACE_SCHEMA_VERSIONS:
        level = (
            WorkspaceIssueLevel.WARNING
            if contract.migration_policy == WorkspaceMigrationPolicy.ACCEPT_UNSUPPORTED
            else WorkspaceIssueLevel.ERROR
        )
        issues.append(
            WorkspaceValidationIssue(
                level=level,
                code="UNSUPPORTED_SCHEMA_VERSION",
                path=str(path),
                message=(
                    f"Schema version '{contract.schema_version}' is not supported by loader "
                    f"{SUPPORTED_WORKSPACE_SCHEMA_VERSIONS}; migration policy is "
                    f"'{contract.migration_policy.value}'."
                ),
            )
        )
        if level == WorkspaceIssueLevel.ERROR:
            return None

    return contract


def _read_exports(
    module: ModuleType,
    spec: _WorkspaceGroupSpec,
    contract: WorkspaceAssetContract,
    path: Path,
    issues: list[WorkspaceValidationIssue],
) -> tuple[object, ...]:
    singular, plural = spec.exports
    if contract.export_convention == spec.singular_export:
        convention = singular
    elif contract.export_convention == spec.plural_export:
        convention = plural
    else:
        convention = _resolve_auto_export_convention(module, singular, plural, path, issues)
        if convention is None:
            return ()

    if not hasattr(module, convention):
        issues.append(
            WorkspaceValidationIssue(
                level=WorkspaceIssueLevel.ERROR,
                code="MISSING_EXPORT",
                path=str(path),
                message=f"Expected export '{convention}' is missing.",
            )
        )
        return ()

    value = getattr(module, convention)
    if convention == plural:
        if not isinstance(value, (tuple, list)):
            issues.append(
                WorkspaceValidationIssue(
                    level=WorkspaceIssueLevel.ERROR,
                    code="INVALID_PLURAL_EXPORT_TYPE",
                    path=str(path),
                    message=f"Export '{plural}' must be a tuple or list.",
                )
            )
            return ()
        return tuple(value)
    return (value,)


def _resolve_auto_export_convention(
    module: ModuleType,
    singular: str,
    plural: str,
    path: Path,
    issues: list[WorkspaceValidationIssue],
) -> str | None:
    has_singular = hasattr(module, singular)
    has_plural = hasattr(module, plural)
    if has_singular and has_plural:
        issues.append(
            WorkspaceValidationIssue(
                level=WorkspaceIssueLevel.ERROR,
                code="AMBIGUOUS_EXPORT",
                path=str(path),
                message=f"Use either '{singular}' or '{plural}', not both.",
            )
        )
        return None
    if has_plural:
        return plural
    if has_singular:
        return singular
    issues.append(
        WorkspaceValidationIssue(
            level=WorkspaceIssueLevel.ERROR,
            code="MISSING_EXPORT",
            path=str(path),
            message=f"Expected export '{singular}' or '{plural}'.",
        )
    )
    return None


def _check_catalog_conflicts(
    catalog: EmbodiedCatalog,
    staged_assets: list[_StagedAsset],
    report: WorkspaceLoadReport,
) -> WorkspaceLoadReport:
    issues = list(report.issues)
    for asset in staged_assets:
        if _is_id_present_in_catalog(catalog, asset):
            issues.append(
                WorkspaceValidationIssue(
                    level=WorkspaceIssueLevel.ERROR,
                    code="CATALOG_ID_CONFLICT",
                    path=str(asset.path),
                    message=(
                        f"{asset.kind.value} id '{asset.asset_id}' already exists in the active catalog."
                    ),
                )
            )
    return WorkspaceLoadReport(
        root=report.root,
        schema_version=report.schema_version,
        loaded_counts=report.loaded_counts,
        issues=tuple(issues),
    )


def _is_id_present_in_catalog(catalog: EmbodiedCatalog, asset: _StagedAsset) -> bool:
    try:
        if asset.kind == WorkspaceAssetKind.ROBOT:
            catalog.robots.get(asset.asset_id)
            return True
        if asset.kind == WorkspaceAssetKind.SENSOR:
            catalog.sensors.get(asset.asset_id)
            return True
        if asset.kind == WorkspaceAssetKind.ASSEMBLY:
            catalog.assemblies.get(asset.asset_id)
            return True
        if asset.kind == WorkspaceAssetKind.ADAPTER:
            catalog.adapters.get(asset.asset_id)
            return True
        if asset.kind == WorkspaceAssetKind.DEPLOYMENT:
            catalog.deployments.get(asset.asset_id)
            return True
        if asset.kind == WorkspaceAssetKind.WORLD:
            catalog.simulators.get_world(asset.asset_id)
            return True
        if asset.kind == WorkspaceAssetKind.SCENARIO:
            catalog.simulators.get_scenario(asset.asset_id)
            return True
    except KeyError:
        return False
    return False


def _register_staged_asset(catalog: EmbodiedCatalog, asset: _StagedAsset) -> None:
    if asset.kind == WorkspaceAssetKind.ROBOT:
        catalog.robots.register(asset.value)
        return
    if asset.kind == WorkspaceAssetKind.SENSOR:
        catalog.sensors.register(asset.value)
        return
    if asset.kind == WorkspaceAssetKind.ASSEMBLY:
        catalog.assemblies.register(asset.value)
        return
    if asset.kind == WorkspaceAssetKind.ADAPTER:
        catalog.adapters.register(asset.value)
        return
    if asset.kind == WorkspaceAssetKind.DEPLOYMENT:
        catalog.deployments.register(asset.value)
        return
    if asset.kind == WorkspaceAssetKind.WORLD:
        catalog.simulators.register_world(asset.value)
        return
    if asset.kind == WorkspaceAssetKind.SCENARIO:
        catalog.simulators.register_scenario(asset.value)
        return
    raise ValueError(f"Unsupported workspace asset kind '{asset.kind.value}'.")


def _read_asset_id(item: object) -> str | None:
    value = getattr(item, "id", None)
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized or None


def _try_load_module(path: Path, issues: list[WorkspaceValidationIssue]) -> ModuleType | None:
    try:
        return _load_module(path)
    except Exception as exc:  # pragma: no cover - defensive loader guard.
        issues.append(
            WorkspaceValidationIssue(
                level=WorkspaceIssueLevel.ERROR,
                code="IMPORT_ERROR",
                path=str(path),
                message=f"Could not import module: {exc}",
            )
        )
        return None


def _format_workspace_errors(report: WorkspaceLoadReport) -> str:
    errors = [issue for issue in report.issues if issue.level == WorkspaceIssueLevel.ERROR]
    lines = [f"Workspace asset validation failed for '{report.root}':"]
    for issue in errors:
        lines.append(f"- [{issue.code}] {issue.path}: {issue.message}")
    return "\n".join(lines)


def _load_module(path: Path) -> ModuleType:
    module_name = "roboclaw_workspace_" + "_".join(path.with_suffix("").parts[-6:])
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load workspace module from '{path}'.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
