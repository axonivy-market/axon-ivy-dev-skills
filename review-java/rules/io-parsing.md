# IO & Parsing Rules — M1, M3, M5a

Apply when the file has: `try/catch`, Jackson/`ObjectMapper` imports, `null` checks, `Optional`, or `IOException`.

---

**M1. Optional as First-Class Absence Signal**
*Scan for:* methods returning `null` to signal "not found"; `if (x.hasY()) { x.getY() }` or `x.hasY() ? x.getY() : fallback` double-access patterns; `if (x == null || x.getField() == null) return default;` null-guard before a try-catch block.
*Why:* `Optional<T>` makes absence explicit. The null-guard + try pattern has two separate failure modes and more code paths; the Optional chain unifies them.
```java
// Before: null guard + try — two separate failure modes
public static String getModelName(Entry entry) {
  if (entry == null || entry.getJson() == null) return UNKNOWN;
  try {
    JsonNode array = MAPPER.readTree(entry.getJson());
    ...
  } catch (IOException e) { return UNKNOWN; }
}

// After: Optional chain — null and parse failure in one flow
public static String getModelName(Entry entry) {
  return Optional.ofNullable(entry)
      .map(Entry::getJson)
      .map(json -> {
        try {
          JsonNode array = JsonUtils.getObjectMapper().readTree(json);
          ...
        } catch (IOException e) {
          Ivy.log().warn(...);
          return UNKNOWN;
        }
      })
      .orElse(UNKNOWN);
}

// Also: double-access fix
// Before:
var tools = msg.hasTools() ? msg.tools().stream() : Stream.<Tool>empty();
// After:
var tools = Optional.ofNullable(msg.tools()).orElse(List.of()).stream();
```

---

**M3. Logging at Silent Failure Paths**
*Scan for:* `catch` blocks that swallow exceptions without logging; `Optional.empty()` returns with no log; null-check branches that fall back silently; `java.util.logging.Logger` or `System.out` instead of the platform logger.
*Why:* Silent failures are invisible in production. Emit `WARN` with enough context to diagnose the issue.

**Exception for entity classes:** entity/domain classes must NOT call `Ivy.log()` (violates C1). For internal serialization that cannot realistically fail, `catch (JsonProcessingException ignored) {}` is correct — not a M3 violation.

**Catch specificity:** Always catch the most specific exception the method declares. IDE hint "Can be replaced with multicatch or several catch clauses catching specific exceptions" signals the catch is too broad. `catch (Exception e)` almost always has a more precise replacement — for Jackson `readTree`, use `catch (IOException e)`.
```java
// Wrong — bypasses Ivy runtime logging
private static final Logger LOG = Logger.getLogger(...);
LOG.warning(() -> "msg " + value);

// Wrong — too broad catch type
} catch (Exception e) { return 0; }

// Correct in service/utility — specific exception + Ivy-integrated logging
} catch (IOException e) {
    Ivy.log().warn(String.format("Failed to parse messagesJson for caseUuid=%s: %s",
        entry.getCaseUuid(), e.getMessage()));
    return 0;
}

// Correct in entity class — silent ignore (Ivy.log() would violate C1)
} catch (JsonProcessingException ignored) {}
```

---

**M5a. No Magic Values**
*Scan for:* unnamed numeric/string literals in logic; constants named so vaguely they require a comment; the same sentinel defined independently in multiple classes; **JSON field name strings** used in `node.get("fieldName")` or `map.get("key")` calls; **return value sentinels** (`"unknown"`, `"N/A"`, `""`) repeated across multiple methods of the same class; **inline string concatenation** for multi-part output strings where the shape of the string is fixed but the values vary.
*Why:* Magic values force readers to reverse-engineer intent. JSON field name strings are especially dangerous — if the serialization schema changes, silent `null`/`0` returns with no compile-time or runtime error. Return value sentinels repeated 4+ times will drift. Inline concatenation buries the output shape inside the logic; a named format constant makes the shape explicit and reusable.
```java
// Before: inline literals everywhere
node.get("totalTokens")      // ✗ silent null if schema renames field
node.get(0).get("modelName") // ✗
return "unknown";             // ✗ same string in 4 places — will drift

// After: named constants
private static final String FIELD_TOTAL_TOKENS = "totalTokens";
private static final String FIELD_MODEL_NAME   = "modelName";
private static final String UNKNOWN            = "unknown";

node.get(FIELD_TOTAL_TOKENS)      // ✓
node.get(0).get(FIELD_MODEL_NAME) // ✓
return UNKNOWN;                    // ✓

// Cross-class sentinel duplication — shared constant belongs on the port interface
// Before: two classes define the same sentinel independently
String taskUuid = ...orElse("0");          // AgentCallExecutor
private static final String NO_TASK_UUID = "-1"; // AgentHistoryTreeBuilder — already drifted!

// After: one definition on the interface, used everywhere
String NO_TASK_UUID = "-1";  // HistoryRecorder interface
...orElse(HistoryRecorder.NO_TASK_UUID);
StringUtils.defaultIfBlank(taskUuid, HistoryRecorder.NO_TASK_UUID);

// Inline string concatenation vs. named format constants
// Before: output shape is buried inside the logic
return hours + " hour" + (hours > 1 ? "s" : "") + (remainingMinutes > 0 ? " " + remainingMinutes + " min" : "");

// After: named format constants + String.format — shape is visible at a glance
private static final String MINUTES_FORMAT       = "%d min";
private static final String HOURS_FORMAT         = "%d hour%s";
private static final String HOURS_MINUTES_FORMAT = "%d hour%s %d min";

return String.format(HOURS_MINUTES_FORMAT, hours, plural, remainingMinutes);
```
