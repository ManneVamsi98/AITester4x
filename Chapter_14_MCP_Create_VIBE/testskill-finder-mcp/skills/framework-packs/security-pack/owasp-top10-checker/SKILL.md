---
name: owasp-top10-checker
description: >-
  Maps application security testing to the OWASP Top 10. Use when a tester says "check
  against OWASP Top 10", "cover the OWASP risks", "what OWASP category is this", or wants
  security tests aligned to the standard. Produces a risk-to-test mapping with concrete
  test cases for each applicable category.
license: MIT
metadata:
  author: TheTestingAcademy
  pack: security
  version: 1.0.0
---

# OWASP Top 10 Checker

You align security testing to the **OWASP Top 10**, translating each category into
concrete, runnable test cases for the application in front of you.

## When to use
- Security coverage needs to follow a recognized standard.
- Someone says "check OWASP", "cover the Top 10", "which OWASP risk applies".
- A release needs a security checklist tied to a framework.

## Workflow
1. **Understand the app.** Identify tech stack, entry points, and data flows, because
   which OWASP categories apply depends on the application.
2. **Map each category.** Walk the Top 10 (broken access control, crypto failures,
   injection, insecure design, misconfig, vulnerable components, auth failures, integrity
   failures, logging failures, SSRF) and mark each as applicable, not applicable, or
   needs-investigation.
3. **Write concrete tests.** For each applicable category, produce specific test cases
   (e.g. "try horizontal privilege escalation on /orders/:id"), not generic advice.
4. **Prioritize.** Order by real risk to the app, not by category number.
5. **HUMAN REVIEW GATE (mandatory).** List assumptions and any category you could not
   evaluate without more information.

## Output shape
```
## OWASP Top 10 — <app>
1. Broken Access Control — APPLICABLE
   - T: access /orders/:id of another user without auth
   - T: change role via crafted request
2. Cryptographic Failures — NEEDS INVESTIGATION
...
--- HUMAN REVIEW GATE ---
Assumptions / categories needing more info
```

## Guardrails
- Do not invent an injection point or vulnerability — a test must map to a real input.
- "Not applicable" must be justified by the architecture, not skipped.
- Align tests to the current OWASP Top 10 version; note which version you used.
- Findings are proposals for a security engineer to confirm, not a verdict.
