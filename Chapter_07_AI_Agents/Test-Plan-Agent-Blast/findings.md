# Findings — Test Plan Creator from a Jira ID

> B.L.A.S.T. Phase 1 (Blueprint) — research findings on how to fetch Jira data and turn it into a test plan.

---

## 1. The Sample Template (source of truth for output)

`Test Plan - Template.docx.pdf` (by TheTestingAcademy) defines these sections — our generator must produce them:

1. **Objective**
2. **Scope** (inclusions: functional, data validation, error handling, performance, security, integration, compatibility, documentation, load, regression, edge case, concurrency, ad hoc, usability, CI/CD, performance monitoring, backup/recovery, i18n, rate limiting, third-party)
3. **Inclusions** (CRUD operations: POST/GET/PUT/DELETE, boundary, concurrency, data validation, auth & authorization, error handling, security, performance, integration, regression, documentation, load, compatibility, usability, CI/CD, rate limiting, backup/recovery)
4. **Test Environments** (OS, browsers, devices, API endpoint, test data)
5. **Defect Reporting Procedure**
6. **Test Strategy**
7. **Test Schedule**
8. **Test Deliverables**
9. **Entry and Exit Criteria**
10. **Test Execution** (entry/exit criteria)
11. **Test Closure** (entry/exit criteria)
12. **Tools**
13. **Risks and Mitigations**
14. **Approvals**

## 2. Jira REST API — how to fetch a ticket

### Endpoint (Cloud)
```
GET {JIRA_BASE_URL}/rest/api/3/issue/{issueIdOrKey}
```
Example:
```
GET https://your-domain.atlassian.net/rest/api/3/issue/PROJ-123
```

### Authentication (Cloud, API token)
Jira Cloud accepts **Basic auth** with `email:API_TOKEN`:

```bash
curl -u "you@example.com:YOUR_API_TOKEN" \
  "https://your-domain.atlassian.net/rest/api/3/issue/PROJ-123" \
  -H "Accept: application/json"
```

Or explicit header:
```bash
# base64("you@example.com:YOUR_API_TOKEN")
curl "https://your-domain.atlassian.net/rest/api/3/issue/PROJ-123" \
  -H "Authorization: Basic $(echo -n 'you@example.com:YOUR_API_TOKEN' | base64)" \
  -H "Accept: application/json"
```

### Authentication (Cloud, Personal Access Token — newer)
```bash
curl "https://your-domain.atlassian.net/rest/api/3/issue/PROJ-123" \
  -H "Authorization: Bearer YOUR_PAT" \
  -H "Accept: application/json"
```

### Authentication (Server / Data Center)
```bash
curl -u "username:PASSWORD_OR_PAT" \
  "https://jira.yourcompany.com/rest/api/2/issue/PROJ-123" \
  -H "Accept: application/json"
```
> Note: Server uses `/rest/api/2/`; Cloud uses `/rest/api/3/`.

### Search with JQL (if we need richer field control)
```bash
curl -u "you@example.com:YOUR_API_TOKEN" \
  -X POST "https://your-domain.atlassian.net/rest/api/3/search/jql" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"jql": "key = PROJ-123", "fields": ["summary", "description", "labels", "components", "status", "issuetype"]}'
```

## 3. What the API returns (relevant fields)

```json
{
  "key": "PROJ-123",
  "fields": {
    "summary": "Add booking cancellation flow",
    "description": "As a user I want to cancel a booking...",
    "acceptanceCriteria": "Given a valid booking id, When I cancel, Then status becomes cancelled",
    "status": { "name": "In Progress" },
    "labels": ["api", "p1"],
    "components": [{ "name": "Booking Service" }],
    "issuetype": { "name": "Story" },
    "assignee": { "displayName": "Vamsi" },
    "priority": { "name": "High" }
  }
}
```
> `acceptanceCriteria` is a custom field — its id varies per Jira instance (commonly `customfield_10020` or similar). The generator must **look it up by field name** and not hardcode one id.

## 4. Mapping: Jira fields → Test Plan sections

| Jira field | Test Plan section |
|---|---|
| `key` | Title / reference |
| `summary` | Objective (headline) |
| `description` | Scope + Inclusions |
| `acceptanceCriteria` | Test cases outline (given/when/then) |
| `labels`, `components` | Risk areas, Environments |
| `issuetype` | Test Strategy hint (Story → feature; Bug → regression) |
| `status`, `assignee`, `priority` | Schedule, Approvals |
| `created`, `updated` | Schedule, Closure |

## 5. Constraints & gotchas

- **Rate limits:** Jira Cloud ~ 10 req/s per user (varies); keep the tool to 1–2 calls per run.
- **Scopes (PAT):** needs `read:jira-work`.
- **Custom fields:** `acceptanceCriteria` is not in the default response — resolve it via `/rest/api/3/field` or use a JQL search with explicit fields.
- **Secrets:** never commit tokens; read from `.env` (`JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`).
- **Empty fields:** any missing field → emit "TBD" in the plan rather than inventing content (deterministic rule).
- **PDF text extraction worked via `pypdf`** (the sample's text is available) — the generator's render step can use the same approach to produce a matching layout if needed.

## 6. Suggested `.env` (never committed)

```
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=you@example.com
JIRA_API_TOKEN=your-api-token
```
