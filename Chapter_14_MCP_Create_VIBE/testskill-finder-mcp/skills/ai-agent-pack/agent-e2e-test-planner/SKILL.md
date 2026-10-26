---
name: agent-e2e-test-planner
description: >-
  Plans end-to-end test automation executed by an AI agent, breaking a user journey into
  agent-executable steps with checkpoints and assertions. Use when a tester says "plan
  agent-driven e2e tests", "design tests for an AI browser agent", "script a user journey
  for an agent", or wants steps an autonomous agent can follow. Produces a step plan with
  expected states at each checkpoint.
license: MIT
metadata:
  author: TheTestingAcademy
  area: ai-agents
  version: 1.0.0
---

# Agent E2E Test Planner

You write test plans an **AI agent can execute**, not just a human. Agent steps must be
unambiguous, self-contained, and carry an expected state at every checkpoint so the agent
can detect drift and recover.

## When to use
- Tests will be executed by an AI browser or test agent.
- Someone says "plan agent e2e tests", "write steps for the agent", "script a journey".
- A flaky journey needs explicit checkpoints so an agent can self-verify.

## Workflow
1. **Decompose the journey.** Break the user flow into atomic actions (navigate, click,
   type, wait) with no implied context. Each step must stand alone.
2. **Add checkpoints.** After each meaningful action, state the expected observable state
   (a heading, a count, a URL) the agent can assert before continuing.
3. **Specify data and locators.** Name the exact test data and a stable selector or
   user-visible text for each target; never "click the button".
4. **Define recovery.** For each step, note what the agent should do if the expected state
   is not met (retry, screenshot, abort) so failures are diagnosable.
5. **HUMAN REVIEW GATE (mandatory).** Review that every step is executable and every
   checkpoint observable; hand off for the agent to run.

## Output shape
```yaml
# agent e2e plan — checkout
steps:
  - action: navigate to /cart
    checkpoint: cart shows 1 item titled "Test Widget"
    on_failure: screenshot and abort
  - action: click [data-cy=checkout]
    checkpoint: payment section is visible
  - action: click [data-cy=place-order]
    checkpoint: "Order confirmed" heading is visible
```

## Guardrails
- Never write an ambiguous step — an agent cannot infer what a human would.
- Every checkpoint must be objectively observable, not "the page looks right".
- Name exact data and selectors; do not leave targets to the agent's guess.
- The plan is a draft to validate by running the agent against the real app.
