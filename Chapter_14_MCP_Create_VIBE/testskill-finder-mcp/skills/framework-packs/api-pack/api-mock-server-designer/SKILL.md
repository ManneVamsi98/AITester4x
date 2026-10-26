---
name: api-mock-server-designer
description: >-
  Designs mock API servers and stubs so tests run without a real backend. Use when a tester
  says "mock this API", "set up a mock server", "stub these endpoints", or wants parallel
  frontend/backend testing. Produces a mock server plan, endpoint stubs, and fixtures for
  the engineer to run locally or in CI.
license: MIT
metadata:
  author: TheTestingAcademy
  pack: api
  version: 1.0.0
---

# API Mock Server Designer

You design a **mock API** that returns realistic, controllable responses so frontend and
test work can proceed before — or without — the real backend.

## When to use
- A backend is not ready or is too slow/flaky for tests.
- Someone says "mock the API", "stand up a stub server", "decouple frontend tests".
- Tests need deterministic control over responses.

## Workflow
1. **Inventory the endpoints.** List methods, paths, request/response shapes, and the
   states each caller depends on. Read the contract or observe the real API — do not guess.
2. **Choose the tool.** Pick based on the stack: WireMock, MSW, json-server, Prism, or a
   bespoke FastAPI/Express stub.
3. **Design the stubs.** One stub per endpoint and state (success, empty, error, slow), with
   realistic fixtures that match the real response shape.
4. **Plan state and latency.** Support success/error/slow modes and request matching so
   tests can exercise loading and failure states deterministically.
5. **HUMAN REVIEW GATE (mandatory).** List anything you assumed about the real contract,
   and ask a reviewer to confirm the stubs match what the backend will actually return.

## Output shape
```yaml
# mock server plan
endpoints:
  - path: /api/orders
    method: GET
    states:
      success: { fixture: orders.json, status: 200 }
      empty:   { fixture: empty.json, status: 200 }
      error:   { fixture: error.json, status: 500 }
```

## Guardrails
- Stubs must match the real contract, not an imagined one — confirm shapes before coding.
- Never hardcode secrets or real personal data into fixtures.
- Support controllable error and latency modes, not just happy path.
- The mock is a stand-in; a final run against the real service is still required.
