# Plan: Jira Test Case Generator (Streamlit two-screen app)

Build the app specified by `Finetune_Prompt.md` (RICE-POT spec). Two screens: **Chat** (Screen 1) and **Settings** (Screen 2). Primary LLM is local **Ollama `gemma3:1b`** at `http://localhost:11434`; fallback to **Groq** when Ollama is down or the user selects Groq. Plan first, then build one module at a time.

## Requirements confirmed with user
- **Config store**: local JSON file (`config.json`), gitignored. No SQLite, no reusing `.env`.
- **Test case count**: default **10** when the message doesn't specify a number; message override supported (e.g. "create 15 test cases for QA-102").
- **Output**: render markdown table in chat pane **plus** a download button for the `.md` file.

## File structure to create (all under `Jira_TestCase_Generator/`)

```
Jira_TestCase_Generator/
├── app.py                # Screen 1 — Chat (main entry, `streamlit run app.py`)
├── pages/
│   └── settings.py       # Screen 2 — Settings form (Streamlit multipage)
├── config_store.py       # Read/write settings as JSON (gitignored config.json)
├── jira_client.py        # Fetch ticket via Jira REST API v2
├── llm_client.py         # Ollama primary + Groq fallback
├── templates/
│   └── testcase_creator.md   # Copy of Template/Testcase_creator.md (the [NUMBER] placeholder gets filled)
├── requirements.txt      # streamlit, requests
└── .gitignore            # config.json, .env, __pycache__/
```

## Existing files to reuse / be aware of
- `Chapter_03_Local_TestCase_creation/Template/Testcase_creator.md` — the template with `[NUMBER]` and `[PASTE REQUIREMENTS HERE]` placeholders. Copy it into `templates/testcase_creator.md` (the spec requires a local `/templates` folder).
- `Chapter_03_Local_TestCase_creation/Jira_TestCase_Generator/.env` — already contains the real Jira email/token/URL and Groq key. **Do not hardcode these into code.** The `.env` file is untracked and the whole `Chapter_03_Local_TestCase_creation/` folder is currently untracked, so nothing sensitive is committed. The app will read its settings from `config.json` (created via the Settings screen) — the `.env` stays as the user's manual reference and gets gitignored too.
- `Finetune_Prompt.md` (the spec itself) defines the flow in `[Mandatory] End-to-end flow`.

## Module design

### 1. `config_store.py`
- `CONFIG_PATH = Path(__file__).parent / "config.json"` — sibling of the app, gitignored.
- Functions:
  - `load_config() -> dict` — returns dict with keys `jira_url`, `jira_email`, `jira_token`, `provider` (`"ollama"`/`"groq"`), `groq_key`, `default_tc_count` (int, default 10). Missing file → all empty/None defaults. Never raises.
  - `save_config(cfg: dict) -> None` — writes pretty JSON with `json.dump(..., indent=2)`, creating parent dir if needed. Never raises (best-effort; surface errors in the UI via return bool/exception message).
  - `is_configured(cfg) -> bool` — True if jira_url/email/token present.

### 2. `jira_client.py`
- Plain functions; take config dict. Use `requests` + Jira **Basic Auth** (email + API token) against **REST API v2**:
  - Normalize URL: cut at first `/` after host to get the base URL.
  - `get_ticket(key: str, cfg: dict) -> dict` — raises a clear exception on 401/404/network; returns `{key, summary, description, acceptance_criteria, status, ...}`.
  - Parse acceptance criteria from the description if no dedicated field (look for `Acceptance Criteria` section in the description text; Jira descriptions can be ADF JSON — parse ADF to plain text).
  - Timeout (e.g. 15s) so a bad URL doesn't hang the chat.

