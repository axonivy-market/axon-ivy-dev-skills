---
name: axon-ivy-init
description: Scaffold a new Axon Ivy project. Asks for project name, group ID, and artifact ID, then generates the project from the bundled template in this skill folder.
---

# Initialize Axon Ivy Project

## Step 1 — Collect inputs

Ask the user for the following. Validate that each value contains no spaces:

- **Project name** — root folder name (e.g. `my-new-app`)
- **Group ID** — Maven groupId (e.g. `com.example`)
- **Artifact ID** — Maven artifactId (e.g. `my-new-app`)

Derive from the project name:
- `namespace` = hyphens → dots (e.g. `my-new-app` → `my.new.app`)
- `namespacePath` = hyphens → slashes (e.g. `my-new-app` → `my/new/app`)

Generate a random 16-character hex string for `__PROCESS_ID__`.

## Step 2 — Read the bundled template

Read every file under `.claude/skill/axon-ivy-init/template/` — these are the exact files to create.
Skip `src_generated/` and `target/` — they are build outputs, not source files.

## Step 3 — Scaffold the new project

Create `<project-name>/` at the workspace root by copying every template file, applying these substitutions to both **file paths** and **file contents**:

| Placeholder | Replace with |
|-------------|--------------|
| `__PROJECT_NAME__` | project name |
| `__GROUP_ID__` | group ID |
| `__ARTIFACT_ID__` | artifact ID |
| `__NAMESPACE__` | namespace (dot-separated) |
| `__NAMESPACE_PATH__` | namespacePath (slash-separated) |
| `__PROCESS_ID__` | generated hex ID |

## Step 4 — Create `.ivyproject`

> **Why manually:** `.ivyproject` is intentionally excluded from the template because its presence triggers automatic deployment to the Axon Ivy Designer server when the project folder is opened. Create it only after the project is fully scaffolded.

Create `<project-name>/.ivyproject` with this content:

```
name=<project-name>
version=140011
```

- `name` must match the project folder name exactly (the artifact ID value is fine here if they differ — use the project name).
- `version` is the Ivy Designer format version — keep it as `140011` unless the user specifies otherwise.

Inform the user: **opening this project in Axon Ivy Designer will now register and potentially deploy it to the connected server. Only add `.ivyproject` when ready to work with Designer.**

## Step 5 — Build the project

Run from the project root:

```
mvn clean install
```

Inform the user that the project built successfully.

## Step 6 — Report

Print the created file tree to the user.
