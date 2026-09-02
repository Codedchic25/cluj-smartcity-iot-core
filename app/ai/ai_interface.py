"""Intelligent AI interface component ensuring session persistence against dashboard auto-refresh loops."""

from __future__ import annotations

import streamlit as st

from app.ai.groq_provider import GroqProvider


def get_latest_alerts_context(limit_lines: int = 5) -> str:
    """Extract last historical lines from security log to provide contextual awareness to Qwen."""
    import os

    log_path = "security_alerts.log"
    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()[-limit_lines:]
                return "".join(lines)
        except IOError:
            pass
    return "No active security breach events logged."


def render_ai_assistant(
    location: str,
    temperature: float,
    air_quality: float,
    soil_moisture: float,
    translations: dict[str, str],
) -> None:
    """Render the localized intelligent LLM advisory card component with dynamic session persistence."""
    st.markdown("---")
    st.subheader(f"🧠 {translations.get('ai_assistant', 'Asistent Urban Inteligent (LLM)')}")

    prompt_template_path = "ai_tests/prompts.txt"
    try:
        with open(prompt_template_path, "r", encoding="utf-8") as prompt_file:
            prompt_template = prompt_file.read()
    except IOError:
        st.error("❌ Fișierul de șabloane pentru prompturi 'ai_tests/prompts.txt' nu a fost găsit.")
        return

    # --- DEBLOCARE PERSISTENȚĂ ÎMPOTRIVA AUTO-REFRESH-ULUI ---
    # Creăm o cheie unică în sesiune bazată pe locație pentru a nu se suprapune datele pe pagini diferite
    session_key = f"persistent_ai_response_{location.replace(' ', '_')}"
    if session_key not in st.session_state:
        st.session_state[session_key] = None

    active_lang = st.session_state.get("lang", "RO")
    historical_alerts_log = get_latest_alerts_context(limit_lines=5)

    # Ingestia dinamică a contextului de securitate live direct în structura de prompt
    rendered_prompt = (
        prompt_template.replace("{{locatie}}", location)
        .replace("{{temperature}}", f"{temperature:.1f}")
        .replace("{{air_quality}}", f"{air_quality:.1f}")
        .replace("{{soil_moisture}}", f"{soil_moisture:.1f}")
        .replace("{{limba_activa}}", active_lang)
        .replace("{{jurnal_alerte_recente}}", historical_alerts_log)
    )
    # Definirea butonului cu cheie unică
    if st.button(
        translations.get("generate_rec", "✨ Generează Recomandare Urbană"),
        type="secondary",
        key=f"ai_generate_btn_{location.replace(' ', '_')}",
    ):
        with st.spinner(
            translations.get("loading_ai", "Se analizează datele senzorilor urbani...")
        ):
            try:
                # Inițializăm providerul nativ securizat
                provider = GroqProvider()

                # Apelăm modelul qwen/qwen3.6-27b prin clientul Groq pur
                response_text = provider.generate_completion(rendered_prompt)

                if response_text and not response_text.startswith("❌"):
                    # Salvăm răspunsul în starea sesiunii pentru a rezista reîmprospătării automate
                    st.session_state[session_key] = response_text
                else:
                    st.warning(
                        "⚠️ Serverul Groq a returnat un răspuns gol sau o eroare de conexiune."
                    )

            except Exception as exc:
                st.error(
                    f"❌ Eroare la conexiunea cu API-ul Groq: {exc}. "
                    "Asigură-te că valoarea GROQ_API_KEY este definită corect în fișierul local `.env`."
                )

    # --- RANDARE PERSISTENTĂ A CARDULUI AI ---
    # Dacă în sesiune există un răspuns generat anterior, îl afișăm permanent pe ecran
    if st.session_state[session_key]:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.chat_message("assistant", avatar="🧠"):
            st.markdown(
                f"**{translations.get('ai_recommendation_label', 'Recomandare Operativă (Cluj-Napoca):')}**\n\n"
                f"{st.session_state[session_key]}"
            )

# ============================================================================
# COMPONENTĂ UNIFICATĂ — BARA LATERALĂ GLOBALĂ (SIDEBAR)
# ============================================================================
def render_full_global_sidebar(translations: dict[str, str]) -> str:
    """Randează bara laterală globală completă (Limbi, Operator, Senzori) - Versiune Stabilizată Production."""
    import sqlite3
    import os
    import pandas as pd
    from pathlib import Path

    # Extinderea completă a rețelei de senzori urbani pentru Cluj-Napoca (Aliniat cu seed_db)
    fallback_sensors = [
        "Parcul Central - Spații Verzi",
        "Mărăști - Sens Giratoriu",
        "Mănăștur - Str. Primăverii",
        "Zorilor - Str. Observatorului",
        "Gheorgheni - Iulius Mall",
        "Zorilor Sud - Spitalul Recuperare",
        "Piața Unirii - Centru Istoric",
        "Grigorescu - Malul Someșului"
    ]
    sensor_names = []
    database_path = Path(os.environ.get("DATABASE_PATH", "app.db"))
    
    if database_path.exists():
        try:
            with sqlite3.connect(database_path, timeout=5) as connection:
                df = pd.read_sql_query("SELECT name FROM sensors ORDER BY id", connection)
                if not df.empty:
                    sensor_names = df["name"].tolist()
        except Exception:
            pass

    if not sensor_names:
        sensor_names = fallback_sensors

    # Sincronizăm indexul inițial bazat pe valoarea existentă în widget (dacă există)
    if "global_sensor_selectbox_widget" not in st.session_state:
        current_index = 0
    else:
        try:
            current_index = sensor_names.index(st.session_state["global_sensor_selectbox_widget"])
        except ValueError:
            current_index = 0

    with st.sidebar:
        # A. Schimbare Limbă
        def global_lang_callback():
            st.session_state["lang"] = st.session_state["global_language_widget"]

        supported_languages = ["RO", "EN", "IT", "ES", "HU"]
        st.selectbox(
            translations.get("language_select", "🌐 Schimbă limba / Change language"),
            options=supported_languages,
            index=supported_languages.index(st.session_state.get("lang", "RO")),
            key="global_language_widget",
            on_change=global_lang_callback,
        )
        st.divider()

        # B. Card Premium Operator
        user_full_name = os.environ.get("OPERATOR_FULL_NAME", "Cojocaru Maria Gabriela")
        st.markdown(
            f"""
            <div style="background-color: #111525; padding: 15px; border-radius: 8px; border: 1px solid #000080; margin-bottom: 10px; width: 100%;">
                <span style="color: #888; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px;">👤 {translations.get('operator_label', 'Operator Sistem')}</span>
                <div style="color: white; font-size: 1.05rem; font-weight: bold; margin-top: 4px; line-height: 1.2;">{user_full_name}</div>
                <div style="display: inline-block; background-color: #000080; color: white; font-size: 0.7rem; font-weight: bold; padding: 3px 8px; border-radius: 4px; margin-top: 8px; letter-spacing: 0.5px;">
                     🚀 Lead Cloud & Software Engineer
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # C. Deconectare
        if st.session_state.get("authenticated", False):
            if st.button(translations.get("logout_btn", "🚫 Deconectare"), type="secondary", use_container_width=True, key="global_logout_btn"):
                st.session_state["authenticated"] = False
                st.rerun()
            st.divider()

        # D. Selector Stații Extins
        selected_sensor = st.selectbox(
            f"📍 {translations.get('select_station_adv', 'Selectează Cartier / Zonă IoT')}",
            options=sensor_names,
            index=current_index,
            key="global_sensor_selectbox_widget"
        )
        
    return selected_sensor
