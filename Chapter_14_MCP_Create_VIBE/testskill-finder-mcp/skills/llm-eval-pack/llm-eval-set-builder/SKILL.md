---
name: llm-eval-set-builder
description: >-
  Builds evaluation sets for testing LLM outputs: golden question/answer pairs, rubrics,
  and pass/fail criteria. Use when a tester says "build an eval set", "create golden
  questions", "make test data for the LLM", or wants to measure model quality on a task.
  Produces a labeled eval set and scoring rubric, stopping for review.
license: MIT
metadata:
  author: TheTestingAcademy
  area: llm-evaluation
  version: 1.0.0
---

# LLM Eval Set Builder

You build **evaluation sets** that measure how well an LLM does a task — a labeled set of
inputs with expected outputs and a rubric for scoring. An eval set is test data for a
model, and it is only as good as its labels.

## When to use
- LLM output quality needs to be measured, not eyeballed.
- Someone says "build an eval set", "create golden questions", "make eval data".
- A prompt or model change needs regression testing.

## Workflow
1. **Define the task.** What is the model being asked to do, and what does "correct" mean?
   Capture the input, expected output, and the dimensions that matter (accuracy, format,
   grounding, tone).
2. **Collect and label examples.** Gather diverse real inputs and write ground-truth
   outputs. Cover edge cases and failure modes, not just happy paths.
3. **Write the rubric.** For each dimension, define score levels (e.g. 0-3) with concrete
   criteria, so two graders would agree on a score.
4. **Balance the set.** Ensure the set spans categories, difficulties, and languages the
   model will face, without leaking answers into the prompt.
5. **HUMAN REVIEW GATE (mandatory).** Review labels for correctness and the rubric for
   ambiguity; a wrong gold label silently poisons every future score.

## Output shape
```yaml
# eval set
task: "generate a test plan from a requirement"
examples:
  - input: "<requirement text>"
    expected: "<ground-truth test plan outline>"
    dimensions: [completeness, correctness, structure]
rubric:
  completeness: { 0: "missing sections", 1: "partial", 2: "full" }
  correctness:  { 0: "wrong facts", 1: "minor errors", 2: "accurate" }
```

## Guardrails
- Never auto-generate gold labels without human review — wrong labels poison scores.
- Keep the eval set diverse and representative, not cherry-picked.
- Do not leak the expected output into the prompt under test.
- The eval set is a draft until a human approves labels and rubric.
