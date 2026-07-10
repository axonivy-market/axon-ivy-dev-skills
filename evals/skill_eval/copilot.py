"""GitHub Copilot adapter (SDK-backed) — the only provider-specific module.

Drives the official `github-copilot-sdk`: runs the task/judge in a session and
returns typed usage — official token counts and which skills loaded/fired.

Requires `github-copilot-sdk` (Python 3.11+) in the running interpreter. The
import is lazy, so package import and `--dry-run` work without it; a real run
without it fails with an install hint.
"""

import asyncio
import time

from .schemas import Usage


def _require_sdk():
    try:
        import copilot as sdk
    except ImportError:
        raise SystemExit(
            "This harness needs the 'github-copilot-sdk' package (Python 3.11+). "
            "Install it, e.g.:\n"
            "  python3 -m venv .venv && .venv/bin/python -m pip install github-copilot-sdk\n"
            "then run the harness with that interpreter.")
    return sdk


def _event(ev):
    t = getattr(ev, "type", None)
    return str(getattr(t, "value", t)), getattr(ev, "data", None)


async def _run_session(prompt, cwd, *, model, timeout, skill_dir):
    """Run one prompt in an SDK session; return (text, Usage)."""
    sdk = _require_sdk()
    events = []

    def on_event(ev):
        events.append(_event(ev))

    kwargs = dict(
        model=model or None,
        on_permission_request=sdk.PermissionHandler.approve_all,
        working_directory=str(cwd),
        on_event=on_event,
        include_sub_agent_streaming_events=True,
    )
    if skill_dir:
        kwargs.update(enable_skills=True, skill_directories=[str(skill_dir)])
    else:
        kwargs.update(enable_skills=False)

    async with sdk.CopilotClient(working_directory=str(cwd),
                                 use_logged_in_user=True) as client:
        async with await client.create_session(**kwargs) as session:
            await session.send_and_wait(prompt, timeout=timeout)

    u = Usage()
    text_parts, models, invoked, loaded = [], set(), set(), []
    for t, d in events:
        if t == "assistant.usage":
            u.input_tokens += getattr(d, "input_tokens", 0) or 0
            u.output_tokens += getattr(d, "output_tokens", 0) or 0
            u.cache_read_tokens += getattr(d, "cache_read_tokens", 0) or 0
            u.cache_write_tokens += getattr(d, "cache_write_tokens", 0) or 0
            if getattr(d, "model", None):
                models.add(d.model)
        elif t == "assistant.message":
            c = getattr(d, "content", None)
            if c:
                text_parts.append(c)
        elif t == "skill.invoked":
            n = getattr(d, "name", None) or getattr(d, "skill", None)
            if n:
                invoked.add(n)
        elif t == "session.skills_loaded":
            for s in getattr(d, "skills", []) or []:
                nm = getattr(s, "name", None)
                if nm:
                    loaded.append(nm)
    u.models = sorted(models)
    u.invoked_skills = sorted(invoked)
    u.loaded_skills = loaded
    return "\n".join(text_parts), u


def run_task(prompt, cwd, *, skill_dir, model, timeout, dry_run):
    """Run the task (skill loaded via skill_directories if skill_dir given).
    Returns (text, stderr, returncode, duration_ms, Usage|None, invocation)."""
    invocation = f"[sdk] model={model} skills={[str(skill_dir)] if skill_dir else []}"
    if dry_run:
        print(f"    DRY-RUN {invocation} cwd={cwd}")
        return "", "", 0, 0, None, invocation
    start = time.monotonic()
    try:
        text, usage = asyncio.run(
            _run_session(prompt, cwd, model=model, timeout=timeout, skill_dir=skill_dir))
        rc = 0
    except Exception as e:  # noqa: BLE001 — surface any SDK failure into the record
        text, usage, rc = f"[sdk error] {e}", None, 1
    return text, "", rc, int((time.monotonic() - start) * 1000), usage, invocation


def run_judge(prompt, cwd, *, model, timeout, dry_run):
    """Run the judge (no skills); return (text, returncode)."""
    if dry_run:
        return "", 0
    try:
        text, _ = asyncio.run(
            _run_session(prompt, cwd, model=model, timeout=timeout, skill_dir=None))
        return text, 0
    except Exception as e:  # noqa: BLE001
        return f"[sdk error] {e}", 1
