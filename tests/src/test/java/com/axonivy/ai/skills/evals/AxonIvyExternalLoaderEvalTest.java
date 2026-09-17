package com.axonivy.ai.skills.evals;

import static com.axonivy.ai.skills.judge.LlmAssert.assertThat;
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
import com.axonivy.ai.skills.judge.CopilotJudge;

@TestInstance(Lifecycle.PER_CLASS)
class AxonIvyExternalLoaderEvalTest {

  private static final Path IVY_PROJECT = Path.of("src/test/fixtures/ivy-project");
  private static final Path EXTERNAL_SOURCES = Path.of("src/test/fixtures/external-sources");

  private static final String SKILL = "axon-ivy-external-loader";
  private static final String MODEL = "gpt-5.4-mini";

  /** A field of the Japanese twin sheet: 申請部門コード */
  private static final String JAPANESE_TWIN_FIELD = "申請部門コード";

  private static final String PROMPT = """
      The folder external-requirements next to the project holds an Excel workbook and a BPMN export
      alongside a few other files. Load them and get the context out so we can write the leave
      approval requirements from it.
      """;

  private CopilotAgentRunner runner;
  private CopilotJudge judge;

  @TempDir
  static Path tempDir;

  private Workspace workspace;
  private AgentRun run;
  private String report;
  private Map<String, String> baseline;
  private Set<String> created;

  @BeforeAll
  void extractSources() {
    runner = new CopilotAgentRunner(MODEL, skillsDir());
    judge = new CopilotJudge(MODEL);

    workspace = materializeProjectWithSources(tempDir);
    baseline = checksums(workspace.root());

    run = runner.run(PROMPT, workspace.root(), true);
    report = run.transcript();

    created = new TreeSet<>(checksums(workspace.root()).keySet());
    created.removeAll(baseline.keySet());
  }

  @AfterAll
  void stop() {
    if (runner != null) {
      runner.close();
    }
    if (judge != null) {
      judge.close();
    }
  }

  @Test
  void loadsExcelAndBpmnIntoATraceableReport() {
    assertThat(run.invokedSkills())
        .extracting(InvokedSkill::name)
        .contains(SKILL);
    assertThat(report)
        .as("the skill answered nothing. Files the run created: %s", created)
        .isNotBlank();

    // Only reachable through load_excel.py — the workbook is a binary zip.
    assertThat(report)
        .contains("ApplicantCostCenter")
        .containsPattern("60\\s*[-–—]\\s*70");

    // Only reachable through load_bpmn.py — the annotation is empty in <text/> and lives in the
    // diagram half of the file, and the role comes from the lane.
    assertThat(report)
        .contains("10 working days")
        .contains("HR Operations")
        .containsIgnoringCase("June");

    // The English sheet has a Japanese twin; digesting both would double the field catalogue.
    assertThat(report).doesNotContain(JAPANESE_TWIN_FIELD);

    var afterRun = checksums(workspace.root());
    assertThat(afterRun)
        .as("sources and project files are read, never rewritten")
        .containsAllEntriesOf(baseline);

    assertThat(created)
        .as("dumps are working files, and nothing else may be left behind")
        .allSatisfy(path -> assertThat(path).startsWith(".external-context/"));

    assertThat(judge, report).satisfies("""
        Stakeholder_Briefing.docx is reported as unreadable, with none of its content invented.
        The conflicting 3-day and 10-day approval deadlines are both present and reported as a
        conflict rather than silently resolved.
        Extracted facts stay traceable to an Excel sheet and row, or to a BPMN pool, lane, or node.
        """);
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
