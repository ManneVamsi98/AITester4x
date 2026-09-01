# SOP-01 — Fetch ticket from Jira

**Goal:** Retrieve one Jira issue by key from the REST API.

**Inputs:** `issue_key` (e.g. `VWO-49`), config with `jira_url`, `jira_email`, `jira_token`.

**Logic:**
1. Normalize `jira_url` to the site base (strip deep links).
2. `GET {base}/rest/api/3/issue/{key}` with HTTP Basic auth.
3. Map errors: 401 → auth failure, 404 → not found, 5xx → platform.

**Edge cases:**
- Missing credentials → fail with "not configured".
- Timeout → fail loudly; never return a partial ticket.
- Ticket has no description → `description` is empty string (not None).

**Owner:** `jira_client.fetch_ticket`
