import hashlib
import json
import os
import re
import shutil
from pathlib import Path

DEFAULT_EXCLUDES = {
    ".git", "target", "src_generated", "node_modules", ".idea", ".settings",
}

MAX_FILE_BYTES = 16_000
MAX_BUNDLE_BYTES = 120_000

DEFAULT_TIMEOUT = 900

PACKAGE_DIR = Path(__file__).resolve().parent      # evals/skill_eval
EVALS_DIR = PACKAGE_DIR.parent                      # evals
REPO_ROOT = EVALS_DIR.parent                        # repo root


def resolve_repo_root(override=None):
    return Path(override).resolve() if override else REPO_ROOT


def resolve_skill_dir(repo_root, skill):
    p = Path(skill) if (os.sep in skill or "/" in skill) else repo_root / skill
    return p.resolve()


def resolve_workspace(skill_dir, override=None):
    return (Path(override).resolve() if override
            else skill_dir.parent / f"{skill_dir.name}-workspace")


def default_fixtures_dir(repo_root):
    return repo_root / "evals" / "fixtures"


# --- JSON IO ----------------------------------------------------------------

def read_json(path):
    return json.loads(Path(path).read_text())


def write_json(path, obj, indent=2):
    Path(path).write_text(json.dumps(obj, indent=indent))


# --- Text helpers -----------------------------------------------------------

def slugify(text, maxlen=48):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return (s[:maxlen] or "eval").strip("-")


def eval_dir_name(eid, slug):
    """Directory name for one eval's artifacts — id first so distinct cases
    whose names/prompts slugify the same never collide and overwrite."""
    return f"eval-{eid}-{slug}"


# --- Filesystem -------------------------------------------------------------

def iter_files(root, excludes):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in excludes]
        for name in filenames:
            p = Path(dirpath) / name
            yield p, p.relative_to(root)


def snapshot_hashes(root, excludes):
    """Map relative-path -> content hash for every file under root."""
    result = {}
    if not root.exists():
        return result
    for abspath, relpath in iter_files(root, excludes):
        try:
            result[str(relpath)] = hashlib.sha256(abspath.read_bytes()).hexdigest()
        except OSError:
            pass
    return result


def copy_tree_filtered(src, dst, excludes):
    dst.mkdir(parents=True, exist_ok=True)
    for abspath, relpath in iter_files(src, excludes):
        target = dst / relpath
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(abspath, target)


def collect_changed_files(workspace, baseline, excludes):
    """Return sorted (relpath, text) for files created/modified vs the baseline
    hash map."""
    changed = []
    for abspath, relpath in iter_files(workspace, excludes):
        rel = str(relpath)
        try:
            h = hashlib.sha256(abspath.read_bytes()).hexdigest()
        except OSError:
            continue
        if baseline.get(rel) == h:
            continue
        try:
            text = abspath.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        changed.append((rel, text))
    changed.sort(key=lambda t: t[0])
    return changed
