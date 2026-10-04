// Sample answers for demo mode — used when the live index / keys aren't configured.
// Content is grounded in the Chapter 11/12 QA knowledge base (VWO tickets, the
// 500-case export, the framework repos). Kept small and honest on purpose.

module.exports = {
  intro:
    "**Demo mode.** This hosted copy answers from a small set of **sample** results, so the live " +
    "vector index isn't queried and no API keys are needed. Try one of the example questions below — " +
    "the behaviour (grounded answer + citations, or an honest \"insufficient evidence\") matches the real app.",

  examples: [
    {
      keywords: ["vwo-26", "vwo 26", "login failure", "valid credentials", "vwo app"],
      question: "What is the VWO-26 login failure about?",
      answer:
        "**VWO-26** reports login failures on the VWO app even when users supply valid credentials.\n\n" +
        "- Steps: open `https://app.vwo.com/#/login`, enter a valid username and password, click Submit.\n" +
        "- Expected: the user is logged in and redirected to the dashboard.\n" +
        "- Actual: an error message is shown and login fails [1].\n\n" +
        "A follow-up triage discussion linked the symptom to the new GCP-based Jenkins agents' " +
        "egress IP not being on the VWO test-account allowlist, rather than a framework defect [2].",
      citations: [
        {
          source: "Bug_VWO_26.md",
          type: "jira",
          score: 0.79,
          snippet:
            "[VWO-26] Login failure on VWO app (https://app.vwo.com/#/login) with valid credentials. " +
            "Expected result: User should be logged in and redirected to the dashboard. " +
            "Actual result: An error message is displayed and login fails.",
        },
        {
          source: "2026-04-07_Login_Failure_Triage_Meeting.txt",
          type: "transcript",
          score: 0.71,
          snippet: "Login failure triage meeting notes — cause narrowed to agent egress IP allowlisting.",
        },
      ],
    },
    {
      keywords: ["login-001", "page load", "verify login", "scenario tid"],
      question: "test case for verifying the login page load",
      answer:
        "**LOGIN-001** — *Verify Login - page load*.\n\n" +
        "- Precondition: the VWO login page is available in a supported test environment.\n" +
        "- Steps: open the VWO login area and prepare the data/permissions required for the page load.\n" +
        "- Expected: the system handles the page load correctly per the VWO requirements [1].\n\n" +
        "Priority: Medium · Automated: Yes.",
      citations: [
        {
          source: "VWO_500_Test_Cases.csv",
          type: "test_case",
          score: 0.74,
          snippet:
            "Scenario TID: LOGIN-001 | TestCase Description: Verify Login - page load | " +
            "Priority: Medium | Is Automated: Yes",
        },
      ],
    },
    {
      keywords: ["qab-101", "qab 101", "ip address", "agent migration", "did not match"],
      question: "CI login tests failing because of the IP address",
      answer:
        "**QAB-101** — *CI login tests fail with \"IP address or location did not match\" after the " +
        "Jenkins agent migration.*\n\n" +
        "- Every positive login test failed on CI while passing locally, starting at build #142.\n" +
        "- Cause: the new GCP agent pool egresses via NAT `35.200.14.7`, which wasn't on the VWO " +
        "test-account IP allowlist (old agents used `203.0.113.24`).\n" +
        "- Fix: added `35.200.14.7` to the allowlist; build #143 went green [1].",
      citations: [
        {
          source: "QAB-101_CI_login_IP_block.md",
          type: "jira",
          score: 0.80,
          snippet:
            "Since build #142 of vwo-selenium-regression, every positive login test fails on CI while " +
            "passing locally. Old agents egressed via 203.0.113.24; the GCP pool uses NAT 35.200.14.7. " +
            "Added 35.200.14.7 to the allowlist. Build #143 is green.",
        },
      ],
    },
    {
      keywords: ["qab-103", "qab 103", "cart", "checkout", "playwright"],
      question: "Playwright checkout test sees two cart rows",
      answer:
        "**QAB-103** — the Playwright checkout test observes **2 cart rows instead of 1**, i.e. a " +
        "UI/expectation mismatch in the checkout flow [1]. Triage the cart state handling and the " +
        "assertion in the checkout spec.",
      citations: [
        {
          source: "QAB-103_checkout_parallel_cart.md",
          type: "jira",
          score: 0.62,
          snippet: "QAB-103 — Playwright checkout test sees 2 cart rows instead of 1.",
        },
      ],
    },
    {
      keywords: ["page object", "pom", "selenium", "framework", "locator"],
      question: "How do I write a page object in the Selenium framework?",
      answer:
        "The Selenium framework uses the **Page Object Model**: give each screen its own class that " +
        "holds the locators and exposes action methods, and have tests call those methods instead of " +
        "touching locators directly. It keeps selectors in one place and makes tests readable and " +
        "maintainable [1].",
      citations: [
        {
          source: "ATB13xSeleniumAdvanceFramework (framework code)",
          type: "code",
          score: 0.58,
          snippet:
            "Page Object Model classes define locators and action methods consumed by the test classes.",
        },
      ],
    },
    {
      keywords: ["refund", "pricing", "pro plan", "billing", "policy"],
      question: "What is the refund policy for the Pro plan?",
      answer: "Insufficient evidence in the knowledge base.",
      citations: [],
    },
  ],
};
