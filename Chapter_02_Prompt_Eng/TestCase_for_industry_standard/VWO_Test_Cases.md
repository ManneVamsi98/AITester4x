# VWO Test Cases — app.vwo.com (Login + Dashboard Smoke)

> Generated with the **RICEPOT** structured-prompt framework (Role → Instructions → Context → Example → Parameters → Output → Tone), following enterprise/IEEE 829 standards and the repository's house test-case table format. Pairs with `VWO_Test_Plan.md` in `Test plan_for_industry_standard\`.

---

## 1. Document Control

| Field | Value |
|---|---|
| **Project** | VWO (Wingify) — Application Testing |
| **Application Under Test** | `https://app.vwo.com/#/login` |
| **Document Title** | Industry-Level Test Cases — VWO Login & Dashboard Smoke |
| **Version** | 1.0 |
| **Status** | Draft for review |
| **Author** | CommandCodeBot (AI-assisted) |
| **Reviewers** | QA Lead, SDET, Product Owner (to be assigned) |
| **Date** | 2026-08-11 |
| **Related Document** | `Chapter_02_Prompt_Eng\Test plan_for_industry_standard\VWO_Test_Plan.md` |

### 1.1 Change History

| Version | Date | Author | Description |
|---|---|---|---|
| 0.1 | 2026-08-11 | CommandCodeBot | Initial draft from Chapter_01 VWO requirements |
| 1.0 | 2026-08-11 | CommandCodeBot | Full coverage (login + dashboard smoke) finalized |

---

## 2. Introduction

### 2.1 Purpose

This document defines the industry-level test cases for validating the **VWO login module** at `https://app.vwo.com/#/login` and performing **smoke validation of the post-login VWO dashboard**. It expands the coverage outlined in `VWO_Test_Plan.md` into concrete, executable test cases using the repository's standard table format.

### 2.2 Scope

In scope:

- Core authentication (valid / invalid / blank / malformed credentials)
- Field validation (on-blur, email format, password length & complexity)
- Authentication error handling & rate limiting (3 failed attempts)
- Session management (1-hour timeout, Remember Me, logout invalidation)
- Password reset (email-based recovery, 1-hour reset token, new-password login)
- 2FA / MFA and enterprise SSO flows (where test accounts available)
- Registration / new-user flow (free-trial link, onboarding)
- Dashboard smoke (landing, key elements, logout, timeout redirect)
- UI/UX, responsive/mobile, accessibility, security, integration, compatibility (spot), error recovery

Out of scope:

- Full VWO product functionality (campaigns, experiments, reports, settings, billing)
- Load / stress / soak performance testing at scale
- Full penetration testing
- API contract testing beyond the authentication response codes specified in requirements

### 2.3 References

| ID | Document | Location |
|---|---|---|
| R1 | VWO Login Dashboard — Test Cases with Anti-Hallucination Rules | `Chapter_01_LLM Basics\Use_the_Anti_Hallucination_Rule.md` |
| R2 | VWO Login Dashboard — Test Cases (No Anti-Hallucination Rules) | `Chapter_01_LLM Basics\Without_Use_the_Anti_Hallucination_Rule.md` |
| R3 | Product Requirements Document (PRD) VWO.com | `Chapter_01_LLM Basics\Product Requirements Document (PRD) VWO.com.pdf` |
| R4 | Test Plan Template (reference format) | `Chapter_01_LLM Basics\Test Plan - Template.docx.pdf` |
| R5 | RICE POT Template | `Chapter_02_Prompt_Eng\01_RICE_POT_Template.md` |
| R6 | VWO Test Plan (parent document) | `Chapter_02_Prompt_Eng\Test plan_for_industry_standard\VWO_Test_Plan.md` |

### 2.4 Requirements Source Note

The PRD (R3) is a PDF that could not be text-extracted during authoring. The verified requirements baseline is the set of **user-provided facts** in R1 and the **coverage areas** in R2. Where a requirement detail is available only in the PRD and not in R1/R2, it is marked **TBC (to be confirmed)** — no values are invented.

---

## 3. Test Case Conventions

### 3.1 TC-ID Naming

| Prefix | Suite |
|---|---|
| `VWO-LOGIN-*` | Login & Authentication |
| `VWO-VALID-*` | Field Validation & Password Rules |
| `VWO-ERR-*` / `VWO-RATE-*` | Error Handling & Rate Limiting |
| `VWO-SESSION-*` | Session Management & Remember Me |
| `VWO-PWD-*` | Password Reset |
| `VWO-MFA-*` | 2FA / MFA |
| `VWO-SSO-*` | Enterprise SSO |
| `VWO-REG-*` | Registration / New User |
| `VWO-DASH-*` | Dashboard Smoke |
| `VWO-UI-*` | UI / UX |
| `VWO-MOB-*` | Responsive / Mobile |
| `VWO-A11Y-*` | Accessibility |
| `VWO-SEC-*` | Security |
| `VWO-INT-*` | Integration |
| `VWO-PERF-*` | Performance (spot) |
| `VWO-COMP-*` | Compatibility |
| `VWO-RECOV-*` | Error Recovery |
| `SMK-*` | Smoke Suite |

