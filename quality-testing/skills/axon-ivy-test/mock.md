# REST Mocking

REST endpoint mocking pattern using JAX-RS mock endpoints.

## File Location

`src/package/mock/MockApi.java`

## Mock Endpoint Pattern

```java
package package.mock;

import javax.annotation.security.PermitAll;
import javax.ws.rs.*;
import javax.ws.rs.core.Response;
import com.fasterxml.jackson.databind.JsonNode;
import io.swagger.v3.oas.annotations.Hidden;
import java.util.function.Function;

@Path("myMock")
@PermitAll
@Hidden
public class MockApi {

  private static Function<JsonNode, Response> HANDLER;

  public static void define(Function<JsonNode, Response> handler) {
    MockApi.HANDLER = handler;
  }

  @POST
  @Path("{test}/endpoint")
  public Response handle(JsonNode request, @PathParam("test") String test) {
    return HANDLER.apply(request);
  }
}
```

## Usage in Test

```java
@BeforeEach
void setup(ResourceResponder responder) {
  MockApi.define(request -> {
    if (request.get("type").asText().equals("A")) {
      return responder.send("responseA.json");
    }
    return responder.send("responseB.json");
  });
}
```
