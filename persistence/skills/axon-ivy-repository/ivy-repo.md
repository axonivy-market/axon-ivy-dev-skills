## Ivy.repo() — Default Persistence Approach

Uses Axon Ivy Business Data (`Ivy.repo()`) — a built-in NoSQL store. No database configuration needed.

For entity/model class definitions, use `axon-ivy-java-data` skill.

## When to Use

- User asks to persist/save an entity
- User asks to create CRUD operations for a model
- Workflow needs to store/retrieve data
- No specific database technology requested

## File Location

```text
src/package/repository/EntityRepository.java
```

## Repository Template

```java
package package.repository;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

import org.apache.commons.lang3.StringUtils;

import ch.ivyteam.ivy.business.data.store.search.Filter;
import ch.ivyteam.ivy.environment.Ivy;
import package.model.Entity;
import package.model.EntityStatus;

/**
 * Repository for persisting Entity to Axon Ivy Business Data.
 */
public class EntityRepository {

  private static final String FIELD_ID = "id";
  private static final String FIELD_NAME = "name";
  private static final String FIELD_STATUS = "status";

  private static EntityRepository instance;

  public static EntityRepository getInstance() {
    if (instance == null) {
      instance = new EntityRepository();
    }
    return instance;
  }

  /**
   * Creates a new entity.
   */
  public Entity create(Entity entity) {
    if (entity == null) {
      throw new IllegalArgumentException("Entity cannot be null");
    }

    return Ivy.repo().save(entity).getContext();
  }

  /**
   * Retrieves all entities.
   */
  public List<Entity> findAll() {
    return Ivy.repo().search(Entity.class).execute().getAll();
  }

  /**
   * Finds entity by ID.
   */
  public Entity findById(String id) {
    if (StringUtils.isBlank(id)) {
      return null;
    }
    return Ivy.repo().search(Entity.class)
        .textField(FIELD_ID)
        .isEqualToIgnoringCase(id)
        .execute()
        .getFirst();
  }

  /**
   * Finds entities by name (partial match).
   */
  public List<Entity> findByName(String name) {
    if (StringUtils.isBlank(name)) {
      return new ArrayList<>();
    }
    return Ivy.repo().search(Entity.class)
        .textField(FIELD_NAME)
        .containsAllWordPatterns(name)
        .execute()
        .getAll();
  }

  /**
   * Finds entities by status.
   */
  public List<Entity> findByStatus(EntityStatus status) {
    if (status == null) {
      return new ArrayList<>();
    }
    return Ivy.repo().search(Entity.class)
        .textField(FIELD_STATUS)
        .isEqualToIgnoringCase(status.name())
        .execute()
        .getAll();
  }

  /**
   * Updates an existing entity.
   */
  public Entity update(Entity entity) {
    if (entity == null) {
      return null;
    }

    return Ivy.repo().save(entity).getContext();
  }

  /**
   * Deletes an entity.
   */
  public void delete(Entity entity) {
    if (entity == null) {
      return;
    }
    Entity entityInRepo = findById(entity.getId());
    if (entityInRepo != null) {
      Ivy.repo().delete(entityInRepo);
    }
  }

  /**
   * Deletes an entity by ID.
   */
  public boolean deleteById(String id) {
    Entity entity = findById(id);
    if (entity != null) {
      Ivy.repo().delete(entity);
      return true;
    }
    return false;
  }

  /**
   * Gets the count of all entities.
   */
  public long count() {
    return Ivy.repo().search(Entity.class).execute().count();
  }
}
```

## Search with Multiple Filters

```java
public List<Entity> search(String name, EntityStatus status) {
  var search = Ivy.repo().search(Entity.class);
  List<Filter<Entity>> filters = new ArrayList<>();

  if (StringUtils.isNotBlank(name)) {
    filters.add(search.textField(FIELD_NAME).containsAllWordPatterns(name));
  }

  if (status != null) {
    filters.add(search.textField(FIELD_STATUS).isEqualToIgnoringCase(status.name()));
  }

  if (filters.isEmpty()) {
    return findAll();
  }

  for (Filter<Entity> f : filters) {
    search.filter(f);
  }

  return search.execute().getAll();
}
```

## Usage in Process Script

```java
import package.repository.EntityRepository;

// Create
EntityRepository.getInstance().create(in.entity);

// Find
in.entity = EntityRepository.getInstance().findById(in.entityId);

// Update
EntityRepository.getInstance().update(in.entity);

// Delete
EntityRepository.getInstance().delete(in.entity);
```
