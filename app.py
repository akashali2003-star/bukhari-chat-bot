from __future__ import annotations

import html
import hashlib
import json
import os

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


WELCOME_MESSAGE = "Assalam-o-Alaikum, Main Jarvis hoon. Aapka sawal likhein, Sir."
ENABLE_SUPABASE_AUTH = True

st.set_page_config(page_title="Jarvis", page_icon="⚡", layout="wide")

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
                themeColor.content = "#07111f";
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
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
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
        :root {
            --ink: #18333a;
            --muted: #6d7d80;
            --surface: #ffffff;
            --surface-soft: #f1f7f6;
            --line: #d9e5e2;
            --accent: #147d92;
            --accent-deep: #0c596b;
            --accent-soft: #dff2f0;
            --coral: #f4a28c;
        }
        html, body, [class*="css"] { font-family: "DM Sans", "Avenir Next", sans-serif; }
        .stApp { background: #f7faf9; background-image: radial-gradient(circle at 88% 8%, rgba(20, 125, 146, 0.08), transparent 24rem); }
        .block-container { max-width: 1080px; padding: 2.2rem 2rem 7.5rem; }
        .app-header { display: flex; align-items: center; gap: 1rem; margin: 0.3rem 0 2rem; }
        .app-header-logo { width: 58px; height: 58px; border-radius: 17px; object-fit: cover; box-shadow: 0 10px 22px rgba(20, 125, 146, 0.2); }
        .app-header-copy { min-width: 0; }
        .app-kicker { color: var(--accent); font-size: 0.68rem; font-weight: 700; letter-spacing: 0.16em; text-transform: uppercase; margin: 0 0 0.3rem; }
        .app-header h1 { color: var(--ink); font-family: "Space Grotesk", "Avenir Next", sans-serif; font-size: clamp(1.65rem, 3vw, 2.35rem); font-weight: 700; line-height: 1.05; margin: 0; }
        .app-subtitle { color: var(--muted); font-size: 0.96rem; margin: 0.45rem 0 0; }
        [data-testid="stSidebar"] { background: #17363d; border-right: 0; }
        [data-testid="stSidebar"] .block-container { padding: 1.35rem 1rem; }
        [data-testid="stSidebar"] .sidebar-brand { color: #f4fbfa; font-family: "Space Grotesk", sans-serif; font-size: 1.05rem; font-weight: 700; }
        [data-testid="stSidebar"] .sidebar-note { color: #a9c2c2; font-size: 0.82rem; line-height: 1.5; }
        .sidebar-brand-row { display: flex; align-items: center; gap: 0.7rem; margin: 0.15rem 0 0.3rem; }
        .sidebar-brand-logo { width: 34px; height: 34px; border: 2px solid rgba(255,255,255,0.35); border-radius: 11px; object-fit: cover; }
        .sidebar-section-label { color: #7fa6a6; font-size: 0.64rem; font-weight: 700; letter-spacing: 0.14em; margin: 1.25rem 0 0.5rem; text-transform: uppercase; }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] label { color: #d6e7e5; }
        [data-testid="stSidebar"] hr { border-color: rgba(214, 231, 229, 0.16); margin: 1.1rem 0; }
        [data-testid="stSidebar"] button { background: rgba(255,255,255,0.08) !important; border: 1px solid rgba(255,255,255,0.13) !important; color: #eef9f7 !important; }
        [data-testid="stSidebar"] button:hover { background: rgba(255,255,255,0.16) !important; border-color: rgba(255,255,255,0.3) !important; }
        [data-testid="stChatMessage"] { border: 1px solid var(--line); border-radius: 20px; margin: 1.05rem 0; padding: 1rem 1.15rem; max-width: 78%; background: var(--surface); box-shadow: 0 10px 28px rgba(24, 51, 58, 0.06); }
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) { background: #e4f3f0; border-color: #c5e3df; border-bottom-right-radius: 7px; }
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) { border-bottom-left-radius: 7px; }
        [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p { color: var(--ink); line-height: 1.7; }
        [data-testid="stChatMessage"] [data-testid="chatAvatarIcon-user"] { background: var(--coral); }
        [data-testid="stChatMessage"] [data-testid="chatAvatarIcon-assistant"] { background: var(--accent); }
        [data-testid="stChatInput"] { border-top: 0 !important; background: transparent !important; margin-top: 1.2rem; }
        [data-testid="stChatInput"] > div { border: 1px solid #bfd4d1 !important; border-radius: 18px !important; background: var(--surface) !important; box-shadow: 0 14px 34px rgba(24, 51, 58, 0.13) !important; padding: 0.3rem 0.45rem 0.3rem 0.85rem !important; transition: border-color 160ms ease, box-shadow 160ms ease !important; }
        [data-testid="stChatInput"] > div:focus-within { border-color: var(--accent) !important; box-shadow: 0 14px 34px rgba(20, 125, 146, 0.18) !important; }
        [data-testid="stChatInput"] textarea { color: var(--ink) !important; font-size: 0.96rem !important; }
        [data-testid="stChatInput"] button { background: var(--accent) !important; border: 0 !important; border-radius: 12px !important; color: white !important; }
        [data-testid="stChatInput"] button:hover { background: var(--accent-deep) !important; }
        .stButton > button, [data-testid="stFormSubmitButton"] button { border: 1px solid #c5d8d5; border-radius: 11px; font-weight: 600; min-height: 2.65rem; transition: transform 160ms ease, box-shadow 160ms ease, background 160ms ease; }
        .stButton > button:hover, [data-testid="stFormSubmitButton"] button:hover { box-shadow: 0 7px 16px rgba(20, 125, 146, 0.15); transform: translateY(-1px); }
        @media (max-width: 640px) {
            .block-container { padding: 1.35rem 0.85rem 7rem; }
            .app-header { margin-bottom: 1.35rem; }
            .app-header-logo { width: 48px; height: 48px; border-radius: 14px; }
            [data-testid="stChatMessage"] { max-width: 94%; }
        }
        @media (prefers-color-scheme: dark) {
            :root { --ink: #e7f2f0; --muted: #aabfc0; --surface: #1b2b30; --line: #385057; --accent-soft: #1d4549; }
            .stApp { background: #101d21; }
            .app-header h1, [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p { color: var(--ink); }
            [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) { border-color: #2d6564; }
            [data-testid="stChatInput"] > div { border-color: #3a5a5c !important; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;600;700&family=Rajdhani:wght@400;500;600;700&display=swap');
        :root {
            color-scheme: dark;
            --ink: #e4f8ff;
            --muted: #8aa9bb;
            --surface: #0b1725;
            --line: rgba(73, 202, 255, 0.24);
            --cyan: #55e7ff;
            --blue: #4b91ff;
            --amber: #ffbd62;
        }
        html, body, [class*="css"] { color: var(--ink); font-family: "Rajdhani", "Segoe UI", sans-serif; }
        .stApp { color: var(--ink); background-color: #050b13; background-image: linear-gradient(rgba(62, 167, 222, 0.035) 1px, transparent 1px), linear-gradient(90deg, rgba(62, 167, 222, 0.035) 1px, transparent 1px), linear-gradient(135deg, #07111f 0%, #081522 52%, #07101b 100%); background-size: 36px 36px, 36px 36px, auto; }
        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stDecoration"] { display: none; }
        .block-container { max-width: 1080px; padding: 2rem 2rem 7.5rem; }
        h1, h2, h3, p, label { letter-spacing: 0; }
        .app-header { display: flex; align-items: center; gap: 1rem; margin: 0.3rem 0 2rem; animation: console-boot 500ms ease-out both; }
        .app-header-logo { width: 58px; height: 58px; border: 1px solid rgba(85, 231, 255, 0.48); border-radius: 15px; object-fit: cover; box-shadow: 0 0 24px rgba(49, 198, 255, 0.2); }
        .app-header-copy { min-width: 0; }
        .app-kicker { color: var(--cyan); font-size: 0.77rem; font-weight: 700; text-transform: uppercase; margin: 0 0 0.35rem; }
        .app-kicker::before { content: ""; display: inline-block; width: 7px; height: 7px; margin: 0 0.55rem 1px 0; border-radius: 50%; background: var(--amber); box-shadow: 0 0 10px rgba(255, 189, 98, 0.8); animation: status-pulse 2.2s ease-in-out infinite; }
        .app-header h1 { color: var(--ink); font-family: "Orbitron", "Segoe UI", sans-serif; font-size: 2.2rem; font-weight: 700; line-height: 1.1; margin: 0; text-shadow: 0 0 18px rgba(85, 231, 255, 0.26); }
        .app-subtitle { color: var(--muted); font-size: 1.08rem; margin: 0.4rem 0 0; }
        [data-testid="stSidebar"] { background: rgba(5, 14, 25, 0.97); border-right: 1px solid var(--line); }
        [data-testid="stSidebar"] .block-container { padding: 1.35rem 1rem; }
        [data-testid="stSidebar"] .sidebar-brand { color: var(--ink); font-family: "Orbitron", sans-serif; font-size: 1.05rem; font-weight: 700; }
        [data-testid="stSidebar"] .sidebar-note { color: var(--muted); font-size: 0.96rem; line-height: 1.4; }
        .sidebar-brand-row { display: flex; align-items: center; gap: 0.7rem; margin: 0.15rem 0 0.3rem; }
        .sidebar-brand-logo { width: 34px; height: 34px; border: 1px solid rgba(85, 231, 255, 0.5); border-radius: 10px; object-fit: cover; box-shadow: 0 0 14px rgba(49, 198, 255, 0.2); }
        .sidebar-section-label { color: var(--cyan); font-size: 0.78rem; font-weight: 700; margin: 1.25rem 0 0.5rem; text-transform: uppercase; }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p, [data-testid="stSidebar"] label { color: #c7dce9; }
        [data-testid="stSidebar"] hr { border-color: var(--line); margin: 1.1rem 0; }
        [data-testid="stSidebar"] button { background: #0b1b2b !important; border: 1px solid var(--line) !important; color: var(--ink) !important; }
        [data-testid="stSidebar"] button:hover { border-color: var(--cyan) !important; box-shadow: 0 0 15px rgba(85, 231, 255, 0.16); }
        [data-testid="stChatMessage"] { border: 1px solid var(--line); border-radius: 12px; margin: 1rem 0; padding: 1rem 1.15rem; max-width: 82%; background: rgba(10, 24, 39, 0.92); box-shadow: 0 0 18px rgba(32, 126, 193, 0.08), inset 0 0 20px rgba(19, 71, 103, 0.08); }
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) { margin-left: auto; background: rgba(15, 39, 62, 0.94); border-color: rgba(75, 145, 255, 0.42); }
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) { margin-right: auto; border-left: 2px solid var(--cyan); }
        [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p { color: var(--ink); line-height: 1.55; font-size: 1.08rem; }
        [data-testid="stChatMessage"] [data-testid="chatAvatarIcon-user"] { background: var(--blue); }
        [data-testid="stChatMessage"] [data-testid="chatAvatarIcon-assistant"] { background: #087a9d; }
        [data-testid="stChatInput"] { border-top: 0 !important; background: transparent !important; margin-top: 1rem; }
        [data-testid="stChatInput"] > div { border: 1px solid rgba(85, 231, 255, 0.34) !important; border-radius: 12px !important; background: #091827 !important; box-shadow: 0 0 22px rgba(21, 148, 207, 0.12) !important; padding: 0.3rem 0.45rem 0.3rem 0.85rem !important; transition: border-color 160ms ease, box-shadow 160ms ease !important; }
        [data-testid="stChatInput"] > div:focus-within { border-color: var(--cyan) !important; box-shadow: 0 0 24px rgba(85, 231, 255, 0.2) !important; }
        [data-testid="stChatInput"] textarea { color: var(--ink) !important; font-size: 1.04rem !important; }
        [data-testid="stChatInput"] button { background: #087a9d !important; border: 1px solid rgba(85, 231, 255, 0.4) !important; border-radius: 9px !important; color: white !important; }
        [data-testid="stChatInput"] button:hover { background: #0b9dc2 !important; box-shadow: 0 0 13px rgba(85, 231, 255, 0.35); }
        .stButton > button, [data-testid="stFormSubmitButton"] button { border: 1px solid var(--line); border-radius: 8px; font-weight: 600; min-height: 2.65rem; transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease; }
        .stButton > button:hover, [data-testid="stFormSubmitButton"] button:hover { border-color: var(--cyan); box-shadow: 0 0 14px rgba(85, 231, 255, 0.18); transform: translateY(-1px); }
        [data-testid="stAudioInput"] { border: 1px solid rgba(85, 231, 255, 0.22); border-radius: 10px; padding: 0.55rem 0.8rem 0.2rem; background: rgba(7, 20, 33, 0.75); }
        @keyframes console-boot { from { opacity: 0; transform: translateY(7px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes status-pulse { 50% { opacity: 0.48; box-shadow: 0 0 4px rgba(255, 189, 98, 0.45); } }
        @media (max-width: 640px) {
            .block-container { padding: 1.35rem 0.85rem 7rem; }
            .app-header { margin-bottom: 1.35rem; gap: 0.75rem; }
            .app-header-logo { width: 48px; height: 48px; }
            .app-header h1 { font-size: 1.75rem; }
            .app-subtitle { font-size: 0.98rem; }
            [data-testid="stChatMessage"] { max-width: 96%; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<header class="app-header"><img class="app-header-logo" src="/app/static/jarvis-icon.svg" alt="Jarvis interface icon"><div class="app-header-copy"><div class="app-kicker">System online</div><h1>Jarvis</h1><p class="app-subtitle">Your intelligent assistant is ready, Sir.</p></div></header>',
    unsafe_allow_html=True,
)


def reset_chat() -> None:
    if BasicAgent is not None:
        st.session_state.agent = BasicAgent(name="Jarvis")
    st.session_state.messages = [{"role": "assistant", "content": WELCOME_MESSAGE}]


def response_user(response: object) -> object:
    return getattr(response, "user", None)


def auth_redirect_url() -> str:
    return os.getenv("SUPABASE_REDIRECT_URL", "http://localhost:8501/app/")


def complete_authentication(user: object) -> None:
    was_guest = st.session_state.get("guest", False)
    st.session_state.user = user
    st.session_state.pop("guest", None)
    st.session_state.pop("history_loaded_user", None)
    if was_guest and any(message["role"] == "user" for message in st.session_state.get("messages", [])):
        st.session_state.show_guest_save_prompt = True


def handle_auth_callback(service: SupabaseService) -> None:
    auth_error = st.query_params.get("error_description")
    auth_code = st.query_params.get("code")
    if auth_error:
        st.error(f"Google sign-in failed: {auth_error}")
        st.query_params.clear()
        return
    if not auth_code or "user" in st.session_state:
        return

    try:
        result = service.exchange_code_for_session(auth_code)
        user = response_user(result) or service.current_user()
        complete_authentication(user)
        st.query_params.clear()
        st.rerun()
    except Exception as exc:
        st.error(f"Unable to complete Google sign-in: {exc}")
        st.query_params.clear()


def google_auth_url(result: object) -> str:
    url = getattr(result, "url", None)
    if url:
        return url
    if isinstance(result, dict):
        return result.get("url", "")
    return ""


def show_authentication(service: SupabaseService) -> None:
    if "user" in st.session_state and st.session_state.user:
        user = st.session_state.user
        st.markdown("<div class='sidebar-section-label'>Account</div>", unsafe_allow_html=True)
        st.markdown(f"Signed in as **{user.email}**")
        if st.button("Log out", use_container_width=True):
            service.sign_out()
            for key in ("user", "history_rows", "history_loaded_user", "show_guest_save_prompt"):
                st.session_state.pop(key, None)
            reset_chat()
            st.rerun()
        return

    if st.session_state.get("guest"):
        st.markdown("<div class='sidebar-section-label'>Guest session</div>", unsafe_allow_html=True)
        st.info("Chat history is not saved in guest mode.")
        if st.button("Sign in to save history", use_container_width=True):
            st.session_state.pop("guest", None)
            st.rerun()
        return

    st.markdown("<div class='sidebar-section-label'>Your account</div>", unsafe_allow_html=True)
    st.markdown("**Sign in to save your chats**")
    st.caption("Use email, Google, or continue as a guest.")
    if st.button("Continue as Guest", use_container_width=True, key="guest-sign-in"):
        st.session_state.guest = True
        reset_chat()
        st.rerun()

    try:
        result = service.sign_in_with_google(auth_redirect_url())
        url = google_auth_url(result)
        if not url:
            st.error("Google sign-in URL was not returned by Supabase.")
        else:
            safe_url = html.escape(url, quote=True)
            st.markdown(
                f'<a href="{safe_url}" target="_self" style="display:block;text-align:center;padding:0.62rem 1rem;border:1px solid rgba(85,231,255,0.34);border-radius:8px;background:#091827;color:#e4f8ff;font-weight:600;text-decoration:none">Continue with Google</a>',
                unsafe_allow_html=True,
            )
    except Exception as exc:
        st.error(f"Google sign-in could not start: {exc}")

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
        session = getattr(result, "session", None)
        if user is None or (mode == "Sign up" and session is None):
            st.success("Account created. Check your email to confirm it, then log in.")
        else:
            complete_authentication(user)
            st.rerun()
    except Exception as exc:
        st.error(f"Authentication failed: {exc}")


def guest_chat_pairs() -> list[tuple[str, str]]:
    messages = st.session_state.get("messages", [])
    return [
        (messages[index]["content"], messages[index + 1]["content"])
        for index in range(len(messages) - 1)
        if messages[index].get("role") == "user"
        and messages[index + 1].get("role") == "assistant"
    ]


def render_guest_save_prompt(service: SupabaseService, user_id: str) -> None:
    if not st.session_state.get("show_guest_save_prompt"):
        return

    st.info("You are signed in. Save this guest chat to your account so you can find it later.")
    save_column, discard_column = st.columns(2)
    with save_column:
        if st.button("Save guest chat", use_container_width=True):
            try:
                for message, response in guest_chat_pairs():
                    service.save_chat(user_id, message, response)
                st.session_state.show_guest_save_prompt = False
                st.success("Guest chat saved to your account.")
            except Exception as exc:
                st.error(f"Could not save guest chat: {exc}")
    with discard_column:
        if st.button("Keep it private", use_container_width=True):
            st.session_state.show_guest_save_prompt = False
            st.rerun()


def render_copy_button(content: str, key: str) -> None:
    del key
    copy_text = html.escape(json.dumps(content), quote=True)
    components.html(
        f"""
        <button style="border:1px solid #24516a;border-radius:7px;background:#091827;color:#a9ccdb;cursor:pointer;font:600 13px Rajdhani,sans-serif;padding:5px 9px" onclick="navigator.clipboard.writeText({copy_text})">
            Copy
        </button>
        """,
        height=38,
    )


def render_listen_button(content: str) -> None:
    speech_text = json.dumps(content, ensure_ascii=False)
    speech_text = speech_text.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    components.html(
        f"""
        <button style="border:1px solid #26738b;border-radius:7px;background:#071b29;color:#74eaff;cursor:pointer;font:600 14px Rajdhani,sans-serif;padding:6px 11px">
            🔊 Listen
        </button>
        <script>
            const listenButton = document.querySelector("button");
            listenButton.addEventListener("click", () => {{
                if (!("speechSynthesis" in window)) {{
                    listenButton.textContent = "Speech unavailable";
                    return;
                }}
                window.speechSynthesis.cancel();
                const utterance = new SpeechSynthesisUtterance({speech_text});
                utterance.lang = navigator.language || "en-US";
                utterance.rate = 1;
                window.speechSynthesis.speak(utterance);
            }});
        </script>
        """,
        height=42,
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

    handle_auth_callback(st.session_state.supabase)
    with st.sidebar:
        st.markdown(
            '<div class="sidebar-brand-row"><img class="sidebar-brand-logo" src="/app/static/jarvis-icon.svg" alt=""><div class="sidebar-brand">Jarvis</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown('<p class="sidebar-note">Personal intelligence system</p>', unsafe_allow_html=True)
        show_authentication(st.session_state.supabase)

    if "user" not in st.session_state and not st.session_state.get("guest"):
        st.info("Log in or create an account from the sidebar to start chatting.")
        st.stop()

if BasicAgent is None:
    st.error(f"Unable to start the agent: {IMPORT_ERROR}")
    st.info("Add your GEMINI_API_KEY to the project-root .env file and restart the app.")
    st.stop()

if ENABLE_SUPABASE_AUTH and "user" in st.session_state:
    current_user_id = st.session_state.user.id
    if st.session_state.get("history_loaded_user") != current_user_id:
        try:
            st.session_state.history_rows = st.session_state.supabase.history(current_user_id)
            st.session_state.history_loaded_user = current_user_id
        except Exception as exc:
            st.error(f"Unable to load chat history: {exc}")
            st.session_state.history_rows = []
    render_guest_save_prompt(st.session_state.supabase, current_user_id)

if "agent" not in st.session_state:
    st.session_state.agent = BasicAgent(name="Jarvis")
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": WELCOME_MESSAGE}]

with st.sidebar:
    st.markdown('<div class="sidebar-section-label">Workspace</div>', unsafe_allow_html=True)
    if st.button("✦  New chat", use_container_width=True):
        reset_chat()
        st.rerun()
    if ENABLE_SUPABASE_AUTH and "user" in st.session_state:
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
    st.divider()
    st.caption("Powered by Gemini")

for index, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        if message.get("image"):
            st.image(message["image"], caption="Attached image", use_container_width=True)
        if message.get("audio"):
            st.audio(message["audio"], format="audio/wav")
        st.markdown(message["content"])
        if message["role"] == "assistant":
            render_copy_button(message["content"], f"copy-{index}")
            render_listen_button(message["content"])

voice_recording = st.audio_input("Ask Jarvis by voice", key="voice_note")
voice_audio_data = voice_recording.getvalue() if voice_recording else None
voice_hash = hashlib.sha256(voice_audio_data).hexdigest() if voice_audio_data else None
new_voice_audio = voice_audio_data if voice_hash and voice_hash != st.session_state.get("processed_voice_hash") else None
if new_voice_audio:
    st.session_state.processed_voice_hash = voice_hash

chat_event = st.chat_input(
    "Message Jarvis, Sir...",
    accept_file=True,
    file_type=["jpg", "jpeg", "png", "webp"],
)

if chat_event or new_voice_audio:
    if chat_event is None:
        prompt = ""
        attached_files = []
    elif isinstance(chat_event, str):
        prompt = chat_event
        attached_files = []
    else:
        prompt = chat_event.get("text", "")
        attached_files = chat_event.get("files", [])

    attached_file = attached_files[0] if attached_files else None
    image_data = attached_file.getvalue() if attached_file else None
    image_mime_type = attached_file.type if attached_file else None
    if not prompt.strip() and not image_data and not new_voice_audio:
        st.warning("Write a message or attach an image first.")
        st.stop()

    user_content = prompt or ("Voice question" if new_voice_audio else "Tell me about this image.")
    user_message = {"role": "user", "content": user_content}
    if image_data:
        user_message["image"] = image_data
    if new_voice_audio:
        user_message["audio"] = new_voice_audio
    st.session_state.messages.append(user_message)
    with st.chat_message("user"):
        if image_data:
            st.image(image_data, caption="Attached image", use_container_width=True)
        if new_voice_audio:
            st.audio(new_voice_audio, format="audio/wav")
        st.markdown(user_message["content"])

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.agent.respond(
                prompt,
                image_data,
                image_mime_type,
                new_voice_audio,
                voice_recording.type if voice_recording and new_voice_audio else None,
            )
        st.markdown(response)
        render_copy_button(response, f"copy-live-{len(st.session_state.messages)}")
        render_listen_button(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
    if ENABLE_SUPABASE_AUTH and current_user_id:
        try:
            st.session_state.supabase.save_chat(current_user_id, user_content, response)
            st.session_state.history_rows.append(
                {"message": user_content, "response": response, "timestamp": "now"}
            )
        except Exception as exc:
            st.warning(f"Response generated, but chat history could not be saved: {exc}")
