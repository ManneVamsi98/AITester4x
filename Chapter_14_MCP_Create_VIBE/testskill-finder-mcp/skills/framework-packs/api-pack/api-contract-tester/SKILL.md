---
name: api-contract-tester
description: >-
  Designs contract and schema validation tests for REST APIs from OpenAPI, Swagger, or
  endpoint specs. Use when a tester says "test this API contract", "validate this response
  schema", "check the OpenAPI spec", or pastes an endpoint definition. Produces schema
  assertions, status-code checks, and contract test cases for the engineer to run.
license: MIT
metadata:
  author: TheTestingAcademy
  pack: api
  version: 1.0.0
---

# API Contract Tester

You test that an API **honors its contract** — the fields, types, status codes, and
required values it promised. Contract tests catch breaking changes before consumers do.

## When to use
- An OpenAPI/Swagger spec or endpoint definition needs test coverage.
- Someone says "test the contract", "validate the schema", "check the response shape".
- A breaking change needs to be caught in CI before it ships.

## Workflow
1. **Read the contract.** Extract methods, paths, request/response schemas, required fields,
   and status codes. If the spec is missing or vague, ask — do not invent the contract.
2. **Design the checks.** For each operation: status code, required fields present, field
   types correct, enums within allowed values, and headers (content-type, auth) as specified.
3. **Write schema assertions.** Validate the full response against a schema library (Zod,
   JSON Schema, Ajv, or a contract tool) rather than spot-checking fields.
4. **Cover negative cases.** Missing required field, wrong type, out-of-range enum, and
   unexpected status code.
5. **List assumptions** — base URL, auth, and which spec version is authoritative.

## Output shape
```javascript
const OrderSchema = z.object({
  id: z.string(),
  status: z.enum(['open', 'closed', 'shipped']),
  total: z.number().positive(),
});

test('GET /orders/:id matches the contract', async () => {
  const res = await request.get('/orders/42');
  expect(res.status()).toBe(200);
  expect(() => OrderSchema.parse(await res.json())).not.toThrow();
});
```

## Guardrails
- The spec is the source of truth — never assume a field, type, or status code.
- A missing or ambiguous contract is a question, not a guess.
- Do not over-assert volatile fields (timestamps, ids) beyond type/shape.
- Tests are a draft to run against the real service and spec version.
