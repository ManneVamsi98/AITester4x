"""Test Plan Agent - full dashboard UI.

Run with:  streamlit run app.py

Tabs: Generate (prompt + ticket picker + structured plan) and History
(out/ plans). Sidebar shows connection status, force toggle, settings link.
"""

import sys
from pathlib import Path

import streamlit as st

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

import config_store  # noqa: E402
import jira_client  # noqa: E402
import navigation  # noqa: E402
from navigation import PipelineError  # noqa: E402
from render import render_plan_markdown  # noqa: E402

st.set_page_config(page_title="Test Plan Agent", page_icon="📋", layout="wide")

CSS = """
<style>
  .ticket-card { background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:14px 18px; margin-bottom:10px; }
  .ticket-key { font-size:15px; font-weight:700; color:#2563eb; }
  .badge { display:inline-block; border-radius:999px; padding:2px 10px; font-size:12px; font-weight:600; margin-right:6px; }
  .b-blue { background:#dbeafe; color:#1d4ed8; }
  .b-amber { background:#fef3c7; color:#b45309; }
  .b-emerald { background:#d1fae5; color:#047857; }
  .b-slate { background:#e2e8f0; color:#475569; }
  .b-violet { background:#ede9fe; color:#6d28d9; }
  .stat-num { font-size:26px; font-weight:800; color:#2563eb; }
  .stat-lbl { font-size:12px; color:#64748b; }
  .justified { font-size:12px; color:#64748b; font-style:italic; }
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


def badge(text, cls="b-slate"):
    return f'<span class="badge {cls}">{text}</span>'


def _conn_status() -> tuple:
    """Return (jira_ok, groq_ok, detail)."""
    cfg = config_store.load_config()
    jira_ok = config_store.is_configured(cfg)
    groq_ok = config_store.is_provider_ready(cfg)
    detail = ""
    if jira_ok:
        detail += f"Jira: {jira_client.normalize_base_url(cfg['jira_url'])}"
    else:
        detail += "Jira: not configured"
    detail += " · Groq: " + ("key present" if groq_ok else "missing")
    return jira_ok, groq_ok, detail


def render_ticket_card(ticket: dict) -> None:
    st.markdown(
        f'<div class="ticket-card">'
        f'<span class="ticket-key">{ticket["key"]}</span>'
        f'{badge(ticket["status"], "b-blue")}{badge(ticket["issue_type"], "b-violet")}{badge(ticket["priority"], "b-amber")}'
        f'<div style="font-size:14px;margin-top:6px">{ticket["summary"]}</div>'
        f'<div style="font-size:12px;color:#64748b;margin-top:4px">Assignee: {ticket["assignee"]} · '
        f'Labels: {", ".join(ticket["labels"]) or "—"} · Components: {", ".join(ticket["components"]) or "—"}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_readiness(score: int, total: int) -> None:
    pct = int(score / total * 100)
    st.progress(pct / 100, text=f"Readiness: {score}/{total} ({pct}%)")


def render_plan_sections(ticket: dict, plan: dict) -> None:
    # Objective
    st.subheader("🎯 Objective")
    st.info(plan.get("objective", "TBD"))

    # Scope table with justified_by
    st.subheader("📋 Scope")
    if plan.get("scope"):
        st.table(
            [{"Scope item": s.get("entry"), "Justified by": s.get("justified_by")} for s in plan["scope"]]
        )
    else:
        st.write("TBD")

    # Environments chips
    st.subheader("🖥️ Environments")
    st.write(" · ".join(f"`{e}`" for e in plan.get("environments", [])) or "TBD")

    # Entry / Exit criteria
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🚦 Entry criteria")
        for item in plan.get("entry_criteria", []):
            st.write(f"- {item}")
    with c2:
        st.subheader("🏁 Exit criteria")
        for item in plan.get("exit_criteria", []):
            st.write(f"- {item}")

    # Test cases accordions
    st.subheader("🧪 Test cases")
    for tc in plan.get("test_cases", []):
        with st.expander(f"{tc.get('id', 'TC?')} — {tc.get('title', '')}"):
            st.markdown(f"**Precondition:** {tc.get('precondition', '')}")
            steps = tc.get("steps", [])
            if steps:
                st.markdown("**Steps:**")
                for i, s in enumerate(steps, 1):
                    st.write(f"{i}. {s}")
            st.markdown(f"**Expected:** {tc.get('expected', '')}")
    if not plan.get("test_cases"):
        st.write("TBD")

    # Risks table
    st.subheader("⚠️ Risks & mitigations")
    if plan.get("risks"):
        st.table([{"Risk": r.get("risk"), "Mitigation": r.get("mitigation")} for r in plan["risks"]])
    else:
        st.write("TBD")

    # Deliverables
    st.subheader("📦 Deliverables")
    for d in plan.get("deliverables", []):
        st.write(f"- {d}")

    # Assumptions
    st.subheader("📝 Assumptions")
    if plan.get("assumptions"):
        st.info("\n".join(f"- {a}" for a in plan["assumptions"]))
    else:
        st.write("None")


def run_generate(text: str, force: bool) -> None:
    cfg = config_store.load_config()
    if not config_store.is_configured(cfg):
        st.error("Jira is not configured yet. Open the Settings page and save your Jira URL, email, and API token.")
        return
    if not config_store.is_provider_ready(cfg):
        st.error("Groq API key is not configured. Open the Settings page and add it.")
        return

    try:
        with st.spinner("Fetching ticket from Jira..."):
            ticket = navigation.fetch_normalize(text, cfg)
        render_ticket_card(ticket)

        score, total, _ = navigation.readiness_score(ticket)
        render_readiness(score, total)

        if score < navigation.MIN_READINESS and not force:
            st.warning(navigation.readiness_gap_report(ticket))
            st.info("Tick 'Force generate' in the sidebar to generate anyway.")
            return

        with st.spinner("Generating test plan via Groq (one call)..."):
            plan, meta = navigation.plan_from_ticket(ticket, cfg, force=force)

        render_plan_sections(ticket, plan)

        st.divider()
        st.caption(f"Generated in {meta['duration_s']}s via {meta['model']} · readiness {meta['readiness']['score']}/{meta['readiness']['total']}")
        st.download_button(
            "⬇️ Download plan (.md)",
            data=render_plan_markdown(ticket, plan),
            file_name=f"{ticket['key']}.md",
            mime="text/markdown",
        )
        with st.expander("View trace (JSON)"):
            st.json(meta)
    except PipelineError as exc:
        st.error(exc.message)
    except Exception as exc:  # noqa: BLE001 - surface anything unexpected in the UI
        st.error(f"Unexpected error: {exc}")


def tab_generate() -> None:
    cfg = config_store.load_config()
    force = st.session_state.get("force", False)

    st.subheader("Generate a test plan")
    prompt = st.text_input(
        "Prompt or Jira key",
        placeholder='e.g. "Fetch KAN-5 and create a test plan" or just KAN-5',
        label_visibility="collapsed",
    )

    # Quick-pick chips from live Jira.
    issues = jira_client.list_issues(cfg, max_results=8)
    if issues:
        st.caption("Quick pick:")
        cols = st.columns(min(len(issues), 4))
        for i, issue in enumerate(issues):
            with cols[i % 4]:
                if st.button(f"{issue['key']} · {issue['summary'][:24]}", key=f"chip_{issue['key']}", use_container_width=True):
                    prompt = issue["key"]

    if st.button("🚀 Generate", type="primary", use_container_width=True) and prompt:
        run_generate(prompt, force)


def tab_history() -> None:
    st.subheader("Generated plans")
    out_dir = HERE / "out"
    files = sorted(out_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True) if out_dir.exists() else []
    if not files:
        st.info("No plans generated yet. Go to the Generate tab and run one.")
        return
    for f in files:
        import time as _time
        mtime = _time.strftime("%Y-%m-%d %H:%M", _time.localtime(f.stat().st_mtime))
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(f"**{f.name}** · {mtime}")
        with c2:
            if st.button("View", key=f"view_{f.name}"):
                st.session_state["history_file"] = f
        if st.session_state.get("history_file") == f:
            st.markdown(f.read_text(encoding="utf-8"))
            st.download_button("⬇️ Download", data=f.read_text(encoding="utf-8"), file_name=f.name, mime="text/markdown", key=f"dl_{f.name}")


def main() -> None:
    st.title("📋 Test Plan Agent")
    st.caption("Jira ticket in, formal Test Plan out.")

    # Sidebar
    with st.sidebar:
        st.header("Status")
        jira_ok, groq_ok, detail = _conn_status()
        st.write(f"🔵 Jira: {'configured' if jira_ok else 'not configured'}")
        st.write(f"🟢 Groq: {'key present' if groq_ok else 'missing'}")
        st.caption(detail)
        st.divider()
        st.checkbox("Force generate (skip readiness gate)", value=False, key="force")
        st.divider()
        st.page_link("pages/settings.py", label="⚙️ Settings")

    tab_gen, tab_hist = st.tabs(["🚀 Generate", "🗂️ History"])
    with tab_gen:
        tab_generate()
    with tab_hist:
        tab_history()


if __name__ == "__main__":
    main()