### 3.2 Priority Definitions

| Priority | Meaning |
|---|---|
| **P0** | Critical — blocks release if failed; highest execution priority |
| **P1** | High — core functionality; must pass before sign-off |
| **P2** | Medium — important but non-blocking |

### 3.3 Table Format

All suites use the house format:

`| TC ID | Scenario | Preconditions / Test Data | Steps | Expected Result | Priority |`

---

## 4. Test Data & Preconditions

| Data Item | Value | Source / Status |
|---|---|---|
| Valid email | `vmtester@yopmail.com` | R1 (user-supplied) |
| Valid password | `Pass@1234` | R1 (user-supplied) |
| Email error message | **"Email or password is required"** | R1 |
| Email format example | `example@gmail.com` | R1 |
| Invalid email formats | `vmtester`, `vmtester@`, `vmtesteryopmail.com`, `abc` | R1 |
| Password length | Minimum **4**, maximum **10** characters | R1 |
| Password complexity | Lowercase + uppercase + special characters | R1 |
| Valid complexity sample | `Pass@1234` | R1 |
| Rate limiting | Triggered after **3 failed attempts** | R1 |
| Session timeout | **1 hour** | R1 |
| Reset-token validity | **1 hour** | R1 |
| Post-reset navigation | User lands on **Login page** | R1 |
| Auth API response | **HTTP 200** on success | R1 |
| Password-reset mailbox | `vmtester@yopmail.com` (yopmail) | R1 |
| 2FA test account | `<to be provided>` | TBC |
| SSO test account | `<to be provided>` | TBC |
| External staging URL | `<external staging URL — to be provided by user>` | RICE POT Parameters |
| External username / password | `<to be provided by user>` | RICE POT Parameters |

> **Policy:** Credentials are never hardcoded into automation; they are read from the gitignored `config.properties`. Tests skip with `SkipException` when values are placeholders.

---

## 5. Test Case Suites

### A. Login & Authentication

| TC ID | Scenario | Preconditions / Test Data | Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| VWO-LOGIN-001 | Verify login with valid credentials | Valid account: `vmtester@yopmail.com` / `Pass@1234` | 1. Open login page 2. Enter email 3. Enter password 4. Click **Login** | User authenticated and lands on the main VWO dashboard | P0 |
| VWO-LOGIN-002 | Verify login with invalid email | Invalid email + `Pass@1234` | 1. Enter invalid email 2. Enter password 3. Click **Login** | Authentication fails; appropriate error message displayed | P0 |
| VWO-LOGIN-003 | Verify login with invalid password | `vmtester@yopmail.com` + wrong password | 1. Enter email 2. Enter wrong password 3. Click **Login** | Authentication fails; clear actionable error displayed | P0 |
| VWO-LOGIN-004 | Verify login with both invalid credentials | Invalid email + invalid password | 1. Enter invalid email 2. Enter invalid password 3. Click **Login** | Authentication fails; actionable error displayed | P0 |
| VWO-LOGIN-005 | Verify login with blank email | Blank email + valid password | 1. Leave email blank 2. Enter password 3. Click **Login** | Error: **"Email or password is required"** | P0 |
| VWO-LOGIN-006 | Verify login with blank password | Valid email + blank password | 1. Enter email 2. Leave password blank 3. Click **Login** | Error: **"Email or password is required"** | P0 |
| VWO-LOGIN-007 | Verify login with both fields blank | No input | 1. Leave both fields blank 2. Click **Login** | Required-field validation message displayed | P0 |
| VWO-LOGIN-008 | Verify valid email formats accepted | `vmtester@yopmail.com`, `example@gmail.com` | 1. Enter valid email 2. Move focus away | Valid email formats accepted | P1 |
| VWO-LOGIN-009 | Verify invalid email format rejected | `vmtester`, `abc`, `abc@`, `@gmail.com` | 1. Enter invalid format 2. Move focus away | Email format validation triggered | P0 |
| VWO-LOGIN-010 | Verify leading/trailing spaces in email | Email with leading/trailing spaces | 1. Enter spaced email 2. Submit | System handles spaces per validation rules; no incorrect authentication | P1 |
| VWO-LOGIN-011 | Verify password is masked | Password input | 1. Enter password 2. Observe field | Password characters are hidden/masked | P0 |
| VWO-LOGIN-012 | Verify password case sensitivity | Correct email + changed-case password | 1. Enter email 2. Enter wrong-case password 3. Click **Login** | Authentication fails if password case is incorrect | P1 |
| VWO-LOGIN-013 | Verify Login button behavior | Valid credentials | 1. Enter credentials 2. Observe Login button | Login button allows submission | P0 |
| VWO-LOGIN-014 | Verify duplicate submission protection | Valid credentials | 1. Rapidly click **Login** multiple times | Only one authentication request processed appropriately | P1 |
| VWO-LOGIN-015 | Verify loading state during login | Valid credentials | 1. Click **Login** 2. Observe state | Clear loading/progress indication while authenticating | P1 |

