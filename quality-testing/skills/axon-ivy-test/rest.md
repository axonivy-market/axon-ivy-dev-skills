# REST Testing

REST integration testing with `@RestResourceTest` combining web server and resource loading.

## File Location

`src_test/package/Test*.java`

## RestResourceTest Annotation

Create in `src_test/ch/ivyteam/test/`:

```java
@Retention(RetentionPolicy.RUNTIME)
@Target({ElementType.TYPE, ElementType.PARAMETER})
@Inherited
@IvyProcessTest(enableWebServer = true)
@ExtendWith(ResourceResponse.class)
public @interface RestResourceTest {}
```

## Usage Pattern

```java
@RestResourceTest
public class TestMyRestIntegration {

  @BeforeEach
  void setup(AppFixture fixture, ResourceResponder responder) {
    fixture.var("api.baseUrl", OpenAiTestClient.localMockApiUrl("test"));
    MockOpenAI.defineChat(req -> responder.send("response.json"));
  }

  @Test
  void testRestCall(BpmClient client) {
    var result = client.start()
        .process(BpmProcess.name("MyProcess"))
        .execute();
    assertThat(result.data().last().getResult()).contains("expected");
  }
}
```
