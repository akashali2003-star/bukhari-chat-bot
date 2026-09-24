from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import google.generativeai as genai
from dotenv import load_dotenv

try:
    import streamlit as st
except ImportError:  # pragma: no cover - only needed for Streamlit deployment
    st = None

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key and st is not None:
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        api_key = None

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. Add GEMINI_API_KEY=... to the project .env file or set it in Streamlit Cloud secrets."
    )

genai.configure(api_key=api_key)


@dataclass
class ChatMessage:
    role: str
    content: str


class BasicAgent:
    def __init__(self, name: str = "Bukhari Chat Bot") -> None:
        self.name = name
        self.history: List[ChatMessage] = []
        self.model = genai.GenerativeModel("gemini-3.6-flash")
        self.chat = self.model.start_chat(history=[])

    def respond(
        self,
        prompt: str,
        image_data: Optional[bytes] = None,
        image_mime_type: Optional[str] = None,
    ) -> str:
        cleaned = (prompt or "").strip()
        if not cleaned and image_data is None:
            return "I'm ready when you are."

        try:
            message_parts = [cleaned or "Please describe this image."]
            if image_data is not None:
                message_parts.append(
                    {
                        "mime_type": image_mime_type or "image/jpeg",
                        "data": image_data,
                    }
                )
            response = self.chat.send_message(message_parts)
            return response.text
        except Exception as e:
            return f"Error: {e}"

    def add_message(self, role: str, content: str) -> None:
        self.history.append(ChatMessage(role=role, content=content))