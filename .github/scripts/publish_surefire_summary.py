#!/usr/bin/env python3

import glob
import os
import sys
import xml.etree.ElementTree as ET

STATUS_ICONS = {
    "PASSED": "✅ Passed",
    "FAILED": "❌ Failed",
    "SKIPPED": "⏭️ Skipped",
}


def to_int(value):
    try:
        return int(value or 0)
    except ValueError:
        return 0


def to_float(value):
    try:
        return float(value or 0.0)
    except ValueError:
        return 0.0


def md_escape(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def html_cell(text):
    """Escape text so it survives inside an HTML block in a single markdown table cell."""
    escaped = (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("|", "&#124;")
    )
    return escaped.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "&#10;")


def failure_reason(case):
    """Return the full failure/error/skip text of a test case, or "" when it passed."""
    for tag in ("failure", "error", "skipped"):
        node = case.find(tag)
        if node is None:
            continue
        message = (node.attrib.get("message") or "").strip()
        detail = (node.text or "").strip()
        return detail or message or node.attrib.get("type", "")
    return ""


def reason_cell(reason):
    if not reason:
        return ""
    return f"<details><summary>🔍 View</summary><pre>{html_cell(reason)}</pre></details>"


def publish_summary(report_dir, summary_path):
    files = sorted(glob.glob(f"{report_dir}/TEST-*.xml"))

    with open(summary_path, "a", encoding="utf-8") as out:
        out.write("## 🧪 Evals Summary\n\n")

        if not files:
            out.write(f"- ⚠️ No Surefire XML reports found in {report_dir}.\n")
            return

        totals = {
            "tests": 0,
            "failures": 0,
            "errors": 0,
            "skipped": 0,
            "time": 0.0,
        }
        test_cases = []

        for file_path in files:
            root = ET.parse(file_path).getroot()
            report_name = os.path.basename(file_path)
            tests = to_int(root.attrib.get("tests"))
            failures = to_int(root.attrib.get("failures"))
            errors = to_int(root.attrib.get("errors"))
            skipped = to_int(root.attrib.get("skipped"))
            elapsed = to_float(root.attrib.get("time"))

            totals["tests"] += tests
            totals["failures"] += failures
            totals["errors"] += errors
            totals["skipped"] += skipped
            totals["time"] += elapsed

            for case in root.findall("testcase"):
                case_name = case.attrib.get("name", "unknown")
                case_time = to_float(case.attrib.get("time"))
                if case.find("failure") is not None or case.find("error") is not None:
                    status = "FAILED"
                elif case.find("skipped") is not None:
                    status = "SKIPPED"
                else:
                    status = "PASSED"
                test_cases.append((report_name, case_name, status, case_time, failure_reason(case)))

        passed = totals["tests"] - totals["failures"] - totals["errors"] - totals["skipped"]
        overall = "✅ All tests passed" if totals["failures"] + totals["errors"] == 0 else "❌ Test failures detected"
        out.write(f"**{overall}**\n\n")
        out.write(f"- 🧾 Tests: {totals['tests']}\n")
        out.write(f"- ✅ Passed: {passed}\n")
        out.write(f"- ❌ Failures: {totals['failures']}\n")
        out.write(f"- 💥 Errors: {totals['errors']}\n")
        out.write(f"- ⏭️ Skipped: {totals['skipped']}\n")
        out.write(f"- ⏱️ Duration (s): {totals['time']:.3f}\n\n")

        out.write("### 📋 Test Cases\n\n")
        out.write("| Report | Test | Status | Time (s) | Reason |\n")
        out.write("| --- | --- | --- | ---: | --- |\n")
        for report_name, case_name, status, case_time, reason in test_cases:
            out.write(
                f"| {md_escape(report_name)} | {md_escape(case_name)} | {STATUS_ICONS[status]}"
                f" | {case_time:.3f} | {reason_cell(reason)} |\n"
            )

        out.write("\n### 📦 Artifacts\n\n")
        out.write("- 📄 Surefire XML reports are uploaded in this run's artifacts.\n")


def main():
    report_dir = sys.argv[1] if len(sys.argv) > 1 else "tests/target/surefire-reports"
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        raise SystemExit("GITHUB_STEP_SUMMARY is not set")

    publish_summary(report_dir, summary_path)


if __name__ == "__main__":
    main()
