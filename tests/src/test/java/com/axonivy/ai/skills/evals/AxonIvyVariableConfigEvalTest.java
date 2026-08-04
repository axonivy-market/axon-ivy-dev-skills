package com.axonivy.ai.skills.evals;

import static com.axonivy.ai.skills.judge.LlmAssert.assertThat;
import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;

import java.nio.file.Path;
import java.util.List;
import java.util.Map;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.io.TempDir;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.yaml.snakeyaml.Yaml;

import com.axonivy.ai.skills.agent.AgentRun;
import com.axonivy.ai.skills.agent.CopilotAgentRunner;
import com.axonivy.ai.skills.agent.InvokedSkill;
import com.axonivy.ai.skills.agent.Workspace;
import com.axonivy.ai.skills.judge.CopilotJudge;

class AxonIvyVariableConfigEvalTest {

  private static final Path SKELETON_PROJECT = Path.of("src/test/fixtures/ivy-project");
  private static final String VARIABLES_YAML = "config/variables.yaml";
  private static final String DASHBOARD_TEMPLATES_JSON = "config/variables/Portal/DashboardTemplates.json";
  private static final String DASHBOARD_TEMPLATES_TXT = "config/variables/Portal/DashboardTemplates.txt";
  private static final String SKILL = "axon-ivy-variable-config";

  private static final String RUN_MODEL = "claude-sonnet-5";
  private static final String JUDGE_MODEL = "gpt-5.4-mini";

  @TempDir
  Path tempDir;

  private static CopilotAgentRunner runner;
  private static CopilotJudge judge;

  @BeforeAll
  static void setup() {
    String testedSkillsDir = Path.of("..").toAbsolutePath().normalize().toString();
    runner = new CopilotAgentRunner(RUN_MODEL, testedSkillsDir);
    judge = new CopilotJudge(JUDGE_MODEL);
  }

  @AfterAll
  static void stop() {
    if (runner != null) {
      runner.close();
    }

    if (judge != null) {
      judge.close();
    }
  }

  @ParameterizedTest(name = "createIntegerVariable_enableSkills={0}")
  @ValueSource(booleans = { true, false })
  void createIntegerVariable(boolean enableSkills) {
    var workspace = Workspace.materialize(SKELETON_PROJECT, tempDir);

    var run = runner.run("add a new variable called PageSize and set default value to 10 and also a short comment to describe it",
        workspace.root(), enableSkills);
    var variablesYaml = workspace.read(VARIABLES_YAML);

    // deterministic check
    assertSkillsInvoked(run, enableSkills);

    if (enableSkills) {
      assertThat(run.usage().outputTokens()).isLessThan(800);
      assertThat(run.elapsed().toMinutes()).isLessThan(2);

      // numeric values are quoted strings, and carry no type annotation
      assertYamlContentEquals(variablesYaml, Map.of("Variables", Map.of("PageSize", "10")));
      // under Variables: optional description comments (none of them an annotation), then PageSize: "10"
      assertThat(variablesYaml).containsPattern("(?m)Variables:\\R(?:\\s*#(?!\\s*\\[).+\\R)*\\s*PageSize:\\s*(\"10\"|'10')\\s*$");

      // llm-as-judge check
      assertThat(judge, variablesYaml)
          .satisfies("there is a comment explaining what the PageSize is.");
    }
  }

  @ParameterizedTest(name = "createsBooleanVariable_enableSkills={0}")
  @ValueSource(booleans = { true, false })
  void createsBooleanVariable(boolean enableSkills) {
    var workspace = Workspace.materialize(SKELETON_PROJECT, tempDir);

    var run = runner.run(
        "add variable Portal.Tasks.EnablePinnedTask with default value true and a short comment about what it does.",
        workspace.root(), enableSkills);
    var variablesYaml = workspace.read(VARIABLES_YAML);

    assertSkillsInvoked(run, enableSkills);

    if (enableSkills) {
      assertThat(run.usage().outputTokens()).isLessThan(1000);
      assertThat(run.elapsed().toMinutes()).isLessThan(2);

      // boolean values are quoted strings, and carry no type annotation
      // Portal: > Tasks: > optional description comments (none of them an annotation), then EnablePinnedTask: "true"
      assertThat(variablesYaml).containsPattern("(?m)Portal:\\R\\s*Tasks:\\R(?:\\s*#(?!\\s*\\[).+\\R)*\\s*EnablePinnedTask:\\s*(\"true\"|'true')\\s*$");
      assertYamlContentEquals(variablesYaml, Map.of("Variables", Map.of("Portal", Map.of("Tasks", Map.of("EnablePinnedTask", "true")))));
    }
  }

