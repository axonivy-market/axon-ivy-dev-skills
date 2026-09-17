#!/usr/bin/env python3
"""Extract BPMN 2.0 files as readable text for requirements analysis.

Requires only the Python standard library.
"""

from __future__ import annotations

import argparse
import glob
import html
import io
import os
import re
import sys
import xml.etree.ElementTree as ET


BPMN_EXTS = (".bpmn", ".bpmn2", ".bpmn20.xml")

FLOW_NODE_TAGS = {
    "startEvent", "endEvent",
    "intermediateCatchEvent", "intermediateThrowEvent",
    "boundaryEvent",
    "task", "userTask", "manualTask", "serviceTask", "scriptTask",
    "sendTask", "receiveTask", "businessRuleTask",
    "callActivity", "subProcess", "transaction",
    "exclusiveGateway", "inclusiveGateway", "parallelGateway",
    "complexGateway", "eventBasedGateway",
}

PREFERRED_DATA_KEYS = (
    "bp_ShapeName",
    "bp_DisplayNumber",
    "bp_ShapeNumber",
    "bp_Department",
    "bp_Content",
    "bp_Purpose",
    "bp_System",
    "bp_DiagramID",
    "bp_DiagramType",
)


def ln(tag: str) -> str:
    """Return the local name of a namespaced XML tag."""
    return tag.rsplit("}", 1)[-1]


def attrs(elem: ET.Element) -> dict[str, str]:
    """Return attributes without namespace prefixes."""
    return {ln(key): value for key, value in elem.attrib.items()}


def clean(text: str | None, max_chars: int, keep_lines: bool = False) -> str:
    """Clean HTML/XML-ish text into readable plain text."""
    if not text:
        return ""

    text = html.unescape(str(text))
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(
        r"</?(p|div|li|ul|ol|span|b|i|u|font)[^>]*>",
        "",
        text,
        flags=re.I,
    )
    text = html.unescape(text)
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("_x000D_", "")

    if keep_lines:
        lines = [
            re.sub(r"[ \t]+", " ", line).strip()
            for line in text.split("\n")
        ]
        text = "\n".join(line for line in lines if line)
    else:
        text = re.sub(r"\s+", " ", text).strip()

    if len(text) > max_chars:
        text = text[:max_chars] + f"... [truncated, {len(text)} chars total]"

    return text


def resolve_inputs(patterns: list[str]) -> list[str]:
    """Resolve files, directories, and glob patterns."""
    found = []

    for pattern in patterns:
        if os.path.isdir(pattern):
            found += [
                os.path.join(pattern, name)
                for name in os.listdir(pattern)
                if name.lower().endswith(BPMN_EXTS)
            ]
        elif os.path.isfile(pattern):
            found.append(pattern)
        else:
            found += [
                path
                for path in glob.glob(pattern)
                if os.path.isfile(path)
            ]

    seen = set()
    result = []

    for path in sorted(found):
        key = os.path.normcase(os.path.abspath(path))
        if key not in seen:
            seen.add(key)
            result.append(path)

    return result


def indent(text: str, prefix: str) -> str:
    return "\n".join(prefix + line for line in text.splitlines())


