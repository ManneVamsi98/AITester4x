# VWO Test Plan — app.vwo.com (Login + Dashboard Smoke)

> Generated with the **RICEPOT** structured-prompt framework (Role → Instructions → Context → Example → Parameters → Output → Tone), following enterprise/IEEE 829-style test-plan standards and the repository's RICE POT house conventions.

---

## 1. Document Control

| Field | Value |
|---|---|
| **Project** | VWO (Wingify) — Application Testing |
| **Application Under Test** | `https://app.vwo.com/#/login` |
| **Document Title** | Industry-Level Test Plan — VWO Login & Dashboard Smoke |
| **Version** | 1.0 |
| **Status** | Draft for review |
| **Author** | CommandCodeBot (AI-assisted) |
| **Reviewers** | QA Lead, SDET, Product Owner (to be assigned) |
| **Date** | 2026-08-11 |
| **Framework Alignment** | RICEPOT — `Chapter_02_Prompt_Eng\01_RICE_POT_Template.md`, `02_RICE_POT.example.md`, `04_Plan_Framework.md` |

### 1.1 Change History

| Version | Date | Author | Description |
|---|---|---|---|
| 0.1 | 2026-08-11 | CommandCodeBot | Initial draft created from Chapter_01 VWO requirements |
| 1.0 | 2026-08-11 | CommandCodeBot | Reviewed and finalized for approval |

---

## 2. Introduction

### 2.1 Purpose

This document defines the test plan for validating the **VWO login module** at `https://app.vwo.com/#/login` and performing a **smoke validation of the post-login VWO dashboard**. It establishes the scope, strategy, test environments, test data, deliverables, entry/exit criteria, automation approach (RICEPOT Selenium framework), defect management, metrics, risks, and approval process.

### 2.2 Scope

In scope:

- **Core authentication** — email + password login (valid, invalid, blank, malformed inputs)
- **Field validation** — on-blur validation, email format validation, password complexity/length rules
- **Authentication error handling** — actionable error messages, loading state, duplicate-submission protection
- **Rate limiting / brute-force protection** — 3 failed attempts lockout behavior
- **Session management** — 1-hour session timeout, Remember Me, logout invalidation
- **Password reset (Forgot Password)** — email-based recovery, secure reset token (1-hour validity), reset with valid/invalid password, post-reset navigation to login, login with new password
- **2FA / MFA (optional)** — OTP flow, invalid/expired/empty OTP, OTP retry rate limiting
- **Enterprise SSO** — SAML/OAuth flow availability, success/failure, cancel, unauthorized user
- **Registration / new-user flow** — free-trial link, onboarding, login after registration
- **UI/UX** — branding, layout, labels, auto-focus, loading state, error placement, Light/Dark Mode
- **Responsive / mobile** — rendering, orientation, touch controls, keyboards, no horizontal scroll, mobile validation
- **Accessibility** — keyboard navigation, tab order, screen-reader labels, focus visibility, high contrast, WCAG 2.1 AA
- **Security (login-scoped)** — HTTPS enforcement, password not exposed in URL/storage, secure transmission, rate limiting, account-enumeration protection, SQLi/XSS input rejection, session fixation/hijacking protection, CSRF, token manipulation/reuse rejection
- **Integration** — login → VWO dashboard redirect, personalized dashboard, analytics events
- **Browser compatibility** — Chrome, Edge, Firefox, Safari, Android, iOS
- **Error recovery** — network interruption, service unavailable, request timeout
- **Dashboard smoke** — post-login landing, key dashboard elements render, logout works

Out of scope:

- Full VWO product functionality (campaigns, experiments, reports, settings, billing)
- Load / stress / soak performance testing at production scale
- Penetration testing (covered by a dedicated security engagement)
- API contract testing beyond the authentication response codes already specified in requirements

### 2.3 References

