Role -> You are a Senior QA tester with 15 years of experience, You have a very good understanding of IT. You need to Create industry level Test Plan for app.vwo.com using RICEPOT framework.

I -> Instructions

- Generate a Complete industry level Test Plan the standard of enterprise level standards.
- [Critical] Structure the test plan following enterprise/IEEE 829 standards: document control, introduction, strategy, scope, environments & test data, roles, schedule, deliverables, entry/exit criteria, coverage & traceability, defect management, risks, approvals.
- [Critical] Use the RICEPOT framework (Role, Instructions, Context, Example, Parameters, Output, Tone) to drive the test design.
- [Mandatory] Cover login and authentication flows (valid/invalid/blank credentials, field validation, error handling, rate limiting, session management, password reset, 2FA/MFA, SSO) plus dashboard smoke validation.
- [Mandatory] Trace every test case back to the PRD / provided requirements; do not invent requirements, error messages, endpoints, or exact values beyond what is provided.
- [Mandatory] Define an automation strategy aligned with the RICEPOT Selenium framework (PageFactory, xpath-only locators, WebDriverWait, no Thread.sleep, TestNG, credentials from gitignored config.properties).
- [Output] Provide only the test plan document — no explanations or additional content.

C -> Context

Application under test: https://app.vwo.com/#/login — VWO login page with email/password fields, Login button, forgot password, remember me, 2FA/SSO options. Successful authentication transitions the user to the main VWO dashboard. PRD: Attached (Product Requirements Document (PRD) VWO.com.pdf). Requirements baseline also in Chapter_01_LLM Basics VWO test-case documents.

**E -> Example**

Example test case format (house style):

| TC ID | Scenario | Preconditions / Test Data | Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| VWO-LOGIN-001 | Verify login with valid credentials | Valid account: vmtester@yopmail.com / Pass@1234 | 1. Open login page 2. Enter email 3. Enter password 4. Click Login | User authenticated and lands on the main VWO dashboard | P0 |

**P -> PARAMETERS**

with production level automation script expert with pin point accuracy and almost zero bad coding practice.

- I have external URLs, external staging URLs. I will give you the external username and password as well.
- Test credentials: vmtester@yopmail.com / Pass@1234 (password reset via yopmail).
- Password rules: minimum 4, maximum 10 characters, lowercase + uppercase + special characters.
- Rate limiting: 3 failed login attempts. Session timeout: 1 hour. Reset token validity: 1 hour.
- 2FA and SSO test accounts: to be provided.

O -> Output

Provide only:

- Industry level Test Plan using RICEPOT framework, in Markdown, saved as VWO_Test_Plan.md.

T -> Tone

Technical, precisely, enterprise-grade, code-one.
