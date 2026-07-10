"""Domain dataclasses — the shapes the toolkit passes around and serializes."""

from dataclasses import dataclass, field


@dataclass
class Usage:
    """Token accounting for one agent run, from the SDK's usage events.

    Only `tokens` is a standard metric (agentskills.io); the skill lists are a
    small extension used for the trigger signal.
    """
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    models: list = field(default_factory=list)
    invoked_skills: list = field(default_factory=list)    # from skill.invoked
    loaded_skills: list = field(default_factory=list)      # from session.skills_loaded

    @property
    def total_tokens(self):
        # Full throughput incl. cache, so the with/without delta reflects the
        # context cost the skill's text adds.
        return (self.input_tokens + self.output_tokens
                + self.cache_read_tokens + self.cache_write_tokens)

    def to_dict(self):
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cache_read_tokens": self.cache_read_tokens,
            "cache_write_tokens": self.cache_write_tokens,
            "total_tokens": self.total_tokens,
            "models": self.models,
            "invoked_skills": self.invoked_skills,
            "loaded_skills": self.loaded_skills,
        }
