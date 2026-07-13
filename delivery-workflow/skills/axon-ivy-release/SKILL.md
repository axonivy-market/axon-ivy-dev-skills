---
name: axon-ivy-release
description: Cut a new release version of an Axon Ivy project. Creates a release branch off `develop`, bumps Maven versions, optionally adds a Liquibase folder for schema changes, builds, generates the site report, and tags the release commit. Use whenever the user asks to "release", "cut a release", or "bump the version" of an Ivy project.
---

# Axon Ivy Release

Walk the user through cutting a new release of an Axon Ivy Maven project. Follow the steps in order — each step has a confirmation gate so the user can correct course before destructive operations.

## When to Use

- "Cut release 2.0.17"
- "Bump the version and tag a release"
- "Prepare a release branch"

## When NOT to Use

- For deploying an already-tagged release to an engine — that's a deploy concern, not a release-cut concern.
- For SNAPSHOT publishes during development — those are continuous, not release events.

---

## Step 1 — Confirm preconditions

Before anything else, run these checks and report each as PASS / FAIL:

1. **Working tree clean** — `git status --porcelain` returns nothing. If FAIL, stop and tell the user to commit or stash.
2. **On `develop`** — the release branch must be cut from the latest `develop`. If FAIL, ask whether to switch (`git checkout develop && git pull --ff-only`) or abort.
3. **Up to date with origin** — `git fetch origin && git status -uno` reports "up to date". If FAIL, pull first.
4. **Maven build healthy** — does `mvn -v` work? Does the project root have a `pom.xml`?

If any precondition fails, stop and surface the failure. Do not proceed to step 2.

## Step 2 — Detect the current version

Find the project's current version:

1. Use Glob to locate all `pom.xml` files in the project.
2. Read the root / aggregator pom (the one whose `<artifactId>` matches the project name, or the one without a `<parent>` pointing inside the repo).
3. Extract the `<version>` element. Examples:

```xml
<version>2.0.16</version>             <!-- final release -->
<version>2.0.17-SNAPSHOT</version>    <!-- in-development -->
```

Strip any `-SNAPSHOT` suffix. Report the detected current version to the user.

## Step 3 — Propose the new version

Two cases, depending on what's already in the pom:

**Case A — pom version ends in `-SNAPSHOT`.** Strip the suffix; that's the new release.

```
2.0.17-SNAPSHOT → 2.0.17
```

**Case B — pom version is final (no `-SNAPSHOT`).** Compare against the latest tag:

- If the pom version is **greater** than the latest tag, the team has already bumped develop in preparation. Use the pom version as-is.

  ```
  pom: 2.0.18, latest tag: v2.0.17 → release 2.0.18
  ```

- If the pom version **equals** the latest tag (already-released state), increment the patch by 1.

  ```
  pom: 2.0.16, latest tag: v2.0.16 → release 2.0.17
  ```

To find the latest tag, run `git tag -l "v*" | sort -V | tail -1`. If the user wants a minor or major bump, they will say so — handle it as an override.

Present the proposal and wait for confirmation:

```
Current version: 2.0.16
Proposed new version: 2.0.17
Release branch:  release/version-2.0.17
Tag:             v2.0.17

Confirm or override.
```

Branch name format: `release/version-<NEW>` (matches existing repo convention; check `git branch -r | grep release/` and follow whatever pattern is already there).

Tag format: `v<NEW>` is the safest default. If the project has prior tags, follow the existing convention — `git tag -l | head` to check.

## Step 4 — Create the release branch

After user confirms:

```
git checkout -b release/version-<NEW> origin/develop
```

Verify the branch was created and is checked out.

## Step 5 — Bump Maven versions

Use the Versions plugin — it handles multi-module projects, parent references, and dependency-management entries correctly:

```
mvn versions:set -DnewVersion=<NEW> -DgenerateBackupPoms=false
```

Verify by re-reading the root `pom.xml` `<version>` and confirming it changed. Spot-check one or two child `pom.xml` files if the project is multi-module.

If `versions:set` is not available (very rare), fall back to manual edits — but only on `<version>` elements that match the OLD version string, never on parent `<version>` of external dependencies.

