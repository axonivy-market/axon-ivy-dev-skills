package com.axonivy.ai.skills.evals;

import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;

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
class AxonIvyDataEvalTest {

  private static final Path IVY_PROJECT = Path.of("src/test/fixtures/ivy-project");
  private static final JsonMapper JSON_MAPPER = JsonMapper.builder().build();

  private static final String MODEL = "gpt-5.4-mini";
  private static final String DATA_CLASS = "dataclass/com/example/BusinessProcessData.d.json";
    private static final Map<String, String> EXPECTED_FIELD_TYPES = Map.ofEntries(
      Map.entry("eligibleForAdvance", "Boolean"),
      Map.entry("dependentCount", "java.lang.Integer"),
      Map.entry("conversionRate", "java.lang.Double"),
      Map.entry("reimbursementAmount", "java.math.BigDecimal"),
      Map.entry("serviceDate", "ch.ivyteam.ivy.scripting.objects.Date"),
      Map.entry("submittedAt", "ch.ivyteam.ivy.scripting.objects.DateTime"),
      Map.entry("receiptContent", "ch.ivyteam.ivy.scripting.objects.Binary"),
      Map.entry("receiptFile", "java.io.File"),
      Map.entry("receiptStream", "java.io.InputStream"),
      Map.entry("lineItems", "List<com.example.Item>"),
      Map.entry("reviewTags", "List<String>"),
      Map.entry("mailingAddress", "com.example.Address"),
      Map.entry("reimbursementStatus", "com.example.Status"));

  private static final String PROMPT = """
      Update `com.example.BusinessProcessData` for an employee reimbursement review with:
      - `applicantName`, a regular text value
      - `eligibleForAdvance`, a true/false flag
      - `dependentCount`, a whole-number quantity
      - `conversionRate`, for simple calculations
      - `reimbursementAmount`, requiring strict financial rounding
      - `serviceDate`, a calendar date
      - `submittedAt`, a full timestamp
      - `receiptContent`, uploaded file content held in process data
      - `receiptFile`, an uploaded file handle
      - `receiptStream`, an uploaded file content stream for processing
      - `lineItems`, a list of `com.example.Item` objects
      - `reviewTags`, a list of strings
      - `mailingAddress`, a nested `com.example.Address` object
      - `reimbursementStatus`, a `com.example.Status` enum
      - `approvalResult`, text that must still be available after a UserTask for its dialog
      """;

  @TempDir
  static Path tempDir;

  private CopilotAgentRunner runner;
  private Workspace workspace;
  private AgentRun run;

  @BeforeAll
  void runAgent() {
    runner = new CopilotAgentRunner(MODEL, Path.of("..").toAbsolutePath().normalize().toString());
    workspace = Workspace.materialize(IVY_PROJECT, tempDir);
    run = runner.run(PROMPT, workspace.root(), true);
  }

  @AfterAll
  void stop() {
    if (runner != null) {
      runner.close();
    }
  }

  @Test
  void marksDataNeededAfterAUserTaskPersistent() {
    assertThat(hasModifier(fields().get("approvalResult"), "PERSISTENT"))
        .as("approvalResult must survive the UserTask save point")
      .isTrue();
  }

  @Test
  void createsEveryFieldTypeDocumentedByTheSkill() {
    Map<String, JsonNode> fields = fields();

    EXPECTED_FIELD_TYPES.forEach((name, expectedType) -> assertThat(fields.get(name).path("type").asText())
        .as("field %s must use the documented type", name)
        .isEqualTo(expectedType));

    assertThat(fields.get("applicantName").has("type"))
        .as("String is the default data-class field type")
        .isFalse();
  }

  private Map<String, JsonNode> fields() {
    JsonNode dataClass;
    try {
      dataClass = JSON_MAPPER.readTree(workspace.read(DATA_CLASS));
    } catch (JacksonException e) {
      throw new AssertionError("Could not parse " + DATA_CLASS, e);
    }

    Map<String, JsonNode> fields = new HashMap<>();
    for (JsonNode field : dataClass.path("fields")) {
      fields.put(field.path("name").asText(), field);
    }
    assertThat(fields.keySet())
        .as("all requested data fields must be created. The run replied: %s", run.transcript())
        .contains("applicantName", "approvalResult")
        .containsAll(EXPECTED_FIELD_TYPES.keySet());
    return fields;
  }

  private static boolean hasModifier(JsonNode field, String modifier) {
    for (JsonNode value : field.path("modifiers")) {
      if (modifier.equals(value.asText())) {
        return true;
      }
    }
    return false;
  }
}