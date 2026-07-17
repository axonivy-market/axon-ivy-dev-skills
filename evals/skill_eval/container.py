import json
import os
import shutil
import subprocess
import tempfile
import time
import uuid
from pathlib import Path

from .schemas import JudgeRunResult, TaskRunResult
from .usage_events import parse_session_events

IMAGE = os.environ.get("SKILL_EVAL_IMAGE", "skill-eval-agent")
DOCKER_OVERHEAD_SECS = 120  # container start/stop on top of the task timeout


def preflight():
    if not shutil.which("docker"):
        raise SystemExit(
            "docker CLI not found — the harness runs all agents in Docker. "
            "Install Docker first.")
    if subprocess.run(["docker", "info"], capture_output=True).returncode != 0:
        raise SystemExit(
            "docker daemon not running — start Docker Desktop (or dockerd), "
            "then retry.")
    if subprocess.run(["docker", "image", "inspect", IMAGE],
                      capture_output=True).returncode != 0:
        raise SystemExit(
            f"docker image '{IMAGE}' not found — build it once:\n"
            f"  docker build -t {IMAGE} evals/docker")
    _token()  # raises with its own hint if no PAT is set


def _token():
    tok = os.environ.get("COPILOT_GH_TOKEN") or os.environ.get("GH_TOKEN")
    if not tok:
        raise SystemExit(
            "--container needs COPILOT_GH_TOKEN (or GH_TOKEN) set to a PAT of a "
            "Copilot-licensed account — the container cannot reuse the host login.")
    return tok


def _run_in_container(prompt, cwd, *, model, timeout, skill_dirs, workspace_ro=False):
    with tempfile.TemporaryDirectory(prefix="skill-eval-io-") as io_dir:
        mounts = {}  # container path -> host path
        for d in skill_dirs:
            cpath = f"/skills/{Path(d).name}"
            mounts.setdefault(cpath, Path(d).resolve())
        container_skill_dirs = list(mounts)
        Path(io_dir, "job.json").write_text(json.dumps(
            {"prompt": prompt, "model": model, "timeout": timeout,
             "skill_dirs": container_skill_dirs}))

        mode = ":ro" if workspace_ro else ""
        name = f"skill-eval-{uuid.uuid4().hex[:12]}"
        cmd = ["docker", "run", "--rm", "--name", name, "-e", "GH_TOKEN",
               "-v", f"{Path(cwd).resolve()}:/workspace{mode}",
               "-v", f"{Path(io_dir).resolve()}:/io"]
        for cpath, hpath in mounts.items():
            cmd += ["-v", f"{hpath}:{cpath}:ro"]
        cmd.append(IMAGE)

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True,
                                  timeout=timeout + DOCKER_OVERHEAD_SECS,
                                  env=dict(os.environ, GH_TOKEN=_token()))
        finally:
            subprocess.run(["docker", "rm", "-f", name], capture_output=True)
        result_file = Path(io_dir, "result.json")
        result = json.loads(result_file.read_text()) if result_file.exists() else {}
        if proc.returncode != 0 or "events" not in result:
            raise RuntimeError(
                f"container run failed (rc={proc.returncode}): "
                f"{result.get('error') or proc.stderr[-2000:]}")
        return result


def run_task(prompt, cwd, *, skill_dirs, model, timeout):
    """Run the task in a sandbox container with all of `skill_dirs` mounted (the
    skill under test first, then any `depends_on` skills). Empty = baseline.
    Returns a TaskRunResult."""
    invocation = (f"[docker:{IMAGE}] model={model} "
                  f"skills={[f'/skills/{Path(d).name}' for d in skill_dirs]}")
    start = time.monotonic()
    try:
        result = _run_in_container(prompt, cwd, model=model, timeout=timeout,
                                   skill_dirs=skill_dirs)
        text, usage = parse_session_events(result.get("events", []))
        rc = 0
    except Exception as e:  # noqa: BLE001 — surface any docker/SDK failure into the record
        text, usage, rc = f"[container error] {e}", None, 1
    return TaskRunResult(
        text=text,
        stderr="",
        returncode=rc,
        duration_ms=int((time.monotonic() - start) * 1000),
        usage=usage,
        invocation=invocation,
    )


def run_judge(prompt, cwd, *, model, timeout):
    """Run the judge (no skills, workspace read-only); return a JudgeRunResult."""
    try:
        result = _run_in_container(prompt, cwd, model=model, timeout=timeout,
                                   skill_dirs=[], workspace_ro=True)
        text, _ = parse_session_events(result.get("events", []))
        return JudgeRunResult(text=text, returncode=0)
    except Exception as e:  # noqa: BLE001
        return JudgeRunResult(text=f"[container error] {e}", returncode=1)
