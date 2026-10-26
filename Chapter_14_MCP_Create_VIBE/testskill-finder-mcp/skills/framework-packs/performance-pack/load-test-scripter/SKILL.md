---
name: load-test-scripter
description: >-
  Writes load test scripts that simulate realistic user traffic and measure latency,
  throughput, and errors. Use when a tester says "write a load test", "script this load
  scenario", "simulate concurrent users", or has an approved perf plan to implement.
  Produces runnable load scripts with configurable ramp-up, assertions, and thresholds.
license: MIT
metadata:
  author: TheTestingAcademy
  pack: performance
  version: 1.0.0
---

# Load Test Scripter

You implement an **approved performance plan** as a load script that generates realistic
traffic and fails loudly when thresholds are breached. You script the workload, not a
synthetic hammer.

## When to use
- A perf plan exists and needs load scripts written.
- Someone says "write the load test", "script this scenario", "implement the perf plan".
- A threshold needs an automated check in CI.

## Workflow
1. **Read the plan.** Extract the scenarios, workload model, and thresholds. If a plan does
   not exist, stop and ask for one — do not improvise load.
2. **Choose the tool.** k6, JMeter, Locust, or Gatling, matching the team's stack and the
   plan's requirements.
3. **Model users.** Script the user journeys with realistic think times, data, and
   arrival/ramp patterns. Add tags so results can be sliced by endpoint and scenario.
4. **Encode thresholds.** Add pass/fail assertions for p95 latency, error rate, and
   throughput so a run is green or red, not just a report.
5. **List assumptions** — test data, environment, and any parameter the engineer must tune.

## Output shape
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 50 },   // ramp-up
    { duration: '3m', target: 50 },   // steady load
    { duration: '1m', target: 0 },    // ramp-down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  const res = http.get('https://api.example.com/orders');
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}
```

## Guardrails
- Never script load without an approved plan with thresholds.
- Simulate realistic user behavior, not raw loops — think times and data matter.
- Thresholds must come from the plan; do not invent pass/fail numbers.
- The script is a draft to run in a dedicated perf environment, never against production.
