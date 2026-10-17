package com.axonivy.ai.skills.evals;

import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import static org.assertj.core.api.Assertions.assertThat;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;
import org.junit.jupiter.api.TestInstance.Lifecycle;
import org.junit.jupiter.api.io.TempDir;

import com.axonivy.ai.skills.agent.AgentRun;
import com.axonivy.ai.skills.agent.CopilotAgentRunner;
import com.axonivy.ai.skills.agent.Workspace;

import tools.jackson.core.JacksonException;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

@TestInstance(Lifecycle.PER_CLASS)
class AxonIvyProcessEvalTest {

  private static final Path IVY_PROJECT = Path.of("src/test/fixtures/ivy-project");
  private static final JsonMapper JSON_MAPPER = JsonMapper.builder().build();

  private static final String MODEL = "gpt-5.4-mini";
  private static final String MANAGEMENT_PROCESS = "process/com/example/EmployeeInformationManagement.p.json";
  private static final String CALLABLE_PROCESS = "process/com/example/GetMockEmployee.p.json";

  private static final String CALLABLE_PROMPT = """
      Create a callable GetMockEmployee process that builds a sample com.example.Employee and
      returns it from call().
      """;

  private static final String MAIN_PROCESS_PROMPT = """
      Wire EmployeeInformationManagement to call GetMockEmployee, then show
      EmployeeUpdateTypeSelection and branch on its returned update type. Add the start, call,
      dialog, Alternative, and a default process end; we can add the update tasks next.
      """;

  private static final String TASK_BRANCHES_PROMPT = """
      Create two UserTasks on the existing update branches:
      - Personal information: name the task Update Employee <%= in.employee.firstName %>
        <%= in.employee.lastName %> Information and use the EmployeeInput dialog.
      - Job information: name the task Update Employee <%= in.employee.firstName %>
        <%= in.employee.lastName %> Job Information and use the EmployeeJobInfoUpdate dialog.

      Pass the employee into each dialog and map the updated employee back to process data. Connect
      both tasks to the existing end, and keep the empty or unsupported update-type branch connected
      to that end as well.
      """;

  @TempDir
  static Path tempDir;

  private CopilotAgentRunner runner;
  private Workspace workspace;
  private AgentRun run;

  @BeforeAll
  void prepareWorkspace() {
    runner = new CopilotAgentRunner(MODEL, Path.of("..").toAbsolutePath().normalize().toString());
    workspace = Workspace.materialize(IVY_PROJECT, tempDir);
  }

  @AfterAll
  void stop() {
    if (runner != null) {
      runner.close();
    }
  }

  @Test
  void createsEmployeeInformationManagementWorkflow() {
    runPrompt(CALLABLE_PROMPT);
    assertCallableEmployeeProcess(process(CALLABLE_PROCESS));

    runPrompt(MAIN_PROCESS_PROMPT);
    assertMainProcessCallsCallableAndSelectsUpdateType(process(MANAGEMENT_PROCESS));

    runPrompt(TASK_BRANCHES_PROMPT);
    assertAlternativeBranchesToTaskDialogs(process(MANAGEMENT_PROCESS));
  }

  private void runPrompt(String prompt) {
    run = runner.run(prompt, workspace.root(), true);
  }

  private void assertCallableEmployeeProcess(JsonNode process) {
    assertThat(process.path("kind").asText()).isEqualTo("CALLABLE_SUB");

    JsonNode start = firstElement(process, "CallSubStart");
    assertThat(start.path("name").asText()).isEqualTo("call()");
    assertThat(start.path("config").path("signature").asText()).isEqualTo("call");
    assertThat(start.path("config").path("result").path("map").path("result.employee").asText())
        .isEqualTo("in.employee");

    JsonNode script = firstElement(process, "Script");
    String scriptCode = script.path("config").path("output").path("code").toString();
    boolean usesInputEmployee = scriptCode.contains("in.employee");
    boolean usesOutputEmployee = scriptCode.contains("out.employee");
    assertThat(usesInputEmployee || usesOutputEmployee).isTrue();
    assertThat(scriptCode)
        .contains("Employee");

    JsonNode end = firstElement(process, "CallSubEnd");
    assertThat(targets(start)).contains(id(script));
    assertThat(targets(script)).contains(id(end));
    assertUniqueIds(process);
  }

