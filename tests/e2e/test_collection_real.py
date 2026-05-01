from __future__ import annotations

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
import pytest

pytestmark = pytest.mark.hardware


def _required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        pytest.skip(f"{name} is required for hardware collection E2E")
    return value


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _request(client: httpx.Client, method: str, path: str, token: str, **kwargs: Any) -> Any:
    response = client.request(method, path, headers=_headers(token), **kwargs)
    response.raise_for_status()
    return response.json()


def test_real_collection_publish_claim_start_save_finish() -> None:
    base_url = _required_env("ROBOCLAW_E2E_BASE_URL").rstrip("/")
    admin_token = _required_env("EVO_DATA_DEV_ADMIN_TOKEN")
    collector_token = _required_env("EVO_DATA_DEV_COLLECTOR_TOKEN")
    collector_phone = _required_env("EVO_DATA_DEV_COLLECTOR_PHONE")
    record_seconds = float(os.environ.get("ROBOCLAW_E2E_RECORD_SECONDS", "3"))
    dataset_root = Path(os.environ.get(
        "ROBOCLAW_DATASETS_ROOT",
        str(Path.home() / ".roboclaw" / "workspace" / "embodied" / "datasets"),
    )).expanduser()

    stamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    target_date = datetime.now().date().isoformat()
    task_name = f"hardware-e2e-{stamp}"

    with httpx.Client(base_url=base_url, timeout=30.0) as client:
        task = _request(
            client,
            "POST",
            "/api/collection/admin/tasks",
            admin_token,
            json={
                "name": task_name,
                "description": "hardware e2e",
                "task_prompt": "record a short hardware validation episode",
                "num_episodes": 1,
                "fps": 20,
                "episode_time_s": max(1, int(record_seconds)),
                "reset_time_s": 0,
                "use_cameras": True,
                "arms": os.environ.get("ROBOCLAW_E2E_ARMS", ""),
                "dataset_prefix": "hardware_e2e",
                "is_active": True,
            },
        )
        assignment = _request(
            client,
            "POST",
            "/api/collection/admin/assignments",
            admin_token,
            json={
                "phone": collector_phone,
                "task_id": task["id"],
                "target_date": target_date,
                "target_seconds": 60,
                "is_active": True,
            },
        )

        assignments = _request(
            client,
            "GET",
            f"/api/collection/assignments?target_date={target_date}",
            collector_token,
        )
        assert any(item["id"] == assignment["id"] for item in assignments)

        started = _request(
            client,
            "POST",
            "/api/collection/runs/start",
            collector_token,
            json={"assignment_id": assignment["id"]},
        )
        dataset_name = started["dataset_name"]
        time.sleep(record_seconds)
        _request(client, "POST", "/api/record/episode/save", collector_token)
        time.sleep(1.0)
        stopped = _request(client, "POST", "/api/collection/runs/stop", collector_token)
        assert stopped["status"] == "finished"

        progress = _request(
            client,
            "GET",
            f"/api/collection/admin/progress?target_date={target_date}",
            admin_token,
        )
        matched = next(item for item in progress if item["id"] == assignment["id"])
        assert matched["completed_seconds"] > 0

    info_path = dataset_root / "local" / dataset_name / "meta" / "info.json"
    assert info_path.is_file()
    info = json.loads(info_path.read_text(encoding="utf-8"))
    assert info["total_frames"] > 0
