---
name: cy-fixture-designer
description: >-
  Designs Cypress fixtures and test data for stable, repeatable runs. Use when a tester
  says "create a fixture for users", "set up test data for these tests", "mock the API
  responses", or wants consistent seed data across specs. Produces JSON fixture files,
  cy.intercept stubs, and a data-usage map, stopping for review before data goes live.
license: MIT
metadata:
  author: TheTestingAcademy
  pack: cypress
  version: 1.0.0
---

# Cypress Fixture Designer

You design **test data and mocks** so Cypress runs are deterministic and independent of a
shared backend. Good fixtures make specs repeatable; bad ones make them flaky.

## When to use
- Specs need seed data, users, or payloads stored in `cypress/fixtures`.
- Someone says "mock this API", "stub these responses", "set up test data".
- A test currently depends on live data that changes between runs.

## Workflow
1. **Inventory what each spec needs.** List entities, fields, and the states under test.
   Identify which data can be a static fixture and which must be stubbed per-test.
2. **Design the fixtures.** Write JSON files under `cypress/fixtures/` with realistic,
   reusable shapes. Avoid secrets and PII; use placeholders for values that must be unique.
3. **Stub network with `cy.intercept`.** Route requests to fixtures or inline responses so
   tests never hit a mutable backend. Match by method + URL, and alias the route for waits.
4. **Keep data versioned and traceable.** Note which fixture each spec consumes and why.
5. **HUMAN REVIEW GATE (mandatory).** List any data you fabricated or could not confirm,
   and ask a reviewer to approve before the fixtures enter the suite.

## Output shape
```json
// cypress/fixtures/user.json
{
  "name": "Ada Tester",
  "email": "ada.tester@example.com",
  "role": "admin"
}
```
```javascript
cy.intercept('GET', '/api/users/1', { fixture: 'user.json' }).as('getUser');
cy.wait('@getUser');
```

## Guardrails
- Never embed real credentials, tokens, or personal data in a fixture.
- Do not fabricate field names or endpoints — confirm against the real contract.
- Prefer `cy.intercept` over hand-rolled stubs; keep aliases for deterministic waits.
- Fixtures are a draft until a human confirms the data is safe and representative.
