#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
ROBOCLAW_DOCKER_HOME="${ROBOCLAW_DOCKER_HOME:-${HOME}/.roboclaw-docker}"

die() {
  echo "error: $*" >&2
  exit 1
}

require_instance() {
  local instance="${1:-}"
  [ -n "${instance}" ] || die "instance name is required"
  [[ "${instance}" =~ ^[A-Za-z0-9._-]+$ ]] || die "invalid instance name: ${instance}"
}

instance_dir() {
  local instance="${1}"
  printf '%s\n' "${ROBOCLAW_DOCKER_HOME}/instances/${instance}"
}

image_ref() {
  local instance="${1}"
  printf 'roboclaw:%s-%s\n' "${instance}" "$(current_commit_short)"
}

current_commit_short() {
  git -C "${REPO_ROOT}" rev-parse --short HEAD
}

require_clean_git() {
  if [ -n "$(git -C "${REPO_ROOT}" status --porcelain)" ]; then
    die "git worktree is dirty; commit or stash changes before building the Docker image"
  fi
}

compose_project() {
  local instance="${1}"
  printf 'roboclaw-%s\n' "${instance}"
}

dev_container_name() {
  local instance="${1}"
  printf 'roboclaw-dev-%s\n' "${instance}"
}

find_proxy_port() {
  local ss_output line
  ss_output="$(ss -ltnpH 2>/dev/null || true)"
  if [ -z "${ss_output}" ]; then
    return 1
  fi

  if printf '%s\n' "${ss_output}" | awk '/verge-mihomo/ && $4 ~ /127\.0\.0\.1:7897$/ { print "7897"; exit }' | grep -q .; then
    printf '7897\n'
    return 0
  fi

  local port
  for port in 7897 7890 7891 20170 7895 7898 7899; do
    if printf '%s\n' "${ss_output}" | awk -v port="${port}" '$4 ~ ("127\\.0\\.0\\.1:" port "$") { found=1 } END { exit(found ? 0 : 1) }'; then
      printf '%s\n' "${port}"
      return 0
    fi
  done

  line="$(printf '%s\n' "${ss_output}" | grep -E '127\.0\.0\.1:.*(verge-mihomo|clash|mihomo|sing-box|xray|v2ray|dae|hysteria)' | head -n 1 || true)"
  if [ -n "${line}" ]; then
    printf '%s\n' "${line}" | awk '{split($4, a, ":"); print a[length(a)]}'
    return 0
  fi

  return 1
}

configure_proxy_env() {
  local proxy_port="${1:-}"
  if [ -z "${proxy_port}" ]; then
    proxy_port="$(find_proxy_port || true)"
  fi
  if [ -z "${proxy_port}" ]; then
    unset HTTP_PROXY HTTPS_PROXY ALL_PROXY http_proxy https_proxy all_proxy
    return 0
  fi

  export HTTP_PROXY="http://127.0.0.1:${proxy_port}"
  export HTTPS_PROXY="http://127.0.0.1:${proxy_port}"
  export ALL_PROXY="socks5://127.0.0.1:${proxy_port}"
  export http_proxy="${HTTP_PROXY}"
  export https_proxy="${HTTPS_PROXY}"
  export all_proxy="${ALL_PROXY}"
}

ensure_image_exists() {
  local instance="${1}"
  docker image inspect "$(image_ref "${instance}")" >/dev/null 2>&1 || \
    die "image $(image_ref "${instance}") not found; run scripts/docker/build-image.sh ${instance}"
}

ensure_instance_dir() {
  local instance="${1}"
  mkdir -p \
    "$(instance_dir "${instance}")/workspace" \
    "$(instance_dir "${instance}")/home" \
    "$(instance_dir "${instance}")/home/.codex"
}

host_codex_auth_path() {
  local path="${HOME}/.codex/auth.json"
  if [ -f "${path}" ]; then
    printf '%s\n' "${path}"
  fi
}

compose_cmd() {
  local instance="${1}"
  shift
  if docker compose version >/dev/null 2>&1; then
    ROBOCLAW_IMAGE="$(image_ref "${instance}")" \
    ROBOCLAW_INSTANCE_DIR="$(instance_dir "${instance}")" \
    ROBOCLAW_UID="$(id -u)" \
    ROBOCLAW_GID="$(id -g)" \
    docker compose -f "${REPO_ROOT}/docker-compose.yml" -p "$(compose_project "${instance}")" "$@"
    return
  fi

  if command -v docker-compose >/dev/null 2>&1; then
    ROBOCLAW_IMAGE="$(image_ref "${instance}")" \
    ROBOCLAW_INSTANCE_DIR="$(instance_dir "${instance}")" \
    ROBOCLAW_UID="$(id -u)" \
    ROBOCLAW_GID="$(id -g)" \
    docker-compose -f "${REPO_ROOT}/docker-compose.yml" -p "$(compose_project "${instance}")" "$@"
    return
  fi

  die "neither 'docker compose' nor 'docker-compose' is available"
}
