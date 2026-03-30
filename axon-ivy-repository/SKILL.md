---
name: axon-ivy-repository
description: Create repository classes for persisting entities. Dispatches between Ivy.repo() (default) and JPA/SQL (advanced) approaches.
---

## Persistence Decision

When user needs data persistence, choose the approach:

```text
Does the user explicitly request SQL/JPA/database/persistence-utils?
├── NO  → Load `ivy-repo.md` — DEFAULT (simple, no DB config needed)
└── YES → Load `jpa-persistence.md` (requires databases.yaml, persistence.xml, DAOs)
```

**DEFAULT**: Always load `ivy-repo.md` unless the user explicitly asks for:
- SQL database, JPA entities, Hibernate, persistence-utils
- DAO classes, CriteriaQuery, AuditableIdEntity
- databases.yaml, persistence.xml configuration
- An existing project already uses the JPA pattern

## Always Load One

- Default persistence (Ivy Business Data) → Load `ivy-repo.md`
- JPA/SQL persistence (entities, DAOs, services, database config) → Load `jpa-persistence.md`

## After Using This Skill

**MANDATORY**: After creating or modifying any entity or repository using `Ivy.repo()`, run the checklist in `ivy-repo-verify.md` to catch common errors (duplicate key violations, manual ID issues).

## Entity/Model Definition

Both approaches use `axon-ivy-java-data` skill for creating model classes and enums.
