## Prompt: Create the test cases for Phase 1: Core Authentication using these PRD, anti hallucination rules 



Below are the **Phase 1: Core Authentication** test cases created strictly from the PRD and the Anti-Hallucination Rules. The PRD defines Phase 1 as **secure login form implementation, basic validation/error handling, and password reset functionality**. 

## Verified Facts

* Authentication uses **email and password**. 
* Field validation should occur **on blur**. 
* Email format validation is required.
* Failed authentication attempts should produce **clear, actionable error messages**. 
* Password security requirements must be enforced. 
* Password reset requires **secure token generation**.
* Email-based password recovery is supported. 
* Successful authentication should transition the user to the **main VWO dashboard**. 
* Secure session handling and secure session-token management are required.  
* HTTPS is required for login communications. 
* Rate limiting is required to protect against brute-force attacks. 

## Missing / Unknown Information

Per the anti-hallucination rules, I will **not invent** the following:

* Exact email/password validation messages
* Exact password complexity rules
* Exact minimum/maximum password length
* Exact login button/field labels
* Exact password reset page layout
* Exact reset-token expiration duration
* Exact number of failed attempts before rate limiting
* Exact rate-limit response
* Exact session timeout value
* Exact API endpoints/status codes
* Exact test credentials
* Exact post-reset navigation behavior

Therefore, wherever these details are required, the expected result is stated only at the level supported by the PRD. The anti-hallucination rules explicitly require missing information to be reported rather than assumed. 

# Generated Output — Phase 1 Test Cases

### A. Secure Login Form

| TC ID    | Test Scenario                                                | Preconditions / Test Data                        | Steps                                                                               | Expected Result                                                                        | Priority |
| -------- | ------------------------------------------------------------ | ------------------------------------------------ | ----------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | -------- |
| AUTH-001 | Verify login form supports email and password authentication | Valid registered user credentials                | 1. Open VWO login page 2. Enter valid email 3. Enter valid password 4. Submit login | User is successfully authenticated and transitioned to the main VWO dashboard          | High     |
| AUTH-002 | Verify login with valid email and invalid password           | Registered email + invalid password              | 1. Enter registered email 2. Enter invalid password 3. Submit login                 | Authentication fails and a clear, actionable authentication error is displayed         | High     |
| AUTH-003 | Verify login with invalid/unregistered email and password    | Invalid/unregistered email + password            | 1. Enter invalid/unregistered email 2. Enter password 3. Submit login               | Authentication fails and a clear, actionable authentication error is displayed         | High     |
| AUTH-004 | Verify login when email is empty                             | Email empty, password provided                   | 1. Leave email empty 2. Enter password 3. Trigger field validation                  | Email field validation is performed and appropriate validation feedback is provided    | High     |
| AUTH-005 | Verify login when password is empty                          | Valid email, password empty                      | 1. Enter email 2. Leave password empty 3. Trigger field validation                  | Password field validation is performed and appropriate validation feedback is provided | High     |
| AUTH-006 | Verify login when both email and password are empty          | No input                                         | 1. Leave both fields empty 2. Trigger validation/login                              | Appropriate validation feedback is provided for the required authentication inputs     | High     |
| AUTH-007 | Verify email format validation                               | Invalid email format                             | 1. Enter invalid email format 2. Move focus away from email field                   | Email format validation is triggered on blur and provides validation feedback          | High     |
| AUTH-008 | Verify valid email format is accepted                        | Valid email format                               | 1. Enter valid email 2. Move focus away from email field                            | Email format validation does not reject the valid email format                         | Medium   |
| AUTH-009 | Verify validation occurs on blur                             | Invalid input                                    | 1. Enter invalid field value 2. Move focus to another field                         | Field validation is triggered when the field loses focus                               | High     |
| AUTH-010 | Verify failed authentication provides actionable feedback    | Invalid authentication credentials               | 1. Enter invalid credentials 2. Submit login                                        | Authentication failure is communicated using a clear, actionable error message         | High     |
| AUTH-011 | Verify password security requirements are enforced           | Password that does not meet defined requirements | 1. Enter a password that violates a password requirement 2. Trigger validation      | Password security requirements are enforced and the user receives appropriate feedback | High     |
| AUTH-012 | Verify password strength/requirement feedback                | Password input                                   | 1. Enter password 2. Observe password feedback                                      | Visual feedback is provided for password requirements and strength                     | Medium   |
| AUTH-013 | Verify loading feedback during authentication processing     | Valid/invalid credentials                        | 1. Submit login 2. Observe authentication processing state                          | A clear loading state/feedback is displayed during authentication processing           | Medium   |
| AUTH-014 | Verify secure login communication uses HTTPS                 | VWO login environment                            | 1. Access login page 2. Initiate login communication                                | Login communications use HTTPS/SSL/TLS encryption                                      | High     |
| AUTH-015 | Verify secure session handling after successful login        | Valid credentials                                | 1. Log in successfully 2. Observe authenticated session                             | Session is securely handled and secure session-token management is implemented         | High     |
| AUTH-016 | Verify brute-force protection/rate limiting                  | Repeated failed authentication attempts          | 1. Perform repeated failed login attempts                                           | Request throttling/rate limiting protects against brute-force attacks                  | High     |