  @ParameterizedTest(name = "createsPasswordVariable_enableSkills={0}")
  @ValueSource(booleans = { true, false })
  void createsPasswordVariable(boolean enableSkills) {
    var workspace = Workspace.materialize(SKELETON_PROJECT, tempDir);

    var run = runner.run("add a password variable OpenAI.Api.Key with value `secret-value` and add a short security comment for it.",
        workspace.root(), enableSkills);
    var variablesYaml = workspace.read(VARIABLES_YAML);

    assertSkillsInvoked(run, enableSkills);

    if (enableSkills) {
      assertThat(run.usage().outputTokens()).isLessThan(2000);
      assertThat(run.elapsed().toMinutes()).isLessThan(2);

      assertYamlContentEquals(variablesYaml, Map.of("Variables", Map.of("OpenAI", Map.of("Api", Map.of("Key", "secret-value")))));

      // OpenAI: > Api: > at least one description comment, then #[password] directly above Key: <value>
      assertThat(variablesYaml).containsPattern("(?m)OpenAI:\\R\\s*Api:\\R(?:\\s*#(?!\\[password\\]).*\\R)+\\s*#\\[password\\]\\R\\s*Key:\\s*.+");
    }
  }

  @ParameterizedTest(name = "createsEnumVariable_enableSkills={0}")
  @ValueSource(booleans = { true, false })
  void createsEnumVariable(boolean enableSkills) {
    var workspace = Workspace.materialize(SKELETON_PROJECT, tempDir);

    var run = runner.run(
        "add enum variable Portal.SidebarMode with allowed values HOVER, CLICK, STICK, HIDDEN and default value HOVER.",
        workspace.root(), enableSkills);
    var variablesYaml = workspace.read(VARIABLES_YAML);

    assertSkillsInvoked(run, enableSkills);

    if (enableSkills) {
      assertThat(run.usage().outputTokens()).isLessThan(1100);
      assertThat(run.elapsed().toMinutes()).isLessThan(2);

      assertYamlContentEquals(variablesYaml, Map.of("Variables", Map.of("Portal", Map.of("SidebarMode", "HOVER"))));

      // Portal: > optional description comments, then the enum annotation listing all 4 values directly above SidebarMode: HOVER
      assertThat(variablesYaml).containsPattern("(?m)Portal:\\R(?:\\s*#(?!\\s*\\[enum:).+\\R)*\\s*# \\[enum:\\s*HOVER,\\s*CLICK,\\s*STICK,\\s*HIDDEN\\]\\R\\s*SidebarMode:\\s*HOVER\\b");
    }

    // second turn: update the variable the first turn just wrote
    var updateRun = runner.run(
        "change the default value of Portal.SidebarMode to STICK and allow one more value COLLAPSED.",
        workspace.root(), enableSkills);
    var updatedYaml = workspace.read(VARIABLES_YAML);

    assertSkillsInvoked(updateRun, enableSkills);

    if (enableSkills) {
      assertThat(updateRun.usage().outputTokens()).isLessThan(1500);
      assertThat(updateRun.elapsed().toMinutes()).isLessThan(2);

      assertYamlContentEquals(updatedYaml, Map.of("Variables", Map.of("Portal", Map.of("SidebarMode", "STICK"))));

      // same shape as before, but the enum annotation must now list COLLAPSED too - extended, not replaced - above SidebarMode: STICK
      assertThat(updatedYaml).containsPattern("(?m)Portal:\\R(?:\\s*#(?!\\s*\\[enum:).+\\R)*\\s*# \\[enum:\\s*HOVER,\\s*CLICK,\\s*STICK,\\s*HIDDEN,\\s*COLLAPSED\\]\\R\\s*SidebarMode:\\s*STICK\\b");
    }
  }

