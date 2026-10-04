# 03 — Test cases (~5,000)

**Put here:** the test-case exports as `.csv` or `.xlsx` (one row per test case).

**Ingested by:** `qabuddy.ingest.testcases` — one document per row, no splitting.

**Expected columns (any subset works):** `Test Case ID`, `Summary`, `Preconditions`,
`Test Data`, `Test Steps`, `Expected Result`, `Priority`, `Category`, `Scenario Type`,
`Test Type`, `Execution Status`, `Environment`.

Test-case IDs (e.g. `WING-LOGIN-TC-089`) are preserved verbatim so exact-match search works.
