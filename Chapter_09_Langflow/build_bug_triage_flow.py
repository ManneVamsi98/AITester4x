"""Generate the "Bug Triage AI Agent" Langflow flow export.

Langflow node objects embed each component's full definition, so this script builds
the nodes from Langflow's own component registry rather than hand-authoring them:

  * core components (ChatInput, ChatOutput, Agent, APIRequest) come from the registry
  * the Groq model is a bundle component, so its definition is reused verbatim from
    an existing export of the same Langflow version

Run with the Langflow venv:

    E:\\lf\\Scripts\\python.exe Chapter_09_Langflow/build_bug_triage_flow.py

No credentials are written. Every auth field is emitted empty; supply them in the
Langflow UI (or via Global Variables) after import.
"""

from __future__ import annotations

import asyncio
import glob
import json
import os
import re
import secrets
import sys
from pathlib import Path

from langflow.interface.components import BASE_COMPONENTS_PATH, aget_all_types_dict

REPO = Path(__file__).resolve().parent.parent
CHAPTER = REPO / "Chapter_09_Langflow"
PROMPT_FILE = (
    REPO / "Chapter_08_n8n" / "Agents" / "reference" / "01_ModifiedBugTriagePrompt.prompt.md"
)
OUT_FILE = CHAPTER / "Bug Triage AI Agent.json"
GROQ_TEMPLATE_SOURCE = CHAPTER / "Sample workflow.json"

LF_VERSION = "1.12.1"
GROQ_TYPE = "ext:groq:GroqModel@official"
GROQ_MODEL = "qwen/qwen3.8-27b"

# Same target as the n8n workflow 04_BugTriageAIAgent.
SHEET_ID = "1s-_sDyKBAEAbUXAXHQrnSpP7XMk9MdwsW4XniTnIs2s"
SHEET_TAB = "BugTRIAGE"
JIRA_SEARCH_URL = "https://YOUR-SITE.atlassian.net/rest/api/2/search"
SHEETS_APPEND_URL = (
    f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}"
    f"/values/{SHEET_TAB}!A1:append?valueInputOption=USER_ENTERED"
)

TOOL_OUTPUT = {
    "allows_loop": False,
    "cache": True,
    "display_name": "Toolset",
    "group_outputs": False,
    "hidden": None,
    "loop_types": None,
    "method": "to_toolkit",
    "name": "component_as_tool",
    "options": None,
    "required_inputs": None,
    "selected": "Tool",
    "tool_mode": True,
    "types": ["Tool"],
    "value": "__UNDEFINED__",
}


def load_registry() -> dict:
    """Load every component definition Langflow exposes."""
    site = [p for p in sys.path if p.endswith("site-packages")][0]
    paths = [str(BASE_COMPONENTS_PATH)]
    for d in glob.glob(os.path.join(site, "lfx_*", "components")):
        if os.path.isdir(d):
            paths.append(d)
    return asyncio.run(aget_all_types_dict(paths))


def node_id(component_type: str) -> str:
    """Langflow node ids look like `<type>-<5 char suffix>`."""
    suffix = "".join(secrets.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
                     for _ in range(5))
    return f"{component_type}-{suffix}"


def build_core_node(registry: dict, category: str, name: str, component_type: str,
                    position: tuple[float, float], show_node: bool = True,
                    selected_output: str | None = None) -> dict:
    """Build a node whose definition Langflow's registry already provides."""
    definition = json.loads(json.dumps(registry[category][name]))  # deep copy
    definition["lf_version"] = LF_VERSION

    data: dict = {"id": node_id(component_type), "node": definition}
    if selected_output:
        data["selected_output"] = selected_output
    data["showNode"] = show_node
    data["type"] = component_type

    return {
        "data": data,
        "dragging": False,
        "id": data["id"],
        "measured": {"height": 200, "width": 320},
        "position": {"x": position[0], "y": position[1]},
        "selected": False,
        "type": "genericNode",
    }


