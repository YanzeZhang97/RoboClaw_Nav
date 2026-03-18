# Docker Workflow

RoboClaw supports two Docker workflows on a remote Linux host:

- Long-lived development containers that stay alive until you stop them.
- One-shot task containers that run a single RoboClaw command and exit.

All container state lives under `~/.roboclaw-docker/instances/<instance>/`.
Each instance has its own `config.json`, `workspace/`, and runtime data derived from the config directory.
By default, bootstrap copies `~/.roboclaw/config.json` into the instance once, then the container state diverges from the host.

## Scripts

Build an image for one instance:

```bash
./scripts/docker/build-image.sh devbox
```

Create or refresh the isolated instance state:

```bash
./scripts/docker/bootstrap-instance.sh devbox
```

Start a long-lived container and keep it around:

```bash
./scripts/docker/start-dev.sh devbox
./scripts/docker/exec-dev.sh devbox
```

Run a one-shot RoboClaw task:

```bash
./scripts/docker/run-task.sh devbox status
./scripts/docker/run-task.sh devbox onboard
./scripts/docker/run-task.sh devbox agent -m hello --no-markdown
```

## Networking and proxies

The scripts discover a local proxy port on the remote host and export proxy variables automatically when possible.

- Docker builds always use `--network=host`.
- Runtime containers always use host networking.
- This is required when the remote host exposes its VPN or proxy on `127.0.0.1`.
- When the remote host has `~/.codex/auth.json`, the dev and task workflows mount it read-only into the container so `roboclaw agent` can reuse host authentication without copying credentials into the isolated instance state.