### B. Password Reset

| TC ID    | Test Scenario                                                   | Preconditions / Test Data                             | Steps                                                                                      | Expected Result                                                                           | Priority |
| -------- | --------------------------------------------------------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------- | -------- |
| AUTH-017 | Verify Forgot Password flow is available                        | User is on login page                                 | 1. Open login page 2. Select the password recovery option                                  | User can access the password reset/recovery flow                                          | High     |
| AUTH-018 | Verify password reset supports email-based recovery             | Registered user email                                 | 1. Start password recovery 2. Provide registered email 3. Submit recovery request          | Email-based password recovery is initiated                                                | High     |
| AUTH-019 | Verify secure reset token generation                            | Valid password recovery request                       | 1. Initiate password reset 2. Complete the recovery request                                | A secure token is generated for password reset                                            | High     |
| AUTH-020 | Verify password reset enforces password requirements            | Password reset flow + password violating requirements | 1. Start password reset 2. Provide a password that does not satisfy requirements           | Password security requirements are enforced during password recovery                      | High     |
| AUTH-021 | Verify password reset with compliant password                   | Valid password reset flow + compliant password        | 1. Start password reset 2. Provide password meeting defined requirements 3. Complete reset | Password reset can proceed using a password satisfying the enforced security requirements | High     |
| AUTH-022 | Verify password recovery provides appropriate recovery feedback | Password recovery attempt                             | 1. Initiate recovery 2. Submit recovery information                                        | User receives appropriate feedback for the recovery process                               | Medium   |
| AUTH-023 | Verify password reset token is securely generated               | Password reset request                                | 1. Initiate password recovery 2. Observe reset-token generation                            | Reset token generation is secure                                                          | High     |

## Self-Validation Check

* **No API endpoints invented:** ✅
* **No HTTP status codes invented:** ✅
* **No exact error messages invented:** ✅
* **No password length/complexity values invented:** ✅
* **No token expiry duration invented:** ✅
* **No rate-limit threshold invented:** ✅
* **No UI controls invented beyond PRD-supported authentication/recovery functionality:** ✅
* **Phase 2/Phase 3-only functionality excluded:** ✅
* **Every test case is traceable to PRD requirements:** ✅
* **Missing details explicitly identified:** ✅

The test cases are therefore limited to what the supplied PRD actually specifies, following the rule that every assertion must be traceable to the provided input. 


### Prompt:
* Exact email/password validation messages: Email or password is reuired, valid format is ex:example@gmail.com.
* Exact password complexity rules: Pasword should contains 8 letters with small,capital, special charecters
* Exact minimum/maximum password length: Minimum 4, max:10
* Exact login button/field labels: Login button
* Exact password reset page layout: forgot password
* Exact reset-token expiration duration: 1hr
* Exact number of failed attempts before rate limiting: 3
* Exact rate-limit response: 3
* Exact session timeout value: 1 hr
* Exact API endpoints/status codes: 200
* Exact test credentials: vmtester@yopmail.com, Pass@1234
* Exact post-reset navigation behavior: Login page should land

