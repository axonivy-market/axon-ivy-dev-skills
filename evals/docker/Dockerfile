# Agent sandbox for the skill-eval harness (the default, official runner).
#
# Each task/judge run gets a fresh container that can only see:
#   /workspace  — the run's fixture copy (rw)
#   /skills/*   — the skill under test (ro, with-skill runs only)
#   /io         — job.json in, result.json out
# Nothing else from the host is reachable, so the without-skill baseline
# cannot "discover" skill sources (hard version of the temp-dir isolation).
#
# Build:  docker build -t skill-eval-agent evals/docker
# Auth:   the harness passes GH_TOKEN into the container — a PAT of a
#         Copilot-licensed account (host login does not carry over).

FROM node:22-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-venv ca-certificates git \
    && rm -rf /var/lib/apt/lists/*

# Copilot CLI (spawned by the SDK) + the Python SDK the runner drives.
RUN npm install -g @github/copilot
RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir github-copilot-sdk

COPY agent_runner.py /opt/agent_runner.py

WORKDIR /workspace
ENTRYPOINT ["/opt/venv/bin/python", "/opt/agent_runner.py"]
