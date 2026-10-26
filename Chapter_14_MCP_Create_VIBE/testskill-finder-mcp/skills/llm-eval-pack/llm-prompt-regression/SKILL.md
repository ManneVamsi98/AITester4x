---
name: llm-prompt-regression
description: >-
  Sets up prompt regression tests to catch when a prompt change degrades LLM output. Use
  when a tester says "regression test this prompt", "compare prompt versions", "catch
  prompt regressions", or wants to guard a prompt in CI. Produces a regression suite with
  eval sets, thresholds, and a compare workflow.
license: MIT
metadata:
  author: TheTestingAcademy
  area: llm-evaluation
  version: 1.0.0
---

# LLM Prompt Regression

You guard a prompt the way you guard code — with a **regression suite** that fails when a
change makes outputs worse. Prompts change often; regression tests make those changes safe.

## When to use
- A prompt is in production and needs protection from regressions.
- Someone says "regression test the prompt", "compare prompt versions", "guard the prompt".
- A prompt change needs before/after evidence it is not worse.

## Workflow
1. **Identify what must not break.** Pick the key dimensions and the eval set that
   represents the task. Reuse an approved eval set rather than building from scratch.
2. **Baseline the current prompt.** Run the eval set against the current prompt and record
   per-dimension scores as the baseline.
3. **Define the gate.** Set pass/fail thresholds per dimension and overall (e.g. no
   dimension may drop by more than X, aggregate may not fall below Y).
4. **Build the compare workflow.** A changed prompt runs the same eval set, and the tool
   diffs scores against the baseline and flags regressions.
5. **HUMAN REVIEW GATE (mandatory).** Confirm thresholds and eval-set relevance with the
   owner before the gate blocks changes.

## Output shape
```
## Prompt Regression — <prompt>
baseline: completeness 2.1 | correctness 2.6 | structure 1.9
candidate: completeness 2.0 | correctness 2.3 | structure 1.8
gate: no dimension drops > 0.3 and aggregate drops < 0.2
verdict: FAIL — correctness dropped 0.3 (>= threshold)
```

## Guardrails
- Reuse an approved eval set; a regression suite is only as good as its data.
- Thresholds must be chosen by the owner, not guessed.
- Compare on identical eval sets — changing both sides invalidates the diff.
- The gate is a signal, not a verdict; a human reviews failures.