Got it. I’ll incorporate these exact details into the **Phase 1: Core Authentication** test cases. I’ll preserve the supplied values exactly and will not invent an API endpoint where only the status code `200` was provided.

## Verified Facts

The following details are now explicitly provided by you:

* **Email required message:** `Email or password is required`
* **Email format example:** `example@gmail.com`
* **Password rule:** Password should contain small letters, capital letters, and special characters.
* **Password length:** Minimum 4, maximum 10 characters.
* **Login button:** `Login`
* **Forgot password:** `forgot password`
* **Reset token expiry:** 1 hour
* **Failed attempts before rate limiting:** 3
* **Rate-limit response:** `3` — preserved exactly as provided.
* **Session timeout:** 1 hour
* **API response/status:** `200`
* **Test email:** `vmtester@yopmail.com`
* **Test password:** `Pass@1234`
* **After password reset:** User should land on the Login page.

These additions are now user-provided information, so they can be used under the anti-hallucination rules. 

# Phase 1 – Core Authentication Test Cases

### A. Login – Functional & Validation

| TC ID    | Test Scenario                                      | Test Data                                           | Steps                                                                      | Expected Result                                                                 | Priority |
| -------- | -------------------------------------------------- | --------------------------------------------------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------------- | -------- |
| AUTH-001 | Verify login with valid credentials                | Email: `vmtester@yopmail.com` Password: `Pass@1234` | 1. Open login page 2. Enter email 3. Enter password 4. Click **Login**     | User should be successfully authenticated and land on the VWO dashboard         | High     |
| AUTH-002 | Verify Login button is available                   | —                                                   | 1. Open login page 2. Observe login form                                   | **Login** button should be displayed                                            | High     |
| AUTH-003 | Verify login with valid email and invalid password | Valid email + invalid password                      | 1. Enter valid email 2. Enter invalid password 3. Click **Login**          | Authentication should fail and an appropriate error message should be displayed | High     |
| AUTH-004 | Verify login with invalid email and valid password | Invalid email + `Pass@1234`                         | 1. Enter invalid email 2. Enter valid password 3. Click **Login**          | Authentication should fail and an appropriate error message should be displayed | High     |
| AUTH-005 | Verify login with both fields blank                | Blank email + blank password                        | 1. Leave email blank 2. Leave password blank 3. Click **Login**            | Error message should be displayed: **"Email or password is required"**          | High     |
| AUTH-006 | Verify login with email blank                      | Blank email + valid password                        | 1. Leave email blank 2. Enter `Pass@1234` 3. Click **Login**               | Error message should be displayed: **"Email or password is required"**          | High     |
| AUTH-007 | Verify login with password blank                   | Valid email + blank password                        | 1. Enter `vmtester@yopmail.com` 2. Leave password blank 3. Click **Login** | Error message should be displayed: **"Email or password is required"**          | High     |
| AUTH-008 | Verify valid email format                          | `vmtester@yopmail.com`                              | 1. Enter valid email 2. Move focus away from email field                   | Email should be accepted as a valid email format                                | High     |
| AUTH-009 | Verify invalid email format                        | `vmtester`                                          | 1. Enter invalid email format 2. Move focus away from email field          | Email format validation should be triggered                                     | High     |
| AUTH-010 | Verify email format with missing domain            | `vmtester@`                                         | 1. Enter email 2. Move focus away from email field                         | Email should be rejected as invalid format                                      | High     |
| AUTH-011 | Verify email format with missing @                 | `vmtesteryopmail.com`                               | 1. Enter email 2. Move focus away from email field                         | Email should be rejected as invalid format                                      | High     |
| AUTH-012 | Verify email format with valid example structure   | `example@gmail.com`                                 | 1. Enter email 2. Move focus away from email field                         | Email should be accepted as valid format                                        | Medium   |

### B. Password Validation

