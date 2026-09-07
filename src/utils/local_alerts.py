"""Core utilities for local visual alert throttling and security log auditing."""

from __future__ import annotations

import time
from pathlib import Path

# Barieră temporală industrială pentru a preveni epuizarea spațiului pe disc sau blocarea UI
ALERT_COOLDOWN_SECONDS = 10.0
LOG_FILE_PATH = Path("security_alerts.log")


def send_local_alert_safe(
    alert_type: str, message_body: str, state_cache: dict[str, float]
) -> bool:
    """Validează pragul de cooldown temporal și înregistrează alerta în jurnalul de audit local.

    Aplica igienizarea stringurilor pentru a preveni atacurile de tip Log Injection.
    """
    current_time = time.time()
    last_sent = state_cache.get(alert_type, 0.0)

    # Verificare inegalitate strictă pentru scutul de cooldown
    if current_time - last_sent < ALERT_COOLDOWN_SECONDS:
        return False

    # Actualizăm timestamp-ul în memoria cache injectată
    state_cache[alert_type] = current_time

    # Igienizare critică: eliminăm line-breaks pentru a bloca Log Injection/Forgery
    sanitized_body = message_body.replace("\n", " ").replace("\r", " ").strip()
    sanitized_type = alert_type.replace("\n", "").replace("\r", "").upper()

    # Jurnalizare nativă securizată pe disc
    try:
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as log_file:
            log_file.write(
                f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [ALERT] [{sanitized_type}] {sanitized_body}\n"
            )
        return True
    except IOError:
        # Fail-safe în cazul în care fișierul este blocat de sistemul de operare
        return False
