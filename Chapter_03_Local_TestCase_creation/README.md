# Chapter 03 — Local Test Case Creation

This chapter focuses on **creating test cases from Jira tickets locally**, using a small local LLM (Ollama) with a hosted fallback (Groq), driven by a reusable prompt template.

## What's inside

| Path | Description |
|---|---|
| `Template/Testcase_creator.md` | The reusable test-case generation prompt template (`[NUMBER]` and `[PASTE REQUIREMENTS HERE]` placeholders). |
| `Jira_TestCase_Generator/` | A complete Streamlit application that fetches a Jira ticket and generates a test-case markdown table. |
| `Jira_TestCase_Generator/plan.md` | The implementation plan for the app (file structure, module design, data flow). |

## Jira Test Case Generator

A two-screen Streamlit app:

- **Screen 1 — Chat**: type something like `create 12 test cases for QA-102`, and the app fetches the ticket from Jira, merges its summary/description/acceptance criteria into the template, and renders the generated test cases as a markdown table in the chat pane (with a download button).
- **Screen 2 — Settings**: persist Jira URL, Jira email, Jira API token, LLM provider (Groq by default, Ollama optional), Groq API key, and the default number of test cases.

### Architecture

```
Chat message → parse Jira key (+ optional count)
  → jira_client.get_ticket(key, cfg)      # Jira REST API v2, Basic Auth
  → requirements_text = summary + description + acceptance criteria
  → template (templates/testcase_creator.md) with placeholders filled
  → llm_client: Groq (primary) | Ollama (opt-in, gemma3:1b / llama3.2:1b)
  → markdown table rendered in chat pane + download button
```

### Files

| File | Purpose |
|---|---|
| `app.py` | Screen 1 — Chat interface (main entry point). |
| `pages/settings.py` | Screen 2 — Settings form. |
| `config_store.py` | Read/write settings from local `config.json` (gitignored); seeds from `.env` if present. |
| `jira_client.py` | Fetch ticket details via the Jira REST API v2 (ADF description parsing, acceptance-criteria extraction). |
| `llm_client.py` | LLM calls — Groq primary, Ollama opt-in with fallback; builds the prompt from the template. |
| `templates/testcase_creator.md` | The test-case generation template used to prompt the LLM. |
| `requirements.txt` | Dependencies: `streamlit`, `requests`. |

### Setup

1. Install Python 3.12+.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a local `.env` file (or fill in the Settings screen) with:

   ```env
   JIRA_EMAIL=your@email.com
   JIRA_API_TOKEN=your-jira-api-token
   JIRA_URL=https://your-site.atlassian.net
   GROQ_KEY=your-groq-api-key
   ```

4. Run the app:

   ```bash
   streamlit run app.py
   ```

   Then open http://localhost:8501.

### Usage

- Open the **Settings** screen (sidebar) and save your Jira URL, email, API token, and Groq key.
- Back in the **Chat** screen, type a request with a Jira ticket key, e.g. `create test cases for QA-102` or `create 15 test cases for KAN-42`.
- The generated test cases appear as a markdown table; use **Download test cases (.md)** to save them.

### Notes

- **Credentials are never hardcoded** — they live in `config.json` / `.env`, both gitignored.
- Default LLM provider is **Groq** (model `openai/gpt-oss-120b`). **Ollama** can be selected in Settings (models `gemma3:1b` or `llama3.2:1b`, forced to CPU to avoid out-of-memory crashes on this machine).
- The generated test-case format follows the template: `| Test ID | Description | Pre-conditions | Steps | Expected Result | Priority |` with `TC-001`, `TC-002`, ... IDs and High/Medium/Low priorities.
