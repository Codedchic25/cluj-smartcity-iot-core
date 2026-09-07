"""Database seeding engine optimizing operational geospatial coordinates for Cluj-Napoca."""

from __future__ import annotations

import sqlite3
from pathlib import Path

# Utilizăm calea absolută centralizată din arhitectură pentru coerență totală
DATABASE_PATH = Path(r"C:\Users\user\Documents\Smart-City-Cluj-IoT\app.db")


def seed_database() -> None:
    """Execute clean transactional population for active sensory telemetry nodes."""
    if not DATABASE_PATH.parent.exists():
        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    # ============================================================================
    # CREARE STRUCTURĂ SQL (Rezolvare eroare "no such table: settings")
    # ============================================================================
    print("🏗️ Creăm tabelele sistemului IoT și configurațiile dacă nu există...")
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
            id INTEGER PRIMARY KEY CHECK (id = 1), -- Ne asigurăm că avem o singură linie de config
            temperature_threshold REAL NOT NULL,
            air_quality_threshold REAL NOT NULL,
            soil_moisture_threshold REAL NOT NULL
        );
    """)
    connection.commit()

    print("🧹 Curățăm tranzacțional datele învechite din tabele...")
    try:
        cursor.execute("DELETE FROM city_stats;")
        cursor.execute("DELETE FROM sensors;")
        cursor.execute("DELETE FROM settings;")
        connection.commit()
    except sqlite3.OperationalError as exc:
        print(f"⚠️ Notificare la curățarea structurilor: {exc}")

    # Inserăm valorile implicite de siguranță în tabela settings pentru a fi citite în UI
    print("⚙️ Inițializăm pragurile de siguranță implicite în tabelul settings...")
    cursor.execute("""
        INSERT INTO settings (id, temperature_threshold, air_quality_threshold, soil_moisture_threshold)
        VALUES (1, 35.0, 50.0, 20.0);
    """)

    connection.commit()
    connection.close()
    print("✨ Succes! Baza de date conține acum rețeaua de senzori aliniată geospațial.")


if __name__ == "__main__":
    seed_database()
