"""Screen 1 - Chat: ChatGPT-style interface for generating test cases.

Run with:  streamlit run app.py
"""

import re
import time

import streamlit as st

import config_store
import jira_client
import llm_client

JIRA_KEY_RE = re.compile(r"\b([A-Z][A-Z0-9]+-\d+)\b")
COUNT_RE = re.compile(r"(\d+)\s+test\s+cases?\b", re.IGNORECASE)


def parse_count(text: str, default: int) -> int:
    """Extract an explicit 'N test cases' count from the message, else default."""
    match = COUNT_RE.search(text)
    if match:
        return max(1, min(int(match.group(1)), 50))
    return default


def render_llm_output(markdown_text: str) -> None:
    """Render LLM output, preferring a markdown table but falling back to code."""
    stripped = markdown_text.strip()
    if stripped.startswith("|") or stripped.lower().startswith("| test id"):
        st.markdown(stripped)
    else:
        st.code(stripped, language="markdown")


def handle_message(text: str) -> None:
    """Process one user message: parse, fetch, generate, render."""
    cfg = config_store.load_config()

    if not config_store.is_configured(cfg):
        st.error("Jira is not configured yet. Open the Settings screen and save your Jira URL, email, and API token.")
        return

    key_match = JIRA_KEY_RE.search(text)
    if not key_match:
        st.error('I could not find a Jira ticket key in your message (e.g. "create test cases for QA-102").')
        return

    issue_key = key_match.group(1)
    count = parse_count(text, cfg.get("default_tc_count", 10))

    with st.spinner(f"Fetching {issue_key} from Jira..."):
        try:
            ticket = jira_client.get_ticket(issue_key, cfg)
        except jira_client.JiraError as exc:
            st.error(str(exc))
            return

    # Merge the ticket into the requirements block the template will consume.
    requirements = (
        f"Ticket: {ticket['key']} ({ticket['issue_type']})\n"
        f"Summary: {ticket['summary']}\n"
        f"Status: {ticket['status']}\n\n"
        f"Description:\n{ticket['description']}\n"
    )
    if ticket["acceptance_criteria"]:
        requirements += f"\nAcceptance Criteria:\n{ticket['acceptance_criteria']}\n"

    provider_label = "Ollama (Gemma 3 1B)" if cfg.get("provider") == "ollama" else "Groq"
    with st.spinner(f"Generating {count} test cases via {provider_label}..."):
        started = time.time()
        try:
            output = llm_client.generate_test_cases(requirements, count, cfg)
        except llm_client.LLMError as exc:
            st.error(f"Test case generation failed: {exc}")
            return
        elapsed = time.time() - started

    st.session_state.messages.append({"role": "assistant", "content": output})
    render_llm_output(output)

    st.caption(f"Generated in {elapsed:.1f}s using {provider_label}.")
    st.download_button(
        label="Download test cases (.md)",
        data=output,
        file_name=f"{issue_key}_test_cases.md",
        mime="text/markdown",
    )


def main() -> None:
    st.set_page_config(page_title="Jira Test Case Generator", page_icon="✅")
    st.title("Jira Test Case Generator")
    st.caption("Ask for test cases with a Jira ticket key - e.g. *create test cases for QA-102*.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Chat history.
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant":
                render_llm_output(msg["content"])
            else:
                st.markdown(msg["content"])

    # Input.
    if prompt := st.chat_input("Type a request, e.g. 'create 12 test cases for QA-102'..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        handle_message(prompt)


if __name__ == "__main__":
    main()
