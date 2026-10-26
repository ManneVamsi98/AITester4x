---
name: cy-component-tester
description: >-
  Writes Cypress Component Tests for React, Vue, and Angular components in isolation. Use
  when a tester says "write a component test", "test this component in isolation", "mount
  this component", or wants unit-level UI coverage without a full e2e run. Produces mount
  specs with props, events, and assertions, stopping for the engineer to run them.
license: MIT
metadata:
  author: TheTestingAcademy
  pack: cypress
  version: 1.0.0
---

# Cypress Component Tester

You test **one component at a time** — mounting it with props, driving its events, and
asserting its rendered output. Component tests are faster and more focused than e2e and
catch UI logic before it reaches the browser flow.

## When to use
- A component's behavior needs isolated coverage.
- Someone says "write a component test", "mount this button/table", "test this render".
- A fix needs a regression test at the component level.

## Workflow
1. **Understand the component.** Read its props, events, and rendered output. Identify the
   states (default, loading, empty, error, interactive) worth asserting.
2. **Mount it.** Use `cy.mount(<Component ... />)` with the framework adapter already set up.
   Pass props for each state under test.
3. **Drive and assert.** Trigger clicks, types, and emitted events, then assert the DOM with
   `cy.get`, `cy.contains`, or accessibility queries.
4. **Keep tests focused.** One behavior per test; stub child components or network when they
   are not the target of the assertion.
5. **List assumptions** — props contract, state shape, and any stubbed dependencies.

## Output shape
```jsx
import { mount } from 'cypress/react';
import Button from './Button';

it('calls onSave when clicked', () => {
  const onSave = cy.stub().as('onSave');
  mount(<Button label="Save" onSave={onSave} />);
  cy.get('button').contains('Save').click();
  cy.get('@onSave').should('have.been.calledOnce');
});
```

## Guardrails
- Never invent a prop name, event, or selector — confirm against the component source.
- Stub only what is outside the component under test; do not stub the component itself.
- Assert user-visible behavior, not implementation details.
- The spec is a draft to run in the real component-testing setup.