| TC ID    | Test Scenario                                     | Test Data                               | Steps                                                             | Expected Result                                                         | Priority |
| -------- | ------------------------------------------------- | --------------------------------------- | ----------------------------------------------------------------- | ----------------------------------------------------------------------- | -------- |
| AUTH-013 | Verify password minimum length                    | 4-character password                    | 1. Enter 4-character password 2. Trigger validation               | Password should satisfy the minimum length requirement of 4 characters  | High     |
| AUTH-014 | Verify password maximum length                    | 10-character password                   | 1. Enter 10-character password 2. Trigger validation              | Password should satisfy the maximum length requirement of 10 characters | High     |
| AUTH-015 | Verify password below minimum length              | 3-character password                    | 1. Enter 3-character password 2. Trigger validation               | Password should be rejected because it is below the minimum length of 4 | High     |
| AUTH-016 | Verify password above maximum length              | 11-character password                   | 1. Enter 11-character password 2. Trigger validation              | Password should be rejected because it exceeds the maximum length of 10 | High     |
| AUTH-017 | Verify password contains lowercase character      | Password containing lowercase           | 1. Enter password with lowercase character 2. Trigger validation  | Password should satisfy the lowercase-character requirement             | High     |
| AUTH-018 | Verify password contains uppercase character      | Password containing uppercase           | 1. Enter password with uppercase character 2. Trigger validation  | Password should satisfy the uppercase-character requirement             | High     |
| AUTH-019 | Verify password contains special character        | Password containing special character   | 1. Enter password with special character 2. Trigger validation    | Password should satisfy the special-character requirement               | High     |
| AUTH-020 | Verify password with all required character types | `Pass@1234`                             | 1. Enter `Pass@1234` 2. Trigger validation                        | Password should satisfy the specified character requirements            | High     |
| AUTH-021 | Verify password without lowercase character       | Uppercase + special character + numbers | 1. Enter password without lowercase 2. Trigger validation         | Password should not satisfy the password complexity requirement         | High     |
| AUTH-022 | Verify password without uppercase character       | Lowercase + special character + numbers | 1. Enter password without uppercase 2. Trigger validation         | Password should not satisfy the password complexity requirement         | High     |
| AUTH-023 | Verify password without special character         | Letters + numbers only                  | 1. Enter password without special character 2. Trigger validation | Password should not satisfy the password complexity requirement         | High     |

### C. Authentication Error Handling & Rate Limiting

| TC ID    | Test Scenario                                            | Test Data           | Steps                                                   | Expected Result                                                                                                 | Priority |
| -------- | -------------------------------------------------------- | ------------------- | ------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- | -------- |
| AUTH-024 | Verify failed authentication error message               | Invalid credentials | 1. Enter invalid credentials 2. Click **Login**         | Clear/actionable authentication error should be displayed                                                       | High     |
| AUTH-025 | Verify rate limiting after 3 failed login attempts       | Invalid credentials | 1. Enter invalid credentials 2. Click **Login** 3 times | Rate limiting should be triggered after 3 failed attempts                                                       | Critical |
| AUTH-026 | Verify behavior on fourth login attempt after rate limit | Invalid credentials | 1. Perform 3 failed attempts 2. Attempt login again     | Rate-limit protection should prevent/handle the subsequent attempt according to the defined rate-limit behavior | Critical |
| AUTH-027 | Verify rate-limit response                               | 3 failed attempts   | 1. Perform 3 failed login attempts 2. Observe response  | Rate-limit response should be **`3`**, as specified                                                             | High     |

### D. Session Management

| TC ID    | Test Scenario                               | Test Data         | Steps                                                                                     | Expected Result                                                               | Priority |
| -------- | ------------------------------------------- | ----------------- | ----------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | -------- |
| AUTH-028 | Verify session timeout                      | Valid credentials | 1. Login successfully 2. Remain inactive for 1 hour                                       | Session should timeout after **1 hour**                                       | High     |
| AUTH-029 | Verify authenticated session before timeout | Valid credentials | 1. Login successfully 2. Access authenticated area before 1 hour                          | User should remain within the authenticated session before the 1-hour timeout | High     |
| AUTH-030 | Verify session after timeout                | Valid credentials | 1. Login 2. Allow session to reach 1 hour timeout 3. Attempt to access authenticated area | Session should no longer remain active after the 1-hour timeout               | High     |

