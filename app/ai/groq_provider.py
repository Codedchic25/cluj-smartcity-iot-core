"""Core API client wrapper for local Groq cloud provider execution endpoints."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

# Încercăm să încărcăm din calea calculată, dar adăugăm și o încărcare simplă din directorul curent de rulare
ENV_PATH = Path(__file__).parent.parent.parent / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()  # Caută automat .env în directorul din care ai rulat comanda promptfoo


class GroqProvider:
    """Secure client orchestrator managing dynamic token evaluation via Groq API."""

    def __init__(self) -> None:
        """Initialize the inner Groq SDK engine using local environment tokens."""
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            self.client = None
            return

        # Configurare client cu timeout nativ global integrat direct în constructorul SDK-ului
        self.client = Groq(api_key=self.api_key, timeout=10.0)

        # 🔄 REPARARE COMPARTIMENTATĂ: Modelul de mare viteză și precizie setat în siguranță
        self.model_name = "qwen/qwen3.6-27b"

    def generate_completion(self, prompt_body: str) -> str:
        """Execute text inference and return structural recommendations safely."""
        if not self.client:
            return (
                "⚠️ [OFFLINE ENGINE] API Key lipsă în fișierul `.env`.\n"
                "Sistemul Smart City Cluj rulează local în regim izolat."
            )

        try:
            # Apel de inferență protejat împotriva latențelor lungi de rețea
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt_body,
                    }
                ],
                model=self.model_name,
                temperature=0.2,
                max_tokens=256,
            )

            response = chat_completion.choices[0].message.content
            if response and response.strip():
                return response.strip()

            return "⚠️ [LLM EMPTY RESPONSE] Modelul Qwen a returnat un răspuns gol pentru parametrii transmiși."

        except Exception as exc:
            # Înregistrează eroarea și oferă un răspuns sigur care să nu prăbușească UI-ul Streamlit
            return f"❌ [GROQ API ERROR] Conexiune eșuată sau timeout atins: {exc}"


def call_api(prompt: str, options: dict | None = None, context: dict | None = None) -> dict:
    """Entrypoint special obligatoriu pentru integrarea nativă cu platforma Promptfoo."""
    provider = GroqProvider()
    response_text = provider.generate_completion(prompt)
    return {"output": response_text}
