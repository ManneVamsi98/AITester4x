"""Generate the "Flaky Test Analyzer" Langflow flow, and optionally push it into a running Langflow.

The custom component node is not hand-authored: its template is produced by Langflow's own
`create_component_template`, so the generated node matches what the UI builds when you drop
a Custom Component on the canvas.

    E:\\lf\\Scripts\\python.exe Chapter_09_Langflow\\build_flaky_analyzer_flow.py
    E:\\lf\\Scripts\\python.exe Chapter_09_Langflow\\build_flaky_analyzer_flow.py --push

Without `--push` it only writes `Flaky Analyzer.json`. With `--push` it also uploads the flow
to the Langflow instance (default http://127.0.0.1:7860), updating the existing flow of the
same name rather than creating duplicates.
"""

from __future__ import annotations

import argparse
import asyncio
import glob
import gzip
import json
import os
import secrets
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path

from langflow.interface.components import BASE_COMPONENTS_PATH, aget_all_types_dict

REPO = Path(__file__).resolve().parent.parent
CHAPTER = REPO / "Chapter_09_Langflow"
COMPONENT_FILE = CHAPTER / "flaky_analyzer_component.py"
OUT_FILE = CHAPTER / "Flaky Analyzer.json"

FLOW_NAME = "Flaky Test Analyzer"
FLOW_DESCRIPTION = (
    "Compares two Playwright JSON reports and counts the flaky test cases "
    "(tests whose pass/fail status differs between the two runs)."
)
DEFAULT_API_BASE = "http://127.0.0.1:7860"

LF_VERSION = "1.12.1"
COMPONENT_TYPE = "CustomComponent"

NODE_DEFAULTS = {
    "base_classes": [],
    "beta": False,
    "conditional_paths": [],
    "custom_fields": {},
    "description": FLOW_DESCRIPTION,
    "documentation": "",
    "edited": False,
    "frozen": False,
    "field_order": [],
    "output_types": [],
    "outputs": [],
    "pinned": False,
    "priority": 0,
    "recent": False,
    "show": True,
    "tool_mode": False,
    "lf_version": LF_VERSION,
}


def load_registry() -> dict:
    """Load every component definition Langflow exposes."""
    site = [p for p in sys.path if p.endswith("site-packages")][0]
    paths = [str(BASE_COMPONENTS_PATH)]
    for directory in glob.glob(os.path.join(site, "lfx_*", "components")):
        if os.path.isdir(directory):
            paths.append(directory)
    return asyncio.run(aget_all_types_dict(paths))


def node_id(component_type: str) -> str:
    """Langflow node ids look like `<type>-<5 char suffix>`."""
    suffix = "".join(secrets.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(5))
    return f"{component_type}-{suffix}"


def build_core_node(registry: dict, category: str, name: str, component_type: str,
                    position: tuple[float, float]) -> dict:
    """Build a node whose definition Langflow's registry already provides."""
    definition = json.loads(json.dumps(registry[category][name]))  # deep copy
    definition["lf_version"] = LF_VERSION

    identifier = node_id(component_type)
    return {
        "data": {"id": identifier, "node": definition, "showNode": True, "type": component_type},
        "draggable": True,
        "id": identifier,
        "measured": {"height": 200, "width": 320},
        "position": {"x": position[0], "y": position[1]},
        "selected": False,
        "type": "genericNode",
    }


def build_component_node(code: str, position: tuple[float, float]) -> dict:
    """Build the custom component node using Langflow's own template builder."""
    from lfx.custom.utils import create_component_template

    template, _instance = create_component_template(component={"code": code, "output_types": ["Message"]})
    definition = {**NODE_DEFAULTS, **template}
    definition["lf_version"] = LF_VERSION

    inputs = sorted(definition.get("template", {}))
    outputs = [output.get("name") for output in definition.get("outputs", [])]
    print(f"  component template keys : {len(definition)}")
    print(f"  component inputs        : {inputs}")
    print(f"  component outputs       : {outputs}")
    print(f"  component display_name  : {definition.get('display_name')}")
    if "code" not in definition.get("template", {}):
        raise SystemExit("refusing to write: the built template has no 'code' field")

    identifier = node_id(COMPONENT_TYPE)
    return {
        "data": {"id": identifier, "node": definition, "showNode": True, "type": COMPONENT_TYPE},
        "draggable": True,
        "id": identifier,
        "measured": {"height": 320, "width": 420},
        "position": {"x": position[0], "y": position[1]},
        "selected": False,
        "type": "genericNode",
    }