  private void assertMainProcessCallsCallableAndSelectsUpdateType(JsonNode process) {
    JsonNode start = firstElement(process, "RequestStart");
    JsonNode subprocessCall = firstElement(process, "SubProcessCall");
    JsonNode dialogCall = firstElement(process, "DialogCall");
    JsonNode alternative = firstElement(process, "Alternative");

    assertThat(targets(start)).contains(id(subprocessCall));
    assertThat(targets(subprocessCall)).contains(id(dialogCall));
    assertThat(targets(dialogCall)).contains(id(alternative));

    assertThat(subprocessCall.path("config").path("processCall").asText())
        .isEqualTo("com/example/GetMockEmployee:call()");
    assertThat(subprocessCall.path("config").path("output").path("map").path("out.employee").asText())
        .isEqualTo("result.employee");

    assertThat(dialogCall.path("config").path("dialog").asText())
        .isEqualTo("com.example.EmployeeUpdateTypeSelection:start(com.example.Employee)");
    assertThat(dialogCall.path("config").path("call").path("map").path("param.employee").asText())
        .isEqualTo("in.employee");
    assertThat(dialogCall.path("config").path("output").path("map").path("out.updateType").asText())
        .isEqualTo("result.updateType");

    assertUniqueIds(process);
  }

  private void assertAlternativeBranchesToTaskDialogs(JsonNode process) {
    JsonNode alternative = firstElement(process, "Alternative");
    List<JsonNode> userTasks = elementsOfType(process, "UserTask");
    JsonNode end = firstElement(process, "TaskEnd");

    assertThat(userTasks)
      .as("Generated EmployeeInformationManagement process JSON:\n%s", process.toPrettyString())
      .hasSize(2);
    List<String> taskDialogs = userTasks.stream()
        .map(task -> task.path("config").path("dialog").asText())
        .toList();
    assertThat(taskDialogs)
        .containsExactlyInAnyOrder(
            "com.example.EmployeeInput:start(com.example.Employee)",
            "com.example.EmployeeJobInfoUpdate:start(com.example.Employee)");
    userTasks.forEach(task -> assertThat(task.path("config").path("output").path("map").path("out.employee").asText())
      .isEqualTo("result.employee"));

    Set<String> outgoingIds = new HashSet<>();
    Set<String> branchTargets = new HashSet<>();
    alternative.path("connect").forEach(connection -> outgoingIds.add(connection.path("id").asText()));
    alternative.path("connect").forEach(connection -> branchTargets.add(connection.path("to").asText()));
    Set<String> conditionIds = new HashSet<>();
    alternative.path("config").path("conditions").propertyNames().forEach(conditionIds::add);
    assertThat(conditionIds).containsExactlyInAnyOrderElementsOf(outgoingIds);
    assertThat(outgoingIds.stream().map(id -> alternative.path("config").path("conditions").path(id).asText()))
        .contains("");
    Set<String> expectedBranchTargets = new HashSet<>(userTasks.stream().map(AxonIvyProcessEvalTest::id).toList());
    expectedBranchTargets.add(id(end));
    assertThat(branchTargets).containsExactlyInAnyOrderElementsOf(expectedBranchTargets);
    userTasks.forEach(task -> assertThat(targets(task)).contains(id(end)));
    assertUniqueIds(process);
  }

  private JsonNode process(String path) {
    try {
      return JSON_MAPPER.readTree(workspace.read(path));
    } catch (JacksonException e) {
      throw new AssertionError("Could not parse " + path + ". Agent transcript: " + run.transcript(), e);
    }
  }

  private static List<JsonNode> elementsOfType(JsonNode process, String type) {
    List<JsonNode> matching = new ArrayList<>();
    process.path("elements").forEach(element -> {
      if (type.equals(element.path("type").asText())) {
        matching.add(element);
      }
    });
    return matching;
  }

  private static String id(JsonNode element) {
    return element.path("id").asText();
  }

  private static Set<String> targets(JsonNode element) {
    Set<String> targets = new HashSet<>();
    element.path("connect").forEach(connection -> targets.add(connection.path("to").asText()));
    return targets;
  }

  private JsonNode firstElement(JsonNode process, String type) {
    List<JsonNode> matching = elementsOfType(process, type);
    assertThat(matching)
        .as("expected a %s element; agent transcript: %s", type, run.transcript())
        .isNotEmpty();
    return matching.get(0);
  }

  private static void assertUniqueIds(JsonNode process) {
    Set<String> ids = new HashSet<>();
    int idCount = 0;
    for (JsonNode element : process.path("elements")) {
      String elementId = element.path("id").asText();
      assertThat(ids.add(elementId)).as("duplicate process element ID %s", elementId).isTrue();
      idCount++;
      for (JsonNode connection : element.path("connect")) {
        String connectionId = connection.path("id").asText();
        assertThat(ids.add(connectionId)).as("duplicate element/connection ID %s", connectionId).isTrue();
        idCount++;
      }
    }
    assertThat(ids).hasSize(idCount);
  }
}