### 3. `llm_client.py`
- `generate_test_cases(requirements_text: str, count: int, cfg: dict) -> str` — builds the prompt by reading `templates/testcase_creator.md` and replacing `[NUMBER]` with the count and `[PASTE REQUIREMENTS HERE]` with the ticket content.
- **Ollama path** (`provider == "ollama"` or default): POST to `http://localhost:11434/api/generate` with `{"model": "gemma3:1b", "prompt": prompt, "stream": false}`. Short timeout (e.g. 10s) so a down Ollama fails fast. On any exception/timeout → **fallback to Groq** automatically.
- **Groq path** (explicitly selected, or Ollama failed): POST to `https://api.groq.com/openai/v1/chat/completions` with `model: "llama-3.3-70b-versatile"` (or a sensible Groq default) and `Authorization: Bearer <groq_key>`.
- Return the raw LLM markdown table text. If both fail, return a clear error message to render in chat.

### 4. `app.py` (Screen 1 — Chat)
- `streamlit.set_page_config` + a simple chat history list (persisted in `st.session_state.messages`).
- Input box + **Send** button. On send:
  1. Parse Jira key with regex `([A-Z][A-Z0-9]+-\d+)` (e.g. `QA-102`, `KAN-123`).
  2. Optionally parse a count: `(\d+)\s+test cases?` (default `cfg["default_tc_count"]`, i.e. 10).
  3. Fetch ticket via `jira_client.get_ticket` → build requirements text (summary + description + acceptance criteria).
  4. Call `llm_client.generate_test_cases` → render returned markdown with `st.markdown` (or `st.code` fallback if it isn't a table).
  5. Show a `st.download_button` for the generated `.md` file.
- If no Jira key found in the message → friendly inline error, no LLM call.

### 5. `pages/settings.py` (Screen 2 — Settings)
- Streamlit form with fields: Jira base URL, Jira email, Jira API token (password), provider radio (Ollama / Groq), Groq API key (password), default test case count (number input).
- Pre-fill from `config_store.load_config()`. On **Save**, `save_config()`; show success/error toast.
- Note that provider "Groq" = explicit opt-out of Ollama; "Ollama" = try Ollama, fall back to Groq on failure (spec `[Mandatory]` fallback).

### 6. `requirements.txt`
```
streamlit>=1.30
requests>=2.31
```
(Minimal, per spec tone. No `python-dotenv` needed since we read `config.json`, not `.env`.)

### 7. `.gitignore` (inside the generator folder)
```
config.json
.env
__pycache__/
```
**Note**: the repo-root `.gitignore` currently does NOT cover `config.json` or `.env` — this file is required to keep credentials out of version control.

## Data flow
```
Chat message → parse Jira key (+ optional count)
  → jira_client.get_ticket(key, cfg)  [Jira REST API v2, Basic Auth]
  → requirements_text = summary + description + acceptance criteria
  → template (templates/testcase_creator.md): [NUMBER]=count, [PASTE REQUIREMENTS HERE]=requirements_text
  → llm_client: Ollama localhost:11434 gemma3:1b  → (down/error) → Groq fallback
  → markdown table rendered in chat pane + download button
```
Settings screen writes `config.json` via `config_store.py`; every module reads the same config.

## Build order (one module at a time, per spec)
1. `config_store.py` (foundation)
2. `jira_client.py`
3. `llm_client.py`
4. `templates/testcase_creator.md` (copy)
5. `app.py`
6. `pages/settings.py`
7. `requirements.txt` + `.gitignore`

## Verification
- `pip install -r requirements.txt` (streamlit, requests).
- `python -c "import config_store; print(config_store.load_config())"` — returns defaults, no crash.
- `streamlit run app.py` → Screen 1 loads; type "create test cases for KAN-1" with Ollama running → table renders + download button works; with Ollama stopped → Groq fallback fires (if Groq key set).
- Screen 2 → fill settings, Save → `config.json` created and gitignored (`git check-ignore config.json` passes); verify `.env` and `config.json` are NOT tracked (`git status` clean of them).
- No credentials appear anywhere in source code (grep for token patterns in committed files).
