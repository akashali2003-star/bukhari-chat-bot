from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

try:
    import streamlit as st
except ImportError:  # pragma: no cover - used by the terminal client
    st = None

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))


class SupabaseConfigurationError(RuntimeError):
    """Raised when Supabase credentials are not configured."""


def _setting(name: str) -> Optional[str]:
    value = os.getenv(name)
    if value:
        return value
    if st is not None:
        try:
            value = st.secrets.get(name)
        except Exception:
            value = None
    return value


def _project_url(url: str) -> str:
    return url.rstrip("/").removesuffix("/rest/v1")


@dataclass
class SupabaseService:
    client: Any

    @classmethod
    def from_environment(cls) -> "SupabaseService":
        url = _setting("SUPABASE_URL")
        key = _setting("SUPABASE_KEY")
        if not url or not key:
            raise SupabaseConfigurationError(
                "SUPABASE_URL and SUPABASE_KEY are missing. Add them to .env or Streamlit secrets."
            )

        try:
            from supabase import create_client
        except ImportError as exc:  # pragma: no cover - exercised before dependency install
            raise SupabaseConfigurationError(
                "The supabase package is not installed. Run: py -m pip install supabase"
            ) from exc

        return cls(create_client(_project_url(url), key))

    def sign_up(self, email: str, password: str) -> Any:
        return self.client.auth.sign_up({"email": email, "password": password})

    def sign_in(self, email: str, password: str) -> Any:
        return self.client.auth.sign_in_with_password(
            {"email": email, "password": password}
        )

    def sign_in_with_google(self, redirect_to: str) -> Any:
        return self.client.auth.sign_in_with_oauth(
            {
                "provider": "google",
                "options": {"redirect_to": redirect_to},
            }
        )

    def exchange_code_for_session(self, auth_code: str) -> Any:
        return self.client.auth.exchange_code_for_session(auth_code)

    def current_user(self) -> Any:
        return self.client.auth.get_user().user

    def sign_out(self) -> None:
        self.client.auth.sign_out()

    def history(self, user_id: str) -> List[Dict[str, Any]]:
        result = (
            self.client.table("chats")
            .select("id,message,response,timestamp")
            .eq("user_id", user_id)
            .order("timestamp", desc=False)
            .execute()
        )
        return result.data or []

    def save_chat(self, user_id: str, message: str, response: str) -> None:
        self.client.table("chats").insert(
            {"user_id": user_id, "message": message, "response": response}
        ).execute()


def get_supabase_service() -> SupabaseService:
    return SupabaseService.from_environment()
