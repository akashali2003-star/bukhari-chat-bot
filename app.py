from __future__ import annotations

import streamlit as st

try:
    from src.agent import BasicAgent
except Exception as exc:  # pragma: no cover - UI fallback for missing config
    BasicAgent = None
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None


st.set_page_config(page_title="Bukhari Chat Bot", page_icon="🤖", layout="centered")

if BasicAgent is None:
    st.error(f"Unable to start the agent: {IMPORT_ERROR}")
    st.info("Add your GEMINI_API_KEY to the project-root .env file and restart the app.")
    st.stop()

if "agent" not in st.session_state:
    st.session_state.agent = BasicAgent(name="Bukhari Chat Bot")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Assalam-o-Alaikum, Main Bukhari Chat Bot hoon. Aapka sawal likhein."}
    ]

st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(135deg, #f8fafc 0%, #eef6ff 100%);
        }
        h1 {
            color: #0f172a;
            margin-bottom: 0.2rem;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Bukhari Chat Bot")
st.caption("Smart assistant powered by Gemini")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Type your message...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.agent.respond(prompt)
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
