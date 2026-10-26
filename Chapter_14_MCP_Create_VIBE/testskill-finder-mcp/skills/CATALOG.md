# Test Skill Catalog

The `/skills` folder is the source of truth: **60 skills** in **17 categories** (36 upstream, 24 local). Each skill is a folder with a `SKILL.md` (YAML frontmatter + instructions).

## Categories

- **AI Agents** — 2 skills
- **API Testing** — 4 skills
- **Automation** — 1 skills
- **Cypress** — 5 skills
- **LLM Evaluation** — 3 skills
- **MCP** — 3 skills
- **Performance** — 3 skills
- **Playwright** — 11 skills
- **STLC · Defect Management** — 3 skills
- **STLC · Requirement Analysis** — 1 skills
- **STLC · Test Case Development** — 2 skills
- **STLC · Test Closure** — 2 skills
- **STLC · Test Design** — 2 skills
- **STLC · Test Execution** — 3 skills
- **STLC · Test Planning** — 1 skills
- **Security** — 3 skills
- **Selenium** — 11 skills

## AI Agents

| Skill | Description | Source |
|---|---|---|
| `agent-browser-controller` | Writes browser automation steps and prompts for AI browser agents (Playwright MCP, browser-use, and similar). Use when a tester says "dri... | local |
| `agent-e2e-test-planner` | Plans end-to-end test automation executed by an AI agent, breaking a user journey into agent-executable steps with checkpoints and assert... | local |

## API Testing

| Skill | Description | Source |
|---|---|---|
| `api-contract-tester` | Designs contract and schema validation tests for REST APIs from OpenAPI, Swagger, or endpoint specs. Use when a tester says "test this AP... | local |
| `api-mock-server-designer` | Designs mock API servers and stubs so tests run without a real backend. Use when a tester says "mock this API", "set up a mock server", "... | local |
| `graphql-query-tester` | Designs GraphQL query and mutation tests, including validation, auth, error, and schema checks. Use when a tester says "test this GraphQL... | local |
| `rest-assertion-writer` | Writes precise REST API assertions for status, headers, body, and JSON paths. Use when a tester says "add assertions to this API test", "... | local |

## Automation

| Skill | Description | Source |
|---|---|---|
| `ci-test-pipeline-builder` | Designs CI/CD test pipelines that run the right tests at the right stage and fail fast. Use when a tester says "set up the test pipeline"... | local |

## Cypress

| Skill | Description | Source |
|---|---|---|
| `cy-component-tester` | Writes Cypress Component Tests for React, Vue, and Angular components in isolation. Use when a tester says "write a component test", "tes... | local |
| `cy-e2e-organizer` | Organizes Cypress end-to-end test suites for readability, reuse, and fast CI. Use when a tester says "organize my Cypress specs", "struct... | local |
| `cy-fixture-designer` | Designs Cypress fixtures and test data for stable, repeatable runs. Use when a tester says "create a fixture for users", "set up test dat... | local |
| `cy-network-interceptor` | Designs cy.intercept and network stubbing strategies to control API responses, simulate latency, errors, and edge states in Cypress tests... | local |
| `cy-test-generator` | Generates Cypress end-to-end test scripts from requirements, user stories, or manual test cases. Use when a tester says "write a Cypress ... | local |

## LLM Evaluation

| Skill | Description | Source |
|---|---|---|
| `llm-eval-set-builder` | Builds evaluation sets for testing LLM outputs: golden question/answer pairs, rubrics, and pass/fail criteria. Use when a tester says "bu... | local |
| `llm-output-grader` | Grades LLM outputs against a rubric, producing scores and actionable feedback. Use when a tester says "grade this LLM output", "score thi... | local |
| `llm-prompt-regression` | Sets up prompt regression tests to catch when a prompt change degrades LLM output. Use when a tester says "regression test this prompt", ... | local |

## MCP

