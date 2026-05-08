---
name: axon-ivy-jpa
description: Rules and patterns for plain JPA (`@Entity`, `EntityManager`, `persistence.xml`) inside an Axon Ivy project, with the Hibernate provider. Use whenever Java code in `src/` defines `@Entity` classes, configures persistence units, or chooses fetch / cascade strategies. Pairs with `axon-ivy-persistence-utils` when the project uses the helper library on top.
---

# Axon Ivy + JPA (Hibernate)

Axon Ivy projects typically run JPA via Hibernate against an Oracle datasource registered with the Ivy engine. This skill covers the parts of JPA that are **Ivy-specific or bite people in Ivy projects** — generic JPA tutorials are everywhere else.

## When to Use

- Adding a new `@Entity`
- Editing `persistence.xml`
- Choosing fetch (`LAZY` vs `EAGER`) or cascade types
- Writing `equals` / `hashCode` on an entity
- Resolving `LazyInitializationException` or process-state serialization errors

## When NOT to Use

- For DAOs that extend `AuditableIdDAO` → use `axon-ivy-persistence-utils`.
- For schema changes → use `axon-ivy-liquibase` (Hibernate's `hbm2ddl` is **not** the source of truth in production Ivy projects).
- For `Ivy.repo()` (Ivy's own document store) → use `axon-ivy-repository`.

## File Locations

| Type | Location |
|------|----------|
| Entity | `src/<package>/entities/` |
| `persistence.xml` | `<project>/config/persistence.xml` |
| Generated metamodel (`Entity_.java`) | Same package as the entity, generated build output |

## `persistence.xml` template

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<persistence xmlns="http://xmlns.jcp.org/xml/ns/persistence" version="2.2">
  <persistence-unit name="MYAPP">
    <non-jta-data-source>myapp</non-jta-data-source>
    <properties>
      <property name="hibernate.show_sql" value="false"/>
      <property name="hibernate.format_sql" value="false"/>
      <property name="hibernate.enable_lazy_load_no_trans" value="true"/>
      <property name="hibernate.id.new_generator_mappings" value="false"/>
    </properties>
  </persistence-unit>
</persistence>
```

Notes on each property:

- `non-jta-data-source` — name of the datasource configured in the Ivy engine (`databases.yaml` / Engine Cockpit). It is **not** a JNDI name; Ivy resolves it through its own datasource manager.
- `hibernate.enable_lazy_load_no_trans=true` — required because Ivy releases the EntityManager at the end of each call. Without it, every UI page that touches a lazy collection throws `LazyInitializationException`. Trade-off: it opens a temporary session per access, which can mask N+1 problems.
- `hibernate.id.new_generator_mappings=false` — kept for backwards compatibility on existing projects so existing `@GeneratedValue` strategies do not change shape. **New projects** can drop this.
- No `<class>` elements — entities are auto-discovered from the IAR classpath.

For test isolation, add a second persistence unit (e.g. `MYAPP_TESTING`) pointing at a separate datasource and add `<property name="hibernate.hbm2ddl.auto" value="update"/>` so the test schema follows entity changes automatically.

## Critical Rules

### 1. Every entity implements `Serializable`

Entities are stored in Axon Ivy process data and cross step boundaries. The Ivy engine serializes process data between steps, so every `@Entity` must be `Serializable` with a `serialVersionUID`. Most projects extend a common base class (e.g. `AuditableIdEntity`) that already implements it.

```java
@Entity
@Table(name = "Customer")
public class Customer implements Serializable {
  private static final long serialVersionUID = 1L;
  // …
}
```

### 2. Lazy collections + Ivy process state = footgun

`@OneToMany(fetch = LAZY)` works inside a Hibernate session, but Ivy may serialize the entity into process state **after** the session has closed. Three safe options, in order of preference:

1. **Fetch eagerly inside the DAO** with a JPQL `JOIN FETCH` or Criteria `fetch(...)` and return a detached entity that already has the collection populated.
2. **Don't put the entity into process data.** Map to a DTO at the service boundary.
3. **Mark the field `@Transient`** if it is only needed inside one screen and can be re-fetched.

`@OneToMany(fetch = EAGER)` looks like the easy fix but causes Cartesian-product queries when an entity has more than one eager collection. Use it only for small, bounded child sets.

### 3. `equals` / `hashCode` rules

Auto-generated `@Id` values are `null` until the entity is persisted. If `equals` / `hashCode` use `id`, two unsaved entities collide. Two acceptable patterns:

- **Inherit from a base class** (e.g. `AuditableIdEntity`) that handles identity uniformly — preferred when one exists.
- **Use a natural business key** (`technicalPlace`, `customerNumber`, …) when one exists and is immutable.

Do **not** override `equals` based on a generated `Long`/`String` `@Id` without handling the null case.

### 4. `@Transient` for non-persisted derived fields

Use `@Transient` for fields computed at runtime (totals, formatted strings, UI flags). They are still serialized into process state — only JPA ignores them.

### 5. Enums use `@Enumerated(EnumType.STRING)`

Default ordinal mapping breaks the moment someone reorders the enum. Always:

```java
@Enumerated(EnumType.STRING)
private TelecontrolDeviceType deviceType;
```

### 6. Schema is owned by Liquibase, not Hibernate

In production persistence units, never set `hibernate.hbm2ddl.auto` to anything other than `none` (or omit it). Schema changes go through Liquibase changelogs. The `_TESTING` unit may use `update` because the test database is throwaway.

### 7. Datasource must match the Liquibase target

The datasource referenced in `persistence.xml` and the `url` in `liquibase.properties` must point at the same database. Easy mistake when a developer adds a new persistence unit but forgets to update the Liquibase config.

## Common Patterns

### Eager fetch via Criteria

```java
try (CriteriaQueryContext<Order> query = initializeQuery()) {
  query.r.fetch(Order_.lineItems, JoinType.LEFT);
  query.where(query.c.equal(query.r.get(Order_.id), orderId));
  return findByCriteria(query).stream().findFirst().orElse(null);
}
```

### Soft-delete column

When the project uses `AuditableIdEntity`, soft-delete is already handled by `flaggedDeletedDate`. For other base classes, add a `Date deletedAt` column and filter via `@Where(clause = "deleted_at IS NULL")` (Hibernate-specific) or an explicit predicate in every query.

## Pitfalls

- **`LazyInitializationException` despite `enable_lazy_load_no_trans=true`** — happens when the entity is serialized (e.g. into a Gson payload) before the lazy access. Force the load (`Hibernate.initialize(...)`) before serialization, or map to a DTO.
- **`@OneToMany` + `CascadeType.ALL` + bidirectional ref** — removing one side does not always remove the other. Add `orphanRemoval = true` if children should not exist standalone.
- **Generated metamodel out of date** — `Entity_.java` is regenerated by the build. If a field reference does not compile, run `mvn clean compile` to refresh the metamodel.
- **Multiple persistence units sharing entities** — fine, but every unit must list the same Hibernate properties. Mismatched `enable_lazy_load_no_trans` between prod and test causes "works on my machine" bugs.

## Use Together With

- `axon-ivy-persistence-utils` — when the project uses the helper layer
- `axon-ivy-liquibase` — schema migrations that go with every entity change
- `axon-ivy-java-data` — POJO patterns for DTOs you map entities into