class Bpmn:
    """Indexed BPMN document with human-readable reference resolution."""

    def __init__(self, root: ET.Element, max_chars: int):
        self.root = root
        self.max_chars = max_chars

        self.by_id = {
            a["id"]: elem
            for elem in root.iter()
            if (a := attrs(elem)).get("id")
        }

        self.di_text: dict[str, str] = {}
        self.annotations: dict[str, list[str]] = {}
        self.attached_annotations: set[str] = set()
        self.category_values: dict[str, str] = {}

        self._index_di()
        self._index_annotations()

        for elem in self.find("categoryValue"):
            a = attrs(elem)
            if a.get("id"):
                self.category_values[a["id"]] = a.get("value", "")

    def find(self, *tags: str) -> list[ET.Element]:
        wanted = set(tags)
        return [elem for elem in self.root.iter() if ln(elem.tag) in wanted]

    def _index_di(self) -> None:
        """Recover labels stored in BPMN diagram-interchange extensions."""
        for shape in self.find("BPMNShape", "BPMNEdge"):
            target = attrs(shape).get("bpmnElement")
            if not target:
                continue

            for elem in shape.iter():
                if ln(elem.tag) == "htmlText" and (elem.text or "").strip():
                    self.di_text.setdefault(
                        target,
                        clean(elem.text, self.max_chars, keep_lines=True),
                    )
                    break

    def _index_annotations(self) -> None:
        """Associate BPMN text annotations with their referenced elements."""
        for assoc in self.find("association"):
            a = attrs(assoc)
            source = a.get("sourceRef")
            target = a.get("targetRef")

            if not source or not target:
                continue

            for annotation_id, element_id in (
                (source, target),
                (target, source),
            ):
                annotation = self.by_id.get(annotation_id)

                if annotation is None or ln(annotation.tag) != "textAnnotation":
                    continue

                self.attached_annotations.add(annotation_id)

                text = self.annotation_text(annotation, annotation_id)
                if text:
                    self.annotations.setdefault(element_id, []).append(text)

                break

    def annotation_text(self, elem: ET.Element, eid: str) -> str:
        text = next(
            (
                child.text
                for child in elem
                if ln(child.tag) == "text"
                and (child.text or "").strip()
            ),
            None,
        )

        return (
            clean(text, self.max_chars, keep_lines=True)
            if text
            else self.di_text.get(eid, "")
        )

    def name_of(self, eid: str | None) -> str:
        """Resolve an ID to its semantic name or diagram label."""
        if not eid:
            return "(none)"

        elem = self.by_id.get(eid)

        if elem is not None:
            name = attrs(elem).get("name", "").strip()
            if name:
                return clean(name, 200)

        if label := self.di_text.get(eid):
            return clean(label, 200)

        suffix = eid[-6:]

        if elem is not None:
            return f"(unnamed {ln(elem.tag)} …{suffix})"

        return f"(unresolved ref …{suffix})"

    def documentation(self, elem: ET.Element) -> str:
        parts = [
            clean(child.text, self.max_chars, keep_lines=True)
            for child in elem
            if ln(child.tag) == "documentation"
        ]
        return "\n".join(part for part in parts if part)

    def custom_data(self, elem: ET.Element) -> list[tuple[str, str]]:
        found = []

        for ext in elem:
            if ln(ext.tag) != "extensionElements":
                continue

            for node in ext.iter():
                if ln(node.tag) not in {
                    "customDataValue",
                    "property",
                    "inputParameter",
                    "outputParameter",
                }:
                    continue

                a = attrs(node)
                key = a.get("name", "")
                value = (
                    clean(node.text, self.max_chars, keep_lines=True)
                    or a.get("value", "")
                )

                if key and value:
                    found.append((key, value))

        order = {key: i for i, key in enumerate(PREFERRED_DATA_KEYS)}
        return sorted(
            found,
            key=lambda item: (
                order.get(item[0], len(order)),
                item[0],
            ),
        )

    def event_definitions(self, elem: ET.Element) -> list[str]:
        events = []

        for child in elem:
            tag = ln(child.tag)

            if not tag.endswith("EventDefinition"):
                continue

            detail = next(
                (
                    f"={sub.text.strip()}"
                    for sub in child.iter()
                    if ln(sub.tag).startswith("time")
                    and (sub.text or "").strip()
                ),
                "",
            )

            events.append(tag.removesuffix("EventDefinition") + detail)

        return events

    def phases(self, process: ET.Element) -> list[str]:
        return [
            clean(attrs(elem).get("name", ""), 200)
            for elem in process.iter()
            if ln(elem.tag) == "phase"
        ]


def flow_info(doc: Bpmn, flow: ET.Element) -> tuple[str, str, str]:
    """Return source, label/condition, and target for a flow."""
    a = attrs(flow)

    condition = next(
        (
            clean(child.text, 200)
            for child in flow
            if ln(child.tag) == "conditionExpression"
            and (child.text or "").strip()
        ),
        "",
    )

    return (
        doc.name_of(a.get("sourceRef")),
        clean(a.get("name", ""), 200) or condition,
        doc.name_of(a.get("targetRef")),
    )


def render_lanes(
    out: io.StringIO,
    process: ET.Element,
) -> dict[str, str]:
    """Render lane hierarchy and return node ID -> lane path."""
    lane_of: dict[str, str] = {}
    lanes: list[tuple[int, str, int]] = []

    def walk(container: ET.Element, path: list[str], depth: int) -> None:
        for lane in container:
            if ln(lane.tag) != "lane":
                continue

            name = clean(attrs(lane).get("name", ""), 200) or "(unnamed lane)"
            lane_path = path + [name]
            full_path = " / ".join(lane_path)

            members = [
                (child.text or "").strip()
                for child in lane
                if ln(child.tag) == "flowNodeRef"
            ]

            lanes.append((depth, full_path, len(members)))

            for member in members:
                lane_of[member] = full_path

            for child in lane:
                if ln(child.tag) == "childLaneSet":
                    walk(child, lane_path, depth + 1)

    for lane_set in process:
        if ln(lane_set.tag) == "laneSet":
            walk(lane_set, [], 0)

    if lanes:
        out.write("  LANES:\n")

        for depth, path, count in lanes:
            out.write(
                f"    {'  ' * depth}- {path} ({count} nodes)\n"
            )

    return lane_of


