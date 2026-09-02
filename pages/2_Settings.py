"""Settings and administration page for the Smart City Cluj-Napoca IoT platform."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

from app.ai.ai_interface import render_ai_assistant
from translations import TRANSLATIONS  # Importăm dicționarul oficial multi-limbă

# ============================================================================
# Configuration & Paths — CORECTAT PENTRU RAILWAY/LINUX
# ============================================================================
DATABASE_PATH = Path(os.environ.get("DATABASE_PATH", "app.db"))
SUPPORTED_LANGUAGES = ["RO", "EN", "IT", "ES", "HU"]

# ============================================================================
# Database Extraction Engines (Synchronous & Native)
# ============================================================================


def get_historical_data_export() -> pd.DataFrame:
    """Extract full multi-station indexing history for analytical extraction."""
    query = """
        SELECT
            c.timestamp,
            s.name AS sensor,
            c.temperature,
            c.noise_level,
            c.traffic_load,
            c.air_quality,
            c.soil_moisture
        FROM city_stats AS c
        JOIN sensors AS s ON c.sensor_id = s.id
        ORDER BY c.timestamp DESC
    """
    try:
        with sqlite3.connect(DATABASE_PATH, timeout=10) as connection:
            dataframe = pd.read_sql_query(query, connection)
        return dataframe
    except sqlite3.Error:
        return pd.DataFrame()


def get_all_sensors_sync() -> pd.DataFrame:
    """Fetch complete sensory instrumentation ledger records from the local network."""
    from main import run_automatic_seeding
    run_automatic_seeding()
    
    query = "SELECT id, name, latitude, longitude FROM sensors ORDER BY id"
    try:
        with sqlite3.connect(DATABASE_PATH) as connection:
            return pd.read_sql_query(query, connection)
    except sqlite3.Error:
        return pd.DataFrame()


def get_alert_thresholds_sync() -> tuple[float, float, float, float]:
    """Preia pragurile administrative ocolind complet structurile asincrone."""
    query = (
        "SELECT temp_limit, noise_limit, air_limit, soil_limit FROM settings WHERE id = 1 LIMIT 1"
    )
    try:
        with sqlite3.connect(DATABASE_PATH) as connection:
            row = connection.execute(query).fetchone()
            if row:
                return (float(row[0]), float(row[1]), float(row[2]), float(row[3]))
    except sqlite3.Error:
        pass
    return (32.0, 75.0, 50.0, 20.0)
def main() -> None:
    """Execute master administration parameters allocation interfaces."""
    st.set_page_config(page_title="Smart City Cluj - Settings", page_icon="⚙️", layout="wide")

    # Forțăm verificarea identității operatorului prin starea sesiunii din main.py
    if not st.session_state.get("authenticated", False):
        st.warning("🔒 Acces restricționat! Vă rugăm să vă autentificați pe pagina principală (main).")
        st.stop()

    if "lang" not in st.session_state:
        st.session_state["lang"] = "RO"

    lang = st.session_state["lang"]
    if lang not in SUPPORTED_LANGUAGES:
        lang = "RO"

    t = TRANSLATIONS.get(lang, TRANSLATIONS["RO"])

    # ASIGURAT: Apelăm funcția unificată din main.py pentru consecvența completă a barei laterale
    from app.ai.ai_interface import render_full_global_sidebar
    _ = render_full_global_sidebar(t)

    # Re-inițializare pachet de limbi după închiderea blocului sidebar în caz de comutare
    t = TRANSLATIONS.get(st.session_state["lang"], TRANSLATIONS["RO"])

    st.title(f"⚙️ {t.get('settings_title', 'Administrare Sistem Urban')}")
    st.markdown(
        f"*{t.get('subtitle', 'Monitorizare urbană în timp real, IoT și Inteligență Artificială')}*"
    )
    st.divider()

    # Preluăm pragurile administrative din baza de date pentru a le afișa live
    temperature_limit, noise_limit, air_limit, soil_limit = get_alert_thresholds_sync()

    # --- RANDARE CARDURI DE ALERTĂ TRADUSE SIMETRIC (5 COLOANE) ---
    col_temp, col_noise, col_trafic, col_air, col_soil = st.columns(5)

    with col_temp:
        st.metric(label=t.get("temp", "🌡️ Temperatură"), value=f"{temperature_limit:.1f} °C")

    with col_noise:
        st.metric(label=t.get("noise", "🔊 Nivel Zgomot"), value=f"{noise_limit:.1f} dB")

    with col_trafic:
        st.metric(label=t.get("traffic", "🚗 Trafic Rutier"), value="40%")

    with col_air:
        st.metric(
            label=t.get("air_quality", "🌫️ Calitate Aer (PM2.5)"), value=f"{air_limit:.1f} PM2.5"
        )

    with col_soil:
        st.metric(label=t.get("soil_moisture", "🌱 Umiditate Sol"), value=f"{soil_limit:.1f} %")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Mapare dinamică a tab-urilor administrative pe cheile din translations.py
    tab_alerts, tab_sensors, tab_export = st.tabs(
        [
            f"🔔 {t.get('tab_alerts_cfg', '🔔 Praguri Alerte')}",
            f"📡 {t.get('tab_sensors_cfg', '📡 Rețea Senzori')}",
            f"📂 {t.get('tab_export_cfg', '📂 Export & Rapoarte')}",
        ]
    )

    with tab_alerts:
        st.subheader(t.get("sub_crit_cfg", "⚙️ Configurare Praguri Critice"))

        new_temp = st.slider(
            f"{t.get('temp', '🌡️ Temperatură')} (°C)", 15.0, 45.0, temperature_limit
        )
        new_noise = st.slider(f"{t.get('noise', '🔊 Nivel Zgomot')} (dB)", 30.0, 110.0, noise_limit)
        st.slider(f"{t.get('traffic', '🚗 Trafic Rutier')} (%)", 10.0, 100.0, 40.0)
        new_air = st.slider(
            f"{t.get('air_quality', '🌫️ Calitate Aer')} (PM2.5)", 10.0, 150.0, air_limit
        )
        new_soil = st.slider(
            f"{t.get('soil_moisture', '🌱 Umiditate Sol')} (%)", 10.0, 80.0, soil_limit
        )

        if st.button(
            "💾 Salvează noile praguri de siguranță",
            type="primary",
            key=f"save_alert_thresholds_tab_alerts_{lang}",
        ):
            try:
                with sqlite3.connect(DATABASE_PATH) as conn:
                    conn.execute(
                        """
                        UPDATE settings
                        SET temp_limit = ?, noise_limit = ?, air_limit = ?, soil_limit = ?
                        WHERE id = 1
                        """,
                        (new_temp, new_noise, new_air, new_soil),
                    )
                    conn.commit()
                st.success("✅ Pragurile administrative au fost actualizate cu succes!")
                st.rerun()
            except sqlite3.Error as e:
                st.error(f"Eroare la salvarea pe disc: {e}")

    with tab_sensors:
        st.subheader(f"📡 {t.get('tab_sensors_cfg', 'Gestiune Noduri Rețea')}")

        sensors_df = get_all_sensors_sync()

        if not sensors_df.empty:
            st.dataframe(sensors_df, width="stretch", hide_index=True)
        else:
            st.info("Nu există noduri de senzori înregistrate în sistem.")

        st.divider()
        st.markdown(
            f"##### {t.get('form_register', '➕ Înregistrare și Configurare Nod IoT Complet')}"
        )

        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            toate_cartierele = [
                "Centru", "Mănăștur", "Mărăști", "Zorilor", "Gheorgheni",
                "Grigorescu", "Bună Ziua", "Andrei Mureșanu", "Iris",
                "Dâmbul Rotund", "Someșeni", "Bulgaria", "Între Lacuri",
                "Borhanci", "Sopor", "Parc Tehnologic Tetarom",
                "Zona Metropolitană - Florești", "Zona Metropolitană - Apahida"
            ]
            cartier_selectat = st.selectbox(
                t.get("form_name", "Selectează Cartier / Zonă IoT"),
                options=toate_cartierele,
                index=0,
                key="settings_sensor_name_ext",
            )

        with row1_col2:
            toate_tipurile_metrici = [
                "Stație Completă (Multi-Senzor Telemetry)",
                "Nod Dedicat Calitate Aer (PM2.5 / PM10)",
                "Nod Monitorizare Trafic & Mobilitate",
                "Senzor Acustic (Poluare Fonică & Zgomot)",
                "Nod Agrometeorologic (Umiditate Sol & Microclimat)"
            ]
            tip_selectat = st.selectbox(
                t.get("form_type", "Tip Metric IoT Principal Monitorizat"),
                options=toate_tipurile_metrici,
                index=0,
                key="settings_sensor_type_ext",
            )

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button(
            "💾 Înregistrează noul nod IoT în rețea",
            type="primary",
            key=f"register_new_sensor_node_{lang}",
        ):
            try:
                nou_lat, nou_lon = 46.7704, 23.5914
                nume_complet_nod = f"{cartier_selectat} - {tip_selectat.split(' (')}"

                with sqlite3.connect(DATABASE_PATH) as conn:
                    conn.execute(
                        "INSERT INTO sensors (name, latitude, longitude) VALUES (?, ?, ?)",
                        (nume_complet_nod, nou_lat, nou_lon),
                    )
                    conn.commit()
                st.success(f"✅ Nodul '{nume_complet_nod}' a fost înregistrat cu succes!")
                st.rerun()
            except sqlite3.Error as e:
                st.error(f"Eroare tehnică la salvarea modificărilor: {e}")

    with tab_export:
        st.subheader(f"📂 {t.get('tab_export_cfg', 'Generare Documente Oficiale')}")
        df_export = get_historical_data_export()

        if not df_export.empty:
            st.dataframe(df_export.head(10), width="stretch", hide_index=True)
            csv_data = df_export.to_csv(index=False).encode("utf-8")

            st.download_button(
                label=f"{t.get('pdf_button', '📥 Descarcă Raport Format Executiv')}",
                data=csv_data,
                file_name="smart_city_cluj_data.csv",
                mime="text/csv",
                key="download_csv_settings",
            )
        else:
            st.warning("Nu există date istorice înregistrate disponibile pentru export.")

    st.divider()

    # --- ASISTENTUL AI LA SUBSOL CU DATELE DE CONTROL ACTIVE ---
    from app.ai.ai_interface import render_ai_assistant
    with st.expander(f"🤖 {t.get('ai_assistant_tab', 'Asistent Urban Inteligent AI (Groq/LLM)')}"):
        render_ai_assistant(
            location="Centru - Panou Control Administrare",
            temperature=temperature_limit,
            air_quality=air_limit,
            soil_moisture=soil_limit,
            translations=t
        )
        
    st.divider()
    st.info(f"✨ {t.get('portfolio_footer_text', 'Proiect avansat dezvoltat de Cojocaru Maria Gabriela — Arhitectură modulară optimizată DevOps pentru testare și portofoliu.')}")


if __name__ == "__main__":
    main()
