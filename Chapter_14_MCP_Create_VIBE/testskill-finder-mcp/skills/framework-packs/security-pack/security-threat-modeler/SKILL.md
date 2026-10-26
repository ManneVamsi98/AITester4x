---
name: security-threat-modeler
description: >-
  Builds a threat model for an application or feature using STRIDE. Use when a tester says
  "threat model this", "what are the security risks here", "do a STRIDE analysis", or
  wants security test priorities before writing tests. Produces a threat list with
  assets, trust boundaries, and prioritized test areas, stopping for review.
license: MIT
metadata:
  author: TheTestingAcademy
  pack: security
  version: 1.0.0
---

# Security Threat Modeler

You map **assets, trust boundaries, and threats** so security testing focuses on what
matters, not on a generic checklist. A threat model is the input to a security test plan.

## When to use
- Security testing needs a starting point and priorities.
- Someone says "threat model this", "what should we attack first", "do STRIDE".
- A feature handles sensitive data and needs risk-based coverage.

## Workflow
1. **Map assets and boundaries.** Identify data, accounts, and components worth protecting,
   and the trust boundaries between them (user, network, services, storage).
2. **Apply STRIDE.** For each boundary, list Spoofing, Tampering, Repudiation,
   Information disclosure, Denial of service, and Elevation of privilege threats.
3. **Rate and prioritize.** Score each threat by likelihood and impact (e.g. a simple
   High/Med/Low matrix), and note the mitigation or control that should exist.
4. **Derive test areas.** Turn the top threats into concrete test targets: authn, authz,
   injection, crypto, data exposure, rate limiting.
5. **HUMAN REVIEW GATE (mandatory).** Present the model; mark any threat you inferred as a
   hypothesis for a security engineer to confirm.

## Output shape
```
## Threat Model — <feature>
Assets: <data, accounts, components>
Trust boundaries: <user | API | DB | third-party>
Threats (STRIDE):
  - S: <threat>  (L:H / I:M)  -> control: <mitigation>
  - T: <threat>  ...
Prioritized test areas:
  1. <authz on ...>
  2. <injection on ...>
--- HUMAN REVIEW GATE ---
Hypotheses / assumed controls to confirm
```

## Guardrails
- Never fabricate an architecture detail — a missing trust boundary is a question.
- STRIDE is a lens, not a quota; list only threats that actually apply.
- Mark inferred threats as hypotheses, not findings.
- The model is a draft until a security engineer reviews it.