def render_node(
    out: io.StringIO,
    doc: Bpmn,
    elem: ET.Element,
    lane_of: dict[str, str],
    args,
) -> None:
    a = attrs(elem)
    eid = a.get("id", "")

    extras = []

    if eid in lane_of:
        extras.append(f"lane: {lane_of[eid]}")

    if direction := a.get("gatewayDirection"):
        extras.append(direction)

    if events := doc.event_definitions(elem):
        extras.append("trigger: " + ", ".join(events))

    header = f"  • [{ln(elem.tag)}] {doc.name_of(eid)}"

    if extras:
        header += "   (" + "; ".join(extras) + ")"

    out.write(header + "\n")

    if args.format != "flow":
        if text := doc.documentation(elem):
            out.write(indent(text, "      | ") + "\n")

        for note in doc.annotations.get(eid, []):
            out.write(indent(f"note: {note}", "      ~ ") + "\n")

    if args.format == "full" and not args.no_custom_data:
        for key, value in doc.custom_data(elem):
            out.write(
                f"      · {key}: {value.replace(chr(10), ' / ')}\n"
            )

    if args.format != "prose":
        for child in elem:
            if ln(child.tag) != "outgoing":
                continue

            flow = doc.by_id.get((child.text or "").strip())

            if flow is None:
                continue

            _, label, target = flow_info(doc, flow)
            marker = f" [{label}]" if label else ""

            out.write(f"      →{marker} {target}\n")

    out.write("\n")


def render_collaborations(
    out: io.StringIO,
    doc: Bpmn,
) -> None:
    for collab in doc.find("collaboration"):
        name = clean(attrs(collab).get("name", ""), 200) or "(unnamed)"

        out.write("-" * 100 + "\n")
        out.write(f"COLLABORATION: {name}\n")
        out.write("-" * 100 + "\n")

        for participant in collab.iter():
            if ln(participant.tag) == "participant":
                name = clean(attrs(participant).get("name", ""), 200)
                out.write(f"  POOL: {name}\n")

        flows = [
            elem
            for elem in collab.iter()
            if ln(elem.tag) == "messageFlow"
        ]

        if flows:
            out.write("\n  MESSAGE FLOWS (cross-pool):\n")

            for flow in flows:
                source, label, target = flow_info(doc, flow)
                arrow = f"--[{label}]-->" if label else "-->"
                out.write(f"    {source} {arrow} {target}\n")

        out.write("\n")


def render_process(
    out: io.StringIO,
    doc: Bpmn,
    process: ET.Element,
    args,
) -> None:
    name = clean(attrs(process).get("name", ""), 200) or "(unnamed)"

    out.write("-" * 100 + "\n")
    out.write(f"PROCESS: {name}\n")
    out.write("-" * 100 + "\n")

    phases = [phase for phase in doc.phases(process) if phase]

    if phases:
        out.write("  PHASES: " + " → ".join(phases) + "\n")

    lane_of = render_lanes(out, process)

    if args.format != "flow":
        if text := doc.documentation(process):
            out.write(indent(text, "  | ") + "\n")

    out.write("\n")

    nodes = [
        elem
        for elem in process.iter()
        if ln(elem.tag) in FLOW_NODE_TAGS
    ]

    if nodes:
        out.write("  FLOW NODES:\n\n")

        for node in nodes:
            render_node(out, doc, node, lane_of, args)

    if args.format == "prose":
        return

    flows = [
        elem
        for elem in process.iter()
        if ln(elem.tag) == "sequenceFlow"
    ]

    if flows:
        out.write("  SEQUENCE FLOWS:\n")

        for flow in flows:
            source, label, target = flow_info(doc, flow)
            arrow = f"--[{label}]-->" if label else "-->"
            out.write(f"    {source} {arrow} {target}\n")

        out.write("\n")


