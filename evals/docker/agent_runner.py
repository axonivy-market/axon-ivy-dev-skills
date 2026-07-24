import asyncio
import json
import sys
from pathlib import Path

import copilot as sdk


def _normalize_event(ev):
    t = getattr(ev, "type", None)
    etype = str(getattr(t, "value", t))
    data = getattr(ev, "data", None)

    out = {"type": etype}
    if etype == "assistant.usage":
        out.update({
            "input_tokens": getattr(data, "input_tokens", 0) or 0,
            "output_tokens": getattr(data, "output_tokens", 0) or 0,
            "cache_read_tokens": getattr(data, "cache_read_tokens", 0) or 0,
            "cache_write_tokens": getattr(data, "cache_write_tokens", 0) or 0,
            "model": getattr(data, "model", None),
        })
    elif etype == "assistant.message":
        out["content"] = getattr(data, "content", None)
    elif etype == "skill.invoked":
        out["skill"] = getattr(data, "name", None) or getattr(data, "skill", None)
    elif etype == "session.skills_loaded":
        skills = []
        for s in getattr(data, "skills", []) or []:
            name = getattr(s, "name", None)
            if name:
                skills.append(name)
        out["skills"] = skills
    return out


async def run(job):
    events = []

    kwargs = dict(
        model=job.get("model") or None,
        on_permission_request=sdk.PermissionHandler.approve_all,
        working_directory="/workspace",
        on_event=lambda ev: events.append(_normalize_event(ev)),
        include_sub_agent_streaming_events=True,
    )
    skill_dirs = job.get("skill_dirs") or []
    if skill_dirs:
        kwargs.update(enable_skills=True, skill_directories=skill_dirs)
    else:
        kwargs.update(enable_skills=False)

    async with sdk.CopilotClient(working_directory="/workspace") as client:
        async with await client.create_session(**kwargs) as session:
            await session.send_and_wait(job["prompt"], timeout=job.get("timeout"))
    return {"events": events}


def main():
    job = json.loads(Path("/io/job.json").read_text())
    try:
        result = asyncio.run(run(job))
    except Exception as e:  # noqa: BLE001 — ship the failure out to the harness
        Path("/io/result.json").write_text(json.dumps({"error": str(e)}))
        sys.exit(1)
    Path("/io/result.json").write_text(json.dumps(result))


if __name__ == "__main__":
    main()
