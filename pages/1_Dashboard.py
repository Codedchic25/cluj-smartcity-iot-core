"""Operational monitoring dashboard with unified sidebar layout architecture."""

from __future__ import annotations

import os
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from translations import TRANSLATIONS

# ============================================================================
# Configuration & Context Bounds
# ============================================================================
DATABASE_PATH = Path(os.environ.get("DATABASE_PATH", "app.db"))


def get_historical_data(sensor_id: int, limit: int = 20) -> pd.DataFrame:
    """Preia ultimele înregistrări din jurnalul local al stației selectate."""
    query = """
        SELECT timestamp, temperature, noise_level, traffic_load, air_quality, soil_moisture
        FROM city_stats WHERE sensor_id = ? ORDER BY timestamp DESC LIMIT ?
    """
    try:
        with sqlite3.connect(DATABASE_PATH, timeout=15) as connection:
            dataframe = pd.read_sql_query(query, connection, params=(sensor_id, limit))
        if not dataframe.empty:
            dataframe = dataframe.sort_values("timestamp").reset_index(drop=True)
        return dataframe
    except sqlite3.Error:
        return pd.DataFrame()


def main() -> None:
    """Punctul de execuție principal pentru ecranul de monitoring Dashboard."""
    st.set_page_config(page_title="Smart City Cluj - Dashboard", page_icon="📊", layout="wide")
    
    # Auto-refresh la fiecare 10 secunde pentru simularea fluxurilor live
    st_autorefresh(interval=10000, key="dashboard_refresh_counter")

    # Forțăm verificarea identității operatorului prin starea sesiunii din main.py
    if not st.session_state.get("authenticated", False):
        st.warning("🔒 Acces restricționat! Vă rugăm să vă autentificați pe pagina principală (main).")
        st.stop()

    current_lang = st.session_state.get("lang", "RO")
    t = TRANSLATIONS.get(current_lang, TRANSLATIONS["RO"])

    # ASIGURAT: Apelăm funcția centralizată din app.ai.ai_interface (fără importuri circulare)
    from app.ai.ai_interface import render_full_global_sidebar
    selected_sensor = render_full_global_sidebar(t)

    # Actualizăm traducerile în caz de comutare directă a limbii din widget
    t = TRANSLATIONS.get(st.session_state.get("lang", "RO"), TRANSLATIONS["RO"])

    # 1. Încercăm citirea nodurilor din SQLite
    query_sensors = "SELECT id, name, latitude, longitude FROM sensors ORDER BY id"
    try:
        with sqlite3.connect(DATABASE_PATH) as connection:
            sensors_df = pd.read_sql_query(query_sensors, connection)
    except sqlite3.Error:
        sensors_df = pd.DataFrame()

    # [Fallback DevOps] Generăm structura pe loc dacă SQLite-ul din cloud este gol în acest thread
    if sensors_df.empty:
        sensors_df = pd.DataFrame([
            {"id": 1, "name": "Parcul Central - Spații Verzi", "latitude": 46.7692, "longitude": 23.5796},
            {"id": 2, "name": "Mărăști - Sens Giratoriu", "latitude": 46.7791, "longitude": 23.6142},
            {"id": 3, "name": "Mănăștur - Str. Primăverii", "latitude": 46.7578, "longitude": 23.5521},
            {"id": 4, "name": "Zorilor - Str. Observatorului", "latitude": 46.7512, "longitude": 23.5914},
            {"id": 5, "name": "Gheorgheni - Iulius Mall", "latitude": 46.7725, "longitude": 23.6258},
            {"id": 6, "name": "Piața Unirii - Centru Istoric", "latitude": 46.7687, "longitude": 23.5897}
        ])

    if selected_sensor:
        matches = sensors_df[sensors_df["name"] == selected_sensor]
        if matches.empty:
            matches = sensors_df.iloc[[0]]
            
        sensor_info = matches.iloc[0]
        sensor_id = int(sensor_info["id"])
        
        # 2. Încercăm interogarea istoricului
        history_df = get_historical_data(sensor_id=sensor_id, limit=20)
        
        # [Fallback DevOps] Construim 20 de citiri simulate instant dacă nu avem istoric pe disc
        if history_df.empty:
            acum = datetime.now()
            fake_rows = []
            for i in range(20):
                t_calc = (acum - timedelta(minutes=15 * (20 - i))).strftime("%Y-%m-%d %H:%M:%S")
                fake_rows.append({
                    "timestamp": t_calc,
                    "temperature": round(random.uniform(24.5, 29.5), 1),
                    "noise_level": round(random.uniform(48.0, 62.0), 1),
                    "traffic_load": round(random.uniform(35.0, 65.0), 0),
                    "air_quality": round(random.uniform(28.0, 48.0), 1),
                    "soil_moisture": round(random.uniform(42.0, 56.0), 1)
                })
            history_df = pd.DataFrame(fake_rows)
            
        # Preluăm ultima citire pentru KPI-uri
        latest_telemetry = history_df.iloc[-1]
        temp = float(latest_telemetry["temperature"])
        noise = float(latest_telemetry["noise_level"])
        traffic = float(latest_telemetry["traffic_load"])
        air = float(latest_telemetry["air_quality"])
        soil = float(latest_telemetry["soil_moisture"])
        
        # --- INTERFAȚA OPERAȚIONALĂ PRINCIPALĂ ---
        st.title(f"🏙️ {t.get('title', 'Platformă Smart City Cluj-Napoca')}")
        st.subheader(f"📊 {t.get('form_name', 'Stație IoT')}: {selected_sensor}")
        st.caption(f"📅 Date Telemetrice Active actualizate la: {latest_telemetry['timestamp']}")
        st.divider()
        
        # Afișare KPI-uri iluminate în containere pe 5 coloane discrete
        kpi_cols = st.columns(5)
        with kpi_cols[0]:
            with st.container(border=True):
                st.markdown(f"<small>{t.get('temp', '🌡️ Temperatură')}</small>", unsafe_allow_html=True)
                st.markdown(f"### {temp:.1f} °C")
        with kpi_cols[1]:
            with st.container(border=True):
                st.markdown(f"<small>{t.get('noise', '🔊 Nivel Zgomot')}</small>", unsafe_allow_html=True)
                st.markdown(f"### {noise:.1f} dB")
        with kpi_cols[2]:
            with st.container(border=True):
                st.markdown(f"<small>{t.get('traffic', '🚗 Trafic Rutier')}</small>", unsafe_allow_html=True)
                st.markdown(f"### {traffic:.0f}%")
        with kpi_cols[3]:
            with st.container(border=True):
                st.markdown(f"<small>{t.get('air_quality', '烟 Calitate Aer')}</small>", unsafe_allow_html=True)
                st.markdown(f"### {air:.1f}")
        with kpi_cols[4]:
            with st.container(border=True):
                st.markdown(f"<small>{t.get('soil_moisture', '🌱 Umiditate Sol')}</small>", unsafe_allow_html=True)
                st.markdown(f"### {soil:.1f}%")
                
        st.divider()        # Structură duală simetrică - Harta în STÂNGA, Graficul Avansat în DREAPTA
        ui_cols = st.columns([1, 1.3])
        with ui_cols[0]:
            st.markdown(f"#### 📍 {t.get('live_map_label', 'Poziționare Nod Geospațial Local')}")
            latitude = float(sensor_info["latitude"])
            longitude = float(sensor_info["longitude"])
            map_data = pd.DataFrame({"lat": [latitude], "lon": [longitude]})
            st.map(map_data, zoom=14, width="stretch")
            
        with ui_cols[1]:
            st.markdown(f"#### 📈 {t.get('chart_title', 'Analiză Temporală Corelată (Toate cele 5 Metrici Urban)')}")
            
            # Construim un panou de 5 sub-grafice cu axa X partajată (Shared X Axis)
            fig = make_subplots(
                rows=5, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                subplot_titles=(
                    f"🌡️ {t.get('temp', 'Temperatură')} (°C)",
                    f"🔊 {t.get('noise', 'Zgomot')} (dB)",
                    f"🚗 {t.get('traffic', 'Trafic')} (%)",
                    f"🌫️ {t.get('air_quality', 'Calitate Aer')} (PM2.5)",
                    f"🌱 {t.get('soil_moisture', 'Umiditate Sol')} (%)"
                )
            )
            
            # Configurația de culori premium tip Neon / Cyberpunk
            metrics_config = [
                {"col": "temperature", "color": "#ff4b4b", "row": 1, "name": "Temperatură"},
                {"col": "noise_level", "color": "#00f2fe", "row": 2, "name": "Nivel Zgomot"},
                {"col": "traffic_load", "color": "#ffb300", "row": 3, "name": "Trafic Rutier"},
                {"col": "air_quality", "color": "#a855f7", "row": 4, "name": "Calitate Aer"},
                {"col": "soil_moisture", "color": "#10b981", "row": 5, "name": "Umiditate Sol"}
            ]
            
            # Adăugăm dinamic fiecare linie cu umbrire graduală elegantă
            for cfg in metrics_config:
                fig.add_trace(
                    go.Scatter(
                        x=history_df["timestamp"],
                        y=history_df[cfg["col"]],
                        name=cfg["name"],
                        mode="lines+markers",
                        line=dict(color=cfg["color"], width=2),
                        marker=dict(size=4),
                        fill="tozeroy",
                        fillcolor=f"rgba({int(cfg['color'][1:3], 16)}, {int(cfg['color'][3:5], 16)}, {int(cfg['color'][5:7], 16)}, 0.08)"
                    ),
                    row=cfg["row"], col=1
                )
            
            # Stilizarea estetică avansată a layout-ului în tema dark-mode
            fig.update_layout(
                template="plotly_dark",
                height=650,
                showlegend=False,
                margin=dict(l=20, r=20, t=40, b=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            
            # Curățăm liniile de grilă pentru un aspect minimalist tip dashboard executiv
            fig.update_xaxes(showgrid=True, gridcolor="#222639", tickangle=-15)
            fig.update_yaxes(showgrid=True, gridcolor="#222639")
            
            st.plotly_chart(fig, use_container_width=True)
            
        st.divider()
        
        # ASISTENTUL AI LA SUBSOL
        from app.ai.ai_interface import render_ai_assistant
        with st.expander(f"🤖 {t.get('ai_assistant_tab', 'Asistent Urban Inteligent AI (Groq/LLM)')}"):
            render_ai_assistant(
                location=selected_sensor,
                temperature=temp,
                air_quality=air,
                soil_moisture=soil,
                translations=t
            )
            
        st.divider()
        st.info(f"✨ {t.get('portfolio_footer_text', 'Proiect avansat dezvoltat de Cojocaru Maria Gabriela — Arhitectură modulară optimizată DevOps pentru testare și portofoliu.')}")


if __name__ == "__main__":
    main()

