# Chapter 09 — Langflow

This chapter explores **Langflow** — a low-code, visual framework for building AI agents, RAG pipelines, and automation workflows by dragging components onto a canvas and connecting them.

## What's inside

| Path | Description |
|---|---|
| `README.md` | Local setup, how to run Langflow on localhost, and troubleshooting notes. |

> Workflow exports and project files will be added here as flows are built (similar to the n8n chapter).

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
