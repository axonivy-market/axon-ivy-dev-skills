---
name: ivy-market-import
description: Import an Axon Ivy Marketplace item into the codebase. Optionally adds it as a dependency to one or more projects. Asks for the item name, version, and target projects.
---

# Import Axon Ivy Marketplace Item

## Item-specific instructions

Some marketplace items have additional setup requirements. Before proceeding with Step 1, check if a `<item-name>.md` file exists in this skill's folder and follow its instructions first.

**Known items with extra steps:**
- `smart-workflow` → see [smart-workflow.md](smart-workflow.md)

---

## Step 1 — Collect inputs

### Item name

If the user provided an exact item name (e.g. `smart-workflow`), use it directly.

If the user described a **feature or capability** instead of a name (e.g. "I want AI task routing" or "something for document signing"):

1. Fetch the list of repositories in the `axonivy-market` GitHub org using the API:
   ```
   https://api.github.com/orgs/axonivy-market/repos?per_page=100&page=1
   ```
   Repeat with `page=2`, `page=3`, etc. until all repos are fetched (stop when a page returns fewer than 100 results).

2. For each repo, read its `name` and `description` fields from the API response.

3. Score each repo against the user's described feature — look for keyword and semantic matches in the name and description. Select the top 3–5 candidates.

4. For each candidate, fetch `https://raw.githubusercontent.com/axonivy-market/<repo>/master/README.md` (first 50 lines) to get a human-readable description. Most repo `description` fields are null — the README is the reliable source.

5. Present the matches to the user:
   > "I found these marketplace items that may match what you're looking for:
   > - **`smart-workflow`** — Let AI Agent elements drive your dynamic processes
   > - **`doc-factory`** — Document generation and template management
   >
   > Which one would you like to import? Or none of the above?"

6. Wait for the user to confirm before proceeding.

### Version

Do **not** ask the user for the version unless none can be detected. Resolve it automatically:

1. Glob for `*/pom.xml` in the workspace root subfolders.
2. Read the first one found. Check if the item is already listed under `<dependencies>` — if so, use the version already there.
3. If not already a dependency, use the `<version>` from the `<parent>` block — this is the Axon Ivy engine version the projects are built against (e.g. `14.0.0-SNAPSHOT`).

Only ask the user if no pom.xml exists at all.

### Maven coordinates — groupId lookup (do NOT ask the user)

**Run this in parallel with the version detection above** to save time.

Always resolve the groupId automatically by fetching the item's `pom.xml` from GitHub:

```
https://raw.githubusercontent.com/axonivy-market/<item-name>/master/pom.xml
```

- Read the root `<groupId>` from that file.
- If the root `pom.xml` has no `<groupId>` (it inherits from parent), check the first child module listed in `<modules>` and fetch its `pom.xml` to get the `<groupId>`.
- If `master` returns 404, try `main` branch.

> **Do not guess** and **do not ask the user**. Always look it up from the GitHub source repo.

The **artifactId** is the item slug (e.g. `smart-workflow`) and the **type** is `iar`.

### Target projects

Check whether the dependency is already present in the target project's `pom.xml`:
- **Already present** → skip Step 4 entirely (no pom.xml changes needed).
- **Not present and user specified a project** → add it in Step 4.
- **Not present and no project specified** → download only, no pom.xml changes.

If unclear whether a project should depend on the item, ask:
> "Should any project in this workspace depend on `<item-name>`? If so, which one(s)? Or should I just add it to the codebase without linking it to any project?"

---

## Step 2 — Fix Maven repository configuration (if needed)

The global Maven settings at `/c/apache-maven-3.9.8/conf/settings.xml` includes an always-active profile that adds `axonivy-releases-repo` → `https://repo.axonivy.io` which is **unreachable** (Unknown host). This will cause all downloads to fail.

**Check** whether `~/.m2/settings.xml` already has the mirror fix:
```bash
grep -q "axonivy-releases-mirror" ~/.m2/settings.xml 2>/dev/null && echo "mirror ok" || echo "mirror missing"
```

**If missing**, create `~/.m2/settings.xml` with these mirrors:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<settings xmlns="http://maven.apache.org/SETTINGS/1.2.0"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.2.0 https://maven.apache.org/xsd/settings-1.2.0.xsd">
  <mirrors>
    <mirror>
      <id>maven-default-http-blocker</id>
      <mirrorOf>external:http:*</mirrorOf>
      <name>Pseudo repository to mirror external repositories initially using HTTP.</name>
      <url>http://0.0.0.0/</url>
      <blocked>true</blocked>
    </mirror>
    <mirror>
      <id>axonivy-releases-mirror</id>
      <mirrorOf>axonivy-releases-repo</mirrorOf>
      <name>Mirror axonivy-releases-repo to maven.axonivy.com</name>
      <url>https://maven.axonivy.com</url>
    </mirror>
    <mirror>
      <id>nexus-axonivy-mirror</id>
      <mirrorOf>nexus-axonivy-repo,snapshots-nexus-axonivy-repo</mirrorOf>
      <name>Mirror nexus axonivy repos to maven.axonivy.com</name>
      <url>https://maven.axonivy.com</url>
    </mirror>
  </mirrors>
</settings>
```

---

## Step 3 — Download the marketplace item

Use the Maven dependency plugin to download the IAR into the workspace.

**Important path quoting:** If the workspace path contains spaces, quote both the `-DoutputDirectory` value and the `-f` path.

```bash
mvn dependency:copy \
  -Dartifact=<groupId>:<artifactId>:<version>:iar \
  "-DoutputDirectory=<absolute-path-to-workspace>/marketplace-dependencies" \
  -Dmdep.useRepositoryLayout=false \
  --no-transfer-progress \
  -f "<absolute-path-to-workspace>/<any-existing-project>/pom.xml"
```

> - Use an **absolute path** for `-DoutputDirectory` (relative paths can silently resolve to the wrong location).
> - Use an existing project's `pom.xml` via `-f` so Maven inherits the Axon Ivy repository configuration (`https://maven.axonivy.com`).
> - The `-f` path must also be absolute and quoted if it contains spaces.

**After the command completes**, always verify the file was actually copied:

```bash
ls "c:/work/micro-app project/new-micro-app/marketplace-dependencies/"
```

### If BUILD SUCCESS but no file is copied (SNAPSHOT artifacts built locally)

When the artifact version is a `SNAPSHOT` that was built locally (not published to `maven.axonivy.com`), `dependency:copy` exits with BUILD SUCCESS but copies nothing. If the folder is empty or missing after a successful build, copy directly from the local Maven cache:

```bash
cp ~/.m2/repository/<groupId-path>/<artifactId>/<version>/<artifactId>-<version>.iar \
   "<workspace>/marketplace-dependencies/"
```

Where `<groupId-path>` is the groupId with dots replaced by slashes (e.g. `com/axonivy/utils/ai`).

---

## Step 4 — Add as dependency (conditional)

Skip this step if:
- No target project was specified, **or**
- The dependency is already present in the target project's `pom.xml` (checked in Step 1).

For each target project, add the dependency inside the `<dependencies>` block of `<project-name>/pom.xml`, after the existing `ivy-api` dependency:

```xml
<dependency>
  <groupId><resolved-groupId></groupId>
  <artifactId><item-name></artifactId>
  <version><version></version>
  <type>iar</type>
</dependency>
```

---

## Step 5 — Report

Summarize what was done:
- Path of the downloaded IAR file.
- Which projects (if any) had their `pom.xml` updated (or note if it was already present).
- Remind the user: the `marketplace-dependencies/` folder should be committed to version control so all team members have the item available without needing to re-download it.
