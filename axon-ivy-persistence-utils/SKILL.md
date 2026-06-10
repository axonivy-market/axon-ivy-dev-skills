---
name: axon-ivy-persistence-utils
description: Rules and patterns for the `com.axonivy.utils.persistence` library — the Axon Ivy community helper around JPA. Covers `AuditableIdEntity`, `AuditableIdDAO`, `CriteriaQueryContext`, and `UpdateQueryContext`. Use whenever Java code in `src/` reads or writes data through a DAO that extends `AuditableIdDAO` or an entity that extends `AuditableIdEntity`.
---

# Axon Ivy persistence-utils

`com.axonivy.utils.persistence` is the public Axon Ivy helper that wraps JPA with auditing, soft-delete, criteria-query scaffolding, and an EntityManager-per-call lifecycle that fits the Ivy engine's threading model. Use this skill when working with code that imports from `com.axonivy.utils.persistence.*`.

## When to Use

- Creating or modifying a DAO class
- Adding or modifying an `@Entity` that participates in audit / soft-delete
- Writing a Criteria API query (`findBy...`, `searchBy...`, paged queries)
- Performing batch updates / deletes through `UpdateQueryContext`

## When NOT to Use

- For `Ivy.repo()` (Ivy's built-in repository) → use `axon-ivy-repository`.
- For raw `EntityManager`/`@PersistenceContext` JPA without the helper → use `axon-ivy-jpa`.

## File Locations

| Type | Location |
|------|----------|
| Entity | `src/<package>/entities/` |
| DAO | `src/<package>/dao/` |
| JPA metamodel (`Entity_.java`) | Generated alongside entities; do not edit by hand |
| `persistence.xml` | `<project>/config/persistence.xml` |

## Critical Rules

### 1. Entities must extend `AuditableIdEntity`

`AuditableIdEntity` provides `id` (String, generated), `version` (optimistic lock), and the audit columns (`createdByUsername`, `createdDate`, `modifiedByUsername`, `modifiedDate`, `flaggedDeletedByUsername`, `flaggedDeletedDate`). Do **not** redeclare `id` or audit fields in your entity.

**Reading audit values goes through the `Header` sub-object** — there are no direct `entity.getCreatedDate()` getters. Use `entity.getHeader().getCreatedDate()` (Java) / `#{entity.header.createdDate}` (EL), likewise `modifiedDate`, `flaggedDeletedDate`, `createdByUserName`, `modifiedByUserName`. `#{entity.createdDate}` throws `PropertyNotFoundException` at render time. (`getId()` *is* directly on the entity: `#{entity.id}`.)

```java
import com.axonivy.utils.persistence.beans.AuditableIdEntity;
import javax.persistence.Entity;
import javax.persistence.Table;

@Entity
@Table(name = "Station")
public class Station extends AuditableIdEntity {
  private static final long serialVersionUID = 1L;

  private String technicalPlace;
  private String stationName;
  // getters / setters …
}
```

`serialVersionUID = 1L` is mandatory — entity instances cross Ivy process-state serialization boundaries.

### 2. DAOs extend `AuditableIdDAO<MetaModel, Entity>`

The first type parameter is the JPA static metamodel class (`Entity_`), the second is the entity. Override `getType()` to return the entity class.

```java
import com.axonivy.utils.persistence.dao.AuditableIdDAO;
import com.axonivy.utils.persistence.dao.CriteriaQueryContext;
import javax.persistence.criteria.Predicate;

public class StationDAO extends AuditableIdDAO<Station_, Station> {

  @Override
  protected Class<Station> getType() {
    return Station.class;
  }

  public List<Station> findByStationName(String stationName) {
    try (CriteriaQueryContext<Station> query = initializeQuery()) {
      Predicate p = query.c.equal(query.r.get(Station_.stationName), stationName);
      query.where(p);
      return findByCriteria(query);
    }
  }
}
```

### 3. **Always** use try-with-resources around `CriteriaQueryContext` / `UpdateQueryContext`

Both contexts hold an EntityManager. Leaking them leaks JDBC connections under load.

```java
// RIGHT
try (CriteriaQueryContext<Station> query = initializeQuery()) {
  …
}

// WRONG — connection leak
CriteriaQueryContext<Station> query = initializeQuery();
…
```

### 4. Build predicates through `query.c` and root via `query.r`

`query.c` is the `CriteriaBuilder`, `query.r` is the `Root<Entity>`. Reference fields through the generated metamodel (`Station_.stationName`) — never through string field names. The metamodel gives you compile-time safety when the schema is renamed.

### 5. DAOs are stateless — share single instances

A common pattern is a `DaoServices` aggregator that holds one instance of every DAO as a `private static final` field. DAOs hold no state between calls; do not add instance fields.

### 6. Persistence unit name must match `persistence.xml`

Each DAO declares its persistence unit by overriding `getPersistenceUnitName()` (returns the `<persistence-unit name="…">` value). The Axon Ivy convention is one production unit per project (e.g. `KFWG`) plus an optional `_TESTING` unit pointing at a separate datasource for integration tests. Both units share the same set of `@Entity` classes via classpath auto-scan.

```java
public class StationDAO extends AuditableIdDAO<Station_, Station> {
  @Override public String getPersistenceUnitName() { return "KFWG"; }
  @Override protected Class<Station> getType() { return Station.class; }
}
```

### 7. Soft delete via `flaggedDeleted*` — do not `DELETE`

`AuditableIdDAO.delete(...)` flags the row by setting `flaggedDeletedByUserName` and `flaggedDeletedDate`, then `findAll()` and `findByCriteria()` filter them out via a Criteria predicate added in `AuditableDAO.manipulateCriteriaFactory()`. Bypassing this with raw `EntityManager.remove(...)` defeats audit.

Two sanctioned escape hatches:

- **Hard-delete a single entity** — set the transient `auditingDisabled` flag before `delete()`:

  ```java
  station.setAuditingDisabled(true);
  stationDAO.delete(station);   // physical DELETE, no audit row
  ```

  Use only with a documented reason (e.g. GDPR right-to-erasure).

- **Read soft-deleted rows** — pass a `QuerySettings` with `AuditableMarker.DELETED` (just deleted) or `AuditableMarker.ALL` (active + deleted):

  ```java
  QuerySettings<Station> settings = new QuerySettings<>();
  settings.setAuditableMarker(AuditableMarker.DELETED);
  return findAll(settings);
  ```

  Default is `AuditableMarker.ACTIVE`.

## Common Patterns

### Find with multiple predicates

```java
public List<Station> findByNewOrOldTechnicalPlace(String technicalPlace) {
  try (CriteriaQueryContext<Station> query = initializeQuery()) {
    Predicate pNew = query.c.equal(query.r.get(Station_.technicalPlace), technicalPlace);
    Predicate pOld = query.c.equal(query.r.get(Station_.oldTechnicalPlace), technicalPlace);
    query.where(query.c.or(pNew, pOld));
    return findByCriteria(query);
  }
}
```

### `IN (…)` query with batching

Oracle has a hard limit of ~1000 elements in an `IN` clause. Batch large lists:

```java
private static final int BATCH_SIZE = 50;

public List<Station> findByTechnicalPlaces(List<String> technicalPlaces) {
  List<Station> result = new ArrayList<>();
  for (int i = 0; i < technicalPlaces.size(); i += BATCH_SIZE) {
    List<String> batch = technicalPlaces.subList(i, Math.min(i + BATCH_SIZE, technicalPlaces.size()));
    try (CriteriaQueryContext<Station> query = initializeQuery()) {
      query.where(query.r.get(Station_.technicalPlace).in(batch));
      result.addAll(findByCriteria(query));
    }
  }
  return result;
}
```

### Persist or update

`AuditableIdDAO.save(entity)` covers both insert and update via JPA merge semantics. Audit fields are populated from `Ivy.session().getSessionUserName()` automatically.

```java
Station station = new Station();
station.setStationName(name);
stationDAO.save(station);   // inserts; id generated by AuditableIdEntity
```

**In a process `Script` (IvyScript), `save(...)` needs an explicit `as` cast.** `GenericDAO.save(T)`
returns `T`, but IvyScript erases the generic to its bound `GenericEntity`, so
`in.station = stationDAO.save(in.station)` throws
`Cannot cast object of type …GenericEntity to type …Station`. Write the cast:
`in.station = stationDAO.save(in.station) as Station;`. (Plain Java in `src/` resolves the type
argument — no cast needed there. Only Designer/IvyScript hits this; `mvn` does not.)

## Pitfalls

- **Returning a managed entity to the Ivy process layer.** Once the `CriteriaQueryContext` closes, the entity is detached. Loading lazy associations afterwards throws `LazyInitializationException` unless `hibernate.enable_lazy_load_no_trans=true` is set in `persistence.xml`. Prefer to fetch what you need inside the `try` block.
- **Reusing a `Predicate` across two `CriteriaQueryContext` instances.** Predicates are bound to the `CriteriaBuilder` that created them. Build predicates inside the same `try` block as the query.
- **Not registering new entities in `DaoServices`.** Code that resolves a DAO via `DaoServices.getDaoByEntity(Class<?>)` will fail silently for unregistered entities — add the new DAO to the aggregator when you add a new entity.
- **Carrying a managed entity through process data across a task boundary.** When a workflow suspends at a user task and later resumes (or the entity is mapped between process steps), the deserialized entity arrives **transient** — its `id` reads `null` — so a subsequent `findByCriteria`/relation query throws `TransientObjectException: object references an unsaved transient instance`. **Pattern:** keep only the entity **id (`String`)** in process data (mark the data-class field `PERSISTENT`), and **reload a fresh managed entity** in each step via the DAO (`findByIds(List.of(id))`, or a thin `findById(id)` helper), then mutate + save. Reloading fresh each step also means the script `save(app)` needs no `as` cast and avoids stale-`version` optimistic-lock errors.

## Use Together With

- `axon-ivy-java-data` — base patterns for plain Java models / DTOs
- `axon-ivy-jpa` — when working below the helper layer (raw `@Entity` rules)
- `axon-ivy-liquibase` — schema migrations that go alongside entity changes
