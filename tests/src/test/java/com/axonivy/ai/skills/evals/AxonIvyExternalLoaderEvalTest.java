package com.axonivy.ai.skills.evals;

import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;
import java.util.Map;
import java.util.Set;
import java.util.TreeSet;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import static org.assertj.core.api.Assertions.assertThat;
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
  private static final Path LOADERS = Path.of("..", "delivery-workflow", "skills", "axon-ivy-external-loader", "loaders")
      .toAbsolutePath()
      .normalize();

  private static final String SKILL = "axon-ivy-external-loader";
  private static final String MODEL = "gpt-5.4-mini";

  private static final String PROMPT = """
      Load the Excel and BPMN files in `external-requirements` and summarize the leave approval
      context. Do not modify any files.
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
  void runsBothLoadersOverTheExternalFolder() throws Exception {
    assertThat(run.usage().modelCalls())
        .as("the agent made 0 model calls and replied %s — this is a transient Copilot "
            + "API/quota/auth failure, not a skill or test defect. Re-run the job.", run.transcript())
        .isGreaterThan(0);

    assertThat(run.invokedSkills())
        .extracting(InvokedSkill::name)
        .contains(SKILL);

    String excelOutput = runLoader(
      "load_excel.py",
      workspace.root().resolve("external-requirements/LeaveRequest_Process.xlsx"));
    assertThat(excelOutput)
      .contains("ApplicantCostCenter")
      .contains("[A4]")
      .contains("Mandatory between June and August")
      .contains("60-70 requests per month");

    String bpmnOutput = runLoader(
      "load_bpmn.py",
      workspace.root().resolve("external-requirements/LeaveApproval.bpmn"));
    assertThat(bpmnOutput)
      .contains("HR Operations")
      .contains("Manager Approval")
      .contains("10 working days")
      .contains("June to August")
      .contains("Approved? --[Approved]--> Leave booked");

    assertThat(checksums(workspace.root()))
      .as("the source files must not be modified")
      .containsAllEntriesOf(baseline);

    assertThat(created)
        .as("the skill must not write files unless the user explicitly asks for a saved digest")
        .isEmpty();
  }

  private static String skillsDir() {
    return Path.of("..").toAbsolutePath().normalize().toString();
  }

  private static String runLoader(String script, Path source) throws IOException, InterruptedException {
    Path outputFile = Files.createTempFile("axonivy-loader-", ".log");
    Process process = new ProcessBuilder("python", LOADERS.resolve(script).toString(), source.toString())
        .redirectErrorStream(true)
        .redirectOutput(outputFile.toFile())
        .start();

    try {
      if (!process.waitFor(30, TimeUnit.SECONDS)) {
        process.destroyForcibly();
        throw new AssertionError(script + " timed out");
      }

      String output = Files.readString(outputFile, StandardCharsets.UTF_8);
      assertThat(process.exitValue())
          .as("%s output: %s", script, output)
          .isZero();
      return output;
    } finally {
      if (process.isAlive()) {
        process.destroyForcibly();
      }
      Files.deleteIfExists(outputFile);
    }
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
