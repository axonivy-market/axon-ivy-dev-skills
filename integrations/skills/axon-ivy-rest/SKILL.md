---
name: axon-ivy-rest
description: Rules and patterns for JAX-RS REST endpoints in Axon Ivy projects. Covers `@Path` / HTTP method annotations, parameter binding, building `Response` objects, mapping exceptions to HTTP status codes, and `@RolesAllowed` auth. Use whenever Java code in `src/` defines, modifies, or consumes a REST resource (`@Path`-annotated class).
---

# Axon Ivy + JAX-RS REST

Axon Ivy ships a JAX-RS runtime; REST resources are plain Java classes that the engine picks up automatically. This skill covers the Ivy-specific conventions on top of standard JAX-RS.

## When to Use

- Creating a new REST endpoint (`@Path`-annotated class)
- Adding a method to an existing endpoint
- Mapping a Java exception to an HTTP status code
- Wiring authentication (`@RolesAllowed`) on a resource

## When NOT to Use

- For SOAP / JAX-WS endpoints (Ivy supports them but most projects are migrating away).
- For consuming external REST APIs from a process step → that goes through Ivy's REST Client config (`rest-clients/*.json`), which is separate.
- For request/response DTO design → use `axon-ivy-java-data`.

## File Locations

| Type | Location |
|------|----------|
| Resource class | `src/<package>/api/` (KFWG) or `src/<package>/rest/` (elias). Pick one and stay consistent within the project. |
| DTOs (request / response bodies) | `src/<package>/dto/` |
| Error response bodies | `src/<package>/dto/` or `src/<package>/api/error/` |

There is **no** `web.xml` or `@ApplicationPath` bootstrap class in an Ivy IAR project — the engine auto-discovers JAX-RS resources on the classpath. Do not add a `javax.ws.rs.core.Application` subclass.

## Resource skeleton

```java
package de.example.app.api;

import javax.annotation.security.RolesAllowed;
import javax.ws.rs.GET;
import javax.ws.rs.PUT;
import javax.ws.rs.Path;
import javax.ws.rs.PathParam;
import javax.ws.rs.QueryParam;
import javax.ws.rs.HeaderParam;
import javax.ws.rs.Produces;
import javax.ws.rs.Consumes;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import javax.ws.rs.core.Response.Status;

@Path("telecontrol-devices")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
@RolesAllowed("APP_API")
public class TelecontrolDeviceWebservice {

  @GET
  @Path("/{id}")
  public Response findById(
      @PathParam("id") String id,
      @HeaderParam("X-Requested-By") String requestedBy) {
    try {
      Device device = service.findById(id);
      if (device == null) {
        return Response.status(Status.NOT_FOUND).build();
      }
      return Response.ok(device).build();
    } catch (ValidationException e) {
      return Response.status(Status.BAD_REQUEST)
          .entity(new ErrorResponse(e.getMessage()))
          .build();
    }
  }
}
```

## Critical Rules

### 1. Class-level `@Path` is the URL prefix

The full URL is `<engine-base>/api/<app>/<project>/<class-@Path>/<method-@Path>`. Do not include leading or trailing `/` in `@Path` values; let JAX-RS join them.

```
RIGHT: @Path("telecontrol-devices")
WRONG: @Path("/telecontrol-devices/")
```

### 2. Always declare `@Produces` and `@Consumes` at the class level

Defaulting to `MediaType.APPLICATION_JSON` is the convention. Override per-method only when a single endpoint diverges (e.g. file download with `APPLICATION_OCTET_STREAM`). Without these, Ivy will reject requests with `415 Unsupported Media Type` for reasons that look like config bugs.

### 3. Auth via `@RolesAllowed` at class level

Apply `@RolesAllowed("ROLE_NAME")` to the class, not to every method. Override per-method only for an endpoint that needs a different role. Use `@PermitAll` explicitly on public endpoints — never leave one un-annotated.

The role name must match an Ivy role configured in the application (Engine Cockpit → Security System → Roles).

### 4. Always return `Response`, not the entity directly