| ID | Document | Location |
|---|---|---|
| R1 | VWO Login Dashboard — Test Cases with Anti-Hallucination Rules | `Chapter_01_LLM Basics\Use_the_Anti_Hallucination_Rule.md` |
| R2 | VWO Login Dashboard — Test Cases (No Anti-Hallucination Rules) | `Chapter_01_LLM Basics\Without_Use_the_Anti_Hallucination_Rule.md` |
| R3 | RICE POT Template | `Chapter_02_Prompt_Eng\01_RICE_POT_Template.md` |
| R4 | RICE POT Example (Salesforce) | `Chapter_02_Prompt_Eng\02_RICE_POT.example.md` |
| R5 | RICE POT Framework Plan | `Chapter_02_Prompt_Eng\04_Plan_Framework.md` |
| R6 | RICEPOT Selenium Advance Framework (Maven project) | `Chapter_02_Prompt_Eng\RICE_POT_SeleniumAdvanceFramework\` |
| R7 | VWO Login Dashboard PRD | Provided by product team — see note in §2.4 |

### 2.4 Requirements Source Note

The PRD referenced in Chapter_01 was provided as test-case-generation context; no standalone PRD file exists in this repository. The de-facto requirements baseline for this plan is the set of **verified facts** in reference R1 and the **coverage areas** in R2. Where a requirement detail was explicitly marked "missing / unknown" under the anti-hallucination rules (e.g., exact rate-limit response semantics, exact API endpoints), this plan flags it as **to be confirmed (TBC)** rather than inventing a value.

---

## 3. Test Strategy

| Aspect | Strategy |
|---|---|
| **Approach** | Risk-based, requirement-driven. Test effort weighted toward Critical/High-priority authentication, security, and session flows. |
| **Generation Method** | RICEPOT framework — Role (Senior QA, 15+ yrs), Instructions, Context (app.vwo.com login), Example (repo house format), Parameters (external URLs/creds supplied separately), Output (enterprise test plan + sample cases), Tone (technical, precise, enterprise-grade). |
| **Automation vs Manual** | Automation-first for the critical login paths, validation, and dashboard smoke using the existing RICEPOT Selenium framework (TestNG). Manual execution for accessibility, visual UI/UX, responsive/mobile, and exploratory checks. |
| **Data-Driven Testing** | Boundary/validation cases (email formats, password lengths, complexity) executed data-driven from a test-data source (config.properties / CSV) rather than hardcoded in test methods. |
| **Execution Order** | Smoke suite first (SMK-01..20 style), then functional, then security/regression. Parallelism disabled at suite level (house style: `parallel="false"`) to avoid rate-limit interference. |
| **Traceability** | Every test case maps to a requirement/verified fact in R1/R2. Coverage matrix maintained in §10. |
| **Environment** | Test against the external URL and staging URL supplied by the user (placeholders below); no production data mutation. |

---

## 4. Scope / Out-of-Scope Matrix

| Area | In Scope | Out of Scope |
|---|---|---|
| Authentication (email/password) | ✅ | — |
| Field validation & error handling | ✅ | — |
| Rate limiting / brute-force | ✅ (behavior + response) | Load-tool-based brute-force benchmarking |
| Sessions & Remember Me | ✅ | — |
| Password reset | ✅ | — |
| 2FA / MFA | ✅ (optional accounts) | — |
| Enterprise SSO | ✅ (SAML/OAuth flow) | IdP administration |
| Registration / new-user | ✅ (link, onboarding) | Billing/payment |
| UI/UX & themes | ✅ | Full design-system audit |
| Responsive / mobile | ✅ | Device-farm device matrix beyond supported list |
| Accessibility | ✅ (WCAG 2.1 AA spot checks) | Full formal accessibility audit |
| Security (login-scoped) | ✅ | Full pen test, infrastructure hardening |
| Performance | ⚠️ Page-load SLA spot checks only | Load/stress/soak at scale |
| API | ⚠️ Auth response codes only (200 per R1) | Full API contract suite |
| Dashboard | ✅ Smoke only (render + logout) | Dashboard feature functionality |
| Compatibility | ✅ Supported browsers/devices | Legacy/unsupported browsers |

---

## 5. Test Environments & Test Data

### 5.1 Environments

| Environment | URL | Purpose |
|---|---|---|
| Production | `https://app.vwo.com/#/login` | Baseline verification, smoke (read-only) |
| External staging | `<external staging URL — to be provided by user>` | Primary test environment, full execution |
| Local framework | `Chapter_02_Prompt_Eng\RICE_POT_SeleniumAdvanceFramework\` | Automation execution (Maven + TestNG) |

### 5.2 Browsers / Devices

| Browser | Version | OS | Priority |
|---|---|---|---|
| Google Chrome (primary) | Latest stable | Windows 11 | P0 |
| Microsoft Edge | Latest stable | Windows 11 | P1 |
| Mozilla Firefox | Latest stable | Windows 11 | P1 |
| Safari | Latest stable | macOS | P1 |
| Chrome (Android) | Latest stable | Android | P1 |
| Safari (iOS) | Latest stable | iOS | P1 |

### 5.3 Test Data & Credentials

| Data Item | Value | Source / Status |
|---|---|---|
| Valid email | `vmtester@yopmail.com` | R1 (user-supplied test credential) |
| Valid password | `Pass@1234` | R1 (user-supplied test credential) |
| Invalid email formats | `vmtester`, `vmtester@`, `vmtesteryopmail.com`, `abc` | R1 |
| Password boundaries | 3 / 4 / 10 / 11 chars | R1 (min 4, max 10) |
| Complexity samples | `Pass@1234` (valid); missing lowercase/uppercase/special (invalid) | R1 |
| Password-reset mailbox | `vmtester@yopmail.com` (yopmail) | R1 — reset email retrieval |
| 2FA account | `<to be provided>` | TBC — requires 2FA-enabled test account |
| SSO account | `<to be provided>` | TBC — requires SSO-enabled org |
| Unregistered email | `no-such-user@yopmail.com` (or equivalent disposable) | Derived — confirm no production account exists |
| Additional external creds | `<external username / password — to be provided by user>` | Placeholder per RICE POT Parameters |

> **Policy:** Credentials are never hardcoded into test cases or committed. Automation reads them from the **gitignored** `config.properties` (see §12). Tests skip with a `SkipException` when credentials are placeholders.

---

## 6. Roles & Responsibilities

| Role | Responsibility |
|---|---|
| **QA Lead** | Test plan ownership, review, sign-off, test execution coordination, entry/exit criteria enforcement |
| **SDET / Automation Engineer** | RICEPOT framework automation (Page Object, TestNG scripts), CI integration, maintenance |
| **Manual QA Tester** | Manual functional/UI/accessibility/mobile execution, defect reporting |
| **DevOps** | Environment provisioning, test data reset, CI pipeline |
| **Product Owner** | Requirement clarification (TBC items), defect triage, approval |

---

## 7. Test Schedule & Milestones

| Phase | Activities | Exit Criterion |
|---|---|---|
| **Kickoff** | Confirm scope, environments, credentials, access to staging | Access granted; creds validated |
| **Test Design** | Detail test cases from R1/R2 baseline; traceability matrix | Coverage matrix complete; cases reviewed |
| **Automation Setup** | RICEPOT VWO framework scaffold (config, Page Object, tests) | `mvn test` green on smoke subset |
| **Smoke Execution** | SMK-01..20 + dashboard smoke on staging | All smoke tests pass |
| **Functional Execution** | Login, validation, password reset, sessions, 2FA, SSO, integration | All P0/P1 pass or defect-logged |
| **Cross-Functional** | UI/UX, responsive, accessibility, security, compatibility | No open Blocker/Critical |
| **Defect Cycle** | Fix-retest regression; metric collection | Exit criteria met |
| **Sign-off** | Review report, approval | Sign-off obtained |

---

## 8. Test Deliverables

| Deliverable | Format | Owner |
|---|---|---|
| This test plan | Markdown | QA Lead |
| Detailed test cases (with traceability) | Markdown tables (see §10, §11) | QA / SDET |
| Automated test scripts | Java + TestNG (`com.vwo` package) | SDET |
| Execution reports | TestNG surefire-reports HTML/XML | SDET |
| Defect log | Issue tracker (JIRA-style) | QA |
| Test summary / sign-off report | Markdown | QA Lead |

---

## 9. Entry / Exit / Suspension / Resumption Criteria

### 9.1 Entry Criteria

- Staging environment is available and stable (login reachable over HTTPS).
- Test credentials are valid and provisioned (incl. 2FA/SSO if in scope).
- RICEPOT framework compiles and smoke subset passes.
- Test cases reviewed and approved.
- Defect tracker is accessible.

### 9.2 Exit Criteria

- 100% of P0 (Critical) and ≥95% of P1 (High) test cases executed.
- ≥95% overall pass rate; every failure has an associated defect.
- No open Blocker/Critical defects.
- All TBC items either resolved or explicitly risk-accepted.
- Test summary report delivered and signed off.

### 9.3 Suspension Criteria

- Environment unavailable > 24h or blocking >30% of planned execution.
- Critical defect blocks more than one functional area (e.g., authentication entirely down).
- Invalid test data that cannot be reset.

### 9.4 Resumption Criteria

- Environment restored and smoke suite passes.
- Blocking defect fixed or workaround verified.
- Data reset completed and re-validated.

---

## 10. Test Case Coverage & Traceability

Coverage is organized into suites, reusing the Chapter_01 TC-ID conventions. Each suite maps to reference IDs in R1 (`AUTH-001..042`) and R2 (`VWO-*`, `SMK-*`).

| Suite | Coverage | TC-ID Convention | Source Reference | Priority Focus |
|---|---|---|---|---|
| Functional — Login & Validation | Valid/invalid/blank credentials, email format, password rules, button behavior, duplicate submission, loading state | `VWO-LOGIN-001..015` | R1 AUTH-001..012, R2 §1 | P0 |
| Password Management | Forgot-password flow, reset token (1h validity, reuse, tamper), complexity, new/old password login | `VWO-PWD-001..014` | R1 AUTH-017..023, AUTH-031..040, R2 §3 | P0 |
| Session & Remember Me | Session timeout (1h), Remember Me, logout invalidation, token security, concurrent sessions | `VWO-SESSION-001..008` | R1 AUTH-015, AUTH-028..030, R2 §2 | P0 |
| 2FA / MFA | OTP flow, valid/invalid/expired/empty OTP, retry limiting | `VWO-MFA-001..006` | R2 §4 | P0 |
| Enterprise SSO | SAML/OAuth success/failure, cancel, unauthorized user | `VWO-SSO-001..006` | R2 §5 | P0 |
| Registration / New User | Free-trial link, onboarding, login after registration | `VWO-REG-001..004` | R2 §6 | P1 |
| Dashboard Smoke | Post-login landing, key elements render, logout | `VWO-DASH-001..00N` | R1 "main VWO dashboard", R2 VWO-INT-001/002 | P0 |
| UI / UX | Branding, layout, labels, auto-focus, loading, error placement, Light/Dark | `VWO-UI-001..012` | R2 §7 | P1 |
| Responsive / Mobile | Rendering, orientation, touch, keyboards, no horizontal scroll, mobile validation | `VWO-MOB-001..008` | R2 §8 | P1 |
| Accessibility | Keyboard nav, tab order, labels, focus, contrast, WCAG 2.1 AA | `VWO-A11Y-001..009` | R2 §9 | P0 |
| Security | HTTPS, no password in URL/storage, rate limiting, enumeration, SQLi/XSS, session fixation/hijacking, CSRF, token security | `VWO-SEC-001..018` | R1 AUTH-014, AUTH-016, AUTH-024..027, R2 §10 | P0 |
| Performance (spot) | Login page load ≤ 2s, response SLA spot checks | `VWO-PERF-001..002` | R2 §11 | P1 |
| Integration | Login → dashboard, personalized dashboard, analytics | `VWO-INT-001..009` | R2 §12 | P1 |
| Compatibility | Chrome/Edge/Firefox/Safari, Android/iOS, resolutions | `VWO-COMP-001..008` | R2 §13 | P1 |
| Error Recovery | Network interruption, service unavailable, timeout | `VWO-ERR-001..006` | R2 §14 | P1 |
| **Smoke** | 20-case daily smoke suite | `SMK-01..20` | R2 §15 | P0 |

---

## 11. Sample Test Cases (RICEPOT-Generated)

The following worked examples demonstrate the house format (`| Test ID | Scenario | Preconditions / Test Data | Steps | Expected Result | Priority |`) used across all suites. Full case set is expanded from R1/R2 at execution time.

### 11.1 Functional — Authentication

| TC ID | Scenario | Preconditions / Test Data | Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| VWO-LOGIN-001 | Verify login with valid credentials | Valid account: `vmtester@yopmail.com` / `Pass@1234` | 1. Open login page 2. Enter email 3. Enter password 4. Click **Login** | User authenticated and lands on the main VWO dashboard | P0 |
| VWO-LOGIN-002 | Verify login with invalid email | Invalid email + `Pass@1234` | 1. Enter invalid email 2. Enter password 3. Click **Login** | Authentication fails; appropriate error message displayed | P0 |
| VWO-LOGIN-003 | Verify login with invalid password | `vmtester@yopmail.com` + wrong password | 1. Enter email 2. Enter wrong password 3. Click **Login** | Authentication fails; clear actionable error displayed | P0 |
| VWO-LOGIN-005 | Verify blank email field | Blank email + password | 1. Leave email blank 2. Enter password 3. Click **Login** | Error: **"Email or password is required"** | P0 |
| VWO-LOGIN-007 | Verify both fields blank | No input | 1. Leave both fields blank 2. Click **Login** | Required-field validation message displayed | P0 |
| VWO-LOGIN-009 | Verify invalid email format | `vmtester`, `abc` | 1. Enter invalid format 2. Move focus away | Email format validation triggered on blur | P0 |
| VWO-LOGIN-014 | Verify duplicate submission protection | Valid credentials | 1. Click **Login** rapidly multiple times | Only one authentication request processed appropriately | P1 |

### 11.2 Security — Rate Limiting

| TC ID | Scenario | Preconditions / Test Data | Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| VWO-SEC-005 | Verify brute-force / rate limiting | Invalid credentials | 1. Attempt login with invalid creds 3 times | Rate limiting triggered after 3 failed attempts (behavior per R1; exact response TBC) | P0 |
| VWO-SEC-005a | Verify 4th attempt after rate limit | 3 failed attempts recorded | 1. Attempt login a 4th time | Subsequent attempt handled per defined rate-limit behavior (TBC) | P0 |
| VWO-SEC-006 | Verify account-enumeration protection | Invalid email vs. valid email with wrong password | 1. Compare error responses | Errors do not unnecessarily reveal whether an account exists | P1 |
| VWO-SEC-007 | Verify SQLi input rejection | `' OR 1=1 --` in email field | 1. Enter payload 2. Submit | Malicious input rejected/handled safely; no unauthorized access | P0 |
| VWO-SEC-009 | Verify XSS payload rejection | `<script>alert(1)</script>` in password field | 1. Enter payload 2. Submit | Payload not executed | P0 |

