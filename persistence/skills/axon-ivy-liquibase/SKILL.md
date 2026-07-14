---
name: axon-ivy-liquibase
description: Conventions and patterns for Liquibase changelogs in an Axon Ivy project. Use whenever you create, edit, or order schema migrations under `<project>/liquibase/`. Pairs with `axon-ivy-liquibase-verify` (post-edit checklist).
---

# Axon Ivy + Liquibase

Production schema in Axon Ivy projects is owned by Liquibase, not by Hibernate's `hbm2ddl`. This skill documents the directory layout, master changelog wiring, and the formatted-SQL change conventions used in Ivy projects.

## When to Use

- Adding a new column / table / index
- Reorganising data that goes with a schema change (a backfill)
- Bumping the schema for a new release version
- Resolving a "checksum mismatch" or out-of-order changeset error

## When NOT to Use

- For application-level data inserts that are not part of a schema migration (e.g. user-driven data) → use the application code path, not Liquibase.
- For tweaking the test database schema only → the `_TESTING` persistence unit can use `hibernate.hbm2ddl.auto=update`; you do not need a Liquibase entry.

## Directory Layout

```
<project>/
└── liquibase/
    ├── changelog-master.xml          ← entry point
    ├── liquibase.properties          ← url, driver, changeLogFile (local dev)
    └── script/
        ├── 10101/                    ← release version 1.01.01
        │   ├── 01_drop_table.sql
        │   ├── 02_create_table.sql
        │   └── 03_value_list_item.sql
        ├── 10102/
        │   └── 01_add_index.sql
        └── 20018/                    ← release version 2.00.18
            └── 01_alter_station.sql
```

Conventions:

- **Folder names are release version numbers** packed into a flat integer (`10101` = 1.01.01, `20018` = 2.00.18). Liquibase orders folders alphabetically, so version-based names give a stable execution order. Pick the version that matches the release the change ships in.
- **File names are two-digit ordinal + topic** (`02_create_table.sql`). Two digits give you headroom for late additions without renumbering.
- **One topic per file**. Multiple changesets per file are allowed when they share a topic, but split unrelated changes.

## Master changelog

Keep `changelog-master.xml` minimal — let `<includeAll>` pick up new folders automatically:

```xml
<?xml version="1.0"?>
<databaseChangeLog
    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-latest.xsd">
  <includeAll path="script" relativeToChangelogFile="true" />
</databaseChangeLog>
```

You almost never edit this file. Adding a new release folder or a new SQL file under `script/` is enough.

## Formatted-SQL changesets

Every `.sql` file starts with the `liquibase formatted sql` header and one `--changeset` block per logical change:

```sql
-- liquibase formatted sql

--changeset bolt:10101-0201
CREATE TABLE STATION (
  ID                VARCHAR2(32) NOT NULL,
  VERSION           NUMBER(10,0),
  CREATEDBYUSERNAME VARCHAR2(255),
  CREATEDDATE       DATE,
  …
  CONSTRAINT PK_STATION PRIMARY KEY (ID)
);

--changeset bolt:10101-0202
CREATE INDEX IX_STATION_TECHPLACE ON STATION (TECHNICALPLACE);
```

Conventions:

- **Author tag** — pick one team-wide tag (`bolt:` in KFWG) and stick to it. Mixing authors in the same project makes the `DATABASECHANGELOG` table noisy.
- **Changeset id** — `<folder>-<NNNN>`. The folder prefix anchors the change to a release; the four-digit suffix orders changes inside the release. Never reuse an id.
- **Never edit a changeset after it has been deployed.** Liquibase computes a checksum at first run; editing the SQL changes the checksum and breaks every existing environment. Add a new changeset that fixes the issue.

### Skipping pre-existing statements

Use `--ignoreLines:start` / `--ignoreLines:end` to comment out statements that are only intended for fresh-install or local-dev contexts (e.g. drop-everything-and-recreate blocks at the start of the bootstrap script). These markers are Liquibase's own — they are still valid SQL comments in Oracle.

```sql
--ignoreLines:start
DROP TABLE "STATION" CASCADE CONSTRAINTS PURGE;
--ignoreLines:end
```

## Rollback

Add a `--rollback` block under each destructive changeset (DROP, ALTER, RENAME). For pure additive DDL (`CREATE TABLE`, `CREATE INDEX`), Liquibase auto-generates rollback; you can omit it.

```sql
--changeset bolt:20018-0101
ALTER TABLE STATION ADD (DISTRICT_CODE VARCHAR2(20));

--rollback ALTER TABLE STATION DROP COLUMN DISTRICT_CODE;
```

For multi-statement rollbacks, use:

```sql
--rollback ALTER TABLE STATION DROP COLUMN DISTRICT_CODE;
--rollback DROP INDEX IX_STATION_DISTRICT;
```

## Datasource alignment

`liquibase.properties` (used for local dev only — CI usually passes the URL via the Maven plugin) must target the **same database** the application connects to via `persistence.xml`:

```properties
url=jdbc:oracle:thin:@//localhost:1521/XEPDB1
driver=oracle.jdbc.OracleDriver
changeLogFile=liquibase/changelog-master.xml
```

In production / staging, the URL comes from the deployment pipeline, not from this file. Treat `liquibase.properties` as a developer convenience.

## Critical Rules

### 1. Never modify a deployed changeset

Once a changeset has run anywhere (CI, staging, prod), it is immutable. Add a new changeset to fix mistakes. The exception is local dev databases that can be wiped — but the moment the change is in `develop`, treat it as deployed.

### 2. Big-table NOT NULL needs three changesets

Adding a `NOT NULL` column on a table with millions of rows must be split:

1. Add the column nullable.
2. Backfill existing rows in batches (separate changeset, or scripted outside Liquibase).
3. Set `NOT NULL`.

A single `ADD COLUMN … NOT NULL` blocks the whole table during the deploy.

### 3. One author tag per project

Mixing `bolt:`, `alice:`, `bob:` makes the `DATABASECHANGELOG` table hard to query. Pick one (often a service or team name) and use it for every change.

### 4. Schema is the source of truth, entities follow

If `persistence.xml` enables `hibernate.hbm2ddl.auto=update` for prod, that is a bug. Schema goes through Liquibase, entities reflect the schema.

### 5. Initial-data inserts go in dedicated files

Lookup data (value list items, role catalogues) belongs in `*_value_list_item.sql` or similar — not mixed into a `CREATE TABLE` script. Future migrations may need to update lookup data without retouching DDL files.

## Pitfalls

- **Renaming a column** — Liquibase's `RENAME COLUMN` works, but Hibernate's metamodel cache breaks until the engine restarts. Plan a deployment window.
- **Reordering folders by editing names** — every changeset id is keyed by `(filepath, id, author)`. Renaming the folder makes Liquibase think the change is new and re-runs it.
- **`includeAll` ordering** — alphabetical. `10200` runs before `2018` (string compare). The packed-version-number convention avoids this, but **never** introduce a non-numeric folder.
- **Empty `--changeset`** — Liquibase silently records it as run; the next person to add real SQL after it has to bump the id.

## Use Together With

- `axon-ivy-liquibase-verify` — post-edit checklist
- `axon-ivy-jpa` — entity changes that motivate the migration
- `axon-ivy-persistence-utils` — DAO changes that follow the migration