### B. Field Validation & Password Rules

| TC ID | Scenario | Preconditions / Test Data | Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| VWO-VALID-001 | Verify validation occurs on blur | Invalid input | 1. Enter invalid value 2. Move focus to another field | Validation triggered when field loses focus | P0 |
| VWO-VALID-002 | Verify password minimum length (4) | 4-character password | 1. Enter 4-char password 2. Trigger validation | Password satisfies minimum length of 4 | P0 |
| VWO-VALID-003 | Verify password maximum length (10) | 10-character password | 1. Enter 10-char password 2. Trigger validation | Password satisfies maximum length of 10 | P0 |
| VWO-VALID-004 | Verify password below minimum (3) | 3-character password | 1. Enter 3-char password 2. Trigger validation | Password rejected — below minimum of 4 | P0 |
| VWO-VALID-005 | Verify password above maximum (11) | 11-character password | 1. Enter 11-char password 2. Trigger validation | Password rejected — exceeds maximum of 10 | P0 |
| VWO-VALID-006 | Verify password contains lowercase | Lowercase-containing password | 1. Enter password with lowercase 2. Trigger validation | Lowercase requirement satisfied | P0 |
| VWO-VALID-007 | Verify password contains uppercase | Uppercase-containing password | 1. Enter password with uppercase 2. Trigger validation | Uppercase requirement satisfied | P0 |
| VWO-VALID-008 | Verify password contains special char | Special-char-containing password | 1. Enter password with special char 2. Trigger validation | Special-character requirement satisfied | P0 |
| VWO-VALID-009 | Verify password with all required types | `Pass@1234` | 1. Enter `Pass@1234` 2. Trigger validation | All character requirements satisfied | P0 |
| VWO-VALID-010 | Verify password without lowercase | Uppercase + special + numbers | 1. Enter password without lowercase 2. Trigger validation | Complexity requirement not satisfied | P0 |
| VWO-VALID-011 | Verify password without uppercase | Lowercase + special + numbers | 1. Enter password without uppercase 2. Trigger validation | Complexity requirement not satisfied | P0 |
| VWO-VALID-012 | Verify password without special char | Letters + numbers only | 1. Enter password without special char 2. Trigger validation | Complexity requirement not satisfied | P0 |

### C. Error Handling & Rate Limiting

| TC ID | Scenario | Preconditions / Test Data | Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| VWO-ERR-001 | Verify failed authentication error message | Invalid credentials | 1. Enter invalid credentials 2. Click **Login** | Clear, actionable authentication error displayed | P0 |
| VWO-ERR-002 | Verify network interruption during login | Interrupted connection | 1. Initiate login 2. Interrupt network | Appropriate failure/retry feedback shown | P1 |
| VWO-ERR-003 | Verify authentication service unavailable | Service down | 1. Attempt login while service unavailable | Graceful error, no broken page | P0 |
| VWO-ERR-004 | Verify login request timeout | Slow/unresponsive backend | 1. Submit login 2. Wait for timeout | Appropriate timeout message displayed | P1 |
| VWO-ERR-005 | Verify password reset service unavailable | Reset service down | 1. Initiate password reset while unavailable | Appropriate recovery/support message | P1 |
| VWO-ERR-006 | Verify successful recovery indication | Recovered from error | 1. Retry after error 2. Complete login | Clear indication of successful login | P1 |
| VWO-RATE-001 | Verify rate limiting after 3 failed attempts | Invalid credentials (disposable account) | 1. Attempt login with invalid creds 3 times | Rate limiting triggered after 3 failed attempts (behavior per R1; exact response TBC) | P0 |
| VWO-RATE-002 | Verify 4th attempt after rate limit | 3 failed attempts recorded | 1. Attempt login a 4th time | Subsequent attempt handled per defined rate-limit behavior (TBC) | P0 |
| VWO-RATE-003 | Verify rate-limit response | 3 failed attempts | 1. Trigger rate limit 2. Observe response | Rate-limit response per specification (R1 value `3` preserved; exact semantics TBC) | P0 |
| VWO-RATE-004 | Verify account-enumeration protection | Valid email + wrong password vs invalid email | 1. Compare error responses | Errors do not reveal whether an account exists | P1 |

### D. Session Management & Remember Me

