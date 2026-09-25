from __future__ import annotations

import html
import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

try:
    from src.agent import BasicAgent
except Exception as exc:  # pragma: no cover - UI fallback for missing config
    BasicAgent = None
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None

from src.supabase_client import SupabaseConfigurationError, SupabaseService, get_supabase_service


WELCOME_MESSAGE = "Assalam-o-Alaikum, Main Bukhari Chat Bot hoon. Aapka sawal likhein."
LOGO_PATH = Path(__file__).resolve().parent / "bukhari.logo.png"
ENABLE_SUPABASE_AUTH = False

st.set_page_config(page_title="Bukhari Chat Bot", page_icon=str(LOGO_PATH), layout="wide")

components.html(
    """
    <script>
        (() => {
            const parentDocument = window.parent.document;
            const staticPath = "/app/static/";

            if (!parentDocument.querySelector('link[rel="manifest"]')) {
                const manifest = parentDocument.createElement("link");
                manifest.rel = "manifest";
                manifest.href = `${staticPath}manifest.json`;
                parentDocument.head.appendChild(manifest);
            }

            if (!parentDocument.querySelector('meta[name="theme-color"]')) {
                const themeColor = parentDocument.createElement("meta");
                themeColor.name = "theme-color";
                themeColor.content = "#147d92";
                parentDocument.head.appendChild(themeColor);
            }

            if ("serviceWorker" in navigator) {
                navigator.serviceWorker.register(`${staticPath}sw.js`, { scope: "/app/" })
                    .catch(() => navigator.serviceWorker.register(`${staticPath}sw.js`));
            }
        })();
    </script>
    """,
    height=0,
)