| Skill | Description | Source |
|---|---|---|
| `mcp-client-connector` | Writes MCP client connection configs for Claude Code, Claude Desktop, Cursor, and VS Code. Use when a tester says "connect this MCP", "ad... | local |
| `mcp-server-builder` | Builds a Model Context Protocol (MCP) server that exposes tools, resources, and prompts to any LLM client. Use when a tester says "build ... | local |
| `mcp-tool-designer` | Designs MCP tools with clear names, typed schemas, and "when to use" descriptions so a client LLM picks the right tool. Use when a tester... | local |

## Performance

| Skill | Description | Source |
|---|---|---|
| `k6-script-generator` | Generates k6 load and performance test scripts with stages, thresholds, checks, and reusable scenarios. Use when a tester says "write a k... | local |
| `load-test-scripter` | Writes load test scripts that simulate realistic user traffic and measure latency, throughput, and errors. Use when a tester says "write ... | local |
| `perf-plan-designer` | Designs a performance test plan: goals, workload model, scenarios, metrics, thresholds, and tooling. Use when a tester says "create a per... | local |

## Playwright

| Skill | Description | Source |
|---|---|---|
| `pw-accessibility-auditor` | Integrates automated accessibility checks into Playwright tests using axe-core. Use when an SDET says "add a11y checks", "run axe on this... | upstream |
| `pw-api-tester` | Designs and generates API tests using Playwright's request context. Use when an SDET says "write API tests for this endpoint", "test the ... | upstream |
| `pw-ci-configurator` | Generates CI configuration (GitHub Actions) for a Playwright suite. Use when an SDET says "set up Playwright in CI", "add a GitHub Action... | upstream |
| `pw-fixture-designer` | Designs custom Playwright test fixtures (auth/session, seeded data, page objects) with correct setup/teardown and scope. Use when an SDET... | upstream |
| `pw-flaky-debugger` | Diagnoses a flaky Playwright test and proposes web-first fixes. Use when an SDET says "this test is flaky", "passes locally fails in CI",... | upstream |
| `pw-locator-fixer` | Scans a Playwright spec or Page Object for brittle locators and rewrites them to resilient ones. Use when an SDET says "fix these locator... | upstream |
| `pw-network-mocker` | Designs Playwright route interception and mocking. Use when an SDET says "mock this API", "stub the /orders response", "force a 500 error... | upstream |
| `pw-page-object-builder` | Builds a Playwright Page Object Model class from a page or URL. Use when an SDET says "make a page object for the login page", "build a P... | upstream |
| `pw-test-generator` | Generates a Playwright (TypeScript) test spec from a described user flow or scenario. Use when an SDET says "write a Playwright test for ... | upstream |
| `pw-trace-analyzer` | Analyzes a Playwright trace.zip or test failure to pinpoint the root cause. Use when an SDET says "read this trace", "why did this test f... | upstream |
| `pw-visual-regression` | Sets up Playwright visual/screenshot regression testing. Use when an SDET says "add visual regression", "snapshot this component", "set u... | upstream |

## STLC · Defect Management

| Skill | Description | Source |
|---|---|---|
| `bug-reporter` | Turn a failure into a clean, reproducible bug report. Use when a tester says "file a bug for this", "write up this defect", or describes ... | upstream |
| `bug-triage-assistant` | Triage a batch of defects instead of grinding through them one by one. Use when a lead says "triage these bugs", "prioritize the defect b... | upstream |
| `rca-analyzer` | Run a structured root-cause analysis on a defect. Use when someone says "do an RCA for this bug", "why did this escape", or wants to unde... | upstream |

## STLC · Requirement Analysis

| Skill | Description | Source |
|---|---|---|
| `jira-requirement-analyzer` | Read a JIRA ticket and judge whether it is actually ready to test. Use when a tester says "analyze this ticket", "is this story ready to ... | upstream |

## STLC · Test Case Development

| Skill | Description | Source |
|---|---|---|
| `test-case-writer` | Expand approved test scenarios into detailed, executable test cases. Use when a tester says "write test cases for TS-1", "detail these sc... | upstream |
| `test-data-generator` | Produce the data sets a scenario or test case needs to run. Use when a tester says "generate test data", "give me boundary values for thi... | upstream |

## STLC · Test Closure