### 11.3 Password Reset

| TC ID | Scenario | Preconditions / Test Data | Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| VWO-PWD-001 | Verify Forgot Password option | Login page open | 1. Observe recovery option | **forgot password** option available | P0 |
| VWO-PWD-007 | Verify reset token within validity | Valid reset token (1h validity) | 1. Generate token 2. Use within 1 hour | Token accepted within its 1-hour validity | P0 |
| VWO-PWD-008 | Verify expired reset token | Expired token | 1. Use token after 1 hour | Reset rejected; token no longer valid | P0 |
| VWO-PWD-013 | Verify login with new password | Password successfully reset | 1. Land on login 2. Enter email 3. Enter new password 4. Click **Login** | Authentication succeeds with new password | P0 |
| VWO-PWD-014 | Verify old password invalidated | Password reset completed | 1. Attempt login with old password | Old password no longer authenticates | P0 |

### 11.4 Dashboard Smoke

| TC ID | Scenario | Preconditions / Test Data | Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| VWO-DASH-001 | Verify dashboard landing after login | Valid credentials | 1. Login successfully | Redirected to main VWO dashboard | P0 |
| VWO-DASH-002 | Verify key dashboard elements render | Authenticated session | 1. Observe dashboard 2. Verify core widgets/navigation render | Dashboard renders without layout breakage; core elements visible | P0 |
| VWO-DASH-003 | Verify logout from dashboard | Authenticated session | 1. Click logout 2. Verify redirect | Session invalidated; redirected to login; protected dashboard inaccessible via Back | P0 |
| VWO-DASH-004 | Verify session timeout redirects to login | Authenticated session expired (1h inactivity) | 1. Allow session timeout 2. Access dashboard | Redirected to login / re-authentication required | P0 |

