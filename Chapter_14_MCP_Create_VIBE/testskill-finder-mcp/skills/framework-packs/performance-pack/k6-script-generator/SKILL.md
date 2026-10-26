---
name: k6-script-generator
description: >-
  Generates k6 load and performance test scripts with stages, thresholds, checks, and
  reusable scenarios. Use when a tester says "write a k6 script", "generate a k6 load
  test", "set up k6 thresholds", or wants JavaScript-based load testing. Produces runnable
  k6 scripts for the engineer to execute against a perf environment.
license: MIT
metadata:
  author: TheTestingAcademy
  pack: performance
  version: 1.0.0
---

# k6 Script Generator

You write **k6 scripts** that are readable, configurable, and carry their own pass/fail
thresholds. k6 is the fastest way to turn a workload model into a reproducible load test.

## When to use
- A load test is needed and k6 is the chosen tool.
- Someone says "write a k6 script", "generate a k6 test", "set up k6 thresholds".
- A perf check should run in CI as a lightweight smoke.

## Workflow
1. **Read the workload model.** Extract virtual users, stages/ramp, endpoints, and
   thresholds. If missing, ask — do not invent load numbers.
2. **Structure the script.** Use `options.stages` for ramp, `options.thresholds` for
   pass/fail, and the default function for the user journey. Add tags per endpoint.
3. **Add checks and metrics.** Use `check()` for functional assertions and threshold
   expressions for latency/error rates. Keep checks cheap.
4. **Make it configurable.** Parameterize the base URL, users, and duration via env vars
   or a config object so the same script runs at different intensities.
5. **List assumptions** — endpoints, auth, data, and environment.

## Output shape
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 10 },
    { duration: '1m', target: 10 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<400'],
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  const res = http.get(`${__ENV.BASE_URL}/health`);
  check(res, { '200': (r) => r.status === 200 });
  sleep(1);
}
```

## Guardrails
- Never invent a load number or threshold — take them from the plan or ask.
- Keep `check()` cheap and threshold expressions simple; heavy logic skews results.
- Do not run load scripts against production without explicit approval.
- The script is a draft to run in a dedicated perf environment.
