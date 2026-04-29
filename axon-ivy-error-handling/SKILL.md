---
name: axon-ivy-error-handling
description: Rules and patterns for error handling in Axon Ivy projects — `BpmError` construction, error code naming, error start events in processes, exception walking, and the boundary between Java exceptions and Ivy errors. Use whenever Java code needs to surface a recoverable failure into a process, or when a process needs to react to a Java-thrown error.
---

# Axon Ivy Error Handling

In Axon Ivy, an error is a typed signal that flows through a process and can be caught at an **error boundary** (catch / error start event) on a `BPMN` element. The Java side raises errors via `BpmError`; the process side catches them via error code patterns.

This skill is about getting both sides aligned.

## When to Use

- Throwing an error from a Java service that an Ivy process should handle
- Designing the error code for a new failure mode
- Wiring an error catch / error start event in a process
- Translating a third-party exception (JPA, REST, LDAP) into something the process can react to

## When NOT to Use

- For HTTP status code mapping in REST endpoints → use `axon-ivy-rest` (REST endpoints map exceptions to `Response.status(...)` directly; they do NOT throw `BpmError`).
- For validation messages shown in a JSF dialog → use the JSF / PrimeFaces validation flow, not `BpmError`.
- For unrecoverable bugs (NPE, IllegalState) — let them propagate. `BpmError` is for *expected* failure modes the business wants to react to.

## The two sides

### Java side — throw `BpmError`

```java
import ch.ivyteam.ivy.bpm.error.BpmError;

public class StationService {

  public Station activate(String stationId) {
    Station station = stationDAO.findById(stationId);
    if (station == null) {
      throw BpmError.create("kfwg:station:notFound")
          .withMessage("Station " + stationId + " does not exist")
          .withAttribute("stationId", stationId)
          .build();
    }
    if (!station.isActivatable()) {
      throw BpmError.create("kfwg:station:notActivatable")
          .withMessage("Station " + stationId + " cannot be activated in its current state")
          .withAttribute("stationId", stationId)
          .withAttribute("currentStatus", station.getStatus())
          .build();
    }
    return station;
  }
}
```

### Process side — catch on the matching error code

In the `.p.json` of the calling process, attach an **Error Boundary Event** to the script step that calls the Java method:

- A boundary event with `errorCode = "kfwg:station:notFound"` catches only that one.
- A boundary event with `errorCode = "kfwg:station:*"` catches both via wildcard.
- A boundary event with `errorCode = "kfwg:*"` catches everything in the project.

The error attributes are accessible in the catch branch via `error.attributes["stationId"]`.

## Critical Rules

### 1. Error codes follow `<domain>:<entity>:<failure>` (lowercase, colon-separated)

Three segments minimum. Lower-case. No spaces. No underscores. Examples:

```
RIGHT: "kfwg:station:notFound"
RIGHT: "wastemgmt:disposition:invalidStatus"
RIGHT: "rest:external:timeout"
WRONG: "STATION_NOT_FOUND"
WRONG: "Station Not Found"
WRONG: "kfwg.station.notFound"
```

The first segment is your project / module prefix. Pick one and stay consistent — error codes are routing keys; rename them and every catch branch in every process breaks.

### 2. Always include a human-readable `message`

Process-side error handlers display the message. Pull it from CMS for i18n when you have it:

```java
throw BpmError.create("kfwg:station:notFound")
    .withMessage(Ivy.cms().co("/Errors/station/notFound", List.of(stationId)))
    .build();
```

### 3. Use `withAttribute` for context, not the message

Attributes are queryable in the catch branch. Stuffing an entity id into the message means the catch branch has to parse the string back. Wrong:

```java
.withMessage("Station " + stationId + " not found in district " + district)
```

Right:

```java
.withMessage("Station not found")
.withAttribute("stationId", stationId)
.withAttribute("district", district)
```

For more than 2-3 attributes, use the bulk form `.withAttributes(Map<String, Object>)`:

```java
.withAttributes(Map.of(
    "stationId", stationId,
    "district",  district,
    "operator",  operatorName))
```

### 4. Don't catch and re-throw `Exception` blindly

Wrapping every checked exception into a generic `BpmError` loses information and prevents callers from reacting to specific failures. Map deliberately:

```java
try {
  return ldapClient.findPerson(kid);
} catch (LdapNotFoundException e) {
  throw BpmError.create("kfwg:ldap:personNotFound")
      .withMessage("No LDAP person for kid " + kid)
      .withAttribute("kid", kid)
      .build();
} catch (LdapTimeoutException e) {
  throw BpmError.create("kfwg:ldap:timeout")
      .withMessage("LDAP service timed out")
      .withCause(e)
      .build();
}
// Anything else propagates as a Java exception — it's a bug, not an expected failure.
```

### 5. Put the `BpmError` throw closest to the failure

Don't translate exceptions at the top of the call stack. Translate them where the underlying call happens — in the DAO / client / utility — so every caller benefits from one centralised mapping.

### 6. Error start events for asynchronous flows

When the failure happens in a sub-process or signal handler that has no direct caller to react, attach an **Error Start Event** at the top of a sibling process. It receives `BpmError` objects whose `errorCode` matches its filter pattern. This is the equivalent of a process-wide try/catch.

### 7. Walking exception chains

When a `BpmError` is caused by a non-Ivy exception (JPA, REST, LDAP), the original cause is kept in `error.cause`. To find a specific cause type — e.g. distinguish "constraint violation" from "connection refused" — walk the chain:

```java
public static <T extends Throwable> Optional<T> findCause(Throwable t, Class<T> target) {
  for (Throwable cur = t; cur != null; cur = cur.getCause()) {
    if (target.isInstance(cur)) return Optional.of(target.cast(cur));
  }
  return Optional.empty();
}
```

A single utility class (`ExceptionUtilities` in elias) is the conventional home for this. Don't inline the walk in every catch block.

## Common Pitfalls

- **Throwing a plain `RuntimeException` from Java when the process expected an error** — the process-side catch branch never fires; the engine treats it as a system error and the task ends up in the failed-tasks list. Always use `BpmError` for expected failures.
- **Reusing the same error code for multiple failures** — any catch branch that listens for that code now fires for unrelated reasons. One code per failure mode.
- **Putting non-serializable objects in `withAttribute(...)`** — error attributes cross process boundaries and must serialize. Keep them to strings, numbers, enums, and small DTOs.
- **Catching `BpmError` in Java to log it** — the engine already logs uncaught errors with full context. A custom log line that swallows the `BpmError` and re-throws a worse one is a regression.
- **Wildcards too broad** — a boundary event listening for `*` catches everything including the engine's own errors (timeout, security). Always scope the prefix.

## Project variations

Two error-handling styles appear in the wild:

- **`BpmError`-based** (preferred, Ivy-idiomatic): Java throws `BpmError`; processes catch on error code. Documented above.
- **Custom RuntimeException** (legacy, e.g. `KfwgException`): Java throws a project-specific `RuntimeException`; processes either catch via a generic Java-exception handler or surface the message in a generic error page.

If a project uses the second style, prefer migrating new code to `BpmError` rather than perpetuating the custom exception. The `BpmError` style integrates with error start events; a custom `RuntimeException` does not.

## Use Together With

- `axon-ivy-process` — for wiring error boundary / error start events in `.p.json`
- `axon-ivy-rest` — for the orthogonal pattern of HTTP status code mapping
- `axon-ivy-cms` — for localised error messages
