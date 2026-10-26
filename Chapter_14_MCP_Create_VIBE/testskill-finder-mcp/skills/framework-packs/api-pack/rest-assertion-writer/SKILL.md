---
name: rest-assertion-writer
description: >-
  Writes precise REST API assertions for status, headers, body, and JSON paths. Use when a
  tester says "add assertions to this API test", "assert the response body", "check the
  headers", or wants readable, targeted API assertions. Produces assertion code with exact
  expected values and clear failure messages, to run against a real service.
license: MIT
metadata:
  author: TheTestingAcademy
  pack: api
  version: 1.0.0
---

# REST Assertion Writer

You write **assertions that fail with a clear message** and assert exactly the contract,
not more and not less. Good API assertions pinpoint the broken field in one line.

## When to use
- API tests need status, header, and body assertions.
- Someone says "assert the response", "check the JSON body", "make the failure readable".
- A test is flaky because it over-asserts volatile fields.

## Workflow
1. **Identify what must hold.** For each response: status code, key headers
   (content-type, cache, auth), and the body fields that matter.
2. **Assert precisely.** Assert status first (it gates the body), then headers, then body
   fields and JSON paths. Use a matcher that prints actual vs expected clearly.
3. **Avoid over-assertion.** Assert type/shape for volatile values (ids, timestamps);
   assert exact values only for stable business fields.
4. **Name the intent.** Group assertions with a message that says what is being verified,
   so a red line is self-explanatory.
5. **List assumptions** — base URL, auth, and any values the engineer must confirm.

## Output shape
```python
def test_get_order_returns_open_order():
    res = client.get("/orders/42", headers=auth)
    assert res.status_code == 200, f"expected 200, got {res.status_code}"
    assert res.headers["content-type"].startswith("application/json")
    body = res.json()
    assert body["status"] == "open"
    assert body["total"] > 0
    assert isinstance(body["id"], str)
```

## Guardrails
- Never assert an exact value for a generated id or timestamp — assert type/shape.
- Confirm expected values against the real contract, not memory.
- Keep the assertion message specific so a failure names the field, not just "failed".
- Tests are a draft to run against the live service.
