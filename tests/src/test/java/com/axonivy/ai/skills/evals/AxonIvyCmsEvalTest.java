package com.axonivy.ai.skills.evals;

import java.nio.file.Path;
import java.util.HashSet;
import java.util.List;
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

  private static final Path SKELETON_PROJECT = Path.of("src/test/fixtures/ivy-project");

  private static final String SKILL = "axon-ivy-cms";
  private static final String MODEL = "gpt-5.4-mini";
  private static final String CMS_EN = "cms/cms_en.yaml";
  private static final String CMS_DE = "cms/cms_de.yaml";
  private static final String SEED_KEY_PATH = "Labels.ExistingFixtureLabel";
  private static final String EN_SEED_VALUE = "Keep this English label";
  private static final String DE_SEED_VALUE = "Diese deutsche Bezeichnung behalten";
  private static final String DIALOG = "dialog/com/example/CmsExample/CmsExample.xhtml";
  private static final String DIALOG_PATH_PREFIX = "Dialogs.com.example.CmsExample";
  private static final List<String> HARDCODED_TEXT = List.of(
      "Employee information",
      "Employee ID",
      "Employee ID is required",
      "First name",
      "First name is required",
      "Last name",
      "Last name is required",
      "Birthday",
      "Birthday is required",
      "Enter a valid birthday",
      "Email",
      "Email is required",
      "Years of experience",
      "Performance rating",
      "Job title",
      "Department",
      "Cancel",
      "Save employee");

  private static final String PROMPT = """
      Update the existing XHTML dialog `dialog/com/example/CmsExample/CmsExample.xhtml`.
      Move every hardcoded user-visible text, including the title, field labels, validation messages,
      and action labels, to CMS references. Update the existing English and German CMS files in place;
      both files already exist, so do not create or delete CMS files. Preserve existing CMS entries,
      the current English wording, and all dialog behavior, component IDs, and technical attributes.
      """;

  private CopilotAgentRunner runner;

  @TempDir
  static Path tempDir;

  private Workspace workspace;
  private AgentRun run;
  private String dialogBefore;

  @BeforeAll
  void runAgent() {
    var projectPath = Path.of("..").toAbsolutePath().normalize().toString();
    runner = new CopilotAgentRunner(MODEL, projectPath);
    workspace = Workspace.materialize(SKELETON_PROJECT, tempDir);

    assertThat(workspace.has(CMS_EN)).as("English CMS must exist before the agent run").isTrue();
    assertThat(workspace.has(CMS_DE)).as("German CMS must exist before the agent run").isTrue();
    assertThat(flatten(loadYaml(CMS_EN))).containsEntry(SEED_KEY_PATH, EN_SEED_VALUE);
    assertThat(flatten(loadYaml(CMS_DE))).containsEntry(SEED_KEY_PATH, DE_SEED_VALUE);
    dialogBefore = workspace.read(DIALOG);

    run = runner.run(PROMPT, workspace.root(), true);
  }

  @AfterAll
  void stop() {
    if (runner != null) {
      runner.close();
    }
  }

  @Test
  void cmsFilesAreCreatedWithMatchingKeysAndGermanTranslations() {
    assertCmsFilesExist();
    assertDialogUsesCms();

    Map<String, Object> rawEn = loadYaml(CMS_EN);
    Map<String, Object> rawDe = loadYaml(CMS_DE);
    assertBooleanLookingKeysAreStrings(rawEn, rawDe);

    Map<String, Object> en = flatten(rawEn);
    Map<String, Object> de = flatten(rawDe);
    assertCmsSeedEntriesPreserved(en, de);
    assertEnglishEntriesPreserveDialogText(en);
    assertCmsKeyPathsMatch(en, de);
    assertGermanTitleIsTranslated(en, de);
  }

  private void assertBooleanLookingKeysAreStrings(Map<String, Object> en, Map<String, Object> de) {
    Set<Object> enKeys = collectKeys(en);
    Set<Object> deKeys = collectKeys(de);

    assertThat(enKeys).as("Yes/No/True/False keys must be quoted so SnakeYAML keeps them as strings")
        .noneMatch(Boolean.class::isInstance);
    assertThat(deKeys).as("Yes/No/True/False keys must be quoted so SnakeYAML keeps them as strings")
        .noneMatch(Boolean.class::isInstance);
  }

  private void assertCmsFilesExist() {
    assertThat(run.invoked(SKILL))
        .as("the CMS skill must be invoked. The run replied: %s", run.transcript())
        .isTrue();
    assertThat(workspace.has(CMS_EN))
        .as("%s must remain available. The run replied: %s", CMS_EN, run.transcript())
        .isTrue();
    assertThat(workspace.has(CMS_DE))
        .as("%s must remain available. The run replied: %s", CMS_DE, run.transcript())
        .isTrue();
  }

  private void assertCmsSeedEntriesPreserved(Map<String, Object> en, Map<String, Object> de) {
    assertThat(en).as("the English CMS must preserve its existing entry")
        .containsEntry(SEED_KEY_PATH, EN_SEED_VALUE);
    assertThat(de).as("the German CMS must preserve its existing entry")
        .containsEntry(SEED_KEY_PATH, DE_SEED_VALUE);
  }

  private void assertDialogUsesCms() {
    String dialogAfter = workspace.read(DIALOG);
    assertThat(dialogAfter)
        .as("the dialog must be updated to reference CMS. The run replied: %s", run.transcript())
        .isNotEqualTo(dialogBefore)
        .contains("ivy.cms.co(")
        .doesNotContain(HARDCODED_TEXT);
  }

  private void assertEnglishEntriesPreserveDialogText(Map<String, Object> en) {
    assertThat(en.values())
        .as("the English CMS must preserve every user-visible string from the original dialog")
        .containsAll(HARDCODED_TEXT);
  }

  private void assertCmsKeyPathsMatch(Map<String, Object> en, Map<String, Object> de) {
    assertThat(de.keySet())
        .as("cms_de.yaml must define exactly the same key paths as cms_en.yaml")
        .containsExactlyInAnyOrderElementsOf(en.keySet());
  }

  private void assertGermanTitleIsTranslated(Map<String, Object> en, Map<String, Object> de) {
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