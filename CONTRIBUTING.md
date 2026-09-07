# 🤝 Ghid de Contribuire la Proiectul Smart City Cluj IoT

Vă mulțumim că ați ales să contribuiți la dezvoltarea platformei urbane! Pentru a menține integritatea arhitecturală și un istoric curat al codului, vă rugăm să respectați următorul set de reguli administrative și tehnice.

---

## 🚀 Workflow de Dezvoltare Locală

Toate operațiunile din mediu se realizează utilizând exclusiv managerul de pachete de mare viteză `uv`. Nu adăugați dependințe manual fără a le înregistra în structura proiectului.

1. **Clonarea și pornirea mediului:**
   ```bash
   git clone <repository-url>
   cd Smart-City-Cluj-IoT
   uv sync
   ```
2. **Rularea suitei complete de verificare (Pipeline local obligatoriu):**
   Înainte de a deschide un Pull Request, asigurați-vă că toate testele, linterele și evaluările AI trec cu succes prin comanda unificată:
   ```bash
   uv run pytest -v -s; uvx promptfoo eval --no-cache; uv run streamlit run main.py
   ```

---

## 🛠️ Reguli de Calitate a Codului (Ruff-Style)

Proiectul folosește un sistem strict de analiză statică. Orice cod care încalcă regulile va fi respins la integrare de către pipeline-ul de CI/CD:
* Toate fișierele de cod Python trebuie verificate și formatate folosind `ruff`.
* Nu lăsați instrucțiuni `print()` reziduale în straturile de backend; folosiți sistemul nativ de logging asincron.
* Păstrați inegalitățile stricte (`>`) pentru evaluarea limitelor telemetrice pentru a preveni oscilația alertelor în dashboard.

---

## 🧪 Integrarea Testelor Unitare și MLOps

* **Teste Offline:** Dacă adăugați funcționalități noi în utilitare, adăugați scenarii parametrizate corespunzătoare în folderul dedicat din rădăcină: `ai_tests/test_alerts_offline.py`.
* **Validare Semantică:** Modificările aduse prompturilor din `ai_tests/prompts.txt` necesită re-rularea matricei Promptfoo pentru modelul de producție **Qwen 3.6-27B** pentru a demonstra un scor stabil de **100% passed (8/8 cases)**.

---

## 🔐 Securitate și Izolare

* **Fără Secrete în Git:** Nu introduceți niciodată chei private API (`GROQ_API_KEY`) în cod. Toate variabilele de mediu trebuie să rămână izolate pe disc în fișierul local `.env`.
* **Sistem Local:** Toate sistemele de alertare trebuie să utilizeze scrierea asincronă protejată prin cooldown-ul de 10 secunde în `security_alerts.log`. Este interzisă reintroducerea oricărei dependințe cloud de mesagerie externă (ex: Twilio).
