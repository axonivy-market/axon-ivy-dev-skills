# Architecture Rules — C1–C3, H1–H4

## Tier 1 — Critical (Architecture)

**C1. Dependency Rule**
*Scan for:* imports from `java.sql.*`, `java.net.*`, third-party libraries, **or platform APIs** (`ch.ivyteam.ivy.*`) inside domain/entity packages.
*Why:* Core logic that imports infrastructure types cannot be tested or reused without that infrastructure. The entire inner layer is contaminated. In Axon Ivy projects, `Ivy.log()` and other `ch.ivyteam.*` calls must not appear in entity or domain classes — they belong only in adapter/service/listener classes.

**C2. No Direct Instantiation — Inject Interfaces**
*Scan for:* `new ConcreteClass(runtimeArg)` in business logic; `private [final] Interface field = new ConcreteImpl()` at field declaration level; multiple overloaded constructors that differ only in which concrete class they instantiate; `Function<X, ConcreteClass>` fields instead of `Function<X, Interface>`; static infrastructure fields initialized with `new ConcreteImpl()` when a shared factory (e.g. `JsonUtils.getObjectMapper()`) already exists.
*Why:* Calling `new` in a high-level class couples it to the concrete implementation and blocks substitution. Field-level instantiation is equally harmful — it is invisible to triage rules that only scan method bodies, and in JSF/CDI beans it also bypasses the container lifecycle. The caller (or `@PostConstruct`) must own the wiring.
```java
// ✗ — field-level: hard-couples concrete type, bypasses JSF lifecycle
private final HistoryStorage storage = new IvyRepoHistoryStorage();

// ✓ — declared separately, wired in @PostConstruct
private HistoryStorage storage;

@PostConstruct
public void init() {
  storage = new IvyRepoHistoryStorage();
  loadData();
}
```

**C3. Ports, Adapters, and Package Contracts**
*Scan for:* core logic that bypasses an interface and calls an adapter directly; implementation classes (`IvyRepo*`, `Jdbc*`, `Http*`) living in a package without an `internal` qualifier.
*Why:* Boundaries must be crossed through interfaces (Ports) defined by the inner layer. Classes in a top-level public package silently invite coupling — move implementations to `internal` sub-packages to signal they are not stable contracts.

---

## Tier 2 — High (Coupling)

**H1. Symmetric Abstraction Across Parallel Collaborators**
*Scan for:* pairs of classes with the same role (two listeners, two repositories, two handlers) where one accepts an interface and the other accepts a concrete class.
*Why:* Asymmetry signals an incomplete refactor. Both collaborators must be equally substitutable.
```java
// Before: asymmetric
public AiServiceHistoryListener(Function<String, HistoryRecorder> f) { ... }        // ✓
public ToolExecutionHistoryListener(Function<String, ToolExecutionRepository> f) {} // ✗

// After: symmetric
public AiServiceHistoryListener(Function<String, HistoryRecorder> f) { ... }        // ✓
public ToolExecutionHistoryListener(Function<String, ToolExecutionRecorder> f) { }  // ✓
```

**H2. Composition over Inheritance**
*Scan for:* `extends` used for code reuse (not domain classification); deep class hierarchies sharing behavior through base classes.
*Why:* Inheritance for reuse creates rigid coupling. Use `implements` + delegation instead.

**H3. Separation of Concerns**
*Scan for:* classes that mix business validation, orchestration, persistence, and formatting. Methods longer than ~30 lines doing multiple conceptually distinct things.
*Why:* A class with multiple reasons to change will break in unexpected places. Extract each responsibility into its own collaborator.

**H4. No Static Mutable Fields as Test Seams**
*Scan for:* `static` non-final fields (common names: `testStorage`, `mockProvider`, `override*`) whose only purpose is to be mutated by test setup; production constructors that check a static field to swap behavior.
*Why:* Pollutes production code with test infrastructure and introduces hidden global state. Replace with constructor injection.