```
RIGHT: public Response find() { return Response.ok(entity).build(); }
WRONG: public Device find() { return entity; }
```

Returning the entity directly works in trivial cases but blocks you from setting status codes, headers (e.g. `Content-Disposition` for downloads), or returning an error body.

### 5. Map exceptions inside the method, not via `ExceptionMapper`

The Ivy convention is per-method `try { … } catch (…) { return Response.status(…).entity(…).build(); }`. Reasons:

- The mapping is local — easy to read and change.
- Cross-class `ExceptionMapper`s are loaded inconsistently across IAR boundaries.
- It forces the author to think about which status code is right.

```java
try {
  return Response.ok(service.process(input)).build();
} catch (ValidationException e) {
  return Response.status(Status.BAD_REQUEST)
      .entity(new ErrorResponse("validation", e.getMessage()))
      .build();
} catch (NotFoundException e) {
  return Response.status(Status.NOT_FOUND).build();
} catch (ExternalServiceException e) {
  return Response.status(Status.SERVICE_UNAVAILABLE)
      .entity(new ErrorResponse("external", e.getMessage()))
      .build();
}
```

### 6. Use a typed `ErrorResponse` body

A bare `String` error body parses awkwardly on the client. Define a small DTO once and reuse it:

```java
public class ErrorResponse implements Serializable {
  private static final long serialVersionUID = 1L;
  private String code;
  private String message;
  // getters / setters …
}
```

Pull the message text from CMS so it follows the project's i18n setup:

```java
String msg = Ivy.cms().co("/Webservice/error/statusNotValid");
return Response.status(Status.BAD_REQUEST).entity(new ErrorResponse("statusNotValid", msg)).build();
```

### 7. Status codes — pick the right one

| Situation | Status | Notes |
|---|---|---|
| Input failed validation | `400 BAD_REQUEST` | Include a structured `ErrorResponse` body. |
| Caller not authenticated | `401 UNAUTHORIZED` | Auto-handled by Ivy's auth filter; rarely returned manually. |
| Caller authenticated but lacks role | `403 FORBIDDEN` | Auto-handled by `@RolesAllowed`. |
| Resource not found | `404 NOT_FOUND` | Empty body is fine. |
| Method exists, body wrong type | `415 UNSUPPORTED_MEDIA_TYPE` | Auto-handled when `@Consumes` is set. |
| Downstream service is down | `503 SERVICE_UNAVAILABLE` | Distinguish from `500` so clients know to retry. |
| Anything you didn't anticipate | `500 INTERNAL_SERVER_ERROR` | Catch `Exception` last. Log it. |

### 8. File downloads

```java
@GET
@Path("/{id}/document")
@Produces(MediaType.APPLICATION_OCTET_STREAM)
public Response download(@PathParam("id") String id) {
  java.io.File file = service.exportPdf(id);
  return Response.ok(file)
      .header("Content-Disposition", "attachment; filename=\"" + file.getName() + "\"")
      .build();
}
```

## Common Pitfalls

- **Forgetting `@RolesAllowed`** — leaves the endpoint open. Treat any new resource class without an explicit auth annotation as a security review failure.
- **Returning `Response` from a method that throws checked exceptions** — JAX-RS will translate them to `500` with no body. Catch and map them.
- **`@PathParam` not matching `@Path` placeholder** — silently binds `null`. Compile-time check: every `@PathParam("x")` has a `{x}` somewhere in `@Path`.
- **JSON body deserialization failing** — without an `@Consumes` declaration, the request is rejected before your method runs; with one, malformed JSON throws a `JsonProcessingException` that maps to a generic 400 with no useful body. Catch it and return a structured error if you care.
- **Authentication via custom header** (e.g. `X-Requested-By`) — fine, but combine it with `@RolesAllowed`, never as a substitute. The role check is what the engine enforces.

## Use Together With

- `axon-ivy-error-handling` — for translating between Java exceptions and `BpmError` when a process needs to react to REST failure
- `axon-ivy-java-data` — DTO patterns for request / response bodies
- `axon-ivy-cms` — for i18n of error messages
