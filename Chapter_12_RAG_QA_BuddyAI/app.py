"""QABuddy.ai — Streamlit chatbot with cited, grounded answers."""

from __future__ import annotations

import html

import streamlit as st

from qabuddy import rag
from qabuddy.config import Settings
from qabuddy.retrieval import Retriever

st.set_page_config(page_title="QABuddy.ai", page_icon="🔎", layout="wide")

SOURCE_TYPES = {
    "test_case": "Test cases",
    "jira": "JIRA",
    "code": "Framework code",
    "document": "Docs / PRD",
    "transcript": "Meeting notes",
    "diagram": "Lucid charts",
    "jenkins_log": "Jenkins logs",
}
REPOS = ["selenium", "playwright"]
EXAMPLES = [
    "test case for verifying the login page load",
    "What is the VWO-26 login failure about?",
    "CI login tests failing because of the IP address",
    "How do I write a page object in the Selenium framework?",
]

CUSTOM_CSS = """
<style>
  .block-container {max-width: 1080px; padding-top: 1.6rem; padding-bottom: 3rem;}
  #MainMenu, footer {visibility: hidden;}

  .qb-hero {
    background: linear-gradient(120deg, #4f46e5 0%, #7c3aed 48%, #0ea5e9 100%);
    border-radius: 18px; padding: 22px 26px; color: #fff;
    box-shadow: 0 12px 32px rgba(79, 70, 229, .28); margin-bottom: 1.1rem;
  }
  .qb-hero h1 {margin: 0; font-size: 1.95rem; letter-spacing: -.02em; font-weight: 800;}
  .qb-hero p {margin: .4rem 0 .7rem; opacity: .92; font-size: .95rem; max-width: 60ch;}
  .qb-pill {
    display: inline-block; padding: 3px 11px; border-radius: 999px; font-size: .74rem;
    font-weight: 600; margin: 0 6px 0 0; background: rgba(255,255,255,.18);
    border: 1px solid rgba(255,255,255,.30); backdrop-filter: blur(3px);
  }

  .qb-card {
    border: 1px solid rgba(125,125,150,.22); border-radius: 14px;
    padding: 11px 14px; margin: 7px 0; background: rgba(127,127,160,.07);
  }
  .qb-badge {
    display: inline-block; min-width: 20px; text-align: center; padding: 2px 8px;
    border-radius: 8px; background: #4f46e5; color: #fff; font-weight: 700;
    font-size: .73rem; margin-right: 9px;
  }
  .qb-src {font-weight: 650;}
  .qb-type {
    display: inline-block; padding: 1px 9px; border-radius: 999px; font-size: .69rem;
    font-weight: 700; margin-left: 8px; background: rgba(14,165,233,.16); color: #0369a1;
  }
  .qb-score {float: right; font-size: .71rem; opacity: .62;}

  .qb-empty {text-align: center; opacity: .8; padding: 1.4rem 0 .6rem; font-size: .95rem;}
</style>
"""


@st.cache_resource(show_spinner="Loading models…")
def get_retriever() -> Retriever:
    return Retriever(Settings.load())


def source_label(meta: dict) -> str:
    for key in ("tc_id", "jira_key", "path", "source_file"):
        if meta.get(key):
            return str(meta[key])
    return "source"


def as_dicts(contexts) -> list[dict]:
    out = []
    for item in contexts:
        if isinstance(item, dict):
            out.append(item)
        else:
            out.append({"text": item.text, "metadata": item.metadata, "score": item.score})
    return out


def render_citations(items: list[dict], show_chunks: bool) -> None:
    if not items:
        return
    with st.expander(f"📎 Citations ({len(items)})", expanded=False):
        for number, item in enumerate(items, start=1):
            meta = item["metadata"]
            kind = SOURCE_TYPES.get(meta.get("source_type", ""), "")
            type_pill = f"<span class='qb-type'>{html.escape(kind)}</span>" if kind else ""
            st.markdown(
                f"<div class='qb-card'><span class='qb-badge'>{number}</span>"
                f"<span class='qb-src'>{html.escape(source_label(meta))}</span>"
                f"{type_pill}"
                f"<span class='qb-score'>score {item['score']:.3f}</span></div>",
                unsafe_allow_html=True,
            )
            if show_chunks:
                st.code(item["text"][:1200], language=None)


def render_message(message: dict, show_chunks: bool) -> None:
    st.markdown(message["content"])
    if message["role"] == "assistant":
        render_citations(message.get("sources", []), show_chunks)


def main() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    settings = Settings.load()

    count = None
    with st.sidebar:
        st.markdown("### 🔎 QABuddy.ai")
        selected = st.pills(
            "Sources",
            list(SOURCE_TYPES),
            selection_mode="multi",
            default=list(SOURCE_TYPES),
            format_func=lambda key: SOURCE_TYPES[key],
        )
        repos = st.pills("Repos", REPOS, selection_mode="multi", default=[])
        show_chunks = st.toggle("Show retrieved chunks", value=False)

        st.divider()
        try:
            from qabuddy import qdrant_store

            count = qdrant_store.count(get_retriever().client, settings.collection)
        except Exception as exc:
            st.warning(f"Qdrant not reachable: {exc}")
        if count is not None:
            st.metric("Indexed chunks", count)
            if count == 0:
                st.info("Nothing indexed yet:\n\n`python -m qabuddy.cli ingest --source all`")
        st.caption(f"Embedder · `{settings.embed_provider}` / `{settings.embed_model}`")
        st.caption(f"Generator · `{settings.groq_model}`")

        st.divider()
        if st.button("Clear chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    st.markdown(
        "<div class='qb-hero'><h1>QABuddy.ai</h1>"
        "<p>One cited answer across test cases, JIRA, framework code, PRDs, docs, "
        "meeting notes, charts and CI logs.</p>"
        f"<span class='qb-pill'>{count if count is not None else '–'} chunks</span>"
        f"<span class='qb-pill'>{html.escape(settings.embed_provider)}</span>"
        f"<span class='qb-pill'>{html.escape(settings.groq_model)}</span></div>",
        unsafe_allow_html=True,
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        avatar = "🧑‍💻" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar):
            render_message(message, show_chunks)

    if not st.session_state.messages:
        st.markdown(
            "<div class='qb-empty'>Ask a question, or start with one of these:</div>",
            unsafe_allow_html=True,
        )
        columns = st.columns(2)
        for index, example in enumerate(EXAMPLES):
            if columns[index % 2].button(example, key=f"example{index}", use_container_width=True):
                st.session_state.pending = example
                st.rerun()

    prompt = st.chat_input("Ask about a test case, a bug, framework code, or a requirement…")
    if st.session_state.get("pending"):
        prompt = st.session_state.pop("pending")
    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Retrieving…"):
            try:
                results = get_retriever().retrieve(
                    prompt, source_types=selected or None, repos=repos or None
                )
                sources = as_dicts(results)
            except Exception as exc:
                st.error(f"Retrieval failed: {exc}")
                results, sources = [], []
        answer = rag.generate(settings, prompt, results) if sources else rag.NO_EVIDENCE
        st.markdown(answer)
        render_citations(sources, show_chunks)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "sources": sources}
    )


main()
