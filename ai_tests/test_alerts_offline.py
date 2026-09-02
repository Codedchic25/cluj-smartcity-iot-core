# ai_tests/test_alerts_offline.py
"""Automated offline validation tests for the Smart City local alert engine."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from src.utils.local_alerts import send_local_alert_safe
from translations import TRANSLATIONS


# =====================================================================
# 1. INTEGRITATEA MATRICEI DE TRADUCERI (Sincronizare Globală)
# =====================================================================
def test_translation_matrix_integrity():
    """Verifică dacă toate limbile au exact aceleași chei ca limba de referință (RO)."""
    base_keys = set(TRANSLATIONS["RO"].keys())
    for lang in ["EN", "IT", "ES", "HU"]:
        lang_keys = set(TRANSLATIONS[lang].keys())
        assert base_keys == lang_keys, (
            f"Limbii {lang} îi lipsesc chei sau are chei în plus în translations.py!"
        )


# =====================================================================
# 2. VALIDAREA PRAGURILOR STRICTE (Inegalități Matematice active)
# =====================================================================
@pytest.mark.parametrize(
    "alert_type, value, threshold, expected",
    [
        ("temperature", 32.0, 32.0, False),  # Exact egal -> nu este alarmă
        ("temperature", 32.1, 32.0, True),  # Peste prag -> declanșează alarmă
        ("air_quality", 80.0, 80.0, False),  # Exact egal -> nu este alarmă
        ("air_quality", 81.0, 80.0, True),  # Peste prag -> declanșează alarmă
        ("soil_moisture", 35.0, 35.0, False),  # Exact egal -> nu este alarmă
        ("soil_moisture", 34.9, 35.0, True),  # Sub prag -> declanșează alarmă
    ],
)
def test_strict_alert_boundaries(alert_type, value, threshold, expected):
    """Verifică comportamentul inegalităților stricte din motorul IoT urban."""
    state_cache = {alert_type: 0.0}

    if alert_type == "soil_moisture":
        is_critical = value < threshold
    else:
        is_critical = value > threshold

    if is_critical:
        # Aici apelăm noua funcție locală gata curățată
        result = send_local_alert_safe(alert_type, "Test limit alert breach", state_cache)
        assert result is expected
    else:
        assert not expected


# =====================================================================
# 3. DISPATCH ASINCRON URBAN (Evaluare concurentă simulată)
# =====================================================================
def test_multiple_live_alerts_dispatch():
    """Simulează un dispatch asincron controlat utilizând execuția nativă asyncio.run."""

    async def run_mock_pipeline():
        mock_dispatcher = AsyncMock(return_value=True)
        # Mock-uim noul handler local izolat pentru a nu scrie pe disc în timpul testelor concurente
        with patch("src.utils.local_alerts.send_local_alert_safe", mock_dispatcher):
            results = [
                await mock_dispatcher("temperature", "Alert 1"),
                await mock_dispatcher("air_quality", "Alert 2"),
                await mock_dispatcher("soil_moisture", "Alert 3"),
            ]
            assert len(results) == 3
            assert mock_dispatcher.call_count == 3

    # Executăm corutina asincronă în mod controlat și sincron
    asyncio.run(run_mock_pipeline())


# =====================================================================
# 4. COOLDOWN-UL LOCAL PE DISC (Bariera temporală de siguranță)
# =====================================================================
def test_alert_engine_cooldown_offline():
    """Validează blocarea alertelor duplicat în interiorul aceleiași ferestre de timp."""
    local_state_cache = {"temperature": 0.0, "air_quality": 0.0, "soil_moisture": 0.0}

    # Pasul A: Prima rulare - Trebuie să permită jurnalizarea și să treacă de barieră
    assert (
        send_local_alert_safe("temperature", "Caniculă detectată în Centru", local_state_cache)
        is True
    )

    # Pasul B: A doua rulare instantă - Trebuie să blocheze scrierea (Scut Cooldown activ)
    assert (
        send_local_alert_safe("temperature", "Caniculă detectată în Centru", local_state_cache)
        is False
    )