  @ParameterizedTest(name = "createsJsonVariableReference_enableSkills={0}")
  @ValueSource(booleans = { true, false })
  void createsJsonVariableReference(boolean enableSkills) {
    var workspace = Workspace.materialize(SKELETON_PROJECT, tempDir);

    var run = runner.run(
      "add Portal.DashboardTemplates json variable which provides list of default dashboard templates for Portal.",
        workspace.root(), enableSkills);
    var variablesYaml = workspace.read(VARIABLES_YAML);

    assertSkillsInvoked(run, enableSkills);

    if (enableSkills) {
      assertThat(run.usage().outputTokens()).isLessThan(10_000);
      assertThat(run.elapsed().toMinutes()).isLessThan(2);

      assertYamlContentEquals(variablesYaml,
        Map.of("Variables", Map.of("Portal", Map.of("DashboardTemplates", ""))));

      // Portal: > optional description comments, then the json file annotation directly above an empty-valued DashboardTemplates:
      assertThat(variablesYaml).containsPattern("(?m)Portal:\\R(?:\\s*#(?!\\s*\\[file:\\s*json\\]).+\\R)*\\s*# \\[file:\\s*json\\]\\R\\s*DashboardTemplates:\\s*(\"\"|'')\\s*$");

      assertThat(workspace.has(DASHBOARD_TEMPLATES_JSON)).isTrue();
      assertDoesNotThrow(() -> {
        new Yaml().load(workspace.read(DASHBOARD_TEMPLATES_JSON));
      });
    }

    // delete the variable together with its backing file
    var deleteRun = runner.run("remove the Portal.DashboardTemplates variable",
        workspace.root(), enableSkills);
    assertThat(workspace.has(VARIABLES_YAML)).isTrue();
    var deletedYaml = workspace.read(VARIABLES_YAML);

    assertSkillsInvoked(deleteRun, enableSkills);

    if (enableSkills) {
      assertDoesNotThrow(() -> {
        new Yaml().load(deletedYaml);
      });
      assertThat(deletedYaml).doesNotContain("DashboardTemplates");
      assertThat(workspace.has(DASHBOARD_TEMPLATES_TXT)).isFalse();
    }
  }

  @ParameterizedTest(name = "createsDaytimeVariable_enableSkills={0}")
  @ValueSource(booleans = { true, false })
  void createsDaytimeVariable(boolean enableSkills) {
    var workspace = Workspace.materialize(SKELETON_PROJECT, tempDir);

    var run = runner.run(
      "add a variable named MyTime with value 13:00 and a short comment explaining it is a time of day setting.",
        workspace.root(), enableSkills);
    var variablesYaml = workspace.read(VARIABLES_YAML);

    assertSkillsInvoked(run, enableSkills);

    if (enableSkills) {
      assertThat(run.usage().outputTokens()).isLessThan(1000);
      assertThat(run.elapsed().toMinutes()).isLessThan(2);

      // optional description comments, then the daytime annotation directly above MyTime: 13:00
      assertThat(variablesYaml).containsPattern("(?m)(?:\\s*#(?!\\s*\\[daytime\\]).+\\R)*\\s*# \\[daytime\\]\\R\\s*MyTime:\\s*13:00\\b");
    }
  }

  private static void assertSkillsInvoked(AgentRun run, boolean enableSkills) {
    var expectedSkills = enableSkills ? List.of(SKILL) : List.<String>of();
    assertThat(run.invokedSkills())
        .extracting(InvokedSkill::name)
        .containsExactlyInAnyOrderElementsOf(expectedSkills);
  }

  private static void assertYamlContentEquals(String actualYaml, Object expectedYaml) {
    var yaml = new Yaml();
    assertDoesNotThrow(() -> {
      yaml.load(actualYaml);
    });
    var actual = yaml.load(actualYaml);
    assertThat(actual).isEqualTo(expectedYaml);
  }
}
