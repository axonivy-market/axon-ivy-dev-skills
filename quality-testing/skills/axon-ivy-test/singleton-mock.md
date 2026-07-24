# Mocking Static Singletons

Many project collaborators expose themselves as a static singleton (`XxxDAO.getInstance()`,
`XxxService.getInstance()`, …), not as an injected dependency. Callers reach the accessor
directly, so tests must mock the *static method*, not just an instance.

Applies to **any** `getInstance()`-style singleton the class under test calls — DAOs,
services, config/registry holders, and similar.

## When to Use

Target method calls one or more `Xxx.getInstance()...` chains directly (no
constructor/setter injection). Combine with `unit.md`'s Ivy Unit Test section when the
same method also touches `Ivy.var()`, CMS, or the workflow session.

## Pattern

One `MockedStatic<T>` + one plain `mock(T.class)` per singleton used by the method under
test. The example uses a DAO; a service singleton (or any other) follows the identical
shape — swap `MyDAO` for `MyService` etc.

```java
@IvyTest
class TestMyService {

  private MyService service;

  private MyDAO mockMyDao;
  private MockedStatic<MyDAO> myDaoStatic;

  @BeforeEach
  void setUp() {
    service = new MyService();

    mockMyDao = mock(MyDAO.class);
    myDaoStatic = mockStatic(MyDAO.class);
    myDaoStatic.when(MyDAO::getInstance).thenReturn(mockMyDao);
  }

  @AfterEach
  void tearDown() {
    myDaoStatic.close();
  }

  @Test
  void methodUnderTest_scenario_expectedBehavior() {
    var input = MyEntityFake.create();
    var expected = MyEntityFake.create();
    when(mockMyDao.findById(eq(input.getId()))).thenReturn(expected);
    when(mockMyDao.save(eq(expected))).thenReturn(expected);

    var result = service.methodUnderTest(input);

    // Assert the returned/mutated state against the exact stubbed value.
    assertThat(result.getSomeField()).isEqualTo(expected.getSomeField());

    // Verify collaborator calls with the exact argument (eq(...)) and an explicit count
    // (times(1)) rather than any()/the bare verify(mock)... shorthand, so a wrong
    // argument or an accidental double-fetch/double-save fails the test.
    verify(mockMyDao, times(1)).findById(eq(input.getId()));
    verify(mockMyDao, times(1)).save(eq(expected));
  }
}
```

## Rules

- One `MockedStatic<T>` field + one plain `mock(T.class)` per singleton used by the method
  under test — declare both in `@BeforeEach`, close every `MockedStatic` in `@AfterEach`.
- Stub `getInstance()` with a method reference: `xxxStatic.when(Xxx::getInstance).thenReturn(mockXxx)`.
- Only mock the singletons the target method actually calls — don't pre-emptively mock every
  DAO/service in the project.
- Never mock the class under test itself. If the SUT is also a singleton, construct it with
  `new`, not via its own `getInstance()`.
- Prefer `eq(...)` over `any()` when stubbing/verifying — pin down the exact argument the
  method under test is expected to pass, and have the stub return a distinct expected
  value (not just echo the input) so the assertion proves the value actually flowed
  through the collaborator round-trip.
- Every test asserts the returned/mutated state (`assertThat(result...)`) *and* verifies
  the collaborator interactions with an explicit count (`verify(mock, times(1))...`) — one
  without the other leaves a gap (state could be right by accident, or the call count could
  drift without any assertion catching it).
- Build input/expected entities with the project's `*Fake` factories (`service/fake/`)
  instead of constructing them field-by-field in the test.

## File Placement

Same test class as the method under test — this is not a separate helper file, just the
`@BeforeEach`/`@AfterEach` shape for tests in Intent B (`unit.md`) whose code reaches its
collaborators through static singletons.