| TC ID | Scenario | Preconditions / Test Data | Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| VWO-SESSION-001 | Verify Remember Me checkbox available | Login page open | 1. Observe login form | Remember Me option displayed | P1 |
| VWO-SESSION-002 | Verify Remember Me persistence | Valid credentials | 1. Select Remember Me 2. Login 3. Close/reopen browser | Session/credentials persist per persistent-login requirement | P1 |
| VWO-SESSION-003 | Verify no persistence without Remember Me | Valid credentials | 1. Login without selecting checkbox 2. Close/reopen browser | Session does not persist beyond configured behavior | P1 |
| VWO-SESSION-004 | Verify session timeout (1 hour) | Valid credentials | 1. Login 2. Remain inactive for 1 hour | Session times out after 1 hour | P0 |
| VWO-SESSION-005 | Verify protected access after session expiry | Expired session | 1. Allow session to expire 2. Access dashboard | Redirected to login/re-authentication | P0 |
| VWO-SESSION-006 | Verify logout invalidates session | Authenticated session | 1. Login 2. Logout 3. Use browser **Back** | Protected dashboard inaccessible with invalidated session | P0 |
| VWO-SESSION-007 | Verify session token security | Authenticated session | 1. Login 2. Inspect session behavior | Secure session token generated and managed securely | P0 |
| VWO-SESSION-008 | Verify simultaneous sessions | Multiple sessions | 1. Login from multiple supported sessions | Behavior follows session policy; no unauthorized access | P1 |

### E. Password Reset

| TC ID | Scenario | Preconditions / Test Data | Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| VWO-PWD-001 | Verify Forgot Password option | Login page open | 1. Observe recovery option | **forgot password** option available | P0 |
| VWO-PWD-002 | Verify navigation to Forgot Password flow | Login page open | 1. Click **forgot password** | User taken to password reset flow | P0 |
| VWO-PWD-003 | Verify reset with registered email | `vmtester@yopmail.com` | 1. Click **forgot password** 2. Enter registered email 3. Submit | Password recovery initiated | P0 |
| VWO-PWD-004 | Verify reset with unregistered email | Unregistered email | 1. Enter unregistered email 2. Submit | Appropriate secure response displayed | P1 |
| VWO-PWD-005 | Verify reset with invalid email format | Invalid email format | 1. Enter invalid format 2. Submit | Email validation message displayed | P1 |
| VWO-PWD-006 | Verify reset with blank email | Blank field | 1. Submit blank email field | Required-field validation displayed | P1 |
| VWO-PWD-007 | Verify password reset email sent | Registered email | 1. Request reset | Reset email sent through recovery mechanism | P0 |
| VWO-PWD-008 | Verify valid reset token | Valid token (1h validity) | 1. Open reset link 2. Use within 1 hour | Valid token allows password reset | P0 |
| VWO-PWD-009 | Verify expired reset token | Expired token | 1. Use token after 1 hour | Reset rejected; token no longer valid | P0 |
| VWO-PWD-010 | Verify invalid reset token | Tampered/invalid token | 1. Modify/use invalid token | Reset rejected securely | P0 |
| VWO-PWD-011 | Verify reset token reuse | Previously used token | 1. Reset password 2. Reuse old token | Token cannot be reused | P0 |
| VWO-PWD-012 | Verify weak password rejected at reset | Password violating complexity | 1. Enter weak password during reset | Password requirements/validation shown | P0 |
| VWO-PWD-013 | Verify strong password accepted at reset | Password satisfying complexity | 1. Enter compliant password 2. Complete reset | Password accepted | P1 |
| VWO-PWD-014 | Verify post-reset navigation & new-password login | Reset completed | 1. Land on Login page 2. Enter email + new password 3. Click **Login** | User lands on Login page; authentication succeeds with new password | P0 |
| VWO-PWD-015 | Verify old password invalidated | Reset completed | 1. Attempt login with old password | Old password no longer authenticates | P0 |

### F. 2FA / MFA

| TC ID | Scenario | Preconditions / Test Data | Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| VWO-MFA-001 | Verify optional 2FA flow | Account with 2FA enabled | 1. Login with 2FA-enabled account | 2FA verification step displayed | P0 |
| VWO-MFA-002 | Verify login with valid OTP | Valid OTP | 1. Enter credentials 2. Enter valid OTP | Authentication succeeds | P0 |
| VWO-MFA-003 | Verify login with invalid OTP | Invalid OTP | 1. Enter invalid OTP | Authentication fails with appropriate error | P0 |
| VWO-MFA-004 | Verify expired OTP | Expired OTP | 1. Enter expired OTP | OTP rejected | P1 |
| VWO-MFA-005 | Verify empty OTP submission | No OTP entered | 1. Submit without OTP | Validation message displayed | P1 |
| VWO-MFA-006 | Verify multiple invalid OTP attempts | Repeated invalid OTPs | 1. Enter invalid OTP repeatedly | Security controls/rate limiting applied | P0 |

### G. Enterprise SSO

