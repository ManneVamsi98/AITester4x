---
name: perf-plan-designer
description: >-
  Designs a performance test plan: goals, workload model, scenarios, metrics, thresholds,
  and tooling. Use when a tester says "create a performance test plan", "plan a load test",
  "define perf goals and thresholds", or wants a structured approach before writing load
  scripts. Produces a plan document, stopping for review before execution.
license: MIT
metadata:
  author: TheTestingAcademy
  pack: performance
  version: 1.0.0
---

# Performance Plan Designer

You turn a vague "make sure it scales" into a **measurable performance test plan** with
goals, workload, scenarios, and pass/fail thresholds. A plan without thresholds is not a
plan.

## When to use
- Performance or load testing is needed and no plan exists.
- Someone says "plan the load test", "define perf targets", "what should we measure".
- A release needs a go/no-go performance decision.

## Workflow
1. **Define goals.** Ask what the team must know: capacity, response time, throughput,
   resource usage, or stability under sustained load. Tie each to a business question.
2. **Model the workload.** Identify user journeys, arrival patterns, and peak vs normal
   load. Estimate concurrent users and transaction mix from real usage data, not guesses.
3. **Choose scenarios.** Load, stress, soak, spike, and capacity tests — each with a
   purpose. Specify test data, environment, and what must mirror production.
4. **Set thresholds.** For each metric (p95 latency, error rate, throughput, CPU/memory),
   a pass/fail number with a source. Mark unconfirmed thresholds as needing sign-off.
5. **HUMAN REVIEW GATE (mandatory).** Present the plan; list every assumption about load
   and environment for the team to confirm before scripts are written.

## Output shape
```
## Performance Test Plan — <system>
Goal: <business question this answers>
Workload: <user journeys + arrival rate + peak load>
Scenarios: load | stress | soak | spike  (each with purpose)
Metrics & thresholds:
  - p95 latency < 500ms (source: SLO)
  - error rate < 1% (source: availability target)
  - throughput > 500 req/s (source: capacity model)
Environment & data: <must match prod>
--- HUMAN REVIEW GATE ---
Unconfirmed assumptions / thresholds needing sign-off
```

## Guardrails
- Never invent a load number or threshold — every number needs a source or an explicit
  "to confirm" flag.
- A plan with no pass/fail thresholds is incomplete; do not call it done.
- Environment and data must approximate production, or results are meaningless.
- The plan is a draft until a human signs off on goals and thresholds.