---

## 12. Automation Strategy (RICEPOT Framework)

Reuses the existing **RICEPOT Selenium Advance Framework** conventions (`R6`) — Maven, Java 17, Selenium 4.20.0, TestNG 7.10.2, WebDriverManager 5.9.2 — with a new VWO package.

### 12.1 Component Mapping

| Component | Existing (Salesforce) | VWO Addition (future work) |
|---|---|---|
| Page Object | `com.salesforce.pages.LoginPage` | `com.vwo.pages.VwoLoginPage`, `com.vwo.pages.VwoDashboardPage` |
| Test scripts | `LoginValidTest`, `LoginInvalidTest` | `VwoLoginValidTest`, `VwoLoginInvalidTest`, `VwoDashboardSmokeTest` |
| Config | `src/test/resources/config.properties` (gitignored) | Same file; keys `vwo.url`, `vwo.username`, `vwo.password` |
| Suite config | `testng.xml` | `testng-vwo.xml` (`parallel="false"`) |
| Reports | `target/surefire-reports/` | Same |

### 12.2 Framework Standards (house style — mandatory)

- **PageFactory + `@FindBy`** with **xpath-only** locators (no `By.id/name/cssSelector/className`).
- **Explicit `WebDriverWait`** (15s default) — **zero `Thread.sleep`**.
- **Robust exception handling** — waits wrapped in try-catch; `TimeoutException` rethrown as `AssertionError` with context; element getters return safe defaults.
- **No comments / no dead code**; consistent structure across scripts.
- **Credentials from `config.properties`** — never hardcoded; `SkipException` guard when values are placeholders.
- **TestNG lifecycle** — `@BeforeMethod` (driver init, maximize, navigate) / `@AfterMethod` (`driver.quit()`).
- **Runbook** — `mvn test -DsuiteXmlFile=testng-vwo.xml`; report at `target/surefire-reports/index.html`.

