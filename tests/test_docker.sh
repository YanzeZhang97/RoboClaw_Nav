#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.." || exit 1

INSTANCE_NAME="${INSTANCE_NAME:-docker-test}"
SCRIPT_DIR="$(pwd)/scripts/docker"
# shellcheck source=../scripts/docker/common.sh
source "${SCRIPT_DIR}/common.sh"

echo "=== Building Docker image ==="
"${SCRIPT_DIR}/build-image.sh" "$INSTANCE_NAME"

echo ""
echo "=== Bootstrapping instance ==="
"${SCRIPT_DIR}/bootstrap-instance.sh" "$INSTANCE_NAME"

echo ""
echo "=== Running 'roboclaw status' ==="
STATUS_OUTPUT=$("${SCRIPT_DIR}/run-task.sh" "$INSTANCE_NAME" status 2>&1) || true

echo "$STATUS_OUTPUT"

echo ""
echo "=== Validating output ==="
PASS=true

check() {
    if echo "$STATUS_OUTPUT" | grep -q "$1"; then
        echo "  PASS: found '$1'"
    else
        echo "  FAIL: missing '$1'"
        PASS=false
    fi
}

check "RoboClaw Status"
check "Config:"
check "Workspace:"

echo ""
if $PASS; then
    echo "=== All checks passed ==="
else
    echo "=== Some checks FAILED ==="
    exit 1
fi

# Cleanup
echo ""
echo "=== Cleanup ==="
docker rm -f "$(dev_container_name "$INSTANCE_NAME")" 2>/dev/null || true
docker rmi -f "$(image_ref "$INSTANCE_NAME")" 2>/dev/null || true
rm -rf "$(instance_dir "$INSTANCE_NAME")"
echo "Done."
