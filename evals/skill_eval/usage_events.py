from .schemas import Usage


def parse_session_events(events):
    """Derive assistant text and Usage from normalized event dicts."""
    usage = Usage()
    text_parts = []
    models, invoked, loaded = set(), set(), []

    for ev in events:
        etype = ev.get("type")
        if etype == "assistant.usage":
            usage.input_tokens += ev.get("input_tokens", 0) or 0
            usage.output_tokens += ev.get("output_tokens", 0) or 0
            usage.cache_read_tokens += ev.get("cache_read_tokens", 0) or 0
            usage.cache_write_tokens += ev.get("cache_write_tokens", 0) or 0
            if ev.get("model"):
                models.add(ev["model"])
        elif etype == "assistant.message":
            if ev.get("content"):
                text_parts.append(ev["content"])
        elif etype == "skill.invoked":
            if ev.get("skill"):
                invoked.add(ev["skill"])
        elif etype == "session.skills_loaded":
            loaded.extend(ev.get("skills") or [])

    usage.models = sorted(models)
    usage.invoked_skills = sorted(invoked)
    usage.loaded_skills = loaded
    return "\n".join(text_parts), usage