def build_groq_node(position: tuple[float, float]) -> dict:
    """Reuse the authentic Groq bundle node definition from the existing export."""
    flow = json.loads(GROQ_TEMPLATE_SOURCE.read_text(encoding="utf-8"))
    source = next(n for n in flow["data"]["nodes"] if n["data"]["type"] == GROQ_TYPE)
    node = json.loads(json.dumps(source))  # deep copy

    new_id = node_id(GROQ_TYPE)
    node["id"] = new_id
    node["data"]["id"] = new_id
    node["position"] = {"x": position[0], "y": position[1]}
    node["data"]["selected_output"] = "model_output"

    template = node["data"]["node"]["template"]
    template["model_name"]["value"] = GROQ_MODEL
    template["api_key"]["value"] = ""       # never ship a key
    template["base_url"]["value"] = "https://api.groq.com"
    return node


def enable_tool_mode(node: dict, tool_name: str, description: str,
                     args: dict[str, dict]) -> None:
    """Turn a component into an agent tool.

    Langflow does this by setting node.tool_mode, appending a `component_as_tool`
    output, and recording the tool schema in a `tools_metadata` template field.
    """
    definition = node["data"]["node"]
    definition["tool_mode"] = True
    definition["outputs"] = list(definition["outputs"]) + [json.loads(json.dumps(TOOL_OUTPUT))]
    definition["template"]["tools_metadata"] = {
        "_input_type": "ToolsInput",
        "advanced": False,
        "display_name": "Actions",
        "dynamic": False,
        "info": "Modify tool names and descriptions to help agents understand when to use each tool.",
        "is_list": True,
        "list_add_label": "Add More",
        "name": "tools_metadata",
        "override_skip": False,
        "placeholder": "",
        "real_time_refresh": True,
        "required": False,
        "show": True,
        "title_case": False,
        "tool_mode": False,
        "trace_as_metadata": True,
        "track_in_telemetry": False,
        "type": "tools",
        "value": [
            {
                "args": args,
                "description": description,
                "display_description": description,
                "display_name": tool_name,
                "name": tool_name,
                "readonly": False,
                "status": True,
                "tags": [tool_name],
            }
        ],
    }


def make_edge(source_node: dict, output_name: str, output_types: list[str],
              target_node: dict, field_name: str, input_types: list[str],
              field_type: str) -> dict:
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
        raw = json.dumps(obj, separators=(", ", ": "))
        return raw.replace('"', "œ")

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


def read_triage_prompt() -> str:
    """The 370-line triage prompt, embedded verbatim."""
    text = PROMPT_FILE.read_text(encoding="utf-8")
    # Strip a leading H1 if the file has one, so the prompt starts at the persona line.
    return text.strip()


