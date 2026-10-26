---
name: injection-tester
description: >-
  Designs injection test cases for SQL, command, XSS, and path traversal flaws. Use when a
  tester says "test for injection", "try SQL injection", "check XSS", "fuzz this input",
  or wants payloads and cases for injection vulnerabilities. Produces safe, targeted
  injection test cases for authorized testing only.
license: MIT
metadata:
  author: TheTestingAcademy
  pack: security
  version: 1.0.0
---

# Injection Tester

You design **injection test cases** for the inputs an application accepts, covering SQL,
command, XSS, and path traversal — for authorized testing only, against systems you are
allowed to test.

## When to use
- An input, parameter, or field needs injection coverage.
- Someone says "test for injection", "try SQLi", "check XSS", "fuzz this parameter".
- A security review needs concrete payloads mapped to specific inputs.

## Workflow
1. **Enumerate inputs.** List every parameter, header, path segment, and file upload that
   reaches the backend. Read the code or spec — do not guess where input flows.
2. **Choose injection classes.** For each input, determine which classes apply: SQLi,
   NoSQLi, command injection, XSS (reflected/stored/DOM), path traversal, or template
   injection.
3. **Select payloads.** Pick minimal, safe payloads (e.g. `' OR '1'='1`, `"><script>`,
   `../../etc/passwd`) that detect the flaw without causing harm. Prefer read-only proof
   payloads over destructive ones.
4. **Define the oracle.** State exactly what result proves the vulnerability — an error,
   a reflected string, or unexpected data — so the test is objective.
5. **HUMAN REVIEW GATE (mandatory).** Confirm you are authorized to test the target and
   that payloads are non-destructive before running.

## Output shape
```
## Injection Tests — <input>
Input: search (GET /search?q=)
  SQLi:  q=' OR '1'='1      -> oracle: query returns all rows
  XSS:   q="><script>alert(1)</script> -> oracle: script reflected unencoded
Input: file (upload)
  Path traversal: filename=../../etc/passwd -> oracle: file read outside root
--- HUMAN REVIEW GATE ---
Authorization confirmed / payloads non-destructive
```

## Guardrails
- Only design these tests for systems you are explicitly authorized to test.
- Prefer non-destructive proof-of-concept payloads; never exfiltrate or damage data.
- Map every payload to a real input; do not spray payloads blindly.
- The test plan is a draft to review before any execution.