### 12.3 Automation Priority

| Priority | Automated | Examples |
|---|---|---|
| P0 | Yes — full automation | Valid/invalid/blank login, email format, rate limiting, reset flow, session, dashboard smoke |
| P1 | Yes — key paths | Remember Me, SSO happy path (if creds available), error recovery |
| P1/P2 | Manual-first | Visual UI/UX, themes, responsive, accessibility (optionally axe-core later), exploratory |

---

## 13. Defect Management & Metrics

### 13.1 Severity / Priority Matrix

| Severity | Definition | Example |
|---|---|---|
| **Blocker** | Blocks release; no workaround | Login completely unavailable |
| **Critical** | Major function broken | Valid credentials fail to authenticate |
| **Major** | Function works with workaround | Rate limit message incorrect |
| **Minor** | Cosmetic / low impact | Label alignment, theme contrast |
| **Trivial** | Negligible impact | Typo in tooltip |

| Priority | Meaning | Response SLA |
|---|---|---|
| P0 | Fix immediately | ≤ 24h |
| P1 | Fix before release | Before exit criteria |
| P2 | Fix in next release | Backlog |

### 13.2 Defect Lifecycle

New → Triage (severity/priority) → Assigned → In Progress → Fixed → Verified → Closed (or Reopened).

### 13.3 Metrics & KPI Targets

