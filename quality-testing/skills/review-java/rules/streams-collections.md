# Streams & Collections Rules — M2, M2b, M5b, M5c

Apply when the file has: `.stream(`, `.map(`, `Comparator`, `sorted(`, `filter(`, `List`, `Set`, `ArrayList`.

---

**M2. Right Collection for the Job**
*Scan for:* `List` used when uniqueness is required; `.contains()` called in a hot path on a `List`; `.stream().distinct()` that could be eliminated by using a `Set` from the start.
*Why:* The wrong collection degrades correctness and performance. Duplicate entries in a list that should be a set are silent data bugs.

---

**M2b. List Mutability — Match Initialization to Usage**
*Scan for:* lists initialized with immutable factories (`List.of(...)`, `.toList()`, `List.copyOf(...)`, `Collections.unmodifiableList(...)`) where downstream code calls mutating methods (`add`, `remove`, `set`, `clear`, `sort`); and conversely, `new ArrayList<>()` wrapping when the list is never mutated.
*Why:* `List.of()` and `.toList()` return immutable lists — `add()`/`remove()` throws `UnsupportedOperationException` at runtime with no compile-time warning. Fix at the initialization site, not the call site.
```java
// Bug: .toList() is immutable — appendGhostNodes() calls nodes.add(...)
List<AgentNode> nodes = stream.map(...).toList();  // ✗ immutable
appendGhostNodes(nodes, ...);                       // throws at runtime

// Fix: wrap in ArrayList when downstream mutation is needed
List<AgentNode> nodes = new ArrayList<>(stream.map(...).toList());  // ✓
appendGhostNodes(nodes, ...);                                        // safe

// Checklist:
// 1. Trace every usage — does any call add/remove/set/clear/sort?
// 2. YES → must be new ArrayList<>(...) or similar mutable factory
// 3. NO  → prefer .toList() or List.of() to signal intent
```

---

**M5b. No Single-Letter Lambda Parameters**
*Scan for:* single-letter lambda parameters (`e`, `l`, `n`, `c`, `t`, `a`) when the type is non-obvious from context.
*Why:* Single-letter variables are opaque — `entry`, `link`, `node`, `candidate`, `task` communicate the type and role at a glance.
```java
// ✗ — reader must trace the stream source to understand what 'e' is
chatEntries.stream().filter(e -> !subAgentIds.contains(e.getAgentId()))

// ✓ — type and role are self-evident
chatEntries.stream().filter(entry -> !subAgentIds.contains(entry.getAgentId()))
```

---

**M5c. Sort Method Names Must Include By-Clause and Direction**
*Scan for:* sort/order methods that omit the sort key or direction from their name.
*Why:* A reader should never have to open a sort method body to know what it sorts by and in which direction. Convention: `<verb><Subject>By<Key><Dir>` where `<Dir>` is `Asc` or `Desc`.
```java
// ✗ — reader must open the body to understand sort key and direction
private List<TaskNode> sortTaskNodes(List<TaskNode> tasks) { ... }

// ✓ — self-documenting
private List<TaskNode> sortTaskNodesByAgentTimestampAsc(List<TaskNode> tasks) { ... }
// More examples: sortUsersByCreatedAtDesc, sortEntriesByPriorityAsc
```

---

## Apache Commons idioms (prefer over manual ternaries)
```java
// StringUtils.defaultIfBlank > isNotBlank ternary
return StringUtils.isNotBlank(taskUuid) ? taskUuid : NO_TASK_UUID;  // ✗
return StringUtils.defaultIfBlank(taskUuid, NO_TASK_UUID);           // ✓

// CollectionUtils.emptyIfNull — ONLY when streaming directly (returns Collection<T>, not List<T>)
return CollectionUtils.emptyIfNull(map.get(key)).stream()...         // ✓ streamed immediately
buildNode(map.getOrDefault(key, List.of()), ...);                    // ✓ use getOrDefault for List<T>
```
