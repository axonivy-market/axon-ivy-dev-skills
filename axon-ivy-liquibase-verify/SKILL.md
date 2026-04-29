---
name: axon-ivy-liquibase-verify
description: Verification checklist for Liquibase changelogs in Axon Ivy projects. MUST be used after the `axon-ivy-liquibase` skill, or whenever a `.sql` / `.xml` file under `<project>/liquibase/` is created or modified.
---

**MANDATORY**: Run this checklist on EVERY Liquibase file touched. Read the file, then verify each applicable check below. Fix any violations before considering the task done.

## Checklist

### 1. Header — every formatted-SQL file starts with `-- liquibase formatted sql`

Without the header, Liquibase ignores the file silently and your changes never run.

```sql
-- liquibase formatted sql
```

### 2. Every change has a `--changeset author:id` line

```sql
--changeset bolt:20018-0101
```

- The author tag must match the project-wide convention (read a sibling file to confirm — typically one team tag, e.g. `bolt:`).
- The id must be **unique across the whole repository**. Convention is `<folderName>-<NNNN>` where the folder name is the version (e.g. `20018-0101`).
- An id is NEVER reused, even after the original changeset is renamed or moved.

**To confirm id uniqueness**, grep the whole `liquibase/` tree for the new id. There must be exactly one match (the file under review):

```
Grep(pattern: "<changeset-id>", path: "<project>/liquibase", output_mode: "files_with_matches")
```

If two or more files match, the id is reused — FAIL.

### 3. Destructive change → must have `--rollback`

If the changeset contains any of: `DROP TABLE`, `DROP INDEX`, `DROP CONSTRAINT`, `ALTER … DROP COLUMN`, `RENAME`, `TRUNCATE`, or `DELETE` (without a backfill plan), it MUST have a `--rollback` line covering the inverse operation.

```sql
--changeset bolt:20018-0102
ALTER TABLE STATION DROP COLUMN OLD_FLAG;
--rollback ALTER TABLE STATION ADD (OLD_FLAG VARCHAR2(1));
```

Pure additive DDL (`CREATE TABLE`, `CREATE INDEX`, `ADD COLUMN` nullable) may rely on Liquibase's auto-generated rollback and omit the line.

### 4. NOT NULL on existing column → must be split

Adding `NOT NULL` to a column on a table that already has rows in production is a three-step migration:

1. `ALTER TABLE … ADD (col …)`  ← nullable
2. Backfill (`UPDATE …`) in a separate changeset
3. `ALTER TABLE … MODIFY (col NOT NULL)`

If you see a single changeset doing `ADD … NOT NULL` on a non-empty table, FAIL the check and split it.

Exception: a brand-new table created in the same release.

### 5. Folder name follows the version-number convention

Liquibase runs `<includeAll>` folders alphabetically, so the folder name dictates execution order. New folders must:

- be all digits (e.g. `20019`),
- be **lexicographically greater** than every existing folder (so they run after them),
- correspond to the release version the change ships in.

If the new folder is `2019` (4 digits) while existing folders are `20018` (5 digits), `2019` sorts BEFORE `20018` — this is a bug. Pad to match.

### 6. File name follows `NN_topic.sql`

**Scope**: this rule applies only to files under `<project>/liquibase/script/<version>/`. Test fixtures, scratch SQL, and files outside the changelog tree are exempt.

- Two-digit ordinal prefix (`01_`, `02_`, …) for ordering inside the folder.
- Hyphen-or-underscore-separated lowercase topic.
- `.sql` extension.

```
RIGHT: 02_create_station.sql
WRONG: create_station.sql
WRONG: 2_CreateStation.sql
```

### 7. No edits to deployed changesets

Before saving, check `git log -- <file>` (or just inspect the diff). If you are modifying SQL inside an **existing** `--changeset` block whose id has already been deployed (i.e. exists in any non-feature branch), that breaks Liquibase's checksum check at startup.

The fix is to add a **new** changeset that corrects the issue, not to edit the old one.

### 8. No application data inserts in schema files

Schema files (`CREATE TABLE`, `ALTER TABLE`, etc.) should not contain `INSERT` statements for application data. Lookup data (value list items, role catalogue) belongs in dedicated files like `03_value_list_item.sql`. User-driven data does not belong in Liquibase at all.

### 9. Oracle-specific checks (if Oracle is the target DB)

Treat each sub-rule as an independent check — do not bundle.

#### 9a. `VARCHAR2`, not `VARCHAR`

Oracle reserves the right to redefine `VARCHAR` semantics. Always use `VARCHAR2`.

```
RIGHT: NAME VARCHAR2(255)
WRONG: NAME VARCHAR(255)
```

#### 9b. Identifier names ≤ 30 characters

Legacy Oracle limit; some installations still enforce it. Applies to table names, column names, index names, and constraint names.

To check, count characters of every new identifier the file introduces. Anything over 30 is a FAIL. Common offender: long composite-index names like `IX_STATION_DISTRICT_AND_TECHNICAL_PLACE_COMBINED` (47 chars).

#### 9c. `CASCADE CONSTRAINTS PURGE` only inside `--ignoreLines`

Never in a changeset that will run against prod. The pattern is reserved for the bootstrap drop-everything blocks at the top of fresh-install scripts.

```sql
--ignoreLines:start
DROP TABLE "STATION" CASCADE CONSTRAINTS PURGE;
--ignoreLines:end
```

If `CASCADE CONSTRAINTS PURGE` appears outside an `--ignoreLines` pair, FAIL.

### 10. Datasource alignment

If you added a new persistence unit in `persistence.xml`, confirm `liquibase.properties` (or the deployment Liquibase config) points at the same datasource. Mismatched targets are silent failures — the migration runs on a different database than the app uses.

### 11. `--ignoreLines:start` blocks are paired

Every `--ignoreLines:start` must have a matching `--ignoreLines:end`. Unpaired markers cause Liquibase to skip everything to the end of file.

**Mechanical check**: count occurrences of each marker in the file — they must match.

```
Grep(pattern: "--ignoreLines:start", path: "<file>", output_mode: "count")
Grep(pattern: "--ignoreLines:end",   path: "<file>", output_mode: "count")
```

If the two counts differ, FAIL.

### 12. Master changelog untouched (usually)

`changelog-master.xml` should already use `<includeAll path="script" />`. New folders / files are picked up automatically. If your change required editing `changelog-master.xml`, that is a strong signal something is off — re-evaluate.

---

## Reporting

After the checklist, give the user:

1. The list of files reviewed.
2. PASS / FAIL per check.
3. For each FAIL: the file, the line, and the fix.

Do not silently fix without reporting; the team must see what was wrong.