| Metric | Target |
|---|---|
| Test execution pass rate | ≥ 95% |
| P0/P1 test coverage executed | 100% / ≥ 95% |
| Open Blocker/Critical defects at exit | 0 |
| Defect rejection rate | < 10% |
| Smoke suite duration | ≤ 15 min (automated) |
| Login page load (spot check) | ≤ 2 s (per R2) |

---

## 14. Risks & Mitigations

| # | Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|---|
| 1 | **Rate limiting during automation** — 3 failed attempts lock the test account (R1) | Test data lockout | High | Rate-limit tests use a disposable account; stagger attempts; resume after lockout window |
| 2 | **Real credentials not yet provided** | P0 valid-login & dashboard tests blocked | High | Placeholders in config; skip with `SkipException`; request creds at kickoff |
| 3 | **2FA / SSO test accounts unavailable** | MFA/SSO suites blocked | Medium | Mark TBC; execute after accounts provisioned |
| 4 | **Staging environment instability / external URL changes** | Execution delays | Medium | Use user-supplied external/staging URLs; document current URLs |
| 5 | **CAPTCHA / bot detection on login** | Automation false failures | Medium | Coordinated login cadence; whitelist test IP where possible; manual fallback |
| 6 | **Password reset depends on yopmail mailbox** | Reset flow blocked | Medium | Confirm mailbox access; use dedicated disposable inbox |
| 7 | **Exact behaviors TBC** (rate-limit response, API endpoints) | Assertion ambiguity | Medium | Explicitly flag TBC; confirm with product before finalizing assertions |
| 8 | **Session timeout test needs 1h wait** | Slow execution | Medium | Use reduced-timeout config on staging if supported, else scheduled overnight run |

---

## 15. Approval

| Role | Name | Signature | Date |
|---|---|---|---|
| QA Lead | | | |
| SDET | | | |
| Product Owner | | | |

---

*End of test plan — Version 1.0*
