package com.axonivy.ai.skills.evals;

import static com.axonivy.ai.skills.judge.LlmAssert.assertThat;
import static org.assertj.core.api.Assertions.assertThat;

import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.Map;
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
  private static final String MANIFEST = ".external-context/manifest.md";
  private static final String MODEL = "gpt-5.4-mini";

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
  private String manifest;
  private Map<String, String> baseline;

  @BeforeAll
  void extractSources() {
    runner = new CopilotAgentRunner(MODEL, skillsDir());
    judge = new CopilotJudge(MODEL);

    workspace = materializeProjectWithSources(tempDir);
    baseline = checksums(workspace.root());

    run = runner.run(PROMPT, workspace.root(), true);
    manifest = workspace.has(MANIFEST) ? workspace.read(MANIFEST) : "";
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
  void invokesLoaderAndWritesManifest() {
    assertThat(run.invokedSkills())
        .extracting(InvokedSkill::name)
        .contains(SKILL);

    assertThat(manifest).isNotBlank();
  }

  @Test
  void extractsExcelContent() {
    assertThat(manifest)
        .contains("ApplicantCostCenter")
        .contains("60-70");
  }

  @Test
  void extractsBpmnContent() {
    assertThat(manifest)
        .contains("10 working days")
        .contains("HR Operations")
        .containsIgnoringCase("June");
  }

  @Test
  void preservesGapsAndContradictions() {
    assertThat(judge, manifest).satisfies("""
        Stakeholder_Briefing.docx is reported as unreadable without invented content.
        The conflicting 3-day and 10-day approval deadlines are both reported as a conflict.
        """);
  }

  @Test
  void producesCleanTraceableContext() {
    assertThat(judge, manifest).satisfies("""
        Use the English workbook sheet without duplicating its Japanese twin.
        Do not treat the Version sheet as business requirements.
        Extracted facts remain traceable to their Excel or BPMN source location.
        """);
  }

  @Test
  void onlyWritesExternalContext() {
    var afterRun = checksums(workspace.root());

    assertThat(afterRun).containsAllEntriesOf(baseline);

    var produced = new HashSet<>(afterRun.keySet());
    produced.removeAll(baseline.keySet());

    assertThat(produced)
        .isNotEmpty()
        .allSatisfy(path -> assertThat(path).startsWith(".external-context/"));
  }

  @Test
  void handlesMissingPath(@TempDir Path missingPathDir) {
    var missingWorkspace = materializeProjectWithSources(missingPathDir);

    var missingRun = runner.run(
        "Load the Excel and BPMN files in vendor-specs so we can write requirements from them.",
        missingWorkspace.root(),
        true);

    // A manifest recording the missing path is fine; loading the folder next to it is not.
    var writtenManifest = missingWorkspace.has(MANIFEST) ? missingWorkspace.read(MANIFEST) : "";
    assertThat(writtenManifest).doesNotContain("LeaveRequest_Process.xlsx", "LeaveApproval.bpmn");

    assertThat(judge, missingRun.transcript()).satisfies("""
        Reports that vendor-specs is missing and does not invent or substitute content.
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