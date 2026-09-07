# app/services/producer.py
"""IoT telemetry producer and local log alert service for Smart City Cluj-Napoca."""

from __future__ import annotations

import asyncio
import random
import time
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import text

from app.database.database import (
    cleanup_old_data,
    get_alert_thresholds_async,
    get_async_db_session,
)

load_dotenv()

# ============================================================================
# IoT Generation Configuration & Bounds
# ============================================================================

DATA_GENERATION_INTERVAL_SECONDS = 5
DATABASE_RETRY_INTERVAL_SECONDS = 2
MAINTENANCE_CYCLE_INTERVAL = 50
DATA_RETENTION_HOURS = 24

LOG_FILE_PATH = Path("security_alerts.log")
ALERT_COOLDOWN_SECONDS = 10.0

# Memorie cache locală pentru gestionarea barierelor temporale de cooldown asincrone
alert_cooldown_registry: dict[str, float] = {}


async def send_local_log_alert_async(
    alert_type: str,
    message_body: str,
) -> None:
    """Write an infrastructure anomaly event directly into the local enterprise audit log."""
    current_time = time.time()
    last_sent = alert_cooldown_registry.get(alert_type, 0.0)

    # Scut anti-duplicat: Verificare inegalitate strictă asumată local
    if current_time - last_sent < ALERT_COOLDOWN_SECONDS:
        return

    # Actualizare imediată a cache-ului pentru a bloca pachetele concurente retransmise
    alert_cooldown_registry[alert_type] = current_time

    # Jurnalizare nativă sigură folosind execuția asincronă neblocantă pe thread-ul de I/O
    try:
        loop = asyncio.get_running_loop()
        formatted_line = (
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [ALERT] "
            f"[{alert_type.upper()}] {message_body}\n"
        )

        await loop.run_in_executor(
            None,
            lambda: LOG_FILE_PATH.open("a", encoding="utf-8").write(formatted_line),
        )
        print(f"📝 Jurnal de audit actualizat local pe disc pentru anomalia: {alert_type}")
    except IOError:
        print("⚠️ Fail-safe: Jurnalul local pe disc este blocat temporar de sistemul de operare.")


async def process_alerts_async(
    sensor_name: str,
    temperature: float,
    air_quality: float,
    soil_moisture: float,
    thresholds: tuple[float, float, float, float],
) -> None:
    """Evaluate pipeline telemetry vectors against strict multi-layer mathematical limits."""
    (
        temperature_threshold,
        _noise_threshold,
        air_quality_threshold,
        soil_moisture_threshold,
    ) = thresholds

    alert_tasks = []

    if temperature > temperature_threshold:
        message = f"Temperatură critică detectată în {sensor_name}: {temperature:.1f}°C"
        alert_tasks.append(
            send_local_log_alert_async(
                alert_type=f"{sensor_name}_temperature",
                message_body=message,
            )
        )

    if air_quality > air_quality_threshold:
        message = f"Poluare aer crescută detectată în {sensor_name}: {air_quality:.1f} PM2.5"
        alert_tasks.append(
            send_local_log_alert_async(
                alert_type=f"{sensor_name}_air_quality",
                message_body=message,
            )
        )

    if soil_moisture < soil_moisture_threshold:
        message = f"Umiditate sol scăzută detectată în {sensor_name}: {soil_moisture:.1f}%"
        alert_tasks.append(
            send_local_log_alert_async(
                alert_type=f"{sensor_name}_soil_moisture",
                message_body=message,
            )
        )

    if alert_tasks:
        await asyncio.gather(*alert_tasks)


def generate_sensor_telemetry(sensor_name: str) -> dict[str, float]:
    """Generate multi-variable deterministic simulated urban data structures."""
    traffic = int(random.randint(10, 95))
    temperature = round(random.uniform(18, 32) + (traffic * 0.03), 1)
    noise_level = round(random.uniform(40, 60) + (traffic * 0.3), 1)
    air_quality = round((traffic * 0.7) + random.uniform(5, 25), 1)

    if "Parc" in sensor_name or "Spații" in sensor_name:
        soil_moisture = round(random.uniform(40, 80), 1)
    else:
        soil_moisture = round(random.uniform(15, 45), 1)

    return {
        "traffic_load": traffic,
        "temperature": temperature,
        "noise_level": noise_level,
        "air_quality": air_quality,
        "soil_moisture": soil_moisture,
    }


async def produce_data_async() -> None:
    """Continuously execute lifecycle stages for telemetry collection and maintenance extraction."""
    cycle_counter = 0

    while True:
        try:
            thresholds = await get_alert_thresholds_async()

            async with get_async_db_session() as session:
                result = await session.execute(text("SELECT id, name FROM sensors ORDER BY id"))
                sensors = result.fetchall()

                if not sensors:
                    print(
                        "⚠️ Tabela 'sensors' este goală. Se așteaptă configurarea nodurilor din Setări..."
                    )
                    await asyncio.sleep(5)
                    continue

                for row in sensors:
                    sensor_id, sensor_name = row[0], str(row[1])
                    telemetry = generate_sensor_telemetry(sensor_name)

                    # Procesare asincronă a logurilor locale
                    await process_alerts_async(
                        sensor_name=sensor_name,
                        temperature=telemetry["temperature"],
                        air_quality=telemetry["air_quality"],
                        soil_moisture=telemetry["soil_moisture"],
                        thresholds=thresholds,
                    )

                    await session.execute(
                        text(
                            """
                            INSERT INTO city_stats (
                                sensor_id, temperature, noise_level, traffic_load, air_quality, soil_moisture
                            )
                            VALUES (
                                :sensor_id, :temperature, :noise_level, :traffic_load, :air_quality, :soil_moisture
                            )
                            """
                        ),
                        {
                            "sensor_id": int(sensor_id),
                            "temperature": telemetry["temperature"],
                            "noise_level": telemetry["noise_level"],
                            "traffic_load": telemetry["traffic_load"],
                            "air_quality": telemetry["air_quality"],
                            "soil_moisture": telemetry["soil_moisture"],
                        },
                    )

                await session.commit()

            cycle_counter += 1

            # Executarea ciclului de purjare a seriilor temporale vechi
            if cycle_counter >= MAINTENANCE_CYCLE_INTERVAL:
                try:
                    await cleanup_old_data(hours=DATA_RETENTION_HOURS)
                except Exception as maintenance_error:
                    print(
                        f"❌ [MAINTENANCE ERROR] Eșec la curățarea datelor vechi: {maintenance_error}"
                    )
                finally:
                    cycle_counter = 0

            await asyncio.sleep(DATA_GENERATION_INTERVAL_SECONDS)

        except Exception as exc:
            print(
                f"⚠️ Întrerupere în pipeline: {exc}. Reîncerc în {DATABASE_RETRY_INTERVAL_SECONDS}s..."
            )
            await asyncio.sleep(DATABASE_RETRY_INTERVAL_SECONDS)


if __name__ == "__main__":
    try:
        asyncio.run(produce_data_async())
    except KeyboardInterrupt:
        print("\n🛑 Serviciul Producer a fost oprit controlat din consolă.")
