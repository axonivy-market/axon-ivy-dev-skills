#!/usr/bin/env python3
"""Run Maven build for an Axon Ivy project and summarize the result.

Usage:
    python verify-build.py [project_dir]

Runs `mvn clean install` and prints a condensed summary (build status,
errors, validateProject findings, generated data-class files) so it can be
read in one shot instead of re-running/paging through the raw Maven output.
No files are written; everything is printed to stdout.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path


def run_maven(project_dir: Path) -> str:
    proc = subprocess.run(
        ["mvn", "clean", "install"],
        cwd=str(project_dir),
        capture_output=True,
        text=True,
        shell=True,
    )
    return proc.stdout + "\n" + proc.stderr


def summarize(output: str, project_dir: Path) -> str:
    lines = output.splitlines()
    build_success = any("BUILD SUCCESS" in l for l in lines)
    build_failure = any("BUILD FAILURE" in l for l in lines)

    errors = [l for l in lines if re.search(r"\bERROR\b", l)]
    validate_summary = []
    in_summary = False
    for l in lines:
        if "Project validation summary" in l:
            in_summary = True
        if in_summary:
            validate_summary.append(l)
        if in_summary and "Duration" in l:
            break

    findings = [l for l in lines if "[INFO]" in l and " is not whitelisted" in l]

    generated_dir = project_dir / "target" / "generated-sources" / "ivy-dataclass"
    generated_files = sorted(p.relative_to(generated_dir).as_posix()
                              for p in generated_dir.rglob("*.java")) if generated_dir.exists() else []

    report = []
    report.append("=== BUILD STATUS ===")
    report.append("SUCCESS" if build_success else "FAILURE" if build_failure else "UNKNOWN")
    report.append("")
    report.append("=== ERRORS ===")
    report.extend(errors if errors else ["(none)"])
    report.append("")
    report.append("=== VALIDATE PROJECT SUMMARY ===")
    report.extend(validate_summary if validate_summary else ["(not found)"])
    report.append("")
    report.append(f"=== INFO FINDINGS (whitelist advisories) ({len(findings)}) ===")
    report.extend(findings if findings else ["(none)"])
    report.append("")
    report.append(f"=== GENERATED DATA CLASSES ({len(generated_files)}) ===")

    return "\n".join(report)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project_dir", nargs="?", default="my-project")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    if not project_dir.exists():
        print(f"Project directory not found: {project_dir}", file=sys.stderr)
        sys.exit(1)

    output = run_maven(project_dir)
    report = summarize(output, project_dir)

    print(report)


if __name__ == "__main__":
    main()
