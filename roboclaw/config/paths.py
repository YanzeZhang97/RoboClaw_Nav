"""Runtime path helpers derived from the active config context."""

from __future__ import annotations

import os
from pathlib import Path

from roboclaw.config.loader import get_config_path
from roboclaw.utils.helpers import ensure_dir

WORKSPACE_PATH_ENV = "ROBOCLAW_WORKSPACE_PATH"
_current_workspace_path: Path | None = None


def set_workspace_path(path: Path | None) -> None:
    """Set the active runtime workspace path override."""
    global _current_workspace_path
    _current_workspace_path = path


def get_data_dir() -> Path:
    """Return the instance-level runtime data directory."""
    return ensure_dir(get_config_path().parent)


def get_runtime_subdir(name: str) -> Path:
    """Return a named runtime subdirectory under the instance data dir."""
    return ensure_dir(get_data_dir() / name)


def get_media_dir(channel: str | None = None) -> Path:
    """Return the media directory, optionally namespaced per channel."""
    base = get_runtime_subdir("media")
    return ensure_dir(base / channel) if channel else base


def get_cron_dir() -> Path:
    """Return the cron storage directory."""
    return get_runtime_subdir("cron")


def get_logs_dir() -> Path:
    """Return the logs directory."""
    return get_runtime_subdir("logs")


def get_workspace_path(workspace: str | None = None) -> Path:
    """Resolve and ensure the agent workspace path."""
    env_path = os.environ.get(WORKSPACE_PATH_ENV)
    if _current_workspace_path is not None:
        path = _current_workspace_path.expanduser()
    elif env_path:
        path = Path(env_path).expanduser()
    elif workspace:
        path = Path(workspace).expanduser()
    else:
        path = Path.home() / ".roboclaw" / "workspace"
    return ensure_dir(path)


def get_cli_history_path() -> Path:
    """Return the shared CLI history file path."""
    return Path.home() / ".roboclaw" / "history" / "cli_history"


def get_bridge_install_dir() -> Path:
    """Return the shared WhatsApp bridge installation directory."""
    return Path.home() / ".roboclaw" / "bridge"


def get_legacy_sessions_dir() -> Path:
    """Return the legacy global session directory used for migration fallback."""
    return Path.home() / ".roboclaw" / "sessions"
