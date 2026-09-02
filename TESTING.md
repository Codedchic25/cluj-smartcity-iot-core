# 🧪 Ghid de Testare Automată — Smart City Cluj-Napoca

Acest document descrie arhitectura suitei de teste și instrucțiunile de rulare pentru platforma Urban IoT, asigurând verificarea calității codului înainte de deployment.

## 🛠️ Instrumente de Testare (Testing Stack)
Conform specificațiilor unificate din `pyproject.toml`, suita de teste utilizează:
- **`pytest`** (>= 8.0) — Framework-ul principal de testare și aserțiune a calității.
- **`pytest-asyncio`** — Extensie utilizată pentru simularea pipeline-ului asincron de colectare.
- **`unittest.mock`** — Patch-uri de izolare a execuției pentru testele de rețea concurente.

## 🚀 Instrucțiuni de Rulare

Toate comenzile de testare trebuie executate din rădăcina proiectului utilizând managerul de pachete `uv`:

```bash
# Rularea întregii suite de teste automate cu afișare detaliată și mesaje (Recomandat)
uv run pytest -v -s

# Rularea testelor specifice pentru verificarea motorului local de alertare
uv run pytest src/utils/ -v

# Rularea testelor și oprirea imediată la prima eroare întâlnită
uv run pytest -x
```

## 🏗️ Structura și Logica Testelor (Offline Verification)

Testele automate sunt proiectate să ruleze în izolare completă, garantând că logica software-ului este validă înainte de scrierea persistentă în baza de date `app.db`.

### 1. Integritatea Matricei de Traduceri
Funcția `test_translation_matrix_integrity` verifică automat dacă toate cele 5 limbi suportate (`RO`, `EN`, `IT`, `ES`, `HU`) conțin exact aceleași chei de traducere ca limba de referință (`RO`), prevenind prăbușirea interfeței din cauza cheilor lipsă (`KeyError`).

### 2. Validarea Pragurilor Stricte (Boundary Testing)
Funcția `test_strict_alert_boundaries` utilizează parametrizarea Pytest pentru a injecta telemetrie simulată la valorile limită exacte. Testul garantează că platforma utilizează inegalități substituite strict:
- `temperature > 32.0`
- `air_quality > 80.0`
- `soil_moisture < 35.0`
Dacă senzorul transmite o valoare egală cu pragul (ex: exact `32.0°C`), sistemul NU va declanșa alerta text, respectând modelul matematic unificat.

### 3. Cooldown-ul Local și Scutul Anti-Duplicat
Funcția `test_alert_engine_cooldown_offline` validează barieră temporală de siguranță a utilitarului `local_alerts.py`. Testul simulează transmiterea a două alerte identice în aceeași secundă: prima este aprobată și înregistrată în `security_alerts.log`, în timp ce a doua este respinsă instant (Returnează `False`), prevenind aglomerarea logurilor sau epuizarea spațiului pe disc.

### 4. Izolarea Completă a Execuției în Medii CI/CD (No-Network Policy)
- **Întrebare de Arhitectură**: Deoarece suita de teste rulează automat în GitHub Actions la fiecare push, cum garantezi că testele Pytest nu eșuează din cauza lipsei conexiunii la internet sau a indisponibilității API-ului Groq?
- **Justificare Tehnică**: Toate testele din directorul `ai_tests/` sunt proiectate să ruleze **100% offline**. Componentele care interfațează cu API-ul extern Groq sau cu baza de date fizică persistentă utilizează decoratori de tip `unittest.mock.patch` pentru a simula (mock-ui) răspunsurile de rețea ale modelului Qwen. Această abordare garantează determinism total în pipeline-ul CI/CD, asigurând rulări rapide (sub 5 secunde) și eliminând complet eșecurile false cauzate de latențele de cloud sau de epuizarea rate-limit-urilor de API.
