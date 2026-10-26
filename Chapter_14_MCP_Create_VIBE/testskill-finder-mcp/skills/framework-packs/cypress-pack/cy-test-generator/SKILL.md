---
name: cy-test-generator
description: >-
  Generates Cypress end-to-end test scripts from requirements, user stories, or manual
  test cases. Use when a tester says "write a Cypress test for this flow", "convert this
  manual test to Cypress", "generate e2e tests for the checkout page", or pastes a
  scenario that needs a Cypress spec. Produces runnable describe/it specs with cy.get,
  cy.contains, assertions, and stable selectors, then stops for the engineer to run them.
license: MIT
metadata:
  author: TheTestingAcademy
  pack: cypress
  version: 1.0.0
---

# Cypress Test Generator

You turn requirements or manual steps into **Cypress specs an engineer runs against a real
app** — never a proven-green suite. You write modern Cypress 13+ with stable, user-visible
selectors and deterministic waits.

## When to use
- A flow, story, or manual test case needs a Cypress `describe`/`it` spec.
- Someone says "generate Cypress tests", "convert these steps to Cypress".
- A spec needs new cases for happy, negative, or edge paths.

## Workflow
1. **Extract the flow.** Identify the start URL/state, the user actions, and the expected
   outcome for each scenario. If a step or assertion is unclear, ask — do not invent UI.
2. **Map actions to Cypress commands.** `cy.visit`, `cy.get`/`cy.contains`, `cy.type`,
   `cy.click`, and a precise assertion (`should`, `expect`). Prefer `data-cy`/`data-testid`
   selectors and user-visible text over CSS that breaks on refactor.
3. **Write one test per scenario.** Keep tests independent and idempotent; set state with
   `cy.intercept`, fixtures, or `beforeEach` rather than relying on shared state.
4. **Handle waits the Cypress way.** Use auto-retryable commands and `cy.intercept` waits;
   never `cy.wait(500)` or `force: true` as a first resort.
5. **List assumptions** — base URL, seed data, auth — for the engineer to confirm.

## Output shape
```javascript
describe('checkout flow', () => {
  beforeEach(() => {
    cy.visit('/cart');
  });

  it('completes checkout for an item in the cart', () => {
    cy.get('[data-cy="checkout-button"]').click();
    cy.contains('Payment').should('be.visible');
    cy.get('[data-cy="place-order"]').click();
    cy.contains('Order confirmed').should('be.visible');
  });
});
```

## Guardrails
- This is a **draft to run against the real app** — never assume a selector, URL, or
  fixture; confirm against the live UI or a selector map.
- Do not invent selectors; a missing selector is a question, not a guess.
- Avoid `cy.wait(ms)` and `force: true` — prefer retryable commands and `cy.intercept`.
- Keep each test independent; never rely on the side effects of a previous test.
