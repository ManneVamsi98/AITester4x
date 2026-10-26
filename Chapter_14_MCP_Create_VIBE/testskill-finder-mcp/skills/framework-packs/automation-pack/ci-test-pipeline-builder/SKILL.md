---
name: ci-test-pipeline-builder
description: >-
  Designs CI/CD test pipelines that run the right tests at the right stage and fail fast.
  Use when a tester says "set up the test pipeline", "add tests to CI", "parallelize the
  test runs", or wants a reliable, fast test stage. Produces a pipeline plan with stages,
  caching, parallelization, and flake handling.
license: MIT
metadata:
  author: TheTestingAcademy
  pack: automation
  version: 1.0.0
---

# CI Test Pipeline Builder

You design a **test pipeline that runs the right tests at the right time** and fails fast
without flaking. A good pipeline runs unit tests in seconds and keeps slow e2e tests from
blocking a merge.

## When to use
- Tests need to run in CI reliably and quickly.
- Someone says "set up the test pipeline", "add tests to CI", "parallelize the runs".
- A test stage is slow or flaky and needs restructuring.

## Workflow
1. **Layer the tests.** Map unit, integration, e2e, and performance tests to pipeline
   stages, so fast tests run first and expensive ones gate only releases.
2. **Add caching and parallelism.** Cache dependencies and build artifacts; split test
   jobs by module or shard, and parallelize independent suites.
3. **Set quality gates.** Define pass/fail thresholds, required coverage, and which stages
   block a merge versus run after.
4. **Handle flake and artifacts.** Add retries with a flake budget, and publish reports,
   traces, and screenshots so failures are debuggable.
5. **HUMAN REVIEW GATE (mandatory).** Confirm the stage gates, budgets, and runner resources
   with the team before wiring it into the repository.

## Output shape
```yaml
# pipeline plan
stages:
  - unit:         { trigger: push,  parallel: 4, gate: block-merge }
  - integration:  { trigger: push,  parallel: 2, gate: block-merge }
  - e2e:          { trigger: nightly/PR, parallel: 6, gate: warn }
  - performance:  { trigger: release, gate: block-release }
flake_budget: 2 retries per test
artifacts: [junit reports, playwright traces, screenshots]
```

## Guardrails
- Never guess runner resources or thresholds — confirm with the team.
- Keep fast tests in the blocking path and slow tests out of it.
- A retry budget hides flakes; a separate job should still surface them.
- The plan is a draft to review before it becomes repository config.
