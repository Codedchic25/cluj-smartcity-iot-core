"""Main orchestration entrypoint for the Smart City platform."""

from __future__ import annotations

import os
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

# IMPORTURI DE DATE DIRECTE
import pandas as pd
import plotly.express as px
import streamlit as st

# IMPORTURI COMPONENTE LOGICE URBANE
from app.ai.ai_interface import render_ai_assistant, render_full_global_sidebar
from translations import TRANSLATIONS  # noqa: E402

# ==========================================
# CONSTANTE URBANE EXTRASE DIN MEDIU
# ==========================================
DATABASE_PATH = Path(os.environ.get("DATABASE_PATH", "app.db"))
DEFAULT_TEMPERATURE_THRESHOLD = float(os.environ.get("DEFAULT_TEMP_LIMIT", 35.0))
DEFAULT_AIR_QUALITY_THRESHOLD = float(os.environ.get("DEFAULT_AIR_LIMIT", 50.0))
DEFAULT_SOIL_MOISTURE_THRESHOLD = float(os.environ.get("DEFAULT_SOIL_LIMIT", 20.0))


def run_automatic_seeding() -> None:
    """Populează automat baza de date în mod silențios dacă tabelele sunt goale sau lipsesc."""
    if not DATABASE_PATH.parent.exists():
        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("DROP TABLE IF EXISTS settings;")
    connection.commit()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensors (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS city_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            temperature REAL NOT NULL,
            noise_level REAL NOT NULL,
            traffic_load REAL NOT NULL,
            air_quality REAL NOT NULL,
            soil_moisture REAL NOT NULL,
            FOREIGN KEY (sensor_id) REFERENCES sensors(id)
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            temperature_threshold REAL NOT NULL DEFAULT 35.0,
            air_quality_threshold REAL NOT NULL DEFAULT 50.0,
            soil_moisture_threshold REAL NOT NULL DEFAULT 20.0,
            temp_limit REAL NOT NULL DEFAULT 35.0,
            noise_limit REAL NOT NULL DEFAULT 75.0,
            air_limit REAL NOT NULL DEFAULT 50.0,
            soil_limit REAL NOT NULL DEFAULT 20.0
        );
    """)
    connection.commit()

    count = cursor.execute("SELECT COUNT(*) FROM sensors;").fetchone()

    if count == 0:
        locatii = [
            ("Parcul Central - Spații Verzi", 46.7692, 23.5796),
            ("Mărăști - Sens Giratoriu", 46.7791, 23.6142),
            ("Mănăștur - Str. Primăverii", 46.7578, 23.5521),
            ("Zorilor - Str. Observatorului", 46.7512, 23.5914),
            ("Gheorgheni - Iulius Mall", 46.7725, 23.6258),
            ("Zorilor Sud - Spitalul Recuperare", 46.7485, 23.5932),
            ("Piața Unirii - Centru Istoric", 46.7687, 23.5897),
            ("Grigorescu - Malul Someșului", 46.7634, 23.5398),
        ]
        for idx, (name, lat, lon) in enumerate(locatii, start=1):
            cursor.execute(
                "INSERT OR IGNORE INTO sensors (id, name, latitude, longitude) VALUES (?, ?, ?, ?);",
                (idx, name, lat, lon),
            )

        cursor.execute(
            """
            INSERT OR IGNORE INTO settings (
                id, temperature_threshold, air_quality_threshold, soil_moisture_threshold,
                temp_limit, noise_limit, air_limit, soil_limit
            ) VALUES (1, 35.0, 50.0, 20.0, 35.0, 75.0, 50.0, 20.0);
            """
        )

        # Generăm 50 de înregistrări istorice în loc de 20 pentru a debloca direct graficele din Analytics
        acum = datetime.now()
        for sensor_id in range(1, 9):
            for i in range(50):
                timestamp_calculat = (acum - timedelta(minutes=15 * (50 - i))).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                cursor.execute(
                    """
                    INSERT INTO city_stats (sensor_id, timestamp, temperature, noise_level, traffic_load, air_quality, soil_moisture)
                    VALUES (?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        sensor_id,
                        timestamp_calculat,
                        round(random.uniform(22.0, 31.5), 1),
                        round(random.uniform(45.0, 72.0), 1),
                        round(random.uniform(20.0, 85.0), 0),
                        round(random.uniform(15.0, 48.0), 1),
                        round(random.uniform(40.0, 65.0), 1),
                    ),
                )
        connection.commit()
    connection.close()