| TC ID | Scenario | Preconditions / Test Data | Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| VWO-SSO-001 | Verify SSO option | SSO-enabled organization | 1. Open login page | SSO option available | P1 |
| VWO-SSO-002 | Verify successful SAML authentication | Valid SAML IdP | 1. Initiate SAML SSO 2. Authenticate successfully | User logged into VWO | P0 |
| VWO-SSO-003 | Verify failed SAML authentication | Failing IdP | 1. Initiate SSO 2. Fail authentication | Appropriate error received | P0 |
| VWO-SSO-004 | Verify OAuth authentication | Supported OAuth provider | 1. Initiate OAuth flow | User authenticated successfully | P1 |
| VWO-SSO-005 | Verify cancel SSO authentication | SSO in progress | 1. Start SSO 2. Cancel IdP flow | User returns safely to login flow | P1 |
| VWO-SSO-006 | Verify unauthorized SSO user | Non-authorized org user | 1. Authenticate via SSO as unauthorized user | Access denied appropriately | P0 |

### H. Registration / New User

| TC ID | Scenario | Preconditions / Test Data | Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| VWO-REG-001 | Verify free trial link | Login page open | 1. Click free trial/signup link | Registration page opens | P1 |
| VWO-REG-002 | Verify registration link accessibility | Login page open | 1. Navigate using keyboard | Link reachable and activatable via keyboard | P1 |
| VWO-REG-003 | Verify new-user onboarding | Registration completed | 1. Complete registration | Guided introduction/onboarding presented | P1 |
| VWO-REG-004 | Verify login after registration | New account | 1. Register 2. Complete onboarding 3. Login | User reaches personalized dashboard | P0 |

### I. Dashboard Smoke

| TC ID | Scenario | Preconditions / Test Data | Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| VWO-DASH-001 | Verify dashboard landing after login | Valid credentials | 1. Login successfully | Redirected to main VWO dashboard | P0 |
| VWO-DASH-002 | Verify key dashboard elements render | Authenticated session | 1. Observe dashboard 2. Verify core widgets/navigation | Dashboard renders without layout breakage; core elements visible | P0 |
| VWO-DASH-003 | Verify logout from dashboard | Authenticated session | 1. Click logout 2. Verify redirect | Session invalidated; redirected to login; dashboard inaccessible via **Back** | P0 |
| VWO-DASH-004 | Verify session-timeout redirect from dashboard | Expired session | 1. Allow 1-hour timeout 2. Access dashboard | Redirected to login / re-authentication required | P0 |
| VWO-DASH-005 | Verify dashboard responsiveness | Authenticated session | 1. Resize browser / open on mobile | Dashboard remains usable without breakage | P1 |

### J. UI / UX

| TC ID | Scenario | Preconditions / Test Data | Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| VWO-UI-001 | Verify VWO branding | Login page open | 1. Observe page | VWO branding displayed consistently | P1 |
| VWO-UI-002 | Verify login page layout | Login page open | 1. Observe layout | Login form properly aligned and visually consistent | P1 |
| VWO-UI-003 | Verify email field label | Login page open | 1. Observe email field | Label clearly associated with email input | P1 |
| VWO-UI-004 | Verify password field label | Login page open | 1. Observe password field | Label clearly associated with password input | P1 |
| VWO-UI-005 | Verify clickable labels | Login page open | 1. Click field label | Clicking label focuses corresponding field | P1 |
| VWO-UI-006 | Verify auto-focus | Login page open | 1. Open login page | First input field receives focus automatically | P1 |
| VWO-UI-007 | Verify loading state | Valid credentials | 1. Submit login | Clear loading feedback appears | P1 |
| VWO-UI-008 | Verify error message placement | Invalid credentials | 1. Submit invalid credentials | Error appears near/relevant to affected field or auth area | P1 |
| VWO-UI-009 | Verify error message clarity | Trigger auth failure | 1. Trigger failure 2. Read message | Error is understandable and actionable | P1 |
| VWO-UI-010 | Verify Light Mode | Login page open | 1. Open in Light Mode | Interface renders correctly | P1 |
| VWO-UI-011 | Verify Dark Mode | Login page open | 1. Switch to Dark Mode | Interface renders correctly; text/controls readable | P1 |
| VWO-UI-012 | Verify theme persistence | Theme changed | 1. Change theme 2. Refresh/reopen | Theme persists per product requirement | P2 |

### K. Responsive / Mobile

