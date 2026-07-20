import os
import tempfile
from pathlib import Path
import subprocess

DEFAULT_BRANCH = "master"


def _default_git_runner(args, cwd):
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def _remove_worktree(git_runner, repo_root, worktree_dir):
    git_runner(["worktree", "remove", "--force", str(worktree_dir)], repo_root)


def resolve_previous_version(repo_root, skill_rel_path, *, git_runner=None):
    git_runner = git_runner or _default_git_runner

    remote_ref = f"refs/remotes/origin/{DEFAULT_BRANCH}"
    git_runner(["fetch", "--depth=1", "origin",
                f"+refs/heads/{DEFAULT_BRANCH}:{remote_ref}"], repo_root)

    worktree_dir = Path(tempfile.mkdtemp(
        prefix="skill-eval-baseline-", dir=os.environ.get("RUNNER_TEMP")))
    git_runner(["worktree", "add", "--detach", str(worktree_dir), remote_ref], repo_root)

    skill_dir = worktree_dir / skill_rel_path
    if not (skill_dir / "SKILL.md").exists():
        _remove_worktree(git_runner, repo_root, worktree_dir)
        return None

    sha = git_runner(["rev-parse", "--short", remote_ref], repo_root)
    desc = f"{DEFAULT_BRANCH}@{sha}"

    def cleanup():
        _remove_worktree(git_runner, repo_root, worktree_dir)

    return skill_dir, desc, cleanup