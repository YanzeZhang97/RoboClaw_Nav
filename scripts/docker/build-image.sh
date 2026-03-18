#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=./common.sh
source "${SCRIPT_DIR}/common.sh"

INSTANCE="${1:-}"
require_instance "${INSTANCE}"
configure_proxy_env

build_args=()
for key in HTTP_PROXY HTTPS_PROXY ALL_PROXY http_proxy https_proxy all_proxy; do
  value="${!key:-}"
  if [ -n "${value}" ]; then
    build_args+=(--build-arg "${key}=${value}")
  fi
done

docker build \
  --network=host \
  "${build_args[@]}" \
  -t "$(image_ref "${INSTANCE}")" \
  "${REPO_ROOT}"