| TC ID | Scenario | Preconditions / Test Data | Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| VWO-MOB-001 | Verify login page on mobile | Mobile viewport | 1. Open login page on mobile | Page renders without layout breakage | P0 |
| VWO-MOB-002 | Verify portrait orientation | Portrait viewport | 1. Open page in portrait | Login controls remain usable | P1 |
| VWO-MOB-003 | Verify landscape orientation | Landscape viewport | 1. Open page in landscape | Login controls remain usable | P1 |
| VWO-MOB-004 | Verify touch controls | Touch device | 1. Interact with buttons/links | Buttons/links easy to tap | P1 |
| VWO-MOB-005 | Verify email keyboard | Email field focused | 1. Focus email field | Appropriate email keyboard presented | P1 |
| VWO-MOB-006 | Verify password keyboard | Password field focused | 1. Focus password field | Appropriate keyboard behavior provided | P1 |
| VWO-MOB-007 | Verify no horizontal scrolling | Mobile viewport | 1. Open login page on mobile | No unwanted horizontal scrolling | P1 |
| VWO-MOB-008 | Verify mobile validation | Invalid values | 1. Enter invalid values on mobile | Validation works correctly on mobile | P1 |

### L. Accessibility

| TC ID | Scenario | Preconditions / Test Data | Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| VWO-A11Y-001 | Verify keyboard-only navigation | No mouse | 1. Navigate login form with keyboard | All controls reachable | P0 |
| VWO-A11Y-002 | Verify keyboard tab order | No mouse | 1. Tab through fields | Focus follows logical sequence | P0 |
| VWO-A11Y-003 | Verify Login activation via keyboard | No mouse | 1. Focus Login 2. Activate with keyboard | Login can be triggered via keyboard | P1 |
| VWO-A11Y-004 | Verify Forgot Password activation via keyboard | No mouse | 1. Focus link 2. Activate with keyboard | Link can be activated via keyboard | P1 |
| VWO-A11Y-005 | Verify screen-reader labels | Screen reader active | 1. Read login form | Inputs/buttons have meaningful accessible labels | P0 |
| VWO-A11Y-006 | Verify error accessibility | Screen reader active | 1. Trigger validation error | Screen reader can identify validation errors | P0 |
| VWO-A11Y-007 | Verify focus visibility | Keyboard navigation | 1. Tab through form | Focus indicator clearly visible | P1 |
| VWO-A11Y-008 | Verify high contrast mode | High-contrast enabled | 1. Enable high contrast 2. Observe | Text and controls remain distinguishable | P1 |
| VWO-A11Y-009 | Verify WCAG 2.1 AA compliance | Login page | 1. Audit login interface | Meets applicable WCAG 2.1 AA requirements | P0 |

### M. Security (Login-Scoped)

| TC ID | Scenario | Preconditions / Test Data | Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| VWO-SEC-001 | Verify HTTPS enforcement | Login environment | 1. Access login page 2. Inspect protocol | Login communication only over HTTPS | P0 |
| VWO-SEC-002 | Verify password never in URL | Login submission | 1. Submit login 2. Inspect URL/query string | Password never appears in URL/query string | P0 |
| VWO-SEC-003 | Verify password not stored in browser storage | Login submission | 1. Login 2. Inspect storage | Password not stored insecurely | P0 |
| VWO-SEC-004 | Verify password transmitted securely | Login submission | 1. Submit login 2. Inspect traffic | Password protected during transmission | P0 |
| VWO-SEC-005 | Verify brute-force protection | Invalid credentials | 1. Perform repeated failed attempts | Repeated failures trigger throttling/rate limiting | P0 |
| VWO-SEC-006 | Verify account-enumeration protection | Invalid vs valid email | 1. Compare error responses | Errors do not expose account existence | P1 |
| VWO-SEC-007 | Verify SQL injection in email field | `' OR 1=1 --` | 1. Enter malicious input 2. Submit | Malicious input rejected/handled safely | P0 |
| VWO-SEC-008 | Verify XSS in email field | `<script>alert(1)</script>` | 1. Enter script payload 2. Submit | Script payload not executed | P0 |
| VWO-SEC-009 | Verify XSS in password field | `<script>alert(1)</script>` | 1. Enter script payload 2. Submit | Script payload not executed | P0 |
| VWO-SEC-010 | Verify session fixation protection | Fresh session | 1. Login 2. Inspect session | Session cannot be fixed/hijacked by attacker | P0 |
| VWO-SEC-011 | Verify session token manipulation | Modified token | 1. Modify/invalid token 2. Access protected resource | Modified token cannot access protected resources | P0 |
| VWO-SEC-012 | Verify session hijacking protection | Stolen session attempt | 1. Attempt unauthorized session access | Unauthorized session access prevented | P0 |
| VWO-SEC-013 | Verify logout session invalidation | Authenticated session | 1. Login 2. Logout 3. Access protected page | Issued session cannot access protected pages after logout | P0 |
| VWO-SEC-014 | Verify password reset token manipulation | Tampered token | 1. Modify reset token 2. Use it | Modified token rejected | P0 |
| VWO-SEC-015 | Verify password reset token reuse | Used token | 1. Reset password 2. Reuse token | Token becomes invalid after successful use | P0 |
| VWO-SEC-016 | Verify CSRF protection | State-changing request | 1. Forge request 2. Submit | Unauthorized state-changing requests rejected | P0 |
| VWO-SEC-017 | Verify sensitive info in errors | Trigger errors | 1. Trigger various failures 2. Inspect messages | Errors do not expose credentials, tokens, stack traces | P0 |
| VWO-SEC-018 | Verify rate-limit bypass resistance | Repeated requests | 1. Attempt rate-limit bypass patterns | Rate limiting cannot easily be bypassed | P0 |