def render_annotations(
    out: io.StringIO,
    doc: Bpmn,
    args,
) -> None:
    if args.format == "flow":
        return

    annotations = []

    for elem in doc.find("textAnnotation"):
        eid = attrs(elem).get("id", "")

        if eid not in doc.attached_annotations:
            if text := doc.annotation_text(elem, eid):
                annotations.append(text)

    if not annotations:
        return

    out.write("-" * 100 + "\n")
    out.write("UNATTACHED ANNOTATIONS\n")
    out.write("-" * 100 + "\n")

    for text in annotations:
        out.write(indent(text, "  ~ ") + "\n")

    out.write("\n")


def render_groups(
    out: io.StringIO,
    doc: Bpmn,
) -> None:
    labels = []

    for group in doc.find("group"):
        a = attrs(group)

        label = (
            doc.di_text.get(a.get("id", ""), "")
            or doc.category_values.get(a.get("categoryValueRef", ""), "")
        )

        if label:
            labels.append(clean(label, 200))

    if labels:
        out.write("GROUPS: " + " | ".join(labels) + "\n\n")


def dump_document(
    out: io.StringIO,
    path: str,
    args,
) -> None:
    root = ET.parse(path).getroot()

    if ln(root.tag) != "definitions":
        raise ValueError(
            f"not a BPMN document: root is <{ln(root.tag)}>, "
            "expected <definitions>"
        )

    doc = Bpmn(root, args.max_chars)
    root_attrs = attrs(root)

    out.write("=" * 100 + "\n")
    out.write(f"FILE: {os.path.abspath(path)}\n")

    if exporter := root_attrs.get("exporter"):
        version = root_attrs.get("exporterVersion", "")
        out.write(f"EXPORTER: {exporter} {version}\n")

    out.write("=" * 100 + "\n\n")

    counted = FLOW_NODE_TAGS | {
        "sequenceFlow",
        "messageFlow",
        "textAnnotation",
        "lane",
        "participant",
    }

    counts: dict[str, int] = {}

    for elem in root.iter():
        tag = ln(elem.tag)
        if tag in counted:
            counts[tag] = counts.get(tag, 0) + 1

    if counts:
        out.write(
            "ELEMENT COUNTS: "
            + ", ".join(
                f"{key}={value}"
                for key, value in sorted(counts.items())
            )
            + "\n\n"
        )

    render_collaborations(out, doc)

    for process in doc.find("process"):
        render_process(out, doc, process, args)

    render_annotations(out, doc, args)
    render_groups(out, doc)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract BPMN files as readable text."
    )

    parser.add_argument(
        "inputs",
        nargs="+",
        help="BPMN files, directories, or glob patterns",
    )
    parser.add_argument(
        "--out",
        help="Write UTF-8 output to this file instead of stdout",
    )
    parser.add_argument(
        "--format",
        choices=("full", "flow", "prose"),
        default="full",
        help=(
            "full: structure + prose + custom data; "
            "flow: process structure only; "
            "prose: documentation and annotations"
        ),
    )
    parser.add_argument(
        "--no-custom-data",
        action="store_true",
        help="Omit vendor extension fields",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=4000,
        help="Maximum characters per text block",
    )

    args = parser.parse_args()

    if args.max_chars <= 0:
        parser.error("--max-chars must be > 0")

    paths = resolve_inputs(args.inputs)

    if not paths:
        missing = [p for p in args.inputs if not os.path.exists(p) and not glob.glob(p)]
        if missing:
            sys.stderr.write(f"ERROR: path not found: {', '.join(missing)}\n")
        else:
            sys.stderr.write(f"ERROR: no BPMN files under: {', '.join(args.inputs)}\n")
        return 1

    out = io.StringIO()

    for path in paths:
        try:
            dump_document(out, path, args)

        except ET.ParseError as exc:
            out.write(
                f"{'=' * 100}\n"
                f"FILE: {path}\n"
                f"ERROR: not well-formed XML: {exc}\n\n"
            )
            sys.stderr.write(
                f"WARNING: failed to parse {path}: {exc}\n"
            )

        except Exception as exc:
            out.write(
                f"{'=' * 100}\n"
                f"FILE: {path}\n"
                f"ERROR: {type(exc).__name__}: {exc}\n\n"
            )
            sys.stderr.write(
                f"WARNING: failed to read {path}: {exc}\n"
            )

    text = out.getvalue()

    if args.out:
        path = os.path.abspath(args.out)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "w", encoding="utf-8") as file:
            file.write(text)

        print(
            f"Wrote {len(text)} chars from "
            f"{len(paths)} BPMN file(s) to {args.out}"
        )

    else:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(
                encoding="utf-8",
                errors="replace",
            )

        sys.stdout.write(text)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())