def main() -> None:
    registry = load_registry()
    prompt = read_triage_prompt()
    print(f"prompt: {len(prompt)} chars, {prompt.count(chr(10)) + 1} lines")

    chat_input = build_core_node(registry, "input_output", "ChatInput", "ChatInput", (-760, 20), True)
    chat_input["data"]["node"]["template"]["input_value"]["value"] = (
        "Retrieve the Jira issues and triage them, then write each result to Google Sheets."
    )

    agent = build_core_node(registry, "models_and_agents", "Agent", "Agent", (-120, 20),
                            True, selected_output="response")
    agent_tpl = agent["data"]["node"]["template"]
    agent_tpl["system_prompt"]["value"] = prompt
    agent_tpl["stream"]["value"] = False          # keep the final JSON clean
    agent_tpl["max_iterations"]["value"] = 30     # batch triage needs many tool calls

    groq = build_groq_node((-440, 420))

    jira_tool = build_core_node(registry, "data_source", "APIRequest", "APIRequest", (-440, -320), True)
    jira_tpl = jira_tool["data"]["node"]["template"]
    jira_tpl["mode"]["value"] = "URL"
    jira_tpl["method"]["value"] = "GET"
    jira_tpl["url_input"]["value"] = JIRA_SEARCH_URL
    jira_tpl["query_params"]["value"] = json.dumps(
        {"jql": 'textfields ~ "bug*" ORDER BY createdDate', "maxResults": 100}
    )
    jira_tpl["headers"]["value"] = [
        {"key": "Accept", "value": "application/json"},
        {"key": "Authorization", "value": ""},  # fill in: Basic <base64(email:token)>
    ]
    enable_tool_mode(
        jira_tool,
        "jira_search_issues",
        "Search Jira for issues using JQL. Returns matching issues as JSON. Read-only.",
        {
            "url_input": {
                "default": JIRA_SEARCH_URL,
                "description": "Jira REST search endpoint, e.g. https://your-site.atlassian.net/rest/api/2/search",
                "title": "Jira Search URL",
                "type": "string",
            }
        },
    )

    sheets_tool = build_core_node(registry, "data_source", "APIRequest", "APIRequest", (300, -320), True)
    sheets_tpl = sheets_tool["data"]["node"]["template"]
    sheets_tpl["mode"]["value"] = "URL"
    sheets_tpl["method"]["value"] = "POST"
    sheets_tpl["url_input"]["value"] = SHEETS_APPEND_URL
    sheets_tpl["headers"]["value"] = [
        {"key": "Content-Type", "value": "application/json"},
        {"key": "Authorization", "value": ""},  # fill in: Bearer <google oauth token>
    ]
    sheets_tpl["body"]["value"] = []
    enable_tool_mode(
        sheets_tool,
        "append_triage_row_to_sheet",
        "Append one triaged Jira issue as a row in Google Sheets. Send all 37 columns in order.",
        {
            "url_input": {
                "default": SHEETS_APPEND_URL,
                "description": "Google Sheets values.append URL for the BugTRIAGE tab.",
                "title": "Sheets Append URL",
                "type": "string",
            },
            "body": {
                "default": "",
                "description": (
                    'JSON string of the request body, e.g. {"values": [["KAN-8", "VWO", ...]]} '
                    "with all 37 columns in the exact order given in the instructions."
                ),
                "title": "Body",
                "type": "string",
            },
        },
    )

    chat_output = build_core_node(registry, "input_output", "ChatOutput", "ChatOutput", (740, 20), True)

    nodes = [chat_input, jira_tool, sheets_tool, groq, agent, chat_output]

    edges = [
        make_edge(chat_input, "message", ["Message"], agent, "input_value", ["Message"], "str"),
        make_edge(groq, "model_output", ["LanguageModel"], agent, "model", ["LanguageModel"], "model"),
        make_edge(jira_tool, "component_as_tool", ["Tool"], agent, "tools", ["Tool"], "other"),
        make_edge(sheets_tool, "component_as_tool", ["Tool"], agent, "tools", ["Tool"], "other"),
        make_edge(agent, "response", ["Message"], chat_output, "input_value",
                  ["Data", "JSON", "DataFrame", "Table", "Message"], "other"),
    ]

    flow = {
        "data": {
            "edges": edges,
            "nodes": nodes,
            "viewport": {"x": 240, "y": 120, "zoom": 0.72},
        },
        "description": "Triages Jira bugs against a controlled vocabulary and writes each result to Google Sheets.",
        "endpoint_name": None,
        "id": str(__import__("uuid").uuid4()),
        "is_component": False,
        "last_tested_version": LF_VERSION,
        "locked": False,
        "name": "Bug Triage AI Agent",
        "tags": [],
    }

    serialized = json.dumps(flow, indent=2, ensure_ascii=False)

    # Guard: never write a credential-shaped string.
    leak = re.search(r"gsk_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|ATATT[A-Za-z0-9_\-]{20,}"
                     r"|xox[baprs]-|AIza[0-9A-Za-z_\-]{20,}", serialized)
    if leak:
        raise SystemExit(f"refusing to write: credential-shaped string found -> {leak.group(0)[:12]}...")

    OUT_FILE.write_text(serialized + "\n", encoding="utf-8")
    print(f"wrote {OUT_FILE} ({len(serialized)} chars, {len(nodes)} nodes, {len(edges)} edges)")


if __name__ == "__main__":
    main()
