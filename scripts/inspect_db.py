"""Utility script to inspect and validate the Smart City Cluj-Napoca database."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

DATABASE_PATH = Path(os.getenv("DATABASE_PATH", "app.db"))


def inspect_database() -> None:
    """Inspect SQLite tables, thresholds, sensors, and latest telemetry records safely."""
    print("🔍 [DATABASE INSPECTOR] Starting database inspection...")

    if not DATABASE_PATH.exists():
        print(f"❌ Database file not found: '{DATABASE_PATH.resolve()}'. Run 'setup_db.py' first.")
        return

    try:
        with sqlite3.connect(DATABASE_PATH, timeout=10) as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                  AND name NOT LIKE 'sqlite_%'
                ORDER BY name
                """
            )

            tables = [row[0] for row in cursor.fetchall()]

            if not tables:
                print("⚠️ Database contains no application tables.")
                return

            print(f"📊 Detected {len(tables)} application tables:")

            for table_name in tables:
                cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
                count = cursor.fetchone()[0]
                print(f"   └── 📋 {table_name:<15} | Records: {count}")

            print("\n⚙️ [THRESHOLD VALIDATION] Active safety thresholds:")

            cursor.execute(
                """
                SELECT id, temp_limit, noise_limit, air_limit, soil_limit
                FROM settings
                WHERE id = 1
                """
            )

            settings = cursor.fetchone()

            if settings:
                setting_id, temperature_limit, noise_limit, air_limit, soil_limit = settings
                print(f"   ├── ID: {setting_id}")
                print(f"   ├── Temperature: {temperature_limit} °C")
                print(f"   ├── Noise: {noise_limit} dB")
                print(f"   ├── Air quality: {air_limit}")
                print(f"   └── Soil moisture: {soil_limit} %")
            else:
                print("   ⚠️ No safety thresholds configured with ID = 1.")

            print("\n📡 [SENSOR VALIDATION] Registered sensors:")

            cursor.execute(
                """
                SELECT id, name, latitude, longitude
                FROM sensors
                ORDER BY id
                """
            )

            sensors = cursor.fetchall()

            if sensors:
                for sensor_id, name, latitude, longitude in sensors:
                    lat_str = f"{latitude:.4f}" if latitude is not None else "N/A"
                    lon_str = f"{longitude:.4f}" if longitude is not None else "N/A"
                    print(f"   ├── #{sensor_id} {name} | Lat: {lat_str} | Lon: {lon_str}")
            else:
                print("   ⚠️ No sensors registered.")

            print("\n📡 [TELEMETRY] Latest 3 records:")

            cursor.execute(
                """
                SELECT
                    c.timestamp,
                    s.name,
                    c.temperature,
                    c.noise_level,
                    c.traffic_load,
                    c.air_quality,
                    c.soil_moisture
                FROM city_stats AS c
                LEFT JOIN sensors AS s
                    ON c.sensor_id = s.id
                ORDER BY c.timestamp DESC
                LIMIT 3
                """
            )

            records = cursor.fetchall()

            if records:
                for record in records:
                    timestamp, sensor_name, temp, noise, traffic, air, soil = record

                    temp_str = f"{temp:.1f} °C" if temp is not None else "N/A"
                    noise_str = f"{noise:.1f} dB" if noise is not None else "N/A"
                    traffic_str = f"{traffic}%" if traffic is not None else "N/A"
                    air_str = f"{air:.1f}" if air is not None else "N/A"
                    soil_str = f"{soil:.1f}%" if soil is not None else "N/A"

                    print(
                        f"   ├── [{timestamp}] {sensor_name or 'Unknown sensor'} | "
                        f"{temp_str} | {noise_str} | Traffic: {traffic_str} | "
                        f"Air: {air_str} | Soil: {soil_str}"
                    )
            else:
                print("   ℹ️ No telemetry records found in 'city_stats'. Start the IoT producer.")

            print("\n✅ Database inspection completed successfully.")

    except (sqlite3.Error, ValueError) as exc:
        print(f"❌ Database inspection failed: {exc}")
        raise


if __name__ == "__main__":
    inspect_database()