def make_edge(source_node: dict, output_name: str, output_types: list[str],
              target_node: dict, field_name: str, input_types: list[str], field_type: str) -> dict:
    """Build an edge using Langflow's `œ`-quoted handle encoding."""
    source_type = source_node["data"]["type"]
    target_id = target_node["data"]["id"]

    source_handle_obj = {
        "dataType": source_type,
        "id": source_node["data"]["id"],
        "name": output_name,
        "output_types": output_types,
    }
    target_handle_obj = {
        "fieldName": field_name,
        "id": target_id,
        "inputTypes": input_types,
        "type": field_type,
    }

    def enc(obj: dict) -> str:
        return json.dumps(obj, separators=(", ", ": ")).replace('"', "œ")

    source_handle = enc(source_handle_obj)
    target_handle = enc(target_handle_obj)

    return {
        "animated": False,
        "className": "",
        "data": {"sourceHandle": source_handle_obj, "targetHandle": target_handle_obj},
        "id": f"xy-edge__{source_handle}-{target_handle}",
        "selected": False,
        "source": source_node["data"]["id"],
        "sourceHandle": source_handle,
        "target": target_id,
        "targetHandle": target_handle,
    }


def build_flow(registry: dict, code: str) -> dict:
    """Assemble the flow: the analyzer feeding a Chat Output."""
    component = build_component_node(code, (-120, 20))
    chat_output = build_core_node(registry, "input_output", "ChatOutput", "ChatOutput", (420, 20))

    edges = [
        make_edge(
            component,
            "report",
            ["Message"],
            chat_output,
            "input_value",
            ["Data", "JSON", "DataFrame", "Table", "Message"],
            "other",
        )
    ]

    return {
        "data": {
            "edges": edges,
            "nodes": [component, chat_output],
            "viewport": {"x": 60, "y": 120, "zoom": 0.9},
        },
        "description": FLOW_DESCRIPTION,
        "endpoint_name": None,
        "id": str(uuid.uuid4()),
        "is_component": False,
        "last_tested_version": LF_VERSION,
        "locked": False,
        "name": FLOW_NAME,
        "tags": [],
    }


def api(method: str, path: str, token: str | None = None, payload: dict | None = None):
    """Call the Langflow API and return the decoded JSON body."""
    request = urllib.request.Request(f"{API_BASE}{path}", method=method)
    request.add_header("Accept-Encoding", "identity")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    body = None
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        request.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(request, body, timeout=300) as response:
            raw = response.read()
            if response.headers.get("Content-Encoding", "").lower() == "gzip":
                raw = gzip.decompress(raw)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:400]
        raise RuntimeError(f"{method} {path} -> HTTP {exc.code} {exc.reason}: {detail}") from exc
    text = raw.decode("utf-8")
    return json.loads(text) if text.strip() else None


def push(flow: dict) -> None:
    """Create or update the flow in the running Langflow instance."""
    token = api("GET", "/api/v1/auto_login")["access_token"]

    listing = api("GET", "/api/v1/flows/?remove_example_flows=true", token)
    flows = listing.get("items", []) if isinstance(listing, dict) else listing
    existing = next((item for item in flows if item.get("name") == FLOW_NAME), None)

    payload = {"name": FLOW_NAME, "description": FLOW_DESCRIPTION, "data": flow["data"]}
    if existing:
        saved = api("PUT", f"/api/v1/flows/{existing['id']}", token, payload)
        action = "updated"
    else:
        saved = api("POST", "/api/v1/flows/", token, payload)
        action = "created"

    flow_id = saved.get("id") if isinstance(saved, dict) else None
    print(f"  {action} flow '{FLOW_NAME}' (id {flow_id})")
    print(f"  open it at {API_BASE}/flow/{flow_id}")


API_BASE = DEFAULT_API_BASE


def main(argv: list[str] | None = None) -> int:
    """Build the flow export and optionally push it."""
    parser = argparse.ArgumentParser(description="Build the Flaky Test Analyzer Langflow flow.")
    parser.add_argument("--push", action="store_true", help="upload the flow to the running Langflow instance")
    parser.add_argument("--api-base", default=DEFAULT_API_BASE, help=f"Langflow base URL (default {DEFAULT_API_BASE})")
    args = parser.parse_args(argv)

    global API_BASE
    API_BASE = args.api_base.rstrip("/")

    code = COMPONENT_FILE.read_text(encoding="utf-8")
    print(f"component: {COMPONENT_FILE.name} ({len(code)} chars)")

    registry = load_registry()
    print(f"registry : {sum(len(v) for v in registry.values())} components")

    flow = build_flow(registry, code)
    serialized = json.dumps(flow, indent=2, ensure_ascii=False)
    OUT_FILE.write_text(serialized + "\n", encoding="utf-8")
    print(f"wrote {OUT_FILE} ({len(serialized)} chars, {len(flow['data']['nodes'])} nodes, {len(flow['data']['edges'])} edges)")

    if args.push:
        try:
            push(flow)
        except RuntimeError as exc:
            print(f"push failed: {exc}", file=sys.stderr)
            return 2
        except urllib.error.URLError as exc:
            print(f"push failed: cannot reach {API_BASE} ({exc.reason})", file=sys.stderr)
            print("start Langflow first, see Chapter_09_Langflow/README.md", file=sys.stderr)
            return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