### N. Integration

| TC ID | Scenario | Preconditions / Test Data | Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| VWO-INT-001 | Verify login → VWO core platform | Valid credentials | 1. Login successfully | Successful authentication redirects to main VWO dashboard | P0 |
| VWO-INT-002 | Verify personalized dashboard | Authenticated session | 1. Observe post-login dashboard | Appropriate personalized dashboard shown | P1 |
| VWO-INT-003 | Verify previous session context | Prior activity | 1. Login 2. Observe context | Relevant recent activity/context preserved | P1 |
| VWO-INT-004 | Verify login success analytics | Valid login | 1. Login 2. Check analytics | Successful login event tracked | P1 |
| VWO-INT-005 | Verify login failure analytics | Failed login | 1. Attempt failed login 2. Check analytics | Failed authentication event tracked | P1 |

### O. Performance (Spot)

| TC ID | Scenario | Preconditions / Test Data | Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| VWO-PERF-001 | Verify login page load time | Standard connection | 1. Open login page 2. Measure load | Page loads within **2 seconds** (per R2) | P0 |
| VWO-PERF-002 | Verify login response time | Valid credentials | 1. Submit login 2. Measure response | Authentication response within agreed SLA (TBC) | P1 |

### P. Compatibility

| TC ID | Scenario | Preconditions / Test Data | Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| VWO-COMP-001 | Verify Chrome desktop | Chrome browser | 1. Execute login flow in Chrome | Login works correctly | P0 |
| VWO-COMP-002 | Verify Edge desktop | Edge browser | 1. Execute login flow in Edge | Login works correctly | P1 |
| VWO-COMP-003 | Verify Firefox desktop | Firefox browser | 1. Execute login flow in Firefox | Login works correctly | P1 |
| VWO-COMP-004 | Verify Safari desktop | Safari browser | 1. Execute login flow in Safari | Login works correctly | P1 |
| VWO-COMP-005 | Verify Chrome Android | Android device | 1. Execute login flow on Chrome Android | Login works correctly | P1 |
| VWO-COMP-006 | Verify Safari iOS | iOS device | 1. Execute login flow on Safari iOS | Login works correctly | P1 |
| VWO-COMP-007 | Verify different desktop resolutions | Various resolutions | 1. Resize to multiple resolutions | UI remains responsive | P1 |
| VWO-COMP-008 | Verify different mobile resolutions | Various mobile resolutions | 1. Resize to mobile sizes | UI remains responsive | P1 |

### Q. Error Recovery

| TC ID | Scenario | Preconditions / Test Data | Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| VWO-RECOV-001 | Verify invalid-credential recovery | Invalid credentials | 1. Fail login 2. Enter valid credentials | Clear failure message then successful login | P0 |
| VWO-RECOV-002 | Verify network interruption recovery | Interrupted connection | 1. Interrupt during login 2. Restore 3. Retry | Appropriate failure/retry feedback; recovery works | P1 |
| VWO-RECOV-003 | Verify auth service outage recovery | Service unavailable | 1. Attempt during outage 2. Retry after restore | Graceful error; recovery after service returns | P0 |
| VWO-RECOV-004 | Verify login request timeout recovery | Slow backend | 1. Trigger timeout 2. Retry | Timeout message; retry succeeds when backend recovers | P1 |
| VWO-RECOV-005 | Verify reset service outage recovery | Reset service down | 1. Attempt reset during outage 2. Retry | Recovery/support message; reset works after restore | P1 |
| VWO-RECOV-006 | Verify successful recovery confirmation | Recovery completed | 1. Recover from error 2. Complete login | Clear confirmation of successful login | P1 |

### R. Smoke Suite (Daily)

| Smoke ID | Test Case |
|---|---|
| SMK-01 | Login page loads successfully |
| SMK-02 | Email and password fields are displayed |
| SMK-03 | Valid email + password login |
| SMK-04 | Invalid password validation |
| SMK-05 | Blank email validation |
| SMK-06 | Blank password validation |
| SMK-07 | Invalid email format validation |
| SMK-08 | Forgot Password flow |
| SMK-09 | Remember Me option |
| SMK-10 | Login loading state |
| SMK-11 | Successful login redirects to VWO dashboard |
| SMK-12 | Logout invalidates session |
| SMK-13 | Session timeout redirects to login |
| SMK-14 | Login page works on mobile |
| SMK-15 | Keyboard navigation works |
| SMK-16 | Light/Dark Mode works |
| SMK-17 | HTTPS is enforced |
| SMK-18 | Login page loads within 2 seconds |
| SMK-19 | 2FA login works when enabled |
| SMK-20 | SSO login works for enterprise account |

