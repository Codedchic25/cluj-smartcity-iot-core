"""About and system architecture documentation page with unified sidebar layout."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

from translations import TRANSLATIONS

# ============================================================================
# Configuration & Paths — CORECTAT PENTRU RAILWAY/LINUX
# ============================================================================
DATABASE_PATH = Path(os.environ.get("DATABASE_PATH", "app.db"))
def main() -> None:
    """Render system architecture documentation and engineer portfolio details."""
    st.set_page_config(page_title="Smart City Cluj - About", page_icon="ℹ️", layout="wide")

    # Forțăm verificarea identității operatorului prin starea sesiunii din main.py
    if not st.session_state.get("authenticated", False):
        st.warning("🔒 Acces restricționat! Vă rugăm să vă autentificați pe pagina principală (main).")
        st.stop()

    current_lang = st.session_state.get("lang", "RO")
    t = TRANSLATIONS.get(current_lang, TRANSLATIONS["RO"])

    # ASIGURAT: Apelăm funcția centralizată din main.py pentru consecvența barei laterale
    from app.ai.ai_interface import render_full_global_sidebar
    selected_sensor = render_full_global_sidebar(t)

    # Actualizăm traducerile în caz de comutare a limbii din widget
    t = TRANSLATIONS.get(st.session_state.get("lang", "RO"), TRANSLATIONS["RO"])

    st.title(f"ℹ️ {t.get('about_title', 'Despre Platformă & Arhitectură')}")
    st.caption(f"🚀 {t.get('subtitle', 'Monitorizare urbană în timp real, IoT și Inteligență Artificială')} | {selected_sensor}")
    st.divider()

    # Extragem ultimele date pentru cartierul selectat pentru a le trimite la asistentul AI de la subsol
    query_sensor_id = "SELECT id FROM sensors WHERE name = ? LIMIT 1"
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            row = conn.execute(query_sensor_id, (selected_sensor,)).fetchone()
            sensor_id = int(row) if row else 1
            
            query_data = """
                SELECT temperature, air_quality, soil_moisture
                FROM city_stats WHERE sensor_id = ? ORDER BY timestamp DESC LIMIT 1
            """
            df_about = pd.read_sql_query(query_data, conn, params=(sensor_id,))
    except Exception:
        df_about = pd.DataFrame()

    if not df_about.empty:
        latest_telemetry = df_about.iloc[0]
        temp_act = float(latest_telemetry["temperature"])
        air_act = float(latest_telemetry["air_quality"])
        soil_act = float(latest_telemetry["soil_moisture"])
    else:
        temp_act, air_act, soil_act = 25.0, 35.0, 50.0

    # --- STRUCTURA PGINII DE DOCUMENTAȚIE TEHNICĂ ---
    col_doc1, col_doc2 = st.columns(2)

    with col_doc1:
        with st.container(border=True):
            st.markdown("### 🛠️ Stack Tehnologic & Implementare")
            st.markdown(
                """
                Această platformă reprezintă un ecosistem complet dezvoltat pentru monitorizarea indicatorilor urbani, optimizat pentru performanță și scalabilitate modulară:
                - **Frontend / UI:** `Streamlit Framework` (Configurat în mod Multipage nativ).
                - **Data Processing:** `Pandas` și `NumPy` pentru manipularea vectorizată a matricelor informaționale.
                - **Sistem de Stocare:** `SQLite Embedded Engine` (Arhitectură de conexiune sincronă stabilizată).
                - **Corelații și Predicții ML:** Modele matematice predictive rulante `Numpy Polyfit` (Regresie Liniară Simplă).
                - **Integrare Inteligență Artificială:** Interfațare prin `Groq Cloud LLM API` cu comutare dinamică de context lingvistic.
                """
            )

    with col_doc2:
        with st.container(border=True):
            st.markdown("### 👤 Informații Dezvoltator & Portofoliu")
            st.markdown(
                """
                **Nume Operator Principal:** `Cojocaru Maria Gabriela`
                - **Rol Profesional:** `Lead Cloud & Software Engineer`
                - **Arhitectură Proiect:** Modulară, optimizată DevOps pentru testare continuă, izolare de instanțe și implementare automată (*Railway Cloud Engine*).
                - **Scop Platformă:** Centru de control unificat conceput ca aplicație demonstrativă premium de portofoliu avansat, integrând baze de date, analiză statistică ML și inteligență artificială aplicată.
                """
            )

    st.divider()

    # --- ASISTENTUL AI LA SUBSOL CU DATE DE TELEMETRIE ŞI TRADUCERI INTACTE ---
    from app.ai.ai_interface import render_ai_assistant
    with st.expander(f"🤖 {t.get('ai_assistant_tab', 'Asistent Urban Inteligent AI (Groq/LLM)')}"):
        render_ai_assistant(
            location=f"{selected_sensor} - Modul Documentație Proiect",
            temperature=temp_act,
            air_quality=air_act,
            soil_moisture=soil_act,
            translations=t
        )
        
    st.divider()
    st.info(f"✨ {t.get('portfolio_footer_text', 'Proiect avansat dezvoltat de Cojocaru Maria Gabriela — Arhitectură modulară optimizată DevOps pentru testare și portofoliu.')}")


if __name__ == "__main__":
    main()
