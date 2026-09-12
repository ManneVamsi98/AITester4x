# Requirement to Test Cases — Streamlit UI

A UI for the `09_RequirementToTestCase` n8n workflow.

Enter a Jira issue key (a user story or PRD ticket) and the app:

1. POSTs the key to the workflow's webhook.
2. The workflow fetches the story, drafts positive and negative BDD/Gherkin scenarios, and appends one Google Sheets row per scenario.
3. The app renders the scenarios as a BDD feature — summary counts, a table, one card per scenario — with JSON and `.feature` downloads.

## How it fits together

```
Streamlit UI  --POST {issueKey}-->  Webhook - New Requirement
                                      -> IF - Issue Key Present
                                      -> Jira - Get User Story
                                      -> Code - Normalize Jira Story
                                      -> AI Agent - Requirement to Gherkin
                                      -> Split Out - Scenarios
                                      -> Google Sheets - Append Test Cases
                                   <-- those rows returned as JSON
```

The webhook's **Response Mode** is set to `lastNode`, so n8n replies with the rows the Google Sheets node just wrote. Those rows already contain every drafted field (`scenario_id`, `scenario_title`, `scenario_type`, `priority`, `gherkin`, `preconditions`, `test_data`, `expected_result`, `requirement_ref`, `automation_candidate`, `review_status`), so no extra response node is needed.

If your import still has `onReceived`, the workflow will answer immediately with the request echo and the UI will show nothing. Switch the Webhook node's **Respond** setting to *When Last Node Finishes*.

## Prerequisites

- `09_RequirementToTestCase.json` imported, with the Jira, Groq, and Google Sheets credentials attached.
- A header row in row 1 of the destination sheet tab, or you will hit *"No columns found in Google Sheets"*.

## Run it

```bash
cd "Chapter_08_n8n/UI_RequirementToTestCase"
python -m pip install -r requirements.txt
streamlit run app.py
```

Streamlit prints a local URL (usually <http://localhost:8501>). Open it.

To keep it off the network, bind to loopback:

```bash
streamlit run app.py --server.address 127.0.0.1
```

## Configure

Use the sidebar, or set these environment variables:

| Variable | Default | Meaning |
|---|---|---|
| `N8N_BASE_URL` | `https://boxubum.app.n8n.cloud` | Your n8n instance |
| `N8N_WEBHOOK_PATH` | `requirement-to-testcases` | The Webhook node's **Path** field |
| `N8N_TIMEOUT` | `180` | Seconds to wait for the agent |
| `N8N_AUTH_HEADER_NAME` | *(empty)* | Only if the Webhook node has auth enabled |
| `N8N_AUTH_HEADER_VALUE` | *(empty)* | Value for the above |

### Production vs Test mode

| Mode | URL | When it works |
|---|---|---|
| Production | `{base}/webhook/{path}` | Whenever the workflow is **Active** |
| Test | `{base}/webhook-test/{path}` | Only while the editor is listening — open the workflow and click *Listen for test event* |

The test URL handles a single call and then stops listening. Use Production for anything repeatable.

## Troubleshooting

**404 — webhook not registered.** Production needs the workflow Active; Test needs the editor listening. This is the most common failure.

**"n8n returned no scenario rows."** The workflow ran but produced nothing — usually the agent failed schema validation, or the Jira key doesn't exist. Check the execution in n8n.

**Timed out.** The Jira lookup plus the model call can exceed the default. Raise it in the sidebar; the n8n execution continues regardless and the sheet may still get written.

**"No columns found in Google Sheets"** in n8n. The destination tab has no header row. Add one (the workflow expects the 15 column names it maps).
