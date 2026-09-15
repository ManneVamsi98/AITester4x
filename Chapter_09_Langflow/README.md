# Chapter 09 — Langflow

This chapter explores **Langflow** — a low-code, visual framework for building AI agents, RAG pipelines, and automation workflows by dragging components onto a canvas and connecting them.

## What's inside

| Path | Description |
|---|---|
| `README.md` | Local setup, how to run Langflow on localhost, and troubleshooting notes. |
| `Sample workflow.json` | A minimal Chat Input → Groq → Chat Output flow. |
| `Bug Triage AI Agent.json` | Agent flow that triages Jira bugs and writes each result to Google Sheets. |
| `build_bug_triage_flow.py` | Regenerates `Bug Triage AI Agent.json` from Langflow's own component registry. |

## Local setup (this machine)

Langflow **1.12.1** is installed in a dedicated virtual environment at `E:\lf` (Python 3.12). It is **not** installed in the global Python — see the notes below for why.

## Run Langflow on localhost

Start the server (first boot takes a minute or two while Langflow initializes):

```bash
E:\lf\Scripts\langflow.exe run --host 127.0.0.1 --port 7860
```

Then open the UI:

- **UI**: http://127.0.0.1:7860
- **Health check**: http://127.0.0.1:7860/health → returns `{"status":"ok"}` when ready

To stop it: press `Ctrl+C` in the terminal, or kill the `langflow.exe` / `python.exe` process tree.

## Notes & troubleshooting

- **Why a venv at `E:\lf`?** Installing into the global Python failed with `OSError: No such file or directory` while extracting the `langwatch` package. Its wheel contains files whose full paths exceed the Windows 260-character `MAX_PATH` limit (long-path support is disabled on this machine and enabling it requires admin rights). A venv at a short path (`E:\lf\Lib\site-packages\...`) keeps extracted paths under the limit.
- **pip upgrade required**: `pip 25.0.1` crashed during dependency resolution (`InvalidVersion: Invalid version: 'hosting'`). Upgrading to `pip 26.2.1` fixed it. Langflow itself requires `pip>=26.2.1`.
- **Updating Langflow**: `E:\lf\Scripts\python.exe -m pip install --upgrade langflow`
- **Restarting from scratch**: delete `E:\lf` and re-run `python -m venv E:\lf`, then `E:\lf\Scripts\python.exe -m pip install langflow`.
- Models are configured per-component inside the Langflow UI (e.g. OpenAI, Ollama) with credentials stored by Langflow itself.

## Bug Triage AI Agent

A Langflow port of the n8n `04_BugTriageAIAgent` workflow: the agent retrieves Jira bugs, triages
each one against a controlled vocabulary, and writes all 37 columns per issue into Google Sheets.

```
Chat Input ──► AI Agent ──► Chat Output
                 ▲   ▲   ▲
     Groq model ─┘   │   └─ Tool: API Request (Google Sheets append)
                     └───── Tool: API Request (Jira JQL search)
```

### Import

1. Langflow → **My Projects** → **Import** → choose `Bug Triage AI Agent.json`.
2. Open the flow; the canvas should show six nodes with the Groq model feeding the agent's
   *Language Model* handle and both API Request nodes feeding its *Tools* handle.

### Credentials are NOT in the file

Every secret field is deliberately blank. Langflow stores secrets inline on export, so a key in a
committed flow is a leaked key — `Sample workflow.json` had to have its Groq key stripped before it
could be committed.

| Where | What to set |
|---|---|
| Groq model node | **Groq API Key** — your `gsk_...` key |
| API Request (Jira) | Header `Authorization` — `Basic <base64(email:api_token)>` |
| API Request (Sheets) | Header `Authorization` — `Bearer <google oauth token>` |

Prefer setting these through Langflow's **Global Variables** so they are never written back into an
export. If you do edit them inline, clear them before exporting or committing.

### Two things to know

- **Jira + Sheets are generic API Request tools.** Langflow has no native Jira or Google Sheets
  component, so the agent builds the calls itself: it supplies the Jira search URL, and for the
  Sheets write it supplies a JSON `body` such as `{"values": [["KAN-8", "VWO", ...]]}` with all 37
  columns in the documented order. That is more LLM-side work than n8n's purpose-built tools, so
  expect more variability and some prompt tuning.
- **The Jira URL is a placeholder.** `url_input` defaults to
  `https://YOUR-SITE.atlassian.net/rest/api/2/search`; set it to your site.

### Regenerating

`build_bug_triage_flow.py` rebuilds the export from Langflow's own component registry, so it survives
a Langflow upgrade. It refuses to write a file containing a credential-shaped string.

```bash
E:\lf\Scripts\python.exe Chapter_09_Langflow\build_bug_triage_flow.py
```
