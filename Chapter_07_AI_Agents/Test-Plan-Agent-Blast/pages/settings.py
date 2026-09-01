"""Settings page - configure Jira credentials and the Groq key.

Settings persist to config.json (gitignored) via config_store; empty
fields are seeded from .env. Both connections can be tested here
(BLAST Phase 2: Link).
"""

import sys
from pathlib import Path

import streamlit as st

HERE = Path(__file__).parent.parent
sys.path.insert(0, str(HERE))

import config_store  # noqa: E402

st.set_page_config(page_title="Settings - Test Plan Agent", page_icon="⚙️", layout="wide")


def _test_connections(cfg: dict) -> None:
    import requests

    import jira_client  # noqa: E402
    import llm_client  # noqa: E402

    ok = True

    base = jira_client.normalize_base_url(cfg.get("jira_url", ""))
    if not base or not cfg.get("jira_email") or not cfg.get("jira_token"):
        st.error("Jira: URL/email/token missing.")
        ok = False
    else:
        try:
            resp = requests.get(f"{base}/rest/api/3/myself", auth=(cfg["jira_email"], cfg["jira_token"]), timeout=15)
            if resp.status_code == 200:
                st.success(f"Jira: authenticated at {base}")
            elif resp.status_code == 401:
                st.error("Jira: credentials rejected (401).")
                ok = False
            else:
                st.error(f"Jira: HTTP {resp.status_code}.")
                ok = False
        except Exception as exc:
            st.error(f"Jira: {exc}")
            ok = False

    if not cfg.get("groq_key"):
        st.error("Groq: API key missing.")
        ok = False
    else:
        try:
            resp = requests.post(
                llm_client.GROQ_URL,
                json={"model": llm_client.GROQ_MODEL, "messages": [{"role": "user", "content": "ping"}], "max_tokens": 1},
                headers={"Authorization": f"Bearer {cfg['groq_key']}"},
                timeout=30,
            )
            if resp.status_code == 200:
                st.success(f"Groq: {llm_client.GROQ_MODEL} reachable")
            else:
                st.error(f"Groq: HTTP {resp.status_code} - {resp.text[:200]}")
                ok = False
        except Exception as exc:
            st.error(f"Groq: {exc}")
            ok = False

    if ok:
        st.success("Both connections OK - ready to generate plans.")


def main() -> None:
    st.title("⚙️ Settings")
    st.caption("Credentials are stored locally in config.json (gitignored) - never in source code.")

    cfg = config_store.load_config()

    with st.form("settings_form"):
        st.subheader("Jira")
        jira_url = st.text_input(
            "Jira base URL",
            value=cfg.get("jira_url", ""),
            placeholder="https://your-site.atlassian.net",
            help="Deep Jira links are trimmed to the base URL automatically.",
        )
        jira_email = st.text_input("Jira email ID", value=cfg.get("jira_email", ""))
        jira_token = st.text_input("Jira API token", value=cfg.get("jira_token", ""), type="password")

        st.subheader("LLM")
        groq_key = st.text_input("Groq API key", value=cfg.get("groq_key", ""), type="password")

        submitted = st.form_submit_button("Save settings", type="primary")

    if submitted:
        new_cfg = {
            "jira_url": jira_url.strip(),
            "jira_email": jira_email.strip(),
            "jira_token": jira_token.strip(),
            "groq_key": groq_key.strip(),
        }
        try:
            config_store.save_config(new_cfg)
            st.success("Settings saved to config.json.")
        except OSError as exc:
            st.error(f"Could not save settings: {exc}")

    st.divider()
    st.subheader("Test connections")
    st.caption("BLAST Phase 2: verify Jira and Groq before generating.")
    if st.button("Test both connections", type="secondary"):
        _test_connections(config_store.load_config())


if __name__ == "__main__":
    main()