## Step 6 — Decide on Liquibase folder

Ask the user: **"Does this release ship any database schema changes?"**

- **No** → skip to step 7.
- **Yes** → create a new folder under `<project>/liquibase/script/` named after the new version using the project's existing folder convention. If folders are packed-version integers (`20016`, `20017`), the new one is `20017` — see the `axon-ivy-liquibase` skill for the folder/file format and the `axon-ivy-liquibase-verify` skill for the post-edit checklist.

Do not prefill SQL files; the user adds those as schema work happens.

## Step 7 — Build

Run a clean build to catch issues introduced by the version bump:

```
mvn clean install
```

If the build fails, surface the error and stop. Do not commit a release branch with a broken build.

## Step 8 — Generate the site report

```
mvn site
```

After it completes, point the user at the generated site (typically `target/site/index.html` for a single-module project, or each module's `target/site/` for a multi-module). Wait for them to review the docs before tagging — this is the user's checkpoint to spot anything off in the release artifacts.

## Step 9 — Commit and tag

After the user signs off on the build + site:

```
git add -A
git commit -m "Release version <NEW>"
git tag -a v<NEW> -m "Release version <NEW>"
```

Show `git log -n 2 --decorate` to confirm the commit and tag landed.

## Step 10 — Hand-off

Print the post-release checklist for the user. Do **not** push or merge automatically — those are the user's call.

```
Release v<NEW> prepared on branch release/version-<NEW>.

To publish:
  git push -u origin release/version-<NEW>
  git push origin v<NEW>

After the release is verified in production, merge the release branch back to develop:
  git checkout develop
  git pull --ff-only
  git merge --no-ff release/version-<NEW>
  git push
```

Stop here. The skill's job ends at the local commit + tag.

---

## Critical Rules

### 1. Never push or tag automatically

Pushing a tag is irreversible (without rewriting history publicly). All push commands are printed for the user to run, never executed by the skill.

### 2. Never proceed past a failed precondition

If `git status` shows uncommitted work, the build fails, or the user is on the wrong branch — stop. Releasing on top of dirty state poisons the tag and confuses everyone.

### 3. Use `mvn versions:set` over manual edits

In a multi-module project, manual `<version>` edits routinely miss parent references or dependency-management entries, leaving an inconsistent state. The Versions plugin is the safe path.

### 4. One release branch at a time

Before creating `release/version-<NEW>`, check whether an unmerged release branch already exists (`git branch -a | grep release/`). If so, ask the user whether to abandon it or finish it first. Two open release branches lead to merge chaos.

### 5. The Liquibase folder is optional

Don't create an empty Liquibase folder "just in case". Empty folders are noise and an empty folder still gets `<includeAll>`'d at runtime, which is fine but pointless. Only create one when there is real schema work.

### 6. Keep the version monotonic

The new version must be lexicographically greater than every existing tag. Run `git tag -l | sort -V | tail -3` to spot-check before proposing the new version.

## Common Pitfalls

- **`mvn versions:set` leaves backup `pom.xml.versionsBackup` files** — pass `-DgenerateBackupPoms=false` to suppress them. Otherwise you have to clean them up before `git add`.
- **`-SNAPSHOT` not stripped** — if the current version is `2.0.17-SNAPSHOT` and you "bump to 2.0.18", you skipped a release. The release version is the SNAPSHOT minus the suffix (`2.0.17`); the *next* development cycle then becomes `2.0.18-SNAPSHOT`.
- **Wrong branch in `mvn versions:set`** — running it on `develop` by mistake bumps versions on the dev line. Always verify the branch immediately before this step.
- **Tag pushed before merge** — pushing the tag before the release is verified means you cannot withdraw it gracefully. The skill prints the push commands separately so the user can sequence them deliberately.
- **`mvn site` on a fresh checkout fails** — sometimes site generation needs `mvn install` first because reports reference compiled classes. The order in this skill (install before site) avoids that.

## Use Together With

- `axon-ivy-liquibase` — when the release ships schema changes, for the new folder layout
- `axon-ivy-liquibase-verify` — to validate any new changesets before tagging