| Skill | Description | Source |
|---|---|---|
| `test-closure-reporter` | Produce the closure report that wraps up a test cycle. Use when a lead says "write the test closure report", "summarize the test cycle", ... | upstream |
| `test-coverage-analyzer` | Find the gaps between what was required and what was actually tested. Use when a lead says "where are our coverage gaps", "what isn't tes... | upstream |

## STLC · Test Design

| Skill | Description | Source |
|---|---|---|
| `api-test-designer` | Design API-level test coverage from an endpoint or contract. Use when a tester says "design API tests for POST /orders", "test this endpo... | upstream |
| `test-scenario-designer` | Derive high-level test scenarios from a requirement or acceptance criteria before anyone writes detailed steps. Use when a tester says "w... | upstream |

## STLC · Test Execution

| Skill | Description | Source |
|---|---|---|
| `automation-script-generator` | Turn an approved test case into a runnable automation script skeleton. Use when an engineer says "automate TC-5", "write a Playwright tes... | upstream |
| `regression-suite-selector` | Pick a targeted regression subset for a change instead of running the whole suite. Use when an engineer says "what regression should I ru... | upstream |
| `test-execution-tracker` | Log and summarize the execution of a test cycle. Use when a tester says "log this run", "track execution for the sprint", or reports resu... | upstream |

## STLC · Test Planning

| Skill | Description | Source |
|---|---|---|
| `test-plan-generator` | Turn a JIRA ticket into a review-ready test plan. Use when a tester or QA lead says "write a test plan for JIRA-1234", "plan testing for ... | upstream |

## Security

| Skill | Description | Source |
|---|---|---|
| `injection-tester` | Designs injection test cases for SQL, command, XSS, and path traversal flaws. Use when a tester says "test for injection", "try SQL injec... | local |
| `owasp-top10-checker` | Maps application security testing to the OWASP Top 10. Use when a tester says "check against OWASP Top 10", "cover the OWASP risks", "wha... | local |
| `security-threat-modeler` | Builds a threat model for an application or feature using STRIDE. Use when a tester says "threat model this", "what are the security risk... | local |

## Selenium

| Skill | Description | Source |
|---|---|---|
| `se-cross-browser-runner` | Sets up cross-browser Selenium execution across Chrome, Firefox, and Edge via TestNG parameters or a factory, plus a browser matrix. Use ... | upstream |
| `se-data-driven-designer` | Designs data-driven Selenium tests with TestNG @DataProvider (or Excel/CSV/JSON sources), covering valid, invalid, and boundary data sets... | upstream |
| `se-driver-manager` | Sets up browser driver management with Selenium Manager (built-in) or WebDriverManager, browser options, and a thread-safe driver factory... | upstream |
| `se-flaky-debugger` | Diagnoses flaky Selenium tests — StaleElementReferenceException, timing and synchronization races, dynamic/late-rendering elements — and ... | upstream |
| `se-framework-scaffolder` | Scaffolds a Maven Selenium framework — TestNG suite, base test, Page Object package, config loader, logging, and reporting hooks. Use whe... | upstream |
| `se-grid-configurator` | Configures Selenium Grid 4 (hub-and-node or standalone, including Docker) and wires RemoteWebDriver for parallel and distributed runs. Us... | upstream |
| `se-locator-strategist` | Recommends and repairs Selenium locator strategy — replaces brittle absolute XPath with By.id, By.cssSelector, or Selenium 4 relative loc... | upstream |
| `se-page-object-builder` | Builds a Page Object Model class in Java (PageFactory @FindBy or explicit locators) with action methods and a WebDriverWait for a given p... | upstream |
| `se-report-integrator` | Integrates reporting (Allure or ExtentReports) into a Selenium + TestNG suite with listeners, screenshot-on-failure, and step logging. Us... | upstream |
| `se-test-generator` | Generates a runnable Selenium 4 + TestNG test in Java from a plain-language scenario, using explicit waits and stable locators. Use when ... | upstream |
| `se-wait-fixer` | Scans Selenium Java code for Thread.sleep and for implicit+explicit wait mixing, then replaces them with WebDriverWait/ExpectedConditions... | upstream |

