---
name: advanced-selenium-automation-framework
description: Generate functional test cases under strict anti-hallucination rules combined with RICE prioritization. Use when user requests test cases, QA coverage, test design for checkout or any flow, or mentions anti-hallucination, RICE prioritization of tests, or incomplete requirements. Triggers on PRD-based testing, missing-spec scenarios, or skeptical thorough test generation.
---

# Anti-Hallucination QA Test Generation with RICE Prioritization

## Overview

Produce independently executable functional test cases that use ONLY explicitly provided information (PRD, API docs, logs, screenshots, test data, user input). Apply RICE scoring to prioritize the resulting test cases. Never invent features, APIs, error codes, UI elements, or behavior.

## Core Process (Mandatory)

Follow these steps in order. If any step cannot be completed, stop and report why.

**Step 1: Extract verifiable facts**
- List every concrete fact present in the supplied inputs (PRD sections, API contracts, log messages, UI labels from screenshots, given test data, explicit user statements).
- Quote or paraphrase only what is written. Do not paraphrase into new claims.

**Step 2: List unknown / missing information**
- Explicitly enumerate every detail required for a complete test but absent from the inputs.
- Mark each gap with "[NOT SPECIFIED]".

**Step 3: Generate output ONLY from Step 1 facts**
- Create test cases solely from verified facts.
- If insufficient facts exist to produce even one valid test case for a requested category, output "Insufficient information to determine." for that category and do not fabricate.
- Each test case must be independently executable (no shared mutable state assumptions beyond what is documented).
- Cover only the categories or scenarios the user explicitly requested when facts support them.

**Step 4: Apply RICE prioritization to generated tests**
- For every test case that survives Step 3, compute a RICE score using only data present in the inputs or explicitly supplied by the user:
  - Reach = estimated number of users or transactions affected per relevant period (use only numbers given; otherwise mark "[NOT SPECIFIED]" and set Reach = 1 as neutral placeholder).
  - Impact = 0.25 / 0.5 / 1 / 2 / 3 scale based solely on documented severity or business impact statements.
  - Confidence = 50% / 80% / 100% based on strength of evidence in the supplied artifacts (data-backed = 100%, partial = 80%, mostly absent = 50%).
  - Effort = person-hours or person-months estimated only from complexity clues present in the inputs; otherwise mark "[NOT SPECIFIED]".
- RICE Score = (Reach × Impact × Confidence) ÷ Effort
- Rank the test cases by descending RICE score. If any component is "[NOT SPECIFIED]", place the test in a separate "Insufficient data for RICE" group and do not invent numbers.

**Step 5: Self-validation check**
- Confirm every assertion is traceable to Step 1.
- Confirm no invented features, error codes, UI elements, or behavior appear.
- Confirm gaps are labeled "[NOT SPECIFIED]" or "Insufficient information to determine."
- Confirm output is deterministic (identical input yields identical result).

## Required Output Format

Always structure the response as:

- Verified Facts:
- Missing / Unknown Information:
- Generated Output:
  (table or list of test cases; each row/item contains Test ID, Category, Description, Steps, Expected Result, Priority, RICE Score)
- Self-Validation Check:

If the user requested a specific table format, use it inside the Generated Output section while still satisfying the five-step process above.

## Strict Rules (Non-negotiable)

1. DO NOT invent features, APIs, error codes, UI elements, or behavior.
2. DO NOT assume default or typical system behavior.
3. If information is missing or unclear, respond with "Insufficient information to determine."
4. Every assertion must be traceable to provided input.
5. If a detail is inferred, label it explicitly as "Inference (low confidence)".
6. Output must be deterministic and repeatable.
7. Never fill RICE components with guessed numbers; leave them marked when data is absent.
8. Test cases that cannot be fully specified from the inputs are omitted or flagged; they are never completed by assumption.

## When Inputs Are Insufficient

If the supplied artifacts lack enough concrete detail to produce the minimum number of test cases requested, output only the five-step structure with "Insufficient information to determine." in the Generated Output section. Do not expand, pad, or invent to meet a numeric quota.

## References

- Load the anti-hallucination rules exactly as supplied by the user when present.
- RICE scoring follows the standard (Reach × Impact × Confidence) ÷ Effort definition; scales are applied only when values appear in the input or are explicitly defined by the user.