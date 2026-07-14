# Story Type: Entity and Repository

**Source:** Persist Data step + Entity definition in requirements.

**This story enables developers to** persist and retrieve domain entities using the Axon Ivy repository.

---

## Scope

One story for the persistence layer:

- Entity definition (composes data classes, adds lifecycle metadata like `createdDate`, `modifiedDate`, `status`)
- Repository class with CRUD methods (save, findById, findByStatus, findAll, delete, plus domain-specific finders)

**Why together:** A repository without its entity is not useful.

---

## Implementation Details to Include

### Entity

- Class name, package, base class (if any)
- Field table: Name | Type | Description
- Must include: `id` (UUID or String), `createdDate`, `lastModifiedDate`, `status`
- Status field uses a process-specific enum (e.g., `SupplierStatus`)

### Repository

- Class name, package
- Singleton pattern: `getInstance()` method
- Method table:

| Method | Parameters | Returns | Notes |
| ------ | ---------- | ------- | ----- |
| save | entity | entity | Persists or updates |
| findById | String id | entity or null | Returns null if not found |
| findAll | — | List | All persisted instances |
| findByStatus | StatusEnum | List | Filter by status |
| delete | String id | void | Removes from repo |

Add domain-specific finders as needed (e.g., `findBySupplierId`).

---

## Acceptance Criteria

- [ ] Entity can be saved and retrieved by ID via `Ivy.repo()`
- [ ] `findAll()` returns all persisted instances
- [ ] `findById(null)` and `findById("")` return null without throwing
- [ ] Repository is a singleton (`getInstance()`)
- [ ] Entity has `createdDate` and `lastModifiedDate` fields set on save
