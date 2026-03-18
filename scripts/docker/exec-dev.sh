#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=./common.sh
source "${SCRIPT_DIR}/common.sh"

INSTANCE="${1:-}"
require_instance "${INSTANCE}"
ensure_image_exists "${INSTANCE}"
ensure_instance_dir "${INSTANCE}"
configure_proxy_env

"${SCRIPT_DIR}/start-dev.sh" "${INSTANCE}" >/dev/null
docker exec -it "$(dev_container_name "${INSTANCE}")" /bin/sh
