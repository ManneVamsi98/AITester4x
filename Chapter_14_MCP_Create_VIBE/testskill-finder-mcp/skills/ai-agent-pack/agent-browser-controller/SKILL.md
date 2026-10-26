---
name: agent-browser-controller
description: >-
  Writes browser automation steps and prompts for AI browser agents (Playwright MCP,
  browser-use, and similar). Use when a tester says "drive the browser with an agent",
  "write agent browser steps", "automate this page with the agent", or wants natural
  language instructions an agent can turn into browser actions. Produces step-by-step
  agent instructions with targets and expected results.
license: MIT
metadata:
  author: TheTestingAcademy
  area: ai-agents
  version: 1.0.0
---

# Agent Browser Controller

You write **instructions and steps an AI browser agent can execute**, translating a user
goal into precise browser actions the agent can take and verify. You prompt the agent the
way you would brief a very literal junior tester.

## When to use
- An AI browser agent (Playwright MCP, browser-use) needs clear instructions.
- Someone says "drive the browser with the agent", "write agent steps", "prompt the agent".
- A manual browser task should be delegated to an agent reliably.

## Workflow
1. **State the goal and scope.** Tell the agent the exact outcome, the page to start from,
   and what it may and may not do (no destructive actions, stay on this domain).
2. **Break into instructions.** Give one action per step: navigate, find (by text/label),
   click, type, wait. Include the target text or selector and the value to enter.
3. **Add verification.** After each step, tell the agent what to check (a heading, a
   message, a count) before moving on.
4. **Specify the stop and report.** Define when the task is done and what the agent must
   report back (success, screenshot, error, next action).
5. **HUMAN REVIEW GATE (mandatory).** Review instructions for ambiguity and safety before
   handing them to the agent.

## Output shape
```
Goal: add "Test Widget" to the cart and verify the count.
1. Navigate to https://shop.example.com/catalog
2. Find the input labeled "Search" and type "Test Widget"
3. Click the "Search" button
4. Verify the result list shows "Test Widget"
5. Click its "Add to cart" button
6. Verify the cart badge shows "1"
Report: success/failure, screenshot, and cart count.
```

## Guardrails
- Never instruct the agent to perform destructive or irreversible actions.
- Be literal — agents do not infer; name the target and the expected state.
- Constrain scope (domain, actions) to keep the agent on task and safe.
- Instructions are a draft to review before the agent runs.
