from __future__ import annotations

import html
import json

import streamlit as st
import streamlit.components.v1 as components

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

if st.sidebar.button("New Chat", icon="🗨️", use_container_width=True):
    st.session_state.agent = BasicAgent(name="Bukhari Chat Bot")
    st.session_state.messages = [
        {"role": "assistant", "content": "Assalam-o-Alaikum, Main Bukhari Chat Bot hoon. Aapka sawal likhein."}
    ]
    st.rerun()

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
        if message.get("image"):
            st.image(message["image"], caption="Uploaded image", use_container_width=True)
        st.markdown(message["content"])
        if message["role"] == "assistant":
            copy_text = html.escape(json.dumps(message["content"]), quote=True)
            components.html(
                f"""
                <button class="copy-response" onclick="navigator.clipboard.writeText({copy_text})">
                    Copy response
                </button>
                <style>
                    .copy-response {{
                        border: 1px solid #cbd5e1;
                        border-radius: 6px;
                        background: white;
                        color: #334155;
                        cursor: pointer;
                        padding: 0.35rem 0.65rem;
                    }}
                </style>
                """,
                height=42,
            )

uploaded_image = st.file_uploader(
    "Upload an image to ask about it",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=False,
)
prompt = st.chat_input("Type your message...")

if prompt:
    image_data = uploaded_image.getvalue() if uploaded_image else None
    image_mime_type = uploaded_image.type if uploaded_image else None
    user_message = {"role": "user", "content": prompt}
    if image_data:
        user_message["image"] = image_data
    st.session_state.messages.append(user_message)
    with st.chat_message("user"):
        if image_data:
            st.image(image_data, caption="Uploaded image", use_container_width=True)
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.agent.respond(prompt, image_data, image_mime_type)
        st.markdown(response)
        copy_text = html.escape(json.dumps(response), quote=True)
        components.html(
            f"""
            <button class="copy-response" onclick="navigator.clipboard.writeText({copy_text})">
                Copy response
            </button>
            """,
            height=42,
        )

    st.session_state.messages.append({"role": "assistant", "content": response})
