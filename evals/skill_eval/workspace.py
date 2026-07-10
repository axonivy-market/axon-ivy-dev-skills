"""Workspace preparation — build the initial project state a run acts on.

Provider-agnostic: copies the fixture snapshot and any extra input files into a
fresh run directory.
"""

import shutil
from pathlib import Path

from .common import DEFAULT_EXCLUDES, copy_tree_filtered


def prepare_workspace(work_dir, fixture_dir, files, skill_repo_root):
    """Wipe and rebuild the run workspace from the fixture + extra input files."""
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True)
    if fixture_dir is not None:
        copy_tree_filtered(fixture_dir, work_dir, DEFAULT_EXCLUDES)
    for f in files:
        src = (skill_repo_root / f).resolve()
        if not src.exists():
            raise FileNotFoundError(f"eval input file not found: {src}")
        dst = work_dir / Path(f).name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
