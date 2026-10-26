---
name: cy-e2e-organizer
description: >-
  Organizes Cypress end-to-end test suites for readability, reuse, and fast CI. Use when a
  tester says "organize my Cypress specs", "structure these e2e tests", "set up custom
  commands", "reduce duplication across specs", or wants a maintainable cypress/ layout.
  Produces a spec/folder plan, custom commands, and shared setup patterns.
license: MIT
metadata:
  author: TheTestingAcademy
  pack: cypress
  version: 1.0.0
---

# Cypress E2E Organizer

You structure a Cypress project so specs are **discoverable, DRY, and fast in CI**. Good
organization is the difference between a suite people maintain and one they abandon.

## When to use
- A Cypress project has grown and needs structure.
- Someone says "organize the specs", "set up custom commands", "reduce duplication".
- A team wants shared setup, hooks, or selectors reused across specs.

## Workflow
1. **Survey the suite.** List the existing specs, commands, and fixtures. Find duplicated
   selectors, repeated setup, and inconsistent folder layout.
2. **Propose a layout.** Group specs by feature or user journey under `cypress/e2e/`, keep
   `support/commands.js` for cross-cutting helpers, and `fixtures/` for data.
3. **Extract custom commands.** Move repeated `cy.get('[data-cy=...]').click()` into named
   commands like `cy.login()` or `cy.addToCart()`, with a clear signature.
4. **Centralize selectors and config.** Recommend a selector map or `data-cy` convention, and
   shared `beforeEach`/`Cypress.Commands` for auth and navigation.
5. **HUMAN REVIEW GATE (mandatory).** Present the plan as a proposal; list anything you
   could not verify about the current suite before files are moved.

## Output shape
```
cypress/
  e2e/
    auth/login.cy.js
    checkout/checkout.cy.js
  support/
    commands.js     # cy.login(), cy.addToCart()
    e2e.js
  fixtures/         # users.json, orders.json
```

## Guardrails
- Never move or delete files without a human-approved plan; changes to a working suite are
  reversible and reviewable.
- Do not guess what a command does — read it before refactoring.
- Keep custom commands named by user intent, not by selector detail.
- Propose first, refactor after review.