---

## 6. Traceability Matrix

| Suite | Test Cases | Source Reference (R1/R2) | Parent Plan Suite |
|---|---|---|---|
| A. Login & Authentication | `VWO-LOGIN-001..015` | R1 AUTH-001..012; R2 §1 | §10 Functional — Login & Validation |
| B. Field Validation & Password Rules | `VWO-VALID-001..012` | R1 AUTH-008..012, AUTH-013..023 | §10 Functional — Login & Validation |
| C. Error Handling & Rate Limiting | `VWO-ERR-001..006`, `VWO-RATE-001..004` | R1 AUTH-016, AUTH-024..027; R2 §14 | §10 Security / Error Recovery |
| D. Session Management & Remember Me | `VWO-SESSION-001..008` | R1 AUTH-015, AUTH-028..030; R2 §2 | §10 Session & Remember Me |
| E. Password Reset | `VWO-PWD-001..015` | R1 AUTH-017..023, AUTH-031..040; R2 §3 | §10 Password Management |
| F. 2FA / MFA | `VWO-MFA-001..006` | R2 §4 | §10 2FA / MFA |
| G. Enterprise SSO | `VWO-SSO-001..006` | R2 §5 | §10 Enterprise SSO |
| H. Registration / New User | `VWO-REG-001..004` | R2 §6 | §10 Registration / New User |
| I. Dashboard Smoke | `VWO-DASH-001..005` | R1 "main VWO dashboard"; R2 VWO-INT-001/002 | §10 Dashboard Smoke |
| J. UI / UX | `VWO-UI-001..012` | R2 §7 | §10 UI / UX |
| K. Responsive / Mobile | `VWO-MOB-001..008` | R2 §8 | §10 Responsive / Mobile |
| L. Accessibility | `VWO-A11Y-001..009` | R2 §9 | §10 Accessibility |
| M. Security | `VWO-SEC-001..018` | R1 AUTH-014, AUTH-016; R2 §10 | §10 Security |
| N. Integration | `VWO-INT-001..005` | R2 §12 | §10 Integration |
| O. Performance (Spot) | `VWO-PERF-001..002` | R2 §11 | §10 Performance (spot) |
| P. Compatibility | `VWO-COMP-001..008` | R2 §13 | §10 Compatibility |
| Q. Error Recovery | `VWO-RECOV-001..006` | R2 §14 | §10 Error Recovery |
| R. Smoke Suite | `SMK-01..20` | R2 §15 | §10 Smoke |

---

## 7. Execution Notes

### 7.1 Automation Mapping

Per `VWO_Test_Plan.md` §12 (RICEPOT framework):

- **Automate (P0):** `VWO-LOGIN-001..015`, `VWO-VALID-001..012`, `VWO-RATE-001..003`, `VWO-SESSION-004..007`, `VWO-PWD-003,008..015`, `VWO-DASH-001..005`, `SMK-03..13` — mapped to `com.vwo.pages.VwoLoginPage` / `VwoDashboardPage` Page Objects and `VwoLoginValidTest` / `VwoLoginInvalidTest` / `VwoDashboardSmokeTest` TestNG classes.
- **Automate (P1, key paths):** `VWO-SESSION-002..003,008`, `VWO-SSO-002`, `VWO-RECOV-001..004` (where creds available).
- **Manual-first (P1/P2):** `VWO-UI-*`, `VWO-MOB-*`, `VWO-A11Y-*`, `VWO-COMP-*`, exploratory.
- **Manual / limited:** `VWO-PERF-*` (spot timing), `VWO-SEC-*` (some require tooling — DevTools/OWASP ZAP).

### 7.2 Rate-Limit Sequencing Warning

`VWO-RATE-001..004` and `VWO-SEC-005/018` must run against a **disposable test account** and be sequenced last in any given browser session — after 3 failed attempts the account locks per R1. Never run these before `VWO-LOGIN-001`/`VWO-DASH-001` on the shared valid account.

### 7.3 TBC (To Be Confirmed) Items

| Item | Where | Owner |
|---|---|---|
| Exact rate-limit response semantics (R1 value `3` preserved) | VWO-RATE-003 | Product |
| Authentication API endpoints | (not invented) | Product |
| Performance SLA exact value (load ≤ 2s per R2 is baseline) | VWO-PERF-002 | Product |
| 2FA test account availability | VWO-MFA-001..006 | User / Product |
| SSO test account availability | VWO-SSO-001..006 | User / Product |
| External staging URL + external username/password | All suites (test data) | User |

---

*End of test cases — Version 1.0*
