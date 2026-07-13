# Resource Responder

Load JSON fixtures with `ResourceResponder` for test data.

## File Location

Fixtures: `src_test/package/feature/response.json`

## ResourceResponder Class

Create in `src_test/ch/ivyteam/test/resource/`:

```java
public class ResourceResponder {
  private final Class<?> testClass;

  public ResourceResponder(Class<?> testClass) {
    this.testClass = testClass;
  }

  public Response send(String resourceName) {
    try (var stream = testClass.getResourceAsStream(resourceName)) {
      String content = new String(stream.readAllBytes());
      return Response.ok(content).build();
    } catch (Exception e) {
      return Response.serverError().entity(e.getMessage()).build();
    }
  }
}
```

## Usage Pattern

```java
@RestResourceTest
public class TestFeature {

  @BeforeEach
  void setup(ResourceResponder responder) {
    // Loads src_test/package/feature/response.json
    MockApi.define(req -> responder.send("response.json"));
  }
}
```

## Fixture File Example

`src_test/package/feature/response.json`:

```json
{
  "id": "test-123",
  "status": "success",
  "data": { "value": 42 }
}
```
