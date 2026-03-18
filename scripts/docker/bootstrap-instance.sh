#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=./common.sh
source "${SCRIPT_DIR}/common.sh"

INSTANCE="${1:-}"
require_instance "${INSTANCE}"
ensure_image_exists "${INSTANCE}"
ensure_instance_dir "${INSTANCE}"

INSTANCE_DIR="$(instance_dir "${INSTANCE}")"
INSTANCE_CONFIG="${INSTANCE_DIR}/config.json"
HOST_CONFIG="${HOME}/.roboclaw/config.json"

if [ ! -f "${INSTANCE_CONFIG}" ]; then
  if [ -f "${HOST_CONFIG}" ]; then
    cp "${HOST_CONFIG}" "${INSTANCE_CONFIG}"
  else
    printf '{}\n' > "${INSTANCE_CONFIG}"
  fi
fi

configure_proxy_env

docker run --rm \
  --network host \
  --user "$(id -u):$(id -g)" \
  -e HOME=/roboclaw-instance/home \
  -e ROBOCLAW_CONFIG_PATH=/roboclaw-instance/config.json \
  -e ROBOCLAW_WORKSPACE_PATH=/roboclaw-instance/workspace \
  -e HTTP_PROXY="${HTTP_PROXY:-}" \
  -e HTTPS_PROXY="${HTTPS_PROXY:-}" \
  -e ALL_PROXY="${ALL_PROXY:-}" \
  -e http_proxy="${http_proxy:-}" \
  -e https_proxy="${https_proxy:-}" \
  -e all_proxy="${all_proxy:-}" \
  -v "${INSTANCE_DIR}:/roboclaw-instance" \
  --entrypoint python \
  "$(image_ref "${INSTANCE}")" \
  -c 'from roboclaw.config.loader import get_config_path, load_config, save_config; from roboclaw.config.paths import get_workspace_path; from roboclaw.config.schema import Config; from roboclaw.utils.helpers import sync_workspace_templates; path = get_config_path(); cfg = load_config(path) if path.exists() else Config(); save_config(cfg, path); workspace = get_workspace_path(); workspace.mkdir(parents=True, exist_ok=True); sync_workspace_templates(workspace)'