### E. Password Reset

| TC ID    | Test Scenario                                        | Test Data                           | Steps                                                                                                               | Expected Result                                                        | Priority |
| -------- | ---------------------------------------------------- | ----------------------------------- | ------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- | -------- |
| AUTH-031 | Verify Forgot Password option                        | —                                   | 1. Open Login page 2. Observe password recovery option                                                              | **forgot password** option should be available                         | High     |
| AUTH-032 | Verify navigation to Forgot Password flow            | —                                   | 1. Open Login page 2. Click **forgot password**                                                                     | User should be taken to the password reset flow                        | High     |
| AUTH-033 | Verify password reset using registered email         | `vmtester@yopmail.com`              | 1. Click **forgot password** 2. Enter registered email 3. Submit                                                    | Password recovery should be initiated for the provided email           | High     |
| AUTH-034 | Verify reset token generation                        | Registered email                    | 1. Initiate password reset 2. Check reset process                                                                   | Secure reset token should be generated                                 | High     |
| AUTH-035 | Verify reset token is valid within 1 hour            | Valid reset token                   | 1. Generate reset token 2. Use token within 1 hour                                                                  | Reset token should be accepted within its 1-hour validity period       | High     |
| AUTH-036 | Verify reset token after 1 hour                      | Expired reset token                 | 1. Generate reset token 2. Wait until 1-hour validity expires 3. Use token                                          | Reset token should no longer be valid after 1 hour                     | High     |
| AUTH-037 | Verify password reset with valid password            | Valid password meeting requirements | 1. Open reset flow 2. Enter valid password 3. Complete reset                                                        | Password should be successfully reset                                  | High     |
| AUTH-038 | Verify password reset with invalid password          | Password violating requirements     | 1. Open reset flow 2. Enter invalid password 3. Submit                                                              | Password should be rejected based on the defined password requirements | High     |
| AUTH-039 | Verify user lands on Login page after password reset | Successfully reset password         | 1. Complete password reset 2. Observe navigation                                                                    | User should land on the **Login page**                                 | High     |
| AUTH-040 | Verify login with newly reset password               | Newly reset valid password          | 1. Complete password reset 2. Land on Login page 3. Enter registered email 4. Enter new password 5. Click **Login** | User should successfully authenticate using the new password           | Critical |

### F. API / Authentication Response

| TC ID    | Test Scenario                                 | Test Data           | Steps                                                                      | Expected Result                                                             | Priority |
| -------- | --------------------------------------------- | ------------------- | -------------------------------------------------------------------------- | --------------------------------------------------------------------------- | -------- |
| AUTH-041 | Verify successful authentication API response | Valid credentials   | 1. Enter valid credentials 2. Click **Login** 3. Observe API response      | Authentication API should return **HTTP 200** for successful authentication | High     |
| AUTH-042 | Verify password reset API success response    | Valid reset request | 1. Initiate password reset 2. Submit valid request 3. Observe API response | Applicable successful API response should be **HTTP 200**                   | High     |

**API endpoint:** Not provided. I have intentionally **not invented an endpoint URL**.

## Important Validation Note

There is one detail that needs clarification before I would consider the password test suite completely unambiguous:

You provided **“Password should contain 8 letters with small, capital, special characters”**, but also specified **minimum 4 and maximum 10 characters**.

For the test cases above, I treated these as separate requirements:

* Minimum length = **4**
* Maximum length = **10**
* Complexity = lowercase + uppercase + special character
* Example valid password = **`Pass@1234`**

This is based directly on your supplied information; I did not assume that “8 letters” means exactly 8 characters. The anti-hallucination rules require unclear information to be identified rather than silently assumed. 

**Also, “rate-limit response: 3” is preserved exactly as provided.** If `3` means something specific such as an HTTP `429`, error message, or response body, that should be specified before creating API-level test cases.
