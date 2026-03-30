# Skill Overview

All available skills and their purpose. Skills folder: `.claude/skill/`

Each skill has a `SKILL.md` file in its folder with full instructions.

| Intent | Skill | Description |
|---|---|---|
| requirement | `axon-ivy-requirements-creation` | Generate structured requirements and ordered story files from vague user input |
| develop | `axon-ivy-init` | Scaffold a new Axon Ivy project from template (asks for name, groupId, artifactId) |
| develop | `axon-ivy-implement-story` | Implement a story file end-to-end, mapping each part to the correct skill |
| develop | `axon-ivy-workflow-guide` | Step-by-step guide for building complete workflow processes — use first when creating new workflows |
| develop | `axon-ivy-process` | Create, edit, review, and fix `.p.json` workflow process files and IvyScript |
| develop | `axon-ivy-data` | Create and manage `.d.json` data class files |
| develop | `axon-ivy-java-data` | Java model classes, enums, DTOs, and persistence patterns (Ivy.repo() or JPA/SQL) |
| develop | `axon-ivy-repository` | Create repository classes — dispatches between Ivy.repo() (default) and JPA/SQL |
| develop | `axon-ivy-html` | HTML dialog rules: PrimeFaces, PrimeFlex, CSS, JS, and Ivy components |
| develop | `axon-ivy-cms` | Create and manage CMS multi-language YAML files, binary content, and Portal CMS overrides |
| develop | `axon-ivy-smart-workflow` | Build AI-powered data extraction using AgenticProcessCall |
| develop | `axon-ivy-variable-config` | Manage `variables.yaml` config files |
| develop | `axon-ivy-user-role-config` | Manage `roles.yaml` and `users.yaml` config files |
| develop | `axon-ivy-custom-fields` | Define custom fields in `custom-fields.yaml` for tasks, cases, and process starts |
| develop | `ivy-market-import` | Import an Axon Ivy Marketplace item and add it as a dependency to `pom.xml` |
| review | `axon-ivy-process-verify` | Verify `.p.json` files for structural and IvyScript errors |
| review | `axon-ivy-cms-verify` | Verify `cms_*.yaml` files for common errors — run after `axon-ivy-cms` |
| review | `axon-ivy-primefaces-verify` | Verify PrimeFaces column widths, table layout, AJAX updates, and rendering pitfalls |
| review | `axon-ivy-verify-story` | Verify story acceptance criteria and UI behavior (field interactions, validations) |
| review | `review-java` | Review Java code for Clean Architecture, Ports and Adapters, and SOLID principles |
| review | `review-javascript` | Review JavaScript code for clean architecture, audit compliance, DRY, and file organization |
| test | `axon-ivy-test` | Write and update process tests |
| orchestrate | `axon-ivy` | Master router — detects intent and orchestrates all paths using the skills above |
