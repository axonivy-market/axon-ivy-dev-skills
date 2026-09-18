# Multiple Stories

Use this guidance when the user asks to implement more than one story.

## Build a Dependency Graph

Read all requested stories and identify their dependencies before implementing anything.

Do not assume story number defines execution order.

Example:

```text
              ┌─> Entity + Repository
Data Model ───┤
              ├─> Smart Workflow
              │
              └─> UI Components
                        ↓
                   Tag Library
                        ↓
                      Forms
                        ↓
                  Main Process
```

Stories with no dependency on each other may be implemented in parallel.

Stories that depend on another story must wait until the required dependency is complete.

## Execution Rules

* Start with stories whose dependencies are already satisfied.
* Run independent stories in parallel when useful.
* When a story completes, unblock dependent stories.
* Never allow parallel work to modify the same shared file.
* Re-evaluate the dependency graph after each completed batch.

Typical shared files requiring coordination include:

* CMS files
* tag libraries
* configuration files
* shared registries
* central process files

## Missing Dependencies

If a requested story depends on another requested story, automatically schedule the dependency first.

If a required dependency is not included in the requested stories and its expected artifacts do not exist, mark the dependent story as blocked.

Do not create temporary implementations to bypass missing dependencies.

## Verification

Verify each story individually after implementation.

After all related stories are complete, run integration/build verification to detect problems between their artifacts.
