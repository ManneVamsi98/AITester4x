# Flaky Test Analyzer

Compares two Playwright JSON reports from the same suite and reports **how many test cases are
flaky** — tests whose pass/fail status flipped between the two runs.

| Path | Description |
|---|---|
| `flaky_analyze.py` | The analyzer. Stdlib only, no dependencies. |
| `flaky_analyzer_component.py` | Langflow custom component wrapping the analyzer, for the UI. |
| `build_flaky_analyzer_flow.py` | Builds the Langflow flow, and pushes it into a running Langflow. |
| `Flaky Analyzer.json` | The generated Langflow flow export. |
| `Flaky_Test_Analyzer.md` | This document. |

## What "flaky" means here

A test is flaky when it **passed in one run and failed in the other**. That is the whole rule:
the status has to *change*.

| Run 1 | Run 2 | Classification |
|---|---|---|
| passed | failed | **flaky** — regressed |
| failed | passed | **flaky** — recovered |
| failed | failed | consistently failing — a real, reproducible defect, **not** flaky |
| passed | passed | consistently passing |
| skipped | anything | excluded from the flaky count |

## Worked example

A suite of 100 tests, run twice.

**Run 1** — 97 passed, 3 failed: `A`, `B`, `C` fail.
**Run 2** — `A` and `B` still fail, `C` now passes.

| Test | Run 1 | Run 2 | Classification |
|---|---|---|---|
| A | failed | failed | consistently failing — real bug |
| B | failed | failed | consistently failing — real bug |
| C | failed | passed | **flaky** (recovered) |

**Flaky test cases: 1** (`C`). Consistently failing: 2 (`A`, `B`). The three buckets reconcile to
the suite size: 97 consistently passing + 2 consistently failing + 1 flaky = 100.

If the expected answer was 2, the usual reason is counting the two tests that failed in run 2. Those
failed *both* times, so they are deterministic defects rather than flakiness — the tool reports them
in their own section so they can be fixed separately.

## Setup

Two Playwright JSON reports in one folder, named exactly:

```
<folder>/
  result1.json
  result2.json
```

Produce them with Playwright's JSON reporter:

```bash
npx playwright test --reporter=json > result1.json
```

Any other `.json` in the folder is ignored.

## Run

```bash
python Chapter_09_Langflow/flaky_analyze.py "<folder>"
```

Optionally write the reports somewhere other than the input folder:

```bash
python Chapter_09_Langflow/flaky_analyze.py "<folder>" --output-dir <somewhere>
```

Console output:

```
Folder: <folder>
  result1.json: 100 tests — 97 passed, 3 failed, 0 skipped
  result2.json: 100 tests — 98 passed, 2 failed, 0 skipped
  matched by: test id

Flaky: 1
  - [checkout.spec.ts] checkout.spec.ts > C flips fail to pass (chromium)  run1: failed -> run2: passed  (recovered)

Consistently failing (not flaky): 2
  - [checkout.spec.ts] checkout.spec.ts > A always fails (chromium)
  - [checkout.spec.ts] checkout.spec.ts > B always fails (chromium)
```

## Run in Langflow (the UI)

The same analysis runs as a Langflow flow, so it can be used from Langflow's playground instead of
a terminal. The flow is already loaded in the local instance: **My Projects → Flaky Test Analyzer**.

### Using it

1. Open the flow and click the **Flaky Test Analyzer** node.
2. Upload `result1.json` into **Run 1 report** and `result2.json` into **Run 2 report**.
3. Run the flow. The chat panel shows the per-run counts, the `Flaky: N` headline, the flaky tests,
   the consistently failing tests, and the full markdown report. The node's **Flaky tests** output
   carries the same rows as a table.

The node has two inputs and two outputs:

| Port | Name | Meaning |
|---|---|---|
| in | Run 1 report | `result1.json` — the first Playwright run |
| in | Run 2 report | `result2.json` — the second Playwright run |
| out | Report | text summary plus the full markdown report |
| out | Flaky tests | one row per flaky test: test, file, project, run 1, run 2, direction |

Bad input is reported on the node as a plain message (`file not found`, `not a Playwright JSON
report`), not a traceback.

### Regenerating and pushing

```bash
E:\lf\Scripts\python.exe Chapter_09_Langflow\build_flaky_analyzer_flow.py          # rebuild the export
E:\lf\Scripts\python.exe Chapter_09_Langflow\build_flaky_analyzer_flow.py --push   # rebuild + upload
```

Re-running `--push` updates the existing flow of the same name instead of creating a duplicate. The
component node is generated through Langflow's own template builder rather than hand-written, so it
survives a Langflow upgrade.

### Two things to know

- **The component imports `flaky_analyze.py` from this folder** instead of duplicating the counting
  logic, so the flow and the command line tool can never disagree. If this folder moves, update
  `ANALYZER_DIR` in `flaky_analyzer_component.py` and re-push.
- **Running the flow over the API needs an API key.** The UI works as-is; only programmatic runs are
  gated, because `LANGFLOW_AUTO_LOGIN` requires a valid API key since Langflow 1.5. Create one under
  Settings → API keys, or start Langflow with `LANGFLOW_SKIP_AUTH_AUTO_LOGIN=true`.

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Analysed — no flaky tests |
| `1` | Analysed — flaky tests found |
| `2` | Bad input — folder missing, `result1.json`/`result2.json` missing, invalid JSON, or not a Playwright report |

Exit `1` on flakiness makes the tool usable as a gate in a pipeline: `0` means clean, `1` means
flakiness was detected, `2` means the analysis itself failed and should not be trusted.

## Outputs

Both files are written into the target folder (or `--output-dir`):

- **`flaky-report.md`** — the readable report: summary table, the flaky list, the consistently
  failing list, and the skipped / single-run / retry-dependent lists.
- **`flaky-report.json`** — the same result, machine-readable: per-run counts, `flaky_count`,
  `matched_by`, and one entry per test with `run1`/`run2` status and `direction`.

## How tests are matched between the two runs

1. **Playwright test id** when both runs share ids — ids are stable across runs, so this is
   preferred.
2. **`project :: file :: full title path`** when the ids do not line up. If ids were present in both
   reports but share nothing in common, the tool says so as a warning rather than silently reporting
   zero flaky tests.

Tests present in only one run are listed as *not comparable* and never counted as flaky.

## Retry-dependent tests

Playwright marks a test `flaky` when it failed and then passed on retry **inside a single run**. These
are listed in their own section for visibility but are **not added to the flaky count**, which stays
purely a comparison of the two runs. This keeps the headline number aligned with the definition above.

## Sanity check

Each report's parsed pass/fail/skip counts are compared against the `stats` block inside that same
file. A mismatch means the file did not parse as expected (for example a newer Playwright schema) and
is printed as a warning, so a wrong answer is never quietly returned.

## Limitations

- Exactly two runs. There is no aggregation across three or more reports.
- A failure status covers `failed`, `timedOut`, and `interrupted`.
- Only pass/fail/skip status is compared. No assertion-message diffing, failure clustering, or
  first-failure attribution.
- The tool never modifies the input reports.
