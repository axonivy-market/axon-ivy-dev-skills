package com.axonivy.ai.skills.evals;

import java.nio.file.Path;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;

import static org.assertj.core.api.Assertions.assertThat;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;
import org.junit.jupiter.api.TestInstance.Lifecycle;
import org.junit.jupiter.api.io.TempDir;
import org.yaml.snakeyaml.Yaml;

import com.axonivy.ai.skills.agent.AgentRun;
import com.axonivy.ai.skills.agent.CopilotAgentRunner;
import com.axonivy.ai.skills.agent.Workspace;

@TestInstance(Lifecycle.PER_CLASS)
class AxonIvyCmsEvalTest {

  private static final Path IVY_PROJECT = Path.of("src/test/fixtures/ivy-project");

  private static final String SKILL = "axon-ivy-cms";
  private static final String MODEL = "gpt-5.4-mini";
  private static final String CMS_EN = "cms/cms_en.yaml";
  private static final String CMS_DE = "cms/cms_de.yaml";
  private static final String DIALOG_PATH_PREFIX = "Dialogs.ivy.project.onboarding.StartOnboarding";

  private static final String PROMPT = """
      Add CMS labels for a new dialog `ivy.project.onboarding.StartOnboarding`. It needs:
      - a page title: "Start Employee Onboarding"
      - a Submit button
      - a Cancel button
      - a confirmation question with Yes/No answer labels

      Create the English and German CMS entries for it.
      """;

  private CopilotAgentRunner runner;

  @TempDir
  static Path tempDir;

  private Workspace workspace;
  private AgentRun run;

  @BeforeAll
  void runAgent() {
    var projectPath = Path.of("..").toAbsolutePath().normalize().toString();
    runner = new CopilotAgentRunner(MODEL, projectPath);
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
  void booleanLookingKeysAreQuoted() {
    Set<Object> enKeys = collectKeys(loadYaml(CMS_EN));
    Set<Object> deKeys = collectKeys(loadYaml(CMS_DE));

    assertThat(enKeys).as("Yes/No/True/False keys must be quoted so SnakeYAML keeps them as strings")
        .noneMatch(Boolean.class::isInstance);
    assertThat(deKeys).as("Yes/No/True/False keys must be quoted so SnakeYAML keeps them as strings")
        .noneMatch(Boolean.class::isInstance);
  }

  @Test
  void cmsFilesAreCreatedWithMatchingKeysAndGermanTranslations() {
    assertThat(run.invoked(SKILL))
        .as("the CMS skill must be invoked. The run replied: %s", run.transcript())
        .isTrue();
    assertThat(workspace.has(CMS_EN))
        .as("%s must be created. The run replied: %s", CMS_EN, run.transcript())
        .isTrue();
    assertThat(workspace.has(CMS_DE))
        .as("%s must be created. The run replied: %s", CMS_DE, run.transcript())
        .isTrue();

    Map<String, Object> en = flatten(loadYaml(CMS_EN));
    Map<String, Object> de = flatten(loadYaml(CMS_DE));

    assertThat(de.keySet())
        .as("cms_de.yaml must define exactly the same key paths as cms_en.yaml")
        .containsExactlyInAnyOrderElementsOf(en.keySet());

    String titleKey = en.keySet().stream()
        .filter(path -> path.startsWith(DIALOG_PATH_PREFIX) && path.endsWith("Title"))
        .findFirst()
        .orElseThrow(() -> new AssertionError("no dialog title key found. The run replied: " + run.transcript()));

    assertThat(String.valueOf(de.get(titleKey)))
        .as("the German title must be an actual translation, not a copy of the English text")
        .isNotEqualToIgnoringCase(String.valueOf(en.get(titleKey)));
  }

  private Map<String, Object> loadYaml(String relativePath) {
    Object loaded = new Yaml().load(workspace.read(relativePath));
    @SuppressWarnings("unchecked")
    Map<String, Object> map = (Map<String, Object>) loaded;
    return map;
  }

  private static Map<String, Object> flatten(Map<String, Object> yaml) {
    Map<String, Object> out = new TreeMap<>();
    flattenInto("", yaml, out);
    return out;
  }

  private static void flattenInto(String prefix, Object node, Map<String, Object> out) {
    if (node instanceof Map<?, ?> map) {
      map.forEach((key, value) -> flattenInto(prefix.isEmpty() ? String.valueOf(key) : prefix + "." + key, value, out));
    } else {
      out.put(prefix, node);
    }
  }

  private static Set<Object> collectKeys(Object node) {
    Set<Object> keys = new HashSet<>();
    collectKeysInto(node, keys);
    return keys;
  }

  private static void collectKeysInto(Object node, Set<Object> keys) {
    if (node instanceof Map<?, ?> map) {
      keys.addAll(map.keySet());
      map.values().forEach(value -> collectKeysInto(value, keys));
    }
  }

}