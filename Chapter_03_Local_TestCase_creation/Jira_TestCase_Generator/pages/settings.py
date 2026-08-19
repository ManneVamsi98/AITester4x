"""Screen 2 - Settings: configure Jira credentials, LLM provider, and defaults.

Settings are persisted to config.json (gitignored) via config_store.
"""

import streamlit as st

import config_store


def main() -> None:
    st.set_page_config(page_title="Settings - Jira Test Case Generator", page_icon="⚙️")
    st.title("Settings")
    st.caption("Credentials are stored locally in `config.json` (gitignored) - never in source code.")

    cfg = config_store.load_config()

    with st.form("settings_form"):
        st.subheader("Jira")
        jira_url = st.text_input("Jira base URL", value=cfg.get("jira_url", ""),
                                 placeholder="https://your-site.atlassian.net",
                                 help="Deep Jira links are trimmed to the base URL automatically.")
        jira_email = st.text_input("Jira email ID", value=cfg.get("jira_email", ""))
        jira_token = st.text_input("Jira API token", value=cfg.get("jira_token", ""), type="password")

        st.subheader("LLM Provider")
        provider = st.radio(
            "Provider",
            options=["groq", "ollama"],
            index=0 if cfg.get("provider", "groq") == "groq" else 1,
            format_func=lambda p: {
                "groq": "Groq (hosted) - recommended",
                "ollama": "Ollama (local, gemma3:1b) - try Ollama, fall back to Groq",
            }[p],
        )
        groq_key = st.text_input("Groq API key", value=cfg.get("groq_key", ""), type="password")

        st.subheader("Defaults")
        default_tc_count = st.number_input(
            "Default number of test cases",
            min_value=1, max_value=50, value=int(cfg.get("default_tc_count", 10)),
            help="Used when the chat message doesn't specify a count.",
        )

        submitted = st.form_submit_button("Save settings", type="primary")

    if submitted:
        new_cfg = {
            "jira_url": jira_url.strip(),
            "jira_email": jira_email.strip(),
            "jira_token": jira_token.strip(),
            "provider": provider,
            "groq_key": groq_key.strip(),
            "default_tc_count": int(default_tc_count),
        }
        try:
            config_store.save_config(new_cfg)
            st.success("Settings saved to config.json.")
        except OSError as exc:
            st.error(f"Could not save settings: {exc}")


if __name__ == "__main__":
    main()
