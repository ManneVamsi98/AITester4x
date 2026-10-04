# 04 — JIRA tickets

**Put here (optional):** exported JIRA tickets as `.json` (a list of issues, or a JQL search
response), if you prefer offline ingestion over the live connection.

**Ingested by:** `qabuddy.ingest.jira`. Preferred path is the **live JIRA MCP connection + JQL**
(configure in `.env` / `config.py`); a REST fallback is built in. One document per ticket.