st.markdown(
    """
    <style>
        :root {
            --ink: #17212b;
            --muted: #6b7785;
            --surface: #ffffff;
            --line: #e1e8ed;
            --accent: #147d92;
            --accent-soft: #dff2f4;
        }
        .stApp { background: #f7fafb; color: var(--ink); }
        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stDecoration"] { display: none; }
        .block-container { max-width: 980px; padding: 2.8rem 1.25rem 7.5rem; }
        h1, h2, h3, p, label { letter-spacing: 0; }
        h1 { color: var(--ink); font-size: 2rem !important; font-weight: 750 !important; margin: 0 !important; }
        .app-kicker { color: var(--accent); font-size: 0.75rem; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 0.45rem; }
        .app-subtitle { color: var(--muted); margin-top: 0.35rem; }
        [data-testid="stChatMessage"] { border: 1px solid var(--line); border-radius: 18px; margin: 0.9rem 0; padding: 0.95rem 1.1rem; max-width: 82%; background: var(--surface); box-shadow: 0 5px 18px rgba(26, 53, 66, 0.045); }
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) { margin-left: auto; background: var(--accent-soft); border-color: #c5e6e8; }
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) { margin-right: auto; }
        [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p { line-height: 1.65; }
        [data-testid="stChatInput"] { border-top: 0 !important; background: transparent !important; }
        [data-testid="stChatInput"] > div { border: 1px solid #cad7dd !important; border-radius: 19px !important; background: var(--surface) !important; box-shadow: 0 10px 30px rgba(33, 67, 79, 0.13) !important; padding: 0.25rem 0.4rem 0.25rem 0.8rem !important; }
        [data-testid="stChatInput"] textarea { color: var(--ink) !important; }
        [data-testid="stSidebar"] { background: #eef4f5; border-right: 1px solid var(--line); }
        [data-testid="stSidebar"] .block-container { padding: 1.5rem 1.1rem; }
        .sidebar-brand { font-size: 1.2rem; font-weight: 750; color: var(--ink); }
        .sidebar-note { color: var(--muted); font-size: 0.86rem; line-height: 1.5; }
        .copy-response { border: 1px solid var(--line); border-radius: 8px; background: transparent; color: var(--muted); cursor: pointer; font-size: 0.75rem; padding: 0.28rem 0.55rem; }
        @media (prefers-color-scheme: dark) {
            :root { --ink: #e7eef1; --muted: #aab9c0; --surface: #18242a; --line: #34474f; --accent-soft: #193e45; }
            .stApp { background: #111a1e; }
            [data-testid="stSidebar"] { background: #162126; }
            [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) { border-color: #2d5e63; }
            [data-testid="stChatInput"] > div { border-color: #3a4f57 !important; }
        }
        @media (max-width: 640px) {
            .block-container { padding: 1.7rem 0.8rem 7rem; }
            [data-testid="stChatMessage"] { max-width: 94%; }
            h1 { font-size: 1.65rem !important; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def reset_chat() -> None:
    if BasicAgent is not None:
        st.session_state.agent = BasicAgent(name="Bukhari Chat Bot")
    st.session_state.messages = [{"role": "assistant", "content": WELCOME_MESSAGE}]


def response_user(response: object) -> object:
    return getattr(response, "user", None)


def show_authentication(service: SupabaseService) -> None:
    if "user" in st.session_state and st.session_state.user:
        user = st.session_state.user
        st.markdown(f"Signed in as **{user.email}**")
        if st.button("Log out", use_container_width=True):
            service.sign_out()
            for key in ("user", "history_rows", "history_loaded_user"):
                st.session_state.pop(key, None)
            reset_chat()
            st.rerun()
        return

    mode = st.radio("Account", ["Log in", "Sign up"], horizontal=True)
    with st.form("auth-form"):
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button(mode, use_container_width=True)

    if not submitted:
        return
    if not email.strip() or len(password) < 6:
        st.error("Enter a valid email and a password with at least 6 characters.")
        return

    try:
        result = service.sign_in(email.strip(), password) if mode == "Log in" else service.sign_up(email.strip(), password)
        user = response_user(result)
        if user is None:
            st.success("Account created. Check your email to confirm it, then log in.")
        else:
            st.session_state.user = user
            st.session_state.pop("history_loaded_user", None)
            st.rerun()
    except Exception as exc:
        st.error(f"Authentication failed: {exc}")


def render_copy_button(content: str, key: str) -> None:
    del key
    copy_text = html.escape(json.dumps(content), quote=True)
    components.html(
        f"""
        <button class="copy-response" onclick="navigator.clipboard.writeText({copy_text})">
            Copy response
        </button>
        """,
        height=38,
    )


current_user_id = None
if ENABLE_SUPABASE_AUTH:
    if "supabase" not in st.session_state:
        try:
            st.session_state.supabase = get_supabase_service()
        except SupabaseConfigurationError as exc:
            st.error(str(exc))
            st.info("Add SUPABASE_URL and SUPABASE_KEY to .env or Streamlit secrets, then restart the app.")
            st.stop()

    with st.sidebar:
        st.markdown('<div class="sidebar-brand">Bukhari Chat Bot</div>', unsafe_allow_html=True)
        st.markdown('<p class="sidebar-note">Sign in to save and revisit your conversations.</p>', unsafe_allow_html=True)
        show_authentication(st.session_state.supabase)

    if "user" not in st.session_state:
        st.info("Log in or create an account from the sidebar to start chatting.")
        st.stop()

if BasicAgent is None:
    st.error(f"Unable to start the agent: {IMPORT_ERROR}")
    st.info("Add your GEMINI_API_KEY to the project-root .env file and restart the app.")
    st.stop()

if ENABLE_SUPABASE_AUTH:
    current_user_id = st.session_state.user.id
    if st.session_state.get("history_loaded_user") != current_user_id:
        try:
            st.session_state.history_rows = st.session_state.supabase.history(current_user_id)
            st.session_state.history_loaded_user = current_user_id
        except Exception as exc:
            st.error(f"Unable to load chat history: {exc}")
            st.session_state.history_rows = []

if "agent" not in st.session_state:
    st.session_state.agent = BasicAgent(name="Bukhari Chat Bot")
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": WELCOME_MESSAGE}]

with st.sidebar:
    if st.button("✦  New chat", use_container_width=True):
        reset_chat()
        st.rerun()
    if ENABLE_SUPABASE_AUTH:
        st.markdown("**Previous chats**")
        history_rows = st.session_state.get("history_rows", [])
        if not history_rows:
            st.caption("Your saved chats will appear here.")
        for history_index, row in enumerate(reversed(history_rows)):
            label = row.get("message", "Untitled chat").strip() or "Untitled chat"
            label = label[:42] + ("..." if len(label) > 42 else "")
            if st.button(label, key=f"history-{history_index}-{row.get('id', '')}", use_container_width=True):
                st.session_state.messages = [
                    {"role": "user", "content": row.get("message", "")},
                    {"role": "assistant", "content": row.get("response", "")},
                ]
                st.rerun()
    st.divider()
    st.markdown("**Voice input**")
    st.audio_input("Record a voice note", key="voice_note")
    st.caption("Voice notes are captured here. Text transcription needs a speech-to-text service.")
    st.divider()
    st.caption("Powered by Gemini")

st.markdown('<div class="app-kicker">Personal AI workspace</div>', unsafe_allow_html=True)
st.title("Bukhari Chat Bot")
st.markdown('<p class="app-subtitle">Ask a question, attach an image, and keep the conversation flowing.</p>', unsafe_allow_html=True)

for index, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        if message.get("image"):
            st.image(message["image"], caption="Attached image", use_container_width=True)
        st.markdown(message["content"])
        if message["role"] == "assistant":
            render_copy_button(message["content"], f"copy-{index}")

chat_event = st.chat_input(
    "Message Bukhari Chat Bot...",
    accept_file=True,
    file_type=["jpg", "jpeg", "png", "webp"],
)

if chat_event:
    if isinstance(chat_event, str):
        prompt = chat_event
        attached_files = []
    else:
        prompt = chat_event.get("text", "")
        attached_files = chat_event.get("files", [])

    attached_file = attached_files[0] if attached_files else None
    image_data = attached_file.getvalue() if attached_file else None
    image_mime_type = attached_file.type if attached_file else None
    if not prompt.strip() and not image_data:
        st.warning("Write a message or attach an image first.")
        st.stop()

    user_message = {"role": "user", "content": prompt or "Tell me about this image."}
    if image_data:
        user_message["image"] = image_data
    st.session_state.messages.append(user_message)
    with st.chat_message("user"):
        if image_data:
            st.image(image_data, caption="Attached image", use_container_width=True)
        st.markdown(user_message["content"])

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.agent.respond(prompt, image_data, image_mime_type)
        st.markdown(response)
        render_copy_button(response, f"copy-live-{len(st.session_state.messages)}")
    st.session_state.messages.append({"role": "assistant", "content": response})
    if ENABLE_SUPABASE_AUTH:
        try:
            st.session_state.supabase.save_chat(current_user_id, user_message["content"], response)
            st.session_state.history_rows.append(
                {"message": user_message["content"], "response": response, "timestamp": "now"}
            )
        except Exception as exc:
            st.warning(f"Response generated, but chat history could not be saved: {exc}")
