package com.axonivy.ai.skills.evals;

import static org.assertj.core.api.Assertions.assertThat;

import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;
import java.util.Map;
import java.util.Set;
import java.util.TreeSet;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;
import org.junit.jupiter.api.TestInstance.Lifecycle;
import org.junit.jupiter.api.io.TempDir;

import com.axonivy.ai.skills.agent.AgentRun;
import com.axonivy.ai.skills.agent.CopilotAgentRunner;
import com.axonivy.ai.skills.agent.InvokedSkill;
import com.axonivy.ai.skills.agent.Workspace;

@TestInstance(Lifecycle.PER_CLASS)
class AxonIvyExternalLoaderEvalTest {

  private static final Path IVY_PROJECT = Path.of("src/test/fixtures/ivy-project");
  private static final Path EXTERNAL_SOURCES = Path.of("src/test/fixtures/external-sources");

  private static final String SKILL = "axon-ivy-external-loader";
  private static final String MODEL = "gpt-5.4-mini";
  private static final String EXCEL_DUMP = ".external-context/excel_dump.txt";
  private static final String BPMN_DUMP = ".external-context/bpmn_dump.txt";

  private static final String PROMPT = """
      The folder external-requirements next to the project holds an Excel workbook and a BPMN export
      alongside a few other files. Load them and get the context out so we can write the leave
      approval requirements from it.
      """;

  private CopilotAgentRunner runner;

  @TempDir
  static Path tempDir;

  private Workspace workspace;
  private AgentRun run;
  private Map<String, String> baseline;
  private Set<String> created;

  @BeforeAll
  void extractSources() {
    runner = new CopilotAgentRunner(MODEL, skillsDir());

    workspace = materializeProjectWithSources(tempDir);
    baseline = checksums(workspace.root());

    run = runner.run(PROMPT, workspace.root(), true);

    created = new TreeSet<>(checksums(workspace.root()).keySet());
    created.removeAll(baseline.keySet());
  }

  @AfterAll
  void stop() {
    if (runner != null) {
      runner.close();
    }
  }

  @Test
  void runsBothLoadersOverTheExternalFolder() {
    assertThat(run.invokedSkills())
        .extracting(InvokedSkill::name)
        .contains(SKILL);

    assertThat(created)
        .as("the run left nothing behind. It replied: %s", run.transcript())
        .contains(EXCEL_DUMP, BPMN_DUMP);

    assertThat(workspace.read(EXCEL_DUMP))
        .as("load_excel.py must have opened the binary workbook")
        .contains("ApplicantCostCenter")
        .containsPattern("60\\s*[-–—]\\s*70");

    assertThat(workspace.read(BPMN_DUMP))
        .as("the default full format keeps annotations and lanes, --format flow drops them")
        .contains("10 working days")
        .contains("HR Operations")
        .containsIgnoringCase("June");

    assertThat(checksums(workspace.root()))
        .as("sources and project files are read, never rewritten")
        .containsAllEntriesOf(baseline);

    assertThat(created)
        .as("dumps are working files, and nothing else may be left behind")
        .allSatisfy(path -> assertThat(path).startsWith(".external-context/"));
  }

  private static String skillsDir() {
    return Path.of("..").toAbsolutePath().normalize().toString();
  }

  private static Workspace materializeProjectWithSources(Path target) {
    Workspace.materialize(IVY_PROJECT, target);
    return Workspace.materialize(EXTERNAL_SOURCES, target);
  }

  private static Map<String, String> checksums(Path root) {
    try (Stream<Path> files = Files.walk(root)) {
      return files
          .filter(Files::isRegularFile)
          .filter(path -> !root.relativize(path).toString().contains("target"))
          .collect(Collectors.toMap(
              path -> root.relativize(path).toString().replace('\\', '/'),
              AxonIvyExternalLoaderEvalTest::sha256));
    } catch (IOException ex) {
      throw new UncheckedIOException(ex);
    }
  }

  private static String sha256(Path file) {
    try {
      var digest = MessageDigest.getInstance("SHA-256");
      return HexFormat.of().formatHex(digest.digest(Files.readAllBytes(file)));
    } catch (IOException ex) {
      throw new UncheckedIOException(ex);
    } catch (NoSuchAlgorithmException ex) {
      throw new IllegalStateException(ex);
    }
  }
}