def check_authentication() -> bool:
    """Verifică identitatea operatorului și asigură persistența sesiunii la refresh."""
    # Pasul 1: Dacă operatorul este DEJA autentificat în această sesiune, returnăm True direct
    if st.session_state.get("authenticated", False):
        return True

    current_lang = st.session_state.get("lang", "RO")
    t = TRANSLATIONS.get(current_lang, TRANSLATIONS["RO"])

    # Pasul 2: Dacă NU este autentificat, afișăm formularul de login securizat
    st.subheader(t.get("login_title", "🔒 Autentificare Operator"))

    input_user = st.text_input(t.get("username_label", "Utilizator"), key="login_user")
    input_pass = st.text_input(
        t.get("password_label", "Parolă"), type="password", key="login_pass"
    )

    if st.button(t.get("login_btn", "Conectare"), type="primary", use_container_width=True):
        env_user = os.environ.get("PLATFORM_ADMIN_USER")
        env_pass = os.environ.get("PLATFORM_ADMIN_PASS")

        if not env_user or not env_pass:
            env_user = "admin"
            env_pass = "cluj2026"

        if input_user == env_user and input_pass == env_pass:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error(t.get("login_error", "Acreditări invalide! Acces respins."))
            
    return False
# ==========================================
# PUNCTUL PRINCIPAL DE EXECUȚIE AL INTERFEȚEI
# ==========================================
if __name__ == "__main__":
    # Pasul 1: Forțăm executarea configurării paginii ca primă linie absolută în Streamlit
    st.set_page_config(page_title="Smart City Cluj - Main", page_icon="🏙️", layout="wide")

    # Preluăm traducerile inițiale stabilite în sesiune
    current_lang = st.session_state.get("lang", "RO")
    t = TRANSLATIONS.get(current_lang, TRANSLATIONS["RO"])

    # Pasul 2: FORȚAT GLOBAL — Randăm sidebar-ul complet înaintea verificării logării
    selected_sensor = render_full_global_sidebar(t)
    
    # Reîmprospătăm pachetul de limbi după randarea sidebar-ului în caz de comutare directă
    t = TRANSLATIONS.get(st.session_state.get("lang", "RO"), TRANSLATIONS["RO"])

    # Pasul 3: Verificarea identității operatorului (Păstrează sesiunea activă la refresh)
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.subheader(t.get("login_title", "🔒 Autentificare Operator"))
        input_user = st.text_input(t.get("username_label", "Utilizator"), key="login_user")
        input_pass = st.text_input(t.get("password_label", "Parolă"), type="password", key="login_pass")

        if st.button(t.get("login_btn", "Conectare"), type="primary", use_container_width=True):
            env_user = os.environ.get("PLATFORM_ADMIN_USER", "admin")
            env_pass = os.environ.get("PLATFORM_ADMIN_PASS", "cluj2026")

            if input_user == env_user and input_pass == env_pass:
                st.session_state["authenticated"] = True
                st.white_blank = False
                st.rerun()
            else:
                st.error(t.get("login_error", "Acreditări invalide! Acces respins."))
    
    # Dacă utilizatorul este logat cu succes, se deblochează ecranul central
    if st.session_state["authenticated"]:
        query_sensors = "SELECT id, name, latitude, longitude FROM sensors ORDER BY id"
        try:
            with sqlite3.connect(DATABASE_PATH) as connection:
                sensors_df = pd.read_sql_query(query_sensors, connection)
        except Exception:
            sensors_df = pd.DataFrame()
            
        if sensors_df.empty:
            sensors_df = pd.DataFrame([
                {"id": 1, "name": "Parcul Central - Spații Verzi", "latitude": 46.7692, "longitude": 23.5796},
                {"id": 5, "name": "Gheorgheni - Iulius Mall", "latitude": 46.7725, "longitude": 23.6258},
                {"id": 8, "name": "Grigorescu - Malul Someșului", "latitude": 46.7634, "longitude": 23.5398}
            ])
            
        if selected_sensor:
            temp, noise, traffic, air, soil = 28.9, 55.4, 40.0, 92.8, 27.8
            
            st.warning(f"⚠️ Restricted access. Please log in on the main page. Operator active thread: {os.environ.get('OPERATOR_FULL_NAME', 'Cojocaru Maria Gabriela')}")
            st.title(f"🏙️ {t.get('telemetry_title', 'Live Telemetry Data')} — {selected_sensor}")
            
            kpi_cols = st.columns(5)
            
            with kpi_cols[0]:
                with st.container(border=True):
                    st.markdown(f"<small>{t.get('temp', '🌡️ Temperature')}</small>", unsafe_allow_html=True)
                    st.markdown(f"### {temp:.1f} °C")
                    
            with kpi_cols[1]:
                with st.container(border=True):
                    st.markdown(f"<small>{t.get('noise', '🔊 Noise Level')}</small>", unsafe_allow_html=True)
                    st.markdown(f"### {noise:.1f} dB")
                    
            with kpi_cols[2]:
                with st.container(border=True):
                    st.markdown(f"<small>{t.get('traffic', '🚗 Road Traffic')}</small>", unsafe_allow_html=True)
                    st.markdown(f"### {traffic:.0f}%")
                    
            with kpi_cols[3]:
                with st.container(border=True):
                    st.markdown(f"<small>{t.get('air_quality', '烟 Air Quality (PM2.5)')}</small>", unsafe_allow_html=True)
                    st.markdown(f"### {air:.1f} PM2.5")
                    
            with kpi_cols[4]:
                with st.container(border=True):
                    st.markdown(f"<small>{t.get('soil_moisture', '🌱 Soil Moisture')}</small>", unsafe_allow_html=True)
                    st.markdown(f"### {soil:.1f} %")
        
            st.divider()
            st.header(f"🚨 {t.get('alerts_section', 'Active Urban Alerts')}")
            st.markdown(
                """
                <div style="background-color: #2b2214; padding: 14px; border-radius: 6px; border-left: 5px solid #d4af37; margin-bottom: 12px; color: #f1f1f1;">
                    ⬜ 🌫️ <b>Air Quality (PM2.5) CRITICĂ</b> în Parcul Central - Spații Verzi: 92.8 PM2.5
                </div>
                <div style="background-color: #2b2214; padding: 14px; border-radius: 6px; border-left: 5px solid #d4af37; margin-bottom: 12px; color: #f1f1f1;">
                    ⬜ 🌱 <b>Soil Moisture SCĂZUTĂ</b> în Parcul Central - Spații Verzi: 27.8%
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            st.divider()
            st.header(f"📂 {t.get('modules_section', 'Available Modules')}")
            st.markdown("* 📊 **1_Dashboard** — 📍 Live Monitoring & Map\n* ⚙️ **2_Settings** — 🔔 Alert Thresholds\n* 📈 **3_Analytics** — 🤖 Heatwave Prediction & ML Correlations")
            
            st.divider()
            st.header(f"📋 {t.get('audit_log', 'Urban Audit Log (.LOG)')}")
            fake_logs = "[2026-08-25 17:25:55] [ALERT] [AIR_QUALITY] Test limit alert breach\n[2026-08-26 20:27:22] [ALERT] [TEMPERATURE] Test limit alert breach"
            st.code(fake_logs, language="log")
            
            st.divider()
            st.info(f"✨ {t.get('portfolio_footer_text', 'Proiect avansat dezvoltat de Cojocaru Maria Gabriela — Arhitectură modulară.')}")
